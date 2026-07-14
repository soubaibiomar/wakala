-- ═══════════════════════════════════════════════════════════════
-- AutoMind — Migration 003 : Table listings
-- Annonces publiées avec gestion du cycle de vie et anti-fraude
-- ═══════════════════════════════════════════════════════════════

-- ─── Enum : statut d'annonce ──────────────────────────────────
DO $$ BEGIN
    CREATE TYPE listing_status AS ENUM ('draft', 'active', 'sold', 'expired', 'flagged');
EXCEPTION WHEN duplicate_object THEN NULL;
END $$;

-- ─── Table : listings ─────────────────────────────────────────
CREATE TABLE IF NOT EXISTS listings (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    vehicle_id      UUID            NOT NULL,

    -- Statut et cycle de vie
    status          listing_status  NOT NULL DEFAULT 'draft',
    published_at    TIMESTAMP WITH TIME ZONE,
    sold_at         TIMESTAMP WITH TIME ZONE,
    expires_at      TIMESTAMP WITH TIME ZONE,

    -- Module anti-fraude
    fraud_score     DECIMAL(5, 4),             -- ← Isolation Forest [0, 1] (1 = très suspect)
    fraud_flags     JSONB       NOT NULL DEFAULT '[]',  -- Raisons détaillées du flagging
    is_manually_reviewed BOOLEAN NOT NULL DEFAULT FALSE,

    -- Média
    images_urls     TEXT[]      NOT NULL DEFAULT '{}',
    thumbnail_url   TEXT,
    video_url       TEXT,

    -- Statistiques
    view_count      INTEGER     NOT NULL DEFAULT 0,
    contact_count   INTEGER     NOT NULL DEFAULT 0,
    favorite_count  INTEGER     NOT NULL DEFAULT 0,

    -- Promotion / Boost
    is_boosted      BOOLEAN     NOT NULL DEFAULT FALSE,
    boost_expires_at TIMESTAMP WITH TIME ZONE,

    -- Timestamps
    created_at      TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),

    -- Contraintes
    CONSTRAINT fk_listings_vehicle FOREIGN KEY (vehicle_id) REFERENCES vehicles(id) ON DELETE CASCADE,
    CONSTRAINT ck_listings_fraud   CHECK (fraud_score IS NULL OR (fraud_score >= 0 AND fraud_score <= 1)),
    CONSTRAINT ck_listings_sold    CHECK (
        (status != 'sold') OR (sold_at IS NOT NULL)
    ),
    CONSTRAINT ck_listings_published CHECK (
        (status = 'draft') OR (published_at IS NOT NULL)
    )
);

-- ─── Index ────────────────────────────────────────────────────
CREATE INDEX IF NOT EXISTS idx_listings_vehicle      ON listings (vehicle_id);
CREATE INDEX IF NOT EXISTS idx_listings_status        ON listings (status);
CREATE INDEX IF NOT EXISTS idx_listings_active        ON listings (status, created_at DESC) WHERE status = 'active';
CREATE INDEX IF NOT EXISTS idx_listings_fraud_suspect ON listings (fraud_score DESC) WHERE fraud_score > 0.5;
CREATE INDEX IF NOT EXISTS idx_listings_flagged       ON listings (status) WHERE status = 'flagged';
CREATE INDEX IF NOT EXISTS idx_listings_boosted       ON listings (is_boosted, boost_expires_at) WHERE is_boosted = TRUE;
CREATE INDEX IF NOT EXISTS idx_listings_published     ON listings (published_at DESC);

-- ─── Trigger : updated_at ─────────────────────────────────────
CREATE OR REPLACE TRIGGER trg_listings_updated_at
    BEFORE UPDATE ON listings
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- ─── Trigger : publier = mettre published_at ──────────────────
CREATE OR REPLACE FUNCTION set_published_at()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.status = 'active' AND OLD.status = 'draft' AND NEW.published_at IS NULL THEN
        NEW.published_at = NOW();
    END IF;
    IF NEW.status = 'sold' AND OLD.status != 'sold' AND NEW.sold_at IS NULL THEN
        NEW.sold_at = NOW();
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE TRIGGER trg_listings_publish
    BEFORE UPDATE ON listings
    FOR EACH ROW
    EXECUTE FUNCTION set_published_at();
