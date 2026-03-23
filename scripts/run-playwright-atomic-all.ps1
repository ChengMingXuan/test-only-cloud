# Playwright 原子化测试批量执行脚本
# 功能：依次执行所有 Playwright 测试文件，并保存原子化结果

$ErrorActionPreference = "Continue"
$playwrightDir = "d:\2026\aiops.v2\testing\tests\playwright-tests"
$atomicDir = "d:\2026\aiops.v2\TestResults\atomic\playwright"
$logFile = "d:\2026\aiops.v2\TestResults\playwright-atomic-run.log"

# 确保原子化结果目录存在
if (-not (Test-Path $atomicDir)) {
    New-Item -ItemType Directory -Path $atomicDir -Force | Out-Null
}

Set-Location $playwrightDir

# 获取已测试的文件
$done = @()
Get-ChildItem $atomicDir -Filter "*.json" -ErrorAction SilentlyContinue | 
    Where-Object { $_.BaseName -ne "summary" } | 
    ForEach-Object { $done += $_.BaseName -replace '\.spec\.ts$', '' }

# 获取所有测试文件
$allTests = Get-ChildItem "tests" -Filter "*.spec.ts" -Recurse -ErrorAction SilentlyContinue

if (-not $allTests -or $allTests.Count -eq 0) {
    Write-Host "未找到测试文件，尝试其他目录..."
    $allTests = Get-ChildItem $playwrightDir -Filter "*.spec.ts" -Recurse -ErrorAction SilentlyContinue
}

# 过滤出未测试的文件
$todo = $allTests | Where-Object { $done -notcontains ($_.BaseName -replace '\.spec$', '') }

$totalCount = $todo.Count
$passedCount = 0
$failedCount = 0
$idx = 0

"========================================" | Tee-Object -FilePath $logFile -Append
"Playwright 原子化批量测试开始: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')" | Tee-Object -FilePath $logFile -Append
"待执行: $totalCount 个测试文件" | Tee-Object -FilePath $logFile -Append
"========================================" | Tee-Object -FilePath $logFile -Append

foreach ($test in $todo) {
    $idx++
    $relativePath = $test.FullName -replace [regex]::Escape($playwrightDir + "\"), ""
    $relativePath = $relativePath -replace "\\", "/"
    
    # 构建原子化结果文件名
    $resultName = "$($test.Name).json"
    $resultPath = Join-Path $atomicDir $resultName
    
    "[$idx/$totalCount] 执行: $($test.Name)" | Tee-Object -FilePath $logFile -Append
    
    $startTime = Get-Date
    
    try {
        # 执行 Playwright 测试，使用 line 报告器
        $output = npx playwright test $test.FullName --reporter=line 2>&1
        $duration = ((Get-Date) - $startTime).TotalSeconds
        $outputText = $output -join "`n"
        
        # 从输出解析结果（例如 "1 passed" 或 "2 failed"）
        $passed = 0
        $failed = 0
        $skipped = 0
        
        # 匹配 "X passed"
        if ($outputText -match "(\d+)\s+passed") {
            $passed = [int]$Matches[1]
        }
        # 匹配 "X failed"
        if ($outputText -match "(\d+)\s+failed") {
            $failed = [int]$Matches[1]
        }
        # 匹配 "X skipped"
        if ($outputText -match "(\d+)\s+skipped") {
            $skipped = [int]$Matches[1]
        }
        
        $total = $passed + $failed + $skipped
        
        $atomicResult = @{
            file = $relativePath
            total = $total
            passed = $passed
            failed = $failed
            skipped = $skipped
            duration_s = [math]::Round($duration, 1)
            status = if ($failed -eq 0 -and $passed -gt 0) { "passed" } elseif ($failed -gt 0) { "failed" } else { "error" }
            timestamp = (Get-Date -Format "yyyy-MM-ddTHH:mm:ss")
            exitCode = $LASTEXITCODE
        }
        
        if ($failed -eq 0 -and $passed -gt 0) {
            $passedCount++
            $atomicResult | ConvertTo-Json | Out-File $resultPath -Encoding utf8
            "  ✅ 通过: $passed 测试 | 耗时: $([math]::Round($duration, 1))s" | Tee-Object -FilePath $logFile -Append
        } elseif ($failed -gt 0) {
            $failedCount++
            $atomicResult | ConvertTo-Json | Out-File $resultPath -Encoding utf8
            "  ❌ 失败: $failed/$total | 耗时: $([math]::Round($duration, 1))s" | Tee-Object -FilePath $logFile -Append
        } else {
            $failedCount++
            # total=0 时不写入 JSON，避免阻止后续重跑
            "  ⚠️ 无测试运行 (exit=$LASTEXITCODE) | 耗时: $([math]::Round($duration, 1))s — 不写入结果" | Tee-Object -FilePath $logFile -Append
        }
    } catch {
        $failedCount++
        "  ❌ 执行异常: $_" | Tee-Object -FilePath $logFile -Append
    }
}

"========================================" | Tee-Object -FilePath $logFile -Append
"测试完成: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')" | Tee-Object -FilePath $logFile -Append
"通过: $passedCount | 失败: $failedCount | 总计: $totalCount" | Tee-Object -FilePath $logFile -Append
"========================================" | Tee-Object -FilePath $logFile -Append

# 生成报告
Write-Host "`n正在生成 Playwright 独立报告..."
& d:\2026\aiops.v2\scripts\generate-tool-reports.ps1 -Tool playwright

Write-Host "`n✅ 全部完成！"
