"""
有序充电 API 测试
=================
覆盖 OrderlyChargingController 全部 5 个端点
"""
import pytest
import uuid
from tests.conftest import ApiClient

BASE = "/api/charging/orderly"


@pytest.fixture
def station_id():
    return str(uuid.uuid4())


@pytest.fixture
def queue_request(station_id):
    return {
        "stationId": station_id,
        "userId": str(uuid.uuid4()),
        "vehiclePlate": "京A12345",
        "chargingMode": "fast",
        "targetSoc": 80,
    }


class TestOrderlyChargingEnqueue:
    """排队入队"""

    def test_enqueue_success(self, api: ApiClient, queue_request):
        resp = api.post(f"{BASE}/enqueue", json=queue_request)
        assert resp.status_code == 200
        body = resp.json()
        assert body["success"] is True
        assert body["data"] is not None

    def test_enqueue_missing_station(self, api: ApiClient):
        resp = api.post(f"{BASE}/enqueue", json={"userId": str(uuid.uuid4())})
        assert resp.status_code in (400, 422)

    def test_enqueue_unauthorized(self, anon_api: ApiClient, queue_request):
        resp = anon_api.post(f"{BASE}/enqueue", json=queue_request)
        assert resp.status_code == 401

    def test_enqueue_no_permission(self, readonly_api: ApiClient, queue_request):
        resp = readonly_api.post(f"{BASE}/enqueue", json=queue_request)
        assert resp.status_code == 403


class TestOrderlyChargingDispatch:
    """调度派发"""

    def test_dispatch_success(self, api: ApiClient, station_id):
        resp = api.post(f"{BASE}/{station_id}/dispatch")
        assert resp.status_code == 200

    def test_dispatch_invalid_station(self, api: ApiClient):
        resp = api.post(f"{BASE}/not-a-uuid/dispatch")
        assert resp.status_code in (400, 404)


class TestOrderlyChargingGetQueue:
    """查询队列"""

    def test_get_queue_success(self, api: ApiClient, station_id):
        resp = api.get(f"{BASE}/{station_id}/queue")
        assert resp.status_code == 200
        body = resp.json()
        assert body["success"] is True

    def test_get_queue_unauthorized(self, anon_api: ApiClient, station_id):
        resp = anon_api.get(f"{BASE}/{station_id}/queue")
        assert resp.status_code == 401


class TestOrderlyChargingCancelQueue:
    """取消排队"""

    def test_cancel_queue_not_found(self, api: ApiClient):
        resp = api.delete(f"{BASE}/queue/{uuid.uuid4()}")
        assert resp.status_code in (200, 404)

    def test_cancel_queue_unauthorized(self, anon_api: ApiClient):
        resp = anon_api.delete(f"{BASE}/queue/{uuid.uuid4()}")
        assert resp.status_code == 401


class TestOrderlyChargingPileLoad:
    """桩负荷查询"""

    def test_pile_load_success(self, api: ApiClient, station_id):
        resp = api.get(f"{BASE}/{station_id}/pile-load")
        assert resp.status_code == 200

    def test_pile_load_unauthorized(self, anon_api: ApiClient, station_id):
        resp = anon_api.get(f"{BASE}/{station_id}/pile-load")
        assert resp.status_code == 401
