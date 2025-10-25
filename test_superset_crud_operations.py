#!/usr/bin/env python3
"""
Testes CRUD específicos para Apache Superset
Foca em operações Create, Read, Update, Delete para cada recurso
"""

import requests
import json
import time
from typing import Dict, Optional

# Configurações
SUPERSET_URL = "http://localhost:8088"
USERNAME = "admin"
PASSWORD = "admin"


class SupersetCRUDTester:
    """Tester para operações CRUD no Superset"""

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

            # CSRF Token
            response = self.session.get(
                f"{self.base_url}/api/v1/security/csrf_token/",
                headers={"Authorization": f"Bearer {self.access_token}"}
            )

            if response.status_code == 200:
                self.csrf_token = response.json().get("result")
                return True

        return False

    def get_headers(self, with_csrf: bool = True) -> Dict[str, str]:
        """Headers para requisições"""
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }
        if with_csrf and self.csrf_token:
            headers["X-CSRFToken"] = self.csrf_token
            headers["Referer"] = self.base_url
        return headers

    def test_database_crud(self):
        """Testa CRUD completo de Database"""
        print("\n" + "=" * 80)
        print("  TESTE CRUD - DATABASE")
        print("=" * 80 + "\n")

        db_name = f"crud_test_db_{int(time.time())}"
        db_id = None

        try:
            # CREATE
            print("1. CREATE - Criando database...")
            create_payload = {
                "database_name": db_name,
                "sqlalchemy_uri": "postgresql://admin:admin123@postgres:5432/superset",
                "expose_in_sqllab": True,
                "allow_run_async": True,
                "allow_ctas": True,
                "allow_cvas": True,
                "allow_file_upload": True,
                "extra": json.dumps({
                    "metadata_params": {},
                    "engine_params": {},
                    "metadata_cache_timeout": {},
                    "schemas_allowed_for_file_upload": []
                })
            }

            response = self.session.post(
                f"{self.base_url}/api/v1/database/",
                json=create_payload,
                headers=self.get_headers()
            )

            if response.status_code == 201:
                db_id = response.json().get("id")
                print(f"   ✓ Database criado com ID: {db_id}")
            else:
                print(f"   ✗ Falha ao criar: {response.status_code}")
                print(f"   Response: {response.text}")
                return

            # READ
            print("\n2. READ - Lendo database criado...")
            response = self.session.get(
                f"{self.base_url}/api/v1/database/{db_id}",
                headers=self.get_headers(with_csrf=False)
            )

            if response.status_code == 200:
                db_data = response.json().get("result", {})
                print(f"   ✓ Database encontrado: {db_data.get('database_name')}")
                print(f"   - URI: {db_data.get('sqlalchemy_uri_placeholder', 'N/A')}")
                print(f"   - SQL Lab: {db_data.get('expose_in_sqllab')}")
            else:
                print(f"   ✗ Falha ao ler: {response.status_code}")

            # UPDATE
            print("\n3. UPDATE - Atualizando database...")
            update_payload = {
                "database_name": f"{db_name}_updated",
                "expose_in_sqllab": False
            }

            response = self.session.put(
                f"{self.base_url}/api/v1/database/{db_id}",
                json=update_payload,
                headers=self.get_headers()
            )

            if response.status_code == 200:
                print(f"   ✓ Database atualizado")

                # Verificar atualização
                response = self.session.get(
                    f"{self.base_url}/api/v1/database/{db_id}",
                    headers=self.get_headers(with_csrf=False)
                )

                if response.status_code == 200:
                    updated_data = response.json().get("result", {})
                    print(f"   - Novo nome: {updated_data.get('database_name')}")
                    print(f"   - SQL Lab: {updated_data.get('expose_in_sqllab')}")
            else:
                print(f"   ✗ Falha ao atualizar: {response.status_code}")

            # DELETE
            print("\n4. DELETE - Deletando database...")
            response = self.session.delete(
                f"{self.base_url}/api/v1/database/{db_id}",
                headers=self.get_headers()
            )

            if response.status_code == 200:
                print(f"   ✓ Database deletado")

                # Verificar deleção
                response = self.session.get(
                    f"{self.base_url}/api/v1/database/{db_id}",
                    headers=self.get_headers(with_csrf=False)
                )

                if response.status_code == 404:
                    print(f"   ✓ Confirmado: Database não existe mais")
            else:
                print(f"   ✗ Falha ao deletar: {response.status_code}")

        except Exception as e:
            print(f"   ✗ Erro: {e}")

            # Cleanup em caso de erro
            if db_id:
                try:
                    self.session.delete(
                        f"{self.base_url}/api/v1/database/{db_id}",
                        headers=self.get_headers()
                    )
                except:
                    pass

    def test_dataset_crud(self):
        """Testa CRUD completo de Dataset"""
        print("\n" + "=" * 80)
        print("  TESTE CRUD - DATASET")
        print("=" * 80 + "\n")

        # Primeiro, pegar um database existente
        response = self.session.get(
            f"{self.base_url}/api/v1/database/",
            headers=self.get_headers(with_csrf=False)
        )

        if response.status_code != 200 or not response.json().get("result"):
            print("   ✗ Nenhum database disponível")
            return

        database_id = response.json()["result"][0]["id"]
        dataset_name = f"crud_test_dataset_{int(time.time())}"
        dataset_id = None

        try:
            # CREATE
            print("1. CREATE - Criando dataset virtual...")
            create_payload = {
                "database": database_id,
                "schema": "public",
                "table_name": dataset_name,
                "sql": "SELECT 1 as id, 'test' as name, NOW() as created_at",
                "is_managed_externally": False,
                "owners": []
            }

            response = self.session.post(
                f"{self.base_url}/api/v1/dataset/",
                json=create_payload,
                headers=self.get_headers()
            )

            if response.status_code == 201:
                dataset_id = response.json().get("id")
                print(f"   ✓ Dataset criado com ID: {dataset_id}")
            else:
                print(f"   ✗ Falha ao criar: {response.status_code}")
                print(f"   Response: {response.text}")
                return

            # READ
            print("\n2. READ - Lendo dataset criado...")
            response = self.session.get(
                f"{self.base_url}/api/v1/dataset/{dataset_id}",
                headers=self.get_headers(with_csrf=False)
            )

            if response.status_code == 200:
                ds_data = response.json().get("result", {})
                print(f"   ✓ Dataset encontrado: {ds_data.get('table_name')}")
                print(f"   - SQL: {ds_data.get('sql', 'N/A')[:50]}...")
                print(f"   - Colunas: {len(ds_data.get('columns', []))}")
            else:
                print(f"   ✗ Falha ao ler: {response.status_code}")

            # UPDATE
            print("\n3. UPDATE - Atualizando dataset...")
            update_payload = {
                "table_name": f"{dataset_name}_updated",
                "sql": "SELECT 1 as id, 'updated' as name, NOW() as created_at"
            }

            response = self.session.put(
                f"{self.base_url}/api/v1/dataset/{dataset_id}",
                json=update_payload,
                headers=self.get_headers()
            )

            if response.status_code == 200:
                print(f"   ✓ Dataset atualizado")
            else:
                print(f"   ✗ Falha ao atualizar: {response.status_code}")
                print(f"   Response: {response.text}")

            # DELETE
            print("\n4. DELETE - Deletando dataset...")
            response = self.session.delete(
                f"{self.base_url}/api/v1/dataset/{dataset_id}",
                headers=self.get_headers()
            )

            if response.status_code == 200:
                print(f"   ✓ Dataset deletado")
            else:
                print(f"   ✗ Falha ao deletar: {response.status_code}")

        except Exception as e:
            print(f"   ✗ Erro: {e}")

            # Cleanup
            if dataset_id:
                try:
                    self.session.delete(
                        f"{self.base_url}/api/v1/dataset/{dataset_id}",
                        headers=self.get_headers()
                    )
                except:
                    pass

    def test_chart_crud(self):
        """Testa CRUD completo de Chart"""
        print("\n" + "=" * 80)
        print("  TESTE CRUD - CHART")
        print("=" * 80 + "\n")

        # Pegar um dataset existente ou criar um
        response = self.session.get(
            f"{self.base_url}/api/v1/dataset/",
            headers=self.get_headers(with_csrf=False)
        )

        if response.status_code != 200 or not response.json().get("result"):
            print("   ✗ Nenhum dataset disponível")
            return

        datasource_id = response.json()["result"][0]["id"]
        chart_name = f"CRUD Test Chart {int(time.time())}"
        chart_id = None

        try:
            # CREATE
            print("1. CREATE - Criando chart...")
            create_payload = {
                "slice_name": chart_name,
                "datasource_id": datasource_id,
                "datasource_type": "table",
                "viz_type": "table",
                "params": json.dumps({
                    "metrics": [],
                    "groupby": [],
                    "all_columns": [],
                    "row_limit": 1000
                })
            }

            response = self.session.post(
                f"{self.base_url}/api/v1/chart/",
                json=create_payload,
                headers=self.get_headers()
            )

            if response.status_code == 201:
                chart_id = response.json().get("id")
                print(f"   ✓ Chart criado com ID: {chart_id}")
            else:
                print(f"   ✗ Falha ao criar: {response.status_code}")
                print(f"   Response: {response.text}")
                return

            # READ
            print("\n2. READ - Lendo chart criado...")
            response = self.session.get(
                f"{self.base_url}/api/v1/chart/{chart_id}",
                headers=self.get_headers(with_csrf=False)
            )

            if response.status_code == 200:
                chart_data = response.json().get("result", {})
                print(f"   ✓ Chart encontrado: {chart_data.get('slice_name')}")
                print(f"   - Tipo: {chart_data.get('viz_type')}")
                print(f"   - Datasource ID: {chart_data.get('datasource_id')}")
            else:
                print(f"   ✗ Falha ao ler: {response.status_code}")

            # UPDATE
            print("\n3. UPDATE - Atualizando chart...")
            update_payload = {
                "slice_name": f"{chart_name} - UPDATED",
                "description": "Chart atualizado via API"
            }

            response = self.session.put(
                f"{self.base_url}/api/v1/chart/{chart_id}",
                json=update_payload,
                headers=self.get_headers()
            )

            if response.status_code == 200:
                print(f"   ✓ Chart atualizado")
            else:
                print(f"   ✗ Falha ao atualizar: {response.status_code}")

            # DELETE
            print("\n4. DELETE - Deletando chart...")
            response = self.session.delete(
                f"{self.base_url}/api/v1/chart/{chart_id}",
                headers=self.get_headers()
            )

            if response.status_code == 200:
                print(f"   ✓ Chart deletado")
            else:
                print(f"   ✗ Falha ao deletar: {response.status_code}")

        except Exception as e:
            print(f"   ✗ Erro: {e}")

            # Cleanup
            if chart_id:
                try:
                    self.session.delete(
                        f"{self.base_url}/api/v1/chart/{chart_id}",
                        headers=self.get_headers()
                    )
                except:
                    pass

    def test_dashboard_crud(self):
        """Testa CRUD completo de Dashboard"""
        print("\n" + "=" * 80)
        print("  TESTE CRUD - DASHBOARD")
        print("=" * 80 + "\n")

        dashboard_title = f"CRUD Test Dashboard {int(time.time())}"
        dashboard_id = None

        try:
            # CREATE
            print("1. CREATE - Criando dashboard...")
            create_payload = {
                "dashboard_title": dashboard_title,
                "slug": None,
                "owners": [],
                "position_json": json.dumps({}),
                "css": "",
                "json_metadata": json.dumps({
                    "color_scheme": "supersetColors",
                    "refresh_frequency": 0,
                    "timed_refresh_immune_slices": [],
                    "expanded_slices": {},
                    "filter_scopes": {}
                }),
                "published": True
            }

            response = self.session.post(
                f"{self.base_url}/api/v1/dashboard/",
                json=create_payload,
                headers=self.get_headers()
            )

            if response.status_code == 201:
                dashboard_id = response.json().get("id")
                print(f"   ✓ Dashboard criado com ID: {dashboard_id}")
            else:
                print(f"   ✗ Falha ao criar: {response.status_code}")
                print(f"   Response: {response.text}")
                return

            # READ
            print("\n2. READ - Lendo dashboard criado...")
            response = self.session.get(
                f"{self.base_url}/api/v1/dashboard/{dashboard_id}",
                headers=self.get_headers(with_csrf=False)
            )

            if response.status_code == 200:
                dash_data = response.json().get("result", {})
                print(f"   ✓ Dashboard encontrado: {dash_data.get('dashboard_title')}")
                print(f"   - Publicado: {dash_data.get('published')}")
                print(f"   - Slug: {dash_data.get('slug')}")
            else:
                print(f"   ✗ Falha ao ler: {response.status_code}")

            # UPDATE
            print("\n3. UPDATE - Atualizando dashboard...")
            update_payload = {
                "dashboard_title": f"{dashboard_title} - UPDATED",
                "published": False,
                "css": "/* Custom CSS */"
            }

            response = self.session.put(
                f"{self.base_url}/api/v1/dashboard/{dashboard_id}",
                json=update_payload,
                headers=self.get_headers()
            )

            if response.status_code == 200:
                print(f"   ✓ Dashboard atualizado")
            else:
                print(f"   ✗ Falha ao atualizar: {response.status_code}")

            # DELETE
            print("\n4. DELETE - Deletando dashboard...")
            response = self.session.delete(
                f"{self.base_url}/api/v1/dashboard/{dashboard_id}",
                headers=self.get_headers()
            )

            if response.status_code == 200:
                print(f"   ✓ Dashboard deletado")
            else:
                print(f"   ✗ Falha ao deletar: {response.status_code}")

        except Exception as e:
            print(f"   ✗ Erro: {e}")

            # Cleanup
            if dashboard_id:
                try:
                    self.session.delete(
                        f"{self.base_url}/api/v1/dashboard/{dashboard_id}",
                        headers=self.get_headers()
                    )
                except:
                    pass

    def run_all_crud_tests(self):
        """Executa todos os testes CRUD"""
        print("\n" + "=" * 80)
        print("  TESTES CRUD - APACHE SUPERSET")
        print("  Testando operações Create, Read, Update, Delete")
        print("=" * 80)

        if not self.authenticate():
            print("\n❌ Falha na autenticação")
            return

        print("\n✓ Autenticação bem-sucedida\n")

        self.test_database_crud()
        self.test_dataset_crud()
        self.test_chart_crud()
        self.test_dashboard_crud()

        print("\n" + "=" * 80)
        print("  TESTES CRUD CONCLUÍDOS")
        print("=" * 80 + "\n")


def main():
    tester = SupersetCRUDTester(SUPERSET_URL, USERNAME, PASSWORD)
    tester.run_all_crud_tests()


if __name__ == "__main__":
    main()
