#!/usr/bin/env python3
"""
Exemplo prático de uso das APIs do Apache Superset
Demonstra configuração completa: Database -> Dataset -> Chart -> Dashboard
"""

import requests
import json
import time
from typing import Optional


class SupersetAutomation:
    """Classe para automação de configuração do Superset via API"""

    def __init__(self, base_url: str, username: str, password: str):
        self.base_url = base_url
        self.session = requests.Session()
        self.access_token = None
        self.csrf_token = None

        # Autenticar automaticamente
        self._authenticate(username, password)

    def _authenticate(self, username: str, password: str) -> bool:
        """Autentica e obtém tokens"""
        print("🔐 Autenticando...")

        # Login
        response = self.session.post(
            f"{self.base_url}/api/v1/security/login",
            json={
                "username": username,
                "password": password,
                "provider": "db",
                "refresh": True
            }
        )

        if response.status_code != 200:
            raise Exception(f"Falha na autenticação: {response.text}")

        self.access_token = response.json().get("access_token")

        # CSRF Token
        response = self.session.get(
            f"{self.base_url}/api/v1/security/csrf_token/",
            headers={"Authorization": f"Bearer {self.access_token}"}
        )

        if response.status_code == 200:
            self.csrf_token = response.json().get("result")

        print("✓ Autenticação bem-sucedida\n")
        return True

    def _get_headers(self, with_csrf: bool = True) -> dict:
        """Retorna headers padrão para requisições"""
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }
        if with_csrf and self.csrf_token:
            headers["X-CSRFToken"] = self.csrf_token
            headers["Referer"] = self.base_url
        return headers

    def create_database(self, name: str, uri: str, expose_in_sqllab: bool = True) -> int:
        """Cria um novo database"""
        print(f"📊 Criando database: {name}")

        payload = {
            "database_name": name,
            "sqlalchemy_uri": uri,
            "expose_in_sqllab": expose_in_sqllab,
            "allow_run_async": True,
            "allow_ctas": True,
            "allow_cvas": True,
            "allow_file_upload": False,
            "extra": json.dumps({
                "metadata_params": {},
                "engine_params": {},
                "metadata_cache_timeout": {},
                "schemas_allowed_for_file_upload": []
            })
        }

        response = self.session.post(
            f"{self.base_url}/api/v1/database/",
            json=payload,
            headers=self._get_headers()
        )

        if response.status_code != 201:
            raise Exception(f"Falha ao criar database: {response.text}")

        db_id = response.json().get("id")
        print(f"✓ Database criado (ID: {db_id})\n")
        return db_id

    def create_virtual_dataset(self, database_id: int, name: str, sql: str) -> int:
        """Cria um dataset virtual"""
        print(f"📋 Criando dataset virtual: {name}")

        payload = {
            "database": database_id,
            "schema": "public",
            "table_name": name,
            "sql": sql,
            "is_managed_externally": False,
            "owners": []
        }

        response = self.session.post(
            f"{self.base_url}/api/v1/dataset/",
            json=payload,
            headers=self._get_headers()
        )

        if response.status_code != 201:
            raise Exception(f"Falha ao criar dataset: {response.text}")

        ds_id = response.json().get("id")
        print(f"✓ Dataset criado (ID: {ds_id})\n")
        return ds_id

    def create_chart(self, name: str, datasource_id: int, viz_type: str = "table",
                     metrics: list = None, groupby: list = None) -> int:
        """Cria um chart"""
        print(f"📈 Criando chart: {name}")

        params = {
            "viz_type": viz_type,
            "metrics": metrics or [],
            "groupby": groupby or [],
            "row_limit": 1000
        }

        payload = {
            "slice_name": name,
            "datasource_id": datasource_id,
            "datasource_type": "table",
            "viz_type": viz_type,
            "params": json.dumps(params),
            "description": f"Chart criado via API - {time.strftime('%Y-%m-%d %H:%M:%S')}"
        }

        response = self.session.post(
            f"{self.base_url}/api/v1/chart/",
            json=payload,
            headers=self._get_headers()
        )

        if response.status_code != 201:
            raise Exception(f"Falha ao criar chart: {response.text}")

        chart_id = response.json().get("id")
        print(f"✓ Chart criado (ID: {chart_id})\n")
        return chart_id

    def create_dashboard(self, title: str, chart_ids: list = None) -> int:
        """Cria um dashboard"""
        print(f"📊 Criando dashboard: {title}")

        # Position JSON básico para os charts
        position_json = {}
        if chart_ids:
            # Layout simples em coluna
            for i, chart_id in enumerate(chart_ids):
                position_json[f"CHART-{chart_id}"] = {
                    "type": "CHART",
                    "id": chart_id,
                    "meta": {
                        "chartId": chart_id,
                        "width": 12,
                        "height": 50
                    }
                }

        payload = {
            "dashboard_title": title,
            "slug": None,
            "owners": [],
            "position_json": json.dumps(position_json),
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
            json=payload,
            headers=self._get_headers()
        )

        if response.status_code != 201:
            raise Exception(f"Falha ao criar dashboard: {response.text}")

        dash_id = response.json().get("id")
        print(f"✓ Dashboard criado (ID: {dash_id})\n")
        return dash_id

    def execute_sql(self, database_id: int, sql: str) -> dict:
        """Executa uma query SQL"""
        print(f"🔍 Executando SQL...")

        payload = {
            "database_id": database_id,
            "sql": sql,
            "runAsync": False
        }

        response = self.session.post(
            f"{self.base_url}/api/v1/sqllab/execute/",
            json=payload,
            headers=self._get_headers()
        )

        if response.status_code != 200:
            raise Exception(f"Falha ao executar SQL: {response.text}")

        result = response.json()
        print(f"✓ Query executada com sucesso\n")
        return result

    def list_databases(self) -> list:
        """Lista todos os databases"""
        response = self.session.get(
            f"{self.base_url}/api/v1/database/",
            headers=self._get_headers(with_csrf=False)
        )

        if response.status_code == 200:
            return response.json().get("result", [])
        return []

    def delete_database(self, db_id: int) -> bool:
        """Deleta um database"""
        print(f"🗑️  Deletando database ID: {db_id}")

        response = self.session.delete(
            f"{self.base_url}/api/v1/database/{db_id}",
            headers=self._get_headers()
        )

        if response.status_code == 200:
            print(f"✓ Database deletado\n")
            return True
        return False


def exemplo_completo():
    """Exemplo completo de uso das APIs"""
    print("=" * 80)
    print("  EXEMPLO PRÁTICO - AUTOMAÇÃO SUPERSET VIA API")
    print("=" * 80 + "\n")

    # Configurações
    SUPERSET_URL = "http://localhost:8088"
    USERNAME = "admin"
    PASSWORD = "admin"

    # Inicializar
    superset = SupersetAutomation(SUPERSET_URL, USERNAME, PASSWORD)

    try:
        # 1. Usar database existente
        databases = superset.list_databases()
        if not databases:
            print("❌ Nenhum database disponível")
            return

        db_id = databases[0]["id"]
        db_name = databases[0]["database_name"]
        print(f"📊 Usando database existente: {db_name} (ID: {db_id})\n")

        # 3. Criar Dataset Virtual
        dataset_name = f"vw_exemplo_{int(time.time())}"
        dataset_id = superset.create_virtual_dataset(
            database_id=db_id,
            name=dataset_name,
            sql="""
                SELECT 
                    1 as id,
                    'Produto A' as produto,
                    1000.50 as valor,
                    NOW() as data_criacao
                UNION ALL
                SELECT 
                    2 as id,
                    'Produto B' as produto,
                    2500.75 as valor,
                    NOW() as data_criacao
            """
        )

        # 4. Criar Charts
        chart_ids = []

        # Chart 1 - Tabela
        chart1_id = superset.create_chart(
            name=f"Tabela de Produtos - {int(time.time())}",
            datasource_id=dataset_id,
            viz_type="table"
        )
        chart_ids.append(chart1_id)

        # Chart 2 - Outro chart de exemplo
        chart2_id = superset.create_chart(
            name=f"Análise de Produtos - {int(time.time())}",
            datasource_id=dataset_id,
            viz_type="table"
        )
        chart_ids.append(chart2_id)

        # 5. Criar Dashboard com os charts
        dashboard_id = superset.create_dashboard(
            title=f"Dashboard de Exemplo - {int(time.time())}",
            chart_ids=chart_ids
        )

        # 6. Resumo
        print("=" * 80)
        print("  ✅ RECURSOS CRIADOS COM SUCESSO!")
        print("=" * 80 + "\n")

        print(f"📊 Database ID: {db_id} - Nome: {db_name}")
        print(f"📋 Dataset ID: {dataset_id} - Nome: {dataset_name}")
        print(f"📈 Chart 1 ID: {chart1_id}")
        print(f"📈 Chart 2 ID: {chart2_id}")
        print(f"📊 Dashboard ID: {dashboard_id}")

        print(f"\n🌐 Acesse o dashboard em:")
        print(f"   {SUPERSET_URL}/superset/dashboard/{dashboard_id}/\n")

        # 7. Opcional - Limpar recursos (comentado por padrão)
        """
        print("\n🗑️  Limpando recursos criados...")
        superset.delete_database(db_id)
        print("✓ Limpeza concluída")
        """

    except Exception as e:
        print(f"\n❌ Erro: {e}")
        raise

    print("\n" + "=" * 80)
    print("  EXEMPLO CONCLUÍDO")
    print("=" * 80 + "\n")


def exemplo_simples():
    """Exemplo simples - apenas listar databases"""
    print("\n" + "=" * 80)
    print("  EXEMPLO SIMPLES - LISTAR DATABASES")
    print("=" * 80 + "\n")

    superset = SupersetAutomation(
        "http://localhost:8088",
        "admin",
        "admin"
    )

    databases = superset.list_databases()

    print(f"Total de databases: {len(databases)}\n")

    for db in databases:
        print(f"ID: {db.get('id')}")
        print(f"Nome: {db.get('database_name')}")
        print(f"SQL Lab: {db.get('expose_in_sqllab')}")
        print(f"Backend: {db.get('backend', 'N/A')}")
        print("-" * 80)


if __name__ == "__main__":
    # Executar exemplo completo
    exemplo_completo()

    # Ou executar exemplo simples:
    # exemplo_simples()
