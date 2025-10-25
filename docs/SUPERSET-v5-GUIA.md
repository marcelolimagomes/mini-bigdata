# Apache Superset 5.0.0 - Guia Completo

## 📋 Índice

- [Visão Geral](#visão-geral)
- [Arquitetura](#arquitetura)
- [Pré-requisitos](#pré-requisitos)
- [Instalação](#instalação)
- [Configuração](#configuração)
- [Uso](#uso)
- [Troubleshooting](#troubleshooting)
- [Produção](#produção)

---

## 🎯 Visão Geral

Esta configuração do Apache Superset 5.0.0 inclui:

- ✅ **Superset Server** - Interface web e API
- ✅ **Redis** - Cache de alta performance
- ✅ **Celery Worker** - Processamento assíncrono de queries
- ✅ **Celery Beat** - Agendador de tarefas (alertas/relatórios)
- ✅ **PostgreSQL** - Banco de metadados
- ✅ **Múltiplos drivers** - Suporte para 10+ bancos de dados

---

## 🏗️ Arquitetura

```
┌─────────────────────────────────────────────────────────┐
│                    Apache Superset                      │
│                                                           │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │   Superset   │  │   Celery     │  │   Celery     │  │
│  │   Server     │  │   Worker     │  │   Beat       │  │
│  │  (Web + API) │  │  (Async)     │  │  (Schedule)  │  │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘  │
│         │                 │                  │           │
│         └─────────────────┴──────────────────┘           │
│                           │                              │
└───────────────────────────┼──────────────────────────────┘
                            │
          ┌─────────────────┼─────────────────┐
          │                 │                 │
    ┌─────▼─────┐    ┌─────▼─────┐    ┌─────▼─────┐
    │PostgreSQL │    │   Redis   │    │   Data    │
    │ (Metadata)│    │  (Cache)  │    │  Sources  │
    └───────────┘    └───────────┘    └───────────┘
```

---

## 📦 Pré-requisitos

### Sistema
- Docker 24.0+
- Docker Compose 2.20+
- Mínimo 8 GB RAM
- 10 GB espaço em disco

### Diretórios
Certifique-se de criar os diretórios necessários:

```bash
sudo mkdir -p /media/marcelo/dados1/bigdata-docker/{superset,redis}
sudo chown -R $USER:$USER /media/marcelo/dados1/bigdata-docker/
```

---

## 🚀 Instalação

### 1. Build da imagem customizada

```bash
cd /home/marcelo/des/mini-bigdata
docker compose build superset
```

Isso irá:
- Baixar a imagem base `apache/superset:5.0.0`
- Instalar drivers de banco (PostgreSQL, Trino, MySQL, etc.)
- Instalar Redis e Celery

### 2. Iniciar os serviços

```bash
# Iniciar todos os serviços do Superset
docker compose up -d redis superset superset-worker superset-beat

# Verificar logs
docker compose logs -f superset
```

### 3. Aguardar inicialização

O primeiro start pode levar 2-3 minutos:
- Migrations do banco de dados
- Criação do usuário admin
- Inicialização de roles e permissions

---

## ⚙️ Configuração

### Variáveis de Ambiente (.env)

```env
# Superset
SUPERSET_SECRET_KEY=thisISaSECRET_1234
SUPERSET_ADMIN_USER=admin
SUPERSET_ADMIN_PASSWORD=admin
SUPERSET_ADMIN_EMAIL=admin@example.com
SUPERSET_LOAD_EXAMPLES=no

# Redis
REDIS_HOST=redis
REDIS_PORT=6379
```

### Arquivo de configuração (superset_config.py)

Localização: `config/superset/superset_config.py`

**Principais configurações:**

```python
# Cache com Redis
CACHE_CONFIG = {
    'CACHE_TYPE': 'RedisCache',
    'CACHE_REDIS_HOST': 'redis',
    'CACHE_REDIS_PORT': 6379,
}

# Celery para async queries
CELERY_CONFIG = CeleryConfig

# Feature flags
FEATURE_FLAGS = {
    "GLOBAL_ASYNC_QUERIES": True,
    "DASHBOARD_NATIVE_FILTERS": True,
}
```

---

## 🎮 Uso

### Acessar a interface

1. Abra o navegador: http://localhost:8088
2. Login:
   - **Usuário**: `admin`
   - **Senha**: `admin`

### Conectar fontes de dados

#### Trino (já configurado na stack)

1. **Data** → **Databases** → **+ Database**
2. Selecione: **Trino**
3. Connection string:
   ```
   trino://trino@trino:8080/hive
   ```

#### PostgreSQL (metadados da stack)

```
postgresql://admin:admin123@postgres:5432/metastore
```

#### MinIO (via Trino Hive)

Já está acessível via Trino:
```sql
SELECT * FROM hive.default.sua_tabela;
```

### Criar um Dashboard

1. **SQL Lab** → Execute query
2. **Explore** → Criar visualização
3. **Dashboards** → Adicionar ao dashboard

---

## 🔧 Troubleshooting

### Container não inicia

```bash
# Verificar logs
docker compose logs superset

# Verificar se PostgreSQL está saudável
docker compose ps postgres

# Verificar se Redis está rodando
docker compose ps redis
```

### Problemas de conexão com banco

```bash
# Testar conexão manual
docker exec -it superset superset test-db

# Verificar se o driver está instalado
docker exec -it superset pip list | grep trino
```

### Queries lentas

1. Verifique se o Redis está funcionando:
   ```bash
   docker exec -it superset-redis redis-cli ping
   ```

2. Habilite cache nas queries (SQL Lab)

3. Use o Celery Worker para queries assíncronas

### Erro "OOM" ou "Exit 137"

Aumente a memória do Docker:
- Docker Desktop: Settings → Resources → Memory (min 8GB)
- Linux: verifique memória disponível com `free -h`

---

## 🏭 Produção

### Checklist de segurança

- [ ] Altere `SUPERSET_SECRET_KEY` para um valor seguro
- [ ] Altere senhas padrão (`SUPERSET_ADMIN_PASSWORD`)
- [ ] Habilite CSRF: `WTF_CSRF_ENABLED = True`
- [ ] Configure HTTPS/SSL
- [ ] Configure backup do PostgreSQL
- [ ] Configure autenticação (LDAP/OAuth)
- [ ] Habilite rate limiting
- [ ] Configure monitoramento (Prometheus/Grafana)

### Gerar SECRET_KEY segura

```python
import secrets
print(secrets.token_urlsafe(32))
```

### Backup do banco de metadados

```bash
# Exportar
docker exec postgres pg_dump -U admin superset > superset_backup.sql

# Restaurar
docker exec -i postgres psql -U admin superset < superset_backup.sql
```

### Escalar Workers

Edite `docker-compose.yml`:

```yaml
superset-worker:
  # ...
  deploy:
    replicas: 3  # Múltiplos workers
```

### Configurar SSL/HTTPS

Use um reverse proxy (nginx/traefik):

```nginx
server {
    listen 443 ssl;
    server_name superset.exemplo.com;
    
    ssl_certificate /etc/ssl/certs/superset.crt;
    ssl_certificate_key /etc/ssl/private/superset.key;
    
    location / {
        proxy_pass http://localhost:8088;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

---

## 📚 Recursos Adicionais

### Documentação oficial
- [Apache Superset Documentation](https://superset.apache.org/docs/)
- [Superset 5.0 Release Notes](https://preset.io/blog/superset-5-0-0-release-notes/)

### Drivers suportados

Esta configuração inclui drivers para:
- ✅ PostgreSQL
- ✅ Trino / Presto
- ✅ MySQL / MariaDB
- ✅ ClickHouse
- ✅ Google BigQuery
- ✅ Snowflake
- ✅ Amazon Redshift
- ✅ Microsoft SQL Server

### Comandos úteis

```bash
# Rebuild após alterações
docker compose build superset
docker compose up -d superset

# Reiniciar serviços
docker compose restart superset superset-worker superset-beat

# Ver logs em tempo real
docker compose logs -f superset

# Acessar shell do container
docker exec -it superset bash

# Executar comandos Superset
docker exec -it superset superset --help

# Criar novo usuário admin
docker exec -it superset superset fab create-admin

# Importar dashboard
docker exec -it superset superset import-dashboards -p /path/to/dashboard.json
```

---

## 🎯 Próximos Passos

1. ✅ Configuração completa do Superset v5
2. 📊 Criar conexões com suas fontes de dados
3. 📈 Desenvolver dashboards e visualizações
4. 🔔 Configurar alertas e relatórios agendados
5. 👥 Gerenciar usuários e permissões
6. 🚀 Otimizar performance com cache

---

## 🆘 Suporte

Em caso de problemas:

1. Verifique os logs: `docker compose logs superset`
2. Consulte [TROUBLESHOOTING.md](../TROUBLESHOOTING.md)
3. Documentação oficial: https://superset.apache.org
4. GitHub Issues: https://github.com/apache/superset/issues

---

**Última atualização**: Outubro 2025  
**Versão do Superset**: 5.0.0  
**Versão do Docker Compose**: 3.8
