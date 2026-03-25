"""
修复 Cypress 测试文件中的错误路由路径。
基于 .umirc.ts 中的实际路由配置，将父路由改为子路由，将不存在的路由改为正确路由。
"""
import re
import os
import glob

# 路由修正映射表：旧路由 -> 新路由
# 仅针对 visitAuth() 和 cy.visit() 中的路由
ROUTE_FIXES = {
    # ===== 03-30 系列：父路由 → 第一个有 component 的子路由 =====
    "'/station'": "'/station/list'",
    '"/station"': '"/station/list"',
    "'/device'": "'/device/registry/list'",
    '"/device"': '"/device/registry/list"',
    "'/workorder'": "'/workorder/list'",
    '"/workorder"': '"/workorder/list"',
    "'/settlement'": "'/settlement/list'",
    '"/settlement"': '"/settlement/list"',
    "'/simulator'": "'/simulator/charging'",
    '"/simulator"': '"/simulator/charging"',
    "'/tenant'": "'/tenant/list'",
    '"/tenant"': '"/tenant/list"',
    "'/system'": "'/system/user'",
    '"/system"': '"/system/user"',
    "'/monitor'": "'/monitor/online'",
    '"/monitor"': '"/monitor/online"',
    "'/account'": "'/account/profile'",
    '"/account"': '"/account/profile"',
    "'/message'": "'/message/notice'",
    '"/message"': '"/message/notice"',
    "'/workflow'": "'/workflow/template'",
    '"/workflow"': '"/workflow/template"',
    "'/log'": "'/log/center'",
    '"/log"': '"/log/center"',
    "'/report'": "'/report/center'",
    '"/report"': '"/report/center"',
    "'/security'": "'/security/ip-blacklist'",
    '"/security"': '"/security/ip-blacklist"',
    "'/ingestion'": "'/ingestion/sources'",
    '"/ingestion"': '"/ingestion/sources"',
    "'/analytics'": "'/analytics/event-tracking'",
    '"/analytics"': '"/analytics/event-tracking"',
    "'/blockchain'": "'/blockchain/dashboard'",
    '"/blockchain"': '"/blockchain/dashboard"',
    "'/digital-twin'": "'/digital-twin/overview'",
    '"/digital-twin"': '"/digital-twin/overview"',

    # ===== 05-permission =====
    "'/permission'": "'/system/permission'",
    '"/permission"': '"/system/permission"',

    # ===== 07-user（认证布局） → 系统用户 =====
    # 注意：仅在 visitAuth 上下文中修复，login 页面的 /user/login 不变

    # ===== 09-energy =====
    "'/energy'": "'/energy/vpp/dashboard'",
    '"/energy"': '"/energy/vpp/dashboard"',

    # ===== 12-ai =====
    "'/ai'": "'/ai/dashboard'",
    '"/ai"': '"/ai/dashboard"',

    # ===== 14-ruleengine =====
    "'/ruleengine'": "'/rule-engine/chains'",
    '"/ruleengine"': '"/rule-engine/chains"',

    # ===== 26-device-alerts =====
    "'/device/alerts'": "'/device/monitoring/alerts'",
    '"/device/alerts"': '"/device/monitoring/alerts"',

    # ===== 27-energy-advanced =====
    "'/energy/vpp'": "'/energy/vpp/dashboard'",
    '"/energy/vpp"': '"/energy/vpp/dashboard"',
    "'/finance'": "'/finance/invoice'",
    '"/finance"': '"/finance/invoice"',

    # ===== ui-* 能源/AI 父路由修复 =====
    "'/energy/microgrid'": "'/energy/microgrid/dashboard'",
    '"/energy/microgrid"': '"/energy/microgrid/dashboard"',
    "'/energy/pvessc'": "'/energy/pvessc/dashboard'",
    '"/energy/pvessc"': '"/energy/pvessc/dashboard"',
    "'/energy/sehs'": "'/energy/sehs/dashboard'",
    '"/energy/sehs"': '"/energy/sehs/dashboard"',
    "'/energy/carbontrade'": "'/energy/carbontrade/dashboard'",
    '"/energy/carbontrade"': '"/energy/carbontrade/dashboard"',
    "'/energy/electrade'": "'/energy/electrade/dashboard'",
    '"/energy/electrade"': '"/energy/electrade/dashboard"',
    "'/energy/demandresp'": "'/energy/demandresp/dashboard'",
    '"/energy/demandresp"': '"/energy/demandresp/dashboard"',
    "'/energy/energyeff'": "'/energy/energyeff/dashboard'",
    '"/energy/energyeff"': '"/energy/energyeff/dashboard"',
    "'/energy/multienergy'": "'/energy/multienergy/dashboard'",
    '"/energy/multienergy"': '"/energy/multienergy/dashboard"',
    "'/energy/safecontrol'": "'/energy/safecontrol/dashboard'",
    '"/energy/safecontrol"': '"/energy/safecontrol/dashboard"',
    "'/ai/prediction'": "'/ai/prediction/load'",
    '"/ai/prediction"': '"/ai/prediction/load"',
    "'/ai/health-monitor'": "'/ai/health-monitor/dashboard'",
    '"/ai/health-monitor"': '"/ai/health-monitor/dashboard"',

    # ===== 31-48 系列缩写/错误路径 =====
    # 32: AI 预测
    "'/ai/pred/load'": "'/ai/prediction/load'",
    "'/ai/pred/power'": "'/ai/prediction/power'",
    "'/ai/pred/price'": "'/ai/prediction/price'",
    "'/ai/peakvalley'": "'/ai/scenarios/peak-valley'",
    # 33: AI 高级
    "'/ai/health'": "'/ai/health-monitor/dashboard'",
    "'/ai/fault'": "'/ai/scenarios/fault-warning'",
    "'/ai/carbon'": "'/ai/scenarios/carbon'",
    "'/ai/market'": "'/ai/scenarios/market'",
    # 35: 分析
    "'/analytics/events'": "'/analytics/event-tracking'",
    "'/analytics/nlquery'": "'/analytics/nl-query'",
    # 36: 分析
    "'/analytics/userprofile'": "'/analytics/user-profile'",
    # 37: 区块链
    "'/blockchain/txns'": "'/blockchain/transactions'",
    "'/blockchain/carbon'": "'/blockchain/carbon-credit'",
    # 38: 充电
    "'/charging/stats'": "'/charging/dashboard'",
    "'/charging/card'": "'/charging/piles'",
    # 40: 代理/内容
    "'/agent'": "'/tenant/agent-manage'",
    "'/agent/commission'": "'/tenant/agent-manage'",
    "'/content'": "'/content/sites'",
    "'/media'": "'/content/media'",
    # 41: 开发者/边缘
    "'/developer/codegen'": "'/developer/code-gen'",
    "'/developer/forms'": "'/developer/form'",
    "'/edge'": "'/device/ops/dashboard'",
    # 42: 设备子页
    "'/device/asset'": "'/device/registry/asset'",
    "'/device/control'": "'/device/monitoring/control'",
    "'/device/firmware'": "'/device/registry/firmware'",
    "'/device/phm'": "'/ai/health-monitor/dashboard'",
    # 43-44: 数字孪生
    "'/digital-twin/scene'": "'/digital-twin/scene3d'",
    "'/digital-twin/simulation'": "'/digital-twin/overview'",
    # 45: 能源服务
    "'/energy/carbon-trade'": "'/energy/carbontrade/dashboard'",
    "'/energy/demand-resp'": "'/energy/demandresp/dashboard'",
    "'/energy/elec-trade'": "'/energy/electrade/dashboard'",
    # 46: 能源服务2
    "'/energy/eff'": "'/energy/energyeff/dashboard'",
    "'/energy/multi'": "'/energy/multienergy/dashboard'",
    "'/energy/safe'": "'/energy/safecontrol/dashboard'",
    # 47: 能源服务3
    "'/energy/orchestrator'": "'/energy/sehs/dashboard'",
    "'/station/map'": "'/station/monitor'",
    "'/station/stats'": "'/station/monitor'",
    # 48: 杂项
    "'/storage'": "'/system/storage'",
    "'/workorder/stats'": "'/workorder/list'",
    "'/settlement/invoice'": "'/settlement/list'",
    "'/ruleengine/debug'": "'/rule-engine/debug'",

    # ===== 54: 设备/接入/规则引擎 =====
    "'/device/list'": "'/device/registry/list'",
    "'/device/groups'": "'/device/registry/list'",
    "'/device/templates'": "'/device/registry/list'",
    "'/device/category'": "'/device/registry/list'",
    "'/device/attributes'": "'/device/registry/list'",
    "'/device/ota'": "'/device/registry/firmware'",
    "'/device/map'": "'/device/monitoring/realtime'",
    "'/device/realtime'": "'/device/monitoring/realtime'",
    "'/device/history'": "'/device/monitoring/realtime'",
    "'/device/alarm-rules'": "'/device/monitoring/alerts'",
    "'/device/alarms'": "'/device/monitoring/alerts'",
    "'/device/commands'": "'/device/monitoring/control'",
    "'/ingestion/endpoints'": "'/ingestion/sources'",
    "'/ingestion/protocols'": "'/ingestion/sources'",
    "'/ingestion/parsers'": "'/ingestion/sources'",
    "'/ingestion/streams'": "'/ingestion/sources'",
    "'/ingestion/stats'": "'/ingestion/sources'",
    "'/rule-engine/designer'": "'/rule-engine/chains'",
    "'/rule-engine/alarm-definitions'": "'/rule-engine/alarms'",

    # ===== 55: AI/IotCloud/PHM =====
    "'/ai/model-versions'": "'/ai/models'",
    "'/ai/inference-tasks'": "'/ai/training'",
    "'/ai/training-tasks'": "'/ai/training'",
    "'/ai/datasets'": "'/ai/models'",
    "'/ai/features'": "'/ai/models'",
    "'/iotcloud/connections'": "'/ingestion/sources'",
    "'/iotcloud/protocols'": "'/ingestion/sources'",
    "'/iotcloud/topics'": "'/ingestion/sources'",
    "'/iotcloud/rules'": "'/rule-engine/chains'",
    "'/iotcloud/devices'": "'/device/registry/list'",
    "'/iotcloud/dashboard'": "'/ai/dashboard'",
    "'/analytics/load-forecast'": "'/ai/prediction/load'",
    "'/analytics/fault-diagnosis'": "'/ai/scenarios/fault-warning'",
    "'/analytics/energy-forecast'": "'/ai/prediction/power'",
    "'/digital-twin/status'": "'/digital-twin/overview'",
    "'/digital-twin/3d-model'": "'/digital-twin/scene3d'",
    "'/digital-twin/calibration'": "'/digital-twin/overview'",
    "'/phm/health-score'": "'/ai/health-monitor/dashboard'",
    "'/phm/degradation'": "'/ai/health-monitor/dashboard'",
    "'/phm/maintenance'": "'/ai/health-monitor/dashboard'",
    "'/phm/prediction'": "'/ai/health-monitor/dashboard'",
    "'/phm/reports'": "'/ai/health-monitor/dashboard'",

    # ===== 56: VPP/微网/光储充 =====
    "'/energy/vpp/resources'": "'/energy/vpp/resource'",
    "'/energy/vpp/frequency'": "'/energy/vpp/dashboard'",
    "'/energy/vpp/market'": "'/energy/vpp/dashboard'",
    "'/energy/vpp/records'": "'/energy/vpp/dashboard'",
    "'/energy/vpp/revenue'": "'/energy/vpp/dashboard'",
    "'/energy/microgrid/topology'": "'/energy/microgrid/dashboard'",
    "'/energy/microgrid/devices'": "'/energy/microgrid/dashboard'",
    "'/energy/microgrid/scheduling'": "'/energy/microgrid/dashboard'",
    "'/energy/microgrid/reports'": "'/energy/microgrid/dashboard'",
    "'/energy/pvessc/config'": "'/energy/pvessc/dashboard'",
    "'/energy/pvessc/monitoring'": "'/energy/pvessc/dashboard'",
    "'/energy/pvessc/optimization'": "'/energy/pvessc/dashboard'",
    "'/energy/pvessc/reports'": "'/energy/pvessc/dashboard'",
    "'/energy/pvessc/analytics'": "'/energy/pvessc/dashboard'",

    # ===== 57: 电力交易/碳交易/需求响应（顶级路由错误）=====
    "'/electrade/dashboard'": "'/energy/electrade/dashboard'",
    "'/electrade/orders'": "'/energy/electrade/dashboard'",
    "'/electrade/prices'": "'/energy/electrade/dashboard'",
    "'/electrade/forecast'": "'/energy/electrade/dashboard'",
    "'/electrade/reports'": "'/energy/electrade/dashboard'",
    "'/carbontrade/dashboard'": "'/energy/carbontrade/dashboard'",
    "'/carbontrade/certificates'": "'/energy/carbontrade/dashboard'",
    "'/carbontrade/trading'": "'/energy/carbontrade/dashboard'",
    "'/carbontrade/reports'": "'/energy/carbontrade/dashboard'",
    "'/carbontrade/compliance'": "'/energy/carbontrade/dashboard'",
    "'/demand-response/dashboard'": "'/energy/demandresp/dashboard'",
    "'/demand-response/programs'": "'/energy/demandresp/dashboard'",
    "'/demand-response/events'": "'/energy/demandresp/dashboard'",
    "'/demand-response/reports'": "'/energy/demandresp/dashboard'",
    "'/demand-response/loads'": "'/energy/demandresp/dashboard'",

    # ===== 58: 能效/多能/安全/设备运维 =====
    "'/energy-eff/dashboard'": "'/energy/energyeff/dashboard'",
    "'/energy-eff/audit'": "'/energy/energyeff/dashboard'",
    "'/energy-eff/optimization'": "'/energy/energyeff/dashboard'",
    "'/energy-eff/benchmarks'": "'/energy/energyeff/dashboard'",
    "'/energy-eff/reports'": "'/energy/energyeff/dashboard'",
    "'/multi-energy/dashboard'": "'/energy/multienergy/dashboard'",
    "'/multi-energy/coupling'": "'/energy/multienergy/dashboard'",
    "'/multi-energy/optimization'": "'/energy/multienergy/dashboard'",
    "'/multi-energy/simulation'": "'/energy/multienergy/dashboard'",
    "'/multi-energy/economics'": "'/energy/multienergy/dashboard'",
    "'/safe-control/dashboard'": "'/energy/safecontrol/dashboard'",
    "'/safe-control/monitoring'": "'/energy/safecontrol/dashboard'",
    "'/safe-control/alarms'": "'/energy/safecontrol/dashboard'",
    "'/safe-control/emergency'": "'/energy/safecontrol/dashboard'",
    "'/safe-control/compliance'": "'/energy/safecontrol/dashboard'",
    "'/device-ops/dashboard'": "'/device/ops/dashboard'",
    "'/device-ops/maintenance'": "'/device/ops/maintenance'",
    "'/device-ops/inspection'": "'/device/ops/inspection'",
    "'/device-ops/spare-parts'": "'/device/ops/dashboard'",
    "'/device-ops/reports'": "'/device/ops/dashboard'",

    # ===== 59: 区块链/数字孪生 =====
    "'/blockchain/overview'": "'/blockchain/dashboard'",
    "'/blockchain/contracts'": "'/blockchain/contract'",
    "'/blockchain/wallets'": "'/blockchain/wallet'",
    "'/blockchain/query'": "'/blockchain/transactions'",
    "'/digital-twin/models'": "'/digital-twin/device'",
    "'/digital-twin/instances'": "'/digital-twin/overview'",

    # ===== 60: 分析/建站 =====
    "'/analytics/dashboard'": "'/analytics/event-tracking'",
    "'/analytics/reports'": "'/analytics/operations'",
    "'/analytics/data-sources'": "'/analytics/event-tracking'",
    "'/analytics/alerts'": "'/analytics/anomaly'",
    "'/analytics/segments'": "'/analytics/user-profile'",
    "'/builder/dashboard'": "'/builder/sites'",
    "'/builder/forms'": "'/builder/sites'",
    "'/builder/workflows'": "'/builder/sites'",
    "'/builder/templates'": "'/builder/sites'",
    "'/builder/themes'": "'/builder/sites'",

    # ===== 61: 内容/门户 =====
    "'/content/articles'": "'/content/sites'",
    "'/content/tags'": "'/content/sites'",
    "'/content/banners'": "'/content/sites'",
    "'/content/categories'": "'/content/sites'",
    "'/content/comments'": "'/content/sites'",
    "'/portal/home-config'": "'/portal/company'",
    "'/portal/themes'": "'/portal/company'",
    "'/portal/widgets'": "'/portal/company'",
    "'/portal/navigation'": "'/portal/company'",
    "'/portal/seo'": "'/portal/company'",

    # ===== 62: 租户/账户 =====
    "'/tenant/packages'": "'/tenant/list'",
    "'/tenant/billing'": "'/tenant/list'",
    "'/tenant/features'": "'/tenant/list'",
    "'/tenant/domains'": "'/tenant/list'",
    "'/tenant/quota'": "'/tenant/list'",
    "'/tenant/users'": "'/tenant/list'",
    "'/tenant/log'": "'/tenant/list'",
    "'/tenant/approval'": "'/tenant/list'",
    "'/tenant/migration'": "'/tenant/list'",
    "'/account/security'": "'/account/profile'",
    "'/account/sessions'": "'/account/profile'",
    "'/account/preferences'": "'/account/profile'",
    "'/account/api-keys'": "'/account/profile'",
    "'/account/activity'": "'/account/profile'",
    "'/account/billing'": "'/account/profile'",

    # ===== 63: 工单/工作流/开发者 =====
    "'/work-order/list'": "'/workorder/list'",
    "'/work-order/create'": "'/workorder/list'",
    "'/work-order/dispatch'": "'/workorder/dispatch'",
    "'/work-order/stats'": "'/workorder/list'",
    "'/work-order/types'": "'/workorder/list'",
    "'/message/templates'": "'/message/template'",
    "'/message/channels'": "'/message/notice'",
    "'/message/logs'": "'/message/notice'",
    "'/message/rules'": "'/message/notice'",
    "'/message/queue'": "'/message/notice'",
    "'/workflow/definitions'": "'/workflow/template'",
    "'/workflow/instances'": "'/workflow/template'",
    "'/workflow/tasks'": "'/workflow/template'",
    "'/workflow/forms'": "'/workflow/template'",
    "'/workflow/history'": "'/workflow/template'",
    "'/developer/sdk'": "'/developer/api'",
    "'/developer/webhooks'": "'/developer/api'",
    "'/developer/logs'": "'/developer/api'",
    "'/developer/sandbox'": "'/developer/api'",
    "'/developer/docs'": "'/developer/api'",

    # ===== 64: 杂项/平台 =====
    "'/platform/overview'": "'/platform/theme'",
    "'/platform/plugins'": "'/platform/theme'",
    "'/platform/extensions'": "'/platform/theme'",
    "'/platform/updates'": "'/platform/theme'",
    "'/platform/license'": "'/platform/theme'",
    "'/dashboard-home'": "'/dashboard'",
    "'/simulator/control'": "'/simulator/charging'",
    "'/simulator/nodes'": "'/simulator/charging'",
    "'/simulator/scenarios'": "'/simulator/charging'",
    "'/simulator/config'": "'/simulator/charging'",

    # ===== 65: 认证/错误/个人 =====
    "'/user/reset-password'": "'/user/forgot-password'",
    "'/user/verify-email'": "'/user/login'",
    "'/user/sso'": "'/user/login'",
    "'/404'": "'/nonexistent-test-page'",
    "'/500'": "'/nonexistent-test-page'",
    "'/profile/settings'": "'/account/settings'",
    "'/profile/notifications'": "'/account/profile'",
    "'/profile/security'": "'/account/profile'",
    "'/profile/linked-accounts'": "'/account/profile'",
    "'/profile/api-keys'": "'/account/profile'",
}

# 需要特殊处理的文件 - 07-user.cy.js 的 '/user' 需要改为 '/system/user'
# 但只在 visitAuth 上下文中（login 页面不改）
SPECIAL_FIXES = {
    '07-user.cy.js': {
        "cy.visitAuth('/user')": "cy.visitAuth('/system/user')",
    }
}


def fix_file(filepath):
    """修复单个文件中的路由路径"""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original = content
    filename = os.path.basename(filepath)
    fixes_applied = []
    
    # 特殊文件处理
    if filename in SPECIAL_FIXES:
        for old, new in SPECIAL_FIXES[filename].items():
            if old in content:
                content = content.replace(old, new)
                fixes_applied.append(f"  特殊: {old} → {new}")
    
    # 通用路由修复 - 对 visitAuth 和 visit 调用中的路由
    for old_route, new_route in ROUTE_FIXES.items():
        # 在 visitAuth() 上下文中替换
        old_visit = f"cy.visitAuth({old_route})"
        new_visit = f"cy.visitAuth({new_route})"
        if old_visit in content:
            content = content.replace(old_visit, new_visit)
            fixes_applied.append(f"  visitAuth: {old_route} → {new_route}")
        
        # 在 cy.visit() 上下文中替换
        old_visit2 = f"cy.visit({old_route})"
        new_visit2 = f"cy.visit({new_route})"
        if old_visit2 in content:
            content = content.replace(old_visit2, new_visit2)
            fixes_applied.append(f"  visit: {old_route} → {new_route}")
        
        # 在 page25() 函数参数中替换（49-65 系列）
        # 匹配 page25('xxx', '/route') 或 page25("xxx", "/route")
        # 路由是第二个参数
        old_page25 = f", {old_route})"
        new_page25 = f", {new_route})"
        if old_page25 in content:
            content = content.replace(old_page25, new_page25)
            fixes_applied.append(f"  page25: {old_route} → {new_route}")
        
        # 也处理 pagePath 变量赋值
        old_pagepath = f"pagePath = {old_route}"
        new_pagepath = f"pagePath = {new_route}"
        if old_pagepath in content:
            content = content.replace(old_pagepath, new_pagepath)
            fixes_applied.append(f"  pagePath: {old_route} → {new_route}")
    
    if content != original:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        return fixes_applied
    return []


def main():
    e2e_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'e2e')
    files = sorted(glob.glob(os.path.join(e2e_dir, '*.cy.js')))
    
    total_fixed = 0
    total_fixes = 0
    
    # 跳过已验证通过的文件
    skip_files = {'01-login.cy.js', '02-dashboard.cy.js'}
    
    for filepath in files:
        filename = os.path.basename(filepath)
        if filename in skip_files:
            continue
        
        fixes = fix_file(filepath)
        if fixes:
            total_fixed += 1
            total_fixes += len(fixes)
            print(f"✅ {filename}: {len(fixes)} 个修复")
            for fix in fixes:
                print(fix)
    
    print(f"\n📊 总计: 修复了 {total_fixed} 个文件，共 {total_fixes} 处路由替换")


if __name__ == '__main__':
    main()
