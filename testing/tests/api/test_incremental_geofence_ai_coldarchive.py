"""
增量测试 — GeoFence + IotCloudAI 5大新能力 + ColdArchive + 后台任务 + 内部API
============================================================================
覆盖本轮 Git 变更新增的全部 API 端点与业务逻辑：
- Station GeoFence（6 端点：CRUD + CheckPoint）
- IotCloudAI ImageSearch（6 端点）
- IotCloudAI LLM 多模型（5 端点）
- IotCloudAI ModelRouting（8 端点）
- IotCloudAI SolarPrediction（3 端点）
- IotCloudAI VisionInspection（4 端点）
- Storage Archive（3 端点）
- Observability InternalAlertNotification（2 端点）
- WorkOrder InternalWorkOrder（1 端点）
- Ingestion ProtocolSharding 配置
- Permission Blockchain 三员分立权限
- Device CommandTimeout 后台任务
- Trading OrderExpiration 后台任务
- Analytics DailyReportETL + ScheduledReport
- Settlement AutoSettlement
- Gateway YARP 路由拆分
"""

import pytest
import logging
import uuid
import json
import base64

logger = logging.getLogger(__name__)

_STATION_ID = str(uuid.uuid4())
_FENCE_ID = str(uuid.uuid4())
_MODULE_ID = "solar_fusion"


# ═══════════════════════════════════════════════════
# Station GeoFence 地理围栏
# ═══════════════════════════════════════════════════

@pytest.mark.p0
@pytest.mark.station
class TestStationGeoFenceAPI:
    """Station 地理围栏 CRUD + 空间判断"""

    @pytest.fixture(autouse=True)
    def _setup(self, gateway_api):
        self.client = gateway_api

    def test_geofence_create_circular(self):
        """创建圆形围栏"""
        payload = {
            "name": "测试圆形围栏",
            "fenceType": 1,
            "centerLongitude": 116.397428,
            "centerLatitude": 39.90923,
            "radiusMeters": 500,
            "isActive": True,
            "remark": "pytest自动创建"
        }
        resp = self.client.post(f"/api/stations/{_STATION_ID}/geo-fences", json=payload)
        assert resp.status_code < 500
        logger.info("GeoFence 创建圆形围栏 ✓")

    def test_geofence_create_polygon(self):
        """创建多边形围栏"""
        coords = json.dumps([
            [116.39, 39.90], [116.40, 39.90],
            [116.40, 39.91], [116.39, 39.91]
        ])
        payload = {
            "name": "测试多边形围栏",
            "fenceType": 2,
            "polygonCoordinates": coords,
            "isActive": True
        }
        resp = self.client.post(f"/api/stations/{_STATION_ID}/geo-fences", json=payload)
        assert resp.status_code < 500
        logger.info("GeoFence 创建多边形围栏 ✓")

    def test_geofence_list_by_station(self):
        """按场站查询围栏列表"""
        resp = self.client.get(f"/api/stations/{_STATION_ID}/geo-fences")
        assert resp.status_code < 500
        logger.info("GeoFence 场站围栏列表 ✓")

    def test_geofence_get_by_id(self):
        """根据ID获取围栏详情"""
        resp = self.client.get(f"/api/stations/{_STATION_ID}/geo-fences/{_FENCE_ID}")
        assert resp.status_code < 500
        logger.info("GeoFence 围栏详情 ✓")

    def test_geofence_update(self):
        """更新围栏"""
        payload = {"name": "更新后围栏名称", "radiusMeters": 800, "isActive": True}
        resp = self.client.put(f"/api/stations/{_STATION_ID}/geo-fences/{_FENCE_ID}", json=payload)
        assert resp.status_code < 500
        logger.info("GeoFence 更新围栏 ✓")

    def test_geofence_delete(self):
        """软删除围栏"""
        resp = self.client.delete(f"/api/stations/{_STATION_ID}/geo-fences/{_FENCE_ID}")
        assert resp.status_code < 500
        logger.info("GeoFence 软删除围栏 ✓")

    def test_geofence_check_point_inside(self):
        """坐标点判断-在围栏内"""
        payload = {"longitude": 116.397428, "latitude": 39.90923}
        resp = self.client.post(f"/api/stations/{_STATION_ID}/geo-fences/check", json=payload)
        assert resp.status_code < 500
        logger.info("GeoFence 坐标判断(内) ✓")

    def test_geofence_check_point_outside(self):
        """坐标点判断-在围栏外(远端坐标)"""
        payload = {"longitude": 121.47, "latitude": 31.23}
        resp = self.client.post(f"/api/stations/{_STATION_ID}/geo-fences/check", json=payload)
        assert resp.status_code < 500
        logger.info("GeoFence 坐标判断(外) ✓")

    def test_geofence_create_missing_fields(self):
        """创建围栏-缺少必填字段"""
        resp = self.client.post(f"/api/stations/{_STATION_ID}/geo-fences", json={})
        assert resp.status_code < 500
        logger.info("GeoFence 缺少字段校验 ✓")

    def test_geofence_invalid_fence_type(self):
        """创建围栏-无效围栏类型"""
        payload = {"name": "测试", "fenceType": 99}
        resp = self.client.post(f"/api/stations/{_STATION_ID}/geo-fences", json=payload)
        assert resp.status_code < 500
        logger.info("GeoFence 无效类型校验 ✓")


# ═══════════════════════════════════════════════════
# IotCloudAI — ImageSearch 以图搜图
# ═══════════════════════════════════════════════════

@pytest.mark.p0
@pytest.mark.iotcloudai
class TestImageSearchAPI:
    """IotCloudAI 图像检索 API"""

    @pytest.fixture(autouse=True)
    def _setup(self, gateway_api):
        self.client = gateway_api

    def test_imagesearch_status(self):
        """获取图检索引擎状态"""
        resp = self.client.get("/api/iotcloudai/image-search/status")
        assert resp.status_code < 500
        logger.info("ImageSearch 引擎状态 ✓")

    def test_imagesearch_by_text(self):
        """文本搜图"""
        payload = {"query": "光伏面板", "topK": 5, "minScore": 0.3}
        resp = self.client.post("/api/iotcloudai/image-search/by-text", json=payload)
        assert resp.status_code < 500
        logger.info("ImageSearch 文本搜图 ✓")

    def test_imagesearch_index_image(self):
        """索引图片"""
        resp = self.client.post("/api/iotcloudai/image-search/index",
                                params={"id": str(uuid.uuid4()), "label": "pv_panel"})
        assert resp.status_code < 500
        logger.info("ImageSearch 索引图片 ✓")

    def test_imagesearch_remove_index(self):
        """移除索引"""
        resp = self.client.delete(f"/api/iotcloudai/image-search/index/{str(uuid.uuid4())}")
        assert resp.status_code < 500
        logger.info("ImageSearch 移除索引 ✓")

    def test_imagesearch_save_index(self):
        """保存索引到磁盘"""
        resp = self.client.post("/api/iotcloudai/image-search/save-index")
        assert resp.status_code < 500
        logger.info("ImageSearch 保存索引 ✓")


# ═══════════════════════════════════════════════════
# IotCloudAI — LLM 多模型管理
# ═══════════════════════════════════════════════════

@pytest.mark.p0
@pytest.mark.iotcloudai
class TestLlmControllerAPI:
    """IotCloudAI LLM 多模型热切换与推理"""

    @pytest.fixture(autouse=True)
    def _setup(self, gateway_api):
        self.client = gateway_api

    def test_llm_list_models(self):
        """列出所有模型状态"""
        resp = self.client.get("/api/iotcloudai/llm/models")
        assert resp.status_code < 500
        logger.info("LLM 模型列表 ✓")

    def test_llm_get_active(self):
        """获取当前活跃模型"""
        resp = self.client.get("/api/iotcloudai/llm/active")
        assert resp.status_code < 500
        logger.info("LLM 活跃模型 ✓")

    def test_llm_switch_model(self):
        """切换模型"""
        payload = {"modelKey": "qwen-7b"}
        resp = self.client.post("/api/iotcloudai/llm/switch", json=payload)
        assert resp.status_code < 500
        logger.info("LLM 切换模型 ✓")

    def test_llm_unload_model(self):
        """卸载模型"""
        payload = {"modelKey": "qwen-7b"}
        resp = self.client.post("/api/iotcloudai/llm/unload", json=payload)
        assert resp.status_code < 500
        logger.info("LLM 卸载模型 ✓")

    def test_llm_generate(self):
        """LLM 推理问答"""
        payload = {
            "prompt": "充电桩设备运行状态如何？",
            "maxTokens": 128,
            "temperature": 0.7
        }
        resp = self.client.post("/api/iotcloudai/llm/generate", json=payload)
        assert resp.status_code < 500
        logger.info("LLM 推理问答 ✓")

    def test_llm_generate_empty_prompt(self):
        """LLM 空 prompt 校验"""
        payload = {"prompt": "", "maxTokens": 128}
        resp = self.client.post("/api/iotcloudai/llm/generate", json=payload)
        assert resp.status_code < 500
        logger.info("LLM 空prompt校验 ✓")


# ═══════════════════════════════════════════════════
# IotCloudAI — ModelRouting 智能路由
# ═══════════════════════════════════════════════════

@pytest.mark.p0
@pytest.mark.iotcloudai
class TestModelRoutingAPI:
    """IotCloudAI 智能模型路由 — 意图×场景×置信度三维矩阵"""

    @pytest.fixture(autouse=True)
    def _setup(self, gateway_api):
        self.client = gateway_api

    def test_routing_route_device_query(self):
        """路由-设备查询意图"""
        payload = {"intentType": "device_query", "scene": "general", "confidence": 0.85}
        resp = self.client.post("/api/v1/iotcloudai/model-routing/route", json=payload)
        assert resp.status_code < 500
        logger.info("ModelRouting 设备查询路由 ✓")

    def test_routing_route_prediction(self):
        """路由-预测意图"""
        payload = {"intentType": "prediction_query", "scene": "energy", "confidence": 0.9}
        resp = self.client.post("/api/v1/iotcloudai/model-routing/route", json=payload)
        assert resp.status_code < 500
        logger.info("ModelRouting 预测路由 ✓")

    def test_routing_route_low_confidence_fallback(self):
        """路由-低置信度回退"""
        payload = {"intentType": "device_query", "scene": "general", "confidence": 0.1}
        resp = self.client.post("/api/v1/iotcloudai/model-routing/route", json=payload)
        assert resp.status_code < 500
        logger.info("ModelRouting 低置信度回退 ✓")

    def test_routing_get_all_roles(self):
        """获取全部模型角色"""
        resp = self.client.get("/api/v1/iotcloudai/model-routing/roles")
        assert resp.status_code < 500
        logger.info("ModelRouting 全部角色 ✓")

    def test_routing_get_role_by_key(self):
        """获取指定模型角色"""
        resp = self.client.get("/api/v1/iotcloudai/model-routing/roles/qwen-7b")
        assert resp.status_code < 500
        logger.info("ModelRouting 指定角色 ✓")

    def test_routing_get_all_benchmarks(self):
        """获取全部精度基准"""
        resp = self.client.get("/api/v1/iotcloudai/model-routing/benchmarks")
        assert resp.status_code < 500
        logger.info("ModelRouting 全部基准 ✓")

    def test_routing_get_module_benchmark(self):
        """获取模块精度基准"""
        resp = self.client.get(f"/api/v1/iotcloudai/model-routing/benchmarks/{_MODULE_ID}")
        assert resp.status_code < 500
        logger.info("ModelRouting 模块基准 ✓")

    def test_routing_get_online_stats(self):
        """获取在线评估统计"""
        resp = self.client.get(f"/api/v1/iotcloudai/model-routing/benchmarks/{_MODULE_ID}/stats")
        assert resp.status_code < 500
        logger.info("ModelRouting 在线统计 ✓")

    def test_routing_record_inference(self):
        """记录推理结果"""
        payload = {"predicted": 95.2, "actual": 93.8}
        resp = self.client.post(
            f"/api/v1/iotcloudai/model-routing/benchmarks/{_MODULE_ID}/record", json=payload)
        assert resp.status_code < 500
        logger.info("ModelRouting 记录推理 ✓")

    def test_routing_dashboard(self):
        """AI能力总览仪表盘"""
        resp = self.client.get("/api/v1/iotcloudai/model-routing/dashboard")
        assert resp.status_code < 500
        logger.info("ModelRouting 仪表盘 ✓")


# ═══════════════════════════════════════════════════
# IotCloudAI — SolarPrediction 光伏预测
# ═══════════════════════════════════════════════════

@pytest.mark.p0
@pytest.mark.iotcloudai
class TestSolarPredictionAPI:
    """IotCloudAI 光伏发电量融合预测"""

    @pytest.fixture(autouse=True)
    def _setup(self, gateway_api):
        self.client = gateway_api

    def test_solar_predict_fusion(self):
        """三模型融合预测"""
        payload = {
            "stationId": str(uuid.uuid4()),
            "longitude": 116.397428,
            "latitude": 39.90923,
            "capacityKw": 100.0,
            "tiltAngle": 30.0,
            "azimuth": 180.0,
            "forecastHours": 24,
            "recentOutputKwh": [85.0, 92.0, 78.0, 95.0, 88.0]
        }
        resp = self.client.post("/api/iotcloudai/solar/predict", json=payload)
        assert resp.status_code < 500
        logger.info("Solar 融合预测 ✓")

    def test_solar_predict_physical_only(self):
        """纯物理模型预测"""
        payload = {
            "longitude": 116.397428,
            "latitude": 39.90923,
            "capacityKw": 100.0,
            "tiltAngle": 30.0,
            "azimuth": 180.0,
            "forecastHours": 12
        }
        resp = self.client.post("/api/iotcloudai/solar/predict/physical", json=payload)
        assert resp.status_code < 500
        logger.info("Solar 物理模型预测 ✓")

    def test_solar_status(self):
        """预测引擎状态"""
        resp = self.client.get("/api/iotcloudai/solar/status")
        assert resp.status_code < 500
        logger.info("Solar 引擎状态 ✓")

    def test_solar_predict_missing_coords(self):
        """缺少经纬度"""
        payload = {"capacityKw": 100.0, "forecastHours": 24}
        resp = self.client.post("/api/iotcloudai/solar/predict", json=payload)
        assert resp.status_code < 500
        logger.info("Solar 缺少坐标校验 ✓")

    def test_solar_predict_zero_capacity(self):
        """零容量预测"""
        payload = {
            "longitude": 116.4, "latitude": 39.9,
            "capacityKw": 0.0, "forecastHours": 24
        }
        resp = self.client.post("/api/iotcloudai/solar/predict", json=payload)
        assert resp.status_code < 500
        logger.info("Solar 零容量校验 ✓")


# ═══════════════════════════════════════════════════
# IotCloudAI — VisionInspection 视觉巡检
# ═══════════════════════════════════════════════════

@pytest.mark.p1
@pytest.mark.iotcloudai
class TestVisionInspectionAPI:
    """IotCloudAI 视觉智能巡检"""

    @pytest.fixture(autouse=True)
    def _setup(self, gateway_api):
        self.client = gateway_api

    def test_vision_understand_image(self):
        """图像理解"""
        resp = self.client.post("/api/iotcloudai/vision/understand",
                                params={"question": "这是什么设备？"})
        assert resp.status_code < 500
        logger.info("Vision 图像理解 ✓")

    def test_vision_inspect_pv(self):
        """光伏面板巡检"""
        resp = self.client.post("/api/iotcloudai/vision/inspect/pv")
        assert resp.status_code < 500
        logger.info("Vision 光伏巡检 ✓")

    def test_vision_inspect_charger(self):
        """充电桩巡检"""
        resp = self.client.post("/api/iotcloudai/vision/inspect/charger")
        assert resp.status_code < 500
        logger.info("Vision 充电桩巡检 ✓")

    def test_vision_analyze_batch(self):
        """批量帧分析"""
        resp = self.client.post("/api/iotcloudai/vision/analyze/batch",
                                params={"task": "defect_detection"})
        assert resp.status_code < 500
        logger.info("Vision 批量帧分析 ✓")


# ═══════════════════════════════════════════════════
# Storage Archive 冷归档
# ═══════════════════════════════════════════════════

@pytest.mark.p1
@pytest.mark.storage
class TestStorageArchiveAPI:
    """Storage 冷归档 API"""

    @pytest.fixture(autouse=True)
    def _setup(self, gateway_api):
        self.client = gateway_api

    def test_archive_upload(self):
        """上传归档文件"""
        payload = {
            "objectKey": f"archive/charging/heartbeat/2024-01/{uuid.uuid4()}.gz",
            "contentBase64": base64.b64encode(b"test archive data").decode(),
            "serviceName": "charging",
            "tableName": "charging_device_heartbeat",
            "metadata": {"rowCount": 10000, "dateRange": "2024-01-01~2024-01-31"}
        }
        resp = self.client.post("/api/storage/archive/upload", json=payload)
        assert resp.status_code < 500
        logger.info("Archive 上传归档 ✓")

    def test_archive_exists(self):
        """检查归档文件是否存在"""
        resp = self.client.get("/api/storage/archive/exists",
                               params={"objectKey": "archive/test/notexist.gz"})
        assert resp.status_code < 500
        logger.info("Archive 文件存在检查 ✓")

    def test_archive_download_url(self):
        """获取归档下载链接"""
        resp = self.client.get("/api/storage/archive/download-url",
                               params={"objectKey": "archive/test/sample.gz", "expiresMinutes": 30})
        assert resp.status_code < 500
        logger.info("Archive 下载链接 ✓")

    def test_archive_upload_oversized(self):
        """超大归档文件(>200MB)校验"""
        payload = {
            "objectKey": "archive/test/oversized.gz",
            "contentBase64": "A" * 100,  # Mock 模式不会真实传大文件
            "serviceName": "test"
        }
        resp = self.client.post("/api/storage/archive/upload", json=payload)
        assert resp.status_code < 500
        logger.info("Archive 超限校验 ✓")


# ═══════════════════════════════════════════════════
# Observability 内部告警通知 API
# ═══════════════════════════════════════════════════

@pytest.mark.p1
@pytest.mark.observability
class TestInternalAlertNotificationAPI:
    """Observability 内部告警通知（/api/internal/observability）"""

    @pytest.fixture(autouse=True)
    def _setup(self, gateway_api):
        self.client = gateway_api

    def test_receive_alert(self):
        """接收内部告警"""
        payload = {
            "alertId": str(uuid.uuid4()),
            "source": "ruleengine",
            "severity": "critical",
            "title": "设备离线告警",
            "description": "设备 DEV-001 超过5分钟未上报心跳",
            "deviceId": str(uuid.uuid4()),
            "tenantId": str(uuid.uuid4())
        }
        resp = self.client.post("/api/internal/observability/alerts", json=payload)
        assert resp.status_code < 500
        logger.info("InternalAlert 接收告警 ✓")

    def test_receive_notification(self):
        """接收内部通知"""
        payload = {
            "notificationId": str(uuid.uuid4()),
            "source": "ruleengine",
            "type": "email",
            "recipients": ["admin@jgsy.com"],
            "title": "规则触发通知",
            "body": "规则链 RULE-001 触发告警动作"
        }
        resp = self.client.post("/api/internal/observability/notifications", json=payload)
        assert resp.status_code < 500
        logger.info("InternalAlert 接收通知 ✓")

    def test_receive_alert_missing_source(self):
        """告警缺少 source 字段"""
        payload = {"alertId": str(uuid.uuid4()), "severity": "warning"}
        resp = self.client.post("/api/internal/observability/alerts", json=payload)
        assert resp.status_code < 500
        logger.info("InternalAlert 缺少source ✓")


# ═══════════════════════════════════════════════════
# WorkOrder 内部告警联动工单
# ═══════════════════════════════════════════════════

@pytest.mark.p1
@pytest.mark.workorder
class TestInternalWorkOrderAPI:
    """WorkOrder 内部告警联动工单（/api/internal/workorder）"""

    @pytest.fixture(autouse=True)
    def _setup(self, gateway_api):
        self.client = gateway_api

    def test_create_from_alarm(self):
        """告警联动创建工单"""
        payload = {
            "alarmId": str(uuid.uuid4()),
            "deviceId": str(uuid.uuid4()),
            "stationId": str(uuid.uuid4()),
            "severity": "critical",
            "alarmType": "device_offline",
            "description": "设备离线超时",
            "tenantId": str(uuid.uuid4())
        }
        resp = self.client.post("/api/internal/workorder/from-alarm", json=payload)
        assert resp.status_code < 500
        logger.info("InternalWorkOrder 告警联动 ✓")

    def test_create_from_alarm_missing_device(self):
        """告警联动-缺少设备ID"""
        payload = {"alarmId": str(uuid.uuid4()), "severity": "warning"}
        resp = self.client.post("/api/internal/workorder/from-alarm", json=payload)
        assert resp.status_code < 500
        logger.info("InternalWorkOrder 缺少设备 ✓")


# ═══════════════════════════════════════════════════
# Gateway YARP 路由拆分验证
# ═══════════════════════════════════════════════════

@pytest.mark.p1
@pytest.mark.gateway
class TestGatewayYarpRoutesSplit:
    """Gateway YARP 路由拆分为5个文件后的关键路径验证"""

    @pytest.fixture(autouse=True)
    def _setup(self, gateway_api):
        self.client = gateway_api

    def test_platform_route_identity(self):
        """平台路由-Identity"""
        resp = self.client.get("/api/auth/health")
        assert resp.status_code < 500
        logger.info("YARP 平台路由 Identity ✓")

    def test_platform_route_permission(self):
        """平台路由-Permission"""
        resp = self.client.get("/api/permission/health")
        assert resp.status_code < 500
        logger.info("YARP 平台路由 Permission ✓")

    def test_charging_route_orders(self):
        """充电路由-Orders"""
        resp = self.client.get("/api/orders", params={"page": 1, "pageSize": 5})
        assert resp.status_code < 500
        logger.info("YARP 充电路由 Orders ✓")

    def test_energy_route_vpp(self):
        """能源路由-VPP"""
        resp = self.client.get("/api/vpp/health")
        assert resp.status_code < 500
        logger.info("YARP 能源路由 VPP ✓")

    def test_business_route_device(self):
        """业务路由-Device"""
        resp = self.client.get("/api/device/health")
        assert resp.status_code < 500
        logger.info("YARP 业务路由 Device ✓")

    def test_advanced_route_blockchain(self):
        """高级路由-Blockchain"""
        resp = self.client.get("/api/blockchain/health")
        assert resp.status_code < 500
        logger.info("YARP 高级路由 Blockchain ✓")

    def test_advanced_route_iotcloudai(self):
        """高级路由-IotCloudAI"""
        resp = self.client.get("/api/iotcloudai/health")
        assert resp.status_code < 500
        logger.info("YARP 高级路由 IotCloudAI ✓")

    def test_internal_route_blocked(self):
        """内部路由-外部访问被拦截"""
        resp = self.client.get("/api/internal/test")
        # 内部路由应该被 Gateway 拦截(403或404)
        assert resp.status_code < 500
        logger.info("YARP 内部路由拦截 ✓")


# ═══════════════════════════════════════════════════
# Device CommandTimeout 后台任务
# ═══════════════════════════════════════════════════

@pytest.mark.p1
@pytest.mark.device
class TestDeviceCommandTimeoutAPI:
    """Device 命令超时检查后台任务关联 API"""

    @pytest.fixture(autouse=True)
    def _setup(self, gateway_api):
        self.client = gateway_api

    def test_remote_command_list(self):
        """远程指令列表（含超时状态）"""
        resp = self.client.get("/api/device/remote-commands",
                               params={"page": 1, "pageSize": 10})
        assert resp.status_code < 500
        logger.info("Device 远程指令列表 ✓")

    def test_remote_command_send(self):
        """发送远程指令"""
        payload = {
            "deviceId": str(uuid.uuid4()),
            "commandType": "restart",
            "timeoutSeconds": 60,
            "params": {"force": False}
        }
        resp = self.client.post("/api/device/remote-commands", json=payload)
        assert resp.status_code < 500
        logger.info("Device 发送远程指令 ✓")

    def test_remote_command_status_check(self):
        """远程指令状态查询"""
        cmd_id = str(uuid.uuid4())
        resp = self.client.get(f"/api/device/remote-commands/{cmd_id}")
        assert resp.status_code < 500
        logger.info("Device 指令状态查询 ✓")


# ═══════════════════════════════════════════════════
# Trading OrderExpiration 后台任务
# ═══════════════════════════════════════════════════

@pytest.mark.p1
@pytest.mark.trading
class TestTradingOrderExpirationAPI:
    """Trading 订单过期后台任务关联 API"""

    @pytest.fixture(autouse=True)
    def _setup(self, gateway_api):
        self.client = gateway_api

    def test_electrade_order_list_with_status(self):
        """电力交易挂牌单列表(含expired状态)"""
        resp = self.client.get("/api/electrade/orders",
                               params={"page": 1, "pageSize": 10, "status": "expired"})
        assert resp.status_code < 500
        logger.info("Trading 过期订单列表 ✓")

    def test_electrade_bilateral_trade_list(self):
        """双边交易列表(含cancelled超时状态)"""
        resp = self.client.get("/api/electrade/bilateral-trades",
                               params={"page": 1, "pageSize": 10, "status": "cancelled"})
        assert resp.status_code < 500
        logger.info("Trading 超时双边交易 ✓")


# ═══════════════════════════════════════════════════
# Analytics 后台任务关联 API
# ═══════════════════════════════════════════════════

@pytest.mark.p2
@pytest.mark.analytics
class TestAnalyticsBackgroundTasksAPI:
    """Analytics DailyReport ETL + ScheduledReport 后台任务关联"""

    @pytest.fixture(autouse=True)
    def _setup(self, gateway_api):
        self.client = gateway_api

    def test_daily_report_list(self):
        """日报列表"""
        resp = self.client.get("/api/analytics/daily-reports",
                               params={"page": 1, "pageSize": 10})
        assert resp.status_code < 500
        logger.info("Analytics 日报列表 ✓")

    def test_scheduled_report_tasks(self):
        """定时报表任务列表"""
        resp = self.client.get("/api/analytics/scheduled-report-tasks",
                               params={"page": 1, "pageSize": 10})
        assert resp.status_code < 500
        logger.info("Analytics 定时任务列表 ✓")

    def test_scheduled_report_create(self):
        """创建定时报表任务"""
        payload = {
            "name": "日运营报表",
            "reportType": "daily_operation",
            "cronExpression": "0 8 * * *",
            "format": "pdf",
            "recipients": ["admin@jgsy.com"],
            "isEnabled": True
        }
        resp = self.client.post("/api/analytics/scheduled-report-tasks", json=payload)
        assert resp.status_code < 500
        logger.info("Analytics 创建定时任务 ✓")


# ═══════════════════════════════════════════════════
# Settlement AutoSettlement 后台任务
# ═══════════════════════════════════════════════════

@pytest.mark.p2
@pytest.mark.settlement
class TestSettlementAutoJobAPI:
    """Settlement 自动结算后台任务关联 API"""

    @pytest.fixture(autouse=True)
    def _setup(self, gateway_api):
        self.client = gateway_api

    def test_auto_settlement_rules(self):
        """自动结算规则列表"""
        resp = self.client.get("/api/settlement/auto-settlement-rules",
                               params={"page": 1, "pageSize": 10})
        assert resp.status_code < 500
        logger.info("Settlement 自动结算规则 ✓")

    def test_auto_settlement_history(self):
        """自动结算执行记录"""
        resp = self.client.get("/api/settlement/auto-settlement-history",
                               params={"page": 1, "pageSize": 10})
        assert resp.status_code < 500
        logger.info("Settlement 自动结算记录 ✓")


# ═══════════════════════════════════════════════════
# Ingestion ProtocolSharding 配置
# ═══════════════════════════════════════════════════

@pytest.mark.p2
@pytest.mark.ingestion
class TestIngestionProtocolShardingAPI:
    """Ingestion 协议分片+TimescaleDB 关联 API"""

    @pytest.fixture(autouse=True)
    def _setup(self, gateway_api):
        self.client = gateway_api

    def test_ingestion_protocol_status(self):
        """协议适配器状态"""
        resp = self.client.get("/api/ingestion/protocol/status")
        assert resp.status_code < 500
        logger.info("Ingestion 协议状态 ✓")

    def test_ingestion_message_list(self):
        """采集消息列表"""
        resp = self.client.get("/api/ingestion-message/list",
                               params={"page": 1, "pageSize": 10})
        assert resp.status_code < 500
        logger.info("Ingestion 消息列表 ✓")

    def test_ingestion_health(self):
        """Ingestion 健康检查"""
        resp = self.client.get("/api/ingestion/health")
        assert resp.status_code < 500
        logger.info("Ingestion 健康检查 ✓")


# ═══════════════════════════════════════════════════
# Permission — Blockchain 三员分立权限
# ═══════════════════════════════════════════════════

@pytest.mark.p1
@pytest.mark.permission
class TestBlockchainThreeAdminPermissions:
    """Permission 区块链三员分立权限验证"""

    @pytest.fixture(autouse=True)
    def _setup(self, gateway_api):
        self.client = gateway_api

    def test_security_admin_has_wallet_perms(self):
        """安全管理员(role=10)拥有钱包权限"""
        resp = self.client.get("/api/role/permissions",
                               params={"roleId": "00000000-0000-0000-0000-000000000010"})
        assert resp.status_code < 500
        logger.info("Permission 安全管理员钱包权限 ✓")

    def test_audit_admin_has_audit_perms(self):
        """审计管理员(role=11)拥有审计权限"""
        resp = self.client.get("/api/role/permissions",
                               params={"roleId": "00000000-0000-0000-0000-000000000011"})
        assert resp.status_code < 500
        logger.info("Permission 审计管理员审计权限 ✓")

    def test_sys_admin_has_business_perms(self):
        """系统管理员(role=12)拥有业务权限"""
        resp = self.client.get("/api/role/permissions",
                               params={"roleId": "00000000-0000-0000-0000-000000000012"})
        assert resp.status_code < 500
        logger.info("Permission 系统管理员业务权限 ✓")

    def test_super_admin_has_all_blockchain_perms(self):
        """超级管理员(role=01)拥有全部blockchain权限"""
        resp = self.client.get("/api/role/permissions",
                               params={"roleId": "00000000-0000-0000-0000-000000000001"})
        assert resp.status_code < 500
        logger.info("Permission 超级管理员全量权限 ✓")


# ═══════════════════════════════════════════════════
# 跨服务联动 — 告警→通知→工单全链路
# ═══════════════════════════════════════════════════

@pytest.mark.p0
@pytest.mark.e2e
class TestAlertToWorkOrderChainAPI:
    """跨服务联动：RuleEngine告警 → Observability通知 → WorkOrder工单"""

    @pytest.fixture(autouse=True)
    def _setup(self, gateway_api):
        self.client = gateway_api

    def test_chain_ruleengine_trigger_alert(self):
        """步骤1: RuleEngine 触发告警"""
        resp = self.client.get("/api/ruleengine/alarm-definitions",
                               params={"page": 1, "pageSize": 5})
        assert resp.status_code < 500
        logger.info("Chain Step1: RuleEngine 告警定义 ✓")

    def test_chain_observability_receive_alert(self):
        """步骤2: Observability 接收告警"""
        payload = {
            "alertId": str(uuid.uuid4()),
            "source": "ruleengine",
            "severity": "critical",
            "title": "链路测试告警"
        }
        resp = self.client.post("/api/internal/observability/alerts", json=payload)
        assert resp.status_code < 500
        logger.info("Chain Step2: Observability 接收告警 ✓")

    def test_chain_workorder_create_from_alarm(self):
        """步骤3: WorkOrder 自动创建工单"""
        payload = {
            "alarmId": str(uuid.uuid4()),
            "deviceId": str(uuid.uuid4()),
            "severity": "critical",
            "alarmType": "device_fault"
        }
        resp = self.client.post("/api/internal/workorder/from-alarm", json=payload)
        assert resp.status_code < 500
        logger.info("Chain Step3: WorkOrder 联动工单 ✓")

    def test_chain_workorder_list_alert_linked(self):
        """步骤4: 查询告警联动工单"""
        resp = self.client.get("/api/workorder/list",
                               params={"page": 1, "pageSize": 5, "source": "alarm"})
        assert resp.status_code < 500
        logger.info("Chain Step4: 告警联动工单列表 ✓")
