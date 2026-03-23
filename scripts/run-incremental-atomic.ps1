<#
.SYNOPSIS
  增量原子化测试执行器 - 逐文件执行增量变更的测试，记录每个文件的通过/失败/跳过状态
.DESCRIPTION
  从 git diff 获取增量变更的测试文件，按工具分类逐个执行，输出 JSON 结果
#>
param(
    [ValidateSet("all","cypress","puppeteer","playwright","selenium","k6","pytest")]
    [string]$Tool = "all",
    [int]$CommitRange = 5,
    [switch]$DryRun
)

$ErrorActionPreference = "Continue"
$WorkspaceRoot = Split-Path $PSScriptRoot -Parent
$ResultsDir = Join-Path $WorkspaceRoot "TestResults\incremental"
if (!(Test-Path $ResultsDir)) { New-Item -ItemType Directory -Path $ResultsDir -Force | Out-Null }

$Timestamp = Get-Date -Format "yyyyMMdd-HHmmss"
$ResultFile = Join-Path $ResultsDir "incremental-$Timestamp.json"

# 获取增量文件
Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "  增量原子化测试执行器" -ForegroundColor Cyan
Write-Host "  时间: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')" -ForegroundColor Cyan
Write-Host "  范围: HEAD~$CommitRange..HEAD" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

# 获取新增和修改的文件
$newFiles = git diff --diff-filter=A --name-only "HEAD~$CommitRange" HEAD -- testing/tests/ k6/ 2>&1 | Where-Object { $_ -and $_.Trim() -ne '' }
$modFiles = git diff --diff-filter=M --name-only "HEAD~$CommitRange" HEAD -- testing/tests/ k6/ 2>&1 | Where-Object { $_ -and $_.Trim() -ne '' }

# 分类函数
function Get-TestTool($filePath) {
    if ($filePath -match 'cypress-tests.*\.cy\.js$') { return "cypress" }
    if ($filePath -match 'puppeteer-tests.*\.test\.js$') { return "puppeteer" }
    if ($filePath -match 'playwright-tests.*\.spec\.ts$') { return "playwright" }
    if ($filePath -match 'selenium-tests.*\.py$' -and $filePath -match 'test_') { return "selenium" }
    if ($filePath -match 'k6[/\\]' -and $filePath -match '\.js$') { return "k6" }
    if ($filePath -match 'tests[/\\].*\.py$' -and $filePath -match 'test_') { return "pytest" }
    return $null
}

# 构建测试文件清单
$testQueue = @()
foreach ($f in $newFiles) {
    $detectedTool = Get-TestTool $f
    if ($detectedTool) { $testQueue += [PSCustomObject]@{ File=$f; Tool=$detectedTool; Change="NEW" } }
}
foreach ($f in $modFiles) {
    $detectedTool = Get-TestTool $f
    if ($detectedTool) { $testQueue += [PSCustomObject]@{ File=$f; Tool=$detectedTool; Change="MOD" } }
}

# 按工具筛选
if ($Tool -ne "all") {
    $testQueue = $testQueue | Where-Object { $_.Tool -eq $Tool }
}

# 按工具分组统计
$summary = $testQueue | Group-Object Tool | ForEach-Object {
    $newCount = ($_.Group | Where-Object { $_.Change -eq "NEW" }).Count
    $modCount = ($_.Group | Where-Object { $_.Change -eq "MOD" }).Count
    Write-Host ("  {0,-12} 新增:{1,3}  修改:{2,3}  共:{3,3}" -f $_.Name, $newCount, $modCount, $_.Count) -ForegroundColor Yellow
}

$totalFiles = $testQueue.Count
Write-Host "`n  总计待测试文件: $totalFiles" -ForegroundColor White
Write-Host ""

if ($DryRun) {
    Write-Host "  [DryRun] 仅列出文件，不执行测试" -ForegroundColor Gray
    $testQueue | Format-Table -Property Change, Tool, File -AutoSize
    return
}

# 执行结果收集
$results = @()
$passed = 0; $failed = 0; $skipped = 0; $current = 0

foreach ($item in $testQueue) {
    $current++
    $filePath = Join-Path $WorkspaceRoot $item.File
    $shortName = Split-Path $item.File -Leaf
    $tag = if ($item.Change -eq "NEW") { "[NEW]" } else { "[MOD]" }
    
    Write-Host ("[$current/$totalFiles] $tag {0,-12} {1}" -f $item.Tool, $shortName) -NoNewline

    # 检查文件是否存在
    if (!(Test-Path $filePath)) {
        Write-Host " => SKIP (文件不存在)" -ForegroundColor DarkGray
        $skipped++
        $results += [PSCustomObject]@{
            File=$item.File; Tool=$item.Tool; Change=$item.Change
            Status="SKIP"; Tests=0; Pass=0; Fail=0; Duration="0s"; Error="文件不存在"
        }
        continue
    }

    # 非测试文件跳过 (辅助脚本/配置等)
    $skipPatterns = @('\.ini$', '\.json$', '\.txt$', 'conftest\.py$', 'commands\.js$', 
                      'global-setup', 'generate-', 'fix-', 'batch-fix', 'analyze-', 
                      'parse-', 'check-', 'verify-', 'run-one', 'run-and-', 'run-tests\.js$',
                      'patch-', 'auto-fix', 'extract-', 'parallel-', 'test-subprocess',
                      '__init__\.py$', 'test-helpers\.js$', 'k6[/\\]config\.js$')
    $shouldSkip = $false
    foreach ($pat in $skipPatterns) {
        if ($item.File -match $pat) { $shouldSkip = $true; break }
    }
    if ($shouldSkip) {
        Write-Host " => SKIP (辅助文件)" -ForegroundColor DarkGray
        $skipped++
        $results += [PSCustomObject]@{
            File=$item.File; Tool=$item.Tool; Change=$item.Change
            Status="SKIP"; Tests=0; Pass=0; Fail=0; Duration="0s"; Error="辅助文件"
        }
        continue
    }

    $startTime = Get-Date
    $testCount = 0; $passCount = 0; $failCount = 0; $errorMsg = ""
    $status = "FAIL"

    try {
        switch ($item.Tool) {
            "cypress" {
                $specPath = $item.File -replace '^testing/tests/cypress-tests/', ''
                $output = & cmd /c "cd /d `"$1\testing\tests\cypress-tests`" && npx cypress run --spec `"$specPath`" --headless --browser electron 2>&1"
                $outputStr = $output -join "`n"
                
                # 解析 Cypress 结果
                if ($outputStr -match 'All specs passed') {
                    $status = "PASS"
                }
                if ($outputStr -match '(\d+)\s+passing') { $passCount = [int]$Matches[1] }
                if ($outputStr -match '(\d+)\s+failing') { $failCount = [int]$Matches[1] }
                $testCount = $passCount + $failCount
                if ($failCount -gt 0) { $status = "FAIL"; $errorMsg = ($output | Select-String "AssertionError|Error:|CypressError" | Select-Object -First 1) }
                if ($testCount -eq 0 -and $outputStr -match 'SyntaxError|Error:') { 
                    $status = "ERROR"; $errorMsg = ($output | Select-String "SyntaxError|Error:" | Select-Object -First 1)
                }
            }
            "puppeteer" {
                $testPath = $item.File -replace '^testing/tests/puppeteer-tests/', ''
                $output = & cmd /c "cd /d `"$1\testing\tests\puppeteer-tests`" && npx jest `"$testPath`" --no-coverage --forceExit 2>&1"
                $outputStr = $output -join "`n"
                
                if ($outputStr -match 'Tests:\s+(\d+)\s+passed') { $passCount = [int]$Matches[1]; $status = "PASS" }
                if ($outputStr -match 'Tests:\s+(\d+)\s+failed') { $failCount = [int]$Matches[1]; $status = "FAIL" }
                if ($outputStr -match 'Tests:\s+\d+ failed,\s+(\d+)\s+passed') { $passCount = [int]$Matches[1] }
                $testCount = $passCount + $failCount
                if ($testCount -eq 0 -and $outputStr -match 'FAIL|Error') { $status = "ERROR"; $errorMsg = "Jest execution error" }
            }
            "playwright" {
                $testPath = $item.File -replace '^testing/tests/playwright-tests/', ''
                $output = & cmd /c "cd /d `"$1\testing\tests\playwright-tests`" && npx playwright test `"$testPath`" --reporter=list 2>&1"
                $outputStr = $output -join "`n"
                
                if ($outputStr -match '(\d+) passed') { $passCount = [int]$Matches[1]; $status = "PASS" }
                if ($outputStr -match '(\d+) failed') { $failCount = [int]$Matches[1]; $status = "FAIL" }
                $testCount = $passCount + $failCount
            }
            "selenium" {
                $testPath = Join-Path $WorkspaceRoot $item.File
                $output = & cmd /c "cd /d `"$WorkspaceRoot`" && python -m pytest `"$testPath`" -v --tb=short -x 2>&1"
                $outputStr = $output -join "`n"
                
                if ($outputStr -match '(\d+) passed') { $passCount = [int]$Matches[1]; $status = "PASS" }
                if ($outputStr -match '(\d+) failed') { $failCount = [int]$Matches[1]; $status = "FAIL" }
                $testCount = $passCount + $failCount
            }
            "k6" {
                $scriptPath = Join-Path $WorkspaceRoot $item.File
                $output = & cmd /c "k6 run --duration 5s --vus 1 `"$scriptPath`" 2>&1"
                $outputStr = $output -join "`n"
                
                if ($outputStr -match 'default.*✓' -or $outputStr -match 'iteration_duration') {
                    $status = "PASS"; $passCount = 1; $testCount = 1
                } else {
                    $status = "FAIL"; $failCount = 1; $testCount = 1
                    $errorMsg = ($output | Select-String "ERRO|level=error|GoError" | Select-Object -First 1)
                }
            }
            "pytest" {
                $testPath = Join-Path $WorkspaceRoot $item.File
                $output = & cmd /c "cd /d `"$WorkspaceRoot`" && python -m pytest `"$testPath`" -v --tb=short 2>&1"
                $outputStr = $output -join "`n"
                
                if ($outputStr -match '(\d+) passed') { $passCount = [int]$Matches[1] }
                if ($outputStr -match '(\d+) failed') { $failCount = [int]$Matches[1] }
                $testCount = $passCount + $failCount
                $status = if ($failCount -eq 0 -and $passCount -gt 0) { "PASS" } elseif ($failCount -gt 0) { "FAIL" } else { "ERROR" }
            }
        }
    } catch {
        $status = "ERROR"
        $errorMsg = $_.Exception.Message
    }

    $duration = "{0:N1}s" -f ((Get-Date) - $startTime).TotalSeconds

    # 输出结果
    switch ($status) {
        "PASS"  { Write-Host " => PASS ($passCount/$testCount) [$duration]" -ForegroundColor Green; $passed++ }
        "FAIL"  { Write-Host " => FAIL ($passCount/$testCount) [$duration]" -ForegroundColor Red; $failed++ }
        "ERROR" { Write-Host " => ERROR [$duration] $errorMsg" -ForegroundColor Red; $failed++ }
        "SKIP"  { Write-Host " => SKIP" -ForegroundColor DarkGray; $skipped++ }
    }

    $results += [PSCustomObject]@{
        File=$item.File; Tool=$item.Tool; Change=$item.Change
        Status=$status; Tests=$testCount; Pass=$passCount; Fail=$failCount
        Duration=$duration; Error=$errorMsg
    }
}

# 输出汇总
Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "  增量原子化测试汇总" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  总文件: $totalFiles" -ForegroundColor White
Write-Host "  通过:   $passed" -ForegroundColor Green
Write-Host "  失败:   $failed" -ForegroundColor $(if ($failed -gt 0) { "Red" } else { "Green" })
Write-Host "  跳过:   $skipped" -ForegroundColor DarkGray

# 按工具汇总
Write-Host "`n  按工具分类:" -ForegroundColor Yellow
$results | Group-Object Tool | ForEach-Object {
    $tp = ($_.Group | Where-Object { $_.Status -eq "PASS" }).Count
    $tf = ($_.Group | Where-Object { $_.Status -in @("FAIL","ERROR") }).Count
    $ts = ($_.Group | Where-Object { $_.Status -eq "SKIP" }).Count
    $icon = if ($tf -eq 0) { "✅" } else { "❌" }
    Write-Host ("  $icon {0,-12} Pass:{1,3}  Fail:{2,3}  Skip:{3,3}" -f $_.Name, $tp, $tf, $ts)
}

# 列出失败项
$failedItems = $results | Where-Object { $_.Status -in @("FAIL","ERROR") }
if ($failedItems.Count -gt 0) {
    Write-Host "`n  失败明细:" -ForegroundColor Red
    foreach ($fi in $failedItems) {
        Write-Host "    ❌ [$($fi.Change)] $($fi.File)" -ForegroundColor Red
        if ($fi.Error) { Write-Host "       $($fi.Error)" -ForegroundColor DarkRed }
    }
}

# 保存 JSON 结果
$jsonResult = @{
    timestamp = Get-Date -Format "yyyy-MM-ddTHH:mm:ss"
    commitRange = "HEAD~$CommitRange..HEAD"
    total = $totalFiles
    passed = $passed
    failed = $failed
    skipped = $skipped
    results = $results | ForEach-Object {
        @{
            file = $_.File; tool = $_.Tool; change = $_.Change
            status = $_.Status; tests = $_.Tests; pass = $_.Pass; fail = $_.Fail
            duration = $_.Duration; error = $_.Error
        }
    }
} | ConvertTo-Json -Depth 4

$jsonResult | Out-File -FilePath $ResultFile -Encoding utf8
Write-Host "`n  结果已保存: $ResultFile" -ForegroundColor Gray
Write-Host "========================================`n" -ForegroundColor Cyan
