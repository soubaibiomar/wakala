import re

# Marqueurs forts de darija en alphabet latin (Arabizi)
DARIJA_LATIN_MARKERS = {
    "bghit", "3andi", "ma3endich", "dyal", "fin", "kayen", "wach", 
    "bzaf", "chwiya", "tomobila", "zwin", "zwina", "khassni", "mdina", 
    "sghira", "kbira", "sayara", "chari", "taman", "mzyan", "mzyana"
}

# Marqueurs forts de darija en script arabe
DARIJA_ARABIC_MARKERS = {
    "بغيت", "ديال", "واش", "بزاف", "شوية", "طوموبيل", "خصني", 
    "مزيان", "مزيانة", "فين", "كاين", "ماكاينش"
}

def analyze_language_hints(text: str) -> str:
    """
    Pré-filtre heuristique rapide pour fournir un indice de langue.
    CECI N'EST QU'UN INDICE destiné à guider le LLM, et non une décision finale.
    """
    text_lower = text.lower()
    
    # 1. Détection de caractères arabes
    # La plage \u0600-\u06FF couvre les lettres de l'alphabet arabe
    has_arabic_chars = bool(re.search(r'[\u0600-\u06FF]', text))
    
    # 2. Détection des marqueurs
    words = set(re.findall(r'\w+', text_lower))
    
    latin_darija_hits = len(words.intersection(DARIJA_LATIN_MARKERS))
    arabic_darija_hits = len(words.intersection(DARIJA_ARABIC_MARKERS))
    
    # 3. Détection des chiffres utilisés comme lettres (3, 7, 9) dans l'arabizi
    # ex: 3andi, 9bel, mli7
    arabizi_number_hits = len(re.findall(r'[a-z]+[379][a-z]+|^[379][a-z]+', text_lower))
    
    if has_arabic_chars:
        if arabic_darija_hits > 0:
            return "darija_probable_arabe"
        else:
            return "arabe_standard_probable"
    else:
        if latin_darija_hits > 0 or arabizi_number_hits > 0:
            return "darija_probable_latin"
        else:
            return "langue_etrangere_probable_ou_francais"
