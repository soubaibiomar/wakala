import pytest
from datetime import datetime, timedelta, timezone
from data_pipeline.kafka.producers.scrapers.resilience_loop import ResilienceLoop

def test_should_run_never_run():
    loop = ResilienceLoop()
    loop.state_manager.get_state = lambda src: {"status": "active", "last_run_at": None}
    assert loop.should_run("test", 1.0) is True

def test_should_run_active_within_backoff():
    loop = ResilienceLoop()
    # Ran 30 mins ago, normal interval is 1 hour
    loop.state_manager.get_state = lambda src: {
        "status": "active",
        "current_backoff_interval": 3600,
        "last_run_at": datetime.now(timezone.utc) - timedelta(minutes=30)
    }
    assert loop.should_run("test", 1.0) is False

def test_should_run_active_outside_backoff():
    loop = ResilienceLoop()
    # Ran 2 hours ago, normal interval is 1 hour
    loop.state_manager.get_state = lambda src: {
        "status": "active",
        "current_backoff_interval": 3600,
        "last_run_at": datetime.now(timezone.utc) - timedelta(hours=2)
    }
    assert loop.should_run("test", 1.0) is True

def test_should_run_paused_within_24h():
    loop = ResilienceLoop()
    # Paused, ran 12 hours ago. Should wait for 24h.
    loop.state_manager.get_state = lambda src: {
        "status": "paused",
        "current_backoff_interval": 86400,
        "last_run_at": datetime.now(timezone.utc) - timedelta(hours=12)
    }
    assert loop.should_run("test", 1.0) is False

def test_should_run_paused_outside_24h():
    loop = ResilienceLoop()
    # Paused, ran 25 hours ago. Should run to check if block lifted.
    loop.state_manager.get_state = lambda src: {
        "status": "paused",
        "current_backoff_interval": 86400,
        "last_run_at": datetime.now(timezone.utc) - timedelta(hours=25)
    }
    assert loop.should_run("test", 1.0) is True
