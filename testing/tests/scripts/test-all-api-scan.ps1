<#
.SYNOPSIS
    Layer 1-2: 全量 API 可达性扫描
.DESCRIPTION
    - 20 个服务健康检查
    - 17 个服务 3373+ 端点全量扫描（通过 Swagger 自动发现）
    - GET 端点直接请求，POST/PUT/DELETE 发最小体验证非 5xx
    - 输出 CSV + 统计摘要
#>
param(
    [string]$GatewayBase = "http://localhost:5000",
    [string]$LogDir = "tests/scripts/logs"
)

$ErrorActionPreference = "Continue"
$ts = Get-Date -Format "yyyyMMdd-HHmmss"
$csvPath = "$LogDir/api-scan-$ts.csv"
if (!(Test-Path $LogDir)) { New-Item -ItemType Directory -Path $LogDir -Force | Out-Null }

# ========== 公共函数 ==========
function Get-Token {
    $body = '{"userName":"admin","password":"P@ssw0rd"}'
    $resp = Invoke-RestMethod -Uri "$GatewayBase/api/auth/login" -Method POST -Body $body -ContentType "application/json" -TimeoutSec 10
    return $resp.data.accessToken
}

$global:results = [System.Collections.Generic.List[pscustomobject]]::new()
function Add-Result($Layer, $Service, $Method, $Path, $Status, $Detail) {
    $global:results.Add([pscustomobject]@{
        Layer=$Layer; Service=$Service; Method=$Method; Path=$Path;
        Status=$Status; Detail=$Detail; Time=(Get-Date -Format "HH:mm:ss")
    })
}

# ========== Layer 1: 健康检查 ==========
Write-Host "`n========== Layer 1: 健康检查 ==========" -ForegroundColor Cyan
$healthPorts = @{
    Gateway=5000; Tenant=8001; Identity=8002; Permission=8003; Observability=8005;
    Storage=8006; Account=8008; Analytics=8009; Charging=8010; Device=8011;
    DigitalTwin=8012; Ingestion=8013; Settlement=8014; Station=8015; WorkOrder=8016;
    ContentPlatform=8017; Blockchain=8021; EnergyCore=8022; EnergyServices=8026; IotCloudAI=8020
}
$healthPass = 0; $healthFail = 0
foreach ($svc in $healthPorts.GetEnumerator() | Sort-Object Value) {
    try {
        $r = Invoke-WebRequest -Uri "http://localhost:$($svc.Value)/health" -UseBasicParsing -TimeoutSec 5
        if ($r.StatusCode -eq 200) {
            Write-Host "  [PASS] $($svc.Key):$($svc.Value)" -ForegroundColor Green
            Add-Result "L1-Health" $svc.Key "GET" "/health" "PASS" "HTTP 200"
            $healthPass++
        } else {
            Write-Host "  [FAIL] $($svc.Key):$($svc.Value) => $($r.StatusCode)" -ForegroundColor Red
            Add-Result "L1-Health" $svc.Key "GET" "/health" "FAIL" "HTTP $($r.StatusCode)"
            $healthFail++
        }
    } catch {
        Write-Host "  [FAIL] $($svc.Key):$($svc.Value) => $($_.Exception.Message)" -ForegroundColor Red
        Add-Result "L1-Health" $svc.Key "GET" "/health" "FAIL" $_.Exception.Message
        $healthFail++
    }
}
Write-Host "  Health: $healthPass PASS / $healthFail FAIL" -ForegroundColor $(if($healthFail -eq 0){"Green"}else{"Red"})

# ========== Layer 1b: 基础设施连通 ==========
Write-Host "`n========== Layer 1b: 基础设施连通 ==========" -ForegroundColor Cyan
# Redis
try {
    docker exec jgsy-redis redis-cli -a jgsy_redis_2024 ping 2>$null | Out-Null
    Write-Host "  [PASS] Redis" -ForegroundColor Green
    Add-Result "L1-Infra" "Redis" "PING" "redis:6379" "PASS" "PONG"
} catch {
    Write-Host "  [FAIL] Redis" -ForegroundColor Red
    Add-Result "L1-Infra" "Redis" "PING" "redis:6379" "FAIL" $_.Exception.Message
}
# PostgreSQL
try {
    $dbList = docker exec -e PGCLIENTENCODING=UTF8 jgsy-postgres psql -U postgres -t -c "SELECT count(*) FROM pg_database WHERE datistemplate = false;" 2>$null
    Write-Host "  [PASS] PostgreSQL ($($dbList.Trim()) databases)" -ForegroundColor Green
    Add-Result "L1-Infra" "PostgreSQL" "QUERY" "postgres:5432" "PASS" "$($dbList.Trim()) databases"
} catch {
    Write-Host "  [FAIL] PostgreSQL" -ForegroundColor Red
    Add-Result "L1-Infra" "PostgreSQL" "QUERY" "postgres:5432" "FAIL" $_.Exception.Message
}
# RabbitMQ
try {
    $r = Invoke-WebRequest -Uri "http://localhost:15672/api/overview" -Headers @{Authorization="Basic $([Convert]::ToBase64String([Text.Encoding]::ASCII.GetBytes('jgsy_admin:jgsy_rabbitmq_2024')))"} -UseBasicParsing -TimeoutSec 5
    Write-Host "  [PASS] RabbitMQ" -ForegroundColor Green
    Add-Result "L1-Infra" "RabbitMQ" "GET" "rabbitmq:15672" "PASS" "HTTP 200"
} catch {
    Write-Host "  [FAIL] RabbitMQ" -ForegroundColor Red
    Add-Result "L1-Infra" "RabbitMQ" "GET" "rabbitmq:15672" "FAIL" $_.Exception.Message
}

# ========== Layer 2: 全量 API 扫描 ==========
Write-Host "`n========== Layer 2: 全量 API 可达性扫描 ==========" -ForegroundColor Cyan
$token = Get-Token
$headers = @{ Authorization = "Bearer $token" }

$servicePorts = @{
    Tenant=8001; Identity=8002; Permission=8003; Observability=8005; Storage=8006;
    Account=8008; Analytics=8009; Charging=8010; Device=8011; DigitalTwin=8012;
    Ingestion=8013; Settlement=8014; Station=8015; WorkOrder=8016; ContentPlatform=8017;
    Blockchain=8021; EnergyCore=8022; EnergyServices=8026
}

# 网关路由映射：使用网关转发 (port 5000)
$totalEndpoints = 0; $pass2xx = 0; $pass4xx = 0; $fail5xx = 0; $failErr = 0

foreach ($svc in $servicePorts.GetEnumerator() | Sort-Object Value) {
    Write-Host "`n  扫描 $($svc.Key) (port $($svc.Value))..." -ForegroundColor Yellow
    
    # 获取 Swagger
    try {
        $swagger = Invoke-RestMethod -Uri "http://localhost:$($svc.Value)/swagger/v1/swagger.json" -TimeoutSec 10
    } catch {
        Write-Host "    [SKIP] Swagger 不可用" -ForegroundColor DarkYellow
        Add-Result "L2-APIScan" $svc.Key "GET" "/swagger" "SKIP" "Swagger unreachable"
        continue
    }
    
    $paths = $swagger.paths.PSObject.Properties
    $svcPass = 0; $svcFail = 0; $svcWarn = 0
    
    # 危险端点排除列表：这些端点会修改关键数据（密码、删除等）
    $dangerousPatterns = @(
        'reset-password', 'change-password', 'force-password',
        'delete-account', '/logout', '/revoke',
        '/clear$', '/purge$', '/wipe$'
    )
    
    foreach ($p in $paths) {
        $apiPath = $p.Name
        foreach ($m in $p.Value.PSObject.Properties) {
            $method = $m.Name.ToUpper()
            $totalEndpoints++
            
            # 跳过危险端点的变更操作
            if ($method -in @('POST','PUT','PATCH','DELETE')) {
                $isDangerous = $false
                foreach ($dp in $dangerousPatterns) {
                    if ($apiPath -match $dp) { $isDangerous = $true; break }
                }
                if ($isDangerous) {
                    $pass4xx++; $svcWarn++
                    Add-Result "L2-APIScan" $svc.Key $method $apiPath "SKIP-DANGER" "跳过危险端点"
                    continue
                }
            }
            
            # 替换路径参数为测试值
            $testPath = $apiPath -replace '\{id\}', '00000000-0000-0000-0000-000000000001'
            $testPath = $testPath -replace '\{[a-zA-Z]+Id\}', '00000000-0000-0000-0000-000000000001'
            $testPath = $testPath -replace '\{[a-zA-Z]+\}', 'test'
            
            $url = "http://localhost:$($svc.Value)$testPath"
            
            try {
                $params = @{
                    Uri = $url
                    Method = $method
                    Headers = $headers
                    UseBasicParsing = $true
                    TimeoutSec = 10
                }
                
                # POST/PUT 需要 body
                if ($method -in @('POST','PUT','PATCH')) {
                    $params.ContentType = "application/json"
                    $params.Body = '{}'
                }
                
                $resp = Invoke-WebRequest @params -ErrorAction Stop
                $code = $resp.StatusCode
                
                if ($code -lt 300) {
                    $svcPass++; $pass2xx++
                    Add-Result "L2-APIScan" $svc.Key $method $apiPath "PASS" "HTTP $code"
                } elseif ($code -lt 500) {
                    $svcWarn++; $pass4xx++
                    Add-Result "L2-APIScan" $svc.Key $method $apiPath "WARN" "HTTP $code"
                } else {
                    $svcFail++; $fail5xx++
                    Add-Result "L2-APIScan" $svc.Key $method $apiPath "FAIL" "HTTP $code"
                }
            } catch {
                $statusCode = 0
                if ($_.Exception.Response) {
                    $statusCode = [int]$_.Exception.Response.StatusCode
                }
                if ($statusCode -ge 400 -and $statusCode -lt 500) {
                    $svcWarn++; $pass4xx++
                    Add-Result "L2-APIScan" $svc.Key $method $apiPath "WARN" "HTTP $statusCode"
                } elseif ($statusCode -ge 500) {
                    $svcFail++; $fail5xx++
                    Add-Result "L2-APIScan" $svc.Key $method $apiPath "FAIL" "HTTP $statusCode"
                } else {
                    $failErr++
                    Add-Result "L2-APIScan" $svc.Key $method $apiPath "ERROR" $_.Exception.Message.Substring(0, [Math]::Min(200, $_.Exception.Message.Length))
                }
            }
        }
    }
    
    $svcColor = if ($svcFail -eq 0) {"Green"} else {"Red"}
    Write-Host "    $($svc.Key): $svcPass OK / $svcWarn 4xx / $svcFail 5xx (共 $($svcPass+$svcWarn+$svcFail) 端点)" -ForegroundColor $svcColor
}

# ========== 汇总 ==========
Write-Host "`n========== 扫描汇总 ==========" -ForegroundColor Cyan
Write-Host "  总端点数:    $totalEndpoints"
Write-Host "  2xx 成功:    $pass2xx" -ForegroundColor Green
Write-Host "  4xx 客户端:  $pass4xx" -ForegroundColor Yellow
Write-Host "  5xx 服务端:  $fail5xx" -ForegroundColor $(if($fail5xx -eq 0){"Green"}else{"Red"})
Write-Host "  连接错误:    $failErr" -ForegroundColor $(if($failErr -eq 0){"Green"}else{"Red"})

$fiveXXRate = if ($totalEndpoints -gt 0) { [math]::Round($fail5xx / $totalEndpoints * 100, 2) } else { 0 }
Write-Host "  5xx 错误率:  $fiveXXRate%" -ForegroundColor $(if($fiveXXRate -lt 1){"Green"}elseif($fiveXXRate -lt 5){"Yellow"}else{"Red"})

# 导出 CSV
$global:results | Export-Csv -Path $csvPath -NoTypeInformation -Encoding UTF8
Write-Host "`n  结果已导出: $csvPath" -ForegroundColor DarkGray

# 5xx 详情
if ($fail5xx -gt 0) {
    Write-Host "`n  === 5xx 错误详情 ===" -ForegroundColor Red
    $global:results | Where-Object { $_.Status -eq "FAIL" -and $_.Layer -eq "L2-APIScan" } | 
        Group-Object Service | ForEach-Object {
            Write-Host "  $($_.Name): $($_.Count) 个 5xx" -ForegroundColor Red
            $_.Group | Select-Object -First 5 | ForEach-Object {
                Write-Host "    $($_.Method) $($_.Path) => $($_.Detail)" -ForegroundColor DarkRed
            }
        }
}

Write-Host "`n========== Layer 1-2 完成 ==========" -ForegroundColor Cyan
return @{
    Total = $totalEndpoints
    Pass2xx = $pass2xx
    Pass4xx = $pass4xx
    Fail5xx = $fail5xx
    FailErr = $failErr
    FiveXXRate = $fiveXXRate
    HealthPass = $healthPass
    HealthFail = $healthFail
    CsvPath = $csvPath
    Results = $global:results
}
