"""
ml/recommendation/eight_dimension_scorer.py — Calcul des 8 dimensions Wakala.

Les 8 dimensions sont : Espace, Sécurité, Coût réel, Prix d'accès,
Praticité urbaine, Performance, Écologie, Motricité.

Deux modes :
1. Mode pré-calculé (par défaut) : lit depuis vehicle_wakala_scores en base
2. Mode calcul (fallback) : calcule à la volée avec les seuils du catalogue xlsx

PRINCIPE : Ce module ne fait que CALCULER des scores — il ne filtre pas,
ne classe pas, ne recommande pas. C'est top3_selector.py qui orchestre.
"""

import logging
import re
from typing import Any, Optional

from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


# ══════════════════════════════════════════════════════════════════
# Schéma de sortie structuré (Pydantic)
# ══════════════════════════════════════════════════════════════════

class EightDimensionScores(BaseModel):
    """Scores sur les 8 dimensions Wakala (1–5 chacune)."""
    espace: float = Field(..., ge=1, le=5, description="Volume coffre + places")
    securite: float = Field(..., ge=1, le=5, description="NCAP + équipements sécurité")
    cout_reel: float = Field(..., ge=1, le=5, description="Consommation + coût d'usage")
    prix_acces: float = Field(..., ge=1, le=5, description="Prix catalogue d'entrée")
    praticite_urbaine: float = Field(..., ge=1, le=5, description="Dimensions + maniabilité")
    performance: float = Field(..., ge=1, le=5, description="Puissance + accélération")
    ecologie: float = Field(..., ge=1, le=5, description="CO2 + type de motorisation")
    motricite: float = Field(..., ge=1, le=5, description="4x4 / AWD / garde au sol")


class EightDimensionResult(BaseModel):
    """Résultat de scoring complet pour un véhicule."""
    vehicle_id: str
    scores: EightDimensionScores
    source: str = Field(
        default="computed",
        description="'precomputed' si lu depuis vehicle_wakala_scores, 'computed' si calculé à la volée"
    )


# ══════════════════════════════════════════════════════════════════
# Seuils de scoring issus de l'audit du catalogue xlsx
# Conformes au document de référence Wakala
# ══════════════════════════════════════════════════════════════════

def _score_cout_reel(fuel_consumption: Optional[float], fuel_type: Optional[str]) -> float:
    """
    Coût réel d'usage — seuils xlsx :
    - Électrique ou <4.5L → 5
    - 4.5–6L → 4
    - 6–8L → 3
    - 8–10L → 2
    - >10L → 1
    """
    ft = (fuel_type or "").lower()
    if "electrique" in ft or "électrique" in ft:
        return 5.0

    conso = fuel_consumption or 7.0  # valeur par défaut pessimiste
    if conso < 4.5:
        return 5.0
    elif conso < 6.0:
        return 4.0
    elif conso < 8.0:
        return 3.0
    elif conso < 10.0:
        return 2.0
    else:
        return 1.0


def _score_securite(ncap_rating: Optional[str], year: Optional[int]) -> float:
    """
    Sécurité — notes NCAP réelles (corrigées lors de l'audit) :
    - 5★ NCAP → 5
    - 4★ → 4
    - 3★ → 3
    - 2★ ou moins → 2
    - Pas de note NCAP : estimation par année (>2020 → 3.5, >2018 → 3, sinon 2.5)
    """
    if ncap_rating:
        rating_str = str(ncap_rating).strip().lower()
        # Read the rating itself, not an unrelated year in a string such as
        # "4★ (Euro NCAP 2021)". This makes safety ranking deterministic.
        rating_match = re.search(r"(?<!\d)([1-5](?:[.,]0)?)(?=\s*(?:/\s*5|[★*]|stars?|étoiles?))", rating_str)
        if rating_match:
            return min(5.0, max(1.0, float(rating_match.group(1).replace(',', '.'))))
        if re.fullmatch(r"[1-5](?:[.,]0)?", rating_str):
            return float(rating_str.replace(',', '.'))

    # Fallback: estimation par année
    y = year or 2020
    if y >= 2022:
        return 3.5
    elif y >= 2020:
        return 3.0
    elif y >= 2018:
        return 2.5
    else:
        return 2.0


def _score_espace(
    trunk_volume: Optional[int],
    seats: Optional[int],
    body_type: Optional[str],
) -> float:
    """
    Espace — seuils xlsx :
    - >500L coffre → 5
    - 400–500L → 4
    - 300–400L → 3
    - 200–300L → 2
    - <200L → 1
    Bonus +0.5 si ≥7 places.
    """
    # Default trunk volume based on body type
    defaults = {
        "citadine": 280, "berline": 460, "break": 560,
        "suv": 490, "monospace": 580, "utilitaire": 750,
        "pick_up": 800, "coupe": 320, "cabriolet": 250,
    }
    bt = (body_type or "").lower()
    trunk = trunk_volume or defaults.get(bt, 380)

    if trunk >= 500:
        score = 5.0
    elif trunk >= 400:
        score = 4.0
    elif trunk >= 300:
        score = 3.0
    elif trunk >= 200:
        score = 2.0
    else:
        score = 1.0

    # Bonus places
    s = seats or 5
    if s >= 7:
        score = min(5.0, score + 0.5)

    return score


def _score_prix_acces(price: Optional[float]) -> float:
    """
    Prix d'accès — seuils marché marocain :
    - <150 000 MAD → 5
    - 150 000–250 000 → 4
    - 250 000–400 000 → 3
    - 400 000–600 000 → 2
    - >600 000 → 1
    """
    p = float(price or 300000)
    if p < 150000:
        return 5.0
    elif p < 250000:
        return 4.0
    elif p < 400000:
        return 3.0
    elif p < 600000:
        return 2.0
    else:
        return 1.0


def _score_praticite_urbaine(
    length_cm: Optional[int],
    body_type: Optional[str],
) -> float:
    """
    Praticité urbaine — seuils xlsx :
    - <400cm → 5 (citadine idéale)
    - 400–430cm → 4
    - 430–460cm → 3
    - 460–500cm → 2
    - >500cm → 1
    """
    # Default lengths by body type
    defaults = {
        "citadine": 380, "berline": 460, "break": 470,
        "suv": 445, "monospace": 470, "utilitaire": 520,
        "pick_up": 530, "coupe": 440, "cabriolet": 430,
    }
    bt = (body_type or "").lower()
    length = length_cm or defaults.get(bt, 440)

    if length < 400:
        return 5.0
    elif length < 430:
        return 4.0
    elif length < 460:
        return 3.0
    elif length < 500:
        return 2.0
    else:
        return 1.0


def _score_performance(engine_power_hp: Optional[int]) -> float:
    """
    Performance — seuils :
    - >250 ch → 5
    - 180–250 → 4
    - 120–180 → 3
    - 80–120 → 2
    - <80 → 1
    """
    hp = engine_power_hp or 100
    if hp >= 250:
        return 5.0
    elif hp >= 180:
        return 4.0
    elif hp >= 120:
        return 3.0
    elif hp >= 80:
        return 2.0
    else:
        return 1.0


def _score_ecologie(
    co2_emissions: Optional[float],
    fuel_type: Optional[str],
) -> float:
    """
    Écologie — seuils :
    - Électrique (0 CO2) → 5
    - <100g CO2 ou hybride rechargeable → 4.5
    - 100–130g → 4
    - 130–160g → 3
    - 160–200g → 2
    - >200g → 1
    """
    ft = (fuel_type or "").lower()
    if "electrique" in ft or "électrique" in ft:
        return 5.0

    co2 = co2_emissions
    if co2 is None:
        # Estimation par type carburant
        if "hybride_rechargeable" in ft:
            return 4.5
        elif "hybride" in ft:
            return 4.0
        elif "diesel" in ft:
            return 2.5
        else:
            return 2.0

    co2_val = float(co2)
    if co2_val <= 0:
        return 5.0
    elif co2_val < 100:
        return 4.5
    elif co2_val < 130:
        return 4.0
    elif co2_val < 160:
        return 3.0
    elif co2_val < 200:
        return 2.0
    else:
        return 1.0


def _score_motricite(is_4x4: Optional[bool], body_type: Optional[str]) -> float:
    """
    Motricité (capacité tout-terrain) :
    - 4x4/AWD confirmé → 5
    - SUV sans 4x4 → 3
    - Pick-up sans 4x4 → 3.5
    - Autres → 1.5
    """
    bt = (body_type or "").lower()
    has_4x4 = bool(is_4x4)

    if has_4x4:
        return 5.0
    elif bt == "pick_up":
        return 3.5
    elif bt == "suv":
        return 3.0
    elif bt == "utilitaire":
        return 2.5
    else:
        return 1.5


# ══════════════════════════════════════════════════════════════════
# Scoreur principal
# ══════════════════════════════════════════════════════════════════

def _get_val(obj: Any, key: str, default: Any = None) -> Any:
    """Helper to get value from dict or object."""
    if isinstance(obj, dict):
        return obj.get(key, default)
    return getattr(obj, key, default)


def score_vehicle_8d(vehicle: Any) -> EightDimensionResult:
    """
    Calcule les 8 dimensions pour un véhicule.

    Mode pré-calculé : si le véhicule a un attribut `wakala_scores`
    (relation ORM vers VehicleWakalaScore), utilise ces scores directement.

    Mode calcul : sinon, calcule à la volée depuis la fiche technique.
    """
    vehicle_id = str(_get_val(vehicle, "id", ""))

    # ── Mode pré-calculé ──────────────────────────────────────────
    ws = _get_val(vehicle, "wakala_scores")
    if ws is not None:
        space = _get_val(ws, "space_score")
        safety = _get_val(ws, "safety_score")
        real_cost = _get_val(ws, "real_cost_score")
        access_price = _get_val(ws, "access_price_score")
        city = _get_val(ws, "city_practicality_score")
        perf = _get_val(ws, "performance_score")
        eco = _get_val(ws, "ecology_score")
        offroad = _get_val(ws, "offroad_score")

        # Only use precomputed if all scores are present
        all_scores = [space, safety, real_cost, access_price, city, perf, eco, offroad]
        if all(s is not None for s in all_scores):
            logger.debug("Using precomputed wakala_scores for vehicle %s", vehicle_id)
            return EightDimensionResult(
                vehicle_id=vehicle_id,
                scores=EightDimensionScores(
                    espace=float(space),
                    securite=float(safety),
                    cout_reel=float(real_cost),
                    prix_acces=float(access_price),
                    praticite_urbaine=float(city),
                    performance=float(perf),
                    ecologie=float(eco),
                    motricite=float(offroad),
                ),
                source="precomputed",
            )

    # ── Mode calcul (fallback) ────────────────────────────────────
    logger.debug("Computing 8D scores on-the-fly for vehicle %s", vehicle_id)

    fuel_consumption = _get_val(vehicle, "fuel_consumption")
    fuel_type = _get_val(vehicle, "fuel_type")
    ncap_rating = _get_val(vehicle, "ncap_rating")
    year = _get_val(vehicle, "year")
    trunk_volume = _get_val(vehicle, "trunk_volume_l")
    seats = _get_val(vehicle, "seats")
    body_type = _get_val(vehicle, "body_type")
    price = _get_val(vehicle, "price")
    length_cm = _get_val(vehicle, "length_cm")
    engine_power_hp = _get_val(vehicle, "engine_power_hp")
    co2_emissions = _get_val(vehicle, "co2_emissions")
    is_4x4 = _get_val(vehicle, "is_4x4")

    scores = EightDimensionScores(
        espace=_score_espace(trunk_volume, seats, body_type),
        securite=_score_securite(ncap_rating, year),
        cout_reel=_score_cout_reel(fuel_consumption, fuel_type),
        prix_acces=_score_prix_acces(price),
        praticite_urbaine=_score_praticite_urbaine(length_cm, body_type),
        performance=_score_performance(engine_power_hp),
        ecologie=_score_ecologie(co2_emissions, fuel_type),
        motricite=_score_motricite(is_4x4, body_type),
    )

    return EightDimensionResult(
        vehicle_id=vehicle_id,
        scores=scores,
        source="computed",
    )
