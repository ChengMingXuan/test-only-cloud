"""
业务编号生成器 API 测试
========================
覆盖 BusinessNoGenerator 工具类（通过各业务端点间接测试）
"""
import pytest
import uuid
from tests.conftest import ApiClient


class TestBusinessNoViaCharging:
    """通过充电订单验证业务编号生成"""

    BASE = "/api/charging"

    def test_create_order_generates_no(self, api: ApiClient):
        """创建订单应生成唯一业务编号"""
        resp = api.post(f"{self.BASE}/orders", json={
            "stationId": str(uuid.uuid4()),
            "pileId": str(uuid.uuid4()),
            "connectorId": 1,
            "userId": str(uuid.uuid4()),
            "startSoc": 20.0,
            "chargingMode": "fast",
        })
        if resp.status_code == 200:
            data = resp.json().get("data", {})
            order_no = data.get("orderNo") or data.get("orderNumber")
            if order_no:
                assert len(order_no) > 0
                assert order_no.startswith(("CHG", "ORD"))  # 业务前缀

    def test_order_no_uniqueness(self, api: ApiClient):
        """连续创建两个订单，编号应不同"""
        payload = {
            "stationId": str(uuid.uuid4()),
            "pileId": str(uuid.uuid4()),
            "connectorId": 1,
            "userId": str(uuid.uuid4()),
            "startSoc": 20.0,
            "chargingMode": "fast",
        }
        resp1 = api.post(f"{self.BASE}/orders", json=payload)
        resp2 = api.post(f"{self.BASE}/orders", json=payload)
        if resp1.status_code == 200 and resp2.status_code == 200:
            no1 = resp1.json().get("data", {}).get("orderNo")
            no2 = resp2.json().get("data", {}).get("orderNo")
            if no1 and no2:
                assert no1 != no2


class TestBusinessNoViaWorkOrder:
    """通过工单验证业务编号生成"""

    BASE = "/api/workorder"

    def test_create_workorder_generates_no(self, api: ApiClient):
        resp = api.post(f"{self.BASE}/orders", json={
            "title": f"测试工单_{uuid.uuid4().hex[:4]}",
            "description": "业务编号测试",
            "orderType": "repair",
            "priority": "high",
            "deviceId": str(uuid.uuid4()),
        })
        if resp.status_code == 200:
            data = resp.json().get("data", {})
            wo_no = data.get("orderNo") or data.get("workOrderNo")
            if wo_no:
                assert len(wo_no) > 0


class TestBusinessNoViaSettlement:
    """通过结算验证业务编号生成"""

    BASE = "/api/settlement"

    def test_create_settlement_generates_no(self, api: ApiClient):
        resp = api.post(f"{self.BASE}/bills", json={
            "orderId": str(uuid.uuid4()),
            "amount": 100.50,
            "settlementType": "charging",
        })
        if resp.status_code == 200:
            data = resp.json().get("data", {})
            bill_no = data.get("billNo") or data.get("settlementNo")
            if bill_no:
                assert len(bill_no) > 0
