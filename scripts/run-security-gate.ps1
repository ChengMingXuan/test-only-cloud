<#
.SYNOPSIS
    安全测试门禁脚本 - IMP-P0-006 实现
.DESCRIPTION
    运行 testing/tests/security/ 下的全部安全测试并生成门禁结果。
    覆盖 OWASP Top 10、HTTP 安全头、TLS、CSRF、审计日志完整性。
.PARAMETER BaseUrl
    被测服务的根地址
.PARAMETER OutputPath
    结果输出路径
.PARAMETER Quick
    快速模式，仅执行关键用例
#>
param(
    [string]$BaseUrl = 'http://localhost:5000',
    [string]$OutputPath = 'TestResults/reports/security-gate-report.json',
    [switch]$Quick
)

$ErrorActionPreference = 'Continue'
$startTime = Get-Date
$securityDir = Join-Path $PSScriptRoot '..' 'tests' 'security'

Write-Host "`n=============================" -ForegroundColor Cyan
Write-Host "  安全测试门禁" -ForegroundColor Cyan
Write-Host "  目标: $BaseUrl" -ForegroundColor Cyan
Write-Host "=============================" -ForegroundColor Cyan

# 检查 pytest 环境
$pythonCmd = Get-Command python -ErrorAction SilentlyContinue
if (-not $pythonCmd) {
    $pythonCmd = Get-Command python3 -ErrorAction SilentlyContinue
}
if (-not $pythonCmd) {
    Write-Host "❌ Python 未安装" -ForegroundColor Red
    exit 1
}

# 检查安全测试目录
if (-not (Test-Path $securityDir)) {
    Write-Host "❌ 安全测试目录不存在: $securityDir" -ForegroundColor Red
    exit 1
}

$testFiles = Get-ChildItem $securityDir -Filter 'test_*.py' | Sort-Object Name
Write-Host "  发现 $($testFiles.Count) 个安全测试文件" -ForegroundColor White

# 定义测试分类
$categories = @{
    'test_http_security_headers.py' = 'HTTP安全头'
    'test_tls_and_crypto.py'        = 'TLS/加密'
    'test_csrf_protection.py'       = 'CSRF防护'
    'test_audit_log_integrity.py'   = '审计日志完整性'
    'test_owasp_comprehensive.py'   = 'OWASP综合'
    'test_auth_bypass.py'           = '认证绕过'
    'test_sql_injection.py'         = 'SQL注入'
    'test_xss_protection.py'        = 'XSS防护'
    'test_rate_limiting.py'         = '速率限制'
    'test_cors_policy.py'           = 'CORS策略'
    'test_token_security.py'        = 'Token安全'
    'test_input_validation.py'      = '输入验证'
    'test_dependency_vulnerabilities.py' = '依赖漏洞'
    'test_error_handling.py'        = '错误处理'
    'test_session_management.py'    = '会话管理'
}

# 运行测试
$results = @()
$totalPassed = 0
$totalFailed = 0
$totalErrors = 0

foreach ($file in $testFiles) {
    $category = if ($categories.ContainsKey($file.Name)) { $categories[$file.Name] } else { $file.BaseName }
    Write-Host "  🔒 $category ($($file.Name))..." -NoNewline

    $junitFile = Join-Path $env:TEMP "security-$($file.BaseName).xml"
    $testResult = & python -m pytest $file.FullName `
        --tb=short `
        --no-header `
        -q `
        --junitxml=$junitFile `
        -x `
        2>&1

    $exitCode = $LASTEXITCODE

    # 解析结果
    $passed = 0
    $failed = 0
    $errors = 0
    if (Test-Path $junitFile) {
        try {
            [xml]$junit = Get-Content $junitFile
            $suite = $junit.testsuites.testsuite
            if (-not $suite) { $suite = $junit.testsuite }
            if ($suite) {
                $passed = [int]$suite.tests - [int]$suite.failures - [int]$suite.errors
                $failed = [int]$suite.failures
                $errors = [int]$suite.errors
            }
        } catch {}
        Remove-Item $junitFile -Force -ErrorAction SilentlyContinue
    }

    $status = if ($exitCode -eq 0) { 'PASS' } elseif ($exitCode -eq 5) { 'SKIP' } else { 'FAIL' }

    $results += [PSCustomObject]@{
        File     = $file.Name
        Category = $category
        Status   = $status
        Passed   = $passed
        Failed   = $failed
        Errors   = $errors
    }

    $totalPassed += $passed
    $totalFailed += $failed
    $totalErrors += $errors

    switch ($status) {
        'PASS' { Write-Host " ✅ ($passed 通过)" -ForegroundColor Green }
        'SKIP' { Write-Host " ⏭️ (无用例)" -ForegroundColor Yellow }
        'FAIL' { Write-Host " ❌ (失败 $failed, 错误 $errors)" -ForegroundColor Red }
    }
}

$endTime = Get-Date
$duration = ($endTime - $startTime).TotalSeconds

# 门禁结论
$gateStatus = if ($totalFailed -eq 0 -and $totalErrors -eq 0) { 'PASS' } else { 'FAIL' }

# 生成 JSON 报告
$outputDir = Split-Path $OutputPath
if ($outputDir -and -not (Test-Path $outputDir)) { New-Item -ItemType Directory -Path $outputDir -Force | Out-Null }

$report = @{
    tool      = 'security'
    timestamp = (Get-Date -Format 'yyyy-MM-ddTHH:mm:ss')
    duration  = [math]::Round($duration, 1)
    summary   = @{
        total  = $totalPassed + $totalFailed + $totalErrors
        passed = $totalPassed
        failed = $totalFailed
        errors = $totalErrors
        files  = $testFiles.Count
        status = $gateStatus
    }
    details   = $results | ForEach-Object {
        @{
            file     = $_.File
            category = $_.Category
            status   = $_.Status
            passed   = $_.Passed
            failed   = $_.Failed
            errors   = $_.Errors
        }
    }
} | ConvertTo-Json -Depth 4

Set-Content -Path $OutputPath -Value $report -Encoding UTF8

Write-Host "`n=============================" -ForegroundColor Cyan
Write-Host "  安全测试门禁结果: $gateStatus" -ForegroundColor $(if ($gateStatus -eq 'PASS') { 'Green' } else { 'Red' })
Write-Host "  通过: $totalPassed | 失败: $totalFailed | 错误: $totalErrors" -ForegroundColor White
Write-Host "  报告: $OutputPath" -ForegroundColor White
Write-Host "=============================" -ForegroundColor Cyan

exit $(if ($gateStatus -eq 'PASS') { 0 } else { 1 })
