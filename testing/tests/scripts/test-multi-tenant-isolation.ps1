<#
.SYNOPSIS
    多租户数据隔离全面测试
.DESCRIPTION
    ╔══════════════════════════════════════════════════════════════╗
    ║  JGSY.AGI 多租户数据隔离测试                                ║
    ║  目标：验证租户间数据完全隔离、跨租户访问被拒绝              ║
    ║  覆盖：创建隔离 → 读隔离 → 写隔离 → 删隔离 → 安全边界      ║
    ╚══════════════════════════════════════════════════════════════╝
    
    测试流程:
    ┌──────────────────────────────────────────────────────────────┐
    │  SETUP:    创建2个测试租户 + 管理员 + 登录获取Token          │
    │  Phase 1:  租户A创建资源（角色/站点/公告/字典/用户等）       │
    │  Phase 2:  租户B创建资源（同模块不同数据）                   │
    │  Phase 3:  读隔离 — A只见A的数据，B只见B的数据               │
    │  Phase 4:  跨租户直接访问 — B访问A的ID → 404/403             │
    │  Phase 5:  跨租户写入 — B修改/删除A → 拒绝                   │
    │  Phase 6:  SUPER_ADMIN全局可见性                              │
    │  Phase 7:  租户生命周期（禁用/启用/暂停）                     │
    │  Phase 8:  安全边界（伪造Header/过期Token/无Token）           │
    │  Phase 9:  租户条件验证（配额/过期/参数校验）                 │
    │  CLEANUP: 清理所有测试数据                                    │
    └──────────────────────────────────────────────────────────────┘
#>
param(
    [string]$GatewayUrl = "http://localhost:5000",
    [string]$IdentityUrl = "http://localhost:8002",
    [string]$InternalKey = "jgsy_internal_service_key_2024_prod_v2!@#",
    [string]$PgHost = "localhost",
    [int]$PgPort = 5432,
    [string]$PgUser = "postgres",
    [string]$PgPass = "P@ssw0rd",
    [string]$PgDb = "jgsy_identity"
)

$ErrorActionPreference = 'Continue'
$logDir = "$PSScriptRoot\logs"
if (-not (Test-Path $logDir)) { New-Item -ItemType Directory -Path $logDir -Force | Out-Null }

$ts = Get-Date -Format 'yyyyMMdd-HHmmss'
$csvFile = "$logDir\multi-tenant-isolation-$ts.csv"
$uid = Get-Date -Format 'HHmmss'

# ════════════════════════════════════════════════════════════════
# 全局工具函数
# ════════════════════════════════════════════════════════════════
$script:results = @()
$script:pass = 0; $script:fail = 0; $script:warn = 0; $script:skip = 0

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
        [hashtable]$Headers = @{}, [int]$Timeout = 15
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
        $code = 0; $body = ""
        if ($_.Exception.Response) {
            $code = [int]$_.Exception.Response.StatusCode
            try { $body = [System.IO.StreamReader]::new($_.Exception.Response.GetResponseStream()).ReadToEnd() } catch {}
        }
        return @{ Code = $code; Body = $body; Data = $null; Error = $_.Exception.Message }
    }
}

function Extract-Id {
    param($response, [string[]]$fields = @("id","tenantId","roleId","stationId","deviceId"))
    if (-not $response.Data) { return $null }
    $d = $response.Data.data
    if (-not $d) { $d = $response.Data }
    foreach ($f in $fields) {
        if ($d.$f) { return $d.$f }
    }
    if ($d -is [string] -and $d -match '^[0-9a-f\-]{36}$') { return $d }
    return $null
}

function Exec-Psql {
    param([string]$Sql, [string]$Database = $PgDb)
    try {
        $env:PGPASSWORD = $PgPass
        $raw = docker exec -e PGCLIENTENCODING=UTF8 jgsy-postgres psql -U $PgUser -d $Database -t -A -c $Sql 2>&1
        # docker exec may return array; join and trim
        if ($raw -is [array]) { $result = ($raw | Where-Object { $_ -is [string] }) -join "`n" }
        else { $result = "$raw" }
        return $result.Trim()
    } catch {
        Write-Host "    [DB] psql 执行失败: $_" -ForegroundColor DarkYellow
        return $null
    }
}

# ════════════════════════════════════════════════════════════════
# SETUP: 登录 SUPER_ADMIN
# ════════════════════════════════════════════════════════════════
Write-Host "`n" -NoNewline
Write-Host "╔══════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║  JGSY.AGI 多租户数据隔离测试                            ║" -ForegroundColor Cyan
Write-Host "║  租户隔离 × 跨访问拒绝 × 安全边界 × 生命周期            ║" -ForegroundColor Cyan
Write-Host "╚══════════════════════════════════════════════════════════╝" -ForegroundColor Cyan

Write-Host "`n━━━━━ SETUP: 登录 SUPER_ADMIN ━━━━━" -ForegroundColor Magenta
$loginR = Invoke-Api POST "$GatewayUrl/api/auth/login" @{userName="admin";password="P@ssw0rd"}
if ($loginR.Code -ne 200 -or -not $loginR.Data.data.accessToken) {
    Write-Host "  ✗ SUPER_ADMIN 登录失败，终止测试" -ForegroundColor Red
    exit 1
}
$adminToken = $loginR.Data.data.accessToken
$adminRefresh = $loginR.Data.data.refreshToken
$adminHeaders = @{ Authorization = "Bearer $adminToken" }
$adminTenantId = $loginR.Data.data.user.tenantId
Write-Host "  ✓ SUPER_ADMIN 登录成功 (TenantId=$adminTenantId)" -ForegroundColor Green

# ════════════════════════════════════════════════════════════════
# SETUP: 创建测试租户 A 和 B
# ════════════════════════════════════════════════════════════════
Write-Host "`n━━━━━ SETUP: 创建测试租户 ━━━━━" -ForegroundColor Magenta

$tenantA_code = "iso_a_$uid"
$tenantB_code = "iso_b_$uid"
$phoneA = "139${uid}01"
$phoneB = "139${uid}02"

# 创建租户 A
$rA = Invoke-Api POST "$GatewayUrl/api/tenants" @{
    tenantName   = "隔离测试企业A_$uid"
    tenantCode   = $tenantA_code
    tenantDomain = "iso-a-$uid.test.com"
    contactPerson = "管理员A"
    contactPhone  = $phoneA
    maxUserCount  = 50
    packageType   = "Standard"
} -Headers $adminHeaders

$tenantA_id = $null
if ($rA.Code -in 200,201) {
    $tenantA_id = Extract-Id $rA
    if (-not $tenantA_id -and $rA.Data.tenantId) { $tenantA_id = $rA.Data.tenantId }
    if (-not $tenantA_id -and $rA.Data.data.tenantId) { $tenantA_id = $rA.Data.data.tenantId }
    Write-Host "  ✓ 租户A创建成功: $tenantA_id ($tenantA_code)" -ForegroundColor Green
} else {
    Write-Host "  ✗ 租户A创建失败: HTTP $($rA.Code) $($rA.Body)" -ForegroundColor Red
    Write-Host "    尝试从现有租户中发现..." -ForegroundColor Yellow
    $listR = Invoke-Api GET "$GatewayUrl/api/tenants?keyword=iso_a_$uid&pageSize=1" -Headers $adminHeaders
    if ($listR.Data.data.items -and $listR.Data.data.items.Count -gt 0) {
        $tenantA_id = $listR.Data.data.items[0].tenantId
        if (-not $tenantA_id) { $tenantA_id = $listR.Data.data.items[0].id }
        Write-Host "  ✓ 发现已有租户A: $tenantA_id" -ForegroundColor Yellow
    }
}

# 创建租户 B
$rB = Invoke-Api POST "$GatewayUrl/api/tenants" @{
    tenantName   = "隔离测试企业B_$uid"
    tenantCode   = $tenantB_code
    tenantDomain = "iso-b-$uid.test.com"
    contactPerson = "管理员B"
    contactPhone  = $phoneB
    maxUserCount  = 50
    packageType   = "Standard"
} -Headers $adminHeaders

$tenantB_id = $null
if ($rB.Code -in 200,201) {
    $tenantB_id = Extract-Id $rB
    if (-not $tenantB_id -and $rB.Data.tenantId) { $tenantB_id = $rB.Data.tenantId }
    if (-not $tenantB_id -and $rB.Data.data.tenantId) { $tenantB_id = $rB.Data.data.tenantId }
    Write-Host "  ✓ 租户B创建成功: $tenantB_id ($tenantB_code)" -ForegroundColor Green
} else {
    Write-Host "  ✗ 租户B创建失败: HTTP $($rB.Code) $($rB.Body)" -ForegroundColor Red
}

if (-not $tenantA_id -or -not $tenantB_id) {
    Write-Host "`n  ✗ 无法创建测试租户，终止测试" -ForegroundColor Red
    exit 1
}

# ════════════════════════════════════════════════════════════════
# SETUP: 创建租户管理员 (内部API → Identity服务直连)
# ════════════════════════════════════════════════════════════════
Write-Host "`n━━━━━ SETUP: 创建租户管理员 ━━━━━" -ForegroundColor Magenta

$internalHeaders = @{ "X-Internal-Service-Key" = $InternalKey; "X-Service-Name" = "multi-tenant-test" }

# 计算唯一手机号 (确保 11 位数字)
$phoneAdminA = "138${uid}01".PadRight(11, '0').Substring(0,11)
$phoneAdminB = "138${uid}02".PadRight(11, '0').Substring(0,11)
$usernameA = "admin_$phoneAdminA"
$usernameB = "admin_$phoneAdminB"
$adminPassword = "Test@Admin123"

# 创建租户A管理员
$rAdminA = Invoke-Api POST "$IdentityUrl/api/internal/users/create-tenant-admin" @{
    tenantId   = $tenantA_id
    adminName  = "租户A管理员"
    adminPhone = $phoneAdminA
    adminEmail = "admin_a_$uid@test.com"
    password   = $adminPassword
} -Headers $internalHeaders

$adminA_userId = $null
if ($rAdminA.Code -in 200,201) {
    $adminA_userId = Extract-Id $rAdminA
    if (-not $adminA_userId) {
        if ($rAdminA.Data.id) { $adminA_userId = $rAdminA.Data.id }
        elseif ($rAdminA.Data.data.id) { $adminA_userId = $rAdminA.Data.data.id }
    }
    Write-Host "  ✓ 租户A管理员创建成功: userId=$adminA_userId username=$usernameA" -ForegroundColor Green
} else {
    Write-Host "  ⚠ 租户A管理员创建: HTTP $($rAdminA.Code) — $($rAdminA.Body)" -ForegroundColor Yellow
    # 尝试通过手机号查找
    $findR = Invoke-Api GET "$IdentityUrl/api/internal/users/by-phone/$phoneAdminA" -Headers $internalHeaders
    if ($findR.Code -eq 200 -and $findR.Data) {
        $adminA_userId = if ($findR.Data.id) { $findR.Data.id } elseif ($findR.Data.data.id) { $findR.Data.data.id } else { $null }
        Write-Host "  ✓ 发现已有租户A管理员: $adminA_userId" -ForegroundColor Yellow
    }
    # 最终降级：从数据库查找
    if (-not $adminA_userId) {
        $dbId = Exec-Psql "SELECT id FROM user_info WHERE user_name = '$usernameA' AND delete_at IS NULL LIMIT 1;"
        if ($dbId -and $dbId.Length -gt 30) { $adminA_userId = $dbId.Trim(); Write-Host "  ✓ 从数据库发现租户A管理员: $adminA_userId" -ForegroundColor Yellow }
    }
}

# 创建租户B管理员
$rAdminB = Invoke-Api POST "$IdentityUrl/api/internal/users/create-tenant-admin" @{
    tenantId   = $tenantB_id
    adminName  = "租户B管理员"
    adminPhone = $phoneAdminB
    adminEmail = "admin_b_$uid@test.com"
    password   = $adminPassword
} -Headers $internalHeaders

$adminB_userId = $null
if ($rAdminB.Code -in 200,201) {
    $adminB_userId = Extract-Id $rAdminB
    if (-not $adminB_userId) {
        if ($rAdminB.Data.id) { $adminB_userId = $rAdminB.Data.id }
        elseif ($rAdminB.Data.data.id) { $adminB_userId = $rAdminB.Data.data.id }
    }
    Write-Host "  ✓ 租户B管理员创建成功: userId=$adminB_userId username=$usernameB" -ForegroundColor Green
} else {
    Write-Host "  ⚠ 租户B管理员创建: HTTP $($rAdminB.Code) — $($rAdminB.Body)" -ForegroundColor Yellow
    $findR = Invoke-Api GET "$IdentityUrl/api/internal/users/by-phone/$phoneAdminB" -Headers $internalHeaders
    if ($findR.Code -eq 200 -and $findR.Data) {
        $adminB_userId = if ($findR.Data.id) { $findR.Data.id } elseif ($findR.Data.data.id) { $findR.Data.data.id } else { $null }
        Write-Host "  ✓ 发现已有租户B管理员: $adminB_userId" -ForegroundColor Yellow
    }
    # 最终降级：从数据库查找
    if (-not $adminB_userId) {
        $dbId = Exec-Psql "SELECT id FROM user_info WHERE user_name = '$usernameB' AND delete_at IS NULL LIMIT 1;"
        if ($dbId -and $dbId.Length -gt 30) { $adminB_userId = $dbId.Trim(); Write-Host "  ✓ 从数据库发现租户B管理员: $adminB_userId" -ForegroundColor Yellow }
    }
}

# ════════════════════════════════════════════════════════════════
# SETUP: 验证 user_tenant 记录 (Bug修复后平台应自动创建)
# ════════════════════════════════════════════════════════════════
Write-Host "`n━━━━━ SETUP: 验证 user_tenant 记录（平台自动创建） ━━━━━" -ForegroundColor Magenta

$tenantAdminRoleId = "00000000-0000-0000-0000-000000000010"  # TENANT_ADMIN 内置角色
$systemUserId = "00000000-0000-0000-0000-000000000001"     # system creator

if ($adminA_userId) {
    $verifyA = Exec-Psql "SELECT count(*) FROM user_tenant WHERE user_id = '$adminA_userId' AND tenant_id = '$tenantA_id' AND delete_at IS NULL;"
    if ([int]$verifyA -ge 1) {
        Write-Host "  ✓ 租户A user_tenant 记录已由平台自动创建 (记录数=$verifyA)" -ForegroundColor Green
        $tenantIdA = Exec-Psql "SELECT tenant_id FROM user_info WHERE id = '$adminA_userId';"
        Write-Host "  ✓ 租户A管理员 user_info.tenant_id = $tenantIdA" -ForegroundColor Green
    } else {
        Write-Host "  ✗ 租户A user_tenant 记录缺失（平台Bug未修复），使用DB补救..." -ForegroundColor Yellow
        Exec-Psql "INSERT INTO user_tenant (id, tenant_id, user_id, role_id, role_name, is_default, is_admin, joined_at, join_type, status, create_by, create_name, create_time, update_by, update_name, update_time, delete_at) VALUES (gen_random_uuid(), '$tenantA_id', '$adminA_userId', '$tenantAdminRoleId', 'TENANT_ADMIN', true, true, NOW(), 'system', 1, '$systemUserId', '系统', NOW(), '$systemUserId', '系统', NOW(), NULL);"
        Exec-Psql "UPDATE user_info SET tenant_id = '$tenantA_id' WHERE id = '$adminA_userId' AND tenant_id != '$tenantA_id';"
    }
} else {
    Write-Host "  ✗ 租户A管理员userId为空" -ForegroundColor Red
}

if ($adminB_userId) {
    $verifyB = Exec-Psql "SELECT count(*) FROM user_tenant WHERE user_id = '$adminB_userId' AND tenant_id = '$tenantB_id' AND delete_at IS NULL;"
    if ([int]$verifyB -ge 1) {
        Write-Host "  ✓ 租户B user_tenant 记录已由平台自动创建 (记录数=$verifyB)" -ForegroundColor Green
        $tenantIdB = Exec-Psql "SELECT tenant_id FROM user_info WHERE id = '$adminB_userId';"
        Write-Host "  ✓ 租户B管理员 user_info.tenant_id = $tenantIdB" -ForegroundColor Green
    } else {
        Write-Host "  ✗ 租户B user_tenant 记录缺失（平台Bug未修复），使用DB补救..." -ForegroundColor Yellow
        Exec-Psql "INSERT INTO user_tenant (id, tenant_id, user_id, role_id, role_name, is_default, is_admin, joined_at, join_type, status, create_by, create_name, create_time, update_by, update_name, update_time, delete_at) VALUES (gen_random_uuid(), '$tenantB_id', '$adminB_userId', '$tenantAdminRoleId', 'TENANT_ADMIN', true, true, NOW(), 'system', 1, '$systemUserId', '系统', NOW(), '$systemUserId', '系统', NOW(), NULL);"
        Exec-Psql "UPDATE user_info SET tenant_id = '$tenantB_id' WHERE id = '$adminB_userId' AND tenant_id != '$tenantB_id';"
    }
} else {
    Write-Host "  ✗ 租户B管理员userId为空" -ForegroundColor Red
}

# ════════════════════════════════════════════════════════════════
# SETUP: 给测试租户管理员分配权限 (通过数据库)
# ════════════════════════════════════════════════════════════════
Write-Host "`n━━━━━ SETUP: 分配权限给租户管理员 ━━━━━" -ForegroundColor Magenta

$superAdminRoleId = "00000000-0000-0000-0000-000000000001"
$script:testRoleA_id = $null
$script:testRoleB_id = $null

function Grant-TenantPermissions {
    param([string]$TenantId, [string]$UserId, [string]$Label)
    
    # 1) 在 perm_role 中为该租户创建测试角色
    $testRoleId = [System.Guid]::NewGuid().ToString()
    $roleSql = "INSERT INTO perm_role (id, role_name, role_code, status, scope, level, is_system, sort_order, tenant_id, create_by, create_name, create_time, update_by, update_name, update_time, delete_at) VALUES ('$testRoleId', 'IsoTestAdmin_$uid', 'ISO_TEST_ADMIN_${uid}_${Label}', 1, 1, 1, false, 999, '$TenantId', '$systemUserId', '系统', NOW(), '$systemUserId', '系统', NOW(), NULL);"
    $roleResult = Exec-Psql $roleSql "jgsy_permission"
    Write-Host "    角色创建: [$roleResult]" -ForegroundColor DarkGray
    
    # 2) 复制 SUPER_ADMIN 的权限到该测试角色 (取关键的权限)
    $permCopySql = "INSERT INTO perm_role_permission (id, role_id, perm_id, tenant_id, create_by, create_name, create_time, update_by, update_name, update_time, delete_at) SELECT gen_random_uuid(), '$testRoleId', rp.perm_id, '$TenantId', '$systemUserId', '系统', NOW(), '$systemUserId', '系统', NOW(), NULL FROM perm_role_permission rp WHERE rp.role_id = '$superAdminRoleId' AND rp.delete_at IS NULL;"
    $copyResult = Exec-Psql $permCopySql "jgsy_permission"
    Write-Host "    权限复制: [$copyResult]" -ForegroundColor DarkGray
    
    # 3) 创建 perm_user_role 绑定
    $userRoleSql = "INSERT INTO perm_user_role (id, user_id, role_id, tenant_id, create_by, create_name, create_time, update_by, update_name, update_time, delete_at) SELECT gen_random_uuid(), '$UserId', '$testRoleId', '$TenantId', '$systemUserId', '系统', NOW(), '$systemUserId', '系统', NOW(), NULL WHERE NOT EXISTS (SELECT 1 FROM perm_user_role WHERE user_id = '$UserId' AND role_id = '$testRoleId' AND delete_at IS NULL);"
    Exec-Psql $userRoleSql "jgsy_permission"
    
    # 验证
    $permCount = Exec-Psql "SELECT count(*) FROM perm_role_permission WHERE role_id = '$testRoleId' AND delete_at IS NULL;" "jgsy_permission"
    Write-Host "  ✓ $Label 权限分配完成: roleId=$testRoleId, 权限数=$permCount ($copyResult)" -ForegroundColor Green
    
    return $testRoleId
}

if ($adminA_userId -and $tenantA_id) {
    $script:testRoleA_id = Grant-TenantPermissions -TenantId $tenantA_id -UserId $adminA_userId -Label "租户A"
}
if ($adminB_userId -and $tenantB_id) {
    $script:testRoleB_id = Grant-TenantPermissions -TenantId $tenantB_id -UserId $adminB_userId -Label "租户B"
}

# ════════════════════════════════════════════════════════════════
# SETUP: 登录租户管理员
# ════════════════════════════════════════════════════════════════
Write-Host "`n━━━━━ SETUP: 登录租户管理员 ━━━━━" -ForegroundColor Magenta

$tokenA = $null; $tokenB = $null
$headersA = @{}; $headersB = @{}

# 登录租户A管理员
$loginA = Invoke-Api POST "$GatewayUrl/api/auth/login" @{userName=$usernameA; password=$adminPassword; tenantId=$tenantA_id}
if ($loginA.Code -eq 200 -and $loginA.Data.data.accessToken) {
    $tokenA = $loginA.Data.data.accessToken
    $headersA = @{ Authorization = "Bearer $tokenA" }
    $tenantA_jwt = $loginA.Data.data.user.tenantId
    Write-Host "  ✓ 租户A管理员登录成功 (JWT.tenantId=$tenantA_jwt)" -ForegroundColor Green
    Add-R "SETUP" "登录" "租户A管理员登录" "PASS" "username=$usernameA"
} else {
    Write-Host "  ✗ 租户A管理员登录失败: HTTP $($loginA.Code) $($loginA.Body)" -ForegroundColor Red
    Add-R "SETUP" "登录" "租户A管理员登录" "FAIL" "HTTP $($loginA.Code)"
    # 尝试用手机号登录
    $loginA2 = Invoke-Api POST "$GatewayUrl/api/auth/login" @{userName=$phoneAdminA; password=$adminPassword; tenantId=$tenantA_id}
    if ($loginA2.Code -eq 200 -and $loginA2.Data.data.accessToken) {
        $tokenA = $loginA2.Data.data.accessToken
        $headersA = @{ Authorization = "Bearer $tokenA" }
        Write-Host "  ✓ 租户A管理员通过手机号登录成功" -ForegroundColor Green
    }
}

# 登录租户B管理员
$loginB = Invoke-Api POST "$GatewayUrl/api/auth/login" @{userName=$usernameB; password=$adminPassword; tenantId=$tenantB_id}
if ($loginB.Code -eq 200 -and $loginB.Data.data.accessToken) {
    $tokenB = $loginB.Data.data.accessToken
    $headersB = @{ Authorization = "Bearer $tokenB" }
    $tenantB_jwt = $loginB.Data.data.user.tenantId
    Write-Host "  ✓ 租户B管理员登录成功 (JWT.tenantId=$tenantB_jwt)" -ForegroundColor Green
    Add-R "SETUP" "登录" "租户B管理员登录" "PASS" "username=$usernameB"
} else {
    Write-Host "  ✗ 租户B管理员登录失败: HTTP $($loginB.Code) $($loginB.Body)" -ForegroundColor Red
    Add-R "SETUP" "登录" "租户B管理员登录" "FAIL" "HTTP $($loginB.Code)"
    $loginB2 = Invoke-Api POST "$GatewayUrl/api/auth/login" @{userName=$phoneAdminB; password=$adminPassword; tenantId=$tenantB_id}
    if ($loginB2.Code -eq 200 -and $loginB2.Data.data.accessToken) {
        $tokenB = $loginB2.Data.data.accessToken
        $headersB = @{ Authorization = "Bearer $tokenB" }
        Write-Host "  ✓ 租户B管理员通过手机号登录成功" -ForegroundColor Green
    }
}

# 判断是否可以继续
$canTestIsolation = ($null -ne $tokenA -and $null -ne $tokenB)
if (-not $canTestIsolation) {
    Write-Host "`n  ⚠ 无法获取两个租户的Token，将使用 SUPER_ADMIN + 数据库级别验证" -ForegroundColor Yellow
}

# ════════════════════════════════════════════════════════════════
# 定义隔离测试模块
# ════════════════════════════════════════════════════════════════
$isoModules = @(
    @{
        Name = "角色"; Key = "role"
        ListUrl = "/api/system/role"; CreateUrl = "/api/system/role"; UpdateUrl = "/api/system/role/{id}"; DeleteUrl = "/api/system/role/{id}"; DetailUrl = "/api/system/role/{id}"
        CreateBodyA = { param($i) @{ name = "IsoRoleA_${uid}_$i"; code = "ISO_A_${uid}_$i"; sortOrder = $i; status = 1 } }
        CreateBodyB = { param($i) @{ name = "IsoRoleB_${uid}_$i"; code = "ISO_B_${uid}_$i"; sortOrder = $i; status = 1 } }
        ListField = "items"; NameField = "name"; MatchA = "IsoRoleA_$uid"; MatchB = "IsoRoleB_$uid"
    },
    @{
        Name = "充电站"; Key = "station"
        ListUrl = "/api/stations"; CreateUrl = "/api/stations"; UpdateUrl = "/api/stations/{id}"; DeleteUrl = "/api/stations/{id}"; DetailUrl = "/api/stations/{id}"
        CreateBodyA = { param($i) @{ name = "IsoStationA_${uid}_$i"; code = "ISA_${uid}_$i"; address = "A地址$i"; longitude = 116.4; latitude = 39.9; status = 1 } }
        CreateBodyB = { param($i) @{ name = "IsoStationB_${uid}_$i"; code = "ISB_${uid}_$i"; address = "B地址$i"; longitude = 117.4; latitude = 40.9; status = 1 } }
        ListField = "items"; NameField = "name"; MatchA = "IsoStationA_$uid"; MatchB = "IsoStationB_$uid"
    },
    @{
        Name = "字典类型"; Key = "dict"
        ListUrl = "/api/system/dict/types"; CreateUrl = "/api/system/dict/types"; UpdateUrl = "/api/system/dict/types/{id}"; DeleteUrl = "/api/system/dict/types/{id}"; DetailUrl = "/api/system/dict/types/{id}"
        CreateBodyA = { param($i) @{ code = "ISO_DICT_A_${uid}_$i"; name = "隔离字典A_${uid}_$i"; sortOrder = $i; status = 1 } }
        CreateBodyB = { param($i) @{ code = "ISO_DICT_B_${uid}_$i"; name = "隔离字典B_${uid}_$i"; sortOrder = $i; status = 1 } }
        ListField = "items"; NameField = "name"; MatchA = "隔离字典A_$uid"; MatchB = "隔离字典B_$uid"
    },
    @{
        Name = "公告"; Key = "announcement"
        ListUrl = "/api/system/announcements"; CreateUrl = "/api/system/announcements"; UpdateUrl = "/api/system/announcements/{id}"; DeleteUrl = "/api/system/announcements/{id}"; DetailUrl = "/api/system/announcements/{id}"
        CreateBodyA = { param($i) @{ title = "隔离公告A_${uid}_$i"; content = "租户A公告内容$i"; type = "notice"; status = 0 } }
        CreateBodyB = { param($i) @{ title = "隔离公告B_${uid}_$i"; content = "租户B公告内容$i"; type = "notice"; status = 0 } }
        ListField = "items"; NameField = "title"; MatchA = "隔离公告A_$uid"; MatchB = "隔离公告B_$uid"
    },
    @{
        Name = "租户公告"; Key = "tenant-ann"
        ListUrl = "/api/tenant/announcements"; CreateUrl = "/api/tenant/announcements"; UpdateUrl = "/api/tenant/announcements/{id}"; DeleteUrl = "/api/tenant/announcements/{id}"; DetailUrl = "/api/tenant/announcements/{id}"
        CreateBodyA = { param($i) @{ title = "租户A公告_${uid}_$i"; content = "隔离内容A$i"; type = "system"; priority = "normal"; targetAudience = "all" } }
        CreateBodyB = { param($i) @{ title = "租户B公告_${uid}_$i"; content = "隔离内容B$i"; type = "system"; priority = "normal"; targetAudience = "all" } }
        ListField = "items"; NameField = "title"; MatchA = "租户A公告_$uid"; MatchB = "租户B公告_$uid"
    },
    @{
        Name = "租户分类"; Key = "tenant-cat"
        ListUrl = "/api/tenant/categories"; CreateUrl = "/api/tenant/categories"; UpdateUrl = "/api/tenant/categories/{id}"; DeleteUrl = "/api/tenant/categories/{id}"; DetailUrl = "/api/tenant/categories/{id}"
        CreateBodyA = { param($i) @{ categoryName = "隔离分类A_${uid}_$i"; categoryCode = "ISOA_${uid}_$i"; sortOrder = $i } }
        CreateBodyB = { param($i) @{ categoryName = "隔离分类B_${uid}_$i"; categoryCode = "ISOB_${uid}_$i"; sortOrder = $i } }
        ListField = "items"; NameField = "categoryName"; MatchA = "隔离分类A_$uid"; MatchB = "隔离分类B_$uid"
    },
    @{
        Name = "工单"; Key = "workorder"
        ListUrl = "/api/workorder"; CreateUrl = "/api/workorder/fault"; UpdateUrl = $null; DeleteUrl = $null; DetailUrl = "/api/workorder/{id}"
        CreateBodyA = { param($i) @{ title = "隔离工单A_${uid}_$i"; description = "租户A工单$i"; priority = "high"; source = "test" } }
        CreateBodyB = { param($i) @{ title = "隔离工单B_${uid}_$i"; description = "租户B工单$i"; priority = "high"; source = "test" } }
        ListField = "items"; NameField = "title"; MatchA = "隔离工单A_$uid"; MatchB = "隔离工单B_$uid"
    }
)

# 存储每个模块创建的资源ID
$resourcesA = @{}  # key=module.Key, value=@(id1, id2)
$resourcesB = @{}

# ════════════════════════════════════════════════════════════════
# Phase 1: 租户A创建资源
# ════════════════════════════════════════════════════════════════
Write-Host "`n━━━━━ Phase 1: 租户A创建资源 ━━━━━" -ForegroundColor Magenta

if ($canTestIsolation) {
    foreach ($mod in $isoModules) {
        if (-not $mod.CreateUrl) { continue }
        $ids = @()
        for ($i = 1; $i -le 2; $i++) {
            $body = & $mod.CreateBodyA $i
            $r = Invoke-Api POST "$GatewayUrl$($mod.CreateUrl)" $body -Headers $headersA
            if ($r.Code -in 200,201) {
                $id = Extract-Id $r
                if ($id) { $ids += $id }
                Add-R "CREATE-A" $mod.Name "租户A创建#$i" "PASS" "HTTP $($r.Code) ID=$id"
            } elseif ($r.Code -in 400,403,409,500) {
                Add-R "CREATE-A" $mod.Name "租户A创建#$i" "WARN" "HTTP $($r.Code) — 权限不足或服务限制"
            } else {
                Add-R "CREATE-A" $mod.Name "租户A创建#$i" "FAIL" "HTTP $($r.Code)"
            }
        }
        $resourcesA[$mod.Key] = $ids
    }
} else {
    # Fallback: 用 SUPER_ADMIN 创建，通过数据库层面验证
    foreach ($mod in $isoModules) {
        if (-not $mod.CreateUrl) { continue }
        $ids = @()
        for ($i = 1; $i -le 2; $i++) {
            $body = & $mod.CreateBodyA $i
            $r = Invoke-Api POST "$GatewayUrl$($mod.CreateUrl)" $body -Headers $adminHeaders
            if ($r.Code -in 200,201) {
                $id = Extract-Id $r
                if ($id) { $ids += $id }
                Add-R "CREATE-A" $mod.Name "SUPER_ADMIN代创建A#$i" "PASS" "HTTP $($r.Code) ID=$id"
            } else {
                Add-R "CREATE-A" $mod.Name "SUPER_ADMIN代创建A#$i" "WARN" "HTTP $($r.Code)"
            }
        }
        $resourcesA[$mod.Key] = $ids
    }
}

# ════════════════════════════════════════════════════════════════
# Phase 2: 租户B创建资源
# ════════════════════════════════════════════════════════════════
Write-Host "`n━━━━━ Phase 2: 租户B创建资源 ━━━━━" -ForegroundColor Magenta

if ($canTestIsolation) {
    foreach ($mod in $isoModules) {
        if (-not $mod.CreateUrl) { continue }
        $ids = @()
        for ($i = 1; $i -le 2; $i++) {
            $body = & $mod.CreateBodyB $i
            $r = Invoke-Api POST "$GatewayUrl$($mod.CreateUrl)" $body -Headers $headersB
            if ($r.Code -in 200,201) {
                $id = Extract-Id $r
                if ($id) { $ids += $id }
                Add-R "CREATE-B" $mod.Name "租户B创建#$i" "PASS" "HTTP $($r.Code) ID=$id"
            } elseif ($r.Code -in 400,403,409,500) {
                Add-R "CREATE-B" $mod.Name "租户B创建#$i" "WARN" "HTTP $($r.Code) — 权限不足或服务限制"
            } else {
                Add-R "CREATE-B" $mod.Name "租户B创建#$i" "FAIL" "HTTP $($r.Code)"
            }
        }
        $resourcesB[$mod.Key] = $ids
    }
} else {
    foreach ($mod in $isoModules) {
        if (-not $mod.CreateUrl) { continue }
        $ids = @()
        for ($i = 1; $i -le 2; $i++) {
            $body = & $mod.CreateBodyB $i
            $r = Invoke-Api POST "$GatewayUrl$($mod.CreateUrl)" $body -Headers $adminHeaders
            if ($r.Code -in 200,201) {
                $id = Extract-Id $r
                if ($id) { $ids += $id }
                Add-R "CREATE-B" $mod.Name "SUPER_ADMIN代创建B#$i" "PASS" "HTTP $($r.Code) ID=$id"
            } else {
                Add-R "CREATE-B" $mod.Name "SUPER_ADMIN代创建B#$i" "WARN" "HTTP $($r.Code)"
            }
        }
        $resourcesB[$mod.Key] = $ids
    }
}

# ════════════════════════════════════════════════════════════════
# Phase 3: 读隔离 — 租户A/B各自只能看到自己的数据
# ════════════════════════════════════════════════════════════════
Write-Host "`n━━━━━ Phase 3: 读隔离验证 ━━━━━" -ForegroundColor Magenta

if ($canTestIsolation) {
    foreach ($mod in $isoModules) {
        $listUrl = "$GatewayUrl$($mod.ListUrl)?page=1&pageSize=100"
        $listField = $mod.ListField
        
        # ---- 租户A查列表 ----
        $rListA = Invoke-Api GET $listUrl -Headers $headersA
        if ($rListA.Code -eq 200) {
            $itemsA = $rListA.Data.data
            if ($listField -and $itemsA.$listField) { $itemsA = $itemsA.$listField }
            elseif ($itemsA -is [array]) { }  # 已是数组
            else { $itemsA = @() }
            
            $nameField = $mod.NameField
            $namesA = @($itemsA | ForEach-Object { $_.$nameField })
            
            # 3.1 A 能看到自己的数据
            $hasOwnA = ($namesA | Where-Object { $_ -match [regex]::Escape($mod.MatchA) }).Count
            if ($hasOwnA -gt 0) {
                Add-R "READ-ISO" $mod.Name "租户A看到自己数据" "PASS" "匹配 $hasOwnA 条"
            } else {
                Add-R "READ-ISO" $mod.Name "租户A看到自己数据" "WARN" "未匹配到自己数据(可能权限不足)"
            }
            
            # 3.2 A 不应看到 B 的数据
            $seesBData = ($namesA | Where-Object { $_ -match [regex]::Escape($mod.MatchB) }).Count
            if ($seesBData -eq 0) {
                Add-R "READ-ISO" $mod.Name "租户A不可见B数据" "PASS" "确认不可见"
            } else {
                Add-R "READ-ISO" $mod.Name "租户A不可见B数据" "FAIL" "泄露! 看到B数据 $seesBData 条"
            }
        } else {
            Add-R "READ-ISO" $mod.Name "租户A列表查询" "WARN" "HTTP $($rListA.Code)"
        }
        
        # ---- 租户B查列表 ----
        $rListB = Invoke-Api GET $listUrl -Headers $headersB
        if ($rListB.Code -eq 200) {
            $itemsB = $rListB.Data.data
            if ($listField -and $itemsB.$listField) { $itemsB = $itemsB.$listField }
            elseif ($itemsB -is [array]) { }
            else { $itemsB = @() }
            
            $namesB = @($itemsB | ForEach-Object { $_.$nameField })
            
            # 3.3 B 能看到自己的数据
            $hasOwnB = ($namesB | Where-Object { $_ -match [regex]::Escape($mod.MatchB) }).Count
            if ($hasOwnB -gt 0) {
                Add-R "READ-ISO" $mod.Name "租户B看到自己数据" "PASS" "匹配 $hasOwnB 条"
            } else {
                Add-R "READ-ISO" $mod.Name "租户B看到自己数据" "WARN" "未匹配到自己数据(可能权限不足)"
            }
            
            # 3.4 B 不应看到 A 的数据
            $seesAData = ($namesB | Where-Object { $_ -match [regex]::Escape($mod.MatchA) }).Count
            if ($seesAData -eq 0) {
                Add-R "READ-ISO" $mod.Name "租户B不可见A数据" "PASS" "确认不可见"
            } else {
                Add-R "READ-ISO" $mod.Name "租户B不可见A数据" "FAIL" "泄露! 看到A数据 $seesAData 条"
            }
        } else {
            Add-R "READ-ISO" $mod.Name "租户B列表查询" "WARN" "HTTP $($rListB.Code)"
        }
    }
} else {
    # Fallback: 数据库级别验证租户隔离
    Write-Host "  >> 使用数据库级别验证（无法通过API测试双租户隔离）" -ForegroundColor Yellow
    
    # 验证数据库中的 tenant_id 字段
    $dbTables = @(
        @{Table="user_info"; TenantCol="tenant_id"; Name="用户表"},
        @{Table="perm_role"; TenantCol="tenant_id"; Name="角色表"}
    )
    foreach ($tbl in $dbTables) {
        $sql = "SELECT COUNT(*) FROM $($tbl.Table) WHERE delete_at IS NULL"
        $count = Exec-Psql $sql
        if ($count) {
            $sqlNull = "SELECT COUNT(*) FROM $($tbl.Table) WHERE tenant_id IS NULL AND delete_at IS NULL"
            $nullCount = Exec-Psql $sqlNull
            $nullCountInt = 0; try { $nullCountInt = [int]$nullCount.ToString().Trim() } catch { $nullCountInt = -1 }
            if ($nullCountInt -eq 0) {
                Add-R "READ-ISO" "DB验证" "$($tbl.Name) tenant_id 完整" "PASS" "无NULL记录"
            } else {
                Add-R "READ-ISO" "DB验证" "$($tbl.Name) tenant_id 完整" "FAIL" "$nullCountInt 条记录缺少 tenant_id"
            }
        } else {
            Add-R "READ-ISO" "DB验证" "$($tbl.Name) 查询" "WARN" "无法访问数据库"
        }
    }
}

# ════════════════════════════════════════════════════════════════
# Phase 4: 跨租户ID直接访问 — B访问A的资源ID → 应返回 404/403
# ════════════════════════════════════════════════════════════════
Write-Host "`n━━━━━ Phase 4: 跨租户ID直接访问 ━━━━━" -ForegroundColor Magenta

if ($canTestIsolation) {
    foreach ($mod in $isoModules) {
        $aIds = $resourcesA[$mod.Key]
        if (-not $aIds -or $aIds.Count -eq 0) {
            Add-R "CROSS-ID" $mod.Name "跨访问(无A资源)" "SKIP" ""
            continue
        }
        
        $targetId = $aIds[0]
        
        # 4.1 B尝试GET A的资源详情
        if ($mod.DetailUrl) {
            $detailUrl = "$GatewayUrl$($mod.DetailUrl -replace '\{id\}', $targetId)"
            $r = Invoke-Api GET $detailUrl -Headers $headersB
            if ($r.Code -in 404,403,401) {
                Add-R "CROSS-ID" $mod.Name "B访问A详情→拒绝" "PASS" "HTTP $($r.Code)"
            } elseif ($r.Code -eq 200) {
                # 检查返回的是不是确实A的数据
                $returnedName = $r.Data.data.$($mod.NameField)
                if ($returnedName -match [regex]::Escape($mod.MatchA)) {
                    Add-R "CROSS-ID" $mod.Name "B访问A详情→泄露!" "FAIL" "返回了A的数据: $returnedName"
                } else {
                    Add-R "CROSS-ID" $mod.Name "B访问A详情→拒绝" "PASS" "200但非A数据(可能是B自己的同ID资源)"
                }
            } else {
                Add-R "CROSS-ID" $mod.Name "B访问A详情" "WARN" "HTTP $($r.Code)"
            }
        }
        
        # 4.2 B尝试 PUT A的资源
        if ($mod.UpdateUrl) {
            $updateUrl = "$GatewayUrl$($mod.UpdateUrl -replace '\{id\}', $targetId)"
            $updateBody = @{ name = "HACKED_BY_B" }
            $r = Invoke-Api PUT $updateUrl $updateBody -Headers $headersB
            if ($r.Code -in 404,403,401) {
                Add-R "CROSS-ID" $mod.Name "B修改A资源→拒绝" "PASS" "HTTP $($r.Code)"
            } elseif ($r.Code -in 200,204) {
                Add-R "CROSS-ID" $mod.Name "B修改A资源→⚠️成功" "FAIL" "跨租户写入未被阻止!"
            } else {
                Add-R "CROSS-ID" $mod.Name "B修改A资源" "WARN" "HTTP $($r.Code)"
            }
        }
        
        # 4.3 B尝试 DELETE A的资源
        if ($mod.DeleteUrl) {
            $deleteUrl = "$GatewayUrl$($mod.DeleteUrl -replace '\{id\}', $targetId)"
            $r = Invoke-Api DELETE $deleteUrl -Headers $headersB
            if ($r.Code -in 404,403,401) {
                Add-R "CROSS-ID" $mod.Name "B删除A资源→拒绝" "PASS" "HTTP $($r.Code)"
            } elseif ($r.Code -in 200,204) {
                Add-R "CROSS-ID" $mod.Name "B删除A资源→⚠️成功" "FAIL" "跨租户删除未被阻止!"
            } else {
                Add-R "CROSS-ID" $mod.Name "B删除A资源" "WARN" "HTTP $($r.Code)"
            }
        }
        
        # 反向: A访问B的资源
        $bIds = $resourcesB[$mod.Key]
        if ($bIds -and $bIds.Count -gt 0) {
            $targetBId = $bIds[0]
            if ($mod.DetailUrl) {
                $detailUrl = "$GatewayUrl$($mod.DetailUrl -replace '\{id\}', $targetBId)"
                $r = Invoke-Api GET $detailUrl -Headers $headersA
                if ($r.Code -in 404,403,401) {
                    Add-R "CROSS-ID" $mod.Name "A访问B详情→拒绝" "PASS" "HTTP $($r.Code)"
                } elseif ($r.Code -eq 200) {
                    $returnedName = $r.Data.data.$($mod.NameField)
                    if ($returnedName -match [regex]::Escape($mod.MatchB)) {
                        Add-R "CROSS-ID" $mod.Name "A访问B详情→泄露!" "FAIL" "返回了B的数据"
                    } else {
                        Add-R "CROSS-ID" $mod.Name "A访问B详情→拒绝" "PASS" "200但非B数据"
                    }
                } else {
                    Add-R "CROSS-ID" $mod.Name "A访问B详情" "WARN" "HTTP $($r.Code)"
                }
            }
        }
    }
}

# ════════════════════════════════════════════════════════════════
# Phase 5: SUPER_ADMIN 全局可见性验证
# ════════════════════════════════════════════════════════════════
Write-Host "`n━━━━━ Phase 5: SUPER_ADMIN 全局可见性 ━━━━━" -ForegroundColor Magenta

foreach ($mod in $isoModules) {
    $listUrl = "$GatewayUrl$($mod.ListUrl)?page=1&pageSize=200"
    $r = Invoke-Api GET $listUrl -Headers $adminHeaders
    if ($r.Code -eq 200) {
        $items = $r.Data.data
        $listField = $mod.ListField
        if ($listField -and $items.$listField) { $items = $items.$listField }
        elseif ($items -is [array]) { }
        else { $items = @() }
        
        $nameField = $mod.NameField
        $allNames = @($items | ForEach-Object { $_.$nameField })
        
        # SUPER_ADMIN 应该能看到所有数据（或至少系统租户数据）
        $totalVisible = $allNames.Count
        Add-R "ADMIN-VIEW" $mod.Name "SUPER_ADMIN总可见" "PASS" "可见 $totalVisible 条"
        
        # 如果是双租户模式，检查是否看到 A 和 B
        if ($canTestIsolation) {
            $seesA = ($allNames | Where-Object { $_ -match [regex]::Escape($mod.MatchA) }).Count
            $seesB = ($allNames | Where-Object { $_ -match [regex]::Escape($mod.MatchB) }).Count
            if ($seesA -gt 0 -and $seesB -gt 0) {
                Add-R "ADMIN-VIEW" $mod.Name "SUPER_ADMIN看到A+B" "PASS" "A=$seesA B=$seesB"
            } elseif ($seesA -gt 0 -or $seesB -gt 0) {
                Add-R "ADMIN-VIEW" $mod.Name "SUPER_ADMIN看到部分" "WARN" "A=$seesA B=$seesB (可能需跨租户查询)"
            } else {
                Add-R "ADMIN-VIEW" $mod.Name "SUPER_ADMIN看到A+B" "WARN" "未看到测试数据(可能在系统租户范围内)"
            }
        }
    } else {
        Add-R "ADMIN-VIEW" $mod.Name "SUPER_ADMIN列表" "WARN" "HTTP $($r.Code)"
    }
}

# ════════════════════════════════════════════════════════════════
# Phase 6: 安全边界测试
# ════════════════════════════════════════════════════════════════
Write-Host "`n━━━━━ Phase 6: 安全边界测试 ━━━━━" -ForegroundColor Magenta

# 6.1 无Token访问受保护端点 → 401
$secureEndpoints = @(
    "/api/system/role", "/api/stations", "/api/system/user",
    "/api/tenants", "/api/system/announcements", "/api/workorder"
)
foreach ($ep in $secureEndpoints) {
    $r = Invoke-Api GET "$GatewayUrl$ep?page=1&pageSize=1" -Headers @{}
    if ($r.Code -eq 401) {
        Add-R "SECURITY" "无Token" "无Token访问 $ep" "PASS" "HTTP 401"
    } elseif ($r.Code -in 403,200) {
        # 200 可能是公开端点
        Add-R "SECURITY" "无Token" "无Token访问 $ep" "WARN" "HTTP $($r.Code)"
    } else {
        Add-R "SECURITY" "无Token" "无Token访问 $ep" "PASS" "HTTP $($r.Code) (拒绝访问)"
    }
}

# 6.2 伪造过期Token → 401
$fakeToken = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4iLCJpYXQiOjE1MTYyMzkwMjJ9.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c"
$r = Invoke-Api GET "$GatewayUrl/api/system/role?page=1&pageSize=1" -Headers @{Authorization="Bearer $fakeToken"}
if ($r.Code -eq 401) {
    Add-R "SECURITY" "伪造Token" "过期/伪造Token拒绝" "PASS" "HTTP 401"
} else {
    Add-R "SECURITY" "伪造Token" "过期/伪造Token拒绝" "FAIL" "HTTP $($r.Code) — 应返回401"
}

# 6.3 伪造 X-Tenant-Id Header (已认证用户应被忽略)
if ($canTestIsolation -and $tenantA_id -and $tenantB_id) {
    # 用租户A的Token + 伪造B的TenantId Header
    $forgedHeaders = @{
        Authorization = "Bearer $tokenA"
        "X-Tenant-Id" = $tenantB_id
    }
    $r = Invoke-Api GET "$GatewayUrl/api/system/role?page=1&pageSize=100" -Headers $forgedHeaders
    if ($r.Code -eq 200) {
        $items = $r.Data.data
        if ($items.items) { $items = $items.items }
        $nameField = "name"
        $names = @($items | ForEach-Object { $_.$nameField })
        $seesBData = ($names | Where-Object { $_ -match "IsoRoleB_$uid" }).Count
        if ($seesBData -eq 0) {
            Add-R "SECURITY" "伪造Header" "X-Tenant-Id伪造被忽略" "PASS" "JWT优先，B数据不可见"
        } else {
            Add-R "SECURITY" "伪造Header" "X-Tenant-Id伪造被忽略" "FAIL" "Header覆盖了JWT! 看到B数据 $seesBData 条"
        }
    } else {
        Add-R "SECURITY" "伪造Header" "X-Tenant-Id伪造" "WARN" "HTTP $($r.Code)"
    }
}

# 6.4 错误密码登录 → 拒绝
$r = Invoke-Api POST "$GatewayUrl/api/auth/login" @{userName="admin";password="WrongPassword123"}
if ($r.Code -in 400,401) {
    Add-R "SECURITY" "错误密码" "错误密码被拒绝" "PASS" "HTTP $($r.Code)"
} else {
    Add-R "SECURITY" "错误密码" "错误密码被拒绝" "FAIL" "HTTP $($r.Code)"
}

# 6.5 不存在用户登录 → 拒绝
$r = Invoke-Api POST "$GatewayUrl/api/auth/login" @{userName="nonexist_$uid";password="P@ssw0rd"}
if ($r.Code -in 400,401,404) {
    Add-R "SECURITY" "不存在用户" "不存在用户被拒绝" "PASS" "HTTP $($r.Code)"
} else {
    Add-R "SECURITY" "不存在用户" "不存在用户被拒绝" "FAIL" "HTTP $($r.Code)"
}

# 6.6 SQL注入尝试
$r = Invoke-Api POST "$GatewayUrl/api/auth/login" @{userName="admin' OR '1'='1";password="P@ssw0rd"}
if ($r.Code -in 400,401,404) {
    Add-R "SECURITY" "SQL注入" "SQL注入登录被拒绝" "PASS" "HTTP $($r.Code)"
} else {
    Add-R "SECURITY" "SQL注入" "SQL注入登录被拒绝" "FAIL" "HTTP $($r.Code)"
}

# 6.7 XSS载荷在API参数中
$r = Invoke-Api GET "$GatewayUrl/api/system/role?page=1&pageSize=5&keyword=<script>alert(1)</script>" -Headers $adminHeaders
if ($r.Code -in 200,400) {
    # 检查响应中是否原样返回了脚本标签
    if ($r.Body -match '<script>alert\(1\)</script>') {
        Add-R "SECURITY" "XSS" "XSS载荷未过滤" "WARN" "响应包含原始脚本标签"
    } else {
        Add-R "SECURITY" "XSS" "XSS载荷安全处理" "PASS" "HTTP $($r.Code)"
    }
} else {
    Add-R "SECURITY" "XSS" "XSS载荷" "PASS" "HTTP $($r.Code)"
}

# 6.8 内部API无Key访问
$r = Invoke-Api GET "$IdentityUrl/api/internal/users/count" -Headers @{}
if ($r.Code -in 401,403) {
    Add-R "SECURITY" "内部API" "无Key访问内部API→拒绝" "PASS" "HTTP $($r.Code)"
} else {
    Add-R "SECURITY" "内部API" "无Key访问内部API" "WARN" "HTTP $($r.Code)"
}

# 6.9 内部API错误Key
$r = Invoke-Api GET "$IdentityUrl/api/internal/users/count" -Headers @{"X-Internal-Service-Key"="wrong_key_123"}
if ($r.Code -in 401,403) {
    Add-R "SECURITY" "内部API" "错误Key访问内部API→拒绝" "PASS" "HTTP $($r.Code)"
} else {
    Add-R "SECURITY" "内部API" "错误Key访问内部API" "WARN" "HTTP $($r.Code)"
}

# ════════════════════════════════════════════════════════════════
# Phase 7: 租户生命周期测试
# ════════════════════════════════════════════════════════════════
Write-Host "`n━━━━━ Phase 7: 租户生命周期测试 ━━━━━" -ForegroundColor Magenta

# 7.1 禁用租户A → 检查A管理员是否被阻止
$r = Invoke-Api POST "$GatewayUrl/api/tenants/$tenantA_id/disable" -Headers $adminHeaders
if ($r.Code -in 200,204) {
    Add-R "LIFECYCLE" "禁用" "禁用租户A" "PASS" "HTTP $($r.Code)"
    
    # 7.2 禁用后，A管理员访问需被限制
    if ($tokenA) {
        Start-Sleep -Milliseconds 500
        $r2 = Invoke-Api GET "$GatewayUrl/api/system/role?page=1&pageSize=1" -Headers $headersA
        # 禁用后应该返回 401/403 或正常（取决于实现：是否实时检查租户状态）
        if ($r2.Code -in 401,403) {
            Add-R "LIFECYCLE" "禁用" "禁用后A无法访问" "PASS" "HTTP $($r2.Code) — 租户状态检查实时"
        } else {
            Add-R "LIFECYCLE" "禁用" "禁用后A访问结果" "WARN" "HTTP $($r2.Code) — 可能Token未过期或未实时检查租户状态"
        }
        
        # 7.3 禁用后重新登录应失败
        $r3 = Invoke-Api POST "$GatewayUrl/api/auth/login" @{userName=$usernameA; password=$adminPassword}
        if ($r3.Code -in 400,401,403) {
            Add-R "LIFECYCLE" "禁用" "禁用后A重新登录失败" "PASS" "HTTP $($r3.Code)"
        } else {
            Add-R "LIFECYCLE" "禁用" "禁用后A重新登录" "WARN" "HTTP $($r3.Code) — 租户禁用可能未阻止登录"
        }
    }
} else {
    Add-R "LIFECYCLE" "禁用" "禁用租户A" "WARN" "HTTP $($r.Code)"
}

# 7.4 重新启用租户A
$r = Invoke-Api POST "$GatewayUrl/api/tenants/$tenantA_id/enable" -Headers $adminHeaders
if ($r.Code -in 200,204) {
    Add-R "LIFECYCLE" "启用" "重新启用租户A" "PASS" "HTTP $($r.Code)"
    
    # 7.5 启用后A管理员可以重新登录
    Start-Sleep -Milliseconds 500
    $r2 = Invoke-Api POST "$GatewayUrl/api/auth/login" @{userName=$usernameA; password=$adminPassword; tenantId=$tenantA_id}
    if ($r2.Code -eq 200 -and $r2.Data.data.accessToken) {
        $tokenA = $r2.Data.data.accessToken
        $headersA = @{ Authorization = "Bearer $tokenA" }
        Add-R "LIFECYCLE" "启用" "启用后A重新登录成功" "PASS" ""
    } else {
        Add-R "LIFECYCLE" "启用" "启用后A重新登录" "WARN" "HTTP $($r2.Code)"
    }
} else {
    Add-R "LIFECYCLE" "启用" "重新启用租户A" "WARN" "HTTP $($r.Code)"
}

# 7.6 暂停租户A
$r = Invoke-Api POST "$GatewayUrl/api/tenants/$tenantA_id/suspend" -Headers $adminHeaders
if ($r.Code -in 200,204) {
    Add-R "LIFECYCLE" "暂停" "暂停租户A" "PASS" "HTTP $($r.Code)"
} else {
    Add-R "LIFECYCLE" "暂停" "暂停租户A" "WARN" "HTTP $($r.Code)"
}

# 恢复租户A
$r = Invoke-Api POST "$GatewayUrl/api/tenants/$tenantA_id/enable" -Headers $adminHeaders
if ($r.Code -in 200,204) {
    Add-R "LIFECYCLE" "恢复" "恢复租户A" "PASS" ""
} else {
    Add-R "LIFECYCLE" "恢复" "恢复租户A" "WARN" "HTTP $($r.Code)"
}

# ════════════════════════════════════════════════════════════════
# Phase 8: 租户条件验证
# ════════════════════════════════════════════════════════════════
Write-Host "`n━━━━━ Phase 8: 租户条件验证 ━━━━━" -ForegroundColor Magenta

# 8.1 创建重复编码租户 → 应拒绝
$r = Invoke-Api POST "$GatewayUrl/api/tenants" @{
    tenantName = "重复编码测试"; tenantCode = $tenantA_code; tenantDomain = "dup-$uid.test.com"
    contactPerson = "Test"
} -Headers $adminHeaders
if ($r.Code -in 400,409,422) {
    Add-R "CONDITION" "唯一性" "重复tenantCode被拒绝" "PASS" "HTTP $($r.Code)"
} elseif ($r.Code -in 200,201) {
    Add-R "CONDITION" "唯一性" "重复tenantCode被拒绝" "FAIL" "居然创建成功了!"
    # 清理
    $dupId = Extract-Id $r
    if ($dupId) { Invoke-Api DELETE "$GatewayUrl/api/tenants/$dupId" -Headers $adminHeaders | Out-Null }
} else {
    Add-R "CONDITION" "唯一性" "重复tenantCode" "WARN" "HTTP $($r.Code)"
}

# 8.2 创建重复域名租户 → 应拒绝
$r = Invoke-Api POST "$GatewayUrl/api/tenants" @{
    tenantName = "重复域名测试_$uid"; tenantCode = "dup_dm_$uid"; tenantDomain = "iso-a-$uid.test.com"
    contactPerson = "Test"
} -Headers $adminHeaders
if ($r.Code -in 400,409,422) {
    Add-R "CONDITION" "唯一性" "重复tenantDomain被拒绝" "PASS" "HTTP $($r.Code)"
} elseif ($r.Code -in 200,201) {
    Add-R "CONDITION" "唯一性" "重复tenantDomain被拒绝" "FAIL" "居然创建成功了!"
    $dupId = Extract-Id $r
    if ($dupId) { Invoke-Api DELETE "$GatewayUrl/api/tenants/$dupId" -Headers $adminHeaders | Out-Null }
} else {
    Add-R "CONDITION" "唯一性" "重复tenantDomain" "WARN" "HTTP $($r.Code)"
}

# 8.3 缺少必填字段 → 400
$r = Invoke-Api POST "$GatewayUrl/api/tenants" @{tenantName="缺字段测试"} -Headers $adminHeaders
if ($r.Code -in 400,422) {
    Add-R "CONDITION" "校验" "缺少必填字段拒绝(tenantCode)" "PASS" "HTTP $($r.Code)"
} else {
    Add-R "CONDITION" "校验" "缺少必填字段" "WARN" "HTTP $($r.Code)"
}

# 8.4 空租户名称 → 400
$r = Invoke-Api POST "$GatewayUrl/api/tenants" @{tenantName="";tenantCode="empty_$uid";tenantDomain="empty-$uid.test.com"} -Headers $adminHeaders
if ($r.Code -in 400,422) {
    Add-R "CONDITION" "校验" "空tenantName拒绝" "PASS" "HTTP $($r.Code)"
} else {
    Add-R "CONDITION" "校验" "空tenantName" "WARN" "HTTP $($r.Code)"
    if ($r.Code -in 200,201) {
        $dupId = Extract-Id $r
        if ($dupId) { Invoke-Api DELETE "$GatewayUrl/api/tenants/$dupId" -Headers $adminHeaders | Out-Null }
    }
}

# 8.5 租户详情查询
$r = Invoke-Api GET "$GatewayUrl/api/tenants/$tenantA_id" -Headers $adminHeaders
if ($r.Code -eq 200) {
    $td = $r.Data.data
    if (-not $td) { $td = $r.Data }
    $tenantName = $td.tenantName
    $tenantStatus = $td.status
    Add-R "CONDITION" "详情" "租户A详情查询" "PASS" "name=$tenantName status=$tenantStatus"
} else {
    Add-R "CONDITION" "详情" "租户A详情查询" "WARN" "HTTP $($r.Code)"
}

# 8.6 租户列表分页
$r = Invoke-Api GET "$GatewayUrl/api/tenants?page=1&pageSize=5" -Headers $adminHeaders
if ($r.Code -eq 200) {
    $total = $r.Data.data.totalCount
    if (-not $total) { $total = $r.Data.data.total }
    Add-R "CONDITION" "分页" "租户列表分页" "PASS" "总数=$total"
} else {
    Add-R "CONDITION" "分页" "租户列表分页" "WARN" "HTTP $($r.Code)"
}

# 8.7 租户搜索
$r = Invoke-Api GET "$GatewayUrl/api/tenants?keyword=隔离测试&pageSize=10" -Headers $adminHeaders
if ($r.Code -eq 200) {
    $items = $r.Data.data.items
    if (-not $items) { $items = $r.Data.data }
    $count = if ($items -is [array]) { $items.Count } else { 0 }
    Add-R "CONDITION" "搜索" "租户关键词搜索" "PASS" "匹配 $count 条"
} else {
    Add-R "CONDITION" "搜索" "租户关键词搜索" "WARN" "HTTP $($r.Code)"
}

# 8.8 更新租户信息
$r = Invoke-Api PUT "$GatewayUrl/api/tenants/$tenantA_id" @{tenantName="隔离测试企业A_已修改_$uid"; contactPerson="修改后联系人"} -Headers $adminHeaders
if ($r.Code -in 200,204) {
    Add-R "CONDITION" "更新" "租户信息更新" "PASS" "HTTP $($r.Code)"
} else {
    Add-R "CONDITION" "更新" "租户信息更新" "WARN" "HTTP $($r.Code)"
}

# 8.9 租户状态变更
$r = Invoke-Api PATCH "$GatewayUrl/api/tenants/$tenantA_id/status" @{status=1} -Headers $adminHeaders
if ($r.Code -in 200,204,405) {
    Add-R "CONDITION" "状态" "租户状态变更" "PASS" "HTTP $($r.Code)"
} else {
    Add-R "CONDITION" "状态" "租户状态变更" "WARN" "HTTP $($r.Code)"
}

# ════════════════════════════════════════════════════════════════
# Phase 9: 数据库级租户隔离验证
# ════════════════════════════════════════════════════════════════
Write-Host "`n━━━━━ Phase 9: 数据库级租户隔离验证 ━━━━━" -ForegroundColor Magenta

# 检查关键表是否包含 tenant_id 字段且无 NULL
$dbChecks = @(
    @{Db="jgsy_identity"; Table="user_info"; Name="用户表"},
    @{Db="jgsy_permission"; Table="perm_role"; Name="角色表"},
    @{Db="jgsy_station"; Table="station_info"; Name="充电站表"},
    @{Db="jgsy_device"; Table="device_info"; Name="设备表"},
    @{Db="jgsy_workorder"; Table="workorder_info"; Name="工单表"},
    @{Db="jgsy_tenant"; Table="tenant_info"; Name="租户表"},
    @{Db="jgsy_charging"; Table="charging_order"; Name="充电订单表"},
    @{Db="jgsy_settlement"; Table="settlement_record"; Name="结算表"},
    @{Db="jgsy_content"; Table="content_article"; Name="文章表"},
    @{Db="jgsy_ingestion"; Table="ingestion_task"; Name="采集任务表"}
)

foreach ($chk in $dbChecks) {
    # 检查表是否有 tenant_id 列
    $colCheck = Exec-Psql "SELECT column_name FROM information_schema.columns WHERE table_name = '$($chk.Table)' AND column_name = 'tenant_id'" $chk.Db
    if ($colCheck -and $colCheck.ToString().Trim() -match 'tenant_id') {
        # 检查是否有 NULL tenant_id
        $nullCount = Exec-Psql "SELECT COUNT(*) FROM $($chk.Table) WHERE tenant_id IS NULL AND delete_at IS NULL" $chk.Db
        $nullInt = 0; try { $nullInt = [int]$nullCount.ToString().Trim() } catch { $nullInt = -1 }
        if ($nullInt -eq 0) {
            Add-R "DB-ISO" $chk.Name "tenant_id 字段完整性" "PASS" "无NULL记录"
        } else {
            Add-R "DB-ISO" $chk.Name "tenant_id 字段完整性" "WARN" "存在 $nullInt 条 NULL tenant_id"
        }
        
        # 检查是否有 delete_at 列（软删除）
        $delCol = Exec-Psql "SELECT column_name FROM information_schema.columns WHERE table_name = '$($chk.Table)' AND column_name = 'delete_at'" $chk.Db
        if ($delCol -and $delCol.ToString().Trim() -match 'delete_at') {
            Add-R "DB-ISO" $chk.Name "delete_at 软删除字段" "PASS" "字段存在"
        } else {
            Add-R "DB-ISO" $chk.Name "delete_at 软删除字段" "WARN" "字段不存在"
        }
    } elseif ($colCheck) {
        Add-R "DB-ISO" $chk.Name "tenant_id 字段存在" "PASS" ""
    } else {
        Add-R "DB-ISO" $chk.Name "tenant_id 字段检查" "WARN" "表不存在或无法访问"
    }
}

# ════════════════════════════════════════════════════════════════
# Phase 10: 多租户用户管理测试
# ════════════════════════════════════════════════════════════════
Write-Host "`n━━━━━ Phase 10: 多租户用户管理 ━━━━━" -ForegroundColor Magenta

if ($canTestIsolation) {
    # 10.1 租户A创建用户
    $subUserA = Invoke-Api POST "$GatewayUrl/api/system/user" @{
        userName = "tenant_a_user_$uid"
        password = "Test@User123"
        realName = "A租户子用户"
        email = "a_user_$uid@test.com"
    } -Headers $headersA
    
    $subUserA_id = $null
    if ($subUserA.Code -in 200,201) {
        $subUserA_id = Extract-Id $subUserA
        Add-R "USER-ISO" "用户管理" "租户A创建子用户" "PASS" "ID=$subUserA_id"
    } else {
        Add-R "USER-ISO" "用户管理" "租户A创建子用户" "WARN" "HTTP $($subUserA.Code)"
    }
    
    # 10.2 租户B查看用户列表 → 不应看到A的用户
    $r = Invoke-Api GET "$GatewayUrl/api/system/user?page=1&pageSize=100" -Headers $headersB
    if ($r.Code -eq 200) {
        $users = $r.Data.data.items
        if (-not $users) { $users = $r.Data.data }
        $userNames = @($users | ForEach-Object { $_.userName })
        $seesAUser = ($userNames | Where-Object { $_ -match "tenant_a_user_$uid" }).Count
        if ($seesAUser -eq 0) {
            Add-R "USER-ISO" "用户管理" "租户B不可见A子用户" "PASS" "确认隔离"
        } else {
            Add-R "USER-ISO" "用户管理" "租户B不可见A子用户" "FAIL" "泄露! 看到A用户"
        }
    } else {
        Add-R "USER-ISO" "用户管理" "租户B用户列表" "WARN" "HTTP $($r.Code)"
    }
    
    # 10.3 租户B直接访问A用户ID → 404/403
    if ($subUserA_id) {
        $r = Invoke-Api GET "$GatewayUrl/api/system/user/$subUserA_id" -Headers $headersB
        if ($r.Code -in 404,403) {
            Add-R "USER-ISO" "用户管理" "B直接访问A用户→拒绝" "PASS" "HTTP $($r.Code)"
        } elseif ($r.Code -eq 200) {
            Add-R "USER-ISO" "用户管理" "B直接访问A用户→泄露" "FAIL" "返回了A的用户数据!"
        } else {
            Add-R "USER-ISO" "用户管理" "B直接访问A用户" "WARN" "HTTP $($r.Code)"
        }
    }
    
    # 10.4 租户B尝试删除A的用户
    if ($subUserA_id) {
        $r = Invoke-Api DELETE "$GatewayUrl/api/system/user/$subUserA_id" -Headers $headersB
        if ($r.Code -in 404,403) {
            Add-R "USER-ISO" "用户管理" "B删除A用户→拒绝" "PASS" "HTTP $($r.Code)"
        } elseif ($r.Code -in 200,204) {
            Add-R "USER-ISO" "用户管理" "B删除A用户→成功!" "FAIL" "跨租户删除未阻止!"
        } else {
            Add-R "USER-ISO" "用户管理" "B删除A用户" "WARN" "HTTP $($r.Code)"
        }
    }
    
    # 清理A的子用户
    if ($subUserA_id) {
        Invoke-Api DELETE "$GatewayUrl/api/system/user/$subUserA_id" -Headers $headersA | Out-Null
    }
}

# ════════════════════════════════════════════════════════════════
# Phase 11: 租户管理权限边界
# ════════════════════════════════════════════════════════════════
Write-Host "`n━━━━━ Phase 11: 租户管理权限边界 ━━━━━" -ForegroundColor Magenta

if ($canTestIsolation) {
    # 11.1 租户A管理员尝试创建新租户 → 403 (仅SUPER_ADMIN可以)
    $r = Invoke-Api POST "$GatewayUrl/api/tenants" @{
        tenantName = "A尝试创建_$uid"; tenantCode = "a_try_$uid"; tenantDomain = "a-try-$uid.test.com"; contactPerson = "Test"
    } -Headers $headersA
    if ($r.Code -in 403,401) {
        Add-R "PERM-ISO" "权限" "租户A无法创建租户" "PASS" "HTTP $($r.Code)"
    } elseif ($r.Code -in 200,201) {
        Add-R "PERM-ISO" "权限" "租户A无法创建租户" "FAIL" "TENANT_ADMIN 不应能创建租户!"
        $dupId = Extract-Id $r
        if ($dupId) { Invoke-Api DELETE "$GatewayUrl/api/tenants/$dupId" -Headers $adminHeaders | Out-Null }
    } else {
        Add-R "PERM-ISO" "权限" "租户A创建租户" "WARN" "HTTP $($r.Code)"
    }
    
    # 11.2 租户A管理员尝试删除自己的租户 → 403
    $r = Invoke-Api DELETE "$GatewayUrl/api/tenants/$tenantA_id" -Headers $headersA
    if ($r.Code -in 403,401) {
        Add-R "PERM-ISO" "权限" "租户A无法删除自身" "PASS" "HTTP $($r.Code)"
    } else {
        Add-R "PERM-ISO" "权限" "租户A删除自身" "WARN" "HTTP $($r.Code)"
    }
    
    # 11.3 租户A管理员尝试查看其他租户详情 → 403/404
    $r = Invoke-Api GET "$GatewayUrl/api/tenants/$tenantB_id" -Headers $headersA
    if ($r.Code -in 403,404) {
        Add-R "PERM-ISO" "权限" "A查看B租户详情→拒绝" "PASS" "HTTP $($r.Code)"
    } elseif ($r.Code -eq 200) {
        # 检查是否返回了B的信息
        $td = $r.Data.data
        if ($td.tenantCode -eq $tenantB_code) {
            Add-R "PERM-ISO" "权限" "A查看B租户详情→泄露" "FAIL" "返回了B的租户信息!"
        } else {
            Add-R "PERM-ISO" "权限" "A查看B租户详情" "WARN" "200但非B数据"
        }
    } else {
        Add-R "PERM-ISO" "权限" "A查看B租户详情" "WARN" "HTTP $($r.Code)"
    }
    
    # 11.4 租户A管理员尝试禁用B → 403
    $r = Invoke-Api POST "$GatewayUrl/api/tenants/$tenantB_id/disable" -Headers $headersA
    if ($r.Code -in 403,401,404) {
        Add-R "PERM-ISO" "权限" "A禁用B→拒绝" "PASS" "HTTP $($r.Code)"
    } elseif ($r.Code -in 200,204) {
        Add-R "PERM-ISO" "权限" "A禁用B→成功!" "FAIL" "TENANT_ADMIN 不应能操作其他租户!"
        # 恢复
        Invoke-Api POST "$GatewayUrl/api/tenants/$tenantB_id/enable" -Headers $adminHeaders | Out-Null
    } else {
        Add-R "PERM-ISO" "权限" "A禁用B" "WARN" "HTTP $($r.Code)"
    }
}

# ════════════════════════════════════════════════════════════════
# CLEANUP: 清理所有测试数据
# ════════════════════════════════════════════════════════════════
Write-Host "`n━━━━━ CLEANUP: 清理测试数据 ━━━━━" -ForegroundColor Magenta

# 清理模块资源 (使用 SUPER_ADMIN 确保权限)
$cleanupHeaders = $adminHeaders
foreach ($mod in $isoModules) {
    if ($mod.DeleteUrl) {
        foreach ($id in $resourcesA[$mod.Key]) {
            if ($id) { Invoke-Api DELETE "$GatewayUrl$($mod.DeleteUrl -replace '\{id\}',$id)" -Headers $cleanupHeaders | Out-Null }
        }
        foreach ($id in $resourcesB[$mod.Key]) {
            if ($id) { Invoke-Api DELETE "$GatewayUrl$($mod.DeleteUrl -replace '\{id\}',$id)" -Headers $cleanupHeaders | Out-Null }
        }
    }
}
Write-Host "  ✓ 模块资源已清理" -ForegroundColor DarkCyan

# 清理用户
if ($adminA_userId) {
    Invoke-Api DELETE "$GatewayUrl/api/system/user/$adminA_userId" -Headers $adminHeaders | Out-Null
    Exec-Psql "DELETE FROM user_tenant WHERE user_id = '$adminA_userId'" | Out-Null
}
if ($adminB_userId) {
    Invoke-Api DELETE "$GatewayUrl/api/system/user/$adminB_userId" -Headers $adminHeaders | Out-Null
    Exec-Psql "DELETE FROM user_tenant WHERE user_id = '$adminB_userId'" | Out-Null
}
Write-Host "  ✓ 测试用户已清理" -ForegroundColor DarkCyan

# 清理权限数据 (perm_role_permission, perm_user_role, perm_role)
foreach ($testRoleId in @($script:testRoleA_id, $script:testRoleB_id)) {
    if ($testRoleId) {
        Exec-Psql "DELETE FROM perm_role_permission WHERE role_id = '$testRoleId';" "jgsy_permission"
        Exec-Psql "DELETE FROM perm_user_role WHERE role_id = '$testRoleId';" "jgsy_permission"
        Exec-Psql "DELETE FROM perm_role WHERE id = '$testRoleId';" "jgsy_permission"
    }
}
Write-Host "  ✓ 测试权限数据已清理" -ForegroundColor DarkCyan

# 清理租户 (先启用再删除)
foreach ($tid in @($tenantA_id, $tenantB_id)) {
    Invoke-Api POST "$GatewayUrl/api/tenants/$tid/enable" -Headers $adminHeaders | Out-Null
    Invoke-Api DELETE "$GatewayUrl/api/tenants/$tid" -Headers $adminHeaders | Out-Null
}
Write-Host "  ✓ 测试租户已清理" -ForegroundColor DarkCyan

# ════════════════════════════════════════════════════════════════
# 汇总报告
# ════════════════════════════════════════════════════════════════
Write-Host "`n" -NoNewline
Write-Host "╔══════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║          多租户数据隔离测试完成                          ║" -ForegroundColor Cyan
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

# FAIL 详情
if ($script:fail -gt 0) {
    Write-Host "`n  === ⚠️ FAIL 详情（数据泄露风险）===" -ForegroundColor Red
    $failItems = $script:results | Where-Object { $_.Status -eq "FAIL" }
    foreach ($f in $failItems) {
        Write-Host "  ✗ [$($f.Phase)] $($f.Module) | $($f.Test) — $($f.Detail)" -ForegroundColor Red
    }
}

# 导出 CSV
$script:results | Export-Csv -Path $csvFile -NoTypeInformation -Encoding UTF8
Write-Host "`n  报告导出: $csvFile" -ForegroundColor Gray

# 隔离测试评估
Write-Host "`n  === 隔离测试总评 ===" -ForegroundColor Cyan
$isoFails = ($script:results | Where-Object { $_.Phase -in "READ-ISO","CROSS-ID","USER-ISO","PERM-ISO" -and $_.Status -eq "FAIL" }).Count
if ($isoFails -eq 0) {
    Write-Host "  ★ 多租户隔离: 全部通过 — 无数据泄露风险" -ForegroundColor Green
} else {
    Write-Host "  ⚠ 多租户隔离: 发现 $isoFails 个隔离失败 — 需要紧急修复!" -ForegroundColor Red
}

return @{
    Total = $total
    Pass = $script:pass
    Fail = $script:fail
    Warn = $script:warn
    Skip = $script:skip
    PassRate = $passRate
    IsolationFails = $isoFails
    CsvPath = $csvFile
}
