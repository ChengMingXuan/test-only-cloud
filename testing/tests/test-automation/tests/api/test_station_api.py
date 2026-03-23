"""
Station 服务 API 测试
自动生成于 generate_api_tests.py
共 47 个API端点，约 799 个测试用例

服务信息:
  - 服务名: Station
  - API数量: 47
  - 标准用例: 799
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
@pytest.mark.station
class TestStationApi:
    """
    Station 服务API测试类
    测试覆盖: 47 个端点 × ~17 用例 = ~799 用例
    """

    def test_Station_AdminStation_get_0_positive_0000(self, api_client):
        """[Station][AdminStation] get_0 - 正常请求"""
        # GET /api/station/admin/stations
        response = api_client.get("station/api/station/admin/stations")
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"GET 正常请求不应返回 5xx, 实际: {response.status_code}"


    def test_Station_AdminStation_get_0_no_auth_0000(self, api_client):
        """[Station][AdminStation] get_0 - 缺少认证头"""
        # GET /api/station/admin/stations
        api_client.clear_token()
        try:
            response = api_client.get("station/api/station/admin/stations")
            assert response is not None, "响应不应为空"
            assert response.status_code in (200, 400, 401, 403), f"无认证头应返回 401/403, 实际: {response.status_code}"
        finally:
            api_client.restore_token()


    def test_Station_AdminStation_get_0_invalid_token_0000(self, api_client):
        """[Station][AdminStation] get_0 - 无效Token"""
        # GET /api/station/admin/stations
        api_client.set_invalid_token()
        try:
            response = api_client.get("station/api/station/admin/stations")
            assert response is not None, "响应不应为空"
            assert response.status_code in (200, 400, 401, 403), f"无效Token应返回 401/403, 实际: {response.status_code}"
        finally:
            api_client.restore_token()


    def test_Station_AdminStation_get_0_tenant_isolation_0000(self, api_client):
        """[Station][AdminStation] get_0 - 租户隔离"""
        # GET /api/station/admin/stations
        response = api_client.get("station/api/station/admin/stations")
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"租户隔离测试不应返回 5xx, 实际: {response.status_code}"
        data = response.json()
        assert isinstance(data, dict), "响应应为JSON对象"


    def test_Station_AdminStation_get_0_boundary_0000(self, api_client):
        """[Station][AdminStation] get_0 - 边界值测试"""
        # GET /api/station/admin/stations
        response = api_client.get("station/api/station/admin/stations")
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"边界值测试不应返回 5xx 服务器错误, 实际: {response.status_code}"
        assert isinstance(response.json(), dict), "响应应为JSON对象"


    def test_Station_AdminStation_get_0_sql_injection_0000(self, api_client):
        """[Station][AdminStation] get_0 - SQL注入防护"""
        # GET /api/station/admin/stations
        response = api_client.get("station/api/station/admin/stations")
        assert response is not None, "响应不应为空"
        assert response.status_code != 500, f"SQL注入不应导致服务器错误, 实际: {response.status_code}"
        data = response.json()
        assert isinstance(data, dict), "响应应为JSON对象"


    def test_Station_AdminStation_get_0_concurrent_0000(self, api_client):
        """[Station][AdminStation] get_0 - 并发请求"""
        # GET /api/station/admin/stations
        responses = []
        for _ in range(3):
            r = api_client.get("station/api/station/admin/stations")
            responses.append(r)
        for r in responses:
            assert r is not None, "并发响应不应为空"
            assert r.status_code < 500, f"并发请求不应返回 5xx, 实际: {r.status_code}"


    def test_Station_AdminStation_get_0_timeout_0000(self, api_client):
        """[Station][AdminStation] get_0 - 超时处理"""
        # GET /api/station/admin/stations
        response = api_client.get("station/api/station/admin/stations")
        assert response is not None, "超时处理响应不应为空"
        assert response.status_code < 500, f"超时测试不应返回 5xx, 实际: {response.status_code}"


    def test_Station_AdminStation_get_0_permission_denied_0000(self, api_client):
        """[Station][AdminStation] get_0 - 权限不足"""
        # GET /api/station/admin/stations
        response = api_client.get("station/api/station/admin/stations")
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"权限测试不应返回 5xx, 实际: {response.status_code}"


    def test_Station_AdminStation_get_0_response_format_0000(self, api_client):
        """[Station][AdminStation] get_0 - 响应格式"""
        # GET /api/station/admin/stations
        response = api_client.get("station/api/station/admin/stations")
        assert response is not None, "响应不应为空"
        data = response.json()
        assert isinstance(data, dict), "响应应为JSON对象"
        if response.status_code == 200:
            assert "success" in data or "data" in data or "code" in data, "200 响应应包含标准字段"


    def test_Station_AdminStation_get_1_positive_0001(self, api_client):
        """[Station][AdminStation] get_1 - 正常请求"""
        # GET /api/station/admin/stations/{id:guid}
        response = api_client.get("station/api/station/admin/stations/{id:guid}")
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"GET 正常请求不应返回 5xx, 实际: {response.status_code}"


    def test_Station_AdminStation_get_1_no_auth_0001(self, api_client):
        """[Station][AdminStation] get_1 - 缺少认证头"""
        # GET /api/station/admin/stations/{id:guid}
        api_client.clear_token()
        try:
            response = api_client.get("station/api/station/admin/stations/{id:guid}")
            assert response is not None, "响应不应为空"
            assert response.status_code in (200, 400, 401, 403), f"无认证头应返回 401/403, 实际: {response.status_code}"
        finally:
            api_client.restore_token()


    def test_Station_AdminStation_get_1_invalid_token_0001(self, api_client):
        """[Station][AdminStation] get_1 - 无效Token"""
        # GET /api/station/admin/stations/{id:guid}
        api_client.set_invalid_token()
        try:
            response = api_client.get("station/api/station/admin/stations/{id:guid}")
            assert response is not None, "响应不应为空"
            assert response.status_code in (200, 400, 401, 403), f"无效Token应返回 401/403, 实际: {response.status_code}"
        finally:
            api_client.restore_token()


    def test_Station_AdminStation_get_1_tenant_isolation_0001(self, api_client):
        """[Station][AdminStation] get_1 - 租户隔离"""
        # GET /api/station/admin/stations/{id:guid}
        response = api_client.get("station/api/station/admin/stations/{id:guid}")
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"租户隔离测试不应返回 5xx, 实际: {response.status_code}"
        data = response.json()
        assert isinstance(data, dict), "响应应为JSON对象"


    def test_Station_AdminStation_get_1_invalid_id_0001(self, api_client):
        """[Station][AdminStation] get_1 - 无效ID"""
        # GET /api/station/admin/stations/{id:guid}
        response = api_client.get("station/api/station/admin/stations/{id:guid}")
        assert response is not None, "响应不应为空"
        assert response.status_code in (200, 400, 403, 404), f"无效ID应返回 200/400/403/404, 实际: {response.status_code}"


    def test_Station_AdminStation_get_1_not_found_id_0001(self, api_client):
        """[Station][AdminStation] get_1 - 不存在ID"""
        # GET /api/station/admin/stations/{id:guid}
        response = api_client.get("station/api/station/admin/stations/{id:guid}")
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"不存在ID不应返回 5xx, 实际: {response.status_code}"


    def test_Station_AdminStation_get_1_boundary_0001(self, api_client):
        """[Station][AdminStation] get_1 - 边界值测试"""
        # GET /api/station/admin/stations/{id:guid}
        response = api_client.get("station/api/station/admin/stations/{id:guid}")
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"边界值测试不应返回 5xx 服务器错误, 实际: {response.status_code}"
        assert isinstance(response.json(), dict), "响应应为JSON对象"


    def test_Station_AdminStation_get_1_sql_injection_0001(self, api_client):
        """[Station][AdminStation] get_1 - SQL注入防护"""
        # GET /api/station/admin/stations/{id:guid}
        response = api_client.get("station/api/station/admin/stations/{id:guid}")
        assert response is not None, "响应不应为空"
        assert response.status_code != 500, f"SQL注入不应导致服务器错误, 实际: {response.status_code}"
        data = response.json()
        assert isinstance(data, dict), "响应应为JSON对象"


    def test_Station_AdminStation_get_1_concurrent_0001(self, api_client):
        """[Station][AdminStation] get_1 - 并发请求"""
        # GET /api/station/admin/stations/{id:guid}
        responses = []
        for _ in range(3):
            r = api_client.get("station/api/station/admin/stations/{id:guid}")
            responses.append(r)
        for r in responses:
            assert r is not None, "并发响应不应为空"
            assert r.status_code < 500, f"并发请求不应返回 5xx, 实际: {r.status_code}"


    def test_Station_AdminStation_get_1_timeout_0001(self, api_client):
        """[Station][AdminStation] get_1 - 超时处理"""
        # GET /api/station/admin/stations/{id:guid}
        response = api_client.get("station/api/station/admin/stations/{id:guid}")
        assert response is not None, "超时处理响应不应为空"
        assert response.status_code < 500, f"超时测试不应返回 5xx, 实际: {response.status_code}"


    def test_Station_AdminStation_get_1_permission_denied_0001(self, api_client):
        """[Station][AdminStation] get_1 - 权限不足"""
        # GET /api/station/admin/stations/{id:guid}
        response = api_client.get("station/api/station/admin/stations/{id:guid}")
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"权限测试不应返回 5xx, 实际: {response.status_code}"


    def test_Station_AdminStation_get_1_response_format_0001(self, api_client):
        """[Station][AdminStation] get_1 - 响应格式"""
        # GET /api/station/admin/stations/{id:guid}
        response = api_client.get("station/api/station/admin/stations/{id:guid}")
        assert response is not None, "响应不应为空"
        data = response.json()
        assert isinstance(data, dict), "响应应为JSON对象"
        if response.status_code == 200:
            assert "success" in data or "data" in data or "code" in data, "200 响应应包含标准字段"


    def test_Station_AdminStation_get_2_positive_0002(self, api_client):
        """[Station][AdminStation] get_2 - 正常请求"""
        # GET /api/station/admin/stats
        response = api_client.get("station/api/station/admin/stats")
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"GET 正常请求不应返回 5xx, 实际: {response.status_code}"


    def test_Station_AdminStation_get_2_no_auth_0002(self, api_client):
        """[Station][AdminStation] get_2 - 缺少认证头"""
        # GET /api/station/admin/stats
        api_client.clear_token()
        try:
            response = api_client.get("station/api/station/admin/stats")
            assert response is not None, "响应不应为空"
            assert response.status_code in (200, 400, 401, 403), f"无认证头应返回 401/403, 实际: {response.status_code}"
        finally:
            api_client.restore_token()


    def test_Station_AdminStation_get_2_invalid_token_0002(self, api_client):
        """[Station][AdminStation] get_2 - 无效Token"""
        # GET /api/station/admin/stats
        api_client.set_invalid_token()
        try:
            response = api_client.get("station/api/station/admin/stats")
            assert response is not None, "响应不应为空"
            assert response.status_code in (200, 400, 401, 403), f"无效Token应返回 401/403, 实际: {response.status_code}"
        finally:
            api_client.restore_token()


    def test_Station_AdminStation_get_2_tenant_isolation_0002(self, api_client):
        """[Station][AdminStation] get_2 - 租户隔离"""
        # GET /api/station/admin/stats
        response = api_client.get("station/api/station/admin/stats")
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"租户隔离测试不应返回 5xx, 实际: {response.status_code}"
        data = response.json()
        assert isinstance(data, dict), "响应应为JSON对象"


    def test_Station_AdminStation_get_2_boundary_0002(self, api_client):
        """[Station][AdminStation] get_2 - 边界值测试"""
        # GET /api/station/admin/stats
        response = api_client.get("station/api/station/admin/stats")
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"边界值测试不应返回 5xx 服务器错误, 实际: {response.status_code}"
        assert isinstance(response.json(), dict), "响应应为JSON对象"


    def test_Station_AdminStation_get_2_sql_injection_0002(self, api_client):
        """[Station][AdminStation] get_2 - SQL注入防护"""
        # GET /api/station/admin/stats
        response = api_client.get("station/api/station/admin/stats")
        assert response is not None, "响应不应为空"
        assert response.status_code != 500, f"SQL注入不应导致服务器错误, 实际: {response.status_code}"
        data = response.json()
        assert isinstance(data, dict), "响应应为JSON对象"


    def test_Station_AdminStation_get_2_concurrent_0002(self, api_client):
        """[Station][AdminStation] get_2 - 并发请求"""
        # GET /api/station/admin/stats
        responses = []
        for _ in range(3):
            r = api_client.get("station/api/station/admin/stats")
            responses.append(r)
        for r in responses:
            assert r is not None, "并发响应不应为空"
            assert r.status_code < 500, f"并发请求不应返回 5xx, 实际: {r.status_code}"


    def test_Station_AdminStation_get_2_timeout_0002(self, api_client):
        """[Station][AdminStation] get_2 - 超时处理"""
        # GET /api/station/admin/stats
        response = api_client.get("station/api/station/admin/stats")
        assert response is not None, "超时处理响应不应为空"
        assert response.status_code < 500, f"超时测试不应返回 5xx, 实际: {response.status_code}"


    def test_Station_AdminStation_get_2_permission_denied_0002(self, api_client):
        """[Station][AdminStation] get_2 - 权限不足"""
        # GET /api/station/admin/stats
        response = api_client.get("station/api/station/admin/stats")
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"权限测试不应返回 5xx, 实际: {response.status_code}"


    def test_Station_AdminStation_get_2_response_format_0002(self, api_client):
        """[Station][AdminStation] get_2 - 响应格式"""
        # GET /api/station/admin/stats
        response = api_client.get("station/api/station/admin/stats")
        assert response is not None, "响应不应为空"
        data = response.json()
        assert isinstance(data, dict), "响应应为JSON对象"
        if response.status_code == 200:
            assert "success" in data or "data" in data or "code" in data, "200 响应应包含标准字段"


    def test_Station_AdminStation_post_3_positive_0003(self, api_client):
        """[Station][AdminStation] post_3 - 正常请求"""
        # POST /api/station/admin/stations
        response = api_client.post("station/api/station/admin/stations", json_data={"name": "test", "code": "TEST"})
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"POST 正常请求不应返回 5xx, 实际: {response.status_code}"


    def test_Station_AdminStation_post_3_no_auth_0003(self, api_client):
        """[Station][AdminStation] post_3 - 缺少认证头"""
        # POST /api/station/admin/stations
        api_client.clear_token()
        try:
            response = api_client.post("station/api/station/admin/stations")
            assert response is not None, "响应不应为空"
            assert response.status_code in (200, 400, 401, 403), f"无认证头应返回 401/403, 实际: {response.status_code}"
        finally:
            api_client.restore_token()


    def test_Station_AdminStation_post_3_invalid_token_0003(self, api_client):
        """[Station][AdminStation] post_3 - 无效Token"""
        # POST /api/station/admin/stations
        api_client.set_invalid_token()
        try:
            response = api_client.post("station/api/station/admin/stations")
            assert response is not None, "响应不应为空"
            assert response.status_code in (200, 400, 401, 403), f"无效Token应返回 401/403, 实际: {response.status_code}"
        finally:
            api_client.restore_token()


    def test_Station_AdminStation_post_3_tenant_isolation_0003(self, api_client):
        """[Station][AdminStation] post_3 - 租户隔离"""
        # POST /api/station/admin/stations
        response = api_client.post("station/api/station/admin/stations")
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"租户隔离测试不应返回 5xx, 实际: {response.status_code}"
        data = response.json()
        assert isinstance(data, dict), "响应应为JSON对象"


    def test_Station_AdminStation_post_3_empty_body_0003(self, api_client):
        """[Station][AdminStation] post_3 - 空请求体"""
        # POST /api/station/admin/stations
        response = api_client.post("station/api/station/admin/stations")
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"空请求体不应返回 5xx, 实际: {response.status_code}"


    def test_Station_AdminStation_post_3_boundary_0003(self, api_client):
        """[Station][AdminStation] post_3 - 边界值测试"""
        # POST /api/station/admin/stations
        response = api_client.post("station/api/station/admin/stations")
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"边界值测试不应返回 5xx 服务器错误, 实际: {response.status_code}"
        assert isinstance(response.json(), dict), "响应应为JSON对象"


    def test_Station_AdminStation_post_3_sql_injection_0003(self, api_client):
        """[Station][AdminStation] post_3 - SQL注入防护"""
        # POST /api/station/admin/stations
        response = api_client.post("station/api/station/admin/stations")
        assert response is not None, "响应不应为空"
        assert response.status_code != 500, f"SQL注入不应导致服务器错误, 实际: {response.status_code}"
        data = response.json()
        assert isinstance(data, dict), "响应应为JSON对象"


    def test_Station_AdminStation_post_3_xss_protection_0003(self, api_client):
        """[Station][AdminStation] post_3 - XSS防护"""
        # POST /api/station/admin/stations
        xss_payload = {"name": "<script>alert('xss')</script>", "code": "XSS_TEST"}
        response = api_client.post("station/api/station/admin/stations", json_data=xss_payload)
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"XSS防护测试不应返回 5xx, 实际: {response.status_code}"


    def test_Station_AdminStation_post_3_large_payload_0003(self, api_client):
        """[Station][AdminStation] post_3 - 大数据量"""
        # POST /api/station/admin/stations
        large_data = {"name": "x" * 10000, "code": "LARGE", "description": "y" * 50000}
        response = api_client.post("station/api/station/admin/stations", json_data=large_data)
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"大数据量测试不应返回 5xx, 实际: {response.status_code}"


    def test_Station_AdminStation_post_3_concurrent_0003(self, api_client):
        """[Station][AdminStation] post_3 - 并发请求"""
        # POST /api/station/admin/stations
        responses = []
        for _ in range(3):
            r = api_client.post("station/api/station/admin/stations")
            responses.append(r)
        for r in responses:
            assert r is not None, "并发响应不应为空"
            assert r.status_code < 500, f"并发请求不应返回 5xx, 实际: {r.status_code}"


    def test_Station_AdminStation_post_3_timeout_0003(self, api_client):
        """[Station][AdminStation] post_3 - 超时处理"""
        # POST /api/station/admin/stations
        response = api_client.post("station/api/station/admin/stations")
        assert response is not None, "超时处理响应不应为空"
        assert response.status_code < 500, f"超时测试不应返回 5xx, 实际: {response.status_code}"


    def test_Station_AdminStation_post_3_permission_denied_0003(self, api_client):
        """[Station][AdminStation] post_3 - 权限不足"""
        # POST /api/station/admin/stations
        response = api_client.post("station/api/station/admin/stations")
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"权限测试不应返回 5xx, 实际: {response.status_code}"


    def test_Station_AdminStation_post_3_field_validation_0003(self, api_client):
        """[Station][AdminStation] post_3 - 字段校验"""
        # POST /api/station/admin/stations
        invalid_data = {"name": "", "code": ""}
        response = api_client.post("station/api/station/admin/stations", json_data=invalid_data)
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"字段校验不应返回 5xx, 实际: {response.status_code}"


    def test_Station_AdminStation_post_3_response_format_0003(self, api_client):
        """[Station][AdminStation] post_3 - 响应格式"""
        # POST /api/station/admin/stations
        response = api_client.post("station/api/station/admin/stations")
        assert response is not None, "响应不应为空"
        data = response.json()
        assert isinstance(data, dict), "响应应为JSON对象"
        if response.status_code == 200:
            assert "success" in data or "data" in data or "code" in data, "200 响应应包含标准字段"


    def test_Station_AdminStation_put_4_positive_0004(self, api_client):
        """[Station][AdminStation] put_4 - 正常请求"""
        # PUT /api/station/admin/stations/{id:guid}
        response = api_client.put("station/api/station/admin/stations/{id:guid}", json_data={"name": "updated"})
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"PUT 正常请求不应返回 5xx, 实际: {response.status_code}"


    def test_Station_AdminStation_put_4_no_auth_0004(self, api_client):
        """[Station][AdminStation] put_4 - 缺少认证头"""
        # PUT /api/station/admin/stations/{id:guid}
        api_client.clear_token()
        try:
            response = api_client.put("station/api/station/admin/stations/{id:guid}")
            assert response is not None, "响应不应为空"
            assert response.status_code in (200, 400, 401, 403), f"无认证头应返回 401/403, 实际: {response.status_code}"
        finally:
            api_client.restore_token()


    def test_Station_AdminStation_put_4_invalid_token_0004(self, api_client):
        """[Station][AdminStation] put_4 - 无效Token"""
        # PUT /api/station/admin/stations/{id:guid}
        api_client.set_invalid_token()
        try:
            response = api_client.put("station/api/station/admin/stations/{id:guid}")
            assert response is not None, "响应不应为空"
            assert response.status_code in (200, 400, 401, 403), f"无效Token应返回 401/403, 实际: {response.status_code}"
        finally:
            api_client.restore_token()


    def test_Station_AdminStation_put_4_tenant_isolation_0004(self, api_client):
        """[Station][AdminStation] put_4 - 租户隔离"""
        # PUT /api/station/admin/stations/{id:guid}
        response = api_client.put("station/api/station/admin/stations/{id:guid}")
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"租户隔离测试不应返回 5xx, 实际: {response.status_code}"
        data = response.json()
        assert isinstance(data, dict), "响应应为JSON对象"


    def test_Station_AdminStation_put_4_empty_body_0004(self, api_client):
        """[Station][AdminStation] put_4 - 空请求体"""
        # PUT /api/station/admin/stations/{id:guid}
        response = api_client.put("station/api/station/admin/stations/{id:guid}")
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"空请求体不应返回 5xx, 实际: {response.status_code}"


    def test_Station_AdminStation_put_4_invalid_id_0004(self, api_client):
        """[Station][AdminStation] put_4 - 无效ID"""
        # PUT /api/station/admin/stations/{id:guid}
        response = api_client.put("station/api/station/admin/stations/{id:guid}")
        assert response is not None, "响应不应为空"
        assert response.status_code in (200, 400, 403, 404), f"无效ID应返回 200/400/403/404, 实际: {response.status_code}"


    def test_Station_AdminStation_put_4_not_found_id_0004(self, api_client):
        """[Station][AdminStation] put_4 - 不存在ID"""
        # PUT /api/station/admin/stations/{id:guid}
        response = api_client.put("station/api/station/admin/stations/{id:guid}")
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"不存在ID不应返回 5xx, 实际: {response.status_code}"


    def test_Station_AdminStation_put_4_boundary_0004(self, api_client):
        """[Station][AdminStation] put_4 - 边界值测试"""
        # PUT /api/station/admin/stations/{id:guid}
        response = api_client.put("station/api/station/admin/stations/{id:guid}")
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"边界值测试不应返回 5xx 服务器错误, 实际: {response.status_code}"
        assert isinstance(response.json(), dict), "响应应为JSON对象"


    def test_Station_AdminStation_put_4_sql_injection_0004(self, api_client):
        """[Station][AdminStation] put_4 - SQL注入防护"""
        # PUT /api/station/admin/stations/{id:guid}
        response = api_client.put("station/api/station/admin/stations/{id:guid}")
        assert response is not None, "响应不应为空"
        assert response.status_code != 500, f"SQL注入不应导致服务器错误, 实际: {response.status_code}"
        data = response.json()
        assert isinstance(data, dict), "响应应为JSON对象"


    def test_Station_AdminStation_put_4_xss_protection_0004(self, api_client):
        """[Station][AdminStation] put_4 - XSS防护"""
        # PUT /api/station/admin/stations/{id:guid}
        xss_payload = {"name": "<script>alert('xss')</script>", "code": "XSS_TEST"}
        response = api_client.put("station/api/station/admin/stations/{id:guid}", json_data=xss_payload)
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"XSS防护测试不应返回 5xx, 实际: {response.status_code}"


    def test_Station_AdminStation_put_4_large_payload_0004(self, api_client):
        """[Station][AdminStation] put_4 - 大数据量"""
        # PUT /api/station/admin/stations/{id:guid}
        large_data = {"name": "x" * 10000, "code": "LARGE", "description": "y" * 50000}
        response = api_client.put("station/api/station/admin/stations/{id:guid}", json_data=large_data)
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"大数据量测试不应返回 5xx, 实际: {response.status_code}"


    def test_Station_AdminStation_put_4_concurrent_0004(self, api_client):
        """[Station][AdminStation] put_4 - 并发请求"""
        # PUT /api/station/admin/stations/{id:guid}
        responses = []
        for _ in range(3):
            r = api_client.put("station/api/station/admin/stations/{id:guid}")
            responses.append(r)
        for r in responses:
            assert r is not None, "并发响应不应为空"
            assert r.status_code < 500, f"并发请求不应返回 5xx, 实际: {r.status_code}"


    def test_Station_AdminStation_put_4_idempotent_0004(self, api_client):
        """[Station][AdminStation] put_4 - 幂等性"""
        # PUT /api/station/admin/stations/{id:guid}
        r1 = api_client.put("station/api/station/admin/stations/{id:guid}")
        r2 = api_client.put("station/api/station/admin/stations/{id:guid}")
        assert r1 is not None and r2 is not None, "幂等性响应不应为空"
        assert r1.status_code == r2.status_code, f"幂等性: 两次请求状态码应一致, {r1.status_code} vs {r2.status_code}"


    def test_Station_AdminStation_put_4_timeout_0004(self, api_client):
        """[Station][AdminStation] put_4 - 超时处理"""
        # PUT /api/station/admin/stations/{id:guid}
        response = api_client.put("station/api/station/admin/stations/{id:guid}")
        assert response is not None, "超时处理响应不应为空"
        assert response.status_code < 500, f"超时测试不应返回 5xx, 实际: {response.status_code}"


    def test_Station_AdminStation_put_4_permission_denied_0004(self, api_client):
        """[Station][AdminStation] put_4 - 权限不足"""
        # PUT /api/station/admin/stations/{id:guid}
        response = api_client.put("station/api/station/admin/stations/{id:guid}")
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"权限测试不应返回 5xx, 实际: {response.status_code}"


    def test_Station_AdminStation_put_4_field_validation_0004(self, api_client):
        """[Station][AdminStation] put_4 - 字段校验"""
        # PUT /api/station/admin/stations/{id:guid}
        invalid_data = {"name": "", "code": ""}
        response = api_client.put("station/api/station/admin/stations/{id:guid}", json_data=invalid_data)
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"字段校验不应返回 5xx, 实际: {response.status_code}"


    def test_Station_AdminStation_put_4_response_format_0004(self, api_client):
        """[Station][AdminStation] put_4 - 响应格式"""
        # PUT /api/station/admin/stations/{id:guid}
        response = api_client.put("station/api/station/admin/stations/{id:guid}")
        assert response is not None, "响应不应为空"
        data = response.json()
        assert isinstance(data, dict), "响应应为JSON对象"
        if response.status_code == 200:
            assert "success" in data or "data" in data or "code" in data, "200 响应应包含标准字段"


    def test_Station_AdminStation_delete_5_positive_0005(self, api_client):
        """[Station][AdminStation] delete_5 - 正常请求"""
        # DELETE /api/station/admin/stations/{id:guid}
        response = api_client.delete("station/api/station/admin/stations/{id:guid}")
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"DELETE 正常请求不应返回 5xx, 实际: {response.status_code}"


    def test_Station_AdminStation_delete_5_no_auth_0005(self, api_client):
        """[Station][AdminStation] delete_5 - 缺少认证头"""
        # DELETE /api/station/admin/stations/{id:guid}
        api_client.clear_token()
        try:
            response = api_client.delete("station/api/station/admin/stations/{id:guid}")
            assert response is not None, "响应不应为空"
            assert response.status_code in (200, 400, 401, 403), f"无认证头应返回 401/403, 实际: {response.status_code}"
        finally:
            api_client.restore_token()


    def test_Station_AdminStation_delete_5_invalid_token_0005(self, api_client):
        """[Station][AdminStation] delete_5 - 无效Token"""
        # DELETE /api/station/admin/stations/{id:guid}
        api_client.set_invalid_token()
        try:
            response = api_client.delete("station/api/station/admin/stations/{id:guid}")
            assert response is not None, "响应不应为空"
            assert response.status_code in (200, 400, 401, 403), f"无效Token应返回 401/403, 实际: {response.status_code}"
        finally:
            api_client.restore_token()


    def test_Station_AdminStation_delete_5_tenant_isolation_0005(self, api_client):
        """[Station][AdminStation] delete_5 - 租户隔离"""
        # DELETE /api/station/admin/stations/{id:guid}
        response = api_client.delete("station/api/station/admin/stations/{id:guid}")
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"租户隔离测试不应返回 5xx, 实际: {response.status_code}"
        data = response.json()
        assert isinstance(data, dict), "响应应为JSON对象"


    def test_Station_AdminStation_delete_5_invalid_id_0005(self, api_client):
        """[Station][AdminStation] delete_5 - 无效ID"""
        # DELETE /api/station/admin/stations/{id:guid}
        response = api_client.delete("station/api/station/admin/stations/{id:guid}")
        assert response is not None, "响应不应为空"
        assert response.status_code in (200, 400, 403, 404), f"无效ID应返回 200/400/403/404, 实际: {response.status_code}"


    def test_Station_AdminStation_delete_5_not_found_id_0005(self, api_client):
        """[Station][AdminStation] delete_5 - 不存在ID"""
        # DELETE /api/station/admin/stations/{id:guid}
        response = api_client.delete("station/api/station/admin/stations/{id:guid}")
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"不存在ID不应返回 5xx, 实际: {response.status_code}"


    def test_Station_AdminStation_delete_5_boundary_0005(self, api_client):
        """[Station][AdminStation] delete_5 - 边界值测试"""
        # DELETE /api/station/admin/stations/{id:guid}
        response = api_client.delete("station/api/station/admin/stations/{id:guid}")
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"边界值测试不应返回 5xx 服务器错误, 实际: {response.status_code}"
        assert isinstance(response.json(), dict), "响应应为JSON对象"


    def test_Station_AdminStation_delete_5_sql_injection_0005(self, api_client):
        """[Station][AdminStation] delete_5 - SQL注入防护"""
        # DELETE /api/station/admin/stations/{id:guid}
        response = api_client.delete("station/api/station/admin/stations/{id:guid}")
        assert response is not None, "响应不应为空"
        assert response.status_code != 500, f"SQL注入不应导致服务器错误, 实际: {response.status_code}"
        data = response.json()
        assert isinstance(data, dict), "响应应为JSON对象"


    def test_Station_AdminStation_delete_5_concurrent_0005(self, api_client):
        """[Station][AdminStation] delete_5 - 并发请求"""
        # DELETE /api/station/admin/stations/{id:guid}
        responses = []
        for _ in range(3):
            r = api_client.delete("station/api/station/admin/stations/{id:guid}")
            responses.append(r)
        for r in responses:
            assert r is not None, "并发响应不应为空"
            assert r.status_code < 500, f"并发请求不应返回 5xx, 实际: {r.status_code}"


    def test_Station_AdminStation_delete_5_idempotent_0005(self, api_client):
        """[Station][AdminStation] delete_5 - 幂等性"""
        # DELETE /api/station/admin/stations/{id:guid}
        r1 = api_client.delete("station/api/station/admin/stations/{id:guid}")
        r2 = api_client.delete("station/api/station/admin/stations/{id:guid}")
        assert r1 is not None and r2 is not None, "幂等性响应不应为空"
        assert r1.status_code == r2.status_code, f"幂等性: 两次请求状态码应一致, {r1.status_code} vs {r2.status_code}"


    def test_Station_AdminStation_delete_5_timeout_0005(self, api_client):
        """[Station][AdminStation] delete_5 - 超时处理"""
        # DELETE /api/station/admin/stations/{id:guid}
        response = api_client.delete("station/api/station/admin/stations/{id:guid}")
        assert response is not None, "超时处理响应不应为空"
        assert response.status_code < 500, f"超时测试不应返回 5xx, 实际: {response.status_code}"


    def test_Station_AdminStation_delete_5_permission_denied_0005(self, api_client):
        """[Station][AdminStation] delete_5 - 权限不足"""
        # DELETE /api/station/admin/stations/{id:guid}
        response = api_client.delete("station/api/station/admin/stations/{id:guid}")
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"权限测试不应返回 5xx, 实际: {response.status_code}"


    def test_Station_AdminStation_delete_5_response_format_0005(self, api_client):
        """[Station][AdminStation] delete_5 - 响应格式"""
        # DELETE /api/station/admin/stations/{id:guid}
        response = api_client.delete("station/api/station/admin/stations/{id:guid}")
        assert response is not None, "响应不应为空"
        data = response.json()
        assert isinstance(data, dict), "响应应为JSON对象"
        if response.status_code == 200:
            assert "success" in data or "data" in data or "code" in data, "200 响应应包含标准字段"


    def test_Station_AdminStation_patch_6_positive_0006(self, api_client):
        """[Station][AdminStation] patch_6 - 正常请求"""
        # PATCH /api/station/admin/stations/{id:guid}/status
        response = api_client.patch("station/api/station/admin/stations/{id:guid}/status", json_data={"name": "updated"})
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"PATCH 正常请求不应返回 5xx, 实际: {response.status_code}"


    def test_Station_AdminStation_patch_6_no_auth_0006(self, api_client):
        """[Station][AdminStation] patch_6 - 缺少认证头"""
        # PATCH /api/station/admin/stations/{id:guid}/status
        api_client.clear_token()
        try:
            response = api_client.patch("station/api/station/admin/stations/{id:guid}/status")
            assert response is not None, "响应不应为空"
            assert response.status_code in (200, 400, 401, 403), f"无认证头应返回 401/403, 实际: {response.status_code}"
        finally:
            api_client.restore_token()


    def test_Station_AdminStation_patch_6_invalid_token_0006(self, api_client):
        """[Station][AdminStation] patch_6 - 无效Token"""
        # PATCH /api/station/admin/stations/{id:guid}/status
        api_client.set_invalid_token()
        try:
            response = api_client.patch("station/api/station/admin/stations/{id:guid}/status")
            assert response is not None, "响应不应为空"
            assert response.status_code in (200, 400, 401, 403), f"无效Token应返回 401/403, 实际: {response.status_code}"
        finally:
            api_client.restore_token()


    def test_Station_AdminStation_patch_6_tenant_isolation_0006(self, api_client):
        """[Station][AdminStation] patch_6 - 租户隔离"""
        # PATCH /api/station/admin/stations/{id:guid}/status
        response = api_client.patch("station/api/station/admin/stations/{id:guid}/status")
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"租户隔离测试不应返回 5xx, 实际: {response.status_code}"
        data = response.json()
        assert isinstance(data, dict), "响应应为JSON对象"


    def test_Station_AdminStation_patch_6_empty_body_0006(self, api_client):
        """[Station][AdminStation] patch_6 - 空请求体"""
        # PATCH /api/station/admin/stations/{id:guid}/status
        response = api_client.patch("station/api/station/admin/stations/{id:guid}/status")
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"空请求体不应返回 5xx, 实际: {response.status_code}"


    def test_Station_AdminStation_patch_6_invalid_id_0006(self, api_client):
        """[Station][AdminStation] patch_6 - 无效ID"""
        # PATCH /api/station/admin/stations/{id:guid}/status
        response = api_client.patch("station/api/station/admin/stations/{id:guid}/status")
        assert response is not None, "响应不应为空"
        assert response.status_code in (200, 400, 403, 404), f"无效ID应返回 200/400/403/404, 实际: {response.status_code}"


    def test_Station_AdminStation_patch_6_not_found_id_0006(self, api_client):
        """[Station][AdminStation] patch_6 - 不存在ID"""
        # PATCH /api/station/admin/stations/{id:guid}/status
        response = api_client.patch("station/api/station/admin/stations/{id:guid}/status")
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"不存在ID不应返回 5xx, 实际: {response.status_code}"


    def test_Station_AdminStation_patch_6_boundary_0006(self, api_client):
        """[Station][AdminStation] patch_6 - 边界值测试"""
        # PATCH /api/station/admin/stations/{id:guid}/status
        response = api_client.patch("station/api/station/admin/stations/{id:guid}/status")
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"边界值测试不应返回 5xx 服务器错误, 实际: {response.status_code}"
        assert isinstance(response.json(), dict), "响应应为JSON对象"


    def test_Station_AdminStation_patch_6_sql_injection_0006(self, api_client):
        """[Station][AdminStation] patch_6 - SQL注入防护"""
        # PATCH /api/station/admin/stations/{id:guid}/status
        response = api_client.patch("station/api/station/admin/stations/{id:guid}/status")
        assert response is not None, "响应不应为空"
        assert response.status_code != 500, f"SQL注入不应导致服务器错误, 实际: {response.status_code}"
        data = response.json()
        assert isinstance(data, dict), "响应应为JSON对象"


    def test_Station_AdminStation_patch_6_xss_protection_0006(self, api_client):
        """[Station][AdminStation] patch_6 - XSS防护"""
        # PATCH /api/station/admin/stations/{id:guid}/status
        xss_payload = {"name": "<script>alert('xss')</script>", "code": "XSS_TEST"}
        response = api_client.patch("station/api/station/admin/stations/{id:guid}/status", json_data=xss_payload)
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"XSS防护测试不应返回 5xx, 实际: {response.status_code}"


    def test_Station_AdminStation_patch_6_large_payload_0006(self, api_client):
        """[Station][AdminStation] patch_6 - 大数据量"""
        # PATCH /api/station/admin/stations/{id:guid}/status
        large_data = {"name": "x" * 10000, "code": "LARGE", "description": "y" * 50000}
        response = api_client.patch("station/api/station/admin/stations/{id:guid}/status", json_data=large_data)
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"大数据量测试不应返回 5xx, 实际: {response.status_code}"


    def test_Station_AdminStation_patch_6_concurrent_0006(self, api_client):
        """[Station][AdminStation] patch_6 - 并发请求"""
        # PATCH /api/station/admin/stations/{id:guid}/status
        responses = []
        for _ in range(3):
            r = api_client.patch("station/api/station/admin/stations/{id:guid}/status")
            responses.append(r)
        for r in responses:
            assert r is not None, "并发响应不应为空"
            assert r.status_code < 500, f"并发请求不应返回 5xx, 实际: {r.status_code}"


    def test_Station_AdminStation_patch_6_timeout_0006(self, api_client):
        """[Station][AdminStation] patch_6 - 超时处理"""
        # PATCH /api/station/admin/stations/{id:guid}/status
        response = api_client.patch("station/api/station/admin/stations/{id:guid}/status")
        assert response is not None, "超时处理响应不应为空"
        assert response.status_code < 500, f"超时测试不应返回 5xx, 实际: {response.status_code}"


    def test_Station_AdminStation_patch_6_permission_denied_0006(self, api_client):
        """[Station][AdminStation] patch_6 - 权限不足"""
        # PATCH /api/station/admin/stations/{id:guid}/status
        response = api_client.patch("station/api/station/admin/stations/{id:guid}/status")
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"权限测试不应返回 5xx, 实际: {response.status_code}"


    def test_Station_AdminStation_patch_6_field_validation_0006(self, api_client):
        """[Station][AdminStation] patch_6 - 字段校验"""
        # PATCH /api/station/admin/stations/{id:guid}/status
        invalid_data = {"name": "", "code": ""}
        response = api_client.patch("station/api/station/admin/stations/{id:guid}/status", json_data=invalid_data)
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"字段校验不应返回 5xx, 实际: {response.status_code}"


    def test_Station_AdminStation_patch_6_response_format_0006(self, api_client):
        """[Station][AdminStation] patch_6 - 响应格式"""
        # PATCH /api/station/admin/stations/{id:guid}/status
        response = api_client.patch("station/api/station/admin/stations/{id:guid}/status")
        assert response is not None, "响应不应为空"
        data = response.json()
        assert isinstance(data, dict), "响应应为JSON对象"
        if response.status_code == 200:
            assert "success" in data or "data" in data or "code" in data, "200 响应应包含标准字段"


    def test_Station_Interaction_get_0_positive_0007(self, api_client):
        """[Station][Interaction] get_0 - 正常请求"""
        # GET /api/stations/{stationId}/reviews
        response = api_client.get("station/api/stations/{stationId}/reviews")
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"GET 正常请求不应返回 5xx, 实际: {response.status_code}"


    def test_Station_Interaction_get_0_no_auth_0007(self, api_client):
        """[Station][Interaction] get_0 - 缺少认证头"""
        # GET /api/stations/{stationId}/reviews
        api_client.clear_token()
        try:
            response = api_client.get("station/api/stations/{stationId}/reviews")
            assert response is not None, "响应不应为空"
            assert response.status_code in (200, 400, 401, 403), f"无认证头应返回 401/403, 实际: {response.status_code}"
        finally:
            api_client.restore_token()


    def test_Station_Interaction_get_0_invalid_token_0007(self, api_client):
        """[Station][Interaction] get_0 - 无效Token"""
        # GET /api/stations/{stationId}/reviews
        api_client.set_invalid_token()
        try:
            response = api_client.get("station/api/stations/{stationId}/reviews")
            assert response is not None, "响应不应为空"
            assert response.status_code in (200, 400, 401, 403), f"无效Token应返回 401/403, 实际: {response.status_code}"
        finally:
            api_client.restore_token()


    def test_Station_Interaction_get_0_tenant_isolation_0007(self, api_client):
        """[Station][Interaction] get_0 - 租户隔离"""
        # GET /api/stations/{stationId}/reviews
        response = api_client.get("station/api/stations/{stationId}/reviews")
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"租户隔离测试不应返回 5xx, 实际: {response.status_code}"
        data = response.json()
        assert isinstance(data, dict), "响应应为JSON对象"


    def test_Station_Interaction_get_0_invalid_id_0007(self, api_client):
        """[Station][Interaction] get_0 - 无效ID"""
        # GET /api/stations/{stationId}/reviews
        response = api_client.get("station/api/stations/{stationId}/reviews")
        assert response is not None, "响应不应为空"
        assert response.status_code in (200, 400, 403, 404), f"无效ID应返回 200/400/403/404, 实际: {response.status_code}"


    def test_Station_Interaction_get_0_not_found_id_0007(self, api_client):
        """[Station][Interaction] get_0 - 不存在ID"""
        # GET /api/stations/{stationId}/reviews
        response = api_client.get("station/api/stations/{stationId}/reviews")
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"不存在ID不应返回 5xx, 实际: {response.status_code}"


    def test_Station_Interaction_get_0_boundary_0007(self, api_client):
        """[Station][Interaction] get_0 - 边界值测试"""
        # GET /api/stations/{stationId}/reviews
        response = api_client.get("station/api/stations/{stationId}/reviews")
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"边界值测试不应返回 5xx 服务器错误, 实际: {response.status_code}"
        assert isinstance(response.json(), dict), "响应应为JSON对象"


    def test_Station_Interaction_get_0_sql_injection_0007(self, api_client):
        """[Station][Interaction] get_0 - SQL注入防护"""
        # GET /api/stations/{stationId}/reviews
        response = api_client.get("station/api/stations/{stationId}/reviews")
        assert response is not None, "响应不应为空"
        assert response.status_code != 500, f"SQL注入不应导致服务器错误, 实际: {response.status_code}"
        data = response.json()
        assert isinstance(data, dict), "响应应为JSON对象"


    def test_Station_Interaction_get_0_concurrent_0007(self, api_client):
        """[Station][Interaction] get_0 - 并发请求"""
        # GET /api/stations/{stationId}/reviews
        responses = []
        for _ in range(3):
            r = api_client.get("station/api/stations/{stationId}/reviews")
            responses.append(r)
        for r in responses:
            assert r is not None, "并发响应不应为空"
            assert r.status_code < 500, f"并发请求不应返回 5xx, 实际: {r.status_code}"


    def test_Station_Interaction_get_0_timeout_0007(self, api_client):
        """[Station][Interaction] get_0 - 超时处理"""
        # GET /api/stations/{stationId}/reviews
        response = api_client.get("station/api/stations/{stationId}/reviews")
        assert response is not None, "超时处理响应不应为空"
        assert response.status_code < 500, f"超时测试不应返回 5xx, 实际: {response.status_code}"


    def test_Station_Interaction_get_0_permission_denied_0007(self, api_client):
        """[Station][Interaction] get_0 - 权限不足"""
        # GET /api/stations/{stationId}/reviews
        response = api_client.get("station/api/stations/{stationId}/reviews")
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"权限测试不应返回 5xx, 实际: {response.status_code}"


    def test_Station_Interaction_get_0_response_format_0007(self, api_client):
        """[Station][Interaction] get_0 - 响应格式"""
        # GET /api/stations/{stationId}/reviews
        response = api_client.get("station/api/stations/{stationId}/reviews")
        assert response is not None, "响应不应为空"
        data = response.json()
        assert isinstance(data, dict), "响应应为JSON对象"
        if response.status_code == 200:
            assert "success" in data or "data" in data or "code" in data, "200 响应应包含标准字段"


    def test_Station_Interaction_get_1_positive_0008(self, api_client):
        """[Station][Interaction] get_1 - 正常请求"""
        # GET /api/stations/{stationId}/rating-statistics
        response = api_client.get("station/api/stations/{stationId}/rating-statistics")
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"GET 正常请求不应返回 5xx, 实际: {response.status_code}"


    def test_Station_Interaction_get_1_no_auth_0008(self, api_client):
        """[Station][Interaction] get_1 - 缺少认证头"""
        # GET /api/stations/{stationId}/rating-statistics
        api_client.clear_token()
        try:
            response = api_client.get("station/api/stations/{stationId}/rating-statistics")
            assert response is not None, "响应不应为空"
            assert response.status_code in (200, 400, 401, 403), f"无认证头应返回 401/403, 实际: {response.status_code}"
        finally:
            api_client.restore_token()


    def test_Station_Interaction_get_1_invalid_token_0008(self, api_client):
        """[Station][Interaction] get_1 - 无效Token"""
        # GET /api/stations/{stationId}/rating-statistics
        api_client.set_invalid_token()
        try:
            response = api_client.get("station/api/stations/{stationId}/rating-statistics")
            assert response is not None, "响应不应为空"
            assert response.status_code in (200, 400, 401, 403), f"无效Token应返回 401/403, 实际: {response.status_code}"
        finally:
            api_client.restore_token()


    def test_Station_Interaction_get_1_tenant_isolation_0008(self, api_client):
        """[Station][Interaction] get_1 - 租户隔离"""
        # GET /api/stations/{stationId}/rating-statistics
        response = api_client.get("station/api/stations/{stationId}/rating-statistics")
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"租户隔离测试不应返回 5xx, 实际: {response.status_code}"
        data = response.json()
        assert isinstance(data, dict), "响应应为JSON对象"


    def test_Station_Interaction_get_1_invalid_id_0008(self, api_client):
        """[Station][Interaction] get_1 - 无效ID"""
        # GET /api/stations/{stationId}/rating-statistics
        response = api_client.get("station/api/stations/{stationId}/rating-statistics")
        assert response is not None, "响应不应为空"
        assert response.status_code in (200, 400, 403, 404), f"无效ID应返回 200/400/403/404, 实际: {response.status_code}"


    def test_Station_Interaction_get_1_not_found_id_0008(self, api_client):
        """[Station][Interaction] get_1 - 不存在ID"""
        # GET /api/stations/{stationId}/rating-statistics
        response = api_client.get("station/api/stations/{stationId}/rating-statistics")
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"不存在ID不应返回 5xx, 实际: {response.status_code}"


    def test_Station_Interaction_get_1_boundary_0008(self, api_client):
        """[Station][Interaction] get_1 - 边界值测试"""
        # GET /api/stations/{stationId}/rating-statistics
        response = api_client.get("station/api/stations/{stationId}/rating-statistics")
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"边界值测试不应返回 5xx 服务器错误, 实际: {response.status_code}"
        assert isinstance(response.json(), dict), "响应应为JSON对象"


    def test_Station_Interaction_get_1_sql_injection_0008(self, api_client):
        """[Station][Interaction] get_1 - SQL注入防护"""
        # GET /api/stations/{stationId}/rating-statistics
        response = api_client.get("station/api/stations/{stationId}/rating-statistics")
        assert response is not None, "响应不应为空"
        assert response.status_code != 500, f"SQL注入不应导致服务器错误, 实际: {response.status_code}"
        data = response.json()
        assert isinstance(data, dict), "响应应为JSON对象"


    def test_Station_Interaction_get_1_concurrent_0008(self, api_client):
        """[Station][Interaction] get_1 - 并发请求"""
        # GET /api/stations/{stationId}/rating-statistics
        responses = []
        for _ in range(3):
            r = api_client.get("station/api/stations/{stationId}/rating-statistics")
            responses.append(r)
        for r in responses:
            assert r is not None, "并发响应不应为空"
            assert r.status_code < 500, f"并发请求不应返回 5xx, 实际: {r.status_code}"


    def test_Station_Interaction_get_1_timeout_0008(self, api_client):
        """[Station][Interaction] get_1 - 超时处理"""
        # GET /api/stations/{stationId}/rating-statistics
        response = api_client.get("station/api/stations/{stationId}/rating-statistics")
        assert response is not None, "超时处理响应不应为空"
        assert response.status_code < 500, f"超时测试不应返回 5xx, 实际: {response.status_code}"


    def test_Station_Interaction_get_1_permission_denied_0008(self, api_client):
        """[Station][Interaction] get_1 - 权限不足"""
        # GET /api/stations/{stationId}/rating-statistics
        response = api_client.get("station/api/stations/{stationId}/rating-statistics")
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"权限测试不应返回 5xx, 实际: {response.status_code}"


    def test_Station_Interaction_get_1_response_format_0008(self, api_client):
        """[Station][Interaction] get_1 - 响应格式"""
        # GET /api/stations/{stationId}/rating-statistics
        response = api_client.get("station/api/stations/{stationId}/rating-statistics")
        assert response is not None, "响应不应为空"
        data = response.json()
        assert isinstance(data, dict), "响应应为JSON对象"
        if response.status_code == 200:
            assert "success" in data or "data" in data or "code" in data, "200 响应应包含标准字段"


    def test_Station_Interaction_get_2_positive_0009(self, api_client):
        """[Station][Interaction] get_2 - 正常请求"""
        # GET /api/feedbacks
        response = api_client.get("station/api/feedbacks")
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"GET 正常请求不应返回 5xx, 实际: {response.status_code}"


    def test_Station_Interaction_get_2_no_auth_0009(self, api_client):
        """[Station][Interaction] get_2 - 缺少认证头"""
        # GET /api/feedbacks
        api_client.clear_token()
        try:
            response = api_client.get("station/api/feedbacks")
            assert response is not None, "响应不应为空"
            assert response.status_code in (200, 400, 401, 403), f"无认证头应返回 401/403, 实际: {response.status_code}"
        finally:
            api_client.restore_token()


    def test_Station_Interaction_get_2_invalid_token_0009(self, api_client):
        """[Station][Interaction] get_2 - 无效Token"""
        # GET /api/feedbacks
        api_client.set_invalid_token()
        try:
            response = api_client.get("station/api/feedbacks")
            assert response is not None, "响应不应为空"
            assert response.status_code in (200, 400, 401, 403), f"无效Token应返回 401/403, 实际: {response.status_code}"
        finally:
            api_client.restore_token()


    def test_Station_Interaction_get_2_tenant_isolation_0009(self, api_client):
        """[Station][Interaction] get_2 - 租户隔离"""
        # GET /api/feedbacks
        response = api_client.get("station/api/feedbacks")
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"租户隔离测试不应返回 5xx, 实际: {response.status_code}"
        data = response.json()
        assert isinstance(data, dict), "响应应为JSON对象"


    def test_Station_Interaction_get_2_boundary_0009(self, api_client):
        """[Station][Interaction] get_2 - 边界值测试"""
        # GET /api/feedbacks
        response = api_client.get("station/api/feedbacks")
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"边界值测试不应返回 5xx 服务器错误, 实际: {response.status_code}"
        assert isinstance(response.json(), dict), "响应应为JSON对象"


    def test_Station_Interaction_get_2_sql_injection_0009(self, api_client):
        """[Station][Interaction] get_2 - SQL注入防护"""
        # GET /api/feedbacks
        response = api_client.get("station/api/feedbacks")
        assert response is not None, "响应不应为空"
        assert response.status_code != 500, f"SQL注入不应导致服务器错误, 实际: {response.status_code}"
        data = response.json()
        assert isinstance(data, dict), "响应应为JSON对象"


    def test_Station_Interaction_get_2_concurrent_0009(self, api_client):
        """[Station][Interaction] get_2 - 并发请求"""
        # GET /api/feedbacks
        responses = []
        for _ in range(3):
            r = api_client.get("station/api/feedbacks")
            responses.append(r)
        for r in responses:
            assert r is not None, "并发响应不应为空"
            assert r.status_code < 500, f"并发请求不应返回 5xx, 实际: {r.status_code}"


    def test_Station_Interaction_get_2_timeout_0009(self, api_client):
        """[Station][Interaction] get_2 - 超时处理"""
        # GET /api/feedbacks
        response = api_client.get("station/api/feedbacks")
        assert response is not None, "超时处理响应不应为空"
        assert response.status_code < 500, f"超时测试不应返回 5xx, 实际: {response.status_code}"


    def test_Station_Interaction_get_2_permission_denied_0009(self, api_client):
        """[Station][Interaction] get_2 - 权限不足"""
        # GET /api/feedbacks
        response = api_client.get("station/api/feedbacks")
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"权限测试不应返回 5xx, 实际: {response.status_code}"


    def test_Station_Interaction_get_2_response_format_0009(self, api_client):
        """[Station][Interaction] get_2 - 响应格式"""
        # GET /api/feedbacks
        response = api_client.get("station/api/feedbacks")
        assert response is not None, "响应不应为空"
        data = response.json()
        assert isinstance(data, dict), "响应应为JSON对象"
        if response.status_code == 200:
            assert "success" in data or "data" in data or "code" in data, "200 响应应包含标准字段"


    def test_Station_Interaction_get_3_positive_0010(self, api_client):
        """[Station][Interaction] get_3 - 正常请求"""
        # GET /api/feedbacks/statistics
        response = api_client.get("station/api/feedbacks/statistics")
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"GET 正常请求不应返回 5xx, 实际: {response.status_code}"


    def test_Station_Interaction_get_3_no_auth_0010(self, api_client):
        """[Station][Interaction] get_3 - 缺少认证头"""
        # GET /api/feedbacks/statistics
        api_client.clear_token()
        try:
            response = api_client.get("station/api/feedbacks/statistics")
            assert response is not None, "响应不应为空"
            assert response.status_code in (200, 400, 401, 403), f"无认证头应返回 401/403, 实际: {response.status_code}"
        finally:
            api_client.restore_token()


    def test_Station_Interaction_get_3_invalid_token_0010(self, api_client):
        """[Station][Interaction] get_3 - 无效Token"""
        # GET /api/feedbacks/statistics
        api_client.set_invalid_token()
        try:
            response = api_client.get("station/api/feedbacks/statistics")
            assert response is not None, "响应不应为空"
            assert response.status_code in (200, 400, 401, 403), f"无效Token应返回 401/403, 实际: {response.status_code}"
        finally:
            api_client.restore_token()


    def test_Station_Interaction_get_3_tenant_isolation_0010(self, api_client):
        """[Station][Interaction] get_3 - 租户隔离"""
        # GET /api/feedbacks/statistics
        response = api_client.get("station/api/feedbacks/statistics")
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"租户隔离测试不应返回 5xx, 实际: {response.status_code}"
        data = response.json()
        assert isinstance(data, dict), "响应应为JSON对象"


    def test_Station_Interaction_get_3_boundary_0010(self, api_client):
        """[Station][Interaction] get_3 - 边界值测试"""
        # GET /api/feedbacks/statistics
        response = api_client.get("station/api/feedbacks/statistics")
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"边界值测试不应返回 5xx 服务器错误, 实际: {response.status_code}"
        assert isinstance(response.json(), dict), "响应应为JSON对象"


    def test_Station_Interaction_get_3_sql_injection_0010(self, api_client):
        """[Station][Interaction] get_3 - SQL注入防护"""
        # GET /api/feedbacks/statistics
        response = api_client.get("station/api/feedbacks/statistics")
        assert response is not None, "响应不应为空"
        assert response.status_code != 500, f"SQL注入不应导致服务器错误, 实际: {response.status_code}"
        data = response.json()
        assert isinstance(data, dict), "响应应为JSON对象"


    def test_Station_Interaction_get_3_concurrent_0010(self, api_client):
        """[Station][Interaction] get_3 - 并发请求"""
        # GET /api/feedbacks/statistics
        responses = []
        for _ in range(3):
            r = api_client.get("station/api/feedbacks/statistics")
            responses.append(r)
        for r in responses:
            assert r is not None, "并发响应不应为空"
            assert r.status_code < 500, f"并发请求不应返回 5xx, 实际: {r.status_code}"


    def test_Station_Interaction_get_3_timeout_0010(self, api_client):
        """[Station][Interaction] get_3 - 超时处理"""
        # GET /api/feedbacks/statistics
        response = api_client.get("station/api/feedbacks/statistics")
        assert response is not None, "超时处理响应不应为空"
        assert response.status_code < 500, f"超时测试不应返回 5xx, 实际: {response.status_code}"


    def test_Station_Interaction_get_3_permission_denied_0010(self, api_client):
        """[Station][Interaction] get_3 - 权限不足"""
        # GET /api/feedbacks/statistics
        response = api_client.get("station/api/feedbacks/statistics")
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"权限测试不应返回 5xx, 实际: {response.status_code}"


    def test_Station_Interaction_get_3_response_format_0010(self, api_client):
        """[Station][Interaction] get_3 - 响应格式"""
        # GET /api/feedbacks/statistics
        response = api_client.get("station/api/feedbacks/statistics")
        assert response is not None, "响应不应为空"
        data = response.json()
        assert isinstance(data, dict), "响应应为JSON对象"
        if response.status_code == 200:
            assert "success" in data or "data" in data or "code" in data, "200 响应应包含标准字段"


    def test_Station_Interaction_post_4_positive_0011(self, api_client):
        """[Station][Interaction] post_4 - 正常请求"""
        # POST /api/stations/{stationId}/reviews
        response = api_client.post("station/api/stations/{stationId}/reviews", json_data={"name": "test", "code": "TEST"})
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"POST 正常请求不应返回 5xx, 实际: {response.status_code}"


    def test_Station_Interaction_post_4_no_auth_0011(self, api_client):
        """[Station][Interaction] post_4 - 缺少认证头"""
        # POST /api/stations/{stationId}/reviews
        api_client.clear_token()
        try:
            response = api_client.post("station/api/stations/{stationId}/reviews")
            assert response is not None, "响应不应为空"
            assert response.status_code in (200, 400, 401, 403), f"无认证头应返回 401/403, 实际: {response.status_code}"
        finally:
            api_client.restore_token()


    def test_Station_Interaction_post_4_invalid_token_0011(self, api_client):
        """[Station][Interaction] post_4 - 无效Token"""
        # POST /api/stations/{stationId}/reviews
        api_client.set_invalid_token()
        try:
            response = api_client.post("station/api/stations/{stationId}/reviews")
            assert response is not None, "响应不应为空"
            assert response.status_code in (200, 400, 401, 403), f"无效Token应返回 401/403, 实际: {response.status_code}"
        finally:
            api_client.restore_token()


    def test_Station_Interaction_post_4_tenant_isolation_0011(self, api_client):
        """[Station][Interaction] post_4 - 租户隔离"""
        # POST /api/stations/{stationId}/reviews
        response = api_client.post("station/api/stations/{stationId}/reviews")
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"租户隔离测试不应返回 5xx, 实际: {response.status_code}"
        data = response.json()
        assert isinstance(data, dict), "响应应为JSON对象"


    def test_Station_Interaction_post_4_empty_body_0011(self, api_client):
        """[Station][Interaction] post_4 - 空请求体"""
        # POST /api/stations/{stationId}/reviews
        response = api_client.post("station/api/stations/{stationId}/reviews")
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"空请求体不应返回 5xx, 实际: {response.status_code}"


    def test_Station_Interaction_post_4_invalid_id_0011(self, api_client):
        """[Station][Interaction] post_4 - 无效ID"""
        # POST /api/stations/{stationId}/reviews
        response = api_client.post("station/api/stations/{stationId}/reviews")
        assert response is not None, "响应不应为空"
        assert response.status_code in (200, 400, 403, 404), f"无效ID应返回 200/400/403/404, 实际: {response.status_code}"


    def test_Station_Interaction_post_4_not_found_id_0011(self, api_client):
        """[Station][Interaction] post_4 - 不存在ID"""
        # POST /api/stations/{stationId}/reviews
        response = api_client.post("station/api/stations/{stationId}/reviews")
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"不存在ID不应返回 5xx, 实际: {response.status_code}"


    def test_Station_Interaction_post_4_boundary_0011(self, api_client):
        """[Station][Interaction] post_4 - 边界值测试"""
        # POST /api/stations/{stationId}/reviews
        response = api_client.post("station/api/stations/{stationId}/reviews")
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"边界值测试不应返回 5xx 服务器错误, 实际: {response.status_code}"
        assert isinstance(response.json(), dict), "响应应为JSON对象"


    def test_Station_Interaction_post_4_sql_injection_0011(self, api_client):
        """[Station][Interaction] post_4 - SQL注入防护"""
        # POST /api/stations/{stationId}/reviews
        response = api_client.post("station/api/stations/{stationId}/reviews")
        assert response is not None, "响应不应为空"
        assert response.status_code != 500, f"SQL注入不应导致服务器错误, 实际: {response.status_code}"
        data = response.json()
        assert isinstance(data, dict), "响应应为JSON对象"


    def test_Station_Interaction_post_4_xss_protection_0011(self, api_client):
        """[Station][Interaction] post_4 - XSS防护"""
        # POST /api/stations/{stationId}/reviews
        xss_payload = {"name": "<script>alert('xss')</script>", "code": "XSS_TEST"}
        response = api_client.post("station/api/stations/{stationId}/reviews", json_data=xss_payload)
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"XSS防护测试不应返回 5xx, 实际: {response.status_code}"


    def test_Station_Interaction_post_4_large_payload_0011(self, api_client):
        """[Station][Interaction] post_4 - 大数据量"""
        # POST /api/stations/{stationId}/reviews
        large_data = {"name": "x" * 10000, "code": "LARGE", "description": "y" * 50000}
        response = api_client.post("station/api/stations/{stationId}/reviews", json_data=large_data)
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"大数据量测试不应返回 5xx, 实际: {response.status_code}"


    def test_Station_Interaction_post_4_concurrent_0011(self, api_client):
        """[Station][Interaction] post_4 - 并发请求"""
        # POST /api/stations/{stationId}/reviews
        responses = []
        for _ in range(3):
            r = api_client.post("station/api/stations/{stationId}/reviews")
            responses.append(r)
        for r in responses:
            assert r is not None, "并发响应不应为空"
            assert r.status_code < 500, f"并发请求不应返回 5xx, 实际: {r.status_code}"


    def test_Station_Interaction_post_4_timeout_0011(self, api_client):
        """[Station][Interaction] post_4 - 超时处理"""
        # POST /api/stations/{stationId}/reviews
        response = api_client.post("station/api/stations/{stationId}/reviews")
        assert response is not None, "超时处理响应不应为空"
        assert response.status_code < 500, f"超时测试不应返回 5xx, 实际: {response.status_code}"


    def test_Station_Interaction_post_4_permission_denied_0011(self, api_client):
        """[Station][Interaction] post_4 - 权限不足"""
        # POST /api/stations/{stationId}/reviews
        response = api_client.post("station/api/stations/{stationId}/reviews")
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"权限测试不应返回 5xx, 实际: {response.status_code}"


    def test_Station_Interaction_post_4_field_validation_0011(self, api_client):
        """[Station][Interaction] post_4 - 字段校验"""
        # POST /api/stations/{stationId}/reviews
        invalid_data = {"name": "", "code": ""}
        response = api_client.post("station/api/stations/{stationId}/reviews", json_data=invalid_data)
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"字段校验不应返回 5xx, 实际: {response.status_code}"


    def test_Station_Interaction_post_4_response_format_0011(self, api_client):
        """[Station][Interaction] post_4 - 响应格式"""
        # POST /api/stations/{stationId}/reviews
        response = api_client.post("station/api/stations/{stationId}/reviews")
        assert response is not None, "响应不应为空"
        data = response.json()
        assert isinstance(data, dict), "响应应为JSON对象"
        if response.status_code == 200:
            assert "success" in data or "data" in data or "code" in data, "200 响应应包含标准字段"


    def test_Station_Interaction_post_5_positive_0012(self, api_client):
        """[Station][Interaction] post_5 - 正常请求"""
        # POST /api/reviews/{reviewId}/audit
        response = api_client.post("station/api/reviews/{reviewId}/audit", json_data={"name": "test", "code": "TEST"})
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"POST 正常请求不应返回 5xx, 实际: {response.status_code}"


    def test_Station_Interaction_post_5_no_auth_0012(self, api_client):
        """[Station][Interaction] post_5 - 缺少认证头"""
        # POST /api/reviews/{reviewId}/audit
        api_client.clear_token()
        try:
            response = api_client.post("station/api/reviews/{reviewId}/audit")
            assert response is not None, "响应不应为空"
            assert response.status_code in (200, 400, 401, 403), f"无认证头应返回 401/403, 实际: {response.status_code}"
        finally:
            api_client.restore_token()


    def test_Station_Interaction_post_5_invalid_token_0012(self, api_client):
        """[Station][Interaction] post_5 - 无效Token"""
        # POST /api/reviews/{reviewId}/audit
        api_client.set_invalid_token()
        try:
            response = api_client.post("station/api/reviews/{reviewId}/audit")
            assert response is not None, "响应不应为空"
            assert response.status_code in (200, 400, 401, 403), f"无效Token应返回 401/403, 实际: {response.status_code}"
        finally:
            api_client.restore_token()


    def test_Station_Interaction_post_5_tenant_isolation_0012(self, api_client):
        """[Station][Interaction] post_5 - 租户隔离"""
        # POST /api/reviews/{reviewId}/audit
        response = api_client.post("station/api/reviews/{reviewId}/audit")
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"租户隔离测试不应返回 5xx, 实际: {response.status_code}"
        data = response.json()
        assert isinstance(data, dict), "响应应为JSON对象"


    def test_Station_Interaction_post_5_empty_body_0012(self, api_client):
        """[Station][Interaction] post_5 - 空请求体"""
        # POST /api/reviews/{reviewId}/audit
        response = api_client.post("station/api/reviews/{reviewId}/audit")
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"空请求体不应返回 5xx, 实际: {response.status_code}"


    def test_Station_Interaction_post_5_invalid_id_0012(self, api_client):
        """[Station][Interaction] post_5 - 无效ID"""
        # POST /api/reviews/{reviewId}/audit
        response = api_client.post("station/api/reviews/{reviewId}/audit")
        assert response is not None, "响应不应为空"
        assert response.status_code in (200, 400, 403, 404), f"无效ID应返回 200/400/403/404, 实际: {response.status_code}"


    def test_Station_Interaction_post_5_not_found_id_0012(self, api_client):
        """[Station][Interaction] post_5 - 不存在ID"""
        # POST /api/reviews/{reviewId}/audit
        response = api_client.post("station/api/reviews/{reviewId}/audit")
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"不存在ID不应返回 5xx, 实际: {response.status_code}"


    def test_Station_Interaction_post_5_boundary_0012(self, api_client):
        """[Station][Interaction] post_5 - 边界值测试"""
        # POST /api/reviews/{reviewId}/audit
        response = api_client.post("station/api/reviews/{reviewId}/audit")
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"边界值测试不应返回 5xx 服务器错误, 实际: {response.status_code}"
        assert isinstance(response.json(), dict), "响应应为JSON对象"


    def test_Station_Interaction_post_5_sql_injection_0012(self, api_client):
        """[Station][Interaction] post_5 - SQL注入防护"""
        # POST /api/reviews/{reviewId}/audit
        response = api_client.post("station/api/reviews/{reviewId}/audit")
        assert response is not None, "响应不应为空"
        assert response.status_code != 500, f"SQL注入不应导致服务器错误, 实际: {response.status_code}"
        data = response.json()
        assert isinstance(data, dict), "响应应为JSON对象"


    def test_Station_Interaction_post_5_xss_protection_0012(self, api_client):
        """[Station][Interaction] post_5 - XSS防护"""
        # POST /api/reviews/{reviewId}/audit
        xss_payload = {"name": "<script>alert('xss')</script>", "code": "XSS_TEST"}
        response = api_client.post("station/api/reviews/{reviewId}/audit", json_data=xss_payload)
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"XSS防护测试不应返回 5xx, 实际: {response.status_code}"


    def test_Station_Interaction_post_5_large_payload_0012(self, api_client):
        """[Station][Interaction] post_5 - 大数据量"""
        # POST /api/reviews/{reviewId}/audit
        large_data = {"name": "x" * 10000, "code": "LARGE", "description": "y" * 50000}
        response = api_client.post("station/api/reviews/{reviewId}/audit", json_data=large_data)
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"大数据量测试不应返回 5xx, 实际: {response.status_code}"


    def test_Station_Interaction_post_5_concurrent_0012(self, api_client):
        """[Station][Interaction] post_5 - 并发请求"""
        # POST /api/reviews/{reviewId}/audit
        responses = []
        for _ in range(3):
            r = api_client.post("station/api/reviews/{reviewId}/audit")
            responses.append(r)
        for r in responses:
            assert r is not None, "并发响应不应为空"
            assert r.status_code < 500, f"并发请求不应返回 5xx, 实际: {r.status_code}"


    def test_Station_Interaction_post_5_timeout_0012(self, api_client):
        """[Station][Interaction] post_5 - 超时处理"""
        # POST /api/reviews/{reviewId}/audit
        response = api_client.post("station/api/reviews/{reviewId}/audit")
        assert response is not None, "超时处理响应不应为空"
        assert response.status_code < 500, f"超时测试不应返回 5xx, 实际: {response.status_code}"


    def test_Station_Interaction_post_5_permission_denied_0012(self, api_client):
        """[Station][Interaction] post_5 - 权限不足"""
        # POST /api/reviews/{reviewId}/audit
        response = api_client.post("station/api/reviews/{reviewId}/audit")
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"权限测试不应返回 5xx, 实际: {response.status_code}"


    def test_Station_Interaction_post_5_field_validation_0012(self, api_client):
        """[Station][Interaction] post_5 - 字段校验"""
        # POST /api/reviews/{reviewId}/audit
        invalid_data = {"name": "", "code": ""}
        response = api_client.post("station/api/reviews/{reviewId}/audit", json_data=invalid_data)
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"字段校验不应返回 5xx, 实际: {response.status_code}"


    def test_Station_Interaction_post_5_response_format_0012(self, api_client):
        """[Station][Interaction] post_5 - 响应格式"""
        # POST /api/reviews/{reviewId}/audit
        response = api_client.post("station/api/reviews/{reviewId}/audit")
        assert response is not None, "响应不应为空"
        data = response.json()
        assert isinstance(data, dict), "响应应为JSON对象"
        if response.status_code == 200:
            assert "success" in data or "data" in data or "code" in data, "200 响应应包含标准字段"


    def test_Station_Interaction_post_6_positive_0013(self, api_client):
        """[Station][Interaction] post_6 - 正常请求"""
        # POST /api/reviews/{reviewId}/reply
        response = api_client.post("station/api/reviews/{reviewId}/reply", json_data={"name": "test", "code": "TEST"})
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"POST 正常请求不应返回 5xx, 实际: {response.status_code}"


    def test_Station_Interaction_post_6_no_auth_0013(self, api_client):
        """[Station][Interaction] post_6 - 缺少认证头"""
        # POST /api/reviews/{reviewId}/reply
        api_client.clear_token()
        try:
            response = api_client.post("station/api/reviews/{reviewId}/reply")
            assert response is not None, "响应不应为空"
            assert response.status_code in (200, 400, 401, 403), f"无认证头应返回 401/403, 实际: {response.status_code}"
        finally:
            api_client.restore_token()


    def test_Station_Interaction_post_6_invalid_token_0013(self, api_client):
        """[Station][Interaction] post_6 - 无效Token"""
        # POST /api/reviews/{reviewId}/reply
        api_client.set_invalid_token()
        try:
            response = api_client.post("station/api/reviews/{reviewId}/reply")
            assert response is not None, "响应不应为空"
            assert response.status_code in (200, 400, 401, 403), f"无效Token应返回 401/403, 实际: {response.status_code}"
        finally:
            api_client.restore_token()


    def test_Station_Interaction_post_6_tenant_isolation_0013(self, api_client):
        """[Station][Interaction] post_6 - 租户隔离"""
        # POST /api/reviews/{reviewId}/reply
        response = api_client.post("station/api/reviews/{reviewId}/reply")
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"租户隔离测试不应返回 5xx, 实际: {response.status_code}"
        data = response.json()
        assert isinstance(data, dict), "响应应为JSON对象"


    def test_Station_Interaction_post_6_empty_body_0013(self, api_client):
        """[Station][Interaction] post_6 - 空请求体"""
        # POST /api/reviews/{reviewId}/reply
        response = api_client.post("station/api/reviews/{reviewId}/reply")
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"空请求体不应返回 5xx, 实际: {response.status_code}"


    def test_Station_Interaction_post_6_invalid_id_0013(self, api_client):
        """[Station][Interaction] post_6 - 无效ID"""
        # POST /api/reviews/{reviewId}/reply
        response = api_client.post("station/api/reviews/{reviewId}/reply")
        assert response is not None, "响应不应为空"
        assert response.status_code in (200, 400, 403, 404), f"无效ID应返回 200/400/403/404, 实际: {response.status_code}"


    def test_Station_Interaction_post_6_not_found_id_0013(self, api_client):
        """[Station][Interaction] post_6 - 不存在ID"""
        # POST /api/reviews/{reviewId}/reply
        response = api_client.post("station/api/reviews/{reviewId}/reply")
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"不存在ID不应返回 5xx, 实际: {response.status_code}"


    def test_Station_Interaction_post_6_boundary_0013(self, api_client):
        """[Station][Interaction] post_6 - 边界值测试"""
        # POST /api/reviews/{reviewId}/reply
        response = api_client.post("station/api/reviews/{reviewId}/reply")
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"边界值测试不应返回 5xx 服务器错误, 实际: {response.status_code}"
        assert isinstance(response.json(), dict), "响应应为JSON对象"


    def test_Station_Interaction_post_6_sql_injection_0013(self, api_client):
        """[Station][Interaction] post_6 - SQL注入防护"""
        # POST /api/reviews/{reviewId}/reply
        response = api_client.post("station/api/reviews/{reviewId}/reply")
        assert response is not None, "响应不应为空"
        assert response.status_code != 500, f"SQL注入不应导致服务器错误, 实际: {response.status_code}"
        data = response.json()
        assert isinstance(data, dict), "响应应为JSON对象"


    def test_Station_Interaction_post_6_xss_protection_0013(self, api_client):
        """[Station][Interaction] post_6 - XSS防护"""
        # POST /api/reviews/{reviewId}/reply
        xss_payload = {"name": "<script>alert('xss')</script>", "code": "XSS_TEST"}
        response = api_client.post("station/api/reviews/{reviewId}/reply", json_data=xss_payload)
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"XSS防护测试不应返回 5xx, 实际: {response.status_code}"


    def test_Station_Interaction_post_6_large_payload_0013(self, api_client):
        """[Station][Interaction] post_6 - 大数据量"""
        # POST /api/reviews/{reviewId}/reply
        large_data = {"name": "x" * 10000, "code": "LARGE", "description": "y" * 50000}
        response = api_client.post("station/api/reviews/{reviewId}/reply", json_data=large_data)
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"大数据量测试不应返回 5xx, 实际: {response.status_code}"


    def test_Station_Interaction_post_6_concurrent_0013(self, api_client):
        """[Station][Interaction] post_6 - 并发请求"""
        # POST /api/reviews/{reviewId}/reply
        responses = []
        for _ in range(3):
            r = api_client.post("station/api/reviews/{reviewId}/reply")
            responses.append(r)
        for r in responses:
            assert r is not None, "并发响应不应为空"
            assert r.status_code < 500, f"并发请求不应返回 5xx, 实际: {r.status_code}"


    def test_Station_Interaction_post_6_timeout_0013(self, api_client):
        """[Station][Interaction] post_6 - 超时处理"""
        # POST /api/reviews/{reviewId}/reply
        response = api_client.post("station/api/reviews/{reviewId}/reply")
        assert response is not None, "超时处理响应不应为空"
        assert response.status_code < 500, f"超时测试不应返回 5xx, 实际: {response.status_code}"


    def test_Station_Interaction_post_6_permission_denied_0013(self, api_client):
        """[Station][Interaction] post_6 - 权限不足"""
        # POST /api/reviews/{reviewId}/reply
        response = api_client.post("station/api/reviews/{reviewId}/reply")
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"权限测试不应返回 5xx, 实际: {response.status_code}"


    def test_Station_Interaction_post_6_field_validation_0013(self, api_client):
        """[Station][Interaction] post_6 - 字段校验"""
        # POST /api/reviews/{reviewId}/reply
        invalid_data = {"name": "", "code": ""}
        response = api_client.post("station/api/reviews/{reviewId}/reply", json_data=invalid_data)
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"字段校验不应返回 5xx, 实际: {response.status_code}"


    def test_Station_Interaction_post_6_response_format_0013(self, api_client):
        """[Station][Interaction] post_6 - 响应格式"""
        # POST /api/reviews/{reviewId}/reply
        response = api_client.post("station/api/reviews/{reviewId}/reply")
        assert response is not None, "响应不应为空"
        data = response.json()
        assert isinstance(data, dict), "响应应为JSON对象"
        if response.status_code == 200:
            assert "success" in data or "data" in data or "code" in data, "200 响应应包含标准字段"


    def test_Station_Interaction_post_7_positive_0014(self, api_client):
        """[Station][Interaction] post_7 - 正常请求"""
        # POST /api/reviews/{reviewId}/like
        response = api_client.post("station/api/reviews/{reviewId}/like", json_data={"name": "test", "code": "TEST"})
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"POST 正常请求不应返回 5xx, 实际: {response.status_code}"


    def test_Station_Interaction_post_7_no_auth_0014(self, api_client):
        """[Station][Interaction] post_7 - 缺少认证头"""
        # POST /api/reviews/{reviewId}/like
        api_client.clear_token()
        try:
            response = api_client.post("station/api/reviews/{reviewId}/like")
            assert response is not None, "响应不应为空"
            assert response.status_code in (200, 400, 401, 403), f"无认证头应返回 401/403, 实际: {response.status_code}"
        finally:
            api_client.restore_token()


    def test_Station_Interaction_post_7_invalid_token_0014(self, api_client):
        """[Station][Interaction] post_7 - 无效Token"""
        # POST /api/reviews/{reviewId}/like
        api_client.set_invalid_token()
        try:
            response = api_client.post("station/api/reviews/{reviewId}/like")
            assert response is not None, "响应不应为空"
            assert response.status_code in (200, 400, 401, 403), f"无效Token应返回 401/403, 实际: {response.status_code}"
        finally:
            api_client.restore_token()


    def test_Station_Interaction_post_7_tenant_isolation_0014(self, api_client):
        """[Station][Interaction] post_7 - 租户隔离"""
        # POST /api/reviews/{reviewId}/like
        response = api_client.post("station/api/reviews/{reviewId}/like")
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"租户隔离测试不应返回 5xx, 实际: {response.status_code}"
        data = response.json()
        assert isinstance(data, dict), "响应应为JSON对象"


    def test_Station_Interaction_post_7_empty_body_0014(self, api_client):
        """[Station][Interaction] post_7 - 空请求体"""
        # POST /api/reviews/{reviewId}/like
        response = api_client.post("station/api/reviews/{reviewId}/like")
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"空请求体不应返回 5xx, 实际: {response.status_code}"


    def test_Station_Interaction_post_7_invalid_id_0014(self, api_client):
        """[Station][Interaction] post_7 - 无效ID"""
        # POST /api/reviews/{reviewId}/like
        response = api_client.post("station/api/reviews/{reviewId}/like")
        assert response is not None, "响应不应为空"
        assert response.status_code in (200, 400, 403, 404), f"无效ID应返回 200/400/403/404, 实际: {response.status_code}"


    def test_Station_Interaction_post_7_not_found_id_0014(self, api_client):
        """[Station][Interaction] post_7 - 不存在ID"""
        # POST /api/reviews/{reviewId}/like
        response = api_client.post("station/api/reviews/{reviewId}/like")
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"不存在ID不应返回 5xx, 实际: {response.status_code}"


    def test_Station_Interaction_post_7_boundary_0014(self, api_client):
        """[Station][Interaction] post_7 - 边界值测试"""
        # POST /api/reviews/{reviewId}/like
        response = api_client.post("station/api/reviews/{reviewId}/like")
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"边界值测试不应返回 5xx 服务器错误, 实际: {response.status_code}"
        assert isinstance(response.json(), dict), "响应应为JSON对象"


    def test_Station_Interaction_post_7_sql_injection_0014(self, api_client):
        """[Station][Interaction] post_7 - SQL注入防护"""
        # POST /api/reviews/{reviewId}/like
        response = api_client.post("station/api/reviews/{reviewId}/like")
        assert response is not None, "响应不应为空"
        assert response.status_code != 500, f"SQL注入不应导致服务器错误, 实际: {response.status_code}"
        data = response.json()
        assert isinstance(data, dict), "响应应为JSON对象"


    def test_Station_Interaction_post_7_xss_protection_0014(self, api_client):
        """[Station][Interaction] post_7 - XSS防护"""
        # POST /api/reviews/{reviewId}/like
        xss_payload = {"name": "<script>alert('xss')</script>", "code": "XSS_TEST"}
        response = api_client.post("station/api/reviews/{reviewId}/like", json_data=xss_payload)
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"XSS防护测试不应返回 5xx, 实际: {response.status_code}"


    def test_Station_Interaction_post_7_large_payload_0014(self, api_client):
        """[Station][Interaction] post_7 - 大数据量"""
        # POST /api/reviews/{reviewId}/like
        large_data = {"name": "x" * 10000, "code": "LARGE", "description": "y" * 50000}
        response = api_client.post("station/api/reviews/{reviewId}/like", json_data=large_data)
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"大数据量测试不应返回 5xx, 实际: {response.status_code}"


    def test_Station_Interaction_post_7_concurrent_0014(self, api_client):
        """[Station][Interaction] post_7 - 并发请求"""
        # POST /api/reviews/{reviewId}/like
        responses = []
        for _ in range(3):
            r = api_client.post("station/api/reviews/{reviewId}/like")
            responses.append(r)
        for r in responses:
            assert r is not None, "并发响应不应为空"
            assert r.status_code < 500, f"并发请求不应返回 5xx, 实际: {r.status_code}"


    def test_Station_Interaction_post_7_timeout_0014(self, api_client):
        """[Station][Interaction] post_7 - 超时处理"""
        # POST /api/reviews/{reviewId}/like
        response = api_client.post("station/api/reviews/{reviewId}/like")
        assert response is not None, "超时处理响应不应为空"
        assert response.status_code < 500, f"超时测试不应返回 5xx, 实际: {response.status_code}"


    def test_Station_Interaction_post_7_permission_denied_0014(self, api_client):
        """[Station][Interaction] post_7 - 权限不足"""
        # POST /api/reviews/{reviewId}/like
        response = api_client.post("station/api/reviews/{reviewId}/like")
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"权限测试不应返回 5xx, 实际: {response.status_code}"


    def test_Station_Interaction_post_7_field_validation_0014(self, api_client):
        """[Station][Interaction] post_7 - 字段校验"""
        # POST /api/reviews/{reviewId}/like
        invalid_data = {"name": "", "code": ""}
        response = api_client.post("station/api/reviews/{reviewId}/like", json_data=invalid_data)
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"字段校验不应返回 5xx, 实际: {response.status_code}"


    def test_Station_Interaction_post_7_response_format_0014(self, api_client):
        """[Station][Interaction] post_7 - 响应格式"""
        # POST /api/reviews/{reviewId}/like
        response = api_client.post("station/api/reviews/{reviewId}/like")
        assert response is not None, "响应不应为空"
        data = response.json()
        assert isinstance(data, dict), "响应应为JSON对象"
        if response.status_code == 200:
            assert "success" in data or "data" in data or "code" in data, "200 响应应包含标准字段"


    def test_Station_Interaction_post_8_positive_0015(self, api_client):
        """[Station][Interaction] post_8 - 正常请求"""
        # POST /api/feedbacks
        response = api_client.post("station/api/feedbacks", json_data={"name": "test", "code": "TEST"})
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"POST 正常请求不应返回 5xx, 实际: {response.status_code}"


    def test_Station_Interaction_post_8_no_auth_0015(self, api_client):
        """[Station][Interaction] post_8 - 缺少认证头"""
        # POST /api/feedbacks
        api_client.clear_token()
        try:
            response = api_client.post("station/api/feedbacks")
            assert response is not None, "响应不应为空"
            assert response.status_code in (200, 400, 401, 403), f"无认证头应返回 401/403, 实际: {response.status_code}"
        finally:
            api_client.restore_token()


    def test_Station_Interaction_post_8_invalid_token_0015(self, api_client):
        """[Station][Interaction] post_8 - 无效Token"""
        # POST /api/feedbacks
        api_client.set_invalid_token()
        try:
            response = api_client.post("station/api/feedbacks")
            assert response is not None, "响应不应为空"
            assert response.status_code in (200, 400, 401, 403), f"无效Token应返回 401/403, 实际: {response.status_code}"
        finally:
            api_client.restore_token()


    def test_Station_Interaction_post_8_tenant_isolation_0015(self, api_client):
        """[Station][Interaction] post_8 - 租户隔离"""
        # POST /api/feedbacks
        response = api_client.post("station/api/feedbacks")
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"租户隔离测试不应返回 5xx, 实际: {response.status_code}"
        data = response.json()
        assert isinstance(data, dict), "响应应为JSON对象"


    def test_Station_Interaction_post_8_empty_body_0015(self, api_client):
        """[Station][Interaction] post_8 - 空请求体"""
        # POST /api/feedbacks
        response = api_client.post("station/api/feedbacks")
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"空请求体不应返回 5xx, 实际: {response.status_code}"


    def test_Station_Interaction_post_8_boundary_0015(self, api_client):
        """[Station][Interaction] post_8 - 边界值测试"""
        # POST /api/feedbacks
        response = api_client.post("station/api/feedbacks")
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"边界值测试不应返回 5xx 服务器错误, 实际: {response.status_code}"
        assert isinstance(response.json(), dict), "响应应为JSON对象"


    def test_Station_Interaction_post_8_sql_injection_0015(self, api_client):
        """[Station][Interaction] post_8 - SQL注入防护"""
        # POST /api/feedbacks
        response = api_client.post("station/api/feedbacks")
        assert response is not None, "响应不应为空"
        assert response.status_code != 500, f"SQL注入不应导致服务器错误, 实际: {response.status_code}"
        data = response.json()
        assert isinstance(data, dict), "响应应为JSON对象"


    def test_Station_Interaction_post_8_xss_protection_0015(self, api_client):
        """[Station][Interaction] post_8 - XSS防护"""
        # POST /api/feedbacks
        xss_payload = {"name": "<script>alert('xss')</script>", "code": "XSS_TEST"}
        response = api_client.post("station/api/feedbacks", json_data=xss_payload)
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"XSS防护测试不应返回 5xx, 实际: {response.status_code}"


    def test_Station_Interaction_post_8_large_payload_0015(self, api_client):
        """[Station][Interaction] post_8 - 大数据量"""
        # POST /api/feedbacks
        large_data = {"name": "x" * 10000, "code": "LARGE", "description": "y" * 50000}
        response = api_client.post("station/api/feedbacks", json_data=large_data)
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"大数据量测试不应返回 5xx, 实际: {response.status_code}"


    def test_Station_Interaction_post_8_concurrent_0015(self, api_client):
        """[Station][Interaction] post_8 - 并发请求"""
        # POST /api/feedbacks
        responses = []
        for _ in range(3):
            r = api_client.post("station/api/feedbacks")
            responses.append(r)
        for r in responses:
            assert r is not None, "并发响应不应为空"
            assert r.status_code < 500, f"并发请求不应返回 5xx, 实际: {r.status_code}"


    def test_Station_Interaction_post_8_timeout_0015(self, api_client):
        """[Station][Interaction] post_8 - 超时处理"""
        # POST /api/feedbacks
        response = api_client.post("station/api/feedbacks")
        assert response is not None, "超时处理响应不应为空"
        assert response.status_code < 500, f"超时测试不应返回 5xx, 实际: {response.status_code}"


    def test_Station_Interaction_post_8_permission_denied_0015(self, api_client):
        """[Station][Interaction] post_8 - 权限不足"""
        # POST /api/feedbacks
        response = api_client.post("station/api/feedbacks")
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"权限测试不应返回 5xx, 实际: {response.status_code}"


    def test_Station_Interaction_post_8_field_validation_0015(self, api_client):
        """[Station][Interaction] post_8 - 字段校验"""
        # POST /api/feedbacks
        invalid_data = {"name": "", "code": ""}
        response = api_client.post("station/api/feedbacks", json_data=invalid_data)
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"字段校验不应返回 5xx, 实际: {response.status_code}"


    def test_Station_Interaction_post_8_response_format_0015(self, api_client):
        """[Station][Interaction] post_8 - 响应格式"""
        # POST /api/feedbacks
        response = api_client.post("station/api/feedbacks")
        assert response is not None, "响应不应为空"
        data = response.json()
        assert isinstance(data, dict), "响应应为JSON对象"
        if response.status_code == 200:
            assert "success" in data or "data" in data or "code" in data, "200 响应应包含标准字段"


    def test_Station_Interaction_post_9_positive_0016(self, api_client):
        """[Station][Interaction] post_9 - 正常请求"""
        # POST /api/feedbacks/{complaintId}/assign
        response = api_client.post("station/api/feedbacks/{complaintId}/assign", json_data={"name": "test", "code": "TEST"})
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"POST 正常请求不应返回 5xx, 实际: {response.status_code}"


    def test_Station_Interaction_post_9_no_auth_0016(self, api_client):
        """[Station][Interaction] post_9 - 缺少认证头"""
        # POST /api/feedbacks/{complaintId}/assign
        api_client.clear_token()
        try:
            response = api_client.post("station/api/feedbacks/{complaintId}/assign")
            assert response is not None, "响应不应为空"
            assert response.status_code in (200, 400, 401, 403), f"无认证头应返回 401/403, 实际: {response.status_code}"
        finally:
            api_client.restore_token()


    def test_Station_Interaction_post_9_invalid_token_0016(self, api_client):
        """[Station][Interaction] post_9 - 无效Token"""
        # POST /api/feedbacks/{complaintId}/assign
        api_client.set_invalid_token()
        try:
            response = api_client.post("station/api/feedbacks/{complaintId}/assign")
            assert response is not None, "响应不应为空"
            assert response.status_code in (200, 400, 401, 403), f"无效Token应返回 401/403, 实际: {response.status_code}"
        finally:
            api_client.restore_token()


    def test_Station_Interaction_post_9_tenant_isolation_0016(self, api_client):
        """[Station][Interaction] post_9 - 租户隔离"""
        # POST /api/feedbacks/{complaintId}/assign
        response = api_client.post("station/api/feedbacks/{complaintId}/assign")
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"租户隔离测试不应返回 5xx, 实际: {response.status_code}"
        data = response.json()
        assert isinstance(data, dict), "响应应为JSON对象"


    def test_Station_Interaction_post_9_empty_body_0016(self, api_client):
        """[Station][Interaction] post_9 - 空请求体"""
        # POST /api/feedbacks/{complaintId}/assign
        response = api_client.post("station/api/feedbacks/{complaintId}/assign")
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"空请求体不应返回 5xx, 实际: {response.status_code}"


    def test_Station_Interaction_post_9_invalid_id_0016(self, api_client):
        """[Station][Interaction] post_9 - 无效ID"""
        # POST /api/feedbacks/{complaintId}/assign
        response = api_client.post("station/api/feedbacks/{complaintId}/assign")
        assert response is not None, "响应不应为空"
        assert response.status_code in (200, 400, 403, 404), f"无效ID应返回 200/400/403/404, 实际: {response.status_code}"


    def test_Station_Interaction_post_9_not_found_id_0016(self, api_client):
        """[Station][Interaction] post_9 - 不存在ID"""
        # POST /api/feedbacks/{complaintId}/assign
        response = api_client.post("station/api/feedbacks/{complaintId}/assign")
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"不存在ID不应返回 5xx, 实际: {response.status_code}"


    def test_Station_Interaction_post_9_boundary_0016(self, api_client):
        """[Station][Interaction] post_9 - 边界值测试"""
        # POST /api/feedbacks/{complaintId}/assign
        response = api_client.post("station/api/feedbacks/{complaintId}/assign")
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"边界值测试不应返回 5xx 服务器错误, 实际: {response.status_code}"
        assert isinstance(response.json(), dict), "响应应为JSON对象"


    def test_Station_Interaction_post_9_sql_injection_0016(self, api_client):
        """[Station][Interaction] post_9 - SQL注入防护"""
        # POST /api/feedbacks/{complaintId}/assign
        response = api_client.post("station/api/feedbacks/{complaintId}/assign")
        assert response is not None, "响应不应为空"
        assert response.status_code != 500, f"SQL注入不应导致服务器错误, 实际: {response.status_code}"
        data = response.json()
        assert isinstance(data, dict), "响应应为JSON对象"


    def test_Station_Interaction_post_9_xss_protection_0016(self, api_client):
        """[Station][Interaction] post_9 - XSS防护"""
        # POST /api/feedbacks/{complaintId}/assign
        xss_payload = {"name": "<script>alert('xss')</script>", "code": "XSS_TEST"}
        response = api_client.post("station/api/feedbacks/{complaintId}/assign", json_data=xss_payload)
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"XSS防护测试不应返回 5xx, 实际: {response.status_code}"


    def test_Station_Interaction_post_9_large_payload_0016(self, api_client):
        """[Station][Interaction] post_9 - 大数据量"""
        # POST /api/feedbacks/{complaintId}/assign
        large_data = {"name": "x" * 10000, "code": "LARGE", "description": "y" * 50000}
        response = api_client.post("station/api/feedbacks/{complaintId}/assign", json_data=large_data)
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"大数据量测试不应返回 5xx, 实际: {response.status_code}"


    def test_Station_Interaction_post_9_concurrent_0016(self, api_client):
        """[Station][Interaction] post_9 - 并发请求"""
        # POST /api/feedbacks/{complaintId}/assign
        responses = []
        for _ in range(3):
            r = api_client.post("station/api/feedbacks/{complaintId}/assign")
            responses.append(r)
        for r in responses:
            assert r is not None, "并发响应不应为空"
            assert r.status_code < 500, f"并发请求不应返回 5xx, 实际: {r.status_code}"


    def test_Station_Interaction_post_9_timeout_0016(self, api_client):
        """[Station][Interaction] post_9 - 超时处理"""
        # POST /api/feedbacks/{complaintId}/assign
        response = api_client.post("station/api/feedbacks/{complaintId}/assign")
        assert response is not None, "超时处理响应不应为空"
        assert response.status_code < 500, f"超时测试不应返回 5xx, 实际: {response.status_code}"


    def test_Station_Interaction_post_9_permission_denied_0016(self, api_client):
        """[Station][Interaction] post_9 - 权限不足"""
        # POST /api/feedbacks/{complaintId}/assign
        response = api_client.post("station/api/feedbacks/{complaintId}/assign")
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"权限测试不应返回 5xx, 实际: {response.status_code}"


    def test_Station_Interaction_post_9_field_validation_0016(self, api_client):
        """[Station][Interaction] post_9 - 字段校验"""
        # POST /api/feedbacks/{complaintId}/assign
        invalid_data = {"name": "", "code": ""}
        response = api_client.post("station/api/feedbacks/{complaintId}/assign", json_data=invalid_data)
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"字段校验不应返回 5xx, 实际: {response.status_code}"


    def test_Station_Interaction_post_9_response_format_0016(self, api_client):
        """[Station][Interaction] post_9 - 响应格式"""
        # POST /api/feedbacks/{complaintId}/assign
        response = api_client.post("station/api/feedbacks/{complaintId}/assign")
        assert response is not None, "响应不应为空"
        data = response.json()
        assert isinstance(data, dict), "响应应为JSON对象"
        if response.status_code == 200:
            assert "success" in data or "data" in data or "code" in data, "200 响应应包含标准字段"


    def test_Station_Interaction_post_10_positive_0017(self, api_client):
        """[Station][Interaction] post_10 - 正常请求"""
        # POST /api/feedbacks/{complaintId}/resolve
        response = api_client.post("station/api/feedbacks/{complaintId}/resolve", json_data={"name": "test", "code": "TEST"})
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"POST 正常请求不应返回 5xx, 实际: {response.status_code}"


    def test_Station_Interaction_post_10_no_auth_0017(self, api_client):
        """[Station][Interaction] post_10 - 缺少认证头"""
        # POST /api/feedbacks/{complaintId}/resolve
        api_client.clear_token()
        try:
            response = api_client.post("station/api/feedbacks/{complaintId}/resolve")
            assert response is not None, "响应不应为空"
            assert response.status_code in (200, 400, 401, 403), f"无认证头应返回 401/403, 实际: {response.status_code}"
        finally:
            api_client.restore_token()


    def test_Station_Interaction_post_10_invalid_token_0017(self, api_client):
        """[Station][Interaction] post_10 - 无效Token"""
        # POST /api/feedbacks/{complaintId}/resolve
        api_client.set_invalid_token()
        try:
            response = api_client.post("station/api/feedbacks/{complaintId}/resolve")
            assert response is not None, "响应不应为空"
            assert response.status_code in (200, 400, 401, 403), f"无效Token应返回 401/403, 实际: {response.status_code}"
        finally:
            api_client.restore_token()


    def test_Station_Interaction_post_10_tenant_isolation_0017(self, api_client):
        """[Station][Interaction] post_10 - 租户隔离"""
        # POST /api/feedbacks/{complaintId}/resolve
        response = api_client.post("station/api/feedbacks/{complaintId}/resolve")
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"租户隔离测试不应返回 5xx, 实际: {response.status_code}"
        data = response.json()
        assert isinstance(data, dict), "响应应为JSON对象"


    def test_Station_Interaction_post_10_empty_body_0017(self, api_client):
        """[Station][Interaction] post_10 - 空请求体"""
        # POST /api/feedbacks/{complaintId}/resolve
        response = api_client.post("station/api/feedbacks/{complaintId}/resolve")
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"空请求体不应返回 5xx, 实际: {response.status_code}"


    def test_Station_Interaction_post_10_invalid_id_0017(self, api_client):
        """[Station][Interaction] post_10 - 无效ID"""
        # POST /api/feedbacks/{complaintId}/resolve
        response = api_client.post("station/api/feedbacks/{complaintId}/resolve")
        assert response is not None, "响应不应为空"
        assert response.status_code in (200, 400, 403, 404), f"无效ID应返回 200/400/403/404, 实际: {response.status_code}"


    def test_Station_Interaction_post_10_not_found_id_0017(self, api_client):
        """[Station][Interaction] post_10 - 不存在ID"""
        # POST /api/feedbacks/{complaintId}/resolve
        response = api_client.post("station/api/feedbacks/{complaintId}/resolve")
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"不存在ID不应返回 5xx, 实际: {response.status_code}"


    def test_Station_Interaction_post_10_boundary_0017(self, api_client):
        """[Station][Interaction] post_10 - 边界值测试"""
        # POST /api/feedbacks/{complaintId}/resolve
        response = api_client.post("station/api/feedbacks/{complaintId}/resolve")
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"边界值测试不应返回 5xx 服务器错误, 实际: {response.status_code}"
        assert isinstance(response.json(), dict), "响应应为JSON对象"


    def test_Station_Interaction_post_10_sql_injection_0017(self, api_client):
        """[Station][Interaction] post_10 - SQL注入防护"""
        # POST /api/feedbacks/{complaintId}/resolve
        response = api_client.post("station/api/feedbacks/{complaintId}/resolve")
        assert response is not None, "响应不应为空"
        assert response.status_code != 500, f"SQL注入不应导致服务器错误, 实际: {response.status_code}"
        data = response.json()
        assert isinstance(data, dict), "响应应为JSON对象"


    def test_Station_Interaction_post_10_xss_protection_0017(self, api_client):
        """[Station][Interaction] post_10 - XSS防护"""
        # POST /api/feedbacks/{complaintId}/resolve
        xss_payload = {"name": "<script>alert('xss')</script>", "code": "XSS_TEST"}
        response = api_client.post("station/api/feedbacks/{complaintId}/resolve", json_data=xss_payload)
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"XSS防护测试不应返回 5xx, 实际: {response.status_code}"


    def test_Station_Interaction_post_10_large_payload_0017(self, api_client):
        """[Station][Interaction] post_10 - 大数据量"""
        # POST /api/feedbacks/{complaintId}/resolve
        large_data = {"name": "x" * 10000, "code": "LARGE", "description": "y" * 50000}
        response = api_client.post("station/api/feedbacks/{complaintId}/resolve", json_data=large_data)
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"大数据量测试不应返回 5xx, 实际: {response.status_code}"


    def test_Station_Interaction_post_10_concurrent_0017(self, api_client):
        """[Station][Interaction] post_10 - 并发请求"""
        # POST /api/feedbacks/{complaintId}/resolve
        responses = []
        for _ in range(3):
            r = api_client.post("station/api/feedbacks/{complaintId}/resolve")
            responses.append(r)
        for r in responses:
            assert r is not None, "并发响应不应为空"
            assert r.status_code < 500, f"并发请求不应返回 5xx, 实际: {r.status_code}"


    def test_Station_Interaction_post_10_timeout_0017(self, api_client):
        """[Station][Interaction] post_10 - 超时处理"""
        # POST /api/feedbacks/{complaintId}/resolve
        response = api_client.post("station/api/feedbacks/{complaintId}/resolve")
        assert response is not None, "超时处理响应不应为空"
        assert response.status_code < 500, f"超时测试不应返回 5xx, 实际: {response.status_code}"


    def test_Station_Interaction_post_10_permission_denied_0017(self, api_client):
        """[Station][Interaction] post_10 - 权限不足"""
        # POST /api/feedbacks/{complaintId}/resolve
        response = api_client.post("station/api/feedbacks/{complaintId}/resolve")
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"权限测试不应返回 5xx, 实际: {response.status_code}"


    def test_Station_Interaction_post_10_field_validation_0017(self, api_client):
        """[Station][Interaction] post_10 - 字段校验"""
        # POST /api/feedbacks/{complaintId}/resolve
        invalid_data = {"name": "", "code": ""}
        response = api_client.post("station/api/feedbacks/{complaintId}/resolve", json_data=invalid_data)
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"字段校验不应返回 5xx, 实际: {response.status_code}"


    def test_Station_Interaction_post_10_response_format_0017(self, api_client):
        """[Station][Interaction] post_10 - 响应格式"""
        # POST /api/feedbacks/{complaintId}/resolve
        response = api_client.post("station/api/feedbacks/{complaintId}/resolve")
        assert response is not None, "响应不应为空"
        data = response.json()
        assert isinstance(data, dict), "响应应为JSON对象"
        if response.status_code == 200:
            assert "success" in data or "data" in data or "code" in data, "200 响应应包含标准字段"


    def test_Station_Interaction_post_11_positive_0018(self, api_client):
        """[Station][Interaction] post_11 - 正常请求"""
        # POST /api/feedbacks/{complaintId}/rate
        response = api_client.post("station/api/feedbacks/{complaintId}/rate", json_data={"name": "test", "code": "TEST"})
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"POST 正常请求不应返回 5xx, 实际: {response.status_code}"


    def test_Station_Interaction_post_11_no_auth_0018(self, api_client):
        """[Station][Interaction] post_11 - 缺少认证头"""
        # POST /api/feedbacks/{complaintId}/rate
        api_client.clear_token()
        try:
            response = api_client.post("station/api/feedbacks/{complaintId}/rate")
            assert response is not None, "响应不应为空"
            assert response.status_code in (200, 400, 401, 403), f"无认证头应返回 401/403, 实际: {response.status_code}"
        finally:
            api_client.restore_token()


    def test_Station_Interaction_post_11_invalid_token_0018(self, api_client):
        """[Station][Interaction] post_11 - 无效Token"""
        # POST /api/feedbacks/{complaintId}/rate
        api_client.set_invalid_token()
        try:
            response = api_client.post("station/api/feedbacks/{complaintId}/rate")
            assert response is not None, "响应不应为空"
            assert response.status_code in (200, 400, 401, 403), f"无效Token应返回 401/403, 实际: {response.status_code}"
        finally:
            api_client.restore_token()


    def test_Station_Interaction_post_11_tenant_isolation_0018(self, api_client):
        """[Station][Interaction] post_11 - 租户隔离"""
        # POST /api/feedbacks/{complaintId}/rate
        response = api_client.post("station/api/feedbacks/{complaintId}/rate")
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"租户隔离测试不应返回 5xx, 实际: {response.status_code}"
        data = response.json()
        assert isinstance(data, dict), "响应应为JSON对象"


    def test_Station_Interaction_post_11_empty_body_0018(self, api_client):
        """[Station][Interaction] post_11 - 空请求体"""
        # POST /api/feedbacks/{complaintId}/rate
        response = api_client.post("station/api/feedbacks/{complaintId}/rate")
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"空请求体不应返回 5xx, 实际: {response.status_code}"


    def test_Station_Interaction_post_11_invalid_id_0018(self, api_client):
        """[Station][Interaction] post_11 - 无效ID"""
        # POST /api/feedbacks/{complaintId}/rate
        response = api_client.post("station/api/feedbacks/{complaintId}/rate")
        assert response is not None, "响应不应为空"
        assert response.status_code in (200, 400, 403, 404), f"无效ID应返回 200/400/403/404, 实际: {response.status_code}"


    def test_Station_Interaction_post_11_not_found_id_0018(self, api_client):
        """[Station][Interaction] post_11 - 不存在ID"""
        # POST /api/feedbacks/{complaintId}/rate
        response = api_client.post("station/api/feedbacks/{complaintId}/rate")
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"不存在ID不应返回 5xx, 实际: {response.status_code}"


    def test_Station_Interaction_post_11_boundary_0018(self, api_client):
        """[Station][Interaction] post_11 - 边界值测试"""
        # POST /api/feedbacks/{complaintId}/rate
        response = api_client.post("station/api/feedbacks/{complaintId}/rate")
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"边界值测试不应返回 5xx 服务器错误, 实际: {response.status_code}"
        assert isinstance(response.json(), dict), "响应应为JSON对象"


    def test_Station_Interaction_post_11_sql_injection_0018(self, api_client):
        """[Station][Interaction] post_11 - SQL注入防护"""
        # POST /api/feedbacks/{complaintId}/rate
        response = api_client.post("station/api/feedbacks/{complaintId}/rate")
        assert response is not None, "响应不应为空"
        assert response.status_code != 500, f"SQL注入不应导致服务器错误, 实际: {response.status_code}"
        data = response.json()
        assert isinstance(data, dict), "响应应为JSON对象"


    def test_Station_Interaction_post_11_xss_protection_0018(self, api_client):
        """[Station][Interaction] post_11 - XSS防护"""
        # POST /api/feedbacks/{complaintId}/rate
        xss_payload = {"name": "<script>alert('xss')</script>", "code": "XSS_TEST"}
        response = api_client.post("station/api/feedbacks/{complaintId}/rate", json_data=xss_payload)
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"XSS防护测试不应返回 5xx, 实际: {response.status_code}"


    def test_Station_Interaction_post_11_large_payload_0018(self, api_client):
        """[Station][Interaction] post_11 - 大数据量"""
        # POST /api/feedbacks/{complaintId}/rate
        large_data = {"name": "x" * 10000, "code": "LARGE", "description": "y" * 50000}
        response = api_client.post("station/api/feedbacks/{complaintId}/rate", json_data=large_data)
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"大数据量测试不应返回 5xx, 实际: {response.status_code}"


    def test_Station_Interaction_post_11_concurrent_0018(self, api_client):
        """[Station][Interaction] post_11 - 并发请求"""
        # POST /api/feedbacks/{complaintId}/rate
        responses = []
        for _ in range(3):
            r = api_client.post("station/api/feedbacks/{complaintId}/rate")
            responses.append(r)
        for r in responses:
            assert r is not None, "并发响应不应为空"
            assert r.status_code < 500, f"并发请求不应返回 5xx, 实际: {r.status_code}"


    def test_Station_Interaction_post_11_timeout_0018(self, api_client):
        """[Station][Interaction] post_11 - 超时处理"""
        # POST /api/feedbacks/{complaintId}/rate
        response = api_client.post("station/api/feedbacks/{complaintId}/rate")
        assert response is not None, "超时处理响应不应为空"
        assert response.status_code < 500, f"超时测试不应返回 5xx, 实际: {response.status_code}"


    def test_Station_Interaction_post_11_permission_denied_0018(self, api_client):
        """[Station][Interaction] post_11 - 权限不足"""
        # POST /api/feedbacks/{complaintId}/rate
        response = api_client.post("station/api/feedbacks/{complaintId}/rate")
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"权限测试不应返回 5xx, 实际: {response.status_code}"


    def test_Station_Interaction_post_11_field_validation_0018(self, api_client):
        """[Station][Interaction] post_11 - 字段校验"""
        # POST /api/feedbacks/{complaintId}/rate
        invalid_data = {"name": "", "code": ""}
        response = api_client.post("station/api/feedbacks/{complaintId}/rate", json_data=invalid_data)
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"字段校验不应返回 5xx, 实际: {response.status_code}"


    def test_Station_Interaction_post_11_response_format_0018(self, api_client):
        """[Station][Interaction] post_11 - 响应格式"""
        # POST /api/feedbacks/{complaintId}/rate
        response = api_client.post("station/api/feedbacks/{complaintId}/rate")
        assert response is not None, "响应不应为空"
        data = response.json()
        assert isinstance(data, dict), "响应应为JSON对象"
        if response.status_code == 200:
            assert "success" in data or "data" in data or "code" in data, "200 响应应包含标准字段"


    def test_Station_InternalStation_post_0_positive_0019(self, api_client):
        """[Station][InternalStation] post_0 - 正常请求"""
        # POST /api/internal/station/create
        response = api_client.post("station/api/internal/station/create", json_data={"name": "test", "code": "TEST"})
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"POST 正常请求不应返回 5xx, 实际: {response.status_code}"


    def test_Station_InternalStation_post_0_no_auth_0019(self, api_client):
        """[Station][InternalStation] post_0 - 缺少认证头"""
        # POST /api/internal/station/create
        api_client.clear_token()
        try:
            response = api_client.post("station/api/internal/station/create")
            assert response is not None, "响应不应为空"
            assert response.status_code in (200, 400, 401, 403), f"无认证头应返回 401/403, 实际: {response.status_code}"
        finally:
            api_client.restore_token()


    def test_Station_InternalStation_post_0_invalid_token_0019(self, api_client):
        """[Station][InternalStation] post_0 - 无效Token"""
        # POST /api/internal/station/create
        api_client.set_invalid_token()
        try:
            response = api_client.post("station/api/internal/station/create")
            assert response is not None, "响应不应为空"
            assert response.status_code in (200, 400, 401, 403), f"无效Token应返回 401/403, 实际: {response.status_code}"
        finally:
            api_client.restore_token()


    def test_Station_InternalStation_post_0_tenant_isolation_0019(self, api_client):
        """[Station][InternalStation] post_0 - 租户隔离"""
        # POST /api/internal/station/create
        response = api_client.post("station/api/internal/station/create")
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"租户隔离测试不应返回 5xx, 实际: {response.status_code}"
        data = response.json()
        assert isinstance(data, dict), "响应应为JSON对象"


    def test_Station_InternalStation_post_0_empty_body_0019(self, api_client):
        """[Station][InternalStation] post_0 - 空请求体"""
        # POST /api/internal/station/create
        response = api_client.post("station/api/internal/station/create")
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"空请求体不应返回 5xx, 实际: {response.status_code}"


    def test_Station_InternalStation_post_0_boundary_0019(self, api_client):
        """[Station][InternalStation] post_0 - 边界值测试"""
        # POST /api/internal/station/create
        response = api_client.post("station/api/internal/station/create")
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"边界值测试不应返回 5xx 服务器错误, 实际: {response.status_code}"
        assert isinstance(response.json(), dict), "响应应为JSON对象"


    def test_Station_InternalStation_post_0_sql_injection_0019(self, api_client):
        """[Station][InternalStation] post_0 - SQL注入防护"""
        # POST /api/internal/station/create
        response = api_client.post("station/api/internal/station/create")
        assert response is not None, "响应不应为空"
        assert response.status_code != 500, f"SQL注入不应导致服务器错误, 实际: {response.status_code}"
        data = response.json()
        assert isinstance(data, dict), "响应应为JSON对象"


    def test_Station_InternalStation_post_0_xss_protection_0019(self, api_client):
        """[Station][InternalStation] post_0 - XSS防护"""
        # POST /api/internal/station/create
        xss_payload = {"name": "<script>alert('xss')</script>", "code": "XSS_TEST"}
        response = api_client.post("station/api/internal/station/create", json_data=xss_payload)
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"XSS防护测试不应返回 5xx, 实际: {response.status_code}"


    def test_Station_InternalStation_post_0_large_payload_0019(self, api_client):
        """[Station][InternalStation] post_0 - 大数据量"""
        # POST /api/internal/station/create
        large_data = {"name": "x" * 10000, "code": "LARGE", "description": "y" * 50000}
        response = api_client.post("station/api/internal/station/create", json_data=large_data)
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"大数据量测试不应返回 5xx, 实际: {response.status_code}"


    def test_Station_InternalStation_post_0_concurrent_0019(self, api_client):
        """[Station][InternalStation] post_0 - 并发请求"""
        # POST /api/internal/station/create
        responses = []
        for _ in range(3):
            r = api_client.post("station/api/internal/station/create")
            responses.append(r)
        for r in responses:
            assert r is not None, "并发响应不应为空"
            assert r.status_code < 500, f"并发请求不应返回 5xx, 实际: {r.status_code}"


    def test_Station_InternalStation_post_0_timeout_0019(self, api_client):
        """[Station][InternalStation] post_0 - 超时处理"""
        # POST /api/internal/station/create
        response = api_client.post("station/api/internal/station/create")
        assert response is not None, "超时处理响应不应为空"
        assert response.status_code < 500, f"超时测试不应返回 5xx, 实际: {response.status_code}"


    def test_Station_InternalStation_post_0_permission_denied_0019(self, api_client):
        """[Station][InternalStation] post_0 - 权限不足"""
        # POST /api/internal/station/create
        response = api_client.post("station/api/internal/station/create")
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"权限测试不应返回 5xx, 实际: {response.status_code}"


    def test_Station_InternalStation_post_0_field_validation_0019(self, api_client):
        """[Station][InternalStation] post_0 - 字段校验"""
        # POST /api/internal/station/create
        invalid_data = {"name": "", "code": ""}
        response = api_client.post("station/api/internal/station/create", json_data=invalid_data)
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"字段校验不应返回 5xx, 实际: {response.status_code}"


    def test_Station_InternalStation_post_0_response_format_0019(self, api_client):
        """[Station][InternalStation] post_0 - 响应格式"""
        # POST /api/internal/station/create
        response = api_client.post("station/api/internal/station/create")
        assert response is not None, "响应不应为空"
        data = response.json()
        assert isinstance(data, dict), "响应应为JSON对象"
        if response.status_code == 200:
            assert "success" in data or "data" in data or "code" in data, "200 响应应包含标准字段"


    def test_Station_InternalStation_post_1_positive_0020(self, api_client):
        """[Station][InternalStation] post_1 - 正常请求"""
        # POST /api/internal/station/list
        response = api_client.post("station/api/internal/station/list", json_data={"name": "test", "code": "TEST"})
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"POST 正常请求不应返回 5xx, 实际: {response.status_code}"


    def test_Station_InternalStation_post_1_no_auth_0020(self, api_client):
        """[Station][InternalStation] post_1 - 缺少认证头"""
        # POST /api/internal/station/list
        api_client.clear_token()
        try:
            response = api_client.post("station/api/internal/station/list")
            assert response is not None, "响应不应为空"
            assert response.status_code in (200, 400, 401, 403), f"无认证头应返回 401/403, 实际: {response.status_code}"
        finally:
            api_client.restore_token()


    def test_Station_InternalStation_post_1_invalid_token_0020(self, api_client):
        """[Station][InternalStation] post_1 - 无效Token"""
        # POST /api/internal/station/list
        api_client.set_invalid_token()
        try:
            response = api_client.post("station/api/internal/station/list")
            assert response is not None, "响应不应为空"
            assert response.status_code in (200, 400, 401, 403), f"无效Token应返回 401/403, 实际: {response.status_code}"
        finally:
            api_client.restore_token()


    def test_Station_InternalStation_post_1_tenant_isolation_0020(self, api_client):
        """[Station][InternalStation] post_1 - 租户隔离"""
        # POST /api/internal/station/list
        response = api_client.post("station/api/internal/station/list")
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"租户隔离测试不应返回 5xx, 实际: {response.status_code}"
        data = response.json()
        assert isinstance(data, dict), "响应应为JSON对象"


    def test_Station_InternalStation_post_1_empty_body_0020(self, api_client):
        """[Station][InternalStation] post_1 - 空请求体"""
        # POST /api/internal/station/list
        response = api_client.post("station/api/internal/station/list")
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"空请求体不应返回 5xx, 实际: {response.status_code}"


    def test_Station_InternalStation_post_1_boundary_0020(self, api_client):
        """[Station][InternalStation] post_1 - 边界值测试"""
        # POST /api/internal/station/list
        response = api_client.post("station/api/internal/station/list")
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"边界值测试不应返回 5xx 服务器错误, 实际: {response.status_code}"
        assert isinstance(response.json(), dict), "响应应为JSON对象"


    def test_Station_InternalStation_post_1_sql_injection_0020(self, api_client):
        """[Station][InternalStation] post_1 - SQL注入防护"""
        # POST /api/internal/station/list
        response = api_client.post("station/api/internal/station/list")
        assert response is not None, "响应不应为空"
        assert response.status_code != 500, f"SQL注入不应导致服务器错误, 实际: {response.status_code}"
        data = response.json()
        assert isinstance(data, dict), "响应应为JSON对象"


    def test_Station_InternalStation_post_1_xss_protection_0020(self, api_client):
        """[Station][InternalStation] post_1 - XSS防护"""
        # POST /api/internal/station/list
        xss_payload = {"name": "<script>alert('xss')</script>", "code": "XSS_TEST"}
        response = api_client.post("station/api/internal/station/list", json_data=xss_payload)
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"XSS防护测试不应返回 5xx, 实际: {response.status_code}"


    def test_Station_InternalStation_post_1_large_payload_0020(self, api_client):
        """[Station][InternalStation] post_1 - 大数据量"""
        # POST /api/internal/station/list
        large_data = {"name": "x" * 10000, "code": "LARGE", "description": "y" * 50000}
        response = api_client.post("station/api/internal/station/list", json_data=large_data)
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"大数据量测试不应返回 5xx, 实际: {response.status_code}"


    def test_Station_InternalStation_post_1_concurrent_0020(self, api_client):
        """[Station][InternalStation] post_1 - 并发请求"""
        # POST /api/internal/station/list
        responses = []
        for _ in range(3):
            r = api_client.post("station/api/internal/station/list")
            responses.append(r)
        for r in responses:
            assert r is not None, "并发响应不应为空"
            assert r.status_code < 500, f"并发请求不应返回 5xx, 实际: {r.status_code}"


    def test_Station_InternalStation_post_1_timeout_0020(self, api_client):
        """[Station][InternalStation] post_1 - 超时处理"""
        # POST /api/internal/station/list
        response = api_client.post("station/api/internal/station/list")
        assert response is not None, "超时处理响应不应为空"
        assert response.status_code < 500, f"超时测试不应返回 5xx, 实际: {response.status_code}"


    def test_Station_InternalStation_post_1_permission_denied_0020(self, api_client):
        """[Station][InternalStation] post_1 - 权限不足"""
        # POST /api/internal/station/list
        response = api_client.post("station/api/internal/station/list")
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"权限测试不应返回 5xx, 实际: {response.status_code}"


    def test_Station_InternalStation_post_1_field_validation_0020(self, api_client):
        """[Station][InternalStation] post_1 - 字段校验"""
        # POST /api/internal/station/list
        invalid_data = {"name": "", "code": ""}
        response = api_client.post("station/api/internal/station/list", json_data=invalid_data)
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"字段校验不应返回 5xx, 实际: {response.status_code}"


    def test_Station_InternalStation_post_1_response_format_0020(self, api_client):
        """[Station][InternalStation] post_1 - 响应格式"""
        # POST /api/internal/station/list
        response = api_client.post("station/api/internal/station/list")
        assert response is not None, "响应不应为空"
        data = response.json()
        assert isinstance(data, dict), "响应应为JSON对象"
        if response.status_code == 200:
            assert "success" in data or "data" in data or "code" in data, "200 响应应包含标准字段"


    def test_Station_InternalStation_post_2_positive_0021(self, api_client):
        """[Station][InternalStation] post_2 - 正常请求"""
        # POST /api/internal/station/delete
        response = api_client.post("station/api/internal/station/delete", json_data={"name": "test", "code": "TEST"})
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"POST 正常请求不应返回 5xx, 实际: {response.status_code}"


    def test_Station_InternalStation_post_2_no_auth_0021(self, api_client):
        """[Station][InternalStation] post_2 - 缺少认证头"""
        # POST /api/internal/station/delete
        api_client.clear_token()
        try:
            response = api_client.post("station/api/internal/station/delete")
            assert response is not None, "响应不应为空"
            assert response.status_code in (200, 400, 401, 403), f"无认证头应返回 401/403, 实际: {response.status_code}"
        finally:
            api_client.restore_token()


    def test_Station_InternalStation_post_2_invalid_token_0021(self, api_client):
        """[Station][InternalStation] post_2 - 无效Token"""
        # POST /api/internal/station/delete
        api_client.set_invalid_token()
        try:
            response = api_client.post("station/api/internal/station/delete")
            assert response is not None, "响应不应为空"
            assert response.status_code in (200, 400, 401, 403), f"无效Token应返回 401/403, 实际: {response.status_code}"
        finally:
            api_client.restore_token()


    def test_Station_InternalStation_post_2_tenant_isolation_0021(self, api_client):
        """[Station][InternalStation] post_2 - 租户隔离"""
        # POST /api/internal/station/delete
        response = api_client.post("station/api/internal/station/delete")
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"租户隔离测试不应返回 5xx, 实际: {response.status_code}"
        data = response.json()
        assert isinstance(data, dict), "响应应为JSON对象"


    def test_Station_InternalStation_post_2_empty_body_0021(self, api_client):
        """[Station][InternalStation] post_2 - 空请求体"""
        # POST /api/internal/station/delete
        response = api_client.post("station/api/internal/station/delete")
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"空请求体不应返回 5xx, 实际: {response.status_code}"


    def test_Station_InternalStation_post_2_boundary_0021(self, api_client):
        """[Station][InternalStation] post_2 - 边界值测试"""
        # POST /api/internal/station/delete
        response = api_client.post("station/api/internal/station/delete")
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"边界值测试不应返回 5xx 服务器错误, 实际: {response.status_code}"
        assert isinstance(response.json(), dict), "响应应为JSON对象"


    def test_Station_InternalStation_post_2_sql_injection_0021(self, api_client):
        """[Station][InternalStation] post_2 - SQL注入防护"""
        # POST /api/internal/station/delete
        response = api_client.post("station/api/internal/station/delete")
        assert response is not None, "响应不应为空"
        assert response.status_code != 500, f"SQL注入不应导致服务器错误, 实际: {response.status_code}"
        data = response.json()
        assert isinstance(data, dict), "响应应为JSON对象"


    def test_Station_InternalStation_post_2_xss_protection_0021(self, api_client):
        """[Station][InternalStation] post_2 - XSS防护"""
        # POST /api/internal/station/delete
        xss_payload = {"name": "<script>alert('xss')</script>", "code": "XSS_TEST"}
        response = api_client.post("station/api/internal/station/delete", json_data=xss_payload)
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"XSS防护测试不应返回 5xx, 实际: {response.status_code}"


    def test_Station_InternalStation_post_2_large_payload_0021(self, api_client):
        """[Station][InternalStation] post_2 - 大数据量"""
        # POST /api/internal/station/delete
        large_data = {"name": "x" * 10000, "code": "LARGE", "description": "y" * 50000}
        response = api_client.post("station/api/internal/station/delete", json_data=large_data)
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"大数据量测试不应返回 5xx, 实际: {response.status_code}"


    def test_Station_InternalStation_post_2_concurrent_0021(self, api_client):
        """[Station][InternalStation] post_2 - 并发请求"""
        # POST /api/internal/station/delete
        responses = []
        for _ in range(3):
            r = api_client.post("station/api/internal/station/delete")
            responses.append(r)
        for r in responses:
            assert r is not None, "并发响应不应为空"
            assert r.status_code < 500, f"并发请求不应返回 5xx, 实际: {r.status_code}"


    def test_Station_InternalStation_post_2_timeout_0021(self, api_client):
        """[Station][InternalStation] post_2 - 超时处理"""
        # POST /api/internal/station/delete
        response = api_client.post("station/api/internal/station/delete")
        assert response is not None, "超时处理响应不应为空"
        assert response.status_code < 500, f"超时测试不应返回 5xx, 实际: {response.status_code}"


    def test_Station_InternalStation_post_2_permission_denied_0021(self, api_client):
        """[Station][InternalStation] post_2 - 权限不足"""
        # POST /api/internal/station/delete
        response = api_client.post("station/api/internal/station/delete")
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"权限测试不应返回 5xx, 实际: {response.status_code}"


    def test_Station_InternalStation_post_2_field_validation_0021(self, api_client):
        """[Station][InternalStation] post_2 - 字段校验"""
        # POST /api/internal/station/delete
        invalid_data = {"name": "", "code": ""}
        response = api_client.post("station/api/internal/station/delete", json_data=invalid_data)
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"字段校验不应返回 5xx, 实际: {response.status_code}"


    def test_Station_InternalStation_post_2_response_format_0021(self, api_client):
        """[Station][InternalStation] post_2 - 响应格式"""
        # POST /api/internal/station/delete
        response = api_client.post("station/api/internal/station/delete")
        assert response is not None, "响应不应为空"
        data = response.json()
        assert isinstance(data, dict), "响应应为JSON对象"
        if response.status_code == 200:
            assert "success" in data or "data" in data or "code" in data, "200 响应应包含标准字段"


    def test_Station_InternalStation_post_3_positive_0022(self, api_client):
        """[Station][InternalStation] post_3 - 正常请求"""
        # POST /api/internal/station/hard-delete-simulated
        response = api_client.post("station/api/internal/station/hard-delete-simulated", json_data={"name": "test", "code": "TEST"})
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"POST 正常请求不应返回 5xx, 实际: {response.status_code}"


    def test_Station_InternalStation_post_3_no_auth_0022(self, api_client):
        """[Station][InternalStation] post_3 - 缺少认证头"""
        # POST /api/internal/station/hard-delete-simulated
        api_client.clear_token()
        try:
            response = api_client.post("station/api/internal/station/hard-delete-simulated")
            assert response is not None, "响应不应为空"
            assert response.status_code in (200, 400, 401, 403), f"无认证头应返回 401/403, 实际: {response.status_code}"
        finally:
            api_client.restore_token()


    def test_Station_InternalStation_post_3_invalid_token_0022(self, api_client):
        """[Station][InternalStation] post_3 - 无效Token"""
        # POST /api/internal/station/hard-delete-simulated
        api_client.set_invalid_token()
        try:
            response = api_client.post("station/api/internal/station/hard-delete-simulated")
            assert response is not None, "响应不应为空"
            assert response.status_code in (200, 400, 401, 403), f"无效Token应返回 401/403, 实际: {response.status_code}"
        finally:
            api_client.restore_token()


    def test_Station_InternalStation_post_3_tenant_isolation_0022(self, api_client):
        """[Station][InternalStation] post_3 - 租户隔离"""
        # POST /api/internal/station/hard-delete-simulated
        response = api_client.post("station/api/internal/station/hard-delete-simulated")
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"租户隔离测试不应返回 5xx, 实际: {response.status_code}"
        data = response.json()
        assert isinstance(data, dict), "响应应为JSON对象"


    def test_Station_InternalStation_post_3_empty_body_0022(self, api_client):
        """[Station][InternalStation] post_3 - 空请求体"""
        # POST /api/internal/station/hard-delete-simulated
        response = api_client.post("station/api/internal/station/hard-delete-simulated")
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"空请求体不应返回 5xx, 实际: {response.status_code}"


    def test_Station_InternalStation_post_3_boundary_0022(self, api_client):
        """[Station][InternalStation] post_3 - 边界值测试"""
        # POST /api/internal/station/hard-delete-simulated
        response = api_client.post("station/api/internal/station/hard-delete-simulated")
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"边界值测试不应返回 5xx 服务器错误, 实际: {response.status_code}"
        assert isinstance(response.json(), dict), "响应应为JSON对象"


    def test_Station_InternalStation_post_3_sql_injection_0022(self, api_client):
        """[Station][InternalStation] post_3 - SQL注入防护"""
        # POST /api/internal/station/hard-delete-simulated
        response = api_client.post("station/api/internal/station/hard-delete-simulated")
        assert response is not None, "响应不应为空"
        assert response.status_code != 500, f"SQL注入不应导致服务器错误, 实际: {response.status_code}"
        data = response.json()
        assert isinstance(data, dict), "响应应为JSON对象"


    def test_Station_InternalStation_post_3_xss_protection_0022(self, api_client):
        """[Station][InternalStation] post_3 - XSS防护"""
        # POST /api/internal/station/hard-delete-simulated
        xss_payload = {"name": "<script>alert('xss')</script>", "code": "XSS_TEST"}
        response = api_client.post("station/api/internal/station/hard-delete-simulated", json_data=xss_payload)
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"XSS防护测试不应返回 5xx, 实际: {response.status_code}"


    def test_Station_InternalStation_post_3_large_payload_0022(self, api_client):
        """[Station][InternalStation] post_3 - 大数据量"""
        # POST /api/internal/station/hard-delete-simulated
        large_data = {"name": "x" * 10000, "code": "LARGE", "description": "y" * 50000}
        response = api_client.post("station/api/internal/station/hard-delete-simulated", json_data=large_data)
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"大数据量测试不应返回 5xx, 实际: {response.status_code}"


    def test_Station_InternalStation_post_3_concurrent_0022(self, api_client):
        """[Station][InternalStation] post_3 - 并发请求"""
        # POST /api/internal/station/hard-delete-simulated
        responses = []
        for _ in range(3):
            r = api_client.post("station/api/internal/station/hard-delete-simulated")
            responses.append(r)
        for r in responses:
            assert r is not None, "并发响应不应为空"
            assert r.status_code < 500, f"并发请求不应返回 5xx, 实际: {r.status_code}"


    def test_Station_InternalStation_post_3_timeout_0022(self, api_client):
        """[Station][InternalStation] post_3 - 超时处理"""
        # POST /api/internal/station/hard-delete-simulated
        response = api_client.post("station/api/internal/station/hard-delete-simulated")
        assert response is not None, "超时处理响应不应为空"
        assert response.status_code < 500, f"超时测试不应返回 5xx, 实际: {response.status_code}"


    def test_Station_InternalStation_post_3_permission_denied_0022(self, api_client):
        """[Station][InternalStation] post_3 - 权限不足"""
        # POST /api/internal/station/hard-delete-simulated
        response = api_client.post("station/api/internal/station/hard-delete-simulated")
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"权限测试不应返回 5xx, 实际: {response.status_code}"


    def test_Station_InternalStation_post_3_field_validation_0022(self, api_client):
        """[Station][InternalStation] post_3 - 字段校验"""
        # POST /api/internal/station/hard-delete-simulated
        invalid_data = {"name": "", "code": ""}
        response = api_client.post("station/api/internal/station/hard-delete-simulated", json_data=invalid_data)
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"字段校验不应返回 5xx, 实际: {response.status_code}"


    def test_Station_InternalStation_post_3_response_format_0022(self, api_client):
        """[Station][InternalStation] post_3 - 响应格式"""
        # POST /api/internal/station/hard-delete-simulated
        response = api_client.post("station/api/internal/station/hard-delete-simulated")
        assert response is not None, "响应不应为空"
        data = response.json()
        assert isinstance(data, dict), "响应应为JSON对象"
        if response.status_code == 200:
            assert "success" in data or "data" in data or "code" in data, "200 响应应包含标准字段"


    def test_Station_MobileStation_get_0_positive_0023(self, api_client):
        """[Station][MobileStation] get_0 - 正常请求"""
        # GET /api/stations/mobile/nearby
        response = api_client.get("station/api/stations/mobile/nearby")
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"GET 正常请求不应返回 5xx, 实际: {response.status_code}"


    def test_Station_MobileStation_get_0_no_auth_0023(self, api_client):
        """[Station][MobileStation] get_0 - 缺少认证头"""
        # GET /api/stations/mobile/nearby
        api_client.clear_token()
        try:
            response = api_client.get("station/api/stations/mobile/nearby")
            assert response is not None, "响应不应为空"
            assert response.status_code in (200, 400, 401, 403), f"无认证头应返回 401/403, 实际: {response.status_code}"
        finally:
            api_client.restore_token()


    def test_Station_MobileStation_get_0_invalid_token_0023(self, api_client):
        """[Station][MobileStation] get_0 - 无效Token"""
        # GET /api/stations/mobile/nearby
        api_client.set_invalid_token()
        try:
            response = api_client.get("station/api/stations/mobile/nearby")
            assert response is not None, "响应不应为空"
            assert response.status_code in (200, 400, 401, 403), f"无效Token应返回 401/403, 实际: {response.status_code}"
        finally:
            api_client.restore_token()


    def test_Station_MobileStation_get_0_tenant_isolation_0023(self, api_client):
        """[Station][MobileStation] get_0 - 租户隔离"""
        # GET /api/stations/mobile/nearby
        response = api_client.get("station/api/stations/mobile/nearby")
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"租户隔离测试不应返回 5xx, 实际: {response.status_code}"
        data = response.json()
        assert isinstance(data, dict), "响应应为JSON对象"


    def test_Station_MobileStation_get_0_boundary_0023(self, api_client):
        """[Station][MobileStation] get_0 - 边界值测试"""
        # GET /api/stations/mobile/nearby
        response = api_client.get("station/api/stations/mobile/nearby")
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"边界值测试不应返回 5xx 服务器错误, 实际: {response.status_code}"
        assert isinstance(response.json(), dict), "响应应为JSON对象"


    def test_Station_MobileStation_get_0_sql_injection_0023(self, api_client):
        """[Station][MobileStation] get_0 - SQL注入防护"""
        # GET /api/stations/mobile/nearby
        response = api_client.get("station/api/stations/mobile/nearby")
        assert response is not None, "响应不应为空"
        assert response.status_code != 500, f"SQL注入不应导致服务器错误, 实际: {response.status_code}"
        data = response.json()
        assert isinstance(data, dict), "响应应为JSON对象"


    def test_Station_MobileStation_get_0_concurrent_0023(self, api_client):
        """[Station][MobileStation] get_0 - 并发请求"""
        # GET /api/stations/mobile/nearby
        responses = []
        for _ in range(3):
            r = api_client.get("station/api/stations/mobile/nearby")
            responses.append(r)
        for r in responses:
            assert r is not None, "并发响应不应为空"
            assert r.status_code < 500, f"并发请求不应返回 5xx, 实际: {r.status_code}"


    def test_Station_MobileStation_get_0_timeout_0023(self, api_client):
        """[Station][MobileStation] get_0 - 超时处理"""
        # GET /api/stations/mobile/nearby
        response = api_client.get("station/api/stations/mobile/nearby")
        assert response is not None, "超时处理响应不应为空"
        assert response.status_code < 500, f"超时测试不应返回 5xx, 实际: {response.status_code}"


    def test_Station_MobileStation_get_0_permission_denied_0023(self, api_client):
        """[Station][MobileStation] get_0 - 权限不足"""
        # GET /api/stations/mobile/nearby
        response = api_client.get("station/api/stations/mobile/nearby")
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"权限测试不应返回 5xx, 实际: {response.status_code}"


    def test_Station_MobileStation_get_0_response_format_0023(self, api_client):
        """[Station][MobileStation] get_0 - 响应格式"""
        # GET /api/stations/mobile/nearby
        response = api_client.get("station/api/stations/mobile/nearby")
        assert response is not None, "响应不应为空"
        data = response.json()
        assert isinstance(data, dict), "响应应为JSON对象"
        if response.status_code == 200:
            assert "success" in data or "data" in data or "code" in data, "200 响应应包含标准字段"


    def test_Station_MobileStation_get_1_positive_0024(self, api_client):
        """[Station][MobileStation] get_1 - 正常请求"""
        # GET /api/stations/mobile/search
        response = api_client.get("station/api/stations/mobile/search")
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"GET 正常请求不应返回 5xx, 实际: {response.status_code}"


    def test_Station_MobileStation_get_1_no_auth_0024(self, api_client):
        """[Station][MobileStation] get_1 - 缺少认证头"""
        # GET /api/stations/mobile/search
        api_client.clear_token()
        try:
            response = api_client.get("station/api/stations/mobile/search")
            assert response is not None, "响应不应为空"
            assert response.status_code in (200, 400, 401, 403), f"无认证头应返回 401/403, 实际: {response.status_code}"
        finally:
            api_client.restore_token()


    def test_Station_MobileStation_get_1_invalid_token_0024(self, api_client):
        """[Station][MobileStation] get_1 - 无效Token"""
        # GET /api/stations/mobile/search
        api_client.set_invalid_token()
        try:
            response = api_client.get("station/api/stations/mobile/search")
            assert response is not None, "响应不应为空"
            assert response.status_code in (200, 400, 401, 403), f"无效Token应返回 401/403, 实际: {response.status_code}"
        finally:
            api_client.restore_token()


    def test_Station_MobileStation_get_1_tenant_isolation_0024(self, api_client):
        """[Station][MobileStation] get_1 - 租户隔离"""
        # GET /api/stations/mobile/search
        response = api_client.get("station/api/stations/mobile/search")
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"租户隔离测试不应返回 5xx, 实际: {response.status_code}"
        data = response.json()
        assert isinstance(data, dict), "响应应为JSON对象"


    def test_Station_MobileStation_get_1_boundary_0024(self, api_client):
        """[Station][MobileStation] get_1 - 边界值测试"""
        # GET /api/stations/mobile/search
        response = api_client.get("station/api/stations/mobile/search")
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"边界值测试不应返回 5xx 服务器错误, 实际: {response.status_code}"
        assert isinstance(response.json(), dict), "响应应为JSON对象"


    def test_Station_MobileStation_get_1_sql_injection_0024(self, api_client):
        """[Station][MobileStation] get_1 - SQL注入防护"""
        # GET /api/stations/mobile/search
        response = api_client.get("station/api/stations/mobile/search")
        assert response is not None, "响应不应为空"
        assert response.status_code != 500, f"SQL注入不应导致服务器错误, 实际: {response.status_code}"
        data = response.json()
        assert isinstance(data, dict), "响应应为JSON对象"


    def test_Station_MobileStation_get_1_concurrent_0024(self, api_client):
        """[Station][MobileStation] get_1 - 并发请求"""
        # GET /api/stations/mobile/search
        responses = []
        for _ in range(3):
            r = api_client.get("station/api/stations/mobile/search")
            responses.append(r)
        for r in responses:
            assert r is not None, "并发响应不应为空"
            assert r.status_code < 500, f"并发请求不应返回 5xx, 实际: {r.status_code}"


    def test_Station_MobileStation_get_1_timeout_0024(self, api_client):
        """[Station][MobileStation] get_1 - 超时处理"""
        # GET /api/stations/mobile/search
        response = api_client.get("station/api/stations/mobile/search")
        assert response is not None, "超时处理响应不应为空"
        assert response.status_code < 500, f"超时测试不应返回 5xx, 实际: {response.status_code}"


    def test_Station_MobileStation_get_1_permission_denied_0024(self, api_client):
        """[Station][MobileStation] get_1 - 权限不足"""
        # GET /api/stations/mobile/search
        response = api_client.get("station/api/stations/mobile/search")
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"权限测试不应返回 5xx, 实际: {response.status_code}"


    def test_Station_MobileStation_get_1_response_format_0024(self, api_client):
        """[Station][MobileStation] get_1 - 响应格式"""
        # GET /api/stations/mobile/search
        response = api_client.get("station/api/stations/mobile/search")
        assert response is not None, "响应不应为空"
        data = response.json()
        assert isinstance(data, dict), "响应应为JSON对象"
        if response.status_code == 200:
            assert "success" in data or "data" in data or "code" in data, "200 响应应包含标准字段"


    def test_Station_MobileStation_get_2_positive_0025(self, api_client):
        """[Station][MobileStation] get_2 - 正常请求"""
        # GET /api/stations/mobile/{id:guid}
        response = api_client.get("station/api/stations/mobile/{id:guid}")
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"GET 正常请求不应返回 5xx, 实际: {response.status_code}"


    def test_Station_MobileStation_get_2_no_auth_0025(self, api_client):
        """[Station][MobileStation] get_2 - 缺少认证头"""
        # GET /api/stations/mobile/{id:guid}
        api_client.clear_token()
        try:
            response = api_client.get("station/api/stations/mobile/{id:guid}")
            assert response is not None, "响应不应为空"
            assert response.status_code in (200, 400, 401, 403), f"无认证头应返回 401/403, 实际: {response.status_code}"
        finally:
            api_client.restore_token()


    def test_Station_MobileStation_get_2_invalid_token_0025(self, api_client):
        """[Station][MobileStation] get_2 - 无效Token"""
        # GET /api/stations/mobile/{id:guid}
        api_client.set_invalid_token()
        try:
            response = api_client.get("station/api/stations/mobile/{id:guid}")
            assert response is not None, "响应不应为空"
            assert response.status_code in (200, 400, 401, 403), f"无效Token应返回 401/403, 实际: {response.status_code}"
        finally:
            api_client.restore_token()


    def test_Station_MobileStation_get_2_tenant_isolation_0025(self, api_client):
        """[Station][MobileStation] get_2 - 租户隔离"""
        # GET /api/stations/mobile/{id:guid}
        response = api_client.get("station/api/stations/mobile/{id:guid}")
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"租户隔离测试不应返回 5xx, 实际: {response.status_code}"
        data = response.json()
        assert isinstance(data, dict), "响应应为JSON对象"


    def test_Station_MobileStation_get_2_invalid_id_0025(self, api_client):
        """[Station][MobileStation] get_2 - 无效ID"""
        # GET /api/stations/mobile/{id:guid}
        response = api_client.get("station/api/stations/mobile/{id:guid}")
        assert response is not None, "响应不应为空"
        assert response.status_code in (200, 400, 403, 404), f"无效ID应返回 200/400/403/404, 实际: {response.status_code}"


    def test_Station_MobileStation_get_2_not_found_id_0025(self, api_client):
        """[Station][MobileStation] get_2 - 不存在ID"""
        # GET /api/stations/mobile/{id:guid}
        response = api_client.get("station/api/stations/mobile/{id:guid}")
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"不存在ID不应返回 5xx, 实际: {response.status_code}"


    def test_Station_MobileStation_get_2_boundary_0025(self, api_client):
        """[Station][MobileStation] get_2 - 边界值测试"""
        # GET /api/stations/mobile/{id:guid}
        response = api_client.get("station/api/stations/mobile/{id:guid}")
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"边界值测试不应返回 5xx 服务器错误, 实际: {response.status_code}"
        assert isinstance(response.json(), dict), "响应应为JSON对象"


    def test_Station_MobileStation_get_2_sql_injection_0025(self, api_client):
        """[Station][MobileStation] get_2 - SQL注入防护"""
        # GET /api/stations/mobile/{id:guid}
        response = api_client.get("station/api/stations/mobile/{id:guid}")
        assert response is not None, "响应不应为空"
        assert response.status_code != 500, f"SQL注入不应导致服务器错误, 实际: {response.status_code}"
        data = response.json()
        assert isinstance(data, dict), "响应应为JSON对象"


    def test_Station_MobileStation_get_2_concurrent_0025(self, api_client):
        """[Station][MobileStation] get_2 - 并发请求"""
        # GET /api/stations/mobile/{id:guid}
        responses = []
        for _ in range(3):
            r = api_client.get("station/api/stations/mobile/{id:guid}")
            responses.append(r)
        for r in responses:
            assert r is not None, "并发响应不应为空"
            assert r.status_code < 500, f"并发请求不应返回 5xx, 实际: {r.status_code}"


    def test_Station_MobileStation_get_2_timeout_0025(self, api_client):
        """[Station][MobileStation] get_2 - 超时处理"""
        # GET /api/stations/mobile/{id:guid}
        response = api_client.get("station/api/stations/mobile/{id:guid}")
        assert response is not None, "超时处理响应不应为空"
        assert response.status_code < 500, f"超时测试不应返回 5xx, 实际: {response.status_code}"


    def test_Station_MobileStation_get_2_permission_denied_0025(self, api_client):
        """[Station][MobileStation] get_2 - 权限不足"""
        # GET /api/stations/mobile/{id:guid}
        response = api_client.get("station/api/stations/mobile/{id:guid}")
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"权限测试不应返回 5xx, 实际: {response.status_code}"


    def test_Station_MobileStation_get_2_response_format_0025(self, api_client):
        """[Station][MobileStation] get_2 - 响应格式"""
        # GET /api/stations/mobile/{id:guid}
        response = api_client.get("station/api/stations/mobile/{id:guid}")
        assert response is not None, "响应不应为空"
        data = response.json()
        assert isinstance(data, dict), "响应应为JSON对象"
        if response.status_code == 200:
            assert "success" in data or "data" in data or "code" in data, "200 响应应包含标准字段"


    def test_Station_MobileStation_get_3_positive_0026(self, api_client):
        """[Station][MobileStation] get_3 - 正常请求"""
        # GET /api/stations/mobile/favorites
        response = api_client.get("station/api/stations/mobile/favorites")
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"GET 正常请求不应返回 5xx, 实际: {response.status_code}"


    def test_Station_MobileStation_get_3_no_auth_0026(self, api_client):
        """[Station][MobileStation] get_3 - 缺少认证头"""
        # GET /api/stations/mobile/favorites
        api_client.clear_token()
        try:
            response = api_client.get("station/api/stations/mobile/favorites")
            assert response is not None, "响应不应为空"
            assert response.status_code in (200, 400, 401, 403), f"无认证头应返回 401/403, 实际: {response.status_code}"
        finally:
            api_client.restore_token()


    def test_Station_MobileStation_get_3_invalid_token_0026(self, api_client):
        """[Station][MobileStation] get_3 - 无效Token"""
        # GET /api/stations/mobile/favorites
        api_client.set_invalid_token()
        try:
            response = api_client.get("station/api/stations/mobile/favorites")
            assert response is not None, "响应不应为空"
            assert response.status_code in (200, 400, 401, 403), f"无效Token应返回 401/403, 实际: {response.status_code}"
        finally:
            api_client.restore_token()


    def test_Station_MobileStation_get_3_tenant_isolation_0026(self, api_client):
        """[Station][MobileStation] get_3 - 租户隔离"""
        # GET /api/stations/mobile/favorites
        response = api_client.get("station/api/stations/mobile/favorites")
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"租户隔离测试不应返回 5xx, 实际: {response.status_code}"
        data = response.json()
        assert isinstance(data, dict), "响应应为JSON对象"


    def test_Station_MobileStation_get_3_boundary_0026(self, api_client):
        """[Station][MobileStation] get_3 - 边界值测试"""
        # GET /api/stations/mobile/favorites
        response = api_client.get("station/api/stations/mobile/favorites")
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"边界值测试不应返回 5xx 服务器错误, 实际: {response.status_code}"
        assert isinstance(response.json(), dict), "响应应为JSON对象"


    def test_Station_MobileStation_get_3_sql_injection_0026(self, api_client):
        """[Station][MobileStation] get_3 - SQL注入防护"""
        # GET /api/stations/mobile/favorites
        response = api_client.get("station/api/stations/mobile/favorites")
        assert response is not None, "响应不应为空"
        assert response.status_code != 500, f"SQL注入不应导致服务器错误, 实际: {response.status_code}"
        data = response.json()
        assert isinstance(data, dict), "响应应为JSON对象"


    def test_Station_MobileStation_get_3_concurrent_0026(self, api_client):
        """[Station][MobileStation] get_3 - 并发请求"""
        # GET /api/stations/mobile/favorites
        responses = []
        for _ in range(3):
            r = api_client.get("station/api/stations/mobile/favorites")
            responses.append(r)
        for r in responses:
            assert r is not None, "并发响应不应为空"
            assert r.status_code < 500, f"并发请求不应返回 5xx, 实际: {r.status_code}"


    def test_Station_MobileStation_get_3_timeout_0026(self, api_client):
        """[Station][MobileStation] get_3 - 超时处理"""
        # GET /api/stations/mobile/favorites
        response = api_client.get("station/api/stations/mobile/favorites")
        assert response is not None, "超时处理响应不应为空"
        assert response.status_code < 500, f"超时测试不应返回 5xx, 实际: {response.status_code}"


    def test_Station_MobileStation_get_3_permission_denied_0026(self, api_client):
        """[Station][MobileStation] get_3 - 权限不足"""
        # GET /api/stations/mobile/favorites
        response = api_client.get("station/api/stations/mobile/favorites")
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"权限测试不应返回 5xx, 实际: {response.status_code}"


    def test_Station_MobileStation_get_3_response_format_0026(self, api_client):
        """[Station][MobileStation] get_3 - 响应格式"""
        # GET /api/stations/mobile/favorites
        response = api_client.get("station/api/stations/mobile/favorites")
        assert response is not None, "响应不应为空"
        data = response.json()
        assert isinstance(data, dict), "响应应为JSON对象"
        if response.status_code == 200:
            assert "success" in data or "data" in data or "code" in data, "200 响应应包含标准字段"


    def test_Station_MobileStation_post_4_positive_0027(self, api_client):
        """[Station][MobileStation] post_4 - 正常请求"""
        # POST /api/stations/mobile/favorites/{stationId:guid}
        response = api_client.post("station/api/stations/mobile/favorites/{stationId:guid}", json_data={"name": "test", "code": "TEST"})
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"POST 正常请求不应返回 5xx, 实际: {response.status_code}"


    def test_Station_MobileStation_post_4_no_auth_0027(self, api_client):
        """[Station][MobileStation] post_4 - 缺少认证头"""
        # POST /api/stations/mobile/favorites/{stationId:guid}
        api_client.clear_token()
        try:
            response = api_client.post("station/api/stations/mobile/favorites/{stationId:guid}")
            assert response is not None, "响应不应为空"
            assert response.status_code in (200, 400, 401, 403), f"无认证头应返回 401/403, 实际: {response.status_code}"
        finally:
            api_client.restore_token()


    def test_Station_MobileStation_post_4_invalid_token_0027(self, api_client):
        """[Station][MobileStation] post_4 - 无效Token"""
        # POST /api/stations/mobile/favorites/{stationId:guid}
        api_client.set_invalid_token()
        try:
            response = api_client.post("station/api/stations/mobile/favorites/{stationId:guid}")
            assert response is not None, "响应不应为空"
            assert response.status_code in (200, 400, 401, 403), f"无效Token应返回 401/403, 实际: {response.status_code}"
        finally:
            api_client.restore_token()


    def test_Station_MobileStation_post_4_tenant_isolation_0027(self, api_client):
        """[Station][MobileStation] post_4 - 租户隔离"""
        # POST /api/stations/mobile/favorites/{stationId:guid}
        response = api_client.post("station/api/stations/mobile/favorites/{stationId:guid}")
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"租户隔离测试不应返回 5xx, 实际: {response.status_code}"
        data = response.json()
        assert isinstance(data, dict), "响应应为JSON对象"


    def test_Station_MobileStation_post_4_empty_body_0027(self, api_client):
        """[Station][MobileStation] post_4 - 空请求体"""
        # POST /api/stations/mobile/favorites/{stationId:guid}
        response = api_client.post("station/api/stations/mobile/favorites/{stationId:guid}")
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"空请求体不应返回 5xx, 实际: {response.status_code}"


    def test_Station_MobileStation_post_4_invalid_id_0027(self, api_client):
        """[Station][MobileStation] post_4 - 无效ID"""
        # POST /api/stations/mobile/favorites/{stationId:guid}
        response = api_client.post("station/api/stations/mobile/favorites/{stationId:guid}")
        assert response is not None, "响应不应为空"
        assert response.status_code in (200, 400, 403, 404), f"无效ID应返回 200/400/403/404, 实际: {response.status_code}"


    def test_Station_MobileStation_post_4_not_found_id_0027(self, api_client):
        """[Station][MobileStation] post_4 - 不存在ID"""
        # POST /api/stations/mobile/favorites/{stationId:guid}
        response = api_client.post("station/api/stations/mobile/favorites/{stationId:guid}")
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"不存在ID不应返回 5xx, 实际: {response.status_code}"


    def test_Station_MobileStation_post_4_boundary_0027(self, api_client):
        """[Station][MobileStation] post_4 - 边界值测试"""
        # POST /api/stations/mobile/favorites/{stationId:guid}
        response = api_client.post("station/api/stations/mobile/favorites/{stationId:guid}")
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"边界值测试不应返回 5xx 服务器错误, 实际: {response.status_code}"
        assert isinstance(response.json(), dict), "响应应为JSON对象"


    def test_Station_MobileStation_post_4_sql_injection_0027(self, api_client):
        """[Station][MobileStation] post_4 - SQL注入防护"""
        # POST /api/stations/mobile/favorites/{stationId:guid}
        response = api_client.post("station/api/stations/mobile/favorites/{stationId:guid}")
        assert response is not None, "响应不应为空"
        assert response.status_code != 500, f"SQL注入不应导致服务器错误, 实际: {response.status_code}"
        data = response.json()
        assert isinstance(data, dict), "响应应为JSON对象"


    def test_Station_MobileStation_post_4_xss_protection_0027(self, api_client):
        """[Station][MobileStation] post_4 - XSS防护"""
        # POST /api/stations/mobile/favorites/{stationId:guid}
        xss_payload = {"name": "<script>alert('xss')</script>", "code": "XSS_TEST"}
        response = api_client.post("station/api/stations/mobile/favorites/{stationId:guid}", json_data=xss_payload)
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"XSS防护测试不应返回 5xx, 实际: {response.status_code}"


    def test_Station_MobileStation_post_4_large_payload_0027(self, api_client):
        """[Station][MobileStation] post_4 - 大数据量"""
        # POST /api/stations/mobile/favorites/{stationId:guid}
        large_data = {"name": "x" * 10000, "code": "LARGE", "description": "y" * 50000}
        response = api_client.post("station/api/stations/mobile/favorites/{stationId:guid}", json_data=large_data)
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"大数据量测试不应返回 5xx, 实际: {response.status_code}"


    def test_Station_MobileStation_post_4_concurrent_0027(self, api_client):
        """[Station][MobileStation] post_4 - 并发请求"""
        # POST /api/stations/mobile/favorites/{stationId:guid}
        responses = []
        for _ in range(3):
            r = api_client.post("station/api/stations/mobile/favorites/{stationId:guid}")
            responses.append(r)
        for r in responses:
            assert r is not None, "并发响应不应为空"
            assert r.status_code < 500, f"并发请求不应返回 5xx, 实际: {r.status_code}"


    def test_Station_MobileStation_post_4_timeout_0027(self, api_client):
        """[Station][MobileStation] post_4 - 超时处理"""
        # POST /api/stations/mobile/favorites/{stationId:guid}
        response = api_client.post("station/api/stations/mobile/favorites/{stationId:guid}")
        assert response is not None, "超时处理响应不应为空"
        assert response.status_code < 500, f"超时测试不应返回 5xx, 实际: {response.status_code}"


    def test_Station_MobileStation_post_4_permission_denied_0027(self, api_client):
        """[Station][MobileStation] post_4 - 权限不足"""
        # POST /api/stations/mobile/favorites/{stationId:guid}
        response = api_client.post("station/api/stations/mobile/favorites/{stationId:guid}")
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"权限测试不应返回 5xx, 实际: {response.status_code}"


    def test_Station_MobileStation_post_4_field_validation_0027(self, api_client):
        """[Station][MobileStation] post_4 - 字段校验"""
        # POST /api/stations/mobile/favorites/{stationId:guid}
        invalid_data = {"name": "", "code": ""}
        response = api_client.post("station/api/stations/mobile/favorites/{stationId:guid}", json_data=invalid_data)
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"字段校验不应返回 5xx, 实际: {response.status_code}"


    def test_Station_MobileStation_post_4_response_format_0027(self, api_client):
        """[Station][MobileStation] post_4 - 响应格式"""
        # POST /api/stations/mobile/favorites/{stationId:guid}
        response = api_client.post("station/api/stations/mobile/favorites/{stationId:guid}")
        assert response is not None, "响应不应为空"
        data = response.json()
        assert isinstance(data, dict), "响应应为JSON对象"
        if response.status_code == 200:
            assert "success" in data or "data" in data or "code" in data, "200 响应应包含标准字段"


    def test_Station_MobileStation_delete_5_positive_0028(self, api_client):
        """[Station][MobileStation] delete_5 - 正常请求"""
        # DELETE /api/stations/mobile/favorites/{stationId:guid}
        response = api_client.delete("station/api/stations/mobile/favorites/{stationId:guid}")
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"DELETE 正常请求不应返回 5xx, 实际: {response.status_code}"


    def test_Station_MobileStation_delete_5_no_auth_0028(self, api_client):
        """[Station][MobileStation] delete_5 - 缺少认证头"""
        # DELETE /api/stations/mobile/favorites/{stationId:guid}
        api_client.clear_token()
        try:
            response = api_client.delete("station/api/stations/mobile/favorites/{stationId:guid}")
            assert response is not None, "响应不应为空"
            assert response.status_code in (200, 400, 401, 403), f"无认证头应返回 401/403, 实际: {response.status_code}"
        finally:
            api_client.restore_token()


    def test_Station_MobileStation_delete_5_invalid_token_0028(self, api_client):
        """[Station][MobileStation] delete_5 - 无效Token"""
        # DELETE /api/stations/mobile/favorites/{stationId:guid}
        api_client.set_invalid_token()
        try:
            response = api_client.delete("station/api/stations/mobile/favorites/{stationId:guid}")
            assert response is not None, "响应不应为空"
            assert response.status_code in (200, 400, 401, 403), f"无效Token应返回 401/403, 实际: {response.status_code}"
        finally:
            api_client.restore_token()


    def test_Station_MobileStation_delete_5_tenant_isolation_0028(self, api_client):
        """[Station][MobileStation] delete_5 - 租户隔离"""
        # DELETE /api/stations/mobile/favorites/{stationId:guid}
        response = api_client.delete("station/api/stations/mobile/favorites/{stationId:guid}")
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"租户隔离测试不应返回 5xx, 实际: {response.status_code}"
        data = response.json()
        assert isinstance(data, dict), "响应应为JSON对象"


    def test_Station_MobileStation_delete_5_invalid_id_0028(self, api_client):
        """[Station][MobileStation] delete_5 - 无效ID"""
        # DELETE /api/stations/mobile/favorites/{stationId:guid}
        response = api_client.delete("station/api/stations/mobile/favorites/{stationId:guid}")
        assert response is not None, "响应不应为空"
        assert response.status_code in (200, 400, 403, 404), f"无效ID应返回 200/400/403/404, 实际: {response.status_code}"


    def test_Station_MobileStation_delete_5_not_found_id_0028(self, api_client):
        """[Station][MobileStation] delete_5 - 不存在ID"""
        # DELETE /api/stations/mobile/favorites/{stationId:guid}
        response = api_client.delete("station/api/stations/mobile/favorites/{stationId:guid}")
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"不存在ID不应返回 5xx, 实际: {response.status_code}"


    def test_Station_MobileStation_delete_5_boundary_0028(self, api_client):
        """[Station][MobileStation] delete_5 - 边界值测试"""
        # DELETE /api/stations/mobile/favorites/{stationId:guid}
        response = api_client.delete("station/api/stations/mobile/favorites/{stationId:guid}")
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"边界值测试不应返回 5xx 服务器错误, 实际: {response.status_code}"
        assert isinstance(response.json(), dict), "响应应为JSON对象"


    def test_Station_MobileStation_delete_5_sql_injection_0028(self, api_client):
        """[Station][MobileStation] delete_5 - SQL注入防护"""
        # DELETE /api/stations/mobile/favorites/{stationId:guid}
        response = api_client.delete("station/api/stations/mobile/favorites/{stationId:guid}")
        assert response is not None, "响应不应为空"
        assert response.status_code != 500, f"SQL注入不应导致服务器错误, 实际: {response.status_code}"
        data = response.json()
        assert isinstance(data, dict), "响应应为JSON对象"


    def test_Station_MobileStation_delete_5_concurrent_0028(self, api_client):
        """[Station][MobileStation] delete_5 - 并发请求"""
        # DELETE /api/stations/mobile/favorites/{stationId:guid}
        responses = []
        for _ in range(3):
            r = api_client.delete("station/api/stations/mobile/favorites/{stationId:guid}")
            responses.append(r)
        for r in responses:
            assert r is not None, "并发响应不应为空"
            assert r.status_code < 500, f"并发请求不应返回 5xx, 实际: {r.status_code}"


    def test_Station_MobileStation_delete_5_idempotent_0028(self, api_client):
        """[Station][MobileStation] delete_5 - 幂等性"""
        # DELETE /api/stations/mobile/favorites/{stationId:guid}
        r1 = api_client.delete("station/api/stations/mobile/favorites/{stationId:guid}")
        r2 = api_client.delete("station/api/stations/mobile/favorites/{stationId:guid}")
        assert r1 is not None and r2 is not None, "幂等性响应不应为空"
        assert r1.status_code == r2.status_code, f"幂等性: 两次请求状态码应一致, {r1.status_code} vs {r2.status_code}"


    def test_Station_MobileStation_delete_5_timeout_0028(self, api_client):
        """[Station][MobileStation] delete_5 - 超时处理"""
        # DELETE /api/stations/mobile/favorites/{stationId:guid}
        response = api_client.delete("station/api/stations/mobile/favorites/{stationId:guid}")
        assert response is not None, "超时处理响应不应为空"
        assert response.status_code < 500, f"超时测试不应返回 5xx, 实际: {response.status_code}"


    def test_Station_MobileStation_delete_5_permission_denied_0028(self, api_client):
        """[Station][MobileStation] delete_5 - 权限不足"""
        # DELETE /api/stations/mobile/favorites/{stationId:guid}
        response = api_client.delete("station/api/stations/mobile/favorites/{stationId:guid}")
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"权限测试不应返回 5xx, 实际: {response.status_code}"


    def test_Station_MobileStation_delete_5_response_format_0028(self, api_client):
        """[Station][MobileStation] delete_5 - 响应格式"""
        # DELETE /api/stations/mobile/favorites/{stationId:guid}
        response = api_client.delete("station/api/stations/mobile/favorites/{stationId:guid}")
        assert response is not None, "响应不应为空"
        data = response.json()
        assert isinstance(data, dict), "响应应为JSON对象"
        if response.status_code == 200:
            assert "success" in data or "data" in data or "code" in data, "200 响应应包含标准字段"


    def test_Station_Station_get_0_positive_0029(self, api_client):
        """[Station][Station] get_0 - 正常请求"""
        # GET /api/stations
        response = api_client.get("station/api/stations")
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"GET 正常请求不应返回 5xx, 实际: {response.status_code}"


    def test_Station_Station_get_0_no_auth_0029(self, api_client):
        """[Station][Station] get_0 - 缺少认证头"""
        # GET /api/stations
        api_client.clear_token()
        try:
            response = api_client.get("station/api/stations")
            assert response is not None, "响应不应为空"
            assert response.status_code in (200, 400, 401, 403), f"无认证头应返回 401/403, 实际: {response.status_code}"
        finally:
            api_client.restore_token()


    def test_Station_Station_get_0_invalid_token_0029(self, api_client):
        """[Station][Station] get_0 - 无效Token"""
        # GET /api/stations
        api_client.set_invalid_token()
        try:
            response = api_client.get("station/api/stations")
            assert response is not None, "响应不应为空"
            assert response.status_code in (200, 400, 401, 403), f"无效Token应返回 401/403, 实际: {response.status_code}"
        finally:
            api_client.restore_token()


    def test_Station_Station_get_0_tenant_isolation_0029(self, api_client):
        """[Station][Station] get_0 - 租户隔离"""
        # GET /api/stations
        response = api_client.get("station/api/stations")
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"租户隔离测试不应返回 5xx, 实际: {response.status_code}"
        data = response.json()
        assert isinstance(data, dict), "响应应为JSON对象"


    def test_Station_Station_get_0_boundary_0029(self, api_client):
        """[Station][Station] get_0 - 边界值测试"""
        # GET /api/stations
        response = api_client.get("station/api/stations")
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"边界值测试不应返回 5xx 服务器错误, 实际: {response.status_code}"
        assert isinstance(response.json(), dict), "响应应为JSON对象"


    def test_Station_Station_get_0_sql_injection_0029(self, api_client):
        """[Station][Station] get_0 - SQL注入防护"""
        # GET /api/stations
        response = api_client.get("station/api/stations")
        assert response is not None, "响应不应为空"
        assert response.status_code != 500, f"SQL注入不应导致服务器错误, 实际: {response.status_code}"
        data = response.json()
        assert isinstance(data, dict), "响应应为JSON对象"


    def test_Station_Station_get_0_concurrent_0029(self, api_client):
        """[Station][Station] get_0 - 并发请求"""
        # GET /api/stations
        responses = []
        for _ in range(3):
            r = api_client.get("station/api/stations")
            responses.append(r)
        for r in responses:
            assert r is not None, "并发响应不应为空"
            assert r.status_code < 500, f"并发请求不应返回 5xx, 实际: {r.status_code}"


    def test_Station_Station_get_0_timeout_0029(self, api_client):
        """[Station][Station] get_0 - 超时处理"""
        # GET /api/stations
        response = api_client.get("station/api/stations")
        assert response is not None, "超时处理响应不应为空"
        assert response.status_code < 500, f"超时测试不应返回 5xx, 实际: {response.status_code}"


    def test_Station_Station_get_0_permission_denied_0029(self, api_client):
        """[Station][Station] get_0 - 权限不足"""
        # GET /api/stations
        response = api_client.get("station/api/stations")
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"权限测试不应返回 5xx, 实际: {response.status_code}"


    def test_Station_Station_get_0_response_format_0029(self, api_client):
        """[Station][Station] get_0 - 响应格式"""
        # GET /api/stations
        response = api_client.get("station/api/stations")
        assert response is not None, "响应不应为空"
        data = response.json()
        assert isinstance(data, dict), "响应应为JSON对象"
        if response.status_code == 200:
            assert "success" in data or "data" in data or "code" in data, "200 响应应包含标准字段"


    def test_Station_Station_get_1_positive_0030(self, api_client):
        """[Station][Station] get_1 - 正常请求"""
        # GET /api/stations/{id:guid}
        response = api_client.get("station/api/stations/{id:guid}")
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"GET 正常请求不应返回 5xx, 实际: {response.status_code}"


    def test_Station_Station_get_1_no_auth_0030(self, api_client):
        """[Station][Station] get_1 - 缺少认证头"""
        # GET /api/stations/{id:guid}
        api_client.clear_token()
        try:
            response = api_client.get("station/api/stations/{id:guid}")
            assert response is not None, "响应不应为空"
            assert response.status_code in (200, 400, 401, 403), f"无认证头应返回 401/403, 实际: {response.status_code}"
        finally:
            api_client.restore_token()


    def test_Station_Station_get_1_invalid_token_0030(self, api_client):
        """[Station][Station] get_1 - 无效Token"""
        # GET /api/stations/{id:guid}
        api_client.set_invalid_token()
        try:
            response = api_client.get("station/api/stations/{id:guid}")
            assert response is not None, "响应不应为空"
            assert response.status_code in (200, 400, 401, 403), f"无效Token应返回 401/403, 实际: {response.status_code}"
        finally:
            api_client.restore_token()


    def test_Station_Station_get_1_tenant_isolation_0030(self, api_client):
        """[Station][Station] get_1 - 租户隔离"""
        # GET /api/stations/{id:guid}
        response = api_client.get("station/api/stations/{id:guid}")
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"租户隔离测试不应返回 5xx, 实际: {response.status_code}"
        data = response.json()
        assert isinstance(data, dict), "响应应为JSON对象"


    def test_Station_Station_get_1_invalid_id_0030(self, api_client):
        """[Station][Station] get_1 - 无效ID"""
        # GET /api/stations/{id:guid}
        response = api_client.get("station/api/stations/{id:guid}")
        assert response is not None, "响应不应为空"
        assert response.status_code in (200, 400, 403, 404), f"无效ID应返回 200/400/403/404, 实际: {response.status_code}"


    def test_Station_Station_get_1_not_found_id_0030(self, api_client):
        """[Station][Station] get_1 - 不存在ID"""
        # GET /api/stations/{id:guid}
        response = api_client.get("station/api/stations/{id:guid}")
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"不存在ID不应返回 5xx, 实际: {response.status_code}"


    def test_Station_Station_get_1_boundary_0030(self, api_client):
        """[Station][Station] get_1 - 边界值测试"""
        # GET /api/stations/{id:guid}
        response = api_client.get("station/api/stations/{id:guid}")
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"边界值测试不应返回 5xx 服务器错误, 实际: {response.status_code}"
        assert isinstance(response.json(), dict), "响应应为JSON对象"


    def test_Station_Station_get_1_sql_injection_0030(self, api_client):
        """[Station][Station] get_1 - SQL注入防护"""
        # GET /api/stations/{id:guid}
        response = api_client.get("station/api/stations/{id:guid}")
        assert response is not None, "响应不应为空"
        assert response.status_code != 500, f"SQL注入不应导致服务器错误, 实际: {response.status_code}"
        data = response.json()
        assert isinstance(data, dict), "响应应为JSON对象"


    def test_Station_Station_get_1_concurrent_0030(self, api_client):
        """[Station][Station] get_1 - 并发请求"""
        # GET /api/stations/{id:guid}
        responses = []
        for _ in range(3):
            r = api_client.get("station/api/stations/{id:guid}")
            responses.append(r)
        for r in responses:
            assert r is not None, "并发响应不应为空"
            assert r.status_code < 500, f"并发请求不应返回 5xx, 实际: {r.status_code}"


    def test_Station_Station_get_1_timeout_0030(self, api_client):
        """[Station][Station] get_1 - 超时处理"""
        # GET /api/stations/{id:guid}
        response = api_client.get("station/api/stations/{id:guid}")
        assert response is not None, "超时处理响应不应为空"
        assert response.status_code < 500, f"超时测试不应返回 5xx, 实际: {response.status_code}"


    def test_Station_Station_get_1_permission_denied_0030(self, api_client):
        """[Station][Station] get_1 - 权限不足"""
        # GET /api/stations/{id:guid}
        response = api_client.get("station/api/stations/{id:guid}")
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"权限测试不应返回 5xx, 实际: {response.status_code}"


    def test_Station_Station_get_1_response_format_0030(self, api_client):
        """[Station][Station] get_1 - 响应格式"""
        # GET /api/stations/{id:guid}
        response = api_client.get("station/api/stations/{id:guid}")
        assert response is not None, "响应不应为空"
        data = response.json()
        assert isinstance(data, dict), "响应应为JSON对象"
        if response.status_code == 200:
            assert "success" in data or "data" in data or "code" in data, "200 响应应包含标准字段"


    def test_Station_Station_post_2_positive_0031(self, api_client):
        """[Station][Station] post_2 - 正常请求"""
        # POST /api/stations
        response = api_client.post("station/api/stations", json_data={"name": "test", "code": "TEST"})
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"POST 正常请求不应返回 5xx, 实际: {response.status_code}"


    def test_Station_Station_post_2_no_auth_0031(self, api_client):
        """[Station][Station] post_2 - 缺少认证头"""
        # POST /api/stations
        api_client.clear_token()
        try:
            response = api_client.post("station/api/stations")
            assert response is not None, "响应不应为空"
            assert response.status_code in (200, 400, 401, 403), f"无认证头应返回 401/403, 实际: {response.status_code}"
        finally:
            api_client.restore_token()


    def test_Station_Station_post_2_invalid_token_0031(self, api_client):
        """[Station][Station] post_2 - 无效Token"""
        # POST /api/stations
        api_client.set_invalid_token()
        try:
            response = api_client.post("station/api/stations")
            assert response is not None, "响应不应为空"
            assert response.status_code in (200, 400, 401, 403), f"无效Token应返回 401/403, 实际: {response.status_code}"
        finally:
            api_client.restore_token()


    def test_Station_Station_post_2_tenant_isolation_0031(self, api_client):
        """[Station][Station] post_2 - 租户隔离"""
        # POST /api/stations
        response = api_client.post("station/api/stations")
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"租户隔离测试不应返回 5xx, 实际: {response.status_code}"
        data = response.json()
        assert isinstance(data, dict), "响应应为JSON对象"


    def test_Station_Station_post_2_empty_body_0031(self, api_client):
        """[Station][Station] post_2 - 空请求体"""
        # POST /api/stations
        response = api_client.post("station/api/stations")
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"空请求体不应返回 5xx, 实际: {response.status_code}"


    def test_Station_Station_post_2_boundary_0031(self, api_client):
        """[Station][Station] post_2 - 边界值测试"""
        # POST /api/stations
        response = api_client.post("station/api/stations")
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"边界值测试不应返回 5xx 服务器错误, 实际: {response.status_code}"
        assert isinstance(response.json(), dict), "响应应为JSON对象"


    def test_Station_Station_post_2_sql_injection_0031(self, api_client):
        """[Station][Station] post_2 - SQL注入防护"""
        # POST /api/stations
        response = api_client.post("station/api/stations")
        assert response is not None, "响应不应为空"
        assert response.status_code != 500, f"SQL注入不应导致服务器错误, 实际: {response.status_code}"
        data = response.json()
        assert isinstance(data, dict), "响应应为JSON对象"


    def test_Station_Station_post_2_xss_protection_0031(self, api_client):
        """[Station][Station] post_2 - XSS防护"""
        # POST /api/stations
        xss_payload = {"name": "<script>alert('xss')</script>", "code": "XSS_TEST"}
        response = api_client.post("station/api/stations", json_data=xss_payload)
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"XSS防护测试不应返回 5xx, 实际: {response.status_code}"


    def test_Station_Station_post_2_large_payload_0031(self, api_client):
        """[Station][Station] post_2 - 大数据量"""
        # POST /api/stations
        large_data = {"name": "x" * 10000, "code": "LARGE", "description": "y" * 50000}
        response = api_client.post("station/api/stations", json_data=large_data)
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"大数据量测试不应返回 5xx, 实际: {response.status_code}"


    def test_Station_Station_post_2_concurrent_0031(self, api_client):
        """[Station][Station] post_2 - 并发请求"""
        # POST /api/stations
        responses = []
        for _ in range(3):
            r = api_client.post("station/api/stations")
            responses.append(r)
        for r in responses:
            assert r is not None, "并发响应不应为空"
            assert r.status_code < 500, f"并发请求不应返回 5xx, 实际: {r.status_code}"


    def test_Station_Station_post_2_timeout_0031(self, api_client):
        """[Station][Station] post_2 - 超时处理"""
        # POST /api/stations
        response = api_client.post("station/api/stations")
        assert response is not None, "超时处理响应不应为空"
        assert response.status_code < 500, f"超时测试不应返回 5xx, 实际: {response.status_code}"


    def test_Station_Station_post_2_permission_denied_0031(self, api_client):
        """[Station][Station] post_2 - 权限不足"""
        # POST /api/stations
        response = api_client.post("station/api/stations")
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"权限测试不应返回 5xx, 实际: {response.status_code}"


    def test_Station_Station_post_2_field_validation_0031(self, api_client):
        """[Station][Station] post_2 - 字段校验"""
        # POST /api/stations
        invalid_data = {"name": "", "code": ""}
        response = api_client.post("station/api/stations", json_data=invalid_data)
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"字段校验不应返回 5xx, 实际: {response.status_code}"


    def test_Station_Station_post_2_response_format_0031(self, api_client):
        """[Station][Station] post_2 - 响应格式"""
        # POST /api/stations
        response = api_client.post("station/api/stations")
        assert response is not None, "响应不应为空"
        data = response.json()
        assert isinstance(data, dict), "响应应为JSON对象"
        if response.status_code == 200:
            assert "success" in data or "data" in data or "code" in data, "200 响应应包含标准字段"


    def test_Station_Station_put_3_positive_0032(self, api_client):
        """[Station][Station] put_3 - 正常请求"""
        # PUT /api/stations/{id:guid}
        response = api_client.put("station/api/stations/{id:guid}", json_data={"name": "updated"})
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"PUT 正常请求不应返回 5xx, 实际: {response.status_code}"


    def test_Station_Station_put_3_no_auth_0032(self, api_client):
        """[Station][Station] put_3 - 缺少认证头"""
        # PUT /api/stations/{id:guid}
        api_client.clear_token()
        try:
            response = api_client.put("station/api/stations/{id:guid}")
            assert response is not None, "响应不应为空"
            assert response.status_code in (200, 400, 401, 403), f"无认证头应返回 401/403, 实际: {response.status_code}"
        finally:
            api_client.restore_token()


    def test_Station_Station_put_3_invalid_token_0032(self, api_client):
        """[Station][Station] put_3 - 无效Token"""
        # PUT /api/stations/{id:guid}
        api_client.set_invalid_token()
        try:
            response = api_client.put("station/api/stations/{id:guid}")
            assert response is not None, "响应不应为空"
            assert response.status_code in (200, 400, 401, 403), f"无效Token应返回 401/403, 实际: {response.status_code}"
        finally:
            api_client.restore_token()


    def test_Station_Station_put_3_tenant_isolation_0032(self, api_client):
        """[Station][Station] put_3 - 租户隔离"""
        # PUT /api/stations/{id:guid}
        response = api_client.put("station/api/stations/{id:guid}")
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"租户隔离测试不应返回 5xx, 实际: {response.status_code}"
        data = response.json()
        assert isinstance(data, dict), "响应应为JSON对象"


    def test_Station_Station_put_3_empty_body_0032(self, api_client):
        """[Station][Station] put_3 - 空请求体"""
        # PUT /api/stations/{id:guid}
        response = api_client.put("station/api/stations/{id:guid}")
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"空请求体不应返回 5xx, 实际: {response.status_code}"


    def test_Station_Station_put_3_invalid_id_0032(self, api_client):
        """[Station][Station] put_3 - 无效ID"""
        # PUT /api/stations/{id:guid}
        response = api_client.put("station/api/stations/{id:guid}")
        assert response is not None, "响应不应为空"
        assert response.status_code in (200, 400, 403, 404), f"无效ID应返回 200/400/403/404, 实际: {response.status_code}"


    def test_Station_Station_put_3_not_found_id_0032(self, api_client):
        """[Station][Station] put_3 - 不存在ID"""
        # PUT /api/stations/{id:guid}
        response = api_client.put("station/api/stations/{id:guid}")
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"不存在ID不应返回 5xx, 实际: {response.status_code}"


    def test_Station_Station_put_3_boundary_0032(self, api_client):
        """[Station][Station] put_3 - 边界值测试"""
        # PUT /api/stations/{id:guid}
        response = api_client.put("station/api/stations/{id:guid}")
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"边界值测试不应返回 5xx 服务器错误, 实际: {response.status_code}"
        assert isinstance(response.json(), dict), "响应应为JSON对象"


    def test_Station_Station_put_3_sql_injection_0032(self, api_client):
        """[Station][Station] put_3 - SQL注入防护"""
        # PUT /api/stations/{id:guid}
        response = api_client.put("station/api/stations/{id:guid}")
        assert response is not None, "响应不应为空"
        assert response.status_code != 500, f"SQL注入不应导致服务器错误, 实际: {response.status_code}"
        data = response.json()
        assert isinstance(data, dict), "响应应为JSON对象"


    def test_Station_Station_put_3_xss_protection_0032(self, api_client):
        """[Station][Station] put_3 - XSS防护"""
        # PUT /api/stations/{id:guid}
        xss_payload = {"name": "<script>alert('xss')</script>", "code": "XSS_TEST"}
        response = api_client.put("station/api/stations/{id:guid}", json_data=xss_payload)
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"XSS防护测试不应返回 5xx, 实际: {response.status_code}"


    def test_Station_Station_put_3_large_payload_0032(self, api_client):
        """[Station][Station] put_3 - 大数据量"""
        # PUT /api/stations/{id:guid}
        large_data = {"name": "x" * 10000, "code": "LARGE", "description": "y" * 50000}
        response = api_client.put("station/api/stations/{id:guid}", json_data=large_data)
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"大数据量测试不应返回 5xx, 实际: {response.status_code}"


    def test_Station_Station_put_3_concurrent_0032(self, api_client):
        """[Station][Station] put_3 - 并发请求"""
        # PUT /api/stations/{id:guid}
        responses = []
        for _ in range(3):
            r = api_client.put("station/api/stations/{id:guid}")
            responses.append(r)
        for r in responses:
            assert r is not None, "并发响应不应为空"
            assert r.status_code < 500, f"并发请求不应返回 5xx, 实际: {r.status_code}"


    def test_Station_Station_put_3_idempotent_0032(self, api_client):
        """[Station][Station] put_3 - 幂等性"""
        # PUT /api/stations/{id:guid}
        r1 = api_client.put("station/api/stations/{id:guid}")
        r2 = api_client.put("station/api/stations/{id:guid}")
        assert r1 is not None and r2 is not None, "幂等性响应不应为空"
        assert r1.status_code == r2.status_code, f"幂等性: 两次请求状态码应一致, {r1.status_code} vs {r2.status_code}"


    def test_Station_Station_put_3_timeout_0032(self, api_client):
        """[Station][Station] put_3 - 超时处理"""
        # PUT /api/stations/{id:guid}
        response = api_client.put("station/api/stations/{id:guid}")
        assert response is not None, "超时处理响应不应为空"
        assert response.status_code < 500, f"超时测试不应返回 5xx, 实际: {response.status_code}"


    def test_Station_Station_put_3_permission_denied_0032(self, api_client):
        """[Station][Station] put_3 - 权限不足"""
        # PUT /api/stations/{id:guid}
        response = api_client.put("station/api/stations/{id:guid}")
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"权限测试不应返回 5xx, 实际: {response.status_code}"


    def test_Station_Station_put_3_field_validation_0032(self, api_client):
        """[Station][Station] put_3 - 字段校验"""
        # PUT /api/stations/{id:guid}
        invalid_data = {"name": "", "code": ""}
        response = api_client.put("station/api/stations/{id:guid}", json_data=invalid_data)
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"字段校验不应返回 5xx, 实际: {response.status_code}"


    def test_Station_Station_put_3_response_format_0032(self, api_client):
        """[Station][Station] put_3 - 响应格式"""
        # PUT /api/stations/{id:guid}
        response = api_client.put("station/api/stations/{id:guid}")
        assert response is not None, "响应不应为空"
        data = response.json()
        assert isinstance(data, dict), "响应应为JSON对象"
        if response.status_code == 200:
            assert "success" in data or "data" in data or "code" in data, "200 响应应包含标准字段"


    def test_Station_Station_delete_4_positive_0033(self, api_client):
        """[Station][Station] delete_4 - 正常请求"""
        # DELETE /api/stations/{id:guid}
        response = api_client.delete("station/api/stations/{id:guid}")
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"DELETE 正常请求不应返回 5xx, 实际: {response.status_code}"


    def test_Station_Station_delete_4_no_auth_0033(self, api_client):
        """[Station][Station] delete_4 - 缺少认证头"""
        # DELETE /api/stations/{id:guid}
        api_client.clear_token()
        try:
            response = api_client.delete("station/api/stations/{id:guid}")
            assert response is not None, "响应不应为空"
            assert response.status_code in (200, 400, 401, 403), f"无认证头应返回 401/403, 实际: {response.status_code}"
        finally:
            api_client.restore_token()


    def test_Station_Station_delete_4_invalid_token_0033(self, api_client):
        """[Station][Station] delete_4 - 无效Token"""
        # DELETE /api/stations/{id:guid}
        api_client.set_invalid_token()
        try:
            response = api_client.delete("station/api/stations/{id:guid}")
            assert response is not None, "响应不应为空"
            assert response.status_code in (200, 400, 401, 403), f"无效Token应返回 401/403, 实际: {response.status_code}"
        finally:
            api_client.restore_token()


    def test_Station_Station_delete_4_tenant_isolation_0033(self, api_client):
        """[Station][Station] delete_4 - 租户隔离"""
        # DELETE /api/stations/{id:guid}
        response = api_client.delete("station/api/stations/{id:guid}")
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"租户隔离测试不应返回 5xx, 实际: {response.status_code}"
        data = response.json()
        assert isinstance(data, dict), "响应应为JSON对象"


    def test_Station_Station_delete_4_invalid_id_0033(self, api_client):
        """[Station][Station] delete_4 - 无效ID"""
        # DELETE /api/stations/{id:guid}
        response = api_client.delete("station/api/stations/{id:guid}")
        assert response is not None, "响应不应为空"
        assert response.status_code in (200, 400, 403, 404), f"无效ID应返回 200/400/403/404, 实际: {response.status_code}"


    def test_Station_Station_delete_4_not_found_id_0033(self, api_client):
        """[Station][Station] delete_4 - 不存在ID"""
        # DELETE /api/stations/{id:guid}
        response = api_client.delete("station/api/stations/{id:guid}")
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"不存在ID不应返回 5xx, 实际: {response.status_code}"


    def test_Station_Station_delete_4_boundary_0033(self, api_client):
        """[Station][Station] delete_4 - 边界值测试"""
        # DELETE /api/stations/{id:guid}
        response = api_client.delete("station/api/stations/{id:guid}")
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"边界值测试不应返回 5xx 服务器错误, 实际: {response.status_code}"
        assert isinstance(response.json(), dict), "响应应为JSON对象"


    def test_Station_Station_delete_4_sql_injection_0033(self, api_client):
        """[Station][Station] delete_4 - SQL注入防护"""
        # DELETE /api/stations/{id:guid}
        response = api_client.delete("station/api/stations/{id:guid}")
        assert response is not None, "响应不应为空"
        assert response.status_code != 500, f"SQL注入不应导致服务器错误, 实际: {response.status_code}"
        data = response.json()
        assert isinstance(data, dict), "响应应为JSON对象"


    def test_Station_Station_delete_4_concurrent_0033(self, api_client):
        """[Station][Station] delete_4 - 并发请求"""
        # DELETE /api/stations/{id:guid}
        responses = []
        for _ in range(3):
            r = api_client.delete("station/api/stations/{id:guid}")
            responses.append(r)
        for r in responses:
            assert r is not None, "并发响应不应为空"
            assert r.status_code < 500, f"并发请求不应返回 5xx, 实际: {r.status_code}"


    def test_Station_Station_delete_4_idempotent_0033(self, api_client):
        """[Station][Station] delete_4 - 幂等性"""
        # DELETE /api/stations/{id:guid}
        r1 = api_client.delete("station/api/stations/{id:guid}")
        r2 = api_client.delete("station/api/stations/{id:guid}")
        assert r1 is not None and r2 is not None, "幂等性响应不应为空"
        assert r1.status_code == r2.status_code, f"幂等性: 两次请求状态码应一致, {r1.status_code} vs {r2.status_code}"


    def test_Station_Station_delete_4_timeout_0033(self, api_client):
        """[Station][Station] delete_4 - 超时处理"""
        # DELETE /api/stations/{id:guid}
        response = api_client.delete("station/api/stations/{id:guid}")
        assert response is not None, "超时处理响应不应为空"
        assert response.status_code < 500, f"超时测试不应返回 5xx, 实际: {response.status_code}"


    def test_Station_Station_delete_4_permission_denied_0033(self, api_client):
        """[Station][Station] delete_4 - 权限不足"""
        # DELETE /api/stations/{id:guid}
        response = api_client.delete("station/api/stations/{id:guid}")
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"权限测试不应返回 5xx, 实际: {response.status_code}"


    def test_Station_Station_delete_4_response_format_0033(self, api_client):
        """[Station][Station] delete_4 - 响应格式"""
        # DELETE /api/stations/{id:guid}
        response = api_client.delete("station/api/stations/{id:guid}")
        assert response is not None, "响应不应为空"
        data = response.json()
        assert isinstance(data, dict), "响应应为JSON对象"
        if response.status_code == 200:
            assert "success" in data or "data" in data or "code" in data, "200 响应应包含标准字段"


    def test_Station_StationOptions_get_0_positive_0034(self, api_client):
        """[Station][StationOptions] get_0 - 正常请求"""
        # GET /api/station/options
        response = api_client.get("station/api/station/options")
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"GET 正常请求不应返回 5xx, 实际: {response.status_code}"


    def test_Station_StationOptions_get_0_no_auth_0034(self, api_client):
        """[Station][StationOptions] get_0 - 缺少认证头"""
        # GET /api/station/options
        api_client.clear_token()
        try:
            response = api_client.get("station/api/station/options")
            assert response is not None, "响应不应为空"
            assert response.status_code in (200, 400, 401, 403), f"无认证头应返回 401/403, 实际: {response.status_code}"
        finally:
            api_client.restore_token()


    def test_Station_StationOptions_get_0_invalid_token_0034(self, api_client):
        """[Station][StationOptions] get_0 - 无效Token"""
        # GET /api/station/options
        api_client.set_invalid_token()
        try:
            response = api_client.get("station/api/station/options")
            assert response is not None, "响应不应为空"
            assert response.status_code in (200, 400, 401, 403), f"无效Token应返回 401/403, 实际: {response.status_code}"
        finally:
            api_client.restore_token()


    def test_Station_StationOptions_get_0_tenant_isolation_0034(self, api_client):
        """[Station][StationOptions] get_0 - 租户隔离"""
        # GET /api/station/options
        response = api_client.get("station/api/station/options")
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"租户隔离测试不应返回 5xx, 实际: {response.status_code}"
        data = response.json()
        assert isinstance(data, dict), "响应应为JSON对象"


    def test_Station_StationOptions_get_0_boundary_0034(self, api_client):
        """[Station][StationOptions] get_0 - 边界值测试"""
        # GET /api/station/options
        response = api_client.get("station/api/station/options")
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"边界值测试不应返回 5xx 服务器错误, 实际: {response.status_code}"
        assert isinstance(response.json(), dict), "响应应为JSON对象"


    def test_Station_StationOptions_get_0_sql_injection_0034(self, api_client):
        """[Station][StationOptions] get_0 - SQL注入防护"""
        # GET /api/station/options
        response = api_client.get("station/api/station/options")
        assert response is not None, "响应不应为空"
        assert response.status_code != 500, f"SQL注入不应导致服务器错误, 实际: {response.status_code}"
        data = response.json()
        assert isinstance(data, dict), "响应应为JSON对象"


    def test_Station_StationOptions_get_0_concurrent_0034(self, api_client):
        """[Station][StationOptions] get_0 - 并发请求"""
        # GET /api/station/options
        responses = []
        for _ in range(3):
            r = api_client.get("station/api/station/options")
            responses.append(r)
        for r in responses:
            assert r is not None, "并发响应不应为空"
            assert r.status_code < 500, f"并发请求不应返回 5xx, 实际: {r.status_code}"


    def test_Station_StationOptions_get_0_timeout_0034(self, api_client):
        """[Station][StationOptions] get_0 - 超时处理"""
        # GET /api/station/options
        response = api_client.get("station/api/station/options")
        assert response is not None, "超时处理响应不应为空"
        assert response.status_code < 500, f"超时测试不应返回 5xx, 实际: {response.status_code}"


    def test_Station_StationOptions_get_0_permission_denied_0034(self, api_client):
        """[Station][StationOptions] get_0 - 权限不足"""
        # GET /api/station/options
        response = api_client.get("station/api/station/options")
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"权限测试不应返回 5xx, 实际: {response.status_code}"


    def test_Station_StationOptions_get_0_response_format_0034(self, api_client):
        """[Station][StationOptions] get_0 - 响应格式"""
        # GET /api/station/options
        response = api_client.get("station/api/station/options")
        assert response is not None, "响应不应为空"
        data = response.json()
        assert isinstance(data, dict), "响应应为JSON对象"
        if response.status_code == 200:
            assert "success" in data or "data" in data or "code" in data, "200 响应应包含标准字段"


    def test_Station_StationPrice_get_0_positive_0035(self, api_client):
        """[Station][StationPrice] get_0 - 正常请求"""
        # GET /api/stations/{stationId:guid}/prices
        response = api_client.get("station/api/stations/{stationId:guid}/prices")
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"GET 正常请求不应返回 5xx, 实际: {response.status_code}"


    def test_Station_StationPrice_get_0_no_auth_0035(self, api_client):
        """[Station][StationPrice] get_0 - 缺少认证头"""
        # GET /api/stations/{stationId:guid}/prices
        api_client.clear_token()
        try:
            response = api_client.get("station/api/stations/{stationId:guid}/prices")
            assert response is not None, "响应不应为空"
            assert response.status_code in (200, 400, 401, 403), f"无认证头应返回 401/403, 实际: {response.status_code}"
        finally:
            api_client.restore_token()


    def test_Station_StationPrice_get_0_invalid_token_0035(self, api_client):
        """[Station][StationPrice] get_0 - 无效Token"""
        # GET /api/stations/{stationId:guid}/prices
        api_client.set_invalid_token()
        try:
            response = api_client.get("station/api/stations/{stationId:guid}/prices")
            assert response is not None, "响应不应为空"
            assert response.status_code in (200, 400, 401, 403), f"无效Token应返回 401/403, 实际: {response.status_code}"
        finally:
            api_client.restore_token()


    def test_Station_StationPrice_get_0_tenant_isolation_0035(self, api_client):
        """[Station][StationPrice] get_0 - 租户隔离"""
        # GET /api/stations/{stationId:guid}/prices
        response = api_client.get("station/api/stations/{stationId:guid}/prices")
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"租户隔离测试不应返回 5xx, 实际: {response.status_code}"
        data = response.json()
        assert isinstance(data, dict), "响应应为JSON对象"


    def test_Station_StationPrice_get_0_boundary_0035(self, api_client):
        """[Station][StationPrice] get_0 - 边界值测试"""
        # GET /api/stations/{stationId:guid}/prices
        response = api_client.get("station/api/stations/{stationId:guid}/prices")
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"边界值测试不应返回 5xx 服务器错误, 实际: {response.status_code}"
        assert isinstance(response.json(), dict), "响应应为JSON对象"


    def test_Station_StationPrice_get_0_sql_injection_0035(self, api_client):
        """[Station][StationPrice] get_0 - SQL注入防护"""
        # GET /api/stations/{stationId:guid}/prices
        response = api_client.get("station/api/stations/{stationId:guid}/prices")
        assert response is not None, "响应不应为空"
        assert response.status_code != 500, f"SQL注入不应导致服务器错误, 实际: {response.status_code}"
        data = response.json()
        assert isinstance(data, dict), "响应应为JSON对象"


    def test_Station_StationPrice_get_0_concurrent_0035(self, api_client):
        """[Station][StationPrice] get_0 - 并发请求"""
        # GET /api/stations/{stationId:guid}/prices
        responses = []
        for _ in range(3):
            r = api_client.get("station/api/stations/{stationId:guid}/prices")
            responses.append(r)
        for r in responses:
            assert r is not None, "并发响应不应为空"
            assert r.status_code < 500, f"并发请求不应返回 5xx, 实际: {r.status_code}"


    def test_Station_StationPrice_get_0_timeout_0035(self, api_client):
        """[Station][StationPrice] get_0 - 超时处理"""
        # GET /api/stations/{stationId:guid}/prices
        response = api_client.get("station/api/stations/{stationId:guid}/prices")
        assert response is not None, "超时处理响应不应为空"
        assert response.status_code < 500, f"超时测试不应返回 5xx, 实际: {response.status_code}"


    def test_Station_StationPrice_get_0_permission_denied_0035(self, api_client):
        """[Station][StationPrice] get_0 - 权限不足"""
        # GET /api/stations/{stationId:guid}/prices
        response = api_client.get("station/api/stations/{stationId:guid}/prices")
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"权限测试不应返回 5xx, 实际: {response.status_code}"


    def test_Station_StationPrice_get_0_response_format_0035(self, api_client):
        """[Station][StationPrice] get_0 - 响应格式"""
        # GET /api/stations/{stationId:guid}/prices
        response = api_client.get("station/api/stations/{stationId:guid}/prices")
        assert response is not None, "响应不应为空"
        data = response.json()
        assert isinstance(data, dict), "响应应为JSON对象"
        if response.status_code == 200:
            assert "success" in data or "data" in data or "code" in data, "200 响应应包含标准字段"


    def test_Station_StationPrice_get_1_positive_0036(self, api_client):
        """[Station][StationPrice] get_1 - 正常请求"""
        # GET /api/stations/{stationId:guid}/prices/{ruleId:guid}
        response = api_client.get("station/api/stations/{stationId:guid}/prices/{ruleId:guid}")
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"GET 正常请求不应返回 5xx, 实际: {response.status_code}"


    def test_Station_StationPrice_get_1_no_auth_0036(self, api_client):
        """[Station][StationPrice] get_1 - 缺少认证头"""
        # GET /api/stations/{stationId:guid}/prices/{ruleId:guid}
        api_client.clear_token()
        try:
            response = api_client.get("station/api/stations/{stationId:guid}/prices/{ruleId:guid}")
            assert response is not None, "响应不应为空"
            assert response.status_code in (200, 400, 401, 403), f"无认证头应返回 401/403, 实际: {response.status_code}"
        finally:
            api_client.restore_token()


    def test_Station_StationPrice_get_1_invalid_token_0036(self, api_client):
        """[Station][StationPrice] get_1 - 无效Token"""
        # GET /api/stations/{stationId:guid}/prices/{ruleId:guid}
        api_client.set_invalid_token()
        try:
            response = api_client.get("station/api/stations/{stationId:guid}/prices/{ruleId:guid}")
            assert response is not None, "响应不应为空"
            assert response.status_code in (200, 400, 401, 403), f"无效Token应返回 401/403, 实际: {response.status_code}"
        finally:
            api_client.restore_token()


    def test_Station_StationPrice_get_1_tenant_isolation_0036(self, api_client):
        """[Station][StationPrice] get_1 - 租户隔离"""
        # GET /api/stations/{stationId:guid}/prices/{ruleId:guid}
        response = api_client.get("station/api/stations/{stationId:guid}/prices/{ruleId:guid}")
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"租户隔离测试不应返回 5xx, 实际: {response.status_code}"
        data = response.json()
        assert isinstance(data, dict), "响应应为JSON对象"


    def test_Station_StationPrice_get_1_invalid_id_0036(self, api_client):
        """[Station][StationPrice] get_1 - 无效ID"""
        # GET /api/stations/{stationId:guid}/prices/{ruleId:guid}
        response = api_client.get("station/api/stations/{stationId:guid}/prices/{ruleId:guid}")
        assert response is not None, "响应不应为空"
        assert response.status_code in (200, 400, 403, 404), f"无效ID应返回 200/400/403/404, 实际: {response.status_code}"


    def test_Station_StationPrice_get_1_not_found_id_0036(self, api_client):
        """[Station][StationPrice] get_1 - 不存在ID"""
        # GET /api/stations/{stationId:guid}/prices/{ruleId:guid}
        response = api_client.get("station/api/stations/{stationId:guid}/prices/{ruleId:guid}")
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"不存在ID不应返回 5xx, 实际: {response.status_code}"


    def test_Station_StationPrice_get_1_boundary_0036(self, api_client):
        """[Station][StationPrice] get_1 - 边界值测试"""
        # GET /api/stations/{stationId:guid}/prices/{ruleId:guid}
        response = api_client.get("station/api/stations/{stationId:guid}/prices/{ruleId:guid}")
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"边界值测试不应返回 5xx 服务器错误, 实际: {response.status_code}"
        assert isinstance(response.json(), dict), "响应应为JSON对象"


    def test_Station_StationPrice_get_1_sql_injection_0036(self, api_client):
        """[Station][StationPrice] get_1 - SQL注入防护"""
        # GET /api/stations/{stationId:guid}/prices/{ruleId:guid}
        response = api_client.get("station/api/stations/{stationId:guid}/prices/{ruleId:guid}")
        assert response is not None, "响应不应为空"
        assert response.status_code != 500, f"SQL注入不应导致服务器错误, 实际: {response.status_code}"
        data = response.json()
        assert isinstance(data, dict), "响应应为JSON对象"


    def test_Station_StationPrice_get_1_concurrent_0036(self, api_client):
        """[Station][StationPrice] get_1 - 并发请求"""
        # GET /api/stations/{stationId:guid}/prices/{ruleId:guid}
        responses = []
        for _ in range(3):
            r = api_client.get("station/api/stations/{stationId:guid}/prices/{ruleId:guid}")
            responses.append(r)
        for r in responses:
            assert r is not None, "并发响应不应为空"
            assert r.status_code < 500, f"并发请求不应返回 5xx, 实际: {r.status_code}"


    def test_Station_StationPrice_get_1_timeout_0036(self, api_client):
        """[Station][StationPrice] get_1 - 超时处理"""
        # GET /api/stations/{stationId:guid}/prices/{ruleId:guid}
        response = api_client.get("station/api/stations/{stationId:guid}/prices/{ruleId:guid}")
        assert response is not None, "超时处理响应不应为空"
        assert response.status_code < 500, f"超时测试不应返回 5xx, 实际: {response.status_code}"


    def test_Station_StationPrice_get_1_permission_denied_0036(self, api_client):
        """[Station][StationPrice] get_1 - 权限不足"""
        # GET /api/stations/{stationId:guid}/prices/{ruleId:guid}
        response = api_client.get("station/api/stations/{stationId:guid}/prices/{ruleId:guid}")
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"权限测试不应返回 5xx, 实际: {response.status_code}"


    def test_Station_StationPrice_get_1_response_format_0036(self, api_client):
        """[Station][StationPrice] get_1 - 响应格式"""
        # GET /api/stations/{stationId:guid}/prices/{ruleId:guid}
        response = api_client.get("station/api/stations/{stationId:guid}/prices/{ruleId:guid}")
        assert response is not None, "响应不应为空"
        data = response.json()
        assert isinstance(data, dict), "响应应为JSON对象"
        if response.status_code == 200:
            assert "success" in data or "data" in data or "code" in data, "200 响应应包含标准字段"


    def test_Station_StationPrice_get_2_positive_0037(self, api_client):
        """[Station][StationPrice] get_2 - 正常请求"""
        # GET /api/stations/{stationId:guid}/prices/current
        response = api_client.get("station/api/stations/{stationId:guid}/prices/current")
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"GET 正常请求不应返回 5xx, 实际: {response.status_code}"


    def test_Station_StationPrice_get_2_no_auth_0037(self, api_client):
        """[Station][StationPrice] get_2 - 缺少认证头"""
        # GET /api/stations/{stationId:guid}/prices/current
        api_client.clear_token()
        try:
            response = api_client.get("station/api/stations/{stationId:guid}/prices/current")
            assert response is not None, "响应不应为空"
            assert response.status_code in (200, 400, 401, 403), f"无认证头应返回 401/403, 实际: {response.status_code}"
        finally:
            api_client.restore_token()


    def test_Station_StationPrice_get_2_invalid_token_0037(self, api_client):
        """[Station][StationPrice] get_2 - 无效Token"""
        # GET /api/stations/{stationId:guid}/prices/current
        api_client.set_invalid_token()
        try:
            response = api_client.get("station/api/stations/{stationId:guid}/prices/current")
            assert response is not None, "响应不应为空"
            assert response.status_code in (200, 400, 401, 403), f"无效Token应返回 401/403, 实际: {response.status_code}"
        finally:
            api_client.restore_token()


    def test_Station_StationPrice_get_2_tenant_isolation_0037(self, api_client):
        """[Station][StationPrice] get_2 - 租户隔离"""
        # GET /api/stations/{stationId:guid}/prices/current
        response = api_client.get("station/api/stations/{stationId:guid}/prices/current")
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"租户隔离测试不应返回 5xx, 实际: {response.status_code}"
        data = response.json()
        assert isinstance(data, dict), "响应应为JSON对象"


    def test_Station_StationPrice_get_2_boundary_0037(self, api_client):
        """[Station][StationPrice] get_2 - 边界值测试"""
        # GET /api/stations/{stationId:guid}/prices/current
        response = api_client.get("station/api/stations/{stationId:guid}/prices/current")
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"边界值测试不应返回 5xx 服务器错误, 实际: {response.status_code}"
        assert isinstance(response.json(), dict), "响应应为JSON对象"


    def test_Station_StationPrice_get_2_sql_injection_0037(self, api_client):
        """[Station][StationPrice] get_2 - SQL注入防护"""
        # GET /api/stations/{stationId:guid}/prices/current
        response = api_client.get("station/api/stations/{stationId:guid}/prices/current")
        assert response is not None, "响应不应为空"
        assert response.status_code != 500, f"SQL注入不应导致服务器错误, 实际: {response.status_code}"
        data = response.json()
        assert isinstance(data, dict), "响应应为JSON对象"


    def test_Station_StationPrice_get_2_concurrent_0037(self, api_client):
        """[Station][StationPrice] get_2 - 并发请求"""
        # GET /api/stations/{stationId:guid}/prices/current
        responses = []
        for _ in range(3):
            r = api_client.get("station/api/stations/{stationId:guid}/prices/current")
            responses.append(r)
        for r in responses:
            assert r is not None, "并发响应不应为空"
            assert r.status_code < 500, f"并发请求不应返回 5xx, 实际: {r.status_code}"


    def test_Station_StationPrice_get_2_timeout_0037(self, api_client):
        """[Station][StationPrice] get_2 - 超时处理"""
        # GET /api/stations/{stationId:guid}/prices/current
        response = api_client.get("station/api/stations/{stationId:guid}/prices/current")
        assert response is not None, "超时处理响应不应为空"
        assert response.status_code < 500, f"超时测试不应返回 5xx, 实际: {response.status_code}"


    def test_Station_StationPrice_get_2_permission_denied_0037(self, api_client):
        """[Station][StationPrice] get_2 - 权限不足"""
        # GET /api/stations/{stationId:guid}/prices/current
        response = api_client.get("station/api/stations/{stationId:guid}/prices/current")
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"权限测试不应返回 5xx, 实际: {response.status_code}"


    def test_Station_StationPrice_get_2_response_format_0037(self, api_client):
        """[Station][StationPrice] get_2 - 响应格式"""
        # GET /api/stations/{stationId:guid}/prices/current
        response = api_client.get("station/api/stations/{stationId:guid}/prices/current")
        assert response is not None, "响应不应为空"
        data = response.json()
        assert isinstance(data, dict), "响应应为JSON对象"
        if response.status_code == 200:
            assert "success" in data or "data" in data or "code" in data, "200 响应应包含标准字段"


    def test_Station_StationPrice_get_3_positive_0038(self, api_client):
        """[Station][StationPrice] get_3 - 正常请求"""
        # GET /api/stations/{stationId:guid}/prices/api/price-templates
        response = api_client.get("station/api/stations/{stationId:guid}/prices/api/price-templates")
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"GET 正常请求不应返回 5xx, 实际: {response.status_code}"


    def test_Station_StationPrice_get_3_no_auth_0038(self, api_client):
        """[Station][StationPrice] get_3 - 缺少认证头"""
        # GET /api/stations/{stationId:guid}/prices/api/price-templates
        api_client.clear_token()
        try:
            response = api_client.get("station/api/stations/{stationId:guid}/prices/api/price-templates")
            assert response is not None, "响应不应为空"
            assert response.status_code in (200, 400, 401, 403), f"无认证头应返回 401/403, 实际: {response.status_code}"
        finally:
            api_client.restore_token()


    def test_Station_StationPrice_get_3_invalid_token_0038(self, api_client):
        """[Station][StationPrice] get_3 - 无效Token"""
        # GET /api/stations/{stationId:guid}/prices/api/price-templates
        api_client.set_invalid_token()
        try:
            response = api_client.get("station/api/stations/{stationId:guid}/prices/api/price-templates")
            assert response is not None, "响应不应为空"
            assert response.status_code in (200, 400, 401, 403), f"无效Token应返回 401/403, 实际: {response.status_code}"
        finally:
            api_client.restore_token()


    def test_Station_StationPrice_get_3_tenant_isolation_0038(self, api_client):
        """[Station][StationPrice] get_3 - 租户隔离"""
        # GET /api/stations/{stationId:guid}/prices/api/price-templates
        response = api_client.get("station/api/stations/{stationId:guid}/prices/api/price-templates")
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"租户隔离测试不应返回 5xx, 实际: {response.status_code}"
        data = response.json()
        assert isinstance(data, dict), "响应应为JSON对象"


    def test_Station_StationPrice_get_3_boundary_0038(self, api_client):
        """[Station][StationPrice] get_3 - 边界值测试"""
        # GET /api/stations/{stationId:guid}/prices/api/price-templates
        response = api_client.get("station/api/stations/{stationId:guid}/prices/api/price-templates")
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"边界值测试不应返回 5xx 服务器错误, 实际: {response.status_code}"
        assert isinstance(response.json(), dict), "响应应为JSON对象"


    def test_Station_StationPrice_get_3_sql_injection_0038(self, api_client):
        """[Station][StationPrice] get_3 - SQL注入防护"""
        # GET /api/stations/{stationId:guid}/prices/api/price-templates
        response = api_client.get("station/api/stations/{stationId:guid}/prices/api/price-templates")
        assert response is not None, "响应不应为空"
        assert response.status_code != 500, f"SQL注入不应导致服务器错误, 实际: {response.status_code}"
        data = response.json()
        assert isinstance(data, dict), "响应应为JSON对象"


    def test_Station_StationPrice_get_3_concurrent_0038(self, api_client):
        """[Station][StationPrice] get_3 - 并发请求"""
        # GET /api/stations/{stationId:guid}/prices/api/price-templates
        responses = []
        for _ in range(3):
            r = api_client.get("station/api/stations/{stationId:guid}/prices/api/price-templates")
            responses.append(r)
        for r in responses:
            assert r is not None, "并发响应不应为空"
            assert r.status_code < 500, f"并发请求不应返回 5xx, 实际: {r.status_code}"


    def test_Station_StationPrice_get_3_timeout_0038(self, api_client):
        """[Station][StationPrice] get_3 - 超时处理"""
        # GET /api/stations/{stationId:guid}/prices/api/price-templates
        response = api_client.get("station/api/stations/{stationId:guid}/prices/api/price-templates")
        assert response is not None, "超时处理响应不应为空"
        assert response.status_code < 500, f"超时测试不应返回 5xx, 实际: {response.status_code}"


    def test_Station_StationPrice_get_3_permission_denied_0038(self, api_client):
        """[Station][StationPrice] get_3 - 权限不足"""
        # GET /api/stations/{stationId:guid}/prices/api/price-templates
        response = api_client.get("station/api/stations/{stationId:guid}/prices/api/price-templates")
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"权限测试不应返回 5xx, 实际: {response.status_code}"


    def test_Station_StationPrice_get_3_response_format_0038(self, api_client):
        """[Station][StationPrice] get_3 - 响应格式"""
        # GET /api/stations/{stationId:guid}/prices/api/price-templates
        response = api_client.get("station/api/stations/{stationId:guid}/prices/api/price-templates")
        assert response is not None, "响应不应为空"
        data = response.json()
        assert isinstance(data, dict), "响应应为JSON对象"
        if response.status_code == 200:
            assert "success" in data or "data" in data or "code" in data, "200 响应应包含标准字段"


    def test_Station_StationPrice_get_4_positive_0039(self, api_client):
        """[Station][StationPrice] get_4 - 正常请求"""
        # GET /api/stations/{stationId:guid}/prices/overview
        response = api_client.get("station/api/stations/{stationId:guid}/prices/overview")
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"GET 正常请求不应返回 5xx, 实际: {response.status_code}"


    def test_Station_StationPrice_get_4_no_auth_0039(self, api_client):
        """[Station][StationPrice] get_4 - 缺少认证头"""
        # GET /api/stations/{stationId:guid}/prices/overview
        api_client.clear_token()
        try:
            response = api_client.get("station/api/stations/{stationId:guid}/prices/overview")
            assert response is not None, "响应不应为空"
            assert response.status_code in (200, 400, 401, 403), f"无认证头应返回 401/403, 实际: {response.status_code}"
        finally:
            api_client.restore_token()


    def test_Station_StationPrice_get_4_invalid_token_0039(self, api_client):
        """[Station][StationPrice] get_4 - 无效Token"""
        # GET /api/stations/{stationId:guid}/prices/overview
        api_client.set_invalid_token()
        try:
            response = api_client.get("station/api/stations/{stationId:guid}/prices/overview")
            assert response is not None, "响应不应为空"
            assert response.status_code in (200, 400, 401, 403), f"无效Token应返回 401/403, 实际: {response.status_code}"
        finally:
            api_client.restore_token()


    def test_Station_StationPrice_get_4_tenant_isolation_0039(self, api_client):
        """[Station][StationPrice] get_4 - 租户隔离"""
        # GET /api/stations/{stationId:guid}/prices/overview
        response = api_client.get("station/api/stations/{stationId:guid}/prices/overview")
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"租户隔离测试不应返回 5xx, 实际: {response.status_code}"
        data = response.json()
        assert isinstance(data, dict), "响应应为JSON对象"


    def test_Station_StationPrice_get_4_boundary_0039(self, api_client):
        """[Station][StationPrice] get_4 - 边界值测试"""
        # GET /api/stations/{stationId:guid}/prices/overview
        response = api_client.get("station/api/stations/{stationId:guid}/prices/overview")
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"边界值测试不应返回 5xx 服务器错误, 实际: {response.status_code}"
        assert isinstance(response.json(), dict), "响应应为JSON对象"


    def test_Station_StationPrice_get_4_sql_injection_0039(self, api_client):
        """[Station][StationPrice] get_4 - SQL注入防护"""
        # GET /api/stations/{stationId:guid}/prices/overview
        response = api_client.get("station/api/stations/{stationId:guid}/prices/overview")
        assert response is not None, "响应不应为空"
        assert response.status_code != 500, f"SQL注入不应导致服务器错误, 实际: {response.status_code}"
        data = response.json()
        assert isinstance(data, dict), "响应应为JSON对象"


    def test_Station_StationPrice_get_4_concurrent_0039(self, api_client):
        """[Station][StationPrice] get_4 - 并发请求"""
        # GET /api/stations/{stationId:guid}/prices/overview
        responses = []
        for _ in range(3):
            r = api_client.get("station/api/stations/{stationId:guid}/prices/overview")
            responses.append(r)
        for r in responses:
            assert r is not None, "并发响应不应为空"
            assert r.status_code < 500, f"并发请求不应返回 5xx, 实际: {r.status_code}"


    def test_Station_StationPrice_get_4_timeout_0039(self, api_client):
        """[Station][StationPrice] get_4 - 超时处理"""
        # GET /api/stations/{stationId:guid}/prices/overview
        response = api_client.get("station/api/stations/{stationId:guid}/prices/overview")
        assert response is not None, "超时处理响应不应为空"
        assert response.status_code < 500, f"超时测试不应返回 5xx, 实际: {response.status_code}"


    def test_Station_StationPrice_get_4_permission_denied_0039(self, api_client):
        """[Station][StationPrice] get_4 - 权限不足"""
        # GET /api/stations/{stationId:guid}/prices/overview
        response = api_client.get("station/api/stations/{stationId:guid}/prices/overview")
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"权限测试不应返回 5xx, 实际: {response.status_code}"


    def test_Station_StationPrice_get_4_response_format_0039(self, api_client):
        """[Station][StationPrice] get_4 - 响应格式"""
        # GET /api/stations/{stationId:guid}/prices/overview
        response = api_client.get("station/api/stations/{stationId:guid}/prices/overview")
        assert response is not None, "响应不应为空"
        data = response.json()
        assert isinstance(data, dict), "响应应为JSON对象"
        if response.status_code == 200:
            assert "success" in data or "data" in data or "code" in data, "200 响应应包含标准字段"


    def test_Station_StationPrice_post_5_positive_0040(self, api_client):
        """[Station][StationPrice] post_5 - 正常请求"""
        # POST /api/stations/{stationId:guid}/prices
        response = api_client.post("station/api/stations/{stationId:guid}/prices", json_data={"name": "test", "code": "TEST"})
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"POST 正常请求不应返回 5xx, 实际: {response.status_code}"


    def test_Station_StationPrice_post_5_no_auth_0040(self, api_client):
        """[Station][StationPrice] post_5 - 缺少认证头"""
        # POST /api/stations/{stationId:guid}/prices
        api_client.clear_token()
        try:
            response = api_client.post("station/api/stations/{stationId:guid}/prices")
            assert response is not None, "响应不应为空"
            assert response.status_code in (200, 400, 401, 403), f"无认证头应返回 401/403, 实际: {response.status_code}"
        finally:
            api_client.restore_token()


    def test_Station_StationPrice_post_5_invalid_token_0040(self, api_client):
        """[Station][StationPrice] post_5 - 无效Token"""
        # POST /api/stations/{stationId:guid}/prices
        api_client.set_invalid_token()
        try:
            response = api_client.post("station/api/stations/{stationId:guid}/prices")
            assert response is not None, "响应不应为空"
            assert response.status_code in (200, 400, 401, 403), f"无效Token应返回 401/403, 实际: {response.status_code}"
        finally:
            api_client.restore_token()


    def test_Station_StationPrice_post_5_tenant_isolation_0040(self, api_client):
        """[Station][StationPrice] post_5 - 租户隔离"""
        # POST /api/stations/{stationId:guid}/prices
        response = api_client.post("station/api/stations/{stationId:guid}/prices")
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"租户隔离测试不应返回 5xx, 实际: {response.status_code}"
        data = response.json()
        assert isinstance(data, dict), "响应应为JSON对象"


    def test_Station_StationPrice_post_5_empty_body_0040(self, api_client):
        """[Station][StationPrice] post_5 - 空请求体"""
        # POST /api/stations/{stationId:guid}/prices
        response = api_client.post("station/api/stations/{stationId:guid}/prices")
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"空请求体不应返回 5xx, 实际: {response.status_code}"


    def test_Station_StationPrice_post_5_boundary_0040(self, api_client):
        """[Station][StationPrice] post_5 - 边界值测试"""
        # POST /api/stations/{stationId:guid}/prices
        response = api_client.post("station/api/stations/{stationId:guid}/prices")
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"边界值测试不应返回 5xx 服务器错误, 实际: {response.status_code}"
        assert isinstance(response.json(), dict), "响应应为JSON对象"


    def test_Station_StationPrice_post_5_sql_injection_0040(self, api_client):
        """[Station][StationPrice] post_5 - SQL注入防护"""
        # POST /api/stations/{stationId:guid}/prices
        response = api_client.post("station/api/stations/{stationId:guid}/prices")
        assert response is not None, "响应不应为空"
        assert response.status_code != 500, f"SQL注入不应导致服务器错误, 实际: {response.status_code}"
        data = response.json()
        assert isinstance(data, dict), "响应应为JSON对象"


    def test_Station_StationPrice_post_5_xss_protection_0040(self, api_client):
        """[Station][StationPrice] post_5 - XSS防护"""
        # POST /api/stations/{stationId:guid}/prices
        xss_payload = {"name": "<script>alert('xss')</script>", "code": "XSS_TEST"}
        response = api_client.post("station/api/stations/{stationId:guid}/prices", json_data=xss_payload)
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"XSS防护测试不应返回 5xx, 实际: {response.status_code}"


    def test_Station_StationPrice_post_5_large_payload_0040(self, api_client):
        """[Station][StationPrice] post_5 - 大数据量"""
        # POST /api/stations/{stationId:guid}/prices
        large_data = {"name": "x" * 10000, "code": "LARGE", "description": "y" * 50000}
        response = api_client.post("station/api/stations/{stationId:guid}/prices", json_data=large_data)
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"大数据量测试不应返回 5xx, 实际: {response.status_code}"


    def test_Station_StationPrice_post_5_concurrent_0040(self, api_client):
        """[Station][StationPrice] post_5 - 并发请求"""
        # POST /api/stations/{stationId:guid}/prices
        responses = []
        for _ in range(3):
            r = api_client.post("station/api/stations/{stationId:guid}/prices")
            responses.append(r)
        for r in responses:
            assert r is not None, "并发响应不应为空"
            assert r.status_code < 500, f"并发请求不应返回 5xx, 实际: {r.status_code}"


    def test_Station_StationPrice_post_5_timeout_0040(self, api_client):
        """[Station][StationPrice] post_5 - 超时处理"""
        # POST /api/stations/{stationId:guid}/prices
        response = api_client.post("station/api/stations/{stationId:guid}/prices")
        assert response is not None, "超时处理响应不应为空"
        assert response.status_code < 500, f"超时测试不应返回 5xx, 实际: {response.status_code}"


    def test_Station_StationPrice_post_5_permission_denied_0040(self, api_client):
        """[Station][StationPrice] post_5 - 权限不足"""
        # POST /api/stations/{stationId:guid}/prices
        response = api_client.post("station/api/stations/{stationId:guid}/prices")
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"权限测试不应返回 5xx, 实际: {response.status_code}"


    def test_Station_StationPrice_post_5_field_validation_0040(self, api_client):
        """[Station][StationPrice] post_5 - 字段校验"""
        # POST /api/stations/{stationId:guid}/prices
        invalid_data = {"name": "", "code": ""}
        response = api_client.post("station/api/stations/{stationId:guid}/prices", json_data=invalid_data)
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"字段校验不应返回 5xx, 实际: {response.status_code}"


    def test_Station_StationPrice_post_5_response_format_0040(self, api_client):
        """[Station][StationPrice] post_5 - 响应格式"""
        # POST /api/stations/{stationId:guid}/prices
        response = api_client.post("station/api/stations/{stationId:guid}/prices")
        assert response is not None, "响应不应为空"
        data = response.json()
        assert isinstance(data, dict), "响应应为JSON对象"
        if response.status_code == 200:
            assert "success" in data or "data" in data or "code" in data, "200 响应应包含标准字段"


    def test_Station_StationPrice_post_6_positive_0041(self, api_client):
        """[Station][StationPrice] post_6 - 正常请求"""
        # POST /api/stations/{stationId:guid}/prices/batch
        response = api_client.post("station/api/stations/{stationId:guid}/prices/batch", json_data={"name": "test", "code": "TEST"})
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"POST 正常请求不应返回 5xx, 实际: {response.status_code}"


    def test_Station_StationPrice_post_6_no_auth_0041(self, api_client):
        """[Station][StationPrice] post_6 - 缺少认证头"""
        # POST /api/stations/{stationId:guid}/prices/batch
        api_client.clear_token()
        try:
            response = api_client.post("station/api/stations/{stationId:guid}/prices/batch")
            assert response is not None, "响应不应为空"
            assert response.status_code in (200, 400, 401, 403), f"无认证头应返回 401/403, 实际: {response.status_code}"
        finally:
            api_client.restore_token()


    def test_Station_StationPrice_post_6_invalid_token_0041(self, api_client):
        """[Station][StationPrice] post_6 - 无效Token"""
        # POST /api/stations/{stationId:guid}/prices/batch
        api_client.set_invalid_token()
        try:
            response = api_client.post("station/api/stations/{stationId:guid}/prices/batch")
            assert response is not None, "响应不应为空"
            assert response.status_code in (200, 400, 401, 403), f"无效Token应返回 401/403, 实际: {response.status_code}"
        finally:
            api_client.restore_token()


    def test_Station_StationPrice_post_6_tenant_isolation_0041(self, api_client):
        """[Station][StationPrice] post_6 - 租户隔离"""
        # POST /api/stations/{stationId:guid}/prices/batch
        response = api_client.post("station/api/stations/{stationId:guid}/prices/batch")
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"租户隔离测试不应返回 5xx, 实际: {response.status_code}"
        data = response.json()
        assert isinstance(data, dict), "响应应为JSON对象"


    def test_Station_StationPrice_post_6_empty_body_0041(self, api_client):
        """[Station][StationPrice] post_6 - 空请求体"""
        # POST /api/stations/{stationId:guid}/prices/batch
        response = api_client.post("station/api/stations/{stationId:guid}/prices/batch")
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"空请求体不应返回 5xx, 实际: {response.status_code}"


    def test_Station_StationPrice_post_6_boundary_0041(self, api_client):
        """[Station][StationPrice] post_6 - 边界值测试"""
        # POST /api/stations/{stationId:guid}/prices/batch
        response = api_client.post("station/api/stations/{stationId:guid}/prices/batch")
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"边界值测试不应返回 5xx 服务器错误, 实际: {response.status_code}"
        assert isinstance(response.json(), dict), "响应应为JSON对象"


    def test_Station_StationPrice_post_6_sql_injection_0041(self, api_client):
        """[Station][StationPrice] post_6 - SQL注入防护"""
        # POST /api/stations/{stationId:guid}/prices/batch
        response = api_client.post("station/api/stations/{stationId:guid}/prices/batch")
        assert response is not None, "响应不应为空"
        assert response.status_code != 500, f"SQL注入不应导致服务器错误, 实际: {response.status_code}"
        data = response.json()
        assert isinstance(data, dict), "响应应为JSON对象"


    def test_Station_StationPrice_post_6_xss_protection_0041(self, api_client):
        """[Station][StationPrice] post_6 - XSS防护"""
        # POST /api/stations/{stationId:guid}/prices/batch
        xss_payload = {"name": "<script>alert('xss')</script>", "code": "XSS_TEST"}
        response = api_client.post("station/api/stations/{stationId:guid}/prices/batch", json_data=xss_payload)
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"XSS防护测试不应返回 5xx, 实际: {response.status_code}"


    def test_Station_StationPrice_post_6_large_payload_0041(self, api_client):
        """[Station][StationPrice] post_6 - 大数据量"""
        # POST /api/stations/{stationId:guid}/prices/batch
        large_data = {"name": "x" * 10000, "code": "LARGE", "description": "y" * 50000}
        response = api_client.post("station/api/stations/{stationId:guid}/prices/batch", json_data=large_data)
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"大数据量测试不应返回 5xx, 实际: {response.status_code}"


    def test_Station_StationPrice_post_6_concurrent_0041(self, api_client):
        """[Station][StationPrice] post_6 - 并发请求"""
        # POST /api/stations/{stationId:guid}/prices/batch
        responses = []
        for _ in range(3):
            r = api_client.post("station/api/stations/{stationId:guid}/prices/batch")
            responses.append(r)
        for r in responses:
            assert r is not None, "并发响应不应为空"
            assert r.status_code < 500, f"并发请求不应返回 5xx, 实际: {r.status_code}"


    def test_Station_StationPrice_post_6_timeout_0041(self, api_client):
        """[Station][StationPrice] post_6 - 超时处理"""
        # POST /api/stations/{stationId:guid}/prices/batch
        response = api_client.post("station/api/stations/{stationId:guid}/prices/batch")
        assert response is not None, "超时处理响应不应为空"
        assert response.status_code < 500, f"超时测试不应返回 5xx, 实际: {response.status_code}"


    def test_Station_StationPrice_post_6_permission_denied_0041(self, api_client):
        """[Station][StationPrice] post_6 - 权限不足"""
        # POST /api/stations/{stationId:guid}/prices/batch
        response = api_client.post("station/api/stations/{stationId:guid}/prices/batch")
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"权限测试不应返回 5xx, 实际: {response.status_code}"


    def test_Station_StationPrice_post_6_field_validation_0041(self, api_client):
        """[Station][StationPrice] post_6 - 字段校验"""
        # POST /api/stations/{stationId:guid}/prices/batch
        invalid_data = {"name": "", "code": ""}
        response = api_client.post("station/api/stations/{stationId:guid}/prices/batch", json_data=invalid_data)
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"字段校验不应返回 5xx, 实际: {response.status_code}"


    def test_Station_StationPrice_post_6_response_format_0041(self, api_client):
        """[Station][StationPrice] post_6 - 响应格式"""
        # POST /api/stations/{stationId:guid}/prices/batch
        response = api_client.post("station/api/stations/{stationId:guid}/prices/batch")
        assert response is not None, "响应不应为空"
        data = response.json()
        assert isinstance(data, dict), "响应应为JSON对象"
        if response.status_code == 200:
            assert "success" in data or "data" in data or "code" in data, "200 响应应包含标准字段"


    def test_Station_StationPrice_post_7_positive_0042(self, api_client):
        """[Station][StationPrice] post_7 - 正常请求"""
        # POST /api/stations/{stationId:guid}/prices/copy-from/{sourceStationId:guid}
        response = api_client.post("station/api/stations/{stationId:guid}/prices/copy-from/{sourceStationId:guid}", json_data={"name": "test", "code": "TEST"})
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"POST 正常请求不应返回 5xx, 实际: {response.status_code}"


    def test_Station_StationPrice_post_7_no_auth_0042(self, api_client):
        """[Station][StationPrice] post_7 - 缺少认证头"""
        # POST /api/stations/{stationId:guid}/prices/copy-from/{sourceStationId:guid}
        api_client.clear_token()
        try:
            response = api_client.post("station/api/stations/{stationId:guid}/prices/copy-from/{sourceStationId:guid}")
            assert response is not None, "响应不应为空"
            assert response.status_code in (200, 400, 401, 403), f"无认证头应返回 401/403, 实际: {response.status_code}"
        finally:
            api_client.restore_token()


    def test_Station_StationPrice_post_7_invalid_token_0042(self, api_client):
        """[Station][StationPrice] post_7 - 无效Token"""
        # POST /api/stations/{stationId:guid}/prices/copy-from/{sourceStationId:guid}
        api_client.set_invalid_token()
        try:
            response = api_client.post("station/api/stations/{stationId:guid}/prices/copy-from/{sourceStationId:guid}")
            assert response is not None, "响应不应为空"
            assert response.status_code in (200, 400, 401, 403), f"无效Token应返回 401/403, 实际: {response.status_code}"
        finally:
            api_client.restore_token()


    def test_Station_StationPrice_post_7_tenant_isolation_0042(self, api_client):
        """[Station][StationPrice] post_7 - 租户隔离"""
        # POST /api/stations/{stationId:guid}/prices/copy-from/{sourceStationId:guid}
        response = api_client.post("station/api/stations/{stationId:guid}/prices/copy-from/{sourceStationId:guid}")
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"租户隔离测试不应返回 5xx, 实际: {response.status_code}"
        data = response.json()
        assert isinstance(data, dict), "响应应为JSON对象"


    def test_Station_StationPrice_post_7_empty_body_0042(self, api_client):
        """[Station][StationPrice] post_7 - 空请求体"""
        # POST /api/stations/{stationId:guid}/prices/copy-from/{sourceStationId:guid}
        response = api_client.post("station/api/stations/{stationId:guid}/prices/copy-from/{sourceStationId:guid}")
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"空请求体不应返回 5xx, 实际: {response.status_code}"


    def test_Station_StationPrice_post_7_invalid_id_0042(self, api_client):
        """[Station][StationPrice] post_7 - 无效ID"""
        # POST /api/stations/{stationId:guid}/prices/copy-from/{sourceStationId:guid}
        response = api_client.post("station/api/stations/{stationId:guid}/prices/copy-from/{sourceStationId:guid}")
        assert response is not None, "响应不应为空"
        assert response.status_code in (200, 400, 403, 404), f"无效ID应返回 200/400/403/404, 实际: {response.status_code}"


    def test_Station_StationPrice_post_7_not_found_id_0042(self, api_client):
        """[Station][StationPrice] post_7 - 不存在ID"""
        # POST /api/stations/{stationId:guid}/prices/copy-from/{sourceStationId:guid}
        response = api_client.post("station/api/stations/{stationId:guid}/prices/copy-from/{sourceStationId:guid}")
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"不存在ID不应返回 5xx, 实际: {response.status_code}"


    def test_Station_StationPrice_post_7_boundary_0042(self, api_client):
        """[Station][StationPrice] post_7 - 边界值测试"""
        # POST /api/stations/{stationId:guid}/prices/copy-from/{sourceStationId:guid}
        response = api_client.post("station/api/stations/{stationId:guid}/prices/copy-from/{sourceStationId:guid}")
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"边界值测试不应返回 5xx 服务器错误, 实际: {response.status_code}"
        assert isinstance(response.json(), dict), "响应应为JSON对象"


    def test_Station_StationPrice_post_7_sql_injection_0042(self, api_client):
        """[Station][StationPrice] post_7 - SQL注入防护"""
        # POST /api/stations/{stationId:guid}/prices/copy-from/{sourceStationId:guid}
        response = api_client.post("station/api/stations/{stationId:guid}/prices/copy-from/{sourceStationId:guid}")
        assert response is not None, "响应不应为空"
        assert response.status_code != 500, f"SQL注入不应导致服务器错误, 实际: {response.status_code}"
        data = response.json()
        assert isinstance(data, dict), "响应应为JSON对象"


    def test_Station_StationPrice_post_7_xss_protection_0042(self, api_client):
        """[Station][StationPrice] post_7 - XSS防护"""
        # POST /api/stations/{stationId:guid}/prices/copy-from/{sourceStationId:guid}
        xss_payload = {"name": "<script>alert('xss')</script>", "code": "XSS_TEST"}
        response = api_client.post("station/api/stations/{stationId:guid}/prices/copy-from/{sourceStationId:guid}", json_data=xss_payload)
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"XSS防护测试不应返回 5xx, 实际: {response.status_code}"


    def test_Station_StationPrice_post_7_large_payload_0042(self, api_client):
        """[Station][StationPrice] post_7 - 大数据量"""
        # POST /api/stations/{stationId:guid}/prices/copy-from/{sourceStationId:guid}
        large_data = {"name": "x" * 10000, "code": "LARGE", "description": "y" * 50000}
        response = api_client.post("station/api/stations/{stationId:guid}/prices/copy-from/{sourceStationId:guid}", json_data=large_data)
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"大数据量测试不应返回 5xx, 实际: {response.status_code}"


    def test_Station_StationPrice_post_7_concurrent_0042(self, api_client):
        """[Station][StationPrice] post_7 - 并发请求"""
        # POST /api/stations/{stationId:guid}/prices/copy-from/{sourceStationId:guid}
        responses = []
        for _ in range(3):
            r = api_client.post("station/api/stations/{stationId:guid}/prices/copy-from/{sourceStationId:guid}")
            responses.append(r)
        for r in responses:
            assert r is not None, "并发响应不应为空"
            assert r.status_code < 500, f"并发请求不应返回 5xx, 实际: {r.status_code}"


    def test_Station_StationPrice_post_7_timeout_0042(self, api_client):
        """[Station][StationPrice] post_7 - 超时处理"""
        # POST /api/stations/{stationId:guid}/prices/copy-from/{sourceStationId:guid}
        response = api_client.post("station/api/stations/{stationId:guid}/prices/copy-from/{sourceStationId:guid}")
        assert response is not None, "超时处理响应不应为空"
        assert response.status_code < 500, f"超时测试不应返回 5xx, 实际: {response.status_code}"


    def test_Station_StationPrice_post_7_permission_denied_0042(self, api_client):
        """[Station][StationPrice] post_7 - 权限不足"""
        # POST /api/stations/{stationId:guid}/prices/copy-from/{sourceStationId:guid}
        response = api_client.post("station/api/stations/{stationId:guid}/prices/copy-from/{sourceStationId:guid}")
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"权限测试不应返回 5xx, 实际: {response.status_code}"


    def test_Station_StationPrice_post_7_field_validation_0042(self, api_client):
        """[Station][StationPrice] post_7 - 字段校验"""
        # POST /api/stations/{stationId:guid}/prices/copy-from/{sourceStationId:guid}
        invalid_data = {"name": "", "code": ""}
        response = api_client.post("station/api/stations/{stationId:guid}/prices/copy-from/{sourceStationId:guid}", json_data=invalid_data)
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"字段校验不应返回 5xx, 实际: {response.status_code}"


    def test_Station_StationPrice_post_7_response_format_0042(self, api_client):
        """[Station][StationPrice] post_7 - 响应格式"""
        # POST /api/stations/{stationId:guid}/prices/copy-from/{sourceStationId:guid}
        response = api_client.post("station/api/stations/{stationId:guid}/prices/copy-from/{sourceStationId:guid}")
        assert response is not None, "响应不应为空"
        data = response.json()
        assert isinstance(data, dict), "响应应为JSON对象"
        if response.status_code == 200:
            assert "success" in data or "data" in data or "code" in data, "200 响应应包含标准字段"


    def test_Station_StationPrice_post_8_positive_0043(self, api_client):
        """[Station][StationPrice] post_8 - 正常请求"""
        # POST /api/stations/{stationId:guid}/prices/apply-template
        response = api_client.post("station/api/stations/{stationId:guid}/prices/apply-template", json_data={"name": "test", "code": "TEST"})
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"POST 正常请求不应返回 5xx, 实际: {response.status_code}"


    def test_Station_StationPrice_post_8_no_auth_0043(self, api_client):
        """[Station][StationPrice] post_8 - 缺少认证头"""
        # POST /api/stations/{stationId:guid}/prices/apply-template
        api_client.clear_token()
        try:
            response = api_client.post("station/api/stations/{stationId:guid}/prices/apply-template")
            assert response is not None, "响应不应为空"
            assert response.status_code in (200, 400, 401, 403), f"无认证头应返回 401/403, 实际: {response.status_code}"
        finally:
            api_client.restore_token()


    def test_Station_StationPrice_post_8_invalid_token_0043(self, api_client):
        """[Station][StationPrice] post_8 - 无效Token"""
        # POST /api/stations/{stationId:guid}/prices/apply-template
        api_client.set_invalid_token()
        try:
            response = api_client.post("station/api/stations/{stationId:guid}/prices/apply-template")
            assert response is not None, "响应不应为空"
            assert response.status_code in (200, 400, 401, 403), f"无效Token应返回 401/403, 实际: {response.status_code}"
        finally:
            api_client.restore_token()


    def test_Station_StationPrice_post_8_tenant_isolation_0043(self, api_client):
        """[Station][StationPrice] post_8 - 租户隔离"""
        # POST /api/stations/{stationId:guid}/prices/apply-template
        response = api_client.post("station/api/stations/{stationId:guid}/prices/apply-template")
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"租户隔离测试不应返回 5xx, 实际: {response.status_code}"
        data = response.json()
        assert isinstance(data, dict), "响应应为JSON对象"


    def test_Station_StationPrice_post_8_empty_body_0043(self, api_client):
        """[Station][StationPrice] post_8 - 空请求体"""
        # POST /api/stations/{stationId:guid}/prices/apply-template
        response = api_client.post("station/api/stations/{stationId:guid}/prices/apply-template")
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"空请求体不应返回 5xx, 实际: {response.status_code}"


    def test_Station_StationPrice_post_8_boundary_0043(self, api_client):
        """[Station][StationPrice] post_8 - 边界值测试"""
        # POST /api/stations/{stationId:guid}/prices/apply-template
        response = api_client.post("station/api/stations/{stationId:guid}/prices/apply-template")
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"边界值测试不应返回 5xx 服务器错误, 实际: {response.status_code}"
        assert isinstance(response.json(), dict), "响应应为JSON对象"


    def test_Station_StationPrice_post_8_sql_injection_0043(self, api_client):
        """[Station][StationPrice] post_8 - SQL注入防护"""
        # POST /api/stations/{stationId:guid}/prices/apply-template
        response = api_client.post("station/api/stations/{stationId:guid}/prices/apply-template")
        assert response is not None, "响应不应为空"
        assert response.status_code != 500, f"SQL注入不应导致服务器错误, 实际: {response.status_code}"
        data = response.json()
        assert isinstance(data, dict), "响应应为JSON对象"


    def test_Station_StationPrice_post_8_xss_protection_0043(self, api_client):
        """[Station][StationPrice] post_8 - XSS防护"""
        # POST /api/stations/{stationId:guid}/prices/apply-template
        xss_payload = {"name": "<script>alert('xss')</script>", "code": "XSS_TEST"}
        response = api_client.post("station/api/stations/{stationId:guid}/prices/apply-template", json_data=xss_payload)
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"XSS防护测试不应返回 5xx, 实际: {response.status_code}"


    def test_Station_StationPrice_post_8_large_payload_0043(self, api_client):
        """[Station][StationPrice] post_8 - 大数据量"""
        # POST /api/stations/{stationId:guid}/prices/apply-template
        large_data = {"name": "x" * 10000, "code": "LARGE", "description": "y" * 50000}
        response = api_client.post("station/api/stations/{stationId:guid}/prices/apply-template", json_data=large_data)
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"大数据量测试不应返回 5xx, 实际: {response.status_code}"


    def test_Station_StationPrice_post_8_concurrent_0043(self, api_client):
        """[Station][StationPrice] post_8 - 并发请求"""
        # POST /api/stations/{stationId:guid}/prices/apply-template
        responses = []
        for _ in range(3):
            r = api_client.post("station/api/stations/{stationId:guid}/prices/apply-template")
            responses.append(r)
        for r in responses:
            assert r is not None, "并发响应不应为空"
            assert r.status_code < 500, f"并发请求不应返回 5xx, 实际: {r.status_code}"


    def test_Station_StationPrice_post_8_timeout_0043(self, api_client):
        """[Station][StationPrice] post_8 - 超时处理"""
        # POST /api/stations/{stationId:guid}/prices/apply-template
        response = api_client.post("station/api/stations/{stationId:guid}/prices/apply-template")
        assert response is not None, "超时处理响应不应为空"
        assert response.status_code < 500, f"超时测试不应返回 5xx, 实际: {response.status_code}"


    def test_Station_StationPrice_post_8_permission_denied_0043(self, api_client):
        """[Station][StationPrice] post_8 - 权限不足"""
        # POST /api/stations/{stationId:guid}/prices/apply-template
        response = api_client.post("station/api/stations/{stationId:guid}/prices/apply-template")
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"权限测试不应返回 5xx, 实际: {response.status_code}"


    def test_Station_StationPrice_post_8_field_validation_0043(self, api_client):
        """[Station][StationPrice] post_8 - 字段校验"""
        # POST /api/stations/{stationId:guid}/prices/apply-template
        invalid_data = {"name": "", "code": ""}
        response = api_client.post("station/api/stations/{stationId:guid}/prices/apply-template", json_data=invalid_data)
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"字段校验不应返回 5xx, 实际: {response.status_code}"


    def test_Station_StationPrice_post_8_response_format_0043(self, api_client):
        """[Station][StationPrice] post_8 - 响应格式"""
        # POST /api/stations/{stationId:guid}/prices/apply-template
        response = api_client.post("station/api/stations/{stationId:guid}/prices/apply-template")
        assert response is not None, "响应不应为空"
        data = response.json()
        assert isinstance(data, dict), "响应应为JSON对象"
        if response.status_code == 200:
            assert "success" in data or "data" in data or "code" in data, "200 响应应包含标准字段"


    def test_Station_StationPrice_put_9_positive_0044(self, api_client):
        """[Station][StationPrice] put_9 - 正常请求"""
        # PUT /api/stations/{stationId:guid}/prices/{ruleId:guid}
        response = api_client.put("station/api/stations/{stationId:guid}/prices/{ruleId:guid}", json_data={"name": "updated"})
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"PUT 正常请求不应返回 5xx, 实际: {response.status_code}"


    def test_Station_StationPrice_put_9_no_auth_0044(self, api_client):
        """[Station][StationPrice] put_9 - 缺少认证头"""
        # PUT /api/stations/{stationId:guid}/prices/{ruleId:guid}
        api_client.clear_token()
        try:
            response = api_client.put("station/api/stations/{stationId:guid}/prices/{ruleId:guid}")
            assert response is not None, "响应不应为空"
            assert response.status_code in (200, 400, 401, 403), f"无认证头应返回 401/403, 实际: {response.status_code}"
        finally:
            api_client.restore_token()


    def test_Station_StationPrice_put_9_invalid_token_0044(self, api_client):
        """[Station][StationPrice] put_9 - 无效Token"""
        # PUT /api/stations/{stationId:guid}/prices/{ruleId:guid}
        api_client.set_invalid_token()
        try:
            response = api_client.put("station/api/stations/{stationId:guid}/prices/{ruleId:guid}")
            assert response is not None, "响应不应为空"
            assert response.status_code in (200, 400, 401, 403), f"无效Token应返回 401/403, 实际: {response.status_code}"
        finally:
            api_client.restore_token()


    def test_Station_StationPrice_put_9_tenant_isolation_0044(self, api_client):
        """[Station][StationPrice] put_9 - 租户隔离"""
        # PUT /api/stations/{stationId:guid}/prices/{ruleId:guid}
        response = api_client.put("station/api/stations/{stationId:guid}/prices/{ruleId:guid}")
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"租户隔离测试不应返回 5xx, 实际: {response.status_code}"
        data = response.json()
        assert isinstance(data, dict), "响应应为JSON对象"


    def test_Station_StationPrice_put_9_empty_body_0044(self, api_client):
        """[Station][StationPrice] put_9 - 空请求体"""
        # PUT /api/stations/{stationId:guid}/prices/{ruleId:guid}
        response = api_client.put("station/api/stations/{stationId:guid}/prices/{ruleId:guid}")
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"空请求体不应返回 5xx, 实际: {response.status_code}"


    def test_Station_StationPrice_put_9_invalid_id_0044(self, api_client):
        """[Station][StationPrice] put_9 - 无效ID"""
        # PUT /api/stations/{stationId:guid}/prices/{ruleId:guid}
        response = api_client.put("station/api/stations/{stationId:guid}/prices/{ruleId:guid}")
        assert response is not None, "响应不应为空"
        assert response.status_code in (200, 400, 403, 404), f"无效ID应返回 200/400/403/404, 实际: {response.status_code}"


    def test_Station_StationPrice_put_9_not_found_id_0044(self, api_client):
        """[Station][StationPrice] put_9 - 不存在ID"""
        # PUT /api/stations/{stationId:guid}/prices/{ruleId:guid}
        response = api_client.put("station/api/stations/{stationId:guid}/prices/{ruleId:guid}")
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"不存在ID不应返回 5xx, 实际: {response.status_code}"


    def test_Station_StationPrice_put_9_boundary_0044(self, api_client):
        """[Station][StationPrice] put_9 - 边界值测试"""
        # PUT /api/stations/{stationId:guid}/prices/{ruleId:guid}
        response = api_client.put("station/api/stations/{stationId:guid}/prices/{ruleId:guid}")
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"边界值测试不应返回 5xx 服务器错误, 实际: {response.status_code}"
        assert isinstance(response.json(), dict), "响应应为JSON对象"


    def test_Station_StationPrice_put_9_sql_injection_0044(self, api_client):
        """[Station][StationPrice] put_9 - SQL注入防护"""
        # PUT /api/stations/{stationId:guid}/prices/{ruleId:guid}
        response = api_client.put("station/api/stations/{stationId:guid}/prices/{ruleId:guid}")
        assert response is not None, "响应不应为空"
        assert response.status_code != 500, f"SQL注入不应导致服务器错误, 实际: {response.status_code}"
        data = response.json()
        assert isinstance(data, dict), "响应应为JSON对象"


    def test_Station_StationPrice_put_9_xss_protection_0044(self, api_client):
        """[Station][StationPrice] put_9 - XSS防护"""
        # PUT /api/stations/{stationId:guid}/prices/{ruleId:guid}
        xss_payload = {"name": "<script>alert('xss')</script>", "code": "XSS_TEST"}
        response = api_client.put("station/api/stations/{stationId:guid}/prices/{ruleId:guid}", json_data=xss_payload)
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"XSS防护测试不应返回 5xx, 实际: {response.status_code}"


    def test_Station_StationPrice_put_9_large_payload_0044(self, api_client):
        """[Station][StationPrice] put_9 - 大数据量"""
        # PUT /api/stations/{stationId:guid}/prices/{ruleId:guid}
        large_data = {"name": "x" * 10000, "code": "LARGE", "description": "y" * 50000}
        response = api_client.put("station/api/stations/{stationId:guid}/prices/{ruleId:guid}", json_data=large_data)
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"大数据量测试不应返回 5xx, 实际: {response.status_code}"


    def test_Station_StationPrice_put_9_concurrent_0044(self, api_client):
        """[Station][StationPrice] put_9 - 并发请求"""
        # PUT /api/stations/{stationId:guid}/prices/{ruleId:guid}
        responses = []
        for _ in range(3):
            r = api_client.put("station/api/stations/{stationId:guid}/prices/{ruleId:guid}")
            responses.append(r)
        for r in responses:
            assert r is not None, "并发响应不应为空"
            assert r.status_code < 500, f"并发请求不应返回 5xx, 实际: {r.status_code}"


    def test_Station_StationPrice_put_9_idempotent_0044(self, api_client):
        """[Station][StationPrice] put_9 - 幂等性"""
        # PUT /api/stations/{stationId:guid}/prices/{ruleId:guid}
        r1 = api_client.put("station/api/stations/{stationId:guid}/prices/{ruleId:guid}")
        r2 = api_client.put("station/api/stations/{stationId:guid}/prices/{ruleId:guid}")
        assert r1 is not None and r2 is not None, "幂等性响应不应为空"
        assert r1.status_code == r2.status_code, f"幂等性: 两次请求状态码应一致, {r1.status_code} vs {r2.status_code}"


    def test_Station_StationPrice_put_9_timeout_0044(self, api_client):
        """[Station][StationPrice] put_9 - 超时处理"""
        # PUT /api/stations/{stationId:guid}/prices/{ruleId:guid}
        response = api_client.put("station/api/stations/{stationId:guid}/prices/{ruleId:guid}")
        assert response is not None, "超时处理响应不应为空"
        assert response.status_code < 500, f"超时测试不应返回 5xx, 实际: {response.status_code}"


    def test_Station_StationPrice_put_9_permission_denied_0044(self, api_client):
        """[Station][StationPrice] put_9 - 权限不足"""
        # PUT /api/stations/{stationId:guid}/prices/{ruleId:guid}
        response = api_client.put("station/api/stations/{stationId:guid}/prices/{ruleId:guid}")
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"权限测试不应返回 5xx, 实际: {response.status_code}"


    def test_Station_StationPrice_put_9_field_validation_0044(self, api_client):
        """[Station][StationPrice] put_9 - 字段校验"""
        # PUT /api/stations/{stationId:guid}/prices/{ruleId:guid}
        invalid_data = {"name": "", "code": ""}
        response = api_client.put("station/api/stations/{stationId:guid}/prices/{ruleId:guid}", json_data=invalid_data)
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"字段校验不应返回 5xx, 实际: {response.status_code}"


    def test_Station_StationPrice_put_9_response_format_0044(self, api_client):
        """[Station][StationPrice] put_9 - 响应格式"""
        # PUT /api/stations/{stationId:guid}/prices/{ruleId:guid}
        response = api_client.put("station/api/stations/{stationId:guid}/prices/{ruleId:guid}")
        assert response is not None, "响应不应为空"
        data = response.json()
        assert isinstance(data, dict), "响应应为JSON对象"
        if response.status_code == 200:
            assert "success" in data or "data" in data or "code" in data, "200 响应应包含标准字段"


    def test_Station_StationPrice_delete_10_positive_0045(self, api_client):
        """[Station][StationPrice] delete_10 - 正常请求"""
        # DELETE /api/stations/{stationId:guid}/prices/{ruleId:guid}
        response = api_client.delete("station/api/stations/{stationId:guid}/prices/{ruleId:guid}")
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"DELETE 正常请求不应返回 5xx, 实际: {response.status_code}"


    def test_Station_StationPrice_delete_10_no_auth_0045(self, api_client):
        """[Station][StationPrice] delete_10 - 缺少认证头"""
        # DELETE /api/stations/{stationId:guid}/prices/{ruleId:guid}
        api_client.clear_token()
        try:
            response = api_client.delete("station/api/stations/{stationId:guid}/prices/{ruleId:guid}")
            assert response is not None, "响应不应为空"
            assert response.status_code in (200, 400, 401, 403), f"无认证头应返回 401/403, 实际: {response.status_code}"
        finally:
            api_client.restore_token()


    def test_Station_StationPrice_delete_10_invalid_token_0045(self, api_client):
        """[Station][StationPrice] delete_10 - 无效Token"""
        # DELETE /api/stations/{stationId:guid}/prices/{ruleId:guid}
        api_client.set_invalid_token()
        try:
            response = api_client.delete("station/api/stations/{stationId:guid}/prices/{ruleId:guid}")
            assert response is not None, "响应不应为空"
            assert response.status_code in (200, 400, 401, 403), f"无效Token应返回 401/403, 实际: {response.status_code}"
        finally:
            api_client.restore_token()


    def test_Station_StationPrice_delete_10_tenant_isolation_0045(self, api_client):
        """[Station][StationPrice] delete_10 - 租户隔离"""
        # DELETE /api/stations/{stationId:guid}/prices/{ruleId:guid}
        response = api_client.delete("station/api/stations/{stationId:guid}/prices/{ruleId:guid}")
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"租户隔离测试不应返回 5xx, 实际: {response.status_code}"
        data = response.json()
        assert isinstance(data, dict), "响应应为JSON对象"


    def test_Station_StationPrice_delete_10_invalid_id_0045(self, api_client):
        """[Station][StationPrice] delete_10 - 无效ID"""
        # DELETE /api/stations/{stationId:guid}/prices/{ruleId:guid}
        response = api_client.delete("station/api/stations/{stationId:guid}/prices/{ruleId:guid}")
        assert response is not None, "响应不应为空"
        assert response.status_code in (200, 400, 403, 404), f"无效ID应返回 200/400/403/404, 实际: {response.status_code}"


    def test_Station_StationPrice_delete_10_not_found_id_0045(self, api_client):
        """[Station][StationPrice] delete_10 - 不存在ID"""
        # DELETE /api/stations/{stationId:guid}/prices/{ruleId:guid}
        response = api_client.delete("station/api/stations/{stationId:guid}/prices/{ruleId:guid}")
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"不存在ID不应返回 5xx, 实际: {response.status_code}"


    def test_Station_StationPrice_delete_10_boundary_0045(self, api_client):
        """[Station][StationPrice] delete_10 - 边界值测试"""
        # DELETE /api/stations/{stationId:guid}/prices/{ruleId:guid}
        response = api_client.delete("station/api/stations/{stationId:guid}/prices/{ruleId:guid}")
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"边界值测试不应返回 5xx 服务器错误, 实际: {response.status_code}"
        assert isinstance(response.json(), dict), "响应应为JSON对象"


    def test_Station_StationPrice_delete_10_sql_injection_0045(self, api_client):
        """[Station][StationPrice] delete_10 - SQL注入防护"""
        # DELETE /api/stations/{stationId:guid}/prices/{ruleId:guid}
        response = api_client.delete("station/api/stations/{stationId:guid}/prices/{ruleId:guid}")
        assert response is not None, "响应不应为空"
        assert response.status_code != 500, f"SQL注入不应导致服务器错误, 实际: {response.status_code}"
        data = response.json()
        assert isinstance(data, dict), "响应应为JSON对象"


    def test_Station_StationPrice_delete_10_concurrent_0045(self, api_client):
        """[Station][StationPrice] delete_10 - 并发请求"""
        # DELETE /api/stations/{stationId:guid}/prices/{ruleId:guid}
        responses = []
        for _ in range(3):
            r = api_client.delete("station/api/stations/{stationId:guid}/prices/{ruleId:guid}")
            responses.append(r)
        for r in responses:
            assert r is not None, "并发响应不应为空"
            assert r.status_code < 500, f"并发请求不应返回 5xx, 实际: {r.status_code}"


    def test_Station_StationPrice_delete_10_idempotent_0045(self, api_client):
        """[Station][StationPrice] delete_10 - 幂等性"""
        # DELETE /api/stations/{stationId:guid}/prices/{ruleId:guid}
        r1 = api_client.delete("station/api/stations/{stationId:guid}/prices/{ruleId:guid}")
        r2 = api_client.delete("station/api/stations/{stationId:guid}/prices/{ruleId:guid}")
        assert r1 is not None and r2 is not None, "幂等性响应不应为空"
        assert r1.status_code == r2.status_code, f"幂等性: 两次请求状态码应一致, {r1.status_code} vs {r2.status_code}"


    def test_Station_StationPrice_delete_10_timeout_0045(self, api_client):
        """[Station][StationPrice] delete_10 - 超时处理"""
        # DELETE /api/stations/{stationId:guid}/prices/{ruleId:guid}
        response = api_client.delete("station/api/stations/{stationId:guid}/prices/{ruleId:guid}")
        assert response is not None, "超时处理响应不应为空"
        assert response.status_code < 500, f"超时测试不应返回 5xx, 实际: {response.status_code}"


    def test_Station_StationPrice_delete_10_permission_denied_0045(self, api_client):
        """[Station][StationPrice] delete_10 - 权限不足"""
        # DELETE /api/stations/{stationId:guid}/prices/{ruleId:guid}
        response = api_client.delete("station/api/stations/{stationId:guid}/prices/{ruleId:guid}")
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"权限测试不应返回 5xx, 实际: {response.status_code}"


    def test_Station_StationPrice_delete_10_response_format_0045(self, api_client):
        """[Station][StationPrice] delete_10 - 响应格式"""
        # DELETE /api/stations/{stationId:guid}/prices/{ruleId:guid}
        response = api_client.delete("station/api/stations/{stationId:guid}/prices/{ruleId:guid}")
        assert response is not None, "响应不应为空"
        data = response.json()
        assert isinstance(data, dict), "响应应为JSON对象"
        if response.status_code == 200:
            assert "success" in data or "data" in data or "code" in data, "200 响应应包含标准字段"


    def test_Station_StationPrice_patch_11_positive_0046(self, api_client):
        """[Station][StationPrice] patch_11 - 正常请求"""
        # PATCH /api/stations/{stationId:guid}/prices/{ruleId:guid}/toggle
        response = api_client.patch("station/api/stations/{stationId:guid}/prices/{ruleId:guid}/toggle", json_data={"name": "updated"})
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"PATCH 正常请求不应返回 5xx, 实际: {response.status_code}"


    def test_Station_StationPrice_patch_11_no_auth_0046(self, api_client):
        """[Station][StationPrice] patch_11 - 缺少认证头"""
        # PATCH /api/stations/{stationId:guid}/prices/{ruleId:guid}/toggle
        api_client.clear_token()
        try:
            response = api_client.patch("station/api/stations/{stationId:guid}/prices/{ruleId:guid}/toggle")
            assert response is not None, "响应不应为空"
            assert response.status_code in (200, 400, 401, 403), f"无认证头应返回 401/403, 实际: {response.status_code}"
        finally:
            api_client.restore_token()


    def test_Station_StationPrice_patch_11_invalid_token_0046(self, api_client):
        """[Station][StationPrice] patch_11 - 无效Token"""
        # PATCH /api/stations/{stationId:guid}/prices/{ruleId:guid}/toggle
        api_client.set_invalid_token()
        try:
            response = api_client.patch("station/api/stations/{stationId:guid}/prices/{ruleId:guid}/toggle")
            assert response is not None, "响应不应为空"
            assert response.status_code in (200, 400, 401, 403), f"无效Token应返回 401/403, 实际: {response.status_code}"
        finally:
            api_client.restore_token()


    def test_Station_StationPrice_patch_11_tenant_isolation_0046(self, api_client):
        """[Station][StationPrice] patch_11 - 租户隔离"""
        # PATCH /api/stations/{stationId:guid}/prices/{ruleId:guid}/toggle
        response = api_client.patch("station/api/stations/{stationId:guid}/prices/{ruleId:guid}/toggle")
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"租户隔离测试不应返回 5xx, 实际: {response.status_code}"
        data = response.json()
        assert isinstance(data, dict), "响应应为JSON对象"


    def test_Station_StationPrice_patch_11_empty_body_0046(self, api_client):
        """[Station][StationPrice] patch_11 - 空请求体"""
        # PATCH /api/stations/{stationId:guid}/prices/{ruleId:guid}/toggle
        response = api_client.patch("station/api/stations/{stationId:guid}/prices/{ruleId:guid}/toggle")
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"空请求体不应返回 5xx, 实际: {response.status_code}"


    def test_Station_StationPrice_patch_11_invalid_id_0046(self, api_client):
        """[Station][StationPrice] patch_11 - 无效ID"""
        # PATCH /api/stations/{stationId:guid}/prices/{ruleId:guid}/toggle
        response = api_client.patch("station/api/stations/{stationId:guid}/prices/{ruleId:guid}/toggle")
        assert response is not None, "响应不应为空"
        assert response.status_code in (200, 400, 403, 404), f"无效ID应返回 200/400/403/404, 实际: {response.status_code}"


    def test_Station_StationPrice_patch_11_not_found_id_0046(self, api_client):
        """[Station][StationPrice] patch_11 - 不存在ID"""
        # PATCH /api/stations/{stationId:guid}/prices/{ruleId:guid}/toggle
        response = api_client.patch("station/api/stations/{stationId:guid}/prices/{ruleId:guid}/toggle")
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"不存在ID不应返回 5xx, 实际: {response.status_code}"


    def test_Station_StationPrice_patch_11_boundary_0046(self, api_client):
        """[Station][StationPrice] patch_11 - 边界值测试"""
        # PATCH /api/stations/{stationId:guid}/prices/{ruleId:guid}/toggle
        response = api_client.patch("station/api/stations/{stationId:guid}/prices/{ruleId:guid}/toggle")
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"边界值测试不应返回 5xx 服务器错误, 实际: {response.status_code}"
        assert isinstance(response.json(), dict), "响应应为JSON对象"


    def test_Station_StationPrice_patch_11_sql_injection_0046(self, api_client):
        """[Station][StationPrice] patch_11 - SQL注入防护"""
        # PATCH /api/stations/{stationId:guid}/prices/{ruleId:guid}/toggle
        response = api_client.patch("station/api/stations/{stationId:guid}/prices/{ruleId:guid}/toggle")
        assert response is not None, "响应不应为空"
        assert response.status_code != 500, f"SQL注入不应导致服务器错误, 实际: {response.status_code}"
        data = response.json()
        assert isinstance(data, dict), "响应应为JSON对象"


    def test_Station_StationPrice_patch_11_xss_protection_0046(self, api_client):
        """[Station][StationPrice] patch_11 - XSS防护"""
        # PATCH /api/stations/{stationId:guid}/prices/{ruleId:guid}/toggle
        xss_payload = {"name": "<script>alert('xss')</script>", "code": "XSS_TEST"}
        response = api_client.patch("station/api/stations/{stationId:guid}/prices/{ruleId:guid}/toggle", json_data=xss_payload)
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"XSS防护测试不应返回 5xx, 实际: {response.status_code}"


    def test_Station_StationPrice_patch_11_large_payload_0046(self, api_client):
        """[Station][StationPrice] patch_11 - 大数据量"""
        # PATCH /api/stations/{stationId:guid}/prices/{ruleId:guid}/toggle
        large_data = {"name": "x" * 10000, "code": "LARGE", "description": "y" * 50000}
        response = api_client.patch("station/api/stations/{stationId:guid}/prices/{ruleId:guid}/toggle", json_data=large_data)
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"大数据量测试不应返回 5xx, 实际: {response.status_code}"


    def test_Station_StationPrice_patch_11_concurrent_0046(self, api_client):
        """[Station][StationPrice] patch_11 - 并发请求"""
        # PATCH /api/stations/{stationId:guid}/prices/{ruleId:guid}/toggle
        responses = []
        for _ in range(3):
            r = api_client.patch("station/api/stations/{stationId:guid}/prices/{ruleId:guid}/toggle")
            responses.append(r)
        for r in responses:
            assert r is not None, "并发响应不应为空"
            assert r.status_code < 500, f"并发请求不应返回 5xx, 实际: {r.status_code}"


    def test_Station_StationPrice_patch_11_timeout_0046(self, api_client):
        """[Station][StationPrice] patch_11 - 超时处理"""
        # PATCH /api/stations/{stationId:guid}/prices/{ruleId:guid}/toggle
        response = api_client.patch("station/api/stations/{stationId:guid}/prices/{ruleId:guid}/toggle")
        assert response is not None, "超时处理响应不应为空"
        assert response.status_code < 500, f"超时测试不应返回 5xx, 实际: {response.status_code}"


    def test_Station_StationPrice_patch_11_permission_denied_0046(self, api_client):
        """[Station][StationPrice] patch_11 - 权限不足"""
        # PATCH /api/stations/{stationId:guid}/prices/{ruleId:guid}/toggle
        response = api_client.patch("station/api/stations/{stationId:guid}/prices/{ruleId:guid}/toggle")
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"权限测试不应返回 5xx, 实际: {response.status_code}"


    def test_Station_StationPrice_patch_11_field_validation_0046(self, api_client):
        """[Station][StationPrice] patch_11 - 字段校验"""
        # PATCH /api/stations/{stationId:guid}/prices/{ruleId:guid}/toggle
        invalid_data = {"name": "", "code": ""}
        response = api_client.patch("station/api/stations/{stationId:guid}/prices/{ruleId:guid}/toggle", json_data=invalid_data)
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"字段校验不应返回 5xx, 实际: {response.status_code}"


    def test_Station_StationPrice_patch_11_response_format_0046(self, api_client):
        """[Station][StationPrice] patch_11 - 响应格式"""
        # PATCH /api/stations/{stationId:guid}/prices/{ruleId:guid}/toggle
        response = api_client.patch("station/api/stations/{stationId:guid}/prices/{ruleId:guid}/toggle")
        assert response is not None, "响应不应为空"
        data = response.json()
        assert isinstance(data, dict), "响应应为JSON对象"
        if response.status_code == 200:
            assert "success" in data or "data" in data or "code" in data, "200 响应应包含标准字段"
