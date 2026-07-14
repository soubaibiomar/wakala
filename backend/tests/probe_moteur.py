import cloudscraper, re, json
from bs4 import BeautifulSoup

scraper = cloudscraper.create_scraper()
resp = scraper.get("https://www.moteur.ma/fr/voiture/achat-voiture-occasion/", timeout=15)
soup = BeautifulSoup(resp.text, "lxml")

# Save HTML for debugging
with open(r"D:\Projet automobile\vente-auto-platform\backend\tests\moteur_debug.html", "w", encoding="utf-8") as f:
    f.write(resp.text)

# Find structured data
for script in soup.find_all("script"):
    stype = script.get("type", "")
    content = script.string or ""
    if "ld+json" in stype or "application/json" in stype:
        print(f"Script type={stype}: {content[:500]}")
    elif content and any(x in content for x in ["__NEXT_DATA__", "__NUXT__", "window.__"]):
        print(f"Script with SPA data: {content[:500]}")

# Find listing links with vehicle details
links = set()
for a in soup.find_all("a", href=True):
    h = a["href"]
    if re.search(r"/fr/voiture/achat-voiture-occasion/\d+/", h):
        links.add(h)
print(f"\nDetail links: {len(links)}")
for l in sorted(links)[:5]:
    print(f"  {l}")

# Check for JSON in script tags
scripts = soup.find_all("script", type="application/json")
print(f"\nJSON scripts: {len(scripts)}")
for s in scripts[:3]:
    print(f"  Content: {s.string[:300] if s.string else 'empty'}")

# Look for data-attributes with vehicle info
for tag in soup.find_all(attrs={"data-vehicle-id": True}):
    print(f"\nVehicle data: {tag.attrs}")

# Extract all data-* attributes from divs
data_divs = soup.find_all("div", attrs={"data-*": True})
print(f"\nData divs: {len(data_divs)}")
