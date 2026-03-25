"""
测试 04 — 业务逻辑与状态机测试
================================
充电订单状态机 · 工单生命周期 · 结算流程 · 规则引擎
"""
import uuid
import pytest
from datetime import datetime


class TestChargingOrderStateMachine:
    """充电订单状态机"""

    @pytest.mark.business
    @pytest.mark.p0
    def test_create_charging_order(self, api, v, uid):
        """创建充电订单"""
        resp = api.post("/api/charging/orders", json={
            "stationId": str(uuid.uuid4()),
            "deviceId": str(uuid.uuid4()),
            "connectorId": "1",
            "userId": str(uuid.uuid4()),
        })
        v.not_5xx(resp)

    @pytest.mark.business
    @pytest.mark.p0
    def test_query_charging_orders_by_status(self, api, v):
        """按状态查询充电订单"""
        for status in ["charging", "completed", "abnormal"]:
            resp = api.get("/api/charging/orders", params={
                "status": status, "page": 1, "pageSize": 5,
            })
            v.not_5xx(resp)

    @pytest.mark.business
    def test_admin_order_query(self, api, v):
        """管理端充电订单查询"""
        resp = api.get("/api/charging/admin/orders", params={
            "page": 1, "pageSize": 10,
        })
        v.not_5xx(resp)

    @pytest.mark.business
    def test_charging_pricing_list(self, api, v):
        """充电定价策略列表"""
        resp = api.get("/api/charging/pricing", params={"page": 1, "pageSize": 10})
        v.not_5xx(resp)

    @pytest.mark.business
    def test_reservation_list(self, api, v):
        """预约列表查询"""
        resp = api.get("/api/charging/reservation", params={"page": 1, "pageSize": 10})
        v.not_5xx(resp)

    @pytest.mark.business
    def test_refund_list(self, api, v):
        """退款记录列表"""
        resp = api.get("/api/refund", params={"page": 1, "pageSize": 10})
        v.not_5xx(resp)


class TestWorkOrderLifecycle:
    """工单生命周期"""

    @pytest.mark.business
    @pytest.mark.p0
    def test_workorder_list(self, api, v):
        """工单列表查询"""
        resp = api.get("/api/workorder", params={"page": 1, "pageSize": 10})
        v.not_5xx(resp)

    @pytest.mark.business
    @pytest.mark.p0
    def test_create_workorder(self, api, v, uid):
        """创建工单"""
        resp = api.post("/api/workorder", json={
            "title": f"AutoTest工单_{uid}",
            "type": "repair",
            "priority": "high",
            "description": "自动化测试创建的工单",
        })
        v.not_5xx(resp)
        if resp.status_code in (200, 201):
            data = resp.json().get("data", {})
            rid = data.get("id") if isinstance(data, dict) else data
            if rid:
                # 清理
                api.delete(f"/api/workorder/{rid}")

    @pytest.mark.business
    def test_workorder_approval_list(self, api, v):
        """审批工单列表"""
        resp = api.get("/api/workorder/approval", params={"page": 1, "pageSize": 10})
        v.not_5xx(resp)

    @pytest.mark.business
    def test_workorder_dispatch_list(self, api, v):
        """派单列表"""
        resp = api.get("/api/workorder/dispatch", params={"page": 1, "pageSize": 10})
        v.not_5xx(resp)

    @pytest.mark.business
    def test_workorder_staff_list(self, api, v):
        """工单人员列表"""
        resp = api.get("/api/workorder/staff", params={"page": 1, "pageSize": 10})
        v.not_5xx(resp)

    @pytest.mark.business
    def test_workorder_stats(self, api, v):
        """工单统计"""
        resp = api.get("/api/workorder/stats")
        v.not_5xx(resp)

    @pytest.mark.business
    def test_spare_parts_list(self, api, v):
        """备件列表"""
        resp = api.get("/api/spare-part", params={"page": 1, "pageSize": 10})
        v.not_5xx(resp)

    @pytest.mark.business
    def test_shift_list(self, api, v):
        """排班列表"""
        resp = api.get("/api/shift", params={"page": 1, "pageSize": 10})
        v.not_5xx(resp)

    @pytest.mark.business
    def test_satisfaction_list(self, api, v):
        """满意度列表"""
        resp = api.get("/api/satisfaction", params={"page": 1, "pageSize": 10})
        v.not_5xx(resp)


class TestSettlementFlow:
    """结算流程"""

    @pytest.mark.business
    @pytest.mark.p1
    def test_settlement_records_list(self, api, v):
        """结算记录列表"""
        resp = api.get("/api/settlements", params={"page": 1, "pageSize": 10})
        v.not_5xx(resp)

    @pytest.mark.business
    def test_merchant_settlement_list(self, api, v):
        """商户结算列表"""
        resp = api.get("/api/merchant-settlement", params={"page": 1, "pageSize": 10})
        v.not_5xx(resp)

    @pytest.mark.business
    def test_profit_sharing_list(self, api, v):
        """分润列表"""
        resp = api.get("/api/profit-sharing", params={"page": 1, "pageSize": 10})
        v.not_5xx(resp)

    @pytest.mark.business
    def test_withdraw_list(self, api, v):
        """提现列表"""
        resp = api.get("/api/settlement/withdraw", params={"page": 1, "pageSize": 10})
        v.not_5xx(resp)

    @pytest.mark.business
    def test_settlement_stats(self, api, v):
        """结算统计"""
        resp = api.get("/api/settlement-stats")
        v.not_5xx(resp)


class TestRuleEngine:
    """规则引擎"""

    @pytest.mark.business
    @pytest.mark.p1
    def test_rule_chains_list(self, api, v):
        """规则链列表"""
        resp = api.get("/api/ruleengine/chains", params={"page": 1, "pageSize": 10})
        v.not_5xx(resp)

    @pytest.mark.business
    def test_rule_alarms_list(self, api, v):
        """告警规则列表"""
        resp = api.get("/api/ruleengine/alarms", params={"page": 1, "pageSize": 10})
        v.not_5xx(resp)

    @pytest.mark.business
    def test_create_rule_chain(self, api, v, uid):
        """创建规则链"""
        resp = api.post("/api/ruleengine/chains", json={
            "name": f"AutoChain_{uid}",
            "description": "自动化测试规则链",
            "type": "device",
        })
        v.not_5xx(resp)
        if resp.status_code in (200, 201):
            data = resp.json().get("data", {})
            rid = data.get("id") if isinstance(data, dict) else data
            if rid:
                api.delete(f"/api/ruleengine/chains/{rid}")


class TestStationManagement:
    """站点管理业务"""

    @pytest.mark.business
    @pytest.mark.p1
    def test_station_list(self, api, v):
        """站点列表"""
        resp = api.get("/api/stations", params={"page": 1, "pageSize": 10})
        v.not_5xx(resp)

    @pytest.mark.business
    def test_station_price_list(self, api, v):
        """站点价格列表"""
        resp = api.get("/api/prices", params={"page": 1, "pageSize": 10})
        v.not_5xx(resp)

    @pytest.mark.business
    def test_admin_station_list(self, api, v):
        """管理端站点列表"""
        resp = api.get("/api/station/admin", params={"page": 1, "pageSize": 10})
        v.not_5xx(resp)


class TestDeviceManagement:
    """设备管理业务"""

    @pytest.mark.business
    @pytest.mark.p1
    def test_device_list(self, api, v):
        """设备列表"""
        resp = api.get("/api/device", params={"page": 1, "pageSize": 10})
        v.not_5xx(resp)

    @pytest.mark.business
    def test_device_alerts(self, api, v):
        """设备告警列表"""
        resp = api.get("/api/device/alerts", params={"page": 1, "pageSize": 10})
        v.not_5xx(resp)

    @pytest.mark.business
    def test_device_profiles(self, api, v):
        """设备模型列表"""
        resp = api.get("/api/device/profiles", params={"page": 1, "pageSize": 10})
        v.not_5xx(resp)

    @pytest.mark.business
    def test_device_firmware(self, api, v):
        """固件列表"""
        resp = api.get("/api/device/firmware", params={"page": 1, "pageSize": 10})
        v.not_5xx(resp)

    @pytest.mark.business
    def test_device_assets(self, api, v):
        """设备资产列表"""
        resp = api.get("/api/device-assets", params={"page": 1, "pageSize": 10})
        v.not_5xx(resp)

    @pytest.mark.business
    def test_edge_gateways(self, api, v):
        """边缘网关列表"""
        resp = api.get("/api/device/edge-gateways", params={"page": 1, "pageSize": 10})
        v.not_5xx(resp)


class TestAccountFinancial:
    """账户与财务"""

    @pytest.mark.business
    def test_user_accounts(self, api, v):
        """用户账户列表"""
        resp = api.get("/api/users", params={"page": 1, "pageSize": 10})
        v.not_5xx(resp)

    @pytest.mark.business
    def test_coupons(self, api, v):
        """优惠券列表"""
        resp = api.get("/api/coupon", params={"page": 1, "pageSize": 10})
        v.not_5xx(resp)

    @pytest.mark.business
    def test_invoices(self, api, v):
        """发票列表"""
        resp = api.get("/api/invoice", params={"page": 1, "pageSize": 10})
        v.not_5xx(resp)

    @pytest.mark.business
    def test_membership(self, api, v):
        """会员列表"""
        resp = api.get("/api/membership", params={"page": 1, "pageSize": 10})
        v.not_5xx(resp)

    @pytest.mark.business
    def test_vehicles(self, api, v):
        """车辆列表"""
        resp = api.get("/api/vehicles", params={"page": 1, "pageSize": 10})
        v.not_5xx(resp)

    @pytest.mark.business
    def test_points(self, api, v):
        """积分查询"""
        resp = api.get("/api/points", params={"page": 1, "pageSize": 10})
        v.not_5xx(resp)


class TestAnalyticsReporting:
    """分析与报表"""

    @pytest.mark.business
    def test_analytics_dashboard(self, api, v):
        """分析仪表盘"""
        resp = api.get("/api/analytics/dashboard")
        v.not_5xx(resp)

    @pytest.mark.business
    def test_charging_analytics(self, api, v):
        """充电分析"""
        resp = api.get("/api/analytics/charging")
        v.not_5xx(resp)

    @pytest.mark.business
    def test_revenue_analytics(self, api, v):
        """营收分析"""
        resp = api.get("/api/analytics/revenue")
        v.not_5xx(resp)

    @pytest.mark.business
    def test_anomaly_detection(self, api, v):
        """异常检测"""
        resp = api.get("/api/analytics/anomaly")
        v.not_5xx(resp)

    @pytest.mark.business
    def test_report_center(self, api, v):
        """报表中心"""
        resp = api.get("/api/report-center", params={"page": 1, "pageSize": 10})
        v.not_5xx(resp)

    @pytest.mark.business
    def test_funnel_analysis(self, api, v):
        """漏斗分析"""
        resp = api.get("/api/analytics/funnel", params={"page": 1, "pageSize": 10})
        v.not_5xx(resp)

    @pytest.mark.business
    def test_event_tracking(self, api, v):
        """事件追踪"""
        resp = api.get("/api/analytics/event-tracking", params={"page": 1, "pageSize": 10})
        v.not_5xx(resp)


class TestBlockchainOps:
    """区块链操作"""

    @pytest.mark.business
    def test_wallet_list(self, api, v):
        """钱包列表"""
        resp = api.get("/api/wallet", params={"page": 1, "pageSize": 10})
        v.not_5xx(resp)

    @pytest.mark.business
    def test_transactions(self, api, v):
        """交易记录"""
        resp = api.get("/api/transactions", params={"page": 1, "pageSize": 10})
        v.not_5xx(resp)

    @pytest.mark.business
    def test_contracts(self, api, v):
        """合约列表"""
        resp = api.get("/api/contracts", params={"page": 1, "pageSize": 10})
        v.not_5xx(resp)

    @pytest.mark.business
    def test_certificates(self, api, v):
        """证书列表"""
        resp = api.get("/api/certificates", params={"page": 1, "pageSize": 10})
        v.not_5xx(resp)


class TestDigitalTwin:
    """数字孪生"""

    @pytest.mark.business
    def test_digital_twin_list(self, api, v):
        """孪生体列表"""
        resp = api.get("/api/digital-twin", params={"page": 1, "pageSize": 10})
        v.not_5xx(resp)

    @pytest.mark.business
    def test_scene_models(self, api, v):
        """场景模型列表"""
        resp = api.get("/api/scene-model", params={"page": 1, "pageSize": 10})
        v.not_5xx(resp)

    @pytest.mark.business
    def test_visualization(self, api, v):
        """可视化列表"""
        resp = api.get("/api/visualization", params={"page": 1, "pageSize": 10})
        v.not_5xx(resp)

    @pytest.mark.business
    def test_device_model_catalog(self, api, v):
        """设备模型目录"""
        resp = api.get("/api/device-model-catalog", params={"page": 1, "pageSize": 10})
        v.not_5xx(resp)


class TestIotCloudAI:
    """IoT 与 AI"""

    @pytest.mark.business
    def test_ai_models(self, api, v):
        """AI 模型列表"""
        resp = api.get("/api/iotcloudai/models", params={"page": 1, "pageSize": 10})
        v.not_5xx(resp)

    @pytest.mark.business
    def test_ai_training(self, api, v):
        """训练任务列表"""
        resp = api.get("/api/iotcloudai/training", params={"page": 1, "pageSize": 10})
        v.not_5xx(resp)

    @pytest.mark.business
    def test_ai_config(self, api, v):
        """AI 配置"""
        resp = api.get("/api/iotcloudai/config", params={"page": 1, "pageSize": 10})
        v.not_5xx(resp)

    @pytest.mark.business
    def test_ai_dashboard(self, api, v):
        """AI 仪表盘"""
        resp = api.get("/api/iotcloudai/dashboard")
        v.not_5xx(resp)


class TestEnergyServices:
    """能源服务"""

    @pytest.mark.business
    def test_vpp_list(self, api, v):
        """虚拟电厂列表"""
        resp = api.get("/api/vpp", params={"page": 1, "pageSize": 10})
        v.not_5xx(resp)

    @pytest.mark.business
    def test_microgrid_list(self, api, v):
        """微电网列表"""
        resp = api.get("/api/microgrid", params={"page": 1, "pageSize": 10})
        v.not_5xx(resp)

    @pytest.mark.business
    def test_pvessc_sites(self, api, v):
        """光储充站点"""
        resp = api.get("/api/pvessc/site", params={"page": 1, "pageSize": 10})
        v.not_5xx(resp)

    @pytest.mark.business
    def test_electrade(self, api, v):
        """电力交易"""
        resp = api.get("/api/electrade", params={"page": 1, "pageSize": 10})
        v.not_5xx(resp)

    @pytest.mark.business
    def test_demandresp(self, api, v):
        """需求响应"""
        resp = api.get("/api/demandresp/instructions", params={"page": 1, "pageSize": 10})
        v.not_5xx(resp)


class TestIngestionData:
    """数据采集"""

    @pytest.mark.business
    def test_collection_points(self, api, v):
        """采集点列表"""
        resp = api.get("/api/collection-point", params={"page": 1, "pageSize": 10})
        v.not_5xx(resp)

    @pytest.mark.business
    def test_data_sources(self, api, v):
        """数据源列表"""
        resp = api.get("/api/data-source", params={"page": 1, "pageSize": 10})
        v.not_5xx(resp)

    @pytest.mark.business
    def test_ingestion_tasks(self, api, v):
        """采集任务列表"""
        resp = api.get("/api/ingestion-task", params={"page": 1, "pageSize": 10})
        v.not_5xx(resp)

    @pytest.mark.business
    def test_protocols(self, api, v):
        """协议列表"""
        resp = api.get("/api/ingestion/protocols", params={"page": 1, "pageSize": 10})
        v.not_5xx(resp)
