import asyncio
import json
from app.core.database import async_session_factory
from sqlalchemy import text

async def clean():
    async with async_session_factory() as db:
        res = await db.execute(text("SELECT l.id, l.images_urls FROM listings l JOIN vehicles v ON l.vehicle_id = v.id WHERE v.source_url LIKE '%kifal%'"))
        updated = 0
        for row in res:
            l_id = row[0]
            images = row[1]
            if not images:
                continue
                
            clean_images = []
            for url in images:
                lower_url = url.lower()
                if (
                    "ma.svg" in lower_url 
                    or "logo" in lower_url 
                    or "brands" in lower_url 
                    or "users" in lower_url 
                    or "google.png" in lower_url
                    or ".svg" in lower_url
                ):
                    continue
                clean_images.append(url)
                
            if len(clean_images) != len(images):
                # We need to update this row
                # Parameterized query to avoid SQL injection / formatting issues
                await db.execute(
                    text("UPDATE listings SET images_urls = :imgs WHERE id = :id"),
                    {"imgs": clean_images, "id": l_id}
                )
                updated += 1
                
        if updated > 0:
            await db.commit()
            print(f"Successfully cleaned images for {updated} Kifal listings.")
        else:
            print("No listings needed cleaning.")

asyncio.run(clean())
