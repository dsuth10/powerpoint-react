# LLM Diagnostic Runner Script (PowerShell)
# This script sets up the environment and runs comprehensive LLM diagnostics

Write-Host "=== LLM Diagnostic Runner ===" -ForegroundColor Green
Write-Host "Timestamp: $(Get-Date)" -ForegroundColor Yellow
Write-Host ""

# Check if we're in the right directory
if (-not (Test-Path "app/main.py")) {
    Write-Host "Error: This script must be run from the backend directory" -ForegroundColor Red
    Write-Host "Current directory: $(Get-Location)" -ForegroundColor Red
    Write-Host "Expected to find: app/main.py" -ForegroundColor Red
    exit 1
}

# Check for required environment variables
Write-Host "Checking environment variables..." -ForegroundColor Yellow

if (-not $env:OPENROUTER_API_KEY) {
    Write-Host "❌ OPENROUTER_API_KEY is not set" -ForegroundColor Red
    Write-Host "Please set your OpenRouter API key:" -ForegroundColor Yellow
    Write-Host '$env:OPENROUTER_API_KEY = "your-api-key-here"' -ForegroundColor Cyan
    exit 1
} else {
    Write-Host "✅ OPENROUTER_API_KEY is set" -ForegroundColor Green
}

# Set required environment variables for live testing
$env:RUN_LIVE_LLM = "1"
$env:RUN_LIVE_IMAGES = "1"

Write-Host "✅ RUN_LIVE_LLM=1" -ForegroundColor Green
Write-Host "✅ RUN_LIVE_IMAGES=1" -ForegroundColor Green

# Check for optional environment variables
if ($env:STABILITY_API_KEY) {
    Write-Host "✅ STABILITY_API_KEY is set" -ForegroundColor Green
} else {
    Write-Host "⚠️  STABILITY_API_KEY is not set (image generation will use placeholders)" -ForegroundColor Yellow
}

Write-Host ""

# Run the diagnostic script
Write-Host "Running LLM diagnostics..." -ForegroundColor Yellow
Write-Host "This will take a few minutes and generate detailed logs..." -ForegroundColor Yellow
Write-Host ""

try {
    python scripts/run_llm_diagnostics.py
} catch {
    Write-Host "Error running diagnostics: $_" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "=== Diagnostic Complete ===" -ForegroundColor Green
Write-Host "Check llm_diagnostic_report.txt for detailed results" -ForegroundColor Cyan
Write-Host "Check the console output above for real-time logs" -ForegroundColor Cyan
