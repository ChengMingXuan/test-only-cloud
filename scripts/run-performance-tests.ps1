#!/usr/bin/env pwsh
<#
.SYNOPSIS
    JGSY AGI 性能测试执行脚本
.DESCRIPTION
    封装 k6 性能测试的执行，支持多种测试场景和输出格式
.PARAMETER Scenario
    测试场景: smoke, load, stress, spike, comprehensive, digital-twin, blockchain
.PARAMETER Duration
    测试持续时间（覆盖默认配置）
.PARAMETER VUs
    虚拟用户数（覆盖默认配置）
.PARAMETER BaseUrl
    API 基础 URL
.PARAMETER OutputFormat
    输出格式: console, json, html, influxdb
.PARAMETER InfluxDBUrl
    InfluxDB 地址（用于指标存储）
#>

param(
    [ValidateSet('smoke', 'load', 'stress', 'spike', 'comprehensive', 'digital-twin', 'blockchain', 'all')]
    [string]$Scenario = 'smoke',
    
    [string]$Duration = '',
    [int]$VUs = 0,
    [string]$BaseUrl = 'http://localhost:5000',
    [string]$TenantId = 'default',
    
    [ValidateSet('console', 'json', 'html', 'influxdb', 'all')]
    [string]$OutputFormat = 'console',
    
    [string]$InfluxDBUrl = 'http://localhost:8086/write?db=k6',
    [switch]$NoThresholds,
    [switch]$Verbose
)

$ErrorActionPreference = "Stop"

Write-Host @"
╔═══════════════════════════════════════════════════════════════╗
║            JGSY AGI 性能测试执行工具                          ║
║                    版本: 1.1.0                               ║
╚═══════════════════════════════════════════════════════════════╝
"@ -ForegroundColor Cyan

# 检查 k6 是否安装
$k6Version = k6 version 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ k6 未安装。请先安装 k6:" -ForegroundColor Red
    Write-Host "   Windows: choco install k6" -ForegroundColor Yellow
    Write-Host "   或访问: https://k6.io/docs/getting-started/installation/" -ForegroundColor Yellow
    exit 1
}
Write-Host "✅ k6 版本: $k6Version" -ForegroundColor Green

# 创建结果目录
$resultsDir = "testing/k6/results"
if (-not (Test-Path $resultsDir)) {
    New-Item -ItemType Directory -Path $resultsDir -Force | Out-Null
}

# 测试场景映射
$scenarioFiles = @{
    'smoke'         = 'testing/k6/scenarios/smoke-test.js'
    'load'          = 'testing/k6/scenarios/load-test.js'
    'stress'        = 'testing/k6/scenarios/stress-test.js'
    'comprehensive' = 'testing/k6/scenarios/comprehensive-test.js'
    'digital-twin'  = 'testing/k6/scenarios/digital-twin-test.js'
    'blockchain'    = 'testing/k6/scenarios/blockchain-test.js'
}

# 构建 k6 命令参数
function Build-K6Args {
    param(
        [string]$TestFile,
        [string]$ScenarioName
    )
    
    $args = @()
    
    # 基础参数
    $args += "run"
    
    # 环境变量
    $args += "-e", "BASE_URL=$BaseUrl"
    $args += "-e", "TENANT_ID=$TenantId"
    $args += "-e", "SCENARIO=$ScenarioName"
    
    # 覆盖持续时间
    if ($Duration) {
        $args += "--duration", $Duration
    }
    
    # 覆盖 VUs
    if ($VUs -gt 0) {
        $args += "--vus", $VUs
    }
    
    # 禁用阈值检查
    if ($NoThresholds) {
        $args += "--no-thresholds"
    }
    
    # 详细输出
    if ($Verbose) {
        $args += "--verbose"
    }
    
    # 输出格式
    $timestamp = Get-Date -Format "yyyyMMdd-HHmmss"
    
    switch ($OutputFormat) {
        'json' {
            $args += "--out", "json=$resultsDir/${ScenarioName}-${timestamp}.json"
        }
        'influxdb' {
            $args += "--out", "influxdb=$InfluxDBUrl"
        }
        'all' {
            $args += "--out", "json=$resultsDir/${ScenarioName}-${timestamp}.json"
            if ($InfluxDBUrl) {
                $args += "--out", "influxdb=$InfluxDBUrl"
            }
        }
    }
    
    # 测试文件
    $args += $TestFile
    
    return $args
}

# 执行单个测试
function Run-Test {
    param(
        [string]$ScenarioName,
        [string]$TestFile
    )
    
    Write-Host "`n📋 执行测试场景: $ScenarioName" -ForegroundColor Cyan
    Write-Host "   测试文件: $TestFile" -ForegroundColor Gray
    Write-Host "   目标 URL: $BaseUrl" -ForegroundColor Gray
    Write-Host "   租户 ID: $TenantId" -ForegroundColor Gray
    
    if (-not (Test-Path $TestFile)) {
        Write-Host "❌ 测试文件不存在: $TestFile" -ForegroundColor Red
        return $false
    }
    
    $k6Args = Build-K6Args -TestFile $TestFile -ScenarioName $ScenarioName
    
    Write-Host "`n🚀 启动测试..." -ForegroundColor Yellow
    Write-Host "   命令: k6 $($k6Args -join ' ')" -ForegroundColor Gray
    
    $startTime = Get-Date
    
    # 执行 k6
    & k6 @k6Args
    $exitCode = $LASTEXITCODE
    
    $endTime = Get-Date
    $duration = $endTime - $startTime
    
    Write-Host "`n⏱️ 测试耗时: $($duration.TotalSeconds.ToString('F2')) 秒" -ForegroundColor Gray
    
    if ($exitCode -eq 0) {
        Write-Host "✅ 测试通过: $ScenarioName" -ForegroundColor Green
        return $true
    } else {
        Write-Host "❌ 测试失败: $ScenarioName (退出码: $exitCode)" -ForegroundColor Red
        return $false
    }
}

# 执行健康检查
function Test-ServiceHealth {
    Write-Host "`n🏥 检查服务健康状态..." -ForegroundColor Yellow
    
    try {
        $response = Invoke-RestMethod -Uri "$BaseUrl/health" -Method Get -TimeoutSec 10
        Write-Host "✅ 服务健康检查通过" -ForegroundColor Green
        return $true
    }
    catch {
        Write-Host "❌ 服务不可用: $BaseUrl" -ForegroundColor Red
        Write-Host "   错误: $($_.Exception.Message)" -ForegroundColor Red
        return $false
    }
}

# 主执行逻辑
Write-Host "`n📊 测试配置:" -ForegroundColor Cyan
Write-Host "   场景: $Scenario" -ForegroundColor Gray
Write-Host "   URL: $BaseUrl" -ForegroundColor Gray
Write-Host "   输出: $OutputFormat" -ForegroundColor Gray

# 健康检查
if (-not (Test-ServiceHealth)) {
    Write-Host "`n⚠️ 服务不可用，是否继续测试? (y/N)" -ForegroundColor Yellow
    $continue = Read-Host
    if ($continue -ne 'y' -and $continue -ne 'Y') {
        exit 1
    }
}

# 执行测试
$results = @{}

if ($Scenario -eq 'all') {
    # 执行所有测试
    foreach ($scenarioName in $scenarioFiles.Keys) {
        $testFile = $scenarioFiles[$scenarioName]
        $results[$scenarioName] = Run-Test -ScenarioName $scenarioName -TestFile $testFile
        
        # 测试间隔
        Write-Host "`n⏸️ 等待 10 秒后执行下一个测试..." -ForegroundColor Gray
        Start-Sleep -Seconds 10
    }
} elseif ($Scenario -eq 'spike') {
    # spike 测试使用 stress-test.js 但配置不同
    $results[$Scenario] = Run-Test -ScenarioName $Scenario -TestFile 'testing/k6/scenarios/stress-test.js'
} else {
    $testFile = $scenarioFiles[$Scenario]
    if ($testFile) {
        $results[$Scenario] = Run-Test -ScenarioName $Scenario -TestFile $testFile
    } else {
        Write-Host "❌ 未知测试场景: $Scenario" -ForegroundColor Red
        exit 1
    }
}

# 汇总结果
Write-Host @"

╔═══════════════════════════════════════════════════════════════╗
║                      测试结果汇总                              ║
╚═══════════════════════════════════════════════════════════════╝
"@ -ForegroundColor Cyan

$passCount = 0
$failCount = 0

foreach ($scenarioName in $results.Keys) {
    $passed = $results[$scenarioName]
    if ($passed) {
        Write-Host "  ✅ $scenarioName" -ForegroundColor Green
        $passCount++
    } else {
        Write-Host "  ❌ $scenarioName" -ForegroundColor Red
        $failCount++
    }
}

Write-Host "`n📈 总计: $passCount 通过, $failCount 失败" -ForegroundColor $(if ($failCount -gt 0) { "Yellow" } else { "Green" })

# 列出生成的报告
$reports = Get-ChildItem -Path $resultsDir -Filter "*.json" -ErrorAction SilentlyContinue | Sort-Object LastWriteTime -Descending | Select-Object -First 5
if ($reports.Count -gt 0) {
    Write-Host "`n📄 最近生成的报告:" -ForegroundColor Cyan
    foreach ($report in $reports) {
        Write-Host "   - $($report.Name)" -ForegroundColor Gray
    }
}

# 退出码
if ($failCount -gt 0) {
    exit 1
} else {
    exit 0
}
