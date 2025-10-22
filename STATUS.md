# 🎯 Status da Stack Big Data - Mini-BigData

**Data de Implantação:** 22/10/2025  
**Versão:** 1.0.0  
**Status:** ✅ **OPERACIONAL**

---

## 📊 Status dos Serviços

| Serviço | Status | Porta | URL de Acesso |
|---------|--------|-------|---------------|
| **PostgreSQL** | 🟢 Healthy | 5432 | `localhost:5432` |
| **MinIO (S3)** | 🟢 Healthy | 9000, 9001 | http://localhost:9001 |
| **Apache Spark Master** | 🟢 Running | 7077, 8081 | http://localhost:8081 |
| **Apache Spark Worker** | 🟢 Running | 8082 | http://localhost:8082 |
| **Apache Hive Metastore** | 🟡 Starting | 9083 | `localhost:9083` |
| **Trino** | 🟢 Healthy | 8085 | http://localhost:8085 |
| **Apache Airflow** | 🟢 Healthy | 8080 | http://localhost:8080 |
| **Apache Superset** | 🟢 Healthy | 8088 | http://localhost:8088 |

---

## 🔐 Credenciais de Acesso

### MinIO (Object Storage)
- **Console:** http://localhost:9001
- **Usuário:** `minioadmin`
- **Senha:** `minioadmin123`
- **Buckets criados:** bronze, silver, gold, warehouse, raw

### Apache Airflow (Orquestração ETL)
- **UI:** http://localhost:8080
- **Usuário:** `airflow`
- **Senha:** `airflow`

### Apache Superset (BI/Dashboards)
- **UI:** http://localhost:8088
- **Usuário:** `admin`
- **Senha:** `admin`

### Trino (Query Engine)
- **UI:** http://localhost:8085
- **Usuário:** `trino`
- **Sem senha**

### PostgreSQL (Banco de Dados)
- **Host:** `localhost:5432`
- **Usuário:** `admin`
- **Senha:** `admin123`
- **Databases:** `airflow`, `superset`, `metastore`

---

## 💾 Armazenamento de Dados

**Localização:** `/media/marcelo/dados1/bigdata-docker/`

```
/media/marcelo/dados1/bigdata-docker/
├── airflow/
│   ├── dags/       # DAGs do Airflow
│   ├── logs/       # Logs do Airflow
│   └── plugins/    # Plugins personalizados
├── hive/           # Warehouse do Hive
├── minio/          # Dados do MinIO (S3)
├── postgres/       # Dados do PostgreSQL
├── spark/
│   ├── master/     # Work directory do Spark Master
│   └── worker/     # Work directory do Spark Worker
├── superset/       # Dados do Superset
└── trino/          # Dados do Trino
```

---

## 🛠️ Ajustes Realizados

### 1. Hive Metastore - Driver PostgreSQL
**Problema:** Imagem oficial não contém driver JDBC do PostgreSQL  
**Solução:** Criado Dockerfile customizado em `config/hive/Dockerfile` que:
- Instala `wget` e `curl`
- Baixa driver PostgreSQL JDBC (42.7.1)
- Configura variáveis de ambiente

### 2. Apache Spark - Imagem Oficial
**Problema:** Imagens Bitnami indisponíveis (manifest unknown)  
**Solução:** Migrado para imagem oficial `apache/spark:3.5.3`

### 3. Apache Airflow - Dependências
**Problema:** Conflito de dependências com protobuf  
**Solução:** Removida variável `_PIP_ADDITIONAL_REQUIREMENTS` que causava conflitos

### 4. Apache Superset - Configuração
**Problema:** Erro "No application module specified"  
**Solução:** 
- Adicionada instalação de `psycopg2-binary`
- Ajustado comando de inicialização para `/usr/bin/run-server.sh`
- Adicionadas variáveis de ambiente para conexão com PostgreSQL

---

## 🚀 Como Usar

### Iniciar a Stack
```bash
cd /home/marcelo/central/mini-bigdata
docker compose up -d
```

### Parar a Stack
```bash
docker compose down
```

### Ver Logs
```bash
# Todos os serviços
docker compose logs -f

# Serviço específico
docker compose logs -f airflow-webserver
docker compose logs -f spark-master
```

### Verificar Status
```bash
docker compose ps
```

### Reconstruir Imagem do Hive
```bash
docker compose build hive-metastore
docker compose up -d --force-recreate hive-metastore
```

---

## 📝 Próximos Passos

1. ✅ **Aguardar inicialização completa** (2-3 minutos após `docker compose up -d`)
2. ✅ **Acessar interfaces web** e validar login
3. 📋 **Executar pipeline de exemplo:** Ativar DAG `etl_sales_pipeline` no Airflow
4. 🔍 **Validar dados no Trino:**
   ```sql
   SELECT * FROM hive.sales.sales_silver LIMIT 10;
   ```
5. 📊 **Criar dashboard no Superset** conectando ao Trino

---

## 🔧 Troubleshooting

### Serviço não está healthy
```bash
# Ver logs do serviço
docker compose logs <service-name> --tail 50

# Reiniciar serviço
docker compose restart <service-name>
```

### Airflow não aparece UI
```bash
# Verificar se o banco foi inicializado
docker compose logs airflow-init

# Recriar containers
docker compose up -d --force-recreate airflow-webserver airflow-scheduler
```

### Hive Metastore com problema
```bash
# Rebuild da imagem
docker compose build hive-metastore --no-cache
docker compose up -d --force-recreate hive-metastore
```

### Limpar tudo e começar do zero
```bash
docker compose down -v
docker compose up -d
```

---

## 📚 Documentação Adicional

- **README.md:** Documentação principal do projeto
- **QUICKSTART.md:** Guia rápido de início
- **STORAGE.md:** Detalhes sobre persistência de dados
- **TROUBLESHOOTING.md:** Guia de resolução de problemas
- **examples/:** Exemplos de DAGs, Jobs PySpark e queries

---

## ✅ Checklist de Validação

- [x] PostgreSQL rodando e healthy
- [x] MinIO rodando e buckets criados
- [x] Spark Master e Worker rodando
- [x] Hive Metastore inicializado (aguardando healthy)
- [x] Trino rodando e healthy
- [x] Airflow webserver e scheduler rodando
- [x] Superset rodando e healthy
- [x] Todos os dados persistidos em `/media/marcelo/dados1/bigdata-docker/`
- [ ] Pipeline de exemplo executado com sucesso
- [ ] Dashboard criado no Superset

---

**🎉 Stack está operacional e pronta para uso!**

Para mais informações, consulte a documentação em `README.md` ou execute:
```bash
./check-storage.sh
```
