# pytest 原子化测试批量执行脚本
# 功能：依次执行所有 pytest 测试文件，并保存原子化结果

$ErrorActionPreference = "Continue"
$testRoot = "d:\2026\aiops.v2\testing\tests"
$atomicDir = "d:\2026\aiops.v2\TestResults\atomic\pytest"
$logFile = "d:\2026\aiops.v2\TestResults\pytest-atomic-run.log"

# 确保原子化结果目录存在
if (-not (Test-Path $atomicDir)) {
    New-Item -ItemType Directory -Path $atomicDir -Force | Out-Null
}

Set-Location $testRoot

# 获取已测试的文件
$done = @()
Get-ChildItem $atomicDir -Filter "*.json" -ErrorAction SilentlyContinue | 
    Where-Object { $_.BaseName -ne "summary" } | 
    ForEach-Object { $done += $_.BaseName }

# 获取所有 pytest 测试文件
$allTests = Get-ChildItem $testRoot -Filter "test_*.py" -Recurse -ErrorAction SilentlyContinue

# 过滤出未测试的文件
$todo = $allTests | Where-Object { $done -notcontains $_.BaseName }

$totalCount = $todo.Count
$passedCount = 0
$failedCount = 0
$idx = 0

"========================================" | Tee-Object -FilePath $logFile -Append
"pytest 原子化批量测试开始: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')" | Tee-Object -FilePath $logFile -Append
"待执行: $totalCount 个测试文件" | Tee-Object -FilePath $logFile -Append
"========================================" | Tee-Object -FilePath $logFile -Append

foreach ($test in $todo) {
    $idx++
    $relativePath = $test.FullName -replace [regex]::Escape($testRoot + "\"), ""
    $relativePath = $relativePath -replace "\\", "/"
    
    # 构建原子化结果文件名
    $resultName = "$($test.BaseName).json"
    $resultPath = Join-Path $atomicDir $resultName
    
    "[$idx/$totalCount] 执行: $($test.Name)" | Tee-Object -FilePath $logFile -Append
    
    $startTime = Get-Date
    
    try {
        # 执行 pytest 测试
        $output = python -m pytest $test.FullName -v 2>&1
        $duration = ((Get-Date) - $startTime).TotalSeconds
        $outputText = $output -join "`n"
        
        # 从输出解析结果
        $passed = 0; $failed = 0; $skipped = 0; $errors = 0
        
        # 匹配 pytest 输出格式
        if ($outputText -match "(\d+)\s+passed") { $passed = [int]$Matches[1] }
        if ($outputText -match "(\d+)\s+failed") { $failed = [int]$Matches[1] }
        if ($outputText -match "(\d+)\s+skipped") { $skipped = [int]$Matches[1] }
        if ($outputText -match "(\d+)\s+error") { $errors = [int]$Matches[1] }
        
        # 检查是否收集了测试
        $collected = 0
        if ($outputText -match "collected\s+(\d+)\s+item") { $collected = [int]$Matches[1] }
        
        $total = $passed + $failed + $skipped + $errors
        if ($total -eq 0 -and $collected -gt 0) { $total = $collected }
        
        # 确定状态
        $status = "error"
        if ($failed -eq 0 -and $errors -eq 0 -and $passed -gt 0) {
            $status = "passed"
        } elseif ($failed -gt 0 -or $errors -gt 0) {
            $status = "failed"
        }
        
        $atomicResult = @{
            file = $relativePath
            total = $total
            passed = $passed
            failed = $failed + $errors
            skipped = $skipped
            duration_s = [math]::Round($duration, 1)
            status = $status
            timestamp = (Get-Date -Format "yyyy-MM-ddTHH:mm:ss")
            exitCode = $LASTEXITCODE
        }
        
        $atomicResult | ConvertTo-Json | Out-File $resultPath -Encoding utf8
        
        if ($status -eq "passed") {
            $passedCount++
            "  ✅ 通过: $passed/$total | 耗时: $([math]::Round($duration, 1))s" | Tee-Object -FilePath $logFile -Append
        } elseif ($status -eq "failed") {
            $failedCount++
            "  ❌ 失败: $($failed + $errors)/$total | 耗时: $([math]::Round($duration, 1))s" | Tee-Object -FilePath $logFile -Append
        } else {
            $failedCount++
            "  ⚠️ 无测试运行 (exit=$LASTEXITCODE) | 耗时: $([math]::Round($duration, 1))s" | Tee-Object -FilePath $logFile -Append
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
Write-Host "`n正在生成 pytest 独立报告..."
& d:\2026\aiops.v2\scripts\generate-tool-reports.ps1 -Tool pytest

Write-Host "`n✅ 全部完成！"
