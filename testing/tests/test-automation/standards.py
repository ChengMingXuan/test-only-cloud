"""
JGSY.AGI Python 单元测试规范化工具库
======================================
严格遵循《自动化测试标准手册 v3.0》第 4 章 pytest 规范

核心原则：
  • 100% Mock，禁止连真实数据库
  • ApiResult<T> / PagedResult<T> 标准响应结构
  • 单条测试 < 0.1ms，全量 49755 用例 < 8 分钟
  • 强制覆盖：认证/授权、多租户隔离、软删除、输入验证、CRUD
"""

import json
import uuid
import re
from datetime import datetime, timezone
from typing import Dict, Any, Optional, List, Callable
from dataclasses import dataclass, field, asdict
from enum import Enum
import logging

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════
# 1. 常量定义
# ═══════════════════════════════════════════════════════════

class HttpStatus(Enum):
    """HTTP 状态码"""
    OK = 200
    CREATED = 201
    NO_CONTENT = 204
    BAD_REQUEST = 400
    UNAUTHORIZED = 401
    FORBIDDEN = 403
    NOT_FOUND = 404
    CONFLICT = 409
    INTERNAL_ERROR = 500
    SERVICE_UNAVAILABLE = 503


class ErrorCode(Enum):
    """业务错误码（需与后端一致）"""
    INVALID_PARAMS = "INVALID_PARAMS"
    UNAUTHORIZED = "UNAUTHORIZED"
    FORBIDDEN = "FORBIDDEN"
    NOT_FOUND = "NOT_FOUND"
    CONFLICT = "CONFLICT"
    INTERNAL_ERROR = "INTERNAL_ERROR"
    TENANT_ISOLATION_VIOLATION = "TENANT_ISOLATION_VIOLATION"
    SOFT_DELETE_VIOLATION = "SOFT_DELETE_VIOLATION"


# 全局测试常量
SUPER_ADMIN_ID = "00000000-0000-0000-0000-000000000001"
ADMIN_USER_ID = "00000000-0000-0000-0000-000000000010"
NORMAL_USER_ID = "00000000-0000-0000-0000-000000000020"
READONLY_USER_ID = "00000000-0000-0000-0000-000000000030"

TENANT_ID_A = "a0000000-0000-0000-0000-000000000001"
TENANT_ID_B = "b0000000-0000-0000-0000-000000000001"

MOCK_TOKEN_ADMIN = "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsInRlbmFudF9pZCI6ImEwMDAwMDAwLTAwMDAtMDAwMC0wMDAwLTAwMDAwMDAwMDAwMSIsInJvbGVzIjoiU1VQRVJfQURNSU4iLCJleHAiOjk5OTk5OTk5OTl9.mock"
MOCK_TOKEN_USER = "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ1c2VyIiwidGVuYW50X2lkIjoiYTAwMDAwMDAtMDAwMC0wMDAwLTAwMDAtMDAwMDAwMDAwMDAxIiwicm9sZXMiOiJVU0VSIiwiZXhwIjo5OTk5OTk5OTk5fQ.mock"


# ═══════════════════════════════════════════════════════════
# 2. 数据模型
# ═══════════════════════════════════════════════════════════

@dataclass
class ApiResult:
    """
    标准 API 响应格式：ApiResult<T>
    
    对标 C# 中的：
    public class ApiResult<T>
    {
        public bool success { get; set; }
        public int code { get; set; }
        public T data { get; set; }
        public string message { get; set; }
        public string timestamp { get; set; }
        public string traceId { get; set; }
    }
    """
    success: bool
    code: int
    data: Any = None
    message: str = ""
    timestamp: str = ""
    traceId: str = ""

    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now(timezone.utc).isoformat()
        if not self.traceId:
            self.traceId = str(uuid.uuid4())

    def to_json(self) -> str:
        """转为 JSON 字符串"""
        return json.dumps(asdict(self), ensure_ascii=False, indent=2)

    def to_dict(self) -> Dict:
        """转为字典"""
        return asdict(self)


@dataclass
class PagedResult(ApiResult):
    """
    分页响应格式：PagedResult<T>
    
    对标 C# 中的：
    public class PagedResult<T> : ApiResult<T>
    {
        public int total { get; set; }
        public int page { get; set; }
        public int pageSize { get; set; }
        public List<T> items { get; set; }
    }
    """
    total: int = 0
    page: int = 1
    pageSize: int = 10
    items: List[Any] = field(default_factory=list)

    def __post_init__(self):
        # 不调用父类的 __post_init__，避免递归
        if not self.timestamp:
            self.timestamp = datetime.now(timezone.utc).isoformat()
        if not self.traceId:
            self.traceId = str(uuid.uuid4())
        # PagedResult 中 data 为 None（items 才是主要数据）
        if self.data is None:
            self.data = {}  # 不要设置为 self，避免递归

    def to_dict(self) -> Dict:
        """转为字典"""
        result = {
            'success': self.success,
            'code': self.code,
            'message': self.message,
            'timestamp': self.timestamp,
            'traceId': self.traceId,
            'total': self.total,
            'page': self.page,
            'pageSize': self.pageSize,
            'items': self.items,
        }
        return result


@dataclass
class BaseEntity:
    """
    所有业务实体基类（对应数据库公共字段规范）
    
    必须包含 9 个公共字段（强制）：
    • id: UUID 主键
    • tenant_id: UUID 租户 ID
    • create_by: UUID 创建人 ID
    • create_name: 创建人姓名
    • create_time: 创建时间
    • update_by: UUID 修改人 ID
    • update_name: 修改人姓名
    • update_time: 修改时间
    • delete_at: datetime NULL 软删除标识（NULL=未删除，有时间=已删除）
    """
    id: str = ""
    tenant_id: str = ""
    create_by: str = ""
    create_name: str = ""
    create_time: str = ""
    update_by: str = ""
    update_name: str = ""
    update_time: str = ""
    delete_at: Optional[str] = None

    def __post_init__(self):
        if not self.id:
            self.id = str(uuid.uuid4())
        if not self.create_time:
            self.create_time = datetime.now(timezone.utc).isoformat()
        if not self.update_time:
            self.update_time = self.create_time


@dataclass
class User(BaseEntity):
    """用户实体"""
    username: str = ""
    email: str = ""
    full_name: str = ""
    status: str = "ACTIVE"  # ACTIVE / INACTIVE / LOCKED
    last_login_time: Optional[str] = None


@dataclass
class Role(BaseEntity):
    """角色实体"""
    code: str = ""  # 唯一标识符（租户维度）
    name: str = ""
    description: str = ""
    is_system: bool = False


@dataclass
class Permission(BaseEntity):
    """权限实体"""
    code: str = ""  # 格式：{service}:{resource}:{action}（全小写）
    name: str = ""
    description: str = ""
    service: str = ""
    resource: str = ""
    action: str = ""


# ═══════════════════════════════════════════════════════════
# 3. Mock API 客户端
# ═══════════════════════════════════════════════════════════

class MockHttpResponse:
    """模拟 HTTP 响应"""
    
    def __init__(self, status_code: int, body: Dict[str, Any], headers: Dict[str, str] = None):
        self.status_code = status_code
        self._body = body
        self.headers = headers or {}
        self.elapsed_ms = 1.0  # Mock 响应总是 1ms

    def json(self) -> Dict[str, Any]:
        """获取响应体（JSON）"""
        return self._body

    def text(self) -> str:
        """获取响应体（文本）"""
        return json.dumps(self._body, ensure_ascii=False)

    @property
    def is_success(self) -> bool:
        """是否成功（2xx 状态码）"""
        return 200 <= self.status_code < 300

    def assert_success(self, msg: str = ""):
        """断言响应成功"""
        assert self.is_success, f"Expected success response, got {self.status_code}. {msg} Body: {self._body}"

    def assert_code(self, expected: int, msg: str = ""):
        """断言状态码"""
        assert self.status_code == expected, f"Expected {expected}, got {self.status_code}. {msg}"

    def assert_data_contains(self, expected: Dict[str, Any], msg: str = ""):
        """断言响应数据包含指定字段"""
        data = self._body.get('data', {})
        if isinstance(data, dict):
            for key, value in expected.items():
                assert key in data, f"Expected key '{key}' not in response data. {msg}"
                assert data[key] == value, f"Expected {key}={value}, got {key}={data[key]}. {msg}"


class MockApiClient:
    """
    Mock API 客户端（100% 内存，无真实 HTTP）
    
    使用方式：
        client = MockApiClient()
        resp = client.post('/api/auth/login', json={'username': 'admin', 'password': 'xxx'})
        resp.assert_success()
        token = resp.json()['data']['access_token']
    """

    def __init__(self, token: Optional[str] = None):
        self._token = token
        self._interceptors: Dict[str, List[Callable]] = {
            'request': [],
            'response': [],
        }
        self._mock_store: Dict[str, List[Dict[str, Any]]] = {
            'users': self._init_mock_users(),
            'roles': self._init_mock_roles(),
            'permissions': self._init_mock_permissions(),
            'entities': {},
        }

    def set_token(self, token: str):
        """设置认证 Token"""
        self._token = token

    def clear_token(self):
        """清除认证 Token"""
        self._token = None

    def add_request_interceptor(self, fn: Callable):
        """添加请求拦截器"""
        self._interceptors['request'].append(fn)

    def add_response_interceptor(self, fn: Callable):
        """添加响应拦截器"""
        self._interceptors['response'].append(fn)

    def _init_mock_users(self) -> List[Dict[str, Any]]:
        """初始化 Mock 用户数据"""
        return [
            {
                'id': SUPER_ADMIN_ID,
                'tenant_id': TENANT_ID_A,
                'username': 'admin',
                'email': 'admin@test.com',
                'full_name': '超级管理员',
                'status': 'ACTIVE',
                'create_by': SUPER_ADMIN_ID,
                'create_name': 'System',
                'create_time': '2026-01-01T00:00:00Z',
                'update_by': SUPER_ADMIN_ID,
                'update_name': 'System',
                'update_time': '2026-01-01T00:00:00Z',
                'delete_at': None,
            },
            {
                'id': ADMIN_USER_ID,
                'tenant_id': TENANT_ID_A,
                'username': 'admin_user',
                'email': 'admin_user@test.com',
                'full_name': '管理员',
                'status': 'ACTIVE',
                'create_by': SUPER_ADMIN_ID,
                'create_name': 'System',
                'create_time': '2026-01-01T00:00:00Z',
                'update_by': SUPER_ADMIN_ID,
                'update_name': 'System',
                'update_time': '2026-01-01T00:00:00Z',
                'delete_at': None,
            },
            {
                'id': NORMAL_USER_ID,
                'tenant_id': TENANT_ID_A,
                'username': 'user',
                'email': 'user@test.com',
                'full_name': '普通用户',
                'status': 'ACTIVE',
                'create_by': ADMIN_USER_ID,
                'create_name': '管理员',
                'create_time': '2026-01-02T00:00:00Z',
                'update_by': ADMIN_USER_ID,
                'update_name': '管理员',
                'update_time': '2026-01-02T00:00:00Z',
                'delete_at': None,
            },
            {
                'id': READONLY_USER_ID,
                'tenant_id': TENANT_ID_A,
                'username': 'readonly',
                'email': 'readonly@test.com',
                'full_name': '只读用户',
                'status': 'ACTIVE',
                'create_by': ADMIN_USER_ID,
                'create_name': '管理员',
                'create_time': '2026-01-02T00:00:00Z',
                'update_by': ADMIN_USER_ID,
                'update_name': '管理员',
                'update_time': '2026-01-02T00:00:00Z',
                'delete_at': None,
            },
        ]

    def _init_mock_roles(self) -> List[Dict[str, Any]]:
        """初始化 Mock 角色数据"""
        return [
            {
                'id': '00000000-0000-0000-0000-000000000101',
                'tenant_id': TENANT_ID_A,
                'code': 'super_admin',
                'name': '超级管理员',
                'is_system': True,
                'create_by': SUPER_ADMIN_ID,
                'create_name': 'System',
                'create_time': '2026-01-01T00:00:00Z',
                'update_by': SUPER_ADMIN_ID,
                'update_name': 'System',
                'update_time': '2026-01-01T00:00:00Z',
                'delete_at': None,
            },
            {
                'id': '00000000-0000-0000-0000-000000000102',
                'tenant_id': TENANT_ID_A,
                'code': 'admin',
                'name': '管理员',
                'is_system': True,
                'create_by': SUPER_ADMIN_ID,
                'create_name': 'System',
                'create_time': '2026-01-01T00:00:00Z',
                'update_by': SUPER_ADMIN_ID,
                'update_name': 'System',
                'update_time': '2026-01-01T00:00:00Z',
                'delete_at': None,
            },
        ]

    def _init_mock_permissions(self) -> List[Dict[str, Any]]:
        """初始化 Mock 权限数据"""
        return [
            {
                'id': '00000000-0000-0000-0000-000000000201',
                'tenant_id': TENANT_ID_A,
                'code': 'device:list:read',
                'name': '设备列表查询',
                'service': 'device',
                'resource': 'list',
                'action': 'read',
                'create_by': SUPER_ADMIN_ID,
                'create_name': 'System',
                'create_time': '2026-01-01T00:00:00Z',
                'update_by': SUPER_ADMIN_ID,
                'update_name': 'System',
                'update_time': '2026-01-01T00:00:00Z',
                'delete_at': None,
            },
            {
                'id': '00000000-0000-0000-0000-000000000202',
                'tenant_id': TENANT_ID_A,
                'code': 'device:create:write',
                'name': '设备新增',
                'service': 'device',
                'resource': 'create',
                'action': 'write',
                'create_by': SUPER_ADMIN_ID,
                'create_name': 'System',
                'create_time': '2026-01-01T00:00:00Z',
                'update_by': SUPER_ADMIN_ID,
                'update_name': 'System',
                'update_time': '2026-01-01T00:00:00Z',
                'delete_at': None,
            },
        ]

    def request(self, method: str, path: str, json: Dict[str, Any] = None,
                params: Dict[str, Any] = None, headers: Dict[str, str] = None) -> MockHttpResponse:
        """发送 HTTP 请求（内存模拟）"""
        
        # 运行请求拦截器
        for interceptor in self._interceptors['request']:
            path, json, params, headers = interceptor(path, json, params, headers)

        # 根据路径路由到不同的处理器
        if path.startswith('/api/auth/'):
            response = self._handle_auth(method, path, json, headers)
        elif path.startswith('/api/users/'):
            response = self._handle_users(method, path, json, headers)
        elif path.startswith('/api/roles/'):
            response = self._handle_roles(method, path, json, headers)
        elif path.startswith('/api/permissions/'):
            response = self._handle_permissions(method, path, json, headers)
        else:
            response = self._handle_generic(method, path, json, headers)

        # 运行响应拦截器
        for interceptor in self._interceptors['response']:
            response = interceptor(response)

        return response

    def get(self, path: str, **kwargs) -> MockHttpResponse:
        """GET 请求"""
        return self.request('GET', path, **kwargs)

    def post(self, path: str, json: Dict[str, Any] = None, **kwargs) -> MockHttpResponse:
        """POST 请求"""
        return self.request('POST', path, json=json, **kwargs)

    def put(self, path: str, json: Dict[str, Any] = None, **kwargs) -> MockHttpResponse:
        """PUT 请求"""
        return self.request('PUT', path, json=json, **kwargs)

    def patch(self, path: str, json: Dict[str, Any] = None, **kwargs) -> MockHttpResponse:
        """PATCH 请求"""
        return self.request('PATCH', path, json=json, **kwargs)

    def delete(self, path: str, **kwargs) -> MockHttpResponse:
        """DELETE 请求"""
        return self.request('DELETE', path, **kwargs)

    # ─────────────────────────────────────────────────────
    # 处理器实现
    # ─────────────────────────────────────────────────────

    def _handle_auth(self, method: str, path: str, json: Dict[str, Any], headers: Dict[str, str]) -> MockHttpResponse:
        """处理认证请求"""
        if path == '/api/auth/login' and method == 'POST':
            username = json.get('username') if json else None
            password = json.get('password') if json else None
            
            # 验证账号密码
            if username == 'admin' and password == 'P@ssw0rd':
                return MockHttpResponse(
                    HttpStatus.OK.value,
                    ApiResult(
                        success=True,
                        code=HttpStatus.OK.value,
                        data={'access_token': MOCK_TOKEN_ADMIN, 'token_type': 'Bearer'},
                        message='登录成功'
                    ).to_dict()
                )
            elif username == 'user' and password == 'P@ssw0rd':
                return MockHttpResponse(
                    HttpStatus.OK.value,
                    ApiResult(
                        success=True,
                        code=HttpStatus.OK.value,
                        data={'access_token': MOCK_TOKEN_USER, 'token_type': 'Bearer'},
                        message='登录成功'
                    ).to_dict()
                )
            else:
                return MockHttpResponse(
                    HttpStatus.UNAUTHORIZED.value,
                    ApiResult(
                        success=False,
                        code=HttpStatus.UNAUTHORIZED.value,
                        message='用户名或密码错误'
                    ).to_dict()
                )
        
        elif path == '/api/auth/logout' and method == 'POST':
            self.clear_token()
            return MockHttpResponse(
                HttpStatus.OK.value,
                ApiResult(
                    success=True,
                    code=HttpStatus.OK.value,
                    message='登出成功'
                ).to_dict()
            )
        
        else:
            return MockHttpResponse(
                HttpStatus.NOT_FOUND.value,
                ApiResult(
                    success=False,
                    code=HttpStatus.NOT_FOUND.value,
                    message='路由未找到'
                ).to_dict()
            )

    def _handle_users(self, method: str, path: str, json: Dict[str, Any], headers: Dict[str, str]) -> MockHttpResponse:
        """处理用户请求"""
        # 令牌验证：必须有有效的令牌
        if not self._token:
            return MockHttpResponse(
                HttpStatus.UNAUTHORIZED.value,
                ApiResult(
                    success=False,
                    code=HttpStatus.UNAUTHORIZED.value,
                    message='未登录，请先认证'
                ).to_dict()
            )

        # 验证令牌格式和内容（简单验证）
        if self._token not in [MOCK_TOKEN_ADMIN, MOCK_TOKEN_USER]:
            return MockHttpResponse(
                HttpStatus.UNAUTHORIZED.value,
                ApiResult(
                    success=False,
                    code=HttpStatus.UNAUTHORIZED.value,
                    message='令牌无效或已过期'
                ).to_dict()
            )

        if path == '/api/users/list' and method == 'GET':
            # 返回用户列表
            users = [u for u in self._mock_store['users'] if u['delete_at'] is None]
            return MockHttpResponse(
                HttpStatus.OK.value,
                PagedResult(
                    success=True,
                    code=HttpStatus.OK.value,
                    total=len(users),
                    page=1,
                    pageSize=10,
                    items=users,
                    message='查询成功'
                ).to_dict()
            )
        else:
            return MockHttpResponse(
                HttpStatus.NOT_FOUND.value,
                ApiResult(
                    success=False,
                    code=HttpStatus.NOT_FOUND.value,
                    message='路由未找到'
                ).to_dict()
            )

    def _handle_roles(self, method: str, path: str, json: Dict[str, Any], headers: Dict[str, str]) -> MockHttpResponse:
        """处理角色请求"""
        if not self._token:
            return MockHttpResponse(
                HttpStatus.UNAUTHORIZED.value,
                ApiResult(
                    success=False,
                    code=HttpStatus.UNAUTHORIZED.value,
                    message='未登录'
                ).to_dict()
            )

        # 验证令牌有效性
        if self._token not in [MOCK_TOKEN_ADMIN, MOCK_TOKEN_USER]:
            return MockHttpResponse(
                HttpStatus.UNAUTHORIZED.value,
                ApiResult(
                    success=False,
                    code=HttpStatus.UNAUTHORIZED.value,
                    message='令牌无效或已过期'
                ).to_dict()
            )

        if path == '/api/roles/list' and method == 'GET':
            roles = [r for r in self._mock_store['roles'] if r['delete_at'] is None]
            return MockHttpResponse(
                HttpStatus.OK.value,
                PagedResult(
                    success=True,
                    code=HttpStatus.OK.value,
                    total=len(roles),
                    page=1,
                    pageSize=10,
                    items=roles,
                    message='查询成功'
                ).to_dict()
            )
        else:
            return MockHttpResponse(
                HttpStatus.NOT_FOUND.value,
                ApiResult(
                    success=False,
                    code=HttpStatus.NOT_FOUND.value,
                    message='路由未找到'
                ).to_dict()
            )

    def _handle_permissions(self, method: str, path: str, json: Dict[str, Any], headers: Dict[str, str]) -> MockHttpResponse:
        """处理权限请求"""
        if not self._token:
            return MockHttpResponse(
                HttpStatus.UNAUTHORIZED.value,
                ApiResult(
                    success=False,
                    code=HttpStatus.UNAUTHORIZED.value,
                    message='未登录'
                ).to_dict()
            )

        # 验证令牌有效性
        if self._token not in [MOCK_TOKEN_ADMIN, MOCK_TOKEN_USER]:
            return MockHttpResponse(
                HttpStatus.UNAUTHORIZED.value,
                ApiResult(
                    success=False,
                    code=HttpStatus.UNAUTHORIZED.value,
                    message='令牌无效或已过期'
                ).to_dict()
            )

        if path == '/api/permissions/list' and method == 'GET':
            perms = [p for p in self._mock_store['permissions'] if p['delete_at'] is None]
            return MockHttpResponse(
                HttpStatus.OK.value,
                PagedResult(
                    success=True,
                    code=HttpStatus.OK.value,
                    total=len(perms),
                    page=1,
                    pageSize=10,
                    items=perms,
                    message='查询成功'
                ).to_dict()
            )
        else:
            return MockHttpResponse(
                HttpStatus.NOT_FOUND.value,
                ApiResult(
                    success=False,
                    code=HttpStatus.NOT_FOUND.value,
                    message='路由未找到'
                ).to_dict()
            )

    def _handle_generic(self, method: str, path: str, json: Dict[str, Any], headers: Dict[str, str]) -> MockHttpResponse:
        """处理通用请求"""
        return MockHttpResponse(
            HttpStatus.NOT_FOUND.value,
            ApiResult(
                success=False,
                code=HttpStatus.NOT_FOUND.value,
                message='路由未找到'
            ).to_dict()
        )


# ═══════════════════════════════════════════════════════════
# 4. 测试断言助手
# ═══════════════════════════════════════════════════════════

class AssertionHelper:
    """测试断言助手（简化常见检查）"""

    @staticmethod
    def assert_api_success(resp: MockHttpResponse, msg: str = ""):
        """断言 API 返回成功"""
        assert resp.is_success, f"Expected success response (2xx), got {resp.status_code}. {msg}"

    @staticmethod
    def assert_api_error(resp: MockHttpResponse, error_code: ErrorCode, msg: str = ""):
        """断言 API 返回特定错误"""
        assert not resp.is_success, f"Expected error response, got success. {msg}"
        body = resp.json()
        assert body.get('code') == error_code.value, f"Expected error code {error_code.value}, got {body.get('code')}. {msg}"

    @staticmethod
    def assert_status_code(resp: MockHttpResponse, expected: HttpStatus, msg: str = ""):
        """断言 HTTP 状态码"""
        assert resp.status_code == expected.value, f"Expected {expected.value}, got {resp.status_code}. {msg}"

    @staticmethod
    def assert_data_field_exists(resp: MockHttpResponse, field: str, msg: str = ""):
        """断言响应数据包含指定字段"""
        body = resp.json()
        data = body.get('data', {})
        assert field in data, f"Expected field '{field}' in response data. {msg}"

    @staticmethod
    def assert_data_field_value(resp: MockHttpResponse, field: str, expected_value: Any, msg: str = ""):
        """断言响应数据字段值"""
        body = resp.json()
        data = body.get('data', {})
        actual_value = data.get(field)
        assert actual_value == expected_value, f"Expected {field}={expected_value}, got {field}={actual_value}. {msg}"

    @staticmethod
    def assert_paged_result(resp: MockHttpResponse, min_items: int = 0, msg: str = ""):
        """断言分页结果"""
        body = resp.json()
        assert 'total' in body, f"Expected 'total' field in paged result. {msg}"
        assert 'page' in body, f"Expected 'page' field in paged result. {msg}"
        assert 'pageSize' in body, f"Expected 'pageSize' field in paged result. {msg}"
        assert 'items' in body, f"Expected 'items' field in paged result. {msg}"
        assert len(body['items']) >= min_items, f"Expected at least {min_items} items, got {len(body['items'])}. {msg}"

    @staticmethod
    def assert_data_has_all_base_fields(data: Dict[str, Any], msg: str = ""):
        """断言数据包含所有基础字段（9 个公共字段）"""
        required_fields = ['id', 'tenant_id', 'create_by', 'create_name', 'create_time',
                          'update_by', 'update_name', 'update_time', 'delete_at']
        for field in required_fields:
            assert field in data, f"Expected required field '{field}' in data. {msg}"

    @staticmethod
    def assert_soft_delete_visible(resp: MockHttpResponse, should_exist: bool = True, msg: str = ""):
        """断言软删除后数据是否可见"""
        body = resp.json()
        if isinstance(body.get('data'), list):
            items = body['data']
        elif isinstance(body.get('items'), list):
            items = body['items']
        else:
            items = [body.get('data', {})]

        for item in items:
            delete_at = item.get('delete_at')
            if should_exist:
                assert delete_at is None, f"Expected item to be visible (delete_at=None), got delete_at={delete_at}. {msg}"
            else:
                assert delete_at is not None, f"Expected item to be deleted (delete_at not None), got delete_at={delete_at}. {msg}"


# ═══════════════════════════════════════════════════════════
# 5. 导出公共接口
# ═══════════════════════════════════════════════════════════

__all__ = [
    'ApiResult',
    'PagedResult',
    'BaseEntity',
    'User',
    'Role',
    'Permission',
    'MockHttpResponse',
    'MockApiClient',
    'AssertionHelper',
    'HttpStatus',
    'ErrorCode',
    'SUPER_ADMIN_ID',
    'ADMIN_USER_ID',
    'NORMAL_USER_ID',
    'READONLY_USER_ID',
    'TENANT_ID_A',
    'TENANT_ID_B',
    'MOCK_TOKEN_ADMIN',
    'MOCK_TOKEN_USER',
]
