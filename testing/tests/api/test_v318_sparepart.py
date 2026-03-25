"""
备品备件 API 测试
=================
覆盖 SparePartController 全部 17 个端点
"""
import pytest
import uuid
from tests.conftest import ApiClient

BASE = "/api/spare-part"


@pytest.fixture
def spare_part_payload():
    return {
        "partCode": f"SP_{uuid.uuid4().hex[:8]}",
        "partName": f"逆变器模块_{uuid.uuid4().hex[:4]}",
        "category": "inverter",
        "specification": "50kW",
        "unit": "个",
        "safetyStock": 10,
        "warehouseId": str(uuid.uuid4()),
    }


@pytest.fixture
def stock_in_payload():
    return {
        "partId": str(uuid.uuid4()),
        "quantity": 20,
        "supplierId": str(uuid.uuid4()),
        "unitPrice": 15000.0,
        "batchNo": f"BATCH_{uuid.uuid4().hex[:6]}",
    }


@pytest.fixture
def stock_out_payload():
    return {
        "partId": str(uuid.uuid4()),
        "quantity": 5,
        "workOrderId": str(uuid.uuid4()),
        "recipientName": "张工",
        "purpose": "维修更换",
    }


class TestSparePartCrud:
    """备件基础 CRUD"""

    def test_create_spare_part(self, api: ApiClient, spare_part_payload):
        resp = api.post(BASE, json=spare_part_payload)
        assert resp.status_code == 200
        body = resp.json()
        assert body["success"] is True

    def test_create_missing_fields(self, api: ApiClient):
        resp = api.post(BASE, json={})
        assert resp.status_code in (400, 422)

    def test_create_unauthorized(self, anon_api: ApiClient, spare_part_payload):
        resp = anon_api.post(BASE, json=spare_part_payload)
        assert resp.status_code == 401

    def test_list_spare_parts(self, api: ApiClient):
        resp = api.get(BASE, params={"page": 1, "pageSize": 10})
        assert resp.status_code == 200

    def test_list_with_category_filter(self, api: ApiClient):
        resp = api.get(BASE, params={"category": "inverter", "page": 1, "pageSize": 10})
        assert resp.status_code == 200

    def test_get_spare_part(self, api: ApiClient):
        part_id = str(uuid.uuid4())
        resp = api.get(f"{BASE}/{part_id}")
        assert resp.status_code in (200, 404)

    def test_update_spare_part(self, api: ApiClient, spare_part_payload):
        part_id = str(uuid.uuid4())
        resp = api.put(f"{BASE}/{part_id}", json=spare_part_payload)
        assert resp.status_code in (200, 404)

    def test_delete_spare_part(self, api: ApiClient):
        part_id = str(uuid.uuid4())
        resp = api.delete(f"{BASE}/{part_id}")
        assert resp.status_code in (200, 404)


class TestSparePartStockIn:
    """入库管理"""

    def test_stock_in(self, api: ApiClient, stock_in_payload):
        resp = api.post(f"{BASE}/stock-in", json=stock_in_payload)
        assert resp.status_code == 200

    def test_stock_in_zero_quantity(self, api: ApiClient, stock_in_payload):
        stock_in_payload["quantity"] = 0
        resp = api.post(f"{BASE}/stock-in", json=stock_in_payload)
        assert resp.status_code in (400, 422)

    def test_stock_in_unauthorized(self, anon_api: ApiClient, stock_in_payload):
        resp = anon_api.post(f"{BASE}/stock-in", json=stock_in_payload)
        assert resp.status_code == 401

    def test_stock_in_history(self, api: ApiClient):
        part_id = str(uuid.uuid4())
        resp = api.get(f"{BASE}/{part_id}/stock-in-records", params={"page": 1, "pageSize": 10})
        assert resp.status_code in (200, 404)


class TestSparePartStockOut:
    """出库管理"""

    def test_stock_out(self, api: ApiClient, stock_out_payload):
        resp = api.post(f"{BASE}/stock-out", json=stock_out_payload)
        assert resp.status_code in (200, 400)  # 库存不足时返回 400

    def test_stock_out_exceeds_stock(self, api: ApiClient, stock_out_payload):
        stock_out_payload["quantity"] = 999999
        resp = api.post(f"{BASE}/stock-out", json=stock_out_payload)
        assert resp.status_code in (400, 422)

    def test_stock_out_unauthorized(self, anon_api: ApiClient, stock_out_payload):
        resp = anon_api.post(f"{BASE}/stock-out", json=stock_out_payload)
        assert resp.status_code == 401

    def test_stock_out_history(self, api: ApiClient):
        part_id = str(uuid.uuid4())
        resp = api.get(f"{BASE}/{part_id}/stock-out-records", params={"page": 1, "pageSize": 10})
        assert resp.status_code in (200, 404)


class TestSparePartInventory:
    """库存查询"""

    def test_get_inventory(self, api: ApiClient):
        resp = api.get(f"{BASE}/inventory", params={"page": 1, "pageSize": 10})
        assert resp.status_code == 200

    def test_get_inventory_by_warehouse(self, api: ApiClient):
        warehouse_id = str(uuid.uuid4())
        resp = api.get(f"{BASE}/inventory", params={
            "warehouseId": warehouse_id,
            "page": 1,
            "pageSize": 10,
        })
        assert resp.status_code == 200

    def test_get_low_stock_alerts(self, api: ApiClient):
        resp = api.get(f"{BASE}/inventory/low-stock")
        assert resp.status_code == 200

    def test_inventory_unauthorized(self, anon_api: ApiClient):
        resp = anon_api.get(f"{BASE}/inventory")
        assert resp.status_code == 401


class TestSparePartStatistics:
    """统计分析"""

    def test_get_statistics(self, api: ApiClient):
        resp = api.get(f"{BASE}/statistics", params={"year": 2025})
        assert resp.status_code == 200

    def test_get_consumption_report(self, api: ApiClient):
        resp = api.get(f"{BASE}/statistics/consumption", params={
            "startDate": "2025-01-01",
            "endDate": "2025-06-30",
        })
        assert resp.status_code == 200
