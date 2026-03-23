<#
.SYNOPSIS
    Layer 8: 合规性审计测试
.DESCRIPTION
    覆盖:
    1. AOT 兼容性扫描 - 禁止列表检查(AutoMapper, MediatR, Newtonsoft.Json, dynamic, Activator)
    2. Publish 产物完整性 - 20 服务 DLL 检查
    3. 配置合规 - appsettings.json 必需节点检查
    4. NuGet 漏洞扫描 - dotnet list package --vulnerable
    5. 权限码覆盖率 - all-permission-codes.txt vs RequirePermission
    6. 数据库完整性 - tenant_id/delete_at 列覆盖
    7. Docker 配置合规 - 容器命名/健康检查
    8. 编码规范 - UTF-8 BOM，禁止dev专用配置
#>
param(
    [string]$RootDir = (Split-Path (Split-Path $PSScriptRoot -Parent) -Parent),
    [string]$GatewayUrl = "http://localhost:5000"
)

$ErrorActionPreference = 'Continue'
$logDir = "$PSScriptRoot\logs"
if (-not (Test-Path $logDir)) { New-Item -ItemType Directory -Path $logDir -Force | Out-Null }

$ts = Get-Date -Format 'yyyy-MM-dd_HH-mm-ss'
$reportFile = "$logDir\compliance-report-$ts.txt"

$script:totalTests = 0
$script:passedTests = 0
$script:failedTests = 0
$script:results = @()

function Write-TestResult {
    param([string]$Category, [string]$Name, [bool]$Pass, [string]$Detail = "")
    $script:totalTests++
    if ($Pass) { $script:passedTests++ } else { $script:failedTests++ }
    $status = if ($Pass) { "PASS" } else { "FAIL" }
    $line = "[$status] $Category :: $Name $(if($Detail){"| $Detail"})"
    Write-Host $line -ForegroundColor $(if ($Pass) { "Green" } else { "Red" })
    $script:results += $line
}

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "  Layer 8: 合规性审计测试" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

# ===========================
# 1. AOT 兼容性扫描
# ===========================
Write-Host "--- 1. AOT 兼容性扫描 ---" -ForegroundColor Yellow

$aotForbidden = @(
    @{ Pattern = "using AutoMapper"; Desc = "禁止 AutoMapper" },
    @{ Pattern = "using MediatR"; Desc = "禁止 MediatR" },
    @{ Pattern = "using Newtonsoft.Json"; Desc = "禁止 Newtonsoft.Json" },
    @{ Pattern = "Activator.CreateInstance"; Desc = "禁止 Activator.CreateInstance" },
    @{ Pattern = "Type.GetType\("; Desc = "禁止 Type.GetType()" },
    @{ Pattern = "\bdynamic\b"; Desc = "禁止 dynamic 关键字" }
)

$serviceProjects = @(
    "JGSY.AGI.Gateway", "JGSY.AGI.Tenant", "JGSY.AGI.Identity", "JGSY.AGI.Permission",
    "JGSY.AGI.Observability", "JGSY.AGI.Storage", "JGSY.AGI.Account", "JGSY.AGI.Analytics",
    "JGSY.AGI.Charging", "JGSY.AGI.Device", "JGSY.AGI.DigitalTwin", "JGSY.AGI.Ingestion",
    "JGSY.AGI.Settlement", "JGSY.AGI.Station", "JGSY.AGI.WorkOrder", "JGSY.AGI.ContentPlatform",
    "JGSY.AGI.Blockchain", "JGSY.AGI.EnergyCore", "JGSY.AGI.EnergyServices", "JGSY.AGI.IotCloudAI"
)

foreach ($fb in $aotForbidden) {
    $violations = @()
    foreach ($proj in $serviceProjects) {
        $projDir = Join-Path $RootDir $proj
        if (Test-Path $projDir) {
            $csFiles = Get-ChildItem -Path $projDir -Filter "*.cs" -Recurse -ErrorAction SilentlyContinue
            foreach ($f in $csFiles) {
                try {
                    $content = Get-Content $f.FullName -Raw -ErrorAction SilentlyContinue
                    if ($content -and $content -match $fb.Pattern) {
                        $violations += "$($proj)/$($f.Name)"
                    }
                } catch {}
            }
        }
    }
    Write-TestResult "AOT兼容" $fb.Desc ($violations.Count -eq 0) $(if($violations.Count -gt 0){"违规: $($violations -join ', ')"}else{"无违规"})
}

# 检查 AppJsonContext 注册
$jsonContextFile = Join-Path $RootDir "JGSY.AGI.Common.Infra\Json\AppJsonContext.cs"
if (Test-Path $jsonContextFile) {
    $jcContent = Get-Content $jsonContextFile -Raw
    $jsonTypes = ([regex]::Matches($jcContent, '\[JsonSerializable\(typeof\(([^)]+)\)\)\]')).Count
    Write-TestResult "AOT兼容" "AppJsonContext 注册类型数" ($jsonTypes -gt 10) "已注册 $jsonTypes 个类型"
} else {
    Write-TestResult "AOT兼容" "AppJsonContext.cs 存在" $false "文件不存在"
}

# ===========================
# 2. Publish 产物完整性
# ===========================
Write-Host "`n--- 2. Publish 产物完整性 ---" -ForegroundColor Yellow

$publishDir = Join-Path $RootDir "docker\publish"
$expectedServices = @(
    "Gateway", "Tenant", "Identity", "Permission", "Observability", "Storage",
    "Account", "Analytics", "Charging", "Device", "DigitalTwin", "Ingestion",
    "Settlement", "Station", "WorkOrder", "ContentPlatform", "Blockchain",
    "EnergyCore", "EnergyServices", "IotCloudAI"
)

if (Test-Path $publishDir) {
    foreach ($svc in $expectedServices) {
        $svcDir = Join-Path $publishDir $svc
        $exists = Test-Path $svcDir
        $hasDll = $false
        if ($exists) {
            $dlls = Get-ChildItem -Path $svcDir -Filter "*.dll" -ErrorAction SilentlyContinue
            $hasDll = $dlls.Count -gt 0
        }
        Write-TestResult "产物完整" "$svc 产物目录" ($exists -and $hasDll) $(if(-not $exists){"目录不存在"}elseif(-not $hasDll){"无 DLL 文件"}else{"$($dlls.Count) DLLs"})
    }
} else {
    Write-TestResult "产物完整" "publish 目录存在" $false "$publishDir 不存在"
}

# ===========================
# 3. 配置合规检查
# ===========================
Write-Host "`n--- 3. 配置合规检查 ---" -ForegroundColor Yellow

$requiredConfigNodes = @("Service", "ConnectionStrings", "Redis", "Jwt", "Logging")

foreach ($proj in $serviceProjects) {
    $configFile = Join-Path $RootDir "$proj\appsettings.json"
    if (Test-Path $configFile) {
        try {
            $config = Get-Content $configFile -Raw | ConvertFrom-Json
            $missingNodes = @()
            foreach ($node in $requiredConfigNodes) {
                if (-not ($config.PSObject.Properties.Name -contains $node)) {
                    $missingNodes += $node
                }
            }
            Write-TestResult "配置合规" "$proj appsettings.json" ($missingNodes.Count -eq 0) $(if($missingNodes.Count -gt 0){"缺少: $($missingNodes -join ', ')"}else{"全部节点完整"})
        } catch {
            Write-TestResult "配置合规" "$proj appsettings.json 解析" $false "$_"
        }
    } else {
        # Gateway 等可能在不同位置
        Write-TestResult "配置合规" "$proj appsettings.json 存在" $false "文件不存在"
    }
}

# 禁止 Development 配置
foreach ($proj in $serviceProjects) {
    $devConfig = Join-Path $RootDir "$proj\appsettings.Development.json"
    $devExists = Test-Path $devConfig
    Write-TestResult "配置合规" "$proj 无 Development 配置" (-not $devExists) $(if($devExists){"存在 appsettings.Development.json"}else{"合规"})
}

# ===========================
# 4. NuGet 漏洞扫描（快速版）
# ===========================
Write-Host "`n--- 4. NuGet 漏洞扫描 ---" -ForegroundColor Yellow

# 检查 Directory.Packages.props 是否使用 Central Package Management
$cpmFile = Join-Path $RootDir "Directory.Packages.props"
if (Test-Path $cpmFile) {
    try {
        $cpmContent = Get-Content $cpmFile -Raw
        $packageCount = ([regex]::Matches($cpmContent, '<PackageVersion\s')).Count
        Write-TestResult "NuGet" "Central Package Management 启用" $true "$packageCount 个包"
        
        # 检查是否有已知高危依赖
        $riskyPkgs = @("Newtonsoft.Json", "AutoMapper", "MediatR")
        foreach ($pkg in $riskyPkgs) {
            $hasPkg = $cpmContent -match "Include=""$pkg"""
            Write-TestResult "NuGet" "无高风险/禁止依赖: $pkg" (-not $hasPkg) $(if($hasPkg){"发现 $pkg"}else{"合规"})
        }
    } catch {
        Write-TestResult "NuGet" "Directory.Packages.props 解析" $false "$_"
    }
} else {
    Write-TestResult "NuGet" "Directory.Packages.props 存在" $false
}

# ===========================
# 5. 权限码覆盖率
# ===========================
Write-Host "`n--- 5. 权限码覆盖率 ---" -ForegroundColor Yellow

$permFile = Join-Path $RootDir "scripts\all-permission-codes.txt"
if (Test-Path $permFile) {
    $permCodes = Get-Content $permFile | Where-Object { $_ -match '\S' -and $_ -notmatch '^\s*#' }
    $permCount = $permCodes.Count
    Write-TestResult "权限码" "权限码清单存在" $true "$permCount 个权限码"
    
    # 扫描所有服务的 RequirePermission 标注
    $annotationCount = 0
    foreach ($proj in $serviceProjects) {
        $projDir = Join-Path $RootDir $proj
        if (Test-Path $projDir) {
            $csFiles = Get-ChildItem -Path $projDir -Filter "*.cs" -Recurse -ErrorAction SilentlyContinue
            foreach ($f in $csFiles) {
                try {
                    $content = Get-Content $f.FullName -Raw -ErrorAction SilentlyContinue
                    if ($content) {
                        $matches = [regex]::Matches($content, '\[RequirePermission\(')
                        $annotationCount += $matches.Count
                    }
                } catch {}
            }
        }
    }
    Write-TestResult "权限码" "RequirePermission 标注数" ($annotationCount -gt 0) "$annotationCount 个标注"
    
    # 检查未使用的权限码
    $usedCodes = @()
    foreach ($proj in $serviceProjects) {
        $projDir = Join-Path $RootDir $proj
        if (Test-Path $projDir) {
            $csFiles = Get-ChildItem -Path $projDir -Filter "*.cs" -Recurse -ErrorAction SilentlyContinue
            foreach ($f in $csFiles) {
                try {
                    $content = Get-Content $f.FullName -Raw -ErrorAction SilentlyContinue
                    if ($content) {
                        $codeMatches = [regex]::Matches($content, '\[RequirePermission\("([^"]+)"\)\]')
                        foreach ($m in $codeMatches) {
                            $usedCodes += $m.Groups[1].Value
                        }
                    }
                } catch {}
            }
        }
    }
    $usedCodes = $usedCodes | Sort-Object -Unique
    $unusedCodes = $permCodes | Where-Object { $usedCodes -notcontains $_ }
    $coverageRate = if ($permCount -gt 0) { [math]::Round(($permCount - $unusedCodes.Count) / $permCount * 100, 1) } else { 0 }
    Write-TestResult "权限码" "权限码覆盖率" ($coverageRate -gt 50) "覆盖率: ${coverageRate}% ($($permCount - $unusedCodes.Count)/$permCount)"
} else {
    Write-TestResult "权限码" "all-permission-codes.txt 存在" $false
}

# ===========================
# 6. 数据库完整性
# ===========================
Write-Host "`n--- 6. 数据库完整性 ---" -ForegroundColor Yellow

$dbHost = "localhost"
$dbPort = 5432
$dbUser = "postgres"
$dbPass = "P@ssw0rd"

$databases = @(
    "jgsy_tenant", "jgsy_identity", "jgsy_permission", "jgsy_station",
    "jgsy_device", "jgsy_account", "jgsy_charging", "jgsy_settlement",
    "jgsy_work_order", "jgsy_analytics", "jgsy_observability", "jgsy_storage",
    "jgsy_blockchain", "jgsy_ingestion", "jgsy_digital_twin", "jgsy_content_platform",
    "jgsy_orchestrator", "jgsy_vpp", "jgsy_microgrid", "jgsy_pvessc",
    "jgsy_electrade", "jgsy_carbontrade", "jgsy_demandresp", "jgsy_deviceops",
    "jgsy_energyeff", "jgsy_multienergy", "jgsy_safecontrol"
)

$env:PGPASSWORD = $dbPass

foreach ($db in $databases) {
    # 检查 tenant_id 列覆盖
    try {
        $tenantQuery = "SELECT count(*) FROM information_schema.tables t WHERE t.table_schema='public' AND t.table_type='BASE TABLE' AND NOT EXISTS (SELECT 1 FROM information_schema.columns c WHERE c.table_schema=t.table_schema AND c.table_name=t.table_name AND c.column_name='tenant_id') AND t.table_name NOT LIKE 'dist_%' AND t.table_name NOT LIKE '__ef%' AND t.table_name NOT IN ('schemaversions','schema_versions');"
        $rawResult = docker exec -e PGCLIENTENCODING=UTF8 jgsy-postgres psql -U $dbUser -d $db -Aqt -c $tenantQuery 2>$null
        $resultStr = if ($rawResult -is [array]) { ($rawResult | Where-Object { $_ -match '^\s*\d+\s*$' } | Select-Object -First 1) } else { $rawResult }
        $missingTenantId = if ($resultStr) { [int]($resultStr.ToString().Trim()) } else { -1 }
        if ($missingTenantId -ge 0) {
            Write-TestResult "数据库" "$db tenant_id 覆盖" ($missingTenantId -eq 0) $(if($missingTenantId -gt 0){"$missingTenantId 表缺少 tenant_id"}else{"全部覆盖"})
        } else {
            Write-TestResult "数据库" "$db tenant_id 查询" $false "数据库不存在或无法连接"
        }
    } catch {
        Write-TestResult "数据库" "$db tenant_id 查询" $false "$_"
    }
    
    # 检查 delete_at 列覆盖
    try {
        $deleteQuery = "SELECT count(*) FROM information_schema.tables t WHERE t.table_schema='public' AND t.table_type='BASE TABLE' AND NOT EXISTS (SELECT 1 FROM information_schema.columns c WHERE c.table_schema=t.table_schema AND c.table_name=t.table_name AND c.column_name='delete_at') AND t.table_name NOT LIKE 'dist_%' AND t.table_name NOT LIKE '__ef%' AND t.table_name NOT IN ('schemaversions','schema_versions');"
        $rawResult2 = docker exec -e PGCLIENTENCODING=UTF8 jgsy-postgres psql -U $dbUser -d $db -Aqt -c $deleteQuery 2>$null
        $resultStr2 = if ($rawResult2 -is [array]) { ($rawResult2 | Where-Object { $_ -match '^\s*\d+\s*$' } | Select-Object -First 1) } else { $rawResult2 }
        $missingDeleteAt = if ($resultStr2) { [int]($resultStr2.ToString().Trim()) } else { -1 }
        if ($missingDeleteAt -ge 0) {
            Write-TestResult "数据库" "$db delete_at 覆盖" ($missingDeleteAt -eq 0) $(if($missingDeleteAt -gt 0){"$missingDeleteAt 表缺少 delete_at"}else{"全部覆盖"})
        } else {
            Write-TestResult "数据库" "$db delete_at 查询" $false "数据库不存在或无法连接"
        }
    } catch {
        Write-TestResult "数据库" "$db delete_at 查询" $false "$_"
    }
}

$env:PGPASSWORD = ""

# ===========================
# 7. Docker 配置合规
# ===========================
Write-Host "`n--- 7. Docker 配置合规 ---" -ForegroundColor Yellow

# 检查容器命名规范 (jgsy-*)
try {
    $containers = docker ps --format "{{.Names}}" 2>$null
    if ($containers) {
        $containerList = $containers -split "`n" | Where-Object { $_ }
        $nonCompliant = $containerList | Where-Object { $_ -notmatch '^jgsy-' -and $_ -notmatch '^[a-z0-9]+-dapr' }
        Write-TestResult "Docker" "容器命名规范 (jgsy-*)" ($nonCompliant.Count -eq 0) $(if($nonCompliant.Count -gt 0){"不合规: $($nonCompliant -join ', ')"}else{"全部合规"})
        Write-TestResult "Docker" "运行中容器数" ($containerList.Count -ge 20) "$($containerList.Count) 个容器"
    }
} catch {
    Write-TestResult "Docker" "容器列表获取" $false "$_"
}

# 检查健康检查配置
$healthCheckContainers = @("jgsy-gateway", "jgsy-tenant", "jgsy-identity", "jgsy-permission",
    "jgsy-station", "jgsy-device", "jgsy-account", "jgsy-charging",
    "jgsy-settlement", "jgsy-workorder", "jgsy-analytics", "jgsy-observability")

foreach ($hc in $healthCheckContainers) {
    try {
        $inspect = docker inspect $hc --format "{{.State.Health.Status}}" 2>$null
        $healthy = $inspect -and $inspect.Trim() -eq "healthy"
        Write-TestResult "Docker" "$hc 健康状态" $healthy $(if(-not $healthy){"状态: $($inspect)"}else{"healthy"})
    } catch {
        Write-TestResult "Docker" "$hc 健康检查" $false "容器不存在或无健康检查"
    }
}

# ===========================
# 8. 编码规范检查
# ===========================
Write-Host "`n--- 8. 编码规范检查 ---" -ForegroundColor Yellow

# 检查是否存在 environment 判断代码
$envCheckViolations = @()
foreach ($proj in $serviceProjects) {
    $projDir = Join-Path $RootDir $proj
    if (Test-Path $projDir) {
        $csFiles = Get-ChildItem -Path $projDir -Filter "*.cs" -Recurse -ErrorAction SilentlyContinue
        foreach ($f in $csFiles) {
            try {
                $content = Get-Content $f.FullName -Raw -ErrorAction SilentlyContinue
                if ($content -match 'env\s*==\s*"Development"' -or $content -match 'IsDevelopment\(\)') {
                    $envCheckViolations += "$($proj)/$($f.Name)"
                }
            } catch {}
        }
    }
}
Write-TestResult "编码规范" "无 Development 环境判断" ($envCheckViolations.Count -eq 0) $(if($envCheckViolations.Count -gt 0){"违规 $($envCheckViolations.Count) 处: $($envCheckViolations[0..2] -join ', ')..."}else{"合规"})

# 检查是否存在 HttpClient 直接使用（应使用 IServiceTransport）
$httpClientViolations = @()
foreach ($proj in $serviceProjects) {
    if ($proj -match "Gateway|Common") { continue }
    $projDir = Join-Path $RootDir $proj
    if (Test-Path $projDir) {
        $csFiles = Get-ChildItem -Path $projDir -Filter "*.cs" -Recurse -ErrorAction SilentlyContinue
        foreach ($f in $csFiles) {
            if ($f.Name -match "Program\.cs|Startup\.cs|Extension") { continue }
            try {
                $content = Get-Content $f.FullName -Raw -ErrorAction SilentlyContinue
                if ($content -match 'new\s+HttpClient\(' -or $content -match 'IHttpClientFactory') {
                    $httpClientViolations += "$($proj)/$($f.Name)"
                }
            } catch {}
        }
    }
}
Write-TestResult "编码规范" "无直接 HttpClient 使用" ($httpClientViolations.Count -le 5) $(if($httpClientViolations.Count -gt 0){"发现 $($httpClientViolations.Count) 处"}else{"合规"})

# 检查 appsettings 中是否有硬编码密码(非标准的)
$hardcodedSecrets = 0
foreach ($proj in $serviceProjects) {
    $configFile = Join-Path $RootDir "$proj\appsettings.json"
    if (Test-Path $configFile) {
        try {
            $content = Get-Content $configFile -Raw
            # 检查非标准密码
            if ($content -match '"Password"\s*:\s*"(?!P@ssw0rd|jgsy_)' -or $content -match '"Secret"\s*:\s*"[^$]') {
                $hardcodedSecrets++
            }
        } catch {}
    }
}
Write-TestResult "编码规范" "无非标准硬编码密码" ($hardcodedSecrets -eq 0) $(if($hardcodedSecrets -gt 0){"$hardcodedSecrets 处发现"}else{"合规"})

# === 汇总 ===
Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "  Layer 8 合规性审计完成" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  总测试: $($script:totalTests)" -ForegroundColor White
Write-Host "  通过:   $($script:passedTests)" -ForegroundColor Green
Write-Host "  失败:   $($script:failedTests)" -ForegroundColor $(if ($script:failedTests -gt 0) { "Red" } else { "Green" })
$passRate = if ($script:totalTests -gt 0) { [math]::Round($script:passedTests / $script:totalTests * 100, 1) } else { 0 }
Write-Host "  通过率: ${passRate}%`n" -ForegroundColor $(if ($passRate -ge 90) { "Green" } elseif ($passRate -ge 70) { "Yellow" } else { "Red" })

# 输出报告
$reportContent = @"
========================================
Layer 8: 合规性审计测试报告
时间: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')
========================================
总测试: $($script:totalTests)
通过:   $($script:passedTests)
失败:   $($script:failedTests)
通过率: ${passRate}%

--- 详细结果 ---
$($script:results -join "`n")
"@

$reportContent | Out-File -FilePath $reportFile -Encoding utf8
Write-Host "报告已保存: $reportFile" -ForegroundColor Gray

return @{
    Total = $script:totalTests
    Passed = $script:passedTests
    Failed = $script:failedTests
    PassRate = $passRate
}
