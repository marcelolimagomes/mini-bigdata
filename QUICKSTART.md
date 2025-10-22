# 🚀 Quick Start Guide

## Início Rápido em 5 Minutos

### 1. Preparar ambiente
```bash
# Clonar/navegar para o diretório
cd mini-bigdata

# Executar setup
chmod +x setup.sh
./setup.sh
```

### 2. Iniciar serviços
```bash
docker-compose up -d
```

### 3. Aguardar inicialização (2-3 minutos)
```bash
# Acompanhar logs
docker-compose logs -f

# Verificar status
docker-compose ps
```

### 4. Acessar interfaces

| Serviço | URL | Credenciais |
|---------|-----|-------------|
| **MinIO** | http://localhost:9001 | minioadmin / minioadmin123 |
| **Airflow** | http://localhost:8080 | airflow / airflow |
| **Superset** | http://localhost:8088 | admin / admin |
| **Trino** | http://localhost:8085 | trino (sem senha) |
| **Spark** | http://localhost:8081 | - |

### 5. Executar primeiro pipeline

1. Acesse Airflow: http://localhost:8080
2. Ative a DAG `etl_sales_pipeline`
3. Clique em "Trigger DAG"
4. Acompanhe a execução

### 6. Consultar dados processados

**Via Trino Web UI:**
- Acesse: http://localhost:8085
- Execute: `SELECT * FROM hive.sales.sales_silver LIMIT 10`

**Via Python:**
```python
from trino.dbapi import connect

conn = connect(
    host='localhost',
    port=8085,
    user='trino',
    catalog='hive',
    schema='sales'
)

cur = conn.cursor()
cur.execute("SELECT COUNT(*) FROM sales_silver")
print(cur.fetchone())
```

### 7. Criar Dashboard no Superset

1. Acesse: http://localhost:8088
2. Login: admin / admin
3. Settings > Database Connections > + Database
4. **Connection String**: `trino://trino@trino:8080/hive/sales`
5. Test Connection > Connect
6. SQL Lab > SQL Editor
7. Execute queries e crie visualizações

## Próximos Passos

### Upload de seus próprios dados
```python
import boto3

s3 = boto3.client(
    's3',
    endpoint_url='http://localhost:9000',
    aws_access_key_id='minioadmin',
    aws_secret_access_key='minioadmin123'
)

# Upload arquivo
s3.upload_file('meu_arquivo.csv', 'bronze', 'raw/meus_dados.csv')
```

### Criar sua própria DAG

1. Criar arquivo em `examples/dags/minha_dag.py`:
```python
from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime

def minha_funcao():
    print("Olá Big Data!")

with DAG('minha_dag', start_date=datetime(2025, 1, 1), schedule_interval='@daily') as dag:
    task = PythonOperator(task_id='task1', python_callable=minha_funcao)
```

2. DAG aparecerá automaticamente no Airflow

### Criar Job Spark

1. Criar arquivo em `examples/jobs/meu_job.py`:
```python
from pyspark.sql import SparkSession

spark = SparkSession.builder.appName("MeuJob").getOrCreate()
df = spark.read.csv("s3a://bronze/raw/meus_dados.csv", header=True)
df.show()
```

2. Executar:
```bash
docker-compose exec spark-master \
  spark-submit \
  --master spark://spark-master:7077 \
  /opt/spark-jobs/meu_job.py
```

## Dicas Úteis

### Verificar saúde dos serviços
```bash
docker-compose ps
docker-compose logs -f <service_name>
```

### Reiniciar um serviço
```bash
docker-compose restart airflow-webserver
```

### Parar tudo
```bash
docker-compose down
```

### Limpar tudo (incluindo dados)
```bash
docker-compose down -v
rm -rf data/
./setup.sh
docker-compose up -d
```

## Estrutura de Dados Recomendada

```
MinIO Buckets:
├── bronze/       # Dados brutos (CSV, JSON, etc.)
├── silver/       # Dados processados (Parquet)
└── gold/         # Dados analíticos (Agregações)
```

## Comandos Essenciais

```bash
# Ver logs em tempo real
docker-compose logs -f

# Entrar em um container
docker-compose exec airflow-webserver bash

# Reiniciar com rebuild
docker-compose up -d --build --force-recreate

# Ver uso de recursos
docker stats

# Backup de dados
tar -czf backup.tar.gz data/
```

## Troubleshooting

Se algo não funcionar:

1. Verificar logs: `docker-compose logs -f`
2. Verificar portas livres: `sudo netstat -tulpn | grep 8080`
3. Limpar e recriar: `docker-compose down -v && docker-compose up -d`
4. Consultar: `TROUBLESHOOTING.md`

## Suporte

- README.md - Documentação completa
- TROUBLESHOOTING.md - Solução de problemas
- examples/ - Exemplos práticos
