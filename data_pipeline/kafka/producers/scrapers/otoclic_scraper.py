from datetime import datetime
from typing import List, Dict, Any, Optional
import logging
import re

from bs4 import BeautifulSoup

from .base_scraper import BaseScraper
from . import config
from .selector_loader import SelectorLoader
from .extraction_fallback import FallbackExtractor

logger = logging.getLogger(__name__)

class OtoclicScraper(BaseScraper):
    def __init__(self):
        super().__init__(
            base_url="https://www.otoclic.ma/voitures-occasion",
            source_name="otoclic"
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
        # Default implementation, may need override per platform
        urls = [self.base_url]
        for page in range(2, max_pages + 1):
            urls.append(f"{self.base_url}?page={page}")
        return urls

    def _parse_listings_page(self, html: str, max_items: int) -> List[Dict[str, Any]]:
        soup = BeautifulSoup(html, 'html.parser')
        listings = []

        selectors = self.selector_loader.load(self.source_name)
        card_sel = selectors.get("listing_card", ".default-card")
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
                logger.error(f"Error parsing {self.source_name} listing element: {e}")

        return listings

    def _parse_listing_element(self, elem) -> Optional[Dict[str, Any]]:
        try:
            selectors = self.selector_loader.load(self.source_name)
            fields = selectors.get("fields", {})
            fallbacks = selectors.get("fallback_fields", {})
            
            source_url = FallbackExtractor.extract_attr(
                elem, fields.get("url"), "href", fallbacks.get("url")
            )
            if source_url and not source_url.startswith('http'):
                # Assuming relative URLs might need the base domain, to be customized
                domain = self.base_url.split('/')[0] + '//' + self.base_url.split('/')[2]
                source_url = f"{domain}{source_url}"

            price = FallbackExtractor.extract_text(
                elem, fields.get("price"), fallbacks.get("price"), heuristic="price"
            )

            title = FallbackExtractor.extract_text(
                elem, fields.get("title"), fallbacks.get("title")
            )
            brand, model = self._extract_brand_model(title or '')

            city = FallbackExtractor.extract_text(
                elem, fields.get("city"), fallbacks.get("city")
            )

            # Specs
            year = self._parse_int(FallbackExtractor.extract_text(elem, fields.get("year"), fallbacks.get("year"), heuristic="year"))
            mileage = self._parse_int(FallbackExtractor.extract_text(elem, fields.get("mileage"), fallbacks.get("mileage")))
            fuel_type = FallbackExtractor.extract_text(elem, fields.get("fuel_type"), fallbacks.get("fuel_type"))
            transmission = FallbackExtractor.extract_text(elem, fields.get("transmission"), fallbacks.get("transmission"))
            body_type = FallbackExtractor.extract_text(elem, fields.get("body_type"), fallbacks.get("body_type"))

            # Trust metrics
            is_inspected = FallbackExtractor.extract_text(elem, fields.get("is_inspected"), fallbacks.get("is_inspected"))
            is_inspected_bool = bool(is_inspected) if is_inspected else False
            
            inspection_points = self._parse_int(FallbackExtractor.extract_text(elem, fields.get("inspection_points"), fallbacks.get("inspection_points")))
            
            has_warranty = FallbackExtractor.extract_text(elem, fields.get("has_warranty"), fallbacks.get("has_warranty"))
            has_warranty_bool = bool(has_warranty) if has_warranty else False
            
            warranty_months = self._parse_int(FallbackExtractor.extract_text(elem, fields.get("warranty_months"), fallbacks.get("warranty_months")))
            
            is_certified = FallbackExtractor.extract_text(elem, fields.get("is_certified"), fallbacks.get("is_certified"))
            is_certified_bool = bool(is_certified) if is_certified else False

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
                "images_urls": [],
                "is_inspected": is_inspected_bool,
                "inspection_points": inspection_points,
                "has_warranty": has_warranty_bool,
                "warranty_months": warranty_months,
                "is_certified": is_certified_bool
            }
            return raw_data
        except Exception as e:
            logger.error(f"Error parsing listing element: {e}")
            return None

    def _extract_brand_model(self, title: str) -> tuple:
        if not title:
            return None, None
        brands = [
            'Dacia', 'Renault', 'Peugeot', 'Citroën', 'Citroen',
            'Hyundai', 'Kia', 'Toyota', 'Volkswagen', 'VW',
            'BMW', 'Mercedes', 'Audi', 'Ford', 'Fiat'
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
