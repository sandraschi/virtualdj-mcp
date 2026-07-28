Param([switch]$Headless)
$SkipFrontend = $Headless

# --- SOTA Headless Standard ---
if ($Headless -and ($Host.UI.RawUI.WindowTitle -notmatch 'Hidden')) {
    Start-Process pwsh -ArgumentList '-NoProfile', '-File', $PSCommandPath, '-Headless' -WindowStyle Hidden
    exit
}
$WindowStyle = if ($Headless) { 'Hidden' } else { 'Normal' }
# ------------------------------

# Webapp Start - Standardized SOTA (Auto-Repaired V2.5)
$ProjectRoot = Split-Path -Parent $PSScriptRoot
$WebPort = 10876
$BackendPort = 10877
$FleetStartPath = Join-Path $ProjectRoot "scripts\FleetStartMode.ps1"
if (-not (Test-Path -LiteralPath $FleetStartPath)) {
    Write-Host "ERROR: Missing vendored launcher helper: $FleetStartPath" -ForegroundColor Red
    exit 1
}
. $FleetStartPath

# 1. Kill any process squatting on the ports
Write-Host "Checking for port squatters on $WebPort and $BackendPort..." -ForegroundColor Yellow
$connections = Get-NetTCPConnection -LocalPort $WebPort, $BackendPort -ErrorAction SilentlyContinue
$pidSet = @{}
foreach ($c in $connections) {
    if ($null -ne $c -and $c.OwningProcess -gt 4) {
        $pidSet[[string]$c.OwningProcess] = $true
    }
}
foreach ($pidKey in $pidSet.Keys) {
    $p = [int]$pidKey
    Write-Host "Found squatter (PID: $p). Terminating..." -ForegroundColor Red
    try { Stop-Process -Id $p -Force -ErrorAction Stop } catch { Write-Host "Warning: Could not terminate PID $p." -ForegroundColor Gray }
}

# 2. Setup
Set-Location $PSScriptRoot
$PkgManager = "npm"
if (Get-Command bun -ErrorAction SilentlyContinue) {
    $PkgManager = "bun"
}
Write-Host "Using package manager: $PkgManager" -ForegroundColor Gray
if (-not (Test-Path "node_modules")) {
    if ($PkgManager -eq "bun") { bun install } else { npm install }
}

# 3. Start the Python backend (Background)
Write-Host "Starting Python backend on port $BackendPort ..." -ForegroundColor Cyan

# VDJ_OSC_PORT is required by the server (config.from_env). Must match VirtualDJ Settings ├óÔÇáÔÇÖ OSC or control breaks.
$OscPort = if ($env:VDJ_OSC_PORT -and $env:VDJ_OSC_PORT.Trim()) { $env:VDJ_OSC_PORT.Trim() } else { "40100" }
Write-Host "VDJ_OSC_PORT=$OscPort (set env VDJ_OSC_PORT to match VirtualDJ; required)" -ForegroundColor DarkGray

# Backend (virtualdj_mcp) lives in repo root src/virtualdj_mcp; run from ProjectRoot so uv + imports match pyproject/lock
# (running from web_sota alone can bind the wrong env or an older install ├óÔé¼ÔÇØ uvicorn then fails: Attribute "app" not found)
$backendCmd = "`$env:VDJ_OSC_PORT = '$OscPort'; `$env:PYTHONPATH = '$ProjectRoot;$ProjectRoot\src'; Set-Location '$ProjectRoot'; uv run --project '$ProjectRoot' uvicorn virtualdj_mcp.server:app --host 127.0.0.1 --port $BackendPort --log-level info"

Start-Process powershell -ArgumentList "-NoExit", "-Command", $backendCmd -WindowStyle Normal

# 4. Open the webapp in a browser once backend + frontend are reachable
$webUrl = "http://127.0.0.1:$WebPort/"
$healthUrl = "http://127.0.0.1:$BackendPort/health"

$openCmd = @"
`$ErrorActionPreference = 'SilentlyContinue'
`$webUrl = '$webUrl'
`$healthUrl = '$healthUrl'

function Test-HttpOk([string]`$Url, [int]`$TimeoutSec) {
    try {
        `$r = Invoke-WebRequest -Uri `$Url -TimeoutSec `$TimeoutSec -Method Get
        if (`$null -ne `$r -and `$r.StatusCode -ge 200 -and `$r.StatusCode -lt 500) { return `$true }
        return `$false
    } catch {
        return `$false
    }
}

`$backendOk = `$false
for (`$i = 0; `$i -lt 120; `$i++) {
    if (Test-HttpOk -Url `$healthUrl -TimeoutSec 2) { `$backendOk = `$true; break }
    Start-Sleep -Seconds 1
}

if (-not `$backendOk) { exit 0 }

`$frontendOk = `$false
for (`$j = 0; `$j -lt 120; `$j++) {
    if (Test-HttpOk -Url `$webUrl -TimeoutSec 2) { `$frontendOk = `$true; break }
    Start-Sleep -Seconds 1
}

if (`$frontendOk) { Start-Process `$webUrl }
"@

$null = Start-Process powershell -ArgumentList "-WindowStyle", "Hidden", "-Command", $openCmd

# 5. Run server (Vite dev)
Write-Host "Starting Vite frontend on port $WebPort ..." -ForegroundColor Green

# 4b. Launch background task to open browser once frontend is ready (Auto-opened by Antigravity)
$frontendUrl = "http://127.0.0.1:$WebPort/"
$pollAndOpen = "for (`$i = 0; `$i -lt 60; `$i++) { try { `$null = Invoke-WebRequest -Uri '$frontendUrl' -TimeoutSec 2 -UseBasicParsing -ErrorAction Stop; Start-Process '$frontendUrl'; exit } catch { Start-Sleep -Seconds 1 } }"
Start-Process powershell -ArgumentList "-NoProfile", "-WindowStyle", "Hidden", "-Command", $pollAndOpen

Write-Host "Browser will open automatically when Vite is ready." -ForegroundColor Gray
if ($SkipFrontend) { return }
if ($PkgManager -eq "bun") {
    bun run dev -- --port $WebPort --host
} else {
    npm run dev -- --port $WebPort --host
}
