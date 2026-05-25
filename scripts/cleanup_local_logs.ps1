# 这里只清理本地临时日志，别把验收留档和业务数据塞进来。
# 默认只处理 .tmp/*.log；验收 smoke 日志必须显式开关才会动。
param(
    [string]$TmpDir = ".tmp",
    [int]$OlderThanDays = 7,
    [switch]$IncludeValidationSmoke,
    [string]$ValidationDir = "acceptance_refs/validation",
    [switch]$WhatIfOnly
)

$ErrorActionPreference = "Stop"

function Resolve-InProjectPath {
    param([string]$Path)
    return (Resolve-Path -LiteralPath $Path -ErrorAction SilentlyContinue)
}

function Remove-OldLogs {
    param(
        [string]$Directory,
        [string]$Pattern,
        [datetime]$Cutoff
    )

    $resolved = Resolve-InProjectPath -Path $Directory
    if (-not $resolved) {
        return 0
    }

    $removed = 0
    Get-ChildItem -LiteralPath $resolved.Path -File -Filter $Pattern -ErrorAction SilentlyContinue |
        Where-Object { $_.LastWriteTime -lt $Cutoff } |
        ForEach-Object {
            if ($WhatIfOnly) {
                Write-Host "[cleanup-local-logs] would remove $($_.FullName)"
            } else {
                Remove-Item -LiteralPath $_.FullName -Force
                Write-Host "[cleanup-local-logs] removed $($_.FullName)"
            }
            $removed += 1
        }
    return $removed
}

if ($OlderThanDays -lt 1) {
    throw "OlderThanDays must be >= 1"
}

$cutoff = (Get-Date).AddDays(-$OlderThanDays)
$total = 0
$total += Remove-OldLogs -Directory $TmpDir -Pattern "*.log" -Cutoff $cutoff

if ($IncludeValidationSmoke) {
    $total += Remove-OldLogs -Directory $ValidationDir -Pattern "*smoke*.log" -Cutoff $cutoff
}

Write-Host "[cleanup-local-logs] matched $total old log file(s)"
