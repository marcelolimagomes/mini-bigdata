#!/bin/bash
set -e

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🚀 Apache Superset 5.0.0 - Inicialização"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Função para verificar se o serviço está disponível
wait_for_service() {
    local host=$1
    local port=$2
    local service=$3
    local max_attempts=30
    local attempt=1

    echo "⏳ Aguardando $service ($host:$port)..."
    
    while ! timeout 1 bash -c "cat < /dev/null > /dev/tcp/$host/$port" 2>/dev/null; do
        if [ $attempt -eq $max_attempts ]; then
            echo "❌ Timeout ao aguardar $service"
            exit 1
        fi
        echo "   Tentativa $attempt/$max_attempts..."
        sleep 2
        ((attempt++))
    done
    
    echo "✅ $service está disponível!"
}

# Aguarda dependências
wait_for_service "postgres" "5432" "PostgreSQL"
wait_for_service "redis" "6379" "Redis"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📦 Instalando drivers de banco de dados..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Verificar se há arquivo requirements customizado
if [ -f "/app/pythonpath/requirements.txt" ]; then
    echo "📋 Instalando dependências do requirements.txt..."
    pip install --no-cache-dir -r /app/pythonpath/requirements.txt
else
    echo "✅ Drivers já instalados na imagem Docker"
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🔄 Atualizando banco de dados (migrations)..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Fazer upgrade do banco
superset db upgrade

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "👤 Criando usuário administrador..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Criar usuário admin (ou atualizar se já existir)
superset fab create-admin \
    --username "${SUPERSET_ADMIN_USER:-admin}" \
    --firstname "Superset" \
    --lastname "Admin" \
    --email "${SUPERSET_ADMIN_EMAIL:-admin@example.com}" \
    --password "${SUPERSET_ADMIN_PASSWORD:-admin}" || {
        echo "⚠️  Usuário admin já existe, continuando..."
    }

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "⚙️  Inicializando Superset (roles, permissions)..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Inicializar (criar roles e permissions)
superset init

# Carregar exemplos apenas se solicitado
if [ "${SUPERSET_LOAD_EXAMPLES:-no}" = "yes" ]; then
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "📊 Carregando exemplos..."
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    superset load_examples
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ Configuração concluída!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "🌐 Acesse o Superset em: http://localhost:8088"
echo "👤 Usuário: ${SUPERSET_ADMIN_USER:-admin}"
echo "🔑 Senha: ${SUPERSET_ADMIN_PASSWORD:-admin}"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🚀 Iniciando servidor web..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Iniciar servidor
exec /usr/bin/run-server.sh

