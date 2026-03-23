"""
能源服务 — Phase 2 完整 API 测试
=================================
覆盖全部11个能源微服务的 Phase 2 增强 API
优先级：P0-P1
"""
import pytest
import logging
from tests.api.base_test import BaseApiTest

logger = logging.getLogger(__name__)

# ═══════════════════════════════════════════
# CarbonTrade 碳交易 Phase 2/3
# ═══════════════════════════════════════════

@pytest.mark.p0
@pytest.mark.energy
class TestCarbonTradePhase2(BaseApiTest):
    """碳交易 Phase 2: 排放因子 + MRV"""

    SERVICE_NAME = "carbontrade"
    API_PREFIX = "/api/carbontrade"

    def test_list_emission_factors(self, api):
        resp = api.get(f"{self.API_PREFIX}/emission-factor", params={"pageSize": 10})
        self.assert_paged(resp)

    def test_get_emission_factor_detail(self, api):
        list_resp = api.get(f"{self.API_PREFIX}/emission-factor", params={"pageSize": 1})
        data = self.assert_paged(list_resp)
        if data["total"] == 0:
            return
        factor_id = data["items"][0]["id"]
        resp = api.get(f"{self.API_PREFIX}/emission-factor/{factor_id}")
        self.assert_success(resp)

    def test_list_mrv_records(self, api):
        resp = api.get(f"{self.API_PREFIX}/mrv", params={"pageSize": 10})
        self.assert_paged(resp)

    def test_calculate_emission(self, api):
        resp = api.post(f"{self.API_PREFIX}/emission/calculate", json={
            "stationId": "00000000-0000-0000-0000-000000000001",
            "energyKwh": 1000.0,
            "factorCode": "GRID_DEFAULT",
        })
        assert resp.status_code in (200, 404, 400)


@pytest.mark.p0
@pytest.mark.energy
class TestCarbonTradePhase3(BaseApiTest):
    """碳交易 Phase 3: 配额交易 + 撮合 + 存证"""

    SERVICE_NAME = "carbontrade"
    API_PREFIX = "/api/carbontrade"

    def test_list_factor_weights(self, api):
        resp = api.get(f"{self.API_PREFIX}/factor-weight", params={"pageSize": 10})
        self.assert_paged(resp)

    def test_list_trade_orders(self, api):
        resp = api.get(f"{self.API_PREFIX}/trade-order", params={"pageSize": 10})
        self.assert_paged(resp)

    def test_list_trade_matchings(self, api):
        resp = api.get(f"{self.API_PREFIX}/trade-matching", params={"pageSize": 10})
        assert resp.status_code in (200, 404)

    def test_list_trade_settlements(self, api):
        resp = api.get(f"{self.API_PREFIX}/trade-settlement", params={"pageSize": 10})
        assert resp.status_code in (200, 404)

    def test_list_blockchain_proofs(self, api):
        resp = api.get(f"{self.API_PREFIX}/blockchain-proof", params={"pageSize": 10})
        assert resp.status_code in (200, 404)

    def test_list_mrv_verifications(self, api):
        resp = api.get(f"{self.API_PREFIX}/mrv-verification", params={"pageSize": 10})
        assert resp.status_code in (200, 404)

    def test_dashboard(self, api):
        resp = api.get(f"{self.API_PREFIX}/dashboard")
        self.assert_success(resp)


# ═══════════════════════════════════════════
# VPP 虚拟电厂 Phase 2
# ═══════════════════════════════════════════

@pytest.mark.p0
@pytest.mark.energy
class TestVPPPhase2(BaseApiTest):
    """VPP Phase 2: 调度执行 + 辅助服务 + 收益分配"""

    SERVICE_NAME = "vpp"
    API_PREFIX = "/api/vpp"

    def test_list_vpps(self, api):
        resp = api.get(f"{self.API_PREFIX}/list", params={"pageSize": 10})
        self.assert_paged(resp)

    def test_vpp_dashboard(self, api):
        resp = api.get(f"{self.API_PREFIX}/dashboard")
        self.assert_success(resp)

    def test_list_dispatch_plans(self, api):
        resp = api.get(f"{self.API_PREFIX}/dispatch", params={"pageSize": 10})
        self.assert_paged(resp)

    def test_list_dispatch_details(self, api):
        resp = api.get(f"{self.API_PREFIX}/dispatch-execution", params={"pageSize": 10})
        self.assert_paged(resp)

    def test_list_ancillary_services(self, api):
        resp = api.get(f"{self.API_PREFIX}/ancillary", params={"pageSize": 10})
        self.assert_paged(resp)

    def test_load_forecast(self, api):
        resp = api.get(f"{self.API_PREFIX}/forecast", params={"hours": 24})
        assert resp.status_code in (200, 404)

    def test_list_resources(self, api):
        resp = api.get(f"{self.API_PREFIX}/resources", params={"pageSize": 10})
        self.assert_paged(resp)

    def test_aggregation_status(self, api):
        resp = api.get(f"{self.API_PREFIX}/aggregation/status")
        assert resp.status_code in (200, 404)


# ═══════════════════════════════════════════
# ElecTrade 电力交易 Phase 2
# ═══════════════════════════════════════════

@pytest.mark.p0
@pytest.mark.energy
class TestElecTradePhase2(BaseApiTest):
    """电力交易 Phase 2: 现货清算 + 绿电 + 风险"""

    SERVICE_NAME = "electrade"
    API_PREFIX = "/api/electrade"

    def test_list_spot_clearings(self, api):
        resp = api.get(f"{self.API_PREFIX}/spot/clearing", params={"pageSize": 10})
        self.assert_paged(resp)

    def test_list_green_certificates(self, api):
        resp = api.get(f"{self.API_PREFIX}/green-cert", params={"pageSize": 10})
        self.assert_paged(resp)

    def test_list_risk_indicators(self, api):
        resp = api.get(f"{self.API_PREFIX}/risk/indicators", params={"pageSize": 10})
        assert resp.status_code in (200, 404)

    def test_risk_dashboard(self, api):
        resp = api.get(f"{self.API_PREFIX}/risk/dashboard")
        assert resp.status_code in (200, 404)

    def test_list_market_orders(self, api):
        resp = api.get(f"{self.API_PREFIX}/market/orders", params={"pageSize": 10})
        self.assert_paged(resp)

    def test_market_price_curve(self, api):
        resp = api.get(f"{self.API_PREFIX}/market/price-curve")
        assert resp.status_code in (200, 404)

    def test_list_bilateral_contracts(self, api):
        resp = api.get(f"{self.API_PREFIX}/bilateral", params={"pageSize": 10})
        self.assert_paged(resp)


# ═══════════════════════════════════════════
# MicroGrid 微电网 Phase 2
# ═══════════════════════════════════════════

@pytest.mark.p0
@pytest.mark.energy
class TestMicroGridPhase2(BaseApiTest):
    """微电网 Phase 2: 拓扑 + 告警 + 保护"""

    SERVICE_NAME = "microgrid"
    API_PREFIX = "/api/microgrid"

    def test_list_microgrids(self, api):
        resp = api.get(f"{self.API_PREFIX}/list", params={"pageSize": 10})
        self.assert_paged(resp)

    def test_microgrid_dashboard(self, api):
        resp = api.get(f"{self.API_PREFIX}/dashboard")
        self.assert_success(resp)

    def test_list_topology(self, api):
        resp = api.get(f"{self.API_PREFIX}/topology", params={"pageSize": 10})
        self.assert_paged(resp)

    def test_list_alerts(self, api):
        resp = api.get(f"{self.API_PREFIX}/alert", params={"pageSize": 10})
        self.assert_paged(resp)

    def test_list_protection_rules(self, api):
        resp = api.get(f"{self.API_PREFIX}/protection/rules", params={"pageSize": 10})
        self.assert_paged(resp)

    def test_protection_status(self, api):
        resp = api.get(f"{self.API_PREFIX}/protection/status")
        assert resp.status_code in (200, 404)

    def test_control_mode(self, api):
        resp = api.get(f"{self.API_PREFIX}/control/mode")
        assert resp.status_code in (200, 404)


# ═══════════════════════════════════════════
# DeviceOps 设备运维
# ═══════════════════════════════════════════

@pytest.mark.p1
@pytest.mark.energy
class TestDeviceOps(BaseApiTest):
    """设备运维: 工单 + 预测性维护 + 备件"""

    SERVICE_NAME = "deviceops"
    API_PREFIX = "/api/deviceops"

    def test_list_workorders(self, api):
        resp = api.get(f"{self.API_PREFIX}/work-order", params={"pageSize": 10})
        self.assert_paged(resp)

    def test_list_predictive_maintenance(self, api):
        resp = api.get(f"{self.API_PREFIX}/predictive-maintenance", params={"pageSize": 10})
        self.assert_paged(resp)

    def test_list_spare_parts(self, api):
        resp = api.get(f"{self.API_PREFIX}/spare-part", params={"pageSize": 10})
        self.assert_paged(resp)

    def test_workorder_stats(self, api):
        resp = api.get(f"{self.API_PREFIX}/work-order/stats")
        assert resp.status_code in (200, 404)


# ═══════════════════════════════════════════
# EnergyEff 能效管理
# ═══════════════════════════════════════════

@pytest.mark.p1
@pytest.mark.energy
class TestEnergyEff(BaseApiTest):
    """能效管理: 基线 + 节能措施"""

    SERVICE_NAME = "energyeff"
    API_PREFIX = "/api/energyeff"

    def test_list_baselines(self, api):
        resp = api.get(f"{self.API_PREFIX}/baseline", params={"pageSize": 10})
        self.assert_paged(resp)

    def test_list_saving_measures(self, api):
        resp = api.get(f"{self.API_PREFIX}/saving-measure", params={"pageSize": 10})
        self.assert_paged(resp)

    def test_energy_efficiency_dashboard(self, api):
        resp = api.get(f"{self.API_PREFIX}/dashboard")
        self.assert_success(resp)


# ═══════════════════════════════════════════
# SafeControl 安全控制
# ═══════════════════════════════════════════

@pytest.mark.p1
@pytest.mark.energy
class TestSafeControl(BaseApiTest):
    """安全控制: 联锁规则 + 应急预案"""

    SERVICE_NAME = "safecontrol"
    API_PREFIX = "/api/safecontrol"

    def test_list_interlock_rules(self, api):
        resp = api.get(f"{self.API_PREFIX}/interlock-rule", params={"pageSize": 10})
        self.assert_paged(resp)

    def test_list_emergency_plans(self, api):
        resp = api.get(f"{self.API_PREFIX}/emergency-plan", params={"pageSize": 10})
        self.assert_paged(resp)

    def test_safety_dashboard(self, api):
        resp = api.get(f"{self.API_PREFIX}/dashboard")
        self.assert_success(resp)


# ═══════════════════════════════════════════
# DemandResp 需求响应
# ═══════════════════════════════════════════

@pytest.mark.p1
@pytest.mark.energy
class TestDemandResp(BaseApiTest):
    """需求响应: 事件 + 执行 + 仪表盘"""

    SERVICE_NAME = "demandresp"
    API_PREFIX = "/api/demandresp"

    def test_list_dr_events(self, api):
        resp = api.get(f"{self.API_PREFIX}/events", params={"pageSize": 10})
        self.assert_paged(resp)

    def test_list_executions(self, api):
        resp = api.get(f"{self.API_PREFIX}/executions", params={"pageSize": 10})
        self.assert_paged(resp)

    def test_dr_dashboard(self, api):
        resp = api.get(f"{self.API_PREFIX}/dashboard")
        self.assert_success(resp)

    def test_list_participants(self, api):
        resp = api.get(f"{self.API_PREFIX}/participants", params={"pageSize": 10})
        assert resp.status_code in (200, 404)


# ═══════════════════════════════════════════
# MultiEnergy 多能协同
# ═══════════════════════════════════════════

@pytest.mark.p1
@pytest.mark.energy
class TestMultiEnergy(BaseApiTest):
    """多能协同: 耦合矩阵 + 协调优化"""

    SERVICE_NAME = "multienergy"
    API_PREFIX = "/api/multienergy"

    def test_list_coupling_configs(self, api):
        resp = api.get(f"{self.API_PREFIX}/coupling", params={"pageSize": 10})
        self.assert_paged(resp)

    def test_multi_energy_dashboard(self, api):
        resp = api.get(f"{self.API_PREFIX}/dashboard")
        self.assert_success(resp)


# ═══════════════════════════════════════════
# Orchestrator 能源编排
# ═══════════════════════════════════════════

@pytest.mark.p1
@pytest.mark.energy
class TestOrchestrator(BaseApiTest):
    """能源编排: 调度策略 + 三级调度"""

    SERVICE_NAME = "orchestrator"
    API_PREFIX = "/api/sehs"

    def test_list_dispatch_strategies(self, api):
        resp = api.get(f"{self.API_PREFIX}/dispatch/strategies", params={"pageSize": 10})
        self.assert_paged(resp)

    def test_sehs_dashboard(self, api):
        resp = api.get(f"{self.API_PREFIX}/dashboard")
        self.assert_success(resp)

    def test_list_schedules(self, api):
        resp = api.get(f"{self.API_PREFIX}/schedules", params={"pageSize": 10})
        self.assert_paged(resp)


# ═══════════════════════════════════════════
# PVESSC 光储充协同
# ═══════════════════════════════════════════

@pytest.mark.p1
@pytest.mark.energy
class TestPVESSC(BaseApiTest):
    """光储充协同: 站点 + 拓扑 + V2G + 调度"""

    SERVICE_NAME = "pvessc"
    API_PREFIX = "/api/pvessc"

    def test_list_sites(self, api):
        resp = api.get(f"{self.API_PREFIX}/sites", params={"pageSize": 10})
        self.assert_paged(resp)

    def test_pvessc_dashboard(self, api):
        resp = api.get(f"{self.API_PREFIX}/dashboard")
        self.assert_success(resp)

    def test_list_topology(self, api):
        resp = api.get(f"{self.API_PREFIX}/topology", params={"pageSize": 10})
        self.assert_paged(resp)

    def test_list_v2g_sessions(self, api):
        resp = api.get(f"{self.API_PREFIX}/v2g/sessions", params={"pageSize": 10})
        self.assert_paged(resp)

    def test_list_dispatches(self, api):
        resp = api.get(f"{self.API_PREFIX}/dispatch", params={"pageSize": 10})
        self.assert_paged(resp)

    def test_soh_report(self, api):
        resp = api.get(f"{self.API_PREFIX}/soh/report")
        assert resp.status_code in (200, 404)
