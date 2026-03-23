<#
.SYNOPSIS
    六类测试并行执行引擎 - 全部工具同时跑，失败不阻塞，统一收集
.DESCRIPTION
    核心理念：
    1. 并行启动：6 个工具同时以后台 Job 方式执行，互不阻塞
    2. 实时监控：主进程轮询各 Job 状态，实时显示进度
    3. 失败隔离：单工具失败不影响其他工具继续执行
    4. 统一收集：所有工具完成后，汇总失败用例清单
    5. 精准重跑：只重跑失败用例，不重跑整个 suite

    时间对比（full 级别）：
    - 串行: pytest(12m) + Cypress(8m) + Playwright(34m) + Selenium(40m) + Puppeteer(12m) + K6(18m) ≈ 124 分钟
    - 并行: max(所有工具) ≈ 40 分钟（节省 67%）
.PARAMETER Level
    smoke    : 冒烟（约3分钟）   - pytest@smoke + K6@smoke 并行
    quick    : 快速（约12分钟）  - pytest + Cypress + K6@smoke 并行
    standard : 标准（约25分钟）  - pytest + Cypress + Playwright@Chromium + K6@load 并行
    full     : 完整（约40分钟）  - 全6类核心场景并行
    ultimate : 终极（约60分钟）  - 全6类全场景并行
.PARAMETER SkipInstall
    跳过依赖安装检查
.PARAMETER TimeoutMinutes
    全局超时（分钟），超时后强制终止所有 Job
.PARAMETER RetryFailed
    自动重试失败的用例（仅重跑失败，不重跑全量）
.PARAMETER MaxRetries
    最大重试次数
.EXAMPLE
    .\run-parallel-tests.ps1 -Level smoke
    .\run-parallel-tests.ps1 -Level full
    .\run-parallel-tests.ps1 -Level full -RetryFailed -MaxRetries 2
    .\run-parallel-tests.ps1 -Level ultimate -TimeoutMinutes 90
#>
param(
    [ValidateSet("smoke", "quick", "standard", "full", "ultimate")]
    [string]$Level = "standard",
    [switch]$SkipInstall,
    [int]$TimeoutMinutes = 120,
    [switch]$RetryFailed,
    [int]$MaxRetries = 1
)

$ErrorActionPreference = "Continue"
$script:StartTime = Get-Date
$script:RootDir = (Resolve-Path "$PSScriptRoot\..").Path
$script:ResultsDir = Join-Path $script:RootDir "TestResults"
$script:FailuresDir = Join-Path $script:ResultsDir "failures"

# 加载测试环境变量
$envScript = Join-Path $script:RootDir "testing\tests\set-test-env.ps1"
if (Test-Path $envScript) { . $envScript }

# 确保输出目录存在
New-Item -Path $script:ResultsDir -ItemType Directory -Force | Out-Null
New-Item -Path $script:FailuresDir -ItemType Directory -Force | Out-Null

# ═══════════════════════════════════════════════
# 颜色输出
# ═══════════════════════════════════════════════
function Write-Banner {
    param($msg)
    Write-Host "`n╔══════════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
    Write-Host "║  $($msg.PadRight(62))║" -ForegroundColor Cyan
    Write-Host "╚══════════════════════════════════════════════════════════════════╝`n" -ForegroundColor Cyan
}
function Write-Step { param($msg) Write-Host "  ─── $msg ───" -ForegroundColor Cyan }
function Write-Progress { param($msg) Write-Host "  ⏳ $msg" -ForegroundColor DarkGray }
function Write-OK { param($msg) Write-Host "  ✅ $msg" -ForegroundColor Green }
function Write-Fail { param($msg) Write-Host "  ❌ $msg" -ForegroundColor Red }
function Write-Warn { param($msg) Write-Host "  ⚠️ $msg" -ForegroundColor Yellow }
function Write-Info { param($msg) Write-Host "  ℹ️ $msg" -ForegroundColor Gray }

# ═══════════════════════════════════════════════
# 每个工具的执行命令定义
# ═══════════════════════════════════════════════
function Get-ToolCommands {
    param([string]$Level)

    $root = $script:RootDir
    $results = $script:ResultsDir

    # 基础命令映射（每个工具 → 对应命令和工作目录）
    $tools = [ordered]@{}

    # ── pytest ──
    switch ($Level) {
        "smoke" {
            $tools["pytest"] = @{
                Cmd = "cd '$root\testing\tests'; python -m pytest -x -v -m smoke --tb=short --junitxml='$results\pytest-results.xml' --timeout=30 -q 2>&1"
                Desc = "API冒烟 (smoke标记)"
                ExpectedMin = 2
            }
        }
        "quick" {
            $tools["pytest"] = @{
                Cmd = "cd '$root\testing\tests'; python -m pytest -v --tb=short --junitxml='$results\pytest-results.xml' -n auto --timeout=60 -q 2>&1"
                Desc = "全量API (4 workers并行)"
                ExpectedMin = 10
            }
        }
        default {
            $tools["pytest"] = @{
                Cmd = "cd '$root\testing\tests'; python -m pytest -v --tb=short --junitxml='$results\pytest-results.xml' -n auto --timeout=60 -q 2>&1"
                Desc = "全量API (4 workers并行)"
                ExpectedMin = 12
            }
        }
    }

    # ── Cypress ── (quick 及以上)
    if ($Level -in @("quick", "standard", "full", "ultimate")) {
        $tools["cypress"] = @{
            Cmd = "cd '$root\testing\tests\cypress-tests'; npx cypress run --reporter json --reporter-options output='$results\cypress-results.json' 2>&1"
            Desc = "组件交互测试"
            ExpectedMin = 8
        }
    }

    # ── Playwright ──
    if ($Level -eq "standard") {
        $tools["playwright"] = @{
            Cmd = "cd '$root\testing\tests\playwright-tests'; npx playwright test --project=chromium --reporter=json 2>&1"
            Desc = "E2E Chromium"
            ExpectedMin = 10
        }
    }
    if ($Level -eq "full") {
        $tools["playwright"] = @{
            Cmd = "cd '$root\testing\tests\playwright-tests'; npx playwright test --reporter=json 2>&1"
            Desc = "跨浏览器E2E (Chromium+Firefox+WebKit)"
            ExpectedMin = 34
        }
    }
    if ($Level -eq "ultimate") {
        $tools["playwright"] = @{
            Cmd = "cd '$root\testing\tests\playwright-tests'; npx playwright test --reporter=json 2>&1"
            Desc = "全浏览器E2E (含移动端)"
            ExpectedMin = 40
        }
    }

    # ── Selenium ── (full/ultimate)
    if ($Level -in @("full", "ultimate")) {
        $tools["selenium"] = @{
            Cmd = @"
cd '$root\testing\tests\selenium-tests'
`$grid = docker ps --filter 'name=selenium-hub' --format '{{.Names}}' 2>`$null
if (-not `$grid) {
    docker-compose -f selenium-grid-config.yml up -d 2>&1 | Out-Null
    Start-Sleep -Seconds 15
}
python -m pytest testing/tests/test_cross_browser.py -v --tb=short --junitxml='$results\selenium-results.xml' --timeout=120 2>&1
"@
            Desc = "多浏览器兼容性 (Grid 3节点×5并发)"
            ExpectedMin = 40
        }
    }

    # ── Puppeteer ── (full/ultimate)
    if ($Level -in @("full", "ultimate")) {
        $pCmd = if ($Level -eq "ultimate") { "npm run test:all" } else { "npm run test:performance" }
        $tools["puppeteer"] = @{
            Cmd = "cd '$root\testing\tests\puppeteer-tests'; $pCmd 2>&1"
            Desc = $(if ($Level -eq "ultimate") { "性能+视觉回归" } else { "性能基准" })
            ExpectedMin = $(if ($Level -eq "ultimate") { 20 } else { 12 })
        }
    }

    # ── K6 ──
    switch ($Level) {
        "smoke" {
            $tools["k6"] = @{
                Cmd = "cd '$root\testing\k6'; k6 run scenarios/smoke-test.js --summary-export='$results\k6-results.json' 2>&1"
                Desc = "API冒烟压测"
                ExpectedMin = 2
            }
        }
        "quick" {
            $tools["k6"] = @{
                Cmd = "cd '$root\testing\k6'; k6 run scenarios/smoke-test.js --summary-export='$results\k6-results.json' 2>&1"
                Desc = "API冒烟压测"
                ExpectedMin = 2
            }
        }
        "standard" {
            $tools["k6"] = @{
                Cmd = "cd '$root\testing\k6'; k6 run scenarios/load-test.js --summary-export='$results\k6-results.json' 2>&1"
                Desc = "负载测试"
                ExpectedMin = 20
            }
        }
        "full" {
            $tools["k6"] = @{
                Cmd = "cd '$root\testing\k6'; k6 run scenarios/stress-test.js --summary-export='$results\k6-results.json' 2>&1"
                Desc = "压力测试"
                ExpectedMin = 18
            }
        }
        "ultimate" {
            $tools["k6"] = @{
                Cmd = "cd '$root\testing\k6'; k6 run scenarios/comprehensive-test.js --summary-export='$results\k6-results.json' 2>&1"
                Desc = "综合压测"
                ExpectedMin = 25
            }
        }
    }

    return $tools
}

# ═══════════════════════════════════════════════
# 并行执行核心
# ═══════════════════════════════════════════════
function Start-ParallelTests {
    param([hashtable]$Tools)

    $jobs = @{}
    $logFiles = @{}

    Write-Step "并行启动 $($Tools.Count) 个工具"

    foreach ($name in $Tools.Keys) {
        $tool = $Tools[$name]
        $logFile = Join-Path $script:ResultsDir "$name-output.log"
        $logFiles[$name] = $logFile

        $icon = switch ($name) {
            "pytest"     { "🐍" }
            "cypress"    { "🌲" }
            "playwright" { "🎭" }
            "selenium"   { "🌐" }
            "puppeteer"  { "🤖" }
            "k6"         { "⚡" }
            default      { "🧪" }
        }

        Write-Host "  $icon 启动 $($name.ToUpper().PadRight(12)) → $($tool.Desc) (预计 $($tool.ExpectedMin)m)" -ForegroundColor White

        # 将命令封装为 ScriptBlock 并作为后台 Job 启动
        $cmd = $tool.Cmd
        $log = $logFile
        $envScript = Join-Path $script:RootDir "testing\tests\set-test-env.ps1"

        $job = Start-Job -ScriptBlock {
            param($Command, $LogFile, $EnvScript)

            $ErrorActionPreference = "Continue"

            # 加载测试环境变量
            if (Test-Path $EnvScript) { . $EnvScript }

            $startTime = Get-Date
            try {
                $output = Invoke-Expression $Command
                $exitCode = $LASTEXITCODE
                if ($null -eq $exitCode) { $exitCode = 0 }
            } catch {
                $output = $_.ToString()
                $exitCode = 1
            }
            $duration = [math]::Round(((Get-Date) - $startTime).TotalMinutes, 1)

            # 写入日志文件
            $output | Out-File -FilePath $LogFile -Encoding UTF8 -Force

            # 返回结果对象
            [PSCustomObject]@{
                ExitCode = $exitCode
                Duration = $duration
                OutputFile = $LogFile
            }
        } -ArgumentList $cmd, $log, $envScript

        $jobs[$name] = @{
            Job = $job
            StartTime = Get-Date
            ExpectedMin = $tool.ExpectedMin
            Desc = $tool.Desc
        }
    }

    Write-Host ""
    return $jobs, $logFiles
}

# ═══════════════════════════════════════════════
# 实时监控进度
# ═══════════════════════════════════════════════
function Watch-Jobs {
    param($Jobs, $TimeoutMinutes)

    $deadline = (Get-Date).AddMinutes($TimeoutMinutes)
    $completed = @{}
    $statusIcons = @{
        "Running"   = "🔄"
        "Completed" = "✅"
        "Failed"    = "❌"
        "Stopped"   = "⛔"
    }

    Write-Step "等待所有工具完成 (超时: ${TimeoutMinutes}m)"
    Write-Host ""

    while ($completed.Count -lt $Jobs.Count) {
        # 检查超时
        if ((Get-Date) -gt $deadline) {
            Write-Warn "全局超时 ${TimeoutMinutes} 分钟已到，强制终止剩余 Job"
            foreach ($name in $Jobs.Keys) {
                if (-not $completed.Contains($name)) {
                    Stop-Job -Job $Jobs[$name].Job -PassThru | Out-Null
                    $completed[$name] = "timeout"
                }
            }
            break
        }

        # 检查每个 Job 状态
        foreach ($name in $Jobs.Keys) {
            if ($completed.Contains($name)) { continue }

            $jobInfo = $Jobs[$name]
            $job = $jobInfo.Job

            if ($job.State -ne "Running") {
                $elapsed = [math]::Round(((Get-Date) - $jobInfo.StartTime).TotalMinutes, 1)

                if ($job.State -eq "Completed") {
                    $result = Receive-Job -Job $job
                    if ($result.ExitCode -eq 0) {
                        Write-OK "$($name.ToUpper().PadRight(12)) 完成 ── ${elapsed}m (预计 $($jobInfo.ExpectedMin)m)"
                        $completed[$name] = "passed"
                    } else {
                        Write-Fail "$($name.ToUpper().PadRight(12)) 失败 ── ${elapsed}m (退出码: $($result.ExitCode))"
                        $completed[$name] = "failed"
                    }
                } else {
                    Write-Fail "$($name.ToUpper().PadRight(12)) 异常终止 ── 状态: $($job.State)"
                    $completed[$name] = "error"
                }
            }
        }

        # 显示剩余工具状态
        if ($completed.Count -lt $Jobs.Count) {
            $remaining = ($Jobs.Keys | Where-Object { -not $completed.Contains($_) }) -join ", "
            $elapsed = [math]::Round(((Get-Date) - $script:StartTime).TotalMinutes, 1)
            Write-Host "`r  ⏳ ${elapsed}m 已过 | 剩余: $remaining" -NoNewline -ForegroundColor DarkGray
            Start-Sleep -Seconds 5
        }
    }

    Write-Host ""
    return $completed
}

# ═══════════════════════════════════════════════
# 解析失败用例
# ═══════════════════════════════════════════════
function Collect-Failures {
    param($Completed, $LogFiles)

    $failures = [ordered]@{}

    foreach ($name in $Completed.Keys) {
        if ($Completed[$name] -notin @("failed", "error", "timeout")) { continue }
        
        $logFile = $LogFiles[$name]
        if (-not (Test-Path $logFile)) { continue }

        $content = Get-Content $logFile -Raw -Encoding UTF8 -ErrorAction SilentlyContinue
        if (-not $content) { continue }

        $toolFailures = @()

        switch ($name) {
            "pytest" {
                # 从 pytest 输出提取 FAILED 行
                $failedLines = $content -split "`n" | Where-Object { $_ -match "^FAILED " }
                foreach ($line in $failedLines) {
                    if ($line -match "^FAILED (.+?)(?:\s+-\s+(.+))?$") {
                        $toolFailures += [PSCustomObject]@{
                            TestId = $Matches[1].Trim()
                            Reason = if ($Matches[2]) { $Matches[2].Trim() } else { "未知" }
                        }
                    }
                }
                # 也提取 ERROR 行
                $errorLines = $content -split "`n" | Where-Object { $_ -match "^ERROR " }
                foreach ($line in $errorLines) {
                    $toolFailures += [PSCustomObject]@{
                        TestId = $line.Trim()
                        Reason = "ERROR"
                    }
                }
            }
            "cypress" {
                # 从 Cypress JSON 或输出提取失败
                $failedLines = $content -split "`n" | Where-Object { $_ -match "failing|✗|×|AssertionError" }
                foreach ($line in $failedLines) {
                    $toolFailures += [PSCustomObject]@{
                        TestId = $line.Trim().Substring(0, [Math]::Min($line.Trim().Length, 200))
                        Reason = "Cypress 断言失败"
                    }
                }
            }
            "playwright" {
                # 从 Playwright 输出提取失败
                $failedLines = $content -split "`n" | Where-Object { $_ -match "\[.*\] › .+ ── failed" -or ($_ -match "✘|×|Error:") }
                foreach ($line in $failedLines) {
                    $toolFailures += [PSCustomObject]@{
                        TestId = $line.Trim().Substring(0, [Math]::Min($line.Trim().Length, 200))
                        Reason = "E2E 失败"
                    }
                }
            }
            "selenium" {
                # 从 selenium pytest 输出提取
                $failedLines = $content -split "`n" | Where-Object { $_ -match "^FAILED " }
                foreach ($line in $failedLines) {
                    $toolFailures += [PSCustomObject]@{
                        TestId = $line.Trim()
                        Reason = "浏览器兼容性失败"
                    }
                }
            }
            "puppeteer" {
                # 从 Puppeteer 输出提取
                $failedLines = $content -split "`n" | Where-Object { $_ -match "FAIL|✕|✗|Error" }
                foreach ($line in $failedLines) {
                    $toolFailures += [PSCustomObject]@{
                        TestId = $line.Trim().Substring(0, [Math]::Min($line.Trim().Length, 200))
                        Reason = "渲染/性能失败"
                    }
                }
            }
            "k6" {
                # K6 thresh 失败
                $failedLines = $content -split "`n" | Where-Object { $_ -match "✗|thresholds.*failed" }
                foreach ($line in $failedLines) {
                    $toolFailures += [PSCustomObject]@{
                        TestId = $line.Trim().Substring(0, [Math]::Min($line.Trim().Length, 200))
                        Reason = "性能阈值未达标"
                    }
                }
            }
        }

        if ($toolFailures.Count -gt 0) {
            $failures[$name] = $toolFailures
        } else {
            # 有失败但解析不到明细，记录通用失败
            $failures[$name] = @([PSCustomObject]@{
                TestId = "(解析失败，请查看日志: $logFile)"
                Reason = $Completed[$name]
            })
        }
    }

    return $failures
}

# ═══════════════════════════════════════════════
# 生成失败报告
# ═══════════════════════════════════════════════
function Write-FailureReport {
    param($Completed, $Failures, $TotalTime)

    $reportPath = Join-Path $script:FailuresDir "failure-report-$(Get-Date -Format 'yyyyMMdd-HHmmss').md"

    $passCount = ($Completed.Values | Where-Object { $_ -eq "passed" }).Count
    $failCount = ($Completed.Values | Where-Object { $_ -in @("failed","error","timeout") }).Count
    $totalCount = $Completed.Count

    $sb = [System.Text.StringBuilder]::new()
    [void]$sb.AppendLine("# 六类测试并行执行报告")
    [void]$sb.AppendLine("")
    [void]$sb.AppendLine("- **执行时间**: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')")
    [void]$sb.AppendLine("- **执行级别**: $Level")
    [void]$sb.AppendLine("- **总耗时**: $TotalTime 分钟（并行）")
    [void]$sb.AppendLine("- **通过率**: $passCount/$totalCount 工具通过")
    [void]$sb.AppendLine("")
    [void]$sb.AppendLine("## 工具状态总览")
    [void]$sb.AppendLine("")
    [void]$sb.AppendLine("| 工具 | 状态 | 日志 |")
    [void]$sb.AppendLine("|------|------|------|")

    foreach ($name in $Completed.Keys) {
        $status = switch ($Completed[$name]) {
            "passed"  { "✅ 通过" }
            "failed"  { "❌ 失败" }
            "error"   { "❌ 异常" }
            "timeout" { "⏰ 超时" }
            default   { "❓ 未知" }
        }
        [void]$sb.AppendLine("| $($name.ToUpper()) | $status | ``TestResults/$name-output.log`` |")
    }

    if ($Failures.Count -gt 0) {
        [void]$sb.AppendLine("")
        [void]$sb.AppendLine("## 失败用例清单（按工具分类）")
        [void]$sb.AppendLine("")

        foreach ($tool in $Failures.Keys) {
            [void]$sb.AppendLine("### $($tool.ToUpper()) ($($Failures[$tool].Count) 个失败)")
            [void]$sb.AppendLine("")
            [void]$sb.AppendLine("| # | 用例 | 原因 |")
            [void]$sb.AppendLine("|---|------|------|")
            $i = 0
            foreach ($f in $Failures[$tool]) {
                $i++
                $testId = $f.TestId -replace '\|', '`|`'
                [void]$sb.AppendLine("| $i | $testId | $($f.Reason) |")
            }
            [void]$sb.AppendLine("")
        }

        [void]$sb.AppendLine("## 修复优先级建议")
        [void]$sb.AppendLine("")
        [void]$sb.AppendLine("1. **先修 pytest 失败** → API/后端问题，影响其他所有测试")
        [void]$sb.AppendLine("2. **再修 Cypress/Playwright** → 前端功能问题")
        [void]$sb.AppendLine("3. **然后 Selenium** → 浏览器兼容性（通常是 CSS/JS polyfill）")
        [void]$sb.AppendLine("4. **再看 Puppeteer** → 性能/渲染（低优先级）")
        [void]$sb.AppendLine("5. **最后 K6** → 性能阈值调整（可能需调参而非修 bug）")
        [void]$sb.AppendLine("")
        [void]$sb.AppendLine("## 重跑失败用例命令")
        [void]$sb.AppendLine("")

        if ($Failures.Contains("pytest")) {
            $failedIds = ($Failures["pytest"] | ForEach-Object { $_.TestId -replace "^FAILED\s+", "" }) -join " "
            [void]$sb.AppendLine("``````powershell")
            [void]$sb.AppendLine("# pytest: 仅重跑失败")
            [void]$sb.AppendLine("cd testing/tests && python -m pytest --lf -v --tb=long")
            [void]$sb.AppendLine("``````")
            [void]$sb.AppendLine("")
        }
        if ($Failures.Contains("playwright")) {
            [void]$sb.AppendLine("``````powershell")
            [void]$sb.AppendLine("# Playwright: 仅重跑失败")
            [void]$sb.AppendLine("cd testing/tests/playwright-tests && npx playwright test --last-failed")
            [void]$sb.AppendLine("``````")
            [void]$sb.AppendLine("")
        }
        if ($Failures.Contains("cypress")) {
            [void]$sb.AppendLine("``````powershell")
            [void]$sb.AppendLine("# Cypress: 打开交互界面逐个调试")
            [void]$sb.AppendLine("cd testing/tests/cypress-tests && npx cypress open")
            [void]$sb.AppendLine("``````")
            [void]$sb.AppendLine("")
        }
    }

    $sb.ToString() | Out-File -FilePath $reportPath -Encoding UTF8
    return $reportPath
}

# ═══════════════════════════════════════════════
# 显示最终汇总
# ═══════════════════════════════════════════════
function Show-Summary {
    param($Completed, $Failures, $ReportPath)

    $totalTime = [math]::Round(((Get-Date) - $script:StartTime).TotalMinutes, 1)
    $passCount = ($Completed.Values | Where-Object { $_ -eq "passed" }).Count
    $failCount = ($Completed.Values | Where-Object { $_ -in @("failed","error","timeout") }).Count

    Write-Host ""
    Write-Banner "📊 六类测试并行执行 - 汇总报告"

    Write-Host "  ┌────────────────────────────────────────────────────┐" -ForegroundColor White
    Write-Host "  │  执行级别: $($Level.ToUpper().PadRight(42))│" -ForegroundColor White
    Write-Host "  │  执行模式: 并行$((' (6工具同时)').PadRight(38))│" -ForegroundColor White
    Write-Host "  │  总耗时:   $("$totalTime 分钟".PadRight(42))│" -ForegroundColor White
    Write-Host "  │  ✅ 通过:  $("$passCount 个工具".PadRight(42))│" -ForegroundColor Green
    if ($failCount -gt 0) {
        Write-Host "  │  ❌ 失败:  $("$failCount 个工具".PadRight(42))│" -ForegroundColor Red
    }
    Write-Host "  └────────────────────────────────────────────────────┘" -ForegroundColor White

    if ($failCount -gt 0) {
        Write-Host ""
        Write-Host "  失败工具详情:" -ForegroundColor Red
        foreach ($name in $Completed.Keys) {
            if ($Completed[$name] -in @("failed","error","timeout")) {
                $fCount = if ($Failures.Contains($name)) { $Failures[$name].Count } else { "?" }
                Write-Host "    ❌ $($name.ToUpper()) ── $fCount 个失败用例" -ForegroundColor Red
            }
        }
        Write-Host ""
        Write-Host "  📋 完整失败报告: $ReportPath" -ForegroundColor Yellow
        Write-Host "  📂 各工具日志目录: $($script:ResultsDir)" -ForegroundColor Yellow
        Write-Host ""
        Write-Host "  💡 快速修复流程:" -ForegroundColor Cyan
        Write-Host "     1. 查看报告: code `"$ReportPath`"" -ForegroundColor White
        Write-Host "     2. 按优先级修复 (pytest → Cypress → Playwright → Selenium → Puppeteer → K6)" -ForegroundColor White
        Write-Host "     3. 重跑失败: .\scripts\rerun-failed-tests.ps1" -ForegroundColor White
    } else {
        Write-Host ""
        Write-Host "  🎉 全部通过！" -ForegroundColor Green
    }

    Write-Host ""
    return $totalTime
}

# ═══════════════════════════════════════════════
# 主流程
# ═══════════════════════════════════════════════
Clear-Host
Write-Host @"

  ╔══════════════════════════════════════════════════════════════════════════════╗
  ║                                                                              ║
  ║   🧪 AIOPS 六类测试 - 并行执行引擎                                           ║
  ║                                                                              ║
  ║   模式: 全部工具同时启动，失败不阻塞，统一收集修复                                ║
  ║   级别: $($Level.ToUpper().PadRight(68))║
  ║                                                                              ║
  ╚══════════════════════════════════════════════════════════════════════════════╝

"@ -ForegroundColor Cyan

# 获取本级别的工具命令
$tools = Get-ToolCommands -Level $Level

Write-Info "本次将并行执行 $($tools.Count) 个工具"
$expectedMax = ($tools.Values | ForEach-Object { $_.ExpectedMin } | Measure-Object -Maximum).Maximum
Write-Info "预计最长 ${expectedMax} 分钟完成（并行，取最慢工具）"
Write-Host ""

# 并行启动
$jobs, $logFiles = Start-ParallelTests -Tools $tools

# 等待完成
$completed = Watch-Jobs -Jobs $jobs -TimeoutMinutes $TimeoutMinutes

# 清理 Job 对象
foreach ($name in $jobs.Keys) {
    Remove-Job -Job $jobs[$name].Job -Force -ErrorAction SilentlyContinue
}

# 收集失败
$failures = Collect-Failures -Completed $completed -LogFiles $logFiles

# 生成失败报告
$totalTime = [math]::Round(((Get-Date) - $script:StartTime).TotalMinutes, 1)
$reportPath = Write-FailureReport -Completed $completed -Failures $failures -TotalTime $totalTime

# 显示汇总
Show-Summary -Completed $completed -Failures $failures -ReportPath $reportPath

# 自动收集结果并生成跟踪报告
Write-Step "📊 生成六类测试跟踪报告"
try {
    & "$PSScriptRoot\generate-test-report.ps1" -CollectFirst
} catch {
    Write-Host "  ⚠️ 报告生成失败: $_" -ForegroundColor Yellow
}

# 退出码
if (($completed.Values | Where-Object { $_ -in @("failed","error","timeout") }).Count -gt 0) {
    exit 1
} else {
    exit 0
}
