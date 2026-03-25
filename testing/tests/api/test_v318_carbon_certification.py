"""
碳认证（I-REC / CCER）API 测试
===============================
覆盖 CarbonCertificationController 全部 12 个端点
"""
import pytest
import uuid
from tests.conftest import ApiClient

BASE = "/api/carbon"


@pytest.fixture
def irec_register_payload():
    return {
        "facilityName": "光伏电站A",
        "facilityType": "solar",
        "capacityMW": 50.0,
        "country": "CN",
        "commissionDate": "2024-01-01",
    }


@pytest.fixture
def irec_issue_payload():
    return {
        "facilityId": str(uuid.uuid4()),
        "productionStartDate": "2025-01-01",
        "productionEndDate": "2025-12-31",
        "mwhGenerated": 12000.0,
    }


@pytest.fixture
def ccer_project_payload():
    return {
        "projectName": "分布式光伏碳减排项目",
        "methodology": "CDM-ACM0002",
        "estimatedReduction": 5000.0,
        "startDate": "2025-01-01",
        "endDate": "2030-12-31",
    }


class TestIRecRegistration:
    """I-REC 设施注册"""

    def test_register_success(self, api: ApiClient, irec_register_payload):
        resp = api.post(f"{BASE}/irec/register", json=irec_register_payload)
        assert resp.status_code == 200
        assert resp.json()["success"] is True

    def test_register_missing_fields(self, api: ApiClient):
        resp = api.post(f"{BASE}/irec/register", json={})
        assert resp.status_code in (400, 422)

    def test_register_unauthorized(self, anon_api: ApiClient, irec_register_payload):
        resp = anon_api.post(f"{BASE}/irec/register", json=irec_register_payload)
        assert resp.status_code == 401


class TestIRecIssuance:
    """I-REC 证书签发"""

    def test_issue_success(self, api: ApiClient, irec_issue_payload):
        resp = api.post(f"{BASE}/irec/issue", json=irec_issue_payload)
        assert resp.status_code == 200

    def test_issue_unauthorized(self, anon_api: ApiClient, irec_issue_payload):
        resp = anon_api.post(f"{BASE}/irec/issue", json=irec_issue_payload)
        assert resp.status_code == 401


class TestIRecTransfer:
    """I-REC 证书转让"""

    def test_transfer_success(self, api: ApiClient):
        cert_id = str(uuid.uuid4())
        resp = api.post(f"{BASE}/irec/{cert_id}/transfer", json={"toAccountId": str(uuid.uuid4())})
        assert resp.status_code in (200, 404)

    def test_transfer_unauthorized(self, anon_api: ApiClient):
        resp = anon_api.post(f"{BASE}/irec/{uuid.uuid4()}/transfer", json={})
        assert resp.status_code == 401


class TestIRecRetire:
    """I-REC 证书注销"""

    def test_retire_success(self, api: ApiClient):
        cert_id = str(uuid.uuid4())
        resp = api.post(f"{BASE}/irec/{cert_id}/retire", json={"retirementPurpose": "自愿减排"})
        assert resp.status_code in (200, 404)


class TestIRecCertificates:
    """I-REC 证书查询"""

    def test_list_certificates(self, api: ApiClient):
        resp = api.get(f"{BASE}/irec/certificates", params={"page": 1, "pageSize": 10})
        assert resp.status_code == 200

    def test_list_with_status_filter(self, api: ApiClient):
        resp = api.get(f"{BASE}/irec/certificates", params={"status": "active", "page": 1, "pageSize": 10})
        assert resp.status_code == 200

    def test_list_unauthorized(self, anon_api: ApiClient):
        resp = anon_api.get(f"{BASE}/irec/certificates")
        assert resp.status_code == 401


class TestCcerProject:
    """CCER 项目注册"""

    def test_register_project(self, api: ApiClient, ccer_project_payload):
        resp = api.post(f"{BASE}/ccer/project", json=ccer_project_payload)
        assert resp.status_code == 200

    def test_list_projects(self, api: ApiClient):
        resp = api.get(f"{BASE}/ccer/projects", params={"page": 1, "pageSize": 10})
        assert resp.status_code == 200


class TestCcerCredits:
    """CCER 碳信用"""

    def test_request_credits(self, api: ApiClient):
        resp = api.post(f"{BASE}/ccer/credits", json={
            "projectId": str(uuid.uuid4()),
            "reductionTco2": 1000.0,
            "monitoringPeriodStart": "2025-01-01",
            "monitoringPeriodEnd": "2025-06-30",
        })
        assert resp.status_code == 200

    def test_verify_credit(self, api: ApiClient):
        credit_id = str(uuid.uuid4())
        resp = api.post(f"{BASE}/ccer/credits/{credit_id}/verify", json={"verifierName": "审核机构A", "pass": True})
        assert resp.status_code in (200, 404)

    def test_trade_credit(self, api: ApiClient):
        credit_id = str(uuid.uuid4())
        resp = api.post(f"{BASE}/ccer/credits/{credit_id}/trade", json={
            "buyerTenantId": str(uuid.uuid4()),
            "pricePerTco2": 45.5,
        })
        assert resp.status_code in (200, 404)

    def test_retire_credit(self, api: ApiClient):
        credit_id = str(uuid.uuid4())
        resp = api.post(f"{BASE}/ccer/credits/{credit_id}/retire", json={"purpose": "履约抵消"})
        assert resp.status_code in (200, 404)

    def test_list_credits(self, api: ApiClient):
        resp = api.get(f"{BASE}/ccer/credits", params={"page": 1, "pageSize": 10})
        assert resp.status_code == 200

    def test_list_credits_with_project_filter(self, api: ApiClient):
        resp = api.get(f"{BASE}/ccer/credits", params={"projectId": str(uuid.uuid4()), "page": 1, "pageSize": 10})
        assert resp.status_code == 200
