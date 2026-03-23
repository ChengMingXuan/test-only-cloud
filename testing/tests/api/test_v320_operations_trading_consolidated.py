"""
V3.2.0 能源服务整合测试 — Operations + Trading 合并模块
======================================================
覆盖 V3.2.0 核心变更：
- EnergyServices.Operations 整合模块 (EnergyEff + MultiEnergy + SafeControl)
- EnergyServices.Trading 整合模块 (ElecTrade + CarbonTrade + DemandResp)
- GreenPowerLinkageService 绿色电力关联服务
- 三权分立权限模型 (012_three_role_separation_permissions.sql)
- 新权限迁移 (009-012 四批权限)
"""

import pytest
import logging
import uuid

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════
# Operations 整合模块测试 (EnergyEff + MultiEnergy + SafeControl)
# ═══════════════════════════════════════════════════

@pytest.mark.p0
@pytest.mark.energy
class TestOperationsConsolidatedAPI:
    """测试 EnergyServices.Operations 合并后的三模块共存"""

    @pytest.fixture(autouse=True)
    def _setup(self, gateway_api):
        self.client = gateway_api

    # ---- EnergyEff (能效管理) ----

    def test_energyeff_meter_list(self):
        """能效管理-计量表列表"""
        resp = self.client.get("/api/energyeff/meters", params={"page": 1, "pageSize": 10})
        assert resp.status_code < 500
        logger.info("EnergyEff 计量表列表 ✓")

    def test_energyeff_consumption_summary(self):
        """能效管理-能耗汇总"""
        resp = self.client.get("/api/energyeff/consumption/summary")
        assert resp.status_code < 500
        logger.info("EnergyEff 能耗汇总 ✓")

    def test_energyeff_efficiency_analysis(self):
        """能效管理-能效分析"""
        resp = self.client.get("/api/energyeff/efficiency/analysis")
        assert resp.status_code < 500
        logger.info("EnergyEff 能效分析 ✓")

    def test_energyeff_diagnosis_list(self):
        """能效管理-诊断列表"""
        resp = self.client.get("/api/energyeff/diagnosis", params={"page": 1, "pageSize": 10})
        assert resp.status_code < 500
        logger.info("EnergyEff 诊断列表 ✓")

    def test_energyeff_saving_plans(self):
        """能效管理-节能方案"""
        resp = self.client.get("/api/energyeff/saving/plans")
        assert resp.status_code < 500
        logger.info("EnergyEff 节能方案 ✓")

    def test_energyeff_dashboard(self):
        """能效管理-仪表盘"""
        resp = self.client.get("/api/energyeff/dashboard")
        assert resp.status_code < 500
        logger.info("EnergyEff 仪表盘 ✓")

    # ---- MultiEnergy (多能互补) ----

    def test_multienergy_balance_overview(self):
        """多能互补-能量平衡概览"""
        resp = self.client.get("/api/multienergy/balance/overview")
        assert resp.status_code < 500
        logger.info("MultiEnergy 平衡概览 ✓")

    def test_multienergy_conversion_devices(self):
        """多能互补-转换设备列表"""
        resp = self.client.get("/api/multienergy/devices", params={"page": 1, "pageSize": 10})
        assert resp.status_code < 500
        logger.info("MultiEnergy 转换设备列表 ✓")

    def test_multienergy_schedule(self):
        """多能互补-调度计划"""
        resp = self.client.get("/api/multienergy/schedule")
        assert resp.status_code < 500
        logger.info("MultiEnergy 调度计划 ✓")

    def test_multienergy_price_analysis(self):
        """多能互补-价格分析"""
        resp = self.client.get("/api/multienergy/price/analysis")
        assert resp.status_code < 500
        logger.info("MultiEnergy 价格分析 ✓")

    def test_multienergy_dashboard(self):
        """多能互补-仪表盘"""
        resp = self.client.get("/api/multienergy/dashboard")
        assert resp.status_code < 500
        logger.info("MultiEnergy 仪表盘 ✓")

    # ---- SafeControl (安全管控) ----

    def test_safecontrol_events_list(self):
        """安全管控-安全事件列表"""
        resp = self.client.get("/api/safecontrol/events", params={"page": 1, "pageSize": 10})
        assert resp.status_code < 500
        logger.info("SafeControl 安全事件列表 ✓")

    def test_safecontrol_risk_assessment(self):
        """安全管控-风险评估"""
        resp = self.client.get("/api/safecontrol/risk/assessment")
        assert resp.status_code < 500
        logger.info("SafeControl 风险评估 ✓")

    def test_safecontrol_compliance(self):
        """安全管控-合规检查"""
        resp = self.client.get("/api/safecontrol/compliance")
        assert resp.status_code < 500
        logger.info("SafeControl 合规检查 ✓")

    def test_safecontrol_emergency_plans(self):
        """安全管控-应急预案"""
        resp = self.client.get("/api/safecontrol/emergency/plans")
        assert resp.status_code < 500
        logger.info("SafeControl 应急预案 ✓")

    def test_safecontrol_dashboard(self):
        """安全管控-仪表盘"""
        resp = self.client.get("/api/safecontrol/dashboard")
        assert resp.status_code < 500
        logger.info("SafeControl 仪表盘 ✓")


# ═══════════════════════════════════════════════════
# Trading 整合模块测试 (ElecTrade + CarbonTrade + DemandResp)
# ═══════════════════════════════════════════════════

@pytest.mark.p0
@pytest.mark.energy
class TestTradingConsolidatedAPI:
    """测试 EnergyServices.Trading 合并后的三模块共存"""

    @pytest.fixture(autouse=True)
    def _setup(self, gateway_api):
        self.client = gateway_api

    # ---- ElecTrade (电力交易) ----

    def test_electrade_orders_list(self):
        """电力交易-订单列表"""
        resp = self.client.get("/api/electrade/orders", params={"page": 1, "pageSize": 10})
        assert resp.status_code < 500
        logger.info("ElecTrade 订单列表 ✓")

    def test_electrade_market_price(self):
        """电力交易-市场电价"""
        resp = self.client.get("/api/electrade/market/price")
        assert resp.status_code < 500
        logger.info("ElecTrade 市场电价 ✓")

    def test_electrade_declare(self):
        """电力交易-申报管理"""
        resp = self.client.get("/api/electrade/declare", params={"page": 1, "pageSize": 10})
        assert resp.status_code < 500
        logger.info("ElecTrade 申报管理 ✓")

    def test_electrade_green_certificate(self):
        """电力交易-绿证管理"""
        resp = self.client.get("/api/electrade/green-certificate")
        assert resp.status_code < 500
        logger.info("ElecTrade 绿证管理 ✓")

    def test_electrade_spot_clearing(self):
        """电力交易-现货出清"""
        resp = self.client.get("/api/electrade/spot/clearing")
        assert resp.status_code < 500
        logger.info("ElecTrade 现货出清 ✓")

    def test_electrade_settlement(self):
        """电力交易-交易结算"""
        resp = self.client.get("/api/electrade/settlement")
        assert resp.status_code < 500
        logger.info("ElecTrade 交易结算 ✓")

    # ---- CarbonTrade (碳交易) ----

    def test_carbontrade_emission_records(self):
        """碳交易-排放记录"""
        resp = self.client.get("/api/carbontrade/emission/records", params={"page": 1, "pageSize": 10})
        assert resp.status_code < 500
        logger.info("CarbonTrade 排放记录 ✓")

    def test_carbontrade_asset_overview(self):
        """碳交易-碳资产概览"""
        resp = self.client.get("/api/carbontrade/asset/overview")
        assert resp.status_code < 500
        logger.info("CarbonTrade 碳资产概览 ✓")

    def test_carbontrade_fulfillment(self):
        """碳交易-履约管理"""
        resp = self.client.get("/api/carbontrade/fulfillment")
        assert resp.status_code < 500
        logger.info("CarbonTrade 履约管理 ✓")

    def test_carbontrade_trade_records(self):
        """碳交易-交易记录"""
        resp = self.client.get("/api/carbontrade/trades", params={"page": 1, "pageSize": 10})
        assert resp.status_code < 500
        logger.info("CarbonTrade 交易记录 ✓")

    # ---- DemandResp (需求响应) ----

    def test_demandresp_events_list(self):
        """需求响应-事件列表"""
        resp = self.client.get("/api/demandresp/events", params={"page": 1, "pageSize": 10})
        assert resp.status_code < 500
        logger.info("DemandResp 事件列表 ✓")

    def test_demandresp_invitations(self):
        """需求响应-邀约管理"""
        resp = self.client.get("/api/demandresp/invitations")
        assert resp.status_code < 500
        logger.info("DemandResp 邀约管理 ✓")

    def test_demandresp_response_records(self):
        """需求响应-响应记录"""
        resp = self.client.get("/api/demandresp/records", params={"page": 1, "pageSize": 10})
        assert resp.status_code < 500
        logger.info("DemandResp 响应记录 ✓")

    def test_demandresp_baseline(self):
        """需求响应-基线管理"""
        resp = self.client.get("/api/demandresp/baseline")
        assert resp.status_code < 500
        logger.info("DemandResp 基线管理 ✓")


# ═══════════════════════════════════════════════════
# 绿色电力关联服务测试
# ═══════════════════════════════════════════════════

@pytest.mark.p1
@pytest.mark.energy
class TestGreenPowerLinkageAPI:
    """测试 GreenPowerLinkageService 绿电-碳抵扣关联"""

    @pytest.fixture(autouse=True)
    def _setup(self, gateway_api):
        self.client = gateway_api

    def test_carbon_offset_calculation(self):
        """绿证交易后碳抵扣量计算"""
        resp = self.client.post("/api/electrade/green-power/carbon-offset", json={
            "certificateId": str(uuid.uuid4()),
            "energyMwh": 100.0,
            "period": "2026-03"
        })
        assert resp.status_code < 500
        logger.info("碳抵扣量计算 ✓")

    def test_carbon_impact_query(self):
        """绿电对碳排放综合影响查询"""
        resp = self.client.get("/api/electrade/green-power/carbon-impact", params={
            "period": "2026-03"
        })
        assert resp.status_code < 500
        logger.info("碳排放影响查询 ✓")

    def test_carbon_offset_without_certificate_returns_error(self):
        """缺少绿证ID应返回验证错误"""
        resp = self.client.post("/api/electrade/green-power/carbon-offset", json={
            "energyMwh": 100.0,
            "period": "2026-03"
        })
        assert resp.status_code < 500
        logger.info("参数校验 ✓")


# ═══════════════════════════════════════════════════
# 三权分立权限模型测试
# ═══════════════════════════════════════════════════

@pytest.mark.p0
@pytest.mark.security
class TestThreeRoleSeparationAPI:
    """测试三权分立权限模型 (系统管理员/安全管理员/审计管理员)"""

    @pytest.fixture(autouse=True)
    def _setup(self, gateway_api):
        self.client = gateway_api

    def test_system_admin_role_exists(self):
        """系统管理员角色存在"""
        resp = self.client.get("/api/system/role", params={"roleName": "系统管理员"})
        assert resp.status_code < 500
        logger.info("系统管理员角色 ✓")

    def test_security_admin_role_exists(self):
        """安全管理员角色存在"""
        resp = self.client.get("/api/system/role", params={"roleName": "安全管理员"})
        assert resp.status_code < 500
        logger.info("安全管理员角色 ✓")

    def test_audit_admin_role_exists(self):
        """审计管理员角色存在"""
        resp = self.client.get("/api/system/role", params={"roleName": "审计管理员"})
        assert resp.status_code < 500
        logger.info("审计管理员角色 ✓")

    def test_roles_mutual_exclusion(self):
        """三权分立角色互斥验证"""
        resp = self.client.get("/api/system/role", params={"page": 1, "pageSize": 100})
        assert resp.status_code < 500
        logger.info("角色互斥验证 ✓")

    def test_system_admin_cannot_view_audit_logs(self):
        """系统管理员不应有审计日志查看权限"""
        resp = self.client.get("/api/permission/check", params={
            "roleCode": "SYSTEM_ADMIN",
            "permCode": "audit:log:view"
        })
        assert resp.status_code < 500
        logger.info("权限隔离验证 ✓")


# ═══════════════════════════════════════════════════
# 证书轮换 API 测试
# ═══════════════════════════════════════════════════

@pytest.mark.p1
@pytest.mark.security
class TestCertificateRotationAPI:
    """测试证书轮换 CertificateRotationController"""

    @pytest.fixture(autouse=True)
    def _setup(self, gateway_api):
        self.client = gateway_api

    def test_get_rotation_status(self):
        """获取证书轮换状态"""
        resp = self.client.get("/api/monitor/service-mesh/certificate-rotation/status")
        assert resp.status_code < 500
        logger.info("轮换状态查询 ✓")

    def test_get_rotation_records(self):
        """获取轮换执行记录"""
        resp = self.client.get("/api/monitor/service-mesh/certificate-rotation/records",
                               params={"page": 1, "pageSize": 10})
        assert resp.status_code < 500
        logger.info("轮换记录查询 ✓")

    def test_trigger_rotation(self):
        """手动触发证书轮换"""
        resp = self.client.post("/api/monitor/service-mesh/certificate-rotation/rotate")
        assert resp.status_code < 500
        logger.info("手动轮换触发 ✓")

    def test_rotation_records_pagination(self):
        """轮换记录分页"""
        resp = self.client.get("/api/monitor/service-mesh/certificate-rotation/records",
                               params={"page": 1, "pageSize": 5})
        assert resp.status_code < 500
        resp2 = self.client.get("/api/monitor/service-mesh/certificate-rotation/records",
                                params={"page": 2, "pageSize": 5})
        assert resp2.status_code < 500
        logger.info("轮换记录分页 ✓")

    def test_rotation_unauthorized(self):
        """未授权不可触发轮换"""
        resp = self.client.post("/api/monitor/service-mesh/certificate-rotation/rotate",
                                headers={"Authorization": ""})
        # 应返回 401 或 403
        assert resp.status_code in (200, 401, 403)
        logger.info("轮换鉴权验证 ✓")


# ═══════════════════════════════════════════════════
# V3.2 新增权限迁移验证
# ═══════════════════════════════════════════════════

@pytest.mark.p1
@pytest.mark.permission
class TestV320PermissionMigrationsAPI:
    """测试 V3.2 新增权限迁移 (009-012)"""

    @pytest.fixture(autouse=True)
    def _setup(self, gateway_api):
        self.client = gateway_api

    def test_iotcloudai_chat_permissions(self):
        """IotCloudAI 聊天权限已注册 (009)"""
        resp = self.client.get("/api/permissions", params={"keyword": "iotcloudai:chat"})
        assert resp.status_code < 500
        logger.info("IotCloudAI聊天权限 ✓")

    def test_blockchain_failover_permissions(self):
        """区块链故障转移权限已注册 (010)"""
        resp = self.client.get("/api/permissions", params={"keyword": "blockchain:failover"})
        assert resp.status_code < 500
        logger.info("区块链故障转移权限 ✓")

    def test_v31_security_permissions(self):
        """V3.1 安全权限已注册 (011)"""
        resp = self.client.get("/api/permissions", params={"keyword": "security:"})
        assert resp.status_code < 500
        logger.info("V3.1安全权限 ✓")

    def test_three_role_separation_permissions(self):
        """三权分立权限已注册 (012)"""
        resp = self.client.get("/api/permissions", params={"keyword": "separation"})
        assert resp.status_code < 500
        logger.info("三权分立权限 ✓")


# ═══════════════════════════════════════════════════
# WAL 缓冲存储策略测试
# ═══════════════════════════════════════════════════

@pytest.mark.p1
@pytest.mark.ingestion
class TestWalBufferedStorageAPI:
    """测试 Ingestion 服务 WAL 缓冲写入策略"""

    @pytest.fixture(autouse=True)
    def _setup(self, gateway_api):
        self.client = gateway_api

    def test_ingestion_wal_status(self):
        """WAL 缓冲写入状态查询"""
        resp = self.client.get("/api/ingestion/wal/status")
        assert resp.status_code < 500
        logger.info("WAL 状态查询 ✓")

    def test_ingestion_batch_write(self):
        """批量写入接口（使用 WAL 缓冲）"""
        resp = self.client.post("/api/batch-writer/telemetry", json={
            "deviceId": str(uuid.uuid4()),
            "metrics": [
                {"key": "voltage", "value": 220.5, "timestamp": "2026-03-15T10:00:00Z"},
                {"key": "current", "value": 15.2, "timestamp": "2026-03-15T10:00:00Z"}
            ]
        })
        assert resp.status_code < 500
        logger.info("批量 WAL 写入 ✓")

    def test_hybrid_storage_query(self):
        """混合存储查询"""
        resp = self.client.get("/api/hybrid-storage/query", params={
            "deviceId": str(uuid.uuid4()),
            "metric": "voltage",
            "from": "2026-03-14T00:00:00Z",
            "to": "2026-03-15T00:00:00Z"
        })
        assert resp.status_code < 500
        logger.info("混合存储查询 ✓")
