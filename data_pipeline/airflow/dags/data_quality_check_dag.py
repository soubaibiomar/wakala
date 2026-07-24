from datetime import datetime, timedelta
from pathlib import Path

from airflow import DAG
from airflow.operators.python import PythonOperator

QUALITY_DIR = Path("/data/quality_checks")
BRONZE_L = Path("/data/bronze/listings")
BRONZE_I = Path("/data/bronze/interactions")
SILVER_L = Path("/data/silver/listings")
SILVER_I = Path("/data/silver/interactions")
GOLD = Path("/data/gold")


def _count_parquet(path: Path) -> int:
    if not path.exists():
        return 0
    return sum(1 for _ in path.rglob("*.parquet"))


def _check_quality(**context):
    QUALITY_DIR.mkdir(parents=True, exist_ok=True)
    report = QUALITY_DIR / f"check_{datetime.now().strftime('%Y%m%d_%H%M')}.txt"

    counts = {
        "bronze_listings": _count_parquet(BRONZE_L),
        "bronze_interactions": _count_parquet(BRONZE_I),
        "silver_listings": _count_parquet(SILVER_L),
        "silver_interactions": _count_parquet(SILVER_I),
        "gold_views": _count_parquet(GOLD / "views_per_vehicle"),
        "gold_price_trends": _count_parquet(GOLD / "price_trends_by_region"),
    }

    with open(report, "w") as f:
        f.write(f"Quality check: {datetime.now().isoformat()}\n")
        f.write("=" * 40 + "\n")
        for layer, cnt in counts.items():
            f.write(f"{layer:30s} : {cnt:>6d} fichiers\n")
        anomalies = [k for k, v in counts.items() if v == 0]
        if anomalies:
            f.write("\nANOMALIES: couches vides\n")
            for a in anomalies:
                f.write(f"  - {a}\n")
        else:
            f.write("\nAucune anomalie detectee.\n")

    print(report.read_text())


default_args = {
    "owner": "wakala",
    "depends_on_past": False,
    "retries": 1,
    "retry_delay": timedelta(minutes=2),
}

with DAG(
    dag_id="data_quality_check",
    default_args=default_args,
    description="Verification horaire de la qualite des donnees",
    schedule="0 * * * *",
    start_date=datetime(2024, 1, 1),
    catchup=False,
    tags=["wakala", "quality"],
) as dag:

    quality_check = PythonOperator(
        task_id="run_quality_check",
        python_callable=_check_quality,
    )
