# Test Script - Use OpenCode Docker Server API Key
# This script extracts the API key from the Docker container and runs the agent

Write-Host "🔍 Checking for OpenCode Docker container..." -ForegroundColor Cyan

# Check if Docker is running
$dockerRunning = docker ps 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Docker is not running or not accessible" -ForegroundColor Red
    Write-Host "Please start Docker Desktop first" -ForegroundColor Yellow
    exit 1
}

# Find OpenCode container
$container = docker ps --format "{{.ID}} {{.Names}}" | Where-Object { $_ -match "opencode" } | ForEach-Object { ($_ -split " ")[0] }
if (-not $container) {
    Write-Host "❌ OpenCode container not found" -ForegroundColor Red
    Write-Host "Start it with:" -ForegroundColor Yellow
    $startCmd = 'docker run -d -p 4096:4096 --name opencode-server -e OPENROUTER_API_KEY="YOUR_KEY" ghcr.io/sst/opencode opencode serve --port 4096 --hostname 0.0.0.0'
    Write-Host $startCmd -ForegroundColor Cyan
    exit 1
}

Write-Host "✅ Found OpenCode container: $container" -ForegroundColor Green

# Try to extract API key from container environment
Write-Host "`n🔑 Trying to extract API key from container..." -ForegroundColor Cyan

$apiKey = $null

# Try environment variable first
try {
    $envKey = docker exec $container printenv OPENROUTER_API_KEY 2>$null
    if ($envKey -and $envKey.Trim()) {
        $apiKey = $envKey.Trim()
        Write-Host "✅ Found API key in environment variable" -ForegroundColor Green
    }
} catch {
    # Ignore errors
}

# Try /tmp/api-key
if (-not $apiKey) {
    try {
        $fileKey = docker exec $container cat /tmp/api-key 2>$null
        if ($fileKey -and $fileKey.Trim()) {
            $apiKey = $fileKey.Trim()
            Write-Host "✅ Found API key in /tmp/api-key" -ForegroundColor Green
        }
    } catch {
        # Ignore errors
    }
}

# Try .opencode.json
if (-not $apiKey) {
    try {
        $opcodeJson = docker exec $container cat /workspace/.opencode.json 2>$null
        if ($opcodeJson) {
            $config = $opcodeJson | ConvertFrom-Json -ErrorAction SilentlyContinue
            if ($config.apiKey) {
                $apiKey = $config.apiKey
                Write-Host "✅ Found API key in .opencode.json" -ForegroundColor Green
            }
        }
    } catch {
        # Ignore errors
    }
}

if (-not $apiKey) {
    Write-Host "❌ Could not find API key in container" -ForegroundColor Red
    Write-Host "Please set it manually:" -ForegroundColor Yellow
    Write-Host '  $env:OPENROUTER_API_KEY="sk-or-v1-..."' -ForegroundColor Cyan
    exit 1
}

# Set environment variable
$env:OPENROUTER_API_KEY = $apiKey.Trim()
Write-Host "✅ API key set in environment" -ForegroundColor Green

# Alternatively, write to file so client.py can read it
$tmpDir = "C:\tmp"
if (-not (Test-Path $tmpDir)) {
    New-Item -ItemType Directory -Path $tmpDir | Out-Null
}
$apiKey.Trim() | Out-File -FilePath "$tmpDir\api-key" -Encoding utf8 -NoNewline
Write-Host "✅ API key written to C:\tmp\api-key" -ForegroundColor Green

# Run the agent
Write-Host "`n🚀 Starting autonomous agent..." -ForegroundColor Cyan
Write-Host "Arguments: $args" -ForegroundColor Gray
Write-Host ""

if ($args.Count -eq 0) {
    # Default test run
    python autonomous_agent_demo.py --project-dir ./my-app --model auto --max-iterations 2
} else {
    # Pass through arguments
    python autonomous_agent_demo.py @args
}

Write-Host "`n✅ Test complete!" -ForegroundColor Green
