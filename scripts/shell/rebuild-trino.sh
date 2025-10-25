#!/bin/bash

# Script para rebuild do Trino com suporte S3A

set -e

echo "========================================"
echo "REBUILD TRINO COM SUPORTE S3A (hadoop-aws)"
echo "========================================"
echo ""

# Cores para output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${YELLOW}1. Parando container Trino...${NC}"
docker compose stop trino

echo ""
echo -e "${YELLOW}2. Removendo container antigo...${NC}"
docker compose rm -f trino

echo ""
echo -e "${YELLOW}3. Removendo imagem antiga (se existir)...${NC}"
docker rmi mini-bigdata-trino:435-s3a 2>/dev/null || echo "Imagem não encontrada (OK)"

echo ""
echo -e "${YELLOW}4. Fazendo build da nova imagem com Hadoop AWS...${NC}"
docker compose build trino

echo ""
echo -e "${YELLOW}5. Iniciando novo container Trino...${NC}"
docker compose up -d trino

echo ""
echo -e "${YELLOW}6. Aguardando Trino inicializar (30s)...${NC}"
sleep 30

echo ""
echo -e "${YELLOW}7. Verificando status do Trino...${NC}"
docker compose ps trino

echo ""
echo -e "${YELLOW}8. Verificando JARs instalados...${NC}"
docker compose exec trino ls -lh /usr/lib/trino/plugin/hive/hadoop-*.jar || echo "Erro ao verificar JARs"

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}✓ Rebuild concluído!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo "Acesse o Trino em: http://localhost:8085"
echo ""
echo "Teste o protocolo s3a:// com:"
echo "  SELECT * FROM hive.default.\"tabela\$files\" WHERE path LIKE 's3a://%'"
echo ""
