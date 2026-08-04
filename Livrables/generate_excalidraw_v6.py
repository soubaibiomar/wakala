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
    
    def add_text(self, text, x, y, font_size=13, color="#1e1e1e", align="left", bold=False, font_family=1):
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
            "fontFamily": font_family,
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

    def add_rectangle(self, x, y, width, height, stroke_color, bg_color, stroke_style="solid", fill_style="solid", roundness=3):
        rect_id = generate_id()
        
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
            "fillStyle": fill_style,
            "strokeWidth": 1.5,
            "strokeStyle": stroke_style,
            "roughness": 0 if stroke_style == "dashed" else 1,
            "opacity": 100,
            "groupIds": [],
            "frameId": None,
            "roundness": {"type": roundness} if roundness else None,
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
        return rect_id

    def add_zone(self, x, y, width, height, title):
        # The light gray bounding box
        rect_id = self.add_rectangle(x, y, width, height, "#adb5bd", "#f8f9fa", stroke_style="dashed", roundness=3)
        # Move zone to the very back by putting it at the start of elements array
        zone_el = self.elements.pop()
        self.elements.insert(0, zone_el)
        
        # Zone title (uppercase, top-left)
        self.add_text(title.upper(), x - 40, y + 20, font_size=12, color="#868e96", align="right", bold=True)
        return rect_id

    def add_node(self, x, y, width, theme, title, routes=None, body=None, body_align="center"):
        # Calculate dynamic height
        routes_h = len(routes) * 20 if routes else 5
        body_h = (body.count('\n') + 1) * 20 if body else 0
        box_h = 50 + routes_h + body_h
        
        rect_id = self.add_rectangle(x, y, width, box_h, theme[0], theme[1])
        
        # We find the rect to add groupIds
        rect_el = next(e for e in self.elements if e["id"] == rect_id)
        group_id = generate_id()
        rect_el["groupIds"] = [group_id]
        
        title_width = len(title) * 16 * 0.6
        title_x = x + (width - title_width) / 2
        title_el = self.add_text(title, title_x, y + 12, font_size=16, color="#1e1e1e", align="center", bold=True)
        title_el["groupIds"] = [group_id]
        
        current_y_offset = 35

        if routes:
            for route in routes:
                route_width = len(route) * 12 * 0.6
                route_x = x + (width - route_width) / 2
                route_el = self.add_text(route, route_x, y + current_y_offset, font_size=12, color="#c92a2a", align="center", font_family=3)
                route_el["groupIds"] = [group_id]
                current_y_offset += 20
        else:
            current_y_offset += 5

        if body:
            lines = body.split('\n')
            max_line_len = max(len(line) for line in lines)
            body_width = max_line_len * 13 * 0.6
            
            if body_align == "center":
                body_x = x + (width - body_width) / 2
            else:
                body_x = x + 15
                
            body_el = self.add_text(body, body_x, y + current_y_offset + 5, font_size=13, color="#495057", align=body_align)
            body_el["groupIds"] = [group_id]
            
        return {"id": rect_id, "x": x, "y": y, "width": width, "height": box_h, "bottom": y + box_h}

    def add_header(self, x, y, title, subtitle):
        self.add_text(title, x, y, font_size=24, color="#1e1e1e", align="left", bold=True)
        
        rect_id = self.add_rectangle(x - 100, y + 40, 1113, 44, "#f08c00", "#fff9db")
        self.add_text(subtitle, x - 80, y + 52, font_size=14, color="#5c3c00", align="left")

    def add_arrow(self, start_x, start_y, end_x, end_y, stroke_color="#495057", dashed=False):
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
            "strokeStyle": "dashed" if dashed else "solid",
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

    def add_detail_box(self, x, y, width, theme, title, text_body, icon_text=None, title_color=None):
        # dynamic height for detail boxes
        lines = text_body.split('\n')
        body_h = len(lines) * 20
        box_h = 60 + body_h
        
        rect_id = self.add_rectangle(x, y, width, box_h, theme[0], theme[1])
        group_id = generate_id()
        rect_el = next(e for e in self.elements if e["id"] == rect_id)
        rect_el["groupIds"] = [group_id]
        
        # Add Icon if present
        title_x = x + 15
        if icon_text:
            icon_el = self.add_text(icon_text, title_x, y + 10, font_size=16, color=title_color or theme[0], align="left", bold=True)
            icon_el["groupIds"] = [group_id]
            title_x += 30
            
        title_el = self.add_text(title, title_x, y + 10, font_size=14, color=title_color or theme[0], align="left", bold=True)
        title_el["groupIds"] = [group_id]
        
        body_el = self.add_text(text_body, x + 15, y + 40, font_size=13, color="#495057", align="left")
        body_el["groupIds"] = [group_id]
        
        return {"id": rect_id, "x": x, "y": y, "width": width, "height": box_h, "bottom": y + box_h}

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

blue_theme = ("#1864ab", "#d0ebff")
red_theme = ("#e03131", "#ffe3e3")
green_theme = ("#0ca678", "#c3fae8")
purple_theme = ("#7048e8", "#e5dbff")
gray_theme = ("#495057", "#e9ecef")
yellow_theme = ("#f08c00", "#fff9db")
orange_theme = ("#d9480f", "#fff4e6")

# --- GLOBAL SETTINGS ---
current_y = 0
zone_w = 1000
zone_x = 160
node_w = 340
center_x = zone_x + (zone_w / 2) - (node_w / 2)

# --- PARTIE 1 ---
gen.add_header(60, current_y, "PARTIE 1 — Flux d'Authentification Détaillé", "En simple : Le front-end envoie les identifiants aux routes d'API correspondantes. Le backend sécurise et interagit avec PostgreSQL.")
current_y += 120

# Zone 1
z1_h = 160
gen.add_zone(zone_x, current_y, zone_w, z1_h, "CLIENT (FRONTEND)")
n1 = gen.add_node(center_x, current_y + 20, node_w, blue_theme, "React Frontend (Formulaires)", ["/login", "/register", "useAuth() -> Zustand Slice"], "Gestion de l'état (Zustand / Context)\nEnregistrement du Token JWT dans localStorage/Cookies\nMiddleware Route Guard (Zod/Yup validations)")
current_y += z1_h + 30

gen.add_arrow(n1["x"] + node_w/2, n1["bottom"], n1["x"] + node_w/2, current_y + 20)

# Zone 2
z2_h = 160
gen.add_zone(zone_x, current_y, zone_w, z2_h, "API GATEWAY & ROUTING")
n2 = gen.add_node(center_x, current_y + 20, node_w, blue_theme, "API Gateway (FastAPI / Nginx)", ["POST /api/auth/register", "POST /api/auth/login", "GET /api/users/me"], "FastAPI Router (`routes_auth.py`)\nCORS Policy & Rate Limiting (10 req/min)\nValidation Pydantic (UserCreate, TokenResponse)")
current_y += z2_h + 30

gen.add_arrow(n2["x"] + node_w/2, n2["bottom"], n2["x"] + node_w/2, current_y + 20)

# Zone 3
z3_h = 160
gen.add_zone(zone_x, current_y, zone_w, z3_h, "CORE BUSINESS LOGIC")
n3 = gen.add_node(center_x, current_y + 20, node_w, blue_theme, "Service Authentification", ["AuthService.authenticate()", "TokenService.create_access_token()"], "bcrypt: Vérification & Hachage du MDP\npython-jose: Signature du JWT (HS256)\nPayload Injecté: sub, exp, role")
current_y += z3_h + 30

gen.add_arrow(n3["x"] + node_w/2, n3["bottom"], n3["x"] + node_w/2, current_y + 20)

# Zone 4
z4_h = 180
gen.add_zone(zone_x, current_y, zone_w, z4_h, "PERSISTENCE")
n4 = gen.add_node(center_x, current_y + 20, node_w, yellow_theme, "PostgreSQL (Table Users)", ["CREATE TABLE users"], "  - id (UUID PRIMARY KEY)\n  - email (VARCHAR UNIQUE, INDEXED)\n  - hashed_password (VARCHAR)\n  - role (ENUM: admin/buyer/seller)\n  - is_active (BOOLEAN DEFAULT TRUE)", body_align="left")
current_y += z4_h + 30

# DETAILS 1
z_det1_h = 180
gen.add_zone(zone_x, current_y, zone_w, z_det1_h, "DÉTAIL - SÉCURITÉ & TOKENS")
gen.add_detail_box(zone_x + 40, current_y + 20, 920, blue_theme, "Détail - Sécurité Avancée et Architecture JWT", "1. Le mot de passe est haché avec bcrypt (work factor=12) pour ralentir les attaques par force brute (défense Rainbow Tables).\n2. Le token JWT a une durée de vie courte (Access Token = 15 min). Un Refresh Token (valide 7 jours) est stocké dans un cookie HTTPOnly empêchant le vol via XSS.\n3. Payload JWT typique : { \"iss\": \"wakala-api\", \"sub\": \"user_uuid\", \"exp\": 171829432, \"roles\": [\"buyer\"] }.\n4. Les mots de passe ne sont JAMAIS stockés en clair et ne transitent jamais dans les logs de l'application FastAPI.", icon_text="🔒")
current_y += z_det1_h + 150


# --- PARTIE 2 ---
gen.add_header(60, current_y, "PARTIE 2 — Architecture des Scrapers", "En simple : Des scripts parcourent le web, collectent des données brutes, et les confient à Kafka qui garantit la livraison au serveur.")
current_y += 120

# Zone 1 (Side by side nodes)
z1_h = 160
gen.add_zone(zone_x, current_y, zone_w, z1_h, "DATA ACQUISITION")
n2_1 = gen.add_node(zone_x + 100, current_y + 20, node_w, red_theme, "Scraper Avito", ["Cron: 0 */4 * * *", "Parser: BeautifulSoup4"], "Extraction HTML (div.price, span.mileage)\nRotation d'User-Agents Résidentiels")
n2_2 = gen.add_node(zone_x + 560, current_y + 20, node_w, red_theme, "Scraper Moteur.ma", ["Cron: 0 */4 * * *", "Parser: Playwright"], "Script Headless Browser (JS Rendering)\nContournement Cloudflare & Proxys")
current_y += z1_h + 30

# Zone 2 (Message Broker)
z2_h = 280
gen.add_zone(zone_x, current_y, zone_w, z2_h, "MESSAGE BROKER (KAFKA)")
n2_3 = gen.add_node(center_x, current_y + 20, node_w, gray_theme, "Kafka Producer", ["confluent_kafka.Producer"], "Sérialisation en JSON (Schema Registry)\nGestion des timeouts (request.timeout.ms=30000)\nRetries = Integer.MAX_VALUE")
gen.add_arrow(n2_1["x"] + node_w/2, n2_1["bottom"], n2_3["x"] + node_w/4, n2_3["y"], dashed=True)
gen.add_arrow(n2_2["x"] + node_w/2, n2_2["bottom"], n2_3["x"] + 3*node_w/4, n2_3["y"], dashed=True)

n2_4 = gen.add_node(center_x, n2_3["bottom"] + 40, node_w, red_theme, "Cluster Kafka (Topics)", ["Topic: raw-vehicles (Partitions: 3)", "Topic: dlq-vehicles (Dead Letter Queue)"], "Rétention: 7 jours (log.retention.hours=168)\nRéplication: Factor 3 (Haute Disponibilité)")
gen.add_arrow(n2_3["x"] + node_w/2, n2_3["bottom"], n2_4["x"] + node_w/2, n2_4["y"])
current_y += z2_h + 30

# Zone 3
z3_h = 160
gen.add_zone(zone_x, current_y, zone_w, z3_h, "INGESTION")
n2_5 = gen.add_node(center_x, current_y + 20, node_w, blue_theme, "Kafka Consumer (Backend)", ["Background Task (FastAPI / Faust)"], "Boucle `consumer.poll()` continue\nDé-duplication basique par URL d'origine (Redis Cache)")
gen.add_arrow(n2_4["x"] + node_w/2, n2_4["bottom"], n2_5["x"] + node_w/2, n2_5["y"])
current_y += z3_h + 30

# DETAILS 2
z_det2_h = 240
gen.add_zone(zone_x, current_y, zone_w, z_det2_h, "DÉTAIL - RÉSILIENCE, CRAWLING & SCHEMAS")
gen.add_detail_box(zone_x + 40, current_y + 20, 920, red_theme, "Détail - Contournement, DLQ (Dead Letter Queue) & JSON Schema", "1. Proxy Rotation: Les scripts utilisent des proxys résidentiels et injectent des headers (User-Agent, Accept-Language) qui changent à chaque requête pour éviter le blocage par Cloudflare / Captchas.\n2. Backoff Exponentiel: En cas d'échec de chargement HTTP 429, le script attend 2s, puis 4s, puis 8s.\n3. Tolérance aux pannes: Si le parser échoue parce que le site a changé de structure, le message JSON brut est envoyé dans le topic `dlq-vehicles` pour une analyse manuelle. Aucune donnée n'est perdue.\n4. Schéma JSON Produit : { \"id\": \"uniq-123\", \"source_url\": \"avito.ma/...\", \"title\": \"Golf 7\", \"raw_price\": \"120 000 DH\", \"raw_mileage\": \"100k km\" }", icon_text="🕸️")
current_y += z_det2_h + 150


# --- PARTIE 3 ---
gen.add_header(60, current_y, "PARTIE 3 — Data Pipeline Intégré (Vision & NLP)", "En simple : La donnée passe par un tunnel de validation, puis des IAs analysent l'image et le texte avant de tout stocker.")
current_y += 120

# Zone 1
z1_h = 180
gen.add_zone(zone_x, current_y, zone_w, z1_h, "VALIDATION & NETTOYAGE")
n3_1 = gen.add_node(center_x, current_y + 20, node_w, green_theme, "Pipeline Processor", ["Service: pipeline.clean_data()", "Model: Pydantic VehicleCreate"], "Nettoyage Regex (ex: '100k km' -> 100000)\nHomogénéisation des devises (MAD)\nMapping Strict (Rejet si données critiques manquantes)")
current_y += z1_h + 30

# Zone 2
z2_h = 220
gen.add_zone(zone_x, current_y, zone_w, z2_h, "AI ENRICHMENT & FEATURE EXTRACTION")
n3_2 = gen.add_node(zone_x + 100, current_y + 20, node_w, purple_theme, "Computer Vision (Images)", ["Worker: Celery / GPU Task", "GET /api/images/process (interne)"], "Pré-processing: Resize 640x640, Normalize\nUltralytics YOLOv8: Détection chocs/rayures\nImageHash: Détection d'annonces en double (Hamming Distance)")
n3_3 = gen.add_node(zone_x + 560, current_y + 20, node_w, purple_theme, "Moteur NLP (Texte)", ["Model: all-MiniLM-L6-v2 (HuggingFace)", "Inférence: PyTorch CPU/GPU"], "Analyse de sentiment sur la description globale\nExtraction NLP des options (Toit ouvrant, cuir, radar)\nGénération de l'Embedding Sémantique (Vecteur 384 dimensions)")
gen.add_arrow(n3_1["x"] + node_w/2, n3_1["bottom"], n3_2["x"] + node_w/2, n3_2["y"])
gen.add_arrow(n3_1["x"] + node_w/2, n3_1["bottom"], n3_3["x"] + node_w/2, n3_3["y"])
current_y += z2_h + 30

# Zone 3 (Triple side-by-side)
z3_h = 220
gen.add_zone(zone_x, current_y, zone_w, z3_h, "MULTI-MODEL STORAGE")
n3_4 = gen.add_node(zone_x + 20, current_y + 20, node_w - 40, yellow_theme, "PostgreSQL", ["ORM: SQLAlchemy"], "Table `vehicles` (Relational)\nIndex B-Tree sur Marque, Modèle, Prix\nStocke les URL des images et IDs")
n3_5 = gen.add_node(zone_x + 340, current_y + 20, node_w - 40, yellow_theme, "Qdrant", ["Client: qdrant-client"], "Collection `vehicles_vectors`\nStocke les vecteurs 384-dim (Payload ID)\nRecherche Cosine Similarity")
n3_6 = gen.add_node(zone_x + 660, current_y + 20, node_w - 40, yellow_theme, "Neo4j", ["Client: neo4j-driver"], "Graph Node: `(:Vehicle {id: '...'})`\nRelations: `(User)-[:VIEWS]->(Vehicle)`\nRelations: `(Vehicle)-[:SIMILAR_TO]->(Vehicle)`")

gen.add_arrow(n3_2["x"] + node_w/2, n3_2["bottom"], n3_4["x"] + (node_w-40)/2, n3_4["y"])
gen.add_arrow(n3_3["x"] + node_w/2, n3_3["bottom"], n3_5["x"] + (node_w-40)/2, n3_5["y"])
gen.add_arrow(n3_3["x"] + node_w/2, n3_3["bottom"], n3_6["x"] + (node_w-40)/2, n3_6["y"], dashed=True)
current_y += z3_h + 30

# DETAILS 3
z_det3_h = 180
gen.add_zone(zone_x, current_y, zone_w, z_det3_h, "DÉTAIL - VECTORISATION & COMPUTER VISION")
gen.add_detail_box(zone_x + 40, current_y + 20, 920, green_theme, "Détail - Embedding et Pipeline Moteur de Recherche Vectoriel", "1. Le texte de l'annonce ('Superbe Golf 7 bien entretenue toit ouvrant') est converti par Sentence-Transformers (`all-MiniLM-L6-v2`) en un tenseur PyTorch, puis en tableau de 384 nombres flottants.\n2. Qdrant stocke ces vecteurs en utilisant un index HNSW (Hierarchical Navigable Small World) pour permettre des recherches sémantiques approximatives (ANN) en millisecondes, calculant la distance cosinus entre la requête texte de l'utilisateur et les annonces.\n3. YOLOv8 applique le filtrage Non-Maximum Suppression (NMS) pour éviter les détections de rayures en double sur une même zone d'image.", icon_text="🧠")
current_y += z_det3_h + 150


# --- PARTIE 4 ---
gen.add_header(60, current_y, "PARTIE 4 — L'Interface Acheteur (Routes & IA)", "En simple : L'interface web appelle l'API FastAPI, qui orchestre l'accès aux IAs (Qdrant, XGBoost, LLM) pour servir l'acheteur.")
current_y += 120

# Zone 1
z1_h = 180
gen.add_zone(zone_x, current_y, zone_w, z1_h, "INTENTION UTILISATEUR & UI COMPONENTS")
n4_1 = gen.add_node(center_x, current_y + 20, node_w, blue_theme, "Actions Frontend (React)", ["<SearchEngine />", "<VehicleDetails />", "<ChatbotWidget />"], "L'utilisateur cherche 'voiture montagne' dans l'Omnibox\nConsulte les détails d'un SUV 4x4 (Galerie, Specs)\nDéclenche un WebSocket avec l'assistant IA")
current_y += z1_h + 30

# Zone 2
z2_h = 280
gen.add_zone(zone_x, current_y, zone_w, z2_h, "ORCHESTRATION API")
n4_2 = gen.add_node(zone_x + 40, current_y + 20, node_w - 40, gray_theme, "Search API", ["GET /api/vehicles/search?q=...", "Filters: min_price, max_price, year"], "Convertit requête texte\nen recherche vectorielle Qdrant\nFiltres pré-appliqués SQL")
n4_3 = gen.add_node(zone_x + 360, current_y + 20, node_w - 40, gray_theme, "Pricing API", ["GET /api/pricing/predict/{id}"], "Récupère les features (Marque, Modèle, Année, Km)\nConstruit le DataFrame Pandas\nAppelle le modèle XGBoost")
n4_4 = gen.add_node(zone_x + 680, current_y + 20, node_w - 40, gray_theme, "Chat API (RAG WebSocket)", ["ws://api/chat/stream", "POST /api/chat/offer"], "Gère l'historique conversationnel (Session Memory)\nInjecte le contexte système (Ton, Limites)\nStream les tokens de réponse (Server-Sent Events)")

gen.add_arrow(n4_1["x"] + node_w/2, n4_1["bottom"], n4_2["x"] + (node_w-40)/2, n4_2["y"])
gen.add_arrow(n4_1["x"] + node_w/2, n4_1["bottom"], n4_3["x"] + (node_w-40)/2, n4_3["y"])
gen.add_arrow(n4_1["x"] + node_w/2, n4_1["bottom"], n4_4["x"] + (node_w-40)/2, n4_4["y"])
current_y += z2_h + 30

# Zone 3
z3_h = 240
gen.add_zone(zone_x, current_y, zone_w, z3_h, "MOTEURS IA & DONNEES")
n4_5 = gen.add_node(zone_x + 40, current_y + 20, node_w - 40, purple_theme, "Qdrant + Postgres", [], "Similarity Search pour trouver\nles véhicules pertinents\nLeft Join SQL pour la pagination (LIMIT/OFFSET)")
n4_6 = gen.add_node(zone_x + 360, current_y + 20, node_w - 40, purple_theme, "XGBoost (Regression)", ["Library: scikit-learn / xgboost"], "Arbres de décisions (Gradient Boosting)\nEstime la valeur juste (Prix Marché)\npour comparaison avec Prix Demandé")
n4_7 = gen.add_node(zone_x + 680, current_y + 20, node_w - 40, purple_theme, "LLM (Ollama / Llama3 / Groq)", ["Framework: LangChain (Agent Executor)"], "Agent RAG fournissant des\nconseils techniques personnalisés\nCapable d'évaluer une offre de prix via Tool Calling")

gen.add_arrow(n4_2["x"] + (node_w-40)/2, n4_2["bottom"], n4_5["x"] + (node_w-40)/2, n4_5["y"])
gen.add_arrow(n4_3["x"] + (node_w-40)/2, n4_3["bottom"], n4_6["x"] + (node_w-40)/2, n4_6["y"])
gen.add_arrow(n4_4["x"] + (node_w-40)/2, n4_4["bottom"], n4_7["x"] + (node_w-40)/2, n4_7["y"])
current_y += z3_h + 30

# DETAILS 4 (Based EXACTLY on user's screenshot details for Recommendation Hybrid formula)
z_det4_h = 360
gen.add_zone(zone_x, current_y, zone_w, z_det4_h, "DÉTAIL DES FORMULES")
gen.add_detail_box(zone_x + 40, current_y + 20, 440, purple_theme, "Détail - Filtrage par Contenu", "1. V_user = [budget, usage, prestige, passagers]\n2. V_annonce = [prix, type, cause, places, finitions]\n3. Les deux vecteurs vivent dans l'espace Embeddings de Qdrant (dim = 384).\n4. On calcule sim = cosine(V_user, V_annonce). Plus l'angle est petit, plus le match est fort.\n\nAvantage: prédictible, explicable, sans historique requis.", icon_text="⚙️")
gen.add_detail_box(zone_x + 520, current_y + 20, 440, purple_theme, "Détail - Filtrage Collaboratif", "1. Identifier le Persona de l'utilisateur.\n2. Traverser le graphe Neo4j :\n   (user) -[:AIME]->(V_1)<-[:AIME]- (user2)\n   (user2) -[:A_ACHETE]->(V_Reco)\n3. Pondérer par type d'interaction: Sauvegarde (x3) > Clic (x1) > Vue (x0.5)\n4. Pondérer par récence.\n\nAvantage: capte les signaux implicites.", icon_text="🔗")

gen.add_detail_box(zone_x + 40, current_y + 220, 920, orange_theme, "Problème du Cold Start & Poids Dynamiques", "Au lancement, le graphe Neo4j est vide : aucune interaction à exploiter. Le système démarre en mode `Contenu Seul` (W1 = 100%, W2 = 0%).\nÀ mesure que les utilisateurs interagissent (clics, sauvegardes, achats), le poids W2 augmente progressivement. L'intelligence collective démarre.\nFormule d'ajustement: W2 = min(0.5, log(1 + N_interactions) / K)", icon_text="⚠️", title_color="#d9480f")

current_y += z_det4_h + 50

gen.generate(r"d:\Projet automobile\vente-auto-platform\Livrables\wakala_architecture_layered.excalidraw")
print("Excalidraw Layered file generated successfully.")
