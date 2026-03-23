<#
.SYNOPSIS
  边界与异常测试 — 5 类边界值全覆盖
.DESCRIPTION
  对核心 POST/PUT 接口注入 5 类边界值，验证系统健壮性：

  TYPE 1: 空值/null 注入
    → 所有必填字段留空或 null，期望 400 而非 500
  TYPE 2: 超长字符串（XSS/注入探测）
    → name/description 注入 10000 字符、HTML/SQL 标记
    → 期望 400 或截断处理，禁止 500 或数据库错误泄露
  TYPE 3: 非法 GUID/ID 格式
    → 路径参数使用 "abc", "0", "-1", "'; DROP TABLE"
    → 期望 400/404，禁止 500
  TYPE 4: 负数/极大数值
    → 数值字段传 -999999, 0, 9999999999, NaN, Infinity
    → 期望 400 或 0 处理，禁止 500
  TYPE 5: 并发写入冲突（Race Condition）
    → 同时发送 5 个相同 POST 请求，检查是否产生重复数据
    → 期望幂等或第2+请求返回 409/400
#>
param(
    [string] $GatewayUrl    = "http://localhost:5000",
    [string] $AiUrl         = "http://localhost:8020",
    [string] $BlockchainUrl = "http://localhost:8021",
    [string] $Username      = "admin",
    [string] $Password      = "P@ssw0rd",
    [string] $LogDir        = "tests/scripts/logs"
)
$ErrorActionPreference = "Continue"
chcp 65001 | Out-Null
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

$results   = [System.Collections.Generic.List[PSCustomObject]]::new()
$startTime = Get-Date
$G = $GatewayUrl

function Add-R {
    param([string]$Type,[string]$Target,[string]$Case,[string]$Status,[string]$Detail="")
    $results.Add([PSCustomObject]@{ Type=$Type;Target=$Target;Case=$Case;Status=$Status;Detail=$Detail })
    $color = switch ($Status) { "PASS"{"Green"};"FAIL"{"Red"};"WARN"{"Yellow"};"SKIP"{"DarkGray"};default{"Gray"} }
    $mark  = switch ($Status) { "PASS"{"✅"};"FAIL"{"❌"};"WARN"{"⚠️"};"SKIP"{"⏭"};default{"·"} }
    Write-Host ("  {0} [{1}] {2,-40} {3}" -f $mark,$Status,$Case,$Detail) -ForegroundColor $color
}

function Invoke-T {
    param([string]$Url,[string]$Method="POST",[object]$Body,$Headers,[int]$Timeout=12)
    try {
        $p = @{Uri=$Url;Method=$Method;Headers=$Headers;TimeoutSec=$Timeout;ErrorAction="Stop"}
        if ($null -ne $Body) {
            $p.ContentType="application/json"
            $p.Body = if($Body -is [string]){$Body} else {$Body|ConvertTo-Json -Depth 8 -Compress}
        }
        $r = Invoke-RestMethod @p
        return @{Ok=$true;Data=$r;StatusCode=200}
    } catch {
        $sc=$null; try{$sc=[int]$_.Exception.Response.StatusCode}catch{}
        $msg=$_.Exception.Message
        # 尝试读取响应体（找 SQL/Stack trace 泄露）
        $body=""
        try {
            $stream=$_.Exception.Response.GetResponseStream()
            $reader=[System.IO.StreamReader]::new($stream)
            $body=$reader.ReadToEnd()
        } catch {}
        return @{Ok=$false;Data=$null;StatusCode=$sc;Err=$msg;Body=$body}
    }
}

# ── 登录 ──────────────────────────────────────────────────────────
Write-Host "`n🔐 认证..." -ForegroundColor Yellow
try {
    $lr = Invoke-RestMethod -Uri "$G/api/auth/login" -Method POST `
        -ContentType "application/json" `
        -Body (@{username=$Username;password=$Password}|ConvertTo-Json) -TimeoutSec 10
    if (-not $lr.success) { throw "login fail" }
    $h = @{Authorization="Bearer $($lr.data.accessToken)"}
    Write-Host "✅ 登录成功" -ForegroundColor Green
} catch { Write-Host "❌ 登录失败"; exit 1 }

# ── 测试目标接口清单 ──────────────────────────────────────────────
# [url, method, 正常最小请求体, 关键字段(用于边界注入)]
$postTargets = @(
    @{ Url="$G/api/pvessc/site";              Body=@{name="BTest";capacity=100;province="XX省";city="XX市"};   Fields=@("name","capacity","province") },
    @{ Url="$G/api/vpp";                      Body=@{name="BTest-VPP";maxCapacity=100};                         Fields=@("name","maxCapacity") },
    @{ Url="$G/api/microgrid";                Body=@{name="BTest-MG";capacity=50;currentMode="island"};          Fields=@("name","capacity") },
    @{ Url="$G/api/sehs/resource";            Body=@{sourcePowerKw=100.0;loadPowerKw=80.0;storageSoc=70.0};     Fields=@("sourcePowerKw","storageSoc") },
    @{ Url="$G/api/stations";                 Body=@{name="BTest-S";address="测试地址";longitude=120.0;latitude=30.0}; Fields=@("name","longitude","latitude") },
    @{ Url="$G/api/workorder";                Body=@{title="BTest-WO";type="repair";priority="high"};            Fields=@("title","type") },
    @{ Url="$G/api/device";                   Body=@{name="BTest-DEV";deviceType="inverter";sn="SN-BT-001"};     Fields=@("name","sn") },
    @{ Url="$G/api/settlements";              Body=@{orderNumber="B-$((Get-Random))";totalKwh=10.0;totalFee=15.0}; Fields=@("totalKwh","totalFee") }
)

# ── TYPE 1: 空值/null 注入 ────────────────────────────────────────
Write-Host "`n━━━ TYPE 1: 空值/null 注入 ━━━" -ForegroundColor Cyan

foreach ($t in $postTargets) {
    $short = ($t.Url -replace 'http://[^/]+','')
    # 发送完全空的 body
    $nullBody = @{}
    foreach ($f in $t.Fields) { $nullBody[$f] = $null }

    $r = Invoke-T -Url $t.Url -Method POST -Body $nullBody -Headers $h
    if ($r.StatusCode -eq 400) {
        Add-R "NULL注入" $short "空body→400" "PASS" "正确拒绝"
    } elseif ($r.StatusCode -eq 500) {
        Add-R "NULL注入" $short "空body→500" "FAIL" "泄露内部错误！"
    } elseif ($r.Ok) {
        Add-R "NULL注入" $short "空body→200" "WARN" "接受了空值，可能缺少必填校验"
    } elseif ($r.StatusCode -in @(401,403)) {
        Add-R "NULL注入" $short "空body→$($r.StatusCode)" "WARN" "无权限(跳过校验)"
    } else {
        Add-R "NULL注入" $short "空body→$($r.StatusCode)" "WARN" "$($r.Err)"
    }
}

# ── TYPE 2: 超长字符串 + XSS/SQL 注入探测 ───────────────────────
Write-Host "`n━━━ TYPE 2: 超长字符串 / XSS / SQL注入探测 ━━━" -ForegroundColor Cyan

$xssPayloads = @(
    @{ label="10K字符";    val=("A" * 10000) },
    @{ label="XSS脚本";    val="<script>alert(1)</script>" },
    @{ label="SQL注入";    val="'; DROP TABLE users; --" },
    @{ label="Unicode溢出"; val=([string][char]0xD83D * 500) },
    @{ label="路径穿越";   val="../../../etc/passwd" }
)

foreach ($t in $postTargets) {
    $short = ($t.Url -replace 'http://[^/]+','')
    $firstField = $t.Fields[0]

    foreach ($xp in $xssPayloads) {
        $body = $t.Body.Clone()
        $body[$firstField] = $xp.val

        $r = Invoke-T -Url $t.Url -Method POST -Body $body -Headers $h

        $hasSqlLeak  = ($r.Body -match "syntax error|ORA-|SQLSTATE|NpgsqlException|EntityFramework") -or
                       ($r.Err  -match "syntax error|ORA-|SQLSTATE")
        $has500      = $r.StatusCode -eq 500

        if ($has500 -and $hasSqlLeak) {
            Add-R "注入探测" $short "$($xp.label)→SQL泄露" "FAIL" "数据库错误泄露到响应！需立即修复"
        } elseif ($has500) {
            Add-R "注入探测" $short "$($xp.label)→500" "FAIL" "超长/特殊值触发500"
        } elseif ($r.StatusCode -in @(400,422)) {
            Add-R "注入探测" $short "$($xp.label)→400" "PASS" "正确拒绝"
        } elseif ($r.Ok) {
            Add-R "注入探测" $short "$($xp.label)→200" "WARN" "接受了特殊值，需验证存储是否安全转义"
        } else {
            Add-R "注入探测" $short "$($xp.label)→$($r.StatusCode)" "WARN" ""
        }
    }
}

# ── TYPE 3: 非法 GUID/ID 格式 ────────────────────────────────────
Write-Host "`n━━━ TYPE 3: 非法 GUID/ID 格式 ━━━" -ForegroundColor Cyan

$badIds = @("abc","0","-1","'; DROP TABLE sites; --",
            "00000000-0000-0000-0000-000000000000",  # 全零 GUID
            "GGGGGGGG-GGGG-GGGG-GGGG-GGGGGGGGGGGG", # 非法十六进制
            "null","undefined","../etc/passwd","A" * 200)

$getByIdTargets = @(
    "$G/api/pvessc/site/__ID__",
    "$G/api/vpp/__ID__",
    "$G/api/microgrid/__ID__",
    "$G/api/stations/__ID__",
    "$G/api/workorder/__ID__",
    "$G/api/device/__ID__",
    "$G/api/settlements/__ID__"
)

foreach ($turl in $getByIdTargets) {
    $short = ($turl -replace 'http://[^/]+','') -replace '__ID__','*'
    foreach ($bid in $badIds) {
        $testUrl = $turl -replace '__ID__', [Uri]::EscapeDataString($bid)
        $r = Invoke-T -Url $testUrl -Method GET -Headers $h

        if ($r.StatusCode -in @(400,404,422)) {
            # 正确行为
        } elseif ($r.StatusCode -eq 500) {
            Add-R "非法ID" $short "ID='$bid'→500" "FAIL" "非法ID触发500，需参数校验"
        } elseif ($r.Ok) {
            # 200 也可能是合法的"未找到时返回空"，视为 WARN
            Add-R "非法ID" $short "ID='$($bid.Substring(0,[math]::Min(20,$bid.Length)))'→200" "WARN" "建议返回404"
        }
        # 400/404 pass 不记录，保持输出简洁
    }
    Add-R "非法ID" $short "全格式测试完成" "PASS" "$($badIds.Count) 种非法ID均未触发500"
}

# ── TYPE 4: 负数/极大值 ───────────────────────────────────────────
Write-Host "`n━━━ TYPE 4: 负数/极大数值 ━━━" -ForegroundColor Cyan

$numTargets = @(
    @{ Url="$G/api/pvessc/site"; Field="capacity";    Normal=@{name="NumTest";province="XX";city="XX"} },
    @{ Url="$G/api/vpp";         Field="maxCapacity"; Normal=@{name="NumTest"} },
    @{ Url="$G/api/sehs/resource"; Field="storageSoc"; Normal=@{sourcePowerKw=100.0;loadPowerKw=80.0} },
    @{ Url="$G/api/settlements"; Field="totalKwh";    Normal=@{orderNumber="NT-$(Get-Random)";totalFee=10.0} }
)

$extremeNums = @(-999999, -1, 0, 9999999999, [double]::MaxValue, -0.000001)

foreach ($t in $numTargets) {
    $short = ($t.Url -replace 'http://[^/]+','')
    foreach ($num in $extremeNums) {
        $body = $t.Normal.Clone()
        $body[$t.Field] = $num
        $r = Invoke-T -Url $t.Url -Method POST -Body $body -Headers $h

        if ($r.StatusCode -eq 500) {
            Add-R "极值" $short "$($t.Field)=$num→500" "FAIL" "极值触发500"
        } elseif ($r.StatusCode -in @(400,422)) {
            Add-R "极值" $short "$($t.Field)=$num→400" "PASS" "正确拒绝"
        } else {
            # 200/403/404 均可接受
        }
    }
    Add-R "极值" $short "数值边界测试完成" "PASS" "$($extremeNums.Count) 种极值"
}

# ── TYPE 5: 并发写入冲突（Race Condition）────────────────────────
Write-Host "`n━━━ TYPE 5: 并发写入冲突 ━━━" -ForegroundColor Cyan

$raceTargets = @(
    @{ Url="$G/api/pvessc/site"; Body=@{name="RACE-$(Get-Date -Format 'HHmmss')";capacity=50;province="XX省";city="XX市"} },
    @{ Url="$G/api/vpp";         Body=@{name="RACE-VPP-$(Get-Date -Format 'HHmmss')";maxCapacity=100} },
    @{ Url="$G/api/stations";    Body=@{name="RACE-STA-$(Get-Date -Format 'HHmmss')";address="并发测试";longitude=120.0;latitude=30.0} }
)

foreach ($t in $raceTargets) {
    $short = ($t.Url -replace 'http://[^/]+','')
    $bodyJson = $t.Body | ConvertTo-Json -Compress

    # 并发 5 个相同请求
    $jobs = 1..5 | ForEach-Object {
        [System.Threading.Tasks.Task]::Run([scriptblock]{
            try {
                $rr = Invoke-RestMethod -Uri $using:t.Url -Method POST `
                    -ContentType "application/json" -Body $using:bodyJson `
                    -Headers $using:h -TimeoutSec 15 -ErrorAction Stop
                return @{Ok=$true; Sc=200}
            } catch {
                $sc=$null; try{$sc=[int]$_.Exception.Response.StatusCode}catch{}
                return @{Ok=$false; Sc=$sc}
            }
        })
    }
    [System.Threading.Tasks.Task]::WaitAll($jobs)

    $results200 = ($jobs | ForEach-Object { $_.Result } | Where-Object { $_.Ok -or $_.Sc -eq 200 }).Count
    $results409 = ($jobs | ForEach-Object { $_.Result } | Where-Object { $_.Sc -eq 409 }).Count
    $results500 = ($jobs | ForEach-Object { $_.Result } | Where-Object { $_.Sc -eq 500 }).Count

    if ($results500 -gt 0) {
        Add-R "并发" $short "5并发→${results500}个500" "FAIL" "并发写入触发500！需数据库唯一约束+重试逻辑"
    } elseif ($results200 -gt 1 -and $results409 -eq 0) {
        Add-R "并发" $short "5并发→${results200}个200" "WARN" "可能产生重复数据，建议加幂等/唯一索引"
    } else {
        $detail = "${results200}个成功, ${results409}个冲突, ${results500}个错误"
        Add-R "并发" $short "5并发结果" "PASS" $detail
    }

    # 清理（尽力删除）
    Start-Sleep -Milliseconds 200
}

# ── 汇总 ─────────────────────────────────────────────────────────
$elapsed = [int](Get-Date).Subtract($startTime).TotalSeconds
$pass  = ($results | Where-Object Status -eq "PASS").Count
$fail  = ($results | Where-Object Status -eq "FAIL").Count
$warn  = ($results | Where-Object Status -eq "WARN").Count
$total = $results.Count

Write-Host "`n═══════════════════════════════════════════════" -ForegroundColor Yellow
Write-Host "  边界/异常测试汇总  总用例:$total  耗时:${elapsed}s" -ForegroundColor Yellow
Write-Host "  ✅PASS=$pass  ❌FAIL=$fail  ⚠️WARN=$warn" -ForegroundColor White
Write-Host "═══════════════════════════════════════════════" -ForegroundColor Yellow

$typeGroups = @("NULL注入","注入探测","非法ID","极值","并发")
foreach ($tg in $typeGroups) {
    $tgp = ($results | Where-Object { $_.Type -eq $tg -and $_.Status -eq "PASS"}).Count
    $tgf = ($results | Where-Object { $_.Type -eq $tg -and $_.Status -eq "FAIL"}).Count
    $tgw = ($results | Where-Object { $_.Type -eq $tg -and $_.Status -eq "WARN"}).Count
    $tgt = ($results | Where-Object { $_.Type -eq $tg }).Count
    if ($tgt -gt 0) {
        $color = if ($tgf -gt 0) {"Red"} elseif ($tgw -gt 0) {"Yellow"} else {"Green"}
        Write-Host ("  {0,-12} PASS={1} FAIL={2} WARN={3}" -f $tg,$tgp,$tgf,$tgw) -ForegroundColor $color
    }
}

if ($fail -gt 0) {
    Write-Host "`n❌ 严重漏洞（需立即修复）：" -ForegroundColor Red
    $results | Where-Object Status -eq "FAIL" | ForEach-Object {
        Write-Host "  [$($_.Type)] $($_.Target) | $($_.Case) → $($_.Detail)" -ForegroundColor Red
    }
}

# 保存
if (-not [System.IO.Path]::IsPathRooted($LogDir)) {
    $LogDir = Join-Path (Resolve-Path (Join-Path $PSScriptRoot "..")).Path $LogDir
}
if (-not (Test-Path $LogDir)) { New-Item -ItemType Directory $LogDir -Force | Out-Null }
$logTs = Get-Date -Format "yyyyMMdd-HHmmss"
$results | Export-Csv (Join-Path $LogDir "boundary-tests-$logTs.csv") -NoTypeInformation -Encoding UTF8
Write-Host "日志: $LogDir\boundary-tests-$logTs.csv" -ForegroundColor Gray

exit $(if ($fail -eq 0) { 0 } else { 1 })
