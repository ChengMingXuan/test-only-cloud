# ============================================
# 工具3: PowerShell 基础设施健康检测
# 覆盖维度: 容器状态 / 端口连通 / 服务注册 / 资源用量
# ============================================

$ErrorActionPreference = "Continue"
$results = @{
    tool       = "powershell"
    timestamp  = (Get-Date -Format "o")
    total      = 0
    passed     = 0
    failed     = 0
    warnings   = 0
    details    = @()
}

function Add-Result($category, $name, $status, $message) {
    $results.total++
    switch ($status) {
        "PASS" { $results.passed++ }
        "FAIL" { $results.failed++ }
        "WARN" { $results.warnings++ }
    }
    $results.details += @{ category = $category; name = $name; status = $status; message = $message }
    $icon = switch ($status) { "PASS" { "[PASS]" } "FAIL" { "[FAIL]" } "WARN" { "[WARN]" } }
    Write-Host "$icon $category :: $name - $message"
}

# ── T3.1 Docker 引擎 ──
Write-Host "`n=== T3.1 Docker 引擎健康 ===" -ForegroundColor Cyan
try {
    $dockerInfo = docker info --format '{{.Containers}} {{.ContainersRunning}} {{.ServerVersion}}' 2>$null
    if ($dockerInfo) {
        $parts = $dockerInfo -split ' '
        Add-Result "Docker引擎" "Docker可用" "PASS" "版本 $($parts[2]), 容器 $($parts[0]) 个, 运行 $($parts[1]) 个"
    } else { Add-Result "Docker引擎" "Docker可用" "FAIL" "Docker 不可用" }
} catch { Add-Result "Docker引擎" "Docker可用" "FAIL" "Docker 异常: $_" }

# ── T3.2 容器状态 ──
Write-Host "`n=== T3.2 容器健康状态 ===" -ForegroundColor Cyan
$containers = docker ps -a --filter "name=jgsy-" --format "{{.Names}}|{{.Status}}|{{.Ports}}" 2>$null
$runningCount = 0
$unhealthyCount = 0
foreach ($c in $containers) {
    if (-not $c) { continue }
    $parts = $c -split '\|'
    $name = $parts[0]
    $status = $parts[1]
    if ($status -match "Up") {
        $runningCount++
        if ($status -match "unhealthy") {
            $unhealthyCount++
            Add-Result "容器状态" $name "FAIL" "运行中但不健康: $status"
        }
        # 不逐个打印健康容器，只检查异常
    } else {
        Add-Result "容器状态" $name "FAIL" "未运行: $status"
    }
}
Add-Result "容器状态" "运行容器总数" $(if ($runningCount -ge 30) { "PASS" } else { "WARN" }) "$runningCount 个容器运行中"
if ($unhealthyCount -eq 0 -and $runningCount -ge 30) {
    Add-Result "容器状态" "全部健康" "PASS" "无不健康容器"
}

# ── T3.3 关键端口连通 ──
Write-Host "`n=== T3.3 端口连通性 ===" -ForegroundColor Cyan
$ports = @(
    @{ Name="PostgreSQL";   Port=5432 },
    @{ Name="Redis";        Port=6379 },
    @{ Name="RabbitMQ";     Port=5672 },
    @{ Name="RabbitMQ管理"; Port=15672 },
    @{ Name="Consul";       Port=8500 },
    @{ Name="Gateway";      Port=5000 },
    @{ Name="Seq日志";      Port=5341 }
)
foreach ($p in $ports) {
    try {
        $tcp = New-Object System.Net.Sockets.TcpClient
        $tcp.Connect("localhost", $p.Port)
        $tcp.Close()
        Add-Result "端口连通" $p.Name "PASS" "端口 $($p.Port) 可达"
    } catch {
        Add-Result "端口连通" $p.Name "FAIL" "端口 $($p.Port) 不可达"
    }
}

# ── T3.4 网关健康 ──
Write-Host "`n=== T3.4 网关 & API 入口 ===" -ForegroundColor Cyan
$gwEndpoints = @(
    @{ Name="网关健康"; Url="http://localhost:5000/health" },
    @{ Name="Consul API"; Url="http://localhost:8500/v1/catalog/services" }
)
foreach ($ep in $gwEndpoints) {
    try {
        $r = Invoke-WebRequest -Uri $ep.Url -Method GET -TimeoutSec 10 -UseBasicParsing -ErrorAction Stop
        Add-Result "网关健康" $ep.Name "PASS" "HTTP $($r.StatusCode)"
    } catch {
        $code = if ($_.Exception.Response) { $_.Exception.Response.StatusCode.value__ } else { "超时" }
        Add-Result "网关健康" $ep.Name "FAIL" "HTTP $code"
    }
}

# ── T3.5 Consul 服务注册 ──
Write-Host "`n=== T3.5 服务注册完整性 ===" -ForegroundColor Cyan
$expectedServices = @(
    "tenant-service", "identity-service", "permission-service", "account-service",
    "device-service", "station-service", "charging-service", "settlement-service",
    "workorder-service", "analytics-service", "storage-service", "ingestion-service",
    "ruleengine-service", "simulator-service", "digitaltwin-service", "iotcloudai-service",
    "blockchain-service", "contentplatform-service", "observability-service",
    "orchestrator-service", "vpp-service", "microgrid-service", "pvessc-service",
    "electrade-service", "carbontrade-service", "demandresp-service", "deviceops-service",
    "energyeff-service", "multienergy-service", "safecontrol-service"
)
try {
    $consulServices = (Invoke-RestMethod -Uri "http://localhost:8500/v1/catalog/services" -TimeoutSec 10) | Get-Member -MemberType NoteProperty | Select-Object -ExpandProperty Name
    $missing = @()
    foreach ($svc in $expectedServices) {
        if ($svc -notin $consulServices) { $missing += $svc }
    }
    if ($missing.Count -eq 0) {
        Add-Result "服务注册" "全部注册" "PASS" "$($expectedServices.Count) 个服务全部在 Consul 注册"
    } else {
        Add-Result "服务注册" "缺失服务" "FAIL" "缺失 $($missing.Count) 个: $($missing -join ', ')"
    }
} catch {
    Add-Result "服务注册" "Consul查询" "FAIL" "无法查询 Consul: $_"
}

# ── T3.6 API 网关路由 ──
Write-Host "`n=== T3.6 网关路由验证 ===" -ForegroundColor Cyan
# 先获取 token
try {
    $loginBody = @{ username = "admin"; password = "P@ssw0rd" } | ConvertTo-Json
    $loginResp = Invoke-RestMethod -Uri "http://localhost:5000/api/auth/login" -Method POST -Body $loginBody -ContentType "application/json" -TimeoutSec 15
    $token = $loginResp.data.accessToken
    $authHeader = @{ Authorization = "Bearer $token" }

    $apiRoutes = @(
        @{ Name="租户"; Url="/api/tenants?page=1&pageSize=1" },
        @{ Name="角色"; Url="/api/roles?page=1&pageSize=1" },
        @{ Name="菜单"; Url="/api/menus?type=all" },
        @{ Name="设备"; Url="/api/device?page=1&pageSize=1" },
        @{ Name="站点"; Url="/api/station?page=1&pageSize=1" },
        @{ Name="充电订单"; Url="/api/charging/orders?page=1&pageSize=1" },
        @{ Name="工单"; Url="/api/workorder?page=1&pageSize=1" },
        @{ Name="规则链"; Url="/api/ruleengine/chains?page=1&pageSize=1" },
        @{ Name="数据分析"; Url="/api/analytics/funnel?page=1&pageSize=1" },
        @{ Name="模拟器"; Url="/api/simulator/engines" }
    )
    foreach ($route in $apiRoutes) {
        try {
            $r = Invoke-WebRequest -Uri "http://localhost:5000$($route.Url)" -Method GET -Headers $authHeader -TimeoutSec 10 -UseBasicParsing -ErrorAction Stop
            Add-Result "网关路由" $route.Name "PASS" "HTTP $($r.StatusCode)"
        } catch {
            $code = if ($_.Exception.Response) { $_.Exception.Response.StatusCode.value__ } else { "超时" }
            Add-Result "网关路由" $route.Name $(if ($code -ge 500) { "FAIL" } else { "WARN" }) "HTTP $code"
        }
    }
} catch {
    Add-Result "网关路由" "认证" "FAIL" "无法获取 Token: $_"
}

# ── T3.7 容器资源用量 ──
Write-Host "`n=== T3.7 容器资源用量 ===" -ForegroundColor Cyan
$stats = docker stats --no-stream --format "{{.Name}}|{{.CPUPerc}}|{{.MemUsage}}" 2>$null | Where-Object { $_ -match "^jgsy-" }
$highCpu = @()
$highMem = @()
foreach ($s in $stats) {
    $parts = $s -split '\|'
    $name = $parts[0]
    $cpu = [double]($parts[1] -replace '%','')
    $memStr = $parts[2] -split '/'
    $memUsed = $memStr[0].Trim()
    if ($cpu -gt 80) { $highCpu += "$name($cpu%)" }
    if ($memUsed -match "(\d+\.?\d*)GiB" -and [double]$Matches[1] -gt 1.5) { $highMem += "$name($memUsed)" }
}
if ($highCpu.Count -eq 0) {
    Add-Result "资源用量" "CPU" "PASS" "无容器 CPU > 80%"
} else {
    Add-Result "资源用量" "CPU" "WARN" "高 CPU: $($highCpu -join ', ')"
}
if ($highMem.Count -eq 0) {
    Add-Result "资源用量" "内存" "PASS" "无容器内存 > 1.5GB"
} else {
    Add-Result "资源用量" "内存" "WARN" "高内存: $($highMem -join ', ')"
}

# ── T3.8 日志错误检查 ──
Write-Host "`n=== T3.8 近期日志错误 ===" -ForegroundColor Cyan
$criticalServices = @("jgsy-gateway", "jgsy-tenant", "jgsy-permission", "jgsy-device", "jgsy-charging")
foreach ($svc in $criticalServices) {
    $logs = docker logs --tail 100 $svc 2>&1 | Where-Object { $_ -match "Error|Exception|FATAL|Critical" -and $_ -notmatch "HealthCheck|deprecated|warn" }
    $errCount = ($logs | Measure-Object).Count
    if ($errCount -eq 0) {
        Add-Result "日志错误" $svc "PASS" "近100行无严重错误"
    } elseif ($errCount -le 5) {
        Add-Result "日志错误" $svc "WARN" "$errCount 条错误/异常"
    } else {
        Add-Result "日志错误" $svc "FAIL" "$errCount 条错误/异常（需排查）"
    }
}

# ── 输出 JSON ──
$jsonPath = "D:\2026\aiops.v2\TestResults\ps-infra-results.json"
$results | ConvertTo-Json -Depth 5 | Set-Content -Path $jsonPath -Encoding UTF8

Write-Host "`n=== 基础设施检测汇总 ===" -ForegroundColor Yellow
Write-Host "总计: $($results.total) | 通过: $($results.passed) | 失败: $($results.failed) | 警告: $($results.warnings)"
Write-Host "结果已保存: $jsonPath"
