import asyncio
import json
from sqlalchemy import text
from app.core.database import async_session_factory

async def update_database():
    with open('/app/curated_studio_images.json', 'r', encoding='utf-8') as f:
        curated = json.load(f)

    with open('/app/scraped_moteur_images.json', 'r', encoding='utf-8') as f:
        scraped = json.load(f)

    async with async_session_factory() as session:
        # 1. Update from curated
        updated_count = 0
        for key, img_url in curated.items():
            brand_name, model_name = key.split('|', 1)
            await session.execute(text("""
                UPDATE car_models
                SET hero_image_url = :img_url
                WHERE brand_id IN (SELECT id FROM car_brands WHERE name ILIKE :brand_name)
                AND (name ILIKE :model_name OR :model_name ILIKE ('%' || name || '%'))
            """), {"img_url": img_url, "brand_name": brand_name, "model_name": model_name})
            updated_count += 1

        # 2. Update from scraped for any remaining
        for brand_name, models_dict in scraped.items():
            for mod_name, img_url in models_dict.items():
                if img_url and 'storage/media/images/models/' in img_url:
                    clean_mod = mod_name.lower().replace(brand_name.lower(), '').strip()
                    await session.execute(text("""
                        UPDATE car_models
                        SET hero_image_url = :img_url
                        WHERE brand_id IN (SELECT id FROM car_brands WHERE name ILIKE :brand_name)
                        AND (hero_image_url LIKE '%unsplash%' OR hero_image_url IS NULL OR hero_image_url = '')
                        AND (name ILIKE :mod_name OR name ILIKE :clean_mod)
                    """), {"img_url": img_url, "brand_name": brand_name, "mod_name": mod_name, "clean_mod": clean_mod})

        await session.commit()
        print(f"Updated car_models in PostgreSQL successfully! Processed {updated_count} curated models.")

        # Check remaining unsplash
        res = await session.execute(text("""
            SELECT b.name as brand, m.name as model, m.hero_image_url
            FROM car_models m
            JOIN car_brands b ON m.brand_id = b.id
            WHERE m.hero_image_url LIKE '%unsplash%'
            ORDER BY b.name, m.name
        """))
        remaining = res.fetchall()
        print(f"Remaining models with Unsplash: {len(remaining)}")
        for r in remaining:
            print(f"- {r[0]} | {r[1]}")

asyncio.run(update_database())
