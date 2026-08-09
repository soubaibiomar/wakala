import asyncio
import os
import aiohttp
from urllib.parse import urlparse
from sqlalchemy import text
from app.core.database import async_session_factory

UPLOAD_DIR = "/app/uploads/scraped"
os.makedirs(UPLOAD_DIR, exist_ok=True)

async def download_image(session, url: str) -> str:
    if not url.startswith("http"):
        return url
    if url.startswith("http://localhost") or "/uploads/" in url:
        return url
        
    try:
        async with session.get(url, timeout=10) as response:
            if response.status == 200:
                filename = os.path.basename(urlparse(url).path)
                if not filename:
                    filename = "image.jpg"
                
                import uuid
                base, ext = os.path.splitext(filename)
                unique_filename = f"{base}_{uuid.uuid4().hex[:8]}{ext}"
                filepath = os.path.join(UPLOAD_DIR, unique_filename)
                
                with open(filepath, "wb") as f:
                    f.write(await response.read())
                return f"http://localhost:8000/uploads/scraped/{unique_filename}"
    except Exception as e:
        print(f"Failed to download {url}: {e}")
    return url

async def main():
    async with aiohttp.ClientSession() as session:
        async with async_session_factory() as db:
            result = await db.execute(text("SELECT id, images_urls FROM listings WHERE array_length(images_urls, 1) > 0;"))
            listings = result.fetchall()
            
            print(f"Found {len(listings)} listings to process")
            updated = 0
            
            for row in listings:
                l_id, urls = row[0], row[1]
                new_urls = []
                changed = False
                for url in urls:
                    if url.startswith("http") and not url.startswith("http://localhost") and "unsplash.com" not in url:
                        print(f"Downloading {url}...")
                        new_url = await download_image(session, url)
                        new_urls.append(new_url)
                        if new_url != url:
                            changed = True
                    else:
                        new_urls.append(url)
                
                if changed:
                    await db.execute(
                        text("UPDATE listings SET images_urls = :new_urls WHERE id = :l_id"),
                        {"new_urls": new_urls, "l_id": l_id}
                    )
                    await db.commit()
                    updated += 1
                    
            print(f"Updated {updated} listings successfully.")

if __name__ == "__main__":
    asyncio.run(main())
