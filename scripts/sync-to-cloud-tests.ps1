<#
.SYNOPSIS
    同步测试文件到 GitHub 测试仓库并推送
.DESCRIPTION
    支持两种模式：
    - Full：全量覆盖（运行 sync-from-main.ps1 后提交推送）
    - Incremental：仅同步自上次提交后变更的测试文件
.EXAMPLE
    .\scripts\sync-to-cloud-tests.ps1 -Mode Full
    .\scripts\sync-to-cloud-tests.ps1 -Mode Incremental
#>

param(
    [ValidateSet("Full", "Incremental")]
    [string]$Mode = "Incremental",
    [string]$MainProjectPath = "D:\2026\aiops.v2",
    [string]$TestRepoPath = "D:\2026\test-only-cloud",
    [string]$CommitMessage = ""
)

$ErrorActionPreference = "Stop"

Write-Host "═══════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "  同步测试文件到 GitHub 测试仓库" -ForegroundColor Cyan
Write-Host "  模式: $Mode" -ForegroundColor $(if ($Mode -eq "Full") { "Yellow" } else { "Green" })
Write-Host "═══════════════════════════════════════════════════" -ForegroundColor Cyan

# ── 校验路径 ──
if (-not (Test-Path $MainProjectPath)) {
    Write-Error "主项目路径不存在: $MainProjectPath"
    exit 1
}
if (-not (Test-Path $TestRepoPath)) {
    Write-Error "测试仓库路径不存在: $TestRepoPath"
    exit 1
}

$syncScript = Join-Path $TestRepoPath "sync-from-main.ps1"
if (-not (Test-Path $syncScript)) {
    Write-Error "同步脚本不存在: $syncScript"
    exit 1
}

# ═══════════════════════════════════════════════════
# 步骤 1：同步文件
# ═══════════════════════════════════════════════════

if ($Mode -eq "Full") {
    Write-Host "`n📦 全量同步模式：运行 sync-from-main.ps1 ..." -ForegroundColor Yellow
    Push-Location $TestRepoPath
    try {
        & $syncScript -MainProjectPath $MainProjectPath -TestRepoPath $TestRepoPath
    } finally {
        Pop-Location
    }
} else {
    Write-Host "`n🔄 增量同步模式：仅复制变更的测试文件 ..." -ForegroundColor Green

    Push-Location $TestRepoPath
    try {
        # 获取测试仓库最后一次提交时间
        $lastCommitTime = $null
        $lastCommitStr = git log -1 --format="%aI" 2>$null
        if ($lastCommitStr) {
            $lastCommitTime = [DateTimeOffset]::Parse($lastCommitStr).LocalDateTime
            Write-Host "  上次提交时间: $($lastCommitTime.ToString('yyyy-MM-dd HH:mm:ss'))" -ForegroundColor Gray
        } else {
            Write-Host "  ⚠️ 无法获取上次提交时间，回退到全量模式" -ForegroundColor Yellow
            $Mode = "Full"
            & $syncScript -MainProjectPath $MainProjectPath -TestRepoPath $TestRepoPath
            Pop-Location
            # 继续后面的提交推送逻辑
            Push-Location $TestRepoPath
        }

        if ($Mode -eq "Incremental" -and $lastCommitTime) {
            # 需要同步的测试目录（与 sync-from-main.ps1 保持一致）
            $watchDirs = @(
                "testing/tests", "testing/k6", "testing/JGSY.AGI.Test",
                "testing/JGSY.AGI.Benchmarks", "testing/test-reports",
                "scripts"
            )

            $excludeSegments = @("bin", "obj", "node_modules", "__pycache__",
                ".pytest_cache", "reports", "test-results", "playwright-report",
                "screenshots", ".vs", ".vscode", "venv", ".venv", "env")

            $copiedCount = 0
            $skippedCount = 0

            foreach ($dir in $watchDirs) {
                $srcDir = Join-Path $MainProjectPath $dir
                if (-not (Test-Path $srcDir)) { continue }

                $files = Get-ChildItem -Path $srcDir -Recurse -File -ErrorAction SilentlyContinue |
                    Where-Object { $_.LastWriteTime -gt $lastCommitTime }

                foreach ($file in $files) {
                    $relPath = $file.FullName.Substring($MainProjectPath.Length).TrimStart('\', '/')
                    $relPathNorm = $relPath -replace '\\', '/'

                    # 排除检查
                    $skip = $false
                    foreach ($seg in $excludeSegments) {
                        if ($relPathNorm -match "(^|/)$([regex]::Escape($seg))(/|$)") {
                            $skip = $true; break
                        }
                    }

                    # 排除敏感文件
                    if ($relPathNorm -match 'appsettings|\.env|NuGet\.Config|connectionstring') {
                        $skip = $true
                    }

                    if ($skip) { $skippedCount++; continue }

                    $dstFile = Join-Path $TestRepoPath $relPathNorm.Replace('/', '\')
                    $dstDir = Split-Path $dstFile -Parent
                    if (-not (Test-Path $dstDir)) {
                        New-Item -ItemType Directory -Path $dstDir -Force | Out-Null
                    }
                    Copy-Item -Path $file.FullName -Destination $dstFile -Force
                    $copiedCount++
                }
            }

            Write-Host "  ✅ 增量同步完成：复制 $copiedCount 个文件，跳过 $skippedCount 个" -ForegroundColor Green
        }
    } finally {
        Pop-Location
    }
}

# ═══════════════════════════════════════════════════
# 步骤 2：提交并推送
# ═══════════════════════════════════════════════════

Write-Host "`n📤 提交并推送到 GitHub ..." -ForegroundColor Cyan

Push-Location $TestRepoPath
try {
    git add -A 2>$null

    $changes = git status --porcelain 2>$null
    if (-not $changes) {
        Write-Host "  ℹ️ 无变更，跳过推送" -ForegroundColor Yellow
        Pop-Location
        return
    }

    $changeCount = ($changes | Measure-Object).Count
    Write-Host "  变更文件数: $changeCount" -ForegroundColor Gray

    if (-not $CommitMessage) {
        $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm"
        $modeLabel = if ($Mode -eq "Full") { "全量同步" } else { "增量同步" }
        $CommitMessage = "sync($modeLabel): $timestamp - $changeCount 个文件"
    }

    git commit -m $CommitMessage 2>$null
    Write-Host "  ✅ 已提交: $CommitMessage" -ForegroundColor Green

    $pushOutput = git push 2>&1 | Out-String
    if ($LASTEXITCODE -eq 0) {
        Write-Host "  ✅ 推送成功" -ForegroundColor Green
    } else {
        Write-Host "  ❌ 推送失败，请检查网络或 SSH 配置" -ForegroundColor Red
        Write-Host $pushOutput -ForegroundColor Gray
        exit 1
    }
} finally {
    Pop-Location
}

Write-Host "`n═══════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "  完成！GitHub Actions 将自动执行测试" -ForegroundColor Cyan
Write-Host "  查看: https://github.com/ChengMingXuan/test-only-cloud/actions" -ForegroundColor Gray
Write-Host "═══════════════════════════════════════════════════" -ForegroundColor Cyan
