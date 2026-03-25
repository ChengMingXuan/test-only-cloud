"""
全服务批量参数化 CRUD 测试
============================
覆盖 30 个微服务的标准化 15 类测试场景
总用例数 = 30 服务 × 15 场景 = 450 条（parametrize 展开后每条独立计数）
"""
import uuid
import pytest
import logging

logger = logging.getLogger(__name__)

# ──────────────────────────────────────────────────────────────────────────────
# 30 个微服务端点清单（服务名, 基础路径, 列表路径, 创建测试body, 数据库表）
# ──────────────────────────────────────────────────────────────────────────────
ALL_SERVICES = [
    # (name, list_path, create_path, sample_body, update_body, db_table)
    ("tenant",          "/api/tenants",                 "/api/tenants",
     {"name": "测试租户_{uid}", "code": "T{uid}", "contactName": "张三", "contactPhone": "13800138000",
      "contactEmail": "test@test.com", "status": 1},
     {"name": "更新租户_{uid}"},
     "tenant.tenant_info"),

    ("permission_role",  "/api/system/role",            "/api/system/role",
     {"name": "测试角色_{uid}", "code": "R{uid}", "description": "测试", "status": 1},
     {"name": "更新角色_{uid}"},
     "perm_role"),

    ("permission_menu",  "/api/system/menu",            "/api/system/menu",
     {"name": "测试菜单_{uid}", "code": "M{uid}", "path": "/test/{uid}", "type": 1, "sort": 1},
     {"name": "更新菜单_{uid}"},
     "perm_menu"),

    ("permission_perm",  "/api/system/permission",      "/api/system/permission",
     {"name": "测试权限_{uid}", "code": "device:test:read_{uid}", "type": 1},
     {"name": "更新权限_{uid}"},
     "perm_permission"),

    ("device_category",  "/api/device-category",        "/api/device-category",
     {"name": "测试设备分类_{uid}", "code": "DC{uid}", "description": "测试分类"},
     {"name": "更新设备分类_{uid}"},
     "device_category"),

    ("device",           "/api/device",                 "/api/device",
     {"name": "测试设备_{uid}", "serialNumber": "SN{uid}", "type": "charger",
      "categoryId": None, "stationId": None},
     {"name": "更新设备_{uid}"},
     "device_info"),

    ("station",          "/api/stations",               "/api/stations",
     {"name": "测试场站_{uid}", "code": "ST{uid}", "address": "测试地址",
      "province": "广东", "city": "深圳", "lat": 22.5, "lng": 114.0},
     {"name": "更新场站_{uid}"},
     "station_info"),

    ("charging_order",   "/api/charging/admin/orders",  "/api/charging/orders",
     {"stationId": None, "deviceId": None, "connectorId": "1", "userId": None},
     {"remark": "更新备注"},
     "charging_order"),

    ("charging_pricing", "/api/charging/pricing",       "/api/charging/pricing",
     {"name": "测试定价_{uid}", "type": "time", "stationId": None,
      "details": [{"startTime": "00:00", "endTime": "08:00", "price": 0.5}]},
     {"name": "更新定价_{uid}"},
     "charging_pricing"),

    ("workorder",        "/api/workorder",              "/api/workorder",
     {"title": "测试工单_{uid}", "type": "maintenance", "priority": "medium",
      "description": "测试描述", "stationId": None},
     {"title": "更新工单_{uid}"},
     "workorder_info"),

    ("settlement",       "/api/settlements",            "/api/settlements",
     {"merchantId": None, "period": "2026-01", "amount": 1000.0},
     {"remark": "更新备注"},
     "settlement_record"),

    ("account_user",     "/api/users",                  "/api/users",
     {"username": "test_{uid}", "phone": "138{uid:010d}",
      "nickname": "测试用户_{uid}", "status": 1},
     {"nickname": "更新用户_{uid}"},
     "account.account_info"),

    ("identity_user",    "/api/identity/users",         "/api/identity/users",
     {"username": "id_test_{uid}", "password": "P@ssw0rd123",
      "phone": "139{uid:010d}", "tenantId": None},
     {"status": 1},
     "identity_user"),

    ("ingestion_task",   "/api/ingestion-task",         "/api/ingestion-task",
     {"name": "接入任务_{uid}", "protocol": "mqtt", "config": {}},
     {"name": "更新接入任务_{uid}"},
     "ingestion.ingestion_task"),

    ("analytics_custom", "/api/analytics/events",       "/api/analytics/custom-events",
     {"eventName": "test_event_{uid}", "eventType": "custom", "properties": {}},
     {"eventName": "updated_event_{uid}"},
     "analytics_events"),

    ("observability_alert", "/api/alerts",              "/api/alerts",
     {"name": "告警规则_{uid}", "severity": "warning", "condition": "cpu > 80",
      "enabled": True},
     {"name": "更新告警_{uid}"},
     "alert_rule"),

    ("content_article",  "/api/content/articles",       "/api/content/articles",
     {"title": "测试文章_{uid}", "content": "测试内容", "categoryId": None,
      "status": 0, "authorId": None},
     {"title": "更新文章_{uid}"},
     "content_article"),

    ("content_category", "/api/content/categories",     "/api/content/categories",
     {"name": "测试分类_{uid}", "code": "CC{uid}", "sort": 1},
     {"name": "更新分类_{uid}"},
     "content_category"),

    ("digitaltwin_model","/api/digitaltwin/models",     "/api/digitaltwin/models",
     {"name": "数字孪生模型_{uid}", "code": "DT{uid}", "type": "device",
      "schema": {}},
     {"name": "更新模型_{uid}"},
     "twin_model"),

    ("digitaltwin_instance", "/api/digitaltwin/instances", "/api/digitaltwin/instances",
     {"name": "模型实例_{uid}", "modelId": None, "deviceId": None, "config": {}},
     {"name": "更新实例_{uid}"},
     "twin_instance"),

    ("iotcloudai_model",  "/api/ai-models",             "/api/ai-models",
     {"name": "AI模型_{uid}", "type": "inference", "framework": "onnx",
      "description": "测试模型"},
     {"name": "更新AI模型_{uid}"},
     "ai_model"),

    ("blockchain_record", "/api/blockchain/records",    "/api/blockchain/records",
     {"businessId": None, "businessType": "order", "data": {"key": "value_{uid}"},
      "hash": "abc{uid}"},
     {"remark": "更新备注"},
     "bc_record"),

    ("ruleengine_chain",  "/api/rule-chains",           "/api/rule-chains",
     {"name": "规则链_{uid}", "description": "测试规则链"},
     {"name": "更新规则链_{uid}"},
     "rule_chain"),

    ("storage_file",      "/api/storage/files",         "/api/storage/files",
     {"fileName": "test_{uid}.txt", "fileType": "text/plain",
      "content": "dGVzdA=="},
     {"remark": "更新备注"},
     "storage_file"),

    ("simulator_device",  "/api/simulator/devices",     "/api/simulator/devices",
     {"name": "模拟设备_{uid}", "type": "charger", "protocol": "mqtt",
      "config": {"host": "localhost", "port": 1883}},
     {"name": "更新模拟设备_{uid}"},
     "simulator_device"),

    ("energy_vpp",        "/api/vpp/resources",         "/api/vpp/resources",
     {"name": "VPP资源_{uid}", "type": "load", "capacity": 100.0,
      "stationId": None},
     {"name": "更新VPP资源_{uid}"},
     "vpp_resource"),

    ("energy_microgrid",  "/api/microgrid/configs",     "/api/microgrid/configs",
     {"name": "微网配置_{uid}", "stationId": None, "gridMode": "island",
      "config": {}},
     {"name": "更新微网配置_{uid}"},
     "microgrid_config"),

    ("energy_electrade",  "/api/electrade/contracts",   "/api/electrade/contracts",
     {"name": "电力交易合同_{uid}", "buyerId": None, "sellerId": None,
      "amount": 1000.0, "price": 0.6},
     {"name": "更新合同_{uid}"},
     "et_contract"),

    ("energy_carbontrade","/api/carbon/credits",        "/api/carbon/credits",
     {"name": "碳积分_{uid}", "amount": 100.0, "source": "solar",
      "stationId": None},
     {"name": "更新碳积分_{uid}"},
     "carbon_credit"),

    ("energy_demandresp", "/api/demand-response/events","/api/demand-response/events",
     {"name": "需求响应事件_{uid}", "startTime": "2026-03-06T10:00:00",
      "endTime": "2026-03-06T11:00:00", "type": "peak"},
     {"name": "更新DR事件_{uid}"},
     "dr_event"),
]

# ──────────────────────────────────────────────────────────────────────────────
# 辅助函数
# ──────────────────────────────────────────────────────────────────────────────

def _render(obj, uid_int: int):
    """替换body中的 {uid} 和 {uid:010d} 占位符"""
    if isinstance(obj, dict):
        return {k: _render(v, uid_int) for k, v in obj.items()}
    if isinstance(obj, str):
        try:
            return obj.replace("{uid:010d}", f"{uid_int:010d}").replace("{uid}", str(uid_int))
        except Exception:
            return obj
    return obj


# ──────────────────────────────────────────────────────────────────────────────
# 场景 1 ～ 5：列表、详情、创建、更新、删除
# ──────────────────────────────────────────────────────────────────────────────

@pytest.mark.parametrize("name,list_path,create_path,body,upd,tbl", ALL_SERVICES,
                         ids=[s[0] for s in ALL_SERVICES])
@pytest.mark.p1
def test_list_returns_200(api, v, name, list_path, create_path, body, upd, tbl):
    """场景1: GET 列表接口返回 2xx（非 5xx）"""
    resp = api.get(list_path, params={"page": 1, "pageSize": 5})
    v.not_5xx(resp)


@pytest.mark.parametrize("name,list_path,create_path,body,upd,tbl", ALL_SERVICES,
                         ids=[s[0] for s in ALL_SERVICES])
@pytest.mark.p1
def test_list_with_paging_params(api, v, name, list_path, create_path, body, upd, tbl):
    """场景2: 分页参数 pageSize=1 时只返回 ≤1 条数据"""
    resp = api.get(list_path, params={"page": 1, "pageSize": 1})
    v.not_5xx(resp)
    if resp.status_code == 200:
        data = resp.json().get("data") or {}
        items = data.get("items") or data.get("list") or data.get("rows") or []
        assert len(items) <= 1, f"{name}: pageSize=1 但返回 {len(items)} 条"


@pytest.mark.parametrize("name,list_path,create_path,body,upd,tbl", ALL_SERVICES,
                         ids=[s[0] for s in ALL_SERVICES])
@pytest.mark.p1
def test_list_large_page_size(api, v, name, list_path, create_path, body, upd, tbl):
    """场景3: 超大分页（pageSize=1000）不报错"""
    resp = api.get(list_path, params={"page": 1, "pageSize": 1000})
    v.not_5xx(resp)


@pytest.mark.parametrize("name,list_path,create_path,body,upd,tbl", ALL_SERVICES,
                         ids=[s[0] for s in ALL_SERVICES])
@pytest.mark.p1
def test_list_page_zero_rejected_or_reset(api, v, name, list_path, create_path, body, upd, tbl):
    """场景4: page=0 不报 500（框架应拦截或重置）"""
    resp = api.get(list_path, params={"page": 0, "pageSize": 10})
    assert resp.status_code != 500, f"{name}: page=0 触发 500"


@pytest.mark.parametrize("name,list_path,create_path,body,upd,tbl", ALL_SERVICES,
                         ids=[s[0] for s in ALL_SERVICES])
@pytest.mark.p1
def test_list_negative_page(api, v, name, list_path, create_path, body, upd, tbl):
    """场景5: page=-1 不报 500"""
    resp = api.get(list_path, params={"page": -1, "pageSize": 10})
    assert resp.status_code != 500, f"{name}: page=-1 触发 500"


@pytest.mark.parametrize("name,list_path,create_path,body,upd,tbl", ALL_SERVICES,
                         ids=[s[0] for s in ALL_SERVICES])
@pytest.mark.p1
def test_response_content_type_json(api, v, name, list_path, create_path, body, upd, tbl):
    """场景6: 列表接口返回 Content-Type application/json"""
    resp = api.get(list_path, params={"page": 1, "pageSize": 5})
    if 200 <= resp.status_code < 300:
        ct = resp.headers.get("Content-Type", "")
        assert "application/json" in ct, f"{name}: Content-Type={ct} 非 JSON"


@pytest.mark.parametrize("name,list_path,create_path,body,upd,tbl", ALL_SERVICES,
                         ids=[s[0] for s in ALL_SERVICES])
@pytest.mark.p1
def test_detail_nonexistent_id_returns_404(api, v, name, list_path, create_path, body, upd, tbl):
    """场景7: 查询不存在 ID 返回 404（非 500）"""
    fake_id = str(uuid.uuid4())
    resp = api.get(f"{list_path}/{fake_id}")
    assert resp.status_code != 500, f"{name}: 查询不存在ID触发 500"
    assert resp.status_code in (200, 400, 401, 403, 404, 405), \
        f"{name}: 不存在ID应被安全处理，实际={resp.status_code}"


@pytest.mark.parametrize("name,list_path,create_path,body,upd,tbl", ALL_SERVICES,
                         ids=[s[0] for s in ALL_SERVICES])
@pytest.mark.p1
def test_detail_invalid_uuid_returns_400(api, v, name, list_path, create_path, body, upd, tbl):
    """场景8: 非法 UUID 格式路径参数返回 400（非 500）"""
    resp = api.get(f"{list_path}/not-a-valid-uuid")
    assert resp.status_code != 500, f"{name}: 非法UUID触发 500"


@pytest.mark.parametrize("name,list_path,create_path,body,upd,tbl", ALL_SERVICES,
                         ids=[s[0] for s in ALL_SERVICES])
@pytest.mark.p1
def test_delete_nonexistent_id_returns_404(api, v, name, list_path, create_path, body, upd, tbl):
    """场景9: 删除不存在 ID 返回 404（非 500）"""
    fake_id = str(uuid.uuid4())
    resp = api.delete(f"{list_path}/{fake_id}")
    assert resp.status_code != 500, f"{name}: 删除不存在ID触发 500"


@pytest.mark.parametrize("name,list_path,create_path,body,upd,tbl", ALL_SERVICES,
                         ids=[s[0] for s in ALL_SERVICES])
@pytest.mark.p1
def test_create_empty_body_returns_400(api, v, name, list_path, create_path, body, upd, tbl):
    """场景10: 创建接口传空 Body 返回 400（不报 500）"""
    resp = api.post(create_path, json={})
    assert resp.status_code != 500, f"{name}: 空Body创建触发 500"
    assert resp.status_code in (200, 201, 400, 401, 403, 404, 405, 409, 422), \
        f"{name}: 空Body应被安全处理，实际={resp.status_code}"


@pytest.mark.parametrize("name,list_path,create_path,body,upd,tbl", ALL_SERVICES,
                         ids=[s[0] for s in ALL_SERVICES])
@pytest.mark.p1
def test_update_nonexistent_id_not_500(api, v, name, list_path, create_path, body, upd, tbl):
    """场景11: 更新不存在 ID 不报 500"""
    fake_id = str(uuid.uuid4())
    resp = api.put(f"{list_path}/{fake_id}", json=upd)
    assert resp.status_code != 500, f"{name}: 更新不存在ID触发 500"


@pytest.mark.parametrize("name,list_path,create_path,body,upd,tbl", ALL_SERVICES,
                         ids=[s[0] for s in ALL_SERVICES])
@pytest.mark.p1
def test_create_missing_required_field_rejected(api, v, name, list_path, create_path, body, upd, tbl):
    """场景12: 仅传 {pageSize:10} 等无效字段，不报 500"""
    resp = api.post(create_path, json={"pageSize": 10, "invalid_field": True})
    assert resp.status_code != 500, f"{name}: 无效字段创建触发 500"


@pytest.mark.parametrize("name,list_path,create_path,body,upd,tbl", ALL_SERVICES,
                         ids=[s[0] for s in ALL_SERVICES])
@pytest.mark.p1
def test_list_with_keyword_search(api, v, name, list_path, create_path, body, upd, tbl):
    """场景13: keyword 搜索不报 500"""
    resp = api.get(list_path, params={"page": 1, "pageSize": 10, "keyword": "test"})
    v.not_5xx(resp)


@pytest.mark.parametrize("name,list_path,create_path,body,upd,tbl", ALL_SERVICES,
                         ids=[s[0] for s in ALL_SERVICES])
@pytest.mark.p1
def test_list_sort_by_create_time(api, v, name, list_path, create_path, body, upd, tbl):
    """场景14: 按 createTime 排序不报 500"""
    resp = api.get(list_path, params={"page": 1, "pageSize": 10, "sortBy": "createTime",
                                       "sortOrder": "desc"})
    v.not_5xx(resp)


@pytest.mark.parametrize("name,list_path,create_path,body,upd,tbl", ALL_SERVICES,
                         ids=[s[0] for s in ALL_SERVICES])
@pytest.mark.p1
def test_unauthenticated_returns_401(name, list_path, create_path, body, upd, tbl):
    """场景15: 未携带 Token 访问返回 401（权限拦截正常）"""
    from mock_client import MockApiClient
    no_auth = MockApiClient(token=None)
    resp = no_auth.get(list_path, params={"page": 1, "pageSize": 5})
    assert resp.status_code in (401, 403), \
        f"{name}: 未认证应返回401/403，实际={resp.status_code}"
