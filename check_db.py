import asyncio
import asyncpg

async def main():
    conn = await asyncpg.connect('postgresql://postgres:postgres@localhost:5432/ventes_auto')
    rows = await conn.fetch("SELECT brand, model, mileage, source_url FROM vehicles WHERE brand ILIKE '%Changan%'")
    for r in rows:
        print(dict(r))
    await conn.close()

asyncio.run(main())
