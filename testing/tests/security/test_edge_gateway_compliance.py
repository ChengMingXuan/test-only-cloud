"""
边缘部署配置 + 网关防重放 合规性验证
=============================================
纯静态检查：验证 Compose/YARP/Gateway 配置满足合规要求
"""
import json
import os
import re

import pytest
import yaml

# 项目根目录
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))


# ═══════════════════════════════════════════════════
# 边缘部署配置验证
# ═══════════════════════════════════════════════════

@pytest.mark.security
@pytest.mark.compliance
class TestEdgeDeploymentConfig:
    """边缘部署 Compose 配置合规性"""

    COMPOSE_PATH = os.path.join(ROOT, "docker", "docker-compose.edge-full.yml")

    @pytest.fixture(autouse=True)
    def load_compose(self):
        assert os.path.exists(self.COMPOSE_PATH), \
            "docker-compose.edge-full.yml 不存在"
        with open(self.COMPOSE_PATH, "r", encoding="utf-8") as f:
            self.compose = yaml.safe_load(f)

    def test_compose_has_services(self):
        """边缘 Compose 应包含服务定义"""
        services = self.compose.get("services", {})
        assert len(services) >= 10, \
            f"边缘部署服务数不足: {len(services)} < 10"

    ZONE_I_SERVICES = [
        "edge-microgrid", "edge-pvessc", "edge-safecontrol",
        "edge-ingestion", "edge-device",
    ]
    ZONE_II_SERVICES = [
        "edge-orchestrator", "edge-ruleengine", "edge-charging",
        "edge-identity", "edge-observability", "edge-iotcloudai",
        "edge-gateway",
    ]

    @pytest.mark.parametrize("svc", ZONE_I_SERVICES)
    def test_zone_i_service_exists(self, svc):
        """Ⅰ区（实时控制）服务应存在"""
        services = self.compose.get("services", {})
        assert svc in services, f"Ⅰ区服务 {svc} 缺失"

    @pytest.mark.parametrize("svc", ZONE_II_SERVICES)
    def test_zone_ii_service_exists(self, svc):
        """Ⅱ区（非实时控制）服务应存在"""
        services = self.compose.get("services", {})
        assert svc in services, f"Ⅱ区服务 {svc} 缺失"

    def test_security_zone_networks(self):
        """应定义安全分区网络"""
        networks = self.compose.get("networks", {})
        assert "zone-realtime" in networks, "缺少 zone-realtime 网络"
        assert "zone-control" in networks, "缺少 zone-control 网络"

    def test_zone_realtime_internal(self):
        """Ⅰ区网络应为 internal（不直连外网）"""
        networks = self.compose.get("networks", {})
        rt = networks.get("zone-realtime", {})
        assert rt.get("internal") is True, \
            "zone-realtime 网络应设置 internal: true"

    def test_services_have_healthcheck(self):
        """所有业务服务应有健康检查"""
        services = self.compose.get("services", {})
        biz_services = {k: v for k, v in services.items()
                        if k.startswith("edge-") and k not in ("edge-postgres", "edge-redis", "edge-mqtt")}
        for name, svc in biz_services.items():
            assert "healthcheck" in svc, \
                f"服务 {name} 缺少健康检查"

    def test_services_have_deployment_labels(self):
        """业务服务应有部署模式标签"""
        services = self.compose.get("services", {})
        biz_services = {k: v for k, v in services.items()
                        if k.startswith("edge-") and k not in ("edge-postgres", "edge-redis", "edge-mqtt")}
        for name, svc in biz_services.items():
            labels = svc.get("labels", {})
            if isinstance(labels, list):
                label_text = "\n".join(labels)
            else:
                label_text = str(labels)
            assert "jgsy.deployment.mode" in label_text, \
                f"服务 {name} 缺少 jgsy.deployment.mode 标签"

    def test_services_have_resource_limits(self):
        """业务服务应有资源限制"""
        services = self.compose.get("services", {})
        biz_services = {k: v for k, v in services.items()
                        if k.startswith("edge-") and k not in ("edge-postgres", "edge-redis", "edge-mqtt")}
        for name, svc in biz_services.items():
            deploy = svc.get("deploy", {})
            resources = deploy.get("resources", {})
            assert "limits" in resources, \
                f"服务 {name} 缺少资源限制(deploy.resources.limits)"

    def test_jwt_secret_from_env(self):
        """JWT密钥应从环境变量注入"""
        services = self.compose.get("services", {})
        for name, svc in services.items():
            env = svc.get("environment", {})
            if isinstance(env, dict):
                jwt_val = env.get("Jwt__SecretKey", "")
                if jwt_val:
                    assert "${" in str(jwt_val), \
                        f"服务 {name} JWT密钥应从环境变量注入，而非硬编码"

    def test_postgres_password_from_env(self):
        """数据库密码应从环境变量注入"""
        services = self.compose.get("services", {})
        pg_svc = services.get("edge-postgres", {})
        env = pg_svc.get("environment", {})
        pg_pwd = str(env.get("POSTGRES_PASSWORD", ""))
        assert "${" in pg_pwd or "PG_LOCAL_PASSWORD" in pg_pwd, \
            "PostgreSQL 密码应从环境变量注入"

    def test_data_volumes_defined(self):
        """应定义持久化数据卷"""
        volumes = self.compose.get("volumes", {})
        assert "edge-pgdata" in volumes, "缺少 edge-pgdata 数据卷"
        assert "edge-redis-data" in volumes, "缺少 edge-redis-data 数据卷"


@pytest.mark.security
@pytest.mark.compliance
class TestEdgeDeployScript:
    """边缘部署脚本验证"""

    DEPLOY_SCRIPT = os.path.join(ROOT, "docker", "deploy-edge.ps1")
    INIT_DB_SCRIPT = os.path.join(ROOT, "docker", "init-edge-databases.ps1")

    def test_deploy_script_exists(self):
        """部署脚本应存在"""
        assert os.path.exists(self.DEPLOY_SCRIPT), \
            "deploy-edge.ps1 不存在"

    def test_init_db_script_exists(self):
        """数据库初始化脚本应存在"""
        assert os.path.exists(self.INIT_DB_SCRIPT), \
            "init-edge-databases.ps1 不存在"

    def test_deploy_script_checks_docker(self):
        """部署脚本应检查 Docker 环境"""
        with open(self.DEPLOY_SCRIPT, "r", encoding="utf-8") as f:
            content = f.read()
        assert "docker --version" in content or "docker" in content.lower(), \
            "部署脚本应包含 Docker 环境检查"

    def test_deploy_script_checks_env_file(self):
        """部署脚本应检查环境变量文件"""
        with open(self.DEPLOY_SCRIPT, "r", encoding="utf-8") as f:
            content = f.read()
        assert ".env" in content, \
            "部署脚本应检查环境文件"

    def test_deploy_script_has_health_check(self):
        """部署脚本应包含健康检查"""
        with open(self.DEPLOY_SCRIPT, "r", encoding="utf-8") as f:
            content = f.read()
        assert "health" in content.lower(), \
            "部署脚本应包含健康检查步骤"

    def test_init_db_has_edge_services(self):
        """数据库初始化脚本应覆盖边缘服务"""
        with open(self.INIT_DB_SCRIPT, "r", encoding="utf-8") as f:
            content = f.read()
        # 至少应包含 Identity, Device, Charging, MicroGrid
        for svc in ["Identity", "Device", "Charging", "MicroGrid"]:
            assert svc in content, \
                f"数据库初始化脚本应包含 {svc} 服务"

    def test_init_db_uses_utf8(self):
        """数据库脚本应使用 UTF-8 编码"""
        with open(self.INIT_DB_SCRIPT, "r", encoding="utf-8") as f:
            content = f.read()
        assert "PGCLIENTENCODING=UTF8" in content, \
            "数据库初始化应使用 PGCLIENTENCODING=UTF8"


@pytest.mark.security
@pytest.mark.compliance
class TestSecurityZonesConfig:
    """安全分区网络配置验证"""

    ZONES_PATH = os.path.join(ROOT, "docker", "docker-compose.security-zones.yml")

    def test_security_zones_file_exists(self):
        """安全分区配置文件应存在"""
        assert os.path.exists(self.ZONES_PATH), \
            "docker-compose.security-zones.yml 不存在"

    def test_four_security_zones(self):
        """应定义四个安全分区网络"""
        with open(self.ZONES_PATH, "r", encoding="utf-8") as f:
            config = yaml.safe_load(f)
        networks = config.get("networks", {})
        expected = ["jgsy-zone-control", "jgsy-zone-manage",
                    "jgsy-zone-external", "jgsy-zone-dmz", "jgsy-zone-infra"]
        for net in expected:
            assert net in networks, f"缺少安全分区网络: {net}"

    def test_control_zone_internal(self):
        """控制区应设为 internal"""
        with open(self.ZONES_PATH, "r", encoding="utf-8") as f:
            config = yaml.safe_load(f)
        networks = config.get("networks", {})
        ctrl = networks.get("jgsy-zone-control", {})
        assert ctrl.get("internal") is True, \
            "控制区网络应设置 internal: true"

    def test_zones_have_subnets(self):
        """各分区应有独立子网"""
        with open(self.ZONES_PATH, "r", encoding="utf-8") as f:
            config = yaml.safe_load(f)
        networks = config.get("networks", {})
        subnets = set()
        for name, net in networks.items():
            ipam = net.get("ipam", {})
            configs = ipam.get("config", [])
            for c in configs:
                subnet = c.get("subnet", "")
                if subnet:
                    assert subnet not in subnets, \
                        f"子网 {subnet} 重复分配于 {name}"
                    subnets.add(subnet)
        assert len(subnets) >= 4, \
            f"独立子网数不足: {len(subnets)} < 4"


# ═══════════════════════════════════════════════════
# 网关防重放 + 路由合规性
# ═══════════════════════════════════════════════════

@pytest.mark.security
@pytest.mark.compliance
class TestGatewayAntiReplay:
    """网关防重放配置验证"""

    GW_CONFIG = os.path.join(ROOT, "JGSY.AGI.Gateway", "appsettings.json")

    @pytest.fixture(autouse=True)
    def load_config(self):
        assert os.path.exists(self.GW_CONFIG), \
            "Gateway appsettings.json 不存在"
        with open(self.GW_CONFIG, "r", encoding="utf-8-sig") as f:
            self.config = json.load(f)

    def _get_anti_replay(self):
        """从多层嵌套中定位 AntiReplay 配置"""
        ar = self.config.get("Gateway", {}).get("Features", {}).get("AntiReplay", {})
        if not ar:
            ar = self.config.get("AntiReplay", {})
        return ar

    def test_anti_replay_enabled(self):
        """防重放应已启用"""
        ar = self._get_anti_replay()
        assert ar.get("Enabled") is True, \
            "网关防重放应已启用(AntiReplay.Enabled = true)"

    def test_anti_replay_paths_count(self):
        """防重放保护路径应 ≥ 10"""
        ar = self._get_anti_replay()
        paths = ar.get("ProtectedPaths", ar.get("Paths", []))
        assert len(paths) >= 10, \
            f"防重放保护路径不足: {len(paths)} < 10"

    CRITICAL_PATHS = [
        "/api/device",
        "/api/charging",
        "/api/blockchain/evidence",
    ]

    @pytest.mark.parametrize("path_prefix", CRITICAL_PATHS)
    def test_critical_paths_protected(self, path_prefix):
        """关键控制路径应受防重放保护"""
        ar = self._get_anti_replay()
        paths = ar.get("ProtectedPaths", ar.get("Paths", []))
        found = any(path_prefix in p for p in paths)
        assert found, \
            f"关键路径 {path_prefix} 未受防重放保护"


@pytest.mark.security
@pytest.mark.compliance
class TestGatewayYarpRouting:
    """YARP 路由配置验证"""

    YARP_PATH = os.path.join(ROOT, "JGSY.AGI.Gateway", "yarp.json")
    YARP_EDGE_PATH = os.path.join(ROOT, "JGSY.AGI.Gateway", "yarp.edge.json")

    def test_yarp_config_exists(self):
        """YARP 路由配置应存在"""
        assert os.path.exists(self.YARP_PATH), \
            "yarp.json 不存在"

    def test_yarp_edge_config_exists(self):
        """YARP 边缘路由配置应存在"""
        assert os.path.exists(self.YARP_EDGE_PATH), \
            "yarp.edge.json 不存在"

    def test_yarp_has_blockchain_route(self):
        """YARP 应包含 blockchain 服务路由"""
        with open(self.YARP_PATH, "r", encoding="utf-8-sig") as f:
            yarp = json.load(f)
        routes = yarp.get("ReverseProxy", {}).get("Routes", {})
        blockchain_routes = [k for k in routes if "blockchain" in k.lower()]
        assert len(blockchain_routes) > 0, \
            "YARP 缺少 blockchain 服务路由"

    def test_yarp_has_evidence_route(self):
        """YARP 应支持 evidence API 路由"""
        with open(self.YARP_PATH, "r", encoding="utf-8-sig") as f:
            yarp = json.load(f)
        routes = yarp.get("ReverseProxy", {}).get("Routes", {})
        evidence_routes = [k for k in routes if "evidence" in k.lower()]
        assert len(evidence_routes) > 0, \
            "YARP 缺少 evidence API 路由"


# ═══════════════════════════════════════════════════
# Loki 日志留存 + 基础设施合规
# ═══════════════════════════════════════════════════

@pytest.mark.security
@pytest.mark.compliance
class TestInfrastructureCompliance:
    """基础设施合规检查"""

    INFRA_COMPOSE = os.path.join(ROOT, "docker", "docker-compose.infrastructure.yml")

    def test_infra_compose_exists(self):
        """基础设施 Compose 应存在"""
        assert os.path.exists(self.INFRA_COMPOSE), \
            "docker-compose.infrastructure.yml 不存在"

    def test_clamav_container(self):
        """应包含 ClamAV 病毒扫描容器"""
        with open(self.INFRA_COMPOSE, "r", encoding="utf-8") as f:
            config = yaml.safe_load(f)
        services = config.get("services", {})
        clamav_found = any("clamav" in k.lower() for k in services)
        assert clamav_found, \
            "基础设施应包含 ClamAV 容器"

    def test_grafana_sla_dashboard(self):
        """Grafana SLA 仪表盘应存在"""
        dashboard_dir = os.path.join(ROOT, "deploy", "configs", "grafana", "dashboards")
        if os.path.exists(dashboard_dir):
            files = os.listdir(dashboard_dir)
            sla_found = any("sla" in f.lower() for f in files)
            assert sla_found, \
                "缺少 Grafana SLA 合规仪表盘"
        else:
            pytest.skip("Grafana dashboards 目录不存在")

    def test_loki_retention_180_days(self):
        """Loki 日志留存应 ≥ 180 天"""
        config_paths = [
            os.path.join(ROOT, "docker", "observability", "loki", "loki-config.yaml"),
            os.path.join(ROOT, "deploy", "configs", "loki", "loki-config.yaml"),
        ]
        checked = False
        for cp in config_paths:
            if not os.path.exists(cp):
                continue
            with open(cp, "r", encoding="utf-8") as f:
                config = yaml.safe_load(f)
            limits = config.get("limits_config", {})
            retention = limits.get("retention_period", "0h")
            hours = int(re.sub(r"[^0-9]", "", str(retention)) or "0")
            assert hours >= 4320, \
                f"Loki 日志留存不足 180 天: {retention}"
            checked = True
        assert checked, "未找到任何 Loki 配置文件"
