Param(
  [string]$ComposeFile = "docker-compose.dev.yml"
)

Write-Host "Verifying repo structure and versions..." -ForegroundColor Cyan

# Check critical files
$mustExist = @(
  ".nvmrc",
  "backend/.python-version",
  "frontend/Dockerfile",
  "backend/Dockerfile",
  "docker-compose.dev.yml",
  "planning_documents/versions.md"
)
$errors = 0
foreach ($f in $mustExist) {
  if (-not (Test-Path $f)) { Write-Host "Missing: $f" -ForegroundColor Red; $errors++ }
}

if ($errors -gt 0) { Write-Host "Verification failed." -ForegroundColor Red; exit 1 }

Write-Host "Repo structure OK." -ForegroundColor Green
exit 0

