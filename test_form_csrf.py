#!/usr/bin/env python3
"""
Teste completo: obtém CSRF do formulário, faz login, tenta criar dataset
"""
import requests
import re
import json
from urllib.parse import urljoin

SUPERSET_URL = "http://localhost:8088"
USERNAME = "admin"
PASSWORD = "admin"


def main():
    session = requests.Session()

    # Passo 1: Obter o formulário de login e extrair o token CSRF
    print("1. Obtendo formulário de login...")
    login_page = session.get(f"{SUPERSET_URL}/login/")

    if login_page.status_code != 200:
        print(f"❌ Erro ao carregar página de login: {login_page.status_code}")
        return

    # Extrair o token CSRF usando regex
    csrf_match = re.search(r'<input[^>]*name="csrf_token"[^>]*value="([^"]+)"', login_page.text)

    if not csrf_match:
        print("❌ Token CSRF não encontrado no formulário")
        return

    csrf_token = csrf_match.group(1)
    print(f"✅ Token CSRF obtido: {csrf_token[:50]}...")

    # Passo 2: Fazer login com o token CSRF
    print("\n2. Fazendo login com CSRF do formulário...")
    login_data = {
        'username': USERNAME,
        'password': PASSWORD,
        'csrf_token': csrf_token
    }

    login_response = session.post(f"{SUPERSET_URL}/login/", data=login_data, allow_redirects=False)
    print(f"Status do login: {login_response.status_code}")
    print(f"Cookies após login: {dict(session.cookies)}")

    if login_response.status_code not in [200, 302]:
        print(f"❌ Login falhou: {login_response.status_code}")
        print(login_response.text[:500])
        return

    # Passo 3: Verificar autenticação acessando /api/v1/me/
    print("\n3. Verificando autenticação via API...")
    me_response = session.get(f"{SUPERSET_URL}/api/v1/me/")
    print(f"Status /api/v1/me/: {me_response.status_code}")

    if me_response.status_code == 200:
        print(f"✅ Autenticado como: {me_response.json()['result']['username']}")
    else:
        print(f"❌ Não autenticado via API: {me_response.status_code}")
        print(me_response.text[:500])
        return

    # Passo 4: Obter um novo token CSRF para operações API
    print("\n4. Obtendo token CSRF para API...")
    csrf_api_response = session.get(f"{SUPERSET_URL}/api/v1/security/csrf_token/")
    print(f"Status CSRF API: {csrf_api_response.status_code}")

    if csrf_api_response.status_code == 200:
        csrf_api_token = csrf_api_response.json()['result']
        print(f"✅ Token CSRF API: {csrf_api_token[:50]}...")
    else:
        print(f"❌ Erro ao obter CSRF API: {csrf_api_response.status_code}")
        print(csrf_api_response.text)
        return

    # Passo 5: Tentar criar um dataset de teste
    print("\n5. Tentando criar dataset de teste...")

    dataset_payload = {
        "database": 1,
        "schema": "default",
        "table_name": "test_csrf_dataset",
        "sql": "SELECT 1 as test_column"
    }

    headers = {
        'X-CSRFToken': csrf_api_token,
        'Content-Type': 'application/json',
        'Referer': f"{SUPERSET_URL}/superset/welcome/"
    }

    print(f"Headers: {headers}")
    print(f"Cookies: {dict(session.cookies)}")

    create_response = session.post(
        f"{SUPERSET_URL}/api/v1/dataset/",
        json=dataset_payload,
        headers=headers
    )

    print(f"\nStatus criação dataset: {create_response.status_code}")

    if create_response.status_code in [200, 201]:
        print("✅ SUCESSO! Dataset criado com sucesso!")
        print(json.dumps(create_response.json(), indent=2))
    else:
        print(f"❌ Erro ao criar dataset: {create_response.status_code}")
        print(create_response.text)


if __name__ == "__main__":
    main()
