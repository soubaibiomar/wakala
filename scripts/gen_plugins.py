import os
platforms = [
    ('moteur', 'occasion', 'False'), ('wandaloo', 'occasion', 'False'),
    ('global_occaz', 'occasion', 'False'), ('otoclic', 'occasion', 'False'),
    ('kifal_auto', 'occasion', 'True'), ('spoticar', 'occasion', 'True'),
    ('moteur', 'neuf', 'False'), ('wandaloo', 'neuf', 'False')
]

for p, t, cert in platforms:
    class_name = ''.join(word.capitalize() for word in p.split('_')) + t.capitalize() + 'Scraper'
    code = f"""from scrapers.base_scraper import BaseScraper

class {class_name}(BaseScraper):
    platform_name = "{p}"
    listing_type = "{t}"

    def get_listing_urls(self, page: int) -> list[str]:
        return [f"https://example.com/{p}/{t}/annonce_{{page}}"]

    def parse_listing(self, html: str, url: str) -> dict:
        return {{
            "source_plateforme": self.platform_name,
            "type_annonce": self.listing_type,
            "titre_brut": "Exemple {class_name}",
            "prix_brut": "100 000 DH",
            "description_brute": "Description exemple",
            "photos_urls": ["http://example.com/photo.jpg"],
            "vendeur_info": {{}} if self.listing_type == "neuf" else {{"nom": "Vendeur"}},
            "date_publication": "2026-07-28",
            "url_source": url,
            "certifie": {cert}
        }}
"""
    with open(f'scrapers/platforms/{p}_{t}.py', 'w', encoding='utf-8') as f:
        f.write(code)
