<#
.SYNOPSIS
    Playwright 快速并发执行 - 利用原生 Workers 并行，避免端口冲突
.DESCRIPTION
    不使用 Start-Job 多进程（会导致 Mock Server 端口冲突），
    而是用 Playwright 原生 --workers 参数实现进程内并行。
    global-setup 只运行一次，所有 worker 共享同一个 Mock Server。
.PARAMETER Workers
    并行 Worker 数（默认 8，机器有 20 核）
.PARAMETER Project
    指定浏览器项目（不指定则跑全部 7 个项目）
.PARAMETER MaxFailures
    最大失败数，达到后停止（默认 0=不限制）
.PARAMETER Shard
    分片参数，格式 "1/3" 表示共3片取第1片（用于手动多进程分片）
.PARAMETER ResumeOnly
    仅执行未完成的文件（排除已有原子化结果的文件）
.PARAMETER SkipAtomicSplit
    跳过结果拆分到原子化 JSON（仅生成总 JUnit XML）
#>
param(
    [int]$Workers = 8,
    [string]$Project = "",
    [int]$MaxFailures = 0,
    [string]$Shard = "",
    [switch]$ResumeOnly,
    [switch]$SkipAtomicSplit
)

$ErrorActionPreference = "Continue"
$RootDir = (Resolve-Path "$PSScriptRoot\..").Path
$PlaywrightDir = "$RootDir\testing\tests\playwright-tests"
$AtomicDir = "$RootDir\TestResults\atomic\playwright"
$JunitXml = "$RootDir\TestResults\playwright-results.xml"

Write-Host ""
Write-Host "╔══════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║  Playwright 快速并发执行（原生 Workers 模式）               ║" -ForegroundColor Cyan
Write-Host "╚══════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""

# ──── 步骤 1：确认待执行文件 ────
$allSpecs = @(Get-ChildItem "$PlaywrightDir\tests" -Filter "*.spec.ts" -Recurse | Select-Object -ExpandProperty FullName)
$totalSpecs = $allSpecs.Count
Write-Host "  总 spec 文件: $totalSpecs" -ForegroundColor White

$excludeSpecs = @()
if ($ResumeOnly) {
    # 读取已有原子化结果，排除已通过的文件
    if (Test-Path $AtomicDir) {
        $doneFiles = @(Get-ChildItem $AtomicDir -Filter "*.json" -ErrorAction SilentlyContinue | ForEach-Object {
            $j = Get-Content $_.FullName -Raw | ConvertFrom-Json
            if ($j.total -gt 0 -and $j.failed -eq 0) { $_.BaseName }
        })
        if ($doneFiles.Count -gt 0) {
            # 映射 safe name 回 spec 文件
            foreach ($spec in $allSpecs) {
                $relPath = $spec.Replace("$PlaywrightDir\tests\", "").Replace("$PlaywrightDir/tests/", "")
                $safe = ($relPath -replace '[\\/:*?"<>|]','_') -replace '\s+','_'
                if ($doneFiles -contains $safe) {
                    $excludeSpecs += $spec
                }
            }
            Write-Host "  已完成（跳过）: $($excludeSpecs.Count) 个文件" -ForegroundColor Green
        }
    }
}

$pendingSpecs = @($allSpecs | Where-Object { $excludeSpecs -notcontains $_ })
$pendingCount = $pendingSpecs.Count
Write-Host "  待执行: $pendingCount 个文件" -ForegroundColor Yellow

if ($pendingCount -eq 0) {
    Write-Host "`n  ✅ 全部文件已完成，无需执行" -ForegroundColor Green
    exit 0
}

# ──── 步骤 2：构建执行参数 ────
$env:FULL_RUN = "1"  # 启用内存优化模式（JUnit+dot，禁用 trace/screenshot/video）
$env:NODE_OPTIONS = "--max-old-space-size=8192"  # 8GB 堆

$pwArgs = @("test")

# 如果 ResumeOnly 有排除文件，使用 --grep 或指定文件列表
if ($ResumeOnly -and $excludeSpecs.Count -gt 0 -and $pendingCount -lt $totalSpecs) {
    # 生成临时文件列表供 Playwright 使用
    $pendingRelPaths = @()
    foreach ($spec in $pendingSpecs) {
        $rel = $spec.Replace("$PlaywrightDir\tests\", "").Replace("\", "/")
        $pendingRelPaths += "tests/$rel"
    }
    # Playwright 支持直接传文件列表
    $pwArgs += $pendingRelPaths
}

$pwArgs += "--workers=$Workers"

if ($Project) {
    $pwArgs += "--project=$Project"
}

if ($MaxFailures -gt 0) {
    $pwArgs += "--max-failures=$MaxFailures"
}

if ($Shard) {
    $pwArgs += "--shard=$Shard"
}

# 使用 JUnit 报告器输出到统一目录
$pwArgs += "--reporter=junit,dot"

Write-Host ""
Write-Host "  Workers: $Workers" -ForegroundColor White
Write-Host "  Project: $(if($Project){"$Project"}else{"全部 7 个"})" -ForegroundColor White
Write-Host "  MaxFailures: $(if($MaxFailures -gt 0){"$MaxFailures"}else{"不限制"})" -ForegroundColor White
Write-Host "  报告器: JUnit + dot (FULL_RUN 模式)" -ForegroundColor White
Write-Host ""

# ──── 步骤 3：执行 ────
$startTime = Get-Date
Write-Host "  ⏱️  开始执行: $($startTime.ToString('HH:mm:ss'))" -ForegroundColor Cyan
Write-Host "  ─────────────────────────────────────────────" -ForegroundColor DarkGray

Push-Location $PlaywrightDir
try {
    # 直接调用 npx playwright，让 Playwright 原生处理并行
    $pwBin = "node_modules\.bin\playwright"
    if (-not (Test-Path $pwBin)) {
        $pwBin = "npx"
        $pwArgs = @("playwright") + $pwArgs
    }
    
    Write-Host "  命令: $pwBin $($pwArgs -join ' ')" -ForegroundColor DarkGray
    Write-Host ""
    
    & $pwBin @pwArgs 2>&1 | ForEach-Object {
        $line = $_.ToString()
        # 过滤关键输出: 进度、失败、完成
        if ($line -match '^\d+ passed|^\d+ failed|^\d+ skipped|Running \d+|Slow test') {
            Write-Host "  $line" -ForegroundColor $(if($line -match 'failed'){"Red"}else{"Green"})
        }
        elseif ($line -match '^\s*\d+ test') {
            Write-Host "  $line" -ForegroundColor Gray
        }
    }
    $exitCode = $LASTEXITCODE
}
finally {
    Pop-Location
}

$endTime = Get-Date
$elapsed = $endTime - $startTime
Write-Host ""
Write-Host "  ─────────────────────────────────────────────" -ForegroundColor DarkGray
Write-Host "  ⏱️  执行完成: $($endTime.ToString('HH:mm:ss')) (耗时 $($elapsed.ToString('hh\:mm\:ss')))" -ForegroundColor Cyan

# ──── 步骤 4：解析 JUnit XML 并拆分到原子化 JSON ────
if (-not $SkipAtomicSplit) {
    Write-Host "`n  📊 拆分 JUnit 结果到原子化 JSON..." -ForegroundColor Yellow
    
    $junitFile = "$PlaywrightDir\junit-results.xml"
    if (-not (Test-Path $junitFile)) {
        # 尝试 TestResults 目录
        $junitFile = $JunitXml
    }
    
    if (Test-Path $junitFile) {
        New-Item -Path $AtomicDir -ItemType Directory -Force | Out-Null
        
        try {
            [xml]$xml = Get-Content $junitFile -Encoding UTF8
            
            $suites = @()
            if ($xml.testsuites -and $xml.testsuites.testsuite) {
                $suites = @($xml.testsuites.testsuite)
            } elseif ($xml.testsuite) {
                $suites = @($xml.testsuite)
            }
            
            # 按 spec 文件名分组
            $fileResults = @{}
            foreach ($suite in $suites) {
                # Playwright JUnit 格式: testsuite name 包含文件路径
                $suiteName = $suite.name
                
                # 提取 spec 文件名
                $specFile = ""
                if ($suiteName -match '([^\\\/]+\.spec\.ts)') {
                    $specFile = $matches[1]
                } elseif ($suite.file -and $suite.file -match '([^\\\/]+\.spec\.ts)') {
                    $specFile = $matches[1]
                } else {
                    $specFile = $suiteName
                }
                
                if (-not $fileResults.ContainsKey($specFile)) {
                    $fileResults[$specFile] = @{ total=0; passed=0; failed=0; skipped=0; duration_s=0; details=@() }
                }
                
                $fr = $fileResults[$specFile]
                $sTotal = if ($null -ne $suite.tests) { [int]$suite.tests } else { 0 }
                $sFailed = if ($null -ne $suite.failures) { [int]$suite.failures } else { 0 }
                $sErrors = if ($null -ne $suite.errors) { [int]$suite.errors } else { 0 }
                $sSkipped = if ($null -ne $suite.skipped) { [int]$suite.skipped } else { 0 }
                $sDur = if ($null -ne $suite.time) { [double]$suite.time } else { 0 }
                
                $fr.total += $sTotal
                $fr.failed += ($sFailed + $sErrors)
                $fr.skipped += $sSkipped
                $fr.duration_s += $sDur
            }
            
            # 计算 passed
            foreach ($key in @($fileResults.Keys)) {
                $fr = $fileResults[$key]
                $fr.passed = $fr.total - $fr.failed - $fr.skipped
            }
            
            # 保存原子化 JSON
            $savedCount = 0
            $totalTests = 0
            $totalPassed = 0
            $totalFailed = 0
            
            foreach ($key in $fileResults.Keys) {
                $fr = $fileResults[$key]
                $safe = ($key -replace '[\\/:*?"<>|]','_') -replace '\s+','_'
                $jsonPath = Join-Path $AtomicDir "$safe.json"
                
                $atomicResult = [ordered]@{
                    file = $key
                    total = $fr.total
                    passed = $fr.passed
                    failed = $fr.failed
                    skipped = $fr.skipped
                    duration_s = [math]::Round($fr.duration_s, 2)
                    status = if ($fr.failed -gt 0) { "failed" } elseif ($fr.total -eq 0) { "pending" } else { "passed" }
                    timestamp = (Get-Date -Format "yyyy-MM-ddTHH:mm:ss")
                    details = @()
                }
                
                $atomicResult | ConvertTo-Json -Depth 5 | Set-Content $jsonPath -Encoding UTF8
                $savedCount++
                $totalTests += $fr.total
                $totalPassed += $fr.passed
                $totalFailed += $fr.failed
            }
            
            Write-Host "  ✅ 已拆分 $savedCount 个文件的结果到原子化 JSON" -ForegroundColor Green
            Write-Host "  📊 总计: $totalTests 用例, 通过: $totalPassed, 失败: $totalFailed" -ForegroundColor White
            
            # 同步到 playwright-outputs.json
            $outputsPath = "$RootDir\TestResults\playwright-outputs.json"
            if (Test-Path $outputsPath) {
                try {
                    $outputs = Get-Content $outputsPath -Raw -Encoding UTF8 | ConvertFrom-Json
                    $outputs.total = $totalTests
                    $outputs.passed = $totalPassed
                    $outputs.failed = $totalFailed
                    $outputs.skipped = ($fileResults.Values | ForEach-Object { $_.skipped } | Measure-Object -Sum).Sum
                    $outputs.fileCount = $savedCount
                    $outputs | ConvertTo-Json -Depth 5 | Set-Content $outputsPath -Encoding UTF8
                    Write-Host "  ✅ 已更新 playwright-outputs.json" -ForegroundColor Green
                } catch {
                    Write-Host "  ⚠️  更新 playwright-outputs.json 失败: $_" -ForegroundColor Yellow
                }
            }
            
        } catch {
            Write-Host "  ❌ 解析 JUnit XML 失败: $_" -ForegroundColor Red
        }
    } else {
        Write-Host "  ⚠️  未找到 JUnit XML: $junitFile" -ForegroundColor Yellow
    }
}

# ──── 步骤 5：汇总 ────
Write-Host ""
Write-Host "╔══════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║  Playwright 执行完成                                        ║" -ForegroundColor Cyan
Write-Host "╠══════════════════════════════════════════════════════════════╣" -ForegroundColor Cyan
Write-Host "║  耗时: $($elapsed.ToString('hh\:mm\:ss'))                                                    ║" -ForegroundColor White
Write-Host "║  Workers: $Workers                                                   ║" -ForegroundColor White
Write-Host "║  退出码: $exitCode                                                    ║" -ForegroundColor $(if($exitCode -eq 0){"Green"}else{"Red"})
Write-Host "╚══════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan

exit $exitCode
