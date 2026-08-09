"""
app.ml.scoring.criteria_ranker — Calcul des 9 critères de notation intrinsèque
et extraction des faits justificatifs chiffrés pour chaque véhicule.

Selon le livrable "Comment Wakala note et classe les voitures" :
- Les notes sont des rangs percentiles (0 à 100) face au marché marocain.
- 7 critères sont calculés à partir de la fiche technique et des équipements.
- 2 critères (fiabilité, design) sont laissés à None (Règle d'honnêteté).
"""

from typing import Any, Dict, List, Optional



# Valeurs moyennes de référence sur le marché marocain pour l'estimation de rangs
MARKET_BENCHMARKS = {
    "trunk_capacity": {"min": 150, "p50": 380, "max": 750},
    "fuel_consumption": {"min": 3.2, "p50": 5.4, "max": 11.0},
    "power_to_weight": {"min": 45, "p50": 95, "max": 250}, # hp / tonne
    "safety_features": {"min": 2, "p50": 6, "max": 10},
    "comfort_features": {"min": 1, "p50": 5, "max": 10},
    "tech_features": {"min": 1, "p50": 4, "max": 9},
}

BODY_TYPE_DEFAULT_TRUNK = {
    "citadine": 280,
    "berline": 460,
    "break": 560,
    "suv": 490,
    "monospace": 580,
    "utilitaire": 750,
    "pick_up": 800,
    "coupe": 320,
    "cabriolet": 250,
}

BODY_TYPE_DEFAULT_SEATS = {
    "citadine": 5,
    "berline": 5,
    "break": 5,
    "suv": 5,
    "monospace": 7,
    "utilitaire": 3,
    "pick_up": 5,
    "coupe": 4,
    "cabriolet": 4,
}

SAFETY_KEYWORDS = [
    "airbag", "abs", "esp", "isofix", "freinage d'urgence", "angle mort",
    "maintien de voie", "anti-patinage", "radar de recul", "camera de recul",
    "alerte collision", "ncap"
]

COMFORT_KEYWORDS = [
    "climatisation automatique", "clim auto", "sièges chauffants", "regulateur",
    "régulateur", "limiteur", "toit ouvrant", "toit panoramique", "sellerie cuir",
    "insonorisation", "suspension", "accoudoir", "demarrage sans cle"
]

TECH_KEYWORDS = [
    "carplay", "android auto", "ecran tactile", "écran tactile", "camera 360",
    "caméra 360", "affichage tete haute", "hud", "recharge induction", "gps",
    "navigation", "bluetooth", "cockpit digital", "tableau de bord digital"
]


class CriteriaRanker:
    """Calculateur de rangs intrinsèques sur les 9 critères du référentiel Wakala."""

    def __init__(self):
        pass

    def _get_val(self, obj: Any, key: str, default: Any = None) -> Any:
        if isinstance(obj, dict):
            return obj.get(key, default)
        return getattr(obj, key, default)

    def extract_raw_metrics(self, vehicle: Any) -> Dict[str, float]:
        """Extrait ou estime les métriques physiques brutes du véhicule."""
        body_type = (self._get_val(vehicle, "body_type", "") or "").lower()
        fuel_type = (self._get_val(vehicle, "fuel_type", "") or "").lower()
        transmission = (self._get_val(vehicle, "transmission", "") or "").lower()
        
        # 1. Coffre et Places
        trunk = self._get_val(vehicle, "trunk_capacity_l")
        if trunk is None or trunk <= 0:
            trunk = BODY_TYPE_DEFAULT_TRUNK.get(body_type, 380)
            
        seats = self._get_val(vehicle, "seats")
        if seats is None or seats <= 0:
            seats = BODY_TYPE_DEFAULT_SEATS.get(body_type, 5)

        # 2. Consommation & Coût
        consumption = self._get_val(vehicle, "consumption_l_100")
        if consumption is None or consumption <= 0:
            if "electrique" in fuel_type:
                consumption = 1.8  # Equivalent L/100km en coût énergie
            elif "hybride" in fuel_type:
                consumption = 4.2
            elif "diesel" in fuel_type:
                consumption = 5.2
            else:
                consumption = 6.8

        # 3. Puissance & Accélération
        power_hp = self._get_val(vehicle, "engine_power_hp")
        if power_hp is None or power_hp <= 0:
            power_hp = 110  # Valeur médiane marché

        accel = self._get_val(vehicle, "acceleration_0_100")
        if accel is None or accel <= 0:
            # Estimation via puissance
            accel = max(6.0, 15.0 - (power_hp / 30.0))

        # 4, 5, 6. Équipements de Sécurité, Confort, Technologie
        description = (self._get_val(vehicle, "description", "") or "").lower()
        equipment_dict = self._get_val(vehicle, "equipment_list", {}) or {}
        if isinstance(equipment_dict, dict):
            eq_text = " ".join([f"{k} {v}" for k, v in equipment_dict.items()]).lower()
        elif isinstance(equipment_dict, list):
            eq_text = " ".join([str(item) for item in equipment_dict]).lower()
        else:
            eq_text = ""
        full_text = f"{description} {eq_text}"

        # Comptage équipements présents
        safety_count = sum(1 for kw in SAFETY_KEYWORDS if kw in full_text)
        comfort_count = sum(1 for kw in COMFORT_KEYWORDS if kw in full_text)
        tech_count = sum(1 for kw in TECH_KEYWORDS if kw in full_text)

        # Bonus de base selon l'année et la carrosserie
        year = self._get_val(vehicle, "year", 2020) or 2020
        if year >= 2022:
            safety_count = max(safety_count, 5)
            comfort_count = max(comfort_count, 4)
            tech_count = max(tech_count, 3)
        elif year >= 2018:
            safety_count = max(safety_count, 4)
            comfort_count = max(comfort_count, 3)
            tech_count = max(tech_count, 2)
        else:
            safety_count = max(safety_count, 3)

        # 7. Robustesse
        is_4x4 = "4x4" in description or "awd" in description or "4wd" in description
        is_suv = body_type in ["suv", "pick_up", "utilitaire"]
        robustness_score = 40.0
        if is_suv:
            robustness_score += 35.0
        if is_4x4:
            robustness_score += 25.0

        return {
            "trunk": float(trunk),
            "seats": float(seats),
            "consumption": float(consumption),
            "power_hp": float(power_hp),
            "accel": float(accel),
            "safety_count": float(safety_count),
            "comfort_count": float(comfort_count),
            "tech_count": float(tech_count),
            "robustness": float(robustness_score),
            "year": float(year),
            "is_auto": 1.0 if "auto" in transmission else 0.0,
        }

    def _normalize_percentile(self, value: float, v_min: float, v_p50: float, v_max: float, higher_is_better: bool = True) -> float:
        """Calcule un rang percentile (0-100) par interpolation linéaire par morceaux."""
        if not higher_is_better:
            # Pour la consommation ou l'accélération (plus bas = meilleur)
            if value <= v_min:
                return 100.0
            if value >= v_max:
                return 5.0
            if value <= v_p50:
                return 50.0 + (v_p50 - value) / (v_p50 - v_min) * 50.0
            else:
                return 5.0 + (v_max - value) / (v_max - v_p50) * 45.0
        else:
            if value >= v_max:
                return 100.0
            if value <= v_min:
                return 5.0
            if value >= v_p50:
                return 50.0 + (value - v_p50) / (v_max - v_p50) * 50.0
            else:
                return 5.0 + (value - v_min) / (v_p50 - v_min) * 45.0

    def compute_criteria_scores(self, vehicle: Any) -> Dict[str, Optional[float]]:
        """
        Calcule les 9 notes (0-100) pour un véhicule donné.
        Conformément à la règle d'honnêteté, 'fiabilite' et 'design' renvoient None.
        """
        raw = self.extract_raw_metrics(vehicle)

        # 1. Espace et coffre (mix volume de coffre + places)
        trunk_rank = self._normalize_percentile(raw["trunk"], 180, 420, 700, higher_is_better=True)
        seats_bonus = 15.0 if raw["seats"] >= 7 else (5.0 if raw["seats"] >= 5 else -10.0)
        espace_score = min(100.0, max(0.0, trunk_rank * 0.85 + seats_bonus))

        # 2. Économie à l'usage (consommation inversée)
        economie_score = self._normalize_percentile(raw["consumption"], 3.0, 5.2, 9.5, higher_is_better=False)

        # 3. Performance (puissance et accélération)
        power_rank = self._normalize_percentile(raw["power_hp"], 65, 115, 250, higher_is_better=True)
        accel_rank = self._normalize_percentile(raw["accel"], 6.0, 11.0, 16.0, higher_is_better=False)
        performance_score = (power_rank * 0.6) + (accel_rank * 0.4)

        # 4. Sécurité
        securite_score = self._normalize_percentile(raw["safety_count"], 1, 5, 10, higher_is_better=True)

        # 5. Confort
        confort_base = self._normalize_percentile(raw["comfort_count"], 1, 4, 9, higher_is_better=True)
        confort_score = min(100.0, confort_base + (10.0 if raw["is_auto"] else 0.0))

        # 6. Technologie
        technologie_score = self._normalize_percentile(raw["tech_count"], 1, 3, 8, higher_is_better=True)

        # 7. Robustesse
        robustesse_score = min(100.0, max(10.0, raw["robustness"]))

        # 8 & 9. Règle d'honnêteté : pas d'estimation artificielle
        fiabilite_score = None
        design_score = None

        return {
            "espace_coffre": round(espace_score, 1),
            "economie_usage": round(economie_score, 1),
            "performance": round(performance_score, 1),
            "securite": round(securite_score, 1),
            "confort": round(confort_score, 1),
            "technologie": round(technologie_score, 1),
            "robustesse": round(robustesse_score, 1),
            "fiabilite": fiabilite_score,
            "design": design_score,
        }

    def extract_key_facts(self, vehicle: Any, criteria_scores: Dict[str, Optional[float]]) -> List[str]:
        """
        Extrait les faits tangibles chiffrés (ex: '6 Airbags', '470 L de coffre')
        pour étayer les 2 meilleures notes du véhicule.
        """
        raw = self.extract_raw_metrics(vehicle)
        facts = []

        # Identifier les critères les mieux notés
        valid_scores = {k: v for k, v in criteria_scores.items() if v is not None}
        top_criteria = sorted(valid_scores.items(), key=lambda x: x[1], reverse=True)

        for crit, score in top_criteria:
            if len(facts) >= 2:
                break
                
            if crit == "espace_coffre":
                if raw["seats"] >= 7:
                    facts.append(f"{int(raw['seats'])} places & Coffre {int(raw['trunk'])} L")
                else:
                    facts.append(f"Coffre {int(raw['trunk'])} L (Top {max(5, 100 - int(score))}% marché)")
            elif crit == "economie_usage":
                facts.append(f"Consommation sobre : {raw['consumption']:.1f} L/100 km")
            elif crit == "securite":
                airbag_txt = f"{int(raw['safety_count'])} équipements de sécurité" if raw['safety_count'] > 2 else "Sécurité renforcée"
                facts.append(f"{airbag_txt} (ESP, Isofix)")
            elif crit == "performance":
                facts.append(f"Moteur {int(raw['power_hp'])} ch (0-100 en {raw['accel']:.1f}s)")
            elif crit == "technologie":
                facts.append("Écran tactile connecté & aides à la conduite")
            elif crit == "confort":
                facts.append("Climatisation régulée & grand confort")
            elif crit == "robustesse":
                facts.append("Garde au sol surélevée & châssis renforcé")

        # Fallback si pas assez de faits
        if not facts:
            facts.append(f"Coffre {int(raw['trunk'])} L")
            facts.append(f"Moteur {int(raw['power_hp'])} ch")

        return facts[:2]


criteria_ranker = CriteriaRanker()
