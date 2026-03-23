<# 
  批量运行全部 Cypress 测试并生成 mochawesome 合并报告
  输出: reports/mochawesome.json (供 collect-test-results.ps1 读取)
#>
param(
    [int]$BatchSize = 10,
    [switch]$Quick  # 只跑前5个文件做快速验证
)

$ErrorActionPreference = "Continue"
$root = $PSScriptRoot
Set-Location $root

# 清理旧报告
if (Test-Path reports) { Remove-Item reports\*.json -Force -ErrorAction SilentlyContinue }
if (-not (Test-Path reports)) { New-Item reports -ItemType Directory | Out-Null }

# 获取全部测试文件
$allSpecs = Get-ChildItem e2e -Filter "*.cy.js" | Sort-Object Name
if ($Quick) { $allSpecs = $allSpecs | Select-Object -First 5 }

$totalFiles = $allSpecs.Count
Write-Host "═══════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "  Cypress 批量测试 - $totalFiles 个文件" -ForegroundColor Cyan
Write-Host "  批次大小: $BatchSize" -ForegroundColor Cyan
Write-Host "═══════════════════════════════════════════" -ForegroundColor Cyan

$totalPass = 0
$totalFail = 0
$totalSkip = 0
$totalDuration = 0
$batchNum = 0
$startTime = Get-Date

# 分批执行
for ($i = 0; $i -lt $totalFiles; $i += $BatchSize) {
    $batchNum++
    $batchSpecs = $allSpecs[$i..([Math]::Min($i + $BatchSize - 1, $totalFiles - 1))]
    $specList = ($batchSpecs | ForEach-Object { "e2e/$($_.Name)" }) -join ","
    $specNames = ($batchSpecs | ForEach-Object { $_.BaseName }) -join ", "
    
    $elapsed = ((Get-Date) - $startTime).ToString("hh\:mm\:ss")
    Write-Host "`n[$elapsed] 批次 $batchNum ($($i+1)-$([Math]::Min($i+$BatchSize, $totalFiles))/$totalFiles): $specNames" -ForegroundColor Yellow
    
    # 用 mochawesome reporter 运行
    $env:CYPRESS_NO_COMMAND_LOG = "1"
    $output = npx cypress run `
        --config-file cypress.fast.config.js `
        --spec $specList `
        --reporter mochawesome `
        --reporter-options "reportDir=reports,overwrite=false,html=false,json=true,reportFilename=mochawesome-batch-$batchNum" `
        --config "retries=0,video=false,screenshotOnRunFailure=false" `
        --quiet 2>&1
    
    # 解析当前批次结果
    $batchPass = 0; $batchFail = 0
    $output | ForEach-Object {
        if ($_ -match "(\d+)\s+passing") { $batchPass = [int]$Matches[1] }
        if ($_ -match "(\d+)\s+failing") { $batchFail = [int]$Matches[1] }
    }
    
    $totalPass += $batchPass
    $totalFail += $batchFail
    
    Write-Host "  -> ✅ $batchPass 通过 | ❌ $batchFail 失败 | 累计: ✅ $totalPass / ❌ $totalFail" -ForegroundColor $(if ($batchFail -eq 0) { "Green" } else { "Red" })
}

$endTime = Get-Date
$totalDuration = ($endTime - $startTime).TotalSeconds

Write-Host "`n═══════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "  执行完成！" -ForegroundColor Cyan
Write-Host "  ✅ 通过: $totalPass" -ForegroundColor Green
Write-Host "  ❌ 失败: $totalFail" -ForegroundColor $(if ($totalFail -gt 0) { "Red" } else { "Green" })
Write-Host "  ⏱  耗时: $([math]::Round($totalDuration/60, 1)) 分钟" -ForegroundColor Cyan
Write-Host "═══════════════════════════════════════════" -ForegroundColor Cyan

# 合并所有 mochawesome JSON 报告
Write-Host "`n📊 合并报告..." -ForegroundColor Yellow
$mergeResult = npx mochawesome-merge "reports/mochawesome-batch-*.json" 2>&1
if ($mergeResult -and $mergeResult[0] -match "^\{") {
    $mergeResult | Out-File "reports/mochawesome.json" -Encoding UTF8
    Write-Host "✅ 合并报告已写入 reports/mochawesome.json" -ForegroundColor Green
} else {
    # 手动合并
    Write-Host "  手动合并 JSON..." -ForegroundColor Yellow
    $allJsonFiles = Get-ChildItem reports -Filter "mochawesome-batch-*.json" | Sort-Object Name
    $mergedStats = @{ tests = 0; passes = 0; failures = 0; pending = 0; skipped = 0; duration = 0 }
    $allSuites = @()
    
    foreach ($jf in $allJsonFiles) {
        try {
            $jdata = Get-Content $jf.FullName -Raw -Encoding UTF8 | ConvertFrom-Json
            if ($jdata.stats) {
                $mergedStats.tests += [int]$jdata.stats.tests
                $mergedStats.passes += [int]$jdata.stats.passes
                $mergedStats.failures += [int]$jdata.stats.failures
                $mergedStats.pending += [int]$jdata.stats.pending
                $mergedStats.skipped += [int]$jdata.stats.skipped
                $mergedStats.duration += [int]$jdata.stats.duration
            }
            if ($jdata.results) { $allSuites += $jdata.results }
        } catch { Write-Host "  跳过 $($jf.Name): $_" -ForegroundColor DarkYellow }
    }
    
    $merged = @{
        stats = $mergedStats
        results = $allSuites
    }
    $merged | ConvertTo-Json -Depth 10 | Out-File "reports/mochawesome.json" -Encoding UTF8
    Write-Host "✅ 手动合并完成 -> reports/mochawesome.json (tests=$($mergedStats.tests), passes=$($mergedStats.passes), failures=$($mergedStats.failures))" -ForegroundColor Green
}

# 输出最终汇总到日志（作为备用收集源）
$summary = @"
═══════════════════════════════════════════
Cypress 批量测试结果
═══════════════════════════════════════════
Tests: $($totalPass + $totalFail + $totalSkip)
Passing: $totalPass
Failing: $totalFail
Pending: $totalSkip
Duration: $([math]::Round($totalDuration, 1))s
Time: $(Get-Date -Format "yyyy-MM-dd HH:mm:ss")
═══════════════════════════════════════════
"@
$summary | Out-File "$root\cy-result.txt" -Encoding UTF8
Write-Host $summary
