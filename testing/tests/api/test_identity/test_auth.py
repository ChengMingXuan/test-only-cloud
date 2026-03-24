"""
Identity 服务 — 认证接口自动化测试
===================================
覆盖：登录/注册/Token刷新/密码重置/MFA/OAuth
优先级：P0（核心认证）
"""
import pytest
import logging

from tests.api.base_test import BaseApiTest

logger = logging.getLogger(__name__)


@pytest.mark.p0
class TestAuthLogin(BaseApiTest):
    """登录接口测试"""

    SERVICE_NAME = "identity"
    API_PREFIX = "/api/auth"

    def test_login_success(self, api):
        """正常登录 → 返回 Token"""
        resp = api.post(f"{self.API_PREFIX}/login", json={
            "username": "admin",
            "password": "P@ssw0rd",
        })
        data = self.assert_success(resp)
        assert "accessToken" in data or "token" in data, "响应缺少 Token"
        token = data.get("accessToken") or data.get("token")
        assert len(token) > 50, "Token 长度不足"

    def test_login_wrong_password(self, api):
        """错误密码 → 401"""
        resp = api.post(f"{self.API_PREFIX}/login", json={
            "username": "admin",
            "password": "WrongPassword",
        })
        assert resp.status_code in (400, 401), f"应返回 400/401，实际: {resp.status_code}"

    def test_login_empty_username(self, api):
        """空用户名 → 400"""
        resp = api.post(f"{self.API_PREFIX}/login", json={
            "username": "",
            "password": "P@ssw0rd",
        })
        assert resp.status_code in (400, 401, 422), f"应返回 400/401，实际: {resp.status_code}"

    def test_login_empty_password(self, api):
        """空密码 → 400"""
        resp = api.post(f"{self.API_PREFIX}/login", json={
            "username": "admin",
            "password": "",
        })
        assert resp.status_code in (400, 401, 422), f"应返回 400/401，实际: {resp.status_code}"

    def test_login_nonexistent_user(self, api):
        """不存在的用户 → 401"""
        resp = api.post(f"{self.API_PREFIX}/login", json={
            "username": "nonexistent_user_xyz_999",
            "password": "Test@123456",
        })
        assert resp.status_code in (400, 401, 404)

    def test_login_sql_injection(self, api):
        """SQL 注入尝试 → 应拒绝"""
        resp = api.post(f"{self.API_PREFIX}/login", json={
            "username": "' OR 1=1 --",
            "password": "' OR 1=1 --",
        })
        assert resp.status_code in (400, 401, 422)

    def test_login_xss_attempt(self, api):
        """XSS 尝试 → 应拒绝"""
        resp = api.post(f"{self.API_PREFIX}/login", json={
            "username": "<script>alert('xss')</script>",
            "password": "Test@123456",
        })
        assert resp.status_code in (400, 401, 422)


@pytest.mark.p0
class TestAuthToken(BaseApiTest):
    """Token 管理接口测试"""

    SERVICE_NAME = "identity"
    API_PREFIX = "/api/auth"

    def test_get_current_user(self, api):
        """获取当前用户信息"""
        resp = api.get(f"{self.API_PREFIX}/me")
        assert resp.status_code == 200, f"获取当前用户失败: {resp.status_code}"
        data = resp.json().get("data", {})
        assert "id" in data or "userId" in data, "缺少用户ID"

    def test_token_refresh(self, api):
        """刷新 Token"""
        # 先登录获取 refreshToken
        login_resp = api.post(f"{self.API_PREFIX}/login", json={
            "username": "admin",
            "password": "P@ssw0rd",
        })
        login_data = self.assert_success(login_resp)
        refresh_token = login_data.get("refreshToken")
        if refresh_token:
            resp = api.post(f"{self.API_PREFIX}/refresh", json={
                "refreshToken": refresh_token,
            })
            data = self.assert_success(resp)
            assert "accessToken" in data or "token" in data

    def test_access_without_token(self):
        """无 Token 访问 → 401"""
        from tests.conftest import ApiClient, GATEWAY_URL
        no_auth_api = ApiClient(GATEWAY_URL)
        resp = no_auth_api.get("/api/auth/me")
        assert resp.status_code == 401, f"应返回 401，实际: {resp.status_code}"

    def test_access_with_invalid_token(self):
        """伪造 Token → 401"""
        from tests.conftest import ApiClient, GATEWAY_URL
        fake_api = ApiClient(GATEWAY_URL, "fake.invalid.token")
        resp = fake_api.get("/api/auth/me")
        assert resp.status_code == 401


@pytest.mark.p0
class TestUserCRUD(BaseApiTest):
    """用户账户 CRUD 测试（含数据库校验）— 路由 /api/users → Account 服务"""

    SERVICE_NAME = "account"
    API_PREFIX = "/api/users"

    @pytest.fixture
    def created_user_id(self, api, unique_suffix, account_db):
        """创建测试用户账户并在测试后清理"""
        display_name = f"测试用户_{unique_suffix}"
        phone = f"139{unique_suffix[:8].ljust(8, '0')}"
        resp = api.post(self.API_PREFIX, json={
            "displayName": display_name,
            "phoneNumber": phone,
            "email": f"test_{unique_suffix}@test.jgsy.com",
        })
        if resp.status_code in (200, 201):
            data = resp.json().get("data", {}) or resp.json()
            user_id = data.get("id")
            yield user_id
            # 清理：软删除
            if user_id:
                api.delete(f"{self.API_PREFIX}/{user_id}")
        else:
            logger.warning(f"用户账户创建返回 {resp.status_code}（后端已知问题）")
            yield None

    def test_create_user_and_verify_db(self, api, account_db, unique_suffix):
        """新增用户账户 → 验证数据库记录"""
        display_name = f"测试用户_{unique_suffix}"
        phone = f"138{unique_suffix[:8].ljust(8, '0')}"

        # ① 执行前：确认不存在
        before = account_db.query_scalar(
            "SELECT count(*) FROM account.account_info WHERE display_name = %s AND delete_at IS NULL",
            (display_name,)
        )
        assert before == 0, f"测试前用户已存在: {display_name}"

        # ② 创建用户账户
        resp = api.post(self.API_PREFIX, json={
            "displayName": display_name,
            "phoneNumber": phone,
            "email": f"test_{unique_suffix}@test.jgsy.com",
        })
        # Account Create 返回 201 Created
        assert resp.status_code in (200, 201), f"创建失败: {resp.status_code} {resp.text[:300]}"
        data = resp.json()
        user_id = data.get("id") or (data.get("data", {}) or {}).get("id")
        assert user_id, f"未返回用户ID: {data}"

        # ③ 验证数据库
        db_record = account_db.query_one(
            "SELECT * FROM account.account_info WHERE id = %s::uuid AND delete_at IS NULL",
            (user_id,)
        )
        assert db_record is not None, "数据库中未找到用户账户"
        assert db_record["display_name"] == display_name

        # ④ 清理
        api.delete(f"{self.API_PREFIX}/{user_id}")

    def test_get_user_list(self, api):
        """查询用户列表"""
        resp = api.get(self.API_PREFIX, params={"page": 1, "pageSize": 10})
        data = self.assert_paged(resp)
        assert len(data["items"]) <= 10

    def test_get_user_detail(self, api, created_user_id):
        """查询用户账户详情"""
        assert created_user_id, "用户账户创建失败"
        resp = api.get(f"{self.API_PREFIX}/{created_user_id}")
        assert resp.status_code == 200, f"获取详情失败: {resp.status_code}"

    def test_update_user_and_verify_db(self, api, account_db, created_user_id):
        """修改用户账户 → 验证数据库字段变更"""
        assert created_user_id, "用户账户创建失败"

        new_name = "更新后的显示名"
        resp = api.put(f"{self.API_PREFIX}/{created_user_id}", json={
            "displayName": new_name,
        })
        # Account Update 返回 204 NoContent
        assert resp.status_code in (200, 204), f"更新失败: {resp.status_code} {resp.text[:300]}"

        # 验证数据库
        db_record = account_db.query_one(
            "SELECT display_name, update_time FROM account.account_info WHERE id = %s::uuid",
            (created_user_id,)
        )
        assert db_record is not None, "记录不存在"
        assert db_record["display_name"] == new_name, "字段未更新"
        assert db_record["update_time"] is not None, "update_time 未更新"

    def test_delete_user_soft_delete(self, api, account_db, unique_suffix):
        """删除用户账户 → 验证软删除"""
        # 创建
        phone = f"137{unique_suffix[:8].ljust(8, '0')}"
        create_resp = api.post(self.API_PREFIX, json={
            "displayName": "待删除用户",
            "phoneNumber": phone,
        })
        assert create_resp.status_code in (200, 201), f"创建失败: {create_resp.status_code} {create_resp.text[:300]}"
        data = create_resp.json()
        user_id = data.get("id") or (data.get("data", {}) or {}).get("id")
        assert user_id, f"未返回ID: {data}"

        # 删除
        del_resp = api.delete(f"{self.API_PREFIX}/{user_id}")
        assert del_resp.status_code in (200, 204)

        # 验证软删除
        self.assert_db_record_deleted(account_db, "account.account_info", user_id)


@pytest.mark.p0
@pytest.mark.query
class TestUserQuery(BaseApiTest):
    """用户账户查询条件组合测试 — 路由 /api/users → Account 服务"""

    SERVICE_NAME = "account"
    API_PREFIX = "/api/users"

    def test_query_no_params(self, api):
        """无参数 → 返回全部（分页）"""
        resp = api.get(self.API_PREFIX)
        data = self.assert_paged(resp)
        assert data["total"] >= 0

    def test_query_by_username(self, api):
        """按用户名查询"""
        resp = api.get(self.API_PREFIX, params={"keyword": "admin"})
        data = self.assert_paged(resp)
        # 验证响应结构正确（Mock 会回填 keyword 到 username）
        assert isinstance(data["items"], list)

    def test_query_by_status(self, api):
        """按状态查询"""
        resp = api.get(self.API_PREFIX, params={"status": "active"})
        data = self.assert_paged(resp)
        for item in data["items"]:
            assert item.get("status") in ("active", "Active", 1, True)

    def test_query_pagination(self, api):
        """分页查询 — 页码/页大小"""
        # 第 1 页
        resp1 = api.get(self.API_PREFIX, params={"page": 1, "pageSize": 5})
        data1 = self.assert_paged(resp1)
        # 第 2 页
        resp2 = api.get(self.API_PREFIX, params={"page": 2, "pageSize": 5})
        data2 = self.assert_paged(resp2)

        if data1["total"] > 5:
            # 两页数据不应重叠
            ids_1 = {item["id"] for item in data1["items"]}
            ids_2 = {item["id"] for item in data2["items"]}
            assert ids_1.isdisjoint(ids_2), "分页数据重叠"

    def test_query_sort_desc(self, api):
        """倒序排序"""
        resp = api.get(self.API_PREFIX, params={
            "sortBy": "createTime",
            "sortOrder": "desc",
            "pageSize": 10,
        })
        data = self.assert_paged(resp)
        items = data["items"]
        if len(items) >= 2:
            # 验证时间倒序
            for i in range(len(items) - 1):
                t1 = items[i].get("createTime", "")
                t2 = items[i + 1].get("createTime", "")
                if t1 and t2:
                    assert t1 >= t2, f"排序错误: {t1} < {t2}"

    def test_query_sort_asc(self, api):
        """正序排序"""
        resp = api.get(self.API_PREFIX, params={
            "sortBy": "createTime",
            "sortOrder": "asc",
            "pageSize": 10,
        })
        data = self.assert_paged(resp)
        items = data["items"]
        if len(items) >= 2:
            for i in range(len(items) - 1):
                t1 = items[i].get("createTime", "")
                t2 = items[i + 1].get("createTime", "")
                if t1 and t2:
                    assert t1 <= t2, f"排序错误: {t1} > {t2}"
