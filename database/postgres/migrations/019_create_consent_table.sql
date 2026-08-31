-- 019_create_consent_table.sql
-- Table de consentement prospect conforme à la loi 09-08/CNDP.
-- Un prospect doit avoir un consentement valide (opt_out_at IS NULL)
-- avant tout message d'outreach.

CREATE TABLE IF NOT EXISTS prospect_consents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    prospect_id UUID NOT NULL,
    channel VARCHAR(20) NOT NULL CHECK (channel IN ('whatsapp', 'email', 'sms')),
    purpose VARCHAR(50) NOT NULL DEFAULT 'recommendation_outreach',
    consented_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    opt_out_at TIMESTAMPTZ,
    consent_source VARCHAR(20) NOT NULL CHECK (consent_source IN ('web', 'whatsapp', 'chatbot')),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Index pour vérification rapide avant chaque envoi d'outreach
CREATE INDEX IF NOT EXISTS idx_consent_prospect_active
    ON prospect_consents (prospect_id)
    WHERE opt_out_at IS NULL;

CREATE INDEX IF NOT EXISTS idx_consent_prospect_channel
    ON prospect_consents (prospect_id, channel);

COMMENT ON TABLE prospect_consents IS
    'Consentement explicite des prospects pour les communications outreach (loi 09-08/CNDP)';
COMMENT ON COLUMN prospect_consents.opt_out_at IS
    'Si non NULL, le consentement a été retiré à cette date. Aucun message ne peut être envoyé après.';
