import urllib.request
import re
from bs4 import BeautifulSoup
import sys

sys.stdout.reconfigure(encoding='utf-8')
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}

def find_moteur_brands():
    url = 'https://www.moteur.ma/fr/neuf/'
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=10) as resp:
        html = resp.read().decode('utf-8', errors='ignore')
        soup = BeautifulSoup(html, 'html.parser')
        links = soup.find_all('a', href=re.compile(r'/neuf/'))
        print(f"Total /neuf/ links: {len(links)}")
        brand_links = set()
        for a in links:
            href = a.get('href', '')
            if 'fiche-technique-prix' in href:
                brand_links.add(href)
        print(f"Found {len(brand_links)} brand links:")
        for bl in sorted(brand_links)[:20]:
            print("  ", bl)

if __name__ == '__main__':
    find_moteur_brands()
