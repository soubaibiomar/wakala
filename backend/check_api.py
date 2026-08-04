import asyncio
import httpx
async def check():
    async with httpx.AsyncClient() as client:
        res = await client.get('http://localhost:8000/api/vehicles?brand=citroen&condition=neuf&group_by_model=true')
        data = res.json()
        print(f"Total: {data.get('total')}")
        items = data.get('items', [])
        print(f"Items count: {len(items)}")

asyncio.run(check())
