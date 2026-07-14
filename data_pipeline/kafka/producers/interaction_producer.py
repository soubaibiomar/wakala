import argparse
import json
import random
import time
import uuid
from datetime import datetime, timezone

from confluent_kafka import Producer

from data_pipeline.kafka.topics_config import BOOTSTRAP_SERVERS, ensure_topics

ACTIONS = ["view", "click", "favorite", "unfavorite", "contact",
           "share", "search", "recommendation_click"]
ACTION_WEIGHTS = [0.50, 0.15, 0.10, 0.03, 0.05, 0.05, 0.07, 0.05]

SOURCES = ["search", "catalogue", "recommendation", "chatbot", "direct"]
SOURCE_WEIGHTS = [0.30, 0.35, 0.15, 0.10, 0.10]

DEVICE_TYPES = ["desktop", "mobile", "tablet"]
DEVICE_WEIGHTS = [0.40, 0.50, 0.10]

USER_IDS = [str(uuid.uuid4()) for _ in range(200)]
VEHICLE_IDS = [str(uuid.uuid4()) for _ in range(500)]

SEARCH_QUERIES = [
    "SUV diesel pas cher Maroc", "voiture occasion Casablanca",
    "Peugeot 3008", "citadine essence automatique",
    "4x4 Maroc", "familiale 7 places", "berline luxe",
    "voiture hybride occasion", "Clio 4", "Dacia Sandero",
]


def generate_interaction_event() -> dict:
    uid = random.choice(USER_IDS)
    vid = random.choice(VEHICLE_IDS)
    action = random.choices(ACTIONS, weights=ACTION_WEIGHTS, k=1)[0]
    source = random.choices(SOURCES, weights=SOURCE_WEIGHTS, k=1)[0]
    device = random.choices(DEVICE_TYPES, weights=DEVICE_WEIGHTS, k=1)[0]

    event = {
        "interaction_id": str(uuid.uuid4()),
        "user_id": uid,
        "vehicle_id": vid,
        "action": action,
        "source": source,
        "session_id": f"session_{random.randint(1, 5000)}",
        "device_type": device,
        "user_agent": (f"Mozilla/5.0 ({'Windows NT 10.0' if device == 'desktop' "
                       f"else 'Linux; Android 14'})"),
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
    if source == "search":
        event["search_query"] = random.choice(SEARCH_QUERIES)
    if source == "recommendation":
        event["recommendation_method"] = random.choice(
            ["content-based", "collaborative", "hybrid"])
    if action == "view":
        event["duration_seconds"] = random.randint(5, 300)
    return event


def delivery_report(err, msg):
    if err:
        print(f"  Erreur envoi: {err}")
    else:
        print(f"  Interaction envoyee: {msg.key().decode()} [{msg.partition()}]")


def run_producer(num_events: int = 0, fast: bool = False, duration_minutes: int = 5):
    ensure_topics()
    producer = Producer({"bootstrap.servers": BOOTSTRAP_SERVERS})
    topic = "interactions.raw"

    min_delay, max_delay = (0.03, 0.12) if fast else (1, 3)
    max_events = num_events if num_events > 0 else 999999
    start = time.time()
    deadline = start + duration_minutes * 60
    count = 0

    print(f"Producteur interactions sur '{topic}' {'(mode rapide)' if fast else ''}")
    while count < max_events and time.time() < deadline:
        event = generate_interaction_event()
        producer.produce(topic, key=event["vehicle_id"],
                         value=json.dumps(event), callback=delivery_report)
        producer.poll(0)
        count += 1
        time.sleep(random.uniform(min_delay, max_delay))

    producer.flush()
    elapsed = time.time() - start
    print(f"Termine: {count} interactions en {elapsed:.1f}s ({count/elapsed:.1f} evt/s)")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Producteur d'interactions utilisateur")
    parser.add_argument("--fast", action="store_true", help="Mode rapide (demo)")
    parser.add_argument("--num", type=int, default=0, help="Nombre d'evenements (0 = illimite)")
    parser.add_argument("--duration", type=int, default=5, help="Duree max en minutes")
    args = parser.parse_args()
    run_producer(args.num, args.fast, args.duration)
