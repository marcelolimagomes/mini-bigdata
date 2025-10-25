#!/usr/bin/env python3
"""
configure_superset.py - Configura Superset via API
"""

import requests
import json
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
            print("  ✅ Login realizado com sucesso")
            return True
        else:
            print(f"  ❌ Falha no login: {response.text}")
            return False

    def get_headers(self):
        """Retorna headers com autenticação"""
        return {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }

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


def main():
    """Executa configuração completa"""
    print("=" * 70)
    print("  CONFIGURAÇÃO AUTOMATIZADA DO APACHE SUPERSET")
    print("=" * 70)
    print(f"  Data: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)

    # Inicializar configurador
    config = SupersetConfigurator(SUPERSET_URL, USERNAME, PASSWORD)

    # 1. Login
    if not config.login():
        print("\n❌ Não foi possível fazer login. Verifique credenciais.")
        return

    # 2. Listar databases existentes
    databases = config.list_databases()

    if not databases:
        print("\n⚠️  ATENÇÃO: Nenhum database configurado!")
        print("\n💡 Configure uma conexão com Trino primeiro:")
        print("   1. Acesse: http://localhost:8088/databaseview/list")
        print("   2. Clique em '+ Database'")
        print("   3. Selecione 'Trino'")
        print("   4. Preencha:")
        print("      Display Name: Trino Big Data")
        print("      SQLAlchemy URI: trino://trino@trino:8080/hive")
        print("   5. Clique em 'Test Connection' → 'Connect'")
        print("   6. Execute este script novamente")
        return

    # Usar primeiro database disponível
    trino_db_id = databases[0]['id']
    print(f"\n  ℹ️  Usando database: ID {trino_db_id}")

    # 3. Criar datasets
    print("\n" + "=" * 70)
    print("  CRIANDO DATASETS")
    print("=" * 70)

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
    print("\n" + "=" * 70)
    print("  CONFIGURAÇÃO CONCLUÍDA")
    print("=" * 70)

    if created_datasets:
        print(f"\n✅ Superset configurado com sucesso!")
        print(f"\n📊 Próximos passos:")
        print(f"  1. Acesse: {SUPERSET_URL}")
        print(f"  2. Vá em 'Datasets' para ver os datasets criados")
        print(f"  3. Crie charts a partir dos datasets")
        print(f"  4. Monte dashboards com os charts")
    else:
        print(f"\n⚠️  Nenhum dataset foi criado.")
        print(f"\n💡 Verifique se as tabelas existem no Trino:")
        print(f"   docker exec -it trino trino --catalog hive --schema vendas")
        print(f"   SHOW TABLES;")


if __name__ == "__main__":
    main()
