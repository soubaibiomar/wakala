# ═══════════════════════════════════════════════════════════════
# Wakala — Script d'Audit de Sécurité Unifié
# Usage :
#   powershell -ExecutionPolicy Bypass -File scripts/security_audit.ps1
# ═══════════════════════════════════════════════════════════════

Write-Host "============================================" -ForegroundColor Cyan
Write-Host "  Wakala Security Audit" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

$exitCode = 0

# ─── Backend (pip-audit) ───────────────────────────────────────
Write-Host "[1/3] Backend — pip-audit..." -ForegroundColor Yellow
Push-Location "$PSScriptRoot\..\backend"
try {
    & .venv\Scripts\python.exe -m pip install pip-audit --quiet 2>$null
    & .venv\Scripts\python.exe -m pip_audit --requirement requirements.txt
    if ($LASTEXITCODE -ne 0) {
        Write-Host "  WARN: pip-audit a trouvé des vulnérabilités." -ForegroundColor Red
        $exitCode = 1
    } else {
        Write-Host "  OK: Aucune vulnérabilité Python détectée." -ForegroundColor Green
    }
} catch {
    Write-Host "  SKIP: pip-audit non disponible. Installez-le : pip install pip-audit" -ForegroundColor DarkYellow
}
Pop-Location

Write-Host ""

# ─── Frontend (npm audit) ─────────────────────────────────────
Write-Host "[2/3] Frontend — npm audit..." -ForegroundColor Yellow
Push-Location "$PSScriptRoot\..\frontend"
try {
    npm audit --audit-level=high 2>$null
    if ($LASTEXITCODE -ne 0) {
        Write-Host "  WARN: npm audit a trouvé des vulnérabilités." -ForegroundColor Red
        $exitCode = 1
    } else {
        Write-Host "  OK: Aucune vulnérabilité npm détectée." -ForegroundColor Green
    }
} catch {
    Write-Host "  SKIP: npm non disponible." -ForegroundColor DarkYellow
}
Pop-Location

Write-Host ""

# ─── Vérification des secrets dans le build frontend ──────────
Write-Host "[3/3] Secrets leak check (frontend build)..." -ForegroundColor Yellow
$buildIndex = "$PSScriptRoot\..\frontend\dist\assets\index.js"
if (Test-Path $buildIndex) {
    $content = Get-Content $buildIndex -Raw
    $secrets = @("OPENAI_API_KEY", "AWS_SECRET", "S3_BUCKET", "POSTGRES_PASSWORD", "SECRET_KEY")
    foreach ($secret in $secrets) {
        if ($content -match $secret) {
            Write-Host "  CRITICAL: Secret '$secret' détecté dans le build frontend !" -ForegroundColor Red
            $exitCode = 1
        }
    }
    if ($exitCode -eq 0) {
        Write-Host "  OK: Aucun secret détecté dans le build." -ForegroundColor Green
    }
} else {
    Write-Host "  SKIP: Pas de build trouvé (dist/assets/index.js). Lancez 'npm run build' d'abord." -ForegroundColor DarkYellow
}

Write-Host ""
Write-Host "============================================" -ForegroundColor Cyan
if ($exitCode -eq 0) {
    Write-Host "  RESULTAT: Tous les checks sont passés ✅" -ForegroundColor Green
} else {
    Write-Host "  RESULTAT: Des problèmes ont été détectés ⚠️" -ForegroundColor Red
}
Write-Host "============================================" -ForegroundColor Cyan

exit $exitCode
