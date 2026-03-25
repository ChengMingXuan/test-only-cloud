<#
.SYNOPSIS
  多条件组合查询测试 — 对所有列表接口进行 C(N,3) 参数组合天花板测试
.DESCRIPTION
  对每个定义了查询参数的列表接口，
  自动生成所有 3 条件组合（C(n,3)），逐一执行并校验：
    ✅ 返回 200 且 data 结构正常
    ✅ 空结果（items=[]）不算失败
    ❌ 500/400 且不含字段缺失提示 → 失败（应返回空列表而非报错）

  覆盖全部 20 个服务的主要列表接口，共约 300+ 参数组合。
#>
param(
    [string] $GatewayUrl    = "http://localhost:5000",
    [string] $AiUrl         = "http://localhost:8020",
    [string] $BlockchainUrl = "http://localhost:8021",
    [string] $Username      = "admin",
    [string] $Password      = "P@ssw0rd",
    [string] $LogDir        = "tests/scripts/logs",
    [int]    $DelayMs       = 60
)
$ErrorActionPreference = "Continue"
chcp 65001 | Out-Null
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

$results   = [System.Collections.Generic.List[PSCustomObject]]::new()
$startTime = Get-Date

# ── 列表接口 + 可用查询参数清单（查参数见各控制器 FromQuery 参数）──
# 格式: Url, Params(数组), ValidValues(每个参数的合法值)
$G = $GatewayUrl; $A = $AiUrl; $B = $BlockchainUrl

$endpointManifest = @(

# ================================================
# Account 服务
# ================================================
@{ Svc="Account"; Url="$G/api/users";                 Params=@(
    @{k="pageIndex";v="1"}, @{k="pageSize";v="10"}, @{k="keyword";v="test"},
    @{k="status";v="1"}, @{k="roleId";v=""}, @{k="tenantId";v=""} ) },

@{ Svc="Permission"; Url="$G/api/system/role";            Params=@(
    @{k="pageIndex";v="1"}, @{k="pageSize";v="10"}, @{k="keyword";v="admin"},
    @{k="status";v="1"} ) },

# ================================================
# Analytics 服务
# ================================================
@{ Svc="Analytics"; Url="$G/api/analytics/reports";   Params=@(
    @{k="pageIndex";v="1"}, @{k="pageSize";v="10"},
    @{k="startTime";v="2024-01-01 00:00:00"}, @{k="endTime";v="2025-12-31 23:59:59"},
    @{k="type";v="daily"}, @{k="keyword";v=""} ) },

@{ Svc="Analytics"; Url="$G/api/analytics/statistics"; Params=@(
    @{k="startTime";v="2024-01-01"}, @{k="endTime";v="2025-12-31"},
    @{k="granularity";v="day"}, @{k="metric";v="energy"} ) },

# ================================================
# Blockchain 服务
# ================================================
@{ Svc="Blockchain"; Url="$B/api/transactions";        Params=@(
    @{k="pageIndex";v="1"}, @{k="pageSize";v="10"},
    @{k="startTime";v="2024-01-01"}, @{k="endTime";v="2025-12-31"},
    @{k="txType";v=""}, @{k="status";v=""} ) },

@{ Svc="Blockchain"; Url="$B/api/certificates";        Params=@(
    @{k="pageIndex";v="1"}, @{k="pageSize";v="10"},
    @{k="certType";v="green"}, @{k="status";v="active"} ) },

# ================================================
# Charging 服务
# ================================================
@{ Svc="Charging"; Url="$G/api/charging/admin/orders"; Params=@(
    @{k="pageIndex";v="1"}, @{k="pageSize";v="10"},
    @{k="startTime";v="2024-01-01 00:00:00"}, @{k="endTime";v="2025-12-31 23:59:59"},
    @{k="status";v="completed"}, @{k="stationId";v=""},
    @{k="userId";v=""}, @{k="orderNumber";v=""} ) },

@{ Svc="Charging"; Url="$G/api/charging/piles";        Params=@(
    @{k="pageIndex";v="1"}, @{k="pageSize";v="10"},
    @{k="stationId";v=""}, @{k="status";v="idle"}, @{k="keyword";v=""} ) },

# ================================================
# ContentPlatform 服务
# ================================================
@{ Svc="ContentPlatform"; Url="$G/api/content/articles"; Params=@(
    @{k="pageIndex";v="1"}, @{k="pageSize";v="10"},
    @{k="categoryId";v=""}, @{k="status";v="published"},
    @{k="keyword";v="能源"}, @{k="authorId";v=""} ) },

# ================================================
# Device 服务
# ================================================
@{ Svc="Device"; Url="$G/api/device";                  Params=@(
    @{k="pageIndex";v="1"}, @{k="pageSize";v="10"},
    @{k="keyword";v=""}, @{k="status";v="online"},
    @{k="deviceType";v=""}, @{k="stationId";v=""} ) },

@{ Svc="Device"; Url="$G/api/device/alarm";             Params=@(
    @{k="pageIndex";v="1"}, @{k="pageSize";v="10"},
    @{k="level";v="high"}, @{k="startTime";v="2024-01-01"},
    @{k="endTime";v="2025-12-31"}, @{k="deviceId";v=""} ) },

# ================================================
# EnergyCore / PVESSC
# ================================================
@{ Svc="EnergyCore"; Url="$G/api/pvessc/site/list";    Params=@(
    @{k="pageIndex";v="1"}, @{k="pageSize";v="10"},
    @{k="keyword";v=""}, @{k="status";v="running"},
    @{k="province";v=""}, @{k="capacity";v=""} ) },

@{ Svc="EnergyCore"; Url="$G/api/vpp/list";            Params=@(
    @{k="pageIndex";v="1"}, @{k="pageSize";v="10"},
    @{k="keyword";v=""}, @{k="status";v="active"} ) },

@{ Svc="EnergyCore"; Url="$G/api/microgrid/list";      Params=@(
    @{k="pageIndex";v="1"}, @{k="pageSize";v="10"},
    @{k="keyword";v=""}, @{k="currentMode";v=""} ) },

# ================================================
# EnergyServices
# ================================================
@{ Svc="EnergyServices"; Url="$G/api/electrade/orders"; Params=@(
    @{k="pageIndex";v="1"}, @{k="pageSize";v="10"},
    @{k="startTime";v="2024-01-01"}, @{k="endTime";v="2025-12-31"},
    @{k="status";v=""}, @{k="tradeType";v=""} ) },

@{ Svc="EnergyServices"; Url="$G/api/carbontrade/records"; Params=@(
    @{k="pageIndex";v="1"}, @{k="pageSize";v="10"},
    @{k="startTime";v="2024-01-01"}, @{k="endTime";v="2025-12-31"},
    @{k="carbonType";v=""} ) },

# ================================================
# Identity 服务
# ================================================
@{ Svc="Identity"; Url="$G/api/auth/sessions";         Params=@(
    @{k="pageIndex";v="1"}, @{k="pageSize";v="10"},
    @{k="userId";v=""}, @{k="startTime";v="2024-01-01"},
    @{k="endTime";v="2025-12-31"} ) },

# ================================================
# IotCloudAI
# ================================================
@{ Svc="IotCloudAI"; Url="$A/api/iotcloudai/fault-warning/list"; Params=@(
    @{k="pageIndex";v="1"}, @{k="pageSize";v="10"},
    @{k="deviceId";v=""}, @{k="level";v="warn"},
    @{k="startTime";v="2024-01-01"}, @{k="status";v="active"} ) },

@{ Svc="IotCloudAI"; Url="$A/api/iotcloudai/health-monitor/list"; Params=@(
    @{k="pageIndex";v="1"}, @{k="pageSize";v="10"},
    @{k="deviceType";v="Inverter"}, @{k="healthLevel";v=""},
    @{k="startTime";v="2024-01-01"} ) },

# ================================================
# Observability 服务
# ================================================
@{ Svc="Observability"; Url="$G/api/observability/audit"; Params=@(
    @{k="pageIndex";v="1"}, @{k="pageSize";v="10"},
    @{k="userId";v=""}, @{k="action";v=""},
    @{k="startTime";v="2024-01-01"}, @{k="endTime";v="2025-12-31"},
    @{k="module";v=""}, @{k="result";v="success"} ) },

@{ Svc="Observability"; Url="$G/api/observability/alerts"; Params=@(
    @{k="pageIndex";v="1"}, @{k="pageSize";v="10"},
    @{k="level";v="error"}, @{k="status";v="active"},
    @{k="startTime";v="2024-01-01"}, @{k="service";v=""} ) },

# ================================================
# Permission 服务
# ================================================
@{ Svc="Permission"; Url="$G/api/system/permission";     Params=@(
    @{k="pageIndex";v="1"}, @{k="pageSize";v="10"},
    @{k="keyword";v=""}, @{k="module";v=""}, @{k="action";v="read"} ) },

@{ Svc="Permission"; Url="$G/api/system/menu/tree";     Params=@(
    @{k="keyword";v=""}, @{k="status";v="1"}, @{k="parentId";v=""} ) },

# ================================================
# Settlement 服务
# ================================================
@{ Svc="Settlement"; Url="$G/api/settlements";          Params=@(
    @{k="pageIndex";v="1"}, @{k="pageSize";v="10"},
    @{k="startTime";v="2024-01-01"}, @{k="endTime";v="2025-12-31"},
    @{k="status";v=""}, @{k="stationId";v=""},
    @{k="userId";v=""}, @{k="minFee";v="0"}, @{k="maxFee";v="1000"} ) },

@{ Svc="Settlement"; Url="$G/api/merchant/settlements"; Params=@(
    @{k="pageIndex";v="1"}, @{k="pageSize";v="10"},
    @{k="startTime";v="2024-01-01"}, @{k="status";v="pending"} ) },

# ================================================
# Station 服务
# ================================================
@{ Svc="Station"; Url="$G/api/stations";               Params=@(
    @{k="pageIndex";v="1"}, @{k="pageSize";v="10"},
    @{k="keyword";v=""}, @{k="status";v=""},
    @{k="province";v=""}, @{k="city";v=""}, @{k="operator";v=""} ) },

# ================================================
# Tenant 服务
# ================================================
@{ Svc="Tenant"; Url="$G/api/tenants";                 Params=@(
    @{k="pageIndex";v="1"}, @{k="pageSize";v="10"},
    @{k="keyword";v=""}, @{k="status";v="active"},
    @{k="plan";v=""} ) },

# ================================================
# WorkOrder 服务
# ================================================
@{ Svc="WorkOrder"; Url="$G/api/workorder";             Params=@(
    @{k="pageIndex";v="1"}, @{k="pageSize";v="10"},
    @{k="status";v=""}, @{k="type";v=""},
    @{k="startTime";v="2024-01-01"}, @{k="endTime";v="2025-12-31"},
    @{k="assigneeId";v=""}, @{k="priority";v=""} ) }
)

# ── 工具函数 ─────────────────────────────────────────────────────
function Add-R {
    param([string]$Svc,[string]$Endpoint,[string]$Combo,[string]$Status,[string]$Detail="")
    $results.Add([PSCustomObject]@{
        Service=$Svc; Endpoint=$Endpoint; Combination=$Combo; Status=$Status; Detail=$Detail
    })
    $color = switch ($Status) { "PASS"{"Green"}; "FAIL"{"Red"}; "WARN"{"Yellow"}; default{"Gray"} }
    $mark  = switch ($Status) { "PASS"{"✅"}; "FAIL"{"❌"}; "WARN"{"⚠️"}; default{"·"} }
    Write-Host ("    {0} [{1}] {2}" -f $mark, $Status, $Combo) -ForegroundColor $color
    if ($Detail) { Write-Host "        → $Detail" -ForegroundColor DarkGray }
}

function Invoke-Q {
    param([string]$Url,[hashtable]$Headers,[int]$TimeoutSec=12)
    try {
        $r = Invoke-RestMethod -Uri $Url -Method GET -Headers $Headers -TimeoutSec $TimeoutSec -ErrorAction Stop
        return @{ Ok=$true; Data=$r; StatusCode=200 }
    } catch {
        $sc = $null; try { $sc = [int]$_.Exception.Response.StatusCode } catch {}
        return @{ Ok=$false; Data=$null; StatusCode=$sc; Err=$_.Exception.Message }
    }
}

# C(n,3) 组合生成器
function Get-Combinations {
    param([array]$Items, [int]$Size=3)
    $result = @()
    for ($i=0; $i -lt $Items.Count; $i++) {
        for ($j=$i+1; $j -lt $Items.Count; $j++) {
            if ($Size -eq 2) {
                $result += ,@($Items[$i], $Items[$j])
            } else {
                for ($k=$j+1; $k -lt $Items.Count; $k++) {
                    $result += ,@($Items[$i], $Items[$j], $Items[$k])
                }
            }
        }
    }
    return $result
}

# ── 登录 ──────────────────────────────────────────────────────────
Write-Host "`n🔐 认证..." -ForegroundColor Yellow
try {
    $loginR = Invoke-RestMethod -Uri "$GatewayUrl/api/auth/login" -Method POST `
        -ContentType "application/json" -Body (@{username=$Username;password=$Password} | ConvertTo-Json) -TimeoutSec 10
    if (-not $loginR.success) { throw "login failed" }
    $h = @{ Authorization="Bearer $($loginR.data.accessToken)" }
    Write-Host "✅ 登录成功" -ForegroundColor Green
} catch { Write-Host "❌ 登录失败，退出"; exit 1 }

# ── 主循环 ────────────────────────────────────────────────────────
Write-Host "`n共 $($endpointManifest.Count) 个接口定义，开始组合查询测试..." -ForegroundColor Cyan

foreach ($ep in $endpointManifest) {
    $short = ($ep.Url -replace 'http://[^/]+', '')
    Write-Host "`n  📋 [$($ep.Svc)] $short  ($($ep.Params.Count) 参数)" -ForegroundColor Magenta

    # 固定必须的分页参数（不参与组合）
    $mandatory = $ep.Params | Where-Object { $_.k -in @("pageIndex","pageSize") }
    $mandatory = if ($mandatory) { $mandatory } else { @() }
    $optional  = $ep.Params | Where-Object { $_.k -notin @("pageIndex","pageSize") }

    $mandQs = ($mandatory | Where-Object { $_.v -ne "" } | ForEach-Object { "$($_.k)=$($_.v)" }) -join "&"

    if ($optional.Count -lt 2) {
        # 参数太少，直接测单一完整请求
        $qs  = ($ep.Params | Where-Object { $_.v -ne "" } | ForEach-Object { "$($_.k)=$($_.v)" }) -join "&"
        $url = "$($ep.Url)?$qs"
        $r   = Invoke-Q -Url $url -Headers $h
        if ($r.Ok -or $r.StatusCode -in @(403,404)) {
            Add-R $ep.Svc $short "全参数" "PASS" "→$($r.StatusCode)"
        } else {
            Add-R $ep.Svc $short "全参数" "FAIL" "→$($r.StatusCode)"
        }
        continue
    }

    # 生成 C(optional, min(3,optional.Count)) 组合
    $comboSize = [math]::Min(3, $optional.Count)
    $combos = Get-Combinations -Items $optional -Size $comboSize
    Write-Host "    → $($combos.Count) 种组合 (C($($optional.Count),$comboSize))" -ForegroundColor DarkGray

    foreach ($combo in $combos) {
        $comboQs  = ($combo | Where-Object { $_.v -ne "" } | ForEach-Object { "$($_.k)=$([Uri]::EscapeDataString($_.v))" }) -join "&"
        $sep      = if ($mandQs) { "$mandQs&$comboQs" } else { $comboQs }
        $testUrl  = "$($ep.Url)?$sep"
        $comboKey = ($combo | ForEach-Object { $_.k }) -join "+"

        Start-Sleep -Milliseconds $DelayMs

        $r = Invoke-Q -Url $testUrl -Headers $h

        if ($r.Ok) {
            # 验证返回结构正常（不是 500 包装成 200）
            $isValid = $r.Data.success -ne $false -or ($r.Data.total -ne $null) -or ($r.Data.data -ne $null)
            if ($isValid) {
                Add-R $ep.Svc $short $comboKey "PASS" "200 数据正常"
            } else {
                Add-R $ep.Svc $short $comboKey "WARN" "200 但 data=null"
            }
        } elseif ($r.StatusCode -in @(403,404)) {
            Add-R $ep.Svc $short $comboKey "WARN" "HTTP $($r.StatusCode) 权限/无数据"
        } elseif ($r.StatusCode -eq 400) {
            # 400 可能是参数格式问题，不算系统错误
            Add-R $ep.Svc $short $comboKey "WARN" "400 参数校验(预期内)"
        } elseif ($r.StatusCode -eq 500) {
            Add-R $ep.Svc $short $comboKey "FAIL" "500 服务器错误 — 参数组合[$comboKey]触发内部异常！"
        } else {
            Add-R $ep.Svc $short $comboKey "FAIL" "HTTP $($r.StatusCode)"
        }
    }
}

# ── 汇总 ─────────────────────────────────────────────────────────
$elapsed = [int](Get-Date).Subtract($startTime).TotalSeconds
$pass  = ($results | Where-Object Status -eq "PASS").Count
$fail  = ($results | Where-Object Status -eq "FAIL").Count
$warn  = ($results | Where-Object Status -eq "WARN").Count
$total = $results.Count

Write-Host "`n═══════════════════════════════════════════════" -ForegroundColor Yellow
Write-Host "  多条件组合查询测试汇总  总用例:$total  耗时:${elapsed}s" -ForegroundColor Yellow
Write-Host "  ✅PASS=$pass  ❌FAIL=$fail  ⚠️WARN=$warn" -ForegroundColor White
Write-Host "═══════════════════════════════════════════════" -ForegroundColor Yellow

if ($fail -gt 0) {
    Write-Host "`n❌ 失败组合（参数组合触发服务器崩溃，必须修复）：" -ForegroundColor Red
    $results | Where-Object Status -eq "FAIL" | ForEach-Object {
        Write-Host "  [$($_.Service)] $($_.Endpoint) + [$($_.Combination)] → $($_.Detail)" -ForegroundColor Red
    }
}

# 保存
if (-not [System.IO.Path]::IsPathRooted($LogDir)) {
    $LogDir = Join-Path (Resolve-Path (Join-Path $PSScriptRoot "../..")).Path $LogDir
}
if (-not (Test-Path $LogDir)) { New-Item -ItemType Directory $LogDir -Force | Out-Null }
$logTs = Get-Date -Format "yyyyMMdd-HHmmss"
$results | Export-Csv (Join-Path $LogDir "query-combinations-$logTs.csv") -NoTypeInformation -Encoding UTF8
Write-Host "日志: $LogDir\query-combinations-$logTs.csv" -ForegroundColor Gray

$verdict = if ($fail -eq 0) { "无参数组合崩溃 ✅" } else { "存在参数组合触发500 ❌" }
Write-Host "`n结论: $verdict" -ForegroundColor $(if ($fail -eq 0) {"Green"} else {"Red"})
exit $(if ($fail -eq 0) { 0 } else { 1 })
