# 🔌 APIs REST e Acesso JDBC

## 🎯 Visão Geral

Este guia mostra como acessar programaticamente os dados através de APIs REST e conexões JDBC.

## 📊 Trino JDBC

### Configuração

#### Maven (pom.xml)

```xml
<dependency>
    <groupId>io.trino</groupId>
    <artifactId>trino-jdbc</artifactId>
    <version>435</version>
</dependency>
```

#### Gradle (build.gradle)

```gradle
implementation 'io.trino:trino-jdbc:435'
```

### Java - Conexão Básica

```java
import java.sql.*;

public class TrinoExample {
    public static void main(String[] args) {
        String url = "jdbc:trino://localhost:8080/hive/vendas";
        String user = "trino";
        
        try (Connection conn = DriverManager.getConnection(url, user, null)) {
            Statement stmt = conn.createStatement();
            ResultSet rs = stmt.executeQuery(
                "SELECT produto, SUM(valor_total) as receita " +
                "FROM vendas_silver " +
                "GROUP BY produto " +
                "ORDER BY receita DESC " +
                "LIMIT 10"
            );
            
            while (rs.next()) {
                String produto = rs.getString("produto");
                double receita = rs.getDouble("receita");
                System.out.printf("%s: R$ %.2f%n", produto, receita);
            }
        } catch (SQLException e) {
            e.printStackTrace();
        }
    }
}
```

### Java - PreparedStatement

```java
public class TrinoParametrizado {
    public static void main(String[] args) {
        String url = "jdbc:trino://localhost:8080/hive/vendas";
        
        try (Connection conn = DriverManager.getConnection(url, "trino", null)) {
            String sql = "SELECT * FROM vendas_silver " +
                        "WHERE produto = ? AND ano = ?";
            
            PreparedStatement pstmt = conn.prepareStatement(sql);
            pstmt.setString(1, "Notebook");
            pstmt.setInt(2, 2025);
            
            ResultSet rs = pstmt.executeQuery();
            
            while (rs.next()) {
                System.out.println(
                    rs.getString("id") + " - " +
                    rs.getDate("data") + " - " +
                    rs.getBigDecimal("valor_total")
                );
            }
        } catch (SQLException e) {
            e.printStackTrace();
        }
    }
}
```

### Python - JDBC via JayDeBeApi

```python
import jaydebeapi

# Configuração
jdbc_url = "jdbc:trino://localhost:8080/hive/vendas"
driver_class = "io.trino.jdbc.TrinoDriver"
jar_file = "/path/to/trino-jdbc-435.jar"

# Conectar
conn = jaydebeapi.connect(
    driver_class,
    jdbc_url,
    ["trino", ""],
    jar_file
)

# Query
cursor = conn.cursor()
cursor.execute("""
    SELECT produto, SUM(valor_total) as receita
    FROM vendas_silver
    GROUP BY produto
    ORDER BY receita DESC
    LIMIT 10
""")

# Resultados
for row in cursor.fetchall():
    print(f"{row[0]}: R$ {row[1]:.2f}")

conn.close()
```

### Python - Trino com SQLAlchemy

```python
from sqlalchemy import create_engine, text
import pandas as pd

# Criar engine
engine = create_engine('trino://trino@localhost:8080/hive')

# Query direta
with engine.connect() as conn:
    result = conn.execute(text("""
        SELECT produto, SUM(quantidade) as total
        FROM vendas.vendas_silver
        GROUP BY produto
    """))
    
    for row in result:
        print(f"{row.produto}: {row.total}")

# Pandas
df = pd.read_sql(
    "SELECT * FROM vendas.vendas_silver WHERE ano = 2025",
    engine
)
print(df.head())
```

### R - RJDBC

```r
library(RJDBC)

# Configurar driver
drv <- JDBC(
    "io.trino.jdbc.TrinoDriver",
    "/path/to/trino-jdbc-435.jar"
)

# Conectar
conn <- dbConnect(
    drv,
    "jdbc:trino://localhost:8080/hive/vendas",
    "trino",
    ""
)

# Query
result <- dbGetQuery(conn, "
    SELECT produto, SUM(valor_total) as receita
    FROM vendas_silver
    GROUP BY produto
    ORDER BY receita DESC
    LIMIT 10
")

print(result)

# Fechar
dbDisconnect(conn)
```

## 🌐 Trino REST API

### HTTP Básico

```bash
# Submeter query
curl -X POST http://localhost:8080/v1/statement \
  -H "X-Trino-User: trino" \
  -H "X-Trino-Catalog: hive" \
  -H "X-Trino-Schema: vendas" \
  -d "SELECT * FROM vendas_silver LIMIT 10"
```

### Python - requests

```python
import requests
import time

# Submeter query
url = "http://localhost:8080/v1/statement"
headers = {
    "X-Trino-User": "trino",
    "X-Trino-Catalog": "hive",
    "X-Trino-Schema": "vendas"
}
query = "SELECT produto, SUM(valor_total) as receita FROM vendas_silver GROUP BY produto"

response = requests.post(url, headers=headers, data=query)
result = response.json()

# Buscar resultados
next_uri = result.get("nextUri")
while next_uri:
    response = requests.get(next_uri, headers=headers)
    result = response.json()
    
    # Processar dados
    if "data" in result:
        for row in result["data"]:
            print(row)
    
    next_uri = result.get("nextUri")
    time.sleep(0.1)  # Throttle
```

### Python - Cliente Oficial

```python
from trino.dbapi import connect
from trino.auth import BasicAuthentication

conn = connect(
    host='localhost',
    port=8080,
    user='trino',
    catalog='hive',
    schema='vendas'
)

cursor = conn.cursor()
cursor.execute("""
    SELECT 
        produto,
        SUM(quantidade) as qtd,
        SUM(valor_total) as receita
    FROM vendas_silver
    WHERE ano = 2025
    GROUP BY produto
""")

rows = cursor.fetchall()
for row in rows:
    print(f"{row[0]}: Qtd={row[1]}, R$={row[2]:.2f}")
```

## 🐍 Apache Spark JDBC

### Python - PySpark

```python
from pyspark.sql import SparkSession

spark = SparkSession.builder \
    .appName("TrinoJDBC") \
    .config("spark.jars", "/path/to/trino-jdbc-435.jar") \
    .getOrCreate()

# Ler via JDBC
df = spark.read \
    .format("jdbc") \
    .option("url", "jdbc:trino://localhost:8080/hive/vendas") \
    .option("dbtable", "vendas_silver") \
    .option("user", "trino") \
    .load()

df.show()

# Query customizada
query = """
(SELECT produto, SUM(valor_total) as receita
 FROM vendas_silver
 GROUP BY produto) AS vendas_agregadas
"""

df_agg = spark.read \
    .format("jdbc") \
    .option("url", "jdbc:trino://localhost:8080/hive/vendas") \
    .option("dbtable", query) \
    .option("user", "trino") \
    .load()

df_agg.show()
```

### Scala - Spark

```scala
import org.apache.spark.sql.SparkSession

val spark = SparkSession.builder()
  .appName("TrinoJDBC")
  .getOrCreate()

val df = spark.read
  .format("jdbc")
  .option("url", "jdbc:trino://localhost:8080/hive/vendas")
  .option("dbtable", "vendas_silver")
  .option("user", "trino")
  .load()

df.show()

// Escrever de volta
df.write
  .format("jdbc")
  .option("url", "jdbc:trino://localhost:8080/hive/vendas")
  .option("dbtable", "vendas_backup")
  .option("user", "trino")
  .mode("overwrite")
  .save()
```

## 🌬️ Apache Airflow REST API

### Autenticação

```python
import requests
from requests.auth import HTTPBasicAuth

# Configuração
airflow_url = "http://localhost:8080"
auth = HTTPBasicAuth("airflow", "airflow")

# Listar DAGs
response = requests.get(
    f"{airflow_url}/api/v1/dags",
    auth=auth
)
dags = response.json()
print(dags)
```

### Triggerar DAG

```python
# Triggerar DAG manualmente
dag_id = "etl_vendas_pipeline"
response = requests.post(
    f"{airflow_url}/api/v1/dags/{dag_id}/dagRuns",
    auth=auth,
    json={"conf": {"data_inicio": "2025-01-01"}}
)

dag_run = response.json()
print(f"DAG Run ID: {dag_run['dag_run_id']}")
```

### Checar Status

```python
# Status de uma DAG run
dag_run_id = "manual__2025-01-23T10:00:00+00:00"
response = requests.get(
    f"{airflow_url}/api/v1/dags/{dag_id}/dagRuns/{dag_run_id}",
    auth=auth
)

status = response.json()
print(f"Estado: {status['state']}")
print(f"Início: {status['start_date']}")
print(f"Fim: {status['end_date']}")
```

### Listar Tasks

```python
# Tasks de uma DAG run
response = requests.get(
    f"{airflow_url}/api/v1/dags/{dag_id}/dagRuns/{dag_run_id}/taskInstances",
    auth=auth
)

tasks = response.json()
for task in tasks['task_instances']:
    print(f"{task['task_id']}: {task['state']}")
```

### Logs de Task

```python
# Logs de uma task específica
task_id = "processar_bronze"
response = requests.get(
    f"{airflow_url}/api/v1/dags/{dag_id}/dagRuns/{dag_run_id}/taskInstances/{task_id}/logs/1",
    auth=auth
)

print(response.text)
```

## 📊 Apache Superset REST API

### Login e Token

```python
import requests

superset_url = "http://localhost:8088"

# Login
login_data = {
    "username": "admin",
    "password": "admin",
    "provider": "db",
    "refresh": True
}

response = requests.post(
    f"{superset_url}/api/v1/security/login",
    json=login_data
)

tokens = response.json()
access_token = tokens["access_token"]
headers = {"Authorization": f"Bearer {access_token}"}
```

### Listar Dashboards

```python
# Buscar dashboards
response = requests.get(
    f"{superset_url}/api/v1/dashboard/",
    headers=headers
)

dashboards = response.json()
for dash in dashboards['result']:
    print(f"{dash['id']}: {dash['dashboard_title']}")
```

### Executar Query

```python
# Executar SQL via Superset
query_data = {
    "database_id": 1,
    "sql": "SELECT produto, SUM(valor_total) FROM hive.vendas.vendas_silver GROUP BY produto",
    "schema": "vendas"
}

response = requests.post(
    f"{superset_url}/api/v1/sqllab/execute/",
    headers=headers,
    json=query_data
)

result = response.json()
print(result)
```

### Exportar Dashboard

```python
# Exportar dashboard como PDF
dashboard_id = 1
response = requests.get(
    f"{superset_url}/api/v1/dashboard/{dashboard_id}/export",
    headers=headers
)

with open("dashboard.zip", "wb") as f:
    f.write(response.content)
```

## 🪣 MinIO S3 API

### Python - boto3

```python
import boto3
from io import BytesIO
import pandas as pd

# Configurar cliente S3
s3 = boto3.client(
    's3',
    endpoint_url='http://localhost:9000',
    aws_access_key_id='minioadmin',
    aws_secret_access_key='minioadmin'
)

# Listar buckets
buckets = s3.list_buckets()
for bucket in buckets['Buckets']:
    print(bucket['Name'])

# Listar objetos
objects = s3.list_objects_v2(Bucket='bronze', Prefix='vendas/')
for obj in objects.get('Contents', []):
    print(obj['Key'])

# Upload arquivo
s3.upload_file(
    'local_file.csv',
    'bronze',
    'vendas/data.csv'
)

# Download arquivo
s3.download_file(
    'bronze',
    'vendas/data.csv',
    'downloaded_file.csv'
)

# Ler CSV direto para Pandas
obj = s3.get_object(Bucket='silver', Key='vendas/vendas.parquet')
df = pd.read_parquet(BytesIO(obj['Body'].read()))
print(df.head())
```

### Python - MinIO SDK

```python
from minio import Minio
import pandas as pd
from io import BytesIO

# Cliente MinIO
client = Minio(
    "localhost:9000",
    access_key="minioadmin",
    secret_key="minioadmin",
    secure=False
)

# Criar bucket
if not client.bucket_exists("test"):
    client.make_bucket("test")

# Upload
df = pd.DataFrame({'col1': [1, 2], 'col2': ['a', 'b']})
parquet_buffer = BytesIO()
df.to_parquet(parquet_buffer)
parquet_buffer.seek(0)

client.put_object(
    "test",
    "data.parquet",
    parquet_buffer,
    len(parquet_buffer.getvalue())
)

# Download
response = client.get_object("test", "data.parquet")
df_loaded = pd.read_parquet(BytesIO(response.read()))
print(df_loaded)
```

### cURL - REST API

```bash
# Listar buckets
curl -X GET http://minioadmin:minioadmin@localhost:9000/

# Upload arquivo
curl -X PUT \
  -H "Content-Type: application/octet-stream" \
  --data-binary @data.csv \
  http://minioadmin:minioadmin@localhost:9000/bronze/vendas/data.csv
```

## 🔧 Aplicação Exemplo Completa

### Flask API - Python

```python
from flask import Flask, jsonify, request
from trino.dbapi import connect
import pandas as pd

app = Flask(__name__)

# Conexão Trino
def get_trino_connection():
    return connect(
        host='localhost',
        port=8080,
        user='trino',
        catalog='hive',
        schema='vendas'
    )

@app.route('/vendas/produtos', methods=['GET'])
def listar_produtos():
    """Lista produtos com receita total"""
    conn = get_trino_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT 
            produto,
            SUM(quantidade) as quantidade_total,
            SUM(valor_total) as receita_total
        FROM vendas_silver
        GROUP BY produto
        ORDER BY receita_total DESC
    """)
    
    columns = [desc[0] for desc in cursor.description]
    rows = cursor.fetchall()
    
    result = [dict(zip(columns, row)) for row in rows]
    return jsonify(result)

@app.route('/vendas/analise', methods=['POST'])
def analise_vendas():
    """Análise customizada via JSON"""
    params = request.json
    produto = params.get('produto')
    ano = params.get('ano', 2025)
    
    conn = get_trino_connection()
    cursor = conn.cursor()
    
    query = """
        SELECT 
            mes,
            SUM(quantidade) as quantidade,
            SUM(valor_total) as receita
        FROM vendas_silver
        WHERE produto = ? AND ano = ?
        GROUP BY mes
        ORDER BY mes
    """
    
    # Trino não suporta parâmetros, usar formatação segura
    cursor.execute(f"""
        SELECT 
            mes,
            SUM(quantidade) as quantidade,
            SUM(valor_total) as receita
        FROM vendas_silver
        WHERE produto = '{produto}' AND ano = {ano}
        GROUP BY mes
        ORDER BY mes
    """)
    
    columns = [desc[0] for desc in cursor.description]
    rows = cursor.fetchall()
    
    result = [dict(zip(columns, row)) for row in rows]
    return jsonify(result)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
```

### Node.js API - Express

```javascript
const express = require('express');
const trino = require('trino-client');

const app = express();
app.use(express.json());

const trinoClient = trino.create({
  host: 'localhost',
  port: 8080,
  user: 'trino',
  catalog: 'hive',
  schema: 'vendas'
});

app.get('/vendas/resumo', async (req, res) => {
  const query = `
    SELECT 
      produto,
      COUNT(*) as num_vendas,
      SUM(valor_total) as receita_total
    FROM vendas_silver
    GROUP BY produto
    ORDER BY receita_total DESC
    LIMIT 10
  `;
  
  trinoClient.query(query, (error, data, columns) => {
    if (error) {
      return res.status(500).json({ error: error.message });
    }
    
    const result = data.map(row => {
      const obj = {};
      columns.forEach((col, i) => {
        obj[col.name] = row[i];
      });
      return obj;
    });
    
    res.json(result);
  });
});

app.listen(3000, () => {
  console.log('API rodando em http://localhost:3000');
});
```

## 📚 Bibliotecas Cliente

### Python
```bash
pip install trino
pip install sqlalchemy-trino
pip install apache-airflow-client
pip install boto3
pip install minio
```

### Java
```xml
<!-- Maven -->
<dependency>
    <groupId>io.trino</groupId>
    <artifactId>trino-jdbc</artifactId>
    <version>435</version>
</dependency>
```

### Node.js
```bash
npm install trino-client
npm install @aws-sdk/client-s3
```

### R
```r
install.packages("RJDBC")
install.packages("aws.s3")
```

## 🎓 Próximos Passos

- **Casos de uso práticos:** `08-casos-uso-praticos.md`
- **Segurança e autenticação:** Configurar OAuth/LDAP
- **Monitoramento:** Integrar com Prometheus/Grafana
