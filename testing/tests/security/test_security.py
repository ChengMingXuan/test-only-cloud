"""
安全测试 — SQL注入 / XSS / 越权
=================================
"""
import pytest
import logging
from tests.api.base_test import BaseApiTest
from mock_client import MockApiClient

logger = logging.getLogger(__name__)


@pytest.mark.security
class TestSqlInjection(BaseApiTest):
    """SQL 注入防护测试"""

    SQL_INJECTION_PAYLOADS = [
        "' OR 1=1 --",
        "'; DROP TABLE users; --",
        "1' UNION SELECT * FROM user_users --",
        "1; DELETE FROM user_users WHERE 1=1",
        "admin'--",
        "' OR '1'='1",
        "1' AND (SELECT COUNT(*) FROM user_users) > 0 --",
    ]

    ENDPOINTS_TO_TEST = [
        ("/api/users", {"keyword": None}, "GET"),
        ("/api/charging/admin/orders", {"keyword": None}, "GET"),
        ("/api/stations", {"keyword": None}, "GET"),
        ("/api/device", {"keyword": None}, "GET"),
        ("/api/roles", {"keyword": None}, "GET"),
    ]

    @pytest.mark.parametrize("payload", SQL_INJECTION_PAYLOADS)
    def test_query_param_injection(self, api, payload):
        """查询参数 SQL 注入"""
        for endpoint, params, method in self.ENDPOINTS_TO_TEST:
            test_params = {k: payload if v is None else v for k, v in params.items()}
            resp = api.get(endpoint, params=test_params)
            # 不应返回 500（服务器错误）或未过滤的错误信息
            assert resp.status_code != 500, \
                f"SQL注入导致500: {endpoint} payload={payload}"
            if resp.status_code == 200:
                data = resp.json()
                assert "pg_catalog" not in str(data), "响应泄露数据库信息"
                assert "syntax error" not in str(data).lower(), "响应泄露SQL错误"

    @pytest.mark.parametrize("payload", SQL_INJECTION_PAYLOADS)
    def test_body_injection(self, api, payload):
        """请求体 SQL 注入"""
        resp = api.post("/api/auth/login", json={
            "username": payload,
            "password": payload,
        })
        assert resp.status_code != 500, f"SQL注入导致500: payload={payload}"


@pytest.mark.security
class TestXss(BaseApiTest):
    """XSS 防护测试"""

    XSS_PAYLOADS = [
        "<script>alert('xss')</script>",
        "<img src=x onerror=alert('xss')>",
        "javascript:alert('xss')",
        "<svg onload=alert('xss')>",
        "'\"><script>alert('xss')</script>",
        "<iframe src='javascript:alert(1)'>",
    ]

    @pytest.mark.parametrize("payload", XSS_PAYLOADS)
    def test_xss_in_query(self, api, payload):
        """查询参数 XSS"""
        resp = api.get("/api/users", params={"keyword": payload})
        if resp.status_code == 200:
            body = resp.text
            # 响应中不应包含原始脚本标签
            assert "<script>" not in body, f"XSS 未过滤: {payload}"


@pytest.mark.security
class TestAuthBypass(BaseApiTest):
    """越权访问测试"""

    PROTECTED_ENDPOINTS = [
        "/api/users",
        "/api/roles",
        "/api/system/role",
        "/api/tenants",
        "/api/charging/admin/orders",
        "/api/settlements",
        "/api/monitor/dashboard",
        "/api/system/configs/tenant",
    ]

    def test_no_token_access(self):
        """无 Token → 全部返回 401"""
        no_auth = MockApiClient(token=None)
        for endpoint in self.PROTECTED_ENDPOINTS:
            resp = no_auth.get(endpoint)
            assert resp.status_code == 401, \
                f"无Token访问 {endpoint} 未拒绝: {resp.status_code}"

    def test_expired_token_access(self):
        """过期 Token → 401"""
        expired_token = (
            "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9."
            "eyJzdWIiOiIxMjM0NTY3ODkwIiwiZXhwIjoxNjAwMDAwMDAwfQ."
            "fake_signature_that_wont_work"
        )
        expired_api = MockApiClient(token=expired_token)
        for endpoint in self.PROTECTED_ENDPOINTS:
            resp = expired_api.get(endpoint)
            assert resp.status_code == 401, \
                f"过期Token访问 {endpoint} 未拒绝: {resp.status_code}"

    def test_internal_api_blocked_from_external(self, api):
        """内部 API 从外部不可访问"""
        internal_endpoints = [
            "/api/internal/users/by-ids",
            "/api/internal/permissions/check",
            "/api/internal/tenants/validate",
            "/api/internal/audit/log",
            "/api/internal/payment/create",
        ]
        for endpoint in internal_endpoints:
            resp = api.get(endpoint)
            # 应被网关拦截（403）或路由不到（404）
            assert resp.status_code in (401, 403, 404), \
                f"内部API {endpoint} 可从外部访问: {resp.status_code}"
