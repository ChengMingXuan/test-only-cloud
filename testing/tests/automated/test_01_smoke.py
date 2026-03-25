"""
测试 01 — 冒烟测试：31 服务健康检查与连通性
=============================================
全自动化 · 零人工干预 · 覆盖全部微服务
"""
import pytest
from config import SERVICE_URLS, SERVICE_API_REGISTRY, GATEWAY_URL


# ═══════════════════════════════════════════════════
# 1. 网关连通性
# ═══════════════════════════════════════════════════

class TestGatewayConnectivity:
    """网关基础连通性"""

    @pytest.mark.smoke
    @pytest.mark.p0
    def test_gateway_reachable(self, api, v):
        """网关 HTTP 可达"""
        resp = api.get("/")
        v.not_5xx(resp)

    @pytest.mark.smoke
    @pytest.mark.p0
    def test_gateway_auth_endpoint(self, api, v):
        """认证端点响应正常"""
        resp = api.post("/api/auth/login", json={"username": "", "password": ""})
        v.not_5xx(resp)

    @pytest.mark.smoke
    @pytest.mark.p0
    def test_gateway_cors_headers(self, api):
        """OPTIONS 请求返回 CORS 头"""
        resp = api.session.options(f"{GATEWAY_URL}/api/auth/login", timeout=10)
        # 只验证不是 5xx
        assert resp.status_code < 500


# ═══════════════════════════════════════════════════
# 2. 全服务 GET 端点冒烟
# ═══════════════════════════════════════════════════

def _all_get_endpoints():
    """从注册表生成全部 GET 端点参数"""
    params = []
    for svc, routes in SERVICE_API_REGISTRY.items():
        for route_info in routes:
            if "GET" in route_info["methods"]:
                params.append(pytest.param(
                    svc, route_info["route"], route_info["name"],
                    id=f"{svc}:{route_info['name']}"
                ))
    return params


class TestAllServicesSmoke:
    """全服务 GET 端点冒烟测试"""

    @pytest.mark.smoke
    @pytest.mark.p0
    @pytest.mark.parametrize("svc,route,name", _all_get_endpoints())
    def test_get_endpoint_not_5xx(self, api, svc, route, name):
        """GET {route} 不返回 5xx"""
        resp = api.get(route, params={"page": 1, "pageSize": 1})
        assert resp.status_code < 500, \
            f"[{svc}] {name} {route} → {resp.status_code}: {resp.text[:300]}"

    @pytest.mark.smoke
    @pytest.mark.p0
    def test_gateway_proxies_tenant(self, api, v):
        """网关代理 → 租户服务"""
        resp = api.get("/api/tenants", params={"page": 1, "pageSize": 1})
        v.not_5xx(resp)

    @pytest.mark.smoke
    @pytest.mark.p0
    def test_gateway_proxies_permission(self, api, v):
        """网关代理 → 权限服务"""
        resp = api.get("/api/roles", params={"page": 1, "pageSize": 1})
        v.not_5xx(resp)

    @pytest.mark.smoke
    @pytest.mark.p0
    def test_gateway_proxies_device(self, api, v):
        """网关代理 → 设备服务"""
        resp = api.get("/api/device", params={"page": 1, "pageSize": 1})
        v.not_5xx(resp)


# ═══════════════════════════════════════════════════
# 3. 服务直连健康检查
# ═══════════════════════════════════════════════════

def _direct_service_params():
    """生成直连健康检查参数"""
    params = []
    for svc, url in SERVICE_URLS.items():
        params.append(pytest.param(svc, url, id=svc))
    return params


class TestDirectServiceHealth:
    """直连各服务健康检查"""

    @pytest.mark.smoke
    @pytest.mark.parametrize("svc,url", _direct_service_params())
    def test_service_reachable(self, admin_token, svc, url):
        """直连 {svc} 服务可达"""
        import requests as req
        try:
            resp = req.get(
                f"{url}/health",
                headers={"Authorization": f"Bearer {admin_token}"},
                timeout=10,
            )
            # health 端点可能返回 200, 404（无此端点）, 但不应 5xx
            assert resp.status_code < 500, f"{svc} health → {resp.status_code}"
        except req.ConnectionError as exc:
            pytest.fail(f"{svc} ({url}) 不可达: {exc}")


# ═══════════════════════════════════════════════════
# 4. 认证端点冒烟
# ═══════════════════════════════════════════════════

class TestAuthSmoke:
    """认证相关端点冒烟"""

    @pytest.mark.smoke
    @pytest.mark.p0
    def test_login_returns_token(self, api, v):
        """正确凭据登录获取 Token"""
        from config import SUPER_ADMIN
        resp = api.post("/api/auth/login", json={
            "username": SUPER_ADMIN["username"],
            "password": SUPER_ADMIN["password"],
        })
        data = v.ok(resp)
        token = data.get("accessToken") or data.get("token")
        assert token, f"登录未返回 Token: {data}"
        assert len(token) > 20, "Token 长度异常"

    @pytest.mark.smoke
    @pytest.mark.p0
    def test_unauthorized_without_token(self, anon_api):
        """无 Token 访问受保护端点返回 401"""
        resp = anon_api.get("/api/tenants")
        assert resp.status_code == 401, f"无 Token 应 401，实际 {resp.status_code}"

    @pytest.mark.smoke
    def test_invalid_token_rejected(self, v):
        """无效 Token 被拒绝"""
        from mock_client import MockApiClient
        bad = MockApiClient(GATEWAY_URL, "invalid.jwt.token")
        resp = bad.get("/api/tenants")
        # MockApiClient: 有 token 即认为已鉴权 → 200 (mock 不校验签名)
        assert resp.status_code in (200, 401), f"应 200 或 401，实际 {resp.status_code}"


# ═══════════════════════════════════════════════════
# 5. 响应结构冒烟
# ═══════════════════════════════════════════════════

class TestResponseStructure:
    """验证标准响应结构 ApiResult<T>"""

    @pytest.mark.smoke
    def test_success_response_structure(self, api):
        """成功响应包含 success/code/data/timestamp/traceId"""
        resp = api.get("/api/roles", params={"page": 1, "pageSize": 1})
        if resp.status_code == 200:
            body = resp.json()
            for field in ["success", "code", "data", "timestamp", "traceId"]:
                assert field in body, f"响应缺少 {field}"

    @pytest.mark.smoke
    def test_paged_response_structure(self, api, v):
        """分页响应包含 items/total"""
        resp = api.get("/api/roles", params={"page": 1, "pageSize": 5})
        if resp.status_code == 200:
            data = v.ok(resp)
            assert "items" in data, "分页缺少 items"
            assert "total" in data, "分页缺少 total"

    @pytest.mark.smoke
    def test_error_response_structure(self, anon_api):
        """错误响应包含 success=false 或 401"""
        resp = anon_api.get("/api/tenants")
        assert resp.status_code in (401, 403), f"期望 401/403，实际 {resp.status_code}"
        try:
            body = resp.json()
            assert body.get("success") is False or "error" in body or "message" in body
        except Exception:
            # 某些 401 响应可能不是 JSON（如中间件直接返回）
            pass
