import pytest
from data_pipeline.kafka.producers.scrapers.health_monitor import HealthMonitor

def test_health_monitor_metrics(monkeypatch):
    # Mock DB save and alerts to prevent side-effects during test
    mock_save_called = []
    mock_alert_called = []
    
    def mock_save(*args, **kwargs):
        mock_save_called.append((args, kwargs))
        
    def mock_alert(*args, **kwargs):
        mock_alert_called.append((args, kwargs))
        
    monkeypatch.setattr("data_pipeline.kafka.producers.scrapers.health_monitor.HealthMonitor._save_to_db", mock_save)
    monkeypatch.setattr("data_pipeline.kafka.producers.scrapers.health_monitor.send_alert", mock_alert)
    
    monitor = HealthMonitor("test_site", threshold=0.6)
    
    # 1. Simulate 5 attempts
    for _ in range(5):
        monitor.record_attempt()
        
    # 2. Simulate 4 successes (80% success rate, above 0.6 threshold)
    valid_listing = {"price": 10000, "brand": "audi"}
    for _ in range(4):
        monitor.record_success(valid_listing)
        
    # 3. Simulate 1 success but missing price
    monitor.record_success({"brand": "bmw", "price": None})
    
    monitor.finalize_run()
    
    # Success rate should be 5 / 5 = 100% (since we called record_success 5 times out of 5 attempts)
    # Field rate for brand: 5/5 = 100%
    # Field rate for price: 4/5 = 80%
    
    assert len(mock_save_called) == 1
    args, kwargs = mock_save_called[0]
    success_rate = args[1] # The first arg is 'self', second is success_rate
    field_rates = args[2]
    
    assert success_rate == 1.0
    assert field_rates["brand"] == 1.0
    assert field_rates["price"] == 0.8
    
    # No alert should be fired since 1.0 >= 0.6
    assert len(mock_alert_called) == 0

def test_health_monitor_alert(monkeypatch):
    mock_save_called = []
    mock_alert_called = []
    
    def mock_save(*args, **kwargs):
        mock_save_called.append((args, kwargs))
        
    def mock_alert(*args, **kwargs):
        mock_alert_called.append((args, kwargs))
        
    monkeypatch.setattr("data_pipeline.kafka.producers.scrapers.health_monitor.HealthMonitor._save_to_db", mock_save)
    monkeypatch.setattr("data_pipeline.kafka.producers.scrapers.health_monitor.send_alert", mock_alert)
    
    monitor = HealthMonitor("test_site", threshold=0.5)
    
    # 10 attempts
    for _ in range(10):
        monitor.record_attempt()
        
    # Only 3 successes (30% success rate, below 0.5 threshold)
    for _ in range(3):
        monitor.record_success({"brand": "audi"})
        
    monitor.finalize_run()
    
    # Alert should be triggered
    assert len(mock_alert_called) == 1
    assert mock_alert_called[0][0][0] == "test_site"
    assert "Degradation detected" in mock_alert_called[0][0][1]
