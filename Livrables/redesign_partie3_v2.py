#!/usr/bin/env python3
"""
Redesign Partie 3 v2
====================
- Replaces all emojis with illustrated badge shapes (colored mini-rectangles + icons via shapes)
- Detailed formulas with step-by-step math
- Cleaner visual hierarchy
"""

import json, shutil, uuid, time, sys

SRC = r"d:\Projet automobile\vente-auto-platform\Livrables\wakala_architecture_complete_explique.excalidraw"
BAK = SRC + ".bak_v2"

# ── Helpers ──────────────────────────────────────────────────────────────
_idx = [0]
def uid():  return uuid.uuid4().hex[:20]
def ts():   return int(time.time() * 1000)
def nidx():
    _idx[0] += 1
    return f"p3v2_{_idx[0]:04d}"

ALL = []

# ── Color palette (richer, more professional) ────────────────────────────
# Layer colors
AMBER_BG, AMBER_STR      = "#fff3bf", "#e67700"
INDIGO_BG, INDIGO_STR     = "#dbe4ff", "#364fc7"
VIOLET_BG, VIOLET_STR     = "#f3d9fa", "#862e9c"
TEAL_BG, TEAL_STR         = "#c3fae8", "#087f5b"
SKY_BG, SKY_STR           = "#d0ebff", "#1864ab"
ROSE_BG, ROSE_STR         = "#ffe0eb", "#a61e4d"
ORANGE_BG, ORANGE_STR     = "#fff4e6", "#d9480f"
GRAY_BG, GRAY_STR         = "#f1f3f5", "#adb5bd"
DARK = "#1e1e1e"
SUB  = "#495057"
MUTED = "#868e96"

# Formula card
FORMULA_BG, FORMULA_STR   = "#f8f0fc", "#7048e8"

# ── Shape factories ──────────────────────────────────────────────────────
def rect(x, y, w, h, bg, stroke, sw=2, opacity=100, rx=3):
    return {"id": uid(), "type": "rectangle", "x": x, "y": y, "width": w, "height": h,
            "angle": 0, "strokeColor": stroke, "backgroundColor": bg,
            "fillStyle": "solid", "strokeWidth": sw, "strokeStyle": "solid",
            "roughness": 0, "opacity": opacity,
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

def diamond(x, y, w, h, bg, stroke, sw=2):
    return {"id": uid(), "type": "diamond", "x": x, "y": y, "width": w, "height": h,
            "angle": 0, "strokeColor": stroke, "backgroundColor": bg,
            "fillStyle": "solid", "strokeWidth": sw, "strokeStyle": "solid",
            "roughness": 0, "opacity": 100,
            "groupIds": [], "frameId": None, "roundness": {"type": 2},
            "seed": abs(hash(uid())) % 2**31, "version": 1, "versionNonce": abs(hash(uid())) % 2**31,
            "isDeleted": False, "boundElements": [], "updated": ts(),
            "link": None, "locked": False}

def ellipse(x, y, w, h, bg, stroke, sw=2):
    return {"id": uid(), "type": "ellipse", "x": x, "y": y, "width": w, "height": h,
            "angle": 0, "strokeColor": stroke, "backgroundColor": bg,
            "fillStyle": "solid", "strokeWidth": sw, "strokeStyle": "solid",
            "roughness": 0, "opacity": 100,
            "groupIds": [], "frameId": None, "roundness": None,
            "seed": abs(hash(uid())) % 2**31, "version": 1, "versionNonce": abs(hash(uid())) % 2**31,
            "isDeleted": False, "boundElements": [], "updated": ts(),
            "link": None, "locked": False}

def line(x1, y1, x2, y2, color=SUB, sw=1.5, dashed=False):
    return {"id": uid(), "type": "line", "x": x1, "y": y1,
            "width": abs(x2-x1), "height": abs(y2-y1),
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
            "startArrowhead": None, "endArrowhead": None}

def add(*elems):
    ALL.extend(elems)

# ── Illustration badge: colored pill + icon letter ───────────────────────
def badge(x, y, letter, bg, stroke, size=28):
    """A small colored circle with a letter inside — replaces emojis."""
    # Box Neo4j (adjusted width to not spill out)
    elements.append(rect(2100, 463, 395, 140, bg="#e3fafc", stroke="#1098ad"))
    add(
        ellipse(x, y, size, size, bg, stroke, sw=2),
        txt(x + size*0.15, y + size*0.08, letter, sz=int(size*0.55), color=stroke, align="center", w=size*0.7),
    )
    return x + size + 8  # returns x position after the badge

# ═══════════════════════════════════════════════════════════════════════════
# LAYOUT
# ═══════════════════════════════════════════════════════════════════════════
X0 = 1580
W_FULL = 920  # total width
MID = X0 + W_FULL // 2

# ─── TITLE ───────────────────────────────────────────────────────────────
Y = -15
add(txt(X0 + 10, Y, "PARTIE 3", sz=28, color=DARK, w=200))
add(txt(X0 + 210, Y + 5, "Moteur de Recommandation Hybride  (Stockage & Formules)", sz=18, color=MUTED, w=700))

# ─── BANNER ──────────────────────────────────────────────────────────────
Y += 48
add(
    rect(X0, Y, W_FULL, 48, ORANGE_BG, ORANGE_STR, sw=1.5),
    txt(X0 + 18, Y + 6,
        "Le moteur croise le profil de l'acheteur avec le catalogue pour suggerer la voiture parfaite,\nmeme celle a laquelle on n'avait pas pense. Il agit comme un entremetteur automobile.",
        sz=13, color="#c92a2a", w=880, lh=1.35),
)

# ═══════════════════════════════════════════════════════════════════════════
# LAYER 1 — STOCKAGE  (3 DB boxes in a row)
# ═══════════════════════════════════════════════════════════════════════════
Y += 75
add(txt(X0 + 5, Y - 18, "COUCHE STOCKAGE", sz=11, color=MUTED, w=160))
add(rect(X0 - 5, Y - 22, W_FULL + 50, 115, "#fafafa", "#dee2e6", sw=1))

BW = 270   # box width
BH = 80    # box height
BG = 30    # gap

# -- PostgreSQL --
bx = X0 + 15
add(rect(bx, Y, BW, BH, AMBER_BG, AMBER_STR))
# illustration: small cylinder shape (two ellipses + rect)
cx = bx + 14; cy = Y + 14
add(
    rect(cx, cy + 6, 22, 28, AMBER_STR, AMBER_STR, sw=0),     # body
    ellipse(cx, cy, 22, 14, AMBER_BG, AMBER_STR, sw=1.5),     # top lid
    ellipse(cx, cy + 22, 22, 14, AMBER_BG, AMBER_STR, sw=1.5),# bottom lid
)
add(
    txt(bx + 48, Y + 12, "PostgreSQL", sz=16, color=DARK, w=200),
    txt(bx + 48, Y + 36, "Annonces nettoyees,\nprofils utilisateurs bruts", sz=11, color=SUB, w=210, lh=1.3),
)

# -- Qdrant --
bx2 = bx + BW + BG
add(rect(bx2, Y, BW, BH, AMBER_BG, AMBER_STR))
# illustration: vector grid (3 small parallel lines)
vx = bx2 + 14; vy = Y + 18
add(
    line(vx, vy, vx + 20, vy - 10, AMBER_STR, 2),
    line(vx, vy + 8, vx + 20, vy - 2, AMBER_STR, 2),
    line(vx, vy + 16, vx + 20, vy + 6, AMBER_STR, 2),
    ellipse(vx + 18, vy - 14, 8, 8, AMBER_STR, AMBER_STR, sw=0),
    ellipse(vx + 18, vy - 6, 8, 8, AMBER_STR, AMBER_STR, sw=0),
    ellipse(vx + 18, vy + 2, 8, 8, AMBER_STR, AMBER_STR, sw=0),
)
add(
    txt(bx2 + 48, Y + 12, "Qdrant  (Vectoriel)", sz=16, color=DARK, w=210),
    txt(bx2 + 48, Y + 36, "Embeddings des annonces,\nrecherche par similarite", sz=11, color=SUB, w=210, lh=1.3),
)

# -- Neo4j --
bx3 = bx2 + BW + BG
add(rect(bx3, Y, BW, BH, AMBER_BG, AMBER_STR))
# illustration: mini graph (3 nodes + 2 edges)
gx = bx3 + 14; gy = Y + 22
add(
    ellipse(gx, gy, 12, 12, AMBER_STR, AMBER_STR, sw=0),
    ellipse(gx + 18, gy - 12, 12, 12, AMBER_STR, AMBER_STR, sw=0),
    ellipse(gx + 18, gy + 12, 12, 12, AMBER_STR, AMBER_STR, sw=0),
    line(gx + 10, gy + 4, gx + 20, gy - 6, AMBER_STR, 1.5),
    line(gx + 10, gy + 8, gx + 20, gy + 16, AMBER_STR, 1.5),
)
add(
    txt(bx3 + 48, Y + 12, "Neo4j  (Graphe)", sz=16, color=DARK, w=210),
    txt(bx3 + 48, Y + 36, "Interactions utilisateurs,\nBuyer Personas & relations", sz=11, color=SUB, w=210, lh=1.3),
)

# -- ETL small tag --
ex = bx3 + BW + 20
add(
    rect(ex, Y + 15, 100, 45, "#e9ecef", MUTED, sw=1),
    txt(ex + 10, Y + 22, "ETL Pipeline", sz=12, color=SUB, w=80),
    txt(ex + 10, Y + 40, "Airflow, Scripts", sz=10, color=MUTED, w=80),
    arrow(ex, Y + 37, bx3 + BW, Y + 37, MUTED, 1.5, dashed=True),
)

# ═══════════════════════════════════════════════════════════════════════════
# LAYER 2 — ENTREE UTILISATEUR + CHATBOT
# ═══════════════════════════════════════════════════════════════════════════
Y += BH + 55
add(txt(X0 + 5, Y - 18, "ENTREE & COMPREHENSION", sz=11, color=MUTED, w=220))
add(rect(X0 - 5, Y - 22, W_FULL + 10, 110, "#fafafa", "#dee2e6", sw=1))

UW = 380; UH = 72

# -- User box --
ux = X0 + 20
add(rect(ux, Y, UW, UH, SKY_BG, SKY_STR))
# illustration: person silhouette (circle head + trapezoid body)
px = ux + 16; py = Y + 12
add(
    ellipse(px + 4, py, 16, 16, SKY_STR, SKY_STR, sw=0),       # head
    rect(px, py + 18, 24, 20, SKY_STR, SKY_STR, sw=0),         # body
    ellipse(px + 2, py + 32, 20, 8, SKY_STR, SKY_STR, sw=0),   # base
)
add(
    txt(ux + 52, Y + 10, "Utilisateur", sz=18, color=SKY_STR, w=300),
    txt(ux + 52, Y + 36, "Requete en langage naturel :\n\"Je cherche un SUV familial, budget 140k DH...\"", sz=12, color=SUB, w=320, lh=1.3),
)

# Arrow user -> chatbot
cx = ux + UW + 80
add(
    arrow(ux + UW, Y + UH // 2, cx, Y + UH // 2, SKY_STR, 2),
    txt(ux + UW + 20, Y + UH // 2 - 20, "NLP", sz=13, color=INDIGO_STR, w=35),
)

# -- Chatbot box --
add(rect(cx, Y, UW, UH, ROSE_BG, ROSE_STR))
# illustration: chat bubble (rect + small triangle)
cbx = cx + 14; cby = Y + 14
add(
    rect(cbx, cby, 26, 18, ROSE_STR, ROSE_STR, sw=0),
    # small triangle below chat bubble (simulated with a diamond)
    diamond(cbx + 4, cby + 16, 10, 10, ROSE_STR, ROSE_STR, sw=0),
    # dots inside bubble
    ellipse(cbx + 5, cby + 5, 4, 4, ROSE_BG, ROSE_BG, sw=0),
    ellipse(cbx + 11, cby + 5, 4, 4, ROSE_BG, ROSE_BG, sw=0),
    ellipse(cbx + 17, cby + 5, 4, 4, ROSE_BG, ROSE_BG, sw=0),
)
add(
    txt(cx + 52, Y + 10, "Chatbot  (LLM local)", sz=18, color=ROSE_STR, w=310),
    txt(cx + 52, Y + 36, "Extraction d'intentions, entites,\nprofil acheteur structure", sz=12, color=SUB, w=310, lh=1.3),
)

# Arrow chatbot -> orchestrateur
ocy = Y + UH + 40
mid_c = cx + UW // 2
add(
    arrow(mid_c, Y + UH, mid_c, ocy, ROSE_STR, 2),
    txt(mid_c + 8, Y + UH + 6, "Intentions extraites", sz=11, color=ROSE_STR, w=130),
)

# ═══════════════════════════════════════════════════════════════════════════
# LAYER 3 — ORCHESTRATEUR HYBRIDE
# ═══════════════════════════════════════════════════════════════════════════
Y_ORCH = ocy
add(txt(X0 + 5, Y_ORCH - 18, "ORCHESTRATION", sz=11, color=MUTED, w=150))
add(rect(X0 - 5, Y_ORCH - 22, W_FULL + 10, 95, "#fafafa", "#dee2e6", sw=1))

OW = 600; OH = 58
ox = X0 + (W_FULL - OW) // 2
add(rect(ox, Y_ORCH, OW, OH, INDIGO_BG, INDIGO_STR, sw=2))
# illustration: brain / gear (interlocking circles)
brx = ox + 16; bry = Y_ORCH + 12
add(
    ellipse(brx, bry, 18, 18, INDIGO_STR, INDIGO_STR, sw=0),
    ellipse(brx + 10, bry - 6, 14, 14, INDIGO_BG, INDIGO_STR, sw=1.5),
    ellipse(brx + 14, bry + 8, 14, 14, INDIGO_BG, INDIGO_STR, sw=1.5),
)
add(
    txt(ox + 52, Y_ORCH + 8, "Orchestrateur Hybride", sz=19, color=INDIGO_STR, w=520),
    txt(ox + 52, Y_ORCH + 34, "Construit les contextes de recherche et distribue aux deux moteurs de scoring", sz=12, color=SUB, w=520),
)

# Arrows ORCH -> two algo boxes
Y_ALGO = Y_ORCH + OH + 50
LW = 410; LH = 140
left_x = X0 + 10
right_x = X0 + W_FULL - LW - 10

add(
    arrow(ox + OW * 0.3, Y_ORCH + OH, left_x + LW // 2, Y_ALGO, VIOLET_STR, 2),
    txt(ox + OW * 0.12, Y_ORCH + OH + 5, "Requete vectorielle", sz=11, color=VIOLET_STR, w=130),
    arrow(ox + OW * 0.7, Y_ORCH + OH, right_x + LW // 2, Y_ALGO, VIOLET_STR, 2),
    txt(ox + OW * 0.7, Y_ORCH + OH + 5, "Requete graphe (ID)", sz=11, color=VIOLET_STR, w=130),
)

# Dashed arrows from DB layer to algo
qd_mid_x = bx2 + BW // 2
nj_mid_x = bx3 + BW // 2
# We need the Y of the storage layer bottom
y_storage_bottom = (Y - UH - 55) + BH + 55 - 55 + BH  # approximate
# Simpler: direct dashed lines from Qdrant/Neo4j area to algo boxes
add(
    arrow(qd_mid_x, Y - 55 + BH + 55 - 55 - 55 + BH + 55 + 10, left_x + LW // 2, Y_ALGO, AMBER_STR, 1, dashed=True),
    arrow(nj_mid_x, Y - 55 + BH + 55 - 55 - 55 + BH + 55 + 10, right_x + LW // 2, Y_ALGO, AMBER_STR, 1, dashed=True),
)

# ═══════════════════════════════════════════════════════════════════════════
# LAYER 4 — ALGORITHMES DE SCORING  (the two big boxes with FORMULAS)
# ═══════════════════════════════════════════════════════════════════════════
add(txt(X0 + 5, Y_ALGO - 18, "ALGORITHMES DE SCORING", sz=11, color=MUTED, w=220))
add(rect(X0 - 5, Y_ALGO - 22, W_FULL + 10, LH + 40, "#fafafa", "#dee2e6", sw=1))

# ── LEFT: Filtrage par Contenu ───────────────────────────────────────────
add(rect(left_x, Y_ALGO, LW, LH, VIOLET_BG, VIOLET_STR, sw=2))
# illustration: ruler/measuring (two converging lines)
rx = left_x + 14; ry = Y_ALGO + 14
add(
    line(rx, ry, rx + 24, ry + 8, VIOLET_STR, 2.5),
    line(rx, ry + 16, rx + 24, ry + 8, VIOLET_STR, 2.5),
    ellipse(rx + 21, ry + 4, 10, 10, VIOLET_BG, VIOLET_STR, sw=2),
)
add(
    txt(left_x + 50, Y_ALGO + 10, "Filtrage par Contenu", sz=17, color=VIOLET_STR, w=340),
    txt(left_x + 20, Y_ALGO + 38,
        "Similarite cosinus dans l'espace vectoriel de Qdrant.\nCompare le vecteur utilisateur au vecteur annonce.",
        sz=12, color=SUB, w=370, lh=1.35),
)
# FORMULA
add(
    rect(left_x + 15, Y_ALGO + 80, LW - 30, 46, "#f3f0ff", VIOLET_STR, sw=1.5),
    txt(left_x + 25, Y_ALGO + 86,
        "             A . B\nsim(A, B) = --------\n            ||A|| x ||B||",
        sz=14, color=VIOLET_STR, w=LW - 50, lh=1.15, align="left"),
)

# ── RIGHT: Filtrage Collaboratif ─────────────────────────────────────────
add(rect(right_x, Y_ALGO, LW, LH, VIOLET_BG, VIOLET_STR, sw=2))
# illustration: network graph (3 connected nodes)
nx_ = right_x + 14; ny_ = Y_ALGO + 16
add(
    ellipse(nx_, ny_ + 6, 10, 10, VIOLET_STR, VIOLET_STR, sw=0),
    ellipse(nx_ + 18, ny_ - 4, 10, 10, VIOLET_STR, VIOLET_STR, sw=0),
    ellipse(nx_ + 18, ny_ + 16, 10, 10, VIOLET_STR, VIOLET_STR, sw=0),
    line(nx_ + 8, ny_ + 10, nx_ + 20, ny_, VIOLET_STR, 1.5),
    line(nx_ + 8, ny_ + 14, nx_ + 20, ny_ + 20, VIOLET_STR, 1.5),
    line(nx_ + 24, ny_ + 4, nx_ + 24, ny_ + 18, VIOLET_STR, 1.5),
)
add(
    txt(right_x + 50, Y_ALGO + 10, "Filtrage Collaboratif", sz=17, color=VIOLET_STR, w=340),
    txt(right_x + 20, Y_ALGO + 38,
        "Traversee du graphe Neo4j. Les annonces liees\naux utilisateurs du meme persona sont ponderees.",
        sz=12, color=SUB, w=370, lh=1.35),
)
# FORMULA
add(
    rect(right_x + 15, Y_ALGO + 80, LW - 30, 46, "#f3f0ff", VIOLET_STR, sw=1.5),
    txt(right_x + 25, Y_ALGO + 86,
        "Score_collab = SUM( w_interaction x r_recence )\n  ou  w : Sauvegarde > Clic > Vue",
        sz=14, color=VIOLET_STR, w=LW - 50, lh=1.15, align="left"),
)

# Arrows: content score, collab score
Y_FUSION = Y_ALGO + LH + 50
add(
    arrow(left_x + LW // 2, Y_ALGO + LH, MID - 50, Y_FUSION, VIOLET_STR, 2),
    txt(left_x + LW // 2 - 45, Y_ALGO + LH + 5, "Score Contenu", sz=11, color=VIOLET_STR, w=100),
    arrow(right_x + LW // 2, Y_ALGO + LH, MID + 50, Y_FUSION, VIOLET_STR, 2),
    txt(right_x + LW // 2 - 50, Y_ALGO + LH + 5, "Score Collaboratif", sz=11, color=VIOLET_STR, w=120),
)

# ═══════════════════════════════════════════════════════════════════════════
# LAYER 5 — FUSION PONDEREE  (big formula box)
# ═══════════════════════════════════════════════════════════════════════════
FW = 700; FH = 155
fx = X0 + (W_FULL - FW) // 2

add(txt(X0 + 5, Y_FUSION - 18, "FUSION & SCORING FINAL", sz=11, color=MUTED, w=220))
add(rect(X0 - 5, Y_FUSION - 22, W_FULL + 10, FH + 40, "#fafafa", "#dee2e6", sw=1))

add(rect(fx, Y_FUSION, FW, FH, "#e6fcf5", TEAL_STR, sw=2))

# illustration: balance scale
sx = fx + 16; sy = Y_FUSION + 12
add(
    line(sx + 10, sy, sx + 10, sy + 22, TEAL_STR, 2.5),          # stem
    line(sx, sy, sx + 20, sy, TEAL_STR, 2.5),                     # beam
    line(sx, sy, sx - 4, sy + 12, TEAL_STR, 1.5),                 # left string
    line(sx + 20, sy, sx + 24, sy + 12, TEAL_STR, 1.5),           # right string
    rect(sx - 8, sy + 12, 10, 6, TEAL_STR, TEAL_STR, sw=0),      # left pan
    rect(sx + 20, sy + 12, 10, 6, TEAL_STR, TEAL_STR, sw=0),     # right pan
    rect(sx + 4, sy + 22, 12, 4, TEAL_STR, TEAL_STR, sw=0),      # base
)

add(txt(fx + 52, Y_FUSION + 10, "Fusion Ponderee  --  Formule de Scoring Hybride", sz=18, color=TEAL_STR, w=620))

# Main formula
add(
    rect(fx + 20, Y_FUSION + 40, FW - 40, 50, FORMULA_BG, FORMULA_STR, sw=2),
    txt(fx + 40, Y_FUSION + 48,
        "Score_final  =  W1  x  sim(V_user, V_annonce)  +  W2  x  Score_graphe(persona)",
        sz=16, color=FORMULA_STR, w=FW - 80, align="left"),
    txt(fx + 40, Y_FUSION + 70,
        "ou  W1 + W2 = 1   et   W1, W2 sont ajustes dynamiquement selon l'historique disponible",
        sz=12, color=MUTED, w=FW - 80, align="left"),
)

# Dynamic weights explanation
add(
    txt(fx + 20, Y_FUSION + 100,
        "Lancement (cold start) :   W1 = 0.95,  W2 = 0.05      (le graphe est quasi vide)\n"
        "Apres 1000 interactions :  W1 = 0.60,  W2 = 0.40      (intelligence collective active)\n"
        "Regime etabli :            W1 = 0.50,  W2 = 0.50      (equilibre optimal)",
        sz=13, color=SUB, w=FW - 40, lh=1.35, align="left"),
)

# ═══════════════════════════════════════════════════════════════════════════
# LAYER 6 — OUTPUT : TOP 3
# ═══════════════════════════════════════════════════════════════════════════
Y_OUT = Y_FUSION + FH + 50
OUW = 550; OUH = 75
oux = X0 + (W_FULL - OUW) // 2

add(
    arrow(fx + FW // 2, Y_FUSION + FH, oux + OUW // 2, Y_OUT, TEAL_STR, 2),
    txt(fx + FW // 2 + 8, Y_FUSION + FH + 5, "Tri final (top N)", sz=11, color=TEAL_STR, w=120),
)

add(txt(X0 + 5, Y_OUT - 18, "RESULTAT", sz=11, color=MUTED, w=100))
add(rect(X0 - 5, Y_OUT - 22, W_FULL + 10, OUH + 60, "#fafafa", "#dee2e6", sw=1))

add(rect(oux, Y_OUT, OUW, OUH, TEAL_BG, TEAL_STR, sw=2))
# illustration: trophy (simple cup shape)
tx = oux + 16; ty = Y_OUT + 12
add(
    rect(tx + 4, ty, 16, 22, TEAL_STR, TEAL_STR, sw=0),       # cup body
    rect(tx + 6, ty + 22, 12, 4, TEAL_STR, TEAL_STR, sw=0),   # stem
    rect(tx + 2, ty + 26, 20, 5, TEAL_STR, TEAL_STR, sw=0),   # base
    ellipse(tx - 2, ty + 4, 10, 12, "transparent", TEAL_STR, sw=2),  # left handle
    ellipse(tx + 16, ty + 4, 10, 12, "transparent", TEAL_STR, sw=2), # right handle
)
add(
    txt(oux + 52, Y_OUT + 10, "Top 3 Annonces Recommandees", sz=18, color=TEAL_STR, w=470),
    txt(oux + 52, Y_OUT + 38, "Enrichies avec justifications IA :  \"Pourquoi cette voiture vous correspond\"", sz=13, color=SUB, w=470),
)

# Feedback loop
fb_x = oux + OUW + 30
add(
    arrow(oux + OUW, Y_OUT + OUH // 2, fb_x + 60, Y_ORCH + OH // 2, "#c92a2a", 1.5, dashed=True),
    txt(fb_x - 5, Y_OUT - 8, "Boucle Feedback\nExplicabilite\n(Pourquoi ?)", sz=11, color="#c92a2a", w=110, lh=1.3),
)

# ═══════════════════════════════════════════════════════════════════════════
# DETAIL SECTION — Full mathematical breakdown
# ═══════════════════════════════════════════════════════════════════════════
Y_DET = Y_OUT + OUH + 65
DW = 420; DH = 180

add(txt(X0 + 5, Y_DET - 18, "DETAIL DES FORMULES", sz=11, color=MUTED, w=200))

# ── Detail 1: Content-based full derivation ──────────────────────────────
d1x = X0 + 10
add(rect(d1x, Y_DET, DW, DH, "#f8f0ff", "#9775fa", sw=1.5))
# mini ruler illustration
add(
    line(d1x + 14, Y_DET + 14, d1x + 34, Y_DET + 22, "#9775fa", 2),
    line(d1x + 14, Y_DET + 30, d1x + 34, Y_DET + 22, "#9775fa", 2),
    ellipse(d1x + 30, Y_DET + 18, 10, 10, "#f3d9fa", "#9775fa", sw=1.5),
)
add(
    txt(d1x + 50, Y_DET + 12, "Detail : Filtrage par Contenu", sz=15, color=VIOLET_STR, w=350),
    txt(d1x + 15, Y_DET + 42,
        "1. V_user  = [budget, usage, priorites, passagers]\n"
        "2. V_annonce = [prix, type, conso, places, fiabilite]\n"
        "3. Les deux vecteurs vivent dans l'espace\n"
        "   d'embeddings de Qdrant (dim = 768).\n"
        "4. sim = cos(angle) entre V_user et V_annonce.\n"
        "   Plus l'angle est petit, plus le match est fort.\n\n"
        "Avantage : predictible, explicable, zero historique\n"
        "requis (fonctionne des le premier utilisateur).",
        sz=12, color=SUB, w=390, lh=1.25, align="left"),
)

# ── Detail 2: Collaborative full derivation ──────────────────────────────
d2x = d1x + DW + 40
add(rect(d2x, Y_DET, DW, DH, "#f8f0ff", "#9775fa", sw=1.5))
# mini graph illustration
add(
    ellipse(d2x + 14, Y_DET + 18, 10, 10, "#9775fa", "#9775fa", sw=0),
    ellipse(d2x + 30, Y_DET + 10, 10, 10, "#9775fa", "#9775fa", sw=0),
    ellipse(d2x + 30, Y_DET + 26, 10, 10, "#9775fa", "#9775fa", sw=0),
    line(d2x + 22, Y_DET + 22, d2x + 32, Y_DET + 16, "#9775fa", 1.5),
    line(d2x + 22, Y_DET + 26, d2x + 32, Y_DET + 30, "#9775fa", 1.5),
)
add(
    txt(d2x + 50, Y_DET + 12, "Detail : Filtrage Collaboratif", sz=15, color=VIOLET_STR, w=350),
    txt(d2x + 15, Y_DET + 42,
        "1. Identifier le Persona de l'utilisateur\n"
        "   (ex: 'Famille_Pragmatique', 'Jeune_Sportif').\n"
        "2. Traverser le graphe Neo4j :\n"
        "   (User) -[:MEME_PERSONA]-> (Karim)\n"
        "   (Karim) -[:A_SAUVEGARDE]-> (Dacia Lodgy)\n"
        "3. Ponderer par type d'interaction :\n"
        "   Sauvegarde (x3) > Clic (x2) > Vue (x1)\n"
        "4. Ponderer par recence (decay exponentiel).\n\n"
        "Avantage : capte les signaux implicites sociaux.",
        sz=12, color=SUB, w=390, lh=1.25, align="left"),
)

# ── Detail 3: Cold Start + Weight dynamics ───────────────────────────────
Y_COLD = Y_DET + DH + 25
CW = 2 * DW + 40; CH = 120
add(rect(d1x, Y_COLD, CW, CH, ORANGE_BG, ORANGE_STR, sw=1.5))
# warning triangle illustration
wx = d1x + 14; wy = Y_COLD + 14
add(
    diamond(wx, wy, 24, 24, ORANGE_STR, ORANGE_STR, sw=0),
    txt(wx + 7, wy + 2, "!", sz=16, color="#fff", w=10, align="center"),
)
add(
    txt(d1x + 50, Y_COLD + 12, "Probleme du Cold Start & Poids Dynamiques", sz=15, color=ORANGE_STR, w=CW - 60),
    txt(d1x + 15, Y_COLD + 42,
        "Au lancement, le graphe Neo4j est vide : aucune interaction a exploiter.\n"
        "Le systeme demarre en mode 'contenu seul' (W1 = 95%, W2 = 5%).\n\n"
        "A mesure que les utilisateurs interagissent (clics, sauvegardes, achats),\n"
        "le poids W2 augmente progressivement. L'intelligence collective s'active.\n"
        "Formule d'ajustement :  W2 = min(0.5, log(1 + N_interactions) / K)",
        sz=12, color=SUB, w=CW - 30, lh=1.3, align="left"),
)


# ═══════════════════════════════════════════════════════════════════════════
# APPLY CHANGES
# ═══════════════════════════════════════════════════════════════════════════
shutil.copy2(SRC, BAK)
with open(SRC, "r", encoding="utf-8") as f:
    data = json.load(f)

# Identify ALL old P3 elements to remove (both v1 originals and v1 redesign)
old_ids = set()
for e in data["elements"]:
    eid = e.get("id", "")
    idx = e.get("index", "")
    # Old originals
    if "_p3" in eid or eid == "title_partie_3" or eid == "text_expl_moteur":
        old_ids.add(eid)
    if eid.startswith("227a6203"):
        old_ids.add(eid)
    # v1 redesign elements (index starts with p3_)
    if idx.startswith("p3_"):
        old_ids.add(eid)

# Mark as deleted
for e in data["elements"]:
    if e.get("id") in old_ids:
        e["isDeleted"] = True

# Add new v2 elements
data["elements"].extend(ALL)

with open(SRC, "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

sys.stdout.reconfigure(encoding="utf-8")
print(f"Removed {len(old_ids)} old elements")
print(f"Added {len(ALL)} new elements")
print("Partie 3 v2 redesign complete!")
print(f"Backup: {BAK}")
