#!/usr/bin/env python3
"""
Testes de execução de queries SQL via API do Superset
Testa SQL Lab e execução de queries programaticamente
"""

import requests
import json
import time

# Configurações
SUPERSET_URL = "http://localhost:8088"
USERNAME = "admin"
PASSWORD = "admin"


class SupersetSQLTester:
    """Tester para execução de SQL via API"""

    def __init__(self, base_url: str, username: str, password: str):
        self.base_url = base_url
        self.username = username
        self.password = password
        self.session = requests.Session()
        self.access_token = None
        self.csrf_token = None

    def authenticate(self) -> bool:
        """Autenticação"""
        response = self.session.post(
            f"{self.base_url}/api/v1/security/login",
            json={
                "username": self.username,
                "password": self.password,
                "provider": "db",
                "refresh": True
            }
        )

        if response.status_code == 200:
            self.access_token = response.json().get("access_token")

            response = self.session.get(
                f"{self.base_url}/api/v1/security/csrf_token/",
                headers={"Authorization": f"Bearer {self.access_token}"}
            )

            if response.status_code == 200:
                self.csrf_token = response.json().get("result")
                return True

        return False

    def get_headers(self, with_csrf: bool = True) -> dict:
        """Headers para requisições"""
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }
        if with_csrf and self.csrf_token:
            headers["X-CSRFToken"] = self.csrf_token
            headers["Referer"] = self.base_url
        return headers

    def list_databases(self):
        """Lista databases disponíveis"""
        print("\n" + "=" * 80)
        print("  DATABASES DISPONÍVEIS")
        print("=" * 80 + "\n")

        response = self.session.get(
            f"{self.base_url}/api/v1/database/",
            headers=self.get_headers(with_csrf=False)
        )

        if response.status_code == 200:
            databases = response.json().get("result", [])
            print(f"Total de databases: {len(databases)}\n")

            for db in databases:
                print(f"ID: {db.get('id')}")
                print(f"Nome: {db.get('database_name')}")
                print(f"SQL Lab: {db.get('expose_in_sqllab')}")
                print(f"Backend: {db.get('backend', 'N/A')}")
                print("-" * 80)

            return databases
        else:
            print(f"❌ Erro ao listar databases: {response.status_code}")
            return []

    def execute_sql_query(self, database_id: int, sql: str, schema: str = None):
        """Executa uma query SQL"""
        print(f"\nExecutando SQL no database ID {database_id}:")
        print(f"SQL: {sql}")
        print("-" * 80)

        payload = {
            "database_id": database_id,
            "sql": sql,
            "runAsync": False,
            "schema": schema
        }

        response = self.session.post(
            f"{self.base_url}/api/v1/sqllab/execute/",
            json=payload,
            headers=self.get_headers()
        )

        print(f"Status: {response.status_code}")

        if response.status_code == 200:
            result = response.json()
            print("✓ Query executada com sucesso!")

            # Mostrar dados retornados
            if "data" in result:
                data = result["data"]
                print(f"Linhas retornadas: {len(data)}")

                if data:
                    # Mostrar colunas
                    if isinstance(data[0], dict):
                        print(f"Colunas: {', '.join(data[0].keys())}")

                    # Mostrar primeiras linhas
                    print("\nPrimeiras linhas:")
                    for i, row in enumerate(data[:5], 1):
                        print(f"  {i}. {row}")

            return True, result
        else:
            print(f"✗ Erro na execução")
            print(f"Response: {response.text}")
            return False, None

    def test_basic_queries(self, database_id: int):
        """Testa queries SQL básicas"""
        print("\n" + "=" * 80)
        print("  TESTE DE QUERIES SQL BÁSICAS")
        print("=" * 80)

        queries = [
            ("SELECT 1 as number", "Query simples - SELECT 1"),
            ("SELECT 1 as id, 'test' as name, NOW() as timestamp", "Query com múltiplas colunas"),
            ("SELECT generate_series(1, 5) as number", "Query com generate_series"),
            ("""
                SELECT 
                    'Database' as category,
                    current_database() as value
                UNION ALL
                SELECT 
                    'User' as category,
                    current_user as value
                UNION ALL
                SELECT 
                    'Time' as category,
                    NOW()::text as value
            """, "Query com UNION ALL"),
        ]

        results = []
        for sql, description in queries:
            print(f"\n{description}")
            print("-" * 80)
            success, result = self.execute_sql_query(database_id, sql)
            results.append((description, success))
            time.sleep(1)  # Pequeno delay entre queries

        # Resumo
        print("\n" + "=" * 80)
        print("  RESUMO DOS TESTES")
        print("=" * 80 + "\n")

        passed = sum(1 for _, success in results if success)
        total = len(results)

        print(f"Queries executadas: {passed}/{total}")

        for desc, success in results:
            status = "✓" if success else "✗"
            print(f"  {status} {desc}")

    def test_table_queries(self, database_id: int):
        """Testa queries em tabelas existentes"""
        print("\n" + "=" * 80)
        print("  TESTE DE QUERIES EM TABELAS")
        print("=" * 80)

        # Listar schemas
        print("\n1. Listando schemas disponíveis...")
        response = self.session.get(
            f"{self.base_url}/api/v1/database/{database_id}/schemas/",
            headers=self.get_headers(with_csrf=False)
        )

        if response.status_code == 200:
            schemas = response.json().get("result", [])
            print(f"   Schemas encontrados: {schemas}")

            # Testar em cada schema
            for schema in schemas[:3]:  # Limitar a 3 schemas
                print(f"\n2. Listando tabelas do schema '{schema}'...")

                response = self.session.get(
                    f"{self.base_url}/api/v1/database/{database_id}/tables/",
                    params={"schema_name": schema},
                    headers=self.get_headers(with_csrf=False)
                )

                if response.status_code == 200:
                    tables_data = response.json().get("result", [])
                    print(f"   Tabelas encontradas: {len(tables_data)}")

                    for table in tables_data[:3]:  # Limitar a 3 tabelas
                        table_name = table.get("value") if isinstance(table, dict) else table
                        print(f"\n   Testando query na tabela: {schema}.{table_name}")

                        sql = f"SELECT * FROM {schema}.{table_name} LIMIT 5"
                        self.execute_sql_query(database_id, sql, schema)
                        time.sleep(1)
        else:
            print(f"   ✗ Erro ao listar schemas: {response.status_code}")

    def test_chart_data_query(self):
        """Testa obtenção de dados de um chart via API"""
        print("\n" + "=" * 80)
        print("  TESTE DE QUERY VIA CHART DATA API")
        print("=" * 80)

        # Listar charts disponíveis
        response = self.session.get(
            f"{self.base_url}/api/v1/chart/",
            headers=self.get_headers(with_csrf=False)
        )

        if response.status_code == 200:
            charts = response.json().get("result", [])

            if charts:
                chart = charts[0]
                chart_id = chart.get("id")
                chart_name = chart.get("slice_name")

                print(f"\nTestando com chart: {chart_name} (ID: {chart_id})")

                # Obter dados do chart
                response = self.session.get(
                    f"{self.base_url}/api/v1/chart/{chart_id}/data/",
                    headers=self.get_headers(with_csrf=False)
                )

                if response.status_code == 200:
                    print("✓ Dados do chart obtidos com sucesso!")
                    data = response.json()
                    print(f"Resultado: {json.dumps(data, indent=2)[:500]}...")
                else:
                    print(f"✗ Erro ao obter dados: {response.status_code}")
            else:
                print("⚠ Nenhum chart disponível para testar")
        else:
            print(f"✗ Erro ao listar charts: {response.status_code}")

    def run_all_tests(self):
        """Executa todos os testes SQL"""
        print("\n" + "=" * 80)
        print("  TESTES DE EXECUÇÃO SQL - APACHE SUPERSET")
        print("=" * 80)

        if not self.authenticate():
            print("\n❌ Falha na autenticação")
            return

        print("\n✓ Autenticação bem-sucedida")

        # Listar databases
        databases = self.list_databases()

        if databases:
            # Usar o primeiro database disponível
            db = databases[0]
            db_id = db.get("id")

            # Testes básicos
            self.test_basic_queries(db_id)

            # Testes em tabelas
            if db.get("expose_in_sqllab"):
                self.test_table_queries(db_id)

        # Teste de chart data
        self.test_chart_data_query()

        print("\n" + "=" * 80)
        print("  TESTES SQL CONCLUÍDOS")
        print("=" * 80 + "\n")


def main():
    tester = SupersetSQLTester(SUPERSET_URL, USERNAME, PASSWORD)
    tester.run_all_tests()


if __name__ == "__main__":
    main()
