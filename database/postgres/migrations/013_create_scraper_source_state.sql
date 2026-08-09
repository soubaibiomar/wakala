CREATE TABLE scraper_source_state (
    source_name VARCHAR(50) PRIMARY KEY,
    status VARCHAR(20) NOT NULL DEFAULT 'active', -- 'active', 'degraded', 'paused'
    consecutive_failure_count INT NOT NULL DEFAULT 0,
    current_backoff_interval INT NOT NULL DEFAULT 0,
    selector_health_score NUMERIC(5, 2) NOT NULL DEFAULT 100.0,
    last_run_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE OR REPLACE FUNCTION update_scraper_source_state_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER tr_scraper_source_state_updated_at
    BEFORE UPDATE ON scraper_source_state
    FOR EACH ROW
    EXECUTE PROCEDURE update_scraper_source_state_updated_at();
