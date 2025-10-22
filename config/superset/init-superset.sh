#!/bin/bash
set -e

echo "🚀 Iniciando configuração do Superset..."

# Instalar driver PostgreSQL
echo "📦 Instalando psycopg2-binary..."
pip install psycopg2-binary

# Upgrade do banco de dados
echo "🔄 Atualizando banco de dados..."
superset db upgrade

# Criar usuário admin
echo "👤 Criando usuário administrador..."
superset fab create-admin \
    --username "${SUPERSET_ADMIN_USER}" \
    --firstname Superset \
    --lastname Admin \
    --email "${SUPERSET_ADMIN_EMAIL}" \
    --password "${SUPERSET_ADMIN_PASSWORD}" || echo "⚠️ Usuário pode já existir"

# Inicializar Superset
echo "⚙️ Inicializando Superset..."
superset init

echo "✅ Configuração concluída! Iniciando servidor..."

# Iniciar servidor
exec /usr/bin/run-server.sh
