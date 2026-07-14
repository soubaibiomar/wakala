from bs4 import BeautifulSoup
import re

with open(r"D:\Projet automobile\vente-auto-platform\backend\tests\avito_debug.html", encoding="utf-8") as f:
    html = f.read()

soup = BeautifulSoup(html, "lxml")

# Find all listing containers by common classes
for cls in ["sc-", "listing", "card", "item", "ad", "annonce"]:
    divs = soup.find_all("div", class_=lambda c: c and cls in " ".join(c) if isinstance(c, list) else (c and cls in c))
    if divs:
        print(f"Class containing '{cls}': {len(divs)} items")
        if divs:
            first = divs[0]
            print(f"  Example: class={first.get('class')}, tag={first.name}")
            print(f"  Content starts: {str(first)[:300]}")

# Try to find the listing grid
print("\n--- Looking for structured data ---")
# Search for price patterns (MAD prices)
prices = re.findall(r'(\d[\d\s]*\.?\d*)\s*(?:DH|MAD|د\.م\.)', html)
print(f"Price patterns found: {len(prices)}")

# Look for __NEXT_DATA__ or __NUXT__
for marker in ["__NEXT_DATA__", "__NUXT__", "window.__INITIAL_STATE__"]:
    if marker in html:
        idx = html.index(marker)
        print(f"\nFound {marker} at position {idx}")
        # Extract the data
        end = html.find("</script>", idx)
        data = html[idx + len(marker) + 2:end-1]  # Remove type="...">
        print(f"  Size: {len(data)} chars")
        try:
            import json
            parsed = json.loads(data)
            if isinstance(parsed, dict):
                print(f"  Keys: {list(parsed.keys())[:10]}")
        except:
            print(f"  First 200 chars: {data[:200]}")

# Try to find ad/article containers
for tag in ["article", "section"]:
    items = soup.find_all(tag)
    if items:
        print(f"\n<{tag}> elements: {len(items)}")
        for item in items[:5]:
            print(f"  class={item.get('class')}, id={item.get('id')}")

# First 100 div classes
classes = set()
for div in soup.find_all("div", class_=True):
    c = div.get("class")
    if c:
        classes.add(" ".join(c) if isinstance(c, list) else c)
print(f"\nUnique div classes: {len(classes)}")
for c in sorted(classes)[:30]:
    print(f"  {c}")
