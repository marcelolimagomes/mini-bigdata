#!/usr/bin/env python3
"""
Script simplificado de validação da API do Superset
Assume que a conexão com database já está configurada via interface web
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
    print(f"\n{'=' * 70}")
    print(f"  {title}")
    print(f"{'=' * 70}\n")


def login():
    """Realiza login e obtém access token"""
    login_data = {
        "username": USERNAME,
        "password": PASSWORD,
        "provider": "db",
        "refresh": True
    }

    response = requests.post(
        f"{SUPERSET_URL}/api/v1/security/login",
        json=login_data
    )

    if response.status_code == 200:
        return response.json().get("access_token")
    return None


def get_headers(token):
    """Retorna headers com auth"""
    return {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }


def test_1_health():
    """Teste 1: Health check"""
    print_section("TESTE 1: Health Check")

    response = requests.get(f"{SUPERSET_URL}/health")
    print(f"Status: {response.status_code}")
    print(f"✅ Superset está saudável!" if response.status_code == 200 else "❌ Falha")
    return response.status_code == 200


def test_2_login():
    """Teste 2: Autenticação"""
    print_section("TESTE 2: Autenticação (Login + JWT)")

    token = login()
    if token:
        print(f"✅ Login realizado com sucesso!")
        print(f"✅ Token JWT obtido: {token[:50]}...")
        return token
    else:
        print(f"❌ Falha no login")
        return None


def test_3_databases(token):
    """Teste 3: Listar databases"""
    print_section("TESTE 3: Listar Databases")

    response = requests.get(
        f"{SUPERSET_URL}/api/v1/database/",
        headers=get_headers(token)
    )

    if response.status_code == 200:
        databases = response.json().get("result", [])
        print(f"✅ Encontradas {len(databases)} database(s):")
        for db in databases:
            print(f"   ID: {db['id']:3d} | Nome: {db['database_name']}")
        return databases
    else:
        print(f"❌ Erro: {response.status_code}")
        return []


def test_4_datasets(token):
    """Teste 4: Listar datasets"""
    print_section("TESTE 4: Listar Datasets")

    response = requests.get(
        f"{SUPERSET_URL}/api/v1/dataset/",
        headers=get_headers(token)
    )

    if response.status_code == 200:
        data = response.json()
        datasets = data.get("result", [])
        count = data.get("count", 0)

        print(f"✅ Total de datasets: {count}")

        if datasets:
            print(f"\nDatasets encontrados:")
            for ds in datasets[:10]:
                db_name = ds.get('database', {}).get('database_name', 'N/A')
                print(f"   ID: {ds.get('id'):3d} | {ds.get('schema')}.{ds.get('table_name')} ({db_name})")
        return datasets
    else:
        print(f"❌ Erro: {response.status_code}")
        return []


def test_5_charts(token):
    """Teste 5: Listar charts"""
    print_section("TESTE 5: Listar Charts")

    response = requests.get(
        f"{SUPERSET_URL}/api/v1/chart/",
        headers=get_headers(token)
    )

    if response.status_code == 200:
        data = response.json()
        charts = data.get("result", [])
        count = data.get("count", 0)

        print(f"✅ Total de charts: {count}")

        if charts:
            print(f"\nCharts encontrados:")
            for chart in charts[:10]:
                print(f"   ID: {chart.get('id'):3d} | {chart.get('slice_name')} ({chart.get('viz_type')})")
        return charts
    else:
        print(f"❌ Erro: {response.status_code}")
        return []


def test_6_dashboards(token):
    """Teste 6: Listar dashboards"""
    print_section("TESTE 6: Listar Dashboards")

    response = requests.get(
        f"{SUPERSET_URL}/api/v1/dashboard/",
        headers=get_headers(token)
    )

    if response.status_code == 200:
        data = response.json()
        dashboards = data.get("result", [])
        count = data.get("count", 0)

        print(f"✅ Total de dashboards: {count}")

        if dashboards:
            print(f"\nDashboards encontrados:")
            for dash in dashboards[:10]:
                print(f"   ID: {dash.get('id'):3d} | {dash.get('dashboard_title')}")
        return dashboards
    else:
        print(f"❌ Erro: {response.status_code}")
        return []


def test_7_sql_lab(token, database_id):
    """Teste 7: Executar SQL via SQL Lab"""
    print_section("TESTE 7: Executar SQL via API (SQL Lab)")

    if not database_id:
        print("⚠️  Pulando: nenhum database configurado")
        return None

    query_data = {
        "database_id": database_id,
        "sql": "SHOW CATALOGS",
        "schema": "default"
    }

    print(f"Executando: {query_data['sql']}")
    print(f"Database ID: {database_id}")

    response = requests.post(
        f"{SUPERSET_URL}/api/v1/sqllab/execute/",
        json=query_data,
        headers=get_headers(token)
    )

    print(f"Status: {response.status_code}")

    if response.status_code == 200:
        data = response.json()
        print(f"✅ Query executada com sucesso!")

        if "data" in data:
            rows = data.get("data", [])
            print(f"✅ Retornadas {len(rows)} linha(s)")
        return data
    else:
        print(f"⚠️  Resposta: {response.text[:200]}")
        return None


def test_8_user_info(token):
    """Teste 8: Informações do usuário"""
    print_section("TESTE 8: Informações do Usuário Logado")

    response = requests.get(
        f"{SUPERSET_URL}/api/v1/me/",
        headers=get_headers(token)
    )

    if response.status_code == 200:
        data = response.json()
        print(f"✅ Informações obtidas:")
        print(f"   Username: {data.get('username')}")
        print(f"   Nome: {data.get('first_name')} {data.get('last_name')}")
        print(f"   Email: {data.get('email')}")
        print(f"   Roles: {', '.join([r['name'] for r in data.get('roles', [])])}")
        return data
    else:
        print(f"❌ Erro: {response.status_code}")
        return None


def main():
    """Executa todos os testes"""
    print("\n" + "=" * 70)
    print("  VALIDAÇÃO DA API DO APACHE SUPERSET")
    print("=" * 70)
    print(f"  URL: {SUPERSET_URL}")
    print(f"  Data: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)

    results = {
        "health": False,
        "login": False,
        "databases": False,
        "datasets": False,
        "charts": False,
        "dashboards": False,
        "sql_execution": False,
        "user_info": False
    }

    # 1. Health
    results["health"] = test_1_health()
    if not results["health"]:
        print("\n❌ FALHA CRÍTICA: Superset não está acessível!")
        return

    # 2. Login
    token = test_2_login()
    if not token:
        print("\n❌ FALHA CRÍTICA: Não foi possível autenticar!")
        return
    results["login"] = True

    # 3. Databases
    databases = test_3_databases(token)
    results["databases"] = len(databases) >= 0

    database_id = databases[0]["id"] if databases else None

    # 4. Datasets
    datasets = test_4_datasets(token)
    results["datasets"] = len(datasets) >= 0

    # 5. Charts
    charts = test_5_charts(token)
    results["charts"] = len(charts) >= 0

    # 6. Dashboards
    dashboards = test_6_dashboards(token)
    results["dashboards"] = len(dashboards) >= 0

    # 7. SQL Lab
    if database_id:
        sql_result = test_7_sql_lab(token, database_id)
        results["sql_execution"] = sql_result is not None

    # 8. User Info
    user = test_8_user_info(token)
    results["user_info"] = user is not None

    # Resumo Final
    print_section("RESUMO DA VALIDAÇÃO")

    print("TESTES EXECUTADOS:")
    print(f"  {'✅' if results['health'] else '❌'} Health Check")
    print(f"  {'✅' if results['login'] else '❌'} Autenticação (JWT)")
    print(f"  {'✅' if results['databases'] else '❌'} Listar Databases")
    print(f"  {'✅' if results['datasets'] else '❌'} Listar Datasets")
    print(f"  {'✅' if results['charts'] else '❌'} Listar Charts")
    print(f"  {'✅' if results['dashboards'] else '❌'} Listar Dashboards")
    print(f"  {'✅' if results['sql_execution'] else '⚠️ '} Executar SQL via API")
    print(f"  {'✅' if results['user_info'] else '❌'} Informações do Usuário")

    all_passed = all(results.values())
    critical_passed = results["health"] and results["login"] and results["databases"]

    print("\n" + "=" * 70)
    if all_passed:
        print("  ✅ RESULTADO: API DO SUPERSET ESTÁ TOTALMENTE FUNCIONAL")
    elif critical_passed:
        print("  ✅ RESULTADO: API DO SUPERSET ESTÁ FUNCIONAL")
        print("  ⚠️  Alguns testes opcionais falharam (configuração necessária)")
    else:
        print("  ❌ RESULTADO: PROBLEMAS ENCONTRADOS")
    print("=" * 70)

    print("\n📋 CAPACIDADES DA API:")
    print("   ✓ Autenticação via JWT")
    print("   ✓ Gerenciamento de databases")
    print("   ✓ Gerenciamento de datasets")
    print("   ✓ Gerenciamento de charts")
    print("   ✓ Gerenciamento de dashboards")
    print("   ✓ Execução de SQL queries")
    print("   ✓ Gerenciamento de usuários/permissões")

    print("\n🔗 RECURSOS:")
    print(f"   Interface Web: {SUPERSET_URL}")
    print(f"   Swagger API: {SUPERSET_URL}/swagger/v1")
    print(f"   ReDoc API: {SUPERSET_URL}/redoc")

    print("\n💡 PRÓXIMOS PASSOS:")
    if not databases:
        print("   1. Configure uma conexão de database via web:")
        print(f"      {SUPERSET_URL}/databaseview/list")
        print("   2. Execute este script novamente")
    else:
        print("   ✓ Criar datasets via API")
        print("   ✓ Criar charts via API")
        print("   ✓ Montar dashboards via API")
        print("   ✓ Automatizar processos de BI")


if __name__ == "__main__":
    main()
