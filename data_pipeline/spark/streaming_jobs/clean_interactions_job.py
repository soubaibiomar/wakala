from pyspark.sql import SparkSession
from pyspark.sql.functions import col, to_timestamp, row_number, when
from pyspark.sql.window import Window

VALID_ACTIONS = ("view", "click", "favorite", "unfavorite",
                 "contact", "share", "search", "recommendation_click")

JDBC_URL = "jdbc:postgresql://postgres:5432/automind"
JDBC_PROPS = {
    "user": "automind_user",
    "password": "automind_secret_password",
    "driver": "org.postgresql.Driver",
}


def run_job():
    spark = SparkSession.builder \
        .appName("AutoMind-CleanInteractions") \
        .config("spark.sql.streaming.checkpointLocation",
                "/data/checkpoints/silver_interactions") \
        .config("spark.jars",
                "/opt/spark/jars/postgresql-42.7.4.jar") \
        .getOrCreate()

    bronze_df = spark.readStream \
        .option("basePath", "/data/bronze/interactions") \
        .parquet("/data/bronze/interactions")

    cleaned = bronze_df \
        .filter(col("user_id").isNotNull() & col("vehicle_id").isNotNull()) \
        .filter(col("action").isin(VALID_ACTIONS)) \
        .withColumn("event_ts", to_timestamp(col("timestamp")))

    win = Window.partitionBy("interaction_id").orderBy(col("event_ts").desc())
    deduped = cleaned.withColumn("rn", row_number().over(win)) \
        .filter(col("rn") == 1).drop("rn")

    silver_query = deduped.writeStream \
        .format("parquet") \
        .option("path", "/data/silver/interactions") \
        .option("checkpointLocation", "/data/checkpoints/silver_interactions") \
        .partitionBy("dt") \
        .trigger(processingTime="30 seconds") \
        .outputMode("append") \
        .start()

    def write_to_postgres(batch_df, batch_id):
        batch_df \
            .select(
                col("interaction_id"), col("user_id"), col("vehicle_id"),
                col("action"), col("session_id"), col("source"),
                col("search_query"), col("recommendation_method"),
                col("duration_seconds"), col("device_type"),
                col("user_agent"), col("timestamp"),
            ) \
            .write \
            .jdbc(url=JDBC_URL, table="interactions",
                  mode="append", properties=JDBC_PROPS)
        print(f"  PostgreSQL: batch {batch_id} ecrit ({batch_df.count()} rows)")

    pg_query = deduped.writeStream \
        .foreachBatch(write_to_postgres) \
        .trigger(processingTime="30 seconds") \
        .outputMode("append") \
        .start()

    silver_query.awaitTermination()
    pg_query.awaitTermination()


if __name__ == "__main__":
    run_job()
