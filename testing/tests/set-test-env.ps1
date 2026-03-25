<#
.SYNOPSIS
    统一设置六大测试工具的环境变量，将所有缓存和输出指向 D:\VSCode\cache\
.DESCRIPTION
    解决问题：浏览器二进制缓存、npm缓存、WebDriver缓存默认写入 C 盘 AppData，
    本机 C 盘仅剩 ~5 GB，必须全部重定向到 D 盘。
    
    与 scripts\migrate-vscode-to-d-drive.ps1 配合使用，统一缓存目录：
    D:\VSCode\cache\  ← 所有开发工具缓存统一根目录
    
    在 run-all-tests.ps1 或手动执行测试前，先 dot-source 本脚本：
      . .\tests\set-test-env.ps1
.NOTES
    缓存目录：D:\VSCode\cache\
    测试输出：D:\2026\aiops.v2\TestResults\（已有）
#>

$projectRoot = (Resolve-Path "$PSScriptRoot\..").Path
# 统一缓存根目录 — 与 migrate-vscode-to-d-drive.ps1 保持一致
$cacheRoot = "D:\VSCode\cache"

# ═══════════════════════════════════════════════════════════════
# 创建缓存目录结构
# ═══════════════════════════════════════════════════════════════
$dirs = @(
    $cacheRoot,
    (Join-Path $cacheRoot "cypress"),
    (Join-Path $cacheRoot "playwright"),
    (Join-Path $cacheRoot "puppeteer"),
    (Join-Path $cacheRoot "webdriver"),
    (Join-Path $cacheRoot "npm"),
    (Join-Path $cacheRoot "pip"),
    (Join-Path $cacheRoot "temp")
)
foreach ($d in $dirs) {
    if (-not (Test-Path $d)) {
        New-Item -ItemType Directory -Path $d -Force | Out-Null
    }
}

# ═══════════════════════════════════════════════════════════════
# Cypress — 二进制缓存（默认 C:\Users\xxx\AppData\Local\Cypress\Cache）
# ═══════════════════════════════════════════════════════════════
$env:CYPRESS_CACHE_FOLDER = Join-Path $cacheRoot "cypress"

# ═══════════════════════════════════════════════════════════════
# Playwright — 浏览器二进制（默认 C:\Users\xxx\AppData\Local\ms-playwright）
# ═══════════════════════════════════════════════════════════════
$env:PLAYWRIGHT_BROWSERS_PATH = Join-Path $cacheRoot "playwright"

# ═══════════════════════════════════════════════════════════════
# Puppeteer — Chromium 缓存（默认 C:\Users\xxx\.cache\puppeteer）
# ═══════════════════════════════════════════════════════════════
$env:PUPPETEER_CACHE_DIR = Join-Path $cacheRoot "puppeteer"

# ═══════════════════════════════════════════════════════════════
# Selenium WebDriver Manager — 驱动缓存（默认 C:\Users\xxx\.wdm）
# ═══════════════════════════════════════════════════════════════
$env:WDM_LOCAL = "1"
$env:WDM_LOG_LEVEL = "0"

# ═══════════════════════════════════════════════════════════════
# npm 缓存（默认 C:\Users\xxx\AppData\Roaming\npm-cache）
# ═══════════════════════════════════════════════════════════════
$env:npm_config_cache = Join-Path $cacheRoot "npm"

# ═══════════════════════════════════════════════════════════════
# pip 缓存（默认 C:\Users\xxx\AppData\Local\pip\Cache）
# ═══════════════════════════════════════════════════════════════
$env:PIP_CACHE_DIR = Join-Path $cacheRoot "pip"

# ═══════════════════════════════════════════════════════════════
# NuGet 包缓存（默认 C:\Users\xxx\.nuget\packages）
# ═══════════════════════════════════════════════════════════════
$env:NUGET_PACKAGES = Join-Path $cacheRoot "nuget"

# ═══════════════════════════════════════════════════════════════
# TEMP/TMP — 浏览器临时 profile 数据（默认 C:\Users\xxx\AppData\Local\Temp）
# 仅在测试执行期间重定向，不影响系统全局
# ═══════════════════════════════════════════════════════════════
$env:TEMP = Join-Path $cacheRoot "temp"
$env:TMP  = Join-Path $cacheRoot "temp"

# ═══════════════════════════════════════════════════════════════
# k6 — 确保结果输出在项目目录
# ═══════════════════════════════════════════════════════════════
$env:K6_OUT = "json=$projectRoot\k6\results\k6-output.json"

# 输出确认
Write-Host "  ✅ 测试环境变量已设置（全部指向 D:\VSCode\cache\）" -ForegroundColor Green
Write-Host "     CYPRESS_CACHE_FOLDER     = $env:CYPRESS_CACHE_FOLDER" -ForegroundColor Gray
Write-Host "     PLAYWRIGHT_BROWSERS_PATH = $env:PLAYWRIGHT_BROWSERS_PATH" -ForegroundColor Gray
Write-Host "     PUPPETEER_CACHE_DIR      = $env:PUPPETEER_CACHE_DIR" -ForegroundColor Gray
Write-Host "     npm_config_cache         = $env:npm_config_cache" -ForegroundColor Gray
Write-Host "     PIP_CACHE_DIR            = $env:PIP_CACHE_DIR" -ForegroundColor Gray
Write-Host "     NUGET_PACKAGES           = $env:NUGET_PACKAGES" -ForegroundColor Gray
Write-Host "     TEMP/TMP                 = $env:TEMP" -ForegroundColor Gray
