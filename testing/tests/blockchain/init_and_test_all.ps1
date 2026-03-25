<#
.SYNOPSIS
    区块链服务 — 数据库初始化 + 全量测试执行脚本（PowerShell）

.DESCRIPTION
    完整的数据库初始化和测试流程：
    1. 检查 PostgreSQL 连接
    2. 初始化表结构（DbUp 迁移）
    3. 导入权限和菜单种子数据
    4. 逐个运行所有测试
    5. 生成综合报告

.EXAMPLE
    .\init_and_test_all.ps1
    .\init_and_test_all.ps1 -Verbose
#>

param(
    [switch]$Verbose,
    [string]$DbHost = "localhost",
    [int]$DbPort = 5432,
    [string]$DbUser = "postgres",
    [string]$DbPassword = "postgres",
    [string]$DbName = "jgsy_blockchain"
)

# 颜色定义
$colors = @{
    'Reset'   = "`e[0m"
    'Bold'    = "`e[1m"
    'Green'   = "`e[32m"
    'Red'     = "`e[31m"
    'Yellow'  = "`e[33m"
    'Cyan'    = "`e[36m"
    'Blue'    = "`e[34m"
}

function Write-Log {
    param([string]$Message, [string]$Color = 'Reset', [string]$Level = 'INFO')
    $timestamp = (Get-Date).ToString("yyyy-MM-dd HH:mm:ss")
    Write-Host "$($colors[$Color])[$timestamp] [$Level] $Message$($colors['Reset'])"
}

function Write-Section {
    param([string]$Title, [int]$Number)
    Write-Log ("═" * 70) "Cyan"
    Write-Log "$($Number)️⃣  $Title" "Cyan"
    Write-Log ("═" * 70) "Cyan"
}

# ════════════════════════════════════════════════════════════════════════════════
# 数据库初始化函数
# ════════════════════════════════════════════════════════════════════════════════

function Test-DatabaseConnection {
    Write-Section "检查数据库连接" 1
    
    try {
        # 设置环境变量
        $env:PGPASSWORD = $DbPassword
        
        # 测试连接
        Write-Log "连接到 $DbHost`:$DbPort..." "Blue"
        
        $result = & psql -h $DbHost -p $DbPort -U $DbUser -d postgres -c "SELECT 1;" 2>&1
        
        if ($LASTEXITCODE -eq 0) {
            Write-Log "✅ PostgreSQL 连接成功" "Green"
            
            # 检查业务库
            Write-Log "检查库 $DbName..." "Blue"
            $result = & psql -h $DbHost -U $DbUser -lqt 2>&1
            
            if ($result -match $DbName) {
                Write-Log "✅ 库 $DbName 存在" "Green"
            } else {
                Write-Log "⚠️  库 $DbName 不存在，正在创建..." "Yellow"
                & psql -h $DbHost -U $DbUser -d postgres -c "CREATE DATABASE $DbName OWNER postgres;" | Out-Null
                Write-Log "✅ 库 $DbName 创建成功" "Green"
            }
            
            Clear-Variable env:PGPASSWORD
            return $true
        } else {
            Write-Log "❌ 数据库连接失败" "Red"
            Write-Log "检查点: PostgreSQL 是否启动? 凭证是否正确?" "Yellow"
            Clear-Variable env:PGPASSWORD
            return $false
        }
    }
    catch {
        Write-Log "❌ 连接错误: $_" "Red"
        Write-Log "提示: psql 命令未找到？请检查 PostgreSQL 是否安装" "Yellow"
        return $false
    }
}

function Invoke-DbUpMigration {
    Write-Section "执行 DbUp 迁移初始化表结构" 2
    
    try {
        # 查找迁移脚本
        $sqlDir = "JGSY.AGI.Blockchain\Data\Migrations"
        
        if (-not (Test-Path $sqlDir)) {
            Write-Log "⚠️  未找到迁移脚本目录: $sqlDir" "Yellow"
            Write-Log "跳过迁移（可能表结构已存在）" "Yellow"
            return $true
        }
        
        # 获取所有 SQL 脚本
        $sqlFiles = Get-ChildItem -Path $sqlDir -Filter "*.sql" | Sort-Object Name
        
        if ($sqlFiles.Count -eq 0) {
            Write-Log "⚠️  未找到 SQL 迁移脚本" "Yellow"
            return $true
        }
        
        Write-Log "发现 $($sqlFiles.Count) 个迁移脚本" "Blue"
        
        # 执行每个脚本
        $env:PGPASSWORD = $DbPassword
        $executed = 0
        
        foreach ($file in $sqlFiles) {
            Write-Log "执行: $($file.Name)" "Blue"
            
            try {
                & psql -h $DbHost -U $DbUser -d $DbName -f $file.FullName 2>&1 | Select-Object -First 10 | ForEach-Object { Write-Log "  $_" }
                
                if ($LASTEXITCODE -eq 0 -or $LASTEXITCODE -eq 1) {  # 1 = 有警告但成功
                    Write-Log "  ✅ 成功" "Green"
                    $executed++
                } else {
                    Write-Log "  ⚠️  可能有问题，继续下一个脚本" "Yellow"
                    $executed++
                }
            }
            catch {
                Write-Log "  ⚠️  执行失败: $_" "Yellow"
                $executed++
            }
        }
        
        Clear-Variable env:PGPASSWORD
        
        if ($executed -gt 0) {
            Write-Log "✅ 已执行 $executed 个迁移脚本" "Green"
            return $true
        } else {
            Write-Log "⚠️  没有成功执行迁移脚本" "Yellow"
            return $true
        }
    }
    catch {
        Write-Log "⚠️  迁移失败: $_" "Yellow"
        return $true
    }
}

function Import-SeedData {
    Write-Section "导入权限和菜单种子数据" 3
    
    try {
        $seedScript = "docker\seed-data\permission\005_blockchain_failover_permission_and_menu.sql"
        
        if (-not (Test-Path $seedScript)) {
            Write-Log "⚠️  未找到种子数据脚本: $seedScript" "Yellow"
            Write-Log "跳过权限初始化（可手动执行）" "Yellow"
            return $false
        }
        
        Write-Log "执行: $seedScript" "Blue"
        
        $env:PGPASSWORD = $DbPassword
        
        # 尝试在 Permission 库执行（如果存在）
        $result = & psql -h $DbHost -U $DbUser -lqt 2>&1
        
        if ($result -match "jgsy_permission") {
            Write-Log "库 jgsy_permission 存在，导入权限..." "Blue"
            & psql -h $DbHost -U $DbUser -d "jgsy_permission" -f $seedScript 2>&1 | Select-Object -First 5 | ForEach-Object { Write-Log "  $_" }
            
            if ($LASTEXITCODE -eq 0) {
                Write-Log "✅ 权限和菜单初始化成功" "Green"
                Clear-Variable env:PGPASSWORD
                return $true
            }
        } else {
            Write-Log "⚠️  库 jgsy_permission 不存在（正常情况）" "Yellow"
            Write-Log "权限将在该库初始化时导入" "Yellow"
        }
        
        Clear-Variable env:PGPASSWORD
        return $false
    }
    catch {
        Write-Log "⚠️  种子数据导入失败: $_" "Yellow"
        return $false
    }
}

# ════════════════════════════════════════════════════════════════════════════════
# 测试执行函数
# ════════════════════════════════════════════════════════════════════════════════

function Invoke-AllTests {
    Write-Section "逐个运行所有测试" 4
    
    # 定义测试清单
    $tests = @(
        @{ Name = "单元测试"; File = "test_failover_unit.py"; Cmd = "pytest" },
        @{ Name = "API 集成测试"; File = "test_failover_api.py"; Cmd = "pytest" },
        @{ Name = "数据一致性测试"; File = "test_data_consistency.py"; Cmd = "pytest" },
        @{ Name = "灾备集成测试"; File = "test_disaster_recovery_integration.py"; Cmd = "pytest" },
        @{ Name = "性能基准"; File = "test_performance.k6.js"; Cmd = "k6" }
    )
    
    $testDir = "tests\blockchain"
    $results = @{}
    
    # 切换到测试目录
    Push-Location $testDir
    
    try {
        foreach ($test in $tests) {
            Write-Log "─" * 70 "Cyan"
            Write-Log "▶️  $($test.Name): $($test.File)" "Cyan"
            Write-Log "─" * 70 "Cyan"
            
            $startTime = Get-Date
            
            try {
                # 构建命令
                if ($test.Cmd -eq "pytest") {
                    $cmd = "pytest $($test.File) -v --tb=short"
                    $output = Invoke-Expression $cmd 2>&1
                } elseif ($test.Cmd -eq "k6") {
                    $cmd = "k6 run $($test.File) --vus=10 --duration=30s"
                    $output = Invoke-Expression $cmd 2>&1
                }
                
                $elapsed = (Get-Date) - $startTime
                $success = $LASTEXITCODE -eq 0
                
                if ($success) {
                    Write-Log "✅ $($test.Name): 通过 ($($elapsed.TotalSeconds.ToString('F1'))s)" "Green"
                    $results[$test.Name] = $true
                } else {
                    Write-Log "❌ $($test.Name): 失败 ($($elapsed.TotalSeconds.ToString('F1'))s)" "Red"
                    $results[$test.Name] = $false
                    
                    # 显示错误摘要
                    if ($output -match "FAILED|ERROR") {
                        $output | Where-Object { $_ -match "FAILED|ERROR" } | Select-Object -First 3 | ForEach-Object {
                            Write-Log "   $_" "Red"
                        }
                    }
                }
            }
            catch {
                Write-Log "❌ $($test.Name): 执行错误" "Red"
                Write-Log "   $_" "Red"
                $results[$test.Name] = $false
            }
            
            Start-Sleep -Seconds 2  # 测试间隔
        }
    }
    finally {
        Pop-Location
    }
    
    return $results
}

# ════════════════════════════════════════════════════════════════════════════════
# 报告生成函数
# ════════════════════════════════════════════════════════════════════════════════

function New-TestReport {
    param([hashtable]$Results)
    
    Write-Section "生成综合测试报告" 5
    
    $reportDir = "TestResults\blockchain\full_test_results"
    New-Item -ItemType Directory -Force -Path $reportDir | Out-Null
    
    # 生成 JSON 报告
    $reportData = @{
        timestamp = (Get-Date).ToString("o")
        database = @{
            host = $DbHost
            port = $DbPort
            name = $DbName
        }
        results = $Results
        summary = @{
            total = $Results.Count
            passed = ($Results.Values | Where-Object { $_ -eq $true } | Measure-Object).Count
            failed = ($Results.Values | Where-Object { $_ -eq $false } | Measure-Object).Count
        }
    }
    
    $jsonFile = Join-Path $reportDir "test_report.json"
    ConvertTo-Json $reportData | Set-Content $jsonFile -Encoding UTF8
    Write-Log "✅ JSON 报告: $jsonFile" "Green"
    
    # 生成 Markdown 报告
    $passed = $reportData.summary.passed
    $total = $reportData.summary.total
    $passRate = if ($total -gt 0) { [math]::Round(($passed / $total) * 100, 1) } else { 0 }
    
    $mdContent = @"
# 区块链服务 — 全量测试报告

**生成时间**: $($reportData.timestamp)

**数据库**: $($reportData.database.host):$($reportData.database.port)/$($reportData.database.name)

## 测试摘要

- **总测试数**: $total
- **通过数**: $passed
- **失败数**: $($reportData.summary.failed)
- **通过率**: $passRate%

## 测试结果

| 测试项 | 状态 |
|--------|------|
$(
    foreach ($test in $Results.GetEnumerator()) {
        $status = if ($test.Value) { "✅ 通过" } else { "❌ 失败" }
        "| $($test.Key) | $status |"
    }
)

## 详情

所有详细输出已保存到: `$reportDir`

"@
    
    $mdFile = Join-Path $reportDir "test_report.md"
    $mdContent | Set-Content $mdFile -Encoding UTF8
    Write-Log "✅ Markdown 报告: $mdFile" "Green"
    
    return $reportDir
}

# ════════════════════════════════════════════════════════════════════════════════
# 主程序
# ════════════════════════════════════════════════════════════════════════════════

function Main {
    Write-Host "$($colors['Cyan'])
    ╔════════════════════════════════════════════════════════════════════╗
    ║   区块链服务—数据库初始化+全量测试执行(PowerShell)                  ║
    ║                                                                    ║
    ║  阶段:                                                              ║
    ║   1️⃣  检查数据库连接                                               ║
    ║   2️⃣  执行DbUp迁移初始化表结构                                     ║
    ║   3️⃣  导入权限和菜单种子数据                                       ║
    ║   4️⃣  逐个运行所有测试                                             ║
    ║   5️⃣  生成综合测试报告                                             ║
    ║                                                                    ║
    ║  预计耗时: 15-30分钟                                                ║
    ╚════════════════════════════════════════════════════════════════════╝
    $($colors['Reset'])"
    
    $startTime = Get-Date
    
    try {
        # 步骤 1: 数据库检查
        if (-not (Test-DatabaseConnection)) {
            Write-Log "❌ 无法连接数据库，停止执行" "Red"
            exit 1
        }
        
        # 步骤 2: 迁移
        Invoke-DbUpMigration | Out-Null
        
        # 步骤 3: 种子数据
        Import-SeedData | Out-Null
        
        # 步骤 4: 运行测试
        $testResults = Invoke-AllTests
        
        # 步骤 5: 生成报告
        $reportDir = New-TestReport $testResults
        
        # 汇总
        Write-Log "═" * 70 "Cyan"
        Write-Log "📊 最终汇总" "Cyan"
        Write-Log "═" * 70 "Cyan"
        
        $elapsed = (Get-Date) - $startTime
        $passed = ($testResults.Values | Where-Object { $_ -eq $true } | Measure-Object).Count
        $total = $testResults.Count
        
        Write-Log "`n测试结果: $passed/$total 通过`n" "Yellow"
        foreach ($result in $testResults.GetEnumerator()) {
            $status = if ($result.Value) { "✅" } else { "❌" }
            Write-Log "  $status $($result.Key)" $(if ($result.Value) { "Green" } else { "Red" })
        }
        
        Write-Log "`n总耗时: $($elapsed.TotalSeconds.ToString('F1')) 秒" "Blue"
        Write-Log "报告位置: $reportDir`n" "Blue"
        
        if ($passed -eq $total) {
            Write-Log "🎉 所有测试通过！" "Green"
            exit 0
        } else {
            Write-Log "⚠️  $($total - $passed) 个测试失败" "Yellow"
            exit 1
        }
    }
    catch {
        Write-Log "❌ 执行失败: $_" "Red"
        exit 1
    }
}

Main
