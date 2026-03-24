"""
JGSY.AGI 安全门禁测试套件 - MFA/CSRF/部署凭据/审计完整性增强
覆盖: IMP-P0-006 / GATE-009 / TEST-P0-002 / TEST-P1-004 / GATE-013

测试分组:
  SEC-MFA: MFA 多因素认证门禁
  SEC-CSRF: CSRF 防护验证
  SEC-DEPLOY: 部署凭据安全验证
  SEC-AUDIT-ENH: 审计日志增强验证
  SEC-HEADER-ENH: HTTP 安全头增强验证
"""

import pytest
import os
import re
import json
import glob

# ============================================================
# 测试配置
# ============================================================

# 仓库根目录
REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))

# 已知弱密码黑名单
WEAK_PASSWORD_BLACKLIST = [
    "P@ssw0rd", "password", "123456", "admin", "root", "test",
    "jgsy_redis_2024", "jgsy_rabbitmq_2024", "jgsy_influx_2024",
    "jgsy_influx_token_2024", "jgsy_internal_service_key_2024_prod_v2!@#",
    "YourSuperSecretKeyForJwtTokenGeneration2024!", "secret", "changeme",
]

# 必须配置凭据的 Compose 字段
COMPOSE_CREDENTIAL_FIELDS = [
    "POSTGRES_PASSWORD", "REDIS_PASSWORD", "RABBITMQ_PASSWORD",
    "JWT_SECRET_KEY", "INTERNAL_SERVICE_KEY", "INFLUXDB_PASSWORD", "INFLUXDB_TOKEN",
]


# ============================================================
# SEC-DEPLOY: 部署凭据安全测试
# ============================================================

class TestDeployCredentialSecurity:
    """部署配置凭据安全验证 (IMP-P0-001/002)"""

    def test_env_example_no_weak_passwords(self):
        """SEC-DEPLOY-001: .env.example 不包含硬编码弱密码"""
        env_file = os.path.join(REPO_ROOT, "Configuration2.0", "docker", ".env.example")
        if not os.path.exists(env_file):
            pytest.skip(".env.example 不存在")

        content = open(env_file, "r", encoding="utf-8").read()
        found_weak = []
        for weak in WEAK_PASSWORD_BLACKLIST:
            if weak in content:
                found_weak.append(weak)
        assert not found_weak, f".env.example 包含弱密码: {found_weak}"

    def test_env_example_uses_placeholders(self):
        """SEC-DEPLOY-002: .env.example 必须使用 <CHANGE_ME_*> 占位符"""
        env_file = os.path.join(REPO_ROOT, "Configuration2.0", "docker", ".env.example")
        if not os.path.exists(env_file):
            pytest.skip(".env.example 不存在")

        content = open(env_file, "r", encoding="utf-8").read()
        # 每个敏感字段的值应该包含 CHANGE_ME
        for field in COMPOSE_CREDENTIAL_FIELDS:
            pattern = rf"^{field}=(.+)$"
            match = re.search(pattern, content, re.MULTILINE)
            if match:
                value = match.group(1).strip()
                assert "CHANGE_ME" in value or value.startswith("<"), \
                    f"{field} 的值 '{value}' 不是占位符格式"

    @pytest.mark.parametrize("compose_file,weak_default", [
        ("Configuration2.0/docker/docker-compose.infrastructure.yml", ":-P@ssw0rd"),
        ("Configuration2.0/docker/docker-compose.infrastructure.yml", ":-jgsy_redis_2024"),
        ("Configuration2.0/docker/docker-compose.infrastructure.yml", ":-jgsy_rabbitmq_2024"),
        ("Configuration2.0/docker/docker-compose.infrastructure.yml", ":-jgsy_influx_2024"),
        ("Configuration2.0/docker/docker-compose.infrastructure.yml", ":-jgsy_influx_token_2024"),
    ])
    def test_compose_no_weak_fallback(self, compose_file, weak_default):
        """SEC-DEPLOY-003: Compose 文件不包含弱密码 fallback 默认值"""
        filepath = os.path.join(REPO_ROOT, compose_file)
        if not os.path.exists(filepath):
            pytest.skip(f"{compose_file} 不存在")

        content = open(filepath, "r", encoding="utf-8").read()
        assert weak_default not in content, \
            f"{compose_file} 包含弱密码 fallback: {weak_default}"

    def test_compose_uses_required_syntax(self):
        """SEC-DEPLOY-004: 基础设施 Compose 使用 :? 必需变量语法"""
        filepath = os.path.join(REPO_ROOT, "Configuration2.0", "docker", "docker-compose.infrastructure.yml")
        if not os.path.exists(filepath):
            pytest.skip("infrastructure compose 不存在")

        content = open(filepath, "r", encoding="utf-8").read()
        # POSTGRES_PASSWORD 应该使用 :? 而非 :- 语法
        assert "POSTGRES_PASSWORD:-" not in content, \
            "POSTGRES_PASSWORD 仍使用 :- fallback 语法，应改为 :? 必需语法"

    def test_edge_env_has_placeholders(self):
        """SEC-DEPLOY-005: 边缘配置模板使用占位符"""
        env_file = os.path.join(REPO_ROOT, "Configuration2.0", "docker", ".env.edge.example")
        if not os.path.exists(env_file):
            pytest.skip(".env.edge.example 不存在")

        content = open(env_file, "r", encoding="utf-8").read()
        assert "<CHANGE_ME" in content, "边缘配置模板缺少 <CHANGE_ME> 占位符"

    def test_prod_env_has_placeholders(self):
        """SEC-DEPLOY-006: 生产环境配置模板使用占位符"""
        env_file = os.path.join(REPO_ROOT, "Configuration2.0", "docker", ".env.prod")
        if not os.path.exists(env_file):
            pytest.skip("Configuration2.0/docker/.env.prod 不存在")

        content = open(env_file, "r", encoding="utf-8").read()
        assert "<CHANGE_ME" in content, "生产环境配置缺少 <CHANGE_ME> 占位符"

    def test_deploy_script_validates_credentials(self):
        """SEC-DEPLOY-007: deploy.ps1 必须验证凭据而非跳过"""
        deploy_script = os.path.join(REPO_ROOT, "Configuration2.0", "docker", "deploy.ps1")
        if not os.path.exists(deploy_script):
            pytest.skip("deploy.ps1 不存在")

        content = open(deploy_script, "r", encoding="utf-8").read()
        # 检查不再使用"跳过占位符"的旧逻辑
        assert "requiredSecrets" in content or "凭据安全检查" in content, \
            "deploy.ps1 缺少凭据安全验证逻辑"

    def test_validate_env_script_exists(self):
        """SEC-DEPLOY-008: validate-env.ps1 凭据验证脚本存在"""
        script = os.path.join(REPO_ROOT, "scripts", "validate-env.ps1")
        assert os.path.exists(script), "scripts/validate-env.ps1 不存在"

    def test_no_hardcoded_secrets_in_csharp(self):
        """SEC-DEPLOY-009: C# 代码不含硬编码密钥（排除安全黑名单/弱密码校验/测试文件）"""
        patterns_to_check = [
            r'"P@ssw0rd"',
            r'"jgsy_redis_2024"',
            r'"jgsy_rabbitmq_2024"',
            r'"YourSuperSecretKeyForJwtTokenGeneration2024!"',
        ]
        # 合法用途文件：安全黑名单、弱密码校验列表、测试/Benchmark 项目
        ALLOWED_FILES = {
            "JwtAuthenticationExtensions.cs",   # UnsafeDefaultKeys 黑名单
            "PasswordPolicyService.cs",          # IsCommonPassword 弱口令校验
            "AuthController.cs",                 # ContentPlatform 弱密码校验列表
        }
        EXCLUDED_PROJECT_PREFIXES = (
            "JGSY.AGI.Test",
            "JGSY.AGI.Benchmarks",
        )
        service_dirs = glob.glob(os.path.join(REPO_ROOT, "JGSY.AGI.*"))
        violations = []
        for svc_dir in service_dirs:
            svc_name = os.path.basename(svc_dir)
            if svc_name.startswith(EXCLUDED_PROJECT_PREFIXES):
                continue
            for cs_file in glob.glob(os.path.join(svc_dir, "**", "*.cs"), recursive=True):
                basename = os.path.basename(cs_file)
                if basename in ALLOWED_FILES:
                    continue
                try:
                    content = open(cs_file, "r", encoding="utf-8-sig").read()
                    for pattern in patterns_to_check:
                        if re.search(pattern, content):
                            violations.append(f"{basename}: {pattern}")
                except (UnicodeDecodeError, PermissionError):
                    pass
        assert not violations, f"发现硬编码密钥: {violations[:5]}"


# ============================================================
# SEC-MFA: MFA 多因素认证门禁
# ============================================================

class TestMFACapability:
    """MFA 多因素认证能力验证 (GATE-013 / TEST-P1-004 / IMP-P1-009)"""

    def _find_csharp_files(self, *patterns):
        """在 C# 文件中搜索模式"""
        service_dirs = glob.glob(os.path.join(REPO_ROOT, "JGSY.AGI.*"))
        results = []
        for svc_dir in service_dirs:
            for cs_file in glob.glob(os.path.join(svc_dir, "**", "*.cs"), recursive=True):
                try:
                    content = open(cs_file, "r", encoding="utf-8-sig").read()
                    for pattern in patterns:
                        if re.search(pattern, content, re.IGNORECASE):
                            results.append(os.path.basename(cs_file))
                            break
                except (UnicodeDecodeError, PermissionError):
                    pass
        return results

    def test_mfa_service_exists(self):
        """SEC-MFA-001: 平台具备 MFA 服务接口"""
        files = self._find_csharp_files(r"IMfaService|IMfaProvider|IMultiFactorAuth")
        assert len(files) > 0, "未找到 MFA 服务接口定义"

    def test_totp_support(self):
        """SEC-MFA-002: 支持 TOTP（基于时间的一次性密码）"""
        files = self._find_csharp_files(r"TOTP|Totp|TotpProvider|OtpNet|GoogleAuthenticator")
        assert len(files) > 0, "未找到 TOTP 相关实现"

    def test_mfa_configuration(self):
        """SEC-MFA-003: MFA 配置在 appsettings 中存在"""
        config_files = glob.glob(os.path.join(REPO_ROOT, "JGSY.AGI.Identity", "**", "appsettings*.json"), recursive=True)
        mfa_configured = False
        for f in config_files:
            try:
                content = open(f, "r", encoding="utf-8-sig").read()
                if "MFA" in content or "MultiFactorAuth" in content or "Mfa" in content:
                    mfa_configured = True
                    break
            except (UnicodeDecodeError, PermissionError):
                pass
        assert mfa_configured, "Identity 服务 appsettings 中未配置 MFA"

    def test_passkey_support(self):
        """SEC-MFA-004: 支持 Passkey 无密码认证 (AUTH-002)"""
        files = self._find_csharp_files(r"IPasskey|PasskeyAuth|WebAuthn|FIDO2")
        assert len(files) > 0, "未找到 Passkey 认证相关实现"

    def test_biometric_support(self):
        """SEC-MFA-005: 支持生物识别认证 (AUTH-004)"""
        files = self._find_csharp_files(r"IBiometric|BiometricAuth|Fingerprint|FaceRecognition")
        assert len(files) > 0, "未找到生物识别认证相关实现"


# ============================================================
# SEC-CSRF: CSRF 防护验证
# ============================================================

class TestCSRFProtection:
    """CSRF 防护能力验证 (OWASP A05)"""

    def test_antiforgery_service_registered(self):
        """SEC-CSRF-001: CSRF 防护已配置（AntiForgery/SameSite Cookie/CORS 均可）"""
        # 搜索范围：Common.Hosting + Gateway（Gateway 已配置 SameSite Cookie）
        search_dirs = [
            os.path.join(REPO_ROOT, "JGSY.AGI.Common.Hosting"),
            os.path.join(REPO_ROOT, "JGSY.AGI.Gateway"),
            os.path.join(REPO_ROOT, "JGSY.AGI.Common.Auth"),
        ]
        csrf_keywords = [
            "AddAntiforgery", "AntiForgery", "ValidateAntiForgeryToken",
            "SameSite", "SameSiteMode",
        ]
        csrf_found = False
        for search_dir in search_dirs:
            if not os.path.isdir(search_dir):
                continue
            for f in glob.glob(os.path.join(search_dir, "**", "*.cs"), recursive=True):
                try:
                    content = open(f, "r", encoding="utf-8-sig").read()
                    if any(kw in content for kw in csrf_keywords):
                        csrf_found = True
                        break
                except (UnicodeDecodeError, PermissionError):
                    pass
            if csrf_found:
                break
        assert csrf_found, \
            "未找到 CSRF 防护（AntiForgery 或 SameSite Cookie 配置）"

    def test_cors_policy_configured(self):
        """SEC-CSRF-002: CORS 策略已配置"""
        gateway_files = glob.glob(os.path.join(REPO_ROOT, "JGSY.AGI.Gateway", "**", "*.cs"), recursive=True)
        cors_found = False
        for f in gateway_files:
            try:
                content = open(f, "r", encoding="utf-8-sig").read()
                if "AddCors" in content or "UseCors" in content or "CorsPolicy" in content:
                    cors_found = True
                    break
            except (UnicodeDecodeError, PermissionError):
                pass
        assert cors_found, "Gateway 未配置 CORS 策略"

    def test_security_headers_middleware(self):
        """SEC-CSRF-003: 安全头中间件存在"""
        security_ext = os.path.join(REPO_ROOT, "JGSY.AGI.Common.Hosting", "Extensions", "SecurityServiceExtensions.cs")
        assert os.path.exists(security_ext), "SecurityServiceExtensions.cs 不存在"

        content = open(security_ext, "r", encoding="utf-8-sig").read()
        required_headers = [
            "X-Frame-Options",
            "X-Content-Type-Options",
            "Strict-Transport-Security",
            "Content-Security-Policy",
            "X-XSS-Protection",
            "Referrer-Policy",
            "Permissions-Policy",
        ]
        missing = [h for h in required_headers if h not in content]
        assert not missing, f"SecurityServiceExtensions 缺少安全头: {missing}"


# ============================================================
# SEC-AUDIT-ENH: 审计日志增强验证
# ============================================================

class TestAuditLogEnhanced:
    """审计日志增强验证 (OWASP A09 / TEST-P1-005 / GATE-014)"""

    def test_audit_middleware_exists(self):
        """SEC-AUDIT-ENH-001: 审计日志中间件存在"""
        files = glob.glob(os.path.join(REPO_ROOT, "JGSY.AGI.Common.Hosting", "**", "*.cs"), recursive=True)
        audit_found = any(
            "AuditLog" in open(f, "r", encoding="utf-8-sig").read()
            for f in files
            if f.endswith(".cs")
        )
        assert audit_found, "未找到审计日志中间件"

    def test_audit_service_interface(self):
        """SEC-AUDIT-ENH-002: 审计日志服务接口定义"""
        files = glob.glob(os.path.join(REPO_ROOT, "JGSY.AGI.Common.*", "**", "*.cs"), recursive=True)
        interface_found = any(
            "IAuditLogService" in open(f, "r", encoding="utf-8-sig").read()
            for f in files
            if f.endswith(".cs")
        )
        assert interface_found, "未找到 IAuditLogService 接口"

    def test_audit_retention_config(self):
        """SEC-AUDIT-ENH-003: 审计日志保留配置已定义"""
        edge_env = os.path.join(REPO_ROOT, "Configuration2.0", "docker", ".env.edge.example")
        if os.path.exists(edge_env):
            content = open(edge_env, "r", encoding="utf-8").read()
            assert "AUDIT_RETENTION" in content, "边缘配置缺少审计日志保留天数配置"

    def test_audit_log_test_file_exists(self):
        """SEC-AUDIT-ENH-004: 审计日志完整性测试文件存在"""
        test_file = os.path.join(REPO_ROOT, "tests", "security", "test_audit_log_integrity.py")
        assert os.path.exists(test_file), "审计日志完整性测试文件不存在"

    def test_no_password_logging(self):
        """SEC-AUDIT-ENH-005: C# 日志不输出密码明文"""
        patterns_forbidden = [
            r'Log.*\$".*password.*\{',  # 插值字符串含 password
            r'Log.*password\s*=\s*\{',   # 结构化日志含 password 参数
        ]
        service_dirs = glob.glob(os.path.join(REPO_ROOT, "JGSY.AGI.*"))
        violations = []
        checked = 0
        for svc_dir in service_dirs:
            for cs_file in glob.glob(os.path.join(svc_dir, "**", "*.cs"), recursive=True):
                try:
                    content = open(cs_file, "r", encoding="utf-8-sig").read()
                    checked += 1
                    for pattern in patterns_forbidden:
                        matches = re.findall(pattern, content, re.IGNORECASE)
                        if matches:
                            violations.append(f"{os.path.basename(cs_file)}: {matches[0][:60]}")
                except (UnicodeDecodeError, PermissionError):
                    pass
        assert not violations, f"发现可能的密码日志泄露: {violations[:5]}"


# ============================================================
# SEC-HEADER-ENH: HTTP 安全头增强验证
# ============================================================

class TestSecurityHeadersEnhanced:
    """HTTP 安全头增强验证 (OWASP A05 / GATE-009)"""

    def test_security_extension_file_exists(self):
        """SEC-HEADER-ENH-001: SecurityServiceExtensions.cs 存在"""
        filepath = os.path.join(REPO_ROOT, "JGSY.AGI.Common.Hosting", "Extensions", "SecurityServiceExtensions.cs")
        assert os.path.exists(filepath)

    @pytest.mark.parametrize("header,expected_value", [
        ("X-Frame-Options", "DENY"),
        ("X-Content-Type-Options", "nosniff"),
        ("X-XSS-Protection", "1; mode=block"),
        ("X-Download-Options", "noopen"),
        ("X-Permitted-Cross-Domain-Policies", "none"),
    ])
    def test_security_header_value(self, header, expected_value):
        """SEC-HEADER-ENH-002: 安全头设置为正确值"""
        filepath = os.path.join(REPO_ROOT, "JGSY.AGI.Common.Hosting", "Extensions", "SecurityServiceExtensions.cs")
        content = open(filepath, "r", encoding="utf-8-sig").read()
        assert expected_value in content, f"{header} 未设置为 {expected_value}"

    def test_hsts_max_age_sufficient(self):
        """SEC-HEADER-ENH-003: HSTS max-age ≥ 31536000 (1年)"""
        filepath = os.path.join(REPO_ROOT, "JGSY.AGI.Common.Hosting", "Extensions", "SecurityServiceExtensions.cs")
        content = open(filepath, "r", encoding="utf-8-sig").read()
        match = re.search(r"max-age=(\d+)", content)
        assert match, "未找到 HSTS max-age 配置"
        max_age = int(match.group(1))
        assert max_age >= 31536000, f"HSTS max-age={max_age} 不足 1 年"

    def test_csp_policy_defined(self):
        """SEC-HEADER-ENH-004: CSP 策略已定义"""
        filepath = os.path.join(REPO_ROOT, "JGSY.AGI.Common.Hosting", "Extensions", "SecurityServiceExtensions.cs")
        content = open(filepath, "r", encoding="utf-8-sig").read()
        assert "Content-Security-Policy" in content, "CSP 策略未定义"
        assert "default-src" in content, "CSP 缺少 default-src 指令"

    def test_permissions_policy_defined(self):
        """SEC-HEADER-ENH-005: Permissions-Policy 定义了敏感能力限制"""
        filepath = os.path.join(REPO_ROOT, "JGSY.AGI.Common.Hosting", "Extensions", "SecurityServiceExtensions.cs")
        content = open(filepath, "r", encoding="utf-8-sig").read()
        restricted_features = ["geolocation", "microphone", "camera"]
        for feature in restricted_features:
            assert feature in content, f"Permissions-Policy 未限制 {feature}"

    def test_referrer_policy_set(self):
        """SEC-HEADER-ENH-006: Referrer-Policy 已配置"""
        filepath = os.path.join(REPO_ROOT, "JGSY.AGI.Common.Hosting", "Extensions", "SecurityServiceExtensions.cs")
        content = open(filepath, "r", encoding="utf-8-sig").read()
        assert "strict-origin-when-cross-origin" in content, \
            "Referrer-Policy 未设置为 strict-origin-when-cross-origin"


# ============================================================
# SEC-K6-SLA: K6 SLA 阈值配置验证
# ============================================================

class TestK6SLAConfiguration:
    """K6 SLA 阈值配置验证 (GATE-008 / TEST-P1-001)"""

    def test_k6_config_exists(self):
        """SEC-K6-SLA-001: k6/config.js 存在"""
        filepath = os.path.join(REPO_ROOT, "k6", "config.js")
        assert os.path.exists(filepath), "k6/config.js 不存在"

    def test_k6_p95_threshold(self):
        """SEC-K6-SLA-002: P95 响应时间阈值 ≤ 2000ms"""
        filepath = os.path.join(REPO_ROOT, "k6", "config.js")
        content = open(filepath, "r", encoding="utf-8").read()
        assert "p(95)<2000" in content, "K6 缺少 P95<2000ms 商用 SLA 阈值"

    def test_k6_p99_threshold(self):
        """SEC-K6-SLA-003: P99 响应时间阈值 ≤ 5000ms"""
        filepath = os.path.join(REPO_ROOT, "k6", "config.js")
        content = open(filepath, "r", encoding="utf-8").read()
        assert "p(99)<5000" in content, "K6 缺少 P99<5000ms 阈值"

    def test_k6_error_rate_threshold(self):
        """SEC-K6-SLA-004: 错误率阈值 < 1%"""
        filepath = os.path.join(REPO_ROOT, "k6", "config.js")
        content = open(filepath, "r", encoding="utf-8").read()
        assert "rate<0.01" in content, "K6 缺少 ErrorRate<1% 阈值"

    def test_k6_scenarios_complete(self):
        """SEC-K6-SLA-005: K6 包含 5 种标准测试场景"""
        filepath = os.path.join(REPO_ROOT, "k6", "config.js")
        content = open(filepath, "r", encoding="utf-8").read()
        required_scenarios = ["smoke", "load", "stress", "spike", "soak"]
        missing = [s for s in required_scenarios if s not in content]
        assert not missing, f"K6 缺少测试场景: {missing}"

    def test_k6_security_test_exists(self):
        """SEC-K6-SLA-006: K6 安全合规测试场景存在"""
        filepath = os.path.join(REPO_ROOT, "k6", "scenarios", "security-compliance-test.js")
        assert os.path.exists(filepath), "k6/scenarios/security-compliance-test.js 不存在"


# ============================================================
# SEC-RELEASE: 发布门禁完整性验证
# ============================================================

class TestReleaseGateCompleteness:
    """发布门禁脚本完整性验证 (IMP-P0-003 / GATE-001/002)"""

    def test_production_ready_gate_exists(self):
        """SEC-RELEASE-001: production-ready-gate.ps1 存在"""
        script = os.path.join(REPO_ROOT, "scripts", "production-ready-gate.ps1")
        assert os.path.exists(script)

    def test_gate_count_sufficient(self):
        """SEC-RELEASE-002: 门禁数量 ≥ 18"""
        script = os.path.join(REPO_ROOT, "scripts", "production-ready-gate.ps1")
        content = open(script, "r", encoding="utf-8-sig").read()
        gate_count = content.count("Write-Gate")
        assert gate_count >= 18, f"门禁数量 {gate_count} < 18"

    def test_credential_gate_exists(self):
        """SEC-RELEASE-003: 凭据安全门禁已纳入"""
        script = os.path.join(REPO_ROOT, "scripts", "production-ready-gate.ps1")
        content = open(script, "r", encoding="utf-8-sig").read()
        assert "凭据安全" in content, "production-ready-gate.ps1 缺少凭据安全门禁"

    def test_sla_gate_exists(self):
        """SEC-RELEASE-004: K6 SLA 门禁已纳入"""
        script = os.path.join(REPO_ROOT, "scripts", "production-ready-gate.ps1")
        content = open(script, "r", encoding="utf-8-sig").read()
        assert "性能SLA" in content or "K6 SLA" in content, \
            "production-ready-gate.ps1 缺少 K6 SLA 性能门禁"

    def test_report_generation_scripts_exist(self):
        """SEC-RELEASE-005: 6+1 报告生成脚本存在"""
        scripts = [
            "scripts/generate-tool-reports.ps1",
            "scripts/aggregate-tool-reports.ps1",
        ]
        missing = [s for s in scripts if not os.path.exists(os.path.join(REPO_ROOT, s))]
        assert not missing, f"缺少报告生成脚本: {missing}"

    def test_release_manual_exists(self):
        """SEC-RELEASE-006: 统一发布手册存在"""
        possible_paths = [
            os.path.join(REPO_ROOT, "docs", "06-运维部署", "发布手册（统一入口）v1.0.md"),
        ]
        found = any(os.path.exists(p) for p in possible_paths)
        assert found, "统一发布手册不存在"
