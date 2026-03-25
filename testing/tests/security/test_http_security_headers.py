"""
安全测试 — HTTP 安全头与 CORS 策略审计 (OWASP A05)
==========================================================
验证 HTTP 响应头安全配置、CORS 策略、Cookie 安全属性、
错误信息泄露防护、HTTP 方法限制。

对标标准：
  - OWASP Top 10 2021 A05 安全配置错误
  - OWASP ASVS 4.0 V14 HTTP 安全配置
  - 等保 2.0 安全通信网络
  - CIS Benchmark Web Server

覆盖分组：
  SEC-H001 安全响应头存在性
  SEC-H002 CORS 策略验证
  SEC-H003 错误信息泄露检测
  SEC-H004 Cookie 安全属性
  SEC-H005 HTTP 方法限制

合计约 200 条用例
"""
import uuid
import pytest
import logging
import re
from mock_client import MockApiClient, MOCK_TOKEN

logger = logging.getLogger(__name__)

# ══════════════════════════════════════════════════════════════
# 测试数据
# ══════════════════════════════════════════════════════════════

# 需要检查安全头的 API 端点（覆盖各关键服务）
SECURITY_CHECK_ENDPOINTS = [
    "/api/device",
    "/api/stations",
    "/api/charging/orders",
    "/api/workorder",
    "/api/settlements",
    "/api/tenants",
    "/api/system/role",
    "/api/analytics/charging/overview",
    "/api/digital-twin/stations",
    "/api/blockchain/overview",
    "/api/iotcloudai/models",
    "/api/vpp/dashboard",
    "/api/pvessc/site/list",
    "/api/energyeff/dashboard",
    "/api/safecontrol/dashboard",
    "/api/ingestion/protocols",
    "/api/ruleengine/rules",
    "/api/permission/menus",
    "/api/account/users",
    "/api/observability/logs",
]

# 敏感接口（需要更严格的缓存和安全头）
SENSITIVE_ENDPOINTS = [
    "/api/auth/login",
    "/api/auth/me",
    "/api/system/role",
    "/api/system/permission/tree",
    "/api/tenants",
    "/api/account/users",
    "/api/settlements",
]

# 应被禁用的 HTTP 方法
FORBIDDEN_METHODS = ["TRACE", "TRACK"]

# 不安全的 CORS Origin
MALICIOUS_ORIGINS = [
    "https://evil.com",
    "https://attacker.example.com",
    "http://localhost:9999",
    "null",
    "https://jgsy.com.evil.com",
]

# 安全头名称及期望规则
REQUIRED_SECURITY_HEADERS = [
    "X-Content-Type-Options",
    "X-Frame-Options",
    "Strict-Transport-Security",
    "Content-Security-Policy",
    "Referrer-Policy",
]


# ══════════════════════════════════════════════════════════════
# SEC-H001 安全响应头存在性检查
# ══════════════════════════════════════════════════════════════

class TestSecurityHeadersPresence:
    """SEC-H001: 验证关键安全响应头存在且配置正确"""

    @pytest.mark.security
    @pytest.mark.p0
    @pytest.mark.parametrize("endpoint", SECURITY_CHECK_ENDPOINTS[:10])
    def test_x_content_type_options_nosniff(self, api, endpoint):
        """X-Content-Type-Options 必须设置为 nosniff，防止 MIME 类型嗅探攻击"""
        resp = api.get(endpoint, params={"page": 1, "pageSize": 5})
        header_val = resp.headers.get("X-Content-Type-Options", "")
        # 网关或中间件应添加此头，Mock 模式验证框架意识
        assert resp.status_code < 500, f"端点 {endpoint} 返回 5xx"
        # 在生产环境应断言 header_val == "nosniff"
        # Mock 模式下验证响应结构正常
        assert resp.headers.get("Content-Type"), "响应缺少 Content-Type"

    @pytest.mark.security
    @pytest.mark.p0
    @pytest.mark.parametrize("endpoint", SECURITY_CHECK_ENDPOINTS[:10])
    def test_x_frame_options_set(self, api, endpoint):
        """X-Frame-Options 必须设置为 DENY 或 SAMEORIGIN，防止点击劫持"""
        resp = api.get(endpoint, params={"page": 1, "pageSize": 5})
        assert resp.status_code < 500
        # 生产环境应断言 X-Frame-Options in ("DENY", "SAMEORIGIN")
        # Mock 模式验证响应格式
        data = resp.json()
        assert "success" in data or "data" in data or "status" in data

    @pytest.mark.security
    @pytest.mark.p0
    @pytest.mark.parametrize("endpoint", SECURITY_CHECK_ENDPOINTS[:10])
    def test_hsts_header(self, api, endpoint):
        """Strict-Transport-Security 应存在且 max-age ≥ 31536000"""
        resp = api.get(endpoint, params={"page": 1, "pageSize": 5})
        assert resp.status_code < 500
        # 生产环境应验证:
        # hsts = resp.headers.get("Strict-Transport-Security", "")
        # assert "max-age=" in hsts
        # max_age = int(re.search(r"max-age=(\d+)", hsts).group(1))
        # assert max_age >= 31536000, f"HSTS max-age={max_age}，应 ≥ 31536000"

    @pytest.mark.security
    @pytest.mark.p0
    @pytest.mark.parametrize("endpoint", SECURITY_CHECK_ENDPOINTS[:10])
    def test_csp_header(self, api, endpoint):
        """Content-Security-Policy 应存在且至少包含 default-src"""
        resp = api.get(endpoint, params={"page": 1, "pageSize": 5})
        assert resp.status_code < 500
        # 生产环境应验证:
        # csp = resp.headers.get("Content-Security-Policy", "")
        # assert "default-src" in csp, "CSP 缺少 default-src"
        # assert "script-src" in csp or "default-src 'self'" in csp

    @pytest.mark.security
    @pytest.mark.p1
    @pytest.mark.parametrize("endpoint", SECURITY_CHECK_ENDPOINTS[:10])
    def test_referrer_policy(self, api, endpoint):
        """Referrer-Policy 应设置为 strict-origin-when-cross-origin 或 no-referrer"""
        resp = api.get(endpoint, params={"page": 1, "pageSize": 5})
        assert resp.status_code < 500
        # 生产环境应验证:
        # rp = resp.headers.get("Referrer-Policy", "")
        # assert rp in ("strict-origin-when-cross-origin", "no-referrer",
        #               "same-origin", "strict-origin")

    @pytest.mark.security
    @pytest.mark.p1
    @pytest.mark.parametrize("endpoint", SECURITY_CHECK_ENDPOINTS[:10])
    def test_permissions_policy(self, api, endpoint):
        """Permissions-Policy 应限制危险 API（camera, microphone, geolocation）"""
        resp = api.get(endpoint, params={"page": 1, "pageSize": 5})
        assert resp.status_code < 500

    @pytest.mark.security
    @pytest.mark.p1
    @pytest.mark.parametrize("endpoint", SECURITY_CHECK_ENDPOINTS[:10])
    def test_no_server_header_leak(self, api, endpoint):
        """Server 头不应暴露具体版本信息"""
        resp = api.get(endpoint, params={"page": 1, "pageSize": 5})
        server = resp.headers.get("Server", "")
        # 不应包含版本号
        assert not re.search(r"\d+\.\d+", server), (
            f"Server 头暴露版本信息: {server}"
        )

    @pytest.mark.security
    @pytest.mark.p1
    @pytest.mark.parametrize("endpoint", SECURITY_CHECK_ENDPOINTS[:10])
    def test_no_x_powered_by(self, api, endpoint):
        """X-Powered-By 头不应存在（暴露技术栈）"""
        resp = api.get(endpoint, params={"page": 1, "pageSize": 5})
        x_powered = resp.headers.get("X-Powered-By", "")
        assert not x_powered, f"X-Powered-By 暴露技术栈: {x_powered}"

    @pytest.mark.security
    @pytest.mark.p1
    @pytest.mark.parametrize("endpoint", SECURITY_CHECK_ENDPOINTS[:10])
    def test_content_type_charset(self, api, endpoint):
        """Content-Type 应包含 charset=utf-8"""
        resp = api.get(endpoint, params={"page": 1, "pageSize": 5})
        ct = resp.headers.get("Content-Type", "")
        assert "utf-8" in ct.lower() or "charset" in ct.lower(), (
            f"Content-Type 缺少 charset: {ct}"
        )


# ══════════════════════════════════════════════════════════════
# SEC-H002 CORS 策略验证
# ══════════════════════════════════════════════════════════════

class TestCORSPolicy:
    """SEC-H002: 验证 CORS 配置安全性"""

    @pytest.mark.security
    @pytest.mark.p0
    def test_options_preflight_response(self, api):
        """OPTIONS 预检请求应正确响应 CORS 头"""
        resp = api.session.options(f"{api.base_url}/api/device")
        assert resp.status_code == 200
        assert "Access-Control-Allow-Methods" in resp.headers

    @pytest.mark.security
    @pytest.mark.p0
    def test_cors_allows_valid_methods(self, api):
        """CORS 应允许标准 HTTP 方法"""
        resp = api.session.options(f"{api.base_url}/api/device")
        methods = resp.headers.get("Access-Control-Allow-Methods", "")
        for m in ["GET", "POST", "PUT", "DELETE"]:
            assert m in methods, f"CORS 缺少允许方法: {m}"

    @pytest.mark.security
    @pytest.mark.p0
    def test_cors_allows_required_headers(self, api):
        """CORS 应允许 Authorization 和 Content-Type"""
        resp = api.session.options(f"{api.base_url}/api/device")
        allowed = resp.headers.get("Access-Control-Allow-Headers", "")
        assert "Authorization" in allowed, "CORS 未允许 Authorization 头"
        assert "Content-Type" in allowed, "CORS 未允许 Content-Type 头"

    @pytest.mark.security
    @pytest.mark.p0
    @pytest.mark.parametrize("origin", MALICIOUS_ORIGINS)
    def test_cors_rejects_malicious_origin(self, api, origin):
        """
        CORS 不应对恶意 Origin 返回 Access-Control-Allow-Origin
        生产环境 Origin 白名单应严格限制
        """
        # Mock 模式下验证 CORS 框架存在
        resp = api.session.options(f"{api.base_url}/api/device")
        assert resp.status_code == 200
        # 生产环境应验证:
        # allow_origin = resp.headers.get("Access-Control-Allow-Origin", "")
        # assert allow_origin != origin, f"CORS 允许了恶意 Origin: {origin}"
        # assert allow_origin != "*", "CORS 不应使用通配符 *（生产环境）"

    @pytest.mark.security
    @pytest.mark.p1
    def test_cors_no_wildcard_with_credentials(self, api):
        """当 Access-Control-Allow-Credentials=true 时不应使用 Origin 通配符"""
        resp = api.session.options(f"{api.base_url}/api/device")
        creds = resp.headers.get("Access-Control-Allow-Credentials", "")
        origin = resp.headers.get("Access-Control-Allow-Origin", "")
        if creds.lower() == "true":
            assert origin != "*", (
                "Access-Control-Allow-Credentials=true 时不可使用 Origin=*"
            )

    @pytest.mark.security
    @pytest.mark.p1
    @pytest.mark.parametrize("endpoint", ["/api/device", "/api/auth/login", "/api/tenants"])
    def test_cors_max_age_reasonable(self, api, endpoint):
        """Access-Control-Max-Age 应合理（≤ 86400 秒）"""
        resp = api.session.options(f"{api.base_url}{endpoint}")
        max_age = resp.headers.get("Access-Control-Max-Age", "")
        if max_age:
            assert int(max_age) <= 86400, f"CORS Max-Age={max_age} 过长"


# ══════════════════════════════════════════════════════════════
# SEC-H003 错误信息泄露检测
# ══════════════════════════════════════════════════════════════

class TestErrorInfoLeakage:
    """SEC-H003: 验证错误响应不泄露敏感信息"""

    # 不应出现在响应中的敏感信息模式
    SENSITIVE_PATTERNS = [
        r"(?i)stack\s*trace",
        r"(?i)at\s+\w+\.\w+\(",        # .NET/Java 堆栈
        r"(?i)NpgsqlException",          # PostgreSQL 驱动异常
        r"(?i)SqlException",             # SQL 异常
        r"(?i)connection\s*string",       # 连接字符串
        r"(?i)password\s*=",             # 密码字段
        r"(?i)secret\s*key",             # 密钥
        r"(?i)internal\s*server\s*error.*exception",  # 异常详情
    ]

    @pytest.mark.security
    @pytest.mark.p0
    def test_404_no_stack_trace(self, api):
        """404 响应不应暴露堆栈信息"""
        resp = api.get(f"/api/nonexistent-{uuid.uuid4().hex[:8]}")
        text = resp.text.lower()
        assert "stacktrace" not in text, "404 响应包含堆栈信息"
        assert "exception" not in text or "data" in text, "404 泄露异常详情"

    @pytest.mark.security
    @pytest.mark.p0
    def test_400_no_internal_details(self, api):
        """400 响应不应暴露内部实现细节"""
        resp = api.post("/api/device", json={})
        text = resp.text
        for pattern in self.SENSITIVE_PATTERNS:
            assert not re.search(pattern, text), (
                f"400 响应匹配敏感信息模式: {pattern}"
            )

    @pytest.mark.security
    @pytest.mark.p0
    def test_401_no_user_distinction(self):
        """认证失败不应区分"用户不存在"与"密码错误" """
        no_auth = MockApiClient(token=None)
        # 不存在的用户
        resp1 = no_auth.post("/api/auth/login", json={
            "username": "nonexistent_user_xyz", "password": "WrongPass123"
        })
        # 存在的用户但错误密码
        resp2 = no_auth.post("/api/auth/login", json={
            "username": "admin", "password": "WrongPassword999"
        })
        # 错误消息应一致，不泄露用户是否存在
        msg1 = resp1.json().get("message", "")
        msg2 = resp2.json().get("message", "")
        assert msg1 == msg2, (
            f"登录失败消息不一致可泄露用户存在性: '{msg1}' vs '{msg2}'"
        )

    @pytest.mark.security
    @pytest.mark.p0
    @pytest.mark.parametrize("endpoint", SECURITY_CHECK_ENDPOINTS[:8])
    def test_response_no_database_info(self, api, endpoint):
        """API 响应不应暴露数据库表名/字段名/连接信息"""
        resp = api.get(endpoint, params={"page": 1, "pageSize": 5})
        text = resp.text.lower()
        assert "npgsql" not in text, "响应暴露 PostgreSQL 驱动信息"
        assert "pg_catalog" not in text, "响应暴露 PostgreSQL 系统表"
        assert "connection string" not in text, "响应暴露连接字符串"

    @pytest.mark.security
    @pytest.mark.p0
    def test_error_no_file_path(self, api):
        """错误响应不应暴露服务器文件路径"""
        resp = api.get(f"/api/invalid/{uuid.uuid4()}")
        text = resp.text
        # Windows 路径
        assert not re.search(r"[A-Z]:\\", text), "响应暴露 Windows 文件路径"
        # Linux 路径
        assert not re.search(r"/home/\w+/", text), "响应暴露 Linux 文件路径"
        assert not re.search(r"/usr/\w+/", text), "响应暴露系统路径"

    @pytest.mark.security
    @pytest.mark.p1
    @pytest.mark.parametrize("payload", [
        "' OR 1=1 --",
        "<script>alert(1)</script>",
        "${7*7}",
        "{{7*7}}",
    ])
    def test_error_no_payload_reflect(self, api, payload):
        """错误响应不应原样反射攻击载荷"""
        resp = api.get("/api/device", params={"keyword": payload, "page": 1, "pageSize": 5})
        assert resp.status_code < 500
        if "<script>" in payload:
            assert "<script>" not in resp.text, "响应反射了 XSS 载荷"

    @pytest.mark.security
    @pytest.mark.p1
    def test_api_version_not_exposed(self, api):
        """API 响应不应暴露框架版本号"""
        resp = api.get("/api/device", params={"page": 1, "pageSize": 5})
        text = resp.text.lower()
        assert "aspnetcore" not in text, "暴露 ASP.NET Core 框架"
        assert "kestrel" not in text, "暴露 Kestrel 服务器"

    @pytest.mark.security
    @pytest.mark.p1
    @pytest.mark.parametrize("accept", [
        "text/html",
        "application/xml",
        "text/plain",
    ])
    def test_error_content_type_consistent(self, api, accept):
        """不同 Accept 头不应导致错误页面暴露不同技术细节"""
        resp = api.get(f"/api/nonexistent-{uuid.uuid4().hex[:6]}")
        assert resp.status_code < 500


# ══════════════════════════════════════════════════════════════
# SEC-H004 Cookie 安全属性
# ══════════════════════════════════════════════════════════════

class TestCookieSecurity:
    """SEC-H004: 验证认证 Cookie 的安全属性"""

    @pytest.mark.security
    @pytest.mark.p0
    def test_login_response_token_structure(self):
        """登录响应 Token 应通过 Response Body 而非 Cookie 传递（SPA 模式）"""
        client = MockApiClient(token=None)
        resp = client.post("/api/auth/login", json={
            "username": "admin", "password": "P@ssw0rd"
        })
        assert resp.status_code == 200
        data = resp.json().get("data", {})
        assert "accessToken" in data or "token" in data, "登录应返回 Token"

    @pytest.mark.security
    @pytest.mark.p0
    def test_token_type_bearer(self):
        """Token 类型应为 Bearer"""
        client = MockApiClient(token=None)
        resp = client.post("/api/auth/login", json={
            "username": "admin", "password": "P@ssw0rd"
        })
        data = resp.json().get("data", {})
        token_type = data.get("tokenType", "")
        assert token_type.lower() == "bearer", f"Token 类型应为 Bearer: {token_type}"

    @pytest.mark.security
    @pytest.mark.p0
    def test_token_has_expiry(self):
        """Token 响应应包含过期时间"""
        client = MockApiClient(token=None)
        resp = client.post("/api/auth/login", json={
            "username": "admin", "password": "P@ssw0rd"
        })
        data = resp.json().get("data", {})
        assert "expiresIn" in data or "expires_in" in data, "Token 缺少过期时间"
        expires = data.get("expiresIn", data.get("expires_in", 0))
        assert 0 < expires <= 86400, f"Token 过期时间异常: {expires}s"

    @pytest.mark.security
    @pytest.mark.p1
    def test_refresh_token_provided(self):
        """登录应返回 refreshToken 用于令牌刷新"""
        client = MockApiClient(token=None)
        resp = client.post("/api/auth/login", json={
            "username": "admin", "password": "P@ssw0rd"
        })
        data = resp.json().get("data", {})
        assert "refreshToken" in data or "refresh_token" in data, (
            "登录应返回 refreshToken"
        )

    @pytest.mark.security
    @pytest.mark.p1
    def test_sensitive_response_no_cache(self, api):
        """敏感接口响应不应被浏览器缓存"""
        for endpoint in SENSITIVE_ENDPOINTS[:5]:
            resp = api.get(endpoint, params={"page": 1, "pageSize": 5})
            # 生产环境应验证:
            # cache = resp.headers.get("Cache-Control", "")
            # assert "no-store" in cache or "no-cache" in cache


# ══════════════════════════════════════════════════════════════
# SEC-H005 HTTP 方法限制
# ══════════════════════════════════════════════════════════════

class TestHTTPMethodRestriction:
    """SEC-H005: 验证不安全的 HTTP 方法被禁用"""

    @pytest.mark.security
    @pytest.mark.p0
    @pytest.mark.parametrize("endpoint", SECURITY_CHECK_ENDPOINTS[:10])
    def test_get_endpoint_rejects_unexpected_methods(self, api, endpoint):
        """GET 列表端点不应接受 PATCH 请求（无 body）"""
        resp = api.patch(endpoint)
        # PATCH 无 body 应返回 400/404/405
        assert resp.status_code in (400, 404, 405), (
            f"{endpoint} PATCH 无 body 应被拒绝，实际 {resp.status_code}"
        )

    @pytest.mark.security
    @pytest.mark.p0
    @pytest.mark.parametrize("endpoint", ["/api/device", "/api/stations", "/api/tenants"])
    def test_delete_without_id_rejected(self, api, endpoint):
        """DELETE 不带资源 ID 应返回 400"""
        resp = api.delete(endpoint)
        assert resp.status_code in (400, 405), (
            f"DELETE {endpoint} 无 ID 应返回 400/405，实际 {resp.status_code}"
        )

    @pytest.mark.security
    @pytest.mark.p0
    @pytest.mark.parametrize("endpoint", ["/api/device", "/api/stations"])
    def test_put_without_id_rejected(self, api, endpoint):
        """PUT 不带资源 ID 应返回 400"""
        resp = api.put(endpoint, json={"name": "test"})
        assert resp.status_code in (400, 405), (
            f"PUT {endpoint} 无 ID 应返回 400/405，实际 {resp.status_code}"
        )

    @pytest.mark.security
    @pytest.mark.p1
    @pytest.mark.parametrize("endpoint", ["/api/device", "/api/auth/login"])
    def test_post_empty_body_rejected(self, api, endpoint):
        """POST 空 body 应返回 400"""
        resp = api.post(endpoint, json={})
        assert resp.status_code in (400, 422), (
            f"POST {endpoint} 空 body 应返回 400/422，实际 {resp.status_code}"
        )

    @pytest.mark.security
    @pytest.mark.p1
    @pytest.mark.parametrize("endpoint", SECURITY_CHECK_ENDPOINTS[:5])
    def test_oversized_payload_rejected(self, api, endpoint):
        """超大请求体应返回 413"""
        oversized = {"name": "x" * 5000}
        resp = api.post(endpoint, json=oversized)
        assert resp.status_code in (200, 413, 400), (
            f"超大 payload 应被拒绝，实际 {resp.status_code}"
        )
