"""
outreach_daily_check_dag.py — DAG Airflow quotidien pour le traitement
des séquences d'outreach.

Exécution : tous les jours à 09:00 UTC (10:00 heure Maroc)

Pipeline :
1. Query les séquences avec status='active' et next_scheduled_at <= NOW()
2. Pour chaque prospect : vérifie stop_conditions
3. Si pas de stop : génère le message (template + données réelles) et LOG (mode simulé)
4. Met à jour current_milestone et next_scheduled_at
"""

from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.python import PythonOperator


default_args = {
    "owner": "wakala",
    "depends_on_past": False,
    "email_on_failure": False,
    "email_on_retry": False,
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
}


dag = DAG(
    dag_id="outreach_daily_check",
    default_args=default_args,
    description="Traitement quotidien des séquences d'outreach 0-60 jours",
    schedule_interval="0 9 * * *",  # 09:00 UTC = 10:00 Maroc
    start_date=datetime(2024, 1, 1),
    catchup=False,
    tags=["outreach", "wakala", "engagement"],
)


def fetch_due_sequences(**context):
    """
    Récupère les séquences dues (status='active', next_scheduled_at <= NOW).
    Stocke les IDs dans XCom pour le traitement.
    """
    import asyncio
    from sqlalchemy import select
    from datetime import datetime, timezone

    async def _fetch():
        from app.core.database import async_session_factory
        from app.models.outreach import OutreachSequence

        async with async_session_factory() as db:
            now = datetime.now(timezone.utc)
            result = await db.execute(
                select(OutreachSequence).where(
                    OutreachSequence.status == "active",
                    OutreachSequence.next_scheduled_at <= now,
                )
            )
            sequences = list(result.scalars().all())

            return [
                {
                    "sequence_id": str(s.id),
                    "prospect_id": str(s.prospect_id),
                    "current_milestone": s.current_milestone,
                    "top3_vehicle_ids": s.top3_vehicle_ids,
                }
                for s in sequences
            ]

    due = asyncio.run(_fetch())
    context["task_instance"].xcom_push(key="due_sequences", value=due)

    print(f"[OUTREACH] Found {len(due)} due sequences")
    return len(due)


def process_due_sequences(**context):
    """
    Traite chaque séquence due :
    - Vérifie les stop conditions
    - Génère et "envoie" (simule) le message
    - Programme le jalon suivant
    """
    import asyncio

    due = context["task_instance"].xcom_pull(
        task_ids="fetch_due_sequences", key="due_sequences"
    )
    if not due:
        print("[OUTREACH] No due sequences to process")
        return 0

    async def _process():
        from app.core.database import async_session_factory
        from app.models.outreach import OutreachSequence
        from app.outreach.outreach_scheduler import process_milestone
        from sqlalchemy import select

        processed = 0
        async with async_session_factory() as db:
            for seq_info in due:
                try:
                    result = await db.execute(
                        select(OutreachSequence).where(
                            OutreachSequence.id == seq_info["sequence_id"]
                        )
                    )
                    sequence = result.scalar_one_or_none()
                    if not sequence:
                        continue

                    # Minimal vehicle data for templates
                    vehicles_data = [
                        {"vehicle_id": vid}
                        for vid in (seq_info.get("top3_vehicle_ids") or [])
                    ]

                    result = await process_milestone(
                        sequence=sequence,
                        vehicles_data=vehicles_data,
                        prospect_name="Cher(e) client(e)",  # Default
                        db=db,
                        simulate=True,  # MODE SIMULÉ
                    )

                    print(
                        f"[OUTREACH] Sequence {seq_info['sequence_id']}: "
                        f"{result.get('action')} milestone={result.get('milestone')}"
                    )
                    processed += 1

                except Exception as e:
                    print(
                        f"[OUTREACH] Error processing sequence "
                        f"{seq_info['sequence_id']}: {e}"
                    )

            await db.commit()

        return processed

    return asyncio.run(_process())


def report_results(**context):
    """Résume l'exécution quotidienne."""
    fetched = context["task_instance"].xcom_pull(task_ids="fetch_due_sequences")
    processed = context["task_instance"].xcom_pull(task_ids="process_due_sequences")

    print(f"[OUTREACH REPORT] Fetched: {fetched} | Processed: {processed}")


# ─── Tasks ───────────────────────────────────────────────────────

fetch_task = PythonOperator(
    task_id="fetch_due_sequences",
    python_callable=fetch_due_sequences,
    dag=dag,
)

process_task = PythonOperator(
    task_id="process_due_sequences",
    python_callable=process_due_sequences,
    dag=dag,
)

report_task = PythonOperator(
    task_id="report_results",
    python_callable=report_results,
    dag=dag,
)

fetch_task >> process_task >> report_task
