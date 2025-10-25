FROM apache/superset:3.1.1

# Mudar para usuário root para instalar dependências
USER root

# Instalar drivers de banco de dados
RUN pip install --no-cache-dir \
	psycopg2-binary>=2.9.0 \
	trino>=0.328.0 \
	sqlalchemy-trino>=0.5.0 \
	redis>=5.0.0 \
	celery>=5.3.0

# Voltar para usuário superset
USER superset

