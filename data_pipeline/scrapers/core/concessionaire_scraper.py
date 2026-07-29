from abc import ABC, abstractmethod
from typing import List, Any
import logging

from models.listing import ModelCatalogEntry
from core.http_client import ScraperHTTPClient

logger = logging.getLogger(__name__)

class ConcessionaireScraper(ABC):
    """
    Base class for official concessionaire brand catalogs (new cars without individual VINs).
    """
    site_name: str
    base_url: str

    def __init__(self):
        self.client = ScraperHTTPClient()

    @abstractmethod
    def get_models(self) -> List[ModelCatalogEntry]:
        """
        Scrape the brand's model catalog and return a list of ModelCatalogEntry.
        """
        pass

    def run(self, max_pages: int = None) -> List[ModelCatalogEntry]:
        """
        Orchestrate the scraping process.
        max_pages is ignored here, usually it's just one or two catalog pages.
        """
        logger.info(f"Starting concessionaire scraper for {self.site_name}")
        
        try:
            catalog = self.get_models()
            logger.info(f"Successfully scraped {len(catalog)} models from {self.site_name}.")
            return catalog
        except Exception as e:
            logger.error(f"Error scraping catalog from {self.site_name}: {e}")
            return []
