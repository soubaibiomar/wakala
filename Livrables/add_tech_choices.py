import uuid
import time

filepath = "D:/Projet automobile/vente-auto-platform/Livrables/wakala_architecture_complete_technique.excalidraw"

with open(filepath, "r", encoding="utf-8") as f:
    data = json.load(f)

# Find max Y
max_y = 0
for el in data["elements"]:
    y = el.get("y", 0)
    h = el.get("height", 0)
    if y + h > max_y:
        max_y = y + h

def create_text(text, x, y, size=16, color="#000000", font_family=1):
    lines = text.split('\n')
    max_line_len = max([len(line) for line in lines]) if lines else len(text)
    
    return {
        "id": str(uuid.uuid4()),
        "type": "text",
        "x": x,
        "y": y,
        "width": max_line_len * (size * 0.6),
        "height": size * 1.25 * len(lines),
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
        "seed": int(time.time() * 1000) % 1000000000,
        "versionNonce": int(time.time() * 1000) % 1000000000,
        "isDeleted": False,
        "boundElements": [],
        "updated": int(time.time() * 1000),
        "link": None,
        "locked": False,
        "text": text,
        "fontSize": size,
        "fontFamily": font_family,
        "textAlign": "left",
        "verticalAlign": "top",
        "baseline": size,
        "containerId": None,
        "originalText": text,
        "lineHeight": 1.25,
        "version": 1,
        "index": None
    }


detailed_text = """JUSTIFICATION DES CHOIX TECHNIQUES (POURQUOI CES TECHNOS ?)

1. Backend : FastAPI (Python)
   - Pourquoi : Nativement Asynchrone (hautes performances I/O pour gérer de multiples requêtes) et 100% compatible avec l'écosystème ML/Data (PyTorch, Scikit-learn, Pandas) sans avoir à créer des microservices passerelles dans d'autres langages.

2. IA & NLP : Groq API + Llama 3.3
   - Pourquoi Groq : Offre une latence ultra-faible (LPU au lieu de GPU) permettant un chat en temps réel sans "lag" frustrant pour l'utilisateur.
   - Pourquoi Llama 3.3 : Puissance de raisonnement State-of-the-Art idéale pour extraire des entités complexes (budget, priorités) d'un prompt texte en "Zero-Shot".

3. Base de Données Vectorielle : Qdrant / Milvus
   - Pourquoi : PostgreSQL avec pgvector est bien pour débuter, mais un Vector DB natif (HNSW index) est indispensable à grande échelle pour calculer la distance (Cosine Similarity) entre des milliers de vecteurs (voitures) en moins de 50ms.

4. Streaming & Data Processing : Apache Kafka + Spark
   - Pourquoi : Kafka absorbe les pics de trafic issus des scrapers (des milliers d'annonces aspirées en même temps) sans surcharger la DB. Spark permet de calculer les embeddings et d'appliquer les modèles de ML sur de gros volumes (Batch ETL).

5. Graphe de Connaissance : Neo4j (Pour le Trust Engine)
   - Pourquoi : Détecter les arnaques nécessite de trouver des connexions indirectes (ex: un numéro de téléphone lié à 5 comptes qui vendent 20 voitures fantômes). Les requêtes de graphe trouvent ces "patterns" cycliques instantanément (impossible en SQL classique).

6. Frontend : React 18 + TypeScript
   - Pourquoi : L'interface demande beaucoup d'interactivité (Chatbot, filtres dynamiques, swipe de véhicules). React gère ces états complexes efficacement via son Virtual DOM, et TypeScript prévient les erreurs de typage avec l'API Backend."""

new_y = max_y + 80
new_text = create_text(detailed_text, 60, new_y, size=18, color="#1e1e1e", font_family=1)

# Create a prominent orange box for it
rect_id = str(uuid.uuid4())
rect = {
    "id": rect_id,
    "type": "rectangle",
    "x": 40,
    "y": new_y - 20,
    "width": 1050,
    "height": 700,
    "angle": 0,
    "strokeColor": "#d9480f", # Orange border
    "backgroundColor": "#fff4e6", # Light orange background
    "fillStyle": "solid",
    "strokeWidth": 2,
    "strokeStyle": "solid",
    "roughness": 1,
    "opacity": 100,
    "groupIds": [],
    "frameId": None,
    "roundness": {"type": 3},
    "seed": int(time.time() * 1000) % 1000000000,
    "versionNonce": int(time.time() * 1000) % 1000000000,
    "isDeleted": False,
    "boundElements": [{"id": new_text["id"], "type": "text"}],
    "updated": int(time.time() * 1000),
    "link": None,
    "locked": False,
    "version": 1,
    "index": None
}

new_text["containerId"] = rect_id
new_text["verticalAlign"] = "middle"

data["elements"].append(rect)
data["elements"].append(new_text)

with open(filepath, "w", encoding="utf-8") as f:
    json.dump(data, f, indent=2, ensure_ascii=False)

print("Tech choices details added.")
