#!/usr/bin/env pwsh
<#
.SYNOPSIS
  Release the Smart Irrigation HACS integration.

.DESCRIPTION
  One command for the whole release so the steps can't drift (manual releases
  previously bumped versions in v2026.06.06-.08 but never tagged/published them).

  It will, on a clean and up-to-date master:
    1. bump the version in const.py, manifest.json and frontend/package.json
       (mirrors the Makefile `bump` target),
    2. rebuild the frontend bundle (the version is embedded from package.json,
       so dist MUST be rebuilt and committed — HACS installs the source tree at
       the tag, there is no zip_release),
    3. commit "build: release <version>", create the tag,
    4. push master + tag,
    5. create the GitHub release.

  Version scheme: vYYYY.MM.NN  (NN = sequence within the calendar month).

.PARAMETER Version
  Explicit version, e.g. v2026.06.09. If omitted it is auto-computed from the
  current VERSION in const.py: same calendar month -> NN+1, new month -> .01.

.PARAMETER Notes
  Release notes body. If omitted, GitHub auto-generates notes from merged PRs.

.PARAMETER DryRun
  Print the plan and stop before changing anything.

.EXAMPLE
  pwsh scripts/release.ps1
  pwsh scripts/release.ps1 -Version v2026.07.01
  pwsh scripts/release.ps1 -DryRun
#>
param(
  [string]$Version,
  [string]$Notes,
  [switch]$DryRun
)

$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

# Run a native command and abort the release if it fails.
function Invoke-Checked {
  param([Parameter(Mandatory)][scriptblock]$Cmd)
  & $Cmd
  if ($LASTEXITCODE -ne 0) { throw "Command failed (exit $LASTEXITCODE): $Cmd" }
}

$RepoRoot = Split-Path -Parent $PSScriptRoot
Set-Location $RepoRoot

# The pre-commit hook runs `python -m black/ruff` on staged .py files (const.py
# is bumped here). Put the repo venv first on PATH so the hook finds those tools
# regardless of which python is ambient in the caller's shell.
$venvBin = Join-Path $RepoRoot ".venv/Scripts"   # Windows venv layout
if (-not (Test-Path $venvBin)) { $venvBin = Join-Path $RepoRoot ".venv/bin" }
if (Test-Path $venvBin) {
  $env:PATH = "$venvBin$([IO.Path]::PathSeparator)$env:PATH"
}

# The frontend rebuild shells out to node (via `npx rollup`). node is often
# installed through nvm-windows, whose per-version dirs are NOT on PATH unless
# `nvm use` ran in this shell. If node isn't resolvable, add the newest v22
# install (the version the dist is built with) so the release doesn't fail
# mid-run after already bumping the version files. Prefer v22; fall back to the
# newest available.
if (-not (Get-Command node -ErrorAction SilentlyContinue)) {
  $nvmRoots = @($env:NVM_HOME, "$env:LOCALAPPDATA/nvm", "$env:APPDATA/nvm") |
    Where-Object { $_ -and (Test-Path $_) }
  $nodeVersions = foreach ($root in $nvmRoots) {
    Get-ChildItem -Path $root -Directory -Filter "v*" -ErrorAction SilentlyContinue |
      Where-Object { Test-Path (Join-Path $_.FullName "node.exe") }
  }
  if ($nodeVersions) {
    $pick = $nodeVersions |
      Where-Object { $_.Name -like "v22.*" } |
      Sort-Object { [version]($_.Name.TrimStart("v")) } -Descending |
      Select-Object -First 1
    if (-not $pick) {
      $pick = $nodeVersions |
        Sort-Object { [version]($_.Name.TrimStart("v")) } -Descending |
        Select-Object -First 1
    }
    $env:PATH = "$($pick.FullName)$([IO.Path]::PathSeparator)$env:PATH"
    Write-Host "Using node from $($pick.FullName) (not on PATH; resolved from nvm)" -ForegroundColor DarkGray
  }
}
if (-not (Get-Command node -ErrorAction SilentlyContinue)) {
  throw "node not found on PATH and no nvm install located - install Node (v22) or run 'nvm use 22' first."
}

$ConstPath    = "custom_components/smart_irrigation/const.py"
$ManifestPath = "custom_components/smart_irrigation/manifest.json"
$PkgPath      = "custom_components/smart_irrigation/frontend/package.json"
$FrontendDir  = "custom_components/smart_irrigation/frontend"
$DistRel      = "dist/smart-irrigation.js"
$DistPath     = "$FrontendDir/$DistRel"
$CardRel      = "dist/smart-irrigation-card.js"
$CardPath     = "$FrontendDir/$CardRel"
$ImplRel      = "dist/smart-irrigation-card-impl.js"
$ImplPath     = "$FrontendDir/$ImplRel"

# --- preflight ------------------------------------------------------------
$branch = (git rev-parse --abbrev-ref HEAD).Trim()
if ($branch -ne "master") { throw "Must be on master (currently '$branch')." }
if (git status --porcelain) { throw "Working tree not clean - commit or stash first." }

Invoke-Checked { git fetch origin --tags --quiet }
if ((git rev-parse HEAD).Trim() -ne (git rev-parse origin/master).Trim()) {
  throw "Local master is not in sync with origin/master - pull/push first."
}

# --- current + next version ----------------------------------------------
$constText = Get-Content $ConstPath -Raw
if ($constText -notmatch 'VERSION = "v(\d{4})\.(\d{2})\.(\d+)"') {
  throw "Could not parse current VERSION from $ConstPath"
}
$curY = $Matches[1]; $curM = $Matches[2]; $curN = [int]$Matches[3]
$current = "v{0}.{1}.{2:D2}" -f $curY, $curM, $curN

if (-not $Version) {
  $now = Get-Date
  $y = $now.ToString("yyyy"); $m = $now.ToString("MM")
  $n = if ($y -eq $curY -and $m -eq $curM) { $curN + 1 } else { 1 }
  $Version = "v{0}.{1}.{2:D2}" -f $y, $m, $n
}

if ($Version -notmatch '^v\d{4}\.\d{2}\.\d{2,}$') {
  throw "Version '$Version' must look like vYYYY.MM.NN"
}
if (git tag -l $Version) { throw "Tag $Version already exists." }

$VerNoPrefix = $Version.Substring(1)
Write-Host "Current $current  ->  releasing $Version" -ForegroundColor Cyan
if ($DryRun) { Write-Host "[DryRun] stopping before any changes." -ForegroundColor Yellow; exit 0 }

# --- bump the three files (mirrors Makefile `bump`) -----------------------
(Get-Content $PkgPath -Raw)      -replace '"version":\s*"[^"]*"', ('"version": "{0}"' -f $VerNoPrefix) | Set-Content -NoNewline $PkgPath
(Get-Content $ManifestPath -Raw) -replace '"version":\s*"[^"]*"', ('"version": "{0}"' -f $Version)     | Set-Content -NoNewline $ManifestPath
(Get-Content $ConstPath -Raw)    -replace '(?m)^VERSION = "[^"]*"', ('VERSION = "{0}"' -f $Version)    | Set-Content -NoNewline $ConstPath
Write-Host "Bumped const.py, manifest.json, package.json -> $Version"

# --- rebuild the frontend bundle (embeds version from package.json) -------
Push-Location $FrontendDir
try {
  if (-not (Test-Path node_modules)) { Invoke-Checked { npm ci } }
  Invoke-Checked { npx rollup -c }
} finally { Pop-Location }

# const.ts embeds `v${pkg.version}`, which rollup keeps as `v${"<VerNoPrefix>"}`,
# so the contiguous literal in the bundle is the no-prefix version. Both bundles
# import const.ts, so both must embed it.
foreach ($p in @($DistPath, $CardPath)) {
  if (-not (Select-String -Path $p -Pattern ([regex]::Escape($VerNoPrefix)) -Quiet)) {
    throw "Built bundle $p does not contain $VerNoPrefix - aborting before commit."
  }
}
Write-Host "Frontend rebuilt and verified to embed $Version (panel + card)"

# --- commit, tag, push, release ------------------------------------------
Invoke-Checked { git add $ConstPath $ManifestPath $PkgPath }
Invoke-Checked { git add -f $DistPath $CardPath $ImplPath }   # dist is gitignored but tracked
Invoke-Checked { git commit -m "build: release $Version" }
Invoke-Checked { git tag $Version }
Invoke-Checked { git push origin master }
Invoke-Checked { git push origin $Version }

# --- build the HACS install zip and attach it AT release creation ---------
# Deterministic + atomic: the smart_irrigation.zip asset exists the moment the
# release is published, instead of relying on the post-publish release-zip
# workflow (which fails when no hosted runner is free). `git archive` of the tag
# is exactly the tracked integration tree HACS would otherwise fetch as source
# (no __pycache__/.pyc/node_modules), with the integration files at the zip root.
$ZipPath = Join-Path ([System.IO.Path]::GetTempPath()) "smart_irrigation.zip"
Invoke-Checked { git archive --format=zip -o $ZipPath "${Version}:custom_components/smart_irrigation" }
if ((Get-Item $ZipPath).Length -lt 1024) { throw "Built smart_irrigation.zip looks too small - aborting before release." }
Write-Host "Built smart_irrigation.zip from the $Version tree ($([int]((Get-Item $ZipPath).Length/1024)) KB)"

if ($Notes) {
  Invoke-Checked { gh release create $Version $ZipPath --title $Version --notes $Notes }
} else {
  Invoke-Checked { gh release create $Version $ZipPath --title $Version --generate-notes }
}

Write-Host "Released $Version" -ForegroundColor Green
