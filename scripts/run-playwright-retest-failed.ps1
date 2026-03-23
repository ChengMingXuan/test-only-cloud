# Playwright 重测失败用例脚本
# 功能：并行重测所有失败的 Playwright 测试文件
# 参数：-Workers 并行数（默认6）

param(
    [int]$Workers = 6
)

$ErrorActionPreference = "Continue"
$playwrightDir = "D:\2026\aiops.v2\testing\tests\playwright-tests"
$atomicDir = "D:\2026\aiops.v2\TestResults\atomic\playwright"
$logFile = "D:\2026\aiops.v2\TestResults\playwright-retest-failed.log"

# 确保目录存在
if (-not (Test-Path $atomicDir)) {
    New-Item -ItemType Directory -Path $atomicDir -Force | Out-Null
}

# 切换到 Playwright 目录
Set-Location $playwrightDir

# 清理 test-results 目录防止 ENOTEMPTY 错误
$testResultsDir = Join-Path $playwrightDir "test-results"
if (Test-Path $testResultsDir) {
    Get-Process | Where-Object { $_.Name -match "chromium|firefox|webkit|node" } -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue
    Start-Sleep -Milliseconds 500
    Remove-Item -Path $testResultsDir -Recurse -Force -ErrorAction SilentlyContinue
    Write-Host "✅ 已清理 test-results 目录"
}

# 获取失败的测试文件
$failedTests = @()
Get-ChildItem $atomicDir -Filter "*.json" -ErrorAction SilentlyContinue | ForEach-Object {
    try {
        $content = Get-Content $_.FullName -Raw | ConvertFrom-Json
        if ($content.failed -gt 0) {
            # 从 JSON 文件名还原测试文件路径
            $testFileName = $_.Name -replace '\.json$', ''
            # 搜索对应的测试文件
            $testFile = Get-ChildItem "tests" -Filter $testFileName -Recurse -ErrorAction SilentlyContinue | Select-Object -First 1
            if ($testFile) {
                $failedTests += @{
                    File = $testFile.FullName
                    Name = $testFileName
                    Passed = $content.passed
                    Failed = $content.failed
                }
            }
        }
    } catch {
        Write-Host "⚠️ 解析失败: $($_.Name)"
    }
}

$totalFailed = $failedTests.Count

if ($totalFailed -eq 0) {
    Write-Host "✅ 没有失败的测试需要重测"
    exit 0
}

Write-Host "╔══════════════════════════════════════════════════════════════╗"
Write-Host "║  Playwright 失败用例重测                                     ║"
Write-Host "╚══════════════════════════════════════════════════════════════╝"
Write-Host ""
Write-Host "  失败文件: $totalFailed 个"
Write-Host "  并行数: $Workers workers"
Write-Host ""

foreach ($test in $failedTests) {
    Write-Host "  ❌ $($test.Name): passed=$($test.Passed) failed=$($test.Failed)"
}
Write-Host ""

"========================================" | Out-File $logFile
"开始时间: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')" | Out-File $logFile -Append
"失败文件: $totalFailed" | Out-File $logFile -Append
"========================================" | Out-File $logFile -Append

# 删除旧的原子化结果（仅删除失败的）
foreach ($test in $failedTests) {
    $jsonFile = Join-Path $atomicDir "$($test.Name).json"
    if (Test-Path $jsonFile) {
        Remove-Item $jsonFile -Force
        Write-Host "  🗑️ 删除旧结果: $($test.Name).json"
    }
}
Write-Host ""

# 并行执行重测
$env:FULL_RUN = "1"  # 禁用 trace/screenshot/video 减少内存压力
$testFiles = $failedTests | ForEach-Object { $_.File }

Write-Host "🚀 开始并行重测 (workers=$Workers)..."
$startTime = Get-Date

try {
    # 使用 Playwright 的 --workers 参数并行执行
    $fileList = $testFiles -join " "
    $result = & npx playwright test $testFiles --workers=$Workers --reporter=json 2>&1
    
    # 解析结果并保存原子化数据
    foreach ($test in $failedTests) {
        $testFileName = $test.Name
        $jsonFile = Join-Path $atomicDir "$testFileName.json"
        
        # 执行单个文件获取精确结果
        $singleResult = & npx playwright test $test.File --reporter=json 2>&1 | Out-String
        
        try {
            $parsed = $singleResult | ConvertFrom-Json
            $atomicResult = @{
                file = $testFileName
                total = $parsed.suites[0].specs.Count
                passed = ($parsed.suites[0].specs | Where-Object { $_.ok }).Count
                failed = ($parsed.suites[0].specs | Where-Object { -not $_.ok }).Count
                skipped = 0
                duration = $parsed.stats.duration
                timestamp = (Get-Date -Format "yyyy-MM-ddTHH:mm:ss")
                status = if (($parsed.suites[0].specs | Where-Object { -not $_.ok }).Count -eq 0) { "passed" } else { "failed" }
            }
            $atomicResult | ConvertTo-Json -Depth 5 | Out-File $jsonFile -Encoding utf8
            
            if ($atomicResult.failed -eq 0) {
                Write-Host "  ✅ $testFileName : $($atomicResult.passed) passed"
            } else {
                Write-Host "  ❌ $testFileName : $($atomicResult.passed) passed, $($atomicResult.failed) failed"
            }
        } catch {
            Write-Host "  ⚠️ 解析失败: $testFileName"
        }
    }
} catch {
    Write-Host "❌ 执行出错: $_"
}

$endTime = Get-Date
$duration = ($endTime - $startTime).TotalMinutes

Write-Host ""
Write-Host "══════════════════════════════════════════════════════════════"
Write-Host "  重测完成 - 耗时: $([math]::Round($duration, 1)) 分钟"
Write-Host "══════════════════════════════════════════════════════════════"

"结束时间: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')" | Out-File $logFile -Append
"耗时: $([math]::Round($duration, 1)) 分钟" | Out-File $logFile -Append
