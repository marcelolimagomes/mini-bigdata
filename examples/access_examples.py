"""
Script Python: Exemplo de acesso aos dados via diferentes métodos
"""

# ============================================
# 1. ACESSO VIA BOTO3 (MinIO/S3)
# ============================================


def example_boto3():
    """Exemplo de acesso direto ao MinIO via boto3"""
    import boto3
    import pandas as pd
    import io

    # Configurar cliente S3
    s3 = boto3.client(
        's3',
        endpoint_url='http://localhost:9000',
        aws_access_key_id='minioadmin',
        aws_secret_access_key='minioadmin123'
    )

    # Listar buckets
    print("📦 Buckets disponíveis:")
    response = s3.list_buckets()
    for bucket in response['Buckets']:
        print(f"  - {bucket['Name']}")

    # Listar objetos em um bucket
    print("\n📁 Objetos no bucket 'bronze':")
    response = s3.list_objects_v2(Bucket='bronze', Prefix='raw/sales/')
    if 'Contents' in response:
        for obj in response['Contents'][:5]:  # Primeiros 5
            print(f"  - {obj['Key']} ({obj['Size']} bytes)")

    # Ler um arquivo CSV
    try:
        response = s3.get_object(Bucket='bronze', Key='raw/sales/sales_20251021.csv')
        df = pd.read_csv(io.BytesIO(response['Body'].read()))
        print(f"\n📊 Dados carregados: {len(df)} linhas")
        print(df.head())
    except Exception as e:
        print(f"⚠️  Arquivo ainda não existe: {e}")


# ============================================
# 2. ACESSO VIA TRINO (JDBC/Python)
# ============================================

def example_trino():
    """Exemplo de acesso aos dados via Trino"""
    from trino.dbapi import connect
    import pandas as pd

    # Conectar ao Trino
    conn = connect(
        host='localhost',
        port=8085,
        user='trino',
        catalog='hive',
        schema='sales'
    )

    # Executar query
    query = """
        SELECT 
            product_category,
            SUM(total_revenue) as revenue,
            SUM(total_quantity) as items_sold
        FROM sales_by_category
        GROUP BY product_category
        ORDER BY revenue DESC
    """

    # Carregar em DataFrame
    df = pd.read_sql(query, conn)
    print("📊 Top categorias por receita:")
    print(df)

    # Executar query simples
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) as total FROM sales_silver")
    result = cur.fetchone()
    print(f"\n📈 Total de transações: {result[0]:,}")

    conn.close()


# ============================================
# 3. ACESSO VIA REST API (Trino)
# ============================================

def example_trino_rest():
    """Exemplo de acesso via REST API do Trino"""
    import requests
    import json

    # Endpoint do Trino
    url = "http://localhost:8085/v1/statement"

    # Headers
    headers = {
        "X-Trino-User": "trino",
        "X-Trino-Catalog": "hive",
        "X-Trino-Schema": "sales"
    }

    # Query
    query = "SELECT product_category, SUM(total_revenue) as revenue FROM sales_by_category GROUP BY product_category ORDER BY revenue DESC LIMIT 5"

    # Executar query
    response = requests.post(url, headers=headers, data=query)

    if response.status_code == 200:
        result = response.json()
        print("📊 Resposta da API:")
        print(json.dumps(result, indent=2))

        # Se houver nextUri, buscar resultados
        if 'nextUri' in result:
            next_response = requests.get(result['nextUri'], headers=headers)
            data = next_response.json()

            if 'data' in data:
                print("\n📈 Dados retornados:")
                for row in data['data']:
                    print(f"  {row[0]}: ${row[1]:,.2f}")
    else:
        print(f"❌ Erro: {response.status_code}")


# ============================================
# 4. PROCESSAR DADOS COM PYSPARK
# ============================================

def example_pyspark():
    """Exemplo de processamento com PySpark"""
    from pyspark.sql import SparkSession

    # Criar sessão Spark
    spark = SparkSession.builder \
        .appName("Example Analysis") \
        .config("spark.hadoop.fs.s3a.endpoint", "http://localhost:9000") \
        .config("spark.hadoop.fs.s3a.access.key", "minioadmin") \
        .config("spark.hadoop.fs.s3a.secret.key", "minioadmin123") \
        .config("spark.hadoop.fs.s3a.path.style.access", "true") \
        .config("spark.hadoop.fs.s3a.impl", "org.apache.hadoop.fs.s3a.S3AFileSystem") \
        .getOrCreate()

    # Ler dados do Silver
    df = spark.read.parquet("s3a://silver/processed/sales/")

    print(f"📊 Total de registros: {df.count()}")

    # Análise
    from pyspark.sql.functions import sum, count, avg

    analysis = df.groupBy("product_category") \
        .agg(
            sum("total_amount").alias("revenue"),
            count("*").alias("transactions"),
            avg("total_amount").alias("avg_value")
    ) \
        .orderBy("revenue", ascending=False)

    print("\n📈 Análise por categoria:")
    analysis.show()

    spark.stop()


# ============================================
# 5. UPLOAD DE DADOS PARA MinIO
# ============================================

def example_upload_data():
    """Exemplo de upload de dados para o MinIO"""
    import boto3
    import pandas as pd
    import io
    from datetime import datetime

    s3 = boto3.client(
        's3',
        endpoint_url='http://localhost:9000',
        aws_access_key_id='minioadmin',
        aws_secret_access_key='minioadmin123'
    )

    # Criar DataFrame de exemplo
    data = {
        'id': range(1, 11),
        'name': [f'Item_{i}' for i in range(1, 11)],
        'value': [100 * i for i in range(1, 11)]
    }
    df = pd.DataFrame(data)

    # Salvar como CSV
    csv_buffer = io.StringIO()
    df.to_csv(csv_buffer, index=False)

    # Upload para MinIO
    key = f'examples/sample_data_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
    s3.put_object(
        Bucket='bronze',
        Key=key,
        Body=csv_buffer.getvalue()
    )

    print(f"✅ Arquivo enviado: s3://bronze/{key}")


# ============================================
# 6. CRIAR CONEXÃO NO SUPERSET (via API)
# ============================================

def example_superset_api():
    """Exemplo de criar conexão no Superset via API"""
    import requests

    # Login no Superset
    login_url = "http://localhost:8088/api/v1/security/login"
    login_data = {
        "username": "admin",
        "password": "admin",
        "provider": "db",
        "refresh": True
    }

    session = requests.Session()
    response = session.post(login_url, json=login_data)

    if response.status_code == 200:
        token = response.json()['access_token']
        print("✅ Login realizado com sucesso")

        # Criar database connection
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }

        db_data = {
            "database_name": "Trino - Sales DB",
            "sqlalchemy_uri": "trino://trino@trino:8080/hive/sales",
            "expose_in_sqllab": True
        }

        db_url = "http://localhost:8088/api/v1/database/"
        db_response = session.post(db_url, json=db_data, headers=headers)

        if db_response.status_code in [200, 201]:
            print("✅ Conexão criada no Superset")
        else:
            print(f"⚠️  Status: {db_response.status_code}")
    else:
        print(f"❌ Erro no login: {response.status_code}")


# ============================================
# MAIN - Executar exemplos
# ============================================

if __name__ == "__main__":
    print("=" * 60)
    print("🚀 EXEMPLOS DE ACESSO AOS DADOS")
    print("=" * 60)

    print("\n1️⃣  Acesso via Boto3 (MinIO/S3)")
    print("-" * 60)
    try:
        example_boto3()
    except Exception as e:
        print(f"❌ Erro: {e}")

    print("\n2️⃣  Acesso via Trino (Python DBAPI)")
    print("-" * 60)
    try:
        # Descomentar quando o Trino estiver rodando e com dados
        # example_trino()
        print("⚠️  Descomente a função para testar")
    except Exception as e:
        print(f"❌ Erro: {e}")

    print("\n3️⃣  Acesso via REST API (Trino)")
    print("-" * 60)
    try:
        # example_trino_rest()
        print("⚠️  Descomente a função para testar")
    except Exception as e:
        print(f"❌ Erro: {e}")

    print("\n4️⃣  Upload de dados")
    print("-" * 60)
    try:
        example_upload_data()
    except Exception as e:
        print(f"❌ Erro: {e}")

    print("\n" + "=" * 60)
    print("✅ Exemplos concluídos!")
    print("=" * 60)
