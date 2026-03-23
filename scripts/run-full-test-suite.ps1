<#
.SYNOPSIS
  全量测试套件总入口
.DESCRIPTION
  按序运行所有测试脚本，聚合结果生成 Markdown 报告：
    1. 上线门禁 (go-live-gate)
    2. 四子系统功能测试 (test-four-subsystems)
    3. 实时数据流测试 (test-realtime-data-flow)
    4. 能源 CRUD 测试 (test-energy-crud)
    5. 区块链集成测试 (test-blockchain-integration)
    6. 端到端业务全链路 (test-e2e-business-flow)

  可选：之后调用 k6 做负载测试。
.PARAMETER SkipGate
  跳过上线门禁（开发调试时使用）
.PARAMETER SkipCrud
  跳过写操作测试（只读环境）
.PARAMETER WithLoadTest
  额外运行 k6 负载测试（需已安装 k6.exe）
.PARAMETER GatewayUrl
  网关地址，默认 http://localhost:5000
.PARAMETER AiUrl
  IotCloudAI 地址，默认 http://localhost:8020
.PARAMETER BlockchainUrl
  区块链服务地址，默认 http://localhost:8021
.PARAMETER Username
  登录用户名，默认 admin
.PARAMETER Password
  登录密码，默认 P@ssw0rd
.EXAMPLE
  # 全量运行
  .\scripts\run-full-test-suite.ps1

  # 跳过门禁 + 负载测试
  .\scripts\run-full-test-suite.ps1 -SkipGate -WithLoadTest
#>
param(
    [switch] $SkipGate,
    [switch] $SkipCrud,
    [switch] $WithLoadTest,
    [string] $GatewayUrl    = "http://localhost:5000",
    [string] $AiUrl         = "http://localhost:8020",
    [string] $BlockchainUrl = "http://localhost:8021",
    [string] $Username      = "admin",
    [string] $Password      = "P@ssw0rd",
    [string] $LogDir        = "scripts/logs"
)

$ErrorActionPreference = "Continue"
chcp 65001 | Out-Null
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

$scriptDir  = $PSScriptRoot
$suiteStart = Get-Date

# ──────────────────────────────────────────────────────────
# 工具函数
# ──────────────────────────────────────────────────────────
function Write-Banner {
    param([string]$Title, [string]$Color = "Cyan")
    Write-Host ""
    Write-Host ("=" * 60) -ForegroundColor $Color
    Write-Host "  $Title" -ForegroundColor $Color
    Write-Host ("=" * 60) -ForegroundColor $Color
}

function Invoke-Suite {
    param([string]$Label, [string]$ScriptPath, [string[]]$ExtraArgs = @())

    $displayPath = Split-Path $ScriptPath -Leaf
    Write-Banner "[$Label] $displayPath"

    if (-not (Test-Path $ScriptPath)) {
        Write-Host "  ⚠️  脚本不存在，跳过: $ScriptPath" -ForegroundColor Yellow
        return @{ Label=$Label; Script=$displayPath; ExitCode=-1; Status="SKIP"; DurationSec=0 }
    }

    $start   = Get-Date
    $baseArgs = @(
        "-GatewayUrl", $GatewayUrl,
        "-Username",   $Username,
        "-Password",   $Password,
        "-LogDir",     $LogDir
    )
    # 按脚本支持的参数动态加
    $scriptContent = Get-Content $ScriptPath -Raw
    if ($scriptContent -match '\$AiUrl')         { $baseArgs += @("-AiUrl", $AiUrl) }
    if ($scriptContent -match '\$BlockchainUrl') { $baseArgs += @("-BlockchainUrl", $BlockchainUrl) }

    & $ScriptPath @baseArgs @ExtraArgs
    $exit    = $LASTEXITCODE
    $elapsed = [int](Get-Date).Subtract($start).TotalSeconds

    $status = if ($exit -eq 0 -or $null -eq $exit) { "PASS" } else { "FAIL" }
    return @{ Label=$Label; Script=$displayPath; ExitCode=$exit; Status=$status; DurationSec=$elapsed }
}

# ──────────────────────────────────────────────────────────
# 准备日志目录
# ──────────────────────────────────────────────────────────
if (-not [System.IO.Path]::IsPathRooted($LogDir)) {
    $base   = (Resolve-Path (Join-Path $scriptDir "..")).Path
    $LogDir = Join-Path $base $LogDir
}
if (-not (Test-Path $LogDir)) { New-Item -ItemType Directory -Path $LogDir -Force | Out-Null }

# ──────────────────────────────────────────────────────────
# 全局欢迎横幅
# ──────────────────────────────────────────────────────────
Write-Host ""
Write-Host "╔══════════════════════════════════════════════════════╗" -ForegroundColor White
Write-Host "║         JGSY.AGI 全量测试套件                       ║" -ForegroundColor White
Write-Host "║  Gateway : $GatewayUrl$((" " * (40 - $GatewayUrl.Length)))║" -ForegroundColor White
Write-Host "║  AI      : $AiUrl$((" " * (40 - $AiUrl.Length)))║" -ForegroundColor White
Write-Host "║  Chain   : $BlockchainUrl$((" " * (40 - $BlockchainUrl.Length)))║" -ForegroundColor White
Write-Host "║  Run at  : $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')                   ║" -ForegroundColor White
Write-Host "╚══════════════════════════════════════════════════════╝" -ForegroundColor White

# ──────────────────────────────────────────────────────────
# 快速连通性预检（任一失败直接中止）
# ──────────────────────────────────────────────────────────
Write-Banner "预检 - 服务连通性" "Yellow"
$preCheckFail = $false
@(
    @{ Name="Gateway";    Url="$GatewayUrl/health" },
    @{ Name="IotCloudAI"; Url="$AiUrl/health" },
    @{ Name="Blockchain"; Url="$BlockchainUrl/health" }
) | ForEach-Object {
    try {
        $null = Invoke-WebRequest -Uri $_.Url -Method GET -TimeoutSec 8 -ErrorAction Stop
        Write-Host "  ✅ $($_.Name) 在线" -ForegroundColor Green
    } catch {
        Write-Host "  ❌ $($_.Name) 不可达: $($_.Url)" -ForegroundColor Red
        $preCheckFail = $true
    }
}
if ($preCheckFail) {
    Write-Host "`n服务不可达，请先确认 docker compose 已运行。中止测试。" -ForegroundColor Red
    exit 1
}

# ──────────────────────────────────────────────────────────
# 逐步执行测试套件
# ──────────────────────────────────────────────────────────
$suiteResults = @()

# 1. 上线门禁
if (-not $SkipGate) {
    $suiteResults += Invoke-Suite -Label "1/9 上线门禁"  -ScriptPath (Join-Path $scriptDir "go-live-gate.ps1")
} else {
    Write-Host "`n⏭  跳过上线门禁" -ForegroundColor DarkGray
    $suiteResults += @{ Label="1/9 上线门禁"; Script="go-live-gate.ps1"; ExitCode=0; Status="SKIP"; DurationSec=0 }
}

# 2. 四子系统功能测试
$suiteResults += Invoke-Suite -Label "2/9 四子系统" -ScriptPath (Join-Path $scriptDir "test-four-subsystems.ps1")

# 3. 实时数据流
$suiteResults += Invoke-Suite -Label "3/9 实时数据流" -ScriptPath (Join-Path $scriptDir "test-realtime-data-flow.ps1")

# 4. 能源 CRUD
if (-not $SkipCrud) {
    $suiteResults += Invoke-Suite -Label "4/9 能源CRUD" -ScriptPath (Join-Path $scriptDir "test-energy-crud.ps1")
} else {
    Write-Host "`n⏭  跳过CRUD写操作（-SkipCrud）" -ForegroundColor DarkGray
    $suiteResults += @{ Label="4/9 能源CRUD"; Script="test-energy-crud.ps1"; ExitCode=0; Status="SKIP"; DurationSec=0 }
}

# 5. 区块链集成
$suiteResults += Invoke-Suite -Label "5/9 区块链集成" -ScriptPath (Join-Path $scriptDir "test-blockchain-integration.ps1")

# 6. E2E 业务全链路
$suiteResults += Invoke-Suite -Label "6/9 E2E业务链路" -ScriptPath (Join-Path $scriptDir "test-e2e-business-flow.ps1")

# 7. 接口自动扫描（全量）
if (-not $SkipCrud) {
    $suiteResults += Invoke-Suite -Label "7/9 接口自动扫描" -ScriptPath (Join-Path $scriptDir "auto-test-generator.ps1")
} else {
    $suiteResults += @{ Label="7/9 接口自动扫描"; Script="auto-test-generator.ps1"; ExitCode=0; Status="SKIP"; DurationSec=0 }
}

# 8. 多条件组合查询
$suiteResults += Invoke-Suite -Label "8/9 多条件查询" -ScriptPath (Join-Path $scriptDir "test-query-combinations.ps1")

# 9. 边界/异常测试
$suiteResults += Invoke-Suite -Label "9/9 边界异常" -ScriptPath (Join-Path $scriptDir "test-boundary-cases.ps1")

# ──────────────────────────────────────────────────────────
# 可选：k6 负载测试
# ──────────────────────────────────────────────────────────
if ($WithLoadTest) {
    Write-Banner "K6 负载测试（可选）" "Magenta"
    $k6Scripts = @(
        @{ Label="K6 能源负载"; File="testing/k6/scenarios/energy-load-test.js" },
        @{ Label="K6 全服务压力"; File="testing/k6/scenarios/full-service-stress.js" }
    )
    if (Get-Command k6 -ErrorAction SilentlyContinue) {
        foreach ($ks in $k6Scripts) {
            $k6Path = Join-Path $rootDir.Path $ks.File
            if (-not (Test-Path $k6Path)) {
                Write-Host "  ⚠️  找不到脚本: $($ks.File)" -ForegroundColor Yellow
                $suiteResults += @{ Label=$ks.Label; Script=$ks.File; ExitCode=-1; Status="SKIP"; DurationSec=0 }
                continue
            }
            Write-Host "  ▶ $($ks.Label)" -ForegroundColor Magenta
            $k6Start = Get-Date
            & k6 run `
                --env GATEWAY_URL=$GatewayUrl `
                --env AI_URL=$AiUrl `
                --env BC_URL=$BlockchainUrl `
                --summary-export="$LogDir/k6-$(($ks.Label -replace '[^a-z0-9]','-').ToLower())-$(Get-Date -Format 'yyyyMMddHHmmss').json" `
                $k6Path
            $suiteResults += @{
                Label=$ks.Label; Script=$ks.File
                ExitCode=$LASTEXITCODE
                Status=if ($LASTEXITCODE -eq 0) {"PASS"} else {"FAIL"}
                DurationSec=[int](Get-Date).Subtract($k6Start).TotalSeconds
            }
        }
    } else {
        Write-Host "  ⚠️  k6 未安装，跳过（https://k6.io/docs/get-started/installation/）" -ForegroundColor Yellow
        $k6Scripts | ForEach-Object {
            $suiteResults += @{ Label=$_.Label; Script=$_.File; ExitCode=-1; Status="SKIP"; DurationSec=0 }
        }
    }
}

# ──────────────────────────────────────────────────────────
# 聚合报告
# ──────────────────────────────────────────────────────────
$totalElapsed = [int](Get-Date).Subtract($suiteStart).TotalSeconds
$passCount = ($suiteResults | Where-Object { $_.Status -eq "PASS" }).Count
$failCount = ($suiteResults | Where-Object { $_.Status -eq "FAIL" }).Count
$skipCount = ($suiteResults | Where-Object { $_.Status -eq "SKIP" }).Count
$totalCount = $suiteResults.Count

Write-Banner "全量测试套件汇总" "Cyan"

foreach ($r in $suiteResults) {
    $emoji = switch ($r.Status) { "PASS"{"✅"}; "FAIL"{"❌"}; "SKIP"{"⏭"}; default{"⚠️"} }
    $color = switch ($r.Status) { "PASS"{"Green"}; "FAIL"{"Red"}; "SKIP"{"DarkGray"}; default{"Yellow"} }
    Write-Host ("  {0} {1,-20} {2,3}s  {3}" -f $emoji, $r.Label, $r.DurationSec, $r.Script) -ForegroundColor $color
}

$passRate = if ($totalCount -gt 0) { [math]::Round($passCount / $totalCount * 100) } else { 0 }
Write-Host ""
Write-Host "总计 $totalCount 套件  ✅PASS=$passCount  ❌FAIL=$failCount  ⏭SKIP=$skipCount  通过率=$passRate%  总耗时=${totalElapsed}s" -ForegroundColor White

# ──────────────────────────────────────────────────────────
# 生成 Markdown 报告
# ──────────────────────────────────────────────────────────
$reportTs   = Get-Date -Format "yyyyMMdd-HHmmss"
$reportPath = Join-Path $LogDir "full-test-suite-$reportTs.md"

$failedDetail = $suiteResults | Where-Object { $_.Status -eq "FAIL" } | ForEach-Object {
    "- ❌ **$($_.Label)** (`$($_.Script)`) ExitCode=$($_.ExitCode)"
}
$rowsContent = $suiteResults | ForEach-Object {
    $emoji = switch ($_.Status) { "PASS"{"✅ PASS"}; "FAIL"{"❌ FAIL"}; "SKIP"{"⏭ SKIP"}; default{"⚠️ WARN"} }
    "| $($_.Label) | $($_.Script) | $emoji | $($_.DurationSec)s |"
}

$mdContent = @"
# JGSY.AGI 全量测试报告

**执行时间**：$(Get-Date -Format "yyyy-MM-dd HH:mm:ss")  
**总耗时**：${totalElapsed}s  
**Gateway**：$GatewayUrl  
**IotCloudAI**：$AiUrl  
**Blockchain**：$BlockchainUrl  

## 测试套件汇总

| 套件 | 脚本 | 结果 | 耗时 |
|------|------|------|------|
$($rowsContent -join "`n")

## 整体结论

> **通过率：$passRate%**（$passCount/$totalCount 套件通过）

$(if ($failCount -eq 0) {
"✅ **全部通过** — 系统已就绪，可上线操作。"
} else {
"❌ **存在失败** — 以下套件需修复：

$($failedDetail -join "`n")
"
})

## 说明

- `PASS`：脚本以 ExitCode=0 结束
- `FAIL`：脚本以非零 ExitCode 结束或内部断言失败
- `SKIP`：脚本不存在或通过参数主动跳过
- `WARN`：脚本内部单步警告（不影响套件 PASS/FAIL 判定）

---
*报告由 run-full-test-suite.ps1 自动生成*
"@

try {
    $mdContent | Out-File -FilePath $reportPath -Encoding UTF8 -Force
    Write-Host "`nMarkdown 报告：$reportPath" -ForegroundColor Gray
} catch {
    Write-Host "报告保存失败: $($_.Exception.Message)" -ForegroundColor Yellow
}

# ──────────────────────────────────────────────────────────
# 最终退出码
# ──────────────────────────────────────────────────────────
$verdict = if ($failCount -eq 0) { "✅ 全量测试通过" } else { "❌ 存在失败套件，请查阅日志" }
Write-Host "`n$verdict" -ForegroundColor $(if ($failCount -eq 0) {"Green"} else {"Red"})

exit $(if ($failCount -eq 0) { 0 } else { 1 })
