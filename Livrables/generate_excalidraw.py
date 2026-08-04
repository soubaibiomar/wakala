import json
import uuid
import random

def generate_id():
    return str(uuid.uuid4())[:20] # Or just random string

def random_int():
    return random.randint(100000000, 2000000000)

class ExcalidrawGenerator:
    def __init__(self):
        self.elements = []
    
    def add_text(self, text, x, y, width=None, height=None, font_size=16, color="#1e1e1e", align="center", baseline=None):
        el_id = generate_id()
        if width is None:
            width = len(text) * font_size * 0.6
        if height is None:
            height = (text.count('\n') + 1) * font_size * 1.25
        
        if baseline is None:
            baseline = font_size
            
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
            "strokeWidth": 1,
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
            "baseline": baseline,
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
        title_id = generate_id()
        body_id = generate_id() if text_body else None
        
        bound_elements = [{"id": title_id, "type": "text"}]
        if text_body:
            bound_elements.append({"id": body_id, "type": "text"})
            
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
            "boundElements": bound_elements,
            "updated": 1785143082781,
            "link": None,
            "locked": False,
            "version": 2,
            "index": "a1"
        }
        self.elements.append(rect)
        
        # Add title
        title_width = len(text_title) * 16 * 0.6
        title = {
            "id": title_id,
            "type": "text",
            "x": x + (width - title_width)/2,
            "y": y + 8,
            "width": title_width,
            "height": 20,
            "angle": 0,
            "strokeColor": text_color,
            "backgroundColor": "transparent",
            "fillStyle": "solid",
            "strokeWidth": 1,
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
            "text": text_title,
            "fontSize": 16,
            "fontFamily": 1,
            "textAlign": "center",
            "verticalAlign": "middle",
            "baseline": 16,
            "containerId": rect_id,
            "originalText": text_title,
            "lineHeight": 1.25,
            "version": 2,
            "index": "a2",
            "autoResize": True
        }
        self.elements.append(title)
        
        # Add body
        if text_body:
            body_width = width - 20
            body = {
                "id": body_id,
                "type": "text",
                "x": x + 10,
                "y": y + 32,
                "width": body_width,
                "height": (text_body.count('\n')+1) * 13 * 1.25,
                "angle": 0,
                "strokeColor": text_color,
                "backgroundColor": "transparent",
                "fillStyle": "solid",
                "strokeWidth": 1,
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
                "text": text_body,
                "fontSize": 13,
                "fontFamily": 1,
                "textAlign": "center",
                "verticalAlign": "middle",
                "baseline": 13,
                "containerId": rect_id,
                "originalText": text_body,
                "lineHeight": 1.25,
                "version": 2,
                "index": "a3",
                "autoResize": True
            }
            self.elements.append(body)
            
        return rect_id

    def add_arrow(self, start_x, start_y, end_x, end_y, stroke_color="#495057"):
        arrow_id = generate_id()
        arrow = {
            "id": arrow_id,
            "type": "arrow",
            "x": start_x,
            "y": start_y,
            "width": abs(end_x - start_x),
            "height": abs(end_y - start_y),
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

    def add_flow_block(self, start_x, start_y, flow_title, steps, descriptions=None):
        # Add Title
        self.add_text(flow_title, start_x - 100, start_y, font_size=22, color="#1e1e1e", align="left")
        
        current_y = start_y + 40
        box_width = 320
        box_height = 80
        
        # Colors list based on original
        themes = [
            ("#495057", "#e9ecef", "#343a40"), # Gray
            ("#7048e8", "#e5dbff", "#5f3dc4"), # Purple
            ("#0ca678", "#c3fae8", "#087f5b"), # Green
            ("#f08c00", "#fff9db", "#5c3c00"), # Yellow
            ("#f03e3e", "#ffe3e3", "#c92a2a")  # Red
        ]
        
        for i, step in enumerate(steps):
            theme = themes[i % len(themes)]
            rect_y = current_y
            
            # Draw Box
            title = step.get('title', '')
            body = step.get('body', '')
            self.add_rectangle(start_x, rect_y, box_width, box_height, theme[0], theme[1], theme[2], title, body)
            
            # Draw Description text on the right
            if descriptions and i < len(descriptions) and descriptions[i]:
                self.add_text(descriptions[i], start_x + box_width + 40, rect_y + 20, font_size=13, color="#495057", align="left")
            
            current_y += box_height
            
            # Draw Arrow to next box
            if i < len(steps) - 1:
                arrow_y_start = current_y
                arrow_y_end = current_y + 44
                self.add_arrow(start_x + box_width/2, arrow_y_start, start_x + box_width/2, arrow_y_end, stroke_color=theme[0])
                current_y = arrow_y_end

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

# ─── FLOW 1: LOGIN & REGISTER ───
flow1_steps = [
    {"title": "Frontend (React)", "body": "AuthContext\nFormulaires Connexion / Inscription"},
    {"title": "API Backend (FastAPI)", "body": "POST /api/auth/login\nPOST /api/auth/register"},
    {"title": "Logique Métier (Auth Service)", "body": "Vérification mot de passe (bcrypt)\nGénération JWT (HS256)"},
    {"title": "Base de Données (PostgreSQL)", "body": "Table `users`\n(id, email, password_hash, role)"},
]
flow1_desc = [
    "L'utilisateur saisit ses identifiants.\nLe frontend gère l'état et affiche les erreurs.",
    "Les requêtes arrivent sur le serveur.\nValidation des champs avec Pydantic.",
    "Le backend vérifie si l'utilisateur existe.\nIl crée un token JWT signé et le renvoie.",
    "Stockage persistant des utilisateurs.\nLes rôles (acheteur/vendeur) sont enregistrés."
]
gen.add_flow_block(100, 100, "PARTIE 1 — Flux d'Authentification (Login & Register)", flow1_steps, flow1_desc)

# ─── FLOW 2: DATA PIPELINE ───
flow2_steps = [
    {"title": "Ingestion (Raw Data)", "body": "Kafka / API Ingestion\nJSON brut depuis les sources"},
    {"title": "Nettoyage & Validation", "body": "Pydantic Schemas\nStandardisation (prix, kilométrage...)"},
    {"title": "Enrichissement IA", "body": "Calcul du Score de Confiance\nGénération des embeddings (Sentence-Transformers)"},
    {"title": "Stockage Multi-modèle", "body": "PostgreSQL (Relationnel)\nQdrant (Vectoriel) | Neo4j (Graphe)"},
]
flow2_desc = [
    "Les données brutes arrivent des scrapers\nou des formulaires vendeurs.",
    "Les données sont nettoyées, les erreurs écartées,\net les formats unifiés.",
    "Le modèle IA analyse la description pour calculer\nun score, et crée un vecteur sémantique.",
    "Les données sont réparties selon leur usage :\nSQL (requêtes), Vecteur (Recherche IA), Graphe (Recommandation)."
]
gen.add_flow_block(100, 600, "PARTIE 2 — Data Pipeline (Traitement des annonces)", flow2_steps, flow2_desc)

# ─── FLOW 3: SCRAPERS ───
flow3_steps = [
    {"title": "Scrapers Externes (Python)", "body": "Scripts Playwright / BeautifulSoup\nExtraction Moteur.ma, Avito..."},
    {"title": "Producer Kafka", "body": "Envoi des données brutes\nTopic: `raw-vehicles`"},
    {"title": "Message Broker (Kafka)", "body": "File d'attente distribuée\nGestion de la charge (backpressure)"},
    {"title": "Consumer (Backend)", "body": "Lecture des messages\nDéclenchement du Data Pipeline"},
]
flow3_desc = [
    "Des scripts autonomes scannent périodiquement\nle web pour trouver de nouvelles annonces.",
    "Les annonces extraites sont poussées dans Kafka\npour un traitement asynchrone.",
    "Kafka garantit qu'aucune annonce n'est perdue\nmême si le backend est surchargé.",
    "Le consommateur lit le flux et insère\nles véhicules dans la plateforme Wakala."
]
gen.add_flow_block(800, 100, "PARTIE 3 — Architecture des Scrapers", flow3_steps, flow3_desc)


# ─── FLOW 4: ACHETEUR INTERFACE ───
flow4_steps = [
    {"title": "Catalogue & Recherche IA", "body": "Recherche sémantique (Qdrant)\nFiltres avancés"},
    {"title": "Détails du Véhicule", "body": "Estimation de prix (XGBoost)\nScore de confiance (IA)"},
    {"title": "Tableau de Bord Acheteur", "body": "Favoris (Sauvegarde)\nRecommandations personnalisées (Neo4j)"},
    {"title": "Interaction Vendeur", "body": "Faire une offre de prix\nChatbot Assistant (RAG)"},
]
flow4_desc = [
    "L'acheteur cherche avec du texte libre.\nLe RAG interroge la base vectorielle.",
    "Il consulte une annonce et voit si le prix\nest juste grâce à la prédiction IA.",
    "Le moteur de recommandation lui suggère\nd'autres voitures similaires.",
    "Il peut négocier directement en envoyant une offre,\nou demander de l'aide au Chatbot."
]
gen.add_flow_block(800, 600, "PARTIE 4 — Expérience Acheteur (Frontend)", flow4_steps, flow4_desc)


gen.generate(r"d:\Projet automobile\vente-auto-platform\Livrables\wakala_detailed_flows.excalidraw")
print("Excalidraw file generated successfully.")
