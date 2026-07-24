-- ═══════════════════════════════════════════════════════════════
-- Wakala — Migration 001 : Table users
-- Acheteurs et vendeurs de la marketplace
-- ═══════════════════════════════════════════════════════════════

-- Extensions requises
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";       -- Recherche textuelle fuzzy
CREATE EXTENSION IF NOT EXISTS "btree_gist";    -- Index avancés pour ranges

-- ─── Enum : rôle utilisateur ──────────────────────────────────
DO $$ BEGIN
    CREATE TYPE user_role AS ENUM ('buyer', 'seller', 'admin');
EXCEPTION WHEN duplicate_object THEN NULL;
END $$;

-- ─── Table : users ────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS users (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name            VARCHAR(255)    NOT NULL,
    email           VARCHAR(255)    NOT NULL,
    phone           VARCHAR(30),
    password_hash   VARCHAR(255)    NOT NULL,
    role            user_role       NOT NULL DEFAULT 'buyer',
    is_verified     BOOLEAN         NOT NULL DEFAULT FALSE,  -- TrustBadge vendeur vérifié
    preferences     JSONB           NOT NULL DEFAULT '{}',   -- Préférences utilisateur (budget, carburant, usage…)
    avatar_url      TEXT,
    created_at      TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),

    -- Contraintes
    CONSTRAINT uq_users_email UNIQUE (email),
    CONSTRAINT ck_users_email_format CHECK (email ~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$')
);

-- ─── Index ────────────────────────────────────────────────────
CREATE INDEX IF NOT EXISTS idx_users_email       ON users (email);
CREATE INDEX IF NOT EXISTS idx_users_role        ON users (role);
CREATE INDEX IF NOT EXISTS idx_users_is_verified ON users (is_verified) WHERE role = 'seller';
CREATE INDEX IF NOT EXISTS idx_users_created_at  ON users (created_at DESC);

-- ─── Trigger : updated_at automatique ─────────────────────────
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE TRIGGER trg_users_updated_at
    BEFORE UPDATE ON users
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- ─── Données de démonstration ─────────────────────────────────
INSERT INTO users (name, email, password_hash, role, is_verified) VALUES
    ('Auto Premium Casablanca',   'contact@autopremium.ma',        '$2b$12$placeholder_hash_1', 'seller', TRUE),
    ('Garage Alami',              'alami@garage.ma',               '$2b$12$placeholder_hash_2', 'seller', TRUE),
    ('Occasions Express Maroc',   'info@occasions-express.ma',     '$2b$12$placeholder_hash_3', 'seller', FALSE),
    ('Jean Dupont',               'jean.dupont@email.ma',          '$2b$12$placeholder_hash_4', 'buyer',  FALSE),
    ('Marie Leroy',               'marie.leroy@email.ma',          '$2b$12$placeholder_hash_5', 'buyer',  FALSE)
ON CONFLICT (email) DO NOTHING;
