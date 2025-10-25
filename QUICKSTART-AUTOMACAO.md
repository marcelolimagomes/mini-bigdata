# ⚡ Guia Rápido de Configuração Automatizada

## 🚀 Setup em 3 Comandos

```bash
# 1. Instalar dependências
pip install minio trino requests

# 2. Executar configuração automatizada
python3 scripts/setup_stack.py

# 3. Validar
python3 scripts/validate_stack.py
```

## 📊 O Que É Criado Automaticamente

### MinIO (Object Storage)
- ✅ Bucket `bronze` - Dados brutos
- ✅ Bucket `silver` - Dados processados
- ✅ Bucket `gold` - Dados agregados
- ✅ Bucket `warehouse` - Data warehouse

### Trino/Hive (Data Lake)
- ✅ Schema `vendas`
- ✅ Schema `logs`
- ✅ Schema `analytics`
- ✅ Tabela `vendas.vendas_raw` (CSV)
- ✅ Tabela `vendas.vendas_silver` (Parquet particionado)
- ✅ Tabela `vendas.vendas_agregadas` (Parquet)
- ✅ View `analytics.vendas_mensais`
- ✅ View `analytics.top_produtos`

### Superset (BI)
- ✅ Datasets prontos para uso
- ✅ Conexão com Trino configurável

## 🎯 Configuração Manual do Superset

Se precisar configurar database connection manualmente:

1. Acesse http://localhost:8088
2. Login: `admin` / `admin`
3. **Settings** → **Database Connections** → **+ Database**
4. Selecione **Trino**
5. Preencha:
   ```
   Display Name: Trino Big Data
   SQLAlchemy URI: trino://trino@trino:8080/hive
   ```
6. **Test Connection** → **Connect**

## 📋 Comandos Individuais

```bash
# Apenas MinIO
python3 scripts/configure_minio.py

# Apenas Trino
python3 scripts/configure_trino.py

# Apenas Superset
python3 scripts/configure_superset.py
```

## ✅ Verificação Rápida

```bash
# Validar toda a stack
python3 scripts/validate_stack.py

# Verificar buckets MinIO
docker exec -it minio-client mc ls myminio/

# Verificar tabelas Trino
docker exec -it trino trino --catalog hive --schema vendas -e "SHOW TABLES;"

# Testar Superset API
curl http://localhost:8088/health
```

## 🔗 URLs de Acesso

| Serviço | URL | Credenciais |
|---------|-----|-------------|
| MinIO | http://localhost:9001 | minioadmin / minioadmin123 |
| Trino | http://localhost:8085 | trino / - |
| Superset | http://localhost:8088 | admin / admin |
| Airflow | http://localhost:8080 | airflow / airflow |

## 🆘 Troubleshooting

### Container não está rodando
```bash
docker compose ps
docker compose up -d <serviço>
```

### Erro de conexão
```bash
# Aguardar serviços iniciarem (30s-1min)
docker compose logs -f <serviço>
```

### Resetar configuração
```bash
# Remover buckets
docker exec -it minio-client mc rb --force myminio/bronze

# Remover schemas (cuidado!)
docker exec -it trino trino --catalog hive -e "DROP SCHEMA IF EXISTS vendas CASCADE;"
```

## 📚 Documentação Completa

- `docs/09-configuracao-automatizada.md` - Guia completo
- `scripts/README.md` - Detalhes dos scripts
- `VALIDACAO_SUPERSET_API.md` - Validação da API

## 💡 Próximos Passos

1. ✅ Executar scripts de configuração
2. 📊 Carregar dados de exemplo
3. 🔄 Criar pipelines Airflow
4. 📈 Criar visualizações no Superset
