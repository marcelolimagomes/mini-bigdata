# 🌊 Criando Pipelines ETL com Apache Airflow

## 📚 Conceitos Básicos

### O que é um DAG?
DAG (Directed Acyclic Graph) é um pipeline de tarefas no Airflow. Cada tarefa representa uma operação (extração, transformação, carga, etc).

### Estrutura de um DAG
```python
from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta

# Configurações padrão
default_args = {
    'owner': 'data-team',
    'retries': 2,
    'retry_delay': timedelta(minutes=5)
}

# Definição do DAG
with DAG(
    'meu_pipeline_etl',
    default_args=default_args,
    description='Pipeline ETL simples',
    schedule_interval='@daily',
    start_date=datetime(2025, 1, 1),
    catchup=False,
    tags=['etl', 'exemplo']
) as dag:
    
    # Tarefas aqui
    pass
```

## 🎯 Exemplo 1: Pipeline ETL Básico

### Arquivo: `dags/etl_vendas_basico.py`

```python
from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import pandas as pd
import boto3
from io import StringIO

default_args = {
    'owner': 'data-team',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

# Configuração MinIO (S3)
s3_config = {
    'endpoint_url': 'http://minio:9000',
    'aws_access_key_id': 'minioadmin',
    'aws_secret_access_key': 'minioadmin123'
}

def extrair_dados_bronze(**context):
    """Extrai dados do bucket bronze"""
    s3 = boto3.client('s3', **s3_config)
    
    # Ler arquivo CSV do bronze
    obj = s3.get_object(Bucket='bronze', Key='vendas/vendas.csv')
    df = pd.read_csv(obj['Body'])
    
    print(f"✅ Extraídos {len(df)} registros")
    
    # Salvar em XCom para próxima tarefa
    context['task_instance'].xcom_push(key='dados_brutos', value=df.to_json())
    return len(df)

def transformar_dados(**context):
    """Transforma e limpa os dados"""
    # Recuperar dados da tarefa anterior
    dados_json = context['task_instance'].xcom_pull(
        task_ids='extrair_bronze',
        key='dados_brutos'
    )
    df = pd.read_json(dados_json)
    
    # Transformações
    df['data'] = pd.to_datetime(df['data'])
    df['valor_total'] = df['quantidade'] * df['valor']
    df['mes'] = df['data'].dt.to_period('M').astype(str)
    
    # Validações
    df = df[df['quantidade'] > 0]
    df = df[df['valor'] > 0]
    df = df.dropna()
    
    print(f"✅ Transformados {len(df)} registros válidos")
    
    context['task_instance'].xcom_push(key='dados_limpos', value=df.to_json())
    return len(df)

def carregar_dados_silver(**context):
    """Carrega dados no bucket silver"""
    # Recuperar dados transformados
    dados_json = context['task_instance'].xcom_pull(
        task_ids='transformar',
        key='dados_limpos'
    )
    df = pd.read_json(dados_json)
    
    # Salvar no MinIO (silver)
    s3 = boto3.client('s3', **s3_config)
    
    csv_buffer = StringIO()
    df.to_csv(csv_buffer, index=False)
    
    s3.put_object(
        Bucket='silver',
        Key='vendas/vendas_processadas.csv',
        Body=csv_buffer.getvalue()
    )
    
    print(f"✅ Carregados {len(df)} registros no silver")
    return len(df)

def agregar_dados(**context):
    """Agrega dados para análise"""
    dados_json = context['task_instance'].xcom_pull(
        task_ids='transformar',
        key='dados_limpos'
    )
    df = pd.read_json(dados_json)
    
    # Agregações
    vendas_por_mes = df.groupby('mes').agg({
        'quantidade': 'sum',
        'valor_total': 'sum'
    }).reset_index()
    
    vendas_por_produto = df.groupby('produto').agg({
        'quantidade': 'sum',
        'valor_total': 'sum'
    }).reset_index()
    
    # Salvar agregações no gold
    s3 = boto3.client('s3', **s3_config)
    
    # Vendas por mês
    csv_buffer = StringIO()
    vendas_por_mes.to_csv(csv_buffer, index=False)
    s3.put_object(
        Bucket='gold',
        Key='vendas/vendas_por_mes.csv',
        Body=csv_buffer.getvalue()
    )
    
    # Vendas por produto
    csv_buffer = StringIO()
    vendas_por_produto.to_csv(csv_buffer, index=False)
    s3.put_object(
        Bucket='gold',
        Key='vendas/vendas_por_produto.csv',
        Body=csv_buffer.getvalue()
    )
    
    print(f"✅ Agregações salvas no gold")

# Definição do DAG
with DAG(
    'etl_vendas_basico',
    default_args=default_args,
    description='Pipeline ETL de vendas - Bronze → Silver → Gold',
    schedule_interval='@daily',
    start_date=datetime(2025, 1, 1),
    catchup=False,
    tags=['etl', 'vendas', 'exemplo']
) as dag:
    
    # Definir tarefas
    extrair = PythonOperator(
        task_id='extrair_bronze',
        python_callable=extrair_dados_bronze
    )
    
    transformar = PythonOperator(
        task_id='transformar',
        python_callable=transformar_dados
    )
    
    carregar = PythonOperator(
        task_id='carregar_silver',
        python_callable=carregar_dados_silver
    )
    
    agregar = PythonOperator(
        task_id='agregar_gold',
        python_callable=agregar_dados
    )
    
    # Definir ordem de execução
    extrair >> transformar >> [carregar, agregar]
```

## 📂 Onde Colocar o DAG

```bash
# Copiar para a pasta de DAGs
cp etl_vendas_basico.py /media/marcelo/dados1/bigdata-docker/airflow/dags/

# Ou usar o volume montado
cp etl_vendas_basico.py ./examples/dags/
```

O Airflow detecta novos DAGs automaticamente em cerca de 30 segundos.

## ▶️ Executando o Pipeline

### Via Interface Web

1. Acesse http://localhost:8080
2. Faça login (airflow/airflow)
3. Localize o DAG `etl_vendas_basico`
4. Ative o toggle para habilitar
5. Clique em "▶" (Trigger DAG) para executar

### Via CLI

```bash
# Entrar no container
docker exec -it airflow-webserver bash

# Listar DAGs
airflow dags list

# Testar uma tarefa específica
airflow tasks test etl_vendas_basico extrair_bronze 2025-01-01

# Executar o DAG completo
airflow dags trigger etl_vendas_basico
```

## 🔍 Monitorando a Execução

### Ver Status
- **Graph View:** Visualização gráfica das tarefas
- **Tree View:** Histórico de execuções
- **Gantt View:** Timeline de execução
- **Logs:** Clique em uma tarefa → View Log

### Verificar Dados Gerados

```bash
# Listar arquivos no MinIO
docker exec -it minio-client mc ls myminio/silver/vendas/
docker exec -it minio-client mc ls myminio/gold/vendas/
```

## 🎯 Exemplo 2: Pipeline com Spark

### Arquivo: `dags/etl_vendas_spark.py`

```python
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.apache.spark.operators.spark_submit import SparkSubmitOperator
from datetime import datetime, timedelta

default_args = {
    'owner': 'data-team',
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

with DAG(
    'etl_vendas_spark',
    default_args=default_args,
    description='Pipeline ETL usando Spark',
    schedule_interval='@daily',
    start_date=datetime(2025, 1, 1),
    catchup=False,
    tags=['etl', 'spark', 'vendas']
) as dag:
    
    processar_spark = SparkSubmitOperator(
        task_id='processar_vendas_spark',
        application='/opt/airflow/jobs/process_sales.py',
        conn_id='spark_default',
        conf={
            'spark.master': 'spark://spark-master:7077',
            'spark.executor.memory': '2g',
            'spark.executor.cores': '2'
        },
        application_args=[
            '--input-path', 's3a://bronze/vendas/',
            '--output-path', 's3a://silver/vendas/'
        ]
    )
```

## 📊 Boas Práticas

### 1. Usar XCom para Passar Dados entre Tarefas
```python
# Enviar dados
context['task_instance'].xcom_push(key='minha_chave', value=dados)

# Receber dados
dados = context['task_instance'].xcom_pull(task_ids='tarefa_anterior', key='minha_chave')
```

### 2. Tratamento de Erros
```python
def minha_tarefa(**context):
    try:
        # Seu código
        pass
    except Exception as e:
        print(f"❌ Erro: {e}")
        raise  # Re-lançar para marcar tarefa como falha
```

### 3. Logging Adequado
```python
import logging

def minha_tarefa(**context):
    logging.info("Iniciando processamento...")
    logging.warning("Atenção: dados inconsistentes")
    logging.error("Erro crítico!")
```

### 4. Parametrização
```python
from airflow.models import Variable

# Definir variável na UI: Admin → Variables
db_conn = Variable.get("database_connection")
```

## 🔄 Agendamento de DAGs

```python
# Diariamente às 2h da manhã
schedule_interval='0 2 * * *'

# A cada hora
schedule_interval='@hourly'

# Semanalmente (segunda-feira)
schedule_interval='0 0 * * 1'

# Apenas manual
schedule_interval=None
```

## 📋 Dependências Externas

### Instalar Pacotes Python no Airflow

1. Criar arquivo `requirements.txt`:
```
pandas==2.0.0
boto3==1.26.0
sqlalchemy==2.0.0
```

2. Adicionar ao docker-compose.yml:
```yaml
environment:
  _PIP_ADDITIONAL_REQUIREMENTS: ${_PIP_ADDITIONAL_REQUIREMENTS:- pandas boto3 sqlalchemy}
```

## 🆘 Troubleshooting

### DAG não aparece
- Verifique erros de sintaxe Python
- Aguarde 30 segundos (intervalo de scan)
- Verifique logs: `docker compose logs airflow-scheduler`

### Tarefa falha
- Clique na tarefa → View Log
- Verifique variáveis de ambiente
- Teste a função Python isoladamente

### Dados não aparecem no MinIO
- Verifique credenciais S3
- Confirme permissões do bucket
- Verifique logs da tarefa

## 🎓 Próximos Passos

- **Processamento com Spark:** `03-processamento-spark.md`
- **Consultas SQL:** `04-consultas-trino.md`
- **Dashboards:** `05-criando-dashboards-superset.md`
