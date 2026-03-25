<#
.SYNOPSIS
    全量综合测试 - 主编排脚本
.DESCRIPTION
    按顺序执行所有 8 层测试，汇总结果，生成最终报告:
    Layer 1-2: 健康检查 + 全量 API 扫描 (3,373+ 端点)
    Layer 3:   全服务 CRUD 测试
    Layer 4:   业务流程端到端测试
    Layer 5:   安全与认证测试
    Layer 6:   性能/压力/并发测试 (k6)
    Layer 7:   稳定性与恢复测试
    Layer 8:   合规性审计测试
.PARAMETER SkipLayers
    跳过指定层 (逗号分隔，如 "6,7")
.PARAMETER OnlyLayers
    仅执行指定层 (逗号分隔，如 "1,2,3")
.PARAMETER SkipK6
    跳过 k6 性能测试
.PARAMETER SustainedDuration
    持续稳定性测试时长(秒)，默认 120
#>
param(
    [string]$SkipLayers = "",
    [string]$OnlyLayers = "",
    [switch]$SkipK6,
    [int]$SustainedDuration = 120,
    [string]$GatewayUrl = "http://localhost:5000"
)

$ErrorActionPreference = 'Continue'
$scriptDir = $PSScriptRoot
$logDir = "$scriptDir\logs"
if (-not (Test-Path $logDir)) { New-Item -ItemType Directory -Path $logDir -Force | Out-Null }

# 加载测试环境变量（将浏览器/npm/缓存全部指向 D 盘）
$envScript = Join-Path $scriptDir "..\set-test-env.ps1"
if (Test-Path $envScript) {
    . $envScript
} else {
    Write-Host "  ⚠️ tests\set-test-env.ps1 不存在，浏览器缓存可能写入 C 盘" -ForegroundColor Yellow
}

$ts = Get-Date -Format 'yyyy-MM-dd_HH-mm-ss'
$finalReportFile = "$logDir\full-test-report-$ts.txt"

# 解析层级控制
$skipSet = @()
if ($SkipLayers) { $skipSet = $SkipLayers -split ',' | ForEach-Object { [int]$_.Trim() } }
$onlySet = @()
if ($OnlyLayers) { $onlySet = $OnlyLayers -split ',' | ForEach-Object { [int]$_.Trim() } }

function Should-RunLayer([int]$layer) {
    if ($onlySet.Count -gt 0) { return $onlySet -contains $layer }
    if ($skipSet.Count -gt 0) { return $skipSet -notcontains $layer }
    return $true
}

# === 全局计数 ===
$layerResults = @{}
$globalStart = Get-Date

Write-Host ""
Write-Host "╔══════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║   JGSY.AGI 全量综合测试 - 主编排脚本            ║" -ForegroundColor Cyan
Write-Host "║   覆盖 3,373+ API 端点 × 17+ 微服务             ║" -ForegroundColor Cyan
Write-Host "║   8 层测试架构                                  ║" -ForegroundColor Cyan
Write-Host "╚══════════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""
Write-Host "  开始时间: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')" -ForegroundColor Gray
Write-Host "  网关地址: $GatewayUrl" -ForegroundColor Gray
Write-Host ""

# ===========================
# Layer 1-2: 健康检查 + 全量 API 扫描
# ===========================
if (Should-RunLayer 1) {
    Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Magenta
    Write-Host "  Layer 1-2: 健康检查 + 全量 API 扫描" -ForegroundColor Magenta
    Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Magenta
    
    $l12Start = Get-Date
    try {
        $l12Script = Join-Path $scriptDir "test-all-api-scan.ps1"
        if (Test-Path $l12Script) {
            & $l12Script -GatewayUrl $GatewayUrl
            $layerResults["Layer 1-2"] = @{ Status = "完成"; Time = [math]::Round(((Get-Date) - $l12Start).TotalSeconds) }
        } else {
            Write-Host "[SKIP] test-all-api-scan.ps1 不存在" -ForegroundColor Yellow
            $layerResults["Layer 1-2"] = @{ Status = "跳过-脚本不存在"; Time = 0 }
        }
    } catch {
        Write-Host "[ERROR] Layer 1-2 执行失败: $_" -ForegroundColor Red
        $layerResults["Layer 1-2"] = @{ Status = "失败"; Time = [math]::Round(((Get-Date) - $l12Start).TotalSeconds) }
    }
    Write-Host ""
}

# ===========================
# Layer 3: 全服务 CRUD
# ===========================
if (Should-RunLayer 3) {
    Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Magenta
    Write-Host "  Layer 3: 全服务 CRUD 测试" -ForegroundColor Magenta
    Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Magenta
    
    $l3Start = Get-Date
    try {
        $l3Script = Join-Path $scriptDir "test-crud-all-services.ps1"
        if (Test-Path $l3Script) {
            & $l3Script -GatewayUrl $GatewayUrl
            $layerResults["Layer 3"] = @{ Status = "完成"; Time = [math]::Round(((Get-Date) - $l3Start).TotalSeconds) }
        } else {
            Write-Host "[SKIP] test-crud-all-services.ps1 不存在" -ForegroundColor Yellow
            $layerResults["Layer 3"] = @{ Status = "跳过-脚本不存在"; Time = 0 }
        }
    } catch {
        Write-Host "[ERROR] Layer 3 执行失败: $_" -ForegroundColor Red
        $layerResults["Layer 3"] = @{ Status = "失败"; Time = [math]::Round(((Get-Date) - $l3Start).TotalSeconds) }
    }
    Write-Host ""
}

# ===========================
# Layer 4: 业务流程
# ===========================
if (Should-RunLayer 4) {
    Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Magenta
    Write-Host "  Layer 4: 业务流程端到端测试" -ForegroundColor Magenta
    Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Magenta
    
    $l4Start = Get-Date
    try {
        $l4Script = Join-Path $scriptDir "test-business-flows.ps1"
        if (Test-Path $l4Script) {
            & $l4Script -GatewayUrl $GatewayUrl
            $layerResults["Layer 4"] = @{ Status = "完成"; Time = [math]::Round(((Get-Date) - $l4Start).TotalSeconds) }
        } else {
            Write-Host "[SKIP] test-business-flows.ps1 不存在" -ForegroundColor Yellow
            $layerResults["Layer 4"] = @{ Status = "跳过-脚本不存在"; Time = 0 }
        }
    } catch {
        Write-Host "[ERROR] Layer 4 执行失败: $_" -ForegroundColor Red
        $layerResults["Layer 4"] = @{ Status = "失败"; Time = [math]::Round(((Get-Date) - $l4Start).TotalSeconds) }
    }
    Write-Host ""
}

# ===========================
# Layer 5: 安全测试
# ===========================
if (Should-RunLayer 5) {
    Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Magenta
    Write-Host "  Layer 5: 安全与认证测试" -ForegroundColor Magenta
    Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Magenta
    
    $l5Start = Get-Date
    try {
        $l5Script = Join-Path $scriptDir "test-security-full.ps1"
        if (Test-Path $l5Script) {
            & $l5Script -GatewayUrl $GatewayUrl
            $layerResults["Layer 5"] = @{ Status = "完成"; Time = [math]::Round(((Get-Date) - $l5Start).TotalSeconds) }
        } else {
            Write-Host "[SKIP] test-security-full.ps1 不存在" -ForegroundColor Yellow
            $layerResults["Layer 5"] = @{ Status = "跳过-脚本不存在"; Time = 0 }
        }
    } catch {
        Write-Host "[ERROR] Layer 5 执行失败: $_" -ForegroundColor Red
        $layerResults["Layer 5"] = @{ Status = "失败"; Time = [math]::Round(((Get-Date) - $l5Start).TotalSeconds) }
    }
    Write-Host ""
}

# ===========================
# Layer 6: 性能测试 (k6)
# ===========================
if ((Should-RunLayer 6) -and (-not $SkipK6)) {
    Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Magenta
    Write-Host "  Layer 6: 性能/压力/并发测试 (k6)" -ForegroundColor Magenta
    Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Magenta
    
    $l6Start = Get-Date
    try {
        $k6Script = Join-Path $scriptDir "test-performance.js"
        $k6Exe = Get-Command k6 -ErrorAction SilentlyContinue
        if ($k6Exe -and (Test-Path $k6Script)) {
            $k6Output = "$logDir\k6-output-$ts.txt"
            Push-Location $scriptDir
            & k6 run --out json="$logDir\k6-metrics-$ts.json" $k6Script 2>&1 | Tee-Object -FilePath $k6Output
            Pop-Location
            $layerResults["Layer 6"] = @{ Status = "完成"; Time = [math]::Round(((Get-Date) - $l6Start).TotalSeconds) }
        } else {
            if (-not $k6Exe) { Write-Host "[SKIP] k6 未安装" -ForegroundColor Yellow }
            if (-not (Test-Path $k6Script)) { Write-Host "[SKIP] test-performance.js 不存在" -ForegroundColor Yellow }
            $layerResults["Layer 6"] = @{ Status = "跳过"; Time = 0 }
        }
    } catch {
        Write-Host "[ERROR] Layer 6 执行失败: $_" -ForegroundColor Red
        $layerResults["Layer 6"] = @{ Status = "失败"; Time = [math]::Round(((Get-Date) - $l6Start).TotalSeconds) }
    }
    Write-Host ""
} elseif ($SkipK6) {
    Write-Host "[INFO] Layer 6: k6 性能测试已跳过 (-SkipK6)" -ForegroundColor Yellow
    $layerResults["Layer 6"] = @{ Status = "跳过(-SkipK6)"; Time = 0 }
}

# ===========================
# Layer 7: 稳定性测试
# ===========================
if (Should-RunLayer 7) {
    Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Magenta
    Write-Host "  Layer 7: 稳定性与恢复测试" -ForegroundColor Magenta
    Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Magenta
    
    $l7Start = Get-Date
    try {
        $l7Script = Join-Path $scriptDir "test-stability.ps1"
        if (Test-Path $l7Script) {
            & $l7Script -GatewayUrl $GatewayUrl -SustainedDurationSec $SustainedDuration
            $layerResults["Layer 7"] = @{ Status = "完成"; Time = [math]::Round(((Get-Date) - $l7Start).TotalSeconds) }
        } else {
            Write-Host "[SKIP] test-stability.ps1 不存在" -ForegroundColor Yellow
            $layerResults["Layer 7"] = @{ Status = "跳过-脚本不存在"; Time = 0 }
        }
    } catch {
        Write-Host "[ERROR] Layer 7 执行失败: $_" -ForegroundColor Red
        $layerResults["Layer 7"] = @{ Status = "失败"; Time = [math]::Round(((Get-Date) - $l7Start).TotalSeconds) }
    }
    Write-Host ""
}

# ===========================
# Layer 8: 合规审计
# ===========================
if (Should-RunLayer 8) {
    Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Magenta
    Write-Host "  Layer 8: 合规性审计测试" -ForegroundColor Magenta
    Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Magenta
    
    $l8Start = Get-Date
    try {
        $l8Script = Join-Path $scriptDir "test-compliance-audit.ps1"
        if (Test-Path $l8Script) {
            & $l8Script -GatewayUrl $GatewayUrl
            $layerResults["Layer 8"] = @{ Status = "完成"; Time = [math]::Round(((Get-Date) - $l8Start).TotalSeconds) }
        } else {
            Write-Host "[SKIP] test-compliance-audit.ps1 不存在" -ForegroundColor Yellow
            $layerResults["Layer 8"] = @{ Status = "跳过-脚本不存在"; Time = 0 }
        }
    } catch {
        Write-Host "[ERROR] Layer 8 执行失败: $_" -ForegroundColor Red
        $layerResults["Layer 8"] = @{ Status = "失败"; Time = [math]::Round(((Get-Date) - $l8Start).TotalSeconds) }
    }
    Write-Host ""
}

# ===========================
# 最终汇总
# ===========================
$globalEnd = Get-Date
$totalTime = [math]::Round(($globalEnd - $globalStart).TotalSeconds)
$totalMin = [math]::Floor($totalTime / 60)
$totalSec = $totalTime % 60

Write-Host ""
Write-Host "╔══════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║          全量综合测试 - 最终汇总                 ║" -ForegroundColor Cyan
Write-Host "╚══════════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""
Write-Host "  总耗时: ${totalMin}分${totalSec}秒" -ForegroundColor White
Write-Host ""

# 打印各层结果
Write-Host "  ┌─────────────┬──────────┬──────────┐" -ForegroundColor Gray
Write-Host "  │ 层级        │ 状态     │ 耗时(s)  │" -ForegroundColor Gray
Write-Host "  ├─────────────┼──────────┼──────────┤" -ForegroundColor Gray

$layers = @("Layer 1-2", "Layer 3", "Layer 4", "Layer 5", "Layer 6", "Layer 7", "Layer 8")
foreach ($layer in $layers) {
    $lr = $layerResults[$layer]
    if ($lr) {
        $statusColor = if ($lr.Status -eq "完成") { "Green" } elseif ($lr.Status -match "跳过") { "Yellow" } else { "Red" }
        $statusStr = $lr.Status.PadRight(8)
        $timeStr = "$($lr.Time)".PadLeft(8)
        Write-Host "  │ $($layer.PadRight(11)) │ " -NoNewline -ForegroundColor Gray
        Write-Host "$statusStr" -NoNewline -ForegroundColor $statusColor
        Write-Host " │ $timeStr │" -ForegroundColor Gray
    } else {
        Write-Host "  │ $($layer.PadRight(11)) │ 未执行   │      N/A │" -ForegroundColor Gray
    }
}
Write-Host "  └─────────────┴──────────┴──────────┘" -ForegroundColor Gray

# 收集所有层的日志报告
Write-Host ""
Write-Host "  日志文件:" -ForegroundColor Gray
$logFiles = Get-ChildItem -Path $logDir -Filter "*$($ts.Substring(0,10))*" -ErrorAction SilentlyContinue | Sort-Object Name
foreach ($lf in $logFiles) {
    Write-Host "    - $($lf.Name)" -ForegroundColor DarkGray
}

# 生成最终报告
$finalReport = @"
══════════════════════════════════════════════════
  JGSY.AGI 全量综合测试报告
  生成时间: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')
══════════════════════════════════════════════════

平台信息:
  网关: $GatewayUrl
  微服务: 20 个
  API 端点: 3,373+
  数据库: PostgreSQL 16 × 19 库

测试架构: 8 层
  Layer 1-2: 健康检查 + 全量 API 扫描
  Layer 3:   全服务 CRUD 测试
  Layer 4:   业务流程端到端测试
  Layer 5:   安全与认证测试
  Layer 6:   性能/压力/并发测试 (k6)
  Layer 7:   稳定性与恢复测试
  Layer 8:   合规性审计测试

总耗时: ${totalMin}分${totalSec}秒

各层执行状态:
$(foreach ($layer in $layers) {
    $lr = $layerResults[$layer]
    if ($lr) { "  $layer : $($lr.Status) (${$lr.Time}s)" }
    else { "  $layer : 未执行" }
})

日志文件:
$(foreach ($lf in $logFiles) { "  - $($lf.Name)" })

══════════════════════════════════════════════════
"@

$finalReport | Out-File -FilePath $finalReportFile -Encoding utf8
Write-Host ""
Write-Host "  最终报告: $finalReportFile" -ForegroundColor Cyan
Write-Host ""
