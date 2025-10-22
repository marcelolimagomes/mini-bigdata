#!/bin/bash

# Script para verificar e preparar armazenamento
# Este script deve ser executado ANTES do setup.sh

set -e

# Cores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

DATA_ROOT="/media/marcelo/dados1/bigdata-docker"

echo ""
echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║   Verificação de Armazenamento - Mini Big Data Platform   ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Função para converter bytes em formato legível
human_readable() {
    local bytes=$1
    if [ $bytes -gt 1073741824 ]; then
        echo "$(echo "scale=2; $bytes/1073741824" | bc) GB"
    elif [ $bytes -gt 1048576 ]; then
        echo "$(echo "scale=2; $bytes/1048576" | bc) MB"
    else
        echo "$(echo "scale=2; $bytes/1024" | bc) KB"
    fi
}

# 1. Verificar se o diretório base existe
echo -e "${YELLOW}1. Verificando diretório base...${NC}"
BASE_DIR="/media/marcelo/dados1"

if [ ! -d "$BASE_DIR" ]; then
    echo -e "${RED}❌ Diretório $BASE_DIR não existe!${NC}"
    echo -e "${YELLOW}   Possíveis causas:${NC}"
    echo -e "   - Disco não montado"
    echo -e "   - Caminho incorreto"
    echo ""
    echo -e "${YELLOW}   Verifique com: ${GREEN}df -h${NC}"
    exit 1
else
    echo -e "${GREEN}✅ Diretório base existe: $BASE_DIR${NC}"
fi

# 2. Verificar espaço disponível
echo ""
echo -e "${YELLOW}2. Verificando espaço em disco...${NC}"

AVAILABLE_SPACE=$(df --output=avail "$BASE_DIR" | tail -n 1)
AVAILABLE_SPACE_KB=$((AVAILABLE_SPACE))
AVAILABLE_SPACE_HUMAN=$(human_readable $((AVAILABLE_SPACE_KB * 1024)))

REQUIRED_SPACE_GB=20
REQUIRED_SPACE_KB=$((REQUIRED_SPACE_GB * 1024 * 1024))

echo -e "   Espaço disponível: ${GREEN}${AVAILABLE_SPACE_HUMAN}${NC}"
echo -e "   Espaço recomendado: ${YELLOW}${REQUIRED_SPACE_GB} GB${NC}"

if [ $AVAILABLE_SPACE_KB -lt $REQUIRED_SPACE_KB ]; then
    echo -e "${RED}⚠️  ATENÇÃO: Espaço insuficiente!${NC}"
    echo -e "   Recomendamos pelo menos ${REQUIRED_SPACE_GB}GB livres"
    echo ""
    read -p "Deseja continuar mesmo assim? (s/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Ss]$ ]]; then
        echo -e "${RED}Instalação cancelada.${NC}"
        exit 1
    fi
else
    echo -e "${GREEN}✅ Espaço suficiente disponível${NC}"
fi

# 3. Verificar permissões de escrita
echo ""
echo -e "${YELLOW}3. Verificando permissões de escrita...${NC}"

TEST_FILE="$BASE_DIR/.bigdata_write_test"
if touch "$TEST_FILE" 2>/dev/null; then
    rm -f "$TEST_FILE"
    echo -e "${GREEN}✅ Permissões de escrita OK${NC}"
else
    echo -e "${RED}❌ Sem permissão de escrita em $BASE_DIR${NC}"
    echo ""
    echo -e "${YELLOW}   Execute:${NC}"
    echo -e "   ${GREEN}sudo chown -R \$USER:\$USER $BASE_DIR${NC}"
    exit 1
fi

# 4. Verificar se o diretório bigdata-docker já existe
echo ""
echo -e "${YELLOW}4. Verificando diretório de dados...${NC}"

if [ -d "$DATA_ROOT" ]; then
    echo -e "${YELLOW}⚠️  Diretório $DATA_ROOT já existe${NC}"
    
    CURRENT_SIZE=$(du -sb "$DATA_ROOT" 2>/dev/null | cut -f1)
    CURRENT_SIZE_HUMAN=$(human_readable $CURRENT_SIZE)
    
    echo -e "   Tamanho atual: ${BLUE}${CURRENT_SIZE_HUMAN}${NC}"
    echo ""
    echo -e "${YELLOW}   Opções:${NC}"
    echo -e "   1) Manter dados existentes (continuar)"
    echo -e "   2) Fazer backup e limpar"
    echo -e "   3) Cancelar"
    echo ""
    read -p "Escolha uma opção (1/2/3): " -n 1 -r
    echo
    
    case $REPLY in
        1)
            echo -e "${GREEN}✅ Mantendo dados existentes${NC}"
            ;;
        2)
            BACKUP_DIR="$BASE_DIR/bigdata-backup-$(date +%Y%m%d_%H%M%S)"
            echo -e "${YELLOW}   Criando backup em: $BACKUP_DIR${NC}"
            
            if cp -r "$DATA_ROOT" "$BACKUP_DIR"; then
                echo -e "${GREEN}✅ Backup criado com sucesso${NC}"
                echo -e "${YELLOW}   Removendo dados antigos...${NC}"
                rm -rf "$DATA_ROOT"
                echo -e "${GREEN}✅ Dados removidos${NC}"
            else
                echo -e "${RED}❌ Erro ao criar backup${NC}"
                exit 1
            fi
            ;;
        3)
            echo -e "${RED}Instalação cancelada.${NC}"
            exit 0
            ;;
        *)
            echo -e "${RED}Opção inválida. Instalação cancelada.${NC}"
            exit 1
            ;;
    esac
else
    echo -e "${GREEN}✅ Diretório não existe (será criado)${NC}"
fi

# 5. Criar estrutura de diretórios
echo ""
echo -e "${YELLOW}5. Criando estrutura de diretórios...${NC}"

DIRS=(
    "$DATA_ROOT"
    "$DATA_ROOT/postgres"
    "$DATA_ROOT/minio"
    "$DATA_ROOT/airflow/dags"
    "$DATA_ROOT/airflow/logs"
    "$DATA_ROOT/airflow/plugins"
    "$DATA_ROOT/hive"
    "$DATA_ROOT/spark/master"
    "$DATA_ROOT/spark/worker"
    "$DATA_ROOT/trino"
    "$DATA_ROOT/superset"
)

for dir in "${DIRS[@]}"; do
    if mkdir -p "$dir" 2>/dev/null; then
        echo -e "   ${GREEN}✅${NC} $dir"
    else
        echo -e "   ${RED}❌${NC} Erro ao criar $dir"
        exit 1
    fi
done

# 6. Configurar permissões
echo ""
echo -e "${YELLOW}6. Configurando permissões...${NC}"

# Permissões gerais
chmod -R 755 "$DATA_ROOT"
echo -e "   ${GREEN}✅${NC} Permissões gerais configuradas"

# Airflow precisa de UID específico
if sudo chown -R 50000:0 "$DATA_ROOT/airflow" 2>/dev/null; then
    echo -e "   ${GREEN}✅${NC} Permissões do Airflow configuradas (UID 50000)"
elif chown -R 50000:0 "$DATA_ROOT/airflow" 2>/dev/null; then
    echo -e "   ${GREEN}✅${NC} Permissões do Airflow configuradas (UID 50000)"
else
    echo -e "   ${YELLOW}⚠️${NC}  Não foi possível configurar permissões do Airflow"
    echo -e "   Execute manualmente: ${GREEN}sudo chown -R 50000:0 $DATA_ROOT/airflow${NC}"
fi

# 7. Verificação final
echo ""
echo -e "${YELLOW}7. Verificação final...${NC}"

TOTAL_DIRS=$(find "$DATA_ROOT" -type d | wc -l)
echo -e "   Total de diretórios criados: ${GREEN}$TOTAL_DIRS${NC}"

DISK_USAGE=$(du -sh "$DATA_ROOT" 2>/dev/null | cut -f1)
echo -e "   Espaço utilizado: ${BLUE}$DISK_USAGE${NC}"

# 8. Resumo
echo ""
echo -e "${GREEN}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║                    ✅ Verificação Concluída                ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${BLUE}📍 Localização dos dados:${NC}"
echo -e "   ${GREEN}$DATA_ROOT${NC}"
echo ""
echo -e "${BLUE}💾 Estrutura criada:${NC}"
echo -e "   ${GREEN}✅${NC} PostgreSQL:      $DATA_ROOT/postgres"
echo -e "   ${GREEN}✅${NC} MinIO:           $DATA_ROOT/minio"
echo -e "   ${GREEN}✅${NC} Airflow:         $DATA_ROOT/airflow"
echo -e "   ${GREEN}✅${NC} Hive:            $DATA_ROOT/hive"
echo -e "   ${GREEN}✅${NC} Spark:           $DATA_ROOT/spark"
echo -e "   ${GREEN}✅${NC} Trino:           $DATA_ROOT/trino"
echo -e "   ${GREEN}✅${NC} Superset:        $DATA_ROOT/superset"
echo ""
echo -e "${YELLOW}📋 Próximos passos:${NC}"
echo -e "   1. Execute: ${GREEN}./setup.sh${NC}"
echo -e "   2. Execute: ${GREEN}docker-compose up -d${NC}"
echo -e "   3. Acompanhe: ${GREEN}docker-compose logs -f${NC}"
echo ""
echo -e "${BLUE}📚 Documentação:${NC}"
echo -e "   - README.md           Documentação completa"
echo -e "   - QUICKSTART.md       Guia rápido"
echo -e "   - STORAGE.md          Detalhes de armazenamento"
echo -e "   - TROUBLESHOOTING.md  Solução de problemas"
echo ""
