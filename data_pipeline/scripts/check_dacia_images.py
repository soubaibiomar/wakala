from sqlalchemy import create_engine, text
import json
import sys

sys.stdout.reconfigure(encoding='utf-8')
engine = create_engine('postgresql://wakala_user:wakala_secret_password@localhost:5433/wakala')

with engine.connect() as conn:
    print("=== CAR_MODELS for Dacia ===")
    models = conn.execute(text("SELECT id, name, slug, hero_image_url FROM car_models WHERE brand_id IN (SELECT id FROM car_brands WHERE LOWER(name)='dacia')")).fetchall()
    for m in models:
        print(f"Model: '{m[1]}' (slug: '{m[2]}') -> hero_image_url: {m[3]}")

    print("\n=== VEHICLES for Dacia (sample) ===")
    vehs = conn.execute(text("SELECT id, brand, model, version, price FROM vehicles WHERE LOWER(brand)='dacia' LIMIT 10")).fetchall()
    for v in vehs:
        print(f"Vehicle: '{v[1]}' '{v[2]}' '{v[3]}' ({v[4]} MAD)")
