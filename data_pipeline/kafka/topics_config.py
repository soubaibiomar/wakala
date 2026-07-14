from confluent_kafka.admin import AdminClient, NewTopic


BOOTSTRAP_SERVERS = "localhost:9092"

TOPICS = {
    "listings.raw": {
        "num_partitions": 3,
        "replication_factor": 1,
        "config": {"cleanup.policy": "delete", "retention.ms": "604800000"},
    },
    "interactions.raw": {
        "num_partitions": 3,
        "replication_factor": 1,
        "config": {"cleanup.policy": "delete", "retention.ms": "604800000"},
    },
}


def ensure_topics(bootstrap_servers: str = BOOTSTRAP_SERVERS) -> None:
    admin = AdminClient({"bootstrap.servers": bootstrap_servers})
    existing = admin.list_topics().topics

    new_topics = []
    for name, cfg in TOPICS.items():
        if name not in existing:
            new_topics.append(
                NewTopic(
                    name=name,
                    num_partitions=cfg["num_partitions"],
                    replication_factor=cfg["replication_factor"],
                    config=cfg["config"],
                )
            )

    if new_topics:
        futures = admin.create_topics(new_topics)
        for name, future in futures.items():
            try:
                future.result()
                print(f"  Topic '{name}' cree (3 partitions)")
            except Exception as e:
                if "already exists" in str(e).lower():
                    print(f"  Topic '{name}' existe deja")
                else:
                    print(f"  Erreur creation topic '{name}': {e}")
    else:
        print("  Tous les topics existent deja")


if __name__ == "__main__":
    ensure_topics()
