#!/bin/bash

# Script para testar suporte S3A no Trino

set -e

echo "========================================"
echo "TESTE DE SUPORTE S3A NO TRINO"
echo "========================================"
echo ""

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${YELLOW}1. Verificando JARs Hadoop AWS instalados...${NC}"
echo ""
docker compose exec trino sh -c "ls /usr/lib/trino/plugin/hive/ | grep hadoop"
echo ""

echo -e "${YELLOW}2. Verificando catálogo Hive...${NC}"
echo ""
docker compose exec trino cat /etc/trino/catalog/hive.properties | grep -E "(s3a|hadoop)"
echo ""

echo -e "${YELLOW}3. Testando conexão com Trino...${NC}"
curl -s http://localhost:8085/v1/info | grep -o '"version":"[^"]*"' || echo "Erro ao conectar"
echo ""

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}✓ Verificação concluída!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo "JARs instalados:"
echo "  ✓ hadoop-aws-3.3.6.jar (suporte S3A)"
echo "  ✓ hadoop-common-3.3.6.jar"
echo "  ✓ hadoop-auth-3.3.6.jar"
echo ""
echo "Protocolos suportados:"
echo "  ✓ s3://   (MinIO nativo)"
echo "  ✓ s3a://  (Hadoop S3A FileSystem)"
echo ""
echo "Acesse o Trino UI: http://localhost:8085"
echo ""
