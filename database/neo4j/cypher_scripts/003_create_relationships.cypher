// ═══════════════════════════════════════════════════════════════
// AutoMind — Neo4j 003 : Relations
// Connecte les nœuds : marques, similarités, vues, segments
// ═══════════════════════════════════════════════════════════════

// ─── SAME_BRAND : Véhicule → Marque ──────────────────────────
// Chaque véhicule est rattaché à sa marque

MATCH (v:Vehicle), (b:Brand)
WHERE v.brand = b.name
MERGE (v)-[:SAME_BRAND]->(b);

// ─── SIMILAR_TO : Véhicule ↔ Véhicule ───────────────────────
// Similarité calculée sur : même segment de prix, même body_type,
// même carburant, année proche. Score [0, 1].
// En production, ce score sera recalculé par le module ML.

// SUV diesel : 3008 ↔ Captur (même segment, carburant différent)
MATCH (v1:Vehicle {id: 'demo-001'}), (v2:Vehicle {id: 'demo-002'})
MERGE (v1)-[r:SIMILAR_TO]->(v2)
    SET r.score            = 0.78,
        r.shared_body      = 'suv',
        r.price_delta      = abs(v1.price - v2.price),
        r.computation_date = datetime();

// Captur ↔ Golf (prix proche, acheteur « Famille »)
MATCH (v1:Vehicle {id: 'demo-002'}), (v2:Vehicle {id: 'demo-004'})
MERGE (v1)-[r:SIMILAR_TO]->(v2)
    SET r.score            = 0.62,
        r.shared_body      = NULL,
        r.price_delta      = abs(v1.price - v2.price),
        r.computation_date = datetime();

// Tesla Model 3 ↔ 3008 (même gamme de prix, profil « Premium »)
MATCH (v1:Vehicle {id: 'demo-003'}), (v2:Vehicle {id: 'demo-001'})
MERGE (v1)-[r:SIMILAR_TO]->(v2)
    SET r.score            = 0.45,
        r.shared_body      = NULL,
        r.price_delta      = abs(v1.price - v2.price),
        r.computation_date = datetime();

// Golf ↔ Sandero (berline/citadine, acheteur « Jeune actif »)
MATCH (v1:Vehicle {id: 'demo-004'}), (v2:Vehicle {id: 'demo-005'})
MERGE (v1)-[r:SIMILAR_TO]->(v2)
    SET r.score            = 0.55,
        r.shared_body      = NULL,
        r.price_delta      = abs(v1.price - v2.price),
        r.computation_date = datetime();

// Relations bidirectionnelles (le graphe SIMILAR_TO est non-dirigé sémantiquement)
MATCH (v1:Vehicle {id: 'demo-002'}), (v2:Vehicle {id: 'demo-001'})
MERGE (v1)-[r:SIMILAR_TO]->(v2)
    SET r.score            = 0.78,
        r.shared_body      = 'suv',
        r.price_delta      = abs(v1.price - v2.price),
        r.computation_date = datetime();

MATCH (v1:Vehicle {id: 'demo-004'}), (v2:Vehicle {id: 'demo-002'})
MERGE (v1)-[r:SIMILAR_TO]->(v2)
    SET r.score            = 0.62,
        r.price_delta      = abs(v1.price - v2.price),
        r.computation_date = datetime();

// ─── VIEWED : Utilisateur → Véhicule ─────────────────────────
// Interactions de navigation (synchronisées depuis Kafka/PostgreSQL)
// Ces relations alimentent le collaborative filtering dans le graphe

MATCH (u:User {id: 'user-001'}), (v:Vehicle {id: 'demo-001'})
MERGE (u)-[r:VIEWED]->(v)
    SET r.count     = 3,
        r.last_at   = datetime(),
        r.favorited = true;

MATCH (u:User {id: 'user-001'}), (v:Vehicle {id: 'demo-002'})
MERGE (u)-[r:VIEWED]->(v)
    SET r.count     = 1,
        r.last_at   = datetime(),
        r.favorited = false;

MATCH (u:User {id: 'user-002'}), (v:Vehicle {id: 'demo-003'})
MERGE (u)-[r:VIEWED]->(v)
    SET r.count     = 5,
        r.last_at   = datetime(),
        r.favorited = true;

MATCH (u:User {id: 'user-002'}), (v:Vehicle {id: 'demo-001'})
MERGE (u)-[r:VIEWED]->(v)
    SET r.count     = 2,
        r.last_at   = datetime(),
        r.favorited = false;

// ─── BELONGS_TO : Utilisateur → Segment ──────────────────────
// Segment acheteur déduit par le moteur de recommandation
// (clustering sur les interactions + préférences déclarées)

MATCH (u:User {id: 'user-001'}), (s:Segment {name: 'Famille'})
MERGE (u)-[r:BELONGS_TO]->(s)
    SET r.confidence      = 0.87,
        r.assigned_at     = datetime(),
        r.assignment_method = 'clustering_v1';

MATCH (u:User {id: 'user-002'}), (s:Segment {name: 'Premium'})
MERGE (u)-[r:BELONGS_TO]->(s)
    SET r.confidence      = 0.92,
        r.assigned_at     = datetime(),
        r.assignment_method = 'clustering_v1';

// ─── TARGETS : Segment → Body type préféré ───────────────────
// Relation utile pour le matchmaker : "les familles cherchent des SUV"
// Permet des requêtes du type : "quels véhicules plairaient à ce segment ?"

MATCH (s:Segment {name: 'Famille'}), (v:Vehicle)
WHERE v.body_type = 'suv' AND v.price >= 18000 AND v.price <= 40000
MERGE (s)-[r:TARGETS]->(v)
    SET r.match_score = 0.80;

MATCH (s:Segment {name: 'Jeune actif'}), (v:Vehicle)
WHERE v.body_type = 'citadine' AND v.price <= 18000
MERGE (s)-[r:TARGETS]->(v)
    SET r.match_score = 0.85;

MATCH (s:Segment {name: 'Premium'}), (v:Vehicle)
WHERE v.price >= 35000
MERGE (s)-[r:TARGETS]->(v)
    SET r.match_score = 0.75;

MATCH (s:Segment {name: 'Eco-responsable'}), (v:Vehicle)
WHERE v.fuel_type IN ['electrique', 'hybride']
MERGE (s)-[r:TARGETS]->(v)
    SET r.match_score = 0.90;
