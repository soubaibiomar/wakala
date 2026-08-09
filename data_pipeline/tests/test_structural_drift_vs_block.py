import pytest
from unittest.mock import MagicMock, patch
from data_pipeline.kafka.producers.scrapers.resilience_loop import ResilienceLoop

@pytest.fixture
def resilience_loop():
    with patch('data_pipeline.kafka.producers.scrapers.resilience_loop.SourceStateManager'), \
         patch('data_pipeline.kafka.producers.scrapers.resilience_loop.SelectorRepair'):
        loop = ResilienceLoop()
        # Mock the underlying dependencies
        loop.state_manager = MagicMock()
        loop.repair_engine = MagicMock()
        # Mock get_state to return a valid dictionary
        loop.state_manager.get_state.return_value = {
            "selector_health_score": 100.0,
            "status": "active",
            "consecutive_failure_count": 0,
            "current_backoff_interval": 3600
        }
        return loop

def test_evaluate_scrape_active_block(resilience_loop):
    """Verify that a 403 triggers an active block and NEVER structural drift repair."""
    resilience_loop.evaluate_scrape("test_source", raw_listings=[], http_status=403, html_snippet=None)
    
    # Must record block failure
    resilience_loop.state_manager.record_block_failure.assert_called_once_with("test_source")
    
    # Must NOT record drift or trigger repair
    resilience_loop.state_manager.record_drift.assert_not_called()
    resilience_loop.repair_engine.propose_repair.assert_not_called()
    resilience_loop.state_manager.record_success.assert_not_called()

def test_evaluate_scrape_active_block_429(resilience_loop):
    """Verify that a 429 (rate limit) triggers an active block."""
    resilience_loop.evaluate_scrape("test_source", raw_listings=[], http_status=429, html_snippet=None)
    resilience_loop.state_manager.record_block_failure.assert_called_once_with("test_source")
    resilience_loop.repair_engine.propose_repair.assert_not_called()

def test_evaluate_scrape_structural_drift_0_listings(resilience_loop):
    """Verify that 200 OK with 0 listings triggers structural drift on listing_card."""
    resilience_loop.evaluate_scrape("test_source", raw_listings=[], http_status=200, html_snippet="<html>...</html>")
    
    # Must record drift
    resilience_loop.state_manager.record_drift.assert_called_once_with("test_source", 90.0)
    
    # Must trigger repair for listing_card
    resilience_loop.repair_engine.propose_repair.assert_called_once_with("test_source", "listing_card", "<html>...</html>")
    
    # Must NOT record block failure
    resilience_loop.state_manager.record_block_failure.assert_not_called()
    resilience_loop.state_manager.record_success.assert_not_called()

def test_evaluate_scrape_structural_drift_missing_fields(resilience_loop):
    """Verify that 200 OK with failed fields triggers structural drift on those fields."""
    resilience_loop.evaluate_scrape("test_source", raw_listings=[{"id": 1}], http_status=200, html_snippet="<html>...</html>", failed_fields=["price", "title"])
    
    resilience_loop.state_manager.record_drift.assert_called_once_with("test_source", 90.0)
    assert resilience_loop.repair_engine.propose_repair.call_count == 2
    
    resilience_loop.state_manager.record_block_failure.assert_not_called()
    resilience_loop.state_manager.record_success.assert_not_called()

def test_evaluate_scrape_success(resilience_loop):
    """Verify that a successful scrape triggers success branch."""
    resilience_loop.evaluate_scrape("test_source", raw_listings=[{"id": 1}], http_status=200, html_snippet="<html>...</html>")
    
    resilience_loop.state_manager.record_success.assert_called_once_with("test_source")
    resilience_loop.state_manager.record_block_failure.assert_not_called()
    resilience_loop.state_manager.record_drift.assert_not_called()
    resilience_loop.repair_engine.propose_repair.assert_not_called()
