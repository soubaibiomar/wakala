"""
GlobalOccaz Scraper — STUB DÉSACTIVÉ
URL: https://www.globaloccaz.ma (site hors ligne — timeout DNS)

Ce scraper est prêt à être activé si le site revient en ligne.
Pour l'activer : mettre `enabled: true` dans config/sites.yaml
"""
import os
import yaml
import logging
from typing import List, Optional

from core.base_scraper import BaseScraper
from models.listing import RawListing

logger = logging.getLogger(__name__)


class GlobalOccazScraper(BaseScraper):
    platform_name = "global_occaz"
    listing_type = "occasion"
    is_certified = False

    def __init__(self):
        config_path = os.path.join(os.path.dirname(__file__), "..", "config", "sites.yaml")
        with open(config_path, "r", encoding="utf-8") as f:
            self.config = yaml.safe_load(f)["global_occaz"]

        delay = tuple(self.config.get("delay", [2.0, 4.0]))
        super().__init__(polite_delay=delay)

        self.base_url = self.config["base_url"]
        self.enabled = self.config.get("enabled", False)

    def get_listing_urls(self, max_pages: int = 2) -> List[str]:
        if not self.enabled:
            logger.warning(
                "[global_occaz] Scraper désactivé — le site globaloccaz.ma est hors ligne. "
                "Mettez 'enabled: true' dans sites.yaml pour réactiver."
            )
            return []

        # Placeholder implementation for when the site comes back online
        urls = []
        # TODO: Implement when site is accessible
        return urls

    def parse_listing(self, html: str, url: str) -> Optional[RawListing]:
        if not self.enabled:
            return None

        # TODO: Implement when site is accessible
        return None
