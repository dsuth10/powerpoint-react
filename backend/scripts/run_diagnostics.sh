#!/bin/bash

# LLM Diagnostic Runner Script
# This script sets up the environment and runs comprehensive LLM diagnostics

set -e

echo "=== LLM Diagnostic Runner ==="
echo "Timestamp: $(date)"
echo

# Check if we're in the right directory
if [ ! -f "app/main.py" ]; then
    echo "Error: This script must be run from the backend directory"
    echo "Current directory: $(pwd)"
    echo "Expected to find: app/main.py"
    exit 1
fi

# Check for required environment variables
echo "Checking environment variables..."

if [ -z "$OPENROUTER_API_KEY" ]; then
    echo "❌ OPENROUTER_API_KEY is not set"
    echo "Please set your OpenRouter API key:"
    echo "export OPENROUTER_API_KEY='your-api-key-here'"
    exit 1
else
    echo "✅ OPENROUTER_API_KEY is set"
fi

# Set required environment variables for live testing
export RUN_LIVE_LLM=1
export RUN_LIVE_IMAGES=1

echo "✅ RUN_LIVE_LLM=1"
echo "✅ RUN_LIVE_IMAGES=1"

# Check for optional environment variables
if [ -n "$STABILITY_API_KEY" ]; then
    echo "✅ STABILITY_API_KEY is set"
else
    echo "⚠️  STABILITY_API_KEY is not set (image generation will use placeholders)"
fi

echo

# Run the diagnostic script
echo "Running LLM diagnostics..."
echo "This will take a few minutes and generate detailed logs..."
echo

python scripts/run_llm_diagnostics.py

echo
echo "=== Diagnostic Complete ==="
echo "Check llm_diagnostic_report.txt for detailed results"
echo "Check the console output above for real-time logs"
