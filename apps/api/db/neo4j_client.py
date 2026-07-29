"""
apps/api/db/neo4j_client.py
Client Neo4j pour le filtrage collaboratif Wakala.

Modèle de graphe :
  (:User {id}) -[:BELONGS_TO]-> (:Persona {seg})
  (:User) -[:INTERACTED {type, weight, recency}]-> (:Car {mod, id})

  type ∈ {SAVED, CLICKED, VIEWED}
  weight : SAVED=3, CLICKED=2, VIEWED=1 (défini dans config.py)
  recency : facteur de décroissance exponentielle, calculé et stocké
            au moment de l'écriture de la relation (pas recalculé à la lecture).

Requête Cypher (structure exacte du spec) :
  MATCH (u:User {id: $user_id})-[:BELONGS_TO]->(p:Persona)<-[:BELONGS_TO]-(other:User)
  MATCH (other)-[r:INTERACTED]->(c:Car)
  RETURN c.id, sum(r.weight * r.recency) AS collab_score
  ORDER BY collab_score DESC
"""
import os
import logging

logger = logging.getLogger("wakala.db.neo4j")

NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "wakala")

# Requête Cypher exacte du spec
COLLAB_QUERY = """
MATCH (u:User {id: $user_id})-[:BELONGS_TO]->(p:Persona)<-[:BELONGS_TO]-(other:User)
MATCH (other)-[r:INTERACTED]->(c:Car)
RETURN c.id AS car_id, sum(r.weight * r.recency) AS collab_score
ORDER BY collab_score DESC
"""


class Neo4jClient:
    """
    Client Neo4j pour le scoring collaboratif.

    Formule :
      Score_collab = Σ(w_interaction × r_recence)
      avec w : SAVED=3, CLICKED=2, VIEWED=1
      r.recency est un facteur de décroissance exponentielle déjà stocké.

    La normalisation (score / max_score_du_lot) est faite dans
    services/collaborative_filter.py, pas ici.

    Les imports neo4j sont différés pour permettre l'exécution des tests
    avec des mocks sans dépendance installée.
    """

    def __init__(self, uri: str | None = None, user: str | None = None, password: str | None = None):
        self._uri = uri or NEO4J_URI
        self._user = user or NEO4J_USER
        self._password = password or NEO4J_PASSWORD
        self._driver = None

    def _get_driver(self):
        if self._driver is None:
            from neo4j import GraphDatabase
            self._driver = GraphDatabase.driver(
                self._uri,
                auth=(self._user, self._password),
            )
        return self._driver

    def get_collaborative_scores(self, user_id: str) -> dict[str, float]:
        """
        Exécute la requête Cypher pour obtenir les scores collaboratifs bruts.
        Retourne {car_id: raw_collab_score} non normalisé.
        """
        driver = self._get_driver()
        with driver.session() as session:
            result = session.run(COLLAB_QUERY, user_id=user_id)
            scores = {}
            for record in result:
                car_id = record["car_id"]
                score = float(record["collab_score"])
                scores[car_id] = score
            return scores

    def write_interaction(
        self,
        user_id: str,
        car_id: str,
        interaction_type: str,
        weight: int,
        recency: float,
    ):
        """
        Écrit une relation INTERACTED avec le poids et le facteur de recency
        pré-calculé (décroissance exponentielle calculée à l'écriture).
        """
        query = """
        MERGE (u:User {id: $user_id})
        MERGE (c:Car {id: $car_id})
        CREATE (u)-[:INTERACTED {type: $type, weight: $weight, recency: $recency}]->(c)
        """
        driver = self._get_driver()
        with driver.session() as session:
            session.run(
                query,
                user_id=user_id,
                car_id=car_id,
                type=interaction_type,
                weight=weight,
                recency=recency,
            )

    def close(self):
        if self._driver:
            self._driver.close()
