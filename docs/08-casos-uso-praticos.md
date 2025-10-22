# 🎯 Casos de Uso Práticos

## 📚 Visão Geral

Este guia apresenta cenários reais de uso da stack Big Data com exemplos completos end-to-end.

## 🛒 Caso 1: E-commerce - Análise de Vendas

### Objetivo
Criar pipeline ETL completo para análise de vendas de um e-commerce, desde a ingestão até dashboards executivos.

### Dados de Entrada
```csv
# vendas_raw.csv
data,pedido_id,cliente_id,produto_id,produto_nome,categoria,quantidade,preco_unitario,desconto,total
2025-01-15,P001,C123,PROD001,Notebook Dell,Eletrônicos,1,4500.00,0.10,4050.00
2025-01-15,P002,C456,PROD002,Mouse Logitech,Acessórios,2,150.00,0.00,300.00
2025-01-16,P003,C789,PROD001,Notebook Dell,Eletrônicos,1,4500.00,0.05,4275.00
```

### Etapa 1: Ingestão (Bronze)

**DAG Airflow:**
```python
from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime
import pandas as pd
from minio import Minio

def ingerir_vendas(**context):
    # Simular leitura de API/DB externa
    df = pd.read_csv('/path/to/vendas_raw.csv')
    
    # Upload para MinIO Bronze
    client = Minio(
        "minio:9000",
        access_key="minioadmin",
        secret_key="minioadmin",
        secure=False
    )
    
    # Salvar com partição por data
    data_exec = context['ds']
    path = f"vendas/raw/dt={data_exec}/vendas.csv"
    
    csv_buffer = df.to_csv(index=False).encode('utf-8')
    client.put_object(
        "bronze",
        path,
        data=csv_buffer,
        length=len(csv_buffer)
    )

with DAG(
    'ecommerce_bronze',
    start_date=datetime(2025, 1, 1),
    schedule='@daily',
    catchup=False
) as dag:
    
    ingest = PythonOperator(
        task_id='ingerir_vendas',
        python_callable=ingerir_vendas
    )
```

### Etapa 2: Limpeza e Validação (Silver)

**Job Spark (bronze_to_silver.py):**
```python
from pyspark.sql import SparkSession
from pyspark.sql.functions import *
from pyspark.sql.types import *

spark = SparkSession.builder \
    .appName("Vendas Bronze to Silver") \
    .config("spark.hadoop.fs.s3a.endpoint", "http://minio:9000") \
    .config("spark.hadoop.fs.s3a.access.key", "minioadmin") \
    .config("spark.hadoop.fs.s3a.secret.key", "minioadmin") \
    .config("spark.hadoop.fs.s3a.path.style.access", "true") \
    .config("spark.hadoop.fs.s3a.impl", "org.apache.hadoop.fs.s3a.S3AFileSystem") \
    .getOrCreate()

# Ler Bronze
df = spark.read \
    .option("header", "true") \
    .csv("s3a://bronze/vendas/raw/")

# Limpeza e validação
df_silver = df \
    .withColumn("data", to_date(col("data"))) \
    .withColumn("quantidade", col("quantidade").cast("int")) \
    .withColumn("preco_unitario", col("preco_unitario").cast("decimal(10,2)")) \
    .withColumn("desconto", col("desconto").cast("decimal(5,2)")) \
    .withColumn("total", col("total").cast("decimal(10,2)")) \
    .filter(col("quantidade") > 0) \
    .filter(col("total") > 0) \
    .dropDuplicates(["pedido_id"]) \
    .withColumn("ano", year(col("data"))) \
    .withColumn("mes", month(col("data"))) \
    .withColumn("dia", dayofmonth(col("data")))

# Validação de qualidade
count_original = df.count()
count_limpo = df_silver.count()
print(f"Registros originais: {count_original}")
print(f"Registros após limpeza: {count_limpo}")
print(f"Registros removidos: {count_original - count_limpo}")

# Salvar Silver (Parquet particionado)
df_silver.write \
    .mode("overwrite") \
    .partitionBy("ano", "mes") \
    .parquet("s3a://silver/vendas/")

spark.stop()
```

**Integrar no Airflow:**
```python
from airflow.providers.apache.spark.operators.spark_submit import SparkSubmitOperator

with DAG('ecommerce_pipeline', ...) as dag:
    
    ingest = PythonOperator(...)
    
    process_silver = SparkSubmitOperator(
        task_id='bronze_to_silver',
        application='/opt/spark/jobs/bronze_to_silver.py',
        conn_id='spark_default'
    )
    
    ingest >> process_silver
```

### Etapa 3: Agregações (Gold)

**Job Spark (silver_to_gold.py):**
```python
# Ler Silver
df_silver = spark.read.parquet("s3a://silver/vendas/")

# Agregação 1: Vendas por produto
vendas_produto = df_silver.groupBy("produto_id", "produto_nome", "categoria") \
    .agg(
        count("pedido_id").alias("num_pedidos"),
        sum("quantidade").alias("qtd_total"),
        sum("total").alias("receita_total"),
        avg("total").alias("ticket_medio")
    )

vendas_produto.write \
    .mode("overwrite") \
    .parquet("s3a://gold/vendas/por_produto/")

# Agregação 2: Vendas diárias
vendas_diarias = df_silver.groupBy("data", "ano", "mes", "dia") \
    .agg(
        count("pedido_id").alias("num_pedidos"),
        sum("total").alias("receita_total"),
        countDistinct("cliente_id").alias("clientes_unicos")
    )

vendas_diarias.write \
    .mode("overwrite") \
    .partitionBy("ano", "mes") \
    .parquet("s3a://gold/vendas/diarias/")

# Agregação 3: Top produtos por categoria
from pyspark.sql.window import Window

window = Window.partitionBy("categoria").orderBy(desc("receita_total"))

top_produtos = df_silver.groupBy("categoria", "produto_nome") \
    .agg(sum("total").alias("receita_total")) \
    .withColumn("rank", rank().over(window)) \
    .filter(col("rank") <= 10)

top_produtos.write \
    .mode("overwrite") \
    .parquet("s3a://gold/vendas/top_produtos/")
```

### Etapa 4: Catalogar no Hive

```sql
-- Conectar Trino
docker compose exec trino trino --catalog hive --schema default

-- Criar schema
CREATE SCHEMA IF NOT EXISTS hive.ecommerce
WITH (location = 's3a://gold/vendas/');

-- Tabela: Vendas por produto
CREATE TABLE hive.ecommerce.vendas_produto (
    produto_id VARCHAR,
    produto_nome VARCHAR,
    categoria VARCHAR,
    num_pedidos BIGINT,
    qtd_total BIGINT,
    receita_total DECIMAL(15,2),
    ticket_medio DECIMAL(10,2)
)
WITH (
    format = 'PARQUET',
    external_location = 's3a://gold/vendas/por_produto/'
);

-- Tabela: Vendas diárias (particionada)
CREATE TABLE hive.ecommerce.vendas_diarias (
    data DATE,
    ano INTEGER,
    mes INTEGER,
    dia INTEGER,
    num_pedidos BIGINT,
    receita_total DECIMAL(15,2),
    clientes_unicos BIGINT
)
WITH (
    format = 'PARQUET',
    external_location = 's3a://gold/vendas/diarias/',
    partitioned_by = ARRAY['ano', 'mes']
);
```

### Etapa 5: Dashboard Superset

**Gráficos:**
1. **KPI - Receita Total**
   - Tipo: Big Number
   - Metric: `SUM(receita_total)`
   - Dataset: `vendas_diarias`

2. **Evolução de Vendas**
   - Tipo: Line Chart
   - X: `data`
   - Y: `receita_total`
   - Dataset: `vendas_diarias`

3. **Top 10 Produtos**
   - Tipo: Bar Chart
   - Dimension: `produto_nome`
   - Metric: `receita_total`
   - Dataset: `vendas_produto`
   - Limit: 10

4. **Vendas por Categoria**
   - Tipo: Pie Chart
   - Dimension: `categoria`
   - Metric: `receita_total`
   - Dataset: `vendas_produto`

## 📊 Caso 2: Logs de Aplicação - Monitoramento

### Objetivo
Processar logs de aplicação para detecção de erros e análise de performance.

### Dados de Entrada
```json
{
  "timestamp": "2025-01-15T10:30:45.123Z",
  "level": "ERROR",
  "service": "api-gateway",
  "message": "Connection timeout",
  "user_id": "user123",
  "endpoint": "/api/products",
  "response_time_ms": 5000,
  "status_code": 504
}
```

### Pipeline Spark Streaming

```python
from pyspark.sql import SparkSession
from pyspark.sql.functions import *

spark = SparkSession.builder \
    .appName("Log Processing") \
    .getOrCreate()

# Schema dos logs
schema = StructType([
    StructField("timestamp", StringType()),
    StructField("level", StringType()),
    StructField("service", StringType()),
    StructField("message", StringType()),
    StructField("user_id", StringType()),
    StructField("endpoint", StringType()),
    StructField("response_time_ms", IntegerType()),
    StructField("status_code", IntegerType())
])

# Ler logs do MinIO Bronze
logs = spark.read \
    .schema(schema) \
    .json("s3a://bronze/logs/")

# Transformações
logs_processed = logs \
    .withColumn("timestamp", to_timestamp(col("timestamp"))) \
    .withColumn("date", to_date(col("timestamp"))) \
    .withColumn("hour", hour(col("timestamp"))) \
    .withColumn("is_error", when(col("level").isin("ERROR", "CRITICAL"), 1).otherwise(0)) \
    .withColumn("is_slow", when(col("response_time_ms") > 2000, 1).otherwise(0))

# Agregações por hora
logs_hourly = logs_processed.groupBy("date", "hour", "service", "endpoint") \
    .agg(
        count("*").alias("total_requests"),
        sum("is_error").alias("errors"),
        sum("is_slow").alias("slow_requests"),
        avg("response_time_ms").alias("avg_response_time"),
        max("response_time_ms").alias("max_response_time"),
        countDistinct("user_id").alias("unique_users")
    ) \
    .withColumn("error_rate", col("errors") / col("total_requests")) \
    .withColumn("slow_rate", col("slow_requests") / col("total_requests"))

# Salvar Gold
logs_hourly.write \
    .mode("overwrite") \
    .partitionBy("date") \
    .parquet("s3a://gold/logs/hourly/")

# Alertas (salvar erros críticos)
critical_errors = logs_processed \
    .filter(col("level") == "CRITICAL") \
    .select("timestamp", "service", "endpoint", "message", "user_id")

critical_errors.write \
    .mode("append") \
    .parquet("s3a://gold/logs/alerts/")
```

### Dashboard de Monitoramento

**SQL para alertas:**
```sql
-- Top 10 endpoints com mais erros
SELECT 
    endpoint,
    SUM(errors) as total_errors,
    AVG(error_rate) as avg_error_rate
FROM hive.logs.hourly
WHERE date >= CURRENT_DATE - INTERVAL '7' DAY
GROUP BY endpoint
ORDER BY total_errors DESC
LIMIT 10;

-- Serviços lentos
SELECT 
    service,
    AVG(avg_response_time) as response_time,
    SUM(slow_requests) as slow_count
FROM hive.logs.hourly
WHERE date >= CURRENT_DATE - INTERVAL '1' DAY
GROUP BY service
HAVING AVG(avg_response_time) > 1000
ORDER BY response_time DESC;
```

## 🏦 Caso 3: Sistema Bancário - Detecção de Fraude

### Objetivo
Análise de transações financeiras para identificar padrões suspeitos.

### Pipeline de Feature Engineering

```python
from pyspark.sql import SparkSession
from pyspark.sql.functions import *
from pyspark.sql.window import Window

spark = SparkSession.builder \
    .appName("Fraud Detection Features") \
    .getOrCreate()

# Ler transações
transactions = spark.read.parquet("s3a://silver/transactions/")

# Window para análise temporal
window_1h = Window.partitionBy("account_id") \
    .orderBy("timestamp") \
    .rangeBetween(-3600, 0)  # Última hora

window_24h = Window.partitionBy("account_id") \
    .orderBy("timestamp") \
    .rangeBetween(-86400, 0)  # Último dia

# Features
features = transactions \
    .withColumn("tx_count_1h", count("*").over(window_1h)) \
    .withColumn("tx_count_24h", count("*").over(window_24h)) \
    .withColumn("total_amount_1h", sum("amount").over(window_1h)) \
    .withColumn("total_amount_24h", sum("amount").over(window_24h)) \
    .withColumn("avg_amount_24h", avg("amount").over(window_24h)) \
    .withColumn("max_amount_24h", max("amount").over(window_24h))

# Regras de fraude
fraud_detection = features \
    .withColumn("is_suspicious",
        when((col("tx_count_1h") > 10) | 
             (col("amount") > col("avg_amount_24h") * 3) |
             (col("amount") > 10000), 1).otherwise(0)
    )

# Salvar para análise
fraud_detection.write \
    .mode("overwrite") \
    .partitionBy("date") \
    .parquet("s3a://gold/fraud/transactions_scored/")

# Casos suspeitos
suspicious = fraud_detection.filter(col("is_suspicious") == 1)

suspicious.write \
    .mode("append") \
    .parquet("s3a://gold/fraud/alerts/")
```

### Query de Análise

```sql
-- Padrões de fraude por região
WITH fraudes AS (
    SELECT 
        region,
        merchant_category,
        COUNT(*) as fraud_count,
        SUM(amount) as fraud_amount,
        AVG(amount) as avg_fraud_amount
    FROM hive.fraud.alerts
    WHERE date >= CURRENT_DATE - INTERVAL '30' DAY
    GROUP BY region, merchant_category
)
SELECT *
FROM fraudes
WHERE fraud_count > 5
ORDER BY fraud_amount DESC;
```

## 📱 Caso 4: IoT - Telemetria de Sensores

### Objetivo
Processar dados de sensores IoT para monitoramento em tempo real.

### Schema dos Dados

```python
sensor_schema = StructType([
    StructField("device_id", StringType()),
    StructField("timestamp", TimestampType()),
    StructField("temperature", DoubleType()),
    StructField("humidity", DoubleType()),
    StructField("pressure", DoubleType()),
    StructField("battery_level", IntegerType()),
    StructField("location_lat", DoubleType()),
    StructField("location_lon", DoubleType())
])
```

### Processamento

```python
from pyspark.sql import SparkSession
from pyspark.sql.functions import *

# Ler dados
sensors = spark.read.schema(sensor_schema) \
    .json("s3a://bronze/iot/sensors/")

# Agregações por dispositivo/hora
sensors_hourly = sensors \
    .withColumn("hour", date_trunc("hour", col("timestamp"))) \
    .groupBy("device_id", "hour") \
    .agg(
        avg("temperature").alias("avg_temp"),
        min("temperature").alias("min_temp"),
        max("temperature").alias("max_temp"),
        avg("humidity").alias("avg_humidity"),
        avg("pressure").alias("avg_pressure"),
        avg("battery_level").alias("avg_battery"),
        count("*").alias("readings_count")
    )

# Detectar anomalias
from pyspark.sql.window import Window

window = Window.partitionBy("device_id") \
    .orderBy("hour") \
    .rowsBetween(-24, -1)  # 24 horas anteriores

anomalies = sensors_hourly \
    .withColumn("avg_temp_24h", avg("avg_temp").over(window)) \
    .withColumn("stddev_temp_24h", stddev("avg_temp").over(window)) \
    .withColumn("is_anomaly",
        when(
            (col("avg_temp") > col("avg_temp_24h") + 2 * col("stddev_temp_24h")) |
            (col("avg_temp") < col("avg_temp_24h") - 2 * col("stddev_temp_24h")),
            1
        ).otherwise(0)
    )

# Salvar
anomalies.write \
    .mode("overwrite") \
    .partitionBy("hour") \
    .parquet("s3a://gold/iot/anomalies/")
```

## 🎓 Caso 5: Educação - Análise de Aprendizado

### Objetivo
Analisar progresso de estudantes em plataforma online.

### Pipeline Completo

```python
# Bronze: Eventos de interação
eventos = spark.read.json("s3a://bronze/learning/events/")

# Silver: Limpeza
eventos_clean = eventos \
    .dropDuplicates(["event_id"]) \
    .filter(col("user_id").isNotNull()) \
    .withColumn("date", to_date(col("timestamp")))

# Gold: Métricas de engajamento
engagement = eventos_clean.groupBy("user_id", "course_id", "date") \
    .agg(
        sum(when(col("event_type") == "video_view", 1).otherwise(0)).alias("videos_watched"),
        sum(when(col("event_type") == "quiz_completed", 1).otherwise(0)).alias("quizzes_done"),
        sum(when(col("event_type") == "assignment_submitted", 1).otherwise(0)).alias("assignments_submitted"),
        sum(col("time_spent_seconds")).alias("total_time_seconds")
    )

engagement.write \
    .mode("overwrite") \
    .partitionBy("date") \
    .parquet("s3a://gold/learning/engagement/")
```

### Análise SQL

```sql
-- Estudantes em risco (baixo engajamento)
SELECT 
    user_id,
    course_id,
    AVG(videos_watched) as avg_videos,
    AVG(quizzes_done) as avg_quizzes,
    AVG(total_time_seconds) / 3600 as avg_hours
FROM hive.learning.engagement
WHERE date >= CURRENT_DATE - INTERVAL '7' DAY
GROUP BY user_id, course_id
HAVING AVG(videos_watched) < 2 
   AND AVG(total_time_seconds) < 1800
ORDER BY avg_hours ASC;
```

## 🎯 Padrões e Boas Práticas

### 1. Estrutura de Pipeline
```
Bronze (Raw) → Silver (Clean) → Gold (Aggregated)
     ↓              ↓                  ↓
   JSON/CSV      Parquet           Parquet
   Append     Overwrite/Merge     Overwrite
```

### 2. Particionamento
- **Logs:** Por data (diário)
- **Transações:** Por data (diário ou mensal)
- **IoT:** Por timestamp (horário)
- **Analytics:** Por dimensões de negócio

### 3. Validação de Dados
```python
# Sempre validar
assert df.count() > 0, "Dataset vazio"
assert df.filter(col("id").isNull()).count() == 0, "IDs nulos"
assert df.select("date").distinct().count() == 1, "Múltiplas datas"
```

### 4. Monitoramento
```python
# Métricas do pipeline
metrics = {
    "rows_input": df_bronze.count(),
    "rows_output": df_silver.count(),
    "rows_rejected": df_bronze.count() - df_silver.count(),
    "execution_time_sec": end_time - start_time
}

# Logar métricas
print(f"Pipeline metrics: {metrics}")
```

## 🔄 Automação Completa

### DAG Orquestrador

```python
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.apache.spark.operators.spark_submit import SparkSubmitOperator
from datetime import datetime, timedelta

default_args = {
    'owner': 'data-team',
    'depends_on_past': False,
    'email_on_failure': True,
    'email': ['team@company.com'],
    'retries': 2,
    'retry_delay': timedelta(minutes=5)
}

with DAG(
    'complete_pipeline',
    default_args=default_args,
    description='Pipeline ETL completo',
    schedule='@daily',
    start_date=datetime(2025, 1, 1),
    catchup=False
) as dag:
    
    # Bronze
    ingest = PythonOperator(
        task_id='ingest_data',
        python_callable=ingest_from_source
    )
    
    # Silver
    clean = SparkSubmitOperator(
        task_id='clean_data',
        application='/opt/spark/jobs/bronze_to_silver.py'
    )
    
    # Gold
    aggregate = SparkSubmitOperator(
        task_id='aggregate_data',
        application='/opt/spark/jobs/silver_to_gold.py'
    )
    
    # Catalog
    catalog = PythonOperator(
        task_id='update_catalog',
        python_callable=update_hive_tables
    )
    
    # Alert
    notify = PythonOperator(
        task_id='send_notification',
        python_callable=send_success_email
    )
    
    # Fluxo
    ingest >> clean >> aggregate >> catalog >> notify
```

## 🎓 Próximos Passos

- Implemente seus próprios casos de uso
- Monitore performance dos pipelines
- Otimize queries baseado em uso real
- Configure alertas para falhas

**Continue explorando a documentação! 🚀**
