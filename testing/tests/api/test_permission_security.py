"""
权限与安全 — 全面测试
======================
覆盖：RequirePermission验证 + 未授权访问 + 越权测试 + RBAC
优先级：P0
"""
import pytest
import uuid
import logging
from tests.api.base_test import BaseApiTest

logger = logging.getLogger(__name__)


@pytest.mark.p0
@pytest.mark.security
class TestUnauthorizedAccess(BaseApiTest):
    """未授权访问测试 — 无Token访问受保护API"""

    SERVICE_NAME = "permission"
    API_PREFIX = "/api"

    # 所有需要鉴权的核心端点
    PROTECTED_ENDPOINTS = [
        ("GET", "/api/identity/users"),
        ("GET", "/api/permission/roles"),
        ("GET", "/api/charging/admin/orders"),
        ("GET", "/api/device/devices"),
        ("GET", "/api/station/stations"),
        ("GET", "/api/workorder/workorders"),
        ("GET", "/api/tenant/tenants"),
        ("GET", "/api/vpp/list"),
        ("GET", "/api/carbontrade/dashboard"),
        ("GET", "/api/electrade/market/orders"),
        ("GET", "/api/microgrid/list"),
        ("GET", "/api/blockchain/dashboard"),
        ("GET", "/api/settlement/settlements"),
    ]

    @pytest.mark.parametrize("method,endpoint", PROTECTED_ENDPOINTS)
    def test_unauthorized_returns_401(self, api, method, endpoint):
        """未授权访问返回401"""
        # 使用无Token的请求
        import requests
        from tests.conftest import GATEWAY_URL
        resp = requests.request(method, f"{GATEWAY_URL}{endpoint}",
                                timeout=5, verify=False)
        assert resp.status_code in (401, 403), \
            f"{method} {endpoint} 返回 {resp.status_code}，应为401/403"


@pytest.mark.p0
@pytest.mark.security
class TestPermissionCodeFormat(BaseApiTest):
    """权限码格式验证"""

    SERVICE_NAME = "permission"
    API_PREFIX = "/api/permission"

    def test_all_permissions_have_correct_format(self, api):
        """所有权限码符合 service:resource:action 格式"""
        resp = api.get(f"{self.API_PREFIX}/permissions", params={"pageSize": 500})
        data = self.assert_paged(resp)
        import re
        pattern = re.compile(r'^[a-z_]+:[a-z_]+:[a-z_]+$')
        violations = []
        for perm in data["items"]:
            code = perm.get("permCode", perm.get("code", ""))
            if code and not pattern.match(code):
                violations.append(code)
        assert len(violations) == 0, f"非标权限码: {violations[:10]}"

    def test_super_admin_has_all_permissions(self, api):
        """SUPER_ADMIN角色拥有所有权限"""
        resp = api.get(f"{self.API_PREFIX}/roles/00000000-0000-0000-0000-000000000001/permissions")
        if resp.status_code == 200:
            data = self.assert_success(resp)
            # SUPER_ADMIN应该有大量权限
            if isinstance(data, list):
                assert len(data) >= 50, f"SUPER_ADMIN权限数过少: {len(data)}"
            elif isinstance(data, dict) and "items" in data:
                assert len(data["items"]) >= 50


@pytest.mark.p0
@pytest.mark.security
class TestTenantIsolation(BaseApiTest):
    """多租户隔离验证"""

    SERVICE_NAME = "permission"
    API_PREFIX = "/api"

    def test_cross_tenant_access_blocked(self, api):
        """跨租户访问被阻止"""
        # 尝试用当前Token访问其他租户的数据
        fake_tenant = "00000000-0000-0000-0000-000000000099"
        resp = api.get(f"{self.API_PREFIX}/charging/admin/orders",
                       params={"tenantId": fake_tenant, "pageSize": 1})
        # 应返回空数据或403
        if resp.status_code == 200:
            data = self.assert_paged(resp)
            # 返回的数据不应属于其他租户
            for item in data["items"]:
                actual_tenant = item.get("tenantId", item.get("tenant_id"))
                if actual_tenant:
                    assert actual_tenant != fake_tenant, "跨租户数据泄露！"


@pytest.mark.p1
@pytest.mark.security
class TestMenuPermission(BaseApiTest):
    """菜单权限测试"""

    SERVICE_NAME = "permission"
    API_PREFIX = "/api/permission"

    def test_list_menus(self, api):
        """查询菜单列表"""
        resp = api.get(f"{self.API_PREFIX}/menus", params={"pageSize": 100})
        self.assert_paged(resp)

    def test_menu_tree(self, api):
        """获取菜单树"""
        resp = api.get(f"{self.API_PREFIX}/menus/tree")
        assert resp.status_code in (200, 404)

    def test_user_menus(self, api):
        """获取当前用户菜单"""
        resp = api.get(f"{self.API_PREFIX}/menus/user")
        assert resp.status_code in (200, 404)


@pytest.mark.p1
@pytest.mark.security
class TestApiSecurity(BaseApiTest):
    """API安全边界测试"""

    SERVICE_NAME = "permission"
    API_PREFIX = "/api"

    def test_sql_injection_prevention(self, api):
        """SQL注入防护"""
        resp = api.get(f"{self.API_PREFIX}/identity/users", params={
            "keyword": "' OR 1=1 --"
        })
        # 不应崩溃，应正常返回空结果或400
        assert resp.status_code in (200, 400)

    def test_xss_prevention(self, api):
        """XSS防护"""
        resp = api.get(f"{self.API_PREFIX}/identity/users", params={
            "keyword": "<script>alert(1)</script>"
        })
        assert resp.status_code in (200, 400)

    def test_oversized_payload(self, api):
        """超大载荷防护"""
        resp = api.post(f"{self.API_PREFIX}/identity/users", json={
            "username": "a" * 10000,
            "password": "b" * 10000,
        })
        assert resp.status_code in (400, 413, 422)
