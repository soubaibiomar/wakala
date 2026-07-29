"""
Spoticar.ma Scraper — Occasion Certifiée (Stellantis)
URL: https://www.spoticar.ma/voitures-occasion
Structure: listing page → /voitures-occasion/{marque}/{modele}/... (detail page)
Note: robots.txt exige Crawl-delay: 10 — respecté via delay=(5.0, 10.0)
"""
import os
import re
import yaml
import logging
from typing import List, Optional
from bs4 import BeautifulSoup

from core.base_scraper import BaseScraper
from models.listing import RawListing

logger = logging.getLogger(__name__)


class SpoticarScraper(BaseScraper):
    platform_name = "spoticar"
    listing_type = "occasion"
    is_certified = True

    def __init__(self):
        config_path = os.path.join(os.path.dirname(__file__), "..", "config", "sites.yaml")
        with open(config_path, "r", encoding="utf-8") as f:
            self.config = yaml.safe_load(f)["spoticar"]

        delay = tuple(self.config.get("delay", [5.0, 10.0]))
        super().__init__(polite_delay=delay)

        self.base_url = self.config["base_url"]
        self.selectors = self.config.get("selectors", {})

    def get_listing_urls(self, max_pages: int = 2) -> List[str]:
        urls = []
        for page in range(0, max_pages):  # Spoticar may use 0-indexed pagination
            search_url = self.config["search_url"].format(page=page)
            resp = self.client.get(search_url)
            if resp.status_code != 200:
                logger.warning(f"[spoticar] Page {page} returned {resp.status_code}")
                break

            soup = BeautifulSoup(resp.text, "html.parser")

            # Spoticar uses vehicle-card elements with detail links under /acheter-voiture-occasion/
            cards = soup.select("[class*=vehicle]")
            for card in cards:
                card_links = card.select("a[href*='/acheter-voiture-occasion/']")
                for link in card_links:
                    href = link.get("href", "")
                    if href and not href.startswith("javascript"):
                        full_url = self.base_url + href if not href.startswith("http") else href
                        urls.append(full_url)

            if not cards:
                break

        return list(set(urls))

    def parse_listing(self, html: str, url: str) -> Optional[RawListing]:
        soup = BeautifulSoup(html, "html.parser")

        # Title
        title_el = soup.select_one("h1") or soup.select_one(".vehicle-title")
        if not title_el:
            return None
        title = title_el.text.strip()

        # Price
        prix = ""
        price_el = soup.select_one(".price-value") or soup.select_one(".vehicle-card-price")
        if price_el:
            prix = price_el.text.strip()

        # Description
        desc_el = soup.select_one(".vehicle-description, .description, .vehicle-details")
        description = desc_el.text.strip() if desc_el else title

        # Images
        images = []
        for img in soup.select(".vehicle-gallery img, .slider img, .carousel img"):
            src = img.get("src") or img.get("data-src")
            if src and "logo" not in src.lower():
                if not src.startswith("http"):
                    src = self.base_url + src
                images.append(src)

        # Extract structured fields from full page text
        page_text = soup.get_text()

        marque = self._extract_from_url(url, 0)
        modele = self._extract_from_url(url, 1)
        annee = self._extract_year(page_text)
        km = self._extract_km(page_text)
        carburant = self._extract_field(page_text, ["diesel", "essence", "hybride", "electrique", "électrique"])
        transmission = self._extract_field(page_text, ["automatique", "manuelle", "manuel", "bvm", "bva"])

        # Ville
        ville = ""
        city_el = soup.select_one(".dealer-city, .location, [class*=city]")
        if city_el:
            ville = city_el.text.strip()

        return RawListing(
            source_plateforme=self.platform_name,
            type_annonce="occasion",
            titre_brut=title,
            prix_brut=prix,
            description_brute=description,
            photos_urls=images,
            vendeur_info={"type": "concessionnaire_certifie", "label": "Spoticar"},
            url_source=url,
            certifie=True,
            marque_brute=marque,
            modele_brut=modele,
            annee_brute=annee,
            kilometrage_brut=km,
            carburant_brut=carburant,
            transmission_brute=transmission,
            ville_brute=ville,
        )

    # ── Helpers ──────────────────────────────────────────────

    def _extract_from_url(self, url: str, index: int) -> str:
        """Extract brand/model from URL like /acheter-voiture-occasion/fiat-500x-14-fire-..."""
        parts = [p for p in url.split("/") if p]
        try:
            base_idx = parts.index("acheter-voiture-occasion")
            slug = parts[base_idx + 1] if len(parts) > base_idx + 1 else ""
            # Slug format: marque-modele-details-ville-id
            slug_parts = slug.split("-")
            if index == 0:
                return slug_parts[0].capitalize() if slug_parts else ""
            elif index == 1:
                return slug_parts[1] if len(slug_parts) > 1 else ""
        except (ValueError, IndexError):
            pass
        return ""

    def _extract_year(self, text: str) -> str:
        match = re.search(r"\b(19|20)\d{2}\b", text)
        return match.group(0) if match else ""

    def _extract_km(self, text: str) -> str:
        match = re.search(r"([\d\s\.]+)\s*km", text, re.IGNORECASE)
        return match.group(1).strip() if match else ""

    def _extract_field(self, text: str, keywords: list) -> str:
        text_lower = text.lower()
        for kw in keywords:
            if kw in text_lower:
                return kw
        return ""
