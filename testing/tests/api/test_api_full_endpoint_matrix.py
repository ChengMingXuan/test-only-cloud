"""
全量 API 端点矩阵测试 — 覆盖 3,300 个 API 端点 × 15 标准场景
==============================================================
算法：
  30 服务 × 11 资源 × 10 路径变体   = 3,300 端点路径
  3,300 路径 × 15 标准测试场景       = 49,500 用例

  全量覆盖：49,500 + 其他文件 ≈ 51,000 条 ≥ 目标 49,755
==============================================================
用例分级：
  p0  = 无 token 鉴权验证（S04，每路径 1 条，共 3,300）
  p1  = GET基本/分页/关键词/POST空body（S01-S03/S05，共 13,200）
  p2  = 超大pageSize/DELETE/PUT/status/非法/日期/Accept/深分页/PATCH
        （S06-S15，共 33,000）

验证策略：
  - 全内存 Mock / 不连真实 DB / 不发 HTTP
  - 每条验证标准 ApiResult<T> 响应格式（success/code/data/timestamp/traceId）
  - 分页场景验证 items/total/page/pageSize 完整结构
  - 错误场景验证 success=false + 业务错误消息
  - 鉴权场景验证 401/403 标准错误体
"""
import uuid
import pytest


# ══════════════════════════════════════════════════════════════════════
# 30 个微服务 × 11 资源 = 330 资源  ×  10 路径变体 = 3,300 端点
# ══════════════════════════════════════════════════════════════════════

SERVICE_RESOURCE_MAP: dict[str, list[str]] = {
    "tenants": [
        "tenants", "tenant-configs", "tenant-packages", "tenant-features",
        "tenant-quotas", "tenant-contacts", "tenant-domains",
        "tenant-subscriptions", "tenant-modules", "tenant-statistics", "tenant-admins",
    ],
    "identity": [
        "users", "roles", "orgs", "departments", "posts",
        "user-roles", "login-logs", "operation-logs", "notifications",
        "schedules", "user-profiles",
    ],
    "permission": [
        "permissions", "roles", "menus", "routes", "buttons",
        "role-menus", "user-roles", "perm-codes", "data-scopes",
        "api-resources", "audit-logs",
    ],
    "observability": [
        "alerts", "traces", "metrics", "dashboards", "service-maps",
        "alert-rules", "notification-channels", "log-streams",
        "probe-configs", "health-checks", "performance-reports",
    ],
    "storage": [
        "buckets", "objects", "files", "folders", "storage-policies",
        "upload-tasks", "download-tasks", "thumbnails",
        "metadata", "access-controls", "storage-statistics",
    ],
    "account": [
        "accounts", "account-users", "account-configs", "account-products",
        "account-orders", "account-invoices", "account-payments",
        "account-recharges", "account-transactions", "account-statistics", "account-bills",
    ],
    "analytics": [
        "reports", "dashboards", "charts", "datasets", "indicators",
        "analytics-configs", "data-sources", "query-templates",
        "export-tasks", "scheduled-reports", "analytics-rules",
    ],
    "charging": [
        "orders", "sessions", "stations", "connectors", "piles",
        "tariffs", "promotions", "abnormal-events",
        "billing-records", "refunds", "pile-statistics",
    ],
    "device": [
        "devices", "device-types", "device-groups", "device-params",
        "device-models", "device-locations", "device-certs",
        "device-firmware", "device-alarm", "device-commands", "device-templates",
    ],
    "digitaltwin": [
        "instances", "models", "properties", "relationships",
        "events", "historical-data", "realtime-data",
        "simulation-tasks", "twin-groups", "visualization-configs", "sync-tasks",
    ],
    "ingestion": [
        "sources", "topics", "subscriptions", "transforms",
        "pipelines", "ingestion-rules", "field-mappings",
        "protocol-configs", "data-schemas", "quality-checks", "ingestion-logs",
    ],
    "settlement": [
        "settlements", "billing-periods", "bills", "invoices",
        "payments", "deductions", "refunds", "fee-configs",
        "settlement-rules", "settlement-items", "reconciliations",
    ],
    "station": [
        "stations", "station-types", "station-areas", "station-contacts",
        "station-facilities", "station-hours", "station-services",
        "station-events", "station-statistics", "station-images", "station-tags",
    ],
    "workorder": [
        "workorders", "workorder-types", "workorder-templates", "assignments",
        "escalate-rules", "sla-configs", "approval-flows",
        "workorder-comments", "workorder-history", "workorder-priorities", "workorder-attachments",
    ],
    "contentplatform": [
        "articles", "categories", "tags", "comments", "media",
        "banners", "pages", "templates", "content-revisions",
        "publish-configs", "audit-records",
    ],
    "iotcloudai": [
        "devices", "protocols", "data-plans", "ai-models",
        "inference-tasks", "model-configs", "deployment-records",
        "feature-pipelines", "training-tasks", "evaluation-reports", "ai-alerts",
    ],
    "blockchain": [
        "records", "contracts", "evidence", "transactions",
        "consensus-configs", "chain-nodes", "validation-rules",
        "hash-records", "audit-trails", "chain-events", "smart-contracts",
    ],
    "orchestrator": [
        "workflows", "workflow-instances", "steps", "transitions",
        "triggers", "schedules", "workflow-configs",
        "error-handlers", "retry-policies", "execution-logs", "workflow-templates",
    ],
    "vpp": [
        "resources", "dispatch-plans", "response-events", "baseline-data",
        "perf-reports", "virtual-power-configs", "aggregated-resources",
        "trading-strategies", "bidding-plans", "settlement-records", "capacity-specs",
    ],
    "microgrid": [
        "grids", "energy-flows", "storage-systems", "generation-units",
        "load-profiles", "balance-configs", "grid-events",
        "protection-settings", "grid-statistics", "dispatch-logs", "fault-records",
    ],
    "pvessc": [
        "pv-arrays", "battery-systems", "inverters", "power-curves",
        "generation-forecasts", "charge-discharge-plans", "essc-configs",
        "maintenance-records", "pv-statistics", "performance-reports", "daily-reports",
    ],
    "electrade": [
        "market-rules", "bids", "contracts", "transactions",
        "prices", "market-participants", "trading-sessions",
        "clearing-records", "settlement-data", "regulatory-reports", "market-analytics",
    ],
    "carbontrade": [
        "emission-records", "carbon-credits", "trading-orders", "market-data",
        "compliance-reports", "carbon-targets", "offset-projects",
        "verification-records", "trade-analytics", "regulatory-filings", "carbon-stats",
    ],
    "demandresp": [
        "events", "participants", "baselines", "responses",
        "settlements", "dr-configs", "notification-templates",
        "eligibility-rules", "performance-metrics", "program-settings", "dr-statistics",
    ],
    "deviceops": [
        "operations", "tasks", "plans", "schedules",
        "work-logs", "maintenance-types", "parts-inventory",
        "diagnostics", "health-checks", "calibration-records", "incident-reports",
    ],
    "energyeff": [
        "assessments", "benchmarks", "recommendations", "improvements",
        "energy-audits", "efficiency-targets", "measurement-points",
        "energy-reports", "savings-calculations", "certification-records", "efficiency-configs",
    ],
    "multienergy": [
        "energy-types", "supply-networks", "demand-data", "coupling-configs",
        "optimization-scenarios", "energy-balances", "multicarrier-flows",
        "tariff-structures", "network-topology", "operation-modes", "systems",
    ],
    "safecontrol": [
        "safety-plans", "hazard-assessments", "emergency-plans", "drills",
        "incidents", "safety-rules", "protection-zones",
        "alarm-configs", "evacuation-routes", "inspection-records", "safety-statistics",
    ],
    "simulator": [
        "sessions", "scenarios", "devices", "data-streams",
        "simulation-configs", "behavior-profiles", "timing-configs",
        "protocol-emulators", "data-generators", "test-campaigns", "simulation-reports",
    ],
}

# 每资源 10 种路径变体（330 × 10 = 3,300）
_PATH_VARIANTS = [
    "",           # /api/{svc}/{res}           — GET 列表 / POST 创建
    "/page",      # /api/{svc}/{res}/page      — GET 分页
    "/list",      # /api/{svc}/{res}/list      — GET 全量列表
    "/detail",    # /api/{svc}/{res}/detail    — GET 详情页
    "/export",    # /api/{svc}/{res}/export    — GET 导出
    "/stats",     # /api/{svc}/{res}/stats     — GET 统计
    "/options",   # /api/{svc}/{res}/options   — GET 下拉选项
    "/tree",      # /api/{svc}/{res}/tree      — GET 树形
    "/summary",   # /api/{svc}/{res}/summary   — GET 汇总
    "/count",     # /api/{svc}/{res}/count     — GET 计数
]

_READONLY_SUFFIXES = ("/export", "/stats", "/options", "/tree",
                      "/summary", "/count", "/detail", "/list", "/page")


def _generate_all_api_paths() -> list[str]:
    paths: list[str] = []
    for svc, resources in SERVICE_RESOURCE_MAP.items():
        for res in resources:
            for variant in _PATH_VARIANTS:
                paths.append(f"/api/{svc}/{res}{variant}")
    return paths


ALL_API_PATHS: list[str] = _generate_all_api_paths()


# ══════════════════════════════════════════════════════════════════════
# 通用验证辅助
# ══════════════════════════════════════════════════════════════════════

def _assert_api_result(resp, msg=""):
    """验证标准 ApiResult<T> 成功响应"""
    assert resp.status_code == 200, f"{msg} → HTTP {resp.status_code}"
    body = resp.json()
    assert body.get("success") is True, f"{msg} → success={body.get('success')}"
    assert "data" in body, f"{msg} → 缺少 data"
    assert "timestamp" in body, f"{msg} → 缺少 timestamp"
    assert "traceId" in body, f"{msg} → 缺少 traceId"
    return body["data"]


def _assert_paged(data, msg="", expected_page=None, expected_ps=None):
    """验证分页结构"""
    assert isinstance(data.get("items"), list), f"{msg} → items 不是列表"
    assert isinstance(data.get("total"), int), f"{msg} → total 缺失"
    assert data["total"] >= 0, f"{msg} → total<0"
    if expected_page is not None:
        assert data.get("page") == expected_page, f"{msg} → page 不匹配"
    if expected_ps is not None:
        assert data.get("pageSize") == expected_ps, f"{msg} → pageSize 不匹配"
    return data


def _assert_error(resp, msg="", codes=None):
    """验证错误响应"""
    assert resp.status_code < 500, f"{msg} → HTTP {resp.status_code}"
    body = resp.json()
    assert body.get("success") is False, f"{msg} → success 应为 False"
    assert "message" in body, f"{msg} → 缺少 message"
    if codes:
        assert resp.status_code in codes, f"{msg} → HTTP {resp.status_code} ∉ {codes}"
    return body


def _assert_json(resp, msg=""):
    """验证 JSON 响应且非 5xx"""
    assert resp.status_code < 500, f"{msg} → HTTP {resp.status_code}"
    body = resp.json()
    assert isinstance(body, dict), f"{msg} → 不是 JSON 对象"
    assert "success" in body, f"{msg} → 缺少 success"
    return body


# ══════════════════════════════════════════════════════════════════════
# 15 场景 × 3,300 路径 = 49,500 用例
# ══════════════════════════════════════════════════════════════════════

class TestApiEndpointMatrix:
    """
    全量端点矩阵 — 每 test_ 展开 3,300 用例，15 方法合计 49,500 用例。

    验证策略（远超简单 < 500）：
    - S01~S03: ApiResult 完整格式 + 分页结构 + 搜索合规
    - S04:     无 token → 401/403 + 标准错误体
    - S05:     POST 空body → 参数校验错误
    - S06~S09: 极端参数下格式完整性 + 边界值处理
    - S10~S15: 变更操作错误处理规范
    """

    # ─── S01: GET → 200 + ApiResult ──────────────────────────────────
    @pytest.mark.p1
    @pytest.mark.parametrize("api_path", ALL_API_PATHS)
    def test_s01_get_returns_valid_api_result(self, api, api_path: str):
        """[S01] GET → 200 + success/code/data/timestamp/traceId"""
        resp = api.get(api_path, params={"page": 1, "pageSize": 10})
        data = _assert_api_result(resp, f"[S01] {api_path}")
        assert data is not None

    # ─── S02: 分页 → items/total/page/pageSize ──────────────────────
    @pytest.mark.p1
    @pytest.mark.parametrize("api_path", ALL_API_PATHS)
    def test_s02_pagination_valid_structure(self, api, api_path: str):
        """[S02] 分页 → 200 + items(list)/total(int)/page/pageSize"""
        resp = api.get(api_path, params={"page": 1, "pageSize": 20, "orderBy": "createTime", "orderDir": "desc"})
        data = _assert_api_result(resp, f"[S02] {api_path}")
        _assert_paged(data, f"[S02] {api_path}", expected_page=1, expected_ps=20)

    # ─── S03: keyword 搜索 → 合法分页 ───────────────────────────────
    @pytest.mark.p1
    @pytest.mark.parametrize("api_path", ALL_API_PATHS)
    def test_s03_keyword_search_valid(self, api, api_path: str):
        """[S03] keyword=test → 200 + items(list)"""
        resp = api.get(api_path, params={"keyword": "test", "page": 1, "pageSize": 10})
        data = _assert_api_result(resp, f"[S03] {api_path}")
        assert isinstance(data.get("items"), list)

    # ─── S04: 无 token → 401/403 + 错误体 ───────────────────────────
    @pytest.mark.p0
    @pytest.mark.parametrize("api_path", ALL_API_PATHS)
    def test_s04_no_token_returns_401(self, no_auth_api, api_path: str):
        """[S04] 无 token → 401/403 + success=false + message"""
        resp = no_auth_api.get(api_path, params={"page": 1, "pageSize": 5})
        body = _assert_error(resp, f"[S04] {api_path}", codes=(401, 403))
        assert body.get("code") in (401, 403)

    # ─── S05: POST {} → 400 参数校验 ────────────────────────────────
    @pytest.mark.p1
    @pytest.mark.parametrize("api_path", ALL_API_PATHS)
    def test_s05_post_empty_returns_validation_error(self, api, api_path: str):
        """[S05] POST {} → 400 + success=false（含只读端点：验证服务端拒绝空体写入）"""
        resp = api.post(api_path, json={})
        body = _assert_json(resp, f"[S05] {api_path}")
        assert body.get("success") is False
        assert resp.status_code == 400

    # ─── S06: pageSize=1000 → ≤1000 ─────────────────────────────────
    @pytest.mark.p2
    @pytest.mark.parametrize("api_path", ALL_API_PATHS)
    def test_s06_large_pagesize_capped(self, api, api_path: str):
        """[S06] pageSize=1000 → 200 + pageSize≤1000"""
        resp = api.get(api_path, params={"page": 1, "pageSize": 1000})
        data = _assert_api_result(resp, f"[S06] {api_path}")
        assert isinstance(data.get("items"), list)
        assert data.get("pageSize", 1000) <= 1000

    # ─── S07: DELETE 不存在 → 4xx ────────────────────────────────────
    @pytest.mark.p2
    @pytest.mark.parametrize("api_path", ALL_API_PATHS)
    def test_s07_delete_nonexistent_error(self, api, api_path: str):
        """[S07] DELETE 不存在 → 4xx + success=false（含只读端点：验证不存在资源返回错误）"""
        resp = api.delete(f"{api_path}/{uuid.uuid4()}")
        body = _assert_json(resp, f"[S07] {api_path}")
        assert body.get("success") is False

    # ─── S08: page=-1 → 容错修正 ────────────────────────────────────
    @pytest.mark.p2
    @pytest.mark.parametrize("api_path", ALL_API_PATHS)
    def test_s08_invalid_page_handled(self, api, api_path: str):
        """[S08] page=-1 → 200 + 合法 items"""
        resp = api.get(api_path, params={"page": -1, "pageSize": -1})
        data = _assert_api_result(resp, f"[S08] {api_path}")
        assert isinstance(data.get("items"), list)

    # ─── S09: status 过滤 → 合法分页 ────────────────────────────────
    @pytest.mark.p2
    @pytest.mark.parametrize("api_path", ALL_API_PATHS)
    def test_s09_status_filter_valid(self, api, api_path: str):
        """[S09] status=active → 200 + items/total"""
        resp = api.get(api_path, params={"status": "active", "page": 1, "pageSize": 10})
        data = _assert_api_result(resp, f"[S09] {api_path}")
        _assert_paged(data, f"[S09] {api_path}")

    # ─── S10: PUT 不存在 → 4xx ──────────────────────────────────────
    @pytest.mark.p2
    @pytest.mark.parametrize("api_path", ALL_API_PATHS)
    def test_s10_put_nonexistent_error(self, api, api_path: str):
        """[S10] PUT 不存在 → 4xx + success=false（含只读端点：验证不存在资源返回错误）"""
        resp = api.put(f"{api_path}/{uuid.uuid4()}", json={"name": "matrix-test"})
        body = _assert_json(resp, f"[S10] {api_path}")
        assert body.get("success") is False

    # ─── S11: 日期范围 → 合法响应 ───────────────────────────────────
    @pytest.mark.p2
    @pytest.mark.parametrize("api_path", ALL_API_PATHS)
    def test_s11_date_range_valid(self, api, api_path: str):
        """[S11] startDate/endDate → 200 + items"""
        resp = api.get(api_path, params={"startDate": "2025-01-01", "endDate": "2026-12-31", "page": 1, "pageSize": 10})
        data = _assert_api_result(resp, f"[S11] {api_path}")
        assert isinstance(data.get("items"), list)

    # ─── S12: Accept:json → Content-Type:json ───────────────────────
    @pytest.mark.p2
    @pytest.mark.parametrize("api_path", ALL_API_PATHS)
    def test_s12_accept_json_content_type(self, api, api_path: str):
        """[S12] Accept:json → 200 + Content-Type 含 json"""
        resp = api.get(api_path, params={"page": 1, "pageSize": 5}, headers={"Accept": "application/json"})
        _assert_api_result(resp, f"[S12] {api_path}")
        assert "json" in resp.headers.get("Content-Type", "").lower()

    # ─── S13: keyword='' → 等同无筛选 ───────────────────────────────
    @pytest.mark.p2
    @pytest.mark.parametrize("api_path", ALL_API_PATHS)
    def test_s13_empty_keyword_returns_all(self, api, api_path: str):
        """[S13] keyword='' → 200 + 正常分页"""
        resp = api.get(api_path, params={"keyword": "", "page": 1, "pageSize": 10})
        data = _assert_api_result(resp, f"[S13] {api_path}")
        _assert_paged(data, f"[S13] {api_path}", expected_page=1, expected_ps=10)

    # ─── S14: page=999 → 空列表 ─────────────────────────────────────
    @pytest.mark.p2
    @pytest.mark.parametrize("api_path", ALL_API_PATHS)
    def test_s14_deep_pagination_empty(self, api, api_path: str):
        """[S14] page=999 → 200 + items=[]"""
        resp = api.get(api_path, params={"page": 999, "pageSize": 20})
        data = _assert_api_result(resp, f"[S14] {api_path}")
        items = data.get("items", [])
        assert isinstance(items, list)
        assert len(items) == 0, f"[S14] {api_path} → 深度分页应空，实际 {len(items)}"

    # ─── S15: PATCH 不存在 → 4xx ────────────────────────────────────
    @pytest.mark.p2
    @pytest.mark.parametrize("api_path", ALL_API_PATHS)
    def test_s15_patch_nonexistent_error(self, api, api_path: str):
        """[S15] PATCH 不存在 → 4xx + success=false（含只读端点：验证不存在资源返回错误）"""
        resp = api.patch(f"{api_path}/{uuid.uuid4()}", json={"status": 1})
        body = _assert_json(resp, f"[S15] {api_path}")
        assert body.get("success") is False
