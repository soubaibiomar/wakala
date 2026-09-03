"""
core/kafka.py — Configuration et clients Kafka (Aiven Cloud / Local).

Gère l'authentification Aiven (SASL_SSL / SCRAM-SHA-256) et assure
une initialisation tolérante aux pannes (ne plante pas si Kafka est absent).
"""

import logging
from typing import Optional, Dict, Any, List
from app.core.config import settings

logger = logging.getLogger(__name__)


def get_kafka_config(extra_config: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
    """
    Retourne la configuration Kafka normalisée pour Aiven ou local.
    Si KAFKA_BOOTSTRAP_SERVERS n'est pas défini, retourne None sans lever d'exception.
    """
    if not settings.KAFKA_BOOTSTRAP_SERVERS:
        logger.info("KAFKA_BOOTSTRAP_SERVERS non configuré; fonctionnalités Kafka désactivées.")
        return None

    config: Dict[str, Any] = {
        "bootstrap.servers": settings.KAFKA_BOOTSTRAP_SERVERS,
    }

    # Configuration Aiven Cloud SASL/SSL
    username = settings.kafka_username
    password = settings.kafka_password

    if username and password:
        config["security.protocol"] = settings.KAFKA_SECURITY_PROTOCOL or "SASL_SSL"
        config["sasl.mechanism"] = settings.KAFKA_SASL_MECHANISM or "SCRAM-SHA-256"
        config["sasl.username"] = username
        config["sasl.password"] = password

    if extra_config:
        config.update(extra_config)

    return config


def get_kafka_producer():
    """
    Initialise et retourne un Producer confluent_kafka ou KafkaProducer.
    Retourne None si les variables ne sont pas configurées ou si la connexion échoue.
    """
    config = get_kafka_config()
    if not config:
        return None

    # Tentative avec confluent_kafka
    try:
        from confluent_kafka import Producer
        producer = Producer(config)
        logger.info("Kafka Producer (confluent_kafka) initialisé avec succès.")
        return producer
    except ImportError:
        pass
    except Exception as e:
        logger.warning(f"Impossible d'initialiser le Producer confluent_kafka: {e}")

    # Tentative avec kafka-python standard
    try:
        from kafka import KafkaProducer
        kafka_args = {
            "bootstrap_servers": settings.KAFKA_BOOTSTRAP_SERVERS.split(","),
        }
        if settings.kafka_username and settings.kafka_password:
            kafka_args["security_protocol"] = settings.KAFKA_SECURITY_PROTOCOL or "SASL_SSL"
            kafka_args["sasl_mechanism"] = settings.KAFKA_SASL_MECHANISM or "SCRAM-SHA-256"
            kafka_args["sasl_plain_username"] = settings.kafka_username
            kafka_args["sasl_plain_password"] = settings.kafka_password

        producer = KafkaProducer(**kafka_args)
        logger.info("Kafka Producer (kafka-python) initialisé avec succès.")
        return producer
    except ImportError:
        pass
    except Exception as e:
        logger.warning(f"Impossible d'initialiser le Producer kafka-python: {e}")

    return None


def get_kafka_consumer(group_id: str = "wakala-consumer-group", topics: Optional[List[str]] = None):
    """
    Initialise et retourne un Consumer confluent_kafka ou KafkaConsumer.
    Retourne None si non configuré.
    """
    extra = {
        "group.id": group_id,
        "auto.offset.reset": "earliest",
    }
    config = get_kafka_config(extra)
    if not config:
        return None

    try:
        from confluent_kafka import Consumer
        consumer = Consumer(config)
        if topics:
            consumer.subscribe(topics)
        logger.info(f"Kafka Consumer connecté au groupe '{group_id}'.")
        return consumer
    except ImportError:
        pass
    except Exception as e:
        logger.warning(f"Impossible d'initialiser le Consumer confluent_kafka: {e}")

    try:
        from kafka import KafkaConsumer
        consumer_args = {
            "bootstrap_servers": settings.KAFKA_BOOTSTRAP_SERVERS.split(","),
            "group_id": group_id,
            "auto_offset_reset": "earliest",
        }
        if settings.kafka_username and settings.kafka_password:
            consumer_args["security_protocol"] = settings.KAFKA_SECURITY_PROTOCOL or "SASL_SSL"
            consumer_args["sasl_mechanism"] = settings.KAFKA_SASL_MECHANISM or "SCRAM-SHA-256"
            consumer_args["sasl_plain_username"] = settings.kafka_username
            consumer_args["sasl_plain_password"] = settings.kafka_password

        args = tuple(topics) if topics else ()
        consumer = KafkaConsumer(*args, **consumer_args)
        logger.info(f"Kafka Consumer (kafka-python) connecté au groupe '{group_id}'.")
        return consumer
    except ImportError:
        pass
    except Exception as e:
        logger.warning(f"Impossible d'initialiser le Consumer kafka-python: {e}")

    return None
