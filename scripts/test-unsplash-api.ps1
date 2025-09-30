# Test Unsplash API Key
# This script verifies your Unsplash API key works by searching for puppy images

param(
    [string]$ApiKey = "wWoGcXGfibFrFZtzNnF_CHDaBfon0j3rLhPqf7Y6gfA",
    [string]$Query = "puppy",
    [int]$Count = 3
)

Write-Host "🐕 Testing Unsplash API Key..." -ForegroundColor Green
Write-Host "API Key: $($ApiKey.Substring(0, 10))..." -ForegroundColor Yellow
Write-Host "Search Query: $Query" -ForegroundColor Yellow
Write-Host "Count: $Count" -ForegroundColor Yellow
Write-Host ""

# Build the API URL
$baseUrl = "https://api.unsplash.com"
$searchUrl = "$baseUrl/search/photos?query=$Query&per_page=$Count"

try {
    # Make the API request
    Write-Host "🔍 Searching for '$Query' images..." -ForegroundColor Cyan
    
    $headers = @{
        "Authorization" = "Client-ID $ApiKey"
        "Accept-Version" = "v1"
    }
    
    $response = Invoke-RestMethod -Uri $searchUrl -Headers $headers -Method Get
    
    Write-Host "✅ API Key is working!" -ForegroundColor Green
    Write-Host "📊 Found $($response.results.Count) images" -ForegroundColor Green
    Write-Host ""
    
    # Display results
    Write-Host "📸 Search Results:" -ForegroundColor Magenta
    Write-Host "==================" -ForegroundColor Magenta
    
    for ($i = 0; $i -lt $response.results.Count; $i++) {
        $photo = $response.results[$i]
        Write-Host ""
        Write-Host "Image $($i + 1):" -ForegroundColor Yellow
        $description = if ($photo.description) { $photo.description } elseif ($photo.alt_description) { $photo.alt_description } else { 'No description' }
        Write-Host "  📝 Description: $description" -ForegroundColor White
        Write-Host "  👤 Photographer: $($photo.user.name)" -ForegroundColor White
        Write-Host "  📏 Dimensions: $($photo.width) x $($photo.height)" -ForegroundColor White
        Write-Host "  🔗 Download URL: $($photo.links.download)" -ForegroundColor White
        Write-Host "  📍 Unsplash URL: $($photo.links.html)" -ForegroundColor White
    }
    
    Write-Host ""
    Write-Host "🎉 API test completed successfully!" -ForegroundColor Green
    Write-Host "Your Unsplash MCP server should work perfectly in Cursor." -ForegroundColor Green
    
} catch {
    Write-Host "❌ API test failed!" -ForegroundColor Red
    Write-Host "Error: $($_.Exception.Message)" -ForegroundColor Red
    
    if ($_.Exception.Response) {
        $statusCode = $_.Exception.Response.StatusCode
        Write-Host "Status Code: $statusCode" -ForegroundColor Red
        
        if ($statusCode -eq 401) {
            Write-Host "🔑 Invalid API key. Please check your Unsplash Access Key." -ForegroundColor Red
        } elseif ($statusCode -eq 403) {
            Write-Host "🚫 Access forbidden. Check your API key permissions." -ForegroundColor Red
        } elseif ($statusCode -eq 429) {
            Write-Host "⏰ Rate limit exceeded. Try again later." -ForegroundColor Red
        }
    }
    
    Write-Host ""
    Write-Host "💡 Troubleshooting tips:" -ForegroundColor Yellow
    Write-Host "1. Verify your API key is correct" -ForegroundColor White
    Write-Host "2. Check if your Unsplash application is approved" -ForegroundColor White
    Write-Host "3. Ensure you haven't exceeded rate limits" -ForegroundColor White
    Write-Host "4. Visit https://unsplash.com/developers to check your app status" -ForegroundColor White
}

Write-Host ""
Write-Host "🔗 Unsplash API Documentation: https://unsplash.com/documentation" -ForegroundColor Blue
