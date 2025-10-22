#!/bin/bash

echo "🚀 Configurando ambiente Mini Big Data..."

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Definir diretório raiz para dados
DATA_ROOT="/media/marcelo/dados1/bigdata-docker"

# Verificar se o diretório raiz existe e tem permissão de escrita
if [ ! -d "$DATA_ROOT" ]; then
    echo -e "${YELLOW}⚠️  Diretório $DATA_ROOT não existe. Tentando criar...${NC}"
    sudo mkdir -p "$DATA_ROOT" || {
        echo -e "${RED}❌ Erro ao criar diretório $DATA_ROOT${NC}"
        echo -e "${YELLOW}Execute: sudo mkdir -p $DATA_ROOT && sudo chown -R $USER:$USER $DATA_ROOT${NC}"
        exit 1
    }
    sudo chown -R $USER:$USER "$DATA_ROOT"
fi

# Criar estrutura de diretórios
echo -e "${YELLOW}📁 Criando estrutura de diretórios em $DATA_ROOT...${NC}"

# Diretórios de dados (persistência)
mkdir -p "$DATA_ROOT"/{minio,postgres,airflow/{dags,logs,plugins},spark/{master,worker},trino,hive,superset}

# Diretórios locais (configuração e exemplos)
mkdir -p data/{minio,postgres,airflow/{dags,logs,plugins},spark/{master,worker},trino,hive,superset}

# Diretórios de configuração
mkdir -p config/{postgres,hive,spark,trino/catalog,superset,airflow}

# Diretórios de exemplos
mkdir -p examples/{dags,jobs,queries,notebooks,data}

# Definir permissões corretas
echo -e "${YELLOW}🔐 Configurando permissões...${NC}"

# Permissões para o diretório raiz de dados
chmod -R 755 "$DATA_ROOT"

# Airflow precisa de UID específico
sudo chown -R 50000:0 "$DATA_ROOT/airflow" 2>/dev/null || chown -R 50000:0 "$DATA_ROOT/airflow"

# Permissões gerais para diretórios locais
chmod -R 755 data/ 2>/dev/null || true
chmod -R 755 config/
chmod -R 755 examples/

echo -e "${GREEN}✅ Estrutura de diretórios criada!${NC}"

# Criar arquivos de configuração
echo -e "${YELLOW}⚙️  Criando arquivos de configuração...${NC}"

# PostgreSQL - Init script para múltiplos databases
cat > config/postgres/init-databases.sh << 'EOF'
#!/bin/bash
set -e

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" <<-EOSQL
    CREATE DATABASE airflow;
    CREATE DATABASE superset;
    CREATE DATABASE metastore;
    GRANT ALL PRIVILEGES ON DATABASE airflow TO $POSTGRES_USER;
    GRANT ALL PRIVILEGES ON DATABASE superset TO $POSTGRES_USER;
    GRANT ALL PRIVILEGES ON DATABASE metastore TO $POSTGRES_USER;
EOSQL
EOF

chmod +x config/postgres/init-databases.sh

# Hive Metastore configuration
cat > config/hive/metastore-site.xml << 'EOF'
<?xml version="1.0"?>
<?xml-stylesheet type="text/xsl" href="configuration.xsl"?>
<configuration>
    <property>
        <name>metastore.thrift.uris</name>
        <value>thrift://hive-metastore:9083</value>
    </property>
    <property>
        <name>metastore.task.threads.always</name>
        <value>org.apache.hadoop.hive.metastore.events.EventCleanerTask</value>
    </property>
    <property>
        <name>metastore.expression.proxy</name>
        <value>org.apache.hadoop.hive.metastore.DefaultPartitionExpressionProxy</value>
    </property>
    <property>
        <name>javax.jdo.option.ConnectionDriverName</name>
        <value>org.postgresql.Driver</value>
    </property>
    <property>
        <name>javax.jdo.option.ConnectionURL</name>
        <value>jdbc:postgresql://postgres:5432/metastore</value>
    </property>
    <property>
        <name>javax.jdo.option.ConnectionUserName</name>
        <value>admin</value>
    </property>
    <property>
        <name>javax.jdo.option.ConnectionPassword</name>
        <value>admin123</value>
    </property>
    <property>
        <name>fs.s3a.endpoint</name>
        <value>http://minio:9000</value>
    </property>
    <property>
        <name>fs.s3a.access.key</name>
        <value>minioadmin</value>
    </property>
    <property>
        <name>fs.s3a.secret.key</name>
        <value>minioadmin123</value>
    </property>
    <property>
        <name>fs.s3a.path.style.access</name>
        <value>true</value>
    </property>
    <property>
        <name>fs.s3a.impl</name>
        <value>org.apache.hadoop.fs.s3a.S3AFileSystem</value>
    </property>
</configuration>
EOF

# Spark configuration
cat > config/spark/spark-defaults.conf << 'EOF'
spark.master                     spark://spark-master:7077
spark.eventLog.enabled           true
spark.eventLog.dir               /opt/bitnami/spark/work/events
spark.history.fs.logDirectory    /opt/bitnami/spark/work/events

# S3/MinIO Configuration
spark.hadoop.fs.s3a.endpoint            http://minio:9000
spark.hadoop.fs.s3a.access.key          minioadmin
spark.hadoop.fs.s3a.secret.key          minioadmin123
spark.hadoop.fs.s3a.path.style.access   true
spark.hadoop.fs.s3a.impl                org.apache.hadoop.fs.s3a.S3AFileSystem
spark.hadoop.fs.s3a.connection.ssl.enabled  false

# Hive Metastore
spark.sql.catalogImplementation         hive
spark.sql.warehouse.dir                 s3a://warehouse/
spark.hive.metastore.uris              thrift://hive-metastore:9083

# Performance
spark.sql.adaptive.enabled              true
spark.sql.adaptive.coalescePartitions.enabled  true
EOF

# Trino configuration
cat > config/trino/config.properties << 'EOF'
coordinator=true
node-scheduler.include-coordinator=true
http-server.http.port=8080
discovery.uri=http://localhost:8080
query.max-memory=2GB
query.max-memory-per-node=1GB
EOF

# Trino Hive catalog
cat > config/trino/catalog/hive.properties << 'EOF'
connector.name=hive
hive.metastore.uri=thrift://hive-metastore:9083
hive.s3.endpoint=http://minio:9000
hive.s3.path-style-access=true
hive.s3.aws-access-key=minioadmin
hive.s3.aws-secret-key=minioadmin123
hive.s3.ssl.enabled=false
hive.non-managed-table-writes-enabled=true
hive.allow-drop-table=true
EOF

# Trino Memory catalog (para testes)
cat > config/trino/catalog/memory.properties << 'EOF'
connector.name=memory
EOF

# Superset configuration
cat > config/superset/superset_config.py << 'EOF'
import os

# Database
SQLALCHEMY_DATABASE_URI = 'postgresql://admin:admin123@postgres:5432/superset'

# Security
SECRET_KEY = os.environ.get('SUPERSET_SECRET_KEY', 'thisISaSECRET_1234')

# Feature flags
FEATURE_FLAGS = {
    "ENABLE_TEMPLATE_PROCESSING": True,
    "DASHBOARD_NATIVE_FILTERS": True,
}

# Cache
CACHE_CONFIG = {
    'CACHE_TYPE': 'SimpleCache',
    'CACHE_DEFAULT_TIMEOUT': 300
}
EOF

echo -e "${GREEN}✅ Arquivos de configuração criados!${NC}"

# Verificar se Docker está rodando
echo -e "${YELLOW}🐋 Verificando Docker...${NC}"
if ! docker info > /dev/null 2>&1; then
    echo -e "${RED}❌ Docker não está rodando. Por favor, inicie o Docker e tente novamente.${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Docker está rodando!${NC}"

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}✨ Setup concluído com sucesso!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo -e "${YELLOW}📍 Dados serão persistidos em:${NC}"
echo -e "   ${GREEN}$DATA_ROOT${NC}"
echo ""
echo -e "${YELLOW}Próximos passos:${NC}"
echo ""
echo -e "1. Revisar variáveis de ambiente no arquivo ${GREEN}.env${NC}"
echo -e "2. Iniciar os serviços:"
echo -e "   ${GREEN}docker-compose up -d${NC}"
echo ""
echo -e "3. Aguardar todos os serviços subirem (pode levar alguns minutos)"
echo -e "   ${GREEN}docker-compose ps${NC}"
echo ""
echo -e "4. Acessar as interfaces:"
echo -e "   - MinIO:    ${GREEN}http://localhost:9001${NC} (minioadmin / minioadmin123)"
echo -e "   - Airflow:  ${GREEN}http://localhost:8080${NC} (airflow / airflow)"
echo -e "   - Superset: ${GREEN}http://localhost:8088${NC} (admin / admin)"
echo -e "   - Trino:    ${GREEN}http://localhost:8085${NC} (trino / sem senha)"
echo -e "   - Spark:    ${GREEN}http://localhost:8081${NC}"
echo ""
echo -e "${YELLOW}Para logs:${NC} ${GREEN}docker-compose logs -f${NC}"
echo -e "${YELLOW}Para parar:${NC} ${GREEN}docker-compose down${NC}"
echo ""
