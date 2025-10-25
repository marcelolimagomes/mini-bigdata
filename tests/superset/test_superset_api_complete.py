#!/usr/bin/env python3
"""
Teste completo das APIs do Apache Superset
Valida autenticação, databases, datasets, charts e dashboards
"""

import requests
import json
import time
from typing import Dict, Optional, Tuple

# Configurações
SUPERSET_URL = "http://localhost:8088"
USERNAME = "admin"
PASSWORD = "admin"


class SupersetAPITester:
    """Classe para testar APIs do Superset"""

    def __init__(self, base_url: str, username: str, password: str):
        self.base_url = base_url
        self.username = username
        self.password = password
        self.session = requests.Session()
        self.access_token = None
        self.csrf_token = None

    def print_section(self, title: str):
        """Imprime seção formatada"""
        print(f"\n{'=' * 80}")
        print(f"  {title}")
        print(f"{'=' * 80}\n")

    def print_result(self, test_name: str, success: bool, message: str = ""):
        """Imprime resultado do teste"""
        status = "✓ PASSOU" if success else "✗ FALHOU"
        print(f"{status} - {test_name}")
        if message:
            print(f"  → {message}")

    def authenticate(self) -> bool:
        """Autenticação via API"""
        self.print_section("1. AUTENTICAÇÃO")

        try:
            # Login
            response = self.session.post(
                f"{self.base_url}/api/v1/security/login",
                json={
                    "username": self.username,
                    "password": self.password,
                    "provider": "db",
                    "refresh": True
                },
                headers={"Content-Type": "application/json"}
            )

            if response.status_code != 200:
                self.print_result("Login", False, f"Status: {response.status_code}")
                print(f"Response: {response.text}")
                return False

            data = response.json()
            self.access_token = data.get("access_token")

            if not self.access_token:
                self.print_result("Login", False, "Token não recebido")
                return False

            self.print_result("Login", True, f"Token: {self.access_token[:50]}...")

            # Obter CSRF Token
            response = self.session.get(
                f"{self.base_url}/api/v1/security/csrf_token/",
                headers={"Authorization": f"Bearer {self.access_token}"}
            )

            if response.status_code == 200:
                self.csrf_token = response.json().get("result")
                self.print_result("CSRF Token", True, f"Token: {self.csrf_token[:50]}...")
            else:
                self.print_result("CSRF Token", False, f"Status: {response.status_code}")

            return True

        except Exception as e:
            self.print_result("Autenticação", False, str(e))
            return False

    def get_headers(self, include_csrf: bool = True) -> Dict[str, str]:
        """Retorna headers para requisições"""
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }
        if include_csrf and self.csrf_token:
            headers["X-CSRFToken"] = self.csrf_token
            headers["Referer"] = self.base_url
        return headers

    def test_databases(self) -> Tuple[bool, Optional[int]]:
        """Testa operações com databases"""
        self.print_section("2. DATABASES")

        try:
            # Listar databases existentes
            response = self.session.get(
                f"{self.base_url}/api/v1/database/",
                headers=self.get_headers(include_csrf=False)
            )

            if response.status_code != 200:
                self.print_result("Listar Databases", False, f"Status: {response.status_code}")
                return False, None

            databases = response.json().get("result", [])
            self.print_result("Listar Databases", True, f"Total: {len(databases)}")

            for db in databases:
                print(f"  • {db.get('database_name')} (ID: {db.get('id')})")

            # Criar novo database de teste
            test_db_name = f"test_db_{int(time.time())}"
            db_config = {
                "database_name": test_db_name,
                "sqlalchemy_uri": "postgresql://admin:admin123@postgres:5432/superset",
                "expose_in_sqllab": True,
                "allow_run_async": True,
                "allow_ctas": True,
                "allow_cvas": True,
            }

            response = self.session.post(
                f"{self.base_url}/api/v1/database/",
                json=db_config,
                headers=self.get_headers()
            )

            if response.status_code == 201:
                db_id = response.json().get("id")
                self.print_result("Criar Database", True, f"ID: {db_id}, Nome: {test_db_name}")

                # Testar conexão
                response = self.session.post(
                    f"{self.base_url}/api/v1/database/test_connection",
                    json=db_config,
                    headers=self.get_headers()
                )

                if response.status_code == 200:
                    self.print_result("Testar Conexão", True, "Conexão OK")
                else:
                    self.print_result("Testar Conexão", False, f"Status: {response.status_code}")

                return True, db_id
            else:
                self.print_result("Criar Database", False, f"Status: {response.status_code}")
                print(f"Response: {response.text}")
                return False, None

        except Exception as e:
            self.print_result("Databases", False, str(e))
            return False, None

    def test_datasets(self, database_id: Optional[int] = None) -> Tuple[bool, Optional[int]]:
        """Testa operações com datasets"""
        self.print_section("3. DATASETS")

        try:
            # Listar datasets existentes
            response = self.session.get(
                f"{self.base_url}/api/v1/dataset/",
                headers=self.get_headers(include_csrf=False)
            )

            if response.status_code != 200:
                self.print_result("Listar Datasets", False, f"Status: {response.status_code}")
                return False, None

            datasets = response.json().get("result", [])
            self.print_result("Listar Datasets", True, f"Total: {len(datasets)}")

            for ds in datasets[:5]:  # Mostrar apenas os primeiros 5
                print(f"  • {ds.get('table_name')} (ID: {ds.get('id')})")

            # Se temos um database_id, tentar criar um dataset virtual
            if database_id:
                dataset_config = {
                    "database": database_id,
                    "schema": "public",
                    "table_name": f"test_dataset_{int(time.time())}",
                    "sql": "SELECT 1 as id, 'test' as name",
                    "is_managed_externally": False
                }

                response = self.session.post(
                    f"{self.base_url}/api/v1/dataset/",
                    json=dataset_config,
                    headers=self.get_headers()
                )

                if response.status_code == 201:
                    dataset_id = response.json().get("id")
                    self.print_result("Criar Dataset Virtual", True, f"ID: {dataset_id}")
                    return True, dataset_id
                else:
                    self.print_result("Criar Dataset Virtual", False, f"Status: {response.status_code}")
                    print(f"Response: {response.text}")

            return True, None

        except Exception as e:
            self.print_result("Datasets", False, str(e))
            return False, None

    def test_charts(self, dataset_id: Optional[int] = None) -> Tuple[bool, Optional[int]]:
        """Testa operações com charts"""
        self.print_section("4. CHARTS")

        try:
            # Listar charts existentes
            response = self.session.get(
                f"{self.base_url}/api/v1/chart/",
                headers=self.get_headers(include_csrf=False)
            )

            if response.status_code != 200:
                self.print_result("Listar Charts", False, f"Status: {response.status_code}")
                return False, None

            charts = response.json().get("result", [])
            self.print_result("Listar Charts", True, f"Total: {len(charts)}")

            for chart in charts[:5]:  # Mostrar apenas os primeiros 5
                print(f"  • {chart.get('slice_name')} (ID: {chart.get('id')})")

            # Se temos um dataset_id, tentar criar um chart
            if dataset_id:
                chart_config = {
                    "slice_name": f"Test Chart {int(time.time())}",
                    "datasource_id": dataset_id,
                    "datasource_type": "table",
                    "viz_type": "table",
                    "params": json.dumps({
                        "metrics": [],
                        "groupby": [],
                        "viz_type": "table"
                    })
                }

                response = self.session.post(
                    f"{self.base_url}/api/v1/chart/",
                    json=chart_config,
                    headers=self.get_headers()
                )

                if response.status_code == 201:
                    chart_id = response.json().get("id")
                    self.print_result("Criar Chart", True, f"ID: {chart_id}")
                    return True, chart_id
                else:
                    self.print_result("Criar Chart", False, f"Status: {response.status_code}")
                    print(f"Response: {response.text}")

            return True, None

        except Exception as e:
            self.print_result("Charts", False, str(e))
            return False, None

    def test_dashboards(self, chart_id: Optional[int] = None) -> bool:
        """Testa operações com dashboards"""
        self.print_section("5. DASHBOARDS")

        try:
            # Listar dashboards existentes
            response = self.session.get(
                f"{self.base_url}/api/v1/dashboard/",
                headers=self.get_headers(include_csrf=False)
            )

            if response.status_code != 200:
                self.print_result("Listar Dashboards", False, f"Status: {response.status_code}")
                return False

            dashboards = response.json().get("result", [])
            self.print_result("Listar Dashboards", True, f"Total: {len(dashboards)}")

            for dash in dashboards[:5]:  # Mostrar apenas os primeiros 5
                print(f"  • {dash.get('dashboard_title')} (ID: {dash.get('id')})")

            # Criar novo dashboard
            dashboard_config = {
                "dashboard_title": f"Test Dashboard {int(time.time())}",
                "slug": None,
                "owners": [],
                "position_json": json.dumps({}),
                "css": "",
                "json_metadata": json.dumps({
                    "color_scheme": "",
                    "refresh_frequency": 0
                }),
                "published": True
            }

            response = self.session.post(
                f"{self.base_url}/api/v1/dashboard/",
                json=dashboard_config,
                headers=self.get_headers()
            )

            if response.status_code == 201:
                dashboard_id = response.json().get("id")
                self.print_result("Criar Dashboard", True, f"ID: {dashboard_id}")
                return True
            else:
                self.print_result("Criar Dashboard", False, f"Status: {response.status_code}")
                print(f"Response: {response.text}")
                return False

        except Exception as e:
            self.print_result("Dashboards", False, str(e))
            return False

    def test_sqllab(self) -> bool:
        """Testa SQL Lab"""
        self.print_section("6. SQL LAB")

        try:
            # Listar databases disponíveis para SQL Lab
            response = self.session.get(
                f"{self.base_url}/api/v1/database/",
                params={"q": json.dumps({"filters": [{"col": "expose_in_sqllab", "opr": "eq", "value": True}]})},
                headers=self.get_headers(include_csrf=False)
            )

            if response.status_code != 200:
                self.print_result("Databases SQL Lab", False, f"Status: {response.status_code}")
                return False

            databases = response.json().get("result", [])
            self.print_result("Databases SQL Lab", True, f"Disponíveis: {len(databases)}")

            return True

        except Exception as e:
            self.print_result("SQL Lab", False, str(e))
            return False

    def test_permissions(self) -> bool:
        """Testa informações de permissões"""
        self.print_section("7. PERMISSÕES")

        try:
            # Obter informações do usuário atual
            response = self.session.get(
                f"{self.base_url}/api/v1/me/",
                headers=self.get_headers(include_csrf=False)
            )

            if response.status_code != 200:
                self.print_result("Informações do Usuário", False, f"Status: {response.status_code}")
                return False

            user_info = response.json().get("result", {})
            self.print_result("Informações do Usuário", True,
                              f"Username: {user_info.get('username')}")

            roles = user_info.get("roles", {})
            print(f"  • Roles: {', '.join([r.get('name', '') for r in roles.values()])}")

            return True

        except Exception as e:
            self.print_result("Permissões", False, str(e))
            return False

    def cleanup(self, db_id: Optional[int] = None, dataset_id: Optional[int] = None,
                chart_id: Optional[int] = None):
        """Limpa recursos criados durante os testes"""
        self.print_section("8. LIMPEZA")

        # Deletar chart
        if chart_id:
            try:
                response = self.session.delete(
                    f"{self.base_url}/api/v1/chart/{chart_id}",
                    headers=self.get_headers()
                )
                self.print_result(f"Deletar Chart {chart_id}",
                                  response.status_code == 200)
            except Exception as e:
                self.print_result(f"Deletar Chart {chart_id}", False, str(e))

        # Deletar dataset
        if dataset_id:
            try:
                response = self.session.delete(
                    f"{self.base_url}/api/v1/dataset/{dataset_id}",
                    headers=self.get_headers()
                )
                self.print_result(f"Deletar Dataset {dataset_id}",
                                  response.status_code == 200)
            except Exception as e:
                self.print_result(f"Deletar Dataset {dataset_id}", False, str(e))

        # Deletar database
        if db_id:
            try:
                response = self.session.delete(
                    f"{self.base_url}/api/v1/database/{db_id}",
                    headers=self.get_headers()
                )
                self.print_result(f"Deletar Database {db_id}",
                                  response.status_code == 200)
            except Exception as e:
                self.print_result(f"Deletar Database {db_id}", False, str(e))

    def run_all_tests(self, cleanup_resources: bool = True):
        """Executa todos os testes"""
        print("\n" + "=" * 80)
        print("  TESTE COMPLETO DAS APIs DO APACHE SUPERSET")
        print("=" * 80)

        # Autenticação
        if not self.authenticate():
            print("\n❌ Falha na autenticação. Abortando testes.")
            return

        # Databases
        db_success, db_id = self.test_databases()

        # Datasets
        dataset_success, dataset_id = self.test_datasets(db_id)

        # Charts
        chart_success, chart_id = self.test_charts(dataset_id)

        # Dashboards
        dashboard_success = self.test_dashboards(chart_id)

        # SQL Lab
        sqllab_success = self.test_sqllab()

        # Permissões
        permissions_success = self.test_permissions()

        # Limpeza
        if cleanup_resources:
            self.cleanup(db_id, dataset_id, chart_id)

        # Resumo
        self.print_section("RESUMO")
        tests = [
            ("Autenticação", True),
            ("Databases", db_success),
            ("Datasets", dataset_success),
            ("Charts", chart_success),
            ("Dashboards", dashboard_success),
            ("SQL Lab", sqllab_success),
            ("Permissões", permissions_success)
        ]

        passed = sum(1 for _, success in tests if success)
        total = len(tests)

        print(f"Testes Passados: {passed}/{total}")
        print(f"Taxa de Sucesso: {(passed / total) * 100:.1f}%\n")

        for test_name, success in tests:
            status = "✓" if success else "✗"
            print(f"  {status} {test_name}")

        print("\n" + "=" * 80 + "\n")


def main():
    """Função principal"""
    tester = SupersetAPITester(SUPERSET_URL, USERNAME, PASSWORD)
    tester.run_all_tests(cleanup_resources=True)


if __name__ == "__main__":
    main()
