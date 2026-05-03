param(
    [string]$BaseUrl = "http://127.0.0.1:8000",
    [string]$ComposeFile = "compose.yaml",
    [string]$EnvFile = ".env",
    [string]$SmokeUser = "",
    [string]$SmokePassword = "",
    [switch]$KeepRunning
)

$ErrorActionPreference = "Stop"

function Require-Command {
    param([string]$Name)
    if (-not (Get-Command $Name -ErrorAction SilentlyContinue)) {
        throw "Required command not found: $Name"
    }
}

Require-Command python
Require-Command docker

$composeArgs = @("compose", "-f", $ComposeFile)
if (Test-Path $EnvFile) {
    $composeArgs += @("--env-file", $EnvFile)
}

Write-Host "[smoke-compose] starting compose stack..."
& docker @composeArgs up -d --build

try {
    $deadline = (Get-Date).AddMinutes(5)
    do {
        Start-Sleep -Seconds 2
        try {
            $resp = Invoke-WebRequest -Uri "$BaseUrl/api/health/ready" -UseBasicParsing -TimeoutSec 5
            if ($resp.StatusCode -eq 200) {
                Write-Host "[smoke-compose] readiness check passed"
                break
            }
        } catch {
        }
    } while ((Get-Date) -lt $deadline)

    if ((Get-Date) -ge $deadline) {
        throw "Timed out waiting for $BaseUrl/api/health/ready"
    }

    $scriptArgs = @("scripts/smoke_async_flow.py", "--base-url", $BaseUrl)
    if ($SmokeUser) {
        $scriptArgs += @("--username", $SmokeUser)
    }
    if ($SmokePassword) {
        $scriptArgs += @("--password", $SmokePassword)
    }

    Write-Host "[smoke-compose] running async smoke flow..."
    & python @scriptArgs
    if ($LASTEXITCODE -ne 0) {
        throw "Smoke script failed with exit code $LASTEXITCODE"
    }
    Write-Host "[smoke-compose] smoke flow passed"
} finally {
    if (-not $KeepRunning) {
        Write-Host "[smoke-compose] stopping compose stack..."
        & docker @composeArgs down
    } else {
        Write-Host "[smoke-compose] keeping compose stack running"
    }
}
