-- ═══════════════════════════════════════════════════════════════
-- Wakala — Migration 006 : Table trust_scores
-- Score de confiance composite (vision + fraude + vendeur)
-- Consommé par l'affichage frontend et le matchmaker
-- ═══════════════════════════════════════════════════════════════

CREATE TABLE IF NOT EXISTS trust_scores (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    vehicle_id      UUID            NOT NULL,

    -- ─── Sous-scores (chaque module alimente le sien) ─────────
    condition_score DECIMAL(5, 2),             -- ← Module vision [0, 100]
                                               --   Analyse des photos (rayures, dommages, cohérence)
    seller_score    DECIMAL(5, 2),             -- ← Agrégation des reviews vendeur [0, 100]
                                               --   (avg rating + ancienneté + nb ventes réussies)
    fraud_score     DECIMAL(5, 2),             -- ← Module anti-fraude [0, 100] (100 = sûr, inversé du listing.fraud_score)
                                               --   Isolation Forest transformé en score de confiance
    price_fairness  DECIMAL(5, 2),             -- ← Module pricing [0, 100]
                                               --   Écart prix affiché vs prix prédit (plus le prix est juste, plus c'est haut)
    listing_quality DECIMAL(5, 2),             -- ← Qualité de l'annonce [0, 100]
                                               --   (nb photos, description remplie, complétude des champs)

    -- ─── Score composite ──────────────────────────────────────
    computed_score  DECIMAL(5, 2)   NOT NULL,  -- Moyenne pondérée des sous-scores
    confidence      DECIMAL(5, 4)   NOT NULL DEFAULT 0.0,  -- [0, 1] — Quelle proportion des sous-scores est disponible

    -- ─── Pondérations utilisées (pour auditabilité) ──────────
    weights_used    JSONB           NOT NULL DEFAULT '{
        "condition": 0.25,
        "seller": 0.25,
        "fraud": 0.25,
        "price_fairness": 0.15,
        "listing_quality": 0.10
    }',

    -- ─── Métadonnées ──────────────────────────────────────────
    computation_version VARCHAR(20) NOT NULL DEFAULT 'v1.0',  -- Versioning de l'algorithme
    updated_at      TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    created_at      TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),

    -- Contraintes
    CONSTRAINT fk_trust_vehicle FOREIGN KEY (vehicle_id) REFERENCES vehicles(id) ON DELETE CASCADE,
    CONSTRAINT uq_trust_vehicle UNIQUE (vehicle_id),  -- Un seul score par véhicule
    CONSTRAINT ck_trust_computed   CHECK (computed_score  >= 0 AND computed_score  <= 100),
    CONSTRAINT ck_trust_condition  CHECK (condition_score IS NULL OR (condition_score >= 0 AND condition_score <= 100)),
    CONSTRAINT ck_trust_seller     CHECK (seller_score    IS NULL OR (seller_score    >= 0 AND seller_score    <= 100)),
    CONSTRAINT ck_trust_fraud      CHECK (fraud_score     IS NULL OR (fraud_score     >= 0 AND fraud_score     <= 100)),
    CONSTRAINT ck_trust_price      CHECK (price_fairness  IS NULL OR (price_fairness  >= 0 AND price_fairness  <= 100)),
    CONSTRAINT ck_trust_listing    CHECK (listing_quality  IS NULL OR (listing_quality  >= 0 AND listing_quality  <= 100)),
    CONSTRAINT ck_trust_confidence CHECK (confidence >= 0 AND confidence <= 1)
);

-- ─── Index ────────────────────────────────────────────────────
CREATE INDEX IF NOT EXISTS idx_trust_vehicle   ON trust_scores (vehicle_id);
CREATE INDEX IF NOT EXISTS idx_trust_computed  ON trust_scores (computed_score DESC);
CREATE INDEX IF NOT EXISTS idx_trust_updated   ON trust_scores (updated_at DESC);
-- Index partiel pour les véhicules à score élevé (affichés en priorité)
CREATE INDEX IF NOT EXISTS idx_trust_high
    ON trust_scores (computed_score DESC)
    WHERE computed_score >= 80;
-- Index partiel pour les véhicules suspects (dashboard vendeur)
CREATE INDEX IF NOT EXISTS idx_trust_low
    ON trust_scores (computed_score ASC)
    WHERE computed_score < 40;

-- ─── Trigger : updated_at ─────────────────────────────────────
CREATE OR REPLACE TRIGGER trg_trust_updated_at
    BEFORE UPDATE ON trust_scores
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- ─── Fonction : recalcul du score composite ───────────────────
-- Appelée par le backend après mise à jour d'un sous-score
CREATE OR REPLACE FUNCTION recompute_trust_score(p_vehicle_id UUID)
RETURNS DECIMAL AS $$
DECLARE
    v_condition  DECIMAL;
    v_seller     DECIMAL;
    v_fraud      DECIMAL;
    v_price      DECIMAL;
    v_listing    DECIMAL;
    v_score      DECIMAL;
    v_total_w    DECIMAL := 0;
    v_weighted   DECIMAL := 0;
    v_confidence DECIMAL;
    v_count      INTEGER := 0;
BEGIN
    SELECT condition_score, seller_score, fraud_score, price_fairness, listing_quality
    INTO v_condition, v_seller, v_fraud, v_price, v_listing
    FROM trust_scores WHERE vehicle_id = p_vehicle_id;

    -- Pondération dynamique : seuls les sous-scores non-NULL comptent
    IF v_condition IS NOT NULL THEN
        v_weighted := v_weighted + v_condition * 0.25;
        v_total_w  := v_total_w + 0.25;
        v_count    := v_count + 1;
    END IF;
    IF v_seller IS NOT NULL THEN
        v_weighted := v_weighted + v_seller * 0.25;
        v_total_w  := v_total_w + 0.25;
        v_count    := v_count + 1;
    END IF;
    IF v_fraud IS NOT NULL THEN
        v_weighted := v_weighted + v_fraud * 0.25;
        v_total_w  := v_total_w + 0.25;
        v_count    := v_count + 1;
    END IF;
    IF v_price IS NOT NULL THEN
        v_weighted := v_weighted + v_price * 0.15;
        v_total_w  := v_total_w + 0.15;
        v_count    := v_count + 1;
    END IF;
    IF v_listing IS NOT NULL THEN
        v_weighted := v_weighted + v_listing * 0.10;
        v_total_w  := v_total_w + 0.10;
        v_count    := v_count + 1;
    END IF;

    -- Normaliser par les poids effectifs
    IF v_total_w > 0 THEN
        v_score := ROUND(v_weighted / v_total_w, 2);
    ELSE
        v_score := 0;
    END IF;

    -- Confiance = proportion de sous-scores disponibles (5 au total)
    v_confidence := ROUND(v_count::DECIMAL / 5.0, 4);

    UPDATE trust_scores
    SET computed_score = v_score,
        confidence = v_confidence,
        updated_at = NOW()
    WHERE vehicle_id = p_vehicle_id;

    RETURN v_score;
END;
$$ LANGUAGE plpgsql;
