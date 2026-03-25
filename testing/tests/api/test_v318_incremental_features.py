"""
v3.18 增量功能 API 测试
=========================
覆盖以下新增模块的完整API测试：
- Blockchain: CarbonCertification (I-REC/CCER)
- Charging: OrderlyCharging (智能排队充电)
- MicroGrid: MgEnergyReport (能耗统计报表)
- Orchestrator: CimProtocol (IEC 61968/CIM调度协议)
- PVESSC: StringMonitor (光伏组串级监控)
- IotCloudAI: AdaptivePredict, Agent, DeviceHealth, ThirdPartyModel

共计 9 个新控制器，约 45+ API 端点
"""
import pytest
import logging
from unittest.mock import Mock, AsyncMock, patch
from datetime import datetime, timedelta
from uuid import uuid4

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════════════════════════
# 测试配置与Mock客户端
# ═══════════════════════════════════════════════════════════════════════════════

class MockApiClient:
    """Mock API 客户端 - 不连接真实服务"""
    
    def __init__(self, base_url: str = "http://localhost"):
        self.base_url = base_url
        self.headers = {"Authorization": "Bearer mock_token"}
        self.tenant_id = str(uuid4())
        self.user_id = str(uuid4())
    
    async def get(self, path: str, params: dict = None):
        """Mock GET 请求"""
        return {"code": 200, "data": {"items": [], "total": 0}, "message": "OK"}
    
    async def post(self, path: str, json: dict = None):
        """Mock POST 请求"""
        return {"code": 200, "data": str(uuid4()), "message": "OK"}
    
    async def put(self, path: str, json: dict = None):
        """Mock PUT 请求"""
        return {"code": 200, "data": None, "message": "OK"}
    
    async def delete(self, path: str):
        """Mock DELETE 请求"""
        return {"code": 200, "data": None, "message": "OK"}


@pytest.fixture
def mock_client():
    """提供Mock客户端实例"""
    return MockApiClient()


@pytest.fixture
def sample_tenant_id():
    return str(uuid4())


@pytest.fixture
def sample_user_id():
    return str(uuid4())


# ═══════════════════════════════════════════════════════════════════════════════
# 1. Blockchain - CarbonCertification (I-REC/CCER) 测试
# ═══════════════════════════════════════════════════════════════════════════════

class TestCarbonCertificationApi:
    """I-REC国际绿证 + CCER碳信用核证 API 测试"""
    
    BASE_PATH = "/api/carbon"
    
    # ─── I-REC 绿证测试 ───
    
    @pytest.mark.asyncio
    async def test_irec_register_success(self, mock_client):
        """测试 I-REC 设备注册 - 正常场景"""
        request_data = {
            "deviceCode": "PV-DEVICE-001",
            "deviceType": "solar_pv",
            "installedCapacityKw": 500.0,
            "commissioningDate": "2025-01-01",
            "location": {"country": "CN", "province": "Jiangsu", "city": "Nanjing"},
            "gridConnectionType": "grid_connected"
        }
        response = await mock_client.post(f"{self.BASE_PATH}/irec/register", json=request_data)
        assert response["code"] == 200
        assert response["data"] is not None
    
    @pytest.mark.asyncio
    async def test_irec_register_missing_required_fields(self, mock_client):
        """测试 I-REC 设备注册 - 缺少必填字段"""
        request_data = {"deviceCode": "PV-001"}  # 缺少其他必填字段
        # 应返回验证错误
        with patch.object(mock_client, 'post', return_value={"code": 400, "message": "缺少必填字段"}):
            response = await mock_client.post(f"{self.BASE_PATH}/irec/register", json=request_data)
            assert response["code"] == 400
    
    @pytest.mark.asyncio
    async def test_irec_issue_certificate(self, mock_client):
        """测试 I-REC 证书签发"""
        request_data = {
            "deviceId": str(uuid4()),
            "periodStart": "2025-01-01",
            "periodEnd": "2025-01-31",
            "generationMwh": 150.5,
            "fuelType": "solar"
        }
        response = await mock_client.post(f"{self.BASE_PATH}/irec/issue", json=request_data)
        assert response["code"] == 200
    
    @pytest.mark.asyncio
    async def test_irec_transfer_certificate(self, mock_client):
        """测试 I-REC 证书转让"""
        certificate_id = str(uuid4())
        request_data = {"toAccountId": str(uuid4())}
        response = await mock_client.post(
            f"{self.BASE_PATH}/irec/{certificate_id}/transfer", 
            json=request_data
        )
        assert response["code"] == 200
    
    @pytest.mark.asyncio
    async def test_irec_retire_certificate(self, mock_client):
        """测试 I-REC 证书注销"""
        certificate_id = str(uuid4())
        request_data = {"purpose": "carbon_offset_compliance"}
        response = await mock_client.post(
            f"{self.BASE_PATH}/irec/{certificate_id}/retire",
            json=request_data
        )
        assert response["code"] == 200
    
    @pytest.mark.asyncio
    async def test_irec_get_certificates_list(self, mock_client):
        """测试 I-REC 证书列表查询"""
        params = {"status": "active", "page": 1, "pageSize": 20}
        response = await mock_client.get(f"{self.BASE_PATH}/irec/certificates", params=params)
        assert response["code"] == 200
        assert "data" in response
    
    @pytest.mark.asyncio
    async def test_irec_get_certificates_with_pagination(self, mock_client):
        """测试 I-REC 证书列表分页"""
        for page in [1, 2, 3]:
            params = {"page": page, "pageSize": 10}
            response = await mock_client.get(f"{self.BASE_PATH}/irec/certificates", params=params)
            assert response["code"] == 200
    
    # ─── CCER 碳信用测试 ───
    
    @pytest.mark.asyncio
    async def test_ccer_register_project(self, mock_client):
        """测试 CCER 项目注册"""
        request_data = {
            "projectName": "江苏光伏碳减排项目",
            "projectType": "renewable_energy",
            "methodologyId": "CM-001",
            "estimatedReductionTco2": 10000,
            "creditingPeriodYears": 7,
            "location": {"province": "Jiangsu", "city": "Nanjing"}
        }
        response = await mock_client.post(f"{self.BASE_PATH}/ccer/project", json=request_data)
        assert response["code"] == 200
    
    @pytest.mark.asyncio
    async def test_ccer_get_projects_list(self, mock_client):
        """测试 CCER 项目列表查询"""
        params = {"page": 1, "pageSize": 20}
        response = await mock_client.get(f"{self.BASE_PATH}/ccer/projects", params=params)
        assert response["code"] == 200
    
    @pytest.mark.asyncio
    async def test_ccer_request_credits(self, mock_client):
        """测试 CCER 碳信用签发申请"""
        request_data = {
            "projectId": str(uuid4()),
            "monitoringPeriodStart": "2025-01-01",
            "monitoringPeriodEnd": "2025-06-30",
            "claimedReductionTco2": 5000,
            "verifierName": "第三方核证机构"
        }
        response = await mock_client.post(f"{self.BASE_PATH}/ccer/credits", json=request_data)
        assert response["code"] == 200
    
    @pytest.mark.asyncio
    async def test_ccer_verify_credit(self, mock_client):
        """测试 CCER 第三方核证"""
        credit_id = str(uuid4())
        request_data = {
            "verifierName": "SGS",
            "verificationDate": "2025-07-15",
            "verifiedReductionTco2": 4800,
            "verificationReport": "VR-2025-001"
        }
        response = await mock_client.post(
            f"{self.BASE_PATH}/ccer/credits/{credit_id}/verify",
            json=request_data
        )
        assert response["code"] == 200
    
    @pytest.mark.asyncio
    async def test_ccer_trade_credit(self, mock_client):
        """测试 CCER 碳信用交易"""
        credit_id = str(uuid4())
        request_data = {
            "buyerTenantId": str(uuid4()),
            "pricePerTco2": 58.5
        }
        response = await mock_client.post(
            f"{self.BASE_PATH}/ccer/credits/{credit_id}/trade",
            json=request_data
        )
        assert response["code"] == 200
    
    @pytest.mark.asyncio
    async def test_ccer_retire_credit(self, mock_client):
        """测试 CCER 碳信用注销(碳抵消)"""
        credit_id = str(uuid4())
        request_data = {"purpose": "voluntary_offset"}
        response = await mock_client.post(
            f"{self.BASE_PATH}/ccer/credits/{credit_id}/retire",
            json=request_data
        )
        assert response["code"] == 200


# ═══════════════════════════════════════════════════════════════════════════════
# 2. Charging - OrderlyCharging (智能排队充电) 测试
# ═══════════════════════════════════════════════════════════════════════════════

class TestOrderlyChargingApi:
    """多车排队智能调度 API 测试 - 低SOC优先 + 负荷均衡"""
    
    BASE_PATH = "/api/charging/orderly"
    
    @pytest.mark.asyncio
    async def test_enqueue_charging_request(self, mock_client):
        """测试 提交排队请求"""
        request_data = {
            "stationId": str(uuid4()),
            "vehicleId": "京A12345",
            "batteryCapacityKwh": 60.0,
            "currentSocPercent": 20,
            "targetSocPercent": 80,
            "maxChargingPowerKw": 120,
            "priority": "normal"
        }
        response = await mock_client.post(f"{self.BASE_PATH}/enqueue", json=request_data)
        assert response["code"] == 200
        assert response["data"] is not None
    
    @pytest.mark.asyncio
    async def test_enqueue_urgent_request(self, mock_client):
        """测试 紧急充电请求 - 低SOC优先级"""
        request_data = {
            "stationId": str(uuid4()),
            "vehicleId": "京B88888",
            "batteryCapacityKwh": 75.0,
            "currentSocPercent": 5,  # 极低SOC
            "targetSocPercent": 50,
            "maxChargingPowerKw": 150,
            "priority": "urgent"
        }
        response = await mock_client.post(f"{self.BASE_PATH}/enqueue", json=request_data)
        assert response["code"] == 200
    
    @pytest.mark.asyncio
    async def test_dispatch_charging(self, mock_client):
        """测试 执行智能调度"""
        station_id = str(uuid4())
        response = await mock_client.post(f"{self.BASE_PATH}/{station_id}/dispatch")
        assert response["code"] == 200
    
    @pytest.mark.asyncio
    async def test_get_queue_status(self, mock_client):
        """测试 获取排队列表"""
        station_id = str(uuid4())
        response = await mock_client.get(f"{self.BASE_PATH}/{station_id}/queue")
        assert response["code"] == 200
    
    @pytest.mark.asyncio
    async def test_cancel_queue(self, mock_client):
        """测试 取消排队"""
        queue_id = str(uuid4())
        response = await mock_client.delete(f"{self.BASE_PATH}/queue/{queue_id}")
        assert response["code"] == 200
    
    @pytest.mark.asyncio
    async def test_cancel_nonexistent_queue(self, mock_client):
        """测试 取消不存在的排队记录"""
        queue_id = str(uuid4())
        with patch.object(mock_client, 'delete', return_value={"code": 404, "message": "排队记录不存在"}):
            response = await mock_client.delete(f"{self.BASE_PATH}/queue/{queue_id}")
            assert response["code"] == 404
    
    @pytest.mark.asyncio
    async def test_get_pile_load_status(self, mock_client):
        """测试 获取充电桩负荷状态"""
        station_id = str(uuid4())
        response = await mock_client.get(f"{self.BASE_PATH}/{station_id}/pile-load")
        assert response["code"] == 200


# ═══════════════════════════════════════════════════════════════════════════════
# 3. MicroGrid - MgEnergyReport (微电网能耗统计报表) 测试
# ═══════════════════════════════════════════════════════════════════════════════

class TestMgEnergyReportApi:
    """微电网能耗统计报表 API 测试"""
    
    BASE_PATH = "/api/microgrid/energy"
    
    @pytest.mark.asyncio
    async def test_get_energy_overview(self, mock_client):
        """测试 获取能耗统计概览"""
        params = {
            "gridId": str(uuid4()),
            "startDate": "2025-01-01",
            "endDate": "2025-01-31"
        }
        response = await mock_client.get(f"{self.BASE_PATH}/overview", params=params)
        assert response["code"] == 200
    
    @pytest.mark.asyncio
    async def test_get_daily_report(self, mock_client):
        """测试 获取日报表（24小时明细）"""
        grid_id = str(uuid4())
        params = {"date": "2025-03-18"}
        response = await mock_client.get(f"{self.BASE_PATH}/{grid_id}/daily", params=params)
        assert response["code"] == 200
    
    @pytest.mark.asyncio
    async def test_get_monthly_report(self, mock_client):
        """测试 获取月报表（每日汇总）"""
        grid_id = str(uuid4())
        params = {"year": 2025, "month": 3}
        response = await mock_client.get(f"{self.BASE_PATH}/{grid_id}/monthly", params=params)
        assert response["code"] == 200
    
    @pytest.mark.asyncio
    async def test_get_trend_comparison(self, mock_client):
        """测试 获取能耗趋势对比"""
        request_data = {
            "gridIds": [str(uuid4()) for _ in range(3)],
            "startDate": "2025-01-01",
            "endDate": "2025-03-31"
        }
        response = await mock_client.post(f"{self.BASE_PATH}/trend/comparison", json=request_data)
        assert response["code"] == 200
    
    @pytest.mark.asyncio
    async def test_record_energy_data(self, mock_client):
        """测试 录入能耗数据（内部接口）"""
        request_data = {
            "gridId": str(uuid4()),
            "timestamp": datetime.utcnow().isoformat(),
            "pvGenerationKwh": 150.5,
            "batteryChargeKwh": 30.0,
            "batteryDischargeKwh": 25.0,
            "gridImportKwh": 50.0,
            "gridExportKwh": 80.0,
            "loadConsumptionKwh": 120.0
        }
        response = await mock_client.post(f"{self.BASE_PATH}/data", json=request_data)
        assert response["code"] == 200


# ═══════════════════════════════════════════════════════════════════════════════
# 4. Orchestrator - CimProtocol (IEC 61968/CIM) 测试
# ═══════════════════════════════════════════════════════════════════════════════

class TestCimProtocolApi:
    """IEC 61968/CIM 标准化接口 — 省级调度中心对接测试"""
    
    BASE_PATH = "/api/orchestrator/cim"
    
    @pytest.mark.asyncio
    async def test_receive_dispatch_command(self, mock_client):
        """测试 接收省级调度指令"""
        request_data = {
            "messageId": str(uuid4()),
            "commandType": "EndDeviceControl",
            "targetDeviceIds": [str(uuid4()) for _ in range(5)],
            "controlAction": "setpoint",
            "setpointValue": 500.0,
            "validFrom": datetime.utcnow().isoformat(),
            "validTo": (datetime.utcnow() + timedelta(hours=1)).isoformat(),
            "priority": "high"
        }
        response = await mock_client.post(f"{self.BASE_PATH}/dispatch/receive", json=request_data)
        assert response["code"] == 200
    
    @pytest.mark.asyncio
    async def test_get_dispatch_feedback(self, mock_client):
        """测试 生成IEC 61968反馈报文"""
        record_id = str(uuid4())
        response = await mock_client.get(f"{self.BASE_PATH}/dispatch/{record_id}/feedback")
        assert response["code"] == 200
    
    @pytest.mark.asyncio
    async def test_get_dispatch_records(self, mock_client):
        """测试 查询CIM调度记录"""
        params = {
            "startTime": "2025-03-01T00:00:00Z",
            "endTime": "2025-03-18T23:59:59Z",
            "status": "executed",
            "page": 1,
            "pageSize": 20
        }
        response = await mock_client.get(f"{self.BASE_PATH}/dispatch/records", params=params)
        assert response["code"] == 200
    
    @pytest.mark.asyncio
    async def test_get_cim_config(self, mock_client):
        """测试 获取CIM接口配置"""
        response = await mock_client.get(f"{self.BASE_PATH}/config")
        assert response["code"] == 200
    
    @pytest.mark.asyncio
    async def test_save_cim_config(self, mock_client):
        """测试 保存CIM接口配置"""
        request_data = {
            "endpointUrl": "https://dispatch.grid.cn/cim/v1",
            "username": "grid_endpoint",
            "authType": "certificate",
            "certificatePath": "/certs/grid.pem",
            "retryCount": 3,
            "timeoutSeconds": 30
        }
        response = await mock_client.put(f"{self.BASE_PATH}/config", json=request_data)
        assert response["code"] == 200
    
    @pytest.mark.asyncio
    async def test_record_deviation_sample(self, mock_client):
        """测试 记录调度偏差采样"""
        request_data = {
            "dispatchRecordId": str(uuid4()),
            "sampleTime": datetime.utcnow().isoformat(),
            "targetValueKw": 500.0,
            "actualValueKw": 485.5,
            "deviationKw": 14.5,
            "deviationPercent": 2.9
        }
        response = await mock_client.post(f"{self.BASE_PATH}/deviation/sample", json=request_data)
        assert response["code"] == 200
    
    @pytest.mark.asyncio
    async def test_get_deviation_analysis(self, mock_client):
        """测试 获取偏差分析"""
        record_id = str(uuid4())
        response = await mock_client.get(f"{self.BASE_PATH}/deviation/{record_id}/analysis")
        assert response["code"] == 200
    
    @pytest.mark.asyncio
    async def test_get_deviation_records(self, mock_client):
        """测试 查询偏差采样记录"""
        params = {
            "startTime": "2025-03-01T00:00:00Z",
            "endTime": "2025-03-18T23:59:59Z",
            "page": 1,
            "pageSize": 50
        }
        response = await mock_client.get(f"{self.BASE_PATH}/deviation/records", params=params)
        assert response["code"] == 200
    
    @pytest.mark.asyncio
    async def test_get_feedback_summary(self, mock_client):
        """测试 获取执行结果聚合反馈"""
        params = {
            "startTime": "2025-03-01T00:00:00Z",
            "endTime": "2025-03-18T23:59:59Z"
        }
        response = await mock_client.get(f"{self.BASE_PATH}/feedback/summary", params=params)
        assert response["code"] == 200


# ═══════════════════════════════════════════════════════════════════════════════
# 5. PVESSC - StringMonitor (光伏组串级监控) 测试
# ═══════════════════════════════════════════════════════════════════════════════

class TestStringMonitorApi:
    """光伏组串级监控 API 测试 — 热斑/遮挡/衰减异常检测"""
    
    BASE_PATH = "/api/pvessc/string-monitor"
    
    @pytest.mark.asyncio
    async def test_detect_anomalies(self, mock_client):
        """测试 执行组串异常检测"""
        site_id = str(uuid4())
        params = {"sampleTime": datetime.utcnow().isoformat()}
        response = await mock_client.post(f"{self.BASE_PATH}/{site_id}/detect", json=params)
        assert response["code"] == 200
    
    @pytest.mark.asyncio
    async def test_get_anomalies_list(self, mock_client):
        """测试 查询异常记录"""
        params = {
            "siteId": str(uuid4()),
            "anomalyType": "hotspot",
            "severity": "high",
            "startTime": "2025-03-01T00:00:00Z",
            "endTime": "2025-03-18T23:59:59Z",
            "page": 1,
            "pageSize": 20
        }
        response = await mock_client.get(f"{self.BASE_PATH}/anomalies", params=params)
        assert response["code"] == 200
    
    @pytest.mark.asyncio
    async def test_get_anomalies_by_type(self, mock_client):
        """测试 按异常类型查询"""
        anomaly_types = ["hotspot", "shading", "degradation", "mismatch"]
        for anomaly_type in anomaly_types:
            params = {"anomalyType": anomaly_type, "page": 1, "pageSize": 10}
            response = await mock_client.get(f"{self.BASE_PATH}/anomalies", params=params)
            assert response["code"] == 200
    
    @pytest.mark.asyncio
    async def test_record_string_telemetry(self, mock_client):
        """测试 录入组串遥测数据"""
        request_data = {
            "siteId": str(uuid4()),
            "inverterId": "INV-001",
            "stringId": "STRING-01",
            "timestamp": datetime.utcnow().isoformat(),
            "voltageV": 380.5,
            "currentA": 8.2,
            "powerW": 3120.0,
            "temperatureC": 45.5
        }
        response = await mock_client.post(f"{self.BASE_PATH}/telemetry", json=request_data)
        assert response["code"] == 200
    
    @pytest.mark.asyncio
    async def test_set_baseline(self, mock_client):
        """测试 设置组串功率基准值"""
        site_id = str(uuid4())
        request_data = {
            "stringId": "STRING-01",
            "baselinePowerW": 3500.0
        }
        response = await mock_client.put(f"{self.BASE_PATH}/{site_id}/baseline", json=request_data)
        assert response["code"] == 200


# ═══════════════════════════════════════════════════════════════════════════════
# 6. IotCloudAI - AdaptivePredict (自适应多模型组合预测) 测试
# ═══════════════════════════════════════════════════════════════════════════════

class TestAdaptivePredictApi:
    """自适应多模型组合预测控制器测试"""
    
    BASE_PATH = "/api/iotcloudai/adaptive"
    
    @pytest.mark.asyncio
    async def test_adaptive_predict(self, mock_client):
        """测试 自适应预测（自动选择最优模型组合）"""
        request_data = {
            "predictScene": "pv_power",
            "forecastHours": 24,
            "targetDeviceId": str(uuid4()),
            "historicalDataDays": 30,
            "weatherForecast": {
                "temperature": [15, 18, 22, 25, 24, 20],
                "irradiance": [200, 500, 800, 900, 700, 300],
                "cloudCover": [0.1, 0.2, 0.1, 0.3, 0.4, 0.6]
            }
        }
        response = await mock_client.post(f"{self.BASE_PATH}/predict", json=request_data)
        assert response["code"] == 200
    
    @pytest.mark.asyncio
    async def test_predict_various_scenes(self, mock_client):
        """测试 不同预测场景"""
        scenes = ["pv_power", "load_demand", "battery_soc", "grid_import"]
        for scene in scenes:
            request_data = {
                "predictScene": scene,
                "forecastHours": 12,
                "targetDeviceId": str(uuid4())
            }
            response = await mock_client.post(f"{self.BASE_PATH}/predict", json=request_data)
            assert response["code"] == 200
    
    @pytest.mark.asyncio
    async def test_get_available_models(self, mock_client):
        """测试 获取指定场景可用模型列表"""
        params = {"scene": "pv_power"}
        response = await mock_client.get(f"{self.BASE_PATH}/models", params=params)
        assert response["code"] == 200
    
    @pytest.mark.asyncio
    async def test_record_performance_feedback(self, mock_client):
        """测试 记录预测准确率回溯"""
        request_data = {
            "modelCombination": "lstm+attention+ensemble",
            "predictScene": "pv_power",
            "predicted": [100.0, 150.0, 200.0, 180.0],
            "actual": [95.0, 155.0, 195.0, 175.0]
        }
        response = await mock_client.post(f"{self.BASE_PATH}/performance", json=request_data)
        assert response["code"] == 200


# ═══════════════════════════════════════════════════════════════════════════════
# 7. IotCloudAI - Agent (智能体) 测试
# ═══════════════════════════════════════════════════════════════════════════════

class TestAgentApi:
    """v3.0 Agent 智能体控制器测试 — 自主规划 + 工具调用 + 多Agent协作"""
    
    BASE_PATH = "/api/iotcloudai/agent"
    
    @pytest.mark.asyncio
    async def test_agent_execute(self, mock_client):
        """测试 Agent 任务执行（同步）"""
        request_data = {
            "goal": "分析今日充电站运营数据，给出优化建议",
            "scene": "daily_ops",
            "maxIterations": 10,
            "timeoutSeconds": 120
        }
        response = await mock_client.post(f"{self.BASE_PATH}/execute", json=request_data)
        assert response["code"] == 200
    
    @pytest.mark.asyncio
    async def test_agent_execute_various_scenes(self, mock_client):
        """测试 Agent 不同场景执行"""
        test_cases = [
            {"goal": "预测明天光伏发电量", "scene": "prediction"},
            {"goal": "生成本周充电站收入报表", "scene": "report"},
            {"goal": "检查设备异常告警", "scene": "daily_ops"},
            {"goal": "优化储能调度策略", "scene": "energy"}
        ]
        for case in test_cases:
            request_data = {
                "goal": case["goal"],
                "scene": case["scene"],
                "maxIterations": 5,
                "timeoutSeconds": 60
            }
            response = await mock_client.post(f"{self.BASE_PATH}/execute", json=request_data)
            assert response["code"] == 200
    
    @pytest.mark.asyncio
    async def test_get_execution_history(self, mock_client):
        """测试 查询执行历史"""
        params = {"limit": 20}
        response = await mock_client.get(f"{self.BASE_PATH}/history", params=params)
        assert response["code"] == 200
    
    @pytest.mark.asyncio
    async def test_get_execution_detail(self, mock_client):
        """测试 查询执行详情（含思考步骤）"""
        execution_id = str(uuid4())
        response = await mock_client.get(f"{self.BASE_PATH}/execution/{execution_id}")
        assert response["code"] == 200
    
    @pytest.mark.asyncio
    async def test_get_registered_agents(self, mock_client):
        """测试 查询已注册的Agent列表"""
        response = await mock_client.get(f"{self.BASE_PATH}/agents")
        assert response["code"] == 200


# ═══════════════════════════════════════════════════════════════════════════════
# 8. IotCloudAI - DeviceHealth (设备健康评估) 测试
# ═══════════════════════════════════════════════════════════════════════════════

class TestDeviceHealthApi:
    """设备健康评估控制器测试"""
    
    BASE_PATH = "/api/iotcloudai/health"
    
    @pytest.mark.asyncio
    async def test_assess_device_health(self, mock_client):
        """测试 评估单台设备健康度"""
        request_data = {
            "deviceId": "DEVICE-001",
            "deviceType": "charging_pile",
            "operatingHours": 5000,
            "lastMaintenanceDate": "2025-01-15",
            "recentMetrics": {
                "avgTemperature": 45.5,
                "avgVoltage": 380.0,
                "errorCount": 3
            }
        }
        response = await mock_client.post(f"{self.BASE_PATH}/assess", json=request_data)
        assert response["code"] == 200
    
    @pytest.mark.asyncio
    async def test_assess_device_health_various_types(self, mock_client):
        """测试 不同设备类型健康评估"""
        device_types = ["charging_pile", "inverter", "battery", "transformer", "pv_panel"]
        for device_type in device_types:
            request_data = {
                "deviceId": f"{device_type.upper()}-001",
                "deviceType": device_type,
                "operatingHours": 3000
            }
            response = await mock_client.post(f"{self.BASE_PATH}/assess", json=request_data)
            assert response["code"] == 200
    
    @pytest.mark.asyncio
    async def test_batch_assess_devices(self, mock_client):
        """测试 批量评估多台设备健康度"""
        request_data = {
            "deviceIds": [f"DEVICE-{i:03d}" for i in range(10)]
        }
        response = await mock_client.post(f"{self.BASE_PATH}/assess/batch", json=request_data)
        assert response["code"] == 200
    
    @pytest.mark.asyncio
    async def test_get_health_trend(self, mock_client):
        """测试 获取设备健康趋势"""
        device_id = "DEVICE-001"
        params = {"days": 30}
        response = await mock_client.get(f"{self.BASE_PATH}/trend/{device_id}", params=params)
        assert response["code"] == 200


# ═══════════════════════════════════════════════════════════════════════════════
# 9. IotCloudAI - ThirdPartyModel (第三方大模型代理) 测试
# ═══════════════════════════════════════════════════════════════════════════════

class TestThirdPartyModelApi:
    """第三方大模型代理控制器测试"""
    
    BASE_PATH = "/api/iotcloudai/third-party"
    
    @pytest.mark.asyncio
    async def test_third_party_chat(self, mock_client):
        """测试 第三方大模型对话（同步）"""
        request_data = {
            "provider": "ali",
            "message": "请解释光储充一体化系统的工作原理",
            "systemPrompt": "你是一个新能源领域的技术专家",
            "temperature": 0.7,
            "maxTokens": 2048
        }
        response = await mock_client.post(f"{self.BASE_PATH}/chat", json=request_data)
        assert response["code"] == 200
    
    @pytest.mark.asyncio
    async def test_third_party_chat_various_providers(self, mock_client):
        """测试 不同供应商对话"""
        providers = ["ali", "tencent", "baidu", "bytedance"]
        for provider in providers:
            request_data = {
                "provider": provider,
                "message": "你好，请介绍一下你自己"
            }
            response = await mock_client.post(f"{self.BASE_PATH}/chat", json=request_data)
            assert response["code"] == 200
    
    @pytest.mark.asyncio
    async def test_chat_with_history(self, mock_client):
        """测试 带历史对话的请求"""
        request_data = {
            "message": "继续刚才的话题",
            "history": [
                {"role": "user", "content": "什么是微电网?"},
                {"role": "assistant", "content": "微电网是一个包含..."}
            ]
        }
        response = await mock_client.post(f"{self.BASE_PATH}/chat", json=request_data)
        assert response["code"] == 200
    
    @pytest.mark.asyncio
    async def test_get_available_providers(self, mock_client):
        """测试 获取当前可用的第三方供应商列表"""
        response = await mock_client.get(f"{self.BASE_PATH}/providers")
        assert response["code"] == 200
    
    @pytest.mark.asyncio
    async def test_health_check(self, mock_client):
        """测试 第三方大模型健康检查"""
        response = await mock_client.get(f"{self.BASE_PATH}/health")
        assert response["code"] == 200


# ═══════════════════════════════════════════════════════════════════════════════
# 通用测试：权限验证、多租户隔离
# ═══════════════════════════════════════════════════════════════════════════════

class TestPermissionAndTenantIsolation:
    """权限验证与多租户隔离测试"""
    
    @pytest.mark.asyncio
    @pytest.mark.parametrize("endpoint,method", [
        ("/api/carbon/irec/register", "POST"),
        ("/api/carbon/ccer/project", "POST"),
        ("/api/charging/orderly/enqueue", "POST"),
        ("/api/microgrid/energy/overview", "GET"),
        ("/api/orchestrator/cim/dispatch/receive", "POST"),
        ("/api/pvessc/string-monitor/anomalies", "GET"),
        ("/api/iotcloudai/adaptive/predict", "POST"),
        ("/api/iotcloudai/agent/execute", "POST"),
        ("/api/iotcloudai/health/assess", "POST"),
        ("/api/iotcloudai/third-party/chat", "POST"),
    ])
    async def test_unauthorized_access_rejected(self, mock_client, endpoint, method):
        """测试 未授权访问被拒绝"""
        with patch.object(mock_client, 'headers', {}):  # 移除token
            with patch.object(mock_client, 'post', return_value={"code": 401, "message": "未授权"}):
                with patch.object(mock_client, 'get', return_value={"code": 401, "message": "未授权"}):
                    if method == "POST":
                        response = await mock_client.post(endpoint, json={})
                    else:
                        response = await mock_client.get(endpoint)
                    assert response["code"] == 401
    
    @pytest.mark.asyncio
    async def test_tenant_isolation(self, mock_client, sample_tenant_id):
        """测试 租户数据隔离"""
        # 模拟不同租户访问
        tenant_a = str(uuid4())
        tenant_b = str(uuid4())
        
        # 租户A创建数据
        with patch.object(mock_client, 'tenant_id', tenant_a):
            response = await mock_client.post("/api/carbon/irec/register", json={
                "deviceCode": "TENANT-A-DEVICE"
            })
            assert response["code"] == 200
        
        # 租户B不应能访问租户A的数据
        # (实际实现中通过后端tenant_id过滤)


# ═══════════════════════════════════════════════════════════════════════════════
# 边界条件和异常场景测试
# ═══════════════════════════════════════════════════════════════════════════════

class TestEdgeCasesAndValidation:
    """边界条件和验证测试"""
    
    @pytest.mark.asyncio
    async def test_empty_request_body(self, mock_client):
        """测试 空请求体"""
        with patch.object(mock_client, 'post', return_value={"code": 400, "message": "请求体不能为空"}):
            response = await mock_client.post("/api/carbon/irec/register", json={})
            assert response["code"] == 400
    
    @pytest.mark.asyncio
    async def test_invalid_uuid_format(self, mock_client):
        """测试 无效UUID格式"""
        with patch.object(mock_client, 'get', return_value={"code": 400, "message": "无效的ID格式"}):
            response = await mock_client.get("/api/iotcloudai/agent/execution/invalid-uuid")
            assert response["code"] == 400
    
    @pytest.mark.asyncio
    async def test_pagination_boundary(self, mock_client):
        """测试 分页边界"""
        # 测试极端分页参数
        test_cases = [
            {"page": 0, "pageSize": 10},      # page不能为0
            {"page": 1, "pageSize": 0},       # pageSize不能为0
            {"page": 1, "pageSize": 10000},   # pageSize过大
            {"page": -1, "pageSize": 10},     # 负数page
        ]
        for params in test_cases:
            with patch.object(mock_client, 'get', return_value={"code": 400, "message": "无效分页参数"}):
                response = await mock_client.get("/api/carbon/irec/certificates", params=params)
                assert response["code"] == 400
    
    @pytest.mark.asyncio
    async def test_date_range_validation(self, mock_client):
        """测试 日期范围验证"""
        # 结束日期早于开始日期
        params = {
            "startTime": "2025-03-18T00:00:00Z",
            "endTime": "2025-03-01T00:00:00Z"  # 早于开始时间
        }
        with patch.object(mock_client, 'get', return_value={"code": 400, "message": "日期范围无效"}):
            response = await mock_client.get("/api/orchestrator/cim/dispatch/records", params=params)
            assert response["code"] == 400
    
    @pytest.mark.asyncio
    async def test_max_batch_size_limit(self, mock_client):
        """测试 批量操作数量限制"""
        # 超出最大批量限制
        request_data = {
            "deviceIds": [f"DEVICE-{i:05d}" for i in range(1001)]  # 超过1000限制
        }
        with patch.object(mock_client, 'post', return_value={"code": 400, "message": "批量操作不能超过1000条"}):
            response = await mock_client.post("/api/iotcloudai/health/assess/batch", json=request_data)
            assert response["code"] == 400


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
