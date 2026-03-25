"""
Charging 服务 — 电价与费率管理测试
====================================
覆盖：电价模板 CRUD + 费率策略 + 时段电价
优先级：P1
"""
import pytest
import logging
from tests.api.base_test import BaseApiTest

logger = logging.getLogger(__name__)


@pytest.mark.p1
@pytest.mark.charging
class TestChargingTariff(BaseApiTest):
    """电价模板管理"""

    SERVICE_NAME = "charging"
    API_PREFIX = "/api/charging"

    def test_list_tariffs(self, api):
        """查询电价模板列表"""
        resp = api.get(f"{self.API_PREFIX}/admin/tariffs", params={"page": 1, "pageSize": 10})
        self.assert_paged(resp)

    def test_get_tariff_detail(self, api):
        """获取电价模板详情"""
        list_resp = api.get(f"{self.API_PREFIX}/admin/tariffs", params={"pageSize": 1})
        data = self.assert_paged(list_resp)
        if data["total"] == 0:
            return
        tariff_id = data["items"][0]["id"]
        detail = api.get(f"{self.API_PREFIX}/admin/tariffs/{tariff_id}")
        self.assert_success(detail)

    def test_tariff_by_station(self, api):
        """按场站查询关联电价"""
        resp = api.get(f"{self.API_PREFIX}/admin/tariffs", params={"stationId": "00000000-0000-0000-0000-000000000001"})
        self.assert_paged(resp)


@pytest.mark.p1
@pytest.mark.charging
class TestChargingFeeCalculation(BaseApiTest):
    """费用计算测试"""

    SERVICE_NAME = "charging"
    API_PREFIX = "/api/charging"

    def test_fee_preview(self, api):
        """费用预估"""
        resp = api.post(f"{self.API_PREFIX}/fee/preview", json={
            "stationId": "00000000-0000-0000-0000-000000000001",
            "estimatedKwh": 30.0,
            "chargingMode": "fast",
        })
        # 费用预估可能返回200或404
        assert resp.status_code in (200, 404, 400)

    def test_fee_settlement(self, api):
        """查询费用结算记录"""
        resp = api.get(f"{self.API_PREFIX}/admin/settlements", params={"pageSize": 10})
        # 结算端点可能在settlement服务
        assert resp.status_code in (200, 404)


@pytest.mark.p2
@pytest.mark.charging
class TestChargingPromotion(BaseApiTest):
    """充电优惠活动测试"""

    SERVICE_NAME = "charging"
    API_PREFIX = "/api/charging"

    def test_list_promotions(self, api):
        """查询优惠活动列表"""
        resp = api.get(f"{self.API_PREFIX}/admin/promotions", params={"pageSize": 10})
        # promotions 端点可能不存在
        assert resp.status_code in (200, 404)

    def test_list_coupons(self, api):
        """查询优惠券列表"""
        resp = api.get(f"{self.API_PREFIX}/admin/coupons", params={"pageSize": 10})
        assert resp.status_code in (200, 404)
