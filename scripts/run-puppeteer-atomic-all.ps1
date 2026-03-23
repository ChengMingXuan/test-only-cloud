# Puppeteer 原子化测试批量执行脚本
# 功能：依次执行所有未测试的 Puppeteer 测试文件，并保存原子化结果

$ErrorActionPreference = "Continue"
$puppeteerDir = "d:\2026\aiops.v2\testing\tests\puppeteer-tests"
$atomicDir = "d:\2026\aiops.v2\TestResults\atomic\puppeteer"
$logFile = "d:\2026\aiops.v2\TestResults\puppeteer-atomic-run.log"

Set-Location $puppeteerDir

# 获取已测试的文件（从原子化结果目录）
$done = Get-ChildItem $atomicDir -Filter "*.json" | 
    Where-Object { $_.BaseName -ne "summary" } | 
    ForEach-Object { 
        $name = $_.BaseName -replace '^generated_', '' -replace '\.js$',''
        $name
    }

# 获取所有测试文件
$allTests = Get-ChildItem "tests" -Filter "*.test.js" -Recurse

# 过滤出未测试的文件
$todo = $allTests | Where-Object { $done -notcontains $_.BaseName }

$totalCount = $todo.Count
$passedCount = 0
$failedCount = 0
$idx = 0

"========================================" | Tee-Object -FilePath $logFile -Append
"Puppeteer 原子化批量测试开始: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')" | Tee-Object -FilePath $logFile -Append
"待执行: $totalCount 个测试文件" | Tee-Object -FilePath $logFile -Append
"========================================" | Tee-Object -FilePath $logFile -Append

foreach ($test in $todo) {
    $idx++
    $relativePath = $test.FullName -replace [regex]::Escape($puppeteerDir + "\"), ""
    $relativePath = $relativePath -replace "\\", "/"
    
    # 构建原子化结果文件名
    $baseName = $test.BaseName
    if ($relativePath -match "generated/") {
        $resultName = "generated_$($test.Name).json"
    } else {
        $resultName = "$($test.Name).json"
    }
    $resultPath = Join-Path $atomicDir $resultName
    
    "[$idx/$totalCount] 执行: $($test.Name)" | Tee-Object -FilePath $logFile -Append
    
    $startTime = Get-Date
    
    try {
        # 执行测试并捕获 JSON 输出
        $output = npx jest $relativePath --testTimeout=60000 --json 2>&1
        $jsonLine = $output | Where-Object { $_ -match '^\{' } | Select-Object -First 1
        
        if ($jsonLine) {
            $result = $jsonLine | ConvertFrom-Json
            $duration = ((Get-Date) - $startTime).TotalSeconds
            
            $atomicResult = @{
                file = $relativePath
                total = $result.numTotalTests
                passed = $result.numPassedTests
                failed = $result.numFailedTests
                skipped = $result.numPendingTests
                duration_s = [math]::Round($duration, 1)
                status = if ($result.numFailedTests -eq 0) { "passed" } else { "failed" }
                timestamp = (Get-Date -Format "yyyy-MM-ddTHH:mm:ss")
            }
            
            $atomicResult | ConvertTo-Json | Out-File $resultPath -Encoding utf8
            
            if ($result.numFailedTests -eq 0) {
                $passedCount++
                "  ✅ 通过: $($result.numPassedTests) 测试 | 耗时: $([math]::Round($duration, 1))s" | Tee-Object -FilePath $logFile -Append
            } else {
                $failedCount++
                "  ❌ 失败: $($result.numFailedTests)/$($result.numTotalTests) | 耗时: $([math]::Round($duration, 1))s" | Tee-Object -FilePath $logFile -Append
            }
        } else {
            # 尝试从输出中解析测试结果
            $duration = ((Get-Date) - $startTime).TotalSeconds
            $passLine = $output | Select-String "Tests:\s+(\d+) passed" | Select-Object -First 1
            
            if ($passLine) {
                $matches = [regex]::Match($passLine.Line, "(\d+) passed")
                $passedTests = [int]$matches.Groups[1].Value
                
                $atomicResult = @{
                    file = $relativePath
                    total = $passedTests
                    passed = $passedTests
                    failed = 0
                    skipped = 0
                    duration_s = [math]::Round($duration, 1)
                    status = "passed"
                    timestamp = (Get-Date -Format "yyyy-MM-ddTHH:mm:ss")
                }
                $atomicResult | ConvertTo-Json | Out-File $resultPath -Encoding utf8
                $passedCount++
                "  ✅ 通过: $passedTests 测试 | 耗时: $([math]::Round($duration, 1))s" | Tee-Object -FilePath $logFile -Append
            } else {
                $failedCount++
                "  ⚠️ 无法解析结果 | 耗时: $([math]::Round($duration, 1))s" | Tee-Object -FilePath $logFile -Append
            }
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
Write-Host "`n正在生成 Puppeteer 独立报告..."
& d:\2026\aiops.v2\scripts\generate-tool-reports.ps1 -Tool puppeteer

Write-Host "`n✅ 全部完成！"
