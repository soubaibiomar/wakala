-- ═══════════════════════════════════════════════════════════════
-- Wakala — Migration 002 : Table vehicles
-- Catalogue véhicules avec champs pour tous les modules IA
-- ═══════════════════════════════════════════════════════════════

-- ─── Enums ────────────────────────────────────────────────────
DO $$ BEGIN
    CREATE TYPE fuel_type AS ENUM (
        'essence', 'diesel', 'hybride', 'hybride_rechargeable',
        'electrique', 'gpl', 'hydrogene'
    );
EXCEPTION WHEN duplicate_object THEN NULL;
END $$;

DO $$ BEGIN
    CREATE TYPE body_type AS ENUM (
        'citadine', 'berline', 'suv', 'break', 'coupe',
        'cabriolet', 'monospace', 'utilitaire', 'pick_up'
    );
EXCEPTION WHEN duplicate_object THEN NULL;
END $$;

DO $$ BEGIN
    CREATE TYPE transmission_type AS ENUM ('manuelle', 'automatique', 'semi_auto');
EXCEPTION WHEN duplicate_object THEN NULL;
END $$;

-- ─── Table : vehicles ─────────────────────────────────────────
CREATE TABLE IF NOT EXISTS vehicles (
    id                  UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    seller_id           UUID            NOT NULL,

    -- Identité véhicule
    brand               VARCHAR(100)    NOT NULL,
    model               VARCHAR(100)    NOT NULL,
    version             VARCHAR(200),              -- Ex: "GT Line 1.6 BlueHDi 130"
    year                INTEGER         NOT NULL,
    mileage             INTEGER         NOT NULL,
    fuel_type           fuel_type       NOT NULL,
    body_type           body_type       NOT NULL,
    transmission        transmission_type NOT NULL DEFAULT 'manuelle',
    engine_power_hp     INTEGER,
    color               VARCHAR(50),
    doors               SMALLINT        DEFAULT 5,
    seats               SMALLINT        DEFAULT 5,

    -- Localisation
    city                VARCHAR(150)    NOT NULL,
    postal_code         VARCHAR(10),
    latitude            DECIMAL(10, 7),
    longitude           DECIMAL(10, 7),

    -- Prix
    price               DECIMAL(12, 2)  NOT NULL,
    predicted_price     DECIMAL(12, 2),            -- ← Module pricing (XGBoost)
    price_confidence    DECIMAL(5, 4),             -- ← Intervalle de confiance [0, 1]

    -- Scores IA
    condition_score     DECIMAL(5, 2),             -- ← Module vision (analyse photos)
    popularity_score    DECIMAL(8, 4),             -- ← Neo4j PageRank (graphe similarité)

    -- Description
    description         TEXT,

    -- Timestamps
    created_at          TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at          TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),

    -- Contraintes
    CONSTRAINT fk_vehicles_seller FOREIGN KEY (seller_id) REFERENCES users(id) ON DELETE CASCADE,
    CONSTRAINT ck_vehicles_year   CHECK (year >= 1950 AND year <= EXTRACT(YEAR FROM NOW()) + 1),
    CONSTRAINT ck_vehicles_price  CHECK (price > 0),
    CONSTRAINT ck_vehicles_mileage CHECK (mileage >= 0),
    CONSTRAINT ck_vehicles_condition CHECK (condition_score IS NULL OR (condition_score >= 0 AND condition_score <= 100)),
    CONSTRAINT ck_vehicles_price_conf CHECK (price_confidence IS NULL OR (price_confidence >= 0 AND price_confidence <= 1))
);

-- ─── Index ────────────────────────────────────────────────────
CREATE INDEX IF NOT EXISTS idx_vehicles_seller     ON vehicles (seller_id);
CREATE INDEX IF NOT EXISTS idx_vehicles_brand      ON vehicles (brand);
CREATE INDEX IF NOT EXISTS idx_vehicles_brand_model ON vehicles (brand, model);
CREATE INDEX IF NOT EXISTS idx_vehicles_fuel       ON vehicles (fuel_type);
CREATE INDEX IF NOT EXISTS idx_vehicles_body       ON vehicles (body_type);
CREATE INDEX IF NOT EXISTS idx_vehicles_price      ON vehicles (price);
CREATE INDEX IF NOT EXISTS idx_vehicles_year       ON vehicles (year DESC);
CREATE INDEX IF NOT EXISTS idx_vehicles_city       ON vehicles (city);
CREATE INDEX IF NOT EXISTS idx_vehicles_created    ON vehicles (created_at DESC);

-- Index composite pour les requêtes courantes du moteur de recommandation
CREATE INDEX IF NOT EXISTS idx_vehicles_reco_filter
    ON vehicles (fuel_type, body_type, price, year)
    WHERE price > 0;

-- Index trigram pour la recherche textuelle fuzzy sur description
CREATE INDEX IF NOT EXISTS idx_vehicles_desc_trgm
    ON vehicles USING gin (description gin_trgm_ops);

-- ─── Trigger : updated_at ─────────────────────────────────────
CREATE OR REPLACE TRIGGER trg_vehicles_updated_at
    BEFORE UPDATE ON vehicles
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();
