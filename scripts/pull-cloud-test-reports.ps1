<#
.SYNOPSIS
    从测试仓库拉取云端测试错误报告到主项目
.DESCRIPTION
    将 test-only-cloud 仓库（main 分支）的 test-error-reports/ 目录内容
    拉取到主项目的 TestResults/cloud-test-reports/ 目录
.NOTES
    在主项目目录下执行: .\scripts\pull-cloud-test-reports.ps1
#>

param(
    [string]$TestRepoUrl = "https://github.com/ChengMingXuan/test-only-cloud.git",
    [string]$TestRepoBranch = "main",
    [string]$TestRepoLocalPath = "D:\2026\test-only-cloud",
    [string]$OutputPath = ""
)

$ErrorActionPreference = "Stop"

# 自动推断主项目路径
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$MainProjectPath = Split-Path -Parent $ScriptDir

if (-not $OutputPath) {
    $OutputPath = Join-Path $MainProjectPath "TestResults\cloud-test-reports"
}

Write-Host "═══════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "  拉取云端测试错误报告" -ForegroundColor Cyan
Write-Host "═══════════════════════════════════════════════════" -ForegroundColor Cyan

# ── 方式一：从本地测试仓库复制 ──
if (Test-Path $TestRepoLocalPath) {
    Write-Host "`n📂 从本地测试仓库拉取最新..." -ForegroundColor Green
    
    Push-Location $TestRepoLocalPath
    try {
        # 先拉取最新
        git pull origin $TestRepoBranch
        if ($LASTEXITCODE -eq 0) {
            Write-Host "  ✅ Git pull 完成" -ForegroundColor Green
        } else {
            Write-Host "  ⚠️ Git pull 返回非 0，使用本地缓存" -ForegroundColor Yellow
        }
    } catch {
        Write-Host "  ⚠️ Git pull 失败，使用本地缓存" -ForegroundColor Yellow
    }
    Pop-Location
    
    $srcReports = Join-Path $TestRepoLocalPath "test-error-reports"
    if (Test-Path $srcReports) {
        # 复制到主项目
        if (-not (Test-Path $OutputPath)) {
            New-Item -ItemType Directory -Path $OutputPath -Force | Out-Null
        }
        Copy-Item -Path "$srcReports\*" -Destination $OutputPath -Recurse -Force
        Write-Host "  ✅ 错误报告已复制到: $OutputPath" -ForegroundColor Green

        # ── 同步标准格式报告到 TestResults/reports/（与本地聚合对接）──
        $srcStdReports = Join-Path $srcReports "latest\reports"
        if (Test-Path $srcStdReports) {
            $dstReports = Join-Path $MainProjectPath "TestResults\reports"
            if (-not (Test-Path $dstReports)) {
                New-Item -ItemType Directory -Path $dstReports -Force | Out-Null
            }
            $tools = @("pytest", "cypress", "playwright", "puppeteer", "selenium", "k6", "integration")
            $synced = 0
            foreach ($tool in $tools) {
                $jsonFile = Join-Path $srcStdReports "$tool-report.json"
                $mdFile = Join-Path $srcStdReports "$tool-report.md"
                if (Test-Path $jsonFile) {
                    Copy-Item $jsonFile $dstReports -Force
                    $synced++
                }
                if (Test-Path $mdFile) {
                    Copy-Item $mdFile $dstReports -Force
                }
            }
            if ($synced -gt 0) {
                Write-Host "  ✅ $synced 份标准报告已同步到 TestResults/reports/（可直接聚合）" -ForegroundColor Green
            }
        }
    } else {
        Write-Host "  ℹ️ 测试仓库中暂无错误报告" -ForegroundColor Yellow
    }
}
# ── 方式二：直接从远程仓库克隆（无本地仓库时） ──
else {
    Write-Host "`n📥 本地测试仓库不存在，从远程拉取..." -ForegroundColor Yellow
    
    $tempDir = Join-Path $env:TEMP "test-only-cloud-$(Get-Random)"
    try {
        git clone --depth 1 --branch $TestRepoBranch $TestRepoUrl $tempDir 2>$null
        
        $srcReports = Join-Path $tempDir "test-error-reports"
        if (Test-Path $srcReports) {
            if (-not (Test-Path $OutputPath)) {
                New-Item -ItemType Directory -Path $OutputPath -Force | Out-Null
            }
            Copy-Item -Path "$srcReports\*" -Destination $OutputPath -Recurse -Force
            Write-Host "  ✅ 错误报告已复制到: $OutputPath" -ForegroundColor Green

            # ── 同步标准格式报告 ──
            $srcStdReports = Join-Path $srcReports "latest\reports"
            if (Test-Path $srcStdReports) {
                $dstReports = Join-Path $MainProjectPath "TestResults\reports"
                if (-not (Test-Path $dstReports)) {
                    New-Item -ItemType Directory -Path $dstReports -Force | Out-Null
                }
                Get-ChildItem $srcStdReports -Filter "*-report.*" | Copy-Item -Destination $dstReports -Force
                Write-Host "  ✅ 标准报告已同步到 TestResults/reports/" -ForegroundColor Green
            }
        } else {
            Write-Host "  ℹ️ 远程仓库暂无错误报告" -ForegroundColor Yellow
        }
    } finally {
        if (Test-Path $tempDir) {
            Remove-Item -Path $tempDir -Recurse -Force -ErrorAction SilentlyContinue
        }
    }
}

# ── 显示报告摘要 ──
$summaryFile = Join-Path $OutputPath "latest\summary.md"
if (Test-Path $summaryFile) {
    Write-Host "`n📊 最新测试报告摘要：" -ForegroundColor Cyan
    Write-Host "─────────────────────────────────────────────" -ForegroundColor DarkGray
    Get-Content $summaryFile | Select-Object -First 40 | ForEach-Object {
        Write-Host "  $_"
    }
    Write-Host "─────────────────────────────────────────────" -ForegroundColor DarkGray
    Write-Host "  完整报告: $summaryFile" -ForegroundColor Gray
} else {
    Write-Host "`n  暂无汇总报告" -ForegroundColor DarkYellow
}

Write-Host "`n═══════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "  完成！报告位置: $OutputPath" -ForegroundColor Cyan
Write-Host "═══════════════════════════════════════════════════" -ForegroundColor Cyan
