#!/bin/bash

# ============================================
# Validação da Instalação do Superset v5
# ============================================

set -e

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🔍 Validação da Instalação do Apache Superset 5.0.0"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Cores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Funções
check_ok() {
    echo -e "${GREEN}✅ $1${NC}"
}

check_fail() {
    echo -e "${RED}❌ $1${NC}"
}

check_warn() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

# 1. Verificar se os containers estão rodando
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📦 Verificando containers..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

containers=("redis" "superset" "superset-worker" "superset-beat" "postgres")

for container in "${containers[@]}"; do
    if docker ps --format '{{.Names}}' | grep -q "^${container}$"; then
        status=$(docker inspect -f '{{.State.Health.Status}}' "$container" 2>/dev/null || echo "running")
        if [ "$status" = "healthy" ] || [ "$status" = "running" ]; then
            check_ok "Container $container está rodando"
        else
            check_warn "Container $container está rodando mas não está healthy"
        fi
    else
        check_fail "Container $container NÃO está rodando"
    fi
done

echo ""

# 2. Verificar conectividade Redis
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🔴 Verificando Redis..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

if docker exec superset-redis redis-cli ping > /dev/null 2>&1; then
    check_ok "Redis respondendo a ping"
else
    check_fail "Redis não está respondendo"
fi

echo ""

# 3. Verificar conectividade PostgreSQL
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🐘 Verificando PostgreSQL..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

if docker exec postgres pg_isready -U admin > /dev/null 2>&1; then
    check_ok "PostgreSQL respondendo"
    
    # Verificar se banco superset existe
    if docker exec postgres psql -U admin -lqt | cut -d \| -f 1 | grep -qw superset; then
        check_ok "Banco de dados 'superset' existe"
    else
        check_fail "Banco de dados 'superset' não encontrado"
    fi
else
    check_fail "PostgreSQL não está respondendo"
fi

echo ""

# 4. Verificar acesso web
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🌐 Verificando interface web..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

if curl -s -o /dev/null -w "%{http_code}" http://localhost:8088/health | grep -q "200"; then
    check_ok "Superset web acessível em http://localhost:8088"
else
    check_fail "Superset web não está acessível"
fi

echo ""

# 5. Verificar drivers instalados
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🔌 Verificando drivers instalados..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

drivers=("psycopg2" "trino" "redis" "celery" "mysqlclient")

for driver in "${drivers[@]}"; do
    if docker exec superset /app/.venv/bin/pip list 2>/dev/null | grep -qi "$driver"; then
        check_ok "Driver $driver instalado"
    else
        check_warn "Driver $driver pode não estar instalado"
    fi
done

echo ""

# 6. Verificar processos Celery
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "⚙️  Verificando Celery..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

if docker exec superset-worker pgrep -f celery > /dev/null 2>&1; then
    check_ok "Celery Worker está rodando"
else
    check_warn "Celery Worker pode não estar rodando"
fi

if docker exec superset-beat pgrep -f celery > /dev/null 2>&1; then
    check_ok "Celery Beat está rodando"
else
    check_warn "Celery Beat pode não estar rodando"
fi

echo ""

# 7. Verificar volumes
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "💾 Verificando volumes..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

volumes=("/media/marcelo/dados1/bigdata-docker/superset" "/media/marcelo/dados1/bigdata-docker/redis")

for vol in "${volumes[@]}"; do
    if [ -d "$vol" ]; then
        check_ok "Volume $vol existe"
    else
        check_warn "Volume $vol não encontrado"
    fi
done

echo ""

# 8. Resumo
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📊 Resumo"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "🌐 Acesse: http://localhost:8088"
echo "👤 Usuário: admin"
echo "🔑 Senha: admin"
echo ""
echo "📚 Documentação: docs/SUPERSET-v5-GUIA.md"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Comandos úteis
echo ""
echo "💡 Comandos úteis:"
echo ""
echo "  # Ver logs do Superset"
echo "  docker compose logs -f superset"
echo ""
echo "  # Reiniciar Superset"
echo "  docker compose restart superset"
echo ""
echo "  # Acessar shell do Superset"
echo "  docker exec -it superset bash"
echo ""
echo "  # Ver status de todos os serviços"
echo "  docker compose ps"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
