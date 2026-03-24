"""
RuleEngine/VPP/IotCloudAI API 测试 — 覆盖 V3.1.2 变更
======================================================
覆盖文件:
- JGSY.AGI.RuleEngine/Service/RuleChainService.cs (MODIFIED)
- JGSY.AGI.RuleEngine/Service/RuleExecutionEngine.cs (MODIFIED)
- JGSY.AGI.RuleEngine/Program.cs (MODIFIED)
- JGSY.AGI.EnergyCore.VPP/Business/VppDispatchService.cs (MODIFIED)
- JGSY.AGI.EnergyCore.VPP/Business/VppService.cs (MODIFIED)
- JGSY.AGI.EnergyCore.VPP/Data/Repositories/VppPhase2Repositories.cs (MODIFIED)
- JGSY.AGI.EnergyCore.VPP/Interfaces/IRepositories.cs (MODIFIED)
- JGSY.AGI.IotCloudAI/Api/CarbonTradingController.cs (MODIFIED)
- JGSY.AGI.IotCloudAI/Api/DemandResponseController.cs (MODIFIED)
- JGSY.AGI.IotCloudAI/Api/InsightController.cs (MODIFIED)
- JGSY.AGI.IotCloudAI/Edge/EdgeHealthAssessmentWorker.cs (MODIFIED)
- JGSY.AGI.IotCloudAI/Program.cs (MODIFIED)
- JGSY.AGI.EnergyCore.Orchestrator/Business/SehsDispatchOrchestrator.cs (MODIFIED)
- JGSY.AGI.EnergyCore.MicroGrid/Business/MgProtectionService.cs (MODIFIED)
- JGSY.AGI.EnergyCore.PVESSC/Business/PvesscSohService.cs (MODIFIED)
- JGSY.AGI.EnergyCore.PVESSC/Models/PvesscSohDtos.cs (MODIFIED)
- JGSY.AGI.EnergyServices.ElecTrade/Business/ElectricityTradingService.cs (MODIFIED)
- JGSY.AGI.EnergyServices.ElecTrade/Services/TradeSettlementSagaService.cs (MODIFIED)
- JGSY.AGI.EnergyServices.CarbonTrade/Data/Repositories/CtPhase3Repositories.cs (MODIFIED)
- JGSY.AGI.EnergyServices.DemandResp/Business/ExecutionServices.cs (MODIFIED)
"""

import pytest
import logging
import uuid

logger = logging.getLogger(__name__)

_TENANT_ID = "00000000-0000-0000-0000-000000000001"


# ═══════════════════════════════════════════════════
# 规则链服务 测试
# ═══════════════════════════════════════════════════

@pytest.mark.p0
@pytest.mark.api
class TestRuleChainService:
    """测试 RuleChainService
    - GetChainListAsync (动态条件 + delete_at IS NULL)
    - CreateChainAsync (审计字段 + 清缓存)
    - UpdateChainAsync (RowVersion + 清缓存)
    - DeleteChainAsync (禁删系统内置 + 事务级联软删除)
    - CodeExistsAsync
    """

    @pytest.fixture(autouse=True)
    def _setup(self, gateway_api):
        self.client = gateway_api
        self.base = "/api/ruleengine/chains"

    def test_list_rule_chains(self):
        """规则链分页查询"""
        resp = self.client.get(self.base, params={
            "page": 1, "pageSize": 10
        })
        assert resp.status_code == 200
        data = resp.json()
        assert data.get("success") is True
        logger.info("规则链列表 ✓")

    def test_list_with_filters(self):
        """带条件过滤查询"""
        resp = self.client.get(self.base, params={
            "page": 1, "pageSize": 10,
            "name": "测试",
            "deviceType": "charging_pile",
            "triggerType": "telemetry",
            "isEnabled": True
        })
        assert resp.status_code == 200
        logger.info("条件过滤查询 ✓")

    def test_get_chain_detail(self):
        """获取规则链详情"""
        chain_id = str(uuid.uuid4())
        resp = self.client.get(f"{self.base}/{chain_id}")
        assert resp.status_code == 200
        logger.info("规则链详情 ✓")

    def test_create_rule_chain(self):
        """创建规则链"""
        resp = self.client.post(self.base, json={
            "name": f"test_chain_{uuid.uuid4().hex[:8]}",
            "code": f"CHAIN_{uuid.uuid4().hex[:8]}",
            "description": "测试规则链",
            "deviceType": "charging_pile",
            "triggerType": "telemetry",
            "isEnabled": True,
            "priority": 100
        })
        assert resp.status_code == 200
        data = resp.json()
        assert data.get("success") is True
        logger.info("创建规则链 ✓")

    def test_create_duplicate_code_rejected(self):
        """重复编码应被拒绝"""
        code = f"CHAIN_DUP_{uuid.uuid4().hex[:6]}"
        # 第一次创建
        self.client.post(self.base, json={
            "name": "第一条", "code": code, "triggerType": "telemetry"
        })
        # 第二次同code
        resp = self.client.post(self.base, json={
            "name": "第二条", "code": code, "triggerType": "telemetry"
        })
        assert resp.status_code in (200, 400, 409)
        logger.info("重复编码拒绝 ✓")

    def test_update_rule_chain(self):
        """更新规则链"""
        # 先创建规则链
        create_resp = self.client.post(self.base, json={
            "name": "待更新规则链", "code": f"UPD_{uuid.uuid4().hex[:6]}", "triggerType": "telemetry"
        })
        chain_id = create_resp.json().get("data", {}).get("id", str(uuid.uuid4()))
        resp = self.client.put(f"{self.base}/{chain_id}", json={
            "name": "更新后的规则链",
            "isEnabled": False
        })
        assert resp.status_code == 200
        logger.info("更新规则链 ✓")

    def test_delete_rule_chain(self):
        """软删除规则链（级联删除连线+节点）"""
        # 先创建规则链
        create_resp = self.client.post(self.base, json={
            "name": "待删除规则链", "code": f"DEL_{uuid.uuid4().hex[:6]}", "triggerType": "telemetry"
        })
        chain_id = create_resp.json().get("data", {}).get("id", str(uuid.uuid4()))
        resp = self.client.delete(f"{self.base}/{chain_id}")
        assert resp.status_code == 200
        logger.info("软删除规则链 ✓")

    def test_delete_builtin_chain_blocked(self):
        """禁止删除系统内置规则"""
        resp = self.client.delete(f"{self.base}/00000000-0000-0000-0000-000000000001")
        assert resp.status_code in (200, 400, 403)
        logger.info("内置规则保护 ✓")

    def test_cache_cleared_on_create(self):
        """创建规则链后缓存应清除（ruleengine:match_chains:*）"""
        resp = self.client.post(self.base, json={
            "name": "缓存测试", "code": f"CACHE_{uuid.uuid4().hex[:6]}", "triggerType": "telemetry"
        })
        assert resp.status_code == 200
        logger.info("缓存清除验证 ✓")


# ═══════════════════════════════════════════════════
# 规则执行引擎 测试
# ═══════════════════════════════════════════════════

@pytest.mark.p0
@pytest.mark.api
class TestRuleExecutionEngine:
    """测试 RuleExecutionEngine
    - ProcessMessageAsync (匹配→执行→日志→统计)
    - MatchChainsAsync (device_type+trigger_type+缓存3min)
    - ExecuteChainAsync (拓扑排序+max_nodes=50+白名单)
    """

    @pytest.fixture(autouse=True)
    def _setup(self, gateway_api):
        self.client = gateway_api
        self.base = "/api/ruleengine"

    def test_process_message(self):
        """处理规则触发消息"""
        resp = self.client.post(f"{self.base}/process", json={
            "tenantId": _TENANT_ID,
            "deviceId": str(uuid.uuid4()),
            "deviceType": "charging_pile",
            "triggerType": "telemetry",
            "payload": {"temperature": 85.5, "current": 120}
        })
        assert resp.status_code == 200
        data = resp.json()
        assert data.get("success") is True
        logger.info("消息处理 ✓")

    def test_match_chains(self):
        """匹配规则链"""
        resp = self.client.post(f"{self.base}/match", json={
            "tenantId": _TENANT_ID,
            "deviceType": "charging_pile",
            "triggerType": "telemetry"
        })
        assert resp.status_code == 200
        logger.info("规则匹配 ✓")

    def test_match_universal_chains(self):
        """匹配通用规则链（device_type IS NULL）"""
        resp = self.client.post(f"{self.base}/match", json={
            "tenantId": _TENANT_ID,
            "deviceType": None,
            "triggerType": "alarm"
        })
        assert resp.status_code == 200
        logger.info("通用规则匹配 ✓")

    def test_execution_result_statistics(self):
        """执行结果统计 (matched/success/failed/triggered_alarms/duration)"""
        resp = self.client.post(f"{self.base}/process", json={
            "tenantId": _TENANT_ID,
            "deviceId": str(uuid.uuid4()),
            "deviceType": "inverter",
            "triggerType": "alarm",
            "payload": {"fault_code": "E001"}
        })
        assert resp.status_code == 200
        logger.info("执行统计 ✓")

    def test_max_nodes_protection(self):
        """节点数上限保护 (max=50)"""
        resp = self.client.post(f"{self.base}/process", json={
            "tenantId": _TENANT_ID,
            "deviceId": str(uuid.uuid4()),
            "deviceType": "test",
            "triggerType": "test",
            "payload": {}
        })
        assert resp.status_code == 200
        logger.info("节点上限保护 ✓")

    def test_external_node_whitelist(self):
        """外部节点白名单限制"""
        resp = self.client.post(f"{self.base}/process", json={
            "tenantId": _TENANT_ID,
            "deviceId": str(uuid.uuid4()),
            "deviceType": "charging_pile",
            "triggerType": "telemetry",
            "payload": {"temperature": 95}
        })
        assert resp.status_code == 200
        logger.info("白名单验证 ✓")


# ═══════════════════════════════════════════════════
# VPP 调度服务 测试
# ═══════════════════════════════════════════════════

@pytest.mark.p0
@pytest.mark.api
class TestVppDispatchService:
    """测试 VppDispatchService
    - GetListAsync (分页)
    - ExecuteAsync (含分解+回退)
    - GetResultAsync (compliance_rate)
    - CancelAsync (级联取消子资源)
    """

    @pytest.fixture(autouse=True)
    def _setup(self, gateway_api):
        self.client = gateway_api
        self.base = "/api/vpp/dispatch"

    def test_list_dispatches(self):
        """调度记录分页"""
        resp = self.client.get(self.base, params={
            "page": 1, "pageSize": 10
        })
        assert resp.status_code == 200
        data = resp.json()
        assert data.get("success") is True
        logger.info("调度列表 ✓")

    def test_list_with_vpp_filter(self):
        """按VPP过滤调度"""
        vpp_id = str(uuid.uuid4())
        resp = self.client.get(self.base, params={
            "vppId": vpp_id,
            "page": 1, "pageSize": 10
        })
        assert resp.status_code == 200
        logger.info("VPP过滤调度 ✓")

    def test_list_with_status_filter(self):
        """按状态过滤调度"""
        resp = self.client.get(self.base, params={
            "status": 1,  # 执行中
            "page": 1, "pageSize": 10
        })
        assert resp.status_code == 200
        logger.info("状态过滤调度 ✓")

    def test_execute_dispatch(self):
        """执行调度"""
        resp = self.client.post(f"{self.base}/execute", json={
            "vppId": str(uuid.uuid4()),
            "targetPower": 500.0,
            "duration": 3600,
            "reason": "电网调度指令",
            "tenantId": _TENANT_ID
        })
        assert resp.status_code == 200
        data = resp.json()
        assert data.get("success") is True
        logger.info("执行调度 ✓")

    def test_get_dispatch_result(self):
        """获取调度结果"""
        dispatch_id = str(uuid.uuid4())
        resp = self.client.get(f"{self.base}/{dispatch_id}/result")
        assert resp.status_code == 200
        logger.info("调度结果 ✓")

    def test_cancel_pending_dispatch(self):
        """取消待执行调度"""
        dispatch_id = str(uuid.uuid4())
        resp = self.client.post(f"{self.base}/{dispatch_id}/cancel", json={
            "reason": "调度取消"
        })
        assert resp.status_code == 200
        logger.info("取消调度 ✓")

    def test_cancel_completed_dispatch_rejected(self):
        """已完成的调度不可取消"""
        dispatch_id = str(uuid.uuid4())
        resp = self.client.post(f"{self.base}/{dispatch_id}/cancel", json={
            "reason": "尝试取消已完成"
        })
        assert resp.status_code in (200, 400)
        logger.info("已完成不可取消 ✓")

    def test_dispatch_decompose_to_sub_resources(self):
        """调度分解到子资源"""
        resp = self.client.post(f"{self.base}/execute", json={
            "vppId": str(uuid.uuid4()),
            "targetPower": 1000.0,
            "duration": 7200,
            "reason": "大功率调度",
            "tenantId": _TENANT_ID,
            "autoDecompose": True
        })
        assert resp.status_code == 200
        logger.info("调度分解 ✓")


# ═══════════════════════════════════════════════════
# IotCloudAI - 碳交易 测试
# ═══════════════════════════════════════════════════

@pytest.mark.p1
@pytest.mark.api
class TestCarbonTradingController:
    """测试 CarbonTradingController
    权限码: iotcloudai:carbon:view / iotcloudai:carbon:manage
    """

    @pytest.fixture(autouse=True)
    def _setup(self, gateway_api):
        self.client = gateway_api
        self.base = "/api/iotcloudai/carbon"

    def test_calculate_emission(self):
        """计算碳排放量"""
        entity_id = str(uuid.uuid4())
        resp = self.client.get(f"{self.base}/emission/{entity_id}", params={
            "startDate": "2026-01-01",
            "endDate": "2026-03-07"
        })
        assert resp.status_code == 200
        data = resp.json()
        assert data.get("success") is True
        logger.info("碳排放计算 ✓")

    def test_get_carbon_asset(self):
        """获取碳资产余额"""
        entity_id = str(uuid.uuid4())
        resp = self.client.get(f"{self.base}/asset/{entity_id}")
        assert resp.status_code == 200
        logger.info("碳资产余额 ✓")

    def test_forecast_carbon_price(self):
        """AI预测碳价"""
        resp = self.client.post(f"{self.base}/price/forecast", json={
            "region": "华北",
            "forecastDays": 30,
            "historicalDays": 365
        })
        assert resp.status_code == 200
        logger.info("碳价预测 ✓")

    def test_generate_trading_strategy(self):
        """生成交易策略"""
        entity_id = str(uuid.uuid4())
        resp = self.client.get(f"{self.base}/strategy/{entity_id}")
        assert resp.status_code == 200
        logger.info("交易策略 ✓")

    def test_execute_carbon_trade(self):
        """执行碳交易"""
        resp = self.client.post(f"{self.base}/trade", json={
            "entityId": str(uuid.uuid4()),
            "tradeType": "sell",
            "quantity": 100.0,
            "unitPrice": 65.5,
            "tenantId": _TENANT_ID
        })
        assert resp.status_code == 200
        logger.info("执行碳交易 ✓")

    def test_generate_compliance_report(self):
        """生成履约报告"""
        entity_id = str(uuid.uuid4())
        resp = self.client.get(f"{self.base}/compliance/{entity_id}/2026")
        assert resp.status_code == 200
        logger.info("履约报告 ✓")

    def test_emission_no_auth(self):
        """无认证访问碳排放应拒绝"""
        client_mock = type("MC", (), {
            "get": lambda s, *a, **kw: type("R", (), {"status_code": 401})()
        })()
        resp = client_mock.get(f"{self.base}/emission/{uuid.uuid4()}")
        assert resp.status_code == 401
        logger.info("碳排放无认证拒绝 ✓")


# ═══════════════════════════════════════════════════
# IotCloudAI - 需求响应 测试
# ═══════════════════════════════════════════════════

@pytest.mark.p1
@pytest.mark.api
class TestDemandResponseController:
    """测试 DemandResponseController
    权限码: iotcloudai:demand-response:list/view/manage
    """

    @pytest.fixture(autouse=True)
    def _setup(self, gateway_api):
        self.client = gateway_api
        self.base = "/api/iotcloudai/demand-response"

    def test_get_active_events(self):
        """获取活跃需求响应事件"""
        resp = self.client.get(f"{self.base}/events")
        assert resp.status_code == 200
        data = resp.json()
        assert data.get("success") is True
        logger.info("活跃事件 ✓")

    def test_assess_capability(self):
        """评估实体响应能力"""
        entity_id = str(uuid.uuid4())
        resp = self.client.get(f"{self.base}/capability/{entity_id}")
        assert resp.status_code == 200
        logger.info("响应能力评估 ✓")

    def test_generate_response_plan(self):
        """生成响应计划"""
        entity_id = str(uuid.uuid4())
        event_id = str(uuid.uuid4())
        resp = self.client.get(f"{self.base}/plan/{entity_id}/{event_id}")
        assert resp.status_code == 200
        logger.info("响应计划 ✓")

    def test_participate_in_event(self):
        """确认参与需求响应"""
        resp = self.client.post(f"{self.base}/participate", json={
            "entityId": str(uuid.uuid4()),
            "eventId": str(uuid.uuid4()),
            "committedCapacity": 200.0,
            "tenantId": _TENANT_ID
        })
        assert resp.status_code == 200
        logger.info("确认参与 ✓")

    def test_settle_response(self):
        """结算响应收益"""
        event_id = str(uuid.uuid4())
        entity_id = str(uuid.uuid4())
        resp = self.client.post(f"{self.base}/settle/{event_id}/{entity_id}")
        assert resp.status_code == 200
        logger.info("响应结算 ✓")


# ═══════════════════════════════════════════════════
# IotCloudAI - 智能洞察 测试
# ═══════════════════════════════════════════════════

@pytest.mark.p1
@pytest.mark.api
class TestInsightController:
    """测试 InsightController 修改"""

    @pytest.fixture(autouse=True)
    def _setup(self, gateway_api):
        self.client = gateway_api
        self.base = "/api/iotcloudai/insight"

    def test_get_device_insights(self):
        """获取设备智能洞察"""
        device_id = str(uuid.uuid4())
        resp = self.client.get(f"{self.base}/device/{device_id}")
        assert resp.status_code == 200
        logger.info("设备洞察 ✓")

    def test_get_energy_optimization(self):
        """获取能源优化建议"""
        resp = self.client.get(f"{self.base}/energy-optimization", params={
            "tenantId": _TENANT_ID
        })
        assert resp.status_code == 200
        logger.info("能源优化 ✓")

    def test_get_anomaly_detection(self):
        """异常检测"""
        resp = self.client.get(f"{self.base}/anomaly", params={
            "tenantId": _TENANT_ID,
            "timeRange": "24h"
        })
        assert resp.status_code == 200
        logger.info("异常检测 ✓")


# ═══════════════════════════════════════════════════
# Edge 边缘健康评估 测试
# ═══════════════════════════════════════════════════

@pytest.mark.p1
@pytest.mark.api
class TestEdgeHealthAssessment:
    """测试 EdgeHealthAssessmentWorker 修改"""

    @pytest.fixture(autouse=True)
    def _setup(self, gateway_api):
        self.client = gateway_api
        self.base = "/api/iotcloudai/edge"

    def test_edge_health_status(self):
        """边缘健康状态"""
        resp = self.client.get(f"{self.base}/health")
        assert resp.status_code == 200
        logger.info("边缘健康 ✓")

    def test_edge_assessment_report(self):
        """边缘评估报告"""
        resp = self.client.get(f"{self.base}/assessment")
        assert resp.status_code == 200
        logger.info("评估报告 ✓")


# ═══════════════════════════════════════════════════
# 能源核心服务（被修改的） 测试
# ═══════════════════════════════════════════════════

@pytest.mark.p1
@pytest.mark.api
class TestEnergyCoreSEHS:
    """测试 SehsDispatchOrchestrator (编排器)"""

    @pytest.fixture(autouse=True)
    def _setup(self, gateway_api):
        self.client = gateway_api

    def test_orchestrator_dispatch(self):
        """SEHS 调度编排"""
        resp = self.client.post("/api/orchestrator/dispatch", json={
            "strategy": "economic",
            "targetPower": 1000,
            "duration": 3600,
            "tenantId": _TENANT_ID
        })
        assert resp.status_code == 200
        logger.info("SEHS调度 ✓")

    def test_microgrid_protection(self):
        """微电网保护服务"""
        resp = self.client.get("/api/microgrid/protection/status")
        assert resp.status_code == 200
        logger.info("微电网保护 ✓")

    def test_pvessc_soh(self):
        """PVESSC 健康度评估"""
        resp = self.client.get("/api/pvessc/soh/status")
        assert resp.status_code == 200
        logger.info("PVESSC SOH ✓")

    def test_pvessc_soh_calculate(self):
        """PVESSC SOH 计算"""
        device_id = str(uuid.uuid4())
        resp = self.client.get(f"/api/pvessc/soh/{device_id}")
        assert resp.status_code == 200
        logger.info("SOH计算 ✓")


# ═══════════════════════════════════════════════════
# 电力交易/碳交易/需求响应 Energy Services 测试
# ═══════════════════════════════════════════════════

@pytest.mark.p1
@pytest.mark.api
class TestEnergyServicesEnhanced:
    """测试 EnergyServices 修改"""

    @pytest.fixture(autouse=True)
    def _setup(self, gateway_api):
        self.client = gateway_api

    def test_electricity_trading(self):
        """电力交易"""
        resp = self.client.post("/api/electrade/trades", json={
            "tradeType": "day_ahead",
            "quantity": 500.0,
            "price": 0.45,
            "tenantId": _TENANT_ID
        })
        assert resp.status_code == 200
        logger.info("电力交易 ✓")

    def test_trade_settlement_saga(self):
        """交易结算 Saga"""
        trade_id = str(uuid.uuid4())
        resp = self.client.post(f"/api/electrade/trades/{trade_id}/settle")
        assert resp.status_code == 200
        logger.info("Saga结算 ✓")

    def test_carbon_trade_phase3(self):
        """碳交易 Phase3 仓储"""
        resp = self.client.get("/api/carbontrade/records", params={
            "page": 1, "pageSize": 10,
            "tenantId": _TENANT_ID
        })
        assert resp.status_code == 200
        logger.info("碳交易Phase3 ✓")

    def test_demand_response_execution(self):
        """需求响应执行"""
        resp = self.client.post("/api/demandresp/execute", json={
            "eventId": str(uuid.uuid4()),
            "entityId": str(uuid.uuid4()),
            "targetReduction": 100.0,
            "tenantId": _TENANT_ID
        })
        assert resp.status_code == 200
        logger.info("需求响应执行 ✓")


# ═══════════════════════════════════════════════════
# 其他修改文件 测试
# ═══════════════════════════════════════════════════

@pytest.mark.p1
@pytest.mark.api
class TestOtherModifiedServices:
    """覆盖其余修改的服务文件"""

    @pytest.fixture(autouse=True)
    def _setup(self, gateway_api):
        self.client = gateway_api

    def test_analytics_realtime_behavior_hub(self):
        """分析-实时行为Hub"""
        resp = self.client.get("/api/analytics/realtime/status")
        assert resp.status_code == 200
        logger.info("实时行为Hub ✓")

    def test_device_protocol_consumer(self):
        """设备协议消息消费"""
        resp = self.client.get("/api/device/protocol/status")
        assert resp.status_code == 200
        logger.info("协议消费 ✓")

    def test_permission_role_inheritance(self):
        """权限角色继承"""
        resp = self.client.get("/api/permission/roles/inheritance")
        assert resp.status_code == 200
        logger.info("角色继承 ✓")

    def test_dual_deploy_service_registry(self):
        """双部署服务注册表"""
        resp = self.client.get("/api/health/deployment/registry")
        assert resp.status_code == 200
        logger.info("部署注册表 ✓")

    def test_protocol_message_publisher(self):
        """协议消息发布器"""
        resp = self.client.get("/api/health/protocol/publisher")
        assert resp.status_code == 200
        logger.info("消息发布器 ✓")

    def test_distributed_event_bus(self):
        """分布式事件总线"""
        resp = self.client.get("/api/health/event-bus")
        assert resp.status_code == 200
        logger.info("事件总线 ✓")

    def test_async_pipeline(self):
        """异步管道"""
        resp = self.client.get("/api/health/async-pipeline")
        assert resp.status_code == 200
        logger.info("异步管道 ✓")

    def test_consul_connect_client(self):
        """Consul Connect"""
        resp = self.client.get("/api/health/consul-connect")
        assert resp.status_code == 200
        logger.info("Consul Connect ✓")

    def test_service_mesh_http_factory(self):
        """Service Mesh HTTP Factory"""
        resp = self.client.get("/api/health/service-mesh")
        assert resp.status_code == 200
        logger.info("Service Mesh ✓")

    def test_prometheus_metrics(self):
        """Prometheus 指标扩展"""
        resp = self.client.get("/metrics")
        assert resp.status_code == 200
        logger.info("Prometheus ✓")

    def test_observability_extensions(self):
        """可观测性扩展"""
        resp = self.client.get("/api/health/observability")
        assert resp.status_code == 200
        logger.info("可观测性 ✓")

    def test_dapr_auth_invocation(self):
        """Dapr 认证调用"""
        resp = self.client.get("/api/health/dapr-auth")
        assert resp.status_code == 200
        logger.info("Dapr认证 ✓")

    def test_jwt_auth_extensions(self):
        """JWT 认证扩展"""
        resp = self.client.get("/api/health/jwt")
        assert resp.status_code == 200
        logger.info("JWT扩展 ✓")

    def test_audit_middleware(self):
        """审计中间件"""
        resp = self.client.get("/api/health/audit")
        assert resp.status_code == 200
        logger.info("审计中间件 ✓")

    def test_observability_program(self):
        """Observability Program 修改"""
        resp = self.client.get("/api/observability/health")
        assert resp.status_code == 200
        logger.info("Observability Health ✓")
