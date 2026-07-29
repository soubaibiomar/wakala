import urllib.request
from bs4 import BeautifulSoup

def test():
    url = "https://www.wandaloo.com/neuf/dacia/duster/"
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    try:
        html = urllib.request.urlopen(req).read().decode('utf-8', 'ignore')
        print(html[:2000])
        soup = BeautifulSoup(html, 'html.parser')
        
        # let's just print all img tags
        for img in soup.find_all('img'):
            print(img.get('src'))
    except Exception as e:
        print(f"Error: {e}")

test()
