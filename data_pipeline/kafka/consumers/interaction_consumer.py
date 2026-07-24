import json
import signal
from datetime import datetime, timezone
from pathlib import Path

import pyarrow as pa
import pyarrow.parquet as pq
from confluent_kafka import Consumer, KafkaError

from data_pipeline.kafka.topics_config import BOOTSTRAP_SERVERS

BRONZE_BASE = Path(__file__).parent.parent.parent / "storage" / "bronze" / "interactions"
RUNNING = True

SCHEMA = pa.schema([
    ("interaction_id", pa.string()),
    ("user_id", pa.string()),
    ("vehicle_id", pa.string()),
    ("action", pa.string()),
    ("source", pa.string()),
    ("session_id", pa.string()),
    ("search_query", pa.string()),
    ("recommendation_method", pa.string()),
    ("duration_seconds", pa.int32()),
    ("device_type", pa.string()),
    ("user_agent", pa.string()),
    ("timestamp", pa.string()),
])


def get_dt(timestamp_str: str) -> str:
    return datetime.fromisoformat(timestamp_str).strftime("%Y-%m-%d")


def parse(msg_value: bytes) -> dict | None:
    try:
        ev = json.loads(msg_value.decode("utf-8"))
        return {f.name: ev.get(f.name) for f in SCHEMA}
    except Exception as e:
        print(f"  Parse error: {e}")
        return None


def flush_buffer(rows: list[dict], dt: str):
    path = BRONZE_BASE / f"dt={dt}"
    path.mkdir(parents=True, exist_ok=True)
    table = pa.Table.from_pylist(rows, schema=SCHEMA)
    fname = path / f"interactions_{datetime.now(timezone.utc).strftime('%H%M%S')}.parquet"
    pq.write_table(table, fname, compression="snappy")
    print(f"  Bronze ecrit: {fname} ({len(rows)} lignes)")


def signal_handler(*_):
    global RUNNING
    RUNNING = False


def run_consumer():
    global RUNNING
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    consumer = Consumer({
        "bootstrap.servers": BOOTSTRAP_SERVERS,
        "group.id": "wakala-bronze-interactions",
        "auto.offset.reset": "earliest",
        "enable.auto.commit": True,
    })
    consumer.subscribe(["interactions.raw"])
    print("Consumer interactions demarre. En attente de messages...")

    buf, cur_dt = [], None
    try:
        while RUNNING:
            msg = consumer.poll(1.0)
            if msg is None:
                continue
            if msg.error():
                if msg.error().code() != KafkaError._PARTITION_EOF:
                    print(f"  Erreur Kafka: {msg.error()}")
                continue
            row = parse(msg.value())
            if row is None:
                continue
            dt = get_dt(row["timestamp"])
            if cur_dt is None:
                cur_dt = dt
            if dt != cur_dt or len(buf) >= 100:
                if buf:
                    flush_buffer(buf, cur_dt)
                buf, cur_dt = [], dt
            buf.append(row)
    finally:
        if buf:
            flush_buffer(buf, cur_dt or "unknown")
        consumer.close()
        print("Consumer interactions arrete.")


if __name__ == "__main__":
    run_consumer()
