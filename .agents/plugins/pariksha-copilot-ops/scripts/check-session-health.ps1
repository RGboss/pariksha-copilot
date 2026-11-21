# ==============================================================================
# Pariksha Copilot - SessionStart Health Diagnostic Hook
# ==============================================================================

$ErrorActionPreference = "SilentlyContinue"

$Port8082Healthy = $false
$Port8000Healthy = $false
$ActiveUrl = ""

# 1. Probe Port 8082 (Nginx Gateway)
try {
    $res8082 = Invoke-WebRequest -Uri "http://localhost:8082/health" -UseBasicParsing -TimeoutSec 3 -ErrorAction Stop
    if ($res8082.StatusCode -eq 200) {
        $Port8082Healthy = $true
        $ActiveUrl = "http://localhost:8082"
    }
} catch {
    # Nginx not responding
}

# 2. Probe Port 8000 (Internal Backend)
try {
    $res8000 = Invoke-WebRequest -Uri "http://localhost:8000/health" -UseBasicParsing -TimeoutSec 3 -ErrorAction Stop
    if ($res8000.StatusCode -eq 200) {
        $Port8000Healthy = $true
        if (-not $ActiveUrl) { $ActiveUrl = "http://localhost:8000" }
    }
} catch {
    # Backend direct not responding
}

# 3. Output Status for Agent Context
if ($Port8082Healthy) {
    Write-Host "[Pariksha Copilot Status] Gateway Healthy: $ActiveUrl (Nginx + Backend active, SQLite + ChromaDB ready)"
} elseif ($Port8000Healthy) {
    Write-Host "[Pariksha Copilot Status] Standalone Backend Active: $ActiveUrl (Nginx gateway on 8082 inactive; direct backend serving)"
} else {
    Write-Host "[Pariksha Copilot ALERT] Stack is offline. Neither port 8082 nor 8000 returned HTTP 200."
    Write-Host "Suggested action: Run .\scripts\windows-startup\start-pariksha-copilot.ps1 or 'docker compose up -d'."
}
