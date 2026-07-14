import re
import hashlib
from datetime import datetime, timezone
from typing import Dict, Any, Optional

from . import config


class ScraperNormalizer:
    """
    Normalizes raw scraped data from various sources into the common project schema.
    Compatible with the Silver layer expectations (clean_listings_job.py).
    Output format matches what listing_consumer.py expects.
    """

    VALID_CITIES = {
        "casablanca", "rabat", "marrakech", "fes", "tangier", "tanger",
        "agadir", "meknes", "oujda", "kenitra", "tetouan", "sale", "salé"
    }

    @staticmethod
    def _parse_price(raw_price: Any) -> Optional[int]:
        if not raw_price:
            return None
        digits = re.sub(r'[^\d]', '', str(raw_price))
        return int(digits) if digits else None

    @staticmethod
    def _parse_int(raw_val: Any) -> Optional[int]:
        if not raw_val:
            return None
        try:
            digits = re.sub(r'[^\d]', '', str(raw_val))
            return int(digits) if digits else None
        except Exception:
            return None

    @staticmethod
    def _normalize_city(city: str) -> str:
        if not city:
            return "unknown"
        city_lower = city.strip().lower()
        city_lower = city_lower.replace("é", "e").replace("è", "e").replace("ë", "e").replace("ê", "e")
        city_lower = city_lower.replace("à", "a").replace("â", "a").replace("ô", "o").replace("î", "i")

        if city_lower == "tanger":
            return "tangier"

        for valid_city in ScraperNormalizer.VALID_CITIES:
            if valid_city in city_lower:
                return valid_city

        return city_lower

    @staticmethod
    def _normalize_string(val: Any) -> Optional[str]:
        if not val:
            return None
        return str(val).strip().lower()

    @staticmethod
    def normalize(raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Takes raw data and returns a normalized dictionary matching the listing_consumer.py schema.
        """
        source_url = raw_data.get("source_url", "")

        # Generate deterministic vehicle_id from URL if not provided
        vehicle_id = raw_data.get("vehicle_id")
        if not vehicle_id and source_url:
            vehicle_id = hashlib.md5(source_url.encode('utf-8')).hexdigest()
        elif not vehicle_id:
            vehicle_id = hashlib.md5(str(datetime.now(timezone.utc)).encode('utf-8')).hexdigest()

        scraped_at = raw_data.get("scraped_at", datetime.now(timezone.utc).isoformat())

        return {
            "vehicle_id": vehicle_id,
            "brand": ScraperNormalizer._normalize_string(raw_data.get("brand")) or "unknown",
            "model": ScraperNormalizer._normalize_string(raw_data.get("model")),
            "year": ScraperNormalizer._parse_int(raw_data.get("year")),
            "mileage": ScraperNormalizer._parse_int(raw_data.get("mileage")),
            "price": ScraperNormalizer._parse_price(raw_data.get("price", "")),
            "city": ScraperNormalizer._normalize_city(raw_data.get("city", "")),
            "fuel_type": ScraperNormalizer._normalize_string(raw_data.get("fuel_type")),
            "body_type": ScraperNormalizer._normalize_string(raw_data.get("body_type")),
            "transmission": ScraperNormalizer._normalize_string(raw_data.get("transmission")),
            "images_urls": raw_data.get("images_urls", []),
            "source_url": source_url,
            "source": raw_data.get("source", "unknown"),
            "scraped_at": scraped_at,
            "timestamp": scraped_at,
        }