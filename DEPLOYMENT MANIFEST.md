# DEPLOYMENT MANIFEST

Guide de déploiement personnalisé pour **Wakala** : FastAPI + React/Vite, Neon PostgreSQL, Qdrant Cloud, OpenRouter, Render et Vercel.

> Périmètre de ce déploiement de test : pas de Kafka, Neo4j, scrapers, Redis, Mailhog, PostgreSQL local ni Qdrant local.

## 1. Architecture cible

```
Vercel (React/Vite SPA)
        |
        | HTTPS / VITE_API_URL
        v
Render Web Service (FastAPI)
        |-- Neon PostgreSQL
        |-- Qdrant Cloud
        `-- OpenRouter API
```

Déployer uniquement le frontend sur Vercel et le backend sur Render. Ne pas déployer les services de `docker-compose.yml` pour ce test.

## 2. Structure du dépôt

Racine absolue :

```text
D:\\Projet automobile\\vente-auto-platform
```

| Élément | Chemin absolu | Détail |
|---|---|---|
| Backend requirements | `D:\\Projet automobile\\vente-auto-platform\\backend\\requirements.txt` | Dépendances Python de production |
| Backend FastAPI | `D:\\Projet automobile\\vente-auto-platform\\backend\\app\\main.py` | Objet ASGI : `app` |
| Backend Dockerfile | `D:\\Projet automobile\\vente-auto-platform\\backend\\Dockerfile` | Image Python 3.11 ; le `--reload` doit être retiré en production |
| Frontend package | `D:\\Projet automobile\\vente-auto-platform\\frontend\\package.json` | Scripts React/Vite |
| Vite config | `D:\\Projet automobile\\vente-auto-platform\\frontend\\vite.config.ts` | Port local 3000 et proxy `/api` |
| Frontend output | `D:\\Projet automobile\\vente-auto-platform\\frontend\\dist` | Généré par Vite |
| Frontend production Dockerfile | `D:\\Projet automobile\\vente-auto-platform\\frontend\\Dockerfile.prod` | Build Node 20 puis Nginx |
| Compose local | `D:\\Projet automobile\\vente-auto-platform\\docker-compose.yml` | Stack locale complète |
| Compose production | `D:\\Projet automobile\\vente-auto-platform\\docker-compose.prod.yml` | Design Docker auto-hébergé, non utilisé ici |
| render.yaml | Absent | Configuration Render à saisir dans l’interface |
| vercel.json | Absent | Ajouter seulement si les deep links renvoient 404 |

Commandes vérifiées :

```bash
# Frontend
cd frontend
npm ci
npm run build
# npm run build = tsc -b && vite build, sortie : frontend/dist

# Backend
cd backend
uvicorn app.main:app --host 0.0.0.0 --port "$PORT"
```

## 3. Variables d’environnement

### 3.1 Backend

Les variables sont déclarées dans `backend/app/core/config.py`. Les secrets vont uniquement dans Render.

| Variable | Statut | Fonction / emplacement | Valeur Render |
|---|---|---|---|
| `APP_NAME` | optionnelle | Nom applicatif, `core/config.py` | `Wakala` |
| `APP_ENV` | requise | Mode de l’application et exposition de la documentation, `config.py`/ `main.py` | `production` |
| `DEBUG` | requise | Logs SQL et debug | `false` |
| `SECRET_KEY` | requise | Signature des JWT | `openssl rand -hex 32` |
| `JWT_ALGORITHM` | optionnelle | Algorithme JWT | `HS256` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | optionnelle | Durée d’une session JWT | `60` |
| `CORS_ORIGINS` | requise | Origines web autorisées, `app/main.py` | `["https://YOUR-APP.vercel.app"]` |
| `DATABASE_URL` | requise après adapter | URL Neon pour SQLAlchemy async | URL pooled copiée dans Neon Connect |
| `POSTGRES_HOST` | legacy | Ancien mode PostgreSQL séparé, `config.py` | Ne pas utiliser avec Neon si adapter appliqué |
| `POSTGRES_PORT` | legacy | Ancien port PostgreSQL | Généralement `5432` |
| `POSTGRES_DB` | legacy | Ancien nom de base | Nom fourni par Neon |
| `POSTGRES_USER` | legacy | Ancien utilisateur | Utilisateur fourni par Neon |
| `POSTGRES_PASSWORD` | legacy | Ancien mot de passe | Mot de passe fourni par Neon |
| `QDRANT_URL` | requise après adapter | URL HTTPS Qdrant Cloud | URL du cluster Qdrant |
| `QDRANT_API_KEY` | requise après adapter | Authentification Qdrant Cloud | API key Qdrant |
| `QDRANT_COLLECTION` | requise | Collection vectorielle | `vehicle_embeddings` |
| `OPENROUTER_API_KEY` | requise chatbot | Authentification LLM | Clé créée dans OpenRouter |
| `OPENROUTER_BASE_URL` | requise | Endpoint LLM | `https://openrouter.ai/api/v1` |
| `OPENROUTER_MODEL` | optionnelle | Modèle primaire/compatibilité LangChain | `nvidia/nemotron-3.5-lightning:free` |
| `OPENROUTER_MODELS` | optionnelle | Liste native de fallback | Liste de la Section 7 |
| `EMBEDDING_MODEL` | optionnelle | Étiquette de l’embedder local déterministe | `hash-1024` |
| `GOOGLE_CLIENT_ID` | optionnelle | Google Sign-In | Laisser vide si désactivé |
| `WEBHOOK_SECRET` | conditionnelle | Signature des webhooks transactions | Secret aléatoire séparé |
| `ELEVENLABS_API_KEY` | conditionnelle | Synthèse vocale serveur | Clé ElevenLabs ou vide |
| `TTS_VOICE_FR`, `TTS_VOICE_DARIJA`, `TTS_VOICE_AR`, `TTS_VOICE_EN` | conditionnelles | IDs de voix | IDs ElevenLabs ou vides |
| `VOICE_MAX_SECONDS` | optionnelle | Limite voice input | `90` |

Variables présentes mais inutiles pour le test sans Kafka/Neo4j/scrapers : `NEO4J_URI`, `NEO4J_USER`, `NEO4J_PASSWORD`, `KAFKA_BOOTSTRAP_SERVERS`, `GROQ_API_KEY`, `GROQ_MODEL`, `OPENAI_API_KEY`, `LLM_MODEL`, `HF_TOKEN`, `HUGGINGFACE_API_KEY`, `COHERE_API_KEY`, ainsi que les variables SMTP.

Attention : `NEO4J_PASSWORD` est actuellement déclaré obligatoire et `backend/app/core/neo4j_client.py` instancie un client à l’import. Pour un backend totalement indépendant de Neo4j, rendre ce champ optionnel et charger le client uniquement dans les routes graphe. Ne pas démarrer Neo4j dans le déploiement de test.

### 3.2 Frontend

| Variable | Fonction | Emplacement | Valeur |
|---|---|---|---|
| `VITE_API_URL` | Base URL FastAPI pour Axios, chatbot, voice et maintenance | `frontend/src/services/api.ts` et services associés | `https://YOUR-RENDER-SERVICE.onrender.com/api` |

Les variables `VITE_*` sont embarquées dans le JavaScript public. Ne jamais y placer une clé OpenRouter, Qdrant, Neon, JWT ou SMTP.

### 3.3 OPENAI_API_BASE

`OPENAI_API_BASE` n’est pas lu par le dépôt actuel. La variable réellement utilisée est :

```text
OPENROUTER_BASE_URL=https://openrouter.ai/api/v1
```

Si un script externe exige le nom `OPENAI_API_BASE`, lui donner aussi cette valeur, mais cela ne changera rien dans l’application tant qu’il ne la lit pas.

## 4. Préparer les services cloud

### Neon.tech

1. Créer un projet Neon.
2. Ouvrir **Connect**.
3. Choisir la connexion pooled pour un service web.
4. Copier la chaîne et la mettre dans Render sous `DATABASE_URL`.
5. Conserver `sslmode=require`.

Format source courant :

```text
postgresql://USER:PASSWORD@HOST/DB?sslmode=require
```

Pour asyncpg, le schéma doit devenir :

```text
postgresql+asyncpg://USER:PASSWORD@HOST/DB?sslmode=require
```

La chaîne contient le mot de passe : ne pas la committer.

### Qdrant Cloud

1. Créer un cluster.
2. Copier son URL HTTPS.
3. Créer une API key avec accès à la collection.
4. Mettre l’URL dans `QDRANT_URL` et la clé dans `QDRANT_API_KEY`.
5. Utiliser `QDRANT_COLLECTION=vehicle_embeddings`.

Le lifespan FastAPI teste Qdrant au démarrage : une URL ou clé erronée empêche le service d’être sain.

### OpenRouter

1. Créer un compte OpenRouter.
2. Créer une API key.
3. Ajouter la clé à Render sous `OPENROUTER_API_KEY`.
4. Utiliser `OPENROUTER_BASE_URL=https://openrouter.ai/api/v1`.
5. Garder la liste de modèles de fallback indiquée ci-dessous.

## 5. Déploiement Render

Créer un **Web Service** depuis le dépôt.

| Champ Render | Valeur exacte |
|---|---|
| Root Directory | `backend` |
| Runtime | `Python 3` |
| Build Command | `pip install --upgrade pip && pip install -r requirements.txt` |
| Start Command | `uvicorn app.main:app --host 0.0.0.0 --port $PORT` |
| Health Check Path | `/health` |

Ne pas utiliser Docker Compose, le scraper, ou un script de seed comme commande de démarrage Render.

Après déploiement :

```bash
curl -i https://YOUR-RENDER-SERVICE.onrender.com/health
curl -i "https://YOUR-RENDER-SERVICE.onrender.com/api/vehicles/?page=1&page_size=1"
```

Le endpoint `/docs` est disponible seulement en développement puisque `APP_ENV=production` désactive la documentation.

## 6. Déploiement Vercel

Importer le dépôt dans Vercel et configurer :

| Champ Vercel | Valeur exacte |
|---|---|
| Root Directory | `frontend` |
| Framework | Vite ou Other |
| Install Command | `npm ci` |
| Build Command | `npm run build` |
| Output Directory | `dist` |

Variable Vercel :

```text
VITE_API_URL=https://YOUR-RENDER-SERVICE.onrender.com/api
```

Après chaque modification de `VITE_API_URL`, redéployer. Pour les routes directes comme `/catalogue` ou `/vehicule/...`, si Vercel répond 404, créer `frontend/vercel.json` :

```json
{
  "rewrites": [{ "source": "/(.*)", "destination": "/index.html" }]
}
```

## 7. Diff OpenRouter avec fallback natif

### Configuration

Dans `backend/app/core/config.py` :

```diff
-    OPENROUTER_MODEL: str = "nvidia/nemotron-3.5-lightning:free"
+    OPENROUTER_MODEL: str = "nvidia/nemotron-3.5-lightning:free"
+    OPENROUTER_MODELS: list[str] = [
+        "nvidia/nemotron-3.5-lightning:free",
+        "google/gemma-4-31b-it:free",
+        "openrouter/free",
+    ]
```

### Appel direct chatbot

Dans `backend/app/services/ai/chat.py`, le payload doit envoyer `models`, pas un seul modèle :

```diff
 payload = {
-    "model": settings.OPENROUTER_MODEL,
+    "models": settings.OPENROUTER_MODELS,
     "messages": messages_payload,
     "stream": True,
     "temperature": 0.2,
     "max_tokens": 360,
 }
```

Dans `backend/app/rag/chatbot_chain.py` :

```diff
 payload_data = {
-    "model": settings.OPENROUTER_MODEL,
+    "models": settings.OPENROUTER_MODELS,
     "messages": raw_payload,
     "temperature": 0.3,
     "max_tokens": 300,
 }
```

### Appels LangChain

Les appels `ChatOpenAI` conservés pour les sorties structurées doivent garder leur argument primaire compatible, et ajouter :

```python
model=settings.OPENROUTER_MODEL,
extra_body={"models": settings.OPENROUTER_MODELS},
```

Le dépôt actuel transmet déjà cette liste dans `chat.py`, `chatbot_chain.py`, `compare_chain.py`, `customs_chain.py` et `hybrid_parser.py`.

## 8. Adapter Neon et Qdrant avant le premier déploiement cloud

### PostgreSQL

Le code actuel expose une propriété calculée `DATABASE_URL`. Pour accepter Neon :

```diff
 class Settings(BaseSettings):
+    DATABASE_URL: str | None = None
     POSTGRES_HOST: str = "localhost"
     POSTGRES_PORT: int = 5432
     POSTGRES_DB: str = "Wakala"
     POSTGRES_USER: str = "Wakala_user"
-    POSTGRES_PASSWORD: str
+    POSTGRES_PASSWORD: str = ""

-    @property
-    def DATABASE_URL(self) -> str:
+    @property
+    def database_url(self) -> str:
+        if self.DATABASE_URL:
+            return self.DATABASE_URL.replace(
+                "postgresql://", "postgresql+asyncpg://", 1
+            )
         return (
             f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
             f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
         )
```

Dans `backend/app/core/database.py` :

```diff
-        settings.DATABASE_URL,
+        settings.database_url,
```

Adapter aussi `DATABASE_URL_SYNC` si Alembic ou les scripts synchrones utilisent Neon.

### Qdrant

Dans `backend/app/core/config.py` :

```diff
 QDRANT_HOST: str = "localhost"
 QDRANT_PORT: int = 6333
+QDRANT_URL: str | None = None
+QDRANT_API_KEY: str | None = None
```

Dans `backend/app/services/ai/qdrant.py`, remplacer le constructeur par :

```python
qdrant_client = (
    AsyncQdrantClient(
        url=settings.QDRANT_URL,
        api_key=settings.QDRANT_API_KEY,
    )
    if settings.QDRANT_URL
    else AsyncQdrantClient(
        host=settings.QDRANT_HOST,
        port=settings.QDRANT_PORT,
    )
) if QDRANT_AVAILABLE else None
```

Appliquer le même choix URL/API key à `backend/app/core/qdrant_client.py` et `backend/app/rag/vector_store.py`, qui utilisent encore actuellement `host/port` locaux.

## 9. Suppression Ollama

La recherche effectuée sur le dépôt ne trouve plus de référence `ollama` ou `qwen`. Les éléments retirés sont :

- service et volume Ollama de `docker-compose.yml` ;
- variables Ollama des fichiers `.env` ;
- imports/clients Ollama et fallback local ;
- ancien normalizer et test Ollama du data pipeline ;
- références historiques dans la documentation et les diagrammes.

Contrôle à exécuter :

```bash
rg -n -i "\\bollama\\b|qwen|OLLAMA_HOST|OLLAMA_MODEL|OLLAMA_BASE_URL" . \
  -g '!**/.git/**' \
  -g '!**/node_modules/**' \
  -g '!**/__pycache__/**' \
  -g '!**/dist/**'
```

Résultat attendu : aucune ligne.

## 10. Smoke tests

### Backend

```bash
curl -i https://YOUR-RENDER-SERVICE.onrender.com/health
curl -i "https://YOUR-RENDER-SERVICE.onrender.com/api/vehicles/?page=1&page_size=1"
```

Réponse health attendue :

```json
{"status":"healthy","service":"Wakala-backend","version":"0.1.0"}
```

### Frontend

1. Ouvrir l’URL Vercel.
2. DevTools → Console : aucune exception runtime.
3. DevTools → Network : les requêtes doivent cibler Render, jamais localhost.
4. Vérifier que `/api/vehicles/` renvoie 2xx.
5. Tester le catalogue puis le chatbot.
6. Une erreur CORS signifie que l’origine Vercel manque dans `CORS_ORIGINS`.

## 11. Script de préparation local

```bash
set -euo pipefail

cd backend
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m compileall -q app

cd ../frontend
npm ci
npm run type-check
npm run build

cd ..
if rg -n -i "\\bollama\\b|qwen|OLLAMA_HOST|OLLAMA_MODEL|OLLAMA_BASE_URL" . \
  -g '!**/.git/**' -g '!**/node_modules/**' -g '!**/__pycache__/**' -g '!**/dist/**'; then
  echo "Old local-LLM references found" >&2
  exit 1
fi
```

## 12. Tableau final

| Service | Plateforme | URL / chaîne | Identifiants admin |
|---|---|---|---|
| Frontend | Vercel | `https://YOUR-PROJECT.vercel.app` | Compte Vercel |
| Backend | Render | `https://YOUR-SERVICE.onrender.com` | Compte Render ; auth applicative JWT |
| PostgreSQL | Neon.tech | `DATABASE_URL` depuis Neon Connect | User/password dans l’URL secrète |
| Vector DB | Qdrant Cloud | `QDRANT_URL` + `QDRANT_API_KEY` | API key Qdrant |
| LLM | OpenRouter | `https://openrouter.ai/api/v1` | API key OpenRouter |
