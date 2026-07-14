import sys, json
sys.path.insert(0, r"D:\Projet automobile\vente-auto-platform\backend")
from app.scraper.avito import AvitoScraper

scraper = AvitoScraper()
results = scraper.fetch_page("https://www.avito.ma/fr/maroc/voitures_d_occasion/a_vendre", page=1)
print(f"Résultats: {len(results)}")
for r in results[:10]:
    print(f'  {r["brand"]} {r["model"]} ({r["year"]}) - {r["price"]:,.0f} MAD - {r["city"]}')
    print(f'    fuel={r["fuel_type"]}, trans={r["transmission"]}, km={r["mileage"]}')

if results:
    print(f"\nMarques trouvées: {set(r['brand'] for r in results)}")
scraper.close()
