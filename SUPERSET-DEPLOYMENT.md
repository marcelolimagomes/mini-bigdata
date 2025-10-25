# 🚀 Apache Superset 5.0.0 - Deployment Guide

## ✅ Configuração Completa Realizada

### Arquivos Criados/Modificados

1. **docker-compose.yml**
   - ✅ Adicionado serviço Redis
   - ✅ Configurado Superset Server com build customizado
   - ✅ Adicionado Celery Worker para async queries
   - ✅ Adicionado Celery Beat para agendamento
   - ✅ Health checks configurados
   - ✅ Volume para Redis

2. **config/superset/Dockerfile**
   - ✅ Base: Apache Superset 5.0.0
   - ✅ Drivers: PostgreSQL, Trino, MySQL, ClickHouse, BigQuery, Snowflake, Redshift, SQL Server
   - ✅ Redis e Celery instalados

3. **config/superset/superset_config.py**
   - ✅ Cache Redis configurado
   - ✅ Celery para processamento assíncrono
   - ✅ Feature flags otimizadas
   - ✅ Async queries habilitadas
   - ✅ SQL Lab configurado

4. **config/superset/init-superset.sh**
   - ✅ Wait for dependencies (PostgreSQL, Redis)
   - ✅ Instalação de drivers
   - ✅ Database migrations
   - ✅ Criação de admin user
   - ✅ Inicialização de roles/permissions
   - ✅ Logs melhorados

5. **config/superset/requirements.txt**
   - ✅ Lista completa de drivers
   - ✅ Redis e Celery
   - ✅ Utilitários (Excel, Parquet, etc.)

6. **.env**
   - ✅ Variáveis Redis adicionadas
   - ✅ SUPERSET_LOAD_EXAMPLES configurável

7. **Documentação**
   - ✅ docs/SUPERSET-v5-GUIA.md - Guia completo
   - ✅ config/superset/README.md - Quick reference
   - ✅ validate-superset.sh - Script de validação

---

## 🎯 Deploy em 3 Passos

### Passo 1: Preparar ambiente

```bash
# Criar diretórios de dados
sudo mkdir -p /media/marcelo/dados1/bigdata-docker/{superset,redis}
sudo chown -R $USER:$USER /media/marcelo/dados1/bigdata-docker/

# Navegar para o projeto
cd /home/marcelo/des/mini-bigdata
```

### Passo 2: Build e Start

```bash
# Build da imagem customizada do Superset
docker compose build superset

# Iniciar PostgreSQL (se ainda não estiver rodando)
docker compose up -d postgres

# Aguardar PostgreSQL ficar healthy (~10 segundos)
docker compose ps postgres

# Iniciar Superset e dependências
docker compose up -d redis superset superset-worker superset-beat
```

### Passo 3: Validar

```bash
# Executar script de validação
./validate-superset.sh

# OU verificar manualmente
docker compose logs -f superset

# Aguardar mensagem: "Iniciando servidor web..."
# Primeira inicialização pode levar 2-3 minutos
```

---

## 🌐 Acesso

### Interface Web

**URL**: http://localhost:8088

**Credenciais padrão:**
- Usuário: `admin`
- Senha: `admin`

### Primeira conexão recomendada: Trino

```
Database Type: Trino
Connection String: trino://trino@trino:8080/hive
```

---

## 🔍 Verificação Rápida

### Containers devem estar rodando:

```bash
docker compose ps

# Esperado:
# - postgres      (healthy)
# - redis         (healthy)
# - superset      (healthy)
# - superset-worker (running)
# - superset-beat (running)
```

### Health checks:

```bash
# Superset
curl http://localhost:8088/health
# Esperado: {"message":"OK"}

# Redis
docker exec superset-redis redis-cli ping
# Esperado: PONG

# PostgreSQL
docker exec postgres pg_isready -U admin
# Esperado: postgres:5432 - accepting connections
```

---

## 🎨 Features Disponíveis

### ✅ Habilitadas por padrão

- **Dashboard Native Filters** - Filtros nativos nos dashboards
- **Dashboard Cross Filters** - Filtros entre múltiplos charts
- **Global Async Queries** - Queries assíncronas via Celery
- **Template Processing** - Templates Jinja2 em SQL
- **Versioned Export** - Export/import versionado

### 🔌 Drivers Instalados

| Banco de Dados | Driver | Connection String Exemplo |
|----------------|--------|---------------------------|
| PostgreSQL | psycopg2-binary | `postgresql://user:pass@host:5432/db` |
| Trino | trino | `trino://user@host:8080/catalog` |
| MySQL | mysqlclient | `mysql://user:pass@host:3306/db` |
| ClickHouse | clickhouse-connect | `clickhouse+native://host:9000/db` |
| BigQuery | pybigquery | `bigquery://project-id` |
| Snowflake | snowflake-sqlalchemy | `snowflake://account/db` |
| Redshift | redshift-connector | `redshift+redshift_connector://host:5439/db` |
| SQL Server | pymssql | `mssql+pymssql://user:pass@host:1433/db` |

---

## 🔧 Comandos Úteis

### Logs

```bash
# Todos os logs do Superset
docker compose logs -f superset

# Logs do Worker
docker compose logs -f superset-worker

# Logs do Beat
docker compose logs -f superset-beat

# Últimas 100 linhas
docker compose logs --tail=100 superset
```

### Reiniciar

```bash
# Reiniciar apenas Superset
docker compose restart superset

# Reiniciar todo o stack do Superset
docker compose restart superset superset-worker superset-beat redis

# Rebuild após mudanças
docker compose build superset
docker compose up -d --force-recreate superset
```

### Shell

```bash
# Bash no Superset
docker exec -it superset bash

# Python shell
docker exec -it superset superset shell

# Redis CLI
docker exec -it superset-redis redis-cli
```

---

## 🐛 Troubleshooting Comum

### "Container constantly restarting"

```bash
# Ver logs do último crash
docker compose logs superset --tail=50

# Verificar se PostgreSQL está OK
docker compose ps postgres

# Verificar se Redis está OK
docker compose ps redis

# Forçar recreação
docker compose up -d --force-recreate superset
```

### "Cannot connect to database"

```bash
# Verificar se PostgreSQL aceita conexões
docker exec postgres pg_isready -U admin

# Verificar se banco 'superset' existe
docker exec postgres psql -U admin -lqt | grep superset

# Testar conexão do Superset
docker exec superset superset test-db
```

### "Queries very slow"

```bash
# Verificar se Redis está funcionando
docker exec superset-redis redis-cli INFO stats

# Limpar cache
docker exec superset-redis redis-cli FLUSHDB

# Habilitar cache nos datasets (UI)
```

### "Workers not processing tasks"

```bash
# Verificar status do worker
docker exec superset-worker celery -A superset.tasks.celery_app:app inspect active

# Verificar filas
docker exec superset-redis redis-cli LLEN celery

# Reiniciar worker
docker compose restart superset-worker
```

---

## 🔒 Checklist de Produção

Antes de ir para produção, verifique:

- [ ] **SECRET_KEY forte** - Gerar com `secrets.token_urlsafe(42)`
- [ ] **Senhas alteradas** - Admin, PostgreSQL, Redis
- [ ] **CSRF habilitado** - `WTF_CSRF_ENABLED = True`
- [ ] **HTTPS configurado** - Via nginx/traefik
- [ ] **Backup automático** - PostgreSQL e dashboards
- [ ] **Monitoramento** - Logs, métricas, alertas
- [ ] **Autenticação** - LDAP/OAuth configurado
- [ ] **Rate limiting** - Proteção contra abuso
- [ ] **Volumes externos** - Backup dos volumes Docker
- [ ] **Recursos ajustados** - CPU/Memory limits adequados

---

## 📚 Próximos Passos

1. **Explorar a interface**
   - Acessar http://localhost:8088
   - Login com admin/admin
   - Navegar pelo menu

2. **Conectar fontes de dados**
   - Data → Databases → + Database
   - Testar com Trino local
   - Testar com PostgreSQL

3. **Criar primeiro chart**
   - SQL Lab → New Query
   - Charts → Create Chart
   - Save to Dashboard

4. **Configurar alertas** (opcional)
   - Charts → Alert & Reports
   - Configure schedule
   - Configure notification

5. **Gerenciar usuários**
   - Settings → Users
   - Settings → Roles
   - Configure permissions

6. **Otimizar performance**
   - Habilitar cache em datasets
   - Usar async queries para queries longas
   - Configurar SQL Lab timeout

---

## 📖 Documentação Completa

- **Guia Detalhado**: `docs/SUPERSET-v5-GUIA.md`
- **Quick Reference**: `config/superset/README.md`
- **Validação**: `./validate-superset.sh`

### Links Úteis

- [Apache Superset Docs](https://superset.apache.org/docs/)
- [Superset 5.0 Release Notes](https://preset.io/blog/superset-5-0-0-release-notes/)
- [GitHub Repository](https://github.com/apache/superset)
- [Community Slack](https://superset.apache.org/community)

---

## ✅ Resumo da Configuração

```yaml
Componentes:
  ✅ Superset Server v5.0.0
  ✅ Redis (cache)
  ✅ Celery Worker (async)
  ✅ Celery Beat (scheduler)
  ✅ PostgreSQL (metadata)

Drivers:
  ✅ PostgreSQL, Trino, MySQL
  ✅ ClickHouse, BigQuery, Snowflake
  ✅ Redshift, SQL Server

Features:
  ✅ Async Queries
  ✅ Native Filters
  ✅ Cross Filters
  ✅ Template Processing
  ✅ Alerts & Reports

Segurança:
  ⚠️  CSRF desabilitado (dev)
  ⚠️  Senhas padrão (dev)
  ⚠️  HTTP não criptografado
  👉 Configure para produção!
```

---

**Status**: ✅ Pronto para uso  
**Ambiente**: Desenvolvimento/Teste  
**Próximo passo**: Executar `docker compose build superset && docker compose up -d`
