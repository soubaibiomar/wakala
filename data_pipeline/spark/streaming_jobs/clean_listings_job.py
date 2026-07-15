from pyspark.sql import SparkSession
from pyspark.sql.functions import col, lower, trim, row_number, when, to_timestamp
from pyspark.sql.window import Window


def run_job():
    spark = SparkSession.builder \
        .appName("Wakala-CleanListings") \
        .config("spark.sql.streaming.checkpointLocation",
                "/data/checkpoints/silver_listings") \
        .getOrCreate()

    bronze_df = spark.readStream \
        .option("basePath", "/data/bronze/listings") \
        .parquet("/data/bronze/listings")

    cleaned = bronze_df \
        .withColumn("brand",
                    when(trim(col("brand")) == "", "unknown")
                    .otherwise(trim(col("brand")))) \
        .withColumn("city",
                    when(trim(col("city")) == "", "unknown")
                    .otherwise(trim(col("city")))) \
        .withColumn("fuel_type", lower(trim(col("fuel_type")))) \
        .withColumn("body_type", lower(trim(col("body_type")))) \
        .withColumn("transmission", lower(trim(col("transmission")))) \
        .withColumn("price", col("price").cast("int")) \
        .withColumn("year", col("year").cast("int")) \
        .withColumn("mileage", col("mileage").cast("int")) \
        .withColumn("event_ts", to_timestamp(col("timestamp")))

    win = Window.partitionBy("vehicle_id").orderBy(col("event_ts").desc())
    deduped = cleaned.withColumn("rn", row_number().over(win)) \
        .filter(col("rn") == 1).drop("rn", "event_ts")

    query = deduped.writeStream \
        .format("parquet") \
        .option("path", "/data/silver/listings") \
        .option("checkpointLocation", "/data/checkpoints/silver_listings") \
        .partitionBy("dt") \
        .trigger(processingTime="30 seconds") \
        .outputMode("append") \
        .start()

    query.awaitTermination()


if __name__ == "__main__":
    run_job()
