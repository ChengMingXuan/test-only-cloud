# 批量测试所有 Cypress 文件，收集结果
param(
    [string]$Pattern = "*.cy.js",
    [int]$StartFrom = 1,
    [int]$EndAt = 999
)

$ErrorActionPreference = "Continue"
Set-Location $PSScriptRoot

$files = Get-ChildItem "e2e\$Pattern" | Sort-Object Name
$results = @()
$idx = 0

foreach ($file in $files) {
    $idx++
    if ($idx -lt $StartFrom -or $idx -gt $EndAt) { continue }
    
    $name = $file.Name
    Write-Host "[$idx/$($files.Count)] Testing: $name" -ForegroundColor Cyan
    
    $output = npx cypress run --config-file cypress.fast.config.js --spec "e2e/$name" --config "retries=0" 2>&1 | Out-String
    
    # 解析结果
    $passing = 0; $failing = 0; $total = 0
    if ($output -match "Passing:\s+(\d+)") { $passing = [int]$Matches[1] }
    if ($output -match "Failing:\s+(\d+)") { $failing = [int]$Matches[1] }
    if ($output -match "Tests:\s+(\d+)") { $total = [int]$Matches[1] }
    
    $status = if ($failing -eq 0 -and $total -gt 0) { "PASS" } elseif ($total -eq 0) { "SKIP" } else { "FAIL" }
    
    # 提取错误
    $errors = @()
    $lines = $output -split "`n"
    for ($i = 0; $i -lt $lines.Count; $i++) {
        if ($lines[$i] -match "^\s+\d+\)") {
            $errLine = $lines[$i].Trim()
            # 获取下面几行的错误描述
            for ($j = $i+1; $j -lt [Math]::Min($i+5, $lines.Count); $j++) {
                $l = $lines[$j].Trim()
                if ($l -match "Error|expected|Timed out|Cannot|assert") {
                    $errLine += " | $l"
                    break
                }
            }
            $errors += $errLine
        }
    }
    
    $results += [PSCustomObject]@{
        Index   = $idx
        File    = $name
        Status  = $status
        Total   = $total
        Pass    = $passing
        Fail    = $failing
        Errors  = ($errors -join " ;; ")
    }
    
    $symbol = if ($status -eq "PASS") { "✅" } elseif ($status -eq "FAIL") { "❌" } else { "⏭️" }
    Write-Host "  $symbol $status - Pass: $passing, Fail: $failing" -ForegroundColor $(if ($status -eq "PASS") { "Green" } else { "Red" })
}

# 输出汇总
$passCount = ($results | Where-Object Status -eq "PASS").Count
$failCount = ($results | Where-Object Status -eq "FAIL").Count
$skipCount = ($results | Where-Object Status -eq "SKIP").Count

Write-Host "`n========== 汇总 ==========" -ForegroundColor Yellow
Write-Host "总文件: $($results.Count), 通过: $passCount, 失败: $failCount, 跳过: $skipCount" -ForegroundColor Yellow

# 保存结果
$results | Format-Table -AutoSize | Out-String | Set-Content "reports\batch-results.txt"
$results | Where-Object Status -eq "FAIL" | Select-Object Index, File, Fail, Errors | Format-Table -AutoSize -Wrap | Out-String | Set-Content "reports\failures.txt"

Write-Host "`n结果已保存到 reports\batch-results.txt 和 reports\failures.txt"
