# AutoMind -- Run All Tests (PowerShell)
param([switch]$Backend,[switch]$Frontend)

$RUN_BACKEND = $Backend -or (!$Backend -and !$Frontend)
$RUN_FRONTEND = $Frontend -or (!$Backend -and !$Frontend)
$FAILED_TESTS = @()

Write-Host "--- AutoMind -- Suite de Tests ---"
Write-Host ""

if ($RUN_BACKEND) {
  Write-Host ">> Tests Backend (pytest)..."
  $result = & "D:\Projet automobile\vente-auto-platform\backend\.venv\Scripts\python.exe" -m pytest "D:\Projet automobile\vente-auto-platform\backend\tests" --tb=short -p no:cacheprovider 2>&1
  $exitCode = $LASTEXITCODE
  if ($exitCode -eq 0) {
    Write-Host "  OK Backend : tous les tests passes"
  } else {
    Write-Host $result
    Write-Host "  FAIL Backend : certains tests ont echoue"
    $FAILED_TESTS += "backend"
  }
}

if ($RUN_FRONTEND) {
  Write-Host ">> Tests Frontend (vitest)..."
  Push-Location "D:\Projet automobile\vente-auto-platform\frontend"
  $result = cmd /c "npx vitest run 2>&1"
  $exitCode = $LASTEXITCODE
  Pop-Location
  if ($exitCode -eq 0) {
    Write-Host "  OK Frontend : tous les tests passes"
  } else {
    Write-Host $result
    Write-Host "  FAIL Frontend : certains tests ont echoue"
    $FAILED_TESTS += "frontend"
  }
}

Write-Host ""
if ($FAILED_TESTS.Count -eq 0) {
  Write-Host "  ALL TESTS PASSED"
  exit 0
} else {
  Write-Host "  FAILURES IN : $($FAILED_TESTS -join ', ')"
  exit 1
}
