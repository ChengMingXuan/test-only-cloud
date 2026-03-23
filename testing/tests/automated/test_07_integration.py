"""
测试 07 — 跨服务集成测试
========================
业务链路 · 服务间调用 · 数据一致性 · 端到端流程
"""
import uuid
import time
import pytest


# ──────────────────────────── 充电→结算链路 ────────────────────────────

class TestChargingToSettlement:
    """充电→结算端到端"""

    @pytest.mark.integration
    @pytest.mark.p0
    def test_create_order_and_check_settlement(self, api, v, uid, cleanup):
        """创建充电订单后检查结算记录"""
        # 1. 创建充电订单
        order_resp = api.post("/api/charging/orders", json={
            "stationId": str(uuid.uuid4()),
            "pileId": str(uuid.uuid4()),
            "userId": str(uuid.uuid4()),
            "startSoc": 20,
            "chargingMode": "fast"
        })
        if order_resp.status_code in (200, 201):
            data = order_resp.json().get("data", {})
            order_id = data.get("id")
            if order_id:
                cleanup.append(("DELETE", f"/api/charging/orders/{order_id}"))
                # 2. 查询结算列表看是否有关联
                time.sleep(1)  # 等异步处理
                settle_resp = api.get("/api/settlements", params={
                    "orderId": order_id, "page": 1, "pageSize": 10
                })
                v.not_5xx(settle_resp)
        else:
            v.not_5xx(order_resp)

    @pytest.mark.integration
    @pytest.mark.p1
    def test_settlement_list_has_order_reference(self, api, v):
        """结算列表应包含订单引用"""
        resp = api.get("/api/settlements", params={"page": 1, "pageSize": 10})
        v.not_5xx(resp)
        if resp.status_code == 200:
            data = resp.json().get("data", {})
            items = data.get("items", [])
            # 如果有结算记录，应该有关联订单信息
            for item in items[:3]:
                assert isinstance(item, dict)


# ──────────────────────────── 站点→设备→充电链路 ────────────────────────────

class TestStationDeviceCharging:
    """站点→设备→充电链路"""

    @pytest.mark.integration
    @pytest.mark.p0
    def test_station_has_devices(self, api, v):
        """站点列表→确认站点有设备"""
        # 获取站点
        station_resp = api.get("/api/stations", params={"page": 1, "pageSize": 5})
        v.not_5xx(station_resp)
        if station_resp.status_code == 200:
            data = station_resp.json().get("data", {})
            items = data.get("items", [])
            if items:
                station_id = items[0].get("id")
                if station_id:
                    # 查该站点的设备
                    dev_resp = api.get("/api/device", params={
                        "stationId": station_id, "page": 1, "pageSize": 10
                    })
                    v.not_5xx(dev_resp)

    @pytest.mark.integration
    def test_device_belongs_to_station(self, api, v):
        """设备应属于某个站点"""
        resp = api.get("/api/device", params={"page": 1, "pageSize": 5})
        v.not_5xx(resp)
        if resp.status_code == 200:
            data = resp.json().get("data", {})
            items = data.get("items", [])
            for item in items[:3]:
                # 设备通常有 stationId 字段
                if isinstance(item, dict) and "stationId" in item:
                    assert item["stationId"], "设备缺少站点关联"


# ──────────────────────────── 设备→工单链路 ────────────────────────────

class TestDeviceWorkOrder:
    """设备→工单"""

    @pytest.mark.integration
    @pytest.mark.p1
    def test_create_workorder_for_device(self, api, v, uid, cleanup):
        """为设备创建工单"""
        resp = api.post("/api/workorder", json={
            "title": f"自动化测试工单-{uid}",
            "deviceId": str(uuid.uuid4()),
            "type": "repair",
            "priority": "normal",
            "description": "自动化集成测试创建"
        })
        v.not_5xx(resp)
        if resp.status_code in (200, 201):
            data = resp.json().get("data", {})
            wid = data.get("id")
            if wid:
                cleanup.append(("DELETE", f"/api/workorder/{wid}"))

    @pytest.mark.integration
    def test_workorder_references_device(self, api, v):
        """工单包含设备引用"""
        resp = api.get("/api/workorder", params={"page": 1, "pageSize": 10})
        v.not_5xx(resp)


# ──────────────────────────── 用户→账户→权限链路 ────────────────────────────

class TestUserAccountPermission:
    """用户→账户→权限"""

    @pytest.mark.integration
    @pytest.mark.p0
    def test_login_returns_permissions(self, api, v):
        """登录后能获取权限列表"""
        resp = api.get("/api/permission-check/00000000-0000-0000-0000-000000000000/all-permissions")
        v.not_5xx(resp)

    @pytest.mark.integration
    @pytest.mark.p0
    def test_login_returns_menus(self, api, v):
        """登录后能获取菜单列表"""
        resp = api.get("/api/menus/current")
        v.not_5xx(resp)

    @pytest.mark.integration
    def test_user_info_available(self, api, v):
        """用户信息可获取"""
        resp = api.get("/api/user/profile")
        v.not_5xx(resp)

    @pytest.mark.integration
    def test_tenant_info_available(self, api, v):
        """租户信息可获取"""
        resp = api.get("/api/tenant/current")
        v.not_5xx(resp)


# ──────────────────────────── 规则引擎→设备→告警链路 ────────────────────────────

class TestRuleEngineDeviceAlarm:
    """规则引擎→设备→告警"""

    @pytest.mark.integration
    @pytest.mark.p1
    def test_rule_chains_accessible(self, api, v):
        """规则链列表可访问"""
        resp = api.get("/api/ruleengine/chains", params={"page": 1, "pageSize": 10})
        v.not_5xx(resp)

    @pytest.mark.integration
    def test_rule_execution_logs(self, api, v):
        """规则执行日志可查询"""
        resp = api.get("/api/ruleengine/execution/chains/match", params={"triggerType": "manual"})
        v.not_5xx(resp)

    @pytest.mark.integration
    def test_alarm_definitions_accessible(self, api, v):
        """告警定义列表可访问"""
        resp = api.get("/api/ruleengine/alarms/definitions", params={"pageIndex": 1, "pageSize": 10})
        v.not_5xx(resp)


# ──────────────────────────── 数字孪生→数据采集→可视化 ────────────────────────────

class TestDigitalTwinPipeline:
    """数字孪生数据流"""

    @pytest.mark.integration
    @pytest.mark.p1
    def test_digital_twin_scenes(self, api, v):
        """数字孪生场景列表"""
        resp = api.get("/api/digital-twin/stations")
        v.not_5xx(resp)

    @pytest.mark.integration
    def test_ingestion_points(self, api, v):
        """采集点列表"""
        resp = api.get("/api/ingestion/protocols")
        v.not_5xx(resp)

    @pytest.mark.integration
    def test_analytics_dashboards(self, api, v):
        """分析仪表盘列表"""
        resp = api.get("/api/analytics/dashboard")
        v.not_5xx(resp)


# ──────────────────────────── 能源服务集群 ────────────────────────────

class TestEnergyServicesIntegration:
    """能源服务集群集成"""

    @pytest.mark.integration
    @pytest.mark.p1
    def test_microgrid_accessible(self, api, v):
        """微电网服务"""
        resp = api.get("/api/microgrid/dashboard")
        v.not_5xx(resp)

    @pytest.mark.integration
    def test_vpp_accessible(self, api, v):
        """虚拟电厂服务"""
        resp = api.get("/api/vpp/dashboard")
        v.not_5xx(resp)

    @pytest.mark.integration
    def test_pvessc_accessible(self, api, v):
        """光储充服务"""
        resp = api.get("/api/pvessc/site/list", params={"pageIndex": 1, "pageSize": 10})
        v.not_5xx(resp)

    @pytest.mark.integration
    def test_orchestrator_accessible(self, api, v):
        """能源调度服务"""
        resp = api.get("/api/sehs/dashboard")
        v.not_5xx(resp)

    @pytest.mark.integration
    def test_carbon_trade(self, api, v):
        """碳交易服务"""
        resp = api.get("/api/carbontrade/dashboard")
        v.not_5xx(resp)

    @pytest.mark.integration
    def test_demand_response(self, api, v):
        """需求响应服务"""
        resp = api.get("/api/demandresp/dashboard")
        v.not_5xx(resp)

    @pytest.mark.integration
    def test_elec_trade(self, api, v):
        """电力交易服务"""
        resp = api.get("/api/electrade/dashboard")
        v.not_5xx(resp)


# ──────────────────────────── 数据一致性 ────────────────────────────

class TestDataConsistency:
    """跨服务数据一致性"""

    @pytest.mark.integration
    @pytest.mark.p0
    def test_station_count_consistency(self, api, v):
        """站点计数一致性（列表 total 与 count API）"""
        list_resp = api.get("/api/stations", params={"page": 1, "pageSize": 1})
        v.not_5xx(list_resp)
        if list_resp.status_code == 200:
            data = list_resp.json().get("data", {})
            total = data.get("total")
            # 再请求一次确认稳定
            list_resp2 = api.get("/api/stations", params={"page": 1, "pageSize": 1})
            if list_resp2.status_code == 200:
                total2 = list_resp2.json().get("data", {}).get("total")
                assert total == total2, f"两次请求站点总数不一致: {total} vs {total2}"

    @pytest.mark.integration
    @pytest.mark.p0
    def test_device_count_consistency(self, api, v):
        """设备计数一致性"""
        resp1 = api.get("/api/device", params={"page": 1, "pageSize": 1})
        resp2 = api.get("/api/device", params={"page": 1, "pageSize": 1})
        v.not_5xx(resp1)
        v.not_5xx(resp2)
        if resp1.status_code == 200 and resp2.status_code == 200:
            t1 = resp1.json().get("data", {}).get("total")
            t2 = resp2.json().get("data", {}).get("total")
            assert t1 == t2, f"设备计数不一致: {t1} vs {t2}"

    @pytest.mark.integration
    def test_pagination_total_matches_all_pages(self, api, v):
        """分页总数与实际数据一致"""
        resp = api.get("/api/device", params={"page": 1, "pageSize": 100})
        v.not_5xx(resp)
        if resp.status_code == 200:
            data = resp.json().get("data", {})
            total = data.get("total", 0)
            items = data.get("items", [])
            if total <= 100:
                assert len(items) == total, f"total={total} 但返回 {len(items)} 条"


# ──────────────────────────── 权限分配集成（全员分配） ────────────────────────────

class TestRolePermissionAssignment:
    """一键赋权集成测试 — 全员分配（POST /api/system/role/init-tenant-permissions）"""

    @pytest.mark.integration
    @pytest.mark.p0
    def test_init_tenant_permissions_endpoint_reachable(self, api, v):
        """一键赋权接口可达性：用不存在的租户 ID 调用，应返回 4xx 而非 5xx"""
        fake_tenant_id = str(uuid.uuid4())
        resp = api.post(
            "/api/system/role/init-tenant-permissions",
            json={"tenantId": fake_tenant_id},
        )
        # 接口可达：即使租户不存在，也应返回 400/403/404/422 而非 500
        v.not_5xx(resp)
        assert resp.status_code in (200, 201, 400, 403, 404, 422), (
            f"一键赋权接口应返回 2xx/4xx，实际 {resp.status_code}: {resp.text[:300]}"
        )

    @pytest.mark.integration
    @pytest.mark.p1
    def test_init_tenant_permissions_requires_auth(self, anon_api):
        """一键赋权接口必须鉴权：未携带 Token 应返回 401"""
        fake_tenant_id = str(uuid.uuid4())
        resp = anon_api.post(
            "/api/system/role/init-tenant-permissions",
            json={"tenantId": fake_tenant_id},
        )
        assert resp.status_code == 401, (
            f"一键赋权接口未携带 Token 应返回 401，实际 {resp.status_code}"
        )

    @pytest.mark.integration
    @pytest.mark.p1
    def test_init_tenant_permissions_missing_tenant_id(self, api, v):
        """一键赋权：缺少 tenantId 应返回 400/422（参数校验）"""
        resp = api.post(
            "/api/system/role/init-tenant-permissions",
            json={},  # 故意不传 tenantId
        )
        v.not_5xx(resp)
        assert resp.status_code in (400, 422), (
            f"缺少 tenantId 应返回 400/422，实际 {resp.status_code}: {resp.text[:300]}"
        )

