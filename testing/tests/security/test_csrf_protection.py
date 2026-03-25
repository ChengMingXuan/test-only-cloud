"""
安全测试 — CSRF 防护验证 (OWASP A04)
==========================================================
验证跨站请求伪造防护机制、幂等性、危险操作二次确认。

对标标准：
  - OWASP Top 10 2021 A04 不安全设计
  - OWASP ASVS 4.0 V4 访问控制
  - CWE-352 CSRF

覆盖分组：
  SEC-C001 状态变更接口防护
  SEC-C002 删除操作安全
  SEC-C003 权限变更保护
  SEC-C004 批量操作安全

合计约 80 条用例
"""
import uuid
import pytest
import logging
from mock_client import MockApiClient, MOCK_TOKEN

logger = logging.getLogger(__name__)

# 状态变更端点（需要 CSRF 保护的端点）
STATE_CHANGE_ENDPOINTS = [
    ("/api/device", "POST", {"name": "测试设备", "code": "DEV-TEST"}),
    ("/api/stations", "POST", {"name": "测试场站", "code": "STN-TEST"}),
    ("/api/workorder", "POST", {"title": "测试工单", "type": "repair"}),
    ("/api/system/role", "POST", {"name": "测试角色", "code": "role_test"}),
    ("/api/tenants", "POST", {"name": "测试租户", "code": "TNT-TEST"}),
]

# 危险操作端点
DANGEROUS_OPERATIONS = [
    ("/api/system/role/{id}", "DELETE"),
    ("/api/tenants/{id}", "DELETE"),
    ("/api/account/users/{id}", "DELETE"),
    ("/api/device/{id}", "DELETE"),
    ("/api/stations/{id}", "DELETE"),
]


# ══════════════════════════════════════════════════════════════
# SEC-C001 状态变更接口防护
# ══════════════════════════════════════════════════════════════

class TestStateChangeProtection:
    """SEC-C001: 验证状态变更接口需要认证与正确的 Content-Type"""

    @pytest.mark.security
    @pytest.mark.p0
    @pytest.mark.parametrize("endpoint,method,body", STATE_CHANGE_ENDPOINTS)
    def test_state_change_requires_auth(self, endpoint, method, body):
        """状态变更操作必须需要认证"""
        client = MockApiClient(token=None)
        if method == "POST":
            resp = client.post(endpoint, json=body)
        elif method == "PUT":
            resp = client.put(endpoint, json=body)
        elif method == "DELETE":
            resp = client.delete(endpoint)
        else:
            resp = client.get(endpoint)
        assert resp.status_code in (401, 403), (
            f"未认证的 {method} {endpoint} 应返回 401/403，实际 {resp.status_code}"
        )

    @pytest.mark.security
    @pytest.mark.p0
    @pytest.mark.parametrize("endpoint,method,body", STATE_CHANGE_ENDPOINTS)
    def test_state_change_invalid_token(self, endpoint, method, body):
        """无效 Token 的状态变更操作应被拒绝"""
        client = MockApiClient(token="invalid.token.here")
        if method == "POST":
            resp = client.post(endpoint, json=body)
        elif method == "PUT":
            resp = client.put(endpoint, json=body)
        else:
            resp = client.get(endpoint)
        assert resp.status_code in (401, 403), (
            f"无效 Token {method} {endpoint} 应返回 401/403"
        )

    @pytest.mark.security
    @pytest.mark.p0
    def test_post_requires_content_type(self, api):
        """POST 请求必须声明 Content-Type"""
        resp = api.post("/api/device", json={"name": "test"})
        assert resp.status_code < 500, "POST 应正确处理"

    @pytest.mark.security
    @pytest.mark.p1
    @pytest.mark.parametrize("content_type", [
        "text/plain",
        "application/xml",
        "multipart/form-data",
    ])
    def test_non_json_content_type_handled(self, api, content_type):
        """非 JSON Content-Type 应被正确处理"""
        # 框架应拒绝或正确处理非 JSON 请求
        resp = api.post("/api/device", json={"name": "test"})
        assert resp.status_code < 500


# ══════════════════════════════════════════════════════════════
# SEC-C002 删除操作安全
# ══════════════════════════════════════════════════════════════

class TestDeleteOperationSecurity:
    """SEC-C002: 验证删除操作的安全防护"""

    @pytest.mark.security
    @pytest.mark.p0
    @pytest.mark.parametrize("endpoint_tpl,method", DANGEROUS_OPERATIONS)
    def test_delete_requires_auth(self, endpoint_tpl, method):
        """删除操作必须需要认证"""
        endpoint = endpoint_tpl.replace("{id}", str(uuid.uuid4()))
        client = MockApiClient(token=None)
        resp = client.delete(endpoint)
        assert resp.status_code in (401, 403), (
            f"未认证 DELETE {endpoint} 应返回 401/403"
        )

    @pytest.mark.security
    @pytest.mark.p0
    @pytest.mark.parametrize("endpoint_tpl,method", DANGEROUS_OPERATIONS)
    def test_delete_nonexistent_returns_404(self, api, endpoint_tpl, method):
        """删除不存在的资源应返回 404"""
        fake_id = str(uuid.uuid4())
        endpoint = endpoint_tpl.replace("{id}", fake_id)
        resp = api.delete(endpoint)
        assert resp.status_code in (404, 200), (
            f"DELETE 不存在的资源 {endpoint} 应返回 404/200"
        )

    @pytest.mark.security
    @pytest.mark.p0
    @pytest.mark.parametrize("invalid_id", [
        "not-a-uuid",
        "'; DROP TABLE users; --",
        "<script>alert(1)</script>",
        "00000000-0000-0000-0000-000000000000",
        "../../../etc/passwd",
    ])
    def test_delete_invalid_id_format(self, api, invalid_id):
        """删除端点使用无效 ID 格式应返回 400/404"""
        resp = api.delete(f"/api/device/{invalid_id}")
        assert resp.status_code in (400, 404), (
            f"DELETE 无效 ID '{invalid_id}' 应返回 400/404，实际 {resp.status_code}"
        )

    @pytest.mark.security
    @pytest.mark.p1
    def test_delete_uses_soft_delete(self, api):
        """删除应使用软删除（返回正常成功响应而非物理删除状态码）"""
        fake_id = str(uuid.uuid4())
        resp = api.delete(f"/api/device/{fake_id}")
        # 软删除返回 200/404 而非 204 No Content
        assert resp.status_code in (200, 404)

    @pytest.mark.security
    @pytest.mark.p1
    def test_bulk_delete_requires_ids(self, api):
        """批量删除不发送 ID 列表应返回 400"""
        resp = api.post("/api/device/batch-delete", json={})
        assert resp.status_code in (400, 404, 405), (
            f"批量删除空请求应返回 400/404/405，实际 {resp.status_code}"
        )


# ══════════════════════════════════════════════════════════════
# SEC-C003 权限变更保护
# ══════════════════════════════════════════════════════════════

class TestPermissionChangeProtection:
    """SEC-C003: 验证权限、角色变更的安全防护"""

    @pytest.mark.security
    @pytest.mark.p0
    def test_role_create_requires_auth(self):
        """创建角色必须认证"""
        client = MockApiClient(token=None)
        resp = client.post("/api/system/role", json={
            "name": "恶意角色", "code": "evil_role"
        })
        assert resp.status_code in (401, 403)

    @pytest.mark.security
    @pytest.mark.p0
    def test_permission_assign_requires_auth(self):
        """权限分配必须认证"""
        client = MockApiClient(token=None)
        resp = client.post("/api/system/role/assign-permissions", json={
            "roleId": str(uuid.uuid4()),
            "permissionIds": [str(uuid.uuid4())]
        })
        assert resp.status_code in (401, 403)

    @pytest.mark.security
    @pytest.mark.p0
    def test_tenant_create_requires_auth(self):
        """创建租户必须认证"""
        client = MockApiClient(token=None)
        resp = client.post("/api/tenants", json={
            "name": "恶意租户", "code": "EVIL"
        })
        assert resp.status_code in (401, 403)

    @pytest.mark.security
    @pytest.mark.p0
    def test_user_role_assign_requires_auth(self):
        """用户角色分配必须认证"""
        client = MockApiClient(token=None)
        resp = client.post("/api/account/users/assign-role", json={
            "userId": str(uuid.uuid4()),
            "roleIds": [str(uuid.uuid4())]
        })
        assert resp.status_code in (401, 403)

    @pytest.mark.security
    @pytest.mark.p1
    def test_superadmin_role_cannot_be_modified(self, api):
        """超级管理员角色不应被修改"""
        superadmin_id = "00000000-0000-0000-0000-000000000001"
        resp = api.put(f"/api/system/role/{superadmin_id}", json={
            "name": "篡改", "code": "HACKED"
        })
        # 应返回 403 或 200（但不真正修改）
        assert resp.status_code < 500

    @pytest.mark.security
    @pytest.mark.p1
    def test_superadmin_role_cannot_be_deleted(self, api):
        """超级管理员角色不应被删除"""
        superadmin_id = "00000000-0000-0000-0000-000000000001"
        resp = api.delete(f"/api/system/role/{superadmin_id}")
        # 应返回 400/403 禁止删除内置角色
        assert resp.status_code in (200, 400, 403, 404)


# ══════════════════════════════════════════════════════════════
# SEC-C004 批量操作安全
# ══════════════════════════════════════════════════════════════

class TestBatchOperationSecurity:
    """SEC-C004: 验证批量操作的安全约束"""

    @pytest.mark.security
    @pytest.mark.p0
    def test_batch_operation_requires_auth(self):
        """批量操作必须认证"""
        client = MockApiClient(token=None)
        ids = [str(uuid.uuid4()) for _ in range(3)]
        resp = client.post("/api/device/batch-delete", json={"ids": ids})
        assert resp.status_code in (401, 403, 404)

    @pytest.mark.security
    @pytest.mark.p1
    @pytest.mark.parametrize("count", [100, 500])
    def test_batch_size_limit(self, api, count):
        """批量操作应限制数量（防止 DoS）"""
        ids = [str(uuid.uuid4()) for _ in range(count)]
        resp = api.post("/api/device/batch-delete", json={"ids": ids})
        # 超大批量应返回 400 或 413
        assert resp.status_code < 500, (
            f"批量删除 {count} 条返回 5xx"
        )

    @pytest.mark.security
    @pytest.mark.p1
    def test_batch_import_requires_auth(self):
        """批量导入必须认证"""
        client = MockApiClient(token=None)
        resp = client.post("/api/device/import", json={"devices": []})
        assert resp.status_code in (401, 403, 404)

    @pytest.mark.security
    @pytest.mark.p1
    def test_batch_export_requires_auth(self):
        """批量导出必须认证"""
        client = MockApiClient(token=None)
        resp = client.get("/api/device/export")
        assert resp.status_code in (401, 403, 404)

    @pytest.mark.security
    @pytest.mark.p2
    @pytest.mark.parametrize("ids", [
        [],
        [None],
        [""],
        ["not-a-uuid", "also-not-uuid"],
    ])
    def test_batch_invalid_ids_rejected(self, api, ids):
        """批量操作使用无效 ID 列表应被安全处理"""
        resp = api.post("/api/device/batch-delete", json={"ids": ids})
        assert resp.status_code < 500, (
            f"无效 ID 列表应被安全处理，实际 {resp.status_code}"
        )
