"""
JGSY.AGI 全自动化测试套件 — 统一配置
=====================================
从 docker/services.json 读取服务配置，零硬编码
当 services.json 不存在时（如独立测试仓库 CI），自动使用 Mock 默认配置
"""
import os
import json
from pathlib import Path

# ── 项目根目录 ──
_REPO_ROOT = Path(__file__).resolve().parent.parent.parent.parent
_SERVICES_JSON = _REPO_ROOT / "docker" / "services.json"
# 也尝试 Configuration2.0/docker/services.json
_SERVICES_JSON_ALT = _REPO_ROOT / "Configuration2.0" / "docker" / "services.json"

# ── Mock 默认服务配置（零外部依赖）──
_MOCK_SERVICES = {
    "Gateway": {"port": 8000, "group": "platform"},
    "Identity": {"port": 5101, "group": "platform"},
    "Tenant": {"port": 5102, "group": "platform"},
    "Permission": {"port": 5103, "group": "platform"},
    "Account": {"port": 5104, "group": "platform"},
    "Device": {"port": 5201, "group": "business"},
    "Station": {"port": 5202, "group": "business"},
    "Charging": {"port": 5203, "group": "business"},
    "Settlement": {"port": 5204, "group": "business"},
    "Analytics": {"port": 5205, "group": "business"},
    "WorkOrder": {"port": 5206, "group": "business"},
    "Ingestion": {"port": 5207, "group": "business"},
    "DigitalTwin": {"port": 5208, "group": "business"},
    "Storage": {"port": 5301, "group": "infra"},
    "Observability": {"port": 5302, "group": "infra"},
    "ContentPlatform": {"port": 5303, "group": "business"},
    "IotCloudAI": {"port": 5401, "group": "ai"},
    "Blockchain": {"port": 5402, "group": "web3"},
    "Mcp": {"port": 5403, "group": "ai"},
    "Simulator": {"port": 5501, "group": "tool"},
    "RuleEngine": {"port": 5502, "group": "business"},
    "EnergyCore.VPP": {"port": 5601, "group": "energy"},
    "EnergyCore.MicroGrid": {"port": 5602, "group": "energy"},
    "EnergyCore.PVESSC": {"port": 5603, "group": "energy"},
    "EnergyCore.Orchestrator": {"port": 5604, "group": "energy"},
    "EnergyServices.Trading": {"port": 5701, "group": "energy"},
    "EnergyServices.Operations": {"port": 5702, "group": "energy"},
}


def _load_services() -> dict:
    """从 docker/services.json 加载服务配置，找不到文件时返回 Mock 默认配置"""
    for path in [_SERVICES_JSON, _SERVICES_JSON_ALT]:
        if path.exists():
            with open(path, encoding="utf-8") as f:
                return json.load(f)["services"]
    # CI / 独立测试仓库：使用 Mock 默认配置
    return _MOCK_SERVICES


SERVICES = _load_services()

# ── 环境变量覆盖 ──
GATEWAY_URL = os.getenv("JGSY_GATEWAY_URL", f"http://localhost:{SERVICES['Gateway']['port']}")
DB_HOST = os.getenv("JGSY_DB_HOST", "localhost")
DB_PORT = int(os.getenv("JGSY_DB_PORT", "5432"))
DB_USER = os.getenv("JGSY_DB_USER", "postgres")
DB_PASSWORD = os.getenv("JGSY_DB_PASSWORD", "P@ssw0rd")
LOGIN_TIMEOUT = int(os.getenv("JGSY_LOGIN_TIMEOUT", "10"))

# ── 测试账号 ──
SUPER_ADMIN = {
    "username": os.getenv("JGSY_ADMIN_USERNAME", "admin"),
    "password": os.getenv("JGSY_ADMIN_PASSWORD", "P@ssw0rd"),
}

TENANT_ADMIN = {
    "username": os.getenv("JGSY_TENANT_ADMIN_USERNAME", "tenant_admin"),
    "password": os.getenv("JGSY_TENANT_ADMIN_PASSWORD", "TenantAdmin@123"),
}

OPERATOR = {
    "username": os.getenv("JGSY_OPERATOR_USERNAME", "operator"),
    "password": os.getenv("JGSY_OPERATOR_PASSWORD", "Operator@123"),
}

# ── 服务 URL 映射（自动从 services.json 生成）──
SERVICE_URLS = {}
for name, cfg in SERVICES.items():
    port = cfg["port"]
    env_key = f"JGSY_{name.upper()}_URL"
    SERVICE_URLS[name.lower()] = os.getenv(env_key, f"http://localhost:{port}")

# ── 数据库名映射（约定：jgsy_{服务名小写}）──
DB_NAMES = {}
for name in SERVICES:
    DB_NAMES[name.lower()] = f"jgsy_{name.lower()}"

# 特殊映射
DB_NAMES["contentplatform"] = "jgsy_content"
DB_NAMES["orchestrator"] = "jgsy_orchestrator"

# ── 服务分组 ──
SERVICE_GROUPS = {}
for name, cfg in SERVICES.items():
    group = cfg.get("group", "unknown")
    SERVICE_GROUPS.setdefault(group, []).append(name.lower())

# ── 全部服务 API 路由注册表 ──
# 格式: { "服务名": [ {"route": "/api/xxx", "methods": ["GET","POST",...], "name": "描述"} ] }
SERVICE_API_REGISTRY = {
    "tenant": [
        {"route": "/api/tenants", "methods": ["GET", "POST", "PUT", "DELETE"], "name": "租户管理"},
        {"route": "/api/tenant/categories", "methods": ["GET", "POST", "PUT", "DELETE"], "name": "租户分类"},
        {"route": "/api/tenant-registration", "methods": ["GET", "POST"], "name": "租户注册"},
        {"route": "/api/subscription-plans", "methods": ["GET", "POST", "PUT", "DELETE"], "name": "订阅计划"},
        {"route": "/api/system/configs", "methods": ["GET", "POST", "PUT", "DELETE"], "name": "系统配置"},
        {"route": "/api/system/versions", "methods": ["GET", "POST", "PUT", "DELETE"], "name": "版本管理"},
        {"route": "/api/notifications", "methods": ["GET", "POST", "PUT", "DELETE"], "name": "通知管理"},
        {"route": "/api/api-keys", "methods": ["GET", "POST", "PUT", "DELETE"], "name": "API密钥"},
        {"route": "/api/scheduled-jobs", "methods": ["GET", "POST", "PUT", "DELETE"], "name": "定时任务"},
        {"route": "/api/oauth-apps", "methods": ["GET", "POST", "PUT", "DELETE"], "name": "OAuth应用"},
        {"route": "/api/help-center", "methods": ["GET", "POST", "PUT", "DELETE"], "name": "帮助中心"},
        {"route": "/api/integrations", "methods": ["GET", "POST", "PUT", "DELETE"], "name": "集成管理"},
        {"route": "/api/app-store", "methods": ["GET", "POST", "PUT", "DELETE"], "name": "应用商店"},
        {"route": "/api/data-sources", "methods": ["GET", "POST", "PUT", "DELETE"], "name": "数据源"},
    ],
    "identity": [
        {"route": "/api/auth/login", "methods": ["POST"], "name": "登录"},
        {"route": "/api/auth/refresh", "methods": ["POST"], "name": "刷新Token"},
        {"route": "/api/auth/logout", "methods": ["POST"], "name": "登出"},
        {"route": "/api/mfa", "methods": ["GET", "POST", "PUT", "DELETE"], "name": "MFA管理"},
        {"route": "/api/monitor/login-logs", "methods": ["GET"], "name": "登录日志"},
    ],
    "permission": [
        {"route": "/api/permissions", "methods": ["GET", "POST", "PUT", "DELETE"], "name": "权限管理"},
        {"route": "/api/roles", "methods": ["GET", "POST", "PUT", "DELETE"], "name": "角色管理"},
        {"route": "/api/menus", "methods": ["GET", "POST", "PUT", "DELETE"], "name": "菜单管理"},
        {"route": "/api/role-templates", "methods": ["GET", "POST", "PUT", "DELETE"], "name": "角色模板"},
        {"route": "/api/user-roles", "methods": ["GET", "POST", "PUT", "DELETE"], "name": "用户角色"},
        {"route": "/api/permission/data", "methods": ["GET", "POST"], "name": "数据权限"},
        {"route": "/api/system/dict", "methods": ["GET", "POST", "PUT", "DELETE"], "name": "字典管理"},
        {"route": "/api/system-modules", "methods": ["GET", "POST", "PUT", "DELETE"], "name": "系统模块"},
        {"route": "/api/permissions/statistics", "methods": ["GET"], "name": "权限统计"},
        {"route": "/api/permission/audit", "methods": ["GET"], "name": "权限审计"},
    ],
    "charging": [
        {"route": "/api/charging/orders", "methods": ["GET", "POST", "PUT", "DELETE"], "name": "充电订单"},
        {"route": "/api/charging/pricing", "methods": ["GET", "POST", "PUT", "DELETE"], "name": "充电定价"},
        {"route": "/api/charging/reservation", "methods": ["GET", "POST", "PUT", "DELETE"], "name": "预约管理"},
        {"route": "/api/charging/admin/stats/today", "methods": ["GET"], "name": "退款管理"},
        {"route": "/api/free-charging-quota", "methods": ["GET", "POST", "PUT", "DELETE"], "name": "免费额度"},
    ],
    "device": [
        {"route": "/api/device", "methods": ["GET", "POST", "PUT", "DELETE"], "name": "设备管理"},
        {"route": "/api/device/alerts", "methods": ["GET", "POST", "PUT", "DELETE"], "name": "设备告警"},
        {"route": "/api/device-assets", "methods": ["GET", "POST", "PUT", "DELETE"], "name": "设备资产"},
        {"route": "/api/device/profiles", "methods": ["GET", "POST", "PUT", "DELETE"], "name": "设备模型"},
        {"route": "/api/device/firmware", "methods": ["GET", "POST", "PUT"], "name": "固件管理"},
        {"route": "/api/device/edge-gateways", "methods": ["GET", "POST", "PUT", "DELETE"], "name": "边缘网关"},
        {"route": "/api/device/ota", "methods": ["GET", "POST", "PUT"], "name": "OTA升级"},
    ],
    "station": [
        {"route": "/api/stations", "methods": ["GET", "POST", "PUT", "DELETE"], "name": "站点管理"},
        {"route": "/api/prices", "methods": ["GET", "POST", "PUT", "DELETE"], "name": "价格管理"},
    ],
    "settlement": [
        {"route": "/api/settlements", "methods": ["GET", "POST", "PUT", "DELETE"], "name": "结算记录"},
        {"route": "/api/merchant-settlement", "methods": ["GET", "POST", "PUT", "DELETE"], "name": "商户结算"},
        {"route": "/api/profit-sharing", "methods": ["GET", "POST", "PUT", "DELETE"], "name": "分润管理"},
        {"route": "/api/settlement/withdraw", "methods": ["GET", "POST", "PUT", "DELETE"], "name": "提现管理"},
        {"route": "/api/settlement-stats", "methods": ["GET"], "name": "结算统计"},
    ],
    "workorder": [
        {"route": "/api/workorder", "methods": ["GET", "POST", "PUT", "DELETE"], "name": "工单管理"},
        {"route": "/api/work-orders", "methods": ["GET", "POST", "PUT", "DELETE"], "name": "工单生命周期"},
        {"route": "/api/workorder/approval", "methods": ["GET", "POST", "PUT", "DELETE"], "name": "审批管理"},
        {"route": "/api/workorder/dispatch", "methods": ["GET", "POST", "PUT", "DELETE"], "name": "派单管理"},
        {"route": "/api/workorder/staff", "methods": ["GET", "POST", "PUT", "DELETE"], "name": "人员管理"},
        {"route": "/api/spare-part", "methods": ["GET", "POST", "PUT", "DELETE"], "name": "备件管理"},
        {"route": "/api/shift", "methods": ["GET", "POST", "PUT", "DELETE"], "name": "排班管理"},
        {"route": "/api/satisfaction", "methods": ["GET", "POST", "PUT", "DELETE"], "name": "满意度调查"},
        {"route": "/api/workorder/stats", "methods": ["GET"], "name": "工单统计"},
    ],
    "account": [
        {"route": "/api/users", "methods": ["GET", "POST", "PUT", "DELETE"], "name": "用户账户"},
        {"route": "/api/coupon", "methods": ["GET", "POST", "PUT", "DELETE"], "name": "优惠券"},
        {"route": "/api/invoice", "methods": ["GET", "POST", "PUT", "DELETE"], "name": "发票管理"},
        {"route": "/api/membership", "methods": ["GET", "POST", "PUT", "DELETE"], "name": "会员管理"},
        {"route": "/api/points", "methods": ["GET", "POST", "PUT"], "name": "积分管理"},
        {"route": "/api/recharge", "methods": ["GET", "POST"], "name": "充值管理"},
        {"route": "/api/vehicles", "methods": ["GET", "POST", "PUT", "DELETE"], "name": "车辆管理"},
    ],
    "analytics": [
        {"route": "/api/analytics/dashboard", "methods": ["GET", "POST"], "name": "分析仪表盘"},
        {"route": "/api/analytics/charging", "methods": ["GET"], "name": "充电分析"},
        {"route": "/api/analytics/revenue", "methods": ["GET"], "name": "营收分析"},
        {"route": "/api/analytics/funnel", "methods": ["GET", "POST", "PUT", "DELETE"], "name": "漏斗分析"},
        {"route": "/api/analytics/event-tracking", "methods": ["GET", "POST", "PUT", "DELETE"], "name": "事件追踪"},
        {"route": "/api/analytics/user-profile", "methods": ["GET", "POST", "PUT", "DELETE"], "name": "用户画像"},
        {"route": "/api/analytics/anomaly", "methods": ["GET", "POST"], "name": "异常检测"},
        {"route": "/api/report-center", "methods": ["GET", "POST", "PUT", "DELETE"], "name": "报表中心"},
    ],
    "ruleengine": [
        {"route": "/api/ruleengine/alarms/definitions", "methods": ["GET"], "name": "规则链"},
        {"route": "/api/ruleengine/alarms", "methods": ["GET", "POST", "PUT", "DELETE"], "name": "告警规则"},
    ],
    "blockchain": [
        {"route": "/api/wallet/system-info", "methods": ["GET"], "name": "钱包管理"},
        {"route": "/api/blockchain/gas-price", "methods": ["GET"], "name": "交易记录"},
        {"route": "/api/contracts", "methods": ["GET", "POST", "PUT", "DELETE"], "name": "合约管理"},
        {"route": "/api/certificates", "methods": ["GET", "POST", "PUT", "DELETE"], "name": "证书管理"},
    ],
    "iotcloudai": [
        {"route": "/api/iotcloudai/models", "methods": ["GET", "POST", "PUT", "DELETE"], "name": "AI模型"},
        {"route": "/api/iotcloudai/training", "methods": ["GET", "POST", "PUT", "DELETE"], "name": "模型训练"},
        {"route": "/api/iotcloudai/config", "methods": ["GET", "POST", "PUT", "DELETE"], "name": "配置管理"},
        {"route": "/api/iotcloudai/dashboard", "methods": ["GET"], "name": "AI仪表盘"},
    ],
    "digitaltwin": [
        {"route": "/api/digital-twin", "methods": ["GET", "POST", "PUT", "DELETE"], "name": "数字孪生"},
        {"route": "/api/digital-twin/overview", "methods": ["GET"], "name": "场景模型"},
        {"route": "/api/visualization", "methods": ["GET", "POST", "PUT", "DELETE"], "name": "可视化"},
        {"route": "/api/digital-twin/stations", "methods": ["GET"], "name": "设备模型目录"},
    ],
    "storage": [
        {"route": "/api/storage", "methods": ["GET", "POST", "PUT", "DELETE"], "name": "存储管理"},
        {"route": "/api/storage/files", "methods": ["GET", "POST", "PUT", "DELETE"], "name": "文件管理"},
    ],
    "ingestion": [
        {"route": "/api/collection-point", "methods": ["GET", "POST", "PUT", "DELETE"], "name": "采集点"},
        {"route": "/api/data-source", "methods": ["GET", "POST", "PUT", "DELETE"], "name": "数据源"},
        {"route": "/api/ingestion-task", "methods": ["GET", "POST", "PUT", "DELETE"], "name": "采集任务"},
        {"route": "/api/ingestion/protocols", "methods": ["GET", "POST", "PUT", "DELETE"], "name": "协议管理"},
    ],
    "simulator": [
        {"route": "/api/simulator/charging", "methods": ["GET", "POST", "PUT", "DELETE"], "name": "充电模拟"},
    ],
    "observability": [
        {"route": "/api/audit", "methods": ["GET"], "name": "审计日志"},
    ],
    "orchestrator": [
        {"route": "/api/sehs/resource/latest", "methods": ["GET"], "name": "能源调度"},
    ],
    "vpp": [
        {"route": "/api/vpp", "methods": ["GET", "POST", "PUT", "DELETE"], "name": "虚拟电厂"},
    ],
    "microgrid": [
        {"route": "/api/microgrid", "methods": ["GET", "POST", "PUT", "DELETE"], "name": "微电网"},
    ],
    "pvessc": [
        {"route": "/api/pvessc/site", "methods": ["GET", "POST", "PUT", "DELETE"], "name": "光储充站点"},
        {"route": "/api/pvessc/topology", "methods": ["GET", "POST", "PUT", "DELETE"], "name": "拓扑管理"},
    ],
    "electrade": [
        {"route": "/api/electrade", "methods": ["GET", "POST", "PUT", "DELETE"], "name": "电力交易"},
    ],
    "carbontrade": [
        {"route": "/api/carbontrade/dashboard", "methods": ["GET"], "name": "碳交易"},
    ],
    "demandresp": [
        {"route": "/api/demandresp/dashboard", "methods": ["GET"], "name": "需求响应"},
    ],
    "deviceops": [
        {"route": "/api/deviceops/plans", "methods": ["GET", "POST", "PUT", "DELETE"], "name": "设备运维计划"},
        {"route": "/api/deviceops/inspections", "methods": ["GET", "POST", "PUT", "DELETE"], "name": "巡检任务"},
    ],
    "energyeff": [
        {"route": "/api/energyeff/dashboard", "methods": ["GET"], "name": "能效管理"},
    ],
    "multienergy": [
        {"route": "/api/multienergy/device", "methods": ["GET"], "name": "多能互补"},
    ],
    "safecontrol": [
        {"route": "/api/safecontrol/event", "methods": ["GET"], "name": "安全管控"},
    ],
}

# ── 标准 CRUD 测试模块定义 ──
# 用于全自动 CRUD lifecycle 测试
CRUD_MODULES = {
    "角色管理": {
        "service": "permission",
        "base": "/api/roles",
        "create_body": lambda uid: {
            "roleName": f"AutoTestRole_{uid}",
            "roleCode": f"AUTO_ROLE_{uid.upper()}",
            "remark": "自动化测试角色",
            "sortOrder": 999,
            "level": 100,
        },
        "update_body": lambda uid: {"roleName": f"AutoTestRole_{uid}_Updated", "remark": "已更新"},
        "name_field": "roleName",
        "id_field": "id",
    },
    "菜单管理": {
        "service": "permission",
        "base": "/api/menus",
        "create_body": lambda uid: {
            "name": f"AutoMenu_{uid}",
            "code": f"AUTO_MENU_{uid.upper()}",
            "path": f"/auto-test/{uid}",
            "icon": "setting",
            "sort": 999,
            "menuType": 2,
            "visible": True,
        },
        "update_body": lambda uid: {
            "name": f"AutoMenu_{uid}_Updated",
            "code": f"AUTO_MENU_{uid.upper()}",
            "menuType": 2,
            "sort": 999,
            "visible": True,
        },
        "name_field": "name",
        "id_field": "id",
    },
    "字典管理": {
        "service": "permission",
        "base": "/api/system/dict/types",
        "create_body": lambda uid: {
            "code": f"AUTO_DICT_{uid.upper()}",
            "name": f"AutoDict_{uid}",
            "description": "自动化测试字典",
            "sortOrder": 999,
            "status": 1,
        },
        "update_body": lambda uid: {"name": f"AutoDict_{uid}_Updated"},
        "name_field": "name",
        "id_field": "id",
    },
    "设备模型": {
        "service": "device",
        "base": "/api/device/profiles",
        "create_body": lambda uid: {
            "name": f"AutoProfile_{uid}",
            "code": f"PROF_{uid}",
            "deviceType": "charger",
            "description": "自动化测试模型",
        },
        "update_body": lambda uid: {"name": f"AutoProfile_{uid}_Updated"},
        "name_field": "name",
        "id_field": "id",
    },
    "车辆管理": {
        "service": "account",
        "base": "/api/vehicles",
        "create_body": lambda uid: {
            "plateNumber": f"京A{uid[:5].upper()}",
            "brand": "AutoTest",
            "model": "Model_X",
            "vin": f"WAUZZZ8V9K{uid[:7].upper()}",
        },
        "update_body": lambda uid: {"brand": "AutoTest_Updated"},
        "name_field": "plateNumber",
        "id_field": "id",
    },
    "规则链": {
        "service": "ruleengine",
        "base": "/api/ruleengine/chains",
        "create_body": lambda uid: {
            "name": f"AutoChain_{uid}",
            "code": f"AUTO_CHAIN_{uid.upper()}",
            "description": "自动化测试规则链",
            "type": "device",
        },
        "update_body": lambda uid: {"name": f"AutoChain_{uid}_Updated"},
        "name_field": "name",
        "id_field": "id",
    },
    "漏斗分析": {
        "service": "analytics",
        "base": "/api/analytics/funnel",
        "create_body": lambda uid: {
            "name": f"AutoFunnel_{uid}",
            "description": "自动化测试漏斗",
            "steps": [
                {"name": "Step1", "eventName": "page_view"},
                {"name": "Step2", "eventName": "sign_up"},
            ],
        },
        "update_body": lambda uid: {"name": f"AutoFunnel_{uid}_Updated"},
        "name_field": "name",
        "id_field": "id",
    },
    "场景模型": {
        "service": "digitaltwin",
        "base": "/api/scene-model",
        "create_body": lambda uid: {
            "name": f"AutoScene_{uid}",
            "description": "自动化测试场景",
            "type": "station",
        },
        "update_body": lambda uid: {"name": f"AutoScene_{uid}_Updated"},
        "name_field": "name",
        "id_field": "id",
    },
    "采集点": {
        "service": "ingestion",
        "base": "/api/collection-point",
        "create_body": lambda uid: {
            "name": f"AutoCP_{uid}",
            "code": f"CP_{uid}",
            "protocol": "MQTT",
            "status": 1,
        },
        "update_body": lambda uid: {"name": f"AutoCP_{uid}_Updated"},
        "name_field": "name",
        "id_field": "id",
    },
}
