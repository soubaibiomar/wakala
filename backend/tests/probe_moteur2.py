from bs4 import BeautifulSoup
import re

with open(r"D:\Projet automobile\vente-auto-platform\backend\tests\moteur_debug.html", encoding="utf-8") as f:
    html = f.read()

soup = BeautifulSoup(html, "lxml")

# Find all <a> tags and check their href patterns
links = {}
for a in soup.find_all("a", href=True):
    h = a["href"]
    if h.startswith("/fr/") and len(h) > 20:
        key = h.split("/")[3] if len(h.split("/")) > 3 else "other"
        links[key] = links.get(key, 0) + 1

print("Link categories:")
for k, v in sorted(links.items(), key=lambda x: -x[1])[:30]:
    print(f"  {k}: {v}")

# Find vehicle detail page links
# Typical pattern: /fr/voiture/achat-voiture-occasion/<id>/<slug>.html
for a in soup.find_all("a", href=True):
    h = a["href"]
    if ".html" in h and "/voiture/" in h:
        print(f"\nDetail link: {h}")
        parent = a.parent
        if parent:
            print(f"  Parent class: {parent.get('class')}")
            print(f"  Parent text: {parent.get_text(strip=True)[:100]}")
        break

# Find all elements with classes that might be vehicle cards
for tag in ["div", "article", "section", "li"]:
    items = soup.find_all(tag, class_=True)
    card_candidates = []
    for item in items:
        classes = " ".join(item.get("class", [])) if isinstance(item.get("class"), list) else item.get("class", "")
        if any(x in classes.lower() for x in ["card", "item", "vehicle", "annonce", "listing", "result"]):
            card_candidates.append(item)
    if card_candidates:
        print(f"\n{tag} with card class: {len(card_candidates)}")
        sample = card_candidates[0]
        print(f"  Sample class: {sample.get('class')}")
        print(f"  Sample HTML[:300]: {str(sample)[:300]}")

# Check for common vehicle data containers
print("\n--- Looking for price patterns ---")
prices = re.findall(r"(\d[\d\s]*)\s*(?:DH|MAD|dh|mad)", html)
print(f"Prices found: {len(prices)}")
if prices:
    print(f"  First 5: {prices[:5]}")
