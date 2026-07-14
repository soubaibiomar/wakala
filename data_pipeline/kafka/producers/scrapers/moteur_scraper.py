from datetime import datetime
from typing import List, Dict, Any, Optional
import json
import logging
import re

from bs4 import BeautifulSoup

from .base_scraper import BaseScraper
from . import config
from .selector_loader import SelectorLoader
from .extraction_fallback import FallbackExtractor

logger = logging.getLogger(__name__)


class MoteurScraper(BaseScraper):
    def __init__(self):
        super().__init__(
            base_url="https://www.moteur.ma/fr/voiture/achat-voiture-occasion/",
            source_name="moteur"
        )
        self.selector_loader = SelectorLoader()

    def fetch_listings(self, max_items: int = config.MAX_LISTINGS_PER_RUN) -> List[Dict[str, Any]]:
        logger.info(f"Starting to fetch listings from {self.source_name} (max {max_items})")

        all_listings = []
        pages = self.build_pagination_urls(config.PAGES_PER_SOURCE)

        for page_url in pages:
            if len(all_listings) >= max_items:
                break

            html = self.fetch_page(page_url)
            if not html:
                logger.warning(f"Failed to fetch or prohibited by robots.txt: {page_url}")
                continue

            page_listings = self._parse_listings_page(html, max_items - len(all_listings))
            all_listings.extend(page_listings)

        logger.info(f"Fetched {len(all_listings)} listings from {self.source_name}")
        return all_listings[:max_items]

    def build_pagination_urls(self, max_pages: int) -> List[str]:
        """Moteur.ma uses ?page={page} for pagination"""
        urls = [self.base_url]
        for page in range(2, max_pages + 1):
            urls.append(f"{self.base_url}?page={page}")
        return urls

    def _parse_listings_page(self, html: str, max_items: int) -> List[Dict[str, Any]]:
        soup = BeautifulSoup(html, 'html.parser')
        listings = []

        selectors = self.selector_loader.load(self.source_name)
        card_sel = selectors.get("listing_card", ".ads-index-card")
        fallbacks = selectors.get("fallback_fields", {}).get("listing_card", [])
        
        listing_elements = soup.select(card_sel)
        if not listing_elements:
            for fallback in fallbacks:
                listing_elements = soup.select(fallback)
                if listing_elements:
                    break

        for elem in listing_elements[:max_items]:
            try:
                listing = self._parse_listing_element(elem)
                if listing:
                    listings.append(listing)
            except Exception as e:
                logger.error(f"Error parsing Moteur listing element: {e}")

        return listings

    def _parse_listing_element(self, elem) -> Optional[Dict[str, Any]]:
        """Parse a single listing card element"""
        try:
            selectors = self.selector_loader.load(self.source_name)
            fields = selectors.get("fields", {})
            fallbacks = selectors.get("fallback_fields", {})
            
            # URL
            source_url = FallbackExtractor.extract_attr(
                elem, fields.get("url"), "href", fallbacks.get("url")
            )
            if source_url and not source_url.startswith('http'):
                source_url = f"https://www.moteur.ma{source_url}"

            # Price
            price = FallbackExtractor.extract_text(
                elem, fields.get("price"), fallbacks.get("price"), heuristic="price"
            )

            # Title (brand + model)
            title = FallbackExtractor.extract_text(
                elem, fields.get("title"), fallbacks.get("title")
            )
            brand, model = self._extract_brand_model(title or '')

            # Location/City
            city = FallbackExtractor.extract_text(
                elem, fields.get("city"), fallbacks.get("city")
            )

            # Specs
            year, mileage, fuel_type, transmission, body_type = None, None, None, None, None
            specs_text = FallbackExtractor.extract_text(
                elem, fields.get("specs"), fallbacks.get("specs")
            )
            if specs_text:
                year, mileage, fuel_type, transmission, body_type = self._parse_specs(specs_text)

            # Fallback for year if not in specs
            if not year:
                year_text = FallbackExtractor.extract_text(
                    elem, fields.get("year"), fallbacks.get("year"), heuristic="year"
                )
                if year_text:
                    year = self._parse_int(year_text)

            raw_data = {
                "source": self.source_name,
                "source_url": source_url,
                "price": price,
                "brand": brand,
                "model": model,
                "city": city,
                "year": year,
                "mileage": mileage,
                "fuel_type": fuel_type,
                "body_type": body_type,
                "transmission": transmission,
                "scraped_at": datetime.utcnow().isoformat(),
                "images_urls": []
            }
            return raw_data
        except Exception as e:
            logger.error(f"Error parsing listing element: {e}")
            return None

    def _parse_specs(self, specs_text: str) -> tuple:
        """Parse specs text to extract year, mileage, fuel, transmission, body"""
        year = None
        mileage = None
        fuel_type = None
        transmission = None
        body_type = None

        specs_lower = specs_text.lower()

        # Year - typically 4 digits 1990-2026
        year_match = re.search(r'\b(19|20)\d{2}\b', specs_text)
        if year_match:
            year = int(year_match.group())

        # Mileage - look for km/KM patterns
        km_match = re.search(r'(\d[\d\s\.]*)\s*(km|KM|Km)', specs_text)
        if km_match:
            mileage = self._parse_int(km_match.group(1))

        # Fuel type
        fuel_keywords = {
            'diesel': ['diesel', 'dci', 'hdi', 'tdi', 'crdi'],
            'essence': ['essence', 'tce', 'vti', 'tfsi', 'gdi'],
            'hybride': ['hybride', 'hybrid'],
            'électrique': ['électrique', 'electrique', 'ev', 'electric'],
            'gpl': ['gpl', 'gaz']
        }
        for fuel, keywords in fuel_keywords.items():
            if any(kw in specs_lower for kw in keywords):
                fuel_type = fuel
                break

        # Transmission
        if any(kw in specs_lower for kw in ['automatique', 'automatic', 'at', 'cvt', 'dsg', 'boîte auto']):
            transmission = 'automatique'
        elif any(kw in specs_lower for kw in ['manuelle', 'manual', 'mt', 'boîte man', 'boite man']):
            transmission = 'manuelle'

        # Body type
        body_keywords = {
            'berline': ['berline', 'sedan'],
            'suv': ['suv', '4x4', 'crossover'],
            'citadine': ['citadine', 'city car'],
            'break': ['break', 'sw', 'estate', 'touring'],
            'coupé': ['coupé', 'coupe'],
            'cabriolet': ['cabriolet', 'convertible'],
            'monospace': ['monospace', 'mpv', 'ludospace'],
            'utilitaire': ['utilitaire', 'fourgon', 'camionnette']
        }
        for body, keywords in body_keywords.items():
            if any(kw in specs_lower for kw in keywords):
                body_type = body
                break

        return year, mileage, fuel_type, transmission, body_type

    def _extract_brand_model(self, title: str) -> tuple:
        """Extract brand and model from title string"""
        if not title:
            return None, None

        brands = [
            'Dacia', 'Renault', 'Peugeot', 'Citroën', 'Citroen',
            'Hyundai', 'Kia', 'Toyota', 'Volkswagen', 'VW',
            'BMW', 'Mercedes', 'Audi', 'Ford', 'Fiat',
            'Nissan', 'Mitsubishi', 'Suzuki', 'Honda', 'Mazda',
            'Opel', 'Chevrolet', 'Jeep', 'Land Rover', 'Range Rover',
            'Volvo', 'Seat', 'Skoda', 'Mini', 'Smart',
            'Iveco', 'MAN', 'Scania', 'Mercedes-Benz', 'Alfa Romeo'
        ]

        title_lower = title.lower()
        for brand in brands:
            if title_lower.startswith(brand.lower() + ' ') or title_lower == brand.lower():
                model = title[len(brand):].strip()
                return brand, model if model else None

        parts = title.split()
        if parts:
            return parts[0], ' '.join(parts[1:]) if len(parts) > 1 else None
        return None, None

    def _parse_int(self, val: Any) -> Optional[int]:
        if not val:
            return None
        try:
            digits = re.sub(r'[^\d]', '', str(val))
            return int(digits) if digits else None
        except Exception:
            return None