# Robust startup for ML API + Next.js website with health checks
param(
    [int]$ApiPort = 8000,
    [int]$WebPort = 3000,
    [switch]$Lan
)

Write-Host "=== Starting Allergen Detection Services ===" -ForegroundColor Cyan
$root = Get-Location

# Resolve python path (prefer workspace venv)
$pythonPath = Join-Path $root ".venv/Scripts/python.exe"
if (-not (Test-Path $pythonPath)) { $pythonPath = "python" }

# API args
$apiHost = "127.0.0.1"
if ($Lan.IsPresent) { $apiHost = "0.0.0.0" }
$apiArgs = "-m src.api.allergen_api --host $apiHost --port $ApiPort"

Write-Host "Starting ML API on ${apiHost}:${ApiPort} ..." -ForegroundColor Green
$api = Start-Process -WindowStyle Hidden -PassThru -FilePath $pythonPath -ArgumentList $apiArgs -WorkingDirectory $root

# Probe health with retries
$healthUrl = "http://localhost:$ApiPort/health"
$ok = $false
for ($i = 0; $i -lt 15; $i++) {
  Start-Sleep -Seconds 2
  try {
    $r = Invoke-WebRequest -Uri $healthUrl -UseBasicParsing -TimeoutSec 3 -ErrorAction Stop
    if ($r.StatusCode -eq 200) { $ok = $true; break }
  } catch {}
}
if (-not $ok) {
  Write-Host "ML API failed health checks at $healthUrl. Check dependencies or run from venv." -ForegroundColor Red
  Write-Host "Stopping API process..." -ForegroundColor Yellow
  Stop-Process -Id $api.Id -ErrorAction SilentlyContinue
  exit 1
}
Write-Host "ML API healthy." -ForegroundColor Green

# Start webapp
# Resolve npm to a runnable shim (prefer npm.cmd over npm.ps1 to avoid Win32 errors)
$npmCmd = (Get-Command npm.cmd -ErrorAction SilentlyContinue)?.Source
if (-not $npmCmd) { $npmCmd = (Get-Command npm -ErrorAction SilentlyContinue)?.Source }
if (-not $npmCmd) {
  Write-Host "npm not found in PATH. Install Node.js or reload your shell." -ForegroundColor Red
  Stop-Process -Id $api.Id -ErrorAction SilentlyContinue
  exit 1
}

$webCmd = $npmCmd
$webArgs = @("run")
if ($Lan) { $webArgs += "dev:lan" } else { $webArgs += "dev" }
Write-Host "Starting Next.js on port $WebPort ..." -ForegroundColor Green
Push-Location "$root/webapp"

# If npm is a PowerShell script, run via PowerShell; otherwise run directly
if ($webCmd.ToLower().EndsWith(".ps1")) {
  $web = Start-Process -NoNewWindow -PassThru -FilePath "powershell" -ArgumentList @("-ExecutionPolicy","Bypass","-File", $webCmd) + $webArgs -WorkingDirectory "$root/webapp"
} else {
  $web = Start-Process -NoNewWindow -PassThru -FilePath $webCmd -ArgumentList $webArgs -WorkingDirectory "$root/webapp"
}

Pop-Location

# Probe web health so we don't print success on failure
$webUrl = "http://localhost:$WebPort"
$webOk = $false
for ($i = 0; $i -lt 20; $i++) {
  Start-Sleep -Seconds 1
  if ($web.HasExited) { break }
  try {
    $wr = Invoke-WebRequest -Uri $webUrl -UseBasicParsing -TimeoutSec 3 -ErrorAction Stop
    if ($wr.StatusCode -ge 200 -and $wr.StatusCode -lt 500) { $webOk = $true; break }
  } catch {}
}

if (-not $webOk) {
  Write-Host "Next.js failed to start or is unreachable at $webUrl" -ForegroundColor Red
  Write-Host "Stopping services..." -ForegroundColor Yellow
  Stop-Process -Id $api.Id -ErrorAction SilentlyContinue
  Stop-Process -Id $web.Id -ErrorAction SilentlyContinue
  exit 1
}

Write-Host "Services started. API: http://localhost:${ApiPort}  Web: http://localhost:${WebPort}" -ForegroundColor Cyan
Write-Host "Press Ctrl+C in this terminal to stop both services." -ForegroundColor DarkGray

# Wait until user closes terminal, then cleanup
try {
  while ($true) { Start-Sleep -Seconds 1 }
} finally {
  Write-Host "Stopping services..." -ForegroundColor Yellow
  Stop-Process -Id $api.Id -ErrorAction SilentlyContinue
  Stop-Process -Id $web.Id -ErrorAction SilentlyContinue
  Write-Host "Done." -ForegroundColor Green
}