import re
from typing import Dict, Any

class MatchmakerNLP:
    """
    Extrait des critères structurés (budget, usage, type) à partir
    d'un texte libre (NLP basique par mots-clés / heuristiques).
    """

    def __init__(self):
        # Mots clés simples pour un projet académique
        self.family_keywords = ["famille", "enfants", "espace", "spacieux", "minivan", "suv", "grand"]
        self.city_keywords = ["ville", "citadine", "petit", "se garer", "urbain"]
        self.eco_keywords = ["hybride", "electrique", "eco", "consommation", "faible consommation"]
        self.sport_keywords = ["sport", "rapide", "puissant", "performance"]

    def extract_criteria(self, text: str) -> Dict[str, Any]:
        """Extrait les critères depuis le texte libre de l'utilisateur."""
        text_lower = text.lower()
        
        criteria = {
            "body_type_preferred": [],
            "fuel_type_preferred": [],
            "max_price": None,
            "lifestyle": "standard"
        }

        # Extraction de budget (ex: "moins de 150000", "budget 200 000")
        price_match = re.search(r'(?:budget|moins de|max)\s*(\d{1,3}(?:[ \.]?\d{3})*)', text_lower)
        if price_match:
            try:
                price_str = re.sub(r'[ \.]', '', price_match.group(1))
                criteria["max_price"] = int(price_str)
            except ValueError:
                pass

        # Lifestyle & Body type
        if any(kw in text_lower for kw in self.family_keywords):
            criteria["lifestyle"] = "family"
            criteria["body_type_preferred"].extend(["suv", "break", "monospace"])
            
        if any(kw in text_lower for kw in self.city_keywords):
            criteria["lifestyle"] = "urban"
            criteria["body_type_preferred"].extend(["citadine", "compacte"])
            
        if any(kw in text_lower for kw in self.eco_keywords):
            criteria["fuel_type_preferred"].extend(["hybride", "electrique"])
            
        if any(kw in text_lower for kw in self.sport_keywords):
            criteria["lifestyle"] = "sport"
            criteria["body_type_preferred"].extend(["coupe", "berline"])

        # Deduplicate
        criteria["body_type_preferred"] = list(set(criteria["body_type_preferred"]))
        criteria["fuel_type_preferred"] = list(set(criteria["fuel_type_preferred"]))
        
        return criteria

matchmaker_nlp = MatchmakerNLP()
