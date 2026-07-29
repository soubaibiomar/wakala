"""
Kifal Auto – Occasion Certifiée (contrôle technique 200 points)
Structure HTML inspectée le 29/07/2026 :
  - URL : https://occasion.kifal.ma/annonces?page={n}
  - robots.txt : "Disallow:" vide → scraping autorisé
  - Cartes annonce : div.card-annonce (avec data-url pour l'URL relative de la fiche)
  - Lien détail : a.mrktplc-annonce-card[href] (href absolu vers occasion.kifal.ma/annonce/...)
  - Titre : a[title] dans la carte (ex: "AUDI Q7")
  - Marque/Modèle/Année : dans l'attribut onclick pushDataLayer (product_brand, product_model, product_year)
  - Image : img.cover-image dans .item-card9-imgs (CDN AWS: cdnmdj3lv0.execute-api...)
  - Prix : .text-primary dans .card-body (ex: "570 000 Dh")
  - Mensualité : "A partir de X dh / mois" dans la même zone
  - Ville : dans l'URL (ex: ..._CASABLANCA_...)

Kifal Auto est un professionnel avec garantie — certifie=True pour toutes les annonces.
"""
from scrapers.base_scraper import BaseScraper
import re


class KifalAutoScraper(BaseScraper):
    platform_name = "kifal_auto"
    listing_type = "occasion"
    base_url = "https://occasion.kifal.ma"

    def get_listing_urls(self, page: int) -> list[str]:
        search_url = f"{self.base_url}/annonces?page={page}"
        try:
            response = self.session.get(search_url, delay=2)
            if response.status_code != 200:
                return []
            soup = self._make_soup(response.text)

            urls = []
            # Sélecteur inspecté : a.mrktplc-annonce-card avec href vers /annonce/
            for a in soup.select("a.mrktplc-annonce-card[href]"):
                href = a.get("href", "")
                if "/annonce/" in href:
                    urls.append(self._absolute_url(href))

            return list(dict.fromkeys(urls))
        except Exception as e:
            print(f"[kifal_auto] Erreur get_listing_urls: {e}")
            return []

    def parse_listing(self, html: str, url: str) -> dict:
        soup = self._make_soup(html)

        # Titre : a[title] ou h1
        titre = ""
        title_a = soup.select_one("a[title]")
        if title_a:
            titre = title_a.get("title", "")
        if not titre:
            titre = self._extract_text(soup, ["h1", ".title-card-full-annonce"], "")

        # Prix
        prix = self._extract_text(soup, [
            ".text-primary",
            "[class*=price]",
            "[class*=prix]",
        ], "")
        # Nettoyer la mensualité qui peut être collée au prix
        if "mois" in prix:
            prix = prix.split("A partir")[0].strip()

        # Description / caractéristiques techniques
        description = self._extract_text(soup, [
            "[class*=description]",
            ".item-card9-desc",
            ".card-body p",
        ], "")

        # Extraire la ville depuis l'URL (format: ..._VILLE_...)
        ville = ""
        url_match = re.search(r"_([A-Z]+(?:%20[A-Z]+)*)_\d+_", url)
        if url_match:
            ville = url_match.group(1).replace("%20", " ").title()

        # Photos : CDN AWS (cdnmdj3lv0.execute-api...)
        photos = []
        for img in soup.select("img.cover-image, img[src*=cdnmdj3lv0], img[src*=kifal]"):
            src = img.get("src") or img.get("data-src") or ""
            if src and not src.startswith("data:"):
                photos.append(src)

        vendeur_info = {"type": "professionnel_certifie"}
        if ville:
            vendeur_info["ville"] = ville

        return self._build_raw_listing(
            titre=titre,
            prix=prix,
            description=description,
            photos=photos,
            vendeur_info=vendeur_info,
            date_pub=None,
            url=url,
            certifie=True,  # Kifal Auto = occasion certifiée 200 points
        )
