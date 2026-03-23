<#
.SYNOPSIS
    从主项目同步测试文件到测试专用仓库（全量覆盖）
.DESCRIPTION
    将 d:\2026\aiops.v2 中的测试相关文件全量覆盖到 d:\2026\test-only-cloud
    仅复制测试脚本，严禁复制业务代码、配置、密钥
.NOTES
    执行前确保当前目录为 d:\2026\test-only-cloud
#>

param(
    [string]$MainProjectPath = "D:\2026\aiops.v2",
    [string]$TestRepoPath = "D:\2026\test-only-cloud",
    [switch]$DryRun
)

$ErrorActionPreference = "Stop"

Write-Host "═══════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "  从主项目同步测试文件到测试专用仓库" -ForegroundColor Cyan
Write-Host "  源: $MainProjectPath" -ForegroundColor Gray
Write-Host "  目标: $TestRepoPath" -ForegroundColor Gray
Write-Host "  模式: $(if ($DryRun) { '预览(DryRun)' } else { '执行' })" -ForegroundColor $(if ($DryRun) { 'Yellow' } else { 'Green' })
Write-Host "═══════════════════════════════════════════════════" -ForegroundColor Cyan

# ── 校验 ──
if (-not (Test-Path $MainProjectPath)) {
    Write-Error "主项目路径不存在: $MainProjectPath"
    exit 1
}
if (-not (Test-Path $TestRepoPath)) {
    Write-Error "测试仓库路径不存在: $TestRepoPath"
    exit 1
}

# ── 需要同步的测试目录 ──
$TestDirs = @(
    # pytest / API / 自动化测试
    "testing/tests/api"
    "testing/tests/automated"
    "testing/tests/blockchain"
    "testing/tests/security"
    "testing/tests/integration"
    "testing/tests/e2e"
    "testing/tests/smoke"
    "testing/tests/observability"
    "testing/tests/deployment"
    "testing/tests/recovery"
    "testing/tests/scripts"
    "testing/tests/_shared"
    "testing/tests/test-automation"
    "testing/tests/test-orchestrator"
    "testing/tests/test-plans"
    "testing/tests/tests"
    "testing/tests/manual-test-helpers"

    # Cypress
    "testing/tests/cypress-tests/cypress"
    "testing/tests/cypress-tests/e2e"
    "testing/tests/cypress-tests/support"
    "testing/tests/cypress-tests/_tools"

    # Playwright
    "testing/tests/playwright-tests"

    # Puppeteer
    "testing/tests/puppeteer-tests"

    # Selenium
    "testing/tests/selenium-tests"

    # k6 性能测试
    "testing/k6"

    # C# 集成测试（仅源码，排除 bin/obj）
    "testing/JGSY.AGI.Test"
    "testing/JGSY.AGI.Benchmarks"

    # 测试报告模板目录
    "testing/test-reports"
)

# ── 需要同步的单独文件 ──
$TestFiles = @(
    # pytest 配置
    "testing/tests/conftest.py"
    "testing/tests/conftest_parametrized.py"
    "testing/tests/pytest.ini"
    "testing/tests/requirements.txt"
    "testing/tests/mock_client.py"
    "testing/tests/set-test-env.ps1"
    "testing/tests/__init__.py"
    "testing/tests/count_tests.py"
    "testing/tests/run_tests.py"
    "testing/tests/run-automated-tests.ps1"
    "testing/tests/test_api_comprehensive.py"
    "testing/tests/test_parametrized_standalone.py"
    "testing/tests/incremental-skiplist.json"
    "testing/tests/test-script-registry.json"
    "testing/tests/generate-parametrized-framework.js"
    "testing/tests/_check_pw.py"
    "testing/tests/_mock_frontend.py"
    "testing/tests/_run_all.py"
    "testing/tests/_test_debug_mock.py"
    "testing/tests/_test_mock_verify.py"
    "testing/tests/_test_simple_mock.py"

    # Cypress 配置文件
    "testing/tests/cypress-tests/cypress.config.js"
    "testing/tests/cypress-tests/cypress.fast.config.js"
    "testing/tests/cypress-tests/cypress.local.js"
    "testing/tests/cypress-tests/cypress.quick.js"
    "testing/tests/cypress-tests/package.json"
    "testing/tests/cypress-tests/batch-runner.js"
    "testing/tests/cypress-tests/fast-runner.js"
    "testing/tests/cypress-tests/mock-server.js"
    "testing/tests/cypress-tests/mock-app.html"
    "testing/tests/cypress-tests/batch-test-all.ps1"
    "testing/tests/cypress-tests/run-ui-single.ps1"
    "testing/tests/cypress-tests/.gitignore"
    "testing/tests/cypress-tests/README.md"
)

# ── 需要同步的脚本 ──
$ScriptFiles = @(
    "scripts/run-all-tests.ps1"
    "scripts/run-parallel-tests.ps1"
    "scripts/run-atomic-tests.ps1"
    "scripts/generate-tool-reports.ps1"
    "scripts/aggregate-tool-reports.ps1"
    "scripts/rerun-failed-tests.ps1"
    "scripts/scan-test-scripts.ps1"
    "scripts/lock-seven-tool-baseline.ps1"
    "scripts/incremental-seven-tool-gate.ps1"
    "scripts/seven-tool-report.common.ps1"
    "scripts/collect-test-results.ps1"
    "scripts/run-cypress-atomic.ps1"
    "scripts/run-playwright-atomic-all.ps1"
    "scripts/run-puppeteer-atomic-all.ps1"
    "scripts/run-pytest-atomic-all.ps1"
    "scripts/run-ui-atomic.ps1"
    "scripts/run-playwright-baseline.ps1"
    "scripts/run-playwright-fast.ps1"
    "scripts/run-playwright-oneone.ps1"
    "scripts/run-playwright-retest-failed.ps1"
    "scripts/run-incremental-atomic.ps1"
    "scripts/run-incremental-tests.ps1"
    "scripts/generate-test-report.ps1"
    "scripts/generate-combined-seven-tool-report.ps1"
    "scripts/cypress-serial-groups.ps1"
    "scripts/cypress-serial-run.ps1"
    "scripts/run-business-smoke.ps1"
    "scripts/run-full-test-suite.ps1"
    "scripts/run-tests-with-coverage.ps1"
    "scripts/archive-test-version.ps1"
    "scripts/run-performance-tests.ps1"
    "scripts/run-security-gate.ps1"
    "scripts/playwright-incremental-gate.ps1"
)

# ── 排除模式 ──
$ExcludePatterns = @(
    "bin", "obj", "node_modules", "__pycache__", ".pytest_cache",
    "reports", "test-results", "playwright-report", "screenshots",
    "*.log", "*.trx", ".vs", ".vscode", "venv", ".venv", "env"
)

function Copy-FilteredDir {
    param(
        [string]$SrcBase,
        [string]$DstBase,
        [string]$RelativePath
    )
    
    $src = Join-Path $SrcBase $RelativePath
    $dst = Join-Path $DstBase $RelativePath
    
    if (-not (Test-Path $src)) {
        Write-Host "  [跳过] 源不存在: $RelativePath" -ForegroundColor DarkYellow
        return 0
    }
    
    $count = 0
    $items = Get-ChildItem -Path $src -Recurse -File -ErrorAction SilentlyContinue
    
    foreach ($item in $items) {
        $relFile = $item.FullName.Substring($src.Length).TrimStart('\', '/')
        $fullRel = "$RelativePath/$relFile" -replace '\\', '/'
        
        # 检查排除模式
        $skip = $false
        foreach ($pattern in $ExcludePatterns) {
            if ($fullRel -match [regex]::Escape($pattern) -or $item.Directory.Name -in @("bin", "obj", "node_modules", "__pycache__", ".pytest_cache", "reports", "test-results", "playwright-report", "screenshots", ".vs", ".vscode")) {
                $skip = $true
                break
            }
        }
        if ($skip) { continue }
        
        $dstFile = Join-Path $DstBase $fullRel.Replace('/', '\')
        $dstDir = Split-Path $dstFile -Parent
        
        if ($DryRun) {
            Write-Host "    [预览] $fullRel" -ForegroundColor DarkGray
        } else {
            if (-not (Test-Path $dstDir)) {
                New-Item -ItemType Directory -Path $dstDir -Force | Out-Null
            }
            Copy-Item -Path $item.FullName -Destination $dstFile -Force
        }
        $count++
    }
    
    return $count
}

function Copy-SingleFile {
    param(
        [string]$SrcBase,
        [string]$DstBase,
        [string]$RelativePath
    )
    
    $src = Join-Path $SrcBase $RelativePath
    $dst = Join-Path $DstBase $RelativePath
    
    if (-not (Test-Path $src)) {
        Write-Host "  [跳过] 文件不存在: $RelativePath" -ForegroundColor DarkYellow
        return 0
    }
    
    if ($DryRun) {
        Write-Host "    [预览] $RelativePath" -ForegroundColor DarkGray
        return 1
    }
    
    $dstDir = Split-Path $dst -Parent
    if (-not (Test-Path $dstDir)) {
        New-Item -ItemType Directory -Path $dstDir -Force | Out-Null
    }
    Copy-Item -Path $src -Destination $dst -Force
    return 1
}

# ═══════════════════════════════════════════════════
# 开始同步
# ═══════════════════════════════════════════════════

$totalFiles = 0

# 1. 同步测试目录
Write-Host "`n📁 同步测试目录..." -ForegroundColor Green
foreach ($dir in $TestDirs) {
    Write-Host "  [$dir]" -ForegroundColor White
    $count = Copy-FilteredDir -SrcBase $MainProjectPath -DstBase $TestRepoPath -RelativePath $dir
    $totalFiles += $count
    if ($count -gt 0) {
        Write-Host "    → $count 个文件" -ForegroundColor DarkGreen
    }
}

# 2. 同步单独文件
Write-Host "`n📄 同步测试配置文件..." -ForegroundColor Green
foreach ($file in $TestFiles) {
    $count = Copy-SingleFile -SrcBase $MainProjectPath -DstBase $TestRepoPath -RelativePath $file
    $totalFiles += $count
}

# 3. 同步脚本
Write-Host "`n🔧 同步执行脚本..." -ForegroundColor Green
foreach ($script in $ScriptFiles) {
    $count = Copy-SingleFile -SrcBase $MainProjectPath -DstBase $TestRepoPath -RelativePath $script
    $totalFiles += $count
}

# ── 安全审计 ──
Write-Host "`n🔐 安全审计..." -ForegroundColor Yellow
$dangerous = @("appsettings", "connectionstring", "password", "secret", ".env")
$violations = @()

Get-ChildItem -Path $TestRepoPath -Recurse -File -ErrorAction SilentlyContinue | ForEach-Object {
    foreach ($d in $dangerous) {
        if ($_.Name -match $d -and $_.Name -ne ".gitignore" -and $_.Name -ne ".env.example") {
            $violations += $_.FullName.Substring($TestRepoPath.Length + 1)
        }
    }
}

if ($violations.Count -gt 0) {
    Write-Host "  ⚠️ 发现疑似敏感文件：" -ForegroundColor Red
    $violations | ForEach-Object { Write-Host "    $_" -ForegroundColor Red }
    Write-Host "  请手动确认不含真实密钥后再推送！" -ForegroundColor Red
} else {
    Write-Host "  ✅ 未发现敏感文件" -ForegroundColor Green
}

# ── 汇总 ──
Write-Host "`n═══════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "  同步完成！共 $totalFiles 个文件" -ForegroundColor Cyan
if ($DryRun) {
    Write-Host "  （预览模式，未实际复制）" -ForegroundColor Yellow
} else {
    Write-Host "  下一步: git add . && git commit -m '同步更新' && git push" -ForegroundColor Gray
}
Write-Host "═══════════════════════════════════════════════════" -ForegroundColor Cyan
