import json
import signal
from datetime import datetime, timezone
from pathlib import Path

import pyarrow as pa
import pyarrow.parquet as pq
from confluent_kafka import Consumer, KafkaError

from data_pipeline.kafka.topics_config import BOOTSTRAP_SERVERS

BRONZE_BASE = Path(__file__).parent.parent.parent / "storage" / "bronze" / "listings"
RUNNING = True

SCHEMA = pa.schema([
    ("vehicle_id", pa.string()),
    ("source", pa.string()),
    ("event_type", pa.string()),
    ("timestamp", pa.string()),
    ("brand", pa.string()),
    ("model", pa.string()),
    ("year", pa.int32()),
    ("price", pa.int32()),
    ("mileage", pa.int32()),
    ("fuel_type", pa.string()),
    ("body_type", pa.string()),
    ("transmission", pa.string()),
    ("engine_power_hp", pa.int32()),
    ("color", pa.string()),
    ("doors", pa.int32()),
    ("seats", pa.int32()),
    ("city", pa.string()),
    ("description", pa.string()),
    ("seller_id", pa.string()),
])


def get_dt(timestamp_str: str) -> str:
    return datetime.fromisoformat(timestamp_str).strftime("%Y-%m-%d")


def parse(msg_value: bytes) -> dict | None:
    try:
        ev = json.loads(msg_value.decode("utf-8"))
        d = ev.get("data", {})
        return {
            "vehicle_id": ev.get("vehicle_id", ""),
            "source": ev.get("source", ""),
            "event_type": ev.get("event_type", ""),
            "timestamp": ev.get("timestamp", ""),
            "brand": d.get("brand", ""),
            "model": d.get("model", ""),
            "year": d.get("year", 0),
            "price": d.get("price", 0),
            "mileage": d.get("mileage", 0),
            "fuel_type": d.get("fuel_type", ""),
            "body_type": d.get("body_type", ""),
            "transmission": d.get("transmission", ""),
            "engine_power_hp": d.get("engine_power_hp", 0),
            "color": d.get("color", ""),
            "doors": d.get("doors", 0),
            "seats": d.get("seats", 0),
            "city": d.get("city", ""),
            "description": d.get("description", ""),
            "seller_id": d.get("seller_id", ""),
        }
    except (json.JSONDecodeError, KeyError) as e:
        print(f"  Parse error: {e}")
        return None


def flush_buffer(rows: list[dict], dt: str):
    path = BRONZE_BASE / f"dt={dt}"
    path.mkdir(parents=True, exist_ok=True)
    table = pa.Table.from_pylist(rows, schema=SCHEMA)
    fname = path / f"listings_{datetime.now(timezone.utc).strftime('%H%M%S')}.parquet"
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
        "group.id": "wakala-bronze-listings",
        "auto.offset.reset": "earliest",
        "enable.auto.commit": True,
    })
    consumer.subscribe(["listings.raw"])
    print("Consumer listings demarre. En attente de messages...")

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
            if dt != cur_dt or len(buf) >= 50:
                if buf:
                    flush_buffer(buf, cur_dt)
                buf, cur_dt = [], dt
            buf.append(row)
            print(f"  Recu listing: {row['brand']} {row['model']} ({row['year']})")
    finally:
        if buf:
            flush_buffer(buf, cur_dt or "unknown")
        consumer.close()
        print("Consumer listings arrete.")


if __name__ == "__main__":
    run_consumer()
