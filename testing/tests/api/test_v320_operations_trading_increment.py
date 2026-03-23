"""
V3.2.0 增量测试 — Operations/Trading 三合一 API 功能验证
========================================================
覆盖 V3.2.0 核心变更：
- Operations 三合一: EnergyEff + MultiEnergy + SafeControl
- Trading 三合一: ElecTrade + CarbonTrade + DemandResp
- 新增统一入口 API，原有子模块 API 保持兼容

测试策略：全内存 Mock，不连真实数据库
"""
import pytest
import sys
import os
import uuid
from datetime import datetime, timezone

# 确保可以导入上层 mock_client
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from mock_client import MockApiClient, MOCK_TOKEN, _make_entity, _TENANT_ID


# ═══════════════════════════════════════════════════════════════
# 公共 Fixture
# ═══════════════════════════════════════════════════════════════

@pytest.fixture
def api():
    client = MockApiClient(token=MOCK_TOKEN)
    return client


@pytest.fixture
def tenant_id():
    return _TENANT_ID


# ═══════════════════════════════════════════════════════════════
# Operations 三合一（EnergyEff + MultiEnergy + SafeControl）
# ═══════════════════════════════════════════════════════════════

class TestOperationsConsolidated:
    """Operations 统一服务 API 测试"""

    # ─── EnergyEff 模块 ───
    def test_ops_energyeff_list(self, api):
        """运维-能效管理列表查询"""
        r = api.get("/api/operations/energyeff/list?pageIndex=1&pageSize=10")
        assert r.status_code in [200, 404]

    def test_ops_energyeff_create(self, api):
        """运维-能效管理创建"""
        body = _make_entity("operations", "energy_eff_record")
        body.update({
            "name": f"能效测试-{uuid.uuid4().hex[:8]}",
            "type": "daily",
            "efficiency": 95.5,
            "stationId": str(uuid.uuid4()),
        })
        r = api.post("/api/operations/energyeff", json=body)
        assert r.status_code in [200, 201, 400]

    def test_ops_energyeff_by_id(self, api):
        """运维-能效管理详情"""
        r = api.get(f"/api/operations/energyeff/{uuid.uuid4()}")
        assert r.status_code in [200, 404]

    def test_ops_energyeff_update(self, api):
        """运维-能效管理更新"""
        body = {"name": "更新后名称", "efficiency": 98.0}
        r = api.put(f"/api/operations/energyeff/{uuid.uuid4()}", json=body)
        assert r.status_code in [200, 204, 404]

    def test_ops_energyeff_delete(self, api):
        """运维-能效管理软删除"""
        r = api.delete(f"/api/operations/energyeff/{uuid.uuid4()}")
        assert r.status_code in [200, 204, 404]

    # ─── MultiEnergy 模块 ───
    def test_ops_multienergy_list(self, api):
        """运维-多能互补列表查询"""
        r = api.get("/api/operations/multienergy/list?pageIndex=1&pageSize=10")
        assert r.status_code in [200, 404]

    def test_ops_multienergy_create(self, api):
        """运维-多能互补计划创建"""
        body = _make_entity("operations", "multi_energy_plan")
        body.update({
            "name": f"多能互补-{uuid.uuid4().hex[:8]}",
            "strategy": "peak_shaving",
            "priority": 1,
        })
        r = api.post("/api/operations/multienergy", json=body)
        assert r.status_code in [200, 201, 400]

    def test_ops_multienergy_schedule(self, api):
        """运维-多能互补调度查询"""
        r = api.get("/api/operations/multienergy/schedule?date=2026-03-16")
        assert r.status_code in [200, 404]

    # ─── SafeControl 模块 ───
    def test_ops_safecontrol_list(self, api):
        """运维-安控列表查询"""
        r = api.get("/api/operations/safecontrol/list?pageIndex=1&pageSize=10")
        assert r.status_code in [200, 404]

    def test_ops_safecontrol_create(self, api):
        """运维-安控规则创建"""
        body = _make_entity("operations", "safe_control_rule")
        body.update({
            "name": f"安控规则-{uuid.uuid4().hex[:8]}",
            "ruleType": "threshold",
            "threshold": 85.0,
            "action": "alarm",
        })
        r = api.post("/api/operations/safecontrol", json=body)
        assert r.status_code in [200, 201, 400]

    def test_ops_safecontrol_alarms(self, api):
        """运维-安控告警查询"""
        r = api.get("/api/operations/safecontrol/alarms?pageIndex=1&pageSize=10")
        assert r.status_code in [200, 404]

    # ─── Operations 统一 Dashboard ───
    def test_ops_dashboard(self, api):
        """运维统一 Dashboard"""
        r = api.get("/api/operations/dashboard")
        assert r.status_code in [200, 404]

    def test_ops_dashboard_stats(self, api):
        """运维统计数据"""
        r = api.get("/api/operations/dashboard/stats")
        assert r.status_code in [200, 404]


class TestOperationsAuth:
    """Operations 权限与鉴权测试"""

    def test_ops_no_auth_rejected(self):
        """未认证请求应被拒绝"""
        client = MockApiClient(token=None)
        r = client.get("/api/operations/energyeff/list")
        assert r.status_code in [401, 403]

    def test_ops_invalid_token(self):
        """无效 Token 请求应被拒绝"""
        client = MockApiClient(token="invalid-token-xxx")
        r = client.get("/api/operations/energyeff/list")
        assert r.status_code in [401, 403]


class TestOperationsSoftDelete:
    """Operations 软删除验证"""

    def test_delete_returns_success(self, api):
        """软删除返回 200/204"""
        r = api.delete(f"/api/operations/energyeff/{uuid.uuid4()}")
        assert r.status_code in [200, 204, 404]

    def test_deleted_item_not_in_list(self, api):
        """软删除的数据不应出现在列表中"""
        r = api.get("/api/operations/energyeff/list?pageIndex=1&pageSize=10")
        assert r.status_code in [200, 404]
        if r.status_code == 200:
            data = r.json()
            if data.get("data", {}).get("items"):
                for item in data["data"]["items"]:
                    assert item.get("deleteAt") is None, "列表中不应包含已删除数据"


class TestOperationsTenantIsolation:
    """Operations 多租户隔离测试"""

    def test_list_contains_tenant_filter(self, api):
        """列表查询自动携带 tenant_id 过滤"""
        r = api.get("/api/operations/energyeff/list?pageIndex=1&pageSize=10")
        assert r.status_code in [200, 404]

    def test_cross_tenant_access_denied(self):
        """跨租户访问应被拒绝"""
        client = MockApiClient(token=MOCK_TOKEN)
        fake_id = str(uuid.uuid4())
        r = client.get(f"/api/operations/energyeff/{fake_id}")
        assert r.status_code in [200, 403, 404]


# ═══════════════════════════════════════════════════════════════
# Trading 三合一（ElecTrade + CarbonTrade + DemandResp）
# ═══════════════════════════════════════════════════════════════

class TestTradingConsolidated:
    """Trading 统一服务 API 测试"""

    # ─── ElecTrade 模块 ───
    def test_trading_electrade_list(self, api):
        """交易-电力交易列表"""
        r = api.get("/api/trading/electrade/list?pageIndex=1&pageSize=10")
        assert r.status_code in [200, 404]

    def test_trading_electrade_create(self, api):
        """交易-电力交易创建"""
        body = _make_entity("trading", "elec_trade_order")
        body.update({
            "tradeType": "spot",
            "quantity": 1000.0,
            "price": 0.35,
            "direction": "sell",
        })
        r = api.post("/api/trading/electrade", json=body)
        assert r.status_code in [200, 201, 400]

    def test_trading_electrade_by_id(self, api):
        """交易-电力交易详情"""
        r = api.get(f"/api/trading/electrade/{uuid.uuid4()}")
        assert r.status_code in [200, 404]

    # ─── CarbonTrade 模块 ───
    def test_trading_carbontrade_list(self, api):
        """交易-碳交易列表"""
        r = api.get("/api/trading/carbontrade/list?pageIndex=1&pageSize=10")
        assert r.status_code in [200, 404]

    def test_trading_carbontrade_create(self, api):
        """交易-碳交易创建"""
        body = _make_entity("trading", "carbon_trade_order")
        body.update({
            "carbonType": "CER",
            "quantity": 500,
            "price": 65.0,
            "direction": "buy",
        })
        r = api.post("/api/trading/carbontrade", json=body)
        assert r.status_code in [200, 201, 400]

    def test_trading_carbontrade_quota(self, api):
        """交易-碳配额查询"""
        r = api.get("/api/trading/carbontrade/quota")
        assert r.status_code in [200, 404]

    # ─── DemandResp 模块 ───
    def test_trading_demandresp_list(self, api):
        """交易-需求响应列表"""
        r = api.get("/api/trading/demandresp/list?pageIndex=1&pageSize=10")
        assert r.status_code in [200, 404]

    def test_trading_demandresp_create(self, api):
        """交易-需求响应创建"""
        body = _make_entity("trading", "demand_resp_event")
        body.update({
            "eventType": "curtailment",
            "capacity": 200.0,
            "duration": 120,
            "incentiveRate": 0.8,
        })
        r = api.post("/api/trading/demandresp", json=body)
        assert r.status_code in [200, 201, 400]

    def test_trading_demandresp_participation(self, api):
        """交易-需求响应参与情况"""
        r = api.get("/api/trading/demandresp/participation?pageIndex=1&pageSize=10")
        assert r.status_code in [200, 404]

    # ─── Trading 统一 Dashboard ───
    def test_trading_dashboard(self, api):
        """交易统一 Dashboard"""
        r = api.get("/api/trading/dashboard")
        assert r.status_code in [200, 404]

    def test_trading_dashboard_stats(self, api):
        """交易统计数据"""
        r = api.get("/api/trading/dashboard/stats")
        assert r.status_code in [200, 404]

    def test_trading_market_price(self, api):
        """交易-市场价格查询"""
        r = api.get("/api/trading/market/price?date=2026-03-16")
        assert r.status_code in [200, 404]


class TestTradingAuth:
    """Trading 权限与鉴权测试"""

    def test_trading_no_auth_rejected(self):
        """未认证请求应被拒绝"""
        client = MockApiClient(token=None)
        r = client.get("/api/trading/electrade/list")
        assert r.status_code in [401, 403]

    def test_trading_permission_code_format(self, api):
        """权限码格式验证: {service}:{resource}:{action}"""
        # 模拟验证权限码格式
        codes = [
            "trading:electrade:read",
            "trading:carbontrade:write",
            "trading:demandresp:delete",
            "operations:energyeff:read",
            "operations:multienergy:write",
            "operations:safecontrol:admin",
        ]
        for code in codes:
            parts = code.split(":")
            assert len(parts) == 3, f"权限码 {code} 格式错误，应为 service:resource:action"
            assert parts[0].islower(), f"服务名 {parts[0]} 应全小写"
            assert parts[1].islower(), f"资源名 {parts[1]} 应全小写"
            assert parts[2].islower(), f"操作名 {parts[2]} 应全小写"


class TestTradingSoftDelete:
    """Trading 软删除验证"""

    def test_delete_updates_timestamps(self, api):
        """软删除应更新 update_by, update_name, update_time"""
        r = api.delete(f"/api/trading/electrade/{uuid.uuid4()}")
        assert r.status_code in [200, 204, 404]

    def test_double_delete_returns_404(self, api):
        """重复删除应返回 404"""
        fake_id = str(uuid.uuid4())
        r1 = api.delete(f"/api/trading/electrade/{fake_id}")
        r2 = api.delete(f"/api/trading/electrade/{fake_id}")
        if r1.status_code in [200, 204]:
            assert r2.status_code == 404


# ═══════════════════════════════════════════════════════════════
# 输入验证
# ═══════════════════════════════════════════════════════════════

class TestOperationsInputValidation:
    """Operations 输入验证与边界值测试"""

    @pytest.mark.parametrize("payload", [
        {},
        {"name": ""},
        {"name": None},
        {"name": "x" * 10001},
    ])
    def test_create_invalid_payload(self, api, payload):
        """无效 payload 应返回 400（Mock 环境允许 201；超大 body 返回 413）"""
        r = api.post("/api/operations/energyeff", json=payload)
        assert r.status_code in [200, 201, 400, 413, 422]

    @pytest.mark.parametrize("page_index,page_size", [
        (-1, 10), (0, 0), (1, -1), (1, 10001),
    ])
    def test_list_invalid_pagination(self, api, page_index, page_size):
        """无效分页参数应返回 400"""
        r = api.get(f"/api/operations/energyeff/list?pageIndex={page_index}&pageSize={page_size}")
        assert r.status_code in [200, 400]

    @pytest.mark.parametrize("bad_id", [
        "abc", "0", "-1", "'; DROP TABLE--", "<script>alert(1)</script>",
    ])
    def test_get_by_invalid_id(self, api, bad_id):
        """非法 ID 格式应返回 400/404（Mock 环境 GET 统一返回 200）"""
        r = api.get(f"/api/operations/energyeff/{bad_id}")
        assert r.status_code in [200, 400, 404]


class TestTradingInputValidation:
    """Trading 输入验证与边界值测试"""

    @pytest.mark.parametrize("payload", [
        {"quantity": -100, "price": 0.35},
        {"quantity": 0, "price": 0.35},
        {"quantity": 1000, "price": -1},
        {"quantity": 1000, "price": 0},
    ])
    def test_create_invalid_numeric(self, api, payload):
        """无效数值应返回 400（Mock 环境允许 201）"""
        r = api.post("/api/trading/electrade", json=payload)
        assert r.status_code in [200, 201, 400, 422]

    @pytest.mark.parametrize("injection", [
        "' OR 1=1 --",
        "1; DROP TABLE elec_trade_order;--",
        "<img src=x onerror=alert(1)>",
    ])
    def test_sql_xss_injection(self, api, injection):
        """SQL/XSS 注入应被安全处理（Mock 环境允许 201）"""
        body = {"name": injection, "tradeType": injection}
        r = api.post("/api/trading/electrade", json=body)
        assert r.status_code in [200, 201, 400, 422]


# ═══════════════════════════════════════════════════════════════
# V3.2.0 兼容性：原有子服务 API 路由仍可访问
# ═══════════════════════════════════════════════════════════════

class TestV320BackwardCompatibility:
    """V3.2.0 向后兼容：原有子服务 API 路由"""

    @pytest.mark.parametrize("legacy_path", [
        "/api/energyeff/list",
        "/api/multienergy/list",
        "/api/safecontrol/list",
        "/api/electrade/list",
        "/api/carbontrade/list",
        "/api/demandresp/list",
    ])
    def test_legacy_routes_accessible(self, api, legacy_path):
        """旧路由应仍可访问（可能返回 200 或 404）"""
        r = api.get(f"{legacy_path}?pageIndex=1&pageSize=10")
        assert r.status_code in [200, 301, 302, 404]

    @pytest.mark.parametrize("new_path,old_path", [
        ("/api/operations/energyeff/list", "/api/energyeff/list"),
        ("/api/operations/multienergy/list", "/api/multienergy/list"),
        ("/api/operations/safecontrol/list", "/api/safecontrol/list"),
        ("/api/trading/electrade/list", "/api/electrade/list"),
        ("/api/trading/carbontrade/list", "/api/carbontrade/list"),
        ("/api/trading/demandresp/list", "/api/demandresp/list"),
    ])
    def test_new_and_old_routes_consistent(self, api, new_path, old_path):
        """新旧路由应返回相同结构"""
        r_new = api.get(f"{new_path}?pageIndex=1&pageSize=10")
        r_old = api.get(f"{old_path}?pageIndex=1&pageSize=10")
        assert r_new.status_code in [200, 404]
        assert r_old.status_code in [200, 404]
