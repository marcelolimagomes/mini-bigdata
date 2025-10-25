# 📝 Apache Superset 5.0.0 - Exemplos Práticos

## 🎯 Casos de Uso Comuns

### 1. Conectar ao Trino (Stack Local)

```python
# Na interface do Superset
# Data → Databases → + Database

Database Name: Trino Local
SQLAlchemy URI: trino://trino@trino:8080/hive
```

**Testar conexão:**
```sql
-- SQL Lab
SELECT * FROM hive.default.information_schema.tables LIMIT 10;
```

### 2. Criar Dataset Virtual

```sql
-- SQL Lab → SQL Editor
CREATE OR REPLACE VIEW sales_summary AS
SELECT 
    DATE_TRUNC('month', order_date) as month,
    category,
    SUM(amount) as total_sales,
    COUNT(*) as order_count,
    AVG(amount) as avg_order
FROM hive.default.sales
GROUP BY 1, 2;

-- Depois: Data → Datasets → + Dataset
-- Selecione: trino / hive / sales_summary
```

### 3. Dashboard com Filtros Nativos

**Passo 1 - Criar Charts:**
```
Chart 1: Total Sales (Big Number)
├── Metric: SUM(total_sales)
└── Time Range: Last 90 days

Chart 2: Sales by Category (Bar Chart)
├── Dimension: category
├── Metric: SUM(total_sales)
└── Sort: Descending

Chart 3: Trend Over Time (Line Chart)
├── X-Axis: month
├── Y-Axis: SUM(total_sales)
└── Rolling Window: 7 days
```

**Passo 2 - Criar Dashboard:**
```
1. Dashboards → + Dashboard
2. Adicionar charts criados
3. Layout → Organizar em grid
4. Filtros → + Native Filter
   ├── Nome: Categoria
   ├── Dataset: sales_summary
   ├── Column: category
   └── Scoping: Apply to all charts
```

### 4. Alerta de Vendas Baixas

```yaml
# Alerts & Reports → + Alert

Name: Vendas Diárias Baixas
Chart: Total Sales (Big Number)
Schedule: Daily @ 9:00 AM
Condition: Value < 10000
Recipients: 
  - admin@example.com
  - vendas@example.com
Message: |
  ⚠️ Vendas abaixo da meta!
  Valor: {{ value }}
  Meta: R$ 10.000
```

### 5. Relatório Executivo Semanal

```yaml
# Alerts & Reports → + Report

Name: Relatório Executivo Semanal
Dashboard: Executive Dashboard
Schedule: Monday @ 8:00 AM
Format: PDF
Recipients:
  - ceo@example.com
  - cfo@example.com
Subject: Relatório Executivo - Semana {{ week }}
Message: |
  Prezados,
  
  Segue o relatório executivo da semana.
  
  Principais métricas em anexo.
```

---

## 🔧 SQL Templates (Jinja2)

### Template com Parâmetros

```sql
-- Criar SQL Template
{% set start_date = "'2024-01-01'" %}
{% set end_date = "CURRENT_DATE" %}

SELECT 
    product_name,
    SUM(quantity) as total_qty,
    SUM(amount) as revenue
FROM sales
WHERE order_date BETWEEN {{ start_date }} AND {{ end_date }}
  AND category = '{{ filter_values('category')[0] }}'
GROUP BY 1
ORDER BY 2 DESC
LIMIT 10;
```

### Template com Macro

```sql
-- Definir macro
{% macro revenue_tier(amount) %}
  CASE 
    WHEN {{ amount }} > 10000 THEN 'High'
    WHEN {{ amount }} > 5000 THEN 'Medium'
    ELSE 'Low'
  END
{% endmacro %}

-- Usar macro
SELECT 
    customer_id,
    SUM(amount) as total,
    {{ revenue_tier('SUM(amount)') }} as tier
FROM sales
GROUP BY 1;
```

### Template com Loop

```sql
-- Gerar queries dinâmicas
SELECT *
FROM (
  {% for month in range(1, 13) %}
    SELECT 
      {{ month }} as month,
      SUM(amount) as revenue
    FROM sales
    WHERE MONTH(order_date) = {{ month }}
    {% if not loop.last %} UNION ALL {% endif %}
  {% endfor %}
) months
ORDER BY month;
```

---

## 📊 Tipos de Visualização

### 1. Time Series (Série Temporal)

```yaml
Chart Type: Time-series Chart
Dataset: sales_summary
X-Axis: month (Temporal)
Metrics:
  - SUM(total_sales)
  - SUM(order_count)
Rolling Window: 7 days
Contribution Mode: On
Annotations:
  - Black Friday: 2024-11-29
  - Christmas: 2024-12-25
```

### 2. Geographic (Mapa)

```yaml
Chart Type: Deck.gl - Scatterplot
Dataset: store_locations
Longitude: longitude
Latitude: latitude
Size: total_sales
Color: category
Zoom Level: 10
Map Style: Dark
```

### 3. Pivot Table (Tabela Dinâmica)

```yaml
Chart Type: Pivot Table
Dataset: sales_detailed
Rows: 
  - category
  - product_name
Columns: 
  - month
Metrics:
  - SUM(amount)
  - COUNT(*)
Aggregation: Sum
Conditional Formatting:
  - Range: 0-1000 (Red)
  - Range: 1000-5000 (Yellow)
  - Range: >5000 (Green)
```

### 4. Sankey Diagram (Fluxo)

```yaml
Chart Type: Sankey
Dataset: customer_journey
Source: source_channel
Target: conversion_stage
Value: COUNT(DISTINCT customer_id)
Color Scheme: Superset Colors
```

---

## 🔐 Segurança e Permissões

### 1. Criar Role Customizada

```python
# Via Superset Shell
docker exec -it superset superset shell

from superset import db
from superset.security.manager import SupersetSecurityManager

# Criar role
security_manager = SupersetSecurityManager(appbuilder)
role = security_manager.add_role("Analyst")

# Adicionar permissões
permissions = [
    ("can_read", "Dashboard"),
    ("can_read", "Chart"),
    ("can_read", "Dataset"),
    ("can_sqllab", "Superset"),
]

for permission_name, view_menu_name in permissions:
    pvm = security_manager.find_permission_view_menu(
        permission_name, view_menu_name
    )
    if pvm:
        security_manager.add_permission_role(role, pvm)

db.session.commit()
```

### 2. Row Level Security (RLS)

```sql
-- Settings → Row Level Security → + Rule

Table: sales
Role: Regional Manager
Clause:
  region = '{{ current_user_id() }}'
  
-- OU com tabela de mapeamento
Clause:
  region IN (
    SELECT region 
    FROM user_regions 
    WHERE user_id = '{{ current_user_id() }}'
  )
```

### 3. Criar Usuário Programaticamente

```python
# Via API ou Shell
docker exec -it superset superset fab create-user \
    --username analyst \
    --firstname John \
    --lastname Doe \
    --email john.doe@example.com \
    --role Analyst \
    --password SecurePass123!
```

---

## 🔄 Automação e API

### 1. Export Dashboard via API

```bash
# Login e obter token
TOKEN=$(curl -X POST http://localhost:8088/api/v1/security/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin",
    "password": "admin",
    "provider": "db",
    "refresh": true
  }' | jq -r '.access_token')

# Exportar dashboard
curl -X GET http://localhost:8088/api/v1/dashboard/export/?q=!(1,2,3) \
  -H "Authorization: Bearer $TOKEN" \
  -o dashboards_export.zip
```

### 2. Import Dashboard via CLI

```bash
# Descompactar export
unzip dashboards_export.zip -d /tmp/dashboards

# Copiar para container
docker cp /tmp/dashboards superset:/tmp/

# Importar
docker exec superset superset import-dashboards \
  -p /tmp/dashboards/dashboard_export_*.yaml
```

### 3. Refresh Dataset via API

```bash
# Forçar refresh do cache de um dataset
curl -X PUT http://localhost:8088/api/v1/dataset/1/refresh \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json"
```

### 4. Execute Query via API

```bash
# Executar SQL Lab query
curl -X POST http://localhost:8088/api/v1/sqllab/execute/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "database_id": 1,
    "sql": "SELECT COUNT(*) FROM sales",
    "runAsync": false
  }'
```

---

## 🎨 Customização

### 1. Logo Customizado

```bash
# Copiar logo para container
docker cp /path/to/logo.png superset:/app/superset/static/assets/images/

# Atualizar superset_config.py
APP_NAME = "My Company BI"
APP_ICON = "/static/assets/images/logo.png"
```

### 2. Tema Customizado (CSS)

```python
# superset_config.py
CUSTOM_CSS = """
    /* Header */
    .navbar {
        background-color: #1f77b4 !important;
    }
    
    /* Sidebar */
    .ant-menu {
        background-color: #f5f5f5;
    }
    
    /* Cards */
    .ant-card {
        border-radius: 8px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    }
    
    /* Primary button */
    .ant-btn-primary {
        background-color: #1f77b4;
        border-color: #1f77b4;
    }
"""
```

### 3. Color Scheme Customizado

```python
# superset_config.py
EXTRA_CATEGORICAL_COLOR_SCHEMES = [
    {
        "id": "my_colors",
        "description": "My Company Colors",
        "label": "Company Palette",
        "colors": [
            "#1f77b4",  # Blue
            "#ff7f0e",  # Orange
            "#2ca02c",  # Green
            "#d62728",  # Red
            "#9467bd",  # Purple
        ],
    }
]
```

---

## 📈 Performance Tips

### 1. Otimizar Query com Cache

```sql
-- Adicionar no dataset ou chart
-- Settings → Advanced → Cache Timeout
-- Valor: 3600 (1 hora)

-- Ou via SQL
SELECT /*+ CACHE(3600) */ 
    category,
    COUNT(*) as count
FROM sales
GROUP BY category;
```

### 2. Usar Async Queries

```python
# superset_config.py
SQLLAB_ASYNC_TIME_LIMIT_SEC = 300  # 5 min

# Na interface:
# Database → Edit → SQL Lab → Async query execution ✓
```

### 3. Pre-agregação

```sql
-- Criar tabela agregada
CREATE TABLE sales_daily_summary AS
SELECT 
    DATE(order_date) as date,
    category,
    SUM(amount) as daily_total,
    COUNT(*) as order_count
FROM sales
GROUP BY 1, 2;

-- Usar no Superset ao invés da tabela original
-- Muito mais rápido para dashboards diários
```

### 4. Partition Pruning

```sql
-- Usar filtros em colunas particionadas
SELECT *
FROM sales_partitioned
WHERE 
    date_partition >= '2024-01-01'  -- Partition column
    AND category = 'Electronics';
```

---

## 🔍 Debugging

### 1. Enable SQL Query Logs

```python
# superset_config.py
from superset.app import db

# Log todas as queries
db.engine.echo = True

# Ou via SQL Lab
# Settings → SQL Lab → Display query preview
```

### 2. Profile Slow Queries

```python
# superset_config.py
from flask_profiler import Profiler

ENABLE_PROFILING = True
PROFILER_ENABLED = True
```

### 3. Debug Mode (Dev Only!)

```python
# superset_config.py
DEBUG = True
FLASK_DEBUG = True

# Reiniciar
docker compose restart superset
```

---

## 📝 Backup & Migration

### 1. Backup Completo

```bash
#!/bin/bash
# backup-superset.sh

DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/backup/superset/$DATE"

mkdir -p $BACKUP_DIR

# Backup PostgreSQL
docker exec postgres pg_dump -U admin superset \
  | gzip > $BACKUP_DIR/database.sql.gz

# Backup dashboards/charts
docker exec superset superset export-dashboards \
  -f /tmp/dashboards.json
docker cp superset:/tmp/dashboards.json $BACKUP_DIR/

# Backup config
docker cp superset:/app/pythonpath/superset_config.py \
  $BACKUP_DIR/

echo "Backup completed: $BACKUP_DIR"
```

### 2. Restore Completo

```bash
#!/bin/bash
# restore-superset.sh

BACKUP_DIR="/backup/superset/20241025_120000"

# Restore database
gunzip < $BACKUP_DIR/database.sql.gz | \
  docker exec -i postgres psql -U admin superset

# Restore dashboards
docker cp $BACKUP_DIR/dashboards.json superset:/tmp/
docker exec superset superset import-dashboards \
  -p /tmp/dashboards.json

echo "Restore completed"
```

---

## 🎓 Resources

### Documentação Oficial
- [Charts Gallery](https://superset.apache.org/gallery)
- [API Documentation](https://superset.apache.org/docs/api)
- [SQL Lab](https://superset.apache.org/docs/using-superset/exploring-data)

### Community
- [Slack Channel](https://superset.apache.org/community)
- [GitHub Discussions](https://github.com/apache/superset/discussions)
- [Stack Overflow](https://stackoverflow.com/questions/tagged/apache-superset)

---

**Última atualização**: Outubro 2025  
**Versão**: 5.0.0
