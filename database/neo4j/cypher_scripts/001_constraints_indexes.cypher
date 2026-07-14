// ═══════════════════════════════════════════════════════════════
// AutoMind — Neo4j 001 : Contraintes et Index
// Exécuter en premier pour garantir l'intégrité du graphe
// ═══════════════════════════════════════════════════════════════

// ─── Contraintes d'unicité ────────────────────────────────────
// Garantissent qu'aucun doublon ne peut être créé par les MERGE

CREATE CONSTRAINT vehicle_id_unique IF NOT EXISTS
    FOR (v:Vehicle) REQUIRE v.id IS UNIQUE;

CREATE CONSTRAINT brand_name_unique IF NOT EXISTS
    FOR (b:Brand) REQUIRE b.name IS UNIQUE;

CREATE CONSTRAINT user_id_unique IF NOT EXISTS
    FOR (u:User) REQUIRE u.id IS UNIQUE;

CREATE CONSTRAINT segment_name_unique IF NOT EXISTS
    FOR (s:Segment) REQUIRE s.name IS UNIQUE;

// ─── Index de performance ─────────────────────────────────────
// Accélèrent les requêtes de traversée du graphe

// Recherche par marque/modèle (recommandation content-based)
CREATE INDEX vehicle_brand_idx IF NOT EXISTS
    FOR (v:Vehicle) ON (v.brand);

CREATE INDEX vehicle_model_idx IF NOT EXISTS
    FOR (v:Vehicle) ON (v.model);

CREATE INDEX vehicle_year_idx IF NOT EXISTS
    FOR (v:Vehicle) ON (v.year);

CREATE INDEX vehicle_price_idx IF NOT EXISTS
    FOR (v:Vehicle) ON (v.price);

CREATE INDEX vehicle_fuel_idx IF NOT EXISTS
    FOR (v:Vehicle) ON (v.fuel_type);

CREATE INDEX vehicle_body_idx IF NOT EXISTS
    FOR (v:Vehicle) ON (v.body_type);

// Recherche par popularité (PageRank, trié pour le catalogue)
CREATE INDEX vehicle_popularity_idx IF NOT EXISTS
    FOR (v:Vehicle) ON (v.popularity_score);

// Index composites pour les requêtes de recommandation
CREATE INDEX vehicle_brand_price_idx IF NOT EXISTS
    FOR (v:Vehicle) ON (v.brand, v.price);

// Recherche utilisateur pour les parcours de navigation
CREATE INDEX user_name_idx IF NOT EXISTS
    FOR (u:User) ON (u.name);

// Index full-text pour la recherche textuelle dans le graphe
CREATE FULLTEXT INDEX vehicle_fulltext IF NOT EXISTS
    FOR (v:Vehicle) ON EACH [v.brand, v.model, v.city];
