"""
═══════════════════════════════════════════════════════════════
AutoMind — Initialisation du Vector Store (Qdrant)
Collections : vehicle_embeddings + review_embeddings
═══════════════════════════════════════════════════════════════

Usage :
    python 001_init_collection.py [--host HOST] [--port PORT] [--reset]

Crée deux collections :
    1. vehicle_embeddings — Recherche sémantique véhicules + RAG chatbot
    2. review_embeddings  — Recherche sur avis (futur module sentiment/RAG)

Modèle d'embedding : sentence-transformers/all-MiniLM-L6-v2 (dim=384)
"""

import argparse
import sys
from typing import Optional

from qdrant_client import QdrantClient
from qdrant_client.http.exceptions import UnexpectedResponse
from qdrant_client.models import (
    Distance,
    VectorParams,
    HnswConfigDiff,
    OptimizersConfigDiff,
    PayloadSchemaType,
    PointStruct,
    TextIndexParams,
    TextIndexType,
    TokenizerType,
)


# ═══════════════════════════════════════════════════════════════
# Configuration
# ═══════════════════════════════════════════════════════════════

EMBEDDING_DIM = 384  # sentence-transformers/all-MiniLM-L6-v2

COLLECTIONS = {
    # ─── Collection 1 : Véhicules ──────────────────────────────
    "vehicle_embeddings": {
        "vector_size": EMBEDDING_DIM,
        "distance": Distance.COSINE,
        "hnsw_config": HnswConfigDiff(
            m=16,                    # Nombre de connexions par noeud dans le graphe HNSW
            ef_construct=200,        # Qualité de construction (plus haut = plus précis, plus lent)
            full_scan_threshold=10000,
        ),
        "optimizers_config": OptimizersConfigDiff(
            indexing_threshold=20000,  # Seuil pour déclencher l'indexation
        ),
        # Payload indexes pour le filtrage hybride (vectoriel + structuré)
        "payload_indexes": {
            "brand":       PayloadSchemaType.KEYWORD,
            "model":       PayloadSchemaType.KEYWORD,
            "fuel_type":   PayloadSchemaType.KEYWORD,
            "body_type":   PayloadSchemaType.KEYWORD,
            "city":        PayloadSchemaType.KEYWORD,
            "year":        PayloadSchemaType.INTEGER,
            "price":       PayloadSchemaType.FLOAT,
            "mileage":     PayloadSchemaType.INTEGER,
            "seller_id":   PayloadSchemaType.KEYWORD,
            "listing_status": PayloadSchemaType.KEYWORD,
        },
        # Index full-text sur la description (pour recherche hybride)
        "text_indexes": {
            "description": TextIndexParams(
                type=TextIndexType.TEXT,
                tokenizer=TokenizerType.MULTILINGUAL,
                min_token_len=2,
                max_token_len=20,
                lowercase=True,
            ),
        },
    },

    # ─── Collection 2 : Avis (reviews) ─────────────────────────
    "review_embeddings": {
        "vector_size": EMBEDDING_DIM,
        "distance": Distance.COSINE,
        "hnsw_config": HnswConfigDiff(
            m=16,
            ef_construct=128,
            full_scan_threshold=5000,
        ),
        "optimizers_config": OptimizersConfigDiff(
            indexing_threshold=10000,
        ),
        "payload_indexes": {
            "vehicle_id":      PayloadSchemaType.KEYWORD,
            "seller_id":       PayloadSchemaType.KEYWORD,
            "author_id":       PayloadSchemaType.KEYWORD,
            "rating":          PayloadSchemaType.INTEGER,
            "sentiment_label": PayloadSchemaType.KEYWORD,
            "sentiment_score": PayloadSchemaType.FLOAT,
            "target_type":     PayloadSchemaType.KEYWORD,
        },
        "text_indexes": {
            "comment": TextIndexParams(
                type=TextIndexType.TEXT,
                tokenizer=TokenizerType.MULTILINGUAL,
                min_token_len=2,
                max_token_len=20,
                lowercase=True,
            ),
        },
    },
}


# ═══════════════════════════════════════════════════════════════
# Fonctions
# ═══════════════════════════════════════════════════════════════

def get_client(host: str, port: int) -> QdrantClient:
    """Crée et teste la connexion au serveur Qdrant."""
    client = QdrantClient(host=host, port=port, timeout=30)
    try:
        client.get_collections()
        print(f"✅ Connecté à Qdrant — {host}:{port}")
    except Exception as e:
        print(f"❌ Impossible de se connecter à Qdrant ({host}:{port}): {e}")
        sys.exit(1)
    return client


def collection_exists(client: QdrantClient, name: str) -> bool:
    """Vérifie si une collection existe."""
    collections = [c.name for c in client.get_collections().collections]
    return name in collections


def create_collection(
    client: QdrantClient,
    name: str,
    config: dict,
    reset: bool = False,
) -> None:
    """
    Crée une collection Qdrant avec sa configuration complète.
    Si reset=True, supprime et recrée la collection existante.
    """
    exists = collection_exists(client, name)

    if exists and reset:
        client.delete_collection(name)
        print(f"🗑️  Collection '{name}' supprimée (reset)")
        exists = False

    if exists:
        info = client.get_collection(name)
        print(f"ℹ️  Collection '{name}' existe déjà ({info.points_count} points, dim={info.config.params.vectors.size})")
        return

    # Créer la collection
    client.create_collection(
        collection_name=name,
        vectors_config=VectorParams(
            size=config["vector_size"],
            distance=config["distance"],
        ),
        hnsw_config=config.get("hnsw_config"),
        optimizers_config=config.get("optimizers_config"),
    )
    print(f"✅ Collection '{name}' créée (dim={config['vector_size']}, distance={config['distance']})")

    # Créer les index de payload (filtrage structuré)
    for field_name, field_type in config.get("payload_indexes", {}).items():
        client.create_payload_index(
            collection_name=name,
            field_name=field_name,
            field_schema=field_type,
        )
        print(f"   📌 Index payload : {field_name} ({field_type})")

    # Créer les index full-text
    for field_name, text_params in config.get("text_indexes", {}).items():
        client.create_payload_index(
            collection_name=name,
            field_name=field_name,
            field_schema=text_params,
        )
        print(f"   📝 Index full-text : {field_name}")


def upsert_vehicle_embedding(
    client: QdrantClient,
    vehicle_id: str,
    embedding: list[float],
    metadata: dict,
    collection: str = "vehicle_embeddings",
) -> None:
    """
    Insère ou met à jour l'embedding d'un véhicule.

    Fonction réutilisable par le backend (app/rag/vector_store.py)
    et le pipeline batch (data-pipeline/airflow).

    Args:
        client: Client Qdrant connecté
        vehicle_id: UUID du véhicule (utilisé comme point ID via hash)
        embedding: Vecteur d'embedding (dim=384)
        metadata: Payload structuré (brand, model, price, city, etc.)
        collection: Nom de la collection cible
    """
    import uuid as uuid_lib
    point_id = str(uuid_lib.uuid5(uuid_lib.NAMESPACE_DNS, vehicle_id))

    client.upsert(
        collection_name=collection,
        points=[
            PointStruct(
                id=point_id,
                vector=embedding,
                payload={
                    "vehicle_id": vehicle_id,
                    **metadata,
                },
            )
        ],
    )


def upsert_review_embedding(
    client: QdrantClient,
    review_id: str,
    embedding: list[float],
    metadata: dict,
    collection: str = "review_embeddings",
) -> None:
    """
    Insère ou met à jour l'embedding d'un avis.

    Args:
        client: Client Qdrant connecté
        review_id: UUID de l'avis
        embedding: Vecteur d'embedding du texte de l'avis
        metadata: Payload (vehicle_id, seller_id, rating, sentiment_score, etc.)
        collection: Nom de la collection cible
    """
    import uuid as uuid_lib
    point_id = str(uuid_lib.uuid5(uuid_lib.NAMESPACE_DNS, review_id))

    client.upsert(
        collection_name=collection,
        points=[
            PointStruct(
                id=point_id,
                vector=embedding,
                payload={
                    "review_id": review_id,
                    **metadata,
                },
            )
        ],
    )


def seed_demo_data(client: QdrantClient) -> None:
    """
    Insère des données de démonstration (embeddings aléatoires).
    En production, les embeddings sont générés par sentence-transformers.
    """
    import random

    demo_vehicles = [
        {
            "vehicle_id": "demo-001",
            "brand": "Peugeot", "model": "3008", "year": 2022,
            "price": 285000.0, "fuel_type": "diesel", "body_type": "suv",
            "city": "Casablanca", "mileage": 45000, "listing_status": "active",
            "description": "Peugeot 3008 GT Line diesel 130ch, SUV familial bien entretenu",
        },
        {
            "vehicle_id": "demo-002",
            "brand": "Renault", "model": "Captur", "year": 2023,
            "price": 220000.0, "fuel_type": "hybride", "body_type": "suv",
            "city": "Rabat", "mileage": 12000, "listing_status": "active",
            "description": "Renault Captur E-Tech hybride, faible kilométrage, comme neuf",
        },
        {
            "vehicle_id": "demo-003",
            "brand": "Tesla", "model": "Model 3", "year": 2023,
            "price": 420000.0, "fuel_type": "electrique", "body_type": "berline",
            "city": "Marrakech", "mileage": 8000, "listing_status": "active",
            "description": "Tesla Model 3 Long Range, autopilot, 8000km, garantie constructeur",
        },
        {
            "vehicle_id": "demo-004",
            "brand": "Volkswagen", "model": "Golf", "year": 2021,
            "price": 195000.0, "fuel_type": "essence", "body_type": "berline",
            "city": "Tanger", "mileage": 62000, "listing_status": "active",
            "description": "Volkswagen Golf 8 TSI 110, boîte auto DSG, toit ouvrant",
        },
        {
            "vehicle_id": "demo-005",
            "brand": "Dacia", "model": "Sandero", "year": 2024,
            "price": 115000.0, "fuel_type": "gpl", "body_type": "citadine",
            "city": "Agadir", "mileage": 2000, "listing_status": "active",
            "description": "Dacia Sandero ECO-G GPL, quasi neuve, idéale premier achat",
        },
    ]

    for vehicle in demo_vehicles:
        vid = vehicle.pop("vehicle_id")
        fake_embedding = [random.gauss(0, 1) for _ in range(EMBEDDING_DIM)]
        upsert_vehicle_embedding(client, vid, fake_embedding, vehicle)

    print(f"🚗 {len(demo_vehicles)} véhicules de démonstration insérés dans 'vehicle_embeddings'")


# ═══════════════════════════════════════════════════════════════
# Main
# ═══════════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(
        description="Initialise les collections Qdrant pour AutoMind"
    )
    parser.add_argument("--host", default="localhost", help="Hôte Qdrant (défaut: localhost)")
    parser.add_argument("--port", type=int, default=6333, help="Port Qdrant (défaut: 6333)")
    parser.add_argument("--reset", action="store_true", help="Supprimer et recréer les collections")
    parser.add_argument("--seed", action="store_true", help="Insérer des données de démonstration")
    args = parser.parse_args()

    print("═" * 60)
    print("  AutoMind — Initialisation Vector Store (Qdrant)")
    print("═" * 60)

    client = get_client(args.host, args.port)

    for name, config in COLLECTIONS.items():
        print(f"\n── Collection : {name} {'─' * (40 - len(name))}")
        create_collection(client, name, config, reset=args.reset)

    if args.seed:
        print(f"\n── Données de démonstration {'─' * 30}")
        seed_demo_data(client)

    print(f"\n{'═' * 60}")
    print("  ✅ Initialisation terminée")
    print(f"{'═' * 60}")


if __name__ == "__main__":
    main()
