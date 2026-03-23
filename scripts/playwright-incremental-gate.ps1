<#
.SYNOPSIS
    Playwright 增量测试门禁 - 基线保护 + 增量验证
.DESCRIPTION
    基于已锁定的基线，对代码变更进行增量测试门禁检查：
    
    1. 基线保护：确保已有基线测试不被破坏（回归验证）
    2. 增量检测：发现新增/修改/删除的测试文件
    3. 增量执行：自动执行新增和修改的测试
    4. 门禁判定：所有基线+增量测试必须通过才放行
    
    支持三种运行模式：
    - check   : 仅检查变更，不执行测试（快速预检）
    - changed : 仅执行变更相关的测试（增量门禁）
    - full    : 执行全部测试（发布前全量门禁）

.PARAMETER Mode
    运行模式：check | changed | full
.PARAMETER Project
    Playwright 浏览器项目名（默认 chromium）
.PARAMETER FailFast
    遇到失败立即停止（默认 false）
.PARAMETER AutoFix
    自动清理已删除文件的基线记录（默认 false）

.EXAMPLE
    # 增量门禁（推荐：提交前执行）
    .\playwright-incremental-gate.ps1 -Mode changed
    
    # 快速预检（仅看变更清单，不跑测试）
    .\playwright-incremental-gate.ps1 -Mode check
    
    # 发布前全量门禁
    .\playwright-incremental-gate.ps1 -Mode full
#>
param(
    [ValidateSet("check","changed","full")]
    [string]$Mode = "changed",
    
    [string]$Project = "chromium",
    [switch]$FailFast,
    [switch]$AutoFix
)

$ErrorActionPreference = "Continue"
$RootDir       = (Resolve-Path "$PSScriptRoot\..").Path
$PlaywrightDir = Join-Path $RootDir "testing\tests\playwright-tests"
$AtomicDir     = Join-Path $RootDir "TestResults\atomic\playwright"
$BaselineDir   = Join-Path $RootDir "TestResults\baseline"
$BaselineFile  = Join-Path $BaselineDir "playwright-baseline.json"
$GateReportDir = Join-Path $RootDir "TestResults\gate-reports"

New-Item -Path $GateReportDir -ItemType Directory -Force | Out-Null

function Write-Banner { param($msg, $color="Cyan")
    $line = "═" * 60
    Write-Host "`n╔$line╗" -ForegroundColor $color
    Write-Host "║  $($msg.PadRight(58))║" -ForegroundColor $color
    Write-Host "╚$line╝" -ForegroundColor $color
}

function Write-Gate { param($icon, $msg, $color="White")
    Write-Host "  $icon $msg" -ForegroundColor $color
}

# ═══════════════════════════════════════════════════════════════════════
# 加载基线
# ═══════════════════════════════════════════════════════════════════════
Write-Banner "Playwright 增量测试门禁 [$Mode]" "Yellow"

if (-not (Test-Path $BaselineFile)) {
    Write-Host "  ❌ 基线文件不存在: $BaselineFile" -ForegroundColor Red
    Write-Host "  ℹ️ 请先执行 run-playwright-baseline.ps1 建立基线" -ForegroundColor Gray
    exit 1
}

$baseline = Get-Content $BaselineFile -Raw | ConvertFrom-Json
Write-Gate "📋" "基线版本: $($baseline.version) | 锁定时间: $($baseline.lockedAt)" "Cyan"
Write-Gate "📊" "基线文件: $($baseline.totalFiles) | 用例: $($baseline.totalTests) | 通过: $($baseline.totalPassed)" "Cyan"

# 构建基线文件索引
$baselineIndex = @{}
foreach ($entry in $baseline.entries) {
    $key = if ($entry.file) { Split-Path $entry.file -Leaf } else { "" }
    if ($key) { $baselineIndex[$key] = $entry }
}

# ═══════════════════════════════════════════════════════════════════════
# 检测变更
# ═══════════════════════════════════════════════════════════════════════
Write-Gate "🔍" "检测测试文件变更..." "Yellow"

$currentFiles = Get-ChildItem (Join-Path $PlaywrightDir "tests") -Filter "*.spec.ts" -Recurse -ErrorAction SilentlyContinue
$currentIndex = @{}
foreach ($f in $currentFiles) { $currentIndex[$f.Name] = $f }

# 分类变更
$newFiles      = @()  # 基线中不存在的新文件
$modifiedFiles = @()  # 存在但内容已变更
$deletedFiles  = @()  # 基线中有但当前不存在
$unchangedFiles = @() # 未变更

foreach ($f in $currentFiles) {
    if (-not $baselineIndex.ContainsKey($f.Name)) {
        $newFiles += $f
    } else {
        $baseEntry = $baselineIndex[$f.Name]
        # 计算当前文件 hash 与基线对比
        $currentHash = (Get-FileHash $f.FullName -ErrorAction SilentlyContinue).Hash
        if ($baseEntry.hash -and $currentHash -ne $baseEntry.hash) {
            $modifiedFiles += $f
        } else {
            $unchangedFiles += $f
        }
    }
}

foreach ($key in $baselineIndex.Keys) {
    if (-not $currentIndex.ContainsKey($key)) {
        $deletedFiles += $key
    }
}

# ═══════════════════════════════════════════════════════════════════════
# 变更报告
# ═══════════════════════════════════════════════════════════════════════
Write-Host ""
Write-Gate "📊" "变更检测结果:" "Cyan"
Write-Gate "  🆕" "新增: $($newFiles.Count) 个文件" $(if ($newFiles.Count -gt 0) { "Green" } else { "Gray" })
Write-Gate "  ✏️" "修改: $($modifiedFiles.Count) 个文件" $(if ($modifiedFiles.Count -gt 0) { "Yellow" } else { "Gray" })
Write-Gate "  🗑️" "删除: $($deletedFiles.Count) 个文件" $(if ($deletedFiles.Count -gt 0) { "Red" } else { "Gray" })
Write-Gate "  ✅" "未变更: $($unchangedFiles.Count) 个文件" "Gray"

if ($newFiles.Count -gt 0) {
    Write-Host "  新增文件:" -ForegroundColor Green
    foreach ($f in $newFiles | Select-Object -First 20) {
        Write-Host "    + $($f.Name)" -ForegroundColor Green
    }
    if ($newFiles.Count -gt 20) { Write-Host "    ... 及其余 $($newFiles.Count - 20) 个" -ForegroundColor Green }
}

if ($modifiedFiles.Count -gt 0) {
    Write-Host "  修改文件:" -ForegroundColor Yellow
    foreach ($f in $modifiedFiles | Select-Object -First 20) {
        Write-Host "    ~ $($f.Name)" -ForegroundColor Yellow
    }
}

if ($deletedFiles.Count -gt 0) {
    Write-Host "  删除文件:" -ForegroundColor Red
    foreach ($f in $deletedFiles | Select-Object -First 10) {
        Write-Host "    - $f" -ForegroundColor Red
    }
}

if ($Mode -eq "check") {
    Write-Banner "预检完成（未执行测试）" "Green"
    
    # 生成预检报告
    $checkReport = [ordered]@{
        mode       = "check"
        timestamp  = (Get-Date -Format "yyyy-MM-ddTHH:mm:ss")
        baseline   = [ordered]@{ version=$baseline.version; files=$baseline.totalFiles; tests=$baseline.totalTests }
        changes    = [ordered]@{ new=$newFiles.Count; modified=$modifiedFiles.Count; deleted=$deletedFiles.Count; unchanged=$unchangedFiles.Count }
        verdict    = if ($newFiles.Count -eq 0 -and $modifiedFiles.Count -eq 0 -and $deletedFiles.Count -eq 0) { "NO_CHANGES" } else { "CHANGES_DETECTED" }
    }
    $checkReport | ConvertTo-Json -Depth 5 | Out-File (Join-Path $GateReportDir "playwright-gate-check.json") -Encoding utf8 -Force
    exit 0
}

# ═══════════════════════════════════════════════════════════════════════
# 确定执行范围
# ═══════════════════════════════════════════════════════════════════════
$execFiles = @()

switch ($Mode) {
    "changed" {
        # 增量模式：仅执行新增+修改的文件
        $execFiles = $newFiles + $modifiedFiles
        if ($execFiles.Count -eq 0) {
            Write-Gate "✅" "无变更文件需要测试" "Green"
        }
    }
    "full" {
        # 全量模式：执行所有文件
        $execFiles = @($currentFiles)
    }
}

# ═══════════════════════════════════════════════════════════════════════
# 处理删除文件
# ═══════════════════════════════════════════════════════════════════════
if ($deletedFiles.Count -gt 0) {
    if ($AutoFix) {
        Write-Gate "🔧" "自动清理已删除文件的原子结果..." "Yellow"
        foreach ($df in $deletedFiles) {
            $atomicPath = Join-Path $AtomicDir "$df.json"
            if (Test-Path $atomicPath) {
                Remove-Item $atomicPath -Force
                Write-Host "    移除: $df.json" -ForegroundColor DarkGray
            }
        }
    } else {
        Write-Gate "⚠️" "检测到已删除的基线文件，建议使用 -AutoFix 清理，或手动更新基线" "Yellow"
    }
}

# ═══════════════════════════════════════════════════════════════════════
# 执行测试
# ═══════════════════════════════════════════════════════════════════════
$gateResults = @()
$gatePassed  = $true
$testsPassed = 0
$testsFailed = 0
$testsTotal  = 0

if ($execFiles.Count -gt 0) {
    Write-Banner "执行测试 ($($execFiles.Count) 个文件)" "Green"
    
    Set-Location $PlaywrightDir
    $env:FULL_RUN = "1"
    $idx = 0
    
    foreach ($f in $execFiles) {
        $idx++
        $relPath = $f.FullName -replace [regex]::Escape("$PlaywrightDir\"), ""
        $relPath = $relPath -replace "\\", "/"
        $resultPath = Join-Path $AtomicDir "$($f.Name).json"
        
        Write-Host "  ⏳ [$idx/$($execFiles.Count)] $($f.Name)" -ForegroundColor DarkYellow -NoNewline
        
        $sw = [System.Diagnostics.Stopwatch]::StartNew()
        $output = & node_modules\.bin\playwright test $relPath --project=$Project --reporter=line 2>&1
        $exitCode = $LASTEXITCODE
        $sw.Stop()
        
        $outputText = $output -join "`n"
        $passed = 0; $failed = 0; $skipped = 0
        if ($outputText -match "(\d+)\s+passed")  { $passed  = [int]$Matches[1] }
        if ($outputText -match "(\d+)\s+failed")  { $failed  = [int]$Matches[1] }
        if ($outputText -match "(\d+)\s+skipped") { $skipped = [int]$Matches[1] }
        $total = $passed + $failed + $skipped
        
        $status = if ($failed -gt 0) { "FAIL" } elseif ($passed -gt 0) { "PASS" } else { "ERROR" }
        
        # 保存原子结果
        if ($total -gt 0) {
            [ordered]@{
                file=$relPath; tool="playwright"; project=$Project
                status=($status.ToLower()); total=$total; passed=$passed; failed=$failed; skipped=$skipped
                duration_s=[math]::Round($sw.Elapsed.TotalSeconds,1)
                timestamp=(Get-Date -Format "yyyy-MM-ddTHH:mm:ss")
            } | ConvertTo-Json | Out-File $resultPath -Encoding utf8 -Force
        }
        
        $gateResults += [ordered]@{
            file=$f.Name; status=$status; total=$total; passed=$passed; failed=$failed
            changeType=if($newFiles -contains $f){"NEW"}elseif($modifiedFiles -contains $f){"MODIFIED"}else{"BASELINE"}
        }
        
        $testsTotal  += $total
        $testsPassed += $passed
        $testsFailed += $failed
        
        if ($failed -gt 0) {
            $gatePassed = $false
            Write-Host " ❌ $failed/$total 失败" -ForegroundColor Red
            if ($FailFast) {
                Write-Host "  ⛔ FailFast：检测到失败，停止执行" -ForegroundColor Red
                break
            }
        } else {
            Write-Host " ✅ $passed/$total 通过 ($([math]::Round($sw.Elapsed.TotalSeconds,1))s)" -ForegroundColor Green
        }
    }
}

# ═══════════════════════════════════════════════════════════════════════
# 基线完整性检查（changed 模式下也验证未变更文件的原子结果存在）
# ═══════════════════════════════════════════════════════════════════════
if ($Mode -eq "changed") {
    Write-Host ""
    Write-Gate "🔒" "基线完整性验证（检查未变更文件的原子结果）..." "Cyan"
    
    $missingBaseline = 0
    $brokenBaseline  = 0
    
    foreach ($f in $unchangedFiles) {
        $resultPath = Join-Path $AtomicDir "$($f.Name).json"
        if (-not (Test-Path $resultPath)) {
            $missingBaseline++
            if ($missingBaseline -le 5) {
                Write-Host "    ⚠️ 缺失原子结果: $($f.Name)" -ForegroundColor Yellow
            }
        } else {
            $c = Get-Content $resultPath -Raw | ConvertFrom-Json
            if ([int]$c.failed -gt 0) {
                $brokenBaseline++
                if ($brokenBaseline -le 5) {
                    Write-Host "    ❌ 基线失败: $($f.Name) (failed=$($c.failed))" -ForegroundColor Red
                }
            }
        }
    }
    
    if ($missingBaseline -gt 5) {
        Write-Host "    ... 及其余 $($missingBaseline - 5) 个缺失" -ForegroundColor Yellow
    }
    if ($brokenBaseline -gt 0) {
        $gatePassed = $false
        Write-Gate "❌" "基线中有 $brokenBaseline 个文件失败！需要回归修复。" "Red"
    }
    if ($missingBaseline -gt 0) {
        Write-Gate "⚠️" "基线中有 $missingBaseline 个文件缺失原子结果，建议执行 full 模式补齐" "Yellow"
    }
    if ($missingBaseline -eq 0 -and $brokenBaseline -eq 0) {
        Write-Gate "✅" "基线完整性验证通过（$($unchangedFiles.Count) 个文件）" "Green"
    }
}

# ═══════════════════════════════════════════════════════════════════════
# 门禁判定
# ═══════════════════════════════════════════════════════════════════════
Write-Host ""
$gateVerdict = if ($gatePassed -and $testsFailed -eq 0) { "PASS" } else { "FAIL" }
$verdictColor = if ($gateVerdict -eq "PASS") { "Green" } else { "Red" }
$verdictIcon  = if ($gateVerdict -eq "PASS") { "✅" } else { "❌" }

Write-Banner "门禁结果: $verdictIcon $gateVerdict" $verdictColor

$reportLines = @()
$reportLines += "# Playwright 增量测试门禁报告"
$reportLines += ""
$reportLines += "- **模式**: $Mode"
$reportLines += "- **时间**: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')"
$reportLines += "- **基线版本**: $($baseline.version) (锁定于 $($baseline.lockedAt))"
$reportLines += "- **判定**: **$gateVerdict**"
$reportLines += ""
$reportLines += "## 变更概览"
$reportLines += ""
$reportLines += "| 类型 | 数量 |"
$reportLines += "|------|------|"
$reportLines += "| 🆕 新增 | $($newFiles.Count) |"
$reportLines += "| ✏️ 修改 | $($modifiedFiles.Count) |"
$reportLines += "| 🗑️ 删除 | $($deletedFiles.Count) |"
$reportLines += "| ✅ 未变更 | $($unchangedFiles.Count) |"
$reportLines += ""
$reportLines += "## 执行结果"
$reportLines += ""
$reportLines += "| 指标 | 值 |"
$reportLines += "|------|-----|"
$reportLines += "| 执行文件 | $($execFiles.Count) |"
$reportLines += "| 用例总数 | $testsTotal |"
$reportLines += "| 通过 | $testsPassed |"
$reportLines += "| 失败 | $testsFailed |"
$reportLines += ""

if ($gateResults.Count -gt 0) {
    $reportLines += "## 文件详情"
    $reportLines += ""
    $reportLines += "| 文件 | 变更类型 | 状态 | 通过/总数 |"
    $reportLines += "|------|---------|------|----------|"
    foreach ($gr in $gateResults) {
        $icon = if ($gr.status -eq "PASS") { "✅" } else { "❌" }
        $reportLines += "| $($gr.file) | $($gr.changeType) | $icon $($gr.status) | $($gr.passed)/$($gr.total) |"
    }
}

$reportPath = Join-Path $GateReportDir "playwright-incremental-gate.md"
$reportLines -join "`n" | Out-File $reportPath -Encoding utf8 -Force

# JSON 报告（供 CI/CD 读取）
$jsonReport = [ordered]@{
    tool        = "playwright"
    mode        = $Mode
    verdict     = $gateVerdict
    timestamp   = (Get-Date -Format "yyyy-MM-ddTHH:mm:ss")
    baseline    = [ordered]@{ version=$baseline.version; files=$baseline.totalFiles; tests=$baseline.totalTests }
    changes     = [ordered]@{ new=$newFiles.Count; modified=$modifiedFiles.Count; deleted=$deletedFiles.Count; unchanged=$unchangedFiles.Count }
    execution   = [ordered]@{ files=$execFiles.Count; total=$testsTotal; passed=$testsPassed; failed=$testsFailed }
    gateResults = $gateResults
}
$jsonReport | ConvertTo-Json -Depth 10 | Out-File (Join-Path $GateReportDir "playwright-incremental-gate.json") -Encoding utf8 -Force

Write-Host "  报告: $reportPath" -ForegroundColor Gray
Write-Host ""

if ($gateVerdict -eq "FAIL") {
    exit 1
} else {
    exit 0
}
