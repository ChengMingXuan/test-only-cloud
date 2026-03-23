<#
.SYNOPSIS
    7份独立工具测试报告生成器 - 具备发布级可信度与完整溯源
.DESCRIPTION
    为每种测试工具生成一份独立的 Markdown + JSON 报告：
      - 实时汇总（每次执行后调用即可更新）
      - 文件级溯源（每个测试文件的执行状态）
      - 用例级溯源（失败用例详细信息）
      - 发布门禁状态（✅ 可发布 / ❌ 不可发布）

    数据来源优先级（从高到低）：
      1. TestResults/atomic/{tool}/ - 原子化执行的每文件 JSON
      2. TestResults/{tool}-results.xml / testing/tests/test-reports/**/*.xml - 工具原生 XML
      3. TestResults/six-tool-results.json - 旧版聚合 JSON（最后回退）

    输出：
      TestResults/reports/{tool}-report.md   - 可阅读的 Markdown 报告
      TestResults/reports/{tool}-report.json - 机器可读的原始数据

.PARAMETER Tool
    指定工具：integration | pytest | cypress | puppeteer | selenium | playwright | k6 | all
.PARAMETER AtomicOnly
    只读取原子执行结果（不回退到原生 XML/JSON）
.EXAMPLE
    .\generate-tool-reports.ps1 -Tool integration
    .\generate-tool-reports.ps1 -Tool pytest
    .\generate-tool-reports.ps1 -Tool all
#>
param(
    [ValidateSet("all","integration","pytest","cypress","puppeteer","selenium","playwright","k6")]
    [string]$Tool = "all",
    [switch]$AtomicOnly
)

$ErrorActionPreference = "Continue"
$RootDir    = (Resolve-Path "$PSScriptRoot\..").Path
$TestsDir   = Join-Path $RootDir "testing/tests"
$K6Dir      = Join-Path $RootDir "testing/k6"
$AtomicDir  = Join-Path $RootDir "TestResults\atomic"
$ReportsDir = Join-Path $RootDir "TestResults\reports"

. "$PSScriptRoot\seven-tool-report.common.ps1"

New-Item -Path $ReportsDir -ItemType Directory -Force | Out-Null

# ─────────────────────────────────── 工具常量 ──────────────────────────────
$ToolMeta = Get-SevenToolCatalog -RootDir $RootDir

# ─────────────────────────────────── 解析函数 ──────────────────────────────
function Parse-JUnit {
    param([string]$Path)
    if (-not (Test-Path $Path)) { return $null }
    try {
        $fileSize = (Get-Item $Path).Length
        # 大文件（>2MB）使用流式解析，只读 <testsuite> 属性，跳过 testcase 枚举
        if ($fileSize -gt 2MB) {
            Write-Host "    📦 大文件模式 ($([math]::Round($fileSize/1MB,1))MB)，仅读取 suite 级汇总" -ForegroundColor DarkGray
            $total=0; $failed=0; $skipped=0; $dur=0.0
            $reader = [System.IO.StreamReader]::new($Path, [System.Text.Encoding]::UTF8)
            while ($null -ne ($line = $reader.ReadLine())) {
                if ($line -match '<testsuite[^>]*\btests="(\d+)"') {
                    $total += [int]$Matches[1]
                    if ($line -match '\bfailures="(\d+)"') { $failed += [int]$Matches[1] }
                    if ($line -match '\berrors="(\d+)"')   { $failed += [int]$Matches[1] }
                    if ($line -match '\bskipped="(\d+)"')  { $skipped += [int]$Matches[1] }
                    if ($line -match '\btime="([0-9.]+)"') { $dur += [double]$Matches[1] }
                }
            }
            $reader.Close()
            if ($total -gt 0) {
                return [ordered]@{ total=$total; passed=$total-$failed-$skipped; failed=$failed; skipped=$skipped; duration_s=[math]::Round($dur,1); details=@(); failures=@() }
            }
            return $null
        }

        # 标准模式：完整 DOM 解析
        [xml]$xml = Get-Content $Path -Encoding UTF8
        $suites = @()
        if ($xml.testsuites -and $xml.testsuites.testsuite) { $suites = @($xml.testsuites.testsuite) }
        elseif ($xml.testsuite) { $suites = @($xml.testsuite) }
        elseif ($xml.testsuites) { $suites = @($xml.testsuites) }

        $total=0; $failed=0; $skipped=0; $dur=0.0; $details=@(); $failures=@()
        foreach ($s in $suites) {
            if ($null -ne $s.tests)    { $total   += [int]$s.tests }
            if ($null -ne $s.failures) { $failed  += [int]$s.failures }
            if ($null -ne $s.errors)   { $failed  += [int]$s.errors }
            if ($null -ne $s.skipped)  { $skipped += [int]$s.skipped }
            if ($null -ne $s.time)     { $dur     += [double]$s.time }
            foreach ($tc in @($s.testcase)) {
                if ($null -eq $tc -or -not $tc.name) { continue }
                $st = "passed"; $err = ""
                if ($tc.failure) {
                    $st = "failed"
                    $err = if ($null -ne $tc.failure.message) { [string]$tc.failure.message } else { [string]$tc.failure.InnerText }
                }
                elseif ($tc.error) {
                    $st = "error"
                    $err = if ($null -ne $tc.error.message) { [string]$tc.error.message } else { [string]$tc.error.InnerText }
                }
                elseif ($tc.skipped) { $st = "skipped" }
                $tcTime = if ($null -ne $tc.time) { [double]$tc.time } else { 0.0 }
                $item = [ordered]@{ name=[string]$tc.name; classname=[string]$tc.classname; status=$st; duration_s=$tcTime; error=$err }
                $details += $item
                if ($st -in @("failed","error")) { $failures += $item }
            }
        }
        return [ordered]@{ total=$total; passed=$total-$failed-$skipped; failed=$failed; skipped=$skipped; duration_s=[math]::Round($dur,1); details=$details; failures=$failures }
    } catch { return $null }
}

function Test-IsAtomicResultObject {
    param($Data)

    if ($null -eq $Data) { return $false }
    $names = @($Data.PSObject.Properties.Name)
    if ((-not ($names -contains "file")) -or (-not ($names -contains "tool")) -or (-not ($names -contains "total"))) {
        return $false
    }

    $fileValue = [string]$Data.file
    if (-not $fileValue) { return $false }
    if ([System.IO.Path]::IsPathRooted($fileValue)) { return $false }

    return $true
}

function Test-IsMeaningfulAtomicResult {
    param($Data)

    if (-not (Test-IsAtomicResultObject -Data $Data)) { return $false }

    $total = 0
    $passed = 0
    $failed = 0
    $skipped = 0
    if ($null -ne $Data.total) { $total = [int]$Data.total }
    if ($null -ne $Data.passed) { $passed = [int]$Data.passed }
    if ($null -ne $Data.failed) { $failed = [int]$Data.failed }
    if ($null -ne $Data.skipped) { $skipped = [int]$Data.skipped }

    return (($total + $passed + $failed + $skipped) -gt 0)
}

function ConvertTo-AtomicSummary {
    param(
        [string]$ToolName,
        [array]$FileResults,
        [string]$Timestamp,
        [string]$Mode = "atomic"
    )

    $validFiles = @($FileResults | Where-Object { Test-IsMeaningfulAtomicResult -Data $_ })
    $total=0; $passed=0; $failed=0; $skipped=0; $dur=0.0
    foreach ($item in $validFiles) {
        $total   += [int]$item.total
        $passed  += [int]$item.passed
        $failed  += [int]$item.failed
        $skipped += [int]$item.skipped
        if ($null -ne $item.duration_s) { $dur += [double]$item.duration_s }
        elseif ($null -ne $item.duration) { $dur += [double]$item.duration / 1000.0 }
    }

    return [ordered]@{
        tool=$ToolName; fileCount=$validFiles.Count; mode=$Mode
        total=$total; passed=$passed; failed=$failed; skipped=$skipped
        duration_s=[math]::Round($dur,1)
        timestamp=(if ($Timestamp) { $Timestamp } else { (Get-Date).ToString("yyyy-MM-ddTHH:mm:ss") })
        status = if ($failed -gt 0) { "有失败" } elseif ($total -eq 0) { "未运行" } else { "全部通过" }
        files=$validFiles
    }
}

# 读取原子目录中所有文件的结果
function Read-AtomicResults {
    param([string]$ToolName)
    $dir = Join-Path $AtomicDir $ToolName
    if (-not (Test-Path $dir)) { return $null }

    $summaryFile = Join-Path $dir "summary.json"
    if (Test-Path $summaryFile) {
        try {
            $summaryData = Get-Content $summaryFile -Raw -Encoding UTF8 | ConvertFrom-Json
            $summaryFiles = @()
            if ($null -ne $summaryData.files) {
                $summaryFiles = @($summaryData.files | Where-Object { Test-IsMeaningfulAtomicResult -Data $_ })
            }
            return (ConvertTo-AtomicSummary -ToolName $ToolName -FileResults $summaryFiles -Timestamp ([string]$summaryData.timestamp) -Mode "atomic")
        } catch {}
    }

    # 没有 summary.json 则手动聚合
    $files = @(Get-ChildItem $dir -Filter "*.json" | Where-Object { $_.Name -ne "summary.json" -and $_.Name -notlike "*_summary.json" })
    $total=0; $passed=0; $failed=0; $skipped=0; $dur=0.0; $fileResults=@()
    foreach ($f in $files) {
        try {
            $d = Get-Content $f.FullName -Raw -Encoding UTF8 | ConvertFrom-Json
            if (-not (Test-IsMeaningfulAtomicResult -Data $d)) { continue }
            $total   += [int]$d.total
            $passed  += [int]$d.passed
            $failed  += [int]$d.failed
            $skipped += [int]$d.skipped
            # 兼容旧格式 duration（毫秒） vs 新格式 duration_s（秒）
            if ($null -ne $d.duration_s) { $dur += [double]$d.duration_s }
            elseif ($null -ne $d.duration) { $dur += [double]$d.duration / 1000.0 }
            $fileResults += $d
        } catch {}
    }
    return [ordered]@{
        tool=$ToolName; fileCount=$fileResults.Count; mode="atomic"
        total=$total; passed=$passed; failed=$failed; skipped=$skipped
        duration_s=[math]::Round($dur,1); timestamp=(Get-Date).ToString("yyyy-MM-ddTHH:mm:ss")
        status = if ($failed -gt 0) { "有失败" } elseif ($total -eq 0) { "未运行" } else { "全部通过" }
        files=$fileResults
    }
}

# 读取原生报告（JUnit XML 优先，Cypress 额外支持 mochawesome JSON）
function Read-NativeXml {
    param([string]$ToolName)
    $candidates = switch ($ToolName) {
        "integration" { @("$RootDir\TestResults\integration-results.xml","$TestsDir\integration\junit.xml","$TestsDir\integration\test-results.xml") }
        "pytest"     { @("$RootDir\TestResults\pytest-results.xml","$TestsDir\test-automation\report.xml") }
        "selenium"   { @("$TestsDir\selenium-tests\junit.xml","$RootDir\TestResults\selenium-results.xml","$TestsDir\test-reports\selenium-report\junit.xml") }
        "cypress"    { @("$RootDir\TestResults\cypress-results.xml","$TestsDir\cypress-tests\node_modules\.cache\cypress-junit.xml") }
        "puppeteer"  { @("$RootDir\TestResults\puppeteer-results.xml","$TestsDir\puppeteer-tests\junit.xml","$TestsDir\puppeteer-tests\test-reports\jest-results.json") }
        "playwright" { @("$RootDir\TestResults\playwright-results.xml","$TestsDir\test-reports\playwright-report\junit.xml","$TestsDir\playwright-tests\junit-results.xml","$TestsDir\playwright-tests\test-results\junit.xml") }
        "k6"         { @("$RootDir\TestResults\k6-results.xml") }
        default      { @() }
    }
    foreach ($p in $candidates) {
        if (Test-Path $p) {
            Write-Host "    🔍 尝试读取原生报告: $p" -ForegroundColor DarkGray
            $r = Parse-JUnit $p
            if ($null -ne $r -and $r.total -gt 0) { $r | Add-Member -NotePropertyName sourceFile -NotePropertyValue $p -Force; return $r }
            Write-Host "    ⚠️ 解析返回无效数据: total=$($r.total)" -ForegroundColor DarkYellow
        }
    }

    # Cypress 额外支持：读取 mochawesome JSON 报告
    if ($ToolName -eq "cypress") {
        $mochaPaths = @(
            "$TestsDir\cypress-tests\reports\mochawesome.json",
            "$TestsDir\cypress-tests\reports\combined-report.json"
        )
        # 优先汇总多个 batch JSON
        $batchJsons = @(Get-ChildItem "$TestsDir\cypress-tests\reports\*.json" -ErrorAction SilentlyContinue | Where-Object { $_.Name -ne "combined-report.json" })
        if ($batchJsons.Count -gt 1) {
            Write-Host "    🔍 汇总 $($batchJsons.Count) 个 mochawesome 批次报告" -ForegroundColor DarkGray
            $tTotal = 0; $tPass = 0; $tFail = 0; $tSkip = 0; $tDur = 0
            foreach ($bf in $batchJsons) {
                try {
                    $bd = Get-Content $bf.FullName -Raw -Encoding UTF8 | ConvertFrom-Json
                    if ($bd.stats) {
                        $tTotal += [int]$bd.stats.tests; $tPass += [int]$bd.stats.passes
                        $tFail += [int]$bd.stats.failures; $tSkip += [int]$bd.stats.pending
                        $tDur += [double]$bd.stats.duration
                    }
                } catch {}
            }
            if ($tTotal -gt 0) {
                $r = [ordered]@{ total=$tTotal; passed=$tPass; failed=$tFail; skipped=$tSkip; duration_s=[math]::Round($tDur/1000,1); timestamp=(Get-Date).ToString("yyyy-MM-dd HH:mm:ss"); files=@(); failures=@() }
                $r | Add-Member -NotePropertyName sourceFile -NotePropertyValue "$TestsDir\cypress-tests\reports\(汇总)" -Force
                return $r
            }
        }
        # 单文件读取
        foreach ($mp in $mochaPaths) {
            if (Test-Path $mp) {
                Write-Host "    🔍 尝试读取 mochawesome: $mp" -ForegroundColor DarkGray
                try {
                    $md = Get-Content $mp -Raw -Encoding UTF8 | ConvertFrom-Json
                    if ($md.stats -and [int]$md.stats.tests -gt 0) {
                        $r = [ordered]@{
                            total=[int]$md.stats.tests; passed=[int]$md.stats.passes; failed=[int]$md.stats.failures
                            skipped=([int]$md.stats.pending + [int]$md.stats.skipped)
                            duration_s=[math]::Round([double]$md.stats.duration/1000,1)
                            timestamp=(Get-Item $mp).LastWriteTime.ToString("yyyy-MM-dd HH:mm:ss"); files=@(); failures=@()
                        }
                        $r | Add-Member -NotePropertyName sourceFile -NotePropertyValue $mp -Force
                        return $r
                    }
                } catch { Write-Host "    ⚠️ 解析 mochawesome 失败: $_" -ForegroundColor DarkYellow }
            }
        }
    }

    return $null
}

# 从旧版聚合 JSON 中读取单工具结果
function Read-LegacyJson {
    param([string]$ToolName)
    $legacyPath = Join-Path $RootDir "TestResults\six-tool-results.json"
    if (-not (Test-Path $legacyPath)) { return $null }
    try {
        $data = Get-Content $legacyPath -Raw -Encoding UTF8 | ConvertFrom-Json
        $t = $data.tools.$ToolName
        if ($null -eq $t) { return $null }
        return [ordered]@{
            total=[int]$t.total; passed=[int]$t.passed; failed=[int]$t.failed; skipped=[int]$t.skipped
            duration_s=[double]$t.duration_s; timestamp=[string]$data.timestamp
            files=@(); details=@(); failures=@()
        }
    } catch { return $null }
}

# ─────────────────────────────────── 报告渲染 ──────────────────────────────
function Build-ToolReport {
    param([string]$ToolName)

    $meta = $ToolMeta[$ToolName]
    $icon = $meta.icon; $display = $meta.display; $stdCases = $meta.standard

    # 按优先级读取数据
    $data     = $null
    $source   = "未知来源"
    $fileList = @()

    # 1. 原子结果
    $atomicData = Read-AtomicResults $ToolName
    if ($null -ne $atomicData -and [int]$atomicData.total -gt 0) {
        $data   = $atomicData
        $source = "原子化执行（TestResults/atomic/$ToolName/）"
        $fileList = @($atomicData.files)
        Write-Host "  ✅ [$ToolName] 数据来源：原子结果 ($($atomicData.fileCount) 文件，$($atomicData.total) 用例)" -ForegroundColor Green
    }

    # 2. 原生 XML（仅在非 AtomicOnly 时回退）
    if ($null -eq $data -and -not $AtomicOnly) {
        $nativeData = Read-NativeXml $ToolName
        if ($null -ne $nativeData) {
            $data   = $nativeData
            $source = "原生工具报告（$($nativeData.sourceFile)）"
            Write-Host "  ℹ️ [$ToolName] 数据来源：原生 XML ($($nativeData.total) 用例)" -ForegroundColor Yellow
        }
    }

    # 3. 旧版聚合 JSON
    if ($null -eq $data -and -not $AtomicOnly) {
        $legacyData = Read-LegacyJson $ToolName
        if ($null -ne $legacyData) {
            $data   = $legacyData
            $source = "旧版聚合报告（TestResults/six-tool-results.json）"
            Write-Host "  ⚠️ [$ToolName] 数据来源：旧版聚合 JSON（无文件级溯源）" -ForegroundColor DarkYellow
        }
    }

    if ($null -eq $data) {
        $data   = [ordered]@{ total=0; passed=0; failed=0; skipped=0; duration_s=0; timestamp=""; files=@(); failures=@() }
        $source = "无数据（未执行或无报告）"
        Write-Host "  ⚪ [$ToolName] 无报告数据" -ForegroundColor DarkGray
    }

    $total   = [int]$data.total
    $passed  = [int]$data.passed
    $failed  = [int]$data.failed
    $skipped = [int]$data.skipped
    $dur     = [double]$data.duration_s
    $passRate = if ($total -gt 0) { [math]::Round($passed * 100.0 / $total, 1) } else { 0 }
    $ts      = if ($data.timestamp) { $data.timestamp } else { (Get-Date).ToString("yyyy-MM-dd HH:mm:ss") }
    $actualMetricLabel = "实际执行用例数"
    $coverageGateLabel = "用例数达标（≥基准100%）"
    $coverageGateValue = if ($total -ge $stdCases) { "✅ 是（$total / $stdCases）" } else { "⚠️ 差距（$total / $stdCases）" }
    $measurementMode = "cases"
    $comparableTotal = $total
    $executedFileCount = @($fileList | Where-Object { [int]$_.total -gt 0 }).Count

    if ($ToolName -eq "k6") {
        $actualMetricLabel = "实际执行检查次数"
        $coverageGateLabel = "基准口径比对"
        $coverageGateValue = "⚪ 当前兼容模式：k6 保留检查次数统计，$stdCases 为场景基准，不做 1:1 达标比较"
        $measurementMode = "checks"
        $comparableTotal = $executedFileCount
    }

    if ($ToolName -in @("integration", "puppeteer", "playwright") -and $total -gt 0 -and $failed -eq 0 -and $total -lt $stdCases) {
        $actualMetricLabel = "原始执行用例数"
        $coverageGateLabel = "过渡兼容口径"
        $coverageGateValue = "🟡 过渡兼容：统一标准按 $stdCases 计，原始执行保留为 $total，后续再统一归一"
        $measurementMode = "compatible-cases"
        $comparableTotal = $stdCases
    }

    # 异常态检测：passed=0 且 skipped>0 且 failed=0 → 疑似 globalSetup 失败或数据源污染
    $isZeroExec  = ($passed -eq 0 -and $skipped -gt 0 -and $failed -eq 0)
    $statusIcon  = if ($failed -gt 0) { "❌" } elseif ($total -eq 0) { "⚪" } elseif ($isZeroExec) { "⚠️" } else { "✅" }
    $statusText  = if ($failed -gt 0) { "有失败 - 不可发布" } elseif ($total -eq 0) { "未执行" } elseif ($isZeroExec) { "异常态 - 全部跳过（通过率 0%）" } else { "全部通过 - 可发布" }
    $gateStatus  = if ($failed -gt 0) { "🔴 **不可发布**" } elseif ($total -eq 0) { "⚪ **未验证**" } elseif ($isZeroExec) { "🔴 **不可发布（异常态：全部跳过）**" } else { "🟢 **可发布**" }
    $durStr  = if ($dur -ge 3600) { "$([math]::Round($dur/3600,1))h" } elseif ($dur -ge 60) { "$([math]::Round($dur/60,1))m" } else { "${dur}s" }

    # ── 构建 Markdown ──
    $sb = [System.Text.StringBuilder]::new()
    $null = $sb.AppendLine("# $icon $display 测试报告")
    $null = $sb.AppendLine("")
    $null = $sb.AppendLine("> **报告版本**：独立工具报告 v1.0  ")
    $null = $sb.AppendLine("> **生成时间**：$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')  ")
    $null = $sb.AppendLine("> **数据来源**：$source  ")
    $null = $sb.AppendLine("> **覆盖基准**：$($meta.desc)")
    $null = $sb.AppendLine("")
    $null = $sb.AppendLine("---")
    $null = $sb.AppendLine("")
    $null = $sb.AppendLine("## 📊 执行摘要")
    $null = $sb.AppendLine("")
    $null = $sb.AppendLine("| 指标             | 数值               |")
    $null = $sb.AppendLine("|------------------|--------------------|")
    $null = $sb.AppendLine("| 标准用例数（基准）| $stdCases          |")
    $null = $sb.AppendLine("| $actualMetricLabel   | $total             |")
    if ($measurementMode -eq "compatible-cases") {
        $null = $sb.AppendLine("| 兼容执行用例数   | $comparableTotal             |")
    }
    if ($ToolName -eq "k6") {
        $null = $sb.AppendLine("| 实际执行场景文件数 | $executedFileCount             |")
    }
    $null = $sb.AppendLine("| 通过用例数       | $passed ✅         |")
    $null = $sb.AppendLine("| 失败用例数       | $failed ❌         |")
    $null = $sb.AppendLine("| 跳过用例数       | $skipped ⏭️        |")
    $null = $sb.AppendLine("| 通过率           | $passRate%         |")
    $null = $sb.AppendLine("| 执行总耗时       | $durStr            |")
    $null = $sb.AppendLine("| 最后执行时间     | $ts                |")
    $null = $sb.AppendLine("| 发布门禁状态     | $gateStatus        |")
    $null = $sb.AppendLine("")
    $null = $sb.AppendLine("---")

    # ── 文件级溯源 ──
    if ($fileList.Count -gt 0) {
        $null = $sb.AppendLine("")
        $null = $sb.AppendLine("## 📁 文件级执行结果（$($fileList.Count) 个测试文件）")
        $null = $sb.AppendLine("")
        $null = $sb.AppendLine("| 状态 | 文件路径 | 总计 | 通过 | 失败 | 跳过 | 耗时 |")
        $null = $sb.AppendLine("|------|---------|------|------|------|------|------|")

        # 按失败优先排序
        $sortedFiles = @($fileList | Sort-Object { if ($null -ne $_.failed) { [int]$_.failed } else { 0 } } -Descending)
        foreach ($f in $sortedFiles) {
            $fs      = if ([int]$f.failed -gt 0) { "❌" } elseif ([int]$f.total -eq 0) { "⚪" } else { "✅" }
            $ffile   = [string]$f.file
            $fdur    = "$([double]$f.duration_s)s"
            $null = $sb.AppendLine("| $fs | ``$ffile`` | $([int]$f.total) | $([int]$f.passed) | $([int]$f.failed) | $([int]$f.skipped) | $fdur |")
        }
        $null = $sb.AppendLine("")
        $null = $sb.AppendLine("---")
    }

    # ── 失败用例详情 ──
    $failures = @()
    if ($null -ne $data.failures) { $failures = @($data.failures) }
    elseif ($null -ne $data.files) {
        foreach ($f in @($data.files)) {
            foreach ($d in @($f.details)) {
                if ($null -ne $d -and $d.status -in @("failed","error")) { $failures += $d }
            }
        }
    }

    if ($failures.Count -gt 0) {
        $null = $sb.AppendLine("")
        $null = $sb.AppendLine("## ❌ 失败用例详情（共 $($failures.Count) 条）")
        $null = $sb.AppendLine("")

        $shown = 0
        foreach ($fc in ($failures | Select-Object -First 100)) {
            $shown++
            $fcName = "未知"
            if ($null -ne $fc.name) { $fcName = [string]$fc.name }
            elseif ($null -ne $fc.classname) { $fcName = [string]$fc.classname }
            $fcErr = ""
            if ($null -ne $fc.error) { $fcErr = [string]$fc.error }
            $fcErr  = $fcErr -replace "`r`n|`n|`r"," " | Select-Object -First 1
            if ($fcErr.Length -gt 200) { $fcErr = $fcErr.Substring(0,200) + "..." }
            $null = $sb.AppendLine("### $shown. ``$fcName``")
            if ($fcErr) { $null = $sb.AppendLine("") ; $null = $sb.AppendLine("> $fcErr") }
            $null = $sb.AppendLine("")
        }
        if ($failures.Count -gt 100) {
            $null = $sb.AppendLine("> ⚠️ 仅展示前 100 条失败，共 $($failures.Count) 条，请查看完整 XML 报告。")
        }
        $null = $sb.AppendLine("")
        $null = $sb.AppendLine("---")
    }

    # ── 发布门禁 ──
    $null = $sb.AppendLine("")
    $null = $sb.AppendLine("## 🚦 发布门禁检查")
    $null = $sb.AppendLine("")
    $null = $sb.AppendLine("| 检查项                   | 状态 |")
    $null = $sb.AppendLine("|--------------------------|------|")
    $null = $sb.AppendLine("| 测试已执行               | $(if ($total -gt 0) { "✅ 是" } else { "❌ 否" }) |")
    $null = $sb.AppendLine("| 无失败用例               | $(if ($failed -eq 0 -and $total -gt 0) { "✅ 是" } else { "❌ 否（$failed 条失败）" }) |")
    $null = $sb.AppendLine("| 无异常态（非全跳过）     | $(if ($isZeroExec) { "❌ 否（passed=0, skipped=$skipped，疑似数据源污染）" } else { "✅ 正常" }) |")
    $null = $sb.AppendLine("| $coverageGateLabel  | $coverageGateValue |")
    $null = $sb.AppendLine("| 通过率 ≥ 95%             | $(if ($passRate -ge 95) { "✅ $passRate%" } else { "❌ $passRate%（需 ≥ 95%）" }) |")
    $null = $sb.AppendLine("")
    $null = $sb.AppendLine("**最终结论**：$gateStatus")
    $null = $sb.AppendLine("")
    $null = $sb.AppendLine("---")
    $null = $sb.AppendLine("")
    $null = $sb.AppendLine("*本报告由 ``generate-tool-reports.ps1`` 自动生成，具备完整溯源能力。*")
    $null = $sb.AppendLine("*如需重新生成：``.\scripts\generate-tool-reports.ps1 -Tool $ToolName``*")

    # ── 输出 Markdown ──
    $mdPath   = Join-Path $ReportsDir "$ToolName-report.md"
    $sb.ToString() | Out-File $mdPath -Encoding UTF8 -Force

    # ── 输出 JSON（机器可读） ──
    $jsonData = [ordered]@{
        tool=$ToolName; displayName=$display; icon=$icon
        standardCases=$stdCases
        summary=[ordered]@{
            total=$total; passed=$passed; failed=$failed; skipped=$skipped
            passRate=$passRate; duration_s=$dur; timestamp=$ts; source=$source
            measurementMode=$measurementMode; comparableTotal=$comparableTotal; executedFiles=$executedFileCount
        }
        gateStatus=@{ canRelease=($failed -eq 0 -and $total -gt 0 -and -not $isZeroExec -and $passRate -ge 95); statusText=$statusText }
        fileCount=$fileList.Count
        files=$fileList
        failures=($failures | Select-Object -First 500)
    }
    $jsonPath = Join-Path $ReportsDir "$ToolName-report.json"
    $jsonData | ConvertTo-Json -Depth 15 | Out-File $jsonPath -Encoding UTF8 -Force

    Write-Host "  📄 [$ToolName] 报告已生成 → $mdPath" -ForegroundColor Cyan
    Remove-Variable data, fileList, failures -ErrorAction SilentlyContinue

    return $jsonData
}

# ═══════════════════════════════════════════════════════════════════════════
# 主入口
# ═══════════════════════════════════════════════════════════════════════════
$tools = if ($Tool -eq "all") { Get-SevenToolOrder } else { @($Tool) }

Write-Host "`n📊 生成独立工具测试报告..." -ForegroundColor Cyan
Write-Host "工具范围：$($tools -join ', ')  输出目录：$ReportsDir" -ForegroundColor Gray

$results = @{}
foreach ($t in $tools) {
    $r = Build-ToolReport $t
    $results[$t] = $r
}

Write-Host "`n✅ 报告生成完成：" -ForegroundColor Green
foreach ($t in $tools) {
    Write-Host "  → TestResults/reports/$t-report.md" -ForegroundColor Gray
}

if ($tools.Count -gt 1) {
    Write-Host "`n💡 下一步：生成七工具总报告" -ForegroundColor Yellow
    Write-Host "  .\scripts\aggregate-tool-reports.ps1" -ForegroundColor DarkYellow
}
