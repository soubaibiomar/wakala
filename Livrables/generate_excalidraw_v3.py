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
    
    def add_text(self, text, x, y, font_size=13, color="#1e1e1e", align="left", bold=False):
        el_id = generate_id()
        
        lines = text.split('\n')
        max_line_len = max(len(line) for line in lines)
        width = max_line_len * font_size * 0.6
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

    def add_rectangle(self, x, y, width, height, stroke_color, bg_color, text_title, text_body=None):
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
        
        title_width = len(text_title) * 16 * 0.6
        title_x = x + (width - title_width) / 2
        
        title_el = self.add_text(text_title, title_x, y + 10, font_size=16, color="#495057", align="center", bold=True)
        title_el["groupIds"] = [group_id]
        
        if text_body:
            lines = text_body.split('\n')
            max_line_len = max(len(line) for line in lines)
            body_width = max_line_len * 13 * 0.6
            body_x = x + (width - body_width) / 2
            
            body_el = self.add_text(text_body, body_x, y + 36, font_size=13, color="#495057", align="center")
            body_el["groupIds"] = [group_id]
            
        return rect_id

    def add_header(self, x, y, title, subtitle):
        self.add_text(title, x, y, font_size=22, color="#1e1e1e", align="left")
        
        rect_id = generate_id()
        rect = {
            "id": rect_id,
            "type": "rectangle",
            "x": x - 100,
            "y": y + 30,
            "width": 1113,
            "height": 44,
            "angle": 0,
            "strokeColor": "#f08c00",
            "backgroundColor": "#fff9db",
            "fillStyle": "solid",
            "strokeWidth": 1,
            "strokeStyle": "solid",
            "roughness": 1,
            "opacity": 100,
            "groupIds": [],
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
        self.add_text(subtitle, x - 80, y + 42, font_size=13, color="#495057", align="left")

    def add_arrow(self, start_x, start_y, end_x, end_y, stroke_color="#495057"):
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

# Helper
def build_flow(gen, start_y, title, subtitle, steps, theme):
    gen.add_header(60, start_y, title, subtitle)
    
    current_y = start_y + 110
    box_x = 180
    text_x = 520
    box_w = 300
    box_h = 70
    gap = 44
    
    for i, step in enumerate(steps):
        # Draw main box
        gen.add_rectangle(box_x, current_y, box_w, box_h, theme[0], theme[1], step["title"], step["body"])
        
        # Draw explanation on right
        if step.get("explanation"):
            gen.add_text(step["explanation"], text_x, current_y + 15, font_size=13, color="#495057", align="left")
            
        # Draw arrow to next step
        if i < len(steps) - 1:
            arr_x = box_x + box_w / 2
            arr_y = current_y + box_h
            gen.add_arrow(arr_x, arr_y, arr_x, arr_y + gap, stroke_color=theme[0])
            current_y += box_h + gap
        else:
            current_y += box_h
            
    return current_y + 100

blue_theme = ("#1864ab", "#d0ebff")
red_theme = ("#e03131", "#ffe3e3")
green_theme = ("#0ca678", "#c3fae8")
purple_theme = ("#7048e8", "#e5dbff")
gray_theme = ("#495057", "#e9ecef")

y_pos = 0

# --- PARTIE 1 ---
flow1 = [
    {"title": "React Frontend (UI)", "body": "AuthContext, useForm()\nRedirections Router", "explanation": "L'utilisateur saisit ses identifiants.\nLe frontend gère l'état et affiche les erreurs."},
    {"title": "API Backend (FastAPI)", "body": "POST /api/auth/register\nPOST /api/auth/login", "explanation": "Les requêtes arrivent sur le serveur.\nValidation des champs avec Pydantic (UserCreate)."},
    {"title": "Logique Métier (Auth Service)", "body": "Hachage mot de passe: passlib(bcrypt)\nSigne le JWT avec python-jose", "explanation": "Le backend vérifie si l'utilisateur existe.\nIl crée un token JWT signé et le renvoie."},
    {"title": "Base de Données (PostgreSQL)", "body": "Table `users`\nUUID, Email, hashed_password, role", "explanation": "Stockage persistant des utilisateurs.\nLes rôles (acheteur/vendeur) sont enregistrés."}
]
y_pos = build_flow(gen, y_pos, "PARTIE 1 — Flux d'Authentification (Login & Register)", "En simple : L'utilisateur s'inscrit ou se connecte. Ses données sont validées, sécurisées et un JWT est renvoyé pour l'accès.", flow1, blue_theme)

# --- PARTIE 2 ---
flow2 = [
    {"title": "Scripts Scrapers (Python)", "body": "MoteurMaScraper, AvitoScraper\nGestion pagination & Proxys", "explanation": "Des scripts autonomes scannent périodiquement\nle web pour trouver de nouvelles annonces."},
    {"title": "Producteur Kafka (Producer)", "body": "Formatage en JSON brut\nconfluent_kafka.Producer.produce()", "explanation": "Les annonces extraites sont poussées dans Kafka\npour un traitement asynchrone."},
    {"title": "Cluster Kafka", "body": "Topic: `raw-vehicles`\nPartitions pour charge", "explanation": "Kafka garantit qu'aucune annonce n'est perdue\nmême si le backend est surchargé."},
    {"title": "Consommateur Kafka", "body": "consume_to_postgres.py\nLecture en boucle", "explanation": "Le consommateur lit le flux et déclenche\nle Data Pipeline principal de Wakala."}
]
y_pos = build_flow(gen, y_pos, "PARTIE 2 — Architecture des Scrapers", "En simple : Des bots récupèrent les voitures sur les sites, puis les envoient dans une file d'attente Kafka pour ne rien perdre.", flow2, red_theme)

# --- PARTIE 3 ---
flow3 = [
    {"title": "Validation & Nettoyage", "body": "Pydantic: VehicleCreate\nNettoyage du kilométrage/année", "explanation": "Les données brutes de Kafka sont\nnettoyées et les erreurs écartées."},
    {"title": "Computer Vision (Traitement Image)", "body": "Ultralytics YOLO: Détection dommages\nImageHash: Doublons", "explanation": "Les images sont téléchargées, analysées\npour trouver des dommages ou des doublons."},
    {"title": "Enrichissement NLP / ML", "body": "Analyse de sentiment (Description)\nSentence-Transformers (384-dim vector)", "explanation": "Le modèle IA calcule un vecteur sémantique\net extrait les options de la voiture."},
    {"title": "Stockage Multi-modèle", "body": "PostgreSQL: Relational\nQdrant: Vecteurs\nNeo4j: Graphe", "explanation": "Les données sont réparties selon leur usage :\nSQL (requêtes), Vecteur (IA), Graphe (Recommandation)."}
]
y_pos = build_flow(gen, y_pos, "PARTIE 3 — Data Pipeline & Traitement IA", "En simple : Chaque nouvelle voiture est analysée (images, texte) par l'IA avant d'être sauvegardée dans 3 bases de données.", flow3, green_theme)

# --- PARTIE 4 ---
flow4 = [
    {"title": "Recherche Sémantique", "body": "Input texte naturel\nReact UI -> GET /api/search/parse", "explanation": "L'acheteur cherche avec du texte libre.\nLe RAG interroge la base vectorielle Qdrant."},
    {"title": "Détails & Estimation", "body": "GET /api/pricing/predict\nModèle XGBoost (joblib)", "explanation": "Il consulte une annonce et voit si le prix\nest juste grâce à la prédiction IA XGBoost."},
    {"title": "Tableau de Bord", "body": "Requête Neo4j: Collaborative Filtering\nGestion des Favoris", "explanation": "Le moteur de graphe Neo4j lui suggère\nd'autres voitures similaires à ses goûts."},
    {"title": "Chatbot IA & Négociation", "body": "POST /api/chat (Langchain + Ollama)\nSystème d'Offres", "explanation": "Il peut négocier directement en envoyant une offre,\nou demander de l'aide technique au Chatbot IA."}
]
y_pos = build_flow(gen, y_pos, "PARTIE 4 — Expérience Acheteur & API", "En simple : L'acheteur navigue, cherche avec du texte libre (Qdrant), compare les prix (XGBoost), et reçoit des suggestions (Neo4j).", flow4, purple_theme)

gen.generate(r"d:\Projet automobile\vente-auto-platform\Livrables\wakala_detailed_flows_v3.excalidraw")
print("Excalidraw v3 file generated successfully.")
