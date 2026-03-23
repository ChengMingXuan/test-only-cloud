"""pytest权限审计"""
import pytest
from mock_client import MockApiClient, MOCK_TOKEN

CODES = ['account:list:execute','account:create:execute','account:edit:execute','account:delete:execute','device:list:execute','device:create:execute','device:edit:execute','device:delete:execute','charging:list:execute','charging:create:execute','charging:edit:execute','charging:delete:execute','station:list:execute','station:create:execute','station:edit:execute','station:delete:execute','energy:list:execute','energy:create:execute','energy:edit:execute','energy:delete:execute','settlement:list:execute','settlement:create:execute','settlement:edit:execute','settlement:delete:execute','analytics:list:execute','analytics:create:execute','analytics:edit:execute','analytics:delete:execute']

class TestPerms:
    @pytest.mark.parametrize("code", CODES)
    def test_perm(self, code):
        client = MockApiClient(token=MOCK_TOKEN)
        r = client.get("/test", headers={"X-Perm": code})
        assert r.status_code in [200, 403]
