from abc import ABC, abstractmethod
from typing import List, Optional
import logging

from models.listing import RawListing
from core.http_client import ScraperHTTPClient

logger = logging.getLogger(__name__)


class BaseScraper(ABC):
    """
    Abstract base class for all Wakala scrapers (marketplaces + concessionaires).

    Every platform scraper must:
    1. Define `platform_name` (e.g. "avito", "moteur", "wandaloo")
    2. Define `listing_type` ("neuf", "occasion", or "both")
    3. Implement `get_listing_urls()` to discover listing pages
    4. Implement `parse_listing()` to extract a RawListing from HTML

    The `run()` method orchestrates the full lifecycle:
        get_listing_urls → fetch each → parse_listing → return list of RawListing
    """
    platform_name: str = "unknown"
    listing_type: str = "occasion"     # "neuf", "occasion", or "both"
    is_certified: bool = False          # True for Kifal Auto, Spoticar

    def __init__(self, polite_delay: tuple = (1.0, 3.0)):
        self.client = ScraperHTTPClient(
            polite_delay_min=polite_delay[0],
            polite_delay_max=polite_delay[1]
        )

    @abstractmethod
    def get_listing_urls(self, max_pages: int = 2) -> List[str]:
        """
        Paginate search/listing pages and collect individual ad URLs.
        """
        pass

    @abstractmethod
    def parse_listing(self, html: str, url: str) -> Optional[RawListing]:
        """
        Parse one ad page into the unified RawListing schema.
        Should return None if the listing is invalid or sold.
        """
        pass

    def determine_type(self, url: str) -> str:
        """
        Determine whether a URL is for a 'neuf' or 'occasion' listing.
        Subclasses can override for more specific logic.
        """
        if self.listing_type != "both":
            return self.listing_type

        neuf_patterns = ["/neuf/", "/voiture-neuve/", "/neuf/voiture/", "/fr/neuf/"]
        for pattern in neuf_patterns:
            if pattern in url:
                return "neuf"
        return "occasion"

    def run(self, max_pages: int = 2) -> List[RawListing]:
        """
        Orchestrate the scraping process:
        1. Get all listing URLs
        2. Fetch each page
        3. Parse into RawListing
        4. Return collected listings
        """
        logger.info(f"Starting scraper for {self.platform_name} (type={self.listing_type}, max_pages={max_pages})")
        urls = self.get_listing_urls(max_pages=max_pages)
        logger.info(f"[{self.platform_name}] Found {len(urls)} listing URLs to parse.")

        listings = []
        errors = 0
        for i, url in enumerate(urls):
            logger.info(f"[{self.platform_name}] Parsing {i+1}/{len(urls)}: {url}")
            try:
                response = self.client.get(url)
                if response.status_code != 200:
                    logger.warning(f"[{self.platform_name}] Failed to fetch {url} (status: {response.status_code})")
                    errors += 1
                    continue

                raw = self.parse_listing(response.text, url)
                if raw:
                    listings.append(raw)
            except Exception as e:
                logger.error(f"[{self.platform_name}] Error parsing listing {url}: {e}")
                errors += 1

        logger.info(
            f"[{self.platform_name}] Completed: {len(listings)} scraped, "
            f"{errors} errors, {len(urls) - len(listings) - errors} skipped."
        )
        return listings
