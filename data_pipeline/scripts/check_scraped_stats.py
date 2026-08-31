from sqlalchemy import create_engine, text
import sys

sys.stdout.reconfigure(encoding='utf-8')
engine = create_engine('postgresql://wakala_user:wakala_secret_password@localhost:5433/wakala')
with engine.connect() as conn:
    m_imgs = conn.execute(text("SELECT count(*) FROM car_models WHERE hero_image_url LIKE '%moteur.ma%' OR hero_image_url LIKE '%wandaloo.com%'")).scalar()
    total = conn.execute(text("SELECT count(*) FROM car_models")).scalar()
    print(f"Modèles avec images réelles de portails marocains : {m_imgs} / {total}")
    samples = conn.execute(text("SELECT name, hero_image_url FROM car_models WHERE hero_image_url LIKE '%moteur.ma%' LIMIT 10")).fetchall()
    for s in samples:
        print("  ✓", s[0], "->", s[1])
