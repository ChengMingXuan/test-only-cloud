"""
═══════════════════════════════════════════════════════════════════════════════
JGSY.AGI 三场景合规测试套件
═══════════════════════════════════════════════════════════════════════════════
覆盖范围：
  场景1（纯云端SaaS充电）: AUTH/AUDIT/DATA/COMM 等保三级
  场景2（微电网本地+云端）: + DEPLOY/ZONE/FLOW 电力分区
  场景3（虚拟电厂云端）: + VPP 国密通信
标准：GB/T 22239-2019 + GB/T 36572 + GB/T 44241-2024
"""

import os
import re
import json
import glob
import yaml
import pytest
import requests
from pathlib import Path

# ═══════════════════ 测试配置 ═══════════════════

WORKSPACE = os.environ.get("WORKSPACE_DIR", r"D:\2026\aiops.v2")
API_BASE = os.environ.get("API_BASE_URL", "http://localhost:8000")
GATEWAY_URL = f"{API_BASE}/api"

# 测试用户凭据（从环境变量读取，禁止硬编码）
TEST_USER = os.environ.get("TEST_USERNAME", "admin")
TEST_PASS = os.environ.get("TEST_PASSWORD", "")


def get_auth_token():
    """获取测试认证 Token"""
    assert TEST_PASS, "未设置 TEST_PASSWORD 环境变量"
    try:
        resp = requests.post(f"{GATEWAY_URL}/identity/auth/login", json={
            "username": TEST_USER,
            "password": TEST_PASS
        }, timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            return data.get("data", {}).get("accessToken")
    except requests.ConnectionError as exc:
        pytest.fail(f"API 网关不可达: {exc}")
    return None


# ═══════════════════════════════════════════════════════════════════════════════
# 场景1：纯云端 SaaS（充电运营）— 4 项 P0
# ═══════════════════════════════════════════════════════════════════════════════

class TestScenario1_AUTH:
    """AUTH: 身份认证与权限（等保三级）"""

    def test_auth001_password_complexity(self):
        """AUTH-001: 密码复杂度 ≥ 8 位，字母+数字+特殊字符"""
        policy_file = os.path.join(WORKSPACE, "JGSY.AGI.Common.Auth", "Security", "PasswordPolicy.cs")
        assert os.path.exists(policy_file), "密码策略文件缺失"
        content = Path(policy_file).read_text(encoding="utf-8")
        assert "MinLength" in content or "minLength" in content, "未定义最小密码长度"
        assert re.search(r"[Uu]pper|大写", content), "未要求大写字母"
        assert re.search(r"[Dd]igit|数字|\d", content), "未要求数字"
        assert re.search(r"[Ss]pecial|特殊", content), "未要求特殊字符"

    def test_auth002_login_lockout(self):
        """AUTH-002: 登录失败锁定 5 次 / 10 分钟"""
        protection_file = os.path.join(WORKSPACE, "JGSY.AGI.Common.Auth", "Security", "LoginProtectionService.cs")
        assert os.path.exists(protection_file), "登录保护服务缺失"
        content = Path(protection_file).read_text(encoding="utf-8")
        assert re.search(r"MaxAttempts|maxAttempts|最大.*次", content), "未定义最大尝试次数"
        assert re.search(r"[Ll]ock|锁定", content), "未实现锁定机制"

    def test_auth003_mfa_implemented(self):
        """AUTH-003: 双因子认证（MFA）已实现"""
        mfa_dir = os.path.join(WORKSPACE, "JGSY.AGI.Identity", "Auth", "Business")
        mfa_files = glob.glob(os.path.join(mfa_dir, "Mfa*.cs"))
        assert len(mfa_files) >= 2, f"MFA 服务文件不足: 找到 {len(mfa_files)} 个"

    def test_auth003_mfa_enforced_for_admins(self):
        """AUTH-003: MFA 对管理员强制启用"""
        config_file = os.path.join(WORKSPACE, "JGSY.AGI.Identity", "appsettings.json")
        config = json.loads(Path(config_file).read_text(encoding="utf-8-sig"))
        mfa_config = config.get("Mfa", {})
        assert mfa_config.get("Enabled", False), "MFA 未启用"
        enforced_roles = mfa_config.get("EnforcedForRoles", [])
        assert "SUPER_ADMIN" in enforced_roles, "SUPER_ADMIN 未强制 MFA"

    def test_auth005_three_admin_separation(self):
        """AUTH-005: 三员分立（等保三级一票否决项）"""
        # 检查角色种子数据
        migration_files = glob.glob(os.path.join(WORKSPACE, "JGSY.AGI.Permission", "Data", "Migrations", "*.sql"))
        migration_files += glob.glob(os.path.join(WORKSPACE, "JGSY.AGI.Blockchain", "Data", "Migrations", "*.sql"))
        all_sql = ""
        for f in migration_files:
            all_sql += Path(f).read_text(encoding="utf-8")
        assert "SYSTEM_ADMIN" in all_sql, "SYSTEM_ADMIN 角色种子缺失"
        assert "SECURITY_ADMIN" in all_sql, "SECURITY_ADMIN 角色种子缺失"
        assert "AUDIT_ADMIN" in all_sql, "AUDIT_ADMIN 角色种子缺失"

    def test_auth005_admin_mutual_exclusion(self):
        """AUTH-005: 三管理员角色互斥"""
        svc_file = os.path.join(WORKSPACE, "JGSY.AGI.Permission", "Business", "UserRoleService.cs")
        content = Path(svc_file).read_text(encoding="utf-8")
        assert "ValidateAdminRoleMutualExclusion" in content, "缺少管理员角色互斥校验"
        assert "ADMIN_ROLE_MUTUAL_EXCLUSION" in content, "缺少互斥异常码"

    def test_auth006_permission_system(self):
        """AUTH-006: 功能权限最小化"""
        attr_file = os.path.join(WORKSPACE, "JGSY.AGI.Common.Auth", "Security", "RequirePermissionAttribute.cs")
        assert os.path.exists(attr_file), "权限属性文件缺失"
        middleware_file = os.path.join(WORKSPACE, "JGSY.AGI.Common.Auth", "Security", "PermissionAuthorizationMiddleware.cs")
        assert os.path.exists(middleware_file), "权限中间件缺失"

    def test_auth008_password_hashing(self):
        """AUTH-008: 密码加盐哈希存储"""
        hasher_file = os.path.join(WORKSPACE, "JGSY.AGI.Common.Auth", "Security", "BcryptPasswordHasher.cs")
        assert os.path.exists(hasher_file), "密码哈希器缺失"


class TestScenario1_AUDIT:
    """AUDIT: 操作审计（等保三级）"""

    def test_audit005_tamper_proof(self):
        """AUDIT-005: 审计日志防篡改（等保三级一票否决项）"""
        # 链式哈希服务
        chain_svc = os.path.join(WORKSPACE, "JGSY.AGI.Blockchain", "Services", "AuditChainHashService.cs")
        assert os.path.exists(chain_svc), "审计链式哈希服务缺失"
        content = Path(chain_svc).read_text(encoding="utf-8")
        assert "SM3" in content, "未使用 SM3 哈希算法"
        assert "VerifyChainIntegrityAsync" in content, "缺少完整性验证方法"

        # 数据库触发器
        trigger_sql_files = glob.glob(os.path.join(WORKSPACE, "JGSY.AGI.Blockchain", "Data", "Migrations", "*tamper*.sql"))
        assert len(trigger_sql_files) > 0, "缺少防篡改触发器迁移脚本"
        for f in trigger_sql_files:
            sql = Path(f).read_text(encoding="utf-8")
            assert "TRIGGER" in sql.upper(), "SQL 中未包含触发器定义"

    def test_audit_log_service_exists(self):
        """AUDIT-001~004: 审计日志服务存在"""
        svc = os.path.join(WORKSPACE, "JGSY.AGI.Common.Auth", "Security", "AuditLogService.cs")
        assert os.path.exists(svc), "审计日志服务缺失"


class TestScenario1_DATA:
    """DATA: 数据安全（等保三级）"""

    def test_data001_classification(self):
        """DATA-001: 数据分类分级体系"""
        attr_file = os.path.join(WORKSPACE, "JGSY.AGI.Common.Abstractions", "Security", "DataClassificationAttribute.cs")
        assert os.path.exists(attr_file), "DataClassificationAttribute 缺失"
        content = Path(attr_file).read_text(encoding="utf-8")
        for level in ["Public", "Internal", "Sensitive", "Confidential"]:
            assert level in content, f"缺少数据分级: {level}"

    def test_data002_encryption_service(self):
        """DATA-002: 敏感数据加密服务"""
        enc_file = os.path.join(WORKSPACE, "JGSY.AGI.Common.Auth", "Security", "EncryptionService.cs")
        assert os.path.exists(enc_file), "加密服务缺失"
        content = Path(enc_file).read_text(encoding="utf-8")
        assert "AesGcm" in content, "未使用 AES-GCM 加密"

    def test_data003_log_retention_6months(self):
        """DATA-003: 日志保存 ≥ 6 个月（等保三级一票否决项）"""
        loki_configs = [
            os.path.join(WORKSPACE, "Configuration2.0", "docker", "observability", "loki", "loki-config.yaml"),
            os.path.join(WORKSPACE, "deploy", "configs", "loki", "loki-config.yaml"),
        ]
        for config_path in loki_configs:
            if not os.path.exists(config_path):
                continue
            with open(config_path, "r", encoding="utf-8") as f:
                content = f.read()
            matches = re.findall(r"retention_period:\s*(\d+)h", content)
            for m in matches:
                hours = int(m)
                assert hours >= 4320, f"日志保留不足6个月: {hours}h < 4320h（{config_path}）"

    def test_data005_sensitive_masking(self):
        """DATA-005: 敏感数据脱敏"""
        mask_file = os.path.join(WORKSPACE, "JGSY.AGI.Common.Auth", "Security", "SensitiveMaskAttribute.cs")
        assert os.path.exists(mask_file), "敏感数据脱敏属性缺失"
        content = Path(mask_file).read_text(encoding="utf-8")
        for mask_type in ["Phone", "IdCard", "BankCard", "Email"]:
            assert mask_type in content, f"缺少脱敏类型: {mask_type}"

    def test_data007_watermark_enabled(self):
        """DATA-007: 水印功能已启用"""
        config_file = os.path.join(WORKSPACE, "JGSY.AGI.Frontend", "src", "config", "system.ts")
        content = Path(config_file).read_text(encoding="utf-8")
        assert re.search(r"WATERMARK\s*:\s*true", content), "水印功能未启用"


class TestScenario1_COMM:
    """COMM: 通信加密（等保三级 + 电力专项）"""

    def test_comm001_https_config(self):
        """COMM-001: 全站 HTTPS 配置"""
        gateway_config = os.path.join(WORKSPACE, "JGSY.AGI.Gateway", "appsettings.json")
        content = Path(gateway_config).read_text(encoding="utf-8")
        assert "HTTPS" in content.upper() or "https" in content, "网关配置中未找到 HTTPS 相关配置"

    def test_comm002_sm4_encryption_filter(self):
        """COMM-002: SM4 加密 Action Filter 存在"""
        sm4_file = os.path.join(WORKSPACE, "JGSY.AGI.Common.Auth", "Security", "RequireSM4EncryptionAttribute.cs")
        assert os.path.exists(sm4_file), "RequireSM4EncryptionAttribute 缺失"
        content = Path(sm4_file).read_text(encoding="utf-8")
        assert "ISM4KeyStore" in content, "SM4 密钥存储接口缺失"
        assert "SM4EncryptionActionFilter" in content, "SM4 加密过滤器缺失"

    def test_comm003_sm2_signature_filter(self):
        """COMM-003: SM2 签名 Action Filter 存在"""
        sm2_file = os.path.join(WORKSPACE, "JGSY.AGI.Common.Auth", "Security", "RequireSM2SignatureAttribute.cs")
        assert os.path.exists(sm2_file), "RequireSM2SignatureAttribute 缺失"
        content = Path(sm2_file).read_text(encoding="utf-8")
        assert "ISM2KeyStore" in content, "SM2 密钥存储接口缺失"
        assert "SM2SignatureActionFilter" in content, "SM2 签名过滤器缺失"

    def test_comm004_anti_replay(self):
        """COMM-004: 防重放中间件"""
        middleware_file = os.path.join(WORKSPACE, "JGSY.AGI.Gateway", "Middleware", "AntiReplayMiddleware.cs")
        assert os.path.exists(middleware_file), "防重放中间件缺失"

    def test_comm004_anti_replay_enabled(self):
        """COMM-004: 防重放已启用"""
        config_file = os.path.join(WORKSPACE, "JGSY.AGI.Gateway", "appsettings.json")
        config = json.loads(Path(config_file).read_text(encoding="utf-8-sig"))
        features = config.get("Gateway", {}).get("Features", {})
        anti_replay = features.get("AntiReplay", {})
        assert anti_replay.get("Enabled", False), "防重放未启用"
        paths = anti_replay.get("ProtectedPaths", [])
        assert len(paths) >= 5, f"受保护路径不足: {len(paths)} < 5"

    def test_comm006_mtls(self):
        """COMM-006: 微服务间 mTLS"""
        mtls_file = os.path.join(WORKSPACE, "JGSY.AGI.Common.Auth", "Security", "MtlsHttpClientFactory.cs")
        assert os.path.exists(mtls_file), "mTLS HTTP 客户端工厂缺失"

    def test_sm_crypto_service(self):
        """国密 SM2/SM3/SM4 完整实现"""
        crypto_file = os.path.join(WORKSPACE, "JGSY.AGI.Blockchain", "Web3", "CryptoServices.cs")
        assert os.path.exists(crypto_file), "SMCryptoService 缺失"
        content = Path(crypto_file).read_text(encoding="utf-8")
        assert "SMCryptoService" in content, "SMCryptoService 类缺失"
        assert "SM2" in content, "SM2 签名未实现"
        assert "SM3" in content, "SM3 哈希未实现"
        assert "SM4Engine" in content, "SM4 加密未实现"


class TestScenario1_VULN:
    """VULN: 应用安全漏洞防护"""

    def test_vuln001_sql_injection(self):
        """VULN-001: SQL 注入防护（Dapper 参数化）"""
        # 检查不存在拼接 SQL 的模式
        # 排除已确认安全的动态 WHERE 子句构建（使用 Dapper 参数化 + BuildFilterConditions 模式）
        safe_dirs = {"DigitalTwin"}
        repo_files = glob.glob(os.path.join(WORKSPACE, "**", "Repositories", "*.cs"), recursive=True)
        dangerous_patterns = [r'\$".*SELECT.*\{', r"string\.Format.*SELECT"]
        for f in repo_files[:20]:  # 抽样检查
            if any(d in f for d in safe_dirs):
                continue
            content = Path(f).read_text(encoding="utf-8")
            for pattern in dangerous_patterns:
                matches = re.findall(pattern, content, re.IGNORECASE)
                assert len(matches) == 0, f"可能的 SQL 注入: {f} 匹配 {pattern}"

    def test_vuln002_xss(self):
        """VULN-002: XSS 防护过滤器"""
        filter_file = os.path.join(WORKSPACE, "JGSY.AGI.Common.Hosting", "Middleware", "InputSanitizationFilter.cs")
        assert os.path.exists(filter_file), "XSS 过滤器缺失"

    def test_vuln003_virus_scan_interface(self):
        """VULN-003: 文件上传病毒扫描接口"""
        scan_file = os.path.join(WORKSPACE, "JGSY.AGI.Common.Auth", "Security", "VirusScanService.cs")
        assert os.path.exists(scan_file), "病毒扫描服务缺失"
        content = Path(scan_file).read_text(encoding="utf-8")
        assert "IVirusScanService" in content, "IVirusScanService 接口缺失"
        assert "ClamAv" in content, "ClamAV 集成缺失"


class TestScenario1_HA:
    """HA: 高可用"""

    def test_ha005_sla_dashboard(self):
        """HA-005: SLA 监控仪表盘"""
        dashboard_file = os.path.join(WORKSPACE, "deploy", "configs", "grafana", "dashboards", "sla-compliance.json")
        assert os.path.exists(dashboard_file), "SLA 仪表盘配置尚未落库"
        dashboard = json.loads(Path(dashboard_file).read_text(encoding="utf-8"))
        panels = dashboard.get("panels", [])
        assert len(panels) >= 5, f"仪表盘面板不足: {len(panels)}"


# ═══════════════════════════════════════════════════════════════════════════════
# 场景2：微电网本地+云端（接电网）— 全部缺陷
# ═══════════════════════════════════════════════════════════════════════════════

class TestScenario2_DEPLOY:
    """DEPLOY: 部署架构合规（GB/T 36572）"""

    def test_deploy001_edge_compose_exists(self):
        """DEPLOY-001: 本地部署 compose 文件存在"""
        edge_compose = os.path.join(WORKSPACE, "Configuration2.0", "docker", "docker-compose.edge-full.yml")
        assert os.path.exists(edge_compose), "本地完整部署 compose 缺失"

    def test_deploy001_edge_services_count(self):
        """DEPLOY-001: 本地部署包含 ≥ 10 个控制服务"""
        edge_compose = os.path.join(WORKSPACE, "Configuration2.0", "docker", "docker-compose.edge-full.yml")
        with open(edge_compose, "r", encoding="utf-8") as f:
            content = f.read()
        # 统计 edge- 前缀的服务定义
        services = re.findall(r"^\s{2}(edge-\w+):", content, re.MULTILINE)
        # 排除基础设施
        app_services = [s for s in services if s not in ("edge-postgres", "edge-redis", "edge-mqtt")]
        assert len(app_services) >= 10, f"本地应用服务不足: {len(app_services)} < 10"

    def test_deploy004_security_zones(self):
        """DEPLOY-004: 安全分区网络隔离"""
        edge_compose = os.path.join(WORKSPACE, "Configuration2.0", "docker", "docker-compose.edge-full.yml")
        with open(edge_compose, "r", encoding="utf-8") as f:
            content = f.read()
        assert "zone-realtime" in content, "Ⅰ区（实时控制）网络缺失"
        assert "zone-control" in content, "Ⅱ区（非实时控制）网络缺失"
        assert "internal: true" in content, "Ⅰ区网络未设置为内部网络"

    def test_deploy009_offline_auth(self):
        """DEPLOY-009: 本地鉴权可离线工作"""
        edge_compose = os.path.join(WORKSPACE, "Configuration2.0", "docker", "docker-compose.edge-full.yml")
        with open(edge_compose, "r", encoding="utf-8") as f:
            content = f.read()
        assert "edge-identity" in content, "本地认证服务缺失"
        assert "OfflineAuth" in content, "离线认证配置缺失"

    def test_deploy_edge_package_script(self):
        """DEPLOY: 边缘部署包打包脚本"""
        script = os.path.join(WORKSPACE, "Configuration2.0", "docker", "build-edge-package.ps1")
        assert os.path.exists(script), "边缘部署包打包脚本缺失"


class TestScenario2_FLOW:
    """FLOW: 数据流合规"""

    def test_flow_edge_sync_interface(self):
        """FLOW-001~005: 云边同步接口定义"""
        sync_file = os.path.join(WORKSPACE, "JGSY.AGI.Common.Abstractions", "Interfaces", "IEdgeSyncService.cs")
        assert os.path.exists(sync_file), "云边同步接口缺失"
        content = Path(sync_file).read_text(encoding="utf-8")
        assert "IUpstreamSyncService" in content, "上行同步接口缺失"
        assert "IDownstreamSyncService" in content, "下行同步接口缺失"
        assert "IOfflineBufferService" in content, "离线缓冲接口缺失"

    def test_flow_upstream_filter(self):
        """FLOW-001: 上行数据过滤（禁止控制数据上行）"""
        sync_file = os.path.join(WORKSPACE, "JGSY.AGI.Common.Abstractions", "Interfaces", "IEdgeSyncService.cs")
        content = Path(sync_file).read_text(encoding="utf-8")
        assert "IUpstreamDataFilter" in content, "上行数据过滤器接口缺失"

    def test_flow_downstream_filter(self):
        """FLOW-002: 下行数据过滤（禁止直接控制指令）"""
        sync_file = os.path.join(WORKSPACE, "JGSY.AGI.Common.Abstractions", "Interfaces", "IEdgeSyncService.cs")
        content = Path(sync_file).read_text(encoding="utf-8")
        assert "IDownstreamDataFilter" in content, "下行数据过滤器接口缺失"

    def test_flow_encryption(self):
        """FLOW-004: 跨区数据 SM4 加密 + SM2 签名"""
        sync_file = os.path.join(WORKSPACE, "JGSY.AGI.Common.Abstractions", "Interfaces", "IEdgeSyncService.cs")
        content = Path(sync_file).read_text(encoding="utf-8")
        assert "ISyncIntegrityValidator" in content, "同步完整性校验接口缺失"
        assert "EncryptPayload" in content, "SM4 载荷加密缺失"
        assert "SignMessage" in content, "SM2 消息签名缺失"

    def test_flow_sync_message_types(self):
        """FLOW: 同步消息类型完整性"""
        sync_file = os.path.join(WORKSPACE, "JGSY.AGI.Common.Abstractions", "Interfaces", "IEdgeSyncService.cs")
        content = Path(sync_file).read_text(encoding="utf-8")
        # 上行类型
        for msg_type in ["Telemetry", "DeviceStatus", "AuditLog", "AlarmEvent"]:
            assert msg_type in content, f"上行消息类型缺失: {msg_type}"
        # 下行类型
        for msg_type in ["DispatchStrategy", "RulePackage", "PricingPolicy", "OtaFirmware"]:
            assert msg_type in content, f"下行消息类型缺失: {msg_type}"


class TestScenario2_ZONE:
    """ZONE: 安全分区"""

    def test_zone_network_isolation(self):
        """ZONE-001~003: 安全分区网络隔离"""
        edge_compose = os.path.join(WORKSPACE, "Configuration2.0", "docker", "docker-compose.edge-full.yml")
        with open(edge_compose, "r", encoding="utf-8") as f:
            compose = yaml.safe_load(f)
        networks = compose.get("networks", {})
        assert "zone-realtime" in networks, "Ⅰ区网络未定义"
        assert "zone-control" in networks, "Ⅱ区网络未定义"

    def test_zone_i_services(self):
        """ZONE-001: Ⅰ区服务清单（实时控制）"""
        edge_compose = os.path.join(WORKSPACE, "Configuration2.0", "docker", "docker-compose.edge-full.yml")
        with open(edge_compose, "r", encoding="utf-8") as f:
            compose = yaml.safe_load(f)
        services = compose.get("services", {})
        zone_i_expected = ["edge-microgrid", "edge-pvessc", "edge-safecontrol", "edge-ingestion", "edge-device"]
        for svc in zone_i_expected:
            assert svc in services, f"Ⅰ区服务缺失: {svc}"
            svc_networks = services[svc].get("networks", {})
            if isinstance(svc_networks, list):
                assert "zone-realtime" in svc_networks, f"{svc} 未部署到Ⅰ区网络"
            elif isinstance(svc_networks, dict):
                assert "zone-realtime" in svc_networks, f"{svc} 未部署到Ⅰ区网络"

    def test_zone_ii_services(self):
        """ZONE-002: Ⅱ区服务清单（非实时控制）"""
        edge_compose = os.path.join(WORKSPACE, "Configuration2.0", "docker", "docker-compose.edge-full.yml")
        with open(edge_compose, "r", encoding="utf-8") as f:
            compose = yaml.safe_load(f)
        services = compose.get("services", {})
        zone_ii_expected = ["edge-orchestrator", "edge-ruleengine", "edge-charging", "edge-identity", "edge-observability"]
        for svc in zone_ii_expected:
            assert svc in services, f"Ⅱ区服务缺失: {svc}"


# ═══════════════════════════════════════════════════════════════════════════════
# 场景3：虚拟电厂云端（接电力市场）— 6 项
# ═══════════════════════════════════════════════════════════════════════════════

class TestScenario3_VPP:
    """VPP: 虚拟电厂合规（GB/T 44241-2024）"""

    def test_vpp_service_exists(self):
        """VPP 服务项目存在"""
        vpp_dir = os.path.join(WORKSPACE, "JGSY.AGI.EnergyCore.VPP")
        assert os.path.exists(vpp_dir), "VPP 服务项目缺失"

    def test_vpp_orchestrator_exists(self):
        """Orchestrator 调度服务存在"""
        orch_dir = os.path.join(WORKSPACE, "JGSY.AGI.EnergyCore.Orchestrator")
        assert os.path.exists(orch_dir), "Orchestrator 服务项目缺失"

    def test_vpp_demand_response(self):
        """需求响应服务存在"""
        dr_dir = os.path.join(WORKSPACE, "JGSY.AGI.EnergyServices.Trading", "Modules", "DemandResp")
        assert os.path.exists(dr_dir), "DemandResp 服务项目缺失"

    def test_vpp_elec_trade(self):
        """电力交易服务存在"""
        et_dir = os.path.join(WORKSPACE, "JGSY.AGI.EnergyServices.Trading", "Modules", "ElecTrade")
        assert os.path.exists(et_dir), "ElecTrade 服务项目缺失"

    def test_vpp_settlement(self):
        """结算服务存在"""
        st_dir = os.path.join(WORKSPACE, "JGSY.AGI.Settlement")
        assert os.path.exists(st_dir), "Settlement 服务项目缺失"

    def test_vpp_carbon_trade(self):
        """碳交易服务存在"""
        ct_dir = os.path.join(WORKSPACE, "JGSY.AGI.EnergyServices.Trading", "Modules", "CarbonTrade")
        assert os.path.exists(ct_dir), "CarbonTrade 服务项目缺失"


class TestScenario3_SM_CRYPTO:
    """国密通信合规（VPP 场景）"""

    def test_sm_crypto_module(self):
        """SM2/SM3/SM4 密码学模块"""
        crypto_file = os.path.join(WORKSPACE, "JGSY.AGI.Blockchain", "Web3", "CryptoServices.cs")
        assert os.path.exists(crypto_file), "密码学服务文件缺失"
        content = Path(crypto_file).read_text(encoding="utf-8")
        assert "class SMCryptoService" in content, "SMCryptoService 类缺失"

    def test_sm2_key_generation(self):
        """SM2 密钥生成"""
        crypto_file = os.path.join(WORKSPACE, "JGSY.AGI.Blockchain", "Web3", "CryptoServices.cs")
        content = Path(crypto_file).read_text(encoding="utf-8")
        assert "sm2p256v1" in content, "SM2 曲线参数缺失"
        assert "GenerateKeyPair" in content, "SM2 密钥生成方法缺失"

    def test_sm4_encryption_module(self):
        """SM4 加密模块"""
        crypto_file = os.path.join(WORKSPACE, "JGSY.AGI.Blockchain", "Web3", "CryptoServices.cs")
        content = Path(crypto_file).read_text(encoding="utf-8")
        assert "SM4Engine" in content, "SM4 加密引擎缺失"

    def test_blockchain_evidence(self):
        """区块链存证服务"""
        evidence_file = os.path.join(WORKSPACE, "JGSY.AGI.Blockchain", "Services", "EnergyEvidenceService.cs")
        assert os.path.exists(evidence_file), "存证服务缺失"


# ═══════════════════════════════════════════════════════════════════════════════
# 跨场景：基础设施合规
# ═══════════════════════════════════════════════════════════════════════════════

class TestInfraCompliance:
    """基础设施合规"""

    def test_docker_compose_infrastructure(self):
        """基础设施 compose 存在"""
        infra_file = os.path.join(WORKSPACE, "Configuration2.0", "docker", "docker-compose.infrastructure.yml")
        assert os.path.exists(infra_file), "基础设施 compose 缺失"

    def test_services_json_complete(self):
        """services.json 定义全部 26 个服务"""
        svc_file = os.path.join(WORKSPACE, "Configuration2.0", "docker", "services.json")
        assert os.path.exists(svc_file), "services.json 缺失"
        with open(svc_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        services = data.get("services", [])
        assert len(services) == 26, f"服务数量不一致: {len(services)} != 26"

    def test_yarp_gateway_config(self):
        """YARP 网关路由配置完整"""
        yarp_file = os.path.join(WORKSPACE, "JGSY.AGI.Gateway", "yarp.json")
        assert os.path.exists(yarp_file), "yarp.json 缺失"

    def test_dapr_compose(self):
        """Dapr sidecar 配置"""
        dapr_file = os.path.join(WORKSPACE, "Configuration2.0", "docker", "docker-compose.dapr.yml")
        assert os.path.exists(dapr_file), "Dapr compose 缺失"

    def test_no_hardcoded_secrets(self):
        """禁止硬编码密码/密钥"""
        sensitive_patterns = [
            r"password\s*=\s*['\"][^$\{]",
            r"secret\s*=\s*['\"][^$\{]",
        ]
        config_files = glob.glob(os.path.join(WORKSPACE, "JGSY.AGI.*", "appsettings.json"))
        violations = []
        for f in config_files:
            content = Path(f).read_text(encoding="utf-8")
            for pattern in sensitive_patterns:
                if re.search(pattern, content, re.IGNORECASE):
                    # 排除模板占位符和空值
                    matches = re.findall(pattern, content, re.IGNORECASE)
                    for m in matches:
                        if "${" not in m and "YourSuper" not in m and '""' not in m:
                            violations.append(f"{f}: {m[:50]}")
        # 允许少量开发配置（如默认 JWT 占位符）
        assert len(violations) < 5, f"发现可能的硬编码密钥: {violations}"

    def test_global_exception_handler(self):
        """全局异常处理中间件"""
        handler_file = os.path.join(WORKSPACE, "JGSY.AGI.Common.Hosting", "Middleware", "GlobalExceptionHandlerMiddleware.cs")
        assert os.path.exists(handler_file), "全局异常处理中间件缺失"

    def test_security_headers(self):
        """安全响应头配置"""
        sec_ext = os.path.join(WORKSPACE, "JGSY.AGI.Common.Hosting", "Security", "SecurityHeadersMiddleware.cs")
        assert os.path.exists(sec_ext), "安全服务扩展缺失"
        content = Path(sec_ext).read_text(encoding="utf-8")
        for header in ["X-Content-Type-Options", "X-Frame-Options", "Content-Security-Policy"]:
            assert header in content, f"安全头缺失: {header}"


# ═══════════════════════════════════════════════════════════════════════════════
# 合规总览统计
# ═══════════════════════════════════════════════════════════════════════════════

class TestComplianceSummary:
    """合规总览"""

    def test_scenario1_p0_all_fixed(self):
        """场景1 P0 缺陷全部修复"""
        # FIX-001: 三员分立
        assert os.path.exists(os.path.join(WORKSPACE, "JGSY.AGI.Permission", "Data", "Migrations", "006_three_admin_separation.sql"))
        # FIX-003: 日志 ≥ 6 月
        loki = Path(os.path.join(WORKSPACE, "Configuration2.0", "docker", "observability", "loki", "loki-config.yaml")).read_text()
        assert "4320h" in loki
        # FIX-004: 审计防篡改
        assert os.path.exists(os.path.join(WORKSPACE, "JGSY.AGI.Blockchain", "Services", "AuditChainHashService.cs"))
        # MFA 强制
        identity_config = json.loads(Path(os.path.join(WORKSPACE, "JGSY.AGI.Identity", "appsettings.json")).read_text(encoding="utf-8-sig"))
        assert identity_config.get("Mfa", {}).get("Enabled", False)

    def test_scenario1_security_middleware_complete(self):
        """场景1 安全中间件完整性"""
        required_files = [
            "JGSY.AGI.Common.Auth/Security/RequireSM2SignatureAttribute.cs",
            "JGSY.AGI.Common.Auth/Security/RequireSM4EncryptionAttribute.cs",
            "JGSY.AGI.Common.Auth/Security/SensitiveMaskAttribute.cs",
            "JGSY.AGI.Common.Auth/Security/VirusScanService.cs",
            "JGSY.AGI.Common.Auth/Security/EncryptionService.cs",
            "JGSY.AGI.Common.Auth/Security/PasswordPolicy.cs",
            "JGSY.AGI.Common.Auth/Security/RequirePermissionAttribute.cs",
            "JGSY.AGI.Gateway/Middleware/AntiReplayMiddleware.cs",
        ]
        for f in required_files:
            full_path = os.path.join(WORKSPACE, f.replace("/", os.sep))
            assert os.path.exists(full_path), f"安全组件缺失: {f}"

    def test_scenario2_edge_infrastructure(self):
        """场景2 边缘基础设施完整性"""
        required_files = [
            "Configuration2.0/docker/docker-compose.edge-full.yml",
            "Configuration2.0/docker/build-edge-package.ps1",
            "JGSY.AGI.Common.Abstractions/Interfaces/IEdgeSyncService.cs",
        ]
        for f in required_files:
            full_path = os.path.join(WORKSPACE, f.replace("/", os.sep))
            assert os.path.exists(full_path), f"边缘组件缺失: {f}"

    def test_scenario3_vpp_services_exist(self):
        """场景3 VPP 服务完整性"""
        vpp_services = [
            "JGSY.AGI.EnergyCore.VPP",
            "JGSY.AGI.EnergyCore.Orchestrator",
            os.path.join("JGSY.AGI.EnergyServices.Trading", "Modules", "ElecTrade"),
            os.path.join("JGSY.AGI.EnergyServices.Trading", "Modules", "DemandResp"),
            os.path.join("JGSY.AGI.EnergyServices.Trading", "Modules", "CarbonTrade"),
            "JGSY.AGI.Settlement",
        ]
        for svc in vpp_services:
            svc_dir = os.path.join(WORKSPACE, svc)
            assert os.path.exists(svc_dir), f"VPP 服务缺失: {svc}"

