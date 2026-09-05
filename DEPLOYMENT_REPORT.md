# Deployment Report for Wakala

## 1. Project Overview
- **Wakala** is a full-stack, AI-powered intelligent automotive marketplace and decision platform designed for the Moroccan automotive market.
- The platform enables buying, selling, and evaluating used and new vehicles with advanced AI features:
  - **Conversational RAG Chatbot:** Conversational assistant for automotive advisory, powered by LangChain, OpenRouter/Groq/OpenAI LLMs, and sentence embeddings.
  - **Hybrid AI Recommendation Engine:** Multi-criteria and vector similarity vehicle recommendations using Qdrant vector database and scikit-learn.
  - **Automated Price Valuation:** Vehicle pricing and market value estimation via XGBoost regression models and historical market data.
  - **Computer Vision Pipeline:** Damage assessment and vehicle image deduplication using Ultralytics YOLO models and ImageHash.
  - **Interactive 3D Visualizer:** Real-time 3D car viewer/configurator built using Three.js and React Three Fiber.
  - **Graph Relationships:** Similarity graphs, cluster detection, and vehicle connectivity modeled in Neo4j.
  - **Data Scraping & Medallion Pipeline:** Automated web scrapers (Avito, Moteur.ma) and data pipelines (Kafka, Spark, Airflow) structured in Bronze, Silver, and Gold data layers.

## 2. Detected Tech Stack
- **Frontend:** React 18.3.1 (TypeScript 5.5) + Vite 7.x (SPA with React Router DOM v7, TanStack Query, Framer Motion, Lucide Icons, and Three.js / React Three Fiber).
- **Backend:** Python 3.11 + FastAPI 0.115.0 (ASGI framework with Uvicorn, Pydantic v2, Pydantic-Settings, SlowAPI rate limiting, and FastAPI-Mail).
- **Database:**
  - **Relational:** PostgreSQL 16 (accessed via SQLAlchemy 2.0 ORM with `asyncpg` async driver and `psycopg2-binary` sync driver; compatible with Neon Serverless Postgres). In-memory SQLite (`aiosqlite`) fallback for local testing.
  - **Vector Store:** Qdrant 1.11.3 (vector similarity search for vehicle embeddings; local container or Qdrant Cloud).
  - **Graph Database:** Neo4j 5.25.0 (graph queries and similarity relationships via Cypher).
- **Cache/Queue:**
  - **Cache:** Redis 7.2-alpine (session state, rate limiting, and temporary cache).
  - **Event Streaming / Message Queue:** Apache Kafka (Confluent-Kafka 2.5.3 client, compatible with Aiven Cloud Kafka or local Kafka broker).
- **Hosting/Server Requirements:**
  - **Frontend:** Static Web Hosting / CDN (e.g., Vercel, Cloudflare Pages, Netlify, AWS S3 + CloudFront, or Nginx container). Requires Node.js >= 18 for build phase.
  - **Backend:** Persistent Linux Container / VM with Python 3.11 runtime, system libraries (`gcc`, `libpq-dev`, `ffmpeg`, `libgl1`, `libglib2.0-0`), and ASGI process manager (Uvicorn with 2-4 workers or Gunicorn).
  - **Databases/Services:** Managed PostgreSQL (or Neon), Managed Qdrant (or Qdrant Cloud), Redis instance, and optional Neo4j Aura / Kafka cluster.

## 3. Dependencies (Key packages)
- **Frontend (Production):**
  1. `react` & `react-dom` (v18.3.1) - Core UI library
  2. `vite` (v7.x) - High-speed build tool and dev server
  3. `three` & `@react-three/fiber`, `@react-three/drei` - 3D WebGL car configurator
  4. `@tanstack/react-query` (v5.101.2) - Server-state management and client-side caching
  5. `react-router-dom` (v7.18.3) - Client-side SPA routing
  6. `axios` (v1.7.7) - API communication client
  7. `framer-motion` (v11.5.0) - UI micro-interactions and transitions
  8. `lucide-react` (v0.441.0) - Modern iconography
  9. `react-hook-form` (v7.81.0) - Form validation and handling
- **Backend (Production):**
  1. `fastapi` (v0.115.0) & `uvicorn[standard]` (v0.30.6) - Async web framework and ASGI application server
  2. `pydantic` (v2.9.1) & `pydantic-settings` (v2.5.2) - Data validation and settings management
  3. `sqlalchemy` (v2.0.35), `asyncpg` (v0.31.0), `psycopg2-binary` (v2.9.12) - Relational ORM and database drivers
  4. `qdrant-client` (v1.11.3) & `sentence-transformers` (v3.1.1) - Vector embeddings and search
  5. `langchain` (v0.3.0) & `langchain-openai`, `langchain-groq` - RAG chatbot orchestration
  6. `scikit-learn`, `xgboost`, `pandas`, `numpy` - Machine learning, car pricing, and feature engineering
  7. `ultralytics` (v8.2.100), `imagehash`, `Pillow` - Computer vision damage inspection and image hashing
  8. `neo4j` (v5.25.0) - Neo4j graph database client
  9. `confluent-kafka` (v2.5.3) - High-throughput Kafka event streaming
  10. `python-jose[cryptography]`, `passlib[bcrypt]` - JWT authentication and password hashing

## 4. Build & Start Commands
- **Install dependencies:**
  - Frontend: `cd frontend && npm install` (or `npm ci`)
  - Backend: `cd backend && pip install -r requirements.txt`
- **Development server:**
  - Frontend: `cd frontend && npm run dev` (starts on port 3000)
  - Backend: `cd backend && uvicorn app.main:app --reload --port 8000`
  - Full Stack (Docker Compose Local): `docker compose up -d`
- **Production build:**
  - Frontend: `cd frontend && npm run build` (executes `tsc --noEmit && vite build`, outputs static assets to `frontend/dist`)
  - Backend: `docker build -t wakala-backend ./backend` (Python code does not require compilation, dependencies are installed into container image)
- **Production start:**
  - Frontend:
    - CDN / Static Host (e.g., Vercel, Netlify): Deploy `frontend/dist` directory directly with single-page rewrite rules (`/* -> /index.html`).
    - Nginx Container: `docker build -f Dockerfile.prod -t wakala-frontend ./frontend && docker run -p 80:80 wakala-frontend`
  - Backend:
    - Container / VM: `uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4`
    - Cloud Platforms (Render, Railway, Fly.io, Cloud Run): `uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}`
  - Full Stack (Docker Compose Production): `docker compose -f docker-compose.prod.yml up -d`

## 5. Environment Variables Required

### Frontend (`frontend/.env` / Cloud Provider Environment Settings)
- `VITE_API_URL` - Absolute backend API base URL (e.g., `https://api.wakala.ma/api` or `http://localhost:8000/api`).

### Backend Core & Security (`backend/.env`)
- `APP_NAME` - Application identifier (default: `Wakala`).
- `APP_ENV` - Environment mode (`development`, `staging`, `production`).
- `DEBUG` - Debug mode flag (`false` in production, `true` in development).
- `SECRET_KEY` - Cryptographic secret key used for signing JWT authentication tokens (minimum 32/64 hex characters).
- `JWT_ALGORITHM` - Algorithm for JWT verification (default: `HS256`).
- `ACCESS_TOKEN_EXPIRE_MINUTES` - Lifetime of JWT access tokens (default: `60`).
- `GOOGLE_CLIENT_ID` - Google OAuth 2.0 Client ID for social login.
- `CORS_ORIGINS` - JSON array of allowed frontend origins (e.g., `["https://wakala.vercel.app","https://wakala.ma"]`).
- `WEBHOOK_SECRET` - Shared secret for webhook signature verification.

### Backend Relational Database (PostgreSQL / Neon)
- `DATABASE_URL` - Full pooled PostgreSQL connection string for SQLAlchemy async (e.g., `postgresql+asyncpg://user:password@ep-xyz.neon.tech/wakala?sslmode=require`).
- *Legacy/Individual Parameters:*
  - `POSTGRES_HOST` - Database hostname / server endpoint.
  - `POSTGRES_PORT` - Database port (default: `5432`).
  - `POSTGRES_DB` - Target database name.
  - `POSTGRES_USER` - Database username.
  - `POSTGRES_PASSWORD` - Database user password.

### Backend Vector Store (Qdrant)
- `QDRANT_URL` - HTTPS connection URL for Qdrant Cloud cluster (e.g., `https://xxxx.qdrant.tech:6333`).
- `QDRANT_API_KEY` - Authentication key for Qdrant Cloud.
- `QDRANT_HOST` - Local Qdrant server hostname (default: `localhost` or `qdrant`).
- `QDRANT_PORT` - Local Qdrant REST port (default: `6333`).
- `QDRANT_COLLECTION` - Collection name for vehicle embeddings (default: `vehicle_embeddings`).

### Backend Graph Database (Neo4j)
- `NEO4J_URI` - Bolt connection URL (e.g., `neo4j+s://xxxx.databases.neo4j.io` or `bolt://localhost:7687`).
- `NEO4J_USER` - Neo4j username (default: `neo4j`).
- `NEO4J_PASSWORD` - Neo4j password.

### Backend Caching & Event Streaming
- `REDIS_URL` - Redis connection URL (e.g., `redis://redis:6379/0` or Upstash Redis URL).
- `KAFKA_BOOTSTRAP_SERVERS` - Comma-separated Kafka broker addresses (e.g., `aiven-kafka.aivencloud.com:port`).
- `KAFKA_USERNAME` / `KAFKA_API_KEY` - SASL username or access key.
- `KAFKA_PASSWORD` / `KAFKA_API_SECRET` - SASL password or secret.
- `KAFKA_SECURITY_PROTOCOL` - Kafka protocol (default: `SASL_SSL`).
- `KAFKA_SASL_MECHANISM` - Authentication mechanism (default: `SCRAM-SHA-256`).

### Backend AI / LLM / RAG / Voice Services
- `OPENROUTER_API_KEY` - API key for OpenRouter LLM Gateway.
- `OPENROUTER_BASE_URL` - Endpoint for OpenRouter (default: `https://openrouter.ai/api/v1`).
- `OPENROUTER_MODEL` - Selected primary model (default: `liquid/lfm-2.5-2.6b:free` or `openrouter/free`).
- `OPENAI_API_KEY` - Fallback OpenAI API key for GPT models.
- `GROQ_API_KEY` - Groq API key for low-latency Llama inference.
- `GROQ_MODEL` - Default Groq model (default: `llama-3.3-70b-versatile`).
- `EMBEDDING_MODEL` - Sentence transformer or embedding model identifier (e.g., `sentence-transformers/all-MiniLM-L6-v2` or `hash-1024`).
- `HF_TOKEN` / `HUGGINGFACE_API_KEY` - Hugging Face API token for models/tokenizers.
- `COHERE_API_KEY` - Cohere API key (reranking and embeddings).
- `ELEVENLABS_API_KEY` - ElevenLabs API key for AI voice generation.
- `TTS_VOICE_FR`, `TTS_VOICE_DARIJA`, `TTS_VOICE_AR`, `TTS_VOICE_EN` - Voice IDs for multi-language TTS.
- `VOICE_MAX_SECONDS` - Maximum voice recording duration limit (default: `90`).

### Backend Email (SMTP)
- `MAIL_SERVER` - SMTP host (default: `mailhog` locally or e.g., `smtp.sendgrid.net`, `smtp.resend.com`).
- `MAIL_PORT` - SMTP port (e.g., `1025` for MailHog, `587` for TLS).
- `MAIL_USERNAME` - SMTP username.
- `MAIL_PASSWORD` - SMTP password.
- `MAIL_FROM` - Sender email address (default: `noreply@wakala.ma`).
- `MAIL_STARTTLS` - Enable STARTTLS (`true` / `false`).
- `MAIL_SSL_TLS` - Enable SSL/TLS (`true` / `false`).
- `USE_CREDENTIALS` - Authentication requirement flag (`true` / `false`).

## 6. Static vs Dynamic Classification
- **Hybrid Decoupled Application Architecture**:
  - **Frontend:** **Static Site (Single Page Application)**.
    - Compiles entirely into static assets (`index.html`, JavaScript bundles, CSS stylesheets, 3D glTF/GLB models, and optimized images).
    - Can and should be deployed to a high-performance global Content Delivery Network (CDN) such as Vercel, Cloudflare Pages, Netlify, or AWS CloudFront/S3.
    - Requires SPA rewrite rules (all route paths `/*` rewrite to `/index.html`) to support client-side routing via React Router DOM.
  - **Backend:** **Dynamic Application (Active Server Required 24/7)**.
    - Requires an active, persistent Python 3.11 ASGI server running continuously to handle API traffic, real-time database transactions, JWT authentication checks, and rate-limiting.
    - Executes heavy on-demand computations, including RAG embeddings, Qdrant vector similarity queries, ML price regressions (XGBoost), YOLO image damage inference, and external LLM/voice API calls.
    - Requires persistent connections to PostgreSQL, Qdrant, Redis, and Kafka. Cannot be hosted purely on serverless static edge functions without continuous connection pooling.

## 7. Database Setup
- **PostgreSQL Database Migrations & Schemas:**
  - **Raw SQL Migration Scripts (Active Migration Path):** A comprehensive sequence of 24 versioned SQL migration files is located in `database/postgres/migrations/` (from `001_create_users.sql` up to `023_add_detailed_vehicle_specs.sql`). These are executed automatically on first container init via Docker entrypoint (`/docker-entrypoint-initdb.d`).
  - **Post-Launch Migrations (#25 onward):** Documented in `database/postgres/MIGRATIONS.md`. Since `/docker-entrypoint-initdb.d` runs only once on initial volume creation, subsequent migrations are applied via `docker exec` / `psql`.
  - **Alembic ORM Migrations:** Alembic configuration at `database/postgres/alembic.ini` is currently an unconfigured scaffold (`target_metadata = None`) and is not executed by the production pipeline.
  - **Database Seeding:**
    - SQL Seed: `database/postgres/seed.sql` (test seller and sample vehicles).
    - Digital Showroom Catalog: `docker compose -f docker-compose.prod.yml exec backend python scripts/seed_morocco_new_cars.py` (run once post-boot, completely idempotent).
    - Excel Importer: `python backend/scripts/import_excel_catalogue.py` (offline batch utility).
- **Neo4j Graph Database Setup:**
  - Cypher setup scripts located in `database/neo4j/cypher_scripts/`:
    - `001_constraints_indexes.cypher` (creates unique constraints and search indexes)
    - `002_create_vehicle_nodes.cypher` (generates vehicle nodes)
    - `003_create_relationships.cypher` (builds brand, segment, price tier, and similarity relationships)
    - `004_pagerank_setup.cypher` (configures PageRank algorithm for node importance scoring)
- **Vector Store (Qdrant) Setup:**
  - Collection initialization script: `python database/vector-store/init_scripts/001_init_collection.py`
  - Sets up the `vehicle_embeddings` collection with Cosine distance metric for semantic vehicle matching.

## 8. Estimated Resource Requirements
- **RAM:**
  - **Frontend:** Negligible at runtime (< 128 MB on CDN edge). Build process requires ~1 GB to 2 GB during `npm run build` (TypeScript check and Vite bundle compilation).
  - **Backend API:** **> 2 GB to 4 GB RAM**.
    - *Rationale:* Running `sentence-transformers`, `torch` (CPU), `ultralytics` (YOLO computer vision), `xgboost`, and `whisper` in addition to 2-4 Uvicorn ASGI workers requires a minimum of 2 GB RAM. For sustained production traffic with concurrent ML inference, 4 GB RAM is strongly recommended.
  - **Databases (if self-hosted):**
    - PostgreSQL: > 1 GB to 2 GB RAM.
    - Qdrant: > 512 MB to 1 GB RAM.
    - Redis: > 256 MB RAM.
    - Neo4j: > 1 GB to 2 GB RAM.
  - **Cloud Architecture Recommendation:** Offload database engines to managed serverless/cloud tiers (Neon Serverless Postgres [0.5-1 CU auto-scale], Qdrant Cloud [Free/Starter tier], Upstash Redis) to keep backend container footprint down to a clean 2 GB container on Render / Fly.io / AWS ECS / Google Cloud Run.
- **Storage:**
  - **Frontend:** ~200 MB – 500 MB (includes 3D GLB vehicle models, textures, and compiled JavaScript/CSS bundles).
  - **Backend Container Image:** ~1.8 GB – 2.5 GB (Python 3.11 base image, PyTorch CPU, Ultralytics, OpenCV/FFmpeg system libraries, Scikit-learn, and model cache).
  - **Database & Asset Storage:** 10 GB – 50 GB SSD.
    - PostgreSQL & Qdrant vectors: ~5 GB – 10 GB initial.
    - Uploaded Vehicle Images: Should be stored in an S3-compatible object storage bucket (e.g., Cloudflare R2 or AWS S3) rather than persistent local container disks.
- **CPU:**
  - **Medium to High**:
    - **Medium (Baseline):** Idle and general REST API routing, JWT validation, and database queries consume minimal CPU (< 0.5 vCPU).
    - **High (Burst / Workload):** AI inference tasks (YOLO damage detection, sentence transformer embedding calculations, XGBoost model training/predictions, and audio transcription) generate intensive CPU spikes unless offloaded to dedicated GPU worker queues or remote cloud inference APIs. Recommended minimum: 2 vCPU cores for production backend.
