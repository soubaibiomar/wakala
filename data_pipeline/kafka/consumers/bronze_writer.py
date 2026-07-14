"""
Kafka Consumer — Consomme les événements véhicules et les écrit en Bronze layer.
"""

import json
from confluent_kafka import Consumer, KafkaError
from pathlib import Path
from datetime import datetime

KAFKA_CONFIG = {
    "bootstrap.servers": "localhost:9092",
    "group.id": "automind-bronze-writer",
    "auto.offset.reset": "earliest",
}

BRONZE_PATH = Path(__file__).parent.parent.parent / "storage" / "bronze"


def write_to_bronze(event: dict):
    """Écrit l'événement brut en Bronze layer (JSON)."""
    BRONZE_PATH.mkdir(parents=True, exist_ok=True)
    date_str = datetime.utcnow().strftime("%Y-%m-%d")
    filepath = BRONZE_PATH / f"vehicles_{date_str}.jsonl"
    with open(filepath, "a") as f:
        f.write(json.dumps(event) + "\n")


def run_consumer():
    """Lance le consumer Kafka pour le topic vehicle-events."""
    consumer = Consumer(KAFKA_CONFIG)
    consumer.subscribe(["vehicle-events"])

    print("📡 Consumer démarré — en attente de messages...")
    try:
        while True:
            msg = consumer.poll(1.0)
            if msg is None:
                continue
            if msg.error():
                if msg.error().code() != KafkaError._PARTITION_EOF:
                    print(f"❌ Erreur : {msg.error()}")
                continue

            event = json.loads(msg.value().decode("utf-8"))
            write_to_bronze(event)
            print(f"📥 Bronze écrit : {event['data']['brand']} {event['data']['model']}")
    except KeyboardInterrupt:
        pass
    finally:
        consumer.close()
        print("🛑 Consumer arrêté.")


if __name__ == "__main__":
    run_consumer()
