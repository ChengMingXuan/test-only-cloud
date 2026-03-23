"""
JGSY.AGI Python pytest 最佳实践与快速参考
==========================================
"""

# 1. 导入标准模板
# ══════════════════════════════════════════════════════════════════════

import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from standards import (
    MockApiClient,
    AssertionHelper,
    HttpStatus,
    ErrorCode,
    ApiResult,
    PagedResult,
    BaseEntity,
    User,
    Role,
    Permission,
    MOCK_TOKEN_ADMIN,
    MOCK_TOKEN_USER,
    TENANT_ID_A,
    TENANT_ID_B,
)


# 2. Fixture 标准模式
# ══════════════════════════════════════════════════════════════════════

class TestExample:
    """示例测试类"""

    @pytest.fixture
    def api_client(self):
        """创建 Mock API 客户端"""
        return MockApiClient()

    @pytest.fixture
    def admin_client(self, api_client):
        """创建管理员认证客户端"""
        api_client.set_token(MOCK_TOKEN_ADMIN)
        return api_client

    @pytest.fixture
    def user_client(self, api_client):
        """创建普通用户认证客户端"""
        api_client.set_token(MOCK_TOKEN_USER)
        return api_client

    # ─────────────────────────────────────────────────────────────────────
    # 3. 常见测试模式
    # ─────────────────────────────────────────────────────────────────────

    def test_successful_operation(self, admin_client):
        """✅ 成功场景"""
        resp = admin_client.get('/api/users/list')
        
        # 方法 1：快速断言
        AssertionHelper.assert_api_success(resp)
        
        # 方法 2：精确断言
        assert resp.status_code == HttpStatus.OK.value
        assert resp.is_success
        
        # 方法 3：数据验证
        body = resp.json()
        AssertionHelper.assert_paged_result(resp)
        assert body['total'] >= 0
        assert isinstance(body['items'], list)

    def test_authentication_error(self, api_client):
        """❌ 认证失败"""
        # 不设置 Token，直接访问
        resp = api_client.get('/api/users/list')
        
        # 验证返回 401
        assert resp.status_code == HttpStatus.UNAUTHORIZED.value
        assert not resp.is_success
        assert '未登录' in resp.json().get('message', '')

    def test_authorization_error(self, user_client):
        """❌ 权限不足（需要完整实现）"""
        # 当后端实现权限检查时
        pass

    def test_validation_error(self, api_client):
        """❌ 输入验证失败"""
        resp = api_client.post('/api/auth/login', json={
            'username': 'admin'
            # 缺少 password 字段
        })
        
        assert resp.status_code in [HttpStatus.BAD_REQUEST.value, HttpStatus.UNAUTHORIZED.value]
        assert not resp.is_success

    def test_not_found_error(self, admin_client):
        """❌ 资源不存在"""
        nonexistent_id = "99999999-9999-9999-9999-999999999999"
        resp = admin_client.delete(f'/api/users/{nonexistent_id}')
        
        assert resp.status_code == HttpStatus.NOT_FOUND.value
        assert not resp.is_success

    def test_conflict_error(self, admin_client):
        """❌ 冲突（如重复创建）"""
        # 当后端实现唯一性检查时
        resp = admin_client.post('/api/roles', json={
            'code': 'admin',
            'name': '管理员'
        })
        
        # 假设已存在，应返回 409
        # assert resp.status_code == HttpStatus.CONFLICT.value

    # ─────────────────────────────────────────────────────────────────────
    # 4. 多租户隔离测试模式
    # ─────────────────────────────────────────────────────────────────────

    def test_tenant_isolation_basic(self):
        """🔒 基础租户隔离"""
        # 使用 TENANT_A 的客户端
        client_a = MockApiClient()
        client_a.set_token(MOCK_TOKEN_ADMIN)  # 该 Token 属于 TENANT_A
        
        resp = client_a.get('/api/users/list')
        items = resp.json()['items']
        
        # 验证所有项都属于租户 A
        for item in items:
            assert item['tenant_id'] == TENANT_ID_A

    def test_tenant_isolation_query_must_have_filters(self, admin_client):
        """🔒 查询必须包含租户过滤"""
        resp = admin_client.get('/api/users/list')
        body = resp.json()
        items = body['items']
        
        # 强制检查 1：所有项都有 tenant_id
        for item in items:
            assert 'tenant_id' in item, "缺陷：tenant_id 字段缺失"
            
        # 强制检查 2：所有项都有 delete_at
        for item in items:
            assert 'delete_at' in item, "缺陷：delete_at 字段缺失"
            assert item['delete_at'] is None, "缺陷：查询返回了已删除数据"

    # ─────────────────────────────────────────────────────────────────────
    # 5. 软删除测试模式
    # ─────────────────────────────────────────────────────────────────────

    def test_soft_delete_basics(self, admin_client):
        """🗑️  基础软删除"""
        # 获取初始列表
        list_resp = admin_client.get('/api/users/list')
        total_before = list_resp.json()['total']
        
        # 验证：所有项都有 delete_at = None
        for item in list_resp.json()['items']:
            assert item['delete_at'] is None, "应该没有已删除的数据"
        
        # 模拟删除（在完整实现中）
        # delete_resp = admin_client.delete('/api/users/{id}')
        # assert delete_resp.status_code in [200, 204]
        
        # 再次查询，数量应该减少 1
        # list_resp_after = admin_client.get('/api/users/list')
        # assert list_resp_after.json()['total'] == total_before - 1

    def test_soft_delete_metadata_updates(self):
        """🗑️  软删除元数据"""
        # 规范强制：
        # UPDATE SET delete_at = NOW(),
        #           update_by = @UserId,
        #           update_name = @UserName,
        #           update_time = NOW()
        # WHERE id = ?
        pass

    def test_soft_delete_never_in_queries(self, admin_client):
        """🗑️  已删除数据永不返回"""
        # 任何查询都应该自动过滤 delete_at IS NULL
        
        # 测试列表
        list_resp = admin_client.get('/api/users/list')
        for item in list_resp.json()['items']:
            assert item['delete_at'] is None
        
        # 测试搜索
        search_resp = admin_client.get('/api/users/list?search=test')
        for item in search_resp.json()['items']:
            assert item['delete_at'] is None

    # ─────────────────────────────────────────────────────────────────────
    # 6. 安全测试模式
    # ─────────────────────────────────────────────────────────────────────

    def test_sql_injection_prevention(self, api_client):
        """🛡️  SQL 注入防护"""
        injection_payloads = [
            "admin' OR '1'='1",
            "admin'; DROP TABLE users; --",
            "' UNION SELECT * FROM passwords --",
        ]
        
        for payload in injection_payloads:
            resp = api_client.post('/api/auth/login', json={
                'username': payload,
                'password': 'anything'
            })
            
            # 应该当做普通字符串，登录失败
            assert resp.status_code == HttpStatus.UNAUTHORIZED.value, \
                f"SQL 注入 '{payload}' 未被防护"

    def test_xss_prevention(self, api_client):
        """🛡️  XSS 防护"""
        xss_payloads = [
            "<script>alert('xss')</script>",
            "<img src=x onerror='alert(1)'>",
            "javascript:alert('xss')",
        ]
        
        for payload in xss_payloads:
            resp = api_client.post('/api/auth/login', json={
                'username': payload,
                'password': 'anything'
            })
            
            # 不应该执行脚本
            assert resp.status_code in [400, 401]

    # ─────────────────────────────────────────────────────────────────────
    # 7. 参数化测试模式
    # ─────────────────────────────────────────────────────────────────────

    @pytest.mark.parametrize('username,password,expected_code', [
        ('admin', 'P@ssw0rd', 200),      # ✅ 成功
        ('admin', 'wrong', 401),          # ❌ 错误密码
        ('', '', 401),                    # ❌ 空字段
        ('nonexistent', 'xxx', 401),      # ❌ 用户不存在
    ])
    def test_login_parameterized(self, api_client, username, password, expected_code):
        """参数化：标准化多个场景"""
        resp = api_client.post('/api/auth/login', json={
            'username': username,
            'password': password
        })
        assert resp.status_code == expected_code

    # ─────────────────────────────────────────────────────────────────────
    # 8. 打印调试模式
    # ─────────────────────────────────────────────────────────────────────

    def test_with_debug_output(self, admin_client):
        """调试：打印响应内容"""
        resp = admin_client.get('/api/users/list')
        
        # 打印原始响应
        print("\n=== Response ===")
        print(f"Status Code: {resp.status_code}")
        print(f"Body: {resp.json()}")
        print(f"Headers: {resp.headers}")
        
        # 打印统计
        body = resp.json()
        print(f"\n=== Statistics ===")
        print(f"Total: {body['total']}")
        print(f"Items: {len(body['items'])}")
        
        assert resp.is_success


# ═══════════════════════════════════════════════════════════════════════════
# 运行速查表
# ═══════════════════════════════════════════════════════════════════════════

"""
# 运行全量
pytest test-automation/tests/ -v

# 运行单个文件
pytest test-automation/tests/test_auth_and_permissions.py -v

# 运行单个类
pytest test-automation/tests/test_auth_and_permissions.py::TestAuthenticationPytest -v

# 运行单个测试
pytest test-automation/tests/test_auth_and_permissions.py::TestAuthenticationPytest::test_successful_login_with_correct_credentials -v

# 运行按标记（当添加了 markers 后）
pytest test-automation/tests/ -m "auth" -v
pytest test-automation/tests/ -m "tenant_isolation" -v

# 运行并显示 print 输出
pytest test-automation/tests/ -v -s

# 运行不显示警告
pytest test-automation/tests/ -v --tb=short

# 运行并生成报告
pytest test-automation/tests/ -v --html=report.html
pytest test-automation/tests/ --junit-xml=report.xml

# 并行运行（如果用了 pytest-xdist）
pytest test-automation/tests/ -n auto

# 失败后停止
pytest test-automation/tests/ -x

# 失败后继续但记录
pytest test-automation/tests/ --tb=short --failed-first
"""


if __name__ == '__main__':
    import pytest
    pytest.main([__file__, '-v', '--tb=short'])
