<#
.SYNOPSIS
    增量测试执行引擎 - 基于 Git diff 自动检测变更并只运行受影响的测试
.DESCRIPTION
    工作流程：
    1. git diff 检测当前分支与基准分支的文件变更
    2. 按照变更文件的路径映射到受影响的微服务和测试工具
    3. 仅执行受影响范围的测试脚本
    4. 输出增量测试报告

    映射规则：
    - JGSY.AGI.{Service}/** → pytest(对应服务) + IntegrationTest(对应服务)
    - JGSY.AGI.Frontend/** → Cypress + Playwright + Puppeteer + Selenium
    - JGSY.AGI.Gateway/**  → k6(网关路由) + pytest(网关健康)
    - testing/tests/{tool}/** → 该工具自身
    - JGSY.AGI.Common.*/** → 全量回归（公共库变更影响全部服务）
    - docker/** → k6(部署验证) + pytest(健康检查)

.PARAMETER BaseBranch
    基准分支（默认 main），用于比较差异
.PARAMETER DiffMode
    差异模式：branch(与分支比较) | staged(已暂存) | unstaged(未暂存) | last-commit(最后一次提交)
.PARAMETER ToolFilter
    只运行指定工具的增量测试（逗号分隔），留空则运行全部受影响的工具
.PARAMETER DryRun
    仅显示将要执行的测试范围，不实际运行
.PARAMETER GenerateReport
    执行完成后生成增量报告

.EXAMPLE
    .\run-incremental-tests.ps1                           # 默认：对比 main 分支
    .\run-incremental-tests.ps1 -DiffMode staged          # 只测试已暂存的变更
    .\run-incremental-tests.ps1 -DiffMode last-commit     # 只测试最后一次提交
    .\run-incremental-tests.ps1 -ToolFilter pytest,k6     # 只运行 pytest 和 k6
    .\run-incremental-tests.ps1 -DryRun                   # 仅预览影响范围
#>
param(
    [string]$BaseBranch = "main",
    [ValidateSet("branch", "staged", "unstaged", "last-commit")]
    [string]$DiffMode = "last-commit",
    [string]$ToolFilter = "",
    [switch]$DryRun,
    [switch]$GenerateReport
)

$ErrorActionPreference = "Continue"
$RootDir = (Resolve-Path "$PSScriptRoot\..").Path
$ResultsDir = Join-Path $RootDir "TestResults"
$IncrDir = Join-Path $ResultsDir "incremental"
New-Item -Path $IncrDir -ItemType Directory -Force | Out-Null

$timestamp = Get-Date -Format "yyyy-MM-dd_HH-mm-ss"
$reportFile = Join-Path $IncrDir "incremental-report-$timestamp.md"

# ═══════════════════════════════════════════════════════════════
# 服务到测试的映射表
# ═══════════════════════════════════════════════════════════════
$ServiceTestMap = @{
    "Account"              = @{ pytest = @("api/test_account_*.py"); integration = @("Account/"); k6 = @("auto-*-account.js") }
    "Analytics"            = @{ pytest = @("api/test_analytics_*.py"); integration = @("Analytics/"); k6 = @("auto-*-analytics.js") }
    "Blockchain"           = @{ pytest = @("blockchain/test_*.py"); integration = @("Blockchain/"); k6 = @("blockchain-test.js") }
    "Charging"             = @{ pytest = @("api/test_charging_*.py"); integration = @("Charging/"); k6 = @("auto-*-charging.js") }
    "ContentPlatform"      = @{ pytest = @("api/test_contentplatform_*.py"); integration = @("ContentPlatform/") }
    "Device"               = @{ pytest = @("api/test_device_*.py"); integration = @("Device/"); k6 = @("auto-*-device.js") }
    "DigitalTwin"          = @{ pytest = @("api/test_digitaltwin_*.py"); integration = @("DigitalTwin/") }
    "EnergyCore.MicroGrid" = @{ pytest = @("api/test_energy_*.py","api/test_microgrid_*.py"); integration = @("MicroGrid/","EnergyCore/") }
    "EnergyCore.Orchestrator" = @{ pytest = @("api/test_energy_*.py"); integration = @("EnergyCore/") }
    "EnergyCore.PVESSC"    = @{ pytest = @("api/test_energy_*.py","api/test_pvessc_*.py"); integration = @("PVESSC/") }
    "EnergyCore.VPP"       = @{ pytest = @("api/test_energy_*.py","api/test_vpp_*.py"); integration = @("EnergyCore/") }
    "EnergyServices.Operations" = @{ pytest = @("api/test_operations_*.py","api/test_energyeff_*.py","api/test_multienergy_*.py","api/test_safecontrol_*.py"); integration = @("EnergyServices/","EnergyEff/") }
    "EnergyServices.Trading"    = @{ pytest = @("api/test_trading_*.py","api/test_electrade_*.py","api/test_carbontrade_*.py","api/test_demandresp_*.py"); integration = @("EnergyServices/") }
    "Gateway"              = @{ pytest = @("api/test_gateway_*.py"); integration = @("Gateway/"); k6 = @("gateway-*.js") }
    "Identity"             = @{ pytest = @("api/test_identity_*.py","api/test_auth_*.py"); integration = @("Identity/","Auth/") }
    "Ingestion"            = @{ pytest = @("api/test_ingestion_*.py"); integration = @("Ingestion/") }
    "IotCloudAI"           = @{ pytest = @("api/test_iotcloudai_*.py","api/test_ai_*.py"); integration = @("IotCloudAI/") }
    "Observability"        = @{ pytest = @("api/test_observability_*.py"); integration = @("Observability/") }
    "Permission"           = @{ pytest = @("api/test_permission_*.py"); integration = @("Permission/") }
    "RuleEngine"           = @{ pytest = @("api/test_ruleengine_*.py"); integration = @("RuleEngine/") }
    "Settlement"           = @{ pytest = @("api/test_settlement_*.py"); integration = @("Settlement/"); k6 = @("auto-*-settlement.js") }
    "Simulator"            = @{ pytest = @("api/test_simulator_*.py"); integration = @("Simulator/") }
    "Station"              = @{ pytest = @("api/test_station_*.py"); integration = @("Station/"); k6 = @("auto-*-station.js") }
    "Storage"              = @{ pytest = @("api/test_storage_*.py"); integration = @("Storage/") }
    "Tenant"               = @{ pytest = @("api/test_tenant_*.py"); integration = @("Tenant/") }
    "WorkOrder"            = @{ pytest = @("api/test_workorder_*.py"); integration = @("WorkOrder/") }
}

# 前端变更 → 前端测试工具
$FrontendTools = @("cypress", "playwright", "puppeteer", "selenium")

# 工具过滤
$allowedTools = @()
if ($ToolFilter) {
    $allowedTools = $ToolFilter -split ',' | ForEach-Object { $_.Trim().ToLower() }
}

Write-Host "╔═══════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║        增量测试执行引擎 v1.0                                 ║" -ForegroundColor Cyan
Write-Host "╚═══════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""

# ═══════════════════════════════════════════════════════════════
# Step 1: 获取变更文件列表
# ═══════════════════════════════════════════════════════════════
Write-Host "  📋 检测变更文件（模式: $DiffMode）..." -ForegroundColor Yellow

Push-Location $RootDir
$changedFiles = @()
switch ($DiffMode) {
    "branch" {
        $changedFiles = git diff --name-only "$BaseBranch" 2>$null
    }
    "staged" {
        $changedFiles = git diff --cached --name-only 2>$null
    }
    "unstaged" {
        $changedFiles = git diff --name-only 2>$null
    }
    "last-commit" {
        $changedFiles = git diff --name-only HEAD~1 HEAD 2>$null
        if (-not $changedFiles) {
            # 如果没有 HEAD~1，使用 HEAD 与空树比较
            $changedFiles = git diff --name-only 4b825dc642cb6eb9a060e54bf899d69f82c6af58 HEAD 2>$null
        }
    }
}
Pop-Location

if (-not $changedFiles) {
    Write-Host "  ✅ 没有检测到文件变更，无需执行增量测试。" -ForegroundColor Green
    exit 0
}

Write-Host "  📁 检测到 $($changedFiles.Count) 个文件变更" -ForegroundColor White

# ═══════════════════════════════════════════════════════════════
# Step 2: 分析影响范围
# ═══════════════════════════════════════════════════════════════
Write-Host "`n  🔍 分析影响范围..." -ForegroundColor Yellow

$affectedServices = [System.Collections.Generic.HashSet[string]]::new()
$affectedTools = [System.Collections.Generic.HashSet[string]]::new()
$isCommonChange = $false
$isFrontendChange = $false
$isDockerChange = $false
$testFilesChanged = @{ pytest = @(); cypress = @(); puppeteer = @(); selenium = @(); playwright = @(); k6 = @(); integration = @() }

foreach ($file in $changedFiles) {
    # 公共库变更 → 全量回归
    if ($file -match "^JGSY\.AGI\.Common\.") {
        $isCommonChange = $true
        continue
    }

    # 前端变更
    if ($file -match "^JGSY\.AGI\.Frontend") {
        $isFrontendChange = $true
        continue
    }

    # Docker/部署变更
    if ($file -match "^docker/") {
        $isDockerChange = $true
        continue
    }

    # 微服务变更
    if ($file -match "^JGSY\.AGI\.([^/]+)/") {
        $svc = $Matches[1]
        [void]$affectedServices.Add($svc)
        continue
    }

    # 测试文件自身变更
    if ($file -match "^testing/tests/cypress-tests/") { $testFilesChanged.cypress += $file }
    elseif ($file -match "^testing/tests/playwright-tests/") { $testFilesChanged.playwright += $file }
    elseif ($file -match "^testing/tests/puppeteer-tests/") { $testFilesChanged.puppeteer += $file }
    elseif ($file -match "^testing/tests/selenium-tests/") { $testFilesChanged.selenium += $file }
    elseif ($file -match "^testing/k6/") { $testFilesChanged.k6 += $file }
    elseif ($file -match "^testing/tests/integration/") { $testFilesChanged.integration += $file }
    elseif ($file -match "^testing/tests/.+test_.*\.py$") { $testFilesChanged.pytest += $file }
}

# 公共库变更 → 全量
if ($isCommonChange) {
    Write-Host "  ⚠️ 公共库变更，触发全量回归" -ForegroundColor Yellow
    @("pytest","cypress","puppeteer","selenium","playwright","k6","integration") | ForEach-Object { [void]$affectedTools.Add($_) }
}

# 前端变更 → 前端测试
if ($isFrontendChange) {
    $FrontendTools | ForEach-Object { [void]$affectedTools.Add($_) }
}

# Docker变更 → k6 + pytest 健康检查
if ($isDockerChange) {
    [void]$affectedTools.Add("k6")
    [void]$affectedTools.Add("pytest")
}

# 服务变更 → 对应工具
foreach ($svc in $affectedServices) {
    if ($ServiceTestMap.ContainsKey($svc)) {
        $map = $ServiceTestMap[$svc]
        foreach ($tool in $map.Keys) { [void]$affectedTools.Add($tool) }
    } else {
        # 未映射服务 → pytest + integration
        [void]$affectedTools.Add("pytest")
        [void]$affectedTools.Add("integration")
    }
}

# 测试文件自身变更
foreach ($tool in $testFilesChanged.Keys) {
    if ($testFilesChanged[$tool].Count -gt 0) {
        [void]$affectedTools.Add($tool)
    }
}

# 应用工具过滤
if ($allowedTools.Count -gt 0) {
    $filtered = [System.Collections.Generic.HashSet[string]]::new()
    foreach ($tool in $affectedTools) {
        if ($allowedTools -contains $tool) { [void]$filtered.Add($tool) }
    }
    $affectedTools = $filtered
}

# ═══════════════════════════════════════════════════════════════
# Step 3: 输出影响分析
# ═══════════════════════════════════════════════════════════════
Write-Host "`n  ┌─────────── 影响分析 ───────────┐" -ForegroundColor White
Write-Host "  │ 变更文件数: $($changedFiles.Count)" -ForegroundColor White
Write-Host "  │ 受影响服务: $($affectedServices -join ', ')" -ForegroundColor White
Write-Host "  │ 公共库变更: $isCommonChange" -ForegroundColor White
Write-Host "  │ 前端变更:   $isFrontendChange" -ForegroundColor White
Write-Host "  │ 部署变更:   $isDockerChange" -ForegroundColor White
Write-Host "  │ 受影响工具: $($affectedTools -join ', ')" -ForegroundColor White
Write-Host "  └─────────────────────────────────┘" -ForegroundColor White

if ($affectedTools.Count -eq 0) {
    Write-Host "`n  ✅ 变更不影响任何测试工具范围，跳过执行。" -ForegroundColor Green
    exit 0
}

if ($DryRun) {
    Write-Host "`n  🔍 [DryRun] 以下工具将被执行（但当前为预览模式）:" -ForegroundColor Cyan
    foreach ($tool in $affectedTools) {
        Write-Host "    • $tool" -ForegroundColor White
    }
    exit 0
}

# ═══════════════════════════════════════════════════════════════
# Step 4: 执行增量测试
# ═══════════════════════════════════════════════════════════════
Write-Host "`n  🚀 开始执行增量测试..." -ForegroundColor Yellow

$results = @{}
$startTime = Get-Date

foreach ($tool in $affectedTools) {
    Write-Host "`n  ═══ $tool ═══" -ForegroundColor Cyan
    $toolStart = Get-Date

    try {
        & "$PSScriptRoot\run-atomic-tests.ps1" -Tool $tool -Mode atomic -MaxFiles 0 -GenerateReport
        $toolResult = "PASS"
    } catch {
        $toolResult = "FAIL"
        Write-Host "  ❌ $tool 执行失败: $_" -ForegroundColor Red
    }

    $toolEnd = Get-Date
    $results[$tool] = @{
        Status = $toolResult
        Duration = ($toolEnd - $toolStart).TotalSeconds
    }
}

$endTime = Get-Date
$totalDuration = ($endTime - $startTime).TotalSeconds

# ═══════════════════════════════════════════════════════════════
# Step 5: 生成报告
# ═══════════════════════════════════════════════════════════════
if ($GenerateReport) {
    $reportLines = @()
    $reportLines += "# 增量测试报告"
    $reportLines += ""
    $reportLines += "- **生成时间**: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')"
    $reportLines += "- **差异模式**: $DiffMode"
    $reportLines += "- **变更文件数**: $($changedFiles.Count)"
    $reportLines += "- **总耗时**: $([math]::Round($totalDuration, 1)) 秒"
    $reportLines += ""
    $reportLines += "## 影响范围"
    $reportLines += ""
    $reportLines += "| 维度 | 值 |"
    $reportLines += "|------|----|"
    $reportLines += "| 受影响服务 | $($affectedServices -join ', ') |"
    $reportLines += "| 公共库变更 | $isCommonChange |"
    $reportLines += "| 前端变更 | $isFrontendChange |"
    $reportLines += "| 受影响工具 | $($affectedTools -join ', ') |"
    $reportLines += ""
    $reportLines += "## 执行结果"
    $reportLines += ""
    $reportLines += "| 工具 | 状态 | 耗时(秒) |"
    $reportLines += "|------|------|---------|"
    foreach ($tool in $results.Keys) {
        $r = $results[$tool]
        $icon = if ($r.Status -eq "PASS") { "✅" } else { "❌" }
        $reportLines += "| $icon $tool | $($r.Status) | $([math]::Round($r.Duration, 1)) |"
    }
    $reportLines += ""
    $reportLines += "## 变更文件清单"
    $reportLines += ""
    foreach ($file in $changedFiles | Sort-Object) {
        $reportLines += "- ``$file``"
    }

    $reportLines -join "`n" | Set-Content -Path $reportFile -Encoding UTF8
    Write-Host "`n  📊 增量报告已生成: $reportFile" -ForegroundColor Green
}

# 最终汇总
Write-Host "`n╔═══════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║        增量测试执行完成                                       ║" -ForegroundColor Cyan
Write-Host "╚═══════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
$passCount = ($results.Values | Where-Object { $_.Status -eq "PASS" }).Count
$failCount = ($results.Values | Where-Object { $_.Status -eq "FAIL" }).Count
Write-Host "  总耗时: $([math]::Round($totalDuration, 1)) 秒 | 通过: $passCount | 失败: $failCount" -ForegroundColor $(if ($failCount -gt 0) { "Red" } else { "Green" })
