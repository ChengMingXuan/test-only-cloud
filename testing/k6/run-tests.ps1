#!/usr/bin/env pwsh
# K6性能测试运行脚本
# 用法: .\run-tests.ps1 -TestType <smoke|load|stress|spike|soak> [-BaseUrl <url>]

param(
    [Parameter(Mandatory=$true)]
    [ValidateSet('smoke', 'load', 'stress', 'spike', 'soak', 'all')]
    [string]$TestType,
    
    [Parameter(Mandatory=$false)]
    [string]$BaseUrl = "http://localhost:8000",
    
    [Parameter(Mandatory=$false)]
    [string]$OutputDir = "results",
    
    [Parameter(Mandatory=$false)]
    [switch]$WithInfluxDB,
    
    [Parameter(Mandatory=$false)]
    [switch]$WithPrometheus,
    
    [Parameter(Mandatory=$false)]
    [switch]$VerboseOutput
)

# 颜色输出
function Write-ColorOutput {
    param(
        [string]$Message,
        [string]$Color = "White"
    )
    Write-Host $Message -ForegroundColor $Color
}

# 检查K6是否安装
function Test-K6Installed {
    try {
        $version = k6 version 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-ColorOutput "✓ K6 已安装: $version" "Green"
            return $true
        }
    } catch {
        Write-ColorOutput "✗ K6 未安装" "Red"
        Write-ColorOutput "请运行: choco install k6" "Yellow"
        return $false
    }
}

# 创建输出目录
function New-OutputDirectory {
    if (-not (Test-Path $OutputDir)) {
        New-Item -ItemType Directory -Path $OutputDir | Out-Null
        Write-ColorOutput "✓ 创建输出目录: $OutputDir" "Green"
    }
}

# 运行单个测试
function Invoke-K6Test {
    param(
        [string]$ScenarioFile,
        [string]$TestName
    )
    
    Write-ColorOutput "`n========================================" "Cyan"
    Write-ColorOutput "🚀 运行测试: $TestName" "Cyan"
    Write-ColorOutput "========================================" "Cyan"
    Write-ColorOutput "目标: $BaseUrl" "Gray"
    Write-ColorOutput "时间: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')" "Gray"
    Write-ColorOutput ""
    
    # 构建K6命令
    $timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
    $outputFile = "$OutputDir/${TestName}_${timestamp}.json"
    
    $k6Args = @(
        "run"
        "--env", "BASE_URL=$BaseUrl"
        "--out", "json=$outputFile"
    )
    
    # InfluxDB输出
    if ($WithInfluxDB) {
        $k6Args += "--out"
        $k6Args += "influxdb=http://localhost:8086/k6"
    }
    
    # Prometheus输出
    if ($WithPrometheus) {
        $k6Args += "--out"
        $k6Args += "experimental-prometheus-rw=http://localhost:9090/api/v1/write"
    }
    
    # 详细输出
    if ($VerboseOutput) {
        $k6Args += "--http-debug"
    }
    
    $k6Args += $ScenarioFile
    
    # 运行测试
    $startTime = Get-Date
    & k6 @k6Args
    $exitCode = $LASTEXITCODE
    $endTime = Get-Date
    $duration = $endTime - $startTime
    
    if ($exitCode -eq 0) {
        Write-ColorOutput "`n✅ 测试完成: $TestName" "Green"
        Write-ColorOutput "耗时: $($duration.ToString('mm\:ss'))" "Green"
        Write-ColorOutput "结果保存到: $outputFile" "Green"
    } else {
        Write-ColorOutput "`n❌ 测试失败: $TestName" "Red"
        Write-ColorOutput "退出码: $exitCode" "Red"
    }
    
    return $exitCode
}

# 主函数
function Main {
    Write-ColorOutput @"
╔════════════════════════════════════════════╗
║   JGSY AGI Platform - K6 性能测试工具       ║
╚════════════════════════════════════════════╝
"@ "Cyan"
    
    # 检查K6
    if (-not (Test-K6Installed)) {
        exit 1
    }
    
    # 创建输出目录
    New-OutputDirectory
    
    # 定义测试场景
    $scenarios = @{
        'smoke' = @{
            File = 'scenarios/smoke-test.js'
            Name = 'smoke-test'
            Description = '冒烟测试 (10 VUs, 3分钟)'
        }
        'load' = @{
            File = 'scenarios/load-test.js'
            Name = 'load-test'
            Description = '负载测试 (200 VUs, 16分钟)'
        }
        'stress' = @{
            File = 'scenarios/stress-test.js'
            Name = 'stress-test'
            Description = '压力测试 (1000 VUs, 23分钟)'
        }
        'spike' = @{
            File = 'scenarios/spike-test.js'
            Name = 'spike-test'
            Description = '峰值测试 (2000 VUs峰值, 5分钟)'
        }
        'soak' = @{
            File = 'scenarios/soak-test.js'
            Name = 'soak-test'
            Description = '浸泡测试 (200 VUs, 70分钟)'
        }
    }
    
    $exitCodes = @()
    
    # 运行测试
    if ($TestType -eq 'all') {
        Write-ColorOutput "运行所有测试场景..." "Yellow"
        foreach ($scenario in $scenarios.Keys) {
            $info = $scenarios[$scenario]
            Write-ColorOutput "`n→ $($info.Description)" "Gray"
            $exitCode = Invoke-K6Test -ScenarioFile $info.File -TestName $info.Name
            $exitCodes += $exitCode
            
            if ($scenario -ne 'soak') {
                Write-ColorOutput "等待30秒后开始下一个测试..." "Gray"
                Start-Sleep -Seconds 30
            }
        }
    } else {
        $info = $scenarios[$TestType]
        Write-ColorOutput "→ $($info.Description)" "Gray"
        $exitCode = Invoke-K6Test -ScenarioFile $info.File -TestName $info.Name
        $exitCodes += $exitCode
    }
    
    # 汇总结果
    Write-ColorOutput "`n========================================" "Cyan"
    Write-ColorOutput "📊 测试汇总" "Cyan"
    Write-ColorOutput "========================================" "Cyan"
    
    $successCount = ($exitCodes | Where-Object { $_ -eq 0 }).Count
    $failCount = ($exitCodes | Where-Object { $_ -ne 0 }).Count
    
    Write-ColorOutput "成功: $successCount" "Green"
    Write-ColorOutput "失败: $failCount" "Red"
    Write-ColorOutput "总计: $($exitCodes.Count)" "Gray"
    
    if ($failCount -eq 0) {
        Write-ColorOutput "`n✅ 所有测试通过！" "Green"
        exit 0
    } else {
        Write-ColorOutput "`n❌ 部分测试失败！" "Red"
        exit 1
    }
}

# 切换到K6目录
$k6Dir = Join-Path $PSScriptRoot "k6"
if (Test-Path $k6Dir) {
    Push-Location $k6Dir
}

try {
    Main
} finally {
    Pop-Location
}
