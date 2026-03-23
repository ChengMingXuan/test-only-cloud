<#
.SYNOPSIS
    六类测试结果收集器 - 实时解析每个测试框架的原生输出
.DESCRIPTION
    从各测试框架的报告文件/输出中提取用例数、通过数、失败数、跳过数，
    写入统一 JSON 格式供报告生成器使用。
    支持框架：pytest / Cypress / Puppeteer / Selenium / Playwright / K6
.PARAMETER Tool
    指定收集哪个工具的结果。留空则收集全部。
.PARAMETER OutputPath
    结果 JSON 输出路径
.EXAMPLE
    .\collect-test-results.ps1
    .\collect-test-results.ps1 -Tool pytest
#>
param(
    [ValidateSet("all", "pytest", "cypress", "puppeteer", "selenium", "playwright", "k6")]
    [string]$Tool = "all",
    [string]$OutputPath = "$PSScriptRoot\..\TestResults\six-tool-results.json"
)

$ErrorActionPreference = "Continue"
$rootDir = (Resolve-Path "$PSScriptRoot\..").Path

# PowerShell 5.1 兼容的空值合并
function Coalesce($a, $b) { if ($null -ne $a) { $a } else { $b } }

# ═══════════════════════════════════════════════════════════════════════════════════════════════
# ⚠️ 禁止修改！标准用例数（固定基准，不随运行变化）
# 平台全景覆盖基准：31 微服务 / 2893 API / 827 页面
# 基准锁定日期：2026-03-08（基于实际用例数锁定）
# ───────────────────────────────────────────────────────────────────────────────────────────────
# | 工具       | 标准用例数 | 推导逻辑                                                           |
# |------------|------------|--------------------------------------------------------------------|
# | pytest     | 56121      | 2893 API × ~19 用例/API（正向/反向/边界/鉴权/多租户等）            |
# | Cypress    | 9506       | 827 页面 × ~11.5 交互场景/页面                                     |
# | Puppeteer  | 8000       | 827 页面 × ~10 渲染/性能检查/页面                                  |
# | Selenium   | 6335       | 827 页面 × ~8 浏览器兼容/页面                                      |
# | Playwright | 10708      | 业务流程链路 × 多浏览器矩阵                                        |
# | k6         | 3429       | 2893 API × ~1.2 性能场景/API                                       |
# ═══════════════════════════════════════════════════════════════════════════════════════════════
$standardCases = @{
    pytest     = 56121  # 2893 API × ~19 用例/API
    cypress    = 9506   # 827 页面 × ~11.5 交互场景
    puppeteer  = 8000   # 827 页面 × ~10 渲染/性能
    selenium   = 6335   # 827 页面 × ~8 浏览器兼容
    playwright = 10708  # 业务流程 × 多浏览器矩阵
    k6         = 3429   # 2893 API × ~1.2 性能场景
}
# ═══════════════════════════════════════════════════════════════════════════════════════════════

# 确保输出目录存在
$outputDir = Split-Path $OutputPath -Parent
if (-not (Test-Path $outputDir)) {
    New-Item -ItemType Directory -Path $outputDir -Force | Out-Null
}

# 初始化结果结构
function New-ToolResult {
    param([string]$Name, [string]$DisplayName, [string]$Icon)
    return [ordered]@{
        name         = $Name
        displayName  = $DisplayName
        icon         = $Icon
        definedCases = 0   # 源码中定义的用例数（通过扫描源码计数）
        total        = 0   # 执行报告中的用例数（来自实际运行结果）
        passed       = 0
        failed       = 0
        skipped      = 0
        errors       = 0
        fileCount    = 0
        filePattern  = ""
        duration_s   = 0
        lastRun      = $null
        status       = "未运行"
        details      = @()
        reportPath   = ""
    }
}

# ═════════════════════════════════════════════════════════════════════════
# 1. pytest 结果收集
# ═════════════════════════════════════════════════════════════════════════
function Collect-PytestResults {
    $result = New-ToolResult -Name "pytest" -DisplayName "pytest (API功能测试)" -Icon "🐍"
    
    # 尝试多个可能的 JSON 报告路径
    $possibleJsonPaths = @(
        "$RootDir\testing\tests\test-automation\.report.json",
        "$RootDir\testing\tests\test-automation\report.json",
        "$RootDir\testing\tests\pytest-report\report.json",
        "$rootDir\TestResults\pytest-results.json"
    )
    
    $found = $false
    foreach ($path in $possibleJsonPaths) {
        if (Test-Path $path) {
            try {
                $data = Get-Content $path -Raw -Encoding UTF8 | ConvertFrom-Json
                if ($data.summary) {
                    $result.total = [int](Coalesce $data.summary.total 0)
                    $result.passed = [int](Coalesce $data.summary.passed 0)
                    $result.failed = [int](Coalesce $data.summary.failed 0)
                    $result.skipped = [int](Coalesce $data.summary.skipped 0)
                    $result.duration_s = [math]::Round((Coalesce $data.summary.duration 0), 1)
                    $result.lastRun = (Get-Item $path).LastWriteTime.ToString("yyyy-MM-dd HH:mm:ss")
                    $result.status = if ($result.failed -eq 0) { "✅ 全部通过" } else { "❌ 有失败" }
                    $result.reportPath = $path
                    $found = $true
                    break
                }
            } catch {}
        }
    }
    
    # 回退：从 combined-results.json 读取
    if (-not $found) {
        $combined = "$rootDir\TestResults\combined-results.json"
        if (Test-Path $combined) {
            try {
                $data = Get-Content $combined -Raw -Encoding utf8 | ConvertFrom-Json
                if ($data.tools.pytest) {
                    $pt = $data.tools.pytest
                    $result.total = [int](Coalesce $pt.total 0)
                    $result.passed = [int](Coalesce $pt.passed 0)
                    $result.skipped = [int](Coalesce $pt.skipped 0)
                    $result.failed = $result.total - $result.passed - $result.skipped
                    $result.duration_s = [math]::Round((Coalesce $pt.duration_s 0), 1)
                    $result.lastRun = $data.timestamp
                    $result.status = if ($result.failed -eq 0) { "✅ 全部通过" } else { "❌ 有失败" }
                    $result.reportPath = $combined
                    $found = $true
                }
            } catch {}
        }
    }
    
    # 回退：JUnit XML（pytest --junitxml 生成）
    if (-not $found) {
        $junitPaths = @(
            "$rootDir\TestResults\pytest-results.xml",
            "$RootDir\testing\tests\pytest-results.xml",
            "$RootDir\testing\tests\test-automation\pytest-results.xml"
        )
        foreach ($junitPath in $junitPaths) {
            if (Test-Path $junitPath) {
                try {
                    [xml]$xml = Get-Content $junitPath -Encoding UTF8
                    # pytest 生成 <testsuites><testsuite tests=...> 结构，取内层 testsuite
                    $suite = $null
                    if ($xml.testsuites -and $xml.testsuites.testsuite) {
                        $suite = $xml.testsuites.testsuite
                    } elseif ($xml.testsuites) {
                        $suite = $xml.testsuites
                    } elseif ($xml.testsuite) {
                        $suite = $xml.testsuite
                    }
                    if ($suite -and $suite.tests) {
                        $result.total  = [int](Coalesce $suite.tests 0)
                        $result.failed = [int](Coalesce $suite.failures 0) + [int](Coalesce $suite.errors 0)
                        $result.skipped = [int](Coalesce $suite.skipped 0)
                        $result.passed = $result.total - $result.failed - $result.skipped
                        $result.duration_s = [math]::Round([double](Coalesce $suite.time 0), 1)
                        $result.lastRun = (Get-Item $junitPath).LastWriteTime.ToString("yyyy-MM-dd HH:mm:ss")
                        $result.status = if ($result.failed -eq 0) { "✅ 全部通过" } else { "❌ 有失败" }
                        $result.reportPath = $junitPath
                        $found = $true
                        break
                    }
                } catch {}
            }
        }
    }

    if (-not $found) {
        $result.status = "⚪ 未运行或无报告"
    }

    # 统计 pytest 测试文件数（tests/ 下排除 selenium/playwright/puppeteer/automated/__pycache__）
    $pyFiles = @(Get-ChildItem "$rootDir\tests" -Filter "test_*.py" -Recurse -ErrorAction SilentlyContinue |
        Where-Object { $_.FullName -notmatch "selenium|playwright|puppeteer|__pycache__" })
    $result.fileCount = $pyFiles.Count
    $result.filePattern = "test_*.py"

    # 扫描源码统计定义的用例数（def test_）
    $defCount = 0
    foreach ($f in $pyFiles) {
        $content = Get-Content $f.FullName -Raw -ErrorAction SilentlyContinue
        if ($content) { $defCount += ([regex]::Matches($content, "def test_")).Count }
    }
    $result.definedCases = $defCount
    
    return $result
}

# ═════════════════════════════════════════════════════════════════════════
# 2. Cypress 结果收集
# ═════════════════════════════════════════════════════════════════════════
function Collect-CypressResults {
    $result = New-ToolResult -Name "cypress" -DisplayName "Cypress (组件交互测试)" -Icon "🌲"
    
    # 读取 mochawesome 报告
    $reportDir = "$RootDir\testing\tests\cypress-tests\reports"
    
    $found = $false
    
    # 优先：汇总 reports 目录下所有单独的 JSON 报告（每个 spec 文件一个）
    $allJsonReports = @(Get-ChildItem "$reportDir\*.json" -ErrorAction SilentlyContinue |
        Where-Object { $_.Name -ne "combined-report.json" })
    if ($allJsonReports.Count -gt 1) {
        $totalTests = 0; $totalPasses = 0; $totalFailures = 0; $totalPending = 0; $totalDuration = 0
        $latestTime = [datetime]::MinValue
        foreach ($rf in $allJsonReports) {
            try {
                $d = Get-Content $rf.FullName -Raw -Encoding UTF8 | ConvertFrom-Json
                if ($d.stats) {
                    $totalTests += [int](Coalesce $d.stats.tests 0)
                    $totalPasses += [int](Coalesce $d.stats.passes 0)
                    $totalFailures += [int](Coalesce $d.stats.failures 0)
                    $totalPending += [int](Coalesce $d.stats.pending 0)
                    $totalDuration += [int](Coalesce $d.stats.duration 0)
                    if ($rf.LastWriteTime -gt $latestTime) { $latestTime = $rf.LastWriteTime }
                }
            } catch {}
        }
        if ($totalTests -gt 0) {
            $result.total = $totalTests
            $result.passed = $totalPasses
            $result.failed = $totalFailures
            $result.skipped = $totalPending
            $result.duration_s = [math]::Round($totalDuration / 1000, 1)
            $result.lastRun = $latestTime.ToString("yyyy-MM-dd HH:mm:ss")
            $result.status = if ($result.failed -eq 0) { "✅ 全部通过" } else { "❌ 有失败" }
            $result.reportPath = $reportDir
            $found = $true
        }
    }
    
    # 回退：读取单个汇总报告
    if (-not $found) {
        $possiblePaths = @(
            "$reportDir\combined-report.json",
            "$reportDir\mochawesome.json",
            "$reportDir\mochawesome-report\mochawesome.json"
        )
        foreach ($path in $possiblePaths) {
            if (Test-Path $path) {
                try {
                    $data = Get-Content $path -Raw -Encoding UTF8 | ConvertFrom-Json
                    if ($data.stats) {
                        $result.total = [int](Coalesce $data.stats.tests 0)
                        $result.passed = [int](Coalesce $data.stats.passes 0)
                        $result.failed = [int](Coalesce $data.stats.failures 0)
                        $result.skipped = [int](Coalesce $data.stats.pending 0) + [int](Coalesce $data.stats.skipped 0)
                        $result.duration_s = [math]::Round((Coalesce $data.stats.duration 0) / 1000, 1)
                        $result.lastRun = (Get-Item $path).LastWriteTime.ToString("yyyy-MM-dd HH:mm:ss")
                        $result.status = if ($result.failed -eq 0) { "✅ 全部通过" } else { "❌ 有失败" }
                        $result.reportPath = $path
                        $found = $true
                        break
                    }
                } catch {}
            }
        }
    }
    
    # 回退：读取 parallel-results/results.json（并行执行汇总）
    if (-not $found) {
        $parallelResult = "$RootDir\testing\tests\cypress-tests\parallel-results\results.json"
        if (Test-Path $parallelResult) {
            try {
                $pData = Get-Content $parallelResult -Raw -Encoding UTF8 | ConvertFrom-Json
                if ($pData.total_cases_pass -ge 0 -or $pData.total_cases_fail -ge 0) {
                    $totalPass = [int](Coalesce $pData.total_cases_pass 0)
                    $totalFail = [int](Coalesce $pData.total_cases_fail 0)
                    # 从各 spec 汇总 pending
                    $totalPending = 0
                    if ($pData.specs) {
                        foreach ($s in $pData.specs) {
                            $totalPending += [int](Coalesce $s.pending 0)
                        }
                    }
                    $result.total = $totalPass + $totalFail + $totalPending
                    $result.passed = $totalPass
                    $result.failed = $totalFail
                    $result.skipped = $totalPending
                    $result.duration_s = [math]::Round((Coalesce $pData.elapsed_seconds 0), 1)
                    $result.lastRun = (Get-Item $parallelResult).LastWriteTime.ToString("yyyy-MM-dd HH:mm:ss")
                    $result.status = if ($result.failed -eq 0) { "✅ 全部通过" } else { "❌ 有失败" }
                    $result.reportPath = $parallelResult
                    $found = $true
                }
            } catch {}
        }
    }

    # 回退：扫描 Cypress 运行日志（汇总全文件所有 spec 结果）
    if (-not $found) {
        $logFiles = @(
            "$RootDir\testing\tests\cypress-tests\cy-result.txt",
            "$rootDir\cy-out.txt",
            "$rootDir\cypress-run-results.txt"
        )
        foreach ($logFile in $logFiles) {
            if (Test-Path $logFile) {
                $content = Get-Content $logFile -Raw -Encoding UTF8
                # 汇总所有 spec 的 Tests/Passing/Failing/Pending（Cypress 每 spec 输出一次）
                $allTests = [regex]::Matches($content, "Tests:\s*(\d+)")
                $allPassing = [regex]::Matches($content, "Passing:\s*(\d+)")
                $allFailing = [regex]::Matches($content, "Failing:\s*(\d+)")
                $allPending = [regex]::Matches($content, "Pending:\s*(\d+)")
                if ($allTests.Count -gt 0) {
                    $sumTests = 0; foreach ($m in $allTests) { $sumTests += [int]$m.Groups[1].Value }
                    $sumPass = 0; foreach ($m in $allPassing) { $sumPass += [int]$m.Groups[1].Value }
                    $sumFail = 0; foreach ($m in $allFailing) { $sumFail += [int]$m.Groups[1].Value }
                    $sumPend = 0; foreach ($m in $allPending) { $sumPend += [int]$m.Groups[1].Value }
                    $result.total = $sumTests
                    $result.passed = $sumPass
                    $result.failed = $sumFail
                    $result.skipped = $sumPend
                    $result.lastRun = (Get-Item $logFile).LastWriteTime.ToString("yyyy-MM-dd HH:mm:ss")
                    $result.status = if ($result.failed -eq 0) { "✅ 全部通过" } else { "❌ 有失败" }
                    $result.reportPath = $logFile
                    $found = $true
                    break
                }
            }
        }
    }
    
    # 回退：计算用例文件数量作为展示（不计入执行 total）
    if (-not $found) {
        $specFiles = @(Get-ChildItem "$RootDir\testing\tests\cypress-tests\e2e" -Filter "*.cy.js" -Recurse -ErrorAction SilentlyContinue)
        if ($specFiles.Count -gt 0) {
            $result.status = "⚪ 仅统计文件数（未运行）"
            $result.details += "检测到 $($specFiles.Count) 个测试文件（未执行）"
        } else {
            $result.status = "⚪ 未运行或无报告"
        }
    }

    # 统计 cypress 测试文件数
    $cyFiles = @(Get-ChildItem "$RootDir\testing\tests\cypress-tests" -Filter "*.cy.js" -Recurse -ErrorAction SilentlyContinue)
    $result.fileCount = $cyFiles.Count
    $result.filePattern = "*.cy.js"

    # 扫描源码统计定义的用例数（it()）
    $defCount = 0
    $eFiles = @(Get-ChildItem "$RootDir\testing\tests\cypress-tests\e2e" -Filter "*.cy.js" -Recurse -ErrorAction SilentlyContinue)
    foreach ($f in $eFiles) {
        $content = Get-Content $f.FullName -Raw -ErrorAction SilentlyContinue
        if ($content) { $defCount += ([regex]::Matches($content, "\bit\s*\(")).Count }
    }
    $result.definedCases = $defCount
    
    return $result
}

# ═════════════════════════════════════════════════════════════════════════
# 3. Puppeteer 结果收集
# ═════════════════════════════════════════════════════════════════════════
function Collect-PuppeteerResults {
    $result = New-ToolResult -Name "puppeteer" -DisplayName "Puppeteer (性能监控测试)" -Icon "🤖"
    
    $reportDir = "$RootDir\testing\tests\puppeteer-tests\test-reports"
    $testReportDir = "$RootDir\testing\tests\test-reports\puppeteer-report"
    
    $possiblePaths = @(
        "$reportDir\jest-results.json",
        "$testReportDir\jest-results.json",
        "$reportDir\results.json",
        "$testReportDir\results.json"
    )
    
    $found = $false
    foreach ($path in $possiblePaths) {
        if (Test-Path $path) {
            try {
                $data = Get-Content $path -Raw -Encoding UTF8 | ConvertFrom-Json
                if ($null -ne $data.numTotalTests) {
                    $result.total = [int]$data.numTotalTests
                    $result.passed = [int]$data.numPassedTests
                    $result.failed = [int]$data.numFailedTests
                    $result.skipped = [int](Coalesce $data.numPendingTests 0)
                    $result.lastRun = (Get-Item $path).LastWriteTime.ToString("yyyy-MM-dd HH:mm:ss")
                    $result.status = if ($result.failed -eq 0) { "✅ 全部通过" } else { "❌ 有失败" }
                    $result.reportPath = $path
                    $found = $true
                    break
                }
                if ($null -ne $data.numTotalTestSuites) {
                    $result.total = [int]$data.numTotalTests
                    $result.passed = [int]$data.numPassedTests
                    $result.failed = [int]$data.numFailedTests
                    $result.skipped = [int](Coalesce $data.numPendingTests 0)
                    $result.lastRun = (Get-Item $path).LastWriteTime.ToString("yyyy-MM-dd HH:mm:ss")
                    $result.status = if ($result.failed -eq 0) { "✅ 全部通过" } else { "❌ 有失败" }
                    $result.reportPath = $path
                    $found = $true
                    break
                }
            } catch {}
        }
    }
    
    if (-not $found) {
        $perfReport = "$RootDir\testing\tests\puppeteer-tests\test-reports\performance-report.json"
        if (Test-Path $perfReport) {
            try {
                $data = Get-Content $perfReport -Raw -Encoding UTF8 | ConvertFrom-Json
                if ($data.pages) {
                    $result.total = ($data.pages | Measure-Object).Count
                    $result.passed = ($data.pages | Where-Object { $_.status -eq "pass" -or $_.loadTime -lt 3000 } | Measure-Object).Count
                    $result.failed = $result.total - $result.passed
                    $result.lastRun = (Get-Item $perfReport).LastWriteTime.ToString("yyyy-MM-dd HH:mm:ss")
                    $result.status = if ($result.failed -eq 0) { "✅ 全部通过" } else { "❌ 有失败" }
                    $result.reportPath = $perfReport
                    $found = $true
                }
            } catch {}
        }
    }
    
    # 优先读取 comprehensive-report.json（Puppeteer 综合报告，含多类子测试，数据最全）
    if (-not $found) {
        $compPaths = @(
            "$reportDir\puppeteer-report\comprehensive-report.json",
            "$reportDir\comprehensive-report.json",
            "$testReportDir\comprehensive-report.json"
        )
        foreach ($cp in $compPaths) {
            if (Test-Path $cp) {
                try {
                    $data = Get-Content $cp -Raw -Encoding UTF8 | ConvertFrom-Json
                    if ($null -ne $data.summary) {
                        # 汇总所有子类别（performance/visual/pagesRender/pagesPerfBatch）
                        # 注意：skipped 标记仅表示该子类不在本次实际运行中但有历史/预计算数据，
                        # 只要有 total > 0 的子类都应计入
                        $totalAll = 0; $passedAll = 0; $failedAll = 0
                        foreach ($cat in @("performance", "visual", "pagesRender", "pagesPerfBatch")) {
                            $sub = $data.summary.$cat
                            if ($null -ne $sub -and [int](Coalesce $sub.total 0) -gt 0) {
                                $totalAll += [int](Coalesce $sub.total 0)
                                $passedAll += [int](Coalesce $sub.passed 0)
                                $failedAll += [int](Coalesce $sub.failed 0)
                            }
                        }
                        if ($totalAll -gt 0) {
                            $result.total = $totalAll
                            $result.passed = $passedAll
                            $result.failed = $failedAll
                            $result.lastRun = (Get-Item $cp).LastWriteTime.ToString("yyyy-MM-dd HH:mm:ss")
                            $result.status = if ($failedAll -eq 0 -and $passedAll -gt 0) { "✅ 全部通过" } elseif ($passedAll -gt 0) { "❌ 有失败" } else { "⚠️ 全部跳过" }
                            $result.reportPath = $cp
                            $found = $true
                            break
                        }
                    }
                } catch {}
            }
        }
    }
    
    # 回退读取 summary.json（仅含单次性能测试的报告，数据量小于 comprehensive）
    if (-not $found) {
        $summaryPaths = @(
            "$reportDir\puppeteer-report\summary.json",
            "$reportDir\summary.json",
            "$testReportDir\summary.json"
        )
        foreach ($sp in $summaryPaths) {
            if (Test-Path $sp) {
                try {
                    $data = Get-Content $sp -Raw -Encoding UTF8 | ConvertFrom-Json
                    if ($null -ne $data.total) {
                        $result.total = [int](Coalesce $data.total 0)
                        $result.passed = [int](Coalesce $data.passed 0)
                        $result.failed = [int](Coalesce $data.failed 0)
                        $result.skipped = [int](Coalesce $data.skipped 0)
                        $result.lastRun = (Get-Item $sp).LastWriteTime.ToString("yyyy-MM-dd HH:mm:ss")
                        $result.status = if ($result.failed -eq 0 -and $result.passed -gt 0) { "✅ 全部通过" } elseif ($result.passed -gt 0) { "❌ 有失败" } else { "⚠️ 全部跳过" }
                        $result.reportPath = $sp
                        $found = $true
                        break
                    }
                } catch {}
            }
        }
    }

    # 也尝试 visual-summary.json / pages-render-summary.json / pages-performance-batch-summary.json
    if (-not $found) {
        $otherSummaries = @(
            "$reportDir\puppeteer-report\visual-summary.json",
            "$reportDir\puppeteer-report\pages-render-summary.json",
            "$reportDir\puppeteer-report\pages-performance-batch-summary.json"
        )
        foreach ($os in $otherSummaries) {
            if (Test-Path $os) {
                try {
                    $data = Get-Content $os -Raw -Encoding UTF8 | ConvertFrom-Json
                    if ($null -ne $data.total) {
                        $result.total += [int](Coalesce $data.total 0)
                        $result.passed += [int](Coalesce $data.passed 0)
                        $result.failed += [int](Coalesce $data.failed 0)
                        $result.lastRun = (Get-Item $os).LastWriteTime.ToString("yyyy-MM-dd HH:mm:ss")
                        $found = $true
                    }
                } catch {}
            }
        }
        if ($found) {
            $result.status = if ($result.failed -eq 0 -and $result.passed -gt 0) { "✅ 全部通过" } elseif ($result.passed -gt 0) { "❌ 有失败" } else { "⚠️ 全部跳过" }
            $result.reportPath = ($otherSummaries | Where-Object { Test-Path $_ } | Select-Object -First 1)
        }
    }
    
    if (-not $found) {
        $result.status = "⚪ 未运行或无报告"
    }

    # 统计 puppeteer 测试文件数
    $ppFiles = @(Get-ChildItem "$RootDir\testing\tests\puppeteer-tests\tests" -Filter "*.test.js" -Recurse -ErrorAction SilentlyContinue)
    $result.fileCount = $ppFiles.Count
    $result.filePattern = "*.test.js"

    # 扫描源码统计定义的用例数（it() / test()）
    $defCount = 0
    foreach ($f in $ppFiles) {
        $content = Get-Content $f.FullName -Raw -ErrorAction SilentlyContinue
        if ($content) { $defCount += ([regex]::Matches($content, "\b(it|test)\s*\(")).Count }
    }
    $result.definedCases = $defCount
    
    return $result
}

# ═════════════════════════════════════════════════════════════════════════
# 4. Selenium 结果收集
# ═════════════════════════════════════════════════════════════════════════
function Collect-SeleniumResults {
    $result = New-ToolResult -Name "selenium" -DisplayName "Selenium (跨浏览器兼容测试)" -Icon "🌐"
    
    $found = $false
    
    # 尝试 JUnit XML
    $junitPath = "$RootDir\testing\tests\selenium-tests\junit.xml"
    if (Test-Path $junitPath) {
        try {
            [xml]$xml = Get-Content $junitPath -Encoding UTF8
            # 兼容两种结构：<testsuite tests="..."> 或 <testsuites><testsuite tests="...">
            $suite = if ($xml.testsuite) { $xml.testsuite }
                     elseif ($xml.testsuites.testsuite) { $xml.testsuites.testsuite }
                     elseif ($xml.testsuites) { $xml.testsuites }
                     else { $null }
            if ($suite) {
                # 若 suite 是数组（多个 testsuite），汇总求和
                $allSuites = @($suite)
                $totalTests   = ($allSuites | ForEach-Object { [int](Coalesce $_.tests 0) } | Measure-Object -Sum).Sum
                $totalFailed  = ($allSuites | ForEach-Object { [int](Coalesce $_.failures 0) + [int](Coalesce $_.errors 0) } | Measure-Object -Sum).Sum
                $totalSkipped = ($allSuites | ForEach-Object { [int](Coalesce $_.skipped 0) } | Measure-Object -Sum).Sum
                $totalTime    = ($allSuites | ForEach-Object { [double](Coalesce $_.time 0) } | Measure-Object -Sum).Sum
                $result.total      = $totalTests
                $result.failed     = $totalFailed
                $result.skipped    = $totalSkipped
                $result.passed     = $result.total - $result.failed - $result.skipped
                $result.duration_s = [math]::Round($totalTime, 1)
                $result.lastRun    = (Get-Item $junitPath).LastWriteTime.ToString("yyyy-MM-dd HH:mm:ss")
                $result.status     = if ($result.failed -eq 0) { "✅ 全部通过" } else { "❌ 有失败" }
                $result.reportPath = $junitPath
                $found = $true
            }
        } catch {}
    }
    
    if (-not $found) {
        # 扫描生成的测试文件计数作为估算（仅记录到 definedCases，不计入执行 total）
        $testFiles = Get-ChildItem "$RootDir\testing\tests\selenium-tests\tests" -Filter "*.py" -Recurse -ErrorAction SilentlyContinue
        if ($testFiles) {
            $totalFunctions = 0
            foreach ($f in $testFiles) {
                $content = Get-Content $f.FullName -Raw -ErrorAction SilentlyContinue
                if ($content) {
                    $m = [regex]::Matches($content, "def test_")
                    $totalFunctions += $m.Count
                }
            }
            if ($totalFunctions -gt 0) {
                # 注意：不设置 $result.total，避免未执行的用例数虚高分母
                $result.status = "⚪ 仅统计用例数（未运行）"
                $result.details += "检测到 $totalFunctions 个测试用例（未执行）"
            }
        }
    }
    
    if (-not $found -and $result.total -eq 0) {
        $result.status = "⚪ 未运行或无报告"
    }

    # 统计 selenium 测试文件数
    $seFiles = @(Get-ChildItem "$RootDir\testing\tests\selenium-tests\tests" -Filter "test_*.py" -Recurse -ErrorAction SilentlyContinue |
        Where-Object { $_.FullName -notmatch "__pycache__" })
    $result.fileCount = $seFiles.Count
    $result.filePattern = "test_*.py"

    # 扫描源码统计定义的用例数（def test_）
    $defCount = 0
    foreach ($f in $seFiles) {
        $content = Get-Content $f.FullName -Raw -ErrorAction SilentlyContinue
        if ($content) { $defCount += ([regex]::Matches($content, "def test_")).Count }
    }
    $result.definedCases = $defCount
    
    return $result
}

# ═════════════════════════════════════════════════════════════════════════
# 5. Playwright 结果收集
# ═════════════════════════════════════════════════════════════════════════
function Collect-PlaywrightResults {
    $result = New-ToolResult -Name "playwright" -DisplayName "Playwright (E2E端到端测试)" -Icon "🎭"
    
    $possiblePaths = @(
        "$RootDir\testing\tests\test-reports\playwright-report\results.json",
        "$RootDir\testing\tests\playwright-tests\test-results\results.json",
        "$RootDir\testing\tests\playwright-tests\playwright-report\results.json"
    )
    
    $found = $false
    foreach ($path in $possiblePaths) {
        if (Test-Path $path) {
            try {
                $data = Get-Content $path -Raw -Encoding UTF8 | ConvertFrom-Json
                if ($data.suites) {
                    # Playwright JSON 结构 - 递归提取所有测试
                    $script:allTests = @()
                    function Get-AllSpecs($suites) {
                        foreach ($s in $suites) {
                            if ($s.specs) {
                                foreach ($spec in $s.specs) {
                                    if ($spec.tests) {
                                        foreach ($test in $spec.tests) {
                                            $script:allTests += $test
                                        }
                                    }
                                }
                            }
                            if ($s.suites) { Get-AllSpecs $s.suites }
                        }
                    }
                    Get-AllSpecs $data.suites
                    
                    $result.total = $script:allTests.Count
                    $result.passed = ($script:allTests | Where-Object { $_.status -eq "expected" -or $_.status -eq "flaky" }).Count
                    $result.failed = ($script:allTests | Where-Object { $_.status -eq "unexpected" }).Count
                    $result.skipped = ($script:allTests | Where-Object { $_.status -eq "skipped" }).Count
                    $result.duration_s = [math]::Round((Coalesce $data.stats.duration 0) / 1000, 1)
                    $result.lastRun = (Get-Item $path).LastWriteTime.ToString("yyyy-MM-dd HH:mm:ss")
                    # 全部跳过且 0 通过 = globalSetup 失败或测试被强制跳过，不能算"通过"
                    $result.status = if ($result.total -eq 0) { "⚠️ 零执行（报告无记录）" } elseif ($result.passed -eq 0 -and $result.failed -eq 0 -and $result.skipped -gt 0) { "⚠️ 零执行（全部跳过，疑似 globalSetup 失败）" } elseif ($result.failed -eq 0) { "✅ 全部通过" } else { "❌ 有失败" }
                    $result.reportPath = $path
                    $found = $true
                    break
                }
                if ($data.stats) {
                    $result.total = [int](Coalesce $data.stats.expected 0) + [int](Coalesce $data.stats.unexpected 0) + [int](Coalesce $data.stats.skipped 0) + [int](Coalesce $data.stats.flaky 0)
                    $result.passed = [int](Coalesce $data.stats.expected 0) + [int](Coalesce $data.stats.flaky 0)
                    $result.failed = [int](Coalesce $data.stats.unexpected 0)
                    $result.skipped = [int](Coalesce $data.stats.skipped 0)
                    $result.duration_s = [math]::Round((Coalesce $data.stats.duration 0) / 1000, 1)
                    $result.lastRun = (Get-Item $path).LastWriteTime.ToString("yyyy-MM-dd HH:mm:ss")
                    # 全部跳过且 0 通过 = globalSetup 失败或测试被强制跳过，不能算"通过"
                    $result.status = if ($result.total -eq 0) { "⚠️ 零执行（报告无记录）" } elseif ($result.passed -eq 0 -and $result.failed -eq 0 -and $result.skipped -gt 0) { "⚠️ 零执行（全部跳过，疑似 globalSetup 失败）" } elseif ($result.failed -eq 0) { "✅ 全部通过" } else { "❌ 有失败" }
                    $result.reportPath = $path
                    $found = $true
                    break
                }
            } catch {}
        }
    }
    
    # 回退：JUnit XML
    if (-not $found) {
        $junitPath = "$RootDir\testing\tests\test-reports\playwright-report\junit.xml"
        if (Test-Path $junitPath) {
            try {
                [xml]$xml = Get-Content $junitPath -Encoding UTF8
                $suites = $xml.testsuites
                if ($suites) {
                    $result.total = [int](Coalesce $suites.tests 0)
                    $result.failed = [int](Coalesce $suites.failures 0) + [int](Coalesce $suites.errors 0)
                    $result.skipped = [int](Coalesce $suites.skipped 0)
                    $result.passed = $result.total - $result.failed - $result.skipped
                    $result.duration_s = [math]::Round([double](Coalesce $suites.time 0), 1)
                    $result.lastRun = (Get-Item $junitPath).LastWriteTime.ToString("yyyy-MM-dd HH:mm:ss")
                    # 全部跳过且 0 通过 = globalSetup 失败或测试被强制跳过，不能算"通过"
                    $result.status = if ($result.total -eq 0) { "⚠️ 零执行（报告无记录）" } elseif ($result.passed -eq 0 -and $result.failed -eq 0 -and $result.skipped -gt 0) { "⚠️ 零执行（全部跳过，疑似 globalSetup 失败）" } elseif ($result.failed -eq 0) { "✅ 全部通过" } else { "❌ 有失败" }
                    $result.reportPath = $junitPath
                    $found = $true
                }
            } catch {}
        }
    }
    
    if (-not $found) {
        $result.status = "⚪ 未运行或无报告"
    }

    # 统计 playwright 测试文件数
    $pwFiles = @(Get-ChildItem "$RootDir\testing\tests\playwright-tests\tests" -Filter "*.spec.ts" -Recurse -ErrorAction SilentlyContinue)
    $result.fileCount = $pwFiles.Count
    $result.filePattern = "*.spec.ts"

    # 扫描源码统计定义的用例数（只匹配 test('xxx') 或 test("xxx")，排除 test.describe/test.beforeEach 等）
    $defCount = 0
    foreach ($f in $pwFiles) {
        $content = Get-Content $f.FullName -Raw -ErrorAction SilentlyContinue
        if ($content) { $defCount += ([regex]::Matches($content, "\btest\s*\(['""`]")).Count }
    }
    $result.definedCases = $defCount
    
    return $result
}

# ═════════════════════════════════════════════════════════════════════════
# 6. K6 结果收集
# ═════════════════════════════════════════════════════════════════════════
function Collect-K6Results {
    $result = New-ToolResult -Name "k6" -DisplayName "K6 (性能压力测试)" -Icon "⚡"
    
    $found = $false
    
    # 合并所有 K6 结果文件（支持 summary JSON 和 NDJSON 两种格式）
    $k6ResultsDir = "$RootDir\testing\k6\results"
    if (Test-Path $k6ResultsDir) {
        $jsonFiles = Get-ChildItem $k6ResultsDir -Filter "*.json" -ErrorAction SilentlyContinue | Sort-Object LastWriteTime -Descending
        if ($jsonFiles) {
            $totalChecks = 0
            $passedChecks = 0
            $failedChecks = 0
            $totalRequests = 0
            $latestTime = $null
            
            foreach ($jf in $jsonFiles) {
                try {
                    # 检测文件格式：读取第一行判断是否为 NDJSON
                    $firstLine = Get-Content $jf.FullName -First 1 -Encoding UTF8
                    $firstObj = $firstLine | ConvertFrom-Json -ErrorAction SilentlyContinue
                    
                    if ($firstObj -and ($firstObj.type -eq "Metric" -or $firstObj.metric)) {
                        # ── NDJSON 格式（k6 --out json 输出，每行一个 JSON 对象）──
                        # 用 Select-String 高效提取 checks 和 http_reqs 数据点
                        $checkLines = Select-String -Path $jf.FullName -Pattern '"metric":"checks","type":"Point"' -SimpleMatch
                        foreach ($cl in $checkLines) {
                            $obj = $cl.Line | ConvertFrom-Json -ErrorAction SilentlyContinue
                            if ($obj -and $obj.data) {
                                if ([int]$obj.data.value -eq 1) { $passedChecks++ } else { $failedChecks++ }
                                $totalChecks++
                            }
                        }
                        $httpLines = Select-String -Path $jf.FullName -Pattern '"metric":"http_reqs","type":"Point"' -SimpleMatch
                        $totalRequests += $httpLines.Count
                    } else {
                        # ── 标准 summary JSON 格式（handleSummary 输出）──
                        $data = Get-Content $jf.FullName -Raw -Encoding UTF8 | ConvertFrom-Json
                        if ($data.metrics) {
                            if ($data.metrics.checks) {
                                $passes = [int](Coalesce $data.metrics.checks.values.passes 0)
                                $fails = [int](Coalesce $data.metrics.checks.values.fails 0)
                                $totalChecks += ($passes + $fails)
                                $passedChecks += $passes
                                $failedChecks += $fails
                            }
                            if ($data.metrics.http_reqs) {
                                $totalRequests += [int](Coalesce $data.metrics.http_reqs.values.count 0)
                            }
                        }
                        if ($data.root_group -and $data.root_group.checks) {
                            foreach ($check in $data.root_group.checks) {
                                $totalChecks += [int](Coalesce $check.passes 0) + [int](Coalesce $check.fails 0)
                                $passedChecks += [int](Coalesce $check.passes 0)
                                $failedChecks += [int](Coalesce $check.fails 0)
                            }
                        }
                    }
                    if ($null -eq $latestTime -or $jf.LastWriteTime -gt $latestTime) {
                        $latestTime = $jf.LastWriteTime
                    }
                } catch {}
            }
            
            if ($totalChecks -gt 0 -or $totalRequests -gt 0) {
                $result.total = $totalChecks
                $result.passed = $passedChecks
                $result.failed = $failedChecks
                $result.lastRun = $latestTime.ToString("yyyy-MM-dd HH:mm:ss")
                $result.status = if ($failedChecks -eq 0) { "✅ 全部通过" } else { "❌ 有失败" }
                $result.details += "HTTP请求总数: $totalRequests"
                $result.reportPath = $k6ResultsDir
                $found = $true
            }
        }
    }
    
    # 回退：从 combined-results.json
    if (-not $found) {
        $combined = "$rootDir\TestResults\combined-results.json"
        if (Test-Path $combined) {
            try {
                $data = Get-Content $combined -Raw -Encoding utf8 | ConvertFrom-Json
                if ($data.tools.k6) {
                    $k = $data.tools.k6
                    $result.total = [int](Coalesce $k.total 0)
                    $result.passed = [int](Coalesce $k.passed 0)
                    $result.failed = [int](Coalesce $k.failed 0)
                    $result.lastRun = $data.timestamp
                    if ($result.total -gt 0 -and $result.failed -eq 0) {
                        $result.status = "✅ 全部通过"
                    } elseif ($result.total -eq 0) {
                        $result.status = "⚪ 未运行"
                    } else {
                        $result.status = "❌ 有失败"
                    }
                    $result.reportPath = $combined
                    $found = $true
                }
            } catch {}
        }
    }
    
    if (-not $found) {
        $result.status = "⚪ 未运行或无报告"
    }

    # 统计 k6 场景文件数
    $k6Files = @(Get-ChildItem "$RootDir\testing\k6\scenarios" -Filter "*.js" -Recurse -ErrorAction SilentlyContinue)
    $result.fileCount = $k6Files.Count
    $result.filePattern = "*.js"

    # 扫描源码统计定义的检查点数（check()）
    $defCount = 0
    foreach ($f in $k6Files) {
        $content = Get-Content $f.FullName -Raw -ErrorAction SilentlyContinue
        if ($content) { $defCount += ([regex]::Matches($content, "check\s*\(")).Count }
    }
    $result.definedCases = $defCount
    
    return $result
}

# ═════════════════════════════════════════════════════════════════════════
# 主收集流程
# ═════════════════════════════════════════════════════════════════════════
Write-Host "`n  📊 六类测试结果收集器`n" -ForegroundColor Cyan

$results = [ordered]@{}
$toolCollectors = [ordered]@{
    pytest     = { Collect-PytestResults }
    cypress    = { Collect-CypressResults }
    puppeteer  = { Collect-PuppeteerResults }
    selenium   = { Collect-SeleniumResults }
    playwright = { Collect-PlaywrightResults }
    k6         = { Collect-K6Results }
}

foreach ($toolName in $toolCollectors.Keys) {
    if ($Tool -eq "all" -or $Tool -eq $toolName) {
        Write-Host "  收集 $toolName 结果..." -NoNewline
        $r = & $toolCollectors[$toolName]
        $results[$toolName] = $r
        $std = $standardCases[$toolName]
        $color = if ($r.status -match "✅") { "Green" } elseif ($r.status -match "❌") { "Red" } else { "Yellow" }
        Write-Host " $($r.status) (文件:$($r.fileCount) 标准用例数:$std 实际用例数:$($r.definedCases) 执行用例数:$($r.total) 通过:$($r.passed) 失败:$($r.failed) 跳过:$($r.skipped))" -ForegroundColor $color
    }
}

# 聚合总计
$grandDefined = ($results.Values | ForEach-Object { $_.definedCases } | Measure-Object -Sum).Sum
$grandTotal = ($results.Values | ForEach-Object { $_.total } | Measure-Object -Sum).Sum
$grandPassed = ($results.Values | ForEach-Object { $_.passed } | Measure-Object -Sum).Sum
$grandFailed = ($results.Values | ForEach-Object { $_.failed } | Measure-Object -Sum).Sum
$grandSkipped = ($results.Values | ForEach-Object { $_.skipped } | Measure-Object -Sum).Sum
$grandFiles = ($results.Values | ForEach-Object { $_.fileCount } | Measure-Object -Sum).Sum
$passRateDenom = $grandPassed + $grandFailed
$passRate = if ($passRateDenom -gt 0) { [math]::Round($grandPassed / $passRateDenom * 100, 1) } else { if ($grandTotal -gt 0) { 100 } else { 0 } }

$output = [ordered]@{
    timestamp     = (Get-Date).ToString("yyyy-MM-dd HH:mm:ss")
    version       = "2.2"
    tools         = $results
    summary       = [ordered]@{
        total_tools        = $results.Count
        total_files        = $grandFiles
        total_defined_cases = $grandDefined
        total_cases        = $grandTotal
        total_passed       = $grandPassed
        total_failed       = $grandFailed
        total_skipped      = $grandSkipped
        pass_rate          = $passRate
    }
}

# 写入 JSON
$output | ConvertTo-Json -Depth 10 | Out-File $OutputPath -Encoding UTF8
Write-Host "`n  ✅ 结果已保存: $OutputPath" -ForegroundColor Green
Write-Host "  📊 总计: $grandFiles 文件 | 实际用例数: $grandDefined | 执行用例数: $grandTotal | 通过: $grandPassed | 失败: $grandFailed | 跳过: $grandSkipped | 通过率: $($passRate)%`n" -ForegroundColor Cyan
