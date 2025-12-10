# Restart OpenCode Server with FREE model enforced
# This ensures the server ONLY uses free models

Write-Host "🛑 Stopping existing OpenCode container..." -ForegroundColor Yellow

# Stop and remove existing container
docker stop opencode-server 2>$null
docker rm opencode-server 2>$null

Write-Host "✅ Old container removed" -ForegroundColor Green

# Create config directory
$configDir = "$PWD\.opencode-server"
if (-not (Test-Path $configDir)) {
    New-Item -ItemType Directory -Path $configDir | Out-Null
}

# Create .opencode.json with FREE model enforced
$config = @{
    '$schema' = 'https://opencode.ai/config.json'
    theme = 'opencode'
    model = 'openrouter/mistralai/mistral-7b-instruct:free'
    max_tokens = 200
    autoupdate = $true
    permission = @{
        edit = 'allow'
        bash = 'ask'
        webfetch = 'deny'
        doom_loop = 'ask'
        external_directory = 'ask'
    }
}

$config | ConvertTo-Json -Depth 10 | Out-File -FilePath "$configDir\.opencode.json" -Encoding utf8

Write-Host "✅ Created config with FREE model" -ForegroundColor Green

# Get OpenRouter API key
$apiKey = $env:OPENROUTER_API_KEY
if (-not $apiKey) {
    Write-Host "⚠️  No OPENROUTER_API_KEY found in environment" -ForegroundColor Yellow
    Write-Host "Enter your OpenRouter API key (or press Enter to skip):" -ForegroundColor Cyan
    $apiKey = Read-Host
}

# Start OpenCode server with volume mount and environment variables
Write-Host "`n🚀 Starting OpenCode server with FREE model..." -ForegroundColor Cyan

$dockerCmd = @"
docker run -d ``
  -p 4096:4096 ``
  --name opencode-server ``
  -v "${configDir}:/workspace" ``
  -e OPENROUTER_API_KEY="$apiKey" ``
  -e DEFAULT_MODEL="openrouter/mistralai/mistral-7b-instruct:free" ``
  ghcr.io/sst/opencode ``
  opencode serve --port 4096 --hostname 0.0.0.0
"@

Write-Host $dockerCmd -ForegroundColor Gray
Invoke-Expression $dockerCmd

if ($LASTEXITCODE -eq 0) {
    Write-Host "`n✅ OpenCode server started successfully!" -ForegroundColor Green
    Write-Host "`n📋 Configuration:" -ForegroundColor Cyan
    Write-Host "  - Port: 4096" -ForegroundColor White
    Write-Host "  - Model: mistralai/mistral-7b-instruct:free (FREE!)" -ForegroundColor Green
    Write-Host "  - Max Tokens: 200" -ForegroundColor White
    Write-Host "  - Config: $configDir\.opencode.json" -ForegroundColor White
    Write-Host "`n⚠️  IMPORTANT: This model is FREE but may have rate limits" -ForegroundColor Yellow
    Write-Host "`n🔗 Access: http://localhost:4096" -ForegroundColor Cyan
} else {
    Write-Host "`n❌ Failed to start server" -ForegroundColor Red
    exit 1
}

# Wait for server to be ready
Write-Host "`n⏳ Waiting for server to be ready..." -ForegroundColor Yellow
Start-Sleep -Seconds 5

# Test connection
try {
    $response = Invoke-WebRequest -Uri "http://localhost:4096/health" -TimeoutSec 5 -ErrorAction Stop
    Write-Host "✅ Server is ready!" -ForegroundColor Green
} catch {
    Write-Host "⚠️  Server may not be fully ready yet. Wait a few more seconds." -ForegroundColor Yellow
}

Write-Host "`n✅ You can now run:" -ForegroundColor Green
Write-Host "   .\test_with_docker_key.ps1" -ForegroundColor Cyan
