import pytest
from unittest.mock import AsyncMock, patch, MagicMock

from app.ml.matching.schemas import SearchRequest
from app.ml.matching.matching_engine import matching_engine
from app.ml.nlp_pipeline.schemas import ExtractedCriteria
from app.models.vehicle import Vehicle

@pytest.fixture
def mock_db_session():
    session = AsyncMock()
    # On mock db.execute().scalars().all()
    mock_result = MagicMock()
    
    # 2 véhicules de test
    v1 = Vehicle(id="v1", brand="Renault", model="Clio", price=100000, body_type="citadine", year=2020, mileage=50000)
    v2 = Vehicle(id="v2", brand="Dacia", model="Lodgy", price=120000, body_type="monospace", year=2021, mileage=30000)
    
    mock_result.scalars.return_value.all.return_value = [v1, v2]
    session.execute.return_value = mock_result
    return session

@pytest.mark.asyncio
@patch("app.ml.matching.matching_engine.extract_search_criteria")
@patch("app.ml.matching.matching_engine.semantic_search")
@patch("app.ml.matching.matching_engine.compute_collaborative_scores")
async def test_matching_engine_simple_query(mock_collab, mock_semantic, mock_nlp, mock_db_session):
    # Setup mocks
    mock_nlp.return_value = ExtractedCriteria(budget=150000, usage_prevu="familial", priorites=[], erreur=False)
    mock_semantic.return_value = ["v2", "v1"] # Qdrant returns v2 then v1
    mock_collab.return_value = ([{"vehicle_id": "v1", "collaborative_score": 0.5}], False)
    
    req = SearchRequest(query="voiture familiale", user_id="u1")
    
    results = await matching_engine.search_with_persona(req, mock_db_session)
    
    assert mock_nlp.called
    assert mock_semantic.called
    assert mock_collab.called
    
    assert len(results) == 2
    # Verify badges mapping
    badges = [b for r in results for b in r.badges]
    assert "Idéal Famille" in badges

@pytest.mark.asyncio
@patch("app.ml.matching.matching_engine.extract_search_criteria")
@patch("app.ml.matching.matching_engine.semantic_search")
async def test_matching_engine_quiz_answers_override(mock_semantic, mock_nlp, mock_db_session):
    # Setup mocks: NLP says "urbain" but quiz says "familial"
    mock_nlp.return_value = ExtractedCriteria(budget=150000, usage_prevu="urbain", priorites=[], erreur=False)
    mock_semantic.return_value = []
    
    req = SearchRequest(
        query="peu importe",
        quiz_answers={"usage": "familial"}
    )
    
    results = await matching_engine.search_with_persona(req, mock_db_session)
    
    badges = [b for r in results for b in r.badges]
    # Quiz override should make it "familial"
    assert "Idéal Famille" in badges
    assert "Urbain" not in badges # Not generated anyway but confirms it didn't use "urbain"

@pytest.mark.asyncio
@patch("app.ml.matching.matching_engine.extract_search_criteria")
@patch("app.ml.matching.matching_engine.semantic_search")
async def test_matching_engine_no_candidates(mock_semantic, mock_nlp, mock_db_session):
    # DB returns empty
    mock_db_session.execute.return_value.scalars.return_value.all.return_value = []
    mock_nlp.return_value = ExtractedCriteria(erreur=False)
    mock_semantic.return_value = []
    
    req = SearchRequest(query="rien")
    results = await matching_engine.search_with_persona(req, mock_db_session)
    
    assert results == [] # Should be handled properly, no 500
