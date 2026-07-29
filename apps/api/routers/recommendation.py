"""
apps/api/routers/recommendation.py
Endpoint POST /api/recommend — point d'entrée du moteur de recommandation hybride.
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from apps.api.db.postgres import PostgresClient
from apps.api.db.qdrant_client import QdrantVectorClient
from apps.api.db.neo4j_client import Neo4jClient
from apps.api.services.orchestrator import run_recommendation_pipeline

router = APIRouter()

# Instances de clients DB (en production, injectées via FastAPI Depends)
pg_client = PostgresClient()
qdrant_client = QdrantVectorClient()
neo4j_client = Neo4jClient()


class RecommendationRequest(BaseModel):
    user_id: str
    query: str


class RecommendationItem(BaseModel):
    car_id: str
    score_final: float
    score_contenu: float
    score_collab: float
    w1: float
    w2: float
    justification: str


class RecommendationResponse(BaseModel):
    results: list[RecommendationItem]


@router.post("/api/recommend", response_model=RecommendationResponse)
def get_recommendations(req: RecommendationRequest):
    """
    Moteur de recommandation hybride Wakala.
    Combine filtrage par contenu (Qdrant/bge-m3) et collaboratif (Neo4j)
    avec fusion pondérée dynamique.
    """
    try:
        results = run_recommendation_pipeline(
            user_id=req.user_id,
            query=req.query,
            pg_client=pg_client,
            qdrant_client=qdrant_client,
            neo4j_client=neo4j_client,
        )
        return {"results": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
