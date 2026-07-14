// ═══════════════════════════════════════════════════════════════
// AutoMind — Neo4j 004 : PageRank Setup (Graph Data Science)
// Calcule la popularité des véhicules via le graphe SIMILAR_TO
// ═══════════════════════════════════════════════════════════════
//
// PRÉREQUIS : Plugin Neo4j Graph Data Science (GDS) installé.
//             Inclus dans le docker-compose via NEO4J_PLUGINS.
//
// USAGE :
//   1. Exécuter ce script après 001, 002, 003
//   2. Planifier un rafraîchissement via Airflow (DAG daily_pipeline)
//
// ═══════════════════════════════════════════════════════════════

// ─── Étape 1 : Nettoyer les projections précédentes ──────────
// Supprime le graphe projeté s'il existe (idempotent)
CALL gds.graph.exists('automind-vehicle-similarity')
YIELD exists
WITH exists
WHERE exists
CALL gds.graph.drop('automind-vehicle-similarity')
YIELD graphName
RETURN graphName + ' supprimé' AS status;

// ─── Étape 2 : Projeter le graphe pondéré ────────────────────
// Projette les nœuds Vehicle et les relations SIMILAR_TO
// avec le score de similarité comme poids de la relation

CALL gds.graph.project(
    'automind-vehicle-similarity',           // Nom du graphe projeté
    'Vehicle',                                // Nœuds à inclure
    {
        SIMILAR_TO: {
            type: 'SIMILAR_TO',
            orientation: 'UNDIRECTED',        // La similarité est symétrique
            properties: {
                score: {
                    property: 'score',
                    defaultValue: 0.5          // Poids par défaut si absent
                }
            }
        }
    }
)
YIELD graphName, nodeCount, relationshipCount
RETURN graphName, nodeCount, relationshipCount;

// ─── Étape 3 : Estimer la mémoire nécessaire (optionnel) ────
CALL gds.pageRank.write.estimate(
    'automind-vehicle-similarity',
    {
        writeProperty: 'popularity_score',
        relationshipWeightProperty: 'score',
        maxIterations: 30,
        dampingFactor: 0.85
    }
)
YIELD requiredMemory, nodeCount, relationshipCount
RETURN requiredMemory, nodeCount, relationshipCount;

// ─── Étape 4 : Exécuter PageRank pondéré ─────────────────────
// Le score est écrit directement sur le nœud Vehicle.popularity_score
// Plus un véhicule est connecté à des véhicules populaires/similaires,
// plus son score est élevé → visibilité accrue dans le catalogue.

CALL gds.pageRank.write(
    'automind-vehicle-similarity',
    {
        writeProperty: 'popularity_score',
        relationshipWeightProperty: 'score',
        maxIterations: 30,
        dampingFactor: 0.85,
        tolerance: 0.0001,
        concurrency: 4
    }
)
YIELD nodePropertiesWritten, ranIterations, didConverge, centralityDistribution
RETURN
    nodePropertiesWritten,
    ranIterations,
    didConverge,
    centralityDistribution.min  AS min_score,
    centralityDistribution.max  AS max_score,
    centralityDistribution.mean AS mean_score;

// ─── Étape 5 : Vérification — Top 10 véhicules populaires ───
MATCH (v:Vehicle)
WHERE v.popularity_score IS NOT NULL
RETURN v.id, v.brand, v.model, v.year, v.price, v.popularity_score
ORDER BY v.popularity_score DESC
LIMIT 10;

// ─── Étape 6 (optionnel) : Community Detection ──────────────
// Détecte des clusters de véhicules similaires (utile pour le matchmaker)
// Décommentez si le module matchmaker est actif.

// CALL gds.louvain.write(
//     'automind-vehicle-similarity',
//     {
//         writeProperty: 'community_id',
//         relationshipWeightProperty: 'score',
//         includeIntermediateCommunities: false
//     }
// )
// YIELD communityCount, modularity
// RETURN communityCount, modularity;

// ─── Étape 7 : Nettoyer la projection (libérer la mémoire) ──
CALL gds.graph.drop('automind-vehicle-similarity')
YIELD graphName
RETURN graphName + ' libéré — PageRank terminé' AS status;
