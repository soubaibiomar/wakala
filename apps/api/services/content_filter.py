import requests
from apps.api.config import OLLAMA_URL, EMBEDDING_MODEL
from apps.api.db.qdrant_client import QdrantVectorClient

def get_embedding(text: str) -> list[float]:
    """
    Génère le vecteur d'embedding via bge-m3 sur Ollama local.
    """
    try:
        response = requests.post(
            f"{OLLAMA_URL}/api/embeddings",
            json={
                "model": EMBEDDING_MODEL,
                "prompt": text
            },
            timeout=10
        )
        response.raise_for_status()
        return response.json().get("embedding", [])
    except Exception as e:
        raise RuntimeError(f"Erreur génération embedding: {str(e)}")

def get_content_scores(soft_features: list[str], allowed_ids: list[str], qdrant_client: QdrantVectorClient) -> dict[str, float]:
    """
    Recherche cosinus dans Qdrant restreinte aux IDs pré-filtrés.
    
    Formule de similarité cosinus utilisée par Qdrant :
    Cos(θ) = Σ(A_i × B_i) / (√Σ(A_i²) × √Σ(B_i²))
    où A = vecteur utilisateur, B = vecteur annonce, i parcourt chaque dimension de l'embedding.
    """
    text_query = " ".join(soft_features)
    vector = get_embedding(text_query)
    
    if not vector:
        # Fallback de sécurité (utile pour les tests mockés si l'appel Ollama échoue)
        return {}
        
    scores = qdrant_client.search(
        collection_name="annonces_vecteurs",
        query_vector=vector,
        filter_ids=allowed_ids
    )
    
    return scores
