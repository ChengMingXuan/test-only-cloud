"""
修复 Cypress 测试文件中的错误路由路径 - V2。
包含所有遗漏的虚构路由映射。
"""
import re
import os
import glob

# 完整路由修正映射表
# 格式：错误路由 -> 正确路由（.umirc.ts 中有 component 的叶子路由）
ROUTE_MAP = {
    # ===== 54: 设备/接入/规则引擎 =====
    '/device/list': '/device/registry/list',
    '/device/groups': '/device/registry/list',
    '/device/templates': '/device/registry/list',
    '/device/category': '/device/registry/list',
    '/device/attributes': '/device/registry/list',
    '/device/firmware': '/device/registry/firmware',
    '/device/ota': '/device/registry/firmware',
    '/device/map': '/device/monitoring/realtime',
    '/device/realtime': '/device/monitoring/realtime',
    '/device/history': '/device/monitoring/realtime',
    '/device/alarm-rules': '/device/monitoring/alerts',
    '/device/alarms': '/device/monitoring/alerts',
    '/device/commands': '/device/monitoring/control',
    '/device/control': '/device/monitoring/control',
    '/device/asset': '/device/registry/asset',
    '/device/phm': '/ai/health-monitor/dashboard',
    '/ingestion/endpoints': '/ingestion/sources',
    '/ingestion/protocols': '/ingestion/sources',
    '/ingestion/parsers': '/ingestion/sources',
    '/ingestion/streams': '/ingestion/sources',
    '/ingestion/stats': '/ingestion/sources',
    '/rule-engine/designer': '/rule-engine/chains',
    '/rule-engine/alarm-definitions': '/rule-engine/alarms',
    '/rule-engine/logs': '/rule-engine/debug',

    # ===== 55: AI/IotCloud/PHM =====
    '/ai/model-versions': '/ai/models',
    '/ai/inference-tasks': '/ai/training',
    '/ai/training-tasks': '/ai/training',
    '/ai/datasets': '/ai/models',
    '/ai/features': '/ai/models',
    '/ai/pred/load': '/ai/prediction/load',
    '/ai/pred/power': '/ai/prediction/power',
    '/ai/pred/price': '/ai/prediction/price',
    '/ai/peakvalley': '/ai/scenarios/peak-valley',
    '/ai/health': '/ai/health-monitor/dashboard',
    '/ai/fault': '/ai/scenarios/fault-warning',
    '/ai/carbon': '/ai/scenarios/carbon',
    '/ai/market': '/ai/scenarios/market',
    '/iotcloud/connections': '/ingestion/sources',
    '/iotcloud/protocols': '/ingestion/sources',
    '/iotcloud/topics': '/ingestion/sources',
    '/iotcloud/messages': '/ingestion/sources',
    '/iotcloud/telemetry': '/device/monitoring/realtime',
    '/iotcloud/rules': '/rule-engine/chains',
    '/iotcloud/devices': '/device/registry/list',
    '/iotcloud/dashboard': '/ai/dashboard',
    '/analytics/load-forecast': '/ai/prediction/load',
    '/analytics/fault-diagnosis': '/ai/scenarios/fault-warning',
    '/analytics/energy-forecast': '/ai/prediction/power',
    '/digital-twin/status': '/digital-twin/monitor',
    '/digital-twin/3d-model': '/digital-twin/scene3d',
    '/digital-twin/calibration': '/digital-twin/overview',
    '/phm/health-score': '/ai/health-monitor/dashboard',
    '/phm/life-prediction': '/ai/health-monitor/prediction',
    '/phm/maintenance-advice': '/ai/health-monitor/lifecycle',
    '/phm/history-trend': '/ai/health-monitor/analysis',
    '/phm/degradation': '/ai/health-monitor/dashboard',
    '/phm/maintenance': '/ai/health-monitor/lifecycle',
    '/phm/prediction': '/ai/health-monitor/prediction',
    '/phm/reports': '/ai/health-monitor/dashboard',

    # ===== 56: VPP/微网/光储充 =====
    '/energy/vpp/resources': '/energy/vpp/resource',
    '/energy/vpp/revenue': '/energy/vpp/performance',
    '/energy/vpp/frequency': '/energy/vpp/dashboard',
    '/energy/vpp/market': '/energy/vpp/dashboard',
    '/energy/vpp/records': '/energy/vpp/dashboard',
    '/energy/microgrid/optimize': '/energy/microgrid/optimization',
    '/energy/microgrid/topology': '/energy/microgrid/dashboard',
    '/energy/microgrid/monitor': '/energy/microgrid/dashboard',
    '/energy/microgrid/devices': '/energy/microgrid/dashboard',
    '/energy/microgrid/scheduling': '/energy/microgrid/dashboard',
    '/energy/microgrid/reports': '/energy/microgrid/dashboard',
    '/energy/microgrid/protection': '/energy/microgrid/dashboard',
    '/energy/microgrid/grid-mode': '/energy/microgrid/dashboard',
    '/energy/microgrid/report': '/energy/microgrid/dashboard',
    '/energy/pvessc/overview': '/energy/pvessc/dashboard',
    '/energy/pvessc/config': '/energy/pvessc/dashboard',
    '/energy/pvessc/monitoring': '/energy/pvessc/dashboard',
    '/energy/pvessc/optimization': '/energy/pvessc/dashboard',
    '/energy/pvessc/reports': '/energy/pvessc/dashboard',
    '/energy/pvessc/analytics': '/energy/pvessc/dashboard',
    '/energy/pvessc/pv-monitor': '/energy/pvessc/dashboard',
    '/energy/pvessc/ess-monitor': '/energy/pvessc/dashboard',
    '/energy/pvessc/charge-strategy': '/energy/pvessc/dashboard',
    '/energy/pvessc/power-adjust': '/energy/pvessc/dashboard',
    '/energy/pvessc/power-quality': '/energy/pvessc/dashboard',
    '/energy/pvessc/soc': '/energy/pvessc/dashboard',
    '/energy/pvessc/devices': '/energy/pvessc/dashboard',
    '/energy/pvessc/report': '/energy/pvessc/dashboard',

    # ===== 57: 电力交易/碳交易/需求响应（顶级路由全错）=====
    '/electrade/dashboard': '/energy/electrade/dashboard',
    '/electrade/orders': '/energy/electrade/dashboard',
    '/electrade/prices': '/energy/electrade/dashboard',
    '/electrade/forecast': '/energy/electrade/dashboard',
    '/electrade/reports': '/energy/electrade/dashboard',
    '/electrade/settlement': '/energy/electrade/settlement',
    '/electrade/spot': '/energy/electrade/dashboard',
    '/electrade/forward': '/energy/electrade/dashboard',
    '/electrade/ancillary': '/energy/electrade/dashboard',
    '/electrade/market-bid': '/energy/electrade/dashboard',
    '/electrade/results': '/energy/electrade/dashboard',
    '/electrade/users': '/energy/electrade/dashboard',
    '/electrade/params': '/energy/electrade/dashboard',
    '/electrade/price-curve': '/energy/electrade/dashboard',
    '/electrade/load-curve': '/energy/electrade/dashboard',
    '/electrade/logs': '/energy/electrade/dashboard',
    '/carbontrade/dashboard': '/energy/carbontrade/dashboard',
    '/carbontrade/certificates': '/energy/carbontrade/dashboard',
    '/carbontrade/trading': '/energy/carbontrade/dashboard',
    '/carbontrade/reports': '/energy/carbontrade/dashboard',
    '/carbontrade/compliance': '/energy/carbontrade/dashboard',
    '/carbontrade/quota': '/energy/carbontrade/dashboard',
    '/carbontrade/market': '/energy/carbontrade/dashboard',
    '/carbontrade/account': '/energy/carbontrade/dashboard',
    '/carbontrade/verify': '/energy/carbontrade/dashboard',
    '/carbontrade/ccer': '/energy/carbontrade/dashboard',
    '/carbontrade/records': '/energy/carbontrade/dashboard',
    '/carbontrade/offset': '/energy/carbontrade/dashboard',
    '/demand-response/dashboard': '/energy/demandresp/dashboard',
    '/demand-response/programs': '/energy/demandresp/programs',
    '/demand-response/events': '/energy/demandresp/dashboard',
    '/demand-response/reports': '/energy/demandresp/dashboard',
    '/demand-response/loads': '/energy/demandresp/dashboard',
    '/demand-response/projects': '/energy/demandresp/programs',
    '/demand-response/resources': '/energy/demandresp/dashboard',
    '/demand-response/invitations': '/energy/demandresp/dashboard',
    '/demand-response/executions': '/energy/demandresp/dashboard',
    '/demand-response/incentive': '/energy/demandresp/dashboard',
    '/demand-response/analysis': '/energy/demandresp/dashboard',

    # ===== 58: 能效/多能/安全/设备运维 =====
    '/energy-eff/dashboard': '/energy/energyeff/dashboard',
    '/energy-eff/audit': '/energy/energyeff/audit',
    '/energy-eff/optimization': '/energy/energyeff/optimization',
    '/energy-eff/benchmarks': '/energy/energyeff/dashboard',
    '/energy-eff/reports': '/energy/energyeff/dashboard',
    '/energy-eff/overview': '/energy/energyeff/dashboard',
    '/energy-eff/monitor': '/energy/energyeff/dashboard',
    '/energy-eff/analysis': '/energy/energyeff/dashboard',
    '/energy-eff/benchmark': '/energy/energyeff/dashboard',
    '/energy-eff/diagnosis': '/energy/energyeff/dashboard',
    '/energy-eff/report': '/energy/energyeff/dashboard',
    '/multi-energy/dashboard': '/energy/multienergy/dashboard',
    '/multi-energy/coupling': '/energy/multienergy/coupling',
    '/multi-energy/optimization': '/energy/multienergy/dashboard',
    '/multi-energy/simulation': '/energy/multienergy/dashboard',
    '/multi-energy/economics': '/energy/multienergy/dashboard',
    '/multi-energy/overview': '/energy/multienergy/dashboard',
    '/multi-energy/cooling': '/energy/multienergy/dashboard',
    '/multi-energy/heating': '/energy/multienergy/dashboard',
    '/multi-energy/gas': '/energy/multienergy/dashboard',
    '/multi-energy/optimize': '/energy/multienergy/dashboard',
    '/safe-control/dashboard': '/energy/safecontrol/dashboard',
    '/safe-control/monitoring': '/energy/safecontrol/monitoring',
    '/safe-control/alarms': '/energy/safecontrol/dashboard',
    '/safe-control/emergency': '/energy/safecontrol/dashboard',
    '/safe-control/compliance': '/energy/safecontrol/dashboard',
    '/safe-control/monitor': '/energy/safecontrol/monitoring',
    '/safe-control/interlock': '/energy/safecontrol/dashboard',
    '/safe-control/report': '/energy/safecontrol/dashboard',
    '/safe-control/config': '/energy/safecontrol/dashboard',
    '/device-ops/dashboard': '/device/ops/dashboard',
    '/device-ops/maintenance': '/device/ops/maintenance',
    '/device-ops/inspection': '/device/ops/inspection',
    '/device-ops/spare-parts': '/device/ops/dashboard',
    '/device-ops/reports': '/device/ops/dashboard',
    '/device-ops/overview': '/device/ops/dashboard',
    '/device-ops/repair': '/device/ops/maintenance',
    '/device-ops/report': '/device/ops/dashboard',

    # ===== 59: 区块链/数字孪生 =====
    '/blockchain/overview': '/blockchain/dashboard',
    '/blockchain/contracts': '/blockchain/contract',
    '/blockchain/wallets': '/blockchain/wallet',
    '/blockchain/query': '/blockchain/transactions',
    '/blockchain/evidence': '/blockchain/certificate',
    '/blockchain/nodes': '/blockchain/dashboard',
    '/blockchain/events': '/blockchain/dashboard',
    '/blockchain/audit': '/blockchain/dashboard',
    '/digital-twin/models': '/digital-twin/device',
    '/digital-twin/instances': '/digital-twin/overview',
    '/digital-twin/scene': '/digital-twin/scene3d',
    '/digital-twin/3d-scene': '/digital-twin/scene3d',
    '/digital-twin/simulation': '/digital-twin/overview',
    '/digital-twin/alerts': '/digital-twin/monitor',
    '/digital-twin/history': '/digital-twin/overview',
    '/digital-twin/config': '/digital-twin/overview',
    '/digital-twin/report': '/digital-twin/overview',

    # ===== 60: 分析/建站 =====
    '/analytics/dashboard': '/analytics/event-tracking',
    '/analytics/reports': '/analytics/operations',
    '/analytics/data-sources': '/analytics/event-tracking',
    '/analytics/alerts': '/analytics/anomaly',
    '/analytics/segments': '/analytics/user-profile',
    '/analytics/events': '/analytics/event-tracking',
    '/analytics/nlquery': '/analytics/nl-query',
    '/analytics/userprofile': '/analytics/user-profile',
    '/analytics/visualizations': '/analytics/event-tracking',
    '/analytics/custom-reports': '/analytics/operations',
    '/analytics/scheduled': '/analytics/event-tracking',
    '/analytics/exports': '/analytics/event-tracking',
    '/analytics/templates': '/analytics/event-tracking',
    '/analytics/sharing': '/analytics/event-tracking',
    '/builder/dashboard': '/builder/sites',
    '/builder/forms': '/builder/sites',
    '/builder/workflows': '/builder/sites',
    '/builder/templates': '/builder/sites',
    '/builder/themes': '/builder/sites',
    '/builder/pages': '/builder/sites',
    '/builder/components': '/builder/sites',
    '/builder/data-sources': '/builder/sites',
    '/builder/publish': '/builder/sites',

    # ===== 61: 内容/门户 =====
    '/content/articles': '/content/sites',
    '/content/tags': '/content/sites',
    '/content/banners': '/content/sites',
    '/content/categories': '/content/sites',
    '/content/comments': '/content/sites',
    '/content/pages': '/content/sites',
    '/content/media': '/content/media',
    '/content/templates': '/content/sites',
    '/content/navigation': '/content/sites',
    '/content/widgets': '/content/sites',
    '/content/seo': '/content/sites',
    '/content/analytics': '/content/sites',
    '/content/settings': '/content/sites',
    '/portal/home-config': '/portal/company',
    '/portal/themes': '/portal/company',
    '/portal/widgets': '/portal/company',
    '/portal/navigation': '/portal/company',
    '/portal/seo': '/portal/company',
    '/portal/footer': '/portal/company',
    '/portal/header': '/portal/company',
    '/portal/pages': '/portal/company',
    '/portal/blog': '/portal/company',
    '/portal/faq': '/portal/company',
    '/portal/contact': '/portal/company',
    '/portal/analytics': '/portal/company',

    # ===== 62: 租户/账户 =====
    '/tenant/packages': '/tenant/list',
    '/tenant/billing': '/tenant/list',
    '/tenant/features': '/tenant/list',
    '/tenant/domains': '/tenant/list',
    '/tenant/quota': '/tenant/list',
    '/tenant/users': '/tenant/list',
    '/tenant/log': '/tenant/list',
    '/tenant/approval': '/tenant/list',
    '/tenant/migration': '/tenant/list',
    '/account/security': '/account/profile',
    '/account/sessions': '/account/profile',
    '/account/preferences': '/account/profile',
    '/account/api-keys': '/account/profile',
    '/account/activity': '/account/profile',
    '/account/billing': '/account/profile',
    '/account/notifications': '/account/profile',
    '/account/linked-accounts': '/account/profile',
    '/account/privacy': '/account/profile',
    '/account/devices': '/account/profile',

    # ===== 63: 工单/工作流/开发者 =====
    '/work-order/list': '/workorder/list',
    '/work-order/create': '/workorder/list',
    '/work-order/dispatch': '/workorder/dispatch',
    '/work-order/stats': '/workorder/list',
    '/work-order/types': '/workorder/list',
    '/work-order/templates': '/workorder/list',
    '/work-order/pending': '/workorder/list',
    '/work-order/in-progress': '/workorder/list',
    '/work-order/completed': '/workorder/list',
    '/work-order/statistics': '/workorder/list',
    '/work-order/categories': '/workorder/list',
    '/work-order/rules': '/workorder/list',
    '/work-order/escalation': '/workorder/list',
    '/work-order/sla': '/workorder/list',
    '/message/templates': '/message/template',
    '/message/channels': '/message/notice',
    '/message/logs': '/message/notice',
    '/message/rules': '/message/notice',
    '/message/queue': '/message/notice',
    '/workflow/definitions': '/workflow/template',
    '/workflow/instances': '/workflow/template',
    '/workflow/tasks': '/workflow/template',
    '/workflow/forms': '/workflow/template',
    '/workflow/history': '/workflow/template',
    '/developer/sdk': '/developer/api',
    '/developer/webhooks': '/developer/api',
    '/developer/logs': '/developer/api',
    '/developer/sandbox': '/developer/api',
    '/developer/docs': '/developer/api',
    '/developer/codegen': '/developer/code-gen',
    '/developer/forms': '/developer/form',
    '/developer/playground': '/developer/api',
    '/developer/marketplace': '/developer/api',
    '/developer/changelog': '/developer/api',

    # ===== 64: 杂项/平台 =====
    '/platform/overview': '/platform/theme',
    '/platform/plugins': '/platform/theme',
    '/platform/extensions': '/platform/theme',
    '/platform/updates': '/platform/theme',
    '/platform/license': '/platform/theme',
    '/platform/status': '/platform/theme',
    '/platform/health': '/platform/theme',
    '/dashboard-home': '/dashboard',
    '/simulator/control': '/simulator/charging',
    '/simulator/nodes': '/simulator/charging',
    '/simulator/scenarios': '/simulator/charging',
    '/simulator/config': '/simulator/charging',
    '/open-platform/oauth-apps': '/open-platform/oauth-app',
    '/open-platform/api-keys': '/open-platform/oauth-app',
    '/open-platform/webhooks': '/open-platform/oauth-app',
    '/open-platform/docs': '/open-platform/oauth-app',
    '/ops/tools': '/ops/tools',
    '/ops/health': '/ops/tools',
    '/ops/backup': '/ops/tools',
    '/help/center': '/help/center',
    '/help/faq': '/help/center',
    '/help/feedback': '/help/center',
    '/help/changelog': '/help/center',
    '/i18n/config': '/i18n/config',
    '/i18n/translations': '/i18n/config',
    '/i18n/export': '/i18n/config',
    '/report/templates': '/report/template',
    '/report/scheduler': '/report/center',
    '/report/history': '/report/center',

    # ===== 49-50: 系统管理虚构路由 =====
    '/system/servicemesh': '/system/config',
    '/system/file': '/system/storage',
    '/system/job': '/system/config',
    '/system/cache': '/system/config',
    '/system/datasource': '/system/config',
    '/system/data-permission': '/system/permission',
    '/system/high-risk-permission': '/system/permission',
    '/system/temporary-auth': '/system/permission',
    '/system/channel': '/system/config',
    '/system/auth-config': '/system/config',
    '/system/rate-limiting': '/system/config',
    '/system/version': '/system/config',
    '/system/announcement': '/system/config',
    '/system/backup': '/system/config',

    # ===== 51: 系统监控虚构路由 =====
    '/monitor/login-log': '/monitor/log',
    '/monitor/sql': '/monitor/log',
    '/monitor/tracing': '/monitor/log',

    # ===== 52: 安全中心虚构路由 =====
    '/security/sensitive-word': '/security/compliance',
    '/security/data-mask': '/security/compliance',
    '/security/audit': '/security/compliance',
    '/security/real-name-auth': '/security/compliance',

    # ===== 65: 认证/错误/个人 =====
    '/user/reset-password': '/user/forgot-password',
    '/user/verify-email': '/user/login',
    '/user/sso': '/user/login',
    '/user/mfa': '/user/login',
    '/user/account-locked': '/user/login',
    '/user/pending-approval': '/user/login',
    '/404': '/welcome',
    '/500': '/welcome',
    '/profile/settings': '/account/settings',
    '/profile/notifications': '/account/profile',
    '/profile/security': '/account/profile',
    '/profile/linked-accounts': '/account/profile',
    '/profile/api-keys': '/account/profile',

    # ===== 其他杂项 =====
    '/edge': '/device/ops/dashboard',
    '/agent': '/tenant/agent-manage',
    '/agent/commission': '/tenant/agent-manage',
    '/media': '/content/media',
    '/storage': '/system/storage',
    '/workorder/stats': '/workorder/list',
    '/settlement/invoice': '/settlement/list',
    '/ruleengine/debug': '/rule-engine/debug',
    '/station/map': '/station/monitor',
    '/station/stats': '/station/monitor',
    '/energy/orchestrator': '/energy/sehs/dashboard',
    '/energy/carbon-trade': '/energy/carbontrade/dashboard',
    '/energy/demand-resp': '/energy/demandresp/dashboard',
    '/energy/elec-trade': '/energy/electrade/dashboard',
    '/energy/eff': '/energy/energyeff/dashboard',
    '/energy/multi': '/energy/multienergy/dashboard',
    '/energy/safe': '/energy/safecontrol/dashboard',
    '/charging/stats': '/charging/dashboard',
    '/charging/card': '/charging/piles',
    '/blockchain/txns': '/blockchain/transactions',
    '/blockchain/carbon': '/blockchain/carbon-credit',
}


def fix_file(filepath):
    """修复单个文件中的路由路径"""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original = content
    fixes_applied = []
    
    # 按路由长度降序排列，优先匹配更长的路由（避免 /energy 匹配到 /energy/vpp 等）
    sorted_routes = sorted(ROUTE_MAP.items(), key=lambda x: len(x[0]), reverse=True)
    
    for old_route, new_route in sorted_routes:
        if old_route == new_route:
            continue
        
        # 匹配各种引号格式
        for quote in ["'", '"']:
            old_quoted = f"{quote}{old_route}{quote}"
            new_quoted = f"{quote}{new_route}{quote}"
            
            # 匹配 visitAuth/visit/page25 参数中的路由
            # 使用正则确保精确匹配（不匹配子路径）
            pattern = re.compile(
                r'(?<=[(\s,])' + re.escape(old_quoted) + r'(?=[)\s,])',
                re.MULTILINE
            )
            
            if pattern.search(content):
                new_content = pattern.sub(new_quoted, content)
                if new_content != content:
                    count = len(pattern.findall(content))
                    content = new_content
                    fixes_applied.append(f"  {old_route} → {new_route} ({count}处)")
    
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
            print(f"✅ {filename}: {len(fixes)} 项修复")
            for fix in fixes:
                print(fix)
    
    print(f"\n📊 总计: 修复了 {total_fixed} 个文件，共 {total_fixes} 处路由替换")


if __name__ == '__main__':
    main()
