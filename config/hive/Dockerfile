FROM apache/hive:4.0.0

USER root

# Versões compatíveis
ENV HADOOP_VERSION=3.3.6

# Instalar ferramentas necessárias
RUN apt-get update && \
	apt-get install -y wget curl netcat-openbsd && \
	rm -rf /var/lib/apt/lists/*

# Baixar driver PostgreSQL JDBC
RUN wget -q https://jdbc.postgresql.org/download/postgresql-42.7.1.jar \
	-O /opt/hive/lib/postgresql-jdbc.jar

# Baixar JARs Hadoop AWS para suporte S3A
RUN cd /opt/hive/lib && \
	wget -q https://repo1.maven.org/maven2/org/apache/hadoop/hadoop-aws/${HADOOP_VERSION}/hadoop-aws-${HADOOP_VERSION}.jar && \
	wget -q https://repo1.maven.org/maven2/org/apache/hadoop/hadoop-common/${HADOOP_VERSION}/hadoop-common-${HADOOP_VERSION}.jar && \
	wget -q https://repo1.maven.org/maven2/org/apache/hadoop/hadoop-auth/${HADOOP_VERSION}/hadoop-auth-${HADOOP_VERSION}.jar && \
	wget -q https://repo1.maven.org/maven2/com/amazonaws/aws-java-sdk-bundle/1.12.262/aws-java-sdk-bundle-1.12.262.jar

# Copiar configuração Hadoop core-site.xml
COPY ./core-site.xml /opt/hive/conf/core-site.xml

# Verificar JARs instalados
RUN ls -lh /opt/hive/lib/hadoop-*.jar /opt/hive/lib/aws-*.jar && \
	chown hive:hive /opt/hive/conf/core-site.xml

# Configurar variáveis de ambiente para Metastore
ENV DB_DRIVER=postgres
ENV SERVICE_NAME=metastore

USER hive

WORKDIR /opt/hive

ENTRYPOINT ["/entrypoint.sh"]
