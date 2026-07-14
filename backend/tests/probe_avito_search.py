import cloudscraper
from bs4 import BeautifulSoup
import json

scraper = cloudscraper.create_scraper()

url = "https://www.avito.ma/fr/maroc/voitures_d_occasion-a_vendre"
resp = scraper.get(url, timeout=30)
print(f"Status: {resp.status_code}, URL: {resp.url}, Size: {len(resp.text)}")

soup = BeautifulSoup(resp.text, "lxml")

# Find listing links
links = set()
for a in soup.find_all("a", href=True):
    h = a["href"]
    if "/fr/annonce/" in h.lower() or "/item/" in h.lower():
        links.add(h)

print(f"\nListing links: {len(links)}")
for l in sorted(links)[:5]:
    print(f"  {l}")

# Check for JSON data blocks
for script in soup.find_all("script"):
    if script.string and any(x in script.string for x in ["window.__", "__NUXT__", "__NEXT_DATA__", "application/ld"]):
        print(f"\nScript data found: {script.string[:200]}")

# Try to find car listing JSON
for div in soup.find_all("div", class_=lambda c: c and "listing" in c.lower()):
    print(f"\nListing div: {div.get('class')}")

# Save the HTML for debugging
with open(r"D:\Projet automobile\vente-auto-platform\backend\tests\avito_debug.html", "w", encoding="utf-8") as f:
    f.write(resp.text)
print("\nHTML saved to avito_debug.html")
