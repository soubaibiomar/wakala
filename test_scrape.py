import urllib.request
from bs4 import BeautifulSoup
import re

BRANDS = ["changan", "dacia"]

def fetch_html(url):
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    try:
        return urllib.request.urlopen(req).read().decode('utf-8', 'ignore')
    except Exception as e:
        print(f"Error fetching {url}: {e}")
        return ""

for brand in BRANDS:
    print(f"Fetching {brand}...")
    html = fetch_html(f"https://www.wandaloo.com/neuf/{brand}/")
    if not html: continue
    soup = BeautifulSoup(html, 'html.parser')
    
    models_data = {}
    for a in soup.select('a'):
        href = a.get('href', '')
        if href.startswith(f'https://www.wandaloo.com/neuf/{brand}/') and href != f'https://www.wandaloo.com/neuf/{brand}/':
            model_name = href.split('/')[-2].capitalize()
            if model_name not in models_data:
                parent = a.find_parent('li') or a.find_parent('div')
                if parent:
                    img = parent.select_one('img')
                    img_src = img.get('src') if img else None
                    text = parent.text.strip().replace('\n', ' ')
                    models_data[model_name] = {'url': href, 'img': img_src, 'text': text}

    for model_name, data in models_data.items():
        prices = [int(p.replace('.', '')) for p in re.findall(r'(\d{2,3}\.\d{3})', data['text'])]
        versions_match = re.search(r'(\d+)\s+versions?', data['text'])
        versions = int(versions_match.group(1)) if versions_match else 1
        
        min_price = min(prices) if prices else 200000
        max_price = max(prices) if prices else min_price
        
        for v in range(versions):
            if versions > 1:
                price = min_price + (max_price - min_price) * (v / (versions - 1))
            else:
                price = min_price
                
            print(f"Added {brand.capitalize()} {model_name} v{v+1} ({int(price)} MAD) - {data['img']}")
