<#
.SYNOPSIS
    AIOPS v2.0 全面自动化测试运行器
.DESCRIPTION
    运行 tests/automated/ 下的 pytest 自动化测试套件。
    支持按类别、优先级、标记筛选运行。
.PARAMETER Mode
    运行模式:
      smoke    — 仅烟雾测试 (P0, ~2 分钟)
      core     — 烟雾 + 认证 + CRUD (P0+P1, ~5 分钟)
      full     — 全量测试 (~15 分钟)
      security — 仅安全测试
      tenant   — 仅租户隔离测试
      integration — 仅集成测试
.PARAMETER Parallel
    并行 worker 数量，默认 auto (CPU 核数)
.PARAMETER Markers
    自定义 pytest markers 表达式
.EXAMPLE
    .\run-automated-tests.ps1 -Mode smoke
    .\run-automated-tests.ps1 -Mode full -Parallel 4
    .\run-automated-tests.ps1 -Markers "p0 and not db_verify"
#>

param(
    [ValidateSet("smoke", "core", "full", "security", "tenant", "integration")]
    [string]$Mode = "full",

    [string]$Parallel = "auto",
    [string]$Markers = "",
    [switch]$Html,
    [switch]$Verbose
)

$ErrorActionPreference = "Stop"
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$TestDir = Join-Path $ScriptDir "automated"
$ResultDir = Join-Path $ScriptDir ".." "TestResults"

# 确保结果目录存在
if (-not (Test-Path $ResultDir)) {
    New-Item -ItemType Directory -Path $ResultDir -Force | Out-Null
}

# 检查 Python 和 pytest
try {
    $null = python --version 2>&1
} catch {
    Write-Error "未找到 Python，请确保已安装并在 PATH 中"
    exit 1
}

# 安装依赖（首次运行）
$reqFile = Join-Path $TestDir "requirements.txt"
if (Test-Path $reqFile) {
    Write-Host "📦 检查依赖..." -ForegroundColor Cyan
    python -m pip install -r $reqFile -q 2>&1 | Out-Null
}

# 构建 pytest 参数
$pytestArgs = @()
$pytestArgs += "--rootdir=$TestDir"
$pytestArgs += "-c", (Join-Path $TestDir "pytest.ini")

# 根据模式设置 markers
if ($Markers) {
    $pytestArgs += "-m", $Markers
} else {
    switch ($Mode) {
        "smoke"       { $pytestArgs += "-m", "smoke or p0" }
        "core"        { $pytestArgs += "-m", "smoke or auth or crud or p0 or p1" }
        "security"    { $pytestArgs += "-m", "security or boundary" }
        "tenant"      { $pytestArgs += "-m", "tenant" }
        "integration" { $pytestArgs += "-m", "integration" }
        "full"        { } # 不加 -m，运行全部
    }
}

# JUnit XML 报告
$junitFile = Join-Path $ResultDir "automated-tests-junit.xml"
$pytestArgs += "--junitxml=$junitFile"

# HTML 报告
if ($Html) {
    $htmlFile = Join-Path $ResultDir "automated-tests-report.html"
    $pytestArgs += "--html=$htmlFile", "--self-contained-html"
}

# 并行
if ($Parallel -ne "1") {
    $pytestArgs += "-n", $Parallel
}

# 详细输出
if ($Verbose) {
    $pytestArgs += "-v", "--tb=long"
} else {
    $pytestArgs += "--tb=short"
}

# 运行信息
$ts = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
Write-Host ""
Write-Host "╔══════════════════════════════════════════╗" -ForegroundColor Green
Write-Host "║   AIOPS v2.0 全面自动化测试              ║" -ForegroundColor Green
Write-Host "╠══════════════════════════════════════════╣" -ForegroundColor Green
Write-Host "║  模式: $($Mode.PadRight(34))║" -ForegroundColor Green
Write-Host "║  时间: $($ts.PadRight(34))║" -ForegroundColor Green
Write-Host "╚══════════════════════════════════════════╝" -ForegroundColor Green
Write-Host ""

# 执行
Write-Host "🚀 开始测试..." -ForegroundColor Yellow
Write-Host "   命令: python -m pytest $($pytestArgs -join ' ')" -ForegroundColor DarkGray
Write-Host ""

$startTime = Get-Date
python -m pytest @pytestArgs $TestDir
$exitCode = $LASTEXITCODE
$duration = (Get-Date) - $startTime

# 结果汇总
Write-Host ""
Write-Host "════════════════════════════════════════════" -ForegroundColor Cyan
if ($exitCode -eq 0) {
    Write-Host "✅ 全部测试通过！" -ForegroundColor Green
} elseif ($exitCode -eq 1) {
    Write-Host "❌ 部分测试失败" -ForegroundColor Red
} elseif ($exitCode -eq 5) {
    Write-Host "⚠️  未收集到测试用例" -ForegroundColor Yellow
} else {
    Write-Host "⚠️  测试异常退出 (code=$exitCode)" -ForegroundColor Red
}
Write-Host "⏱️  耗时: $($duration.ToString('mm\:ss'))" -ForegroundColor Cyan
Write-Host "📊 JUnit 报告: $junitFile" -ForegroundColor Cyan
if ($Html) {
    Write-Host "📊 HTML 报告: $htmlFile" -ForegroundColor Cyan
}
Write-Host "════════════════════════════════════════════" -ForegroundColor Cyan

exit $exitCode
