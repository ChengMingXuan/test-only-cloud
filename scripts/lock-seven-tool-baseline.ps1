<#
.SYNOPSIS
    锁定七工具当前基线
.DESCRIPTION
    将当前七工具独立报告 + 原子结果 + 测试脚本快照固化为后续迭代增量门禁的基线。

    适用场景：
    1. 当前版本已全绿，需要作为后续迭代开发基线
    2. 发布前完成一次全量验证，需要重置基线
    3. 大版本切换，需要以新的脚本集合重建标准用例数

.PARAMETER GenerateReports
    锁定前先重新生成 7 份独立报告并聚合总报告

.PARAMETER Version
    基线版本号，默认使用当天时间戳
#>
param(
    [switch]$GenerateReports,
    [string]$Version = "",
    [switch]$AllowPartial
)

$ErrorActionPreference = "Stop"
$RootDir = (Resolve-Path "$PSScriptRoot\..").Path
$ReportsDir = Join-Path $RootDir "TestResults\reports"
$BaselineDir = Join-Path $RootDir "TestResults\baseline"
$BaselinePath = Join-Path $BaselineDir "seven-tool-baseline.json"

. "$PSScriptRoot\seven-tool-report.common.ps1"

New-Item -Path $BaselineDir -ItemType Directory -Force | Out-Null

function Write-Info($msg) { Write-Host "  ℹ️ $msg" -ForegroundColor Gray }
function Write-OK($msg) { Write-Host "  ✅ $msg" -ForegroundColor Green }
function Write-Warn($msg) { Write-Host "  ⚠️ $msg" -ForegroundColor Yellow }

if ($GenerateReports) {
    Write-Host "🔄 先刷新 7 份独立报告与总报告..." -ForegroundColor Cyan
    & "$PSScriptRoot\generate-tool-reports.ps1" -Tool all
    & "$PSScriptRoot\aggregate-tool-reports.ps1"
}

$toolOrder = Get-SevenToolOrder
$staticCatalog = Get-SevenToolStaticCatalog
$baselineTools = [ordered]@{}
$summaryTotalCases = 0
$summaryRuntimeCases = 0
$summaryFileCount = 0
$unhealthyTools = @()

foreach ($tool in $toolOrder) {
    $baseDir = Get-SevenToolBaseDir -RootDir $RootDir -Tool $tool
    $relFiles = @(Get-SevenToolFiles -RootDir $RootDir -Tool $tool)
    $reportPath = Join-Path $ReportsDir "$tool-report.json"
    $report = $null

    if (Test-Path $reportPath) {
        try {
            $report = Get-Content $reportPath -Raw -Encoding UTF8 | ConvertFrom-Json
        } catch {
            Write-Warn "[$tool] 独立报告读取失败，将回退到原子结果汇总"
        }
    }

    $entries = @()
    $toolTotal = 0

    foreach ($relFile in $relFiles) {
        $fullPath = Join-Path $baseDir ($relFile -replace '/', '\')
        $hash = if (Test-Path $fullPath) { (Get-FileHash $fullPath -Algorithm SHA256).Hash } else { "" }
        $atomic = Read-SevenToolAtomicResult -RootDir $RootDir -Tool $tool -RelPath $relFile
        $testCount = 0

        if ($null -ne $atomic -and $null -ne $atomic.total) {
            $testCount = [int]$atomic.total
        }

        $toolTotal += $testCount
        $entries += [ordered]@{
            file = $relFile
            hash = $hash
            tests = $testCount
        }
    }

    $nonZeroEntries = @($entries | Where-Object { [int]$_.tests -gt 0 }).Count
    $entryCoverage = if ($relFiles.Count -gt 0) { [math]::Round(($nonZeroEntries * 100.0 / $relFiles.Count), 1) } else { 0 }
    $reportFileCount = 0
    if ($null -ne $report -and $null -ne $report.fileCount) {
        $reportFileCount = [int]$report.fileCount
    }
    $reportCoverage = if ($relFiles.Count -gt 0) { [math]::Round(($reportFileCount * 100.0 / $relFiles.Count), 1) } else { 0 }
    $isHealthy = ($toolTotal -gt 0) -and (($entryCoverage -ge 70) -or ($reportCoverage -ge 70 -and $nonZeroEntries -gt 0))

    if (-not $isHealthy) {
        $unhealthyTools += [ordered]@{
            tool = $tool
            entryCoverage = $entryCoverage
            reportCoverage = $reportCoverage
            nonZeroEntries = $nonZeroEntries
            fileCount = $relFiles.Count
            cases = $toolTotal
        }
    }

    $toolStandard = [int]$staticCatalog[$tool].standard
    $summaryTotalCases += $toolStandard
    $summaryRuntimeCases += $toolTotal
    $summaryFileCount += $relFiles.Count

    $baselineTools[$tool] = [ordered]@{
        standardCases = $toolStandard
        runtimeCases = $toolTotal
        fileCount = $relFiles.Count
        displayName = $staticCatalog[$tool].displayName
        desc = $staticCatalog[$tool].desc
        health = [ordered]@{
            isHealthy = $isHealthy
            entryCoverage = $entryCoverage
            reportCoverage = $reportCoverage
            nonZeroEntries = $nonZeroEntries
        }
        entries = $entries
    }

    Write-OK "[$tool] 基线已采集: 文件=$($relFiles.Count) 标准=$toolStandard 运行=$toolTotal"
    if (-not $isHealthy) {
        Write-Warn "[$tool] 基线健康度不足：entryCoverage=$entryCoverage% reportCoverage=$reportCoverage% nonZero=$nonZeroEntries/$($relFiles.Count)"
    }
    if ($tool -eq "k6" -and $toolTotal -gt 0) {
        $resolvedEntryCount = @($entries | Where-Object { [int]$_.tests -gt 0 }).Count
        if ($resolvedEntryCount -eq 0) {
            Write-Warn "[k6] 当前基线仅锁定了总用例数，尚未形成场景级原子结果；如需增量门禁完全统一，请先执行 run-atomic-tests.ps1 -Tool k6。"
        }
    }
}

if (-not $Version) {
    $Version = (Get-Date -Format "yyyy.MM.dd-HHmmss")
}

if ($unhealthyTools.Count -gt 0 -and -not $AllowPartial) {
    Write-Host "" 
    Write-Warn "检测到不健康的工具基线，已拒绝锁定，以避免写入失真 baseline。"
    foreach ($item in $unhealthyTools) {
        Write-Warn "[$($item.tool)] 用例=$($item.cases) 文件=$($item.fileCount) entryCoverage=$($item.entryCoverage)% reportCoverage=$($item.reportCoverage)%"
    }
    Write-Info "如需强制锁定当前部分基线，请显式使用 -AllowPartial。"
    exit 1
}

$baseline = [ordered]@{
    version = $Version
    lockedAt = (Get-Date -Format "yyyy-MM-ddTHH:mm:ss")
    source = "current-seven-tool-green-baseline"
    tools = $baselineTools
    summary = [ordered]@{
        totalFiles = $summaryFileCount
        totalCases = $summaryTotalCases
        totalRuntimeCases = $summaryRuntimeCases
    }
}

$baseline | ConvertTo-Json -Depth 15 | Out-File $BaselinePath -Encoding UTF8 -Force

Write-Host "" 
Write-Host "╔══════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║  七工具基线已锁定                                    ║" -ForegroundColor Cyan
Write-Host "╚══════════════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Info "版本: $Version"
Write-Info "文件: $BaselinePath"
Write-Info "总文件数: $summaryFileCount"
Write-Info "总基线用例数: $summaryTotalCases"
Write-Info "总运行统计数: $summaryRuntimeCases"