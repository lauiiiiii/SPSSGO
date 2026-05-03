param(
    [string]$BaseUrl = "http://127.0.0.1:8000",
    [string]$UserPrefix = "loaduser",
    [string]$UserPassword = "",
    [int]$UserCount = 50,
    [int]$VUs = 10,
    [string]$Duration = "1m",
    [string]$FlowMode = "full_chain",
    [string]$UserSelection = "vu_sticky",
    [string]$SummaryExport = "",
    [string]$ScriptPath = "loadtests/k6/async-category-summary.js"
)

$ErrorActionPreference = "Stop"

function Require-Command {
    param([string]$Name)
    if (-not (Get-Command $Name -ErrorAction SilentlyContinue)) {
        throw "Required command not found: $Name"
    }
}

Require-Command k6

if (-not $UserPassword) {
    throw "Please provide -UserPassword or set a secure value before running k6."
}

Write-Host "[k6-baseline] running $ScriptPath"
$args = @("run")
if ($SummaryExport) {
    $args += @("--summary-export", $SummaryExport)
}
$args += @(
    "-e", "BASE_URL=$BaseUrl",
    "-e", "USERNAME_PREFIX=$UserPrefix",
    "-e", "USER_PASSWORD=$UserPassword",
    "-e", "USER_COUNT=$UserCount",
    "-e", "VUS=$VUs",
    "-e", "DURATION=$Duration",
    "-e", "FLOW_MODE=$FlowMode",
    "-e", "USER_SELECTION=$UserSelection",
    $ScriptPath
)

& k6 @args

if ($LASTEXITCODE -ne 0) {
    throw "k6 baseline failed with exit code $LASTEXITCODE"
}
