param(
    [Parameter(Mandatory = $true)]
    [string]$SpaceRepoUrl,

    [string]$HfUsername,

    [string]$HfToken,

    [string]$Branch = "main",

    [string]$CommitMessage = "Deploy Sentinel-Net backend to HF Space"
)

$ErrorActionPreference = "Stop"

function Assert-Command {
    param([string]$Name)
    if (-not (Get-Command $Name -ErrorAction SilentlyContinue)) {
        throw "Required command '$Name' is not available in PATH."
    }
}

function Invoke-Git {
    param(
        [Parameter(ValueFromRemainingArguments = $true)]
        [string[]]$Args
    )

    & git @Args
    if ($LASTEXITCODE -ne 0) {
        throw "git $($Args -join ' ') failed with exit code $LASTEXITCODE"
    }
}

Assert-Command -Name "git"

$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$backendDir = Join-Path $repoRoot "backend"

$requiredFiles = @(
    "main.py",
    "github_analyzer.py",
    "ml_models.py",
    "ml_risk_model.py",
    "nlp_processor.py",
    "realtime_handler.py",
    "requirements.txt",
    "Dockerfile.hf"
)

foreach ($f in $requiredFiles) {
    $p = Join-Path $backendDir $f
    if (-not (Test-Path $p)) {
        throw "Missing required backend file: $p"
    }
}

$tempRoot = Join-Path $env:TEMP ("sentinel-hf-space-" + (Get-Date -Format "yyyyMMddHHmmss"))
$spaceWorkDir = Join-Path $tempRoot "space"

Write-Host "Creating temp workspace: $tempRoot"
New-Item -ItemType Directory -Path $tempRoot -Force | Out-Null

Write-Host "Cloning Space repo: $SpaceRepoUrl"
Invoke-Git clone --branch $Branch $SpaceRepoUrl $spaceWorkDir

if (-not (Test-Path (Join-Path $spaceWorkDir ".git"))) {
    throw "Clone failed. Could not find .git in $spaceWorkDir"
}

Write-Host "Cleaning existing Space files (keeping .git)"
Get-ChildItem -Path $spaceWorkDir -Force | Where-Object { $_.Name -ne ".git" } | Remove-Item -Recurse -Force

Write-Host "Copying backend files"
Copy-Item (Join-Path $backendDir "main.py") $spaceWorkDir
Copy-Item (Join-Path $backendDir "github_analyzer.py") $spaceWorkDir
Copy-Item (Join-Path $backendDir "ml_models.py") $spaceWorkDir
Copy-Item (Join-Path $backendDir "ml_risk_model.py") $spaceWorkDir
Copy-Item (Join-Path $backendDir "nlp_processor.py") $spaceWorkDir
Copy-Item (Join-Path $backendDir "realtime_handler.py") $spaceWorkDir
Copy-Item (Join-Path $backendDir "requirements.txt") $spaceWorkDir

Copy-Item (Join-Path $backendDir "Dockerfile.hf") (Join-Path $spaceWorkDir "Dockerfile")

if (Test-Path (Join-Path $backendDir "data")) {
    Copy-Item (Join-Path $backendDir "data") $spaceWorkDir -Recurse
}

if (Test-Path (Join-Path $backendDir "models")) {
    Copy-Item (Join-Path $backendDir "models") $spaceWorkDir -Recurse
}

@"
---
title: Sentinel-Net Backend
emoji: 🚀
colorFrom: blue
colorTo: cyan
sdk: docker
app_port: 7860
pinned: false
---

FastAPI backend for Sentinel-Net.

Required Space secret:
- GITHUB_TOKEN
"@ | Set-Content -Path (Join-Path $spaceWorkDir "README.md") -Encoding UTF8

Push-Location $spaceWorkDir
try {
    if ($HfToken) {
        if (-not $HfUsername) {
            throw "-HfUsername is required when -HfToken is provided."
        }

        $authedRepoUrl = $SpaceRepoUrl -replace "https://", ("https://" + $HfUsername + ":" + $HfToken + "@")
        Invoke-Git remote set-url origin $authedRepoUrl
    }

    Invoke-Git add .

    $changes = git status --porcelain
    if (-not $changes) {
        Write-Host "No changes to commit. Space is already up to date."
        return
    }

    Invoke-Git commit -m $CommitMessage
    Invoke-Git push origin $Branch
}
finally {
    if ($HfToken) {
        try {
            Invoke-Git remote set-url origin $SpaceRepoUrl
        } catch {
            Write-Warning "Could not restore non-authenticated origin URL in temp clone."
        }
    }

    Pop-Location
}

Write-Host ""
Write-Host "Deployment push complete."
Write-Host "Next steps:"
Write-Host "1) Open your Space settings and add secret: GITHUB_TOKEN"
Write-Host "2) Wait for Space build to complete"
Write-Host "3) Test: https://<your-space>.hf.space/api/health"
