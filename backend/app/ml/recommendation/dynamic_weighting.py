"""
ml/recommendation/dynamic_weighting.py — Transforme le profil de besoin
en pondération des 8 dimensions Wakala.

Logique du document de référence :
- Famille nombreuse → poids fort sur Espace + Sécurité
- Jeune actif urbain → poids fort sur Prix d'accès + Praticité urbaine
- Routier longue distance → poids fort sur Coût réel + Performance + Sécurité
- etc.

Réutilise la structure de wakala_scorer.py PROFILE_WEIGHTS, mais mappée
sur les 8 dimensions du document au lieu des 9 critères originaux.
"""

from typing import Optional

from app.rag.needs_profile_schema import NeedsProfile, VALID_DIMENSIONS


# Les 8 dimensions avec leur clé
DIMENSIONS = [
    "espace", "securite", "cout_reel", "prix_acces",
    "praticite_urbaine", "performance", "ecologie", "motricite",
]

# ══════════════════════════════════════════════════════════════════
# Profils-types avec pondérations (somme = 1.0)
# ══════════════════════════════════════════════════════════════════

PERSONA_WEIGHTS: dict[str, dict[str, float]] = {
    # Famille nombreuse : espace + sécurité dominants
    "famille_nombreuse": {
        "espace": 0.25, "securite": 0.25, "cout_reel": 0.15,
        "prix_acces": 0.10, "praticite_urbaine": 0.05,
        "performance": 0.05, "ecologie": 0.10, "motricite": 0.05,
    },
    # Jeune actif urbain : prix + praticité
    "jeune_actif_urbain": {
        "espace": 0.05, "securite": 0.10, "cout_reel": 0.15,
        "prix_acces": 0.25, "praticite_urbaine": 0.25,
        "performance": 0.05, "ecologie": 0.10, "motricite": 0.05,
    },
    # Routier longue distance : coût réel + performance + sécurité
    "routier_longue_distance": {
        "espace": 0.10, "securite": 0.20, "cout_reel": 0.25,
        "prix_acces": 0.05, "praticite_urbaine": 0.05,
        "performance": 0.15, "ecologie": 0.10, "motricite": 0.10,
    },
    # Écolo convaincu : écologie + coût réel
    "ecolo": {
        "espace": 0.05, "securite": 0.10, "cout_reel": 0.20,
        "prix_acces": 0.10, "praticite_urbaine": 0.10,
        "performance": 0.05, "ecologie": 0.30, "motricite": 0.10,
    },
    # Amateur de conduite : performance + motricité
    "conducteur_passionné": {
        "espace": 0.05, "securite": 0.10, "cout_reel": 0.05,
        "prix_acces": 0.10, "praticite_urbaine": 0.05,
        "performance": 0.30, "ecologie": 0.05, "motricite": 0.30,
    },
    # Professionnel : coût réel + espace + praticité
    "professionnel": {
        "espace": 0.20, "securite": 0.10, "cout_reel": 0.25,
        "prix_acces": 0.15, "praticite_urbaine": 0.15,
        "performance": 0.05, "ecologie": 0.05, "motricite": 0.05,
    },
    # Profil neutre (par défaut) : équilibré
    "neutre": {
        "espace": 0.125, "securite": 0.125, "cout_reel": 0.125,
        "prix_acces": 0.125, "praticite_urbaine": 0.125,
        "performance": 0.125, "ecologie": 0.125, "motricite": 0.125,
    },
}

# Mapping usage → persona
USAGE_TO_PERSONA: dict[str, str] = {
    "ville": "jeune_actif_urbain",
    "route": "routier_longue_distance",
    "mixte": "neutre",
    "offroad": "conducteur_passionné",
}

# Boost appliqué aux priorités explicites (+15%)
PRIORITY_BOOST = 0.15


def _detect_persona(profile: NeedsProfile) -> str:
    """
    Détecte automatiquement le persona à partir du profil de besoin.
    Logique heuristique basée sur les champs remplis.
    """
    # Si nb_passagers >= 5 → famille nombreuse
    if profile.nb_passagers and profile.nb_passagers >= 5:
        return "famille_nombreuse"

    # Si des priorités explicites orientent vers un persona
    if profile.priorities:
        prio_set = set(profile.priorities)
        if "ecologie" in prio_set:
            return "ecolo"
        if "performance" in prio_set and "motricite" in prio_set:
            return "conducteur_passionné"

    # Si usage spécifié
    if profile.usage:
        return USAGE_TO_PERSONA.get(profile.usage, "neutre")

    # Si budget très faible → jeune actif
    if profile.budget_max and profile.budget_max < 180000:
        return "jeune_actif_urbain"

    # Si nb_passagers >= 3 + contraintes famille
    if profile.nb_passagers and profile.nb_passagers >= 3:
        return "famille_nombreuse"

    return "neutre"


def compute_dynamic_weights(profile: NeedsProfile) -> dict[str, float]:
    """
    Calcule les pondérations dynamiques des 8 dimensions à partir du profil.

    1. Détermine le persona de base
    2. Applique les boosters pour les priorités explicites (+15%)
    3. Normalise à 100%
    """
    # 1. Persona de base
    persona = _detect_persona(profile)
    weights = PERSONA_WEIGHTS.get(persona, PERSONA_WEIGHTS["neutre"]).copy()

    # 2. Boosters de priorité explicite
    if profile.priorities:
        for priority in profile.priorities:
            if priority in weights:
                weights[priority] += PRIORITY_BOOST

    # 3. Ajustements selon les contraintes textuelles
    for constraint in (profile.constraints or []):
        c_lower = constraint.lower()
        if "consommation" in c_lower or "conso" in c_lower:
            weights["cout_reel"] += 0.10
        if "parking" in c_lower or "manoeuvre" in c_lower:
            weights["praticite_urbaine"] += 0.10
        if "pollution" in c_lower or "co2" in c_lower:
            weights["ecologie"] += 0.10

    # 4. Normalisation à 1.0
    total = sum(weights.values())
    if total > 0:
        weights = {k: round(v / total, 4) for k, v in weights.items()}

    return weights


def compute_dynamic_weights_from_query(query: dict) -> dict[str, float]:
    """
    Version alternative qui accepte le dict de requête du consultative_flow.
    Convertit en NeedsProfile puis calcule les poids.
    """
    profile = NeedsProfile(
        usage=query.get("usage"),
        budget_max=query.get("budget_max"),
        nb_passagers=query.get("nb_passagers"),
        priorities=query.get("priorities", []),
        constraints=query.get("constraints", []),
        fuel_preference=query.get("fuel_type"),
        body_type_preference=query.get("body_type"),
        brand_preference=query.get("brand"),
    )
    return compute_dynamic_weights(profile)
