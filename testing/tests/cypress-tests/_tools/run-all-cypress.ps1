#!/usr/bin/env pwsh
# ====================================================================
# Cypress 全量测试批量执行脚本
# 将 135 个 spec 文件按批次执行，汇总通过/失败情况
# ====================================================================

param(
    [string]$StartFrom = "",       # 从指定spec开始（用于断点续跑）
    [int]$BatchSize = 10,          # 每批spec数量
    [switch]$FailedOnly,           # 仅重跑失败项
    [string]$FailedListFile = ""   # 失败spec列表文件
)

$ErrorActionPreference = "Continue"
$BaseDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $BaseDir

# 确保reports目录存在
if (-not (Test-Path "reports")) { New-Item -ItemType Directory -Path "reports" | Out-Null }

# 加载失败列表（如果指定）
$FailedSpecs = @()
if ($FailedOnly -and $FailedListFile -and (Test-Path $FailedListFile)) {
    $FailedSpecs = Get-Content $FailedListFile | Where-Object { $_ -match "\.cy\.js$" }
    Write-Host "📋 仅重跑失败用例: $($FailedSpecs.Count) 个" -ForegroundColor Yellow
}

# 获取所有spec文件
$AllSpecs = Get-ChildItem "e2e" -Filter "*.cy.js" | Sort-Object Name | Select-Object -ExpandProperty Name

# 如果是失败重跑模式，过滤列表
if ($FailedOnly -and $FailedSpecs.Count -gt 0) {
    $AllSpecs = $AllSpecs | Where-Object { $FailedSpecs -contains $_ }
}

# 如果指定起始文件
if ($StartFrom) {
    $idx = [Array]::IndexOf($AllSpecs, $StartFrom)
    if ($idx -ge 0) {
        $AllSpecs = $AllSpecs[$idx..($AllSpecs.Count-1)]
        Write-Host "▶ 从 $StartFrom 开始（共 $($AllSpecs.Count) 个剩余）" -ForegroundColor Cyan
    }
}

Write-Host "`n🚀 Cypress 全量测试开始" -ForegroundColor Green
Write-Host "   总计: $($AllSpecs.Count) 个 spec 文件" -ForegroundColor Green
Write-Host "   批次大小: $BatchSize`n" -ForegroundColor Green

# 统计变量
$TotalPassing = 0
$TotalFailing = 0
$FailedSpecsList = @()
$PassedSpecsList = @()
$BatchNum = 0
$StartTime = Get-Date

# 将spec分批
$Batches = @()
for ($i = 0; $i -lt $AllSpecs.Count; $i += $BatchSize) {
    $end = [Math]::Min($i + $BatchSize - 1, $AllSpecs.Count - 1)
    $Batches += ,($AllSpecs[$i..$end])
}

Write-Host "📦 共 $($Batches.Count) 个批次`n" -ForegroundColor Cyan

foreach ($batch in $Batches) {
    $BatchNum++
    $specList = $batch -join ","
    $specPatterns = ($batch | ForEach-Object { "e2e/$_" }) -join ","
    $logFile = "reports\batch-auto-$BatchNum.log"
    
    $batchStart = [int](($BatchNum - 1) * $BatchSize + 1)
    $batchEnd = [int]([Math]::Min($BatchNum * $BatchSize, $AllSpecs.Count))
    
    Write-Host "┌─ 批次 $BatchNum/$($Batches.Count) [${batchStart}-${batchEnd}/$($AllSpecs.Count)] " -NoNewline -ForegroundColor Cyan
    Write-Host "($($batch.Count) specs)" -ForegroundColor Gray
    
    $batch | ForEach-Object { Write-Host "│  · $_" -ForegroundColor Gray }
    
    # 运行 Cypress
    $output = npx cypress run --config-file cypress.fast.config.js --spec $specPatterns 2>&1
    $output | Out-File $logFile -Encoding UTF8
    
    # 解析结果
    $batchPassing = 0
    $batchFailing = 0
    
    $output | Select-String "^\s+(\d+) passing" | ForEach-Object {
        if ($_.Matches[0].Groups[1].Value -match '^\d+$') {
            $batchPassing += [int]$_.Matches[0].Groups[1].Value
        }
    }
    $output | Select-String "^\s+(\d+) failing" | ForEach-Object {
        if ($_.Matches[0].Groups[1].Value -match '^\d+$') {
            $batchFailing += [int]$_.Matches[0].Groups[1].Value
        }
    }
    
    $TotalPassing += $batchPassing
    $TotalFailing += $batchFailing
    
    # 检查哪些spec失败了
    $failedInBatch = @()
    foreach ($spec in $batch) {
        # 检查该spec是否在失败行中出现
        $specFails = $output | Select-String "failing" | Where-Object { $_ -match $spec.Replace(".", "\.") }
        if ($batchFailing -gt 0) {
            # 查找spec运行结果块
            $specResult = $output | Select-String "Spec Ran:.*$($spec.Replace('.cy.js',''))" 
            if ($specResult) {
                # 找到spec前面的失败数
                $lineIdx = [Array]::IndexOf($output, $specResult[0].Line)
                if ($lineIdx -gt 0) {
                    $prevLines = $output[([Math]::Max(0,$lineIdx-10))..$lineIdx]
                    $hasFail = $prevLines | Select-String "Failing:\s+[1-9]"
                    if ($hasFail) {
                        $failedInBatch += $spec
                        $FailedSpecsList += $spec
                    }
                }
            }
        }
        if (-not ($FailedSpecsList -contains $spec)) {
            $PassedSpecsList += $spec
        }
    }
    
    $status = if ($batchFailing -eq 0) { "✅" } else { "❌" }
    Write-Host "└─ $status 通过: $batchPassing | 失败: $batchFailing" -ForegroundColor (if ($batchFailing -eq 0) { "Green" } else { "Red" })
    
    if ($failedInBatch.Count -gt 0) {
        Write-Host "   ⚠ 失败的spec: $($failedInBatch -join ', ')" -ForegroundColor Red
        # 输出失败详情
        $output | Select-String "AssertionError:" | Select-Object -First 5 | ForEach-Object {
            Write-Host "   ! $($_.Line.Trim())" -ForegroundColor DarkRed
        }
    }
    Write-Host ""
}

# 最终汇总
$Duration = (Get-Date) - $StartTime
$TotalSpecs = $AllSpecs.Count
$PassRate = if ($TotalPassing + $TotalFailing -gt 0) { [Math]::Round($TotalPassing / ($TotalPassing + $TotalFailing) * 100, 1) } else { 0 }

Write-Host "=" * 70 -ForegroundColor Cyan
Write-Host "📊 Cypress 全量测试汇总" -ForegroundColor Cyan
Write-Host "=" * 70 -ForegroundColor Cyan
Write-Host "  Spec 文件: $TotalSpecs" 
Write-Host "  通过用例: $TotalPassing" -ForegroundColor Green
Write-Host "  失败用例: $TotalFailing" -ForegroundColor (if ($TotalFailing -eq 0) { "Green" } else { "Red" })
Write-Host "  通过率:   $PassRate%"
Write-Host "  耗时:     $([Math]::Round($Duration.TotalMinutes, 1)) 分钟"
Write-Host ""

if ($FailedSpecsList.Count -gt 0) {
    Write-Host "❌ 失败的 Spec 文件 ($($FailedSpecsList.Count) 个):" -ForegroundColor Red
    $FailedSpecsList | ForEach-Object { Write-Host "   - $_" -ForegroundColor Red }
    
    # 保存失败列表
    $FailedSpecsList | Out-File "reports\failed-specs.txt" -Encoding UTF8
    Write-Host "`n💾 失败列表已保存到 reports\failed-specs.txt" -ForegroundColor Yellow
    Write-Host "   重跑失败项: .\run-all-cypress.ps1 -FailedOnly -FailedListFile reports\failed-specs.txt`n" -ForegroundColor Yellow
} else {
    Write-Host "🎉 全部通过！" -ForegroundColor Green
}

# 返回退出码
exit $TotalFailing
