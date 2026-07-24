"""
Airflow DAG — Orchestration du pipeline batch quotidien.
Silver → Gold → Entraînement modèles ML → Mise à jour embeddings.
"""

from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator

default_args = {
    "owner": "wakala",
    "depends_on_past": False,
    "email_on_failure": False,
    "retries": 2,
    "retry_delay": timedelta(minutes=5),
}

with DAG(
    dag_id="wakala_daily_pipeline",
    default_args=default_args,
    description="Pipeline batch quotidien : Gold aggregations → ML training → Embeddings",
    schedule_interval="0 2 * * *",  # Tous les jours à 2h du matin
    start_date=datetime(2024, 1, 1),
    catchup=False,
    tags=["wakala", "ml", "batch"],
) as dag:

    # ─── Étape 1 : Agrégation Gold ────────────────────────────
    gold_aggregation = BashOperator(
        task_id="silver_to_gold",
        bash_command="spark-submit /opt/spark/batch_jobs/silver_to_gold.py",
    )

    # ─── Étape 2 : Entraînement XGBoost (prix) ───────────────
    train_price_model = BashOperator(
        task_id="train_price_model",
        bash_command="python /app/ml/pricing/train.py",
    )

    # ─── Étape 3 : Détection d'anomalies ─────────────────────
    run_anomaly_detection = BashOperator(
        task_id="anomaly_detection",
        bash_command="python /app/ml/anomaly/batch_detect.py",
    )

    # ─── Étape 4 : Mise à jour des embeddings ────────────────
    update_embeddings = BashOperator(
        task_id="update_embeddings",
        bash_command="python /app/rag/batch_embed.py",
    )

    # Pipeline : Gold → (Price + Anomaly en parallèle) → Embeddings
    gold_aggregation >> [train_price_model, run_anomaly_detection] >> update_embeddings
