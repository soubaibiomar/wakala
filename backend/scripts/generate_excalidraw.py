import json
import uuid
import random
import os

def create_element(
    el_type: str,
    x: float,
    y: float,
    width: float,
    height: float,
    text: str = "",
    stroke_color: str = "#3b82f6",
    bg_color: str = "#1e293b",
    font_size: int = 15,
    text_align: str = "center",
    roundness_type: int = 3,
):
    el_id = str(uuid.uuid4())[:8]
    seed = random.randint(10000, 99999)
    
    if el_type == "rectangle":
        return {
            "id": el_id,
            "type": "rectangle",
            "x": x,
            "y": y,
            "width": width,
            "height": height,
            "angle": 0,
            "strokeColor": stroke_color,
            "backgroundColor": bg_color,
            "fillStyle": "solid",
            "strokeWidth": 2,
            "strokeStyle": "solid",
            "roughness": 0,
            "opacity": 100,
            "groupIds": [],
            "frameId": None,
            "roundness": {"type": roundness_type},
            "seed": seed,
            "version": 1,
            "versionNonce": seed + 1,
            "isDeleted": False,
            "boundElements": [],
            "updated": 1,
            "link": None,
            "locked": False
        }
    elif el_type == "text":
        lines = text.split("\n")
        line_height = font_size * 1.35
        calc_height = len(lines) * line_height
        return {
            "id": el_id,
            "type": "text",
            "x": x,
            "y": y,
            "width": width,
            "height": calc_height,
            "angle": 0,
            "strokeColor": stroke_color,
            "backgroundColor": "transparent",
            "fillStyle": "solid",
            "strokeWidth": 1,
            "strokeStyle": "solid",
            "roughness": 0,
            "opacity": 100,
            "groupIds": [],
            "frameId": None,
            "roundness": None,
            "seed": seed,
            "version": 1,
            "versionNonce": seed + 1,
            "isDeleted": False,
            "boundElements": None,
            "updated": 1,
            "link": None,
            "locked": False,
            "text": text,
            "fontSize": font_size,
            "fontFamily": 1,
            "textAlign": text_align,
            "verticalAlign": "middle",
            "containerId": None,
            "originalText": text,
            "lineHeight": 1.3
        }
    elif el_type == "arrow":
        return {
            "id": el_id,
            "type": "arrow",
            "x": x,
            "y": y,
            "width": width,
            "height": height,
            "angle": 0,
            "strokeColor": stroke_color,
            "backgroundColor": "transparent",
            "fillStyle": "solid",
            "strokeWidth": 2,
            "strokeStyle": "solid",
            "roughness": 0,
            "opacity": 100,
            "groupIds": [],
            "frameId": None,
            "roundness": {"type": 2},
            "seed": seed,
            "version": 1,
            "versionNonce": seed + 1,
            "isDeleted": False,
            "boundElements": None,
            "updated": 1,
            "link": None,
            "locked": False,
            "points": [[0, 0], [width, height]],
            "lastCommittedPoint": None,
            "startBinding": None,
            "endBinding": None,
            "startArrowhead": None,
            "endArrowhead": "arrow"
        }

def make_card(elements, x, y, w, h, title, subtitle="", stroke="#3b82f6", bg="#111827", title_color="#ffffff", font_size=14, align="center"):
    rect = create_element("rectangle", x, y, w, h, stroke_color=stroke, bg_color=bg)
    elements.append(rect)
    
    full_text = title if not subtitle else f"{title}\n{subtitle}"
    lines_count = len(full_text.split("\n"))
    txt_y = y + (h - (lines_count * (font_size * 1.35))) / 2
    txt = create_element("text", x + 12, txt_y, w - 24, h, text=full_text, stroke_color=title_color, font_size=font_size, text_align=align)
    elements.append(txt)
    return rect

def make_header(elements, x, y, w, title, subtitle="", stroke="#60a5fa"):
    hdr_box = create_element("rectangle", x, y, w, 65, stroke_color=stroke, bg_color="#0f172a")
    elements.append(hdr_box)
    full_text = f"{title}" if not subtitle else f"{title}\n{subtitle}"
    txt = create_element("text", x + 15, y + 14, w - 30, 40, text=full_text, stroke_color="#ffffff", font_size=16)
    elements.append(txt)

def generate_nlp_excalidraw():
    elements = []
    
    # Title Banner
    make_header(elements, 80, 40, 1180, "WAKALA — PIPELINE NLP MULTILINGUE (FR / AR / DARIJA / ARABIZI)", "Conformite CNDP (Loi 09-08) & Normalisation Argot Financier Marocain", stroke="#3b82f6")
    
    # Col 1: INGRESS
    c1_x = 80
    make_card(elements, c1_x, 130, 260, 45, "1. ENTREE MULTICANALE", "", stroke="#3b82f6", bg="#1e293b", title_color="#60a5fa", font_size=15)
    make_card(elements, c1_x, 195, 260, 75, "💬 Chatbot / Recherche", "Texte libre (FR, Darija, AR)", stroke="#3b82f6", bg="#111827")
    make_card(elements, c1_x, 290, 260, 75, "🎙️ Message Vocal WebRTC", "Capture audio utilisateur", stroke="#3b82f6", bg="#111827")
    make_card(elements, c1_x, 385, 260, 75, "⚡ Whisper ASR", "Transcription vocale en texte", stroke="#3b82f6", bg="#111827")
    
    elements.append(create_element("arrow", c1_x + 130, 365, 0, 20, stroke_color="#60a5fa"))
    elements.append(create_element("arrow", c1_x + 260, 420, 50, -150, stroke_color="#60a5fa"))
    elements.append(create_element("arrow", c1_x + 260, 230, 50, 40, stroke_color="#60a5fa"))

    # Col 2: CNDP ZERO-PII
    c2_x = 380
    make_card(elements, c2_x, 130, 260, 45, "2. SECURITE CNDP (09-08)", "", stroke="#ef4444", bg="#450a0a", title_color="#f87171", font_size=15)
    make_card(elements, c2_x, 195, 260, 60, "🛡️ Regex Sanitizer", "Masquage pre-LLM temps reel", stroke="#ef4444", bg="#18181b")
    make_card(elements, c2_x, 270, 260, 50, "🆔 CIN Marocaine", "[CIN_REDACTED]", stroke="#ef4444", bg="#18181b", title_color="#fca5a5")
    make_card(elements, c2_x, 335, 260, 50, "📱 Telephones +212/06/07", "[PHONE_REDACTED]", stroke="#ef4444", bg="#18181b", title_color="#fca5a5")
    make_card(elements, c2_x, 400, 260, 50, "✉️ Emails & Coordonnees", "[EMAIL_REDACTED]", stroke="#ef4444", bg="#18181b", title_color="#fca5a5")
    make_card(elements, c2_x, 470, 260, 60, "✅ Texte Anonymise", "Zero fuite de donnees privees", stroke="#10b981", bg="#064e3b", title_color="#34d399")

    elements.append(create_element("arrow", c2_x + 130, 255, 0, 15, stroke_color="#ef4444"))
    elements.append(create_element("arrow", c2_x + 130, 450, 0, 20, stroke_color="#10b981"))
    elements.append(create_element("arrow", c2_x + 260, 500, 50, -220, stroke_color="#10b981"))

    # Col 3: MOROCCAN NLP ENGINE
    c3_x = 680
    make_card(elements, c3_x, 130, 280, 45, "3. NORMALISATION DARIJA", "", stroke="#8b5cf6", bg="#2e1065", title_color="#c4b5fd", font_size=15)
    make_card(elements, c3_x, 195, 280, 65, "🌐 Detecteur Code-Switching", "Darija, Arabizi, Arabe, FR", stroke="#8b5cf6", bg="#111827")
    make_card(elements, c3_x, 275, 280, 85, "💰 Argot Financier Marocain", "'25 melyoun' -> 250 000 MAD\n'180k / alf' -> 180 000 MAD\n'500 alf ryal' -> 25 000 MAD", stroke="#f59e0b", bg="#111827", title_color="#fbbf24")
    make_card(elements, c3_x, 375, 280, 85, "🚗 Dictionnaire Automobile", "'mazot / gasoil' -> DIESEL\n'lisans / essence' -> ESSENCE\n'bva / auto' -> AUTOMATIQUE\n'4x4 / baroudeur' -> SUV", stroke="#8b5cf6", bg="#111827", title_color="#a78bfa")
    make_card(elements, c3_x, 475, 280, 55, "📋 Extraction Intent & Slots", "{budget, fuel, body, brand}", stroke="#8b5cf6", bg="#1e1b4b", title_color="#c4b5fd")

    elements.append(create_element("arrow", c3_x + 140, 260, 0, 15, stroke_color="#8b5cf6"))
    elements.append(create_element("arrow", c3_x + 140, 360, 0, 15, stroke_color="#8b5cf6"))
    elements.append(create_element("arrow", c3_x + 140, 460, 0, 15, stroke_color="#8b5cf6"))
    elements.append(create_element("arrow", c3_x + 280, 500, 50, -240, stroke_color="#8b5cf6"))
    elements.append(create_element("arrow", c3_x + 280, 500, 50, -100, stroke_color="#8b5cf6"))

    # Col 4: OUTPUT ENGINES
    c4_x = 1000
    make_card(elements, c4_x, 130, 260, 45, "4. DOUBLE DISPATCH", "", stroke="#10b981", bg="#064e3b", title_color="#6ee7b7", font_size=15)
    make_card(elements, c4_x, 210, 260, 105, "🗄️ Requetes SQL Dures", "PostgreSQL 4-Tier Catalog\n• Marques & Modeles\n• Finitions & Equipements\n• Tarifs Cle en main DGI", stroke="#3b82f6", bg="#111827", title_color="#93c5fd")
    make_card(elements, c4_x, 345, 260, 105, "🧠 RAG & IA Generative", "Qdrant Vector Store + LLM\n• Recommandations hybrides\n• Explications Darija / FR\n• Argumentaire concession", stroke="#8b5cf6", bg="#111827", title_color="#c4b5fd")
    make_card(elements, c4_x, 480, 260, 50, "✨ Showroom Digital & Lead", "Essai CNDP + Devis Proforma", stroke="#10b981", bg="#064e3b", title_color="#34d399")

    elements.append(create_element("arrow", c4_x + 130, 315, 0, 30, stroke_color="#3b82f6"))
    elements.append(create_element("arrow", c4_x + 130, 450, 0, 30, stroke_color="#10b981"))

    return {
        "type": "excalidraw",
        "version": 2,
        "source": "https://excalidraw.com",
        "elements": elements,
        "appState": {
            "gridSize": None,
            "viewBackgroundColor": "#0b0f19"
        },
        "files": {}
    }

def generate_hybrid_scoring_excalidraw():
    elements = []
    
    # Title Banner
    make_header(elements, 80, 40, 1200, "WAKALA — MOTEUR DE SCORING HYBRIDE & RECOMMANDATION", "Ponderation Multi-Criteres & Integration Fiscale Marocaine Live", stroke="#8b5cf6")
    
    # Col 1: INPUTS
    c1_x = 80
    make_card(elements, c1_x, 130, 260, 45, "1. ENTREES UTILISATEUR", "", stroke="#3b82f6", bg="#1e293b", title_color="#60a5fa", font_size=15)
    make_card(elements, c1_x, 195, 260, 65, "🎯 Criteres Explicites", "Carburant, Boite, Carrosserie", stroke="#3b82f6", bg="#111827")
    make_card(elements, c1_x, 275, 260, 75, "🎛️ Priority Tubes (0-100)", "Curseurs Economie, Puissance,\nHabitabilite, Equipements", stroke="#8b5cf6", bg="#111827", title_color="#c4b5fd")
    make_card(elements, c1_x, 365, 260, 65, "💵 Budget Maximal MAD", "Budget plafond acheteur", stroke="#10b981", bg="#111827", title_color="#34d399")
    make_card(elements, c1_x, 445, 260, 75, "📑 Fiches Constructeur", "Base 4-Tier certifiee Maroc", stroke="#64748b", bg="#111827")

    elements.append(create_element("arrow", c1_x + 260, 395, 50, -145, stroke_color="#10b981"))
    elements.append(create_element("arrow", c1_x + 260, 480, 50, -180, stroke_color="#64748b"))

    # Col 2: REAL-TIME MOROCCAN TAX ENGINE
    c2_x = 380
    make_card(elements, c2_x, 130, 260, 45, "2. FISCALITE MAROCAINE", "", stroke="#10b981", bg="#064e3b", title_color="#6ee7b7", font_size=15)
    make_card(elements, c2_x, 195, 260, 80, "🧾 Prix Cle en Main (OTR)", "Prix TTC + Vignette + Carte Grise\n+ Taxe de Luxe + Concession", stroke="#10b981", bg="#111827", title_color="#34d399")
    make_card(elements, c2_x, 290, 260, 70, "🏷️ Vignette DGI (CGI 262)", "Diesel: 700-20k DH | Ess: 350-8k\nHybride / EV: 0 DH (Exonere)", stroke="#10b981", bg="#111827", title_color="#6ee7b7")
    make_card(elements, c2_x, 375, 260, 65, "💳 Carte Grise & Immat", "350-400 DH / CV fiscal + timbres", stroke="#10b981", bg="#111827")
    make_card(elements, c2_x, 455, 260, 65, "💎 Taxe de Luxe (0-20%)", "Tranches progressives Loi Finances", stroke="#f59e0b", bg="#111827", title_color="#fbbf24")

    elements.append(create_element("arrow", c2_x + 260, 235, 50, -20, stroke_color="#10b981"))
    elements.append(create_element("arrow", c1_x + 260, 225, 370, 70, stroke_color="#3b82f6"))
    elements.append(create_element("arrow", c1_x + 260, 310, 370, 70, stroke_color="#8b5cf6"))
    elements.append(create_element("arrow", c1_x + 260, 480, 370, -20, stroke_color="#64748b"))

    # Col 3: 4 SPECIALIZED SCORING PILLARS
    c3_x = 680
    make_card(elements, c3_x, 130, 280, 45, "3. PILIERS DE SCORING", "", stroke="#f59e0b", bg="#451a03", title_color="#fbbf24", font_size=15)
    make_card(elements, c3_x, 195, 280, 70, "📈 S_budget (0 - 100)", "Adequation au prix cle en main\nBonus si < 90% budget, penalite si >", stroke="#10b981", bg="#111827", title_color="#34d399")
    make_card(elements, c3_x, 280, 280, 70, "⚙️ S_specs (0 - 100)", "Concordance exacte moteur, boite,\ncarrosserie et carburant", stroke="#3b82f6", bg="#111827", title_color="#93c5fd")
    make_card(elements, c3_x, 365, 280, 90, "📊 S_radar Benchmark (0 - 100)", "• Economie (L/100km & Vignette)\n• Puissance (ch & couple Nm)\n• Habitabilite (Coffre L) & Serie", stroke="#8b5cf6", bg="#111827", title_color="#c4b5fd")
    make_card(elements, c3_x, 470, 280, 65, "🛡️ S_trust (0 - 100)", "Garantie constructeur (annees/km)\n+ Certification Concessionnaire", stroke="#6366f1", bg="#111827", title_color="#a5b4fc")

    elements.append(create_element("arrow", c3_x + 280, 230, 50, 110, stroke_color="#10b981"))
    elements.append(create_element("arrow", c3_x + 280, 315, 50, 35, stroke_color="#3b82f6"))
    elements.append(create_element("arrow", c3_x + 280, 410, 50, -40, stroke_color="#8b5cf6"))
    elements.append(create_element("arrow", c3_x + 280, 500, 50, -115, stroke_color="#6366f1"))

    # Col 4: WEIGHTED AGGREGATION & OUTPUT
    c4_x = 1000
    make_card(elements, c4_x, 130, 260, 45, "4. AGREGATION & TOP RANG", "", stroke="#ec4899", bg="#500724", title_color="#f472b6", font_size=15)
    make_card(elements, c4_x, 260, 260, 135, "🧮 Formule d'Agregation", "S_total = w_b · S_budget\n       + w_s · S_specs\n       + w_r · S_radar\n       + w_t · S_trust\n(Normalisation continue)", stroke="#ec4899", bg="#1e1b4b", title_color="#ffffff")
    make_card(elements, c4_x, 420, 260, 55, "🏆 Showroom Recommande", "Top finitions classees", stroke="#10b981", bg="#064e3b", title_color="#34d399")
    make_card(elements, c4_x, 490, 260, 55, "⚖️ Matrice Face-a-Face", "Comparateur avec diffs", stroke="#3b82f6", bg="#1e293b", title_color="#60a5fa")

    elements.append(create_element("arrow", c4_x + 130, 395, 0, 25, stroke_color="#ec4899"))
    elements.append(create_element("arrow", c4_x + 130, 475, 0, 15, stroke_color="#10b981"))

    return {
        "type": "excalidraw",
        "version": 2,
        "source": "https://excalidraw.com",
        "elements": elements,
        "appState": {
            "gridSize": None,
            "viewBackgroundColor": "#0b0f19"
        },
        "files": {}
    }

def generate_all_in_one_excalidraw():
    nlp = generate_nlp_excalidraw()
    scoring = generate_hybrid_scoring_excalidraw()
    
    all_elements = []
    all_elements.extend(nlp["elements"])
    
    for el in scoring["elements"]:
        shifted = dict(el)
        shifted["y"] = el["y"] + 580
        if el.get("points"):
            shifted["points"] = el["points"]
        all_elements.append(shifted)
        
    return {
        "type": "excalidraw",
        "version": 2,
        "source": "https://excalidraw.com",
        "elements": all_elements,
        "appState": {
            "gridSize": None,
            "viewBackgroundColor": "#0b0f19"
        },
        "files": {}
    }

if __name__ == "__main__":
    out_dir = r"d:\Projet automobile\vente-auto-platform\docs\diagrams"
    os.makedirs(out_dir, exist_ok=True)
    
    nlp_data = generate_nlp_excalidraw()
    nlp_path = os.path.join(out_dir, "nlp_pipeline_multilingual.excalidraw")
    with open(nlp_path, "w", encoding="utf-8") as f:
        json.dump(nlp_data, f, indent=2, ensure_ascii=False)
    print(f"Generated: {nlp_path}")
    
    scoring_data = generate_hybrid_scoring_excalidraw()
    scoring_path = os.path.join(out_dir, "hybrid_scoring_engine.excalidraw")
    with open(scoring_path, "w", encoding="utf-8") as f:
        json.dump(scoring_data, f, indent=2, ensure_ascii=False)
    print(f"Generated: {scoring_path}")

    all_data = generate_all_in_one_excalidraw()
    all_path = os.path.join(out_dir, "wakala_architecture_all_in_one.excalidraw")
    with open(all_path, "w", encoding="utf-8") as f:
        json.dump(all_data, f, indent=2, ensure_ascii=False)
    print(f"Generated: {all_path}")
