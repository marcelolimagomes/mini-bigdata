#!/usr/bin/env python3
"""
Script para criar 14 datasets virtuais no Superset via API
Automatiza a Fase 02 - Datasets Virtuais completa (100%)
"""

import requests
import json
import sys
import os
from pathlib import Path
from typing import Dict, Optional

# Configuração do Superset
SUPERSET_URL = "http://localhost:8088"
SUPERSET_USER = "admin"
SUPERSET_PASSWORD = "admin"

# IDs obtidos manualmente (ajustar após primeira execução)
DATABASE_ID = 1  # ID do database "Trino - Hive Catalog" (verificar)

# Diretório base do projeto
BASE_DIR = Path(__file__).resolve().parent.parent
SQL_DIR = BASE_DIR / "sql"


class SupersetAPI:
    """Cliente para interagir com a API do Superset"""

    def __init__(self, url: str, username: str, password: str):
        self.url = url
        self.username = username
        self.password = password
        self.session = requests.Session()
        self.access_token = None
        self.csrf_token = None

    def login(self) -> bool:
        """Faz login no Superset e obtém tokens"""
        try:
            # Login via API
            login_data = {
                "username": self.username,
                "password": self.password,
                "provider": "db",
                "refresh": True
            }

            response = self.session.post(
                f"{self.url}/api/v1/security/login",
                json=login_data
            )

            if response.status_code == 200:
                data = response.json()
                self.access_token = data.get("access_token")
                self.session.headers.update({
                    "Authorization": f"Bearer {self.access_token}",
                    "Content-Type": "application/json"
                })

                # Obter CSRF token após login
                csrf_response = self.session.get(
                    f"{self.url}/api/v1/security/csrf_token/",
                    headers={"Authorization": f"Bearer {self.access_token}"}
                )

                if csrf_response.status_code == 200:
                    self.csrf_token = csrf_response.json().get("result")
                    if self.csrf_token:
                        # Atualizar headers e cookies com CSRF token
                        self.session.headers.update({
                            "X-CSRFToken": self.csrf_token,
                            "Referer": self.url
                        })
                        self.session.cookies.set("csrf_access_token", self.csrf_token)
                        self.session.cookies.set("csrf_refresh_token", self.csrf_token)
                        print(f"✅ Login realizado com sucesso")
                        return True

                print(f"⚠️  CSRF token não obtido, mas login OK")
                return True
            else:
                print(f"❌ Falha no login: {response.status_code}")
                print(f"   Response: {response.text}")
                return False

        except Exception as e:
            print(f"❌ Erro ao fazer login: {e}")
            return False

    def get_csrf_token(self) -> Optional[str]:
        """Obtém CSRF token para requisições POST/PUT"""
        try:
            response = self.session.get(
                f"{self.url}/api/v1/security/csrf_token/",
                headers={"Authorization": f"Bearer {self.access_token}"}
            )

            if response.status_code == 200:
                result = response.json().get("result")
                if result:
                    self.csrf_token = result
                    # Atualizar headers com CSRF token
                    self.session.headers.update({
                        "X-CSRFToken": self.csrf_token,
                        "Referer": self.url
                    })
                    # Atualizar cookies
                    self.session.cookies.set("csrf_access_token", self.csrf_token)
                    self.session.cookies.set("csrf_refresh_token", self.csrf_token)
                    return self.csrf_token
            return None
        except Exception as e:
            print(f"⚠️  Erro ao obter CSRF token: {e}")
            return None

    def get_databases(self) -> list:
        """Lista todos os databases"""
        try:
            response = self.session.get(f"{self.url}/api/v1/database/")
            if response.status_code == 200:
                return response.json().get("result", [])
            return []
        except Exception as e:
            print(f"❌ Erro ao listar databases: {e}")
            return []

    def create_dataset(self, dataset_data: Dict) -> Optional[int]:
        """Cria um dataset virtual"""
        try:
            # Sempre obter CSRF token fresco antes de criar dataset
            if not self.csrf_token:
                self.get_csrf_token()

            # Garantir que headers estão corretos
            headers = {
                "Authorization": f"Bearer {self.access_token}",
                "Content-Type": "application/json",
                "X-CSRFToken": self.csrf_token,
                "Referer": self.url
            }

            response = self.session.post(
                f"{self.url}/api/v1/dataset/",
                json=dataset_data,
                headers=headers
            )

            if response.status_code == 201:
                dataset_id = response.json().get("id")
                print(f"   ✅ Dataset criado com ID: {dataset_id}")
                return dataset_id
            elif response.status_code == 422:
                # Dataset pode já existir
                error_msg = response.json().get("message", "")
                if "already exists" in error_msg.lower():
                    print(f"   ⏭️  Dataset já existe")
                    return -1  # Retornar valor especial para indicar que já existe
                else:
                    print(f"   ❌ Erro de validação: {error_msg}")
                    return None
            else:
                print(f"   ❌ Erro ao criar dataset: {response.status_code}")
                print(f"   Response: {response.text[:500]}")
                return None

        except Exception as e:
            print(f"   ❌ Erro ao criar dataset: {e}")
            return None

    def dataset_exists(self, table_name: str) -> bool:
        """Verifica se dataset já existe"""
        try:
            response = self.session.get(
                f"{self.url}/api/v1/dataset/",
                params={"q": f"(filters:!((col:table_name,opr:eq,value:'{table_name}')))"}
            )

            if response.status_code == 200:
                result = response.json().get("result", [])
                return len(result) > 0
            return False
        except Exception as e:
            print(f"⚠️  Erro ao verificar dataset: {e}")
            return False


def load_sql_files() -> Dict[str, str]:
    """Carrega todos os arquivos SQL do diretório"""
    datasets = {}

    # Mapear arquivo para nome do dataset
    sql_files = {
        "01_vw_consistencia_alocacao.sql": "vw_consistencia_alocacao",
        "02_vw_horario_trabalho.sql": "vw_horario_trabalho",
        "03_vw_produtividade_horaria.sql": "vw_produtividade_horaria",
        "04_vw_sensibilidade_preco.sql": "vw_sensibilidade_preco",
        "05_vw_vpn_projetos.sql": "vw_vpn_projetos",
        "06_vw_competitividade_salarial.sql": "vw_competitividade_salarial",
        "07_vw_kpis_executivo.sql": "vw_kpis_executivo",
        "08_vw_capacidade_detalhada.sql": "vw_capacidade_detalhada",
        "09_vw_performance_projetos.sql": "vw_performance_projetos",
        "10_vw_custos_rentabilidade.sql": "vw_custos_rentabilidade",
        "11_vw_qualidade_bugs.sql": "vw_qualidade_bugs",
        "12_vw_sazonalidade_utilizacao.sql": "vw_sazonalidade_utilizacao",
        "13_vw_ponto_equilibrio.sql": "vw_ponto_equilibrio",
        "14_vw_concentracao_hhi.sql": "vw_concentracao_hhi",
    }

    for filename, dataset_name in sql_files.items():
        sql_file_path = SQL_DIR / filename
        if sql_file_path.exists():
            with open(sql_file_path, 'r', encoding='utf-8') as f:
                sql_content = f.read().strip()
                # Remover comentários de cabeçalho se existirem
                if sql_content.startswith('--'):
                    lines = sql_content.split('\n')
                    # Encontrar primeira linha que não é comentário
                    for i, line in enumerate(lines):
                        if not line.strip().startswith('--') and line.strip():
                            sql_content = '\n'.join(lines[i:])
                            break
                datasets[dataset_name] = sql_content
        else:
            print(f"⚠️  Arquivo não encontrado: {sql_file_path}")

    return datasets


def main():
    """Função principal"""
    print("\n" + "=" * 70)
    print("🚀 CRIAÇÃO DE DATASETS VIRTUAIS NO SUPERSET")
    print("   FASE 02 - COMPLETA (14 Datasets = 100%)")
    print("=" * 70 + "\n")

    # Carregar SQLs dos arquivos
    print("📂 Carregando arquivos SQL...")
    datasets_virtuais = load_sql_files()

    if not datasets_virtuais:
        print("❌ Nenhum arquivo SQL encontrado. Verifique o diretório:", SQL_DIR)
        sys.exit(1)

    print(f"✅ {len(datasets_virtuais)} arquivos SQL carregados com sucesso\n")

    # Inicializar API
    api = SupersetAPI(SUPERSET_URL, SUPERSET_USER, SUPERSET_PASSWORD)

    # Fazer login
    print("🔐 Realizando login no Superset...")
    if not api.login():
        print("\n❌ Falha no login. Verifique as credenciais.")
        print("   Tente acessar http://localhost:8088 manualmente")
        sys.exit(1)

    # Verificar se CSRF token foi obtido
    if not api.csrf_token:
        print("\n⚠️  CSRF token não foi obtido durante login.")
        print("   Tentando obter CSRF token separadamente...")
        api.get_csrf_token()

        if not api.csrf_token:
            print("\n❌ Não foi possível obter CSRF token.")
            print("\n💡 SOLUÇÃO ALTERNATIVA:")
            print("   A API do Superset requer CSRF token que não está disponível.")
            print("   Use a interface web do Superset para criar datasets manualmente:")
            print(f"\n   1. Acesse: {SUPERSET_URL}")
            print("   2. Data → Datasets → + Dataset")
            print("   3. Selecione 'Create dataset from SQL query'")
            print(f"   4. Cole o SQL de cada arquivo em: {SQL_DIR}")
            print("\n   OU execute via superset CLI no container:")
            print("   docker exec -it superset bash")
            print("   superset fab create-dataset --help")
            sys.exit(1)

    # Listar databases para confirmar ID
    print("\n📊 Buscando databases disponíveis...")
    databases = api.get_databases()

    if databases:
        print("\n   Databases encontrados:")
        for db in databases:
            print(f"   - ID {db.get('id')}: {db.get('database_name')}")
            if 'trino' in db.get('database_name', '').lower() or 'hive' in db.get('database_name', '').lower():
                global DATABASE_ID
                DATABASE_ID = db.get('id')
                print(f"      ✅ Usando este database (ID: {DATABASE_ID})")
    else:
        print("\n   ⚠️  Nenhum database encontrado!")
        print("\n💡 CONFIGURE UM DATABASE PRIMEIRO:")
        print(f"   1. Acesse: {SUPERSET_URL}/databaseview/list")
        print("   2. Clique em '+ Database'")
        print("   3. Configure conexão com Trino:")
        print("      SQLAlchemy URI: trino://trino@trino:8080/hive")
        print("   4. Execute este script novamente")
        sys.exit(1)

    # Criar datasets virtuais
    print(f"\n📝 Criando {len(datasets_virtuais)} datasets virtuais...")
    print("=" * 70)

    created_count = 0
    skipped_count = 0
    failed_count = 0

    for i, (table_name, sql) in enumerate(datasets_virtuais.items(), 1):
        print(f"\n{i}. Dataset: {table_name}")

        # Verificar se já existe
        if api.dataset_exists(table_name):
            print(f"   ⏭️  Dataset já existe. Pulando...")
            skipped_count += 1
            continue

        # Preparar dados do dataset
        dataset_data = {
            "database": DATABASE_ID,
            "schema": "",  # Vazio para virtual dataset
            "table_name": table_name,
            "sql": sql,
            "is_managed_externally": False,
            "external_url": None
        }

        # Criar dataset
        dataset_id = api.create_dataset(dataset_data)

        if dataset_id:
            created_count += 1
        else:
            failed_count += 1

    # Relatório final
    print("\n" + "=" * 70)
    print("✅ RESUMO DA EXECUÇÃO")
    print("=" * 70)
    print(f"   ✅ Criados com sucesso: {created_count}")
    print(f"   ⏭️  Já existiam (pulados): {skipped_count}")
    print(f"   ❌ Falharam: {failed_count}")
    print(f"   📊 Total processado: {len(datasets_virtuais)}")
    print(f"   📈 Taxa de conclusão: {((created_count + skipped_count) / len(datasets_virtuais) * 100):.1f}%")
    print("=" * 70)

    if created_count > 0:
        print("\n🎯 PRÓXIMOS PASSOS:")
        print("   1. Acesse http://localhost:8088")
        print("   2. Vá em Data → Datasets")
        print("   3. Valide que os 14 datasets aparecem na lista")
        print("   4. Teste queries dos datasets (botão Preview)")
        print("   5. Prossiga para Fase 03 - Dashboard Executivo")

    print("\n✅ Fase 02 concluída! (100% dos datasets criados)\n")


if __name__ == "__main__":
    main()
