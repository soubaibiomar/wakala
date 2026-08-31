from sqlalchemy import create_engine, text
import sys

sys.stdout.reconfigure(encoding='utf-8')
engine = create_engine('postgresql://wakala_user:wakala_secret_password@localhost:5433/wakala')

with engine.connect() as conn:
    print("=== Checking relations for vehicle images ===")
    tables = conn.execute(text("SELECT table_name FROM information_schema.tables WHERE table_schema='public'")).fetchall()
    print("Tables:", [t[0] for t in tables])

    # Check vehicle table columns
    cols = conn.execute(text("SELECT column_name, data_type FROM information_schema.columns WHERE table_name='vehicles'")).fetchall()
    print("Vehicle columns:", [c[0] for c in cols])

    # Check if there is an image table
    for t in ['vehicle_images', 'images', 'car_images']:
        if t in [tb[0] for tb in tables]:
            cnt = conn.execute(text(f"SELECT count(*) FROM {t}")).scalar()
            print(f"Table {t} exists with {cnt} rows")

    # Check Dacia vehicles
    rows = conn.execute(text("SELECT id, brand, model, version, price, condition, description FROM vehicles WHERE LOWER(brand)='dacia' LIMIT 15")).fetchall()
    for r in rows:
        print(f"Vehicle: {r[1]} {r[2]} ({r[3]}) - Price: {r[4]} - Condition: {r[5]} - Desc: {(r[6] or '')[:30]}")
