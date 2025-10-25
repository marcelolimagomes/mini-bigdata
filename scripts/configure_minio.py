#!/usr/bin/env python3
"""
configure_minio.py - Configura buckets no MinIO
"""

from minio import Minio
from minio.error import S3Error

# Configuração
MINIO_ENDPOINT = "localhost:9000"
MINIO_ACCESS_KEY = "minioadmin"
MINIO_SECRET_KEY = "minioadmin123"


def setup_minio():
    """Configura buckets no MinIO"""

    # Conectar ao MinIO
    client = Minio(
        MINIO_ENDPOINT,
        access_key=MINIO_ACCESS_KEY,
        secret_key=MINIO_SECRET_KEY,
        secure=False
    )

    # Buckets para criar (arquitetura Medallion)
    buckets = ["bronze", "silver", "gold", "warehouse", "raw-data"]

    print("🪣 Configurando buckets no MinIO...\n")

    for bucket in buckets:
        try:
            # Verificar se bucket existe
            if client.bucket_exists(bucket):
                print(f"  ✅ Bucket '{bucket}' já existe")
            else:
                # Criar bucket
                client.make_bucket(bucket)
                print(f"  ✅ Bucket '{bucket}' criado com sucesso")
        except S3Error as e:
            print(f"  ❌ Erro ao criar bucket '{bucket}': {e}")

    print("\n✅ Configuração do MinIO concluída!")

    # Listar todos os buckets
    print("\n📋 Buckets disponíveis:")
    buckets = client.list_buckets()
    for bucket in buckets:
        print(f"  - {bucket.name} (criado em {bucket.creation_date})")


if __name__ == "__main__":
    setup_minio()
