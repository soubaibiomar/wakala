from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.bash import BashOperator

default_args = {
    "owner": "automind",
    "depends_on_past": False,
    "email_on_failure": False,
    "retries": 2,
    "retry_delay": timedelta(minutes=5),
}

with DAG(
    dag_id="daily_gold_aggregation",
    default_args=default_args,
    description="Agregation quotidienne Silver -> Gold + refresh mat view",
    schedule="0 3 * * *",
    start_date=datetime(2024, 1, 1),
    catchup=False,
    tags=["automind", "gold", "daily"],
) as dag:

    aggregate_gold = BashOperator(
        task_id="aggregate_gold",
        bash_command=(
            "spark-submit /opt/spark/batch_jobs/aggregate_gold_job.py "
            "--date {{ ds }}"
        ),
    )

    refresh_matview = BashOperator(
        task_id="refresh_materialized_view",
        bash_command=(
            "psql -U automind_user -d automind -h postgres "
            "-c 'REFRESH MATERIALIZED VIEW CONCURRENTLY mv_user_item_matrix;'"
        ),
    )

    quality_check = BashOperator(
        task_id="data_quality_check",
        bash_command="python /opt/airflow/dags/data_quality_check_dag.py",
    )

    aggregate_gold >> refresh_matview >> quality_check
