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

from app.rag.needs_profile_schema import (
    DIMENSION_ORDER,
    NeedsProfile,
    PRIORITY_ALIASES,
    VALID_DIMENSIONS,
)

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
    # Le cas mixte doit être détecté avant "ville" ou "route" :
    # "ville et route" ne doit pas être tronqué en simple usage urbain.
    mixed_keywords = _USAGE_KEYWORDS["mixte"] + ["city and highway", "city/highway", "city or highway"]
    if any(kw in text_lower for kw in mixed_keywords):
        extracted["usage"] = "mixte"
    else:
        for usage, keywords in _USAGE_KEYWORDS.items():
            if usage == "mixte":
                continue
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
        r"(\d+)\s*(?:passagers?|personnes?|people|persons?|places?|pers|nas)", text_lower
    )
    if passengers_match:
        val = int(passengers_match.group(1))
        if 1 <= val <= 9:
            extracted["nb_passagers"] = val

    # ── Priorités (8 dimensions) ─────────────────────────────────
    priorities = []
    # Ces termes alimentent les filtres durs/contexte (et non une préférence
    # 8D explicite). Cela évite par exemple que "budget 240000" couvre
    # artificiellement la dimension prix_acces.
    non_priority_aliases = {"budget", "prix", "ville", "city", "urbain", "urban"}
    for alias, dimension in PRIORITY_ALIASES.items():
        if alias not in non_priority_aliases and alias in text_lower and dimension in VALID_DIMENSIONS:
            priorities.append(dimension)
    if priorities:
        extracted["priorities"] = list(set(priorities))

    # Une sensibilité forte à la consommation concerne à la fois le coût réel
    # et l'impact énergétique. On conserve les deux signaux séparément afin
    # que le moteur puisse les pondérer sans que le LLM ne les invente.
    if any(term in text_lower for term in ("consommation", "consumption", "conso", "faible consommation", "économie de carburant", "fuel economy")):
        extracted["priorities"] = list(set(extracted.get("priorities", [])) | {"cout_reel", "ecologie"})

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
            # Les filtres durs ne sont pas des préférences 8D. Une préférence
            # n'est couverte que lorsqu'elle est explicitement exprimée :
            # budget et usage restent donc des prérequis indépendants.
            covered = set(updated.covered_dimensions)
            covered.update(dimension for dimension in extracted.get("priorities", []) if dimension in VALID_DIMENSIONS)
            if extracted.get("nb_passagers") is not None:
                covered.add("espace")
            if extracted.get("fuel_preference") in {"hybride", "electrique"}:
                covered.add("ecologie")
            updated = updated.model_copy(update={
                "covered_dimensions": [d for d in DIMENSION_ORDER if d in covered],
                "pending_dimensions": [d for d in updated.pending_dimensions if d not in covered],
            })
            self._profiles[session_id] = updated
            logger.info(
                "Profile updated for session %s: %d fields filled, complete=%s",
                session_id, updated.filled_fields_count, updated.is_complete,
            )
            return updated

        return current

    def get_phase(self, session_id: str) -> str:
        """Retourne la phase historique basée sur les prérequis minimaux.

        Cette méthode reste compatible avec les intégrations existantes. Le
        chatbot utilise ``get_dialogue_phase`` afin de poursuivre la découverte
        jusqu'à ce que les préférences soient réellement assez discriminantes.
        """
        profile = self.get_profile(session_id)
        return "restitution" if profile.is_complete else "discovery"

    def get_dialogue_phase(self, session_id: str) -> str:
        """Phase utilisée par le chatbot : découverte ou restitution réelle."""
        return "restitution" if self.get_profile(session_id).ready_for_recommendation else "discovery"

    def _dimension_priority_order(self, profile: NeedsProfile) -> list[str]:
        """Retourne les dimensions pertinentes avant les dimensions génériques."""
        if profile.usage == "ville":
            preferred = ["espace", "securite", "praticite_urbaine"]
        elif profile.usage == "route":
            preferred = ["securite", "cout_reel", "performance"]
        elif profile.usage == "offroad":
            preferred = ["motricite", "performance", "securite"]
        else:
            preferred = ["espace", "securite", "praticite_urbaine", "cout_reel", "performance", "ecologie", "motricite", "prix_acces"]
        return preferred + [dimension for dimension in DIMENSION_ORDER if dimension not in preferred]

    @staticmethod
    def _vehicle_dimension_value(vehicle: dict, dimension: str) -> str:
        """Extrait une valeur comparable pour estimer le pouvoir discriminant."""
        aliases = {
            "espace": ("trunk_capacity_l", "seats", "body_type"),
            "securite": ("ncap_rating", "safety_rating", "description"),
            "cout_reel": ("consumption_l_100", "fuel_type"),
            "prix_acces": ("price",),
            "praticite_urbaine": ("body_type", "length_mm", "turning_radius"),
            "performance": ("engine_power_hp", "acceleration_0_100"),
            "ecologie": ("fuel_type", "co2_g_km", "consumption_l_100"),
            "motricite": ("drive_type", "body_type", "description"),
        }
        for key in aliases.get(dimension, ()):
            value = vehicle.get(key)
            if value not in (None, "", []):
                return str(value).lower()
        return "unknown"

    def _rank_missing_dimensions(self, profile: NeedsProfile, candidate_vehicles: Optional[list[dict]]) -> list[str]:
        """Classe les dimensions par utilité et, si possible, par diversité du pool."""
        covered = set(profile.covered_dimensions) | set(profile.pending_dimensions)
        candidates = [d for d in self._dimension_priority_order(profile) if d not in covered]
        if not candidate_vehicles or len(candidate_vehicles) < 2:
            return candidates
        # Une dimension qui sépare le mieux les candidats est plus utile qu'une
        # dimension dont tous les véhicules ont la même valeur.
        diversity = {
            dimension: len({self._vehicle_dimension_value(vehicle, dimension) for vehicle in candidate_vehicles})
            for dimension in candidates
        }
        return sorted(candidates, key=lambda dimension: (-diversity[dimension], candidates.index(dimension)))

    def get_next_question_plan(
        self, session_id: str, candidate_vehicles: Optional[list[dict]] = None
    ) -> dict[str, Any]:
        """Produit une sélection Analyze → Select → Formulate de 1 à 2 questions."""
        profile = self.get_profile(session_id)
        if profile.budget_max is None:
            return {"dimensions": [], "target": "budget", "questions": [
                "Quel est votre budget maximum en dirhams (MAD ou DH) ?"
            ]}
        if profile.usage is None:
            return {"dimensions": [], "target": "usage", "questions": [
                "Utiliserez-vous surtout la voiture en ville, sur route, ou dans les deux ?"
            ]}

        ranked = self._rank_missing_dimensions(profile, candidate_vehicles)
        if not ranked:
            return {"dimensions": [], "target": "complete", "questions": []}

        first = ranked[0]
        questions = {
            "espace": "De combien de place avez-vous besoin pour les passagers et les valises ?",
            "securite": "Quel niveau d'importance accordez-vous à la sécurité certifiée (notes NCAP) ?",
            "cout_reel": "Préférez-vous réduire la consommation et les coûts d'utilisation, même si le prix d'achat est plus élevé ?",
            "prix_acces": "Souhaitez-vous privilégier le prix d'achat le plus bas dans votre budget ?",
            "praticite_urbaine": "Pour la ville, privilégiez-vous une voiture compacte et facile à garer ?",
            "performance": "Préférez-vous davantage de puissance et de reprises, ou une conduite plus économique ?",
            "ecologie": "L'énergie hybride ou électrique est-elle une priorité pour vous ?",
            "motricite": "Avez-vous besoin d'une transmission intégrale ou d'aptitudes tout-terrain ?",
        }
        selected = [first]
        if len(ranked) > 1 and first not in {"cout_reel", "performance"}:
            selected.append(ranked[1])
        rendered = [questions[dimension] for dimension in selected]
        if len(selected) == 2:
            rendered[1] = f"Et entre {selected[0]} et {selected[1]}, lequel compte le plus pour vous ?"
        return {"dimensions": selected, "target": ",".join(selected), "questions": rendered}

    def record_question_plan(self, session_id: str, plan: dict[str, Any]) -> None:
        """Enregistre la question envoyée pour empêcher les répétitions."""
        dimensions = [d for d in plan.get("dimensions", []) if d in VALID_DIMENSIONS]
        if not dimensions:
            return
        profile = self.get_profile(session_id)
        asked = list(dict.fromkeys(profile.asked_dimensions + dimensions))
        updated = profile.model_copy(update={"asked_dimensions": asked, "pending_dimensions": dimensions})
        self._profiles[session_id] = updated

    def get_next_question_target(self, session_id: str, candidate_vehicles: Optional[list[dict]] = None) -> tuple[str, str]:
        """
        Détermine l'UNIQUE information prioritaire à demander au prochain tour.
        Stratégie : 1 seule question à la fois, par ordre de priorité.
        """
        plan = self.get_next_question_plan(session_id, candidate_vehicles)
        if not plan["questions"]:
            return ("complete", "Le profil est suffisant pour passer à la recommandation.")
        return (plan["target"], " Pose au maximum ces questions, sans en ajouter : " + " ".join(plan["questions"]))

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
        if profile.nb_passagers:
            filled.append(f"Passagers habituels: {profile.nb_passagers}")
        if profile.priorities:
            filled.append(f"Priorités: {', '.join(profile.priorities)}")

        missing = ", ".join(profile.missing_dimensions) or "aucune"
        pending = ", ".join(profile.pending_dimensions) or "aucune"
        essential_missing = ", ".join(profile.missing_essential_fields()) or "aucun"
        res = (
            "Informations connues : " + (", ".join(filled) if filled else "Aucune pour l'instant")
            + f". CHAMPS MANQUANTS : {essential_missing}."
            + f". DIMENSIONS 8D COUVERTES : {', '.join(profile.covered_dimensions) or 'aucune'}."
            + f" DIMENSIONS 8D MANQUANTS : {missing}."
            + f" QUESTIONS EN ATTENTE : {pending}. Pose 1 à 2 questions maximum."
        )
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
