import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
import re

from bs4 import BeautifulSoup
import os

from ..base_scraper import BaseScraper
from .. import config
from ..extraction_fallback import FallbackExtractor
import yaml

logger = logging.getLogger(__name__)

class GenericDealerScraper(BaseScraper):
    """
    A generic scraper for dealerships that builds itself from a declarative YAML config.
    Instead of writing code per dealer, this class loads the dealer's specific CSS selectors
    and applies standard extraction logic.
    """
    def __init__(self, dealer_config: Dict[str, Any]):
        self.dealer_config = dealer_config
        self.dealer_name = dealer_config.get("name", "unknown_dealer")
        # Prefix the source name with 'dealer_' so it's clearly identifiable
        source_name = f"dealer_{self.dealer_name}"
        base_url = dealer_config.get("base_url")
        
        super().__init__(base_url=base_url, source_name=source_name)
        
        # Load the specific selectors for this dealer
        self.selectors = self._load_dealer_selectors(dealer_config.get("selectors_file"))

    def _load_dealer_selectors(self, selectors_filename: str) -> Dict[str, Any]:
        if not selectors_filename:
            logger.warning(f"No selectors file provided for dealer {self.dealer_name}")
            return {}
            
        # Selectors files are expected to be in the same registry directory
        current_dir = os.path.dirname(os.path.abspath(__file__))
        selectors_path = os.path.join(current_dir, "registry", selectors_filename)
        
        if not os.path.exists(selectors_path):
            logger.warning(f"Selectors file not found at {selectors_path}")
            return {}
            
        try:
            with open(selectors_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f) or {}
        except Exception as e:
            logger.error(f"Error loading selectors for {self.dealer_name}: {e}")
            return {}

    def fetch_listings(self, max_items: int = config.MAX_LISTINGS_PER_RUN) -> List[Dict[str, Any]]:
        logger.info(f"Starting to fetch listings from {self.source_name} (max {max_items})")

        all_listings = []
        pages_with_city = self.build_pagination_urls(config.PAGES_PER_SOURCE)

        for page_url, city in pages_with_city:
            if len(all_listings) >= max_items:
                break

            html = self.fetch_page(page_url)
            if not html:
                logger.warning(f"Failed to fetch or prohibited by robots.txt: {page_url}")
                continue

            page_listings = self._parse_listings_page(html, max_items - len(all_listings), city)
            all_listings.extend(page_listings)

        logger.info(f"Fetched {len(all_listings)} listings from {self.source_name}")
        return all_listings[:max_items]

    def build_pagination_urls(self, max_pages: int) -> List[tuple[str, str]]:
        """
        Returns a list of tuples (url, city).
        If 'locations' is present, it generates URLs for each city.
        """
        urls_with_city = []
        locations = self.dealer_config.get("locations", [])
        pagination_pattern = self.dealer_config.get("pagination_pattern", "?page={page}")
        
        if locations:
            # For each location, build the base url and pagination
            for city in locations:
                # E.g., append ?city=Casablanca or similar, depends on actual dealer pattern. 
                # For this demo, we assume the base_url takes a city param if locations are specified.
                separator = "&" if "?" in self.base_url else "?"
                city_url = f"{self.base_url}{separator}city={city}"
                urls_with_city.append((city_url, city))
                
                for page in range(2, max_pages + 1):
                    paginated_url = f"{city_url}&page={page}" if "?" in city_url else f"{city_url}?page={page}"
                    urls_with_city.append((paginated_url, city))
        else:
            default_city = self.dealer_config.get("city", "Inconnu")
            urls_with_city.append((self.base_url, default_city))
            for page in range(2, max_pages + 1):
                urls_with_city.append((self.base_url + pagination_pattern.format(page=page), default_city))
                
        return urls_with_city

    def _parse_listings_page(self, html: str, max_items: int, city: str) -> List[Dict[str, Any]]:
        soup = BeautifulSoup(html, 'html.parser')
        listings = []

        card_sel = self.selectors.get("listing_card", ".default-card")
        fallbacks = self.selectors.get("fallback_fields", {}).get("listing_card", [])
        
        listing_elements = soup.select(card_sel)
        if not listing_elements:
            for fallback in fallbacks:
                listing_elements = soup.select(fallback)
                if listing_elements:
                    break

        for elem in listing_elements[:max_items]:
            try:
                listing = self._parse_listing_element(elem, city)
                if listing:
                    listings.append(listing)
            except Exception as e:
                logger.error(f"Error parsing {self.source_name} listing element: {e}")

        return listings

    def _parse_listing_element(self, elem, city: str) -> Optional[Dict[str, Any]]:
        try:
            fields = self.selectors.get("fields", {})
            fallbacks = self.selectors.get("fallback_fields", {})
            
            source_url = FallbackExtractor.extract_attr(
                elem, fields.get("url"), "href", fallbacks.get("url")
            )
            if source_url and not source_url.startswith('http'):
                domain = self.base_url.split('/')[0] + '//' + self.base_url.split('/')[2]
                if not source_url.startswith('/'):
                    source_url = '/' + source_url
                source_url = f"{domain}{source_url}"

            price = FallbackExtractor.extract_text(
                elem, fields.get("price"), fallbacks.get("price"), heuristic="price"
            )

            title = FallbackExtractor.extract_text(
                elem, fields.get("title"), fallbacks.get("title")
            )
            
            # Use dealer's brand if monobrand, else parse from title
            default_brand = self.dealer_config.get("brand")
            brand, model = self._extract_brand_model(title or '', default_brand)

            # Specs
            year = self._parse_int(FallbackExtractor.extract_text(elem, fields.get("year"), fallbacks.get("year"), heuristic="year"))
            mileage = self._parse_int(FallbackExtractor.extract_text(elem, fields.get("mileage"), fallbacks.get("mileage")))
            fuel_type = FallbackExtractor.extract_text(elem, fields.get("fuel_type"), fallbacks.get("fuel_type"))
            transmission = FallbackExtractor.extract_text(elem, fields.get("transmission"), fallbacks.get("transmission"))
            
            # Dealer specific fields
            is_certified = self.dealer_config.get("is_certified_dealer", False)
            warranty_months = self.dealer_config.get("default_warranty_months", 0)

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
                "transmission": transmission,
                "scraped_at": datetime.utcnow().isoformat(),
                "images_urls": [],
                "is_certified": is_certified,
                "has_warranty": warranty_months > 0,
                "warranty_months": warranty_months,
                "is_pro": True
            }
            return raw_data
        except Exception as e:
            logger.error(f"Error parsing listing element: {e}")
            return None

    def _extract_brand_model(self, title: str, default_brand: str) -> tuple:
        if not title:
            return default_brand, None
            
        if default_brand:
            title_lower = title.lower()
            default_brand_lower = default_brand.lower()
            if title_lower.startswith(default_brand_lower):
                model = title[len(default_brand):].strip()
                return default_brand, model if model else title
            return default_brand, title

        brands = [
            'Dacia', 'Renault', 'Peugeot', 'Citroën', 'Citroen',
            'Hyundai', 'Kia', 'Toyota', 'Volkswagen', 'VW',
            'BMW', 'Mercedes', 'Audi', 'Ford', 'Fiat'
        ]
        title_lower = title.lower()
        for b in brands:
            if title_lower.startswith(b.lower() + ' ') or title_lower == b.lower():
                model = title[len(b):].strip()
                return b, model if model else None
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
