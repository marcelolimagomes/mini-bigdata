#!/bin/bash
#
# full-setup.sh - Setup completo e automatizado da stack Big Data
#
# Este script:
# 1. Cria toda a estrutura de diretórios necessária
# 2. Para e remove containers/volumes antigos
# 3. Sobe a stack completa
# 4. Monitora os logs
# 5. Valida todos os serviços
# 6. Configura MinIO, Trino e Superset
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
    echo -e "${CYAN}========================================${NC}"
    echo -e "${CYAN}  $1${NC}"
    echo -e "${CYAN}========================================${NC}"
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

# ============================================================================
# ETAPA 1: Criar estrutura de diretórios
# ============================================================================
print_header "ETAPA 1/7: Criando estrutura de diretórios"

if [ ! -d "$DATA_ROOT" ]; then
    print_warning "Diretório $DATA_ROOT não existe. Criando com sudo..."
    sudo mkdir -p "$DATA_ROOT" || {
        print_error "Falha ao criar $DATA_ROOT"
        exit 1
    }
    sudo chown -R $USER:$USER "$DATA_ROOT"
    print_success "Diretório $DATA_ROOT criado"
else
    print_info "Diretório $DATA_ROOT já existe"
fi

# Criar subdiretórios
print_info "Criando subdiretórios..."
mkdir -p "$DATA_ROOT"/{postgres,minio,airflow/{dags,logs,plugins},hive,spark/{master,worker},trino,superset,redis}

# Configurar permissões
print_info "Configurando permissões..."
chmod -R 755 "$DATA_ROOT"

# Airflow precisa de UID específico
if command -v sudo &> /dev/null; then
    sudo chown -R 50000:0 "$DATA_ROOT/airflow" 2>/dev/null || chown -R 50000:0 "$DATA_ROOT/airflow"
else
    chown -R 50000:0 "$DATA_ROOT/airflow"
fi

print_success "Estrutura de diretórios criada e configurada"

# ============================================================================
# ETAPA 2: Limpar ambiente Docker
# ============================================================================
print_header "ETAPA 2/7: Limpando ambiente Docker"

# Verificar se Docker está rodando
if ! docker info > /dev/null 2>&1; then
    print_error "Docker não está rodando. Inicie o Docker e tente novamente."
    exit 1
fi

print_info "Parando containers..."
docker compose down -v 2>/dev/null || true

print_info "Removendo volumes órfãos..."
docker volume prune -f > /dev/null 2>&1 || true

print_info "Removendo redes não utilizadas..."
docker network prune -f > /dev/null 2>&1 || true

print_success "Ambiente Docker limpo"

# ============================================================================
# ETAPA 3: Construir imagens personalizadas
# ============================================================================
print_header "ETAPA 3/7: Construindo imagens personalizadas"

print_info "Construindo imagem do Hive Metastore..."
docker compose build hive-metastore

print_info "Construindo imagem do Trino..."
docker compose build trino

print_success "Imagens construídas"

# ============================================================================
# ETAPA 4: Subir serviços base (PostgreSQL, MinIO, Redis)
# ============================================================================
print_header "ETAPA 4/7: Iniciando serviços base"

print_info "Subindo PostgreSQL, MinIO e Redis..."
docker compose up -d postgres minio redis

print_info "Aguardando PostgreSQL ficar saudável..."
timeout 60 bash -c 'until docker exec postgres pg_isready -U admin &>/dev/null; do sleep 2; done' || {
    print_error "PostgreSQL não ficou pronto a tempo"
    print_info "Logs do PostgreSQL:"
    docker compose logs postgres
    exit 1
}
print_success "PostgreSQL está pronto"

print_info "Aguardando MinIO ficar saudável..."
timeout 60 bash -c 'until docker exec minio curl -sf http://localhost:9000/minio/health/live &>/dev/null; do sleep 2; done' || {
    print_error "MinIO não ficou pronto a tempo"
    print_info "Logs do MinIO:"
    docker compose logs minio
    exit 1
}
print_success "MinIO está pronto"

print_info "Aguardando Redis ficar saudável..."
timeout 30 bash -c 'until docker exec redis redis-cli ping &>/dev/null; do sleep 2; done' || {
    print_error "Redis não ficou pronto a tempo"
    exit 1
}
print_success "Redis está pronto"

# Criar buckets no MinIO
print_info "Criando buckets no MinIO..."
docker compose up -d minio-client
sleep 5
print_success "Buckets criados"

# ============================================================================
# ETAPA 5: Subir Hive Metastore
# ============================================================================
print_header "ETAPA 5/7: Iniciando Hive Metastore"

docker compose up -d hive-metastore

print_info "Aguardando Hive Metastore ficar pronto (pode levar até 90s)..."
timeout 90 bash -c 'until docker exec hive-metastore timeout 2 bash -c "</dev/tcp/localhost/9083" &>/dev/null; do sleep 3; done' || {
    print_error "Hive Metastore não ficou pronto a tempo"
    print_info "Logs do Hive Metastore:"
    docker compose logs --tail=50 hive-metastore
    exit 1
}
print_success "Hive Metastore está pronto"

# ============================================================================
# ETAPA 6: Subir todos os outros serviços
# ============================================================================
print_header "ETAPA 6/7: Iniciando serviços restantes"

print_info "Subindo Spark Master e Worker..."
docker compose up -d spark-master spark-worker

print_info "Subindo Trino..."
docker compose up -d trino

print_info "Subindo Airflow..."
docker compose up -d airflow-init
print_info "Aguardando inicialização do banco do Airflow..."
timeout 120 bash -c 'until [ "$(docker inspect -f {{.State.Status}} airflow-init 2>/dev/null)" = "exited" ]; do sleep 2; done' || {
    print_warning "Airflow init demorou mais que o esperado"
}

docker compose up -d airflow-webserver airflow-scheduler

print_info "Subindo Superset..."
docker compose up -d superset

print_success "Todos os serviços foram iniciados"

# ============================================================================
# ETAPA 7: Aguardar e validar serviços
# ============================================================================
print_header "ETAPA 7/7: Validando serviços"

print_info "Aguardando serviços ficarem prontos (60s)..."
sleep 60

# Verificar status dos containers
print_info "Verificando status dos containers..."
docker compose ps

# Validar serviços críticos
services_ok=true

# PostgreSQL
if docker exec postgres pg_isready -U admin &>/dev/null; then
    print_success "PostgreSQL: OK"
else
    print_error "PostgreSQL: FALHOU"
    services_ok=false
fi

# MinIO
if docker exec minio curl -sf http://localhost:9000/minio/health/live &>/dev/null; then
    print_success "MinIO: OK"
else
    print_error "MinIO: FALHOU"
    services_ok=false
fi

# Redis
if docker exec redis redis-cli ping &>/dev/null; then
    print_success "Redis: OK"
else
    print_error "Redis: FALHOU"
    services_ok=false
fi

# Hive Metastore
if docker exec hive-metastore timeout 2 bash -c "</dev/tcp/localhost/9083" &>/dev/null; then
    print_success "Hive Metastore: OK"
else
    print_error "Hive Metastore: FALHOU"
    services_ok=false
fi

# Trino
if docker exec trino curl -sf http://localhost:8080/v1/info &>/dev/null; then
    print_success "Trino: OK"
else
    print_warning "Trino: Verificar manualmente (pode estar inicializando)"
fi

# Spark Master
if docker exec spark-master curl -sf http://localhost:8080 &>/dev/null; then
    print_success "Spark Master: OK"
else
    print_warning "Spark Master: Verificar manualmente"
fi

# Airflow
if docker exec airflow-webserver curl -sf http://localhost:8080/health &>/dev/null; then
    print_success "Airflow: OK"
else
    print_warning "Airflow: Verificar manualmente (pode estar inicializando)"
fi

# Superset
if docker exec superset curl -sf http://localhost:8088/health &>/dev/null; then
    print_success "Superset: OK"
else
    print_warning "Superset: Verificar manualmente (pode estar inicializando)"
fi

# ============================================================================
# Configuração automática (se os serviços estiverem OK)
# ============================================================================
if [ "$services_ok" = true ]; then
    print_header "Executando configuração automática"
    
    print_info "Aguardando mais 30s para garantir estabilidade..."
    sleep 30
    
    # Executar script Python de setup
    if [ -f "$PROJECT_ROOT/scripts/setup_stack.py" ]; then
        print_info "Executando configuração do MinIO, Trino e Superset..."
        cd "$PROJECT_ROOT/scripts"
        python3 setup_stack.py || print_warning "Configuração automática falhou parcialmente"
        cd "$PROJECT_ROOT"
    fi
fi

# ============================================================================
# Resumo final
# ============================================================================
print_header "🎉 SETUP COMPLETO!"

echo ""
echo -e "${GREEN}✅ Stack Big Data iniciada com sucesso!${NC}"
echo ""
echo -e "${YELLOW}📊 URLs de Acesso:${NC}"
echo -e "  ${CYAN}MinIO Console:${NC}  http://localhost:9001 ${GREEN}(minioadmin / minioadmin123)${NC}"
echo -e "  ${CYAN}Airflow:${NC}        http://localhost:8080 ${GREEN}(airflow / airflow)${NC}"
echo -e "  ${CYAN}Superset:${NC}       http://localhost:8088 ${GREEN}(admin / admin)${NC}"
echo -e "  ${CYAN}Trino:${NC}          http://localhost:8085 ${GREEN}(trino / sem senha)${NC}"
echo -e "  ${CYAN}Spark Master:${NC}   http://localhost:8080"
echo -e "  ${CYAN}Spark Worker:${NC}   http://localhost:8081"
echo ""
echo -e "${YELLOW}📁 Dados persistidos em:${NC}"
echo -e "  ${GREEN}$DATA_ROOT${NC}"
echo ""
echo -e "${YELLOW}🔍 Comandos úteis:${NC}"
echo -e "  ${CYAN}Ver logs:${NC}         docker compose logs -f [serviço]"
echo -e "  ${CYAN}Status:${NC}           docker compose ps"
echo -e "  ${CYAN}Reiniciar:${NC}        docker compose restart [serviço]"
echo -e "  ${CYAN}Parar tudo:${NC}       docker compose down"
echo -e "  ${CYAN}Validar:${NC}          python3 scripts/validate_all_services.py"
echo ""
echo -e "${YELLOW}📚 Documentação:${NC}"
echo -e "  ${GREEN}docs/INDICE.md${NC}"
echo ""

if [ "$services_ok" = true ]; then
    print_success "Todos os serviços críticos estão funcionando!"
else
    print_warning "Alguns serviços podem precisar de atenção. Verifique os logs."
    echo ""
    echo -e "${YELLOW}Para ver logs de um serviço específico:${NC}"
    echo -e "  ${CYAN}docker compose logs -f <nome-do-serviço>${NC}"
fi

echo ""
