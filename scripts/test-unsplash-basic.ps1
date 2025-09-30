# Basic Unsplash API Test
$ApiKey = "wWoGcXGfibFrFZtzNnF_CHDaBfon0j3rLhPqf7Y6gfA"
$Query = "puppy"

Write-Host "Testing Unsplash API Key..." -ForegroundColor Green
Write-Host "API Key: $($ApiKey.Substring(0, 10))..." -ForegroundColor Yellow
Write-Host "Search Query: $Query" -ForegroundColor Yellow

$baseUrl = "https://api.unsplash.com"
$searchUrl = "$baseUrl/search/photos?query=$Query&per_page=3"

$headers = @{
    "Authorization" = "Client-ID $ApiKey"
    "Accept-Version" = "v1"
}

Write-Host "Searching for '$Query' images..." -ForegroundColor Cyan

$response = Invoke-RestMethod -Uri $searchUrl -Headers $headers -Method Get

Write-Host "API Key is working!" -ForegroundColor Green
Write-Host "Found $($response.results.Count) images" -ForegroundColor Green

for ($i = 0; $i -lt $response.results.Count; $i++) {
    $photo = $response.results[$i]
    Write-Host ""
    Write-Host "Image $($i + 1):" -ForegroundColor Yellow
    Write-Host "  Photographer: $($photo.user.name)" -ForegroundColor White
    Write-Host "  Dimensions: $($photo.width) x $($photo.height)" -ForegroundColor White
    Write-Host "  Download URL: $($photo.links.download)" -ForegroundColor White
}

Write-Host ""
Write-Host "API test completed successfully!" -ForegroundColor Green

