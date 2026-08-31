"""
rag/consultative_flow.py — Orchestre la phase de découverte consultative.

Pose des questions ciblées (usage, budget, contraintes), accumule les réponses
dans un "profil de besoin" structuré (NeedsProfile), et ne déclenche le
moteur déterministe (Partie B) qu'une fois le profil suffisamment rempli.

PRINCIPE DIRECTEUR : Le LLM comprend et met en forme ; le moteur déterministe
certifie. Le LLM ne calcule JAMAIS un score, ne propose JAMAIS un véhicule.
"""

import logging
import re
from typing import Any, Optional

from app.rag.needs_profile_schema import NeedsProfile, PRIORITY_ALIASES, VALID_DIMENSIONS

logger = logging.getLogger(__name__)

# ──────────────────────────────────────────────────────────────────
# Extraction déterministe de champs depuis le message utilisateur
# ──────────────────────────────────────────────────────────────────

# Budget patterns (supports MAD, DH, dhs, k, million, etc.)
_BUDGET_PATTERNS = [
    # "250k", "250K MAD", "budget 250k"
    r"(?:budget\s*(?:de|dyal|dyali)?\s*)?(\d+\s*[kK])\b\s*(?:mad|dh|dhs|dirhams?)?",
    # "budget 250000", "budget de 250 000 MAD"
    r"budget\s*(?:de|dyal|dyali)?\s*(\d[\d\s.,]*)\s*(?:mad|dh|dhs|dirhams?)?",
    # "250000 MAD", "250 000 DH"
    r"(\d[\d\s.,]*)\s*(?:mad|dh|dhs|dirhams?)",
    # "ma3ndich/3andi ghir 200000", darija budget
    r"(?:3andi|m3aya|3ndi|عندي)\s*(?:ghir|ghi|غير)?\s*(\d[\d\s.,]*)",
    # "entre X et Y" — take the upper bound
    r"entre\s*(\d[\d\s.,]*)\s*(?:et|w|و)\s*(\d[\d\s.,]*)",
    # "max 250000", "maximum 250000"
    r"max(?:imum)?\s*(\d[\d\s.,]*)",
    # "moins de 300000"
    r"moins\s*de\s*(\d[\d\s.,]*)",
]

_USAGE_KEYWORDS = {
    "ville": ["ville", "urbain", "mdina", "city", "المدينة", "فالمدينة"],
    "route": ["route", "autoroute", "highway", "tri9", "الطريق", "longs trajets", "voyage"],
    "mixte": ["mixte", "les deux", "both", "ville et route", "mixed"],
    "offroad": ["offroad", "piste", "montagne", "4x4", "tout terrain"],
}

_FUEL_KEYWORDS = {
    "essence": ["essence", "benzine", "lisans", "gasoline", "بنزين"],
    "diesel": ["diesel", "mazout", "gazoil", "ديزل"],
    "hybride": ["hybride", "hybrid", "هجين"],
    "electrique": ["electrique", "électrique", "electric", "كهربائية", "ev"],
}

_BODY_TYPE_KEYWORDS = {
    "citadine": ["citadine", "petite voiture", "compact"],
    "berline": ["berline", "sedan", "سيدان"],
    "suv": ["suv", "4x4", "crossover"],
    "monospace": ["monospace", "van", "familiale"],
    "break": ["break", "wagon", "station wagon"],
    "coupe": ["coupe", "coupé", "sportive"],
    "pick_up": ["pick up", "pickup", "pick-up"],
    "utilitaire": ["utilitaire", "commercial"],
}


def _parse_number(text: str) -> Optional[float]:
    """Parse a number from various formats: 250000, 250 000, 250,000, 250k."""
    cleaned = re.sub(r"[^\d.,kK]", "", text.strip())
    if not cleaned:
        return None
    # Handle "k" suffix
    if cleaned[-1] in ("k", "K"):
        try:
            return float(cleaned[:-1].replace(",", ".")) * 1000
        except ValueError:
            return None
    # Remove spaces and commas used as thousands separators
    cleaned = cleaned.replace(" ", "").replace(",", "")
    try:
        return float(cleaned)
    except ValueError:
        return None


def extract_profile_fields(message: str) -> dict:
    """
    Extraction déterministe des champs du profil depuis un message utilisateur.
    Retourne un dict partiel (seuls les champs détectés).
    """
    text_lower = message.lower().strip()
    extracted: dict[str, Any] = {}

    # ── Budget ───────────────────────────────────────────────────
    for pattern in _BUDGET_PATTERNS:
        match = re.search(pattern, text_lower)
        if match:
            groups = match.groups()
            if len(groups) == 2:
                # "entre X et Y" — take the upper bound
                val = _parse_number(groups[1])
            else:
                val = _parse_number(groups[0])
            if val and val > 1000:  # Sanity check: must be > 1000 MAD
                extracted["budget_max"] = val
                break

    # ── Usage ────────────────────────────────────────────────────
    for usage, keywords in _USAGE_KEYWORDS.items():
        if any(kw in text_lower for kw in keywords):
            extracted["usage"] = usage
            break

    # ── Carburant ────────────────────────────────────────────────
    for fuel, keywords in _FUEL_KEYWORDS.items():
        if any(kw in text_lower for kw in keywords):
            extracted["fuel_preference"] = fuel
            break

    # ── Carrosserie ──────────────────────────────────────────────
    for body, keywords in _BODY_TYPE_KEYWORDS.items():
        if any(kw in text_lower for kw in keywords):
            extracted["body_type_preference"] = body
            break

    # ── Nombre de passagers ──────────────────────────────────────
    passengers_match = re.search(
        r"(\d)\s*(?:passagers?|personnes?|places?|pers|nas)", text_lower
    )
    if passengers_match:
        val = int(passengers_match.group(1))
        if 1 <= val <= 9:
            extracted["nb_passagers"] = val

    # ── Priorités (8 dimensions) ─────────────────────────────────
    priorities = []
    for alias, dimension in PRIORITY_ALIASES.items():
        if alias in text_lower and dimension in VALID_DIMENSIONS:
            priorities.append(dimension)
    if priorities:
        extracted["priorities"] = list(set(priorities))

    # ── Contraintes textuelles ───────────────────────────────────
    constraint_patterns = [
        r"pas\s+(?:trop\s+)?(?:de\s+)?(.+?)(?:\.|,|$)",
        r"je\s+(?:ne\s+)?veux\s+pas\s+(.+?)(?:\.|,|$)",
        r"sans\s+(.+?)(?:\.|,|$)",
        r"ma\s+bghitch\s+(.+?)(?:\.|,|$)",  # darija
    ]
    constraints = []
    for pattern in constraint_patterns:
        for match in re.finditer(pattern, text_lower):
            constraint = match.group(1).strip()
            if constraint and len(constraint) > 3:
                constraints.append(constraint)
    if constraints:
        extracted["constraints"] = constraints

    # ── Marque ────────────────────────────────────────────────────
    known_brands = [
        "renault", "peugeot", "dacia", "citroen", "citroën", "toyota",
        "hyundai", "kia", "volkswagen", "vw", "fiat", "ford", "opel",
        "mercedes", "bmw", "audi", "seat", "skoda", "nissan", "suzuki",
        "mitsubishi", "mg", "chery", "byd", "geely",
    ]
    for brand in known_brands:
        if brand in text_lower:
            extracted["brand_preference"] = brand.title()
            break

    return extracted


class ConsultativeFlow:
    """
    Orchestre la phase de découverte consultative.

    Deux phases distinctes :
    - DÉCOUVERTE : poser des questions ciblées, accumuler le profil
    - RESTITUTION : recevoir les résultats du moteur B et les mettre en forme

    Le passage de découverte à restitution est AUTOMATIQUE dès que le profil
    est complet (budget + usage au minimum).
    """

    def __init__(self):
        # Stockage des profils par session
        self._profiles: dict[str, NeedsProfile] = {}

    def get_profile(self, session_id: str) -> NeedsProfile:
        """Retourne le profil courant pour la session, ou un profil vide."""
        if session_id not in self._profiles:
            self._profiles[session_id] = NeedsProfile()
        return self._profiles[session_id]

    def update_profile(self, session_id: str, message: str) -> NeedsProfile:
        """
        Extrait les champs du message et met à jour le profil incrémentalement.
        Retourne le profil mis à jour.
        """
        current = self.get_profile(session_id)
        extracted = extract_profile_fields(message)

        if extracted:
            updated = current.merge_update(extracted)
            self._profiles[session_id] = updated
            logger.info(
                "Profile updated for session %s: %d fields filled, complete=%s",
                session_id, updated.filled_fields_count, updated.is_complete,
            )
            return updated

        return current

    def get_phase(self, session_id: str) -> str:
        """Détermine la phase courante : 'discovery' ou 'restitution'."""
        profile = self.get_profile(session_id)
        return "restitution" if profile.is_complete else "discovery"

    def get_next_question_target(self, session_id: str) -> tuple[str, str]:
        """
        Détermine l'UNIQUE information prioritaire à demander au prochain tour.
        Stratégie : 1 seule question à la fois, par ordre de priorité.
        """
        profile = self.get_profile(session_id)
        if profile.budget_max is None:
            return (
                "budget",
                "Demande UNIQUEMENT le budget maximum souhaité en Dirhams (MAD / DH). "
                "Exemple : 'Quel budget maximum envisagez-vous en DH ?'",
            )
        elif profile.usage is None:
            return (
                "usage",
                "Demande UNIQUEMENT l'usage principal prévu pour le véhicule. "
                "Exemple : 'Ce sera plutôt pour la ville au quotidien, des trajets mixtes, ou de longs trajets ?'",
            )
        elif not profile.fuel_preference and not profile.brand_preference:
            return (
                "preference",
                "Demande s'il y a une préférence de carburant (essence, diesel, hybride) ou de marque particulière.",
            )
        else:
            return ("complete", "Le profil est suffisant pour passer à la recommandation.")

    def get_discovery_context(self, session_id: str) -> str:
        """
        Génère un résumé concis du profil pour le LLM.
        """
        profile = self.get_profile(session_id)
        filled = []
        if profile.usage:
            filled.append(f"Usage: {profile.usage}")
        if profile.budget_max:
            filled.append(f"Budget: {profile.budget_max:,.0f} MAD")
        if profile.fuel_preference:
            filled.append(f"Carburant: {profile.fuel_preference}")
        if profile.brand_preference:
            filled.append(f"Marque: {profile.brand_preference}")
        if profile.body_type_preference:
            filled.append(f"Carrosserie: {profile.body_type_preference}")

        res = "Informations connues : " + (", ".join(filled) if filled else "Aucune pour l'instant")
        return res

    def build_recommendation_query(self, session_id: str) -> dict:
        """
        Construit la requête pour le moteur de recommandation (Partie B)
        à partir du profil complet.
        """
        profile = self.get_profile(session_id)
        if not profile.is_complete:
            raise ValueError("Cannot build recommendation query: profile is not complete")

        return {
            "budget_max": profile.budget_max,
            "usage": profile.usage,
            "nb_passagers": profile.nb_passagers,
            "priorities": profile.priorities,
            "fuel_type": profile.fuel_preference,
            "body_type": profile.body_type_preference,
            "brand": profile.brand_preference,
            "constraints": profile.constraints,
        }

    def handle_budget_objection(
        self, session_id: str, new_budget: Optional[float] = None
    ) -> dict:
        """
        Gère une objection budgétaire : met à jour le budget si fourni,
        ou réduit de 20% le budget actuel pour proposer des alternatives.
        """
        profile = self.get_profile(session_id)

        if new_budget:
            updated = profile.merge_update({"budget_max": None})  # Reset first
            # Force update
            data = updated.model_dump()
            data["budget_max"] = new_budget
            self._profiles[session_id] = NeedsProfile(**data)
        elif profile.budget_max:
            reduced = profile.budget_max * 0.80
            data = profile.model_dump()
            data["budget_max"] = reduced
            self._profiles[session_id] = NeedsProfile(**data)

        return self.build_recommendation_query(session_id)

    def clear_session(self, session_id: str) -> None:
        """Supprime le profil d'une session."""
        self._profiles.pop(session_id, None)


# Singleton
consultative_flow = ConsultativeFlow()
