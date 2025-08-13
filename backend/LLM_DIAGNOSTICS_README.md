# LLM Diagnostics Guide

This guide will help you run comprehensive diagnostics to identify why the LLM API calls aren't returning actual images and responses.

## Overview

We've implemented extensive logging throughout the LLM service and created diagnostic tools to help identify the root cause of the issues. The diagnostics will:

1. **Test Environment Configuration** - Verify API keys and settings
2. **Test Direct API Connectivity** - Ensure OpenRouter API is accessible
3. **Test Structured Slide Generation** - Verify LLM can generate proper slide structures
4. **Test Service Integration** - Test the full service pipeline
5. **Test Image Generation** - Specifically test image generation capabilities

## Prerequisites

1. **OpenRouter API Key**: You need a valid OpenRouter API key
2. **Stability AI API Key** (optional): For image generation testing
3. **Python Environment**: Backend dependencies installed

## Quick Start

### 1. Set Environment Variables

```powershell
# Set your OpenRouter API key
$env:OPENROUTER_API_KEY = "your-openrouter-api-key-here"

# Optional: Set Stability AI API key for image generation
$env:STABILITY_API_KEY = "your-stability-api-key-here"

# Set log level for detailed debugging
$env:LOG_LEVEL = "DEBUG"
```

### 2. Run Comprehensive Diagnostics

```powershell
# Navigate to backend directory
cd backend

# Run the comprehensive diagnostic script
.\scripts\run_diagnostics.ps1
```

### 3. Run Live Tests

```powershell
# Run existing pytest tests with live LLM
.\scripts\run_live_tests.ps1
```

## What the Diagnostics Will Show

### Environment Configuration Test
- ✅/❌ API keys present
- ✅/❌ Environment variables set correctly
- ✅/❌ Settings loaded properly

### Direct API Connectivity Test
- ✅/❌ Can connect to OpenRouter API
- ✅/❌ Simple "PONG" response works
- ✅/❌ Authentication is valid

### Structured Slide Generation Test
- ✅/❌ LLM can generate proper JSON structure
- ✅/❌ Slides have titles, bullets, notes
- ✅/❌ Images are included in responses
- ✅/❌ JSON parsing works correctly

### Service Integration Test
- ✅/❌ Full service pipeline works
- ✅/❌ Error handling works correctly
- ✅/❌ Fallback mechanisms work

### Image Generation Test
- ✅/❌ LLM includes images in responses
- ✅/❌ Image URLs are accessible
- ✅/❌ Image metadata is complete

## Expected Issues and Solutions

### Issue: "No API key available"
**Solution**: Set your OpenRouter API key:
```powershell
$env:OPENROUTER_API_KEY = "your-api-key-here"
```

### Issue: "HTTP 401/403" errors
**Solution**: Check your API key is valid and has sufficient credits

### Issue: "HTTP 429" rate limiting
**Solution**: Wait a few minutes and retry, or check your usage limits

### Issue: "Malformed LLM response"
**Solution**: This indicates the LLM isn't returning proper JSON. Check:
- Model selection (use "openai/gpt-4o-mini" or "openai/gpt-4o")
- Prompt engineering
- Response format settings

### Issue: "No images in responses"
**Solution**: The LLM prompt may not be requesting images strongly enough. Check:
- System prompt includes image requirements
- User prompt specifically requests images
- Model supports image generation in responses

## Log Files

The diagnostics will generate several log files:

- `llm_diagnostic_report.txt` - Summary of all test results
- `logs/app.log` - Detailed application logs
- Console output - Real-time diagnostic information

## Manual Testing

You can also test manually using the FastAPI application:

1. **Start the backend**:
```powershell
cd backend
uvicorn app.main:app --reload --log-level debug
```

2. **Make a test request**:
```bash
curl -X POST "http://localhost:8000/api/v1/chat/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Artificial Intelligence",
    "slide_count": 2,
    "model": "openai/gpt-4o-mini",
    "language": "en"
  }'
```

3. **Check the logs** for detailed information about the request/response cycle.

## Troubleshooting

### If diagnostics fail completely:
1. Check your internet connection
2. Verify API keys are correct
3. Check OpenRouter service status
4. Ensure you have sufficient API credits

### If some tests pass but others fail:
1. Look at the specific error messages
2. Check the detailed logs for the failing tests
3. Verify the specific API endpoints being tested

### If images are missing:
1. Check if the LLM prompt is requesting images
2. Verify the JSON structure includes image fields
3. Test image URL accessibility
4. Check if Stability AI integration is working

## Next Steps

After running the diagnostics:

1. **Review the diagnostic report** to understand what's working and what's not
2. **Check the detailed logs** for specific error messages
3. **Share the results** with the development team
4. **Implement fixes** based on the identified issues

## Support

If you're still having issues after running the diagnostics:

1. Save the diagnostic report and logs
2. Note any specific error messages
3. Check the OpenRouter and Stability AI service status
4. Contact the development team with the diagnostic results
