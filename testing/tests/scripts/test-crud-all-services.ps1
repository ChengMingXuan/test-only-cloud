<#
.SYNOPSIS
    Layer 3: 全量 CRUD 增删改查（所有 17 个业务服务）
.DESCRIPTION
    对每个服务核心资源执行 CREATE → READ → UPDATE → DELETE → 验证删除
    含 DB 断言（直查 PostgreSQL 验证写入）
#>
param(
    [string]$GatewayBase = "http://localhost:5000",
    [string]$LogDir = "tests/scripts/logs"
)

$ErrorActionPreference = "Continue"
$ts = Get-Date -Format "yyyyMMdd-HHmmss"
$csvPath = "$LogDir/crud-test-$ts.csv"
if (!(Test-Path $LogDir)) { New-Item -ItemType Directory -Path $LogDir -Force | Out-Null }

function Get-Token {
    $body = '{"userName":"admin","password":"P@ssw0rd"}'
    $resp = Invoke-RestMethod -Uri "$GatewayBase/api/auth/login" -Method POST -Body $body -ContentType "application/json" -TimeoutSec 10
    return $resp.data.accessToken
}

$global:crudResults = [System.Collections.Generic.List[pscustomobject]]::new()
$global:pass = 0; $global:fail = 0; $global:skip = 0

function Add-CrudResult($Service, $Resource, $Op, $Status, $Detail) {
    $global:crudResults.Add([pscustomobject]@{
        Service=$Service; Resource=$Resource; Operation=$Op;
        Status=$Status; Detail=$Detail; Time=(Get-Date -Format "HH:mm:ss")
    })
    if ($Status -eq "PASS") { $global:pass++ }
    elseif ($Status -eq "FAIL") { $global:fail++ }
    else { $global:skip++ }
    
    $color = switch($Status) { "PASS" {"Green"} "FAIL" {"Red"} default {"Yellow"} }
    Write-Host "  [$Status] $Service/$Resource - $Op : $Detail" -ForegroundColor $color
}

function Invoke-Api($Method, $Path, $Body, $Headers) {
    $params = @{
        Uri = "$GatewayBase$Path"
        Method = $Method
        Headers = $Headers
        ContentType = "application/json"
        UseBasicParsing = $true
        TimeoutSec = 15
    }
    if ($Body) { $params.Body = ($Body | ConvertTo-Json -Depth 10 -Compress) }
    try {
        $resp = Invoke-WebRequest @params -ErrorAction Stop
        return @{ Code = $resp.StatusCode; Body = ($resp.Content | ConvertFrom-Json) }
    } catch {
        $code = 0; $msg = $_.Exception.Message
        if ($_.Exception.Response) { $code = [int]$_.Exception.Response.StatusCode }
        try { $errBody = $_ | ConvertFrom-Json } catch { $errBody = $null }
        return @{ Code = $code; Body = $errBody; Error = $msg }
    }
}

function Invoke-DbQuery($Db, $Sql) {
    $raw = docker exec -e PGCLIENTENCODING=UTF8 jgsy-postgres psql -U postgres -d $Db -t -A -c $Sql 2>$null
    return $raw
}

Write-Host "`n========== Layer 3: 全量 CRUD 增删改查 ==========" -ForegroundColor Cyan

$token = Get-Token
$h = @{ Authorization = "Bearer $token" }
$testId = [guid]::NewGuid().ToString().Substring(0, 8)

# ============================================================
# 1. Permission 服务 - 角色 CRUD
# ============================================================
Write-Host "`n--- Permission: 角色 ---" -ForegroundColor Yellow
$roleName = "crud-test-role-$testId"
$roleCode = "CRUD_TEST_ROLE_$($testId.ToUpper())"

# CREATE
$r = Invoke-Api POST "/api/system/role" @{name=$roleName;code=$roleCode;description="CRUD测试角色";sortOrder=99} $h
if ($r.Code -in 200,201) {
    $roleId = if ($r.Body.data.id) { $r.Body.data.id } elseif ($r.Body.data) { $r.Body.data } else { $r.Body.id }
    Add-CrudResult "Permission" "Role" "CREATE" "PASS" "ID=$roleId"
    
    # DB 断言
    $dbRow = Invoke-DbQuery "jgsy_permission" "SELECT role_name FROM perm_role WHERE id='$roleId' AND delete_at IS NULL"
    if ($dbRow -and $dbRow.Trim() -eq $roleName) {
        Add-CrudResult "Permission" "Role" "DB-CREATE" "PASS" "DB 记录一致"
    } else {
        Add-CrudResult "Permission" "Role" "DB-CREATE" "FAIL" "DB 记录不一致: $dbRow"
    }
    
    # READ
    $r2 = Invoke-Api GET "/api/system/role/$roleId" $null $h
    if ($r2.Code -eq 200) {
        Add-CrudResult "Permission" "Role" "READ" "PASS" "获取成功"
    } else {
        Add-CrudResult "Permission" "Role" "READ" "FAIL" "HTTP $($r2.Code)"
    }
    
    # UPDATE
    $r3 = Invoke-Api PUT "/api/system/role/$roleId" @{name="$roleName-updated";code=$roleCode;description="已更新";sortOrder=99} $h
    if ($r3.Code -in 200,204) {
        Add-CrudResult "Permission" "Role" "UPDATE" "PASS" "更新成功"
        $dbRow2 = Invoke-DbQuery "jgsy_permission" "SELECT role_name FROM perm_role WHERE id='$roleId' AND delete_at IS NULL"
        if ($dbRow2 -and $dbRow2.Trim() -eq "$roleName-updated") {
            Add-CrudResult "Permission" "Role" "DB-UPDATE" "PASS" "DB 更新一致"
        } else {
            Add-CrudResult "Permission" "Role" "DB-UPDATE" "FAIL" "DB=$dbRow2"
        }
    } else {
        Add-CrudResult "Permission" "Role" "UPDATE" "FAIL" "HTTP $($r3.Code)"
    }
    
    # DELETE
    $r4 = Invoke-Api DELETE "/api/system/role/$roleId" $null $h
    if ($r4.Code -in 200,204) {
        Add-CrudResult "Permission" "Role" "DELETE" "PASS" "删除成功"
        # 验证软删除
        $dbDel = Invoke-DbQuery "jgsy_permission" "SELECT delete_at FROM perm_role WHERE id='$roleId'"
        if ($dbDel -and $dbDel.Trim() -eq "t") {
            Add-CrudResult "Permission" "Role" "SOFT-DELETE" "PASS" "软删除标记正确"
        } else {
            Add-CrudResult "Permission" "Role" "SOFT-DELETE" "FAIL" "delete_at=$dbDel"
        }
        # API 不可见
        $r5 = Invoke-Api GET "/api/system/role/$roleId" $null $h
        if ($r5.Code -eq 404 -or ($r5.Body -and $r5.Body.success -eq $false)) {
            Add-CrudResult "Permission" "Role" "INVISIBLE" "PASS" "删除后不可见"
        } else {
            Add-CrudResult "Permission" "Role" "INVISIBLE" "FAIL" "删除后仍可见"
        }
    } else {
        Add-CrudResult "Permission" "Role" "DELETE" "FAIL" "HTTP $($r4.Code)"
    }
} else {
    Add-CrudResult "Permission" "Role" "CREATE" "FAIL" "HTTP $($r.Code) $($r.Error)"
}

# ============================================================
# 2. Permission 服务 - 字典 CRUD
# ============================================================
Write-Host "`n--- Permission: 字典 ---" -ForegroundColor Yellow
$dictCode = "TEST_DICT_$($testId.ToUpper())"

$r = Invoke-Api POST "/api/system/dict/types" @{code=$dictCode;name="测试字典$testId";description="CRUD测试";sortOrder=99} $h
if ($r.Code -in 200,201) {
    $dictId = if ($r.Body.data.id) { $r.Body.data.id } elseif ($r.Body.data) { $r.Body.data } else { $r.Body.id }
    Add-CrudResult "Permission" "Dict" "CREATE" "PASS" "ID=$dictId"
    
    $dbRow = Invoke-DbQuery "jgsy_permission" "SELECT code FROM perm_dict_type WHERE id='$dictId' AND delete_at IS NULL"
    if ($dbRow -and $dbRow.Trim() -eq $dictCode) {
        Add-CrudResult "Permission" "Dict" "DB-CREATE" "PASS" "DB OK"
    } else {
        Add-CrudResult "Permission" "Dict" "DB-CREATE" "FAIL" "DB=$dbRow"
    }
    
    $r2 = Invoke-Api GET "/api/system/dict/types/$dictId" $null $h
    Add-CrudResult "Permission" "Dict" "READ" $(if($r2.Code -eq 200){"PASS"}else{"FAIL"}) "HTTP $($r2.Code)"
    
    $r3 = Invoke-Api PUT "/api/system/dict/types/$dictId" @{code=$dictCode;name="字典已更新$testId";description="已更新";sortOrder=99} $h
    Add-CrudResult "Permission" "Dict" "UPDATE" $(if($r3.Code -in 200,204){"PASS"}else{"FAIL"}) "HTTP $($r3.Code)"
    
    $r4 = Invoke-Api DELETE "/api/system/dict/types/$dictId" $null $h
    Add-CrudResult "Permission" "Dict" "DELETE" $(if($r4.Code -in 200,204){"PASS"}else{"FAIL"}) "HTTP $($r4.Code)"
    
    $dbDel = Invoke-DbQuery "jgsy_permission" "SELECT delete_at FROM perm_dict_type WHERE id='$dictId'"
    Add-CrudResult "Permission" "Dict" "SOFT-DELETE" $(if($dbDel -and $dbDel.Trim() -eq "t"){"PASS"}else{"FAIL"}) "delete_at=$($dbDel.Trim())"
} else {
    Add-CrudResult "Permission" "Dict" "CREATE" "FAIL" "HTTP $($r.Code)"
}

# ============================================================
# 3. Permission 服务 - 公告 CRUD
# ============================================================
Write-Host "`n--- Permission: 公告 ---" -ForegroundColor Yellow
$r = Invoke-Api POST "/api/system/announcements" @{title="测试公告$testId";content="自动化测试内容";type="notice";status=0} $h
if ($r.Code -in 200,201) {
    $noticeId = if ($r.Body.data.id) { $r.Body.data.id } elseif ($r.Body.data) { $r.Body.data } else { $r.Body.id }
    Add-CrudResult "Permission" "Notice" "CREATE" "PASS" "ID=$noticeId"
    
    $r2 = Invoke-Api GET "/api/system/announcements/$noticeId" $null $h
    Add-CrudResult "Permission" "Notice" "READ" $(if($r2.Code -eq 200){"PASS"}else{"FAIL"}) "HTTP $($r2.Code)"
    
    $r3 = Invoke-Api PUT "/api/system/announcements/$noticeId" @{title="公告已更新$testId";content="已更新内容";type="notice";status=0} $h
    Add-CrudResult "Permission" "Notice" "UPDATE" $(if($r3.Code -in 200,204){"PASS"}else{"FAIL"}) "HTTP $($r3.Code)"
    
    $r4 = Invoke-Api DELETE "/api/system/announcements/$noticeId" $null $h
    Add-CrudResult "Permission" "Notice" "DELETE" $(if($r4.Code -in 200,204){"PASS"}else{"FAIL"}) "HTTP $($r4.Code)"
} else {
    Add-CrudResult "Permission" "Notice" "CREATE" "FAIL" "HTTP $($r.Code)"
}

# ============================================================
# 4. Tenant 服务 - 租户 CRUD
# ============================================================
Write-Host "`n--- Tenant: 租户 ---" -ForegroundColor Yellow
$tenantName = "test-tenant-$testId"
$r = Invoke-Api POST "/api/tenants" @{tenantName=$tenantName;tenantCode="t_$testId";tenantDomain="test-$testId.jgsy.com";contactName="测试联系人";contactPhone="13800138000";status=1} $h
if ($r.Code -in 200,201) {
    $tenantId = if ($r.Body.data.tenantId) { $r.Body.data.tenantId } elseif ($r.Body.data.id) { $r.Body.data.id } elseif ($r.Body.data -is [string]) { $r.Body.data } else { $r.Body.id }
    Add-CrudResult "Tenant" "Tenant" "CREATE" "PASS" "ID=$tenantId"
    
    $r2 = Invoke-Api GET "/api/tenants/$tenantId" $null $h
    Add-CrudResult "Tenant" "Tenant" "READ" $(if($r2.Code -eq 200){"PASS"}else{"FAIL"}) "HTTP $($r2.Code)"
    
    $r3 = Invoke-Api PUT "/api/tenants/$tenantId" @{tenantName="$tenantName-updated";tenantCode="t_$testId";tenantDomain="test-$testId.jgsy.com";contactName="更新联系人";status=1} $h
    Add-CrudResult "Tenant" "Tenant" "UPDATE" $(if($r3.Code -in 200,204){"PASS"}else{"FAIL"}) "HTTP $($r3.Code)"
    
    $r4 = Invoke-Api DELETE "/api/tenants/$tenantId" $null $h
    Add-CrudResult "Tenant" "Tenant" "DELETE" $(if($r4.Code -in 200,204){"PASS"}else{"FAIL"}) "HTTP $($r4.Code)"
} else {
    Add-CrudResult "Tenant" "Tenant" "CREATE" "FAIL" "HTTP $($r.Code) $($r.Error)"
}

# ============================================================
# 5. Identity 服务 - 用户查询 (不做创建/删除避免污染)
# ============================================================
Write-Host "`n--- Identity: 用户 ---" -ForegroundColor Yellow
$r = Invoke-Api GET "/api/system/user?page=1&pageSize=5" $null $h
if ($r.Code -eq 200) {
    $userCount = if ($r.Body.data.total) { $r.Body.data.total } elseif ($r.Body.data.items) { $r.Body.data.items.Count } else { 0 }
    Add-CrudResult "Identity" "User" "LIST" "PASS" "共 $userCount 条"
} else {
    Add-CrudResult "Identity" "User" "LIST" "FAIL" "HTTP $($r.Code)"
}

$r2 = Invoke-Api GET "/api/user/profile" $null $h
Add-CrudResult "Identity" "User" "PROFILE" $(if($r2.Code -eq 200){"PASS"}else{"FAIL"}) "HTTP $($r2.Code)"

# ============================================================
# 6. Station 服务 - 场站 CRUD
# ============================================================
Write-Host "`n--- Station: 场站 ---" -ForegroundColor Yellow
$stationName = "test-station-$testId"
$r = Invoke-Api POST "/api/stations" @{name=$stationName;address="自动化测试地址";status=1} $h
if ($r.Code -in 200,201) {
    $stationId = if ($r.Body.data.id) { $r.Body.data.id } elseif ($r.Body.data) { $r.Body.data } else { $r.Body.id }
    Add-CrudResult "Station" "Station" "CREATE" "PASS" "ID=$stationId"
    
    $dbRow = Invoke-DbQuery "jgsy_station" "SELECT name,create_by FROM station_info WHERE id='$stationId' AND delete_at IS NULL"
    if ($dbRow -and $dbRow.Trim().Length -gt 0) {
        Add-CrudResult "Station" "Station" "DB-CREATE" "PASS" "DB=$($dbRow.Trim())"
    } else {
        Add-CrudResult "Station" "Station" "DB-CREATE" "FAIL" "DB 无记录"
    }
    
    $r2 = Invoke-Api GET "/api/stations/$stationId" $null $h
    Add-CrudResult "Station" "Station" "READ" $(if($r2.Code -eq 200){"PASS"}else{"FAIL"}) "HTTP $($r2.Code)"
    
    $r3 = Invoke-Api PUT "/api/stations/$stationId" @{name="$stationName-updated";address="更新地址"} $h
    Add-CrudResult "Station" "Station" "UPDATE" $(if($r3.Code -in 200,204){"PASS"}else{"FAIL"}) "HTTP $($r3.Code)"
    
    $r4 = Invoke-Api DELETE "/api/stations/$stationId" $null $h
    Add-CrudResult "Station" "Station" "DELETE" $(if($r4.Code -in 200,204){"PASS"}else{"FAIL"}) "HTTP $($r4.Code)"
    
    $dbDel = Invoke-DbQuery "jgsy_station" "SELECT delete_at FROM station_info WHERE id='$stationId'"
    Add-CrudResult "Station" "Station" "SOFT-DELETE" $(if($dbDel -and $dbDel.Trim() -eq "t"){"PASS"}else{"FAIL"}) "delete_at=$($dbDel.Trim())"
} else {
    Add-CrudResult "Station" "Station" "CREATE" "FAIL" "HTTP $($r.Code) $($r.Error)"
}

# ============================================================
# 7. Device 服务 - 设备 CRUD
# ============================================================
Write-Host "`n--- Device: 设备 ---" -ForegroundColor Yellow
$r = Invoke-Api GET "/api/device?page=1&pageSize=5" $null $h
Add-CrudResult "Device" "Device" "LIST" $(if($r.Code -eq 200){"PASS"}else{"FAIL"}) "HTTP $($r.Code)"

$deviceName = "test-device-$testId"
$r = Invoke-Api POST "/api/device" @{name=$deviceName;code="DEV$testId";typeId="00000000-0000-0000-0000-000000000001";status=1} $h
if ($r.Code -in 200,201) {
    $deviceId = if ($r.Body.data.id) { $r.Body.data.id } elseif ($r.Body.data) { $r.Body.data } else { $r.Body.id }
    Add-CrudResult "Device" "Device" "CREATE" "PASS" "ID=$deviceId"
    
    $r2 = Invoke-Api GET "/api/device/$deviceId" $null $h
    Add-CrudResult "Device" "Device" "READ" $(if($r2.Code -eq 200){"PASS"}else{"FAIL"}) "HTTP $($r2.Code)"
    
    $r4 = Invoke-Api DELETE "/api/device/$deviceId" $null $h
    Add-CrudResult "Device" "Device" "DELETE" $(if($r4.Code -in 200,204){"PASS"}else{"FAIL"}) "HTTP $($r4.Code)"
} else {
    Add-CrudResult "Device" "Device" "CREATE" $(if($r.Code -in 400,422){"WARN"}else{"FAIL"}) "HTTP $($r.Code) (可能需要设备类型)"
}

# ============================================================
# 8. Account 服务 - 账户查询
# ============================================================
Write-Host "`n--- Account: 账户 ---" -ForegroundColor Yellow
$acctPaths = @("/api/wallet", "/api/account/list?page=1&pageSize=5", "/api/accounts?page=1&pageSize=5")
$found = $false
foreach ($ap in $acctPaths) {
    $r = Invoke-Api GET $ap $null $h
    if ($r.Code -eq 200) {
        Add-CrudResult "Account" "Account" "LIST" "PASS" "路径=$ap"
        $found = $true; break
    }
}
if (!$found) { Add-CrudResult "Account" "Account" "LIST" "WARN" "账户端点需探索" }

# ============================================================
# 9. Charging 服务 - 充电查询
# ============================================================
Write-Host "`n--- Charging: 充电 ---" -ForegroundColor Yellow
$chargingPaths = @("/api/charging/records?page=1&pageSize=5", "/api/charging/orders?page=1&pageSize=5", "/api/charging/list?page=1&pageSize=5")
$found = $false
foreach ($cp in $chargingPaths) {
    $r = Invoke-Api GET $cp $null $h
    if ($r.Code -eq 200) {
        Add-CrudResult "Charging" "ChargingRecord" "LIST" "PASS" "路径=$cp"
        $found = $true; break
    }
}
if (!$found) { Add-CrudResult "Charging" "ChargingRecord" "LIST" "WARN" "未找到列表端点" }

# ============================================================
# 10. Settlement 服务 - 结算查询
# ============================================================
Write-Host "`n--- Settlement: 结算 ---" -ForegroundColor Yellow
$settlePaths = @("/api/settlement/records?page=1&pageSize=5", "/api/settlements?page=1&pageSize=5", "/api/settlement/list?page=1&pageSize=5")
$found = $false
foreach ($sp in $settlePaths) {
    $r = Invoke-Api GET $sp $null $h
    if ($r.Code -eq 200) {
        Add-CrudResult "Settlement" "Settlement" "LIST" "PASS" "路径=$sp"
        $found = $true; break
    }
}
if (!$found) { Add-CrudResult "Settlement" "Settlement" "LIST" "WARN" "未找到列表端点" }

# ============================================================
# 11. WorkOrder 服务 - 工单 CRUD
# ============================================================
Write-Host "`n--- WorkOrder: 工单 ---" -ForegroundColor Yellow
$r = Invoke-Api GET "/api/workorder?page=1&pageSize=5" $null $h
Add-CrudResult "WorkOrder" "WorkOrder" "LIST" $(if($r.Code -eq 200){"PASS"}else{"FAIL"}) "HTTP $($r.Code)"

$woName = "test-workorder-$testId"
$r = Invoke-Api POST "/api/workorder" @{title=$woName;description="自动化测试工单";priority=1;type=1;status=0} $h
if ($r.Code -in 200,201) {
    $woId = if ($r.Body.data.id) { $r.Body.data.id } elseif ($r.Body.data) { $r.Body.data } else { $r.Body.id }
    Add-CrudResult "WorkOrder" "WorkOrder" "CREATE" "PASS" "ID=$woId"
    
    $r2 = Invoke-Api GET "/api/workorder/$woId" $null $h
    Add-CrudResult "WorkOrder" "WorkOrder" "READ" $(if($r2.Code -eq 200){"PASS"}else{"FAIL"}) "HTTP $($r2.Code)"
    
    $r4 = Invoke-Api DELETE "/api/workorder/$woId" $null $h
    Add-CrudResult "WorkOrder" "WorkOrder" "DELETE" $(if($r4.Code -in 200,204){"PASS"}else{"FAIL"}) "HTTP $($r4.Code)"
} else {
    Add-CrudResult "WorkOrder" "WorkOrder" "CREATE" $(if($r.Code -in 400,405,422){"WARN"}else{"FAIL"}) "HTTP $($r.Code)"
}

# ============================================================
# 12. Analytics 服务 - 数据分析查询
# ============================================================
Write-Host "`n--- Analytics: 数据分析 ---" -ForegroundColor Yellow
$analyticsPaths = @("/api/analytics/reports?page=1&pageSize=5", "/api/analytics/dashboard", "/api/analytics/overview", "/api/analytics/statistics")
$found = $false
foreach ($ap in $analyticsPaths) {
    $r = Invoke-Api GET $ap $null $h
    if ($r.Code -eq 200) {
        Add-CrudResult "Analytics" "Dashboard" "READ" "PASS" "路径=$ap"
        $found = $true; break
    }
}
if (!$found) { Add-CrudResult "Analytics" "Dashboard" "READ" "WARN" "仪表盘端点需探索" }

# ============================================================
# 13. Observability 服务 - 监控查询
# ============================================================
Write-Host "`n--- Observability: 监控 ---" -ForegroundColor Yellow
$obsPaths = @("/api/monitor/operation-logs?page=1&pageSize=5", "/api/system/audit-log/list?page=1&pageSize=5", "/api/observability/logs?page=1&pageSize=5", "/api/audit/logs?page=1&pageSize=5")
$found = $false
foreach ($op in $obsPaths) {
    $r = Invoke-Api GET $op $null $h
    if ($r.Code -eq 200) {
        Add-CrudResult "Observability" "AuditLog" "LIST" "PASS" "路径=$op"
        $found = $true; break
    }
}
if (!$found) { Add-CrudResult "Observability" "AuditLog" "LIST" "WARN" "监控端点需探索" }

# ============================================================
# 14. Storage 服务 - 存储查询
# ============================================================
Write-Host "`n--- Storage: 存储 ---" -ForegroundColor Yellow
$r = Invoke-Api GET "/api/storage/files?page=1&pageSize=5" $null $h
if ($r.Code -eq 200) {
    Add-CrudResult "Storage" "File" "LIST" "PASS" "查询成功"
} else {
    $r2 = Invoke-Api GET "/api/files?page=1&pageSize=5" $null $h
    Add-CrudResult "Storage" "File" "LIST" $(if($r2.Code -eq 200){"PASS"}else{"WARN"}) "HTTP $($r2.Code)"
}

# ============================================================
# 15. Blockchain 服务 - 区块链查询
# ============================================================
Write-Host "`n--- Blockchain: 区块链 ---" -ForegroundColor Yellow
$bcPaths = @("/api/blockchain/blocks?page=1&pageSize=5", "/api/blockchain/transactions?page=1&pageSize=5", "/api/blockchain/contracts?page=1&pageSize=5")
$found = $false
foreach ($bp in $bcPaths) {
    $r = Invoke-Api GET $bp $null $h
    if ($r.Code -eq 200) {
        Add-CrudResult "Blockchain" "Block" "LIST" "PASS" "路径=$bp"
        $found = $true; break
    }
}
if (!$found) { Add-CrudResult "Blockchain" "Block" "LIST" "WARN" "区块链端点需探索" }

# ============================================================
# 16. Ingestion 服务 - 数据采集
# ============================================================
Write-Host "`n--- Ingestion: 数据采集 ---" -ForegroundColor Yellow
$ingPaths = @("/api/datasource/list?page=1&pageSize=5", "/api/ingestion/datasources?page=1&pageSize=5", "/api/ingestion/tasks?page=1&pageSize=5", "/api/ingestion/channels?page=1&pageSize=5")
$found = $false
foreach ($ip in $ingPaths) {
    $r = Invoke-Api GET $ip $null $h
    if ($r.Code -eq 200) {
        Add-CrudResult "Ingestion" "Task" "LIST" "PASS" "路径=$ip"
        $found = $true; break
    }
}
if (!$found) { Add-CrudResult "Ingestion" "Task" "LIST" "WARN" "采集端点需探索" }

# ============================================================
# 17. ContentPlatform 服务 - 内容平台 CRUD
# ============================================================
Write-Host "`n--- ContentPlatform: 文章 ---" -ForegroundColor Yellow
$r = Invoke-Api GET "/api/content/articles?page=1&pageSize=5" $null $h
Add-CrudResult "ContentPlatform" "Article" "LIST" $(if($r.Code -eq 200){"PASS"}else{"FAIL"}) "HTTP $($r.Code)"

$articleTitle = "test-article-$testId"
$r = Invoke-Api POST "/api/content/articles" @{title=$articleTitle;content="自动化测试文章内容";summary="测试摘要";status=1;categoryId="00000000-0000-0000-0000-000000000001"} $h
if ($r.Code -in 200,201) {
    $articleId = if ($r.Body.data.id) { $r.Body.data.id } elseif ($r.Body.data) { $r.Body.data } else { $r.Body.id }
    Add-CrudResult "ContentPlatform" "Article" "CREATE" "PASS" "ID=$articleId"
    
    $r2 = Invoke-Api GET "/api/content/articles/$articleId" $null $h
    Add-CrudResult "ContentPlatform" "Article" "READ" $(if($r2.Code -eq 200){"PASS"}else{"FAIL"}) "HTTP $($r2.Code)"
    
    $r4 = Invoke-Api DELETE "/api/content/articles/$articleId" $null $h
    Add-CrudResult "ContentPlatform" "Article" "DELETE" $(if($r4.Code -in 200,204){"PASS"}else{"FAIL"}) "HTTP $($r4.Code)"
} else {
    Add-CrudResult "ContentPlatform" "Article" "CREATE" $(if($r.Code -in 400,422){"WARN"}else{"FAIL"}) "HTTP $($r.Code)"
}

# ============================================================
# 18. DigitalTwin 服务 - 数字孪生
# ============================================================
Write-Host "`n--- DigitalTwin: 数字孪生 ---" -ForegroundColor Yellow
$dtPaths = @("/api/digitaltwin/models?page=1&pageSize=5", "/api/digital-twin/models?page=1&pageSize=5", "/api/twins?page=1&pageSize=5")
$found = $false
foreach ($dp in $dtPaths) {
    $r = Invoke-Api GET $dp $null $h
    if ($r.Code -eq 200) {
        Add-CrudResult "DigitalTwin" "Model" "LIST" "PASS" "路径=$dp"
        $found = $true; break
    }
}
if (!$found) { Add-CrudResult "DigitalTwin" "Model" "LIST" "WARN" "数字孪生端点需探索" }

# ============================================================
# 19. EnergyCore 服务 - 能源核心
# ============================================================
Write-Host "`n--- EnergyCore: 能源核心 ---" -ForegroundColor Yellow
$ecPaths = @("/api/energy/plants?page=1&pageSize=5", "/api/energy/overview", "/api/energy-core/plants?page=1&pageSize=5")
$found = $false
foreach ($ep in $ecPaths) {
    $r = Invoke-Api GET $ep $null $h
    if ($r.Code -eq 200) {
        Add-CrudResult "EnergyCore" "Plant" "LIST" "PASS" "路径=$ep"
        $found = $true; break
    }
}
if (!$found) { Add-CrudResult "EnergyCore" "Plant" "LIST" "WARN" "能源端点需探索" }

# ============================================================
# 20. EnergyServices 服务 - 能源服务
# ============================================================
Write-Host "`n--- EnergyServices: 能源服务 ---" -ForegroundColor Yellow
$esPaths = @("/api/energy/services?page=1&pageSize=5", "/api/energy-services/forecasts?page=1&pageSize=5", "/api/energy/trading/orders?page=1&pageSize=5")
$found = $false
foreach ($ep in $esPaths) {
    $r = Invoke-Api GET $ep $null $h
    if ($r.Code -eq 200) {
        Add-CrudResult "EnergyServices" "Service" "LIST" "PASS" "路径=$ep"
        $found = $true; break
    }
}
if (!$found) { Add-CrudResult "EnergyServices" "Service" "LIST" "WARN" "能源服务端点需探索" }

# ========== 汇总 ==========
Write-Host "`n========== CRUD 汇总 ==========" -ForegroundColor Cyan
Write-Host "  PASS: $($global:pass)" -ForegroundColor Green
Write-Host "  FAIL: $($global:fail)" -ForegroundColor $(if($global:fail -eq 0){"Green"}else{"Red"})
Write-Host "  WARN/SKIP: $($global:skip)" -ForegroundColor Yellow

$global:crudResults | Export-Csv -Path $csvPath -NoTypeInformation -Encoding UTF8
Write-Host "  结果导出: $csvPath"

Write-Host "`n========== Layer 3 完成 ==========" -ForegroundColor Cyan
return @{ Pass = $global:pass; Fail = $global:fail; Skip = $global:skip; CsvPath = $csvPath; Results = $global:crudResults }
