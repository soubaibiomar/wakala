"""
CLI — Lancement du scraper / générateur de données.

Usage:
    python -m app.scraper.cli scrape --pages 2 --db
    python -m app.scraper.cli scrape --source avito --pages 3 --db
    python -m app.scraper.cli scrape --source moteur --pages 1 --output results.json
"""
import argparse
import asyncio
import json
import logging
import sys

logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)


async def _main():
    parser = argparse.ArgumentParser(description="Wakala Scraper & Data Generator")
    sub = parser.add_subparsers(dest="command")

    scrap = sub.add_parser("scrape", help="Scraper les sites d'annonces")
    scrap.add_argument("--source", default=None,
                       choices=["avito", "moteur"],
                       help="Source specifique (defaut: toutes)")
    scrap.add_argument("--pages", type=int, default=1, help="Pages par source")
    scrap.add_argument("--db", action="store_true", help="Sauvegarder en base")
    scrap.add_argument("--output", type=str, help="Fichier JSON de sortie")

    args = parser.parse_args()

    if args.command == "scrape":
        from app.scraper.engine import run_all

        sources = [args.source] if args.source else None
        results = await run_all(pages=args.pages, sources=sources)

        total = sum(len(v) for v in results.values())
        print(f"\nRésultat: {total} annonces récupérées")
        for name, listings in results.items():
            print(f"  {name}: {len(listings)} annonces")

        if args.db and total > 0:
            from app.core.database import async_session_factory
            from app.scraper.db_writer import save_vehicles

            async with async_session_factory() as session:
                for name, listings in results.items():
                    inserted = await save_vehicles(session, listings)
                    await session.commit()
                    print(f"  {name}: {inserted} insérées en base")

        if args.output:
            with open(args.output, "w", encoding="utf-8") as f:
                json.dump(results, f, ensure_ascii=False, indent=2)
            print(f"Sauvegardé: {args.output}")
    else:
        parser.print_help()
        sys.exit(1)

    sys.exit(0)


def main():
    asyncio.run(_main())


if __name__ == "__main__":
    main()
