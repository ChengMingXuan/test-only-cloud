<#
.SYNOPSIS
    原子化测试执行引擎 - 默认逐文件执行，保证资源稳定
.DESCRIPTION
    三种执行模式：
      atomic   (默认) 一个文件执行完再执行下一个，稳定可预期
      batch    N个文件一组并发，-BatchSize 控制单批并发数（默认5）
      parallel 全部文件同时并发（最快，资源要求最高）

    结果存储：TestResults/atomic/{tool}/{filename}.json (原子)
    工具报告：TestResults/reports/{tool}-report.json
    三种模式产生相同的 JSON schema，报告聚合层无感知

.PARAMETER Tool
    必填。指定工具：pytest | cypress | puppeteer | selenium | playwright | k6 | all
.PARAMETER Mode
    执行模式：atomic（默认）| batch | parallel
.PARAMETER File
    只执行指定文件（相对于工具测试目录的路径）
.PARAMETER BatchSize
    batch 模式下的每批文件数（默认5）
.PARAMETER MaxFiles
    最多执行文件数（0=全部，正数用于快速冒烟）
.PARAMETER CollectOnly
    仅重新聚合已有原子结果，不跑测试
.PARAMETER GenerateReport
    执行完成后自动生成该工具的独立报告

.EXAMPLE
    # 原子化执行 pytest（逐文件，默认）
    .\run-atomic-tests.ps1 -Tool pytest
    # 批量执行（每批5文件）
    .\run-atomic-tests.ps1 -Tool pytest -Mode batch -BatchSize 5
    # 并发（全文件同时）
    .\run-atomic-tests.ps1 -Tool pytest -Mode parallel
    # 执行单个文件
    .\run-atomic-tests.ps1 -Tool pytest -File "test-automation/tests/api/test_account_api.py"
    # 全部6类原子化执行（自动生成报告）
    .\run-atomic-tests.ps1 -Tool all -GenerateReport
#>
param(
    [Parameter(Mandatory)]
    [ValidateSet("all","integration","pytest","cypress","puppeteer","selenium","playwright","k6")]
    [string]$Tool,

    [ValidateSet("atomic","batch","parallel")]
    [string]$Mode = "atomic",

    [string]$File = "",
    [int]$BatchSize = 5,
    [int]$MaxFiles = 0,
    [switch]$CollectOnly,
    [switch]$GenerateReport,
    [switch]$ForceRunAll,
    [switch]$ContinueOnFailure,
    [switch]$VerboseOutput
)

$ErrorActionPreference = "Continue"
$RootDir  = (Resolve-Path "$PSScriptRoot\..").Path
$TestsDir = Join-Path $RootDir "testing/tests"
$K6Dir    = Join-Path $RootDir "testing/k6"
$AtomicDir  = Join-Path $RootDir "TestResults\atomic"
$ControlDir = Join-Path $RootDir "TestResults\control"
$ReportsDir = Join-Path $RootDir "TestResults\reports"

foreach ($d in @($AtomicDir, $ControlDir, $ReportsDir)) {
    New-Item -Path $d -ItemType Directory -Force | Out-Null
}

$envScript = Join-Path $TestsDir "set-test-env.ps1"
if (Test-Path $envScript) { . $envScript }

# ───────────────────────────────── 工具函数 ─────────────────────────────────
function Write-Banner { param($msg, $color="Cyan")
    Write-Host "`n╔═══════════════════════════════════════════════════════════╗" -ForegroundColor $color
    Write-Host "║  $($msg.PadRight(57))║" -ForegroundColor $color
    Write-Host "╚═══════════════════════════════════════════════════════════╝" -ForegroundColor $color
}
function Write-Step  { param($m) Write-Host "  ─── $m" -ForegroundColor Cyan  }
function Write-OK    { param($m) Write-Host "  ✅ $m"  -ForegroundColor Green  }
function Write-Fail  { param($m) Write-Host "  ❌ $m"  -ForegroundColor Red    }
function Write-Info  { param($m) Write-Host "  ℹ️ $m"  -ForegroundColor Gray   }
function Write-Prog  { param($m) Write-Host "  ⏳ $m"  -ForegroundColor DarkYellow }

function Get-ToolRelativePath {
    param(
        [string]$BaseDir,
        [string]$Path
    )

    if (-not $Path) { return "" }

    try {
        $baseFull = [System.IO.Path]::GetFullPath($BaseDir)
        $pathFull = [System.IO.Path]::GetFullPath($Path)
        return ([System.IO.Path]::GetRelativePath($baseFull, $pathFull)).Replace("\", "/")
    } catch {
        return $Path.Replace("$BaseDir\", "").Replace("$BaseDir/", "").Replace("\", "/")
    }
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

function Refresh-ToolOutputs {
    param([string]$ToolName)

    $summary = Aggregate-ToolResults $ToolName
    return $summary
}

function Get-ControlDocPath {
    param([string]$ToolName)
    return (Join-Path $ControlDir "$ToolName-control.json")
}

function Update-ControlStats {
    param($ControlDoc)
    $entries = @($ControlDoc.testFiles)
    $ControlDoc.stats = [ordered]@{
        baseline = $entries.Count
        active   = @($entries | Where-Object { $_.status -ne "archived" }).Count
        archived = @($entries | Where-Object { $_.status -eq "archived" }).Count
        pending  = @($entries | Where-Object { $_.status -in @("pending","pending_retest") }).Count
        passed   = @($entries | Where-Object { $_.status -eq "passed" }).Count
        failed   = @($entries | Where-Object { $_.status -eq "failed" }).Count
    }
    $ControlDoc.lastUpdated = (Get-Date).ToString("yyyy-MM-ddTHH:mm:ss")
}

function Save-ControlDoc {
    param([string]$ToolName, $ControlDoc)
    Update-ControlStats -ControlDoc $ControlDoc
    $path = Get-ControlDocPath $ToolName
    $ControlDoc | ConvertTo-Json -Depth 10 | Out-File $path -Encoding UTF8 -Force
}

function Read-AtomicStatusMap {
    param([string]$ToolName)
    $map = @{}
    $dir = Join-Path $AtomicDir $ToolName
    if (-not (Test-Path $dir)) { return $map }

    $files = @(Get-ChildItem $dir -Filter "*.json" -ErrorAction SilentlyContinue | Where-Object { $_.Name -ne "summary.json" })
    foreach ($f in $files) {
        try {
            $data = Get-Content $f.FullName -Raw -Encoding UTF8 | ConvertFrom-Json
            if (-not (Test-IsAtomicResultObject -Data $data)) { continue }
            $normalizedFile = ([string]$data.file).Replace("\", "/")
            $map[$normalizedFile] = $data
        } catch {}
    }
    return $map
}

function Ensure-ControlDoc {
    param([string]$ToolName, [array]$AllFiles, [string]$BaseDir)

    $path = Get-ControlDocPath $ToolName
    $control = $null
    if (Test-Path $path) {
        try {
            $control = Get-Content $path -Raw -Encoding UTF8 | ConvertFrom-Json
        } catch {
            $control = $null
        }
    }

    if ($null -eq $control) {
        $items = @()
        $idx = 0
        foreach ($f in $AllFiles) {
            $idx++
            $relPath = Get-ToolRelativePath -BaseDir $BaseDir -Path $f
            $items += [ordered]@{
                id = ("TF-{0}-{1:D4}" -f $ToolName, $idx)
                file = $relPath
                status = "pending"
                type = "BASELINE"
                lastExecuted = $null
                passedCount = 0
                failedCount = 0
                skippedCount = 0
                totalCount = 0
                duration_s = 0
                lastError = ""
            }
        }

        $control = [ordered]@{
            tool = $ToolName
            baselineVersion = "v1.0"
            baselineLockedAt = (Get-Date).ToString("yyyy-MM-ddTHH:mm:ss")
            currentVersion = "v1.0"
            lastUpdated = (Get-Date).ToString("yyyy-MM-ddTHH:mm:ss")
            stats = [ordered]@{}
            testFiles = $items
        }
    }

    if ($null -ne $control.testFiles) {
        $control.testFiles = @($control.testFiles | Where-Object {
            $fileValue = [string]$_.file
            $fileValue -and (-not [System.IO.Path]::IsPathRooted($fileValue))
        })

        $index = 0
        foreach ($item in @($control.testFiles)) {
            $index++
            $item.file = ([string]$item.file).Replace("\", "/")
            $item.id = ("TF-{0}-{1:D4}" -f $ToolName, $index)
        }
    }

    $known = @{}
    foreach ($entry in @($control.testFiles)) {
        $known[[string]$entry.file] = $true
    }

    $nextIndex = @($control.testFiles).Count
    foreach ($f in $AllFiles) {
        $relPath = Get-ToolRelativePath -BaseDir $BaseDir -Path $f
        if ($known.ContainsKey($relPath)) { continue }
        $nextIndex++
        $control.testFiles += [ordered]@{
            id = ("TF-{0}-{1:D4}" -f $ToolName, $nextIndex)
            file = $relPath
            status = "pending"
            type = "NEW"
            lastExecuted = $null
            passedCount = 0
            failedCount = 0
            skippedCount = 0
            totalCount = 0
            duration_s = 0
            lastError = ""
        }
    }

    $atomicMap = Read-AtomicStatusMap -ToolName $ToolName
    foreach ($entry in @($control.testFiles)) {
        if (-not $atomicMap.ContainsKey([string]$entry.file)) { continue }
        $atomic = $atomicMap[[string]$entry.file]
        if ($entry.status -eq "archived") { continue }
        $entry.status = [string]$atomic.status
        $entry.lastExecuted = [string]$atomic.timestamp
        $entry.passedCount = [int]$atomic.passed
        $entry.failedCount = [int]$atomic.failed
        $entry.skippedCount = [int]$atomic.skipped
        $entry.totalCount = [int]$atomic.total
        $entry.duration_s = [double]$atomic.duration_s
        $entry.lastError = if ($atomic.details) {
            $firstError = @($atomic.details | Where-Object { $_.status -in @("failed","error") } | Select-Object -First 1)
            if ($firstError.Count -gt 0) { [string]$firstError[0].error } else { "" }
        } else { "" }
    }

    Save-ControlDoc -ToolName $ToolName -ControlDoc $control
    return $control
}

function Update-ControlEntry {
    param([string]$ToolName, $ControlDoc, [string]$RelPath, $Result)

    $normalizedRelPath = ([string]$RelPath).Replace("\", "/")
    $entry = @($ControlDoc.testFiles | Where-Object { ([string]$_.file).Replace("\", "/") -eq $normalizedRelPath } | Select-Object -First 1)
    if ($entry.Count -eq 0) { return }

    $target = $entry[0]
    $target.status = if ([int]$Result.failed -gt 0) { "failed" } elseif ([int]$Result.total -eq 0) { "skipped" } else { "passed" }
    $target.lastExecuted = (Get-Date).ToString("yyyy-MM-ddTHH:mm:ss")
    $target.passedCount = [int]$Result.passed
    $target.failedCount = [int]$Result.failed
    $target.skippedCount = [int]$Result.skipped
    $target.totalCount = [int]$Result.total
    $target.duration_s = [double]$Result.duration_s
    $target.lastError = if ($Result.details) {
        $firstError = @($Result.details | Where-Object { $_.status -in @("failed","error") } | Select-Object -First 1)
        if ($firstError.Count -gt 0) { [string]$firstError[0].error } else { "" }
    } else { "" }

    Save-ControlDoc -ToolName $ToolName -ControlDoc $ControlDoc
}

function Get-PendingExecutionFiles {
    param($ControlDoc, [array]$AllFiles, [string]$BaseDir, [string]$SingleFile="")

    if ($SingleFile) { return $AllFiles }
    if ($ForceRunAll) { return $AllFiles }

    $fileMap = @{}
    foreach ($f in $AllFiles) {
        $relPath = Get-ToolRelativePath -BaseDir $BaseDir -Path $f
        $fileMap[$relPath] = $f
    }

    $failed = @()
    $pending = @()
    foreach ($entry in @($ControlDoc.testFiles)) {
        if (-not $fileMap.ContainsKey([string]$entry.file)) { continue }
        switch ([string]$entry.status) {
            "failed" { $failed += $fileMap[[string]$entry.file] }
            "pending" { $pending += $fileMap[[string]$entry.file] }
            "pending_retest" { $pending += $fileMap[[string]$entry.file] }
        }
    }
    return @($failed + $pending)
}

# 解析 JUnit XML → 统一结果对象
function Parse-JUnit {
    param([string]$Path)
    if (-not (Test-Path $Path)) { return $null }
    try {
        [xml]$xml = Get-Content $Path -Encoding UTF8
        $suites = @()
        if ($xml.testsuites -and $xml.testsuites.testsuite) { $suites = @($xml.testsuites.testsuite) }
        elseif ($xml.testsuite) { $suites = @($xml.testsuite) }
        elseif ($xml.testsuites) { $suites = @($xml.testsuites) }

        $total=0; $failed=0; $skipped=0; $dur=0.0; $details=@()
        foreach ($s in $suites) {
            if ($null -ne $s.tests)    { $total   += [int]$s.tests }
            if ($null -ne $s.failures) { $failed  += [int]$s.failures }
            if ($null -ne $s.errors)   { $failed  += [int]$s.errors }
            if ($null -ne $s.skipped)  { $skipped += [int]$s.skipped }
            if ($null -ne $s.time)     { $dur     += [double]$s.time }
            foreach ($tc in @($s.testcase)) {
                if ($null -eq $tc -or -not $tc.name) { continue }
                $st = "passed"; $err = ""
                if ($tc.failure) { $st = "failed";  $errMsg = if ($null -ne $tc.failure.message) { $tc.failure.message } else { $tc.failure.InnerText }; $err = [string]$errMsg -replace "`n"," " }
                elseif ($tc.error)   { $st = "error";   $errMsg = if ($null -ne $tc.error.message) { $tc.error.message } else { $tc.error.InnerText }; $err = [string]$errMsg -replace "`n"," " }
                elseif ($tc.skipped) { $st = "skipped" }
                $tcTime = 0.0; if ($null -ne $tc.time) { $tcTime = [double]$tc.time }
                $details += [ordered]@{ name=$tc.name; status=$st; error=[string]$err; duration_s=$tcTime }
            }
        }
        return [ordered]@{ total=$total; passed=$total-$failed-$skipped; failed=$failed; skipped=$skipped; duration_s=[math]::Round($dur,1); details=$details }
    } catch { return $null }
}

# 解析 TRX (dotnet test) → 统一结果对象
function Parse-Trx {
    param([string]$Path)
    if (-not (Test-Path $Path)) { return $null }
    try {
        [xml]$trx = Get-Content $Path -Encoding UTF8
        $counters = $trx.TestRun.ResultSummary.Counters
        if ($null -eq $counters) { return $null }
        $total   = [int]$counters.total
        $passed  = [int]$counters.passed
        $failed  = [int]$counters.failed
        $skipped = $total - $passed - $failed
        $dur     = 0.0
        $details = @()
        foreach ($result in @($trx.TestRun.Results.UnitTestResult)) {
            if ($null -eq $result -or -not $result.testName) { continue }
            $st = switch ($result.outcome) { "Passed" { "passed" } "Failed" { "failed" } default { "skipped" } }
            $err = ""; if ($result.Output.ErrorInfo.Message) { $err = [string]$result.Output.ErrorInfo.Message -replace "`n"," " }
            $tcDur = 0.0; if ($result.duration) { try { $tcDur = [timespan]::Parse($result.duration).TotalSeconds } catch {} }
            $dur += $tcDur
            $details += [ordered]@{ name=$result.testName; status=$st; error=[string]$err; duration_s=$tcDur }
        }
        return [ordered]@{ total=$total; passed=$passed; failed=$failed; skipped=$skipped; duration_s=[math]::Round($dur,1); details=$details }
    } catch { return $null }
}

# 将单文件结果写入原子目录
function Save-Atomic {
    param([string]$ToolName, [string]$RelFile, [hashtable]$R, [double]$Dur, [string]$XmlPath="")
    $dir = Join-Path $AtomicDir $ToolName
    New-Item -Path $dir -ItemType Directory -Force | Out-Null
    $safe = ($RelFile -replace '[\\/:*?"<>|]','_') -replace '\s+','_'
    $out  = Join-Path $dir "$safe.json"
    $obj  = [ordered]@{
        file=$RelFile; tool=$ToolName
        status = if ($R.failed -gt 0) { "failed" } elseif ($R.total -eq 0) { "skipped" } else { "passed" }
        total=$R.total; passed=$R.passed; failed=$R.failed; skipped=$R.skipped
        duration_s=[math]::Round($Dur,1); timestamp=(Get-Date).ToString("yyyy-MM-ddTHH:mm:ss")
        xmlReport=$XmlPath; details=$R.details
    }
    $obj | ConvertTo-Json -Depth 10 | Out-File $out -Encoding UTF8 -Force
}

# 从原子目录聚合工具级汇总
function Aggregate-ToolResults {
    param([string]$ToolName)
    $dir = Join-Path $AtomicDir $ToolName
    if (-not (Test-Path $dir)) { return $null }
    $files = @(Get-ChildItem $dir -Filter "*.json" | Where-Object { $_.Name -ne "summary.json" -and $_.Name -notlike "*_summary.json" })
    $total=0; $passed=0; $failed=0; $skipped=0; $dur=0.0
    $fileResults = @()
    foreach ($f in $files) {
        try {
            $d = Get-Content $f.FullName -Raw -Encoding UTF8 | ConvertFrom-Json
            if (-not (Test-IsMeaningfulAtomicResult -Data $d)) { continue }
            $total   += [int]$d.total
            $passed  += [int]$d.passed
            $failed  += [int]$d.failed
            $skipped += [int]$d.skipped
            $dur     += [double]$d.duration_s
            $fileResults += $d
        } catch {}
    }
    $summary = [ordered]@{
        tool=$ToolName; fileCount=$fileResults.Count; mode="atomic"
        total=$total; passed=$passed; failed=$failed; skipped=$skipped
        duration_s=[math]::Round($dur,1); timestamp=(Get-Date).ToString("yyyy-MM-ddTHH:mm:ss")
        status = if ($failed -gt 0) { "❌ 有失败" } elseif ($total -eq 0) { "⚪ 未运行" } else { "✅ 全部通过" }
        files = $fileResults
    }
    $summary | ConvertTo-Json -Depth 10 | Out-File (Join-Path $dir "summary.json") -Encoding UTF8 -Force
    return $summary
}

function Get-K6CheckDetails {
    param($Group)

    $details = @()
    if ($null -eq $Group) { return $details }

    if ($Group.checks) {
        foreach ($entry in $Group.checks.PSObject.Properties) {
            $check = $entry.Value
            $passes = 0
            $fails = 0
            $checkName = $entry.Name
            if ($null -ne $check.passes) { $passes = [int]$check.passes }
            if ($null -ne $check.fails)  { $fails = [int]$check.fails }
            if ($null -ne $check.name -and [string]$check.name) { $checkName = [string]$check.name }
            $details += [ordered]@{
                name = $checkName
                status = if ($fails -gt 0) { "failed" } else { "passed" }
                error = if ($fails -gt 0) { "k6 check failed: $passes passed / $fails failed" } else { "" }
                duration_s = 0
                passed = $passes
                failed = $fails
            }
        }
    }

    if ($Group.groups) {
        foreach ($entry in $Group.groups.PSObject.Properties) {
            $details += @(Get-K6CheckDetails -Group $entry.Value)
        }
    }

    return $details
}

function Parse-K6Summary {
    param([string]$SummaryPath)

    if (-not (Test-Path $SummaryPath)) {
        return [ordered]@{ total=0; passed=0; failed=0; skipped=0; duration_s=0; details=@() }
    }

    try {
        $summary = Get-Content $SummaryPath -Raw -Encoding UTF8 | ConvertFrom-Json

        $checksMetric = $summary.metrics.checks
        $checksPassed = 0
        $checksFailed = 0

        if ($null -ne $checksMetric) {
            if ($null -ne $checksMetric.passes) {
                $checksPassed = [int]$checksMetric.passes
            } elseif ($null -ne $checksMetric.values.passes) {
                $checksPassed = [int]$checksMetric.values.passes
            }

            if ($null -ne $checksMetric.fails) {
                $checksFailed = [int]$checksMetric.fails
            } elseif ($null -ne $checksMetric.values.fails) {
                $checksFailed = [int]$checksMetric.values.fails
            }
        }

        if (($checksPassed + $checksFailed) -eq 0 -and $summary.root_group) {
            foreach ($detail in @(Get-K6CheckDetails -Group $summary.root_group)) {
                if ($null -ne $detail.passed) { $checksPassed += [int]$detail.passed }
                if ($null -ne $detail.failed) { $checksFailed += [int]$detail.failed }
            }
        }

        $totalChecks = $checksPassed + $checksFailed
        $durationSeconds = 0
        if ($null -ne $summary.state.testRunDurationMs) {
            $durationSeconds = [math]::Round(([double]$summary.state.testRunDurationMs / 1000.0), 1)
        }

        $details = @(Get-K6CheckDetails -Group $summary.root_group)
        return [ordered]@{
            total = $totalChecks
            passed = $checksPassed
            failed = $checksFailed
            skipped = 0
            duration_s = $durationSeconds
            details = $details
        }
    } catch {
        return [ordered]@{ total=0; passed=0; failed=0; skipped=0; duration_s=0; details=@() }
    }
}

# 执行单个文件并返回解析后结果
function Invoke-SingleFile {
    param([string]$ToolName, [string]$FilePath, [string]$RelPath="")
    $sw = [System.Diagnostics.Stopwatch]::StartNew()
    $safe = ($RelPath -replace '[\\/:*?"<>|]','_') -replace '\s+','_'
    $outDir = Join-Path $AtomicDir $ToolName
    New-Item -Path $outDir -ItemType Directory -Force | Out-Null

    switch ($ToolName) {
        "integration" {
            $trxFile = Join-Path $outDir "$safe.trx"
            $projPath = Join-Path $RootDir "testing\JGSY.AGI.Test\JGSY.AGI.Test.csproj"
            $className = [System.IO.Path]::GetFileNameWithoutExtension($FilePath)
            & dotnet test $projPath --filter "FullyQualifiedName~$className" --logger "trx;LogFileName=$trxFile" --no-build --verbosity quiet --results-directory $outDir 2>&1 | Out-Null
            if (-not (Test-Path $trxFile)) {
                & dotnet test $projPath --filter "FullyQualifiedName~$className" --logger "trx;LogFileName=$trxFile" --verbosity quiet --results-directory $outDir 2>&1 | Out-Null
            }
            # 解析 trx 为统一结果
            $r = $null
            if (Test-Path $trxFile) {
                try {
                    [xml]$trx = Get-Content $trxFile -Encoding UTF8
                    $ns = @{ t = "http://microsoft.com/schemas/VisualStudio/TeamTest/2010" }
                    $counters = $trx.TestRun.ResultSummary.Counters
                    $total   = [int]$counters.total
                    $passed  = [int]$counters.passed
                    $failed  = [int]$counters.failed
                    $skipped = $total - $passed - $failed
                    $dur     = 0.0
                    $details = @()
                    foreach ($result in $trx.TestRun.Results.UnitTestResult) {
                        $st = switch ($result.outcome) { "Passed" { "passed" } "Failed" { "failed" } default { "skipped" } }
                        $err = ""; if ($result.Output.ErrorInfo.Message) { $err = [string]$result.Output.ErrorInfo.Message -replace "`n"," " }
                        $tcDur = 0.0; if ($result.duration) { try { $tcDur = [timespan]::Parse($result.duration).TotalSeconds } catch {} }
                        $dur += $tcDur
                        $details += [ordered]@{ name=$result.testName; status=$st; error=[string]$err; duration_s=$tcDur }
                    }
                    $r = [ordered]@{ total=$total; passed=$passed; failed=$failed; skipped=$skipped; duration_s=[math]::Round($dur,1); details=$details }
                } catch { $r = $null }
            }
        }
        "pytest" {
            $py  = if (Test-Path "$RootDir\.venv\Scripts\python.exe") { "$RootDir\.venv\Scripts\python.exe" } else { "python" }
            $xml = Join-Path $outDir "$safe.xml"
            & $py -m pytest $FilePath --tb=short --no-header -q --junitxml=$xml --timeout=60 2>&1 | Out-Null
            $r   = Parse-JUnit $xml
        }
        "selenium" {
            $py  = if (Test-Path "$TestsDir\selenium-tests\venv\Scripts\python.exe") { "$TestsDir\selenium-tests\venv\Scripts\python.exe" } else { "python" }
            $xml = Join-Path $outDir "$safe.xml"
            & $py -m pytest $FilePath --tb=short --no-header -q --junitxml=$xml --timeout=120 2>&1 | Out-Null
            $r   = Parse-JUnit $xml
        }
        "cypress" {
            $xml = Join-Path $outDir "$safe.xml"
            $specRel = $RelPath  # cypress --spec 接受相对路径
            Push-Location "$TestsDir\cypress-tests"
            $env:CYPRESS_RESULTS_XML = $xml
            npx cypress run --spec $FilePath --reporter junit --reporter-options "mochaFile=$xml" --headless 2>&1 | Out-Null
            Pop-Location
            $r = Parse-JUnit $xml
        }
        "puppeteer" {
            $xml = Join-Path $outDir "$safe.xml"
            $env:JEST_JUNIT_OUTPUT_FILE = $xml
            $jestPath = if ($RelPath) { $RelPath -replace '\\','/' } else { $FilePath -replace '\\','/' }
            Push-Location "$TestsDir\puppeteer-tests"
            & node_modules\.bin\jest $jestPath --no-coverage --testResultsProcessor=jest-junit --testTimeout=30000 --forceExit 2>&1 | Out-Null
            Pop-Location
            $r = Parse-JUnit $xml
        }
        "playwright" {
            $xml = Join-Path $outDir "$safe.xml"
            $pwPath = if ($RelPath) { $RelPath -replace '\\','/' } else { $FilePath -replace '\\','/' }
            Push-Location "$TestsDir\playwright-tests"
            & node_modules\.bin\playwright test $pwPath --reporter=junit 2>&1 | Out-Null
            # playwright 默认输出到 junit-results.xml
            $pwXml = "junit-results.xml"
            if (Test-Path $pwXml) { Copy-Item $pwXml $xml -Force }
            Pop-Location
            $r = Parse-JUnit $xml
        }
        "k6" {
            $tempDir = Join-Path $ControlDir "k6-temp"
            New-Item -Path $tempDir -ItemType Directory -Force | Out-Null
            $jsonOut = Join-Path $tempDir "$safe.ndjson"
            $summaryJson = Join-Path $tempDir "${safe}_summary.json"
            & k6 run --out "json=$jsonOut" --summary-export "$summaryJson" $FilePath 2>&1 | Out-Null
            $r = Parse-K6Summary -SummaryPath $summaryJson
            Remove-Item $jsonOut, $summaryJson -Force -ErrorAction SilentlyContinue
        }
    }

    $sw.Stop()
    if ($null -eq $r) { $r = [ordered]@{ total=0; passed=0; failed=0; skipped=0; duration_s=0; details=@() } }
    $r.duration_s = [math]::Round($sw.Elapsed.TotalSeconds, 1)
    Save-Atomic -ToolName $ToolName -RelFile $RelPath -R $r -Dur $r.duration_s

    return $r
}

# ═══════════════════════════════════════════════════════════════════════════
# 各工具文件发现函数
# ═══════════════════════════════════════════════════════════════════════════
function Get-TestFiles {
    param([string]$ToolName, [string]$SingleFile="")

    if ($SingleFile) {
        # 接受绝对路径或相对路径
        if ([System.IO.Path]::IsPathRooted($SingleFile)) { return @($SingleFile) }
        else {
            $toolBaseDir = Get-ToolBaseDir $ToolName
            $candidates = @(
                (Join-Path $toolBaseDir $SingleFile),
                (Join-Path $TestsDir $SingleFile),
                (Join-Path $K6Dir    $SingleFile),
                (Join-Path $RootDir  $SingleFile)
            )
            foreach ($c in $candidates) { if (Test-Path $c) { return @($c) } }
        }
        return @()
    }

    switch ($ToolName) {
        "integration" {
            return @(Get-ChildItem "$RootDir\testing\JGSY.AGI.Test" -Filter "*Tests.cs" -Recurse -ErrorAction SilentlyContinue |
                Where-Object { $_.DirectoryName -notmatch 'obj|bin' } |
                Select-Object -ExpandProperty FullName)
        }
        "pytest" {
            $dirs = @("$TestsDir\api","$TestsDir\automated","$TestsDir\test-automation","$TestsDir\security","$TestsDir\blockchain")
            $all = @()
            foreach ($d in $dirs) {
                if (Test-Path $d) {
                    $all += @(Get-ChildItem $d -Filter "test_*.py" -Recurse -ErrorAction SilentlyContinue |
                        Where-Object { $_.FullName -notmatch "__pycache__" } |
                        Select-Object -ExpandProperty FullName)
                }
            }
            return $all
        }
        "selenium" {
            return @(Get-ChildItem "$TestsDir\selenium-tests\tests" -Filter "test_*.py" -Recurse -ErrorAction SilentlyContinue |
                Where-Object { $_.FullName -notmatch "__pycache__" -and $_.FullName -notmatch "venv" } |
                Select-Object -ExpandProperty FullName)
        }
        "cypress" {
            return @(Get-ChildItem "$TestsDir\cypress-tests\e2e" -Filter "*.cy.js" -Recurse -ErrorAction SilentlyContinue |
                Select-Object -ExpandProperty FullName)
        }
        "puppeteer" {
            return @(Get-ChildItem "$TestsDir\puppeteer-tests\tests" -Filter "*.test.js" -Recurse -ErrorAction SilentlyContinue |
                Select-Object -ExpandProperty FullName)
        }
        "playwright" {
            return @(Get-ChildItem "$TestsDir\playwright-tests\tests" -Filter "*.spec.ts" -Recurse -ErrorAction SilentlyContinue |
                Select-Object -ExpandProperty FullName)
        }
        "k6" {
            return @(Get-ChildItem "$K6Dir\scenarios" -Filter "*.js" -Recurse -ErrorAction SilentlyContinue |
                Select-Object -ExpandProperty FullName)
        }
    }
    return @()
}

# 工具基础目录（用于计算相对路径）
function Get-ToolBaseDir {
    param([string]$ToolName)
    switch ($ToolName) {
        "integration" { return "$RootDir\testing\JGSY.AGI.Test" }
        "pytest"     { return $TestsDir }
        "selenium"   { return "$TestsDir\selenium-tests\tests" }
        "cypress"    { return "$TestsDir\cypress-tests\e2e" }
        "puppeteer"  { return "$TestsDir\puppeteer-tests\tests" }
        "playwright" { return "$TestsDir\playwright-tests\tests" }
        "k6"         { return "$K6Dir\scenarios" }
    }
    return $RootDir
}

# ═══════════════════════════════════════════════════════════════════════════
# 主执行函数
# ═══════════════════════════════════════════════════════════════════════════
function Run-Tool {
    param([string]$ToolName)

    $baseDir  = Get-ToolBaseDir $ToolName
    $discoveredFiles = @(Get-TestFiles -ToolName $ToolName -SingleFile $File)
    $controlDoc = Ensure-ControlDoc -ToolName $ToolName -AllFiles $discoveredFiles -BaseDir $baseDir
    [array]$allFiles = @(Get-PendingExecutionFiles -ControlDoc $controlDoc -AllFiles $discoveredFiles -BaseDir $baseDir -SingleFile $File)
    if ($MaxFiles -gt 0) { $allFiles = $allFiles | Select-Object -First $MaxFiles }

    $baselineCount = @($discoveredFiles).Count
    $resumeCount = @($allFiles).Count

    $total = $allFiles.Count
    if ($total -eq 0) {
        Write-OK "[$ToolName] 无待执行文件（已全部通过或已归档）"
        if ($GenerateReport) {
            return Refresh-ToolOutputs -ToolName $ToolName
        }
        return Aggregate-ToolResults $ToolName
    }

    Write-Banner "⚛️ [$ToolName] $Mode 模式 - $total 个文件"
    Write-Info "[$ToolName] 控制文档：$(Get-ControlDocPath $ToolName)"
    if (-not $File) {
        Write-Info "[$ToolName] 基线总数:$baselineCount，本轮待执行:$resumeCount，策略: 默认跳过已通过，仅执行失败/跳过/未完成"
    }

    if ($CollectOnly) {
        Write-Info "CollectOnly：跳过执行，直接聚合已有原子结果"
        return Aggregate-ToolResults $ToolName
    }

    $started = Get-Date
    $passedFiles = 0; $failedFiles = 0

    switch ($Mode) {
        "atomic" {
            $i = 0
            foreach ($f in $allFiles) {
                $i++
                $relPath = Get-ToolRelativePath -BaseDir $baseDir -Path $f
                if ($VerboseOutput) { Write-Prog "[$i/$total] $relPath" }
                $r = Invoke-SingleFile -ToolName $ToolName -FilePath $f -RelPath $relPath
                Update-ControlEntry -ToolName $ToolName -ControlDoc $controlDoc -RelPath $relPath -Result $r
                $icon = if ($r.failed -gt 0) { "❌" } else { "✅" }
                $pct  = [math]::Round($i*100/$total, 0)
                if ($r.failed -gt 0) { $failedFiles++ } else { $passedFiles++ }
                $clr = if ($r.failed -gt 0) { "Red" } else { "DarkGray" }
                Write-Host ("  {0} [{1}/{2}]({3}%) {4} 通:$($r.passed) 败:$($r.failed) 总:$($r.total) 耗:$($r.duration_s)s" -f $icon,$i,$total,$pct,$relPath) `
                    -ForegroundColor $clr
                $summary = Refresh-ToolOutputs -ToolName $ToolName
                Write-Info "[$ToolName] 已即时同步：累计文件 $($summary.fileCount) / 用例 $($summary.total) / 失败 $($summary.failed)"
                if ($r.failed -gt 0 -and -not $ContinueOnFailure) {
                    Write-Fail "[$ToolName] 检测到失败，按控制文档策略暂停；下次将从失败文件继续。使用 -ContinueOnFailure 可跳过暂停。"
                    break
                }
            }
        }

        "batch" {
            $batchNum = 0
            for ($b = 0; $b -lt $total; $b += $BatchSize) {
                $batchNum++
                $batch = $allFiles[$b..([math]::Min($b+$BatchSize-1, $total-1))]
                Write-Prog "批次 $batchNum (共$([math]::Ceiling($total/$BatchSize))批) - $($batch.Count) 文件并发..."

                # integration 直接调 Invoke-SingleFile（TRX 解析已内置），无需 Start-Job
                if ($ToolName -eq 'integration') {
                    foreach ($f in $batch) {
                        $relPath = Get-ToolRelativePath -BaseDir $baseDir -Path $f
                        $r = Invoke-SingleFile -ToolName $ToolName -FilePath $f -RelPath $relPath
                        Update-ControlEntry -ToolName $ToolName -ControlDoc $controlDoc -RelPath $relPath -Result $r
                        if ($r.failed -gt 0) { $failedFiles++ } else { $passedFiles++ }
                        $summary = Refresh-ToolOutputs -ToolName $ToolName
                        Write-Info "[$ToolName] 已即时同步：累计文件 $($summary.fileCount) / 用例 $($summary.total) / 失败 $($summary.failed)"
                    }
                    Write-OK "批次 $batchNum 完成 (文件通过:$passedFiles 失败:$failedFiles 累计)"
                    if ($failedFiles -gt 0 -and -not $ContinueOnFailure) {
                        Write-Fail "[$ToolName] 当前批次存在失败，按控制文档策略停止后续批次；下次优先重跑失败文件。使用 -ContinueOnFailure 可跳过暂停。"
                        break
                    }
                    continue
                }

                $jobs = @()
                foreach ($f in $batch) {
                    $relPath = Get-ToolRelativePath -BaseDir $baseDir -Path $f
                    $safe    = ($relPath -replace '[\\/:*?"<>|]','_') -replace '\s+','_'
                    $xmlOut  = Join-Path $AtomicDir "$ToolName\$safe.xml"
                    New-Item -Path (Split-Path $xmlOut) -ItemType Directory -Force | Out-Null

                    $jobScript = switch ($ToolName) {
                        "pytest"     { "python -m pytest '$f' --tb=short -q --junitxml='$xmlOut' --timeout=60 2>&1 | Out-Null" }
                        "selenium"   { "python -m pytest '$f' --tb=short -q --junitxml='$xmlOut' --timeout=120 2>&1 | Out-Null" }
                        "cypress"    { "Set-Location '$TestsDir\cypress-tests'; npx cypress run --spec '$f' --reporter junit --reporter-options 'mochaFile=$xmlOut' --headless 2>&1 | Out-Null" }
                        "puppeteer"  { $fwd = $relPath -replace '\\\\','/'; "`$env:JEST_JUNIT_OUTPUT_FILE='$xmlOut'; Set-Location '$TestsDir\puppeteer-tests'; & node_modules\.bin\jest '$fwd' --no-coverage --testResultsProcessor=jest-junit --testTimeout=30000 --forceExit 2>&1 | Out-Null" }
                        "playwright" { $fwd = $relPath -replace '\\\\','/'; "Set-Location '$TestsDir\playwright-tests'; & node_modules\.bin\playwright test '$fwd' --reporter=junit 2>&1 | Out-Null" }
                        "k6"         { "k6 run '$f' 2>&1 | Out-Null" }
                        default      { "Write-Host 'no-op'" }
                    }
                    $jobs += Start-Job -ScriptBlock ([scriptblock]::Create($jobScript))
                }

                $jobs | Wait-Job | Out-Null
                $jobs | Remove-Job -Force

                # 解析本批次结果
                foreach ($f in $batch) {
                    $relPath = Get-ToolRelativePath -BaseDir $baseDir -Path $f
                    $safe    = ($relPath -replace '[\\/:*?"<>|]','_') -replace '\s+','_'
                    $xmlOut  = Join-Path $AtomicDir "$ToolName\$safe.xml"
                    $r = Parse-JUnit $xmlOut
                    if ($null -eq $r) { $r = [ordered]@{ total=0; passed=0; failed=0; skipped=0; duration_s=0; details=@() } }
                    Save-Atomic -ToolName $ToolName -RelFile $relPath -R $r -Dur $r.duration_s -XmlPath $xmlOut
                    Update-ControlEntry -ToolName $ToolName -ControlDoc $controlDoc -RelPath $relPath -Result $r
                    if ($r.failed -gt 0) { $failedFiles++ } else { $passedFiles++ }
                    $summary = Refresh-ToolOutputs -ToolName $ToolName
                    Write-Info "[$ToolName] 已即时同步：累计文件 $($summary.fileCount) / 用例 $($summary.total) / 失败 $($summary.failed)"
                }
                Write-OK "批次 $batchNum 完成 (文件通过:$passedFiles 失败:$failedFiles 累计)"
                if ($failedFiles -gt 0 -and -not $ContinueOnFailure) {
                    Write-Fail "[$ToolName] 当前批次存在失败，按控制文档策略停止后续批次；下次优先重跑失败文件。使用 -ContinueOnFailure 可跳过暂停。"
                    break
                }
            }
        }

        "parallel" {
            Write-Prog "并发执行全部 $total 文件..."
            $atomicOut = Join-Path $AtomicDir "$ToolName\parallel_all.xml"
            New-Item -Path (Split-Path $atomicOut) -ItemType Directory -Force | Out-Null

            switch ($ToolName) {
                "pytest" {
                    $py = if (Test-Path "$RootDir\.venv\Scripts\python.exe") { "$RootDir\.venv\Scripts\python.exe" } else { "python" }
                    & $py -m pytest @allFiles --tb=short -q --junitxml=$atomicOut --timeout=60 -n auto 2>&1 | Out-Null
                }
                "selenium" {
                    $py = if (Test-Path "$TestsDir\selenium-tests\venv\Scripts\python.exe") { "$TestsDir\selenium-tests\venv\Scripts\python.exe" } else { "python" }
                    & $py -m pytest @allFiles --tb=short -q --junitxml=$atomicOut --timeout=120 -n auto 2>&1 | Out-Null
                }
                default {
                    Write-Host "  ⚠️ [$ToolName] parallel 模式回退到 batch（BatchSize=$BatchSize）" -ForegroundColor Yellow
                    # 回退到批量
                    $global:Mode = "batch"
                    Run-Tool $ToolName
                    return
                }
            }
            $r = Parse-JUnit $atomicOut
            if ($null -ne $r) {
                # 将 parallel 结果作为单条聚合记录存储
                Save-Atomic -ToolName $ToolName -RelFile "parallel_all" -R $r -Dur $r.duration_s -XmlPath $atomicOut
                $passedFiles = if ($r.failed -eq 0) { $total } else { 0 }
                $failedFiles = if ($r.failed -gt 0)  { $total } else { 0 }
                $summary = Refresh-ToolOutputs -ToolName $ToolName
                Write-Info "[$ToolName] 已即时同步：累计文件 $($summary.fileCount) / 用例 $($summary.total) / 失败 $($summary.failed)"
            }
        }
    }

    $elapsed = [math]::Round(((Get-Date) - $started).TotalSeconds, 0)
    $summary = Aggregate-ToolResults $ToolName

    # 打印汇总行
    $icon = if ($summary.failed -gt 0) { "❌" } else { "✅" }
    $summClr = if ($summary.failed -gt 0) { "Red" } else { "Green" }
    Write-Host "`n  $icon [$ToolName] 完成 | 文件:$total | 用例:$($summary.total) | 通过:$($summary.passed) | 失败:$($summary.failed) | 耗时:${elapsed}s" `
        -ForegroundColor $summClr

    return $summary
}

# ═══════════════════════════════════════════════════════════════════════════
# 入口
# ═══════════════════════════════════════════════════════════════════════════

$tools = if ($Tool -eq "all") { @("integration","pytest","cypress","puppeteer","selenium","playwright","k6") } else { @($Tool) }

$allSummaries = @{}
foreach ($t in $tools) {
    $s = Run-Tool $t
    if ($null -ne $s) { $allSummaries[$t] = $s }
}

# 输出总汇表
if ($tools.Count -gt 1) {
    Write-Banner "📊 七类原子化测试完成汇总"
    $totalCases = 0; $totalPassed = 0; $totalFailed = 0
    foreach ($t in $tools) {
        $s = $allSummaries[$t]
        if ($null -eq $s) { Write-Fail "[$t] 未返回结果"; continue }
        $icon = if ($s.failed -gt 0) { "❌" } else { "✅" }
        $totalCases  += [int]$s.total
        $totalPassed += [int]$s.passed
        $totalFailed += [int]$s.failed
        Write-Host ("  {0} {1,-12} 文件:{2,4}  用例:{3,6}  通过:{4,6}  失败:{5,4}  耗时:{6,6}s" -f `
            $icon,$t,$s.fileCount,$s.total,$s.passed,$s.failed,$s.duration_s) `
            -ForegroundColor (if ($s.failed -gt 0) { "Red" } else { "Gray" })
    }
    Write-Host "-" * 70 -ForegroundColor DarkGray
    Write-Host ("  📋 合计                  用例:{0,6}  通过:{1,6}  失败:{2,4}" -f $totalCases,$totalPassed,$totalFailed) `
        -ForegroundColor (if ($totalFailed -gt 0) { "Yellow" } else { "Cyan" })
}

Write-Info "原子结果目录：$AtomicDir"
Write-Info "如需生成独立报告：.\scripts\generate-tool-reports.ps1 -Tool <工具名>"
