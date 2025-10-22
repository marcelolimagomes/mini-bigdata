# 📚 Documentação - Mini Big Data Stack

## 🎯 Bem-vindo!

Esta é a documentação completa da stack Big Data enxuta para desenvolvimento de pipelines ETL e dashboards BI.

## 📖 Guias Disponíveis

### 🚀 [01 - Guia de Início Rápido](./01-guia-inicio-rapido.md)
Comece aqui! Aprenda sobre a arquitetura, acesse os serviços e crie seu primeiro projeto.

**Você vai aprender:**
- Visão geral da arquitetura (MinIO, Spark, Trino, Airflow, Superset)
- URLs de acesso e credenciais
- Conceito de camadas Bronze → Silver → Gold
- Criar seu primeiro pipeline ETL simples

**Tempo:** 30 minutos

---

### 🔄 [02 - Criando Pipelines com Airflow](./02-criando-pipelines-airflow.md)
Domine a orquestração de pipelines ETL com Apache Airflow.

**Você vai aprender:**
- Estrutura de DAGs (Directed Acyclic Graphs)
- Criar pipeline Bronze → Silver → Gold completo
- Integrar Airflow com Spark
- Agendar execuções e monitorar pipelines
- Usar XCom para passar dados entre tasks

**Tempo:** 1-2 horas

---

### ⚡ [03 - Processamento com Spark](./03-processamento-spark.md)
Desenvolva jobs de processamento distribuído com Apache Spark.

**Você vai aprender:**
- Escrever jobs PySpark
- Conectar Spark ao MinIO (S3)
- Transformações e agregações
- Validação de qualidade de dados
- Executar jobs via spark-submit, Airflow ou shell

**Tempo:** 1-2 horas

---

### 🔍 [04 - Consultas SQL com Trino](./04-consultas-trino.md)
Execute queries SQL distribuídas sobre o Data Lake.

**Você vai aprender:**
- Conectar ao Trino (CLI, Python, SQLAlchemy)
- Criar schemas e tabelas
- Queries SQL avançadas (window functions, CTEs, joins)
- Otimização de performance
- Análises analíticas complexas

**Tempo:** 1 hora

---

### 📊 [05 - Criando Dashboards com Superset](./05-criando-dashboards-superset.md)
Construa visualizações e dashboards interativos de BI.

**Você vai aprender:**
- Conectar Superset ao Trino
- Criar diversos tipos de gráficos (linha, barra, pizza, KPIs, heatmap)
- Montar dashboards completos com filtros
- SQL customizado e datasets virtuais
- Agendar envio de relatórios

**Tempo:** 1-2 horas

---

### 🗄️ [06 - Catálogo Hive Metastore](./06-catalogo-hive-metastore.md)
Gerencie o catálogo de metadados central do Data Lake.

**Você vai aprender:**
- Criar databases e tabelas
- Tabelas gerenciadas vs externas
- Particionamento estratégico
- Schema evolution
- Formatos de arquivo (Parquet, ORC, Avro)
- Consultar metadados internos

**Tempo:** 1 hora

---

### 🔌 [07 - APIs REST e JDBC](./07-apis-rest-jdbc.md)
Acesse dados programaticamente via APIs e JDBC.

**Você vai aprender:**
- Conectar via JDBC (Java, Python, R)
- Usar Trino REST API
- Integrar com Airflow REST API
- Acessar Superset API
- Usar MinIO S3 API (boto3)
- Criar APIs customizadas (Flask, Express)

**Tempo:** 1-2 horas

---

## 🎓 Trilhas de Aprendizado

### 👨‍💻 Desenvolvedor Iniciante
1. **Início Rápido** → Entenda a arquitetura
2. **Consultas Trino** → Execute SQL básico
3. **Dashboards Superset** → Visualize dados existentes

**Tempo total:** ~3 horas

---

### 🧑‍🔧 Engenheiro de Dados
1. **Início Rápido** → Visão geral
2. **Pipelines Airflow** → Orquestração ETL
3. **Processamento Spark** → Transformações
4. **Catálogo Hive** → Gestão de metadados
5. **APIs REST/JDBC** → Integração programática

**Tempo total:** 6-8 horas

---

### 📊 Analista de BI
1. **Início Rápido** → Arquitetura básica
2. **Consultas Trino** → SQL avançado
3. **Dashboards Superset** → Visualizações
4. **APIs REST/JDBC** → Automatização

**Tempo total:** 4-5 horas

---

## 🏗️ Arquitetura da Stack

```
┌─────────────────────────────────────────────────────┐
│                    Camada BI                        │
│  📊 Apache Superset (Dashboards e Visualizações)   │
└────────────────────┬────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────┐
│                Camada de Query                      │
│      🔍 Trino (SQL Engine Distribuído)              │
└────────────────────┬────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────┐
│               Camada de Catálogo                    │
│    🗄️ Hive Metastore (Schemas, Tabelas, Partições) │
└────────────────────┬────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────┐
│              Camada de Storage                      │
│         🪣 MinIO (Object Storage S3)                │
│    [bronze/] [silver/] [gold/] [warehouse/]        │
└────────────────────┬────────────────────────────────┘
                     │
          ┌──────────┴──────────┐
          ▼                     ▼
┌──────────────────┐  ┌──────────────────┐
│ Orquestração ETL │  │  Processamento   │
│ 🔄 Apache Airflow│  │ ⚡ Apache Spark  │
└──────────────────┘  └──────────────────┘
```

## 🌐 URLs de Acesso Rápido

| Serviço | URL | Usuário | Senha |
|---------|-----|---------|-------|
| **MinIO** | http://localhost:9001 | `minioadmin` | `minioadmin` |
| **Airflow** | http://localhost:8080 | `airflow` | `airflow` |
| **Trino** | http://localhost:8081 | `trino` | - |
| **Superset** | http://localhost:8088 | `admin` | `admin` |
| **Spark Master** | http://localhost:8082 | - | - |

## 📂 Estrutura de Pastas

```
mini-bigdata/
├── docker-compose.yml          # Orquestração dos containers
├── config/
│   ├── hive/                   # Configuração Hive Metastore
│   │   └── Dockerfile
│   ├── superset/               # Scripts Superset
│   │   └── init-superset.sh
│   └── airflow/
│       └── dags/               # DAGs do Airflow
├── docs/                       # 📚 VOCÊ ESTÁ AQUI!
│   ├── README.md
│   ├── 01-guia-inicio-rapido.md
│   ├── 02-criando-pipelines-airflow.md
│   ├── 03-processamento-spark.md
│   ├── 04-consultas-trino.md
│   ├── 05-criando-dashboards-superset.md
│   ├── 06-catalogo-hive-metastore.md
│   ├── 07-apis-rest-jdbc.md
│   └── senhas.txt
└── data/                       # Dados de exemplo (opcional)
```

## 🚀 Quick Start

```bash
# 1. Subir a stack completa
docker compose up -d

# 2. Verificar serviços
docker compose ps

# 3. Acessar Airflow
# http://localhost:8080 (airflow/airflow)

# 4. Acessar Superset
# http://localhost:8088 (admin/admin)

# 5. Ver logs (se necessário)
docker compose logs -f <serviço>
```

## 🔧 Comandos Úteis

### Docker
```bash
# Parar todos os serviços
docker compose down

# Recriar um serviço específico
docker compose up -d --force-recreate <serviço>

# Ver logs de um serviço
docker compose logs -f <serviço>

# Executar comando em container
docker compose exec <serviço> bash
```

### Spark
```bash
# Abrir Spark Shell
docker compose exec spark-master spark-shell

# PySpark
docker compose exec spark-master pyspark

# Submeter job
docker compose exec spark-master spark-submit \
  --master spark://spark-master:7077 \
  /path/to/job.py
```

### Trino
```bash
# Trino CLI
docker compose exec trino trino --catalog hive --schema default
```

### PostgreSQL
```bash
# Acessar banco Hive Metastore
docker compose exec postgres psql -U postgres -d hive_metastore

# Acessar banco Airflow
docker compose exec postgres psql -U postgres -d airflow_db

# Acessar banco Superset
docker compose exec postgres psql -U postgres -d superset_db
```

## 🆘 Troubleshooting

### Serviço não sobe
```bash
# Ver logs detalhados
docker compose logs <serviço>

# Recriar volume e container
docker compose down
docker compose up -d --force-recreate <serviço>
```

### Falta de espaço
```bash
# Verificar espaço em disco
df -h /media/marcelo/dados1/bigdata-docker/

# Limpar dados antigos (cuidado!)
docker system prune -a --volumes
```

### Erro de conexão entre serviços
```bash
# Verificar rede Docker
docker network inspect mini-bigdata_default

# Reiniciar stack completa
docker compose down
docker compose up -d
```

### Airflow: DAG não aparece
```bash
# Verificar logs do scheduler
docker compose logs airflow-scheduler

# Restartar scheduler
docker compose restart airflow-scheduler
```

## 📊 Exemplo Completo: Pipeline ETL → BI

### 1. Dados Bronze (Raw)
```python
# Ingerir CSV para MinIO bronze/
import pandas as pd
df = pd.read_csv('vendas.csv')
df.to_csv('s3://bronze/vendas/raw.csv')
```

### 2. Processar → Silver (Airflow + Spark)
```python
# DAG Airflow executando job Spark
# Limpa dados, valida, converte para Parquet
```

### 3. Agregar → Gold (Spark)
```python
# Agregações e métricas de negócio
# Tabelas prontas para BI
```

### 4. Catalogar (Hive Metastore)
```sql
CREATE EXTERNAL TABLE vendas.vendas_gold (...)
LOCATION 's3a://gold/vendas/';
```

### 5. Consultar (Trino)
```sql
SELECT produto, SUM(receita) 
FROM hive.vendas.vendas_gold
GROUP BY produto;
```

### 6. Visualizar (Superset)
```
Dashboard com gráficos de receita, tendências, KPIs
```

## 🎯 Boas Práticas

### 📁 Organização de Dados
- **Bronze:** Dados raw, formato original
- **Silver:** Dados limpos, validados, Parquet
- **Gold:** Dados agregados, prontos para BI

### 🔄 ETL
- Use Airflow para orquestração
- Spark para processamento pesado
- Valide qualidade dos dados
- Registre no Hive Metastore

### 📊 BI
- Crie datasets no Superset a partir do Trino
- Use SQL Lab para queries ad-hoc
- Dashboards com filtros interativos

### 🛡️ Segurança
- Mude senhas padrão em produção
- Use autenticação (OAuth, LDAP)
- Restrinja acesso via firewall

## 📞 Suporte

### Documentação Oficial
- [Apache Airflow](https://airflow.apache.org/docs/)
- [Apache Spark](https://spark.apache.org/docs/latest/)
- [Trino](https://trino.io/docs/current/)
- [Apache Superset](https://superset.apache.org/docs/intro)
- [MinIO](https://min.io/docs/minio/linux/index.html)
- [Hive](https://cwiki.apache.org/confluence/display/Hive/Home)

### Issues Conhecidos
Veja `senhas.txt` para troubleshooting de autenticação.

## 🎓 Próximos Passos

1. ✅ Leia o **Guia de Início Rápido**
2. ✅ Crie seu primeiro pipeline no **Airflow**
3. ✅ Processe dados com **Spark**
4. ✅ Consulte via **Trino**
5. ✅ Construa dashboards no **Superset**

**Boa jornada no mundo Big Data! 🚀**
