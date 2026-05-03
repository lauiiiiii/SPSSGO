param(
    [string]$BaseUrl = "http://127.0.0.1:8000",
    [string]$ComposeFile = "compose.yaml",
    [string]$EnvFile = ".env",
    [string]$SmokeUser = "",
    [string]$SmokePassword = "",
    [string]$UserPrefix = "loaduser",
    [string]$UserPassword = "",
    [int]$FullChainUserCount = 1000,
    [int]$FullChainVUs = 20,
    [string]$FullChainDuration = "5m",
    [int]$AnalysisUserCount = 50,
    [int]$AnalysisVUs = 50,
    [string]$AnalysisDuration = "10m",
    [string]$ReportDir = "acceptance_refs/validation",
    [switch]$WithMonitoring,
    [switch]$SkipSmoke,
    [switch]$SkipLoad,
    [switch]$KeepRunning
)

$ErrorActionPreference = "Stop"

function Require-Command {
    param([string]$Name)
    if (-not (Get-Command $Name -ErrorAction SilentlyContinue)) {
        throw "Required command not found: $Name"
    }
}

function Read-EnvFile {
    param([string]$Path)

    $values = @{}
    if (-not (Test-Path $Path)) {
        return $values
    }

    foreach ($line in Get-Content $Path) {
        $trimmed = $line.Trim()
        if (-not $trimmed -or $trimmed.StartsWith("#")) {
            continue
        }
        $parts = $trimmed.Split("=", 2)
        if ($parts.Count -ne 2) {
            continue
        }
        $values[$parts[0].Trim()] = $parts[1].Trim()
    }
    return $values
}

function Wait-Ready {
    param(
        [string]$TargetUrl,
        [int]$TimeoutSeconds = 300
    )

    $deadline = (Get-Date).AddSeconds($TimeoutSeconds)
    do {
        Start-Sleep -Seconds 2
        try {
            $resp = Invoke-WebRequest -Uri "$TargetUrl/api/health/ready" -UseBasicParsing -TimeoutSec 5
            if ($resp.StatusCode -eq 200) {
                Write-Host "[compose-validation] readiness check passed"
                return
            }
        } catch {
        }
    } while ((Get-Date) -lt $deadline)

    throw "Timed out waiting for $TargetUrl/api/health/ready"
}

Require-Command python
Require-Command docker
Require-Command k6

if (-not $SmokePassword -and -not $SkipSmoke) {
    throw "Please provide -SmokePassword for compose smoke validation."
}
if (-not $UserPassword -and -not $SkipLoad) {
    throw "Please provide -UserPassword for compose load validation."
}

$envValues = Read-EnvFile -Path $EnvFile

$composeArgs = @("compose", "-f", $ComposeFile)
if (Test-Path $EnvFile) {
    $composeArgs += @("--env-file", $EnvFile)
}
if ($WithMonitoring) {
    $composeArgs += @("--profile", "monitoring")
}

Write-Host "[compose-validation] starting compose stack..."
& docker @composeArgs up -d --build

try {
    Wait-Ready -TargetUrl $BaseUrl
    New-Item -ItemType Directory -Path $ReportDir -Force | Out-Null

    if (-not $SkipSmoke) {
        Write-Host "[compose-validation] running compose smoke..."
        $smokeArgs = @("scripts/smoke_async_flow.py", "--base-url", $BaseUrl, "--password", $SmokePassword)
        if ($SmokeUser) {
            $smokeArgs += @("--username", $SmokeUser)
        }
        & python @smokeArgs
        if ($LASTEXITCODE -ne 0) {
            throw "Compose smoke failed with exit code $LASTEXITCODE"
        }
    }

    if (-not $SkipLoad) {
        Write-Host "[compose-validation] ensuring load-test users exist..."
        $mysqlHostPort = if ($envValues.ContainsKey("MYSQL_HOST_PORT")) { $envValues["MYSQL_HOST_PORT"] } else { "3307" }
        $mysqlUser = if ($envValues.ContainsKey("MYSQL_USER")) { $envValues["MYSQL_USER"] } else { "spssgo" }
        $mysqlPassword = if ($envValues.ContainsKey("MYSQL_PASSWORD")) { $envValues["MYSQL_PASSWORD"] } else { "" }
        $mysqlDatabase = if ($envValues.ContainsKey("MYSQL_DATABASE")) { $envValues["MYSQL_DATABASE"] } else { "data_analysis" }
        $bootstrapEnv = @{
            MYSQL_HOST = "127.0.0.1"
            MYSQL_PORT = $mysqlHostPort
            MYSQL_USER = $mysqlUser
            MYSQL_PASSWORD = $mysqlPassword
            MYSQL_DATABASE = $mysqlDatabase
        }
        $originalEnv = @{}
        foreach ($item in $bootstrapEnv.GetEnumerator()) {
            $originalEnv[$item.Key] = [Environment]::GetEnvironmentVariable($item.Key)
            [Environment]::SetEnvironmentVariable($item.Key, $item.Value)
        }
        try {
            & python scripts/bootstrap_load_users.py --prefix $UserPrefix --count $FullChainUserCount --password $UserPassword
            if ($LASTEXITCODE -ne 0) {
                throw "bootstrap_load_users failed with exit code $LASTEXITCODE"
            }
        } finally {
            foreach ($item in $originalEnv.GetEnumerator()) {
                [Environment]::SetEnvironmentVariable($item.Key, $item.Value)
            }
        }

        $fullChainSummary = Join-Path $ReportDir "compose_k6_stability_full_chain.json"
        Write-Host "[compose-validation] running full_chain stability scenario..."
        & powershell -ExecutionPolicy Bypass -File scripts/run-k6-baseline.ps1 `
            -BaseUrl $BaseUrl `
            -UserPrefix $UserPrefix `
            -UserPassword $UserPassword `
            -UserCount $FullChainUserCount `
            -VUs $FullChainVUs `
            -Duration $FullChainDuration `
            -FlowMode "full_chain" `
            -UserSelection "iteration_round_robin" `
            -SummaryExport $fullChainSummary
        if ($LASTEXITCODE -ne 0) {
            throw "full_chain k6 scenario failed with exit code $LASTEXITCODE"
        }

        $analysisSummary = Join-Path $ReportDir "compose_k6_target_50vu_reuse_dataset.json"
        Write-Host "[compose-validation] running reuse_dataset analysis scenario..."
        & powershell -ExecutionPolicy Bypass -File scripts/run-k6-baseline.ps1 `
            -BaseUrl $BaseUrl `
            -UserPrefix $UserPrefix `
            -UserPassword $UserPassword `
            -UserCount $AnalysisUserCount `
            -VUs $AnalysisVUs `
            -Duration $AnalysisDuration `
            -FlowMode "reuse_dataset" `
            -UserSelection "vu_sticky" `
            -SummaryExport $analysisSummary
        if ($LASTEXITCODE -ne 0) {
            throw "reuse_dataset k6 scenario failed with exit code $LASTEXITCODE"
        }
    }

    Write-Host "[compose-validation] validation flow completed"
} finally {
    if (-not $KeepRunning) {
        Write-Host "[compose-validation] stopping compose stack..."
        & docker @composeArgs down
    } else {
        Write-Host "[compose-validation] keeping compose stack running"
    }
}
