import pytest
from unittest.mock import MagicMock, patch
from data_pipeline.kafka.producers.scrapers.selector_repair import SelectorRepair

@pytest.fixture
def repair_engine():
    with patch('data_pipeline.kafka.producers.scrapers.selector_repair.SelectorReviewQueue'):
        engine = SelectorRepair()
        engine.queue = MagicMock()
        return engine

@patch('data_pipeline.kafka.producers.scrapers.selector_repair.ask_ollama')
def test_propose_repair_success(mock_ask_ollama, repair_engine):
    """Verify that a successful Ollama proposal is added to the review queue."""
    mock_ask_ollama.return_value = ".new-price-selector"
    
    result = repair_engine.propose_repair("test_site", "price", "<html><div class='new-price-selector'>1000</div></html>")
    
    assert result == ".new-price-selector"
    mock_ask_ollama.assert_called_once()
    
    repair_engine.queue.add_suggestion.assert_called_once_with(
        site="test_site",
        field="price",
        new_selector=".new-price-selector",
        confidence=0.8,
        reasoning="Proposed by Ollama self-repair due to structural drift.",
        example_value="Requires manual verification."
    )

@patch('data_pipeline.kafka.producers.scrapers.selector_repair.ask_ollama')
def test_propose_repair_failure(mock_ask_ollama, repair_engine):
    """Verify that if Ollama fails to propose, nothing is added to the queue."""
    mock_ask_ollama.return_value = None
    
    result = repair_engine.propose_repair("test_site", "price", "<html>...</html>")
    
    assert result is None
    repair_engine.queue.add_suggestion.assert_not_called()
