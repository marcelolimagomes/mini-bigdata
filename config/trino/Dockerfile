FROM trinodb/trino:435

USER root

# Versões compatíveis
ENV HADOOP_VERSION=3.3.6

# Download e instalação do Hadoop AWS JAR e dependências S3A
RUN cd /usr/lib/trino/plugin/hive && \
	curl -L -o hadoop-aws-${HADOOP_VERSION}.jar \
	https://repo1.maven.org/maven2/org/apache/hadoop/hadoop-aws/${HADOOP_VERSION}/hadoop-aws-${HADOOP_VERSION}.jar && \
	curl -L -o hadoop-common-${HADOOP_VERSION}.jar \
	https://repo1.maven.org/maven2/org/apache/hadoop/hadoop-common/${HADOOP_VERSION}/hadoop-common-${HADOOP_VERSION}.jar && \
	curl -L -o hadoop-auth-${HADOOP_VERSION}.jar \
	https://repo1.maven.org/maven2/org/apache/hadoop/hadoop-auth/${HADOOP_VERSION}/hadoop-auth-${HADOOP_VERSION}.jar

# Copiar configuração Hadoop core-site.xml
COPY ./core-site.xml /etc/trino/core-site.xml

# Ajustar permissões
RUN chown -R trino:trino /usr/lib/trino/plugin/hive && \
	chown trino:trino /etc/trino/core-site.xml

USER trino

# Verificar instalação
RUN ls -lh /usr/lib/trino/plugin/hive/hadoop-*.jar
