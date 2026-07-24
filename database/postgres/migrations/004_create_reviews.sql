-- ═══════════════════════════════════════════════════════════════
-- Wakala — Migration 004 : Table reviews
-- Avis utilisateurs avec analyse de sentiment NLP
-- ═══════════════════════════════════════════════════════════════

-- ─── Enum : cible de l'avis ───────────────────────────────────
DO $$ BEGIN
    CREATE TYPE review_target_type AS ENUM ('vehicle', 'seller');
EXCEPTION WHEN duplicate_object THEN NULL;
END $$;

-- ─── Table : reviews ──────────────────────────────────────────
CREATE TABLE IF NOT EXISTS reviews (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    author_id       UUID            NOT NULL,

    -- Cible polymorphe : soit un véhicule, soit un vendeur
    target_type     review_target_type NOT NULL,
    vehicle_id      UUID,
    seller_id       UUID,

    -- Contenu de l'avis
    rating          SMALLINT        NOT NULL,
    title           VARCHAR(200),
    comment         TEXT            NOT NULL,

    -- Module NLP sentiment
    sentiment_score DECIMAL(5, 4),             -- ← NLP sentiment [-1.0, +1.0]
    sentiment_label VARCHAR(20),               -- ← 'positive', 'neutral', 'negative'
    key_phrases     TEXT[],                    -- ← Phrases clés extraites par NLP

    -- Modération
    is_approved     BOOLEAN         NOT NULL DEFAULT FALSE,
    is_flagged      BOOLEAN         NOT NULL DEFAULT FALSE,

    -- Timestamps
    created_at      TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),

    -- Contraintes
    CONSTRAINT fk_reviews_author  FOREIGN KEY (author_id)  REFERENCES users(id) ON DELETE CASCADE,
    CONSTRAINT fk_reviews_vehicle FOREIGN KEY (vehicle_id) REFERENCES vehicles(id) ON DELETE SET NULL,
    CONSTRAINT fk_reviews_seller  FOREIGN KEY (seller_id)  REFERENCES users(id) ON DELETE SET NULL,
    CONSTRAINT ck_reviews_rating  CHECK (rating >= 1 AND rating <= 5),
    CONSTRAINT ck_reviews_sentiment CHECK (
        sentiment_score IS NULL OR (sentiment_score >= -1.0 AND sentiment_score <= 1.0)
    ),
    -- Exactement une cible doit être renseignée
    CONSTRAINT ck_reviews_target CHECK (
        (target_type = 'vehicle' AND vehicle_id IS NOT NULL AND seller_id IS NULL)
        OR
        (target_type = 'seller'  AND seller_id  IS NOT NULL AND vehicle_id IS NULL)
    )
);

-- ─── Index ────────────────────────────────────────────────────
CREATE INDEX IF NOT EXISTS idx_reviews_vehicle     ON reviews (vehicle_id)  WHERE vehicle_id IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_reviews_seller      ON reviews (seller_id)   WHERE seller_id IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_reviews_author      ON reviews (author_id);
CREATE INDEX IF NOT EXISTS idx_reviews_rating      ON reviews (rating);
CREATE INDEX IF NOT EXISTS idx_reviews_sentiment   ON reviews (sentiment_score DESC) WHERE sentiment_score IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_reviews_approved    ON reviews (is_approved, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_reviews_created     ON reviews (created_at DESC);

-- Index pour la recherche textuelle sur les avis (utilisé par RAG)
CREATE INDEX IF NOT EXISTS idx_reviews_comment_trgm
    ON reviews USING gin (comment gin_trgm_ops);

-- ─── Trigger : updated_at ─────────────────────────────────────
CREATE OR REPLACE TRIGGER trg_reviews_updated_at
    BEFORE UPDATE ON reviews
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();
