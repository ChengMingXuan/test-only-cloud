<#
.SYNOPSIS
    Playwright 基线全量执行脚本 - 清除 batch-estimate 占位，逐文件真实执行
.DESCRIPTION
    解决问题：204个文件因并行批次失败产生 batch-estimate 占位（total=0），
    导致实际执行率仅20%（2141/10708）。
    
    本脚本：
    1. 清除所有 batch-estimate 占位结果
    2. 逐文件使用 --project=chromium 执行（避免 WebKit/移动端在 Windows 上的 skip）
    3. 保存精确原子化结果到 TestResults/atomic/playwright/
    4. 执行完成后锁定基线快照
    5. 生成基线报告

    预计用时：~204文件 × ~40s/文件 ≈ ~2.5小时（chromium 单浏览器）

.PARAMETER ClearEstimates
    是否清除 batch-estimate 结果（默认 true）
.PARAMETER Project
    Playwright 浏览器项目名（默认 chromium）
.PARAMETER MaxConcurrent
    如果大于1，使用多进程并发（每进程用不同端口的 Mock Server）
.PARAMETER ResumeOnly
    仅执行尚未有真实结果的文件（跳过已通过的）
.PARAMETER MaxFiles
    最多执行文件数（0=全部）
.PARAMETER LockBaseline
    执行完成后是否锁定基线（默认 true）

.EXAMPLE
    # 全量基线执行（清除估算→逐文件执行→锁定基线）
    .\run-playwright-baseline.ps1
    
    # 仅执行未通过的文件（恢复模式）
    .\run-playwright-baseline.ps1 -ResumeOnly
    
    # 快速验证前5个文件
    .\run-playwright-baseline.ps1 -MaxFiles 5
#>
param(
    [switch]$ClearEstimates = $true,
    [string]$Project = "chromium",
    [switch]$ResumeOnly,
    [int]$MaxFiles = 0,
    [switch]$LockBaseline = $true,
    [switch]$SkipReport
)

$ErrorActionPreference = "Continue"
$RootDir       = (Resolve-Path "$PSScriptRoot\..").Path
$PlaywrightDir = Join-Path $RootDir "testing\tests\playwright-tests"
$AtomicDir     = Join-Path $RootDir "TestResults\atomic\playwright"
$ControlDir    = Join-Path $RootDir "TestResults\control"
$BaselineDir   = Join-Path $RootDir "TestResults\baseline"
$LogFile       = Join-Path $RootDir "TestResults\playwright-baseline-run.log"

foreach ($d in @($AtomicDir, $ControlDir, $BaselineDir)) {
    New-Item -Path $d -ItemType Directory -Force | Out-Null
}

function Write-Banner { param($msg, $color="Cyan")
    $line = "═" * 60
    Write-Host "`n╔$line╗" -ForegroundColor $color
    Write-Host "║  $($msg.PadRight(58))║" -ForegroundColor $color
    Write-Host "╚$line╝" -ForegroundColor $color
}

function Write-Log { param($msg)
    $ts = Get-Date -Format "HH:mm:ss"
    $line = "[$ts] $msg"
    Write-Host $line
    $line | Out-File $LogFile -Append -Encoding utf8
}

# ═══════════════════════════════════════════════════════════════════════
# 阶段一：清除 batch-estimate 占位结果
# ═══════════════════════════════════════════════════════════════════════
Write-Banner "Playwright 基线全量执行" "Yellow"
Write-Log "开始时间: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')"
Write-Log "浏览器项目: $Project"

if ($ClearEstimates) {
    Write-Log "阶段一：清除 batch-estimate 占位结果..."
    $cleared = 0
    Get-ChildItem $AtomicDir -Filter "*.json" -ErrorAction SilentlyContinue | ForEach-Object {
        try {
            $content = Get-Content $_.FullName -Raw | ConvertFrom-Json
            if ($content.source -eq "batch-estimate") {
                Remove-Item $_.FullName -Force
                $cleared++
            }
        } catch {}
    }
    Write-Log "已清除 $cleared 个 batch-estimate 占位文件"
}

# ═══════════════════════════════════════════════════════════════════════
# 阶段二：发现待执行文件
# ═══════════════════════════════════════════════════════════════════════
Write-Log "阶段二：发现测试文件..."

$allTests = Get-ChildItem (Join-Path $PlaywrightDir "tests") -Filter "*.spec.ts" -Recurse -ErrorAction SilentlyContinue | Sort-Object Name

Write-Log "发现测试文件: $($allTests.Count) 个"

# 确定待执行列表
$pendingTests = @()
$alreadyDone  = @()

foreach ($test in $allTests) {
    $resultPath = Join-Path $AtomicDir "$($test.Name).json"
    if (Test-Path $resultPath) {
        $existing = Get-Content $resultPath -Raw | ConvertFrom-Json
        if ([int]$existing.total -gt 0 -and [int]$existing.failed -eq 0 -and $existing.source -ne "batch-estimate") {
            $alreadyDone += $test
            continue
        }
    }
    $pendingTests += $test
}

Write-Log "已有真实通过结果: $($alreadyDone.Count) 个文件"
Write-Log "待执行: $($pendingTests.Count) 个文件"

if ($ResumeOnly) {
    Write-Log "ResumeOnly 模式：仅执行待处理文件"
    $execList = $pendingTests
} else {
    # 全量模式：优先执行待处理，再重新验证已通过
    $execList = $pendingTests + $alreadyDone
}

if ($MaxFiles -gt 0 -and $execList.Count -gt $MaxFiles) {
    $execList = $execList | Select-Object -First $MaxFiles
    Write-Log "MaxFiles 限制：截取前 $MaxFiles 个文件"
}

if ($execList.Count -eq 0) {
    Write-Log "无待执行文件，所有文件已通过！"
    if (-not $SkipReport) {
        Write-Log "生成报告..."
        & "$PSScriptRoot\generate-tool-reports.ps1" -Tool playwright
    }
    exit 0
}

# ═══════════════════════════════════════════════════════════════════════
# 阶段三：逐文件执行
# ═══════════════════════════════════════════════════════════════════════
Write-Banner "逐文件执行 ($($execList.Count) 个文件)" "Green"

$totalCount   = $execList.Count
$passedCount  = 0
$failedCount  = 0
$totalTests   = 0
$totalPassed  = 0
$totalFailed  = 0
$totalSkipped = 0
$idx = 0
$startAll = Get-Date

Set-Location $PlaywrightDir

# 设置 FULL_RUN 以使用精简报告器配置
$env:FULL_RUN = "1"

foreach ($test in $execList) {
    $idx++
    $pct = [math]::Round($idx * 100 / $totalCount, 0)
    $relativePath = $test.FullName -replace [regex]::Escape("$PlaywrightDir\"), ""
    $relativePath = $relativePath -replace "\\", "/"
    $resultPath   = Join-Path $AtomicDir "$($test.Name).json"

    $elapsed = [math]::Round(((Get-Date) - $startAll).TotalMinutes, 1)
    Write-Host "  ⏳ [$idx/$totalCount]($pct%) $($test.Name) [已用 ${elapsed}m]" -ForegroundColor DarkYellow -NoNewline

    $sw = [System.Diagnostics.Stopwatch]::StartNew()

    try {
        # 使用 JUnit 报告器获取精确结果
        $junitXml = Join-Path $AtomicDir "$($test.Name).xml"
        $output = & node_modules\.bin\playwright test $relativePath --project=$Project --reporter=junit 2>&1
        $exitCode = $LASTEXITCODE
        $sw.Stop()
        $duration = $sw.Elapsed.TotalSeconds

        # 将 JUnit XML 从 playwright 默认位置复制出来
        $pwJunit = Join-Path $PlaywrightDir "junit-results.xml"
        if (Test-Path $pwJunit) {
            Copy-Item $pwJunit $junitXml -Force
        }

        # 解析 JUnit XML
        $passed  = 0
        $failed  = 0
        $skipped = 0
        $total   = 0

        if (Test-Path $junitXml) {
            try {
                [xml]$xml = Get-Content $junitXml -Raw -Encoding UTF8
                foreach ($suite in $xml.SelectNodes("//testsuite")) {
                    $total   += [int]$suite.GetAttribute("tests")
                    $failed  += [int]$suite.GetAttribute("failures")
                    $skipped += [int]$suite.GetAttribute("skipped")
                    if ($suite.GetAttribute("errors")) { $failed += [int]$suite.GetAttribute("errors") }
                }
                $passed = $total - $failed - $skipped
            } catch {
                # JUnit XML 解析失败，回退到 stdout 正则
                $outputText = $output -join "`n"
                if ($outputText -match "(\d+)\s+passed")  { $passed  = [int]$Matches[1] }
                if ($outputText -match "(\d+)\s+failed")  { $failed  = [int]$Matches[1] }
                if ($outputText -match "(\d+)\s+skipped") { $skipped = [int]$Matches[1] }
                $total = $passed + $failed + $skipped
            }
            Remove-Item $junitXml -Force -ErrorAction SilentlyContinue
        } else {
            # 无 JUnit XML，从 stdout 解析
            $outputText = $output -join "`n"
            if ($outputText -match "(\d+)\s+passed")  { $passed  = [int]$Matches[1] }
            if ($outputText -match "(\d+)\s+failed")  { $failed  = [int]$Matches[1] }
            if ($outputText -match "(\d+)\s+skipped") { $skipped = [int]$Matches[1] }
            $total = $passed + $failed + $skipped
        }

        # 保存原子化结果
        $status = if ($failed -gt 0) { "failed" } 
                  elseif ($passed -gt 0) { "passed" }
                  elseif ($total -eq 0) { "error" }
                  else { "skipped" }

        $atomicResult = [ordered]@{
            file       = $relativePath
            tool       = "playwright"
            project    = $Project
            status     = $status
            total      = $total
            passed     = $passed
            failed     = $failed
            skipped    = $skipped
            duration_s = [math]::Round($duration, 1)
            timestamp  = (Get-Date -Format "yyyy-MM-ddTHH:mm:ss")
            exitCode   = $exitCode
        }

        if ($total -gt 0) {
            $atomicResult | ConvertTo-Json -Depth 5 | Out-File $resultPath -Encoding utf8 -Force
        } else {
            # total=0 不写入，避免阻止后续重跑
            Write-Host "" # 换行
            Write-Log "  ⚠️ [$idx] $($test.Name): 无测试运行 (exit=$exitCode) — 不写入"
            $failedCount++
            continue
        }

        $totalTests   += $total
        $totalPassed  += $passed
        $totalFailed  += $failed
        $totalSkipped += $skipped

        if ($failed -eq 0 -and $passed -gt 0) {
            $passedCount++
            Write-Host " ✅ $passed/$total 通过 ($([math]::Round($duration,1))s)" -ForegroundColor Green
        } else {
            $failedCount++
            Write-Host " ❌ $failed/$total 失败 ($([math]::Round($duration,1))s)" -ForegroundColor Red
        }

    } catch {
        $sw.Stop()
        $failedCount++
        Write-Host " ❌ 异常: $_" -ForegroundColor Red
        Write-Log "  ❌ [$idx] $($test.Name): 执行异常 - $_"
    }

    # 进度摘要（每20个文件输出一次）
    if ($idx % 20 -eq 0) {
        $rate = [math]::Round($idx / ((Get-Date) - $startAll).TotalMinutes, 1)
        $eta  = if ($rate -gt 0) { [math]::Round(($totalCount - $idx) / $rate, 0) } else { "?" }
        Write-Log "  📊 进度: 文件 $idx/$totalCount | 用例 $totalPassed/$totalTests | 速率 ${rate}文件/分 | 预计剩余 ${eta}分"
    }
}

$totalElapsed = [math]::Round(((Get-Date) - $startAll).TotalMinutes, 1)

# ═══════════════════════════════════════════════════════════════════════
# 阶段四：汇总与输出
# ═══════════════════════════════════════════════════════════════════════
Write-Banner "基线执行完成" "Green"

# 重新统计所有原子结果
$allAtomicFiles = Get-ChildItem $AtomicDir -Filter "*.json" -ErrorAction SilentlyContinue
$grandTotal   = 0
$grandPassed  = 0
$grandFailed  = 0
$grandSkipped = 0
$filesPassed  = 0
$filesFailed  = 0

foreach ($af in $allAtomicFiles) {
    try {
        $c = Get-Content $af.FullName -Raw | ConvertFrom-Json
        if ([int]$c.total -gt 0) {
            $grandTotal   += [int]$c.total
            $grandPassed  += [int]$c.passed
            $grandFailed  += [int]$c.failed
            $grandSkipped += [int]$c.skipped
            if ([int]$c.failed -eq 0) { $filesPassed++ } else { $filesFailed++ }
        }
    } catch {}
}

$summary = @"
╔══════════════════════════════════════════════════════════════╗
║  Playwright 基线执行总结                                      ║
╠══════════════════════════════════════════════════════════════╣
║  文件总数:  $($allTests.Count)                                 ║
║  有结果:    $($filesPassed + $filesFailed)                      ║
║  文件通过:  $filesPassed  | 文件失败:  $filesFailed              ║
╠══════════════════════════════════════════════════════════════╣
║  用例总数:  $grandTotal                                        ║
║  通过:      $grandPassed                                       ║
║  失败:      $grandFailed                                       ║
║  跳过:      $grandSkipped                                      ║
║  通过率:    $([math]::Round($grandPassed * 100 / [math]::Max($grandTotal,1), 1))%    ║
╠══════════════════════════════════════════════════════════════╣
║  总耗时:    ${totalElapsed} 分钟                                ║
╚══════════════════════════════════════════════════════════════╝
"@

Write-Host $summary -ForegroundColor Cyan
$summary | Out-File $LogFile -Append -Encoding utf8

# ═══════════════════════════════════════════════════════════════════════
# 阶段五：锁定基线
# ═══════════════════════════════════════════════════════════════════════
if ($LockBaseline -and $grandFailed -eq 0 -and $grandTotal -gt 0) {
    Write-Log "阶段五：锁定基线快照..."
    
    $baselineFile = Join-Path $BaselineDir "playwright-baseline.json"
    
    # 收集每个文件的基线数据
    $baselineEntries = @()
    foreach ($af in $allAtomicFiles) {
        try {
            $c = Get-Content $af.FullName -Raw | ConvertFrom-Json
            if ([int]$c.total -gt 0) {
                # 计算源文件 hash（PowerShell 5.1 兼容）
                $filePath = if ($c.file) { $c.file } else { ($af.BaseName -replace '\.spec\.ts$','') + ".spec.ts" }
                $specFile = Get-ChildItem $PlaywrightDir -Filter (Split-Path $filePath -Leaf) -Recurse -ErrorAction SilentlyContinue | Select-Object -First 1
                $fileHash = if ($specFile) { (Get-FileHash $specFile.FullName -ErrorAction SilentlyContinue).Hash } else { "" }
                
                $baselineEntries += [ordered]@{
                    file     = $c.file
                    total    = [int]$c.total
                    passed   = [int]$c.passed
                    skipped  = [int]$c.skipped
                    hash     = $fileHash
                }
            }
        } catch {}
    }

    $baseline = [ordered]@{
        version      = "1.0"
        lockedAt     = (Get-Date -Format "yyyy-MM-ddTHH:mm:ss")
        project      = $Project
        totalFiles   = $baselineEntries.Count
        totalTests   = $grandTotal
        totalPassed  = $grandPassed
        totalSkipped = $grandSkipped
        entries      = $baselineEntries
    }

    $baseline | ConvertTo-Json -Depth 10 | Out-File $baselineFile -Encoding utf8 -Force
    Write-Log "✅ 基线已锁定: $baselineFile"
    Write-Log "   文件数: $($baselineEntries.Count) | 用例数: $grandTotal | 通过: $grandPassed"
} elseif ($grandFailed -gt 0) {
    Write-Log "⚠️ 存在失败用例（$grandFailed 个），基线未锁定。请修复后重新执行。"
}

# 阶段六：生成报告
if (-not $SkipReport) {
    Write-Log "阶段六：生成 Playwright 独立报告..."
    & "$PSScriptRoot\generate-tool-reports.ps1" -Tool playwright
}

Write-Log "完成时间: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')"
Write-Log "总耗时: ${totalElapsed} 分钟"
Set-Location $RootDir
