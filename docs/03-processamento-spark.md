# ⚡ Processamento de Dados com Apache Spark

## 🎯 Visão Geral

O Apache Spark permite processar grandes volumes de dados de forma distribuída. Nossa stack possui:
- **Spark Master:** Coordenador (http://localhost:8081)
- **Spark Worker:** Executor com 2 cores e 2GB RAM (http://localhost:8082)

## 📁 Estrutura de Jobs Spark

```
examples/jobs/
├── process_sales.py      # Processamento de vendas
├── aggregate_sales.py    # Agregações
└── data_quality.py       # Validação de qualidade
```

## 🚀 Exemplo 1: Job Spark Básico

### Arquivo: `process_vendas.py`

```python
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, sum as _sum, count, avg
from pyspark.sql.types import StructType, StructField, StringType, IntegerType, DoubleType, DateType
import sys

def create_spark_session(app_name="ProcessamentoVendas"):
    """Cria sessão Spark com configurações para MinIO"""
    return SparkSession.builder \
        .appName(app_name) \
        .config("spark.hadoop.fs.s3a.endpoint", "http://minio:9000") \
        .config("spark.hadoop.fs.s3a.access.key", "minioadmin") \
        .config("spark.hadoop.fs.s3a.secret.key", "minioadmin123") \
        .config("spark.hadoop.fs.s3a.path.style.access", "true") \
        .config("spark.hadoop.fs.s3a.impl", "org.apache.hadoop.fs.s3a.S3AFileSystem") \
        .getOrCreate()

def ler_dados_bronze(spark, caminho):
    """Lê dados do bucket bronze"""
    # Definir schema
    schema = StructType([
        StructField("data", DateType(), True),
        StructField("produto", StringType(), True),
        StructField("quantidade", IntegerType(), True),
        StructField("valor", DoubleType(), True)
    ])
    
    df = spark.read \
        .option("header", "true") \
        .option("inferSchema", "false") \
        .schema(schema) \
        .csv(caminho)
    
    print(f"✅ Lidos {df.count()} registros")
    return df

def transformar_dados(df):
    """Aplica transformações nos dados"""
    from pyspark.sql.functions import year, month, dayofmonth, to_date
    
    # Converter string para data se necessário
    df = df.withColumn("data", to_date(col("data")))
    
    # Adicionar colunas calculadas
    df = df.withColumn("valor_total", col("quantidade") * col("valor"))
    df = df.withColumn("ano", year(col("data")))
    df = df.withColumn("mes", month(col("data")))
    df = df.withColumn("dia", dayofmonth(col("data")))
    
    # Filtrar dados inválidos
    df = df.filter(col("quantidade") > 0)
    df = df.filter(col("valor") > 0)
    df = df.filter(col("produto").isNotNull())
    
    print(f"✅ Transformados {df.count()} registros válidos")
    return df

def salvar_dados_silver(df, caminho):
    """Salva dados no bucket silver"""
    df.write \
        .mode("overwrite") \
        .option("header", "true") \
        .parquet(caminho)
    
    print(f"✅ Dados salvos em {caminho}")

def main():
    # Caminhos (podem vir de argumentos)
    input_path = "s3a://bronze/vendas/vendas.csv"
    output_path = "s3a://silver/vendas/vendas_processadas"
    
    # Processar argumentos
    if len(sys.argv) > 1:
        input_path = sys.argv[1]
    if len(sys.argv) > 2:
        output_path = sys.argv[2]
    
    # Criar sessão Spark
    spark = create_spark_session()
    
    try:
        # ETL Pipeline
        print("🚀 Iniciando processamento...")
        
        # Extract
        df_bronze = ler_dados_bronze(spark, input_path)
        df_bronze.show(5)
        
        # Transform
        df_silver = transformar_dados(df_bronze)
        df_silver.show(5)
        
        # Load
        salvar_dados_silver(df_silver, output_path)
        
        # Estatísticas
        print("\n📊 Estatísticas do processamento:")
        df_silver.describe().show()
        
        print("✅ Processamento concluído com sucesso!")
        
    except Exception as e:
        print(f"❌ Erro no processamento: {e}")
        raise
    finally:
        spark.stop()

if __name__ == "__main__":
    main()
```

## 🎯 Exemplo 2: Agregações com Spark

### Arquivo: `agregar_vendas.py`

```python
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, sum as _sum, count, avg, max as _max, min as _min
from pyspark.sql.functions import year, month

def create_spark_session():
    return SparkSession.builder \
        .appName("AgregacaoVendas") \
        .config("spark.hadoop.fs.s3a.endpoint", "http://minio:9000") \
        .config("spark.hadoop.fs.s3a.access.key", "minioadmin") \
        .config("spark.hadoop.fs.s3a.secret.key", "minioadmin123") \
        .config("spark.hadoop.fs.s3a.path.style.access", "true") \
        .config("spark.hadoop.fs.s3a.impl", "org.apache.hadoop.fs.s3a.S3AFileSystem") \
        .getOrCreate()

def agregar_por_periodo(spark):
    """Agrega vendas por período (ano/mês)"""
    # Ler dados processados
    df = spark.read.parquet("s3a://silver/vendas/vendas_processadas")
    
    # Agregar por ano e mês
    vendas_mensais = df.groupBy("ano", "mes") \
        .agg(
            count("*").alias("total_vendas"),
            _sum("quantidade").alias("quantidade_total"),
            _sum("valor_total").alias("receita_total"),
            avg("valor").alias("ticket_medio"),
            _max("valor_total").alias("maior_venda"),
            _min("valor_total").alias("menor_venda")
        ) \
        .orderBy("ano", "mes")
    
    # Salvar no gold
    vendas_mensais.write \
        .mode("overwrite") \
        .option("header", "true") \
        .parquet("s3a://gold/vendas/vendas_por_periodo")
    
    print("✅ Agregação por período concluída")
    vendas_mensais.show()
    
    return vendas_mensais

def agregar_por_produto(spark):
    """Agrega vendas por produto"""
    df = spark.read.parquet("s3a://silver/vendas/vendas_processadas")
    
    # Top produtos
    top_produtos = df.groupBy("produto") \
        .agg(
            count("*").alias("total_vendas"),
            _sum("quantidade").alias("quantidade_total"),
            _sum("valor_total").alias("receita_total"),
            avg("valor").alias("preco_medio")
        ) \
        .orderBy(col("receita_total").desc())
    
    # Salvar no gold
    top_produtos.write \
        .mode("overwrite") \
        .option("header", "true") \
        .parquet("s3a://gold/vendas/vendas_por_produto")
    
    print("✅ Agregação por produto concluída")
    top_produtos.show()
    
    return top_produtos

def main():
    spark = create_spark_session()
    
    try:
        print("🚀 Iniciando agregações...")
        
        agregar_por_periodo(spark)
        agregar_por_produto(spark)
        
        print("✅ Todas agregações concluídas!")
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        raise
    finally:
        spark.stop()

if __name__ == "__main__":
    main()
```

## ▶️ Executando Jobs Spark

### Método 1: Via spark-submit (Linha de Comando)

```bash
# Entrar no container do Spark Master
docker exec -it spark-master bash

# Executar job
spark-submit \
  --master spark://spark-master:7077 \
  --executor-memory 1G \
  --executor-cores 1 \
  /opt/spark-jobs/process_vendas.py

# Com argumentos
spark-submit \
  --master spark://spark-master:7077 \
  /opt/spark-jobs/process_vendas.py \
  s3a://bronze/vendas/vendas.csv \
  s3a://silver/vendas/output
```

### Método 2: Via Airflow (Recomendado)

```python
from airflow.providers.apache.spark.operators.spark_submit import SparkSubmitOperator

processar_vendas = SparkSubmitOperator(
    task_id='processar_vendas',
    application='/opt/airflow/jobs/process_vendas.py',
    conn_id='spark_default',
    conf={
        'spark.master': 'spark://spark-master:7077',
        'spark.executor.memory': '1g',
        'spark.executor.cores': '1'
    },
    application_args=[
        's3a://bronze/vendas/vendas.csv',
        's3a://silver/vendas/output'
    ]
)
```

### Método 3: PySpark Shell (Interativo)

```bash
# Entrar no container
docker exec -it spark-master bash

# Iniciar PySpark com configurações MinIO
pyspark \
  --conf spark.hadoop.fs.s3a.endpoint=http://minio:9000 \
  --conf spark.hadoop.fs.s3a.access.key=minioadmin \
  --conf spark.hadoop.fs.s3a.secret.key=minioadmin123 \
  --conf spark.hadoop.fs.s3a.path.style.access=true
```

```python
# No shell PySpark
df = spark.read.csv("s3a://bronze/vendas/vendas.csv", header=True)
df.show()
df.printSchema()
```

## 📊 Monitorando Jobs Spark

### Spark Master UI
- **URL:** http://localhost:8081
- **Visualizar:**
  - Workers disponíveis
  - Aplicações rodando
  - Aplicações completadas
  - Recursos em uso

### Spark Worker UI
- **URL:** http://localhost:8082
- **Visualizar:**
  - Executors ativos
  - Tarefas em execução
  - Logs de erros

## 🎯 Exemplo 3: Qualidade de Dados

### Arquivo: `validacao_qualidade.py`

```python
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, count, when, isnan, isnull

def create_spark_session():
    return SparkSession.builder \
        .appName("ValidacaoQualidade") \
        .config("spark.hadoop.fs.s3a.endpoint", "http://minio:9000") \
        .config("spark.hadoop.fs.s3a.access.key", "minioadmin") \
        .config("spark.hadoop.fs.s3a.secret.key", "minioadmin123") \
        .config("spark.hadoop.fs.s3a.path.style.access", "true") \
        .config("spark.hadoop.fs.s3a.impl", "org.apache.hadoop.fs.s3a.S3AFileSystem") \
        .getOrCreate()

def validar_dados(df):
    """Valida qualidade dos dados"""
    total_registros = df.count()
    
    print(f"\n📊 RELATÓRIO DE QUALIDADE")
    print(f"{'='*60}")
    print(f"Total de registros: {total_registros}")
    
    # Verificar valores nulos
    print(f"\n🔍 Valores Nulos:")
    for coluna in df.columns:
        nulos = df.filter(col(coluna).isNull()).count()
        percentual = (nulos / total_registros) * 100
        print(f"  {coluna}: {nulos} ({percentual:.2f}%)")
    
    # Verificar duplicatas
    duplicatas = total_registros - df.dropDuplicates().count()
    print(f"\n🔄 Registros Duplicados: {duplicatas}")
    
    # Validações específicas
    if 'quantidade' in df.columns:
        invalidos = df.filter(col('quantidade') <= 0).count()
        print(f"\n⚠️  Quantidades inválidas (<=0): {invalidos}")
    
    if 'valor' in df.columns:
        invalidos = df.filter(col('valor') <= 0).count()
        print(f"⚠️  Valores inválidos (<=0): {invalidos}")
    
    # Estatísticas
    print(f"\n📈 Estatísticas:")
    df.describe().show()

def main():
    spark = create_spark_session()
    
    try:
        # Ler dados
        df = spark.read.parquet("s3a://silver/vendas/vendas_processadas")
        
        # Validar
        validar_dados(df)
        
    finally:
        spark.stop()

if __name__ == "__main__":
    main()
```

## 💡 Boas Práticas

### 1. Particionamento de Dados
```python
# Salvar com particionamento
df.write \
    .partitionBy("ano", "mes") \
    .mode("overwrite") \
    .parquet("s3a://silver/vendas/particoes")
```

### 2. Cache para Reutilização
```python
# Cachear DataFrame usado múltiplas vezes
df_cached = df.cache()
df_cached.count()  # Primeira execução
df_cached.show()   # Usa cache
```

### 3. Broadcast Join para Tabelas Pequenas
```python
from pyspark.sql.functions import broadcast

# Join otimizado
df_grande.join(broadcast(df_pequeno), "chave")
```

### 4. Modo de Salvamento
```python
# Sobrescrever
.mode("overwrite")

# Adicionar (append)
.mode("append")

# Erro se existir
.mode("errorifexists")
```

## 🔧 Configurações Importantes

### Ajustar Recursos
```python
spark = SparkSession.builder \
    .config("spark.executor.memory", "2g") \
    .config("spark.executor.cores", "2") \
    .config("spark.driver.memory", "1g") \
    .getOrCreate()
```

### Otimizar Shuffle
```python
.config("spark.sql.shuffle.partitions", "4")  # Padrão: 200
```

## 🆘 Troubleshooting

### Erro de Memória
- Reduzir `executor.memory`
- Aumentar `sql.shuffle.partitions`
- Processar dados em lotes

### Conexão MinIO Falha
- Verificar endpoint: `http://minio:9000`
- Confirmar credenciais
- Testar conectividade: `ping minio`

### Job Lento
- Verificar particionamento
- Usar cache quando apropriado
- Revisar operações shuffle

## 🎓 Próximos Passos

- **Consultas SQL:** `04-consultas-trino.md`
- **Dashboards:** `05-criando-dashboards-superset.md`
- **Catálogo Hive:** `06-catalogo-hive-metastore.md`
