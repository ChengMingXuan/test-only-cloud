<#
.SYNOPSIS
    七工具迭代式增量测试门禁
.DESCRIPTION
    基于锁定基线，对七工具测试脚本执行迭代式门禁：

    1. 新增脚本：执行该脚本并纳入基线
    2. 修改脚本：仅执行该脚本，按新用例数覆盖旧基线
    3. 删除脚本：从基线和原子结果中移除，基线总数做减法
    4. 报告同步：更新受影响工具独立报告与七工具总报告

    日常迭代只跑 changed 模式；正式上线前再跑 full 模式。

.PARAMETER Mode
    check   仅做变更预检
    changed 仅执行新增/修改脚本
    full    执行当前全部脚本并重算基线

.PARAMETER AutoFix
    删除脚本时自动清理对应原子结果

.PARAMETER UpdateBaseline
    门禁通过后自动更新七工具基线
#>
param(
    [ValidateSet("check", "changed", "full")]
    [string]$Mode = "changed",

    [switch]$AutoFix = $true,
    [switch]$UpdateBaseline = $true
)

$ErrorActionPreference = "Continue"
$RootDir = (Resolve-Path "$PSScriptRoot\..").Path
$GateReportDir = Join-Path $RootDir "TestResults\gate-reports"
$BaselinePath = Join-Path $RootDir "TestResults\baseline\seven-tool-baseline.json"

. "$PSScriptRoot\seven-tool-report.common.ps1"

New-Item -Path $GateReportDir -ItemType Directory -Force | Out-Null

function Write-Banner { param($msg, $color = "Cyan")
    Write-Host "`n╔══════════════════════════════════════════════════════════════╗" -ForegroundColor $color
    Write-Host "║  $($msg.PadRight(58))║" -ForegroundColor $color
    Write-Host "╚══════════════════════════════════════════════════════════════╝" -ForegroundColor $color
}

function Write-Info($msg) { Write-Host "  ℹ️ $msg" -ForegroundColor Gray }
function Write-OK($msg) { Write-Host "  ✅ $msg" -ForegroundColor Green }
function Write-Warn($msg) { Write-Host "  ⚠️ $msg" -ForegroundColor Yellow }
function Write-Fail($msg) { Write-Host "  ❌ $msg" -ForegroundColor Red }

function Get-FileHashSafe {
    param([string]$Path)
    if (-not (Test-Path $Path)) { return "" }
    try { (Get-FileHash $Path -Algorithm SHA256).Hash } catch { "" }
}

function Normalize-SevenToolRelPath {
    param([string]$RelPath)

    if (-not $RelPath) { return "" }
    ([string]$RelPath).Replace("\", "/").Trim()
}

function Remove-AtomicForDeletedFile {
    param(
        [string]$Tool,
        [string]$RelFile
    )

    $normalizedRelFile = Normalize-SevenToolRelPath -RelPath $RelFile
    $atomicPath = Get-SevenToolAtomicResultPath -RootDir $RootDir -Tool $Tool -RelPath $normalizedRelFile
    if (Test-Path $atomicPath) {
        Remove-Item $atomicPath -Force -ErrorAction SilentlyContinue
    }
}

function Invoke-ChangedTest {
    param(
        [string]$Tool,
        [string]$RelFile
    )

    $normalizedRelFile = Normalize-SevenToolRelPath -RelPath $RelFile
    Write-Info "[$Tool] 执行: $normalizedRelFile"
    & "$PSScriptRoot\run-atomic-tests.ps1" -Tool $Tool -File $normalizedRelFile -ForceRunAll | Out-Host
    $atomic = Read-SevenToolAtomicResult -RootDir $RootDir -Tool $Tool -RelPath $normalizedRelFile
    return $atomic
}

function Build-UpdatedBaseline {
    param(
        $CurrentBaseline,
        [hashtable]$CurrentState
    )

    $updatedTools = [ordered]@{}
    $summaryFiles = 0
    $summaryCases = 0
    $summaryRuntimeCases = 0
    $staticCatalog = Get-SevenToolStaticCatalog

    foreach ($tool in (Get-SevenToolOrder)) {
        $toolState = $CurrentState[$tool]
        $entries = @()

        foreach ($item in @($toolState.currentFiles)) {
            $relFile = [string]$item.file
            $atomic = Read-SevenToolAtomicResult -RootDir $RootDir -Tool $tool -RelPath $relFile
            $tests = 0
            if ($null -ne $atomic -and $null -ne $atomic.total) {
                $tests = [int]$atomic.total
            } else {
                $oldEntry = @($CurrentBaseline.tools.$tool.entries | Where-Object { $_.file -eq $relFile } | Select-Object -First 1)
                if ($oldEntry.Count -gt 0) {
                    $tests = [int]$oldEntry[0].tests
                }
            }

            $entries += [ordered]@{
                file = $relFile
                hash = [string]$item.hash
                tests = $tests
            }
        }

        $toolRuntime = (@($entries | ForEach-Object { [int]$_.tests } | Measure-Object -Sum).Sum)
        $toolStandard = 0
        if ($null -ne $CurrentBaseline.tools.$tool -and $null -ne $CurrentBaseline.tools.$tool.standardCases -and [int]$CurrentBaseline.tools.$tool.standardCases -gt 0) {
            $toolStandard = [int]$CurrentBaseline.tools.$tool.standardCases
        } else {
            $toolStandard = [int]$staticCatalog[$tool].standard
        }

        $summaryFiles += $entries.Count
        $summaryCases += $toolStandard
        $summaryRuntimeCases += $toolRuntime

        $updatedTools[$tool] = [ordered]@{
            standardCases = $toolStandard
            runtimeCases = $toolRuntime
            fileCount = $entries.Count
            displayName = $CurrentBaseline.tools.$tool.displayName
            desc = $CurrentBaseline.tools.$tool.desc
            entries = $entries
        }
    }

    [ordered]@{
        version = $CurrentBaseline.version
        lockedAt = (Get-Date -Format "yyyy-MM-ddTHH:mm:ss")
        source = "incremental-seven-tool-gate"
        tools = $updatedTools
        summary = [ordered]@{
            totalFiles = $summaryFiles
            totalCases = $summaryCases
            totalRuntimeCases = $summaryRuntimeCases
        }
    }
}

Write-Banner "七工具迭代式增量门禁 [$Mode]" "Yellow"

if (-not (Test-Path $BaselinePath)) {
    Write-Fail "未找到七工具基线文件: $BaselinePath"
    Write-Info "请先执行 .\scripts\lock-seven-tool-baseline.ps1 以当前全绿状态锁定基线。"
    exit 1
}

$baseline = Read-SevenToolBaseline -RootDir $RootDir
$toolOrder = Get-SevenToolOrder
$catalog = Get-SevenToolCatalog -RootDir $RootDir
$gatePassed = $true
$affectedTools = New-Object System.Collections.Generic.HashSet[string]
$stateMap = @{}
$gateToolResults = @()
$baselineUpdateAllowed = $true

Write-Info "基线版本: $($baseline.version)"
Write-Info "锁定时间: $($baseline.lockedAt)"
Write-Info "当前基线用例数: $($baseline.summary.totalCases)"

foreach ($tool in $toolOrder) {
    $baseDir = Get-SevenToolBaseDir -RootDir $RootDir -Tool $tool
    $currentFiles = @()
    foreach ($relFile in (Get-SevenToolFiles -RootDir $RootDir -Tool $tool)) {
        $currentFiles += [ordered]@{
            file = $relFile
            hash = Get-FileHashSafe -Path (Join-Path $baseDir ($relFile -replace '/', '\'))
        }
    }

    $baselineEntries = @($baseline.tools.$tool.entries)
    $baselineIndex = @{}
    foreach ($entry in $baselineEntries) { $baselineIndex[[string]$entry.file] = $entry }

    $currentIndex = @{}
    foreach ($item in $currentFiles) { $currentIndex[[string]$item.file] = $item }

    $newFiles = @()
    $modifiedFiles = @()
    $deletedFiles = @()
    $unchangedFiles = @()

    foreach ($item in $currentFiles) {
        $relFile = [string]$item.file
        if (-not $baselineIndex.ContainsKey($relFile)) {
            $newFiles += $relFile
            continue
        }

        $oldHash = [string]$baselineIndex[$relFile].hash
        if ($oldHash -ne [string]$item.hash) {
            $modifiedFiles += $relFile
        } else {
            $unchangedFiles += $relFile
        }
    }

    foreach ($entry in $baselineEntries) {
        $relFile = [string]$entry.file
        if (-not $currentIndex.ContainsKey($relFile)) {
            $deletedFiles += $relFile
        }
    }

    $stateMap[$tool] = [ordered]@{
        currentFiles = $currentFiles
        newFiles = $newFiles
        modifiedFiles = $modifiedFiles
        deletedFiles = $deletedFiles
        unchangedFiles = $unchangedFiles
    }

    Write-Host "" 
    Write-Host "[$tool] $($catalog[$tool].displayName)" -ForegroundColor Cyan
    Write-Info "新增=$($newFiles.Count) 修改=$($modifiedFiles.Count) 删除=$($deletedFiles.Count) 未变更=$($unchangedFiles.Count)"

    if ($newFiles.Count -gt 0 -or $modifiedFiles.Count -gt 0 -or $deletedFiles.Count -gt 0) {
        [void]$affectedTools.Add($tool)
    }

    if ($Mode -eq "check") {
        continue
    }

    if ($deletedFiles.Count -gt 0 -and $AutoFix) {
        foreach ($deletedFile in $deletedFiles) {
            Remove-AtomicForDeletedFile -Tool $tool -RelFile $deletedFile
        }
    }

    $execFiles = switch ($Mode) {
        "changed" { @($newFiles + $modifiedFiles) }
        "full" { @($currentFiles | ForEach-Object { [string]$_.file }) }
    }

    $toolExecuted = 0
    $toolPassed = 0
    $toolFailed = 0

    foreach ($relFile in $execFiles) {
        $toolExecuted++
        $atomic = Invoke-ChangedTest -Tool $tool -RelFile $relFile

        if ($null -eq $atomic -or [int]$atomic.total -le 0) {
            $toolFailed++
            $gatePassed = $false
            Write-Fail "[$tool] $relFile 未生成有效结果。"
            continue
        }

        if ([int]$atomic.failed -gt 0) {
            $toolFailed++
            $gatePassed = $false
            Write-Fail "[$tool] $relFile 失败: $($atomic.failed)/$($atomic.total)"
        } else {
            $toolPassed++
            Write-OK "[$tool] $relFile 通过: $($atomic.passed)/$($atomic.total)"
        }
    }

    $gateToolResults += [ordered]@{
        tool = $tool
        new = $newFiles.Count
        modified = $modifiedFiles.Count
        deleted = $deletedFiles.Count
        executed = $toolExecuted
        passed = $toolPassed
        failed = $toolFailed
    }
}

if ($Mode -eq "check") {
    $report = [ordered]@{
        mode = $Mode
        timestamp = (Get-Date -Format "yyyy-MM-ddTHH:mm:ss")
        baselineVersion = $baseline.version
        tools = $stateMap
    }
    $report | ConvertTo-Json -Depth 15 | Out-File (Join-Path $GateReportDir "seven-tool-incremental-gate-check.json") -Encoding UTF8 -Force
    Write-Banner "预检完成" "Green"
    exit 0
}

if ($affectedTools.Count -gt 0) {
    Write-Host "" 
    Write-Host "🔄 同步受影响工具报告..." -ForegroundColor Cyan
    foreach ($tool in $affectedTools) {
        & "$PSScriptRoot\generate-tool-reports.ps1" -Tool $tool | Out-Host
    }
}

if ($gatePassed -and $UpdateBaseline) {
    $updatedBaseline = Build-UpdatedBaseline -CurrentBaseline $baseline -CurrentState $stateMap
    foreach ($tool in $toolOrder) {
        $health = Get-SevenToolBaselineHealth -RootDir $RootDir -Tool $tool -BaselineTool $updatedBaseline.tools.$tool
        $updatedBaseline.tools.$tool.health = $health
        if (-not [bool]$health.isHealthy) {
            $baselineUpdateAllowed = $false
            Write-Warn "[$tool] 本轮增量后的 baseline 健康度不足，已阻止自动覆盖。entryCoverage=$($health.entryCoverage)% reportCoverage=$($health.reportCoverage)%"
        }
    }

    if ($baselineUpdateAllowed) {
        $updatedBaseline | ConvertTo-Json -Depth 15 | Out-File $BaselinePath -Encoding UTF8 -Force
        Write-OK "七工具基线已按本轮迭代更新。"
    } else {
        Write-Warn "已跳过 baseline 自动更新，请在完整执行后使用 lock-seven-tool-baseline.ps1 重新锁定健康基线。"
    }
}

& "$PSScriptRoot\aggregate-tool-reports.ps1" | Out-Host

$gateVerdict = if ($gatePassed) { "PASS" } else { "FAIL" }
$gateReport = [ordered]@{
    mode = $Mode
    timestamp = (Get-Date -Format "yyyy-MM-ddTHH:mm:ss")
    baselineVersion = $baseline.version
    verdict = $gateVerdict
    affectedTools = @($affectedTools)
    tools = $gateToolResults
}

$gateReport | ConvertTo-Json -Depth 15 | Out-File (Join-Path $GateReportDir "seven-tool-incremental-gate.json") -Encoding UTF8 -Force

$md = [System.Text.StringBuilder]::new()
$null = $md.AppendLine("# 七工具迭代式增量测试门禁报告")
$null = $md.AppendLine("")
$null = $md.AppendLine("- 模式: $Mode")
$null = $md.AppendLine("- 基线版本: $($baseline.version)")
$null = $md.AppendLine("- 判定: $gateVerdict")
$null = $md.AppendLine("")
$null = $md.AppendLine("| 工具 | 新增 | 修改 | 删除 | 执行 | 通过 | 失败 |")
$null = $md.AppendLine("|------|------|------|------|------|------|------|")
foreach ($item in $gateToolResults) {
    $null = $md.AppendLine("| $($item.tool) | $($item.new) | $($item.modified) | $($item.deleted) | $($item.executed) | $($item.passed) | $($item.failed) |")
}
$md.ToString() | Out-File (Join-Path $GateReportDir "seven-tool-incremental-gate.md") -Encoding UTF8 -Force

Write-Host "" 
Write-Banner "七工具门禁结果: $gateVerdict" $(if ($gatePassed) { "Green" } else { "Red" })
Write-Info "报告: $(Join-Path $GateReportDir 'seven-tool-incremental-gate.md')"

if (-not $gatePassed) {
    exit 1
}