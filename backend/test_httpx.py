import asyncio
import httpx
from bs4 import BeautifulSoup

async def f():
    async with httpx.AsyncClient(headers={'User-Agent': 'Mozilla/5.0'}) as c:
        r = await c.get('https://www.wandaloo.com/occasion/?page=1')
        s = BeautifulSoup(r.text, 'html.parser')
        l = [a['href'] for a in s.select('a') if 'href' in a.attrs and '/occasion/' in a['href'] and '.html' in a['href']]
        print(l)

asyncio.run(f())
