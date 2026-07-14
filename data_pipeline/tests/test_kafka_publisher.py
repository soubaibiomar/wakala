"""
Tests for KafkaPublisher using real fixture data with mocked Kafka.
No synthetic data - only real scraped fixtures.
"""
import json
import pytest
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path

from scrapers.normalizer import ScraperNormalizer
from scrapers.avito_scraper import AvitoScraper
from scrapers.moteur_scraper import MoteurScraper
from scrapers.kafka_publisher import KafkaPublisher

FIXTURE_DIR = Path(__file__).parent / "fixtures" / "scraped_html"


class TestKafkaPublisher:
    """Test Kafka publisher with real fixture data"""

    @pytest.fixture
    def avito_raw_listings(self):
        html = (FIXTURE_DIR / "avito_page1.html").read_text(encoding='utf-8')
        scraper = AvitoScraper()
        return scraper._parse_listings_page(html, max_items=10)

    @pytest.fixture
    def moteur_raw_listings(self):
        html = (FIXTURE_DIR / "moteur_page1.html").read_text(encoding='utf-8')
        scraper = MoteurScraper()
        return scraper._parse_listings_page(html, max_items=10)

    @patch('scrapers.kafka_publisher.Producer')
    def test_publish_avito_listings(self, mock_producer_class, avito_raw_listings):
        """Test publishing real Avito listings to Kafka"""
        mock_producer = Mock()
        mock_producer_class.return_value = mock_producer

        publisher = KafkaPublisher(bootstrap_servers="localhost:9092")
        count = publisher.publish_listings(avito_raw_listings)

        assert count == 3
        assert mock_producer.produce.call_count == 3
        mock_producer.flush.assert_called_once_with(timeout=10)

        # Verify message format matches listing_consumer.py expectations
        for call in mock_producer.produce.call_args_list:
            args, kwargs = call
            topic = args[0] if args else kwargs.get('topic')
            key = args[1] if len(args) > 1 else kwargs.get('key')
            value = args[2] if len(args) > 2 else kwargs.get('value')

            assert topic == "listings.raw"
            assert key is not None
            assert value is not None

            # Decode and validate message structure
            event = json.loads(value.decode('utf-8'))
            assert "vehicle_id" in event
            assert "source" in event
            assert event["source"] == "avito"
            assert "event_type" in event
            assert event["event_type"] == "listing_created"
            assert "timestamp" in event
            assert "data" in event

            data = event["data"]
            assert "brand" in data
            assert "model" in data
            assert "year" in data
            assert "price" in data
            assert "mileage" in data
            assert "fuel_type" in data
            assert "transmission" in data
            assert "city" in data

    @patch('scrapers.kafka_publisher.Producer')
    def test_publish_moteur_listings(self, mock_producer_class, moteur_raw_listings):
        """Test publishing real Moteur listings to Kafka"""
        mock_producer = Mock()
        mock_producer_class.return_value = mock_producer

        publisher = KafkaPublisher(bootstrap_servers="localhost:9092")
        count = publisher.publish_listings(moteur_raw_listings)

        assert count >= 2
        assert mock_producer.produce.call_count >= 2

        # Verify message format
        for call in mock_producer.produce.call_args_list:
            args, kwargs = call
            value = args[2] if len(args) > 2 else kwargs.get('value')
            event = json.loads(value.decode('utf-8'))

            assert event["source"] == "moteur"
            assert "data" in event
            assert event["data"]["brand"] is not None

    @patch('scrapers.kafka_publisher.Producer')
    def test_publish_empty_list(self, mock_producer_class):
        """Test publishing empty list returns 0"""
        mock_producer = Mock()
        mock_producer_class.return_value = mock_producer

        publisher = KafkaPublisher()
        count = publisher.publish_listings([])

        assert count == 0
        mock_producer.produce.assert_not_called()
        mock_producer.flush.assert_called_once_with(timeout=10)

    @patch('scrapers.kafka_publisher.Producer')
    def test_delivery_report_callback(self, mock_producer_class):
        """Test delivery report callback handles errors"""
        mock_producer = Mock()
        mock_producer_class.return_value = mock_producer

        publisher = KafkaPublisher()
        publisher.publish_listings([{"source": "avito", "source_url": "test"}])

        # Get the callback
        call_args = mock_producer.produce.call_args
        callback = call_args.kwargs.get('callback') or call_args[0][3]

        # Test success
        mock_msg = Mock()
        mock_msg.topic.return_value = "listings.raw"
        mock_msg.partition.return_value = 0
        mock_msg.offset.return_value = 42
        callback(None, mock_msg)

        # Test error
        mock_msg_err = Mock()
        mock_msg_err.topic.return_value = "listings.raw"
        callback(Exception("Kafka error"), mock_msg_err)


class TestNormalizerOutputFormat:
    """Ensure normalizer output matches Kafka consumer expectations"""

    def test_normalized_has_all_consumer_fields(self, avito_raw_listings):
        normalizer = ScraperNormalizer()
        normalized = [normalizer.normalize(raw) for raw in avito_raw_listings]

        for item in normalized:
            # Fields that listing_consumer.py SCHEMA expects
            required = [
                "vehicle_id", "brand", "model", "year", "price",
                "mileage", "fuel_type", "body_type", "transmission",
                "images_urls", "source_url", "source", "scraped_at", "timestamp"
            ]
            for field in required:
                assert field in item, f"Missing field: {field}"

            # Type checks
            assert isinstance(item["vehicle_id"], str)
            assert isinstance(item["brand"], str)
            assert item["brand"] != "unknown"
            assert item["model"] is None or isinstance(item["model"], str)
            assert item["year"] is None or isinstance(item["year"], int)
            assert item["price"] is None or isinstance(item["price"], int)
            assert item["mileage"] is None or isinstance(item["mileage"], int)
            assert item["source"] in ["avito", "moteur"]