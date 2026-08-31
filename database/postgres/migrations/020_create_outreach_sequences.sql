-- 020_create_outreach_sequences.sql
-- Table de séquences d'outreach 0-60 jours.
-- Stocke l'état de progression de chaque prospect dans la séquence de jalons.

CREATE TABLE IF NOT EXISTS outreach_sequences (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    prospect_id UUID NOT NULL,
    top3_vehicle_ids JSONB NOT NULL,
    sequence_started_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    current_milestone VARCHAR(10),
    next_scheduled_at TIMESTAMPTZ,
    status VARCHAR(20) NOT NULL DEFAULT 'active'
        CHECK (status IN ('active', 'stopped', 'completed')),
    stop_reason VARCHAR(100),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Index pour le DAG Airflow quotidien
CREATE INDEX IF NOT EXISTS idx_outreach_active_scheduled
    ON outreach_sequences (next_scheduled_at)
    WHERE status = 'active';

CREATE INDEX IF NOT EXISTS idx_outreach_prospect
    ON outreach_sequences (prospect_id);

COMMENT ON TABLE outreach_sequences IS
    'Séquences d''outreach 0-60 jours avec 6 jalons (J0 → J60)';
COMMENT ON COLUMN outreach_sequences.top3_vehicle_ids IS
    'IDs des véhicules recommandés (JSON array) — source de vérité pour les templates';
COMMENT ON COLUMN outreach_sequences.stop_reason IS
    'Raison d''arrêt : purchase_confirmed, test_drive_booked, consent_withdrawn, ou sequence_completed';
