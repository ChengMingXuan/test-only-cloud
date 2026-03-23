function Coalesce($a, $b) { if ($null -ne $a) { $a } else { $b } }

function Get-SevenToolOrder {
    @("integration", "pytest", "cypress", "puppeteer", "selenium", "playwright", "k6")
}

function Get-SevenToolStaticCatalog {
    # ═══════════════════════════════════════════════════════════════════════════
    # 标准用例数基线（基于文件内实际用例计数，2026-03-23 锁定）
    # ───────────────────────────────────────────────────────────────────────────
    # 计数规则：
    #   integration : 统计 *Tests.cs 中 [Fact]/[Theory]/[Test] 特性数
    #   pytest      : 统计 test_*.py 中 def test_*() 函数数
    #   cypress     : 统计 *.cy.js 中 it() 调用数
    #   puppeteer   : 统计 *.test.js 中 it()/test() 调用数
    #   selenium    : 统计 test_*.py 中 def test_*() 函数数
    #   playwright  : 统计 *.spec.ts 中 test()/it() 调用数
    #   k6          : 统计 *.js 中 check() 调用数
    #
    # 标准用例 = 文件数 × 每文件平均用例数（从磁盘实际统计）
    # 后续迭代新增/删除测试文件后，重新运行统计更新基线
    # ═══════════════════════════════════════════════════════════════════════════
    [ordered]@{
        integration = [ordered]@{ name="integration"; display="集成测试"; displayName="集成测试（跨服务调用）"; icon="🔗"; standard=1999; group="跨服务集成"; filePattern="*Tests.cs"; countPattern="[Fact]/[Theory]/[Test]"; avgPerFile=16.3; desc="123 文件 × ~16.3 用例/文件（[Fact]/[Theory]/[Test] 测试方法）" }
        pytest     = [ordered]@{ name="pytest"; display="pytest"; displayName="pytest（API功能测试）"; icon="🐍"; standard=57774; group="API功能"; filePattern="test_*.py"; countPattern="def test_*()"; avgPerFile=368.0; desc="157 文件 × ~368 用例/文件（def test_ 测试函数）" }
        cypress    = [ordered]@{ name="cypress"; display="Cypress"; displayName="Cypress（组件交互测试）"; icon="🌲"; standard=9877; group="组件交互"; filePattern="*.cy.js"; countPattern="it()"; avgPerFile=60.6; desc="163 文件 × ~60.6 用例/文件（it() 测试用例）" }
        puppeteer  = [ordered]@{ name="puppeteer"; display="Puppeteer"; displayName="Puppeteer（渲染/性能）"; icon="🤖"; standard=8137; group="渲染性能"; filePattern="*.test.js"; countPattern="it()/test()"; avgPerFile=47.0; desc="173 文件 × ~47.0 用例/文件（it()/test() 测试用例）" }
        selenium   = [ordered]@{ name="selenium"; display="Selenium"; displayName="Selenium（浏览器兼容）"; icon="🌐"; standard=6540; group="浏览器兼容"; filePattern="test_*.py"; countPattern="def test_*()"; avgPerFile=45.4; desc="144 文件 × ~45.4 用例/文件（def test_ 测试函数）" }
        playwright = [ordered]@{ name="playwright"; display="Playwright"; displayName="Playwright（E2E端到端）"; icon="🎭"; standard=11093; group="E2E端到端"; filePattern="*.spec.ts"; countPattern="test()/it()"; avgPerFile=51.4; desc="216 文件 × ~51.4 用例/文件（test()/it() 测试用例）" }
        k6         = [ordered]@{ name="k6"; display="k6"; displayName="k6（性能压测）"; icon="⚡"; standard=3651; group="性能压测"; filePattern="*.js"; countPattern="check()"; avgPerFile=24.8; desc="147 文件 × ~24.8 检查点/文件（check() 调用）" }
    }
}

function Get-SevenToolBaselinePath {
    param([string]$RootDir = "")

    if (-not $RootDir) {
        $RootDir = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
    }

    Join-Path $RootDir "TestResults\baseline\seven-tool-baseline.json"
}

function Read-SevenToolBaseline {
    param([string]$RootDir = "")

    $path = Get-SevenToolBaselinePath -RootDir $RootDir
    if (-not (Test-Path $path)) { return $null }

    try {
        Get-Content $path -Raw -Encoding UTF8 | ConvertFrom-Json
    } catch {
        $null
    }
}

function Read-SevenToolReportJson {
    param(
        [string]$RootDir = "",
        [string]$Tool = ""
    )

    if (-not $RootDir) {
        $RootDir = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
    }

    if (-not $Tool) {
        return $null
    }

    $path = Join-Path $RootDir "TestResults\reports\$Tool-report.json"
    if (-not (Test-Path $path)) { return $null }

    try {
        Get-Content $path -Raw -Encoding UTF8 | ConvertFrom-Json
    } catch {
        $null
    }
}

function Get-SevenToolBaselineHealth {
    param(
        [string]$RootDir = "",
        [string]$Tool = "",
        $BaselineTool = $null
    )

    if (-not $RootDir) {
        $RootDir = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
    }

    if (-not $Tool) {
        return [ordered]@{
            isHealthy = $false
            reason = "missing-tool-name"
            entryCount = 0
            nonZeroEntries = 0
            entryCoverage = 0
            reportFileCount = 0
            reportCoverage = 0
        }
    }

    if ($null -eq $BaselineTool) {
        $baseline = Read-SevenToolBaseline -RootDir $RootDir
        if ($null -eq $baseline -or $null -eq $baseline.tools) {
            return [ordered]@{
                isHealthy = $false
                reason = "missing-baseline"
                entryCount = 0
                nonZeroEntries = 0
                entryCoverage = 0
                reportFileCount = 0
                reportCoverage = 0
            }
        }
        $BaselineTool = $baseline.tools.$Tool
    }

    if ($null -eq $BaselineTool) {
        return [ordered]@{
            isHealthy = $false
            reason = "missing-tool"
            entryCount = 0
            nonZeroEntries = 0
            entryCoverage = 0
            reportFileCount = 0
            reportCoverage = 0
        }
    }

    $entries = @($BaselineTool.entries)
    $entryCount = $entries.Count
    $nonZeroEntries = @($entries | Where-Object { [int]$_.tests -gt 0 }).Count
    $entryCoverage = if ($entryCount -gt 0) { [math]::Round(($nonZeroEntries * 100.0 / $entryCount), 1) } else { 0 }

    $report = Read-SevenToolReportJson -RootDir $RootDir -Tool $Tool
    $reportFileCount = 0
    if ($null -ne $report -and $null -ne $report.fileCount) {
        $reportFileCount = [int]$report.fileCount
    }
    $reportCoverage = if ($entryCount -gt 0) { [math]::Round(($reportFileCount * 100.0 / $entryCount), 1) } else { 0 }

    $isHealthy = ([int]$BaselineTool.standardCases -gt 0) -and (
        ($entryCoverage -ge 70) -or
        ($reportCoverage -ge 70 -and $nonZeroEntries -gt 0)
    )

    $reason = if ($isHealthy) { "ok" } elseif ([int]$BaselineTool.standardCases -le 0) { "non-positive-standard" } elseif ($nonZeroEntries -le 0) { "no-nonzero-entries" } else { "low-coverage" }

    [ordered]@{
        isHealthy = $isHealthy
        reason = $reason
        entryCount = $entryCount
        nonZeroEntries = $nonZeroEntries
        entryCoverage = $entryCoverage
        reportFileCount = $reportFileCount
        reportCoverage = $reportCoverage
    }
}

function Get-SevenToolCatalog {
    param([string]$RootDir = "")

    if (-not $RootDir) {
        $RootDir = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
    }

    $catalog = Get-SevenToolStaticCatalog
    $baseline = Read-SevenToolBaseline -RootDir $RootDir
    if ($null -eq $baseline -or $null -eq $baseline.tools) {
        return $catalog
    }

    foreach ($tool in $catalog.Keys) {
        $baselineTool = $baseline.tools.$tool
        $health = Get-SevenToolBaselineHealth -RootDir $RootDir -Tool $tool -BaselineTool $baselineTool
        if ($null -ne $baselineTool -and [bool]$health.isHealthy) {
            $catalog[$tool].standard = [int]$baselineTool.standardCases
        }
    }

    $catalog
}

function Get-SevenToolStandardCases {
    param([string]$RootDir = "")

    $catalog = Get-SevenToolCatalog -RootDir $RootDir
    $cases = @{}
    foreach ($tool in $catalog.Keys) {
        $cases[$tool] = [int]$catalog[$tool].standard
    }
    $cases
}

function Get-SevenToolTotalStandard {
    param([string]$RootDir = "")

    $total = 0
    foreach ($item in (Get-SevenToolCatalog -RootDir $RootDir).Values) {
        $total += [int]$item.standard
    }
    $total
}

function Get-SevenToolBaseDir {
    param(
        [string]$RootDir,
        [string]$Tool
    )

    $testsDir = Join-Path $RootDir "testing\tests"

    switch ($Tool) {
        "integration" { Join-Path $RootDir "testing\JGSY.AGI.Test" }
        "pytest"      { $testsDir }
        "cypress"     { Join-Path $testsDir "cypress-tests\e2e" }
        "puppeteer"   { Join-Path $testsDir "puppeteer-tests\tests" }
        "selenium"    { Join-Path $testsDir "selenium-tests\tests" }
        "playwright"  { Join-Path $testsDir "playwright-tests\tests" }
        "k6"          { Join-Path $RootDir "testing\k6\scenarios" }
        default        { $RootDir }
    }
}

function Get-SevenToolFiles {
    param(
        [string]$RootDir,
        [string]$Tool
    )

    $testsDir = Join-Path $RootDir "testing\tests"
    $baseDir = Get-SevenToolBaseDir -RootDir $RootDir -Tool $Tool
    $files = @()

    switch ($Tool) {
        "integration" {
            $files = @(Get-ChildItem $baseDir -Filter "*Tests.cs" -Recurse -ErrorAction SilentlyContinue |
                Where-Object { $_.FullName -notmatch 'bin|obj' })
        }
        "pytest" {
            $pytestDirs = @(
                (Join-Path $testsDir "api"),
                (Join-Path $testsDir "automated"),
                (Join-Path $testsDir "test-automation"),
                (Join-Path $testsDir "security"),
                (Join-Path $testsDir "blockchain")
            )
            foreach ($dir in $pytestDirs) {
                if (-not (Test-Path $dir)) { continue }
                $files += @(Get-ChildItem $dir -Filter "test_*.py" -Recurse -ErrorAction SilentlyContinue |
                    Where-Object { $_.FullName -notmatch '__pycache__' })
            }
        }
        "cypress" {
            $files = @(Get-ChildItem $baseDir -Filter "*.cy.js" -Recurse -ErrorAction SilentlyContinue)
        }
        "puppeteer" {
            $files = @(Get-ChildItem $baseDir -Filter "*.test.js" -Recurse -ErrorAction SilentlyContinue)
        }
        "selenium" {
            $files = @(Get-ChildItem $baseDir -Filter "test_*.py" -Recurse -ErrorAction SilentlyContinue |
                Where-Object { $_.FullName -notmatch '__pycache__' -and $_.FullName -notmatch 'venv' })
        }
        "playwright" {
            $files = @(Get-ChildItem $baseDir -Filter "*.spec.ts" -Recurse -ErrorAction SilentlyContinue)
        }
        "k6" {
            $files = @(Get-ChildItem $baseDir -Filter "*.js" -Recurse -ErrorAction SilentlyContinue)
        }
    }

    @($files |
        Sort-Object FullName |
        ForEach-Object {
            $_.FullName.Replace("$baseDir\", "").Replace("$baseDir/", "").Replace("\", "/")
        })
}

function Get-SevenToolFileCount {
    param(
        [string]$RootDir,
        [string]$Tool
    )

    @(Get-SevenToolFiles -RootDir $RootDir -Tool $Tool).Count
}

function Get-SevenToolAtomicResultPath {
    param(
        [string]$RootDir,
        [string]$Tool,
        [string]$RelPath
    )

    $safe = ($RelPath -replace '[\\/:*?"<>|]','_') -replace '\s+','_'
    Join-Path $RootDir "TestResults\atomic\$Tool\$safe.json"
}

function Read-SevenToolAtomicResult {
    param(
        [string]$RootDir,
        [string]$Tool,
        [string]$RelPath
    )

    $path = Get-SevenToolAtomicResultPath -RootDir $RootDir -Tool $Tool -RelPath $RelPath
    if (-not (Test-Path $path)) { return $null }

    try {
        Get-Content $path -Raw -Encoding UTF8 | ConvertFrom-Json
    } catch {
        $null
    }
}

function Read-SevenToolHistoryEntries {
    param([string]$Path)

    $historyList = New-Object System.Collections.ArrayList
    if (Test-Path $Path) {
        try {
            $raw = Get-Content $Path -Raw -Encoding UTF8 | ConvertFrom-Json
            foreach ($item in @($raw)) {
                if ($item.PSObject.Properties.Name -contains 'value') {
                    foreach ($inner in @($item.value)) { [void]$historyList.Add($inner) }
                } elseif ($item.PSObject.Properties.Name -contains 'timestamp') {
                    [void]$historyList.Add($item)
                }
            }
        } catch {}
    }

    @($historyList)
}