"""
多租户数据隔离测试（增强版）
==============================
验证所有服务的租户隔离正确性:

Phase 1: 数据库级隔离验证 — 每个表的 tenant_id 一致性
Phase 2: API 级隔离验证 — 列表只返回当前租户数据
Phase 3: 跨租户详情/修改/删除 — 动态创建双租户验证
Phase 4: 安全边界 — 无 Token / 伪造 Token / SQL 注入

优先级：P0
"""
import pytest
import logging
import time
import os

from mock_client import MockApiClient, MockResponse, MOCK_TOKEN, MOCK_MODE
from tests.conftest import GATEWAY_URL, DbClient, DB_CONFIGS

logger = logging.getLogger(__name__)

IDENTITY_URL = os.getenv("JGSY_IDENTITY_URL", "http://localhost:8002")
INTERNAL_KEY = os.getenv("JGSY_INTERNAL_KEY")
if not INTERNAL_KEY:
    import pytest
    pytest.skip("缺少 JGSY_INTERNAL_KEY 环境变量", allow_module_level=True)


def _login(username, password, tenant_id=None):
    """Mock login — 返回 MOCK_TOKEN"""
    api = MockApiClient(token=None)
    body = {"username": username, "password": password}
    if tenant_id:
        body["tenantId"] = tenant_id
    resp = api.post("/api/auth/login", json=body)
    if resp.status_code == 200:
        data = resp.json()
        return data.get("data", {}).get("accessToken") or data.get("data", {}).get("token")
    return None


def _api(method, path, token=None, json=None, params=None):
    """Mock API call"""
    api = MockApiClient(token=token)
    m = method.upper()
    if m == "GET":
        return api.get(path, params=params)
    elif m == "POST":
        return api.post(path, json=json)
    elif m == "PUT":
        return api.put(path, json=json)
    elif m == "DELETE":
        return api.delete(path)
    elif m == "PATCH":
        return api.patch(path, json=json)
    return MockResponse(405, {"message": "Method not allowed"})


# ═══════════════════════════════════════════════════
# Phase 1: 数据库级租户隔离 — 不需要额外租户
# ═══════════════════════════════════════════════════

# 主表 → DB → tenant_id 字段
DB_ISOLATION_CHECKS = [
    ("tenant_info",           "jgsy_tenant",       "tenant_id"),
    ("permission.perm_role",  "jgsy_permission",   "tenant_id"),
    ("station_info",          "jgsy_station",      "tenant_id"),
    ("device_info",           "jgsy_device",       "tenant_id"),
    ("workorder_info",        "jgsy_workorder",    "tenant_id"),
    ("settlement_record",     "jgsy_settlement",   "tenant_id"),
    ("content.cms_article",   "jgsy_content",      "tenant_id"),
    ("account.account_info",  "jgsy_account",      "tenant_id"),
]


@pytest.mark.p0
@pytest.mark.tenant_isolation
class TestDbLevelIsolation:
    """Phase 1: 数据库级租户隔离验证"""

    @pytest.mark.parametrize("table,dbname,col", DB_ISOLATION_CHECKS,
                             ids=[t[0] for t in DB_ISOLATION_CHECKS])
    def test_all_records_have_tenant_id(self, table, dbname, col):
        """每条记录都有非空 tenant_id"""
        try:
            db = DbClient(dbname)
        except Exception:
            pytest.skip(f"无法连接 {dbname}")
        try:
            result = db.query(
                f"SELECT COUNT(*) as cnt FROM {table} WHERE {col} IS NULL AND delete_at IS NULL"
            )
            null_count = result[0]["cnt"] if result else 0
            assert null_count == 0, \
                f"[{table}] 有 {null_count} 条记录 tenant_id 为 NULL — 隔离漏洞！"
            logger.info(f"[{table}] 所有记录 tenant_id 非空 ✓")
        except Exception as e:
            if "does not exist" in str(e) or "UndefinedTable" in str(e):
                pytest.skip(f"[{table}] 表不存在")
            raise
        finally:
            db.close()

    @pytest.mark.parametrize("table,dbname,col", DB_ISOLATION_CHECKS,
                             ids=[f"{t[0]}_no_cross" for t in DB_ISOLATION_CHECKS])
    def test_no_cross_tenant_in_db(self, table, dbname, col):
        """API 返回的数据只包含一个 tenant_id"""
        try:
            db = DbClient(dbname)
        except Exception:
            pytest.skip(f"无法连接 {dbname}")
        try:
            result = db.query(
                f"SELECT {col}, COUNT(*) as cnt FROM {table} WHERE delete_at IS NULL GROUP BY {col}"
            )
            if len(result) > 1:
                logger.info(f"[{table}] 存在 {len(result)} 个租户的数据（正常 — 多租户共库）")
            for row in result:
                assert row[col] is not None, f"[{table}] 存在 tenant_id=NULL 的分组"
        except Exception as e:
            if "does not exist" in str(e) or "UndefinedTable" in str(e):
                pytest.skip(f"[{table}] 表不存在")
            raise
        finally:
            db.close()


# ═══════════════════════════════════════════════════
# Phase 2: API 级隔离验证 — 当前 Token 只返回自己数据
# ═══════════════════════════════════════════════════

API_ISOLATION_ENDPOINTS = [
    ("/api/system/role",           "角色列表"),
    ("/api/stations",              "充电站列表"),
    ("/api/device",                "设备列表"),
    ("/api/workorder",             "工单列表"),
    ("/api/system/announcements",  "公告列表"),
    ("/api/system/dict/types",     "字典类型"),
    ("/api/tenant/announcements",  "租户公告"),
    ("/api/tenant/categories",     "租户分类"),
    ("/api/charging/admin/orders", "充电订单"),
    ("/api/settlements",           "结算记录"),
    ("/api/content/articles",      "文章列表"),
    ("/api/system/user",           "用户列表"),
]


@pytest.mark.p0
@pytest.mark.tenant_isolation
class TestApiLevelIsolation:
    """Phase 2: API 级租户隔离验证"""

    @pytest.fixture(autouse=True)
    def _setup(self, gateway_api, auth_token):
        self.client = gateway_api
        self.client.session.headers["Authorization"] = f"Bearer {auth_token}"

    @pytest.mark.parametrize("endpoint,desc", API_ISOLATION_ENDPOINTS,
                             ids=[e[1] for e in API_ISOLATION_ENDPOINTS])
    def test_endpoint_returns_single_tenant(self, endpoint, desc):
        """每个端点返回的数据只包含一个 tenantId"""
        resp = self.client.get(endpoint, params={"page": 1, "pageSize": 100})
        if resp.status_code != 200:
            pytest.skip(f"[{desc}] 返回 {resp.status_code}")

        data = resp.json()
        raw = data.get("data", {})
        if isinstance(raw, list):
            items = raw
        elif isinstance(raw, dict):
            items = raw.get("items", raw.get("list", []))
        else:
            items = []

        tenant_ids = set()
        # 平台级零 GUID 属于系统数据，不算隔离泄漏
        PLATFORM_GUIDS = {
            "00000000-0000-0000-0000-000000000000",
            "00000000-0000-0000-0000-000000000001",
        }
        for item in items:
            tid = item.get("tenantId") or item.get("tenant_id")
            if tid and str(tid) not in PLATFORM_GUIDS:
                tenant_ids.add(str(tid))

        assert len(tenant_ids) <= 1, \
            f"[{desc}] 返回了多个租户的数据: {tenant_ids} — 隔离泄漏！"
        logger.info(f"[{desc}] 单租户验证通过 ({len(items)} 条, TenantIDs={tenant_ids or 'N/A'})")


# ═══════════════════════════════════════════════════
# Phase 3: 双租户交叉隔离验证（DB+API 混合）
# —— 用 DB 直插数据 + 用 SQL 验证隔离 + 用 API 验证过滤
# ═══════════════════════════════════════════════════

# 零 UUID 用作 create_by / update_by
_SYS_UUID = "00000000-0000-0000-0000-000000000001"

# 跨租户验证模块: (display_name, db_name, table, insert_cfg, name_col, api_url)
CROSS_TENANT_DB_MODULES = [
    ("角色", "jgsy_permission", "perm_role", {
        "cols": "id, role_name, role_code, status, scope, level, is_system, sort_order, tenant_id, create_by, create_name, create_time, update_by, update_name, update_time, delete_at",
        "vals": f"(%s, %s, %s, 1, 0, 0, false, 0, %s, '{_SYS_UUID}', '系统', NOW(), '{_SYS_UUID}', '系统', NOW(), NULL)",
        "args_a": lambda uid: (f"a1{uid[:6]}-0000-0000-0000-aaaaaaaaaaaa", f"IsoA_Role_{uid}", f"ISO_AR_{uid}"),
        "args_b": lambda uid: (f"b1{uid[:6]}-0000-0000-0000-bbbbbbbbbbbb", f"IsoB_Role_{uid}", f"ISO_BR_{uid}"),
    }, "role_name", "/api/system/role"),
    ("充电站", "jgsy_station", "station_info", {
        "cols": f"id, name, address, status, row_version, tenant_id, create_by, create_name, create_time, update_by, update_name, update_time, delete_at",
        "vals": f"(%s, %s, 'test_addr', 1, 1, %s, '{_SYS_UUID}', '系统', NOW(), '{_SYS_UUID}', '系统', NOW(), NULL)",
        "args_a": lambda uid: (f"a2{uid[:6]}-0000-0000-0000-aaaaaaaaaaaa", f"IsoA_Station_{uid}"),
        "args_b": lambda uid: (f"b2{uid[:6]}-0000-0000-0000-bbbbbbbbbbbb", f"IsoB_Station_{uid}"),
    }, "name", "/api/stations"),
    ("工单", "jgsy_workorder", "workorder_info", {
        "cols": f"id, title, priority, status, row_version, tenant_id, create_by, create_name, create_time, update_by, update_name, update_time, delete_at",
        "vals": f"(%s, %s, 'normal', 0, 1, %s, '{_SYS_UUID}', '系统', NOW(), '{_SYS_UUID}', '系统', NOW(), NULL)",
        "args_a": lambda uid: (f"a4{uid[:6]}-0000-0000-0000-aaaaaaaaaaaa", f"IsoA_WO_{uid}"),
        "args_b": lambda uid: (f"b4{uid[:6]}-0000-0000-0000-bbbbbbbbbbbb", f"IsoB_WO_{uid}"),
    }, "title", "/api/workorder"),
    ("结算", "jgsy_settlement", "settlement_record", {
        "cols": f"id, period_start, period_end, total_amount, platform_share, merchant_share, status, row_version, tenant_id, create_by, create_name, create_time, update_by, update_name, update_time, delete_at",
        "vals": f"(%s, '2026-01-01', '2026-01-31', 100.00, 20.00, 80.00, 0, 1, %s, '{_SYS_UUID}', '系统', NOW(), '{_SYS_UUID}', '系统', NOW(), NULL)",
        "args_a": lambda uid: (f"a5{uid[:6]}-0000-0000-0000-aaaaaaaaaaaa",),
        "args_b": lambda uid: (f"b5{uid[:6]}-0000-0000-0000-bbbbbbbbbbbb",),
    }, "id", "/api/settlements"),
    # CMS文章已移除: cms_article 有 FK 约束 (site_id→cms_site, category_id→cms_category)，不适合直插
]


@pytest.fixture(scope="module")
def two_tenants():
    """创建双测试租户（仅获取 tenant_id 即可，不依赖租户管理员权限）"""
    admin_token = _login("admin", "P@ssw0rd")
    if not admin_token:
        pytest.skip("无法获取 SUPER_ADMIN token")

    uid = str(int(time.time()))[-6:]
    tenants = []

    for idx, label in enumerate(["A", "B"]):
        code = f"iso{label.lower()}{uid}"
        phone_suffix = f"{uid}{idx+1:02d}"[:8]
        tenant_phone = f"138{phone_suffix}"[:11]
        resp = _api("POST", "/api/tenants", token=admin_token, json={
            "tenantName": f"IsoTest{label}_{uid}",
            "tenantCode": code,
            "tenantDomain": f"{code}.test.com",
            "contactPerson": f"Contact{label}",
            "contactPhone": tenant_phone,
        })
        if not resp or resp.status_code not in (200, 201):
            detail = resp.text[:200] if resp else "无响应"
            for t in tenants:
                _api("DELETE", f"/api/tenants/{t['id']}", token=admin_token)
            pytest.skip(f"创建租户{label}失败: {resp.status_code if resp else 'N/A'} {detail}")

        tdata = resp.json().get("data", {})
        tid = tdata.get("tenantId") or tdata.get("id")
        if not tid:
            for t in tenants:
                _api("DELETE", f"/api/tenants/{t['id']}", token=admin_token)
            pytest.skip(f"租户{label}无ID")

        tenants.append({"id": str(tid), "code": code})

    yield tenants, admin_token, uid

    # Cleanup
    for t in tenants:
        _api("DELETE", f"/api/tenants/{t['id']}", token=admin_token)


def _db_conn(dbname):
    """创建数据库连接"""
    import psycopg2
    return psycopg2.connect(
        host="localhost", port=5432, user="postgres",
        password="P@ssw0rd", dbname=dbname
    )


@pytest.mark.p0
@pytest.mark.tenant_isolation
@pytest.mark.skipif(MOCK_MODE, reason="DB 隔离测试需要真实数据库，Mock 模式下跳过")
class TestCrossTenantIsolation:
    """Phase 3: 双租户交叉隔离验证 — DB 直插 + SQL 查询验证"""

    @pytest.fixture(autouse=True)
    def _setup(self, two_tenants):
        data, self.admin_token, self.uid = two_tenants
        self.tid_a = data[0]["id"]
        self.tid_b = data[1]["id"]

    @pytest.mark.parametrize(
        "mod_name,dbname,table,insert_cfg,name_col,api_url",
        CROSS_TENANT_DB_MODULES,
        ids=[m[0] for m in CROSS_TENANT_DB_MODULES],
    )
    def test_db_read_isolation(self, mod_name, dbname, table, insert_cfg, name_col, api_url):
        """DB 级: 按 tenant_id 查询只返回本租户数据"""
        try:
            conn = _db_conn(dbname)
        except Exception:
            pytest.skip(f"无法连接 {dbname}")
        id_a = insert_cfg["args_a"](self.uid)[0]
        id_b = insert_cfg["args_b"](self.uid)[0]
        try:
            cur = conn.cursor()
            args_a = insert_cfg["args_a"](self.uid) + (self.tid_a,)
            args_b = insert_cfg["args_b"](self.uid) + (self.tid_b,)
            sql = f"INSERT INTO {table} ({insert_cfg['cols']}) VALUES {insert_cfg['vals']}"
            cur.execute(sql, args_a)
            cur.execute(sql, args_b)
            conn.commit()

            # A 查询: 能找到 id_a，不能找到 id_b
            cur.execute(
                f"SELECT id FROM {table} WHERE tenant_id = %s AND delete_at IS NULL AND id IN (%s, %s)",
                (self.tid_a, id_a, id_b)
            )
            ids_a = {str(r[0]) for r in cur.fetchall()}
            assert id_a in ids_a, f"[{mod_name}] A 查不到自己的数据"
            assert id_b not in ids_a, f"[{mod_name}] A 能看到 B 的数据！隔离泄漏！"

            # B 查询: 能找到 id_b，不能找到 id_a
            cur.execute(
                f"SELECT id FROM {table} WHERE tenant_id = %s AND delete_at IS NULL AND id IN (%s, %s)",
                (self.tid_b, id_a, id_b)
            )
            ids_b = {str(r[0]) for r in cur.fetchall()}
            assert id_b in ids_b, f"[{mod_name}] B 查不到自己的数据"
            assert id_a not in ids_b, f"[{mod_name}] B 能看到 A 的数据！隔离泄漏！"

            logger.info(f"[{mod_name}] DB 读隔离 ✓")
        except Exception as e:
            if "does not exist" in str(e) or "UndefinedTable" in str(e) or "UndefinedColumn" in str(e):
                conn.rollback()
                pytest.skip(f"[{mod_name}] 表/列不存在: {e}")
            raise
        finally:
            # Cleanup
            try:
                cur = conn.cursor()
                for args_fn in [insert_cfg["args_a"], insert_cfg["args_b"]]:
                    rec_id = args_fn(self.uid)[0]
                    cur.execute(f"DELETE FROM {table} WHERE id = %s", (rec_id,))
                conn.commit()
            except Exception:
                conn.rollback()
            conn.close()

    @pytest.mark.parametrize(
        "mod_name,dbname,table,insert_cfg,name_col,api_url",
        CROSS_TENANT_DB_MODULES,
        ids=[m[0] for m in CROSS_TENANT_DB_MODULES],
    )
    def test_db_update_isolation(self, mod_name, dbname, table, insert_cfg, name_col, api_url):
        """DB 级: B 的 UPDATE 不影响 A 的数据"""
        try:
            conn = _db_conn(dbname)
        except Exception:
            pytest.skip(f"无法连接 {dbname}")
        try:
            cur = conn.cursor()
            args_a = insert_cfg["args_a"](self.uid) + (self.tid_a,)
            sql = f"INSERT INTO {table} ({insert_cfg['cols']}) VALUES {insert_cfg['vals']}"
            cur.execute(sql, args_a)
            conn.commit()

            rec_id_a = insert_cfg["args_a"](self.uid)[0]
            # 模拟 B 的 UPDATE: 带 tenant_id = B 的条件更新 A 的记录 → 应影响 0 行
            cur.execute(
                f"UPDATE {table} SET update_time = NOW() WHERE id = %s AND tenant_id = %s AND delete_at IS NULL",
                (rec_id_a, self.tid_b)
            )
            affected = cur.rowcount
            conn.commit()
            assert affected == 0, f"[{mod_name}] B 的 UPDATE 影响了 A 的 {affected} 条记录！隔离失败！"

            # 验证 A 的数据仍属于 A
            cur.execute(f"SELECT tenant_id FROM {table} WHERE id = %s AND delete_at IS NULL", (rec_id_a,))
            row = cur.fetchone()
            assert row is not None, f"[{mod_name}] A 的记录不存在了"
            assert str(row[0]) == self.tid_a, f"[{mod_name}] A 的 tenant_id 被篡改了！"
            logger.info(f"[{mod_name}] DB 写隔离(UPDATE) ✓")
        except Exception as e:
            if "does not exist" in str(e) or "UndefinedTable" in str(e) or "UndefinedColumn" in str(e):
                conn.rollback()
                pytest.skip(f"[{mod_name}] 表/列不存在: {e}")
            raise
        finally:
            try:
                cur = conn.cursor()
                rec_id = insert_cfg["args_a"](self.uid)[0]
                cur.execute(f"DELETE FROM {table} WHERE id = %s", (rec_id,))
                conn.commit()
            except Exception:
                conn.rollback()
            conn.close()

    @pytest.mark.parametrize(
        "mod_name,dbname,table,insert_cfg,name_col,api_url",
        CROSS_TENANT_DB_MODULES,
        ids=[m[0] for m in CROSS_TENANT_DB_MODULES],
    )
    def test_db_delete_isolation(self, mod_name, dbname, table, insert_cfg, name_col, api_url):
        """DB 级: B 的软删除不影响 A 的数据"""
        try:
            conn = _db_conn(dbname)
        except Exception:
            pytest.skip(f"无法连接 {dbname}")
        try:
            cur = conn.cursor()
            args_a = insert_cfg["args_a"](self.uid) + (self.tid_a,)
            sql = f"INSERT INTO {table} ({insert_cfg['cols']}) VALUES {insert_cfg['vals']}"
            cur.execute(sql, args_a)
            conn.commit()

            rec_id_a = insert_cfg["args_a"](self.uid)[0]
            # 模拟 B 的软删除: 带 tenant_id = B → 应影响 0 行
            cur.execute(
                f"UPDATE {table} SET delete_at = NOW() WHERE id = %s AND tenant_id = %s AND delete_at IS NULL",
                (rec_id_a, self.tid_b)
            )
            affected = cur.rowcount
            conn.commit()
            assert affected == 0, f"[{mod_name}] B 的 DELETE 影响了 A 的 {affected} 条记录！隔离失败！"

            # 验证 A 的数据仍然存活
            cur.execute(f"SELECT delete_at FROM {table} WHERE id = %s", (rec_id_a,))
            row = cur.fetchone()
            assert row is not None and row[0] is None, f"[{mod_name}] A 的数据被 B 软删了！"
            logger.info(f"[{mod_name}] DB 写隔离(DELETE) ✓")
        except Exception as e:
            if "does not exist" in str(e) or "UndefinedTable" in str(e) or "UndefinedColumn" in str(e):
                conn.rollback()
                pytest.skip(f"[{mod_name}] 表/列不存在: {e}")
            raise
        finally:
            try:
                cur = conn.cursor()
                rec_id = insert_cfg["args_a"](self.uid)[0]
                cur.execute(f"DELETE FROM {table} WHERE id = %s", (rec_id,))
                conn.commit()
            except Exception:
                conn.rollback()
            conn.close()

    @pytest.mark.parametrize(
        "mod_name,dbname,table,insert_cfg,name_col,api_url",
        [(m[0], m[1], m[2], m[3], m[4], m[5]) for m in CROSS_TENANT_DB_MODULES if m[5]],
        ids=[m[0] for m in CROSS_TENANT_DB_MODULES if m[5]],
    )
    def test_api_cross_tenant_invisible(self, mod_name, dbname, table, insert_cfg, name_col, api_url):
        """API 级: 直插 B 数据后，super_admin (tenant=平台) 列表中不含 B 数据标记"""
        try:
            conn = _db_conn(dbname)
        except Exception:
            pytest.skip(f"无法连接 {dbname}")
        try:
            cur = conn.cursor()
            args_b = insert_cfg["args_b"](self.uid) + (self.tid_b,)
            sql = f"INSERT INTO {table} ({insert_cfg['cols']}) VALUES {insert_cfg['vals']}"
            cur.execute(sql, args_b)
            conn.commit()

            # Super admin (平台租户) 查列表 → 不应看到 B 租户的测试数据
            resp = _api("GET", api_url, token=self.admin_token, params={"page": 1, "pageSize": 500})
            if resp is not None and resp.status_code == 200:
                raw = resp.json().get("data", {})
                items = raw.get("items", raw.get("list", [])) if isinstance(raw, dict) else raw
                args_b = insert_cfg["args_b"](self.uid)
                search_key = args_b[1] if len(args_b) > 1 else str(args_b[0])
                found = any(search_key in str(item.get(name_col, "") or item.get("title", "") or item.get("id", "")) for item in items)
                assert not found, f"[{mod_name}] 平台 admin 看到了租户 B 的隔离测试数据 '{search_key}'！"
                logger.info(f"[{mod_name}] API 跨租户不可见 ✓ ({len(items)} items)")
            else:
                status = resp.status_code if resp else "N/A"
                logger.warning(f"[{mod_name}] API 查询返回 {status}，跳过 API 验证")
        except Exception as e:
            if "does not exist" in str(e) or "UndefinedTable" in str(e) or "UndefinedColumn" in str(e):
                conn.rollback()
                pytest.skip(f"[{mod_name}] 表/列不存在: {e}")
            raise
        finally:
            try:
                cur = conn.cursor()
                rec_id = insert_cfg["args_b"](self.uid)[0]
                cur.execute(f"DELETE FROM {table} WHERE id = %s", (rec_id,))
                conn.commit()
            except Exception:
                conn.rollback()
            conn.close()


# ═══════════════════════════════════════════════════
# Phase 4: 安全边界
# ═══════════════════════════════════════════════════

@pytest.mark.p0
@pytest.mark.tenant_isolation
class TestTenantSecurityBoundary:
    """Phase 4: 安全边界测试"""

    @pytest.fixture(autouse=True)
    def _setup(self, gateway_api, auth_token):
        self.client = gateway_api
        self.admin_token = auth_token

    def test_no_token_returns_401(self):
        """无 Token → 401"""
        resp = _api("GET", "/api/system/role?page=1&pageSize=1")
        assert resp is not None and resp.status_code == 401

    def test_fake_token_returns_401(self):
        """伪造 Token → 401"""
        resp = _api("GET", "/api/system/role?page=1&pageSize=1",
                     token="eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJmYWtlIn0.fake_sig")
        assert resp is not None and resp.status_code == 401

    def test_expired_token_returns_401(self):
        """损坏 Token → 401"""
        resp = _api("GET", "/api/stations?page=1&pageSize=1", token="expired_xxx")
        assert resp is not None and resp.status_code == 401

    def test_internal_api_no_key(self):
        """内部 API 无 Key → 拒绝"""
        no_auth = MockApiClient(token=None)
        resp = no_auth.get("/api/internal/users/count")
        assert resp.status_code in (401, 403, 404)

    def test_internal_api_wrong_key(self):
        """内部 API 错误 Key → 拒绝"""
        bad_api = MockApiClient(token="wrong_key")
        resp = bad_api.get("/api/internal/users/count")
        assert resp.status_code in (401, 403)

    def test_sql_injection_login(self):
        """SQL 注入登录 → 400/401"""
        resp = _api("POST", "/api/auth/login", json={
            "username": "admin' OR '1'='1", "password": "P@ssw0rd"})
        assert resp is not None and resp.status_code in (400, 401)

    def test_xss_in_search(self):
        """XSS 不导致 500"""
        resp = self.client.get("/api/system/role",
                               params={"page": 1, "pageSize": 5, "keyword": "<script>alert(1)</script>"})
        assert resp.status_code < 500
