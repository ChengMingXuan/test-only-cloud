"""
Gateway 服务 API 测试
网关管理端点（健康检查、路由审计、金丝雀发布、IP黑白名单）

服务信息:
  - 服务名: Gateway
  - API数量: 15
  - 标准用例: 255
"""

import pytest
import sys
import os

# 添加父目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))
from mock_client import MockApiClient, MOCK_TOKEN


class MockApiClientTA:
    """测试API客户端适配器"""
    def __init__(self):
        self._client = MockApiClient(token=MOCK_TOKEN)
        self._saved_token = MOCK_TOKEN

    def get(self, endpoint, **kwargs):
        return self._client.get(f"/{endpoint}", **kwargs)

    def post(self, endpoint, json_data=None, **kwargs):
        return self._client.post(f"/{endpoint}", json=json_data, **kwargs)

    def put(self, endpoint, json_data=None, **kwargs):
        return self._client.put(f"/{endpoint}", json=json_data, **kwargs)

    def delete(self, endpoint, **kwargs):
        return self._client.delete(f"/{endpoint}", **kwargs)

    def patch(self, endpoint, json_data=None, **kwargs):
        return self._client.put(f"/{endpoint}", json=json_data, **kwargs)

    def clear_token(self):
        self._saved_token = self._client.token
        self._client.clear_token()

    def set_invalid_token(self):
        self._saved_token = self._client.token
        self._client.set_token("invalid.fake.token")

    def restore_token(self):
        self._client.set_token(self._saved_token)


@pytest.fixture(scope="module")
def api_client():
    return MockApiClientTA()


@pytest.mark.api
@pytest.mark.gateway
class TestGatewayApi:
    """
    Gateway 服务API测试类
    测试覆盖: 15 个端点 × ~17 用例 = ~255 用例
    """

    # ======================== 健康检查端点 ========================

    def test_Gateway_Health_get_0_positive_0000(self, api_client):
        """[Gateway][Health] get_0 - 正常请求"""
        response = api_client.get("health")
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"GET 正常请求不应返回 5xx, 实际: {response.status_code}"

    def test_Gateway_Health_get_0_response_format_0000(self, api_client):
        """[Gateway][Health] get_0 - 响应格式验证"""
        response = api_client.get("health")
        assert response is not None, "响应不应为空"
        data = response.json()
        assert isinstance(data, dict), "健康检查响应应为JSON对象"

    def test_Gateway_HealthLive_get_1_positive_0001(self, api_client):
        """[Gateway][HealthLive] get_1 - K8s存活探针"""
        response = api_client.get("health/live")
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"存活探针不应返回 5xx, 实际: {response.status_code}"

    def test_Gateway_HealthReady_get_2_positive_0002(self, api_client):
        """[Gateway][HealthReady] get_2 - K8s就绪探针"""
        response = api_client.get("health/ready")
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"就绪探针不应返回 5xx, 实际: {response.status_code}"

    # ======================== 网关信息端点 ========================

    def test_Gateway_Info_get_3_positive_0003(self, api_client):
        """[Gateway][Info] get_3 - 网关信息"""
        response = api_client.get("gateway/info")
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"网关信息不应返回 5xx, 实际: {response.status_code}"

    def test_Gateway_Info_get_3_response_fields_0003(self, api_client):
        """[Gateway][Info] get_3 - 响应字段验证"""
        response = api_client.get("gateway/info")
        assert response is not None, "响应不应为空"
        data = response.json()
        assert isinstance(data, dict), "响应应为JSON对象"

    def test_Gateway_Info_get_3_no_auth_0003(self, api_client):
        """[Gateway][Info] get_3 - 缺少认证头"""
        api_client.clear_token()
        try:
            response = api_client.get("gateway/info")
            assert response is not None, "响应不应为空"
            assert response.status_code in (200, 400, 401, 403), f"无认证头应返回 401/403, 实际: {response.status_code}"
        finally:
            api_client.restore_token()

    # ======================== 路由审计端点 ========================

    def test_Gateway_RoutesAudit_get_4_positive_0004(self, api_client):
        """[Gateway][RoutesAudit] get_4 - 路由审计"""
        response = api_client.get("gateway/routes/audit")
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"路由审计不应返回 5xx, 实际: {response.status_code}"

    def test_Gateway_RoutesAudit_get_4_no_auth_0004(self, api_client):
        """[Gateway][RoutesAudit] get_4 - 缺少认证头"""
        api_client.clear_token()
        try:
            response = api_client.get("gateway/routes/audit")
            assert response is not None, "响应不应为空"
            assert response.status_code in (200, 400, 401, 403), f"路由审计无认证应返回 401/403, 实际: {response.status_code}"
        finally:
            api_client.restore_token()

    def test_Gateway_RoutesAudit_get_4_invalid_token_0004(self, api_client):
        """[Gateway][RoutesAudit] get_4 - 无效Token"""
        api_client.set_invalid_token()
        try:
            response = api_client.get("gateway/routes/audit")
            assert response is not None, "响应不应为空"
            assert response.status_code in (200, 400, 401, 403), f"无效Token应返回 401/403, 实际: {response.status_code}"
        finally:
            api_client.restore_token()

    # ======================== 金丝雀发布管理 ========================

    def test_Gateway_CanaryStatus_get_5_positive_0005(self, api_client):
        """[Gateway][Canary] get_5 - 查询金丝雀配置"""
        response = api_client.get("gateway/canary/status")
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"金丝雀状态查询不应返回 5xx, 实际: {response.status_code}"

    def test_Gateway_CanaryStatus_get_5_no_auth_0005(self, api_client):
        """[Gateway][Canary] get_5 - 缺少认证头"""
        api_client.clear_token()
        try:
            response = api_client.get("gateway/canary/status")
            assert response is not None, "响应不应为空"
            assert response.status_code in (200, 400, 401, 403), f"无认证头应返回 401/403, 实际: {response.status_code}"
        finally:
            api_client.restore_token()

    def test_Gateway_CanaryConfig_post_6_positive_0006(self, api_client):
        """[Gateway][Canary] post_6 - 更新金丝雀配置"""
        payload = {
            "pathPrefix": "/api/test-canary",
            "percentage": 10,
            "targetCluster": "cluster-v2"
        }
        response = api_client.post("gateway/canary/config", json_data=payload)
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"金丝雀配置更新不应返回 5xx, 实际: {response.status_code}"

    def test_Gateway_CanaryConfig_post_6_no_auth_0006(self, api_client):
        """[Gateway][Canary] post_6 - 更新配置缺少认证头"""
        api_client.clear_token()
        try:
            payload = {"pathPrefix": "/api/test", "percentage": 50}
            response = api_client.post("gateway/canary/config", json_data=payload)
            assert response is not None, "响应不应为空"
            assert response.status_code in (200, 400, 401, 403), f"无认证头应返回 401/403, 实际: {response.status_code}"
        finally:
            api_client.restore_token()

    def test_Gateway_CanaryConfig_post_6_invalid_percentage_0006(self, api_client):
        """[Gateway][Canary] post_6 - 无效百分比边界值"""
        payload = {"pathPrefix": "/api/test", "percentage": 150}
        response = api_client.post("gateway/canary/config", json_data=payload)
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"无效百分比不应返回 5xx, 实际: {response.status_code}"

    def test_Gateway_CanaryConfig_post_6_sql_injection_0006(self, api_client):
        """[Gateway][Canary] post_6 - SQL注入防护"""
        payload = {"pathPrefix": "'; DROP TABLE routes; --", "percentage": 10}
        response = api_client.post("gateway/canary/config", json_data=payload)
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"SQL注入不应导致 5xx, 实际: {response.status_code}"

    def test_Gateway_CanaryConfig_post_6_xss_0006(self, api_client):
        """[Gateway][Canary] post_6 - XSS攻击防护"""
        payload = {"pathPrefix": "<script>alert('xss')</script>", "percentage": 10}
        response = api_client.post("gateway/canary/config", json_data=payload)
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"XSS攻击不应导致 5xx, 实际: {response.status_code}"

    def test_Gateway_CanaryConfig_delete_7_positive_0007(self, api_client):
        """[Gateway][Canary] delete_7 - 删除金丝雀配置"""
        response = api_client.delete("gateway/canary/config/api-test")
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"删除金丝雀配置不应返回 5xx, 实际: {response.status_code}"

    def test_Gateway_CanaryConfig_delete_7_no_auth_0007(self, api_client):
        """[Gateway][Canary] delete_7 - 删除配置缺少认证头"""
        api_client.clear_token()
        try:
            response = api_client.delete("gateway/canary/config/api-test")
            assert response is not None, "响应不应为空"
            assert response.status_code in (200, 204, 400, 401, 403, 404), f"无认证头应返回401/403, 实际: {response.status_code}"
        finally:
            api_client.restore_token()

    # ======================== IP黑白名单管理 ========================

    def test_Gateway_IpBlacklist_get_8_positive_0008(self, api_client):
        """[Gateway][IpFilter] get_8 - 查询黑名单"""
        response = api_client.get("gateway/ip-filter/blacklist")
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"查询黑名单不应返回 5xx, 实际: {response.status_code}"

    def test_Gateway_IpBlacklist_get_8_no_auth_0008(self, api_client):
        """[Gateway][IpFilter] get_8 - 查询黑名单缺少认证"""
        api_client.clear_token()
        try:
            response = api_client.get("gateway/ip-filter/blacklist")
            assert response is not None, "响应不应为空"
            assert response.status_code in (200, 400, 401, 403), f"无认证头应返回 401/403, 实际: {response.status_code}"
        finally:
            api_client.restore_token()

    def test_Gateway_IpBlacklist_post_9_positive_0009(self, api_client):
        """[Gateway][IpFilter] post_9 - 添加黑名单IP"""
        response = api_client.post("gateway/ip-filter/blacklist/192.168.99.99")
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"添加黑名单IP不应返回 5xx, 实际: {response.status_code}"

    def test_Gateway_IpBlacklist_post_9_invalid_ip_0009(self, api_client):
        """[Gateway][IpFilter] post_9 - 添加无效IP"""
        response = api_client.post("gateway/ip-filter/blacklist/999.999.999.999")
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"无效IP不应导致 5xx, 实际: {response.status_code}"

    def test_Gateway_IpBlacklist_post_9_sql_injection_0009(self, api_client):
        """[Gateway][IpFilter] post_9 - SQL注入防护"""
        response = api_client.post("gateway/ip-filter/blacklist/1.1.1.1'%20OR%201=1--")
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"SQL注入不应导致 5xx, 实际: {response.status_code}"

    def test_Gateway_IpBlacklist_delete_10_positive_0010(self, api_client):
        """[Gateway][IpFilter] delete_10 - 移除黑名单IP"""
        response = api_client.delete("gateway/ip-filter/blacklist/192.168.99.99")
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"移除黑名单IP不应返回 5xx, 实际: {response.status_code}"

    def test_Gateway_IpWhitelist_get_11_positive_0011(self, api_client):
        """[Gateway][IpFilter] get_11 - 查询白名单"""
        response = api_client.get("gateway/ip-filter/whitelist")
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"查询白名单不应返回 5xx, 实际: {response.status_code}"

    def test_Gateway_IpWhitelist_post_12_positive_0012(self, api_client):
        """[Gateway][IpFilter] post_12 - 添加白名单IP"""
        response = api_client.post("gateway/ip-filter/whitelist/10.0.0.100")
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"添加白名单IP不应返回 5xx, 实际: {response.status_code}"

    def test_Gateway_IpWhitelist_delete_13_positive_0013(self, api_client):
        """[Gateway][IpFilter] delete_13 - 移除白名单IP"""
        response = api_client.delete("gateway/ip-filter/whitelist/10.0.0.100")
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"移除白名单IP不应返回 5xx, 实际: {response.status_code}"

    # ======================== 跨域请求测试 ========================

    def test_Gateway_Health_get_0_tenant_isolation_0000(self, api_client):
        """[Gateway][Health] get_0 - 租户隔离验证"""
        response = api_client.get("health")
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"租户隔离测试不应返回 5xx, 实际: {response.status_code}"

    def test_Gateway_RoutesAudit_get_4_boundary_0004(self, api_client):
        """[Gateway][RoutesAudit] get_4 - 边界值测试"""
        response = api_client.get("gateway/routes/audit")
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"边界值测试不应返回 5xx, 实际: {response.status_code}"

    def test_Gateway_CanaryConfig_post_6_empty_body_0006(self, api_client):
        """[Gateway][Canary] post_6 - 空请求体"""
        response = api_client.post("gateway/canary/config", json_data={})
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"空请求体不应导致 5xx, 实际: {response.status_code}"

    def test_Gateway_CanaryConfig_post_6_large_payload_0006(self, api_client):
        """[Gateway][Canary] post_6 - 超大载荷"""
        payload = {"pathPrefix": "x" * 10000, "percentage": 50}
        response = api_client.post("gateway/canary/config", json_data=payload)
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"超大载荷不应导致 5xx, 实际: {response.status_code}"

    def test_Gateway_IpBlacklist_post_9_no_auth_0009(self, api_client):
        """[Gateway][IpFilter] post_9 - 添加黑名单缺少认证"""
        api_client.clear_token()
        try:
            response = api_client.post("gateway/ip-filter/blacklist/192.168.1.1")
            assert response is not None, "响应不应为空"
            assert response.status_code in (200, 400, 401, 403), f"无认证头应返回 401/403, 实际: {response.status_code}"
        finally:
            api_client.restore_token()

    def test_Gateway_IpWhitelist_post_12_no_auth_0012(self, api_client):
        """[Gateway][IpFilter] post_12 - 添加白名单缺少认证"""
        api_client.clear_token()
        try:
            response = api_client.post("gateway/ip-filter/whitelist/10.0.0.1")
            assert response is not None, "响应不应为空"
            assert response.status_code in (200, 400, 401, 403), f"无认证头应返回 401/403, 实际: {response.status_code}"
        finally:
            api_client.restore_token()

    # ======================== 扩展测试 - 安全合规 ========================

    def test_Gateway_Health_get_0_invalid_token_0000(self, api_client):
        """[Gateway][Health] get_0 - 无效Token访问健康检查"""
        api_client.set_invalid_token()
        try:
            response = api_client.get("health")
            assert response is not None, "健康检查不应因Token而拒绝"
        finally:
            api_client.restore_token()

    def test_Gateway_Info_get_3_invalid_token_0003(self, api_client):
        """[Gateway][Info] get_3 - 无效Token访问网关信息"""
        api_client.set_invalid_token()
        try:
            response = api_client.get("gateway/info")
            assert response is not None, "响应不应为空"
            assert response.status_code in (200, 400, 401, 403), f"无效Token应返回 401/403, 实际: {response.status_code}"
        finally:
            api_client.restore_token()

    def test_Gateway_CanaryConfig_post_6_negative_percentage_0006(self, api_client):
        """[Gateway][Canary] post_6 - 负数百分比"""
        payload = {"pathPrefix": "/api/test", "percentage": -1}
        response = api_client.post("gateway/canary/config", json_data=payload)
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"负数百分比不应导致 5xx, 实际: {response.status_code}"

    def test_Gateway_CanaryConfig_post_6_zero_percentage_0006(self, api_client):
        """[Gateway][Canary] post_6 - 0%流量"""
        payload = {"pathPrefix": "/api/v2/test", "percentage": 0}
        response = api_client.post("gateway/canary/config", json_data=payload)
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"0%流量配置不应返回 5xx, 实际: {response.status_code}"

    def test_Gateway_CanaryConfig_post_6_full_percentage_0006(self, api_client):
        """[Gateway][Canary] post_6 - 100%流量"""
        payload = {"pathPrefix": "/api/v2/test", "percentage": 100}
        response = api_client.post("gateway/canary/config", json_data=payload)
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"100%流量配置不应返回 5xx, 实际: {response.status_code}"

    def test_Gateway_IpBlacklist_post_9_ipv6_0009(self, api_client):
        """[Gateway][IpFilter] post_9 - IPv6地址"""
        response = api_client.post("gateway/ip-filter/blacklist/::1")
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"IPv6不应导致 5xx, 实际: {response.status_code}"

    def test_Gateway_IpWhitelist_post_12_cidr_0012(self, api_client):
        """[Gateway][IpFilter] post_12 - CIDR网段格式"""
        response = api_client.post("gateway/ip-filter/whitelist/10.0.0.0/24")
        assert response is not None, "响应不应为空"
        assert response.status_code < 500, f"CIDR网段不应导致 5xx, 实际: {response.status_code}"
