#!/usr/bin/env python3
"""
Add a persona example section to Partie 3
==========================================
Adds a concrete walkthrough using Karim 'Le Pragmatique'
showing how each step of the engine processes his request.
"""

import json, uuid, time, sys

SRC = r"d:\Projet automobile\vente-auto-platform\Livrables\wakala_architecture_complete_explique.excalidraw"

_idx = [0]
def uid():  return uuid.uuid4().hex[:20]
def ts():   return int(time.time() * 1000)
def nidx():
    _idx[0] += 1
    return f"p3ex_{_idx[0]:04d}"

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

# Shape factories (same as v2)
def rect(x, y, w, h, bg, stroke, sw=2, rx=3):
    return {"id": uid(), "type": "rectangle", "x": x, "y": y, "width": w, "height": h,
            "angle": 0, "strokeColor": stroke, "backgroundColor": bg,
            "fillStyle": "solid", "strokeWidth": sw, "strokeStyle": "solid",
            "roughness": 0, "opacity": 100,
            "groupIds": [], "frameId": None, "roundness": {"type": rx},
            "seed": abs(hash(uid())) % 2**31, "version": 1, "versionNonce": abs(hash(uid())) % 2**31,
            "isDeleted": False, "boundElements": [], "updated": ts(),
            "link": None, "locked": False}

def txt(x, y, text, sz=14, color=SUB, align="left", w=None, lh=1.25, vAlign="middle"):
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
            "fontSize": sz, "fontFamily": 1,
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

def line(x1, y1, x2, y2, color=SUB, sw=1.5):
    return {"id": uid(), "type": "line", "x": x1, "y": y1,
            "width": abs(x2-x1), "height": abs(y2-y1),
            "angle": 0, "strokeColor": color, "backgroundColor": "transparent",
            "fillStyle": "solid", "strokeWidth": sw, "strokeStyle": "solid",
            "roughness": 0, "opacity": 100,
            "groupIds": [], "frameId": None, "roundness": {"type": 2},
            "seed": abs(hash(uid())) % 2**31, "version": 1, "versionNonce": abs(hash(uid())) % 2**31,
            "isDeleted": False, "boundElements": [], "updated": ts(),
            "link": None, "locked": False,
            "points": [[0, 0], [x2-x1, y2-y1]],
            "lastCommittedPoint": None,
            "startBinding": None, "endBinding": None,
            "startArrowhead": None, "endArrowhead": None}

def add(*elems):
    ALL.extend(elems)

# ═══════════════════════════════════════════════════════════════════════════
# LAYOUT
# ═══════════════════════════════════════════════════════════════════════════
X0 = 1580
W_FULL = 920
Y_START = 1430  # below the cold start box

# ─── SECTION TITLE ───────────────────────────────────────────────────────
add(txt(X0 + 5, Y_START, "EXEMPLE CONCRET  --  Persona : Karim, \"Le Pragmatique\"", sz=13, color=MUTED, w=500))

# Large outer container
CONTAINER_H = 820
add(rect(X0 - 5, Y_START - 5, W_FULL + 10, CONTAINER_H, "#f8f9fa", "#ced4da", sw=1.5))

# ═══════════════════════════════════════════════════════════════════════════
# STEP 1 — The user speaks
# ═══════════════════════════════════════════════════════════════════════════
Y = Y_START + 30
STEP_W = 880
step_x = X0 + 15

# Step number badge
add(
    ellipse(step_x, Y + 3, 28, 28, SKY_STR, SKY_STR, sw=0),
    txt(step_x + 6, Y + 6, "1", sz=16, color="#fff", w=16, align="center"),
)

# User card
card_x = step_x + 42
card_w = STEP_W - 50
add(rect(card_x, Y, card_w, 85, SKY_BG, SKY_STR, sw=1.5))

# Person illustration inside card
px = card_x + 18; py = Y + 12
add(
    ellipse(px + 3, py, 14, 14, SKY_STR, SKY_STR, sw=0),       # head
    rect(px, py + 16, 20, 16, SKY_STR, SKY_STR, sw=0),          # body
    ellipse(px + 2, py + 28, 16, 7, SKY_STR, SKY_STR, sw=0),    # base
)

add(
    txt(card_x + 52, Y + 8, "Karim, 35 ans  --  Persona : \"Le Pragmatique\"", sz=16, color=SKY_STR, w=card_w - 70),
    txt(card_x + 52, Y + 32,
        "Requete :\n\"Je cherche une voiture robuste pour ma famille de 5 personnes,\n budget maximum 140 000 DH. Je fais beaucoup d'autoroute.\"",
        sz=13, color=SUB, w=card_w - 70, lh=1.3),
)

# Arrow down
Y_NEXT = Y + 85 + 20
mid = card_x + card_w // 2
add(arrow(mid, Y + 85, mid, Y_NEXT, MUTED, 1.5))

# ═══════════════════════════════════════════════════════════════════════════
# STEP 2 — NLP extraction
# ═══════════════════════════════════════════════════════════════════════════
Y = Y_NEXT

add(
    ellipse(step_x, Y + 3, 28, 28, ROSE_STR, ROSE_STR, sw=0),
    txt(step_x + 6, Y + 6, "2", sz=16, color="#fff", w=16, align="center"),
)

add(rect(card_x, Y, card_w, 110, ROSE_BG, ROSE_STR, sw=1.5))

# Chat bubble illustration
cbx = card_x + 16; cby = Y + 14
add(
    rect(cbx, cby, 22, 16, ROSE_STR, ROSE_STR, sw=0),
    ellipse(cbx + 4, cby + 4, 4, 4, ROSE_BG, ROSE_BG, sw=0),
    ellipse(cbx + 9, cby + 4, 4, 4, ROSE_BG, ROSE_BG, sw=0),
    ellipse(cbx + 14, cby + 4, 4, 4, ROSE_BG, ROSE_BG, sw=0),
)

add(
    txt(card_x + 52, Y + 8, "Chatbot (LLM) -- Extraction NLP", sz=16, color=ROSE_STR, w=card_w - 70),
)

# Extracted structured data
struct_x = card_x + 52
struct_y = Y + 34
add(
    txt(struct_x, struct_y,
        "Le LLM analyse la phrase et produit :", sz=12, color=SUB, w=400),
    # JSON-like output box
    rect(struct_x, struct_y + 18, 380, 52, "#fff", ROSE_STR, sw=1),
    txt(struct_x + 10, struct_y + 22,
        '{ "usage": "familiale",  "places_min": 5,\n'
        '  "budget_max": 140000,  "critere": "robustesse",\n'
        '  "trajet": "autoroute" }',
        sz=12, color=ROSE_STR, w=360, lh=1.2),
)

# Right side: persona identification
pid_x = card_x + 480
add(
    rect(pid_x, struct_y + 10, 180, 60, "#fff", INDIGO_STR, sw=1.5),
    txt(pid_x + 10, struct_y + 15, "Persona identifie :", sz=11, color=MUTED, w=160),
    txt(pid_x + 10, struct_y + 32, "Famille_Pragmatique", sz=15, color=INDIGO_STR, w=160),
    txt(pid_x + 10, struct_y + 52, "ID_Persona = FP-024", sz=11, color=MUTED, w=160),
)

# Arrow pointing to persona box
add(arrow(struct_x + 380, struct_y + 44, pid_x, struct_y + 44, INDIGO_STR, 1.5))

# Arrow down
Y_NEXT = Y + 110 + 20
add(arrow(mid, Y + 110, mid, Y_NEXT, MUTED, 1.5))

# ═══════════════════════════════════════════════════════════════════════════
# STEP 3 — Dual scoring (side by side)
# ═══════════════════════════════════════════════════════════════════════════
Y = Y_NEXT

add(
    ellipse(step_x, Y + 3, 28, 28, VIOLET_STR, VIOLET_STR, sw=0),
    txt(step_x + 6, Y + 6, "3", sz=16, color="#fff", w=16, align="center"),
)

# TWO SIDE-BY-SIDE CARDS
half_w = (card_w - 20) // 2

# ── LEFT: Qdrant content scoring ──
lx = card_x
add(rect(lx, Y, half_w, 200, VIOLET_BG, VIOLET_STR, sw=1.5))

# Converging lines illustration
add(
    line(lx + 14, Y + 14, lx + 34, Y + 22, VIOLET_STR, 2),
    line(lx + 14, Y + 30, lx + 34, Y + 22, VIOLET_STR, 2),
    ellipse(lx + 30, Y + 18, 10, 10, "#f3d9fa", VIOLET_STR, sw=1.5),
)

add(
    txt(lx + 52, Y + 8, "Qdrant  (Contenu)", sz=15, color=VIOLET_STR, w=half_w - 70),
    txt(lx + 15, Y + 35,
        "V_karim  = [140k, familiale, robuste, autoroute]\n"
        "V_lodgy  = [120k, 7 places, fiable, polyvalent]\n"
        "V_kangoo = [95k, 5 places, utilitaire, ville]",
        sz=12, color=SUB, w=half_w - 30, lh=1.3),
)

# Mini formula + results
add(
    rect(lx + 10, Y + 105, half_w - 20, 82, "#f8f0fc", VIOLET_STR, sw=1),
    txt(lx + 18, Y + 110,
        "sim(Karim, Lodgy) :", sz=12, color=MUTED, w=200),
    txt(lx + 18, Y + 126,
        "= cos(angle) = 0.94    (94%)", sz=14, color=VIOLET_STR, w=300),
    txt(lx + 18, Y + 148,
        "sim(Karim, Kangoo) :", sz=12, color=MUTED, w=200),
    txt(lx + 18, Y + 164,
        "= cos(angle) = 0.71    (71%)", sz=14, color=VIOLET_STR, w=300),
)

# ── RIGHT: Neo4j collaborative scoring ──
rx_ = card_x + half_w + 20
add(rect(rx_, Y, half_w, 200, VIOLET_BG, VIOLET_STR, sw=1.5))

# Graph illustration
gx = rx_ + 14; gy = Y + 16
add(
    ellipse(gx, gy + 6, 10, 10, VIOLET_STR, VIOLET_STR, sw=0),
    ellipse(gx + 18, gy - 4, 10, 10, VIOLET_STR, VIOLET_STR, sw=0),
    ellipse(gx + 18, gy + 16, 10, 10, VIOLET_STR, VIOLET_STR, sw=0),
    line(gx + 8, gy + 10, gx + 20, gy, VIOLET_STR, 1.5),
    line(gx + 8, gy + 14, gx + 20, gy + 20, VIOLET_STR, 1.5),
)

add(
    txt(rx_ + 52, Y + 8, "Neo4j  (Collaboratif)", sz=15, color=VIOLET_STR, w=half_w - 70),
    txt(rx_ + 15, Y + 42,
        "Traversee du graphe :\n"
        "(Karim) -[:MEME_PERSONA]-> (Youssef)\n"
        "(Youssef) -[:A_SAUVEGARDE]-> (Dacia Lodgy)\n"
        "(Karim) -[:MEME_PERSONA]-> (Amina)\n"
        "(Amina) -[:A_CLIQUE]-> (Renault Kangoo)",
        sz=12, color=SUB, w=half_w - 30, lh=1.3),
)

# Results
add(
    rect(rx_ + 10, Y + 125, half_w - 20, 62, "#f8f0fc", VIOLET_STR, sw=1),
    txt(rx_ + 18, Y + 130,
        "Score_collab(Lodgy) :", sz=12, color=MUTED, w=200),
    txt(rx_ + 18, Y + 146,
        "= 3 (sauvegarde) x 0.95 (recent) = 2.85", sz=14, color=VIOLET_STR, w=350),
    txt(rx_ + 18, Y + 166,
        "Score_collab(Kangoo)  = 2 x 0.80 = 1.60", sz=13, color=VIOLET_STR, w=350),
)

# Arrow down
Y_NEXT = Y + 200 + 20
add(arrow(mid, Y + 200, mid, Y_NEXT, MUTED, 1.5))

# ═══════════════════════════════════════════════════════════════════════════
# STEP 4 — Fusion (final scoring)
# ═══════════════════════════════════════════════════════════════════════════
Y = Y_NEXT

add(
    ellipse(step_x, Y + 3, 28, 28, TEAL_STR, TEAL_STR, sw=0),
    txt(step_x + 6, Y + 6, "4", sz=16, color="#fff", w=16, align="center"),
)

add(rect(card_x, Y, card_w, 150, GREEN_BG, TEAL_STR, sw=1.5))

# Scale illustration
sx = card_x + 16; sy = Y + 14
add(
    line(sx + 10, sy, sx + 10, sy + 20, TEAL_STR, 2.5),
    line(sx, sy, sx + 20, sy, TEAL_STR, 2.5),
    line(sx, sy, sx - 3, sy + 10, TEAL_STR, 1.5),
    line(sx + 20, sy, sx + 23, sy + 10, TEAL_STR, 1.5),
    rect(sx - 6, sy + 10, 8, 5, TEAL_STR, TEAL_STR, sw=0),
    rect(sx + 19, sy + 10, 8, 5, TEAL_STR, TEAL_STR, sw=0),
    rect(sx + 4, sy + 20, 12, 4, TEAL_STR, TEAL_STR, sw=0),
)

add(txt(card_x + 52, Y + 8, "Fusion Ponderee  --  Calcul du Score Final", sz=16, color=TEAL_STR, w=card_w - 70))

# Formula with actual numbers
add(
    txt(card_x + 20, Y + 36,
        "Poids actuels (500 interactions) :  W1 = 0.65,  W2 = 0.35",
        sz=13, color=MUTED, w=card_w - 40),
)

# Lodgy calculation
add(
    rect(card_x + 20, Y + 58, card_w - 40, 36, "#fff", TEAL_STR, sw=1.5),
    txt(card_x + 30, Y + 62,
        "Dacia Lodgy :    Score = 0.65 x 0.94  +  0.35 x 2.85/3  =  0.611 + 0.332  =  0.943",
        sz=14, color=TEAL_STR, w=card_w - 60),
    txt(card_x + card_w - 110, Y + 78, "RANG #1", sz=12, color=TEAL_STR, w=80, align="right"),
)

# Kangoo calculation
add(
    rect(card_x + 20, Y + 100, card_w - 40, 36, "#fff", MUTED, sw=1),
    txt(card_x + 30, Y + 104,
        "Renault Kangoo : Score = 0.65 x 0.71  +  0.35 x 1.60/3  =  0.462 + 0.187  =  0.649",
        sz=14, color=SUB, w=card_w - 60),
    txt(card_x + card_w - 110, Y + 120, "RANG #2", sz=12, color=MUTED, w=80, align="right"),
)

# Arrow down
Y_NEXT = Y + 150 + 20
add(arrow(mid, Y + 150, mid, Y_NEXT, MUTED, 1.5))

# ═══════════════════════════════════════════════════════════════════════════
# STEP 5 — Result shown to user
# ═══════════════════════════════════════════════════════════════════════════
Y = Y_NEXT

add(
    ellipse(step_x, Y + 3, 28, 28, "#2b8a3e", "#2b8a3e", sw=0),
    txt(step_x + 6, Y + 6, "5", sz=16, color="#fff", w=16, align="center"),
)

add(rect(card_x, Y, card_w, 145, TEAL_BG, "#2b8a3e", sw=2))

# Trophy illustration
tx = card_x + 16; ty = Y + 14
add(
    rect(tx + 4, ty, 14, 18, "#2b8a3e", "#2b8a3e", sw=0),
    rect(tx + 6, ty + 18, 10, 4, "#2b8a3e", "#2b8a3e", sw=0),
    rect(tx + 2, ty + 22, 18, 4, "#2b8a3e", "#2b8a3e", sw=0),
    ellipse(tx - 2, ty + 3, 8, 10, "transparent", "#2b8a3e", sw=1.5),
    ellipse(tx + 14, ty + 3, 8, 10, "transparent", "#2b8a3e", sw=1.5),
)

add(txt(card_x + 52, Y + 8, "Resultat affiche a Karim", sz=16, color="#2b8a3e", w=card_w - 70))

# Result card #1
r1x = card_x + 30; r1y = Y + 38
add(
    rect(r1x, r1y, card_w - 60, 34, "#fff", "#2b8a3e", sw=1.5),
    txt(r1x + 10, r1y + 4, "#1  Dacia Lodgy  --  Score: 94.3%", sz=15, color="#2b8a3e", w=card_w - 100),
    txt(r1x + 10, r1y + 22,
        "\"Recommandee car 7 places, budget respecte, et les familles similaires l'adorent.\"",
        sz=11, color=SUB, w=card_w - 100),
)

# Result card #2
r2y = r1y + 40
add(
    rect(r1x, r2y, card_w - 60, 34, "#fff", MUTED, sw=1),
    txt(r1x + 10, r2y + 4, "#2  Renault Kangoo  --  Score: 64.9%", sz=14, color=SUB, w=card_w - 100),
    txt(r1x + 10, r2y + 22,
        "\"Alternative plus economique, 5 places, ideal ville mais moins adapte autoroute.\"",
        sz=11, color=MUTED, w=card_w - 100),
)

# Surprise badge
add(
    rect(card_x + card_w - 230, Y + 120, 210, 18, AMBER_BG, AMBER_STR, sw=1),
    txt(card_x + card_w - 225, Y + 120, "Karim n'avait pas pense au Lodgy !", sz=11, color=AMBER_STR, w=200),
)


# ═══════════════════════════════════════════════════════════════════════════
# APPLY
# ═══════════════════════════════════════════════════════════════════════════
with open(SRC, "r", encoding="utf-8") as f:
    data = json.load(f)

data["elements"].extend(ALL)

with open(SRC, "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

sys.stdout.reconfigure(encoding="utf-8")
print(f"Added {len(ALL)} elements for the persona example")
print("Persona example added to Partie 3!")
