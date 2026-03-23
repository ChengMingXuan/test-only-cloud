<#
.SYNOPSIS
    精准重跑失败用例 - 只重跑上次跑挂的，不重跑整个 Suite
.DESCRIPTION
    从上次并行执行的日志中提取失败用例，仅重跑这些用例：
    - pytest:     --lf (last-failed) 自动重跑上次失败
    - Playwright: --last-failed 重跑失败
    - Cypress:    --spec 指定失败文件重跑
    - Selenium:   --lf 重跑失败
    - Puppeteer:  全量重跑（无精准重跑能力）
    - K6:         重跑失败场景

    典型场景：全量并行跑完后，有 3 个工具失败，执行此脚本只重跑那 3 个工具的失败用例
.PARAMETER Tools
    指定要重跑的工具，逗号分隔。留空则自动检测失败工具
.PARAMETER Verbose
    显示详细重跑日志
.EXAMPLE
    .\rerun-failed-tests.ps1                          # 自动检测并重跑所有失败
    .\rerun-failed-tests.ps1 -Tools pytest,playwright  # 只重跑指定工具
#>
param(
    [string]$Tools = "",
    [switch]$VerboseOutput
)

$ErrorActionPreference = "Continue"
$RootDir = (Resolve-Path "$PSScriptRoot\..").Path
$ResultsDir = Join-Path $RootDir "TestResults"
$FailuresDir = Join-Path $ResultsDir "failures"

# 加载测试环境变量
$envScript = Join-Path $RootDir "testing\tests\set-test-env.ps1"
if (Test-Path $envScript) { . $envScript }

function Write-Banner { param($msg) Write-Host "`n══ $msg ══`n" -ForegroundColor Cyan }
function Write-OK { param($msg) Write-Host "  ✅ $msg" -ForegroundColor Green }
function Write-Fail { param($msg) Write-Host "  ❌ $msg" -ForegroundColor Red }
function Write-Info { param($msg) Write-Host "  ℹ️ $msg" -ForegroundColor Gray }

# ═══════════════════════════════════════════════
# 检测哪些工具上次失败了
# ═══════════════════════════════════════════════
function Get-FailedTools {
    $failed = @()
    $allTools = @("pytest", "cypress", "playwright", "selenium", "puppeteer", "k6")

    foreach ($tool in $allTools) {
        $logFile = Join-Path $ResultsDir "$tool-output.log"
        if (-not (Test-Path $logFile)) { continue }

        $content = Get-Content $logFile -Raw -Encoding UTF8 -ErrorAction SilentlyContinue
        if (-not $content) { continue }

        # 通过关键词判断是否有失败
        $hasFail = switch ($tool) {
            "pytest"     { $content -match "FAILED|ERROR|failed" }
            "cypress"    { $content -match "failing|✗|×|CypressError" }
            "playwright" { $content -match "failed|✘|Error:" }
            "selenium"   { $content -match "FAILED|ERROR" }
            "puppeteer"  { $content -match "FAIL|✕|Error" }
            "k6"         { $content -match "✗|thresholds.*crossed" }
        }

        if ($hasFail) {
            $failed += $tool
        }
    }

    return $failed
}

# ═══════════════════════════════════════════════
# 各工具的精准重跑命令
# ═══════════════════════════════════════════════
function Rerun-Tool {
    param([string]$Name)

    $startTime = Get-Date
    $exitCode = 0

    switch ($Name) {
        "pytest" {
            Write-Info "pytest: 使用 --lf 仅重跑上次失败的用例"
            Push-Location "$RootDir\tests"
            try {
                & "$RootDir\.venv\Scripts\python.exe" -m pytest --lf -v --tb=long --timeout=60 2>&1 | Tee-Object -FilePath "$ResultsDir\pytest-rerun.log"
                $exitCode = $LASTEXITCODE
            } finally { Pop-Location }
        }
        "cypress" {
            Write-Info "Cypress: 重跑失败的 spec 文件"
            # 从日志提取失败的 spec 文件
            $logFile = Join-Path $ResultsDir "cypress-output.log"
            $failedSpecs = @()
            if (Test-Path $logFile) {
                $content = Get-Content $logFile -Encoding UTF8
                $failedSpecs = $content | Where-Object { $_ -match "Spec.*│.*✖|Running:.*\.cy\." } |
                    ForEach-Object { if ($_ -match "([\w\-/]+\.cy\.\w+)") { $Matches[1] } } |
                    Select-Object -Unique
            }

            Push-Location "$RootDir\testing\tests\cypress-tests"
            try {
                if ($failedSpecs.Count -gt 0) {
                    foreach ($spec in $failedSpecs) {
                        Write-Info "  重跑: $spec"
                        npx cypress run --spec "cypress/e2e/$spec" 2>&1 | Tee-Object -Append -FilePath "$ResultsDir\cypress-rerun.log"
                    }
                } else {
                    Write-Info "  无法精确定位失败文件，重跑全量"
                    npx cypress run 2>&1 | Tee-Object -FilePath "$ResultsDir\cypress-rerun.log"
                }
                $exitCode = $LASTEXITCODE
            } finally { Pop-Location }
        }
        "playwright" {
            Write-Info "Playwright: 使用 --last-failed 仅重跑失败"
            Push-Location "$RootDir\testing\tests\playwright-tests"
            try {
                npx playwright test --last-failed --reporter=list 2>&1 | Tee-Object -FilePath "$ResultsDir\playwright-rerun.log"
                $exitCode = $LASTEXITCODE
            } finally { Pop-Location }
        }
        "selenium" {
            Write-Info "Selenium: 使用 --lf 仅重跑上次失败"
            Push-Location "$RootDir\testing\tests\selenium-tests"
            try {
                & "$RootDir\.venv\Scripts\python.exe" -m pytest --lf -v --tb=long --timeout=120 2>&1 | Tee-Object -FilePath "$ResultsDir\selenium-rerun.log"
                $exitCode = $LASTEXITCODE
            } finally { Pop-Location }
        }
        "puppeteer" {
            Write-Info "Puppeteer: 无精准重跑能力，重跑全量"
            Push-Location "$RootDir\testing\tests\puppeteer-tests"
            try {
                npm run test:all 2>&1 | Tee-Object -FilePath "$ResultsDir\puppeteer-rerun.log"
                $exitCode = $LASTEXITCODE
            } finally { Pop-Location }
        }
        "k6" {
            Write-Info "K6: 重跑压测场景"
            Push-Location "$RootDir\k6"
            try {
                k6 run scenarios/smoke-test.js 2>&1 | Tee-Object -FilePath "$ResultsDir\k6-rerun.log"
                $exitCode = $LASTEXITCODE
            } finally { Pop-Location }
        }
    }

    $duration = [math]::Round(((Get-Date) - $startTime).TotalMinutes, 1)
    return @{ ExitCode = $exitCode; Duration = $duration }
}

# ═══════════════════════════════════════════════
# 主流程
# ═══════════════════════════════════════════════
Write-Banner "🔄 精准重跑失败用例"

# 确定要重跑的工具
if ($Tools) {
    $targetTools = $Tools -split "," | ForEach-Object { $_.Trim().ToLower() }
    Write-Info "手动指定重跑: $($targetTools -join ', ')"
} else {
    $targetTools = Get-FailedTools
    if ($targetTools.Count -eq 0) {
        Write-OK "上次执行无失败记录，无需重跑"
        exit 0
    }
    Write-Info "自动检测到 $($targetTools.Count) 个工具有失败: $($targetTools -join ', ')"
}

Write-Host ""

# 逐个精准重跑
$results = [ordered]@{}
foreach ($tool in $targetTools) {
    Write-Host "  ─── 重跑 $($tool.ToUpper()) ───" -ForegroundColor Cyan
    $result = Rerun-Tool -Name $tool
    $results[$tool] = $result

    if ($result.ExitCode -eq 0) {
        Write-OK "$($tool.ToUpper()) 重跑通过 ($($result.Duration)m)"
    } else {
        Write-Fail "$($tool.ToUpper()) 仍然失败 ($($result.Duration)m)"
    }
    Write-Host ""
}

# 汇总
Write-Banner "📊 重跑结果汇总"
$stillFailing = @()
foreach ($tool in $results.Keys) {
    if ($results[$tool].ExitCode -eq 0) {
        Write-OK "$($tool.ToUpper().PadRight(12)) → 修复成功 ✅"
    } else {
        Write-Fail "$($tool.ToUpper().PadRight(12)) → 仍然失败 ❌"
        $stillFailing += $tool
    }
}

if ($stillFailing.Count -gt 0) {
    Write-Host ""
    Write-Host "  ⚠️ 仍有 $($stillFailing.Count) 个工具失败: $($stillFailing -join ', ')" -ForegroundColor Yellow
    Write-Host "  📂 查看重跑日志: $ResultsDir\*-rerun.log" -ForegroundColor Yellow
    exit 1
} else {
    Write-Host ""
    Write-OK "所有失败用例已修复！"
    exit 0
}
