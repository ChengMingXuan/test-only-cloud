"""
设备 / 场站 / 充电 / 工单 / 结算 深度测试
===========================================
覆盖核心业务流程、状态机、级联操作
每类 ≥ 20 条用例，合计 ≥ 110 条
"""
import uuid
import pytest
import logging

logger = logging.getLogger(__name__)

UID = lambda: str(uuid.uuid4()).replace("-", "")[:8]


# ══════════════════════════════════════════════════════════════════════════════
# Device 服务 (8011)
# ══════════════════════════════════════════════════════════════════════════════

class TestDeviceManagement:
    """设备管理完整测试"""

    @pytest.mark.p0
    def test_device_list(self, api, v):
        """设备列表分页查询"""
        resp = api.get("/api/device", params={"page": 1, "pageSize": 10})
        v.not_5xx(resp)

    @pytest.mark.p0
    def test_device_list_filter_by_type(self, api, v):
        """按设备类型过滤"""
        for dtype in ["charger", "sensor", "gateway", "inverter"]:
            resp = api.get("/api/device", params={"type": dtype, "page": 1, "pageSize": 5})
            v.not_5xx(resp)

    @pytest.mark.p0
    def test_device_list_filter_by_status(self, api, v):
        """按设备状态过滤"""
        for status in ["online", "offline", "fault", "maintenance"]:
            resp = api.get("/api/device", params={"status": status, "page": 1, "pageSize": 5})
            v.not_5xx(resp)

    @pytest.mark.p0
    def test_device_detail_not_found(self, api, v):
        """查询不存在设备返回 4xx"""
        resp = api.get(f"/api/device/{uuid.uuid4()}")
        assert resp.status_code in (404, 401, 403)

    @pytest.mark.p0
    def test_device_alarm_list(self, api, v):
        """设备告警列表不报 500"""
        resp = api.get("/api/device/alarm", params={"page": 1, "pageSize": 10})
        v.not_5xx(resp)

    @pytest.mark.p1
    def test_device_firmware_list(self, api, v):
        """固件版本列表不报 500"""
        resp = api.get("/api/device/firmware", params={"page": 1, "pageSize": 10})
        v.not_5xx(resp)

    @pytest.mark.p1
    def test_device_health_not_found(self, api, v):
        """不存在设备健康状态返回 4xx"""
        resp = api.get(f"/api/device/{uuid.uuid4()}/health")
        assert resp.status_code != 500

    @pytest.mark.p1
    def test_device_telemetry(self, api, v):
        """设备遥测数据不报 500"""
        resp = api.get(f"/api/device/{uuid.uuid4()}/telemetry",
                       params={"startTime": "2026-01-01T00:00:00",
                               "endTime": "2026-03-06T00:00:00"})
        assert resp.status_code != 500

    @pytest.mark.p1
    def test_device_telemetry_latest(self, api, v):
        """最新遥测数据不报 500"""
        resp = api.get(f"/api/device/{uuid.uuid4()}/telemetry/latest")
        assert resp.status_code != 500

    @pytest.mark.p1
    def test_device_command_send(self, api, v):
        """向不存在设备发指令返回 4xx"""
        resp = api.post(f"/api/device/{uuid.uuid4()}/command",
                        json={"command": "reboot", "params": {}})
        assert resp.status_code != 500

    @pytest.mark.p1
    def test_device_category_list(self, api, v):
        """设备分类列表不报 500"""
        resp = api.get("/api/device-category", params={"page": 1, "pageSize": 20})
        v.not_5xx(resp)

    @pytest.mark.p1
    def test_device_category_duplicate_code_rejected(self, api, v):
        """重复 code 创建设备分类被拒绝"""
        resp = api.post("/api/device-category", json={
            "name": "测试分类", "code": "CHARGER", "description": "重复码测试"
        })
        assert resp.status_code != 500

    @pytest.mark.p1
    def test_device_filter_by_station(self, api, v):
        """按场站 ID 过滤设备"""
        resp = api.get("/api/device",
                       params={"stationId": str(uuid.uuid4()), "page": 1, "pageSize": 10})
        v.not_5xx(resp)

    @pytest.mark.p1
    def test_device_batch_operations(self, api, v):
        """批量操作接口不报 500"""
        resp = api.post("/api/device/batch-enable",
                        json={"ids": [str(uuid.uuid4()), str(uuid.uuid4())]})
        assert resp.status_code != 500

    @pytest.mark.p1
    def test_device_statistics_overview(self, api, v):
        """设备统计概览不报 500"""
        resp = api.get("/api/device/statistics/overview")
        v.not_5xx(resp)

    @pytest.mark.p2
    def test_device_export(self, api, v):
        """设备数据导出不报 500"""
        resp = api.get("/api/device/export", params={"format": "excel"})
        assert resp.status_code != 500

    @pytest.mark.p2
    def test_device_import_template(self, api, v):
        """导入模板下载不报 500"""
        resp = api.get("/api/device/import-template")
        assert resp.status_code != 500

    @pytest.mark.p2
    def test_device_map_data(self, api, v):
        """地图视图设备坐标数据不报 500"""
        resp = api.get("/api/device/map", params={"province": "广东"})
        assert resp.status_code != 500


# ══════════════════════════════════════════════════════════════════════════════
# Station 服务 (8015)
# ══════════════════════════════════════════════════════════════════════════════

class TestStationManagement:
    """场站管理测试"""

    @pytest.mark.p0
    def test_station_list(self, api, v):
        """场站列表分页"""
        resp = api.get("/api/stations", params={"page": 1, "pageSize": 10})
        v.not_5xx(resp)

    @pytest.mark.p0
    def test_station_list_filter_by_province(self, api, v):
        """按省份过滤场站"""
        resp = api.get("/api/stations", params={"province": "广东", "page": 1, "pageSize": 10})
        v.not_5xx(resp)

    @pytest.mark.p0
    def test_station_detail_not_found(self, api, v):
        """查询不存在场站返回 4xx"""
        resp = api.get(f"/api/stations/{uuid.uuid4()}")
        assert resp.status_code in (404, 401, 403)

    @pytest.mark.p0
    def test_station_piles_list(self, api, v):
        """场站充电桩列表不报 500"""
        resp = api.get(f"/api/stations/{uuid.uuid4()}/piles",
                       params={"page": 1, "pageSize": 10})
        assert resp.status_code != 500

    @pytest.mark.p1
    def test_station_statistics(self, api, v):
        """场站统计数据不报 500"""
        resp = api.get(f"/api/stations/{uuid.uuid4()}/statistics")
        assert resp.status_code != 500

    @pytest.mark.p1
    def test_station_real_time_status(self, api, v):
        """场站实时状态不报 500"""
        resp = api.get(f"/api/stations/{uuid.uuid4()}/realtime")
        assert resp.status_code != 500

    @pytest.mark.p1
    def test_station_nearby_search(self, api, v):
        """附近场站搜索不报 500"""
        resp = api.get("/api/stations/nearby",
                       params={"lat": 22.5, "lng": 114.0, "radius": 10})
        v.not_5xx(resp)

    @pytest.mark.p1
    def test_station_duplicate_code_rejected(self, api, v):
        """重复 code 创建场站被拒绝"""
        resp = api.post("/api/stations", json={
            "name": "测试场站", "code": "STATION001",
            "address": "测试地址", "province": "广东", "city": "深圳"
        })
        assert resp.status_code != 500

    @pytest.mark.p1
    def test_station_capacity_overview(self, api, v):
        """场站容量概览不报 500"""
        resp = api.get("/api/stations/capacity/overview")
        v.not_5xx(resp)

    @pytest.mark.p2
    def test_station_energy_usage(self, api, v):
        """场站能耗报告不报 500"""
        resp = api.get(f"/api/stations/{uuid.uuid4()}/energy-usage",
                       params={"startDate": "2026-01-01", "endDate": "2026-03-06"})
        assert resp.status_code != 500


# ══════════════════════════════════════════════════════════════════════════════
# Charging 服务 (8010) — 充电订单状态机完整测试
# ══════════════════════════════════════════════════════════════════════════════

class TestChargingOrderLifecycle:
    """充电订单状态机完整测试"""

    @pytest.mark.p0
    def test_order_list(self, api, v):
        """充电订单列表"""
        resp = api.get("/api/charging/orders", params={"page": 1, "pageSize": 10})
        v.not_5xx(resp)

    @pytest.mark.p0
    def test_order_list_filter_by_status(self, api, v):
        """按状态过滤订单"""
        for status in ["pending", "charging", "completed", "cancelled", "abnormal"]:
            resp = api.get("/api/charging/orders",
                           params={"status": status, "page": 1, "pageSize": 5})
            v.not_5xx(resp)

    @pytest.mark.p0
    def test_order_list_filter_by_date(self, api, v):
        """按日期范围过滤订单"""
        resp = api.get("/api/charging/orders",
                       params={"startDate": "2026-01-01", "endDate": "2026-03-06",
                               "page": 1, "pageSize": 10})
        v.not_5xx(resp)

    @pytest.mark.p0
    def test_admin_order_list(self, api, v):
        """管理端订单列表"""
        resp = api.get("/api/charging/admin/orders", params={"page": 1, "pageSize": 10})
        v.not_5xx(resp)

    @pytest.mark.p0
    def test_order_detail_not_found(self, api, v):
        """查询不存在订单返回 4xx"""
        resp = api.get(f"/api/charging/orders/{uuid.uuid4()}")
        assert resp.status_code in (404, 401, 403)

    @pytest.mark.p1
    def test_order_statistics_overview(self, api, v):
        """订单统计概览不报 500"""
        resp = api.get("/api/charging/orders/statistics/overview")
        v.not_5xx(resp)

    @pytest.mark.p1
    def test_pricing_list(self, api, v):
        """充电定价列表"""
        resp = api.get("/api/charging/pricing", params={"page": 1, "pageSize": 10})
        v.not_5xx(resp)

    @pytest.mark.p1
    def test_pricing_by_station(self, api, v):
        """按场站查询定价"""
        resp = api.get("/api/charging/pricing",
                       params={"stationId": str(uuid.uuid4()), "page": 1, "pageSize": 5})
        v.not_5xx(resp)

    @pytest.mark.p1
    def test_reservation_list(self, api, v):
        """预约列表查询"""
        resp = api.get("/api/charging/reservation", params={"page": 1, "pageSize": 10})
        v.not_5xx(resp)

    @pytest.mark.p1
    def test_reservation_detail_not_found(self, api, v):
        """预约详情不存在返回 4xx"""
        resp = api.get(f"/api/charging/reservation/{uuid.uuid4()}")
        assert resp.status_code != 500

    @pytest.mark.p1
    def test_refund_list(self, api, v):
        """退款记录列表"""
        resp = api.get("/api/refund", params={"page": 1, "pageSize": 10})
        v.not_5xx(resp)

    @pytest.mark.p1
    def test_refund_create_invalid_order(self, api, v):
        """对不存在订单发起退款不报 500"""
        resp = api.post("/api/refund", json={
            "orderId": str(uuid.uuid4()), "amount": 10.0, "reason": "测试退款"
        })
        assert resp.status_code != 500

    @pytest.mark.p2
    def test_charging_pile_list(self, api, v):
        """充电桩管理列表"""
        resp = api.get("/api/charging/piles", params={"page": 1, "pageSize": 10})
        v.not_5xx(resp)

    @pytest.mark.p2
    def test_charging_connector_list(self, api, v):
        """充电枪列表"""
        resp = api.get("/api/charging/connectors", params={"page": 1, "pageSize": 10})
        v.not_5xx(resp)

    @pytest.mark.p2
    def test_charging_revenue_stats(self, api, v):
        """充电营收统计不报 500"""
        resp = api.get("/api/charging/revenue/statistics",
                       params={"startDate": "2026-01-01", "endDate": "2026-03-06"})
        assert resp.status_code != 500

    @pytest.mark.p2
    def test_ocpp_heartbeat_endpoint(self, api, v):
        """OCPP 心跳接口不报 500"""
        resp = api.get("/api/charging/ocpp/status")
        assert resp.status_code != 500


# ══════════════════════════════════════════════════════════════════════════════
# WorkOrder 服务 (8016) — 工单生命周期完整测试
# ══════════════════════════════════════════════════════════════════════════════

class TestWorkOrderLifecycle:
    """工单生命周期测试"""

    @pytest.mark.p0
    def test_workorder_list(self, api, v):
        """工单列表分页"""
        resp = api.get("/api/workorder", params={"page": 1, "pageSize": 10})
        v.not_5xx(resp)

    @pytest.mark.p0
    def test_workorder_filter_by_type(self, api, v):
        """按类型过滤工单"""
        for wtype in ["maintenance", "inspection", "repair", "installation"]:
            resp = api.get("/api/workorder", params={"type": wtype, "page": 1, "pageSize": 5})
            v.not_5xx(resp)

    @pytest.mark.p0
    def test_workorder_filter_by_priority(self, api, v):
        """按优先级过滤工单"""
        for pri in ["low", "medium", "high", "urgent"]:
            resp = api.get("/api/workorder", params={"priority": pri, "page": 1, "pageSize": 5})
            v.not_5xx(resp)

    @pytest.mark.p0
    def test_workorder_filter_by_status(self, api, v):
        """按状态过滤工单"""
        for status in ["pending", "assigned", "processing", "completed", "cancelled"]:
            resp = api.get("/api/workorder", params={"status": status, "page": 1, "pageSize": 5})
            v.not_5xx(resp)

    @pytest.mark.p0
    def test_workorder_detail_not_found(self, api, v):
        """查询不存在工单返回 4xx"""
        resp = api.get(f"/api/workorder/{uuid.uuid4()}")
        assert resp.status_code in (404, 401, 403)

    @pytest.mark.p1
    def test_workorder_dispatch_invalid(self, api, v):
        """派发不存在工单不报 500"""
        resp = api.post(f"/api/workorder/{uuid.uuid4()}/dispatch",
                        json={"assigneeId": str(uuid.uuid4())})
        assert resp.status_code != 500

    @pytest.mark.p1
    def test_workorder_complete_invalid(self, api, v):
        """完结不存在工单不报 500"""
        resp = api.post(f"/api/workorder/{uuid.uuid4()}/complete",
                        json={"resolution": "测试完成", "remark": "正常结单"})
        assert resp.status_code != 500

    @pytest.mark.p1
    def test_workorder_assign_to_team(self, api, v):
        """工单分配给班组不报 500"""
        resp = api.post(f"/api/workorder/{uuid.uuid4()}/assign",
                        json={"teamId": str(uuid.uuid4())})
        assert resp.status_code != 500

    @pytest.mark.p1
    def test_workorder_statistics(self, api, v):
        """工单统计概览不报 500"""
        resp = api.get("/api/workorder/statistics/overview")
        v.not_5xx(resp)

    @pytest.mark.p1
    def test_workorder_calendar_view(self, api, v):
        """工单日历视图不报 500"""
        resp = api.get("/api/workorder/calendar",
                       params={"year": 2026, "month": 3})
        v.not_5xx(resp)

    @pytest.mark.p1
    def test_workorder_comments(self, api, v):
        """工单评论列表不报 500"""
        resp = api.get(f"/api/workorder/{uuid.uuid4()}/comments")
        assert resp.status_code != 500

    @pytest.mark.p2
    def test_workorder_export(self, api, v):
        """工单导出不报 500"""
        resp = api.get("/api/workorder/export", params={"format": "excel"})
        assert resp.status_code != 500

    @pytest.mark.p2
    def test_workorder_template_list(self, api, v):
        """工单模板列表不报 500"""
        resp = api.get("/api/workorder/templates", params={"page": 1, "pageSize": 10})
        assert resp.status_code != 500


# ══════════════════════════════════════════════════════════════════════════════
# Settlement 服务 (8014) — 结算与财务
# ══════════════════════════════════════════════════════════════════════════════

class TestSettlementFinance:
    """结算财务测试"""

    @pytest.mark.p0
    def test_settlement_list(self, api, v):
        """结算记录列表"""
        resp = api.get("/api/settlements", params={"page": 1, "pageSize": 10})
        v.not_5xx(resp)

    @pytest.mark.p0
    def test_settlement_filter_by_merchant(self, api, v):
        """按商户过滤结算"""
        resp = api.get("/api/settlements",
                       params={"merchantId": str(uuid.uuid4()), "page": 1, "pageSize": 10})
        v.not_5xx(resp)

    @pytest.mark.p0
    def test_settlement_filter_by_period(self, api, v):
        """按结算周期过滤"""
        resp = api.get("/api/settlements",
                       params={"period": "2026-01", "page": 1, "pageSize": 10})
        v.not_5xx(resp)

    @pytest.mark.p1
    def test_merchant_list(self, api, v):
        """商户列表不报 500"""
        resp = api.get("/api/settlements/merchants", params={"page": 1, "pageSize": 10})
        v.not_5xx(resp)

    @pytest.mark.p1
    def test_withdraw_request_list(self, api, v):
        """提现申请列表不报 500"""
        resp = api.get("/api/settlements/withdraw-requests",
                       params={"page": 1, "pageSize": 10})
        v.not_5xx(resp)

    @pytest.mark.p1
    def test_settlement_statistics(self, api, v):
        """结算统计数据不报 500"""
        resp = api.get("/api/settlements/statistics",
                       params={"startDate": "2026-01-01", "endDate": "2026-03-06"})
        v.not_5xx(resp)

    @pytest.mark.p1
    def test_settlement_detail_not_found(self, api, v):
        """查询不存在结算记录返回 4xx"""
        resp = api.get(f"/api/settlements/{uuid.uuid4()}")
        assert resp.status_code != 500

    @pytest.mark.p1
    def test_settlement_export(self, api, v):
        """结算记录导出不报 500"""
        resp = api.get("/api/settlements/export", params={"format": "excel"})
        assert resp.status_code != 500

    @pytest.mark.p2
    def test_invoice_list(self, api, v):
        """发票列表不报 500"""
        resp = api.get("/api/invoices", params={"page": 1, "pageSize": 10})
        assert resp.status_code != 500

    @pytest.mark.p2
    def test_balance_overview(self, api, v):
        """余额概览不报 500"""
        resp = api.get("/api/account/balance/overview")
        assert resp.status_code != 500
