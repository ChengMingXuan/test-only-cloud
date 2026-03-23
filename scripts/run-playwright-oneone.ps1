# Playwright 逐个原子化测试脚本
# 一个一个测试，测完同步，失败则停止

$ErrorActionPreference = "Continue"
Set-Location "d:\2026\aiops.v2\testing\tests\playwright-tests"

$atomicDir = "d:\2026\aiops.v2\TestResults\atomic\playwright"
$allTests = Get-ChildItem tests -Filter "*.spec.ts" -Recurse | Sort-Object Name
$total = $allTests.Count
$idx = 0
$passedFiles = 0
$totalCases = 0

Write-Host "========== Playwright 逐个测试 (共 $total 个文件) ==========" -ForegroundColor Cyan

foreach ($test in $allTests) {
    $idx++
    $resultFile = Join-Path $atomicDir "$($test.Name).json"
    
    # 跳过已测试通过的
    if (Test-Path $resultFile) {
        try {
            $existing = Get-Content $resultFile -Raw | ConvertFrom-Json
            if ($existing.status -eq "passed" -and $existing.total -gt 0) {
                $passedFiles++
                $totalCases += $existing.total
                Write-Host "[$idx/$total] $($test.Name) - 已通过 ($($existing.total) 用例)" -ForegroundColor DarkGray
                continue
            }
        } catch {}
    }
    
    # 获取相对于 playwright-tests 目录的路径
    $baseDir = "d:\2026\aiops.v2\testing\tests\playwright-tests"
    $relativePath = $test.FullName.Replace($baseDir + "\", "").Replace("\", "/")
    
    Write-Host "[$idx/$total] 测试: $($test.Name) " -NoNewline
    $start = Get-Date
    # 添加超时30秒每个用例，全局超时15分钟，无重试
    $env:FULL_RUN = "true"
    $output = npx playwright test "$relativePath" --reporter=line --timeout=30000 --global-timeout=900000 2>&1
    $dur = ((Get-Date) - $start).TotalSeconds
    $outputText = $output -join "`n"
    
    # 解析 passed 数量
    $passed = 0; $failed = 0
    if ($outputText -match "(\d+)\s+passed") { $passed = [int]$Matches[1] }
    if ($outputText -match "(\d+)\s+failed") { $failed = [int]$Matches[1] }
    if ($outputText -match "(\d+)\s+flaky")  { $passed += [int]$Matches[1] }  # flaky 也算通过
    
    $status = if ($passed -gt 0 -and $failed -eq 0) { "passed" } elseif ($failed -gt 0) { "failed" } else { "error" }
    
    $result = @{
        file = "tests/$($test.Name)"
        total = $passed + $failed
        passed = $passed
        failed = $failed
        skipped = 0
        duration_s = [math]::Round($dur, 1)
        status = $status
        timestamp = (Get-Date -Format "yyyy-MM-ddTHH:mm:ss")
    }
    $result | ConvertTo-Json | Out-File $resultFile -Encoding utf8
    
    if ($status -eq "passed") {
        $passedFiles++
        $totalCases += $passed
        Write-Host "✅ $passed passed ($([math]::Round($dur,1))s)" -ForegroundColor Green
    } elseif ($status -eq "failed") {
        Write-Host "❌ $passed passed, $failed failed ($([math]::Round($dur,1))s)" -ForegroundColor Yellow
        # 继续执行不停止，最后统一处理失败的
    } else {
        Write-Host "⚠️ 无测试运行 ($([math]::Round($dur,1))s)" -ForegroundColor Yellow
        # 继续执行，不中断
    }
}

Write-Host "`n========== 完成: $passedFiles/$total 文件通过, $totalCases 用例 ==========" -ForegroundColor Cyan

# 同步生成报告
Write-Host "`n正在同步生成 Playwright 报告..."
& d:\2026\aiops.v2\scripts\generate-tool-reports.ps1 -Tool playwright
Write-Host "✅ 报告已同步"
