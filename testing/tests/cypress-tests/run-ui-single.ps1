#!/usr/bin/env pwsh
<#
  单文件模式逐一运行所有 66 个 ui-*.cy.js
  每次只跑1个文件，避免 Electron 内存崩溃
  实时更新进度到 TestResults/ui-single-progress.md
#>

$ErrorActionPreference = "Continue"
$BaseDir   = "D:\2026\aiops.v2\testing\tests\cypress-tests"
$ReportDir = "D:\2026\aiops.v2\TestResults"
$LogDir    = "$BaseDir\reports\ui-single"

if (-not (Test-Path $ReportDir)) { New-Item $ReportDir -ItemType Directory -Force | Out-Null }
if (-not (Test-Path $LogDir))    { New-Item $LogDir    -ItemType Directory -Force | Out-Null }

# 获取所有 ui-*.cy.js，按名称排序
$specs = Get-ChildItem "$BaseDir\e2e\ui-0*.cy.js" | Sort-Object Name

$total   = $specs.Count
$done    = 0
$allPass = 0
$allFail = 0
$results = @()

Write-Host "========================================"
Write-Host "  Cypress 单文件模式 - $total 个 UI spec"
Write-Host "  开始时间: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')"
Write-Host "========================================"

foreach ($spec in $specs) {
    $done++
    $specName = $spec.Name
    $logFile  = "$LogDir\$specName.log"

    Write-Host ""
    Write-Host "[$done/$total] 运行: $specName ..."

    # 单跑, 禁用重试加速（0重试 + 缩短超时）
    $sw = [System.Diagnostics.Stopwatch]::StartNew()
    $output = & npx cypress run `
        --config-file cypress.fast.config.js `
        --spec "e2e/$specName" `
        --config "retries=0,defaultCommandTimeout=5000,pageLoadTimeout=12000" `
        2>&1
    $sw.Stop()
    $elapsed = [math]::Round($sw.Elapsed.TotalSeconds, 1)

    # 保存原始日志
    $output | Out-File $logFile -Encoding UTF8

    # 解析通过/失败
    $pLine = $output | Select-String "  \d+ passing" | Select-Object -Last 1
    $fLine = $output | Select-String "  \d+ failing" | Select-Object -Last 1
    $pv = if ($pLine) { [regex]::Match($pLine.Line, '(\d+) passing').Groups[1].Value } else { "0" }
    $fv = if ($fLine) { [regex]::Match($fLine.Line, '(\d+) failing').Groups[1].Value } else { "0" }
    $p  = [int]$pv
    $f  = [int]$fv

    # 判断是否崩溃
    $crashed = ($output | Select-String "renderer-process-crashed|GPU process exited") -ne $null
    $status  = if ($crashed) { "CRASH" } elseif ($f -eq 0 -and $p -gt 0) { "PASS" } elseif ($f -gt 0) { "FAIL" } else { "EMPTY" }

    $allPass += $p
    $allFail += $f

    $row = [PSCustomObject]@{
        File    = $specName
        Pass    = $p
        Fail    = $f
        Status  = $status
        Elapsed = "${elapsed}s"
    }
    $results += $row

    $icon = switch ($status) { "PASS" { "✅" } "FAIL" { "❌" } "CRASH" { "💥" } default { "⚠️" } }
    Write-Host "  $icon $specName  pass=$p fail=$f (${elapsed}s) [$status]"

    # ---- 实时写进度报告 ----
    $progressMd = @"
# Cypress UI 单文件测试进度报告
> 更新时间: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')  
> 进度: $done / $total 个文件

## 汇总
| 项目 | 数值 |
|------|------|
| 已运行文件数 | $done / $total |
| 累计通过用例 | $allPass |
| 累计失败用例 | $allFail |
| 通过率 | $(if(($allPass+$allFail) -gt 0){ [math]::Round($allPass/($allPass+$allFail)*100,1) }else{0})% |

## 各文件结果
| 文件 | 通过 | 失败 | 状态 | 耗时 |
|------|------|------|------|------|
$($results | ForEach-Object {
    $ic = switch ($_.Status) { "PASS" { "✅" } "FAIL" { "❌" } "CRASH" { "💥" } default { "⚠️" } }
    "| $($_.File) | $($_.Pass) | $($_.Fail) | $ic $($_.Status) | $($_.Elapsed) |"
} | Out-String)

---
*报告由 run-ui-single.ps1 自动生成*
"@
    $progressMd | Out-File "$ReportDir\ui-single-progress.md" -Encoding UTF8
}

# ---- 终态报告 ----
$passRate = if (($allPass + $allFail) -gt 0) { [math]::Round($allPass / ($allPass + $allFail) * 100, 2) } else { 0 }
$crashFiles = $results | Where-Object { $_.Status -eq "CRASH" }
$failFiles  = $results | Where-Object { $_.Status -eq "FAIL" }
$passFiles  = $results | Where-Object { $_.Status -eq "PASS" }

Write-Host ""
Write-Host "=============================="
Write-Host "  测试完成 $(Get-Date -Format 'HH:mm:ss')"
Write-Host "  ✅ 通过: $allPass   ❌ 失败: $allFail"
Write-Host "  通过率: $passRate%"
Write-Host "  通过文件: $($passFiles.Count)  失败文件: $($failFiles.Count)  崩溃: $($crashFiles.Count)"
Write-Host "=============================="

$finalMd = @"
# Cypress UI 单文件测试最终报告
> 生成时间: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')

## 总览
| 项目 | 数值 |
|------|------|
| 总文件数 | $total |
| ✅ 通过文件 | $($passFiles.Count) |
| ❌ 失败文件 | $($failFiles.Count) |
| 💥 崩溃文件 | $($crashFiles.Count) |
| 累计通过用例 | **$allPass** |
| 累计失败用例 | **$allFail** |
| **用例通过率** | **$passRate%** |

## 各文件详细结果
| 文件 | 通过 | 失败 | 状态 | 耗时 |
|------|------|------|------|------|
$($results | ForEach-Object {
    $ic = switch ($_.Status) { "PASS" { "✅" } "FAIL" { "❌" } "CRASH" { "💥" } default { "⚠️" } }
    "| $($_.File) | $($_.Pass) | $($_.Fail) | $ic $($_.Status) | $($_.Elapsed) |"
} | Out-String)

$(if($failFiles.Count -gt 0) {
@"
## ❌ 失败文件清单
$($failFiles | ForEach-Object { "- $($_.File) (pass=$($_.Pass) fail=$($_.Fail))" } | Out-String)
"@
})

$(if($crashFiles.Count -gt 0) {
@"
## 💥 崩溃文件清单
$($crashFiles | ForEach-Object { "- $($_.File)" } | Out-String)
"@
})

---
*日志目录: tests/cypress-tests/reports/ui-single/*
"@

$finalMd | Out-File "$ReportDir\ui-single-final.md" -Encoding UTF8
$finalMd | Out-File "$ReportDir\ui-single-progress.md" -Encoding UTF8

Write-Host ""
Write-Host "📄 最终报告: $ReportDir\ui-single-final.md"
