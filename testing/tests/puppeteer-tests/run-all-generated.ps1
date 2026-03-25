# Puppeteer Generated 全量测试运行脚本
# 启动 Mock 服务器 → 跑 Jest 全量 → 输出结果 → 生成报告
param(
    [int]$MaxWorkers = 2,
    [int]$TestTimeout = 15000,
    [switch]$SkipReport
)

$ErrorActionPreference = "Continue"
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$rootDir = (Resolve-Path "$scriptDir\..\..").Path

Write-Host "============================================" -ForegroundColor Cyan
Write-Host " Puppeteer Generated 全量测试" -ForegroundColor Cyan
Write-Host " Workers: $MaxWorkers | Timeout: ${TestTimeout}ms" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan

# ── 1. 检查/启动 Mock 服务器 ──
$mockRunning = $false
try {
    $r = Invoke-WebRequest -Uri "http://localhost:8000/" -UseBasicParsing -TimeoutSec 2
    if ($r.Content -match "JGSY AGI Platform") {
        Write-Host "✅ Mock 服务器已在 8000 端口运行" -ForegroundColor Green
        $mockRunning = $true
        $mockStartedByUs = $false
    } else {
        Write-Host "⚠️ 端口 8000 被其他服务占用（非 Mock）" -ForegroundColor Yellow
        $mockRunning = $true
        $mockStartedByUs = $false
    }
} catch {
    Write-Host "🚀 启动 Mock 服务器..." -ForegroundColor Yellow
    $mockProc = Start-Process -FilePath "node" -ArgumentList "$scriptDir\mock-server.js" -PassThru -WindowStyle Hidden
    Start-Sleep -Seconds 2
    try {
        $r = Invoke-WebRequest -Uri "http://localhost:8000/" -UseBasicParsing -TimeoutSec 3
        Write-Host "✅ Mock 服务器已启动 (PID: $($mockProc.Id))" -ForegroundColor Green
        $mockRunning = $true
        $mockStartedByUs = $true
    } catch {
        Write-Host "❌ Mock 服务器启动失败" -ForegroundColor Red
        exit 1
    }
}

# ── 2. 运行 Jest 全量测试 ──
$reportDir = "$scriptDir\test-reports"
if (-not (Test-Path $reportDir)) { New-Item -ItemType Directory -Path $reportDir -Force | Out-Null }

$jestResultPath = "$reportDir\jest-results.json"
$junitResultPath = "$reportDir\jest-junit.xml"
$startTime = Get-Date

Write-Host "`n🧪 开始执行 Jest Generated 测试 ($(Get-Date -Format 'HH:mm:ss'))..." -ForegroundColor Cyan
Write-Host "   文件数: $(Get-ChildItem $scriptDir\tests\generated -Recurse -Filter '*.test.js' | Measure-Object | Select-Object -ExpandProperty Count)"

Push-Location $scriptDir
$env:TEST_BASE_URL = "http://localhost:8000"
# 使用 jest-junit 流式输出（避免 --json 内存溢出）
$env:JEST_JUNIT_OUTPUT_DIR = $reportDir
$env:JEST_JUNIT_OUTPUT_NAME = "jest-junit.xml"
# 注意：不能用 Out-String | Out-Null，会造成 PowerShell 管道死锁
$logFile = Join-Path $reportDir "jest-run.log"
& npx jest tests/generated --testTimeout=$TestTimeout --maxWorkers=$MaxWorkers --forceExit --reporters=default --reporters=jest-junit *> $logFile
$exitCode = $LASTEXITCODE

# 将 JUnit XML 转换为与 collect-test-results.ps1 兼容的 jest-results.json
if (Test-Path $junitResultPath) {
    try {
        [xml]$xml = Get-Content $junitResultPath -Encoding UTF8
        $totalTests = 0; $passedTests = 0; $failedTests = 0
        $testSuiteResults = @()
        foreach ($suite in $xml.testsuites.testsuite) {
            $sTests = [int]$suite.tests
            $sFails = [int]$suite.failures + [int]$suite.errors
            $sPassed = $sTests - $sFails
            $totalTests += $sTests; $failedTests += $sFails; $passedTests += $sPassed
            $assertionResults = @()
            foreach ($tc in $suite.testcase) {
                $status = if ($tc.failure) { "failed" } else { "passed" }
                $failMsg = if ($tc.failure) { @($tc.failure.InnerText) } else { @() }
                $assertionResults += @{
                    ancestorTitles = @($suite.name)
                    title = $tc.name
                    fullName = "$($suite.name) > $($tc.name)"
                    status = $status
                    failureMessages = $failMsg
                }
            }
            $testSuiteResults += @{
                name = $suite.name
                status = if ($sFails -gt 0) { "failed" } else { "passed" }
                assertionResults = $assertionResults
            }
        }
        $jsonResult = @{
            numTotalTests = $totalTests
            numPassedTests = $passedTests
            numFailedTests = $failedTests
            numPendingTests = 0
            numTotalTestSuites = $testSuiteResults.Count
            numPassedTestSuites = ($testSuiteResults | Where-Object { $_.status -eq "passed" }).Count
            numFailedTestSuites = ($testSuiteResults | Where-Object { $_.status -eq "failed" }).Count
            success = ($failedTests -eq 0)
            testResults = $testSuiteResults
        }
        $jsonResult | ConvertTo-Json -Depth 5 -Compress | Set-Content $jestResultPath -Encoding UTF8
        Write-Host "✅ 结果已转换: $jestResultPath" -ForegroundColor Green
    } catch {
        Write-Host "⚠️ JUnit→JSON 转换失败: $_" -ForegroundColor Yellow
    }
}
Pop-Location

$elapsed = (Get-Date) - $startTime
Write-Host "`n⏱️ 测试耗时: $($elapsed.ToString('hh\:mm\:ss'))" -ForegroundColor Cyan

# ── 3. 分析结果 ──
if (Test-Path $jestResultPath) {
    $json = Get-Content $jestResultPath -Raw -Encoding UTF8 | ConvertFrom-Json
    $total = [int]$json.numTotalTests
    $passed = [int]$json.numPassedTests
    $failed = [int]$json.numFailedTests
    $pending = [int]$json.numPendingTests
    $suitesPassed = [int]$json.numPassedTestSuites
    $suitesTotal = [int]$json.numTotalTestSuites
    
    $passRate = if ($total -gt 0) { [math]::Round($passed / $total * 100, 1) } else { 0 }
    
    Write-Host "`n📊 测试结果:" -ForegroundColor Cyan
    Write-Host "   Suites: $suitesPassed/$suitesTotal 通过" -ForegroundColor $(if ($suitesPassed -eq $suitesTotal) { "Green" } else { "Yellow" })
    Write-Host "   Tests:  $passed/$total 通过 (通过率: $passRate%)" -ForegroundColor $(if ($passRate -ge 95) { "Green" } elseif ($passRate -ge 80) { "Yellow" } else { "Red" })
    if ($failed -gt 0) { Write-Host "   失败:   $failed" -ForegroundColor Red }
    if ($pending -gt 0) { Write-Host "   跳过:   $pending" -ForegroundColor Gray }
    Write-Host "   结果文件: $jestResultPath" -ForegroundColor Gray
} else {
    Write-Host "❌ 未找到结果文件: $jestResultPath" -ForegroundColor Red
}

# ── 4. 停止 Mock 服务器（仅当由脚本启动时） ──
if ($mockStartedByUs -and $mockProc -and !$mockProc.HasExited) {
    Stop-Process -Id $mockProc.Id -Force -ErrorAction SilentlyContinue
    Write-Host "`n🛑 Mock 服务器已停止" -ForegroundColor Gray
}

# ── 5. 生成六大测试报告 ──
if (-not $SkipReport) {
    Write-Host "`n📊 同步到六大测试报告..." -ForegroundColor Cyan
    $collectScript = "$rootDir\scripts\collect-test-results.ps1"
    $reportScript = "$rootDir\scripts\generate-test-report.ps1"
    
    if (Test-Path $collectScript) {
        & $collectScript
    }
    if (Test-Path $reportScript) {
        & $reportScript
    }
    Write-Host "✅ 报告已更新" -ForegroundColor Green
}

Write-Host "`n============================================" -ForegroundColor Cyan
Write-Host " 完成！" -ForegroundColor Green
Write-Host "============================================" -ForegroundColor Cyan
