"""
═══════════════════════════════════════════════════════════════════════════════
JGSY.AGI 双端部署合规测试套件
═══════════════════════════════════════════════════════════════════════════════
覆盖范围：
  - IotCloudAI 双端部署（Cloud/Edge）架构合规
  - 边缘 Compose 命名规范
  - 安全分区（Zone I/II/III/IV）
  - 共享部署模式抽象
  - 基础设施完整性（ClamAV 等）
标准：GB/T 36572 + GB/T 44241-2024
"""

import os
import re
import json
import glob
import yaml
import pytest
from pathlib import Path

WORKSPACE = os.environ.get("WORKSPACE_DIR", r"D:\2026\aiops.v2")


# ═══════════════════════════════════════════════════════════════════════════════
# 1. 共享部署模式抽象
# ═══════════════════════════════════════════════════════════════════════════════

class TestSharedDeploymentAbstraction:
    """共享部署模式抽象测试"""

    def test_deployment_mode_file_exists(self):
        """DeploymentMode.cs 共享抽象文件存在"""
        f = os.path.join(WORKSPACE, "JGSY.AGI.Common.Abstractions", "Deployment", "DeploymentMode.cs")
        assert os.path.exists(f), "DeploymentMode.cs 缺失"

    def test_deployment_mode_enum(self):
        """DeploymentMode 枚举定义 Cloud/Edge"""
        f = os.path.join(WORKSPACE, "JGSY.AGI.Common.Abstractions", "Deployment", "DeploymentMode.cs")
        content = Path(f).read_text(encoding="utf-8")
        assert "enum DeploymentMode" in content, "DeploymentMode 枚举缺失"
        assert "Cloud" in content, "DeploymentMode.Cloud 缺失"
        assert "Edge" in content, "DeploymentMode.Edge 缺失"

    def test_security_zone_enum(self):
        """SecurityZone 枚举定义四个分区"""
        f = os.path.join(WORKSPACE, "JGSY.AGI.Common.Abstractions", "Deployment", "DeploymentMode.cs")
        content = Path(f).read_text(encoding="utf-8")
        assert "enum SecurityZone" in content, "SecurityZone 枚举缺失"
        assert "ZoneI_Realtime" in content, "Ⅰ区定义缺失"
        assert "ZoneII_Control" in content, "Ⅱ区定义缺失"
        assert "ZoneIII_Management" in content, "Ⅲ区定义缺失"
        assert "ZoneIV_External" in content, "Ⅳ区定义缺失"

    def test_edge_mode_base_options(self):
        """EdgeModeBaseOptions 基类配置"""
        f = os.path.join(WORKSPACE, "JGSY.AGI.Common.Abstractions", "Deployment", "DeploymentMode.cs")
        content = Path(f).read_text(encoding="utf-8")
        assert "class EdgeModeBaseOptions" in content, "EdgeModeBaseOptions 缺失"
        for prop in ["Enabled", "Zone", "StationId", "CloudEndpoint"]:
            assert prop in content, f"EdgeModeBaseOptions.{prop} 属性缺失"

    def test_deployment_mode_provider_interface(self):
        """IDeploymentModeProvider 接口"""
        f = os.path.join(WORKSPACE, "JGSY.AGI.Common.Abstractions", "Deployment", "DeploymentMode.cs")
        content = Path(f).read_text(encoding="utf-8")
        assert "interface IDeploymentModeProvider" in content, "IDeploymentModeProvider 接口缺失"
        assert "IsEdgeMode" in content, "IsEdgeMode 属性缺失"
        assert "IsCloudMode" in content, "IsCloudMode 属性缺失"

    def test_default_provider_implementation(self):
        """DefaultDeploymentModeProvider 默认实现"""
        f = os.path.join(WORKSPACE, "JGSY.AGI.Common.Abstractions", "Deployment", "DeploymentMode.cs")
        content = Path(f).read_text(encoding="utf-8")
        assert "class DefaultDeploymentModeProvider" in content, "默认实现缺失"
        assert "IDeploymentModeProvider" in content, "未实现接口"


# ═══════════════════════════════════════════════════════════════════════════════
# 2. IotCloudAI 双端部署架构
# ═══════════════════════════════════════════════════════════════════════════════

class TestIotCloudAIDualDeployment:
    """IotCloudAI 双端部署架构测试"""

    def test_edge_module_exists(self):
        """IotCloudAI Edge 模块目录存在"""
        edge_dir = os.path.join(WORKSPACE, "JGSY.AGI.IotCloudAI", "Edge")
        assert os.path.isdir(edge_dir), "Edge 模块目录缺失"

    def test_edge_module_files(self):
        """Edge 模块核心文件完整"""
        edge_dir = os.path.join(WORKSPACE, "JGSY.AGI.IotCloudAI", "Edge")
        required_files = [
            "EdgeModeOptions.cs",
            "EdgeServiceExtensions.cs",
            "EdgeStatusController.cs",
            "EdgeDataRepository.cs",
            "SqliteConnectionFactory.cs",
            "OfflineModeManager.cs",
            "MqttDeviceCollector.cs",
            "CloudEdgeSyncService.cs",
            "EdgeHealthAssessmentWorker.cs",
            "EdgeDataCleanupWorker.cs",
        ]
        for f in required_files:
            assert os.path.exists(os.path.join(edge_dir, f)), f"Edge 模块文件缺失: {f}"

    def test_edge_mode_options_complete(self):
        """EdgeModeOptions 配置类完整"""
        f = os.path.join(WORKSPACE, "JGSY.AGI.IotCloudAI", "Edge", "EdgeModeOptions.cs")
        content = Path(f).read_text(encoding="utf-8")
        assert "class EdgeModeOptions" in content
        for field in ["NodeId", "CloudEndpoint", "Offline", "Sync", "Mqtt", "Inference"]:
            assert field in content, f"EdgeModeOptions.{field} 缺失"

    def test_program_dual_mode_detection(self):
        """Program.cs 双端模式检测"""
        f = os.path.join(WORKSPACE, "JGSY.AGI.IotCloudAI", "Program.cs")
        content = Path(f).read_text(encoding="utf-8")
        assert 'EdgeMode:Enabled' in content, "边缘模式检测配置键缺失"
        assert 'DeploymentMode' in content, "DeploymentMode 标准命名缺失"

    def test_cloud_mode_services(self):
        """云端模式服务注册（PostgreSQL/Redis/Consul/RabbitMQ）"""
        f = os.path.join(WORKSPACE, "JGSY.AGI.IotCloudAI", "Program.cs")
        content = Path(f).read_text(encoding="utf-8")
        assert "NpgsqlConnectionFactory" in content, "云端 PostgreSQL 注册缺失"
        assert "StackExchangeRedisCache" in content or "AddStackExchangeRedisCache" in content, "云端 Redis 注册缺失"
        assert "AddConsulServiceRegistration" in content, "云端 Consul 注册缺失"
        assert "ProtocolBridgeWorker" in content or "IngestionProtocolBridgeWorker" in content, "云端 RabbitMQ 桥接缺失"

    def test_edge_mode_services(self):
        """边缘模式服务注册（SQLite/MemoryCache/MQTT/离线管理）"""
        ext_file = os.path.join(WORKSPACE, "JGSY.AGI.IotCloudAI", "Edge", "EdgeServiceExtensions.cs")
        content = Path(ext_file).read_text(encoding="utf-8")
        assert "SqliteConnectionFactory" in content, "边缘 SQLite 注册缺失"
        assert "AddDistributedMemoryCache" in content, "边缘内存缓存注册缺失"
        assert "MqttDeviceCollector" in content, "边缘 MQTT 采集注册缺失"
        assert "OfflineModeManager" in content, "离线管理器注册缺失"
        assert "CloudEdgeSyncService" in content, "云边同步注册缺失"

    def test_sqlite_dependency(self):
        """边缘模式 SQLite 依赖"""
        csproj = os.path.join(WORKSPACE, "JGSY.AGI.IotCloudAI", "JGSY.AGI.IotCloudAI.csproj")
        content = Path(csproj).read_text(encoding="utf-8")
        assert "Microsoft.Data.Sqlite" in content, "SQLite NuGet 包依赖缺失"

    def test_mqtt_dependency(self):
        """边缘模式 MQTT 依赖"""
        csproj = os.path.join(WORKSPACE, "JGSY.AGI.IotCloudAI", "JGSY.AGI.IotCloudAI.csproj")
        content = Path(csproj).read_text(encoding="utf-8")
        assert "MQTTnet" in content, "MQTTnet 包依赖缺失"

    def test_appsettings_edge_config(self):
        """appsettings.json 包含 EdgeMode 完整配置"""
        f = os.path.join(WORKSPACE, "JGSY.AGI.IotCloudAI", "appsettings.json")
        config = json.loads(Path(f).read_text(encoding="utf-8-sig"))
        edge = config.get("EdgeMode", {})
        assert "Enabled" in edge, "EdgeMode.Enabled 缺失"
        assert "Offline" in edge or "Sync" in edge, "EdgeMode 子配置缺失"


# ═══════════════════════════════════════════════════════════════════════════════
# 3. 边缘 Compose 命名规范
# ═══════════════════════════════════════════════════════════════════════════════

class TestEdgeComposeNaming:
    """边缘 Compose 命名规范测试"""

    @pytest.fixture
    def edge_compose(self):
        f = os.path.join(WORKSPACE, "Configuration2.0", "docker", "docker-compose.edge-full.yml")
        with open(f, "r", encoding="utf-8") as fp:
            return yaml.safe_load(fp)

    @pytest.fixture
    def edge_compose_raw(self):
        f = os.path.join(WORKSPACE, "Configuration2.0", "docker", "docker-compose.edge-full.yml")
        return Path(f).read_text(encoding="utf-8")

    def test_service_naming_convention(self, edge_compose):
        """服务名统一 edge-{service} 前缀"""
        services = edge_compose.get("services", {})
        for name in services:
            assert name.startswith("edge-"), f"服务 {name} 未遵循 edge- 前缀"

    def test_container_naming_convention(self, edge_compose):
        """容器名统一 jgsy-edge-{service} 格式"""
        services = edge_compose.get("services", {})
        for name, svc in services.items():
            container = svc.get("container_name", "")
            assert container.startswith("jgsy-edge-"), f"{name}: 容器名 {container} 未遵循 jgsy-edge- 格式"

    def test_deployment_mode_labels(self, edge_compose):
        """所有应用服务具有 jgsy.deployment.mode 标签"""
        services = edge_compose.get("services", {})
        infra = {"edge-postgres", "edge-redis", "edge-mqtt"}
        for name, svc in services.items():
            if name in infra:
                continue
            labels = svc.get("labels", {})
            if isinstance(labels, list):
                label_dict = {}
                for l in labels:
                    if "=" in l:
                        k, v = l.split("=", 1)
                        label_dict[k] = v
                labels = label_dict
            assert labels.get("jgsy.deployment.mode") == "Edge", \
                f"{name}: 缺少 jgsy.deployment.mode=Edge 标签"

    def test_deployment_zone_labels(self, edge_compose):
        """所有应用服务具有正确的安全分区标签"""
        services = edge_compose.get("services", {})
        infra = {"edge-postgres", "edge-redis", "edge-mqtt"}
        zone_i = {"edge-microgrid", "edge-pvessc", "edge-safecontrol", "edge-ingestion", "edge-device"}
        for name, svc in services.items():
            if name in infra:
                continue
            labels = svc.get("labels", {})
            if isinstance(labels, list):
                label_dict = {}
                for l in labels:
                    if "=" in l:
                        k, v = l.split("=", 1)
                        label_dict[k] = v
                labels = label_dict
            zone = labels.get("jgsy.deployment.zone", "")
            expected = "Zone-I" if name in zone_i else "Zone-II"
            assert zone == expected, f"{name}: 分区标签应为 {expected}，实际为 {zone}"

    def test_local_naming_labels(self, edge_compose):
        """所有应用服务具有 {Service}-Local 合规命名标签"""
        services = edge_compose.get("services", {})
        infra = {"edge-postgres", "edge-redis", "edge-mqtt"}
        for name, svc in services.items():
            if name in infra:
                continue
            labels = svc.get("labels", {})
            if isinstance(labels, list):
                label_dict = {}
                for l in labels:
                    if "=" in l:
                        k, v = l.split("=", 1)
                        label_dict[k] = v
                labels = label_dict
            deploy_name = labels.get("jgsy.deployment.name", "")
            assert deploy_name.endswith("-Local"), \
                f"{name}: 缺少 jgsy.deployment.name=*-Local 合规标签"

    def test_iotcloudai_dual_deploy_label(self, edge_compose):
        """IotCloudAI 具有双端部署标签"""
        svc = edge_compose.get("services", {}).get("edge-iotcloudai", {})
        labels = svc.get("labels", {})
        if isinstance(labels, list):
            label_dict = {}
            for l in labels:
                if "=" in l:
                    k, v = l.split("=", 1)
                    label_dict[k] = v
            labels = label_dict
        assert labels.get("jgsy.deployment.dual") == "true", \
            "IotCloudAI 缺少双端部署标签 jgsy.deployment.dual=true"

    def test_iotcloudai_local_name(self, edge_compose_raw):
        """IotCloudAI 注释包含 IotCloudAI-Local 标识"""
        assert "IotCloudAI-Local" in edge_compose_raw, \
            "edge compose 缺少 IotCloudAI-Local 命名标识"


# ═══════════════════════════════════════════════════════════════════════════════
# 4. 安全分区网络隔离
# ═══════════════════════════════════════════════════════════════════════════════

class TestSecurityZoneIsolation:
    """安全分区网络隔离测试"""

    @pytest.fixture
    def edge_compose(self):
        f = os.path.join(WORKSPACE, "Configuration2.0", "docker", "docker-compose.edge-full.yml")
        with open(f, "r", encoding="utf-8") as fp:
            return yaml.safe_load(fp)

    def test_zone_realtime_internal(self, edge_compose):
        """Ⅰ区网络为 internal（不直连外网）"""
        networks = edge_compose.get("networks", {})
        zone_rt = networks.get("zone-realtime", {})
        assert zone_rt.get("internal") is True, "Ⅰ区网络未设置 internal: true"

    def test_zone_control_external(self, edge_compose):
        """Ⅱ区网络可通外部（安全接入）"""
        networks = edge_compose.get("networks", {})
        zone_ctrl = networks.get("zone-control", {})
        # Ⅱ区不设置 internal，允许向云端推送数据
        assert zone_ctrl.get("internal") is not True, "Ⅱ区网络不应设置 internal"

    def test_zone_i_services_in_realtime(self, edge_compose):
        """Ⅰ区服务连接到 zone-realtime 网络"""
        services = edge_compose.get("services", {})
        zone_i_svcs = ["edge-microgrid", "edge-pvessc", "edge-safecontrol", "edge-ingestion", "edge-device"]
        for name in zone_i_svcs:
            svc = services.get(name, {})
            nets = svc.get("networks", {})
            if isinstance(nets, list):
                assert "zone-realtime" in nets, f"{name} 未连接 zone-realtime"
            else:
                assert "zone-realtime" in nets, f"{name} 未连接 zone-realtime"

    def test_zone_ii_services_in_control(self, edge_compose):
        """Ⅱ区服务连接到 zone-control 网络"""
        services = edge_compose.get("services", {})
        zone_ii_svcs = ["edge-orchestrator", "edge-ruleengine", "edge-charging",
                        "edge-identity", "edge-observability", "edge-iotcloudai", "edge-gateway"]
        for name in zone_ii_svcs:
            svc = services.get(name, {})
            nets = svc.get("networks", {})
            if isinstance(nets, list):
                assert "zone-control" in nets, f"{name} 未连接 zone-control"
            else:
                assert "zone-control" in nets, f"{name} 未连接 zone-control"

    def test_zone_i_not_in_control(self, edge_compose):
        """Ⅰ区实时控制服务不应连接Ⅱ区网络（隔离）"""
        services = edge_compose.get("services", {})
        zone_i_svcs = ["edge-microgrid", "edge-pvessc", "edge-safecontrol", "edge-ingestion", "edge-device"]
        for name in zone_i_svcs:
            svc = services.get(name, {})
            nets = svc.get("networks", {})
            if isinstance(nets, list):
                assert "zone-control" not in nets, f"{name} 不应连接 zone-control"
            elif isinstance(nets, dict):
                assert "zone-control" not in nets, f"{name} 不应连接 zone-control"


# ═══════════════════════════════════════════════════════════════════════════════
# 5. 基础设施完整性
# ═══════════════════════════════════════════════════════════════════════════════

class TestInfrastructureCompleteness:
    """基础设施完整性测试"""

    def test_clamav_in_infrastructure_compose(self):
        """ClamAV 在基础设施 compose 中"""
        f = os.path.join(WORKSPACE, "Configuration2.0", "docker", "docker-compose.infrastructure.yml")
        content = Path(f).read_text(encoding="utf-8")
        assert "clamav" in content, "ClamAV 服务未添加到基础设施 compose"

    def test_clamav_image_version(self):
        """ClamAV 镜像版本"""
        f = os.path.join(WORKSPACE, "Configuration2.0", "docker", "docker-compose.infrastructure.yml")
        content = Path(f).read_text(encoding="utf-8")
        assert "clamav/clamav:" in content, "ClamAV 官方镜像缺失"

    def test_clamav_port(self):
        """ClamAV 端口暴露 3310"""
        f = os.path.join(WORKSPACE, "Configuration2.0", "docker", "docker-compose.infrastructure.yml")
        content = Path(f).read_text(encoding="utf-8")
        assert "3310" in content, "ClamAV 3310 端口缺失"

    def test_virus_scan_di_registration(self):
        """IVirusScanService 在 SecurityServiceExtensions 中注册"""
        f = os.path.join(WORKSPACE, "JGSY.AGI.Common.Auth", "Security", "SecurityServiceExtensions.cs")
        content = Path(f).read_text(encoding="utf-8")
        assert "IVirusScanService" in content, "IVirusScanService DI 注册缺失"
        assert "ClamAvVirusScanService" in content, "ClamAvVirusScanService 实现注册缺失"

    def test_deployment_mode_provider_registered(self):
        """IDeploymentModeProvider 在 SecurityServiceExtensions 中注册"""
        f = os.path.join(WORKSPACE, "JGSY.AGI.Common.Auth", "Security", "SecurityServiceExtensions.cs")
        content = Path(f).read_text(encoding="utf-8")
        assert "IDeploymentModeProvider" in content, "IDeploymentModeProvider DI 注册缺失"
        assert "DefaultDeploymentModeProvider" in content, "DefaultDeploymentModeProvider 实现注册缺失"

    def test_edge_compose_basic_exists(self):
        """轻量边缘 compose 存在"""
        f = os.path.join(WORKSPACE, "Configuration2.0", "docker", "docker-compose.edge.yml")
        assert os.path.exists(f), "轻量边缘 compose 缺失"

    def test_edge_compose_full_exists(self):
        """完整边缘 compose 存在"""
        f = os.path.join(WORKSPACE, "Configuration2.0", "docker", "docker-compose.edge-full.yml")
        assert os.path.exists(f), "完整边缘 compose 缺失"


# ═══════════════════════════════════════════════════════════════════════════════
# 6. 双端部署数据流合规
# ═══════════════════════════════════════════════════════════════════════════════

class TestDualDeployDataFlow:
    """双端部署数据流合规（GB/T 36572）"""

    def test_upstream_sync_interface(self):
        """上行数据同步接口（本地→云端）"""
        f = os.path.join(WORKSPACE, "JGSY.AGI.Common.Abstractions", "Interfaces", "IEdgeSyncService.cs")
        content = Path(f).read_text(encoding="utf-8")
        assert "IUpstreamSyncService" in content
        # 上行仅允许遥测/状态/日志/告警
        for method in ["SendTelemetry", "SendDeviceStatus", "SendAlarm", "SendAuditLogs"]:
            assert method in content, f"上行方法缺失: {method}"

    def test_downstream_sync_interface(self):
        """下行数据同步接口（云端→本地：REQ-001 云端绝对只读边界 — 无任何下行方法）"""
        f = os.path.join(WORKSPACE, "JGSY.AGI.Common.Abstractions", "Interfaces", "IEdgeSyncService.cs")
        content = Path(f).read_text(encoding="utf-8")
        assert "IDownstreamSyncService" in content
        # REQ-001: 云端绝对只读边界 — IDownstreamSyncService 不含任何 Send* 方法
        assert "云端绝对只读边界" in content, "REQ-001 只读边界注释缺失"
        for method in ["SendStrategy", "SendRulePackage", "SendDeviceConfig"]:
            assert method not in content, f"下行方法应已移除: {method}"

    def test_upstream_data_filter(self):
        """上行数据过滤器（禁止控制指令上行）"""
        f = os.path.join(WORKSPACE, "JGSY.AGI.Common.Abstractions", "Interfaces", "IEdgeSyncService.cs")
        content = Path(f).read_text(encoding="utf-8")
        assert "IUpstreamDataFilter" in content, "上行数据过滤器缺失"

    def test_downstream_data_filter(self):
        """下行数据过滤器（禁止直接控制指令下行）"""
        f = os.path.join(WORKSPACE, "JGSY.AGI.Common.Abstractions", "Interfaces", "IEdgeSyncService.cs")
        content = Path(f).read_text(encoding="utf-8")
        assert "IDownstreamDataFilter" in content, "下行数据过滤器缺失"

    def test_offline_buffer(self):
        """离线缓冲接口（断网场景本地存储）"""
        f = os.path.join(WORKSPACE, "JGSY.AGI.Common.Abstractions", "Interfaces", "IEdgeSyncService.cs")
        content = Path(f).read_text(encoding="utf-8")
        assert "IOfflineBufferService" in content, "离线缓冲接口缺失"

    def test_sync_integrity_validator(self):
        """同步完整性校验（SM4加密 + SM2签名）"""
        f = os.path.join(WORKSPACE, "JGSY.AGI.Common.Abstractions", "Interfaces", "IEdgeSyncService.cs")
        content = Path(f).read_text(encoding="utf-8")
        assert "ISyncIntegrityValidator" in content, "同步完整性校验接口缺失"
        assert "EncryptPayload" in content, "SM4 载荷加密缺失"
        assert "SignMessage" in content, "SM2 消息签名缺失"

    def test_iotcloudai_cloud_edge_sync(self):
        """IotCloudAI 有 CloudEdgeSyncService 实现"""
        f = os.path.join(WORKSPACE, "JGSY.AGI.IotCloudAI", "Edge", "CloudEdgeSyncService.cs")
        assert os.path.exists(f), "CloudEdgeSyncService 实现缺失"

    def test_iotcloudai_offline_manager(self):
        """IotCloudAI 有离线状态管理器"""
        f = os.path.join(WORKSPACE, "JGSY.AGI.IotCloudAI", "Edge", "OfflineModeManager.cs")
        assert os.path.exists(f), "OfflineModeManager 缺失"


# ═══════════════════════════════════════════════════════════════════════════════
# 7. 充电服务双端部署
# ═══════════════════════════════════════════════════════════════════════════════

class TestChargingDualDeployment:
    """Charging 双端部署测试"""

    def test_charging_edge_options(self):
        """Charging 有边缘模式配置类"""
        f = os.path.join(WORKSPACE, "JGSY.AGI.Charging", "Models", "ChargingEdgeModeOptions.cs")
        assert os.path.exists(f), "ChargingEdgeModeOptions 缺失"
        content = Path(f).read_text(encoding="utf-8")
        assert "Enabled" in content
        assert "StationId" in content or "BillingMode" in content

    def test_charging_offline_service(self):
        """Charging 有离线服务"""
        f = os.path.join(WORKSPACE, "JGSY.AGI.Charging", "Services", "ChargingOfflineService.cs")
        assert os.path.exists(f), "ChargingOfflineService 缺失"

    def test_charging_in_edge_compose(self):
        """Charging 出现在边缘 compose"""
        f = os.path.join(WORKSPACE, "Configuration2.0", "docker", "docker-compose.edge-full.yml")
        content = Path(f).read_text(encoding="utf-8")
        assert "edge-charging" in content, "Charging 未包含在边缘部署中"
        assert "Charging-Local" in content, "Charging 缺少 -Local 合规标签"


# ═══════════════════════════════════════════════════════════════════════════════
# 8. 合规总览
# ═══════════════════════════════════════════════════════════════════════════════

class TestDualDeployComplianceSummary:
    """双端部署合规总览"""

    def test_zone_i_service_count(self):
        """Ⅰ区至少 5 个实时控制服务"""
        f = os.path.join(WORKSPACE, "Configuration2.0", "docker", "docker-compose.edge-full.yml")
        with open(f, "r", encoding="utf-8") as fp:
            compose = yaml.safe_load(fp)
        services = compose.get("services", {})
        zone_i = [n for n, s in services.items()
                  if isinstance(s.get("labels"), dict) and s["labels"].get("jgsy.deployment.zone") == "Zone-I"]
        assert len(zone_i) >= 5, f"Ⅰ区服务不足: {len(zone_i)} < 5"

    def test_zone_ii_service_count(self):
        """Ⅱ区至少 7 个非实时控制服务"""
        f = os.path.join(WORKSPACE, "Configuration2.0", "docker", "docker-compose.edge-full.yml")
        with open(f, "r", encoding="utf-8") as fp:
            compose = yaml.safe_load(fp)
        services = compose.get("services", {})
        zone_ii = [n for n, s in services.items()
                   if isinstance(s.get("labels"), dict) and s["labels"].get("jgsy.deployment.zone") == "Zone-II"]
        assert len(zone_ii) >= 7, f"Ⅱ区服务不足: {len(zone_ii)} < 7"

    def test_all_edge_services_have_healthcheck(self):
        """所有边缘服务都配置了健康检查"""
        f = os.path.join(WORKSPACE, "Configuration2.0", "docker", "docker-compose.edge-full.yml")
        with open(f, "r", encoding="utf-8") as fp:
            compose = yaml.safe_load(fp)
        services = compose.get("services", {})
        for name, svc in services.items():
            assert "healthcheck" in svc, f"{name}: 缺少健康检查配置"

    def test_all_edge_env_no_hardcoded_password(self):
        """所有边缘服务密码通过环境变量注入"""
        f = os.path.join(WORKSPACE, "Configuration2.0", "docker", "docker-compose.edge-full.yml")
        content = Path(f).read_text(encoding="utf-8")
        # 密码应使用 ${VAR} 格式，不应硬编码
        # 搜索 Password= 后面不跟 ${
        hard_coded = re.findall(r'Password=([^$\n{][^\n]*)', content)
        assert len(hard_coded) == 0, f"发现硬编码密码: {hard_coded}"

    def test_shared_abstractions_no_external_deps(self):
        """Common.Abstractions 无外部依赖（零耦合）"""
        csproj = os.path.join(WORKSPACE, "JGSY.AGI.Common.Abstractions", "JGSY.AGI.Common.Abstractions.csproj")
        content = Path(csproj).read_text(encoding="utf-8")
        # 允许 Microsoft.Extensions.Options 等基础包，但不应有 Npgsql/Redis 等
        for forbidden_pkg in ["Npgsql", "StackExchange.Redis", "MQTTnet", "Dapper"]:
            assert forbidden_pkg not in content, \
                f"Common.Abstractions 不应依赖 {forbidden_pkg}"

