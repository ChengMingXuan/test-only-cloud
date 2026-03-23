#!/usr/bin/env pwsh
<#
.SYNOPSIS
Cypress 串行执行脚本 - 避免登录限流（429错误）
#>

$SpecDir = "D:\2026\aiops.v2\testing\tests\cypress-tests\e2e"
$ReportsDir = "D:\2026\aiops.v2\testing\tests\cypress-tests\reports"

# 分组策略：按功能模块分别运行
$Groups = @(
    @{ Name = "core"; Specs = @("01-auth.cy.js", "02-permission.cy.js", "03-account.cy.js") },
    @{ Name = "energy"; Specs = @("09-energy.cy.js", "10-charging-monitor.cy.js") },
    @{ Name = "charging"; Specs = @("12-charging.cy.js", "14-settlement.cy.js") },
    @{ Name = "device"; Specs = @("16-device.cy.js", "17-digital-twin.cy.js") }
    # ... 继续添加其他分组
)

Write-Host "🚀 开始 Cypress 分组串行执行（降低认证压力）...`n" -ForegroundColor Green

foreach ($group in $Groups) {
    $groupName = $group.Name
    $specs = $group.Specs -join ","
    $logFile = "$ReportsDir\cypress-$groupName.log"
    
    Write-Host "📋 执行分组: $groupName" -ForegroundColor Cyan
    Write-Host "   规格: $specs`n"
    
    # 仅使用 2 个 worker 避免限流
    cd "D:\2026\aiops.v2\testing\tests\cypress-tests"
    npx cypress run `
        --config-file cypress.fast.config.js `
        --spec "e2e/$specs" `
        --headless `
        | Tee-Object -FilePath $logFile
    
    if ($LASTEXITCODE -ne 0) {
        Write-Host "⚠️  分组 '$groupName' 有失败，但继续下一个...`n" -ForegroundColor Yellow
    } else {
        Write-Host "✅ 分组 '$groupName' 全部通过`n" -ForegroundColor Green
    }
    
    # 串行延迟（给后端恢复的时间）
    Start-Sleep -Seconds 30
}

Write-Host "📊 所有分组执行完成！" -ForegroundColor Green
