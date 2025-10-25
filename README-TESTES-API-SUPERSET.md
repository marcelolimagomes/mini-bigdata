# Scripts de Teste - APIs Apache Superset

Este diretório contém scripts para testar e automatizar operações nas APIs do Apache Superset.

## 📋 Índice

- [Pré-requisitos](#pré-requisitos)
- [Scripts Disponíveis](#scripts-disponíveis)
- [Como Usar](#como-usar)
- [Configuração](#configuração)
- [Exemplos](#exemplos)

---

## 🔧 Pré-requisitos

### Ambiente
- Python 3.11+
- Apache Superset 4.1.4 rodando
- Redis configurado como results backend

### Bibliotecas Python
```bash
pip install requests
```

### Configuração do Superset

O Superset deve ter o **Results Backend** configurado em `config/superset/superset_config.py`:

```python
from cachelib.redis import RedisCache

RESULTS_BACKEND = RedisCache(
    host='redis',
    port=6379,
    db=1,
    key_prefix='superset_results_'
)
```

---

## 📁 Scripts Disponíveis

### 1. `test_superset_api_complete.py`
**Descrição:** Teste abrangente de todas as APIs do Superset

**Funcionalidades:**
- ✅ Autenticação JWT
- ✅ CRUD de Databases
- ✅ CRUD de Datasets
- ✅ CRUD de Charts
- ✅ CRUD de Dashboards
- ✅ Validação de SQL Lab
- ✅ Verificação de permissões
- ✅ Limpeza automática de recursos

**Uso:**
```bash
python3 test_superset_api_complete.py
```

**Saída Esperada:**
```
================================================================================
  TESTE COMPLETO DAS APIs DO APACHE SUPERSET
================================================================================
✓ Autenticação
✓ Databases
✓ Datasets
...
Taxa de Sucesso: 85.7%
```

---

### 2. `test_superset_crud_operations.py`
**Descrição:** Testes detalhados de operações CRUD

**Funcionalidades:**
- ✅ CREATE - Criar recursos
- ✅ READ - Ler recursos
- ✅ UPDATE - Atualizar recursos
- ✅ DELETE - Deletar recursos
- ✅ Validação de estado após cada operação

**Uso:**
```bash
python3 test_superset_crud_operations.py
```

**Recursos Testados:**
- Database (CREATE → READ → UPDATE → DELETE)
- Dataset (CREATE → READ → UPDATE → DELETE)
- Chart (CREATE → READ → UPDATE → DELETE)
- Dashboard (CREATE → READ → UPDATE → DELETE)

---

### 3. `test_superset_sql_queries.py`
**Descrição:** Testes de execução de queries SQL via API

**Funcionalidades:**
- ✅ Listagem de databases disponíveis
- ✅ Execução de queries básicas
- ✅ Queries em tabelas existentes
- ✅ Validação de resultados
- ✅ Teste de múltiplas engines (PostgreSQL, Trino)

**Uso:**
```bash
python3 test_superset_sql_queries.py
```

**Queries Testadas:**
```sql
-- Query simples
SELECT 1 as number

-- Múltiplas colunas
SELECT 1 as id, 'test' as name, NOW() as timestamp

-- Generate series
SELECT generate_series(1, 5) as number

-- UNION ALL
SELECT 'Database' as category, current_database() as value
UNION ALL SELECT 'User', current_user
```

---

### 4. `exemplo_automacao_superset.py`
**Descrição:** Exemplo prático de automação completa

**Funcionalidades:**
- ✅ Classe `SupersetAutomation` reutilizável
- ✅ Criação automatizada de recursos
- ✅ Pipeline completo: Database → Dataset → Chart → Dashboard
- ✅ Métodos auxiliares para operações comuns

**Uso:**
```bash
python3 exemplo_automacao_superset.py
```

**Exemplo Programático:**
```python
from exemplo_automacao_superset import SupersetAutomation

# Inicializar
superset = SupersetAutomation(
    "http://localhost:8088",
    "admin",
    "admin"
)

# Criar database
db_id = superset.create_database(
    name="My Database",
    uri="postgresql://user:pass@host:5432/db"
)

# Criar dataset virtual
dataset_id = superset.create_virtual_dataset(
    database_id=db_id,
    name="my_dataset",
    sql="SELECT * FROM my_table"
)

# Criar chart
chart_id = superset.create_chart(
    name="My Chart",
    datasource_id=dataset_id,
    viz_type="table"
)

# Criar dashboard
dashboard_id = superset.create_dashboard(
    title="My Dashboard",
    chart_ids=[chart_id]
)

print(f"Dashboard URL: http://localhost:8088/superset/dashboard/{dashboard_id}/")
```

---

## 🚀 Como Usar

### Executar Todos os Testes

```bash
# 1. Teste completo de APIs
python3 test_superset_api_complete.py

# 2. Testes CRUD detalhados
python3 test_superset_crud_operations.py

# 3. Testes de queries SQL
python3 test_superset_sql_queries.py

# 4. Exemplo de automação
python3 exemplo_automacao_superset.py
```

### Executar Teste Específico

Para executar apenas uma parte específica, modifique o script:

```python
# exemplo_automacao_superset.py

if __name__ == "__main__":
    # Comentar o exemplo completo
    # exemplo_completo()
    
    # Executar exemplo simples
    exemplo_simples()
```

---

## ⚙️ Configuração

### Variáveis de Ambiente

Os scripts usam as seguintes configurações (hardcoded):

```python
SUPERSET_URL = "http://localhost:8088"
USERNAME = "admin"
PASSWORD = "admin"
```

Para ambientes diferentes, modifique essas variáveis nos scripts ou use variáveis de ambiente:

```python
import os

SUPERSET_URL = os.getenv("SUPERSET_URL", "http://localhost:8088")
USERNAME = os.getenv("SUPERSET_USER", "admin")
PASSWORD = os.getenv("SUPERSET_PASSWORD", "admin")
```

### Headers Necessários

Todos os scripts já configuram os headers corretamente:

```python
headers = {
    "Authorization": f"Bearer {access_token}",
    "Content-Type": "application/json",
    "X-CSRFToken": csrf_token,  # Para POST/PUT/DELETE
    "Referer": superset_url
}
```

---

## 📊 Exemplos de Uso

### Exemplo 1: Criar Database e Dataset

```python
from exemplo_automacao_superset import SupersetAutomation

superset = SupersetAutomation(
    "http://localhost:8088",
    "admin",
    "admin"
)

# Criar database PostgreSQL
db_id = superset.create_database(
    name="Analytics DB",
    uri="postgresql://user:pass@postgres:5432/analytics",
    expose_in_sqllab=True
)

# Criar dataset virtual com agregações
dataset_id = superset.create_virtual_dataset(
    database_id=db_id,
    name="vw_sales_summary",
    sql="""
        SELECT 
            DATE_TRUNC('month', order_date) as month,
            SUM(amount) as total_sales,
            COUNT(*) as order_count
        FROM orders
        GROUP BY 1
        ORDER BY 1 DESC
    """
)

print(f"Dataset criado: {dataset_id}")
```

### Exemplo 2: Executar Query SQL

```python
# Executar query e obter resultados
result = superset.execute_sql(
    database_id=db_id,
    sql="SELECT COUNT(*) as total FROM customers"
)

# Processar resultados
for row in result['data']:
    print(f"Total de clientes: {row['total']}")
```

### Exemplo 3: Listar Recursos Existentes

```python
# Listar databases
databases = superset.list_databases()
for db in databases:
    print(f"Database: {db['database_name']} (ID: {db['id']})")

# Usar com requests diretamente
import requests

response = requests.get(
    "http://localhost:8088/api/v1/chart/",
    headers=superset._get_headers(with_csrf=False)
)

charts = response.json()['result']
for chart in charts:
    print(f"Chart: {chart['slice_name']}")
```

### Exemplo 4: Pipeline Completo

```python
# Pipeline de criação completo
def create_analytics_dashboard():
    superset = SupersetAutomation(
        "http://localhost:8088",
        "admin",
        "admin"
    )
    
    # 1. Database
    db_id = superset.create_database(
        name="Sales DB",
        uri="postgresql://user:pass@host:5432/sales"
    )
    
    # 2. Múltiplos datasets
    datasets = []
    
    datasets.append(superset.create_virtual_dataset(
        database_id=db_id,
        name="vw_daily_sales",
        sql="SELECT * FROM daily_sales_summary"
    ))
    
    datasets.append(superset.create_virtual_dataset(
        database_id=db_id,
        name="vw_top_products",
        sql="SELECT * FROM top_products_view"
    ))
    
    # 3. Múltiplos charts
    charts = []
    
    charts.append(superset.create_chart(
        name="Daily Sales Trend",
        datasource_id=datasets[0],
        viz_type="line"
    ))
    
    charts.append(superset.create_chart(
        name="Top 10 Products",
        datasource_id=datasets[1],
        viz_type="table"
    ))
    
    # 4. Dashboard
    dashboard_id = superset.create_dashboard(
        title="Sales Analytics Dashboard",
        chart_ids=charts
    )
    
    print(f"✅ Dashboard criado: http://localhost:8088/superset/dashboard/{dashboard_id}/")
    return dashboard_id

# Executar
dashboard_id = create_analytics_dashboard()
```

---

## 🔍 Troubleshooting

### Erro: "Results backend is not configured"

**Solução:** Configurar results backend no `superset_config.py`:

```python
from cachelib.redis import RedisCache

RESULTS_BACKEND = RedisCache(
    host='redis',
    port=6379,
    db=1,
    key_prefix='superset_results_'
)
```

Reiniciar o Superset:
```bash
docker compose restart superset
```

### Erro: "401 Unauthorized"

**Causa:** Token expirado ou inválido

**Solução:** Reautenticar:
```python
superset = SupersetAutomation(url, user, password)
# Autenticação é feita automaticamente no __init__
```

### Erro: "CSRF token missing"

**Solução:** Garantir que o CSRF token está sendo enviado:
```python
headers = {
    "X-CSRFToken": csrf_token,
    "Referer": superset_url
}
```

### Erro: "Connection refused"

**Causa:** Superset não está rodando

**Solução:**
```bash
docker compose up -d superset
# Aguardar ~15 segundos
docker logs superset --tail 20
```

---

## 📈 Resultados Esperados

### test_superset_api_complete.py
- ✅ 6/7 testes passando (85.7%)
- ⚠️ Endpoint `/api/v1/me/` pode falhar (não crítico)

### test_superset_crud_operations.py
- ✅ 16/16 operações passando (100%)
- ✅ Todos os recursos criados e deletados com sucesso

### test_superset_sql_queries.py
- ✅ 4/4 queries executando (100%)
- ✅ Resultados retornados corretamente

### exemplo_automacao_superset.py
- ✅ Pipeline completo executando
- ✅ Dashboard acessível via browser

---

## 📚 Documentação Adicional

- **Relatório Completo:** `RELATORIO-FINAL-TESTES-API-SUPERSET.md`
- **Swagger UI:** `http://localhost:8088/swagger/v1`
- **Documentação Oficial:** https://superset.apache.org/docs/api

---

## ✅ Checklist de Validação

Antes de usar em produção, verifique:

- [ ] Results backend configurado
- [ ] Redis rodando e acessível
- [ ] CSRF protection habilitado (produção)
- [ ] HTTPS configurado (produção)
- [ ] Credenciais seguras (não hardcoded)
- [ ] Rate limiting configurado
- [ ] Logs e monitoramento ativos
- [ ] Backup de configurações implementado

---

**Última atualização:** 25/10/2025  
**Versão Testada:** Apache Superset 4.1.4  
**Status:** ✅ Totalmente funcional
