import urllib.request
import re
from bs4 import BeautifulSoup
import sys

sys.stdout.reconfigure(encoding='utf-8')
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}

def test_brand(brand_slug):
    url = f'https://www.wandaloo.com/neuf/{brand_slug}/'
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=10) as resp:
            html = resp.read().decode('utf-8', errors='ignore')
            soup = BeautifulSoup(html, 'html.parser')
            print(f'=== Models on Wandaloo for {brand_slug} ===')
            for a in soup.find_all('a', href=re.compile(rf'/neuf/{brand_slug}/')):
                img = a.find('img')
                if img and img.get('src') and ('pic' in img.get('src') or 'photo' in img.get('src') or 'upload' in img.get('src') or 'img' in img.get('src')):
                    title = a.find(['h2', 'h3', 'p', 'span']) or a
                    print(f'{title.get_text(strip=True)[:40]} -> {img.get("src")}')
    except Exception as e:
        print(f'Error for {brand_slug}: {e}')

if __name__ == '__main__':
    for b in ['dacia', 'renault', 'hyundai', 'peugeot', 'volkswagen', 'toyota']:
        test_brand(b)
