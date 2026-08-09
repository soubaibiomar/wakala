"""
app.services.budget_normalizer — Normalisation robuste de montants budgétaires pour le marché automobile marocain.
Supporte les entiers, flottants, formats textes (200k, 200 000, 1.5 million, suffixes dh/dirhams/MAD).
"""

import re
from typing import Optional, Union


def normalize_budget(value: Optional[Union[int, float, str]]) -> Optional[int]:
    """
    Normalise une valeur budgétaire en un entier en MAD.
    Retourne None si invalide ou hors plage raisonnable [10 000, 5 000 000].
    """
    if value is None:
        return None

    if isinstance(value, (int, float)):
        val = int(round(value))
        if 10000 <= val <= 5000000:
            return val
        return None

    if not isinstance(value, str):
        return None

    raw = value.strip().lower()
    if not raw:
        return None

    # Nettoyage des suffixes monétaires (dh, dirhams, mad, etc.)
    cleaned = re.sub(r"\b(dh|dirhams?|mad)\b", "", raw).strip()

    # Traitement 'x million(s)' ou 'x.x millions' ou 'x,x millions'
    million_match = re.match(r"^([\d\s]+(?:[.,]\d+)?)\s*millions?$", cleaned)
    if million_match:
        num_str = million_match.group(1).replace(" ", "").replace(",", ".")
        try:
            val = int(round(float(num_str) * 1_000_000))
            if 10000 <= val <= 5000000:
                return val
            return None
        except ValueError:
            return None

    # Traitement 'x mille'
    mille_match = re.match(r"^([\d\s]+(?:[.,]\d+)?)\s*milles?$", cleaned)
    if mille_match:
        num_str = mille_match.group(1).replace(" ", "").replace(",", ".")
        try:
            val = int(round(float(num_str) * 1_000))
            if 10000 <= val <= 5000000:
                return val
            return None
        except ValueError:
            return None

    # Traitement 'xk' / 'x k'
    k_match = re.match(r"^([\d\s]+(?:[.,]\d+)?)\s*k$", cleaned)
    if k_match:
        num_str = k_match.group(1).replace(" ", "").replace(",", ".")
        try:
            val = int(round(float(num_str) * 1_000))
            if 10000 <= val <= 5000000:
                return val
            return None
        except ValueError:
            return None

    # Traitement '200 000' ou '200,000' ou '200000.0'
    plain_str = cleaned.replace(" ", "").replace(",", "")
    try:
        val = int(round(float(plain_str)))
        if 10000 <= val <= 5000000:
            return val
        return None
    except ValueError:
        return None
