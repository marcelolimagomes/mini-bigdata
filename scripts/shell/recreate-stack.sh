#!/bin/bash
#
# recreate-stack.sh - Recria toda a stack do zero
#
# Este script:
# 1. Para e remove todos os containers
# 2. Remove volumes Docker
# 3. Apaga a pasta de dados
# 4. Recria a estrutura de diretórios
# 5. Sobe a stack completa
# 6. Valida os serviços
#

set -e  # Sair em caso de erro

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Diretório raiz dos dados
DATA_ROOT="/media/marcelo/dados1/bigdata-docker"

# Diretório do projeto
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"

# Função para imprimir cabeçalhos
print_header() {
    echo ""
    echo -e "${CYAN}========================================================================${NC}"
    echo -e "${CYAN}  $1${NC}"
    echo -e "${CYAN}========================================================================${NC}"
    echo ""
}

# Função para imprimir mensagens de sucesso
print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

# Função para imprimir mensagens de erro
print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Função para imprimir mensagens de aviso
print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

# Função para imprimir mensagens informativas
print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

# Verificar se está executando no diretório correto
cd "$PROJECT_ROOT" || {
    print_error "Não foi possível acessar o diretório do projeto: $PROJECT_ROOT"
    exit 1
}

# Banner inicial
clear
echo ""
echo -e "${CYAN}════════════════════════════════════════════════════════════════════════${NC}"
echo -e "${CYAN}           RECRIAÇÃO COMPLETA DA STACK MINI BIGDATA                     ${NC}"
echo -e "${CYAN}════════════════════════════════════════════════════════════════════════${NC}"
echo ""
echo -e "${YELLOW}⚠️  ATENÇÃO: Este script irá:${NC}"
echo ""
echo "  1. ❌ Parar e remover TODOS os containers"
echo "  2. ❌ Remover TODOS os volumes Docker"
echo "  3. ❌ APAGAR todos os dados em: $DATA_ROOT"
echo "  4. ✅ Recriar a estrutura de diretórios"
echo "  5. ✅ Subir a stack completa novamente"
echo "  6. ✅ Validar os serviços"
echo ""
echo -e "${RED}⚠️  TODOS OS DADOS SERÃO PERDIDOS!${NC}"
echo ""
echo -e "${CYAN}════════════════════════════════════════════════════════════════════════${NC}"
echo ""

# Solicitar confirmação
read -p "Tem certeza que deseja continuar? (digite 'SIM' para confirmar): " confirmacao

if [ "$confirmacao" != "SIM" ]; then
    print_warning "Operação cancelada pelo usuário"
    exit 0
fi

echo ""
read -p "Última chance! Digite 'CONFIRMO' para prosseguir: " confirmacao_final

if [ "$confirmacao_final" != "CONFIRMO" ]; then
    print_warning "Operação cancelada pelo usuário"
    exit 0
fi

# ============================================================================
# ETAPA 1: Parar e remover containers
# ============================================================================
print_header "ETAPA 1/6: Parando e removendo containers"

# Verificar se Docker está rodando
if ! docker info > /dev/null 2>&1; then
    print_error "Docker não está rodando!"
    exit 1
fi

print_info "Parando todos os containers..."
docker compose down --remove-orphans -v 2>/dev/null || true
print_success "Containers parados e removidos"

print_info "Removendo containers órfãos..."
docker ps -a --filter "name=superset" --format "{{.ID}}" | xargs -r docker rm -f 2>/dev/null || true
docker ps -a --filter "name=airflow" --format "{{.ID}}" | xargs -r docker rm -f 2>/dev/null || true
docker ps -a --filter "name=spark" --format "{{.ID}}" | xargs -r docker rm -f 2>/dev/null || true
docker ps -a --filter "name=trino" --format "{{.ID}}" | xargs -r docker rm -f 2>/dev/null || true
docker ps -a --filter "name=hive" --format "{{.ID}}" | xargs -r docker rm -f 2>/dev/null || true
docker ps -a --filter "name=minio" --format "{{.ID}}" | xargs -r docker rm -f 2>/dev/null || true
docker ps -a --filter "name=postgres" --format "{{.ID}}" | xargs -r docker rm -f 2>/dev/null || true
docker ps -a --filter "name=redis" --format "{{.ID}}" | xargs -r docker rm -f 2>/dev/null || true
print_success "Containers órfãos removidos"

# ============================================================================
# ETAPA 2: Remover volumes Docker
# ============================================================================
print_header "ETAPA 2/6: Removendo volumes Docker"

print_info "Removendo volumes do projeto..."
docker volume ls --filter "name=mini-bigdata" --format "{{.Name}}" | xargs -r docker volume rm -f 2>/dev/null || true
print_success "Volumes Docker removidos"

print_info "Limpando volumes órfãos..."
docker volume prune -f > /dev/null 2>&1 || true
print_success "Volumes órfãos removidos"

# ============================================================================
# ETAPA 3: Apagar pasta de dados
# ============================================================================
print_header "ETAPA 3/6: Apagando pasta de dados"

if [ -d "$DATA_ROOT" ]; then
    print_warning "Removendo todo o conteúdo de: $DATA_ROOT"
    print_info "Aguarde, isso pode levar alguns segundos..."
    
    # Tentar remover sem sudo primeiro
    if rm -rf "$DATA_ROOT" 2>/dev/null; then
        print_success "Pasta de dados removida"
    else
        # Se falhar, tentar com sudo
        print_info "Necessário permissões de administrador para remover..."
        sudo rm -rf "$DATA_ROOT"
        print_success "Pasta de dados removida (com sudo)"
    fi
else
    print_info "Pasta de dados não existe (já foi removida)"
fi

# ============================================================================
# ETAPA 4: Recriar estrutura de diretórios
# ============================================================================
print_header "ETAPA 4/6: Recriando estrutura de diretórios"

print_info "Criando diretório raiz: $DATA_ROOT"
if mkdir -p "$DATA_ROOT" 2>/dev/null; then
    print_success "Diretório raiz criado"
else
    print_info "Criando com sudo..."
    sudo mkdir -p "$DATA_ROOT"
    sudo chown -R $USER:$USER "$DATA_ROOT"
    print_success "Diretório raiz criado (com sudo)"
fi

print_info "Criando subdiretórios..."
mkdir -p "$DATA_ROOT"/{postgres,minio,airflow/{dags,logs,plugins},hive,spark/{master,worker},trino,superset,redis}
print_success "Subdiretórios criados"

print_info "Configurando permissões..."
chmod -R 777 "$DATA_ROOT"
print_success "Permissões configuradas"

print_info "Ajustando permissões específicas do Airflow..."
if chown -R 50000:0 "$DATA_ROOT/airflow" 2>/dev/null; then
    print_success "Permissões do Airflow configuradas"
else
    sudo chown -R 50000:0 "$DATA_ROOT/airflow"
    print_success "Permissões do Airflow configuradas (com sudo)"
fi

# ============================================================================
# ETAPA 5: Subir a stack completa
# ============================================================================
print_header "ETAPA 5/6: Subindo a stack completa"

print_info "Verificando arquivo .env..."
if [ ! -f ".env" ]; then
    print_error "Arquivo .env não encontrado!"
    exit 1
fi
print_success "Arquivo .env encontrado"

print_info "Iniciando serviços com docker compose..."
docker compose up -d

print_success "Comando de inicialização executado"

print_info "Aguardando serviços inicializarem (30 segundos)..."
sleep 30

# ============================================================================
# ETAPA 6: Validar serviços
# ============================================================================
print_header "ETAPA 6/6: Validando serviços"

print_info "Verificando status dos containers..."
echo ""
docker compose ps
echo ""

# Verificar serviços críticos
services=("postgres" "redis" "minio" "hive-metastore" "spark-master" "spark-worker" "trino" "superset" "airflow-webserver" "airflow-scheduler")

failed_services=()

for service in "${services[@]}"; do
    if docker compose ps | grep -q "$service.*Up"; then
        print_success "Serviço $service está rodando"
    else
        print_error "Serviço $service NÃO está rodando"
        failed_services+=("$service")
    fi
done

echo ""

# Verificar logs de serviços com problema
if [ ${#failed_services[@]} -gt 0 ]; then
    print_warning "Alguns serviços falharam. Verificando logs..."
    echo ""
    for service in "${failed_services[@]}"; do
        print_info "Logs de $service:"
        docker compose logs --tail=20 "$service" 2>/dev/null || echo "Container não encontrado"
        echo ""
    done
fi

# ============================================================================
# RESUMO FINAL
# ============================================================================
print_header "RESUMO DA RECRIAÇÃO"

echo ""
echo -e "${CYAN}📊 Status dos Serviços:${NC}"
echo ""

# Tabela de serviços
printf "%-20s %-15s %-40s\n" "SERVIÇO" "STATUS" "URL"
echo "────────────────────────────────────────────────────────────────────────"

check_service() {
    local name=$1
    local url=$2
    if docker compose ps | grep -q "$name.*Up"; then
        printf "%-20s ${GREEN}%-15s${NC} %-40s\n" "$name" "✅ Rodando" "$url"
    else
        printf "%-20s ${RED}%-15s${NC} %-40s\n" "$name" "❌ Parado" "$url"
    fi
}

check_service "postgres" "localhost:5432"
check_service "redis" "localhost:6379"
check_service "minio" "http://localhost:9001"
check_service "hive-metastore" "localhost:9083"
check_service "spark-master" "http://localhost:8080"
check_service "spark-worker" "http://localhost:8081"
check_service "trino" "http://localhost:8085"
check_service "superset" "http://localhost:8088"
check_service "airflow-webserver" "http://localhost:8082"
check_service "airflow-scheduler" "-"

echo ""
echo -e "${CYAN}🔑 Credenciais de Acesso:${NC}"
echo ""
echo "  Airflow:  http://localhost:8082"
echo "    Usuário: airflow"
echo "    Senha: airflow"
echo ""
echo "  Superset: http://localhost:8088"
echo "    Usuário: admin"
echo "    Senha: admin"
echo ""
echo "  MinIO:    http://localhost:9001"
echo "    Usuário: minioadmin"
echo "    Senha: minioadmin123"
echo ""

if [ ${#failed_services[@]} -eq 0 ]; then
    print_success "STACK RECRIADA COM SUCESSO! 🎉"
    echo ""
    echo -e "${GREEN}Todos os serviços estão rodando corretamente!${NC}"
    exit_code=0
else
    print_warning "STACK RECRIADA COM AVISOS ⚠️"
    echo ""
    echo -e "${YELLOW}Os seguintes serviços apresentaram problemas:${NC}"
    for service in "${failed_services[@]}"; do
        echo "  - $service"
    done
    echo ""
    echo "Execute 'docker compose logs <serviço>' para mais detalhes"
    exit_code=1
fi

echo ""
echo -e "${CYAN}════════════════════════════════════════════════════════════════════════${NC}"
echo ""

exit $exit_code
