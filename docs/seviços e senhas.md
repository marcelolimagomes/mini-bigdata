# Serviços e Senhas

## Tabela de Serviços

| Serviço | URL | Usuário | Senha | Observações |
|---------|-----|---------|-------|-------------|
| **Airflow** | http://localhost:8082 | `airflow` | `airflow` | Interface web de orquestração |
| **Spark Master** | http://localhost:8080 | - | - | Dashboard do Spark (sem autenticação) |
| **Spark Worker** | http://localhost:8081 | - | - | Dashboard do Worker (sem autenticação) |
| **Trino** | http://localhost:8085 | - | - | Query engine (sem autenticação web) |
| **Superset** | http://localhost:8088 | `admin` | `admin` | Plataforma de BI e dashboards |
| **MinIO Console** | http://localhost:9001 | `minioadmin` | `minioadmin123` | Interface web do object storage |
| **MinIO API** | http://localhost:9000 | `minioadmin` | `minioadmin123` | Endpoint S3-compatible |
| **PostgreSQL** | localhost:5432 | `admin` | `admin123` | Databases: airflow, superset, metastore |
| **Hive Metastore** | localhost:9083 | - | - | Serviço Thrift (sem interface web) |
| **Redis** | localhost:6379 | - | - | Cache/broker (sem autenticação) |

## Conexões JDBC/SQL

### PostgreSQL
- **Host:** localhost
- **Port:** 5432
- **User:** `admin`
- **Password:** `admin123`
- **Databases:** airflow, superset, metastore

### Trino (via JDBC)
- **URL:** `jdbc:trino://localhost:8085/`
- **User:** qualquer nome (sem senha necessária)

### MinIO (S3-compatible)
- **Endpoint:** http://localhost:9000
- **Access Key:** `minioadmin`
- **Secret Key:** `minioadmin123`
