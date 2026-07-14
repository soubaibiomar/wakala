import cloudscraper
from bs4 import BeautifulSoup

scraper = cloudscraper.create_scraper()

resp = scraper.get("https://www.avito.ma/", timeout=15)
print(f"Status: {resp.status_code}, URL: {resp.url}, Size: {len(resp.text)}")

soup = BeautifulSoup(resp.text, "lxml")

links = []
for a in soup.find_all("a", href=True):
    links.append((a.get_text(strip=True)[:50], a["href"]))

print(f"\nLinks found: {len(links)}")
for txt, href in links[:30]:
    print(f"  {txt[:40]:40s} -> {href}")

for meta in soup.find_all("meta"):
    if meta.get("http-equiv", "").lower() == "refresh":
        print(f"\nMeta refresh: {meta.get('content')}")
