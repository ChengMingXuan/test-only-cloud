"""
微电网能源报告 API 测试
========================
覆盖 MgEnergyReportController 全部 5 个端点
"""
import pytest
import uuid
from tests.conftest import ApiClient

BASE = "/api/microgrid/energy"


@pytest.fixture
def microgrid_id():
    return str(uuid.uuid4())


@pytest.fixture
def report_request():
    return {
        "microgridId": str(uuid.uuid4()),
        "reportType": "daily",
        "startDate": "2025-01-01",
        "endDate": "2025-01-31",
    }


class TestEnergyReportGenerate:
    """生成能源报告"""

    def test_generate_report(self, api: ApiClient, report_request):
        resp = api.post(f"{BASE}/reports/generate", json=report_request)
        assert resp.status_code == 200
        body = resp.json()
        assert body["success"] is True

    def test_generate_missing_params(self, api: ApiClient):
        resp = api.post(f"{BASE}/reports/generate", json={})
        assert resp.status_code in (400, 422)

    def test_generate_unauthorized(self, anon_api: ApiClient, report_request):
        resp = anon_api.post(f"{BASE}/reports/generate", json=report_request)
        assert resp.status_code == 401


class TestEnergyReportList:
    """报告列表"""

    def test_list_reports(self, api: ApiClient, microgrid_id):
        resp = api.get(f"{BASE}/reports", params={
            "microgridId": microgrid_id,
            "page": 1,
            "pageSize": 10,
        })
        assert resp.status_code == 200

    def test_list_reports_with_type_filter(self, api: ApiClient, microgrid_id):
        resp = api.get(f"{BASE}/reports", params={
            "microgridId": microgrid_id,
            "reportType": "monthly",
            "page": 1,
            "pageSize": 10,
        })
        assert resp.status_code == 200

    def test_list_reports_unauthorized(self, anon_api: ApiClient):
        resp = anon_api.get(f"{BASE}/reports")
        assert resp.status_code == 401


class TestEnergyReportDetail:
    """报告详情"""

    def test_get_report(self, api: ApiClient):
        report_id = str(uuid.uuid4())
        resp = api.get(f"{BASE}/reports/{report_id}")
        assert resp.status_code in (200, 404)


class TestEnergyReportExport:
    """导出报告"""

    def test_export_pdf(self, api: ApiClient):
        report_id = str(uuid.uuid4())
        resp = api.get(f"{BASE}/reports/{report_id}/export", params={"format": "pdf"})
        assert resp.status_code in (200, 404)

    def test_export_excel(self, api: ApiClient):
        report_id = str(uuid.uuid4())
        resp = api.get(f"{BASE}/reports/{report_id}/export", params={"format": "excel"})
        assert resp.status_code in (200, 404)


class TestEnergyReportSummary:
    """能源汇总"""

    def test_get_summary(self, api: ApiClient, microgrid_id):
        resp = api.get(f"{BASE}/summary/{microgrid_id}")
        assert resp.status_code in (200, 404)

    def test_get_summary_with_period(self, api: ApiClient, microgrid_id):
        resp = api.get(f"{BASE}/summary/{microgrid_id}", params={
            "period": "month",
            "year": 2025,
            "month": 1,
        })
        assert resp.status_code in (200, 404)
