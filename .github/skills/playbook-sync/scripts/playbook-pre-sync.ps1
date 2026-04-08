# playbook-pre-sync.ps1 — Prepare a remote repository for playbook sync.
#
# Clones (or updates) the target repo, sets up the branch, and outputs
# the playbook output path on the last line of stdout.
#
# Usage:  .\scripts\playbook-pre-sync.ps1 -RepoUrl <github-repo-url>
# Output: The absolute path to the playbook/ directory (last line of stdout)
#
# Exit codes:
#   0 — success
#   1 — clone/pull failed
#   2 — authentication failed
#   3 — branch setup failed
#
# Requires: git, gh (GitHub CLI)

[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [string]$RepoUrl
)

$ErrorActionPreference = 'Stop'
$Branch = 'modernize/playbook-sync'

# Ensure GITHUB_TOKEN is set for gh CLI (needed when running in agent terminals)
if (-not $env:GITHUB_TOKEN -and (Get-Command 'gh' -ErrorAction SilentlyContinue)) {
    try { $env:GITHUB_TOKEN = & gh auth token 2>$null } catch {}
}

# --- Derive temp path ---
$repoName = ($RepoUrl -replace '.*/', '' -replace '\.git$', '').Trim('/')
$TempDir = [System.IO.Path]::GetTempPath()
$RepoDir = Join-Path $TempDir 'modernize-playbook-sync' $repoName

# --- Clone or update ---
if (Test-Path (Join-Path $RepoDir '.git')) {
    Write-Host "Updating existing clone at $RepoDir..." -ForegroundColor Yellow
    Push-Location $RepoDir
    try {
        # Reset to default branch before pulling
        $defaultBranch = git remote show origin 2>$null | Select-String 'HEAD branch' | ForEach-Object { ($_ -split '\s+')[-1] }
        if ($defaultBranch) {
            git checkout $defaultBranch 2>$null
        }
        $pullOutput = git pull --ff-only 2>&1
        if ($LASTEXITCODE -ne 0) {
            Write-Host "ERROR: Failed to update repository. Retrying with fresh clone..." -ForegroundColor Red
            Pop-Location
            Remove-Item -Recurse -Force $RepoDir
        }
    }
    catch {
        Pop-Location
        Remove-Item -Recurse -Force $RepoDir -ErrorAction SilentlyContinue
    }
    finally {
        if ((Get-Location).Path -eq $RepoDir) { Pop-Location }
    }
}

if (-not (Test-Path (Join-Path $RepoDir '.git'))) {
    Write-Host "Cloning $RepoUrl to $RepoDir..." -ForegroundColor Yellow
    $parentDir = Split-Path $RepoDir -Parent
    if (-not (Test-Path $parentDir)) { New-Item -ItemType Directory -Path $parentDir -Force | Out-Null }

    $cloneOutput = gh repo clone $RepoUrl $RepoDir 2>&1
    if ($LASTEXITCODE -ne 0) {
        Write-Host "ERROR: Failed to clone repository. Verify the URL is correct and accessible: $RepoUrl" -ForegroundColor Red
        exit 1
    }
}

Push-Location $RepoDir

# --- Branch strategy ---
# Check for existing open PR for modernize/playbook-sync
try {
    $existingPr = gh pr list --repo $RepoUrl --head $Branch --state open --json url --limit 1 2>$null
}
catch {
    $existingPr = '[]'
}

if ($existingPr -and $existingPr -match '"url"') {
    # Open PR exists — checkout existing branch and pull latest
    $prUrl = ($existingPr | ConvertFrom-Json)[0].url
    Write-Host "Found existing open PR: $prUrl" -ForegroundColor Yellow
    Write-Host "Checking out branch $Branch..." -ForegroundColor Yellow

    git fetch origin $Branch 2>&1 | Out-Null
    if ($LASTEXITCODE -ne 0) {
        Write-Host "ERROR: Failed to fetch branch $Branch." -ForegroundColor Red
        Pop-Location
        exit 3
    }
    git checkout $Branch 2>&1 | Out-Null
    if ($LASTEXITCODE -ne 0) {
        Write-Host "ERROR: Failed to checkout branch $Branch." -ForegroundColor Red
        Pop-Location
        exit 3
    }
    git pull 2>&1 | Out-Null
    Write-Host "Checked out existing branch $Branch" -ForegroundColor Green
}
else {
    # No open PR — create new branch from default branch
    Write-Host "No existing open PR. Creating new branch $Branch..." -ForegroundColor Yellow

    # Delete local branch if it exists (leftover from a previous merged PR)
    git branch -D $Branch 2>$null
    # Delete remote tracking branch if it exists
    git push origin --delete $Branch 2>$null

    git checkout -b $Branch 2>&1 | Out-Null
    if ($LASTEXITCODE -ne 0) {
        Write-Host "ERROR: Failed to create branch $Branch. Verify you have push access to this repository." -ForegroundColor Red
        Pop-Location
        exit 3
    }
    Write-Host "Created branch $Branch" -ForegroundColor Green
}

# --- Ensure playbook directory exists ---
$PlaybookDir = Join-Path $RepoDir 'playbook'
if (-not (Test-Path $PlaybookDir)) { New-Item -ItemType Directory -Path $PlaybookDir -Force | Out-Null }

Pop-Location

# --- Output the playbook path (last line, read by SKILL.md) ---
Write-Output $PlaybookDir
