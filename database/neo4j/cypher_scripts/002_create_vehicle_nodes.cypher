// ═══════════════════════════════════════════════════════════════
// AutoMind — Neo4j 002 : Création des nœuds
// Idempotent via MERGE — peut être ré-exécuté sans risque
// ═══════════════════════════════════════════════════════════════

// ─── Nœuds : Brands (Marques) ─────────────────────────────────
// Marques françaises
MERGE (b:Brand {name: 'Peugeot'})     SET b.country = 'France',     b.group = 'Stellantis';
MERGE (b:Brand {name: 'Renault'})     SET b.country = 'France',     b.group = 'Renault Group';
MERGE (b:Brand {name: 'Citroën'})     SET b.country = 'France',     b.group = 'Stellantis';
MERGE (b:Brand {name: 'Dacia'})       SET b.country = 'Roumanie',   b.group = 'Renault Group';
MERGE (b:Brand {name: 'DS'})          SET b.country = 'France',     b.group = 'Stellantis';

// Marques allemandes
MERGE (b:Brand {name: 'BMW'})         SET b.country = 'Allemagne',  b.group = 'BMW Group';
MERGE (b:Brand {name: 'Mercedes'})    SET b.country = 'Allemagne',  b.group = 'Mercedes-Benz AG';
MERGE (b:Brand {name: 'Audi'})        SET b.country = 'Allemagne',  b.group = 'Volkswagen AG';
MERGE (b:Brand {name: 'Volkswagen'})  SET b.country = 'Allemagne',  b.group = 'Volkswagen AG';

// Marques asiatiques
MERGE (b:Brand {name: 'Toyota'})      SET b.country = 'Japon',      b.group = 'Toyota Motor';
MERGE (b:Brand {name: 'Hyundai'})     SET b.country = 'Corée du Sud', b.group = 'Hyundai Motor';
MERGE (b:Brand {name: 'Kia'})         SET b.country = 'Corée du Sud', b.group = 'Hyundai Motor';

// Marques électriques
MERGE (b:Brand {name: 'Tesla'})       SET b.country = 'États-Unis', b.group = 'Tesla Inc';

// ─── Nœuds : Segments acheteurs ──────────────────────────────
MERGE (s:Segment {name: 'Jeune actif'})
    SET s.budget_range_min = 5000,
        s.budget_range_max = 18000,
        s.preferred_fuel   = 'essence',
        s.preferred_body   = 'citadine',
        s.description      = 'Premier achat, petit budget, trajet urbain';

MERGE (s:Segment {name: 'Famille'})
    SET s.budget_range_min = 18000,
        s.budget_range_max = 40000,
        s.preferred_fuel   = 'diesel',
        s.preferred_body   = 'suv',
        s.description      = 'Espace, sécurité, polyvalence';

MERGE (s:Segment {name: 'Premium'})
    SET s.budget_range_min = 35000,
        s.budget_range_max = 90000,
        s.preferred_fuel   = 'hybride',
        s.preferred_body   = 'berline',
        s.description      = 'Confort, prestige, équipements haut de gamme';

MERGE (s:Segment {name: 'Eco-responsable'})
    SET s.budget_range_min = 15000,
        s.budget_range_max = 50000,
        s.preferred_fuel   = 'electrique',
        s.preferred_body   = 'citadine',
        s.description      = 'Faible empreinte carbone, électrique ou hybride';

MERGE (s:Segment {name: 'Utilitaire pro'})
    SET s.budget_range_min = 12000,
        s.budget_range_max = 35000,
        s.preferred_fuel   = 'diesel',
        s.preferred_body   = 'utilitaire',
        s.description      = 'Usage professionnel, robustesse, charge utile';

// ─── Nœuds : Véhicules de démonstration ──────────────────────
MERGE (v:Vehicle {id: 'demo-001'})
    SET v.brand      = 'Dacia',
        v.model      = 'Sandero',
        v.year       = 2024,
        v.price      = 115000,
        v.mileage    = 2000,
        v.fuel_type  = 'gpl',
        v.body_type  = 'citadine',
        v.city       = 'Casablanca',
        v.popularity_score = 4.5;

MERGE (v:Vehicle {id: 'demo-002'})
    SET v.brand      = 'Renault',
        v.model      = 'Captur',
        v.year       = 2023,
        v.price      = 220000,
        v.mileage    = 12000,
        v.fuel_type  = 'hybride',
        v.body_type  = 'suv',
        v.city       = 'Rabat',
        v.popularity_score = 4.2;

MERGE (v:Vehicle {id: 'demo-003'})
    SET v.brand      = 'Dacia',
        v.model      = 'Duster',
        v.year       = 2023,
        v.price      = 180000,
        v.mileage    = 15000,
        v.fuel_type  = 'diesel',
        v.body_type  = 'suv',
        v.city       = 'Marrakech',
        v.popularity_score = 4.8;

MERGE (v:Vehicle {id: 'demo-004'})
    SET v.brand      = 'Peugeot',
        v.model      = '301',
        v.year       = 2022,
        v.price      = 140000,
        v.mileage    = 35000,
        v.fuel_type  = 'essence',
        v.body_type  = 'berline',
        v.city       = 'Tanger',
        v.popularity_score = 3.9;

MERGE (v:Vehicle {id: 'demo-005'})
    SET v.brand      = 'Toyota',
        v.model      = 'Hilux',
        v.year       = 2024,
        v.price      = 350000,
        v.mileage    = 10000,
        v.fuel_type  = 'diesel',
        v.body_type  = 'utilitaire',
        v.city       = 'Agadir',
        v.popularity_score = 4.6;

// ─── Nœuds : Utilisateurs de démonstration ───────────────────
MERGE (u:User {id: 'user-001'}) SET u.name = 'Hassan Alaoui',  u.role = 'buyer';
MERGE (u:User {id: 'user-002'}) SET u.name = 'Fatima Zahra',  u.role = 'buyer';
MERGE (u:User {id: 'user-003'}) SET u.name = 'Auto Premium Casablanca',  u.role = 'seller';
