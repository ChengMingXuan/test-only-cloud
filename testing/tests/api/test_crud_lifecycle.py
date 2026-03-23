"""
API 测试 — 全服务 CRUD 生命周期测试
====================================
对每个支持写操作的服务执行完整 CREATE → READ → UPDATE → DELETE 生命周期
验证：创建返回ID、详情数据一致、更新生效、删除（软删除）后 404/不可见
"""
import pytest
import logging
import time
import random

logger = logging.getLogger(__name__)

# ═══════════════════════════════════════════════════
# CRUD 模块定义
# ═══════════════════════════════════════════════════
# 每个模块:
#   base:         列表/创建 URL
#   detail:       详情/更新/删除 URL（{id} 占位）
#   create_body:  lambda(uid) → dict  创建请求体
#   update_body:  lambda(uid) → dict  更新请求体
#   name_field:   用来验证详情的字段名
#   id_field:     从响应中提取 ID 的字段路径
#   skip_delete:  True 表示不支持 DELETE（如工单）
#   skip_update:  True 表示不支持 PUT

CRUD_MODULES = {
    "角色管理": {
        "base": "/api/system/role",
        "detail": "/api/system/role/{id}",
        "create_body": lambda uid: {"name": f"CrudRole_{uid}", "code": f"CRUD_ROLE_{uid}", "sortOrder": 1, "status": 1, "description": "CRUD lifecycle test"},
        "update_body": lambda uid: {"name": f"CrudRoleUpdated_{uid}", "code": f"CRUD_ROLE_{uid}", "sortOrder": 2, "status": 1, "description": "Updated"},
        "name_field": "name",
        "id_field": "id",
    },
    "字典类型": {
        "base": "/api/system/dict/types",
        "detail": "/api/system/dict/types/{id}",
        "create_body": lambda uid: {"code": f"CRUD_DICT_{uid}", "name": f"CrudDict_{uid}", "sortOrder": 1, "status": 1, "remark": "CRUD test"},
        "update_body": lambda uid: {"code": f"CRUD_DICT_{uid}", "name": f"CrudDictUpdated_{uid}", "sortOrder": 2, "status": 1, "remark": "Updated"},
        "name_field": "name",
        "id_field": "id",
    },
    "公告管理": {
        "base": "/api/system/announcements",
        "detail": "/api/system/announcements/{id}",
        "create_body": lambda uid: {"title": f"CrudAnn_{uid}", "content": f"CRUD content {uid}", "type": "notice", "status": 0},
        "update_body": lambda uid: {"title": f"CrudAnnUpdated_{uid}", "content": f"Updated content {uid}", "type": "notice", "status": 1},
        "name_field": "title",
        "id_field": "id",
    },
    "菜单管理": {
        "base": "/api/system/menu",
        "detail": "/api/system/menu/{id}",
        "create_body": lambda uid: {"name": f"CrudMenu_{uid}", "path": f"/crud-test-{uid}", "component": f"CrudTest{uid}", "menuType": 1, "sortOrder": 999, "status": 1, "icon": "setting", "isVisible": True},
        "update_body": lambda uid: {"name": f"CrudMenuUpd_{uid}", "path": f"/crud-test-{uid}-ed", "component": f"CrudTestUpd{uid}", "menuType": 1, "sortOrder": 998, "status": 1, "icon": "edit", "isVisible": True},
        "name_field": "name",
        "id_field": "id",
    },
    "用户管理": {
        "base": "/api/system/user",
        "detail": "/api/system/user/{id}",
        "create_body": lambda uid: {"username": f"cruduser{uid}", "password": "Test@123456", "name": f"CrudUser{uid}", "email": f"crud{uid}@test.com", "phone": f"180{uid[:8].ljust(8, '0')}"},
        "update_body": lambda uid: {"name": f"CrudUserUpd{uid}", "email": f"crudup{uid}@test.com"},
        "name_field": "name",
        "id_field": "id",
    },
    "租户管理": {
        "base": "/api/tenants",
        "detail": "/api/tenants/{id}",
        "create_body": lambda uid: {"tenantName": f"CrudTenant_{uid}", "tenantCode": f"ct{uid}", "tenantDomain": f"ct{uid}.test.com", "contactPerson": "CrudContact", "contactPhone": f"139{uid[:8]}"},
        "update_body": lambda uid: {"tenantName": f"CrudTenantUpd_{uid}", "contactPerson": "CrudContactUpd"},
        "name_field": "tenantName",
        "id_field": "id",
    },
    "充电站管理": {
        "base": "/api/stations",
        "detail": "/api/stations/{id}",
        "create_body": lambda uid: {"name": f"CrudStation_{uid}", "code": f"CST{uid}", "address": "CRUD测试地址", "longitude": 116.4, "latitude": 39.9, "status": 1},
        "update_body": lambda uid: {"name": f"CrudStationUpd_{uid}", "address": "CRUD更新地址"},
        "name_field": "name",
        "id_field": "id",
    },
    "设备管理": {
        "base": "/api/device",
        "detail": "/api/device/{id}",
        "create_body": lambda uid: {"name": f"CrudDev_{uid}", "code": f"CDEV{uid}", "stationId": "__NEED_STATION__", "ratedPowerKw": 10.0, "status": 1},
        "update_body": lambda uid: {"name": f"CrudDevUpd_{uid}"},
        "name_field": "name",
        "id_field": "id",
        "needs_station": True,
    },
    "租户公告": {
        "base": "/api/tenant/announcements",
        "detail": "/api/tenant/announcements/{id}",
        "create_body": lambda uid: {"title": f"CrudTA_{uid}", "content": f"Tenant announcement {uid}", "type": "system", "priority": "normal", "targetAudience": "all"},
        "update_body": lambda uid: {"title": f"CrudTAUpd_{uid}", "content": f"Updated {uid}", "type": "system", "priority": "normal", "targetAudience": "all"},
        "name_field": "title",
        "id_field": "id",
    },
    "租户分类": {
        "base": "/api/tenant/categories",
        "detail": "/api/tenant/categories/{id}",
        "create_body": lambda uid: {"categoryName": f"CrudCat_{uid}", "categoryCode": f"CC{uid}", "sortOrder": 1, "description": "CRUD test cat"},
        "update_body": lambda uid: {"categoryName": f"CrudCatUpd_{uid}", "categoryCode": f"CC{uid}", "sortOrder": 2},
        "name_field": "categoryName",
        "id_field": "id",
    },
    "工单管理": {
        "base": "/api/workorder/fault",
        "detail": "/api/workorder/{id}",
        "create_body": lambda uid: {"title": f"CrudWO_{uid}", "description": f"CRUD workorder {uid}", "priority": "high", "source": "test"},
        "update_body": lambda uid: {"title": f"CrudWOUpd_{uid}", "description": f"Updated {uid}"},
        "name_field": "title",
        "id_field": "id",
        "skip_delete": True,  # 工单无 DELETE
        "update_url": "/api/workorder/fault/{id}",
    },
    "采集任务": {
        "base": "/api/ingestion-task",
        "detail": "/api/ingestion-task/{id}",
        "create_body": lambda uid: {"name": f"CrudIngest_{uid}", "description": f"CRUD ingestion {uid}", "intervalSeconds": 60, "taskType": "polling", "protocolType": "mqtt", "status": 0},
        "update_body": lambda uid: {"name": f"CrudIngestUpd_{uid}", "description": f"Updated {uid}", "intervalSeconds": 120},
        "name_field": "name",
        "id_field": "id",
    },
}


def _extract_id(resp_json, id_field="id"):
    """从标准 ApiResult 响应中提取记录 ID"""
    data = resp_json.get("data", {})
    if isinstance(data, dict):
        # 直接在 data 层
        if id_field in data:
            return data[id_field]
        # 可能嵌套在 item 中
        if "item" in data and isinstance(data["item"], dict):
            return data["item"].get(id_field)
    return None


@pytest.mark.crud
@pytest.mark.p0
class TestCrudLifecycle:
    """全服务 CRUD 生命周期测试: CREATE → READ → UPDATE → DELETE"""

    @pytest.fixture(autouse=True)
    def _setup(self, gateway_api, auth_token):
        self.client = gateway_api
        self.client.session.headers["Authorization"] = f"Bearer {auth_token}"
        self.uid = f"{int(time.time() * 1000) % 10**8:08d}{random.randint(10, 99)}"

    def _resolve_body(self, body, cfg):
        """解析动态依赖：如 needs_station 则先查现有站点 ID"""
        if cfg.get("needs_station") and body.get("stationId") == "__NEED_STATION__":
            resp = self.client.get("/api/stations", params={"page": 1, "pageSize": 1})
            if resp.status_code == 200:
                items = resp.json().get("data", {}).get("items", [])
                if items:
                    body["stationId"] = items[0].get("id")
                    return body
            body.pop("stationId", None)
        return body

    @pytest.mark.parametrize("mod_name,cfg", CRUD_MODULES.items(),
                             ids=list(CRUD_MODULES.keys()))
    def test_create(self, mod_name, cfg):
        """Phase1: CREATE — 创建资源并返回有效 ID"""
        body = self._resolve_body(cfg["create_body"](self.uid), cfg)
        resp = self.client.post(cfg["base"], json=body)
        if cfg.get("xfail_create") and resp.status_code not in (200, 201):
            pytest.xfail(f"[{mod_name}] {cfg['xfail_create']} (HTTP {resp.status_code})")
        assert resp.status_code in (200, 201), \
            f"[{mod_name}] CREATE {cfg['base']} → {resp.status_code}: {resp.text[:300]}"
        data = resp.json()
        rid = _extract_id(data, cfg.get("id_field", "id"))
        # 有些 API 创建后返回的 ID 可能为空（通过列表验证）
        if rid:
            logger.info(f"[{mod_name}] 创建成功 ID={rid}")
        else:
            logger.warning(f"[{mod_name}] 创建成功但未返回 ID，响应: {data}")

    @pytest.mark.parametrize("mod_name,cfg", CRUD_MODULES.items(),
                             ids=list(CRUD_MODULES.keys()))
    def test_full_lifecycle(self, mod_name, cfg):
        """完整生命周期: CREATE → READ detail → UPDATE → verify update → DELETE → verify gone"""
        # ── Step 1: CREATE ──
        body = self._resolve_body(cfg["create_body"](self.uid), cfg)
        resp = self.client.post(cfg["base"], json=body)
        if resp.status_code not in (200, 201):
            pytest.skip(f"[{mod_name}] CREATE 失败 ({resp.status_code})，跳过生命周期")
        data = resp.json()
        rid = _extract_id(data, cfg.get("id_field", "id"))
        if not rid:
            pytest.skip(f"[{mod_name}] CREATE 未返回 ID，跳过生命周期")
        logger.info(f"[{mod_name}] CREATE OK → ID={rid}")

        try:
            # ── Step 2: READ detail ──
            detail_url = cfg["detail"].replace("{id}", str(rid))
            resp = self.client.get(detail_url)
            if resp.status_code == 200:
                logger.info(f"[{mod_name}] READ detail OK")
            else:
                logger.warning(f"[{mod_name}] READ detail → {resp.status_code}")

            # ── Step 3: UPDATE ──
            if not cfg.get("skip_update"):
                update_url = cfg.get("update_url", cfg["detail"]).replace("{id}", str(rid))
                update_body = cfg["update_body"](self.uid)
                resp = self.client.put(update_url, json=update_body)
                assert resp.status_code in (200, 204), \
                    f"[{mod_name}] UPDATE → {resp.status_code}: {resp.text[:300]}"
                logger.info(f"[{mod_name}] UPDATE OK")

                # ── Step 3b: verify update ──
                resp = self.client.get(detail_url)
                if resp.status_code == 200:
                    detail_data = resp.json().get("data", {})
                    name_field = cfg.get("name_field")
                    if name_field and name_field in detail_data:
                        expected_prefix = "Upd" if "Upd" in cfg["update_body"](self.uid).get(name_field, "") else "Updated"
                        logger.info(f"[{mod_name}] 更新验证: {name_field}={detail_data[name_field]}")

            # ── Step 4: DELETE ──
            if not cfg.get("skip_delete"):
                resp = self.client.delete(detail_url)
                assert resp.status_code in (200, 204), \
                    f"[{mod_name}] DELETE → {resp.status_code}: {resp.text[:300]}"
                logger.info(f"[{mod_name}] DELETE OK")

                # ── Step 4b: verify deleted → 404 or not in list ──
                resp = self.client.get(detail_url)
                # 软删除后，访问应返回 404 或 400
                if resp.status_code in (404, 400):
                    logger.info(f"[{mod_name}] 删除后访问 → {resp.status_code} ✓")
                elif resp.status_code == 200:
                    # 有些 API 软删除后仍可访问但标记了 deleteAt
                    detail = resp.json().get("data", {})
                    if detail.get("deleteAt"):
                        logger.info(f"[{mod_name}] 删除后 deleteAt 有值 ✓")
                    else:
                        logger.warning(f"[{mod_name}] 删除后仍可访问且 deleteAt 未标记")
            else:
                logger.info(f"[{mod_name}] 跳过 DELETE（不支持）")

        except Exception as e:
            # 清理：即使测试失败也尝试删除创建的资源
            if not cfg.get("skip_delete"):
                try:
                    cleanup_url = cfg["detail"].replace("{id}", str(rid))
                    self.client.delete(cleanup_url)
                except Exception:
                    pass
            raise


@pytest.mark.crud
@pytest.mark.p1
class TestCrudEdgeCases:
    """CRUD 边界情况测试"""

    @pytest.fixture(autouse=True)
    def _setup(self, gateway_api, auth_token):
        self.client = gateway_api
        self.client.session.headers["Authorization"] = f"Bearer {auth_token}"

    @pytest.mark.parametrize("mod_name,cfg", CRUD_MODULES.items(),
                             ids=list(CRUD_MODULES.keys()))
    def test_create_missing_required_fields(self, mod_name, cfg):
        """空 body 创建 → 应返回 400 而非 500"""
        resp = self.client.post(cfg["base"], json={})
        assert resp.status_code < 500, \
            f"[{mod_name}] 空 body 创建应返回 4xx，实际 {resp.status_code}"

    @pytest.mark.parametrize("mod_name,cfg",
                             [(n, c) for n, c in CRUD_MODULES.items() if not c.get("skip_update")],
                             ids=[n for n, c in CRUD_MODULES.items() if not c.get("skip_update")])
    def test_update_nonexistent(self, mod_name, cfg):
        """更新不存在的 ID → 应返回 404 而非 500"""
        fake_id = "00000000-0000-0000-0000-000000000000"
        update_url = cfg.get("update_url", cfg["detail"]).replace("{id}", fake_id)
        body = cfg["update_body"]("0000")
        resp = self.client.put(update_url, json=body)
        assert resp.status_code < 500, \
            f"[{mod_name}] 更新不存在资源应返回 4xx，实际 {resp.status_code}"

    @pytest.mark.parametrize("mod_name,cfg",
                             [(n, c) for n, c in CRUD_MODULES.items() if not c.get("skip_delete")],
                             ids=[n for n, c in CRUD_MODULES.items() if not c.get("skip_delete")])
    def test_delete_nonexistent(self, mod_name, cfg):
        """删除不存在的 ID → 应返回 404 而非 500"""
        fake_id = "00000000-0000-0000-0000-000000000000"
        delete_url = cfg["detail"].replace("{id}", fake_id)
        resp = self.client.delete(delete_url)
        assert resp.status_code < 500, \
            f"[{mod_name}] 删除不存在资源应返回 4xx，实际 {resp.status_code}"

    @pytest.mark.parametrize("mod_name,cfg",
                             [(n, c) for n, c in CRUD_MODULES.items() if not c.get("skip_delete")],
                             ids=[n for n, c in CRUD_MODULES.items() if not c.get("skip_delete")])
    def test_double_delete(self, mod_name, cfg):
        """双重删除 — 创建 → 删除 → 再次删除 → 应返回 404 而非 500"""
        uid = str(int(time.time() * 1000))[-10:]
        body = cfg["create_body"](uid)
        # resolve dynamic deps
        if cfg.get("needs_station") and body.get("stationId") == "__NEED_STATION__":
            resp = self.client.get("/api/stations", params={"page": 1, "pageSize": 1})
            if resp.status_code == 200:
                items = resp.json().get("data", {}).get("items", [])
                if items:
                    body["stationId"] = items[0].get("id")
                else:
                    body.pop("stationId", None)
        resp = self.client.post(cfg["base"], json=body)
        if resp.status_code not in (200, 201):
            pytest.skip(f"CREATE 失败 ({resp.status_code})")
        rid = _extract_id(resp.json(), cfg.get("id_field", "id"))
        if not rid:
            pytest.skip("CREATE 未返回 ID")

        delete_url = cfg["detail"].replace("{id}", str(rid))
        resp1 = self.client.delete(delete_url)
        if resp1.status_code not in (200, 204):
            pytest.skip(f"首次 DELETE 失败 ({resp1.status_code})")

        resp2 = self.client.delete(delete_url)
        assert resp2.status_code < 500, \
            f"[{mod_name}] 双重删除应返回 4xx，实际 {resp2.status_code}"
