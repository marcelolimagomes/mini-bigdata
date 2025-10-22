FROM apache/hive:4.0.0

USER root

# Instalar ferramentas necessárias
RUN apt-get update && \
	apt-get install -y wget curl netcat-openbsd && \
	rm -rf /var/lib/apt/lists/*

# Baixar driver PostgreSQL JDBC
RUN wget -q https://jdbc.postgresql.org/download/postgresql-42.7.1.jar \
	-O /opt/hive/lib/postgresql-jdbc.jar

# Configurar variáveis de ambiente para Metastore
ENV DB_DRIVER=postgres
ENV SERVICE_NAME=metastore

USER hive

WORKDIR /opt/hive

ENTRYPOINT ["/entrypoint.sh"]
