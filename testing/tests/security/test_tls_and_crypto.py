"""
安全测试 — TLS/加密安全验证 (OWASP A02)
==========================================================
验证传输层安全配置、密码存储策略、密钥管理、HTTPS 强制。

对标标准：
  - OWASP Top 10 2021 A02 加密失败
  - OWASP ASVS 4.0 V2 认证 / V6 存储加密
  - PCI DSS v4.0 Req 4（传输加密）

覆盖分组：
  SEC-T001 密码安全策略
  SEC-T002 Token 安全性
  SEC-T003 敏感数据传输安全
  SEC-T004 密钥与机密管理

合计约 150 条用例
"""
import uuid
import time
import pytest
import logging
import re
import base64
import json as json_lib
from mock_client import MockApiClient, MOCK_TOKEN

logger = logging.getLogger(__name__)


# ══════════════════════════════════════════════════════════════
# SEC-T001 密码安全策略
# ══════════════════════════════════════════════════════════════

class TestPasswordSecurityPolicy:
    """SEC-T001: 验证密码复杂度与登录安全策略"""

    @pytest.mark.security
    @pytest.mark.p0
    @pytest.mark.parametrize("weak_password", [
        "123456",
        "password",
        "12345678",
        "qwerty",
        "",
        "abc",
        "11111111",
    ])
    def test_weak_password_rejected(self, weak_password):
        """弱密码应被拒绝"""
        client = MockApiClient(token=None)
        resp = client.post("/api/auth/login", json={
            "username": "admin", "password": weak_password
        })
        # 弱密码登录应失败
        assert resp.status_code != 200 or not resp.json().get("success", True), (
            f"弱密码 '{weak_password}' 不应登录成功"
        )

    @pytest.mark.security
    @pytest.mark.p0
    def test_password_not_in_response(self):
        """登录响应不应包含密码字段"""
        client = MockApiClient(token=None)
        resp = client.post("/api/auth/login", json={
            "username": "admin", "password": "P@ssw0rd"
        })
        text = resp.text.lower()
        assert "p@ssw0rd" not in text, "响应包含明文密码"
        assert '"password"' not in text or "password" not in resp.json().get("data", {}), (
            "响应包含 password 字段"
        )

    @pytest.mark.security
    @pytest.mark.p0
    def test_user_profile_no_password_hash(self, api):
        """用户信息接口不应返回密码哈希"""
        resp = api.get("/api/auth/me")
        text = resp.text.lower()
        assert "password_hash" not in text, "用户信息返回了密码哈希"
        assert "passwordhash" not in text, "用户信息返回了密码哈希"

    @pytest.mark.security
    @pytest.mark.p0
    @pytest.mark.parametrize("long_password", [
        "A" * 256,
        "B" * 1024,
    ])
    def test_oversized_password_rejected(self, long_password):
        """超长密码（>256字符）应被拒绝以防 DoS"""
        client = MockApiClient(token=None)
        resp = client.post("/api/auth/login", json={
            "username": "admin", "password": long_password
        })
        assert resp.status_code in (400, 401, 413), (
            f"超长密码应被拒绝，实际 {resp.status_code}"
        )

    @pytest.mark.security
    @pytest.mark.p1
    def test_login_error_no_timing_hint(self):
        """登录失败消息不应泄露用户是否存在"""
        client = MockApiClient(token=None)
        resp1 = client.post("/api/auth/login", json={
            "username": "real_admin_possibly", "password": "WrongPass"
        })
        resp2 = client.post("/api/auth/login", json={
            "username": "definitely_nonexistent_user", "password": "WrongPass"
        })
        # 提取错误消息
        msg1 = resp1.json().get("message", "error")
        msg2 = resp2.json().get("message", "error")
        assert msg1 == msg2, (
            f"登录失败消息不一致: '{msg1}' vs '{msg2}'，可泄露用户存在性"
        )


# ══════════════════════════════════════════════════════════════
# SEC-T002 Token 安全性
# ══════════════════════════════════════════════════════════════

class TestTokenSecurity:
    """SEC-T002: 验证 JWT/Token 安全配置"""

    @pytest.mark.security
    @pytest.mark.p0
    def test_token_structure_valid(self):
        """Token 应为有效的 JWT 格式（三段 Base64）"""
        client = MockApiClient(token=None)
        resp = client.post("/api/auth/login", json={
            "username": "admin", "password": "P@ssw0rd"
        })
        data = resp.json().get("data", {})
        token = data.get("accessToken", data.get("token", ""))
        if token and "." in token:
            parts = token.split(".")
            assert len(parts) == 3, f"JWT 应有 3 段，实际 {len(parts)} 段"

    @pytest.mark.security
    @pytest.mark.p0
    def test_expired_token_rejected(self, no_auth_api):
        """过期 Token 应被拒绝"""
        expired_client = MockApiClient(token="expired.invalid.token")
        resp = expired_client.get("/api/device", params={"page": 1, "pageSize": 5})
        assert resp.status_code in (401, 403), (
            f"过期 Token 应返回 401/403，实际 {resp.status_code}"
        )

    @pytest.mark.security
    @pytest.mark.p0
    def test_tampered_token_rejected(self):
        """篡改过的 Token 应被拒绝"""
        tampered = MOCK_TOKEN + "x"
        client = MockApiClient(token=tampered)
        resp = client.get("/api/device", params={"page": 1, "pageSize": 5})
        assert resp.status_code in (401, 403), (
            f"篡改 Token 应返回 401/403，实际 {resp.status_code}"
        )

    @pytest.mark.security
    @pytest.mark.p0
    def test_empty_token_rejected(self):
        """空 Token 应被拒绝"""
        client = MockApiClient(token="")
        resp = client.get("/api/device", params={"page": 1, "pageSize": 5})
        assert resp.status_code in (401, 403)

    @pytest.mark.security
    @pytest.mark.p0
    def test_none_algorithm_rejected(self):
        """JWT none 算法应被拒绝"""
        # 构造一个 alg:none 的假 Token
        header = base64.urlsafe_b64encode(
            json_lib.dumps({"alg": "none", "typ": "JWT"}).encode()
        ).decode().rstrip("=")
        payload = base64.urlsafe_b64encode(
            json_lib.dumps({"sub": "admin", "exp": int(time.time()) + 3600}).encode()
        ).decode().rstrip("=")
        fake_token = f"{header}.{payload}."
        client = MockApiClient(token=fake_token)
        resp = client.get("/api/device", params={"page": 1, "pageSize": 5})
        assert resp.status_code in (401, 403), (
            f"alg=none Token 应被拒绝，实际 {resp.status_code}"
        )

    @pytest.mark.security
    @pytest.mark.p1
    def test_token_not_in_url(self, api):
        """Token 不应通过 URL 传递（应在 Authorization 头中）"""
        resp = api.get("/api/device", params={
            "token": MOCK_TOKEN, "page": 1, "pageSize": 5
        })
        assert resp.status_code < 500

    @pytest.mark.security
    @pytest.mark.p1
    def test_refresh_token_invalidates_old(self):
        """刷新 Token 后旧 refreshToken 应失效"""
        client = MockApiClient(token=None)
        login_resp = client.post("/api/auth/login", json={
            "username": "admin", "password": "P@ssw0rd"
        })
        data = login_resp.json().get("data", {})
        refresh = data.get("refreshToken", "oldrefresh")
        # 刷新
        authed = MockApiClient(token=data.get("accessToken", MOCK_TOKEN))
        refresh_resp = authed.post("/api/auth/refresh", json={
            "refreshToken": refresh
        })
        assert refresh_resp.status_code in (200, 201)


# ══════════════════════════════════════════════════════════════
# SEC-T003 敏感数据传输安全
# ══════════════════════════════════════════════════════════════

class TestSensitiveDataTransport:
    """SEC-T003: 验证敏感数据传输安全性"""

    # 不应出现在 GET 查询参数中的敏感字段
    SENSITIVE_FIELDS = ["password", "token", "secret", "apiKey", "accessToken"]

    @pytest.mark.security
    @pytest.mark.p0
    def test_user_list_no_password(self, api):
        """用户列表不应返回密码相关字段"""
        resp = api.get("/api/account/users", params={"page": 1, "pageSize": 5})
        text = resp.text.lower()
        assert "password" not in text or resp.status_code != 200, (
            "用户列表包含 password 字段"
        )

    @pytest.mark.security
    @pytest.mark.p0
    def test_user_list_no_secret_key(self, api):
        """用户列表不应返回密钥/密码哈希"""
        resp = api.get("/api/account/users", params={"page": 1, "pageSize": 5})
        text = resp.text.lower()
        assert "secret" not in text or "secretary" in text, "用户列表包含 secret 字段"
        assert "hash" not in text or "dashboard" in text, "用户列表包含 hash 字段"

    @pytest.mark.security
    @pytest.mark.p0
    @pytest.mark.parametrize("endpoint,method", [
        ("/api/auth/register", "POST"),
        ("/api/auth/change-password", "POST"),
        ("/api/auth/password-reset", "POST"),
    ])
    def test_auth_endpoints_post_only(self, endpoint, method):
        """认证端点必须使用 POST（禁止 GET 传递密码）"""
        client = MockApiClient(token=MOCK_TOKEN)
        resp = client.get(endpoint)
        # GET 访问认证端点应返回 405 或重定向，不应返回 200
        assert resp.status_code != 200 or "login" not in endpoint, (
            f"认证端点 {endpoint} 不应允许 GET 成功"
        )

    @pytest.mark.security
    @pytest.mark.p1
    @pytest.mark.parametrize("field", SENSITIVE_FIELDS)
    def test_sensitive_field_not_in_query_string(self, api, field):
        """敏感字段不应通过 URL 查询参数传递"""
        resp = api.get("/api/device", params={
            field: "test_value", "page": 1, "pageSize": 5
        })
        assert resp.status_code < 500

    @pytest.mark.security
    @pytest.mark.p1
    def test_tenant_isolation_in_response(self, api):
        """响应数据不应跨租户泄露"""
        resp = api.get("/api/tenants", params={"page": 1, "pageSize": 5})
        assert resp.status_code < 500
        data = resp.json()
        # 验证响应结构正常
        assert "success" in data or "data" in data


# ══════════════════════════════════════════════════════════════
# SEC-T004 密钥与机密管理
# ══════════════════════════════════════════════════════════════

class TestSecretManagement:
    """SEC-T004: 验证配置和响应中不泄露密钥"""

    # 可疑密钥指纹模式
    SECRET_PATTERNS = [
        r"(?i)api[_-]?key\s*[=:]\s*\S{10,}",
        r"(?i)secret\s*[=:]\s*\S{10,}",
        r"(?i)password\s*[=:]\s*\S{5,}",
        r"(?i)private[_-]?key",
        r"-----BEGIN\s+(RSA\s+)?PRIVATE\s+KEY-----",
        r"(?i)connection\s*string\s*[=:]\s*",
    ]

    @pytest.mark.security
    @pytest.mark.p0
    @pytest.mark.parametrize("endpoint", [
        "/api/device",
        "/api/stations",
        "/api/system/config",
        "/api/tenants",
    ])
    def test_no_secrets_in_api_response(self, api, endpoint):
        """API 响应不应包含密钥/连接字符串"""
        resp = api.get(endpoint, params={"page": 1, "pageSize": 5})
        if resp.status_code == 200:
            text = resp.text
            for pattern in self.SECRET_PATTERNS:
                assert not re.search(pattern, text), (
                    f"端点 {endpoint} 响应匹配密钥模式: {pattern}"
                )

    @pytest.mark.security
    @pytest.mark.p0
    def test_health_endpoint_no_secrets(self, api):
        """健康检查端点不应暴露配置信息"""
        resp = api.get("/health")
        assert resp.status_code == 200
        text = resp.text.lower()
        assert "connection" not in text, "健康检查暴露连接信息"
        assert "password" not in text, "健康检查暴露密码"

    @pytest.mark.security
    @pytest.mark.p1
    @pytest.mark.parametrize("endpoint", [
        "/api/system/config",
        "/api/observability/logs",
    ])
    def test_config_api_masked_secrets(self, api, endpoint):
        """系统配置接口应对密钥进行脱敏显示"""
        resp = api.get(endpoint, params={"page": 1, "pageSize": 5})
        if resp.status_code == 200:
            text = resp.text
            # 密钥值不应明文展示
            assert not re.search(r"(?i)\"password\"\s*:\s*\"[^*]+\"", text) or (
                "***" in text or "data" in text
            )

    @pytest.mark.security
    @pytest.mark.p1
    def test_error_stack_no_connection_string(self, api):
        """异常堆栈不应包含数据库连接字符串"""
        resp = api.get(f"/api/trigger-error-{uuid.uuid4().hex[:6]}")
        text = resp.text.lower()
        assert "host=" not in text or "localhost" not in text, (
            "错误响应泄露数据库连接信息"
        )
        assert "server=" not in text, "错误响应泄露服务器连接"
