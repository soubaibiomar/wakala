# ═══════════════════════════════════════════════════════════════
# Wakala — Script d'installation complet (Windows PowerShell)
#
# Usage :
#   .\setup.ps1                 # Installation complète
#   .\setup.ps1 -SkipDocker     # Sans démarrer les conteneurs Docker
#   .\setup.ps1 -Dev            # Inclure les dépendances de dev
#
# Ce script est idempotent : il peut être relancé sans casser
# une installation existante.
# ═══════════════════════════════════════════════════════════════

param(
    [switch]$SkipDocker,
    [switch]$Dev,
    [switch]$Help
)

$ErrorActionPreference = "Stop"

if ($Help) {
    Write-Host "Usage: .\setup.ps1 [-SkipDocker] [-Dev]"
    Write-Host "  -SkipDocker  Ne pas demarrer les conteneurs Docker"
    Write-Host "  -Dev         Installer les dependances de developpement"
    exit 0
}

# ─── Header ───────────────────────────────────────────────────
Write-Host ""
Write-Host "═══════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "  🚗 Wakala — Installation de la plateforme" -ForegroundColor Cyan
Write-Host "═══════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""

$ProjectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $ProjectRoot


# ═══════════════════════════════════════════════════════════════
# Étape 1 : Vérification des prérequis système
# ═══════════════════════════════════════════════════════════════

Write-Host "[1/6] Verification des prerequis systeme..." -ForegroundColor Blue
Write-Host ""

$Missing = @()

# Node.js >= 18
try {
    $NodeVer = (node -v) -replace 'v', ''
    $NodeMajor = [int]($NodeVer.Split('.')[0])
    if ($NodeMajor -ge 18) {
        Write-Host "  ✓ Node.js v$NodeVer" -ForegroundColor Green
    } else {
        Write-Host "  ✗ Node.js v$NodeVer — version 18+ requise" -ForegroundColor Red
        $Missing += "Node.js 18+"
    }
} catch {
    Write-Host "  ✗ Node.js non trouve" -ForegroundColor Red
    $Missing += "Node.js 18+ (https://nodejs.org)"
}

# npm
try {
    $NpmVer = npm -v
    Write-Host "  ✓ npm $NpmVer" -ForegroundColor Green
} catch {
    Write-Host "  ✗ npm non trouve" -ForegroundColor Red
    $Missing += "npm"
}

# Python >= 3.11
try {
    $PyVer = python --version 2>&1
    $PyMinor = [int]($PyVer -replace 'Python (\d+)\.(\d+)\..*', '$2')
    if ($PyMinor -ge 11) {
        Write-Host "  ✓ $PyVer" -ForegroundColor Green
    } else {
        Write-Host "  ✗ $PyVer — version 3.11+ requise" -ForegroundColor Red
        $Missing += "Python 3.11+"
    }
} catch {
    Write-Host "  ✗ Python non trouve" -ForegroundColor Red
    $Missing += "Python 3.11+ (https://python.org)"
}

# Docker
try {
    $DockerVer = (docker --version) -replace 'Docker version ([^,]+),.*', '$1'
    Write-Host "  ✓ Docker $DockerVer" -ForegroundColor Green
} catch {
    Write-Host "  ⚠ Docker non trouve" -ForegroundColor Yellow
    if (-not $SkipDocker) {
        $Missing += "Docker Desktop (https://docs.docker.com/get-docker/)"
    }
}

# Docker Compose
try {
    $ComposeVer = docker compose version --short 2>&1
    Write-Host "  ✓ Docker Compose $ComposeVer" -ForegroundColor Green
} catch {
    Write-Host "  ⚠ Docker Compose non trouve" -ForegroundColor Yellow
    if (-not $SkipDocker) { $Missing += "Docker Compose v2+" }
}

Write-Host ""

if ($Missing.Count -gt 0) {
    Write-Host "Prerequis manquants :" -ForegroundColor Red
    foreach ($item in $Missing) {
        Write-Host "  • $item" -ForegroundColor Red
    }
    Write-Host ""
    Write-Host "Installez les prerequis ci-dessus puis relancez .\setup.ps1" -ForegroundColor Red
    exit 1
}

Write-Host "  Tous les prerequis sont satisfaits ✓" -ForegroundColor Green
Write-Host ""


# ═══════════════════════════════════════════════════════════════
# Étape 2 : Installation des dépendances Frontend
# ═══════════════════════════════════════════════════════════════

Write-Host "[2/6] Installation des dependances Frontend (npm)..." -ForegroundColor Blue
Write-Host ""

Set-Location "$ProjectRoot\frontend"

if (Test-Path "node_modules") {
    Write-Host "  → node_modules existe deja, mise a jour..." -ForegroundColor Yellow
    npm install --silent 2>&1 | Select-Object -Last 1
} else {
    npm install 2>&1 | Select-Object -Last 5
}

$PackageCount = (Get-ChildItem node_modules -Directory -ErrorAction SilentlyContinue).Count
Write-Host "  ✓ Frontend — $PackageCount packages installes" -ForegroundColor Green
Write-Host ""

Set-Location $ProjectRoot


# ═══════════════════════════════════════════════════════════════
# Étape 3 : Environnement virtuel Python + Backend
# ═══════════════════════════════════════════════════════════════

Write-Host "[3/6] Installation des dependances Python..." -ForegroundColor Blue
Write-Host ""

$VenvDir = "$ProjectRoot\.venv"

if (-not (Test-Path $VenvDir)) {
    Write-Host "  → Creation de l'environnement virtuel (.venv)..." -ForegroundColor Yellow
    python -m venv $VenvDir
}

# Activer le venv
& "$VenvDir\Scripts\Activate.ps1"

# Mise à jour pip
Write-Host "  → Mise a jour de pip..." -ForegroundColor Yellow
python -m pip install --upgrade pip --quiet 2>&1 | Out-Null

# Backend
Write-Host "  → Installation des dependances backend..." -ForegroundColor Yellow
pip install -r "$ProjectRoot\backend\requirements.txt" --quiet 2>&1 | Out-Null

if ($Dev) {
    Write-Host "  → Installation des dependances dev..." -ForegroundColor Yellow
    pip install -r "$ProjectRoot\backend\requirements-dev.txt" --quiet 2>&1 | Out-Null
}

# Data pipeline
Write-Host "  → Installation des dependances data-pipeline..." -ForegroundColor Yellow
pip install -r "$ProjectRoot\data-pipeline\requirements.txt" --quiet 2>&1 | Out-Null

# Analytics
Write-Host "  → Installation des dependances analytics..." -ForegroundColor Yellow
pip install -r "$ProjectRoot\analytics\requirements.txt" --quiet 2>&1 | Out-Null

$Installed = (pip list --format=columns 2>$null | Measure-Object -Line).Lines
Write-Host "  ✓ Python — $Installed packages installes dans .venv" -ForegroundColor Green
Write-Host ""


# ═══════════════════════════════════════════════════════════════
# Étape 4 : Configuration .env
# ═══════════════════════════════════════════════════════════════

Write-Host "[4/6] Configuration de l'environnement (.env)..." -ForegroundColor Blue
Write-Host ""

if (-not (Test-Path "$ProjectRoot\.env")) {
    Copy-Item "$ProjectRoot\.env.example" "$ProjectRoot\.env"
    Write-Host "  ✓ .env cree a partir de .env.example" -ForegroundColor Green
    Write-Host "  ⚠  Pensez a personnaliser les valeurs (SECRET_KEY, OPENAI_API_KEY...)" -ForegroundColor Yellow
} else {
    Write-Host "  ✓ .env existe deja — aucune modification" -ForegroundColor Green
}

Write-Host ""


# ═══════════════════════════════════════════════════════════════
# Étape 5 : Docker Compose (services d'infrastructure)
# ═══════════════════════════════════════════════════════════════

Write-Host "[5/6] Services d'infrastructure (Docker Compose)..." -ForegroundColor Blue
Write-Host ""

if ($SkipDocker) {
    Write-Host "  ⏭ Docker ignore (-SkipDocker)" -ForegroundColor Yellow
} else {
    Set-Location $ProjectRoot

    Write-Host "  → Demarrage : PostgreSQL, Neo4j, Qdrant, Kafka, Zookeeper..." -ForegroundColor Yellow
    docker compose up -d postgres neo4j qdrant zookeeper kafka 2>&1 | Select-Object -Last 10

    # Attendre que PostgreSQL soit prêt
    Write-Host "  → Attente de PostgreSQL..." -ForegroundColor Yellow
    $Retries = 0
    do {
        $Retries++
        Start-Sleep -Seconds 1
        $Ready = docker compose exec -T postgres pg_isready -U wakala_user -d wakala 2>&1
    } while ($LASTEXITCODE -ne 0 -and $Retries -lt 30)

    if ($Retries -lt 30) {
        Write-Host "  ✓ PostgreSQL pret" -ForegroundColor Green
    } else {
        Write-Host "  ✗ PostgreSQL n'a pas demarre apres 30s" -ForegroundColor Red
    }

    Write-Host "  ✓ Services Docker demarres" -ForegroundColor Green
}

Write-Host ""


# ═══════════════════════════════════════════════════════════════
# Étape 6 : Résumé final
# ═══════════════════════════════════════════════════════════════

Write-Host "═══════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "  ✅ Installation terminee !" -ForegroundColor Cyan
Write-Host "═══════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""
Write-Host "Services demarres :" -ForegroundColor White
Write-Host "  ┌──────────────────┬──────────────────────────────┐"
Write-Host "  │ Service          │ URL                          │"
Write-Host "  ├──────────────────┼──────────────────────────────┤"
Write-Host "  │ PostgreSQL       │ localhost:5432               │"
Write-Host "  │ Neo4j Browser    │ http://localhost:7474        │"
Write-Host "  │ Qdrant           │ http://localhost:6333        │"
Write-Host "  │ Kafka            │ localhost:9092               │"
Write-Host "  └──────────────────┴──────────────────────────────┘"
Write-Host ""
Write-Host "Prochaines commandes :" -ForegroundColor White
Write-Host ""
Write-Host "  # 1. Activer l'environnement Python" -ForegroundColor Cyan
Write-Host "  .\.venv\Scripts\Activate.ps1"
Write-Host ""
Write-Host "  # 2. Lancer le backend FastAPI" -ForegroundColor Cyan
Write-Host "  cd backend; uvicorn app.main:app --reload --port 8000"
Write-Host ""
Write-Host "  # 3. Lancer le frontend React (dans un autre terminal)" -ForegroundColor Cyan
Write-Host "  cd frontend; npm run dev"
Write-Host ""
Write-Host "  # 4. Ouvrir l'API docs" -ForegroundColor Cyan
Write-Host "  http://localhost:8000/docs"
Write-Host ""
Write-Host "  # 5. Ouvrir le frontend" -ForegroundColor Cyan
Write-Host "  http://localhost:3000"
Write-Host ""

deactivate 2>$null
