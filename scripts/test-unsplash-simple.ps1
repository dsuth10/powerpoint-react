# Simple Unsplash API Test
# This script verifies your Unsplash API key works

$ApiKey = "wWoGcXGfibFrFZtzNnF_CHDaBfon0j3rLhPqf7Y6gfA"
$Query = "puppy"
$Count = 3

Write-Host "🐕 Testing Unsplash API Key..." -ForegroundColor Green
Write-Host "API Key: $($ApiKey.Substring(0, 10))..." -ForegroundColor Yellow
Write-Host "Search Query: $Query" -ForegroundColor Yellow
Write-Host ""

# Build the API URL
$baseUrl = "https://api.unsplash.com"
$searchUrl = "$baseUrl/search/photos?query=$Query&per_page=$Count"

# Make the API request
Write-Host "🔍 Searching for '$Query' images..." -ForegroundColor Cyan

$headers = @{
    "Authorization" = "Client-ID $ApiKey"
    "Accept-Version" = "v1"
}

try {
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
        
        $description = "No description"
        if ($photo.description) { $description = $photo.description }
        elseif ($photo.alt_description) { $description = $photo.alt_description }
        
        Write-Host "  📝 Description: $description" -ForegroundColor White
        Write-Host "  👤 Photographer: $($photo.user.name)" -ForegroundColor White
        Write-Host "  📏 Dimensions: $($photo.width) x $($photo.height)" -ForegroundColor White
        Write-Host "  🔗 Download URL: $($photo.links.download)" -ForegroundColor White
    }
    
    Write-Host ""
    Write-Host "🎉 API test completed successfully!" -ForegroundColor Green
    Write-Host "Your Unsplash MCP server should work perfectly in Cursor." -ForegroundColor Green
    
} catch {
    Write-Host "❌ API test failed!" -ForegroundColor Red
    Write-Host "Error: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host ""
    Write-Host "💡 Please check your API key at: https://unsplash.com/developers" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "🔗 Unsplash API Documentation: https://unsplash.com/documentation" -ForegroundColor Blue

