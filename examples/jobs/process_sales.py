"""
Job Spark: Processar dados brutos (Bronze -> Silver)
"""

from pyspark.sql import SparkSession
from pyspark.sql.functions import col, to_date, year, month, dayofmonth
import sys


def main(execution_date):
    """
    Processa dados brutos do bucket bronze e salva no bucket silver

    Args:
        execution_date: Data de execução no formato YYYYMMDD
    """

    # Criar SparkSession
    spark = SparkSession.builder \
        .appName("Process Sales - Bronze to Silver") \
        .config("spark.hadoop.fs.s3a.endpoint", "http://minio:9000") \
        .config("spark.hadoop.fs.s3a.access.key", "minioadmin") \
        .config("spark.hadoop.fs.s3a.secret.key", "minioadmin123") \
        .config("spark.hadoop.fs.s3a.path.style.access", "true") \
        .config("spark.hadoop.fs.s3a.impl", "org.apache.hadoop.fs.s3a.S3AFileSystem") \
        .config("spark.hadoop.fs.s3a.connection.ssl.enabled", "false") \
        .getOrCreate()

    print(f"🚀 Iniciando processamento para data: {execution_date}")

    # Ler dados brutos do bronze
    input_path = f"s3a://bronze/raw/sales/sales_{execution_date}.csv"
    print(f"📥 Lendo dados de: {input_path}")

    df = spark.read \
        .option("header", "true") \
        .option("inferSchema", "true") \
        .csv(input_path)

    print(f"📊 Registros lidos: {df.count()}")

    # Transformações
    df_transformed = df \
        .withColumn("transaction_date", to_date(col("transaction_date"))) \
        .withColumn("year", year(col("transaction_date"))) \
        .withColumn("month", month(col("transaction_date"))) \
        .withColumn("day", dayofmonth(col("transaction_date"))) \
        .filter(col("quantity") > 0) \
        .filter(col("unit_price") > 0) \
        .dropDuplicates(["transaction_id"])

    # Adicionar colunas calculadas
    df_transformed = df_transformed \
        .withColumn("total_amount", col("quantity") * col("unit_price"))

    print(f"✨ Transformações aplicadas")
    print(f"📊 Registros após transformação: {df_transformed.count()}")

    # Salvar no bucket silver (formato Parquet particionado)
    output_path = f"s3a://silver/processed/sales/date={execution_date}"
    print(f"💾 Salvando dados em: {output_path}")

    df_transformed.write \
        .mode("overwrite") \
        .parquet(output_path)

    # Também salvar uma cópia em CSV para fácil acesso
    df_transformed.coalesce(1).write \
        .mode("overwrite") \
        .option("header", "true") \
        .csv(f"{output_path}")

    # Estatísticas
    print("\n" + "=" * 50)
    print("📈 ESTATÍSTICAS DO PROCESSAMENTO")
    print("=" * 50)

    stats = df_transformed.agg({
        "total_amount": "sum",
        "quantity": "sum",
        "transaction_id": "count"
    }).collect()[0]

    print(f"Total de transações: {stats['count(transaction_id)']:,}")
    print(f"Total de itens vendidos: {stats['sum(quantity)']:,}")
    print(f"Receita total: ${stats['sum(total_amount)']:,.2f}")

    print("\nTop 5 categorias por volume:")
    df_transformed.groupBy("product_category") \
        .sum("total_amount") \
        .orderBy(col("sum(total_amount)").desc()) \
        .show(5)

    print("\n✅ Processamento concluído com sucesso!")

    spark.stop()


if __name__ == "__main__":
    if len(sys.argv) > 1:
        execution_date = sys.argv[1]
    else:
        from datetime import datetime
        execution_date = datetime.now().strftime('%Y%m%d')

    main(execution_date)
