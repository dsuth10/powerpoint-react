Param(
  [string]$ComposeFile = "docker-compose.dev.yml"
)

Write-Host "Starting dev environment..." -ForegroundColor Cyan
docker compose -f $ComposeFile up -d --build

function Test-Endpoint($url, $name) {
  try {
    $resp = Invoke-WebRequest -Uri $url -UseBasicParsing -TimeoutSec 5
    if ($resp.StatusCode -lt 400) {
      Write-Host "$name OK ($($resp.StatusCode))" -ForegroundColor Green
      return $true
    }
  } catch { }
  Write-Host "$name FAILED" -ForegroundColor Red
  return $false
}

Start-Sleep -Seconds 5
$beOk = Test-Endpoint "http://localhost:8000/api/v1/health" "Backend health"
$feOk = Test-Endpoint "http://localhost:5173" "Frontend dev server"

if (-not ($beOk -and $feOk)) {
  Write-Host "Containers logs (last 200 lines):" -ForegroundColor Yellow
  docker compose -f $ComposeFile logs --tail 200
  exit 1
}

Write-Host "Attempting FE -> BE request (CORS/dev)" -ForegroundColor Cyan
try {
  $resp = Invoke-WebRequest -Uri "http://localhost:8000/api/v1/health" -UseBasicParsing -TimeoutSec 5
  if ($resp.StatusCode -lt 400) {
    Write-Host "FE->BE reachable (direct health)" -ForegroundColor Green
  }
} catch {
  Write-Host "FE->BE check failed" -ForegroundColor Yellow
}

Write-Host "Smoke test complete." -ForegroundColor Cyan

