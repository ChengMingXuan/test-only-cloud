#!/usr/bin/env pwsh
<#
.SYNOPSIS
  逐个原子化运行 ui-*.cy.js 文件（每次独立 Cypress 进程，避免浏览器状态累积）
.DESCRIPTION
  每个 ui-*.cy.js 文件单独启动 Cypress，完成后记录结果
#>

$projectDir = "D:\2026\aiops.v2\testing\tests\cypress-tests"
$specDir = "$projectDir\e2e"
$resultsDir = "D:\2026\aiops.v2\TestResults\ui-atomic"
New-Item -ItemType Directory -Force -Path $resultsDir | Out-Null

# 获取需要测试的文件列表（65, parametrized, ui-001 到 ui-066）
$nonUiFiles = @("65-auth-error-profile.cy.js", "parametrized-comprehensive.cy.js")
$uiFiles = Get-ChildItem "$specDir\ui-*.cy.js" | Sort-Object Name | Select-Object -ExpandProperty Name
$allFiles = $nonUiFiles + $uiFiles

$results = @()
$total = $allFiles.Count
$idx = 0

foreach ($file in $allFiles) {
    $idx++
    $specPath = "$specDir\$file"
    $outFile = "$resultsDir\$($file -replace '\.cy\.js$', '.txt')"
    
    Write-Host ""
    Write-Host "[$idx/$total] Running: $file" -ForegroundColor Cyan
    
    # 运行单个文件（独立进程，每次浏览器重启）
    $proc = Start-Process -FilePath "cmd.exe" `
        -ArgumentList "/c npx cypress run --project `"$projectDir`" --spec `"$specPath`" --headless --browser electron" `
        -WorkingDirectory "D:\2026\aiops.v2" `
        -RedirectStandardOutput $outFile `
        -RedirectStandardError "$outFile.err" `
        -PassThru -NoNewWindow -Wait
    
    # 等待 TCP 连接释放（避免 ENOBUFS）
    Start-Sleep -Seconds 5
    
    # 解析结果
    if (Test-Path $outFile) {
        $content = Get-Content $outFile -Raw -ErrorAction SilentlyContinue
        if ($content) {
            $mPass = [regex]::Match($content, '(\d+) passing')
            $mFail = [regex]::Match($content, '(\d+) failing')
            $passing = if ($mPass.Success) { $mPass.Groups[1].Value } else { "0" }
            $failing = if ($mFail.Success) { $mFail.Groups[1].Value } else { "0" }
        } else {
            $passing = "0"; $failing = "0"
        }
        
        # ENOBUFS 检测：0 passing + 0 failing + non-zero exit = 资源耗尽，重试一次
        if ($proc.ExitCode -ne 0 -and $passing -eq "0" -and $failing -eq "0") {
            Write-Host "  ⚠️  资源不足，5秒后重试..." -ForegroundColor Yellow
            Start-Sleep -Seconds 10
            $proc = Start-Process -FilePath "cmd.exe" `
                -ArgumentList "/c npx cypress run --project `"$projectDir`" --spec `"$specPath`" --headless --browser electron" `
                -WorkingDirectory "D:\2026\aiops.v2" `
                -RedirectStandardOutput $outFile `
                -RedirectStandardError "$outFile.err" `
                -PassThru -NoNewWindow -Wait
            $content = Get-Content $outFile -Raw -ErrorAction SilentlyContinue
            if ($content) {
                $mPass = [regex]::Match($content, '(\d+) passing')
                $mFail = [regex]::Match($content, '(\d+) failing')
                $passing = if ($mPass.Success) { $mPass.Groups[1].Value } else { "0" }
                $failing = if ($mFail.Success) { $mFail.Groups[1].Value } else { "0" }
            }
            Start-Sleep -Seconds 5
        }
        
        $status = if ($proc.ExitCode -eq 0) { "PASS" } else { "FAIL" }
        Write-Host "  $status : $passing passing, $failing failing" -ForegroundColor $(if ($status -eq "PASS") { "Green" } else { "Red" })
    } else {
        $passing = "0"; $failing = "0"; $status = "ERROR"
        Write-Host "  ERROR: 无输出文件" -ForegroundColor Red
    }
    
    $results += [PSCustomObject]@{
        File = $file
        Status = $status
        Passing = [int]$passing
        Failing = [int]$failing
        ExitCode = $proc.ExitCode
    }
}

# 汇总
$totalPassing = ($results | Measure-Object -Property Passing -Sum).Sum
$totalFailing = ($results | Measure-Object -Property Failing -Sum).Sum
$passFiles = ($results | Where-Object { $_.Status -eq "PASS" }).Count
$failFiles = ($results | Where-Object { $_.Status -ne "PASS" }).Count

Write-Host ""
Write-Host "===== UI 文件测试汇总 =====" -ForegroundColor Yellow
Write-Host "文件: $passFiles PASS / $failFiles FAIL / $total 共"
Write-Host "测试: $totalPassing 通过 / $totalFailing 失败"

# 保存汇总结果
$summary = @{
    timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    files = $results
    summary = @{
        totalFiles = $total
        passFiles = $passFiles
        failFiles = $failFiles
        totalPassing = $totalPassing
        totalFailing = $totalFailing
    }
}
$summary | ConvertTo-Json -Depth 5 | Set-Content "$resultsDir\summary.json"
Write-Host "结果保存至: $resultsDir\summary.json"
