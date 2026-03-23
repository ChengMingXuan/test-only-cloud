#!/usr/bin/env pwsh
<#
.SYNOPSIS
Cypress 分批串行执行脚本
- 避免 16 worker 同时登录导致的 429 限流
- 按自然分组执行（2-3 个 spec 为一批）
- 每批之间延迟 30 秒给后端恢复的时间
#>

$SpecDir = "D:\2026\aiops.v2\testing\tests\cypress-tests\e2e"
$ReportsDir = "D:\2026\aiops.v2\testing\tests\cypress-tests\reports"

# 获取所有 spec 文件
$allSpecs = Get-ChildItem "$SpecDir\*.cy.js" | Select-Object -ExpandProperty Name | Sort-Object

Write-Host "📊 Cypress 分批串行执行（防止认证限流）" -ForegroundColor Green
Write-Host "   总规格数: $($allSpecs.Count)" -ForegroundColor Yellow
Write-Host "   批策略: 4 个编辑按一批（串行，2 worker/批）`n" -ForegroundColor Yellow

$batchSize = 4
$batches = @()

for ($i = 0; $i -lt $allSpecs.Count; $i += $batchSize) {
    $end = [Math]::Min($i + $batchSize - 1, $allSpecs.Count - 1)
    $batch = $allSpecs[$i..$end]
    $batches += ,@($batch)
}

$batchNum = 0
foreach ($batch in $batches) {
    $batchNum++
    $specList = $batch -join ','
    $logFile = "$ReportsDir\cypress-batch-$($batchNum).log"
    
    Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Gray
    Write-Host "批 $batchNum / $($batches.Count) - $($batch.Count) 个文件" -ForegroundColor Cyan
    Write-Host "规格: $($batch -join ', ')" -ForegroundColor Gray
    
    cd "D:\2026\aiops.v2\testing\tests\cypress-tests"
    
    # 关键：只用 2 个 worker（而不是 16）
    npx cypress run `
        --config-file cypress.fast.config.js `
        --spec "e2e/$specList" `
        --headless `
        --browser electron `
        2>&1 | Tee-Object -FilePath $logFile
    
    $exitCode = $LASTEXITCODE
    
    # 从日志提取结果
    $result = Select-String "passing|failing" $logFile | Select-Object -Last 1
    if ($result) {
        Write-Host "✅ $($result.Line.Trim())" -ForegroundColor Green
    }
    
    if ($exitCode -ne 0) {
        Write-Host "⚠️  此批有失败，但继续下一批...`n" -ForegroundColor Yellow
    }
    
    # 批间延迟（给后端恢复）
    if ($batchNum -lt $batches.Count) {
        Write-Host "⏰ 等待 30 秒（给后端恢复）...`n" -ForegroundColor Gray
        Start-Sleep -Seconds 30
    }
}

Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Gray
Write-Host "✨ Cypress 全部批次执行完成！" -ForegroundColor Green
Write-Host "📂 日志目录: $ReportsDir`n" -ForegroundColor Cyan

# 汇总报告
Write-Host "📋 批次汇总：" -ForegroundColor Yellow
$batchLogs = Get-ChildItem "$ReportsDir\cypress-batch-*.log" | Sort-Object Name
foreach ($log in $batchLogs) {
    $result = Select-String "passing|failing" $log.FullName | Select-Object -Last 1
    if ($result) {
        Write-Host "  $($log.Name): $($result.Line.Trim())" -ForegroundColor Cyan
    }
}
