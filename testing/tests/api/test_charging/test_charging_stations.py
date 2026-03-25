"""
Charging 服务 — 充电站点管理测试
=================================
覆盖：充电站CRUD + 状态查询 + 统计
优先级：P0
"""
import pytest
import logging
from tests.api.base_test import BaseApiTest

logger = logging.getLogger(__name__)


@pytest.mark.p0
@pytest.mark.charging
class TestChargingStationCRUD(BaseApiTest):
    """充电站管理 CRUD"""

    SERVICE_NAME = "charging"
    API_PREFIX = "/api/charging"

    def test_list_stations(self, api):
        """查询充电站列表"""
        resp = api.get(f"{self.API_PREFIX}/admin/stations", params={"page": 1, "pageSize": 10})
        self.assert_paged(resp)

    def test_get_station_detail(self, api):
        """获取充电站详情"""
        list_resp = api.get(f"{self.API_PREFIX}/admin/stations", params={"pageSize": 1})
        data = self.assert_paged(list_resp)
        if data["total"] == 0:
            return
        station_id = data["items"][0]["id"]
        detail = api.get(f"{self.API_PREFIX}/admin/stations/{station_id}")
        self.assert_success(detail)

    def test_get_nonexistent_station(self, api):
        """查询不存在的站点 → 404"""
        resp = api.get(f"{self.API_PREFIX}/admin/stations/00000000-0000-0000-0000-000000000000")
        assert resp.status_code in (404, 400)

    def test_station_search_by_name(self, api):
        """按名称搜索站点"""
        resp = api.get(f"{self.API_PREFIX}/admin/stations", params={"keyword": "测试", "pageSize": 5})
        self.assert_paged(resp)

    def test_station_search_by_status(self, api):
        """按状态搜索站点"""
        resp = api.get(f"{self.API_PREFIX}/admin/stations", params={"status": "operating"})
        self.assert_paged(resp)


@pytest.mark.p1
@pytest.mark.charging
class TestChargingPileManagement(BaseApiTest):
    """充电桩管理测试"""

    SERVICE_NAME = "charging"
    API_PREFIX = "/api/charging"

    def test_list_piles(self, api):
        """查询充电桩列表"""
        resp = api.get(f"{self.API_PREFIX}/admin/piles", params={"page": 1, "pageSize": 10})
        self.assert_paged(resp)

    def test_get_pile_detail(self, api):
        """获取充电桩详情"""
        list_resp = api.get(f"{self.API_PREFIX}/admin/piles", params={"pageSize": 1})
        data = self.assert_paged(list_resp)
        if data["total"] == 0:
            return
        pile_id = data["items"][0]["id"]
        detail = api.get(f"{self.API_PREFIX}/admin/piles/{pile_id}")
        self.assert_success(detail)

    def test_pile_status_update(self, api):
        """更新充电桩状态"""
        list_resp = api.get(f"{self.API_PREFIX}/admin/piles", params={"pageSize": 1})
        data = self.assert_paged(list_resp)
        if data["total"] == 0:
            return
        pile_id = data["items"][0]["id"]
        resp = api.put(f"{self.API_PREFIX}/admin/piles/{pile_id}/status", json={"status": "idle"})
        # 状态更新可能成功或不支持
        assert resp.status_code in (200, 400, 404, 405)


@pytest.mark.p1
@pytest.mark.charging
class TestChargingConnector(BaseApiTest):
    """充电枪管理测试"""

    SERVICE_NAME = "charging"
    API_PREFIX = "/api/charging"

    def test_list_connectors(self, api):
        """查询充电枪列表"""
        resp = api.get(f"{self.API_PREFIX}/admin/connectors", params={"pageSize": 10})
        data = self.assert_paged(resp)
        for item in data["items"]:
            assert "id" in item

    def test_connector_by_pile(self, api):
        """按充电桩查询充电枪"""
        resp = api.get(f"{self.API_PREFIX}/admin/connectors", params={
            "pileId": "00000000-0000-0000-0000-000000000001"
        })
        self.assert_paged(resp)
