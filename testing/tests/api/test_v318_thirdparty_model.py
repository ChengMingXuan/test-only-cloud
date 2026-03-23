"""
第三方模型管理 API 测试
=======================
覆盖 ThirdPartyModelController 全部 4 个端点
"""
import pytest
import uuid
from tests.conftest import ApiClient

BASE = "/api/iotcloudai/third-party"


@pytest.fixture
def model_register_payload():
    return {
        "modelName": f"Model_{uuid.uuid4().hex[:6]}",
        "provider": "azure",
        "endpointUrl": "https://api.example.com/v1/predict",
        "modelType": "regression",
        "version": "v1.0",
        "inputSchema": {"type": "object", "properties": {"value": {"type": "number"}}},
        "outputSchema": {"type": "object", "properties": {"prediction": {"type": "number"}}},
    }


class TestThirdPartyModelRegistration:
    """模型注册"""

    def test_register_model(self, api: ApiClient, model_register_payload):
        resp = api.post(f"{BASE}/models", json=model_register_payload)
        assert resp.status_code == 200
        body = resp.json()
        assert body["success"] is True

    def test_register_missing_endpoint(self, api: ApiClient):
        resp = api.post(f"{BASE}/models", json={"modelName": "test"})
        assert resp.status_code in (400, 422)

    def test_register_unauthorized(self, anon_api: ApiClient, model_register_payload):
        resp = anon_api.post(f"{BASE}/models", json=model_register_payload)
        assert resp.status_code == 401

    def test_list_models(self, api: ApiClient):
        resp = api.get(f"{BASE}/models", params={"page": 1, "pageSize": 10})
        assert resp.status_code == 200


class TestThirdPartyModelDetail:
    """模型详情与更新"""

    def test_get_model(self, api: ApiClient):
        model_id = str(uuid.uuid4())
        resp = api.get(f"{BASE}/models/{model_id}")
        assert resp.status_code in (200, 404)

    def test_update_model(self, api: ApiClient, model_register_payload):
        model_id = str(uuid.uuid4())
        resp = api.put(f"{BASE}/models/{model_id}", json=model_register_payload)
        assert resp.status_code in (200, 404)

    def test_delete_model(self, api: ApiClient):
        model_id = str(uuid.uuid4())
        resp = api.delete(f"{BASE}/models/{model_id}")
        assert resp.status_code in (200, 404)


class TestThirdPartyModelTest:
    """模型测试调用"""

    def test_invoke_model(self, api: ApiClient):
        model_id = str(uuid.uuid4())
        resp = api.post(f"{BASE}/models/{model_id}/invoke", json={
            "input": {"value": 42.0},
        })
        assert resp.status_code in (200, 404)

    def test_invoke_model_unauthorized(self, anon_api: ApiClient):
        model_id = str(uuid.uuid4())
        resp = anon_api.post(f"{BASE}/models/{model_id}/invoke", json={})
        assert resp.status_code == 401

    def test_get_model_metrics(self, api: ApiClient):
        model_id = str(uuid.uuid4())
        resp = api.get(f"{BASE}/models/{model_id}/metrics")
        assert resp.status_code in (200, 404)
