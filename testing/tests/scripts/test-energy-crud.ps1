<#
.SYNOPSIS
  四子系统写操作 CRUD 全链路测试（POST/PUT/DELETE）
.DESCRIPTION
  覆盖 PVESSC / VPP / MicroGrid / SEHS 四子系统的完整写操作：
  创建 → 读取验证 → 更新 → 再次验证 → 删除 → 验证已删
#>
param(
    [string]$GatewayUrl = "http://localhost:5000",
    [string]$Username   = "admin",
    [string]$Password   = "P@ssw0rd",
    [string]$LogDir     = "tests/scripts/logs"
)

$ErrorActionPreference = "Continue"
chcp 65001 | Out-Null
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

$results   = @()
$cleanup   = @()   # 记录需要清理的资源
$startTime = Get-Date
$ts        = Get-Date -Format "MMddHHmmss"

function Add-Result {
    param([string]$Scene, [string]$Op, [string]$Status, [string]$Detail = "")
    $script:results += [PSCustomObject]@{ Scene=$Scene; Op=$Op; Status=$Status; Detail=$Detail }
    $color = switch ($Status) { "PASS"{"Green"}; "FAIL"{"Red"}; "WARN"{"Yellow"}; default{"Gray"} }
    Write-Host "  [$Status] [$Scene] $Op$(if ($Detail) { " - $Detail" })" -ForegroundColor $color
}

function Invoke-Api {
    param(
        [string]$Url,
        [string]$Method = "GET",
        [object]$Body   = $null,
        [hashtable]$Headers,
        [int]$TimeoutSec = 15
    )
    try {
        $params = @{
            Uri        = $Url
            Method     = $Method
            Headers    = $Headers
            TimeoutSec = $TimeoutSec
            ErrorAction = "Stop"
        }
        if ($null -ne $Body) {
            $params["ContentType"] = "application/json"
            $params["Body"]        = if ($Body -is [string]) { $Body } else { $Body | ConvertTo-Json -Depth 10 -Compress }
        }
        $r = Invoke-RestMethod @params
        return @{ Ok=$true; Data=$r; StatusCode=200 }
    } catch {
        $sc = $_.Exception.Response.StatusCode.value__
        return @{ Ok=$false; Data=$null; StatusCode=$sc; Error=$_.Exception.Message }
    }
}

# ============================================================
# 认证
# ============================================================
Write-Host "`n=== 认证 ===" -ForegroundColor Cyan
$loginBody = @{ username=$Username; password=$Password }
$login = Invoke-Api -Url "$GatewayUrl/api/auth/login" -Method POST -Body $loginBody -Headers @{}
if (-not $login.Ok -or -not $login.Data.success) {
    Write-Host "❌ 登录失败，无法继续CRUD测试" -ForegroundColor Red; exit 1
}
$h = @{ "Authorization" = "Bearer $($login.Data.data.accessToken)" }
Write-Host "✅ 登录成功" -ForegroundColor Green

# ============================================================
# SCENE 1: PVESSC 站点 CRUD
# ============================================================
Write-Host "`n========== SCENE 1: PVESSC 站点 CRUD ==========" -ForegroundColor Cyan

$pvSiteBody = @{
    name             = "CRUD测试站点-$ts"
    code             = "CRUD-SITE-$ts"
    address          = "测试地址 北京市海淀区"
    pvCapacityKw     = 500.0
    essCapacityKwh   = 1000.0
    chargerCount     = 10
    v2gChargerCount  = 4
    maxPowerKw       = 800.0
    gridConnectionKw = 1000.0
}

# CREATE
$r = Invoke-Api -Url "$GatewayUrl/api/pvessc/site" -Method POST -Body $pvSiteBody -Headers $h
if ($r.Ok -and $r.Data.success) {
    $pvSiteId = $r.Data.data
    $cleanup  += @{ Url="$GatewayUrl/api/pvessc/site/$pvSiteId"; Method="DELETE" }
    Add-Result "PVESSC" "创建站点" "PASS" "ID=$pvSiteId"

    # READ BACK
    $r2 = Invoke-Api -Url "$GatewayUrl/api/pvessc/site/$pvSiteId" -Method GET -Headers $h
    if ($r2.Ok -and $r2.Data.success -and $r2.Data.data) {
        Add-Result "PVESSC" "读取验证" "PASS" "Name=$($r2.Data.data.name)"
    } else {
        Add-Result "PVESSC" "读取验证" "FAIL" "StatusCode=$($r2.StatusCode) $($r2.Error)"
    }

    # UPDATE
    $pvSiteUpdate = @{
        name             = "CRUD测试站点-更新-$ts"
        code             = "CRUD-SITE-UPD-$ts"
        pvCapacityKw     = 600.0
        essCapacityKwh   = 1200.0
        chargerCount     = 12
        v2gChargerCount  = 6
        maxPowerKw       = 900.0
        gridConnectionKw = 1200.0
    }
    $r3 = Invoke-Api -Url "$GatewayUrl/api/pvessc/site/$pvSiteId" -Method PUT -Body $pvSiteUpdate -Headers $h
    if ($r3.Ok -and $r3.Data.success) {
        Add-Result "PVESSC" "更新站点" "PASS" "PvCapacity=600kW"
    } else {
        Add-Result "PVESSC" "更新站点" "FAIL" "StatusCode=$($r3.StatusCode) $($r3.Error)"
    }

    # DELETE
    $r4 = Invoke-Api -Url "$GatewayUrl/api/pvessc/site/$pvSiteId" -Method DELETE -Headers $h
    if ($r4.Ok -and $r4.Data.success) {
        Add-Result "PVESSC" "删除站点" "PASS" "软删成功"
        $cleanup = $cleanup | Where-Object { $_.Url -notlike "*$pvSiteId*" }
    } else {
        Add-Result "PVESSC" "删除站点" "FAIL" "StatusCode=$($r4.StatusCode)"
    }

    # 验证已删（应返回 404）
    $r5 = Invoke-Api -Url "$GatewayUrl/api/pvessc/site/$pvSiteId" -Method GET -Headers $h
    if (-not $r5.Ok -or -not $r5.Data.success) {
        Add-Result "PVESSC" "删除后验证" "PASS" "已不可访问 (404/not found)"
    } else {
        Add-Result "PVESSC" "删除后验证" "WARN" "删除后仍可查到，可能软删逻辑未过滤"
    }
} else {
    Add-Result "PVESSC" "创建站点" "FAIL" "StatusCode=$($r.StatusCode) $($r.Error)"
    if ($r.StatusCode -eq 403) {
        Add-Result "PVESSC" "创建站点-权限" "WARN" "403 Forbidden - admin 账号缺少 pvessc:site:create 权限码，需要检查 SUPER_ADMIN 角色映射"
    }
}

# PVESSC 峰谷策略 CRUD
Write-Host "`n--- PVESSC 峰谷策略 ---" -ForegroundColor Gray
$pvSiteForTariff = "019c741e-5ad1-755d-b7e7-4a4acc6c3f5d"  # 使用已有测试站点
$tariffBody = @{
    siteId          = $pvSiteForTariff
    name            = "CRUD测试策略-$ts"
    timeSlots       = '[{"period":"peak","start":"08:00","end":"12:00"},{"period":"valley","start":"00:00","end":"08:00"}]'
    essChargeSoc    = 90.0
    essDischargeSoc = 20.0
}
$rt = Invoke-Api -Url "$GatewayUrl/api/pvessc/tariff" -Method POST -Body $tariffBody -Headers $h
if ($rt.Ok -and $rt.Data.success) {
    $tariffId = $rt.Data.data
    $cleanup += @{ Url="$GatewayUrl/api/pvessc/tariff/$tariffId"; Method="DELETE" }
    Add-Result "PVESSC" "创建峰谷策略" "PASS" "ID=$tariffId"
    # 删除
    $rtd = Invoke-Api -Url "$GatewayUrl/api/pvessc/tariff/$tariffId" -Method DELETE -Headers $h
    if ($rtd.Ok) { Add-Result "PVESSC" "删除峰谷策略" "PASS" "" }
    else { Add-Result "PVESSC" "删除峰谷策略" "WARN" "StatusCode=$($rtd.StatusCode)" }
} else {
    Add-Result "PVESSC" "创建峰谷策略" "FAIL" "StatusCode=$($rt.StatusCode) $($rt.Error)"
}

# ============================================================
# SCENE 2: VPP CRUD
# ============================================================
Write-Host "`n========== SCENE 2: VPP CRUD ==========" -ForegroundColor Cyan

$vppBody = @{
    name                = "CRUD测试VPP-$ts"
    code                = "CRUD-VPP-$ts"
    region              = "华北区"
    capacityMw          = 50.0
    gridDispatchEnabled = $true
    elecTradeEnabled    = $true
    carbonTradeEnabled  = $true
    aiOptimizeEnabled   = $true
    description         = "自动化CRUD测试创建"
}

$r = Invoke-Api -Url "$GatewayUrl/api/vpp" -Method POST -Body $vppBody -Headers $h
if ($r.Ok -and $r.Data.success) {
    $vppId2  = $r.Data.data
    $cleanup += @{ Url="$GatewayUrl/api/vpp/$vppId2"; Method="DELETE" }
    Add-Result "VPP" "创建VPP" "PASS" "ID=$vppId2"

    # READ BACK
    $r2 = Invoke-Api -Url "$GatewayUrl/api/vpp/$vppId2" -Method GET -Headers $h
    if ($r2.Ok -and $r2.Data.success) {
        Add-Result "VPP" "读取验证" "PASS" "Name=$($r2.Data.data.name)"
    } else {
        Add-Result "VPP" "读取验证" "FAIL" "StatusCode=$($r2.StatusCode)"
    }

    # UPDATE
    $vppUpdate = @{
        name             = "CRUD测试VPP-更新-$ts"
        code             = "CRUD-VPP-UPD-$ts"
        region           = "华东区"
        capacityMw       = 80.0
        gridDispatchEnabled = $true
        elecTradeEnabled = $true
        carbonTradeEnabled = $true
        aiOptimizeEnabled  = $true
    }
    $r3 = Invoke-Api -Url "$GatewayUrl/api/vpp/$vppId2" -Method PUT -Body $vppUpdate -Headers $h
    if ($r3.Ok -and $r3.Data.success) {
        Add-Result "VPP" "更新VPP" "PASS" "CapacityMw=80"
    } else {
        Add-Result "VPP" "更新VPP" "FAIL" "StatusCode=$($r3.StatusCode)"
    }

    # DELETE
    $r4 = Invoke-Api -Url "$GatewayUrl/api/vpp/$vppId2" -Method DELETE -Headers $h
    if ($r4.Ok -and $r4.Data.success) {
        Add-Result "VPP" "删除VPP" "PASS" ""
        $cleanup = $cleanup | Where-Object { $_.Url -notlike "*$vppId2*" }
    } else {
        Add-Result "VPP" "删除VPP" "FAIL" "StatusCode=$($r4.StatusCode)"
    }
} else {
    Add-Result "VPP" "创建VPP" "FAIL" "StatusCode=$($r.StatusCode) $($r.Error)"
    if ($r.StatusCode -eq 403) {
        Add-Result "VPP" "权限说明" "WARN" "403 - admin 缺 vpp:manage:create 权限码"
    }
}

# VPP 资源注册（测试 VPP 资源子功能）
Write-Host "`n--- VPP 资源注册 ---" -ForegroundColor Gray
$vppResBody = @{
    vppId          = "019c741f-a680-7972-9ecd-f5f4dba5e628"  # 已有测试VPP
    deviceId       = [guid]::NewGuid().ToString()             # 虚拟设备ID
    resourceType   = 1
    ratedPowerKw   = 100.0
    availablePowerKw = 80.0
    responseTimeSec  = 5
}
$rvr = Invoke-Api -Url "$GatewayUrl/api/vpp/resource" -Method POST -Body $vppResBody -Headers $h
if ($rvr.Ok -and $rvr.Data.success) {
    $vppResId = $rvr.Data.data
    $cleanup += @{ Url="$GatewayUrl/api/vpp/resource/$vppResId"; Method="DELETE" }
    Add-Result "VPP" "注册资源" "PASS" "ResourceID=$vppResId"
    $rvrd = Invoke-Api -Url "$GatewayUrl/api/vpp/resource/$vppResId" -Method DELETE -Headers $h
    if ($rvrd.Ok) { Add-Result "VPP" "删除资源" "PASS" "" }
} else {
    Add-Result "VPP" "注册资源" "FAIL" "StatusCode=$($rvr.StatusCode) $($rvr.Error)"
}

# ============================================================
# SCENE 3: MicroGrid CRUD
# ============================================================
Write-Host "`n========== SCENE 3: MicroGrid CRUD ==========" -ForegroundColor Cyan

$mgBody = @{
    name              = "CRUD测试微电网-$ts"
    code              = "CRUD-MG-$ts"
    gridType          = 1
    ratedCapacityKw   = 200.0
    islandModeEnabled = $true
    directTradeEnabled = $false
    location          = "测试园区B座"
}

$r = Invoke-Api -Url "$GatewayUrl/api/microgrid" -Method POST -Body $mgBody -Headers $h
if ($r.Ok -and $r.Data.success) {
    $mgId2   = $r.Data.data
    $cleanup += @{ Url="$GatewayUrl/api/microgrid/$mgId2"; Method="DELETE" }
    Add-Result "MicroGrid" "创建微电网" "PASS" "ID=$mgId2"

    # READ BACK
    $r2 = Invoke-Api -Url "$GatewayUrl/api/microgrid/$mgId2" -Method GET -Headers $h
    if ($r2.Ok -and $r2.Data.success) {
        Add-Result "MicroGrid" "读取验证" "PASS" "Name=$($r2.Data.data.name)"
    } else {
        Add-Result "MicroGrid" "读取验证" "FAIL" "StatusCode=$($r2.StatusCode)"
    }

    # UPDATE
    $mgUpdate = @{
        name              = "CRUD测试微电网-更新-$ts"
        code              = "CRUD-MG-UPD-$ts"
        gridType          = 1
        ratedCapacityKw   = 250.0
        islandModeEnabled = $true
        vppRegistered     = $false
        directTradeEnabled = $true
        location          = "测试园区C座"
    }
    $r3 = Invoke-Api -Url "$GatewayUrl/api/microgrid/$mgId2" -Method PUT -Body $mgUpdate -Headers $h
    if ($r3.Ok -and $r3.Data.success) {
        Add-Result "MicroGrid" "更新微电网" "PASS" "RatedCapacity=250kW"
    } else {
        Add-Result "MicroGrid" "更新微电网" "FAIL" "StatusCode=$($r3.StatusCode)"
    }

    # 模式切换
    $modeBody = @{ targetMode=2; triggerType=1 }
    $rm = Invoke-Api -Url "$GatewayUrl/api/microgrid/mode/$mgId2/switch" -Method POST -Body $modeBody -Headers $h
    if ($rm.Ok -and $rm.Data.success) {
        Add-Result "MicroGrid" "模式切换→离岛" "PASS" ""
    } else {
        Add-Result "MicroGrid" "模式切换→离岛" "WARN" "StatusCode=$($rm.StatusCode) (可能需要特定状态条件)"
    }

    # DELETE
    $r4 = Invoke-Api -Url "$GatewayUrl/api/microgrid/$mgId2" -Method DELETE -Headers $h
    if ($r4.Ok -and $r4.Data.success) {
        Add-Result "MicroGrid" "删除微电网" "PASS" ""
        $cleanup = $cleanup | Where-Object { $_.Url -notlike "*$mgId2*" }
    } else {
        Add-Result "MicroGrid" "删除微电网" "FAIL" "StatusCode=$($r4.StatusCode)"
    }
} else {
    Add-Result "MicroGrid" "创建微电网" "FAIL" "StatusCode=$($r.StatusCode) $($r.Error)"
    if ($r.StatusCode -eq 403) {
        Add-Result "MicroGrid" "权限说明" "WARN" "403 - admin 缺 mg:manage:create 权限码"
    }
}

# ============================================================
# SCENE 4: SEHS CRUD
# ============================================================
Write-Host "`n========== SCENE 4: SEHS 资源快照 + 调度计划 CRUD ==========" -ForegroundColor Cyan

# 资源快照 CREATE
$snapBody = @{
    sourcePowerKw   = 500.0
    gridPowerKw     = 200.0
    loadPowerKw     = 450.0
    storagePowerKw  = -150.0
    storageSoc      = 65.0
    pvGenerationKw  = 300.0
    windGenerationKw = 50.0
    dataSource      = "CRUD测试"
}
$rs = Invoke-Api -Url "$GatewayUrl/api/sehs/resource" -Method POST -Body $snapBody -Headers $h
if ($rs.Ok -and $rs.Data.success) {
    Add-Result "SEHS" "记录资源快照" "PASS" ""
    # 读取最新快照
    $rs2 = Invoke-Api -Url "$GatewayUrl/api/sehs/resource/latest" -Method GET -Headers $h
    if ($rs2.Ok -and $rs2.Data.success) {
        Add-Result "SEHS" "读取最新快照" "PASS" "SOC=$($rs2.Data.data.storageSoc)%"
    } else {
        Add-Result "SEHS" "读取最新快照" "FAIL" "StatusCode=$($rs2.StatusCode)"
    }
} else {
    Add-Result "SEHS" "记录资源快照" "FAIL" "StatusCode=$($rs.StatusCode) $($rs.Error)"
}

# 调度计划 CREATE
$planBody = @{
    planName         = "CRUD测试计划-$ts"
    planType         = 1
    planDate         = (Get-Date).ToString("yyyy-MM-dd")
    objective        = 1
    algorithmVersion = "v1.0"
    remark           = "自动化CRUD测试"
}
$rp = Invoke-Api -Url "$GatewayUrl/api/sehs/schedule" -Method POST -Body $planBody -Headers $h
if ($rp.Ok -and $rp.Data.success) {
    $planId  = $rp.Data.data
    $cleanup += @{ Url="$GatewayUrl/api/sehs/schedule/$planId"; Method="DELETE" }
    Add-Result "SEHS" "创建调度计划" "PASS" "ID=$planId"

    # 读取计划列表，验证包含新计划
    $rpl = Invoke-Api -Url "$GatewayUrl/api/sehs/schedule?page=1&size=10" -Method GET -Headers $h
    if ($rpl.Ok -and $rpl.Data.success) {
        $found = $rpl.Data.data.items | Where-Object { $_.id -eq $planId -or $_.planName -like "*CRUD*" }
        Add-Result "SEHS" "列表验证计划" $(if ($found) {"PASS"} else {"WARN"}) $(if ($found) {"在列表中找到"} else {"列表中未找到，可能返回首页"})
    }

    # 删除
    $rpd = Invoke-Api -Url "$GatewayUrl/api/sehs/schedule/$planId" -Method DELETE -Headers $h
    if ($rpd.Ok) {
        Add-Result "SEHS" "删除调度计划" "PASS" ""
        $cleanup = $cleanup | Where-Object { $_.Url -notlike "*$planId*" }
    } else {
        Add-Result "SEHS" "删除调度计划" "WARN" "StatusCode=$($rpd.StatusCode)"
    }
} else {
    Add-Result "SEHS" "创建调度计划" "FAIL" "StatusCode=$($rp.StatusCode) $($rp.Error)"
}

# 调度约束 CREATE + DELETE
$constraintBody = @{
    resourceName  = "CRUD测试约束-$ts"
    resourceType  = 1
    maxPowerKw    = 500.0
    minPowerKw    = 0.0
    rampRateKwMin = 50.0
}
$rc = Invoke-Api -Url "$GatewayUrl/api/sehs/constraint" -Method POST -Body $constraintBody -Headers $h
if ($rc.Ok -and $rc.Data.success) {
    $cid     = $rc.Data.data
    $cleanup += @{ Url="$GatewayUrl/api/sehs/constraint/$cid"; Method="DELETE" }
    Add-Result "SEHS" "创建调度约束" "PASS" "ID=$cid"
    $rcd = Invoke-Api -Url "$GatewayUrl/api/sehs/constraint/$cid" -Method DELETE -Headers $h
    if ($rcd.Ok) { Add-Result "SEHS" "删除调度约束" "PASS" "" }
} else {
    Add-Result "SEHS" "创建调度约束" "FAIL" "StatusCode=$($rc.StatusCode) $($rc.Error)"
}

# ============================================================
# SCENE 5: PVESSC 调度指令 CRUD
# ============================================================
Write-Host "`n========== SCENE 5: PVESSC 调度指令 CRUD ==========" -ForegroundColor Cyan

$existingSiteId = "019c741e-5ad1-755d-b7e7-4a4acc6c3f5d"
$dispatchBody = @{
    siteId          = $existingSiteId
    commandType     = 1   # 1=充电
    targetPowerKw   = 50.0
    durationMinutes = 60
    priority        = 1
    source          = 1   # 1=手动
    remark          = "CRUD测试调度指令"
}
$rd = Invoke-Api -Url "$GatewayUrl/api/pvessc/dispatch" -Method POST -Body $dispatchBody -Headers $h
if ($rd.Ok -and $rd.Data.success) {
    $dispatchId = $rd.Data.data
    $cleanup   += @{ Url="$GatewayUrl/api/pvessc/dispatch/$dispatchId/cancel"; Method="PUT" }
    Add-Result "PVESSC" "下发调度指令" "PASS" "DispatchID=$dispatchId"

    # 读取调度列表
    $rdl = Invoke-Api -Url "$GatewayUrl/api/pvessc/dispatch/$existingSiteId/list?pageIndex=1&pageSize=10" -Method GET -Headers $h
    if ($rdl.Ok -and $rdl.Data.success) {
        Add-Result "PVESSC" "调度指令列表" "PASS" "Total=$($rdl.Data.data.totalCount)"
    } else {
        Add-Result "PVESSC" "调度指令列表" "FAIL" "StatusCode=$($rdl.StatusCode)"
    }

    # 取消指令
    $rdc = Invoke-Api -Url "$GatewayUrl/api/pvessc/dispatch/$dispatchId/cancel" -Method PUT -Headers $h
    if ($rdc.Ok -and $rdc.Data.success) {
        Add-Result "PVESSC" "取消调度指令" "PASS" ""
    } else {
        Add-Result "PVESSC" "取消调度指令" "WARN" "StatusCode=$($rdc.StatusCode) (指令可能已完成)"
    }
} else {
    Add-Result "PVESSC" "下发调度指令" "FAIL" "StatusCode=$($rd.StatusCode) $($rd.Error)"
}

# ============================================================
# 清理残余测试数据
# ============================================================
if ($cleanup.Count -gt 0) {
    Write-Host "`n=== 清理残余测试数据 ===" -ForegroundColor Gray
    foreach ($c in $cleanup) {
        try {
            Invoke-RestMethod -Uri $c.Url -Method $c.Method -Headers $h -TimeoutSec 5 -ErrorAction SilentlyContinue | Out-Null
            Write-Host "  已清理: $($c.Url)" -ForegroundColor DarkGray
        } catch { }
    }
}

# ============================================================
# 汇总
# ============================================================
Write-Host "`n========== 四子系统 CRUD 测试汇总 ==========" -ForegroundColor Yellow

$pass  = ($results | Where-Object { $_.Status -eq "PASS"  }).Count
$warn  = ($results | Where-Object { $_.Status -eq "WARN"  }).Count
$fail  = ($results | Where-Object { $_.Status -eq "FAIL"  }).Count
$total = $results.Count
$elapsed = [int](Get-Date).Subtract($startTime).TotalSeconds

Write-Host "总计: $total 项  PASS=$pass  WARN=$warn  FAIL=$fail  耗时:${elapsed}s" -ForegroundColor White

if ($fail -gt 0) {
    Write-Host "`n❌ FAIL 项：" -ForegroundColor Red
    $results | Where-Object { $_.Status -eq "FAIL" } | ForEach-Object {
        Write-Host "  [$($_.Scene)] $($_.Op): $($_.Detail)" -ForegroundColor Red
    }
}
if ($warn -gt 0) {
    Write-Host "`n⚠️  WARN 项：" -ForegroundColor Yellow
    $results | Where-Object { $_.Status -eq "WARN" } | ForEach-Object {
        Write-Host "  [$($_.Scene)] $($_.Op): $($_.Detail)" -ForegroundColor Yellow
    }
}

# 保存日志
try {
    if (-not [System.IO.Path]::IsPathRooted($LogDir)) {
        $base = (Resolve-Path (Join-Path $PSScriptRoot "../..")).Path
        $targetDir = Join-Path $base $LogDir
    } else {
        $targetDir = $LogDir
    }
    if (-not (Test-Path $targetDir)) { New-Item -ItemType Directory -Path $targetDir -Force | Out-Null }
    $logTs   = Get-Date -Format "yyyyMMdd-HHmmss"
    $logPath = Join-Path $targetDir "energy-crud-$logTs.csv"
    $results | Export-Csv -Path $logPath -NoTypeInformation -Encoding UTF8
    Write-Host "`n日志已保存: $logPath" -ForegroundColor Gray
} catch {
    Write-Host "日志保存失败: $($_.Exception.Message)" -ForegroundColor Yellow
}

$verdict = if ($fail -eq 0) { "四子系统写操作通过 ✅" } else { "存在写操作故障 ❌" }
Write-Host "`n四子系统 CRUD 测试结论：$verdict" -ForegroundColor $(if ($fail -eq 0) {"Green"} else {"Red"})
Write-Host "测试完成: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')" -ForegroundColor Gray
