# 📋 Índice Completo da Documentação

## 🎯 Documentação Mini Big Data Stack

Documentação completa para desenvolvimento de pipelines ETL e dashboards BI.

---

## 📚 Guias Disponíveis

### 🚀 [README - Visão Geral](./README.md)
**Comece aqui!** Índice principal com acesso rápido, arquitetura e comandos úteis.

---

### 1️⃣ [Guia de Início Rápido](./01-guia-inicio-rapido.md)
- Arquitetura da stack
- URLs e credenciais de acesso
- Conceito Bronze → Silver → Gold
- Primeiro projeto ETL
- **Tempo:** 30 minutos

---

### 2️⃣ [Criando Pipelines com Airflow](./02-criando-pipelines-airflow.md)
- Estrutura de DAGs
- Pipeline ETL completo
- Integração Airflow + Spark
- Scheduling e monitoramento
- XCom e TaskFlow API
- **Tempo:** 1-2 horas

---

### 3️⃣ [Processamento com Spark](./03-processamento-spark.md)
- Jobs PySpark
- Conexão com MinIO (S3)
- Transformações e agregações
- Validação de qualidade
- spark-submit e execução
- **Tempo:** 1-2 horas

---

### 4️⃣ [Consultas SQL com Trino](./04-consultas-trino.md)
- Conexão (CLI, Python, SQLAlchemy)
- Criar schemas e tabelas
- SQL avançado (window, CTEs, joins)
- Otimização de queries
- Análises analíticas
- **Tempo:** 1 hora

---

### 5️⃣ [Dashboards com Superset](./05-criando-dashboards-superset.md)
- Conectar ao Trino
- Tipos de gráficos
- Montar dashboards
- SQL customizado
- Alertas e agendamento
- Embed e APIs
- **Tempo:** 1-2 horas

---

### 6️⃣ [Catálogo Hive Metastore](./06-catalogo-hive-metastore.md)
- Criar databases e tabelas
- Tabelas gerenciadas vs externas
- Particionamento estratégico
- Schema evolution
- Formatos (Parquet, ORC, Avro)
- Consultar metadados
- **Tempo:** 1 hora

---

### 7️⃣ [APIs REST e JDBC](./07-apis-rest-jdbc.md)
- JDBC (Java, Python, R)
- Trino REST API
- Airflow REST API
- Superset REST API
- MinIO S3 API
- Exemplos Flask/Express
- **Tempo:** 1-2 horas

---

### 8️⃣ [Casos de Uso Práticos](./08-casos-uso-praticos.md)
- E-commerce: Análise de vendas
- Logs: Monitoramento de aplicação
- Bancos: Detecção de fraude
- IoT: Telemetria de sensores
- Educação: Análise de aprendizado
- Pipelines completos end-to-end
- **Tempo:** Referência conforme necessidade

---

## 🎓 Trilhas de Aprendizado Recomendadas

### 👨‍💻 **Desenvolvedor Iniciante**
```
01. Guia de Início Rápido
    ↓
04. Consultas SQL com Trino
    ↓
05. Dashboards com Superset
```
**Tempo total:** ~3 horas  
**Objetivo:** Visualizar e consultar dados existentes

---

### 🧑‍🔧 **Engenheiro de Dados**
```
01. Guia de Início Rápido
    ↓
02. Criando Pipelines com Airflow
    ↓
03. Processamento com Spark
    ↓
06. Catálogo Hive Metastore
    ↓
07. APIs REST e JDBC
    ↓
08. Casos de Uso Práticos
```
**Tempo total:** 6-8 horas  
**Objetivo:** Criar pipelines ETL completos

---

### 📊 **Analista de BI**
```
01. Guia de Início Rápido
    ↓
04. Consultas SQL com Trino
    ↓
05. Dashboards com Superset
    ↓
07. APIs REST e JDBC (seção Superset)
```
**Tempo total:** 4-5 horas  
**Objetivo:** Criar dashboards e análises

---

### 🏗️ **Arquiteto de Dados**
```
Ler todos os guias na ordem (01 a 08)
```
**Tempo total:** 10-12 horas  
**Objetivo:** Domínio completo da stack

---

## 🔍 Busca Rápida por Tópico

### 🪣 **MinIO / S3**
- [Início Rápido](./01-guia-inicio-rapido.md#-minio-object-storage) - Conceitos básicos
- [Processamento Spark](./03-processamento-spark.md#-configuração-minio-s3) - Conexão S3A
- [APIs REST/JDBC](./07-apis-rest-jdbc.md#-minio-s3-api) - boto3 e MinIO SDK

### 🔄 **Apache Airflow**
- [Pipelines Airflow](./02-criando-pipelines-airflow.md) - Guia completo
- [APIs REST/JDBC](./07-apis-rest-jdbc.md#-apache-airflow-rest-api) - REST API
- [Casos de Uso](./08-casos-uso-praticos.md#-caso-1-e-commerce---análise-de-vendas) - Exemplos práticos

### ⚡ **Apache Spark**
- [Processamento Spark](./03-processamento-spark.md) - Guia completo
- [Pipelines Airflow](./02-criando-pipelines-airflow.md#-integração-com-spark) - Integração
- [Casos de Uso](./08-casos-uso-praticos.md) - Jobs completos

### 🔍 **Trino**
- [Consultas SQL](./04-consultas-trino.md) - Guia completo
- [APIs REST/JDBC](./07-apis-rest-jdbc.md#-trino-jdbc) - JDBC e REST
- [Dashboards Superset](./05-criando-dashboards-superset.md#-conectar-ao-trino) - Conexão BI

### 📊 **Apache Superset**
- [Dashboards](./05-criando-dashboards-superset.md) - Guia completo
- [APIs REST/JDBC](./07-apis-rest-jdbc.md#-apache-superset-rest-api) - REST API

### 🗄️ **Hive Metastore**
- [Catálogo Hive](./06-catalogo-hive-metastore.md) - Guia completo
- [Consultas SQL](./04-consultas-trino.md#-gerenciamento-de-catálogos) - Uso via Trino
- [Processamento Spark](./03-processamento-spark.md#-integração-com-hive-metastore) - Registro de tabelas

---

## 🛠️ Comandos Rápidos

### Docker
```bash
# Subir stack
docker compose up -d

# Ver logs
docker compose logs -f <serviço>

# Reiniciar serviço
docker compose restart <serviço>

# Parar tudo
docker compose down
```

### Spark
```bash
# Shell interativo
docker compose exec spark-master spark-shell

# PySpark
docker compose exec spark-master pyspark

# Submeter job
docker compose exec spark-master spark-submit /path/to/job.py
```

### Trino
```bash
# CLI
docker compose exec trino trino --catalog hive --schema default
```

### PostgreSQL
```bash
# Hive Metastore
docker compose exec postgres psql -U postgres -d hive_metastore

# Airflow
docker compose exec postgres psql -U postgres -d airflow_db

# Superset
docker compose exec postgres psql -U postgres -d superset_db
```

---

## 🌐 URLs de Acesso

| Serviço | URL | Usuário | Senha |
|---------|-----|---------|-------|
| **MinIO Console** | http://localhost:9001 | `minioadmin` | `minioadmin` |
| **Airflow Web** | http://localhost:8080 | `airflow` | `airflow` |
| **Trino Web** | http://localhost:8081 | `trino` | - |
| **Superset** | http://localhost:8088 | `admin` | `admin` |
| **Spark Master** | http://localhost:8082 | - | - |

---

## 📂 Estrutura de Arquivos

```
docs/
├── README.md                          # 📍 VOCÊ ESTÁ AQUI
├── INDICE.md                          # Este arquivo
├── 01-guia-inicio-rapido.md           # Quick start
├── 02-criando-pipelines-airflow.md    # Airflow DAGs
├── 03-processamento-spark.md          # Spark jobs
├── 04-consultas-trino.md              # SQL queries
├── 05-criando-dashboards-superset.md  # BI dashboards
├── 06-catalogo-hive-metastore.md      # Hive catalog
├── 07-apis-rest-jdbc.md               # APIs e JDBC
├── 08-casos-uso-praticos.md           # Exemplos completos
└── senhas.txt                         # Credenciais
```

---

## 🎯 Fluxo de Trabalho Típico

### 📥 1. Ingestão (Bronze)
```python
# Carregar dados raw para MinIO
df.to_csv('s3://bronze/dados/raw.csv')
```
📖 **Guia:** [Pipelines Airflow](./02-criando-pipelines-airflow.md)

---

### 🧹 2. Limpeza (Silver)
```python
# Spark: Limpar e validar
df_clean = df.dropDuplicates().filter(...)
df_clean.write.parquet('s3a://silver/dados/')
```
📖 **Guia:** [Processamento Spark](./03-processamento-spark.md)

---

### 📊 3. Agregação (Gold)
```python
# Spark: Criar métricas
df_agg = df.groupBy(...).agg(...)
df_agg.write.parquet('s3a://gold/metricas/')
```
📖 **Guia:** [Processamento Spark](./03-processamento-spark.md)

---

### 🗄️ 4. Catalogar
```sql
-- Trino: Registrar no Hive
CREATE TABLE hive.schema.tabela (...)
WITH (external_location = 's3a://gold/metricas/')
```
📖 **Guia:** [Catálogo Hive](./06-catalogo-hive-metastore.md)

---

### 🔍 5. Consultar
```sql
-- Trino: Análises SQL
SELECT produto, SUM(receita) 
FROM hive.vendas.metricas
GROUP BY produto
```
📖 **Guia:** [Consultas SQL](./04-consultas-trino.md)

---

### 📈 6. Visualizar
```
Superset: Criar gráficos e dashboards
Dataset → Chart → Dashboard
```
📖 **Guia:** [Dashboards Superset](./05-criando-dashboards-superset.md)

---

## 🆘 Troubleshooting Rápido

| Problema | Solução | Guia |
|----------|---------|------|
| Serviço não sobe | `docker compose logs <serviço>` | [README](./README.md#-troubleshooting) |
| Airflow: DAG não aparece | Verificar logs do scheduler | [Pipelines](./02-criando-pipelines-airflow.md#-troubleshooting) |
| Spark: Erro S3A | Verificar credenciais MinIO | [Spark](./03-processamento-spark.md#-configuração-minio-s3) |
| Trino: Table not found | `MSCK REPAIR TABLE` | [Hive](./06-catalogo-hive-metastore.md#-troubleshooting) |
| Superset: Não conecta | Verificar URI do Trino | [Superset](./05-criando-dashboards-superset.md#-conectar-ao-trino) |

---

## 📚 Documentação Oficial

- [Apache Airflow](https://airflow.apache.org/docs/)
- [Apache Spark](https://spark.apache.org/docs/latest/)
- [Trino](https://trino.io/docs/current/)
- [Apache Superset](https://superset.apache.org/docs/intro)
- [MinIO](https://min.io/docs/minio/linux/index.html)
- [Apache Hive](https://cwiki.apache.org/confluence/display/Hive/Home)

---

## ✅ Checklist de Aprendizado

### 🎓 Iniciante
- [ ] Ler Guia de Início Rápido
- [ ] Acessar todos os serviços (MinIO, Airflow, Trino, Superset)
- [ ] Executar consulta SQL no Trino
- [ ] Criar primeiro gráfico no Superset

### 🎓 Intermediário
- [ ] Criar DAG no Airflow
- [ ] Escrever job PySpark
- [ ] Registrar tabela no Hive Metastore
- [ ] Montar dashboard completo no Superset

### 🎓 Avançado
- [ ] Pipeline ETL end-to-end (Bronze → Silver → Gold)
- [ ] Particionamento otimizado
- [ ] Query SQL complexa (window functions, CTEs)
- [ ] Integração via API (REST/JDBC)
- [ ] Implementar caso de uso prático

---

## 🚀 Comece Agora!

1. ✅ Leia o **[README](./README.md)** para visão geral
2. ✅ Siga o **[Guia de Início Rápido](./01-guia-inicio-rapido.md)**
3. ✅ Escolha sua **trilha de aprendizado** acima
4. ✅ Pratique com **[Casos de Uso](./08-casos-uso-praticos.md)**

**Boa jornada no mundo Big Data! 🎉**
