"""
Moteur.ma – Catalogue Neuf
Structure HTML inspectée le 29/07/2026 :
  - URL catalogue : /fr/neuf/voiture/?page={n}
  - Cartes modèle : div.item contenant div.card
  - Marque : h4 dans .card-body
  - Modèle : h6.mb-2
  - Prix catalogue : h6.text-primary (ex: "409 900 Dhs")
  - Image : img.promo-model-img (src = moteur.ma/storage/media/images/models/...)
  - Lien détail : a.link avec href /fr/neuf/voiture/{marque}/{modele}/
  - Versions en promo : texte dans .card-footer > small.text-muted
"""
from scrapers.base_scraper import BaseScraper


class MoteurNeufScraper(BaseScraper):
    platform_name = "moteur"
    listing_type = "neuf"
    base_url = "https://www.moteur.ma"

    def get_listing_urls(self, page: int) -> list[str]:
        search_url = f"{self.base_url}/fr/neuf/voiture/?page={page}"
        try:
            response = self.session.get(search_url, delay=3)
            if response.status_code != 200:
                return []
            soup = self._make_soup(response.text)

            urls = []
            for a in soup.select(".item a.link, .promo-vehicles-row"):
                href = a.get("href", "")
                if "/fr/neuf/voiture/" in href and href.count("/") >= 5:
                    urls.append(self._absolute_url(href))

            return list(dict.fromkeys(urls))
        except Exception as e:
            print(f"[moteur_neuf] Erreur get_listing_urls: {e}")
            return []

    def parse_listing(self, html: str, url: str) -> dict:
        soup = self._make_soup(html)

        # Titre = Marque + Modèle (présents en h4 et h6 dans la carte, ou h1 sur la page détail)
        titre = self._extract_text(soup, ["h1", "h4"], "")
        modele = self._extract_text(soup, ["h6.mb-2", "h6:not(.text-primary)"], "")
        if modele and modele not in titre:
            titre = f"{titre} {modele}".strip()

        prix = self._extract_text(soup, ["h6.text-primary", "[class*=price]"], "")
        description = self._extract_text(soup, [
            "[class*=description]",
            "[class*=desc]",
            ".card-body p",
        ], "")

        # Photos : modèles depuis le storage Moteur.ma
        photos = []
        for img in soup.select("img"):
            src = img.get("src") or img.get("data-src") or ""
            if "moteur.ma/storage" in src:
                photos.append(src)

        return self._build_raw_listing(
            titre=titre,
            prix=prix,
            description=description,
            photos=photos,
            vendeur_info={},  # Catalogue constructeur — pas de vendeur individuel
            date_pub=None,
            url=url,
            certifie=False,
        )
