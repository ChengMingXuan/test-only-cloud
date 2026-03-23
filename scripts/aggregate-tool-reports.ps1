<#
.SYNOPSIS
    七工具总报告聚合器 - 从7份独立报告生成统一总报告
.DESCRIPTION
    读取 TestResults/reports/{tool}-report.json（7份独立工具报告）
    → 聚合为 TestResults/seven-tool-results.json（兼容现有格式）
    → 生成 TestResults/seven-tool-report.md   （统一总报告，继承原始数据+溯源依据）

    数据链路：
      原子结果（TestResults/atomic/{tool}/*.json）
        ↓ generate-tool-reports.ps1
      独立报告（TestResults/reports/{tool}-report.json）
        ↓ aggregate-tool-reports.ps1（本脚本）
      总报告（TestResults/seven-tool-report.md）

    总报告特点：
      - 继承7份独立报告的全量原始数据（不丢失溯源信息）
      - 包含每工具的发布门禁状态
      - 包含整体通过/失败统计
      - 追加历史快照到 seven-tool-history.json

.PARAMETER GenerateIndividual
    聚合前先为所有工具重新生成独立报告
.PARAMETER OutputPath
    总报告 Markdown 输出路径
.EXAMPLE
    .\aggregate-tool-reports.ps1
    .\aggregate-tool-reports.ps1 -GenerateIndividual
#>
param(
    [switch]$GenerateIndividual,
    [string]$OutputPath      = "$PSScriptRoot\..\TestResults\seven-tool-report.md",
    [string]$JsonOutputPath  = "$PSScriptRoot\..\TestResults\seven-tool-results.json",
    [string]$HistoryPath     = "$PSScriptRoot\..\TestResults\seven-tool-history.json"
)

$ErrorActionPreference = "Continue"
. "$PSScriptRoot\seven-tool-report.common.ps1"
$RootDir    = (Resolve-Path "$PSScriptRoot\..").Path
$ReportsDir = Join-Path $RootDir "TestResults\reports"

New-Item -Path $ReportsDir -ItemType Directory -Force | Out-Null

$ToolOrder = Get-SevenToolOrder
$ToolMeta = Get-SevenToolCatalog -RootDir $RootDir
$TotalStandard = Get-SevenToolTotalStandard -RootDir $RootDir
$BaselineData = Read-SevenToolBaseline -RootDir $RootDir

# ── 可选：先生成独立报告 ──
if ($GenerateIndividual) {
    Write-Host "🔄 先生成7份独立工具报告..." -ForegroundColor Cyan
    & "$PSScriptRoot\generate-tool-reports.ps1" -Tool all
}

# ── 读取7份独立报告 ──
Write-Host "`n📥 读取7份独立工具报告..." -ForegroundColor Cyan

$toolData  = [ordered]@{}
$missing   = @()
foreach ($t in $ToolOrder) {
    $jsonPath = Join-Path $ReportsDir "$t-report.json"
    if (Test-Path $jsonPath) {
        try {
            $d = Get-Content $jsonPath -Raw -Encoding UTF8 | ConvertFrom-Json
            $toolData[$t] = $d
            $icon = if ([int]$d.summary.failed -gt 0) { "❌" } elseif ([int]$d.summary.total -eq 0) { "⚪" } else { "✅" }
            Write-Host "  $icon [$t] total=$([int]$d.summary.total) passed=$([int]$d.summary.passed) failed=$([int]$d.summary.failed)" -ForegroundColor Gray
        } catch {
            Write-Host "  ⚠️ [$t] 读取独立报告失败：$_" -ForegroundColor Yellow
            $missing += $t
        }
    } else {
        Write-Host "  ⚪ [$t] 无独立报告（$jsonPath），将从旧版聚合 JSON 回退" -ForegroundColor DarkGray
        $missing += $t
    }
}

# 对缺失的工具回退到旧版 seven-tool-results.json（兼容 six-tool-results.json）
if ($missing.Count -gt 0) {
    $oldJsonPath = Join-Path $RootDir "TestResults\seven-tool-results.json"
    if (-not (Test-Path $oldJsonPath)) {
        $oldJsonPath = Join-Path $RootDir "TestResults\six-tool-results.json"
    }
    if (Test-Path $oldJsonPath) {
        try {
            $oldData = Get-Content $oldJsonPath -Raw -Encoding UTF8 | ConvertFrom-Json
            foreach ($t in $missing) {
                if ($null -ne $oldData.tools.$t) {
                    $ot = $oldData.tools.$t
                    # 构建兼容的独立报告格式
                    $toolData[$t] = [PSCustomObject]@{
                        tool=$t; displayName=$ToolMeta[$t].display; icon=$ToolMeta[$t].icon
                        standardCases=$ToolMeta[$t].standard
                        summary=[PSCustomObject]@{
                            total=[int]$ot.total; passed=[int]$ot.passed; failed=[int]$ot.failed
                            skipped=[int]$ot.skipped; passRate=0; duration_s=[double]$ot.duration_s
                            timestamp=[string]$oldData.timestamp; source="旧版聚合 JSON（六工具汇总）"
                        }
                        gateStatus=[PSCustomObject]@{ canRelease=(([int]$ot.failed -eq 0) -and ([int]$ot.total -gt 0) -and (([int]$ot.passed -gt 0) -or ([int]$ot.skipped -eq 0))); statusText=[string]$ot.status }
                        fileCount=[int]$ot.fileCount; files=@(); failures=@()
                    }
                    Write-Host "  ↩️ [$t] 已从旧版聚合 JSON 回退" -ForegroundColor DarkYellow
                }
            }
        } catch {}
    }
}

# ── 计算总指标 ──
$grandTotal   = 0; $grandComparableTotal = 0; $grandPassed = 0; $grandFailed = 0; $grandSkipped = 0; $grandDur = 0.0
$toolSummaries = [ordered]@{}
foreach ($t in $ToolOrder) {
    if ($null -eq $toolData[$t]) { continue }
    $s = $toolData[$t].summary
    $grandTotal   += [int]$s.total
    if ($null -ne $s.comparableTotal) {
        $grandComparableTotal += [int]$s.comparableTotal
    } else {
        $grandComparableTotal += [int]$s.total
    }
    $grandPassed  += [int]$s.passed
    $grandFailed  += [int]$s.failed
    $grandSkipped += [int]$s.skipped
    $grandDur     += [double]$s.duration_s
    $toolSummaries[$t] = $s
}
$overallPassRate = if ($grandTotal -gt 0) { [math]::Round($grandPassed*100.0/$grandTotal,1) } else { 0.0 }
$allPass         = $grandFailed -eq 0 -and $grandTotal -gt 0
$durH = [math]::Round($grandDur/3600,1)

# ── 构建兼容旧格式的 six-tool-results.json ──
$newJson = [ordered]@{
    timestamp   = (Get-Date).ToString("yyyy-MM-dd HH:mm:ss")
    generatedBy = "aggregate-tool-reports.ps1"
    sourceReports = "$ReportsDir"
    summary = [ordered]@{
        total_files  = ($toolData.Values | ForEach-Object { [int]$_.fileCount } | Measure-Object -Sum).Sum
        total_defined_cases = $TotalStandard
        total_cases  = $grandComparableTotal
        total_raw_cases = $grandTotal
        total_passed = $grandPassed
        total_failed = $grandFailed
        total_skipped = $grandSkipped
        pass_rate    = $overallPassRate
        duration_s   = [math]::Round($grandDur,1)
        allPass      = $allPass
    }
    tools = [ordered]@{}
}
foreach ($t in $ToolOrder) {
    if ($null -eq $toolData[$t]) { continue }
    $s = $toolData[$t].summary
    $m = $ToolMeta[$t]
    $newJson.tools[$t] = [ordered]@{
        name        = $t
        displayName = $toolData[$t].displayName
        icon        = $m.icon
        standardCases = $m.standard
        definedCases = [int]$s.total
        comparableTotal = if ($null -ne $s.comparableTotal) { [int]$s.comparableTotal } else { [int]$s.total }
        measurementMode = if ($null -ne $s.measurementMode) { [string]$s.measurementMode } else { "cases" }
        executedFiles = if ($null -ne $s.executedFiles) { [int]$s.executedFiles } else { 0 }
        total       = [int]$s.total
        passed      = [int]$s.passed
        failed      = [int]$s.failed
        skipped     = [int]$s.skipped
        fileCount   = [int]$toolData[$t].fileCount
        duration_s  = [double]$s.duration_s
        lastRun     = [string]$s.timestamp
        status      = if ([int]$s.failed -gt 0) { "❌ 有失败" } elseif ([int]$s.total -eq 0) { "⚪ 未运行或无报告" } elseif (($null -ne $s.measurementMode) -and ([string]$s.measurementMode -eq "compatible-cases")) { "🟡 兼容通过" } elseif ($m.standard -gt 0 -and [int]$s.total -lt [math]::Floor($m.standard * 0.9)) { "⚠️ 部分通过" } else { "✅ 全部通过" }
        reportPath  = (Join-Path $ReportsDir "$t-report.md")
        canRelease  = ([bool]$toolData[$t].gateStatus.canRelease)
    }
}
$newJson | ConvertTo-Json -Depth 10 | Out-File $JsonOutputPath -Encoding UTF8 -Force
Write-Host "  ✅ seven-tool-results.json 已更新" -ForegroundColor Green

# ── 追加历史快照 ──
$historyEntry = [ordered]@{
    timestamp = (Get-Date).ToString("yyyy-MM-dd HH:mm:ss")
    summary   = $newJson.summary
    toolStatuses = [ordered]@{}
}
foreach ($t in $ToolOrder) {
    if ($null -ne $toolData[$t]) {
        $s = $toolData[$t].summary
        $historyEntry.toolStatuses[$t] = [ordered]@{
            total=[int]$s.total; passed=[int]$s.passed; failed=[int]$s.failed
            skipped=[int]$s.skipped; canRelease=([bool]$toolData[$t].gateStatus.canRelease)
        }
    }
}
$historyList = [System.Collections.ArrayList]::new()
foreach ($item in @(Read-SevenToolHistoryEntries -Path $HistoryPath)) {
    [void]$historyList.Add($item)
}
[void]$historyList.Add($historyEntry)
# 仅保留最近50条
if ($historyList.Count -gt 50) { $historyList = [System.Collections.ArrayList]($historyList | Select-Object -Last 50) }
$historyList | ConvertTo-Json -Depth 10 | Out-File $HistoryPath -Encoding UTF8 -Force

# ── 生成总报告 Markdown ──
$ts   = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
$overallGate = if ($allPass) { "🟢 **全部通过 - 可以发布**" } elseif ($grandTotal -eq 0) { "⚪ **未验证**" } else { "🔴 **有失败 - 禁止发布**" }
$passRateEmoji = if ($overallPassRate -ge 99) { "🟢" } elseif ($overallPassRate -ge 95) { "🟡" } else { "🔴" }

$sb = [System.Text.StringBuilder]::new()
$null = $sb.AppendLine("# 📊 七类测试工具总报告")
$null = $sb.AppendLine("")
$null = $sb.AppendLine("> **报告类型**：统一总报告（基于7份独立工具报告聚合）  ")
$null = $sb.AppendLine("> **生成时间**：$ts  ")
$null = $sb.AppendLine("> **数据来源**：``TestResults/reports/{tool}-report.json`` × 7  ")
$null = $sb.AppendLine("> **溯源支持**：点击下方各工具链接可回溯到文件级和用例级结果")
$null = $sb.AppendLine("")
$null = $sb.AppendLine("---")
$null = $sb.AppendLine("")

# 总体发布门禁状态
$null = $sb.AppendLine("## 🚦 发布门禁总结论")
$null = $sb.AppendLine("")
$null = $sb.AppendLine("| 指标                | 数值                          |")
$null = $sb.AppendLine("|---------------------|-------------------------------|")
$null = $sb.AppendLine("| 标准用例基准        | $TotalStandard（平台全景覆盖）|")
$null = $sb.AppendLine("| 实际执行项数（兼容口径） | $grandComparableTotal          |")
$null = $sb.AppendLine("| 原始执行总量        | $grandTotal                   |")
$null = $sb.AppendLine("| 通过用例数          | $grandPassed ✅               |")
$null = $sb.AppendLine("| 失败用例数          | $grandFailed ❌               |")
$null = $sb.AppendLine("| 跳过用例数          | $grandSkipped ⏭️              |")
$null = $sb.AppendLine("| 总通过率            | $passRateEmoji $overallPassRate% |")
$null = $sb.AppendLine("| 总执行耗时          | ${durH}h                      |")
$null = $sb.AppendLine("| **发布门禁结论**    | $overallGate                  |")
$null = $sb.AppendLine("")

# 各工具发布门禁状态
$null = $sb.AppendLine("### 各工具发布门禁")
$null = $sb.AppendLine("")
$null = $sb.AppendLine("| 工具 | 标准用例 | 实际执行 | 通过 | 失败 | 通过率 | 门禁状态 | 独立报告 |")
$null = $sb.AppendLine("|------|----------|----------|------|------|--------|----------|----------|")
foreach ($t in $ToolOrder) {
    if ($null -eq $toolData[$t]) { continue }
    $m  = $ToolMeta[$t]; $s = $toolData[$t].summary
    $tot  = if ($null -ne $s.comparableTotal) { [int]$s.comparableTotal } else { [int]$s.total }
    $rawTotal = [int]$s.total
    $pas=[int]$s.passed; $fai=[int]$s.failed
    $pr   = if ($rawTotal -gt 0) { [math]::Round($pas*100.0/$rawTotal,1) } else { 0 }
    $gate = if ([bool]$toolData[$t].gateStatus.canRelease) { "✅ 可发布" } elseif ($tot -eq 0) { "⚪ 未执行" } else { "❌ 有失败" }
    $link = "[$t-report.md](reports/$t-report.md)"
    $totDisplay = [string]$tot
    if ($null -ne $s.measurementMode -and [string]$s.measurementMode -eq "checks") {
        $totDisplay = "$tot（原始检查:$([int]$s.total)）"
    } elseif ($null -ne $s.measurementMode -and [string]$s.measurementMode -eq "compatible-cases") {
        $totDisplay = "$tot（原始执行:$([int]$s.total)）"
    }
    $null = $sb.AppendLine("| $($m.icon) $($m.display) | $($m.standard) | $totDisplay | $pas | $fai | $pr% | $gate | $link |")
}
$null = $sb.AppendLine("")
$null = $sb.AppendLine("---")
$null = $sb.AppendLine("")

# 锁定基准说明
$null = $sb.AppendLine("## 🔒 当前锁定基线")
$null = $sb.AppendLine("")
$null = $sb.AppendLine("| 工具       | 标准用例数 | 推导逻辑                                          |")
$null = $sb.AppendLine("|------------|------------|---------------------------------------------------|")
foreach ($t in $ToolOrder) {
    if ($null -eq $ToolMeta[$t]) { continue }
    $m = $ToolMeta[$t]
    $null = $sb.AppendLine("| $($m.icon) $($m.display) | $($m.standard) | $($m.desc) |")
}
$baselineLabel = if ($null -ne $BaselineData -and $BaselineData.lockedAt) { "锁定时间：$($BaselineData.lockedAt)" } else { "未锁定基线时回退到静态默认值" }
$null = $sb.AppendLine("| **合计**   | **$TotalStandard** | **$baselineLabel** |")
$null = $sb.AppendLine("")
$null = $sb.AppendLine("---")
$null = $sb.AppendLine("")

# 溯源路径
$null = $sb.AppendLine("## 🔍 完整溯源路径")
$null = $sb.AppendLine("")
$null = $sb.AppendLine('```')
$null = $sb.AppendLine("总报告 (seven-tool-report.md)")
$null = $sb.AppendLine("  ├─ 🔗 integration-report.md  ← TestResults/reports/integration-report.json")
$null = $sb.AppendLine("  │    ├─ 文件级：TestResults/atomic/integration/{file}.json")
$null = $sb.AppendLine("  │    └─ XML：TestResults/integration-results.xml")
$null = $sb.AppendLine("  ├─ 🐍 pytest-report.md        ← TestResults/reports/pytest-report.json")
$null = $sb.AppendLine("  │    ├─ 文件级：TestResults/atomic/pytest/{file}.json")
$null = $sb.AppendLine("  │    └─ XML：TestResults/pytest-results.xml")
$null = $sb.AppendLine("  ├─ 🌲 cypress-report.md       ← TestResults/reports/cypress-report.json")
$null = $sb.AppendLine("  │    └─ 文件级：TestResults/atomic/cypress/{spec}.json")
$null = $sb.AppendLine("  ├─ 🤖 puppeteer-report.md     ← TestResults/reports/puppeteer-report.json")
$null = $sb.AppendLine("  │    └─ 文件级：TestResults/atomic/puppeteer/{test}.json")
$null = $sb.AppendLine("  ├─ 🌐 selenium-report.md      ← TestResults/reports/selenium-report.json")
$null = $sb.AppendLine("  │    └─ 文件级：TestResults/atomic/selenium/{file}.json")
$null = $sb.AppendLine("  ├─ 🎭 playwright-report.md    ← TestResults/reports/playwright-report.json")
$null = $sb.AppendLine("  │    └─ 文件级：TestResults/atomic/playwright/{spec}.json")
$null = $sb.AppendLine("  └─ ⚡ k6-report.md            ← TestResults/reports/k6-report.json")
$null = $sb.AppendLine("       └─ 场景级：TestResults/atomic/k6/{scenario}.json")
$null = $sb.AppendLine('```')
$null = $sb.AppendLine("")
$null = $sb.AppendLine("---")
$null = $sb.AppendLine("")

# 历史趋势（最近5条）
$null = $sb.AppendLine("## 📈 历史执行趋势（最近5次）")
$null = $sb.AppendLine("")
$null = $sb.AppendLine("| 执行时间 | 总通过率 | 失败数 | 结论 |")
$null = $sb.AppendLine("|---------|---------|--------|------|")
$recent = $historyList | Select-Object -Last 5
foreach ($h in $recent) {
    $ht  = [string]$h.timestamp
    $hs  = $h.summary
    $hpr = 0
    if ([int]$hs.total_cases -gt 0) {
        $hpr = [math]::Round([int]$hs.total_passed*100.0/[int]$hs.total_cases,1)
    } elseif ([int]$hs.totalCases -gt 0) {
        # 兼容旧版 camelCase 历史条目
        $hpr = [math]::Round([int]$hs.passed*100.0/[int]$hs.totalCases,1)
    }
    $hf  = if ($null -ne $hs.total_failed) { [int]$hs.total_failed } else { [int]$hs.failed }
    $hg  = if ($hf -eq 0 -and ($hpr -gt 0)) { "✅ 可发布" } else { "❌ 有失败" }
    $null = $sb.AppendLine("| $ht | $hpr% | $hf | $hg |")
}
$null = $sb.AppendLine("")
$null = $sb.AppendLine("---")
$null = $sb.AppendLine("")
$null = $sb.AppendLine("*本总报告由 ``aggregate-tool-reports.ps1`` 自动生成。*  ")
$null = $sb.AppendLine("*完整溯源：查看 ``TestResults/reports/{tool}-report.md`` × 7份独立报告。*  ")
$null = $sb.AppendLine("*如需重新生成：``.\scripts\aggregate-tool-reports.ps1 -GenerateIndividual``*")

$sb.ToString() | Out-File $OutputPath -Encoding UTF8 -Force

# ── 打印汇总 ──
Write-Host "`n╔══════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║  📊 七工具总报告已生成                                ║" -ForegroundColor Cyan
Write-Host "╚══════════════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host "  总报告：$OutputPath" -ForegroundColor Gray
Write-Host "  JSON：  $JsonOutputPath" -ForegroundColor Gray
Write-Host "  兼容执行：$grandComparableTotal  原始执行：$grandTotal  通过：$grandPassed  失败：$grandFailed  通过率：$overallPassRate%" -ForegroundColor Gray
$gateColor = if ($allPass) { "Green" } else { "Red" }
Write-Host "  $overallGate" -ForegroundColor $gateColor

# 输出各工具独立报告链接
Write-Host "`n  7份独立报告：" -ForegroundColor Cyan
foreach ($t in $ToolOrder) {
    $gate = if ($null -ne $toolData[$t] -and [bool]$toolData[$t].gateStatus.canRelease) { "✅" }
            elseif ($null -eq $toolData[$t]) { "⚪" }
            else { "❌" }
    Write-Host "  $gate $t → TestResults/reports/$t-report.md" -ForegroundColor Gray
}
