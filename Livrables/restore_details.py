

import json
import uuid
import time

filepath = "D:/Projet automobile/vente-auto-platform/Livrables/wakala_architecture_complete_technique.excalidraw"

with open(filepath, "r", encoding="utf-8") as f:
    data = json.load(f)

# 1. Remove the elements I added in the previous "rebuild" step
# They contain specific keywords like "Scraping & Ingestion : Scrapers (Python"
keywords_to_remove = [
    "PARTIE ADDITIONNELLE — Flux des données",
    "Flux des données (Data Ingress",
    "1. Scraping & Ingestion",
    "2. ETL & Transformation",
    "3. Stockage : Données",
    "4. Recherche : L'utilisateur",
    "Moteur de Matching (Fonctionnement",
    "1. Création : Modèle Python",
    "2. Embeddings : Requête",
    "3. Similarité : Calcul de la",
    "4. Classement : Score combinant",
]

elements_to_keep = []
for el in data["elements"]:
    is_mine = False
    if el["type"] == "text":
        text_content = el.get("text", "")
        for kw in keywords_to_remove:
            if text_content.startswith(kw) or text_content == kw:
                is_mine = True
                break
    if not is_mine:
        elements_to_keep.append(el)

data["elements"] = elements_to_keep

# 2. Find max Y to append below
max_y = 0
for el in data["elements"]:
    y = el.get("y", 0)
    h = el.get("height", 0)
    if y + h > max_y:
        max_y = y + h

def create_text(text, x, y, size=16, color="#000000", font_family=1):
    # To avoid excalidraw bugs, we just don't set a containerId
    # and provide a generous width calculation so it doesn't squish.
    lines = text.split('\n')
    max_line_len = max([len(line) for line in lines]) if lines else len(text)
    
    return {
        "id": str(uuid.uuid4()),
        "type": "text",
        "x": x,
        "y": y,
        "width": max_line_len * (size * 0.6), # rough width estimation
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


detailed_text = """PARTIE ADDITIONNELLE — Détails du Flux des données & Moteur de Matching

Flux des données (Data Ingress & Egress):
1. Scraping & Ingestion:
   - Des scrapers (Python/BeautifulSoup/Playwright) collectent les annonces sur des sites tiers.
   - Les données brutes (HTML/JSON) sont extraites.
2. Nettoyage & Transformation (ETL):
   - Extraction des attributs clés (marque, modèle, année, prix, kilométrage).
   - Standardisation (ex: '20 000 km' -> 20000).
   - Les photos sont analysées (Photo Analyzer ML) pour vérifier l'état et repérer les dommages.
   - Évaluation de confiance (Trust Engine) : détection de patterns vendeurs (arnaques potentielles).
3. Stockage (Database):
   - Données structurées stockées dans une base (PostgreSQL / MongoDB).
   - Indexation via ElasticSearch ou un Vector DB (Qdrant/Milvus) pour la recherche de similarité rapide.
4. Flux Utilisateur (Recherche):
   - L'utilisateur entre un prompt ("Je veux une berline pas chère").
   - Requête -> API FastAPI -> Pipeline NLP (LLM/Spacy) -> Extraction d'entités (budget, type).

Moteur de Matching (Fonctionnement & Création):
1. Création (Architecture):
   - Développé en Python (via Scikit-learn / PyTorch).
   - Il crée un 'Persona' ou profil idéal du véhicule basé sur l'input NLP.
2. Embeddings & Vecteurs:
   - Les caractéristiques du véhicule et la requête de l'utilisateur sont transformées en vecteurs mathématiques.
3. Similarité Cosinus / Score:
   - Le moteur calcule la distance (similarité cosinus) entre la requête (ex: budget 10k, familial)
     et le catalogue de voitures indexées dans la Vector DB.
4. Classement (Ranking):
   - Les véhicules avec le score le plus élevé (les plus proches du vecteur utilisateur) remontent en premier.
   - Le score est ensuite ajusté selon le "Trust Score" (fiabilité du vendeur/voiture)."""

new_y = max_y + 80
data["elements"].append(create_text(detailed_text, 60, new_y, size=18, color="#1e1e1e", font_family=1))

with open(filepath, "w", encoding="utf-8") as f:
    json.dump(data, f, indent=2, ensure_ascii=False)

print("Excalidraw updated with detailed text.")
