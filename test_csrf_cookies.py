#!/usr/bin/env python3
"""
Script de teste avançado para CSRF token - testando cookies
"""

import requests
import json

SUPERSET_URL = "http://localhost:8088"
SUPERSET_USER = "admin"
SUPERSET_PASSWORD = "admin"


def test_with_cookies():
    """Testa com configuração completa de cookies"""

    print("🔍 TESTANDO COM COOKIES CSRF")
    print("=" * 70)

    session = requests.Session()

    # 1. GET inicial para obter cookie de sessão
    print("\n1️⃣  GET inicial...")
    session.get(f"{SUPERSET_URL}/")
    print(f"   Cookies: {dict(session.cookies)}")

    # 2. Login via API
    print("\n2️⃣  Login via API...")
    login_response = session.post(
        f"{SUPERSET_URL}/api/v1/security/login",
        json={
            "username": SUPERSET_USER,
            "password": SUPERSET_PASSWORD,
            "provider": "db",
            "refresh": True
        }
    )

    if login_response.status_code != 200:
        print(f"   ❌ Falha no login: {login_response.status_code}")
        return

    access_token = login_response.json()["access_token"]
    print(f"   ✅ Login OK")
    print(f"   Cookies após login: {dict(session.cookies)}")

    # 3. Obter CSRF token
    print("\n3️⃣  Obtendo CSRF token...")
    session.headers.update({
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    })

    csrf_response = session.get(f"{SUPERSET_URL}/api/v1/security/csrf_token/")

    if csrf_response.status_code != 200:
        print(f"   ❌ Falha ao obter CSRF: {csrf_response.status_code}")
        return

    csrf_token = csrf_response.json()["result"]
    print(f"   ✅ CSRF Token obtido: {csrf_token[:30]}...")
    print(f"   Cookies após CSRF: {dict(session.cookies)}")

    # 4. Configurar CSRF token no cookie manualmente
    print("\n4️⃣  Configurando CSRF token nos cookies...")

    # O Superset espera o token no cookie csrf_access_token
    session.cookies.set('csrf_access_token', csrf_token, domain='localhost', path='/')
    session.cookies.set('csrf_refresh_token', csrf_token, domain='localhost', path='/')

    print(f"   Cookies atualizados: {dict(session.cookies)}")

    # 5. Atualizar headers
    session.headers.update({
        "X-CSRFToken": csrf_token,
        "Referer": SUPERSET_URL
    })

    print(f"   Headers: {dict(session.headers)}")

    # 6. Testar criação de dataset
    print("\n5️⃣  Testando criação de dataset...")

    dataset_data = {
        "database": 1,
        "schema": "",
        "table_name": "test_dataset_final",
        "sql": "SELECT 3 as test",
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
        print("\n   ✅ SUCESSO! Dataset criado!")
    elif create_response.status_code == 422:
        print("\n   ⚠️  Dataset já existe (esperado em retry)")
    else:
        print("\n   ❌ Falha na criação")

        # Debug adicional
        print("\n📊 Debug adicional:")
        print(f"   Cookies enviados: {dict(session.cookies)}")
        print(f"   Headers enviados: {dict(session.headers)}")


if __name__ == "__main__":
    test_with_cookies()
