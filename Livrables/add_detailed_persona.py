import json, uuid, time, sys

SRC = r"d:\Projet automobile\vente-auto-platform\Livrables\wakala_architecture_complete_explique.excalidraw"

def uid():  return uuid.uuid4().hex[:20]
def ts():   return int(time.time() * 1000)

ALL = []

# Colors
DARK   = "#1e1e1e"
SUB    = "#495057"
MUTED  = "#868e96"
SKY_BG, SKY_STR       = "#d0ebff", "#1864ab"
ROSE_BG, ROSE_STR     = "#ffe0eb", "#a61e4d"
INDIGO_BG, INDIGO_STR = "#dbe4ff", "#364fc7"
VIOLET_BG, VIOLET_STR = "#f3d9fa", "#862e9c"
TEAL_BG, TEAL_STR     = "#c3fae8", "#087f5b"
AMBER_BG, AMBER_STR   = "#fff3bf", "#e67700"
GREEN_BG, GREEN_STR   = "#d3f9d8", "#2b8a3e"
CODE_BG = "#2b2b2b"
CODE_FG = "#a9b7c6"

def rect(x, y, w, h, bg, stroke, sw=2, rx=3):
    return {"id": uid(), "type": "rectangle", "x": x, "y": y, "width": w, "height": h,
            "angle": 0, "strokeColor": stroke, "backgroundColor": bg,
            "fillStyle": "solid", "strokeWidth": sw, "strokeStyle": "solid",
            "roughness": 0, "opacity": 100,
            "groupIds": [], "frameId": None, "roundness": {"type": rx},
            "seed": abs(hash(uid())) % 2**31, "version": 1, "versionNonce": abs(hash(uid())) % 2**31,
            "isDeleted": False, "boundElements": [], "updated": ts(),
            "link": None, "locked": False}

def txt(x, y, text, sz=14, color=SUB, align="left", w=None, lh=1.25, vAlign="middle", bold=False, fontFam=1):
    lines = text.count("\n") + 1
    return {"id": uid(), "type": "text", "x": x, "y": y,
            "width": w or max(len(l) for l in text.split("\n")) * sz * 0.62,
            "height": sz * lh * lines,
            "angle": 0, "strokeColor": color, "backgroundColor": "transparent",
            "fillStyle": "solid", "strokeWidth": 1, "strokeStyle": "solid",
            "roughness": 0, "opacity": 100,
            "groupIds": [], "frameId": None, "roundness": None,
            "seed": abs(hash(uid())) % 2**31, "version": 1, "versionNonce": abs(hash(uid())) % 2**31,
            "isDeleted": False, "boundElements": [], "updated": ts(),
            "link": None, "locked": False,
            "text": text, "originalText": text,
            "fontSize": sz, "fontFamily": fontFam, # 1=handdrawn, 2=normal, 3=monospace
            "textAlign": align, "verticalAlign": vAlign,
            "baseline": sz, "containerId": None,
            "autoResize": True, "lineHeight": lh}

def arrow(x1, y1, x2, y2, color=SUB, sw=2, dashed=False):
    return {"id": uid(), "type": "arrow", "x": x1, "y": y1,
            "width": abs(x2-x1) if x2 != x1 else 0, "height": abs(y2-y1) if y2 != y1 else 0,
            "angle": 0, "strokeColor": color, "backgroundColor": "transparent",
            "fillStyle": "solid", "strokeWidth": sw,
            "strokeStyle": "dashed" if dashed else "solid",
            "roughness": 0, "opacity": 100,
            "groupIds": [], "frameId": None, "roundness": {"type": 2},
            "seed": abs(hash(uid())) % 2**31, "version": 1, "versionNonce": abs(hash(uid())) % 2**31,
            "isDeleted": False, "boundElements": [], "updated": ts(),
            "link": None, "locked": False,
            "points": [[0, 0], [x2-x1, y2-y1]],
            "lastCommittedPoint": None,
            "startBinding": None, "endBinding": None,
            "startArrowhead": None, "endArrowhead": "arrow"}

def ellipse(x, y, w, h, bg, stroke, sw=2):
    return {"id": uid(), "type": "ellipse", "x": x, "y": y, "width": w, "height": h,
            "angle": 0, "strokeColor": stroke, "backgroundColor": bg,
            "fillStyle": "solid", "strokeWidth": sw, "strokeStyle": "solid",
            "roughness": 0, "opacity": 100,
            "groupIds": [], "frameId": None, "roundness": None,
            "seed": abs(hash(uid())) % 2**31, "version": 1, "versionNonce": abs(hash(uid())) % 2**31,
            "isDeleted": False, "boundElements": [], "updated": ts(),
            "link": None, "locked": False}

def add(*elems):
    ALL.extend(elems)

X0 = 1580
W_FULL = 920
Y_START = 1070

# Outer container
CONTAINER_H = 1450
add(
    txt(X0 + 5, Y_START, "EXEMPLE DÉTAILLÉ DE BOUT EN BOUT  --  Cas : Karim", sz=14, color=MUTED, w=500),
    rect(X0 - 5, Y_START + 25, W_FULL + 10, CONTAINER_H, "#f8f9fa", "#ced4da", sw=1.5)
)

step_x = X0 + 15
card_x = step_x + 42
card_w = W_FULL - 60
mid = card_x + card_w // 2

# STEP 1
Y = Y_START + 45
add(
    ellipse(step_x, Y + 3, 28, 28, SKY_STR, SKY_STR, sw=0),
    txt(step_x + 6, Y + 6, "1", sz=16, color="#fff", w=16, align="center"),
    rect(card_x, Y, card_w, 100, SKY_BG, SKY_STR, sw=1.5),
    txt(card_x + 20, Y + 10, "Profil Utilisateur & Requête Initiale", sz=16, color=SKY_STR, w=card_w - 40),
    txt(card_x + 20, Y + 35,
        "Karim, 35 ans | Persona : 'Famille_Pragmatique' | ID : FP-024\n"
        "Pain points : Déteste les pannes, cherche l'espace, budget contraint.\n"
        "Requête Vocale (\U0001F3A4) : \"Bghit tomobil robuste l3aila fiha 5 d nass, w max 140k dh.\"",
        sz=13, color=SUB, w=card_w - 40, lh=1.35)
)
add(arrow(mid, Y + 100, mid, Y + 130, MUTED, 1.5))

# STEP 2
Y = Y + 130
add(
    ellipse(step_x, Y + 3, 28, 28, ROSE_STR, ROSE_STR, sw=0),
    txt(step_x + 6, Y + 6, "2", sz=16, color="#fff", w=16, align="center"),
    rect(card_x, Y, card_w, 200, ROSE_BG, ROSE_STR, sw=1.5),
    txt(card_x + 20, Y + 10, "Extraction NLP : Speech-to-Text, Détection Langue & Contraintes", sz=16, color=ROSE_STR, w=card_w - 40),
    
    txt(card_x + 20, Y + 35,
        "1. STT (Whisper) : Transcription audio vers texte.\n"
        "2. Détection de Langue : [Darija (ar-MA)] détectée (Support: Darija, FR, EN).\n"
        "3. Le LLM traduit et sépare les contraintes dures (SQL) des attributs doux (Vectoriels) :", sz=13, color=SUB, w=card_w - 40, lh=1.3),
        
    rect(card_x + 20, Y + 100, 300, 70, "#fff", ROSE_STR, sw=1),
    txt(card_x + 30, Y + 105,
        "{\n  \"hard_filters\": {\"budget_max\": 140000, \"places_min\": 5},\n  \"soft_features\": [\"familiale\", \"robuste\"]\n}",
        sz=12, color=ROSE_STR, w=280, lh=1.2, fontFam=3),
    txt(card_x + 340, Y + 105,
        "→ Les 'hard_filters' sont appliqués sur PostgreSQL.\n"
        "Cela élimine 60% du catalogue (voitures trop chères\nou trop petites). Seuls les candidats viables passent\nà l'étape suivante.",
        sz=13, color=SUB, w=500, lh=1.3)
)
add(arrow(mid, Y + 200, mid, Y + 230, MUTED, 1.5))

# STEP 3
Y = Y + 230
add(
    ellipse(step_x, Y + 3, 28, 28, VIOLET_STR, VIOLET_STR, sw=0),
    txt(step_x + 6, Y + 6, "3", sz=16, color="#fff", w=16, align="center"),
    rect(card_x, Y, card_w, 240, VIOLET_BG, VIOLET_STR, sw=1.5),
    txt(card_x + 20, Y + 10, "Moteur Vectoriel Qdrant — Filtrage par Contenu & Indexation HNSW", sz=16, color=VIOLET_STR, w=card_w - 40),
    
    txt(card_x + 20, Y + 35,
        "Modèle d'Embedding : OpenAI text-embedding-3 (1536 dimensions) ou BGE-m3\n"
        "Indexation : Algorithme HNSW (Hierarchical Navigable Small World) pour une recherche ANN ultra-rapide.", sz=13, color=SUB, w=card_w - 40, lh=1.3),
        
    txt(card_x + 40, Y + 85,
        "V_karim = [0.82, -0.11, 0.94, ..., 0.05]  (dim=1536)\n"
        "V_lodgy = [0.78, -0.15, 0.92, ..., 0.10]  (dim=1536)",
        sz=13, color=VIOLET_STR, w=300, lh=1.3, fontFam=3),
        
    rect(card_x + 380, Y + 75, 460, 150, "#fff", VIOLET_STR, sw=1),
    txt(card_x + 390, Y + 80,
        "Formule de la Similarité Cosinus :", sz=14, color=VIOLET_STR, w=440),
    txt(card_x + 390, Y + 110,
        "Cos(\u03B8) = \u03A3(A_i * B_i) / (\u221A\u03A3(A_i\u00B2) * \u221A\u03A3(B_i\u00B2))", sz=16, color=DARK, w=440, fontFam=3),
    txt(card_x + 390, Y + 150,
        "Développement :\n"
        "= (0.82*0.78 + -0.11*-0.15 + ...) / (1.0 * 1.0)\n"
        "Score_Contenu (Lodgy) = 0.94  (94%)", sz=13, color=SUB, w=440, lh=1.3)
)
add(arrow(mid, Y + 240, mid, Y + 270, MUTED, 1.5))

# STEP 4
Y = Y + 270
add(
    ellipse(step_x, Y + 3, 28, 28, AMBER_STR, AMBER_STR, sw=0),
    txt(step_x + 6, Y + 6, "4", sz=16, color="#fff", w=16, align="center"),
    rect(card_x, Y, card_w, 300, AMBER_BG, AMBER_STR, sw=1.5),
    txt(card_x + 20, Y + 10, "Moteur Graphe Neo4j — Filtrage Collaboratif & Cypher", sz=16, color=AMBER_STR, w=card_w - 40),
    
    # Mini Graph Enrichi
    ellipse(card_x + 30, Y + 50, 70, 40, "#fff", AMBER_STR),
    txt(card_x + 35, Y + 55, "(:User)\nid:'Karim'", sz=11, color=DARK, w=60, align="center", lh=1.2),
    
    arrow(card_x + 100, Y + 70, card_x + 170, Y + 70, AMBER_STR, 1.5),
    txt(card_x + 105, Y + 50, "BELONGS_TO", sz=10, color=AMBER_STR, w=60, align="center"),
    
    ellipse(card_x + 170, Y + 50, 90, 40, "#fff", AMBER_STR),
    txt(card_x + 175, Y + 55, "(:Persona)\nseg:'Famille'", sz=11, color=DARK, w=80, align="center", lh=1.2),
    
    arrow(card_x + 330, Y + 70, card_x + 260, Y + 70, AMBER_STR, 1.5),
    txt(card_x + 270, Y + 50, "BELONGS_TO", sz=10, color=AMBER_STR, w=60, align="center"),
    
    ellipse(card_x + 330, Y + 50, 70, 40, "#fff", AMBER_STR),
    txt(card_x + 335, Y + 55, "(:User)\nid:'Youssef'", sz=11, color=DARK, w=60, align="center", lh=1.2),
    
    arrow(card_x + 400, Y + 70, card_x + 480, Y + 70, AMBER_STR, 1.5),
    txt(card_x + 405, Y + 50, "SAVED {w:3}", sz=10, color=AMBER_STR, w=70, align="center"),
    
    rect(card_x + 480, Y + 50, 80, 40, "#fff", AMBER_STR, rx=2),
    txt(card_x + 485, Y + 55, "(:Car)\nmod:'Lodgy'", sz=11, color=DARK, w=70, align="center", lh=1.2),
    
    # Requête Cypher (Code Block)
    rect(card_x + 20, Y + 110, 520, 110, CODE_BG, CODE_BG, rx=1),
    txt(card_x + 30, Y + 115,
        "MATCH (u:User {id:'Karim'})-[:BELONGS_TO]->(p:Persona)<-[:BELONGS_TO]-(other:User)\n"
        "MATCH (other)-[r:INTERACTED]->(c:Car)\n"
        "RETURN c.id, sum(r.weight * r.recency) as collab_score\n"
        "ORDER BY collab_score DESC",
        sz=12, color=CODE_FG, w=500, lh=1.4, fontFam=3),
    
    txt(card_x + 560, Y + 110,
        "Calcul du Score Collaboratif :\n"
        "Youssef (même segment) a SAUVEGARDÉ (w=3)\n"
        "le Lodgy il y a 2 jours (recency=0.95).\n\n"
        "Amina (même segment) a VU (w=1)\n"
        "le Lodgy aujourd'hui (recency=1.0).\n\n"
        "\u03A3 = (3 * 0.95) + (1 * 1.0) = 3.85",
        sz=13, color=SUB, w=300, lh=1.3)
)
add(arrow(mid, Y + 300, mid, Y + 330, MUTED, 1.5))

# STEP 5
Y = Y + 330
add(
    ellipse(step_x, Y + 3, 28, 28, TEAL_STR, TEAL_STR, sw=0),
    txt(step_x + 6, Y + 6, "5", sz=16, color="#fff", w=16, align="center"),
    rect(card_x, Y, card_w, 110, TEAL_BG, TEAL_STR, sw=1.5),
    txt(card_x + 20, Y + 10, "Orchestrateur — Pondération Dynamique & Fusion", sz=16, color=TEAL_STR, w=card_w - 40),
    txt(card_x + 20, Y + 35,
        "Poids actuels pour Karim (historique modéré) : W1 (Contenu) = 0.65, W2 (Collaboratif) = 0.35\n"
        "Score_Final = W1 * Score_Contenu + W2 * (Score_Collab / Max_Collab)", sz=13, color=SUB, w=card_w - 40, lh=1.3),
    rect(card_x + 20, Y + 75, card_w - 40, 25, "#fff", TEAL_STR, sw=1),
    txt(card_x + 30, Y + 79,
        "Dacia Lodgy :   Score = 0.65 * 0.94  +  0.35 * (3.85 / 5.0)  =  0.611 + 0.269  =  0.880  (88.0%)",
        sz=13, color=TEAL_STR, w=card_w - 60)
)
add(arrow(mid, Y + 110, mid, Y + 140, MUTED, 1.5))

# STEP 6
Y = Y + 140
add(
    ellipse(step_x, Y + 3, 28, 28, GREEN_STR, GREEN_STR, sw=0),
    txt(step_x + 6, Y + 6, "6", sz=16, color="#fff", w=16, align="center"),
    rect(card_x, Y, card_w, 110, GREEN_BG, GREEN_STR, sw=1.5),
    txt(card_x + 20, Y + 10, "Résultat Final et Explicabilité IA", sz=16, color=GREEN_STR, w=card_w - 40),
    rect(card_x + 20, Y + 35, card_w - 40, 60, "#fff", GREEN_STR, sw=1),
    txt(card_x + 30, Y + 42,
        "#1  Dacia Lodgy  --  Score: 88.0%", sz=15, color=GREEN_STR, w=card_w - 60),
    txt(card_x + 30, Y + 65,
        "Justification IA : \"Recommandée car elle respecte votre budget strict de 140k DH, offre l'espace\npour 5 personnes, et est très appréciée par les profils pragmatiques comme vous.\"",
        sz=12, color=SUB, w=card_w - 60, lh=1.3)
)

print(f"Elements generated: {len(ALL)}")

with open(SRC, "r", encoding="utf-8") as f:
    data = json.load(f)

# Filter old persona elements
clean = []
for e in data["elements"]:
    x = e.get("x", 0)
    y = e.get("y", 0)
    # Old persona elements are typically at x > 1500 and y >= 1060
    if x > 1500 and y >= 1060:
        continue
    clean.append(e)

data["elements"] = clean
data["elements"].extend(ALL)

with open(SRC, "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print("Detailed engines + STT persona example successfully injected.")
