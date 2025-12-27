param(
  [string]$Message = "chore: auto publish",
  [string]$Branch = "main"
)

$ErrorActionPreference = "Stop"

# Initialize repo if needed
if (-not (git rev-parse --is-inside-work-tree 2>$null)) {
  git init
}

# Ensure default branch
try {
  git rev-parse --verify $Branch 2>$null | Out-Null
} catch {
  git checkout -b $Branch
}

# Add files & commit if changes
$changes = git status --porcelain
if (-not [string]::IsNullOrWhiteSpace($changes)) {
  git add -A
  git commit -m $Message
} else {
  Write-Host "No changes to commit"
}

# Push if remote exists
$remotes = git remote
if ([string]::IsNullOrWhiteSpace($remotes)) {
  Write-Host "No git remote configured. Add one:
  git remote add origin https://github.com/<username>/<repo>.git"
  exit 0
}

git push -u origin $Branch
