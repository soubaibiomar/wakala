import sys
import os
import asyncio
import uuid
from datetime import datetime, timezone
from pathlib import Path

# Add project root to sys.path
sys.path.append(str(Path(__file__).parent.parent))

from app.core.database import async_session_factory
from app.models.catalog import BrandCatalog, ModelCatalog, TechSpecCatalog

async def seed_static_catalog():
    brands_data = [
        {
            "name": "DACIA",
            "country": "Roumanie",
            "models": [
                {
                    "name": "SANDERO",
                    "body_type": "citadine",
                    "specs": [
                        {"version": "1.0 TCe Essential", "price": 139000, "hp": 90, "fuel": "essence", "trans": "manuelle", "cons": 5.2},
                        {"version": "1.0 TCe Expression", "price": 154000, "hp": 90, "fuel": "essence", "trans": "manuelle", "cons": 5.3},
                    ]
                },
                {
                    "name": "DUSTER",
                    "body_type": "suv",
                    "specs": [
                        {"version": "1.5 dCi Expression", "price": 224000, "hp": 115, "fuel": "diesel", "trans": "manuelle", "cons": 4.8},
                        {"version": "1.5 dCi Journey", "price": 244000, "hp": 115, "fuel": "diesel", "trans": "automatique", "cons": 4.9},
                    ]
                }
            ]
        },
        {
            "name": "PEUGEOT",
            "country": "France",
            "models": [
                {
                    "name": "208",
                    "body_type": "citadine",
                    "specs": [
                        {"version": "1.2 PureTech Active", "price": 169000, "hp": 75, "fuel": "essence", "trans": "manuelle", "cons": 5.4},
                        {"version": "1.5 BlueHDi Allure", "price": 205000, "hp": 100, "fuel": "diesel", "trans": "manuelle", "cons": 4.2},
                    ]
                },
                {
                    "name": "3008",
                    "body_type": "suv",
                    "specs": [
                        {"version": "1.5 BlueHDi Allure Pack", "price": 339000, "hp": 130, "fuel": "diesel", "trans": "automatique", "cons": 5.1},
                        {"version": "1.5 BlueHDi GT", "price": 379000, "hp": 130, "fuel": "diesel", "trans": "automatique", "cons": 5.1},
                    ]
                }
            ]
        },
        {
            "name": "HYUNDAI",
            "country": "Corée du Sud",
            "models": [
                {
                    "name": "TUCSON",
                    "body_type": "suv",
                    "specs": [
                        {"version": "1.6 CRDi Premium", "price": 345000, "hp": 136, "fuel": "diesel", "trans": "automatique", "cons": 5.3},
                        {"version": "1.6 CRDi Ultimate", "price": 389000, "hp": 136, "fuel": "diesel", "trans": "automatique", "cons": 5.3},
                    ]
                }
            ]
        },
        {
            "name": "RENAULT",
            "country": "France",
            "models": [
                {
                    "name": "CLIO",
                    "body_type": "citadine",
                    "specs": [
                        {"version": "1.5 dCi Equilibre", "price": 185000, "hp": 115, "fuel": "diesel", "trans": "manuelle", "cons": 4.1},
                        {"version": "1.5 dCi Techno", "price": 209000, "hp": 115, "fuel": "diesel", "trans": "manuelle", "cons": 4.1},
                    ]
                }
            ]
        }
    ]

    try:
        async with async_session_factory() as db:
            for b_data in brands_data:
                result = await db.execute(BrandCatalog.__table__.select().where(BrandCatalog.name == b_data["name"]))
                row = result.fetchone()
                if not row:
                    b_id = uuid.uuid4()
                    brand = BrandCatalog(
                        id=b_id, name=b_data["name"], country_of_origin=b_data["country"],
                        created_at=datetime.now(timezone.utc), updated_at=datetime.now(timezone.utc)
                    )
                    db.add(brand)
                else:
                    b_id = row.id
                    
                for m_data in b_data["models"]:
                    m_res = await db.execute(ModelCatalog.__table__.select().where(
                        (ModelCatalog.brand_id == b_id) & (ModelCatalog.name == m_data["name"])
                    ))
                    m_row = m_res.fetchone()
                    if not m_row:
                        m_id = uuid.uuid4()
                        model = ModelCatalog(
                            id=m_id, brand_id=b_id, name=m_data["name"], body_type=m_data["body_type"],
                            created_at=datetime.now(timezone.utc), updated_at=datetime.now(timezone.utc)
                        )
                        db.add(model)
                    else:
                        m_id = m_row.id
                        
                    for s_data in m_data["specs"]:
                        s_res = await db.execute(TechSpecCatalog.__table__.select().where(
                            (TechSpecCatalog.model_id == m_id) & (TechSpecCatalog.version_name == s_data["version"])
                        ))
                        s_row = s_res.fetchone()
                        if not s_row:
                            spec = TechSpecCatalog(
                                id=uuid.uuid4(), model_id=m_id, version_name=s_data["version"],
                                price_new_mad=s_data["price"], fuel_type=s_data["fuel"],
                                engine_power_hp=s_data["hp"], transmission=s_data["trans"],
                                consumption_l_100=s_data["cons"],
                                created_at=datetime.now(timezone.utc), updated_at=datetime.now(timezone.utc)
                            )
                            db.add(spec)
                            
            await db.commit()
            print("Successfully saved clean, perfect static catalog data to database!")
    except Exception as e:
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(seed_static_catalog())
