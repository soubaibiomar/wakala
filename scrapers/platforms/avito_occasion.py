"""
Avito.ma – Annonces Occasion
Structure HTML inspectée le 29/07/2026 :
  - Liste : a[data-testid^="ad-card-v2"] contiennent href vers les fiches .htm
  - Image : img.sc-1lb3x1r-3 (src = content.avito.ma/classifieds/images/...)
  - Titre : alt de l'image = titre de l'annonce
  - Prix  : rendu côté client (React SSR partiel)

IMPORTANT : Avito utilise une protection anti-bot robuste (Datadome/Cloudflare).
Les requêtes simples via requests retournent le HTML SSR mais avec des données
partielles. Pour un scraping fiable en production, il faudra utiliser Playwright
ou l'API mobile non documentée d'Avito.
"""
from scrapers.base_scraper import BaseScraper


class AvitoOccasionScraper(BaseScraper):
    platform_name = "avito"
    listing_type = "occasion"
    base_url = "https://www.avito.ma"

    def get_listing_urls(self, page: int) -> list[str]:
        """
        Page de recherche : /fr/maroc/voitures-%C3%A0_vendre?o={page}
        Les liens d'annonces individuelles pointent vers des URLs .htm
        """
        search_url = f"{self.base_url}/fr/maroc/voitures-%C3%A0_vendre?o={page}"
        try:
            response = self.session.get(search_url, delay=5)
            if response.status_code != 200:
                return []
            soup = self._make_soup(response.text)

            urls = []
            # Sélecteur inspecté : a[data-testid^="ad-card-v2"]
            for a in soup.select('a[data-testid^="ad-card-v2"]'):
                href = a.get("href", "")
                if href.endswith(".htm"):
                    urls.append(self._absolute_url(href))

            return list(dict.fromkeys(urls))  # déduplique
        except Exception as e:
            print(f"[avito_occasion] Erreur get_listing_urls: {e}")
            return []

    def parse_listing(self, html: str, url: str) -> dict:
        """
        Parse une fiche annonce Avito occasion.
        Structure inspectée : React SSR – les données sont dans le HTML initial
        mais les sélecteurs sont des noms de classes générés (sc-xxx).
        On utilise des sélecteurs sémantiques + fallback h1/prix.
        """
        soup = self._make_soup(html)

        titre = self._extract_text(soup, ["h1", "[class*=Title]"], "")
        prix = self._extract_text(soup, ["[class*=Price] span", "[class*=price]", "h2"], "")
        description = self._extract_text(soup, ["[class*=Description]", "[class*=desc]", "p"], "")

        # Images : content.avito.ma/classifieds/images/
        photos = []
        for img in soup.select("img"):
            src = img.get("src") or img.get("data-src") or ""
            if "content.avito.ma" in src or "classifieds" in src:
                photos.append(src)

        # Vendeur : nom + ville (souvent dans le titre de la page)
        vendeur_info = {}
        seller = soup.select_one("[class*=seller], [class*=Seller]")
        if seller:
            vendeur_info["nom"] = seller.text.strip()

        date_pub = None
        date_el = soup.select_one("time, [class*=date], [class*=Date]")
        if date_el:
            date_pub = date_el.get("datetime") or date_el.text.strip()

        return self._build_raw_listing(
            titre=titre,
            prix=prix,
            description=description,
            photos=photos,
            vendeur_info=vendeur_info,
            date_pub=date_pub,
            url=url,
            certifie=False,
        )
