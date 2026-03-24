"""
JGSY.AGI 全功能单元+API测试 — 全局 Fixture（全内存 Mock 版）
=============================================================
核心原则：全内存 / Mock / 不连真实 DB / 不发真实 HTTP
所有测试通过纯 Python 模拟完成，无需启动任何微服务。
单条测试 < 0.1ms，5万+ 条几分钟跑完。
"""
import sys, os
# 确保 tests/ 目录在 sys.path 首位，xdist worker 和直接运行均可找到 mock_client
_TESTS_DIR = os.path.dirname(os.path.abspath(__file__))
if _TESTS_DIR not in sys.path:
    sys.path.insert(0, _TESTS_DIR)
import os
import json
import uuid
import re
import logging
import threading
import pytest
from datetime import datetime, timezone
from http.server import HTTPServer, BaseHTTPRequestHandler

logger = logging.getLogger(__name__)

# ═══════════════════════════════════════════════════
# 常量
# ═══════════════════════════════════════════════════

# 从 mock_client 模块导入核心 Mock 基础设施（避免循环导入）
from mock_client import (
    MOCK_TOKEN, MockResponse, MockApiClient, _MockSession,
    _make_entity, _make_base_entity, _RESOURCE_FIELDS, _UUID_RE, _TS, _TENANT_ID, _ADMIN_ID,
    _VALID_CREDS, MOCK_MODE,
)

GATEWAY_URL = os.getenv("JGSY_GATEWAY_URL", "http://localhost:18999")
_MOCK_PORT = 18999

SUPER_ADMIN_USERNAME = os.getenv("JGSY_ADMIN_USERNAME", "admin")
SUPER_ADMIN_PASSWORD = os.getenv("JGSY_ADMIN_PASSWORD", "P@ssw0rd")

DB_PASSWORD = os.getenv("JGSY_DB_PASSWORD", "P@ssw0rd")
DB_HOST = os.getenv("JGSY_DB_HOST", "localhost")
DB_PORT = int(os.getenv("JGSY_DB_PORT", "5432"))
DB_USER = os.getenv("JGSY_DB_USER", "postgres")
REQUEST_TIMEOUT = int(os.getenv("JGSY_REQUEST_TIMEOUT", "10"))
LOGIN_TIMEOUT = int(os.getenv("JGSY_LOGIN_TIMEOUT", "10"))
TEST_TENANT_ID = os.getenv("JGSY_TEST_TENANT_ID", "")

DIRECT_URLS = {
    "tenant":          "http://localhost:8001",
    "identity":        "http://localhost:8002",
    "permission":      "http://localhost:8003",
    "observability":   "http://localhost:8005",
    "storage":         "http://localhost:8006",
    "account":         "http://localhost:8008",
    "analytics":       "http://localhost:8009",
    "charging":        "http://localhost:8010",
    "device":          "http://localhost:8011",
    "digitaltwin":     "http://localhost:8012",
    "ingestion":       "http://localhost:8013",
    "settlement":      "http://localhost:8014",
    "station":         "http://localhost:8015",
    "workorder":       "http://localhost:8016",
    "contentplatform": "http://localhost:8017",
    "iotcloudai":      "http://localhost:8020",
    "blockchain":      "http://localhost:8021",
    "orchestrator":    "http://localhost:8022",
    "vpp":             "http://localhost:8023",
    "microgrid":       "http://localhost:8024",
    "pvessc":          "http://localhost:8025",
    "electrade":       "http://localhost:8026",
    "carbontrade":     "http://localhost:8027",
    "demandresp":      "http://localhost:8028",
    "deviceops":       "http://localhost:8029",
    "energyeff":       "http://localhost:8030",
    "multienergy":     "http://localhost:8031",
    "safecontrol":     "http://localhost:8032",
}

DB_CONFIGS = {
    "tenant": "jgsy_tenant", "identity": "jgsy_identity", "permission": "jgsy_permission",
    "observability": "jgsy_observability", "storage": "jgsy_storage", "account": "jgsy_account",
    "analytics": "jgsy_analytics", "charging": "jgsy_charging", "device": "jgsy_device",
    "digitaltwin": "jgsy_digitaltwin", "ingestion": "jgsy_ingestion", "settlement": "jgsy_settlement",
    "station": "jgsy_station", "workorder": "jgsy_workorder", "content": "jgsy_content",
    "orchestrator": "jgsy_orchestrator", "vpp": "jgsy_vpp", "microgrid": "jgsy_microgrid",
    "pvessc": "jgsy_pvessc", "electrade": "jgsy_electrade", "carbontrade": "jgsy_carbontrade",
    "demandresp": "jgsy_demandresp", "deviceops": "jgsy_deviceops", "energyeff": "jgsy_energyeff",
    "multienergy": "jgsy_multienergy", "safecontrol": "jgsy_safecontrol",
    "iotcloudai": "jgsy_iotcloudai", "blockchain": "jgsy_blockchain",
}


# ═══════════════════════════════════════════════════
# HTTP Mock 服务器（向后兼容：security/ 测试直接 requests.get 用）
# ═══════════════════════════════════════════════════

_MOCK_OK = json.dumps({
    "success": True, "code": 200,
    "data": {"id": "00000000-0000-0000-0000-000000000099", "items": [], "total": 0, "page": 1, "pageSize": 10, "list": [], "rows": []},
    "timestamp": "2026-03-07T00:00:00Z", "traceId": "mock-ok",
}, ensure_ascii=False).encode("utf-8")

_MOCK_401 = json.dumps({
    "success": False, "code": 401, "message": "Unauthorized", "data": None,
    "timestamp": "2026-03-07T00:00:00Z", "traceId": "mock-401",
}, ensure_ascii=False).encode("utf-8")


class _MockHandler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):
        pass

    def _send(self, status, body, extra=None):
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        if extra:
            for k, val in extra.items():
                self.send_header(k, val)
        self.end_headers()
        try:
            self.wfile.write(body)
        except (BrokenPipeError, ConnectionResetError):
            pass

    def _body_json(self):
        try:
            n = int(self.headers.get("Content-Length", 0))
            return json.loads(self.rfile.read(n)) if n > 0 else {}
        except Exception:
            return {}

    def _handle(self):
        path = self.path.split("?")[0]
        auth = self.headers.get("Authorization", "")
        if self.command == "OPTIONS":
            self._send(200, b"{}", {"Access-Control-Allow-Methods": "GET,POST,PUT,PATCH,DELETE,OPTIONS",
                                     "Access-Control-Allow-Headers": "Authorization,Content-Type,X-Tenant-Id"})
            return
        if path in ("/", "/health", "/healthz", "/ready"):
            self._send(200, b'{"status":"ok"}')
            return
        if "auth/login" in path and self.command == "POST":
            body = self._body_json()
            if (body.get("username", ""), body.get("password", "")) in _VALID_CREDS:
                self._send(200, json.dumps({"success": True, "code": 200, "data": {"accessToken": MOCK_TOKEN, "token": MOCK_TOKEN, "refreshToken": "mock-refresh", "expiresIn": 86400}, "timestamp": "2026-03-07T00:00:00Z", "traceId": "mock-login"}, ensure_ascii=False).encode("utf-8"))
            else:
                self._send(401, json.dumps({"success": False, "code": 401, "message": "用户名或密码错误", "data": None, "timestamp": "2026-03-07T00:00:00Z", "traceId": "mock-login-err"}, ensure_ascii=False).encode("utf-8"))
            return
        token = auth[7:].strip() if auth.startswith("Bearer ") else ""
        if not token or token != MOCK_TOKEN:
            self._send(401, _MOCK_401)
            return
        if "/internal/" in path:
            self._send(403, json.dumps({"success": False, "code": 403, "message": "Forbidden", "data": None, "timestamp": "2026-03-07T00:00:00Z", "traceId": "mock-403"}, ensure_ascii=False).encode("utf-8"))
            return
        self._send(200, _MOCK_OK)

    do_GET = do_POST = do_PUT = do_PATCH = do_DELETE = do_OPTIONS = do_HEAD = _handle


def _start_mock_on(port):
    try:
        srv = HTTPServer(("127.0.0.1", port), _MockHandler)
        t = threading.Thread(target=srv.serve_forever, daemon=True, name=f"MockAPI:{port}")
        t.start()
        return srv
    except OSError:
        return None

_mock_primary = _start_mock_on(_MOCK_PORT) if MOCK_MODE else None
_mock_port8000 = _start_mock_on(8000) if MOCK_MODE else None
os.environ.setdefault("JGSY_GATEWAY_URL", f"http://localhost:{_MOCK_PORT}")

_bypass = "127.0.0.1,localhost,::1"
_cur = os.environ.get("no_proxy", os.environ.get("NO_PROXY", ""))
if "127.0.0.1" not in _cur:
    _m = _bypass + ("," + _cur if _cur else "")
    os.environ["no_proxy"] = _m
    os.environ["NO_PROXY"] = _m



# ═══════════════════════════════════════════════════════════════════════════
# ApiClient — 真实 HTTP 客户端（保留供需要真实连接的场景）
# ═══════════════════════════════════════════════════════════════════════════

import requests as _real_requests

class ApiClient:
    def __init__(self, base_url, token=None, timeout=REQUEST_TIMEOUT):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.session = _real_requests.Session()
        self.session.headers.update({"Content-Type": "application/json", "Accept": "application/json"})
        if token:
            self.session.headers["Authorization"] = f"Bearer {token}"

    def set_token(self, token):
        self.session.headers["Authorization"] = f"Bearer {token}"

    def get(self, path, params=None, **kw):
        return self.session.get(f"{self.base_url}{path}", params=params, timeout=self.timeout, **kw)

    def post(self, path, json=None, data=None, **kw):
        return self.session.post(f"{self.base_url}{path}", json=json, data=data, timeout=self.timeout, **kw)

    def put(self, path, json=None, **kw):
        return self.session.put(f"{self.base_url}{path}", json=json, timeout=self.timeout, **kw)

    def delete(self, path, **kw):
        return self.session.delete(f"{self.base_url}{path}", timeout=self.timeout, **kw)

    def patch(self, path, json=None, **kw):
        return self.session.patch(f"{self.base_url}{path}", json=json, timeout=self.timeout, **kw)


# ═══════════════════════════════════════════════════════════════════════════
# DbClient
# ═══════════════════════════════════════════════════════════════════════════

class DbClient:
    def __init__(self, dbname):
        import psycopg2
        from psycopg2.extras import RealDictCursor
        self.conn = psycopg2.connect(host=DB_HOST, port=DB_PORT, dbname=dbname, user=DB_USER, password=DB_PASSWORD)
        self.conn.autocommit = True
        self._RDC = RealDictCursor

    def query(self, sql, params=None):
        with self.conn.cursor(cursor_factory=self._RDC) as c:
            c.execute(sql, params); return c.fetchall()

    def query_one(self, sql, params=None):
        with self.conn.cursor(cursor_factory=self._RDC) as c:
            c.execute(sql, params); return c.fetchone()

    def query_scalar(self, sql, params=None):
        with self.conn.cursor() as c:
            c.execute(sql, params); r = c.fetchone(); return r[0] if r else None

    def execute(self, sql, params=None):
        with self.conn.cursor() as c:
            c.execute(sql, params)

    def close(self):
        if self.conn and not self.conn.closed:
            self.conn.close()


# ═══════════════════════════════════════════════════════════════════════════
# ApiResultValidator
# ═══════════════════════════════════════════════════════════════════════════

class ApiResultValidator:
    @staticmethod
    def assert_success(resp, expected_code=200):
        assert resp.status_code == 200, f"HTTP {resp.status_code}: {resp.text[:500]}"
        d = resp.json()
        assert d.get("success") is True
        assert str(d.get("code")) == str(expected_code)
        assert "data" in d and "timestamp" in d and "traceId" in d
        return d["data"]

    @staticmethod
    def assert_paged(resp, min_total=0):
        data = ApiResultValidator.assert_success(resp)
        assert "items" in data and "total" in data
        assert data["total"] >= min_total
        assert isinstance(data["items"], list)
        return data

    @staticmethod
    def assert_error(resp, expected_http=None, expected_code=None):
        if expected_http:
            assert resp.status_code == expected_http
        d = resp.json()
        assert d.get("success") is False
        if expected_code:
            assert str(d.get("code")) == str(expected_code)
        return d

    @staticmethod
    def not_5xx(resp):
        assert resp.status_code < 500, f"HTTP {resp.status_code}: {resp.text[:500]}"
        return resp


# ═══════════════════════════════════════════════════════════════════════════
# RoutingApiClient — 真实模式下按路径前缀路由到直连服务（绕过网关）
# ═══════════════════════════════════════════════════════════════════════════

# 路径前缀 → 服务名 映射
_PATH_ROUTE_MAP = [
    ("/api/auth",              "identity"),
    ("/api/system/role",       "permission"),
    ("/api/system/menu",       "permission"),
    ("/api/system/perm",       "permission"),
    ("/api/system/dict",       "permission"),
    ("/api/system/announce",   "permission"),
    ("/api/system/user",       "account"),
    ("/api/users",             "account"),
    ("/api/tenants",           "tenant"),
    ("/api/tenant",            "tenant"),
    ("/api/stations",          "station"),
    ("/api/device",            "device"),
    ("/api/workorder",         "workorder"),
    ("/api/settlements",       "settlement"),
    ("/api/ingestion",         "ingestion"),
    ("/api/content",           "contentplatform"),
    ("/api/charging",          "charging"),
    ("/api/analytics",         "analytics"),
    ("/api/storage",           "storage"),
    ("/api/blockchain",        "blockchain"),
    ("/api/iot",               "iotcloudai"),
    ("/api/digitaltwin",       "digitaltwin"),
    ("/api/monitor",           "observability"),
    ("/api/observability",     "observability"),
    ("/api/orchestrator",      "orchestrator"),
    ("/api/vpp",               "vpp"),
    ("/api/microgrid",         "microgrid"),
    ("/api/pvessc",            "pvessc"),
    ("/api/electrade",         "electrade"),
    ("/api/carbontrade",       "carbontrade"),
    ("/api/demandresp",        "demandresp"),
    ("/api/deviceops",         "deviceops"),
    ("/api/energyeff",         "energyeff"),
    ("/api/multienergy",       "multienergy"),
    ("/api/safecontrol",       "safecontrol"),
]


class RoutingApiClient:
    """真实模式 API 客户端：按路径前缀自动路由到对应微服务直连地址"""

    def __init__(self, token=None, timeout=REQUEST_TIMEOUT):
        self.timeout = timeout
        self.session = _real_requests.Session()
        self.session.headers.update({
            "Content-Type": "application/json",
            "Accept": "application/json",
        })
        if token:
            self.session.headers["Authorization"] = f"Bearer {token}"

    def _resolve_url(self, path):
        """根据路径前缀找到对应服务的直连 URL"""
        for prefix, svc in _PATH_ROUTE_MAP:
            if path.startswith(prefix):
                base = DIRECT_URLS.get(svc, "")
                if base:
                    return f"{base}{path}"
        # 回退到网关
        return f"{GATEWAY_URL}{path}"

    def set_token(self, token):
        self.session.headers["Authorization"] = f"Bearer {token}"

    def get(self, path, params=None, **kw):
        return self.session.get(self._resolve_url(path), params=params, timeout=self.timeout, **kw)

    def post(self, path, json=None, data=None, **kw):
        return self.session.post(self._resolve_url(path), json=json, data=data, timeout=self.timeout, **kw)

    def put(self, path, json=None, **kw):
        return self.session.put(self._resolve_url(path), json=json, timeout=self.timeout, **kw)

    def delete(self, path, **kw):
        return self.session.delete(self._resolve_url(path), timeout=self.timeout, **kw)

    def patch(self, path, json=None, **kw):
        return self.session.patch(self._resolve_url(path), json=json, timeout=self.timeout, **kw)


def _real_login():
    """真实模式登录 identity 服务获取 token"""
    url = DIRECT_URLS.get("identity", "http://localhost:8002")
    try:
        resp = _real_requests.post(
            f"{url}/api/auth/login",
            json={"username": SUPER_ADMIN_USERNAME, "password": SUPER_ADMIN_PASSWORD},
            timeout=LOGIN_TIMEOUT,
        )
        if resp.status_code == 200:
            data = resp.json().get("data", {})
            return data.get("accessToken") or data.get("token")
    except Exception as exc:
        logger.warning(f"真实登录失败: {exc}")
    return None


# ═══════════════════════════════════════════════════════════════════════════
# Fixtures
# ═══════════════════════════════════════════════════════════════════════════

@pytest.fixture(scope="session")
def auth_token():
    if MOCK_MODE:
        return MOCK_TOKEN
    token = _real_login()
    if not token:
        pytest.skip("真实模式下无法登录获取 token")
    return token

@pytest.fixture(scope="session")
def gateway_api(auth_token):
    if MOCK_MODE:
        return MockApiClient(GATEWAY_URL, auth_token)
    return RoutingApiClient(token=auth_token)

@pytest.fixture(scope="session")
def api(gateway_api):
    return gateway_api

@pytest.fixture(scope="session")
def no_auth_api():
    if MOCK_MODE:
        return MockApiClient(GATEWAY_URL, token=None)
    return RoutingApiClient(token=None)

@pytest.fixture(scope="session")
def readonly_api(auth_token):
    """只读权限客户端 — 供权限检查测试使用（返回 403）"""
    if MOCK_MODE:
        client = MockApiClient(GATEWAY_URL, auth_token)
        client._readonly = True
        return client
    return RoutingApiClient(token=auth_token)

@pytest.fixture(scope="session")
def validator():
    return ApiResultValidator()

@pytest.fixture(scope="session")
def v(validator):
    return validator

@pytest.fixture(scope="function")
def uid():
    return uuid.uuid4().hex[:8]


def _make_svc(name, token):
    url = DIRECT_URLS.get(name, "")
    assert url, f"未知服务: {name}"
    if MOCK_MODE:
        return MockApiClient(url, token)
    return ApiClient(url, token)

@pytest.fixture(scope="session")
def identity_api(auth_token):
    return _make_svc("identity", auth_token)
@pytest.fixture(scope="session")
def permission_api(auth_token):
    return _make_svc("permission", auth_token)
@pytest.fixture(scope="session")
def tenant_api(auth_token):
    return _make_svc("tenant", auth_token)
@pytest.fixture(scope="session")
def charging_api(auth_token):
    return _make_svc("charging", auth_token)
@pytest.fixture(scope="session")
def account_api(auth_token):
    return _make_svc("account", auth_token)
@pytest.fixture(scope="session")
def settlement_api(auth_token):
    return _make_svc("settlement", auth_token)
@pytest.fixture(scope="session")
def station_api(auth_token):
    return _make_svc("station", auth_token)
@pytest.fixture(scope="session")
def device_api(auth_token):
    return _make_svc("device", auth_token)
@pytest.fixture(scope="session")
def workorder_api(auth_token):
    return _make_svc("workorder", auth_token)
@pytest.fixture(scope="session")
def analytics_api(auth_token):
    return _make_svc("analytics", auth_token)
@pytest.fixture(scope="session")
def observability_api(auth_token):
    return _make_svc("observability", auth_token)
@pytest.fixture(scope="session")
def blockchain_api(auth_token):
    return _make_svc("blockchain", auth_token)
@pytest.fixture(scope="session")
def orchestrator_api(auth_token):
    return _make_svc("orchestrator", auth_token)
@pytest.fixture(scope="session")
def vpp_api(auth_token):
    return _make_svc("vpp", auth_token)
@pytest.fixture(scope="session")
def pvessc_api(auth_token):
    return _make_svc("pvessc", auth_token)
@pytest.fixture(scope="session")
def electrade_api(auth_token):
    return _make_svc("electrade", auth_token)
@pytest.fixture(scope="session")
def content_api(auth_token):
    return _make_svc("contentplatform", auth_token)
@pytest.fixture(scope="session")
def storage_api(auth_token):
    return _make_svc("storage", auth_token)
@pytest.fixture(scope="session")
def ingestion_api(auth_token):
    return _make_svc("ingestion", auth_token)
@pytest.fixture(scope="session")
def digitaltwin_api(auth_token):
    return _make_svc("digitaltwin", auth_token)
@pytest.fixture(scope="session")
def iotcloudai_api(auth_token):
    return _make_svc("iotcloudai", auth_token)

# ── 数据库 Fixtures ──
def _make_db(name):
    from mock_client import MOCK_MODE
    if MOCK_MODE:
        pytest.skip(f"Mock 模式下跳过数据库测试 ({name})")
    dbname = DB_CONFIGS.get(name)
    assert dbname, f"未知数据库: {name}"
    try:
        return DbClient(dbname)
    except Exception as exc:
        pytest.skip(f"数据库 {dbname} 不可达: {exc}")

@pytest.fixture(scope="session")
def identity_db():
    db = _make_db("identity"); yield db; db.close()

@pytest.fixture(scope="session")
def permission_db():
    db = _make_db("permission"); yield db; db.close()

@pytest.fixture(scope="session")
def db():
    try:
        _db = _make_db("permission"); yield _db; _db.close()
    except Exception:
        yield None

@pytest.fixture(scope="session")
def account_db():
    db = _make_db("account"); yield db; db.close()

@pytest.fixture(scope="session")
def charging_db():
    db = _make_db("charging"); yield db; db.close()

@pytest.fixture(scope="session")
def station_db():
    db = _make_db("station"); yield db; db.close()

@pytest.fixture(scope="session")
def workorder_db():
    db = _make_db("workorder"); yield db; db.close()

@pytest.fixture(scope="session")
def settlement_db():
    db = _make_db("settlement"); yield db; db.close()

@pytest.fixture
def unique_suffix():
    """生成唯一后缀用于测试数据"""
    import time, random
    return f"{int(time.time() * 1000) % 10**8:08d}{random.randint(10, 99)}"
