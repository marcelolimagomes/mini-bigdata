#!/usr/bin/env python3
"""
Teste com login via API + CSRF
"""
import requests
import json

SUPERSET_URL = "http://localhost:8088"
USERNAME = "admin"
PASSWORD = "admin"


def main():
    session = requests.Session()

    # Passo 1: Login via API para obter access_token
    print("1. Fazendo login via API...")
    login_payload = {
        "username": USERNAME,
        "password": PASSWORD,
        "provider": "db",
        "refresh": True
    }

    login_response = session.post(
        f"{SUPERSET_URL}/api/v1/security/login",
        json=login_payload
    )

    print(f"Status login API: {login_response.status_code}")

    if login_response.status_code != 200:
        print(f"❌ Login falhou: {login_response.text}")
        return

    access_token = login_response.json()['access_token']
    print(f"✅ Access token obtido: {access_token[:50]}...")
    print(f"Cookies após login: {dict(session.cookies)}")

    # Passo 2: Obter CSRF token
    print("\n2. Obtendo CSRF token...")

    # Adicionar Authorization header
    session.headers.update({
        'Authorization': f'Bearer {access_token}'
    })

    csrf_response = session.get(f"{SUPERSET_URL}/api/v1/security/csrf_token/")
    print(f"Status CSRF: {csrf_response.status_code}")

    if csrf_response.status_code != 200:
        print(f"❌ Erro ao obter CSRF: {csrf_response.text}")
        return

    csrf_token = csrf_response.json()['result']
    print(f"✅ CSRF token obtido: {csrf_token[:50]}...")
    print(f"Cookies após CSRF: {dict(session.cookies)}")

    # Passo 3: Configurar headers completos
    print("\n3. Configurando headers para criação de dataset...")

    session.headers.update({
        'X-CSRFToken': csrf_token,
        'Content-Type': 'application/json',
        'Referer': f"{SUPERSET_URL}/",
    })

    # Passo 4: Tentar criar dataset
    print("\n4. Criando dataset de teste...")

    dataset_payload = {
        "database": 1,
        "schema": "default",
        "table_name": "test_final_dataset",
        "sql": "SELECT 1 as test_column"
    }

    print(f"Payload: {json.dumps(dataset_payload, indent=2)}")
    print(f"Headers: {dict(session.headers)}")
    print(f"Cookies: {dict(session.cookies)}")

    create_response = session.post(
        f"{SUPERSET_URL}/api/v1/dataset/",
        json=dataset_payload
    )

    print(f"\nStatus criação: {create_response.status_code}")

    if create_response.status_code in [200, 201]:
        print("✅ SUCESSO! Dataset criado!")
        print(json.dumps(create_response.json(), indent=2))
    else:
        print(f"❌ Erro: {create_response.status_code}")
        try:
            print(json.dumps(create_response.json(), indent=2))
        except:
            print(create_response.text)


if __name__ == "__main__":
    main()
