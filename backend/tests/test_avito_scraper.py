from app.scraper.avito import AvitoScraper
import json

scraper = AvitoScraper()
results = scraper.fetch_page("https://www.avito.ma/fr/maroc/voitures_d_occasion/a_vendre", page=1)
print(f"Résultats: {len(results)}")
for r in results[:5]:
    print(f'  {r["brand"]} {r["model"]} ({r["year"]}) - {r["price"]:,.0f} MAD - {r["city"]}')
    print(f'    fuel={r["fuel_type"]}, trans={r["transmission"]}, km={r["mileage"]}')

if results:
    with open(r"D:\Projet automobile\vente-auto-platform\backend\tests\avito_results.json", "w") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f"\nSauvegardé: {len(results)} annonces")
scraper.close()
