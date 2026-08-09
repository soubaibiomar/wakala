"""
app.ml.scoring.wakala_scorer — Calculateur de score selon la formule à 3 ingrédients,
pondération par situation de vie, redistribution honnête et cascade de relâchement des filtres.
"""

from typing import Any, Dict, List, Optional, Tuple
from app.ml.scoring.criteria_ranker import criteria_ranker


# Profils d'usage de base (totalisant 100%)
PROFILE_WEIGHTS: Dict[str, Dict[str, float]] = {
    "bebe": {
        "securite": 0.32, "espace_coffre": 0.24, "confort": 0.14, "fiabilite": 0.13,
        "economie_usage": 0.07, "technologie": 0.05, "performance": 0.03, "robustesse": 0.02, "design": 0.00
    },
    "famille": {
        "espace_coffre": 0.30, "securite": 0.20, "fiabilite": 0.15, "confort": 0.12,
        "economie_usage": 0.10, "technologie": 0.05, "performance": 0.05, "robustesse": 0.03, "design": 0.00
    },
    "familial": {
        "espace_coffre": 0.30, "securite": 0.20, "fiabilite": 0.15, "confort": 0.12,
        "economie_usage": 0.10, "technologie": 0.05, "performance": 0.05, "robustesse": 0.03, "design": 0.00
    },
    "trajet": {
        "economie_usage": 0.34, "fiabilite": 0.21, "confort": 0.14, "securite": 0.12,
        "technologie": 0.07, "performance": 0.05, "espace_coffre": 0.05, "robustesse": 0.02, "design": 0.00
    },
    "commute": {
        "economie_usage": 0.34, "fiabilite": 0.21, "confort": 0.14, "securite": 0.12,
        "technologie": 0.07, "performance": 0.05, "espace_coffre": 0.05, "robustesse": 0.02, "design": 0.00
    },
    "urbain": {
        "economie_usage": 0.34, "fiabilite": 0.20, "confort": 0.12, "securite": 0.12,
        "technologie": 0.10, "espace_coffre": 0.05, "performance": 0.05, "robustesse": 0.02, "design": 0.00
    },
    "ville": {
        "economie_usage": 0.34, "fiabilite": 0.20, "confort": 0.12, "securite": 0.12,
        "technologie": 0.10, "espace_coffre": 0.05, "performance": 0.05, "robustesse": 0.02, "design": 0.00
    },
    "plaisir": {
        "design": 0.28, "performance": 0.24, "technologie": 0.16, "confort": 0.12,
        "securite": 0.08, "economie_usage": 0.05, "espace_coffre": 0.04, "fiabilite": 0.03, "robustesse": 0.00
    },
    "sportif": {
        "design": 0.28, "performance": 0.24, "technologie": 0.16, "confort": 0.12,
        "securite": 0.08, "economie_usage": 0.05, "espace_coffre": 0.04, "fiabilite": 0.03, "robustesse": 0.00
    },
    "longs_trajets": {
        "confort": 0.20, "fiabilite": 0.19, "robustesse": 0.16, "securite": 0.15,
        "economie_usage": 0.12, "espace_coffre": 0.10, "performance": 0.05, "technologie": 0.03, "design": 0.00
    },
    "voyage": {
        "confort": 0.20, "fiabilite": 0.19, "robustesse": 0.16, "securite": 0.15,
        "economie_usage": 0.12, "espace_coffre": 0.10, "performance": 0.05, "technologie": 0.03, "design": 0.00
    },
    "professionnel": {
        "espace_coffre": 0.34, "economie_usage": 0.26, "fiabilite": 0.24, "securite": 0.06,
        "confort": 0.04, "robustesse": 0.03, "performance": 0.02, "technologie": 0.01, "design": 0.00
    },
    "pro": {
        "espace_coffre": 0.34, "economie_usage": 0.26, "fiabilite": 0.24, "securite": 0.06,
        "confort": 0.04, "robustesse": 0.03, "performance": 0.02, "technologie": 0.01, "design": 0.00
    },
    "neutre": {
        "economie_usage": 0.20, "fiabilite": 0.18, "securite": 0.16, "espace_coffre": 0.14,
        "confort": 0.12, "technologie": 0.10, "performance": 0.06, "robustesse": 0.04, "design": 0.00
    }
}

PRIORITY_MAPPING = {
    "securite": "securite",
    "sécurité": "securite",
    "espace": "espace_coffre",
    "coffre": "espace_coffre",
    "economique": "economie_usage",
    "économique": "economie_usage",
    "conso": "economie_usage",
    "confort": "confort",
    "performance": "performance",
    "puissance": "performance",
    "technologie": "technologie",
    "tech": "technologie",
    "robustesse": "robustesse",
    "fiabilite": "fiabilite",
    "fiabilité": "fiabilite",
}

CASCADE_ORDER = ["puissance", "carrosserie", "places", "energie", "marque", "budget"]


class WakalaScorer:
    """Moteur de calcul et de classement complet selon les spécifications Wakala."""

    def __init__(self):
        self.ranker = criteria_ranker

    def _get_val(self, obj: Any, key: str, default: Any = None) -> Any:
        if isinstance(obj, dict):
            return obj.get(key, default)
        return getattr(obj, key, default)

    def compute_user_weights(
        self,
        usage: Optional[str] = None,
        priorites: Optional[List[str]] = None,
        profil_passagers: Optional[str] = None,
        available_criteria: Optional[List[str]] = None
    ) -> Dict[str, float]:
        """
        Calcule les poids personnalisés selon la situation de vie,
        applique les boosters de priorité explicite,
        et redistribue les poids des critères manquants (Règle d'honnêteté).
        """
        usage_key = (usage or "").lower().strip()
        base_weights = PROFILE_WEIGHTS.get(usage_key, PROFILE_WEIGHTS["neutre"]).copy()

        # 1. Boosters de priorité explicite
        if priorites:
            for p in priorites:
                p_clean = p.lower().strip()
                mapped_crit = PRIORITY_MAPPING.get(p_clean)
                if mapped_crit and mapped_crit in base_weights:
                    base_weights[mapped_crit] += 0.18

        # 2. Ajustements selon passagers
        profil_clean = (profil_passagers or "").lower()
        if any(w in profil_clean for w in ["enfant", "bebe", "bébé", "famille"]):
            base_weights["securite"] += 0.10
            base_weights["espace_coffre"] += 0.08
        elif any(w in profil_clean for w in ["seul", "celibataire", "célibataire"]):
            base_weights["economie_usage"] += 0.10

        # 3. Règle d'honnêteté : filtrer sur les critères disponibles (exclut fiabilite & design)
        if available_criteria is None:
            available_criteria = ["espace_coffre", "economie_usage", "performance", "securite", "confort", "technologie", "robustesse"]

        active_weights = {k: v for k, v in base_weights.items() if k in available_criteria}
        total_active = sum(active_weights.values())

        if total_active <= 0:
            equal_val = 1.0 / len(available_criteria)
            return {k: equal_val for k in available_criteria}

        # Normalisation à 1.0 (100%)
        normalized_weights = {k: v / total_active for k, v in active_weights.items()}
        return normalized_weights

    def compute_budget_score(self, vehicle_price: Optional[float], budget_max: Optional[float]) -> float:
        """
        Ingrédient 2 : Adéquation au budget (25%).
        - 70% à 100% du budget : 100/100
        - 50% à 70% du budget : 88/100
        - < 50% du budget : note réduite
        - > budget : chute rapide jusqu'à 0 à +30% de dépassement
        - Prix non publié : 50/100 (neutre)
        """
        if vehicle_price is None or vehicle_price <= 0:
            return 50.0  # Prix non publié = note neutre

        if budget_max is None or budget_max <= 0:
            return 75.0  # Aucun budget contraint = note standard

        price = float(vehicle_price)
        budget = float(budget_max)

        if price <= budget:
            ratio = price / budget
            if ratio >= 0.70:
                return 100.0
            elif ratio >= 0.50:
                return 88.0
            else:
                # Échelle douce de 60 à 88
                return max(50.0, 60.0 + (ratio / 0.50) * 28.0)
        else:
            # Dépassement
            depassement = (price - budget) / budget
            if depassement >= 0.30:
                return 0.0
            return max(0.0, 100.0 * (1.0 - depassement / 0.30))

    def compute_practical_score(
        self,
        vehicle: Any,
        usage: Optional[str] = None,
        places_requises: Optional[int] = None,
    ) -> float:
        """
        Ingrédient 3 : Adéquation aux besoins pratiques (18%).
        Part de 100 et applique des pénalités multiplicatives.
        """
        score = 100.0
        penalty_factor = 1.0

        body_type = (self._get_val(vehicle, "body_type", "") or "").lower()
        seats = self._get_val(vehicle, "seats", 5) or 5
        usage_clean = (usage or "").lower()

        # Pénalité places insuffisantes
        if places_requises and places_requises > 0:
            if seats < places_requises:
                penalty_factor *= 0.50
        elif usage_clean in ["famille", "familial"] and seats < 5:
            penalty_factor *= 0.50

        # Pénalités d'incohérence d'usage
        if usage_clean in ["urbain", "ville"] and body_type in ["utilitaire", "pick_up"]:
            penalty_factor *= 0.75

        if usage_clean in ["bebe", "famille", "familial"] and body_type in ["coupe", "cabriolet"]:
            penalty_factor *= 0.40

        if usage_clean in ["professionnel", "pro"] and body_type in ["cabriolet", "coupe"]:
            penalty_factor *= 0.60

        return round(score * penalty_factor, 1)

    def score_single_vehicle(
        self,
        vehicle: Any,
        user_weights: Dict[str, float],
        budget_max: Optional[float] = None,
        usage: Optional[str] = None,
        places_requises: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        Calcule la note finale Wakala (0-100) et la décomposition complète :
        Note = 57% Qualité + 25% Budget + 18% Pratique
        """
        # 1. Notes intrinsèques sur les 9 critères
        criteria_scores = self.ranker.compute_criteria_scores(vehicle)
        
        # Qualité (57%) : moyenne pondérée des critères valides
        qualite_score = sum(
            user_weights[k] * (criteria_scores[k] or 0.0)
            for k in user_weights
            if criteria_scores.get(k) is not None
        )

        # Budget (25%)
        price = self._get_val(vehicle, "price")
        budget_score = self.compute_budget_score(price, budget_max)

        # Pratique (18%)
        pratique_score = self.compute_practical_score(vehicle, usage, places_requises)

        # Note finale
        final_score = (0.57 * qualite_score) + (0.25 * budget_score) + (0.18 * pratique_score)
        final_score = min(100.0, max(0.0, round(final_score, 1)))

        # Faits clés justificatifs
        key_facts = self.ranker.extract_key_facts(vehicle, criteria_scores)

        # Marge budgétaire
        budget_margin = None
        if budget_max and price:
            budget_margin = float(budget_max) - float(price)

        return {
            "vehicle_id": str(self._get_val(vehicle, "id")),
            "final_score": final_score,
            "score_breakdown": {
                "qualite": round(qualite_score, 1),
                "budget": round(budget_score, 1),
                "pratique": round(pratique_score, 1),
                "criteria": criteria_scores,
            },
            "key_facts": key_facts,
            "budget_margin": budget_margin,
        }

    def filter_and_cascade(
        self,
        vehicles: List[Any],
        budget_max: Optional[float] = None,
        brand: Optional[str] = None,
        fuel_type: Optional[str] = None,
        body_type: Optional[str] = None,
        seats_min: Optional[int] = None,
        power_min: Optional[int] = None,
    ) -> Tuple[List[Any], Optional[str]]:
        """
        Applique les filtres durs avec tolérance budget 15%.
        Si moins de 3 véhicules subsistent, applique la cascade de relâchement :
        puissance > carrosserie > places > energie > marque > budget
        Retourne (candidats, condition_relâchée_ou_None).
        """
        active_constraints = {
            "puissance": power_min,
            "carrosserie": body_type,
            "places": seats_min,
            "energie": fuel_type,
            "marque": brand,
            "budget": budget_max,
        }

        # Nettoyage des contraintes non spécifiées
        enabled_constraints = {k: v for k, v in active_constraints.items() if v is not None and v != ""}

        def passes(v: Any, constraints: Dict[str, Any]) -> bool:
            v_brand = (self._get_val(v, "brand", "") or "").lower()
            v_fuel = (self._get_val(v, "fuel_type", "") or "").lower()
            v_body = (self._get_val(v, "body_type", "") or "").lower()
            v_seats = self._get_val(v, "seats", 5) or 5
            v_power = self._get_val(v, "engine_power_hp", 0) or 0
            v_price = self._get_val(v, "price")

            if "budget" in constraints and constraints["budget"]:
                max_allowed = constraints["budget"] * 1.15
                if v_price is None or v_price > max_allowed:
                    return False

            if "marque" in constraints and constraints["marque"]:
                if v_brand != constraints["marque"].lower():
                    return False

            if "energie" in constraints and constraints["energie"]:
                if constraints["energie"].lower() not in v_fuel:
                    return False

            if "carrosserie" in constraints and constraints["carrosserie"]:
                if isinstance(constraints["carrosserie"], list):
                    if v_body not in [str(b).lower() for b in constraints["carrosserie"]]:
                        return False
                else:
                    req_b = str(constraints["carrosserie"]).lower()
                    if req_b not in v_body:
                        return False

            if "places" in constraints and constraints["places"]:
                if v_seats < constraints["places"]:
                    return False

            if "puissance" in constraints and constraints["puissance"]:
                if v_power < constraints["puissance"]:
                    return False

            return True

        # Test initial strict
        candidates = [v for v in vehicles if passes(v, enabled_constraints)]
        if len(candidates) >= 3 or not enabled_constraints:
            return candidates, None

        # Cascade de relâchement ordonnée
        relaxed_criterion = None
        current_constraints = enabled_constraints.copy()

        for crit in CASCADE_ORDER:
            if crit in current_constraints:
                del current_constraints[crit]
                relaxed_criterion = crit
                candidates = [v for v in vehicles if passes(v, current_constraints)]
                if len(candidates) >= 3:
                    break

        if not candidates:
            candidates = vehicles

        return candidates, relaxed_criterion


wakala_scorer = WakalaScorer()
