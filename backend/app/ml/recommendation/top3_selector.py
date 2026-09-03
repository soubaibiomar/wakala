"""
ml/recommendation/top3_selector.py — Pipeline complet de sélection du Top 3.

1. Filtres durs (AVANT scoring) : budget, motorisation, disponibilité
2. Scoring pondéré 8 dimensions
3. Tri et sélection (diversité de marque)
4. Enrichissement : points forts + compromis explicites

PRINCIPE : Un véhicule hors budget ne doit JAMAIS apparaître dans le
classement même avec un score élevé. Filtres durs AVANT scoring.
"""

import logging
from typing import Any, Optional

from pydantic import BaseModel, Field

from app.ml.recommendation.eight_dimension_scorer import (
    EightDimensionResult,
    score_vehicle_8d,
)
from app.ml.recommendation.dynamic_weighting import compute_dynamic_weights_from_query

logger = logging.getLogger(__name__)


# ══════════════════════════════════════════════════════════════════
# Schéma de sortie structuré (Pydantic)
# ══════════════════════════════════════════════════════════════════

class RecommendedVehicle(BaseModel):
    """Un véhicule recommandé avec ses scores et justifications."""
    vehicle_id: str
    brand: str
    model: str
    version: Optional[str] = None
    price: float
    year: int
    fuel_type: Optional[str] = None
    body_type: Optional[str] = None
    transmission: Optional[str] = None
    scores: dict[str, float] = Field(
        ..., description="Les 8 dimensions (1–5 chacune)"
    )
    weighted_total: float = Field(
        ..., ge=0, description="Score total pondéré"
    )
    strengths: list[str] = Field(
        default_factory=list,
        description="Points forts textuels (dimensions ≥ 4/5)",
    )
    compromises: list[str] = Field(
        default_factory=list,
        description="Compromis explicites (dimensions < 3/5)",
    )
    budget_margin: Optional[float] = Field(
        None,
        description="Marge par rapport au budget max (positif = sous le budget)",
    )


class Top3Result(BaseModel):
    """Résultat complet du Top 3."""
    vehicles: list[RecommendedVehicle]
    total_candidates: int = Field(
        ..., description="Nombre de véhicules après filtres durs",
    )
    relaxed_filter: Optional[str] = Field(
        None,
        description="Filtre relâché si moins de 3 candidats stricts",
    )


# ══════════════════════════════════════════════════════════════════
# Labels humains pour les dimensions
# ══════════════════════════════════════════════════════════════════

DIMENSION_LABELS: dict[str, str] = {
    "espace": "Espace & coffre",
    "securite": "Sécurité",
    "cout_reel": "Coût réel d'usage",
    "prix_acces": "Prix d'accès",
    "praticite_urbaine": "Praticité urbaine",
    "performance": "Performance",
    "ecologie": "Écologie",
    "motricite": "Motricité (4x4/AWD)",
}


# ══════════════════════════════════════════════════════════════════
# Helpers
# ══════════════════════════════════════════════════════════════════

def _get_val(obj: Any, key: str, default: Any = None) -> Any:
    if isinstance(obj, dict):
        return obj.get(key, default)
    return getattr(obj, key, default)


def _extract_strengths(scores: dict[str, float]) -> list[str]:
    """Dimensions avec score ≥ 4/5 → points forts."""
    strengths = []
    for dim, score in sorted(scores.items(), key=lambda x: x[1], reverse=True):
        if score >= 4.0:
            label = DIMENSION_LABELS.get(dim, dim)
            strengths.append(f"{label} ({score}/5)")
    return strengths[:3]  # Max 3 points forts


def _extract_compromises(scores: dict[str, float]) -> list[str]:
    """Dimensions avec score < 3/5 → compromis explicites."""
    compromises = []
    for dim, score in sorted(scores.items(), key=lambda x: x[1]):
        if score < 3.0:
            label = DIMENSION_LABELS.get(dim, dim)
            compromises.append(f"{label} ({score}/5)")
    return compromises[:2]  # Max 2 compromis


# ══════════════════════════════════════════════════════════════════
# Filtres durs
# ══════════════════════════════════════════════════════════════════

CASCADE_ORDER = ["brand", "body_type", "fuel_type", "budget"]


def _apply_hard_filters(
    vehicles: list[Any],
    budget_max: Optional[float] = None,
    fuel_type: Optional[str] = None,
    body_type: Optional[str] = None,
    brand: Optional[str] = None,
) -> tuple[list[Any], Optional[str]]:
    """
    Applique les filtres durs AVANT le scoring.
    Si moins de 3 véhicules subsistent, relâche les filtres en cascade.
    Budget est le DERNIER relâché (avec tolérance +15%).
    """
    active_filters = {}
    if brand:
        active_filters["brand"] = brand
    if body_type:
        active_filters["body_type"] = body_type
    if fuel_type:
        active_filters["fuel_type"] = fuel_type
    if budget_max:
        active_filters["budget"] = budget_max

    def passes(v: Any, filters: dict) -> bool:
        if "budget" in filters:
            price = _get_val(v, "price")
            max_allowed = filters["budget"] * 1.15  # tolérance 15%
            if price is None or float(price) > max_allowed:
                return False
        if "brand" in filters:
            v_brand = (_get_val(v, "brand", "") or "").lower()
            if v_brand != filters["brand"].lower():
                return False
        if "fuel_type" in filters:
            v_fuel = (_get_val(v, "fuel_type", "") or "").lower()
            if v_fuel != filters["fuel_type"].lower():
                return False
        if "body_type" in filters:
            v_body = (_get_val(v, "body_type", "") or "").lower()
            if isinstance(filters["body_type"], list):
                if v_body not in [b.lower() for b in filters["body_type"]]:
                    return False
            else:
                if v_body != filters["body_type"].lower():
                    return False
        # Must be available
        status = _get_val(v, "status", "available")
        if status and str(status).lower() != "available":
            return False
        return True

    # Only consider available vehicles
    available = [v for v in vehicles if (_get_val(v, "status", "available") or "available") == "available"]

    # Try strict filtering
    candidates = [v for v in available if passes(v, active_filters)]
    # A requested brand is an immutable hard constraint. Returning one or two
    # matching vehicles is correct; replacing them with another brand is not.
    if brand and len(candidates) < 3:
        return candidates, None

    if len(candidates) >= 3:
        return candidates, None

    # Cascade: relax filters one by one
    current = active_filters.copy()
    relaxed = None
    for key in CASCADE_ORDER:
        if key in current:
            del current[key]
            relaxed = key
            candidates = [v for v in available if passes(v, current)]
            if len(candidates) >= 3:
                return candidates, relaxed

    # Last resort is only valid when no identity constraint was supplied.
    if not candidates and not brand:
        candidates = available

    return candidates, relaxed


# ══════════════════════════════════════════════════════════════════
# Pipeline principal
# ══════════════════════════════════════════════════════════════════

def select_top3(
    vehicles: list[Any],
    query: dict,
    limit: int = 3,
) -> Top3Result:
    """
    Pipeline complet de sélection du Top 3 :
    1. Filtres durs (budget, motorisation, disponibilité) — AVANT scoring
    2. Scoring 8 dimensions pour chaque candidat
    3. Pondération dynamique selon le profil
    4. Tri par score pondéré décroissant
    5. Diversité de marque (1 par marque, complété si besoin)
    6. Enrichissement : points forts + compromis
    """
    budget_max = query.get("budget_max")
    fuel_type = query.get("fuel_type")
    body_type = query.get("body_type")
    brand = query.get("brand")

    # 1. Filtres durs
    candidates, relaxed_filter = _apply_hard_filters(
        vehicles, budget_max, fuel_type, body_type, brand,
    )
    total_candidates = len(candidates)
    logger.info("Hard filters: %d candidates (relaxed=%s)", total_candidates, relaxed_filter)

    if not candidates:
        return Top3Result(vehicles=[], total_candidates=0, relaxed_filter=relaxed_filter)

    # 2. Scoring 8 dimensions
    scored: list[tuple[Any, EightDimensionResult]] = []
    for v in candidates:
        result = score_vehicle_8d(v)
        scored.append((v, result))

    # 3. Pondération dynamique
    weights = compute_dynamic_weights_from_query(query)

    # 4. Score pondéré et tri
    weighted_scored: list[tuple[Any, EightDimensionResult, float]] = []
    for v, result in scored:
        scores_dict = result.scores.model_dump()
        weighted_total = sum(
            weights.get(dim, 0) * scores_dict.get(dim, 0)
            for dim in scores_dict
        )
        weighted_scored.append((v, result, weighted_total))

    weighted_scored.sort(key=lambda x: x[2], reverse=True)

    # 5. Diversité de marque (1 par marque, puis complète si besoin)
    seen_brands: set[str] = set()
    diverse: list[tuple[Any, EightDimensionResult, float]] = []
    overflow: list[tuple[Any, EightDimensionResult, float]] = []

    for v, result, total in weighted_scored:
        v_brand = (_get_val(v, "brand", "") or "").strip().lower()
        if v_brand not in seen_brands:
            seen_brands.add(v_brand)
            diverse.append((v, result, total))
        else:
            overflow.append((v, result, total))

    selected = diverse[:limit]
    if len(selected) < limit and overflow:
        needed = limit - len(selected)
        selected.extend(overflow[:needed])

    # 6. Enrichissement
    recommended_vehicles: list[RecommendedVehicle] = []
    for v, result, total in selected:
        scores_dict = result.scores.model_dump()

        margin = None
        v_price = _get_val(v, "price")
        if budget_max and v_price:
            margin = float(budget_max) - float(v_price)

        recommended_vehicles.append(RecommendedVehicle(
            vehicle_id=result.vehicle_id,
            brand=_get_val(v, "brand", ""),
            model=_get_val(v, "model", ""),
            version=_get_val(v, "version"),
            price=float(v_price or 0),
            year=int(_get_val(v, "year", 2020)),
            fuel_type=_get_val(v, "fuel_type"),
            body_type=_get_val(v, "body_type"),
            transmission=_get_val(v, "transmission"),
            scores=scores_dict,
            weighted_total=round(total, 3),
            strengths=_extract_strengths(scores_dict),
            compromises=_extract_compromises(scores_dict),
            budget_margin=margin,
        ))

    return Top3Result(
        vehicles=recommended_vehicles,
        total_candidates=total_candidates,
        relaxed_filter=relaxed_filter,
    )
