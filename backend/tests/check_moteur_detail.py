import cloudscraper
from bs4 import BeautifulSoup
import re, json

scraper = cloudscraper.create_scraper()

# Check one detail page
url = "https://www.moteur.ma/fr/voiture/achat-voiture-occasion/detail-annonce/499001/dacia-logan.html"
resp = scraper.get(url, timeout=15)
print(f"Status: {resp.status_code}, Size: {len(resp.text)}")
soup = BeautifulSoup(resp.text, "lxml")

# Look for structured data
for script in soup.find_all("script"):
    stype = script.get("type", "")
    content = script.string or ""
    if "ld+json" in stype or "application/json" in stype:
        try:
            data = json.loads(content)
            print(f"\n=== JSON data ===")
            print(json.dumps(data, ensure_ascii=False, indent=2)[:2000])
        except:
            pass

# Extract by common patterns
print(f"\nTitle: {soup.title.string if soup.title else 'N/A'}")

# Find vehicle specs
specs = {}
for row in soup.find_all(["li", "div", "span"], class_=lambda c: c and "spec" in c.lower()):
    text = row.get_text(" ", strip=True)
    print(f"Spec: {text}")

# Find all text with numbers for price/year/mileage
for pattern in [r"(\d[\d\s]*)\s*(?:DH|MAD|dh|mad)", r"(\d{4})", r"([\d\s]+)\s*km"]:
    matches = re.findall(pattern, resp.text)
    if matches:
        print(f"\n{pattern}: {matches[:5]}")

# Check for price element
price_el = soup.select_one("[class*=price], [class*=prix], [itemprop=price]")
if price_el:
    print(f"\nPrice element: {price_el.get_text(strip=True)[:100]}")

print(f"\nHTML samples:")
# Print elements with car-related classes
for tag in ["h1", "h2", "h3", "div"]:
    for el in soup.find_all(tag, class_=lambda c: c and any(x in (c if isinstance(c,str) else " ".join(c)).lower() for x in ["price", "title", "info", "detail", "spec", "data"])):
        print(f"  {tag}.{'.'.join(el.get('class',[]))}: {el.get_text(strip=True)[:100]}")
