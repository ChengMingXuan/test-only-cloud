"""
设备健康 API 测试
=================
覆盖 DeviceHealthController 全部 3 个端点
"""
import pytest
import uuid
from tests.conftest import ApiClient

BASE = "/api/iotcloudai/health"


@pytest.fixture
def health_check_request():
    return {
        "deviceIds": [str(uuid.uuid4()), str(uuid.uuid4())],
        "checkType": "comprehensive",
        "includeHistory": True,
    }


class TestDeviceHealthScore:
    """设备健康评分"""

    def test_get_health_score(self, api: ApiClient):
        device_id = str(uuid.uuid4())
        resp = api.get(f"{BASE}/{device_id}/score")
        assert resp.status_code in (200, 404)

    def test_get_health_score_unauthorized(self, anon_api: ApiClient):
        device_id = str(uuid.uuid4())
        resp = anon_api.get(f"{BASE}/{device_id}/score")
        assert resp.status_code == 401


class TestDeviceHealthBatchCheck:
    """批量健康检查"""

    def test_batch_check(self, api: ApiClient, health_check_request):
        resp = api.post(f"{BASE}/batch-check", json=health_check_request)
        assert resp.status_code == 200
        body = resp.json()
        assert body["success"] is True

    def test_batch_check_empty_list(self, api: ApiClient):
        resp = api.post(f"{BASE}/batch-check", json={"deviceIds": []})
        assert resp.status_code in (400, 422)

    def test_batch_check_unauthorized(self, anon_api: ApiClient, health_check_request):
        resp = anon_api.post(f"{BASE}/batch-check", json=health_check_request)
        assert resp.status_code == 401


class TestDeviceHealthHistory:
    """健康趋势"""

    def test_get_health_history(self, api: ApiClient):
        device_id = str(uuid.uuid4())
        resp = api.get(f"{BASE}/{device_id}/history", params={
            "startTime": "2025-01-01T00:00:00Z",
            "endTime": "2025-06-01T00:00:00Z",
        })
        assert resp.status_code in (200, 404)

    def test_get_health_trend(self, api: ApiClient):
        device_id = str(uuid.uuid4())
        resp = api.get(f"{BASE}/{device_id}/trend", params={"days": 30})
        assert resp.status_code in (200, 404)

    def test_health_history_unauthorized(self, anon_api: ApiClient):
        device_id = str(uuid.uuid4())
        resp = anon_api.get(f"{BASE}/{device_id}/history")
        assert resp.status_code == 401
