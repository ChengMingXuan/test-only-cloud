"""
CIM 协议 API 测试
=================
覆盖 CimProtocolController 全部 9 个端点
"""
import pytest
import uuid
from tests.conftest import ApiClient

BASE = "/api/orchestrator/cim"


@pytest.fixture
def cim_model_payload():
    return {
        "modelName": f"CIM模型_{uuid.uuid4().hex[:6]}",
        "modelType": "substation",
        "version": "CIM17",
        "xmlContent": "<rdf:RDF></rdf:RDF>",
    }


@pytest.fixture
def cim_device_mapping():
    return {
        "cimId": str(uuid.uuid4()),
        "deviceId": str(uuid.uuid4()),
        "objectType": "PowerTransformer",
        "mappingRules": {"voltageLevel": "110kV"},
    }


class TestCimModelManagement:
    """CIM 模型管理"""

    def test_create_model(self, api: ApiClient, cim_model_payload):
        resp = api.post(f"{BASE}/models", json=cim_model_payload)
        assert resp.status_code == 200

    def test_list_models(self, api: ApiClient):
        resp = api.get(f"{BASE}/models", params={"page": 1, "pageSize": 10})
        assert resp.status_code == 200

    def test_get_model(self, api: ApiClient):
        model_id = str(uuid.uuid4())
        resp = api.get(f"{BASE}/models/{model_id}")
        assert resp.status_code in (200, 404)

    def test_update_model(self, api: ApiClient, cim_model_payload):
        model_id = str(uuid.uuid4())
        resp = api.put(f"{BASE}/models/{model_id}", json=cim_model_payload)
        assert resp.status_code in (200, 404)

    def test_delete_model(self, api: ApiClient):
        model_id = str(uuid.uuid4())
        resp = api.delete(f"{BASE}/models/{model_id}")
        assert resp.status_code in (200, 404)

    def test_create_model_unauthorized(self, anon_api: ApiClient, cim_model_payload):
        resp = anon_api.post(f"{BASE}/models", json=cim_model_payload)
        assert resp.status_code == 401


class TestCimDeviceMapping:
    """CIM 设备映射"""

    def test_create_mapping(self, api: ApiClient, cim_device_mapping):
        resp = api.post(f"{BASE}/device-mapping", json=cim_device_mapping)
        assert resp.status_code == 200

    def test_list_mappings(self, api: ApiClient):
        model_id = str(uuid.uuid4())
        resp = api.get(f"{BASE}/models/{model_id}/device-mappings")
        assert resp.status_code in (200, 404)

    def test_delete_mapping(self, api: ApiClient):
        mapping_id = str(uuid.uuid4())
        resp = api.delete(f"{BASE}/device-mapping/{mapping_id}")
        assert resp.status_code in (200, 404)


class TestCimTopology:
    """CIM 拓扑分析"""

    def test_get_topology(self, api: ApiClient):
        model_id = str(uuid.uuid4())
        resp = api.get(f"{BASE}/models/{model_id}/topology")
        assert resp.status_code in (200, 404)

    def test_validate_model(self, api: ApiClient):
        model_id = str(uuid.uuid4())
        resp = api.post(f"{BASE}/models/{model_id}/validate")
        assert resp.status_code in (200, 404)

    def test_export_model(self, api: ApiClient):
        model_id = str(uuid.uuid4())
        resp = api.get(f"{BASE}/models/{model_id}/export")
        assert resp.status_code in (200, 404)

    def test_import_model(self, api: ApiClient):
        resp = api.post(f"{BASE}/models/import", json={
            "format": "CIM-XML",
            "xmlContent": "<rdf:RDF></rdf:RDF>",
        })
        assert resp.status_code == 200

    def test_topology_unauthorized(self, anon_api: ApiClient):
        model_id = str(uuid.uuid4())
        resp = anon_api.get(f"{BASE}/models/{model_id}/topology")
        assert resp.status_code == 401
