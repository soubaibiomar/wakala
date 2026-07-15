import re

class StyleDetector:
    def __init__(self):
        self.technical_keywords = {
            "kilométrage", "kilometrage", "puissance", "ch", "cv", "chevaux", "boite", "boîte", 
            "automatique", "manuelle", "dsg", "couple", "nm", "v6", "v8", "cylindres", "turbo", 
            "hybride", "consommation", "l/100", "motorisation", "jantes", "pneus", "traction", "propulsion"
        }
        
        self.formal_keywords = {
            "bonjour", "bonsoir", "merci", "s'il vous plait", "s'il vous plaît", "svp", 
            "cordialement", "madame", "monsieur", "salutations", "pourriez-vous", "voudrais", "aimerais"
        }
    
    def detect_style(self, message: str) -> dict:
        """
        Détecte le style du message pour adapter le ton de la réponse.
        Ne déduit aucune caractéristique personnelle de l'utilisateur.
        """
        text = message.lower()
        words = re.findall(r'\b\w+\b', text)
        word_count = len(words)
        
        # Verbosity: concis (<= 15 mots) ou détaillé (> 15 mots)
        verbosity = "detailed" if word_count > 15 else "concise"
        
        # Technicality: technique (présence de mots-clés automobiles) ou basique
        has_tech = any(re.search(r'\b' + re.escape(kw) + r'\b', text) for kw in self.technical_keywords)
        technicality = "technical" if has_tech else "basic"
        
        # Formality: formel (formules de politesse) ou casual
        has_formal = any(re.search(r'\b' + re.escape(kw) + r'\b', text) for kw in self.formal_keywords)
        formality = "formal" if has_formal else "casual"
        
        return {
            "formality": formality,
            "verbosity": verbosity,
            "technicality": technicality
        }

style_detector = StyleDetector()
