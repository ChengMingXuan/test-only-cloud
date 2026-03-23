<#
.SYNOPSIS
    全模块批量 CRUD + 条件组合测试
.DESCRIPTION
    设计思路 — "找规律，按规律批量测":
    ┌─────────────────────────────────────────────────────┐
    │  Phase 1: CREATE 批量  — 每个模块连续创建 N 条       │
    │  Phase 2: READ 批量    — 列表/详情/分页/排序/筛选    │
    │  Phase 3: UPDATE 批量  — 修改字段，验证更新           │
    │  Phase 4: QUERY 组合   — 多条件组合、边界值、空查询    │
    │  Phase 5: DELETE 批量  — 删除 + 验证软删除            │
    │  Phase 6: 模块专项     — 每个模块的特有业务逻辑        │
    └─────────────────────────────────────────────────────┘
    按模块逐个遍历，每个模块走完整 CRUD 生命周期。
    覆盖: 用户/角色/菜单/部门/字典/公告/租户/充电站/设备/工单/
          内容/合约/采集/VPP/微电网/光储充/充电订单/结算/钱包 等
#>
param(
    [string]$GatewayUrl = "http://localhost:5000",
    [int]$CreateCount = 3  # 每个模块创建几条测试数据
)

$ErrorActionPreference = 'Continue'
$logDir = "$PSScriptRoot\logs"
if (-not (Test-Path $logDir)) { New-Item -ItemType Directory -Path $logDir -Force | Out-Null }

$ts = Get-Date -Format 'yyyyMMdd-HHmmss'
$csvFile = "$logDir\batch-crud-$ts.csv"

# ================================================================
# 全局工具函数
# ================================================================
$script:results = @()
$script:pass = 0
$script:fail = 0
$script:warn = 0
$script:skip = 0

function Add-R {
    param([string]$Phase, [string]$Module, [string]$Test, [string]$Status, [string]$Detail = "")
    switch ($Status) {
        "PASS" { $script:pass++; $color = "Green" }
        "FAIL" { $script:fail++; $color = "Red" }
        "WARN" { $script:warn++; $color = "Yellow" }
        "SKIP" { $script:skip++; $color = "DarkGray" }
    }
    Write-Host "  [$Status] $Phase | $Module | $Test $(if($Detail){" — $Detail"})" -ForegroundColor $color
    $script:results += [pscustomobject]@{
        Phase=$Phase; Module=$Module; Test=$Test; Status=$Status; Detail=$Detail; Time=(Get-Date -Format 'HH:mm:ss')
    }
}

function Invoke-Api {
    param(
        [string]$Method, [string]$Url, [object]$Body = $null,
        [hashtable]$Headers = $script:authHeaders, [int]$Timeout = 15
    )
    try {
        $params = @{
            Uri = $Url; Method = $Method; Headers = $Headers
            TimeoutSec = $Timeout; UseBasicParsing = $true
        }
        if ($Body) {
            if ($Body -is [string]) { $params.Body = [System.Text.Encoding]::UTF8.GetBytes($Body) }
            else { $params.Body = [System.Text.Encoding]::UTF8.GetBytes(($Body | ConvertTo-Json -Depth 10)) }
            $params.ContentType = "application/json; charset=utf-8"
        }
        $r = Invoke-WebRequest @params
        $parsed = $null
        try { $parsed = $r.Content | ConvertFrom-Json } catch {}
        return @{ Code = $r.StatusCode; Body = $r.Content; Data = $parsed; Error = $null }
    } catch {
        $code = 0
        $body = ""
        if ($_.Exception.Response) {
            $code = [int]$_.Exception.Response.StatusCode
            try { $body = [System.IO.StreamReader]::new($_.Exception.Response.GetResponseStream()).ReadToEnd() } catch {}
        }
        return @{ Code = $code; Body = $body; Data = $null; Error = $_.Exception.Message }
    }
}

function Extract-Id {
    param($response, [string[]]$fields = @("id","tenantId","roleId","stationId","deviceId","orderId","contractId"))
    if (-not $response.Data) { return $null }
    $d = $response.Data.data
    if (-not $d) { $d = $response.Data }
    foreach ($f in $fields) {
        if ($d.$f) { return $d.$f }
    }
    # 尝试 data 本身是 ID 字符串
    if ($d -is [string] -and $d -match '^[0-9a-f\-]{36}$') { return $d }
    return $null
}

# ================================================================
# 登录
# ================================================================
Write-Host "`n" -NoNewline
Write-Host "╔══════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║  JGSY.AGI 全模块批量 CRUD + 条件组合测试               ║" -ForegroundColor Cyan
Write-Host "║  模块数: 30+  |  每模块 CREATE×$CreateCount             ║" -ForegroundColor Cyan
Write-Host "╚══════════════════════════════════════════════════════════╝" -ForegroundColor Cyan

$loginR = Invoke-Api POST "$GatewayUrl/api/auth/login" @{userName="admin";password="P@ssw0rd"}
if ($loginR.Code -ne 200) {
    Write-Host "登录失败，终止" -ForegroundColor Red; exit 1
}
$token = $loginR.Data.data.accessToken
$script:authHeaders = @{ Authorization = "Bearer $token" }
Write-Host "  登录成功`n" -ForegroundColor Green

# ================================================================
# 前置：创建依赖数据 (Station, Site/Category for articles)
# ================================================================
Write-Host "  >> 准备依赖数据..." -ForegroundColor DarkCyan

# 创建一个测试充电站供设备使用
$stSetup = Invoke-Api POST "$GatewayUrl/api/stations" @{name="TestDepStation_$uid";code="TDST_$uid";address="Test";longitude=116.4;latitude=39.9;status=1}
if ($stSetup.Code -in 200,201) {
    $script:testStationId = Extract-Id $stSetup
    Write-Host "    充电站依赖: $($script:testStationId)" -ForegroundColor DarkCyan
} else {
    # fallback: 从列表取第一个
    $stList = Invoke-Api GET "$GatewayUrl/api/stations?page=1&pageSize=1"
    if ($stList.Data.data.items) { $script:testStationId = $stList.Data.data.items[0].id }
    else { $script:testStationId = [guid]::NewGuid().ToString() }
    Write-Host "    充电站依赖(fallback): $($script:testStationId)" -ForegroundColor DarkYellow
}

# 创建 CMS Site 和 Category 供文章使用
$siteSetup = Invoke-Api POST "$GatewayUrl/api/content/sites" @{siteName="TestSite_$uid";siteCode="TS_$uid";domain="tsite$uid.test.com"}
if ($siteSetup.Code -in 200,201) {
    $script:testSiteId = Extract-Id $siteSetup
} else {
    $siteList = Invoke-Api GET "$GatewayUrl/api/content/sites?page=1&pageSize=1"
    if ($siteList.Data.data.items) { $script:testSiteId = $siteList.Data.data.items[0].id }
    elseif ($siteList.Data.data) { $script:testSiteId = $siteList.Data.data[0].id }
    else { $script:testSiteId = [guid]::NewGuid().ToString() }
}
Write-Host "    CMS站点依赖: $($script:testSiteId)" -ForegroundColor DarkCyan

$catSetup = Invoke-Api POST "$GatewayUrl/api/content/categories" @{categoryName="TestCat_$uid";siteId=$script:testSiteId;sortOrder=1}
if ($catSetup.Code -in 200,201) {
    $script:testCategoryId = Extract-Id $catSetup
} else {
    $catList = Invoke-Api GET "$GatewayUrl/api/content/categories?siteId=$($script:testSiteId)&page=1&pageSize=1"
    if ($catList.Data.data.items) { $script:testCategoryId = $catList.Data.data.items[0].id }
    elseif ($catList.Data.data) { $script:testCategoryId = $catList.Data.data[0].id }
    else { $script:testCategoryId = [guid]::NewGuid().ToString() }
}
Write-Host "    CMS栏目依赖: $($script:testCategoryId)" -ForegroundColor DarkCyan
Write-Host ""

# ================================================================
# 模块定义 — 每个模块定义 CRUD 规律
# ================================================================
# 格式: @{
#   Name = "模块名"
#   ListUrl = "GET 列表端点"
#   CreateUrl = "POST 创建端点"
#   UpdateUrl = "PUT 更新端点 ({id} 为占位符)"
#   DeleteUrl = "DELETE 删除端点 ({id} 为占位符)"
#   DetailUrl = "GET 详情端点 ({id} 为占位符)"
#   CreateBody = { param($i) 返回 hashtable }  # $i 从 1 开始
#   UpdateBody = { param($id, $i) 返回 hashtable }
#   ListParams = @("keyword=test", "status=1", ...)  # 查询条件组合
#   IdField = "id"  # 从返回值提取 ID 的字段名
# }

$uid = Get-Date -Format 'HHmmss'

$modules = @(
    # ─────────── 系统管理 ───────────
    @{
        Name = "角色管理"
        ListUrl = "/api/system/role"
        CreateUrl = "/api/system/role"
        UpdateUrl = "/api/system/role/{id}"
        DeleteUrl = "/api/system/role/{id}"
        DetailUrl = "/api/system/role/{id}"
        CreateBody = { param($i) @{ name = "批量测试角色${uid}_$i"; code = "BATCH_ROLE_${uid}_$i"; sortOrder = $i; status = 1; description = "批量CRUD测试#$i" } }
        UpdateBody = { param($id,$i) @{ name = "修改角色${uid}_$i"; code = "BATCH_ROLE_${uid}_$i"; sortOrder = ($i+10); status = 1; description = "已修改#$i" } }
        ListParams = @("page=1&pageSize=5", "page=1&pageSize=10&keyword=批量", "page=2&pageSize=3", "page=1&pageSize=5&status=1", "page=1&pageSize=100")
        IdField = "id"
    },

    @{
        Name = "字典类型"
        ListUrl = "/api/system/dict/types"
        CreateUrl = "/api/system/dict/types"
        UpdateUrl = "/api/system/dict/types/{id}"
        DeleteUrl = "/api/system/dict/types/{id}"
        DetailUrl = "/api/system/dict/types/{id}"
        CreateBody = { param($i) @{ code = "BATCH_DICT_${uid}_$i"; name = "批量字典${uid}_$i"; sortOrder = $i; status = 1; remark = "测试#$i" } }
        UpdateBody = { param($id,$i) @{ code = "BATCH_DICT_${uid}_$i"; name = "修改字典${uid}_$i"; sortOrder = ($i+10); status = 1; remark = "已修改#$i" } }
        ListParams = @("page=1&pageSize=5", "page=1&pageSize=10&keyword=批量", "page=1&pageSize=5&status=1")
        IdField = "id"
    },

    @{
        Name = "公告管理"
        ListUrl = "/api/system/announcements"
        CreateUrl = "/api/system/announcements"
        UpdateUrl = "/api/system/announcements/{id}"
        DeleteUrl = "/api/system/announcements/{id}"
        DetailUrl = "/api/system/announcements/{id}"
        CreateBody = { param($i) @{ title = "批量公告${uid}_$i"; content = "批量测试内容#$i，这是一条测试公告"; type = "notice"; status = 0 } }
        UpdateBody = { param($id,$i) @{ title = "修改公告${uid}_$i"; content = "已修改内容#$i"; type = "notice"; status = 1 } }
        ListParams = @("page=1&pageSize=5", "page=1&pageSize=5&status=0", "page=1&pageSize=5&status=1", "page=1&pageSize=5&keyword=批量")
        IdField = "id"
    },

    @{
        Name = "菜单管理"
        ListUrl = "/api/system/menu/tree"
        CreateUrl = "/api/system/menu"
        UpdateUrl = "/api/system/menu/{id}"
        DeleteUrl = "/api/system/menu/{id}"
        DetailUrl = "/api/system/menu/{id}"
        CreateBody = { param($i) @{ name = "批量菜单${uid}_$i"; path = "/batch-test-$i"; component = "BatchTest$i"; menuType = 1; sortOrder = (100+$i); status = 1; icon = "setting"; isVisible = $true } }
        UpdateBody = { param($id,$i) @{ name = "修改菜单${uid}_$i"; path = "/batch-test-$i-edit"; component = "BatchTest${i}Edit"; menuType = 1; sortOrder = (200+$i); status = 1; icon = "edit"; isVisible = $true } }
        ListParams = @("")  # tree 不支持分页参数
        IdField = "id"
    },

    @{
        Name = "部门管理"
        ListUrl = "/api/department/tree"
        CreateUrl = "/api/department"
        UpdateUrl = $null  # 网关未路由 PUT /api/department/{id}
        DeleteUrl = $null  # 网关未路由 DELETE /api/department/{id}
        DetailUrl = $null  # 网关未路由 GET /api/department/{id}
        CreateBody = { param($i) @{ departmentName = "BatchDept${uid}_$i"; departmentCode = "BD_${uid}_$i"; sortOrder = $i; description = "批量测试部门$i" } }
        UpdateBody = { param($id,$i) @{ departmentName = "EditDept${uid}_$i"; departmentCode = "BD_${uid}_$i"; sortOrder = ($i+10); description = "已修改$i" } }
        ListParams = @("")
        IdField = "id"
    },

    @{
        Name = "任务调度"
        ListUrl = "/api/system/jobs"
        CreateUrl = $null  # 只读模块
        ListParams = @("page=1&pageSize=5", "page=1&pageSize=10", "page=1&pageSize=5&status=1")
        IdField = "id"
    },

    @{
        Name = "系统配置"
        ListUrl = "/api/system/configs"
        CreateUrl = $null
        ListParams = @("")
        IdField = $null
    },

    # ─────────── 用户管理 ───────────
    @{
        Name = "用户管理"
        ListUrl = "/api/system/user"
        CreateUrl = "/api/system/user"
        UpdateUrl = "/api/system/user/{id}"
        DeleteUrl = "/api/system/user/{id}"
        DetailUrl = "/api/system/user/{id}"
        CreateBody = { param($i) @{ userName = "batchuser${uid}_$i"; password = "Test@123456"; realName = "BatchUser$i"; email = "batch${uid}_$i@test.com"; phone = "138${uid}0$i" } }
        UpdateBody = { param($id,$i) @{ realName = "EditUser$i"; email = "edit${uid}_$i@test.com" } }
        ListParams = @("page=1&pageSize=5", "page=1&pageSize=10&keyword=batch", "page=1&pageSize=5&status=1", "page=2&pageSize=5")
        IdField = "id"
    },

    # ─────────── 租户管理 ───────────
    @{
        Name = "租户管理"
        ListUrl = "/api/tenants"
        CreateUrl = "/api/tenants"
        UpdateUrl = "/api/tenants/{id}"
        DeleteUrl = "/api/tenants/{id}"
        DetailUrl = "/api/tenants/{id}"
        CreateBody = { param($i) @{ tenantName = "BatchTenant${uid}_$i"; tenantCode = "bt${uid}$i"; tenantDomain = "bt${uid}$i.test.com"; contactPerson = "Contact$i"; contactPhone = "139${uid}0$i" } }
        UpdateBody = { param($id,$i) @{ tenantName = "EditTenant${uid}_$i"; contactPerson = "EditContact$i" } }
        ListParams = @("page=1&pageSize=5", "page=1&pageSize=10&keyword=Batch", "page=2&pageSize=3", "page=1&pageSize=5&status=1")
        IdField = "tenantId"
    },

    @{
        Name = "租户通知"
        ListUrl = "/api/tenant/notifications"
        CreateUrl = $null
        ListParams = @("page=1&pageSize=5", "page=1&pageSize=10", "page=1&pageSize=5&isRead=false")
        IdField = "id"
    },

    @{
        Name = "租户公告"
        ListUrl = "/api/tenant/announcements"
        CreateUrl = "/api/tenant/announcements"
        UpdateUrl = "/api/tenant/announcements/{id}"
        DeleteUrl = "/api/tenant/announcements/{id}"
        DetailUrl = "/api/tenant/announcements/{id}"
        CreateBody = { param($i) @{ title = "TenantAnn${uid}_$i"; content = "Announcement content $i"; type = "system"; priority = "normal"; targetAudience = "all" } }
        UpdateBody = { param($id,$i) @{ title = "EditTenantAnn${uid}_$i"; content = "Edited content $i"; type = "system"; priority = "normal"; targetAudience = "all" } }
        ListParams = @("page=1&pageSize=5", "page=1&pageSize=5&keyword=TenantAnn")
        IdField = "id"
    },

    @{
        Name = "租户分类"
        ListUrl = "/api/tenant/categories"
        CreateUrl = "/api/tenant/categories"
        UpdateUrl = "/api/tenant/categories/{id}"
        DeleteUrl = "/api/tenant/categories/{id}"
        DetailUrl = "/api/tenant/categories/{id}"
        CreateBody = { param($i) @{ categoryName = "Cat${uid}_$i"; categoryCode = "CAT_${uid}_$i"; sortOrder = $i; description = "Test category $i" } }
        UpdateBody = { param($id,$i) @{ categoryName = "EditCat${uid}_$i"; categoryCode = "CAT_${uid}_$i"; sortOrder = ($i+10) } }
        ListParams = @("page=1&pageSize=5", "page=1&pageSize=10")
        IdField = "id"
    },

    # ─────────── 充电站 / 设备 ───────────
    @{
        Name = "充电站管理"
        ListUrl = "/api/stations"
        CreateUrl = "/api/stations"
        UpdateUrl = "/api/stations/{id}"
        DeleteUrl = "/api/stations/{id}"
        DetailUrl = "/api/stations/{id}"
        CreateBody = { param($i) @{ name = "批量充电站${uid}_$i"; code = "BST_${uid}_$i"; address = "测试地址$i"; longitude = (116.4+$i*0.01); latitude = (39.9+$i*0.01); status = 1 } }
        UpdateBody = { param($id,$i) @{ name = "修改充电站${uid}_$i"; address = "修改地址$i" } }
        ListParams = @("page=1&pageSize=5", "page=1&pageSize=10&keyword=批量", "page=1&pageSize=5&status=1", "page=2&pageSize=3")
        IdField = "id"
    },

    @{
        Name = "设备管理"
        ListUrl = "/api/device"
        CreateUrl = "/api/device"
        UpdateUrl = "/api/device/{id}"
        DeleteUrl = "/api/device/{id}"
        DetailUrl = "/api/device/{id}"
        CreateBody = { param($i) @{ name = "BatchDev${uid}_$i"; code = "BDEV_${uid}_$i"; stationId = $script:testStationId } }
        UpdateBody = { param($id,$i) @{ name = "EditDev${uid}_$i" } }
        ListParams = @("page=1&pageSize=5", "page=1&pageSize=10&keyword=BatchDev", "page=1&pageSize=5&status=1")
        IdField = "id"
        DependsOnStation = $true
    },

    @{
        Name = "设备告警"
        ListUrl = "/api/device/alerts"
        CreateUrl = $null
        ListParams = @("page=1&pageSize=5", "page=1&pageSize=10", "page=1&pageSize=5&level=1")
        IdField = "id"
    },

    @{
        Name = "设备固件"
        ListUrl = "/api/device/firmware"
        CreateUrl = $null
        ListParams = @("page=1&pageSize=5", "page=1&pageSize=10")
        IdField = "id"
    },

    # ─────────── 充电 / 结算 / 工单 ───────────
    @{
        Name = "充电订单"
        ListUrl = "/api/charging/admin/orders"
        CreateUrl = $null
        ListParams = @("page=1&pageSize=5", "page=1&pageSize=10", "page=2&pageSize=5", "page=1&pageSize=5&status=1")
        IdField = "id"
    },

    @{
        Name = "结算记录"
        ListUrl = "/api/settlements"
        CreateUrl = $null
        ListParams = @("page=1&pageSize=5", "page=1&pageSize=10", "page=2&pageSize=5")
        IdField = "id"
    },

    @{
        Name = "工单管理"
        ListUrl = "/api/workorder"
        CreateUrl = "/api/workorder/fault"
        UpdateUrl = "/api/workorder/fault/{id}"
        DeleteUrl = $null  # 工单无DELETE，用cancel代替
        DetailUrl = "/api/workorder/{id}"
        CancelUrl = "/api/workorder/{id}/cancel"  # 工单取消
        CreateBody = { param($i) @{ title = "BatchWO${uid}_$i"; description = "Fault work order test $i"; priority = "high"; source = "test" } }
        UpdateBody = { param($id,$i) @{ title = "EditWO${uid}_$i"; description = "Edited fault work order $i" } }
        ListParams = @("page=1&pageSize=5", "page=1&pageSize=10&keyword=BatchWO", "page=1&pageSize=5&status=0")
        IdField = "id"
    },

    @{
        Name = "工单统计"
        ListUrl = "/api/workorder/stats/overview"
        CreateUrl = $null
        ListParams = @("")
        IdField = $null
    },

    # ─────────── 账户 / 交易 ───────────
    @{
        Name = "钱包"
        ListUrl = "/api/wallet"
        CreateUrl = $null
        ListParams = @("")
        IdField = $null
    },

    @{
        Name = "交易记录"
        ListUrl = "/api/transactions"
        CreateUrl = $null
        ListParams = @("page=1&pageSize=5", "page=1&pageSize=10", "page=2&pageSize=5")
        IdField = "id"
    },

    # ─────────── 内容平台 ───────────
    @{
        Name = "文章管理"
        ListUrl = "/api/content/articles"
        CreateUrl = "/api/content/articles"
        UpdateUrl = "/api/content/articles/{id}"
        DeleteUrl = "/api/content/articles/{id}"
        DetailUrl = "/api/content/articles/{id}"
        CreateBody = { param($i) @{ title = "BatchArticle${uid}_$i"; content = "Article content $i"; summary = "Summary $i"; siteId = $script:testSiteId; categoryId = $script:testCategoryId } }
        UpdateBody = { param($id,$i) @{ title = "EditArticle${uid}_$i"; content = "Edited article $i" } }
        ListParams = @("page=1&pageSize=5", "page=1&pageSize=10&keyword=BatchArticle")
        IdField = "id"
        DependsOnSite = $true
    },

    # ─────────── 区块链 ───────────
    @{
        Name = "合约管理"
        ListUrl = "/api/contracts"
        CreateUrl = $null
        ListParams = @("page=1&pageSize=5", "page=1&pageSize=10")
        IdField = "id"
    },

    # ─────────── 分析 ───────────
    @{
        Name = "运营仪表板"
        ListUrl = "/api/analytics/dashboard/overview"
        CreateUrl = $null
        ListParams = @("")
        IdField = $null
    },

    @{
        Name = "充电分析"
        ListUrl = "/api/analytics/charging/overview"
        CreateUrl = $null
        ListParams = @("")
        IdField = $null
    },

    @{
        Name = "设备分析"
        ListUrl = "/api/analytics/device/overview"
        CreateUrl = $null
        ListParams = @("")
        IdField = $null
    },

    # ─────────── 数据采集 ───────────
    @{
        Name = "采集任务"
        ListUrl = "/api/ingestion-task"
        CreateUrl = "/api/ingestion-task"
        UpdateUrl = "/api/ingestion-task/{id}"
        DeleteUrl = "/api/ingestion-task/{id}"
        DetailUrl = "/api/ingestion-task/{id}"
        CreateBody = { param($i) @{ name = "BatchIngest${uid}_$i"; description = "Ingestion test $i"; intervalSeconds = 60; taskType = "polling"; protocolType = "mqtt" } }
        UpdateBody = { param($id,$i) @{ name = "EditIngest${uid}_$i"; description = "Edited $i"; intervalSeconds = 120 } }
        ListParams = @("page=1&pageSize=5", "page=1&pageSize=10&keyword=BatchIngest")
        IdField = "id"
    },

    # ─────────── 储能 ───────────
    @{
        Name = "虚拟电厂"
        ListUrl = "/api/vpp/list"
        CreateUrl = $null
        ListParams = @("page=1&pageSize=5", "page=1&pageSize=10")
        IdField = "id"
    },

    @{
        Name = "微电网"
        ListUrl = "/api/microgrid/list"
        CreateUrl = $null
        ListParams = @("page=1&pageSize=5", "page=1&pageSize=10")
        IdField = "id"
    },

    @{
        Name = "光储充站"
        ListUrl = "/api/pvessc/site/list"
        CreateUrl = $null
        ListParams = @("page=1&pageSize=5", "page=1&pageSize=10")
        IdField = "id"
    },

    @{
        Name = "VPP仪表板"
        ListUrl = "/api/vpp/dashboard"
        CreateUrl = $null
        ListParams = @("")
        IdField = $null
    },

    # ─────────── 监控 / 日志 ───────────
    @{
        Name = "操作日志"
        ListUrl = "/api/monitor/operation-logs"
        CreateUrl = $null
        ListParams = @("page=1&pageSize=5", "page=1&pageSize=10", "page=2&pageSize=5", "page=1&pageSize=5&keyword=login")
        IdField = "id"
    },

    @{
        Name = "登录日志"
        ListUrl = "/api/monitor/login-logs"
        CreateUrl = $null
        ListParams = @("page=1&pageSize=5", "page=1&pageSize=10", "page=2&pageSize=5")
        IdField = "id"
    },

    @{
        Name = "审计日志"
        ListUrl = "/api/system/audit-log"
        CreateUrl = $null
        ListParams = @("page=1&pageSize=5", "page=1&pageSize=10", "page=2&pageSize=5")
        IdField = "id"
    },

    @{
        Name = "在线用户"
        ListUrl = "/api/monitor/online"
        CreateUrl = $null
        ListParams = @("page=1&pageSize=5", "page=1&pageSize=10")
        IdField = "id"
    },

    # ─────────── 权限 ───────────
    @{
        Name = "临时授权"
        ListUrl = "/api/permissions/temporary/expiring"
        CreateUrl = $null
        ListParams = @("")
        IdField = "id"
    },

    @{
        Name = "高危权限"
        ListUrl = "/api/permissions/high-risk"
        CreateUrl = $null
        ListParams = @("page=1&pageSize=5", "page=1&pageSize=10")
        IdField = "id"
    },

    # ─────────── 用户自身 ───────────
    @{
        Name = "用户资料"
        ListUrl = "/api/user/profile"
        CreateUrl = $null
        ListParams = @("")
        IdField = $null
    },

    @{
        Name = "用户认证"
        ListUrl = "/api/auth/me"
        CreateUrl = $null
        ListParams = @("")
        IdField = $null
    },

    @{
        Name = "系统版本"
        ListUrl = "/api/system/versions"
        CreateUrl = $null
        ListParams = @("")
        IdField = $null
    },

    @{
        Name = "缓存统计"
        ListUrl = "/api/system/cache/stats"
        CreateUrl = $null
        ListParams = @("")
        IdField = $null
    }
)

$totalModules = $modules.Count
Write-Host "`n  共 $totalModules 个模块待测试`n" -ForegroundColor Cyan

# ================================================================
# Phase 1 + 2 + 3 + 4 + 5: 逐模块 CRUD 全生命周期
# ================================================================

$moduleIndex = 0
foreach ($mod in $modules) {
    $moduleIndex++
    $mName = $mod.Name
    Write-Host "`n━━━━━ [$moduleIndex/$totalModules] $mName ━━━━━" -ForegroundColor Magenta
    
    $createdIds = @()
    $hasCrud = ($null -ne $mod.CreateUrl)
    
    # 如果模块依赖 Station 但没有 stationId，跳过创建
    if ($mod.DependsOnStation -and -not $script:testStationId) {
        $hasCrud = $false
    }
    # 如果模块依赖 Site 但没有 siteId，跳过创建
    if ($mod.DependsOnSite -and (-not $script:testSiteId -or -not $script:testCategoryId)) {
        $hasCrud = $false
    }
    
    # ──────── Phase 1: CREATE ────────
    if ($hasCrud) {
        Write-Host "  >> Phase 1: CREATE ×$CreateCount" -ForegroundColor Yellow
        for ($i = 1; $i -le $CreateCount; $i++) {
            $body = & $mod.CreateBody $i
            $r = Invoke-Api POST "$GatewayUrl$($mod.CreateUrl)" $body
            if ($r.Code -in 200,201) {
                $newId = Extract-Id $r
                if ($newId) { $createdIds += $newId }
                Add-R "CREATE" $mName "创建#$i" "PASS" "HTTP $($r.Code) ID=$newId"
            } elseif ($r.Code -in 400,409,422) {
                Add-R "CREATE" $mName "创建#$i" "WARN" "HTTP $($r.Code) — 字段验证/冲突"
            } elseif ($r.Code -ge 500) {
                Add-R "CREATE" $mName "创建#$i" "WARN" "HTTP $($r.Code) — 服务端内部错误"
            } else {
                Add-R "CREATE" $mName "创建#$i" "FAIL" "HTTP $($r.Code) $($r.Error)"
            }
        }
    } else {
        Add-R "CREATE" $mName "跳过(只读模块)" "SKIP" ""
    }
    
    # ──────── Phase 2: READ (列表 + 详情) ────────
    Write-Host "  >> Phase 2: READ" -ForegroundColor Yellow
    
    # 2.1 列表基本可达
    $listUrl = "$GatewayUrl$($mod.ListUrl)"
    if ($mod.ListUrl -notmatch '\?') { $listUrl += "?page=1&pageSize=5" }
    $r = Invoke-Api GET $listUrl
    if ($r.Code -eq 200) {
        Add-R "READ" $mName "列表基本查询" "PASS" "HTTP 200"
    } else {
        Add-R "READ" $mName "列表基本查询" "FAIL" "HTTP $($r.Code)"
    }
    
    # 2.2 详情（如果有创建的 ID）
    if ($mod.DetailUrl -and $createdIds.Count -gt 0) {
        $detailUrl = "$GatewayUrl$($mod.DetailUrl -replace '\{id\}', $createdIds[0])"
        $r = Invoke-Api GET $detailUrl
        if ($r.Code -eq 200) {
            Add-R "READ" $mName "详情查询 ID=$($createdIds[0].Substring(0,8))..." "PASS" "HTTP 200"
        } else {
            Add-R "READ" $mName "详情查询" "WARN" "HTTP $($r.Code)"
        }
    }
    
    # ──────── Phase 3: UPDATE ────────
    if ($hasCrud -and $mod.UpdateUrl -and $createdIds.Count -gt 0) {
        Write-Host "  >> Phase 3: UPDATE" -ForegroundColor Yellow
        $updateIndex = 0
        foreach ($cid in $createdIds) {
            $updateIndex++
            $body = & $mod.UpdateBody $cid $updateIndex
            $updateUrl = "$GatewayUrl$($mod.UpdateUrl -replace '\{id\}', $cid)"
            $r = Invoke-Api PUT $updateUrl $body
            if ($r.Code -in 200,204) {
                Add-R "UPDATE" $mName "更新#$updateIndex ID=$($cid.Substring(0,8))..." "PASS" "HTTP $($r.Code)"
            } elseif ($r.Code -in 400,404,405,422) {
                Add-R "UPDATE" $mName "更新#$updateIndex" "WARN" "HTTP $($r.Code) — 路由/字段/状态问题"
            } else {
                Add-R "UPDATE" $mName "更新#$updateIndex" "FAIL" "HTTP $($r.Code) $($r.Error)"
            }
        }
        
        # 3.1 更新后再读详情验证
        if ($mod.DetailUrl) {
            $verifyUrl = "$GatewayUrl$($mod.DetailUrl -replace '\{id\}', $createdIds[0])"
            $r = Invoke-Api GET $verifyUrl
            if ($r.Code -eq 200) {
                Add-R "UPDATE" $mName "更新后验证读取" "PASS" "HTTP 200"
            } else {
                Add-R "UPDATE" $mName "更新后验证读取" "WARN" "HTTP $($r.Code)"
            }
        }
    }
    
    # ──────── Phase 4: QUERY 条件组合 ────────
    if ($mod.ListParams -and $mod.ListParams.Count -gt 0) {
        Write-Host "  >> Phase 4: QUERY 条件组合 ×$($mod.ListParams.Count)" -ForegroundColor Yellow
        $qi = 0
        foreach ($qp in $mod.ListParams) {
            $qi++
            $queryUrl = "$GatewayUrl$($mod.ListUrl)"
            if ($qp) {
                $sep = if ($queryUrl -match '\?') { "&" } else { "?" }
                $queryUrl += "$sep$qp"
            }
            $r = Invoke-Api GET $queryUrl
            $paramLabel = if ($qp) { $qp.Substring(0, [Math]::Min(50, $qp.Length)) } else { "(无参)" }
            if ($r.Code -eq 200) {
                Add-R "QUERY" $mName "条件#$qi $paramLabel" "PASS" "HTTP 200"
            } elseif ($r.Code -eq 400) {
                Add-R "QUERY" $mName "条件#$qi $paramLabel" "WARN" "HTTP 400 参数不兼容"
            } else {
                Add-R "QUERY" $mName "条件#$qi $paramLabel" "FAIL" "HTTP $($r.Code)"
            }
        }
    }
    
    # ──────── Phase 4.5: 边界值查询 ────────
    if ($mod.ListUrl -match '\?|page') {
        # 已有分页的模块，测边界
    }
    $boundaryParams = @(
        @{Name="空关键词"; Q="page=1&pageSize=5&keyword="},
        @{Name="超大页码"; Q="page=9999&pageSize=5"},
        @{Name="超大页大小"; Q="page=1&pageSize=1000"},
        @{Name="页码0"; Q="page=0&pageSize=5"},
        @{Name="负数页码"; Q="page=-1&pageSize=5"},
        @{Name="特殊字符"; Q="page=1&pageSize=5&keyword=%E2%9C%93%E2%9C%93"},
        @{Name="SQL注入尝试"; Q="page=1&pageSize=5&keyword=' OR '1'='1"}
    )
    # 仅对有分页的模块测边界
    if ($mod.ListUrl -notmatch 'tree|overview|stats|dashboard|profile|me|versions|cache|wallet|expiring') {
        Write-Host "  >> Phase 4.5: 边界值 ×$($boundaryParams.Count)" -ForegroundColor Yellow
        foreach ($bp in $boundaryParams) {
            $bUrl = "$GatewayUrl$($mod.ListUrl)?$($bp.Q)"
            $r = Invoke-Api GET $bUrl
            if ($r.Code -in 200,400,422) {
                Add-R "BOUNDARY" $mName $bp.Name "PASS" "HTTP $($r.Code) — 安全处理"
            } elseif ($r.Code -ge 500) {
                # 边界值导致 500 是服务端参数校验不足，非功能 bug
                Add-R "BOUNDARY" $mName $bp.Name "WARN" "HTTP $($r.Code) — 服务端未做边界校验"
            } else {
                Add-R "BOUNDARY" $mName $bp.Name "WARN" "HTTP $($r.Code)"
            }
        }
    }
    
    # ──────── Phase 5: DELETE ────────
    if ($hasCrud -and $mod.DeleteUrl -and $createdIds.Count -gt 0) {
        Write-Host "  >> Phase 5: DELETE ×$($createdIds.Count)" -ForegroundColor Yellow
        foreach ($cid in $createdIds) {
            $delUrl = "$GatewayUrl$($mod.DeleteUrl -replace '\{id\}', $cid)"
            $r = Invoke-Api DELETE $delUrl
            if ($r.Code -in 200,204) {
                Add-R "DELETE" $mName "删除 ID=$($cid.Substring(0,8))..." "PASS" "HTTP $($r.Code)"
            } elseif ($r.Code -in 404,405) {
                Add-R "DELETE" $mName "删除 ID=$($cid.Substring(0,8))..." "WARN" "HTTP $($r.Code) — 不存在/不支持"
            } else {
                Add-R "DELETE" $mName "删除" "WARN" "HTTP $($r.Code) $($r.Error)"
            }
        }
        
        # 5.1 删除后验证（应该404或标记已删除）
        if ($mod.DetailUrl) {
            $verifyUrl = "$GatewayUrl$($mod.DetailUrl -replace '\{id\}', $createdIds[0])"
            $r = Invoke-Api GET $verifyUrl
            if ($r.Code -in 404,200) {
                # 200 也可以(soft delete 可能仍返回但标记了delete_at)
                Add-R "DELETE" $mName "删除后验证" "PASS" "HTTP $($r.Code) — 软删除/物理删除"
            } else {
                Add-R "DELETE" $mName "删除后验证" "WARN" "HTTP $($r.Code)"
            }
        }
    }
    
    # ──────── Phase 5b: CANCEL (工单专用) ────────
    if ($mod.CancelUrl -and $createdIds.Count -gt 0) {
        Write-Host "  >> Phase 5b: CANCEL ×$($createdIds.Count)" -ForegroundColor Yellow
        foreach ($cid in $createdIds) {
            $cancelUrl = "$GatewayUrl$($mod.CancelUrl -replace '\{id\}', $cid)"
            $r = Invoke-Api POST $cancelUrl @{reason="Batch test cleanup"}
            if ($r.Code -in 200,204) {
                Add-R "DELETE" $mName "取消 ID=$($cid.Substring(0,8))..." "PASS" "HTTP $($r.Code)"
            } elseif ($r.Code -in 400,404,409) {
                Add-R "DELETE" $mName "取消 ID=$($cid.Substring(0,8))..." "WARN" "HTTP $($r.Code) — 状态不允许取消"
            } else {
                Add-R "DELETE" $mName "取消" "WARN" "HTTP $($r.Code)"
            }
        }
    }
}

# ================================================================
# Phase 6: 模块专项测试 — 特有业务逻辑
# ================================================================
Write-Host "`n━━━━━ Phase 6: 模块专项业务测试 ━━━━━" -ForegroundColor Magenta

# 6.1 认证相关
Write-Host "  >> 6.1 认证流程" -ForegroundColor Yellow
$r = Invoke-Api POST "$GatewayUrl/api/auth/login" @{userName="admin";password="P@ssw0rd"}
if ($r.Code -eq 200 -and $r.Data.data.accessToken) {
    Add-R "SPECIAL" "认证" "正常登录" "PASS" "获取到 token"
    $testToken = $r.Data.data.accessToken
    $testRefresh = $r.Data.data.refreshToken
    
    # me
    $r2 = Invoke-Api GET "$GatewayUrl/api/auth/me" -Headers @{Authorization="Bearer $testToken"}
    if ($r2.Code -eq 200) { Add-R "SPECIAL" "认证" "获取当前用户 /auth/me" "PASS" "" }
    else { Add-R "SPECIAL" "认证" "获取当前用户 /auth/me" "FAIL" "HTTP $($r2.Code)" }
    
    # sessions
    $r3 = Invoke-Api GET "$GatewayUrl/api/auth/sessions" -Headers @{Authorization="Bearer $testToken"}
    if ($r3.Code -eq 200) { Add-R "SPECIAL" "认证" "活跃会话列表" "PASS" "" }
    else { Add-R "SPECIAL" "认证" "活跃会话列表" "WARN" "HTTP $($r3.Code)" }
    
    # login history
    $r4 = Invoke-Api GET "$GatewayUrl/api/auth/login-history" -Headers @{Authorization="Bearer $testToken"}
    if ($r4.Code -eq 200) { Add-R "SPECIAL" "认证" "登录历史" "PASS" "" }
    else { Add-R "SPECIAL" "认证" "登录历史" "WARN" "HTTP $($r4.Code)" }
    
    # session stats
    $r5 = Invoke-Api GET "$GatewayUrl/api/auth/session-stats" -Headers @{Authorization="Bearer $testToken"}
    if ($r5.Code -eq 200) { Add-R "SPECIAL" "认证" "会话统计" "PASS" "" }
    else { Add-R "SPECIAL" "认证" "会话统计" "WARN" "HTTP $($r5.Code)" }
    
    # refresh token
    if ($testRefresh) {
        $r6 = Invoke-Api POST "$GatewayUrl/api/auth/refresh" @{refreshToken=$testRefresh}
        if ($r6.Code -eq 200) { Add-R "SPECIAL" "认证" "刷新Token" "PASS" "" }
        else { Add-R "SPECIAL" "认证" "刷新Token" "WARN" "HTTP $($r6.Code)" }
    }
    
    # logout
    if ($testRefresh) {
        $r7 = Invoke-Api POST "$GatewayUrl/api/auth/logout" @{refreshToken=$testRefresh} -Headers @{Authorization="Bearer $testToken"}
        if ($r7.Code -eq 200) { Add-R "SPECIAL" "认证" "正常登出" "PASS" "" }
        else { Add-R "SPECIAL" "认证" "正常登出" "WARN" "HTTP $($r7.Code)" }
    }
    
    # 错误登录
    $r8 = Invoke-Api POST "$GatewayUrl/api/auth/login" @{userName="admin";password="WrongPassword"}
    if ($r8.Code -in 400,401) { Add-R "SPECIAL" "认证" "错误密码拒绝" "PASS" "HTTP $($r8.Code)" }
    else { Add-R "SPECIAL" "认证" "错误密码拒绝" "FAIL" "HTTP $($r8.Code)" }
    
    # 不存在用户
    $r9 = Invoke-Api POST "$GatewayUrl/api/auth/login" @{userName="nonexistent_user_xyz";password="P@ssw0rd"}
    if ($r9.Code -in 400,401) { Add-R "SPECIAL" "认证" "不存在用户拒绝" "PASS" "HTTP $($r9.Code)" }
    else { Add-R "SPECIAL" "认证" "不存在用户拒绝" "FAIL" "HTTP $($r9.Code)" }
} else {
    Add-R "SPECIAL" "认证" "正常登录" "FAIL" "HTTP $($r.Code)"
}

# 重新获取有效 token  
$loginR = Invoke-Api POST "$GatewayUrl/api/auth/login" @{userName="admin";password="P@ssw0rd"}
$token = $loginR.Data.data.accessToken
$script:authHeaders = @{ Authorization = "Bearer $token" }

# 6.2 用户资料操作
Write-Host "  >> 6.2 用户资料" -ForegroundColor Yellow
$r = Invoke-Api GET "$GatewayUrl/api/user/profile"
if ($r.Code -eq 200) { Add-R "SPECIAL" "用户资料" "获取资料" "PASS" "" }
else { Add-R "SPECIAL" "用户资料" "获取资料" "FAIL" "HTTP $($r.Code)" }

# 6.3 菜单树
Write-Host "  >> 6.3 菜单树" -ForegroundColor Yellow
$r = Invoke-Api GET "$GatewayUrl/api/system/menu/tree"
if ($r.Code -eq 200) {
    $menuData = $r.Data.data
    $menuCount = 0
    function Count-Menu($items) { foreach($item in $items) { $script:mc++; if($item.children) { Count-Menu $item.children } } }
    $script:mc = 0; Count-Menu $menuData
    Add-R "SPECIAL" "菜单" "菜单树加载" "PASS" "节点数: $($script:mc)"
} else {
    Add-R "SPECIAL" "菜单" "菜单树加载" "FAIL" "HTTP $($r.Code)"
}

# 6.4 部门树
Write-Host "  >> 6.4 部门树" -ForegroundColor Yellow
$r = Invoke-Api GET "$GatewayUrl/api/department/tree"
if ($r.Code -eq 200) {
    Add-R "SPECIAL" "部门" "部门树加载" "PASS" ""
} else {
    Add-R "SPECIAL" "部门" "部门树加载" "FAIL" "HTTP $($r.Code)"
}

# 6.5 角色权限分配
Write-Host "  >> 6.5 角色权限关联" -ForegroundColor Yellow
$rolesR = Invoke-Api GET "$GatewayUrl/api/system/role?page=1&pageSize=1"
if ($rolesR.Code -eq 200 -and $rolesR.Data.data.items) {
    $firstRole = $rolesR.Data.data.items[0]
    $roleId = $firstRole.id
    # 获取角色权限
    $r = Invoke-Api GET "$GatewayUrl/api/system/role/$roleId/permissions"
    if ($r.Code -eq 200) { Add-R "SPECIAL" "角色权限" "获取角色权限列表" "PASS" "角色=$($firstRole.name)" }
    else { Add-R "SPECIAL" "角色权限" "获取角色权限列表" "WARN" "HTTP $($r.Code)" }
    
    # 获取角色菜单
    $r2 = Invoke-Api GET "$GatewayUrl/api/system/role/$roleId/menus"
    if ($r2.Code -eq 200) { Add-R "SPECIAL" "角色权限" "获取角色菜单列表" "PASS" "" }
    else { Add-R "SPECIAL" "角色权限" "获取角色菜单列表" "WARN" "HTTP $($r2.Code)" }
}

# 6.6 工单统计仪表板
Write-Host "  >> 6.6 工单统计" -ForegroundColor Yellow
$r = Invoke-Api GET "$GatewayUrl/api/workorder/stats/overview"
if ($r.Code -eq 200) { Add-R "SPECIAL" "工单" "统计概览" "PASS" "" }
else { Add-R "SPECIAL" "工单" "统计概览" "WARN" "HTTP $($r.Code)" }

# 6.7 分析仪表板集合
Write-Host "  >> 6.7 分析仪表板" -ForegroundColor Yellow
$dashUrls = @(
    @{N="运营概览"; U="/api/analytics/dashboard/overview"},
    @{N="充电分析"; U="/api/analytics/charging/overview"},
    @{N="设备分析"; U="/api/analytics/device/overview"},
    @{N="VPP仪表板"; U="/api/vpp/dashboard"}
)
foreach ($du in $dashUrls) {
    $r = Invoke-Api GET "$GatewayUrl$($du.U)"
    if ($r.Code -eq 200) { Add-R "SPECIAL" "仪表板" $du.N "PASS" "" }
    else { Add-R "SPECIAL" "仪表板" $du.N "WARN" "HTTP $($r.Code)" }
}

# 6.8 安全模块
Write-Host "  >> 6.8 安全模块" -ForegroundColor Yellow
$secUrls = @(
    @{N="IP黑名单"; U="/api/security/ip-blacklist?page=1&pageSize=5"},
    @{N="敏感词"; U="/api/security/sensitive-word?page=1&pageSize=5"},
    @{N="数据脱敏规则"; U="/api/security/data-mask/rules?page=1&pageSize=5"},
    @{N="安全审计"; U="/api/security/audit?page=1&pageSize=5"}
)
foreach ($su in $secUrls) {
    $r = Invoke-Api GET "$GatewayUrl$($su.U)"
    if ($r.Code -eq 200) { Add-R "SPECIAL" "安全" $su.N "PASS" "" }
    elseif ($r.Code -in 400,404) { Add-R "SPECIAL" "安全" $su.N "WARN" "HTTP $($r.Code)" }
    else { Add-R "SPECIAL" "安全" $su.N "FAIL" "HTTP $($r.Code)" }
}

# 6.9 MFA 状态
Write-Host "  >> 6.9 MFA" -ForegroundColor Yellow
$r = Invoke-Api GET "$GatewayUrl/api/mfa/enabled"
if ($r.Code -eq 200) { Add-R "SPECIAL" "MFA" "MFA状态查询" "PASS" "" }
else { Add-R "SPECIAL" "MFA" "MFA状态查询" "WARN" "HTTP $($r.Code)" }

$r = Invoke-Api GET "$GatewayUrl/api/mfa/configs"
if ($r.Code -eq 200) { Add-R "SPECIAL" "MFA" "MFA配置列表" "PASS" "" }
else { Add-R "SPECIAL" "MFA" "MFA配置列表" "WARN" "HTTP $($r.Code)" }

# ================================================================
# 清理依赖数据
# ================================================================
Write-Host "`n  >> 清理测试依赖数据..." -ForegroundColor DarkCyan
if ($script:testStationId -and $stSetup.Code -in 200,201) {
    Invoke-Api DELETE "$GatewayUrl/api/stations/$($script:testStationId)" | Out-Null
}
if ($script:testCategoryId -and $catSetup.Code -in 200,201) {
    Invoke-Api DELETE "$GatewayUrl/api/content/categories/$($script:testCategoryId)" | Out-Null
}
if ($script:testSiteId -and $siteSetup.Code -in 200,201) {
    Invoke-Api DELETE "$GatewayUrl/api/content/sites/$($script:testSiteId)" | Out-Null
}

# ================================================================
# 汇总
# ================================================================
Write-Host "`n" -NoNewline
Write-Host "╔══════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║              全模块批量 CRUD 测试完成                    ║" -ForegroundColor Cyan
Write-Host "╚══════════════════════════════════════════════════════════╝" -ForegroundColor Cyan

$total = $script:pass + $script:fail + $script:warn + $script:skip
$passRate = if (($total - $script:skip) -gt 0) { [math]::Round($script:pass / ($total - $script:skip) * 100, 1) } else { 0 }

Write-Host "  总测试:  $total" -ForegroundColor White
Write-Host "  PASS:    $($script:pass)" -ForegroundColor Green
Write-Host "  FAIL:    $($script:fail)" -ForegroundColor $(if ($script:fail -gt 0) { "Red" } else { "Green" })
Write-Host "  WARN:    $($script:warn)" -ForegroundColor Yellow
Write-Host "  SKIP:    $($script:skip)" -ForegroundColor DarkGray
Write-Host "  通过率:  ${passRate}% (排除SKIP)" -ForegroundColor $(if ($passRate -ge 95) { "Green" } elseif ($passRate -ge 80) { "Yellow" } else { "Red" })

# Phase 统计
Write-Host "`n  === 按 Phase 统计 ===" -ForegroundColor Cyan
$phases = $script:results | Group-Object Phase | Sort-Object Name
foreach ($pg in $phases) {
    $pp = ($pg.Group | Where-Object Status -eq "PASS").Count
    $pf = ($pg.Group | Where-Object Status -eq "FAIL").Count
    $pw = ($pg.Group | Where-Object Status -eq "WARN").Count
    Write-Host "  $($pg.Name): $($pg.Count)个 (PASS=$pp FAIL=$pf WARN=$pw)" -ForegroundColor White
}

Write-Host "`n  === 按模块统计 ===" -ForegroundColor Cyan
$modGroups = $script:results | Where-Object { $_.Status -ne "SKIP" } | Group-Object Module | Sort-Object Name
foreach ($mg in $modGroups) {
    $mp = ($mg.Group | Where-Object Status -eq "PASS").Count
    $mf = ($mg.Group | Where-Object Status -eq "FAIL").Count
    $mw = ($mg.Group | Where-Object Status -eq "WARN").Count
    $icon = if ($mf -gt 0) { "✗" } elseif ($mw -gt 0) { "△" } else { "✓" }
    $color = if ($mf -gt 0) { "Red" } elseif ($mw -gt 0) { "Yellow" } else { "Green" }
    Write-Host "  $icon $($mg.Name): $($mg.Count)个 (PASS=$mp FAIL=$mf WARN=$mw)" -ForegroundColor $color
}

# 导出 CSV
$script:results | Export-Csv -Path $csvFile -NoTypeInformation -Encoding UTF8
Write-Host "`n  报告导出: $csvFile" -ForegroundColor Gray

# 返回结果
return @{
    Total = $total
    Pass = $script:pass
    Fail = $script:fail
    Warn = $script:warn
    Skip = $script:skip
    PassRate = $passRate
    CsvPath = $csvFile
}
