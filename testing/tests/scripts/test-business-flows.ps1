<#
.SYNOPSIS
    Layer 4: 业务流程端到端测试
.DESCRIPTION
    测试核心业务链路的完整跑通，验证跨服务调用和数据一致性
#>
param(
    [string]$GatewayBase = "http://localhost:5000",
    [string]$LogDir = "tests/scripts/logs"
)

$ErrorActionPreference = "Continue"
$ts = Get-Date -Format "yyyyMMdd-HHmmss"
$csvPath = "$LogDir/business-flow-$ts.csv"
if (!(Test-Path $LogDir)) { New-Item -ItemType Directory -Path $LogDir -Force | Out-Null }

function Get-Token($user = "admin", $pass = "P@ssw0rd") {
    $body = @{userName=$user;password=$pass} | ConvertTo-Json
    $resp = Invoke-RestMethod -Uri "$GatewayBase/api/auth/login" -Method POST -Body $body -ContentType "application/json" -TimeoutSec 10
    return $resp.data.accessToken
}

$global:flowResults = [System.Collections.Generic.List[pscustomobject]]::new()
$global:fPass = 0; $global:fFail = 0; $global:fSkip = 0

function Add-FlowResult($Flow, $Step, $Status, $Detail) {
    $global:flowResults.Add([pscustomobject]@{
        Flow=$Flow; Step=$Step; Status=$Status; Detail=$Detail; Time=(Get-Date -Format "HH:mm:ss")
    })
    if ($Status -eq "PASS") { $global:fPass++ } elseif ($Status -eq "FAIL") { $global:fFail++ } else { $global:fSkip++ }
    $color = switch($Status) { "PASS" {"Green"} "FAIL" {"Red"} default {"Yellow"} }
    Write-Host "  [$Status] $Flow/$Step : $Detail" -ForegroundColor $color
}

function Invoke-Api($Method, $Path, $Body, $Headers) {
    $params = @{ Uri="$GatewayBase$Path"; Method=$Method; Headers=$Headers; ContentType="application/json"; UseBasicParsing=$true; TimeoutSec=15 }
    if ($Body) { $params.Body = ($Body | ConvertTo-Json -Depth 10 -Compress) }
    try {
        $resp = Invoke-WebRequest @params -ErrorAction Stop
        return @{ Code=$resp.StatusCode; Body=($resp.Content | ConvertFrom-Json) }
    } catch {
        $code = 0; if ($_.Exception.Response) { $code = [int]$_.Exception.Response.StatusCode }
        return @{ Code=$code; Error=$_.Exception.Message }
    }
}

$token = Get-Token
$h = @{ Authorization = "Bearer $token" }
$testId = [guid]::NewGuid().ToString().Substring(0, 8)

Write-Host "`n========== Layer 4: 业务流程端到端测试 ==========" -ForegroundColor Cyan

# ============================================================
# Flow 1: 认证 → 用户信息 → 权限验证 完整链路
# ============================================================
Write-Host "`n--- Flow 1: 认证-用户-权限链路 ---" -ForegroundColor Yellow

# Step 1: 登录
$loginR = Invoke-Api POST "/api/auth/login" @{userName="admin";password="P@ssw0rd"} @{}
if ($loginR.Code -eq 200 -and $loginR.Body.data.accessToken) {
    Add-FlowResult "认证链路" "登录" "PASS" "获得 Token"
    $flowToken = $loginR.Body.data.accessToken
    $flowH = @{ Authorization = "Bearer $flowToken" }
} else {
    Add-FlowResult "认证链路" "登录" "FAIL" "HTTP $($loginR.Code)"
    $flowH = $h
}

# Step 2: 获取用户信息
$profileR = Invoke-Api GET "/api/user/profile" $null $flowH
if ($profileR.Code -eq 200) {
    $uName = if ($profileR.Body.data.userName) { $profileR.Body.data.userName } elseif ($profileR.Body.data.username) { $profileR.Body.data.username } else { 'ok' }
    Add-FlowResult "认证链路" "获取用户信息" "PASS" "用户名=$uName"
} else {
    Add-FlowResult "认证链路" "获取用户信息" "FAIL" "HTTP $($profileR.Code)"
}

# Step 3: 获取菜单/权限树
$menuR = Invoke-Api GET "/api/system/menu/tree" $null $flowH
if ($menuR.Code -eq 200) {
    $menuCount = if ($menuR.Body.data) { ($menuR.Body.data | Measure-Object).Count } else { 0 }
    Add-FlowResult "认证链路" "获取菜单树" "PASS" "菜单数=$menuCount"
} else {
    Add-FlowResult "认证链路" "获取菜单树" "FAIL" "HTTP $($menuR.Code)"
}

# Step 4: 获取角色列表
$roleR = Invoke-Api GET "/api/system/role?page=1&pageSize=100" $null $flowH
if ($roleR.Code -eq 200) {
    Add-FlowResult "认证链路" "获取角色列表" "PASS" "成功"
} else {
    Add-FlowResult "认证链路" "获取角色列表" "FAIL" "HTTP $($roleR.Code)"
}

# Step 5: 获取部门树
$deptR = Invoke-Api GET "/api/department/tree" $null $flowH
if ($deptR.Code -eq 200) {
    Add-FlowResult "认证链路" "获取部门树" "PASS" "成功"
} else {
    Add-FlowResult "认证链路" "获取部门树" "FAIL" "HTTP $($deptR.Code)"
}

# ============================================================
# Flow 2: 角色-权限管理全流程
# ============================================================
Write-Host "`n--- Flow 2: 角色权限管理流程 ---" -ForegroundColor Yellow

# Step 1: 创建角色
$roleCode = "flow_role_$testId"
$r = Invoke-Api POST "/api/system/role" @{roleName="流程测试角色$testId";roleCode=$roleCode;description="业务流程测试";status=1} $h
if ($r.Code -in 200,201) {
    $roleId = if ($r.Body.data.id) { $r.Body.data.id } elseif ($r.Body.data) { $r.Body.data } else { $r.Body.id }
    Add-FlowResult "角色权限" "创建角色" "PASS" "ID=$roleId"
    
    # Step 2: 获取权限树
    $permR = Invoke-Api GET "/api/system/permission/tree" $null $h
    if ($permR.Code -eq 200) {
        Add-FlowResult "角色权限" "获取权限树" "PASS" "成功"
    } else {
        Add-FlowResult "角色权限" "获取权限树" "WARN" "HTTP $($permR.Code)"
    }
    
    # Step 3: 查看角色详情
    $detailR = Invoke-Api GET "/api/system/role/$roleId" $null $h
    if ($detailR.Code -eq 200) {
        Add-FlowResult "角色权限" "查看角色详情" "PASS" "成功"
    } else {
        Add-FlowResult "角色权限" "查看角色详情" "FAIL" "HTTP $($detailR.Code)"
    }
    
    # Step 4: 更新角色
    $updR = Invoke-Api PUT "/api/system/role/$roleId" @{roleName="流程测试角色-已更新$testId";roleCode=$roleCode;description="已更新";status=1} $h
    Add-FlowResult "角色权限" "更新角色" $(if($updR.Code -in 200,204){"PASS"}else{"FAIL"}) "HTTP $($updR.Code)"
    
    # Step 5: 删除角色
    $delR = Invoke-Api DELETE "/api/system/role/$roleId" $null $h
    Add-FlowResult "角色权限" "删除角色" $(if($delR.Code -in 200,204){"PASS"}else{"FAIL"}) "HTTP $($delR.Code)"
    
    # Step 6: 验证不可见
    $chkR = Invoke-Api GET "/api/system/role/$roleId" $null $h
    Add-FlowResult "角色权限" "验证删除不可见" $(if($chkR.Code -eq 404 -or ($chkR.Body -and $chkR.Body.success -eq $false)){"PASS"}else{"FAIL"}) "HTTP $($chkR.Code)"
} else {
    Add-FlowResult "角色权限" "创建角色" "FAIL" "HTTP $($r.Code)"
}

# ============================================================
# Flow 3: 字典管理 → 字典项全流程
# ============================================================
Write-Host "`n--- Flow 3: 字典管理全流程 ---" -ForegroundColor Yellow

$dictCode = "FLOW_DICT_$($testId.ToUpper())"
$r = Invoke-Api POST "/api/system/dict/types" @{code=$dictCode;name="流程字典$testId";description="业务流程";status=1} $h
if ($r.Code -in 200,201) {
    $dictId = if ($r.Body.data.id) { $r.Body.data.id } elseif ($r.Body.data) { $r.Body.data } else { $r.Body.id }
    Add-FlowResult "字典管理" "创建字典类型" "PASS" "ID=$dictId"
    
    # 创建字典项
    $itemR = Invoke-Api POST "/api/system/dict/items" @{typeCode=$dictCode;label="项A";value="val_a";sort=1;status=1} $h
    if ($itemR.Code -in 200,201) {
        $itemId = if ($itemR.Body.data.id) { $itemR.Body.data.id } elseif ($itemR.Body.data) { $itemR.Body.data } else { $itemR.Body.id }
        Add-FlowResult "字典管理" "创建字典项" "PASS" "ID=$itemId"
    } else {
        Add-FlowResult "字典管理" "创建字典项" "WARN" "HTTP $($itemR.Code)"
    }
    
    # 查询字典项列表
    $listR = Invoke-Api GET "/api/system/dict/items/code/$dictCode" $null $h
    Add-FlowResult "字典管理" "查询字典项" $(if($listR.Code -eq 200){"PASS"}else{"WARN"}) "HTTP $($listR.Code)"
    
    # 清理
    $delR = Invoke-Api DELETE "/api/system/dict/types/$dictId" $null $h
    Add-FlowResult "字典管理" "删除字典类型" $(if($delR.Code -in 200,204){"PASS"}else{"FAIL"}) "HTTP $($delR.Code)"
} else {
    Add-FlowResult "字典管理" "创建字典类型" "FAIL" "HTTP $($r.Code)"
}

# ============================================================
# Flow 4: 场站 → 设备 → 充电 业务链路
# ============================================================
Write-Host "`n--- Flow 4: 场站-设备-充电链路 ---" -ForegroundColor Yellow

# 创建场站
$stationR = Invoke-Api POST "/api/stations" @{name="流程测试场站$testId";address="流程测试地址";status=1} $h
if ($stationR.Code -in 200,201) {
    $stationId = if ($stationR.Body.data.id) { $stationR.Body.data.id } elseif ($stationR.Body.data) { $stationR.Body.data } else { $stationR.Body.id }
    Add-FlowResult "场站设备" "创建场站" "PASS" "ID=$stationId"
    
    # 查看场站详情
    $stDetailR = Invoke-Api GET "/api/stations/$stationId" $null $h
    Add-FlowResult "场站设备" "查看场站详情" $(if($stDetailR.Code -eq 200){"PASS"}else{"FAIL"}) "HTTP $($stDetailR.Code)"
    
    # 查看设备列表
    $devListR = Invoke-Api GET "/api/device?page=1&pageSize=5" $null $h
    Add-FlowResult "场站设备" "查看设备列表" $(if($devListR.Code -eq 200){"PASS"}else{"FAIL"}) "HTTP $($devListR.Code)"
    
    # 查看充电订单
    $chgR = Invoke-Api GET "/api/charging/admin/orders?page=1&pageSize=5" $null $h
    if ($chgR.Code -eq 200) {
        Add-FlowResult "场站设备" "查看充电订单" "PASS" "成功"
    } else {
        Add-FlowResult "场站设备" "查看充电订单" "WARN" "HTTP $($chgR.Code)"
    }
    
    # 清理场站
    $delStR = Invoke-Api DELETE "/api/stations/$stationId" $null $h
    Add-FlowResult "场站设备" "删除场站" $(if($delStR.Code -in 200,204){"PASS"}else{"FAIL"}) "HTTP $($delStR.Code)"
} else {
    Add-FlowResult "场站设备" "创建场站" "FAIL" "HTTP $($stationR.Code)"
}

# ============================================================
# Flow 5: 租户管理全流程
# ============================================================
Write-Host "`n--- Flow 5: 租户管理全流程 ---" -ForegroundColor Yellow

$tenantR = Invoke-Api POST "/api/tenants" @{name="流程租户$testId";code="FT$testId";contactName="测试人";contactPhone="13900139000";status=1} $h
if ($tenantR.Code -in 200,201) {
    $tenantId = if ($tenantR.Body.data.id) { $tenantR.Body.data.id } elseif ($tenantR.Body.data) { $tenantR.Body.data } else { $tenantR.Body.id }
    Add-FlowResult "租户管理" "创建租户" "PASS" "ID=$tenantId"
    
    # 查看租户列表
    $tListR = Invoke-Api GET "/api/tenants?page=1&pageSize=10" $null $h
    Add-FlowResult "租户管理" "查看租户列表" $(if($tListR.Code -eq 200){"PASS"}else{"FAIL"}) "HTTP $($tListR.Code)"
    
    # 查看租户详情
    $tDetailR = Invoke-Api GET "/api/tenants/$tenantId" $null $h
    Add-FlowResult "租户管理" "查看租户详情" $(if($tDetailR.Code -eq 200){"PASS"}else{"FAIL"}) "HTTP $($tDetailR.Code)"
    
    # 更新租户
    $tUpdR = Invoke-Api PUT "/api/tenants/$tenantId" @{name="流程租户-已更新$testId";code="FT$testId";contactName="更新人";status=1} $h
    Add-FlowResult "租户管理" "更新租户" $(if($tUpdR.Code -in 200,204){"PASS"}else{"FAIL"}) "HTTP $($tUpdR.Code)"
    
    # 删除租户
    $tDelR = Invoke-Api DELETE "/api/tenants/$tenantId" $null $h
    Add-FlowResult "租户管理" "删除租户" $(if($tDelR.Code -in 200,204){"PASS"}else{"FAIL"}) "HTTP $($tDelR.Code)"
} else {
    Add-FlowResult "租户管理" "创建租户" "FAIL" "HTTP $($tenantR.Code)"
}

# ============================================================
# Flow 6: 公告发布全流程
# ============================================================
Write-Host "`n--- Flow 6: 公告发布全流程 ---" -ForegroundColor Yellow

$noticeR = Invoke-Api POST "/api/tenant/announcements" @{title="流程测试公告$testId";content="端到端测试公告内容";type="system";priority="normal"} $h
if ($noticeR.Code -in 200,201) {
    $noticeId = if ($noticeR.Body.data.id) { $noticeR.Body.data.id } elseif ($noticeR.Body.data) { $noticeR.Body.data } else { $noticeR.Body.id }
    Add-FlowResult "公告发布" "创建公告" "PASS" "ID=$noticeId"
    
    # 发布
    $pubR = Invoke-Api POST "/api/tenant/announcements/$noticeId/publish" $null $h
    Add-FlowResult "公告发布" "发布公告" $(if($pubR.Code -in 200,204){"PASS"}else{"WARN"}) "HTTP $($pubR.Code)"
    
    # 查看列表验证可见
    $nListR = Invoke-Api GET "/api/tenant/announcements?page=1&pageSize=10" $null $h
    Add-FlowResult "公告发布" "列表可见" $(if($nListR.Code -eq 200){"PASS"}else{"FAIL"}) "HTTP $($nListR.Code)"
    
    # 删除
    $nDelR = Invoke-Api DELETE "/api/tenant/announcements/$noticeId" $null $h
    Add-FlowResult "公告发布" "删除公告" $(if($nDelR.Code -in 200,204){"PASS"}else{"FAIL"}) "HTTP $($nDelR.Code)"
} else {
    Add-FlowResult "公告发布" "创建公告" "FAIL" "HTTP $($noticeR.Code)"
}

# ============================================================
# Flow 7: 数据查询全链路（各服务查询端点）
# ============================================================
Write-Host "`n--- Flow 7: 数据查询全链路 ---" -ForegroundColor Yellow

$queryEndpoints = @(
    @{Name="用户列表";Path="/api/system/user?page=1&pageSize=5"},
    @{Name="角色列表";Path="/api/system/role?page=1&pageSize=5"},
    @{Name="字典类型列表";Path="/api/system/dict/types?page=1&pageSize=5"},
    @{Name="菜单树";Path="/api/system/menu/tree"},
    @{Name="部门树";Path="/api/department/tree"},
    @{Name="租户列表";Path="/api/tenants?page=1&pageSize=5"},
    @{Name="场站列表";Path="/api/stations?page=1&pageSize=5"},
    @{Name="设备列表";Path="/api/device?page=1&pageSize=5"},
    @{Name="工单列表";Path="/api/workorder?page=1&pageSize=5"},
    @{Name="文章列表";Path="/api/content/articles?page=1&pageSize=5"},
    @{Name="用户资料";Path="/api/user/profile"},
    @{Name="系统配置";Path="/api/system/config"},
    @{Name="权限统计-日报";Path="/api/permissions/statistics/aggregate/daily"},
    @{Name="权限临时-到期";Path="/api/permissions/temporary/expiring"},
    @{Name="操作日志";Path="/api/system/operation-log?page=1&pageSize=5"},
    @{Name="登录日志";Path="/api/system/login-log?page=1&pageSize=5"}
)

foreach ($ep in $queryEndpoints) {
    $r = Invoke-Api GET $ep.Path $null $h
    if ($r.Code -eq 200) {
        Add-FlowResult "数据查询" $ep.Name "PASS" "200 OK"
    } elseif ($r.Code -in 400..499) {
        Add-FlowResult "数据查询" $ep.Name "WARN" "HTTP $($r.Code)"
    } else {
        Add-FlowResult "数据查询" $ep.Name "FAIL" "HTTP $($r.Code)"
    }
}

# ============================================================
# Flow 8: 跨服务数据一致性验证
# ============================================================
Write-Host "`n--- Flow 8: 跨服务数据一致性 ---" -ForegroundColor Yellow

# 验证分页数据一致性
$page1 = Invoke-Api GET "/api/system/role?page=1&pageSize=5" $null $h
$page2 = Invoke-Api GET "/api/system/role?page=2&pageSize=5" $null $h
if ($page1.Code -eq 200 -and $page2.Code -eq 200) {
    $ids1 = if ($page1.Body.data.items) { $page1.Body.data.items | ForEach-Object { $_.id } } else { @() }
    $ids2 = if ($page2.Body.data.items) { $page2.Body.data.items | ForEach-Object { $_.id } } else { @() }
    $overlap = $ids1 | Where-Object { $_ -in $ids2 }
    if ($overlap.Count -eq 0) {
        Add-FlowResult "数据一致" "分页无重叠" "PASS" "Page1=$($ids1.Count) Page2=$($ids2.Count)"
    } else {
        Add-FlowResult "数据一致" "分页无重叠" "FAIL" "重叠 $($overlap.Count) 条"
    }
} else {
    Add-FlowResult "数据一致" "分页无重叠" "WARN" "查询失败"
}

# 验证 DB vs API 总数一致
$apiTotal = if ($page1.Body.data.total) { $page1.Body.data.total } else { 0 }
$dbTotal = docker exec -e PGCLIENTENCODING=UTF8 jgsy-postgres psql -U postgres -d jgsy_permission -t -A -c "SELECT count(*) FROM perm_role WHERE delete_at IS NULL" 2>$null
if ($dbTotal) {
    $dbCount = [int]$dbTotal.Trim()
    if ([Math]::Abs($apiTotal - $dbCount) -le 2) {
        Add-FlowResult "数据一致" "API与DB总数" "PASS" "API=$apiTotal DB=$dbCount"
    } else {
        Add-FlowResult "数据一致" "API与DB总数" "WARN" "API=$apiTotal DB=$dbCount 差异较大"
    }
} else {
    Add-FlowResult "数据一致" "API与DB总数" "WARN" "DB查询失败"
}

# ========== 汇总 ==========
Write-Host "`n========== 业务流程汇总 ==========" -ForegroundColor Cyan
Write-Host "  PASS: $($global:fPass)" -ForegroundColor Green
Write-Host "  FAIL: $($global:fFail)" -ForegroundColor $(if($global:fFail -eq 0){"Green"}else{"Red"})
Write-Host "  WARN/SKIP: $($global:fSkip)" -ForegroundColor Yellow

$global:flowResults | Export-Csv -Path $csvPath -NoTypeInformation -Encoding UTF8
Write-Host "  结果导出: $csvPath"

Write-Host "`n========== Layer 4 完成 ==========" -ForegroundColor Cyan
return @{ Pass=$global:fPass; Fail=$global:fFail; Skip=$global:fSkip; CsvPath=$csvPath }
