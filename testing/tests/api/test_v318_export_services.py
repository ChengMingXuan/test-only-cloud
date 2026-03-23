"""
导出服务 API 测试
=================
覆盖 ExcelExportHelper + PdfExportService
"""
import pytest
import uuid
from tests.conftest import ApiClient

EXCEL_BASE = "/api/export/excel"
PDF_BASE = "/api/export/pdf"


@pytest.fixture
def excel_export_request():
    return {
        "dataSource": "charging_orders",
        "filters": {
            "startDate": "2025-01-01",
            "endDate": "2025-06-30",
        },
        "columns": ["orderId", "stationName", "amount", "createTime"],
        "fileName": "充电订单导出",
    }


@pytest.fixture
def pdf_export_request():
    return {
        "templateId": str(uuid.uuid4()),
        "reportType": "monthly_summary",
        "parameters": {
            "month": "2025-06",
            "stationId": str(uuid.uuid4()),
        },
    }


class TestExcelExport:
    """Excel 导出"""

    def test_export_excel(self, api: ApiClient, excel_export_request):
        resp = api.post(f"{EXCEL_BASE}/generate", json=excel_export_request)
        assert resp.status_code in (200, 202)  # 同步或异步

    def test_export_excel_missing_source(self, api: ApiClient):
        resp = api.post(f"{EXCEL_BASE}/generate", json={})
        assert resp.status_code in (400, 422)

    def test_export_excel_unauthorized(self, anon_api: ApiClient, excel_export_request):
        resp = anon_api.post(f"{EXCEL_BASE}/generate", json=excel_export_request)
        assert resp.status_code == 401

    def test_export_templates(self, api: ApiClient):
        resp = api.get(f"{EXCEL_BASE}/templates")
        assert resp.status_code == 200

    def test_download_export(self, api: ApiClient):
        task_id = str(uuid.uuid4())
        resp = api.get(f"{EXCEL_BASE}/download/{task_id}")
        assert resp.status_code in (200, 404)


class TestPdfExport:
    """PDF 导出"""

    def test_export_pdf(self, api: ApiClient, pdf_export_request):
        resp = api.post(f"{PDF_BASE}/generate", json=pdf_export_request)
        assert resp.status_code in (200, 202)

    def test_export_pdf_missing_template(self, api: ApiClient):
        resp = api.post(f"{PDF_BASE}/generate", json={})
        assert resp.status_code in (400, 422)

    def test_export_pdf_unauthorized(self, anon_api: ApiClient, pdf_export_request):
        resp = anon_api.post(f"{PDF_BASE}/generate", json=pdf_export_request)
        assert resp.status_code == 401

    def test_pdf_templates(self, api: ApiClient):
        resp = api.get(f"{PDF_BASE}/templates")
        assert resp.status_code == 200

    def test_download_pdf(self, api: ApiClient):
        task_id = str(uuid.uuid4())
        resp = api.get(f"{PDF_BASE}/download/{task_id}")
        assert resp.status_code in (200, 404)

    def test_pdf_preview(self, api: ApiClient, pdf_export_request):
        resp = api.post(f"{PDF_BASE}/preview", json=pdf_export_request)
        assert resp.status_code in (200, 400)
