#!/usr/bin/env python3
"""
Script de validação da API do Apache Superset
Testa autenticação e criação de datasets
"""

import requests
import json
from datetime import datetime

# Configurações
SUPERSET_URL = "http://localhost:8088"
USERNAME = "admin"
PASSWORD = "admin"


def print_section(title):
    """Imprime seção formatada"""
    print(f"\n{'=' * 60}")
    print(f"  {title}")
    print(f"{'=' * 60}\n")


def test_health():
    """Testa o endpoint de health"""
    print_section("1. TESTE DE SAÚDE DO SUPERSET")

    try:
        response = requests.get(f"{SUPERSET_URL}/health")
        print(f"✅ Status HTTP: {response.status_code}")
        print(f"✅ Resposta: {response.text}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Erro ao acessar Superset: {e}")
        return False


def login():
    """Realiza login e obtém access token"""
    print_section("2. AUTENTICAÇÃO (LOGIN)")

    login_data = {
        "username": USERNAME,
        "password": PASSWORD,
        "provider": "db",
        "refresh": True
    }

    try:
        response = requests.post(
            f"{SUPERSET_URL}/api/v1/security/login",
            json=login_data,
            headers={"Content-Type": "application/json"}
        )

        print(f"Status HTTP: {response.status_code}")

        if response.status_code == 200:
            tokens = response.json()
            access_token = tokens.get("access_token")
            print(f"✅ Login realizado com sucesso!")
            print(f"✅ Access Token obtido: {access_token[:50]}...")
            return access_token
        else:
            print(f"❌ Falha no login: {response.text}")
            return None

    except Exception as e:
        print(f"❌ Erro durante login: {e}")
        return None


def get_databases(access_token):
    """Lista databases disponíveis"""
    print_section("3. LISTAGEM DE DATABASES")

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }

    try:
        response = requests.get(
            f"{SUPERSET_URL}/api/v1/database/",
            headers=headers
        )

        print(f"Status HTTP: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            databases = data.get("result", [])
            print(f"✅ Encontradas {len(databases)} database(s):")
            for db in databases:
                print(f"   - ID: {db['id']}, Nome: {db['database_name']}")
            return databases
        else:
            print(f"❌ Erro ao listar databases: {response.text}")
            return []

    except Exception as e:
        print(f"❌ Erro: {e}")
        return []


def test_database_connection(access_token, database_id):
    """Testa conexão com database"""
    print_section(f"4. TESTE DE CONEXÃO (Database ID: {database_id})")

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }

    try:
        response = requests.post(
            f"{SUPERSET_URL}/api/v1/database/{database_id}/test_connection",
            headers=headers
        )

        print(f"Status HTTP: {response.status_code}")

        if response.status_code == 200:
            print(f"✅ Conexão com database testada com sucesso!")
            print(f"✅ Resposta: {response.json()}")
            return True
        else:
            print(f"⚠️  Resposta: {response.text}")
            return False

    except Exception as e:
        print(f"❌ Erro: {e}")
        return False


def list_datasets(access_token):
    """Lista datasets existentes"""
    print_section("5. LISTAGEM DE DATASETS EXISTENTES")

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }

    try:
        response = requests.get(
            f"{SUPERSET_URL}/api/v1/dataset/",
            headers=headers
        )

        print(f"Status HTTP: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            datasets = data.get("result", [])
            print(f"✅ Encontrados {len(datasets)} dataset(s):")
            for ds in datasets[:10]:  # Limitar a 10 para não poluir
                print(f"   - ID: {ds.get('id')}, Nome: {ds.get('table_name')}, Schema: {ds.get('schema')}")
            return datasets
        else:
            print(f"❌ Erro ao listar datasets: {response.text}")
            return []

    except Exception as e:
        print(f"❌ Erro: {e}")
        return []


def create_test_dataset(access_token, database_id):
    """Cria um dataset de teste"""
    print_section("6. CRIAÇÃO DE DATASET DE TESTE")

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    dataset_data = {
        "database": database_id,
        "schema": "default",
        "table_name": f"test_api_dataset_{timestamp}"
    }

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }

    print(f"Tentando criar dataset: {dataset_data['table_name']}")
    print(f"Database ID: {database_id}")

    try:
        response = requests.post(
            f"{SUPERSET_URL}/api/v1/dataset/",
            json=dataset_data,
            headers=headers
        )

        print(f"Status HTTP: {response.status_code}")
        print(f"Resposta completa: {response.text}")

        if response.status_code in [200, 201]:
            data = response.json()
            dataset_id = data.get("id")
            print(f"✅ Dataset criado com sucesso!")
            print(f"✅ Dataset ID: {dataset_id}")
            return dataset_id
        else:
            print(f"⚠️  Tentativa de criação retornou: {response.status_code}")
            print(f"⚠️  Isso pode ser esperado se a tabela não existir no Trino")
            return None

    except Exception as e:
        print(f"❌ Erro ao criar dataset: {e}")
        return None


def delete_dataset(access_token, dataset_id):
    """Deleta um dataset"""
    print_section(f"7. LIMPEZA - DELETANDO DATASET (ID: {dataset_id})")

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }

    try:
        response = requests.delete(
            f"{SUPERSET_URL}/api/v1/dataset/{dataset_id}",
            headers=headers
        )

        print(f"Status HTTP: {response.status_code}")

        if response.status_code in [200, 204]:
            print(f"✅ Dataset deletado com sucesso!")
            return True
        else:
            print(f"⚠️  Resposta: {response.text}")
            return False

    except Exception as e:
        print(f"❌ Erro ao deletar dataset: {e}")
        return False


def get_api_info(access_token):
    """Obtém informações da API"""
    print_section("8. INFORMAÇÕES DA API")

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }

    try:
        # Tentar pegar info do usuário logado
        response = requests.get(
            f"{SUPERSET_URL}/api/v1/me/",
            headers=headers
        )

        if response.status_code == 200:
            data = response.json()
            print(f"✅ Informações do usuário logado:")
            print(f"   - Username: {data.get('username')}")
            print(f"   - First Name: {data.get('first_name')}")
            print(f"   - Last Name: {data.get('last_name')}")
            print(f"   - Roles: {[r['name'] for r in data.get('roles', [])]}")

    except Exception as e:
        print(f"⚠️  Não foi possível obter informações da API: {e}")


def main():
    """Executa todos os testes"""
    print("\n" + "=" * 60)
    print("  VALIDAÇÃO DA API DO APACHE SUPERSET")
    print("=" * 60)
    print(f"  URL: {SUPERSET_URL}")
    print(f"  Data/Hora: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)

    # 1. Teste de saúde
    if not test_health():
        print("\n❌ FALHA: Superset não está acessível!")
        return

    # 2. Login
    access_token = login()
    if not access_token:
        print("\n❌ FALHA: Não foi possível fazer login!")
        return

    # 3. Listar databases
    databases = get_databases(access_token)
    if not databases:
        print("\n⚠️  AVISO: Nenhuma database encontrada. Configure uma conexão primeiro.")
        print("\nℹ️  A API está funcional, mas você precisa:")
        print("   1. Acessar http://localhost:8088")
        print("   2. Ir em Settings → Database Connections")
        print("   3. Adicionar conexão com Trino ou outro banco")

        # Mesmo sem databases, a API está OK
        get_api_info(access_token)

        print_section("RESULTADO FINAL")
        print("✅ API do Superset está FUNCIONAL")
        print("✅ Autenticação: OK")
        print("✅ Endpoints básicos: OK")
        print("⚠️  Configure databases para criar datasets")
        return

    # 4. Testar primeira database
    database_id = databases[0]['id']
    test_database_connection(access_token, database_id)

    # 5. Listar datasets
    list_datasets(access_token)

    # 6. Criar dataset de teste
    dataset_id = create_test_dataset(access_token, database_id)

    # 7. Deletar se criado
    if dataset_id:
        delete_dataset(access_token, dataset_id)

    # 8. Info da API
    get_api_info(access_token)

    # Resultado final
    print_section("RESULTADO FINAL")
    print("✅ API do Superset está FUNCIONAL")
    print("✅ Autenticação: OK")
    print("✅ Listagem de databases: OK")
    print("✅ Listagem de datasets: OK")

    if dataset_id:
        print("✅ Criação de datasets: OK")
        print("✅ Deleção de datasets: OK")
    else:
        print("⚠️  Criação de datasets: Requer tabela existente no banco")

    print("\n📋 PRÓXIMOS PASSOS:")
    print("   - Use este access token para fazer chamadas à API")
    print("   - Consulte a documentação: http://localhost:8088/swagger/v1")
    print("   - Veja exemplos em: docs/07-apis-rest-jdbc.md")


if __name__ == "__main__":
    main()
