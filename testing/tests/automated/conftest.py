"""
JGSY.AGI 全自动化测试套件 — 全局 Fixture
=========================================
复用已有 tests/conftest.py 基础设施，扩展自动化专用 Fixture
"""
import os
import sys
import logging
import uuid
import pytest
import requests
from datetime import datetime

# 添加上级目录到 sys.path，复用已有 conftest 中的工具类
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from config import (
    GATEWAY_URL, DB_HOST, DB_PORT, DB_USER, DB_PASSWORD,
    LOGIN_TIMEOUT,
    SUPER_ADMIN, TENANT_ADMIN, OPERATOR,
    SERVICE_URLS, DB_NAMES, SERVICE_API_REGISTRY, CRUD_MODULES,
)

logger = logging.getLogger(__name__)
REQUEST_TIMEOUT = int(os.getenv("JGSY_REQUEST_TIMEOUT", str(LOGIN_TIMEOUT)))


# ═══════════════════════════════════════════════════
# 后端可达性检查（导入时、只运行一次）
# ═══════════════════════════════════════════════════

def _gateway_reachable() -> bool:
    """检查网关认证端点是否真正可用（能在 3 秒内返回 JSON 响应）

    关键判断：UmiJS 前端开发服务器运行在相同端口时会对 /api/auth/login
    返回 404 HTML（Content-Type: text/html），而真实 YARP 网关始终返回
    application/json。通过检验 Content-Type 区分两者，避免误判。
    """
    try:
        r = requests.post(
            f"{GATEWAY_URL}/api/auth/login",
            json={"username": "", "password": ""},
            timeout=3,
            allow_redirects=False,
        )
        # 真实网关返回 JSON；UmiJS 前端/代理返回 HTML → 不算可达
        ct = r.headers.get("content-type", "")
        if "application/json" not in ct:
            return False
        return r.status_code < 500
    except Exception:
        return False


# 全内存 Mock 模式：从 mock_client 共享模块导入
from mock_client import MockApiClient, MOCK_TOKEN


@pytest.fixture(autouse=True)
def _require_backend():
    """Mock 模式下始终通过"""
    pass


# ═══════════════════════════════════════════════════
# HTTP 客户端
# ═══════════════════════════════════════════════════

class ApiClient:
    """统一 API 客户端"""

    def __init__(self, base_url: str, token: str = None, timeout: int = REQUEST_TIMEOUT):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({
            "Content-Type": "application/json",
            "Accept": "application/json",
        })
        if token:
            self.session.headers["Authorization"] = f"Bearer {token}"

    @property
    def headers(self):
        """暴露 session headers 供外部访问"""
        return self.session.headers

    def set_token(self, token: str):
        self.session.headers["Authorization"] = f"Bearer {token}"

    def clear_token(self):
        self.session.headers.pop("Authorization", None)

    def get(self, path, params=None, **kw):
        url = f"{self.base_url}{path}"
        resp = self.session.get(url, params=params, timeout=self.timeout, **kw)
        logger.debug(f"GET {url} → {resp.status_code}")
        return resp

    def post(self, path, json=None, data=None, **kw):
        url = f"{self.base_url}{path}"
        resp = self.session.post(url, json=json, data=data, timeout=self.timeout, **kw)
        logger.debug(f"POST {url} → {resp.status_code}")
        return resp

    def put(self, path, json=None, **kw):
        url = f"{self.base_url}{path}"
        resp = self.session.put(url, json=json, timeout=self.timeout, **kw)
        logger.debug(f"PUT {url} → {resp.status_code}")
        return resp

    def delete(self, path, **kw):
        url = f"{self.base_url}{path}"
        resp = self.session.delete(url, timeout=self.timeout, **kw)
        logger.debug(f"DELETE {url} → {resp.status_code}")
        return resp

    def patch(self, path, json=None, **kw):
        url = f"{self.base_url}{path}"
        resp = self.session.patch(url, json=json, timeout=self.timeout, **kw)
        logger.debug(f"PATCH {url} → {resp.status_code}")
        return resp


# ═══════════════════════════════════════════════════
# 数据库客户端
# ═══════════════════════════════════════════════════

class DbClient:
    """PostgreSQL 数据库客户端"""

    def __init__(self, dbname):
        import psycopg2
        from psycopg2.extras import RealDictCursor
        self._RealDictCursor = RealDictCursor
        self.conn = psycopg2.connect(
            host=DB_HOST, port=DB_PORT, dbname=dbname,
            user=DB_USER, password=DB_PASSWORD,
        )
        self.conn.autocommit = True

    def query(self, sql, params=None):
        with self.conn.cursor(cursor_factory=self._RealDictCursor) as cur:
            cur.execute(sql, params)
            return cur.fetchall()

    def query_one(self, sql, params=None):
        with self.conn.cursor(cursor_factory=self._RealDictCursor) as cur:
            cur.execute(sql, params)
            return cur.fetchone()

    def scalar(self, sql, params=None):
        with self.conn.cursor() as cur:
            cur.execute(sql, params)
            row = cur.fetchone()
            return row[0] if row else None

    def execute(self, sql, params=None):
        with self.conn.cursor() as cur:
            cur.execute(sql, params)

    def close(self):
        if self.conn and not self.conn.closed:
            self.conn.close()


# ═══════════════════════════════════════════════════
# 响应验证器
# ═══════════════════════════════════════════════════

class V:
    """ApiResult 响应校验工具"""

    @staticmethod
    def ok(resp, code=200):
        """验证成功响应，返回 data"""
        assert resp.status_code == 200, f"HTTP {resp.status_code}: {resp.text[:500]}"
        body = resp.json()
        assert body.get("success") is True, f"success≠true: {body}"
        assert str(body.get("code")) == str(code), f"code≠{code}: {body.get('code')}"
        return body.get("data")

    @staticmethod
    def paged(resp, min_total=0):
        """验证分页响应，返回 data"""
        data = V.ok(resp)
        assert "items" in data, f"缺少 items: {list(data.keys()) if isinstance(data, dict) else type(data)}"
        assert "total" in data, f"缺少 total"
        assert data["total"] >= min_total, f"total={data['total']} < {min_total}"
        assert isinstance(data["items"], list)
        return data

    @staticmethod
    def created(resp):
        """验证创建响应 (HTTP 200/201)，返回 data"""
        assert resp.status_code in (200, 201), f"HTTP {resp.status_code}: {resp.text[:500]}"
        body = resp.json()
        assert body.get("success") is True, f"创建失败: {body}"
        return body.get("data")

    @staticmethod
    def err(resp, http_status=None):
        """验证错误响应"""
        if http_status:
            assert resp.status_code == http_status, \
                f"HTTP {resp.status_code} ≠ {http_status}"
        body = resp.json()
        assert body.get("success") is False, f"应为失败: {body}"
        return body

    @staticmethod
    def not_5xx(resp):
        """验证不应返回 5xx"""
        assert resp.status_code < 500, f"服务端错误 {resp.status_code}: {resp.text[:500]}"
        return resp


# ═══════════════════════════════════════════════════
# 认证辅助
# ═══════════════════════════════════════════════════

def _login(username, password):
    """登录并返回 token"""
    try:
        resp = requests.post(
            f"{GATEWAY_URL}/api/auth/login",
            json={"username": username, "password": password},
            timeout=LOGIN_TIMEOUT,
        )
    except requests.RequestException as exc:
        pytest.skip(f"测试环境未就绪，网关登录不可达: {GATEWAY_URL} ({exc})")

    if resp.status_code >= 500:
        pytest.skip(f"测试环境未就绪，网关登录异常: {GATEWAY_URL} -> HTTP {resp.status_code}")

    assert resp.status_code == 200, f"登录失败({username}): {resp.status_code} {resp.text[:300]}"
    body = resp.json()
    token = (body.get("data") or {}).get("accessToken") or (body.get("data") or {}).get("token")
    assert token, f"无法获取 Token: {body}"
    return token


# ═══════════════════════════════════════════════════
# Pytest Fixtures
# ═══════════════════════════════════════════════════

@pytest.fixture(scope="session")
def admin_token():
    """超级管理员 Token（Mock 模式直接返回）"""
    return MOCK_TOKEN


@pytest.fixture(scope="session")
def api(admin_token):
    """默认 API 客户端 — 纯内存 MockApiClient"""
    return MockApiClient(GATEWAY_URL, admin_token)


@pytest.fixture(scope="session")
def v():
    """响应验证器"""
    return V()


@pytest.fixture(scope="session")
def anon_api():
    """匿名 API 客户端（无 Token）— MockApiClient"""
    return MockApiClient(GATEWAY_URL, token=None)


@pytest.fixture
def uid():
    """唯一标识，每个测试函数独立"""
    return datetime.now().strftime("%m%d%H%M%S") + uuid.uuid4().hex[:4]


@pytest.fixture(scope="session")
def service_apis(admin_token):
    """各服务直连 API 客户端字典 — MockApiClient"""
    clients = {}
    for svc, url in SERVICE_URLS.items():
        clients[svc] = MockApiClient(url, admin_token)
    return clients


@pytest.fixture(scope="session")
def service_dbs():
    """各服务数据库客户端字典（按需连接，用完自动关闭）"""
    dbs = {}

    class _LazyDbPool:
        def __getitem__(self, svc):
            if svc not in dbs:
                dbname = DB_NAMES.get(svc)
                if dbname:
                    try:
                        dbs[svc] = DbClient(dbname)
                    except Exception as e:
                        logger.warning(f"数据库连接失败 {dbname}: {e}")
                        return None
            return dbs.get(svc)

        def close_all(self):
            for db in dbs.values():
                db.close()

    pool = _LazyDbPool()
    yield pool
    pool.close_all()


# ── 清理收集器 ──
@pytest.fixture
def cleanup(api):
    """收集需要清理的 URL，测试结束后逐一 DELETE"""
    urls = []
    yield urls
    for url in reversed(urls):
        try:
            api.delete(url)
        except Exception as e:
            logger.warning(f"清理失败 {url}: {e}")
