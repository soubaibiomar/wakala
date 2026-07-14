from pyspark.sql import SparkSession
from pyspark.sql.functions import (
    avg, count, col, stddev, sum as _sum, countDistinct, when,
)


def run_job(date_str: str | None = None):
    spark = SparkSession.builder \
        .appName("AutoMind-GoldAggregation") \
        .getOrCreate()

    filter_expr = f"dt = '{date_str}'" if date_str else "1 = 1"

    listings = spark.read.parquet("/data/silver/listings") \
        .filter(filter_expr)
    interactions = spark.read.parquet("/data/silver/interactions") \
        .filter(filter_expr)

    views_per_vehicle = interactions.groupBy("vehicle_id").agg(
        _sum(when(col("action") == "view", col("duration_seconds"))
             .otherwise(0)).alias("total_view_duration"),
        count(when(col("action") == "view", 1)).alias("view_count"),
        count(when(col("action") == "click", 1)).alias("click_count"),
        count(when(col("action") == "favorite", 1)).alias("favorite_count"),
        count(when(col("action") == "contact", 1)).alias("contact_count"),
    )
    views_per_vehicle.write.mode("overwrite") \
        .parquet("/data/gold/views_per_vehicle")

    price_trends = listings.groupBy("city", "body_type", "dt").agg(
        avg("price").alias("avg_price"),
        stddev("price").alias("std_price"),
        count("*").alias("listing_count"),
        avg("mileage").alias("avg_mileage"),
    )
    price_trends.write.mode("overwrite") \
        .parquet("/data/gold/price_trends_by_region")

    interaction_volume = interactions.groupBy("source", "action").agg(
        count("*").alias("event_count"),
        countDistinct("user_id").alias("unique_users"),
    )
    interaction_volume.write.mode("overwrite") \
        .parquet("/data/gold/interaction_volume_by_segment")

    spark.stop()
    print(f"Gold aggregation terminee pour dt={date_str or 'toutes'}")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--date", type=str, default=None)
    args = parser.parse_args()
    run_job(args.date)
