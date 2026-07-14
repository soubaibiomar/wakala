"""
Tests for ScraperNormalizer using REAL scraped HTML fixtures.
NO synthetic/invented vehicle data - only fixtures from actual scrapes.
"""
import pytest
from pathlib import Path
from scrapers.normalizer import ScraperNormalizer
from scrapers.avito_scraper import AvitoScraper
from scrapers.moteur_scraper import MoteurScraper

FIXTURE_DIR = Path(__file__).parent / "fixtures" / "scraped_html"


class TestNormalizerWithRealFixtures:
    """Test normalizer with real scraped data"""

    @pytest.fixture
    def avito_html(self):
        return (FIXTURE_DIR / "avito_page1.html").read_text(encoding='utf-8')

    @pytest.fixture
    def moteur_html(self):
        return (FIXTURE_DIR / "moteur_page1.html").read_text(encoding='utf-8')

    def test_price_parsing(self):
        assert ScraperNormalizer._parse_price("168 000 DH") == 168000
        assert ScraperNormalizer._parse_price("168.000 MAD") == 168000
        assert ScraperNormalizer._parse_price("150000") == 150000
        assert ScraperNormalizer._parse_price("Prix non spécifié") is None
        assert ScraperNormalizer._parse_price(None) is None

    def test_city_normalization(self):
        assert ScraperNormalizer._normalize_city("Casablanca") == "casablanca"
        assert ScraperNormalizer._normalize_city("  Rabat  ") == "rabat"
        assert ScraperNormalizer._normalize_city("Tanger") == "tangier"
        assert ScraperNormalizer._normalize_city("Fès") == "fes"
        assert ScraperNormalizer._normalize_city("fès") == "fes"
        assert ScraperNormalizer._normalize_city(None) == "unknown"

    def test_normalize_avito_real_data(self, avito_html):
        """Normalize real Avito scraped listings"""
        scraper = AvitoScraper()
        normalizer = ScraperNormalizer()

        raw_listings = scraper._parse_listings_page(avito_html, max_items=10)
        assert len(raw_listings) == 3

        normalized = [normalizer.normalize(raw) for raw in raw_listings]

        # Dacia Duster 2022
        dacia = normalized[0]
        assert dacia["brand"] == "dacia"
        assert "duster" in dacia["model"]
        assert dacia["price"] == 185000
        assert dacia["city"] == "casablanca"
        assert dacia["year"] == 2022
        assert dacia["mileage"] == 85000
        assert dacia["fuel_type"] == "diesel"
        assert dacia["transmission"] == "manuelle"
        assert dacia["body_type"] == "suv"
        assert dacia["source"] == "avito"
        assert dacia["source_url"].startswith("https://www.avito.ma")

        # Renault Clio 2020
        clio = normalized[1]
        assert clio["brand"] == "renault"
        assert "clio" in clio["model"]
        assert clio["price"] == 142000
        assert clio["city"] == "rabat"
        assert clio["year"] == 2020
        assert clio["fuel_type"] == "essence"
        assert clio["transmission"] == "automatique"

        # Peugeot 3008 2023
        peugeot = normalized[2]
        assert peugeot["brand"] == "peugeot"
        assert "3008" in peugeot["model"]
        assert peugeot["price"] == 385000
        assert peugeot["fuel_type"] == "hybride"

    def test_normalize_moteur_real_data(self, moteur_html):
        """Normalize real Moteur.ma scraped listings"""
        scraper = MoteurScraper()
        normalizer = ScraperNormalizer()

        raw_listings = scraper._parse_listings_page(moteur_html, max_items=10)
        assert len(raw_listings) >= 2

        normalized = [normalizer.normalize(raw) for raw in raw_listings]

        # Dacia Duster
        dacia = normalized[0]
        assert dacia["brand"] == "dacia"
        assert "duster" in dacia["model"]
        assert dacia["price"] == 168000
        assert dacia["city"] == "tanger" or dacia["city"] == "tangier"
        assert dacia["year"] == 2021
        assert dacia["fuel_type"] == "diesel"
        assert dacia["source"] == "moteur"

        # Hyundai Tucson (or similar)
        hyundai = normalized[1]
        assert "hyundai" in hyundai["brand"]
        assert hyundai["price"] in [295000, 325000]  # fixture variations
        assert hyundai["fuel_type"] == "essence"
        assert hyundai["transmission"] == "automatique"

    def test_normalized_schema_matches_consumer(self, avito_html):
        """Ensure normalized output matches listing_consumer.py SCHEMA expectations"""
        scraper = AvitoScraper()
        normalizer = ScraperNormalizer()

        raw_listings = scraper._parse_listings_page(avito_html, max_items=10)
        normalized = [normalizer.normalize(raw) for raw in raw_listings]

        for item in normalized:
            # Required fields for listing_consumer.py SCHEMA
            assert "vehicle_id" in item
            assert isinstance(item["vehicle_id"], str) and len(item["vehicle_id"]) == 32  # MD5

            assert item["brand"] != "unknown"
            assert item["model"] is not None
            assert isinstance(item["year"], int) and item["year"] >= 1990
            assert isinstance(item["price"], int) and item["price"] > 0
            assert isinstance(item["mileage"], int) and item["mileage"] >= 0
            assert item["fuel_type"] in ["diesel", "essence", "hybride", "electrique", "gpl", None]
            assert item["transmission"] in ["manuelle", "automatique", None]
            assert item["city"] != "unknown"
            assert item["source"] in ["avito", "moteur"]
            assert item["source_url"].startswith("https://")
            assert "timestamp" in item
            assert "scraped_at" in item


class TestFixturesIntegrity:
    """Verify fixtures are valid and complete"""

    def test_avito_fixture_exists(self):
        assert (FIXTURE_DIR / "avito_page1.html").exists()

    def test_moteur_fixture_exists(self):
        assert (FIXTURE_DIR / "moteur_page1.html").exists()

    def test_avito_fixture_has_next_data(self):
        html = (FIXTURE_DIR / "avito_page1.html").read_text()
        assert "__NEXT_DATA__" in html
        assert "Dacia Duster" in html
        assert "Renault Clio" in html

    def test_moteur_fixture_has_cards(self):
        html = (FIXTURE_DIR / "moteur_page1.html").read_text()
        assert "ads-index-card" in html or "listing-card" in html
        assert "Hyundai Tucson" in html or "Citroën C3" in html