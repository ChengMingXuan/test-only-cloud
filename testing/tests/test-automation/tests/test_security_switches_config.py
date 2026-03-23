"""
SecuritySwitches 双环境配置验证 - 增量测试（v2.4.6）
覆盖：
  - SecuritySwitches 配置节点完整性（11 个开关）
  - Dev/Prod JSON 文件存在性与内容正确性
  - appsettings.Security.json 默认值
  - 26 服务环境配置一致性
  - 密码/密钥占位符合规性（无硬编码）
  - RequireHttpsMetadata 配置驱动验证
  - HSTS 条件化中间件验证

100% Mock（不连接真实服务），仅做静态代码/配置分析
"""
import pytest
import json
import os
import re
import glob
from pathlib import Path

# ==================== 常量 ====================

REPO_ROOT = Path(__file__).resolve().parents[4]  # testing/tests/test-automation/tests → 向上4层到 aiops.v2

# 26 个后端微服务
BACKEND_SERVICES = [
    "Account", "Analytics", "Blockchain", "Charging",
    "ContentPlatform", "Device", "DigitalTwin",
    "EnergyCore.MicroGrid", "EnergyCore.Orchestrator",
    "EnergyCore.PVESSC", "EnergyCore.VPP",
    "EnergyServices.Operations", "EnergyServices.Trading",
    "Gateway", "Identity", "Ingestion", "IotCloudAI",
    "Observability", "Permission", "RuleEngine",
    "Settlement", "Simulator", "Station", "Storage",
    "Tenant", "WorkOrder",
]

# SecuritySwitches 11 个标准开关
HTTPS_SWITCHES = ["UseHttps", "ForceHttpsRedirection", "RequireHttpsMetadata", "HstsEnabled"]
SECURITY_SWITCHES = [
    "DbEnableSsl", "RedisEnableSsl", "RedisUseAcl",
    "Sm4Enabled", "KeyRotationEnabled", "SessionControlEnabled", "MtlsEnabled",
]
ALL_SWITCHES = HTTPS_SWITCHES + SECURITY_SWITCHES

# 禁止出现的弱密码
FORBIDDEN_SECRETS = [
    "P@ssw0rd", "password", "123456", "admin123",
    "jgsy_redis_2024", "jgsy_rabbitmq_2024",
    "your-256-bit-secret", "your-secret-key",
]


def _load_json(path: Path) -> dict:
    """安全加载 JSON 文件"""
    with open(path, "r", encoding="utf-8-sig") as f:
        return json.load(f)


def _get_service_dir(service_name: str) -> Path:
    return REPO_ROOT / f"JGSY.AGI.{service_name}"


# ==================== 1. 环境JSON文件存在性 ====================

class TestEnvironmentJsonExistence:
    """验证所有 26 服务的 Dev/Prod JSON 文件存在"""

    @pytest.mark.parametrize("service", BACKEND_SERVICES)
    def test_development_json_exists(self, service):
        """[CFG-ENV-01] {service} 存在 appsettings.Development.json"""
        path = _get_service_dir(service) / "appsettings.Development.json"
        assert path.exists(), f"{service} 缺失 appsettings.Development.json"

    @pytest.mark.parametrize("service", BACKEND_SERVICES)
    def test_production_json_exists(self, service):
        """[CFG-ENV-02] {service} 存在 appsettings.Production.json"""
        path = _get_service_dir(service) / "appsettings.Production.json"
        assert path.exists(), f"{service} 缺失 appsettings.Production.json"


# ==================== 2. Dev 配置内容验证 ====================

class TestDevelopmentConfig:
    """验证 Development 配置 HTTPS=false, 安全开关按需"""

    @pytest.mark.parametrize("service", BACKEND_SERVICES)
    def test_dev_https_switches_are_false(self, service):
        """[CFG-DEV-01] {service} Dev环境 HTTPS 四开关 = false"""
        path = _get_service_dir(service) / "appsettings.Development.json"
        cfg = _load_json(path)
        ss = cfg.get("SecuritySwitches", {})
        for sw in HTTPS_SWITCHES:
            assert ss.get(sw) is False, (
                f"{service} Dev: SecuritySwitches.{sw} 应为 false，实际={ss.get(sw)}"
            )

    @pytest.mark.parametrize("service", BACKEND_SERVICES)
    def test_dev_swagger_enabled(self, service):
        """[CFG-DEV-02] {service} Dev环境 Swagger.Enabled = true"""
        path = _get_service_dir(service) / "appsettings.Development.json"
        cfg = _load_json(path)
        sw = cfg.get("Swagger", {})
        assert sw.get("Enabled") is True, f"{service} Dev: Swagger.Enabled 应为 true"

    @pytest.mark.parametrize("service", BACKEND_SERVICES)
    def test_dev_serilog_debug(self, service):
        """[CFG-DEV-03] {service} Dev环境 Serilog.Default = Debug"""
        path = _get_service_dir(service) / "appsettings.Development.json"
        cfg = _load_json(path)
        level = cfg.get("Serilog", {}).get("MinimumLevel", {}).get("Default", "")
        assert level == "Debug", f"{service} Dev: Serilog.Default 应为 Debug，实际={level}"


# ==================== 3. Prod 配置内容验证 ====================

class TestProductionConfig:
    """验证 Production 配置 HTTPS=true"""

    @pytest.mark.parametrize("service", BACKEND_SERVICES)
    def test_prod_https_switches_are_true(self, service):
        """[CFG-PROD-01] {service} Prod环境 HTTPS 四开关 = true"""
        path = _get_service_dir(service) / "appsettings.Production.json"
        cfg = _load_json(path)
        ss = cfg.get("SecuritySwitches", {})
        for sw in HTTPS_SWITCHES:
            assert ss.get(sw) is True, (
                f"{service} Prod: SecuritySwitches.{sw} 应为 true，实际={ss.get(sw)}"
            )

    @pytest.mark.parametrize("service", BACKEND_SERVICES)
    def test_prod_swagger_disabled(self, service):
        """[CFG-PROD-02] {service} Prod环境 Swagger.Enabled = false"""
        path = _get_service_dir(service) / "appsettings.Production.json"
        cfg = _load_json(path)
        sw = cfg.get("Swagger", {})
        assert sw.get("Enabled") is False, f"{service} Prod: Swagger.Enabled 应为 false"

    @pytest.mark.parametrize("service", BACKEND_SERVICES)
    def test_prod_serilog_warning(self, service):
        """[CFG-PROD-03] {service} Prod环境 Serilog.Default = Warning"""
        path = _get_service_dir(service) / "appsettings.Production.json"
        cfg = _load_json(path)
        level = cfg.get("Serilog", {}).get("MinimumLevel", {}).get("Default", "")
        assert level == "Warning", f"{service} Prod: Serilog.Default 应为 Warning，实际={level}"


# ==================== 4. appsettings.Security.json 基线验证 ====================

class TestSecurityJsonBaseline:
    """验证公共 Security.json 包含 SecuritySwitches 默认值"""

    def test_security_json_has_security_switches(self):
        """[CFG-SEC-01] appsettings.Security.json 包含 SecuritySwitches 节点"""
        path = REPO_ROOT / "JGSY.AGI.Common.Hosting" / "appsettings.Security.json"
        cfg = _load_json(path)
        assert "SecuritySwitches" in cfg, "Security.json 缺失 SecuritySwitches 节点"

    def test_security_json_default_https_false(self):
        """[CFG-SEC-02] SecuritySwitches HTTPS 默认值 = false（安全起见）"""
        path = REPO_ROOT / "JGSY.AGI.Common.Hosting" / "appsettings.Security.json"
        cfg = _load_json(path)
        ss = cfg["SecuritySwitches"]
        for sw in HTTPS_SWITCHES:
            assert ss.get(sw) is False, f"Security.json: {sw} 默认应为 false"

    def test_security_json_all_11_switches_present(self):
        """[CFG-SEC-03] SecuritySwitches 节点包含全部 11 个开关"""
        path = REPO_ROOT / "JGSY.AGI.Common.Hosting" / "appsettings.Security.json"
        cfg = _load_json(path)
        ss = cfg["SecuritySwitches"]
        for sw in ALL_SWITCHES:
            assert sw in ss, f"Security.json: 缺失开关 {sw}"


# ==================== 5. 硬编码密码检测 ====================

class TestNoHardcodedSecrets:
    """检测配置文件中禁止出现弱密码/默认密钥"""

    @pytest.mark.parametrize("service", BACKEND_SERVICES)
    def test_appsettings_no_forbidden_secrets(self, service):
        """[CFG-SEC-10] {service} appsettings.json 无弱密码"""
        path = _get_service_dir(service) / "appsettings.json"
        if not path.exists():
            pytest.skip(f"{service} 无 appsettings.json")
        content = path.read_text(encoding="utf-8-sig")
        for secret in FORBIDDEN_SECRETS:
            assert secret not in content, (
                f"{service}/appsettings.json 包含禁止的密钥: {secret}"
            )

    def test_security_json_no_forbidden_secrets(self):
        """[CFG-SEC-11] appsettings.Security.json 无弱密码"""
        path = REPO_ROOT / "JGSY.AGI.Common.Hosting" / "appsettings.Security.json"
        content = path.read_text(encoding="utf-8-sig")
        for secret in FORBIDDEN_SECRETS:
            assert secret not in content, f"Security.json 包含禁止的密钥: {secret}"


# ==================== 6. C# 代码静态验证 ====================

class TestCodePatterns:
    """静态分析关键代码模式"""

    def test_jwt_extensions_reads_config(self):
        """[CFG-CODE-01] JwtAuthenticationExtensions 使用 SecuritySwitches 配置"""
        path = REPO_ROOT / "JGSY.AGI.Common.Auth" / "Authentication" / "JwtAuthenticationExtensions.cs"
        content = path.read_text(encoding="utf-8-sig")
        assert "SecuritySwitches:RequireHttpsMetadata" in content, (
            "JwtAuthenticationExtensions 未引用 SecuritySwitches:RequireHttpsMetadata"
        )
        assert 'RequireHttpsMetadata = true' not in content, (
            "JwtAuthenticationExtensions 仍硬编码 RequireHttpsMetadata = true"
        )

    def test_gateway_program_reads_config(self):
        """[CFG-CODE-02] Gateway/Program.cs 使用 SecuritySwitches 配置"""
        path = REPO_ROOT / "JGSY.AGI.Gateway" / "Program.cs"
        content = path.read_text(encoding="utf-8-sig")
        assert "SecuritySwitches:ForceHttpsRedirection" in content
        assert "SecuritySwitches:HstsEnabled" in content
        assert "SecuritySwitches:RequireHttpsMetadata" in content

    def test_gateway_hsts_middleware_conditional(self):
        """[CFG-CODE-03] Gateway SecurityHeadersMiddleware HSTS 条件化"""
        path = REPO_ROOT / "JGSY.AGI.Gateway" / "Middleware" / "SecurityHeadersMiddleware.cs"
        content = path.read_text(encoding="utf-8-sig")
        assert "IConfiguration" in content, "Gateway SecurityHeadersMiddleware 需注入 IConfiguration"
        assert "HstsEnabled" in content, "Gateway SecurityHeadersMiddleware 需检查 HstsEnabled"

    def test_common_hsts_middleware_conditional(self):
        """[CFG-CODE-04] Common.Hosting SecurityHeadersMiddleware HSTS 条件化"""
        path = REPO_ROOT / "JGSY.AGI.Common.Hosting" / "Security" / "SecurityHeadersMiddleware.cs"
        content = path.read_text(encoding="utf-8-sig")
        assert "IConfiguration" in content
        assert "HstsEnabled" in content

    def test_security_switches_options_class_exists(self):
        """[CFG-CODE-05] SecuritySwitchesOptions 类存在且包含 11 个属性"""
        path = REPO_ROOT / "JGSY.AGI.Common.Auth" / "Security" / "SecuritySwitchesOptions.cs"
        assert path.exists(), "SecuritySwitchesOptions.cs 不存在"
        content = path.read_text(encoding="utf-8-sig")
        for sw in ALL_SWITCHES:
            assert sw in content, f"SecuritySwitchesOptions 缺失属性 {sw}"

    def test_security_service_extensions_registers_options(self):
        """[CFG-CODE-06] SecurityServiceExtensions 注册 SecuritySwitchesOptions"""
        path = REPO_ROOT / "JGSY.AGI.Common.Hosting" / "Extensions" / "SecurityServiceExtensions.cs"
        content = path.read_text(encoding="utf-8-sig")
        assert "SecuritySwitchesOptions" in content, (
            "SecurityServiceExtensions 未注册 SecuritySwitchesOptions"
        )


# ==================== 7. 密钥占位符合规 ====================

class TestPasswordPlaceholders:
    """验证密码配置使用 ${ENV_VAR} 占位符模式"""

    @pytest.mark.parametrize("service", BACKEND_SERVICES)
    def test_connection_string_uses_env_placeholder(self, service):
        """[CFG-PW-01] {service} 连接字符串密码使用 ${} 占位符"""
        path = _get_service_dir(service) / "appsettings.json"
        if not path.exists():
            pytest.skip(f"{service} 无 appsettings.json")
        content = path.read_text(encoding="utf-8-sig")
        # 检查 PostgreSQL 连接字符串中是否有明文密码
        pg_pattern = re.compile(r'Password\s*=\s*([^;$"\r\n]+)', re.IGNORECASE)
        for match in pg_pattern.finditer(content):
            pwd = match.group(1).strip()
            # 允许 ${ENV} 占位符
            if not pwd.startswith("${"):
                assert False, (
                    f"{service}: 连接字符串密码未使用占位符，"
                    f"发现明文: Password={pwd[:20]}..."
                )


# ==================== 8. 跨服务Dev/Prod一致性 ====================

class TestCrossServiceConsistency:
    """验证全部 26 服务 Dev/Prod 配置结构一致"""

    def test_all_dev_configs_have_same_structure(self):
        """[CFG-CONSIST-01] 所有 Dev JSON 具有相同键集"""
        key_sets = {}
        for svc in BACKEND_SERVICES:
            path = _get_service_dir(svc) / "appsettings.Development.json"
            if path.exists():
                cfg = _load_json(path)
                key_sets[svc] = set(cfg.keys())

        if not key_sets:
            pytest.skip("无 Dev JSON 文件")
        reference = list(key_sets.values())[0]
        for svc, keys in key_sets.items():
            assert keys == reference, (
                f"{svc} Dev JSON 键集不一致: "
                f"多余={keys - reference}, 缺少={reference - keys}"
            )

    def test_all_prod_configs_have_same_structure(self):
        """[CFG-CONSIST-02] 所有 Prod JSON 具有相同键集"""
        key_sets = {}
        for svc in BACKEND_SERVICES:
            path = _get_service_dir(svc) / "appsettings.Production.json"
            if path.exists():
                cfg = _load_json(path)
                key_sets[svc] = set(cfg.keys())

        if not key_sets:
            pytest.skip("无 Prod JSON 文件")
        reference = list(key_sets.values())[0]
        for svc, keys in key_sets.items():
            assert keys == reference, (
                f"{svc} Prod JSON 键集不一致: "
                f"多余={keys - reference}, 缺少={reference - keys}"
            )
