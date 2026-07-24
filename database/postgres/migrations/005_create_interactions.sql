-- ═══════════════════════════════════════════════════════════════
-- Wakala — Migration 005 : Table interactions
-- Événements utilisateur pour le collaborative filtering
-- Alimentée en continu par Kafka, source du re-training ML
-- ═══════════════════════════════════════════════════════════════

-- ─── Enum : type d'action ─────────────────────────────────────
DO $$ BEGIN
    CREATE TYPE action_type AS ENUM (
        'view',         -- Page détail consultée
        'click',        -- Clic depuis le catalogue
        'favorite',     -- Ajouté aux favoris
        'unfavorite',   -- Retiré des favoris
        'contact',      -- Contact vendeur
        'share',        -- Partage du lien
        'search',       -- Recherche ayant mené à ce véhicule
        'recommendation_click'  -- Clic sur une recommandation IA
    );
EXCEPTION WHEN duplicate_object THEN NULL;
END $$;

-- ─── Table : interactions ─────────────────────────────────────
CREATE TABLE IF NOT EXISTS interactions (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id         UUID            NOT NULL,
    vehicle_id      UUID            NOT NULL,
    action          action_type     NOT NULL,

    -- Contexte de l'interaction (pour le collaborative filtering)
    session_id      VARCHAR(64),                -- Session de navigation
    source          VARCHAR(50),                -- 'search', 'catalogue', 'recommendation', 'chatbot'
    search_query    TEXT,                       -- Requête de recherche originale (si source = 'search')
    recommendation_method VARCHAR(30),          -- 'content-based', 'collaborative', 'hybrid' (si source = 'recommendation')

    -- Durée (pour les vues)
    duration_seconds INTEGER,                   -- Temps passé sur la page (action = 'view')

    -- Device
    device_type     VARCHAR(20),                -- 'desktop', 'mobile', 'tablet'
    user_agent      TEXT,

    -- Timestamp précis (pour séries temporelles Kafka)
    timestamp       TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),

    -- Contraintes
    CONSTRAINT fk_interactions_user    FOREIGN KEY (user_id)    REFERENCES users(id) ON DELETE CASCADE,
    CONSTRAINT fk_interactions_vehicle FOREIGN KEY (vehicle_id) REFERENCES vehicles(id) ON DELETE CASCADE,
    CONSTRAINT ck_interactions_duration CHECK (duration_seconds IS NULL OR duration_seconds >= 0)
);

-- ─── Index ────────────────────────────────────────────────────
-- Index principal pour le collaborative filtering : user → véhicules
CREATE INDEX IF NOT EXISTS idx_interactions_user_vehicle
    ON interactions (user_id, vehicle_id);

-- Index pour reconstruire la matrice user-item
CREATE INDEX IF NOT EXISTS idx_interactions_user_action
    ON interactions (user_id, action, timestamp DESC);

-- Index pour les métriques par véhicule
CREATE INDEX IF NOT EXISTS idx_interactions_vehicle_action
    ON interactions (vehicle_id, action);

-- Index temporel pour le streaming / re-training incrémental
CREATE INDEX IF NOT EXISTS idx_interactions_timestamp
    ON interactions (timestamp DESC);

-- Index partiel pour les interactions "fortes" (signal plus fiable pour le collab filtering)
CREATE INDEX IF NOT EXISTS idx_interactions_strong_signal
    ON interactions (user_id, vehicle_id, timestamp DESC)
    WHERE action IN ('favorite', 'contact', 'recommendation_click');

-- Index pour la source (analyser l'efficacité des recommandations)
CREATE INDEX IF NOT EXISTS idx_interactions_source
    ON interactions (source, timestamp DESC)
    WHERE source IS NOT NULL;

-- ─── Vue matérialisée : matrice user-item (collaborative filtering) ─
-- Rafraîchie périodiquement par le DAG Airflow
CREATE MATERIALIZED VIEW IF NOT EXISTS mv_user_item_matrix AS
SELECT
    user_id,
    vehicle_id,
    COUNT(*)                                             AS interaction_count,
    SUM(CASE WHEN action = 'view'      THEN 1 ELSE 0 END) AS views,
    SUM(CASE WHEN action = 'click'     THEN 1 ELSE 0 END) AS clicks,
    SUM(CASE WHEN action = 'favorite'  THEN 1 ELSE 0 END) AS favorites,
    SUM(CASE WHEN action = 'contact'   THEN 1 ELSE 0 END) AS contacts,
    -- Score implicite pondéré (pour le collaborative filtering)
    (
        SUM(CASE WHEN action = 'view'                 THEN 1.0 ELSE 0 END) * 0.1 +
        SUM(CASE WHEN action = 'click'                THEN 1.0 ELSE 0 END) * 0.2 +
        SUM(CASE WHEN action = 'favorite'             THEN 1.0 ELSE 0 END) * 0.5 +
        SUM(CASE WHEN action = 'contact'              THEN 1.0 ELSE 0 END) * 0.8 +
        SUM(CASE WHEN action = 'recommendation_click' THEN 1.0 ELSE 0 END) * 0.6
    ) AS implicit_rating,
    MAX(timestamp) AS last_interaction
FROM interactions
GROUP BY user_id, vehicle_id
WITH NO DATA;

-- Index sur la vue matérialisée
CREATE UNIQUE INDEX IF NOT EXISTS idx_mv_ui_user_vehicle
    ON mv_user_item_matrix (user_id, vehicle_id);
CREATE INDEX IF NOT EXISTS idx_mv_ui_rating
    ON mv_user_item_matrix (implicit_rating DESC);

-- Rafraîchir : REFRESH MATERIALIZED VIEW CONCURRENTLY mv_user_item_matrix;
