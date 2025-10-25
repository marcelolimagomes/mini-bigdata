# 🏗️ Apache Superset 5.0.0 - Arquitetura

## 📊 Visão Geral da Stack

```
┌─────────────────────────────────────────────────────────────────────┐
│                        MINI BIGDATA STACK                           │
│                     Apache Superset v5.0.0                          │
└─────────────────────────────────────────────────────────────────────┘

                              ┌─────────────┐
                              │   Cliente   │
                              │  (Browser)  │
                              └──────┬──────┘
                                     │ HTTP
                                     │ :8088
                                     ▼
        ┌─────────────────────────────────────────────────┐
        │          SUPERSET SERVER                        │
        │  ┌──────────────────────────────────────────┐   │
        │  │   Web UI + REST API                      │   │
        │  │   Flask + React                          │   │
        │  └──────────────────────────────────────────┘   │
        └──────────┬──────────────┬──────────────┬────────┘
                   │              │              │
        ┌──────────▼─────┐ ┌─────▼──────┐ ┌────▼────────┐
        │  PostgreSQL    │ │   Redis    │ │  Celery     │
        │  (Metadata)    │ │  (Cache)   │ │  Queue      │
        │  :5432         │ │  :6379     │ │             │
        └────────────────┘ └────────────┘ └──────┬──────┘
                                                  │
                     ┌────────────────────────────┴──────────┐
                     │                                       │
           ┌─────────▼─────────┐              ┌─────────────▼────────┐
           │  CELERY WORKER    │              │   CELERY BEAT        │
           │  (Async Queries)  │              │   (Scheduler)        │
           │  ┌──────────────┐ │              │   ┌──────────────┐  │
           │  │ Task 1       │ │              │   │ Alerts       │  │
           │  │ Task 2       │ │              │   │ Reports      │  │
           │  │ Task 3       │ │              │   │ Cleanup      │  │
           │  └──────────────┘ │              │   └──────────────┘  │
           └───────────────────┘              └─────────────────────┘
                     │
                     │ Query
                     ▼
        ┌─────────────────────────────────────────────┐
        │         DATA SOURCES                        │
        │  ┌────────┐  ┌────────┐  ┌────────┐        │
        │  │ Trino  │  │ MySQL  │  │  ...   │        │
        │  │ :8080  │  │ :3306  │  │        │        │
        │  └────────┘  └────────┘  └────────┘        │
        └─────────────────────────────────────────────┘
```

---

## 🔄 Fluxo de Dados

### 1. Dashboard Rendering (Síncrono)

```
User Request
    │
    ▼
Superset Server
    │
    ├─► Redis Cache ──┐
    │                 │ Cache Hit?
    │                 └──► Return Cached Data
    │
    ├─► PostgreSQL (metadata)
    │
    └─► Data Source
        └─► Return Data
            └─► Cache in Redis
                └─► Render Dashboard
```

### 2. Async Query Execution

```
User Submits Query
    │
    ▼
Superset Server
    │
    └─► Enqueue Task
        └─► Celery Queue (Redis)
            │
            ▼
        Celery Worker
            │
            ├─► Execute Query
            │   └─► Data Source
            │
            ├─► Store Result
            │   └─► Redis/PostgreSQL
            │
            └─► Notify User
                └─► WebSocket/Polling
```

### 3. Alert & Report Generation

```
Celery Beat (Cron-like)
    │
    ├─► Every Minute
    ├─► Every Hour
    └─► Daily @ 9am
        │
        ▼
    Enqueue Report Task
        └─► Celery Queue
            │
            ▼
        Celery Worker
            │
            ├─► Render Dashboard
            ├─► Generate PDF/PNG
            ├─► Check Conditions
            └─► Send Notification
                ├─► Email
                ├─► Slack
                └─► Webhook
```

---

## 🗄️ Storage & Persistence

### Volumes Mapeados

```
Host                                    Container
─────────────────────────────────────── ─────────────────────
/media/marcelo/dados1/bigdata-docker/
├── postgres/                         → /var/lib/postgresql/data
│   └── superset (database)
├── superset/                         → /app/superset_home
│   ├── dashboards/
│   ├── uploads/
│   └── logs/
└── redis/                            → /data
    └── dump.rdb
```

### Dados no PostgreSQL

```sql
-- Databases
- airflow     (Airflow metadata)
- superset    (Superset metadata) ← USADO
- metastore   (Hive metadata)

-- Tables em 'superset'
├── dashboards           (Dashboards)
├── slices              (Charts/Visualizações)
├── tables              (Datasets)
├── databases           (Conexões)
├── ab_user             (Usuários)
├── ab_role             (Roles)
├── ab_permission       (Permissões)
├── query               (Query history)
├── logs                (Audit logs)
└── ... (50+ tabelas)
```

### Cache no Redis

```
Redis DBs:
├── DB 0: Celery Broker (filas de tarefas)
├── DB 1: Celery Results (resultados de tarefas)
└── DB 2: Superset Cache (cache de queries)

Patterns:
├── superset_*          (Cache geral)
├── superset_data_*     (Cache de dados)
├── celery-task-*       (Tasks Celery)
└── _kombu.*            (Filas Celery)
```

---

## 🔌 Conexões de Rede

### Portas Expostas

| Serviço | Container Port | Host Port | Protocolo |
|---------|---------------|-----------|-----------|
| Superset Web | 8088 | 8088 | HTTP |
| Redis | 6379 | 6379 | TCP |
| PostgreSQL | 5432 | 5432 | TCP |

### Rede Interna (bigdata-network)

```
Containers podem se comunicar usando nomes:

superset        → postgres:5432
superset        → redis:6379
superset        → trino:8080
superset-worker → postgres:5432
superset-worker → redis:6379
superset-worker → trino:8080
superset-beat   → postgres:5432
superset-beat   → redis:6379
```

---

## 🔐 Security Layers

### 1. Network Security

```
┌─────────────────────────────────┐
│       Host Network              │
│  (Acessível via localhost)      │
└──────────────┬──────────────────┘
               │
        ┌──────▼──────┐
        │  Port 8088  │ ← Único ponto de entrada
        └──────┬──────┘
               │
┌──────────────▼──────────────────┐
│   bigdata-network (bridge)      │
│   ┌──────┐  ┌──────┐  ┌──────┐ │
│   │Redis │  │PG SQL│  │Trino │ │
│   └──────┘  └──────┘  └──────┘ │
│   (Isolado do host)             │
└─────────────────────────────────┘
```

### 2. Application Security

```
Request
  │
  ▼
HTTPS (Nginx/Traefik) ← Adicione em produção
  │
  ▼
Flask Security
  ├─► CSRF Token
  ├─► Session Management
  ├─► XSS Protection
  └─► SQL Injection Prevention
  │
  ▼
Authentication
  ├─► Username/Password
  ├─► LDAP (opcional)
  ├─► OAuth (opcional)
  └─► SAML (opcional)
  │
  ▼
Authorization (RBAC)
  ├─► Admin (full access)
  ├─► Alpha (create dashboards)
  ├─► Gamma (view only)
  └─► Custom roles
  │
  ▼
Row Level Security
  └─► Filter data by user
```

### 3. Data Security

```
Data Sources
  │
  ▼
Connection Credentials
  ├─► Encrypted in PostgreSQL
  └─► Secret KEY from env
  │
  ▼
Query Execution
  ├─► SQL Validation
  ├─► Timeout Limits
  └─► Query Cost Estimation
  │
  ▼
Results
  ├─► Cache (encrypted)
  └─► Export (permission check)
```

---

## 📈 Scalability

### Horizontal Scaling

```
Load Balancer (nginx/traefik)
    │
    ├─► Superset Instance 1
    ├─► Superset Instance 2
    └─► Superset Instance 3
            │
            └─► Shared State
                ├─► PostgreSQL (metadata)
                ├─► Redis (cache/sessions)
                └─► Celery Queue

Celery Workers (auto-scale)
    ├─► Worker 1 (2 cores)
    ├─► Worker 2 (2 cores)
    ├─► Worker 3 (2 cores)
    └─► Worker N...
```

### Resource Requirements

```
Minimal (Dev/Test):
├── Superset Server:  1 core,  2 GB RAM
├── Celery Worker:    1 core,  2 GB RAM
├── Redis:            0.5 core, 512 MB RAM
└── PostgreSQL:       Shared with other services
    Total:            ~2.5 cores, ~5 GB RAM

Production (Small):
├── Superset Server:  2 cores,  4 GB RAM (2 replicas)
├── Celery Worker:    2 cores,  4 GB RAM (3 replicas)
├── Celery Beat:      0.5 core, 512 MB RAM
├── Redis:            1 core,   2 GB RAM
└── PostgreSQL:       2 cores,  4 GB RAM
    Total:            ~14 cores, ~30 GB RAM

Production (Large):
├── Superset Server:  4 cores,  8 GB RAM (5+ replicas)
├── Celery Worker:    4 cores,  8 GB RAM (10+ replicas)
├── Celery Beat:      1 core,   1 GB RAM
├── Redis Cluster:    3 nodes × (2 cores, 4 GB)
└── PostgreSQL HA:    3 nodes × (4 cores, 8 GB)
    Total:            ~80+ cores, ~150+ GB RAM
```

---

## 🔄 High Availability Setup

```
┌──────────────────────────────────────────────────────┐
│              LOAD BALANCER (HAProxy)                 │
│                    VIP: 10.0.0.100                   │
└───────────┬──────────────┬──────────────┬────────────┘
            │              │              │
    ┌───────▼──────┐ ┌────▼──────┐ ┌────▼──────┐
    │ Superset 1   │ │Superset 2 │ │Superset 3 │
    │ 10.0.0.11    │ │10.0.0.12  │ │10.0.0.13  │
    └───────┬──────┘ └────┬──────┘ └────┬──────┘
            │              │              │
            └──────────────┴──────────────┘
                          │
        ┌─────────────────┼─────────────────┐
        │                 │                 │
   ┌────▼────┐      ┌─────▼─────┐    ┌─────▼─────┐
   │PostgreSQL│      │   Redis   │    │  Celery   │
   │ Primary  │      │  Sentinel │    │  Workers  │
   │    +     │      │   Master  │    │ (N nodes) │
   │ Replicas │      │     +     │    └───────────┘
   │          │      │  Replicas │
   └──────────┘      └───────────┘
```

---

## 🔍 Monitoring Points

### Application Metrics

```
Superset Server:
├── Request rate (req/s)
├── Response time (ms)
├── Error rate (%)
├── Active sessions
└── Cache hit ratio

Celery Worker:
├── Tasks processed/min
├── Queue depth
├── Task success rate
├── Average task duration
└── Worker pool saturation

Database:
├── Connections active
├── Query duration
├── Cache hit ratio
├── Table sizes
└── Lock contention
```

### System Metrics

```
CPU:
├── Overall utilization
├── Per-container usage
└── Throttling events

Memory:
├── Total usage
├── Per-container usage
├── OOM events
└── Swap usage

Disk:
├── I/O operations
├── Read/Write throughput
├── Disk usage (%)
└── Inode usage

Network:
├── Inbound traffic
├── Outbound traffic
├── Packet loss
└── Connection count
```

---

## 🎯 Performance Tuning

### Cache Strategy

```
Layer 1: Browser Cache
  ├── Static assets (CSS, JS)
  └── TTL: 7 days

Layer 2: Superset Cache (Redis)
  ├── Dashboard data
  ├── Chart results
  └── TTL: 1 hour - 1 day

Layer 3: Database Cache
  ├── Query results
  └── TTL: Based on data freshness

Layer 4: Data Source Cache
  ├── Materialized views
  └── Pre-aggregated tables
```

### Query Optimization

```
1. Use Async Queries
   └── For long-running queries (>5s)

2. Enable Caching
   └── Set TTL based on data freshness

3. Optimize SQL
   ├── Use proper indexes
   ├── Limit result sets
   └── Use aggregations

4. Use Virtual Datasets
   └── Pre-filter common queries

5. Materialize Views
   └── For complex aggregations
```

---

**Arquitetura**: Multi-tier  
**Escalabilidade**: Horizontal  
**Alta Disponibilidade**: Sim (com configuração)  
**Performance**: Otimizada para BI workloads
