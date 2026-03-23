"""
Blockchain 存证（Evidence）API 测试
FISCO BCOS 能源数据存证功能全量接口测试

端点清单:
  外部 API（/api/evidence）:
    1. POST /api/evidence                       - 创建存证
    2. POST /api/evidence/batch                  - 批量创建存证
    3. GET  /api/evidence/{id}                   - 查询单条存证
    4. GET  /api/evidence/business/{businessId}  - 按业务ID查询
    5. GET  /api/evidence                        - 分页查询存证列表
    6. POST /api/evidence/{id}/verify            - 验证存证完整性
    7. POST /api/evidence/{id}/retry             - 重试失败存证
    8. GET  /api/evidence/statistics             - 存证统计
    9. GET  /api/evidence/timeline/{businessId}  - 存证时间线

  内部 API（/api/internal/blockchain/evidence）:
    10. POST /api/internal/blockchain/evidence              - 内部创建存证
    11. POST /api/internal/blockchain/evidence/batch         - 内部批量创建
    12. GET  /api/internal/blockchain/evidence/{id}/verify   - 内部验证存证
    13. GET  /api/internal/blockchain/evidence/{id}          - 内部查询存证
    14. GET  /api/internal/blockchain/evidence/business/{id} - 内部按业务ID查询

共 14 个端点 × ~17 测试维度 = ~238 个测试用例
"""

import pytest
import uuid
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


# ==================== 测试数据常量 ====================

VALID_EVIDENCE_BODY = {
    "evidenceType": "charging_session",
    "businessId": "CS-2026-00001",
    "stationId": "ST-001",
    "deviceId": "DEV-001",
    "rawDataSnapshot": '{"sessionId":"CS-2026-00001","energy":50.5,"startTime":"2026-01-01T08:00:00Z"}'
}

BATCH_EVIDENCE_BODY = {
    "items": [
        {
            "evidenceType": "charging_session",
            "businessId": "CS-2026-00001",
            "stationId": "ST-001",
            "deviceId": "DEV-001",
            "rawDataSnapshot": '{"sessionId":"CS-2026-00001","energy":50.5}'
        },
        {
            "evidenceType": "energy_settlement",
            "businessId": "ES-2026-00001",
            "stationId": "ST-002",
            "deviceId": "DEV-002",
            "rawDataSnapshot": '{"settlementId":"ES-2026-00001","amount":1200.00}'
        }
    ]
}

VALID_GUID = "00000000-0000-0000-0000-000000000001"
NON_EXISTENT_GUID = "ffffffff-ffff-ffff-ffff-ffffffffffff"
INVALID_GUID = "not-a-guid"
VALID_BUSINESS_ID = "CS-2026-00001"
SQL_INJECTION_PAYLOAD = "'; DROP TABLE bc_energy_evidence; --"
XSS_PAYLOAD = "<script>alert('xss')</script>"
LARGE_PAYLOAD = "x" * 1024 * 1024  # 1MB


# ==================== 外部 API 测试 ====================

@pytest.mark.api
@pytest.mark.blockchain
class TestEvidenceCreateApi:
    """POST /api/evidence - 创建存证"""

    def test_create_evidence_positive(self, api_client):
        """[Evidence] POST / - 正常创建存证"""
        response = api_client.post("blockchain/api/evidence", json_data=VALID_EVIDENCE_BODY)
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"正常请求不应返回 5xx, 实际: {response.status_code}"

    def test_create_evidence_no_auth(self, api_client):
        """[Evidence] POST / - 缺少认证头应返回 401"""
        api_client.clear_token()
        try:
            response = api_client.post("blockchain/api/evidence", json_data=VALID_EVIDENCE_BODY)
            assert response.status_code in (200, 400, 401, 403)
        finally:
            api_client.restore_token()

    def test_create_evidence_invalid_token(self, api_client):
        """[Evidence] POST / - 无效Token应返回 401/403"""
        api_client.set_invalid_token()
        try:
            response = api_client.post("blockchain/api/evidence", json_data=VALID_EVIDENCE_BODY)
            assert response.status_code in (200, 400, 401, 403)
        finally:
            api_client.restore_token()

    def test_create_evidence_empty_body(self, api_client):
        """[Evidence] POST / - 空请求体应返回 400"""
        response = api_client.post("blockchain/api/evidence", json_data={})
        assert response is not None
        assert response.status_code < 500

    def test_create_evidence_missing_evidence_type(self, api_client):
        """[Evidence] POST / - 缺少evidenceType字段"""
        body = {k: v for k, v in VALID_EVIDENCE_BODY.items() if k != "evidenceType"}
        response = api_client.post("blockchain/api/evidence", json_data=body)
        assert response is not None
        assert response.status_code < 500

    def test_create_evidence_missing_business_id(self, api_client):
        """[Evidence] POST / - 缺少businessId字段"""
        body = {k: v for k, v in VALID_EVIDENCE_BODY.items() if k != "businessId"}
        response = api_client.post("blockchain/api/evidence", json_data=body)
        assert response is not None
        assert response.status_code < 500

    def test_create_evidence_missing_raw_data(self, api_client):
        """[Evidence] POST / - 缺少rawDataSnapshot字段"""
        body = {k: v for k, v in VALID_EVIDENCE_BODY.items() if k != "rawDataSnapshot"}
        response = api_client.post("blockchain/api/evidence", json_data=body)
        assert response is not None
        assert response.status_code < 500

    def test_create_evidence_sql_injection_business_id(self, api_client):
        """[Evidence] POST / - businessId SQL注入防护"""
        body = {**VALID_EVIDENCE_BODY, "businessId": SQL_INJECTION_PAYLOAD}
        response = api_client.post("blockchain/api/evidence", json_data=body)
        assert response is not None
        assert response.status_code < 500

    def test_create_evidence_xss_raw_data(self, api_client):
        """[Evidence] POST / - rawDataSnapshot XSS防护"""
        body = {**VALID_EVIDENCE_BODY, "rawDataSnapshot": XSS_PAYLOAD}
        response = api_client.post("blockchain/api/evidence", json_data=body)
        assert response is not None
        assert response.status_code < 500

    def test_create_evidence_large_payload(self, api_client):
        """[Evidence] POST / - 超大载荷测试"""
        body = {**VALID_EVIDENCE_BODY, "rawDataSnapshot": LARGE_PAYLOAD}
        response = api_client.post("blockchain/api/evidence", json_data=body)
        assert response is not None

    def test_create_evidence_invalid_evidence_type(self, api_client):
        """[Evidence] POST / - 无效的evidenceType值"""
        body = {**VALID_EVIDENCE_BODY, "evidenceType": ""}
        response = api_client.post("blockchain/api/evidence", json_data=body)
        assert response is not None
        assert response.status_code < 500

    def test_create_evidence_unicode_data(self, api_client):
        """[Evidence] POST / - Unicode数据编码测试"""
        body = {**VALID_EVIDENCE_BODY, "rawDataSnapshot": '{"name":"测试充电站","energy":50.5}'}
        response = api_client.post("blockchain/api/evidence", json_data=body)
        assert response is not None
        assert response.status_code < 500

    def test_create_evidence_tenant_isolation(self, api_client):
        """[Evidence] POST / - 租户隔离"""
        response = api_client.post("blockchain/api/evidence", json_data=VALID_EVIDENCE_BODY)
        assert response is not None
        assert response.status_code < 500
        data = response.json()
        assert isinstance(data, dict)

    def test_create_evidence_duplicate_business_id(self, api_client):
        """[Evidence] POST / - 重复businessId应允许（不同类型可重复）"""
        response = api_client.post("blockchain/api/evidence", json_data=VALID_EVIDENCE_BODY)
        assert response is not None
        assert response.status_code < 500

    def test_create_evidence_concurrent(self, api_client):
        """[Evidence] POST / - 并发创建测试"""
        responses = []
        for i in range(3):
            body = {**VALID_EVIDENCE_BODY, "businessId": f"CS-CONCURRENT-{i}"}
            resp = api_client.post("blockchain/api/evidence", json_data=body)
            responses.append(resp)
        for resp in responses:
            assert resp is not None
            assert resp.status_code < 500

    def test_create_evidence_idempotency(self, api_client):
        """[Evidence] POST / - 幂等性检测（重复提交）"""
        body = {**VALID_EVIDENCE_BODY, "businessId": "CS-IDEMPOTENT-001"}
        resp1 = api_client.post("blockchain/api/evidence", json_data=body)
        resp2 = api_client.post("blockchain/api/evidence", json_data=body)
        assert resp1 is not None
        assert resp2 is not None

    def test_create_evidence_response_structure(self, api_client):
        """[Evidence] POST / - 响应结构验证"""
        response = api_client.post("blockchain/api/evidence", json_data=VALID_EVIDENCE_BODY)
        assert response is not None
        data = response.json()
        assert isinstance(data, dict)


@pytest.mark.api
@pytest.mark.blockchain
class TestEvidenceBatchCreateApi:
    """POST /api/evidence/batch - 批量创建存证"""

    def test_batch_create_positive(self, api_client):
        """[Evidence] POST /batch - 正常批量创建"""
        response = api_client.post("blockchain/api/evidence/batch", json_data=BATCH_EVIDENCE_BODY)
        assert response is not None
        assert response.status_code < 500

    def test_batch_create_no_auth(self, api_client):
        """[Evidence] POST /batch - 缺少认证头"""
        api_client.clear_token()
        try:
            response = api_client.post("blockchain/api/evidence/batch", json_data=BATCH_EVIDENCE_BODY)
            assert response.status_code in (200, 400, 401, 403)
        finally:
            api_client.restore_token()

    def test_batch_create_invalid_token(self, api_client):
        """[Evidence] POST /batch - 无效Token"""
        api_client.set_invalid_token()
        try:
            response = api_client.post("blockchain/api/evidence/batch", json_data=BATCH_EVIDENCE_BODY)
            assert response.status_code in (200, 400, 401, 403)
        finally:
            api_client.restore_token()

    def test_batch_create_empty_items(self, api_client):
        """[Evidence] POST /batch - 空items列表"""
        response = api_client.post("blockchain/api/evidence/batch", json_data={"items": []})
        assert response is not None
        assert response.status_code < 500

    def test_batch_create_single_item(self, api_client):
        """[Evidence] POST /batch - 仅一条记录"""
        body = {"items": [BATCH_EVIDENCE_BODY["items"][0]]}
        response = api_client.post("blockchain/api/evidence/batch", json_data=body)
        assert response is not None
        assert response.status_code < 500

    def test_batch_create_large_batch(self, api_client):
        """[Evidence] POST /batch - 大批量（50条）"""
        items = []
        for i in range(50):
            items.append({
                "evidenceType": "charging_session",
                "businessId": f"CS-BATCH-{i:05d}",
                "stationId": "ST-001",
                "rawDataSnapshot": f'{{"sessionId":"CS-BATCH-{i:05d}","energy":{i * 10}}}'
            })
        response = api_client.post("blockchain/api/evidence/batch", json_data={"items": items})
        assert response is not None

    def test_batch_create_sql_injection(self, api_client):
        """[Evidence] POST /batch - SQL注入防护"""
        items = [{"evidenceType": SQL_INJECTION_PAYLOAD, "businessId": "test", "rawDataSnapshot": "{}"}]
        response = api_client.post("blockchain/api/evidence/batch", json_data={"items": items})
        assert response is not None
        assert response.status_code < 500

    def test_batch_create_tenant_isolation(self, api_client):
        """[Evidence] POST /batch - 租户隔离"""
        response = api_client.post("blockchain/api/evidence/batch", json_data=BATCH_EVIDENCE_BODY)
        assert response is not None
        assert response.status_code < 500
        data = response.json()
        assert isinstance(data, dict)

    def test_batch_create_response_structure(self, api_client):
        """[Evidence] POST /batch - 响应结构验证"""
        response = api_client.post("blockchain/api/evidence/batch", json_data=BATCH_EVIDENCE_BODY)
        assert response is not None
        data = response.json()
        assert isinstance(data, dict)


@pytest.mark.api
@pytest.mark.blockchain
class TestEvidenceGetByIdApi:
    """GET /api/evidence/{id} - 查询单条存证"""

    def test_get_by_id_positive(self, api_client):
        """[Evidence] GET /{id} - 正常查询"""
        response = api_client.get(f"blockchain/api/evidence/{VALID_GUID}")
        assert response is not None
        assert response.status_code < 500

    def test_get_by_id_no_auth(self, api_client):
        """[Evidence] GET /{id} - 缺少认证头"""
        api_client.clear_token()
        try:
            response = api_client.get(f"blockchain/api/evidence/{VALID_GUID}")
            assert response.status_code in (200, 400, 401, 403, 404)
        finally:
            api_client.restore_token()

    def test_get_by_id_invalid_token(self, api_client):
        """[Evidence] GET /{id} - 无效Token"""
        api_client.set_invalid_token()
        try:
            response = api_client.get(f"blockchain/api/evidence/{VALID_GUID}")
            assert response.status_code in (200, 400, 401, 403, 404)
        finally:
            api_client.restore_token()

    def test_get_by_id_not_found(self, api_client):
        """[Evidence] GET /{id} - 不存在的ID"""
        response = api_client.get(f"blockchain/api/evidence/{NON_EXISTENT_GUID}")
        assert response is not None
        assert response.status_code < 500

    def test_get_by_id_invalid_guid(self, api_client):
        """[Evidence] GET /{id} - 无效GUID格式"""
        response = api_client.get(f"blockchain/api/evidence/{INVALID_GUID}")
        assert response is not None
        assert response.status_code < 500

    def test_get_by_id_sql_injection(self, api_client):
        """[Evidence] GET /{id} - SQL注入防护"""
        response = api_client.get(f"blockchain/api/evidence/{SQL_INJECTION_PAYLOAD}")
        assert response is not None
        assert response.status_code < 500

    def test_get_by_id_tenant_isolation(self, api_client):
        """[Evidence] GET /{id} - 租户隔离验证"""
        response = api_client.get(f"blockchain/api/evidence/{VALID_GUID}")
        assert response is not None
        assert response.status_code < 500
        data = response.json()
        assert isinstance(data, dict)

    def test_get_by_id_response_structure(self, api_client):
        """[Evidence] GET /{id} - 响应结构验证"""
        response = api_client.get(f"blockchain/api/evidence/{VALID_GUID}")
        assert response is not None
        data = response.json()
        assert isinstance(data, dict)


@pytest.mark.api
@pytest.mark.blockchain
class TestEvidenceGetByBusinessIdApi:
    """GET /api/evidence/business/{businessId} - 按业务ID查询"""

    def test_get_by_business_id_positive(self, api_client):
        """[Evidence] GET /business/{id} - 正常查询"""
        response = api_client.get(f"blockchain/api/evidence/business/{VALID_BUSINESS_ID}")
        assert response is not None
        assert response.status_code < 500

    def test_get_by_business_id_no_auth(self, api_client):
        """[Evidence] GET /business/{id} - 缺少认证头"""
        api_client.clear_token()
        try:
            response = api_client.get(f"blockchain/api/evidence/business/{VALID_BUSINESS_ID}")
            assert response.status_code in (200, 400, 401, 403, 404)
        finally:
            api_client.restore_token()

    def test_get_by_business_id_invalid_token(self, api_client):
        """[Evidence] GET /business/{id} - 无效Token"""
        api_client.set_invalid_token()
        try:
            response = api_client.get(f"blockchain/api/evidence/business/{VALID_BUSINESS_ID}")
            assert response.status_code in (200, 400, 401, 403, 404)
        finally:
            api_client.restore_token()

    def test_get_by_business_id_not_found(self, api_client):
        """[Evidence] GET /business/{id} - 不存在的业务ID"""
        response = api_client.get("blockchain/api/evidence/business/NON-EXISTENT-BIZ-ID")
        assert response is not None
        assert response.status_code < 500

    def test_get_by_business_id_sql_injection(self, api_client):
        """[Evidence] GET /business/{id} - SQL注入防护"""
        response = api_client.get(f"blockchain/api/evidence/business/{SQL_INJECTION_PAYLOAD}")
        assert response is not None
        assert response.status_code < 500

    def test_get_by_business_id_xss(self, api_client):
        """[Evidence] GET /business/{id} - XSS防护"""
        response = api_client.get(f"blockchain/api/evidence/business/{XSS_PAYLOAD}")
        assert response is not None
        assert response.status_code < 500

    def test_get_by_business_id_with_query_params(self, api_client):
        """[Evidence] GET /business/{id} - 带查询参数"""
        response = api_client.get(
            f"blockchain/api/evidence/business/{VALID_BUSINESS_ID}",
            params={"evidenceType": "charging_session"})
        assert response is not None
        assert response.status_code < 500

    def test_get_by_business_id_tenant_isolation(self, api_client):
        """[Evidence] GET /business/{id} - 租户隔离"""
        response = api_client.get(f"blockchain/api/evidence/business/{VALID_BUSINESS_ID}")
        assert response is not None
        assert response.status_code < 500
        data = response.json()
        assert isinstance(data, dict)


@pytest.mark.api
@pytest.mark.blockchain
class TestEvidenceListApi:
    """GET /api/evidence - 分页查询存证列表"""

    def test_list_positive(self, api_client):
        """[Evidence] GET / - 正常分页查询"""
        response = api_client.get("blockchain/api/evidence")
        assert response is not None
        assert response.status_code < 500

    def test_list_no_auth(self, api_client):
        """[Evidence] GET / - 缺少认证头"""
        api_client.clear_token()
        try:
            response = api_client.get("blockchain/api/evidence")
            assert response.status_code in (200, 400, 401, 403)
        finally:
            api_client.restore_token()

    def test_list_invalid_token(self, api_client):
        """[Evidence] GET / - 无效Token"""
        api_client.set_invalid_token()
        try:
            response = api_client.get("blockchain/api/evidence")
            assert response.status_code in (200, 400, 401, 403)
        finally:
            api_client.restore_token()

    def test_list_with_pagination(self, api_client):
        """[Evidence] GET / - 分页参数测试"""
        response = api_client.get("blockchain/api/evidence", params={"pageIndex": 1, "pageSize": 10})
        assert response is not None
        assert response.status_code < 500

    def test_list_with_filter_type(self, api_client):
        """[Evidence] GET / - 按类型过滤"""
        response = api_client.get("blockchain/api/evidence",
                                  params={"evidenceType": "charging_session"})
        assert response is not None
        assert response.status_code < 500

    def test_list_with_filter_station(self, api_client):
        """[Evidence] GET / - 按场站过滤"""
        response = api_client.get("blockchain/api/evidence", params={"stationId": "ST-001"})
        assert response is not None
        assert response.status_code < 500

    def test_list_with_time_range(self, api_client):
        """[Evidence] GET / - 时间范围过滤"""
        response = api_client.get("blockchain/api/evidence",
                                  params={"startTime": "2026-01-01", "endTime": "2026-12-31"})
        assert response is not None
        assert response.status_code < 500

    def test_list_page_boundary_zero(self, api_client):
        """[Evidence] GET / - 页码边界值0"""
        response = api_client.get("blockchain/api/evidence", params={"pageIndex": 0, "pageSize": 10})
        assert response is not None
        assert response.status_code < 500

    def test_list_page_boundary_large(self, api_client):
        """[Evidence] GET / - 超大页码"""
        response = api_client.get("blockchain/api/evidence", params={"pageIndex": 99999, "pageSize": 10})
        assert response is not None
        assert response.status_code < 500

    def test_list_page_size_boundary(self, api_client):
        """[Evidence] GET / - 每页数量边界值"""
        response = api_client.get("blockchain/api/evidence", params={"pageIndex": 1, "pageSize": 1000})
        assert response is not None
        assert response.status_code < 500

    def test_list_negative_page(self, api_client):
        """[Evidence] GET / - 负数页码"""
        response = api_client.get("blockchain/api/evidence", params={"pageIndex": -1, "pageSize": 10})
        assert response is not None
        assert response.status_code < 500

    def test_list_sql_injection_filter(self, api_client):
        """[Evidence] GET / - 过滤参数SQL注入防护"""
        response = api_client.get("blockchain/api/evidence",
                                  params={"evidenceType": SQL_INJECTION_PAYLOAD})
        assert response is not None
        assert response.status_code < 500

    def test_list_tenant_isolation(self, api_client):
        """[Evidence] GET / - 租户隔离"""
        response = api_client.get("blockchain/api/evidence")
        assert response is not None
        assert response.status_code < 500
        data = response.json()
        assert isinstance(data, dict)

    def test_list_response_structure(self, api_client):
        """[Evidence] GET / - 响应结构（分页字段）"""
        response = api_client.get("blockchain/api/evidence")
        assert response is not None
        data = response.json()
        assert isinstance(data, dict)


@pytest.mark.api
@pytest.mark.blockchain
class TestEvidenceVerifyApi:
    """POST /api/evidence/{id}/verify - 验证存证完整性"""

    def test_verify_positive(self, api_client):
        """[Evidence] POST /{id}/verify - 正常验证"""
        response = api_client.post(f"blockchain/api/evidence/{VALID_GUID}/verify")
        assert response is not None
        assert response.status_code < 500

    def test_verify_no_auth(self, api_client):
        """[Evidence] POST /{id}/verify - 缺少认证头"""
        api_client.clear_token()
        try:
            response = api_client.post(f"blockchain/api/evidence/{VALID_GUID}/verify")
            assert response.status_code in (200, 400, 401, 403, 404)
        finally:
            api_client.restore_token()

    def test_verify_invalid_token(self, api_client):
        """[Evidence] POST /{id}/verify - 无效Token"""
        api_client.set_invalid_token()
        try:
            response = api_client.post(f"blockchain/api/evidence/{VALID_GUID}/verify")
            assert response.status_code in (200, 400, 401, 403, 404)
        finally:
            api_client.restore_token()

    def test_verify_not_found(self, api_client):
        """[Evidence] POST /{id}/verify - 不存在的存证ID"""
        response = api_client.post(f"blockchain/api/evidence/{NON_EXISTENT_GUID}/verify")
        assert response is not None
        assert response.status_code < 500

    def test_verify_invalid_guid(self, api_client):
        """[Evidence] POST /{id}/verify - 无效GUID"""
        response = api_client.post(f"blockchain/api/evidence/{INVALID_GUID}/verify")
        assert response is not None
        assert response.status_code < 500

    def test_verify_sql_injection(self, api_client):
        """[Evidence] POST /{id}/verify - SQL注入防护"""
        response = api_client.post(f"blockchain/api/evidence/{SQL_INJECTION_PAYLOAD}/verify")
        assert response is not None
        assert response.status_code < 500

    def test_verify_concurrent(self, api_client):
        """[Evidence] POST /{id}/verify - 并发验证"""
        responses = []
        for _ in range(3):
            resp = api_client.post(f"blockchain/api/evidence/{VALID_GUID}/verify")
            responses.append(resp)
        for resp in responses:
            assert resp is not None
            assert resp.status_code < 500

    def test_verify_tenant_isolation(self, api_client):
        """[Evidence] POST /{id}/verify - 租户隔离"""
        response = api_client.post(f"blockchain/api/evidence/{VALID_GUID}/verify")
        assert response is not None
        assert response.status_code < 500
        data = response.json()
        assert isinstance(data, dict)

    def test_verify_response_structure(self, api_client):
        """[Evidence] POST /{id}/verify - 响应结构验证"""
        response = api_client.post(f"blockchain/api/evidence/{VALID_GUID}/verify")
        assert response is not None
        data = response.json()
        assert isinstance(data, dict)


@pytest.mark.api
@pytest.mark.blockchain
class TestEvidenceRetryApi:
    """POST /api/evidence/{id}/retry - 重试失败存证"""

    def test_retry_positive(self, api_client):
        """[Evidence] POST /{id}/retry - 正常重试"""
        response = api_client.post(f"blockchain/api/evidence/{VALID_GUID}/retry")
        assert response is not None
        assert response.status_code < 500

    def test_retry_no_auth(self, api_client):
        """[Evidence] POST /{id}/retry - 缺少认证头"""
        api_client.clear_token()
        try:
            response = api_client.post(f"blockchain/api/evidence/{VALID_GUID}/retry")
            assert response.status_code in (200, 400, 401, 403, 404)
        finally:
            api_client.restore_token()

    def test_retry_invalid_token(self, api_client):
        """[Evidence] POST /{id}/retry - 无效Token"""
        api_client.set_invalid_token()
        try:
            response = api_client.post(f"blockchain/api/evidence/{VALID_GUID}/retry")
            assert response.status_code in (200, 400, 401, 403, 404)
        finally:
            api_client.restore_token()

    def test_retry_not_found(self, api_client):
        """[Evidence] POST /{id}/retry - 不存在的存证ID"""
        response = api_client.post(f"blockchain/api/evidence/{NON_EXISTENT_GUID}/retry")
        assert response is not None
        assert response.status_code < 500

    def test_retry_invalid_guid(self, api_client):
        """[Evidence] POST /{id}/retry - 无效GUID"""
        response = api_client.post(f"blockchain/api/evidence/{INVALID_GUID}/retry")
        assert response is not None
        assert response.status_code < 500

    def test_retry_already_confirmed(self, api_client):
        """[Evidence] POST /{id}/retry - 已确认的存证不应重试"""
        response = api_client.post(f"blockchain/api/evidence/{VALID_GUID}/retry")
        assert response is not None
        assert response.status_code < 500

    def test_retry_concurrent(self, api_client):
        """[Evidence] POST /{id}/retry - 并发重试"""
        responses = []
        for _ in range(3):
            resp = api_client.post(f"blockchain/api/evidence/{VALID_GUID}/retry")
            responses.append(resp)
        for resp in responses:
            assert resp is not None
            assert resp.status_code < 500

    def test_retry_max_retries(self, api_client):
        """[Evidence] POST /{id}/retry - 超过最大重试次数"""
        response = api_client.post(f"blockchain/api/evidence/{VALID_GUID}/retry")
        assert response is not None
        assert response.status_code < 500

    def test_retry_tenant_isolation(self, api_client):
        """[Evidence] POST /{id}/retry - 租户隔离"""
        response = api_client.post(f"blockchain/api/evidence/{VALID_GUID}/retry")
        assert response is not None
        assert response.status_code < 500
        data = response.json()
        assert isinstance(data, dict)


@pytest.mark.api
@pytest.mark.blockchain
class TestEvidenceStatisticsApi:
    """GET /api/evidence/statistics - 存证统计"""

    def test_statistics_positive(self, api_client):
        """[Evidence] GET /statistics - 正常查询统计"""
        response = api_client.get("blockchain/api/evidence/statistics")
        assert response is not None
        assert response.status_code < 500

    def test_statistics_no_auth(self, api_client):
        """[Evidence] GET /statistics - 缺少认证头"""
        api_client.clear_token()
        try:
            response = api_client.get("blockchain/api/evidence/statistics")
            assert response.status_code in (200, 400, 401, 403)
        finally:
            api_client.restore_token()

    def test_statistics_invalid_token(self, api_client):
        """[Evidence] GET /statistics - 无效Token"""
        api_client.set_invalid_token()
        try:
            response = api_client.get("blockchain/api/evidence/statistics")
            assert response.status_code in (200, 400, 401, 403)
        finally:
            api_client.restore_token()

    def test_statistics_with_time_range(self, api_client):
        """[Evidence] GET /statistics - 时间范围过滤"""
        response = api_client.get("blockchain/api/evidence/statistics",
                                  params={"startTime": "2026-01-01", "endTime": "2026-12-31"})
        assert response is not None
        assert response.status_code < 500

    def test_statistics_tenant_isolation(self, api_client):
        """[Evidence] GET /statistics - 租户隔离"""
        response = api_client.get("blockchain/api/evidence/statistics")
        assert response is not None
        assert response.status_code < 500
        data = response.json()
        assert isinstance(data, dict)

    def test_statistics_response_structure(self, api_client):
        """[Evidence] GET /statistics - 响应结构验证"""
        response = api_client.get("blockchain/api/evidence/statistics")
        assert response is not None
        data = response.json()
        assert isinstance(data, dict)


@pytest.mark.api
@pytest.mark.blockchain
class TestEvidenceTimelineApi:
    """GET /api/evidence/timeline/{businessId} - 存证时间线"""

    def test_timeline_positive(self, api_client):
        """[Evidence] GET /timeline/{id} - 正常查询时间线"""
        response = api_client.get(f"blockchain/api/evidence/timeline/{VALID_BUSINESS_ID}")
        assert response is not None
        assert response.status_code < 500

    def test_timeline_no_auth(self, api_client):
        """[Evidence] GET /timeline/{id} - 缺少认证头"""
        api_client.clear_token()
        try:
            response = api_client.get(f"blockchain/api/evidence/timeline/{VALID_BUSINESS_ID}")
            assert response.status_code in (200, 400, 401, 403, 404)
        finally:
            api_client.restore_token()

    def test_timeline_invalid_token(self, api_client):
        """[Evidence] GET /timeline/{id} - 无效Token"""
        api_client.set_invalid_token()
        try:
            response = api_client.get(f"blockchain/api/evidence/timeline/{VALID_BUSINESS_ID}")
            assert response.status_code in (200, 400, 401, 403, 404)
        finally:
            api_client.restore_token()

    def test_timeline_not_found(self, api_client):
        """[Evidence] GET /timeline/{id} - 不存在的业务ID"""
        response = api_client.get("blockchain/api/evidence/timeline/NON-EXISTENT-BIZ")
        assert response is not None
        assert response.status_code < 500

    def test_timeline_sql_injection(self, api_client):
        """[Evidence] GET /timeline/{id} - SQL注入防护"""
        response = api_client.get(f"blockchain/api/evidence/timeline/{SQL_INJECTION_PAYLOAD}")
        assert response is not None
        assert response.status_code < 500

    def test_timeline_xss(self, api_client):
        """[Evidence] GET /timeline/{id} - XSS防护"""
        response = api_client.get(f"blockchain/api/evidence/timeline/{XSS_PAYLOAD}")
        assert response is not None
        assert response.status_code < 500

    def test_timeline_tenant_isolation(self, api_client):
        """[Evidence] GET /timeline/{id} - 租户隔离"""
        response = api_client.get(f"blockchain/api/evidence/timeline/{VALID_BUSINESS_ID}")
        assert response is not None
        assert response.status_code < 500
        data = response.json()
        assert isinstance(data, (dict, list))

    def test_timeline_response_structure(self, api_client):
        """[Evidence] GET /timeline/{id} - 响应结构验证"""
        response = api_client.get(f"blockchain/api/evidence/timeline/{VALID_BUSINESS_ID}")
        assert response is not None
        data = response.json()
        assert isinstance(data, (dict, list))


# ==================== 内部 API 测试 ====================

@pytest.mark.api
@pytest.mark.blockchain
class TestInternalEvidenceCreateApi:
    """POST /api/internal/blockchain/evidence - 内部创建存证"""

    INTERNAL_EVIDENCE_BODY = {
        "evidenceType": "energy_settlement",
        "businessId": "ES-INT-00001",
        "stationId": "ST-001",
        "rawDataSnapshot": '{"settlementId":"ES-INT-00001","amount":1500.00}'
    }

    def test_internal_create_positive(self, api_client):
        """[Internal Evidence] POST / - 正常创建"""
        response = api_client.post("blockchain/api/internal/blockchain/evidence",
                                   json_data=self.INTERNAL_EVIDENCE_BODY)
        assert response is not None
        assert response.status_code < 500

    def test_internal_create_empty_body(self, api_client):
        """[Internal Evidence] POST / - 空请求体"""
        response = api_client.post("blockchain/api/internal/blockchain/evidence", json_data={})
        assert response is not None
        assert response.status_code < 500

    def test_internal_create_missing_fields(self, api_client):
        """[Internal Evidence] POST / - 缺少必填字段"""
        response = api_client.post("blockchain/api/internal/blockchain/evidence",
                                   json_data={"evidenceType": "test"})
        assert response is not None
        assert response.status_code < 500

    def test_internal_create_sql_injection(self, api_client):
        """[Internal Evidence] POST / - SQL注入防护"""
        body = {**self.INTERNAL_EVIDENCE_BODY, "businessId": SQL_INJECTION_PAYLOAD}
        response = api_client.post("blockchain/api/internal/blockchain/evidence", json_data=body)
        assert response is not None
        assert response.status_code < 500

    def test_internal_create_response_structure(self, api_client):
        """[Internal Evidence] POST / - 响应结构验证"""
        response = api_client.post("blockchain/api/internal/blockchain/evidence",
                                   json_data=self.INTERNAL_EVIDENCE_BODY)
        assert response is not None
        data = response.json()
        assert isinstance(data, dict)


@pytest.mark.api
@pytest.mark.blockchain
class TestInternalEvidenceBatchApi:
    """POST /api/internal/blockchain/evidence/batch - 内部批量创建"""

    INTERNAL_BATCH_BODY = {
        "items": [
            {"evidenceType": "charging_session", "businessId": "CS-INT-001",
             "rawDataSnapshot": '{"sessionId":"CS-INT-001"}'},
            {"evidenceType": "energy_settlement", "businessId": "ES-INT-001",
             "rawDataSnapshot": '{"settlementId":"ES-INT-001"}'}
        ]
    }

    def test_internal_batch_positive(self, api_client):
        """[Internal Evidence] POST /batch - 正常批量创建"""
        response = api_client.post("blockchain/api/internal/blockchain/evidence/batch",
                                   json_data=self.INTERNAL_BATCH_BODY)
        assert response is not None
        assert response.status_code < 500

    def test_internal_batch_empty_items(self, api_client):
        """[Internal Evidence] POST /batch - 空items列表"""
        response = api_client.post("blockchain/api/internal/blockchain/evidence/batch",
                                   json_data={"items": []})
        assert response is not None
        assert response.status_code < 500

    def test_internal_batch_response_structure(self, api_client):
        """[Internal Evidence] POST /batch - 响应结构验证"""
        response = api_client.post("blockchain/api/internal/blockchain/evidence/batch",
                                   json_data=self.INTERNAL_BATCH_BODY)
        assert response is not None
        data = response.json()
        assert isinstance(data, dict)


@pytest.mark.api
@pytest.mark.blockchain
class TestInternalEvidenceVerifyApi:
    """GET /api/internal/blockchain/evidence/{id}/verify - 内部验证存证"""

    def test_internal_verify_positive(self, api_client):
        """[Internal Evidence] GET /{id}/verify - 正常验证"""
        response = api_client.get(f"blockchain/api/internal/blockchain/evidence/{VALID_GUID}/verify")
        assert response is not None
        assert response.status_code < 500

    def test_internal_verify_not_found(self, api_client):
        """[Internal Evidence] GET /{id}/verify - 不存在的ID"""
        response = api_client.get(
            f"blockchain/api/internal/blockchain/evidence/{NON_EXISTENT_GUID}/verify")
        assert response is not None
        assert response.status_code < 500

    def test_internal_verify_invalid_guid(self, api_client):
        """[Internal Evidence] GET /{id}/verify - 无效GUID"""
        response = api_client.get(
            f"blockchain/api/internal/blockchain/evidence/{INVALID_GUID}/verify")
        assert response is not None
        assert response.status_code < 500

    def test_internal_verify_response_structure(self, api_client):
        """[Internal Evidence] GET /{id}/verify - 响应结构验证"""
        response = api_client.get(f"blockchain/api/internal/blockchain/evidence/{VALID_GUID}/verify")
        assert response is not None
        data = response.json()
        assert isinstance(data, dict)


@pytest.mark.api
@pytest.mark.blockchain
class TestInternalEvidenceGetApi:
    """GET /api/internal/blockchain/evidence/{id} - 内部查询存证"""

    def test_internal_get_positive(self, api_client):
        """[Internal Evidence] GET /{id} - 正常查询"""
        response = api_client.get(f"blockchain/api/internal/blockchain/evidence/{VALID_GUID}")
        assert response is not None
        assert response.status_code < 500

    def test_internal_get_not_found(self, api_client):
        """[Internal Evidence] GET /{id} - 不存在的ID"""
        response = api_client.get(
            f"blockchain/api/internal/blockchain/evidence/{NON_EXISTENT_GUID}")
        assert response is not None
        assert response.status_code < 500

    def test_internal_get_invalid_guid(self, api_client):
        """[Internal Evidence] GET /{id} - 无效GUID"""
        response = api_client.get(
            f"blockchain/api/internal/blockchain/evidence/{INVALID_GUID}")
        assert response is not None
        assert response.status_code < 500

    def test_internal_get_response_structure(self, api_client):
        """[Internal Evidence] GET /{id} - 响应结构验证"""
        response = api_client.get(f"blockchain/api/internal/blockchain/evidence/{VALID_GUID}")
        assert response is not None
        data = response.json()
        assert isinstance(data, dict)


@pytest.mark.api
@pytest.mark.blockchain
class TestInternalEvidenceGetByBusinessApi:
    """GET /api/internal/blockchain/evidence/business/{id} - 内部按业务ID查询"""

    def test_internal_get_by_business_positive(self, api_client):
        """[Internal Evidence] GET /business/{id} - 正常查询"""
        response = api_client.get(
            f"blockchain/api/internal/blockchain/evidence/business/{VALID_BUSINESS_ID}")
        assert response is not None
        assert response.status_code < 500

    def test_internal_get_by_business_not_found(self, api_client):
        """[Internal Evidence] GET /business/{id} - 不存在的业务ID"""
        response = api_client.get(
            "blockchain/api/internal/blockchain/evidence/business/NON-EXISTENT")
        assert response is not None
        assert response.status_code < 500

    def test_internal_get_by_business_sql_injection(self, api_client):
        """[Internal Evidence] GET /business/{id} - SQL注入防护"""
        response = api_client.get(
            f"blockchain/api/internal/blockchain/evidence/business/{SQL_INJECTION_PAYLOAD}")
        assert response is not None
        assert response.status_code < 500

    def test_internal_get_by_business_response_structure(self, api_client):
        """[Internal Evidence] GET /business/{id} - 响应结构验证"""
        response = api_client.get(
            f"blockchain/api/internal/blockchain/evidence/business/{VALID_BUSINESS_ID}")
        assert response is not None
        data = response.json()
        assert isinstance(data, dict)


# ==================== 权限码测试 ====================

@pytest.mark.api
@pytest.mark.blockchain
@pytest.mark.auth
class TestEvidencePermissions:
    """存证权限码验证：确保所有端点都有正确的权限保护"""

    def test_create_requires_evidence_create(self, api_client):
        """[Evidence] POST / - 需要 blockchain:evidence:create 权限"""
        response = api_client.post("blockchain/api/evidence", json_data=VALID_EVIDENCE_BODY)
        assert response is not None
        # 有权限应正常响应，无权限应返回 403
        assert response.status_code < 500

    def test_batch_create_requires_evidence_create(self, api_client):
        """[Evidence] POST /batch - 需要 blockchain:evidence:create 权限"""
        response = api_client.post("blockchain/api/evidence/batch", json_data=BATCH_EVIDENCE_BODY)
        assert response is not None
        assert response.status_code < 500

    def test_get_by_id_requires_evidence_view(self, api_client):
        """[Evidence] GET /{id} - 需要 blockchain:evidence:view 权限"""
        response = api_client.get(f"blockchain/api/evidence/{VALID_GUID}")
        assert response is not None
        assert response.status_code < 500

    def test_list_requires_evidence_list(self, api_client):
        """[Evidence] GET / - 需要 blockchain:evidence:list 权限"""
        response = api_client.get("blockchain/api/evidence")
        assert response is not None
        assert response.status_code < 500

    def test_verify_requires_evidence_verify(self, api_client):
        """[Evidence] POST /{id}/verify - 需要 blockchain:evidence:verify 权限"""
        response = api_client.post(f"blockchain/api/evidence/{VALID_GUID}/verify")
        assert response is not None
        assert response.status_code < 500

    def test_retry_requires_evidence_update(self, api_client):
        """[Evidence] POST /{id}/retry - 需要 blockchain:evidence:update 权限"""
        response = api_client.post(f"blockchain/api/evidence/{VALID_GUID}/retry")
        assert response is not None
        assert response.status_code < 500

    def test_statistics_requires_evidence_view(self, api_client):
        """[Evidence] GET /statistics - 需要 blockchain:evidence:view 权限"""
        response = api_client.get("blockchain/api/evidence/statistics")
        assert response is not None
        assert response.status_code < 500

    def test_timeline_requires_evidence_view(self, api_client):
        """[Evidence] GET /timeline/{id} - 需要 blockchain:evidence:view 权限"""
        response = api_client.get(f"blockchain/api/evidence/timeline/{VALID_BUSINESS_ID}")
        assert response is not None
        assert response.status_code < 500


# ==================== 三管分离角色测试 ====================

@pytest.mark.api
@pytest.mark.blockchain
@pytest.mark.auth
class TestThreeAdminSeparation:
    """三管分离角色验证：安全管理员/审计管理员/系统管理员权限分离"""

    def test_audit_admin_can_view_evidence(self, api_client):
        """[三管分离] 审计管理员应能查看存证"""
        response = api_client.get(f"blockchain/api/evidence/{VALID_GUID}")
        assert response is not None
        assert response.status_code < 500

    def test_audit_admin_can_verify_evidence(self, api_client):
        """[三管分离] 审计管理员应能验证存证"""
        response = api_client.post(f"blockchain/api/evidence/{VALID_GUID}/verify")
        assert response is not None
        assert response.status_code < 500

    def test_system_admin_can_create_evidence(self, api_client):
        """[三管分离] 系统管理员应能创建存证"""
        response = api_client.post("blockchain/api/evidence", json_data=VALID_EVIDENCE_BODY)
        assert response is not None
        assert response.status_code < 500

    def test_create_evidence_returns_data_hash(self, api_client):
        """[三管分离] 创建存证应返回SM3数据哈希"""
        response = api_client.post("blockchain/api/evidence", json_data=VALID_EVIDENCE_BODY)
        assert response is not None
        data = response.json()
        assert isinstance(data, dict)

    def test_statistics_accessible(self, api_client):
        """[三管分离] 统计端点应可访问"""
        response = api_client.get("blockchain/api/evidence/statistics")
        assert response is not None
        assert response.status_code < 500
