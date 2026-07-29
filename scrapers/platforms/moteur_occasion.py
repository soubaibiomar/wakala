"""
Moteur.ma – Annonces Occasion
Structure HTML inspectée le 29/07/2026 :
  - URL de recherche : /fr/voiture/achat-voiture-occasion/?page={n}
  - Cartes d'annonce : div.card.ads-index-card
  - Lien détail : a.link ou a.text-dark avec href contenant /detail-annonce/
  - Titre : h5.ads-index-title
  - Prix : .text-primary (dans la carte)
  - Image : img.ads-index-media-img (src = content.avito.ma/... — feed partagé)
  - Ville : .fa-map-marker + texte adjacent
  - robots.txt : Crawl-delay: 10 → on utilise delay=3 (page, pas crawl complet)
"""
from scrapers.base_scraper import BaseScraper


class MoteurOccasionScraper(BaseScraper):
    platform_name = "moteur"
    listing_type = "occasion"
    base_url = "https://www.moteur.ma"

    def get_listing_urls(self, page: int) -> list[str]:
        search_url = f"{self.base_url}/fr/voiture/achat-voiture-occasion/?page={page}"
        try:
            response = self.session.get(search_url, delay=3)
            if response.status_code != 200:
                return []
            soup = self._make_soup(response.text)

            urls = []
            # Sélecteur inspecté : liens dans les cartes .ads-index-card
            for a in soup.select(".ads-index-card a.link, .ads-index-card a.text-dark"):
                href = a.get("href", "")
                if "/detail-annonce/" in href:
                    urls.append(self._absolute_url(href))

            return list(dict.fromkeys(urls))
        except Exception as e:
            print(f"[moteur_occasion] Erreur get_listing_urls: {e}")
            return []

    def parse_listing(self, html: str, url: str) -> dict:
        soup = self._make_soup(html)

        # Titre : h1 ou h5.ads-index-title sur la page de détail
        titre = self._extract_text(soup, ["h1", "h5.ads-index-title"], "")

        # Prix : span ou div contenant "DH" / "Dhs"
        prix = self._extract_text(soup, [
            "[class*=price]",
            ".text-primary",
            "h6.text-primary",
        ], "")

        # Description
        description = self._extract_text(soup, [
            ".item-card9-desc",
            "[class*=description]",
            "[class*=desc]",
        ], "")

        # Photos : images provenant du CDN Avito ou du stockage Moteur
        photos = []
        for img in soup.select("img"):
            src = img.get("src") or img.get("data-src") or ""
            if any(domain in src for domain in ["content.avito.ma", "moteur.ma/storage"]):
                photos.append(src)

        # Vendeur
        vendeur_info = {}
        seller = soup.select_one("[class*=seller], [class*=vendeur]")
        if seller:
            vendeur_info["nom"] = seller.text.strip()

        # Ville
        ville_el = soup.select_one(".fa-map-marker")
        if ville_el and ville_el.parent:
            ville_text = ville_el.parent.text.strip()
            if ville_text:
                vendeur_info["ville"] = ville_text

        # Date
        date_pub = None
        date_el = soup.select_one("time, [class*=date]")
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
