import sys, json
sys.path.insert(0, r"D:\Projet automobile\vente-auto-platform\backend")

from app.scraper.avito import AvitoScraper
from app.scraper.moteur import MoteurScraper

print("=== Avito.ma ===")
avito = AvitoScraper()
avito_results = avito.fetch_page("https://www.avito.ma/fr/maroc/voitures_d_occasion/a_vendre", page=1)
print(f"  {len(avito_results)} results")
for r in avito_results[:5]:
    print(f'    {r["brand"]} {r["model"]} - {r["price"]:,.0f} MAD')
avito.close()

print("\n=== Moteur.ma ===")
moteur = MoteurScraper()
moteur_results = moteur.fetch_page("", page=1)
print(f"  {len(moteur_results)} results")
for r in moteur_results[:5]:
    print(f'    {r["brand"]} {r["model"]} - {r["price"]:,.0f} MAD')
moteur.close()

# Save combined
all_results = avito_results + moteur_results
with open(r"D:\Projet automobile\vente-auto-platform\backend\tests\scraped_results.json", "w") as f:
    json.dump(all_results, f, ensure_ascii=False, indent=2)
print(f"\nTotal: {len(all_results)} annonces sauvegardées")
