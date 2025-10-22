# 💾 Estrutura de Armazenamento e Persistência

## 📍 Localização dos Dados

Todos os dados da stack Big Data são persistidos em:

```
/media/marcelo/dados1/bigdata-docker/
```

## 🗂️ Estrutura de Diretórios

```
/media/marcelo/dados1/bigdata-docker/
├── postgres/              # Banco de dados PostgreSQL
│   ├── base/             # Databases (airflow, superset, metastore)
│   ├── global/           # Configurações globais
│   └── pg_wal/           # Write-Ahead Logs
│
├── minio/                # Object Storage (S3-compatible)
│   ├── .minio.sys/       # Sistema MinIO
│   ├── bronze/           # Dados brutos
│   ├── silver/           # Dados processados
│   ├── gold/             # Dados analíticos
│   ├── warehouse/        # Hive warehouse
│   └── raw/              # Dados brutos diversos
│
├── airflow/              # Apache Airflow
│   ├── dags/             # DAGs (workflows)
│   ├── logs/             # Logs de execução
│   └── plugins/          # Plugins customizados
│
├── hive/                 # Hive Metastore Warehouse
│   └── warehouse/        # Tabelas gerenciadas
│
├── spark/                # Apache Spark
│   ├── master/           # Dados do Master
│   │   ├── work/         # Work directory
│   │   └── events/       # Event logs
│   └── worker/           # Dados do Worker
│       └── work/         # Work directory
│
├── trino/                # Trino Query Engine
│   ├── catalog/          # Cache de catálogos
│   └── var/              # Dados variáveis
│
└── superset/             # Apache Superset
    ├── superset.db       # SQLite para metadata (se aplicável)
    └── uploads/          # Arquivos uploadados

```

## 🔒 Persistência Garantida

### Volumes Nomeados

O docker-compose usa **volumes nomeados** com bind mounts no caminho especificado:

```yaml
volumes:
  postgres-data:
    driver: local
    driver_opts:
      type: none
      o: bind
      device: /media/marcelo/dados1/bigdata-docker/postgres
```

### Características

✅ **Persistência Total**: Dados sobrevivem a `docker-compose down`  
✅ **Backup Simples**: Basta copiar o diretório raiz  
✅ **Portabilidade**: Pode mover para outro disco/servidor  
✅ **Performance**: Acesso direto ao filesystem do host  

## 📊 Espaço em Disco

### Estimativa de Uso

| Componente | Uso Inicial | Crescimento |
|------------|-------------|-------------|
| PostgreSQL | ~50 MB | Baixo |
| MinIO | ~10 MB | **Alto** (dados) |
| Airflow | ~100 MB | Médio (logs) |
| Hive Metastore | ~50 MB | Baixo |
| Spark | ~100 MB | Médio (eventos) |
| Trino | ~50 MB | Baixo |
| Superset | ~100 MB | Baixo |
| **Total Inicial** | **~500 MB** | - |

### Monitorar Espaço

```bash
# Ver tamanho total
du -sh /media/marcelo/dados1/bigdata-docker/

# Ver por componente
du -sh /media/marcelo/dados1/bigdata-docker/*/

# MinIO (onde ficam os dados)
du -sh /media/marcelo/dados1/bigdata-docker/minio/

# Logs do Airflow
du -sh /media/marcelo/dados1/bigdata-docker/airflow/logs/
```

## 🔄 Backup e Restore

### Backup Completo

```bash
# Parar os serviços
docker-compose down

# Criar backup
tar -czf bigdata-backup-$(date +%Y%m%d).tar.gz \
  -C /media/marcelo/dados1 \
  bigdata-docker/

# Ou usar rsync para backup incremental
rsync -avz /media/marcelo/dados1/bigdata-docker/ \
  /caminho/backup/bigdata-docker/
```

### Backup Seletivo

```bash
# Apenas dados do MinIO (mais importante)
tar -czf minio-backup-$(date +%Y%m%d).tar.gz \
  /media/marcelo/dados1/bigdata-docker/minio/

# Apenas metadados (PostgreSQL + Hive)
tar -czf metadata-backup-$(date +%Y%m%d).tar.gz \
  /media/marcelo/dados1/bigdata-docker/postgres/ \
  /media/marcelo/dados1/bigdata-docker/hive/
```

### Restore

```bash
# Parar serviços
docker-compose down

# Restaurar backup
tar -xzf bigdata-backup-YYYYMMDD.tar.gz \
  -C /media/marcelo/dados1/

# Reiniciar
docker-compose up -d
```

## 🧹 Limpeza e Manutenção

### Limpar Logs Antigos

```bash
# Logs do Airflow com mais de 30 dias
find /media/marcelo/dados1/bigdata-docker/airflow/logs \
  -type f -mtime +30 -delete

# Logs do Spark
find /media/marcelo/dados1/bigdata-docker/spark/*/work/events \
  -type f -mtime +30 -delete
```

### Otimizar PostgreSQL

```bash
# Acessar PostgreSQL
docker-compose exec postgres psql -U admin

# Vacuum para recuperar espaço
VACUUM FULL;
VACUUM ANALYZE;
```

### Compactar Dados no MinIO

```bash
# Via MinIO Client
docker-compose exec minio-client mc ls myminio/bronze/

# Comprimir dados antigos
# (implementar script Python com boto3)
```

## 🔐 Permissões

### Estrutura Recomendada

```bash
# Proprietário geral
sudo chown -R $USER:$USER /media/marcelo/dados1/bigdata-docker/

# Permissões gerais
chmod -R 755 /media/marcelo/dados1/bigdata-docker/

# Airflow (UID específico)
sudo chown -R 50000:0 /media/marcelo/dados1/bigdata-docker/airflow/
```

### Verificar Permissões

```bash
ls -la /media/marcelo/dados1/bigdata-docker/
```

## 📦 Migração de Dados

### Para Outro Disco

```bash
# 1. Parar serviços
docker-compose down

# 2. Copiar dados
rsync -avz --progress \
  /media/marcelo/dados1/bigdata-docker/ \
  /novo/caminho/bigdata-docker/

# 3. Atualizar docker-compose.yml
# Substituir /media/marcelo/dados1/bigdata-docker pelo novo caminho

# 4. Atualizar setup.sh
# Alterar variável DATA_ROOT

# 5. Reiniciar
docker-compose up -d
```

### Para Outro Servidor

```bash
# 1. Backup
tar -czf bigdata-backup.tar.gz \
  /media/marcelo/dados1/bigdata-docker/

# 2. Transferir
scp bigdata-backup.tar.gz user@servidor:/caminho/

# 3. No servidor destino
tar -xzf bigdata-backup.tar.gz
# Ajustar caminhos no docker-compose.yml e setup.sh
docker-compose up -d
```

## 🔍 Troubleshooting

### Volume não monta

```bash
# Verificar se diretório existe
ls -la /media/marcelo/dados1/bigdata-docker/

# Criar manualmente se necessário
sudo mkdir -p /media/marcelo/dados1/bigdata-docker/{postgres,minio,airflow,hive,spark,trino,superset}
sudo chown -R $USER:$USER /media/marcelo/dados1/bigdata-docker/
```

### Sem espaço em disco

```bash
# Verificar espaço disponível
df -h /media/marcelo/dados1/

# Limpar dados antigos do MinIO
docker-compose exec minio-client mc rm --recursive --force \
  myminio/bronze/raw/old_data/

# Limpar logs
find /media/marcelo/dados1/bigdata-docker -name "*.log" -mtime +60 -delete
```

### Permissões negadas

```bash
# Reset de permissões
sudo chown -R $USER:$USER /media/marcelo/dados1/bigdata-docker/
chmod -R 755 /media/marcelo/dados1/bigdata-docker/
sudo chown -R 50000:0 /media/marcelo/dados1/bigdata-docker/airflow/
```

## 📈 Monitoramento

### Script de Monitoramento

```bash
#!/bin/bash
# monitor_storage.sh

DATA_ROOT="/media/marcelo/dados1/bigdata-docker"

echo "=== Uso de Espaço ==="
df -h /media/marcelo/dados1/

echo ""
echo "=== Por Componente ==="
du -sh $DATA_ROOT/*/ | sort -h

echo ""
echo "=== Top 10 Maiores Arquivos ==="
find $DATA_ROOT -type f -exec du -h {} + | sort -rh | head -10
```

### Alertas de Espaço

```bash
# Adicionar ao crontab para alertas
# crontab -e
# 0 8 * * * /caminho/monitor_storage.sh | mail -s "Storage Report" admin@example.com
```

## 🎯 Boas Práticas

1. **Backup Regular**: Diário para metadados, semanal para dados completos
2. **Monitoramento**: Verificar espaço em disco semanalmente
3. **Limpeza**: Remover logs antigos mensalmente
4. **Compressão**: Comprimir dados antigos no MinIO
5. **Documentação**: Documentar mudanças na estrutura
6. **Testes**: Testar restore de backups periodicamente

## 📝 Notas

- Diretório raiz é configurável via `setup.sh`
- Volumes nomeados garantem persistência
- Bind mounts permitem acesso direto aos dados
- Backup simples: copiar diretório raiz
- Migração: atualizar caminhos e copiar dados
