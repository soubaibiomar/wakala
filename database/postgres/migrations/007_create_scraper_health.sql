-- 007_create_scraper_health.sql
-- Table pour stocker les métriques de succès des scrapers

CREATE TABLE IF NOT EXISTS scraper_health (
    id SERIAL PRIMARY KEY,
    site VARCHAR(50) NOT NULL,
    run_timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    success_rate NUMERIC(5, 2) NOT NULL,
    field_success_rates JSONB NOT NULL,
    total_attempted INTEGER NOT NULL,
    total_valid INTEGER NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_scraper_health_site_run ON scraper_health(site, run_timestamp DESC);
