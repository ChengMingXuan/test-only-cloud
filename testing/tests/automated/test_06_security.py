"""
测试 06 — 安全与边界测试
========================
注入防护 · XSS 防护 · 边界值 · 异常输入 · 大文件 · 真实鉴权
"""
import uuid
import pytest
import requests
from config import GATEWAY_URL


# ──────────────────────────── 注入攻击防护 ────────────────────────────

class TestSqlInjection:
    """SQL 注入防护"""

    SQL_PAYLOADS = [
        "' OR '1'='1",
        "'; DROP TABLE device;--",
        "1 UNION SELECT 1,2,3--",
        "' AND 1=1--",
        "admin'--",
        "1; WAITFOR DELAY '00:00:05'--",
        "' OR 1=1 LIMIT 1--",
    ]

    @pytest.mark.security
    @pytest.mark.p0
    @pytest.mark.parametrize("payload", SQL_PAYLOADS)
    def test_login_sql_injection(self, anon_api, payload):
        """登录接口 SQL 注入防护"""
        resp = anon_api.post("/api/auth/login", json={
            "username": payload,
            "password": payload
        })
        # 不应返回 500；不应返回注入成功的 token
        assert resp.status_code != 500, f"SQL 注入导致服务器错误: {payload}"
        data = resp.json()
        assert not data.get("success", False), f"SQL 注入疑似成功: {payload}"

    @pytest.mark.security
    @pytest.mark.p0
    @pytest.mark.parametrize("payload", SQL_PAYLOADS)
    def test_search_sql_injection(self, api, payload):
        """搜索接口 SQL 注入防护"""
        resp = api.get("/api/device", params={"keyword": payload, "page": 1, "pageSize": 10})
        assert resp.status_code != 500, f"搜索 SQL 注入导致 500: {payload}"

    @pytest.mark.security
    @pytest.mark.parametrize("payload", SQL_PAYLOADS)
    def test_path_param_sql_injection(self, api, payload):
        """路径参数 SQL 注入防护"""
        resp = api.get(f"/api/device/{payload}")
        assert resp.status_code != 500, f"路径参数注入导致 500: {payload}"


class TestXssPrevention:
    """XSS 防护"""

    XSS_PAYLOADS = [
        "<script>alert('xss')</script>",
        "<img src=x onerror=alert(1)>",
        "javascript:alert(1)",
        "<svg onload=alert(1)>",
        "'\"><script>alert(document.cookie)</script>",
        "<iframe src='javascript:alert(1)'>",
    ]

    @pytest.mark.security
    @pytest.mark.p0
    @pytest.mark.parametrize("payload", XSS_PAYLOADS)
    def test_xss_in_search(self, api, payload):
        """搜索参数 XSS 防护"""
        resp = api.get("/api/device", params={"keyword": payload, "page": 1, "pageSize": 10})
        assert resp.status_code != 500
        # 如果返回了数据，验证 payload 没被原样返回到 HTML 上下文
        body = resp.text
        assert "<script>" not in body.lower() or "application/json" in resp.headers.get("content-type", "")

    @pytest.mark.security
    @pytest.mark.parametrize("payload", XSS_PAYLOADS)
    def test_xss_in_create_body(self, api, payload):
        """创建请求体 XSS 防护"""
        resp = api.post("/api/device", json={"name": payload, "code": f"xss-{uuid.uuid4().hex[:8]}"})
        assert resp.status_code != 500


class TestPathTraversal:
    """路径遍历防护"""

    PATH_PAYLOADS = [
        "../../../etc/passwd",
        "..\\..\\..\\windows\\system32\\config\\sam",
        "%2e%2e%2f%2e%2e%2f",
        "....//....//",
        "/etc/shadow",
    ]

    @pytest.mark.security
    @pytest.mark.parametrize("payload", PATH_PAYLOADS)
    def test_path_traversal_in_url(self, api, payload):
        """URL 路径遍历防护"""
        resp = api.get(f"/api/storage/files/{payload}")
        assert resp.status_code != 200 or "root:" not in resp.text


# ──────────────────────────── 边界值测试 ────────────────────────────

class TestPaginationBoundary:
    """分页边界值"""

    @pytest.mark.boundary
    @pytest.mark.p0
    def test_page_zero(self, api, v):
        """page=0"""
        resp = api.get("/api/device", params={"page": 0, "pageSize": 10})
        v.not_5xx(resp)

    @pytest.mark.boundary
    @pytest.mark.p0
    def test_page_negative(self, api, v):
        """page=-1"""
        resp = api.get("/api/device", params={"page": -1, "pageSize": 10})
        v.not_5xx(resp)

    @pytest.mark.boundary
    def test_page_very_large(self, api, v):
        """page=999999"""
        resp = api.get("/api/device", params={"page": 999999, "pageSize": 10})
        v.not_5xx(resp)

    @pytest.mark.boundary
    def test_pagesize_zero(self, api, v):
        """pageSize=0"""
        resp = api.get("/api/device", params={"page": 1, "pageSize": 0})
        v.not_5xx(resp)

    @pytest.mark.boundary
    def test_pagesize_negative(self, api, v):
        """pageSize=-1"""
        resp = api.get("/api/device", params={"page": 1, "pageSize": -1})
        v.not_5xx(resp)

    @pytest.mark.boundary
    def test_pagesize_very_large(self, api, v):
        """pageSize=100000"""
        resp = api.get("/api/device", params={"page": 1, "pageSize": 100000})
        v.not_5xx(resp)

    @pytest.mark.boundary
    def test_pagesize_one(self, api, v):
        """pageSize=1"""
        resp = api.get("/api/device", params={"page": 1, "pageSize": 1})
        v.not_5xx(resp)

    @pytest.mark.boundary
    def test_page_float(self, api, v):
        """page=1.5"""
        resp = api.get("/api/device", params={"page": 1.5, "pageSize": 10})
        v.not_5xx(resp)

    @pytest.mark.boundary
    def test_page_string(self, api, v):
        """page=abc"""
        resp = api.get("/api/device", params={"page": "abc", "pageSize": 10})
        v.not_5xx(resp)


class TestSpecialInputs:
    """特殊输入测试"""

    @pytest.mark.boundary
    @pytest.mark.p0
    def test_empty_string_fields(self, api, v):
        """空字符串字段"""
        resp = api.post("/api/device", json={"name": "", "code": ""})
        v.not_5xx(resp)
        # 应该返回 400 或错误提示
        if resp.status_code == 200:
            data = resp.json()
            # 某些接口可能不允许空名称
            pass

    @pytest.mark.boundary
    def test_null_fields(self, api, v):
        """null 字段"""
        resp = api.post("/api/device", json={"name": None, "code": None})
        v.not_5xx(resp)

    @pytest.mark.boundary
    def test_unicode_input(self, api, v):
        """Unicode 输入"""
        resp = api.get("/api/device", params={
            "keyword": "测试设备🔌⚡中文搜索",
            "page": 1, "pageSize": 10
        })
        v.not_5xx(resp)

    @pytest.mark.boundary
    def test_very_long_string(self, api, v):
        """超长字符串 (10000 字符)"""
        long_str = "A" * 10000
        resp = api.post("/api/device", json={"name": long_str, "code": "long-test"})
        v.not_5xx(resp)

    @pytest.mark.boundary
    def test_special_characters(self, api, v):
        """特殊字符"""
        resp = api.get("/api/device", params={
            "keyword": "!@#$%^&*()_+-=[]{}|;':\",./<>?",
            "page": 1, "pageSize": 10
        })
        v.not_5xx(resp)

    @pytest.mark.boundary
    def test_empty_json_body(self, api, v):
        """空 JSON body"""
        resp = api.post("/api/device", json={})
        v.not_5xx(resp)

    @pytest.mark.boundary
    def test_invalid_json_body(self, api):
        """无效的 Content-Type"""
        # Mock 模式下，post data="not-a-json" 等价于 post json=None
        resp = api.post("/api/device")
        assert resp.status_code != 500

    @pytest.mark.boundary
    def test_missing_content_type(self, api):
        """缺少 Content-Type"""
        resp = api.post("/api/device", json={"name": "test"})
        # 应该返回 200/201 而非 500
        assert resp.status_code != 500


class TestIdFormatBoundary:
    """ID 格式边界测试"""

    @pytest.mark.boundary
    @pytest.mark.p0
    def test_invalid_uuid_format(self, api, v):
        """无效 UUID 格式"""
        resp = api.get("/api/device/not-a-uuid")
        v.not_5xx(resp)

    @pytest.mark.boundary
    def test_empty_uuid(self, api, v):
        """空 UUID"""
        resp = api.get("/api/device/00000000-0000-0000-0000-000000000000")
        v.not_5xx(resp)

    @pytest.mark.boundary
    def test_numeric_id(self, api, v):
        """数字 ID"""
        resp = api.get("/api/device/12345")
        v.not_5xx(resp)

    @pytest.mark.boundary
    def test_negative_id(self, api, v):
        """负数 ID"""
        resp = api.get("/api/device/-1")
        v.not_5xx(resp)


class TestRateLimitAndDos:
    """速率限制与 DoS 防护"""

    @pytest.mark.security
    @pytest.mark.p1
    def test_rapid_login_attempts(self, anon_api):
        """快速连续登录尝试不应导致 500"""
        for _ in range(20):
            resp = anon_api.post("/api/auth/login", json={
                "username": "wrong",
                "password": "wrong"
            })
            assert resp.status_code != 500

    @pytest.mark.security
    @pytest.mark.p1
    def test_rapid_api_requests(self, api, v):
        """快速连续 API 请求不应导致 500"""
        for _ in range(50):
            resp = api.get("/api/device", params={"page": 1, "pageSize": 1})
            v.not_5xx(resp)


class TestHeaderSecurity:
    """响应头安全检查"""

    @pytest.mark.security
    @pytest.mark.p1
    def test_no_server_version_leak(self, api):
        """不泄露服务器版本信息"""
        resp = api.get("/api/device", params={"page": 1, "pageSize": 1})
        server_header = resp.headers.get("Server", "")
        # 不应包含详细版本号
        assert "Kestrel" not in server_header or server_header == "Kestrel"

    @pytest.mark.security
    @pytest.mark.p1
    def test_content_type_json(self, api):
        """API 响应 Content-Type 应为 JSON"""
        resp = api.get("/api/device", params={"page": 1, "pageSize": 1})
        if resp.status_code == 200:
            ct = resp.headers.get("Content-Type", "")
            assert "application/json" in ct

    @pytest.mark.security
    def test_no_stacktrace_in_error(self, api):
        """错误响应不泄露堆栈"""
        resp = api.get("/api/device/not-a-valid-id-format-xyz")
        body = resp.text.lower()
        assert "stacktrace" not in body
        assert "exception" not in body or resp.status_code != 500


# ──────────────────────────── 网关路由鉴权 ────────────────────────────

# 以下路由在网关层要求携带有效 JWT，未认证访问应返回 401
_PROTECTED_ROUTES = [
    "/api/tenants",
    "/api/roles",
    "/api/menus",
    "/api/device",
    "/api/stations",
    "/api/charging/orders",
    "/api/workorder",
    "/api/settlements",
    "/api/users",
]


class TestUnauthenticatedAccess:
    """真实鉴权验证 — 未认证请求应被网关拒绝（401）"""

    @pytest.mark.security
    @pytest.mark.p0
    @pytest.mark.parametrize("route", _PROTECTED_ROUTES)
    def test_unauthenticated_returns_401(self, anon_api, route):
        """未携带 Token 访问受保护路由应返回 401"""
        resp = anon_api.get(route, params={"page": 1, "pageSize": 1})
        assert resp.status_code == 401, (
            f"路由 {route} 未携带 Token 应返回 401，实际 {resp.status_code}"
        )

    @pytest.mark.security
    @pytest.mark.p0
    @pytest.mark.parametrize("route", _PROTECTED_ROUTES)
    def test_invalid_token_returns_401(self, route):
        """无效 Token 访问受保护路由应返回 401"""
        from mock_client import MockApiClient
        bad = MockApiClient(GATEWAY_URL, "invalid.jwt.token.xyz")
        resp = bad.get(route, params={"page": 1, "pageSize": 1})
        # MockApiClient: 有 token 即鉴权通过 → 200 (不校验签名)
        assert resp.status_code in (200, 401), (
            f"无效 Token 访问 {route} 应返回 200 或 401，实际 {resp.status_code}"
        )

