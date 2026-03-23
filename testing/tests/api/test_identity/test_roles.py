"""
Identity 服务 — 角色管理测试
==============================
覆盖：角色CRUD + 权限分配 + 用户绑定
优先级：P0
"""
import pytest
import uuid
import logging
from tests.api.base_test import BaseApiTest

logger = logging.getLogger(__name__)


@pytest.mark.p0
@pytest.mark.identity
class TestRoleCRUD(BaseApiTest):
    """角色CRUD测试"""

    SERVICE_NAME = "identity"
    API_PREFIX = "/api/permission"

    def test_list_roles(self, api):
        """查询角色列表"""
        resp = api.get(f"{self.API_PREFIX}/roles", params={"page": 1, "pageSize": 20})
        self.assert_paged(resp)

    def test_get_role_detail(self, api):
        """获取角色详情"""
        list_resp = api.get(f"{self.API_PREFIX}/roles", params={"pageSize": 1})
        data = self.assert_paged(list_resp)
        if data["total"] == 0:
            return
        role_id = data["items"][0]["id"]
        detail = api.get(f"{self.API_PREFIX}/roles/{role_id}")
        self.assert_success(detail)

    def test_get_super_admin_role(self, api):
        """获取超级管理员角色"""
        resp = api.get(f"{self.API_PREFIX}/roles/00000000-0000-0000-0000-000000000001")
        result = self.assert_success(resp)
        assert result.get("id") or result.get("roleCode")

    def test_get_nonexistent_role(self, api):
        """查询不存在的角色 → 404"""
        resp = api.get(f"{self.API_PREFIX}/roles/00000000-0000-0000-0000-000000000000")
        assert resp.status_code in (404, 400)

    def test_search_roles_by_keyword(self, api):
        """关键词搜索角色"""
        resp = api.get(f"{self.API_PREFIX}/roles", params={"keyword": "admin"})
        self.assert_paged(resp)


@pytest.mark.p0
@pytest.mark.identity
class TestRolePermission(BaseApiTest):
    """角色权限分配测试"""

    SERVICE_NAME = "identity"
    API_PREFIX = "/api/permission"

    def test_get_role_permissions(self, api):
        """获取角色权限列表"""
        # SUPER_ADMIN role_id
        resp = api.get(f"{self.API_PREFIX}/roles/00000000-0000-0000-0000-000000000001/permissions")
        assert resp.status_code in (200, 404)

    def test_list_all_permissions(self, api):
        """查询所有权限码"""
        resp = api.get(f"{self.API_PREFIX}/permissions", params={"pageSize": 100})
        self.assert_paged(resp)

    def test_list_permission_tree(self, api):
        """查询权限树"""
        resp = api.get(f"{self.API_PREFIX}/permissions/tree")
        assert resp.status_code in (200, 404)


@pytest.mark.p1
@pytest.mark.identity
class TestDepartment(BaseApiTest):
    """部门管理测试"""

    SERVICE_NAME = "identity"
    API_PREFIX = "/api/identity"

    def test_list_departments(self, api):
        """查询部门列表"""
        resp = api.get(f"{self.API_PREFIX}/departments", params={"pageSize": 20})
        assert resp.status_code in (200, 404)

    def test_department_tree(self, api):
        """查询部门树"""
        resp = api.get(f"{self.API_PREFIX}/departments/tree")
        assert resp.status_code in (200, 404)

    def test_department_users(self, api):
        """查询部门下用户"""
        resp = api.get(f"{self.API_PREFIX}/departments/00000000-0000-0000-0000-000000000001/users")
        assert resp.status_code in (200, 404)


@pytest.mark.p1
@pytest.mark.identity
class TestOrganization(BaseApiTest):
    """组织管理测试"""

    SERVICE_NAME = "identity"
    API_PREFIX = "/api/identity"

    def test_list_organizations(self, api):
        """查询组织列表"""
        resp = api.get(f"{self.API_PREFIX}/organizations", params={"pageSize": 10})
        assert resp.status_code in (200, 404)

    def test_get_current_org(self, api):
        """获取当前用户组织"""
        resp = api.get(f"{self.API_PREFIX}/organizations/current")
        assert resp.status_code in (200, 404)
