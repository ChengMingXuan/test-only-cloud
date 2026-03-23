"""
自适应预测 API 测试
====================
覆盖 AdaptivePredictController 全部 3 个端点
"""
import pytest
import uuid
from tests.conftest import ApiClient

BASE = "/api/iotcloudai/adaptive"


@pytest.fixture
def predict_request():
    return {
        "deviceId": str(uuid.uuid4()),
        "modelType": "power_output",
        "inputFeatures": {
            "temperature": 25.0,
            "irradiance": 800.0,
            "windSpeed": 3.5,
            "humidity": 60.0,
        },
        "horizonMinutes": 60,
    }


@pytest.fixture
def feedback_payload():
    return {
        "predictionId": str(uuid.uuid4()),
        "actualValue": 45.6,
        "feedbackTime": "2025-06-01T12:00:00Z",
    }


class TestAdaptivePredict:
    """自适应预测"""

    def test_predict_success(self, api: ApiClient, predict_request):
        resp = api.post(f"{BASE}/predict", json=predict_request)
        assert resp.status_code == 200
        body = resp.json()
        assert body["success"] is True

    def test_predict_missing_device(self, api: ApiClient):
        resp = api.post(f"{BASE}/predict", json={"modelType": "power_output"})
        assert resp.status_code in (400, 422)

    def test_predict_unauthorized(self, anon_api: ApiClient, predict_request):
        resp = anon_api.post(f"{BASE}/predict", json=predict_request)
        assert resp.status_code == 401


class TestAdaptiveModelStatus:
    """模型状态查询"""

    def test_get_model_status(self, api: ApiClient):
        device_id = str(uuid.uuid4())
        resp = api.get(f"{BASE}/model-status/{device_id}")
        assert resp.status_code in (200, 404)

    def test_list_model_status(self, api: ApiClient):
        resp = api.get(f"{BASE}/model-status", params={"page": 1, "pageSize": 10})
        assert resp.status_code == 200

    def test_model_status_unauthorized(self, anon_api: ApiClient):
        resp = anon_api.get(f"{BASE}/model-status")
        assert resp.status_code == 401


class TestAdaptiveFeedback:
    """预测反馈"""

    def test_submit_feedback(self, api: ApiClient, feedback_payload):
        resp = api.post(f"{BASE}/feedback", json=feedback_payload)
        assert resp.status_code == 200

    def test_submit_feedback_invalid(self, api: ApiClient):
        resp = api.post(f"{BASE}/feedback", json={})
        assert resp.status_code in (400, 422)

    def test_submit_feedback_unauthorized(self, anon_api: ApiClient, feedback_payload):
        resp = anon_api.post(f"{BASE}/feedback", json=feedback_payload)
        assert resp.status_code == 401
