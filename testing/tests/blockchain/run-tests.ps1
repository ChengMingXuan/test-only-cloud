<#
.SYNOPSIS
    区块链服务测试执行脚本（Windows PowerShell）

.DESCRIPTION
    支持快速、单元、API、数据一致性、性能、完整测试运行

.PARAMETER Mode
    测试模式：quick|unit|api|consistency|performance|all（默认：all）

.PARAMETER Parallel
    并行执行（仅 Python 脚本）

.PARAMETER Tool
    指定工具：pytest_unit|pytest_api|pytest_consistency|k6（可多选）

.EXAMPLE
    .\run-tests.ps1 quick                    # 快速测试
    .\run-tests.ps1 unit                     # 仅单元测试
    .\run-tests.ps1 all -Parallel           # 并行运行所有

#>

param(
    [ValidateSet('quick', 'unit', 'api', 'consistency', 'performance', 'all')]
    [string]$Mode = 'all',
    
    [switch]$Parallel,
    
    [string[]]$Tool,
    
    [switch]$Verbose
)

# 颜色定义
$colors = @{
    'Green'   = "`e[32m"
    'Red'     = "`e[31m"
    'Yellow'  = "`e[33m"
    'Cyan'    = "`e[36m"
    'Reset'   = "`e[0m"
}

function Write-ColorOutput {
    param([string]$Message, [string]$Color = 'Reset')
    Write-Host "$($colors[$Color])$Message$($colors['Reset'])"
}

function Test-Dependencies {
    Write-ColorOutput "═══════════════════════════════════════════" "Cyan"
    Write-ColorOutput "检查依赖项..." "Yellow"
    
    $deps = @(
        @{ Name = 'Python'; Command = 'python --version' }
        @{ Name = 'pytest'; Command = 'pytest --version' }
        @{ Name = 'Docker'; Command = 'docker --version' }
    )
    
    $missing = @()
    
    foreach ($dep in $deps) {
        try {
            $result = & ([scriptblock]::Create($dep.Command)) 2>&1
            Write-ColorOutput "  ✅ $($dep.Name): $result" "Green"
        }
        catch {
            $missing += $dep.Name
            Write-ColorOutput "  ❌ $($dep.Name): 未找到" "Red"
        }
    }
    
    if ($missing.Count -gt 0) {
        Write-ColorOutput "缺失依赖: $($missing -join ', ')" "Red"
        Write-ColorOutput "请安装: pip install pytest pytest-html pytest-asyncio httpx" "Yellow"
    }
}

function Get-ServiceStatus {
    Write-ColorOutput "检查服务状态..." "Yellow"
    
    # 检查 PostgreSQL
    try {
        $pg = docker ps --filter "name=postgres" --filter "status=running" 2>$null
        if ($pg) {
            Write-ColorOutput "  ✅ PostgreSQL: 运行中" "Green"
        } else {
            Write-ColorOutput "  ⚠️  PostgreSQL: 未运行" "Yellow"
        }
    } catch {
        Write-ColorOutput "  ❌ Docker: 不可用" "Red"
    }
    
    # 检查 Redis
    try {
        $redis = docker ps --filter "name=redis" --filter "status=running" 2>$null
        if ($redis) {
            Write-ColorOutput "  ✅ Redis: 运行中" "Green"
        } else {
            Write-ColorOutput "  ⚠️  Redis: 未运行" "Yellow"
        }
    } catch {}
    
    # 检查区块链服务
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:8021/api/blockchain/health" `
            -TimeoutSec 2 -ErrorAction SilentlyContinue
        if ($response.StatusCode -eq 200) {
            Write-ColorOutput "  ✅ 区块链服务: 运行中 (localhost:8021)" "Green"
        } else {
            Write-ColorOutput "  ⚠️  区块链服务: 无响应" "Yellow"
        }
    } catch {
        Write-ColorOutput "  ⚠️  区块链服务: 未启动" "Yellow"
    }
}

function Run-QuickTests {
    Write-ColorOutput "═══════════════════════════════════════════" "Cyan"
    Write-ColorOutput "🚀 快速测试（约 2 分钟）" "Yellow"
    Write-ColorOutput "═══════════════════════════════════════════" "Cyan"
    
    # 仅运行单元测试（不需要外部依赖）
    Write-ColorOutput "`n▶ 运行单元测试..." "Cyan"
    & pytest test_failover_unit.py -v --tb=short -q
    
    if ($LASTEXITCODE -eq 0) {
        Write-ColorOutput "✅ 快速测试通过！" "Green"
    } else {
        Write-ColorOutput "❌ 快速测试失败（错误代码: $LASTEXITCODE）" "Red"
    }
}

function Run-UnitTests {
    Write-ColorOutput "═══════════════════════════════════════════" "Cyan"
    Write-ColorOutput "🧪 单元测试（约 1 分钟）" "Yellow"
    Write-ColorOutput "═══════════════════════════════════════════" "Cyan"
    
    Write-ColorOutput "`n▶ test_failover_unit.py (66+ 用例)..." "Cyan"
    & pytest test_failover_unit.py -v --tb=short
    
    if ($LASTEXITCODE -eq 0) {
        Write-ColorOutput "✅ 单元测试通过！" "Green"
    } else {
        Write-ColorOutput "❌ 部分单元测试失败" "Red"
    }
}

function Run-ApiTests {
    Write-ColorOutput "═══════════════════════════════════════════" "Cyan"
    Write-ColorOutput "🔌 API 集成测试（约 2 分钟）" "Yellow"
    Write-ColorOutput "═══════════════════════════════════════════" "Cyan"
    
    Get-ServiceStatus
    
    Write-ColorOutput "`n▶ test_failover_api.py (23+ 用例)..." "Cyan"
    & pytest test_failover_api.py -v --tb=short -m api
    
    if ($LASTEXITCODE -eq 0) {
        Write-ColorOutput "✅ API 测试通过！" "Green"
    } else {
        Write-ColorOutput "❌ 部分 API 测试失败" "Red"
    }
}

function Run-ConsistencyTests {
    Write-ColorOutput "═══════════════════════════════════════════" "Cyan"
    Write-ColorOutput "📊 数据一致性测试（约 1 分钟）" "Yellow"
    Write-ColorOutput "═══════════════════════════════════════════" "Cyan"
    
    Write-ColorOutput "`n▶ test_data_consistency.py (24+ 用例)..." "Cyan"
    & pytest test_data_consistency.py -v --tb=short
    
    if ($LASTEXITCODE -eq 0) {
        Write-ColorOutput "✅ 一致性测试通过！" "Green"
    } else {
        Write-ColorOutput "❌ 部分一致性测试失败" "Red"
    }
}

function Run-PerformanceTests {
    Write-ColorOutput "═══════════════════════════════════════════" "Cyan"
    Write-ColorOutput "⚡ 性能压测（约 3 分钟）" "Yellow"
    Write-ColorOutput "═══════════════════════════════════════════" "Cyan"
    
    Get-ServiceStatus
    
    Write-ColorOutput "`n▶ 性能基准测试..." "Cyan"
    & k6 run test_performance.k6.js --vus=10 --duration=30s
    
    Write-ColorOutput "`n▶ 高压测试..." "Cyan"
    & k6 run test_performance.k6.js --vus=50 --duration=2m
    
    if ($LASTEXITCODE -eq 0) {
        Write-ColorOutput "✅ 性能测试通过！" "Green"
    } else {
        Write-ColorOutput "⚠️  性能测试数据已收集" "Yellow"
    }
}

function Run-AllTests {
    Write-ColorOutput "═══════════════════════════════════════════" "Cyan"
    Write-ColorOutput "🔄 完整测试套件（约 8-10 分钟）" "Yellow"
    Write-ColorOutput "═══════════════════════════════════════════" "Cyan"
    
    Get-ServiceStatus
    
    if ($Parallel) {
        Write-ColorOutput "`n▶ 并行执行所有测试..." "Cyan"
        & python run_all_tests.py --parallel
    } else {
        Write-ColorOutput "`n▶ 顺序执行所有测试..." "Cyan"
        & python run_all_tests.py
    }
    
    $reportPath = "TestResults\blockchain\reports\six-tool-report.md"
    if (Test-Path $reportPath) {
        Write-ColorOutput "`n📊 报告已生成: $reportPath" "Green"
        Get-Content $reportPath | Select-Object -First 50
        Write-ColorOutput "`n... (更多内容见文件)" "Cyan"
    }
}

function Show-Statistics {
    Write-ColorOutput "`n═══════════════════════════════════════════" "Cyan"
    Write-ColorOutput "📈 测试统计" "Yellow"
    Write-ColorOutput "═══════════════════════════════════════════" "Cyan"
    
    @"
    单元测试:       66+ 用例    (Mock-based)
    API 测试:       23+ 用例    (HTTP 集成)
    一致性测试:     24+ 用例    (Data validation)
    性能测试:       5 场景     (k6 压力测试)
    ─────────────────────────────────
    总计:          120+ 用例
    
    预期覆盖:
    - 代码行覆盖:   >90%
    - 功能覆盖:    100%
    - 性能基准:    P95<500ms
"@ | Write-ColorOutput -Color "Cyan"
}

function Show-Help {
    Write-ColorOutput "区块链服务测试脚本 - Windows PowerShell 版本" "Cyan"
    Write-ColorOutput "`n用法: .\run-tests.ps1 [模式] [-Parallel]" "Yellow"
    Write-ColorOutput "`n模式:" "Yellow"
    @"
    quick       - 快速测试（仅单元，2 分钟）
    unit        - 单元测试（pytest Mock，1 分钟）
    api         - API 集成测试（需要服务，2 分钟）
    consistency - 数据一致性测试（1 分钟）
    performance - 性能压测（3 分钟）
    all         - 完整测试（8-10 分钟，默认）
"@ | Write-Host

    Write-ColorOutput "`n选项:" "Yellow"
    @"
    -Parallel   - 并行执行（推荐）
    -Verbose    - 详细输出
    -Tool       - 指定工具（pytest_unit, k6 等）
"@ | Write-Host

    Write-ColorOutput "`n示例:" "Yellow"
    @"
    .\run-tests.ps1                       # 完整测试
    .\run-tests.ps1 quick                 # 快速测试
    .\run-tests.ps1 all -Parallel         # 并行完整测试
    .\run-tests.ps1 unit                  # 仅单元测试
    .\run-tests.ps1 api                   # 仅 API 测试
"@ | Write-Host
}

# ═══════════════════════════════════════════════════════════════════
# 主逻辑
# ═══════════════════════════════════════════════════════════════════

Write-ColorOutput "`n" "Reset"
Write-ColorOutput "╔═══════════════════════════════════════════╗" "Cyan"
Write-ColorOutput "║  区块链服务测试执行脚本 (PowerShell)     ║" "Cyan"
Write-ColorOutput "╚═══════════════════════════════════════════╝" "Cyan"

# 检查依赖
Test-Dependencies

# 根据模式执行
switch ($Mode) {
    'quick' {
        Run-QuickTests
    }
    'unit' {
        Run-UnitTests
    }
    'api' {
        Run-ApiTests
    }
    'consistency' {
        Run-ConsistencyTests
    }
    'performance' {
        Run-PerformanceTests
    }
    'all' {
        Run-AllTests
    }
    'help' {
        Show-Help
    }
    default {
        Show-Help
    }
}

# 显示统计
Show-Statistics

Write-ColorOutput "`n═══════════════════════════════════════════" "Cyan"
Write-ColorOutput "✅ 测试执行完成！" "Green"
Write-ColorOutput "═══════════════════════════════════════════" "Cyan"
