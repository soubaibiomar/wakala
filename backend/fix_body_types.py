import sys
import asyncio
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from app.core.database import async_session_factory
from app.models.vehicle import Vehicle
from sqlalchemy import select, update

# Dictionnaires de classification par mots-clés dans le modèle
BODY_TYPES_MAP = {
    "suv": [
        "duster", "spring", "jogger", "stepway",
        "captur", "arkana", "austral", "koleos", "symbioz", "espace", "scenic",
        "2008", "3008", "5008",
        "tucson", "santa fe", "kona", "bayon", "creta", "palisade", "ioniq 5",
        "tiguan", "touareg", "t-roc", "t-cross", "taigo", "id.4", "id.5",
        "q2", "q3", "q5", "q7", "q8", "e-tron",
        "x1", "x2", "x3", "x4", "x5", "x6", "x7",
        "gla", "glb", "glc", "gle", "gls", "g-class",
        "macan", "cayenne",
        "range rover", "evoque", "velar", "defender", "discovery",
        "sportage", "sorento", "niro", "seltos",
        "rav4", "land cruiser", "c-hr", "highlander", "yaris cross"
    ],
    "citadine": [
        "sandero",
        "clio", "twingo", "zoe",
        "208", 
        "i10", "i20",
        "polo", "up!"
    ],
    "utilitaire": [
        "kangoo", "trafic", "master", "express",
        "partner", "expert", "boxer", "rifter",
        "caddy", "transporter", "crafter", "amarok"
    ],
    "berline": [
        "logan",
        "megane", "talisman",
        "308", "408", "508",
        "i30", "elantra", "sonata", "ioniq 6",
        "golf", "passat", "arteon", "id.3"
    ]
}

async def fix_body_types():
    async with async_session_factory() as db:
        result = await db.execute(select(Vehicle))
        vehicles = result.scalars().all()
        
        updated_count = 0
        for v in vehicles:
            model_lower = v.model.lower()
            new_type = None
            
            for b_type, keywords in BODY_TYPES_MAP.items():
                if any(kw in model_lower for kw in keywords):
                    new_type = b_type
                    break
            
            # Si on ne trouve pas de correspondance exacte, on garde l'existant
            # ou on pourrait affiner. Pour l'instant on met à jour si ça correspond.
            if new_type and v.body_type != new_type:
                v.body_type = new_type
                updated_count += 1
                print(f"Updated {v.brand} {v.model} -> {new_type}")
                
        await db.commit()
        print(f"\nCorrection terminée ! {updated_count} véhicules mis à jour.")

if __name__ == "__main__":
    asyncio.run(fix_body_types())
