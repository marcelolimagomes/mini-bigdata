# 🔄 Mudanças na Estrutura de Persistência

## ✅ Alterações Realizadas

### 1. **Docker Compose (docker-compose.yml)**

#### Antes:
```yaml
volumes:
  - ./data/postgres:/var/lib/postgresql/data
  - ./data/minio:/data
  # ... outros volumes relativos
```

#### Depois:
```yaml
# Serviços usam volumes nomeados
volumes:
  - postgres-data:/var/lib/postgresql/data
  - minio-data:/data

# Definição dos volumes no final do arquivo
volumes:
  postgres-data:
    driver: local
    driver_opts:
      type: none
      o: bind
      device: /media/marcelo/dados1/bigdata-docker/postgres
  # ... outros volumes
```

### 2. **Script de Setup (setup.sh)**

#### Mudanças:
- ✅ Adicionada variável `DATA_ROOT="/media/marcelo/dados1/bigdata-docker"`
- ✅ Verificação de existência do diretório
- ✅ Criação automática com permissões corretas
- ✅ Mensagem informando localização dos dados

### 3. **Novos Arquivos Criados**

#### STORAGE.md
- Documentação completa sobre persistência
- Estrutura de diretórios detalhada
- Guia de backup e restore
- Comandos de manutenção e limpeza
- Troubleshooting de armazenamento

#### check-storage.sh
- Script interativo de verificação
- Verifica espaço em disco
- Verifica permissões
- Cria estrutura de diretórios
- Opção de backup de dados existentes

### 4. **README.md Atualizado**

- ✅ Seção de armazenamento adicionada
- ✅ Referência ao STORAGE.md
- ✅ Estrutura de diretórios atualizada
- ✅ Comandos de backup adicionados

## 📦 Volumes Configurados

| Volume | Caminho Host | Container |
|--------|--------------|-----------|
| postgres-data | /media/marcelo/dados1/bigdata-docker/postgres | PostgreSQL |
| minio-data | /media/marcelo/dados1/bigdata-docker/minio | MinIO |
| airflow-dags | /media/marcelo/dados1/bigdata-docker/airflow/dags | Airflow |
| airflow-logs | /media/marcelo/dados1/bigdata-docker/airflow/logs | Airflow |
| airflow-plugins | /media/marcelo/dados1/bigdata-docker/airflow/plugins | Airflow |
| hive-warehouse | /media/marcelo/dados1/bigdata-docker/hive | Hive Metastore |
| spark-master-work | /media/marcelo/dados1/bigdata-docker/spark/master | Spark Master |
| spark-worker-work | /media/marcelo/dados1/bigdata-docker/spark/worker | Spark Worker |
| trino-data | /media/marcelo/dados1/bigdata-docker/trino | Trino |
| superset-data | /media/marcelo/dados1/bigdata-docker/superset | Superset |

## 🎯 Benefícios

### Persistência Garantida
✅ Dados sobrevivem a `docker-compose down`  
✅ Dados sobrevivem a `docker-compose down -v`  
✅ Apenas remoção manual do diretório apaga os dados

### Backup Simplificado
```bash
# Backup completo
tar -czf backup.tar.gz /media/marcelo/dados1/bigdata-docker/

# Restore
tar -xzf backup.tar.gz -C /media/marcelo/dados1/
```

### Portabilidade
- Fácil migração entre discos
- Fácil migração entre servidores
- Independente do Docker

### Performance
- Acesso direto ao filesystem
- Sem overhead de volumes Docker
- Melhor I/O performance

## 🚀 Como Usar

### Primeira Instalação

```bash
# 1. Verificar e preparar armazenamento
chmod +x check-storage.sh
./check-storage.sh

# 2. Executar setup
chmod +x setup.sh
./setup.sh

# 3. Subir serviços
docker-compose up -d

# 4. Verificar
docker-compose ps
du -sh /media/marcelo/dados1/bigdata-docker/*/
```

### Migração de Dados Existentes

Se você já tinha dados em `./data/`:

```bash
# 1. Parar serviços
docker-compose down

# 2. Criar estrutura nova
./check-storage.sh

# 3. Copiar dados existentes
cp -r ./data/postgres/* /media/marcelo/dados1/bigdata-docker/postgres/
cp -r ./data/minio/* /media/marcelo/dados1/bigdata-docker/minio/
cp -r ./data/airflow/* /media/marcelo/dados1/bigdata-docker/airflow/
# ... outros componentes

# 4. Ajustar permissões
sudo chown -R 50000:0 /media/marcelo/dados1/bigdata-docker/airflow/

# 5. Reiniciar
docker-compose up -d
```

### Mudar Localização do Storage

Para usar outro diretório:

1. **Editar docker-compose.yml**:
```yaml
volumes:
  postgres-data:
    driver_opts:
      device: /novo/caminho/postgres  # Alterar aqui
```

2. **Editar setup.sh**:
```bash
DATA_ROOT="/novo/caminho"  # Alterar aqui
```

3. **Editar check-storage.sh**:
```bash
DATA_ROOT="/novo/caminho"  # Alterar aqui
```

4. **Executar novamente**:
```bash
./check-storage.sh
./setup.sh
docker-compose up -d
```

## 🔍 Verificações

### Verificar montagem dos volumes

```bash
# Ver volumes do Docker
docker volume ls

# Inspecionar volume específico
docker volume inspect mini-bigdata_postgres-data

# Verificar bind mounts
docker-compose exec postgres df -h /var/lib/postgresql/data
```

### Verificar dados persistidos

```bash
# Listar arquivos no host
ls -lah /media/marcelo/dados1/bigdata-docker/postgres/

# Ver tamanho
du -sh /media/marcelo/dados1/bigdata-docker/*/

# Espaço total
df -h /media/marcelo/dados1/
```

### Teste de persistência

```bash
# 1. Criar dados
docker-compose exec postgres psql -U admin -c "CREATE TABLE test (id int);"

# 2. Parar tudo
docker-compose down

# 3. Remover volumes Docker (não afeta bind mounts!)
docker-compose down -v

# 4. Subir novamente
docker-compose up -d

# 5. Verificar dados ainda existem
docker-compose exec postgres psql -U admin -c "SELECT * FROM test;"
# ✅ Dados devem estar lá!
```

## 📋 Checklist de Validação

- [ ] Diretório `/media/marcelo/dados1/` existe
- [ ] Espaço em disco suficiente (>20GB recomendado)
- [ ] Permissões de escrita OK
- [ ] `check-storage.sh` executado com sucesso
- [ ] `setup.sh` executado com sucesso
- [ ] `docker-compose up -d` executado com sucesso
- [ ] Todos os serviços estão healthy
- [ ] Dados aparecem em `/media/marcelo/dados1/bigdata-docker/`
- [ ] Teste de persistência passou

## 🆘 Troubleshooting

### Erro: "Permission denied"

```bash
sudo chown -R $USER:$USER /media/marcelo/dados1/bigdata-docker/
chmod -R 755 /media/marcelo/dados1/bigdata-docker/
sudo chown -R 50000:0 /media/marcelo/dados1/bigdata-docker/airflow/
```

### Erro: "No space left on device"

```bash
# Verificar espaço
df -h /media/marcelo/dados1/

# Limpar dados antigos
docker system prune -a --volumes

# Mover para disco maior (veja STORAGE.md)
```

### Volumes não montam

```bash
# Verificar existência dos diretórios
ls -la /media/marcelo/dados1/bigdata-docker/

# Recriar estrutura
./check-storage.sh

# Verificar docker-compose.yml
docker-compose config
```

## 📚 Documentação Relacionada

- **README.md** - Documentação principal
- **STORAGE.md** - Detalhes completos de armazenamento
- **QUICKSTART.md** - Guia rápido
- **TROUBLESHOOTING.md** - Solução de problemas

## 💡 Notas Importantes

1. **Backup Regular**: Configure backups automáticos do diretório
2. **Monitoramento**: Configure alertas de espaço em disco
3. **Segurança**: O diretório contém dados sensíveis
4. **Performance**: Use SSD para melhor performance
5. **RAID**: Considere RAID para redundância

---

**Última atualização**: 21 de outubro de 2025
