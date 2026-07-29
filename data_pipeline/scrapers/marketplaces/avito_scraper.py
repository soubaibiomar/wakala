"""
Avito.ma Scraper — Occasion + Neuf
URL occasion: https://www.avito.ma/fr/maroc/voitures_d_occasion-à_vendre
URL neuf:     https://www.avito.ma/fr/maroc/voitures_neuves
Structure: Next.js SSR with __NEXT_DATA__ JSON payload
"""
import json
import os
import re
import yaml
import logging
from typing import List, Optional
from datetime import datetime

from core.base_scraper import BaseScraper
from models.listing import RawListing

logger = logging.getLogger(__name__)


class AvitoScraper(BaseScraper):
    platform_name = "avito"
    listing_type = "both"
    is_certified = False

    def __init__(self):
        config_path = os.path.join(os.path.dirname(__file__), "..", "config", "sites.yaml")
        with open(config_path, "r", encoding="utf-8") as f:
            self.config = yaml.safe_load(f)["avito"]

        delay = tuple(self.config.get("delay", [3.0, 6.0]))
        super().__init__(polite_delay=delay)

        self.base_url = self.config["base_url"]

    def get_listing_urls(self, max_pages: int = 2) -> List[str]:
        urls = []

        # --- 1. Occasion listings ---
        for page in range(1, max_pages + 1):
            url = self.config["used_url"].format(page=page)
            resp = self.client.get(url)
            if resp.status_code != 200:
                break

            from bs4 import BeautifulSoup
            soup = BeautifulSoup(resp.text, "html.parser")
            links = soup.select("a[href*='/voitures_d_occasion/']")
            for link in links:
                href = link.get("href")
                if href and href not in urls:
                    urls.append(href)

        # --- 2. Neuf listings (concessionnaires sur Avito) ---
        try:
            resp = self.client.get(self.config.get("new_url", ""))
            if resp.status_code == 200:
                from bs4 import BeautifulSoup
                soup = BeautifulSoup(resp.text, "html.parser")
                links = soup.select("a[href*='/voitures_neuves/']")
                for link in links:
                    href = link.get("href")
                    if href and href not in urls:
                        urls.append(href)
        except Exception as e:
            logger.warning(f"[avito] Could not fetch neuf page: {e}")

        return list(set(urls))

    def parse_listing(self, html: str, url: str) -> Optional[RawListing]:
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(html, "html.parser")

        is_new = "voitures_neuves" in url
        type_annonce = "neuf" if is_new else "occasion"

        # Extract __NEXT_DATA__ JSON
        next_data = soup.find("script", id="__NEXT_DATA__")
        if not next_data:
            return None

        try:
            data = json.loads(next_data.text)
            ad = (
                data.get("props", {})
                .get("pageProps", {})
                .get("initialReduxState", {})
                .get("ad", {})
                .get("view", {})
                .get("adInfo", {})
            )

            if not ad:
                return None

            title = ad.get("subject", "")
            price_val = ad.get("price", {}).get("value", 0)
            prix = f"{price_val} DH" if price_val else ""

            # Parameters
            params = {p.get("name"): p.get("value") for p in ad.get("params", [])}

            marque = params.get("Marque", "")
            modele = params.get("Modèle", "")
            annee = params.get("Année-Modèle", "")
            km = params.get("Kilométrage", "0" if is_new else "")
            carburant = params.get("Type de carburant", "")
            transmission = params.get("Boite de vitesses", "")

            city = ad.get("location", {}).get("city", {}).get("name", "")
            description = ad.get("description", "")

            # Images
            images = []
            for img in ad.get("images", []):
                img_url = img.get("url")
                if img_url:
                    images.append(img_url)

            # Vendeur info
            vendeur = {}
            seller = ad.get("seller", {})
            if seller:
                vendeur["nom"] = seller.get("name", "")
                vendeur["type"] = seller.get("type", "")

            # Date
            date_pub = ad.get("date", None)

            return RawListing(
                source_plateforme=self.platform_name,
                type_annonce=type_annonce,
                titre_brut=title,
                prix_brut=prix,
                description_brute=description,
                photos_urls=images,
                vendeur_info=vendeur,
                date_publication=date_pub,
                url_source=url,
                certifie=False,
                marque_brute=marque,
                modele_brut=modele,
                annee_brute=annee,
                kilometrage_brut=km,
                carburant_brut=carburant,
                transmission_brute=transmission,
                ville_brute=city,
            )

        except Exception as e:
            logger.error(f"[avito] Error parsing listing {url}: {e}")
            return None
