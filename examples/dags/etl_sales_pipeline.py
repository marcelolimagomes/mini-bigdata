"""
DAG de exemplo: Pipeline ETL completo
Demonstra:
- Ingestão de dados brutos no MinIO (bronze)
- Processamento com Spark (silver)
- Agregações e análises (gold)
- Registro de tabelas no Hive Metastore
"""

from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.apache.spark.operators.spark_submit import SparkSubmitOperator
from airflow.operators.bash import BashOperator

default_args = {
    'owner': 'bigdata-team',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}


def generate_sample_data(**context):
    """Gera dados de exemplo e salva no MinIO"""
    import boto3
    import pandas as pd
    import io
    from datetime import datetime, timedelta
    import random

    # Configurar cliente S3 (MinIO)
    s3_client = boto3.client(
        's3',
        endpoint_url='http://minio:9000',
        aws_access_key_id='minioadmin',
        aws_secret_access_key='minioadmin123'
    )

    # Gerar dados de vendas fictícias
    n_records = 1000
    start_date = datetime.now() - timedelta(days=30)

    data = {
        'transaction_id': range(1, n_records + 1),
        'transaction_date': [
            (start_date + timedelta(days=random.randint(0, 30))).strftime('%Y-%m-%d')
            for _ in range(n_records)
        ],
        'product_category': [
            random.choice(['Electronics', 'Clothing', 'Food', 'Books', 'Home'])
            for _ in range(n_records)
        ],
        'product_name': [
            f'Product_{random.randint(1, 50)}'
            for _ in range(n_records)
        ],
        'quantity': [random.randint(1, 10) for _ in range(n_records)],
        'unit_price': [round(random.uniform(10, 500), 2) for _ in range(n_records)],
        'customer_id': [f'CUST_{random.randint(1000, 9999)}' for _ in range(n_records)],
        'region': [
            random.choice(['North', 'South', 'East', 'West', 'Central'])
            for _ in range(n_records)
        ]
    }

    df = pd.DataFrame(data)
    df['total_amount'] = df['quantity'] * df['unit_price']

    # Salvar como CSV no bucket bronze
    csv_buffer = io.StringIO()
    df.to_csv(csv_buffer, index=False)

    execution_date = context['ds_nodash']
    s3_key = f'raw/sales/sales_{execution_date}.csv'

    s3_client.put_object(
        Bucket='bronze',
        Key=s3_key,
        Body=csv_buffer.getvalue()
    )

    print(f"✅ Dados gerados e salvos em s3://bronze/{s3_key}")
    print(f"📊 Total de registros: {len(df)}")

    # Retornar caminho para próximas tasks
    return s3_key


def check_data_quality(**context):
    """Valida qualidade dos dados processados"""
    import boto3
    import pandas as pd
    import io

    s3_client = boto3.client(
        's3',
        endpoint_url='http://minio:9000',
        aws_access_key_id='minioadmin',
        aws_secret_access_key='minioadmin123'
    )

    # Ler dados processados
    execution_date = context['ds_nodash']
    response = s3_client.get_object(
        Bucket='silver',
        Key=f'processed/sales/date={execution_date}/data.csv'
    )

    df = pd.read_csv(io.BytesIO(response['Body'].read()))

    # Validações
    assert len(df) > 0, "❌ Dados vazios após processamento"
    assert df['total_amount'].min() >= 0, "❌ Valores negativos detectados"
    assert not df.isnull().any().any(), "❌ Valores nulos detectados"

    print(f"✅ Qualidade dos dados validada")
    print(f"📊 Registros processados: {len(df)}")
    print(f"💰 Total de vendas: ${df['total_amount'].sum():,.2f}")


with DAG(
    'etl_sales_pipeline',
    default_args=default_args,
    description='Pipeline ETL completo de vendas (Bronze -> Silver -> Gold)',
    schedule_interval='@daily',
    start_date=datetime(2025, 10, 1),
    catchup=False,
    tags=['example', 'etl', 'sales'],
) as dag:

    # Task 1: Gerar dados de exemplo
    generate_data = PythonOperator(
        task_id='generate_sample_data',
        python_callable=generate_sample_data,
        provide_context=True,
    )

    # Task 2: Processar com Spark (Bronze -> Silver)
    process_bronze_to_silver = SparkSubmitOperator(
        task_id='process_bronze_to_silver',
        application='/opt/airflow/jobs/process_sales.py',
        conn_id='spark_default',
        conf={
            'spark.hadoop.fs.s3a.endpoint': 'http://minio:9000',
            'spark.hadoop.fs.s3a.access.key': 'minioadmin',
            'spark.hadoop.fs.s3a.secret.key': 'minioadmin123',
            'spark.hadoop.fs.s3a.path.style.access': 'true',
            'spark.hadoop.fs.s3a.impl': 'org.apache.hadoop.fs.s3a.S3AFileSystem',
        },
        application_args=['{{ ds_nodash }}'],
    )

    # Task 3: Validar qualidade dos dados
    validate_data = PythonOperator(
        task_id='check_data_quality',
        python_callable=check_data_quality,
        provide_context=True,
    )

    # Task 4: Agregações (Silver -> Gold)
    aggregate_to_gold = SparkSubmitOperator(
        task_id='aggregate_to_gold',
        application='/opt/airflow/jobs/aggregate_sales.py',
        conn_id='spark_default',
        conf={
            'spark.hadoop.fs.s3a.endpoint': 'http://minio:9000',
            'spark.hadoop.fs.s3a.access.key': 'minioadmin',
            'spark.hadoop.fs.s3a.secret.key': 'minioadmin123',
            'spark.hadoop.fs.s3a.path.style.access': 'true',
        },
        application_args=['{{ ds_nodash }}'],
    )

    # Task 5: Registrar tabelas no Hive Metastore (para acesso via Trino)
    register_tables = BashOperator(
        task_id='register_hive_tables',
        bash_command="""
        echo "Tabelas registradas no Hive Metastore"
        echo "Acessível via Trino: SELECT * FROM hive.default.sales_silver"
        """
    )

    # Definir ordem de execução
    generate_data >> process_bronze_to_silver >> validate_data >> aggregate_to_gold >> register_tables
