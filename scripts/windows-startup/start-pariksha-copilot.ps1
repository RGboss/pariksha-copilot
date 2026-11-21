# ==============================================================================
# Pariksha Copilot - Automated Windows Startup Script
# Repository: https://github.com/RGboss/pariksha-copilot
# Log Target: %USERPROFILE%\pariksha-copilot-startup.log
# ==============================================================================

[CmdletBinding()]
param (
    [string]$RepoPath = (Resolve-Path "$PSScriptRoot\..\..").Path,
    [string]$TargetUrl = "http://localhost:8082/health",
    [int]$MaxWaitSeconds = 120
)

$ErrorActionPreference = "Continue"
$LogFile = Join-Path $env:USERPROFILE "pariksha-copilot-startup.log"

function Write-Log {
    param([string]$Message, [string]$Level = "INFO")
    $Timestamp = (Get-Date).ToString("yyyy-MM-dd HH:mm:ss")
    $LogLine = "[$Timestamp] [$Level] $Message"
    Write-Host $LogLine
    Add-Content -Path $LogFile -Value $LogLine -Encoding utf8
}

Write-Log "================================================================="
Write-Log "Starting Pariksha Copilot Startup Routine"
Write-Log "Target Repository: $RepoPath"

# 1. Ensure Docker Desktop is Running
Write-Log "Step 1: Checking Docker Desktop process..."
$DockerProcess = Get-Process -Name "Docker Desktop" -ErrorAction SilentlyContinue

if (-not $DockerProcess) {
    $DockerExe = "C:\Program Files\Docker\Docker\Docker Desktop.exe"
    if (Test-Path $DockerExe) {
        Write-Log "Launching Docker Desktop from: $DockerExe"
        Start-Process $DockerExe
    } else {
        Write-Log "Docker Desktop executable not found in default path." "WARN"
    }
} else {
    Write-Log "Docker Desktop process is already running (PID: $($DockerProcess.Id))."
}

# 2. Wait for Docker Daemon to respond
Write-Log "Step 2: Checking Docker daemon availability..."
$DockerReady = $false
$DockerWaitSeconds = 45
$Elapsed = 0

while ($Elapsed -lt $DockerWaitSeconds) {
    try {
        $DockerInfo = & docker info 2>&1
        if ($LASTEXITCODE -eq 0) {
            $DockerReady = $true
            Write-Log "Docker daemon is online and responsive."
            break
        }
    } catch {
        # continue waiting
    }
    Start-Sleep -Seconds 3
    $Elapsed += 3
}

# 3. Launch Stack via Docker Compose (or Fallback if Hyper-V is disabled)
Set-Location $RepoPath
$LaunchSuccess = $false

if ($DockerReady) {
    Write-Log "Step 3: Running 'docker compose up -d' in $RepoPath..."
    $ComposeOutput = & docker compose up -d 2>&1
    Write-Log "Docker Compose Output: $($ComposeOutput -join ' ')"
    if ($LASTEXITCODE -eq 0) {
        $LaunchSuccess = $true
    } else {
        Write-Log "Docker Compose command failed. Checking fallback..." "WARN"
    }
} else {
    Write-Log "Docker daemon not ready (WSL2/Hyper-V virtualization might be inactive)." "WARN"
}

if (-not $LaunchSuccess) {
    Write-Log "Step 3b (Fallback): Checking if local server daemon is active on port 8000..."
    try {
        $LocalCheck = Invoke-WebRequest -Uri "http://localhost:8000/health" -UseBasicParsing -TimeoutSec 3 -ErrorAction SilentlyContinue
        if ($LocalCheck -and $LocalCheck.StatusCode -eq 200) {
            Write-Log "Local fallback server is active on http://localhost:8000"
            $TargetUrl = "http://localhost:8000/health"
            $LaunchSuccess = $true
        } else {
            Write-Log "Starting local background server via Python..."
            Start-Process -FilePath "python" -ArgumentList "-m uvicorn backend.server:app --host 127.0.0.1 --port 8000" -WorkingDirectory $RepoPath -WindowStyle Hidden
            $TargetUrl = "http://localhost:8000/health"
            $LaunchSuccess = $true
        }
    } catch {
        Write-Log "Could not start local fallback server: $_" "ERROR"
    }
}

# 4. Poll Health Endpoint until HTTP 200
Write-Log "Step 4: Polling health endpoint: $TargetUrl (Timeout: ${MaxWaitSeconds}s)..."
$Healthy = $false
$PollElapsed = 0

while ($PollElapsed -lt $MaxWaitSeconds) {
    try {
        $Response = Invoke-WebRequest -Uri $TargetUrl -UseBasicParsing -TimeoutSec 5 -ErrorAction Stop
        if ($Response.StatusCode -eq 200) {
            $Healthy = $true
            Write-Log "SUCCESS: Health check passed with HTTP 200 from $TargetUrl."
            Write-Log "Response Content: $($Response.Content)"
            break
        }
    } catch {
        # Endpoint not ready yet
    }
    Start-Sleep -Seconds 3
    $PollElapsed += 3
}

if ($Healthy) {
    Write-Log "Pariksha Copilot startup completed successfully."
    Write-Log "Web Gateway is accessible."
} else {
    Write-Log "WARNING: Health check did not return HTTP 200 within ${MaxWaitSeconds} seconds." "WARN"
    Write-Log "Please inspect logs via 'docker compose logs' or check $LogFile." "WARN"
}

Write-Log "================================================================="
