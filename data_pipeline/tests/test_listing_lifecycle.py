import pytest
from datetime import datetime, timedelta, timezone
from unittest.mock import MagicMock, patch
from data_pipeline.kafka.producers.scrapers.listing_lifecycle import ListingLifecycleManager

@pytest.fixture
def lifecycle_manager():
    with patch('data_pipeline.kafka.producers.scrapers.listing_lifecycle.psycopg2'):
        manager = ListingLifecycleManager()
        return manager

def test_expire_old_listings(lifecycle_manager):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
    
    # Mock some returned ids
    mock_cursor.fetchall.return_value = [{"id": "1"}, {"id": "2"}]
    
    lifecycle_manager._expire_old_listings(mock_conn)
    
    # Check that query was executed
    assert mock_cursor.execute.called
    args, _ = mock_cursor.execute.call_args
    sql = args[0]
    params = args[1]
    
    assert "UPDATE listings" in sql
    assert "status = 'expired'" in sql
    assert "published_at < %s" in sql
    assert "is_manually_reviewed = FALSE" in sql
    
    # Check cutoff date
    cutoff_date = params[0]
    expected_cutoff = datetime.now(timezone.utc) - timedelta(days=14)
    # Allow 1 second tolerance
    assert abs((cutoff_date - expected_cutoff).total_seconds()) < 1.0

def test_hard_delete_grace_period(lifecycle_manager):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
    
    lifecycle_manager._hard_delete_grace_period(mock_conn)
    
    assert mock_cursor.execute.called
    args, _ = mock_cursor.execute.call_args
    sql = args[0]
    params = args[1]
    
    assert "DELETE FROM listings" in sql
    assert "status IN ('expired', 'sold')" in sql
    assert "updated_at < %s" in sql
    assert "is_manually_reviewed = FALSE" in sql
    
    cutoff_date = params[0]
    expected_cutoff = datetime.now(timezone.utc) - timedelta(days=7)
    assert abs((cutoff_date - expected_cutoff).total_seconds()) < 1.0
