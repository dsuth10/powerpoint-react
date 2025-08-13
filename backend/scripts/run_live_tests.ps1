# Live LLM Test Runner Script (PowerShell)
# This script runs the existing pytest tests with live LLM enabled

Write-Host "=== Live LLM Test Runner ===" -ForegroundColor Green
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

# Run the live LLM tests
Write-Host "Running live LLM tests..." -ForegroundColor Yellow
Write-Host "This will test the actual LLM integration..." -ForegroundColor Yellow
Write-Host ""

try {
    # Run the connectivity test
    Write-Host "Running OpenRouter connectivity test..." -ForegroundColor Cyan
    pytest tests/test_openrouter_connectivity.py -v -s
    
    Write-Host ""
    Write-Host "Running comprehensive LLM diagnostic tests..." -ForegroundColor Cyan
    pytest tests/test_llm_diagnostic.py -v -s
    
    Write-Host ""
    Write-Host "Running all live LLM tests..." -ForegroundColor Cyan
    pytest tests/ -m "live_llm" -v -s
    
} catch {
    Write-Host "Error running live tests: $_" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "=== Live Tests Complete ===" -ForegroundColor Green
Write-Host "Check the console output above for test results" -ForegroundColor Cyan
