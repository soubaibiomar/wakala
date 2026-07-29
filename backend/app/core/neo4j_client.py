import logging
from neo4j import GraphDatabase
from app.core.config import Settings

logger = logging.getLogger(__name__)
settings = Settings()

class Neo4jClient:
    def __init__(self, uri, user, password):
        self.driver = None
        try:
            self.driver = GraphDatabase.driver(uri, auth=(user, password))
            logger.info("Connected to Neo4j successfully")
        except Exception as e:
            logger.error(f"Failed to create Neo4j driver: {e}")

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
