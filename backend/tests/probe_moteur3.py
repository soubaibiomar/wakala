from bs4 import BeautifulSoup
import re

with open(r"D:\Projet automobile\vente-auto-platform\backend\tests\moteur_debug.html", encoding="utf-8") as f:
    html = f.read()

soup = BeautifulSoup(html, "lxml")

# Find all detail links
detail_links = set()
for a in soup.find_all("a", href=True):
    h = a["href"]
    if "/detail-annonce/" in h:
        detail_links.add(h)

print(f"Detail links: {len(detail_links)}")
for l in sorted(detail_links)[:5]:
    print(f"  {l}")

# Find the listing container
for a in soup.find_all("a", href=True):
    h = a["href"]
    if "/detail-annonce/" in h:
        # Navigate up to find the card container
        parent = a
        for i in range(5):
            parent = parent.parent
            if parent:
                classes = parent.get("class", [])
                if classes:
                    cstr = " ".join(classes) if isinstance(classes, list) else classes
                    print(f"\n  Level {i}: class={cstr}, tag={parent.name}")
                    # Check if this looks like a card container
                    if any(x in str(parent.get("class", [])).lower() for x in ["card", "item", "list", "result"]):
                        print(f"  => CONTAINER FOUND!")
                        break
        break

# Find listing container by looking at a detail link's ancestors
first_link = list(detail_links)[0] if detail_links else None
if first_link:
    a = soup.find("a", href=first_link)
    if a:
        # Go up to find the listing card
        current = a
        for i in range(8):
            current = current.parent
            if current:
                c = current.get("class", [])
                print(f"  {current.name} {c}")

# Search for sections with multiple children that contain links
sections = soup.find_all(["div", "section"], recursive=True)
for sec in sections:
    links_in_sec = sec.find_all("a", href=lambda h: h and "/detail-annonce/" in h)
    if len(links_in_sec) >= 3:
        print(f"\nContainer with {len(links_in_sec)} detail links:")
        print(f"  Tag: {sec.name}")
        print(f"  Classes: {sec.get('class')}")
        print(f"  ID: {sec.get('id')}")
        print(f"  HTML[:500]: {str(sec)[:500]}")
        break
