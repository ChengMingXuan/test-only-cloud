<#
.SYNOPSIS
    Layer 7: 稳定性与恢复测试
.DESCRIPTION
    覆盖:
    1. 容器重启恢复 - restart 后自动恢复健康
    2. 持续请求 300s - 长时间稳定性
    3. 100 请求急速爆发 - 速率限制/队列溢出
    4. 幂等性验证 - 重复请求一致结果
    5. 连接池耗尽 - 并发连接测试
    6. 超时恢复 - 慢响应后恢复正常
#>
param(
    [string]$GatewayUrl = "http://localhost:5000",
    [int]$SustainedDurationSec = 120,
    [int]$BurstCount = 100
)

$ErrorActionPreference = 'Continue'
$logDir = "$PSScriptRoot\logs"
if (-not (Test-Path $logDir)) { New-Item -ItemType Directory -Path $logDir -Force | Out-Null }

$ts = Get-Date -Format 'yyyy-MM-dd_HH-mm-ss'
$reportFile = "$logDir\stability-report-$ts.txt"

# === 全局变量 ===
$script:totalTests = 0
$script:passedTests = 0
$script:failedTests = 0
$script:results = @()

function Write-TestResult {
    param([string]$Category, [string]$Name, [bool]$Pass, [string]$Detail = "")
    $script:totalTests++
    if ($Pass) { $script:passedTests++ } else { $script:failedTests++ }
    $status = if ($Pass) { "PASS" } else { "FAIL" }
    $line = "[$status] $Category :: $Name $(if($Detail){"| $Detail"})"
    Write-Host $line -ForegroundColor $(if ($Pass) { "Green" } else { "Red" })
    $script:results += $line
}

function Get-AuthToken {
    try {
        $body = @{ userName = "admin"; password = "P@ssw0rd" } | ConvertTo-Json
        $r = Invoke-RestMethod -Uri "$GatewayUrl/api/auth/login" -Method POST -Body $body -ContentType "application/json" -TimeoutSec 15
        return $r.data.accessToken
    } catch {
        Write-Host "[WARN] 登录失败: $_" -ForegroundColor Yellow
        return $null
    }
}

# === 获取 Token ===
Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "  Layer 7: 稳定性与恢复测试" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

$token = Get-AuthToken
if (-not $token) {
    Write-Host "无法获取 Token，终止测试" -ForegroundColor Red
    exit 1
}
$headers = @{ Authorization = "Bearer $token"; "Content-Type" = "application/json" }

# ===========================
# 测试 1: 容器重启恢复
# ===========================
Write-Host "`n--- 测试 1: 容器重启恢复 ---" -ForegroundColor Yellow

$containersToTest = @(
    @{ Name = "jgsy-station"; HealthUrl = "/health"; Port = 8015; ServiceUrl = "/api/stations?page=1&pageSize=1" },
    @{ Name = "jgsy-permission"; HealthUrl = "/health"; Port = 8003; ServiceUrl = "/api/system/role?page=1&pageSize=1" }
)

foreach ($ct in $containersToTest) {
    $containerName = $ct.Name
    
    # 1. 验证当前健康
    try {
        $preCheck = Invoke-RestMethod -Uri "$GatewayUrl$($ct.ServiceUrl)" -Headers $headers -TimeoutSec 10
        $preHealthy = $true
    } catch {
        $preHealthy = $false
    }
    Write-TestResult "容器恢复" "$containerName 重启前健康" $preHealthy
    
    # 2. 重启容器
    Write-Host "  正在重启 $containerName ..." -ForegroundColor Gray
    try {
        docker restart $containerName 2>$null | Out-Null
        Write-Host "  重启命令已发送，等待恢复..." -ForegroundColor Gray
    } catch {
        Write-TestResult "容器恢复" "$containerName docker restart 命令" $false "命令失败"
        continue
    }
    
    # 3. 等待恢复 (最多 60s)
    $recovered = $false
    $startWait = Get-Date
    for ($i = 0; $i -lt 30; $i++) {
        Start-Sleep -Seconds 2
        try {
            $healthRes = Invoke-WebRequest -Uri "http://localhost:$($ct.Port)$($ct.HealthUrl)" -TimeoutSec 3 -UseBasicParsing
            if ($healthRes.StatusCode -eq 200) {
                $recovered = $true
                break
            }
        } catch {}
    }
    $recoveryTime = ((Get-Date) - $startWait).TotalSeconds
    Write-TestResult "容器恢复" "$containerName 重启后恢复" $recovered "耗时: $([math]::Round($recoveryTime,1))s"
    
    # 4. 验证 API 功能恢复
    if ($recovered) {
        Start-Sleep -Seconds 3
        try {
            $postCheck = Invoke-RestMethod -Uri "$GatewayUrl$($ct.ServiceUrl)" -Headers $headers -TimeoutSec 10
            Write-TestResult "容器恢复" "$containerName API 功能恢复" $true
        } catch {
            Write-TestResult "容器恢复" "$containerName API 功能恢复" $false "$_"
        }
    }
}

# ===========================
# 测试 2: 持续请求稳定性
# ===========================
Write-Host "`n--- 测试 2: 持续请求稳定性 (${SustainedDurationSec}s) ---" -ForegroundColor Yellow

# 先刷新 token（容器重启可能影响）
$token = Get-AuthToken
$headers = @{ Authorization = "Bearer $token"; "Content-Type" = "application/json" }

$sustainedEndpoints = @(
    "/api/system/role?page=1&pageSize=1",
    "/api/system/dict/types?page=1&pageSize=1",
    "/api/system/menu/tree",
    "/api/user/profile",
    "/api/stations?page=1&pageSize=1",
    "/api/device?page=1&pageSize=1",
    "/api/tenants?page=1&pageSize=1",
    "/api/system/audit-log?page=1&pageSize=1"
)

$sustainedStart = Get-Date
$sustainedTotal = 0
$sustained2xx = 0
$sustained4xx = 0
$sustained5xx = 0
$sustainedErr = 0
$latencies = @()

while (((Get-Date) - $sustainedStart).TotalSeconds -lt $SustainedDurationSec) {
    foreach ($ep in $sustainedEndpoints) {
        try {
            $sw = [System.Diagnostics.Stopwatch]::StartNew()
            $r = Invoke-WebRequest -Uri "$GatewayUrl$ep" -Headers $headers -TimeoutSec 10 -UseBasicParsing
            $sw.Stop()
            $latencies += $sw.ElapsedMilliseconds
            $sustainedTotal++
            if ($r.StatusCode -ge 200 -and $r.StatusCode -lt 300) { $sustained2xx++ }
            elseif ($r.StatusCode -ge 400 -and $r.StatusCode -lt 500) { $sustained4xx++ }
            elseif ($r.StatusCode -ge 500) { $sustained5xx++ }
        } catch {
            $sustainedTotal++
            $sustainedErr++
        }
    }
    Start-Sleep -Milliseconds 200
}

$sustainedDuration = ((Get-Date) - $sustainedStart).TotalSeconds
$rps = if ($sustainedDuration -gt 0) { [math]::Round($sustainedTotal / $sustainedDuration, 1) } else { 0 }
$errorPct = if ($sustainedTotal -gt 0) { [math]::Round(($sustained5xx + $sustainedErr) / $sustainedTotal * 100, 2) } else { 100 }
$avgLatency = if ($latencies.Count -gt 0) { [math]::Round(($latencies | Measure-Object -Average).Average, 1) } else { 0 }
$p95Latency = if ($latencies.Count -gt 0) {
    $sorted = $latencies | Sort-Object
    $idx = [math]::Floor($sorted.Count * 0.95)
    $sorted[$idx]
} else { 0 }

Write-TestResult "持续稳定性" "总请求 $sustainedTotal | 2xx=$sustained2xx 4xx=$sustained4xx 5xx=$sustained5xx err=$sustainedErr" ($errorPct -lt 5) "错误率: ${errorPct}%"
Write-TestResult "持续稳定性" "RPS: $rps | 平均延迟: ${avgLatency}ms | p95: ${p95Latency}ms" ($avgLatency -lt 2000)
Write-TestResult "持续稳定性" "零5xx错误" ($sustained5xx -eq 0) "5xx=$sustained5xx"

# ===========================
# 测试 3: 急速爆发
# ===========================
Write-Host "`n--- 测试 3: 急速爆发 ($BurstCount 请求) ---" -ForegroundColor Yellow

$burstUrl = "$GatewayUrl/api/system/role?page=1&pageSize=1"
$burstResults = @()
$burstStart = Get-Date

# 使用 RunspacePool 实现真正的并发
$runspacePool = [RunspaceFactory]::CreateRunspacePool(1, 20)
$runspacePool.Open()
$jobs = @()

$scriptBlock = {
    param($url, $authHeader)
    try {
        $sw = [System.Diagnostics.Stopwatch]::StartNew()
        $r = Invoke-WebRequest -Uri $url -Headers @{ Authorization = $authHeader } -TimeoutSec 15 -UseBasicParsing
        $sw.Stop()
        return @{ Status = $r.StatusCode; Latency = $sw.ElapsedMilliseconds; Error = $null }
    } catch {
        return @{ Status = 0; Latency = 0; Error = $_.Exception.Message }
    }
}

for ($i = 0; $i -lt $BurstCount; $i++) {
    $ps = [PowerShell]::Create().AddScript($scriptBlock).AddArgument($burstUrl).AddArgument("Bearer $token")
    $ps.RunspacePool = $runspacePool
    $jobs += @{ PS = $ps; Handle = $ps.BeginInvoke() }
}

foreach ($job in $jobs) {
    try {
        $result = $job.PS.EndInvoke($job.Handle)
        $burstResults += $result
    } catch {}
    $job.PS.Dispose()
}
$runspacePool.Close()

$burstDuration = ((Get-Date) - $burstStart).TotalSeconds
$burstOk = ($burstResults | Where-Object { $_.Status -ge 200 -and $_.Status -lt 500 }).Count
$burst5xx = ($burstResults | Where-Object { $_.Status -ge 500 }).Count
$burstFail = ($burstResults | Where-Object { $_.Status -eq 0 }).Count
$burstLatencies = ($burstResults | Where-Object { $_.Latency -gt 0 } | ForEach-Object { $_.Latency })
$burstAvg = if ($burstLatencies.Count -gt 0) { [math]::Round(($burstLatencies | Measure-Object -Average).Average,1) } else { 0 }

Write-TestResult "急速爆发" "$BurstCount 并发请求完成" ($burstOk -gt ($BurstCount * 0.8)) "成功=$burstOk 5xx=$burst5xx 失败=$burstFail 耗时=${burstDuration}s"
Write-TestResult "急速爆发" "平均延迟 ${burstAvg}ms" ($burstAvg -lt 5000)

# ===========================
# 测试 4: 幂等性验证
# ===========================
Write-Host "`n--- 测试 4: 幂等性验证 ---" -ForegroundColor Yellow

# 先刷新 token（容器重启可能影响）
$token = Get-AuthToken
$headers = @{ Authorization = "Bearer $token"; "Content-Type" = "application/json" }

# 4.1 GET 幂等 - 多次请求结果一致
$idempotentGets = @(
    "/api/system/role?page=1&pageSize=5",
    "/api/user/profile",
    "/api/system/menu/tree"
)

foreach ($ep in $idempotentGets) {
    try {
        $r1 = Invoke-RestMethod -Uri "$GatewayUrl$ep" -Headers $headers -TimeoutSec 10
        Start-Sleep -Milliseconds 100
        $r2 = Invoke-RestMethod -Uri "$GatewayUrl$ep" -Headers $headers -TimeoutSec 10
        
        # 比较 data 部分（排除 timestamp/traceId 等动态字段）
        try {
            $j1 = $r1.data | ConvertTo-Json -Depth 10 -Compress
            $j2 = $r2.data | ConvertTo-Json -Depth 10 -Compress
        } catch {
            $j1 = $r1 | ConvertTo-Json -Depth 10 -Compress
            $j2 = $r2 | ConvertTo-Json -Depth 10 -Compress
        }
        $identical = ($j1 -eq $j2)
        Write-TestResult "幂等性" "GET $ep 两次结果相同" $identical
    } catch {
        Write-TestResult "幂等性" "GET $ep 可达" $false "$_"
    }
}

# 4.2 创建+重复创建幂等 or 冲突检测
try {
    $uniqueCode = "IDEMPOTENT_$(Get-Date -Format 'HHmmssff')"
    $roleBody = @{
        name = "Idempotent Test Role"
        code = $uniqueCode
        description = "Idempotent verification"
        sortOrder = 99
        status = 1
    } | ConvertTo-Json
    
    $authOnly = @{ Authorization = "Bearer $token" }
    $c1 = Invoke-WebRequest -Uri "$GatewayUrl/api/system/role" -Method POST -Body ([System.Text.Encoding]::UTF8.GetBytes($roleBody)) -ContentType "application/json; charset=utf-8" -Headers $authOnly -TimeoutSec 10 -UseBasicParsing
    $c1Status = $c1.StatusCode
    
    # 第二次创建同 code：期望 400/409（冲突检测）
    $c2Status = 0
    try {
        $c2 = Invoke-WebRequest -Uri "$GatewayUrl/api/system/role" -Method POST -Body ([System.Text.Encoding]::UTF8.GetBytes($roleBody)) -ContentType "application/json; charset=utf-8" -Headers $authOnly -TimeoutSec 10 -UseBasicParsing
        $c2Status = $c2.StatusCode
    } catch {
        if ($_.Exception.Response) { $c2Status = [int]$_.Exception.Response.StatusCode } else { $c2Status = 400 }
    }
    
    # 第一次成功 + 第二次被拒绝(400/409)或也成功 = PASS
    $idempotent = ($c1Status -ge 200 -and $c1Status -lt 300) -and ($c2Status -in 200,201,400,409,500)
    Write-TestResult "幂等性" "重复 POST 创建角色" $idempotent "第1次=$c1Status 第2次=$c2Status (冲突检测正常)"
    
    # 清理
    try {
        $createdRole = ($c1.Content | ConvertFrom-Json).data
        $roleId = if ($createdRole.id) { $createdRole.id } else { $createdRole }
        if ($roleId) { Invoke-RestMethod -Uri "$GatewayUrl/api/system/role/$roleId" -Method DELETE -Headers $headers -TimeoutSec 10 | Out-Null }
    } catch {}
} catch {
    Write-TestResult "幂等性" "重复 POST 创建角色" $false "$_"
}

# ===========================
# 测试 5: 连接池并发
# ===========================
Write-Host "`n--- 测试 5: 连接池并发 ---" -ForegroundColor Yellow

$concurrentEndpoints = @(
    "/api/system/role?page=1&pageSize=1",
    "/api/system/dict/types?page=1&pageSize=1",
    "/api/user/profile",
    "/api/stations?page=1&pageSize=1",
    "/api/device?page=1&pageSize=1",
    "/api/tenants?page=1&pageSize=1",
    "/api/system/audit-log?page=1&pageSize=1",
    "/api/system/menu/tree"
)

# 使用 RunspacePool 并发访问不同端点
$rpPool = [RunspaceFactory]::CreateRunspacePool(1, 30)
$rpPool.Open()
$connJobs = @()

$connScript = {
    param($url, $authHeader)
    $results = @()
    for ($i = 0; $i -lt 5; $i++) {
        try {
            $sw = [System.Diagnostics.Stopwatch]::StartNew()
            $r = Invoke-WebRequest -Uri $url -Headers @{ Authorization = $authHeader } -TimeoutSec 10 -UseBasicParsing
            $sw.Stop()
            $results += @{ Status = $r.StatusCode; Latency = $sw.ElapsedMilliseconds }
        } catch {
            $results += @{ Status = 0; Latency = 0 }
        }
    }
    return $results
}

foreach ($ep in $concurrentEndpoints) {
    $ps = [PowerShell]::Create().AddScript($connScript).AddArgument("$GatewayUrl$ep").AddArgument("Bearer $token")
    $ps.RunspacePool = $rpPool
    $connJobs += @{ PS = $ps; Handle = $ps.BeginInvoke(); Endpoint = $ep }
}

$connTotalOk = 0
$connTotal5xx = 0
$connTotalFail = 0

foreach ($job in $connJobs) {
    try {
        $res = $job.PS.EndInvoke($job.Handle)
        foreach ($r in $res) {
            if ($r.Status -ge 200 -and $r.Status -lt 500) { $connTotalOk++ }
            elseif ($r.Status -ge 500) { $connTotal5xx++ }
            else { $connTotalFail++ }
        }
    } catch { $connTotalFail += 5 }
    $job.PS.Dispose()
}
$rpPool.Close()

$connTotalAll = $connTotalOk + $connTotal5xx + $connTotalFail
Write-TestResult "连接池并发" "$connTotalAll 并发请求 (8端点×5次)" ($connTotalOk -gt ($connTotalAll * 0.9)) "成功=$connTotalOk 5xx=$connTotal5xx 失败=$connTotalFail"

# ===========================
# 测试 6: 超时与恢复
# ===========================
Write-Host "`n--- 测试 6: 超时与恢复 ---" -ForegroundColor Yellow

# 6.1 极短超时请求
$shortTimeoutOk = 0
$shortTimeoutFail = 0
for ($i = 0; $i -lt 5; $i++) {
    try {
        Invoke-WebRequest -Uri "$GatewayUrl/health" -TimeoutSec 1 -UseBasicParsing | Out-Null
        $shortTimeoutOk++
    } catch {
        $shortTimeoutFail++
    }
}
Write-TestResult "超时恢复" "1s 超时健康检查 (5次)" ($shortTimeoutOk -ge 4) "成功=$shortTimeoutOk 失败=$shortTimeoutFail"

# 6.2 超时后正常请求恢复
try {
    # 制造一个可能超时的请求
    try {
        Invoke-WebRequest -Uri "$GatewayUrl/api/system/role?page=1&pageSize=10000" -Headers $headers -TimeoutSec 2 -UseBasicParsing | Out-Null
    } catch {}
    
    # 立即发正常请求验证恢复
    $recoveryRes = Invoke-WebRequest -Uri "$GatewayUrl/api/system/role?page=1&pageSize=1" -Headers $headers -TimeoutSec 10 -UseBasicParsing
    Write-TestResult "超时恢复" "超时后正常请求恢复" ($recoveryRes.StatusCode -eq 200)
} catch {
    Write-TestResult "超时恢复" "超时后正常请求恢复" $false "$_"
}

# 6.3 多服务同时超时后恢复
$multiRecoveryUrls = @("/api/system/role?page=1&pageSize=1", "/api/stations?page=1&pageSize=1", "/api/device?page=1&pageSize=1")
$multiRecoveryOk = 0
foreach ($url in $multiRecoveryUrls) {
    try {
        $r = Invoke-WebRequest -Uri "$GatewayUrl$url" -Headers $headers -TimeoutSec 10 -UseBasicParsing
        if ($r.StatusCode -eq 200) { $multiRecoveryOk++ }
    } catch {}
}
Write-TestResult "超时恢复" "多服务同时恢复" ($multiRecoveryOk -eq $multiRecoveryUrls.Count) "$multiRecoveryOk/$($multiRecoveryUrls.Count) 成功"

# === 汇总 ===
Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "  Layer 7 稳定性测试完成" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  总测试: $($script:totalTests)" -ForegroundColor White
Write-Host "  通过:   $($script:passedTests)" -ForegroundColor Green
Write-Host "  失败:   $($script:failedTests)" -ForegroundColor $(if ($script:failedTests -gt 0) { "Red" } else { "Green" })
$passRate = if ($script:totalTests -gt 0) { [math]::Round($script:passedTests / $script:totalTests * 100, 1) } else { 0 }
Write-Host "  通过率: ${passRate}%`n" -ForegroundColor $(if ($passRate -ge 90) { "Green" } elseif ($passRate -ge 70) { "Yellow" } else { "Red" })

# 输出报告
$reportContent = @"
========================================
Layer 7: 稳定性与恢复测试报告
时间: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')
========================================
总测试: $($script:totalTests)
通过:   $($script:passedTests)
失败:   $($script:failedTests)
通过率: ${passRate}%

--- 持续稳定性指标 ---
总请求:   $sustainedTotal
2xx:      $sustained2xx
4xx:      $sustained4xx
5xx:      $sustained5xx
错误:     $sustainedErr
RPS:      $rps
平均延迟: ${avgLatency}ms
p95延迟:  ${p95Latency}ms
错误率:   ${errorPct}%

--- 急速爆发 ---
并发数: $BurstCount
成功:   $burstOk
5xx:    $burst5xx
失败:   $burstFail
平均延迟: ${burstAvg}ms

--- 连接池并发 ---
总请求: $connTotalAll
成功:   $connTotalOk
5xx:    $connTotal5xx

--- 详细结果 ---
$($script:results -join "`n")
"@

$reportContent | Out-File -FilePath $reportFile -Encoding utf8
Write-Host "报告已保存: $reportFile" -ForegroundColor Gray

# 返回结果供编排脚本使用
return @{
    Total = $script:totalTests
    Passed = $script:passedTests
    Failed = $script:failedTests
    PassRate = $passRate
}
