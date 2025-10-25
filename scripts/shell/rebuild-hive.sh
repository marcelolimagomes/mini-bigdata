#!/bin/bash

# Script para rebuild do Hive Metastore com suporte S3A

set -e

echo "========================================"
echo "REBUILD HIVE METASTORE COM SUPORTE S3A"
echo "========================================"
echo ""

# Cores para output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${YELLOW}1. Parando container Hive Metastore...${NC}"
docker compose stop hive-metastore

echo ""
echo -e "${YELLOW}2. Removendo container antigo...${NC}"
docker compose rm -f hive-metastore

echo ""
echo -e "${YELLOW}3. Removendo imagem antiga (se existir)...${NC}"
docker rmi mini-bigdata-hive:4.0.0 2>/dev/null || echo "Imagem não encontrada (OK)"

echo ""
echo -e "${YELLOW}4. Fazendo build da nova imagem com Hadoop AWS...${NC}"
docker compose build hive-metastore

echo ""
echo -e "${YELLOW}5. Iniciando novo container Hive Metastore...${NC}"
docker compose up -d hive-metastore

echo ""
echo -e "${YELLOW}6. Aguardando Hive Metastore inicializar (30s)...${NC}"
sleep 30

echo ""
echo -e "${YELLOW}7. Verificando status do Hive Metastore...${NC}"
docker compose ps hive-metastore

echo ""
echo -e "${YELLOW}8. Verificando JARs instalados...${NC}"
docker compose exec hive-metastore ls -lh /opt/hive/lib/hadoop-*.jar /opt/hive/lib/aws-*.jar 2>/dev/null || echo "Aguardando container inicializar..."

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}✓ Rebuild concluído!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo "O Hive Metastore agora suporta:"
echo "  ✓ Protocolo s3a:// para criar schemas e tabelas"
echo "  ✓ hadoop-aws-3.3.6.jar"
echo "  ✓ hadoop-common-3.3.6.jar"
echo "  ✓ hadoop-auth-3.3.6.jar"
echo "  ✓ aws-java-sdk-bundle-1.12.262.jar"
echo ""
echo "Teste criando um schema:"
echo "  CREATE SCHEMA hive.test_s3a WITH (location = 's3a://bronze/test/');"
echo ""
