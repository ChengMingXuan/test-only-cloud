<#
.SYNOPSIS
    运行单元测试并生成覆盖率报告（CI友好）

.DESCRIPTION
    使用 coverlet + reportgenerator 生成 Cobertura + HTML 报告
    输出目录：scripts/logs/coverage/

.EXAMPLE
    .\scripts\run-tests-with-coverage.ps1

.EXAMPLE
    .\scripts\run-tests-with-coverage.ps1 -MinCoverage 70
#>

param(
    [int]$MinCoverage = 60,
    [switch]$SkipHtmlReport
)

$ErrorActionPreference = "Stop"
$RepoRoot = Split-Path -Parent $PSScriptRoot
$TestProject = Join-Path $RepoRoot "testing\JGSY.AGI.Test\JGSY.AGI.Test.csproj"
$CoverageDir = Join-Path $RepoRoot "scripts\logs\coverage"
$CoberturaFile = Join-Path $CoverageDir "coverage.cobertura.xml"
$HtmlReportDir = Join-Path $CoverageDir "html"

# 确保输出目录存在
if (!(Test-Path $CoverageDir)) {
    New-Item -ItemType Directory -Path $CoverageDir -Force | Out-Null
}

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  运行测试并收集覆盖率" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 运行测试并收集覆盖率（使用 coverlet.msbuild）
Write-Host "[1/3] 运行测试..." -ForegroundColor Yellow

$testArgs = @(
    "test"
    $TestProject
    "--configuration", "Release"
    "--no-build"
    "--verbosity", "minimal"
    "--logger", "console;verbosity=minimal"
    "--collect", "XPlat Code Coverage"
    "--results-directory", $CoverageDir
    "/p:CollectCoverage=true"
    "/p:CoverletOutputFormat=cobertura"
    "/p:CoverletOutput=$CoberturaFile"
    "/p:Exclude=[xunit.*]*,[*.Tests]*,[testing\JGSY.AGI.Benchmarks]*"
    "/p:ExcludeByAttribute=GeneratedCodeAttribute,CompilerGeneratedAttribute"
)

# 先编译
Write-Host "  编译测试项目..." -ForegroundColor Gray
dotnet build $TestProject --configuration Release --verbosity quiet
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ 编译失败" -ForegroundColor Red
    exit 1
}

# 执行测试
& dotnet @testArgs
$testExitCode = $LASTEXITCODE

# 查找生成的覆盖率文件
$generatedCoverage = Get-ChildItem -Path $CoverageDir -Filter "coverage.cobertura.xml" -Recurse | Select-Object -First 1
if ($generatedCoverage) {
    Copy-Item $generatedCoverage.FullName $CoberturaFile -Force
    Write-Host "  覆盖率文件: $CoberturaFile" -ForegroundColor Gray
}

if ($testExitCode -ne 0) {
    Write-Host "❌ 测试失败 (exit code: $testExitCode)" -ForegroundColor Red
    exit $testExitCode
}

Write-Host "✅ 测试通过" -ForegroundColor Green
Write-Host ""

# 生成 HTML 报告
if (!$SkipHtmlReport -and (Test-Path $CoberturaFile)) {
    Write-Host "[2/3] 生成 HTML 报告..." -ForegroundColor Yellow

    $reportGenPath = dotnet tool list --global | Select-String "reportgenerator"
    if (!$reportGenPath) {
        Write-Host "  安装 reportgenerator..." -ForegroundColor Gray
        dotnet tool install --global dotnet-reportgenerator-globaltool --verbosity quiet
    }

    reportgenerator `
        "-reports:$CoberturaFile" `
        "-targetdir:$HtmlReportDir" `
        "-reporttypes:Html;Badges" `
        "-verbosity:Warning"

    Write-Host "  HTML 报告: $HtmlReportDir\index.html" -ForegroundColor Gray
    Write-Host "✅ HTML 报告已生成" -ForegroundColor Green
}
else {
    Write-Host "[2/3] 跳过 HTML 报告" -ForegroundColor DarkGray
}

Write-Host ""

# 解析覆盖率并检查阈值
Write-Host "[3/3] 检查覆盖率阈值..." -ForegroundColor Yellow

if (Test-Path $CoberturaFile) {
    [xml]$coverage = Get-Content $CoberturaFile
    $lineRate = [double]$coverage.coverage."line-rate" * 100
    $branchRate = [double]$coverage.coverage."branch-rate" * 100

    Write-Host "  行覆盖率:   $([math]::Round($lineRate, 2))%" -ForegroundColor Gray
    Write-Host "  分支覆盖率: $([math]::Round($branchRate, 2))%" -ForegroundColor Gray

    if ($lineRate -lt $MinCoverage) {
        Write-Host "❌ 行覆盖率 ($([math]::Round($lineRate, 2))%) 低于阈值 ($MinCoverage%)" -ForegroundColor Red
        exit 1
    }
    else {
        Write-Host "✅ 覆盖率达标" -ForegroundColor Green
    }
}
else {
    Write-Host "⚠️ 未找到覆盖率文件，跳过阈值检查" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  完成" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
