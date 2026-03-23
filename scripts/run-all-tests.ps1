<#
.SYNOPSIS
    一键执行全部六类测试（按优先级顺序）
.DESCRIPTION
    执行顺序：pytest → Cypress → Playwright → Selenium → Puppeteer → K6
    从快速反馈到完整验证，从单元测试到性能压测
.PARAMETER Level
    执行级别：
    - smoke    : 冒烟测试（约5分钟）- pytest冒烟 + K6冒烟
    - quick    : 快速验证（约20分钟）- pytest全量 + Cypress
    - standard : 标准验证（约1.5小时）- pytest + Cypress + Playwright(Chromium) + K6负载
    - full     : 完整验证（约3-4小时）- 全部6类测试（每类选代表场景）
    - ultimate : 终极验证（约5-6小时）- 全部6类测试所有场景
.PARAMETER SkipInstall
    跳过依赖安装检查
.PARAMETER StopOnFailure
    遇到失败立即停止
.EXAMPLE
    .\run-all-tests.ps1 -Level smoke
    .\run-all-tests.ps1 -Level full -StopOnFailure
#>
param(
    [ValidateSet("smoke", "quick", "standard", "full", "ultimate")]
    [string]$Level = "standard",
    [switch]$SkipInstall,
    [switch]$StopOnFailure
)

$ErrorActionPreference = "Continue"
$script:TotalTests = 0
$script:PassedTests = 0
$script:FailedTests = 0
$script:SkippedTests = 0
$script:StartTime = Get-Date
$script:Results = @()

# 颜色输出
function Write-Step { param($msg) Write-Host "`n═══════════════════════════════════════════════════════════════" -ForegroundColor Cyan; Write-Host "  $msg" -ForegroundColor Cyan; Write-Host "═══════════════════════════════════════════════════════════════`n" -ForegroundColor Cyan }
function Write-SubStep { param($msg) Write-Host "  → $msg" -ForegroundColor White }
function Write-Success { param($msg) Write-Host "  ✅ $msg" -ForegroundColor Green }
function Write-Failure { param($msg) Write-Host "  ❌ $msg" -ForegroundColor Red }
function Write-Skip { param($msg) Write-Host "  ⏭️ $msg" -ForegroundColor Yellow }
function Write-Info { param($msg) Write-Host "  ℹ️ $msg" -ForegroundColor Gray }

# 执行测试并记录结果
function Invoke-Test {
    param(
        [string]$Category,
        [string]$Name,
        [string]$Command,
        [string]$WorkDir,
        [int]$ExpectedMinutes = 10
    )
    
    $script:TotalTests++
    $testStart = Get-Date
    Write-SubStep "[$Category] $Name (预计 $ExpectedMinutes 分钟)"
    
    try {
        Push-Location $WorkDir
        $output = Invoke-Expression $Command 2>&1
        $exitCode = $LASTEXITCODE
        Pop-Location
        
        $duration = [math]::Round(((Get-Date) - $testStart).TotalMinutes, 1)
        
        if ($exitCode -eq 0) {
            $script:PassedTests++
            Write-Success "$Name - 通过 (耗时 $duration 分钟)"
            $script:Results += [PSCustomObject]@{
                Category = $Category
                Name = $Name
                Status = "✅ 通过"
                Duration = "$duration 分钟"
            }
            return $true
        } else {
            $script:FailedTests++
            Write-Failure "$Name - 失败 (退出码: $exitCode, 耗时 $duration 分钟)"
            $script:Results += [PSCustomObject]@{
                Category = $Category
                Name = $Name
                Status = "❌ 失败"
                Duration = "$duration 分钟"
            }
            if ($StopOnFailure) {
                Write-Host "`n⛔ StopOnFailure 已启用，测试终止" -ForegroundColor Red
                Show-Summary
                exit 1
            }
            return $false
        }
    } catch {
        Pop-Location -ErrorAction SilentlyContinue
        $script:FailedTests++
        Write-Failure "$Name - 异常: $_"
        $script:Results += [PSCustomObject]@{
            Category = $Category
            Name = $Name
            Status = "❌ 异常"
            Duration = "N/A"
        }
        return $false
    }
}

# 显示最终汇总
function Show-Summary {
    $totalTime = [math]::Round(((Get-Date) - $script:StartTime).TotalMinutes, 1)
    
    Write-Host "`n" -NoNewline
    Write-Step "📊 测试汇总报告"
    
    Write-Host "  ┌─────────────────────────────────────────────────────────────┐" -ForegroundColor White
    Write-Host "  │  执行级别: $Level                                            " -ForegroundColor White
    Write-Host "  │  总测试数: $($script:TotalTests)                              " -ForegroundColor White
    Write-Host "  │  ✅ 通过: $($script:PassedTests)                              " -ForegroundColor Green
    Write-Host "  │  ❌ 失败: $($script:FailedTests)                              " -ForegroundColor $(if ($script:FailedTests -gt 0) { "Red" } else { "White" })
    Write-Host "  │  ⏭️ 跳过: $($script:SkippedTests)                             " -ForegroundColor Yellow
    Write-Host "  │  总耗时: $totalTime 分钟                                      " -ForegroundColor White
    Write-Host "  └─────────────────────────────────────────────────────────────┘" -ForegroundColor White
    
    Write-Host "`n  详细结果:" -ForegroundColor Cyan
    $script:Results | Format-Table -AutoSize | Out-String | Write-Host
    
    if ($script:FailedTests -eq 0) {
        Write-Host "  🎉 全部测试通过！" -ForegroundColor Green
        return 0
    } else {
        Write-Host "  ⚠️ 存在失败测试，请检查上述详情" -ForegroundColor Yellow
        return 1
    }
}

# 安装依赖
function Install-Dependencies {
    if ($SkipInstall) {
        Write-Info "跳过依赖安装检查"
        return
    }
    
    Write-Step "📦 检查并安装测试依赖"
    
    # pytest
    Write-SubStep "检查 pytest 依赖..."
    if (-not (Test-Path "testing/tests/test-automation/venv")) {
        Write-Info "创建 pytest 虚拟环境..."
        Push-Location "testing/tests/test-automation"
        python -m venv venv
        .\venv\Scripts\Activate.ps1
        pip install -r requirements.txt -q
        Pop-Location
    }
    
    # Cypress
    Write-SubStep "检查 Cypress 依赖..."
    if (-not (Test-Path "testing/tests/cypress-tests/node_modules")) {
        Push-Location "testing/tests/cypress-tests"
        npm install --silent
        Pop-Location
    }
    
    # Playwright
    Write-SubStep "检查 Playwright 依赖..."
    if (-not (Test-Path "testing/tests/playwright-tests/node_modules")) {
        Push-Location "testing/tests/playwright-tests"
        npm install --silent
        npx playwright install --with-deps
        Pop-Location
    }
    
    # Selenium
    Write-SubStep "检查 Selenium 依赖..."
    if (-not (Test-Path "testing/tests/selenium-tests/venv")) {
        Push-Location "testing/tests/selenium-tests"
        python -m venv venv
        .\venv\Scripts\Activate.ps1
        pip install -r requirements.txt -q
        Pop-Location
    }
    
    # Puppeteer
    Write-SubStep "检查 Puppeteer 依赖..."
    if (-not (Test-Path "testing/tests/puppeteer-tests/node_modules")) {
        Push-Location "testing/tests/puppeteer-tests"
        npm install --silent
        Pop-Location
    }
    
    # K6
    Write-SubStep "检查 K6..."
    if (-not (Get-Command k6 -ErrorAction SilentlyContinue)) {
        Write-Failure "K6 未安装，请执行: choco install k6"
    }
    
    Write-Success "依赖检查完成"
}

# ═══════════════════════════════════════════════════════════════════════════
# 主执行流程
# ═══════════════════════════════════════════════════════════════════════════

Clear-Host
Write-Host @"

  ╔══════════════════════════════════════════════════════════════════════════╗
  ║                                                                          ║
  ║   🧪 AIOPS 六类测试 - 一键全量执行                                        ║
  ║                                                                          ║
  ║   执行顺序: pytest → Cypress → Playwright → Selenium → Puppeteer → K6   ║
  ║   执行级别: $($Level.ToUpper().PadRight(10))                                                     ║
  ║                                                                          ║
  ╚══════════════════════════════════════════════════════════════════════════╝

"@ -ForegroundColor Cyan

# 加载测试环境变量（将浏览器/npm/缓存全部指向 D 盘）
$envScript = Join-Path $PSScriptRoot "..\testing\tests\set-test-env.ps1"
if (Test-Path $envScript) {
    . $envScript
} else {
    Write-Host "  ⚠️ testing\tests\set-test-env.ps1 不存在，浏览器缓存可能写入 C 盘" -ForegroundColor Yellow
}

Install-Dependencies

# ─────────────────────────────────────────────────────────────────────────────
# Level: smoke - 冒烟测试（约5分钟）
# ─────────────────────────────────────────────────────────────────────────────
if ($Level -in @("smoke", "quick", "standard", "full", "ultimate")) {
    Write-Step "① 🐍 pytest - API冒烟测试"
    
    Invoke-Test -Category "pytest" -Name "冒烟测试" `
        -Command ".\venv\Scripts\Activate.ps1; pytest testing/tests/ -v -m smoke --tb=short" `
        -WorkDir "testing/tests/test-automation" `
        -ExpectedMinutes 2
}

if ($Level -eq "smoke") {
    Write-Step "⑥ ⚡ K6 - API冒烟测试"
    
    Invoke-Test -Category "K6" -Name "冒烟测试" `
        -Command "k6 run scenarios/smoke-test.js" `
        -WorkDir "k6" `
        -ExpectedMinutes 1
    
    Show-Summary
    exit
}

# ─────────────────────────────────────────────────────────────────────────────
# Level: quick - 快速验证（约20分钟）
# ─────────────────────────────────────────────────────────────────────────────
if ($Level -in @("quick", "standard", "full", "ultimate")) {
    Write-Step "① 🐍 pytest - 全量API测试"
    
    Invoke-Test -Category "pytest" -Name "全量测试" `
        -Command ".\venv\Scripts\Activate.ps1; pytest testing/tests/ -v --html=report.html --self-contained-html" `
        -WorkDir "testing/tests/test-automation" `
        -ExpectedMinutes 12
    
    Write-Step "② 🌲 Cypress - 组件交互测试"
    
    Invoke-Test -Category "Cypress" -Name "组件测试" `
        -Command "npm run cy:run" `
        -WorkDir "testing/tests/cypress-tests" `
        -ExpectedMinutes 8
}

if ($Level -eq "quick") {
    Show-Summary
    exit
}

# ─────────────────────────────────────────────────────────────────────────────
# Level: standard - 标准验证（约1.5小时）
# ─────────────────────────────────────────────────────────────────────────────
if ($Level -in @("standard", "full", "ultimate")) {
    Write-Step "③ 🎭 Playwright - E2E测试 (Chromium)"
    
    Invoke-Test -Category "Playwright" -Name "Chromium E2E" `
        -Command "npm run test:chromium" `
        -WorkDir "testing/tests/playwright-tests" `
        -ExpectedMinutes 10
    
    Write-Step "⑥ ⚡ K6 - 负载测试"
    
    Invoke-Test -Category "K6" -Name "负载测试" `
        -Command "k6 run scenarios/load-test.js" `
        -WorkDir "k6" `
        -ExpectedMinutes 20
}

if ($Level -eq "standard") {
    Show-Summary
    exit
}

# ─────────────────────────────────────────────────────────────────────────────
# Level: full - 完整验证（约3-4小时）
# ─────────────────────────────────────────────────────────────────────────────
if ($Level -in @("full", "ultimate")) {
    Write-Step "③ 🎭 Playwright - 跨浏览器E2E测试"
    
    Invoke-Test -Category "Playwright" -Name "Firefox E2E" `
        -Command "npm run test:firefox" `
        -WorkDir "testing/tests/playwright-tests" `
        -ExpectedMinutes 12
    
    Invoke-Test -Category "Playwright" -Name "WebKit E2E" `
        -Command "npm run test:webkit" `
        -WorkDir "testing/tests/playwright-tests" `
        -ExpectedMinutes 12
    
    Write-Step "④ 🌐 Selenium - 多浏览器兼容性测试"
    
    # 启动 Selenium Grid
    Write-SubStep "启动 Selenium Grid..."
    Push-Location "testing/tests/selenium-tests"
    $grid = docker ps --filter 'name=selenium-hub' --format '{{.Names}}'
    if (-not $grid) {
        docker-compose -f selenium-grid-config.yml up -d
        Start-Sleep -Seconds 10
    }
    Pop-Location
    
    Invoke-Test -Category "Selenium" -Name "多浏览器矩阵" `
        -Command ".\venv\Scripts\Activate.ps1; pytest testing/tests/test_cross_browser.py -v --html=report.html --junitxml=../../TestResults/selenium-results.xml" `
        -WorkDir "testing/tests/selenium-tests" `
        -ExpectedMinutes 40
    
    Write-Step "⑤ 🤖 Puppeteer - 性能监控测试"
    
    Invoke-Test -Category "Puppeteer" -Name "性能基准测试" `
        -Command "npm run test:performance" `
        -WorkDir "testing/tests/puppeteer-tests" `
        -ExpectedMinutes 12
    
    Write-Step "⑥ ⚡ K6 - 压力测试"
    
    Invoke-Test -Category "K6" -Name "压力测试" `
        -Command "k6 run scenarios/stress-test.js" `
        -WorkDir "k6" `
        -ExpectedMinutes 18
}

if ($Level -eq "full") {
    Show-Summary
    exit
}

# ─────────────────────────────────────────────────────────────────────────────
# Level: ultimate - 终极验证（约5-6小时）
# ─────────────────────────────────────────────────────────────────────────────
if ($Level -eq "ultimate") {
    Write-Step "① 🐍 pytest - 分类测试"
    
    Invoke-Test -Category "pytest" -Name "P0优先级测试" `
        -Command ".\venv\Scripts\Activate.ps1; pytest testing/tests/ -v -m p0" `
        -WorkDir "testing/tests/test-automation" `
        -ExpectedMinutes 5
    
    Invoke-Test -Category "pytest" -Name "P1优先级测试" `
        -Command ".\venv\Scripts\Activate.ps1; pytest testing/tests/ -v -m p1" `
        -WorkDir "testing/tests/test-automation" `
        -ExpectedMinutes 8
    
    Invoke-Test -Category "pytest" -Name "多租户隔离测试" `
        -Command ".\venv\Scripts\Activate.ps1; pytest testing/tests/ -v -m tenant_isolation" `
        -WorkDir "testing/tests/test-automation" `
        -ExpectedMinutes 5
    
    Invoke-Test -Category "pytest" -Name "安全测试" `
        -Command ".\venv\Scripts\Activate.ps1; pytest testing/tests/ -v -m security" `
        -WorkDir "testing/tests/test-automation" `
        -ExpectedMinutes 5
    
    Write-Step "③ 🎭 Playwright - 移动端测试"
    
    Invoke-Test -Category "Playwright" -Name "移动端模拟" `
        -Command "npm run test:mobile" `
        -WorkDir "testing/tests/playwright-tests" `
        -ExpectedMinutes 10
    
    Write-Step "⑤ 🤖 Puppeteer - 视觉回归测试"
    
    Invoke-Test -Category "Puppeteer" -Name "视觉回归" `
        -Command "npm run test:visual" `
        -WorkDir "testing/tests/puppeteer-tests" `
        -ExpectedMinutes 10
    
    Write-Step "⑥ ⚡ K6 - 专项测试"
    
    Invoke-Test -Category "K6" -Name "综合测试" `
        -Command "k6 run scenarios/comprehensive-test.js" `
        -WorkDir "k6" `
        -ExpectedMinutes 15
    
    Invoke-Test -Category "K6" -Name "充电并发测试" `
        -Command "k6 run scenarios/charging-concurrency-test.js" `
        -WorkDir "k6" `
        -ExpectedMinutes 10
    
    Invoke-Test -Category "K6" -Name "数字孪生测试" `
        -Command "k6 run scenarios/digital-twin-test.js" `
        -WorkDir "k6" `
        -ExpectedMinutes 10
    
    Invoke-Test -Category "K6" -Name "区块链测试" `
        -Command "k6 run scenarios/blockchain-test.js" `
        -WorkDir "k6" `
        -ExpectedMinutes 10
}

Show-Summary

# 自动收集结果并生成跟踪报告
Write-Step "📊 生成六类测试跟踪报告"
try {
    & "$PSScriptRoot\generate-test-report.ps1" -CollectFirst
} catch {
    Write-Host "  ⚠️ 报告生成失败: $_" -ForegroundColor Yellow
}
