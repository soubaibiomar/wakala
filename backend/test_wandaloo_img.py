import urllib.request
from bs4 import BeautifulSoup

def test():
    url = "https://www.wandaloo.com/neuf/dacia/duster/"
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    try:
        html = urllib.request.urlopen(req).read().decode('utf-8', 'ignore')
        soup = BeautifulSoup(html, 'html.parser')
        
        for img in soup.select('.visuel img'):
            print("VISUEL IMG:", img.get('src'))
            
        for img in soup.select('#img-prin'):
            print("IMG PRIN:", img.get('src'))
            
        # maybe it's in a slider
        for img in soup.select('.slider img'):
            print("SLIDER IMG:", img.get('src'))
            
        for img in soup.select('div[class*="img"] img'):
            print("DIV IMG:", img.get('src'))

    except Exception as e:
        print(f"Error: {e}")

test()
