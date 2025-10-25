#!/bin/bash

# Script para validar suporte S3A completo na stack

set -e

echo "========================================"
echo "VALIDAÇÃO COMPLETA DE SUPORTE S3A"
echo "========================================"
echo ""

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${YELLOW}1. VALIDANDO HIVE METASTORE${NC}"
echo "   Verificando JARs Hadoop AWS..."
HIVE_JARS=$(docker compose exec hive-metastore sh -c "ls /opt/hive/lib/ | grep -E '(hadoop|aws)' | wc -l")
if [ "$HIVE_JARS" -ge 4 ]; then
    echo -e "   ${GREEN}✓${NC} JARs encontrados: $HIVE_JARS"
    docker compose exec hive-metastore sh -c "ls /opt/hive/lib/ | grep -E '(hadoop-aws|hadoop-common|hadoop-auth|aws-java-sdk)'"
else
    echo -e "   ${RED}✗${NC} JARs insuficientes: $HIVE_JARS (esperado >= 4)"
    exit 1
fi

echo ""
echo "   Verificando core-site.xml..."
if docker compose exec hive-metastore test -f /opt/hive/conf/core-site.xml; then
    echo -e "   ${GREEN}✓${NC} core-site.xml encontrado"
else
    echo -e "   ${RED}✗${NC} core-site.xml não encontrado"
    exit 1
fi

echo ""
echo -e "${YELLOW}2. VALIDANDO TRINO${NC}"
echo "   Verificando JARs Hadoop AWS..."
TRINO_JARS=$(docker compose exec trino sh -c "ls /usr/lib/trino/plugin/hive/ | grep -E '(hadoop|aws)' | wc -l")
if [ "$TRINO_JARS" -ge 3 ]; then
    echo -e "   ${GREEN}✓${NC} JARs encontrados: $TRINO_JARS"
    docker compose exec trino sh -c "ls /usr/lib/trino/plugin/hive/ | grep -E '(hadoop-aws|hadoop-common|hadoop-auth)'"
else
    echo -e "   ${RED}✗${NC} JARs insuficientes: $TRINO_JARS (esperado >= 3)"
    exit 1
fi

echo ""
echo "   Verificando core-site.xml..."
if docker compose exec trino test -f /etc/trino/core-site.xml; then
    echo -e "   ${GREEN}✓${NC} core-site.xml encontrado"
else
    echo -e "   ${RED}✗${NC} core-site.xml não encontrado"
    exit 1
fi

echo ""
echo "   Verificando catálogo Hive..."
if docker compose exec trino grep -q "hive.config.resources" /etc/trino/catalog/hive.properties; then
    echo -e "   ${GREEN}✓${NC} Catálogo configurado com core-site.xml"
else
    echo -e "   ${RED}✗${NC} Catálogo não referencia core-site.xml"
    exit 1
fi

echo ""
echo -e "${YELLOW}3. VALIDANDO MINIO${NC}"
echo "   Verificando status..."
if curl -s http://localhost:9000/minio/health/live > /dev/null 2>&1; then
    echo -e "   ${GREEN}✓${NC} MinIO operacional"
else
    echo -e "   ${RED}✗${NC} MinIO não respondendo"
    exit 1
fi

echo ""
echo "   Verificando buckets..."
BUCKETS=$(docker compose exec minio-client sh -c "mc alias set myminio http://minio:9000 minioadmin minioadmin123 > /dev/null 2>&1 && mc ls myminio | wc -l" 2>/dev/null || echo "0")
echo -e "   ${GREEN}✓${NC} Buckets encontrados: $BUCKETS"

echo ""
echo -e "${YELLOW}4. VERIFICANDO CONECTIVIDADE${NC}"
echo "   Testando conexão Trino → Hive Metastore..."
if docker compose exec trino curl -s http://hive-metastore:9083 > /dev/null 2>&1; then
    echo -e "   ${GREEN}✓${NC} Conexão estabelecida"
else
    echo -e "   ${YELLOW}⚠${NC} Porta 9083 não responde HTTP (normal para Thrift)"
fi

echo ""
echo "   Testando conexão Hive → MinIO..."
if docker compose exec hive-metastore curl -s http://minio:9000/minio/health/live > /dev/null 2>&1; then
    echo -e "   ${GREEN}✓${NC} Conexão estabelecida"
else
    echo -e "   ${RED}✗${NC} Sem conexão com MinIO"
    exit 1
fi

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}✓ VALIDAÇÃO COMPLETA COM SUCESSO!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo "📊 RESUMO:"
echo "  ✓ Hive Metastore: $HIVE_JARS JARs S3A"
echo "  ✓ Trino: $TRINO_JARS JARs S3A"
echo "  ✓ MinIO: $BUCKETS buckets"
echo "  ✓ Configurações: core-site.xml OK"
echo ""
echo "🧪 TESTES SUGERIDOS:"
echo ""
echo "1. Criar schema S3A via Trino:"
echo "   trino> CREATE SCHEMA hive.test_s3a WITH (location = 's3a://bronze/test/');"
echo ""
echo "2. Criar tabela S3A:"
echo "   trino> CREATE TABLE hive.test_s3a.sample ("
echo "          id BIGINT,"
echo "          name VARCHAR"
echo "          ) WITH (external_location = 's3a://bronze/test/sample/');"
echo ""
echo "3. Inserir dados:"
echo "   trino> INSERT INTO hive.test_s3a.sample VALUES (1, 'test');"
echo ""
echo "4. Consultar:"
echo "   trino> SELECT * FROM hive.test_s3a.sample;"
echo ""
