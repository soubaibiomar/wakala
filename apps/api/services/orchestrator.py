"""
apps/api/services/orchestrator.py
Orchestre l'ensemble du moteur de recommandation hybride Wakala.

Pipeline :
  1. Récupère l'utilisateur (PostgreSQL → persona_id, n_interactions)
  2. Extraction NLP (Ollama/Qwen → hard_filters + soft_features)
  3. Filtrage SQL strict (PostgreSQL → IDs autorisés)
  4. Filtrage par contenu (bge-m3 → Qdrant → scores cosinus)
  5. Filtrage collaboratif (Neo4j → scores graphe normalisés)
  6. Fusion pondérée dynamique (W1/W2 selon n_interactions)
  7. Top 3 + explicabilité (Ollama/Qwen → justification)
"""
import logging
from apps.api.db.postgres import PostgresClient
from apps.api.db.qdrant_client import QdrantVectorClient
from apps.api.db.neo4j_client import Neo4jClient
from apps.api.services.nlp_extraction import extract_constraints
from apps.api.services.content_filter import get_content_scores
from apps.api.services.collaborative_filter import get_collaborative_scores
from apps.api.services.scoring_fusion import get_final_scores, compute_weights
from apps.api.services.explanation_generator import generate_explanation

logger = logging.getLogger("wakala.orchestrator")


def run_recommendation_pipeline(
    user_id: str,
    query: str,
    pg_client: PostgresClient,
    qdrant_client: QdrantVectorClient,
    neo4j_client: Neo4jClient,
) -> list[dict]:
    """
    Orchestre l'ensemble du moteur de recommandation hybride.

    Args:
        user_id: identifiant de l'utilisateur
        query: requête en langage naturel
        pg_client: client PostgreSQL
        qdrant_client: client Qdrant (recherche vectorielle)
        neo4j_client: client Neo4j (graphe collaboratif)

    Returns:
        Top 3 des recommandations avec scores et justification.
    """
    # ── 1. Info Utilisateur (PostgreSQL) ───────────────────────
    user_info = pg_client.get_user(user_id)
    n_interactions = user_info.get("n_interactions", 0)
    persona_id = user_info.get("persona_id", "Unknown")
    logger.info(f"Utilisateur: {user_id}, persona: {persona_id}, interactions: {n_interactions}")

    # ── 2. Extraction NLP (Ollama / Qwen 2.5 Coder) ──────────
    nlp_result = extract_constraints(query)
    hard_filters = nlp_result.get("hard_filters", {})
    soft_features = nlp_result.get("soft_features", [])
    logger.info(f"NLP: hard_filters={hard_filters}, soft_features={soft_features}")

    # ── 3. Filtrage SQL Strict (PostgreSQL) ───────────────────
    # Appliqué AVANT tout calcul vectoriel
    allowed_ids = pg_client.get_cars_by_hard_filters(hard_filters)
    if not allowed_ids:
        logger.warning("Aucun véhicule ne respecte les contraintes strictes.")
        return []
    logger.info(f"Hard filters → {len(allowed_ids)} véhicules éligibles")

    # ── 4. Filtrage par Contenu (bge-m3 → Qdrant) ────────────
    content_scores = get_content_scores(soft_features, allowed_ids, qdrant_client)
    logger.info(f"Content scores: {len(content_scores)} véhicules scorés")

    # ── 5. Filtrage Collaboratif (Neo4j) ─────────────────────
    collab_scores = get_collaborative_scores(user_id, neo4j_client, allowed_ids)
    logger.info(f"Collab scores: {len(collab_scores)} véhicules scorés")

    # ── 6. Fusion Pondérée Dynamique ──────────────────────────
    w1, w2 = compute_weights(n_interactions)
    final_scores = get_final_scores(n_interactions, content_scores, collab_scores)
    logger.info(f"Fusion: W1={w1:.2f}, W2={w2:.2f} → {len(final_scores)} scores finaux")

    # ── 7. Top 3 + Explicabilité ──────────────────────────────
    sorted_ids = sorted(final_scores.keys(), key=lambda x: final_scores[x], reverse=True)[:3]

    results = []
    for car_id in sorted_ids:
        # Récupérer les détails pour l'explicabilité
        car_details = pg_client.get_car_details(car_id)
        if car_details is None:
            car_details = {"titre": car_id, "id": car_id}

        explication = generate_explanation(persona_id, hard_filters, soft_features, car_details)

        results.append({
            "car_id": car_id,
            "score_final": round(final_scores[car_id], 4),
            "score_contenu": round(content_scores.get(car_id, 0.0), 4),
            "score_collab": round(collab_scores.get(car_id, 0.0), 4),
            "w1": round(w1, 4),
            "w2": round(w2, 4),
            "justification": explication,
        })

    logger.info(f"Top {len(results)} recommandations générées.")
    return results
