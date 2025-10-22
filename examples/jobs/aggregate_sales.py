"""
Job Spark: Agregações e análises (Silver -> Gold)
"""

from pyspark.sql import SparkSession
from pyspark.sql.functions import col, sum as _sum, count, avg, round as _round
import sys


def main(execution_date):
    """
    Agrega dados processados e cria tabelas analíticas no bucket gold

    Args:
        execution_date: Data de execução no formato YYYYMMDD
    """

    # Criar SparkSession
    spark = SparkSession.builder \
        .appName("Aggregate Sales - Silver to Gold") \
        .config("spark.hadoop.fs.s3a.endpoint", "http://minio:9000") \
        .config("spark.hadoop.fs.s3a.access.key", "minioadmin") \
        .config("spark.hadoop.fs.s3a.secret.key", "minioadmin123") \
        .config("spark.hadoop.fs.s3a.path.style.access", "true") \
        .config("spark.hadoop.fs.s3a.impl", "org.apache.hadoop.fs.s3a.S3AFileSystem") \
        .config("spark.sql.catalogImplementation", "hive") \
        .config("hive.metastore.uris", "thrift://hive-metastore:9083") \
        .getOrCreate()

    print(f"🚀 Iniciando agregações para data: {execution_date}")

    # Ler dados do silver
    input_path = f"s3a://silver/processed/sales/date={execution_date}"
    print(f"📥 Lendo dados de: {input_path}")

    df = spark.read.parquet(input_path)
    print(f"📊 Registros lidos: {df.count()}")

    # 1. Agregação por categoria de produto
    print("\n📊 Agregando por categoria...")
    df_by_category = df.groupBy("product_category", "year", "month") \
        .agg(
            _sum("total_amount").alias("total_revenue"),
            _sum("quantity").alias("total_quantity"),
            count("transaction_id").alias("total_transactions"),
            avg("unit_price").alias("avg_price")
    ) \
        .withColumn("avg_price", _round(col("avg_price"), 2)) \
        .withColumn("total_revenue", _round(col("total_revenue"), 2))

    # Salvar agregação por categoria
    output_category = "s3a://gold/analytics/sales_by_category"
    df_by_category.write \
        .mode("overwrite") \
        .partitionBy("year", "month") \
        .parquet(output_category)

    print(f"✅ Salvo em: {output_category}")
    df_by_category.show(10)

    # 2. Agregação por região
    print("\n🌍 Agregando por região...")
    df_by_region = df.groupBy("region", "year", "month") \
        .agg(
            _sum("total_amount").alias("total_revenue"),
            count("transaction_id").alias("total_transactions"),
            count("customer_id").alias("unique_customers")
    ) \
        .withColumn("total_revenue", _round(col("total_revenue"), 2))

    # Salvar agregação por região
    output_region = "s3a://gold/analytics/sales_by_region"
    df_by_region.write \
        .mode("overwrite") \
        .partitionBy("year", "month") \
        .parquet(output_region)

    print(f"✅ Salvo em: {output_region}")
    df_by_region.show(10)

    # 3. Top produtos
    print("\n🏆 Top 20 produtos...")
    df_top_products = df.groupBy("product_name", "product_category") \
        .agg(
            _sum("total_amount").alias("total_revenue"),
            _sum("quantity").alias("total_sold")
    ) \
        .orderBy(col("total_revenue").desc()) \
        .limit(20) \
        .withColumn("total_revenue", _round(col("total_revenue"), 2))

    # Salvar top produtos
    output_top_products = f"s3a://gold/analytics/top_products/date={execution_date}"
    df_top_products.write \
        .mode("overwrite") \
        .parquet(output_top_products)

    print(f"✅ Salvo em: {output_top_products}")
    df_top_products.show(20)

    # 4. Métricas diárias consolidadas
    print("\n📅 Métricas diárias...")
    df_daily_metrics = df.groupBy("transaction_date") \
        .agg(
            _sum("total_amount").alias("daily_revenue"),
            count("transaction_id").alias("daily_transactions"),
            count("customer_id").alias("daily_customers"),
            avg("total_amount").alias("avg_ticket")
    ) \
        .withColumn("daily_revenue", _round(col("daily_revenue"), 2)) \
        .withColumn("avg_ticket", _round(col("avg_ticket"), 2)) \
        .orderBy("transaction_date")

    # Salvar métricas diárias
    output_daily = "s3a://gold/analytics/daily_metrics"
    df_daily_metrics.write \
        .mode("append") \
        .parquet(output_daily)

    print(f"✅ Salvo em: {output_daily}")
    df_daily_metrics.show()

    # Registrar tabelas no Hive Metastore (para acesso via Trino)
    print("\n📋 Registrando tabelas no Hive Metastore...")

    # Criar database se não existe
    spark.sql("CREATE DATABASE IF NOT EXISTS sales")

    # Registrar tabela silver
    df.createOrReplaceTempView("sales_temp")
    spark.sql(f"""
        CREATE TABLE IF NOT EXISTS sales.sales_silver
        USING parquet
        LOCATION 's3a://silver/processed/sales/'
    """)

    # Registrar tabelas gold
    spark.sql(f"""
        CREATE TABLE IF NOT EXISTS sales.sales_by_category
        USING parquet
        LOCATION '{output_category}'
    """)

    spark.sql(f"""
        CREATE TABLE IF NOT EXISTS sales.sales_by_region
        USING parquet
        LOCATION '{output_region}'
    """)

    spark.sql(f"""
        CREATE TABLE IF NOT EXISTS sales.daily_metrics
        USING parquet
        LOCATION '{output_daily}'
    """)

    print("✅ Tabelas registradas no Hive Metastore")
    print("\nTabelas disponíveis para consulta via Trino:")
    print("  - sales.sales_silver")
    print("  - sales.sales_by_category")
    print("  - sales.sales_by_region")
    print("  - sales.daily_metrics")

    # Resumo final
    print("\n" + "=" * 60)
    print("📈 RESUMO DAS AGREGAÇÕES")
    print("=" * 60)
    print(f"✅ Agregações por categoria: {df_by_category.count()} registros")
    print(f"✅ Agregações por região: {df_by_region.count()} registros")
    print(f"✅ Top produtos: {df_top_products.count()} registros")
    print(f"✅ Métricas diárias: {df_daily_metrics.count()} registros")
    print("=" * 60)

    spark.stop()
    print("\n✅ Agregações concluídas com sucesso!")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        execution_date = sys.argv[1]
    else:
        from datetime import datetime
        execution_date = datetime.now().strftime('%Y%m%d')

    main(execution_date)
