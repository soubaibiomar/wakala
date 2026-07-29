import sys
import os
import asyncio
from pathlib import Path
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

# Add project root to sys.path
sys.path.append(str(Path(__file__).parent))

from app.core.database import async_session_factory
from app.models.user import User
from app.models.vehicle import Vehicle
from app.models.catalog import BrandCatalog, ModelCatalog
from app.core.neo4j_client import neo4j_client

async def sync_users(session, db):
    print("Syncing Users to Neo4j...")
    result = await db.execute(select(User))
    users = result.scalars().all()
    
    query = """
    UNWIND $users AS u
    MERGE (user:User {id: u.id})
    SET user.email = u.email,
        user.role = u.role,
        user.name = u.name
    """
    
    users_data = [{"id": str(u.id), "email": u.email, "role": u.role, "name": u.full_name} for u in users]
    if users_data:
        session.run(query, users=users_data)
        print(f"Synced {len(users_data)} users.")

async def sync_catalog(session, db):
    print("Syncing Catalog (Brands & Models) to Neo4j...")
    
    # Sync Brands
    b_res = await db.execute(select(BrandCatalog))
    brands = b_res.scalars().all()
    
    b_query = """
    UNWIND $brands AS b
    MERGE (brand:Brand {name: b.name})
    SET brand.id = b.id,
        brand.country = b.country
    """
    b_data = [{"id": str(b.id), "name": b.name, "country": b.country_of_origin} for b in brands]
    if b_data:
        session.run(b_query, brands=b_data)
        print(f"Synced {len(b_data)} brands.")
        
    # Sync Models
    m_res = await db.execute(select(ModelCatalog).options(selectinload(ModelCatalog.brand)))
    models = m_res.scalars().all()
    
    m_query = """
    UNWIND $models AS m
    MERGE (model:Model {name: m.name, brand_id: m.brand_id})
    SET model.id = m.id,
        model.body_type = m.body_type
        
    WITH model, m
    MATCH (brand:Brand {id: m.brand_id})
    MERGE (model)-[:BELONGS_TO_BRAND]->(brand)
    """
    m_data = [{"id": str(m.id), "name": m.name, "brand_id": str(m.brand_id), "body_type": m.body_type} for m in models]
    if m_data:
        session.run(m_query, models=m_data)
        print(f"Synced {len(m_data)} models and linked to brands.")

async def sync_vehicles(session, db):
    print("Syncing Vehicles to Neo4j...")
    v_res = await db.execute(select(Vehicle).options(selectinload(Vehicle.seller)))
    vehicles = v_res.scalars().all()
    
    query = """
    UNWIND $vehicles AS v
    MERGE (veh:Vehicle {id: v.id})
    SET veh.brand = v.brand,
        veh.model = v.model,
        veh.year = v.year,
        veh.price = v.price,
        veh.fuel_type = v.fuel_type,
        veh.body_type = v.body_type,
        veh.city = v.city,
        veh.description = v.description
        
    WITH veh, v
    MATCH (user:User {id: v.seller_id})
    MERGE (user)-[:SELLS]->(veh)
    
    WITH veh, v
    MATCH (brand:Brand {name: v.brand})
    MERGE (veh)-[:IS_BRAND]->(brand)
    """
    v_data = [{
        "id": str(v.id), "brand": v.brand.upper(), "model": v.model.upper(), 
        "year": v.year, "price": float(v.price), "fuel_type": v.fuel_type, 
        "body_type": v.body_type, "city": v.city, "description": v.description, "seller_id": str(v.seller_id)
    } for v in vehicles]
    
    if v_data:
        session.run(query, vehicles=v_data)
        print(f"Synced {len(v_data)} vehicles and linked to sellers and brands.")

async def main():
    print("Starting Neo4j Sync...")
    try:
        neo_session = neo4j_client.get_session()
        async with async_session_factory() as db:
            await sync_users(neo_session, db)
            await sync_catalog(neo_session, db)
            await sync_vehicles(neo_session, db)
        neo_session.close()
        print("Neo4j Sync completed successfully!")
    except Exception as e:
        print(f"Error during Neo4j sync: {e}")

if __name__ == "__main__":
    asyncio.run(main())
