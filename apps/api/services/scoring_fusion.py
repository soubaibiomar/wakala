import math
from apps.api.config import K, MAX_W2, MIN_W2

def compute_weights(n_interactions: int) -> tuple[float, float]:
    """
    Calcule W1 et W2 dynamiquement selon l'historique utilisateur.
    W2 = min(MAX_W2, max(MIN_W2, log(1 + N_interactions) / K))
    W1 = 1 - W2
    """
    w2 = min(MAX_W2, max(MIN_W2, math.log(1 + n_interactions) / K))
    w1 = 1.0 - w2
    return w1, w2

def compute_final_score(w1: float, w2: float, score_content: float, score_collab: float) -> float:
    """
    Applique la fusion pondérée :
    Score_final = W1 × sim(V_user, V_annonce) + W2 × Score_graphe(persona)
    """
    return (w1 * score_content) + (w2 * score_collab)

def get_final_scores(n_interactions: int, content_scores: dict[str, float], collab_scores: dict[str, float]) -> dict[str, float]:
    """
    Calcule les scores finaux pour tous les IDs communs.
    Retourne {car_id: final_score}.
    """
    w1, w2 = compute_weights(n_interactions)
    
    # On récupère tous les IDs uniques
    all_ids = set(content_scores.keys()).union(set(collab_scores.keys()))
    
    final_scores = {}
    for car_id in all_ids:
        sc = content_scores.get(car_id, 0.0)
        sg = collab_scores.get(car_id, 0.0)
        final_scores[car_id] = compute_final_score(w1, w2, sc, sg)
        
    return final_scores
