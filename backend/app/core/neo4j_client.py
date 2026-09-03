import logging
from neo4j import GraphDatabase
from app.core.config import settings

logger = logging.getLogger(__name__)

class Neo4jClient:
    def __init__(self, uri, user, password):
        self.driver = None
        if not uri or not password:
            logger.info("Neo4j is not configured; graph features are disabled.")
            return
        try:
            self.driver = GraphDatabase.driver(uri, auth=(user, password))
            logger.info("Connected to Neo4j successfully")
        except Exception as e:
            logger.warning(f"Could not connect to Neo4j driver (continuing gracefully): {e}")

    def close(self):
        if self.driver:
            self.driver.close()

    def get_session(self):
        if not self.driver:
            raise Exception("Neo4j driver not initialized")
        return self.driver.session()

# Create a singleton instance
neo4j_client = Neo4jClient(settings.NEO4J_URI, settings.NEO4J_USER, settings.NEO4J_PASSWORD)

def get_neo4j_session():
    """Dependency for FastAPI"""
    session = neo4j_client.get_session()
    try:
        yield session
    finally:
        session.close()
