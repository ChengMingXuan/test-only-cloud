<#
.SYNOPSIS
    Layer 5: 安全与鉴权全量测试
.DESCRIPTION
    - 未认证访问测试 (全量受保护端点)
    - Token 伪造/过期测试
    - 内部 API 隔离测试
    - SQL 注入 (8种载荷 × 多端点)
    - XSS 存储型 (6种载荷)
    - 路径遍历 (5种变体)
    - HTTP 方法攻击
    - 超大请求体防御
    - 租户穿透测试
#>
param(
    [string]$GatewayBase = "http://localhost:5000",
    [string]$LogDir = "tests/scripts/logs"
)

$ErrorActionPreference = "Continue"
$ts = Get-Date -Format "yyyyMMdd-HHmmss"
$csvPath = "$LogDir/security-test-$ts.csv"
if (!(Test-Path $LogDir)) { New-Item -ItemType Directory -Path $LogDir -Force | Out-Null }

function Get-Token { 
    $body = '{"userName":"admin","password":"P@ssw0rd"}'
    $resp = Invoke-RestMethod -Uri "$GatewayBase/api/auth/login" -Method POST -Body $body -ContentType "application/json" -TimeoutSec 10
    return $resp.data.accessToken
}

$global:secResults = [System.Collections.Generic.List[pscustomobject]]::new()
$global:sPass = 0; $global:sFail = 0; $global:sWarn = 0

function Add-SecResult($Category, $TestName, $Status, $Detail) {
    $global:secResults.Add([pscustomobject]@{
        Category=$Category; Test=$TestName; Status=$Status; Detail=$Detail; Time=(Get-Date -Format "HH:mm:ss")
    })
    if ($Status -eq "PASS") { $global:sPass++ } elseif ($Status -eq "FAIL") { $global:sFail++ } else { $global:sWarn++ }
    $color = switch($Status) { "PASS" {"Green"} "FAIL" {"Red"} default {"Yellow"} }
    Write-Host "  [$Status] $Category/$TestName : $Detail" -ForegroundColor $color
}

function Invoke-Raw($Method, $Url, $Body, $Headers, $Timeout = 10) {
    $params = @{ Uri=$Url; Method=$Method; UseBasicParsing=$true; TimeoutSec=$Timeout }
    if ($Headers) { $params.Headers = $Headers }
    if ($Body) { $params.Body = $Body; $params.ContentType = "application/json" }
    try {
        $resp = Invoke-WebRequest @params -ErrorAction Stop
        return @{ Code=$resp.StatusCode; Body=$resp.Content; Headers=$resp.Headers }
    } catch {
        $code = 0; if ($_.Exception.Response) { $code = [int]$_.Exception.Response.StatusCode }
        return @{ Code=$code; Error=$_.Exception.Message }
    }
}

$token = Get-Token
$authH = @{ Authorization = "Bearer $token" }

Write-Host "`n========== Layer 5: 安全与鉴权全量测试 ==========" -ForegroundColor Cyan

# ============================================================
# 5.1 未认证访问 - 全量受保护端点
# ============================================================
Write-Host "`n--- 5.1 未认证访问测试 ---" -ForegroundColor Yellow

$protectedEndpoints = @(
    "/api/system/user?page=1&pageSize=5",
    "/api/system/role?page=1&pageSize=5",
    "/api/system/dict/types?page=1&pageSize=5",
    "/api/system/menu/tree",
    "/api/system/announcements?page=1&pageSize=5",
    "/api/department/tree",
    "/api/user/profile",
    "/api/tenants?page=1&pageSize=5",
    "/api/stations?page=1&pageSize=5",
    "/api/device?page=1&pageSize=5",
    "/api/workorder?page=1&pageSize=5",
    "/api/content/articles?page=1&pageSize=5",
    "/api/permissions/statistics/overview?startDate=2026-01-01&endDate=2026-02-18",
    "/api/permissions/temporary/expiring",
    "/api/permissions/statistics/alerts/unhandled-count",
    "/api/system/config",
    "/api/monitor/operation-logs?page=1&pageSize=5",
    "/api/monitor/login-logs?page=1&pageSize=5",
    "/api/charging/admin/orders?page=1&pageSize=5",
    "/api/settlements?page=1&pageSize=5",
    "/api/vpp/dashboard"
)

foreach ($ep in $protectedEndpoints) {
    $r = Invoke-Raw GET "$GatewayBase$ep" $null @{}
    if ($r.Code -eq 401) {
        Add-SecResult "无Token" $ep "PASS" "401 拒绝"
    } elseif ($r.Code -eq 403) {
        Add-SecResult "无Token" $ep "PASS" "403 拒绝"
    } elseif ($r.Code -eq 200) {
        Add-SecResult "无Token" $ep "FAIL" "200 未拦截！"
    } else {
        Add-SecResult "无Token" $ep "WARN" "HTTP $($r.Code)"
    }
}

# ============================================================
# 5.2 伪造 Token
# ============================================================
Write-Host "`n--- 5.2 伪造 Token 测试 ---" -ForegroundColor Yellow

$fakeTokens = @(
    @{Name="随机字符串"; Token="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkhhY2tlciIsImlhdCI6MTUxNjIzOTAyMn0.invalid_signature"},
    @{Name="空Token"; Token=""},
    @{Name="Bearer前缀"; Token="Bearer"},
    @{Name="过期Token"; Token="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwiZXhwIjoxMDAwMDAwMDAwfQ.fake"},
    @{Name="篡改签名"; Token=$token.Substring(0, $token.Length - 5) + "XXXXX"}
)

foreach ($fake in $fakeTokens) {
    $fakeH = @{ Authorization = "Bearer $($fake.Token)" }
    $r = Invoke-Raw GET "$GatewayBase/api/system/user?page=1&pageSize=1" $null $fakeH
    if ($r.Code -eq 401) {
        Add-SecResult "伪造Token" $fake.Name "PASS" "401 拒绝"
    } elseif ($r.Code -eq 200) {
        Add-SecResult "伪造Token" $fake.Name "FAIL" "200 未拦截！"
    } else {
        Add-SecResult "伪造Token" $fake.Name "WARN" "HTTP $($r.Code)"
    }
}

# ============================================================
# 5.3 内部 API 隔离
# ============================================================
Write-Host "`n--- 5.3 内部 API 隔离测试 ---" -ForegroundColor Yellow

$internalPaths = @(
    "/api/internal/identity/users",
    "/api/internal/permission/roles",
    "/api/internal/tenant/tenants",
    "/api/internal/station/stations",
    "/api/internal/device/devices",
    "/api/internal/charging/records",
    "/api/internal/settlement/records",
    "/api/internal/workorder/orders",
    "/api/internal/analytics/data",
    "/api/internal/blockchain/contracts",
    "/api/internal/ingestion/tasks",
    "/api/internal/storage/files"
)

foreach ($ip in $internalPaths) {
    $r = Invoke-Raw GET "$GatewayBase$ip" $null $authH
    if ($r.Code -in 404,403,401,502) {
        Add-SecResult "内部API" $ip "PASS" "HTTP $($r.Code) 不可达"
    } elseif ($r.Code -eq 200) {
        Add-SecResult "内部API" $ip "FAIL" "200 可达！安全风险"
    } else {
        Add-SecResult "内部API" $ip "PASS" "HTTP $($r.Code)"
    }
}

# ============================================================
# 5.4 SQL 注入
# ============================================================
Write-Host "`n--- 5.4 SQL 注入测试 ---" -ForegroundColor Yellow

$sqlPayloads = @(
    "' OR '1'='1",
    "'; DROP TABLE perm_role; --",
    "1 UNION SELECT * FROM pg_shadow --",
    "admin'; DELETE FROM perm_role WHERE '1'='1",
    "' OR 1=1--",
    "1; SELECT pg_sleep(5)--",
    "' AND (SELECT COUNT(*) FROM information_schema.tables)>0--",
    "CAST((SELECT version()) AS TEXT)"
)

$sqlTestEndpoints = @(
    @{Method="GET"; Path="/api/system/role?keyword={PAYLOAD}"},
    @{Method="GET"; Path="/api/system/user?keyword={PAYLOAD}"},
    @{Method="GET"; Path="/api/system/dict/types?keyword={PAYLOAD}"},
    @{Method="GET"; Path="/api/tenants?keyword={PAYLOAD}"},
    @{Method="GET"; Path="/api/stations?keyword={PAYLOAD}"},
    @{Method="GET"; Path="/api/device?keyword={PAYLOAD}"}
)

foreach ($ep in $sqlTestEndpoints) {
    foreach ($payload in $sqlPayloads) {
        $testUrl = "$GatewayBase$($ep.Path -replace '\{PAYLOAD\}', [uri]::EscapeDataString($payload))"
        $r = Invoke-Raw $ep.Method $testUrl $null $authH
        if ($r.Code -ge 500) {
            Add-SecResult "SQL注入" "$($ep.Path.Split('?')[0]) ← $($payload.Substring(0,[Math]::Min(20,$payload.Length)))" "FAIL" "HTTP $($r.Code) 可能存在注入"
        } else {
            Add-SecResult "SQL注入" "$($ep.Path.Split('?')[0]) ← $($payload.Substring(0,[Math]::Min(20,$payload.Length)))" "PASS" "HTTP $($r.Code) 安全"
        }
    }
}

# ============================================================
# 5.5 XSS 存储型
# ============================================================
Write-Host "`n--- 5.5 XSS 存储型测试 ---" -ForegroundColor Yellow

$xssPayloads = @(
    '<script>alert("XSS")</script>',
    '<img src=x onerror=alert(1)>',
    '<svg/onload=alert(document.cookie)>',
    '"><script>alert(1)</script>',
    "javascript:alert('XSS')",
    '<iframe src="javascript:alert(1)"></iframe>'
)

foreach ($xss in $xssPayloads) {
    $shortXss = $xss.Substring(0, [Math]::Min(30, $xss.Length))
    $body = @{roleName=$xss;roleCode="xss_test_$([guid]::NewGuid().ToString().Substring(0,6))";description="XSS测试";status=1}
    $bodyJson = $body | ConvertTo-Json -Compress
    $r = Invoke-Raw POST "$GatewayBase/api/system/role" $bodyJson $authH
    
    if ($r.Code -in 200,201) {
        try {
            $respObj = $r.Body | ConvertFrom-Json
            $roleId = if ($respObj.data.id) { $respObj.data.id } elseif ($respObj.data) { $respObj.data } else { $null }
        } catch { $roleId = $null }
        
        if ($roleId) {
            # 读回检查是否被编码
            $readR = Invoke-Raw GET "$GatewayBase/api/system/role/$roleId" $null $authH
            if ($readR.Code -eq 200 -and $readR.Body -match [regex]::Escape($xss)) {
                Add-SecResult "XSS存储" "$shortXss" "WARN" "原样存储未编码"
            } else {
                Add-SecResult "XSS存储" "$shortXss" "PASS" "已编码或过滤"
            }
            # 清理
            Invoke-Raw DELETE "$GatewayBase/api/system/role/$roleId" $null $authH | Out-Null
        } else {
            Add-SecResult "XSS存储" "$shortXss" "PASS" "创建被拒绝或无ID"
        }
    } elseif ($r.Code -in 400,422) {
        Add-SecResult "XSS存储" "$shortXss" "PASS" "输入验证拒绝 HTTP $($r.Code)"
    } else {
        Add-SecResult "XSS存储" "$shortXss" "PASS" "HTTP $($r.Code)"
    }
}

# ============================================================
# 5.6 路径遍历
# ============================================================
Write-Host "`n--- 5.6 路径遍历测试 ---" -ForegroundColor Yellow

$traversalPaths = @(
    "/api/../../../etc/passwd",
    "/api/..%2F..%2F..%2Fetc%2Fpasswd",
    "/api/storage/files/../../etc/shadow",
    "/api/storage/download?path=../../../etc/passwd",
    "/api/storage/download?path=....//....//etc/passwd",
    "/api/%2e%2e/%2e%2e/%2e%2e/etc/passwd",
    "/api/storage/files/..\\..\\..\\windows\\system32\\config\\sam"
)

foreach ($tp in $traversalPaths) {
    $r = Invoke-Raw GET "$GatewayBase$tp" $null $authH
    if ($r.Code -eq 200 -and $r.Body -match "root:") {
        Add-SecResult "路径遍历" $tp "FAIL" "读取到系统文件！"
    } else {
        Add-SecResult "路径遍历" $tp "PASS" "HTTP $($r.Code)"
    }
}

# ============================================================
# 5.7 HTTP 方法攻击
# ============================================================
Write-Host "`n--- 5.7 HTTP 方法攻击测试 ---" -ForegroundColor Yellow

$attackMethods = @("TRACE", "OPTIONS", "HEAD", "PATCH")
$targetUrl = "$GatewayBase/api/system/role"

foreach ($am in $attackMethods) {
    $r = Invoke-Raw $am $targetUrl $null $authH
    if ($r.Code -in 405,404,401,403) {
        Add-SecResult "HTTP方法" "$am /api/system/role" "PASS" "HTTP $($r.Code) 拒绝"
    } elseif ($r.Code -eq 200) {
        Add-SecResult "HTTP方法" "$am /api/system/role" "WARN" "200 允许（检查是否预期）"
    } else {
        Add-SecResult "HTTP方法" "$am /api/system/role" "PASS" "HTTP $($r.Code)"
    }
}

# ============================================================
# 5.8 超大请求体
# ============================================================
Write-Host "`n--- 5.8 超大请求体测试 ---" -ForegroundColor Yellow

$sizes = @(
    @{Name="100KB";Size=100*1024},
    @{Name="500KB";Size=500*1024},
    @{Name="1MB";Size=1024*1024}
)

foreach ($s in $sizes) {
    $bigBody = '{"data":"' + ("A" * $s.Size) + '"}'
    $r = Invoke-Raw POST "$GatewayBase/api/system/role" $bigBody $authH
    if ($r.Code -in 400,413,422) {
        Add-SecResult "超大请求" $s.Name "PASS" "HTTP $($r.Code) 拒绝"
    } elseif ($r.Code -ge 500) {
        Add-SecResult "超大请求" $s.Name "WARN" "HTTP $($r.Code) 服务端错误"
    } else {
        Add-SecResult "超大请求" $s.Name "WARN" "HTTP $($r.Code)"
    }
}

# ============================================================
# 5.9 租户穿透测试
# ============================================================
Write-Host "`n--- 5.9 租户穿透测试 ---" -ForegroundColor Yellow

# 尝试通过 Header 注入 TenantId
$fakeTenantH = @{
    Authorization = "Bearer $token"
    "X-Tenant-Id" = "00000000-0000-0000-0000-999999999999"
}
$r = Invoke-Raw GET "$GatewayBase/api/system/role?page=1&pageSize=5" $null $fakeTenantH
$rNormal = Invoke-Raw GET "$GatewayBase/api/system/role?page=1&pageSize=5" $null $authH
if ($r.Code -eq 200 -and $rNormal.Code -eq 200) {
    # 比较返回数据部分是否相同（去除 timestamp/traceId 等动态字段）
    try {
        $fakeData = ($r.Body | ConvertFrom-Json).data | ConvertTo-Json -Depth 10 -Compress
        $normalData = ($rNormal.Body | ConvertFrom-Json).data | ConvertTo-Json -Depth 10 -Compress
        if ($fakeData -eq $normalData) {
            Add-SecResult "租户穿透" "Header注入X-Tenant-Id" "PASS" "Header 注入无效"
        } else {
            Add-SecResult "租户穿透" "Header注入X-Tenant-Id" "FAIL" "返回数据不同，可能穿透！"
        }
    } catch {
        # 如果无法解析JSON，直接比较body
        if ($r.Body -eq $rNormal.Body) {
            Add-SecResult "租户穿透" "Header注入X-Tenant-Id" "PASS" "Header 注入无效"
        } else {
            Add-SecResult "租户穿透" "Header注入X-Tenant-Id" "WARN" "响应比较异常"
        }
    }
} else {
    Add-SecResult "租户穿透" "Header注入X-Tenant-Id" "WARN" "状态码不同 fake=$($r.Code) normal=$($rNormal.Code)"
}

# 尝试通过查询参数注入
$r2 = Invoke-Raw GET "$GatewayBase/api/system/role?page=1&pageSize=5&tenantId=00000000-0000-0000-0000-999999999999" $null $authH
if ($r2.Code -eq 200) {
    try {
        $paramData = ($r2.Body | ConvertFrom-Json).data | ConvertTo-Json -Depth 10 -Compress
        $normalData2 = ($rNormal.Body | ConvertFrom-Json).data | ConvertTo-Json -Depth 10 -Compress
        if ($paramData -eq $normalData2) {
            Add-SecResult "租户穿透" "QueryParam注入tenantId" "PASS" "参数注入无效"
        } else {
            Add-SecResult "租户穿透" "QueryParam注入tenantId" "FAIL" "返回数据不同！"
        }
    } catch {
        if ($r2.Body -eq $rNormal.Body) {
            Add-SecResult "租户穿透" "QueryParam注入tenantId" "PASS" "参数注入无效"
        } else {
            Add-SecResult "租户穿透" "QueryParam注入tenantId" "WARN" "响应比较异常"
        }
    }
} else {
    Add-SecResult "租户穿透" "QueryParam注入tenantId" "WARN" "HTTP $($r2.Code)"
}

# ============================================================
# 5.10 错误密码/暴力登录
# ============================================================
Write-Host "`n--- 5.10 暴力登录测试 ---" -ForegroundColor Yellow

# 错误密码
$wrongR = Invoke-Raw POST "$GatewayBase/api/auth/login" '{"userName":"admin","password":"WrongPassword123"}' @{}
if ($wrongR.Code -in 400,401,403) {
    Add-SecResult "暴力登录" "错误密码" "PASS" "HTTP $($wrongR.Code) 拒绝"
} elseif ($wrongR.Code -eq 200) {
    Add-SecResult "暴力登录" "错误密码" "FAIL" "200 接受了错误密码！"
} else {
    Add-SecResult "暴力登录" "错误密码" "WARN" "HTTP $($wrongR.Code)"
}

# 不存在的用户
$noUserR = Invoke-Raw POST "$GatewayBase/api/auth/login" '{"userName":"nonexistent_user","password":"P@ssw0rd"}' @{}
if ($noUserR.Code -in 400,401,403,404) {
    Add-SecResult "暴力登录" "不存在用户" "PASS" "HTTP $($noUserR.Code) 拒绝"
} elseif ($noUserR.Code -eq 200) {
    Add-SecResult "暴力登录" "不存在用户" "FAIL" "200 接受了不存在用户！"
} else {
    Add-SecResult "暴力登录" "不存在用户" "WARN" "HTTP $($noUserR.Code)"
}

# ========== 汇总 ==========
Write-Host "`n========== 安全测试汇总 ==========" -ForegroundColor Cyan
Write-Host "  PASS: $($global:sPass)" -ForegroundColor Green
Write-Host "  FAIL: $($global:sFail)" -ForegroundColor $(if($global:sFail -eq 0){"Green"}else{"Red"})
Write-Host "  WARN: $($global:sWarn)" -ForegroundColor Yellow

$global:secResults | Export-Csv -Path $csvPath -NoTypeInformation -Encoding UTF8
Write-Host "  结果导出: $csvPath"

Write-Host "`n========== Layer 5 完成 ==========" -ForegroundColor Cyan
return @{ Pass=$global:sPass; Fail=$global:sFail; Warn=$global:sWarn; CsvPath=$csvPath }
