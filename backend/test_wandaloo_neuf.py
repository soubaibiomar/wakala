import urllib.request
from bs4 import BeautifulSoup

def test():
    url = "https://www.wandaloo.com/neuf/"
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'})
    try:
        html = urllib.request.urlopen(req).read().decode('utf-8', 'ignore')
        soup = BeautifulSoup(html, 'html.parser')
        links = soup.find_all('a', href=True)
        brands = set()
        for a in links:
            if '/neuf/' in a['href'] and a['href'] != '/neuf/':
                brands.add(a['href'])
        print(f"Found {len(brands)} brand links in Neuf.")
        for b in list(brands)[:5]:
            print(" -", b)
    except Exception as e:
        print(f"Error: {e}")

test()
