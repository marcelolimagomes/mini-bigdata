# 🔍 Consultas SQL com Trino

## 🎯 Visão Geral

O Trino é um engine SQL distribuído que permite consultar dados de diversas fontes (MinIO, Hive, PostgreSQL, etc) usando SQL padrão.

- **Interface Web:** http://localhost:8085
- **Usuário:** `trino`
- **Catalogs disponíveis:** `hive`, `minio`

## 🚀 Conectando ao Trino

### Método 1: CLI no Container

```bash
# Entrar no container Trino
docker exec -it trino trino

# Ou conectar diretamente
docker exec -it trino trino --catalog hive --schema default
```

### Método 2: Cliente Python

```python
from trino.dbapi import connect

conn = connect(
    host='localhost',
    port=8085,
    user='trino',
    catalog='hive',
    schema='default'
)

cursor = conn.cursor()
cursor.execute('SELECT * FROM vendas LIMIT 10')
rows = cursor.fetchall()

for row in rows:
    print(row)
```

### Método 3: SQLAlchemy

```python
from sqlalchemy import create_engine

engine = create_engine('trino://trino@localhost:8085/hive/default')

import pandas as pd
df = pd.read_sql('SELECT * FROM vendas', engine)
print(df.head())
```

### Método 4: DBeaver / DataGrip

```
Driver: Trino
URL: jdbc:trino://localhost:8085
User: trino
Password: (deixar em branco)
```

## 📊 Catálogos e Schemas

### Listar Catálogos
```sql
SHOW CATALOGS;
```

Resultado:
```
catalog
-------
hive
minio
system
```

### Listar Schemas
```sql
SHOW SCHEMAS FROM hive;
```

### Listar Tabelas
```sql
SHOW TABLES FROM hive.default;
```

## 🎯 Criando Tabelas no Hive

### Tabela Externa apontando para MinIO

```sql
-- Criar schema
CREATE SCHEMA IF NOT EXISTS hive.vendas;

-- Criar tabela externa (dados no MinIO)
CREATE TABLE hive.vendas.vendas_bronze (
    data DATE,
    produto VARCHAR,
    quantidade INTEGER,
    valor DOUBLE
)
WITH (
    external_location = 's3a://bronze/vendas/',
    format = 'CSV',
    skip_header_line_count = 1
);

-- Verificar dados
SELECT * FROM hive.vendas.vendas_bronze LIMIT 10;
```

### Tabela Particionada

```sql
CREATE TABLE hive.vendas.vendas_silver (
    data DATE,
    produto VARCHAR,
    quantidade INTEGER,
    valor DOUBLE,
    valor_total DOUBLE,
    ano INTEGER,
    mes INTEGER
)
WITH (
    external_location = 's3a://silver/vendas/vendas_processadas/',
    format = 'PARQUET',
    partitioned_by = ARRAY['ano', 'mes']
);

-- Popular partições
CALL system.sync_partition_metadata('hive', 'vendas', 'vendas_silver');
```

## 📊 Consultas SQL

### Consultas Básicas

```sql
-- Selecionar todas as vendas
SELECT * FROM hive.vendas.vendas_silver LIMIT 100;

-- Contagem total
SELECT COUNT(*) as total_vendas 
FROM hive.vendas.vendas_silver;

-- Vendas por produto
SELECT 
    produto,
    COUNT(*) as total_vendas,
    SUM(quantidade) as quantidade_total,
    SUM(valor_total) as receita_total,
    AVG(valor) as ticket_medio
FROM hive.vendas.vendas_silver
GROUP BY produto
ORDER BY receita_total DESC;
```

### Análise Temporal

```sql
-- Vendas por mês
SELECT 
    ano,
    mes,
    COUNT(*) as total_vendas,
    SUM(valor_total) as receita,
    AVG(valor_total) as ticket_medio
FROM hive.vendas.vendas_silver
GROUP BY ano, mes
ORDER BY ano, mes;

-- Tendência mensal
SELECT 
    CAST(ano AS VARCHAR) || '-' || LPAD(CAST(mes AS VARCHAR), 2, '0') as periodo,
    SUM(valor_total) as receita,
    LAG(SUM(valor_total)) OVER (ORDER BY ano, mes) as receita_mes_anterior,
    ((SUM(valor_total) - LAG(SUM(valor_total)) OVER (ORDER BY ano, mes)) / 
     LAG(SUM(valor_total)) OVER (ORDER BY ano, mes)) * 100 as crescimento_percentual
FROM hive.vendas.vendas_silver
GROUP BY ano, mes
ORDER BY ano, mes;
```

### Análise de Produtos

```sql
-- Top 10 produtos por receita
SELECT 
    produto,
    SUM(valor_total) as receita_total,
    COUNT(*) as num_vendas,
    AVG(quantidade) as quantidade_media
FROM hive.vendas.vendas_silver
GROUP BY produto
ORDER BY receita_total DESC
LIMIT 10;

-- Produtos com maior crescimento
WITH vendas_por_periodo AS (
    SELECT 
        produto,
        ano,
        mes,
        SUM(valor_total) as receita
    FROM hive.vendas.vendas_silver
    GROUP BY produto, ano, mes
)
SELECT 
    produto,
    receita as receita_atual,
    LAG(receita) OVER (PARTITION BY produto ORDER BY ano, mes) as receita_anterior,
    ((receita - LAG(receita) OVER (PARTITION BY produto ORDER BY ano, mes)) / 
     LAG(receita) OVER (PARTITION BY produto ORDER BY ano, mes)) * 100 as crescimento
FROM vendas_por_periodo
WHERE LAG(receita) OVER (PARTITION BY produto ORDER BY ano, mes) IS NOT NULL
ORDER BY crescimento DESC;
```

### Agregações Avançadas

```sql
-- Análise com múltiplas métricas
SELECT 
    produto,
    COUNT(DISTINCT CAST(ano AS VARCHAR) || LPAD(CAST(mes AS VARCHAR), 2, '0')) as meses_ativos,
    MIN(data) as primeira_venda,
    MAX(data) as ultima_venda,
    SUM(quantidade) as quantidade_total,
    SUM(valor_total) as receita_total,
    AVG(valor_total) as ticket_medio,
    STDDEV(valor_total) as desvio_padrao,
    MIN(valor_total) as menor_venda,
    MAX(valor_total) as maior_venda,
    APPROX_PERCENTILE(valor_total, 0.5) as mediana
FROM hive.vendas.vendas_silver
GROUP BY produto
ORDER BY receita_total DESC;
```

### Window Functions

```sql
-- Ranking de produtos por mês
SELECT 
    ano,
    mes,
    produto,
    SUM(valor_total) as receita,
    RANK() OVER (PARTITION BY ano, mes ORDER BY SUM(valor_total) DESC) as ranking
FROM hive.vendas.vendas_silver
GROUP BY ano, mes, produto
ORDER BY ano, mes, ranking;

-- Acumulado
SELECT 
    data,
    produto,
    valor_total,
    SUM(valor_total) OVER (
        PARTITION BY produto 
        ORDER BY data 
        ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
    ) as receita_acumulada
FROM hive.vendas.vendas_silver
ORDER BY produto, data;
```

## 🔗 Joins entre Fontes

```sql
-- Join entre MinIO e PostgreSQL
SELECT 
    v.produto,
    v.quantidade,
    p.nome_produto,
    p.categoria
FROM hive.vendas.vendas_silver v
JOIN postgres.public.produtos p ON v.produto = p.codigo;
```

## 📊 Criando Views

```sql
-- View para análise mensal
CREATE OR REPLACE VIEW hive.vendas.vendas_mensais AS
SELECT 
    ano,
    mes,
    COUNT(*) as total_vendas,
    SUM(valor_total) as receita,
    AVG(valor_total) as ticket_medio
FROM hive.vendas.vendas_silver
GROUP BY ano, mes;

-- Usar view
SELECT * FROM hive.vendas.vendas_mensais ORDER BY ano, mes;
```

## 🎯 Exportando Resultados

### Para CSV

```sql
-- Via Trino CLI (no container)
trino --execute "
    SELECT * FROM hive.vendas.vendas_mensais
" --output-format CSV > vendas_mensais.csv
```

### Para Parquet (criar nova tabela)

```sql
CREATE TABLE hive.vendas.vendas_resumo
WITH (
    format = 'PARQUET',
    external_location = 's3a://gold/vendas/resumo/'
) AS
SELECT 
    produto,
    SUM(quantidade) as quantidade_total,
    SUM(valor_total) as receita_total
FROM hive.vendas.vendas_silver
GROUP BY produto;
```

## 🔍 Funções Úteis

### Funções de Data

```sql
-- Extrair componentes da data
SELECT 
    data,
    YEAR(data) as ano,
    MONTH(data) as mes,
    DAY(data) as dia,
    DAY_OF_WEEK(data) as dia_semana,
    QUARTER(data) as trimestre,
    DATE_FORMAT(data, '%Y-%m') as ano_mes
FROM hive.vendas.vendas_silver
LIMIT 5;
```

### Funções de String

```sql
SELECT 
    produto,
    UPPER(produto) as produto_maiusculo,
    LOWER(produto) as produto_minusculo,
    LENGTH(produto) as tamanho,
    SUBSTR(produto, 1, 3) as prefixo
FROM hive.vendas.vendas_silver
LIMIT 5;
```

### Funções de Agregação

```sql
SELECT 
    produto,
    COUNT(*) as total,
    COUNT(DISTINCT data) as dias_diferentes,
    SUM(quantidade) as soma,
    AVG(valor) as media,
    MIN(valor) as minimo,
    MAX(valor) as maximo,
    STDDEV(valor) as desvio_padrao,
    VARIANCE(valor) as variancia,
    APPROX_PERCENTILE(valor, 0.5) as mediana
FROM hive.vendas.vendas_silver
GROUP BY produto;
```

## 📈 Otimização de Queries

### 1. Usar Partições

```sql
-- Ruim: Scan completo
SELECT * FROM hive.vendas.vendas_silver;

-- Bom: Filtrar por partição
SELECT * FROM hive.vendas.vendas_silver
WHERE ano = 2025 AND mes = 1;
```

### 2. Filtros no WHERE

```sql
-- Aplicar filtros cedo
SELECT 
    produto,
    SUM(valor_total) as receita
FROM hive.vendas.vendas_silver
WHERE ano = 2025  -- Filtro cedo
GROUP BY produto
HAVING SUM(valor_total) > 1000;  -- Filtro após agregação
```

### 3. LIMIT quando Apropriado

```sql
-- Para testes, usar LIMIT
SELECT * FROM hive.vendas.vendas_silver LIMIT 100;
```

## 🎯 Queries para Dashboard

### KPIs Principais

```sql
-- KPIs do período
SELECT 
    COUNT(*) as total_vendas,
    SUM(quantidade) as itens_vendidos,
    SUM(valor_total) as receita_total,
    AVG(valor_total) as ticket_medio,
    COUNT(DISTINCT produto) as produtos_diferentes
FROM hive.vendas.vendas_silver
WHERE ano = 2025 AND mes = 1;
```

### Série Temporal para Gráfico

```sql
-- Receita diária
SELECT 
    data,
    SUM(valor_total) as receita
FROM hive.vendas.vendas_silver
WHERE data >= DATE '2025-01-01'
GROUP BY data
ORDER BY data;
```

### Distribuição por Categoria

```sql
-- Para gráfico de pizza
SELECT 
    produto,
    SUM(valor_total) as receita,
    (SUM(valor_total) * 100.0 / (SELECT SUM(valor_total) FROM hive.vendas.vendas_silver)) as percentual
FROM hive.vendas.vendas_silver
GROUP BY produto
ORDER BY receita DESC;
```

## 🆘 Troubleshooting

### Tabela não encontrada
```sql
-- Verificar se existe
SHOW TABLES FROM hive.vendas;

-- Recriar metadados
CALL system.sync_partition_metadata('hive', 'vendas', 'vendas_silver');
```

### Erro de permissão MinIO
- Verificar credenciais em `catalog/hive.properties`
- Testar acesso ao bucket no MinIO Console

### Query lenta
- Usar EXPLAIN para ver plano de execução
```sql
EXPLAIN SELECT * FROM hive.vendas.vendas_silver WHERE ano = 2025;
```

## 🎓 Próximos Passos

- **Dashboards no Superset:** `05-criando-dashboards-superset.md`
- **Catálogo Hive:** `06-catalogo-hive-metastore.md`
- **APIs de acesso:** `07-apis-rest-jdbc.md`
