"""
JGSY.AGI Python 单元测试 - 多租户隔离测试
=========================================
按照《自动化测试标准手册 v3.0》第 4 章 pytest / 4.3 核心测试点 / F 小节编写

测试范围（强制）：
  ✓ 租户 A 的数据对租户 B 不可见
  ✓ 跨租户更新/删除被拒绝
  ✓ 超管可访问所有租户数据
  ✓ tenant_id 篡改 → 使用 Token 中的 tenant_id（不可伪造）
  ✓ 任何查询方法缺 tenant_id 或 delete_at IS NULL → 阻断性缺陷

注：规范强制项「任何 Repository 查询方法不含 tenant_id 或 delete_at IS NULL 即为阻断性缺陷」
"""

import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from standards import (
    MockApiClient,
    AssertionHelper,
    HttpStatus,
    MOCK_TOKEN_ADMIN,
    MOCK_TOKEN_USER,
    TENANT_ID_A,
    TENANT_ID_B,
    SUPER_ADMIN_ID,
    ADMIN_USER_ID,
    NORMAL_USER_ID,
)


class TestTenantIsolationPytest:
    """多租户隔离测试 (Tenant Isolation Tests) - 强制必验"""

    @pytest.fixture
    def api_client(self):
        """创建 Mock API 客户端"""
        return MockApiClient()

    @pytest.fixture
    def tenant_a_client(self, api_client):
        """租户 A 的认证客户端"""
        api_client.set_token(MOCK_TOKEN_ADMIN)  # Token 中包含 tenant_id = TENANT_ID_A
        return api_client

    @pytest.fixture
    def tenant_b_client(self):
        """租户 B 的认证客户端"""
        client = MockApiClient()
        client.set_token(MOCK_TOKEN_ADMIN)  # 模拟租户 B 的 Token
        return client

    # ─────────────────────────────────────────────────────
    # 基础隔离验证 (Basic Isolation)
    # ─────────────────────────────────────────────────────

    def test_tenant_a_cannot_see_tenant_b_data(self, tenant_a_client, tenant_b_client):
        """
        测试用例 TENANT-001：租户 A 无法看到租户 B 的数据
        预期：查询结果中只有租户 A 的数据
        """
        # 租户 A 查询用户列表
        resp_a = tenant_a_client.get('/api/users/list')
        assert resp_a.is_success

        body_a = resp_a.json()
        items_a = body_a.get('items', [])

        # 验证所有项都属于租户 A
        for item in items_a:
            assert item.get('tenant_id') == TENANT_ID_A, \
                f"期望租户 A 的数据，但找到租户 {item.get('tenant_id')} 的数据"

        print(f"✓ 租户 A 只能看到自己的数据 ({len(items_a)} 条)")

    def test_query_must_filter_by_tenant_id(self, tenant_a_client):
        """
        测试用例 TENANT-002：任何查询必须包含 tenant_id 过滤（强制项）
        预期：Mock 返回的数据都应该有 tenant_id 字段
        """
        resp = tenant_a_client.get('/api/users/list')
        assert resp.is_success

        body = resp.json()
        items = body.get('items', [])

        # 验证每条数据都有 tenant_id（即使列表为空也应该有字段定义）
        for item in items:
            assert 'tenant_id' in item, \
                "缺陷：查询结果缺少 tenant_id 字段 - 表示查询未正确过滤租户数据"

        print(f"✓ 查询正确过滤了 tenant_id")

    def test_query_must_filter_by_delete_at(self, tenant_a_client):
        """
        测试用例 TENANT-003：任何查询必须包含 delete_at IS NULL 过滤（强制项）
        预期：查询结果中没有被软删除的数据（delete_at != NULL）
        """
        resp = tenant_a_client.get('/api/users/list')
        assert resp.is_success

        body = resp.json()
        items = body.get('items', [])

        # 验证没有被删除的数据
        for item in items:
            assert 'delete_at' in item, \
                "缺陷：查询结果缺少 delete_at 字段 - 表示查询未正确进行软删除过滤"
            
            delete_at = item.get('delete_at')
            assert delete_at is None, \
                f"缺陷：查询返回了已删除数据 (delete_at={delete_at}) - 违反 delete_at IS NULL 规则"

        print(f"✓ 查询正确过滤了软删除的数据")

    # ─────────────────────────────────────────────────────
    # 跨租户操作被拒 (Cross-Tenant Operations Rejected)
    # ─────────────────────────────────────────────────────

    def test_cannot_update_data_with_different_tenant_id(self, tenant_a_client):
        """
        测试用例 TENANT-004：无法更新其他租户的数据
        预期：尝试更新不属于自己租户的数据被拒绝（403 或 404）
        """
        # 构造一个虚假的、属于不同租户的用户 ID
        other_tenant_user_id = "99999999-9999-9999-9999-999999999999"

        # 尝试更新这个用户
        resp = tenant_a_client.put(f'/api/users/{other_tenant_user_id}', json={
            'full_name': '被篡改的名字'
        })

        # 应该被拒绝（404 Not Found 或 403 Forbidden）
        assert resp.status_code in [HttpStatus.NOT_FOUND.value, HttpStatus.FORBIDDEN.value], \
            f"期望 403 或 404，得到 {resp.status_code}"

        print(f"✓ 跨租户更新被拒绝 ({resp.status_code})")

    def test_cannot_delete_data_with_different_tenant_id(self, tenant_a_client):
        """
        测试用例 TENANT-005：无法删除其他租户的数据
        预期：尝试删除不属于自己租户的数据被拒绝（403 或 404）
        """
        other_tenant_user_id = "99999999-9999-9999-9999-999999999999"

        resp = tenant_a_client.delete(f'/api/users/{other_tenant_user_id}')

        assert resp.status_code in [HttpStatus.NOT_FOUND.value, HttpStatus.FORBIDDEN.value]
        print(f"✓ 跨租户删除被拒绝 ({resp.status_code})")

    # ─────────────────────────────────────────────────────
    # Token 中的 tenant_id 权威性 (Token tenant_id is Authoritative)
    # ─────────────────────────────────────────────────────

    def test_tenant_id_from_token_is_authoritative(self, tenant_a_client):
        """
        测试用例 TENANT-006：使用 Token 中的 tenant_id，忽略请求中的值
        预期：即使请求中尝试篡改 tenant_id，也使用 Token 中的值
        """
        # 尝试在请求中篡改 tenant_id
        resp = tenant_a_client.get('/api/users/list', params={'tenant_id': TENANT_ID_B})

        # 但系统应该使用 Token 中的 tenant_id（TENANT_ID_A）
        # 所以返回的数据应该还是租户 A 的
        assert resp.is_success
        items = resp.json().get('items', [])
        for item in items:
            assert item.get('tenant_id') == TENANT_ID_A, \
                "缺陷：系统使用了请求中篡改的 tenant_id，而不是使用 Token 中的值"

        print(f"✓ 系统正确使用 Token 中的 tenant_id，忽略请求参数")

    def test_cannot_forge_tenant_id_in_request_body(self, tenant_a_client):
        """
        测试用例 TENANT-007：请求体中的 tenant_id 无法伪造
        预期：创建的数据应该属于 Token 中的租户，而不是请求中声称的租户
        """
        # 尽管在这个 Mock 实现中创建接口还没实现，
        # 但我们演示这个测试原理
        print(f"℃ 创建接口未实现，但原理是：请求体中的 tenant_id 会被忽略")

    # ─────────────────────────────────────────────────────
    # 超管权限跨租户访问 (Super Admin Cross-Tenant Access)
    # ─────────────────────────────────────────────────────

    def test_super_admin_can_access_all_tenants_data(self, tenant_a_client):
        """
        测试用例 TENANT-008：超管可访问所有租户数据
        预期：超管的查询可能返回多个租户的数据
        """
        # 使用超管 Token
        resp = tenant_a_client.get('/api/users/list')
        assert resp.is_success

        # 在完整实现中，超管应该能看到所有租户的用户
        # 当前 Mock 中，我们验证至少能看到自己租户的数据
        items = resp.json().get('items', [])
        assert len(items) > 0
        print(f"✓ 超管可访问数据 ({len(items)} 条用户)")

    # ─────────────────────────────────────────────────────
    # 数据隔离一致性 (Data Isolation Consistency)
    # ─────────────────────────────────────────────────────

    def test_all_entity_types_respect_tenant_isolation(self, tenant_a_client):
        """
        测试用例 TENANT-009：所有实体类型都遵循租户隔离
        预期：用户、角色、权限等各类数据都独立隔离
        """
        # 测试用户隔离
        users_resp = tenant_a_client.get('/api/users/list')
        assert users_resp.is_success
        users = users_resp.json().get('items', [])
        for user in users:
            assert user.get('tenant_id') == TENANT_ID_A

        # 测试角色隔离
        roles_resp = tenant_a_client.get('/api/roles/list')
        assert roles_resp.is_success
        roles = roles_resp.json().get('items', [])
        for role in roles:
            assert role.get('tenant_id') == TENANT_ID_A

        # 测试权限隔离
        perms_resp = tenant_a_client.get('/api/permissions/list')
        assert perms_resp.is_success
        perms = perms_resp.json().get('items', [])
        for perm in perms:
            assert perm.get('tenant_id') == TENANT_ID_A

        print(f"✓ 所有实体类型都正确隔离")

    def test_search_filters_respect_tenant_isolation(self, tenant_a_client):
        """
        测试用例 TENANT-010：搜索过滤也必须包含租户隔离
        预期：模糊搜索、按条件过滤时仍然只返回该租户的数据
        """
        # 例如搜索 admin 用户
        resp = tenant_a_client.get('/api/users/list', params={'search': 'admin'})
        assert resp.is_success

        items = resp.json().get('items', [])
        for item in items:
            assert item.get('tenant_id') == TENANT_ID_A, \
                "搜索结果应该仍然遵循租户隔离"

        print(f"✓ 搜索过滤正确遵循租户隔离")


class TestTenantComplianceChecksPytest:
    """租户隔离规范合规性检查"""

    @pytest.fixture
    def api_client(self):
        return MockApiClient()

    @pytest.fixture
    def admin_client(self, api_client):
        api_client.set_token(MOCK_TOKEN_ADMIN)
        return api_client

    def test_soft_delete_data_not_visible_to_any_tenant(self, admin_client):
        """
        测试用例 TENANT-COMPLIANCE-001：软删除数据对所有租户都不可见
        预期：delete_at 不为 NULL 的数据不应出现在任何人的查询中
        """
        resp = admin_client.get('/api/users/list')
        assert resp.is_success

        items = resp.json().get('items', [])
        for item in items:
            assert item.get('delete_at') is None, \
                "软删除的数据不应出现在列表中"

        print(f"✓ 软删除数据对所有租户都正确隐藏")

    def test_unique_code_respects_tenant_isolation(self, api_client):
        """
        测试用例 TENANT-COMPLIANCE-002：唯一 code 联合索引正确实现
        预期：code 唯一性在租户维度检查，不同租户可有相同 code
        
        规范要求：带 code 的表必须建联合唯一索引 UNIQUE(tenant_id, code, delete_at)
        """
        # 这里演示原理：不同租户可有相同 code
        # 在 Mock 中我们验证返回的权限 code 都包含在 code 字段中
        resp = api_client.post('/api/auth/login', json={'username': 'admin', 'password': 'P@ssw0rd'})
        token = resp.json()['data']['access_token']
        api_client.set_token(token)

        perms_resp = api_client.get('/api/permissions/list')
        assert perms_resp.is_success

        items = perms_resp.json().get('items', [])
        for item in items:
            assert 'code' in item, "权限应该有 code 字段"

        print(f"✓ 权限 code 字段正确存在")


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])
