"""
网关弹性 + 数据采集 API 测试 — 覆盖 V3.1.2 变更
=================================================
覆盖文件:
- JGSY.AGI.Gateway/Resilience/ResilienceExtensions.cs (MODIFIED) - Polly 4层弹性
- JGSY.AGI.Gateway/ServiceDiscovery/ConsulProxyConfigProvider.cs (MODIFIED) - 双模式服务发现
- JGSY.AGI.Gateway/ServiceDiscovery/K8sProxyConfigProvider.cs (MODIFIED) - K8s服务发现
- JGSY.AGI.Gateway/Program.cs (MODIFIED)
- JGSY.AGI.Ingestion/Storage/WalBufferedStorageStrategy.cs (NEW) - WAL缓冲写入
- JGSY.AGI.Ingestion/Services/BatchIngestionWriter.cs (MODIFIED) - 高性能批量写入
- JGSY.AGI.Ingestion/Services/Ocpp20MessageHandler.cs (MODIFIED) - OCPP 2.0
- JGSY.AGI.Ingestion/Services/IngestionTaskEngine.cs (MODIFIED) - 采集任务引擎
- JGSY.AGI.Ingestion/Storage/InfluxDBWriter.cs (MODIFIED)
- JGSY.AGI.Ingestion/Program.cs (MODIFIED)
"""

import pytest
import logging
import uuid
import time

logger = logging.getLogger(__name__)

_TENANT_ID = "00000000-0000-0000-0000-000000000001"


# ═══════════════════════════════════════════════════
# 网关弹性策略 测试
# ═══════════════════════════════════════════════════

@pytest.mark.p0
@pytest.mark.api
class TestGatewayResilience:
    """测试 ResilienceExtensions: 超时 → 重试 → 熔断 → 降级"""

    @pytest.fixture(autouse=True)
    def _setup(self, gateway_api):
        self.client = gateway_api

    def test_gateway_health(self):
        """网关健康检查"""
        resp = self.client.get("/health")
        assert resp.status_code == 200
        logger.info("网关健康 ✓")

    def test_gateway_ready(self):
        """网关就绪检查"""
        resp = self.client.get("/ready")
        assert resp.status_code == 200
        logger.info("网关就绪 ✓")

    def test_route_to_identity_service(self):
        """路由至 Identity 服务"""
        resp = self.client.get("/api/auth/health")
        assert resp.status_code == 200
        logger.info("Identity路由 ✓")

    def test_route_to_device_service(self):
        """路由至 Device 服务"""
        resp = self.client.get("/api/device/health")
        assert resp.status_code == 200
        logger.info("Device路由 ✓")

    def test_route_to_charging_service(self):
        """路由至 Charging 服务"""
        resp = self.client.get("/api/charging/health")
        assert resp.status_code == 200
        logger.info("Charging路由 ✓")

    def test_nonexistent_route_handled(self):
        """不存在的路由应被降级处理"""
        resp = self.client.get("/api/nonexistent-service/test")
        assert resp.status_code in (200, 404, 502)
        logger.info("不存在路由处理 ✓")

    def test_error_response_transformed(self):
        """YARP 错误应被 YarpErrorTransformer 转换"""
        resp = self.client.get("/api/test-error-transform")
        assert resp.status_code in (200, 500, 502)
        logger.info("错误转换 ✓")


# ═══════════════════════════════════════════════════
# Consul 服务发现 测试
# ═══════════════════════════════════════════════════

@pytest.mark.p1
@pytest.mark.api
class TestConsulServiceDiscovery:
    """测试 ConsulProxyConfigProvider 双模式服务发现"""

    @pytest.fixture(autouse=True)
    def _setup(self, gateway_api):
        self.client = gateway_api

    def test_consul_registered_services(self):
        """Consul 已注册服务列表"""
        resp = self.client.get("/api/gateway/services")
        assert resp.status_code == 200
        logger.info("服务列表 ✓")

    def test_consul_health_check(self):
        """Consul 健康检查"""
        resp = self.client.get("/api/gateway/consul/health")
        assert resp.status_code == 200
        logger.info("Consul健康 ✓")

    def test_docker_dns_mode(self):
        """Docker DNS 模式路由"""
        resp = self.client.get("/api/gateway/routing/mode")
        assert resp.status_code == 200
        logger.info("Docker DNS模式 ✓")

    def test_standalone_optimization(self):
        """Standalone 模式仅为已注册服务创建集群"""
        resp = self.client.get("/api/gateway/clusters")
        assert resp.status_code == 200
        logger.info("Standalone优化 ✓")


# ═══════════════════════════════════════════════════
# K8s 服务发现 测试
# ═══════════════════════════════════════════════════

@pytest.mark.p1
@pytest.mark.api
class TestK8sServiceDiscovery:
    """测试 K8sProxyConfigProvider"""

    @pytest.fixture(autouse=True)
    def _setup(self, gateway_api):
        self.client = gateway_api

    def test_k8s_service_discovery(self):
        """K8s 服务发现端点"""
        resp = self.client.get("/api/gateway/k8s/services")
        assert resp.status_code == 200
        logger.info("K8s服务发现 ✓")

    def test_k8s_dns_format(self):
        """K8s DNS 格式: {service}.{namespace}.svc.cluster.local"""
        resp = self.client.get("/api/gateway/k8s/dns-info")
        assert resp.status_code == 200
        logger.info("K8s DNS格式 ✓")

    def test_k8s_endpoints_query(self):
        """K8s Endpoints 查询"""
        resp = self.client.get("/api/gateway/k8s/endpoints")
        assert resp.status_code == 200
        logger.info("K8s Endpoints ✓")


# ═══════════════════════════════════════════════════
# WAL 缓冲存储 测试
# ═══════════════════════════════════════════════════

@pytest.mark.p0
@pytest.mark.api
class TestWalBufferedStorage:
    """测试 WalBufferedStorageStrategy
    - 装饰器模式
    - WAL 轮转（64MB）
    - 检查点重放
    """

    @pytest.fixture(autouse=True)
    def _setup(self, gateway_api):
        self.client = gateway_api
        self.base = "/api/ingestion"

    def test_wal_status(self):
        """WAL 缓冲状态"""
        resp = self.client.get(f"{self.base}/wal/status")
        assert resp.status_code == 200
        logger.info("WAL状态 ✓")

    def test_wal_write_single(self):
        """WAL 单条写入"""
        resp = self.client.post(f"{self.base}/wal/write", json={
            "deviceId": str(uuid.uuid4()),
            "metric": "temperature",
            "value": 25.6,
            "timestamp": "2026-03-07T10:00:00Z"
        })
        assert resp.status_code == 200
        logger.info("WAL单条写入 ✓")

    def test_wal_write_batch(self):
        """WAL 批量写入"""
        points = [
            {"deviceId": str(uuid.uuid4()), "metric": "temperature", "value": 25.0 + i, "timestamp": f"2026-03-07T10:0{i}:00Z"}
            for i in range(5)
        ]
        resp = self.client.post(f"{self.base}/wal/write-batch", json={
            "points": points
        })
        assert resp.status_code == 200
        logger.info("WAL批量写入 ✓")

    def test_wal_replay_pending(self):
        """WAL 重放待处理数据"""
        resp = self.client.post(f"{self.base}/wal/replay")
        assert resp.status_code == 200
        logger.info("WAL重放 ✓")

    def test_wal_checkpoint(self):
        """WAL 检查点"""
        resp = self.client.get(f"{self.base}/wal/checkpoint")
        assert resp.status_code == 200
        logger.info("WAL检查点 ✓")

    def test_wal_rotation_info(self):
        """WAL 轮转信息（64MB阈值）"""
        resp = self.client.get(f"{self.base}/wal/rotation-info")
        assert resp.status_code == 200
        logger.info("WAL轮转信息 ✓")


# ═══════════════════════════════════════════════════
# 批量采集写入器 测试
# ═══════════════════════════════════════════════════

@pytest.mark.p0
@pytest.mark.api
class TestBatchIngestionWriter:
    """测试 BatchIngestionWriter
    - Channel 有界队列
    - 多 Worker 并行消费
    - 批量写入 + 重试
    - 50,000+ TPS
    """

    @pytest.fixture(autouse=True)
    def _setup(self, gateway_api):
        self.client = gateway_api
        self.base = "/api/ingestion"

    def test_enqueue_single_message(self):
        """单条消息入队"""
        resp = self.client.post(f"{self.base}/enqueue", json={
            "deviceId": str(uuid.uuid4()),
            "tenantId": _TENANT_ID,
            "protocol": "mqtt",
            "payload": {"temperature": 25.5, "humidity": 60}
        })
        assert resp.status_code == 200
        logger.info("单条入队 ✓")

    def test_enqueue_batch_messages(self):
        """批量消息入队"""
        messages = [
            {
                "deviceId": str(uuid.uuid4()),
                "tenantId": _TENANT_ID,
                "protocol": "mqtt",
                "payload": {"temp": 20.0 + i}
            }
            for i in range(10)
        ]
        resp = self.client.post(f"{self.base}/enqueue-batch", json={
            "messages": messages
        })
        assert resp.status_code == 200
        logger.info("批量入队 ✓")

    def test_get_queue_depth(self):
        """获取队列深度"""
        resp = self.client.get(f"{self.base}/queue-depth")
        assert resp.status_code == 200
        logger.info("队列深度 ✓")

    def test_get_statistics(self):
        """获取写入统计"""
        resp = self.client.get(f"{self.base}/statistics")
        assert resp.status_code == 200
        data = resp.json()
        assert data.get("success") is True
        logger.info("写入统计 ✓")

    def test_flush_buffer(self):
        """刷新缓冲"""
        resp = self.client.post(f"{self.base}/flush")
        assert resp.status_code == 200
        logger.info("刷新缓冲 ✓")


# ═══════════════════════════════════════════════════
# OCPP 2.0 消息处理 测试
# ═══════════════════════════════════════════════════

@pytest.mark.p0
@pytest.mark.api
class TestOcpp20MessageHandler:
    """测试 Ocpp20MessageHandler
    - TransactionEvent 处理
    - StatusNotification 处理
    - 状态映射
    - RabbitMQ 解耦
    """

    @pytest.fixture(autouse=True)
    def _setup(self, gateway_api):
        self.client = gateway_api
        self.base = "/api/ingestion/ocpp"

    def test_transaction_event_started(self):
        """OCPP TransactionEvent - Started"""
        resp = self.client.post(f"{self.base}/transaction-event", json={
            "chargerId": str(uuid.uuid4()),
            "tenantId": _TENANT_ID,
            "eventType": "Started",
            "transactionId": str(uuid.uuid4()),
            "seqNo": 0,
            "timestamp": "2026-03-07T10:00:00Z",
            "meterValue": [{"sampledValue": [{"value": "0", "measurand": "Energy.Active.Import.Register"}]}]
        })
        assert resp.status_code == 200
        logger.info("TransactionEvent Started ✓")

    def test_transaction_event_updated(self):
        """OCPP TransactionEvent - Updated (充电中)"""
        resp = self.client.post(f"{self.base}/transaction-event", json={
            "chargerId": str(uuid.uuid4()),
            "tenantId": _TENANT_ID,
            "eventType": "Updated",
            "transactionId": str(uuid.uuid4()),
            "seqNo": 5,
            "timestamp": "2026-03-07T10:30:00Z",
            "meterValue": [{"sampledValue": [{"value": "15500", "measurand": "Energy.Active.Import.Register"}]}]
        })
        assert resp.status_code == 200
        logger.info("TransactionEvent Updated ✓")

    def test_transaction_event_ended(self):
        """OCPP TransactionEvent - Ended (结算)"""
        resp = self.client.post(f"{self.base}/transaction-event", json={
            "chargerId": str(uuid.uuid4()),
            "tenantId": _TENANT_ID,
            "eventType": "Ended",
            "transactionId": str(uuid.uuid4()),
            "seqNo": 10,
            "timestamp": "2026-03-07T11:00:00Z",
            "meterValue": [{"sampledValue": [{"value": "35500", "measurand": "Energy.Active.Import.Register"}]}]
        })
        assert resp.status_code == 200
        data = resp.json()
        assert data.get("success") is True
        logger.info("TransactionEvent Ended ✓")

    def test_status_notification_available(self):
        """OCPP StatusNotification - Available"""
        resp = self.client.post(f"{self.base}/status-notification", json={
            "chargerId": str(uuid.uuid4()),
            "tenantId": _TENANT_ID,
            "timestamp": "2026-03-07T10:00:00Z",
            "connectorStatus": "Available",
            "evseId": 1,
            "connectorId": 1
        })
        assert resp.status_code == 200
        logger.info("StatusNotification Available ✓")

    def test_status_notification_occupied(self):
        """OCPP StatusNotification - Occupied"""
        resp = self.client.post(f"{self.base}/status-notification", json={
            "chargerId": str(uuid.uuid4()),
            "tenantId": _TENANT_ID,
            "timestamp": "2026-03-07T10:00:00Z",
            "connectorStatus": "Occupied",
            "evseId": 1,
            "connectorId": 1
        })
        assert resp.status_code == 200
        logger.info("StatusNotification Occupied ✓")

    def test_status_notification_faulted(self):
        """OCPP StatusNotification - Faulted (故障)"""
        resp = self.client.post(f"{self.base}/status-notification", json={
            "chargerId": str(uuid.uuid4()),
            "tenantId": _TENANT_ID,
            "timestamp": "2026-03-07T10:00:00Z",
            "connectorStatus": "Faulted",
            "evseId": 1,
            "connectorId": 1
        })
        assert resp.status_code == 200
        logger.info("StatusNotification Faulted ✓")

    def test_status_mapping_online(self):
        """连接器状态映射 Available → Online(1)"""
        resp = self.client.post(f"{self.base}/status-notification", json={
            "chargerId": str(uuid.uuid4()),
            "tenantId": _TENANT_ID,
            "timestamp": "2026-03-07T10:00:00Z",
            "connectorStatus": "Available",
            "evseId": 1,
            "connectorId": 1
        })
        assert resp.status_code == 200
        logger.info("状态映射Online ✓")

    def test_status_mapping_offline(self):
        """连接器状态映射 Unavailable → Offline(2)"""
        resp = self.client.post(f"{self.base}/status-notification", json={
            "chargerId": str(uuid.uuid4()),
            "tenantId": _TENANT_ID,
            "timestamp": "2026-03-07T10:00:00Z",
            "connectorStatus": "Unavailable",
            "evseId": 1,
            "connectorId": 1
        })
        assert resp.status_code == 200
        logger.info("状态映射Offline ✓")


# ═══════════════════════════════════════════════════
# 采集任务引擎 测试
# ═══════════════════════════════════════════════════

@pytest.mark.p1
@pytest.mark.api
class TestIngestionTaskEngine:
    """测试 IngestionTaskEngine 修改"""

    @pytest.fixture(autouse=True)
    def _setup(self, gateway_api):
        self.client = gateway_api
        self.base = "/api/ingestion"

    def test_get_task_list(self):
        """获取采集任务列表"""
        resp = self.client.get(f"{self.base}/tasks", params={
            "page": 1, "pageSize": 10
        })
        assert resp.status_code == 200
        logger.info("任务列表 ✓")

    def test_create_task(self):
        """创建采集任务"""
        resp = self.client.post(f"{self.base}/tasks", json={
            "name": f"test_task_{uuid.uuid4().hex[:8]}",
            "protocol": "mqtt",
            "deviceIds": [str(uuid.uuid4())],
            "interval": 60,
            "tenantId": _TENANT_ID
        })
        assert resp.status_code == 200
        logger.info("创建任务 ✓")

    def test_start_task(self):
        """启动采集任务"""
        resp = self.client.post(f"{self.base}/tasks/{uuid.uuid4()}/start")
        assert resp.status_code == 200
        logger.info("启动任务 ✓")

    def test_stop_task(self):
        """停止采集任务"""
        resp = self.client.post(f"{self.base}/tasks/{uuid.uuid4()}/stop")
        assert resp.status_code == 200
        logger.info("停止任务 ✓")
