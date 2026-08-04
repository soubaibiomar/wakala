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

    def add_rectangle(self, x, y, width, height, stroke_color, bg_color, text_title, routes=None, text_body=None):
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
        
        title_el = self.add_text(text_title, title_x, y + 10, font_size=16, color="#1e1e1e", align="center", bold=True)
        title_el["groupIds"] = [group_id]
        
        current_y_offset = 35

        # Render Routes
        if routes:
            for route in routes:
                route_width = len(route) * 12 * 0.6
                route_x = x + (width - route_width) / 2
                route_el = self.add_text(route, route_x, y + current_y_offset, font_size=12, color="#c92a2a", align="center", font_family=3) # Family 3 is Monospace in Excalidraw usually, or just visually different
                route_el["groupIds"] = [group_id]
                current_y_offset += 20
        else:
            current_y_offset += 5

        # Render Body
        if text_body:
            lines = text_body.split('\n')
            max_line_len = max(len(line) for line in lines)
            body_width = max_line_len * 13 * 0.6
            body_x = x + (width - body_width) / 2
            
            body_el = self.add_text(text_body, body_x, y + current_y_offset, font_size=13, color="#495057", align="center")
            body_el["groupIds"] = [group_id]
            
        return rect_id

    def add_header(self, x, y, title, subtitle):
        self.add_text(title, x, y, font_size=22, color="#1e1e1e", align="left", bold=True)
        
        rect_id = generate_id()
        rect = {
            "id": rect_id,
            "type": "rectangle",
            "x": x - 100,
            "y": y + 40,
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
        self.add_text(subtitle, x - 80, y + 52, font_size=14, color="#5c3c00", align="left")

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
    
    current_y = start_y + 120
    box_x = 120
    text_x = 520
    box_w = 340
    box_h = 110 # Increased height for routes
    gap = 50
    
    for i, step in enumerate(steps):
        # Draw main box
        gen.add_rectangle(box_x, current_y, box_w, box_h, theme[0], theme[1], step["title"], step.get("routes"), step["body"])
        
        # Draw explanation on right
        if step.get("explanation"):
            gen.add_text(step["explanation"], text_x, current_y + 20, font_size=14, color="#495057", align="left")
            
        # Draw arrow to next step
        if i < len(steps) - 1:
            arr_x = box_x + box_w / 2
            arr_y = current_y + box_h
            gen.add_arrow(arr_x, arr_y, arr_x, arr_y + gap, stroke_color=theme[0])
            current_y += box_h + gap
        else:
            current_y += box_h
            
    return current_y + 120

blue_theme = ("#1864ab", "#d0ebff")
red_theme = ("#e03131", "#ffe3e3")
green_theme = ("#0ca678", "#c3fae8")
purple_theme = ("#7048e8", "#e5dbff")
gray_theme = ("#495057", "#e9ecef")

y_pos = 0

# --- PARTIE 1 ---
flow1 = [
    {
        "title": "Client React (Formulaires)", 
        "routes": ["/login", "/register"],
        "body": "Gestion de l'état (Zustand / Context)\nEnregistrement du Token JWT\nMiddleware Route Guard", 
        "explanation": "L'utilisateur interagit avec l'interface React.\nLes formulaires sont validés côté client (Zod/Yup)."
    },
    {
        "title": "API Gateway / Auth Controller", 
        "routes": ["POST /api/auth/register", "POST /api/auth/login", "GET /api/users/me"],
        "body": "FastAPI Router (`routes_auth.py`)\nValidation Pydantic (UserCreate, TokenResponse)", 
        "explanation": "Les requêtes sont reçues par FastAPI.\nPydantic s'assure que les champs (email, mot de passe)\nsont corrects."
    },
    {
        "title": "Service Authentification", 
        "routes": [],
        "body": "bcrypt: Vérification & Hachage du MDP\npython-jose: Signature du JWT (HS256)\nPayload: sub, exp, role", 
        "explanation": "Le service gère la logique de sécurité pure.\nIl compare les mots de passe hachés, et émet un token\nqui sera exigé pour les prochaines requêtes."
    },
    {
        "title": "PostgreSQL (Table Users)", 
        "routes": ["CREATE TABLE users"],
        "body": "- id (UUID)\n- email (VARCHAR UNIQUE)\n- hashed_password (VARCHAR)\n- role (ENUM: admin/buyer/seller)", 
        "explanation": "Les utilisateurs sont stockés en base relationnelle.\nOn utilise SQLAlchemy ou SQLModel comme ORM."
    }
]
y_pos = build_flow(gen, y_pos, "PARTIE 1 — Flux d'Authentification Détaillé", "En simple : Le front-end envoie les identifiants aux routes d'API correspondantes. Le backend sécurise et interagit avec PostgreSQL.", flow1, blue_theme)


# --- PARTIE 2 ---
flow2 = [
    {
        "title": "Pool de Scrapers Python", 
        "routes": ["Cron: 0 */4 * * *"],
        "body": "AvitoScraper.py, MoteurMaScraper.py\nRotation d'User-Agents & Proxys\nExtraction BeautifulSoup/Playwright", 
        "explanation": "Des scripts externes se déclenchent régulièrement.\nIls contournent les bloqueurs et extraient le code HTML\ndes annonces de voitures."
    },
    {
        "title": "Kafka Producer", 
        "routes": ["confluent_kafka.Producer"],
        "body": "Sérialisation en JSON\nGestion des timeouts et retries", 
        "explanation": "Les annonces parsées sont empaquetées en JSON.\nElles sont envoyées au Producer Kafka de manière asynchrone."
    },
    {
        "title": "Broker Kafka (Topics)", 
        "routes": ["Topic: raw-vehicles", "Topic: dlq-vehicles"],
        "body": "Rétention: 7 jours\nPartitions: 3 (Scaling horizontal)", 
        "explanation": "Kafka stocke les messages temporairement.\nSi le backend crash, les messages attendent ici (pas de perte de données)."
    },
    {
        "title": "Kafka Consumer (Backend)", 
        "routes": ["Background Task (FastAPI)"],
        "body": "Boucle `consumer.poll()`\nDé-duplication basique par URL d'origine", 
        "explanation": "Le backend écoute le topic en tâche de fond.\nDès qu'un message arrive, il l'injecte dans le Data Pipeline."
    }
]
y_pos = build_flow(gen, y_pos, "PARTIE 2 — Architecture des Scrapers", "En simple : Des scripts parcourent le web, collectent des données brutes, et les confient à Kafka qui garantit la livraison au serveur.", flow2, red_theme)


# --- PARTIE 3 ---
flow3 = [
    {
        "title": "Ingestion & Nettoyage", 
        "routes": ["Service: pipeline.clean_data()"],
        "body": "Conversion String -> Int (Kilométrage)\nHomogénéisation des devises (MAD)\nMapping Pydantic strict", 
        "explanation": "La donnée brute est normalisée.\nLes erreurs de saisie originales (ex: 'km' au lieu de chiffres)\nsont corrigées."
    },
    {
        "title": "Computer Vision (Images)", 
        "routes": ["GET /api/images/process (interne)"],
        "body": "Téléchargement asynchrone des photos\nUltralytics YOLO: Détection de chocs/rayures\nImageHash: Détection d'annonces en double", 
        "explanation": "Les photos de l'annonce sont analysées par l'IA visuelle.\nOn détermine l'état général de la carrosserie."
    },
    {
        "title": "Moteur NLP (Texte)", 
        "routes": ["Model: sentence-transformers"],
        "body": "Analyse de sentiment sur la description\nExtraction NLP des options (Toit ouvrant, etc.)\nGénération de l'Embedding (384 dimensions)", 
        "explanation": "Le texte est converti en un vecteur mathématique.\nCela permettra à la recherche sémantique de comprendre\nle vrai sens de l'annonce."
    },
    {
        "title": "Multi-Stockage Synchronisé", 
        "routes": ["SQLAlchemy", "QdrantClient", "Neo4jDriver"],
        "body": "1. PostgreSQL (Table `vehicles`)\n2. Qdrant (Collection `vehicles_vectors`)\n3. Neo4j (Node `Vehicle`)", 
        "explanation": "Les données sont réparties pour être interrogées efficacement.\nRelationnel pour le CRUD, Vectoriel pour la recherche sémantique,\nGraphe pour les liens entre les utilisateurs et les annonces."
    }
]
y_pos = build_flow(gen, y_pos, "PARTIE 3 — Data Pipeline Intégré (Vision & NLP)", "En simple : La donnée passe par un tunnel de validation, puis des IAs analysent l'image et le texte avant de tout stocker intelligemment.", flow3, green_theme)


# --- PARTIE 4 ---
flow4 = [
    {
        "title": "Recherche Sémantique Avancée", 
        "routes": ["/search (React)", "GET /api/vehicles/search?q=..."],
        "body": "Prompt NLP transformé en Embedding\nSimilarity Search dans Qdrant\nLeft Join sur PostgreSQL", 
        "explanation": "L'utilisateur cherche 'voiture familiale pour montagne'.\nQdrant trouve les vecteurs les plus proches (ex: SUV 4x4).\nPostgreSQL fournit les détails complets à afficher."
    },
    {
        "title": "Prédiction de Prix (XGBoost)", 
        "routes": ["/vehicle/:id (React)", "GET /api/pricing/predict/{id}"],
        "body": "Extraction features (Marque, Km, Année)\nInférence Modèle XGBoost\nRetourne [Prix Bas, Prix Moyen, Prix Haut]", 
        "explanation": "L'acheteur regarde une voiture. L'API consulte le modèle\nMachine Learning entraîné sur tout le marché pour dire si le prix est juste."
    },
    {
        "title": "Moteur de Recommandations", 
        "routes": ["/dashboard/recommendations", "GET /api/recommendations"],
        "body": "Cypher Query dans Neo4j\n(User)-[:VIEWED]->(Car)<-[:VIEWED]-(OtherUser)", 
        "explanation": "Dans son tableau de bord, l'acheteur voit des voitures\nque d'autres acheteurs ayant le même profil ont appréciées."
    },
    {
        "title": "Chatbot Assistant (RAG) & Offres", 
        "routes": ["POST /api/chat", "POST /api/offers"],
        "body": "Langchain + Ollama/Groq\nRAG contextuel sur les voitures Qdrant\nNégociation avec POST /api/offers", 
        "explanation": "L'acheteur pose des questions techniques au chatbot IA.\nIl peut ensuite déclencher une offre de prix via l'API transactionnelle."
    }
]
y_pos = build_flow(gen, y_pos, "PARTIE 4 — L'Interface Acheteur (Routes & IA)", "En simple : L'interface web appelle de multiples routes de l'API FastAPI, qui orchestre l'accès aux IAs (Qdrant, XGBoost, LLM) pour servir l'acheteur.", flow4, purple_theme)

gen.generate(r"d:\Projet automobile\vente-auto-platform\Livrables\wakala_detailed_flows_v4.excalidraw")
print("Excalidraw v4 file generated successfully.")
