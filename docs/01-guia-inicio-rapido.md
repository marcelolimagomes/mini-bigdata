# 🚀 Guia de Início Rápido - Stack Big Data

## 📋 Pré-requisitos

Antes de começar, certifique-se de que a stack está rodando:

```bash
cd /home/marcelo/central/mini-bigdata
docker compose ps
```

Todos os serviços devem estar com status `Up` ou `healthy`.

## 🌐 Acessando as Interfaces

### MinIO (Storage S3)
- **URL:** http://localhost:9001
- **Usuário:** `minioadmin`
- **Senha:** `minioadmin123`
- **Uso:** Upload de arquivos, gerenciamento de buckets

### Apache Airflow (Orquestração)
- **URL:** http://localhost:8080
- **Usuário:** `airflow`
- **Senha:** `airflow`
- **Uso:** Criar e agendar pipelines ETL

### Apache Superset (BI/Dashboards)
- **URL:** http://localhost:8088
- **Usuário:** `admin`
- **Senha:** `admin`
- **Uso:** Criar dashboards e visualizações

### Trino (Query Engine)
- **URL:** http://localhost:8085
- **Usuário:** `trino`
- **Uso:** Executar consultas SQL nos dados

### Spark UI
- **Master:** http://localhost:8081
- **Worker:** http://localhost:8082
- **Uso:** Monitorar jobs Spark

## 🎯 Primeiro Projeto: Pipeline ETL Simples

### Passo 1: Upload de Dados no MinIO

1. Acesse MinIO Console (http://localhost:9001)
2. Navegue até o bucket `bronze`
3. Clique em "Upload" e envie um arquivo CSV

**Exemplo de arquivo CSV (`vendas.csv`):**
```csv
data,produto,quantidade,valor
2025-01-01,Notebook,5,5000.00
2025-01-02,Mouse,10,250.00
2025-01-03,Teclado,8,800.00
```

### Passo 2: Verificar Buckets Disponíveis

Os buckets criados automaticamente seguem a arquitetura Medallion:
- **bronze:** Dados brutos (raw)
- **silver:** Dados limpos e transformados
- **gold:** Dados agregados e prontos para análise
- **warehouse:** Dados para Data Warehouse
- **raw:** Dados temporários

### Passo 3: Próximos Passos

Continue para os guias específicos:
- **Pipeline ETL:** `02-criando-pipelines-airflow.md`
- **Processamento Spark:** `03-processamento-spark.md`
- **Consultas SQL:** `04-consultas-trino.md`
- **Dashboards BI:** `05-criando-dashboards-superset.md`

## 🔧 Comandos Úteis

### Verificar Status da Stack
```bash
docker compose ps
```

### Ver Logs de um Serviço
```bash
docker compose logs -f airflow-webserver
docker compose logs -f spark-master
```

### Reiniciar um Serviço
```bash
docker compose restart airflow-webserver
```

### Parar a Stack
```bash
docker compose down
```

### Iniciar a Stack
```bash
docker compose up -d
```

## 📊 Arquitetura dos Dados

```
┌─────────────┐
│   Fonte     │ → Upload manual ou API
└─────────────┘
      ↓
┌─────────────┐
│   BRONZE    │ → Dados brutos (CSV, JSON, etc)
│   (MinIO)   │
└─────────────┘
      ↓
┌─────────────┐
│    ETL      │ → Airflow + Spark
│ (Transform) │
└─────────────┘
      ↓
┌─────────────┐
│   SILVER    │ → Dados limpos e validados
│   (MinIO)   │
└─────────────┘
      ↓
┌─────────────┐
│    ETL      │ → Agregações e métricas
│ (Aggregate) │
└─────────────┘
      ↓
┌─────────────┐
│    GOLD     │ → Dados prontos para análise
│   (MinIO)   │
└─────────────┘
      ↓
┌─────────────┐
│   Trino     │ → Consultas SQL
└─────────────┘
      ↓
┌─────────────┐
│  Superset   │ → Dashboards e visualizações
└─────────────┘
```

## 🎓 Próximos Passos

1. ✅ **Concluído:** Stack inicializada e acessível
2. 📖 **Próximo:** Leia `02-criando-pipelines-airflow.md`
3. 🔨 **Prática:** Crie seu primeiro pipeline ETL
4. 📊 **Visualize:** Monte dashboards no Superset

## 🆘 Suporte

- **Documentação completa:** Pasta `./docs`
- **Exemplos de código:** Pasta `./examples`
- **Troubleshooting:** `TROUBLESHOOTING.md`
- **Status da stack:** `STATUS.md`
