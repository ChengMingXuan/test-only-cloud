<#
.SYNOPSIS
    首批业务域核心链路冒烟门禁 - TEST-P1-003 / IMP-P1-004 实现
.DESCRIPTION
    验证首批上线域（充电运维、光储充）的 10 条核心链路可用性
.PARAMETER BaseUrl
    网关地址
.PARAMETER Token
    JWT Token（可选，脚本会自动获取）
.PARAMETER OutputPath
    结果输出路径
#>
param(
    [string]$BaseUrl = 'http://localhost:5000',
    [string]$Token = '',
    [string]$OutputPath = 'TestResults/reports/business-smoke-report.json'
)

$ErrorActionPreference = 'Continue'
$startTime = Get-Date

Write-Host "`n=============================" -ForegroundColor Cyan
Write-Host "  首批业务域链路冒烟测试" -ForegroundColor Cyan
Write-Host "  目标: $BaseUrl" -ForegroundColor Cyan
Write-Host "=============================" -ForegroundColor Cyan

# 自动获取 Token（可选）
if (-not $Token) {
    try {
        $loginBody = @{
            username = 'admin'
            password = $env:ADMIN_PASSWORD
        } | ConvertTo-Json
        $loginResp = Invoke-RestMethod -Uri "$BaseUrl/api/identity/auth/login" -Method POST -Body $loginBody -ContentType 'application/json' -ErrorAction Stop
        $Token = $loginResp.data.token
        if ($Token) {
            Write-Host "  ✅ 自动获取 Token 成功" -ForegroundColor Green
        }
    } catch {
        Write-Host "  ⚠️ 无法自动获取 Token，将以匿名方式测试" -ForegroundColor Yellow
    }
}

$headers = @{ 'Content-Type' = 'application/json' }
if ($Token) { $headers['Authorization'] = "Bearer $Token" }

function Test-Endpoint {
    param(
        [string]$Name,
        [string]$Method,
        [string]$Url,
        [int]$ExpectedStatus = 200,
        [string]$Body = $null
    )

    $result = @{
        Name    = $Name
        Method  = $Method
        Url     = $Url
        Status  = 'FAIL'
        Code    = 0
        Latency = 0
        Detail  = ''
    }

    try {
        $sw = [System.Diagnostics.Stopwatch]::StartNew()
        $params = @{
            Uri             = "$BaseUrl$Url"
            Method          = $Method
            Headers         = $headers
            ErrorAction     = 'Stop'
            TimeoutSec      = 30
        }
        if ($Body) { $params['Body'] = $Body }

        $resp = Invoke-WebRequest @params
        $sw.Stop()

        $result.Code = $resp.StatusCode
        $result.Latency = $sw.ElapsedMilliseconds
        if ($resp.StatusCode -eq $ExpectedStatus -or ($resp.StatusCode -ge 200 -and $resp.StatusCode -lt 300)) {
            $result.Status = 'PASS'
            $result.Detail = "HTTP $($resp.StatusCode) - ${([math]::Round($sw.ElapsedMilliseconds))}ms"
        } else {
            $result.Detail = "期望 $ExpectedStatus, 实际 $($resp.StatusCode)"
        }
    } catch {
        $result.Detail = $_.Exception.Message
        if ($_.Exception.Response) {
            $result.Code = [int]$_.Exception.Response.StatusCode
        }
    }

    $icon = if ($result.Status -eq 'PASS') { '✅' } else { '❌' }
    Write-Host "  $icon $Name [$Method] $Url → $($result.Detail)" -ForegroundColor $(if ($result.Status -eq 'PASS') { 'Green' } else { 'Red' })

    return $result
}

# 10 条核心链路定义
$smokeTests = @(
    # === 平台基础 ===
    @{ Name = '健康检查-网关';         Method = 'GET';  Url = '/health' },
    @{ Name = '登录认证';              Method = 'POST'; Url = '/api/identity/auth/login'; Body = '{"username":"admin","password":"test"}'; ExpectedStatus = 200 },
    @{ Name = '租户列表';              Method = 'GET';  Url = '/api/tenant/tenants' },
    @{ Name = '用户信息';              Method = 'GET';  Url = '/api/account/users/current' },
    @{ Name = '权限菜单';              Method = 'GET';  Url = '/api/permission/menus/tree' },

    # === 充电运维核心链路 ===
    @{ Name = '设备列表';              Method = 'GET';  Url = '/api/device/devices?pageIndex=1&pageSize=10' },
    @{ Name = '场站列表';              Method = 'GET';  Url = '/api/station/stations?pageIndex=1&pageSize=10' },
    @{ Name = '充电订单列表';          Method = 'GET';  Url = '/api/charging/orders?pageIndex=1&pageSize=10' },

    # === 光储充核心链路 ===
    @{ Name = '数据采集状态';          Method = 'GET';  Url = '/api/ingestion/status' },
    @{ Name = '分析看板';              Method = 'GET';  Url = '/api/analytics/dashboards' }
)

$results = @()
$passed = 0
$failed = 0

foreach ($test in $smokeTests) {
    $body = if ($test.ContainsKey('Body')) { $test.Body } else { $null }
    $expected = if ($test.ContainsKey('ExpectedStatus')) { $test.ExpectedStatus } else { 200 }
    $r = Test-Endpoint -Name $test.Name -Method $test.Method -Url $test.Url -ExpectedStatus $expected -Body $body
    $results += $r
    if ($r.Status -eq 'PASS') { $passed++ } else { $failed++ }
}

$endTime = Get-Date
$duration = ($endTime - $startTime).TotalSeconds

# 生成报告
$outputDir = Split-Path $OutputPath
if ($outputDir -and -not (Test-Path $outputDir)) { New-Item -ItemType Directory -Path $outputDir -Force | Out-Null }

$report = @{
    tool      = 'business-smoke'
    timestamp = (Get-Date -Format 'yyyy-MM-ddTHH:mm:ss')
    duration  = [math]::Round($duration, 1)
    summary   = @{
        total       = $results.Count
        passed      = $passed
        failed      = $failed
        passRate    = [math]::Round($passed / [math]::Max($results.Count, 1) * 100, 1)
        status      = if ($failed -eq 0) { 'PASS' } else { 'FAIL' }
    }
    chains = $results | ForEach-Object {
        @{
            name    = $_.Name
            method  = $_.Method
            url     = $_.Url
            status  = $_.Status
            code    = $_.Code
            latency = $_.Latency
            detail  = $_.Detail
        }
    }
} | ConvertTo-Json -Depth 4

Set-Content -Path $OutputPath -Value $report -Encoding UTF8

$gateStatus = if ($failed -eq 0) { 'PASS' } else { 'FAIL' }
Write-Host "`n=============================" -ForegroundColor Cyan
Write-Host "  冒烟测试结果: $gateStatus ($passed/$($results.Count))" -ForegroundColor $(if ($gateStatus -eq 'PASS') { 'Green' } else { 'Red' })
Write-Host "  报告: $OutputPath" -ForegroundColor Cyan
Write-Host "=============================" -ForegroundColor Cyan

exit $failed
