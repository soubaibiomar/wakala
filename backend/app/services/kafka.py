"""
services/kafka.py — Re-export core Kafka services for convenience.
"""

from app.core.kafka import (
    get_kafka_config,
    get_kafka_producer,
    get_kafka_consumer,
)

__all__ = [
    "get_kafka_config",
    "get_kafka_producer",
    "get_kafka_consumer",
]
