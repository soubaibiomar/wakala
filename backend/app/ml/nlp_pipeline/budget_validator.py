import re
from typing import Optional

def normalize_and_validate_budget(raw_budget: Optional[str | int | float]) -> Optional[int]:
    """
    Extrait et normalise un budget depuis une chaîne (ex: '200k', '200 000 MAD', '1.5 million').
    Valide que le budget est dans une plage réaliste (20,000 - 3,000,000 MAD).
    Retourne le montant entier en MAD, ou None si invalide/absent.
    """
    if raw_budget is None:
        return None

    budget = None
    if isinstance(raw_budget, (int, float)):
        budget = int(raw_budget)
    else:
        text = str(raw_budget).lower().replace(" ", "").replace(",", ".")
        
        # 1.5 million -> 1500000
        match_million = re.search(r"([\d\.]+)\s*(million|m)", text)
        if match_million:
            try:
                budget = int(float(match_million.group(1)) * 1_000_000)
            except ValueError:
                pass
        else:
            # 200k -> 200000
            match_k = re.search(r"([\d\.]+)\s*[k]", text)
            if match_k:
                try:
                    budget = int(float(match_k.group(1)) * 1_000)
                except ValueError:
                    pass
            else:
                # Extracts raw number
                match_num = re.search(r"(\d[\d\.]*\d|\d+)", text)
                if match_num:
                    try:
                        num = float(match_num.group(1))
                        budget = int(num)
                    except ValueError:
                        pass
    
    if budget is not None:
        # Moroccan specific heuristic
        # If user says "20", they might mean "20 million centimes" -> 200,000 MAD
        if 2 <= budget <= 300:
            budget = budget * 10000
            
        # Range validation
        if 20_000 <= budget <= 3_000_000:
            return budget
            
    return None
