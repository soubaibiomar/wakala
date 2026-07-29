#!/usr/bin/env python3
"""
Redesign Partie 3 — Moteur de Recommandation Hybride
=====================================================
Better visual hierarchy, clearer flow, richer colors, grouped layers.
"""

import json
import shutil
import uuid
import time

SRC = r"d:\Projet automobile\vente-auto-platform\Livrables\wakala_architecture_complete_explique.excalidraw"
BAK = SRC + ".bak"

# ── Helpers ──────────────────────────────────────────────────────────────
def uid():
    return uuid.uuid4().hex[:20]

def ts():
    return int(time.time() * 1000)

# ── Color palette ────────────────────────────────────────────────────────
# Storage layer (warm amber)
C_STORAGE_BG   = "#fff3bf"
C_STORAGE_STR  = "#e67700"

# Processing / IA layer (deep indigo)
C_IA_BG        = "#dbe4ff"
C_IA_STR       = "#364fc7"

# Algo boxes (violet gradient)
C_ALGO_BG      = "#e5dbff"
C_ALGO_STR     = "#7048e8"

# Result / output (teal)
C_OUT_BG       = "#c3fae8"
C_OUT_STR      = "#099268"

# User / input (sky blue)
C_USER_BG      = "#d0ebff"
C_USER_STR     = "#1971c2"

# Chatbot (rose)
C_CHAT_BG      = "#fff0f6"
C_CHAT_STR     = "#c2255c"

# Group frame
C_FRAME_BG     = "#f8f9fa"
C_FRAME_STR    = "#adb5bd"

# Text colors
C_TITLE        = "#1e1e1e"
C_SUB          = "#495057"
C_LABEL        = "#868e96"

# ── Layout constants ─────────────────────────────────────────────────────
X0    = 1600          # left edge of partie 3
COL_W = 320           # standard box width
GAP_X = 40            # horizontal gap between boxes
GAP_Y = 30            # vertical gap between rows
MID_X = X0 + 370      # center column x

# ── Build new elements ───────────────────────────────────────────────────
new_elements = []
idx_counter = [0]

def next_idx():
    idx_counter[0] += 1
    return f"p3_{idx_counter[0]:03d}"

def make_rect(x, y, w, h, bg, stroke, rx=8, sw=2, idx=None):
    return {
        "id": uid(), "type": "rectangle",
        "x": x, "y": y, "width": w, "height": h,
        "angle": 0, "strokeColor": stroke, "backgroundColor": bg,
        "fillStyle": "solid", "strokeWidth": sw, "strokeStyle": "solid",
        "roughness": 0, "opacity": 100,
        "groupIds": [], "frameId": None,
        "roundness": {"type": 3},
        "seed": abs(hash(uid())) % 2**31, "version": 1, "versionNonce": abs(hash(uid())) % 2**31,
        "isDeleted": False, "boundElements": [], "updated": ts(),
        "link": None, "locked": False,
        "index": idx or next_idx()
    }

def make_text(x, y, text, size=14, color=C_SUB, align="center", bold=False, w=None, idx=None, lh=1.25):
    return {
        "id": uid(), "type": "text",
        "x": x, "y": y,
        "width": w or len(text) * size * 0.6,
        "height": size * lh * text.count("\n") + size * lh if "\n" in text else size * lh,
        "angle": 0, "strokeColor": color, "backgroundColor": "transparent",
        "fillStyle": "solid", "strokeWidth": 1, "strokeStyle": "solid",
        "roughness": 0, "opacity": 100,
        "groupIds": [], "frameId": None, "roundness": None,
        "seed": abs(hash(uid())) % 2**31, "version": 1, "versionNonce": abs(hash(uid())) % 2**31,
        "isDeleted": False, "boundElements": [], "updated": ts(),
        "link": None, "locked": False,
        "text": text, "originalText": text,
        "fontSize": size, "fontFamily": 1,
        "textAlign": align, "verticalAlign": "middle",
        "baseline": size, "containerId": None,
        "index": idx or next_idx(),
        "autoResize": True, "lineHeight": lh
    }

def make_arrow(x1, y1, x2, y2, color=C_SUB, sw=2, dashed=False, idx=None):
    return {
        "id": uid(), "type": "arrow",
        "x": x1, "y": y1,
        "width": abs(x2 - x1), "height": abs(y2 - y1),
        "angle": 0, "strokeColor": color, "backgroundColor": "transparent",
        "fillStyle": "solid", "strokeWidth": sw,
        "strokeStyle": "dashed" if dashed else "solid",
        "roughness": 0, "opacity": 100,
        "groupIds": [], "frameId": None,
        "roundness": {"type": 2},
        "seed": abs(hash(uid())) % 2**31, "version": 1, "versionNonce": abs(hash(uid())) % 2**31,
        "isDeleted": False, "boundElements": [], "updated": ts(),
        "link": None, "locked": False,
        "points": [[0, 0], [x2 - x1, y2 - y1]],
        "lastCommittedPoint": None,
        "startBinding": None, "endBinding": None,
        "startArrowhead": None, "endArrowhead": "arrow",
        "index": idx or next_idx()
    }

def add(*elems):
    new_elements.extend(elems)

# ═══════════════════════════════════════════════════════════════════════════
# LAYER 0 — Title + description banner
# ═══════════════════════════════════════════════════════════════════════════
Y_TITLE = -10
add(
    make_text(X0 + 10, Y_TITLE, "PARTIE 3 — Moteur de Recommandation Hybride", size=24, color=C_TITLE, align="left", w=800),
)

Y_BANNER = Y_TITLE + 40
BANNER_W = 850
add(
    make_rect(X0, Y_BANNER, BANNER_W, 50, "#fff4e6", "#fd7e14", sw=1.5),
    make_text(X0 + 15, Y_BANNER + 8,
              "En simple : le moteur croise le profil de l'acheteur avec le catalogue pour\nsuggérer la voiture parfaite, même celle à laquelle on n'avait pas pensé.",
              size=13, color="#e8590c", align="left", w=820, lh=1.35),
)

# ═══════════════════════════════════════════════════════════════════════════
# LAYER 1 — Couche Stockage (top row: 3 DB boxes)
# ═══════════════════════════════════════════════════════════════════════════
Y_STORAGE = Y_BANNER + 80
BOX_H = 75
BOX_W = 240

# Section label
add(make_text(X0 + 10, Y_STORAGE - 24, "COUCHE STOCKAGE", size=12, color=C_LABEL, align="left", w=200))

# Background grouping rect
add(make_rect(X0 - 10, Y_STORAGE - 30, BANNER_W + 20, BOX_H + 45, "#f8f9fa", "#dee2e6", sw=1))

# PostgreSQL
pg_x = X0 + 10
add(
    make_rect(pg_x, Y_STORAGE, BOX_W, BOX_H, C_STORAGE_BG, C_STORAGE_STR),
    make_text(pg_x + 10, Y_STORAGE + 10, "🗄  PostgreSQL", size=16, color=C_TITLE, align="left", w=220),
    make_text(pg_x + 10, Y_STORAGE + 38, "Annonces nettoyées\nProfils utilisateurs bruts", size=12, color=C_SUB, align="left", w=220, lh=1.3),
)

# Qdrant
qd_x = pg_x + BOX_W + GAP_X
add(
    make_rect(qd_x, Y_STORAGE, BOX_W, BOX_H, C_STORAGE_BG, C_STORAGE_STR),
    make_text(qd_x + 10, Y_STORAGE + 10, "🔮  Qdrant (Vectoriel)", size=16, color=C_TITLE, align="left", w=220),
    make_text(qd_x + 10, Y_STORAGE + 38, "Embeddings des annonces\nRecherche par similarité", size=12, color=C_SUB, align="left", w=220, lh=1.3),
)

# Neo4j
nj_x = qd_x + BOX_W + GAP_X
add(
    make_rect(nj_x, Y_STORAGE, BOX_W, BOX_H, C_STORAGE_BG, C_STORAGE_STR),
    make_text(nj_x + 10, Y_STORAGE + 10, "🕸  Neo4j (Graphe)", size=16, color=C_TITLE, align="left", w=220),
    make_text(nj_x + 10, Y_STORAGE + 38, "Interactions utilisateurs\nBuyer Personas & relations", size=12, color=C_SUB, align="left", w=220, lh=1.3),
)

# ── ETL feeder arrow + small box ─────────────────────────────────────────
etl_x = nj_x + BOX_W + 50
add(
    make_rect(etl_x, Y_STORAGE + 10, 160, 55, "#e9ecef", "#868e96"),
    make_text(etl_x + 10, Y_STORAGE + 18, "⚙  ETL Pipeline", size=14, color=C_TITLE, align="left", w=140),
    make_text(etl_x + 10, Y_STORAGE + 40, "Airflow + Scripts", size=11, color=C_LABEL, align="left", w=140),
    make_arrow(etl_x, Y_STORAGE + 37, nj_x + BOX_W, Y_STORAGE + 37, color="#868e96", sw=1.5, dashed=True),
)

# ═══════════════════════════════════════════════════════════════════════════
# LAYER 2 — Entrée Utilisateur + Chatbot (processing)
# ═══════════════════════════════════════════════════════════════════════════
Y_INPUT = Y_STORAGE + BOX_H + GAP_Y + 30

# Section label
add(make_text(X0 + 10, Y_INPUT - 24, "ENTRÉE & COMPRÉHENSION", size=12, color=C_LABEL, align="left", w=250))

# Background
add(make_rect(X0 - 10, Y_INPUT - 30, BANNER_W + 20, 175, "#f1f3f5", "#dee2e6", sw=1))

# User input box
user_w = 360
user_h = 65
user_x = X0 + 30
add(
    make_rect(user_x, Y_INPUT, user_w, user_h, C_USER_BG, C_USER_STR),
    make_text(user_x + 15, Y_INPUT + 10, "👤  Utilisateur", size=17, color=C_USER_STR, align="left", w=330),
    make_text(user_x + 15, Y_INPUT + 38, "Requête en langage naturel  →  \"Je cherche un SUV familial...\"", size=12, color=C_SUB, align="left", w=330),
)

# Arrow user → chatbot
chat_x = user_x + user_w + 60
add(make_arrow(user_x + user_w, Y_INPUT + user_h // 2, chat_x, Y_INPUT + user_h // 2, color=C_USER_STR, sw=2))

# Label on arrow
add(make_text(user_x + user_w + 8, Y_INPUT + user_h // 2 - 18, "NLP", size=11, color=C_IA_STR, align="center", w=40))

# Chatbot box
chat_w = 360
chat_h = 65
add(
    make_rect(chat_x, Y_INPUT, chat_w, chat_h, C_CHAT_BG, C_CHAT_STR),
    make_text(chat_x + 15, Y_INPUT + 10, "🤖  Chatbot (LLM local)", size=17, color=C_CHAT_STR, align="left", w=330),
    make_text(chat_x + 15, Y_INPUT + 38, "Extraction d'intentions, entités & profil acheteur", size=12, color=C_SUB, align="left", w=330),
)

# Arrow chatbot → orchestrateur (vertical, down)
orch_y = Y_INPUT + chat_h + GAP_Y + 15
mid_chat = chat_x + chat_w // 2
add(make_arrow(mid_chat, Y_INPUT + chat_h, mid_chat, orch_y, color=C_CHAT_STR, sw=2))
add(make_text(mid_chat + 8, Y_INPUT + chat_h + 5, "Intentions", size=11, color=C_CHAT_STR, align="left", w=80))

# ═══════════════════════════════════════════════════════════════════════════
# LAYER 3 — Orchestrateur Hybride (center)
# ═══════════════════════════════════════════════════════════════════════════
Y_ORCH = orch_y
orch_w = 550
orch_h = 60
orch_x = X0 + (BANNER_W - orch_w) // 2

# Section label
add(make_text(X0 + 10, Y_ORCH - 24, "ORCHESTRATION HYBRIDE", size=12, color=C_LABEL, align="left", w=250))

# Background
add(make_rect(X0 - 10, Y_ORCH - 30, BANNER_W + 20, orch_h + 50, "#f1f3f5", "#dee2e6", sw=1))

add(
    make_rect(orch_x, Y_ORCH, orch_w, orch_h, C_IA_BG, C_IA_STR, sw=2),
    make_text(orch_x + 20, Y_ORCH + 10, "🧠  Orchestrateur Hybride", size=18, color=C_IA_STR, align="left", w=510),
    make_text(orch_x + 20, Y_ORCH + 38, "Construit les contextes de recherche  →  distribue aux deux moteurs", size=12, color=C_SUB, align="left", w=510),
)

# ── Arrows from Orchestrateur DOWN to two algo boxes ─────────────────────
Y_ALGO = Y_ORCH + orch_h + GAP_Y + 25
algo_w = 380
algo_h = 110

left_algo_x  = X0 + 10
right_algo_x = X0 + BANNER_W - algo_w + 10

# Left arrow (to content)
add(make_arrow(orch_x + orch_w * 0.3, Y_ORCH + orch_h, left_algo_x + algo_w // 2, Y_ALGO, color=C_ALGO_STR, sw=2))
add(make_text(orch_x + orch_w * 0.15, Y_ORCH + orch_h + 3, "Requête vectorielle", size=11, color=C_ALGO_STR, align="left", w=130))

# Right arrow (to collab)
add(make_arrow(orch_x + orch_w * 0.7, Y_ORCH + orch_h, right_algo_x + algo_w // 2, Y_ALGO, color=C_ALGO_STR, sw=2))
add(make_text(orch_x + orch_w * 0.7, Y_ORCH + orch_h + 3, "Graphe (ID utilisateur)", size=11, color=C_ALGO_STR, align="left", w=150))

# ── Arrows from DB layer DOWN to algo boxes ──────────────────────────────
# Qdrant → Content-based
add(make_arrow(qd_x + BOX_W // 2, Y_STORAGE + BOX_H, left_algo_x + algo_w // 2, Y_ALGO, color=C_STORAGE_STR, sw=1.5, dashed=True))
add(make_text(qd_x + BOX_W // 2 - 60, Y_STORAGE + BOX_H + 8, "Similarité Annonces", size=10, color=C_STORAGE_STR, align="left", w=130))

# Neo4j → Collaborative
add(make_arrow(nj_x + BOX_W // 2, Y_STORAGE + BOX_H, right_algo_x + algo_w // 2, Y_ALGO, color=C_STORAGE_STR, sw=1.5, dashed=True))
add(make_text(nj_x + BOX_W // 2 - 50, Y_STORAGE + BOX_H + 8, "Voisinage Persona", size=10, color=C_STORAGE_STR, align="left", w=120))

# ═══════════════════════════════════════════════════════════════════════════
# LAYER 4 — Les 2 algorithmes (Content-based + Collaborative)
# ═══════════════════════════════════════════════════════════════════════════
# Section label
add(make_text(X0 + 10, Y_ALGO - 24, "ALGORITHMES DE SCORING", size=12, color=C_LABEL, align="left", w=250))

# Background
add(make_rect(X0 - 10, Y_ALGO - 30, BANNER_W + 20, algo_h + 50, "#f8f9fa", "#dee2e6", sw=1))

# Content-based filtering (left)
add(
    make_rect(left_algo_x, Y_ALGO, algo_w, algo_h, C_ALGO_BG, C_ALGO_STR, sw=2),
    make_text(left_algo_x + 15, Y_ALGO + 10, "📐  Filtrage par Contenu", size=17, color=C_ALGO_STR, align="left", w=350),
    make_text(left_algo_x + 15, Y_ALGO + 38, "Similarité cosinus dans l'espace vectoriel de Qdrant.\nCompare le vecteur utilisateur [budget, usage, priorités]\nau vecteur annonce [prix, type, caractéristiques].", size=12, color=C_SUB, align="left", w=350, lh=1.35),
    make_text(left_algo_x + 15, Y_ALGO + algo_h - 22, "sim(A,B) = (A·B) / (‖A‖·‖B‖)", size=13, color=C_ALGO_STR, align="left", w=300),
)

# Collaborative filtering (right)
add(
    make_rect(right_algo_x, Y_ALGO, algo_w, algo_h, C_ALGO_BG, C_ALGO_STR, sw=2),
    make_text(right_algo_x + 15, Y_ALGO + 10, "🕸  Filtrage Collaboratif", size=17, color=C_ALGO_STR, align="left", w=350),
    make_text(right_algo_x + 15, Y_ALGO + 38, "Traversée du graphe Neo4j : les annonces liées\naux utilisateurs du même persona sont pondérées\npar le type d'interaction et la récence.", size=12, color=C_SUB, align="left", w=350, lh=1.35),
    make_text(right_algo_x + 15, Y_ALGO + algo_h - 22, "Score = Σ (w_interaction × r_récence)", size=13, color=C_ALGO_STR, align="left", w=300),
)

# ═══════════════════════════════════════════════════════════════════════════
# LAYER 5 — Fusion pondérée (merge)
# ═══════════════════════════════════════════════════════════════════════════
Y_FUSION = Y_ALGO + algo_h + GAP_Y + 25
fusion_w = 600
fusion_h = 100
fusion_x = X0 + (BANNER_W - fusion_w) // 2

# Arrows from algo boxes down to fusion
add(make_arrow(left_algo_x + algo_w // 2, Y_ALGO + algo_h, fusion_x + fusion_w * 0.3, Y_FUSION, color=C_ALGO_STR, sw=2))
add(make_text(left_algo_x + algo_w // 2 - 50, Y_ALGO + algo_h + 3, "Score Contenu", size=11, color=C_ALGO_STR, align="left", w=100))

add(make_arrow(right_algo_x + algo_w // 2, Y_ALGO + algo_h, fusion_x + fusion_w * 0.7, Y_FUSION, color=C_ALGO_STR, sw=2))
add(make_text(right_algo_x + algo_w // 2 - 50, Y_ALGO + algo_h + 3, "Score Collaboratif", size=11, color=C_ALGO_STR, align="left", w=120))

# Section label
add(make_text(X0 + 10, Y_FUSION - 24, "FUSION & SCORING FINAL", size=12, color=C_LABEL, align="left", w=250))

# Background
add(make_rect(X0 - 10, Y_FUSION - 30, BANNER_W + 20, fusion_h + 50, "#f8f9fa", "#dee2e6", sw=1))

add(
    make_rect(fusion_x, Y_FUSION, fusion_w, fusion_h, "#d3f9d8", C_OUT_STR, sw=2),
    make_text(fusion_x + 20, Y_FUSION + 10, "⚖  Fusion Pondérée — Formule de Scoring Hybride", size=18, color=C_OUT_STR, align="left", w=560),
    make_text(fusion_x + 20, Y_FUSION + 40,
              "Score_final = W₁ × Similarité_Vecteur  +  W₂ × Score_Graphe\n\nW₁ et W₂ sont dynamiques : au lancement W₁ ≈ 100% (graphe vide).\nPlus l'historique s'enrichit, plus W₂ augmente (intelligence collective).",
              size=13, color=C_SUB, align="left", w=560, lh=1.3),
)

# ═══════════════════════════════════════════════════════════════════════════
# LAYER 6 — Top 3 output + feedback loop
# ═══════════════════════════════════════════════════════════════════════════
Y_OUTPUT = Y_FUSION + fusion_h + GAP_Y + 25
out_w = 500
out_h = 75
out_x = X0 + (BANNER_W - out_w) // 2

# Arrow fusion → output
add(make_arrow(fusion_x + fusion_w // 2, Y_FUSION + fusion_h, out_x + out_w // 2, Y_OUTPUT, color=C_OUT_STR, sw=2))
add(make_text(fusion_x + fusion_w // 2 + 8, Y_FUSION + fusion_h + 3, "Tri final", size=11, color=C_OUT_STR, align="left", w=60))

# Section label
add(make_text(X0 + 10, Y_OUTPUT - 24, "RÉSULTAT", size=12, color=C_LABEL, align="left", w=100))

# Background
add(make_rect(X0 - 10, Y_OUTPUT - 30, BANNER_W + 20, out_h + 80, "#f8f9fa", "#dee2e6", sw=1))

add(
    make_rect(out_x, Y_OUTPUT, out_w, out_h, C_OUT_BG, C_OUT_STR, sw=2),
    make_text(out_x + 20, Y_OUTPUT + 10, "🏆  Top 3 Annonces Recommandées", size=18, color=C_OUT_STR, align="left", w=460),
    make_text(out_x + 20, Y_OUTPUT + 40, "Enrichies avec justifications IA  →  \"Pourquoi cette voiture vous correspond\"", size=13, color=C_SUB, align="left", w=460),
)

# Feedback loop arrow (from output back to orchestrateur)
feedback_x = out_x + out_w + 30
add(
    make_arrow(out_x + out_w, Y_OUTPUT + out_h // 2, feedback_x + 50, Y_ORCH + orch_h // 2, color="#e03131", sw=1.5, dashed=True),
    make_text(feedback_x - 10, Y_OUTPUT - 10, "Boucle Feedback\nExplicabilité\n(\"Pourquoi ?\")", size=11, color="#e03131", align="left", w=120, lh=1.3),
)

# ═══════════════════════════════════════════════════════════════════════════
# DETAIL BOXES — Below the main flow
# ═══════════════════════════════════════════════════════════════════════════
Y_DETAIL = Y_OUTPUT + out_h + 60
det_w = 400
det_h = 100

# Section label
add(make_text(X0 + 10, Y_DETAIL - 24, "DÉTAILS TECHNIQUES", size=12, color=C_LABEL, align="left", w=200))

# Detail 1: Content-based
add(
    make_rect(X0 + 10, Y_DETAIL, det_w, det_h, "#f3f0ff", "#9775fa", sw=1),
    make_text(X0 + 25, Y_DETAIL + 8, "Détail — Filtrage par Contenu", size=14, color=C_ALGO_STR, align="left", w=370),
    make_text(X0 + 25, Y_DETAIL + 30,
              "La similarité cosinus mesure l'angle entre le\nvecteur utilisateur (budget, priorités) et celui\nde l'annonce dans l'espace de Qdrant.\n→ Avantage : prédictible et explicable.",
              size=12, color=C_SUB, align="left", w=370, lh=1.3),
)

# Detail 2: Collaborative
add(
    make_rect(X0 + det_w + 50, Y_DETAIL, det_w, det_h, "#f3f0ff", "#9775fa", sw=1),
    make_text(X0 + det_w + 65, Y_DETAIL + 8, "Détail — Filtrage Collaboratif", size=14, color=C_ALGO_STR, align="left", w=370),
    make_text(X0 + det_w + 65, Y_DETAIL + 30,
              "Basé sur la théorie des graphes. Les annonces\nliées aux utilisateurs du même persona sont\npondérées par interaction (Sauvegarde > Vue)\net la récence. Capte les signaux implicites.",
              size=12, color=C_SUB, align="left", w=370, lh=1.3),
)

# Detail 3: Cold Start
Y_COLD = Y_DETAIL + det_h + 20
cold_w = 2 * det_w + 50
add(
    make_rect(X0 + 10, Y_COLD, cold_w, 80, "#fff4e6", "#fd7e14", sw=1),
    make_text(X0 + 25, Y_COLD + 8, "⚠  Problème du Cold Start", size=14, color="#e8590c", align="left", w=cold_w - 30),
    make_text(X0 + 25, Y_COLD + 30,
              "Au lancement, W₁ (contenu) ≈ 100% car le graphe Neo4j est vide. Le système fonctionne en mode \"content-only\".\nPlus les utilisateurs interagissent, plus W₂ (collaboratif) augmente pour affiner par l'intelligence collective.",
              size=12, color=C_SUB, align="left", w=cold_w - 30, lh=1.35),
)


# ═══════════════════════════════════════════════════════════════════════════
# APPLY: Remove old P3 elements, inject new ones
# ═══════════════════════════════════════════════════════════════════════════

# Load
shutil.copy2(SRC, BAK)
with open(SRC, "r", encoding="utf-8") as f:
    data = json.load(f)

# Identify old P3 element IDs
old_p3_ids = set()
for e in data["elements"]:
    eid = e.get("id", "")
    if "_p3" in eid or eid == "title_partie_3" or eid == "text_expl_moteur":
        old_p3_ids.add(eid)
    # Also match the scoring formula text box
    if eid.startswith("227a6203"):
        old_p3_ids.add(eid)

print(f"Removing {len(old_p3_ids)} old Partie 3 elements")
print(f"Adding {len(new_elements)} new elements")

# Mark old ones as deleted
for e in data["elements"]:
    if e.get("id") in old_p3_ids:
        e["isDeleted"] = True

# Add new ones
data["elements"].extend(new_elements)

# Save
with open(SRC, "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print("✅ Partie 3 redesigned successfully!")
print(f"   Backup saved to: {BAK}")
