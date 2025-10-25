#!/usr/bin/env python3
"""
Teste final - usando csrf_token do cookie de sessão
"""

import requests
import json
import base64

SUPERSET_URL = "http://localhost:8088"
SUPERSET_USER = "admin"
SUPERSET_PASSWORD = "admin"


def decode_session_cookie(session_cookie):
    """Decodifica o cookie de sessão do Flask"""
    try:
        # O cookie de sessão do Flask é base64 encoded
        parts = session_cookie.split('.')
        if len(parts) >= 1:
            # Decodificar a primeira parte (payload)
            payload = parts[0]
            # Adicionar padding se necessário
            missing_padding = len(payload) % 4
            if missing_padding:
                payload += '=' * (4 - missing_padding)

            decoded = base64.urlsafe_b64decode(payload)
            return json.loads(decoded)
    except Exception as e:
        print(f"   Erro ao decodificar: {e}")
    return None


def test_session_csrf():
    """Testa usando CSRF token da sessão"""

    print("🔍 TESTANDO COM CSRF TOKEN DA SESSÃO")
    print("=" * 70)

    session = requests.Session()

    # 1. GET inicial
    print("\n1️⃣  GET inicial...")
    session.get(f"{SUPERSET_URL}/")
    initial_session = session.cookies.get('session')
    print(f"   Session cookie: {initial_session[:50]}...")

    # Decodificar para ver o csrf_token
    session_data = decode_session_cookie(initial_session)
    if session_data:
        print(f"   Session data: {session_data}")
        if 'csrf_token' in session_data:
            initial_csrf = session_data['csrf_token']
            print(f"   CSRF no cookie: {initial_csrf}")

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
        print(f"   ❌ Falha no login")
        return

    access_token = login_response.json()["access_token"]
    print(f"   ✅ Login OK")

    # Checar session cookie após login
    after_login_session = session.cookies.get('session')
    session_data2 = decode_session_cookie(after_login_session)
    if session_data2:
        print(f"   Session após login: {session_data2}")
        if 'csrf_token' in session_data2:
            csrf_from_session = session_data2['csrf_token']
            print(f"   ✅ CSRF no session cookie: {csrf_from_session}")

    # 3. Usar o CSRF token do cookie de sessão
    print("\n3️⃣  Usando CSRF token do cookie de sessão...")

    session.headers.update({
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
        "X-CSRFToken": csrf_from_session,
        "Referer": SUPERSET_URL
    })

    # 4. Testar criação
    print("\n4️⃣  Testando criação de dataset...")

    dataset_data = {
        "database": 1,
        "schema": "",
        "table_name": "test_session_csrf",
        "sql": "SELECT 4 as test",
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
        dataset_id = create_response.json().get("id")
        print(f"   Dataset ID: {dataset_id}")
    elif create_response.status_code == 422:
        print("\n   ⚠️  Dataset já existe")
    else:
        print("\n   ❌ Falha")


if __name__ == "__main__":
    test_session_csrf()
