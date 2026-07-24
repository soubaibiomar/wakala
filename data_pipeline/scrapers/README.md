# Wakala - Scraper Producer Module

Real web scrapers (Avito.ma, Moteur.ma) as the **sole** Kafka producer for the `listings.raw` topic.
No simulated data anywhere in the ingestion pipeline.

## Architecture

```
data-pipeline/kafka/producers/scrapers/
├── __init__.py
├── config.py              # Central configuration
├── base_scraper.py        # Abstract base (rate limits, robots.txt, retries)
├── avito_scraper.py       # Avito.ma via __NEXT_DATA__ JSON + HTML fallback
├── moteur_scraper.py      # Moteur.ma via HTML card parsing
├── normalizer.py          # Raw -> normalized schema (matches listing_consumer.py)
├── kafka_publisher.py     # Publishes to listings.raw topic
├── scheduler.py           # Periodic execution (APScheduler)
└── run_producer.py        # Single CLI entry point
```

## Key Principles

1. **Dry-run by default** — No network requests unless `--live` is explicitly passed
2. **Respects robots.txt** — Checks before every fetch
3. **Rate limiting** — 3-7s random delay between requests
4. **Retry only 5xx** — Never retries 403/429 (respects server limits)
5. **Single source of truth** — Scrapers are the ONLY producers for `listings.raw`

## Usage

### Development / CI (dry-run, no network)
```bash
# From project root
python -m data_pipeline.kafka.producers.scrapers.run_producer

# Or via docker-compose (dry-run)
docker compose up scraper-producer
```

### Live scraping (explicit opt-in)
```bash
# Single run with real HTTP requests
python -m data_pipeline.kafka.producers.scrapers.run_producer --live

# Scheduled every 12 hours
python -m data_pipeline.kafka.producers.scrapers.run_producer --live --schedule
```

### Docker (production)
```yaml
# In docker-compose.yml - SCRAPER_MODE=live enables real scraping
environment:
  SCRAPER_MODE: "live"
command: python -m data_pipeline.kafka.producers.scrapers.run_producer --live --schedule
```

## Configuration (config.py)

| Setting | Default | Description |
|---------|---------|-------------|
| `BOOTSTRAP_SERVERS` | `localhost:9092` | Kafka broker |
| `TOPIC_RAW` | `listings.raw` | Output topic |
| `MAX_LISTINGS_PER_RUN` | `50` | Max listings per scrape job |
| `PAGES_PER_SOURCE` | `3` | Pagination depth |
| `MIN_DELAY_SECONDS` | `3` | Min delay between requests |
| `MAX_DELAY_SECONDS` | `7` | Max delay between requests |
| `REQUEST_TIMEOUT` | `15` | HTTP timeout (seconds) |
| `MAX_RETRIES` | `3` | Retry attempts for 5xx |
| `BACKOFF_FACTOR` | `2` | Exponential backoff multiplier |
| `SCHEDULE_INTERVAL_HOURS` | `12` | Scheduler interval |

## Message Format

Published to `listings.raw` — matches `listing_consumer.py` expectations:

```json
{
  "vehicle_id": "md5_hash_of_source_url",
  "source": "avito|moteur",
  "event_type": "listing_created",
  "timestamp": "2026-07-10T12:00:00Z",
  "data": {
    "brand": "dacia",
    "model": "duster",
    "year": 2022,
    "price": 185000,
    "mileage": 85000,
    "fuel_type": "diesel",
    "body_type": "suv",
    "transmission": "manuelle",
    "engine_power_hp": null,
    "color": null,
    "doors": null,
    "seats": null,
    "city": "casablanca",
    "description": "",
    "seller_id": ""
  }
}
```

## Testing

Fixtures are **real HTML snapshots** from actual scrapes (anonymized if needed):

```
data-pipeline/tests/fixtures/scraped_html/
├── avito_page1.html    # __NEXT_DATA__ JSON + HTML
└── moteur_page1.html   # Card-based HTML structure
```

Run tests:
```bash
cd data-pipeline
pytest tests/test_kafka_publisher.py -v
pytest tests/test_scraper_normalizer.py -v
```

No tests invent synthetic vehicle data — only fixtures from real scrapes.

## Local Development Database Seeding

For local dev without running scrapers:

```bash
# 1. Generate frozen sample data (run ONCE, then commit)
python -m data_pipeline.scripts.generate_bronze_sample --max 20

# 2. Seed PostgreSQL from versioned sample
python -m data_pipeline.scripts.seed_from_bronze_sample --count 100
```

The sample data in `data-pipeline/storage/sample-data/` is an **immutable snapshot** of real scrapes, versioned in git. Not simulated.

## Extending to New Sources

1. Create `newsite_scraper.py` inheriting `BaseScraper`
2. Implement `fetch_listings(max_items)` returning list of raw dicts
3. Add to `scheduler.py` scrapers list
4. Add fixture HTML to `tests/fixtures/scraped_html/`
5. Add test in `test_kafka_publisher.py`

The normalizer handles schema unification — new scrapers only need to extract:
- Optional: `year`, `mileage`, `fuel_type`, `transmission`, `body_type`, `images_urls`

## Réagir à une alerte de dégradation (Scraper Health)

Si vous recevez une alerte de `health_monitor.py` indiquant une chute du taux de succès (ex: "Degradation detected for moteur. Success rate: 45%"), cela signifie que le site cible a probablement modifié sa structure HTML.

**Procédure de correction manuelle :**
1. **Inspecter le HTML actuel** : Visitez le site cible (ex: Moteur.ma) et utilisez l'inspecteur du navigateur (F12) pour trouver le nouvel élément HTML ou nom de classe pour la donnée manquante (ex: le prix).
2. **Mettre à jour le fichier YAML** : Ouvrez `data_pipeline/kafka/producers/scrapers/selectors/moteur_selectors.yaml`.
3. **Ajouter un fallback** : Ajoutez le nouveau sélecteur CSS dans la liste `fallback_fields` pour le champ concerné, OU remplacez le sélecteur principal dans `fields` s'il est définitivement obsolète.
4. **Mettre à jour la date** : Mettez à jour le champ `version` du YAML.
5. **Valider** : Relancez le scraper en mode local (dry-run) pour vérifier que le nouveau sélecteur extrait correctement la donnée avant de relancer la production.

*Note: Le système de fallback (`extraction_fallback.py`) essaiera automatiquement tous les sélecteurs de la liste.*

## Legal & Ethical

- Academic/demo project only
- Identifiable User-Agent: `VenteAutoBot/1.0 - projet académique`
- Strict rate limits (3-7s)
- Respects robots.txt
- No production use without explicit site permission