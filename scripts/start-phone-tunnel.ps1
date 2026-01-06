# Get local IP address (try multiple methods for robustness)
$ipAddress = $null

# Method 1: Try common network adapters
$ipAddress = (Get-NetIPAddress -AddressFamily IPv4 | Where-Object { $_.IPAddress -notmatch "^127\." -and $_.PrefixLength -eq 24 } | Select-Object -First 1).IPAddress

# Method 2: Fall back to any non-loopback IPv4 address
if (-not $ipAddress) {
  $ipAddress = (Get-NetIPAddress -AddressFamily IPv4 | Where-Object { $_.IPAddress -notmatch "^127\." } | Select-Object -First 1).IPAddress
}

if (-not $ipAddress) {
  Write-Host "Error: Could not detect local IP. Please ensure you're connected to a network." -ForegroundColor Red
  Write-Host "Alternative: Run 'ipconfig' and manually set the IP when prompted." -ForegroundColor Yellow
  $ipAddress = Read-Host "Enter your local IP (e.g., 192.168.1.X)"
  if (-not $ipAddress) {
    exit 1
  }
}

Write-Host "Local IP detected: $ipAddress" -ForegroundColor Green

# Create .env.local for webapp if it doesn't exist
$envFile = ".\webapp\.env.local"
$envContent = @"
# Auto-generated for phone/LAN access
NEXT_PUBLIC_API_BASE_URL=http://$ipAddress:8000
"@

if (-not (Test-Path $envFile)) {
  Write-Host "Creating .env.local with API base URL: $envContent" -ForegroundColor Cyan
  Set-Content -Path $envFile -Value $envContent
} else {
  # Update existing .env.local
  if ((Get-Content $envFile) -notmatch "NEXT_PUBLIC_API_BASE_URL") {
    Add-Content -Path $envFile -Value "`n$envContent"
    Write-Host "Updated .env.local with API base URL" -ForegroundColor Cyan
  } else {
    Write-Host ".env.local already configured" -ForegroundColor Cyan
  }
}

Write-Host ""
Write-Host "Starting services..." -ForegroundColor Yellow
Write-Host "1. ML API will be available at http://$ipAddress:8000" -ForegroundColor Gray
Write-Host "2. Website will be available at http://$ipAddress:3000" -ForegroundColor Gray
Write-Host "3. Tunnel URL will be displayed below for phone access" -ForegroundColor Gray
Write-Host ""

# Resolve Python path (prefer workspace venv)
$pythonPath = Join-Path $PWD ".venv/Scripts/python.exe"
if (-not (Test-Path $pythonPath)) {
  $pythonPath = "python"
}

# Start ML API in background
Write-Host "Starting ML API on 0.0.0.0:8000..." -ForegroundColor Cyan
$apiArgs = "src/api/allergen_api.py --host 0.0.0.0 --port 8000"
$apiProcess = Start-Process -WindowStyle Hidden -PassThru -FilePath $pythonPath -ArgumentList $apiArgs -WorkingDirectory $PWD

# Wait for API health
Write-Host "Waiting for ML API health..." -ForegroundColor Cyan
$healthOk = $false
for ($i = 0; $i -lt 10; $i++) {
  Start-Sleep -Seconds 2
  try {
    $hc = Invoke-WebRequest -Uri "http://$ipAddress:8000/health" -TimeoutSec 3 -ErrorAction Stop
    if ($hc.StatusCode -eq 200) { $healthOk = $true; break }
  } catch {}
}
if (-not $healthOk) {
  Write-Host "ML API did not become healthy. Please check dependencies and try again." -ForegroundColor Red
}

# Start webapp dev server in background
Write-Host "Starting Next.js dev server on 0.0.0.0:3000..." -ForegroundColor Cyan
Push-Location .\webapp
$webProcess = Start-Process -WindowStyle Hidden -PassThru -FilePath "npm" -ArgumentList "run dev:lan"
Pop-Location

# Wait for web server to be ready
Write-Host "Waiting for web server to start..." -ForegroundColor Cyan
Start-Sleep -Seconds 5

# Start localtunnel for HTTPS access
Write-Host "Starting localtunnel (secure HTTPS tunnel)..." -ForegroundColor Cyan
Write-Host ""
npx localtunnel --port 3000

# Cleanup on exit
Write-Host ""
Write-Host "Stopping services..." -ForegroundColor Yellow
Stop-Process -InputObject $apiProcess -ErrorAction SilentlyContinue
Stop-Process -InputObject $webProcess -ErrorAction SilentlyContinue
Write-Host "Done." -ForegroundColor Green
