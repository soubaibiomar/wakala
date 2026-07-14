from pyspark.sql import SparkSession
from pathlib import Path

TRIGGER_FILE = Path("/data/triggers/retrain_embeddings")
THRESHOLD = 10_000


def run_job():
    spark = SparkSession.builder \
        .appName("AutoMind-RetrainTrigger") \
        .getOrCreate()

    interactions = spark.read.parquet("/data/gold/views_per_vehicle")
    total = interactions.count()

    if total > THRESHOLD:
        TRIGGER_FILE.parent.mkdir(parents=True, exist_ok=True)
        TRIGGER_FILE.write_text(str(total))
        print(f"Trigger active: {total} interactions (> {THRESHOLD})")
    else:
        if TRIGGER_FILE.exists():
            TRIGGER_FILE.unlink()
        print(f"Trigger inactif: {total} interactions (<= {THRESHOLD})")

    spark.stop()


if __name__ == "__main__":
    run_job()
