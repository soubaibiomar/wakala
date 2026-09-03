"""
═══════════════════════════════════════════════════════════════
Wakala Scraper Pipeline — Orchestrateur Multi-Plateformes
═══════════════════════════════════════════════════════════════

Exécute séquentiellement les scrapers actifs,
déduplique inter-plateformes, et écrit les résultats.

Usage:
    python main.py                         # Run all scrapers once
    python main.py --site moteur           # Run only Moteur.ma
    python main.py --schedule --interval 10  # Run every 10 minutes
    python main.py --max-pages 3           # Scrape 3 pages per platform
"""
import argparse
import logging
import sys
import time
import traceback

from core.health_monitor import ScraperHealthMonitor
from storage.image_downloader import ImageDownloader
from storage.writer import DataWriter

# ── Import all platform scrapers ──────────────────────────────
from marketplaces.avito_scraper import AvitoScraper
from marketplaces.moteur_scraper import MoteurScraper
from marketplaces.wandaloo_scraper import WandalooScraper
from marketplaces.otoclic_scraper import OtoclicScraper
from marketplaces.spoticar_scraper import SpoticarScraper
from marketplaces.kifal_scraper import KifalScraper
from marketplaces.global_occaz_scraper import GlobalOccazScraper

# ── Import services ──────────────────────────────────────────
from services.deduplication import deduplicate_listings

try:
    from concessionaires.dacia_scraper import DaciaScraper
    HAS_DACIA = True
except ImportError:
    HAS_DACIA = False

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("ScraperMain")


# ── Registry of all available scrapers ────────────────────────
SCRAPER_REGISTRY = {
    # Occasion (particuliers + pros)
    "avito": AvitoScraper,
    "moteur": MoteurScraper,
    "wandaloo": WandalooScraper,
    "otoclic": OtoclicScraper,

    # Occasion certifiée
    "spoticar": SpoticarScraper,
    "kifal_auto": KifalScraper,

    # Occasion (site hors ligne)
    "global_occaz": GlobalOccazScraper,
}

if HAS_DACIA:
    SCRAPER_REGISTRY["dacia"] = DaciaScraper


def run_scraper(scraper_class, max_pages: int, writer: DataWriter,
                downloader: ImageDownloader, monitor: ScraperHealthMonitor):
    """
    Execute a single scraper in isolation.
    Returns list of raw listings (dicts).
    """
    scraper = scraper_class()
    site_name = scraper.platform_name
    logger.info(f"{'='*60}")
    logger.info(f"--- [{site_name.upper()}] Starting scraper ---")
    logger.info(f"    Type: {scraper.listing_type} | Certified: {scraper.is_certified}")
    logger.info(f"{'='*60}")

    try:
        raw_listings = scraper.run(max_pages=max_pages)

        # Convert RawListing objects to dicts for downstream processing
        raw_dicts = []
        for raw in raw_listings:
            if hasattr(raw, "model_dump"):
                raw_dicts.append(raw.model_dump())
            elif isinstance(raw, dict):
                raw_dicts.append(raw)

        # Write raw output to JSONL
        if raw_listings:
            writer.write_jsonl(f"{site_name}_raw.jsonl", raw_listings)

        # Health check
        monitor.evaluate_run(site_name, raw_listings)

        scraped = len(raw_dicts)
        neuf = sum(1 for r in raw_dicts if r.get("type_annonce") == "neuf")
        occasion = scraped - neuf
        logger.info(
            f"--- [{site_name.upper()}] Completed: {scraped} total "
            f"({neuf} neuf, {occasion} occasion) ---"
        )

        return raw_dicts

    except Exception as e:
        logger.error(f"--- [{site_name.upper()}] FATAL CRASH ---")
        logger.error(traceback.format_exc())
        monitor._log_health_issue(
            site=site_name,
            issue="Unhandled exception during scraper run",
            details={"error": str(e), "traceback": traceback.format_exc()}
        )
        return []


def main():
    parser = argparse.ArgumentParser(description="Wakala Multi-Platform Scraper Pipeline")
    parser.add_argument("--site", type=str, default="all",
                        help="Specific site to scrape (e.g. moteur, avito). 'all' for all.")
    parser.add_argument("--max-pages", type=int, default=2,
                        help="Max pages to scrape per platform.")
    parser.add_argument("--schedule", action="store_true",
                        help="Run continuously in a loop.")
    parser.add_argument("--interval", type=int, default=10,
                        help="Interval in minutes between runs (if --schedule).")
    parser.add_argument("--skip-dedup", action="store_true",
                        help="Skip cross-platform deduplication.")

    args = parser.parse_args()

    writer = DataWriter()
    downloader = ImageDownloader()
    monitor = ScraperHealthMonitor()

    # Determine which scrapers to run
    if args.site == "all":
        sites_to_run = list(SCRAPER_REGISTRY.keys())
    else:
        sites_to_run = [s.strip() for s in args.site.split(",")]

    def run_cycle():
        all_raw = []

        logger.info(f"{'#'*60}")
        logger.info(f"# WAKALA SCRAPING CYCLE — {len(sites_to_run)} platforms")
        logger.info(f"# Platforms: {', '.join(sites_to_run)}")
        logger.info(f"{'#'*60}")

        # ── Phase 1: Sequential scraping ──────────────────────
        for site in sites_to_run:
            if site not in SCRAPER_REGISTRY:
                logger.warning(f"Scraper '{site}' not found in registry. Skipping.")
                continue

            raw = run_scraper(
                SCRAPER_REGISTRY[site], args.max_pages,
                writer, downloader, monitor
            )
            all_raw.extend(raw)

        # ── Phase 2: Cross-platform deduplication ─────────────
        if not args.skip_dedup and all_raw:
            logger.info(f"\n--- DEDUPLICATION ({len(all_raw)} listings) ---")
            all_raw = deduplicate_listings(all_raw)

        # ── Phase 3: Summary ─────────────────────────────────
        logger.info(f"\n{'='*60}")
        logger.info(f"PIPELINE SUMMARY")
        logger.info(f"{'='*60}")

        # Per-platform stats
        platform_counts = {}
        for item in all_raw:
            src = item.get("source_plateforme", "unknown")
            if src not in platform_counts:
                platform_counts[src] = {"neuf": 0, "occasion": 0}
            t = item.get("type_annonce", "occasion")
            platform_counts[src][t] = platform_counts[src].get(t, 0) + 1

        for src, counts in sorted(platform_counts.items()):
            total = counts["neuf"] + counts["occasion"]
            logger.info(f"  [{src:>15}] {total:>4} listings ({counts['neuf']} neuf, {counts['occasion']} occasion)")

        multi = sum(1 for r in all_raw if len(r.get("sources_multiples", [])) > 1)
        certified = sum(1 for r in all_raw if r.get("certifie", False))
        logger.info(f"  {'─'*40}")
        logger.info(f"  Total unique: {len(all_raw)}")
        logger.info(f"  Multi-source: {multi}")
        logger.info(f"  Certifiées:   {certified}")
        logger.info(f"{'='*60}")

        return all_raw

    if args.schedule:
        logger.info(f"Starting scheduled scraping. Interval: {args.interval} minutes.")
        while True:
            logger.info("Starting a new scraping cycle...")
            run_cycle()
            logger.info(f"Scraping cycle completed. Sleeping for {args.interval} minutes.")
            time.sleep(args.interval * 60)
    else:
        run_cycle()


if __name__ == "__main__":
    main()
