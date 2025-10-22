# ⚡ Instalação Rápida - Mini Big Data Platform

## 🎯 Pré-requisitos

- [x] Docker e Docker Compose instalados
- [x] Mínimo 8GB RAM
- [x] **20GB+ espaço livre em `/media/marcelo/dados1/`**
- [x] Portas livres: 5432, 7077, 8080-8088, 9000-9001, 9083

## 🚀 Instalação em 3 Passos

### 1️⃣ Preparar Armazenamento
```bash
./check-storage.sh
```
**O que faz:**
- ✅ Verifica espaço em disco
- ✅ Cria estrutura em `/media/marcelo/dados1/bigdata-docker/`
- ✅ Configura permissões
- ✅ Oferece backup de dados existentes

### 2️⃣ Configurar Ambiente
```bash
./setup.sh
```
**O que faz:**
- ✅ Cria diretórios de configuração
- ✅ Gera arquivos de config (Spark, Trino, Hive, etc.)
- ✅ Valida Docker

### 3️⃣ Iniciar Serviços
```bash
docker-compose up -d
```
**O que faz:**
- ✅ Sobe todos os 11 serviços
- ✅ Cria buckets no MinIO
- ✅ Inicializa bancos de dados
- ✅ Configura usuários

## 📊 Acompanhar Inicialização

```bash
# Ver logs em tempo real
docker-compose logs -f

# Verificar status
docker-compose ps

# Ver apenas serviços saudáveis
docker-compose ps | grep healthy
```

## 🌐 Acessar Interfaces

Aguarde ~2-3 minutos para todos os serviços subirem, depois acesse:

| Serviço | URL | Credenciais |
|---------|-----|-------------|
| **MinIO** | http://localhost:9001 | minioadmin / minioadmin123 |
| **Airflow** | http://localhost:8080 | airflow / airflow |
| **Superset** | http://localhost:8088 | admin / admin |
| **Trino** | http://localhost:8085 | trino (sem senha) |
| **Spark Master** | http://localhost:8081 | - |

## ✅ Validar Instalação

### Teste 1: Verificar todos os serviços
```bash
docker-compose ps
```
**Esperado:** Todos com status `Up` e alguns com `healthy`

### Teste 2: Verificar dados persistidos
```bash
du -sh /media/marcelo/dados1/bigdata-docker/*/
```
**Esperado:** Ver diretórios com alguns MBs

### Teste 3: Acessar MinIO
1. Abra: http://localhost:9001
2. Login: minioadmin / minioadmin123
3. Veja buckets: bronze, silver, gold

### Teste 4: Executar pipeline de exemplo
1. Acesse Airflow: http://localhost:8080
2. Login: airflow / airflow
3. Ative DAG: `etl_sales_pipeline`
4. Clique em "Trigger DAG"
5. Aguarde conclusão (~2-5 minutos)

### Teste 5: Consultar dados no Trino
```bash
docker-compose exec trino trino --execute "SHOW CATALOGS;"
```
**Esperado:** Ver `hive`, `memory`, `system`

## 🎓 Primeiros Passos

### 1. Explorar MinIO
```bash
# Via browser
open http://localhost:9001

# Ver buckets criados
docker-compose exec minio-client mc ls myminio/
```

### 2. Executar primeira DAG
- Acesse Airflow
- Ative e execute `etl_sales_pipeline`
- Acompanhe execução no Graph View

### 3. Consultar dados processados
```sql
-- No Trino (http://localhost:8085)
SELECT * FROM hive.sales.sales_silver LIMIT 10;
```

### 4. Criar primeiro dashboard
- Acesse Superset
- Add Database: `trino://trino@trino:8080/hive/sales`
- SQL Lab > Execute queries
- Charts > Create chart

## 📚 Documentação

| Arquivo | Conteúdo |
|---------|----------|
| **README.md** | Documentação completa |
| **QUICKSTART.md** | Guia rápido de uso |
| **STORAGE.md** | Detalhes de armazenamento |
| **CHANGELOG-STORAGE.md** | Mudanças de persistência |
| **TROUBLESHOOTING.md** | Solução de problemas |

## 🆘 Problemas?

### Serviço não sobe
```bash
docker-compose logs <nome-servico>
```

### Porta em uso
```bash
sudo netstat -tulpn | grep <porta>
docker-compose down
# Matar processo ou mudar porta no .env
```

### Sem espaço
```bash
df -h /media/marcelo/dados1/
# Limpar ou usar outro disco (veja STORAGE.md)
```

### Permissões
```bash
sudo chown -R $USER:$USER /media/marcelo/dados1/bigdata-docker/
sudo chown -R 50000:0 /media/marcelo/dados1/bigdata-docker/airflow/
```

## 🛑 Parar/Remover

```bash
# Parar serviços (mantém dados)
docker-compose down

# Parar e remover volumes Docker (dados em /media persistem!)
docker-compose down -v

# Limpar TUDO (incluindo dados)
docker-compose down -v
sudo rm -rf /media/marcelo/dados1/bigdata-docker/
```

## 💾 Backup

```bash
# Backup completo
tar -czf bigdata-backup-$(date +%Y%m%d).tar.gz \
  /media/marcelo/dados1/bigdata-docker/

# Apenas dados (MinIO)
tar -czf minio-backup-$(date +%Y%m%d).tar.gz \
  /media/marcelo/dados1/bigdata-docker/minio/
```

## 📈 Monitoramento

```bash
# Uso de recursos
docker stats

# Espaço em disco
watch -n 5 'du -sh /media/marcelo/dados1/bigdata-docker/*/'

# Status dos serviços
watch -n 10 'docker-compose ps'
```

## 🎯 Checklist de Instalação

- [ ] Executei `./check-storage.sh` com sucesso
- [ ] Executei `./setup.sh` com sucesso
- [ ] Executei `docker-compose up -d`
- [ ] Aguardei 2-3 minutos
- [ ] Todos os serviços estão `Up`
- [ ] Consegui acessar MinIO (9001)
- [ ] Consegui acessar Airflow (8080)
- [ ] Consegui acessar Superset (8088)
- [ ] Consegui acessar Trino (8085)
- [ ] Executei DAG de exemplo com sucesso
- [ ] Dados aparecem em `/media/marcelo/dados1/bigdata-docker/`
- [ ] Li a documentação (README.md)

## ✨ Próximos Passos

1. **Explorar exemplos**: Veja `examples/` para DAGs, Jobs e Queries
2. **Criar seu pipeline**: Copie e modifique DAG de exemplo
3. **Upload de dados**: Use MinIO para fazer upload de seus CSVs
4. **Dashboards**: Crie visualizações no Superset
5. **Escalar**: Adicione mais workers Spark conforme necessário

---

**Instalação completa em ~5 minutos!** 🚀

Para dúvidas, consulte **TROUBLESHOOTING.md** ou abra uma issue.
