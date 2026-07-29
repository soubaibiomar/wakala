"""
Otoclic.ma – Occasion avec reprise
Structure HTML inspectée le 29/07/2026 :
  - URL : https://www.otoclic.ma/ (landing page avec véhicules)
  - Cartes véhicule : div.car-item
  - Image : img.img-responsive dans .car-image (data-src pour lazy loading)
  - Lien détail : a dans .car-image (href = https://www.otoclic.com/cars/{slug}/)
  - Prix : dans .car-content (ex: "182.000 Dhs")
  - Année/Boîte/Km : ul.list-inline dans .car-list
  - robots.txt : pas de restriction notable pour le scraping

NOTE : le domaine principal est otoclic.ma mais les liens détail pointent
vers otoclic.com — les deux domaines coexistent.
"""
from scrapers.base_scraper import BaseScraper


class OtoclicScraper(BaseScraper):
    platform_name = "otoclic"
    listing_type = "occasion"
    base_url = "https://www.otoclic.com"

    def get_listing_urls(self, page: int) -> list[str]:
        """
        Otoclic utilise WordPress avec des pages de catalogue :
        /acheter-votre-voiture-doccasion/page/{n}/
        """
        if page == 1:
            search_url = f"{self.base_url}/acheter-votre-voiture-doccasion/"
        else:
            search_url = f"{self.base_url}/acheter-votre-voiture-doccasion/page/{page}/"

        try:
            response = self.session.get(search_url, delay=2)
            if response.status_code != 200:
                return []
            soup = self._make_soup(response.text)

            urls = []
            # Sélecteur inspecté : liens dans les cartes .car-item
            for a in soup.select(".car-item .car-image a"):
                href = a.get("href", "")
                if "/cars/" in href:
                    urls.append(href)

            return list(dict.fromkeys(urls))
        except Exception as e:
            print(f"[otoclic] Erreur get_listing_urls: {e}")
            return []

    def parse_listing(self, html: str, url: str) -> dict:
        soup = self._make_soup(html)

        titre = self._extract_text(soup, ["h1", "h3", ".car-title"], "")
        prix = self._extract_text(soup, [".car-price", "[class*=price]", ".price"], "")
        description = self._extract_text(soup, [
            ".car-description",
            "[class*=description]",
            ".content p",
        ], "")

        # Métadonnées techniques : année, boîte, km dans la liste
        specs = []
        for li in soup.select(".car-list li, .car-details li"):
            specs.append(li.text.strip())
        if specs and not description:
            description = " | ".join(specs)

        # Photos
        photos = []
        for img in soup.select(".car-image img, .gallery img, .slider img"):
            src = img.get("src") or img.get("data-src") or ""
            if src and not src.startswith("data:") and "otoclic" in src:
                photos.append(src)

        return self._build_raw_listing(
            titre=titre,
            prix=prix,
            description=description,
            photos=photos,
            vendeur_info={},  # Otoclic = plateforme pro, pas de vendeur individuel
            date_pub=None,
            url=url,
            certifie=False,
        )
