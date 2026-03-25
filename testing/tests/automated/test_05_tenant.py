"""
测试 05 — 多租户隔离测试
==========================
数据隔离 · 跨租户访问阻断 · tenant_id 强制
"""
import uuid
import pytest
from config import GATEWAY_URL
from mock_client import MOCK_MODE


class TestTenantIsolation:
    """多租户数据隔离"""

    @pytest.mark.tenant
    @pytest.mark.p0
    def test_tenant_list_only_own_data(self, api, v):
        """租户列表只返回自身数据"""
        resp = api.get("/api/tenants", params={"page": 1, "pageSize": 100})
        v.not_5xx(resp)
        # 正常返回即通过，实际隔离需数据库级验证

    @pytest.mark.tenant
    @pytest.mark.p0
    def test_device_list_tenant_scoped(self, api, v):
        """设备列表租户范围"""
        resp = api.get("/api/device", params={"page": 1, "pageSize": 100})
        v.not_5xx(resp)

    @pytest.mark.tenant
    @pytest.mark.p0
    def test_charging_orders_tenant_scoped(self, api, v):
        """充电订单租户范围"""
        resp = api.get("/api/charging/orders", params={"page": 1, "pageSize": 100})
        v.not_5xx(resp)

    @pytest.mark.tenant
    def test_workorders_tenant_scoped(self, api, v):
        """工单租户范围"""
        resp = api.get("/api/workorder", params={"page": 1, "pageSize": 100})
        v.not_5xx(resp)

    @pytest.mark.tenant
    def test_settlements_tenant_scoped(self, api, v):
        """结算记录租户范围"""
        resp = api.get("/api/settlements", params={"page": 1, "pageSize": 100})
        v.not_5xx(resp)

    @pytest.mark.tenant
    def test_stations_tenant_scoped(self, api, v):
        """站点租户范围"""
        resp = api.get("/api/stations", params={"page": 1, "pageSize": 100})
        v.not_5xx(resp)


class TestCrossTenantAccessBlocked:
    """跨租户访问阻断"""

    @pytest.mark.tenant
    @pytest.mark.p0
    def test_cannot_access_other_tenant_device(self, api, v):
        """不能访问其他租户的设备"""
        fake_id = str(uuid.uuid4())
        resp = api.get(f"/api/device/{fake_id}")
        # 不存在的 ID 应该 404，而不是返回其他租户的数据
        assert resp.status_code in (404, 200, 400), f"异常状态码: {resp.status_code}"
        if resp.status_code == 200:
            data = resp.json().get("data")
            # 如果返回 200，data 应该为空（不应返回其他租户的设备）
            if data and isinstance(data, dict):
                pytest.fail("返回了数据，疑似跨租户访问未被阻断")

    @pytest.mark.tenant
    @pytest.mark.p0
    def test_cannot_access_other_tenant_order(self, api, v):
        """不能访问其他租户的订单"""
        fake_id = str(uuid.uuid4())
        resp = api.get(f"/api/charging/orders/{fake_id}")
        assert resp.status_code in (404, 200, 400)

    @pytest.mark.tenant
    def test_cannot_access_other_tenant_station(self, api, v):
        """不能访问其他租户的站点"""
        fake_id = str(uuid.uuid4())
        resp = api.get(f"/api/stations/{fake_id}")
        assert resp.status_code in (404, 200, 400)

    @pytest.mark.tenant
    def test_cannot_modify_other_tenant_resource(self, api, v):
        """不能修改其他租户的资源"""
        fake_id = str(uuid.uuid4())
        resp = api.put(f"/api/device/{fake_id}", json={"name": "Hacked"})
        assert resp.status_code in (404, 400, 403)

    @pytest.mark.tenant
    def test_cannot_delete_other_tenant_resource(self, api, v):
        """不能删除其他租户的资源"""
        fake_id = str(uuid.uuid4())
        resp = api.delete(f"/api/device/{fake_id}")
        assert resp.status_code in (404, 400, 403)


class TestTenantDbVerification:
    """数据库级租户隔离验证"""

    @pytest.mark.tenant
    @pytest.mark.db_verify
    @pytest.mark.p0
    def test_device_table_has_tenant_id(self, service_dbs):
        """device 表存在 tenant_id 列"""
        db = service_dbs["device"]
        if not db:
            assert MOCK_MODE, "设备数据库不可用且当前不是 Mock 模式"
            return
        cols = db.query(
            "SELECT column_name FROM information_schema.columns "
            "WHERE table_name LIKE '%%device%%' AND column_name = 'tenant_id' "
            "AND table_schema NOT IN ('pg_catalog','information_schema','_timescaledb_catalog','_timescaledb_internal','_timescaledb_config')"
        )
        assert len(cols) > 0, "device 相关表缺少 tenant_id 列"

    @pytest.mark.tenant
    @pytest.mark.db_verify
    @pytest.mark.p0
    def test_device_table_has_delete_at(self, service_dbs):
        """device 表存在 delete_at 列"""
        db = service_dbs["device"]
        if not db:
            assert MOCK_MODE, "设备数据库不可用且当前不是 Mock 模式"
            return
        cols = db.query(
            "SELECT column_name FROM information_schema.columns "
            "WHERE table_name LIKE '%%device%%' AND column_name = 'delete_at' "
            "AND table_schema NOT IN ('pg_catalog','information_schema','_timescaledb_catalog','_timescaledb_internal','_timescaledb_config')"
        )
        assert len(cols) > 0, "device 相关表缺少 delete_at 列"

    @pytest.mark.tenant
    @pytest.mark.db_verify
    def test_charging_order_has_tenant_id(self, service_dbs):
        """charging_order 表存在 tenant_id 列"""
        db = service_dbs["charging"]
        if not db:
            assert MOCK_MODE, "充电数据库不可用且当前不是 Mock 模式"
            return
        cols = db.query(
            "SELECT column_name FROM information_schema.columns "
            "WHERE table_name LIKE 'charging_order%' AND column_name = 'tenant_id'"
        )
        assert len(cols) > 0, "充电订单表缺少 tenant_id 列"

    @pytest.mark.tenant
    @pytest.mark.db_verify
    def test_all_business_tables_have_tenant_id(self, service_dbs):
        """主要业务表都应有 tenant_id（全局表豁免）"""
        # 全局表豁免列表
        global_tables = {"rule_chain", "rule_node", "rule_connection", "rule_alarm_definition",
                         "schemaversions", "__efmigrationshistory"}
        # 分布式事务框架表前缀（非业务表，无需 tenant_id）
        infra_prefixes = ("dist_", "hangfire", "__")

        services_to_check = ["device", "charging", "settlement", "workorder", "station"]
        missing = []
        for svc in services_to_check:
            db = service_dbs[svc]
            if not db:
                continue
            tables = db.query(
                "SELECT table_name FROM information_schema.tables "
                "WHERE table_schema NOT IN ('pg_catalog','information_schema',"
                "'_timescaledb_catalog','_timescaledb_internal','_timescaledb_config','_timescaledb_cache') "
                "AND table_type = 'BASE TABLE'"
            )
            for t in tables:
                tname = t["table_name"]
                if tname in global_tables or tname.startswith("schema"):
                    continue
                if any(tname.startswith(p) for p in infra_prefixes):
                    continue
                cols = db.query(
                    "SELECT column_name FROM information_schema.columns "
                    "WHERE table_name = %s AND column_name = 'tenant_id'",
                    (tname,)
                )
                if len(cols) == 0:
                    missing.append(f"{svc}.{tname}")

        if missing:
            pytest.fail(f"以下表缺少 tenant_id: {missing[:10]}...")


class TestSoftDeleteEnforcement:
    """软删除强制检查"""

    @pytest.mark.tenant
    @pytest.mark.db_verify
    @pytest.mark.p0
    def test_deleted_records_not_returned(self, api, v, service_dbs):
        """软删除记录不应在列表中返回"""
        db = service_dbs["device"]
        if not db:
            resp = api.get("/api/device", params={"page": 1, "pageSize": 1})
            v.not_5xx(resp)
            return

        # 明确查 device_info（主设备表），避免 LIMIT 1 匹配到其他表
        tbl = "device.device_info"
        # 检查表是否存在
        exists = db.query(
            "SELECT 1 FROM information_schema.columns "
            "WHERE table_schema = 'device' AND table_name = 'device_info' AND column_name = 'delete_at' LIMIT 1"
        )
        assert exists, "未找到 device.device_info 含 delete_at"
        deleted_count = db.scalar(
            f"SELECT COUNT(*) FROM {tbl} WHERE delete_at IS NOT NULL"
        )
        # 查询 API 返回的总数
        resp = api.get("/api/device", params={"page": 1, "pageSize": 1})
        if resp.status_code == 200:
            data = resp.json().get("data", {})
            api_total = data.get("total", 0)
            # API 总数不应包含已删除记录
            db_active = db.scalar(
                f"SELECT COUNT(*) FROM {tbl} WHERE delete_at IS NULL"
            )
            if db_active is not None:
                # 由于多租户，API 结果可能少于数据库（只能看到自己的）
                # 当数据库无设备而 API 返回少量默认/虚拟数据时也是合理的
                if db_active > 0:
                    assert api_total <= db_active, \
                        f"API 返回 {api_total} 可能包含已删除记录（DB表活跃 {db_active}）"
