# 🔧 Guia de Troubleshooting

## Problemas Comuns e Soluções

### 1. Serviços não sobem

**Sintoma**: `docker-compose up -d` falha ou serviços ficam reiniciando

**Soluções**:
```bash
# Verificar logs
docker-compose logs -f

# Verificar recursos disponíveis
docker stats

# Limpar e recriar
docker-compose down -v
docker-compose up -d --force-recreate

# Verificar portas em uso
sudo netstat -tulpn | grep -E ':(5432|8080|8081|8085|8088|9000|9001|9083)'
```

### 2. Airflow não inicia

**Sintoma**: Airflow webserver não responde

**Soluções**:
```bash
# Verificar permissões
sudo chown -R 50000:0 data/airflow/

# Reinicializar banco
docker-compose run airflow-init

# Verificar logs
docker-compose logs airflow-webserver
docker-compose logs airflow-scheduler
```

### 3. Spark não conecta ao MinIO

**Sintoma**: Jobs Spark falham ao acessar S3

**Soluções**:
- Verificar credenciais no `spark-defaults.conf`
- Verificar se MinIO está rodando: `curl http://localhost:9000/minio/health/live`
- Testar acesso manual ao MinIO Console: http://localhost:9001

### 4. Trino não encontra tabelas

**Sintoma**: `SHOW TABLES` retorna vazio

**Soluções**:
```bash
# Verificar Hive Metastore
docker-compose logs hive-metastore

# Verificar catálogos
curl http://localhost:8085/v1/info

# Recriar tabelas manualmente via Spark
docker-compose exec spark-master spark-shell
```

### 5. Superset não conecta ao Trino

**Sintoma**: Erro de conexão no Superset

**Soluções**:
1. Instalar driver Trino no Superset:
```bash
docker-compose exec superset pip install trino
docker-compose restart superset
```

2. Connection string correta:
```
trino://trino@trino:8080/hive/sales
```

### 6. Memória insuficiente

**Sintoma**: Containers crasham por OOM

**Soluções**:
```yaml
# Adicionar limits no docker-compose.yml
services:
  spark-worker:
    deploy:
      resources:
        limits:
          memory: 2G
```

### 7. Permissões negadas

**Sintoma**: Permission denied ao criar arquivos

**Soluções**:
```bash
# Ajustar permissões
sudo chown -R $USER:$USER data/
chmod -R 755 data/

# Airflow específico
sudo chown -R 50000:0 data/airflow/
```

## Comandos Úteis de Diagnóstico

```bash
# Ver status de todos os serviços
docker-compose ps

# Ver uso de recursos
docker stats

# Verificar redes
docker network ls
docker network inspect bigdata-network

# Logs específicos
docker-compose logs -f <service_name>

# Acessar container
docker-compose exec <service_name> bash

# Reiniciar serviço específico
docker-compose restart <service_name>

# Verificar saúde
docker-compose ps | grep healthy
```

## Performance

### Otimizar Spark
```bash
# No spark-defaults.conf
spark.executor.memory=2g
spark.driver.memory=1g
spark.sql.shuffle.partitions=200
```

### Otimizar Trino
```bash
# No config.properties
query.max-memory=4GB
query.max-memory-per-node=2GB
```

## Limpeza e Manutenção

```bash
# Limpar logs antigos
find data/airflow/logs -type f -mtime +30 -delete

# Limpar cache do Trino
rm -rf data/trino/*

# Compactar dados antigos no MinIO
# (implementar script de compactação)
```

## Backup

```bash
# Backup de metadados
docker-compose exec postgres pg_dump -U admin metastore > backup_metastore.sql

# Backup de configurações
tar -czf backup_configs.tar.gz config/

# Backup de dados (incremental via MinIO)
mc mirror myminio/gold /backup/gold
```

## Monitoramento

```bash
# Verificar saúde dos serviços
curl http://localhost:9000/minio/health/live
curl http://localhost:8080/health  # Airflow
curl http://localhost:8085/v1/info  # Trino
curl http://localhost:8088/health   # Superset
```
