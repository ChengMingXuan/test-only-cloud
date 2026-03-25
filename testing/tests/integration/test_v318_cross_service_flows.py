"""
v3.18 增量功能 - 跨服务集成测试
================================
测试新增模块的跨服务调用链路和业务流程：
- Carbon认证 → Blockchain存证 → 交易结算
- 智能排队 → 充电调度 → 设备控制
- 能耗统计 → 分析报表 → 告警通知
- CIM调度 → 设备执行 → 偏差监控
- 组串监控 → 异常检测 → 工单创建
- AI预测 → 调度优化 → 执行反馈

共计 15+ 跨服务业务流程
"""
import pytest
import logging
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from datetime import datetime, timedelta
from uuid import uuid4
from typing import List, Dict, Any

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════════════════════════
# Mock 服务客户端
# ═══════════════════════════════════════════════════════════════════════════════

class MockServiceClient:
    """跨服务调用Mock客户端"""
    
    def __init__(self):
        self.call_history: List[Dict[str, Any]] = []
        self.tenant_id = str(uuid4())
        self.user_id = str(uuid4())
    
    async def call_service(self, service: str, endpoint: str, method: str = "GET", data: dict = None):
        """模拟跨服务调用"""
        call_record = {
            "service": service,
            "endpoint": endpoint,
            "method": method,
            "data": data,
            "timestamp": datetime.utcnow().isoformat()
        }
        self.call_history.append(call_record)
        
        # 返回模拟响应
        return {
            "code": 200,
            "data": {"id": str(uuid4()), "status": "success"},
            "message": "OK"
        }
    
    def get_call_count(self, service: str = None) -> int:
        """获取服务调用次数"""
        if service:
            return len([c for c in self.call_history if c["service"] == service])
        return len(self.call_history)
    
    def clear_history(self):
        """清空调用历史"""
        self.call_history = []


@pytest.fixture
def mock_service_client():
    return MockServiceClient()


@pytest.fixture
def sample_ids():
    return {
        "tenant_id": str(uuid4()),
        "user_id": str(uuid4()),
        "device_id": str(uuid4()),
        "station_id": str(uuid4()),
        "grid_id": str(uuid4()),
        "site_id": str(uuid4())
    }


# ═══════════════════════════════════════════════════════════════════════════════
# 1. Carbon认证 → Blockchain存证 → 交易结算 集成流程
# ═══════════════════════════════════════════════════════════════════════════════

class TestCarbonCertificationIntegration:
    """碳认证跨服务集成测试"""
    
    @pytest.mark.asyncio
    async def test_irec_full_lifecycle(self, mock_service_client, sample_ids):
        """测试 I-REC 完整生命周期：注册 → 签发 → 转让 → 注销"""
        # Step 1: 设备注册
        register_response = await mock_service_client.call_service(
            "blockchain", "/api/carbon/irec/register", "POST",
            {"deviceCode": "PV-001", "installedCapacityKw": 500}
        )
        assert register_response["code"] == 200
        device_id = register_response["data"]["id"]
        
        # Step 2: 存证到区块链
        evidence_response = await mock_service_client.call_service(
            "blockchain", "/api/blockchain/evidence", "POST",
            {"dataType": "irec_registration", "dataId": device_id}
        )
        assert evidence_response["code"] == 200
        
        # Step 3: 申请证书签发
        issue_response = await mock_service_client.call_service(
            "blockchain", "/api/carbon/irec/issue", "POST",
            {"deviceId": device_id, "generationMwh": 150}
        )
        assert issue_response["code"] == 200
        certificate_id = issue_response["data"]["id"]
        
        # Step 4: 证书转让
        transfer_response = await mock_service_client.call_service(
            "blockchain", f"/api/carbon/irec/{certificate_id}/transfer", "POST",
            {"toAccountId": str(uuid4())}
        )
        assert transfer_response["code"] == 200
        
        # Step 5: 创建交易结算单
        settlement_response = await mock_service_client.call_service(
            "settlement", "/api/settlement/order", "POST",
            {"orderType": "carbon_trade", "referenceId": certificate_id}
        )
        assert settlement_response["code"] == 200
        
        # 验证调用链路
        assert mock_service_client.get_call_count("blockchain") == 4
        assert mock_service_client.get_call_count("settlement") == 1
    
    @pytest.mark.asyncio
    async def test_ccer_project_to_trade(self, mock_service_client, sample_ids):
        """测试 CCER 项目全流程：注册 → 核证 → 交易"""
        # Step 1: 项目注册
        project_response = await mock_service_client.call_service(
            "blockchain", "/api/carbon/ccer/project", "POST",
            {"projectName": "光伏减排项目", "methodologyId": "CM-001"}
        )
        project_id = project_response["data"]["id"]
        
        # Step 2: 申请碳信用
        credits_response = await mock_service_client.call_service(
            "blockchain", "/api/carbon/ccer/credits", "POST",
            {"projectId": project_id, "claimedReductionTco2": 5000}
        )
        credit_id = credits_response["data"]["id"]
        
        # Step 3: 第三方核证
        verify_response = await mock_service_client.call_service(
            "blockchain", f"/api/carbon/ccer/credits/{credit_id}/verify", "POST",
            {"verifierName": "SGS", "verifiedReductionTco2": 4800}
        )
        
        # Step 4: 碳信用交易
        trade_response = await mock_service_client.call_service(
            "blockchain", f"/api/carbon/ccer/credits/{credit_id}/trade", "POST",
            {"buyerTenantId": str(uuid4()), "pricePerTco2": 58.5}
        )
        
        # Step 5: 生成发票
        invoice_response = await mock_service_client.call_service(
            "settlement", "/api/settlement/invoice", "POST",
            {"orderType": "ccer_trade", "referenceId": credit_id}
        )
        
        assert mock_service_client.get_call_count() == 5


# ═══════════════════════════════════════════════════════════════════════════════
# 2. 智能排队 → 充电调度 → 设备控制 集成流程
# ═══════════════════════════════════════════════════════════════════════════════

class TestOrderlyChargingIntegration:
    """智能排队充电跨服务集成测试"""
    
    @pytest.mark.asyncio
    async def test_enqueue_to_charging_flow(self, mock_service_client, sample_ids):
        """测试 排队请求 → 智能调度 → 设备启动充电"""
        station_id = sample_ids["station_id"]
        
        # Step 1: 提交排队请求
        enqueue_response = await mock_service_client.call_service(
            "charging", "/api/charging/orderly/enqueue", "POST",
            {
                "stationId": station_id,
                "vehicleId": "京A12345",
                "currentSocPercent": 20,
                "targetSocPercent": 80
            }
        )
        queue_id = enqueue_response["data"]["id"]
        
        # Step 2: 执行智能调度
        dispatch_response = await mock_service_client.call_service(
            "charging", f"/api/charging/orderly/{station_id}/dispatch", "POST"
        )
        
        # Step 3: 获取分配的充电桩
        pile_id = str(uuid4())  # 模拟分配结果
        
        # Step 4: 向设备服务发送启动充电指令
        device_response = await mock_service_client.call_service(
            "device", f"/api/device/{pile_id}/command", "POST",
            {"command": "start_charging", "parameters": {"maxPowerKw": 120}}
        )
        
        # Step 5: 创建充电订单
        order_response = await mock_service_client.call_service(
            "charging", "/api/charging/order", "POST",
            {"queueId": queue_id, "pileId": pile_id}
        )
        
        assert mock_service_client.get_call_count("charging") == 3
        assert mock_service_client.get_call_count("device") == 1
    
    @pytest.mark.asyncio
    async def test_low_soc_priority_dispatch(self, mock_service_client, sample_ids):
        """测试 低SOC优先级调度"""
        station_id = sample_ids["station_id"]
        
        # 模拟多个排队请求（不同SOC）
        vehicles = [
            {"vehicleId": "车1", "currentSocPercent": 50},
            {"vehicleId": "车2", "currentSocPercent": 10},  # 低SOC应优先
            {"vehicleId": "车3", "currentSocPercent": 30}
        ]
        
        for v in vehicles:
            await mock_service_client.call_service(
                "charging", "/api/charging/orderly/enqueue", "POST",
                {"stationId": station_id, **v}
            )
        
        # 执行调度
        dispatch_response = await mock_service_client.call_service(
            "charging", f"/api/charging/orderly/{station_id}/dispatch", "POST"
        )
        
        # 查询排队状态（验证优先级）
        queue_response = await mock_service_client.call_service(
            "charging", f"/api/charging/orderly/{station_id}/queue", "GET"
        )
        
        assert mock_service_client.get_call_count("charging") == 5


# ═══════════════════════════════════════════════════════════════════════════════
# 3. 能耗统计 → 分析报表 → 告警通知 集成流程
# ═══════════════════════════════════════════════════════════════════════════════

class TestEnergyReportIntegration:
    """能耗统计报表跨服务集成测试"""
    
    @pytest.mark.asyncio
    async def test_energy_data_to_report(self, mock_service_client, sample_ids):
        """测试 能耗数据采集 → 统计分析 → 报表生成"""
        grid_id = sample_ids["grid_id"]
        
        # Step 1: Ingestion服务推送能耗数据
        for _ in range(24):  # 模拟24小时数据
            await mock_service_client.call_service(
                "microgrid", "/api/microgrid/energy/data", "POST",
                {
                    "gridId": grid_id,
                    "pvGenerationKwh": 150.5,
                    "loadConsumptionKwh": 120.0
                }
            )
        
        # Step 2: 获取日报表
        daily_response = await mock_service_client.call_service(
            "microgrid", f"/api/microgrid/energy/{grid_id}/daily", "GET",
            {"date": "2025-03-18"}
        )
        
        # Step 3: 调用Analytics服务生成分析
        analytics_response = await mock_service_client.call_service(
            "analytics", "/api/analytics/energy/analysis", "POST",
            {"gridId": grid_id, "reportType": "daily"}
        )
        
        # Step 4: 生成PDF报告
        pdf_response = await mock_service_client.call_service(
            "analytics", "/api/analytics/report/export", "POST",
            {"format": "pdf", "reportId": analytics_response["data"]["id"]}
        )
        
        assert mock_service_client.get_call_count("microgrid") == 25
        assert mock_service_client.get_call_count("analytics") == 2
    
    @pytest.mark.asyncio
    async def test_energy_anomaly_to_alert(self, mock_service_client, sample_ids):
        """测试 能耗异常 → 规则引擎 → 告警通知"""
        grid_id = sample_ids["grid_id"]
        
        # Step 1: 记录异常能耗数据
        await mock_service_client.call_service(
            "microgrid", "/api/microgrid/energy/data", "POST",
            {
                "gridId": grid_id,
                "loadConsumptionKwh": 500.0  # 异常高负荷
            }
        )
        
        # Step 2: 触发规则引擎检测
        rule_response = await mock_service_client.call_service(
            "ruleengine", "/api/ruleengine/evaluate", "POST",
            {"dataType": "energy", "gridId": grid_id}
        )
        
        # Step 3: 生成告警
        alert_response = await mock_service_client.call_service(
            "observability", "/api/alerts", "POST",
            {
                "alertType": "energy_anomaly",
                "severity": "warning",
                "source": grid_id
            }
        )
        
        # Step 4: 发送通知
        notification_response = await mock_service_client.call_service(
            "observability", "/api/notifications/send", "POST",
            {"alertId": alert_response["data"]["id"], "channels": ["sms", "email"]}
        )
        
        assert mock_service_client.get_call_count() == 4


# ═══════════════════════════════════════════════════════════════════════════════
# 4. CIM调度 → 设备执行 → 偏差监控 集成流程
# ═══════════════════════════════════════════════════════════════════════════════

class TestCimDispatchIntegration:
    """CIM调度协议跨服务集成测试"""
    
    @pytest.mark.asyncio
    async def test_dispatch_command_flow(self, mock_service_client, sample_ids):
        """测试 省级调度指令 → 设备执行 → 执行反馈"""
        # Step 1: 接收省级调度指令
        dispatch_response = await mock_service_client.call_service(
            "orchestrator", "/api/orchestrator/cim/dispatch/receive", "POST",
            {
                "commandType": "EndDeviceControl",
                "targetDeviceIds": [str(uuid4()) for _ in range(5)],
                "setpointValue": 500.0
            }
        )
        record_id = dispatch_response["data"]["id"]
        
        # Step 2: 向VPP服务下发功率调节
        vpp_response = await mock_service_client.call_service(
            "vpp", "/api/vpp/power/adjust", "POST",
            {"targetPowerKw": 500.0, "dispatchRecordId": record_id}
        )
        
        # Step 3: 向设备发送控制指令
        for device_id in [str(uuid4()) for _ in range(5)]:
            await mock_service_client.call_service(
                "device", f"/api/device/{device_id}/command", "POST",
                {"command": "set_power", "value": 100.0}
            )
        
        # Step 4: 采集执行偏差
        await mock_service_client.call_service(
            "orchestrator", "/api/orchestrator/cim/deviation/sample", "POST",
            {
                "dispatchRecordId": record_id,
                "targetValueKw": 500.0,
                "actualValueKw": 485.5
            }
        )
        
        # Step 5: 生成反馈报文
        feedback_response = await mock_service_client.call_service(
            "orchestrator", f"/api/orchestrator/cim/dispatch/{record_id}/feedback", "GET"
        )
        
        assert mock_service_client.get_call_count("orchestrator") == 3
        assert mock_service_client.get_call_count("device") == 5
    
    @pytest.mark.asyncio
    async def test_deviation_analysis_flow(self, mock_service_client, sample_ids):
        """测试 偏差持续监控 → 偏差分析 → 调优建议"""
        record_id = str(uuid4())
        
        # 模拟持续偏差采样
        for i in range(10):
            await mock_service_client.call_service(
                "orchestrator", "/api/orchestrator/cim/deviation/sample", "POST",
                {
                    "dispatchRecordId": record_id,
                    "targetValueKw": 500.0,
                    "actualValueKw": 500.0 - i * 2  # 模拟逐渐增大的偏差
                }
            )
        
        # 获取偏差分析
        analysis_response = await mock_service_client.call_service(
            "orchestrator", f"/api/orchestrator/cim/deviation/{record_id}/analysis", "GET"
        )
        
        # 调用AI服务获取优化建议
        ai_response = await mock_service_client.call_service(
            "iotcloudai", "/api/iotcloudai/adaptive/predict", "POST",
            {"predictScene": "dispatch_optimization", "referenceId": record_id}
        )
        
        assert mock_service_client.get_call_count("orchestrator") == 11


# ═══════════════════════════════════════════════════════════════════════════════
# 5. 组串监控 → 异常检测 → 工单创建 集成流程
# ═══════════════════════════════════════════════════════════════════════════════

class TestStringMonitorIntegration:
    """光伏组串监控跨服务集成测试"""
    
    @pytest.mark.asyncio
    async def test_anomaly_to_workorder(self, mock_service_client, sample_ids):
        """测试 组串异常 → 告警 → 工单创建"""
        site_id = sample_ids["site_id"]
        
        # Step 1: 执行异常检测
        detect_response = await mock_service_client.call_service(
            "pvessc", f"/api/pvessc/string-monitor/{site_id}/detect", "POST"
        )
        
        # Step 2: 假设检测到热斑异常
        anomaly_id = detect_response["data"]["id"]
        
        # Step 3: 创建告警
        alert_response = await mock_service_client.call_service(
            "observability", "/api/alerts", "POST",
            {
                "alertType": "pv_string_hotspot",
                "severity": "high",
                "source": f"site:{site_id}",
                "anomalyId": anomaly_id
            }
        )
        
        # Step 4: 自动创建维修工单
        workorder_response = await mock_service_client.call_service(
            "workorder", "/api/workorder", "POST",
            {
                "type": "maintenance",
                "category": "pv_string_repair",
                "alertId": alert_response["data"]["id"],
                "siteId": site_id,
                "priority": "high"
            }
        )
        
        # Step 5: 分配备件
        sparepart_response = await mock_service_client.call_service(
            "workorder", "/api/workorder/sparepart/allocate", "POST",
            {
                "workorderId": workorder_response["data"]["id"],
                "partType": "pv_module"
            }
        )
        
        assert mock_service_client.get_call_count("pvessc") == 1
        assert mock_service_client.get_call_count("observability") == 1
        assert mock_service_client.get_call_count("workorder") == 2
    
    @pytest.mark.asyncio
    async def test_telemetry_batch_processing(self, mock_service_client, sample_ids):
        """测试 遥测数据批量处理"""
        site_id = sample_ids["site_id"]
        
        # 模拟多个组串的遥测数据上报
        for string_idx in range(10):
            await mock_service_client.call_service(
                "pvessc", "/api/pvessc/string-monitor/telemetry", "POST",
                {
                    "siteId": site_id,
                    "stringId": f"STRING-{string_idx:02d}",
                    "voltageV": 380.0 + string_idx,
                    "currentA": 8.0,
                    "powerW": 3000.0
                }
            )
        
        # 批量检测
        batch_detect_response = await mock_service_client.call_service(
            "pvessc", f"/api/pvessc/string-monitor/{site_id}/detect", "POST"
        )
        
        assert mock_service_client.get_call_count("pvessc") == 11


# ═══════════════════════════════════════════════════════════════════════════════
# 6. AI预测 → 调度优化 → 执行反馈 集成流程
# ═══════════════════════════════════════════════════════════════════════════════

class TestAiPredictionIntegration:
    """AI预测与调度优化跨服务集成测试"""
    
    @pytest.mark.asyncio
    async def test_adaptive_predict_to_dispatch(self, mock_service_client, sample_ids):
        """测试 自适应预测 → 调度策略 → 执行"""
        # Step 1: 自适应预测光伏发电量
        predict_response = await mock_service_client.call_service(
            "iotcloudai", "/api/iotcloudai/adaptive/predict", "POST",
            {
                "predictScene": "pv_power",
                "forecastHours": 24,
                "targetDeviceId": sample_ids["device_id"]
            }
        )
        
        # Step 2: 基于预测结果，调用调度服务优化储能策略
        schedule_response = await mock_service_client.call_service(
            "orchestrator", "/api/orchestrator/schedule/optimize", "POST",
            {
                "predictionId": predict_response["data"]["id"],
                "optimizationTarget": "self_consumption"
            }
        )
        
        # Step 3: 向储能设备下发调度指令
        battery_response = await mock_service_client.call_service(
            "device", "/api/device/battery/schedule", "POST",
            {"scheduleId": schedule_response["data"]["id"]}
        )
        
        # Step 4: 记录预测准确率反馈
        feedback_response = await mock_service_client.call_service(
            "iotcloudai", "/api/iotcloudai/adaptive/performance", "POST",
            {
                "modelCombination": "lstm+ensemble",
                "predictScene": "pv_power",
                "predicted": [100, 150, 200],
                "actual": [95, 155, 195]
            }
        )
        
        assert mock_service_client.get_call_count("iotcloudai") == 2
    
    @pytest.mark.asyncio
    async def test_agent_multi_step_task(self, mock_service_client, sample_ids):
        """测试 Agent多步骤任务执行"""
        # Step 1: 执行Agent任务
        agent_response = await mock_service_client.call_service(
            "iotcloudai", "/api/iotcloudai/agent/execute", "POST",
            {
                "goal": "分析今日充电站运营数据并生成优化报告",
                "scene": "daily_ops",
                "maxIterations": 10
            }
        )
        
        # Agent内部会调用多个服务（模拟）
        # Step 2: 获取充电站数据
        await mock_service_client.call_service(
            "charging", "/api/charging/statistics/today", "GET"
        )
        
        # Step 3: 获取设备状态
        await mock_service_client.call_service(
            "device", "/api/device/status/summary", "GET"
        )
        
        # Step 4: 调用分析服务
        await mock_service_client.call_service(
            "analytics", "/api/analytics/charging/analysis", "POST"
        )
        
        # Step 5: 生成报告
        await mock_service_client.call_service(
            "analytics", "/api/analytics/report/generate", "POST"
        )
        
        assert mock_service_client.get_call_count() == 5
    
    @pytest.mark.asyncio
    async def test_device_health_to_maintenance(self, mock_service_client, sample_ids):
        """测试 设备健康评估 → 预测性维护"""
        # Step 1: 批量设备健康评估
        health_response = await mock_service_client.call_service(
            "iotcloudai", "/api/iotcloudai/health/assess/batch", "POST",
            {"deviceIds": [f"DEVICE-{i:03d}" for i in range(10)]}
        )
        
        # Step 2: 识别出健康度低的设备
        unhealthy_devices = ["DEVICE-003", "DEVICE-007"]  # 模拟
        
        # Step 3: 为每个不健康设备创建预防性工单
        for device_id in unhealthy_devices:
            await mock_service_client.call_service(
                "workorder", "/api/workorder", "POST",
                {
                    "type": "preventive_maintenance",
                    "deviceId": device_id,
                    "priority": "medium"
                }
            )
        
        # Step 4: 跟踪设备健康趋势
        for device_id in unhealthy_devices:
            await mock_service_client.call_service(
                "iotcloudai", f"/api/iotcloudai/health/trend/{device_id}", "GET"
            )
        
        assert mock_service_client.get_call_count("iotcloudai") == 3
        assert mock_service_client.get_call_count("workorder") == 2


# ═══════════════════════════════════════════════════════════════════════════════
# 7. 第三方大模型 → 意图识别 → Agent路由 集成流程
# ═══════════════════════════════════════════════════════════════════════════════

class TestThirdPartyModelIntegration:
    """第三方大模型集成测试"""
    
    @pytest.mark.asyncio
    async def test_chat_to_agent_routing(self, mock_service_client, sample_ids):
        """测试 用户对话 → 意图识别 → Agent路由执行"""
        # Step 1: 用户通过第三方大模型对话
        chat_response = await mock_service_client.call_service(
            "iotcloudai", "/api/iotcloudai/third-party/chat", "POST",
            {
                "message": "帮我查一下今天A站的充电收入",
                "provider": "ali"
            }
        )
        
        # Step 2: 意图识别（假设识别为：charging_revenue_query）
        intent = "charging_revenue_query"
        
        # Step 3: 路由到对应Agent执行
        agent_response = await mock_service_client.call_service(
            "iotcloudai", "/api/iotcloudai/agent/execute", "POST",
            {
                "goal": "查询A站今日充电收入",
                "scene": "report",
                "intentType": intent
            }
        )
        
        # Step 4: Agent调用Settlement服务获取收入数据
        revenue_response = await mock_service_client.call_service(
            "settlement", "/api/settlement/revenue/daily", "GET",
            {"stationId": sample_ids["station_id"], "date": "2025-03-18"}
        )
        
        assert mock_service_client.get_call_count("iotcloudai") == 2
        assert mock_service_client.get_call_count("settlement") == 1
    
    @pytest.mark.asyncio
    async def test_provider_failover(self, mock_service_client, sample_ids):
        """测试 第三方大模型故障切换"""
        providers = ["ali", "tencent", "baidu"]
        
        # 模拟多次调用，验证故障切换逻辑
        for provider in providers:
            await mock_service_client.call_service(
                "iotcloudai", "/api/iotcloudai/third-party/chat", "POST",
                {"message": "测试", "provider": provider}
            )
        
        # 健康检查
        health_response = await mock_service_client.call_service(
            "iotcloudai", "/api/iotcloudai/third-party/health", "GET"
        )
        
        assert mock_service_client.get_call_count("iotcloudai") == 4


# ═══════════════════════════════════════════════════════════════════════════════
# 8. 综合业务场景测试
# ═══════════════════════════════════════════════════════════════════════════════

class TestComprehensiveBusinessScenarios:
    """综合业务场景测试"""
    
    @pytest.mark.asyncio
    async def test_daily_operations_flow(self, mock_service_client, sample_ids):
        """测试 日常运维完整流程"""
        # 1. 获取今日概览
        await mock_service_client.call_service("analytics", "/api/analytics/dashboard/today", "GET")
        
        # 2. 检查设备健康状态
        await mock_service_client.call_service("iotcloudai", "/api/iotcloudai/health/assess/batch", "POST")
        
        # 3. 获取告警列表
        await mock_service_client.call_service("observability", "/api/alerts/active", "GET")
        
        # 4. 处理工单
        await mock_service_client.call_service("workorder", "/api/workorder/pending", "GET")
        
        # 5. 获取能耗报告
        await mock_service_client.call_service("microgrid", "/api/microgrid/energy/overview", "GET")
        
        # 6. 查看充电统计
        await mock_service_client.call_service("charging", "/api/charging/statistics", "GET")
        
        assert mock_service_client.get_call_count() == 6
    
    @pytest.mark.asyncio
    async def test_emergency_response_flow(self, mock_service_client, sample_ids):
        """测试 紧急响应流程"""
        # 1. 收到紧急调度指令
        await mock_service_client.call_service(
            "orchestrator", "/api/orchestrator/cim/dispatch/receive", "POST",
            {"priority": "urgent", "commandType": "EmergencyShutdown"}
        )
        
        # 2. 广播紧急通知
        await mock_service_client.call_service(
            "observability", "/api/notifications/broadcast", "POST",
            {"type": "emergency", "message": "紧急调度"}
        )
        
        # 3. 设备紧急响应
        await mock_service_client.call_service(
            "device", "/api/device/emergency/execute", "POST"
        )
        
        # 4. 记录操作审计
        await mock_service_client.call_service(
            "observability", "/api/audit/log", "POST",
            {"action": "emergency_dispatch", "result": "success"}
        )
        
        assert mock_service_client.get_call_count() == 4


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
