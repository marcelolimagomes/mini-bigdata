# Suporte S3A no Trino

## 📋 Visão Geral

O Trino foi configurado com suporte completo aos protocolos **S3** e **S3A** para acesso ao MinIO.

## 🔧 Protocolos Suportados

### 1. **s3://** - Protocolo Nativo MinIO/AWS S3
- Implementação nativa do Trino para S3
- Melhor performance para operações básicas
- Uso recomendado para queries simples

### 2. **s3a://** - Protocolo Hadoop S3A FileSystem
- Implementação Hadoop para S3
- Compatível com ferramentas do ecossistema Hadoop (Spark, Hive, etc.)
- Necessário para interoperabilidade com jobs Spark
- Suporte completo a multipart uploads

## 📦 JARs Instalados

O container Trino customizado (`mini-bigdata-trino:435-s3a`) inclui:

```
/usr/lib/trino/plugin/hive/
├── hadoop-aws-3.3.6.jar      # ✅ Cliente S3A
├── hadoop-common-3.3.6.jar   # ✅ Utilitários Hadoop
├── hadoop-auth-3.3.6.jar     # ✅ Autenticação
└── parquet-hadoop-1.13.1.jar # ✅ Parquet support
```

## ⚙️ Configuração

### Arquivos de Configuração

O suporte S3A é configurado através de dois arquivos:

#### 1. Catálogo Hive (`config/trino/catalog/hive.properties`)

```properties
connector.name=hive
hive.metastore.uri=thrift://hive-metastore:9083

# Configurações S3/MinIO - Suporte s3:// e s3a://
hive.s3.endpoint=http://minio:9000
hive.s3.path-style-access=true
hive.s3.aws-access-key=minioadmin
hive.s3.aws-secret-key=minioadmin123
hive.s3.ssl.enabled=false

# Habilitar FileSystem nativo do Hadoop para S3A
hive.config.resources=/etc/trino/core-site.xml

# Permissões de escrita
hive.non-managed-table-writes-enabled=true
hive.allow-drop-table=true
```

#### 2. Configuração Hadoop (`config/trino/core-site.xml`)

```xml
<?xml version="1.0" encoding="UTF-8"?>
<configuration>
    <!-- S3A FileSystem Implementation -->
    <property>
        <name>fs.s3a.impl</name>
        <value>org.apache.hadoop.fs.s3a.S3AFileSystem</value>
    </property>

    <!-- MinIO Endpoint -->
    <property>
        <name>fs.s3a.endpoint</name>
        <value>http://minio:9000</value>
    </property>

    <!-- Credenciais -->
    <property>
        <name>fs.s3a.access.key</name>
        <value>minioadmin</value>
    </property>
    <property>
        <name>fs.s3a.secret.key</name>
        <value>minioadmin123</value>
    </property>

    <!-- Path Style Access -->
    <property>
        <name>fs.s3a.path.style.access</name>
        <value>true</value>
    </property>

    <!-- SSL Desabilitado para MinIO local -->
    <property>
        <name>fs.s3a.connection.ssl.enabled</name>
        <value>false</value>
    </property>

    <!-- Performance tuning -->
    <property>
        <name>fs.s3a.fast.upload</name>
        <value>true</value>
    </property>
    <property>
        <name>fs.s3a.multipart.size</name>
        <value>104857600</value> <!-- 100MB -->
    </property>
</configuration>
```

> ⚠️ **Importante**: As configurações S3A devem estar no `core-site.xml`, **não** no `hive.properties`. Propriedades como `fs.s3a.*` não são reconhecidas diretamente pelo Trino e causarão erro "Configuration property was not used".

## 💡 Exemplos de Uso

### Criar Tabela com S3A

```sql
CREATE TABLE hive.default.sales_data (
    id BIGINT,
    product VARCHAR,
    amount DECIMAL(10,2),
    sale_date DATE
)
WITH (
    external_location = 's3a://silver/sales/data/',
    format = 'PARQUET'
);
```

### Criar Tabela com S3 Nativo

```sql
CREATE TABLE hive.default.customer_data (
    customer_id BIGINT,
    name VARCHAR,
    email VARCHAR
)
WITH (
    external_location = 's3://gold/customers/data/',
    format = 'PARQUET'
);
```

### Query em Dados S3A

```sql
-- Listar arquivos usando S3A
SELECT 
    "$path",
    "$file_size",
    "$file_modified_time"
FROM hive.default."sales_data$files"
WHERE "$path" LIKE 's3a://%';

-- Query normal
SELECT 
    product,
    SUM(amount) as total_revenue
FROM hive.default.sales_data
WHERE sale_date >= DATE '2025-01-01'
GROUP BY product
ORDER BY total_revenue DESC;
```

## 🔄 Interoperabilidade Spark ↔ Trino

### Spark escreve com S3A
```python
from pyspark.sql import SparkSession

spark = SparkSession.builder \
    .config("spark.hadoop.fs.s3a.endpoint", "http://minio:9000") \
    .config("spark.hadoop.fs.s3a.access.key", "minioadmin") \
    .config("spark.hadoop.fs.s3a.secret.key", "minioadmin123") \
    .getOrCreate()

# Escrever dados
df.write.mode('overwrite').parquet("s3a://silver/sales/data/")
```

### Trino lê com S3A
```sql
-- Criar tabela externa apontando para dados escritos pelo Spark
CREATE TABLE hive.default.sales_data (
    id BIGINT,
    product VARCHAR,
    amount DECIMAL(10,2)
)
WITH (
    external_location = 's3a://silver/sales/data/',
    format = 'PARQUET'
);

-- Query nos dados
SELECT * FROM hive.default.sales_data LIMIT 10;
```

## 🧪 Testes

### Testar Instalação

```bash
# Executar script de teste
./scripts/shell/test-trino-s3a.sh
```

Saída esperada:
```
✓ hadoop-aws-3.3.6.jar (suporte S3A)
✓ hadoop-common-3.3.6.jar
✓ hadoop-auth-3.3.6.jar

Protocolos suportados:
  ✓ s3://   (MinIO nativo)
  ✓ s3a://  (Hadoop S3A FileSystem)
```

### Testar Query S3A

```sql
-- No Trino CLI ou UI (http://localhost:8085)
SHOW SCHEMAS FROM hive;
SHOW TABLES FROM hive.default;
```

## 🔨 Rebuild

Se precisar rebuildar o Trino com novos JARs:

```bash
./scripts/shell/rebuild-trino.sh
```

## 📊 Quando Usar Cada Protocolo

| Cenário | Protocolo Recomendado | Motivo |
|---------|----------------------|---------|
| Query simples no Trino | `s3://` | Melhor performance nativa |
| Dados escritos pelo Spark | `s3a://` | Compatibilidade Hadoop |
| Interoperabilidade Hive/Spark/Trino | `s3a://` | Padrão do ecossistema |
| Upload/Download MinIO direto | `s3://` | Protocolo nativo S3 |
| Multipart uploads grandes | `s3a://` | Melhor suporte Hadoop |

## 🐛 Troubleshooting

### Erro: "Configuration property 'fs.s3a.*' was not used"

❌ **Causa**: Propriedades S3A colocadas diretamente no `hive.properties`

✅ **Solução**: Mover propriedades `fs.s3a.*` para `core-site.xml` e referenciar via:
```properties
hive.config.resources=/etc/trino/core-site.xml
```

### Erro: "No FileSystem for scheme: s3a"

✅ **Solução**: 
1. Verificar se JARs Hadoop estão instalados: `docker compose exec trino sh -c "ls /usr/lib/trino/plugin/hive/ | grep hadoop"`
2. Rebuildar Trino: `./scripts/shell/rebuild-trino.sh`
3. Verificar se `core-site.xml` está sendo copiado no Dockerfile

### Erro: "Access Denied" ou "403 Forbidden"

Verificar credenciais em `config/trino/catalog/hive.properties`:
```properties
fs.s3a.access.key=minioadmin
fs.s3a.secret.key=minioadmin123
```

### Erro: "Connection refused" ao MinIO

Verificar endpoint:
```properties
fs.s3a.endpoint=http://minio:9000  # ✅ Correto
# fs.s3a.endpoint=http://localhost:9000  # ❌ Errado (use 'minio')
```

### Verificar logs do Trino

```bash
docker compose logs trino | tail -50
```

## 📚 Referências

- [Trino S3 Connector](https://trino.io/docs/current/connector/hive.html#amazon-s3-configuration)
- [Hadoop S3A FileSystem](https://hadoop.apache.org/docs/stable/hadoop-aws/tools/hadoop-aws/index.html)
- [MinIO Documentation](https://min.io/docs/minio/linux/index.html)

## ✅ Status

- ✅ Trino 435 com Hadoop AWS 3.3.6
- ✅ Suporte S3 nativo
- ✅ Suporte S3A (Hadoop FileSystem)
- ✅ Configuração MinIO
- ✅ Interoperabilidade Spark ↔ Trino
- ✅ Scripts de teste e validação
