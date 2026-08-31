"""
Module Graphe — Requêtes Neo4j pour la similarité véhicules.
Utilise PageRank et requêtes Cypher pour explorer le graphe
véhicules/marques/acheteurs.
"""

try:
    from neo4j import AsyncGraphDatabase
    NEO4J_AVAILABLE = True
except ImportError:
    AsyncGraphDatabase = None
    NEO4J_AVAILABLE = False

from app.core.config import settings


class VehicleGraphService:
    """Service de requêtes sur le graphe Neo4j."""

    def __init__(self):
        if NEO4J_AVAILABLE and AsyncGraphDatabase is not None:
            self.driver = AsyncGraphDatabase.driver(
                settings.NEO4J_URI,
                auth=(settings.NEO4J_USER, settings.NEO4J_PASSWORD),
            )
        else:
            self.driver = None

    async def close(self):
        await self.driver.close()

    async def get_similar_vehicles(self, vehicle_id: str, limit: int = 5) -> list[dict]:
        """Trouve les véhicules similaires via le graphe (voisinage + PageRank)."""
        query = """
        MATCH (v:Vehicle {id: $vehicle_id})-[:SIMILAR_TO]-(similar:Vehicle)
        RETURN similar.id AS id, similar.title AS title, similar.pagerank AS score
        ORDER BY similar.pagerank DESC
        LIMIT $limit
        """
        async with self.driver.session() as session:
            result = await session.run(query, vehicle_id=vehicle_id, limit=limit)
            return [record.data() async for record in result]

    async def get_brand_graph(self, brand: str) -> list[dict]:
        """Explore le sous-graphe d'une marque (modèles, acheteurs types)."""
        query = """
        MATCH (b:Brand {name: $brand})-[:PRODUCES]->(m:Model)-[:BOUGHT_BY]->(buyer:BuyerProfile)
        RETURN m.name AS model, collect(DISTINCT buyer.segment) AS buyer_segments
        """
        async with self.driver.session() as session:
            result = await session.run(query, brand=brand)
            return [record.data() async for record in result]
