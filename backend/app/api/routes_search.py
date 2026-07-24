"""
api/routes_search.py — Endpoint d'extraction NLP pour la recherche en texte libre.

POST /api/search/parse
  Body : {"texte": "je cherche une voiture familiale autour de 200k"}
  Response : {"budget": 200000, "usage": "familial", "priorites": ["économique"], ...}
"""

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.ml.matching.matching_engine import matching_engine
from app.ml.matching.schemas import SearchRequest, RankedResult

router = APIRouter()

@router.post("/parse", response_model=list[RankedResult])
async def parse_search_query(payload: SearchRequest, db: AsyncSession = Depends(get_db)):
    """
    Analyse une phrase de recherche en texte libre, extrait
    les critères NLP, et interroge simultanément Qdrant et Neo4j
    pour retourner une liste rankée de véhicules avec scores et badges.
    """
    results = await matching_engine.search_with_persona(payload, db)
    return results
