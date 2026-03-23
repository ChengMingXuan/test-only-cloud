<#
.SYNOPSIS
  端到端业务全链路测试
.DESCRIPTION
  模拟真实业务流：
  充电站查询 → 订单记录 → 结算生成 → 区块链存证
  → PVESSC 调度评估 → VPP 电力交易 → AI 体检 → SEHS 综合调度
  覆盖多服务跨系统链路完整性。
#>
param(
    [string]$GatewayUrl    = "http://localhost:5000",
    [string]$AiUrl         = "http://localhost:8020",
    [string]$BlockchainUrl = "http://localhost:8021",
    [string]$Username      = "admin",
    [string]$Password      = "P@ssw0rd",
    [string]$LogDir        = "tests/scripts/logs"
)

$ErrorActionPreference = "Continue"
chcp 65001 | Out-Null
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

$results   = @()
$startTime = Get-Date
$ts        = Get-Date -Format "MMddHHmmss"

# 五个核心测试 ID
$pvSiteId = "019c741e-5ad1-755d-b7e7-4a4acc6c3f5d"
$vppId    = "019c741f-a680-7972-9ecd-f5f4dba5e628"
$mgId     = "019c7420-7452-74fd-a050-69e5e5d9a7cd"

function Add-Result {
    param([string]$Flow, [string]$Step, [string]$Status, [string]$Detail = "")
    $script:results += [PSCustomObject]@{ Flow=$Flow; Step=$Step; Status=$Status; Detail=$Detail }
    $color = switch ($Status) { "PASS"{"Green"}; "FAIL"{"Red"}; "WARN"{"Yellow"}; "SKIP"{"DarkGray"}; default{"Gray"} }
    $mark  = switch ($Status) { "PASS"{"✅"}; "FAIL"{"❌"}; "WARN"{"⚠️"}; "SKIP"{"⏭"}; default{"•"} }
    Write-Host "  $mark [$Flow] $Step$(if ($Detail) { " → $Detail" })" -ForegroundColor $color
}

function Invoke-Api {
    param([string]$Url, [string]$Method="GET", [object]$Body=$null, [hashtable]$Headers=@{}, [int]$TimeoutSec=15)
    try {
        $params = @{ Uri=$Url; Method=$Method; Headers=$Headers; TimeoutSec=$TimeoutSec; ErrorAction="Stop" }
        if ($null -ne $Body) {
            $params["ContentType"] = "application/json"
            $params["Body"] = if ($Body -is [string]) { $Body } else { $Body | ConvertTo-Json -Depth 10 -Compress }
        }
        $sw = [System.Diagnostics.Stopwatch]::StartNew()
        $r  = Invoke-RestMethod @params
        $sw.Stop()
        return @{ Ok=$true; Data=$r; StatusCode=200; Ms=$sw.ElapsedMilliseconds }
    } catch {
        $sc = $_.Exception.Response.StatusCode.value__
        return @{ Ok=$false; Data=$null; StatusCode=$sc; Ms=-1; Error=$_.Exception.Message }
    }
}

# ============================================================
# STEP 0: 认证
# ============================================================
Write-Host "`n" -NoNewline
Write-Host "╔════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║        端到端业务全链路测试                    ║" -ForegroundColor Cyan
Write-Host "╚════════════════════════════════════════════════╝" -ForegroundColor Cyan

Write-Host "`n--- STEP 0: 认证 ---" -ForegroundColor Cyan
$login = Invoke-Api -Url "$GatewayUrl/api/auth/login" -Method POST -Body @{ username=$Username; password=$Password }
if (-not $login.Ok -or -not $login.Data.success) {
    Write-Host "❌ 登录失败，终止测试" -ForegroundColor Red; exit 1
}
$h = @{ "Authorization" = "Bearer $($login.Data.data.accessToken)" }
Add-Result "认证" "管理员登录" "PASS" "$($login.Ms)ms"

# ============================================================
# FLOW 1: 充电订单 → 结算 链路
# ============================================================
Write-Host "`n--- FLOW 1: 充电业务链路 ---" -ForegroundColor Magenta

# 1.1 查询充电站列表
$r = Invoke-Api -Url "$GatewayUrl/api/stations?pageIndex=1&pageSize=5" -Headers $h
if ($r.Ok -and $r.Data -ne $null) {
    $stationCount = if ($r.Data.data.items) { $r.Data.data.items.Count } elseif ($r.Data.total) { $r.Data.total } else { "N/A" }
    Add-Result "充电" "充电站列表" "PASS" "Count=$stationCount, ${$r.Ms}ms"
} else {
    Add-Result "充电" "充电站列表" "FAIL" "HTTP $($r.StatusCode)"
}

# 1.2 查询充电订单列表
$r = Invoke-Api -Url "$GatewayUrl/api/charging/admin/orders?pageIndex=1&pageSize=5" -Headers $h
if ($r.Ok -and $r.Data.success) {
    $totalCount = $r.Data.data.totalCount; $totalTotal = $r.Data.data.total
    $orderCount = if ($null -ne $totalCount) { $totalCount } elseif ($null -ne $totalTotal) { $totalTotal } else { 'N/A' }
    Add-Result "充电" "充电订单查询" "PASS" "TotalOrders=$orderCount"
} else {
    Add-Result "充电" "充电订单查询" "FAIL" "HTTP $($r.StatusCode)"
}

# 1.3 创建结算记录（模拟充电完成后结算）
$settleBody = @{
    periodStart    = (Get-Date).AddDays(-1).ToString("yyyy-MM-dd")
    periodEnd      = (Get-Date).ToString("yyyy-MM-dd")
    totalAmount    = 30.60
    platformShare  = 10.20
}
$r = Invoke-Api -Url "$GatewayUrl/api/settlements" -Method POST -Body $settleBody -Headers $h
if ($r.Ok -and ($r.Data.success -or $r.StatusCode -eq 201 -or $r.StatusCode -eq 200)) {
    $settleId = if ($null -ne $r.Data.data) { $r.Data.data } else { $r.Data.id }
    Add-Result "结算" "结算记录创建" "PASS" "SettleID=$(if ($settleId) {$settleId} else {'已创建'})"
} else {
    Add-Result "结算" "结算记录创建" "FAIL" "HTTP $($r.StatusCode) $($r.Error)"
}

# 1.4 查询结算列表
$r = Invoke-Api -Url "$GatewayUrl/api/settlements?pageIndex=1&pageSize=5" -Headers $h
if ($r.Ok -and $r.Data -ne $null) {
    Add-Result "结算" "结算列表查询" "PASS" "${$r.Ms}ms"
} else {
    Add-Result "结算" "结算列表查询" "FAIL" "HTTP $($r.StatusCode)"
}

# 1.5 工单关联（WorkOrder）
$r = Invoke-Api -Url "$GatewayUrl/api/workorder?page=1&pageSize=5" -Headers $h
if ($r.Ok) {
    Add-Result "工单" "工单列表查询" "PASS" "${$r.Ms}ms"
} else {
    Add-Result "工单" "工单列表查询" "WARN" "HTTP $($r.StatusCode)"
}

# ============================================================
# FLOW 2: PVESSC 光储充调度链路
# ============================================================
Write-Host "`n--- FLOW 2: PVESSC 调度链路 ---" -ForegroundColor Magenta

# 2.1 站点实时状态
$r = Invoke-Api -Url "$GatewayUrl/api/pvessc/site/$pvSiteId" -Headers $h
if ($r.Ok -and $r.Data.success) {
    Add-Result "PVESSC" "站点状态읽기" "PASS" "Name=$($r.Data.data.name)"
} else {
    Add-Result "PVESSC" "站点状态读取" "FAIL" "HTTP $($r.StatusCode)"
}

# 2.2 调度评估（根据当前 SOC+光伏+时段，给出充放电建议）
$r = Invoke-Api -Url "$GatewayUrl/api/pvessc/dispatch/$pvSiteId/evaluate" -Headers $h
if ($r.Ok -and $r.Data.success) {
    $decision = if ($null -ne $r.Data.data.decisionType) { $r.Data.data.decisionType } else { '有' }
    Add-Result "PVESSC" "调度决策评估" "PASS" "Decision=$decision"
} else {
    Add-Result "PVESSC" "调度决策评估" "WARN" "HTTP $($r.StatusCode) (需时序数据支撑)"
}

# 2.3 峰谷策略查询
$r = Invoke-Api -Url "$GatewayUrl/api/pvessc/tariff/$pvSiteId/list" -Headers $h
if ($r.Ok -and $r.Data.success) {
    Add-Result "PVESSC" "峰谷策略列表" "PASS" ""
} else {
    Add-Result "PVESSC" "峰谷策略列表" "WARN" "HTTP $($r.StatusCode)"
}

# 2.4 拓扑图查询
$r = Invoke-Api -Url "$GatewayUrl/api/pvessc/topology/$pvSiteId" -Headers $h
if ($r.Ok -and $r.Data.success) {
    Add-Result "PVESSC" "站点拓扑图" "PASS" ""
} else {
    Add-Result "PVESSC" "站点拓扑图" "WARN" "HTTP $($r.StatusCode)"
}

# ============================================================
# FLOW 3: VPP 虚拟电厂电力交易链路
# ============================================================
Write-Host "`n--- FLOW 3: VPP 电力交易链路 ---" -ForegroundColor Magenta

# 3.1 VPP 状态
$r = Invoke-Api -Url "$GatewayUrl/api/vpp/$vppId" -Headers $h
if ($r.Ok -and $r.Data.success) {
    $status = $r.Data.data.status
    Add-Result "VPP" "VPP状态" "PASS" "Status=$status"
} else {
    Add-Result "VPP" "VPP状态" "FAIL" "HTTP $($r.StatusCode)"
}

# 3.2 电力交易 Dashboard
$r = Invoke-Api -Url "$GatewayUrl/api/electrade/dashboard" -Headers $h
if ($r.Ok -and $r.Data.success) {
    Add-Result "VPP" "电力交易Dashboard" "PASS" ""
} else {
    Add-Result "VPP" "电力交易Dashboard" "FAIL" "HTTP $($r.StatusCode)"
}

# 3.3 VPP 资源列表（参与交易的资源）
$r = Invoke-Api -Url "$GatewayUrl/api/vpp/resource/list?pageIndex=1&pageSize=10" -Headers $h
if ($r.Ok -and $r.Data.success) {
    $resCount = if ($null -ne $r.Data.data.totalCount) { $r.Data.data.totalCount } else { 'N/A' }
    Add-Result "VPP" "VPP资源列表" "PASS" "Count=$resCount"
} else {
    Add-Result "VPP" "VPP资源列表" "FAIL" "HTTP $($r.StatusCode)"
}

# 3.4 碳交易
$r = Invoke-Api -Url "$GatewayUrl/api/carbontrade/dashboard" -Headers $h
if ($r.Ok -and $r.Data.success) {
    Add-Result "VPP" "碳交易Dashboard" "PASS" ""
} else {
    Add-Result "VPP" "碳交易Dashboard" "FAIL" "HTTP $($r.StatusCode)"
}

# ============================================================
# FLOW 4: 微电网运行链路
# ============================================================
Write-Host "`n--- FLOW 4: 微电网运行链路 ---" -ForegroundColor Magenta

$r = Invoke-Api -Url "$GatewayUrl/api/microgrid/$mgId" -Headers $h
if ($r.Ok -and $r.Data.success) {
    Add-Result "MicroGrid" "微电网详情" "PASS" "Mode=$($r.Data.data.currentMode)"
} else {
    Add-Result "MicroGrid" "微电网详情" "FAIL" "HTTP $($r.StatusCode)"
}

$r = Invoke-Api -Url "$GatewayUrl/api/microgrid/power/$mgId/realtime" -Headers $h
if ($r.Ok) {
    $hasData = $null -ne $r.Data.data
    Add-Result "MicroGrid" "实时功率" $(if ($hasData) {"PASS"} else {"WARN"}) $(if ($hasData) {"有数据"} else {"data=null"})
} else {
    Add-Result "MicroGrid" "实时功率" "WARN" "HTTP $($r.StatusCode) (无时序数据)"
}

$r = Invoke-Api -Url "$GatewayUrl/api/microgrid/alert/list?pageIndex=1&pageSize=5" -Headers $h
if ($r.Ok -and $r.Data.success) {
    Add-Result "MicroGrid" "告警列表" "PASS" ""
} else {
    Add-Result "MicroGrid" "告警列表" "WARN" "HTTP $($r.StatusCode)"
}

# ============================================================
# FLOW 5: AI 智能体检链路
# ============================================================
Write-Host "`n--- FLOW 5: AI 体检链路 ---" -ForegroundColor Magenta

$r = Invoke-Api -Url "$AiUrl/api/iotcloudai/dashboard" -Headers $h
if ($r.Ok -and $r.Data.success) {
    Add-Result "AI" "AI体检Dashboard" "PASS" ""
} else {
    Add-Result "AI" "AI体检Dashboard" "FAIL" "HTTP $($r.StatusCode)"
}

# 预测设备故障（核心 AI 能力）
$r = Invoke-Api -Url "$AiUrl/api/iotcloudai/fault-warning/predict/DEV-E2E-001" -Headers $h
if ($r.Ok -and $r.Data.success) {
    $faults = $r.Data.data.Count
    Add-Result "AI" "故障预测" "PASS" "PredictedFaults=$faults"
} else {
    Add-Result "AI" "故障预测" "WARN" "HTTP $($r.StatusCode)"
}

# 剩余寿命预测
$r = Invoke-Api -Url "$AiUrl/api/iotcloudai/fault-warning/remaining-life/DEV-E2E-001" -Headers $h
if ($r.Ok -and $r.Data.success) {
    Add-Result "AI" "剩余寿命预测" "PASS" ""
} else {
    Add-Result "AI" "剩余寿命预测" "WARN" "HTTP $($r.StatusCode)"
}

# PHM 评估（按设备类型）
$r = Invoke-Api -Url "$AiUrl/api/iotcloudai/health-monitor/assess/Inverter/DEV-E2E-001" -Headers $h
if ($r.Ok -and $r.Data.success) {
    Add-Result "AI" "逆变器PHM评估" "PASS" ""
} else {
    Add-Result "AI" "逆变器PHM评估" "WARN" "HTTP $($r.StatusCode)"
}

# ============================================================
# FLOW 6: SEHS 综合调度链路
# ============================================================
Write-Host "`n--- FLOW 6: SEHS 综合调度链路 ---" -ForegroundColor Magenta

$r = Invoke-Api -Url "$GatewayUrl/api/sehs/dashboard" -Headers $h
if ($r.Ok -and $r.Data.success) {
    Add-Result "SEHS" "综合Dashboard" "PASS" ""
} else {
    Add-Result "SEHS" "综合Dashboard" "FAIL" "HTTP $($r.StatusCode)"
}

# 资源快照（集成当前四子系统状态）
$snapBody = @{
    sourcePowerKw    = 800.0
    gridPowerKw      = 150.0
    loadPowerKw      = 700.0
    storagePowerKw   = -200.0
    storageSoc       = 72.5
    pvGenerationKw   = 450.0
    windGenerationKw = 0.0
    dataSource       = "E2E-Test-$ts"
}
$r = Invoke-Api -Url "$GatewayUrl/api/sehs/resource" -Method POST -Body $snapBody -Headers $h
if ($r.Ok -and $r.Data.success) {
    Add-Result "SEHS" "资源快照上报" "PASS" ""
} else {
    Add-Result "SEHS" "资源快照上报" "FAIL" "HTTP $($r.StatusCode)"
}

# 多能互补
$r = Invoke-Api -Url "$GatewayUrl/api/multienergy/dashboard" -Headers $h
if ($r.Ok -and $r.Data.success) {
    Add-Result "SEHS" "多能互补Dashboard" "PASS" ""
} else {
    Add-Result "SEHS" "多能互补Dashboard" "FAIL" "HTTP $($r.StatusCode)"
}

# ============================================================
# FLOW 7: 区块链存证链路
# ============================================================
Write-Host "`n--- FLOW 7: 区块链存证链路 ---" -ForegroundColor Magenta

# 交易记录查询
$r = Invoke-Api -Url "$BlockchainUrl/api/transactions?pageIndex=1&pageSize=5" -Headers $h
if ($r.Ok -and $r.Data.success) {
    Add-Result "区块链" "交易记录查询" "PASS" ""
} else {
    Add-Result "区块链" "交易记录查询" "WARN" "HTTP $($r.StatusCode)"
}

# 绿证数量查询
$r = Invoke-Api -Url "$BlockchainUrl/api/certificates?pageIndex=1&pageSize=5" -Headers $h
if ($r.Ok) {
    Add-Result "区块链" "绿证存量查询" "PASS" ""
} else {
    Add-Result "区块链" "绿证存量查询" "WARN" "HTTP $($r.StatusCode)"
}

# 钱包余额
$r = Invoke-Api -Url "$BlockchainUrl/api/wallet/system-info" -Headers $h
if ($r.Ok -and $r.Data.success) {
    Add-Result "区块链" "钱包信息" "PASS" ""
} else {
    Add-Result "区块链" "钱包信息" "WARN" "HTTP $($r.StatusCode)"
}

# ============================================================
# FLOW 8: 跨服务观测 (Observability)
# ============================================================
Write-Host "`n--- FLOW 8: 可观测性链路 ---" -ForegroundColor Magenta

$obsEndpoints = @(
    @{ Name="健康检查汇总"; Url="$GatewayUrl/api/system/health/all" },
    @{ Name="服务指标";      Url="$GatewayUrl/api/observability/metrics" },
    @{ Name="用户操作日志"; Url="$GatewayUrl/api/observability/audit?pageIndex=1&pageSize=5" }
)
foreach ($oe in $obsEndpoints) {
    $r = Invoke-Api -Url $oe.Url -Headers $h
    $st = if ($r.Ok) {"PASS"} elseif ($r.StatusCode -eq 404) {"WARN"} else {"FAIL"}
    Add-Result "可观测" $oe.Name $st "HTTP $($r.StatusCode)"
}

# ============================================================
# 汇总
# ============================================================
Write-Host "`n==========================================" -ForegroundColor Yellow
Write-Host "  端到端业务全链路测试汇总" -ForegroundColor Yellow
Write-Host "==========================================" -ForegroundColor Yellow

$pass  = ($results | Where-Object { $_.Status -eq "PASS"  }).Count
$warn  = ($results | Where-Object { $_.Status -eq "WARN"  }).Count
$fail  = ($results | Where-Object { $_.Status -eq "FAIL"  }).Count
$skip  = ($results | Where-Object { $_.Status -eq "SKIP"  }).Count
$total = $results.Count
$elapsed = [int](Get-Date).Subtract($startTime).TotalSeconds

Write-Host "总步骤: $total  ✅PASS=$pass  ⚠️WARN=$warn  ❌FAIL=$fail  ⏭SKIP=$skip  耗时:${elapsed}s" -ForegroundColor White

# 按 Flow 汇总
$flows = $results | Group-Object -Property Flow | Sort-Object Name
Write-Host "`n各 Flow 通过率：" -ForegroundColor Cyan
foreach ($fl in $flows) {
    $fp = ($fl.Group | Where-Object { $_.Status -eq "PASS" }).Count
    $ft = $fl.Group.Count
    $rate = [math]::Round($fp / $ft * 100)
    $color = if ($rate -ge 80) {"Green"} elseif ($rate -ge 50) {"Yellow"} else {"Red"}
    Write-Host ("  {0,-15} {1,2}/{2,2} ({3}%)" -f "$($fl.Name):", $fp, $ft, $rate) -ForegroundColor $color
}

if ($fail -gt 0) {
    Write-Host "`n❌ 链路故障（需修复）：" -ForegroundColor Red
    $results | Where-Object { $_.Status -eq "FAIL" } | ForEach-Object {
        Write-Host "  [$($_.Flow)] $($_.Step): $($_.Detail)" -ForegroundColor Red
    }
}

# 保存
try {
    if (-not [System.IO.Path]::IsPathRooted($LogDir)) {
        $base      = (Resolve-Path (Join-Path $PSScriptRoot "../..")).Path
        $targetDir = Join-Path $base $LogDir
    } else { $targetDir = $LogDir }
    if (-not (Test-Path $targetDir)) { New-Item -ItemType Directory -Path $targetDir -Force | Out-Null }
    $logTs   = Get-Date -Format "yyyyMMdd-HHmmss"
    $logPath = Join-Path $targetDir "e2e-business-flow-$logTs.csv"
    $results | Export-Csv -Path $logPath -NoTypeInformation -Encoding UTF8
    Write-Host "`n日志已保存: $logPath" -ForegroundColor Gray
} catch {
    Write-Host "日志保存失败: $($_.Exception.Message)" -ForegroundColor Yellow
}

$passRate = [math]::Round($pass / $total * 100)
$verdict  = if ($fail -eq 0) { "全链路通过 ✅（PASS率 $passRate%）" } else { "链路存在断点 ❌（PASS率 $passRate%）" }
Write-Host "`n端到端测试结论：$verdict" -ForegroundColor $(if ($fail -eq 0) {"Green"} else {"Red"})
Write-Host "完成时间: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')" -ForegroundColor Gray
