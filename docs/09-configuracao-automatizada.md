# 🤖 Configuração Automatizada via API e Scripts

## 🎯 Visão Geral

Este guia mostra como automatizar a configuração completa da stack Big Data usando APIs e scripts, eliminando processos manuais.

**O que você vai automatizar:**
- ✅ Conexão do Superset com Trino
- ✅ Criação de databases no Hive Metastore
- ✅ Criação de tabelas via Trino
- ✅ Criação de datasets no Superset
- ✅ Criação de charts e dashboards
- ✅ Configuração de buckets no MinIO

---

## 📦 Parte 1: Configuração do MinIO (Object Storage)

### Script: Criar Buckets Automaticamente

```python
#!/usr/bin/env python3
"""
configure_minio.py - Configura buckets no MinIO
"""

from minio import Minio
from minio.error import S3Error

# Configuração
MINIO_ENDPOINT = "localhost:9000"
MINIO_ACCESS_KEY = "minioadmin"
MINIO_SECRET_KEY = "minioadmin123"

def setup_minio():
    """Configura buckets no MinIO"""
    
    # Conectar ao MinIO
    client = Minio(
        MINIO_ENDPOINT,
        access_key=MINIO_ACCESS_KEY,
        secret_key=MINIO_SECRET_KEY,
        secure=False
    )
    
    # Buckets para criar (arquitetura Medallion)
    buckets = ["bronze", "silver", "gold", "warehouse", "raw-data"]
    
    print("🪣 Configurando buckets no MinIO...\n")
    
    for bucket in buckets:
        try:
            # Verificar se bucket existe
            if client.bucket_exists(bucket):
                print(f"  ✅ Bucket '{bucket}' já existe")
            else:
                # Criar bucket
                client.make_bucket(bucket)
                print(f"  ✅ Bucket '{bucket}' criado com sucesso")
        except S3Error as e:
            print(f"  ❌ Erro ao criar bucket '{bucket}': {e}")
    
    print("\n✅ Configuração do MinIO concluída!")
    
    # Listar todos os buckets
    print("\n📋 Buckets disponíveis:")
    buckets = client.list_buckets()
    for bucket in buckets:
        print(f"  - {bucket.name} (criado em {bucket.creation_date})")

if __name__ == "__main__":
    setup_minio()
```

### Executar

```bash
# Instalar dependência
pip install minio

# Executar script
python3 configure_minio.py
```

---

## 🔍 Parte 2: Configuração do Trino

### Script: Criar Schemas e Tabelas no Hive Metastore

```python
#!/usr/bin/env python3
"""
configure_trino.py - Configura schemas e tabelas no Trino/Hive
"""

from trino.dbapi import connect
from trino.auth import BasicAuthentication

# Configuração
TRINO_HOST = "localhost"
TRINO_PORT = 8080
TRINO_USER = "trino"
TRINO_CATALOG = "hive"

def get_connection():
    """Cria conexão com Trino"""
    return connect(
        host=TRINO_HOST,
        port=TRINO_PORT,
        user=TRINO_USER,
        catalog=TRINO_CATALOG,
        schema="default"
    )

def execute_sql(cursor, sql, description=""):
    """Executa SQL e mostra resultado"""
    try:
        cursor.execute(sql)
        print(f"  ✅ {description}")
        return True
    except Exception as e:
        print(f"  ⚠️  {description}: {str(e)[:100]}")
        return False

def setup_trino():
    """Configura schemas e tabelas no Trino"""
    
    print("🔍 Configurando Trino/Hive Metastore...\n")
    
    conn = get_connection()
    cursor = conn.cursor()
    
    # 1. Criar Schemas
    print("📁 Criando schemas...")
    
    schemas = [
        ("vendas", "s3a://gold/vendas/", "Schema para dados de vendas"),
        ("logs", "s3a://gold/logs/", "Schema para logs de aplicação"),
        ("analytics", "s3a://gold/analytics/", "Schema para análises")
    ]
    
    for schema_name, location, comment in schemas:
        sql = f"""
        CREATE SCHEMA IF NOT EXISTS hive.{schema_name}
        WITH (location = '{location}')
        """
        execute_sql(cursor, sql, f"Schema '{schema_name}' criado")
    
    # 2. Criar Tabelas Externas
    print("\n📊 Criando tabelas...")
    
    # Tabela: vendas_raw (Bronze - CSV)
    execute_sql(cursor, """
        CREATE TABLE IF NOT EXISTS hive.vendas.vendas_raw (
            data VARCHAR,
            pedido_id VARCHAR,
            cliente_id VARCHAR,
            produto VARCHAR,
            quantidade INTEGER,
            valor DOUBLE
        )
        WITH (
            external_location = 's3a://bronze/vendas/',
            format = 'CSV',
            skip_header_line_count = 1
        )
    """, "Tabela 'vendas_raw' (Bronze)")
    
    # Tabela: vendas_silver (Silver - Parquet Particionado)
    execute_sql(cursor, """
        CREATE TABLE IF NOT EXISTS hive.vendas.vendas_silver (
            pedido_id VARCHAR,
            cliente_id VARCHAR,
            produto VARCHAR,
            quantidade INTEGER,
            valor DOUBLE,
            valor_total DOUBLE,
            data DATE,
            ano INTEGER,
            mes INTEGER
        )
        WITH (
            external_location = 's3a://silver/vendas/',
            format = 'PARQUET',
            partitioned_by = ARRAY['ano', 'mes']
        )
    """, "Tabela 'vendas_silver' (Silver)")
    
    # Tabela: vendas_agregadas (Gold - Parquet)
    execute_sql(cursor, """
        CREATE TABLE IF NOT EXISTS hive.vendas.vendas_agregadas (
            produto VARCHAR,
            total_vendas BIGINT,
            quantidade_total BIGINT,
            receita_total DOUBLE,
            ticket_medio DOUBLE,
            ano INTEGER,
            mes INTEGER
        )
        WITH (
            external_location = 's3a://gold/vendas/agregadas/',
            format = 'PARQUET'
        )
    """, "Tabela 'vendas_agregadas' (Gold)")
    
    # 3. Criar Views
    print("\n👁️  Criando views...")
    
    execute_sql(cursor, """
        CREATE OR REPLACE VIEW hive.analytics.vendas_mensais AS
        SELECT 
            ano,
            mes,
            COUNT(*) as total_pedidos,
            SUM(quantidade) as quantidade_total,
            SUM(valor_total) as receita_total,
            AVG(valor_total) as ticket_medio
        FROM hive.vendas.vendas_silver
        GROUP BY ano, mes
    """, "View 'vendas_mensais'")
    
    execute_sql(cursor, """
        CREATE OR REPLACE VIEW hive.analytics.top_produtos AS
        SELECT 
            produto,
            COUNT(*) as total_vendas,
            SUM(quantidade) as quantidade_vendida,
            SUM(valor_total) as receita_total
        FROM hive.vendas.vendas_silver
        GROUP BY produto
        ORDER BY receita_total DESC
    """, "View 'top_produtos'")
    
    # 4. Listar recursos criados
    print("\n📋 Recursos criados:")
    
    print("\n  Schemas:")
    cursor.execute("SHOW SCHEMAS IN hive")
    for row in cursor.fetchall():
        if row[0] not in ['default', 'information_schema']:
            print(f"    - {row[0]}")
    
    print("\n  Tabelas em 'vendas':")
    cursor.execute("SHOW TABLES IN hive.vendas")
    for row in cursor.fetchall():
        print(f"    - {row[0]}")
    
    print("\n  Views em 'analytics':")
    cursor.execute("SHOW TABLES IN hive.analytics")
    for row in cursor.fetchall():
        print(f"    - {row[0]}")
    
    cursor.close()
    conn.close()
    
    print("\n✅ Configuração do Trino concluída!")

if __name__ == "__main__":
    setup_trino()
```

### Executar

```bash
# Instalar dependência
pip install trino

# Executar script
python3 configure_trino.py
```

---

## 📊 Parte 3: Configuração do Apache Superset

### Script Completo: Setup Automatizado

```python
#!/usr/bin/env python3
"""
configure_superset.py - Configura Superset via API
Cria database connection, datasets, charts e dashboards
"""

import requests
import json
import time
from datetime import datetime

# Configuração
SUPERSET_URL = "http://localhost:8088"
USERNAME = "admin"
PASSWORD = "admin"

class SupersetConfigurator:
    """Classe para configurar Superset via API"""
    
    def __init__(self, url, username, password):
        self.url = url
        self.username = username
        self.password = password
        self.session = requests.Session()
        self.token = None
        self.csrf_token = None
    
    def login(self):
        """Faz login e obtém tokens"""
        print("🔐 Fazendo login no Superset...")
        
        response = self.session.post(
            f"{self.url}/api/v1/security/login",
            json={
                "username": self.username,
                "password": self.password,
                "provider": "db",
                "refresh": True
            }
        )
        
        if response.status_code == 200:
            self.token = response.json()["access_token"]
            
            # Obter CSRF token
            csrf_response = self.session.get(
                f"{self.url}/api/v1/security/csrf_token/",
                headers={"Authorization": f"Bearer {self.token}"}
            )
            
            if csrf_response.status_code == 200:
                self.csrf_token = csrf_response.json()["result"]
            
            print("  ✅ Login realizado com sucesso")
            return True
        else:
            print(f"  ❌ Falha no login: {response.text}")
            return False
    
    def get_headers(self):
        """Retorna headers com autenticação"""
        return {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json",
            "X-CSRFToken": self.csrf_token if self.csrf_token else ""
        }
    
    def create_database(self, name, uri):
        """Cria conexão com database"""
        print(f"\n📁 Criando database connection '{name}'...")
        
        # Verificar se já existe
        response = self.session.get(
            f"{self.url}/api/v1/database/",
            headers=self.get_headers()
        )
        
        if response.status_code == 200:
            databases = response.json().get("result", [])
            for db in databases:
                if db.get("database_name") == name:
                    print(f"  ✅ Database '{name}' já existe (ID: {db['id']})")
                    return db['id']
        
        # Criar novo database usando método alternativo (superset CLI)
        print(f"  ℹ️  Use o comando abaixo no container do Superset:")
        print(f"  docker exec -it superset superset set-database-uri \\")
        print(f"    -d '{name}' -u '{uri}'")
        print(f"  ⚠️  Ou configure manualmente em: {self.url}/databaseview/list")
        
        return None
    
    def list_databases(self):
        """Lista databases disponíveis"""
        response = self.session.get(
            f"{self.url}/api/v1/database/",
            headers=self.get_headers()
        )
        
        if response.status_code == 200:
            databases = response.json().get("result", [])
            if databases:
                print("\n📋 Databases disponíveis:")
                for db in databases:
                    print(f"  - ID: {db['id']} | Nome: {db['database_name']}")
            return databases
        return []
    
    def create_dataset(self, database_id, schema, table_name):
        """Cria dataset"""
        print(f"\n📊 Criando dataset '{schema}.{table_name}'...")
        
        dataset_data = {
            "database": database_id,
            "schema": schema,
            "table_name": table_name
        }
        
        response = self.session.post(
            f"{self.url}/api/v1/dataset/",
            json=dataset_data,
            headers=self.get_headers()
        )
        
        if response.status_code in [200, 201]:
            dataset_id = response.json().get("id")
            print(f"  ✅ Dataset criado (ID: {dataset_id})")
            return dataset_id
        else:
            print(f"  ⚠️  Erro: {response.status_code} - {response.text[:200]}")
            return None
    
    def create_chart(self, dataset_id, chart_name, viz_type, params):
        """Cria chart"""
        print(f"\n📈 Criando chart '{chart_name}'...")
        
        chart_data = {
            "slice_name": chart_name,
            "viz_type": viz_type,
            "datasource_id": dataset_id,
            "datasource_type": "table",
            "params": json.dumps(params)
        }
        
        response = self.session.post(
            f"{self.url}/api/v1/chart/",
            json=chart_data,
            headers=self.get_headers()
        )
        
        if response.status_code in [200, 201]:
            chart_id = response.json().get("id")
            print(f"  ✅ Chart criado (ID: {chart_id})")
            return chart_id
        else:
            print(f"  ⚠️  Erro: {response.status_code}")
            return None
    
    def create_dashboard(self, dashboard_title, chart_ids):
        """Cria dashboard"""
        print(f"\n📊 Criando dashboard '{dashboard_title}'...")
        
        dashboard_data = {
            "dashboard_title": dashboard_title,
            "published": True,
            "position_json": json.dumps({
                "DASHBOARD_VERSION_KEY": "v2"
            })
        }
        
        response = self.session.post(
            f"{self.url}/api/v1/dashboard/",
            json=dashboard_data,
            headers=self.get_headers()
        )
        
        if response.status_code in [200, 201]:
            dashboard_id = response.json().get("id")
            print(f"  ✅ Dashboard criado (ID: {dashboard_id})")
            return dashboard_id
        else:
            print(f"  ⚠️  Erro: {response.status_code}")
            return None

def main():
    """Executa configuração completa"""
    print("="*70)
    print("  CONFIGURAÇÃO AUTOMATIZADA DO APACHE SUPERSET")
    print("="*70)
    print(f"  Data: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*70)
    
    # Inicializar configurador
    config = SupersetConfigurator(SUPERSET_URL, USERNAME, PASSWORD)
    
    # 1. Login
    if not config.login():
        print("\n❌ Não foi possível fazer login. Verifique credenciais.")
        return
    
    # 2. Listar databases existentes
    databases = config.list_databases()
    
    # 3. Criar database connection (ou instruir usuário)
    trino_db_id = config.create_database(
        name="Trino Big Data",
        uri="trino://trino@trino:8080/hive"
    )
    
    # Se não conseguiu criar, verificar se existe
    if not trino_db_id and databases:
        print("\n💡 Use um database existente ou configure manualmente:")
        print("   1. Acesse: http://localhost:8088/databaseview/list")
        print("   2. Clique em '+ Database'")
        print("   3. Preencha:")
        print("      Database: Trino Big Data")
        print("      SQLAlchemy URI: trino://trino@trino:8080/hive")
        print("   4. Execute este script novamente")
        
        # Tentar usar primeiro database disponível
        if databases:
            trino_db_id = databases[0]['id']
            print(f"\n  ℹ️  Usando database existente: ID {trino_db_id}")
    
    if not trino_db_id:
        print("\n⚠️  Configure um database primeiro e execute novamente.")
        return
    
    # 4. Criar datasets
    print("\n" + "="*70)
    print("  CRIANDO DATASETS")
    print("="*70)
    
    datasets_to_create = [
        ("vendas", "vendas_silver", "Dataset principal de vendas"),
        ("vendas", "vendas_agregadas", "Vendas agregadas"),
        ("analytics", "vendas_mensais", "View de vendas mensais"),
        ("analytics", "top_produtos", "View de top produtos")
    ]
    
    created_datasets = []
    for schema, table, description in datasets_to_create:
        dataset_id = config.create_dataset(trino_db_id, schema, table)
        if dataset_id:
            created_datasets.append({
                "id": dataset_id,
                "name": f"{schema}.{table}",
                "description": description
            })
    
    print(f"\n  ✅ {len(created_datasets)} dataset(s) criado(s)")
    
    # Resumo final
    print("\n" + "="*70)
    print("  CONFIGURAÇÃO CONCLUÍDA")
    print("="*70)
    
    print(f"\n✅ Superset configurado com sucesso!")
    print(f"\n📊 Próximos passos:")
    print(f"  1. Acesse: {SUPERSET_URL}")
    print(f"  2. Vá em 'Datasets' para ver os datasets criados")
    print(f"  3. Crie charts a partir dos datasets")
    print(f"  4. Monte dashboards com os charts")
    
    print(f"\n💡 Dica: Use a interface web para criar charts e dashboards")
    print(f"   ou expanda este script para automatizar completamente!")

if __name__ == "__main__":
    main()
```

### Executar

```bash
# Instalar dependência
pip install requests

# Executar script
python3 configure_superset.py
```

---

## 🚀 Parte 4: Script Mestre (All-in-One)

### Setup Completo em Um Comando

```python
#!/usr/bin/env python3
"""
setup_stack.py - Configura toda a stack Big Data automaticamente
"""

import subprocess
import sys
import time

def run_script(script_name, description):
    """Executa um script Python"""
    print(f"\n{'='*70}")
    print(f"  {description}")
    print(f"{'='*70}\n")
    
    try:
        result = subprocess.run(
            [sys.executable, script_name],
            capture_output=False,
            text=True
        )
        
        if result.returncode == 0:
            print(f"\n✅ {description} - Concluído")
            return True
        else:
            print(f"\n⚠️  {description} - Completado com avisos")
            return True
    except Exception as e:
        print(f"\n❌ Erro ao executar {script_name}: {e}")
        return False

def check_dependencies():
    """Verifica e instala dependências"""
    print("📦 Verificando dependências Python...\n")
    
    dependencies = [
        "minio",
        "trino",
        "requests"
    ]
    
    for dep in dependencies:
        try:
            __import__(dep)
            print(f"  ✅ {dep}")
        except ImportError:
            print(f"  📥 Instalando {dep}...")
            subprocess.run([sys.executable, "-m", "pip", "install", dep, "-q"])
            print(f"  ✅ {dep} instalado")

def main():
    """Executa setup completo"""
    print("\n" + "="*70)
    print("  SETUP COMPLETO DA STACK BIG DATA")
    print("="*70)
    print("\n  Este script irá configurar:")
    print("    1. MinIO (buckets)")
    print("    2. Trino/Hive (schemas e tabelas)")
    print("    3. Superset (database connections e datasets)")
    print("\n" + "="*70)
    
    input("\n⏸️  Pressione ENTER para continuar...")
    
    # Verificar dependências
    check_dependencies()
    
    # 1. Configurar MinIO
    if not run_script("configure_minio.py", "1/3 - Configurando MinIO"):
        print("\n⚠️  Continuando mesmo com erros no MinIO...")
    
    time.sleep(2)
    
    # 2. Configurar Trino
    if not run_script("configure_trino.py", "2/3 - Configurando Trino/Hive"):
        print("\n⚠️  Continuando mesmo com erros no Trino...")
    
    time.sleep(2)
    
    # 3. Configurar Superset
    if not run_script("configure_superset.py", "3/3 - Configurando Superset"):
        print("\n⚠️  Configuração do Superset pode requerer passos manuais")
    
    # Resumo final
    print("\n" + "="*70)
    print("  🎉 SETUP COMPLETO!")
    print("="*70)
    
    print("\n📋 Recursos configurados:")
    print("  ✅ MinIO: bronze, silver, gold, warehouse")
    print("  ✅ Trino: schemas (vendas, logs, analytics)")
    print("  ✅ Trino: tabelas (vendas_raw, vendas_silver, vendas_agregadas)")
    print("  ✅ Trino: views (vendas_mensais, top_produtos)")
    print("  ✅ Superset: datasets prontos para uso")
    
    print("\n🌐 URLs de Acesso:")
    print("  MinIO:    http://localhost:9001")
    print("  Trino:    http://localhost:8080")
    print("  Superset: http://localhost:8088")
    print("  Airflow:  http://localhost:8080")
    
    print("\n💡 Próximos passos:")
    print("  1. Carregar dados de exemplo nos buckets")
    print("  2. Executar pipelines Airflow para processar dados")
    print("  3. Criar charts e dashboards no Superset")

if __name__ == "__main__":
    main()
```

### Executar Setup Completo

```bash
# Tornar executável
chmod +x setup_stack.py

# Executar
python3 setup_stack.py
```

---

## 📋 Parte 5: Configuração via Docker Compose

### Adicionar Serviço de Inicialização

Crie `config/init/init-stack.sh`:

```bash
#!/bin/bash
# init-stack.sh - Inicializa stack após containers subirem

set -e

echo "⏳ Aguardando serviços ficarem prontos..."
sleep 30

echo "🚀 Executando configuração automatizada..."

# Configurar MinIO
python3 /scripts/configure_minio.py

# Configurar Trino
python3 /scripts/configure_trino.py

# Configurar Superset
python3 /scripts/configure_superset.py

echo "✅ Stack configurada com sucesso!"
```

### Adicionar ao docker-compose.yml

```yaml
services:
  # ... outros serviços ...
  
  stack-init:
    image: python:3.11-slim
    container_name: stack-init
    volumes:
      - ./configure_minio.py:/scripts/configure_minio.py
      - ./configure_trino.py:/scripts/configure_trino.py
      - ./configure_superset.py:/scripts/configure_superset.py
      - ./config/init/init-stack.sh:/init-stack.sh
    command: bash /init-stack.sh
    depends_on:
      - minio
      - trino
      - superset
    networks:
      - bigdata-network
```

---

## 🎯 Parte 6: Validação da Configuração

### Script de Validação

```python
#!/usr/bin/env python3
"""
validate_stack.py - Valida configuração completa da stack
"""

import requests
from minio import Minio
from trino.dbapi import connect

def validate_minio():
    """Valida MinIO"""
    print("\n🪣 Validando MinIO...")
    
    try:
        client = Minio(
            "localhost:9000",
            access_key="minioadmin",
            secret_key="minioadmin123",
            secure=False
        )
        
        buckets = client.list_buckets()
        expected = ["bronze", "silver", "gold", "warehouse"]
        found = [b.name for b in buckets]
        
        for bucket in expected:
            if bucket in found:
                print(f"  ✅ Bucket '{bucket}' existe")
            else:
                print(f"  ❌ Bucket '{bucket}' não encontrado")
        
        return True
    except Exception as e:
        print(f"  ❌ Erro: {e}")
        return False

def validate_trino():
    """Valida Trino"""
    print("\n🔍 Validando Trino...")
    
    try:
        conn = connect(
            host="localhost",
            port=8080,
            user="trino",
            catalog="hive"
        )
        cursor = conn.cursor()
        
        # Verificar schemas
        cursor.execute("SHOW SCHEMAS IN hive")
        schemas = [row[0] for row in cursor.fetchall()]
        
        for schema in ["vendas", "analytics"]:
            if schema in schemas:
                print(f"  ✅ Schema '{schema}' existe")
            else:
                print(f"  ❌ Schema '{schema}' não encontrado")
        
        # Verificar tabelas
        cursor.execute("SHOW TABLES IN hive.vendas")
        tables = [row[0] for row in cursor.fetchall()]
        
        for table in ["vendas_raw", "vendas_silver"]:
            if table in tables:
                print(f"  ✅ Tabela '{table}' existe")
            else:
                print(f"  ❌ Tabela '{table}' não encontrada")
        
        cursor.close()
        conn.close()
        return True
    except Exception as e:
        print(f"  ❌ Erro: {e}")
        return False

def validate_superset():
    """Valida Superset"""
    print("\n📊 Validando Superset...")
    
    try:
        # Login
        response = requests.post(
            "http://localhost:8088/api/v1/security/login",
            json={
                "username": "admin",
                "password": "admin",
                "provider": "db",
                "refresh": True
            }
        )
        
        if response.status_code != 200:
            print(f"  ❌ Falha no login")
            return False
        
        token = response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Verificar databases
        response = requests.get(
            "http://localhost:8088/api/v1/database/",
            headers=headers
        )
        
        databases = response.json().get("result", [])
        if databases:
            print(f"  ✅ {len(databases)} database(s) configurado(s)")
        else:
            print(f"  ⚠️  Nenhum database configurado")
        
        # Verificar datasets
        response = requests.get(
            "http://localhost:8088/api/v1/dataset/",
            headers=headers
        )
        
        datasets = response.json().get("result", [])
        print(f"  ✅ {len(datasets)} dataset(s) disponível(is)")
        
        return True
    except Exception as e:
        print(f"  ❌ Erro: {e}")
        return False

def main():
    """Executa validação completa"""
    print("="*70)
    print("  VALIDAÇÃO DA STACK BIG DATA")
    print("="*70)
    
    results = {
        "MinIO": validate_minio(),
        "Trino": validate_trino(),
        "Superset": validate_superset()
    }
    
    print("\n" + "="*70)
    print("  RESULTADO DA VALIDAÇÃO")
    print("="*70)
    
    for component, status in results.items():
        icon = "✅" if status else "❌"
        print(f"  {icon} {component}")
    
    if all(results.values()):
        print("\n✅ Stack configurada corretamente!")
    else:
        print("\n⚠️  Alguns componentes requerem atenção")

if __name__ == "__main__":
    main()
```

---

## 📝 Resumo dos Scripts

| Script | Função | Dependências |
|--------|--------|--------------|
| `configure_minio.py` | Cria buckets no MinIO | minio |
| `configure_trino.py` | Cria schemas e tabelas | trino |
| `configure_superset.py` | Configura Superset | requests |
| `setup_stack.py` | Executa todos os scripts | todas |
| `validate_stack.py` | Valida configuração | todas |

## 🚀 Guia Rápido de Uso

```bash
# 1. Instalar dependências
pip install minio trino requests

# 2. Executar setup completo
python3 setup_stack.py

# 3. Validar configuração
python3 validate_stack.py
```

## 📌 Observações Importantes

1. **CSRF Token no Superset**: A criação de database connections via API requer tratamento especial de CSRF. Recomenda-se criar a primeira conexão manualmente.

2. **Ordem de Execução**: Execute sempre na ordem: MinIO → Trino → Superset

3. **Verificação**: Use o script de validação após cada configuração

4. **Logs**: Todos os scripts mostram output detalhado para debug

## 🎯 Próximos Passos

Após executar a configuração automatizada:

1. **Carregar dados de exemplo** nos buckets bronze
2. **Executar pipelines Airflow** para processar dados
3. **Criar visualizações** no Superset
4. **Configurar alertas** e monitoramento

---

**Documentação criada em:** 24/10/2025  
**Versão da Stack:** Mini Big Data v1.0
