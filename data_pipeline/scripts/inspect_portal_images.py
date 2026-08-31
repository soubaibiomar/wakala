import urllib.request
from bs4 import BeautifulSoup
import sys

sys.stdout.reconfigure(encoding='utf-8')
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}

def inspect_page(url):
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=10) as resp:
        html = resp.read().decode('utf-8', errors='ignore')
        soup = BeautifulSoup(html, 'html.parser')
        print(f"=== Images on {url} ===")
        for img in soup.find_all('img'):
            src = img.get('src') or ''
            data_src = img.get('data-src') or ''
            alt = img.get('alt') or ''
            if 'logo' not in src.lower() and 'icone' not in src.lower():
                print(f"  Alt: '{alt}' | src: {src} | data-src: {data_src}")

if __name__ == '__main__':
    inspect_page('https://www.wandaloo.com/neuf/dacia/')
    inspect_page('https://www.moteur.ma/fr/neuf/fiche-technique-prix/dacia/')
