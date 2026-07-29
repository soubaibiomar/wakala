ACTIVE_SCRAPERS = [
    "avito_occasion",
    "moteur_occasion",
    "wandaloo_occasion",
    "global_occaz",
    "otoclic",
    "kifal_auto",
    "spoticar",
    "avito_neuf",
    "moteur_neuf",
    "wandaloo_neuf"
]

# Délais par plateforme pour éviter le ban (en secondes)
SCRAPER_DELAYS = {
    "avito": 5,
    "moteur": 3,
    "wandaloo": 4,
    "global_occaz": 2,
    "otoclic": 2,
    "kifal_auto": 2,
    "spoticar": 2
}

CACHE_TTL_HOURS = 24
