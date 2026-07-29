import json
from bs4 import BeautifulSoup
import re

html = open('moteur.html', 'r', encoding='utf-8').read()
soup = BeautifulSoup(html, 'html.parser')

print("Looking for listings...")

listings = []
for elem in soup.select('.row-item, .listing-card, article.ad-item, .ads-index-card, .row.p-3.mb-3.border, .bg-white.rounded.shadow-sm, [class*="car-box"]'):
    price_elem = elem.select_one('.price, .ad-price, [class*="price"], .text-primary.font-weight-bold')
    title_elem = elem.select_one('.title, .ad-title, h3, h4, [class*="title"]')
    url_elem = elem.select_one('a[href*="/voiture/"], a')
    
    price = price_elem.get_text(strip=True) if price_elem else None
    title = title_elem.get_text(strip=True) if title_elem else None
    url = url_elem['href'] if url_elem and 'href' in url_elem.attrs else None
    
    if title and url:
        listings.append({
            'title': title,
            'price': price,
            'url': url,
            'classes': " ".join(elem.get('class', []))
        })

print(f"Found {len(listings)} potential listings")
for l in listings[:5]:
    print(json.dumps(l, indent=2, ensure_ascii=False))

