<#
.SYNOPSIS
  Cypress 增量原子化执行器 - 逐个 spec 文件执行并记录结果
#>
$ErrorActionPreference = "Continue"
$WorkspaceRoot = "D:\2026\aiops.v2"
$CypressDir = "$1\testing\tests\cypress-tests"
$ResultsDir = "$WorkspaceRoot\TestResults\incremental"
if (!(Test-Path $ResultsDir)) { New-Item -ItemType Directory -Path $ResultsDir -Force | Out-Null }

$Timestamp = Get-Date -Format "yyyyMMdd-HHmmss"
$ResultFile = "$ResultsDir\cypress-atomic-$Timestamp.json"

# 获取增量 Cypress 文件
$newFiles = git -C $WorkspaceRoot diff --diff-filter=A --name-only "HEAD~5" HEAD -- testing/tests/cypress-tests/e2e/ 2>&1 | Where-Object { $_ -match '\.cy\.js$' }
$modFiles = git -C $WorkspaceRoot diff --diff-filter=M --name-only "HEAD~5" HEAD -- testing/tests/cypress-tests/e2e/ 2>&1 | Where-Object { $_ -match '\.cy\.js$' }

$testQueue = @()
foreach ($f in $newFiles) { $testQueue += @{ File=$f.Trim(); Change="NEW" } }
foreach ($f in $modFiles) { $testQueue += @{ File=$f.Trim(); Change="MOD" } }

$total = $testQueue.Count
Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "  Cypress 增量原子化测试" -ForegroundColor Cyan
Write-Host "  新增: $($newFiles.Count)  修改: $($modFiles.Count)  总计: $total" -ForegroundColor Yellow
Write-Host "========================================`n" -ForegroundColor Cyan

$results = @(); $passed = 0; $failed = 0; $skipped = 0; $current = 0

Set-Location $CypressDir

foreach ($item in $testQueue) {
    $current++
    $specRelative = $item.File -replace '^testing/tests/cypress-tests/', ''
    $shortName = Split-Path $item.File -Leaf
    $tag = if ($item.Change -eq "NEW") { "[NEW]" } else { "[MOD]" }
    
    Write-Host ("[$current/$total] $tag $shortName") -NoNewline -ForegroundColor White
    
    # cpui-* 文件需要完整 UI 路由可用，标记为 SKIP
    if ($shortName -match '^cpui-') {
        Write-Host " => SKIP (需要完整UI路由)" -ForegroundColor DarkGray
        $skipped++
        $results += @{
            file = $item.File; change = $item.Change; status = "SKIP"
            tests = 0; pass = 0; fail = 0
            duration = "0s"; error = "需要完整UI路由匹配"
        }
        continue
    }
    
    $startTime = Get-Date
    
    # 执行 Cypress
    $output = npx cypress run --spec $specRelative --headless --browser electron 2>&1 | Out-String
    $exitCode = $LASTEXITCODE
    
    $duration = "{0:N1}s" -f ((Get-Date) - $startTime).TotalSeconds
    
    # 解析结果
    $passCount = 0; $failCount = 0; $status = "FAIL"; $errorMsg = ""
    
    if ($output -match '(\d+)\s+passing') { $passCount = [int]$Matches[1] }
    if ($output -match '(\d+)\s+failing') { $failCount = [int]$Matches[1] }
    $testCount = $passCount + $failCount
    
    if ($exitCode -eq 0 -and $passCount -gt 0) {
        $status = "PASS"
    } elseif ($output -match 'SyntaxError|Unexpected token|Webpack Compilation Error') {
        $status = "ERROR"
        $errorMsg = "语法/编译错误"
    } elseif ($failCount -gt 0) {
        $status = "FAIL"
        # 提取第一个失败信息
        if ($output -match 'AssertionError:([^\n]+)') { $errorMsg = $Matches[1].Trim() }
        elseif ($output -match 'CypressError:([^\n]+)') { $errorMsg = $Matches[1].Trim() }
        elseif ($output -match 'Error:([^\n]+)') { $errorMsg = $Matches[1].Trim().Substring(0, [Math]::Min(80, $Matches[1].Trim().Length)) }
    } elseif ($testCount -eq 0) {
        $status = "ERROR"
        $errorMsg = "无测试用例或执行超时"
    }
    
    switch ($status) {
        "PASS"  { Write-Host " => PASS ($passCount/$testCount) [$duration]" -ForegroundColor Green; $passed++ }
        "FAIL"  { Write-Host " => FAIL ($passCount/$testCount) [$duration]" -ForegroundColor Red; $failed++ }
        "ERROR" { Write-Host " => ERROR [$duration] $errorMsg" -ForegroundColor Red; $failed++ }
    }
    
    $results += @{
        file = $item.File; change = $item.Change; status = $status
        tests = $testCount; pass = $passCount; fail = $failCount
        duration = $duration; error = $errorMsg
    }
}

# 汇总
Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "  Cypress 增量原子化汇总" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  总文件: $total" -ForegroundColor White
Write-Host "  通过:   $passed" -ForegroundColor Green
Write-Host "  失败:   $failed" -ForegroundColor $(if ($failed -gt 0) { "Red" } else { "Green" })
Write-Host "  跳过:   $skipped" -ForegroundColor DarkGray

# 计算总用例数
$totalTests = ($results | ForEach-Object { $_.tests } | Measure-Object -Sum).Sum
$totalPass = ($results | ForEach-Object { $_.pass } | Measure-Object -Sum).Sum
Write-Host "  总用例: $totalTests  通过: $totalPass" -ForegroundColor Yellow

# 失败明细
$failedItems = $results | Where-Object { $_.status -in @("FAIL","ERROR") }
if ($failedItems.Count -gt 0) {
    Write-Host "`n  失败明细:" -ForegroundColor Red
    foreach ($fi in $failedItems) {
        $fn = Split-Path $fi.file -Leaf
        Write-Host "    ❌ [$($fi.change)] $fn - $($fi.error)" -ForegroundColor Red
    }
}

# 保存 JSON
@{
    timestamp = Get-Date -Format "yyyy-MM-ddTHH:mm:ss"
    tool = "cypress"; total = $total; passed = $passed; failed = $failed
    totalTests = $totalTests; totalPass = $totalPass
    results = $results
} | ConvertTo-Json -Depth 4 | Out-File -FilePath $ResultFile -Encoding utf8

Write-Host "`n  结果已保存: $ResultFile" -ForegroundColor Gray
Write-Host "========================================`n" -ForegroundColor Cyan
