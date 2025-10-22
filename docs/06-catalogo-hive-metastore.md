# 🗄️ Catálogo Hive Metastore

## 🎯 Visão Geral

O Hive Metastore é o catálogo central de metadados para todas as tabelas e schemas do Data Lake.

- **Porta:** 9083
- **Database Backend:** PostgreSQL
- **Compatibilidade:** Spark, Trino, Hive

## 🔍 Arquitetura do Metastore

```
┌─────────────────────────────────────┐
│        Clientes (Spark/Trino)       │
└──────────────┬──────────────────────┘
               │ Thrift (9083)
┌──────────────▼──────────────────────┐
│       Hive Metastore Service        │
│   - Gerencia schemas e tabelas      │
│   - Armazena metadados              │
│   - Registra partições              │
└──────────────┬──────────────────────┘
               │ JDBC
┌──────────────▼──────────────────────┐
│         PostgreSQL Backend          │
│   - Tabela: DBS (databases)         │
│   - Tabela: TBLS (tables)           │
│   - Tabela: COLUMNS_V2              │
│   - Tabela: PARTITIONS              │
└─────────────────────────────────────┘
```

## 🚀 Gerenciamento via Spark

### Conectar ao Spark Shell

```bash
docker compose exec spark-master spark-shell
```

### Criar Database

```scala
// Criar database
spark.sql("CREATE DATABASE IF NOT EXISTS vendas")

// Com localização customizada
spark.sql("""
  CREATE DATABASE IF NOT EXISTS analytics
  LOCATION 's3a://gold/analytics/'
  COMMENT 'Database para analytics'
""")

// Listar databases
spark.sql("SHOW DATABASES").show()
```

### Criar Tabelas

#### Tabela Gerenciada

```scala
// Tabela gerenciada (dados no warehouse do Hive)
spark.sql("""
  CREATE TABLE vendas.produtos (
    id INT,
    nome STRING,
    categoria STRING,
    preco DECIMAL(10,2),
    data_criacao TIMESTAMP
  )
  USING PARQUET
  COMMENT 'Catálogo de produtos'
""")
```

#### Tabela Externa

```scala
// Tabela externa (dados no MinIO)
spark.sql("""
  CREATE EXTERNAL TABLE vendas.vendas_raw (
    id STRING,
    data STRING,
    produto STRING,
    quantidade INT,
    valor DOUBLE
  )
  USING CSV
  OPTIONS (
    path 's3a://bronze/vendas/raw/',
    header 'true',
    delimiter ','
  )
""")
```

#### Tabela Particionada

```scala
// Tabela particionada por ano e mês
spark.sql("""
  CREATE TABLE vendas.vendas_particionada (
    id STRING,
    data DATE,
    produto STRING,
    quantidade INT,
    valor DECIMAL(10,2)
  )
  USING PARQUET
  PARTITIONED BY (ano INT, mes INT)
  LOCATION 's3a://silver/vendas/particionada/'
""")

// Inserir dados com partição
spark.sql("""
  INSERT INTO vendas.vendas_particionada
  PARTITION (ano=2025, mes=1)
  VALUES 
    ('V001', '2025-01-15', 'Notebook', 2, 4500.00),
    ('V002', '2025-01-20', 'Mouse', 5, 150.00)
""")
```

### Gerenciar Partições

```scala
// Listar partições
spark.sql("SHOW PARTITIONS vendas.vendas_particionada").show()

// Adicionar partição manualmente
spark.sql("""
  ALTER TABLE vendas.vendas_particionada
  ADD PARTITION (ano=2025, mes=2)
  LOCATION 's3a://silver/vendas/particionada/ano=2025/mes=2/'
""")

// Remover partição
spark.sql("""
  ALTER TABLE vendas.vendas_particionada
  DROP PARTITION (ano=2025, mes=2)
""")

// Reparar partições (descobrir automaticamente)
spark.sql("MSCK REPAIR TABLE vendas.vendas_particionada")
```

### Propriedades de Tabelas

```scala
// Adicionar propriedades
spark.sql("""
  ALTER TABLE vendas.produtos
  SET TBLPROPERTIES (
    'description' = 'Tabela de produtos atualizada',
    'last_modified_by' = 'analytics_team',
    'version' = '2.0'
  )
""")

// Ver propriedades
spark.sql("SHOW TBLPROPERTIES vendas.produtos").show()
```

### Estatísticas

```scala
// Coletar estatísticas da tabela
spark.sql("ANALYZE TABLE vendas.produtos COMPUTE STATISTICS")

// Estatísticas de colunas
spark.sql("""
  ANALYZE TABLE vendas.produtos 
  COMPUTE STATISTICS FOR COLUMNS id, preco
""")

// Ver estatísticas
spark.sql("DESCRIBE EXTENDED vendas.produtos").show(false)
```

## 🔧 Gerenciamento via Trino

### Conectar ao Trino CLI

```bash
docker compose exec trino trino --catalog hive --schema default
```

### Gerenciar Schemas

```sql
-- Criar schema
CREATE SCHEMA IF NOT EXISTS hive.vendas
WITH (location = 's3a://gold/vendas/');

-- Listar schemas
SHOW SCHEMAS IN hive;

-- Ver detalhes
SHOW CREATE SCHEMA hive.vendas;

-- Remover schema
DROP SCHEMA IF EXISTS hive.analytics;
```

### Gerenciar Tabelas

```sql
-- Criar tabela ORC
CREATE TABLE hive.vendas.clientes (
    id BIGINT,
    nome VARCHAR,
    email VARCHAR,
    telefone VARCHAR,
    data_cadastro TIMESTAMP
)
WITH (
    format = 'ORC',
    external_location = 's3a://gold/vendas/clientes/'
);

-- Criar tabela a partir de query
CREATE TABLE hive.vendas.vendas_agregadas AS
SELECT 
    produto,
    YEAR(CAST(data AS DATE)) AS ano,
    MONTH(CAST(data AS DATE)) AS mes,
    SUM(quantidade) AS quantidade_total,
    SUM(valor_total) AS receita_total
FROM hive.vendas.vendas_silver
GROUP BY produto, YEAR(CAST(data AS DATE)), MONTH(CAST(data AS DATE));

-- Listar tabelas
SHOW TABLES IN hive.vendas;

-- Ver estrutura
DESCRIBE hive.vendas.clientes;

-- Ver DDL completo
SHOW CREATE TABLE hive.vendas.clientes;
```

### Modificar Tabelas

```sql
-- Adicionar coluna
ALTER TABLE hive.vendas.clientes 
ADD COLUMN cidade VARCHAR;

-- Renomear tabela
ALTER TABLE hive.vendas.clientes 
RENAME TO hive.vendas.cadastro_clientes;

-- Remover tabela
DROP TABLE IF EXISTS hive.vendas.temp_data;
```

## 📊 Formatos de Arquivo Suportados

### Parquet (Recomendado)

```scala
// Criar tabela Parquet
spark.sql("""
  CREATE TABLE vendas.dados_parquet (
    id INT,
    valor DECIMAL(10,2),
    data DATE
  )
  USING PARQUET
  OPTIONS (
    compression 'snappy'
  )
""")
```

**Vantagens:**
- Compressão eficiente
- Schema embarcado
- Otimizado para queries analíticas
- Suporta nested data

### ORC

```sql
-- Trino: Criar tabela ORC
CREATE TABLE hive.vendas.dados_orc (
    id BIGINT,
    valor DECIMAL(10,2),
    data DATE
)
WITH (
    format = 'ORC',
    orc_compression = 'ZLIB'
);
```

**Vantagens:**
- Alta compressão
- Índices integrados
- Ideal para Hive

### Avro

```scala
// Spark: Tabela Avro
spark.sql("""
  CREATE TABLE vendas.dados_avro (
    id INT,
    dados STRING
  )
  USING AVRO
  LOCATION 's3a://bronze/avro/'
""")
```

**Vantagens:**
- Schema evolution
- Bom para streaming
- Interoperabilidade

### CSV (Ingest)

```scala
// Apenas para ingestão inicial
spark.sql("""
  CREATE EXTERNAL TABLE vendas.raw_csv (
    col1 STRING,
    col2 STRING,
    col3 STRING
  )
  USING CSV
  OPTIONS (
    path 's3a://bronze/raw/',
    header 'true',
    inferSchema 'false'
  )
""")
```

## 🔐 Particionamento Estratégico

### Particionamento por Data

```scala
// Particionamento diário
spark.sql("""
  CREATE TABLE vendas.log_eventos (
    evento_id STRING,
    usuario STRING,
    acao STRING,
    timestamp TIMESTAMP
  )
  PARTITIONED BY (dt DATE)
  STORED AS PARQUET
""")

// Inserir com partição automática
spark.sql("""
  INSERT INTO vendas.log_eventos
  PARTITION (dt)
  SELECT 
    evento_id,
    usuario,
    acao,
    timestamp,
    CAST(timestamp AS DATE) as dt
  FROM vendas.eventos_raw
""")
```

### Particionamento Hierárquico

```scala
// Ano → Mês → Dia
spark.sql("""
  CREATE TABLE vendas.transacoes (
    id STRING,
    valor DECIMAL(10,2),
    tipo STRING
  )
  PARTITIONED BY (ano INT, mes INT, dia INT)
  STORED AS PARQUET
""")
```

### Bucketing (Clustering)

```scala
// Bucketing para joins eficientes
spark.sql("""
  CREATE TABLE vendas.vendas_bucketed (
    venda_id STRING,
    cliente_id STRING,
    valor DECIMAL(10,2),
    data DATE
  )
  CLUSTERED BY (cliente_id) INTO 50 BUCKETS
  STORED AS PARQUET
""")
```

## 🔍 Consultar Metadados Internos

### Consultar PostgreSQL Diretamente

```bash
# Conectar ao PostgreSQL
docker compose exec postgres psql -U postgres -d hive_metastore
```

```sql
-- Listar todos os databases
SELECT * FROM "DBS";

-- Listar todas as tabelas
SELECT 
    d."NAME" as database_name,
    t."TBL_NAME" as table_name,
    t."TBL_TYPE" as table_type,
    s."LOCATION" as location
FROM "TBLS" t
JOIN "DBS" d ON t."DB_ID" = d."DB_ID"
JOIN "SDS" s ON t."SD_ID" = s."SD_ID";

-- Ver colunas de uma tabela
SELECT 
    c."COLUMN_NAME",
    c."TYPE_NAME",
    c."INTEGER_IDX" as position
FROM "COLUMNS_V2" c
JOIN "SDS" s ON c."CD_ID" = s."CD_ID"
JOIN "TBLS" t ON t."SD_ID" = s."SD_ID"
WHERE t."TBL_NAME" = 'vendas_silver'
ORDER BY c."INTEGER_IDX";

-- Ver partições
SELECT 
    p."PART_NAME",
    s."LOCATION"
FROM "PARTITIONS" p
JOIN "SDS" s ON p."SD_ID" = s."SD_ID"
JOIN "TBLS" t ON p."TBL_ID" = t."TBL_ID"
WHERE t."TBL_NAME" = 'vendas_particionada';
```

## 🛠️ Manutenção do Catálogo

### Backup do Metastore

```bash
# Backup do PostgreSQL
docker compose exec postgres pg_dump -U postgres hive_metastore > metastore_backup.sql

# Restore
docker compose exec -T postgres psql -U postgres hive_metastore < metastore_backup.sql
```

### Limpeza de Tabelas Órfãs

```sql
-- Identificar tabelas sem dados
SELECT 
    t."TBL_NAME",
    s."LOCATION"
FROM "TBLS" t
JOIN "SDS" s ON t."SD_ID" = s."SD_ID"
WHERE s."LOCATION" LIKE 's3a://%';
```

### Validar Consistência

```scala
// Spark: Verificar tabelas quebradas
val databases = spark.sql("SHOW DATABASES").collect()
databases.foreach { db =>
  val dbName = db.getString(0)
  println(s"Checking database: $dbName")
  
  try {
    spark.sql(s"USE $dbName")
    val tables = spark.sql("SHOW TABLES").collect()
    
    tables.foreach { table =>
      val tableName = table.getString(1)
      try {
        spark.sql(s"SELECT COUNT(*) FROM $tableName").show()
        println(s"✓ $dbName.$tableName OK")
      } catch {
        case e: Exception =>
          println(s"✗ $dbName.$tableName ERROR: ${e.getMessage}")
      }
    }
  } catch {
    case e: Exception =>
      println(s"✗ Database $dbName ERROR: ${e.getMessage}")
  }
}
```

## 📋 Schema Evolution

### Adicionar Colunas

```sql
-- Trino: Adicionar coluna
ALTER TABLE hive.vendas.produtos 
ADD COLUMN estoque INT;

-- Spark: Com valor default
spark.sql("""
  ALTER TABLE vendas.produtos
  ADD COLUMNS (estoque INT COMMENT 'Quantidade em estoque')
""")
```

### Modificar Tipos

```scala
// Trocar tipo de coluna (criar nova tabela)
spark.sql("""
  CREATE TABLE vendas.produtos_v2 AS
  SELECT 
    id,
    nome,
    categoria,
    CAST(preco AS DOUBLE) as preco,
    data_criacao
  FROM vendas.produtos
""")

// Dropar antiga e renomear
spark.sql("DROP TABLE vendas.produtos")
spark.sql("ALTER TABLE vendas.produtos_v2 RENAME TO vendas.produtos")
```

## 🎯 Best Practices

### 1. Nomenclatura
```
✓ databases: minúsculo, underscores (vendas_online)
✓ tabelas: minúsculo, underscores (vendas_silver)
✓ colunas: minúsculo, underscores (data_venda)
✗ evitar: CamelCase, espaços, caracteres especiais
```

### 2. Particionamento
```
✓ Particione por data se queries filtram por período
✓ Use granularidade adequada (dia/mês/ano)
✓ Evite muitas partições pequenas (< 1GB cada)
✗ Não particione tabelas pequenas (< 1GB total)
```

### 3. Formatos
```
✓ Parquet/ORC para dados analíticos
✓ Compressão Snappy (balanço speed/ratio)
✓ Schema explícito (não inferir)
✗ CSV apenas para ingestão inicial
```

### 4. Organização
```
vendas/              # Database
├── raw/             # Bronze (tabelas externas)
├── staging/         # Silver (tabelas gerenciadas)
└── analytics/       # Gold (tabelas agregadas)
```

## 🆘 Troubleshooting

### Erro: "Table not found"
```bash
# Verificar se metastore está rodando
docker compose ps hive-metastore

# Verificar logs
docker compose logs hive-metastore

# Reparar tabela
spark.sql("MSCK REPAIR TABLE vendas.tabela_nome")
```

### Partições não aparecem
```scala
// Atualizar partições automaticamente
spark.sql("MSCK REPAIR TABLE vendas.vendas_particionada")

// Ou adicionar manualmente
spark.sql("""
  ALTER TABLE vendas.vendas_particionada
  ADD PARTITION (ano=2025, mes=1)
  LOCATION 's3a://silver/vendas/particionada/ano=2025/mes=1/'
""")
```

### Schema desatualizado
```scala
// Refresh cache
spark.sql("REFRESH TABLE vendas.produtos")

// Invalidar cache
spark.catalog.refreshTable("vendas.produtos")
```

## 🎓 Próximos Passos

- **APIs REST/JDBC:** `07-apis-rest-jdbc.md`
- **Casos de uso práticos:** `08-casos-uso-praticos.md`
- **Otimização de queries:** Documentação Trino/Spark
