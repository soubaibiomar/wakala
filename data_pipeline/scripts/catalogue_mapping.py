"""
catalogue_mapping.py — Table de correspondance explicite entre le fichier Excel Wakala
et les schémas PostgreSQL (tables 'vehicles' et 'vehicle_wakala_scores').

Chaque colonne du fichier Excel est documentée ici de manière transparente.
Aucun mapping implicite ou masqué n'est autorisé.
"""

from typing import Any, Dict, Optional, Tuple
import re
import unicodedata

# ═══════════════════════════════════════════════════════════════════════════
# 1. TABLE DE CORRESPONDANCE DES COLONNES EXCEL (Feuille 'Catalogue')
# ═══════════════════════════════════════════════════════════════════════════

EXCEL_COLUMN_HEADERS = {
    "brand": "Marque",
    "model": "Modèle",
    "version": "Variante",
    "price": "Prix DH",
    "trunk_volume_l": "Coffre (L)",
    "ncap_rating": "Sécu NCAP ★",
    "fuel_consumption": "Conso L/100km",
    "engine_power_hp": "Puissance ch",
    "co2_emissions": "CO2 g/km",
    "length_cm": "Longueur cm",
    "is_4x4": "4x4",
    "autonomy_raw": "Autonomie km",
    
    # 8 Notes Wakala (1-5) & Métadonnées
    "space_score": "Espace",
    "safety_score": "Sécurité",
    "real_cost_score": "Coût réel",
    "access_price_score": "Prix accès",
    "city_practicality_score": "Pratique ville",
    "performance_score": "Performance",
    "ecology_score": "Écologie",
    "offroad_score": "Tout terrain",
    "overall_score": "Score /5",
    "data_reliability": "Fiabilité données",
    "observations": "Constat (prix officiel / disponibilité)",
    "source_note": "Source",
    "official_colors_raw": "Couleurs Officielles & HEX",
    "official_options_raw": "Options & Packs Équipements",
    "official_website": "Site Web Officiel Marque",
}

# Model-level body styles verified against manufacturer product pages and
# worldwide model nomenclature.  This is intentionally keyed by make + model:
# a trim can say "Fastback" or "SUV Coupé" without changing the vehicle's
# catalogue class, and a generic dealer page can contain several body styles.
# Keep the values restricted to the PostgreSQL body_type enum.
MODEL_BODY_TYPE_OVERRIDES = {
    # --- ABARTH ---
    "abarth|500e": "citadine",
    "abarth|595": "citadine",
    "abarth|695": "citadine",
    # --- ALFA ROMEO ---
    "alfa romeo|giulia": "berline",
    "alfa romeo|giulietta": "berline",
    "alfa romeo|junior": "suv",
    "alfa romeo|junior elettrica": "suv",
    "alfa romeo|junior ev": "suv",
    "alfa romeo|stelvio": "suv",
    "alfa romeo|tonale": "suv",
    # --- ALPINE ---
    "alpine|a110": "coupe",
    "alpine|a290": "citadine",
    "alpine|a390": "coupe",
    # --- ASTON MARTIN ---
    "aston martin|db12": "coupe",
    "aston martin|dbx": "suv",
    "aston martin|valhalla": "coupe",
    "aston martin|valiant": "coupe",
    "aston martin|valkyrie": "coupe",
    "aston martin|vanquish": "coupe",
    "aston martin|vantage": "coupe",
    # --- AUDI ---
    "audi|a1": "citadine",
    "audi|a1 sportback": "citadine",
    "audi|a3": "berline",
    "audi|a3 berline": "berline",
    "audi|a3 sportback": "berline",
    "audi|a4": "berline",
    "audi|a4 berline": "berline",
    "audi|a5": "berline",
    "audi|a5 sportback": "coupe",
    "audi|a6": "berline",
    "audi|a6 e-tron": "berline",
    "audi|a6 phev": "berline",
    "audi|a7": "berline",
    "audi|a8": "berline",
    "audi|q2": "suv",
    "audi|q3": "suv",
    "audi|q3 sportback": "suv",
    "audi|q4 e-tron": "suv",
    "audi|q5": "suv",
    "audi|q5 sportback": "suv",
    "audi|q6": "suv",
    "audi|q6 e-tron": "suv",
    "audi|q7": "suv",
    "audi|q7 phev": "suv",
    "audi|q8": "suv",
    "audi|rs 3": "berline",
    "audi|rs q8": "suv",
    # --- BAIC ---
    "baic|bj30e": "suv",
    "baic|u5 plus": "berline",
    "baic|x35": "suv",
    "baic|x55": "suv",
    "baic|x7": "suv",
    # --- BENTLEY ---
    "bentley|bentayga": "suv",
    "bentley|continental": "coupe",
    "bentley|continental gt": "coupe",
    "bentley|flying spur": "berline",
    # --- BMW ---
    "bmw|i4": "coupe",
    "bmw|i5": "berline",
    "bmw|ix": "suv",
    "bmw|ix1": "suv",
    "bmw|ix3": "suv",
    "bmw|m2": "coupe",
    "bmw|m4": "coupe",
    "bmw|m5": "berline",
    "bmw|serie 1": "berline",
    "bmw|serie 2 gran coupe": "berline",
    "bmw|serie 3": "berline",
    "bmw|serie 4 cabriolet": "cabriolet",
    "bmw|serie 4 coupe": "coupe",
    "bmw|serie 4 gran coupe": "coupe",
    "bmw|serie 5": "berline",
    "bmw|serie 5 phev": "berline",
    "bmw|serie 7": "berline",
    "bmw|serie 7 phev": "berline",
    "bmw|x1": "suv",
    "bmw|x2": "suv",
    "bmw|x3": "suv",
    "bmw|x4": "suv",
    "bmw|x5": "suv",
    "bmw|x5 m": "suv",
    "bmw|x5 phev": "suv",
    "bmw|x6": "suv",
    "bmw|x7": "suv",
    "bmw|xm": "suv",
    "bmw|z4": "cabriolet",
    # --- BYD ---
    "byd|atto 2": "suv",
    "byd|atto 3": "suv",
    "byd|dolphin": "citadine",
    "byd|han": "berline",
    "byd|seagull": "citadine",
    "byd|seal": "berline",
    "byd|seal 5": "berline",
    "byd|seal u": "suv",
    "byd|seal u phev": "suv",
    "byd|sealion 5": "suv",
    "byd|sealion 7": "suv",
    "byd|tang": "suv",
    # --- CHANGAN ---
    "changan|alsvin": "berline",
    "changan|cs15": "suv",
    "changan|cs35": "suv",
    "changan|cs35 plus": "suv",
    "changan|cs55": "suv",
    "changan|cs55 phev": "suv",
    "changan|cs55 plus": "suv",
    "changan|hunter": "pick_up",
    "changan|uni-k": "suv",
    "changan|uni-t": "suv",
    "changan|uni-v": "berline",
    # --- CHERY ---
    "chery|arrizo 6": "berline",
    "chery|arrizo 8": "berline",
    "chery|himla": "pick_up",
    "chery|tiggo 2 pro": "suv",
    "chery|tiggo 3x": "suv",
    "chery|tiggo 4 cross hev": "suv",
    "chery|tiggo 4 pro": "suv",
    "chery|tiggo 7 pro": "suv",
    "chery|tiggo 7 pro phev": "suv",
    "chery|tiggo 8 pro": "suv",
    "chery|tiggo 8 pro phev": "suv",
    "chery|tiggo 9 phev": "suv",
    # --- CITROEN ---
    "citroen|ami": "citadine",
    "citroen|berlingo": "utilitaire",
    "citroen|c3": "citadine",
    "citroen|c3 aircross": "suv",
    "citroen|c4": "berline",
    "citroen|c4 x": "berline",
    "citroen|c5 aircross": "suv",
    "citroen|e-c4": "berline",
    "citroen|spacetourer": "monospace",
    # --- CUPRA ---
    "cupra|formentor": "suv",
    "cupra|leon": "berline",
    "cupra|terramar": "suv",
    # --- DACIA ---
    "dacia|bigster": "suv",
    "dacia|dokker": "utilitaire",
    "dacia|duster": "suv",
    "dacia|jogger": "monospace",
    "dacia|lodgy": "monospace",
    "dacia|logan": "berline",
    "dacia|sandero": "citadine",
    "dacia|sandero stepway": "suv",
    "dacia|spring": "citadine",
    # --- DEEPAL ---
    "deepal|g318": "suv",
    "deepal|l07": "berline",
    "deepal|s05": "suv",
    "deepal|s07": "suv",
    # --- DFSK ---
    "dfsk|c31": "pick_up",
    "dfsk|c35": "utilitaire",
    "dfsk|e5": "suv",
    "dfsk|fengon ix5": "suv",
    "dfsk|glory 580": "suv",
    "dfsk|k01h": "pick_up",
    "dfsk|k01s": "pick_up",
    # --- DONGFENG ---
    "dongfeng|box": "citadine",
    "dongfeng|forthing t5 evo": "suv",
    "dongfeng|huge": "suv",
    "dongfeng|mage": "suv",
    "dongfeng|shine": "berline",
    "dongfeng|shine max": "berline",
    # --- DS AUTOMOBILES ---
    "ds automobiles|ds 3": "suv",
    "ds automobiles|ds 3 e-tense": "suv",
    "ds automobiles|ds 4": "berline",
    "ds automobiles|ds 7": "suv",
    "ds automobiles|ds 7 e-tense": "suv",
    # --- DS ---
    "ds|ds 3": "suv",
    "ds|ds 4": "berline",
    "ds|ds 7": "suv",
    # --- EXEED ---
    "exeed|es": "berline",
    "exeed|et": "suv",
    "exeed|exlantix es": "berline",
    "exeed|exlantix et": "suv",
    "exeed|lx": "suv",
    "exeed|rx": "suv",
    "exeed|txl": "suv",
    "exeed|vx": "suv",
    # --- FERRARI ---
    "ferrari|12cilindri": "coupe",
    "ferrari|296 gtb": "coupe",
    "ferrari|296 gts": "cabriolet",
    "ferrari|812 superfast": "coupe",
    "ferrari|f8 spider": "cabriolet",
    "ferrari|f8 tributo": "coupe",
    "ferrari|purosangue": "suv",
    "ferrari|roma": "coupe",
    "ferrari|roma spider": "cabriolet",
    "ferrari|sf90": "coupe",
    "ferrari|sf90 spider": "cabriolet",
    "ferrari|sf90 stradale": "coupe",
    # --- FIAT ---
    "fiat|500": "citadine",
    "fiat|500c": "cabriolet",
    "fiat|500e": "citadine",
    "fiat|500x": "suv",
    "fiat|600": "suv",
    "fiat|doblo": "utilitaire",
    "fiat|doblo 7 places": "utilitaire",
    "fiat|doblo cargo": "utilitaire",
    "fiat|fiorino": "utilitaire",
    "fiat|panda": "citadine",
    "fiat|scudo": "utilitaire",
    "fiat|tipo": "berline",
    "fiat|titano": "pick_up",
    "fiat|topolino": "citadine",
    # --- FORD ---
    "ford|fiesta": "citadine",
    "ford|focus": "berline",
    "ford|kuga": "suv",
    "ford|mustang": "coupe",
    "ford|puma": "suv",
    "ford|ranger": "pick_up",
    "ford|ranger next-gen": "pick_up",
    "ford|ranger raptor": "pick_up",
    "ford|territory": "suv",
    "ford|tourneo custom": "utilitaire",
    "ford|transit": "utilitaire",
    "ford|transit 2t": "utilitaire",
    # --- GAC ---
    "gac|emkoo": "suv",
    "gac|emkoo hybride": "suv",
    "gac|empow": "berline",
    "gac|emzoom": "suv",
    "gac|gs3 emzoom": "suv",
    "gac|s7 phev": "suv",
    # --- GEELY ---
    "geely|cityray": "suv",
    "geely|coolray": "suv",
    "geely|emgrand": "berline",
    "geely|ex2": "citadine",
    "geely|ex5 em-i": "suv",
    "geely|geometry c": "suv",
    "geely|gx3 pro": "citadine",
    "geely|monjaro": "suv",
    "geely|riddara rd6": "pick_up",
    # --- GWM ---
    "gwm|haval h6": "suv",
    "gwm|haval h7": "suv",
    "gwm|haval jolion": "suv",
    "gwm|jolion pro": "suv",
    "gwm|ora 03": "citadine",
    "gwm|poer": "pick_up",
    "gwm|tank 300": "suv",
    "gwm|tank 500": "suv",
    "gwm|wey 05": "suv",
    # --- HONDA ---
    "honda|civic": "berline",
    "honda|cr-v": "suv",
    "honda|hr-v": "suv",
    "honda|jazz": "citadine",
    # --- HYUNDAI ---
    "hyundai|accent": "berline",
    "hyundai|bayon": "suv",
    "hyundai|creta": "suv",
    "hyundai|elantra": "berline",
    "hyundai|grand i10": "berline",
    "hyundai|i10": "citadine",
    "hyundai|i20": "citadine",
    "hyundai|i30": "berline",
    "hyundai|ioniq 5": "suv",
    "hyundai|ioniq 6": "berline",
    "hyundai|ix35": "suv",
    "hyundai|kona": "suv",
    "hyundai|santa fe": "suv",
    "hyundai|sonata": "berline",
    "hyundai|staria": "monospace",
    "hyundai|tucson": "suv",
    "hyundai|tucson phev": "suv",
    # --- ISUZU ---
    "isuzu|d-max": "pick_up",
    # --- JAC ---
    "jac|e30x": "citadine",
    "jac|js2": "suv",
    "jac|js4": "suv",
    "jac|js6": "suv",
    "jac|m3 ev": "utilitaire",
    "jac|t8": "pick_up",
    "jac|t8 pro": "pick_up",
    # --- JAECOO ---
    "jaecoo|jaecoo 7": "suv",
    "jaecoo|jaecoo 7 phev": "suv",
    # --- JAGUAR ---
    "jaguar|e-pace": "suv",
    "jaguar|f-pace": "suv",
    "jaguar|f-type": "coupe",
    "jaguar|i-pace": "suv",
    "jaguar|xe": "berline",
    "jaguar|xf": "berline",
    # --- JEEP ---
    "jeep|avenger": "suv",
    "jeep|avenger 4xe": "suv",
    "jeep|compass": "suv",
    "jeep|grand cherokee": "suv",
    "jeep|renegade": "suv",
    "jeep|wrangler": "suv",
    # --- JETOUR ---
    "jetour|dashing": "suv",
    "jetour|t1": "suv",
    "jetour|t2": "suv",
    "jetour|t2 i-dm": "suv",
    "jetour|x70 plus": "suv",
    # --- KG MOBILITY ---
    "kg mobility|grand musso": "pick_up",
    "kg mobility|rexton": "suv",
    "kg mobility|tivoli": "suv",
    "kg mobility|torres": "suv",
    "kg mobility|torres evx": "suv",
    "kg mobility|torres hybrid": "suv",
    # --- KIA ---
    "kia|carnival": "monospace",
    "kia|ceed": "berline",
    "kia|ev3": "suv",
    "kia|ev5": "suv",
    "kia|ev6": "suv",
    "kia|ev9": "suv",
    "kia|niro": "suv",
    "kia|niro hybrid": "suv",
    "kia|picanto": "citadine",
    "kia|rio": "citadine",
    "kia|seltos": "suv",
    "kia|sonet": "suv",
    "kia|sorento": "suv",
    "kia|sportage": "suv",
    "kia|stonic": "suv",
    "kia|tasman": "pick_up",
    # --- LAND ROVER ---
    "land rover|defender": "suv",
    "land rover|discovery": "suv",
    "land rover|discovery sport": "suv",
    "land rover|range rover": "suv",
    "land rover|range rover evoque": "suv",
    "land rover|range rover sport": "suv",
    "land rover|range rover sport sv": "suv",
    "land rover|range rover sv": "suv",
    "land rover|range rover velar": "suv",
    # --- LEAPMOTOR ---
    "leapmotor|b10": "suv",
    "leapmotor|c10": "suv",
    "leapmotor|t03": "citadine",
    # --- LEXUS ---
    "lexus|es": "berline",
    "lexus|is": "berline",
    "lexus|lc": "coupe",
    "lexus|lm": "monospace",
    "lexus|ls": "berline",
    "lexus|nx": "suv",
    "lexus|rx": "suv",
    "lexus|rz": "suv",
    "lexus|ux": "suv",
    # --- LOTUS ---
    "lotus|eletre": "suv",
    "lotus|emeya": "berline",
    "lotus|emira": "coupe",
    "lotus|evija": "coupe",
    # --- LYNK & CO ---
    "lynk & co|01": "suv",
    "lynk & co|02": "suv",
    "lynk & co|03": "berline",
    "lynk & co|06": "suv",
    "lynk & co|08": "suv",
    # --- MAHINDRA ---
    "mahindra|kuv100": "citadine",
    "mahindra|pik-up": "pick_up",
    "mahindra|xuv 3xo": "suv",
    "mahindra|xuv300": "suv",
    # --- MASERATI ---
    "maserati|ghibli": "berline",
    "maserati|grancabrio": "cabriolet",
    "maserati|granturismo": "coupe",
    "maserati|grecale": "suv",
    "maserati|gt2 stradale": "coupe",
    "maserati|levante": "suv",
    "maserati|mc20": "coupe",
    "maserati|mcpura": "coupe",
    # --- MAZDA ---
    "mazda|2": "citadine",
    "mazda|3": "berline",
    "mazda|6": "berline",
    "mazda|cx-3": "suv",
    "mazda|cx-30": "suv",
    "mazda|cx-5": "suv",
    "mazda|cx-60": "suv",
    "mazda|mazda3": "berline",
    "mazda|mazda6": "berline",
    "mazda|mx-5": "cabriolet",
    # --- MERCEDES-BENZ ---
    "mercedes-benz|cla": "coupe",
    "mercedes-benz|classe a": "berline",
    "mercedes-benz|classe a berline": "berline",
    "mercedes-benz|classe b": "monospace",
    "mercedes-benz|classe c": "berline",
    "mercedes-benz|classe e": "berline",
    "mercedes-benz|classe g": "suv",
    "mercedes-benz|classe s": "berline",
    "mercedes-benz|classe v": "utilitaire",
    "mercedes-benz|cle": "coupe",
    "mercedes-benz|cle cabriolet": "cabriolet",
    "mercedes-benz|eqa": "suv",
    "mercedes-benz|eqb": "suv",
    "mercedes-benz|eqe": "berline",
    "mercedes-benz|eqe suv": "suv",
    "mercedes-benz|eqs": "berline",
    "mercedes-benz|eqs suv": "suv",
    "mercedes-benz|gla": "suv",
    "mercedes-benz|glb": "suv",
    "mercedes-benz|glc": "suv",
    "mercedes-benz|glc coupe": "suv",
    "mercedes-benz|gle": "suv",
    "mercedes-benz|gle coupe": "suv",
    "mercedes-benz|gls": "suv",
    "mercedes-benz|mercedes-amg gt": "coupe",
    "mercedes-benz|mercedes-amg sl": "cabriolet",
    "mercedes-benz|mercedes-maybach classe s": "berline",
    "mercedes-benz|mercedes-maybach gls": "suv",
    "mercedes-benz|vle electric": "utilitaire",
    # --- MG ---
    "mg|hs": "suv",
    "mg|mg 3": "citadine",
    "mg|mg 3 hybrid+": "citadine",
    "mg|mg 4": "berline",
    "mg|mg 5": "berline",
    "mg|mg cyberster": "cabriolet",
    "mg|mg hs": "suv",
    "mg|mg hs hybrid+": "suv",
    "mg|mg marvel r": "suv",
    "mg|mg zs": "suv",
    "mg|mg zs hybrid+": "suv",
    "mg|zs": "suv",
    # --- MINI ---
    "mini|aceman": "suv",
    "mini|cooper": "citadine",
    "mini|cooper 5 portes": "citadine",
    "mini|countryman": "suv",
    # --- MITSUBISHI ---
    "mitsubishi|asx": "suv",
    "mitsubishi|eclipse cross": "suv",
    "mitsubishi|l200 double cabine glx": "pick_up",
    "mitsubishi|l200 simple cabine": "pick_up",
    "mitsubishi|l200 sportero": "pick_up",
    "mitsubishi|outlander": "suv",
    # --- NISSAN ---
    "nissan|ariya": "suv",
    "nissan|juke": "suv",
    "nissan|magnite": "suv",
    "nissan|micra": "citadine",
    "nissan|navara": "pick_up",
    "nissan|patrol": "suv",
    "nissan|qashqai": "suv",
    "nissan|x-trail": "suv",
    # --- OMODA ---
    "omoda|omoda 3": "suv",
    "omoda|omoda c5": "suv",
    "omoda|omoda e5": "suv",
    # --- OPEL ---
    "opel|astra": "berline",
    "opel|combo": "utilitaire",
    "opel|corsa": "citadine",
    "opel|crossland": "suv",
    "opel|frontera": "suv",
    "opel|grandland": "suv",
    "opel|mokka": "suv",
    "opel|rocks electric": "citadine",
    # --- PEUGEOT ---
    "peugeot|2008": "suv",
    "peugeot|208": "citadine",
    "peugeot|3008": "suv",
    "peugeot|308": "berline",
    "peugeot|408": "berline",
    "peugeot|5008": "suv",
    "peugeot|508": "berline",
    "peugeot|landtrek": "pick_up",
    "peugeot|partner": "utilitaire",
    "peugeot|rifter": "utilitaire",
    # --- PORSCHE ---
    "porsche|718 boxster": "cabriolet",
    "porsche|718 cayman": "coupe",
    "porsche|911": "coupe",
    "porsche|911 cabriolet": "cabriolet",
    "porsche|911 targa": "cabriolet",
    "porsche|cayenne": "suv",
    "porsche|cayenne coupe": "suv",
    "porsche|cayenne coupe electric": "suv",
    "porsche|cayenne electric": "suv",
    "porsche|macan": "suv",
    "porsche|macan electric": "suv",
    "porsche|panamera": "berline",
    "porsche|taycan": "berline",
    "porsche|taycan cross turismo": "break",
    # --- RENAULT ---
    "renault|5 e tech": "citadine",
    "renault|5 e-tech": "citadine",
    "renault|arkana": "suv",
    "renault|austral": "suv",
    "renault|captur": "suv",
    "renault|clio": "citadine",
    "renault|espace": "suv",
    "renault|express": "utilitaire",
    "renault|kadjar": "suv",
    "renault|kangoo": "utilitaire",
    "renault|kardian": "suv",
    "renault|megane": "berline",
    "renault|megane e-tech": "suv",
    "renault|nouvelle clio": "citadine",
    "renault|rafale": "suv",
    "renault|scenic": "suv",
    "renault|symbioz": "suv",
    "renault|twingo": "citadine",
    "renault|zoe": "citadine",
    # --- ROX MOTOR ---
    "rox motor|rox 01": "suv",
    "rox motor|rox adamas": "suv",
    # --- ROX ---
    "rox|01": "suv",
    "rox|adamas": "suv",
    # --- SEAT ---
    "seat|arona": "suv",
    "seat|ateca": "suv",
    "seat|ibiza": "citadine",
    "seat|leon": "berline",
    "seat|tarraco": "suv",
    # --- SERES ---
    "seres|3": "suv",
    "seres|5": "suv",
    "seres|seres 3": "suv",
    "seres|seres 5": "suv",
    # --- SKODA ---
    "skoda|fabia": "citadine",
    "skoda|kamiq": "suv",
    "skoda|karoq": "suv",
    "skoda|kodiaq": "suv",
    "skoda|kodiaq sportline": "suv",
    "skoda|octavia": "berline",
    "skoda|scala": "berline",
    "skoda|superb": "berline",
    # --- SMART ---
    "smart|#1": "suv",
    "smart|#3": "suv",
    "smart|#5": "suv",
    # --- SOUEAST ---
    "soueast|s05": "suv",
    "soueast|s06": "suv",
    "soueast|s07": "suv",
    "soueast|s08": "suv",
    "soueast|s09": "suv",
    # --- SUZUKI ---
    "suzuki|baleno": "citadine",
    "suzuki|celerio": "citadine",
    "suzuki|ertiga": "monospace",
    "suzuki|fronx": "suv",
    "suzuki|ignis": "suv",
    "suzuki|jimny": "suv",
    "suzuki|s-cross": "suv",
    "suzuki|s-presso": "citadine",
    "suzuki|swift": "citadine",
    "suzuki|vitara": "suv",
    # --- TESLA ---
    "tesla|cybertruck": "pick_up",
    "tesla|model 3": "berline",
    "tesla|model s": "berline",
    "tesla|model x": "suv",
    "tesla|model y": "suv",
    # --- TOYOTA ---
    "toyota|aygo": "citadine",
    "toyota|bz4x": "suv",
    "toyota|c-hr": "suv",
    "toyota|camry": "berline",
    "toyota|corolla": "berline",
    "toyota|corolla cross": "suv",
    "toyota|corolla x suv": "suv",
    "toyota|fortuner": "suv",
    "toyota|hilux": "pick_up",
    "toyota|land cruiser": "suv",
    "toyota|proace": "utilitaire",
    "toyota|rav-4": "suv",
    "toyota|rav4": "suv",
    "toyota|yaris": "citadine",
    "toyota|yaris cross": "suv",
    # --- VOLKSWAGEN ---
    "volkswagen|caddy": "utilitaire",
    "volkswagen|golf": "berline",
    "volkswagen|golf 8": "berline",
    "volkswagen|new t-roc": "suv",
    "volkswagen|passat": "berline",
    "volkswagen|polo": "citadine",
    "volkswagen|t-cross": "suv",
    "volkswagen|t-roc": "suv",
    "volkswagen|taigo": "suv",
    "volkswagen|tiguan": "suv",
    "volkswagen|touareg": "suv",
    "volkswagen|touran": "monospace",
    # --- VOLVO ---
    "volvo|ec40": "suv",
    "volvo|es90": "berline",
    "volvo|ex30": "suv",
    "volvo|ex90": "suv",
    "volvo|s60": "berline",
    "volvo|s90": "berline",
    "volvo|xc40": "suv",
    "volvo|xc60": "suv",
    "volvo|xc90": "suv",
    # --- XPENG ---
    "xpeng|g6": "suv",
    "xpeng|g9": "suv",
    "xpeng|p7": "berline",
    "xpeng|p7+": "berline",
    # --- ZEEKR ---
    "zeekr|001": "break",
    "zeekr|7x": "suv",
    "zeekr|x": "suv",
}


def _body_type_model_key(brand: str, model: str) -> str:
    """Build an accent-insensitive key for stable model-level overrides."""
    value = unicodedata.normalize("NFKD", f"{brand}|{model}")
    value = "".join(ch for ch in value if not unicodedata.combining(ch))
    return re.sub(r"\s+", " ", value.casefold().strip())


# ═══════════════════════════════════════════════════════════════════════════
# 2. CONVERTISSEURS & PARSEURS TYPÉS
# ═══════════════════════════════════════════════════════════════════════════

def parse_price(val: Any) -> Optional[float]:
    """Extrait le prix numérique en Dirhams marocains (MAD)."""
    if val is None or val == "":
        return None
    if isinstance(val, (int, float)):
        return float(val)
    # Nettoyage chaîne "152 000 DH" ou "152000"
    cleaned = re.sub(r"[^\d.]", "", str(val).replace(" ", "").replace(",", "."))
    try:
        return float(cleaned) if cleaned else None
    except ValueError:
        return None


def parse_numeric(val: Any, target_type=float) -> Optional[Any]:
    """Parse un champ numérique (entier ou décimal)."""
    if val is None or val == "":
        return None
    if isinstance(val, (int, float)):
        return target_type(val)
    cleaned = re.sub(r"[^\d.]", "", str(val).replace(" ", "").replace(",", "."))
    try:
        return target_type(float(cleaned)) if cleaned else None
    except ValueError:
        return None


def parse_4x4(val: Any) -> bool:
    """
    Parse le champ 4x4 vers un booléen strict.
    'Oui', 'True', '1' -> True
    'Non', 'False', '0', None -> False
    """
    if not val:
        return False
    val_str = str(val).strip().lower()
    return val_str in ["oui", "yes", "true", "1", "4x4", "awd", "4wd"]


def parse_ncap_rating(val: Any) -> str:
    """
    Conserve le texte réel de la note EuroNCAP / GlobalNCAP sans altération.
    Exemples: '2★', '5★ (GlobalNCAP)', 'Non testé', 'NT'.
    Cette chaîne brute ne doit jamais être convertie sur l'échelle 1-5 Wakala.
    """
    if val is None or str(val).strip() == "":
        return "Non testé"
    return str(val).strip()


def parse_engine_and_autonomy(autonomy_raw: Any, version: str) -> Tuple[str, Optional[int]]:
    """
    Convertit la colonne 'Autonomie km' en:
    - engine_type : "Thermique", "Électrique", "Hybride", "Hybride Rechargeable"
    - autonomy_km : valeur numérique en km si électrique / hybride rechargeable.
    """
    raw_str = str(autonomy_raw or "").strip()
    version_lower = str(version or "").lower()
    
    # Recherche d'autonomie numérique (ex: "450 km", "85 km (EV)")
    km_match = re.search(r"(\d+)\s*(?:km)?", raw_str)
    autonomy_km = int(km_match.group(1)) if km_match else None
    
    if "electrique" in version_lower or "électrique" in version_lower or "ev" in raw_str.lower():
        if "phev" in version_lower or "rechargeable" in version_lower:
            engine_type = "Hybride Rechargeable"
        else:
            engine_type = "Électrique"
    elif "hybride" in version_lower or "hybrid" in version_lower or raw_str.lower() == "hybride":
        if "phev" in version_lower or "rechargeable" in version_lower:
            engine_type = "Hybride Rechargeable"
        else:
            engine_type = "Hybride"
    elif raw_str.lower() == "thermique" or raw_str == "":
        engine_type = "Thermique"
    else:
        # Si une autonomie km est indiquée mais sans mention explicite
        if autonomy_km and autonomy_km > 150:
            engine_type = "Électrique"
        elif autonomy_km and autonomy_km <= 150:
            engine_type = "Hybride Rechargeable"
        else:
            engine_type = raw_str
            
    return engine_type, autonomy_km


def infer_fuel_type(autonomy_raw: Any, version: str, conso: Optional[float], co2: Optional[float], source_text: str = "") -> str:
    """
    Déduit l'enum fuel_type compatible PostgreSQL :
    'essence', 'diesel', 'hybride', 'hybride_rechargeable', 'electrique', 'gpl', 'hydrogene'
    """
    var_lower = str(version or "").lower()
    auto_lower = str(autonomy_raw or "").lower()
    src_lower = str(source_text or "").lower()
    
    # 1. 100% Électrique
    if (conso == 0 and co2 == 0) or "100% électrique" in var_lower or "full electric" in var_lower:
        return "electrique"
    if ("electrique" in var_lower or "électrique" in var_lower or "ev" in auto_lower) and not any(k in var_lower for k in ["phev", "rechargeable", "plug-in", "prolongateur"]):
        if conso is None or conso == 0:
            return "electrique"
            
    # 2. Hybride Rechargeable (PHEV)
    if any(k in var_lower for k in ["phev", "plug-in", "rechargeable", "e-hybrid"]) or "prolongateur" in auto_lower:
        return "hybride_rechargeable"
        
    # 3. Hybride Simple (HEV / MHEV)
    if any(k in var_lower for k in ["hybride", "hybrid", "hev", "mhev", "e-tech", "micro-hybride"]) or auto_lower == "hybride":
        return "hybride"
        
    # 4. Diesel
    if any(k in var_lower for k in ["diesel", "dci", "tdi", "bluehdi", "hdi", "cdti", "crdi", "d-4d", "d-id", "multijet", "citan"]) or "diesel" in src_lower:
        return "diesel"
        
    # 5. GPL / Hydrogène
    if "gpl" in var_lower:
        return "gpl"
    if "hydrogene" in var_lower or "hydrogène" in var_lower:
        return "hydrogene"
        
    # 6. Essence par défaut
    return "essence"


def infer_body_type(brand: str, model: str, version: str, length_cm: Optional[int], is_4x4: bool, offroad_score: Optional[float], row: Optional[Dict[str, Any]] = None) -> str:
    """
    Déduit l'enum body_type compatible PostgreSQL :
    'citadine', 'berline', 'suv', 'break', 'coupe', 'cabriolet', 'monospace', 'utilitaire', 'pick_up'
    """
    # 0. Colonne explicite dans le fichier source ou la ligne
    if row:
        for col_name in ("[AG] Carrosserie", "Carrosserie", "carrosserie", "Type Carrosserie"):
            val = str(row.get(col_name) or "").strip().lower()
            if val in ("citadine", "berline", "suv", "break", "coupe", "cabriolet", "monospace", "utilitaire", "pick_up"):
                return val
    combined = f"{brand} {model} {version}".lower()
    model_text = f"{brand} {model}".lower()
    version_text = str(version or "").lower()
    length = length_cm or 420
    tt = offroad_score or 1

    # Prefer an explicit model classification over marketing/trim words such
    # as "GT", "Fastback" or "SUV Coupé". They describe styling or a grade,
    # not necessarily a different catalogue body type.
    model_override = MODEL_BODY_TYPE_OVERRIDES.get(_body_type_model_key(brand, model))
    if model_override:
        return model_override

    if brand.lower() == "ferrari":
        if "purosangue" in model_text:
            return "suv"
        if any(k in model_text or k in version_text for k in ["spider", "cabriolet", "convertible", "gts", "aperta"]):
            return "cabriolet"
        return "coupe"

    # Explicit body-style wording in a trim is authoritative. Do not use
    # broad substring checks here: "GT" is often only a trim line and "van"
    # is part of words such as "avant".
    if re.search(r"\b(cabriolet|convertible|spider|roadster)\b", version_text):
        return "cabriolet"
    if re.search(r"\b(coupe|coupé|fastback)\b", version_text):
        return "coupe"
    
    # Pick-up
    if any(k in model_text for k in ["pick-up", "pickup", "pik-up", "hilux", "ranger", "d-max", "l200", "navara", "gladiator", "landtrek", "titano", "himla", "hunter", "poer", "tasman", "musso", "scorpio pik", "t8 pro"]):
        return "pick_up"
        
    # Utilitaire / Van
    if any(k in model_text for k in ["utilitaire", "transit", "berlingo", "partner", "kangoo", "caddy", "combo", "dokker", "express", "proace", "expert", "jumpy"]):
        return "utilitaire"
        
    # Cabriolet / Spider
    if any(k in model_text for k in ["cabriolet", "spider", "convertible", "roadster"]):
        return "cabriolet"
        
    # Coupé
    if any(k in model_text for k in ["coupe", "coupé", "4-door coupe", "grancoupe", "gran coupe", "taycan", "panamera", "a110", "911", "f-type", "mcpura", "db12", "vantage", "continental gt", "408"]):
        if not any(k in model_text for k in ["suv", "cross", "stepway"]):
            return "coupe"
            
    # Break
    if any(k in model_text for k in ["break", "touring", "estate", "sportwagon", "shooting brake"]):
        return "break"
        
    # Monospace
    if any(k in model_text for k in ["monospace", "touran", "scenic", "espace", "spacetourer", "space tourer", "zafira", "carens", "altea", "sharan"]):
        return "monospace"
        
    # SUV / Crossover
    suv_keywords = [
        "suv", "crossover", "stepway", "duster", "austral", "qashqai", "tucson", "sportage", "tiguan",
        "karoq", "ateca", "3008", "2008", "5008", "xc40", "xc60", "xc90", "t-roc", "t-cross", "touareg",
        "x1", "x2", "x3", "x4", "x5", "x6", "x7", "ix", "q2", "q3", "q4", "q5", "q6", "q7", "q8", "gla", "glb", "glc",
        "gle", "gls", "cr-v", "hr-v", "rav4", "yaris cross", "korando", "rexton", "tivoli", "defender",
        "discovery", "evoque", "velar", "range rover", "cayenne", "macan", "urus", "levante", "grecale", "avenger", "bayon", "f-pace", "e-pace", "fortuner", "land cruiser", "pajero", "vitara", "cityray", "coolray", "starray", "t2", "traveller", "g318", "g9", "txl", "vx", "c11", "seres 7", "uni-k", "cs15", "cs35", "cs55", "uni-t", "uni-k", "s7", "santa fe", "ev6", "ev9", "dfsk e5", "marvel-r", "marvel r", "jaecoo", "omoda c5", "tank", "grand vitara", "grandland", "frontera", "okavango", "seal u", "seal-u", "yaris cross", "ioniq 5", "zeekr 001", "zeekr x", "zeekr 7x",
        "gv70", "gv80", "tang", "song", "yuan", "atto", "sealion", "seal u", "haval", "tiggo", "coolray",
        "monjaro", "stonic", "niro", "sorento", "santa fe", "kuga", "puma", "explorer", "capri", "c3 aircross",
        "c5 aircross", "arkana", "kadjar", "captur", "kamiq", "kodiaq", "mokka", "grandland", "crossland",
        "compass", "renegade", "wrangler", "cherokee", "cx-30", "cx-5", "cx-60", "outlander", "asx", "xm", "aceman", "rocks-e",
        "eclipse cross", "juke", "x-trail", "ariya", "formentor", "terramar", "tavascan", "countryman"
        , "stelvio", "tonale", "bj30", "ev6", "ioniq 5", "nx", "model y", "rav-4"
    ]
    if any(k in model_text for k in suv_keywords):
        return "suv"
        
    # Citadine
    citadine_keywords = [
        "citadine", "clio", "208", "c3", "sandero", "yaris", "polo", "i10", "i20", "picanto",
        "rio", "swift", "micra", "fiesta", "fabia", "ibiza", "corsa", "spring", "zoe", "500",
        "panda", "twingo", "aygo", "dolphin", "seagull", "mini 3"
    ]
    if length <= 415 or any(k in model_text for k in citadine_keywords):
        return "citadine"
        
    # Berline par défaut pour les routières
    return "berline"


def infer_transmission(version: str, fuel_type: str) -> str:
    """
    Déduit l'enum transmission : 'manuelle', 'automatique', 'semi_auto'
    """
    var_lower = str(version or "").lower()
    auto_keywords = [
        "bva", "auto", "boîte auto", "boite auto", "cvt", "e-cvt", "edc", "dsg", "eat8", "eat6",
        "dct", "s-tronic", "tiptronic", "pdk", "9g-tronic", "7g-tronic", "steptronic", "direct shift"
    ]
    if fuel_type in ["electrique", "hybride_rechargeable", "hybride"]:
        return "automatique"
    if any(k in var_lower for k in auto_keywords):
        return "automatique"
    return "manuelle"


def infer_doors_and_seats(body_type: str) -> Tuple[int, int]:
    """Déduit le nombre standard de portes et de places selon la carrosserie."""
    if body_type in ["coupe", "cabriolet"]:
        return 3, 4
    if body_type == "pick_up":
        return 4, 5
    if body_type == "utilitaire":
        return 3, 3
    if body_type == "monospace":
        return 5, 7
    return 5, 5


# ═══════════════════════════════════════════════════════════════════════════
# 3. MAPPING D'UNE LIGNE EXCEL COMPLÈTE
# ═══════════════════════════════════════════════════════════════════════════

def map_excel_row_to_vehicle_data(row: Dict[str, Any]) -> Tuple[Dict[str, Any], Dict[str, Any]]:
    """
    Transforme une ligne Excel brute en deux dictionnaires propres et typés :
    1. vehicle_dict (pour la table 'vehicles')
    2. wakala_scores_dict (pour la table 'vehicle_wakala_scores')
    """
    # Extraction brute
    brand = str(row.get(EXCEL_COLUMN_HEADERS["brand"]) or "").strip()
    model = str(row.get(EXCEL_COLUMN_HEADERS["model"]) or "").strip()
    version = str(row.get(EXCEL_COLUMN_HEADERS["version"]) or "").strip()
    price = parse_price(row.get(EXCEL_COLUMN_HEADERS["price"]))
    trunk_volume_l = parse_numeric(row.get(EXCEL_COLUMN_HEADERS["trunk_volume_l"]), int)
    ncap_rating = parse_ncap_rating(row.get(EXCEL_COLUMN_HEADERS["ncap_rating"]))
    fuel_consumption = parse_numeric(row.get(EXCEL_COLUMN_HEADERS["fuel_consumption"]), float)
    engine_power_hp = parse_numeric(row.get(EXCEL_COLUMN_HEADERS["engine_power_hp"]), int)
    co2_emissions = parse_numeric(row.get(EXCEL_COLUMN_HEADERS["co2_emissions"]), float)
    length_cm = parse_numeric(row.get(EXCEL_COLUMN_HEADERS["length_cm"]), int)
    is_4x4 = parse_4x4(row.get(EXCEL_COLUMN_HEADERS["is_4x4"]))
    autonomy_raw = row.get(EXCEL_COLUMN_HEADERS["autonomy_raw"])
    
    # Inférences
    engine_type, autonomy_km = parse_engine_and_autonomy(autonomy_raw, version)
    fuel_type = infer_fuel_type(autonomy_raw, version, fuel_consumption, co2_emissions, str(row.get(EXCEL_COLUMN_HEADERS["source_note"])))
    offroad_score = parse_numeric(row.get(EXCEL_COLUMN_HEADERS["offroad_score"]), float)
    body_type = infer_body_type(brand, model, version, length_cm, is_4x4, offroad_score, row=row)
    transmission = infer_transmission(version, fuel_type)
    doors, seats = infer_doors_and_seats(body_type)
    
    # Description enrichie automatique
    description_lines = [
        f"Véhicule Neuf Officiel — {brand} {model} {version}.",
        f"Motorisation : {engine_type} ({fuel_type.capitalize()}) - {engine_power_hp or 'N/C'} ch.",
        f"Transmission : {transmission.capitalize()} | 4x4 : {'Oui' if is_4x4 else 'Non'}.",
        f"Volume du coffre : {trunk_volume_l or 'N/C'} L | Longueur : {length_cm or 'N/C'} cm.",
        f"Sécurité crash-test : {ncap_rating}.",
    ]
    if fuel_consumption:
        description_lines.append(f"Consommation mixte : {fuel_consumption} L/100km.")
    if co2_emissions:
        description_lines.append(f"Émissions de CO2 : {co2_emissions} g/km.")
    if autonomy_km:
        description_lines.append(f"Autonomie électrique : {autonomy_km} km.")
    description = "\n".join(description_lines)

    vehicle_data = {
        "brand": brand,
        "model": model,
        "version": version,
        "year": 2026,
        "mileage": 0,
        "fuel_type": fuel_type,
        "body_type": body_type,
        "transmission": transmission,
        "engine_power_hp": engine_power_hp,
        "doors": doors,
        "seats": seats,
        "city": "Casablanca",
        "postal_code": "20000",
        "price": price,
        "trunk_volume_l": trunk_volume_l,
        "ncap_rating": ncap_rating,
        "fuel_consumption": fuel_consumption,
        "co2_emissions": co2_emissions,
        "length_cm": length_cm,
        "is_4x4": is_4x4,
        "engine_type": engine_type,
        "condition": "new",
        "source": "wakala_catalogue",
        "status": "available",
        "description": description,
    }

    # Scores Wakala (1-5)
    wakala_scores_data = {
        "space_score": parse_numeric(row.get(EXCEL_COLUMN_HEADERS["space_score"]), float),
        "safety_score": parse_numeric(row.get(EXCEL_COLUMN_HEADERS["safety_score"]), float),
        "real_cost_score": parse_numeric(row.get(EXCEL_COLUMN_HEADERS["real_cost_score"]), float),
        "access_price_score": parse_numeric(row.get(EXCEL_COLUMN_HEADERS["access_price_score"]), float),
        "city_practicality_score": parse_numeric(row.get(EXCEL_COLUMN_HEADERS["city_practicality_score"]), float),
        "performance_score": parse_numeric(row.get(EXCEL_COLUMN_HEADERS["performance_score"]), float),
        "ecology_score": parse_numeric(row.get(EXCEL_COLUMN_HEADERS["ecology_score"]), float),
        "offroad_score": offroad_score,
        "overall_score": parse_numeric(row.get(EXCEL_COLUMN_HEADERS["overall_score"]), float),
        "data_reliability": str(row.get(EXCEL_COLUMN_HEADERS["data_reliability"]) or "").strip() or None,
        "observations": str(row.get(EXCEL_COLUMN_HEADERS["observations"]) or "").strip() or None,
        "source_note": str(row.get(EXCEL_COLUMN_HEADERS["source_note"]) or "").strip() or None,
    }

    return vehicle_data, wakala_scores_data
