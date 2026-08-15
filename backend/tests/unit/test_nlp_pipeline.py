import pytest
from httpx import TimeoutException, RequestError
import json
from unittest.mock import patch, AsyncMock, MagicMock

from app.ml.nlp_pipeline.schemas import ExtractedCriteria
from app.ml.nlp_pipeline.budget_validator import normalize_and_validate_budget
from app.ml.nlp_pipeline.llm_extractor import extract_search_criteria

def test_budget_normalizer_clear():
    # Phrase avec budget clair
    assert normalize_and_validate_budget("150000") == 150000
    assert normalize_and_validate_budget("150k") == 150000
    assert normalize_and_validate_budget("150 k") == 150000
    assert normalize_and_validate_budget("1.5 million") == 1500000
    # Cas avec DH
    assert normalize_and_validate_budget("je cherche une voiture à 150000 DH") == 150000
    
def test_budget_normalizer_out_of_bounds():
    # 1 DH -> Should reject (range 20,000 - 3,000,000)
    assert normalize_and_validate_budget("1") == None
    # 50 million DH -> too high (50,000,000 > 3,000,000)
    assert normalize_and_validate_budget("50 million") == None

def test_budget_normalizer_ambiguous():
    # Budget ambigu/absent
    assert normalize_and_validate_budget("une voiture pas trop chère") == None
    assert normalize_and_validate_budget("je veux un suv") == None

@pytest.mark.asyncio
@patch("app.ml.nlp_pipeline.llm_extractor.httpx.AsyncClient.post")
async def test_llm_extractor_timeout_fallback(mock_post):
    # Simulate timeout
    mock_post.side_effect = TimeoutException("Timeout")
    
    texte = "je cherche une voiture familiale à 150k"
    res = await extract_search_criteria(texte)
    
    assert res.erreur is False
    assert res.budget == 150000
    assert res.usage_prevu == "familial"

@pytest.mark.asyncio
@patch("app.ml.nlp_pipeline.llm_extractor.httpx.AsyncClient.post")
async def test_llm_extractor_malformed_json(mock_post):
    # Simulate bad JSON
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "choices": [{"message": {"content": "This is not JSON"}}]
    }
    mock_post.return_value = mock_response
    
    texte = "voiture eco"
    res = await extract_search_criteria(texte)
    
    assert res.erreur is False
    assert "économique" in res.priorites
    
@pytest.mark.asyncio
@patch("app.ml.nlp_pipeline.llm_extractor.httpx.AsyncClient.post")
async def test_llm_extractor_success(mock_post):
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "choices": [{"message": {"content": json.dumps({
            "budget": 200000,
            "usage": "urbain",
            "priorites": ["automatique"],
            "profil_passagers": "célibataire"
        })}}]
    }
    mock_post.return_value = mock_response
    
    texte = "je veux une citadine auto 200k"
    res = await extract_search_criteria(texte)
    
    assert res.erreur is False
    assert res.budget == 200000
    assert res.usage_prevu == "urbain"
    assert "automatique" in res.priorites
