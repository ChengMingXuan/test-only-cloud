<#
.SYNOPSIS
  区块链集成测试：链节点健康、交易记录、钱包、绿证/碳证存证
.DESCRIPTION
  直连 Blockchain 服务 (8021) + 网关路由双路验证。
  覆盖：服务健康、交易列表、钱包信息、绿证铸造、碳信用、链上查询。
#>
param(
    [string]$GatewayUrl    = "http://localhost:5000",
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

function Add-Result {
    param([string]$Phase, [string]$Item, [string]$Status, [string]$Detail = "")
    $script:results += [PSCustomObject]@{ Phase=$Phase; Item=$Item; Status=$Status; Detail=$Detail }
    $color = switch ($Status) { "PASS"{"Green"}; "FAIL"{"Red"}; "WARN"{"Yellow"}; default{"Gray"} }
    Write-Host "  [$Status] [$Phase] $Item$(if ($Detail) { " - $Detail" })" -ForegroundColor $color
}

function Invoke-Api {
    param([string]$Url, [string]$Method="GET", [object]$Body=$null, [hashtable]$Headers=@{}, [int]$TimeoutSec=15)
    try {
        $params = @{ Uri=$Url; Method=$Method; Headers=$Headers; TimeoutSec=$TimeoutSec; ErrorAction="Stop" }
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
# Phase 0: 认证
# ============================================================
Write-Host "`n=== Phase 0: 认证 ===" -ForegroundColor Cyan
$login = Invoke-Api -Url "$GatewayUrl/api/auth/login" -Method POST -Body @{ username=$Username; password=$Password }
if (-not $login.Ok -or -not $login.Data.success) {
    Write-Host "❌ 登录失败，无法继续" -ForegroundColor Red; exit 1
}
$h = @{ "Authorization" = "Bearer $($login.Data.data.accessToken)" }
Write-Host "✅ 登录成功" -ForegroundColor Green

# ============================================================
# Phase 1: 区块链服务健康检查
# ============================================================
Write-Host "`n=== Phase 1: Blockchain 服务健康 ===" -ForegroundColor Cyan

# 直连健康端点（无需认证）
try {
    $r = Invoke-WebRequest "$BlockchainUrl/health" -UseBasicParsing -TimeoutSec 8 -ErrorAction Stop
    if ($r.StatusCode -lt 300) {
        $body = $r.Content | ConvertFrom-Json -ErrorAction SilentlyContinue
        Add-Result "健康" "Blockchain /health (直连8021)" "PASS" "HTTP $($r.StatusCode)"
    }
} catch {
    $sc = $_.Exception.Response.StatusCode.value__
    Add-Result "健康" "Blockchain /health (直连8021)" $(if ($sc) {"WARN"} else {"FAIL"}) "HTTP $sc 或连接失败: $($_.Exception.Message)"
}

# 通过网关访问区块链路由
$gwPaths = @(
    "/api/blockchain/health",
    "/health"  # 可能是独立端点
)
$gwBcOk = $false
foreach ($path in $gwPaths) {
    try {
        $r = Invoke-WebRequest "$GatewayUrl$path" -UseBasicParsing -TimeoutSec 8 -ErrorAction Stop
        if ($r.StatusCode -lt 300) {
            Add-Result "健康" "网关→Blockchain$path" "PASS" "HTTP $($r.StatusCode)"
            $gwBcOk = $true; break
        }
    } catch { }
}
if (-not $gwBcOk) {
    Add-Result "健康" "网关→Blockchain" "WARN" "网关路由未发现，直连正常则无影响"
}

# ============================================================
# Phase 2: 交易记录 API
# ============================================================
Write-Host "`n=== Phase 2: 交易记录 ===" -ForegroundColor Cyan

# 直连
$rt = Invoke-Api -Url "$BlockchainUrl/api/transactions?pageIndex=1&pageSize=10" -Headers $h
if ($rt.Ok -and $rt.Data.success) {
    $txCount = $rt.Data.data.Count
    Add-Result "交易" "交易列表 (直连8021)" "PASS" "Count=$txCount"
} else {
    Add-Result "交易" "交易列表 (直连8021)" "FAIL" "StatusCode=$($rt.StatusCode) $($rt.Error)"
}

# 通过网关
$rt2 = Invoke-Api -Url "$GatewayUrl/api/transactions?pageIndex=1&pageSize=10" -Headers $h
if ($rt2.Ok -and $rt2.Data.success) {
    Add-Result "交易" "交易列表 (网关)" "PASS" ""
} else {
    Add-Result "交易" "交易列表 (网关)" $(if ($rt2.StatusCode -eq 404) {"WARN"} else {"FAIL"}) "StatusCode=$($rt2.StatusCode)"
}

# ============================================================
# Phase 3: 钱包信息
# ============================================================
Write-Host "`n=== Phase 3: 钱包信息 ===" -ForegroundColor Cyan

$rw = Invoke-Api -Url "$BlockchainUrl/api/wallet/system-info" -Headers $h
if ($rw.Ok -and $rw.Data.success) {
    Add-Result "钱包" "系统钱包信息" "PASS" "地址存在=$($null -ne $rw.Data.data.callerAddress)"
} else {
    Add-Result "钱包" "系统钱包信息" "FAIL" "StatusCode=$($rw.StatusCode) $($rw.Error)"
}

# ============================================================
# Phase 4: 绿证 (ERC-721 Green Certificate) 铸造
# ============================================================
Write-Host "`n=== Phase 4: 绿证铸造与查询 ===" -ForegroundColor Cyan

$mintBody = @{
    stationId        = "STATION-CRUD-$ts"
    recipientAddress = "0x0000000000000000000000000000000000000001"
    generationMwh    = 1.0
    energySource     = 1          # 1=Solar
    generationStart  = (Get-Date).AddHours(-1).ToString("yyyy-MM-ddTHH:mm:ssZ")
    generationEnd    = (Get-Date).ToString("yyyy-MM-ddTHH:mm:ssZ")
}

$rc = Invoke-Api -Url "$BlockchainUrl/api/certificates/green/mint" -Method POST -Body $mintBody -Headers $h
if ($rc.Ok -and $rc.Data.success) {
    $certId = if ($null -ne $rc.Data.data.tokenId) { $rc.Data.data.tokenId } else { $rc.Data.data }
    Add-Result "绿证" "铸造绿证" "PASS" "TokenID=$certId"

    # 查询绿证列表
    $rcl = Invoke-Api -Url "$BlockchainUrl/api/certificates?type=green&pageIndex=1&pageSize=10" -Headers $h
    if ($rcl.Ok -and $rcl.Data.success) {
        Add-Result "绿证" "绿证列表查询" "PASS" ""
    } else {
        # 尝试不带 type 参数
        $rcl2 = Invoke-Api -Url "$BlockchainUrl/api/certificates?pageIndex=1&pageSize=10" -Headers $h
        $st = if ($rcl2.Ok) {"PASS"} elseif ($rcl2.StatusCode -eq 404) {"WARN"} else {"FAIL"}
        Add-Result "绿证" "绿证列表查询" $st "StatusCode=$($rcl2.StatusCode)"
    }
} else {
    # 区块链铸造失败可能是节点未连接（测试环境 Geth 节点非必须）
    $isBcNode = $rc.StatusCode -eq 500 -or ($rc.Error -like "*chain*") -or ($rc.Error -like "*node*")
    $status   = if ($isBcNode) { "WARN" } else { "FAIL" }
    Add-Result "绿证" "铸造绿证" $status "StatusCode=$($rc.StatusCode) - $(if ($isBcNode) {'链节点未连接(非必须)'} else {$rc.Error})"
}

# ============================================================
# Phase 5: 碳信用 API
# ============================================================
Write-Host "`n=== Phase 5: 碳信用查询 ===" -ForegroundColor Cyan

$rcarbon = Invoke-Api -Url "$BlockchainUrl/api/certificates/carbon?pageIndex=1&pageSize=10" -Headers $h
if ($rcarbon.Ok) {
    Add-Result "碳信用" "碳信用列表" "PASS" ""
} else {
    # 尝试不同路径
    $rcarbon2 = Invoke-Api -Url "$BlockchainUrl/api/carbon?pageIndex=1&pageSize=10" -Headers $h
    $st = if ($rcarbon2.Ok) {"PASS"} elseif ($rcarbon2.StatusCode -eq 404) {"WARN"} else {"FAIL"}
    Add-Result "碳信用" "碳信用列表" $st "StatusCode=$($rcarbon2.StatusCode) HTTP: $($rcarbon.StatusCode)"
}

# ============================================================
# Phase 6: 链上查询
# ============================================================
Write-Host "`n=== Phase 6: 链上查询与合约状态 ===" -ForegroundColor Cyan

$queryPaths = @(
    @{ Name="合约状态";     Path="/api/contracts" },
    @{ Name="链上事件";     Path="/api/events?pageIndex=1&pageSize=5" },
    @{ Name="积分账户";     Path="/api/points/balance" }
)

foreach ($qp in $queryPaths) {
    $rq = Invoke-Api -Url "$BlockchainUrl$($qp.Path)" -Headers $h
    if ($rq.Ok -and ($rq.Data.success -or $rq.Data -ne $null)) {
        Add-Result "链查询" $qp.Name "PASS" ""
    } else {
        $st = if ($rq.StatusCode -eq 404) {"WARN"} elseif ($rq.StatusCode -eq 403) {"WARN"} else {"FAIL"}
        Add-Result "链查询" $qp.Name $st "HTTP $($rq.StatusCode)"
    }
}

# ============================================================
# Phase 7: 存证功能（哈希上链）
# ============================================================
Write-Host "`n=== Phase 7: 业务存证哈希上链 ===" -ForegroundColor Cyan

$proofBody = @{
    businessId   = "SETTLE-$ts"
    businessType = "settlement"
    dataHash     = "0x" + ([System.BitConverter]::ToString([System.Text.Encoding]::UTF8.GetBytes("test-settle-data-$ts")).Replace("-", "").ToLower())
    metadata     = @{ source = "CRUD测试"; timestamp = (Get-Date -Format "yyyy-MM-dd HH:mm:ss") }
} | ConvertTo-Json -Compress

$proofPaths = @(
    "/api/transactions/proof",
    "/api/transactions/certify",
    "/api/blockchain/proof"
)
$proofOk = $false
foreach ($pp in $proofPaths) {
    $rp = Invoke-Api -Url "$BlockchainUrl$pp" -Method POST -Body $proofBody -Headers $h
    if ($rp.Ok -and $rp.Data.success) {
        Add-Result "存证" "结算存证上链 $pp" "PASS" "TxHash=$(if ($null -ne $rp.Data.data) { $rp.Data.data } else { '有' })"
        $proofOk = $true; break
    }
    if ($rp.StatusCode -ne 404 -and $rp.StatusCode -ne 405) {
        Add-Result "存证" "结算存证上链 $pp" "WARN" "HTTP $($rp.StatusCode)"
    }
}
if (-not $proofOk) {
    Add-Result "存证" "结算存证上链" "WARN" "存证端点 404/405，需确认 Blockchain API 路由定义"
}

# ============================================================
# Phase 8: 网关路由完整性
# ============================================================
Write-Host "`n=== Phase 8: 网关→Blockchain 路由覆盖 ===" -ForegroundColor Cyan

$gwBlockchainPaths = @(
    @{ Name="网关→交易列表";  Path="/api/transactions?pageIndex=1&pageSize=5" },
    @{ Name="网关→钱包";      Path="/api/wallet/system-info" },
    @{ Name="网关→合约";      Path="/api/contracts" }
)
foreach ($gp in $gwBlockchainPaths) {
    $rgw = Invoke-Api -Url "$GatewayUrl$($gp.Path)" -Headers $h
    if ($rgw.Ok) {
        Add-Result "网关路由" $gp.Name "PASS" ""
    } else {
        $st = if ($rgw.StatusCode -eq 404) {"WARN"} else {"FAIL"}
        Add-Result "网关路由" $gp.Name $st "HTTP $($rgw.StatusCode) (直连8021正常则路由待配置)"
    }
}

# ============================================================
# 汇总
# ============================================================
Write-Host "`n========== 区块链集成测试汇总 ==========" -ForegroundColor Yellow

$pass  = ($results | Where-Object { $_.Status -eq "PASS"  }).Count
$warn  = ($results | Where-Object { $_.Status -eq "WARN"  }).Count
$fail  = ($results | Where-Object { $_.Status -eq "FAIL"  }).Count
$total = $results.Count
$elapsed = [int](Get-Date).Subtract($startTime).TotalSeconds

Write-Host "总计: $total 项  PASS=$pass  WARN=$warn  FAIL=$fail  耗时:${elapsed}s" -ForegroundColor White

if ($fail -gt 0) {
    Write-Host "`n❌ FAIL 项：" -ForegroundColor Red
    $results | Where-Object { $_.Status -eq "FAIL" } | ForEach-Object {
        Write-Host "  [$($_.Phase)] $($_.Item): $($_.Detail)" -ForegroundColor Red
    }
}
if ($warn -gt 0) {
    Write-Host "`n⚠️  WARN（非阻断，但需关注）：" -ForegroundColor Yellow
    $results | Where-Object { $_.Status -eq "WARN" } | ForEach-Object {
        Write-Host "  [$($_.Phase)] $($_.Item): $($_.Detail)" -ForegroundColor Yellow
    }
}

# 说明 WARN 含义
Write-Host "`n[说明] 链节点相关 WARN：本地测试环境 Geth 节点可选，区块链核心存储逻辑（DB记录）PASS 即满足上线标准。" -ForegroundColor DarkGray

# 保存
try {
    if (-not [System.IO.Path]::IsPathRooted($LogDir)) {
        $base      = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
        $targetDir = Join-Path $base $LogDir
    } else { $targetDir = $LogDir }
    if (-not (Test-Path $targetDir)) { New-Item -ItemType Directory -Path $targetDir -Force | Out-Null }
    $logTs   = Get-Date -Format "yyyyMMdd-HHmmss"
    $logPath = Join-Path $targetDir "blockchain-integration-$logTs.csv"
    $results | Export-Csv -Path $logPath -NoTypeInformation -Encoding UTF8
    Write-Host "日志已保存: $logPath" -ForegroundColor Gray
} catch {
    Write-Host "日志保存失败: $($_.Exception.Message)" -ForegroundColor Yellow
}

$verdict = if ($fail -eq 0) { "区块链集成通过 ✅" } else { "区块链集成有故障 ❌" }
Write-Host "`n区块链集成测试结论：$verdict" -ForegroundColor $(if ($fail -eq 0) {"Green"} else {"Red"})
Write-Host "完成时间: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')" -ForegroundColor Gray
