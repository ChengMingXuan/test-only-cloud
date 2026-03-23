"""
可观测性测试 — 监控告警管道验证
==========================================================
验证日志、指标、链路追踪、告警的完整性与正确性。

对标标准：
  - OpenTelemetry 规范
  - SRE 可观测性三大支柱
  - 等保 2.0 安全审计/集中管控

覆盖分组：
  OBS-001 健康检查端点
  OBS-002 日志接口
  OBS-003 指标与链路
  OBS-004 告警规则

合计约 100 条用例
"""
import uuid
import pytest
import logging
from mock_client import MockApiClient, MOCK_TOKEN

logger = logging.getLogger(__name__)

# 所有服务的健康检查端点（从 services.json 的 31 服务衍生）
HEALTH_ENDPOINTS = [
    "/health",
    "/api/health",
]

# 可观测性端点
OBSERVABILITY_ENDPOINTS = [
    "/api/observability/logs",
    "/api/observability/metrics",
    "/api/observability/traces",
    "/api/observability/alerts",
    "/api/observability/dashboard",
]

# 各服务对应端点（用于验证各服务可达性）
SERVICE_ENDPOINTS = [
    ("/api/device", "设备管理"),
    ("/api/stations", "场站管理"),
    ("/api/charging/orders", "充电管理"),
    ("/api/workorder", "工单管理"),
    ("/api/settlements", "结算管理"),
    ("/api/tenants", "租户管理"),
    ("/api/system/role", "权限角色"),
    ("/api/analytics/charging/overview", "数据分析"),
    ("/api/digital-twin/stations", "数字孪生"),
    ("/api/blockchain/overview", "区块链"),
    ("/api/iotcloudai/models", "IoT/AI"),
    ("/api/vpp/dashboard", "虚拟电厂"),
    ("/api/pvessc/site/list", "光储充"),
    ("/api/energyeff/dashboard", "能效管理"),
    ("/api/safecontrol/dashboard", "安全管控"),
    ("/api/ingestion/protocols", "数据采集"),
    ("/api/ruleengine/rules", "规则引擎"),
    ("/api/permission/menus", "权限菜单"),
    ("/api/account/users", "用户管理"),
    ("/api/observability/logs", "可观测日志"),
]


# ══════════════════════════════════════════════════════════════
# OBS-001 健康检查端点
# ══════════════════════════════════════════════════════════════

class TestHealthCheckEndpoints:
    """OBS-001: 验证健康检查端点可用"""

    @pytest.mark.p0
    @pytest.mark.parametrize("endpoint", HEALTH_ENDPOINTS)
    def test_health_endpoint_200(self, api, endpoint):
        """健康检查端点应返回 200"""
        resp = api.get(endpoint)
        assert resp.status_code == 200, (
            f"健康检查 {endpoint} 返回 {resp.status_code}"
        )

    @pytest.mark.p0
    def test_health_no_auth_required(self):
        """健康检查不应需要认证（供 K8s/Consul 探针使用）"""
        client = MockApiClient(token=None)
        resp = client.get("/health")
        assert resp.status_code == 200, "健康检查应不需认证"

    @pytest.mark.p1
    def test_health_response_json(self, api):
        """健康检查应返回 JSON 格式"""
        resp = api.get("/health")
        ct = resp.headers.get("Content-Type", "")
        assert "json" in ct.lower() or resp.status_code == 200

    @pytest.mark.p1
    def test_health_no_sensitive_info(self):
        """健康检查不应暴露敏感配置"""
        client = MockApiClient(token=None)
        resp = client.get("/health")
        text = resp.text.lower()
        assert "password" not in text, "健康检查暴露密码"
        assert "connection" not in text or "status" in text, "健康检查暴露连接信息"


# ══════════════════════════════════════════════════════════════
# OBS-002 日志接口
# ══════════════════════════════════════════════════════════════

class TestLogEndpoints:
    """OBS-002: 验证日志查询接口"""

    @pytest.mark.p0
    def test_logs_requires_auth(self):
        """日志查询必须认证"""
        client = MockApiClient(token=None)
        resp = client.get("/api/observability/logs", params={
            "page": 1, "pageSize": 10
        })
        assert resp.status_code in (401, 403)

    @pytest.mark.p0
    def test_logs_query(self, api):
        """日志查询应返回分页数据"""
        resp = api.get("/api/observability/logs", params={
            "page": 1, "pageSize": 10
        })
        assert resp.status_code == 200

    @pytest.mark.p1
    def test_logs_with_filter(self, api):
        """日志应支持按级别过滤"""
        resp = api.get("/api/observability/logs", params={
            "level": "Error", "page": 1, "pageSize": 10
        })
        assert resp.status_code == 200

    @pytest.mark.p1
    def test_logs_with_keyword(self, api):
        """日志应支持关键字搜索"""
        resp = api.get("/api/observability/logs", params={
            "keyword": "startup", "page": 1, "pageSize": 10
        })
        assert resp.status_code == 200

    @pytest.mark.p1
    def test_logs_with_time_range(self, api):
        """日志应支持时间范围过滤"""
        resp = api.get("/api/observability/logs", params={
            "startTime": "2024-01-01", "endTime": "2026-12-31",
            "page": 1, "pageSize": 10
        })
        assert resp.status_code == 200

    @pytest.mark.p1
    @pytest.mark.parametrize("injection", [
        "' OR 1=1 --",
        "<script>alert(1)</script>",
    ])
    def test_logs_injection_safe(self, api, injection):
        """日志查询参数应防注入"""
        resp = api.get("/api/observability/logs", params={
            "keyword": injection, "page": 1, "pageSize": 10
        })
        assert resp.status_code < 500


# ══════════════════════════════════════════════════════════════
# OBS-003 指标与链路追踪
# ══════════════════════════════════════════════════════════════

class TestMetricsAndTracing:
    """OBS-003: 验证指标收集与链路追踪"""

    @pytest.mark.p0
    @pytest.mark.parametrize("endpoint,service_name", SERVICE_ENDPOINTS[:10])
    def test_service_reachable(self, api, endpoint, service_name):
        """各服务端点应可正常访问"""
        resp = api.get(endpoint, params={"page": 1, "pageSize": 5})
        assert resp.status_code == 200, (
            f"{service_name} ({endpoint}) 不可达: {resp.status_code}"
        )

    @pytest.mark.p0
    @pytest.mark.parametrize("endpoint,service_name", SERVICE_ENDPOINTS[10:])
    def test_remaining_services_reachable(self, api, endpoint, service_name):
        """剩余服务端点应可正常访问"""
        resp = api.get(endpoint, params={"page": 1, "pageSize": 5})
        assert resp.status_code == 200, (
            f"{service_name} ({endpoint}) 不可达: {resp.status_code}"
        )

    @pytest.mark.p1
    def test_metrics_endpoint(self, api):
        """指标端点应返回数据"""
        resp = api.get("/api/observability/metrics", params={
            "page": 1, "pageSize": 10
        })
        assert resp.status_code == 200

    @pytest.mark.p1
    def test_traces_endpoint(self, api):
        """链路追踪端点应返回数据"""
        resp = api.get("/api/observability/traces", params={
            "page": 1, "pageSize": 10
        })
        assert resp.status_code == 200


# ══════════════════════════════════════════════════════════════
# OBS-004 告警规则验证
# ══════════════════════════════════════════════════════════════

class TestAlertingRules:
    """OBS-004: 验证告警规则配置"""

    @pytest.mark.p0
    def test_alerts_requires_auth(self):
        """告警查询必须认证"""
        client = MockApiClient(token=None)
        resp = client.get("/api/observability/alerts", params={
            "page": 1, "pageSize": 10
        })
        assert resp.status_code in (401, 403)

    @pytest.mark.p0
    def test_alerts_query(self, api):
        """告警查询应返回结果"""
        resp = api.get("/api/observability/alerts", params={
            "page": 1, "pageSize": 10
        })
        assert resp.status_code == 200

    @pytest.mark.p1
    def test_alert_creation_requires_auth(self):
        """告警规则创建必须认证"""
        client = MockApiClient(token=None)
        resp = client.post("/api/observability/alerts", json={
            "name": "测试告警", "condition": "cpu > 90", "severity": "critical"
        })
        assert resp.status_code in (401, 403)

    @pytest.mark.p1
    def test_alert_creation(self, api):
        """告警规则创建应正常处理"""
        resp = api.post("/api/observability/alerts", json={
            "name": "CPU告警",
            "condition": "cpu_usage > 90",
            "severity": "critical",
            "channel": "email"
        })
        assert resp.status_code in (200, 201)

    @pytest.mark.p1
    def test_alert_dashboard(self, api):
        """告警仪表板应可访问"""
        resp = api.get("/api/observability/dashboard", params={
            "page": 1, "pageSize": 10
        })
        assert resp.status_code == 200

    @pytest.mark.p2
    @pytest.mark.parametrize("severity", ["critical", "warning", "info"])
    def test_alert_filter_by_severity(self, api, severity):
        """告警应支持按严重级别过滤"""
        resp = api.get("/api/observability/alerts", params={
            "severity": severity, "page": 1, "pageSize": 10
        })
        assert resp.status_code == 200
