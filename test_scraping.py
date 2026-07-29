import sys
sys.path.insert(0, ".")

# Test imports
from scrapers.base_scraper import BaseScraper
print("OK: base_scraper")

from scrapers.platforms.avito_occasion import AvitoOccasionScraper
from scrapers.platforms.avito_neuf import AvitoNeufScraper
from scrapers.platforms.moteur_occasion import MoteurOccasionScraper
from scrapers.platforms.moteur_neuf import MoteurNeufScraper
from scrapers.platforms.wandaloo_occasion import WandalooOccasionScraper
from scrapers.platforms.wandaloo_neuf import WandalooNeufScraper
from scrapers.platforms.global_occaz import GlobalOccazScraper
from scrapers.platforms.otoclic import OtoclicScraper
from scrapers.platforms.kifal_auto import KifalAutoScraper
from scrapers.platforms.spoticar import SpoticarScraper
print("OK: all 10 scrapers imported")

# Verify they all inherit from BaseScraper
scrapers = [
    AvitoOccasionScraper, AvitoNeufScraper,
    MoteurOccasionScraper, MoteurNeufScraper,
    WandalooOccasionScraper, WandalooNeufScraper,
    GlobalOccazScraper, OtoclicScraper,
    KifalAutoScraper, SpoticarScraper,
]
for s in scrapers:
    assert issubclass(s, BaseScraper), f"{s.__name__} does not inherit BaseScraper"
    assert hasattr(s, "platform_name"), f"{s.__name__} missing platform_name"
    assert hasattr(s, "listing_type"), f"{s.__name__} missing listing_type"
    assert hasattr(s, "base_url"), f"{s.__name__} missing base_url"
    print(f"  {s.__name__}: platform={s.platform_name}, type={s.listing_type}")

# Test dynamic import from pipeline
from services.ingestion_pipeline import get_scraper_class
from config import ACTIVE_SCRAPERS

print(f"\nACTIVE_SCRAPERS: {ACTIVE_SCRAPERS}")
for name in ACTIVE_SCRAPERS:
    cls = get_scraper_class(name)
    print(f"  {name} -> {cls.__name__}")

# Test deduplication
from services.deduplication import deduplicate_listings
test_data = [
    {"marque": "dacia", "modele": "logan", "annee": "2020", "prix_brut": "100 000 DH",
     "source_plateforme": "avito", "url_source": "https://avito.ma/1", "vendeur_info": {"ville": "casa"}},
    {"marque": "dacia", "modele": "logan", "annee": "2020", "prix_brut": "101 000 DH",
     "source_plateforme": "moteur", "url_source": "https://moteur.ma/1", "vendeur_info": {"ville": "casa"}},
    {"marque": "peugeot", "modele": "208", "annee": "2022", "prix_brut": "170 000 DH",
     "source_plateforme": "wandaloo", "url_source": "https://wandaloo.com/1", "vendeur_info": {}},
]
result = deduplicate_listings(test_data)
print(f"\nDeduplication test: {len(test_data)} input -> {len(result)} output")
for r in result:
    sources = r.get("sources_multiples", [r.get("source_plateforme")])
    marque = r["marque"]
    modele = r["modele"]
    print(f"  {marque} {modele} -> sources: {sources}")

# Test normalizer (import only, no Ollama needed)
from services.listing_normalizer import normalize_listing, SYSTEM_PROMPT_OCCASION, SYSTEM_PROMPT_NEUF
# Occasion doit extraire signaux_suspects
assert "signaux_suspects" in SYSTEM_PROMPT_OCCASION
# Neuf doit extraire promotions_detectees
assert "promotions_detectees" in SYSTEM_PROMPT_NEUF
# Neuf dit explicitement de NE PAS générer signaux_suspects
assert "NE génère AUCUN" in SYSTEM_PROMPT_NEUF
# Occasion dit explicitement de NE PAS générer promotions_detectees
assert "NE génère PAS" in SYSTEM_PROMPT_OCCASION
print("\nNormalizer prompts: OK (neuf/occasion distinction verified)")

print("\n=== TOUS LES TESTS PASSENT ===")
