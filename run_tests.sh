#!/usr/bin/env bash
set -e

# ═══════════════════════════════════════════════════════════════
# AutoMind — Run All Tests
# Lance les tests backend (pytest) et frontend (vitest),
# puis affiche un resume de couverture combine.
#
# Usage:
#   bash run_tests.sh              # tous les tests
#   bash run_tests.sh --backend    # backend seulement
#   bash run_tests.sh --frontend   # frontend seulement
#   bash run_tests.sh --coverage   # avec couverture
# ═══════════════════════════════════════════════════════════════

BACKEND_DIR="$(cd "$(dirname "$0")/backend" && pwd)"
FRONTEND_DIR="$(cd "$(dirname "$0")/frontend" && pwd)"
PYTHON="${PYTHON:-python}"

RUN_BACKEND=false
RUN_FRONTEND=false
COVERAGE=false

if [[ $# -eq 0 ]]; then
  RUN_BACKEND=true
  RUN_FRONTEND=true
else
  for arg in "$@"; do
    case "$arg" in
      --backend)  RUN_BACKEND=true ;;
      --frontend) RUN_FRONTEND=true ;;
      --coverage) COVERAGE=true ;;
      *) echo "Usage: $0 [--backend] [--frontend] [--coverage]"; exit 1 ;;
    esac
  done
fi

PASSED=0
FAILED=0
FAILED_TESTS=""

echo ""
echo "╔══════════════════════════════════════════════════════════╗"
echo "║   AutoMind — Suite de Tests Complete                     ║"
echo "╚══════════════════════════════════════════════════════════╝"
echo ""

# ─── Backend ───────────────────────────────────────────────────

if $RUN_BACKEND; then
  echo "→ Tests Backend (pytest)..."
  cd "$BACKEND_DIR"

  COV_OPTS=""
  if $COVERAGE; then
    COV_OPTS="--cov=app --cov-report=term-missing --cov-fail-under=70"
  fi

  if $PYTHON -m pytest tests/ $COV_OPTS -v --tb=short -p no:cacheprovider 2>&1; then
    echo ""
    echo "  ✓ Backend : tous les tests passes"
  else
    echo ""
    echo "  ✗ Backend : certains tests ont echoue"
    FAILED=$((FAILED + 1))
    FAILED_TESTS="$FAILED_TESTS backend"
  fi
  echo ""
fi

# ─── Frontend ──────────────────────────────────────────────────

if $RUN_FRONTEND; then
  echo "→ Tests Frontend (vitest)..."
  cd "$FRONTEND_DIR"

  if npx vitest run 2>&1; then
    echo ""
    echo "  ✓ Frontend : tous les tests passes"
  else
    echo ""
    echo "  ✗ Frontend : certains tests ont echoue"
    FAILED=$((FAILED + 1))
    FAILED_TESTS="$FAILED_TESTS frontend"
  fi
  echo ""
fi

# ─── Resume ────────────────────────────────────────────────────

echo "╔══════════════════════════════════════════════════════════╗"
echo "║   RESUME                                                 ║"
echo "╚══════════════════════════════════════════════════════════╝"
echo ""

if [ -z "$FAILED_TESTS" ]; then
  echo "  ✓ Tous les tests passes"
  exit 0
else
  echo "  ✗ Echecs dans :$FAILED_TESTS"
  exit 1
fi
