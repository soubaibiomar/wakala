from bs4 import BeautifulSoup

with open(r"D:\Projet automobile\vente-auto-platform\backend\tests\moteur_debug.html", encoding="utf-8") as f:
    html = f.read()

soup = BeautifulSoup(html, "lxml")

# Find all listing cards
cards = soup.find_all("div", class_=lambda c: c and "ads-index-card" in (c if isinstance(c, str) else " ".join(c)))
print(f"Cards found: {len(cards)}")
print()
for card in cards[:3]:
    # Get brand/model from the detail link
    a = card.find("a", href=lambda h: h and "/detail-annonce/" in h)
    title = a.get_text(strip=True) if a else "N/A"
    href = a["href"] if a else "N/A"
    
    # Get price
    price_el = card.select_one("[class*=price], [class*=prix]")
    price = price_el.get_text(strip=True) if price_el else "N/A"
    
    # Get all text content
    text = card.get_text(" ", strip=True)
    
    print(f"Title: {title}")
    print(f"Href: {href}")
    print(f"Price: {price}")
    print(f"Full text: {text[:300]}")
    print()
