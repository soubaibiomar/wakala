import urllib.request
from bs4 import BeautifulSoup

def test():
    url = "https://www.wandaloo.com/neuf/dacia/"
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'})
    try:
        html = urllib.request.urlopen(req).read().decode('utf-8', 'ignore')
        soup = BeautifulSoup(html, 'html.parser')
        
        for li in soup.select('ul.list-models li'):
            a = li.select_one('a')
            if a:
                print(a['href'])
                
        # let's just find any link with /neuf/dacia/ in it that doesn't end with /
        for a in soup.select('a'):
            href = a.get('href', '')
            if href.startswith('https://www.wandaloo.com/neuf/dacia/') and href != 'https://www.wandaloo.com/neuf/dacia/':
                print("Found:", href)
    except Exception as e:
        print(f"Error: {e}")

test()
