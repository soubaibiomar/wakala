import sys
import os
import asyncio
import requests
import json
from pathlib import Path
from sqlalchemy.future import select

# Add project root to sys.path
sys.path.append(str(Path(__file__).parent))

from app.core.database import async_session_factory
from app.models.vehicle import Vehicle
from app.core.qdrant_client import get_qdrant_client
from app.core.config import Settings
from qdrant_client.http.models import PointStruct

settings = Settings()
qdrant_client = get_qdrant_client()

def get_embedding(text: str) -> list[float]:
    """Appel à Ollama pour générer un vecteur via le modèle bge-m3:latest"""
    url = f"{settings.OLLAMA_BASE_URL.replace('/v1', '')}/api/embeddings"
    payload = {
        "model": "bge-m3:latest",
        "prompt": text
    }
    try:
        # Default ollama URL is typically http://ollama:11434
        response = requests.post(url, json=payload, timeout=30)
        response.raise_for_status()
        data = response.json()
        return data.get("embedding", [])
    except Exception as e:
        print(f"Error getting embedding from Ollama: {e}")
        return []

async def sync_vehicles_to_qdrant():
    if not qdrant_client:
        print("Qdrant client not initialized. Cannot sync.")
        return

    print("Fetching vehicles from Postgres for Qdrant sync...")
    points = []
    
    async with async_session_factory() as db:
        v_res = await db.execute(select(Vehicle))
        vehicles = v_res.scalars().all()
        
        for idx, v in enumerate(vehicles):
            # Construction d'un texte descriptif très complet pour la recherche sémantique
            text_repr = f"Marque: {v.brand}. Modèle: {v.model}. Type: {v.body_type}. Carburant: {v.fuel_type}. Transmission: {v.transmission}. Année: {v.year}. Kilométrage: {v.mileage} km. Prix: {v.price} MAD. Description: {v.description or 'Aucune'}. Ville: {v.city}"
            
            print(f"[{idx+1}/{len(vehicles)}] Embedding: {v.brand} {v.model}...")
            embedding = get_embedding(text_repr)
            
            if not embedding:
                print(f"Skipping {v.id} due to embedding failure.")
                continue
                
            payload = {
                "id": str(v.id),
                "brand": v.brand,
                "model": v.model,
                "year": v.year,
                "price": float(v.price),
                "fuel_type": v.fuel_type,
                "body_type": v.body_type,
                "city": v.city,
                "description": v.description
            }
            
            # Create a UUID integer representation for Qdrant ID if needed, 
            # but Qdrant supports UUID strings directly.
            points.append(
                PointStruct(
                    id=str(v.id),
                    vector=embedding,
                    payload=payload
                )
            )
            
    if points:
        print(f"Upserting {len(points)} vectors to Qdrant collection '{settings.QDRANT_COLLECTION}'...")
        # Batch upsert
        batch_size = 50
        for i in range(0, len(points), batch_size):
            batch = points[i:i+batch_size]
            qdrant_client.upsert(
                collection_name=settings.QDRANT_COLLECTION,
                points=batch
            )
        print("Qdrant Sync completed successfully!")
    else:
        print("No valid points to insert.")

if __name__ == "__main__":
    asyncio.run(sync_vehicles_to_qdrant())
