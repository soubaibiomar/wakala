"""
Spark Batch Job — Agrégations Silver → Gold layer.
Calcule les métriques agrégées pour le dashboard et les modèles ML.
"""

from pyspark.sql import SparkSession
from pyspark.sql.functions import avg, count, col, stddev


def run_batch_aggregation():
    """Agrège les données Silver en métriques Gold."""
    spark = SparkSession.builder \
        .appName("AutoMind-BatchGold") \
        .getOrCreate()

    # Lecture Silver
    silver_df = spark.read.parquet("/data/silver/vehicles")

    # ─── Agrégation 1 : Prix moyen par marque/modèle/carburant ──
    price_agg = silver_df.groupBy("brand", "model", "fuel_type").agg(
        avg("price").alias("avg_price"),
        stddev("price").alias("std_price"),
        count("*").alias("listing_count"),
        avg("mileage").alias("avg_mileage"),
    )
    price_agg.write.mode("overwrite").parquet("/data/gold/price_aggregations")

    # ─── Agrégation 2 : Profil vendeur ─────────────────────────
    seller_agg = silver_df.groupBy("seller_id").agg(
        count("*").alias("total_listings"),
        avg("price").alias("avg_listing_price"),
    )
    seller_agg.write.mode("overwrite").parquet("/data/gold/seller_profiles")

    # ─── Agrégation 3 : Distribution par type de carburant ────
    fuel_dist = silver_df.groupBy("fuel_type").agg(
        count("*").alias("count"),
        avg("price").alias("avg_price"),
    )
    fuel_dist.write.mode("overwrite").parquet("/data/gold/fuel_distribution")

    spark.stop()
    print("✅ Batch Gold terminé.")


if __name__ == "__main__":
    run_batch_aggregation()
