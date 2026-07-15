from neo4j import AsyncGraphDatabase
import random
import logging

from app.core.config import settings

logger = logging.getLogger(__name__)

class BrokerDetectorService:
    def __init__(self):
        self._driver = None

    @property
    def driver(self):
        """Lazy-load the Neo4j driver to avoid blocking at import time."""
        if self._driver is None:
            try:
                self._driver = AsyncGraphDatabase.driver(
                    settings.NEO4J_URI,
                    auth=(settings.NEO4J_USER, settings.NEO4J_PASSWORD)
                )
            except Exception as e:
                logger.error(f"Impossible de se connecter à Neo4j: {e}")
                raise
        return self._driver

    async def close(self):
        if self._driver:
            await self._driver.close()

    async def ingest_user_listing_activity(self, user_id: str, phone: str, ip_address: str, vehicle_id: str, brand: str, city: str):
        """
        Crée les nœuds et relations dans Neo4j pour l'analyse de graphe.
        """
        try:
            async with self.driver.session() as session:
                query = """
                MERGE (u:User {id: $user_id})
                MERGE (ip:IPAddress {address: $ip_address})
                MERGE (ph:PhoneNumber {number: $phone})
                MERGE (v:Vehicle {id: $vehicle_id, brand: $brand, city: $city})

                MERGE (u)-[:PUBLIE_ANNONCE]->(v)
                MERGE (u)-[:PARTAGE_IP]->(ip)
                MERGE (u)-[:A_POUR_TELEPHONE]->(ph)
                """
                await session.run(query, user_id=user_id, phone=phone, ip_address=ip_address, vehicle_id=vehicle_id, brand=brand, city=city)
        except Exception as e:
            logger.error(f"Erreur lors de l'ingestion Neo4j: {e}")

    async def detect_brokers(self, min_shared_artifacts: int = 2, min_ads: int = 2):
        """
        Détecte les courtiers clandestins via l'analyse de graphe.
        Identifie les clusters d'utilisateurs partageant les mêmes IP ou téléphones,
        publiant de nombreuses annonces sur des marques variées.
        """
        try:
            async with self.driver.session() as session:
                query = """
                MATCH (u1:User)-[:PARTAGE_IP]->(ip:IPAddress)<-[:PARTAGE_IP]-(u2:User)
                WHERE u1.id <> u2.id
                WITH COLLECT(DISTINCT u1.id) + COLLECT(DISTINCT u2.id) AS shared_ip_users

                MATCH (u3:User)-[:A_POUR_TELEPHONE]->(ph:PhoneNumber)<-[:A_POUR_TELEPHONE]-(u4:User)
                WHERE u3.id <> u4.id
                WITH shared_ip_users, COLLECT(DISTINCT u3.id) + COLLECT(DISTINCT u4.id) AS shared_phone_users

                WITH shared_ip_users + shared_phone_users AS all_suspects
                UNWIND all_suspects AS suspect_id
                WITH DISTINCT suspect_id

                MATCH (u:User {id: suspect_id})-[:PUBLIE_ANNONCE]->(v:Vehicle)
                WITH suspect_id, COUNT(DISTINCT v) AS ad_count, COLLECT(DISTINCT v.brand) AS brands
                WHERE ad_count >= $min_ads AND SIZE(brands) >= 2
                RETURN suspect_id
                """
                result = await session.run(query, min_ads=min_ads)
                records = [record async for record in result]
                return [record["suspect_id"] for record in records]
        except Exception as e:
            logger.error(f"Erreur lors de la détection de courtiers: {e}")
            return []

broker_detector = BrokerDetectorService()
