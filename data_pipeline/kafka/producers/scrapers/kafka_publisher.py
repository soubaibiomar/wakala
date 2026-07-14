import json
import logging
from typing import List, Dict, Any

from confluent_kafka import Producer

from . import config
from .normalizer import ScraperNormalizer

logger = logging.getLogger(__name__)


class KafkaPublisher:
    """
    Publishes normalized listing data to Kafka topic 'listings.raw'.
    Reuses the topic configuration from topics_config.py.
    Message format matches what listing_consumer.py expects.
    """

    def __init__(self, bootstrap_servers: str = None):
        self.bootstrap_servers = bootstrap_servers or config.BOOTSTRAP_SERVERS
        self.topic = config.TOPIC_RAW
        self.producer = Producer({"bootstrap.servers": self.bootstrap_servers})
        self.normalizer = ScraperNormalizer()

    def delivery_report(self, err, msg):
        if err:
            logger.error(f"Delivery failed: {err}")
        else:
            logger.debug(f"Published to {msg.topic()}[{msg.partition()}] @ offset {msg.offset()}")

    def publish_listings(self, raw_listings: List[Dict[str, Any]]) -> int:
        """
        Normalizes and publishes a batch of raw listings to Kafka.
        Returns the number of successfully published messages.
        """
        if not raw_listings:
            logger.info("No listings to publish")
            return 0

        published = 0
        for raw in raw_listings:
            try:
                normalized = self.normalizer.normalize(raw)
                
                # Wrap the normalized data in the expected event format
                event = {
                    "vehicle_id": normalized.get("vehicle_id"),
                    "source": normalized.get("source", "unknown"),
                    "event_type": "listing_created",
                    "timestamp": normalized.get("timestamp", normalized.get("scraped_at")),
                    "data": normalized
                }
                
                key = event["vehicle_id"].encode('utf-8')
                value = json.dumps(event, default=str).encode('utf-8')

                self.producer.produce(
                    self.topic,
                    key=key,
                    value=value,
                    callback=self.delivery_report
                )
                self.producer.poll(0)
                published += 1

            except Exception as e:
                logger.error(f"Error publishing listing: {e}")

        # Flush to ensure all messages are sent
        self.producer.flush(timeout=10)
        logger.info(f"Published {published}/{len(raw_listings)} listings to {self.topic}")
        return published

    def close(self):
        self.producer.flush(timeout=10)