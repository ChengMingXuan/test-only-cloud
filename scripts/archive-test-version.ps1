<#!
.SYNOPSIS
    测试版本归档脚本 - 将当前测试报告快照到版本目录
.DESCRIPTION
    按版本号归档当前7份独立报告 + 总报告 + 元数据到 TestResults/versions/{version}/
    每个版本目录包含：
      - version.json        版本元数据（版本号、时间、描述、变更摘要）
      - reports/            7份独立报告快照（JSON+MD）
      - seven-tool-report.md   该版本的七工具总报告
      - seven-tool-results.json 该版本的七工具聚合JSON
      - changelog.md        增量变更说明

    版本规范（详见 TestResults/CONVENTION.md）：
      - baseline   初始基线（无版本号，首次全量执行结果）
      - v1.0       第一个增量版本（当前未提交的功能）
      - v1.1       下一迭代
      - vX.Y       语义化递增

.PARAMETER Version
    版本号，如 "baseline"、"v1.0"、"v1.1"
.PARAMETER Description
    版本描述（简短说明本次增量内容）
.PARAMETER Changelog
    详细变更说明（多行文本）
.PARAMETER RegenerateFirst
    归档前先重新生成7份独立报告 + 总报告
.PARAMETER Force
    覆盖已存在的版本目录
.EXAMPLE
    .\archive-test-version.ps1 -Version "baseline" -Description "初始基线 - 全量测试通过"
    .\archive-test-version.ps1 -Version "v1.0" -Description "GB/T 36572 合规增量" -RegenerateFirst
    .\archive-test-version.ps1 -Version "v1.1" -Description "七工具最终锁版归档" -RegenerateFirst
#>
param(
    [Parameter(Mandatory=$true)]
    [string]$Version,

    [string]$Description = "",

    [string]$Changelog = "",

    [switch]$RegenerateFirst,

    [switch]$Force
)

$ErrorActionPreference = "Continue"
$RootDir     = (Resolve-Path "$PSScriptRoot\..").Path
$TestResults = Join-Path $RootDir "TestResults"
$ReportsDir  = Join-Path $TestResults "reports"
$VersionsDir = Join-Path $TestResults "versions"
$TargetDir   = Join-Path $VersionsDir $Version

# ── 校验 ──
if (-not ($Version -match '^(baseline|v\d+\.\d+)$')) {
    Write-Host "❌ 版本号格式错误：$Version（允许：baseline / v数字.数字）" -ForegroundColor Red
    exit 1
}

if ((Test-Path $TargetDir) -and -not $Force) {
    Write-Host "❌ 版本 $Version 已存在：$TargetDir" -ForegroundColor Red
    Write-Host "   使用 -Force 覆盖" -ForegroundColor Yellow
    exit 1
}

# ── 可选：先重新生成报告 ──
if ($RegenerateFirst) {
    Write-Host "🔄 重新生成7份独立报告 + 总报告..." -ForegroundColor Cyan
    & "$PSScriptRoot\generate-tool-reports.ps1" -Tool all
    & "$PSScriptRoot\aggregate-tool-reports.ps1"
    Write-Host ""
}

# ── 校验源报告存在 ──
$ToolOrder = @("integration", "pytest", "cypress", "puppeteer", "selenium", "playwright", "k6")
$missingReports = @()
foreach ($t in $ToolOrder) {
    $jsonPath = Join-Path $ReportsDir "$t-report.json"
    if (-not (Test-Path $jsonPath)) { $missingReports += $t }
}
if ($missingReports.Count -gt 0) {
    Write-Host "⚠️ 缺少以下工具的独立报告：$($missingReports -join ', ')" -ForegroundColor Yellow
    Write-Host "   建议先执行：.\scripts\generate-tool-reports.ps1 -Tool all" -ForegroundColor Yellow
    Write-Host "   继续归档已有报告..." -ForegroundColor Yellow
}

# ── 创建版本目录 ──
if (Test-Path $TargetDir) {
    Remove-Item -Path $TargetDir -Recurse -Force
}
$targetReports = Join-Path $TargetDir "reports"
New-Item -Path $targetReports -ItemType Directory -Force | Out-Null

Write-Host "📦 归档版本 $Version → $TargetDir" -ForegroundColor Cyan

# ── 复制7份独立报告 ──
$copiedCount = 0
foreach ($t in $ToolOrder) {
    foreach ($ext in @("json", "md")) {
        $src = Join-Path $ReportsDir "$t-report.$ext"
        if (Test-Path $src) {
            Copy-Item $src -Destination $targetReports -Force
            $copiedCount++
        }
    }
}
Write-Host "  ✅ 独立报告：$copiedCount 个文件" -ForegroundColor Green

# ── 复制总报告 ──
$aggregateFiles = @("seven-tool-report.md", "seven-tool-results.json", "six-tool-aggregate.md", "six-tool-report.md", "six-tool-results.json")
$aggCount = 0
foreach ($f in $aggregateFiles) {
    $src = Join-Path $TestResults $f
    if (Test-Path $src) {
        Copy-Item $src -Destination $TargetDir -Force
        $aggCount++
    }
}
Write-Host "  ✅ 总报告：$aggCount 个文件" -ForegroundColor Green

# ── 复制增量跳过清单（如果存在） ──
$skiplistSrc = Join-Path $RootDir "testing\tests\incremental-skiplist.json"
if (Test-Path $skiplistSrc) {
    Copy-Item $skiplistSrc -Destination $TargetDir -Force
    Write-Host "  ✅ 增量跳过清单已归档" -ForegroundColor Green
}

# ── 生成并归档脚本注册表快照 ──
Write-Host "  🔍 扫描测试脚本注册表..." -ForegroundColor DarkGray
$scanScript = Join-Path $RootDir "scripts\scan-test-scripts.ps1"
$registrySrc = Join-Path $RootDir "testing\tests\test-script-registry.json"
if (Test-Path $scanScript) {
    & $scanScript -Scan 2>$null | Out-Null
    if (Test-Path $registrySrc) {
        Copy-Item $registrySrc -Destination $TargetDir -Force
        Write-Host "  ✅ 脚本注册表快照已归档" -ForegroundColor Green

        # 如果不是 baseline，自动计算与上一版本的脚本变更
        if ($Version -ne "baseline") {
            # 找上一版本
            $indexPath2 = Join-Path $VersionsDir "index.json"
            $prevVersion = $null
            if (Test-Path $indexPath2) {
                try {
                    $allVersions = @(Get-Content $indexPath2 -Raw -Encoding UTF8 | ConvertFrom-Json)
                    $sorted2 = $allVersions | Where-Object { $_.version -ne $Version } | Sort-Object {
                        if ($_.version -eq "baseline") { "0.0" } else { ($_.version -replace '^v', '') }
                    }
                    if ($sorted2) { $prevVersion = ($sorted2 | Select-Object -Last 1).version }
                } catch {}
            }
            if (-not $prevVersion) { $prevVersion = "baseline" }

            # 对比
            $prevRegistryPath = Join-Path $VersionsDir "$prevVersion\test-script-registry.json"
            if (Test-Path $prevRegistryPath) {
                $oldReg = Get-Content $prevRegistryPath -Raw -Encoding UTF8 | ConvertFrom-Json
                $newReg = Get-Content $registrySrc -Raw -Encoding UTF8 | ConvertFrom-Json

                $oldIdx = @{}
                foreach ($t2 in @("pytest","cypress","puppeteer","selenium","playwright","k6")) {
                    if ($null -ne $oldReg.tools.$t2) {
                        foreach ($s2 in @($oldReg.tools.$t2.scripts)) { $oldIdx[$s2.file] = $s2 }
                    }
                }
                $newIdx = @{}
                foreach ($t2 in $newReg.tools.PSObject.Properties.Name) {
                    foreach ($s2 in @($newReg.tools.$t2.scripts)) { $newIdx[$s2.file] = $s2 }
                }

                $added = @($newIdx.Keys | Where-Object { -not $oldIdx.ContainsKey($_) } | ForEach-Object { [ordered]@{ file=$_; status=$newIdx[$_].status } })
                $modified = @($newIdx.Keys | Where-Object { $oldIdx.ContainsKey($_) -and $oldIdx[$_].hash -ne $newIdx[$_].hash } | ForEach-Object { [ordered]@{ file=$_; oldHash=$oldIdx[$_].hash; newHash=$newIdx[$_].hash } })
                $newDeprecated = @($newIdx.Keys | Where-Object { $oldIdx.ContainsKey($_) -and $oldIdx[$_].status -eq 'active' -and $newIdx[$_].status -eq 'deprecated' } | ForEach-Object { [ordered]@{ file=$_ } })

                $scriptChanges = [ordered]@{
                    comparedWith = $prevVersion
                    comparedAt   = (Get-Date).ToString("yyyy-MM-dd HH:mm:ss")
                    added        = $added
                    modified     = $modified
                    deprecated   = $newDeprecated
                    summary      = [ordered]@{
                        addedCount      = $added.Count
                        modifiedCount   = $modified.Count
                        deprecatedCount = $newDeprecated.Count
                    }
                }
                $scriptChangesPath = Join-Path $TargetDir "script-changes.json"
                $scriptChanges | ConvertTo-Json -Depth 10 | Out-File $scriptChangesPath -Encoding UTF8 -Force
                Write-Host "  ✅ 脚本变更清单已生成（vs $prevVersion）：+$($added.Count) ~$($modified.Count) -$($newDeprecated.Count)" -ForegroundColor Green
            }
        }
    }
} else {
    Write-Host "  ⚠️ 未找到 scan-test-scripts.ps1，跳过脚本注册表" -ForegroundColor Yellow
}

# ── 收集版本统计 ──
$toolStats = [ordered]@{}
$totalCases = 0; $totalPassed = 0; $totalFailed = 0
foreach ($t in $ToolOrder) {
    $jsonPath = Join-Path $targetReports "$t-report.json"
    if (Test-Path $jsonPath) {
        try {
            $d = Get-Content $jsonPath -Raw -Encoding UTF8 | ConvertFrom-Json
            $s = $d.summary
            $toolStats[$t] = [ordered]@{
                total   = [int]$s.total
                passed  = [int]$s.passed
                failed  = [int]$s.failed
                skipped = [int]$s.skipped
            }
            $totalCases  += [int]$s.total
            $totalPassed += [int]$s.passed
            $totalFailed += [int]$s.failed
        } catch {
            Write-Host "  ⚠️ 读取 $t 报告失败" -ForegroundColor Yellow
        }
    }
}

# ── 生成 version.json ──
$passRate = if ($totalCases -gt 0) { [math]::Round($totalPassed * 100.0 / $totalCases, 2) } else { 0 }

# 读取脚本注册表统计（如果已生成）
$scriptSummary = $null
$registryInTarget = Join-Path $TargetDir "test-script-registry.json"
if (Test-Path $registryInTarget) {
    try {
        $regData = Get-Content $registryInTarget -Raw -Encoding UTF8 | ConvertFrom-Json
        $scriptSummary = $regData.summary
    } catch {}
}

$versionMeta = [ordered]@{
    version      = $Version
    description  = $Description
    archivedAt   = (Get-Date).ToString("yyyy-MM-dd HH:mm:ss")
    archivedBy   = "archive-test-version.ps1"
    summary      = [ordered]@{
        totalCases  = $totalCases
        totalPassed = $totalPassed
        totalFailed = $totalFailed
        passRate    = $passRate
        allPass     = ($totalFailed -eq 0 -and $totalCases -gt 0)
    }
    scripts      = if ($scriptSummary) { $scriptSummary } else { $null }
    tools        = $toolStats
    files        = [ordered]@{
        reports   = (Get-ChildItem $targetReports -File | Select-Object -ExpandProperty Name)
        aggregate = ($aggregateFiles | Where-Object { Test-Path (Join-Path $TargetDir $_) })
    }
}
$versionJsonPath = Join-Path $TargetDir "version.json"
$versionMeta | ConvertTo-Json -Depth 10 | Out-File $versionJsonPath -Encoding UTF8 -Force
Write-Host "  ✅ version.json 已生成" -ForegroundColor Green

# ── 生成 changelog.md ──
$ts = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
$changelogContent = @"
# 📋 版本变更记录 - $Version

> **版本号**：$Version
> **归档时间**：$ts
> **描述**：$Description

---

## 测试统计

| 指标 | 数值 |
|------|------|
| 总用例数 | $totalCases |
| 通过 | $totalPassed ✅ |
| 失败 | $totalFailed $(if ($totalFailed -eq 0) {"✅"} else {"❌"}) |
| 通过率 | $passRate% |

## 各工具统计

| 工具 | 总数 | 通过 | 失败 |
|------|------|------|------|
"@
foreach ($t in $ToolOrder) {
    if ($null -ne $toolStats[$t]) {
        $st = $toolStats[$t]
        $changelogContent += "| $t | $($st.total) | $($st.passed) | $($st.failed) |`n"
    }
}
$changelogContent += @"

## 变更说明

$(if ($Changelog) { $Changelog } else { "_（未提供详细变更说明，请在归档后手动补充）_" })

---

*由 `archive-test-version.ps1` 自动生成*
"@
$changelogPath = Join-Path $TargetDir "changelog.md"
$changelogContent | Out-File $changelogPath -Encoding UTF8 -Force
Write-Host "  ✅ changelog.md 已生成" -ForegroundColor Green

# ── 更新版本索引 ──
$indexPath = Join-Path $VersionsDir "index.json"
$indexList = [System.Collections.ArrayList]::new()
if (Test-Path $indexPath) {
    try {
        $raw = Get-Content $indexPath -Raw -Encoding UTF8 | ConvertFrom-Json
        foreach ($item in @($raw)) {
            if ($item.version -ne $Version) {
                [void]$indexList.Add($item)
            }
        }
    } catch {}
}
[void]$indexList.Add([ordered]@{
    version     = $Version
    description = $Description
    archivedAt  = (Get-Date).ToString("yyyy-MM-dd HH:mm:ss")
    totalCases  = $totalCases
    passRate    = $passRate
    allPass     = ($totalFailed -eq 0 -and $totalCases -gt 0)
})
# 按版本排序：baseline 在前，v版本按数字排
$sorted = $indexList | Sort-Object { 
    if ($_.version -eq "baseline") { "0.0" }
    else { ($_.version -replace '^v', '') }
}
@($sorted) | ConvertTo-Json -Depth 5 | Out-File $indexPath -Encoding UTF8 -Force
Write-Host "  ✅ versions/index.json 已更新" -ForegroundColor Green

# ── 汇总 ──
$gate = if ($totalFailed -eq 0 -and $totalCases -gt 0) { "🟢 全部通过" } elseif ($totalCases -eq 0) { "⚪ 无数据" } else { "🔴 有失败" }
Write-Host ""
Write-Host "╔════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║  📦 版本归档完成                                    ║" -ForegroundColor Cyan
Write-Host "╚════════════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host "  版本：$Version" -ForegroundColor White
Write-Host "  路径：$TargetDir" -ForegroundColor Gray
Write-Host "  用例：$totalCases（通过 $totalPassed / 失败 $totalFailed）" -ForegroundColor Gray
Write-Host "  状态：$gate" -ForegroundColor $(if ($totalFailed -eq 0) {"Green"} else {"Red"})
Write-Host ""
Write-Host "查看版本历史：Get-Content $indexPath | ConvertFrom-Json | Format-Table" -ForegroundColor DarkGray
