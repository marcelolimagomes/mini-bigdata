# 🚀 Mini Big Data Platform

<div align="center">

![Big Data](https://img.shields.io/badge/Big%20Data-Platform-blue?style=for-the-badge)
![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?style=for-the-badge&logo=docker&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)

**Uma stack Big Data completa e enxuta para desenvolvimento local**

[Características](#-características) •
[Componentes](#-componentes) •
[Quick Start](#-quick-start) •
[Documentação](#-documentação) •
[Exemplos](#-exemplos-práticos)

</div>

---

## 📖 Sobre o Projeto

O **Mini Big Data Platform** é uma prova de conceito (PoC) de uma arquitetura Big Data moderna, completa e escalável, projetada para rodar localmente via Docker Compose. Este projeto foi desenvolvido com o objetivo de facilitar o aprendizado, experimentação e desenvolvimento de soluções de dados sem a necessidade de infraestrutura cloud.

### 🎯 Objetivo

Fornecer um ambiente Big Data **totalmente funcional** que pode ser executado em uma máquina local, permitindo que desenvolvedores, engenheiros de dados e entusiastas possam:

- 🧪 **Experimentar** tecnologias Big Data sem custos de cloud
- 📚 **Aprender** arquiteturas modernas de dados (Data Lake, Lakehouse)
- 🔬 **Desenvolver** e testar pipelines ETL/ELT
- 🎓 **Ensinar** conceitos de engenharia de dados
- 🚀 **Prototipar** soluções antes de deployar em produção

### ⚡ Características

- ✅ **Setup Automatizado**: 1 comando para configurar tudo (~8 minutos)
- ✅ **Arquitetura Completa**: Storage, processamento, catálogo, orquestração e visualização
- ✅ **Totalmente Containerizado**: Infraestrutura como código com Docker Compose
- ✅ **Production-Ready**: Mesmas tecnologias usadas em ambientes corporativos
- ✅ **S3-Compatible**: Utiliza MinIO como alternativa local ao AWS S3
- ✅ **Integração Nativa**: Todos os componentes comunicam-se nativamente
- ✅ **Persistência de Dados**: Dados salvos em disco externo para segurança
- ✅ **Validação Automática**: Scripts de validação de todos os serviços

## �️ Componentes

| Componente | Tecnologia | Porta | Descrição |
|------------|-----------|-------|-----------|
| **Object Storage** | MinIO | 9000, 9001 | Armazenamento S3-compatible para Data Lake |
| **Cache/Results** | Redis | 6379 | Cache e Results Backend para Superset |
| **Orquestrador ETL** | Apache Airflow | 8080 | Orquestração de workflows e pipelines |
| **Processamento** | Apache Spark | 8081, 7077 | Engine de processamento distribuído (PySpark) |
| **Query Engine** | Trino | 8085 | SQL distribuído com acesso JDBC/REST |
| **Metastore** | Hive Metastore | 9083 | Catálogo de dados centralizado |
| **Database** | PostgreSQL | 5432 | Banco relacional para metadados |
| **BI/Dashboards** | Apache Superset | 8088 | Plataforma de visualização e dashboards |

> 📝 **Nota**: O Apache Superset está configurado com **Redis Results Backend**, permitindo execução de queries SQL via API e armazenamento de resultados temporários.

## 🏗️ Arquitetura

A plataforma segue uma arquitetura em camadas (layered architecture), separando responsabilidades e permitindo escalabilidade horizontal:

```
┌─────────────────────────────────────────────────────────────┐
│                  📊 Camada de Apresentação                  │
│                                                             │
│  ┌──────────────────┐              ┌──────────────────┐     │
│  │ Apache Superset  │              │  Acesso Externo  │     │
│  │   (Dashboards)   │              │   JDBC/REST API  │     │
│  └────────┬─────────┘              └────────┬─────────┘     │
└───────────┼─────────────────────────────────┼───────────────┘
            │                                 │
┌───────────┼─────────────────────────────────┼───────────────┐
│           │      🔍 Camada de Acesso         │              │
│           └────────────┬────────────────────┘               │
│                        │                                    │
│                  ┌─────▼──────┐                             │
│                  │   Trino    │◄─────────┐                  │
│                  │  SQL Engine│          │                  │
│                  └─────┬──────┘    ┌─────▼──────┐           │
│                        │           │    Hive    │           │
│                        │           │ Metastore  │           │
│                        │           └────────────┘           │
└────────────────────────┼────────────────────────────────────┘
                         │
┌────────────────────────┼────────────────────────────────────┐
│           ⚙️ Camada de Processamento                        │
│                  ┌─────▼──────┐                             │
│                  │   Spark    │                             │
│                  │  (Workers) │                             │
│                  └─────┬──────┘                             │
│                        │                                    │
│                  ┌─────▼──────┐                             │
│                  │  Airflow   │                             │
│                  │(Orchestrator)                            │
│                  └─────┬──────┘                             │
└────────────────────────┼────────────────────────────────────┘
                         │
┌────────────────────────┼────────────────────────────────────┐
│              💾 Camada de Storage                           │
│                  ┌─────▼──────┐    ┌──────────────┐         │
│                  │   MinIO    │    │ PostgreSQL   │         │
│                  │ (Data Lake)│    │  (Metadata)  │         │
│                  └────────────┘    └──────────────┘         │
└─────────────────────────────────────────────────────────────┘
```

### 🔄 Fluxo de Dados

1. **Ingestão**: Dados brutos chegam via APIs, arquivos ou streaming
2. **Storage**: Armazenados no MinIO (Bronze layer)
3. **Orquestração**: Airflow agenda e dispara jobs de processamento
4. **Processamento**: Spark processa dados (Silver/Gold layers)
5. **Catalogação**: Hive Metastore mantém metadados e schemas
6. **Acesso**: Trino permite queries SQL sobre os dados
7. **Visualização**: Superset cria dashboards e relatórios

## 🎯 Casos de Uso

### 1. 📦 **Pipeline ETL Completo**
- Ingestão de dados de múltiplas fontes (APIs, arquivos, databases)
- Transformação com Spark (limpeza, agregação, enriquecimento)
- Armazenamento em camadas (Bronze → Silver → Gold)
- Catalogação automática via Hive Metastore
- Orquestração com Airflow (scheduling, retry, alertas)

### 2. 🔍 **Data Lake & Analytics**
- Armazenamento S3-compatible com MinIO
- Queries SQL federadas com Trino
- Acesso via JDBC para ferramentas BI (Power BI, Tableau, Metabase)
- REST API para aplicações e microserviços
- Análises ad-hoc com SQL Lab (Superset)

### 3. 📊 **Business Intelligence**
- Dashboards interativos com Apache Superset
- Métricas em tempo real
- Relatórios agendados
- Self-service analytics para usuários de negócio

### 4. 🧪 **Prototipagem e Testes**
- Testar arquiteturas Data Lake/Lakehouse
- Validar pipelines antes de produção
- Benchmarking de performance
- Treinamento de equipes

## 🚀 Quick Start

### 📋 Pré-requisitos

Antes de iniciar, certifique-se de ter:

- **Docker** >= 20.10 ([Instalar](https://docs.docker.com/engine/install/))
- **Docker Compose** >= 2.0 ([Instalar](https://docs.docker.com/compose/install/))
- **Python 3** >= 3.8 (para scripts de automação)
- **Recursos Mínimos**:
  - 8GB RAM disponível
  - 20GB espaço em disco
  - CPU com 4+ cores (recomendado)
- **Portas Livres**: 5432, 6379, 7077, 8080-8088, 9000-9001, 9083

### ⚡ Setup Automatizado (Recomendado)

**Opção 1: Setup completo com 1 comando** 🎯

```bash
# Clonar repositório
git clone https://github.com/marcelolimagomes/mini-bigdata.git
cd mini-bigdata

# Executar setup automatizado
python3 scripts/full_setup.py
```

**Tempo estimado:** ~8 minutos  
**O que faz:**
- ✅ Cria estrutura de diretórios
- ✅ Limpa ambiente Docker
- ✅ Constrói imagens personalizadas
- ✅ Inicia todos os serviços em ordem
- ✅ Valida health checks
- ✅ Configura MinIO, Trino e Superset

**Opção 2: Script Shell** (alternativa)

```bash
./scripts/shell/full-setup.sh
```

### 🔧 Setup Manual (Avançado)

Se preferir ter mais controle sobre o processo:

**1. Criar estrutura de diretórios**

```bash
sudo mkdir -p /media/marcelo/dados1/bigdata-docker/{postgres,minio,hive,trino,superset,redis,airflow/{dags,logs,plugins},spark/{master,worker}}
sudo chmod -R 755 /media/marcelo/dados1/bigdata-docker
```

> ⚠️ **Nota**: Ajuste o caminho `/media/marcelo/dados1/bigdata-docker` se necessário no arquivo `docker-compose.yml`.

**2. Construir imagens personalizadas**

```bash
docker compose build hive-metastore trino
```

**3. Iniciar serviços**

```bash
# Iniciar todos os containers em background
docker-compose up -d

# Verificar status dos serviços
docker-compose ps

# Acompanhar logs (Ctrl+C para sair)
docker-compose logs -f
```

**4. Aguarde a inicialização**

O primeiro start pode levar 3-5 minutos. Aguarde até que todos os serviços estejam `healthy`:

```bash
# Verificar saúde dos containers
docker-compose ps

# OU validar todos os serviços com script Python
source .venv/bin/activate  # (se configurou o ambiente virtual)
python3 scripts/validate_all_services.py
```

### 🌐 Acesso às Interfaces

### 🌐 Acesso às Interfaces

Após a inicialização, acesse as interfaces web:

| Serviço | URL | Usuário | Senha |
|---------|-----|---------|-------|
| **MinIO Console** | http://localhost:9001 | `minioadmin` | `minioadmin123` |
| **Airflow** | http://localhost:8080 | `airflow` | `airflow` |
| **Superset** | http://localhost:8088 | `admin` | `admin` |
| **Trino UI** | http://localhost:8085 | `trino` | *(sem senha)* |
| **Spark Master** | http://localhost:8081 | - | - |

> 🔒 **Importante**: Altere as credenciais padrão antes de usar em ambientes não-locais!

### � Persistência de Dados

Todos os dados são persistidos externamente em:

```
/media/marcelo/dados1/bigdata-docker/
├── postgres/      # Metadados do sistema
├── minio/         # Data Lake (arquivos principais)
├── airflow/       # DAGs, logs e plugins
├── hive/          # Warehouse do Hive
├── spark/         # Jobs e checkpoints
├── trino/         # Cache de queries
└── superset/      # Configurações e dashboards
```

📖 **Documentação completa**: [STORAGE.md](STORAGE.md)

## 📚 Documentação

Este projeto possui documentação detalhada para cada componente:

- 📖 **[Guia de Início Rápido](docs/01-guia-inicio-rapido.md)** - Primeiros passos
- 🔄 **[Criando Pipelines Airflow](docs/02-criando-pipelines-airflow.md)** - DAGs e workflows
- ⚡ **[Processamento com Spark](docs/03-processamento-spark.md)** - Jobs PySpark
- 🔍 **[Consultas com Trino](docs/04-consultas-trino.md)** - SQL distribuído
- 📊 **[Dashboards Superset](docs/05-criando-dashboards-superset.md)** - Visualizações
- 📁 **[Catálogo Hive Metastore](docs/06-catalogo-hive-metastore.md)** - Gestão de metadados
- 🔌 **[APIs REST e JDBC](docs/07-apis-rest-jdbc.md)** - Conectividade externa
- 💼 **[Casos de Uso Práticos](docs/08-casos-uso-praticos.md)** - Exemplos reais
- ⚙️ **[Configuração Automatizada](docs/09-configuracao-automatizada.md)** - Scripts de setup

### 📊 Relatórios de Testes e Validação

- 📋 **[Validação API Superset](docs/reports/VALIDACAO_SUPERSET_API.md)** - Testes das APIs REST
- 📄 **[Relatório Final de Testes](docs/reports/RELATORIO-FINAL-TESTES-API-SUPERSET.md)** - Resultados completos
- 📖 **[README Testes API](docs/reports/README-TESTES-API-SUPERSET.md)** - Guia de testes

## 📊 Exemplos Práticos

### 🎬 Pipeline ETL End-to-End

Exemplo completo de um pipeline de dados, do armazenamento à visualização:

#### **1️⃣ Criar Buckets no MinIO (Bronze/Silver/Gold)**

```python
import boto3

# Cliente S3 apontando para MinIO
s3 = boto3.client(
    's3',
    endpoint_url='http://localhost:9000',
    aws_access_key_id='minioadmin',
    aws_secret_access_key='minioadmin123'
)

# Criar camadas do Data Lake
for bucket in ['bronze', 'silver', 'gold']:
    s3.create_bucket(Bucket=bucket)
    print(f'✓ Bucket {bucket} criado')
```

#### **2️⃣ DAG do Airflow (Orquestração)**

```python
```python
# dags/etl_sales_pipeline.py
from airflow import DAG
from airflow.providers.apache.spark.operators.spark_submit import SparkSubmitOperator
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta

default_args = {
    'owner': 'data-team',
    'depends_on_past': False,
    'start_date': datetime(2025, 1, 1),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 2,
    'retry_delay': timedelta(minutes=5),
}

with DAG(
    'etl_sales_pipeline',
    default_args=default_args,
    description='Pipeline ETL de vendas',
    schedule_interval='@daily',
    catchup=False,
    tags=['etl', 'sales', 'production']
) as dag:
    
    # Task 1: Processar dados brutos (Bronze → Silver)
    process_raw_data = SparkSubmitOperator(
        task_id='process_raw_data',
        application='/opt/airflow/jobs/process_sales.py',
        conn_id='spark_default',
        conf={
            'spark.hadoop.fs.s3a.endpoint': 'http://minio:9000',
            'spark.hadoop.fs.s3a.access.key': 'minioadmin',
            'spark.hadoop.fs.s3a.secret.key': 'minioadmin123'
        }
    )
    
    # Task 2: Agregações e métricas (Silver → Gold)
    aggregate_data = SparkSubmitOperator(
        task_id='aggregate_data',
        application='/opt/airflow/jobs/aggregate_sales.py',
        conn_id='spark_default',
    )
    
    # Definir ordem de execução
    process_raw_data >> aggregate_data
```

#### **3️⃣ Job Spark - Processamento (PySpark)**

```python
```python
# jobs/process_sales.py
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, to_date, year, month, sum as _sum

# Inicializar Spark com configurações S3
spark = SparkSession.builder \
    .appName("Process Sales Data") \
    .config("spark.hadoop.fs.s3a.endpoint", "http://minio:9000") \
    .config("spark.hadoop.fs.s3a.access.key", "minioadmin") \
    .config("spark.hadoop.fs.s3a.secret.key", "minioadmin123") \
    .config("spark.hadoop.fs.s3a.path.style.access", "true") \
    .config("spark.hadoop.fs.s3a.impl", "org.apache.hadoop.fs.s3a.S3AFileSystem") \
    .getOrCreate()

# 1. Ler dados brutos (Bronze)
df_raw = spark.read \
    .option("header", "true") \
    .option("inferSchema", "true") \
    .csv("s3a://bronze/sales/raw_data/")

# 2. Transformações (Limpeza e Enriquecimento)
df_clean = df_raw \
    .filter(col("amount") > 0) \
    .withColumn("sale_date", to_date(col("date"), "yyyy-MM-dd")) \
    .withColumn("year", year(col("sale_date"))) \
    .withColumn("month", month(col("sale_date"))) \
    .dropDuplicates(["transaction_id"]) \
    .na.drop()

# 3. Salvar dados processados (Silver)
df_clean.write \
    .mode('overwrite') \
    .partitionBy("year", "month") \
    .parquet("s3a://silver/sales/processed/")

print(f"✓ Processados {df_clean.count()} registros")
spark.stop()
```

#### **4️⃣ Consulta SQL com Trino**

```sql
-- Conectar via Trino UI (localhost:8085) ou JDBC

-- Criar tabela externa apontando para dados no MinIO
CREATE TABLE IF NOT EXISTS hive.default.sales_processed (
    transaction_id VARCHAR,
    customer_id VARCHAR,
    product_id VARCHAR,
    amount DOUBLE,
    sale_date DATE,
    year INT,
    month INT
)
WITH (
    external_location = 's3a://silver/sales/processed/',
    format = 'PARQUET',
    partitioned_by = ARRAY['year', 'month']
);

-- Análise: Top 10 produtos mais vendidos
SELECT 
    product_id,
    COUNT(*) as total_sales,
    ROUND(SUM(amount), 2) as total_revenue
FROM hive.default.sales_processed
WHERE year = 2025 AND month = 10
GROUP BY product_id
ORDER BY total_revenue DESC
LIMIT 10;
```

#### **5️⃣ Dashboard no Superset**

1. Acesse http://localhost:8088
2. **Database** → **+ Database** → Configure conexão Trino:
   ```
   trino://trino@trino:8085/hive/default
   ```
3. **SQL Lab** → Execute queries ad-hoc
4. **Charts** → Crie visualizações
5. **Dashboards** → Monte painéis interativos

### 🔗 Mais Exemplos

Explore exemplos completos no diretório [`examples/`](examples/):

- 📝 **[DAGs](examples/dags/)** - Pipelines Airflow prontos
- ⚙️ **[Jobs Spark](examples/jobs/)** - Scripts PySpark
- 📊 **[Queries SQL](examples/queries/)** - Consultas Trino
- 🐍 **[Scripts Python](examples/access_examples.py)** - Acesso programático

## 🔌 Conectividade e APIs

## 🔌 Conectividade e APIs

### 🔗 JDBC (Trino)

Conecte ferramentas externas (DBeaver, Power BI, Tableau) via JDBC:

```
JDBC URL: jdbc:trino://localhost:8085/hive/default
Driver: io.trino.jdbc.TrinoDriver
Username: trino
Password: (vazio)
```

**Download do Driver**: [Trino JDBC](https://repo1.maven.org/maven2/io/trino/trino-jdbc/)

### 🌐 REST API (Trino)

```bash
# Executar query via REST
curl -X POST http://localhost:8085/v1/statement \
  -H "X-Trino-User: trino" \
  -H "X-Trino-Catalog: hive" \
  -H "X-Trino-Schema: default" \
  -d "SELECT * FROM sales_processed LIMIT 10"
```

### 🐍 Python (MinIO/S3)

```python
import boto3
from botocore.client import Config

# Cliente boto3 para MinIO
s3_client = boto3.client(
    's3',
    endpoint_url='http://localhost:9000',
    aws_access_key_id='minioadmin',
    aws_secret_access_key='minioadmin123',
    config=Config(signature_version='s3v4'),
    region_name='us-east-1'
)

# Listar buckets
response = s3_client.list_buckets()
for bucket in response['Buckets']:
    print(f"  - {bucket['Name']}")

# Upload de arquivo
s3_client.upload_file('local_file.csv', 'bronze', 'data/file.csv')
```

### 🐍 Python (Trino)

```python
from trino.dbapi import connect
from trino.auth import BasicAuthentication

# Conexão com Trino
conn = connect(
    host='localhost',
    port=8085,
    user='trino',
    catalog='hive',
    schema='default',
)

# Executar query
cursor = conn.cursor()
cursor.execute("SELECT COUNT(*) FROM sales_processed")
result = cursor.fetchone()
print(f"Total de registros: {result[0]}")
```

### � PySpark (Local)

```python
from pyspark.sql import SparkSession

spark = SparkSession.builder \
    .appName("Local Spark App") \
    .master("spark://localhost:7077") \
    .config("spark.hadoop.fs.s3a.endpoint", "http://localhost:9000") \
    .config("spark.hadoop.fs.s3a.access.key", "minioadmin") \
    .config("spark.hadoop.fs.s3a.secret.key", "minioadmin123") \
    .getOrCreate()

# Ler dados do MinIO
df = spark.read.parquet("s3a://silver/sales/processed/")
df.show(10)
```

## 📁 Estrutura do Projeto

## 📁 Estrutura do Projeto

```
mini-bigdata/
│
├── 📄 docker-compose.yml          # Orquestração de containers
├──  requirements.txt            # Dependências Python
├── 📖 README.md                   # Esta documentação
├── 📘 QUICKSTART.md              # Guia rápido de início
├── 💾 STORAGE.md                 # Detalhes sobre persistência
├── 🔧 TROUBLESHOOTING.md         # Solução de problemas
├── 📝 INSTALL.md                 # Guia de instalação detalhado
│
├── 📂 config/                     # Configurações dos serviços
│   ├── airflow/                  # Configs Airflow
│   ├── spark/                    # spark-defaults.conf
│   │   └── spark-defaults.conf
│   ├── trino/                    # Configs e catálogos Trino
│   │   ├── config.properties
│   │   └── catalog/
│   │       ├── hive.properties
│   │       └── memory.properties
│   ├── hive/                     # Hive Metastore configs
│   │   ├── Dockerfile
│   │   └── metastore-site.xml
│   ├── postgres/                 # Scripts de inicialização
│   │   └── init-databases.sh
│   └── superset/                 # Superset configs
│       ├── Dockerfile
│       ├── init-superset.sh
│       ├── requirements.txt
│       ├── superset_config.py    # Configuração com Redis results backend
│       └── README.md
│
├── 📂 data/                       # Volumes Docker (runtime)
│   ├── airflow/
│   ├── hive/
│   ├── minio/
│   ├── postgres/
│   ├── spark/
│   ├── superset/
│   └── trino/
│
├── 📂 docs/                       # Documentação completa
│   ├── 01-guia-inicio-rapido.md
│   ├── 02-criando-pipelines-airflow.md
│   ├── 03-processamento-spark.md
│   ├── 04-consultas-trino.md
│   ├── 05-criando-dashboards-superset.md
│   ├── 06-catalogo-hive-metastore.md
│   ├── 07-apis-rest-jdbc.md
│   ├── 08-casos-uso-praticos.md
│   ├── 09-configuracao-automatizada.md
│   ├── INDICE.md
│   ├── senhas.txt                # Credenciais padrão
│   ├── SUPERSET-v5-GUIA.md       # Guia Apache Superset v5
│   ├── SUPERSET-ARCHITECTURE.md  # Arquitetura do Superset
│   ├── SUPERSET-EXAMPLES.md      # Exemplos de uso
│   └── reports/                  # Relatórios de testes e validações
│       ├── RELATORIO-FINAL-TESTES-API-SUPERSET.md
│       ├── RELATORIO-TESTES-API-SUPERSET.md
│       ├── README-TESTES-API-SUPERSET.md
│       └── VALIDACAO_SUPERSET_API.md
│
├── 📂 examples/                   # Exemplos práticos
│   ├── access_examples.py        # Scripts de acesso
│   ├── automation/               # Automação de tarefas
│   │   └── exemplo_automacao_superset.py  # Classe SupersetAutomation
│   ├── dags/                     # DAGs Airflow exemplo
│   │   └── etl_sales_pipeline.py
│   ├── jobs/                     # Jobs Spark exemplo
│   │   ├── process_sales.py
│   │   └── aggregate_sales.py
│   ├── queries/                  # Queries SQL exemplo
│   │   └── trino_examples.sql
│   ├── notebooks/                # Jupyter notebooks
│   └── data/                     # Dados de exemplo
│
├── 📂 scripts/                    # Scripts de automação
│   ├── README.md                 # Documentação dos scripts
│   ├── setup_stack.py            # Setup completo da stack
│   ├── validate_stack.py         # Validação de serviços individuais
│   ├── validate_all_services.py  # ⭐ Validação unificada de todos os serviços
│   ├── configure_minio.py        # Configuração MinIO
│   ├── configure_superset.py     # Configuração Superset
│   ├── configure_trino.py        # Configuração Trino
│   ├── 02_criar_datasets_virtuais_completo.py  # Criação de datasets
│   └── shell/                    # Scripts shell
│       ├── setup.sh              # Setup inicial do ambiente
│       ├── check-storage.sh      # Verificação de storage
│       ├── validate-superset.sh  # Validação Superset
│       └── validate-superset-drivers.sh  # Validação drivers
│
├── 📂 tests/                      # Testes automatizados
│   └── superset/                 # Testes API Apache Superset
│       ├── test_superset_api_complete.py      # Suite completa de testes
│       ├── test_superset_crud_operations.py   # CRUD databases/datasets
│       ├── test_superset_sql_queries.py       # Execução SQL via API
│       ├── test_api_login_final.py
│       ├── test_csrf_cookies.py
│       ├── test_csrf_debug.py
│       ├── test_form_csrf.py
│       ├── test_session_csrf.py
│       ├── test_superset_api.py
│       ├── test_superset_complete.py
│       ├── test_superset_simple.py
│       └── test_web_login.py
│
└── 📂 sql/                        # Views SQL analíticas
    ├── 01_vw_consistencia_alocacao.sql
    ├── 02_vw_horario_trabalho.sql
    ├── 03_vw_produtividade_horaria.sql
    ├── 04_vw_sensibilidade_preco.sql
    ├── 05_vw_vpn_projetos.sql
    ├── 06_vw_competitividade_salarial.sql
    ├── 07_vw_kpis_executivo.sql
    ├── 08_vw_capacidade_detalhada.sql
    ├── 09_vw_performance_projetos.sql
    ├── 10_vw_custos_rentabilidade.sql
    ├── 11_vw_qualidade_bugs.sql
    ├── 12_vw_sazonalidade_utilizacao.sql
    ├── 13_vw_ponto_equilibrio.sql
    └── 14_vw_concentracao_hhi.sql
```

### 💾 Dados Persistidos (Disco Externo)

```
/media/marcelo/dados1/bigdata-docker/
├── postgres/      # 🗄️  Metadados (Airflow, Superset, Hive)
├── minio/         # 📦 Data Lake (arquivos principais)
├── airflow/       # 🔄 DAGs, logs, plugins
├── hive/          # 📚 Warehouse do Hive
├── spark/         # ⚡ Jobs, checkpoints, event logs
├── trino/         # 🔍 Cache de queries
└── superset/      # 📊 Dashboards e configurações
```

## 📂 Organização de Arquivos

### 🧪 Testes (`tests/`)

Todos os testes automatizados estão organizados em `tests/superset/`:
- **test_superset_api_complete.py**: Suite completa com 85.7% de sucesso (12/14 testes)
- **test_superset_crud_operations.py**: Testes CRUD de databases, datasets, charts e dashboards
- **test_superset_sql_queries.py**: Testes de execução SQL via API (100% sucesso)
- Outros testes de autenticação e CSRF

### 🔧 Scripts (`scripts/`)

Scripts de automação e configuração:

**Python**:
- **validate_all_services.py**: ⭐ Validação unificada de todos os 8 serviços da stack
- **validate_stack.py**: Validação individual de cada serviço
- **setup_stack.py**: Setup automatizado completo
- **configure_*.py**: Configuração de MinIO, Superset e Trino
- **02_criar_datasets_virtuais_completo.py**: Criação automática de datasets

**Shell** (`scripts/shell/`):
- **setup.sh**: Setup inicial do ambiente e estrutura de diretórios
- **validate-superset.sh**: Validação específica do Apache Superset
- **validate-superset-drivers.sh**: Verificação de drivers JDBC/Python
- **check-storage.sh**: Verificação de persistência e espaço em disco

### 📚 Exemplos (`examples/`)

Exemplos práticos e reutilizáveis:

**Automação** (`examples/automation/`):
- **exemplo_automacao_superset.py**: Classe `SupersetAutomation` com métodos para:
  - `create_database()`: Criar conexões de banco de dados
  - `create_virtual_dataset()`: Criar datasets virtuais (SQL)
  - `create_chart()`: Criar gráficos
  - `create_dashboard()`: Criar dashboards
  - `execute_sql()`: Executar queries SQL via API

**DAGs Airflow** (`examples/dags/`):
- Pipeline ETL end-to-end com Spark

**Jobs Spark** (`examples/jobs/`):
- Processamento PySpark (Bronze → Silver → Gold)

### 📖 Documentação (`docs/`)

Documentação completa:
- Guias de uso de cada componente (01-09)
- **SUPERSET-v5-GUIA.md**: Guia do Apache Superset v5
- **reports/**: Relatórios de testes e validações da API

### 🗄️ SQL (`sql/`)

Views analíticas prontas para uso:
- KPIs executivos, análise de custos, produtividade, etc.
- 14 views SQL para análises de negócio

## 🛠️ Comandos Úteis

## 🛠️ Comandos Úteis

### � Validação da Stack

```bash
# Validar todos os serviços da stack (recomendado)
source .venv/bin/activate
python3 scripts/validate_all_services.py

# Saída esperada:
# ================================
# VALIDAÇÃO COMPLETA DA STACK MINI-BIGDATA
# ================================
# 
# Serviços Validados: 8
# Serviços OK: 8
# Taxa de Sucesso: 100.0%
# 
# ✓ PostgreSQL - Databases: airflow, superset, metastore
# ✓ Redis - Cache operacional
# ✓ MinIO - Object storage operacional
# ✓ Hive Metastore - Catálogo de metadados
# ✓ Spark - Master e Workers operacionais
# ✓ Trino - Query engine operacional
# ✓ Airflow - Scheduler e Webserver ativos
# ✓ Superset - BI Platform com 2 databases configurados

# Validar serviços individuais
python3 scripts/validate_stack.py

# Validar apenas Superset
./scripts/shell/validate-superset.sh

# Validar drivers do Superset
./scripts/shell/validate-superset-drivers.sh

# Verificar storage
./scripts/shell/check-storage.sh
```

### 🧪 Executar Testes da API Superset

```bash
# Ativar ambiente virtual Python
source .venv/bin/activate

# Instalar dependências (primeira vez)
pip install -r requirements.txt

# Suite completa de testes
python3 tests/superset/test_superset_api_complete.py

# Testes de CRUD (Databases, Datasets, Charts, Dashboards)
python3 tests/superset/test_superset_crud_operations.py

# Testes de execução SQL via API
python3 tests/superset/test_superset_sql_queries.py

# Exemplo de automação (classe reutilizável)
python3 examples/automation/exemplo_automacao_superset.py
```

### �🚀 Gerenciamento do Ambiente

```bash
# Iniciar todos os serviços
docker-compose up -d

# Parar todos os serviços (mantém dados)
docker-compose down

# Parar e remover volumes Docker (⚠️ dados em /media/marcelo/dados1/ são mantidos)
docker-compose down -v

# Reiniciar ambiente completo
docker-compose restart

# Reiniciar serviço específico
docker-compose restart airflow-webserver
docker-compose restart spark-master
docker-compose restart trino

# Ver status dos containers
docker-compose ps

# Ver estatísticas de recursos
docker stats
```

### 📋 Logs e Debugging

```bash
# Ver logs de todos os serviços
docker-compose logs -f

# Ver logs de um serviço específico
docker-compose logs -f trino
docker-compose logs -f spark-master
docker-compose logs -f airflow-scheduler

# Ver últimas 100 linhas
docker-compose logs --tail=100 airflow-webserver

# Acessar shell do container
docker-compose exec airflow-webserver bash
docker-compose exec spark-master bash
docker-compose exec trino /bin/bash
```

### ⚙️ Escalabilidade

```bash
# Escalar workers do Airflow
docker-compose up -d --scale airflow-worker=3

# Escalar workers do Spark
docker-compose up -d --scale spark-worker=2

# Verificar workers ativos
docker-compose ps | grep worker
```

### 💾 Backup e Manutenção

```bash
# Backup completo dos dados
tar -czf backup-bigdata-$(date +%Y%m%d).tar.gz \
  /media/marcelo/dados1/bigdata-docker/

# Backup específico (apenas MinIO)
tar -czf backup-minio-$(date +%Y%m%d).tar.gz \
  /media/marcelo/dados1/bigdata-docker/minio/

# Verificar espaço em disco
du -sh /media/marcelo/dados1/bigdata-docker/*/

# Limpar logs antigos do Airflow
docker-compose exec airflow-scheduler \
  airflow db clean --clean-before-timestamp "$(date -d '30 days ago' '+%Y-%m-%d')" -y

# Limpar cache do Docker
docker system prune -a --volumes
```

### 🧹 Limpeza e Reset

```bash
# Reset completo (⚠️ CUIDADO: remove TODOS os dados)
docker-compose down -v
sudo rm -rf /media/marcelo/dados1/bigdata-docker/
./setup.sh
docker-compose up -d

# Rebuild de um serviço específico
docker-compose build --no-cache hive-metastore
docker-compose up -d hive-metastore
```

## 🔧 Customização e Configuração

## 🔧 Customização e Configuração

### 🔐 Alterar Credenciais Padrão

Edite as variáveis no arquivo `.env` ou diretamente no `docker-compose.yml`:

```bash
# MinIO
MINIO_ROOT_USER=seu_usuario
MINIO_ROOT_PASSWORD=SuaSenhaSegura123!

# PostgreSQL
POSTGRES_PASSWORD=postgres_senha_forte

# Airflow
AIRFLOW_WWW_USER_USERNAME=admin
AIRFLOW_WWW_USER_PASSWORD=admin_senha_forte
```

Após alterar, reinicie os serviços:

```bash
docker-compose down
docker-compose up -d
```

### 📊 Adicionar Catálogos no Trino

Crie novos arquivos em `config/trino/catalog/`:

**MySQL Catalog** (`config/trino/catalog/mysql.properties`):
```properties
connector.name=mysql
connection-url=jdbc:mysql://mysql-host:3306
connection-user=root
connection-password=senha
```

**PostgreSQL Catalog** (`config/trino/catalog/postgresql.properties`):
```properties
connector.name=postgresql
connection-url=jdbc:postgresql://postgres-host:5432/database
connection-user=postgres
connection-password=senha
```

**Iceberg Catalog** (`config/trino/catalog/iceberg.properties`):
```properties
connector.name=iceberg
hive.metastore.uri=thrift://hive-metastore:9083
iceberg.catalog.type=hive_metastore
```

Reinicie o Trino após adicionar catálogos:

```bash
docker-compose restart trino
```

### ⚡ Ajustar Recursos do Spark

Edite `config/spark/spark-defaults.conf`:

```properties
# Memória do driver
spark.driver.memory              2g

# Memória do executor
spark.executor.memory            4g
spark.executor.cores             2

# Número de executores
spark.executor.instances         2

# Configurações de shuffle
spark.sql.shuffle.partitions     200
```

### � Configurar Paralelismo do Airflow

Edite no `docker-compose.yml`:

```yaml
environment:
  AIRFLOW__CORE__PARALLELISM: 32
  AIRFLOW__CORE__DAG_CONCURRENCY: 16
  AIRFLOW__CORE__MAX_ACTIVE_RUNS_PER_DAG: 16
```

## 📊 Formatos de Dados Recomendados

### 🏗️ Arquitetura de Data Lake (Medallion)

| Camada | Formato | Compressão | Uso | Exemplo |
|--------|---------|------------|-----|---------|
| **🥉 Bronze** | JSON, CSV, Avro | gzip, snappy | Dados brutos | `s3a://bronze/raw/` |
| **🥈 Silver** | Parquet | snappy | Dados limpos | `s3a://silver/processed/` |
| **🥇 Gold** | Parquet, Delta, Iceberg | zstd | Analytics-ready | `s3a://gold/analytics/` |

### 💡 Recomendações

- **Bronze**: Mantenha formato original, adicione apenas metadados (ingest_date, source, etc)
- **Silver**: Converta para Parquet, aplique schema, particione por data
- **Gold**: Use Delta/Iceberg para ACID e time-travel, agregue dados por caso de uso

## 🔍 Monitoramento e Observabilidade

## 🔍 Monitoramento e Observabilidade

### 📊 UIs de Monitoramento

| Interface | URL | Descrição |
|-----------|-----|-----------|
| **Airflow** | http://localhost:8080 | Status DAGs, task logs, conexões |
| **Spark Master** | http://localhost:8081 | Jobs, stages, executors |
| **Trino** | http://localhost:8085 | Query monitoring, cluster status |
| **MinIO Console** | http://localhost:9001 | Storage metrics, buckets, bandwidth |
| **Superset** | http://localhost:8088 | Dashboard usage, query logs |

### 📈 Métricas Importantes

**Airflow**:
- DAG run duration
- Task success/failure rate
- Scheduler heartbeat

**Spark**:
- Job duration
- Stages e tasks completed
- Memory e CPU usage

**Trino**:
- Query execution time
- Data read/written
- Active queries

**MinIO**:
- Storage utilizado
- Bandwidth (upload/download)
- Request rate

### 🔔 Alertas (Opcional)

Para implementar alertas, considere adicionar:
- **Prometheus** + **Grafana** para métricas
- **Alertmanager** para notificações
- Configuração de email no Airflow para falhas de DAG

## 🐛 Troubleshooting

### ❌ Problemas Comuns

<details>
<summary><b>Serviços não sobem / Container em estado "unhealthy"</b></summary>

```bash
# Verificar logs do serviço específico
docker-compose logs trino
docker-compose logs airflow-webserver

# Verificar recursos disponíveis
docker stats

# Recriar containers
docker-compose down
docker-compose up -d --force-recreate
```
</details>

<details>
<summary><b>Airflow não conecta ao Spark</b></summary>

1. Verificar conexão no Airflow Admin → Connections
2. Conn Id: `spark_default`
3. Host: `spark://spark-master:7077`
4. Reiniciar scheduler: `docker-compose restart airflow-scheduler`
</details>

<details>
<summary><b>Trino não encontra tabelas</b></summary>

```bash
# Verificar se Hive Metastore está rodando
docker-compose ps hive-metastore

# Conectar ao Trino e verificar catálogos
docker-compose exec trino trino
> SHOW CATALOGS;
> SHOW SCHEMAS FROM hive;
> SHOW TABLES FROM hive.default;

# Verificar permissões no MinIO
# Acesse http://localhost:9001 e verifique buckets
```
</details>

<details>
<summary><b>Falta de espaço em disco</b></summary>

```bash
# Verificar uso de disco
df -h /media/marcelo/dados1/

# Ver tamanho por componente
du -sh /media/marcelo/dados1/bigdata-docker/*/

# Limpar logs antigos
docker-compose exec airflow-scheduler airflow db clean --clean-before-timestamp "$(date -d '30 days ago' '+%Y-%m-%d')" -y

# Limpar cache Docker
docker system prune -a
```
</details>

<details>
<summary><b>Porta já em uso</b></summary>

```bash
# Verificar processo usando porta
sudo lsof -i :8080
sudo lsof -i :9000

# Matar processo (exemplo)
sudo kill -9 <PID>

# Ou alterar portas no docker-compose.yml
ports:
  - "8081:8080"  # Muda porta externa
```
</details>

### 📚 Documentação de Troubleshooting

Para problemas mais complexos, consulte:
- **[TROUBLESHOOTING.md](TROUBLESHOOTING.md)** - Guia completo de solução de problemas
- **[STORAGE.md](STORAGE.md)** - Problemas relacionados a persistência
- **[SUPERSET-DRIVERS.md](SUPERSET-DRIVERS.md)** - Configuração de drivers do Superset
- Issues do projeto no GitHub

## 🚀 Roadmap e Melhorias Futuras

## 🚀 Roadmap e Melhorias Futuras

### 🎯 Próximas Implementações

- [ ] **Apache Iceberg / Delta Lake** - Table format para ACID transactions
- [ ] **Apache Kafka** - Streaming de dados em tempo real
- [ ] **Jupyter Lab** - Notebooks para análises interativas
- [ ] **dbt (Data Build Tool)** - Transformações SQL como código
- [ ] **Great Expectations** - Data quality e testes
- [ ] **Apache Atlas** - Data governance e lineage
- [ ] **Prometheus + Grafana** - Monitoring avançado
- [ ] **Apache Ranger** - Security e controle de acesso
- [ ] **MLflow** - Machine Learning lifecycle
- [ ] **Dagster** - Alternativa moderna ao Airflow

### � Ideias de Contribuição

Contribuições são bem-vindas! Veja como você pode ajudar:

1. 🐛 Reportar bugs via [Issues](https://github.com/marcelolimagomes/mini-bigdata/issues)
2. 📖 Melhorar documentação
3. ✨ Adicionar novos exemplos práticos
4. 🔧 Propor otimizações de configuração
5. 🎨 Criar dashboards de exemplo no Superset
6. 📊 Adicionar datasets de exemplo

## 📚 Recursos de Aprendizado

### 📖 Documentação Oficial

- [Apache Airflow Documentation](https://airflow.apache.org/docs/)
- [Apache Spark Documentation](https://spark.apache.org/docs/latest/)
- [Trino Documentation](https://trino.io/docs/current/)
- [MinIO Documentation](https://min.io/docs/minio/linux/index.html)
- [Apache Superset Documentation](https://superset.apache.org/docs/intro)
- [Hive Metastore](https://cwiki.apache.org/confluence/display/Hive/AdminManual+Metastore+Administration)

### 🎓 Tutoriais e Cursos

- [Fundamentals of Data Engineering (Joe Reis)](https://www.oreilly.com/library/view/fundamentals-of-data/9781098108298/)
- [Data Engineering Cookbook](https://github.com/andkret/Cookbook)
- [Awesome Data Engineering](https://github.com/igorbarinov/awesome-data-engineering)

### 🌐 Comunidades

- [Data Engineering Brasil](https://www.linkedin.com/groups/12345678/)
- [Stack Overflow - Tags: airflow, spark, trino](https://stackoverflow.com/)
- [Reddit r/dataengineering](https://www.reddit.com/r/dataengineering/)

## 🤝 Contribuindo

Contribuições são muito bem-vindas! Para contribuir:

1. Fork o projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add: nova feature incrível'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

### 📋 Guidelines

- Mantenha o código limpo e documentado
- Adicione exemplos práticos quando possível
- Atualize a documentação relevante
- Teste suas mudanças antes de submeter PR

## 📄 Licença

Este projeto está licenciado sob a **MIT License** - veja o arquivo [LICENSE](LICENSE) para detalhes.

Você é livre para:
- ✅ Usar comercialmente
- ✅ Modificar
- ✅ Distribuir
- ✅ Uso privado

## 👤 Autor

**Marcelo Lima Gomes**

- 🌐 GitHub: [@marcelolimagomes](https://github.com/marcelolimagomes)
- 📧 Email: marcelolimagomes@gmail.com
- 💼 LinkedIn: [Marcelo Lima Gomes](https://www.linkedin.com/in/marcelolimagomes/)

## ⭐ Agradecimentos

Este projeto foi inspirado por diversas fontes da comunidade open-source:

- Apache Software Foundation
- Trino Community
- MinIO Project
- Docker Community

## 🙏 Apoie o Projeto

Se este projeto foi útil para você:

- ⭐ Dê uma estrela no GitHub
- 🔀 Faça um fork
- 📢 Compartilhe com sua rede
- 💬 Dê feedback via Issues
- 🤝 Contribua com melhorias

## 📞 Suporte

- 🐛 **Bugs**: Abra uma [issue](https://github.com/marcelolimagomes/mini-bigdata/issues)
- 💬 **Dúvidas**: Use as [Discussions](https://github.com/marcelolimagomes/mini-bigdata/discussions)
- 📧 **Contato Direto**: marcelolimagomes@gmail.com

---

<div align="center">

**Desenvolvido com ❤️ para a comunidade de Big Data e DevOps**

[![GitHub](https://img.shields.io/badge/GitHub-marcelolimagomes-181717?style=for-the-badge&logo=github)](https://github.com/marcelolimagomes)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge)](https://opensource.org/licenses/MIT)

**[⬆ Voltar ao topo](#-mini-big-data-platform)**

</div>
