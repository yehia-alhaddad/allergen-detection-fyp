param(
  [int]$IntervalSeconds = 60,
  [string]$Branch = "main"
)

Write-Host "Auto publishing every $IntervalSeconds seconds when changes detected..."

while ($true) {
  try {
    $changes = git status --porcelain
    if (-not [string]::IsNullOrWhiteSpace($changes)) {
      Write-Host "Changes detected; publishing..."
      & powershell -ExecutionPolicy Bypass -File scripts/publish.ps1 -Message "auto: $(Get-Date -Format s)" -Branch $Branch
    }
  } catch {
    Write-Host "Git not initialized; initializing..."
    git init
  }
  Start-Sleep -Seconds $IntervalSeconds
}
