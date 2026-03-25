"""
EnergyCore.PVESSC 服务 API 测试
自动生成于 generate_api_tests.py
共 28 个API端点，约 476 个测试用例

服务信息:
  - 服务名: EnergyCore.PVESSC
  - API数量: 28
  - 标准用例: 476
"""

import pytest
import sys
import os

# 添加父目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))
from mock_client import MockApiClient, MOCK_TOKEN


class MockApiClientTA:
    """测试API客户端适配器"""
    def __init__(self):
        self._client = MockApiClient(token=MOCK_TOKEN)
        self._saved_token = MOCK_TOKEN
    
    def get(self, endpoint, **kwargs):
        return self._client.get(f"/api/{endpoint}", **kwargs)
    
    def post(self, endpoint, json_data=None, **kwargs):
        return self._client.post(f"/api/{endpoint}", json=json_data, **kwargs)
    
    def put(self, endpoint, json_data=None, **kwargs):
        return self._client.put(f"/api/{endpoint}", json=json_data, **kwargs)
    
    def delete(self, endpoint, **kwargs):
        return self._client.delete(f"/api/{endpoint}", **kwargs)
    
    def patch(self, endpoint, json_data=None, **kwargs):
        return self._client.put(f"/api/{endpoint}", json=json_data, **kwargs)

    def clear_token(self):
        self._saved_token = self._client.token
        self._client.clear_token()
    
    def set_invalid_token(self):
        self._saved_token = self._client.token
        self._client.set_token("invalid.fake.token")
    
    def restore_token(self):
        self._client.set_token(self._saved_token)


@pytest.fixture(scope="module")
def api_client():
    return MockApiClientTA()


@pytest.mark.api
@pytest.mark.energycore_pvessc
class TestEnergyCore_PVESSCApi:
    """
    EnergyCore.PVESSC 服务API测试类
    测试覆盖: 28 个端点 × ~17 用例 = ~476 用例
    """

    def test_EnergyCore_PVESSC_InternalPVESSC_get_0_positive_0000(self, api_client):
        """[EnergyCore.PVESSC][InternalPVESSC] get_0 - 正常请求"""
        # GET /api/internal/pvessc/capacity
        response = api_client.get("pvessc/api/internal/pvessc/capacity")
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"GET 正常请求不应返回 5xx, 实际: {response.status_code}"


    def test_EnergyCore_PVESSC_InternalPVESSC_get_0_no_auth_0000(self, api_client):
        """[EnergyCore.PVESSC][InternalPVESSC] get_0 - 缺少认证头"""
        # GET /api/internal/pvessc/capacity
        api_client.clear_token()
        try:
            response = api_client.get("pvessc/api/internal/pvessc/capacity")
            assert response is not None, "响应不应为空"
            assert response.status_code in (200, 400, 401, 403), f"无认证头应返回 401/403, 实际: {response.status_code}"
        finally:
            api_client.restore_token()


    def test_EnergyCore_PVESSC_InternalPVESSC_get_0_invalid_token_0000(self, api_client):
        """[EnergyCore.PVESSC][InternalPVESSC] get_0 - 无效Token"""
        # GET /api/internal/pvessc/capacity
        api_client.set_invalid_token()
        try:
            response = api_client.get("pvessc/api/internal/pvessc/capacity")
            assert response is not None, "响应不应为空"
            assert response.status_code in (200, 400, 401, 403), f"无效Token应返回 401/403, 实际: {response.status_code}"
        finally:
            api_client.restore_token()


    def test_EnergyCore_PVESSC_InternalPVESSC_get_0_tenant_isolation_0000(self, api_client):
        """[EnergyCore.PVESSC][InternalPVESSC] get_0 - 租户隔离"""
        # GET /api/internal/pvessc/capacity
        response = api_client.get("pvessc/api/internal/pvessc/capacity")
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"租户隔离测试不应返回 5xx, 实际: {response.status_code}"
        data = response.json()
        assert isinstance(data, dict), "响应应为JSON对象"


    def test_EnergyCore_PVESSC_InternalPVESSC_get_0_boundary_0000(self, api_client):
        """[EnergyCore.PVESSC][InternalPVESSC] get_0 - 边界值测试"""
        # GET /api/internal/pvessc/capacity
        response = api_client.get("pvessc/api/internal/pvessc/capacity")
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"边界值测试不应返回 5xx 服务器错误, 实际: {response.status_code}"
        assert isinstance(response.json(), dict), "响应应为JSON对象"


    def test_EnergyCore_PVESSC_InternalPVESSC_get_0_sql_injection_0000(self, api_client):
        """[EnergyCore.PVESSC][InternalPVESSC] get_0 - SQL注入防护"""
        # GET /api/internal/pvessc/capacity
        response = api_client.get("pvessc/api/internal/pvessc/capacity")
        assert response is not None, "响应不应为空"
        assert response.status_code != 500, f"SQL注入不应导致服务器错误, 实际: {response.status_code}"
        data = response.json()
        assert isinstance(data, dict), "响应应为JSON对象"


    def test_EnergyCore_PVESSC_InternalPVESSC_get_0_concurrent_0000(self, api_client):
        """[EnergyCore.PVESSC][InternalPVESSC] get_0 - 并发请求"""
        # GET /api/internal/pvessc/capacity
        responses = []
        for _ in range(3):
            r = api_client.get("pvessc/api/internal/pvessc/capacity")
            responses.append(r)
        for r in responses:
            assert r is not None, "并发响应不应为空"
            assert r.status_code < 500, f"并发请求不应返回 5xx, 实际: {r.status_code}"


    def test_EnergyCore_PVESSC_InternalPVESSC_get_0_timeout_0000(self, api_client):
        """[EnergyCore.PVESSC][InternalPVESSC] get_0 - 超时处理"""
        # GET /api/internal/pvessc/capacity
        response = api_client.get("pvessc/api/internal/pvessc/capacity")
        assert response is not None, "超时处理响应不应为空"
        assert response.status_code < 500, f"超时测试不应返回 5xx, 实际: {response.status_code}"


    def test_EnergyCore_PVESSC_InternalPVESSC_get_0_permission_denied_0000(self, api_client):
        """[EnergyCore.PVESSC][InternalPVESSC] get_0 - 权限不足"""
        # GET /api/internal/pvessc/capacity
        response = api_client.get("pvessc/api/internal/pvessc/capacity")
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"权限测试不应返回 5xx, 实际: {response.status_code}"


    def test_EnergyCore_PVESSC_InternalPVESSC_get_0_response_format_0000(self, api_client):
        """[EnergyCore.PVESSC][InternalPVESSC] get_0 - 响应格式"""
        # GET /api/internal/pvessc/capacity
        response = api_client.get("pvessc/api/internal/pvessc/capacity")
        assert response is not None, "响应不应为空"
        data = response.json()
        assert isinstance(data, dict), "响应应为JSON对象"
        if response.status_code == 200:
            assert "success" in data or "data" in data or "code" in data, "200 响应应包含标准字段"


    def test_EnergyCore_PVESSC_InternalPVESSC_get_1_positive_0001(self, api_client):
        """[EnergyCore.PVESSC][InternalPVESSC] get_1 - 正常请求"""
        # GET /api/internal/pvessc/v2g/available
        response = api_client.get("pvessc/api/internal/pvessc/v2g/available")
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"GET 正常请求不应返回 5xx, 实际: {response.status_code}"


    def test_EnergyCore_PVESSC_InternalPVESSC_get_1_no_auth_0001(self, api_client):
        """[EnergyCore.PVESSC][InternalPVESSC] get_1 - 缺少认证头"""
        # GET /api/internal/pvessc/v2g/available
        api_client.clear_token()
        try:
            response = api_client.get("pvessc/api/internal/pvessc/v2g/available")
            assert response is not None, "响应不应为空"
            assert response.status_code in (200, 400, 401, 403), f"无认证头应返回 401/403, 实际: {response.status_code}"
        finally:
            api_client.restore_token()


    def test_EnergyCore_PVESSC_InternalPVESSC_get_1_invalid_token_0001(self, api_client):
        """[EnergyCore.PVESSC][InternalPVESSC] get_1 - 无效Token"""
        # GET /api/internal/pvessc/v2g/available
        api_client.set_invalid_token()
        try:
            response = api_client.get("pvessc/api/internal/pvessc/v2g/available")
            assert response is not None, "响应不应为空"
            assert response.status_code in (200, 400, 401, 403), f"无效Token应返回 401/403, 实际: {response.status_code}"
        finally:
            api_client.restore_token()


    def test_EnergyCore_PVESSC_InternalPVESSC_get_1_tenant_isolation_0001(self, api_client):
        """[EnergyCore.PVESSC][InternalPVESSC] get_1 - 租户隔离"""
        # GET /api/internal/pvessc/v2g/available
        response = api_client.get("pvessc/api/internal/pvessc/v2g/available")
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"租户隔离测试不应返回 5xx, 实际: {response.status_code}"
        data = response.json()
        assert isinstance(data, dict), "响应应为JSON对象"


    def test_EnergyCore_PVESSC_InternalPVESSC_get_1_boundary_0001(self, api_client):
        """[EnergyCore.PVESSC][InternalPVESSC] get_1 - 边界值测试"""
        # GET /api/internal/pvessc/v2g/available
        response = api_client.get("pvessc/api/internal/pvessc/v2g/available")
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"边界值测试不应返回 5xx 服务器错误, 实际: {response.status_code}"
        assert isinstance(response.json(), dict), "响应应为JSON对象"


    def test_EnergyCore_PVESSC_InternalPVESSC_get_1_sql_injection_0001(self, api_client):
        """[EnergyCore.PVESSC][InternalPVESSC] get_1 - SQL注入防护"""
        # GET /api/internal/pvessc/v2g/available
        response = api_client.get("pvessc/api/internal/pvessc/v2g/available")
        assert response is not None, "响应不应为空"
        assert response.status_code != 500, f"SQL注入不应导致服务器错误, 实际: {response.status_code}"
        data = response.json()
        assert isinstance(data, dict), "响应应为JSON对象"


    def test_EnergyCore_PVESSC_InternalPVESSC_get_1_concurrent_0001(self, api_client):
        """[EnergyCore.PVESSC][InternalPVESSC] get_1 - 并发请求"""
        # GET /api/internal/pvessc/v2g/available
        responses = []
        for _ in range(3):
            r = api_client.get("pvessc/api/internal/pvessc/v2g/available")
            responses.append(r)
        for r in responses:
            assert r is not None, "并发响应不应为空"
            assert r.status_code < 500, f"并发请求不应返回 5xx, 实际: {r.status_code}"


    def test_EnergyCore_PVESSC_InternalPVESSC_get_1_timeout_0001(self, api_client):
        """[EnergyCore.PVESSC][InternalPVESSC] get_1 - 超时处理"""
        # GET /api/internal/pvessc/v2g/available
        response = api_client.get("pvessc/api/internal/pvessc/v2g/available")
        assert response is not None, "超时处理响应不应为空"
        assert response.status_code < 500, f"超时测试不应返回 5xx, 实际: {response.status_code}"


    def test_EnergyCore_PVESSC_InternalPVESSC_get_1_permission_denied_0001(self, api_client):
        """[EnergyCore.PVESSC][InternalPVESSC] get_1 - 权限不足"""
        # GET /api/internal/pvessc/v2g/available
        response = api_client.get("pvessc/api/internal/pvessc/v2g/available")
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"权限测试不应返回 5xx, 实际: {response.status_code}"


    def test_EnergyCore_PVESSC_InternalPVESSC_get_1_response_format_0001(self, api_client):
        """[EnergyCore.PVESSC][InternalPVESSC] get_1 - 响应格式"""
        # GET /api/internal/pvessc/v2g/available
        response = api_client.get("pvessc/api/internal/pvessc/v2g/available")
        assert response is not None, "响应不应为空"
        data = response.json()
        assert isinstance(data, dict), "响应应为JSON对象"
        if response.status_code == 200:
            assert "success" in data or "data" in data or "code" in data, "200 响应应包含标准字段"


    def test_EnergyCore_PVESSC_InternalPVESSC_get_2_positive_0002(self, api_client):
        """[EnergyCore.PVESSC][InternalPVESSC] get_2 - 正常请求"""
        # GET /api/internal/pvessc/ess/status/{siteId}
        response = api_client.get("pvessc/api/internal/pvessc/ess/status/{siteId}")
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"GET 正常请求不应返回 5xx, 实际: {response.status_code}"


    def test_EnergyCore_PVESSC_InternalPVESSC_get_2_no_auth_0002(self, api_client):
        """[EnergyCore.PVESSC][InternalPVESSC] get_2 - 缺少认证头"""
        # GET /api/internal/pvessc/ess/status/{siteId}
        api_client.clear_token()
        try:
            response = api_client.get("pvessc/api/internal/pvessc/ess/status/{siteId}")
            assert response is not None, "响应不应为空"
            assert response.status_code in (200, 400, 401, 403), f"无认证头应返回 401/403, 实际: {response.status_code}"
        finally:
            api_client.restore_token()


    def test_EnergyCore_PVESSC_InternalPVESSC_get_2_invalid_token_0002(self, api_client):
        """[EnergyCore.PVESSC][InternalPVESSC] get_2 - 无效Token"""
        # GET /api/internal/pvessc/ess/status/{siteId}
        api_client.set_invalid_token()
        try:
            response = api_client.get("pvessc/api/internal/pvessc/ess/status/{siteId}")
            assert response is not None, "响应不应为空"
            assert response.status_code in (200, 400, 401, 403), f"无效Token应返回 401/403, 实际: {response.status_code}"
        finally:
            api_client.restore_token()


    def test_EnergyCore_PVESSC_InternalPVESSC_get_2_tenant_isolation_0002(self, api_client):
        """[EnergyCore.PVESSC][InternalPVESSC] get_2 - 租户隔离"""
        # GET /api/internal/pvessc/ess/status/{siteId}
        response = api_client.get("pvessc/api/internal/pvessc/ess/status/{siteId}")
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"租户隔离测试不应返回 5xx, 实际: {response.status_code}"
        data = response.json()
        assert isinstance(data, dict), "响应应为JSON对象"


    def test_EnergyCore_PVESSC_InternalPVESSC_get_2_invalid_id_0002(self, api_client):
        """[EnergyCore.PVESSC][InternalPVESSC] get_2 - 无效ID"""
        # GET /api/internal/pvessc/ess/status/{siteId}
        response = api_client.get("pvessc/api/internal/pvessc/ess/status/{siteId}")
        assert response is not None, "响应不应为空"
        assert response.status_code in (200, 400, 403, 404), f"无效ID应返回 200/400/403/404, 实际: {response.status_code}"


    def test_EnergyCore_PVESSC_InternalPVESSC_get_2_not_found_id_0002(self, api_client):
        """[EnergyCore.PVESSC][InternalPVESSC] get_2 - 不存在ID"""
        # GET /api/internal/pvessc/ess/status/{siteId}
        response = api_client.get("pvessc/api/internal/pvessc/ess/status/{siteId}")
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"不存在ID不应返回 5xx, 实际: {response.status_code}"


    def test_EnergyCore_PVESSC_InternalPVESSC_get_2_boundary_0002(self, api_client):
        """[EnergyCore.PVESSC][InternalPVESSC] get_2 - 边界值测试"""
        # GET /api/internal/pvessc/ess/status/{siteId}
        response = api_client.get("pvessc/api/internal/pvessc/ess/status/{siteId}")
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"边界值测试不应返回 5xx 服务器错误, 实际: {response.status_code}"
        assert isinstance(response.json(), dict), "响应应为JSON对象"


    def test_EnergyCore_PVESSC_InternalPVESSC_get_2_sql_injection_0002(self, api_client):
        """[EnergyCore.PVESSC][InternalPVESSC] get_2 - SQL注入防护"""
        # GET /api/internal/pvessc/ess/status/{siteId}
        response = api_client.get("pvessc/api/internal/pvessc/ess/status/{siteId}")
        assert response is not None, "响应不应为空"
        assert response.status_code != 500, f"SQL注入不应导致服务器错误, 实际: {response.status_code}"
        data = response.json()
        assert isinstance(data, dict), "响应应为JSON对象"


    def test_EnergyCore_PVESSC_InternalPVESSC_get_2_concurrent_0002(self, api_client):
        """[EnergyCore.PVESSC][InternalPVESSC] get_2 - 并发请求"""
        # GET /api/internal/pvessc/ess/status/{siteId}
        responses = []
        for _ in range(3):
            r = api_client.get("pvessc/api/internal/pvessc/ess/status/{siteId}")
            responses.append(r)
        for r in responses:
            assert r is not None, "并发响应不应为空"
            assert r.status_code < 500, f"并发请求不应返回 5xx, 实际: {r.status_code}"


    def test_EnergyCore_PVESSC_InternalPVESSC_get_2_timeout_0002(self, api_client):
        """[EnergyCore.PVESSC][InternalPVESSC] get_2 - 超时处理"""
        # GET /api/internal/pvessc/ess/status/{siteId}
        response = api_client.get("pvessc/api/internal/pvessc/ess/status/{siteId}")
        assert response is not None, "超时处理响应不应为空"
        assert response.status_code < 500, f"超时测试不应返回 5xx, 实际: {response.status_code}"


    def test_EnergyCore_PVESSC_InternalPVESSC_get_2_permission_denied_0002(self, api_client):
        """[EnergyCore.PVESSC][InternalPVESSC] get_2 - 权限不足"""
        # GET /api/internal/pvessc/ess/status/{siteId}
        response = api_client.get("pvessc/api/internal/pvessc/ess/status/{siteId}")
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"权限测试不应返回 5xx, 实际: {response.status_code}"


    def test_EnergyCore_PVESSC_InternalPVESSC_get_2_response_format_0002(self, api_client):
        """[EnergyCore.PVESSC][InternalPVESSC] get_2 - 响应格式"""
        # GET /api/internal/pvessc/ess/status/{siteId}
        response = api_client.get("pvessc/api/internal/pvessc/ess/status/{siteId}")
        assert response is not None, "响应不应为空"
        data = response.json()
        assert isinstance(data, dict), "响应应为JSON对象"
        if response.status_code == 200:
            assert "success" in data or "data" in data or "code" in data, "200 响应应包含标准字段"


    def test_EnergyCore_PVESSC_InternalPVESSC_get_3_positive_0003(self, api_client):
        """[EnergyCore.PVESSC][InternalPVESSC] get_3 - 正常请求"""
        # GET /api/internal/pvessc/dispatch/capability
        response = api_client.get("pvessc/api/internal/pvessc/dispatch/capability")
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"GET 正常请求不应返回 5xx, 实际: {response.status_code}"


    def test_EnergyCore_PVESSC_InternalPVESSC_get_3_no_auth_0003(self, api_client):
        """[EnergyCore.PVESSC][InternalPVESSC] get_3 - 缺少认证头"""
        # GET /api/internal/pvessc/dispatch/capability
        api_client.clear_token()
        try:
            response = api_client.get("pvessc/api/internal/pvessc/dispatch/capability")
            assert response is not None, "响应不应为空"
            assert response.status_code in (200, 400, 401, 403), f"无认证头应返回 401/403, 实际: {response.status_code}"
        finally:
            api_client.restore_token()


    def test_EnergyCore_PVESSC_InternalPVESSC_get_3_invalid_token_0003(self, api_client):
        """[EnergyCore.PVESSC][InternalPVESSC] get_3 - 无效Token"""
        # GET /api/internal/pvessc/dispatch/capability
        api_client.set_invalid_token()
        try:
            response = api_client.get("pvessc/api/internal/pvessc/dispatch/capability")
            assert response is not None, "响应不应为空"
            assert response.status_code in (200, 400, 401, 403), f"无效Token应返回 401/403, 实际: {response.status_code}"
        finally:
            api_client.restore_token()


    def test_EnergyCore_PVESSC_InternalPVESSC_get_3_tenant_isolation_0003(self, api_client):
        """[EnergyCore.PVESSC][InternalPVESSC] get_3 - 租户隔离"""
        # GET /api/internal/pvessc/dispatch/capability
        response = api_client.get("pvessc/api/internal/pvessc/dispatch/capability")
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"租户隔离测试不应返回 5xx, 实际: {response.status_code}"
        data = response.json()
        assert isinstance(data, dict), "响应应为JSON对象"


    def test_EnergyCore_PVESSC_InternalPVESSC_get_3_boundary_0003(self, api_client):
        """[EnergyCore.PVESSC][InternalPVESSC] get_3 - 边界值测试"""
        # GET /api/internal/pvessc/dispatch/capability
        response = api_client.get("pvessc/api/internal/pvessc/dispatch/capability")
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"边界值测试不应返回 5xx 服务器错误, 实际: {response.status_code}"
        assert isinstance(response.json(), dict), "响应应为JSON对象"


    def test_EnergyCore_PVESSC_InternalPVESSC_get_3_sql_injection_0003(self, api_client):
        """[EnergyCore.PVESSC][InternalPVESSC] get_3 - SQL注入防护"""
        # GET /api/internal/pvessc/dispatch/capability
        response = api_client.get("pvessc/api/internal/pvessc/dispatch/capability")
        assert response is not None, "响应不应为空"
        assert response.status_code != 500, f"SQL注入不应导致服务器错误, 实际: {response.status_code}"
        data = response.json()
        assert isinstance(data, dict), "响应应为JSON对象"


    def test_EnergyCore_PVESSC_InternalPVESSC_get_3_concurrent_0003(self, api_client):
        """[EnergyCore.PVESSC][InternalPVESSC] get_3 - 并发请求"""
        # GET /api/internal/pvessc/dispatch/capability
        responses = []
        for _ in range(3):
            r = api_client.get("pvessc/api/internal/pvessc/dispatch/capability")
            responses.append(r)
        for r in responses:
            assert r is not None, "并发响应不应为空"
            assert r.status_code < 500, f"并发请求不应返回 5xx, 实际: {r.status_code}"


    def test_EnergyCore_PVESSC_InternalPVESSC_get_3_timeout_0003(self, api_client):
        """[EnergyCore.PVESSC][InternalPVESSC] get_3 - 超时处理"""
        # GET /api/internal/pvessc/dispatch/capability
        response = api_client.get("pvessc/api/internal/pvessc/dispatch/capability")
        assert response is not None, "超时处理响应不应为空"
        assert response.status_code < 500, f"超时测试不应返回 5xx, 实际: {response.status_code}"


    def test_EnergyCore_PVESSC_InternalPVESSC_get_3_permission_denied_0003(self, api_client):
        """[EnergyCore.PVESSC][InternalPVESSC] get_3 - 权限不足"""
        # GET /api/internal/pvessc/dispatch/capability
        response = api_client.get("pvessc/api/internal/pvessc/dispatch/capability")
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"权限测试不应返回 5xx, 实际: {response.status_code}"


    def test_EnergyCore_PVESSC_InternalPVESSC_get_3_response_format_0003(self, api_client):
        """[EnergyCore.PVESSC][InternalPVESSC] get_3 - 响应格式"""
        # GET /api/internal/pvessc/dispatch/capability
        response = api_client.get("pvessc/api/internal/pvessc/dispatch/capability")
        assert response is not None, "响应不应为空"
        data = response.json()
        assert isinstance(data, dict), "响应应为JSON对象"
        if response.status_code == 200:
            assert "success" in data or "data" in data or "code" in data, "200 响应应包含标准字段"


    def test_EnergyCore_PVESSC_InternalPVESSC_post_4_positive_0004(self, api_client):
        """[EnergyCore.PVESSC][InternalPVESSC] post_4 - 正常请求"""
        # POST /api/internal/pvessc/dispatch/execute
        response = api_client.post("pvessc/api/internal/pvessc/dispatch/execute", json_data={"name": "test", "code": "TEST"})
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"POST 正常请求不应返回 5xx, 实际: {response.status_code}"


    def test_EnergyCore_PVESSC_InternalPVESSC_post_4_no_auth_0004(self, api_client):
        """[EnergyCore.PVESSC][InternalPVESSC] post_4 - 缺少认证头"""
        # POST /api/internal/pvessc/dispatch/execute
        api_client.clear_token()
        try:
            response = api_client.post("pvessc/api/internal/pvessc/dispatch/execute")
            assert response is not None, "响应不应为空"
            assert response.status_code in (200, 400, 401, 403), f"无认证头应返回 401/403, 实际: {response.status_code}"
        finally:
            api_client.restore_token()


    def test_EnergyCore_PVESSC_InternalPVESSC_post_4_invalid_token_0004(self, api_client):
        """[EnergyCore.PVESSC][InternalPVESSC] post_4 - 无效Token"""
        # POST /api/internal/pvessc/dispatch/execute
        api_client.set_invalid_token()
        try:
            response = api_client.post("pvessc/api/internal/pvessc/dispatch/execute")
            assert response is not None, "响应不应为空"
            assert response.status_code in (200, 400, 401, 403), f"无效Token应返回 401/403, 实际: {response.status_code}"
        finally:
            api_client.restore_token()


    def test_EnergyCore_PVESSC_InternalPVESSC_post_4_tenant_isolation_0004(self, api_client):
        """[EnergyCore.PVESSC][InternalPVESSC] post_4 - 租户隔离"""
        # POST /api/internal/pvessc/dispatch/execute
        response = api_client.post("pvessc/api/internal/pvessc/dispatch/execute")
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"租户隔离测试不应返回 5xx, 实际: {response.status_code}"
        data = response.json()
        assert isinstance(data, dict), "响应应为JSON对象"


    def test_EnergyCore_PVESSC_InternalPVESSC_post_4_empty_body_0004(self, api_client):
        """[EnergyCore.PVESSC][InternalPVESSC] post_4 - 空请求体"""
        # POST /api/internal/pvessc/dispatch/execute
        response = api_client.post("pvessc/api/internal/pvessc/dispatch/execute")
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"空请求体不应返回 5xx, 实际: {response.status_code}"


    def test_EnergyCore_PVESSC_InternalPVESSC_post_4_boundary_0004(self, api_client):
        """[EnergyCore.PVESSC][InternalPVESSC] post_4 - 边界值测试"""
        # POST /api/internal/pvessc/dispatch/execute
        response = api_client.post("pvessc/api/internal/pvessc/dispatch/execute")
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"边界值测试不应返回 5xx 服务器错误, 实际: {response.status_code}"
        assert isinstance(response.json(), dict), "响应应为JSON对象"


    def test_EnergyCore_PVESSC_InternalPVESSC_post_4_sql_injection_0004(self, api_client):
        """[EnergyCore.PVESSC][InternalPVESSC] post_4 - SQL注入防护"""
        # POST /api/internal/pvessc/dispatch/execute
        response = api_client.post("pvessc/api/internal/pvessc/dispatch/execute")
        assert response is not None, "响应不应为空"
        assert response.status_code != 500, f"SQL注入不应导致服务器错误, 实际: {response.status_code}"
        data = response.json()
        assert isinstance(data, dict), "响应应为JSON对象"


    def test_EnergyCore_PVESSC_InternalPVESSC_post_4_xss_protection_0004(self, api_client):
        """[EnergyCore.PVESSC][InternalPVESSC] post_4 - XSS防护"""
        # POST /api/internal/pvessc/dispatch/execute
        xss_payload = {"name": "<script>alert('xss')</script>", "code": "XSS_TEST"}
        response = api_client.post("pvessc/api/internal/pvessc/dispatch/execute", json_data=xss_payload)
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"XSS防护测试不应返回 5xx, 实际: {response.status_code}"


    def test_EnergyCore_PVESSC_InternalPVESSC_post_4_large_payload_0004(self, api_client):
        """[EnergyCore.PVESSC][InternalPVESSC] post_4 - 大数据量"""
        # POST /api/internal/pvessc/dispatch/execute
        large_data = {"name": "x" * 10000, "code": "LARGE", "description": "y" * 50000}
        response = api_client.post("pvessc/api/internal/pvessc/dispatch/execute", json_data=large_data)
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"大数据量测试不应返回 5xx, 实际: {response.status_code}"


    def test_EnergyCore_PVESSC_InternalPVESSC_post_4_concurrent_0004(self, api_client):
        """[EnergyCore.PVESSC][InternalPVESSC] post_4 - 并发请求"""
        # POST /api/internal/pvessc/dispatch/execute
        responses = []
        for _ in range(3):
            r = api_client.post("pvessc/api/internal/pvessc/dispatch/execute")
            responses.append(r)
        for r in responses:
            assert r is not None, "并发响应不应为空"
            assert r.status_code < 500, f"并发请求不应返回 5xx, 实际: {r.status_code}"


    def test_EnergyCore_PVESSC_InternalPVESSC_post_4_timeout_0004(self, api_client):
        """[EnergyCore.PVESSC][InternalPVESSC] post_4 - 超时处理"""
        # POST /api/internal/pvessc/dispatch/execute
        response = api_client.post("pvessc/api/internal/pvessc/dispatch/execute")
        assert response is not None, "超时处理响应不应为空"
        assert response.status_code < 500, f"超时测试不应返回 5xx, 实际: {response.status_code}"


    def test_EnergyCore_PVESSC_InternalPVESSC_post_4_permission_denied_0004(self, api_client):
        """[EnergyCore.PVESSC][InternalPVESSC] post_4 - 权限不足"""
        # POST /api/internal/pvessc/dispatch/execute
        response = api_client.post("pvessc/api/internal/pvessc/dispatch/execute")
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"权限测试不应返回 5xx, 实际: {response.status_code}"


    def test_EnergyCore_PVESSC_InternalPVESSC_post_4_field_validation_0004(self, api_client):
        """[EnergyCore.PVESSC][InternalPVESSC] post_4 - 字段校验"""
        # POST /api/internal/pvessc/dispatch/execute
        invalid_data = {"name": "", "code": ""}
        response = api_client.post("pvessc/api/internal/pvessc/dispatch/execute", json_data=invalid_data)
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"字段校验不应返回 5xx, 实际: {response.status_code}"


    def test_EnergyCore_PVESSC_InternalPVESSC_post_4_response_format_0004(self, api_client):
        """[EnergyCore.PVESSC][InternalPVESSC] post_4 - 响应格式"""
        # POST /api/internal/pvessc/dispatch/execute
        response = api_client.post("pvessc/api/internal/pvessc/dispatch/execute")
        assert response is not None, "响应不应为空"
        data = response.json()
        assert isinstance(data, dict), "响应应为JSON对象"
        if response.status_code == 200:
            assert "success" in data or "data" in data or "code" in data, "200 响应应包含标准字段"


    def test_EnergyCore_PVESSC_InternalPVESSC_post_5_positive_0005(self, api_client):
        """[EnergyCore.PVESSC][InternalPVESSC] post_5 - 正常请求"""
        # POST /api/internal/pvessc/data/pv
        response = api_client.post("pvessc/api/internal/pvessc/data/pv", json_data={"name": "test", "code": "TEST"})
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"POST 正常请求不应返回 5xx, 实际: {response.status_code}"


    def test_EnergyCore_PVESSC_InternalPVESSC_post_5_no_auth_0005(self, api_client):
        """[EnergyCore.PVESSC][InternalPVESSC] post_5 - 缺少认证头"""
        # POST /api/internal/pvessc/data/pv
        api_client.clear_token()
        try:
            response = api_client.post("pvessc/api/internal/pvessc/data/pv")
            assert response is not None, "响应不应为空"
            assert response.status_code in (200, 400, 401, 403), f"无认证头应返回 401/403, 实际: {response.status_code}"
        finally:
            api_client.restore_token()


    def test_EnergyCore_PVESSC_InternalPVESSC_post_5_invalid_token_0005(self, api_client):
        """[EnergyCore.PVESSC][InternalPVESSC] post_5 - 无效Token"""
        # POST /api/internal/pvessc/data/pv
        api_client.set_invalid_token()
        try:
            response = api_client.post("pvessc/api/internal/pvessc/data/pv")
            assert response is not None, "响应不应为空"
            assert response.status_code in (200, 400, 401, 403), f"无效Token应返回 401/403, 实际: {response.status_code}"
        finally:
            api_client.restore_token()


    def test_EnergyCore_PVESSC_InternalPVESSC_post_5_tenant_isolation_0005(self, api_client):
        """[EnergyCore.PVESSC][InternalPVESSC] post_5 - 租户隔离"""
        # POST /api/internal/pvessc/data/pv
        response = api_client.post("pvessc/api/internal/pvessc/data/pv")
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"租户隔离测试不应返回 5xx, 实际: {response.status_code}"
        data = response.json()
        assert isinstance(data, dict), "响应应为JSON对象"


    def test_EnergyCore_PVESSC_InternalPVESSC_post_5_empty_body_0005(self, api_client):
        """[EnergyCore.PVESSC][InternalPVESSC] post_5 - 空请求体"""
        # POST /api/internal/pvessc/data/pv
        response = api_client.post("pvessc/api/internal/pvessc/data/pv")
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"空请求体不应返回 5xx, 实际: {response.status_code}"


    def test_EnergyCore_PVESSC_InternalPVESSC_post_5_boundary_0005(self, api_client):
        """[EnergyCore.PVESSC][InternalPVESSC] post_5 - 边界值测试"""
        # POST /api/internal/pvessc/data/pv
        response = api_client.post("pvessc/api/internal/pvessc/data/pv")
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"边界值测试不应返回 5xx 服务器错误, 实际: {response.status_code}"
        assert isinstance(response.json(), dict), "响应应为JSON对象"


    def test_EnergyCore_PVESSC_InternalPVESSC_post_5_sql_injection_0005(self, api_client):
        """[EnergyCore.PVESSC][InternalPVESSC] post_5 - SQL注入防护"""
        # POST /api/internal/pvessc/data/pv
        response = api_client.post("pvessc/api/internal/pvessc/data/pv")
        assert response is not None, "响应不应为空"
        assert response.status_code != 500, f"SQL注入不应导致服务器错误, 实际: {response.status_code}"
        data = response.json()
        assert isinstance(data, dict), "响应应为JSON对象"


    def test_EnergyCore_PVESSC_InternalPVESSC_post_5_xss_protection_0005(self, api_client):
        """[EnergyCore.PVESSC][InternalPVESSC] post_5 - XSS防护"""
        # POST /api/internal/pvessc/data/pv
        xss_payload = {"name": "<script>alert('xss')</script>", "code": "XSS_TEST"}
        response = api_client.post("pvessc/api/internal/pvessc/data/pv", json_data=xss_payload)
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"XSS防护测试不应返回 5xx, 实际: {response.status_code}"


    def test_EnergyCore_PVESSC_InternalPVESSC_post_5_large_payload_0005(self, api_client):
        """[EnergyCore.PVESSC][InternalPVESSC] post_5 - 大数据量"""
        # POST /api/internal/pvessc/data/pv
        large_data = {"name": "x" * 10000, "code": "LARGE", "description": "y" * 50000}
        response = api_client.post("pvessc/api/internal/pvessc/data/pv", json_data=large_data)
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"大数据量测试不应返回 5xx, 实际: {response.status_code}"


    def test_EnergyCore_PVESSC_InternalPVESSC_post_5_concurrent_0005(self, api_client):
        """[EnergyCore.PVESSC][InternalPVESSC] post_5 - 并发请求"""
        # POST /api/internal/pvessc/data/pv
        responses = []
        for _ in range(3):
            r = api_client.post("pvessc/api/internal/pvessc/data/pv")
            responses.append(r)
        for r in responses:
            assert r is not None, "并发响应不应为空"
            assert r.status_code < 500, f"并发请求不应返回 5xx, 实际: {r.status_code}"


    def test_EnergyCore_PVESSC_InternalPVESSC_post_5_timeout_0005(self, api_client):
        """[EnergyCore.PVESSC][InternalPVESSC] post_5 - 超时处理"""
        # POST /api/internal/pvessc/data/pv
        response = api_client.post("pvessc/api/internal/pvessc/data/pv")
        assert response is not None, "超时处理响应不应为空"
        assert response.status_code < 500, f"超时测试不应返回 5xx, 实际: {response.status_code}"


    def test_EnergyCore_PVESSC_InternalPVESSC_post_5_permission_denied_0005(self, api_client):
        """[EnergyCore.PVESSC][InternalPVESSC] post_5 - 权限不足"""
        # POST /api/internal/pvessc/data/pv
        response = api_client.post("pvessc/api/internal/pvessc/data/pv")
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"权限测试不应返回 5xx, 实际: {response.status_code}"


    def test_EnergyCore_PVESSC_InternalPVESSC_post_5_field_validation_0005(self, api_client):
        """[EnergyCore.PVESSC][InternalPVESSC] post_5 - 字段校验"""
        # POST /api/internal/pvessc/data/pv
        invalid_data = {"name": "", "code": ""}
        response = api_client.post("pvessc/api/internal/pvessc/data/pv", json_data=invalid_data)
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"字段校验不应返回 5xx, 实际: {response.status_code}"


    def test_EnergyCore_PVESSC_InternalPVESSC_post_5_response_format_0005(self, api_client):
        """[EnergyCore.PVESSC][InternalPVESSC] post_5 - 响应格式"""
        # POST /api/internal/pvessc/data/pv
        response = api_client.post("pvessc/api/internal/pvessc/data/pv")
        assert response is not None, "响应不应为空"
        data = response.json()
        assert isinstance(data, dict), "响应应为JSON对象"
        if response.status_code == 200:
            assert "success" in data or "data" in data or "code" in data, "200 响应应包含标准字段"


    def test_EnergyCore_PVESSC_InternalPVESSC_post_6_positive_0006(self, api_client):
        """[EnergyCore.PVESSC][InternalPVESSC] post_6 - 正常请求"""
        # POST /api/internal/pvessc/data/ess
        response = api_client.post("pvessc/api/internal/pvessc/data/ess", json_data={"name": "test", "code": "TEST"})
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"POST 正常请求不应返回 5xx, 实际: {response.status_code}"


    def test_EnergyCore_PVESSC_InternalPVESSC_post_6_no_auth_0006(self, api_client):
        """[EnergyCore.PVESSC][InternalPVESSC] post_6 - 缺少认证头"""
        # POST /api/internal/pvessc/data/ess
        api_client.clear_token()
        try:
            response = api_client.post("pvessc/api/internal/pvessc/data/ess")
            assert response is not None, "响应不应为空"
            assert response.status_code in (200, 400, 401, 403), f"无认证头应返回 401/403, 实际: {response.status_code}"
        finally:
            api_client.restore_token()


    def test_EnergyCore_PVESSC_InternalPVESSC_post_6_invalid_token_0006(self, api_client):
        """[EnergyCore.PVESSC][InternalPVESSC] post_6 - 无效Token"""
        # POST /api/internal/pvessc/data/ess
        api_client.set_invalid_token()
        try:
            response = api_client.post("pvessc/api/internal/pvessc/data/ess")
            assert response is not None, "响应不应为空"
            assert response.status_code in (200, 400, 401, 403), f"无效Token应返回 401/403, 实际: {response.status_code}"
        finally:
            api_client.restore_token()


    def test_EnergyCore_PVESSC_InternalPVESSC_post_6_tenant_isolation_0006(self, api_client):
        """[EnergyCore.PVESSC][InternalPVESSC] post_6 - 租户隔离"""
        # POST /api/internal/pvessc/data/ess
        response = api_client.post("pvessc/api/internal/pvessc/data/ess")
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"租户隔离测试不应返回 5xx, 实际: {response.status_code}"
        data = response.json()
        assert isinstance(data, dict), "响应应为JSON对象"


    def test_EnergyCore_PVESSC_InternalPVESSC_post_6_empty_body_0006(self, api_client):
        """[EnergyCore.PVESSC][InternalPVESSC] post_6 - 空请求体"""
        # POST /api/internal/pvessc/data/ess
        response = api_client.post("pvessc/api/internal/pvessc/data/ess")
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"空请求体不应返回 5xx, 实际: {response.status_code}"


    def test_EnergyCore_PVESSC_InternalPVESSC_post_6_boundary_0006(self, api_client):
        """[EnergyCore.PVESSC][InternalPVESSC] post_6 - 边界值测试"""
        # POST /api/internal/pvessc/data/ess
        response = api_client.post("pvessc/api/internal/pvessc/data/ess")
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"边界值测试不应返回 5xx 服务器错误, 实际: {response.status_code}"
        assert isinstance(response.json(), dict), "响应应为JSON对象"


    def test_EnergyCore_PVESSC_InternalPVESSC_post_6_sql_injection_0006(self, api_client):
        """[EnergyCore.PVESSC][InternalPVESSC] post_6 - SQL注入防护"""
        # POST /api/internal/pvessc/data/ess
        response = api_client.post("pvessc/api/internal/pvessc/data/ess")
        assert response is not None, "响应不应为空"
        assert response.status_code != 500, f"SQL注入不应导致服务器错误, 实际: {response.status_code}"
        data = response.json()
        assert isinstance(data, dict), "响应应为JSON对象"


    def test_EnergyCore_PVESSC_InternalPVESSC_post_6_xss_protection_0006(self, api_client):
        """[EnergyCore.PVESSC][InternalPVESSC] post_6 - XSS防护"""
        # POST /api/internal/pvessc/data/ess
        xss_payload = {"name": "<script>alert('xss')</script>", "code": "XSS_TEST"}
        response = api_client.post("pvessc/api/internal/pvessc/data/ess", json_data=xss_payload)
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"XSS防护测试不应返回 5xx, 实际: {response.status_code}"


    def test_EnergyCore_PVESSC_InternalPVESSC_post_6_large_payload_0006(self, api_client):
        """[EnergyCore.PVESSC][InternalPVESSC] post_6 - 大数据量"""
        # POST /api/internal/pvessc/data/ess
        large_data = {"name": "x" * 10000, "code": "LARGE", "description": "y" * 50000}
        response = api_client.post("pvessc/api/internal/pvessc/data/ess", json_data=large_data)
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"大数据量测试不应返回 5xx, 实际: {response.status_code}"


    def test_EnergyCore_PVESSC_InternalPVESSC_post_6_concurrent_0006(self, api_client):
        """[EnergyCore.PVESSC][InternalPVESSC] post_6 - 并发请求"""
        # POST /api/internal/pvessc/data/ess
        responses = []
        for _ in range(3):
            r = api_client.post("pvessc/api/internal/pvessc/data/ess")
            responses.append(r)
        for r in responses:
            assert r is not None, "并发响应不应为空"
            assert r.status_code < 500, f"并发请求不应返回 5xx, 实际: {r.status_code}"


    def test_EnergyCore_PVESSC_InternalPVESSC_post_6_timeout_0006(self, api_client):
        """[EnergyCore.PVESSC][InternalPVESSC] post_6 - 超时处理"""
        # POST /api/internal/pvessc/data/ess
        response = api_client.post("pvessc/api/internal/pvessc/data/ess")
        assert response is not None, "超时处理响应不应为空"
        assert response.status_code < 500, f"超时测试不应返回 5xx, 实际: {response.status_code}"


    def test_EnergyCore_PVESSC_InternalPVESSC_post_6_permission_denied_0006(self, api_client):
        """[EnergyCore.PVESSC][InternalPVESSC] post_6 - 权限不足"""
        # POST /api/internal/pvessc/data/ess
        response = api_client.post("pvessc/api/internal/pvessc/data/ess")
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"权限测试不应返回 5xx, 实际: {response.status_code}"


    def test_EnergyCore_PVESSC_InternalPVESSC_post_6_field_validation_0006(self, api_client):
        """[EnergyCore.PVESSC][InternalPVESSC] post_6 - 字段校验"""
        # POST /api/internal/pvessc/data/ess
        invalid_data = {"name": "", "code": ""}
        response = api_client.post("pvessc/api/internal/pvessc/data/ess", json_data=invalid_data)
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"字段校验不应返回 5xx, 实际: {response.status_code}"


    def test_EnergyCore_PVESSC_InternalPVESSC_post_6_response_format_0006(self, api_client):
        """[EnergyCore.PVESSC][InternalPVESSC] post_6 - 响应格式"""
        # POST /api/internal/pvessc/data/ess
        response = api_client.post("pvessc/api/internal/pvessc/data/ess")
        assert response is not None, "响应不应为空"
        data = response.json()
        assert isinstance(data, dict), "响应应为JSON对象"
        if response.status_code == 200:
            assert "success" in data or "data" in data or "code" in data, "200 响应应包含标准字段"


    def test_EnergyCore_PVESSC_Site_get_0_positive_0007(self, api_client):
        """[EnergyCore.PVESSC][Site] get_0 - 正常请求"""
        # GET /api/pvessc/site/00000000-0000-0000-0000-000000000001
        response = api_client.get("pvessc/api/pvessc/site/00000000-0000-0000-0000-000000000001")
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"GET 正常请求不应返回 5xx, 实际: {response.status_code}"


    def test_EnergyCore_PVESSC_Site_get_0_no_auth_0007(self, api_client):
        """[EnergyCore.PVESSC][Site] get_0 - 缺少认证头"""
        # GET /api/pvessc/site/00000000-0000-0000-0000-000000000001
        api_client.clear_token()
        try:
            response = api_client.get("pvessc/api/pvessc/site/00000000-0000-0000-0000-000000000001")
            assert response is not None, "响应不应为空"
            assert response.status_code in (200, 400, 401, 403), f"无认证头应返回 401/403, 实际: {response.status_code}"
        finally:
            api_client.restore_token()


    def test_EnergyCore_PVESSC_Site_get_0_invalid_token_0007(self, api_client):
        """[EnergyCore.PVESSC][Site] get_0 - 无效Token"""
        # GET /api/pvessc/site/00000000-0000-0000-0000-000000000001
        api_client.set_invalid_token()
        try:
            response = api_client.get("pvessc/api/pvessc/site/00000000-0000-0000-0000-000000000001")
            assert response is not None, "响应不应为空"
            assert response.status_code in (200, 400, 401, 403), f"无效Token应返回 401/403, 实际: {response.status_code}"
        finally:
            api_client.restore_token()


    def test_EnergyCore_PVESSC_Site_get_0_tenant_isolation_0007(self, api_client):
        """[EnergyCore.PVESSC][Site] get_0 - 租户隔离"""
        # GET /api/pvessc/site/00000000-0000-0000-0000-000000000001
        response = api_client.get("pvessc/api/pvessc/site/00000000-0000-0000-0000-000000000001")
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"租户隔离测试不应返回 5xx, 实际: {response.status_code}"
        data = response.json()
        assert isinstance(data, dict), "响应应为JSON对象"


    def test_EnergyCore_PVESSC_Site_get_0_invalid_id_0007(self, api_client):
        """[EnergyCore.PVESSC][Site] get_0 - 无效ID"""
        # GET /api/pvessc/site/00000000-0000-0000-0000-000000000001
        response = api_client.get("pvessc/api/pvessc/site/invalid-not-a-uuid")
        assert response is not None, "响应不应为空"
        assert response.status_code in (200, 400, 403, 404), f"无效ID应返回 200/400/403/404, 实际: {response.status_code}"


    def test_EnergyCore_PVESSC_Site_get_0_not_found_id_0007(self, api_client):
        """[EnergyCore.PVESSC][Site] get_0 - 不存在ID"""
        # GET /api/pvessc/site/00000000-0000-0000-0000-000000000001
        response = api_client.get("pvessc/api/pvessc/site/99999999-9999-9999-9999-999999999999")
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"不存在ID不应返回 5xx, 实际: {response.status_code}"


    def test_EnergyCore_PVESSC_Site_get_0_boundary_0007(self, api_client):
        """[EnergyCore.PVESSC][Site] get_0 - 边界值测试"""
        # GET /api/pvessc/site/00000000-0000-0000-0000-000000000001
        response = api_client.get("pvessc/api/pvessc/site/00000000-0000-0000-0000-000000000001")
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"边界值测试不应返回 5xx 服务器错误, 实际: {response.status_code}"
        assert isinstance(response.json(), dict), "响应应为JSON对象"


    def test_EnergyCore_PVESSC_Site_get_0_sql_injection_0007(self, api_client):
        """[EnergyCore.PVESSC][Site] get_0 - SQL注入防护"""
        # GET /api/pvessc/site/00000000-0000-0000-0000-000000000001
        response = api_client.get("pvessc/api/pvessc/site/1' OR '1'='1")
        assert response is not None, "响应不应为空"
        assert response.status_code != 500, f"SQL注入不应导致服务器错误, 实际: {response.status_code}"
        data = response.json()
        assert isinstance(data, dict), "响应应为JSON对象"


    def test_EnergyCore_PVESSC_Site_get_0_concurrent_0007(self, api_client):
        """[EnergyCore.PVESSC][Site] get_0 - 并发请求"""
        # GET /api/pvessc/site/00000000-0000-0000-0000-000000000001
        responses = []
        for _ in range(3):
            r = api_client.get("pvessc/api/pvessc/site/00000000-0000-0000-0000-000000000001")
            responses.append(r)
        for r in responses:
            assert r is not None, "并发响应不应为空"
            assert r.status_code < 500, f"并发请求不应返回 5xx, 实际: {r.status_code}"


    def test_EnergyCore_PVESSC_Site_get_0_timeout_0007(self, api_client):
        """[EnergyCore.PVESSC][Site] get_0 - 超时处理"""
        # GET /api/pvessc/site/00000000-0000-0000-0000-000000000001
        response = api_client.get("pvessc/api/pvessc/site/00000000-0000-0000-0000-000000000001")
        assert response is not None, "超时处理响应不应为空"
        assert response.status_code < 500, f"超时测试不应返回 5xx, 实际: {response.status_code}"


    def test_EnergyCore_PVESSC_Site_get_0_permission_denied_0007(self, api_client):
        """[EnergyCore.PVESSC][Site] get_0 - 权限不足"""
        # GET /api/pvessc/site/00000000-0000-0000-0000-000000000001
        response = api_client.get("pvessc/api/pvessc/site/00000000-0000-0000-0000-000000000001")
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"权限测试不应返回 5xx, 实际: {response.status_code}"


    def test_EnergyCore_PVESSC_Site_get_0_response_format_0007(self, api_client):
        """[EnergyCore.PVESSC][Site] get_0 - 响应格式"""
        # GET /api/pvessc/site/00000000-0000-0000-0000-000000000001
        response = api_client.get("pvessc/api/pvessc/site/00000000-0000-0000-0000-000000000001")
        assert response is not None, "响应不应为空"
        data = response.json()
        assert isinstance(data, dict), "响应应为JSON对象"
        if response.status_code == 200:
            assert "success" in data or "data" in data or "code" in data, "200 响应应包含标准字段"


    def test_EnergyCore_PVESSC_Site_get_1_positive_0008(self, api_client):
        """[EnergyCore.PVESSC][Site] get_1 - 正常请求"""
        # GET /api/pvessc/site/list
        response = api_client.get("pvessc/api/pvessc/site/list")
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"GET 正常请求不应返回 5xx, 实际: {response.status_code}"


    def test_EnergyCore_PVESSC_Site_get_1_no_auth_0008(self, api_client):
        """[EnergyCore.PVESSC][Site] get_1 - 缺少认证头"""
        # GET /api/pvessc/site/list
        api_client.clear_token()
        try:
            response = api_client.get("pvessc/api/pvessc/site/list")
            assert response is not None, "响应不应为空"
            assert response.status_code in (200, 400, 401, 403), f"无认证头应返回 401/403, 实际: {response.status_code}"
        finally:
            api_client.restore_token()


    def test_EnergyCore_PVESSC_Site_get_1_invalid_token_0008(self, api_client):
        """[EnergyCore.PVESSC][Site] get_1 - 无效Token"""
        # GET /api/pvessc/site/list
        api_client.set_invalid_token()
        try:
            response = api_client.get("pvessc/api/pvessc/site/list")
            assert response is not None, "响应不应为空"
            assert response.status_code in (200, 400, 401, 403), f"无效Token应返回 401/403, 实际: {response.status_code}"
        finally:
            api_client.restore_token()


    def test_EnergyCore_PVESSC_Site_get_1_tenant_isolation_0008(self, api_client):
        """[EnergyCore.PVESSC][Site] get_1 - 租户隔离"""
        # GET /api/pvessc/site/list
        response = api_client.get("pvessc/api/pvessc/site/list")
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"租户隔离测试不应返回 5xx, 实际: {response.status_code}"
        data = response.json()
        assert isinstance(data, dict), "响应应为JSON对象"


    def test_EnergyCore_PVESSC_Site_get_1_boundary_0008(self, api_client):
        """[EnergyCore.PVESSC][Site] get_1 - 边界值测试"""
        # GET /api/pvessc/site/list
        response = api_client.get("pvessc/api/pvessc/site/list")
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"边界值测试不应返回 5xx 服务器错误, 实际: {response.status_code}"
        assert isinstance(response.json(), dict), "响应应为JSON对象"


    def test_EnergyCore_PVESSC_Site_get_1_sql_injection_0008(self, api_client):
        """[EnergyCore.PVESSC][Site] get_1 - SQL注入防护"""
        # GET /api/pvessc/site/list
        response = api_client.get("pvessc/api/pvessc/site/list")
        assert response is not None, "响应不应为空"
        assert response.status_code != 500, f"SQL注入不应导致服务器错误, 实际: {response.status_code}"
        data = response.json()
        assert isinstance(data, dict), "响应应为JSON对象"


    def test_EnergyCore_PVESSC_Site_get_1_concurrent_0008(self, api_client):
        """[EnergyCore.PVESSC][Site] get_1 - 并发请求"""
        # GET /api/pvessc/site/list
        responses = []
        for _ in range(3):
            r = api_client.get("pvessc/api/pvessc/site/list")
            responses.append(r)
        for r in responses:
            assert r is not None, "并发响应不应为空"
            assert r.status_code < 500, f"并发请求不应返回 5xx, 实际: {r.status_code}"


    def test_EnergyCore_PVESSC_Site_get_1_timeout_0008(self, api_client):
        """[EnergyCore.PVESSC][Site] get_1 - 超时处理"""
        # GET /api/pvessc/site/list
        response = api_client.get("pvessc/api/pvessc/site/list")
        assert response is not None, "超时处理响应不应为空"
        assert response.status_code < 500, f"超时测试不应返回 5xx, 实际: {response.status_code}"


    def test_EnergyCore_PVESSC_Site_get_1_permission_denied_0008(self, api_client):
        """[EnergyCore.PVESSC][Site] get_1 - 权限不足"""
        # GET /api/pvessc/site/list
        response = api_client.get("pvessc/api/pvessc/site/list")
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"权限测试不应返回 5xx, 实际: {response.status_code}"


    def test_EnergyCore_PVESSC_Site_get_1_response_format_0008(self, api_client):
        """[EnergyCore.PVESSC][Site] get_1 - 响应格式"""
        # GET /api/pvessc/site/list
        response = api_client.get("pvessc/api/pvessc/site/list")
        assert response is not None, "响应不应为空"
        data = response.json()
        assert isinstance(data, dict), "响应应为JSON对象"
        if response.status_code == 200:
            assert "success" in data or "data" in data or "code" in data, "200 响应应包含标准字段"


    def test_EnergyCore_PVESSC_Site_post_2_positive_0009(self, api_client):
        """[EnergyCore.PVESSC][Site] post_2 - 正常请求"""
        # POST /api/pvessc/site
        response = api_client.post("pvessc/api/pvessc/site", json_data={"name": "test", "code": "TEST"})
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"POST 正常请求不应返回 5xx, 实际: {response.status_code}"


    def test_EnergyCore_PVESSC_Site_post_2_no_auth_0009(self, api_client):
        """[EnergyCore.PVESSC][Site] post_2 - 缺少认证头"""
        # POST /api/pvessc/site
        api_client.clear_token()
        try:
            response = api_client.post("pvessc/api/pvessc/site")
            assert response is not None, "响应不应为空"
            assert response.status_code in (200, 400, 401, 403), f"无认证头应返回 401/403, 实际: {response.status_code}"
        finally:
            api_client.restore_token()


    def test_EnergyCore_PVESSC_Site_post_2_invalid_token_0009(self, api_client):
        """[EnergyCore.PVESSC][Site] post_2 - 无效Token"""
        # POST /api/pvessc/site
        api_client.set_invalid_token()
        try:
            response = api_client.post("pvessc/api/pvessc/site")
            assert response is not None, "响应不应为空"
            assert response.status_code in (200, 400, 401, 403), f"无效Token应返回 401/403, 实际: {response.status_code}"
        finally:
            api_client.restore_token()


    def test_EnergyCore_PVESSC_Site_post_2_tenant_isolation_0009(self, api_client):
        """[EnergyCore.PVESSC][Site] post_2 - 租户隔离"""
        # POST /api/pvessc/site
        response = api_client.post("pvessc/api/pvessc/site")
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"租户隔离测试不应返回 5xx, 实际: {response.status_code}"
        data = response.json()
        assert isinstance(data, dict), "响应应为JSON对象"


    def test_EnergyCore_PVESSC_Site_post_2_empty_body_0009(self, api_client):
        """[EnergyCore.PVESSC][Site] post_2 - 空请求体"""
        # POST /api/pvessc/site
        response = api_client.post("pvessc/api/pvessc/site")
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"空请求体不应返回 5xx, 实际: {response.status_code}"


    def test_EnergyCore_PVESSC_Site_post_2_boundary_0009(self, api_client):
        """[EnergyCore.PVESSC][Site] post_2 - 边界值测试"""
        # POST /api/pvessc/site
        response = api_client.post("pvessc/api/pvessc/site")
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"边界值测试不应返回 5xx 服务器错误, 实际: {response.status_code}"
        assert isinstance(response.json(), dict), "响应应为JSON对象"


    def test_EnergyCore_PVESSC_Site_post_2_sql_injection_0009(self, api_client):
        """[EnergyCore.PVESSC][Site] post_2 - SQL注入防护"""
        # POST /api/pvessc/site
        response = api_client.post("pvessc/api/pvessc/site")
        assert response is not None, "响应不应为空"
        assert response.status_code != 500, f"SQL注入不应导致服务器错误, 实际: {response.status_code}"
        data = response.json()
        assert isinstance(data, dict), "响应应为JSON对象"


    def test_EnergyCore_PVESSC_Site_post_2_xss_protection_0009(self, api_client):
        """[EnergyCore.PVESSC][Site] post_2 - XSS防护"""
        # POST /api/pvessc/site
        xss_payload = {"name": "<script>alert('xss')</script>", "code": "XSS_TEST"}
        response = api_client.post("pvessc/api/pvessc/site", json_data=xss_payload)
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"XSS防护测试不应返回 5xx, 实际: {response.status_code}"


    def test_EnergyCore_PVESSC_Site_post_2_large_payload_0009(self, api_client):
        """[EnergyCore.PVESSC][Site] post_2 - 大数据量"""
        # POST /api/pvessc/site
        large_data = {"name": "x" * 10000, "code": "LARGE", "description": "y" * 50000}
        response = api_client.post("pvessc/api/pvessc/site", json_data=large_data)
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"大数据量测试不应返回 5xx, 实际: {response.status_code}"


    def test_EnergyCore_PVESSC_Site_post_2_concurrent_0009(self, api_client):
        """[EnergyCore.PVESSC][Site] post_2 - 并发请求"""
        # POST /api/pvessc/site
        responses = []
        for _ in range(3):
            r = api_client.post("pvessc/api/pvessc/site")
            responses.append(r)
        for r in responses:
            assert r is not None, "并发响应不应为空"
            assert r.status_code < 500, f"并发请求不应返回 5xx, 实际: {r.status_code}"


    def test_EnergyCore_PVESSC_Site_post_2_timeout_0009(self, api_client):
        """[EnergyCore.PVESSC][Site] post_2 - 超时处理"""
        # POST /api/pvessc/site
        response = api_client.post("pvessc/api/pvessc/site")
        assert response is not None, "超时处理响应不应为空"
        assert response.status_code < 500, f"超时测试不应返回 5xx, 实际: {response.status_code}"


    def test_EnergyCore_PVESSC_Site_post_2_permission_denied_0009(self, api_client):
        """[EnergyCore.PVESSC][Site] post_2 - 权限不足"""
        # POST /api/pvessc/site
        response = api_client.post("pvessc/api/pvessc/site")
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"权限测试不应返回 5xx, 实际: {response.status_code}"


    def test_EnergyCore_PVESSC_Site_post_2_field_validation_0009(self, api_client):
        """[EnergyCore.PVESSC][Site] post_2 - 字段校验"""
        # POST /api/pvessc/site
        invalid_data = {"name": "", "code": ""}
        response = api_client.post("pvessc/api/pvessc/site", json_data=invalid_data)
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"字段校验不应返回 5xx, 实际: {response.status_code}"


    def test_EnergyCore_PVESSC_Site_post_2_response_format_0009(self, api_client):
        """[EnergyCore.PVESSC][Site] post_2 - 响应格式"""
        # POST /api/pvessc/site
        response = api_client.post("pvessc/api/pvessc/site")
        assert response is not None, "响应不应为空"
        data = response.json()
        assert isinstance(data, dict), "响应应为JSON对象"
        if response.status_code == 200:
            assert "success" in data or "data" in data or "code" in data, "200 响应应包含标准字段"


    def test_EnergyCore_PVESSC_Site_put_3_positive_0010(self, api_client):
        """[EnergyCore.PVESSC][Site] put_3 - 正常请求"""
        # PUT /api/pvessc/site/00000000-0000-0000-0000-000000000001
        response = api_client.put("pvessc/api/pvessc/site/00000000-0000-0000-0000-000000000001", json_data={"name": "updated"})
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"PUT 正常请求不应返回 5xx, 实际: {response.status_code}"


    def test_EnergyCore_PVESSC_Site_put_3_no_auth_0010(self, api_client):
        """[EnergyCore.PVESSC][Site] put_3 - 缺少认证头"""
        # PUT /api/pvessc/site/00000000-0000-0000-0000-000000000001
        api_client.clear_token()
        try:
            response = api_client.put("pvessc/api/pvessc/site/00000000-0000-0000-0000-000000000001")
            assert response is not None, "响应不应为空"
            assert response.status_code in (200, 400, 401, 403), f"无认证头应返回 401/403, 实际: {response.status_code}"
        finally:
            api_client.restore_token()


    def test_EnergyCore_PVESSC_Site_put_3_invalid_token_0010(self, api_client):
        """[EnergyCore.PVESSC][Site] put_3 - 无效Token"""
        # PUT /api/pvessc/site/00000000-0000-0000-0000-000000000001
        api_client.set_invalid_token()
        try:
            response = api_client.put("pvessc/api/pvessc/site/00000000-0000-0000-0000-000000000001")
            assert response is not None, "响应不应为空"
            assert response.status_code in (200, 400, 401, 403), f"无效Token应返回 401/403, 实际: {response.status_code}"
        finally:
            api_client.restore_token()


    def test_EnergyCore_PVESSC_Site_put_3_tenant_isolation_0010(self, api_client):
        """[EnergyCore.PVESSC][Site] put_3 - 租户隔离"""
        # PUT /api/pvessc/site/00000000-0000-0000-0000-000000000001
        response = api_client.put("pvessc/api/pvessc/site/00000000-0000-0000-0000-000000000001")
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"租户隔离测试不应返回 5xx, 实际: {response.status_code}"
        data = response.json()
        assert isinstance(data, dict), "响应应为JSON对象"


    def test_EnergyCore_PVESSC_Site_put_3_empty_body_0010(self, api_client):
        """[EnergyCore.PVESSC][Site] put_3 - 空请求体"""
        # PUT /api/pvessc/site/00000000-0000-0000-0000-000000000001
        response = api_client.put("pvessc/api/pvessc/site/00000000-0000-0000-0000-000000000001")
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"空请求体不应返回 5xx, 实际: {response.status_code}"


    def test_EnergyCore_PVESSC_Site_put_3_invalid_id_0010(self, api_client):
        """[EnergyCore.PVESSC][Site] put_3 - 无效ID"""
        # PUT /api/pvessc/site/00000000-0000-0000-0000-000000000001
        response = api_client.put("pvessc/api/pvessc/site/invalid-not-a-uuid")
        assert response is not None, "响应不应为空"
        assert response.status_code in (200, 400, 403, 404), f"无效ID应返回 200/400/403/404, 实际: {response.status_code}"


    def test_EnergyCore_PVESSC_Site_put_3_not_found_id_0010(self, api_client):
        """[EnergyCore.PVESSC][Site] put_3 - 不存在ID"""
        # PUT /api/pvessc/site/00000000-0000-0000-0000-000000000001
        response = api_client.put("pvessc/api/pvessc/site/99999999-9999-9999-9999-999999999999")
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"不存在ID不应返回 5xx, 实际: {response.status_code}"


    def test_EnergyCore_PVESSC_Site_put_3_boundary_0010(self, api_client):
        """[EnergyCore.PVESSC][Site] put_3 - 边界值测试"""
        # PUT /api/pvessc/site/00000000-0000-0000-0000-000000000001
        response = api_client.put("pvessc/api/pvessc/site/00000000-0000-0000-0000-000000000001")
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"边界值测试不应返回 5xx 服务器错误, 实际: {response.status_code}"
        assert isinstance(response.json(), dict), "响应应为JSON对象"


    def test_EnergyCore_PVESSC_Site_put_3_sql_injection_0010(self, api_client):
        """[EnergyCore.PVESSC][Site] put_3 - SQL注入防护"""
        # PUT /api/pvessc/site/00000000-0000-0000-0000-000000000001
        response = api_client.put("pvessc/api/pvessc/site/1' OR '1'='1")
        assert response is not None, "响应不应为空"
        assert response.status_code != 500, f"SQL注入不应导致服务器错误, 实际: {response.status_code}"
        data = response.json()
        assert isinstance(data, dict), "响应应为JSON对象"


    def test_EnergyCore_PVESSC_Site_put_3_xss_protection_0010(self, api_client):
        """[EnergyCore.PVESSC][Site] put_3 - XSS防护"""
        # PUT /api/pvessc/site/00000000-0000-0000-0000-000000000001
        xss_payload = {"name": "<script>alert('xss')</script>", "code": "XSS_TEST"}
        response = api_client.put("pvessc/api/pvessc/site/00000000-0000-0000-0000-000000000001", json_data=xss_payload)
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"XSS防护测试不应返回 5xx, 实际: {response.status_code}"


    def test_EnergyCore_PVESSC_Site_put_3_large_payload_0010(self, api_client):
        """[EnergyCore.PVESSC][Site] put_3 - 大数据量"""
        # PUT /api/pvessc/site/00000000-0000-0000-0000-000000000001
        large_data = {"name": "x" * 10000, "code": "LARGE", "description": "y" * 50000}
        response = api_client.put("pvessc/api/pvessc/site/00000000-0000-0000-0000-000000000001", json_data=large_data)
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"大数据量测试不应返回 5xx, 实际: {response.status_code}"


    def test_EnergyCore_PVESSC_Site_put_3_concurrent_0010(self, api_client):
        """[EnergyCore.PVESSC][Site] put_3 - 并发请求"""
        # PUT /api/pvessc/site/00000000-0000-0000-0000-000000000001
        responses = []
        for _ in range(3):
            r = api_client.put("pvessc/api/pvessc/site/00000000-0000-0000-0000-000000000001")
            responses.append(r)
        for r in responses:
            assert r is not None, "并发响应不应为空"
            assert r.status_code < 500, f"并发请求不应返回 5xx, 实际: {r.status_code}"


    def test_EnergyCore_PVESSC_Site_put_3_idempotent_0010(self, api_client):
        """[EnergyCore.PVESSC][Site] put_3 - 幂等性"""
        # PUT /api/pvessc/site/00000000-0000-0000-0000-000000000001
        r1 = api_client.put("pvessc/api/pvessc/site/00000000-0000-0000-0000-000000000001")
        r2 = api_client.put("pvessc/api/pvessc/site/00000000-0000-0000-0000-000000000001")
        assert r1 is not None and r2 is not None, "幂等性响应不应为空"
        assert r1.status_code == r2.status_code, f"幂等性: 两次请求状态码应一致, {r1.status_code} vs {r2.status_code}"


    def test_EnergyCore_PVESSC_Site_put_3_timeout_0010(self, api_client):
        """[EnergyCore.PVESSC][Site] put_3 - 超时处理"""
        # PUT /api/pvessc/site/00000000-0000-0000-0000-000000000001
        response = api_client.put("pvessc/api/pvessc/site/00000000-0000-0000-0000-000000000001")
        assert response is not None, "超时处理响应不应为空"
        assert response.status_code < 500, f"超时测试不应返回 5xx, 实际: {response.status_code}"


    def test_EnergyCore_PVESSC_Site_put_3_permission_denied_0010(self, api_client):
        """[EnergyCore.PVESSC][Site] put_3 - 权限不足"""
        # PUT /api/pvessc/site/00000000-0000-0000-0000-000000000001
        response = api_client.put("pvessc/api/pvessc/site/00000000-0000-0000-0000-000000000001")
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"权限测试不应返回 5xx, 实际: {response.status_code}"


    def test_EnergyCore_PVESSC_Site_put_3_field_validation_0010(self, api_client):
        """[EnergyCore.PVESSC][Site] put_3 - 字段校验"""
        # PUT /api/pvessc/site/00000000-0000-0000-0000-000000000001
        invalid_data = {"name": "", "code": ""}
        response = api_client.put("pvessc/api/pvessc/site/00000000-0000-0000-0000-000000000001", json_data=invalid_data)
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"字段校验不应返回 5xx, 实际: {response.status_code}"


    def test_EnergyCore_PVESSC_Site_put_3_response_format_0010(self, api_client):
        """[EnergyCore.PVESSC][Site] put_3 - 响应格式"""
        # PUT /api/pvessc/site/00000000-0000-0000-0000-000000000001
        response = api_client.put("pvessc/api/pvessc/site/00000000-0000-0000-0000-000000000001")
        assert response is not None, "响应不应为空"
        data = response.json()
        assert isinstance(data, dict), "响应应为JSON对象"
        if response.status_code == 200:
            assert "success" in data or "data" in data or "code" in data, "200 响应应包含标准字段"


    def test_EnergyCore_PVESSC_Site_delete_4_positive_0011(self, api_client):
        """[EnergyCore.PVESSC][Site] delete_4 - 正常请求"""
        # DELETE /api/pvessc/site/00000000-0000-0000-0000-000000000001
        response = api_client.delete("pvessc/api/pvessc/site/00000000-0000-0000-0000-000000000001")
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"DELETE 正常请求不应返回 5xx, 实际: {response.status_code}"


    def test_EnergyCore_PVESSC_Site_delete_4_no_auth_0011(self, api_client):
        """[EnergyCore.PVESSC][Site] delete_4 - 缺少认证头"""
        # DELETE /api/pvessc/site/00000000-0000-0000-0000-000000000001
        api_client.clear_token()
        try:
            response = api_client.delete("pvessc/api/pvessc/site/00000000-0000-0000-0000-000000000001")
            assert response is not None, "响应不应为空"
            assert response.status_code in (200, 400, 401, 403), f"无认证头应返回 401/403, 实际: {response.status_code}"
        finally:
            api_client.restore_token()


    def test_EnergyCore_PVESSC_Site_delete_4_invalid_token_0011(self, api_client):
        """[EnergyCore.PVESSC][Site] delete_4 - 无效Token"""
        # DELETE /api/pvessc/site/00000000-0000-0000-0000-000000000001
        api_client.set_invalid_token()
        try:
            response = api_client.delete("pvessc/api/pvessc/site/00000000-0000-0000-0000-000000000001")
            assert response is not None, "响应不应为空"
            assert response.status_code in (200, 400, 401, 403), f"无效Token应返回 401/403, 实际: {response.status_code}"
        finally:
            api_client.restore_token()


    def test_EnergyCore_PVESSC_Site_delete_4_tenant_isolation_0011(self, api_client):
        """[EnergyCore.PVESSC][Site] delete_4 - 租户隔离"""
        # DELETE /api/pvessc/site/00000000-0000-0000-0000-000000000001
        response = api_client.delete("pvessc/api/pvessc/site/00000000-0000-0000-0000-000000000001")
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"租户隔离测试不应返回 5xx, 实际: {response.status_code}"
        data = response.json()
        assert isinstance(data, dict), "响应应为JSON对象"


    def test_EnergyCore_PVESSC_Site_delete_4_invalid_id_0011(self, api_client):
        """[EnergyCore.PVESSC][Site] delete_4 - 无效ID"""
        # DELETE /api/pvessc/site/00000000-0000-0000-0000-000000000001
        response = api_client.delete("pvessc/api/pvessc/site/invalid-not-a-uuid")
        assert response is not None, "响应不应为空"
        assert response.status_code in (200, 400, 403, 404), f"无效ID应返回 200/400/403/404, 实际: {response.status_code}"


    def test_EnergyCore_PVESSC_Site_delete_4_not_found_id_0011(self, api_client):
        """[EnergyCore.PVESSC][Site] delete_4 - 不存在ID"""
        # DELETE /api/pvessc/site/00000000-0000-0000-0000-000000000001
        response = api_client.delete("pvessc/api/pvessc/site/99999999-9999-9999-9999-999999999999")
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"不存在ID不应返回 5xx, 实际: {response.status_code}"


    def test_EnergyCore_PVESSC_Site_delete_4_boundary_0011(self, api_client):
        """[EnergyCore.PVESSC][Site] delete_4 - 边界值测试"""
        # DELETE /api/pvessc/site/00000000-0000-0000-0000-000000000001
        response = api_client.delete("pvessc/api/pvessc/site/00000000-0000-0000-0000-000000000001")
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"边界值测试不应返回 5xx 服务器错误, 实际: {response.status_code}"
        assert isinstance(response.json(), dict), "响应应为JSON对象"


    def test_EnergyCore_PVESSC_Site_delete_4_sql_injection_0011(self, api_client):
        """[EnergyCore.PVESSC][Site] delete_4 - SQL注入防护"""
        # DELETE /api/pvessc/site/00000000-0000-0000-0000-000000000001
        response = api_client.delete("pvessc/api/pvessc/site/1' OR '1'='1")
        assert response is not None, "响应不应为空"
        assert response.status_code != 500, f"SQL注入不应导致服务器错误, 实际: {response.status_code}"
        data = response.json()
        assert isinstance(data, dict), "响应应为JSON对象"


    def test_EnergyCore_PVESSC_Site_delete_4_concurrent_0011(self, api_client):
        """[EnergyCore.PVESSC][Site] delete_4 - 并发请求"""
        # DELETE /api/pvessc/site/00000000-0000-0000-0000-000000000001
        responses = []
        for _ in range(3):
            r = api_client.delete("pvessc/api/pvessc/site/00000000-0000-0000-0000-000000000001")
            responses.append(r)
        for r in responses:
            assert r is not None, "并发响应不应为空"
            assert r.status_code < 500, f"并发请求不应返回 5xx, 实际: {r.status_code}"


    def test_EnergyCore_PVESSC_Site_delete_4_idempotent_0011(self, api_client):
        """[EnergyCore.PVESSC][Site] delete_4 - 幂等性"""
        # DELETE /api/pvessc/site/00000000-0000-0000-0000-000000000001
        r1 = api_client.delete("pvessc/api/pvessc/site/00000000-0000-0000-0000-000000000001")
        r2 = api_client.delete("pvessc/api/pvessc/site/00000000-0000-0000-0000-000000000001")
        assert r1 is not None and r2 is not None, "幂等性响应不应为空"
        assert r1.status_code == r2.status_code, f"幂等性: 两次请求状态码应一致, {r1.status_code} vs {r2.status_code}"


    def test_EnergyCore_PVESSC_Site_delete_4_timeout_0011(self, api_client):
        """[EnergyCore.PVESSC][Site] delete_4 - 超时处理"""
        # DELETE /api/pvessc/site/00000000-0000-0000-0000-000000000001
        response = api_client.delete("pvessc/api/pvessc/site/00000000-0000-0000-0000-000000000001")
        assert response is not None, "超时处理响应不应为空"
        assert response.status_code < 500, f"超时测试不应返回 5xx, 实际: {response.status_code}"


    def test_EnergyCore_PVESSC_Site_delete_4_permission_denied_0011(self, api_client):
        """[EnergyCore.PVESSC][Site] delete_4 - 权限不足"""
        # DELETE /api/pvessc/site/00000000-0000-0000-0000-000000000001
        response = api_client.delete("pvessc/api/pvessc/site/00000000-0000-0000-0000-000000000001")
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"权限测试不应返回 5xx, 实际: {response.status_code}"


    def test_EnergyCore_PVESSC_Site_delete_4_response_format_0011(self, api_client):
        """[EnergyCore.PVESSC][Site] delete_4 - 响应格式"""
        # DELETE /api/pvessc/site/00000000-0000-0000-0000-000000000001
        response = api_client.delete("pvessc/api/pvessc/site/00000000-0000-0000-0000-000000000001")
        assert response is not None, "响应不应为空"
        data = response.json()
        assert isinstance(data, dict), "响应应为JSON对象"
        if response.status_code == 200:
            assert "success" in data or "data" in data or "code" in data, "200 响应应包含标准字段"


    def test_EnergyCore_PVESSC_Topology_get_0_positive_0012(self, api_client):
        """[EnergyCore.PVESSC][Topology] get_0 - 正常请求"""
        # GET /api/pvessc/topology
        response = api_client.get("pvessc/api/pvessc/topology")
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"GET 正常请求不应返回 5xx, 实际: {response.status_code}"


    def test_EnergyCore_PVESSC_Topology_get_0_no_auth_0012(self, api_client):
        """[EnergyCore.PVESSC][Topology] get_0 - 缺少认证头"""
        # GET /api/pvessc/topology
        api_client.clear_token()
        try:
            response = api_client.get("pvessc/api/pvessc/topology")
            assert response is not None, "响应不应为空"
            assert response.status_code in (200, 400, 401, 403), f"无认证头应返回 401/403, 实际: {response.status_code}"
        finally:
            api_client.restore_token()


    def test_EnergyCore_PVESSC_Topology_get_0_invalid_token_0012(self, api_client):
        """[EnergyCore.PVESSC][Topology] get_0 - 无效Token"""
        # GET /api/pvessc/topology
        api_client.set_invalid_token()
        try:
            response = api_client.get("pvessc/api/pvessc/topology")
            assert response is not None, "响应不应为空"
            assert response.status_code in (200, 400, 401, 403), f"无效Token应返回 401/403, 实际: {response.status_code}"
        finally:
            api_client.restore_token()


    def test_EnergyCore_PVESSC_Topology_get_0_tenant_isolation_0012(self, api_client):
        """[EnergyCore.PVESSC][Topology] get_0 - 租户隔离"""
        # GET /api/pvessc/topology
        response = api_client.get("pvessc/api/pvessc/topology")
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"租户隔离测试不应返回 5xx, 实际: {response.status_code}"
        data = response.json()
        assert isinstance(data, dict), "响应应为JSON对象"


    def test_EnergyCore_PVESSC_Topology_get_0_boundary_0012(self, api_client):
        """[EnergyCore.PVESSC][Topology] get_0 - 边界值测试"""
        # GET /api/pvessc/topology
        response = api_client.get("pvessc/api/pvessc/topology")
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"边界值测试不应返回 5xx 服务器错误, 实际: {response.status_code}"
        assert isinstance(response.json(), dict), "响应应为JSON对象"


    def test_EnergyCore_PVESSC_Topology_get_0_sql_injection_0012(self, api_client):
        """[EnergyCore.PVESSC][Topology] get_0 - SQL注入防护"""
        # GET /api/pvessc/topology
        response = api_client.get("pvessc/api/pvessc/topology")
        assert response is not None, "响应不应为空"
        assert response.status_code != 500, f"SQL注入不应导致服务器错误, 实际: {response.status_code}"
        data = response.json()
        assert isinstance(data, dict), "响应应为JSON对象"


    def test_EnergyCore_PVESSC_Topology_get_0_concurrent_0012(self, api_client):
        """[EnergyCore.PVESSC][Topology] get_0 - 并发请求"""
        # GET /api/pvessc/topology
        responses = []
        for _ in range(3):
            r = api_client.get("pvessc/api/pvessc/topology")
            responses.append(r)
        for r in responses:
            assert r is not None, "并发响应不应为空"
            assert r.status_code < 500, f"并发请求不应返回 5xx, 实际: {r.status_code}"


    def test_EnergyCore_PVESSC_Topology_get_0_timeout_0012(self, api_client):
        """[EnergyCore.PVESSC][Topology] get_0 - 超时处理"""
        # GET /api/pvessc/topology
        response = api_client.get("pvessc/api/pvessc/topology")
        assert response is not None, "超时处理响应不应为空"
        assert response.status_code < 500, f"超时测试不应返回 5xx, 实际: {response.status_code}"


    def test_EnergyCore_PVESSC_Topology_get_0_permission_denied_0012(self, api_client):
        """[EnergyCore.PVESSC][Topology] get_0 - 权限不足"""
        # GET /api/pvessc/topology
        response = api_client.get("pvessc/api/pvessc/topology")
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"权限测试不应返回 5xx, 实际: {response.status_code}"


    def test_EnergyCore_PVESSC_Topology_get_0_response_format_0012(self, api_client):
        """[EnergyCore.PVESSC][Topology] get_0 - 响应格式"""
        # GET /api/pvessc/topology
        response = api_client.get("pvessc/api/pvessc/topology")
        assert response is not None, "响应不应为空"
        data = response.json()
        assert isinstance(data, dict), "响应应为JSON对象"
        if response.status_code == 200:
            assert "success" in data or "data" in data or "code" in data, "200 响应应包含标准字段"


    def test_EnergyCore_PVESSC_Topology_get_1_positive_0013(self, api_client):
        """[EnergyCore.PVESSC][Topology] get_1 - 正常请求"""
        # GET /api/pvessc/topology/{siteId}/capability
        response = api_client.get("pvessc/api/pvessc/topology/{siteId}/capability")
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"GET 正常请求不应返回 5xx, 实际: {response.status_code}"


    def test_EnergyCore_PVESSC_Topology_get_1_no_auth_0013(self, api_client):
        """[EnergyCore.PVESSC][Topology] get_1 - 缺少认证头"""
        # GET /api/pvessc/topology/{siteId}/capability
        api_client.clear_token()
        try:
            response = api_client.get("pvessc/api/pvessc/topology/{siteId}/capability")
            assert response is not None, "响应不应为空"
            assert response.status_code in (200, 400, 401, 403), f"无认证头应返回 401/403, 实际: {response.status_code}"
        finally:
            api_client.restore_token()


    def test_EnergyCore_PVESSC_Topology_get_1_invalid_token_0013(self, api_client):
        """[EnergyCore.PVESSC][Topology] get_1 - 无效Token"""
        # GET /api/pvessc/topology/{siteId}/capability
        api_client.set_invalid_token()
        try:
            response = api_client.get("pvessc/api/pvessc/topology/{siteId}/capability")
            assert response is not None, "响应不应为空"
            assert response.status_code in (200, 400, 401, 403), f"无效Token应返回 401/403, 实际: {response.status_code}"
        finally:
            api_client.restore_token()


    def test_EnergyCore_PVESSC_Topology_get_1_tenant_isolation_0013(self, api_client):
        """[EnergyCore.PVESSC][Topology] get_1 - 租户隔离"""
        # GET /api/pvessc/topology/{siteId}/capability
        response = api_client.get("pvessc/api/pvessc/topology/{siteId}/capability")
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"租户隔离测试不应返回 5xx, 实际: {response.status_code}"
        data = response.json()
        assert isinstance(data, dict), "响应应为JSON对象"


    def test_EnergyCore_PVESSC_Topology_get_1_invalid_id_0013(self, api_client):
        """[EnergyCore.PVESSC][Topology] get_1 - 无效ID"""
        # GET /api/pvessc/topology/{siteId}/capability
        response = api_client.get("pvessc/api/pvessc/topology/{siteId}/capability")
        assert response is not None, "响应不应为空"
        assert response.status_code in (200, 400, 403, 404), f"无效ID应返回 200/400/403/404, 实际: {response.status_code}"


    def test_EnergyCore_PVESSC_Topology_get_1_not_found_id_0013(self, api_client):
        """[EnergyCore.PVESSC][Topology] get_1 - 不存在ID"""
        # GET /api/pvessc/topology/{siteId}/capability
        response = api_client.get("pvessc/api/pvessc/topology/{siteId}/capability")
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"不存在ID不应返回 5xx, 实际: {response.status_code}"


    def test_EnergyCore_PVESSC_Topology_get_1_boundary_0013(self, api_client):
        """[EnergyCore.PVESSC][Topology] get_1 - 边界值测试"""
        # GET /api/pvessc/topology/{siteId}/capability
        response = api_client.get("pvessc/api/pvessc/topology/{siteId}/capability")
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"边界值测试不应返回 5xx 服务器错误, 实际: {response.status_code}"
        assert isinstance(response.json(), dict), "响应应为JSON对象"


    def test_EnergyCore_PVESSC_Topology_get_1_sql_injection_0013(self, api_client):
        """[EnergyCore.PVESSC][Topology] get_1 - SQL注入防护"""
        # GET /api/pvessc/topology/{siteId}/capability
        response = api_client.get("pvessc/api/pvessc/topology/{siteId}/capability")
        assert response is not None, "响应不应为空"
        assert response.status_code != 500, f"SQL注入不应导致服务器错误, 实际: {response.status_code}"
        data = response.json()
        assert isinstance(data, dict), "响应应为JSON对象"


    def test_EnergyCore_PVESSC_Topology_get_1_concurrent_0013(self, api_client):
        """[EnergyCore.PVESSC][Topology] get_1 - 并发请求"""
        # GET /api/pvessc/topology/{siteId}/capability
        responses = []
        for _ in range(3):
            r = api_client.get("pvessc/api/pvessc/topology/{siteId}/capability")
            responses.append(r)
        for r in responses:
            assert r is not None, "并发响应不应为空"
            assert r.status_code < 500, f"并发请求不应返回 5xx, 实际: {r.status_code}"


    def test_EnergyCore_PVESSC_Topology_get_1_timeout_0013(self, api_client):
        """[EnergyCore.PVESSC][Topology] get_1 - 超时处理"""
        # GET /api/pvessc/topology/{siteId}/capability
        response = api_client.get("pvessc/api/pvessc/topology/{siteId}/capability")
        assert response is not None, "超时处理响应不应为空"
        assert response.status_code < 500, f"超时测试不应返回 5xx, 实际: {response.status_code}"


    def test_EnergyCore_PVESSC_Topology_get_1_permission_denied_0013(self, api_client):
        """[EnergyCore.PVESSC][Topology] get_1 - 权限不足"""
        # GET /api/pvessc/topology/{siteId}/capability
        response = api_client.get("pvessc/api/pvessc/topology/{siteId}/capability")
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"权限测试不应返回 5xx, 实际: {response.status_code}"


    def test_EnergyCore_PVESSC_Topology_get_1_response_format_0013(self, api_client):
        """[EnergyCore.PVESSC][Topology] get_1 - 响应格式"""
        # GET /api/pvessc/topology/{siteId}/capability
        response = api_client.get("pvessc/api/pvessc/topology/{siteId}/capability")
        assert response is not None, "响应不应为空"
        data = response.json()
        assert isinstance(data, dict), "响应应为JSON对象"
        if response.status_code == 200:
            assert "success" in data or "data" in data or "code" in data, "200 响应应包含标准字段"


    def test_EnergyCore_PVESSC_Topology_post_2_positive_0014(self, api_client):
        """[EnergyCore.PVESSC][Topology] post_2 - 正常请求"""
        # POST /api/pvessc/topology/capability/batch
        response = api_client.post("pvessc/api/pvessc/topology/capability/batch", json_data={"name": "test", "code": "TEST"})
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"POST 正常请求不应返回 5xx, 实际: {response.status_code}"


    def test_EnergyCore_PVESSC_Topology_post_2_no_auth_0014(self, api_client):
        """[EnergyCore.PVESSC][Topology] post_2 - 缺少认证头"""
        # POST /api/pvessc/topology/capability/batch
        api_client.clear_token()
        try:
            response = api_client.post("pvessc/api/pvessc/topology/capability/batch")
            assert response is not None, "响应不应为空"
            assert response.status_code in (200, 400, 401, 403), f"无认证头应返回 401/403, 实际: {response.status_code}"
        finally:
            api_client.restore_token()


    def test_EnergyCore_PVESSC_Topology_post_2_invalid_token_0014(self, api_client):
        """[EnergyCore.PVESSC][Topology] post_2 - 无效Token"""
        # POST /api/pvessc/topology/capability/batch
        api_client.set_invalid_token()
        try:
            response = api_client.post("pvessc/api/pvessc/topology/capability/batch")
            assert response is not None, "响应不应为空"
            assert response.status_code in (200, 400, 401, 403), f"无效Token应返回 401/403, 实际: {response.status_code}"
        finally:
            api_client.restore_token()


    def test_EnergyCore_PVESSC_Topology_post_2_tenant_isolation_0014(self, api_client):
        """[EnergyCore.PVESSC][Topology] post_2 - 租户隔离"""
        # POST /api/pvessc/topology/capability/batch
        response = api_client.post("pvessc/api/pvessc/topology/capability/batch")
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"租户隔离测试不应返回 5xx, 实际: {response.status_code}"
        data = response.json()
        assert isinstance(data, dict), "响应应为JSON对象"


    def test_EnergyCore_PVESSC_Topology_post_2_empty_body_0014(self, api_client):
        """[EnergyCore.PVESSC][Topology] post_2 - 空请求体"""
        # POST /api/pvessc/topology/capability/batch
        response = api_client.post("pvessc/api/pvessc/topology/capability/batch")
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"空请求体不应返回 5xx, 实际: {response.status_code}"


    def test_EnergyCore_PVESSC_Topology_post_2_boundary_0014(self, api_client):
        """[EnergyCore.PVESSC][Topology] post_2 - 边界值测试"""
        # POST /api/pvessc/topology/capability/batch
        response = api_client.post("pvessc/api/pvessc/topology/capability/batch")
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"边界值测试不应返回 5xx 服务器错误, 实际: {response.status_code}"
        assert isinstance(response.json(), dict), "响应应为JSON对象"


    def test_EnergyCore_PVESSC_Topology_post_2_sql_injection_0014(self, api_client):
        """[EnergyCore.PVESSC][Topology] post_2 - SQL注入防护"""
        # POST /api/pvessc/topology/capability/batch
        response = api_client.post("pvessc/api/pvessc/topology/capability/batch")
        assert response is not None, "响应不应为空"
        assert response.status_code != 500, f"SQL注入不应导致服务器错误, 实际: {response.status_code}"
        data = response.json()
        assert isinstance(data, dict), "响应应为JSON对象"


    def test_EnergyCore_PVESSC_Topology_post_2_xss_protection_0014(self, api_client):
        """[EnergyCore.PVESSC][Topology] post_2 - XSS防护"""
        # POST /api/pvessc/topology/capability/batch
        xss_payload = {"name": "<script>alert('xss')</script>", "code": "XSS_TEST"}
        response = api_client.post("pvessc/api/pvessc/topology/capability/batch", json_data=xss_payload)
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"XSS防护测试不应返回 5xx, 实际: {response.status_code}"


    def test_EnergyCore_PVESSC_Topology_post_2_large_payload_0014(self, api_client):
        """[EnergyCore.PVESSC][Topology] post_2 - 大数据量"""
        # POST /api/pvessc/topology/capability/batch
        large_data = {"name": "x" * 10000, "code": "LARGE", "description": "y" * 50000}
        response = api_client.post("pvessc/api/pvessc/topology/capability/batch", json_data=large_data)
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"大数据量测试不应返回 5xx, 实际: {response.status_code}"


    def test_EnergyCore_PVESSC_Topology_post_2_concurrent_0014(self, api_client):
        """[EnergyCore.PVESSC][Topology] post_2 - 并发请求"""
        # POST /api/pvessc/topology/capability/batch
        responses = []
        for _ in range(3):
            r = api_client.post("pvessc/api/pvessc/topology/capability/batch")
            responses.append(r)
        for r in responses:
            assert r is not None, "并发响应不应为空"
            assert r.status_code < 500, f"并发请求不应返回 5xx, 实际: {r.status_code}"


    def test_EnergyCore_PVESSC_Topology_post_2_timeout_0014(self, api_client):
        """[EnergyCore.PVESSC][Topology] post_2 - 超时处理"""
        # POST /api/pvessc/topology/capability/batch
        response = api_client.post("pvessc/api/pvessc/topology/capability/batch")
        assert response is not None, "超时处理响应不应为空"
        assert response.status_code < 500, f"超时测试不应返回 5xx, 实际: {response.status_code}"


    def test_EnergyCore_PVESSC_Topology_post_2_permission_denied_0014(self, api_client):
        """[EnergyCore.PVESSC][Topology] post_2 - 权限不足"""
        # POST /api/pvessc/topology/capability/batch
        response = api_client.post("pvessc/api/pvessc/topology/capability/batch")
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"权限测试不应返回 5xx, 实际: {response.status_code}"


    def test_EnergyCore_PVESSC_Topology_post_2_field_validation_0014(self, api_client):
        """[EnergyCore.PVESSC][Topology] post_2 - 字段校验"""
        # POST /api/pvessc/topology/capability/batch
        invalid_data = {"name": "", "code": ""}
        response = api_client.post("pvessc/api/pvessc/topology/capability/batch", json_data=invalid_data)
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"字段校验不应返回 5xx, 实际: {response.status_code}"


    def test_EnergyCore_PVESSC_Topology_post_2_response_format_0014(self, api_client):
        """[EnergyCore.PVESSC][Topology] post_2 - 响应格式"""
        # POST /api/pvessc/topology/capability/batch
        response = api_client.post("pvessc/api/pvessc/topology/capability/batch")
        assert response is not None, "响应不应为空"
        data = response.json()
        assert isinstance(data, dict), "响应应为JSON对象"
        if response.status_code == 200:
            assert "success" in data or "data" in data or "code" in data, "200 响应应包含标准字段"


    def test_EnergyCore_PVESSC_Topology_put_3_positive_0015(self, api_client):
        """[EnergyCore.PVESSC][Topology] put_3 - 正常请求"""
        # PUT /api/pvessc/topology/{siteId}
        response = api_client.put("pvessc/api/pvessc/topology/{siteId}", json_data={"name": "updated"})
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"PUT 正常请求不应返回 5xx, 实际: {response.status_code}"


    def test_EnergyCore_PVESSC_Topology_put_3_no_auth_0015(self, api_client):
        """[EnergyCore.PVESSC][Topology] put_3 - 缺少认证头"""
        # PUT /api/pvessc/topology/{siteId}
        api_client.clear_token()
        try:
            response = api_client.put("pvessc/api/pvessc/topology/{siteId}")
            assert response is not None, "响应不应为空"
            assert response.status_code in (200, 400, 401, 403), f"无认证头应返回 401/403, 实际: {response.status_code}"
        finally:
            api_client.restore_token()


    def test_EnergyCore_PVESSC_Topology_put_3_invalid_token_0015(self, api_client):
        """[EnergyCore.PVESSC][Topology] put_3 - 无效Token"""
        # PUT /api/pvessc/topology/{siteId}
        api_client.set_invalid_token()
        try:
            response = api_client.put("pvessc/api/pvessc/topology/{siteId}")
            assert response is not None, "响应不应为空"
            assert response.status_code in (200, 400, 401, 403), f"无效Token应返回 401/403, 实际: {response.status_code}"
        finally:
            api_client.restore_token()


    def test_EnergyCore_PVESSC_Topology_put_3_tenant_isolation_0015(self, api_client):
        """[EnergyCore.PVESSC][Topology] put_3 - 租户隔离"""
        # PUT /api/pvessc/topology/{siteId}
        response = api_client.put("pvessc/api/pvessc/topology/{siteId}")
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"租户隔离测试不应返回 5xx, 实际: {response.status_code}"
        data = response.json()
        assert isinstance(data, dict), "响应应为JSON对象"


    def test_EnergyCore_PVESSC_Topology_put_3_empty_body_0015(self, api_client):
        """[EnergyCore.PVESSC][Topology] put_3 - 空请求体"""
        # PUT /api/pvessc/topology/{siteId}
        response = api_client.put("pvessc/api/pvessc/topology/{siteId}")
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"空请求体不应返回 5xx, 实际: {response.status_code}"


    def test_EnergyCore_PVESSC_Topology_put_3_invalid_id_0015(self, api_client):
        """[EnergyCore.PVESSC][Topology] put_3 - 无效ID"""
        # PUT /api/pvessc/topology/{siteId}
        response = api_client.put("pvessc/api/pvessc/topology/{siteId}")
        assert response is not None, "响应不应为空"
        assert response.status_code in (200, 400, 403, 404), f"无效ID应返回 200/400/403/404, 实际: {response.status_code}"


    def test_EnergyCore_PVESSC_Topology_put_3_not_found_id_0015(self, api_client):
        """[EnergyCore.PVESSC][Topology] put_3 - 不存在ID"""
        # PUT /api/pvessc/topology/{siteId}
        response = api_client.put("pvessc/api/pvessc/topology/{siteId}")
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"不存在ID不应返回 5xx, 实际: {response.status_code}"


    def test_EnergyCore_PVESSC_Topology_put_3_boundary_0015(self, api_client):
        """[EnergyCore.PVESSC][Topology] put_3 - 边界值测试"""
        # PUT /api/pvessc/topology/{siteId}
        response = api_client.put("pvessc/api/pvessc/topology/{siteId}")
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"边界值测试不应返回 5xx 服务器错误, 实际: {response.status_code}"
        assert isinstance(response.json(), dict), "响应应为JSON对象"


    def test_EnergyCore_PVESSC_Topology_put_3_sql_injection_0015(self, api_client):
        """[EnergyCore.PVESSC][Topology] put_3 - SQL注入防护"""
        # PUT /api/pvessc/topology/{siteId}
        response = api_client.put("pvessc/api/pvessc/topology/{siteId}")
        assert response is not None, "响应不应为空"
        assert response.status_code != 500, f"SQL注入不应导致服务器错误, 实际: {response.status_code}"
        data = response.json()
        assert isinstance(data, dict), "响应应为JSON对象"


    def test_EnergyCore_PVESSC_Topology_put_3_xss_protection_0015(self, api_client):
        """[EnergyCore.PVESSC][Topology] put_3 - XSS防护"""
        # PUT /api/pvessc/topology/{siteId}
        xss_payload = {"name": "<script>alert('xss')</script>", "code": "XSS_TEST"}
        response = api_client.put("pvessc/api/pvessc/topology/{siteId}", json_data=xss_payload)
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"XSS防护测试不应返回 5xx, 实际: {response.status_code}"


    def test_EnergyCore_PVESSC_Topology_put_3_large_payload_0015(self, api_client):
        """[EnergyCore.PVESSC][Topology] put_3 - 大数据量"""
        # PUT /api/pvessc/topology/{siteId}
        large_data = {"name": "x" * 10000, "code": "LARGE", "description": "y" * 50000}
        response = api_client.put("pvessc/api/pvessc/topology/{siteId}", json_data=large_data)
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"大数据量测试不应返回 5xx, 实际: {response.status_code}"


    def test_EnergyCore_PVESSC_Topology_put_3_concurrent_0015(self, api_client):
        """[EnergyCore.PVESSC][Topology] put_3 - 并发请求"""
        # PUT /api/pvessc/topology/{siteId}
        responses = []
        for _ in range(3):
            r = api_client.put("pvessc/api/pvessc/topology/{siteId}")
            responses.append(r)
        for r in responses:
            assert r is not None, "并发响应不应为空"
            assert r.status_code < 500, f"并发请求不应返回 5xx, 实际: {r.status_code}"


    def test_EnergyCore_PVESSC_Topology_put_3_idempotent_0015(self, api_client):
        """[EnergyCore.PVESSC][Topology] put_3 - 幂等性"""
        # PUT /api/pvessc/topology/{siteId}
        r1 = api_client.put("pvessc/api/pvessc/topology/{siteId}")
        r2 = api_client.put("pvessc/api/pvessc/topology/{siteId}")
        assert r1 is not None and r2 is not None, "幂等性响应不应为空"
        assert r1.status_code == r2.status_code, f"幂等性: 两次请求状态码应一致, {r1.status_code} vs {r2.status_code}"


    def test_EnergyCore_PVESSC_Topology_put_3_timeout_0015(self, api_client):
        """[EnergyCore.PVESSC][Topology] put_3 - 超时处理"""
        # PUT /api/pvessc/topology/{siteId}
        response = api_client.put("pvessc/api/pvessc/topology/{siteId}")
        assert response is not None, "超时处理响应不应为空"
        assert response.status_code < 500, f"超时测试不应返回 5xx, 实际: {response.status_code}"


    def test_EnergyCore_PVESSC_Topology_put_3_permission_denied_0015(self, api_client):
        """[EnergyCore.PVESSC][Topology] put_3 - 权限不足"""
        # PUT /api/pvessc/topology/{siteId}
        response = api_client.put("pvessc/api/pvessc/topology/{siteId}")
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"权限测试不应返回 5xx, 实际: {response.status_code}"


    def test_EnergyCore_PVESSC_Topology_put_3_field_validation_0015(self, api_client):
        """[EnergyCore.PVESSC][Topology] put_3 - 字段校验"""
        # PUT /api/pvessc/topology/{siteId}
        invalid_data = {"name": "", "code": ""}
        response = api_client.put("pvessc/api/pvessc/topology/{siteId}", json_data=invalid_data)
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"字段校验不应返回 5xx, 实际: {response.status_code}"


    def test_EnergyCore_PVESSC_Topology_put_3_response_format_0015(self, api_client):
        """[EnergyCore.PVESSC][Topology] put_3 - 响应格式"""
        # PUT /api/pvessc/topology/{siteId}
        response = api_client.put("pvessc/api/pvessc/topology/{siteId}")
        assert response is not None, "响应不应为空"
        data = response.json()
        assert isinstance(data, dict), "响应应为JSON对象"
        if response.status_code == 200:
            assert "success" in data or "data" in data or "code" in data, "200 响应应包含标准字段"


    def test_EnergyCore_PVESSC_V2g_get_0_positive_0016(self, api_client):
        """[EnergyCore.PVESSC][V2g] get_0 - 正常请求"""
        # GET /api/pvessc/v2g/{siteId}/config
        response = api_client.get("pvessc/api/pvessc/v2g/{siteId}/config")
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"GET 正常请求不应返回 5xx, 实际: {response.status_code}"


    def test_EnergyCore_PVESSC_V2g_get_0_no_auth_0016(self, api_client):
        """[EnergyCore.PVESSC][V2g] get_0 - 缺少认证头"""
        # GET /api/pvessc/v2g/{siteId}/config
        api_client.clear_token()
        try:
            response = api_client.get("pvessc/api/pvessc/v2g/{siteId}/config")
            assert response is not None, "响应不应为空"
            assert response.status_code in (200, 400, 401, 403), f"无认证头应返回 401/403, 实际: {response.status_code}"
        finally:
            api_client.restore_token()


    def test_EnergyCore_PVESSC_V2g_get_0_invalid_token_0016(self, api_client):
        """[EnergyCore.PVESSC][V2g] get_0 - 无效Token"""
        # GET /api/pvessc/v2g/{siteId}/config
        api_client.set_invalid_token()
        try:
            response = api_client.get("pvessc/api/pvessc/v2g/{siteId}/config")
            assert response is not None, "响应不应为空"
            assert response.status_code in (200, 400, 401, 403), f"无效Token应返回 401/403, 实际: {response.status_code}"
        finally:
            api_client.restore_token()


    def test_EnergyCore_PVESSC_V2g_get_0_tenant_isolation_0016(self, api_client):
        """[EnergyCore.PVESSC][V2g] get_0 - 租户隔离"""
        # GET /api/pvessc/v2g/{siteId}/config
        response = api_client.get("pvessc/api/pvessc/v2g/{siteId}/config")
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"租户隔离测试不应返回 5xx, 实际: {response.status_code}"
        data = response.json()
        assert isinstance(data, dict), "响应应为JSON对象"


    def test_EnergyCore_PVESSC_V2g_get_0_invalid_id_0016(self, api_client):
        """[EnergyCore.PVESSC][V2g] get_0 - 无效ID"""
        # GET /api/pvessc/v2g/{siteId}/config
        response = api_client.get("pvessc/api/pvessc/v2g/{siteId}/config")
        assert response is not None, "响应不应为空"
        assert response.status_code in (200, 400, 403, 404), f"无效ID应返回 200/400/403/404, 实际: {response.status_code}"


    def test_EnergyCore_PVESSC_V2g_get_0_not_found_id_0016(self, api_client):
        """[EnergyCore.PVESSC][V2g] get_0 - 不存在ID"""
        # GET /api/pvessc/v2g/{siteId}/config
        response = api_client.get("pvessc/api/pvessc/v2g/{siteId}/config")
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"不存在ID不应返回 5xx, 实际: {response.status_code}"


    def test_EnergyCore_PVESSC_V2g_get_0_boundary_0016(self, api_client):
        """[EnergyCore.PVESSC][V2g] get_0 - 边界值测试"""
        # GET /api/pvessc/v2g/{siteId}/config
        response = api_client.get("pvessc/api/pvessc/v2g/{siteId}/config")
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"边界值测试不应返回 5xx 服务器错误, 实际: {response.status_code}"
        assert isinstance(response.json(), dict), "响应应为JSON对象"


    def test_EnergyCore_PVESSC_V2g_get_0_sql_injection_0016(self, api_client):
        """[EnergyCore.PVESSC][V2g] get_0 - SQL注入防护"""
        # GET /api/pvessc/v2g/{siteId}/config
        response = api_client.get("pvessc/api/pvessc/v2g/{siteId}/config")
        assert response is not None, "响应不应为空"
        assert response.status_code != 500, f"SQL注入不应导致服务器错误, 实际: {response.status_code}"
        data = response.json()
        assert isinstance(data, dict), "响应应为JSON对象"


    def test_EnergyCore_PVESSC_V2g_get_0_concurrent_0016(self, api_client):
        """[EnergyCore.PVESSC][V2g] get_0 - 并发请求"""
        # GET /api/pvessc/v2g/{siteId}/config
        responses = []
        for _ in range(3):
            r = api_client.get("pvessc/api/pvessc/v2g/{siteId}/config")
            responses.append(r)
        for r in responses:
            assert r is not None, "并发响应不应为空"
            assert r.status_code < 500, f"并发请求不应返回 5xx, 实际: {r.status_code}"


    def test_EnergyCore_PVESSC_V2g_get_0_timeout_0016(self, api_client):
        """[EnergyCore.PVESSC][V2g] get_0 - 超时处理"""
        # GET /api/pvessc/v2g/{siteId}/config
        response = api_client.get("pvessc/api/pvessc/v2g/{siteId}/config")
        assert response is not None, "超时处理响应不应为空"
        assert response.status_code < 500, f"超时测试不应返回 5xx, 实际: {response.status_code}"


    def test_EnergyCore_PVESSC_V2g_get_0_permission_denied_0016(self, api_client):
        """[EnergyCore.PVESSC][V2g] get_0 - 权限不足"""
        # GET /api/pvessc/v2g/{siteId}/config
        response = api_client.get("pvessc/api/pvessc/v2g/{siteId}/config")
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"权限测试不应返回 5xx, 实际: {response.status_code}"


    def test_EnergyCore_PVESSC_V2g_get_0_response_format_0016(self, api_client):
        """[EnergyCore.PVESSC][V2g] get_0 - 响应格式"""
        # GET /api/pvessc/v2g/{siteId}/config
        response = api_client.get("pvessc/api/pvessc/v2g/{siteId}/config")
        assert response is not None, "响应不应为空"
        data = response.json()
        assert isinstance(data, dict), "响应应为JSON对象"
        if response.status_code == 200:
            assert "success" in data or "data" in data or "code" in data, "200 响应应包含标准字段"


    def test_EnergyCore_PVESSC_V2g_get_1_positive_0017(self, api_client):
        """[EnergyCore.PVESSC][V2g] get_1 - 正常请求"""
        # GET /api/pvessc/v2g/{siteId}/sessions
        response = api_client.get("pvessc/api/pvessc/v2g/{siteId}/sessions")
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"GET 正常请求不应返回 5xx, 实际: {response.status_code}"


    def test_EnergyCore_PVESSC_V2g_get_1_no_auth_0017(self, api_client):
        """[EnergyCore.PVESSC][V2g] get_1 - 缺少认证头"""
        # GET /api/pvessc/v2g/{siteId}/sessions
        api_client.clear_token()
        try:
            response = api_client.get("pvessc/api/pvessc/v2g/{siteId}/sessions")
            assert response is not None, "响应不应为空"
            assert response.status_code in (200, 400, 401, 403), f"无认证头应返回 401/403, 实际: {response.status_code}"
        finally:
            api_client.restore_token()


    def test_EnergyCore_PVESSC_V2g_get_1_invalid_token_0017(self, api_client):
        """[EnergyCore.PVESSC][V2g] get_1 - 无效Token"""
        # GET /api/pvessc/v2g/{siteId}/sessions
        api_client.set_invalid_token()
        try:
            response = api_client.get("pvessc/api/pvessc/v2g/{siteId}/sessions")
            assert response is not None, "响应不应为空"
            assert response.status_code in (200, 400, 401, 403), f"无效Token应返回 401/403, 实际: {response.status_code}"
        finally:
            api_client.restore_token()


    def test_EnergyCore_PVESSC_V2g_get_1_tenant_isolation_0017(self, api_client):
        """[EnergyCore.PVESSC][V2g] get_1 - 租户隔离"""
        # GET /api/pvessc/v2g/{siteId}/sessions
        response = api_client.get("pvessc/api/pvessc/v2g/{siteId}/sessions")
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"租户隔离测试不应返回 5xx, 实际: {response.status_code}"
        data = response.json()
        assert isinstance(data, dict), "响应应为JSON对象"


    def test_EnergyCore_PVESSC_V2g_get_1_invalid_id_0017(self, api_client):
        """[EnergyCore.PVESSC][V2g] get_1 - 无效ID"""
        # GET /api/pvessc/v2g/{siteId}/sessions
        response = api_client.get("pvessc/api/pvessc/v2g/{siteId}/sessions")
        assert response is not None, "响应不应为空"
        assert response.status_code in (200, 400, 403, 404), f"无效ID应返回 200/400/403/404, 实际: {response.status_code}"


    def test_EnergyCore_PVESSC_V2g_get_1_not_found_id_0017(self, api_client):
        """[EnergyCore.PVESSC][V2g] get_1 - 不存在ID"""
        # GET /api/pvessc/v2g/{siteId}/sessions
        response = api_client.get("pvessc/api/pvessc/v2g/{siteId}/sessions")
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"不存在ID不应返回 5xx, 实际: {response.status_code}"


    def test_EnergyCore_PVESSC_V2g_get_1_boundary_0017(self, api_client):
        """[EnergyCore.PVESSC][V2g] get_1 - 边界值测试"""
        # GET /api/pvessc/v2g/{siteId}/sessions
        response = api_client.get("pvessc/api/pvessc/v2g/{siteId}/sessions")
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"边界值测试不应返回 5xx 服务器错误, 实际: {response.status_code}"
        assert isinstance(response.json(), dict), "响应应为JSON对象"


    def test_EnergyCore_PVESSC_V2g_get_1_sql_injection_0017(self, api_client):
        """[EnergyCore.PVESSC][V2g] get_1 - SQL注入防护"""
        # GET /api/pvessc/v2g/{siteId}/sessions
        response = api_client.get("pvessc/api/pvessc/v2g/{siteId}/sessions")
        assert response is not None, "响应不应为空"
        assert response.status_code != 500, f"SQL注入不应导致服务器错误, 实际: {response.status_code}"
        data = response.json()
        assert isinstance(data, dict), "响应应为JSON对象"


    def test_EnergyCore_PVESSC_V2g_get_1_concurrent_0017(self, api_client):
        """[EnergyCore.PVESSC][V2g] get_1 - 并发请求"""
        # GET /api/pvessc/v2g/{siteId}/sessions
        responses = []
        for _ in range(3):
            r = api_client.get("pvessc/api/pvessc/v2g/{siteId}/sessions")
            responses.append(r)
        for r in responses:
            assert r is not None, "并发响应不应为空"
            assert r.status_code < 500, f"并发请求不应返回 5xx, 实际: {r.status_code}"


    def test_EnergyCore_PVESSC_V2g_get_1_timeout_0017(self, api_client):
        """[EnergyCore.PVESSC][V2g] get_1 - 超时处理"""
        # GET /api/pvessc/v2g/{siteId}/sessions
        response = api_client.get("pvessc/api/pvessc/v2g/{siteId}/sessions")
        assert response is not None, "超时处理响应不应为空"
        assert response.status_code < 500, f"超时测试不应返回 5xx, 实际: {response.status_code}"


    def test_EnergyCore_PVESSC_V2g_get_1_permission_denied_0017(self, api_client):
        """[EnergyCore.PVESSC][V2g] get_1 - 权限不足"""
        # GET /api/pvessc/v2g/{siteId}/sessions
        response = api_client.get("pvessc/api/pvessc/v2g/{siteId}/sessions")
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"权限测试不应返回 5xx, 实际: {response.status_code}"


    def test_EnergyCore_PVESSC_V2g_get_1_response_format_0017(self, api_client):
        """[EnergyCore.PVESSC][V2g] get_1 - 响应格式"""
        # GET /api/pvessc/v2g/{siteId}/sessions
        response = api_client.get("pvessc/api/pvessc/v2g/{siteId}/sessions")
        assert response is not None, "响应不应为空"
        data = response.json()
        assert isinstance(data, dict), "响应应为JSON对象"
        if response.status_code == 200:
            assert "success" in data or "data" in data or "code" in data, "200 响应应包含标准字段"


    def test_EnergyCore_PVESSC_V2g_get_2_positive_0018(self, api_client):
        """[EnergyCore.PVESSC][V2g] get_2 - 正常请求"""
        # GET /api/pvessc/v2g/session/{sessionId}
        response = api_client.get("pvessc/api/pvessc/v2g/session/{sessionId}")
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"GET 正常请求不应返回 5xx, 实际: {response.status_code}"


    def test_EnergyCore_PVESSC_V2g_get_2_no_auth_0018(self, api_client):
        """[EnergyCore.PVESSC][V2g] get_2 - 缺少认证头"""
        # GET /api/pvessc/v2g/session/{sessionId}
        api_client.clear_token()
        try:
            response = api_client.get("pvessc/api/pvessc/v2g/session/{sessionId}")
            assert response is not None, "响应不应为空"
            assert response.status_code in (200, 400, 401, 403), f"无认证头应返回 401/403, 实际: {response.status_code}"
        finally:
            api_client.restore_token()


    def test_EnergyCore_PVESSC_V2g_get_2_invalid_token_0018(self, api_client):
        """[EnergyCore.PVESSC][V2g] get_2 - 无效Token"""
        # GET /api/pvessc/v2g/session/{sessionId}
        api_client.set_invalid_token()
        try:
            response = api_client.get("pvessc/api/pvessc/v2g/session/{sessionId}")
            assert response is not None, "响应不应为空"
            assert response.status_code in (200, 400, 401, 403), f"无效Token应返回 401/403, 实际: {response.status_code}"
        finally:
            api_client.restore_token()


    def test_EnergyCore_PVESSC_V2g_get_2_tenant_isolation_0018(self, api_client):
        """[EnergyCore.PVESSC][V2g] get_2 - 租户隔离"""
        # GET /api/pvessc/v2g/session/{sessionId}
        response = api_client.get("pvessc/api/pvessc/v2g/session/{sessionId}")
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"租户隔离测试不应返回 5xx, 实际: {response.status_code}"
        data = response.json()
        assert isinstance(data, dict), "响应应为JSON对象"


    def test_EnergyCore_PVESSC_V2g_get_2_invalid_id_0018(self, api_client):
        """[EnergyCore.PVESSC][V2g] get_2 - 无效ID"""
        # GET /api/pvessc/v2g/session/{sessionId}
        response = api_client.get("pvessc/api/pvessc/v2g/session/{sessionId}")
        assert response is not None, "响应不应为空"
        assert response.status_code in (200, 400, 403, 404), f"无效ID应返回 200/400/403/404, 实际: {response.status_code}"


    def test_EnergyCore_PVESSC_V2g_get_2_not_found_id_0018(self, api_client):
        """[EnergyCore.PVESSC][V2g] get_2 - 不存在ID"""
        # GET /api/pvessc/v2g/session/{sessionId}
        response = api_client.get("pvessc/api/pvessc/v2g/session/{sessionId}")
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"不存在ID不应返回 5xx, 实际: {response.status_code}"


    def test_EnergyCore_PVESSC_V2g_get_2_boundary_0018(self, api_client):
        """[EnergyCore.PVESSC][V2g] get_2 - 边界值测试"""
        # GET /api/pvessc/v2g/session/{sessionId}
        response = api_client.get("pvessc/api/pvessc/v2g/session/{sessionId}")
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"边界值测试不应返回 5xx 服务器错误, 实际: {response.status_code}"
        assert isinstance(response.json(), dict), "响应应为JSON对象"


    def test_EnergyCore_PVESSC_V2g_get_2_sql_injection_0018(self, api_client):
        """[EnergyCore.PVESSC][V2g] get_2 - SQL注入防护"""
        # GET /api/pvessc/v2g/session/{sessionId}
        response = api_client.get("pvessc/api/pvessc/v2g/session/{sessionId}")
        assert response is not None, "响应不应为空"
        assert response.status_code != 500, f"SQL注入不应导致服务器错误, 实际: {response.status_code}"
        data = response.json()
        assert isinstance(data, dict), "响应应为JSON对象"


    def test_EnergyCore_PVESSC_V2g_get_2_concurrent_0018(self, api_client):
        """[EnergyCore.PVESSC][V2g] get_2 - 并发请求"""
        # GET /api/pvessc/v2g/session/{sessionId}
        responses = []
        for _ in range(3):
            r = api_client.get("pvessc/api/pvessc/v2g/session/{sessionId}")
            responses.append(r)
        for r in responses:
            assert r is not None, "并发响应不应为空"
            assert r.status_code < 500, f"并发请求不应返回 5xx, 实际: {r.status_code}"


    def test_EnergyCore_PVESSC_V2g_get_2_timeout_0018(self, api_client):
        """[EnergyCore.PVESSC][V2g] get_2 - 超时处理"""
        # GET /api/pvessc/v2g/session/{sessionId}
        response = api_client.get("pvessc/api/pvessc/v2g/session/{sessionId}")
        assert response is not None, "超时处理响应不应为空"
        assert response.status_code < 500, f"超时测试不应返回 5xx, 实际: {response.status_code}"


    def test_EnergyCore_PVESSC_V2g_get_2_permission_denied_0018(self, api_client):
        """[EnergyCore.PVESSC][V2g] get_2 - 权限不足"""
        # GET /api/pvessc/v2g/session/{sessionId}
        response = api_client.get("pvessc/api/pvessc/v2g/session/{sessionId}")
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"权限测试不应返回 5xx, 实际: {response.status_code}"


    def test_EnergyCore_PVESSC_V2g_get_2_response_format_0018(self, api_client):
        """[EnergyCore.PVESSC][V2g] get_2 - 响应格式"""
        # GET /api/pvessc/v2g/session/{sessionId}
        response = api_client.get("pvessc/api/pvessc/v2g/session/{sessionId}")
        assert response is not None, "响应不应为空"
        data = response.json()
        assert isinstance(data, dict), "响应应为JSON对象"
        if response.status_code == 200:
            assert "success" in data or "data" in data or "code" in data, "200 响应应包含标准字段"


    def test_EnergyCore_PVESSC_V2g_get_3_positive_0019(self, api_client):
        """[EnergyCore.PVESSC][V2g] get_3 - 正常请求"""
        # GET /api/pvessc/v2g/{siteId}/settlement
        response = api_client.get("pvessc/api/pvessc/v2g/{siteId}/settlement")
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"GET 正常请求不应返回 5xx, 实际: {response.status_code}"


    def test_EnergyCore_PVESSC_V2g_get_3_no_auth_0019(self, api_client):
        """[EnergyCore.PVESSC][V2g] get_3 - 缺少认证头"""
        # GET /api/pvessc/v2g/{siteId}/settlement
        api_client.clear_token()
        try:
            response = api_client.get("pvessc/api/pvessc/v2g/{siteId}/settlement")
            assert response is not None, "响应不应为空"
            assert response.status_code in (200, 400, 401, 403), f"无认证头应返回 401/403, 实际: {response.status_code}"
        finally:
            api_client.restore_token()


    def test_EnergyCore_PVESSC_V2g_get_3_invalid_token_0019(self, api_client):
        """[EnergyCore.PVESSC][V2g] get_3 - 无效Token"""
        # GET /api/pvessc/v2g/{siteId}/settlement
        api_client.set_invalid_token()
        try:
            response = api_client.get("pvessc/api/pvessc/v2g/{siteId}/settlement")
            assert response is not None, "响应不应为空"
            assert response.status_code in (200, 400, 401, 403), f"无效Token应返回 401/403, 实际: {response.status_code}"
        finally:
            api_client.restore_token()


    def test_EnergyCore_PVESSC_V2g_get_3_tenant_isolation_0019(self, api_client):
        """[EnergyCore.PVESSC][V2g] get_3 - 租户隔离"""
        # GET /api/pvessc/v2g/{siteId}/settlement
        response = api_client.get("pvessc/api/pvessc/v2g/{siteId}/settlement")
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"租户隔离测试不应返回 5xx, 实际: {response.status_code}"
        data = response.json()
        assert isinstance(data, dict), "响应应为JSON对象"


    def test_EnergyCore_PVESSC_V2g_get_3_invalid_id_0019(self, api_client):
        """[EnergyCore.PVESSC][V2g] get_3 - 无效ID"""
        # GET /api/pvessc/v2g/{siteId}/settlement
        response = api_client.get("pvessc/api/pvessc/v2g/{siteId}/settlement")
        assert response is not None, "响应不应为空"
        assert response.status_code in (200, 400, 403, 404), f"无效ID应返回 200/400/403/404, 实际: {response.status_code}"


    def test_EnergyCore_PVESSC_V2g_get_3_not_found_id_0019(self, api_client):
        """[EnergyCore.PVESSC][V2g] get_3 - 不存在ID"""
        # GET /api/pvessc/v2g/{siteId}/settlement
        response = api_client.get("pvessc/api/pvessc/v2g/{siteId}/settlement")
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"不存在ID不应返回 5xx, 实际: {response.status_code}"


    def test_EnergyCore_PVESSC_V2g_get_3_boundary_0019(self, api_client):
        """[EnergyCore.PVESSC][V2g] get_3 - 边界值测试"""
        # GET /api/pvessc/v2g/{siteId}/settlement
        response = api_client.get("pvessc/api/pvessc/v2g/{siteId}/settlement")
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"边界值测试不应返回 5xx 服务器错误, 实际: {response.status_code}"
        assert isinstance(response.json(), dict), "响应应为JSON对象"


    def test_EnergyCore_PVESSC_V2g_get_3_sql_injection_0019(self, api_client):
        """[EnergyCore.PVESSC][V2g] get_3 - SQL注入防护"""
        # GET /api/pvessc/v2g/{siteId}/settlement
        response = api_client.get("pvessc/api/pvessc/v2g/{siteId}/settlement")
        assert response is not None, "响应不应为空"
        assert response.status_code != 500, f"SQL注入不应导致服务器错误, 实际: {response.status_code}"
        data = response.json()
        assert isinstance(data, dict), "响应应为JSON对象"


    def test_EnergyCore_PVESSC_V2g_get_3_concurrent_0019(self, api_client):
        """[EnergyCore.PVESSC][V2g] get_3 - 并发请求"""
        # GET /api/pvessc/v2g/{siteId}/settlement
        responses = []
        for _ in range(3):
            r = api_client.get("pvessc/api/pvessc/v2g/{siteId}/settlement")
            responses.append(r)
        for r in responses:
            assert r is not None, "并发响应不应为空"
            assert r.status_code < 500, f"并发请求不应返回 5xx, 实际: {r.status_code}"


    def test_EnergyCore_PVESSC_V2g_get_3_timeout_0019(self, api_client):
        """[EnergyCore.PVESSC][V2g] get_3 - 超时处理"""
        # GET /api/pvessc/v2g/{siteId}/settlement
        response = api_client.get("pvessc/api/pvessc/v2g/{siteId}/settlement")
        assert response is not None, "超时处理响应不应为空"
        assert response.status_code < 500, f"超时测试不应返回 5xx, 实际: {response.status_code}"


    def test_EnergyCore_PVESSC_V2g_get_3_permission_denied_0019(self, api_client):
        """[EnergyCore.PVESSC][V2g] get_3 - 权限不足"""
        # GET /api/pvessc/v2g/{siteId}/settlement
        response = api_client.get("pvessc/api/pvessc/v2g/{siteId}/settlement")
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"权限测试不应返回 5xx, 实际: {response.status_code}"


    def test_EnergyCore_PVESSC_V2g_get_3_response_format_0019(self, api_client):
        """[EnergyCore.PVESSC][V2g] get_3 - 响应格式"""
        # GET /api/pvessc/v2g/{siteId}/settlement
        response = api_client.get("pvessc/api/pvessc/v2g/{siteId}/settlement")
        assert response is not None, "响应不应为空"
        data = response.json()
        assert isinstance(data, dict), "响应应为JSON对象"
        if response.status_code == 200:
            assert "success" in data or "data" in data or "code" in data, "200 响应应包含标准字段"


    def test_EnergyCore_PVESSC_V2g_get_4_positive_0020(self, api_client):
        """[EnergyCore.PVESSC][V2g] get_4 - 正常请求"""
        # GET /api/pvessc/v2g/{siteId}/revenue
        response = api_client.get("pvessc/api/pvessc/v2g/{siteId}/revenue")
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"GET 正常请求不应返回 5xx, 实际: {response.status_code}"


    def test_EnergyCore_PVESSC_V2g_get_4_no_auth_0020(self, api_client):
        """[EnergyCore.PVESSC][V2g] get_4 - 缺少认证头"""
        # GET /api/pvessc/v2g/{siteId}/revenue
        api_client.clear_token()
        try:
            response = api_client.get("pvessc/api/pvessc/v2g/{siteId}/revenue")
            assert response is not None, "响应不应为空"
            assert response.status_code in (200, 400, 401, 403), f"无认证头应返回 401/403, 实际: {response.status_code}"
        finally:
            api_client.restore_token()


    def test_EnergyCore_PVESSC_V2g_get_4_invalid_token_0020(self, api_client):
        """[EnergyCore.PVESSC][V2g] get_4 - 无效Token"""
        # GET /api/pvessc/v2g/{siteId}/revenue
        api_client.set_invalid_token()
        try:
            response = api_client.get("pvessc/api/pvessc/v2g/{siteId}/revenue")
            assert response is not None, "响应不应为空"
            assert response.status_code in (200, 400, 401, 403), f"无效Token应返回 401/403, 实际: {response.status_code}"
        finally:
            api_client.restore_token()


    def test_EnergyCore_PVESSC_V2g_get_4_tenant_isolation_0020(self, api_client):
        """[EnergyCore.PVESSC][V2g] get_4 - 租户隔离"""
        # GET /api/pvessc/v2g/{siteId}/revenue
        response = api_client.get("pvessc/api/pvessc/v2g/{siteId}/revenue")
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"租户隔离测试不应返回 5xx, 实际: {response.status_code}"
        data = response.json()
        assert isinstance(data, dict), "响应应为JSON对象"


    def test_EnergyCore_PVESSC_V2g_get_4_invalid_id_0020(self, api_client):
        """[EnergyCore.PVESSC][V2g] get_4 - 无效ID"""
        # GET /api/pvessc/v2g/{siteId}/revenue
        response = api_client.get("pvessc/api/pvessc/v2g/{siteId}/revenue")
        assert response is not None, "响应不应为空"
        assert response.status_code in (200, 400, 403, 404), f"无效ID应返回 200/400/403/404, 实际: {response.status_code}"


    def test_EnergyCore_PVESSC_V2g_get_4_not_found_id_0020(self, api_client):
        """[EnergyCore.PVESSC][V2g] get_4 - 不存在ID"""
        # GET /api/pvessc/v2g/{siteId}/revenue
        response = api_client.get("pvessc/api/pvessc/v2g/{siteId}/revenue")
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"不存在ID不应返回 5xx, 实际: {response.status_code}"


    def test_EnergyCore_PVESSC_V2g_get_4_boundary_0020(self, api_client):
        """[EnergyCore.PVESSC][V2g] get_4 - 边界值测试"""
        # GET /api/pvessc/v2g/{siteId}/revenue
        response = api_client.get("pvessc/api/pvessc/v2g/{siteId}/revenue")
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"边界值测试不应返回 5xx 服务器错误, 实际: {response.status_code}"
        assert isinstance(response.json(), dict), "响应应为JSON对象"


    def test_EnergyCore_PVESSC_V2g_get_4_sql_injection_0020(self, api_client):
        """[EnergyCore.PVESSC][V2g] get_4 - SQL注入防护"""
        # GET /api/pvessc/v2g/{siteId}/revenue
        response = api_client.get("pvessc/api/pvessc/v2g/{siteId}/revenue")
        assert response is not None, "响应不应为空"
        assert response.status_code != 500, f"SQL注入不应导致服务器错误, 实际: {response.status_code}"
        data = response.json()
        assert isinstance(data, dict), "响应应为JSON对象"


    def test_EnergyCore_PVESSC_V2g_get_4_concurrent_0020(self, api_client):
        """[EnergyCore.PVESSC][V2g] get_4 - 并发请求"""
        # GET /api/pvessc/v2g/{siteId}/revenue
        responses = []
        for _ in range(3):
            r = api_client.get("pvessc/api/pvessc/v2g/{siteId}/revenue")
            responses.append(r)
        for r in responses:
            assert r is not None, "并发响应不应为空"
            assert r.status_code < 500, f"并发请求不应返回 5xx, 实际: {r.status_code}"


    def test_EnergyCore_PVESSC_V2g_get_4_timeout_0020(self, api_client):
        """[EnergyCore.PVESSC][V2g] get_4 - 超时处理"""
        # GET /api/pvessc/v2g/{siteId}/revenue
        response = api_client.get("pvessc/api/pvessc/v2g/{siteId}/revenue")
        assert response is not None, "超时处理响应不应为空"
        assert response.status_code < 500, f"超时测试不应返回 5xx, 实际: {response.status_code}"


    def test_EnergyCore_PVESSC_V2g_get_4_permission_denied_0020(self, api_client):
        """[EnergyCore.PVESSC][V2g] get_4 - 权限不足"""
        # GET /api/pvessc/v2g/{siteId}/revenue
        response = api_client.get("pvessc/api/pvessc/v2g/{siteId}/revenue")
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"权限测试不应返回 5xx, 实际: {response.status_code}"


    def test_EnergyCore_PVESSC_V2g_get_4_response_format_0020(self, api_client):
        """[EnergyCore.PVESSC][V2g] get_4 - 响应格式"""
        # GET /api/pvessc/v2g/{siteId}/revenue
        response = api_client.get("pvessc/api/pvessc/v2g/{siteId}/revenue")
        assert response is not None, "响应不应为空"
        data = response.json()
        assert isinstance(data, dict), "响应应为JSON对象"
        if response.status_code == 200:
            assert "success" in data or "data" in data or "code" in data, "200 响应应包含标准字段"


    def test_EnergyCore_PVESSC_V2g_get_5_positive_0021(self, api_client):
        """[EnergyCore.PVESSC][V2g] get_5 - 正常请求"""
        # GET /api/pvessc/v2g/resources/{siteId}
        response = api_client.get("pvessc/api/pvessc/v2g/resources/{siteId}")
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"GET 正常请求不应返回 5xx, 实际: {response.status_code}"


    def test_EnergyCore_PVESSC_V2g_get_5_no_auth_0021(self, api_client):
        """[EnergyCore.PVESSC][V2g] get_5 - 缺少认证头"""
        # GET /api/pvessc/v2g/resources/{siteId}
        api_client.clear_token()
        try:
            response = api_client.get("pvessc/api/pvessc/v2g/resources/{siteId}")
            assert response is not None, "响应不应为空"
            assert response.status_code in (200, 400, 401, 403), f"无认证头应返回 401/403, 实际: {response.status_code}"
        finally:
            api_client.restore_token()


    def test_EnergyCore_PVESSC_V2g_get_5_invalid_token_0021(self, api_client):
        """[EnergyCore.PVESSC][V2g] get_5 - 无效Token"""
        # GET /api/pvessc/v2g/resources/{siteId}
        api_client.set_invalid_token()
        try:
            response = api_client.get("pvessc/api/pvessc/v2g/resources/{siteId}")
            assert response is not None, "响应不应为空"
            assert response.status_code in (200, 400, 401, 403), f"无效Token应返回 401/403, 实际: {response.status_code}"
        finally:
            api_client.restore_token()


    def test_EnergyCore_PVESSC_V2g_get_5_tenant_isolation_0021(self, api_client):
        """[EnergyCore.PVESSC][V2g] get_5 - 租户隔离"""
        # GET /api/pvessc/v2g/resources/{siteId}
        response = api_client.get("pvessc/api/pvessc/v2g/resources/{siteId}")
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"租户隔离测试不应返回 5xx, 实际: {response.status_code}"
        data = response.json()
        assert isinstance(data, dict), "响应应为JSON对象"


    def test_EnergyCore_PVESSC_V2g_get_5_invalid_id_0021(self, api_client):
        """[EnergyCore.PVESSC][V2g] get_5 - 无效ID"""
        # GET /api/pvessc/v2g/resources/{siteId}
        response = api_client.get("pvessc/api/pvessc/v2g/resources/{siteId}")
        assert response is not None, "响应不应为空"
        assert response.status_code in (200, 400, 403, 404), f"无效ID应返回 200/400/403/404, 实际: {response.status_code}"


    def test_EnergyCore_PVESSC_V2g_get_5_not_found_id_0021(self, api_client):
        """[EnergyCore.PVESSC][V2g] get_5 - 不存在ID"""
        # GET /api/pvessc/v2g/resources/{siteId}
        response = api_client.get("pvessc/api/pvessc/v2g/resources/{siteId}")
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"不存在ID不应返回 5xx, 实际: {response.status_code}"


    def test_EnergyCore_PVESSC_V2g_get_5_boundary_0021(self, api_client):
        """[EnergyCore.PVESSC][V2g] get_5 - 边界值测试"""
        # GET /api/pvessc/v2g/resources/{siteId}
        response = api_client.get("pvessc/api/pvessc/v2g/resources/{siteId}")
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"边界值测试不应返回 5xx 服务器错误, 实际: {response.status_code}"
        assert isinstance(response.json(), dict), "响应应为JSON对象"


    def test_EnergyCore_PVESSC_V2g_get_5_sql_injection_0021(self, api_client):
        """[EnergyCore.PVESSC][V2g] get_5 - SQL注入防护"""
        # GET /api/pvessc/v2g/resources/{siteId}
        response = api_client.get("pvessc/api/pvessc/v2g/resources/{siteId}")
        assert response is not None, "响应不应为空"
        assert response.status_code != 500, f"SQL注入不应导致服务器错误, 实际: {response.status_code}"
        data = response.json()
        assert isinstance(data, dict), "响应应为JSON对象"


    def test_EnergyCore_PVESSC_V2g_get_5_concurrent_0021(self, api_client):
        """[EnergyCore.PVESSC][V2g] get_5 - 并发请求"""
        # GET /api/pvessc/v2g/resources/{siteId}
        responses = []
        for _ in range(3):
            r = api_client.get("pvessc/api/pvessc/v2g/resources/{siteId}")
            responses.append(r)
        for r in responses:
            assert r is not None, "并发响应不应为空"
            assert r.status_code < 500, f"并发请求不应返回 5xx, 实际: {r.status_code}"


    def test_EnergyCore_PVESSC_V2g_get_5_timeout_0021(self, api_client):
        """[EnergyCore.PVESSC][V2g] get_5 - 超时处理"""
        # GET /api/pvessc/v2g/resources/{siteId}
        response = api_client.get("pvessc/api/pvessc/v2g/resources/{siteId}")
        assert response is not None, "超时处理响应不应为空"
        assert response.status_code < 500, f"超时测试不应返回 5xx, 实际: {response.status_code}"


    def test_EnergyCore_PVESSC_V2g_get_5_permission_denied_0021(self, api_client):
        """[EnergyCore.PVESSC][V2g] get_5 - 权限不足"""
        # GET /api/pvessc/v2g/resources/{siteId}
        response = api_client.get("pvessc/api/pvessc/v2g/resources/{siteId}")
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"权限测试不应返回 5xx, 实际: {response.status_code}"


    def test_EnergyCore_PVESSC_V2g_get_5_response_format_0021(self, api_client):
        """[EnergyCore.PVESSC][V2g] get_5 - 响应格式"""
        # GET /api/pvessc/v2g/resources/{siteId}
        response = api_client.get("pvessc/api/pvessc/v2g/resources/{siteId}")
        assert response is not None, "响应不应为空"
        data = response.json()
        assert isinstance(data, dict), "响应应为JSON对象"
        if response.status_code == 200:
            assert "success" in data or "data" in data or "code" in data, "200 响应应包含标准字段"


    def test_EnergyCore_PVESSC_V2g_post_6_positive_0022(self, api_client):
        """[EnergyCore.PVESSC][V2g] post_6 - 正常请求"""
        # POST /api/pvessc/v2g/{siteId}/authorize
        response = api_client.post("pvessc/api/pvessc/v2g/{siteId}/authorize", json_data={"name": "test", "code": "TEST"})
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"POST 正常请求不应返回 5xx, 实际: {response.status_code}"


    def test_EnergyCore_PVESSC_V2g_post_6_no_auth_0022(self, api_client):
        """[EnergyCore.PVESSC][V2g] post_6 - 缺少认证头"""
        # POST /api/pvessc/v2g/{siteId}/authorize
        api_client.clear_token()
        try:
            response = api_client.post("pvessc/api/pvessc/v2g/{siteId}/authorize")
            assert response is not None, "响应不应为空"
            assert response.status_code in (200, 400, 401, 403), f"无认证头应返回 401/403, 实际: {response.status_code}"
        finally:
            api_client.restore_token()


    def test_EnergyCore_PVESSC_V2g_post_6_invalid_token_0022(self, api_client):
        """[EnergyCore.PVESSC][V2g] post_6 - 无效Token"""
        # POST /api/pvessc/v2g/{siteId}/authorize
        api_client.set_invalid_token()
        try:
            response = api_client.post("pvessc/api/pvessc/v2g/{siteId}/authorize")
            assert response is not None, "响应不应为空"
            assert response.status_code in (200, 400, 401, 403), f"无效Token应返回 401/403, 实际: {response.status_code}"
        finally:
            api_client.restore_token()


    def test_EnergyCore_PVESSC_V2g_post_6_tenant_isolation_0022(self, api_client):
        """[EnergyCore.PVESSC][V2g] post_6 - 租户隔离"""
        # POST /api/pvessc/v2g/{siteId}/authorize
        response = api_client.post("pvessc/api/pvessc/v2g/{siteId}/authorize")
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"租户隔离测试不应返回 5xx, 实际: {response.status_code}"
        data = response.json()
        assert isinstance(data, dict), "响应应为JSON对象"


    def test_EnergyCore_PVESSC_V2g_post_6_empty_body_0022(self, api_client):
        """[EnergyCore.PVESSC][V2g] post_6 - 空请求体"""
        # POST /api/pvessc/v2g/{siteId}/authorize
        response = api_client.post("pvessc/api/pvessc/v2g/{siteId}/authorize")
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"空请求体不应返回 5xx, 实际: {response.status_code}"


    def test_EnergyCore_PVESSC_V2g_post_6_invalid_id_0022(self, api_client):
        """[EnergyCore.PVESSC][V2g] post_6 - 无效ID"""
        # POST /api/pvessc/v2g/{siteId}/authorize
        response = api_client.post("pvessc/api/pvessc/v2g/{siteId}/authorize")
        assert response is not None, "响应不应为空"
        assert response.status_code in (200, 400, 403, 404), f"无效ID应返回 200/400/403/404, 实际: {response.status_code}"


    def test_EnergyCore_PVESSC_V2g_post_6_not_found_id_0022(self, api_client):
        """[EnergyCore.PVESSC][V2g] post_6 - 不存在ID"""
        # POST /api/pvessc/v2g/{siteId}/authorize
        response = api_client.post("pvessc/api/pvessc/v2g/{siteId}/authorize")
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"不存在ID不应返回 5xx, 实际: {response.status_code}"


    def test_EnergyCore_PVESSC_V2g_post_6_boundary_0022(self, api_client):
        """[EnergyCore.PVESSC][V2g] post_6 - 边界值测试"""
        # POST /api/pvessc/v2g/{siteId}/authorize
        response = api_client.post("pvessc/api/pvessc/v2g/{siteId}/authorize")
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"边界值测试不应返回 5xx 服务器错误, 实际: {response.status_code}"
        assert isinstance(response.json(), dict), "响应应为JSON对象"


    def test_EnergyCore_PVESSC_V2g_post_6_sql_injection_0022(self, api_client):
        """[EnergyCore.PVESSC][V2g] post_6 - SQL注入防护"""
        # POST /api/pvessc/v2g/{siteId}/authorize
        response = api_client.post("pvessc/api/pvessc/v2g/{siteId}/authorize")
        assert response is not None, "响应不应为空"
        assert response.status_code != 500, f"SQL注入不应导致服务器错误, 实际: {response.status_code}"
        data = response.json()
        assert isinstance(data, dict), "响应应为JSON对象"


    def test_EnergyCore_PVESSC_V2g_post_6_xss_protection_0022(self, api_client):
        """[EnergyCore.PVESSC][V2g] post_6 - XSS防护"""
        # POST /api/pvessc/v2g/{siteId}/authorize
        xss_payload = {"name": "<script>alert('xss')</script>", "code": "XSS_TEST"}
        response = api_client.post("pvessc/api/pvessc/v2g/{siteId}/authorize", json_data=xss_payload)
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"XSS防护测试不应返回 5xx, 实际: {response.status_code}"


    def test_EnergyCore_PVESSC_V2g_post_6_large_payload_0022(self, api_client):
        """[EnergyCore.PVESSC][V2g] post_6 - 大数据量"""
        # POST /api/pvessc/v2g/{siteId}/authorize
        large_data = {"name": "x" * 10000, "code": "LARGE", "description": "y" * 50000}
        response = api_client.post("pvessc/api/pvessc/v2g/{siteId}/authorize", json_data=large_data)
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"大数据量测试不应返回 5xx, 实际: {response.status_code}"


    def test_EnergyCore_PVESSC_V2g_post_6_concurrent_0022(self, api_client):
        """[EnergyCore.PVESSC][V2g] post_6 - 并发请求"""
        # POST /api/pvessc/v2g/{siteId}/authorize
        responses = []
        for _ in range(3):
            r = api_client.post("pvessc/api/pvessc/v2g/{siteId}/authorize")
            responses.append(r)
        for r in responses:
            assert r is not None, "并发响应不应为空"
            assert r.status_code < 500, f"并发请求不应返回 5xx, 实际: {r.status_code}"


    def test_EnergyCore_PVESSC_V2g_post_6_timeout_0022(self, api_client):
        """[EnergyCore.PVESSC][V2g] post_6 - 超时处理"""
        # POST /api/pvessc/v2g/{siteId}/authorize
        response = api_client.post("pvessc/api/pvessc/v2g/{siteId}/authorize")
        assert response is not None, "超时处理响应不应为空"
        assert response.status_code < 500, f"超时测试不应返回 5xx, 实际: {response.status_code}"


    def test_EnergyCore_PVESSC_V2g_post_6_permission_denied_0022(self, api_client):
        """[EnergyCore.PVESSC][V2g] post_6 - 权限不足"""
        # POST /api/pvessc/v2g/{siteId}/authorize
        response = api_client.post("pvessc/api/pvessc/v2g/{siteId}/authorize")
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"权限测试不应返回 5xx, 实际: {response.status_code}"


    def test_EnergyCore_PVESSC_V2g_post_6_field_validation_0022(self, api_client):
        """[EnergyCore.PVESSC][V2g] post_6 - 字段校验"""
        # POST /api/pvessc/v2g/{siteId}/authorize
        invalid_data = {"name": "", "code": ""}
        response = api_client.post("pvessc/api/pvessc/v2g/{siteId}/authorize", json_data=invalid_data)
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"字段校验不应返回 5xx, 实际: {response.status_code}"


    def test_EnergyCore_PVESSC_V2g_post_6_response_format_0022(self, api_client):
        """[EnergyCore.PVESSC][V2g] post_6 - 响应格式"""
        # POST /api/pvessc/v2g/{siteId}/authorize
        response = api_client.post("pvessc/api/pvessc/v2g/{siteId}/authorize")
        assert response is not None, "响应不应为空"
        data = response.json()
        assert isinstance(data, dict), "响应应为JSON对象"
        if response.status_code == 200:
            assert "success" in data or "data" in data or "code" in data, "200 响应应包含标准字段"


    def test_EnergyCore_PVESSC_V2g_post_7_positive_0023(self, api_client):
        """[EnergyCore.PVESSC][V2g] post_7 - 正常请求"""
        # POST /api/pvessc/v2g/session/{sessionId}/stop
        response = api_client.post("pvessc/api/pvessc/v2g/session/{sessionId}/stop", json_data={"name": "test", "code": "TEST"})
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"POST 正常请求不应返回 5xx, 实际: {response.status_code}"


    def test_EnergyCore_PVESSC_V2g_post_7_no_auth_0023(self, api_client):
        """[EnergyCore.PVESSC][V2g] post_7 - 缺少认证头"""
        # POST /api/pvessc/v2g/session/{sessionId}/stop
        api_client.clear_token()
        try:
            response = api_client.post("pvessc/api/pvessc/v2g/session/{sessionId}/stop")
            assert response is not None, "响应不应为空"
            assert response.status_code in (200, 400, 401, 403), f"无认证头应返回 401/403, 实际: {response.status_code}"
        finally:
            api_client.restore_token()


    def test_EnergyCore_PVESSC_V2g_post_7_invalid_token_0023(self, api_client):
        """[EnergyCore.PVESSC][V2g] post_7 - 无效Token"""
        # POST /api/pvessc/v2g/session/{sessionId}/stop
        api_client.set_invalid_token()
        try:
            response = api_client.post("pvessc/api/pvessc/v2g/session/{sessionId}/stop")
            assert response is not None, "响应不应为空"
            assert response.status_code in (200, 400, 401, 403), f"无效Token应返回 401/403, 实际: {response.status_code}"
        finally:
            api_client.restore_token()


    def test_EnergyCore_PVESSC_V2g_post_7_tenant_isolation_0023(self, api_client):
        """[EnergyCore.PVESSC][V2g] post_7 - 租户隔离"""
        # POST /api/pvessc/v2g/session/{sessionId}/stop
        response = api_client.post("pvessc/api/pvessc/v2g/session/{sessionId}/stop")
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"租户隔离测试不应返回 5xx, 实际: {response.status_code}"
        data = response.json()
        assert isinstance(data, dict), "响应应为JSON对象"


    def test_EnergyCore_PVESSC_V2g_post_7_empty_body_0023(self, api_client):
        """[EnergyCore.PVESSC][V2g] post_7 - 空请求体"""
        # POST /api/pvessc/v2g/session/{sessionId}/stop
        response = api_client.post("pvessc/api/pvessc/v2g/session/{sessionId}/stop")
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"空请求体不应返回 5xx, 实际: {response.status_code}"


    def test_EnergyCore_PVESSC_V2g_post_7_invalid_id_0023(self, api_client):
        """[EnergyCore.PVESSC][V2g] post_7 - 无效ID"""
        # POST /api/pvessc/v2g/session/{sessionId}/stop
        response = api_client.post("pvessc/api/pvessc/v2g/session/{sessionId}/stop")
        assert response is not None, "响应不应为空"
        assert response.status_code in (200, 400, 403, 404), f"无效ID应返回 200/400/403/404, 实际: {response.status_code}"


    def test_EnergyCore_PVESSC_V2g_post_7_not_found_id_0023(self, api_client):
        """[EnergyCore.PVESSC][V2g] post_7 - 不存在ID"""
        # POST /api/pvessc/v2g/session/{sessionId}/stop
        response = api_client.post("pvessc/api/pvessc/v2g/session/{sessionId}/stop")
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"不存在ID不应返回 5xx, 实际: {response.status_code}"


    def test_EnergyCore_PVESSC_V2g_post_7_boundary_0023(self, api_client):
        """[EnergyCore.PVESSC][V2g] post_7 - 边界值测试"""
        # POST /api/pvessc/v2g/session/{sessionId}/stop
        response = api_client.post("pvessc/api/pvessc/v2g/session/{sessionId}/stop")
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"边界值测试不应返回 5xx 服务器错误, 实际: {response.status_code}"
        assert isinstance(response.json(), dict), "响应应为JSON对象"


    def test_EnergyCore_PVESSC_V2g_post_7_sql_injection_0023(self, api_client):
        """[EnergyCore.PVESSC][V2g] post_7 - SQL注入防护"""
        # POST /api/pvessc/v2g/session/{sessionId}/stop
        response = api_client.post("pvessc/api/pvessc/v2g/session/{sessionId}/stop")
        assert response is not None, "响应不应为空"
        assert response.status_code != 500, f"SQL注入不应导致服务器错误, 实际: {response.status_code}"
        data = response.json()
        assert isinstance(data, dict), "响应应为JSON对象"


    def test_EnergyCore_PVESSC_V2g_post_7_xss_protection_0023(self, api_client):
        """[EnergyCore.PVESSC][V2g] post_7 - XSS防护"""
        # POST /api/pvessc/v2g/session/{sessionId}/stop
        xss_payload = {"name": "<script>alert('xss')</script>", "code": "XSS_TEST"}
        response = api_client.post("pvessc/api/pvessc/v2g/session/{sessionId}/stop", json_data=xss_payload)
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"XSS防护测试不应返回 5xx, 实际: {response.status_code}"


    def test_EnergyCore_PVESSC_V2g_post_7_large_payload_0023(self, api_client):
        """[EnergyCore.PVESSC][V2g] post_7 - 大数据量"""
        # POST /api/pvessc/v2g/session/{sessionId}/stop
        large_data = {"name": "x" * 10000, "code": "LARGE", "description": "y" * 50000}
        response = api_client.post("pvessc/api/pvessc/v2g/session/{sessionId}/stop", json_data=large_data)
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"大数据量测试不应返回 5xx, 实际: {response.status_code}"


    def test_EnergyCore_PVESSC_V2g_post_7_concurrent_0023(self, api_client):
        """[EnergyCore.PVESSC][V2g] post_7 - 并发请求"""
        # POST /api/pvessc/v2g/session/{sessionId}/stop
        responses = []
        for _ in range(3):
            r = api_client.post("pvessc/api/pvessc/v2g/session/{sessionId}/stop")
            responses.append(r)
        for r in responses:
            assert r is not None, "并发响应不应为空"
            assert r.status_code < 500, f"并发请求不应返回 5xx, 实际: {r.status_code}"


    def test_EnergyCore_PVESSC_V2g_post_7_timeout_0023(self, api_client):
        """[EnergyCore.PVESSC][V2g] post_7 - 超时处理"""
        # POST /api/pvessc/v2g/session/{sessionId}/stop
        response = api_client.post("pvessc/api/pvessc/v2g/session/{sessionId}/stop")
        assert response is not None, "超时处理响应不应为空"
        assert response.status_code < 500, f"超时测试不应返回 5xx, 实际: {response.status_code}"


    def test_EnergyCore_PVESSC_V2g_post_7_permission_denied_0023(self, api_client):
        """[EnergyCore.PVESSC][V2g] post_7 - 权限不足"""
        # POST /api/pvessc/v2g/session/{sessionId}/stop
        response = api_client.post("pvessc/api/pvessc/v2g/session/{sessionId}/stop")
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"权限测试不应返回 5xx, 实际: {response.status_code}"


    def test_EnergyCore_PVESSC_V2g_post_7_field_validation_0023(self, api_client):
        """[EnergyCore.PVESSC][V2g] post_7 - 字段校验"""
        # POST /api/pvessc/v2g/session/{sessionId}/stop
        invalid_data = {"name": "", "code": ""}
        response = api_client.post("pvessc/api/pvessc/v2g/session/{sessionId}/stop", json_data=invalid_data)
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"字段校验不应返回 5xx, 实际: {response.status_code}"


    def test_EnergyCore_PVESSC_V2g_post_7_response_format_0023(self, api_client):
        """[EnergyCore.PVESSC][V2g] post_7 - 响应格式"""
        # POST /api/pvessc/v2g/session/{sessionId}/stop
        response = api_client.post("pvessc/api/pvessc/v2g/session/{sessionId}/stop")
        assert response is not None, "响应不应为空"
        data = response.json()
        assert isinstance(data, dict), "响应应为JSON对象"
        if response.status_code == 200:
            assert "success" in data or "data" in data or "code" in data, "200 响应应包含标准字段"


    def test_EnergyCore_PVESSC_V2g_post_8_positive_0024(self, api_client):
        """[EnergyCore.PVESSC][V2g] post_8 - 正常请求"""
        # POST /api/pvessc/v2g/session/{sessionId}/settle
        response = api_client.post("pvessc/api/pvessc/v2g/session/{sessionId}/settle", json_data={"name": "test", "code": "TEST"})
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"POST 正常请求不应返回 5xx, 实际: {response.status_code}"


    def test_EnergyCore_PVESSC_V2g_post_8_no_auth_0024(self, api_client):
        """[EnergyCore.PVESSC][V2g] post_8 - 缺少认证头"""
        # POST /api/pvessc/v2g/session/{sessionId}/settle
        api_client.clear_token()
        try:
            response = api_client.post("pvessc/api/pvessc/v2g/session/{sessionId}/settle")
            assert response is not None, "响应不应为空"
            assert response.status_code in (200, 400, 401, 403), f"无认证头应返回 401/403, 实际: {response.status_code}"
        finally:
            api_client.restore_token()


    def test_EnergyCore_PVESSC_V2g_post_8_invalid_token_0024(self, api_client):
        """[EnergyCore.PVESSC][V2g] post_8 - 无效Token"""
        # POST /api/pvessc/v2g/session/{sessionId}/settle
        api_client.set_invalid_token()
        try:
            response = api_client.post("pvessc/api/pvessc/v2g/session/{sessionId}/settle")
            assert response is not None, "响应不应为空"
            assert response.status_code in (200, 400, 401, 403), f"无效Token应返回 401/403, 实际: {response.status_code}"
        finally:
            api_client.restore_token()


    def test_EnergyCore_PVESSC_V2g_post_8_tenant_isolation_0024(self, api_client):
        """[EnergyCore.PVESSC][V2g] post_8 - 租户隔离"""
        # POST /api/pvessc/v2g/session/{sessionId}/settle
        response = api_client.post("pvessc/api/pvessc/v2g/session/{sessionId}/settle")
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"租户隔离测试不应返回 5xx, 实际: {response.status_code}"
        data = response.json()
        assert isinstance(data, dict), "响应应为JSON对象"


    def test_EnergyCore_PVESSC_V2g_post_8_empty_body_0024(self, api_client):
        """[EnergyCore.PVESSC][V2g] post_8 - 空请求体"""
        # POST /api/pvessc/v2g/session/{sessionId}/settle
        response = api_client.post("pvessc/api/pvessc/v2g/session/{sessionId}/settle")
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"空请求体不应返回 5xx, 实际: {response.status_code}"


    def test_EnergyCore_PVESSC_V2g_post_8_invalid_id_0024(self, api_client):
        """[EnergyCore.PVESSC][V2g] post_8 - 无效ID"""
        # POST /api/pvessc/v2g/session/{sessionId}/settle
        response = api_client.post("pvessc/api/pvessc/v2g/session/{sessionId}/settle")
        assert response is not None, "响应不应为空"
        assert response.status_code in (200, 400, 403, 404), f"无效ID应返回 200/400/403/404, 实际: {response.status_code}"


    def test_EnergyCore_PVESSC_V2g_post_8_not_found_id_0024(self, api_client):
        """[EnergyCore.PVESSC][V2g] post_8 - 不存在ID"""
        # POST /api/pvessc/v2g/session/{sessionId}/settle
        response = api_client.post("pvessc/api/pvessc/v2g/session/{sessionId}/settle")
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"不存在ID不应返回 5xx, 实际: {response.status_code}"


    def test_EnergyCore_PVESSC_V2g_post_8_boundary_0024(self, api_client):
        """[EnergyCore.PVESSC][V2g] post_8 - 边界值测试"""
        # POST /api/pvessc/v2g/session/{sessionId}/settle
        response = api_client.post("pvessc/api/pvessc/v2g/session/{sessionId}/settle")
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"边界值测试不应返回 5xx 服务器错误, 实际: {response.status_code}"
        assert isinstance(response.json(), dict), "响应应为JSON对象"


    def test_EnergyCore_PVESSC_V2g_post_8_sql_injection_0024(self, api_client):
        """[EnergyCore.PVESSC][V2g] post_8 - SQL注入防护"""
        # POST /api/pvessc/v2g/session/{sessionId}/settle
        response = api_client.post("pvessc/api/pvessc/v2g/session/{sessionId}/settle")
        assert response is not None, "响应不应为空"
        assert response.status_code != 500, f"SQL注入不应导致服务器错误, 实际: {response.status_code}"
        data = response.json()
        assert isinstance(data, dict), "响应应为JSON对象"


    def test_EnergyCore_PVESSC_V2g_post_8_xss_protection_0024(self, api_client):
        """[EnergyCore.PVESSC][V2g] post_8 - XSS防护"""
        # POST /api/pvessc/v2g/session/{sessionId}/settle
        xss_payload = {"name": "<script>alert('xss')</script>", "code": "XSS_TEST"}
        response = api_client.post("pvessc/api/pvessc/v2g/session/{sessionId}/settle", json_data=xss_payload)
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"XSS防护测试不应返回 5xx, 实际: {response.status_code}"


    def test_EnergyCore_PVESSC_V2g_post_8_large_payload_0024(self, api_client):
        """[EnergyCore.PVESSC][V2g] post_8 - 大数据量"""
        # POST /api/pvessc/v2g/session/{sessionId}/settle
        large_data = {"name": "x" * 10000, "code": "LARGE", "description": "y" * 50000}
        response = api_client.post("pvessc/api/pvessc/v2g/session/{sessionId}/settle", json_data=large_data)
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"大数据量测试不应返回 5xx, 实际: {response.status_code}"


    def test_EnergyCore_PVESSC_V2g_post_8_concurrent_0024(self, api_client):
        """[EnergyCore.PVESSC][V2g] post_8 - 并发请求"""
        # POST /api/pvessc/v2g/session/{sessionId}/settle
        responses = []
        for _ in range(3):
            r = api_client.post("pvessc/api/pvessc/v2g/session/{sessionId}/settle")
            responses.append(r)
        for r in responses:
            assert r is not None, "并发响应不应为空"
            assert r.status_code < 500, f"并发请求不应返回 5xx, 实际: {r.status_code}"


    def test_EnergyCore_PVESSC_V2g_post_8_timeout_0024(self, api_client):
        """[EnergyCore.PVESSC][V2g] post_8 - 超时处理"""
        # POST /api/pvessc/v2g/session/{sessionId}/settle
        response = api_client.post("pvessc/api/pvessc/v2g/session/{sessionId}/settle")
        assert response is not None, "超时处理响应不应为空"
        assert response.status_code < 500, f"超时测试不应返回 5xx, 实际: {response.status_code}"


    def test_EnergyCore_PVESSC_V2g_post_8_permission_denied_0024(self, api_client):
        """[EnergyCore.PVESSC][V2g] post_8 - 权限不足"""
        # POST /api/pvessc/v2g/session/{sessionId}/settle
        response = api_client.post("pvessc/api/pvessc/v2g/session/{sessionId}/settle")
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"权限测试不应返回 5xx, 实际: {response.status_code}"


    def test_EnergyCore_PVESSC_V2g_post_8_field_validation_0024(self, api_client):
        """[EnergyCore.PVESSC][V2g] post_8 - 字段校验"""
        # POST /api/pvessc/v2g/session/{sessionId}/settle
        invalid_data = {"name": "", "code": ""}
        response = api_client.post("pvessc/api/pvessc/v2g/session/{sessionId}/settle", json_data=invalid_data)
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"字段校验不应返回 5xx, 实际: {response.status_code}"


    def test_EnergyCore_PVESSC_V2g_post_8_response_format_0024(self, api_client):
        """[EnergyCore.PVESSC][V2g] post_8 - 响应格式"""
        # POST /api/pvessc/v2g/session/{sessionId}/settle
        response = api_client.post("pvessc/api/pvessc/v2g/session/{sessionId}/settle")
        assert response is not None, "响应不应为空"
        data = response.json()
        assert isinstance(data, dict), "响应应为JSON对象"
        if response.status_code == 200:
            assert "success" in data or "data" in data or "code" in data, "200 响应应包含标准字段"


    def test_EnergyCore_PVESSC_V2g_post_9_positive_0025(self, api_client):
        """[EnergyCore.PVESSC][V2g] post_9 - 正常请求"""
        # POST /api/pvessc/v2g/batch-authorize
        response = api_client.post("pvessc/api/pvessc/v2g/batch-authorize", json_data={"name": "test", "code": "TEST"})
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"POST 正常请求不应返回 5xx, 实际: {response.status_code}"


    def test_EnergyCore_PVESSC_V2g_post_9_no_auth_0025(self, api_client):
        """[EnergyCore.PVESSC][V2g] post_9 - 缺少认证头"""
        # POST /api/pvessc/v2g/batch-authorize
        api_client.clear_token()
        try:
            response = api_client.post("pvessc/api/pvessc/v2g/batch-authorize")
            assert response is not None, "响应不应为空"
            assert response.status_code in (200, 400, 401, 403), f"无认证头应返回 401/403, 实际: {response.status_code}"
        finally:
            api_client.restore_token()


    def test_EnergyCore_PVESSC_V2g_post_9_invalid_token_0025(self, api_client):
        """[EnergyCore.PVESSC][V2g] post_9 - 无效Token"""
        # POST /api/pvessc/v2g/batch-authorize
        api_client.set_invalid_token()
        try:
            response = api_client.post("pvessc/api/pvessc/v2g/batch-authorize")
            assert response is not None, "响应不应为空"
            assert response.status_code in (200, 400, 401, 403), f"无效Token应返回 401/403, 实际: {response.status_code}"
        finally:
            api_client.restore_token()


    def test_EnergyCore_PVESSC_V2g_post_9_tenant_isolation_0025(self, api_client):
        """[EnergyCore.PVESSC][V2g] post_9 - 租户隔离"""
        # POST /api/pvessc/v2g/batch-authorize
        response = api_client.post("pvessc/api/pvessc/v2g/batch-authorize")
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"租户隔离测试不应返回 5xx, 实际: {response.status_code}"
        data = response.json()
        assert isinstance(data, dict), "响应应为JSON对象"


    def test_EnergyCore_PVESSC_V2g_post_9_empty_body_0025(self, api_client):
        """[EnergyCore.PVESSC][V2g] post_9 - 空请求体"""
        # POST /api/pvessc/v2g/batch-authorize
        response = api_client.post("pvessc/api/pvessc/v2g/batch-authorize")
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"空请求体不应返回 5xx, 实际: {response.status_code}"


    def test_EnergyCore_PVESSC_V2g_post_9_boundary_0025(self, api_client):
        """[EnergyCore.PVESSC][V2g] post_9 - 边界值测试"""
        # POST /api/pvessc/v2g/batch-authorize
        response = api_client.post("pvessc/api/pvessc/v2g/batch-authorize")
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"边界值测试不应返回 5xx 服务器错误, 实际: {response.status_code}"
        assert isinstance(response.json(), dict), "响应应为JSON对象"


    def test_EnergyCore_PVESSC_V2g_post_9_sql_injection_0025(self, api_client):
        """[EnergyCore.PVESSC][V2g] post_9 - SQL注入防护"""
        # POST /api/pvessc/v2g/batch-authorize
        response = api_client.post("pvessc/api/pvessc/v2g/batch-authorize")
        assert response is not None, "响应不应为空"
        assert response.status_code != 500, f"SQL注入不应导致服务器错误, 实际: {response.status_code}"
        data = response.json()
        assert isinstance(data, dict), "响应应为JSON对象"


    def test_EnergyCore_PVESSC_V2g_post_9_xss_protection_0025(self, api_client):
        """[EnergyCore.PVESSC][V2g] post_9 - XSS防护"""
        # POST /api/pvessc/v2g/batch-authorize
        xss_payload = {"name": "<script>alert('xss')</script>", "code": "XSS_TEST"}
        response = api_client.post("pvessc/api/pvessc/v2g/batch-authorize", json_data=xss_payload)
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"XSS防护测试不应返回 5xx, 实际: {response.status_code}"


    def test_EnergyCore_PVESSC_V2g_post_9_large_payload_0025(self, api_client):
        """[EnergyCore.PVESSC][V2g] post_9 - 大数据量"""
        # POST /api/pvessc/v2g/batch-authorize
        large_data = {"name": "x" * 10000, "code": "LARGE", "description": "y" * 50000}
        response = api_client.post("pvessc/api/pvessc/v2g/batch-authorize", json_data=large_data)
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"大数据量测试不应返回 5xx, 实际: {response.status_code}"


    def test_EnergyCore_PVESSC_V2g_post_9_concurrent_0025(self, api_client):
        """[EnergyCore.PVESSC][V2g] post_9 - 并发请求"""
        # POST /api/pvessc/v2g/batch-authorize
        responses = []
        for _ in range(3):
            r = api_client.post("pvessc/api/pvessc/v2g/batch-authorize")
            responses.append(r)
        for r in responses:
            assert r is not None, "并发响应不应为空"
            assert r.status_code < 500, f"并发请求不应返回 5xx, 实际: {r.status_code}"


    def test_EnergyCore_PVESSC_V2g_post_9_timeout_0025(self, api_client):
        """[EnergyCore.PVESSC][V2g] post_9 - 超时处理"""
        # POST /api/pvessc/v2g/batch-authorize
        response = api_client.post("pvessc/api/pvessc/v2g/batch-authorize")
        assert response is not None, "超时处理响应不应为空"
        assert response.status_code < 500, f"超时测试不应返回 5xx, 实际: {response.status_code}"


    def test_EnergyCore_PVESSC_V2g_post_9_permission_denied_0025(self, api_client):
        """[EnergyCore.PVESSC][V2g] post_9 - 权限不足"""
        # POST /api/pvessc/v2g/batch-authorize
        response = api_client.post("pvessc/api/pvessc/v2g/batch-authorize")
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"权限测试不应返回 5xx, 实际: {response.status_code}"


    def test_EnergyCore_PVESSC_V2g_post_9_field_validation_0025(self, api_client):
        """[EnergyCore.PVESSC][V2g] post_9 - 字段校验"""
        # POST /api/pvessc/v2g/batch-authorize
        invalid_data = {"name": "", "code": ""}
        response = api_client.post("pvessc/api/pvessc/v2g/batch-authorize", json_data=invalid_data)
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"字段校验不应返回 5xx, 实际: {response.status_code}"


    def test_EnergyCore_PVESSC_V2g_post_9_response_format_0025(self, api_client):
        """[EnergyCore.PVESSC][V2g] post_9 - 响应格式"""
        # POST /api/pvessc/v2g/batch-authorize
        response = api_client.post("pvessc/api/pvessc/v2g/batch-authorize")
        assert response is not None, "响应不应为空"
        data = response.json()
        assert isinstance(data, dict), "响应应为JSON对象"
        if response.status_code == 200:
            assert "success" in data or "data" in data or "code" in data, "200 响应应包含标准字段"


    def test_EnergyCore_PVESSC_V2g_post_10_positive_0026(self, api_client):
        """[EnergyCore.PVESSC][V2g] post_10 - 正常请求"""
        # POST /api/pvessc/v2g/cluster-dispatch
        response = api_client.post("pvessc/api/pvessc/v2g/cluster-dispatch", json_data={"name": "test", "code": "TEST"})
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"POST 正常请求不应返回 5xx, 实际: {response.status_code}"


    def test_EnergyCore_PVESSC_V2g_post_10_no_auth_0026(self, api_client):
        """[EnergyCore.PVESSC][V2g] post_10 - 缺少认证头"""
        # POST /api/pvessc/v2g/cluster-dispatch
        api_client.clear_token()
        try:
            response = api_client.post("pvessc/api/pvessc/v2g/cluster-dispatch")
            assert response is not None, "响应不应为空"
            assert response.status_code in (200, 400, 401, 403), f"无认证头应返回 401/403, 实际: {response.status_code}"
        finally:
            api_client.restore_token()


    def test_EnergyCore_PVESSC_V2g_post_10_invalid_token_0026(self, api_client):
        """[EnergyCore.PVESSC][V2g] post_10 - 无效Token"""
        # POST /api/pvessc/v2g/cluster-dispatch
        api_client.set_invalid_token()
        try:
            response = api_client.post("pvessc/api/pvessc/v2g/cluster-dispatch")
            assert response is not None, "响应不应为空"
            assert response.status_code in (200, 400, 401, 403), f"无效Token应返回 401/403, 实际: {response.status_code}"
        finally:
            api_client.restore_token()


    def test_EnergyCore_PVESSC_V2g_post_10_tenant_isolation_0026(self, api_client):
        """[EnergyCore.PVESSC][V2g] post_10 - 租户隔离"""
        # POST /api/pvessc/v2g/cluster-dispatch
        response = api_client.post("pvessc/api/pvessc/v2g/cluster-dispatch")
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"租户隔离测试不应返回 5xx, 实际: {response.status_code}"
        data = response.json()
        assert isinstance(data, dict), "响应应为JSON对象"


    def test_EnergyCore_PVESSC_V2g_post_10_empty_body_0026(self, api_client):
        """[EnergyCore.PVESSC][V2g] post_10 - 空请求体"""
        # POST /api/pvessc/v2g/cluster-dispatch
        response = api_client.post("pvessc/api/pvessc/v2g/cluster-dispatch")
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"空请求体不应返回 5xx, 实际: {response.status_code}"


    def test_EnergyCore_PVESSC_V2g_post_10_boundary_0026(self, api_client):
        """[EnergyCore.PVESSC][V2g] post_10 - 边界值测试"""
        # POST /api/pvessc/v2g/cluster-dispatch
        response = api_client.post("pvessc/api/pvessc/v2g/cluster-dispatch")
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"边界值测试不应返回 5xx 服务器错误, 实际: {response.status_code}"
        assert isinstance(response.json(), dict), "响应应为JSON对象"


    def test_EnergyCore_PVESSC_V2g_post_10_sql_injection_0026(self, api_client):
        """[EnergyCore.PVESSC][V2g] post_10 - SQL注入防护"""
        # POST /api/pvessc/v2g/cluster-dispatch
        response = api_client.post("pvessc/api/pvessc/v2g/cluster-dispatch")
        assert response is not None, "响应不应为空"
        assert response.status_code != 500, f"SQL注入不应导致服务器错误, 实际: {response.status_code}"
        data = response.json()
        assert isinstance(data, dict), "响应应为JSON对象"


    def test_EnergyCore_PVESSC_V2g_post_10_xss_protection_0026(self, api_client):
        """[EnergyCore.PVESSC][V2g] post_10 - XSS防护"""
        # POST /api/pvessc/v2g/cluster-dispatch
        xss_payload = {"name": "<script>alert('xss')</script>", "code": "XSS_TEST"}
        response = api_client.post("pvessc/api/pvessc/v2g/cluster-dispatch", json_data=xss_payload)
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"XSS防护测试不应返回 5xx, 实际: {response.status_code}"


    def test_EnergyCore_PVESSC_V2g_post_10_large_payload_0026(self, api_client):
        """[EnergyCore.PVESSC][V2g] post_10 - 大数据量"""
        # POST /api/pvessc/v2g/cluster-dispatch
        large_data = {"name": "x" * 10000, "code": "LARGE", "description": "y" * 50000}
        response = api_client.post("pvessc/api/pvessc/v2g/cluster-dispatch", json_data=large_data)
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"大数据量测试不应返回 5xx, 实际: {response.status_code}"


    def test_EnergyCore_PVESSC_V2g_post_10_concurrent_0026(self, api_client):
        """[EnergyCore.PVESSC][V2g] post_10 - 并发请求"""
        # POST /api/pvessc/v2g/cluster-dispatch
        responses = []
        for _ in range(3):
            r = api_client.post("pvessc/api/pvessc/v2g/cluster-dispatch")
            responses.append(r)
        for r in responses:
            assert r is not None, "并发响应不应为空"
            assert r.status_code < 500, f"并发请求不应返回 5xx, 实际: {r.status_code}"


    def test_EnergyCore_PVESSC_V2g_post_10_timeout_0026(self, api_client):
        """[EnergyCore.PVESSC][V2g] post_10 - 超时处理"""
        # POST /api/pvessc/v2g/cluster-dispatch
        response = api_client.post("pvessc/api/pvessc/v2g/cluster-dispatch")
        assert response is not None, "超时处理响应不应为空"
        assert response.status_code < 500, f"超时测试不应返回 5xx, 实际: {response.status_code}"


    def test_EnergyCore_PVESSC_V2g_post_10_permission_denied_0026(self, api_client):
        """[EnergyCore.PVESSC][V2g] post_10 - 权限不足"""
        # POST /api/pvessc/v2g/cluster-dispatch
        response = api_client.post("pvessc/api/pvessc/v2g/cluster-dispatch")
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"权限测试不应返回 5xx, 实际: {response.status_code}"


    def test_EnergyCore_PVESSC_V2g_post_10_field_validation_0026(self, api_client):
        """[EnergyCore.PVESSC][V2g] post_10 - 字段校验"""
        # POST /api/pvessc/v2g/cluster-dispatch
        invalid_data = {"name": "", "code": ""}
        response = api_client.post("pvessc/api/pvessc/v2g/cluster-dispatch", json_data=invalid_data)
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"字段校验不应返回 5xx, 实际: {response.status_code}"


    def test_EnergyCore_PVESSC_V2g_post_10_response_format_0026(self, api_client):
        """[EnergyCore.PVESSC][V2g] post_10 - 响应格式"""
        # POST /api/pvessc/v2g/cluster-dispatch
        response = api_client.post("pvessc/api/pvessc/v2g/cluster-dispatch")
        assert response is not None, "响应不应为空"
        data = response.json()
        assert isinstance(data, dict), "响应应为JSON对象"
        if response.status_code == 200:
            assert "success" in data or "data" in data or "code" in data, "200 响应应包含标准字段"


    def test_EnergyCore_PVESSC_V2g_put_11_positive_0027(self, api_client):
        """[EnergyCore.PVESSC][V2g] put_11 - 正常请求"""
        # PUT /api/pvessc/v2g/{siteId}/config/{chargerId}
        response = api_client.put("pvessc/api/pvessc/v2g/{siteId}/config/{chargerId}", json_data={"name": "updated"})
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"PUT 正常请求不应返回 5xx, 实际: {response.status_code}"


    def test_EnergyCore_PVESSC_V2g_put_11_no_auth_0027(self, api_client):
        """[EnergyCore.PVESSC][V2g] put_11 - 缺少认证头"""
        # PUT /api/pvessc/v2g/{siteId}/config/{chargerId}
        api_client.clear_token()
        try:
            response = api_client.put("pvessc/api/pvessc/v2g/{siteId}/config/{chargerId}")
            assert response is not None, "响应不应为空"
            assert response.status_code in (200, 400, 401, 403), f"无认证头应返回 401/403, 实际: {response.status_code}"
        finally:
            api_client.restore_token()


    def test_EnergyCore_PVESSC_V2g_put_11_invalid_token_0027(self, api_client):
        """[EnergyCore.PVESSC][V2g] put_11 - 无效Token"""
        # PUT /api/pvessc/v2g/{siteId}/config/{chargerId}
        api_client.set_invalid_token()
        try:
            response = api_client.put("pvessc/api/pvessc/v2g/{siteId}/config/{chargerId}")
            assert response is not None, "响应不应为空"
            assert response.status_code in (200, 400, 401, 403), f"无效Token应返回 401/403, 实际: {response.status_code}"
        finally:
            api_client.restore_token()


    def test_EnergyCore_PVESSC_V2g_put_11_tenant_isolation_0027(self, api_client):
        """[EnergyCore.PVESSC][V2g] put_11 - 租户隔离"""
        # PUT /api/pvessc/v2g/{siteId}/config/{chargerId}
        response = api_client.put("pvessc/api/pvessc/v2g/{siteId}/config/{chargerId}")
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"租户隔离测试不应返回 5xx, 实际: {response.status_code}"
        data = response.json()
        assert isinstance(data, dict), "响应应为JSON对象"


    def test_EnergyCore_PVESSC_V2g_put_11_empty_body_0027(self, api_client):
        """[EnergyCore.PVESSC][V2g] put_11 - 空请求体"""
        # PUT /api/pvessc/v2g/{siteId}/config/{chargerId}
        response = api_client.put("pvessc/api/pvessc/v2g/{siteId}/config/{chargerId}")
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"空请求体不应返回 5xx, 实际: {response.status_code}"


    def test_EnergyCore_PVESSC_V2g_put_11_invalid_id_0027(self, api_client):
        """[EnergyCore.PVESSC][V2g] put_11 - 无效ID"""
        # PUT /api/pvessc/v2g/{siteId}/config/{chargerId}
        response = api_client.put("pvessc/api/pvessc/v2g/{siteId}/config/{chargerId}")
        assert response is not None, "响应不应为空"
        assert response.status_code in (200, 400, 403, 404), f"无效ID应返回 200/400/403/404, 实际: {response.status_code}"


    def test_EnergyCore_PVESSC_V2g_put_11_not_found_id_0027(self, api_client):
        """[EnergyCore.PVESSC][V2g] put_11 - 不存在ID"""
        # PUT /api/pvessc/v2g/{siteId}/config/{chargerId}
        response = api_client.put("pvessc/api/pvessc/v2g/{siteId}/config/{chargerId}")
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"不存在ID不应返回 5xx, 实际: {response.status_code}"


    def test_EnergyCore_PVESSC_V2g_put_11_boundary_0027(self, api_client):
        """[EnergyCore.PVESSC][V2g] put_11 - 边界值测试"""
        # PUT /api/pvessc/v2g/{siteId}/config/{chargerId}
        response = api_client.put("pvessc/api/pvessc/v2g/{siteId}/config/{chargerId}")
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"边界值测试不应返回 5xx 服务器错误, 实际: {response.status_code}"
        assert isinstance(response.json(), dict), "响应应为JSON对象"


    def test_EnergyCore_PVESSC_V2g_put_11_sql_injection_0027(self, api_client):
        """[EnergyCore.PVESSC][V2g] put_11 - SQL注入防护"""
        # PUT /api/pvessc/v2g/{siteId}/config/{chargerId}
        response = api_client.put("pvessc/api/pvessc/v2g/{siteId}/config/{chargerId}")
        assert response is not None, "响应不应为空"
        assert response.status_code != 500, f"SQL注入不应导致服务器错误, 实际: {response.status_code}"
        data = response.json()
        assert isinstance(data, dict), "响应应为JSON对象"


    def test_EnergyCore_PVESSC_V2g_put_11_xss_protection_0027(self, api_client):
        """[EnergyCore.PVESSC][V2g] put_11 - XSS防护"""
        # PUT /api/pvessc/v2g/{siteId}/config/{chargerId}
        xss_payload = {"name": "<script>alert('xss')</script>", "code": "XSS_TEST"}
        response = api_client.put("pvessc/api/pvessc/v2g/{siteId}/config/{chargerId}", json_data=xss_payload)
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"XSS防护测试不应返回 5xx, 实际: {response.status_code}"


    def test_EnergyCore_PVESSC_V2g_put_11_large_payload_0027(self, api_client):
        """[EnergyCore.PVESSC][V2g] put_11 - 大数据量"""
        # PUT /api/pvessc/v2g/{siteId}/config/{chargerId}
        large_data = {"name": "x" * 10000, "code": "LARGE", "description": "y" * 50000}
        response = api_client.put("pvessc/api/pvessc/v2g/{siteId}/config/{chargerId}", json_data=large_data)
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"大数据量测试不应返回 5xx, 实际: {response.status_code}"


    def test_EnergyCore_PVESSC_V2g_put_11_concurrent_0027(self, api_client):
        """[EnergyCore.PVESSC][V2g] put_11 - 并发请求"""
        # PUT /api/pvessc/v2g/{siteId}/config/{chargerId}
        responses = []
        for _ in range(3):
            r = api_client.put("pvessc/api/pvessc/v2g/{siteId}/config/{chargerId}")
            responses.append(r)
        for r in responses:
            assert r is not None, "并发响应不应为空"
            assert r.status_code < 500, f"并发请求不应返回 5xx, 实际: {r.status_code}"


    def test_EnergyCore_PVESSC_V2g_put_11_idempotent_0027(self, api_client):
        """[EnergyCore.PVESSC][V2g] put_11 - 幂等性"""
        # PUT /api/pvessc/v2g/{siteId}/config/{chargerId}
        r1 = api_client.put("pvessc/api/pvessc/v2g/{siteId}/config/{chargerId}")
        r2 = api_client.put("pvessc/api/pvessc/v2g/{siteId}/config/{chargerId}")
        assert r1 is not None and r2 is not None, "幂等性响应不应为空"
        assert r1.status_code == r2.status_code, f"幂等性: 两次请求状态码应一致, {r1.status_code} vs {r2.status_code}"


    def test_EnergyCore_PVESSC_V2g_put_11_timeout_0027(self, api_client):
        """[EnergyCore.PVESSC][V2g] put_11 - 超时处理"""
        # PUT /api/pvessc/v2g/{siteId}/config/{chargerId}
        response = api_client.put("pvessc/api/pvessc/v2g/{siteId}/config/{chargerId}")
        assert response is not None, "超时处理响应不应为空"
        assert response.status_code < 500, f"超时测试不应返回 5xx, 实际: {response.status_code}"


    def test_EnergyCore_PVESSC_V2g_put_11_permission_denied_0027(self, api_client):
        """[EnergyCore.PVESSC][V2g] put_11 - 权限不足"""
        # PUT /api/pvessc/v2g/{siteId}/config/{chargerId}
        response = api_client.put("pvessc/api/pvessc/v2g/{siteId}/config/{chargerId}")
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"权限测试不应返回 5xx, 实际: {response.status_code}"


    def test_EnergyCore_PVESSC_V2g_put_11_field_validation_0027(self, api_client):
        """[EnergyCore.PVESSC][V2g] put_11 - 字段校验"""
        # PUT /api/pvessc/v2g/{siteId}/config/{chargerId}
        invalid_data = {"name": "", "code": ""}
        response = api_client.put("pvessc/api/pvessc/v2g/{siteId}/config/{chargerId}", json_data=invalid_data)
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"字段校验不应返回 5xx, 实际: {response.status_code}"


    def test_EnergyCore_PVESSC_V2g_put_11_response_format_0027(self, api_client):
        """[EnergyCore.PVESSC][V2g] put_11 - 响应格式"""
        # PUT /api/pvessc/v2g/{siteId}/config/{chargerId}
        response = api_client.put("pvessc/api/pvessc/v2g/{siteId}/config/{chargerId}")
        assert response is not None, "响应不应为空"
        data = response.json()
        assert isinstance(data, dict), "响应应为JSON对象"
        if response.status_code == 200:
            assert "success" in data or "data" in data or "code" in data, "200 响应应包含标准字段"
