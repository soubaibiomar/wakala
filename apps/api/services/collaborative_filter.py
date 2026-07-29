from apps.api.db.neo4j_client import Neo4jClient

def get_collaborative_scores(user_id: str, neo4j_client: Neo4jClient, allowed_ids: list[str]) -> dict[str, float]:
    """
    Exécute la requête Cypher pour obtenir les scores collaboratifs bruts et les normalise.
    """
    # L'appel à Neo4j exécute la requête exacte:
    # MATCH (u:User {id: $user_id})-[:BELONGS_TO]->(p:Persona)<-[:BELONGS_TO]-(other:User)
    # MATCH (other)-[r:INTERACTED]->(c:Car)
    # RETURN c.id, sum(r.weight * r.recency) AS collab_score
    # ORDER BY collab_score DESC
    #
    # Formule : Score_collab = Σ(w_interaction × r_recence)
    # avec w: SAVED=3, CLICKED=2, VIEWED=1
    
    raw_scores = neo4j_client.get_collaborative_scores(user_id)
    
    # Filtrer par hard_filters
    filtered_scores = {car_id: score for car_id, score in raw_scores.items() if car_id in allowed_ids}
    
    if not filtered_scores:
        return {}
        
    # Normalisation : score_collab_normalise = collab_score / max_collab_score_du_lot
    max_score = max(filtered_scores.values())
    
    if max_score > 0:
        normalized_scores = {car_id: score / max_score for car_id, score in filtered_scores.items()}
    else:
        normalized_scores = {car_id: 0.0 for car_id in filtered_scores.keys()}
        
    return normalized_scores
