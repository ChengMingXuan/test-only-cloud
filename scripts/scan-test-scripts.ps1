<#
.SYNOPSIS
    测试脚本注册表扫描器 - 自动扫描6类测试脚本并生成/更新注册表
.DESCRIPTION
    扫描全部 6 类测试工具目录，自动识别每个脚本的状态：
      - active      正式测试脚本（编号化/命名规范的文件）
      - deprecated  已弃用（.bak / 旧版 v1 被 v2 替代 / 废弃文件）
      - debug       调试工件（_debug- 前缀）
      - tool        工具脚本（fix_* / generate* / verify* 等，非测试文件）

    输出：testing/tests/test-script-registry.json（全量注册表）

    版本迭代时使用 -CompareVersion 参数计算增量变更清单。

.PARAMETER Scan
    执行全量扫描并更新注册表
.PARAMETER CompareVersion
    与指定版本快照对比，输出增量变更（新增/修改/弃用）
.PARAMETER OutputPath
    注册表输出路径
.EXAMPLE
    .\scan-test-scripts.ps1 -Scan
    .\scan-test-scripts.ps1 -CompareVersion "baseline"
#>
param(
    [switch]$Scan,
    [string]$CompareVersion = "",
    [string]$OutputPath = "$PSScriptRoot\..\testing\tests\test-script-registry.json"
)

$ErrorActionPreference = "Continue"
$RootDir = (Resolve-Path "$PSScriptRoot\..").Path

# ─────────────────────────── 工具目录映射 ───────────────────────────
$ToolDirs = [ordered]@{
    pytest = @{
        testDirs  = @("testing\tests\api", "testing\tests\integration", "testing\tests\security", "testing\tests\e2e")
        testPattern = "test_*.py"
        toolDirs  = @()
        toolPattern = ""
    }
    cypress = @{
        testDirs  = @("testing\tests\cypress-tests\e2e")
        testPattern = "*.cy.js"
        toolDirs  = @("testing\tests\cypress-tests\_tools")
        toolPattern = ""
        dedicatedToolDir = $true
    }
    puppeteer = @{
        testDirs  = @("testing\tests\puppeteer-tests\tests")
        testPattern = "*.test.js"
        toolDirs  = @("testing\tests\puppeteer-tests")
        toolPattern = "generate*"
    }
    selenium = @{
        testDirs  = @("testing\tests\selenium-tests")
        testPattern = "test_*.py"
        toolDirs  = @()
        toolPattern = ""
    }
    playwright = @{
        testDirs  = @("testing\tests\playwright-tests\tests")
        testPattern = "*.spec.ts"
        toolDirs  = @("testing\tests\playwright-tests")
        toolPattern = "generate*"
    }
    k6 = @{
        testDirs  = @("testing\k6\scenarios")
        testPattern = "*.js"
        toolDirs  = @()
        toolPattern = ""
    }
}

# ─────────────────────────── 状态判定规则 ───────────────────────────
function Get-ScriptStatus {
    param([string]$FileName, [string]$RelPath, [string]$Tool)

    # debug: _debug- 前缀
    if ($FileName -match '^_debug') { return "debug" }

    # deprecated: .bak 后缀
    if ($FileName -match '\.bak$') { return "deprecated" }

    # deprecated: 存在 _v2 版本时，标记原版为 deprecated
    # （此逻辑在后处理中执行，此处仅标记 _v2 文件本身为 active）

    # tool: 工具脚本（fix_* / generate* 等非测试文件，在 toolDirs 顶层）
    $toolPatterns = $ToolDirs[$Tool].toolPattern
    if ($toolPatterns) {
        foreach ($pat in ($toolPatterns -split '\|')) {
            if ($FileName -like $pat) { return "tool" }
        }
    }

    return "active"
}

# ─────────────────────────── 扫描函数 ───────────────────────────
function Invoke-FullScan {
    $registry = [ordered]@{
        _meta = [ordered]@{
            version     = "1.0"
            generatedAt = (Get-Date).ToString("yyyy-MM-dd HH:mm:ss")
            generatedBy = "scan-test-scripts.ps1"
            description = "六类测试脚本全量注册表 - 统一管理脚本生命周期"
            statusDefinitions = [ordered]@{
                active     = "正式测试脚本，当前迭代使用"
                deprecated = "已弃用，不参与执行（.bak/被v2替代/不再适用）"
                debug      = "调试工件，非正式测试（_debug-前缀）"
                tool       = "工具脚本（fix/generate等），非测试文件"
            }
        }
        summary = [ordered]@{}
        tools   = [ordered]@{}
    }

    $grandActive = 0; $grandDeprecated = 0; $grandDebug = 0; $grandTool = 0

    foreach ($tool in $ToolDirs.Keys) {
        $toolCfg = $ToolDirs[$tool]
        $scripts = [System.Collections.ArrayList]::new()

        # 扫描测试脚本
        foreach ($dir in $toolCfg.testDirs) {
            $absDir = Join-Path $RootDir $dir
            if (-not (Test-Path $absDir)) { continue }

            # 正式测试文件
            $files = Get-ChildItem -Path $absDir -Filter $toolCfg.testPattern -Recurse -File -ErrorAction SilentlyContinue
            foreach ($f in $files) {
                $relPath = $f.FullName.Substring($RootDir.Length + 1) -replace '\\', '/'
                $status = Get-ScriptStatus -FileName $f.Name -RelPath $relPath -Tool $tool
                $hash = (Get-FileHash $f.FullName -Algorithm SHA256).Hash.Substring(0, 16)
                [void]$scripts.Add([ordered]@{
                    file     = $relPath
                    name     = $f.Name
                    status   = $status
                    hash     = $hash
                    size     = $f.Length
                    modified = $f.LastWriteTime.ToString("yyyy-MM-dd HH:mm:ss")
                })
            }

            # .bak 文件 → deprecated（不匹配正式 pattern，需单独捕获）
            $bakFiles = Get-ChildItem -Path $absDir -Filter "*.bak" -Recurse -File -ErrorAction SilentlyContinue
            foreach ($f in $bakFiles) {
                $relPath = $f.FullName.Substring($RootDir.Length + 1) -replace '\\', '/'
                # 避免重复（如果 .bak 恰好匹配了 testPattern）
                if ($scripts | Where-Object { $_.file -eq $relPath }) { continue }
                $hash = (Get-FileHash $f.FullName -Algorithm SHA256).Hash.Substring(0, 16)
                [void]$scripts.Add([ordered]@{
                    file             = $relPath
                    name             = $f.Name
                    status           = "deprecated"
                    hash             = $hash
                    size             = $f.Length
                    modified         = $f.LastWriteTime.ToString("yyyy-MM-dd HH:mm:ss")
                    deprecatedReason = "备份文件（.bak），已被正式版本替代"
                })
            }
        }

        # 扫描 pytest .bak 文件（可能在非 testDirs 的子目录中）
        if ($tool -eq "pytest") {
            $pytestBakDirs = @("testing\tests\api", "testing\tests\integration", "testing\tests\security", "testing\tests\e2e")
            foreach ($dir in $pytestBakDirs) {
                $absDir = Join-Path $RootDir $dir
                if (-not (Test-Path $absDir)) { continue }
                $bakFiles = Get-ChildItem -Path $absDir -Filter "*.py.bak" -Recurse -File -ErrorAction SilentlyContinue
                foreach ($f in $bakFiles) {
                    $relPath = $f.FullName.Substring($RootDir.Length + 1) -replace '\\', '/'
                    if ($scripts | Where-Object { $_.file -eq $relPath }) { continue }
                    $hash = (Get-FileHash $f.FullName -Algorithm SHA256).Hash.Substring(0, 16)
                    [void]$scripts.Add([ordered]@{
                        file             = $relPath
                        name             = $f.Name
                        status           = "deprecated"
                        hash             = $hash
                        size             = $f.Length
                        modified         = $f.LastWriteTime.ToString("yyyy-MM-dd HH:mm:ss")
                        deprecatedReason = "备份文件（.bak），已被正式版本替代"
                    })
                }
            }
        }

        # 扫描工具脚本（仅顶层 toolDirs，不递归到测试子目录）
        foreach ($dir in $toolCfg.toolDirs) {
            $absDir = Join-Path $RootDir $dir
            if (-not (Test-Path $absDir)) { continue }

            $files = Get-ChildItem -Path $absDir -File -ErrorAction SilentlyContinue
            foreach ($f in $files) {
                $isToolFile = $false
                # 专用工具目录（如 _tools/）：所有文件均视为工具脚本
                if ($toolCfg.dedicatedToolDir) {
                    $isToolFile = $true
                } else {
                    if ($toolCfg.toolPattern) {
                        foreach ($pat in ($toolCfg.toolPattern -split '\|')) {
                            if ($f.Name -like $pat) { $isToolFile = $true; break }
                        }
                    }
                    # 捕获散落的 .py/.txt 工具脚本
                    if (-not $isToolFile -and $f.Extension -eq '.py') { $isToolFile = $true }
                    if (-not $isToolFile -and $f.Extension -eq '.txt') { $isToolFile = $true }
                }

                if ($isToolFile) {
                    $relPath = $f.FullName.Substring($RootDir.Length + 1) -replace '\\', '/'
                    $hash = (Get-FileHash $f.FullName -Algorithm SHA256).Hash.Substring(0, 16)
                    [void]$scripts.Add([ordered]@{
                        file     = $relPath
                        name     = $f.Name
                        status   = "tool"
                        hash     = $hash
                        size     = $f.Length
                        modified = $f.LastWriteTime.ToString("yyyy-MM-dd HH:mm:ss")
                    })
                }
            }
        }

        # 后处理：存在 _v2 版本时标记原版 v1 为 deprecated
        $v2Files = $scripts | Where-Object { $_.name -match '_v2\.' -and $_.status -ne 'tool' }
        foreach ($v2 in $v2Files) {
            $v1Name = $v2.name -replace '_v2\.', '.'
            $v1Entry = $scripts | Where-Object { $_.name -eq $v1Name -and $_.status -eq 'active' }
            if ($v1Entry) {
                $v1Entry.status = "deprecated"
                $v1Entry['deprecatedBy'] = $v2.file
                $v1Entry['deprecatedReason'] = "已被 _v2 版本替代"
            }
        }

        # 统计（用 @() 包装避免单项 hashtable 的 .Count 错误）
        $active     = @($scripts | Where-Object { $_.status -eq 'active' }).Count
        $deprecated = @($scripts | Where-Object { $_.status -eq 'deprecated' }).Count
        $debug      = @($scripts | Where-Object { $_.status -eq 'debug' }).Count
        $toolCount  = @($scripts | Where-Object { $_.status -eq 'tool' }).Count

        $grandActive     += $active
        $grandDeprecated += $deprecated
        $grandDebug      += $debug
        $grandTool       += $toolCount

        $registry.tools[$tool] = [ordered]@{
            summary = [ordered]@{
                total      = $scripts.Count
                active     = $active
                deprecated = $deprecated
                debug      = $debug
                tool       = $toolCount
            }
            scripts = @($scripts | Sort-Object { $_.file })
        }

        $icon = @{ pytest="🐍"; cypress="🌲"; puppeteer="🤖"; selenium="🌐"; playwright="🎭"; k6="⚡" }[$tool]
        Write-Host "  $icon $($tool.PadRight(12)) active=$($active.ToString().PadLeft(4))  deprecated=$($deprecated.ToString().PadLeft(3))  debug=$($debug.ToString().PadLeft(3))  tool=$($toolCount.ToString().PadLeft(3))  total=$($scripts.Count)" -ForegroundColor Gray
    }

    $registry.summary = [ordered]@{
        totalScripts = $grandActive + $grandDeprecated + $grandDebug + $grandTool
        active       = $grandActive
        deprecated   = $grandDeprecated
        debug        = $grandDebug
        tool         = $grandTool
    }

    return $registry
}

# ─────────────────────────── 版本对比函数 ───────────────────────────
function Compare-WithVersion {
    param([string]$Version, $CurrentRegistry)

    $versionRegistryPath = Join-Path $RootDir "TestResults\versions\$Version\test-script-registry.json"
    if (-not (Test-Path $versionRegistryPath)) {
        Write-Host "❌ 版本 $Version 无脚本注册表快照：$versionRegistryPath" -ForegroundColor Red
        return $null
    }

    $oldReg = Get-Content $versionRegistryPath -Raw -Encoding UTF8 | ConvertFrom-Json
    $changes = [ordered]@{
        version    = $Version
        comparedAt = (Get-Date).ToString("yyyy-MM-dd HH:mm:ss")
        added      = [System.Collections.ArrayList]::new()
        modified   = [System.Collections.ArrayList]::new()
        deprecated = [System.Collections.ArrayList]::new()
        removed    = [System.Collections.ArrayList]::new()
    }

    # 构建旧版索引 file→hash
    $oldIndex = @{}
    foreach ($tool in @("pytest","cypress","puppeteer","selenium","playwright","k6")) {
        if ($null -eq $oldReg.tools.$tool) { continue }
        foreach ($s in @($oldReg.tools.$tool.scripts)) {
            $oldIndex[$s.file] = [ordered]@{ hash=$s.hash; status=$s.status }
        }
    }

    # 构建新版索引
    $newIndex = @{}
    foreach ($tool in $CurrentRegistry.tools.Keys) {
        foreach ($s in @($CurrentRegistry.tools[$tool].scripts)) {
            $newIndex[$s.file] = [ordered]@{ hash=$s.hash; status=$s.status }
        }
    }

    # 新增：新版有、旧版无
    foreach ($file in $newIndex.Keys) {
        if (-not $oldIndex.ContainsKey($file)) {
            [void]$changes.added.Add([ordered]@{ file=$file; status=$newIndex[$file].status })
        }
    }

    # 修改：hash 不同
    foreach ($file in $newIndex.Keys) {
        if ($oldIndex.ContainsKey($file) -and $oldIndex[$file].hash -ne $newIndex[$file].hash) {
            [void]$changes.modified.Add([ordered]@{ file=$file; oldHash=$oldIndex[$file].hash; newHash=$newIndex[$file].hash })
        }
    }

    # 新弃用：旧版 active → 新版 deprecated
    foreach ($file in $newIndex.Keys) {
        if ($oldIndex.ContainsKey($file) -and $oldIndex[$file].status -eq 'active' -and $newIndex[$file].status -eq 'deprecated') {
            [void]$changes.deprecated.Add([ordered]@{ file=$file })
        }
    }

    # 移除：旧版有、新版无（理论上不删文件，但做安全检测）
    foreach ($file in $oldIndex.Keys) {
        if (-not $newIndex.ContainsKey($file)) {
            [void]$changes.removed.Add([ordered]@{ file=$file; oldStatus=$oldIndex[$file].status })
        }
    }

    return $changes
}

# ─────────────────────────── 主逻辑 ───────────────────────────
if ($Scan -or (-not $CompareVersion)) {
    Write-Host "🔍 扫描六类测试脚本..." -ForegroundColor Cyan

    $registry = Invoke-FullScan

    # 输出注册表
    $registry | ConvertTo-Json -Depth 10 | Out-File $OutputPath -Encoding UTF8 -Force

    Write-Host ""
    Write-Host "╔════════════════════════════════════════════════════╗" -ForegroundColor Cyan
    Write-Host "║  📋 测试脚本注册表已生成                            ║" -ForegroundColor Cyan
    Write-Host "╚════════════════════════════════════════════════════╝" -ForegroundColor Cyan
    Write-Host "  路径：$OutputPath" -ForegroundColor Gray
    Write-Host "  总计：$($registry.summary.totalScripts) 个脚本" -ForegroundColor White
    Write-Host "    ✅ active:     $($registry.summary.active)" -ForegroundColor Green
    Write-Host "    🚫 deprecated: $($registry.summary.deprecated)" -ForegroundColor Yellow
    Write-Host "    🐛 debug:      $($registry.summary.debug)" -ForegroundColor DarkYellow
    Write-Host "    🔧 tool:       $($registry.summary.tool)" -ForegroundColor DarkGray
}

if ($CompareVersion) {
    Write-Host "`n📊 与版本 $CompareVersion 对比..." -ForegroundColor Cyan

    # 如果未扫描，先扫描
    if (-not $registry) {
        $registry = Invoke-FullScan
    }

    $changes = Compare-WithVersion -Version $CompareVersion -CurrentRegistry $registry
    if ($null -ne $changes) {
        Write-Host "  ➕ 新增：$($changes.added.Count) 个脚本" -ForegroundColor Green
        Write-Host "  ✏️ 修改：$($changes.modified.Count) 个脚本" -ForegroundColor Yellow
        Write-Host "  🚫 弃用：$($changes.deprecated.Count) 个脚本" -ForegroundColor DarkYellow
        Write-Host "  ❌ 移除：$($changes.removed.Count) 个脚本" -ForegroundColor Red

        # 输出变更清单
        $changesPath = Join-Path (Split-Path $OutputPath) "script-changes-vs-$CompareVersion.json"
        $changes | ConvertTo-Json -Depth 10 | Out-File $changesPath -Encoding UTF8 -Force
        Write-Host "  变更清单：$changesPath" -ForegroundColor Gray
    }
}
