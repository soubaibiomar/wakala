#!/usr/bin/env bash
# ═══════════════════════════════════════════════════════════════
# AutoMind — Script d'installation complet (Linux / macOS)
#
# Usage :
#   chmod +x setup.sh
#   ./setup.sh              # Installation complète
#   ./setup.sh --skip-docker # Sans démarrer les conteneurs Docker
#   ./setup.sh --dev         # Inclure les dépendances de dev
#
# Ce script est idempotent : il peut être relancé sans casser
# une installation existante.
# ═══════════════════════════════════════════════════════════════

set -euo pipefail

# ─── Couleurs ──────────────────────────────────────────────────
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m' # No Color

# ─── Arguments ─────────────────────────────────────────────────
SKIP_DOCKER=false
INSTALL_DEV=false
for arg in "$@"; do
    case $arg in
        --skip-docker) SKIP_DOCKER=true ;;
        --dev)         INSTALL_DEV=true ;;
        --help|-h)
            echo "Usage: ./setup.sh [--skip-docker] [--dev]"
            echo "  --skip-docker  Ne pas démarrer les conteneurs Docker"
            echo "  --dev          Installer les dépendances de développement"
            exit 0 ;;
    esac
done

# ─── Header ───────────────────────────────────────────────────
echo ""
echo -e "${CYAN}${BOLD}═══════════════════════════════════════════════════════${NC}"
echo -e "${CYAN}${BOLD}  🚗 AutoMind — Installation de la plateforme${NC}"
echo -e "${CYAN}${BOLD}═══════════════════════════════════════════════════════${NC}"
echo ""

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_ROOT"


# ═══════════════════════════════════════════════════════════════
# Étape 1 : Vérification des prérequis système
# ═══════════════════════════════════════════════════════════════

echo -e "${BLUE}${BOLD}[1/6] Vérification des prérequis système...${NC}"
echo ""

MISSING=()

# Node.js ≥ 18
if command -v node &> /dev/null; then
    NODE_VER=$(node -v | sed 's/v//' | cut -d. -f1)
    if [ "$NODE_VER" -ge 18 ]; then
        echo -e "  ${GREEN}✓${NC} Node.js $(node -v)"
    else
        echo -e "  ${RED}✗${NC} Node.js $(node -v) — version 18+ requise"
        MISSING+=("Node.js 18+")
    fi
else
    echo -e "  ${RED}✗${NC} Node.js non trouvé"
    MISSING+=("Node.js 18+ (https://nodejs.org)")
fi

# npm
if command -v npm &> /dev/null; then
    echo -e "  ${GREEN}✓${NC} npm $(npm -v)"
else
    echo -e "  ${RED}✗${NC} npm non trouvé"
    MISSING+=("npm")
fi

# Python ≥ 3.11
if command -v python3 &> /dev/null; then
    PY_VER=$(python3 -c "import sys; print(f'{sys.version_info.minor}')")
    PY_FULL=$(python3 --version)
    if [ "$PY_VER" -ge 11 ]; then
        echo -e "  ${GREEN}✓${NC} $PY_FULL"
    else
        echo -e "  ${RED}✗${NC} $PY_FULL — version 3.11+ requise"
        MISSING+=("Python 3.11+")
    fi
else
    echo -e "  ${RED}✗${NC} Python3 non trouvé"
    MISSING+=("Python 3.11+ (https://python.org)")
fi

# pip
if command -v pip3 &> /dev/null || python3 -m pip --version &> /dev/null; then
    echo -e "  ${GREEN}✓${NC} pip $(python3 -m pip --version 2>/dev/null | cut -d' ' -f2)"
else
    echo -e "  ${RED}✗${NC} pip non trouvé"
    MISSING+=("pip")
fi

# Docker
if command -v docker &> /dev/null; then
    echo -e "  ${GREEN}✓${NC} Docker $(docker --version | cut -d' ' -f3 | tr -d ',')"
else
    echo -e "  ${YELLOW}⚠${NC} Docker non trouvé (nécessaire pour les services d'infrastructure)"
    if [ "$SKIP_DOCKER" = false ]; then
        MISSING+=("Docker (https://docs.docker.com/get-docker/)")
    fi
fi

# Docker Compose
if docker compose version &> /dev/null 2>&1; then
    echo -e "  ${GREEN}✓${NC} Docker Compose $(docker compose version --short 2>/dev/null)"
elif command -v docker-compose &> /dev/null; then
    echo -e "  ${GREEN}✓${NC} docker-compose $(docker-compose --version | cut -d' ' -f4 | tr -d ',')"
else
    echo -e "  ${YELLOW}⚠${NC} Docker Compose non trouvé"
    if [ "$SKIP_DOCKER" = false ]; then
        MISSING+=("Docker Compose v2+")
    fi
fi

echo ""

if [ ${#MISSING[@]} -gt 0 ]; then
    echo -e "${RED}${BOLD}Prérequis manquants :${NC}"
    for item in "${MISSING[@]}"; do
        echo -e "  ${RED}•${NC} $item"
    done
    echo ""
    echo -e "${RED}Installez les prérequis ci-dessus puis relancez ./setup.sh${NC}"
    exit 1
fi

echo -e "  ${GREEN}${BOLD}Tous les prérequis sont satisfaits ✓${NC}"
echo ""


# ═══════════════════════════════════════════════════════════════
# Étape 2 : Installation des dépendances Frontend
# ═══════════════════════════════════════════════════════════════

echo -e "${BLUE}${BOLD}[2/6] Installation des dépendances Frontend (npm)...${NC}"
echo ""

cd "$PROJECT_ROOT/frontend"

if [ -d "node_modules" ]; then
    echo -e "  ${YELLOW}→${NC} node_modules existe déjà, mise à jour..."
    npm install --silent 2>&1 | tail -1
else
    npm install 2>&1 | tail -5
fi

echo -e "  ${GREEN}✓${NC} Frontend — $(ls node_modules | wc -l | tr -d ' ') packages installés"
echo ""

cd "$PROJECT_ROOT"


# ═══════════════════════════════════════════════════════════════
# Étape 3 : Environnement virtuel Python + Backend
# ═══════════════════════════════════════════════════════════════

echo -e "${BLUE}${BOLD}[3/6] Installation des dépendances Python...${NC}"
echo ""

VENV_DIR="$PROJECT_ROOT/.venv"

# Créer le venv s'il n'existe pas
if [ ! -d "$VENV_DIR" ]; then
    echo -e "  ${YELLOW}→${NC} Création de l'environnement virtuel (.venv)..."
    python3 -m venv "$VENV_DIR"
fi

# Activer le venv
source "$VENV_DIR/bin/activate"

# Mise à jour pip
echo -e "  ${YELLOW}→${NC} Mise à jour de pip..."
pip install --upgrade pip --quiet

# Backend
echo -e "  ${YELLOW}→${NC} Installation des dépendances backend..."
pip install -r "$PROJECT_ROOT/backend/requirements.txt" --quiet 2>&1

if [ "$INSTALL_DEV" = true ]; then
    echo -e "  ${YELLOW}→${NC} Installation des dépendances dev..."
    pip install -r "$PROJECT_ROOT/backend/requirements-dev.txt" --quiet 2>&1
fi

# Data pipeline
echo -e "  ${YELLOW}→${NC} Installation des dépendances data-pipeline..."
pip install -r "$PROJECT_ROOT/data-pipeline/requirements.txt" --quiet 2>&1

# Analytics
echo -e "  ${YELLOW}→${NC} Installation des dépendances analytics..."
pip install -r "$PROJECT_ROOT/analytics/requirements.txt" --quiet 2>&1

INSTALLED=$(pip list --format=columns 2>/dev/null | wc -l)
echo -e "  ${GREEN}✓${NC} Python — $INSTALLED packages installés dans .venv"
echo ""


# ═══════════════════════════════════════════════════════════════
# Étape 4 : Configuration .env
# ═══════════════════════════════════════════════════════════════

echo -e "${BLUE}${BOLD}[4/6] Configuration de l'environnement (.env)...${NC}"
echo ""

if [ ! -f "$PROJECT_ROOT/.env" ]; then
    cp "$PROJECT_ROOT/.env.example" "$PROJECT_ROOT/.env"
    echo -e "  ${GREEN}✓${NC} .env créé à partir de .env.example"
    echo -e "  ${YELLOW}⚠${NC}  Pensez à personnaliser les valeurs (SECRET_KEY, OPENAI_API_KEY...)"
else
    echo -e "  ${GREEN}✓${NC} .env existe déjà — aucune modification"
fi

echo ""


# ═══════════════════════════════════════════════════════════════
# Étape 5 : Docker Compose (services d'infrastructure)
# ═══════════════════════════════════════════════════════════════

echo -e "${BLUE}${BOLD}[5/6] Services d'infrastructure (Docker Compose)...${NC}"
echo ""

if [ "$SKIP_DOCKER" = true ]; then
    echo -e "  ${YELLOW}⏭${NC}  Docker ignoré (--skip-docker)"
else
    cd "$PROJECT_ROOT"

    # Démarrer les services d'infrastructure uniquement
    echo -e "  ${YELLOW}→${NC} Démarrage : PostgreSQL, Neo4j, Qdrant, Kafka, Zookeeper..."
    docker compose up -d postgres neo4j qdrant zookeeper kafka 2>&1 | tail -10

    # Attendre que PostgreSQL soit prêt
    echo -e "  ${YELLOW}→${NC} Attente de PostgreSQL..."
    RETRIES=0
    until docker compose exec -T postgres pg_isready -U automind_user -d automind > /dev/null 2>&1; do
        RETRIES=$((RETRIES+1))
        if [ $RETRIES -gt 30 ]; then
            echo -e "  ${RED}✗${NC} PostgreSQL n'a pas démarré après 30s"
            break
        fi
        sleep 1
    done

    if [ $RETRIES -le 30 ]; then
        echo -e "  ${GREEN}✓${NC} PostgreSQL prêt"
    fi

    # Exécuter les migrations SQL
    echo -e "  ${YELLOW}→${NC} Exécution des migrations PostgreSQL..."
    for migration in "$PROJECT_ROOT"/database/postgres/migrations/*.sql; do
        filename=$(basename "$migration")
        docker compose exec -T postgres psql -U automind_user -d automind -f "/docker-entrypoint-initdb.d/$filename" > /dev/null 2>&1 && \
            echo -e "  ${GREEN}✓${NC} $filename" || \
            echo -e "  ${YELLOW}⚠${NC} $filename (déjà appliquée ou erreur)"
    done

    echo ""
    echo -e "  ${GREEN}✓${NC} Services Docker démarrés"
fi

echo ""


# ═══════════════════════════════════════════════════════════════
# Étape 6 : Résumé final
# ═══════════════════════════════════════════════════════════════

echo -e "${CYAN}${BOLD}═══════════════════════════════════════════════════════${NC}"
echo -e "${CYAN}${BOLD}  ✅ Installation terminée !${NC}"
echo -e "${CYAN}${BOLD}═══════════════════════════════════════════════════════${NC}"
echo ""
echo -e "${BOLD}Services démarrés :${NC}"
echo -e "  ┌──────────────────┬──────────────────────────────┐"
echo -e "  │ Service          │ URL                          │"
echo -e "  ├──────────────────┼──────────────────────────────┤"
echo -e "  │ PostgreSQL       │ localhost:5432               │"
echo -e "  │ Neo4j Browser    │ http://localhost:7474        │"
echo -e "  │ Qdrant           │ http://localhost:6333        │"
echo -e "  │ Kafka            │ localhost:9092               │"
echo -e "  └──────────────────┴──────────────────────────────┘"
echo ""
echo -e "${BOLD}Prochaines commandes :${NC}"
echo ""
echo -e "  ${CYAN}# 1. Activer l'environnement Python${NC}"
echo -e "  source .venv/bin/activate"
echo ""
echo -e "  ${CYAN}# 2. Lancer le backend FastAPI${NC}"
echo -e "  cd backend && uvicorn app.main:app --reload --port 8000"
echo ""
echo -e "  ${CYAN}# 3. Lancer le frontend React (dans un autre terminal)${NC}"
echo -e "  cd frontend && npm run dev"
echo ""
echo -e "  ${CYAN}# 4. Ouvrir l'API docs${NC}"
echo -e "  http://localhost:8000/docs"
echo ""
echo -e "  ${CYAN}# 5. Ouvrir le frontend${NC}"
echo -e "  http://localhost:3000"
echo ""

deactivate 2>/dev/null || true
