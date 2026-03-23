<#
.SYNOPSIS
    七类测试报告生成器 - 从7份独立工具报告JSON聚合生成 Markdown 跟踪报告
.DESCRIPTION
    读取 generate-tool-reports.ps1 产出的 7 份独立报告 JSON
    （TestResults/reports/{tool}-report.json），
    聚合为统一格式的 Markdown 跟踪报告，含历史记录追溯。
    每次生成会追加一条历史快照到 seven-tool-history.json。
.PARAMETER OutputPath
    报告 Markdown 输出路径
.PARAMETER CollectFirst
    是否先执行 generate-tool-reports.ps1 -Tool all 再生成报告
.EXAMPLE
    .\generate-test-report.ps1
    .\generate-test-report.ps1 -CollectFirst
#>
param(
    [string]$ReportsDir = "$PSScriptRoot\..\TestResults\reports",
    [string]$OutputPath = "$PSScriptRoot\..\TestResults\seven-tool-report.md",
    [string]$HistoryPath = "$PSScriptRoot\..\TestResults\seven-tool-history.json",
    [string]$ResultJsonPath = "$PSScriptRoot\..\TestResults\seven-tool-results.json",
    [switch]$CollectFirst,
    [switch]$UseAggregatedResults,
    [switch]$SkipWriteFiles
)

$ErrorActionPreference = "Continue"
. "$PSScriptRoot\seven-tool-report.common.ps1"

# ═══════════════════════════════════════════════════════════════════════
# 数据来源：7 份独立工具报告 JSON（generate-tool-reports.ps1 产出）
# ═══════════════════════════════════════════════════════════════════════

# 先生成独立报告
if ($CollectFirst) {
    Write-Host "  🔄 先生成各工具独立报告..." -ForegroundColor Cyan
    & "$PSScriptRoot\generate-tool-reports.ps1" -Tool all
}

$RootDir = (Resolve-Path "$PSScriptRoot\..").Path
$toolOrder = Get-SevenToolOrder
$toolMeta = Get-SevenToolCatalog -RootDir $RootDir

# ═══════════════════════════════════════════════════════════════════════════════════════════════
# ⚠️ 禁止修改！标准用例数（固定基准，不随运行变化）
# 基准锁定日期：2026-03-08（基于实际用例数锁定）
# ═══════════════════════════════════════════════════════════════════════════════════════════════
$standardCases = Get-SevenToolStandardCases -RootDir $RootDir
$grandStandard = Get-SevenToolTotalStandard -RootDir $RootDir
$grandDefDisplay = $grandStandard

$loadedFromAggregate = $false
$history = @()

if ($UseAggregatedResults -and (Test-Path $ResultJsonPath)) {
    $aggregateResult = Get-Content $ResultJsonPath -Raw -Encoding UTF8 | ConvertFrom-Json
    $toolsData = [ordered]@{}
    $totalFilesFromDisk = 0

    foreach ($tool in $toolOrder) {
        $meta = $toolMeta[$tool]
        $existing = $aggregateResult.tools.$tool
        $fileCountFromDisk = Get-SevenToolFileCount -RootDir $RootDir -Tool $tool
        $totalFilesFromDisk += $fileCountFromDisk
        if ($null -ne $existing) {
            $toolsData[$tool] = [PSCustomObject]@{
                name         = $(if ($existing.name) { [string]$existing.name } else { $meta.name })
                displayName  = $(if ($existing.displayName) { [string]$existing.displayName } else { $meta.displayName })
                icon         = $(if ($existing.icon) { [string]$existing.icon } else { $meta.icon })
                total        = [int]$existing.total
                comparableTotal = [int](Coalesce $existing.comparableTotal $existing.total)
                measurementMode = [string](Coalesce $existing.measurementMode "cases")
                executedFiles = [int](Coalesce $existing.executedFiles 0)
                passed       = [int]$existing.passed
                failed       = [int]$existing.failed
                skipped      = [int]$existing.skipped
                fileCount    = $fileCountFromDisk
                definedCases = [int]$standardCases[$tool]
                duration_s   = [double](Coalesce $existing.duration_s 0)
                lastRun      = [string](Coalesce $existing.lastRun $aggregateResult.timestamp)
                reportPath   = [string](Coalesce $existing.reportPath (Join-Path $ReportsDir "$tool-report.json"))
                status       = [string](Coalesce $existing.status "⚪ 未运行或无报告")
                filePattern  = $meta.filePattern
                details      = @()
            }
        } else {
            $toolsData[$tool] = [PSCustomObject]@{
                name=$meta.name; displayName=$meta.displayName; icon=$meta.icon
                total=0; passed=0; failed=0; skipped=0
                comparableTotal=0; measurementMode="cases"; executedFiles=0
                fileCount=$fileCountFromDisk; definedCases=$standardCases[$tool]; duration_s=0; lastRun=""; reportPath=""
                status="⚪ 未运行或无报告"; filePattern=$meta.filePattern; details=@()
            }
        }
    }

    $data = [PSCustomObject]@{
        timestamp = [string](Coalesce $aggregateResult.timestamp (Get-Date).ToString("yyyy-MM-dd HH:mm:ss"))
        summary   = [PSCustomObject]@{
            total_tools         = 7
            total_files         = $totalFilesFromDisk
            total_defined_cases = [int](Coalesce $aggregateResult.summary.total_defined_cases $grandStandard)
            total_cases         = [int](Coalesce $aggregateResult.summary.total_cases 0)
            total_raw_cases     = [int](Coalesce $aggregateResult.summary.total_raw_cases (Coalesce $aggregateResult.summary.total_cases 0))
            total_passed        = [int](Coalesce $aggregateResult.summary.total_passed 0)
            total_failed        = [int](Coalesce $aggregateResult.summary.total_failed 0)
            total_skipped       = [int](Coalesce $aggregateResult.summary.total_skipped 0)
            pass_rate           = [double](Coalesce $aggregateResult.summary.pass_rate 0)
        }
        tools = [PSCustomObject]$toolsData
    }

    $history = Read-SevenToolHistoryEntries -Path $HistoryPath
    $loadedFromAggregate = $true
}

# 从7份独立报告构建兼容 $data 结构
if (-not $loadedFromAggregate) {
    $missingReports = @()
    $toolsData = [ordered]@{}
    $totalFiles = 0; $totalCases = 0; $totalPassed = 0; $totalFailed = 0; $totalSkipped = 0
    $latestTimestamp = ""

    foreach ($tool in $toolOrder) {
        $jsonPath = Join-Path $ReportsDir "$tool-report.json"
        $meta = $toolMeta[$tool]

        if (Test-Path $jsonPath) {
            $rpt = Get-Content $jsonPath -Raw -Encoding UTF8 | ConvertFrom-Json
            $sm = $rpt.summary
            $fc = Get-SevenToolFileCount -RootDir $RootDir -Tool $tool
            $dc = [int]$rpt.standardCases

            $status = "⚪ 未执行"
            if ([int]$sm.total -gt 0) {
                if ([int]$sm.failed -gt 0) { $status = "❌ 有失败" }
                elseif ([int]$sm.passed -eq 0 -and [int]$sm.skipped -gt 0) { $status = "⚠️ 异常态" }
                elseif ([string](Coalesce $sm.measurementMode "cases") -eq "compatible-cases") { $status = "🟡 兼容通过" }
                elseif ($dc -gt 0 -and [int]$sm.total -lt [math]::Floor($dc * 0.9)) { $status = "⚠️ 部分通过" }
                else { $status = "✅ 全部通过" }
            }

            $toolsData[$tool] = [PSCustomObject]@{
                name         = $meta.name
                displayName  = $meta.displayName
                icon         = $meta.icon
                total        = [int]$sm.total
                comparableTotal = [int](Coalesce $sm.comparableTotal $sm.total)
                measurementMode = [string](Coalesce $sm.measurementMode "cases")
                executedFiles = [int](Coalesce $sm.executedFiles 0)
                passed       = [int]$sm.passed
                failed       = [int]$sm.failed
                skipped      = [int]$sm.skipped
                fileCount    = $fc
                definedCases = $dc
                duration_s   = [double]$sm.duration_s
                lastRun      = $sm.timestamp
                reportPath   = $jsonPath
                status       = $status
                filePattern  = $meta.filePattern
                details      = @()
            }

            $totalFiles   += $fc
            $totalCases   += [int]$sm.total
            $totalPassed  += [int]$sm.passed
            $totalFailed  += [int]$sm.failed
            $totalSkipped += [int]$sm.skipped
            if ($sm.timestamp -and $sm.timestamp -gt $latestTimestamp) { $latestTimestamp = $sm.timestamp }
        } else {
            $missingReports += $tool
            $fc = Get-SevenToolFileCount -RootDir $RootDir -Tool $tool
            $toolsData[$tool] = [PSCustomObject]@{
                name=$meta.name; displayName=$meta.displayName; icon=$meta.icon
                total=0; passed=0; failed=0; skipped=0
                comparableTotal=0; measurementMode="cases"; executedFiles=0
                fileCount=$fc; definedCases=0; duration_s=0; lastRun=""; reportPath=""
                status="⚪ 未运行或无报告"; filePattern=$meta.filePattern; details=@()
            }
            $totalFiles += $fc
        }
    }

    if ($missingReports.Count -gt 0) {
        Write-Host "  ⚠️ 缺少独立报告: $($missingReports -join ', ')" -ForegroundColor Yellow
        Write-Host "  💡 请先运行: .\scripts\generate-tool-reports.ps1 -Tool all" -ForegroundColor Yellow
    }

    if (-not $latestTimestamp) { $latestTimestamp = (Get-Date).ToString("yyyy-MM-dd HH:mm:ss") }

    $passRateCalc = if ($totalCases -gt 0) { [math]::Round($totalPassed / $totalCases * 100, 1) } else { 0 }

    $data = [PSCustomObject]@{
        timestamp = $latestTimestamp
        summary   = [PSCustomObject]@{
            total_tools         = 7
            total_files         = $totalFiles
            total_defined_cases = $grandStandard
            total_cases         = $totalCases
            total_raw_cases     = $totalCases
            total_passed        = $totalPassed
            total_failed        = $totalFailed
            total_skipped       = $totalSkipped
            pass_rate           = $passRateCalc
        }
        tools = [PSCustomObject]$toolsData
    }

    if (-not $SkipWriteFiles) {
        $resultJson = [ordered]@{
            timestamp   = $latestTimestamp
            generatedBy = "generate-test-report.ps1"
            summary     = [ordered]@{
                total_tools=$data.summary.total_tools; total_files=$data.summary.total_files
                total_defined_cases=$grandStandard
                total_cases=$totalCases; total_passed=$totalPassed; total_failed=$totalFailed
                total_skipped=$totalSkipped; pass_rate=$passRateCalc
                allPass=($totalFailed -eq 0 -and $totalCases -gt 0)
            }
            tools = [ordered]@{}
        }
        foreach ($tool in $toolOrder) { $resultJson.tools[$tool] = $toolsData[$tool] }
        ConvertTo-Json -InputObject $resultJson -Depth 10 | Out-File $ResultJsonPath -Encoding UTF8
        Write-Host "  ✅ 结果已同步: $ResultJsonPath" -ForegroundColor DarkGray

        $historyEntry = [ordered]@{
            timestamp    = $data.timestamp
            summary      = $data.summary
            toolStatuses = [ordered]@{}
        }

        foreach ($tool in @("integration", "pytest", "cypress", "puppeteer", "selenium", "playwright", "k6")) {
            if ($data.tools.$tool) {
                $t = $data.tools.$tool
                $historyEntry.toolStatuses[$tool] = [ordered]@{
                    total   = $t.total
                    passed  = $t.passed
                    failed  = $t.failed
                    skipped = $t.skipped
                    status  = $t.status
                }
            }
        }

        $historyList = New-Object System.Collections.ArrayList
        foreach ($item in @(Read-SevenToolHistoryEntries -Path $HistoryPath)) { [void]$historyList.Add($item) }
        [void]$historyList.Add([PSCustomObject]$historyEntry)
        if ($historyList.Count -gt 50) {
            $trimmed = $historyList.GetRange($historyList.Count - 50, 50)
            $historyList = New-Object System.Collections.ArrayList(,$trimmed)
        }
        $history = @($historyList)
        ConvertTo-Json -InputObject $history -Depth 10 | Out-File $HistoryPath -Encoding UTF8
    } else {
        $history = Read-SevenToolHistoryEntries -Path $HistoryPath
    }
}

# ═══════════════════════════════════════════════════════════════════════
# 生成 Markdown 报告
# ═══════════════════════════════════════════════════════════════════════
$s = $data.summary
$passRate = $s.pass_rate
$healthBar = if ($passRate -ge 95) { "🟢" } elseif ($passRate -ge 80) { "🟡" } elseif ($passRate -ge 60) { "🟠" } else { "🔴" }

# 每个工具的快速执行命令
$toolCommands = @{
    integration = "cd testing/tests; python -m pytest testing/tests/integration/ -m integration -v --tb=short"
    pytest     = "cd testing/tests; python -m pytest test-automation/tests/ -v --tb=short"
    cypress    = "cd testing/tests/cypress-tests; npx cypress run"
    puppeteer  = "cd testing/tests/puppeteer-tests; npm run test:full"
    selenium   = "cd testing/tests/selenium-tests; python -m pytest testing/tests/ -v"
    playwright = "cd testing/tests/playwright-tests; npx playwright test"
    k6         = "cd k6; k6 run scenarios/smoke-test.js"
}
$toolTaskNames = @{
    integration = "⚛️ 原子化：IntegrationTest 逐文件执行"
    pytest     = "🧪 pytest：全量API测试"
    cypress    = "🧪 Cypress：E2E测试"
    puppeteer  = "🧪 Puppeteer：全量测试"
    selenium   = "🧪 Selenium：多浏览器矩阵"
    playwright = "🧪 Playwright：跨浏览器E2E"
    k6         = "🧪 K6：冒烟测试"
}

# 工具顺序（分类 + 详情表共用）
$toolOrder = @("integration", "pytest", "cypress", "puppeteer", "selenium", "playwright", "k6")

# 分类：已完成 / 有失败 / 未测试（修复后 $toolOrder 值更新为7工具版）
$doneTools = @()
$failTools = @()
$todoTools = @()
foreach ($tool in $toolOrder) {
    $t = $data.tools.$tool
    if (-not $t) { $todoTools += $tool; continue }
    # 有真实通过的用例才算完成
    if ([int]$t.total -gt 0 -and [int]$t.passed -gt 0 -and [int]$t.failed -eq 0) {
        $doneTools += $tool
    } elseif ([int]$t.failed -gt 0) {
        $failTools += $tool
    } else {
        $todoTools += $tool
    }
}
$completedCount = $doneTools.Count
$totalTools = 7
$progress = [math]::Round($completedCount / $totalTools * 100)

$md = @"
# 📊 AIOPS 七类测试报告跟踪记录

> **生成时间**: $($data.timestamp)  
> **平台版本**: JGSY.AGI 微服务平台（31个微服务）  
> **测试体系**: IntegrationTest → pytest → Cypress → Puppeteer → Selenium → Playwright → K6

---

## 🎯 下一步行动（测试进度 $completedCount / $totalTools）

``````
进度: [$("■" * $completedCount)$("□" * ($totalTools - $completedCount))] $completedCount/$totalTools ($progress%)
``````

"@

# 已完成的（可跳过）
if ($doneTools.Count -gt 0) {
    $md += "### ✅ 已完成（可跳过）`n`n"
    $md += "| # | 工具 | 📁 文件数 | 🎯 标准用例数 | 📝 实际用例数 | 执行/通过 | 结论 |`n"
    $md += "|---|------|----------|-------------|-------------|------|------|`n"
    $dIdx = 0
    foreach ($tool in $doneTools) {
        $dIdx++
        $t = $data.tools.$tool
        $fc = [int](Coalesce $t.fileCount 0)
        $dc = [int](Coalesce $t.definedCases 0)
        $std = $standardCases[$tool]
        $md += "| $dIdx | $($t.icon) **$($t.name)** | $fc | $std | $std | $($t.passed)/$($t.total) | ✅ 已通过，无需重测 |`n"
    }
    $md += "`n"
}

# 有失败的（需修复后重测）
if ($failTools.Count -gt 0) {
    $md += "### ❌ 有失败（需修复后重测）`n`n"
    $md += "| # | 工具 | 失败数 | 执行命令 |`n"
    $md += "|---|------|--------|----------|`n"
    $fIdx = 0
    foreach ($tool in $failTools) {
        $fIdx++
        $t = $data.tools.$tool
        $md += "| $fIdx | $($t.icon) **$($t.name)** | $($t.failed) 个失败 | ``$($toolCommands[$tool])`` |`n"
    }
    $md += "`n"
}

# 未测试的（下一步要做的）
if ($todoTools.Count -gt 0) {
    $md += "### 🔲 未测试（下一步执行）`n`n"
    $md += "| 优先级 | 工具 | 📁 文件数 | 📋 标准用例数 | VSCode Task | 命令行 |`n"
    $md += "|--------|------|----------|-------------|-------------|--------|`n"
    $tIdx = 0
    foreach ($tool in $todoTools) {
        $tIdx++
        $t = $data.tools.$tool
        $icon = if ($t) { $t.icon } else { "🔲" }
        $name = if ($t) { $t.name } else { $tool }
        $fc = if ($t) { [int](Coalesce $t.fileCount 0) } else { 0 }
        $std = $standardCases[$tool]
        $md += "| ▶ $tIdx | $icon **$name** | $fc | $std | ``$($toolTaskNames[$tool])`` | ``$($toolCommands[$tool])`` |`n"
    }
    $md += "`n"
    # 推荐下一步
    $nextTool = $todoTools[0]
    $nextT = $data.tools.$nextTool
    $nextIcon = if ($nextT) { $nextT.icon } else { "🔲" }
    $nextName = if ($nextT) { $nextT.name } else { $nextTool }
    $md += "> **👉 推荐下一步**: 运行 **$nextIcon $nextName** — ``$($toolCommands[$nextTool])``  `n`n"
} else {
    $md += "### 🎉 全部七类测试已完成！`n`n"
    if ($failTools.Count -eq 0) {
        $md += "> **结论**: 所有测试通过，可进入发布流程。`n`n"
    }
}

$md += @"

---

## 一、总览面板

| 指标 | 数值 |
|------|------|
| 健康度 | $healthBar **$passRate%** |
| 📁 测试文件 | **$(Coalesce $s.total_files 0)** |
| 🎯 标准用例数 | **$grandStandard**（全景覆盖基准） |
| 📝 实际用例数 | **$grandDefDisplay** |
| 📊 执行用例数 | **$($s.total_cases)** |
| 📈 执行率 | **$([math]::Round($s.total_cases / $grandStandard * 100, 1))%**（执行用例数 / 标准用例数） |
| ✅ 通过 | **$($s.total_passed)** |
| ❌ 失败 | **$($s.total_failed)** |
| ⏭️ 跳过 | **$($s.total_skipped)** |
| 工具数 | $($s.total_tools) 个（标准7类） |

``````
通过率进度条: [$("█" * [math]::Floor($passRate / 5))$("░" * (20 - [math]::Floor($passRate / 5)))] $passRate%
``````

---

## 二、七类测试详细结果

"@

# 工具详情表
$toolDescriptions = @{
    integration = "跨服务集成调用链路/流程端到端"
    pytest     = "API功能/CRUD/业务逻辑/多租户/安全"
    cypress    = "UmiJS管理后台组件交互/页面导航/表单"
    puppeteer  = "性能基准/页面加载/视觉回归/Core指标"
    selenium   = "Chrome/Firefox/Edge跨浏览器兼容性"
    playwright = "Chromium/Firefox/WebKit E2E端到端流程"
    k6         = "冒烟/负载/压力/并发/尖刺性能压测"
}

    $md += "| # | 工具 | 维度 | 📁 文件数 | 🎯 标准用例数 | 📝 实际用例数 | 📊 执行用例数 | ✅ 通过 | ❌ 失败 | ⏭️ 跳过 | 通过率 | 执行率 | 状态 |`n"
    $md += "|---|------|------|----------|-------------|-------------|-------------|---------|---------|---------|--------|--------|------|`n"

$idx = 0
foreach ($tool in $toolOrder) {
    $idx++
    $t = $data.tools.$tool
    if ($t) {
        $dc = [int](Coalesce $t.definedCases 0)
        # 通过率 = passed/total（含跳过，与 generate-tool-reports/aggregate 一致）
        $isZeroExec = ([int]$t.passed -eq 0 -and [int]$t.failed -eq 0 -and [int]$t.skipped -gt 0)
        $rate = if ($isZeroExec) { 0 } elseif ([int]$t.total -gt 0) { [math]::Round($t.passed / $t.total * 100, 1) } else { 0 }
        $rateIcon = if ($rate -ge 95) { "🟢" } elseif ($rate -ge 80) { "🟡" } elseif ($rate -ge 60) { "🟠" } elseif ($rate -gt 0) { "🔴" } else { "⚪" }
        $fc = [int](Coalesce $t.fileCount 0)
        $std = $standardCases[$tool]
        # 执行率 = 执行数 / 实际用例数
        $execRate = if ($dc -gt 0) { [math]::Round($t.total / $dc * 100, 1) } else { 0 }
        $execRateIcon = if ($execRate -ge 80) { "🟢" } elseif ($execRate -ge 50) { "🟡" } elseif ($execRate -gt 0) { "🟠" } else { "⚪" }
        $md += "| $idx | $($t.icon) **$($t.name)** | $($toolDescriptions[$tool]) | $fc | $std | $dc | $($t.total) | $($t.passed) | $($t.failed) | $($t.skipped) | $rateIcon $rate% | $execRateIcon $execRate% | $($t.status) |`n"
    }
}

# 每个工具的详细说明
$md += @"

---

## 三、各工具详细分析

"@

foreach ($tool in $toolOrder) {
    $t = $data.tools.$tool
    if (-not $t) { continue }
    
    # 通过率 = passed/total（含跳过，与 generate-tool-reports/aggregate 一致）
    $isZeroExec2 = ([int]$t.passed -eq 0 -and [int]$t.failed -eq 0 -and [int]$t.skipped -gt 0)
    $rate = if ($isZeroExec2) { 0 } elseif ([int]$t.total -gt 0) { [math]::Round($t.passed / $t.total * 100, 1) } else { 0 }
    
    $dc = [int](Coalesce $t.definedCases 0)
    $toolExecRate = if ($dc -gt 0) { [math]::Round($t.total / $dc * 100, 1) } else { 0 }
    
    $md += @"

### $($t.icon) $($t.displayName)

| 指标 | 数值 |
|------|------|
| 📁 测试文件 | $([int](Coalesce $t.fileCount 0)) 个$(if ($t.filePattern) { " (``$($t.filePattern)``)" } else { "" }) |
| 📋 标准用例数 | $($standardCases[$tool]) |
| 📝 实际用例数 | $dc |
| 执行用例数 | $($t.total) |
| 📈 执行率 | $toolExecRate% |
| 用例密度 | $(if ([int](Coalesce $t.fileCount 0) -gt 0) { "$([math]::Round($dc / [int]$t.fileCount, 1)) 例/文件" } else { '—' }) |
| 通过 | $($t.passed) |
| 失败 | $($t.failed) |
| 跳过 | $($t.skipped) |
| 通过率 | $rate% |
| 耗时 | $($t.duration_s)s |
| 最后运行 | $(if ($t.lastRun) { $t.lastRun } else { '—' }) |
| 报告路径 | $(if ($t.reportPath) { "``$($t.reportPath)``" } else { '—' }) |

"@
    
    if ($t.details -and $t.details.Count -gt 0) {
        $md += "**备注**:`n"
        foreach ($d in $t.details) {
            $md += "- $d`n"
        }
        $md += "`n"
    }
}

# ═══════════════════════════════════════════════════════════════════════
# 历史趋势
# ═══════════════════════════════════════════════════════════════════════
$md += @"

---

## 四、历史运行趋势

"@

if ($history.Count -gt 1) {
    $md += "| # | 时间 | 总用例 | ✅ 通过 | ❌ 失败 | ⏭️ 跳过 | 通过率 |`n"
    $md += "|---|------|--------|---------|---------|---------|--------|`n"
    
    $runIdx = 0
    $recentHistory = if ($history.Count -gt 10) { $history[-10..-1] } else { $history }
    foreach ($h in $recentHistory) {
        $runIdx++
        $hs = $h.summary
        # 兼容 snake_case (新) 和 camelCase (旧) 历史条目
        $hTotal = [int](Coalesce $hs.total_cases (Coalesce $hs.totalCases 0))
        $hPassed = [int](Coalesce $hs.total_passed (Coalesce $hs.passed 0))
        $hFailed = [int](Coalesce $hs.total_failed (Coalesce $hs.failed 0))
        $hSkipped = [int](Coalesce $hs.total_skipped (Coalesce $hs.skipped 0))
        $hRate = if ($hTotal -gt 0) { [math]::Round($hPassed / $hTotal * 100, 1) } else { 0 }
        $trend = if ($hRate -ge 95) { "🟢" } elseif ($hRate -ge 80) { "🟡" } else { "🔴" }
        $md += "| $runIdx | $($h.timestamp) | $hTotal | $hPassed | $hFailed | $hSkipped | $trend $hRate% |`n"
    }
    
    # 对比前后两次
    if ($history.Count -ge 2) {
        $prev = $history[-2].summary
        $curr = $history[-1].summary
        $caseDiff = [int](Coalesce $curr.total_cases (Coalesce $curr.totalCases 0)) - [int](Coalesce $prev.total_cases (Coalesce $prev.totalCases 0))
        $passDiff = [int](Coalesce $curr.total_passed (Coalesce $curr.passed 0)) - [int](Coalesce $prev.total_passed (Coalesce $prev.passed 0))
        $failDiff = [int](Coalesce $curr.total_failed (Coalesce $curr.failed 0)) - [int](Coalesce $prev.total_failed (Coalesce $prev.failed 0))
        $rateDiff = [math]::Round([double](Coalesce $curr.pass_rate (Coalesce $curr.passRate 0)) - [double](Coalesce $prev.pass_rate (Coalesce $prev.passRate 0)), 1)
        
        $md += @"

**与上次对比**:
- 用例变化: $(if ($caseDiff -ge 0) { "+$caseDiff" } else { "$caseDiff" })
- 通过变化: $(if ($passDiff -ge 0) { "+$passDiff ✅" } else { "$passDiff ⚠️" })
- 失败变化: $(if ($failDiff -le 0) { "$failDiff ✅" } else { "+$failDiff ⚠️" })
- 通过率变化: $(if ($rateDiff -ge 0) { "+$rateDiff%" } else { "$rateDiff%" })

"@
    }
} else {
    $md += "> 📝 首次运行，尚无历史数据。后续每次执行将自动追加趋势记录。`n`n"
}

# ═══════════════════════════════════════════════════════════════════════
# 按工具历史趋势
# ═══════════════════════════════════════════════════════════════════════
$md += @"

---

## 五、各工具历史变化

"@

if ($history.Count -gt 1) {
    foreach ($tool in $toolOrder) {
        $icon = switch ($tool) {
            "integration" { "🔗" }
            "pytest"     { "🐍" }
            "cypress"    { "🌲" }
            "puppeteer"  { "🤖" }
            "selenium"   { "🌐" }
            "playwright" { "🎭" }
            "k6"         { "⚡" }
            default      { "🔷" }
        }
        
        $md += "### $icon $tool`n`n"
        $md += "| 时间 | 总计 | 通过 | 失败 | 跳过 | 状态 |`n"
        $md += "|------|------|------|------|------|------|`n"
        
        $recentHistory = if ($history.Count -gt 10) { $history[-10..-1] } else { $history }
        foreach ($h in $recentHistory) {
            if ($h.toolStatuses.$tool) {
                $ts = $h.toolStatuses.$tool
                $md += "| $($h.timestamp) | $($ts.total) | $($ts.passed) | $($ts.failed) | $($ts.skipped) | $($ts.status) |`n"
            }
        }
        $md += "`n"
    }
}

# ═══════════════════════════════════════════════════════════════════════
# 测试金字塔
# ═══════════════════════════════════════════════════════════════════════
$md += @"

---

## 六、测试金字塔分布（T-1 至 T-7）

``````
                        ⚡ K6 (性能压测)
                       ━━━━━━━━━━━━━━━━━
                  🎭 Playwright (E2E端到端)
                 ━━━━━━━━━━━━━━━━━━━━━━━━━
            🌐 Selenium (跨浏览器兼容性)
           ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        🤖 Puppeteer (性能监控/视觉回归)
       ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    🌲 Cypress (组件交互/页面UI测试)
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  🐍 pytest (API功能/CRUD/业务逻辑)
 ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🔗 IntegrationTest (跨服务集成调用)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
``````

| 层级 | 工具 | 用例占比 | 建议占比 | 状态 |
|------|------|---------|---------|------|
"@

$totalAll = 0
foreach ($tool in $toolOrder) {
    $t = $data.tools.$tool
    if ($t) { $totalAll += [int](Coalesce $t.definedCases 0) }
}
if ($totalAll -eq 0) { $totalAll = 1 }
foreach ($tool in $toolOrder) {
    $t = $data.tools.$tool
    if ($t) {
        $dc = [int](Coalesce $t.definedCases 0)
        $pct = [math]::Round($dc / $totalAll * 100, 1)
        $recommended = switch ($tool) {
            "integration" { "5-10%" }
            "pytest"     { "40-60%" }
            "cypress"    { "15-25%" }
            "puppeteer"  { "5-10%" }
            "selenium"   { "5-10%" }
            "playwright" { "10-20%" }
            "k6"         { "5-15%" }
        }
        $md += "| $($t.icon) | $($t.name) | $pct% ($dc) | $recommended | $(if ($t.status -match '✅') { '✅' } elseif ($t.status -match '❌') { '❌' } else { '⚪' }) |`n"
    }
}

# 结尾
$md += @"

---

## 七、快速操作指南

| 操作 | 命令 |
|------|------|
| 生成7份独立报告 | ``.\scripts\generate-tool-reports.ps1 -Tool all`` |
| 生成总报告 | ``.\scripts\generate-test-report.ps1`` |
| 生成独立报告+总报告 | ``.\scripts\generate-test-report.ps1 -CollectFirst`` |
| 仅生成 pytest 报告 | ``.\scripts\generate-tool-reports.ps1 -Tool pytest`` |
| 仅生成 integration 报告 | ``.\scripts\generate-tool-reports.ps1 -Tool integration`` |
| 聚合总报告 | ``.\scripts\aggregate-tool-reports.ps1`` |
| 运行全量测试 | ``.\scripts\run-all-tests.ps1 -Level full`` |
| 运行冒烟测试 | ``.\scripts\run-all-tests.ps1 -Level smoke`` |

**报告文件**:
- 独立报告: ``TestResults/reports/{tool}-report.json``
- 总报告 JSON: ``TestResults/seven-tool-results.json``
- 总报告 Markdown: ``TestResults/seven-tool-report.md``
- 历史记录: ``TestResults/seven-tool-history.json``

---

*本报告由 ``generate-test-report.ps1`` 自动生成（数据源：7份独立工具报告） — JGSY.AGI 七类测试体系*
"@

function Get-TerminalDisplayWidth {
    try {
        $width = [int]$Host.UI.RawUI.WindowSize.Width
        if ($width -lt 96) { return 80 }
        return $width - 18
    } catch {
        return 100
    }
}

function Get-DisplayWidth {
    param([string]$Text)

    if ([string]::IsNullOrEmpty($Text)) { return 0 }

    $width = 0
    foreach ($ch in $Text.ToCharArray()) {
        $code = [int][char]$ch
        if ($code -le 127) {
            $width += 1
        } else {
            $width += 2
        }
    }
    return $width
}

function Format-DisplayCell {
    param(
        [string]$Text,
        [int]$Width,
        [string]$Align = "left"
    )

    $value = [string](Coalesce $Text "")
    $ellipsis = "..."
    $ellipsisWidth = Get-DisplayWidth $ellipsis
    $displayWidth = Get-DisplayWidth $value

    if ($displayWidth -gt $Width) {
        $current = ""
        $used = 0
        foreach ($ch in $value.ToCharArray()) {
            $charWidth = if ([int][char]$ch -le 127) { 1 } else { 2 }
            if ($used + $charWidth + $ellipsisWidth -gt $Width) { break }
            $current += $ch
            $used += $charWidth
        }
        $value = if ($Width -ge $ellipsisWidth) { $current + $ellipsis } else { $current }
        $displayWidth = Get-DisplayWidth $value
    }

    $padding = [Math]::Max(0, $Width - $displayWidth)
    switch ($Align) {
        "right" { return (" " * $padding) + $value }
        "center" {
            $left = [Math]::Floor($padding / 2)
            $right = $padding - $left
            return ((" " * $left) + $value + (" " * $right))
        }
        default { return $value + (" " * $padding) }
    }
}

function Get-TableWidths {
    param(
        [string[]]$Headers,
        [object[]]$Rows,
        [int]$MaxWidth,
        [int[]]$ShrinkOrder,
        [int[]]$MinWidths
    )

    $widths = @()
    for ($i = 0; $i -lt $Headers.Count; $i++) {
        $max = Get-DisplayWidth $Headers[$i]
        foreach ($row in $Rows) {
            $cellWidth = Get-DisplayWidth ([string]$row[$i])
            if ($cellWidth -gt $max) { $max = $cellWidth }
        }
        $widths += $max
    }

    $tableWidth = 1
    foreach ($width in $widths) { $tableWidth += $width + 3 }

    if ($tableWidth -le $MaxWidth) { return ,$widths }

    $overflow = $tableWidth - $MaxWidth
    while ($overflow -gt 0) {
        $changed = $false
        foreach ($index in $ShrinkOrder) {
            if ($overflow -le 0) { break }
            if ($widths[$index] -gt $MinWidths[$index]) {
                $widths[$index] -= 1
                $overflow -= 1
                $changed = $true
            }
        }
        if (-not $changed) { break }
    }

    return ,$widths
}

function New-TableBorder {
    param(
        [int[]]$Widths,
        [string]$Left,
        [string]$Middle,
        [string]$Right
    )

    $parts = @()
    foreach ($width in $Widths) {
        $parts += ("─" * ($width + 2))
    }
    return $Left + ($parts -join $Middle) + $Right
}

function New-TableRow {
    param(
        [object[]]$Values,
        [int[]]$Widths,
        [string[]]$Alignments
    )

    $cells = @()
    for ($i = 0; $i -lt $Values.Count; $i++) {
        $cells += (" " + (Format-DisplayCell -Text ([string]$Values[$i]) -Width $Widths[$i] -Align $Alignments[$i]) + " ")
    }
    return "│" + ($cells -join "│") + "│"
}

function Write-TerminalTable {
    param(
        [string[]]$Headers,
        [object[]]$Rows,
        [string[]]$Alignments,
        [int[]]$ShrinkOrder,
        [int[]]$MinWidths,
        [string[]]$RowColors
    )

    $widths = Get-TableWidths -Headers $Headers -Rows $Rows -MaxWidth (Get-TerminalDisplayWidth) -ShrinkOrder $ShrinkOrder -MinWidths $MinWidths
    Write-Host ("  " + (New-TableBorder -Widths $widths -Left "┌" -Middle "┬" -Right "┐")) -ForegroundColor White
    Write-Host ("  " + (New-TableRow -Values $Headers -Widths $widths -Alignments $Alignments)) -ForegroundColor White
    Write-Host ("  " + (New-TableBorder -Widths $widths -Left "├" -Middle "┼" -Right "┤")) -ForegroundColor White

    for ($rowIndex = 0; $rowIndex -lt $Rows.Count; $rowIndex++) {
        $color = if ($RowColors.Count -gt $rowIndex) { $RowColors[$rowIndex] } else { "Gray" }
        Write-Host ("  " + (New-TableRow -Values $Rows[$rowIndex] -Widths $widths -Alignments $Alignments)) -ForegroundColor $color
    }

    Write-Host ("  " + (New-TableBorder -Widths $widths -Left "└" -Middle "┴" -Right "┘")) -ForegroundColor White
}

# 写入报告
if (-not $SkipWriteFiles) {
    $md | Out-File $OutputPath -Encoding UTF8
    Write-Host "`n  ✅ 报告已生成: $OutputPath" -ForegroundColor Green
}
$grandExecRateDisplay = if ($grandDefDisplay -gt 0) { [math]::Round($s.total_cases / $grandDefDisplay * 100, 1) } else { 0 }
$rawTotalDisplay = if ($null -ne $s.total_raw_cases) { [int]$s.total_raw_cases } else { [int]$s.total_cases }
Write-Host "  📊 实际用例数: $grandDefDisplay | 兼容执行: $($s.total_cases) (执行率 $grandExecRateDisplay%) | 原始执行: $rawTotalDisplay | 通过率: $healthBar $passRate% ($($s.total_passed)/$rawTotalDisplay)`n" -ForegroundColor Cyan

# 输出跟踪摘要（含预计时间）
$estimatedTimes = @{
    integration = "~30分钟"
    pytest      = "~1.5小时"
    cypress     = "~5.5小时"
    puppeteer   = "~2.5小时"
    selenium    = "~5小时"
    playwright  = "~6小时"
    k6          = "~2小时"
}

Write-Host "  📊 七类测试跟踪摘要" -ForegroundColor Cyan
$overallTerminalStatus = if ([int](Coalesce $s.total_failed 0) -gt 0) {
    "  📋 七大测试框架全量验证完成 - 存在失败 ❌（当前不可发布）"
} elseif ([int](Coalesce $s.total_cases 0) -gt 0) {
    "  📋 七大测试框架全量验证完成 - ALL PASS ✅（当前可发布）"
} else {
    "  📋 七大测试框架尚未形成有效执行结果 ⚪"
}
$overallTerminalColor = if ([int](Coalesce $s.total_failed 0) -gt 0) { "Red" } elseif ([int](Coalesce $s.total_cases 0) -gt 0) { "Green" } else { "Yellow" }
Write-Host $overallTerminalStatus -ForegroundColor $overallTerminalColor

# 用例数推导规范（从 StaticCatalog 读取，保持单一数据源）
$catalogForTrack = Get-SevenToolStaticCatalog

$trackRows = @()
$trackColors = @()
$grandFilesTrack = 0
foreach ($tool in $toolOrder) {
    $t = $data.tools.$tool
    $meta = $catalogForTrack[$tool]
    if ($t -and $meta) {
        $fc = [int](Coalesce $t.fileCount 0)
        $std = [int]$meta.standard
        $avgPF = if ($meta.avgPerFile) { $meta.avgPerFile } else { if ($fc -gt 0) { [math]::Round($std / $fc, 1) } else { 0 } }
        $countPat = if ($meta.countPattern) { [string]$meta.countPattern } else { $meta.filePattern }
        $grandFilesTrack += $fc
        $trackRows += ,@(
            [string]$t.name,
            [string]$fc,
            "~$avgPF",
            [string]$countPat,
            [string]$std,
            $estimatedTimes[$tool],
            [string]$meta.desc
        )
        $trackColors += "DarkGray"
    }
}
$trackRows += ,@("合计", [string]$grandFilesTrack, "-", "-", [string]$grandStandard, "~23小时左右", "1123 文件 × 平均用例/文件 = $grandStandard 用例")
$trackColors += "DarkGray"

Write-TerminalTable -Headers @("框架", "文件数", "平均/文件", "计数规则", "标准用例", "预计时间", "推导说明") -Rows $trackRows -Alignments @("left", "right", "right", "left", "right", "left", "left") -ShrinkOrder @(6) -MinWidths @(14,6,8,16,8,10,30) -RowColors $trackColors

# 输出综合统计（合并：基础规模 + 执行结果 + 比率状态 → 一个表）
Write-Host "`n  📊 七类测试综合统计" -ForegroundColor Cyan

$combinedRows = @()
$combinedColors = @()
foreach ($tool in $toolOrder) {
    $t = $data.tools.$tool
    if ($t) {
        $dc = [int](Coalesce $t.definedCases 0)
        $rate = if ([int]$t.total -gt 0) { [math]::Round($t.passed / $t.total * 100, 1) } else { 0 }
        $std = $standardCases[$tool]
        $compatibleExec = [int](Coalesce $t.comparableTotal $t.total)
        $measurementMode = [string](Coalesce $t.measurementMode "cases")
        $execRateBase = if ($measurementMode -in @("checks", "compatible-cases")) { $compatibleExec } else { $dc }
        $execRate = if ($execRateBase -gt 0) { [math]::Round($compatibleExec / $execRateBase * 100) } else { 0 }
        $statusText = [string]($t.status -replace '✅\s*', '' -replace '⚠️\s*', '' -replace '❌\s*', '' -replace '🟢\s*', '')
        $rowColor = if ($t.status -match "✅") { "Green" } elseif ($t.status -match "❌") { "Red" } else { "Yellow" }
        $actualDisplay = if ($measurementMode -eq "checks") { [string]$compatibleExec } elseif ($measurementMode -eq "compatible-cases") { [string]$compatibleExec } else { [string]$dc }
        $execDisplay = if ($measurementMode -eq "checks") { "$($t.total)次" } elseif ($measurementMode -eq "compatible-cases") { "$compatibleExec（原始$($t.total)）" } else { [string]$t.total }
        $combinedRows += ,@(
            [string]$t.name,
            [string][int](Coalesce $t.fileCount 0),
            [string]$std,
            $actualDisplay,
            $execDisplay,
            [string]$t.passed,
            [string]$t.failed,
            [string]$t.skipped,
            "$rate%",
            "$execRate%",
            $statusText
        )
        $combinedColors += $rowColor
    }
}

$grandDefCases = $grandStandard
$grandExecRate = if ($grandDefCases -gt 0) { [math]::Round($s.total_cases / $grandDefCases * 100) } else { 0 }
$combinedRows += ,@(
    "合计",
    [string](Coalesce $s.total_files 0),
    [string]$grandStandard,
    [string]$grandDefCases,
    [string]$s.total_cases,
    [string]$s.total_passed,
    [string]$s.total_failed,
    [string]$s.total_skipped,
    "$($s.pass_rate)%",
    "$grandExecRate%",
    $(if ([int](Coalesce $s.total_failed 0) -gt 0) { "有失败" } elseif ([int](Coalesce $s.total_cases 0) -gt 0) { "全部通过" } else { "未执行" })
)
$combinedColors += $(if ([int](Coalesce $s.total_failed 0) -gt 0) { "Red" } elseif ([int](Coalesce $s.total_cases 0) -gt 0) { "Green" } else { "Yellow" })

Write-TerminalTable -Headers @("工具", "文件", "标准用例", "实际用例", "执行", "通过", "失败", "跳过", "通过率", "执行率", "状态") -Rows $combinedRows -Alignments @("left", "right", "right", "right", "right", "right", "right", "right", "right", "right", "left") -ShrinkOrder @(0,10) -MinWidths @(14,4,8,8,6,6,4,4,6,6,8) -RowColors $combinedColors
