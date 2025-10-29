# 🤖 Scripts de Configuração Automatizada

Scripts Python e Shell para configurar e gerenciar automaticamente a stack Big Data.

## 📦 Instalação de Dependências

```bash
# Instalar todas as dependências necessárias
pip install minio trino requests
```

## 🔄 Recriar Stack do Zero

**Para destruir e recriar toda a stack (apaga TODOS os dados):**

```bash
# Opção A: Script Bash (Linux/Mac)
./scripts/shell/recreate-stack.sh

# Opção B: Script Python (Cross-platform)
python3 scripts/recreate_stack.py

# Opção C: Modo automático (sem confirmações - USE COM CUIDADO!)
./scripts/shell/recreate-stack.sh --auto
python3 scripts/recreate_stack.py --auto
```

⚠️ **ATENÇÃO:** Estes scripts irão:
- ❌ Parar e remover TODOS os containers
- ❌ Remover TODOS os volumes Docker
- ❌ APAGAR todos os dados em `/media/marcelo/dados1/bigdata-docker`
- ✅ Recriar a estrutura de diretórios
- ✅ Subir a stack completa novamente
- ✅ Validar os serviços

---

## 🚀 Uso Rápido

### Opção 1: Setup Completo do Zero (RECOMENDADO)

**Para iniciar toda a stack do zero (inclui criação de diretórios, build, deploy e configuração):**

```bash
# Opção A: Script Bash (recomendado para Linux/Mac)
./scripts/shell/full-setup.sh

# Opção B: Script Python (cross-platform)
python3 scripts/full_setup.py
```

Estes scripts executam TODAS as etapas automaticamente:
1. ✅ Criam estrutura de diretórios em `/media/marcelo/dados1/bigdata-docker`
2. ✅ Limpam ambiente Docker (containers, volumes, redes antigas)
3. ✅ Fazem build das imagens personalizadas (Hive, Trino)
4. ✅ Sobem serviços base (PostgreSQL, MinIO, Redis)
5. ✅ Sobem Hive Metastore
6. ✅ Sobem demais serviços (Spark, Trino, Airflow, Superset)
7. ✅ Validam todos os serviços
8. ✅ Configuram MinIO (buckets), Trino (schemas/tabelas) e Superset (datasets)

**Tempo estimado:** 5-10 minutos

---

### Opção 2: Apenas Configuração (stack já rodando)

**Se a stack já está rodando e você quer apenas configurar os serviços:**

```bash
# Executar configuração completa
python3 scripts/setup_stack.py
```

Este script executa apenas as configurações:
1. Configura buckets no MinIO
2. Cria schemas e tabelas no Trino/Hive
3. Configura datasets no Superset

### Opção 2: Executar Individualmente

```bash
# 1. Configurar MinIO
python3 scripts/configure_minio.py

# 2. Configurar Trino
python3 scripts/configure_trino.py

# 3. Configurar Superset
python3 scripts/configure_superset.py
```

## ✅ Validação

Após executar a configuração, valide se tudo foi criado corretamente:

```bash
python3 scripts/validate_stack.py
```

## 📋 Descrição dos Scripts

### configure_minio.py
**Função:** Cria buckets no MinIO (arquitetura Medallion)

**Buckets criados:**
- `bronze` - Dados brutos
- `silver` - Dados limpos e validados
- `gold` - Dados agregados e prontos para BI
- `warehouse` - Data warehouse
- `raw-data` - Dados crus temporários

**Execução:**
```bash
python3 scripts/configure_minio.py
```

---

### configure_trino.py
**Função:** Cria schemas, tabelas e views no Trino/Hive Metastore

**Recursos criados:**

**Schemas:**
- `vendas` - Dados de vendas
- `logs` - Logs de aplicação
- `analytics` - Análises e métricas

**Tabelas:**
- `vendas.vendas_raw` - Vendas brutas (CSV no Bronze)
- `vendas.vendas_silver` - Vendas processadas (Parquet no Silver)
- `vendas.vendas_agregadas` - Vendas agregadas (Parquet no Gold)

**Views:**
- `analytics.vendas_mensais` - Agregação mensal de vendas
- `analytics.top_produtos` - Ranking de produtos por receita

**Execução:**
```bash
python3 scripts/configure_trino.py
```

---

### configure_superset.py
**Função:** Configura datasets no Superset via API

**Pré-requisito:** Database connection com Trino deve existir

**Datasets criados:**
- `vendas.vendas_silver`
- `vendas.vendas_agregadas`
- `analytics.vendas_mensais`
- `analytics.top_produtos`

**Execução:**
```bash
python3 scripts/configure_superset.py
```

**Nota:** Se o database connection não existir, o script mostra como criar manualmente.

---

### setup_stack.py
**Função:** Script mestre que executa todos os outros na ordem correta

**Passos executados:**
1. Verifica e instala dependências Python
2. Configura MinIO (buckets)
3. Configura Trino (schemas e tabelas)
4. Configura Superset (datasets)

**Execução:**
```bash
python3 scripts/setup_stack.py
```

---

### validate_stack.py
**Função:** Valida se toda a stack foi configurada corretamente

**Validações:**
- ✅ MinIO: Verifica se buckets foram criados
- ✅ Trino: Verifica schemas, tabelas e views
- ✅ Superset: Verifica databases e datasets

**Execução:**
```bash
python3 scripts/validate_stack.py
```

**Saída esperada:**
```
✅ MinIO
✅ Trino
✅ Superset

✅ Stack configurada corretamente!
```

## 🔧 Troubleshooting

### Erro: "Não foi possível conectar ao MinIO"

**Solução:**
```bash
# Verificar se o container está rodando
docker compose ps minio

# Reiniciar se necessário
docker compose restart minio
```

---

### Erro: "Connection refused" no Trino

**Solução:**
```bash
# Verificar se Trino está rodando
docker compose ps trino

# Aguardar Trino inicializar (pode levar 1-2 minutos)
docker compose logs -f trino

# Aguardar mensagem: "SERVER STARTED"
```

---

### Erro: "Falha no login" no Superset

**Solução:**
```bash
# Verificar credenciais padrão
# Usuário: admin
# Senha: admin

# Se alterou senha, edite scripts/configure_superset.py
# Linhas 11-12
```

---

### Aviso: "Nenhum database configurado" no Superset

**Solução Manual:**

1. Acesse http://localhost:8088
2. Login: admin / admin
3. Settings → Database Connections
4. + Database
5. Selecione "Trino"
6. Preencha:
   - **Display Name:** Trino Big Data
   - **SQLAlchemy URI:** `trino://trino@trino:8080/hive`
7. Test Connection → Connect
8. Execute novamente: `python3 scripts/configure_superset.py`

---

### Erro: "Tabela não encontrada" ao criar dataset

**Solução:**
```bash
# Verificar se tabelas existem no Trino
docker exec -it trino trino --catalog hive --schema vendas

# No prompt do Trino:
SHOW TABLES;

# Se não houver tabelas, execute:
python3 scripts/configure_trino.py
```

## 📊 Estrutura de Dados Criada

```
MinIO (S3)
├── bronze/
│   └── vendas/          # CSV com dados brutos
├── silver/
│   └── vendas/          # Parquet particionado (ano, mes)
├── gold/
│   ├── vendas/
│   │   └── agregadas/   # Parquet com agregações
│   ├── logs/
│   └── analytics/
└── warehouse/

Trino/Hive
├── vendas (schema)
│   ├── vendas_raw (tabela)
│   ├── vendas_silver (tabela)
│   └── vendas_agregadas (tabela)
├── logs (schema)
└── analytics (schema)
    ├── vendas_mensais (view)
    └── top_produtos (view)

Superset
└── Datasets
    ├── vendas.vendas_silver
    ├── vendas.vendas_agregadas
    ├── analytics.vendas_mensais
    └── analytics.top_produtos
```

## 🎯 Próximos Passos

Após executar os scripts:

1. **Carregar dados de exemplo:**
   ```bash
   # Ver exemplos em: examples/data/
   ```

2. **Criar visualizações no Superset:**
   - Acesse http://localhost:8088
   - Charts → + Chart
   - Selecione dataset
   - Configure visualização

3. **Executar pipelines Airflow:**
   - Acesse http://localhost:8080
   - Ver exemplos em: examples/dags/

## 📚 Documentação Completa

Para mais detalhes, consulte:
- `docs/09-configuracao-automatizada.md` - Guia completo de automação
- `docs/07-apis-rest-jdbc.md` - Documentação das APIs
- `VALIDACAO_SUPERSET_API.md` - Validação da API do Superset

## 🔗 Links Úteis

- MinIO: http://localhost:9001
- Trino: http://localhost:8085
- Superset: http://localhost:8088
- Airflow: http://localhost:8080
- Spark Master: http://localhost:8081

## 📝 Customização

Para customizar os scripts:

1. **Alterar credenciais:**
   - Edite as constantes no início de cada script
   - Ex: `MINIO_ACCESS_KEY`, `USERNAME`, etc.

2. **Adicionar mais tabelas:**
   - Edite `configure_trino.py`
   - Adicione definições SQL no método `setup_trino()`

3. **Criar mais datasets:**
   - Edite `configure_superset.py`
   - Adicione tuplas em `datasets_to_create`

## ⚡ Dicas

- Execute `validate_stack.py` sempre após mudanças
- Use `setup_stack.py` para configuração inicial
- Scripts são idempotentes (podem ser executados múltiplas vezes)
- Logs detalhados ajudam no troubleshooting
