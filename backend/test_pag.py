import asyncio
import httpx
from bs4 import BeautifulSoup
import re

async def main():
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36'}
    async with httpx.AsyncClient(headers=headers) as client:
        # WANDALOO
        r1 = await client.get('https://www.wandaloo.com/occasion/?page=1', timeout=15)
        s1 = BeautifulSoup(r1.text, 'html.parser')
        ul1 = s1.select_one('ul.pagination')
        last_page_w = 1
        if ul1:
            pages = [a.text.strip() for a in ul1.select('a') if a.text.strip().isdigit()]
            if pages:
                last_page_w = int(pages[-1])
            last_link = ul1.find('a', string=re.compile(r'Fin|Derni', re.I))
            if last_link and 'page=' in last_link.get('href', ''):
                match = re.search(r'page=(\d+)', last_link['href'])
                if match:
                    last_page_w = int(match.group(1))
        print("Wandaloo max page found:", last_page_w)
        
        # MOTEUR
        r2 = await client.get('https://www.moteur.ma/fr/voiture/achat-voiture-occasion/recherche/?page=1', timeout=15)
        s2 = BeautifulSoup(r2.text, 'html.parser')
        # Dump Moteur text to find total count if pagination is tricky
        count_text = s2.find(string=re.compile(r'annonces trouv'))
        print("Moteur count text:", count_text.strip() if count_text else "None")
        
        # AVITO
        r3 = await client.get('https://www.avito.ma/fr/maroc/voitures_d_occasion?o=1', timeout=15)
        s3 = BeautifulSoup(r3.text, 'html.parser')
        a_links = s3.select('a')
        avito_pages = [int(a.text) for a in a_links if a.text.isdigit() and len(a.text) < 4]
        print("Avito max page found:", max(avito_pages) if avito_pages else 1)
        
asyncio.run(main())
