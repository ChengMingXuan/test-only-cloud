"""
组串监测 API 测试
=================
覆盖 StringMonitorController 全部 4 个端点
"""
import pytest
import uuid
from tests.conftest import ApiClient

BASE = "/api/pvessc/string-monitor"


@pytest.fixture
def device_id():
    return str(uuid.uuid4())


@pytest.fixture
def string_alert_config():
    return {
        "deviceId": str(uuid.uuid4()),
        "thresholdLow": 0.5,
        "thresholdHigh": 1.5,
        "checkInterval": 300,
    }


class TestStringMonitorRealtime:
    """实时组串数据"""

    def test_get_realtime_data(self, api: ApiClient, device_id):
        resp = api.get(f"{BASE}/{device_id}/realtime")
        assert resp.status_code in (200, 404)

    def test_get_realtime_unauthorized(self, anon_api: ApiClient, device_id):
        resp = anon_api.get(f"{BASE}/{device_id}/realtime")
        assert resp.status_code == 401


class TestStringMonitorHistory:
    """历史组串数据"""

    def test_get_history(self, api: ApiClient, device_id):
        resp = api.get(f"{BASE}/{device_id}/history", params={
            "startTime": "2025-01-01T00:00:00Z",
            "endTime": "2025-01-02T00:00:00Z",
        })
        assert resp.status_code in (200, 404)

    def test_get_history_missing_params(self, api: ApiClient, device_id):
        resp = api.get(f"{BASE}/{device_id}/history")
        assert resp.status_code in (400, 422)

    def test_get_history_unauthorized(self, anon_api: ApiClient, device_id):
        resp = anon_api.get(f"{BASE}/{device_id}/history")
        assert resp.status_code == 401


class TestStringMonitorAnalysis:
    """组串分析"""

    def test_get_analysis(self, api: ApiClient, device_id):
        resp = api.get(f"{BASE}/{device_id}/analysis")
        assert resp.status_code in (200, 404)


class TestStringAlertConfig:
    """告警配置"""

    def test_set_alert_config(self, api: ApiClient, string_alert_config):
        resp = api.post(f"{BASE}/alert-config", json=string_alert_config)
        assert resp.status_code == 200

    def test_set_alert_config_missing_fields(self, api: ApiClient):
        resp = api.post(f"{BASE}/alert-config", json={})
        assert resp.status_code in (400, 422)

    def test_set_alert_config_unauthorized(self, anon_api: ApiClient, string_alert_config):
        resp = anon_api.post(f"{BASE}/alert-config", json=string_alert_config)
        assert resp.status_code == 401

    def test_get_alert_config(self, api: ApiClient, device_id):
        resp = api.get(f"{BASE}/{device_id}/alert-config")
        assert resp.status_code in (200, 404)
