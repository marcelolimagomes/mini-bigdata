#!/usr/bin/env python3
"""
Teste usando autenticação via web form + API
"""

import requests
import json

SUPERSET_URL = "http://localhost:8088"
SUPERSET_USER = "admin"
SUPERSET_PASSWORD = "admin"


def test_web_login_then_api():
    """Faz login via web primeiro, depois usa API"""

    print("🔍 TESTANDO: LOGIN WEB + API")
    print("=" * 70)

    session = requests.Session()

    # 1. GET na página de login
    print("\n1️⃣  Acessando página de login...")
    login_page = session.get(f"{SUPERSET_URL}/login/")
    print(f"   Status: {login_page.status_code}")
    print(f"   Cookies: {list(session.cookies.keys())}")

    # 2. Fazer login via formulário
    print("\n2️⃣  Login via formulário web...")
    form_data = {
        "username": SUPERSET_USER,
        "password": SUPERSET_PASSWORD
    }

    login_response = session.post(
        f"{SUPERSET_URL}/login/",
        data=form_data,
        allow_redirects=True
    )

    print(f"   Status: {login_response.status_code}")
    print(f"   Cookies após login: {list(session.cookies.keys())}")
    print(f"   URL final: {login_response.url}")

    # 3. Verificar se está logado
    print("\n3️⃣  Verificando sessão...")
    me_response = session.get(f"{SUPERSET_URL}/api/v1/me/")
    print(f"   Status /api/v1/me/: {me_response.status_code}")

    if me_response.status_code == 200:
        user_info = me_response.json()
        print(f"   ✅ Logado como: {user_info.get('result', {}).get('username')}")
    else:
        print(f"   ❌ Não autenticado")
        return

    # 4. Obter CSRF token
    print("\n4️⃣  Obtendo CSRF token...")
    csrf_response = session.get(f"{SUPERSET_URL}/api/v1/security/csrf_token/")
    print(f"   Status: {csrf_response.status_code}")

    if csrf_response.status_code == 200:
        csrf_data = csrf_response.json()
        csrf_token = csrf_data.get("result")
        print(f"   ✅ CSRF Token: {csrf_token[:30]}...")

        # 5. Configurar headers para POST
        session.headers.update({
            "X-CSRFToken": csrf_token,
            "Referer": SUPERSET_URL,
            "Content-Type": "application/json"
        })

        # 6. Testar criação de dataset
        print("\n5️⃣  Criando dataset...")

        dataset_data = {
            "database": 1,
            "schema": "",
            "table_name": "test_web_login",
            "sql": "SELECT 5 as test",
            "is_managed_externally": False,
            "external_url": None
        }

        create_response = session.post(
            f"{SUPERSET_URL}/api/v1/dataset/",
            json=dataset_data
        )

        print(f"   Status: {create_response.status_code}")
        print(f"   Response: {create_response.text[:500]}")

        if create_response.status_code == 201:
            print("\n   ✅ SUCESSO! Este é o método que funciona!")
            return True
        elif create_response.status_code == 422:
            response_data = create_response.json()
            if "already exists" in str(response_data):
                print("\n   ✅ SUCESSO! (dataset já existia)")
                return True

    return False


if __name__ == "__main__":
    success = test_web_login_then_api()
    if success:
        print("\n" + "=" * 70)
        print("✅ SOLUÇÃO ENCONTRADA!")
        print("   Use login via formulário web ao invés de API login")
        print("=" * 70)
