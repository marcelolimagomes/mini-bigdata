#!/usr/bin/env python3
"""
Script de debug para testar CSRF token do Superset
"""

import requests
import json

SUPERSET_URL = "http://localhost:8088"
SUPERSET_USER = "admin"
SUPERSET_PASSWORD = "admin"


def test_csrf_methods():
    """Testa diferentes métodos de obter e usar CSRF token"""

    print("🔍 TESTANDO MÉTODOS DE CSRF TOKEN")
    print("=" * 70)

    # Método 1: Via API Login + CSRF endpoint
    print("\n1️⃣  Método 1: Login API + CSRF endpoint")
    session1 = requests.Session()

    # Login
    login_response = session1.post(
        f"{SUPERSET_URL}/api/v1/security/login",
        json={
            "username": SUPERSET_USER,
            "password": SUPERSET_PASSWORD,
            "provider": "db",
            "refresh": True
        }
    )

    if login_response.status_code == 200:
        access_token = login_response.json()["access_token"]
        print(f"   ✅ Login OK - Token: {access_token[:20]}...")

        # Tentar obter CSRF via GET
        csrf_response = session1.get(
            f"{SUPERSET_URL}/api/v1/security/csrf_token/",
            headers={"Authorization": f"Bearer {access_token}"}
        )

        print(f"   Status CSRF GET: {csrf_response.status_code}")
        print(f"   Response: {csrf_response.text[:200]}")

        if csrf_response.status_code == 200:
            csrf_token = csrf_response.json().get("result")
            print(f"   ✅ CSRF Token: {csrf_token[:20] if csrf_token else 'NONE'}...")

    # Método 2: Login via formulário web
    print("\n2️⃣  Método 2: Login via formulário web")
    session2 = requests.Session()

    # Primeiro, acessar página de login para obter cookie de sessão
    login_page = session2.get(f"{SUPERSET_URL}/login/")
    print(f"   Status GET /login/: {login_page.status_code}")
    print(f"   Cookies após GET: {list(session2.cookies.keys())}")

    # Fazer POST no formulário de login
    form_login = session2.post(
        f"{SUPERSET_URL}/login/",
        data={
            "username": SUPERSET_USER,
            "password": SUPERSET_PASSWORD
        },
        allow_redirects=False
    )

    print(f"   Status POST /login/: {form_login.status_code}")
    print(f"   Cookies após POST: {list(session2.cookies.keys())}")

    # Tentar obter CSRF
    csrf_response2 = session2.get(f"{SUPERSET_URL}/api/v1/security/csrf_token/")
    print(f"   Status CSRF: {csrf_response2.status_code}")

    if csrf_response2.status_code == 200:
        csrf_data = csrf_response2.json()
        print(f"   Response: {csrf_data}")
        csrf_token2 = csrf_data.get("result")
        print(f"   ✅ CSRF Token via web: {csrf_token2[:20] if csrf_token2 else 'NONE'}...")

        # Testar criar dataset com este método
        print("\n   🧪 Testando criação de dataset com login web...")

        dataset_data = {
            "database": 1,
            "schema": "",
            "table_name": "test_dataset_csrf",
            "sql": "SELECT 1 as test",
            "is_managed_externally": False,
            "external_url": None
        }

        create_response = session2.post(
            f"{SUPERSET_URL}/api/v1/dataset/",
            json=dataset_data,
            headers={
                "X-CSRFToken": csrf_token2,
                "Referer": SUPERSET_URL,
                "Content-Type": "application/json"
            }
        )

        print(f"   Status criação: {create_response.status_code}")
        print(f"   Response: {create_response.text[:300]}")

    # Método 3: Combinado - Login API + usar cookies de sessão
    print("\n3️⃣  Método 3: Login API com cookies de sessão")
    session3 = requests.Session()

    # Primeiro GET na raiz para obter cookie de sessão
    session3.get(f"{SUPERSET_URL}/")
    print(f"   Cookies iniciais: {list(session3.cookies.keys())}")

    # Login via API
    login3 = session3.post(
        f"{SUPERSET_URL}/api/v1/security/login",
        json={
            "username": SUPERSET_USER,
            "password": SUPERSET_PASSWORD,
            "provider": "db",
            "refresh": True
        }
    )

    if login3.status_code == 200:
        token3 = login3.json()["access_token"]
        print(f"   ✅ Login OK")
        print(f"   Cookies após login: {list(session3.cookies.keys())}")

        # Atualizar headers com Bearer token
        session3.headers.update({
            "Authorization": f"Bearer {token3}",
            "Content-Type": "application/json"
        })

        # Obter CSRF
        csrf3 = session3.get(f"{SUPERSET_URL}/api/v1/security/csrf_token/")
        print(f"   Status CSRF: {csrf3.status_code}")
        print(f"   Cookies após CSRF: {list(session3.cookies.keys())}")

        if csrf3.status_code == 200:
            csrf_token3 = csrf3.json().get("result")
            print(f"   CSRF Token: {csrf_token3[:20] if csrf_token3 else 'NONE'}...")

            # Testar criação
            print("\n   🧪 Testando criação de dataset...")

            session3.headers.update({
                "X-CSRFToken": csrf_token3,
                "Referer": SUPERSET_URL
            })

            dataset_data = {
                "database": 1,
                "schema": "",
                "table_name": "test_dataset_method3",
                "sql": "SELECT 2 as test",
                "is_managed_externally": False,
                "external_url": None
            }

            create3 = session3.post(
                f"{SUPERSET_URL}/api/v1/dataset/",
                json=dataset_data
            )

            print(f"   Status criação: {create3.status_code}")
            print(f"   Response: {create3.text[:300]}")


if __name__ == "__main__":
    test_csrf_methods()
