"""
Spark Streaming Job — Traitement temps réel des événements véhicules.
Lit depuis Kafka, nettoie et écrit en Silver layer.
"""

from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json, col, current_timestamp
from pyspark.sql.types import StructType, StructField, StringType, IntegerType, FloatType


# ─── Schéma de l'événement ─────────────────────────────────────
vehicle_schema = StructType([
    StructField("event_type", StringType()),
    StructField("timestamp", StringType()),
    StructField("data", StructType([
        StructField("brand", StringType()),
        StructField("model", StringType()),
        StructField("year", IntegerType()),
        StructField("price", IntegerType()),
        StructField("mileage", IntegerType()),
        StructField("fuel_type", StringType()),
        StructField("body_type", StringType()),
        StructField("seller_id", StringType()),
    ])),
])


def run_streaming_job():
    """Lance le job de streaming Spark (Kafka → Silver)."""
    spark = SparkSession.builder \
        .appName("AutoMind-StreamingSilver") \
        .config("spark.jars.packages", "org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.0") \
        .getOrCreate()

    # Lecture depuis Kafka
    raw_df = spark.readStream \
        .format("kafka") \
        .option("kafka.bootstrap.servers", "kafka:29092") \
        .option("subscribe", "vehicle-events") \
        .option("startingOffsets", "latest") \
        .load()

    # Parsing JSON
    parsed_df = raw_df \
        .selectExpr("CAST(value AS STRING) as json_str") \
        .select(from_json(col("json_str"), vehicle_schema).alias("event")) \
        .select("event.data.*", "event.timestamp") \
        .withColumn("processed_at", current_timestamp())

    # Écriture en Silver layer (Parquet)
    query = parsed_df.writeStream \
        .format("parquet") \
        .option("path", "/data/silver/vehicles") \
        .option("checkpointLocation", "/data/checkpoints/silver_vehicles") \
        .outputMode("append") \
        .start()

    query.awaitTermination()


if __name__ == "__main__":
    run_streaming_job()
