"""
Avito.ma – Annonces Neuf
Même anti-bot que pour l'occasion. Le neuf sur Avito passe par la même
structure de carte React (a[data-testid^="ad-card-v2"]).
"""
from scrapers.base_scraper import BaseScraper


class AvitoNeufScraper(BaseScraper):
    platform_name = "avito"
    listing_type = "neuf"
    base_url = "https://www.avito.ma"

    def get_listing_urls(self, page: int) -> list[str]:
        search_url = f"{self.base_url}/fr/maroc/voitures_neuves-%C3%A0_vendre?o={page}"
        try:
            response = self.session.get(search_url, delay=5)
            if response.status_code != 200:
                return []
            soup = self._make_soup(response.text)
            urls = []
            for a in soup.select('a[data-testid^="ad-card-v2"]'):
                href = a.get("href", "")
                if href.endswith(".htm"):
                    urls.append(self._absolute_url(href))
            return list(dict.fromkeys(urls))
        except Exception as e:
            print(f"[avito_neuf] Erreur get_listing_urls: {e}")
            return []

    def parse_listing(self, html: str, url: str) -> dict:
        soup = self._make_soup(html)
        titre = self._extract_text(soup, ["h1", "[class*=Title]"], "")
        prix = self._extract_text(soup, ["[class*=Price] span", "[class*=price]"], "")
        description = self._extract_text(soup, ["[class*=Description]", "[class*=desc]"], "")

        photos = []
        for img in soup.select("img"):
            src = img.get("src") or img.get("data-src") or ""
            if "content.avito.ma" in src or "classifieds" in src:
                photos.append(src)

        return self._build_raw_listing(
            titre=titre,
            prix=prix,
            description=description,
            photos=photos,
            vendeur_info={},  # Neuf = concessionnaire, pas de vendeur individuel
            date_pub=None,
            url=url,
            certifie=False,
        )
