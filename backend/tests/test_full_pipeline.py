import asyncio, sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.scraper.avito import AvitoScraper
from app.scraper.db_writer import save_vehicles
from app.core.database import async_session_factory


async def main():
    print("=== Scraping Avito (1 page) ===")
    scraper = AvitoScraper()
    results = scraper.fetch_page("https://www.avito.ma/fr/maroc/voitures_d_occasion/a_vendre", page=1)
    scraper.close()
    print(f"  {len(results)} annonces trouvées")
    for r in results[:5]:
        print(f'    {r["brand"]} {r["model"]} - {r["price"]:,.0f} MAD - {r["city"]}')

    if results:
        print("\n=== Sauvegarde en base ===")
        async with async_session_factory() as session:
            count = await save_vehicles(session, results)
            await session.commit()
            print(f"  {count} annonces insérées dans PostgreSQL")

    # Verify via API (backend must be running)
    import httpx
    try:
        resp = httpx.get("http://localhost:8000/api/vehicles/")
        data = resp.json()
        print(f"\n=== API vérification ===")
        print(f"  Total véhicules en base: {data['total']}")
        for v in data["items"][:5]:
            print(f'    {v["brand"]} {v["model"]} - {v["price"]:,.0f} MAD')
    except Exception as e:
        print(f"\nAPI non disponible: {e}")

asyncio.run(main())
