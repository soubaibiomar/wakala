from datetime import datetime, timedelta
from pathlib import Path

from airflow import DAG
from airflow.exceptions import AirflowSkipException
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator

TRIGGER_FILE = Path("/data/triggers/retrain_embeddings")

default_args = {
    "owner": "automind",
    "depends_on_past": False,
    "email_on_failure": False,
    "retries": 2,
    "retry_delay": timedelta(minutes=5),
}


def _check_trigger(**context):
    if TRIGGER_FILE.exists():
        count = TRIGGER_FILE.read_text().strip()
        print(f"Trigger OK: {count} interactions -> lancement re-training")
        return count
    print("Aucun trigger - skip re-training")
    raise AirflowSkipException("Volume insuffisant pour re-training")


with DAG(
    dag_id="weekly_model_retrain",
    default_args=default_args,
    description="Re-training hebdomadaire des modeles ML",
    schedule="0 4 * * 0",
    start_date=datetime(2024, 1, 1),
    catchup=False,
    tags=["automind", "ml", "retrain"],
) as dag:

    check_trigger = PythonOperator(
        task_id="check_retrain_trigger",
        python_callable=_check_trigger,
    )

    update_embeddings = BashOperator(
        task_id="update_embeddings",
        bash_command="python /app/rag/batch_embed.py",
    )

    recompute_collab = BashOperator(
        task_id="recompute_collaborative_scores",
        bash_command=(
            "psql -U automind_user -d automind -h postgres "
            "-c 'REFRESH MATERIALIZED VIEW CONCURRENTLY mv_user_item_matrix;'"
        ),
    )

    clean_trigger = BashOperator(
        task_id="clean_retrain_trigger",
        bash_command="rm -f /data/triggers/retrain_embeddings",
    )

    retrain_pricing = BashOperator(
        task_id="retrain_pricing_model",
        bash_command="cd /app && python -m app.ml.pricing.train_pricing",
    )

    check_trigger >> update_embeddings >> recompute_collab >> retrain_pricing >> clean_trigger
