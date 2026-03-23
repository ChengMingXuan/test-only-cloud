<#
.SYNOPSIS
    七大测试报告统一入口 - 合并总报告摘要与统计表输出
.DESCRIPTION
    按固定顺序拼接两个既有脚本的输出：
    1. aggregate-tool-reports.ps1 的总报告摘要
    2. generate-test-report.ps1 的统计表与跟踪摘要

    这样既保留独立报告聚合链路，也保留原七大测试报告的终端统计展示。

.PARAMETER CollectFirst
    是否先生成 7 份独立工具报告，再执行聚合与统计展示。

.EXAMPLE
    .\generate-combined-seven-tool-report.ps1
    .\generate-combined-seven-tool-report.ps1 -CollectFirst
#>
param(
    [switch]$CollectFirst
)

$ErrorActionPreference = "Stop"

if ($CollectFirst) {
    & "$PSScriptRoot\generate-tool-reports.ps1" -Tool all
}

& "$PSScriptRoot\aggregate-tool-reports.ps1"
Write-Host "" 
Write-Host "══════════════════════════════════════════════════════════════════════════════" -ForegroundColor DarkGray
Write-Host "" 
& "$PSScriptRoot\generate-test-report.ps1" -UseAggregatedResults -SkipWriteFiles