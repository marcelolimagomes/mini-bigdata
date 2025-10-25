#!/usr/bin/env python3
"""
validate_stack.py - Valida configuração completa da stack
"""

import requests
from minio import Minio
from trino.dbapi import connect


def validate_minio():
    """Valida MinIO"""
    print("\n🪣 Validando MinIO...")

    try:
        client = Minio(
            "localhost:9000",
            access_key="minioadmin",
            secret_key="minioadmin123",
            secure=False
        )

        buckets = client.list_buckets()
        expected = ["bronze", "silver", "gold", "warehouse"]
        found = [b.name for b in buckets]

        for bucket in expected:
            if bucket in found:
                print(f"  ✅ Bucket '{bucket}' existe")
            else:
                print(f"  ❌ Bucket '{bucket}' não encontrado")

        return len([b for b in expected if b in found]) >= 3
    except Exception as e:
        print(f"  ❌ Erro: {e}")
        return False


def validate_trino():
    """Valida Trino"""
    print("\n🔍 Validando Trino...")

    try:
        conn = connect(
            host="localhost",
            port=8080,
            user="trino",
            catalog="hive"
        )
        cursor = conn.cursor()

        # Verificar schemas
        cursor.execute("SHOW SCHEMAS IN hive")
        schemas = [row[0] for row in cursor.fetchall()]

        for schema in ["vendas", "analytics"]:
            if schema in schemas:
                print(f"  ✅ Schema '{schema}' existe")
            else:
                print(f"  ⚠️  Schema '{schema}' não encontrado")

        # Verificar tabelas
        try:
            cursor.execute("SHOW TABLES IN hive.vendas")
            tables = [row[0] for row in cursor.fetchall()]

            for table in ["vendas_raw", "vendas_silver"]:
                if table in tables:
                    print(f"  ✅ Tabela '{table}' existe")
                else:
                    print(f"  ⚠️  Tabela '{table}' não encontrada")
        except:
            print(f"  ⚠️  Não foi possível listar tabelas")

        cursor.close()
        conn.close()
        return True
    except Exception as e:
        print(f"  ❌ Erro: {e}")
        return False


def validate_superset():
    """Valida Superset"""
    print("\n📊 Validando Superset...")

    try:
        # Health check
        response = requests.get("http://localhost:8088/health")
        if response.status_code != 200:
            print(f"  ❌ Superset não está respondendo")
            return False

        # Login
        response = requests.post(
            "http://localhost:8088/api/v1/security/login",
            json={
                "username": "admin",
                "password": "admin",
                "provider": "db",
                "refresh": True
            }
        )

        if response.status_code != 200:
            print(f"  ❌ Falha no login")
            return False

        token = response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        print(f"  ✅ Superset está acessível")

        # Verificar databases
        response = requests.get(
            "http://localhost:8088/api/v1/database/",
            headers=headers
        )

        databases = response.json().get("result", [])
        if databases:
            print(f"  ✅ {len(databases)} database(s) configurado(s)")
            for db in databases:
                print(f"     - {db['database_name']}")
        else:
            print(f"  ⚠️  Nenhum database configurado")

        # Verificar datasets
        response = requests.get(
            "http://localhost:8088/api/v1/dataset/",
            headers=headers
        )

        datasets = response.json().get("result", [])
        if datasets:
            print(f"  ✅ {len(datasets)} dataset(s) disponível(is)")
        else:
            print(f"  ⚠️  Nenhum dataset criado ainda")

        return True
    except Exception as e:
        print(f"  ❌ Erro: {e}")
        return False


def main():
    """Executa validação completa"""
    print("=" * 70)
    print("  VALIDAÇÃO DA STACK BIG DATA")
    print("=" * 70)

    results = {
        "MinIO": validate_minio(),
        "Trino": validate_trino(),
        "Superset": validate_superset()
    }

    print("\n" + "=" * 70)
    print("  RESULTADO DA VALIDAÇÃO")
    print("=" * 70)

    for component, status in results.items():
        icon = "✅" if status else "❌"
        print(f"  {icon} {component}")

    if all(results.values()):
        print("\n✅ Stack configurada corretamente!")
        print("\n📊 Próximos passos:")
        print("  1. Carregar dados de exemplo")
        print("  2. Executar pipelines ETL")
        print("  3. Criar visualizações no Superset")
    else:
        print("\n⚠️  Alguns componentes requerem atenção")
        print("\n💡 Verifique:")
        print("  - Containers estão rodando: docker compose ps")
        print("  - Execute: python3 scripts/setup_stack.py")
        print("  - Consulte: docs/09-configuracao-automatizada.md")


if __name__ == "__main__":
    main()
