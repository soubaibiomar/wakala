import json
import uuid
import random

def generate_id():
    return str(uuid.uuid4())[:20]

def random_int():
    return random.randint(100000000, 2000000000)

class ExcalidrawGenerator:
    def __init__(self):
        self.elements = []
    
    def add_text(self, text, x, y, font_size=16, color="#1e1e1e", align="center", bold=False):
        el_id = generate_id()
        
        # Approximate width and height so Excalidraw doesn't clip
        lines = text.split('\n')
        max_line_len = max(len(line) for line in lines)
        width = max_line_len * font_size * 0.7
        height = len(lines) * font_size * 1.5
            
        el = {
            "id": el_id,
            "type": "text",
            "x": x,
            "y": y,
            "width": width,
            "height": height,
            "angle": 0,
            "strokeColor": color,
            "backgroundColor": "transparent",
            "fillStyle": "solid",
            "strokeWidth": 2 if bold else 1,
            "strokeStyle": "solid",
            "roughness": 1,
            "opacity": 100,
            "groupIds": [],
            "frameId": None,
            "roundness": None,
            "seed": random_int(),
            "versionNonce": random_int(),
            "isDeleted": False,
            "boundElements": [],
            "updated": 1785143082781,
            "link": None,
            "locked": False,
            "text": text,
            "fontSize": font_size,
            "fontFamily": 1,
            "textAlign": align,
            "verticalAlign": "middle",
            "baseline": font_size,
            "containerId": None,
            "originalText": text,
            "lineHeight": 1.25,
            "version": 2,
            "index": "a0",
            "autoResize": True
        }
        self.elements.append(el)
        return el

    def add_rectangle(self, x, y, width, height, stroke_color, bg_color, text_color, text_title, text_body=None):
        rect_id = generate_id()
        group_id = generate_id()
        
        rect = {
            "id": rect_id,
            "type": "rectangle",
            "x": x,
            "y": y,
            "width": width,
            "height": height,
            "angle": 0,
            "strokeColor": stroke_color,
            "backgroundColor": bg_color,
            "fillStyle": "solid",
            "strokeWidth": 1.5,
            "strokeStyle": "solid",
            "roughness": 1,
            "opacity": 100,
            "groupIds": [group_id],
            "frameId": None,
            "roundness": {"type": 3},
            "seed": random_int(),
            "versionNonce": random_int(),
            "isDeleted": False,
            "boundElements": [],
            "updated": 1785143082781,
            "link": None,
            "locked": False,
            "version": 2,
            "index": "a1"
        }
        self.elements.append(rect)
        
        # Add Title (freestanding)
        title_width = len(text_title) * 16 * 0.7
        title_x = x + (width - title_width) / 2
        
        title_el = self.add_text(text_title, title_x, y + 15, font_size=18, color=text_color, align="center", bold=True)
        title_el["groupIds"] = [group_id]
        
        # Add Body (freestanding)
        if text_body:
            lines = text_body.split('\n')
            max_line_len = max(len(line) for line in lines)
            body_width = max_line_len * 14 * 0.7
            body_x = x + (width - body_width) / 2
            
            body_el = self.add_text(text_body, body_x, y + 50, font_size=14, color=text_color, align="center")
            body_el["groupIds"] = [group_id]
            
        return rect_id

    def add_arrow(self, start_x, start_y, end_x, end_y, stroke_color="#495057", text_label=None):
        arrow_id = generate_id()
        
        arrow = {
            "id": arrow_id,
            "type": "arrow",
            "x": start_x,
            "y": start_y,
            "width": abs(end_x - start_x) or 1,
            "height": abs(end_y - start_y) or 1,
            "angle": 0,
            "strokeColor": stroke_color,
            "backgroundColor": "transparent",
            "fillStyle": "solid",
            "strokeWidth": 1.5,
            "strokeStyle": "solid",
            "roughness": 1,
            "opacity": 100,
            "groupIds": [],
            "frameId": None,
            "roundness": {"type": 2},
            "seed": random_int(),
            "versionNonce": random_int(),
            "isDeleted": False,
            "boundElements": [],
            "updated": 1785143082781,
            "link": None,
            "locked": False,
            "points": [
                [0, 0],
                [end_x - start_x, end_y - start_y]
            ],
            "lastCommittedPoint": None,
            "startBinding": None,
            "endBinding": None,
            "startArrowhead": None,
            "endArrowhead": "arrow",
            "version": 2,
            "index": "a4"
        }
        self.elements.append(arrow)
        
        if text_label:
            mid_x = (start_x + end_x) / 2
            mid_y = (start_y + end_y) / 2 - 10
            
            label_width = len(text_label) * 12 * 0.7
            label_x = mid_x - (label_width / 2)
            
            self.add_text(text_label, label_x, mid_y, font_size=12, color=stroke_color, align="center")

        return arrow_id

    def generate(self, filename):
        data = {
            "type": "excalidraw",
            "version": 2,
            "source": "https://marketplace.visualstudio.com/items?itemName=pomdtr.excalidraw-editor",
            "elements": self.elements
        }
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

gen = ExcalidrawGenerator()

# Themes
blue_theme = ("#1864ab", "#d0ebff", "#1864ab")
gray_theme = ("#495057", "#e9ecef", "#343a40")
purple_theme = ("#7048e8", "#e5dbff", "#5f3dc4")
green_theme = ("#0ca678", "#c3fae8", "#087f5b")
yellow_theme = ("#f08c00", "#fff9db", "#5c3c00")
red_theme = ("#e03131", "#ffe3e3", "#c92a2a")

# Helper to place a grid of interconnected boxes
def place_system(gen, x_start, y_start, title, components, theme):
    # Title
    gen.add_text(title, x_start, y_start - 60, font_size=24, color=theme[0], align="left", bold=True)
    
    box_w = 400
    box_h = 140
    y_gap = 60
    
    current_y = y_start
    prev_box = None
    
    for comp in components:
        comp_title = comp.get("title")
        comp_body = comp.get("body")
        
        # Manually wrap text lines if they are too long for the box
        # For our content, I pre-wrapped them with \n, so it's fine.
        
        comp_x = x_start
        
        box_id = gen.add_rectangle(comp_x, current_y, box_w, box_h, theme[0], theme[1], theme[2], comp_title, comp_body)
        
        if prev_box and not comp.get("standalone"):
            arr_x = comp_x + box_w/2
            arr_y = current_y
            prev_y_end = current_y - y_gap
            gen.add_arrow(arr_x, prev_y_end, arr_x, arr_y, stroke_color=theme[0], text_label=comp.get("arrow_text"))
            
        prev_box = box_id
        current_y += box_h + y_gap
        
    return current_y

# ─── FLOW 1: LOGIN & REGISTER ───
flow1 = [
    {"title": "React Frontend (UI)", "body": "AuthContext, useForm()\nGestion JWT dans localStorage\nRedirections Router", "arrow_text": "Saisie & Submit"},
    {"title": "API Backend (FastAPI)", "body": "POST /api/auth/register\nPOST /api/auth/login\nValidation Pydantic (UserCreate)", "arrow_text": "JSON Payload"},
    {"title": "Logique Métier (Auth Service)", "body": "Recherche si email existe\nHachage mot de passe: passlib(bcrypt)\nSigne le JWT avec python-jose\n(Payload: sub=id, role, exp)", "arrow_text": "CRUD Database"},
    {"title": "Base de Données (PostgreSQL)", "body": "Table `users`\n- id (UUID)\n- email (Unique)\n- hashed_password\n- role (acheteur/vendeur/admin)", "arrow_text": ""}
]
place_system(gen, 100, 150, "1. Flux d'Authentification (Login & Register)", flow1, blue_theme)


# ─── FLOW 2: SCRAPERS ───
flow2 = [
    {"title": "Scripts Scrapers (Python)", "body": "MoteurMaScraper, AvitoScraper\nBeautifulSoup / Playwright\nGestion pagination & Proxys", "arrow_text": "Scraping périodique"},
    {"title": "Producteur Kafka (Producer)", "body": "Formatage en JSON brut\nconfluent_kafka.Producer.produce()", "arrow_text": "Push"},
    {"title": "Cluster Kafka", "body": "Topic: `raw-vehicles`\nPartitions: Pour répartition de charge\nRétention temporelle", "arrow_text": "Pull (Subscribe)"},
    {"title": "Consommateur Kafka (Backend)", "body": "consume_to_postgres.py\nLecture en boucle (Consumer Group)\nFiltre les doublons basiques", "arrow_text": "Déclenche Data Pipeline"}
]
place_system(gen, 700, 150, "2. Architecture des Scrapers", flow2, red_theme)


# ─── FLOW 3: DATA PIPELINE ───
flow3 = [
    {"title": "Validation & Nettoyage (Pydantic)", "body": "Mapping vers VehicleCreate\nConversion des devises\nNettoyage du kilométrage/année", "arrow_text": "Raw Data"},
    {"title": "Computer Vision (Traitement Image)", "body": "Ultralytics YOLO: Détection dommages\nImageHash: Détection photos dupliquées\nSauvegarde sur S3 / Local", "arrow_text": "URLs Images"},
    {"title": "Enrichissement NLP / ML", "body": "Analyse de sentiment sur description\nExtraction de caractéristiques\nSentence-Transformers (384-dim vector)", "arrow_text": "Textes"},
    {"title": "Stockage Multi-modèle", "body": "1. PostgreSQL: Relational (Véhicules)\n2. Qdrant: Vecteurs Sémantiques\n3. Neo4j: Graphe (User-[:VIEWS]->Vehicle)", "arrow_text": "Sync Transactionnel"}
]
place_system(gen, 100, 1100, "3. Data Pipeline & Stockage (IA)", flow3, green_theme)


# ─── FLOW 4: ACHETEUR INTERFACE ───
flow4 = [
    {"title": "Page Catalogue (Recherche)", "body": "Input texte naturel\nReact UI -> GET /api/search/parse\nRequête Qdrant (Semantic Search)\nJoin PostgreSQL pour affichage", "arrow_text": "Navigue"},
    {"title": "Détails du Véhicule (Estimation)", "body": "GET /api/pricing/predict\nModèle XGBoost chargé via joblib\nCompare 'Prix demandé' vs 'Prix marché'", "arrow_text": "Consulte"},
    {"title": "Tableau de Bord & Recommandation", "body": "Requête Neo4j: Collaborative Filtering\n\"Les utilisateurs ayant vu X ont vu Y\"\nGestion des Favoris & Historique", "arrow_text": "Interagit"},
    {"title": "Chatbot IA & Négociation", "body": "POST /api/chat (Langchain + Ollama)\nRAG: Récupère contexte Qdrant\nSystème d'Offres directes (POST /offers)", "arrow_text": ""}
]
place_system(gen, 700, 1100, "4. Expérience Acheteur & API", flow4, purple_theme)

gen.generate(r"d:\Projet automobile\vente-auto-platform\Livrables\wakala_detailed_flows_v2.excalidraw")
print("Excalidraw v2 file generated successfully.")
