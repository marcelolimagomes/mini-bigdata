# 🎯 Apache Superset 5.0.0 - Configuração Completa

Configuração otimizada do Apache Superset v5 com suporte completo para produção.

## 🚀 Quick Start

### 1. Criar diretórios necessários

```bash
sudo mkdir -p /media/marcelo/dados1/bigdata-docker/{superset,redis}
sudo chown -R $USER:$USER /media/marcelo/dados1/bigdata-docker/
```

### 2. Build e iniciar

```bash
# Build da imagem customizada
docker compose build superset

# Iniciar serviços
docker compose up -d redis superset superset-worker superset-beat

# Acompanhar logs
docker compose logs -f superset
```

### 3. Acessar

🌐 **URL**: http://localhost:8088  
👤 **Usuário**: `admin`  
🔑 **Senha**: `admin`

## 📦 Componentes

### Serviços incluídos

| Serviço | Container | Porta | Descrição |
|---------|-----------|-------|-----------|
| **Superset Server** | `superset` | 8088 | Interface web + API REST |
| **Celery Worker** | `superset-worker` | - | Processamento assíncrono |
| **Celery Beat** | `superset-beat` | - | Agendador de tarefas |
| **Redis** | `redis` | 6379 | Cache e message broker |
| **PostgreSQL** | `postgres` | 5432 | Banco de metadados |

### Drivers de banco de dados

✅ **Incluídos por padrão:**
- PostgreSQL (`psycopg2-binary`)
- Trino / Presto (`trino`, `sqlalchemy-trino`)
- MySQL / MariaDB (`mysqlclient`)
- ClickHouse (`clickhouse-connect`)
- Google BigQuery (`pybigquery`)
- Snowflake (`snowflake-sqlalchemy`)
- Amazon Redshift (`redshift-connector`)
- Microsoft SQL Server (`pymssql`)

## ⚙️ Configuração

### Arquivos principais

```
config/superset/
├── Dockerfile              # Imagem customizada com drivers
├── superset_config.py      # Configuração principal
├── init-superset.sh        # Script de inicialização
└── requirements.txt        # Dependências Python
```

### Variáveis de ambiente (.env)

```env
# Admin
SUPERSET_ADMIN_USER=admin
SUPERSET_ADMIN_PASSWORD=admin
SUPERSET_ADMIN_EMAIL=admin@example.com

# Security
SUPERSET_SECRET_KEY=thisISaSECRET_1234

# Redis
REDIS_HOST=redis
REDIS_PORT=6379

# Exemplos
SUPERSET_LOAD_EXAMPLES=no
```

### Features habilitadas

```python
FEATURE_FLAGS = {
    "ENABLE_TEMPLATE_PROCESSING": True,      # Templates Jinja2
    "DASHBOARD_NATIVE_FILTERS": True,        # Filtros nativos
    "DASHBOARD_CROSS_FILTERS": True,         # Filtros cruzados
    "DASHBOARD_VIRTUALIZATION": True,        # Virtualização
    "GLOBAL_ASYNC_QUERIES": True,            # Queries assíncronas
    "VERSIONED_EXPORT": True,                # Export versionado
}
```

## 🔧 Uso Avançado

### Conectar ao Trino (stack local)

```python
# Connection String
trino://trino@trino:8080/hive

# SQL Lab
SELECT * FROM hive.default.tabela;
```

### Conectar ao PostgreSQL (metadados)

```python
# Connection String
postgresql://admin:admin123@postgres:5432/metastore
```

### Executar queries assíncronas

1. Habilite async queries na conexão do banco
2. Execute query longa no SQL Lab
3. O Celery Worker processa em background
4. Receba notificação quando concluir

### Criar alertas e relatórios

1. **Charts** → Configure chart
2. **Alerts & Reports** → New Alert
3. Configure schedule (Celery Beat executa)
4. Configure destino (email, Slack, etc.)

## 🛠️ Comandos Úteis

### Gerenciar containers

```bash
# Parar todos os serviços do Superset
docker compose stop superset superset-worker superset-beat redis

# Reiniciar apenas o Superset
docker compose restart superset

# Ver logs em tempo real
docker compose logs -f superset

# Ver logs do worker
docker compose logs -f superset-worker
```

### Acessar containers

```bash
# Shell do Superset
docker exec -it superset bash

# Shell do Redis
docker exec -it superset-redis redis-cli

# Shell do PostgreSQL
docker exec -it postgres psql -U admin -d superset
```

### Comandos Superset CLI

```bash
# Criar novo admin
docker exec -it superset superset fab create-admin

# Listar usuários
docker exec -it superset superset fab list-users

# Importar dashboard
docker exec -it superset superset import-dashboards \
  -p /path/to/dashboard.json

# Exportar dashboard
docker exec -it superset superset export-dashboards \
  -f dashboard.json

# Rodar migrations
docker exec -it superset superset db upgrade

# Resetar senha
docker exec -it superset superset fab reset-password \
  --username admin
```

### Verificar instalação

```bash
# Script automático de validação
./validate-superset.sh

# Verificar health manualmente
curl http://localhost:8088/health

# Verificar drivers instalados
docker exec superset pip list | grep -E "trino|psycopg2|mysql"

# Verificar Redis
docker exec superset-redis redis-cli ping

# Verificar Celery Worker
docker exec superset-worker celery -A superset.tasks.celery_app:app inspect stats
```

## 🔒 Segurança (Produção)

### ⚠️ Antes de ir para produção

```bash
# 1. Gerar SECRET_KEY forte
docker exec superset python -c "import secrets; print(secrets.token_urlsafe(42))"

# 2. Atualizar .env
SUPERSET_SECRET_KEY=<chave-gerada-acima>
SUPERSET_ADMIN_PASSWORD=<senha-forte>

# 3. Habilitar CSRF em superset_config.py
WTF_CSRF_ENABLED = True

# 4. Configurar HTTPS/SSL
# Use nginx ou traefik como reverse proxy

# 5. Configurar backup automático
# Ver seção Backup abaixo
```

### Autenticação LDAP (exemplo)

```python
# superset_config.py
from flask_appbuilder.security.manager import AUTH_LDAP

AUTH_TYPE = AUTH_LDAP
AUTH_LDAP_SERVER = "ldap://ldap.example.com"
AUTH_LDAP_BIND_USER = "cn=admin,dc=example,dc=com"
AUTH_LDAP_BIND_PASSWORD = "password"
AUTH_LDAP_SEARCH = "ou=users,dc=example,dc=com"
AUTH_USER_REGISTRATION = True
AUTH_USER_REGISTRATION_ROLE = "Gamma"
```

## 💾 Backup & Restore

### Backup do banco de metadados

```bash
# Exportar
docker exec postgres pg_dump -U admin superset \
  | gzip > superset_backup_$(date +%Y%m%d).sql.gz

# Restaurar
gunzip < superset_backup_20251025.sql.gz | \
  docker exec -i postgres psql -U admin superset
```

### Backup de dashboards

```bash
# Exportar todos os dashboards
docker exec superset superset export-dashboards \
  -f /app/superset_home/all_dashboards.json

# Copiar para host
docker cp superset:/app/superset_home/all_dashboards.json .

# Importar
docker cp all_dashboards.json superset:/app/superset_home/
docker exec superset superset import-dashboards \
  -p /app/superset_home/all_dashboards.json
```

## 🐛 Troubleshooting

### Superset não inicia

```bash
# 1. Verificar logs
docker compose logs superset | tail -50

# 2. Verificar se PostgreSQL está OK
docker compose ps postgres

# 3. Verificar migrations
docker exec superset superset db upgrade

# 4. Recriar container
docker compose up -d --force-recreate superset
```

### Queries lentas

```bash
# 1. Verificar cache Redis
docker exec superset-redis redis-cli INFO stats

# 2. Habilitar cache no dataset
# UI: Dataset → Edit → Cache timeout → 3600

# 3. Usar async queries
# UI: Database → Edit → Async query execution
```

### Erro de memória (OOM)

```bash
# 1. Verificar uso de memória
docker stats

# 2. Aumentar limite do container
# docker-compose.yml:
services:
  superset:
    mem_limit: 4g

# 3. Ajustar workers Celery
# Em superset_config.py:
CELERY_CONFIG.worker_max_tasks_per_child = 100
```

### Container reiniciando constantemente

```bash
# Ver últimos logs antes do crash
docker compose logs superset --tail=100

# Verificar health check
docker inspect superset | grep -A 20 Health

# Desabilitar temporariamente health check
# docker-compose.yml: comentar seção healthcheck
```

## 📊 Monitoramento

### Métricas do Celery

```bash
# Status dos workers
docker exec superset-worker celery -A superset.tasks.celery_app:app inspect active

# Tarefas agendadas
docker exec superset-beat celery -A superset.tasks.celery_app:app inspect scheduled

# Estatísticas
docker exec superset-worker celery -A superset.tasks.celery_app:app inspect stats
```

### Métricas do Redis

```bash
# Info geral
docker exec superset-redis redis-cli INFO

# Memória
docker exec superset-redis redis-cli INFO memory

# Estatísticas
docker exec superset-redis redis-cli INFO stats

# Chaves por padrão
docker exec superset-redis redis-cli --scan --pattern 'superset_*'
```

## 📚 Recursos

### Documentação
- [Apache Superset Docs](https://superset.apache.org/docs/)
- [Superset 5.0 Release Notes](https://preset.io/blog/superset-5-0-0-release-notes/)
- [Guia Completo](docs/SUPERSET-v5-GUIA.md)

### Exemplos
- [Conectar fontes de dados](https://superset.apache.org/docs/databases/installing-database-drivers)
- [Criar dashboards](https://superset.apache.org/docs/creating-charts-dashboards/creating-your-first-dashboard)
- [SQL Lab](https://superset.apache.org/docs/using-superset/exploring-data)

---

**Versão**: 5.0.0  
**Última atualização**: Outubro 2025  
**Autor**: Mini BigData Stack
