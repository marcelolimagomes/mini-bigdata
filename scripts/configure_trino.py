#!/usr/bin/env python3
"""
configure_trino.py - Configura schemas e tabelas no Trino/Hive
"""

from trino.dbapi import connect

# Configuração
TRINO_HOST = "localhost"
TRINO_PORT = 8080
TRINO_USER = "trino"
TRINO_CATALOG = "hive"


def get_connection():
    """Cria conexão com Trino"""
    return connect(
        host=TRINO_HOST,
        port=TRINO_PORT,
        user=TRINO_USER,
        catalog=TRINO_CATALOG,
        schema="default"
    )


def execute_sql(cursor, sql, description=""):
    """Executa SQL e mostra resultado"""
    try:
        cursor.execute(sql)
        print(f"  ✅ {description}")
        return True
    except Exception as e:
        print(f"  ⚠️  {description}: {str(e)[:100]}")
        return False


def setup_trino():
    """Configura schemas e tabelas no Trino"""

    print("🔍 Configurando Trino/Hive Metastore...\n")

    conn = get_connection()
    cursor = conn.cursor()

    # 1. Criar Schemas
    print("📁 Criando schemas...")

    schemas = [
        ("vendas", "s3a://gold/vendas/", "Schema para dados de vendas"),
        ("logs", "s3a://gold/logs/", "Schema para logs de aplicação"),
        ("analytics", "s3a://gold/analytics/", "Schema para análises")
    ]

    for schema_name, location, comment in schemas:
        sql = f"""
        CREATE SCHEMA IF NOT EXISTS hive.{schema_name}
        WITH (location = '{location}')
        """
        execute_sql(cursor, sql, f"Schema '{schema_name}' criado")

    # 2. Criar Tabelas Externas
    print("\n📊 Criando tabelas...")

    # Tabela: vendas_raw (Bronze - CSV)
    execute_sql(cursor, """
        CREATE TABLE IF NOT EXISTS hive.vendas.vendas_raw (
            data VARCHAR,
            pedido_id VARCHAR,
            cliente_id VARCHAR,
            produto VARCHAR,
            quantidade INTEGER,
            valor DOUBLE
        )
        WITH (
            external_location = 's3a://bronze/vendas/',
            format = 'CSV',
            skip_header_line_count = 1
        )
    """, "Tabela 'vendas_raw' (Bronze)")

    # Tabela: vendas_silver (Silver - Parquet Particionado)
    execute_sql(cursor, """
        CREATE TABLE IF NOT EXISTS hive.vendas.vendas_silver (
            pedido_id VARCHAR,
            cliente_id VARCHAR,
            produto VARCHAR,
            quantidade INTEGER,
            valor DOUBLE,
            valor_total DOUBLE,
            data DATE,
            ano INTEGER,
            mes INTEGER
        )
        WITH (
            external_location = 's3a://silver/vendas/',
            format = 'PARQUET',
            partitioned_by = ARRAY['ano', 'mes']
        )
    """, "Tabela 'vendas_silver' (Silver)")

    # Tabela: vendas_agregadas (Gold - Parquet)
    execute_sql(cursor, """
        CREATE TABLE IF NOT EXISTS hive.vendas.vendas_agregadas (
            produto VARCHAR,
            total_vendas BIGINT,
            quantidade_total BIGINT,
            receita_total DOUBLE,
            ticket_medio DOUBLE,
            ano INTEGER,
            mes INTEGER
        )
        WITH (
            external_location = 's3a://gold/vendas/agregadas/',
            format = 'PARQUET'
        )
    """, "Tabela 'vendas_agregadas' (Gold)")

    # 3. Criar Views
    print("\n👁️  Criando views...")

    execute_sql(cursor, """
        CREATE OR REPLACE VIEW hive.analytics.vendas_mensais AS
        SELECT 
            ano,
            mes,
            COUNT(*) as total_pedidos,
            SUM(quantidade) as quantidade_total,
            SUM(valor_total) as receita_total,
            AVG(valor_total) as ticket_medio
        FROM hive.vendas.vendas_silver
        GROUP BY ano, mes
    """, "View 'vendas_mensais'")

    execute_sql(cursor, """
        CREATE OR REPLACE VIEW hive.analytics.top_produtos AS
        SELECT 
            produto,
            COUNT(*) as total_vendas,
            SUM(quantidade) as quantidade_vendida,
            SUM(valor_total) as receita_total
        FROM hive.vendas.vendas_silver
        GROUP BY produto
        ORDER BY receita_total DESC
    """, "View 'top_produtos'")

    # 4. Listar recursos criados
    print("\n📋 Recursos criados:")

    print("\n  Schemas:")
    cursor.execute("SHOW SCHEMAS IN hive")
    for row in cursor.fetchall():
        if row[0] not in ['default', 'information_schema']:
            print(f"    - {row[0]}")

    print("\n  Tabelas em 'vendas':")
    try:
        cursor.execute("SHOW TABLES IN hive.vendas")
        for row in cursor.fetchall():
            print(f"    - {row[0]}")
    except:
        print("    (nenhuma tabela ainda)")

    print("\n  Views em 'analytics':")
    try:
        cursor.execute("SHOW TABLES IN hive.analytics")
        for row in cursor.fetchall():
            print(f"    - {row[0]}")
    except:
        print("    (nenhuma view ainda)")

    cursor.close()
    conn.close()

    print("\n✅ Configuração do Trino concluída!")


if __name__ == "__main__":
    setup_trino()
