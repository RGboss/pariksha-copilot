# ==============================================================================
# Pariksha Copilot - Unregister Windows Startup Task Scheduler Job
# Task Name: ParikshaCopilotAutoStart
# ==============================================================================

[CmdletBinding()]
param ()

$TaskName = "ParikshaCopilotAutoStart"

Write-Host "=================================================================" -ForegroundColor Cyan
Write-Host " Pariksha Copilot - Unregister Startup Task" -ForegroundColor Cyan
Write-Host "=================================================================" -ForegroundColor Cyan

$ExistingTask = Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue

if ($ExistingTask) {
    try {
        Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false
        Write-Host "SUCCESS: Scheduled task '$TaskName' has been cleanly removed." -ForegroundColor Green
    } catch {
        Write-Error "Failed to unregister scheduled task '$TaskName': $_"
    }
} else {
    Write-Host "Task '$TaskName' is not currently registered in Windows Task Scheduler." -ForegroundColor Yellow
}
