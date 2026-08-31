-- ═══════════════════════════════════════════════════════════════
-- Wakala — Migration 018 : Options, Couleurs et Notes Wakala
-- ═══════════════════════════════════════════════════════════════

-- 1. Ajout des colonnes techniques à la table vehicles
ALTER TABLE vehicles 
    ADD COLUMN IF NOT EXISTS trunk_volume_l INTEGER,
    ADD COLUMN IF NOT EXISTS ncap_rating VARCHAR(50),
    ADD COLUMN IF NOT EXISTS fuel_consumption DECIMAL(5, 2),
    ADD COLUMN IF NOT EXISTS co2_emissions DECIMAL(6, 2),
    ADD COLUMN IF NOT EXISTS length_cm INTEGER,
    ADD COLUMN IF NOT EXISTS is_4x4 BOOLEAN NOT NULL DEFAULT FALSE,
    ADD COLUMN IF NOT EXISTS engine_type VARCHAR(100),
    ADD COLUMN IF NOT EXISTS condition VARCHAR(50) NOT NULL DEFAULT 'new',
    ADD COLUMN IF NOT EXISTS source VARCHAR(100) NOT NULL DEFAULT 'wakala_catalogue';

-- Index sur les nouveaux filtres
CREATE INDEX IF NOT EXISTS idx_vehicles_condition ON vehicles(condition);
CREATE INDEX IF NOT EXISTS idx_vehicles_source ON vehicles(source);
CREATE INDEX IF NOT EXISTS idx_vehicles_is_4x4 ON vehicles(is_4x4);

-- 2. Table des scores et notes d'évaluation Wakala
CREATE TABLE IF NOT EXISTS vehicle_wakala_scores (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    vehicle_id UUID NOT NULL UNIQUE REFERENCES vehicles(id) ON DELETE CASCADE,
    
    -- Les 8 notes Wakala sur 5
    space_score DECIMAL(3, 1) CHECK (space_score IS NULL OR (space_score >= 0 AND space_score <= 5)),
    safety_score DECIMAL(3, 1) CHECK (safety_score IS NULL OR (safety_score >= 0 AND safety_score <= 5)),
    real_cost_score DECIMAL(3, 1) CHECK (real_cost_score IS NULL OR (real_cost_score >= 0 AND real_cost_score <= 5)),
    access_price_score DECIMAL(3, 1) CHECK (access_price_score IS NULL OR (access_price_score >= 0 AND access_price_score <= 5)),
    city_practicality_score DECIMAL(3, 1) CHECK (city_practicality_score IS NULL OR (city_practicality_score >= 0 AND city_practicality_score <= 5)),
    performance_score DECIMAL(3, 1) CHECK (performance_score IS NULL OR (performance_score >= 0 AND performance_score <= 5)),
    ecology_score DECIMAL(3, 1) CHECK (ecology_score IS NULL OR (ecology_score >= 0 AND ecology_score <= 5)),
    offroad_score DECIMAL(3, 1) CHECK (offroad_score IS NULL OR (offroad_score >= 0 AND offroad_score <= 5)),
    
    -- Note globale et métadonnées
    overall_score DECIMAL(3, 1) CHECK (overall_score IS NULL OR (overall_score >= 0 AND overall_score <= 5)),
    data_reliability VARCHAR(255),
    observations TEXT,
    source_note TEXT,
    
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_wakala_scores_vehicle ON vehicle_wakala_scores(vehicle_id);
CREATE INDEX IF NOT EXISTS idx_wakala_scores_overall ON vehicle_wakala_scores(overall_score DESC);

-- 3. Table des options et accessoires configurables
CREATE TABLE IF NOT EXISTS vehicle_options (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    vehicle_id UUID NOT NULL REFERENCES vehicles(id) ON DELETE CASCADE,
    category VARCHAR(50) NOT NULL, -- 'accessoire', 'couleur', 'jante', 'sellerie', 'pack'
    name VARCHAR(255) NOT NULL,
    price_delta DECIMAL(10, 2) NOT NULL DEFAULT 0.00,
    is_default BOOLEAN NOT NULL DEFAULT FALSE,
    image_reference VARCHAR(255),
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    CONSTRAINT ck_option_category CHECK (category IN ('accessoire', 'couleur', 'jante', 'sellerie', 'pack'))
);

CREATE INDEX IF NOT EXISTS idx_vehicle_options_vehicle ON vehicle_options(vehicle_id);
CREATE INDEX IF NOT EXISTS idx_vehicle_options_category ON vehicle_options(category);

-- 4. Table des coloris carrosserie disponibles
CREATE TABLE IF NOT EXISTS vehicle_colors (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    vehicle_id UUID NOT NULL REFERENCES vehicles(id) ON DELETE CASCADE,
    color_name VARCHAR(100) NOT NULL,
    hex_code VARCHAR(20) NOT NULL,
    price_delta DECIMAL(10, 2) NOT NULL DEFAULT 0.00,
    is_default BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_vehicle_colors_vehicle ON vehicle_colors(vehicle_id);
