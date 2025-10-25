#!/bin/bash
# Script para validar instalação dos drivers Trino no Superset

echo "🔍 VALIDANDO DRIVERS TRINO NO SUPERSET"
echo "======================================"
echo ""

# Verificar se container está rodando
echo "1️⃣  Verificando se container Superset está rodando..."
if docker ps | grep -q superset; then
    echo "   ✅ Container Superset está rodando"
else
    echo "   ❌ Container Superset NÃO está rodando"
    echo "   Execute: docker-compose up -d superset"
    exit 1
fi

echo ""
echo "2️⃣  Verificando drivers instalados..."
echo ""

# Verificar psycopg2-binary
echo -n "   📦 psycopg2-binary: "
if docker exec superset pip list 2>/dev/null | grep -q psycopg2-binary; then
    VERSION=$(docker exec superset pip show psycopg2-binary 2>/dev/null | grep Version | awk '{print $2}')
    echo "✅ v$VERSION"
else
    echo "❌ NÃO INSTALADO"
fi

# Verificar trino
echo -n "   📦 trino: "
if docker exec superset pip list 2>/dev/null | grep -E "^trino " | grep -q trino; then
    VERSION=$(docker exec superset pip show trino 2>/dev/null | grep Version | awk '{print $2}')
    echo "✅ v$VERSION"
else
    echo "❌ NÃO INSTALADO"
fi

# Verificar sqlalchemy-trino
echo -n "   📦 sqlalchemy-trino: "
if docker exec superset pip list 2>/dev/null | grep -q sqlalchemy-trino; then
    VERSION=$(docker exec superset pip show sqlalchemy-trino 2>/dev/null | grep Version | awk '{print $2}')
    echo "✅ v$VERSION"
else
    echo "❌ NÃO INSTALADO"
fi

echo ""
echo "3️⃣  Testando importação Python..."
echo ""

# Testar importação trino
echo -n "   🐍 import trino: "
if docker exec superset python -c "import trino" 2>/dev/null; then
    echo "✅ OK"
else
    echo "❌ ERRO"
fi

# Testar importação sqlalchemy_trino
echo -n "   🐍 import sqlalchemy_trino: "
if docker exec superset python -c "from sqlalchemy.dialects import registry; registry.load('trino')" 2>/dev/null; then
    echo "✅ OK"
else
    echo "❌ ERRO"
fi

echo ""
echo "4️⃣  Verificando configuração de volumes..."
echo ""

# Verificar se requirements.txt existe
echo -n "   📄 requirements.txt montado: "
if docker exec superset test -f /app/pythonpath/requirements.txt 2>/dev/null; then
    echo "✅ SIM"
    echo "      Conteúdo:"
    docker exec superset cat /app/pythonpath/requirements.txt 2>/dev/null | sed 's/^/      /'
else
    echo "❌ NÃO"
fi

echo ""
echo "5️⃣  Verificando acesso ao Trino..."
echo ""

# Verificar se Trino está rodando
echo -n "   🔍 Container Trino: "
if docker ps | grep -q trino; then
    echo "✅ Rodando"
else
    echo "⚠️  NÃO está rodando"
fi

# Testar conectividade
echo -n "   🌐 Conectividade Superset → Trino: "
if docker exec superset curl -s -o /dev/null -w "%{http_code}" http://trino:8080/v1/info 2>/dev/null | grep -q 200; then
    echo "✅ OK (HTTP 200)"
else
    echo "❌ FALHA"
fi

echo ""
echo "======================================"
echo "✅ VALIDAÇÃO CONCLUÍDA"
echo ""
echo "📖 Próximos passos:"
echo "   1. Acesse: http://localhost:8088"
echo "   2. Login: admin / admin"
echo "   3. Settings → Database Connections → + Database"
echo "   4. URI: trino://trino@trino:8080/hive"
echo "   5. Test Connection"
echo ""
echo "📚 Documentação: SUPERSET-DRIVERS.md"
