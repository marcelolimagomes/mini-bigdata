# Configuração de Drivers do Superset

## 📦 Drivers Instalados Automaticamente

O Apache Superset foi configurado para instalar automaticamente os seguintes drivers durante a inicialização do container:

### Drivers Incluídos

1. **PostgreSQL** (`psycopg2-binary`)
   - Usado para: Metadados do Superset
   - Versão: ≥2.9.0

2. **Trino** (`trino`)
   - Usado para: Conexão com Trino/Hive
   - Versão: ≥0.328.0

3. **SQLAlchemy-Trino** (`sqlalchemy-trino`)
   - Usado para: Integração SQLAlchemy com Trino
   - Versão: ≥0.5.0

## 🔧 Arquivos de Configuração

### 1. `config/superset/requirements.txt`
```txt
psycopg2-binary>=2.9.0
trino>=0.328.0
sqlalchemy-trino>=0.5.0
```

### 2. `config/superset/init-superset.sh`
Script de inicialização que:
- Instala os drivers via pip
- Atualiza o banco de dados do Superset
- Cria o usuário administrador
- Inicializa o Superset

### 3. `docker-compose.yml`
Monta os arquivos de configuração:
```yaml
volumes:
  - ./config/superset/superset_config.py:/app/pythonpath/superset_config.py
  - ./config/superset/requirements.txt:/app/pythonpath/requirements.txt
  - ./config/superset/init-superset.sh:/app/init-superset.sh
```

## 🚀 Como Usar

### Instalação Automática (Recomendado)

Os drivers são instalados automaticamente ao iniciar o container:

```bash
docker-compose up -d superset
```

Durante a inicialização, você verá:
```
📦 Instalando drivers de banco de dados...
Collecting psycopg2-binary>=2.9.0
Collecting trino>=0.328.0
Collecting sqlalchemy-trino>=0.5.0
...
Successfully installed psycopg2-binary-2.9.x trino-0.3xx.x sqlalchemy-trino-0.5.x
```

### Instalação Manual (Se Necessário)

Se precisar reinstalar os drivers manualmente:

```bash
# Entrar no container
docker exec -it superset bash

# Instalar drivers
pip install trino sqlalchemy-trino

# Ou usar o arquivo requirements
pip install -r /app/pythonpath/requirements.txt

# Sair do container
exit
```

## 🔗 Configurando Conexão com Trino

Após os drivers estarem instalados:

1. Acesse: http://localhost:8088
2. Login: `admin` / `admin`
3. Vá em: **Settings → Database Connections**
4. Clique em: **+ Database**
5. Selecione: **Other**
6. Configure:

### URI de Conexão

```
trino://trino@trino:8080/hive
```

### Detalhes da Configuração

- **Display Name**: `Trino - Hive Catalog`
- **SQLAlchemy URI**: `trino://trino@trino:8080/hive`
- **Username**: `trino` (opcional)
- **Host**: `trino`
- **Port**: `8080`
- **Database**: `hive` (catálogo)

### Testar Conexão

Clique em **Test Connection** para validar.

## 📊 Criando Datasets

### Via Interface Web

1. **Data → Datasets → + Dataset**
2. Selecione: **Create dataset from SQL query**
3. Database: `Trino - Hive Catalog`
4. SQL: Cole a query desejada
5. Dataset Name: Nome do dataset

### Via API (Scripts Python)

```python
from scripts.02_criar_datasets_virtuais_completo import SupersetAPI

api = SupersetAPI("http://localhost:8088", "admin", "admin")
api.login()

dataset_data = {
    "database": 1,  # ID do database Trino
    "table_name": "meu_dataset",
    "sql": "SELECT * FROM hive.default.minha_tabela"
}

api.create_dataset(dataset_data)
```

## 🔍 Verificar Drivers Instalados

Para verificar se os drivers foram instalados corretamente:

```bash
# Entrar no container
docker exec -it superset bash

# Verificar pacotes instalados
pip list | grep -E "trino|sqlalchemy-trino|psycopg2"

# Deve mostrar:
# psycopg2-binary    2.9.x
# sqlalchemy-trino   0.5.x
# trino              0.3xx.x
```

## 🐛 Troubleshooting

### Erro: "No module named 'trino'"

**Solução**: Reinstalar drivers manualmente
```bash
docker exec -it superset pip install trino sqlalchemy-trino
docker-compose restart superset
```

### Erro: "Could not load database driver: trino"

**Causa**: Driver não instalado ou Superset não reiniciado

**Solução**:
```bash
docker-compose restart superset
```

### Erro ao conectar: "connection refused"

**Causa**: Trino não está rodando ou nome do host incorreto

**Verificar**:
```bash
docker ps | grep trino
docker exec -it trino curl http://localhost:8080/v1/info
```

### Drivers não persistem após restart

**Causa**: Drivers instalados via `docker exec` são temporários

**Solução**: Use o arquivo `requirements.txt` que é montado no container e instalado automaticamente no `init-superset.sh`

## 📝 Adicionar Novos Drivers

Para adicionar novos drivers de banco de dados:

1. Edite `config/superset/requirements.txt`:
```txt
# Exemplo: MySQL
pymysql>=1.0.0

# Exemplo: MongoDB
pymongo>=4.0.0
```

2. Reinicie o container:
```bash
docker-compose restart superset
```

## 🔄 Atualizar Drivers

Para atualizar versões dos drivers:

1. Edite `config/superset/requirements.txt` com novas versões
2. Recrie o container:
```bash
docker-compose up -d --force-recreate superset
```

## 📚 Referências

- [Superset Database Drivers](https://superset.apache.org/docs/databases/installing-database-drivers)
- [Trino SQLAlchemy](https://github.com/trinodb/trino-python-client)
- [SQLAlchemy-Trino](https://github.com/trinodb/sqlalchemy-trino)

---

✅ **Configuração Completa**: Os drivers Trino estão configurados para instalação automática!
