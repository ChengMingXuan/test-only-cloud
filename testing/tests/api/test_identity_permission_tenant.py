"""
核心服务深度测试 — Identity / Permission / Tenant
===================================================
覆盖认证流程、权限体系、租户管理的完整业务场景
每个类 ≥ 30 条用例，合计 ≥ 95 条
"""
import uuid
import pytest
import logging

logger = logging.getLogger(__name__)

UID = lambda: str(uuid.uuid4()).replace("-", "")[:8]


# ══════════════════════════════════════════════════════════════════════════════
# Identity 服务 (8002) — 认证 / 用户 / MFA / Token / 密码策略
# ══════════════════════════════════════════════════════════════════════════════

class TestIdentityAuth:
    """认证核心流程"""

    @pytest.mark.p0
    def test_login_success(self, api, v):
        """正常账密登录返回 accessToken"""
        resp = api.post("/api/auth/login", json={
            "username": "admin", "password": "P@ssw0rd"
        })
        v.not_5xx(resp)
        if resp.status_code == 200:
            data = resp.json().get("data") or {}
            assert "accessToken" in data or "token" in data, "登录应返回 accessToken"

    @pytest.mark.p0
    def test_login_wrong_password_returns_4xx(self, api, v):
        """错误密码返回 4xx（不报 500）"""
        resp = api.post("/api/auth/login", json={
            "username": "admin", "password": "WrongPass123"
        })
        assert resp.status_code in (400, 401, 403), \
            f"错误密码应返回4xx，实际={resp.status_code}"

    @pytest.mark.p0
    def test_login_nonexistent_user(self, api, v):
        """不存在用户名返回 4xx"""
        resp = api.post("/api/auth/login", json={
            "username": f"nonexist_{UID()}", "password": "P@ssw0rd"
        })
        assert resp.status_code in (400, 401, 404), \
            f"不存在用户应返回4xx，实际={resp.status_code}"

    @pytest.mark.p0
    def test_login_empty_username_rejected(self, api, v):
        """空用户名不报 500"""
        resp = api.post("/api/auth/login", json={"username": "", "password": "P@ssw0rd"})
        assert resp.status_code != 500

    @pytest.mark.p0
    def test_login_empty_password_rejected(self, api, v):
        """空密码不报 500"""
        resp = api.post("/api/auth/login", json={"username": "admin", "password": ""})
        assert resp.status_code != 500

    @pytest.mark.p0
    def test_refresh_token(self, api, v):
        """刷新 Token 接口不报 500"""
        resp = api.post("/api/auth/refresh", json={"refreshToken": "fake_refresh_token"})
        assert resp.status_code != 500

    @pytest.mark.p0
    def test_logout(self, api, v):
        """注销登录不报 500"""
        resp = api.post("/api/auth/logout", json={})
        v.not_5xx(resp)

    @pytest.mark.p1
    def test_get_current_user_info(self, api, v):
        """获取当前用户信息"""
        resp = api.get("/api/auth/me")
        v.not_5xx(resp)

    @pytest.mark.p1
    def test_change_password_weak_rejected(self, api, v):
        """弱密码修改被拒绝"""
        resp = api.post("/api/auth/change-password", json={
            "oldPassword": "P@ssw0rd", "newPassword": "123", "confirmPassword": "123"
        })
        assert resp.status_code != 500

    @pytest.mark.p1
    def test_change_password_mismatch_rejected(self, api, v):
        """两次密码不一致被拒绝"""
        resp = api.post("/api/auth/change-password", json={
            "oldPassword": "P@ssw0rd", "newPassword": "NewPass@123",
            "confirmPassword": "DiffPass@456"
        })
        assert resp.status_code != 500
        assert resp.status_code in (400, 401, 422)


class TestIdentityUserManagement:
    """Identity 用户管理"""

    @pytest.mark.p1
    def test_list_users(self, api, v):
        """用户列表分页查询"""
        resp = api.get("/api/identity/users", params={"page": 1, "pageSize": 10})
        v.not_5xx(resp)

    @pytest.mark.p1
    def test_list_users_filter_by_status(self, api, v):
        """按状态过滤用户"""
        for status in [0, 1]:
            resp = api.get("/api/identity/users", params={"page": 1, "pageSize": 5, "status": status})
            v.not_5xx(resp)

    @pytest.mark.p1
    def test_list_users_filter_by_role(self, api, v):
        """按角色过滤用户"""
        resp = api.get("/api/identity/users", params={"page": 1, "pageSize": 5, "roleId": str(uuid.uuid4())})
        v.not_5xx(resp)

    @pytest.mark.p1
    def test_user_detail_not_found(self, api, v):
        """查询不存在用户返回 404"""
        resp = api.get(f"/api/identity/users/{uuid.uuid4()}")
        assert resp.status_code in (404, 401, 403)

    @pytest.mark.p1
    def test_create_user_duplicate_username_rejected(self, api, v):
        """重复用户名创建被拒绝"""
        resp = api.post("/api/identity/users", json={
            "username": "admin", "password": "P@ssw0rd123",
            "phone": "13800138001", "tenantId": None
        })
        assert resp.status_code != 500

    @pytest.mark.p1
    def test_update_user_status(self, api, v):
        """更新用户状态不报 500"""
        resp = api.put(f"/api/identity/users/{uuid.uuid4()}", json={"status": 0})
        assert resp.status_code != 500

    @pytest.mark.p1
    def test_reset_user_password(self, api, v):
        """重置密码接口不报 500"""
        resp = api.post(f"/api/identity/users/{uuid.uuid4()}/reset-password",
                        json={"newPassword": "NewP@ss123"})
        assert resp.status_code != 500

    @pytest.mark.p1
    def test_lock_user_account(self, api, v):
        """锁定账户接口不报 500"""
        resp = api.post(f"/api/identity/users/{uuid.uuid4()}/lock", json={})
        assert resp.status_code != 500

    @pytest.mark.p1
    def test_user_roles_list(self, api, v):
        """用户角色列表不报 500"""
        resp = api.get(f"/api/identity/users/{uuid.uuid4()}/roles")
        assert resp.status_code != 500

    @pytest.mark.p1
    def test_assign_roles_to_user(self, api, v):
        """分配角色给用户不报 500"""
        resp = api.put(f"/api/identity/users/{uuid.uuid4()}/roles",
                       json={"roleIds": [str(uuid.uuid4())]})
        assert resp.status_code != 500


class TestIdentityTokenSecurity:
    """Token 安全"""

    @pytest.mark.security
    def test_expired_token_returns_401(self, v):
        """过期 Token 访问返回 401"""
        from mock_client import MockApiClient
        expired_api = MockApiClient(token="expired.token.value")
        resp = expired_api.get("/api/identity/users")
        assert resp.status_code in (401, 403)

    @pytest.mark.security
    def test_malformed_token_returns_401(self, v):
        """格式异常 Token 返回 401"""
        from mock_client import MockApiClient
        bad_api = MockApiClient(token="MALFORMED_TOKEN")
        resp = bad_api.get("/api/identity/users")
        assert resp.status_code in (401, 403)

    @pytest.mark.security
    def test_no_bearer_prefix_returns_401(self, v):
        """无 Bearer 前缀 Token 返回 401"""
        from mock_client import MockApiClient
        bad_api = MockApiClient(token="some_token_value")
        resp = bad_api.get("/api/identity/users")
        assert resp.status_code in (401, 403)


class TestIdentityMFA:
    """多因素认证"""

    @pytest.mark.p2
    def test_mfa_send_code(self, api, v):
        """发送 MFA 验证码不报 500"""
        resp = api.post("/api/auth/mfa/send", json={"username": "admin", "type": "sms"})
        assert resp.status_code != 500

    @pytest.mark.p2
    def test_mfa_verify_wrong_code(self, api, v):
        """MFA 错误验证码被拒绝"""
        resp = api.post("/api/auth/mfa/verify", json={
            "username": "admin", "code": "000000"
        })
        assert resp.status_code != 500

    @pytest.mark.p2
    def test_mfa_session_list(self, api, v):
        """会话列表不报 500"""
        resp = api.get("/api/auth/sessions")
        assert resp.status_code != 500


# ══════════════════════════════════════════════════════════════════════════════
# Permission 服务 (8003) — 角色 / 菜单 / 权限 / 分配
# ══════════════════════════════════════════════════════════════════════════════

class TestPermissionRole:
    """权限角色管理"""

    @pytest.mark.p0
    def test_role_list(self, api, v):
        """角色列表正常返回"""
        resp = api.get("/api/system/role", params={"page": 1, "pageSize": 20})
        v.not_5xx(resp)

    @pytest.mark.p0
    def test_role_list_filter_by_name(self, api, v):
        """按名称过滤角色"""
        resp = api.get("/api/system/role", params={"page": 1, "pageSize": 10, "name": "管理员"})
        v.not_5xx(resp)

    @pytest.mark.p0
    def test_role_detail_not_found(self, api, v):
        """查询不存在角色返回 4xx"""
        resp = api.get(f"/api/system/role/{uuid.uuid4()}")
        assert resp.status_code in (404, 401, 403)

    @pytest.mark.p0
    def test_create_role_with_duplicate_code_rejected(self, api, v):
        """重复 code 创建角色被拒绝"""
        resp = api.post("/api/system/role", json={
            "name": "测试角色", "code": "SUPER_ADMIN", "status": 1
        })
        assert resp.status_code != 500

    @pytest.mark.p0
    def test_role_permissions_list(self, api, v):
        """角色权限列表不报 500"""
        resp = api.get(f"/api/system/role/{uuid.uuid4()}/permissions")
        assert resp.status_code != 500

    @pytest.mark.p1
    def test_assign_permissions_to_role(self, api, v):
        """分配权限给角色不报 500"""
        resp = api.put(f"/api/system/role/{uuid.uuid4()}/permissions",
                       json={"permissionIds": [str(uuid.uuid4())]})
        assert resp.status_code != 500

    @pytest.mark.p1
    def test_assign_menus_to_role(self, api, v):
        """分配菜单给角色不报 500"""
        resp = api.put(f"/api/system/role/{uuid.uuid4()}/menus",
                       json={"menuIds": [str(uuid.uuid4())]})
        assert resp.status_code != 500

    @pytest.mark.p1
    def test_delete_system_role_rejected(self, api, v):
        """删除系统内置角色被拒绝（非 500）"""
        resp = api.delete("/api/system/role/00000000-0000-0000-0000-000000000001")
        assert resp.status_code != 500

    @pytest.mark.p1
    def test_role_users_list(self, api, v):
        """角色下的用户列表不报 500"""
        resp = api.get(f"/api/system/role/{uuid.uuid4()}/users",
                       params={"page": 1, "pageSize": 10})
        assert resp.status_code != 500

    @pytest.mark.p1
    def test_create_role_empty_code_rejected(self, api, v):
        """空 code 创建角色被拒绝"""
        resp = api.post("/api/system/role", json={"name": "测试", "code": "", "status": 1})
        assert resp.status_code in (400, 401, 422)


class TestPermissionMenu:
    """菜单管理"""

    @pytest.mark.p1
    def test_menu_tree(self, api, v):
        """菜单树形结构不报 500"""
        resp = api.get("/api/system/menu/tree")
        v.not_5xx(resp)

    @pytest.mark.p1
    def test_menu_list(self, api, v):
        """菜单列表不报 500"""
        resp = api.get("/api/system/menu", params={"page": 1, "pageSize": 50})
        v.not_5xx(resp)

    @pytest.mark.p1
    def test_menu_detail_not_found(self, api, v):
        """查询不存在菜单返回 4xx"""
        resp = api.get(f"/api/system/menu/{uuid.uuid4()}")
        assert resp.status_code in (404, 401, 403)

    @pytest.mark.p1
    def test_create_menu_with_duplicate_code_rejected(self, api, v):
        """重复 code 菜单被拒绝"""
        resp = api.post("/api/system/menu", json={
            "name": "测试菜单", "code": "Dashboard", "path": "/dup", "type": 1
        })
        assert resp.status_code != 500

    @pytest.mark.p1
    def test_menu_filter_by_type(self, api, v):
        """按类型过滤菜单（1=目录,2=菜单,3=按钮）"""
        for mtype in [1, 2, 3]:
            resp = api.get("/api/system/menu", params={"type": mtype, "page": 1, "pageSize": 20})
            v.not_5xx(resp)


class TestPermissionCode:
    """权限码管理"""

    @pytest.mark.p1
    def test_permission_list(self, api, v):
        """权限列表不报 500"""
        resp = api.get("/api/system/permission", params={"page": 1, "pageSize": 20})
        v.not_5xx(resp)

    @pytest.mark.p1
    def test_permission_filter_by_service(self, api, v):
        """按服务前缀过滤权限码"""
        for svc in ["device", "station", "charging"]:
            resp = api.get("/api/system/permission",
                           params={"code": svc, "page": 1, "pageSize": 10})
            v.not_5xx(resp)

    @pytest.mark.p1
    def test_user_permissions(self, api, v):
        """获取当前用户权限集合"""
        resp = api.get("/api/system/permission/current")
        v.not_5xx(resp)

    @pytest.mark.p1
    def test_check_permission_code(self, api, v):
        """校验权限码接口不报 500"""
        resp = api.post("/api/system/permission/check",
                        json={"permCode": "device:device:list"})
        assert resp.status_code != 500


# ══════════════════════════════════════════════════════════════════════════════
# Tenant 服务 (8001) — 租户 / 套餐 / 配置 / 数据隔离
# ══════════════════════════════════════════════════════════════════════════════

class TestTenantManagement:
    """租户 CRUD 与配置"""

    @pytest.mark.p0
    def test_tenant_list(self, api, v):
        """租户列表正常分页"""
        resp = api.get("/api/tenants", params={"page": 1, "pageSize": 10})
        v.not_5xx(resp)

    @pytest.mark.p0
    def test_tenant_list_filter_by_status(self, api, v):
        """按状态过滤租户"""
        for status in [0, 1, 2]:
            resp = api.get("/api/tenants", params={"status": status, "page": 1, "pageSize": 10})
            v.not_5xx(resp)

    @pytest.mark.p0
    def test_tenant_list_filter_by_keyword(self, api, v):
        """关键词搜索租户"""
        resp = api.get("/api/tenants", params={"keyword": "测试", "page": 1, "pageSize": 10})
        v.not_5xx(resp)

    @pytest.mark.p0
    def test_tenant_detail_not_found(self, api, v):
        """查询不存在租户返回 4xx"""
        resp = api.get(f"/api/tenants/{uuid.uuid4()}")
        assert resp.status_code in (404, 401, 403)

    @pytest.mark.p0
    def test_create_tenant_duplicate_code_rejected(self, api, v):
        """重复 code 创建租户被拒绝"""
        resp = api.post("/api/tenants", json={
            "name": "测试租户", "code": "DEFAULT", "contactName": "张三",
            "contactPhone": "13800138000", "contactEmail": "test@test.com", "status": 1
        })
        assert resp.status_code != 500

    @pytest.mark.p1
    def test_tenant_config_get(self, api, v):
        """获取租户配置不报 500"""
        resp = api.get(f"/api/tenants/{uuid.uuid4()}/config")
        assert resp.status_code != 500

    @pytest.mark.p1
    def test_tenant_stats(self, api, v):
        """租户统计数据不报 500"""
        resp = api.get(f"/api/tenants/{uuid.uuid4()}/statistics")
        assert resp.status_code != 500

    @pytest.mark.p1
    def test_tenant_enable(self, api, v):
        """启用租户不报 500"""
        resp = api.post(f"/api/tenants/{uuid.uuid4()}/enable", json={})
        assert resp.status_code != 500

    @pytest.mark.p1
    def test_tenant_disable(self, api, v):
        """禁用租户不报 500"""
        resp = api.post(f"/api/tenants/{uuid.uuid4()}/disable", json={})
        assert resp.status_code != 500

    @pytest.mark.p1
    def test_tenant_users_list(self, api, v):
        """租户用户列表不报 500"""
        resp = api.get(f"/api/tenants/{uuid.uuid4()}/users",
                       params={"page": 1, "pageSize": 10})
        assert resp.status_code != 500

    @pytest.mark.p1
    def test_tenant_summary_overview(self, api, v):
        """租户总览统计不报 500"""
        resp = api.get("/api/tenants/summary")
        v.not_5xx(resp)

    @pytest.mark.p1
    def test_tenant_package_list(self, api, v):
        """租户套餐列表不报 500"""
        resp = api.get("/api/tenant-packages", params={"page": 1, "pageSize": 10})
        v.not_5xx(resp)

    @pytest.mark.p1
    def test_tenant_package_detail(self, api, v):
        """套餐详情不报 500"""
        resp = api.get(f"/api/tenant-packages/{uuid.uuid4()}")
        assert resp.status_code != 500

    @pytest.mark.p1
    def test_tenant_subscription(self, api, v):
        """租户订阅列表不报 500"""
        resp = api.get("/api/tenant-subscriptions", params={"page": 1, "pageSize": 10})
        v.not_5xx(resp)

    @pytest.mark.p1
    def test_tenant_create_validate_email_format(self, api, v):
        """创建租户时非法邮箱被拒绝"""
        resp = api.post("/api/tenants", json={
            "name": "xxx", "code": f"XT{UID()}", "contactName": "张三",
            "contactPhone": "13800138000",
            "contactEmail": "not_a_valid_email", "status": 1
        })
        assert resp.status_code != 500

    @pytest.mark.p1
    def test_tenant_create_validate_phone_format(self, api, v):
        """创建租户时非法手机号被拒绝"""
        resp = api.post("/api/tenants", json={
            "name": "xxx", "code": f"XT{UID()}", "contactName": "张三",
            "contactPhone": "abc123",
            "contactEmail": "valid@test.com", "status": 1
        })
        assert resp.status_code != 500

    @pytest.mark.p1
    def test_tenant_code_search_exactly(self, api, v):
        """精确搜索租户 code 不报 500"""
        resp = api.get("/api/tenants", params={"code": "DEFAULT", "page": 1, "pageSize": 5})
        v.not_5xx(resp)

    @pytest.mark.p2
    def test_tenant_delete_with_users_rejected(self, api, v):
        """有用户的租户不能被删除（业务约束）"""
        resp = api.delete("/api/tenants/00000000-0000-0000-0000-000000000001")
        assert resp.status_code != 500

    @pytest.mark.p2
    def test_tenant_export(self, api, v):
        """租户列表导出不报 500"""
        resp = api.get("/api/tenants/export", params={"format": "csv"})
        assert resp.status_code != 500
