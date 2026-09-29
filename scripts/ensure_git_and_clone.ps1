<#
PowerShell helper: ensure Git is installed and clone luci_tooling_omzsh into third_party/
Usage (run from repo root):
  .\scripts\ensure_git_and_clone.ps1
#>
param(
    [string]$RepoUrl = 'https://github.com/luci-digital/lucia_tooling_omzsh.git',
    [string]$DestDir = 'third_party/lucia_tooling_omzsh'
)

Set-StrictMode -Version Latest

$scriptRoot = Split-Path -Parent $MyInvocation.MyCommand.Definition
Push-Location $scriptRoot
# move to repo root
Set-Location (Resolve-Path "..")

Write-Host "Repo root: $(Get-Location)"

if (Test-Path $DestDir) {
    Write-Host "Target path '$DestDir' already exists. Aborting." -ForegroundColor Yellow
    Pop-Location
    exit 0
}

function Install-Git {
    Write-Host "Git not found. Attempting to install..."
    if (Get-Command winget -ErrorAction SilentlyContinue) {
        Write-Host "Using winget to install Git..."
        winget install --id Git.Git -e --source winget
        return $?
    }
    if (Get-Command choco -ErrorAction SilentlyContinue) {
        Write-Host "Using Chocolatey to install Git..."
        choco install git -y
        return $?
    }
    Write-Host "No supported package manager found (winget/choco). Please install Git for Windows manually:" -ForegroundColor Red
    Write-Host "  https://git-scm.com/download/win"
    return $false
}

$git = Get-Command git -ErrorAction SilentlyContinue
if (-not $git) {
    $ok = Install-Git
    if (-not $ok) { Pop-Location; exit 1 }
}

# verify git now
try {
    $version = & git --version
    Write-Host "Found: $version"
} catch {
    Write-Host "git still not available after install attempt." -ForegroundColor Red
    Pop-Location
    exit 1
}

# If repo root is a git working tree, prefer adding as submodule
$inside = $false
try {
    $inside = (& git rev-parse --is-inside-work-tree) -eq 'true'
} catch { $inside = $false }

if ($inside) {
    Write-Host "Adding as git submodule: $RepoUrl -> $DestDir"
    & git submodule add $RepoUrl $DestDir
    if ($LASTEXITCODE -ne 0) { Write-Host "git submodule add failed" -ForegroundColor Red; Pop-Location; exit 1 }
    & git submodule update --init --recursive $DestDir
} else {
    Write-Host "Cloning repository into $DestDir"
    & git clone $RepoUrl $DestDir
    if ($LASTEXITCODE -ne 0) { Write-Host "git clone failed" -ForegroundColor Red; Pop-Location; exit 1 }
}

Write-Host "Clone complete: $DestDir" -ForegroundColor Green
Pop-Location
return 0
