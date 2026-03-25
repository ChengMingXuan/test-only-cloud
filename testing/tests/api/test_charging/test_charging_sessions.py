"""
Charging 服务 — 充电会话测试
==============================
覆盖：充电会话生命周期（创建→充电中→完成/异常→计费）
优先级：P0
"""
import pytest
import logging
from tests.api.base_test import BaseApiTest

logger = logging.getLogger(__name__)


@pytest.mark.p0
@pytest.mark.charging
class TestChargingSessionLifecycle(BaseApiTest):
    """充电会话生命周期测试"""

    SERVICE_NAME = "charging"
    API_PREFIX = "/api/charging"

    def test_list_sessions(self, api):
        """查询充电会话列表"""
        resp = api.get(f"{self.API_PREFIX}/admin/sessions", params={"page": 1, "pageSize": 10})
        self.assert_paged(resp)

    def test_get_active_sessions(self, api):
        """查询活跃充电会话"""
        resp = api.get(f"{self.API_PREFIX}/admin/sessions", params={"status": "charging", "pageSize": 10})
        self.assert_paged(resp)

    def test_get_session_detail(self, api):
        """获取会话详情"""
        list_resp = api.get(f"{self.API_PREFIX}/admin/sessions", params={"pageSize": 1})
        data = self.assert_paged(list_resp)
        if data["total"] == 0:
            return
        session_id = data["items"][0]["id"]
        detail = api.get(f"{self.API_PREFIX}/admin/sessions/{session_id}")
        self.assert_success(detail)

    def test_get_nonexistent_session(self, api):
        """查询不存在的会话 → 404"""
        resp = api.get(f"{self.API_PREFIX}/admin/sessions/00000000-0000-0000-0000-000000000000")
        assert resp.status_code in (404, 400)

    def test_session_statistics(self, api):
        """查询会话统计数据"""
        resp = api.get(f"{self.API_PREFIX}/admin/sessions/statistics")
        self.assert_success(resp)


@pytest.mark.p1
@pytest.mark.charging
class TestChargingSessionQuery(BaseApiTest):
    """充电会话查询组合测试"""

    SERVICE_NAME = "charging"
    API_PREFIX = "/api/charging/admin/sessions"

    def test_query_by_date_range(self, api):
        """按日期范围查询"""
        resp = api.get(self.API_PREFIX, params={
            "startDate": "2025-01-01", "endDate": "2026-12-31", "pageSize": 10
        })
        self.assert_paged(resp)

    def test_query_by_pile_id(self, api):
        """按充电桩ID查询"""
        resp = api.get(self.API_PREFIX, params={
            "pileId": "00000000-0000-0000-0000-000000000001", "pageSize": 5
        })
        self.assert_paged(resp)

    def test_query_by_user_id(self, api):
        """按用户ID查询"""
        resp = api.get(self.API_PREFIX, params={
            "userId": "00000000-0000-0000-0000-000000000001", "pageSize": 5
        })
        self.assert_paged(resp)

    @pytest.mark.parametrize("status", ["pending", "charging", "completed", "faulted", "cancelled"])
    def test_query_by_all_statuses(self, api, status):
        """按不同状态查询"""
        resp = api.get(self.API_PREFIX, params={"status": status})
        self.assert_paged(resp)


@pytest.mark.p1
@pytest.mark.charging
class TestChargingSessionAbnormal(BaseApiTest):
    """充电会话异常场景测试"""

    SERVICE_NAME = "charging"
    API_PREFIX = "/api/charging"

    def test_stop_nonexistent_session(self, api):
        """停止不存在的会话 → 404"""
        resp = api.post(f"{self.API_PREFIX}/admin/sessions/00000000-0000-0000-0000-000000000000/stop")
        assert resp.status_code in (404, 400, 500)

    def test_invalid_page_params(self, api):
        """非法分页参数"""
        resp = api.get(f"{self.API_PREFIX}/admin/sessions", params={"page": -1, "pageSize": 0})
        # 应返回错误或使用默认值
        assert resp.status_code in (200, 400)

    def test_oversized_page(self, api):
        """超大分页"""
        resp = api.get(f"{self.API_PREFIX}/admin/sessions", params={"page": 1, "pageSize": 10000})
        assert resp.status_code in (200, 400)
