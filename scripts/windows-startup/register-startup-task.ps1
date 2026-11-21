# ==============================================================================
# Pariksha Copilot - Register Windows Startup Task Scheduler Job
# Task Name: ParikshaCopilotAutoStart
# Trigger: At Logon (with 30-second delay)
# ==============================================================================

[CmdletBinding()]
param (
    [string]$RepoPath = (Resolve-Path "$PSScriptRoot\..\..").Path,
    [switch]$Force
)

$TaskName = "ParikshaCopilotAutoStart"
$ScriptToRun = Join-Path $RepoPath "scripts\windows-startup\start-pariksha-copilot.ps1"

Write-Host "=================================================================" -ForegroundColor Cyan
Write-Host " Pariksha Copilot - Startup Task Registration" -ForegroundColor Cyan
Write-Host "=================================================================" -ForegroundColor Cyan
Write-Host "Repository Path: $RepoPath" -ForegroundColor Yellow
Write-Host "Script Target:   $ScriptToRun" -ForegroundColor Yellow
Write-Host "Task Name:       $TaskName" -ForegroundColor Yellow
Write-Host "Trigger:         At User Logon (with 30-second delay)" -ForegroundColor Yellow
Write-Host "-----------------------------------------------------------------"

if (-not (Test-Path $ScriptToRun)) {
    Write-Error "Error: Startup script not found at expected location: $ScriptToRun"
    exit 1
}

# Check if task already exists
$ExistingTask = Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue
if ($ExistingTask) {
    Write-Host "Found existing scheduled task '$TaskName'. Replacing..." -ForegroundColor Magenta
    Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false
}

# Define Action
$Action = New-ScheduledTaskAction `
    -Execute "powershell.exe" `
    -Argument "-ExecutionPolicy Bypass -WindowStyle Hidden -File `"$ScriptToRun`"" `
    -WorkingDirectory $RepoPath

# Define Trigger (At Logon with 30s delay)
$Trigger = New-ScheduledTaskTrigger -AtLogOn
$Trigger.Delay = "PT30S"

# Define Settings
$Settings = New-ScheduledTaskSettingsSet `
    -AllowStartIfOnBatteries `
    -DontStopIfGoingOnBatteries `
    -ExecutionTimeLimit (New-TimeSpan -Minutes 15) `
    -RestartCount 3 `
    -RestartInterval (New-TimeSpan -Minutes 2)

# Define Principal (Current User)
$Principal = New-ScheduledTaskPrincipal -UserId $env:USERNAME -LogonType Interactive

# Register Scheduled Task
try {
    Register-ScheduledTask `
        -TaskName $TaskName `
        -Action $Action `
        -Trigger $Trigger `
        -Settings $Settings `
        -Principal $Principal `
        -Description "Automatically starts Docker Desktop and launches Pariksha Copilot at logon (http://localhost:8082)." | Out-Null

    Write-Host "SUCCESS: Scheduled task '$TaskName' has been registered successfully!" -ForegroundColor Green
    Write-Host "To view task details in PowerShell: Get-ScheduledTask -TaskName '$TaskName'" -ForegroundColor Gray
    Write-Host "To remove this task anytime, run:   .\unregister-startup-task.ps1" -ForegroundColor Gray
} catch {
    Write-Error "Failed to register scheduled task: $_"
}
