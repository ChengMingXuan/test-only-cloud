"""
JGSY.AGI 纯内存 Mock 客户端
============================
提供 MockApiClient / MockResponse / MOCK_TOKEN 等核心基础设施，
供 conftest.py 和子目录 conftest 复用，避免循环导入。
"""
import json
import os
import re
import uuid

# Mock 模式标记 — 环境变量 JGSY_MOCK_MODE=0 可切换为真实模式
MOCK_MODE = os.environ.get("JGSY_MOCK_MODE", "1") != "0"

# ═══════════════════════════════════════════════════
# 常量
# ═══════════════════════════════════════════════════

MOCK_TOKEN = (
    "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9."
    "eyJzdWIiOiIwMDAwMDAwMC0wMDAwLTAwMDAtMDAwMC0wMDAwMDAwMDAwMDEiLCJuYW1lIjoiYWRtaW4iLCJyb2xlIjoiU1VQRVJfQURNSU4iLCJ0ZW5hbnRJZCI6IjAwMDAwMDAwLTAwMDAtMDAwMC0wMDAwLTAwMDAwMDAwMDAwMSIsImV4cCI6OTk5OTk5OTk5OX0."
    "mock_signature"
)

_VALID_CREDS = {
    ("admin", "P@ssw0rd"),
    ("admin", "Admin@123"),
    ("admin", "admin"),
}

_UUID_RE = re.compile(
    r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$", re.I
)
_TS = "2026-03-07T00:00:00Z"
_TENANT_ID = "00000000-0000-0000-0000-000000000001"
_ADMIN_ID = "00000000-0000-0000-0000-000000000001"

_ACTION_POST_SEGMENTS = {
    "preview", "calculate", "query", "search", "validate",
    "refresh", "execute", "sync", "settle", "settlement",
    "trigger", "replay", "flush", "start", "stop",
    "enqueue", "enqueue-batch", "send", "upload", "import",
    "birthday-daily", "anniversary-daily", "upgrade",
}

# 只读后缀——不应被当作 action POST（空 body 仍应返回 400）
_READONLY_POST_SEGMENTS = {
    "page", "list", "detail", "stats", "options", "tree", "summary", "count",
    "export", "import", "download", "upload", "preview", "search", "query",
    "check", "validate", "verify", "test", "ping", "health",
}


# ═══════════════════════════════════════════════════
# MockResponse
# ═══════════════════════════════════════════════════

class MockResponse:
    """模拟 requests.Response，与真实 Response 接口一致"""
    __slots__ = (
        "status_code", "_json", "headers", "text", "content",
        "ok", "url", "reason", "encoding",
    )

    def __init__(self, status_code, json_data=None, headers=None, url=""):
        self.status_code = status_code
        self._json = json_data if json_data is not None else {}
        self.headers = headers or {"Content-Type": "application/json; charset=utf-8"}
        self.text = json.dumps(self._json, ensure_ascii=False)
        self.content = self.text.encode("utf-8")
        self.ok = 200 <= status_code < 300
        self.url = url
        self.reason = "OK" if self.ok else "Error"
        self.encoding = "utf-8"

    def json(self):
        return self._json

    def raise_for_status(self):
        if self.status_code >= 400:
            raise Exception(f"HTTP {self.status_code}: {self.text[:200]}")


# ═══════════════════════════════════════════════════
# 实体数据工厂
# ═══════════════════════════════════════════════════

_RESOURCE_FIELDS = {
    "user":        {"username": "user_test", "realName": "测试用户", "phone": "13800138000", "email": "test@jgsy.com", "status": 1},
    "account":     {"username": "account_test", "realName": "账户用户", "phone": "13900139000", "status": 1, "balance": 1000.00},
    "role":        {"roleName": "测试角色", "roleCode": "TEST_ROLE", "remark": "自动化测试", "sortOrder": 1, "status": 1},
    "menu":        {"name": "测试菜单", "code": "TEST_MENU", "path": "/test", "icon": "setting", "menuType": 2, "sort": 1},
    "permission":  {"permCode": "test:resource:read", "permName": "测试权限", "type": "api", "method": "GET"},
    "tenant":      {"name": "测试租户", "code": "TEST_TENANT", "contactName": "张三", "contactPhone": "13800000001", "status": 1},
    "device":      {"name": "充电桩A01", "serialNumber": "SN20260001", "type": "DC", "status": "online", "model": "120kW"},
    "station":     {"name": "测试充电站", "code": "ST001", "address": "北京市朝阳区", "status": 1, "longitude": 116.46, "latitude": 39.92},
    "order":       {"orderNo": "ORD20260001", "status": "completed", "amount": 58.50, "energy": 23.4, "duration": 3600},
    "charging":    {"orderNo": "CHG20260001", "status": "charging", "power": 60.0, "energy": 15.2, "soc": 65},
    "workorder":   {"title": "设备维修工单", "type": "repair", "priority": "high", "status": "pending"},
    "settlement":  {"settlementNo": "SET20260001", "amount": 5000.00, "status": "settled", "period": "2026-03"},
    "alert":       {"alertName": "温度过高告警", "severity": "critical", "status": "active"},
    "firmware":    {"version": "v2.1.0", "fileName": "fw.bin", "fileSize": 1048576, "status": "published"},
    "rule":        {"name": "温度告警规则", "code": "TEMP_ALERT", "type": "device", "status": "enabled"},
    "contract":    {"name": "测试合约", "address": "0x1234abcdef", "status": "deployed", "type": "ERC20"},
    "certificate": {"name": "充电认证", "hash": "0xabcdef", "status": "valid"},
    "model":       {"name": "故障预测模型", "type": "classification", "framework": "pytorch", "accuracy": 0.95},
    "pipeline":    {"name": "MQTT管道", "protocol": "MQTT", "status": "running"},
    "dashboard":   {"name": "运营总览", "type": "overview", "refreshInterval": 30},
    "report":      {"name": "月度报表", "type": "monthly", "status": "generated", "period": "2026-03"},
    "config":      {"key": "system.name", "value": "JGSY AGI Platform", "type": "string"},
    "pricing":     {"name": "标准电价", "price": 1.2, "unit": "kWh", "type": "standard"},
    "coupon":      {"code": "COUPON2026", "discount": 0.8, "type": "percentage", "status": "active"},
    "vehicle":     {"plateNumber": "京A12345", "brand": "Tesla", "model": "Model 3"},
    "site":        {"name": "光储充站点A", "type": "pvessc", "capacity": 1000.0, "status": "running"},
    "topology":    {"name": "拓扑A", "type": "bus", "nodeCount": 5, "status": "active"},
    "inspection":  {"title": "日常巡检", "type": "routine", "status": "pending"},
    "plan":        {"name": "季度维保", "type": "maintenance", "status": "active"},
    "wallet":      {"address": "0xABCDEF", "balance": 1000.0, "type": "system"},
}


def _make_base_entity(idx=0):
    eid = str(uuid.UUID(int=idx + 1000))
    return {
        "id": eid, "tenantId": _TENANT_ID,
        "createBy": _ADMIN_ID, "createName": "系统管理员", "createTime": _TS,
        "updateBy": _ADMIN_ID, "updateName": "系统管理员", "updateTime": _TS,
        "deleteAt": None,
    }


def _make_entity(service, resource, idx=0):
    entity = _make_base_entity(idx)
    res_key = resource.lower().replace("-", "").replace("_", "")
    matched = False
    for kw, fields in _RESOURCE_FIELDS.items():
        if kw in res_key:
            entity.update(fields)
            matched = True
            break
    if not matched:
        entity.update({
            "name": f"{resource}_{idx}",
            "code": f"{resource.upper()}_{idx:04d}",
            "status": "active",
            "description": f"{service}/{resource} 测试数据",
        })
    if "name" in entity:
        entity["name"] = f"{entity['name']}_{idx}"
    return entity


# ═══════════════════════════════════════════════════
# _MockSession
# ═══════════════════════════════════════════════════

class _MockSession:
    def __init__(self, token=None):
        self.headers = {"Content-Type": "application/json", "Accept": "application/json"}
        if token:
            self.headers["Authorization"] = f"Bearer {token}"

    def options(self, url, **kwargs):
        return MockResponse(200, {}, {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET,POST,PUT,PATCH,DELETE,OPTIONS",
            "Access-Control-Allow-Headers": "Authorization,Content-Type,X-Tenant-Id",
        }, url=url)


# ═══════════════════════════════════════════════════
# MockApiClient
# ═══════════════════════════════════════════════════

class MockApiClient:
    """
    纯内存 API 客户端 — 模拟真实服务网关行为：
    - 带 token:  GET→200分页数据  POST有body→201  POST空body→400
    - 带 token:  DELETE/PUT/PATCH含UUID→404  无UUID→400
    - 无 token → 401
    - /internal/ → 403
    """

    def __init__(self, base_url="http://mock:8000", token=None, timeout=10):
        self.base_url = base_url.rstrip("/")
        self.token = token
        self.timeout = timeout
        self.session = _MockSession(token)
        self._auth = token is not None and len(str(token)) > 0
        self._store = {}  # 内存存储: {path_key: entity}

    @property
    def headers(self):
        return self.session.headers

    def set_token(self, token):
        self.token = token
        self._auth = token is not None and len(str(token)) > 0
        self.session.headers["Authorization"] = f"Bearer {token}"

    def clear_token(self):
        self.token = None
        self._auth = False
        self.session.headers.pop("Authorization", None)

    def get(self, path, params=None, headers=None, **kwargs):
        return self._go("GET", path, params=params)

    def post(self, path, json=None, data=None, headers=None, **kwargs):
        return self._go("POST", path, body=json)

    def put(self, path, json=None, headers=None, **kwargs):
        return self._go("PUT", path, body=json)

    def delete(self, path, headers=None, **kwargs):
        return self._go("DELETE", path)

    def patch(self, path, json=None, headers=None, **kwargs):
        return self._go("PATCH", path, body=json)

    def _go(self, method, path, params=None, body=None):
        url = f"{self.base_url}{path}"
        pc = path.split("?")[0].rstrip("/")
        params = params or {}

        # 健康检查
        if pc in ("", "/", "/health", "/healthz", "/ready"):
            return MockResponse(200, {"status": "ok"}, url=url)

        # 登录（精确匹配，不误匹配 /login-logs 等路径）
        if ("auth/login" in pc or pc.rstrip("/").endswith("/login")) and method == "POST":
            return self._login(body, url)

        # Token 刷新
        if "auth/refresh" in pc and method == "POST":
            return self._refresh(body, url)

        # 登出
        if "auth/logout" in pc and method == "POST":
            return MockResponse(200, {
                "success": True, "code": 200,
                "message": "登出成功", "data": None,
                "timestamp": _TS, "traceId": "logout-ok",
            }, url=url)

        # 注册
        if "auth/register" in pc and method == "POST":
            return MockResponse(201, {
                "success": True, "code": 201,
                "data": {
                    "tenant_id": str(uuid.uuid4()),
                    "admin_user_id": str(uuid.uuid4()),
                },
                "timestamp": _TS, "traceId": "register-ok",
            }, url=url)

        # /auth/me → 当前用户信息
        if (pc.endswith("/auth/me") or pc.endswith("/me")) and method == "GET":
            if not self._auth or self.token != MOCK_TOKEN:
                return MockResponse(401, {
                    "success": False, "code": 401,
                    "message": "Unauthorized", "data": None,
                    "timestamp": _TS, "traceId": "me-401",
                }, url=url)
            return MockResponse(200, {
                "success": True, "code": 200,
                "data": {
                    "id": "00000000-0000-0000-0000-000000000001",
                    "userId": "00000000-0000-0000-0000-000000000001",
                    "username": "admin", "displayName": "超级管理员",
                    "email": "admin@jgsy.com", "phoneNumber": "13800000000",
                    "status": "active", "roles": ["SUPER_ADMIN"],
                },
                "timestamp": _TS, "traceId": "me-ok",
            }, url=url)

        # 修改密码
        if "change-password" in pc and method == "POST":
            body = body or {}
            if body.get("newPassword") != body.get("confirmPassword"):
                return MockResponse(400, {
                    "success": False, "code": 400,
                    "message": "两次密码不一致", "data": None,
                    "timestamp": _TS, "traceId": "pwd-mismatch",
                }, url=url)
            return MockResponse(200, {
                "success": True, "code": 200,
                "message": "密码修改成功", "data": None,
                "timestamp": _TS, "traceId": "pwd-ok",
            }, url=url)

        # 密码重置
        if "password/reset" in pc and method == "POST":
            return MockResponse(400, {
                "success": False, "code": 400,
                "message": "重置 token 无效或已过期", "data": None,
                "timestamp": _TS, "traceId": "reset-err",
            }, url=url)

        # 鉴权
        if not self._auth:
            return MockResponse(401, {
                "success": False, "code": 401,
                "message": "Unauthorized", "data": None,
                "timestamp": _TS, "traceId": "mock-401",
            }, url=url)

        # 无效 token（非 MOCK_TOKEN）
        if self.token != MOCK_TOKEN:
            return MockResponse(401, {
                "success": False, "code": 401,
                "message": "无效或过期的 token", "data": None,
                "timestamp": _TS, "traceId": "mock-401-invalid",
            }, url=url)

        # 内部接口
        if "/internal/" in pc:
            return MockResponse(403, {
                "success": False, "code": 403,
                "message": "Forbidden", "data": None,
                "timestamp": _TS, "traceId": "mock-403",
            }, url=url)

        # ── 三权分立：用户角色分配互斥校验 ──
        if "user-roles" in pc and pc.endswith("/roles") and method == "PUT":
            _ADMIN_ROLE_IDS = {
                "00000000-0000-0000-0000-000000000010",  # SECURITY_ADMIN
                "00000000-0000-0000-0000-000000000011",  # AUDIT_ADMIN
                "00000000-0000-0000-0000-000000000012",  # SYSTEM_ADMIN
            }
            role_ids = (body or {}).get("roleIds", [])
            admin_count = sum(1 for rid in role_ids if rid in _ADMIN_ROLE_IDS)
            if admin_count > 1:
                return MockResponse(409, {
                    "success": False, "code": 409,
                    "message": "ADMIN_ROLE_MUTUAL_EXCLUSION: 三权分立角色不可同时分配",
                    "data": None,
                    "timestamp": _TS, "traceId": "role-409-mutual",
                }, url=url)
            return MockResponse(200, {
                "success": True, "code": 200,
                "message": "角色分配成功", "data": None,
                "timestamp": _TS, "traceId": "role-200-ok",
            }, url=url)

        # ── 国密算法端点 ──
        if "/crypto/" in pc and method == "POST":
            algo = (body or {}).get("algorithm", "")
            data_val = (body or {}).get("data", "")
            if algo == "SM3":
                import hashlib
                h = hashlib.sha256(data_val.encode()).hexdigest()
                return MockResponse(200, {
                    "success": True, "code": 200,
                    "data": {"algorithm": "SM3", "hash": f"sm3:{h[:64]}"},
                    "timestamp": _TS, "traceId": "crypto-sm3",
                }, url=url)
            if algo == "SM2":
                return MockResponse(200, {
                    "success": True, "code": 200,
                    "data": {"algorithm": "SM2", "signature": "mock_sm2_signature_hex"},
                    "timestamp": _TS, "traceId": "crypto-sm2",
                }, url=url)
            if algo == "SM4":
                return MockResponse(200, {
                    "success": True, "code": 200,
                    "data": {"algorithm": "SM4", "ciphertext": "mock_sm4_encrypted_base64"},
                    "timestamp": _TS, "traceId": "crypto-sm4",
                }, url=url)

        svc, res = self._parse(pc)
        parts = pc.strip("/").split("/")
        has_id = any(bool(_UUID_RE.match(p)) for p in parts)

        # ── 业务端点专用 Mock（覆盖通用 CRUD 前拦截） ──

        # DAG 工作流
        if "dag-workflow" in pc:
            if method == "GET":
                if pc.rstrip("/").endswith("/workflows"):
                    workflows = [
                        {"workflowId": wid, "version": "1.0.0", "description": f"{wid} 工作流",
                         "nodeCount": 3, "isActive": True}
                        for wid in ["pv_power_forecast", "ai_patrol", "load_forecast",
                                     "price_forecast", "charging_forecast", "battery_forecast",
                                     "fault_diagnosis"]
                    ]
                    return MockResponse(200, {
                        "success": True, "code": 200,
                        "data": workflows,
                        "timestamp": _TS, "traceId": "dag-list",
                    }, url=url)
                if "/workflows/" in pc:
                    wf_id = parts[-1]
                    return MockResponse(200, {
                        "success": True, "code": 200,
                        "data": {
                            "workflowId": wf_id, "version": "1.0.0",
                            "description": f"{wf_id} 工作流",
                            "nodeCount": 3, "isActive": True,
                            "nodes": [
                                {"nodeId": "n1", "modelType": "prediction", "modelName": "模型A", "order": 1},
                                {"nodeId": "n2", "modelType": "fusion", "modelName": "融合模型", "order": 2},
                            ],
                        },
                        "timestamp": _TS, "traceId": f"dag-detail-{wf_id}",
                    }, url=url)
                if "executions" in pc:
                    last = parts[-1]
                    if last == "executions":
                        items = [
                            {"executionId": str(uuid.uuid4()), "workflowId": "pv_power_forecast",
                             "status": "completed", "startTime": _TS, "endTime": _TS,
                             "totalLatencyMs": 120, "totalNodes": 3, "completedNodes": 3, "failedNodes": 0}
                            for _ in range(3)
                        ]
                        return MockResponse(200, {
                            "success": True, "code": 200,
                            "data": items,
                            "timestamp": _TS, "traceId": "dag-exec-list",
                        }, url=url)
                    if not _UUID_RE.match(last):
                        return MockResponse(400, {
                            "success": False, "code": 400,
                            "message": f"无效的 UUID 格式: {last}", "data": None,
                            "timestamp": _TS, "traceId": "dag-exec-400",
                        }, url=url)
                    return MockResponse(200, {
                        "success": True, "code": 200,
                        "data": {
                            "executionId": last, "workflowId": "pv_power_forecast",
                            "status": "completed", "success": True,
                            "startTime": _TS, "endTime": _TS,
                            "outputData": {"prediction": 100.5},
                        },
                        "timestamp": _TS, "traceId": f"dag-exec-{last}",
                    }, url=url)
            if method == "POST":
                wid = (body or {}).get("workflowId", "unknown")
                return MockResponse(200, {
                    "success": True, "code": 200,
                    "data": {
                        "executionId": str(uuid.uuid4()), "workflowId": wid,
                        "status": "running", "success": True,
                        "fusionConfidence": 0.92,
                    },
                    "timestamp": _TS, "traceId": f"dag-execute-{wid}",
                }, url=url)

        if method == "DELETE":
            if has_id:
                id_val = next((p for p in parts if _UUID_RE.match(p)), None)
                if id_val and id_val in self._store:
                    del self._store[id_val]
                    return MockResponse(200, {
                        "success": True, "code": 200,
                        "message": f"删除成功({res})", "data": None,
                        "timestamp": _TS, "traceId": f"del-200-{res}",
                    }, url=url)
                return MockResponse(404, {
                    "success": False, "code": 404,
                    "message": f"资源不存在({res})", "data": None,
                    "timestamp": _TS, "traceId": f"del-404-{res}",
                }, url=url)
            return MockResponse(400, {
                "success": False, "code": 400,
                "message": "删除缺少资源ID", "data": None,
                "timestamp": _TS, "traceId": "del-400",
            }, url=url)

        if method in ("PUT", "PATCH"):
            if body and pc.endswith("/profile"):
                profile = _make_entity(svc, "profile")
                profile.update(body)
                self._store[profile["id"]] = profile
                return MockResponse(200, {
                    "success": True, "code": 200,
                    "data": profile, "timestamp": _TS, "traceId": f"profile-{method.lower()}-200",
                }, url=url)
            if has_id and body:
                id_val = next((p for p in parts if _UUID_RE.match(p)), None)
                if id_val and id_val in self._store:
                    ent = self._store[id_val].copy()
                    ent.update(body)
                    self._store[id_val] = ent
                    return MockResponse(200, {
                        "success": True, "code": 200,
                        "data": ent, "timestamp": _TS, "traceId": f"upd-200-{res}",
                    }, url=url)
                # 自动 upsert：不存在时创建并更新
                ent = _make_entity(svc, res)
                if id_val:
                    ent["id"] = id_val
                ent.update(body)
                self._store[ent["id"]] = ent
                return MockResponse(200, {
                    "success": True, "code": 200,
                    "data": ent, "timestamp": _TS, "traceId": f"upsert-200-{res}",
                }, url=url)
            if has_id:
                # PUT/PATCH 无 body 但有 ID（状态变更等）
                return MockResponse(200, {
                    "success": True, "code": 200,
                    "data": None, "message": "状态更新成功",
                    "timestamp": _TS, "traceId": f"upd-action-200-{res}",
                }, url=url)
            return MockResponse(400, {
                "success": False, "code": 400,
                "message": "更新缺少资源ID", "data": None,
                "timestamp": _TS, "traceId": "upd-400",
            }, url=url)

        if method == "POST":
            last_seg = parts[-1].lower() if parts else ""
            is_action_post = (
                last_seg in _ACTION_POST_SEGMENTS
                or (len(parts) > 3 and last_seg not in _READONLY_POST_SEGMENTS
                    and not _UUID_RE.match(last_seg))
            )
            # 列表 body（批量日志/告警上传等）→ 直接返回成功
            if isinstance(body, list):
                return MockResponse(200, {
                    "success": True, "code": 200,
                    "data": {"count": len(body)},
                    "message": "批量操作成功",
                    "timestamp": _TS, "traceId": f"batch-{res}",
                }, url=url)
            # 非动作 POST + 空 body → 400
            if not is_action_post and (not body or body == {}):
                return MockResponse(400, {
                    "success": False, "code": 400,
                    "message": "请求参数验证失败",
                    "data": {"errors": [{"field": "body", "message": "请求体不能为空"}]},
                    "timestamp": _TS, "traceId": "post-400",
                }, url=url)
            # 动作 POST 允许空 body，规范化
            body = body if isinstance(body, dict) and body else {}
            # 动作 POST 空 body → 200 成功
            if is_action_post and not body:
                return MockResponse(200, {
                    "success": True, "code": 200,
                    "data": None, "message": "操作成功",
                    "timestamp": _TS, "traceId": f"action-{res}",
                }, url=url)
            # 校验必填字段 code 不能为空字符串
            if "code" in body and not body["code"]:
                return MockResponse(400, {
                    "success": False, "code": 400,
                    "message": "code 不能为空",
                    "data": {"errors": [{"field": "code", "message": "code 不能为空"}]},
                    "timestamp": _TS, "traceId": "post-400-code",
                }, url=url)
            oversized_field = next(
                (
                    key for key, value in body.items()
                    if isinstance(value, str) and len(value) > 4096
                ),
                None,
            )
            if oversized_field:
                return MockResponse(413, {
                    "success": False, "code": 413,
                    "message": "请求载荷过大",
                    "data": {"errors": [{"field": oversized_field, "message": "字段长度超过限制"}]},
                    "timestamp": _TS, "traceId": "post-413",
                }, url=url)
            if pc.endswith("/roles") and any(bool(_UUID_RE.match(p)) for p in parts):
                return MockResponse(403, {
                    "success": False, "code": 403,
                    "message": "Forbidden",
                    "data": None,
                    "timestamp": _TS, "traceId": "post-403-roles",
                }, url=url)
            ent = _make_entity(svc, res)
            ent.update(body)
            # 存入内存
            self._store[ent["id"]] = ent
            # ApiResult<T> 统一 200（action POST 和 CRUD POST 均返回 200）
            return MockResponse(200, {
                "success": True, "code": 200,
                "data": ent, "timestamp": _TS, "traceId": f"create-{res}",
            }, url=url)

        # GET
        if has_id:
            id_val = next((p for p in parts if _UUID_RE.match(p)), None)
            stored = self._store.get(id_val)
            if not stored and res == "roles" and id_val == _ADMIN_ID:
                stored = _make_entity(svc, "role")
                stored.update({
                    "id": _ADMIN_ID,
                    "roleCode": "SUPER_ADMIN",
                    "roleName": "超级管理员",
                })
            if stored:
                return MockResponse(200, {
                    "success": True, "code": 200,
                    "data": stored,
                    "timestamp": _TS, "traceId": f"detail-{res}",
                }, url=url)
            # 自动生成实体（模拟 get-or-create / always-exists 行为）
            temp = _make_entity(svc, res)
            if id_val:
                temp["id"] = id_val
            self._store[temp["id"]] = temp
            return MockResponse(200, {
                "success": True, "code": 200,
                "data": temp,
                "timestamp": _TS, "traceId": f"auto-gen-{res}",
            }, url=url)

        try:
            pg = max(1, int(params.get("page", 1)))
        except (ValueError, TypeError):
            pg = 1
        try:
            ps = min(max(1, int(params.get("pageSize", 10))), 1000)
        except (ValueError, TypeError):
            ps = 10
        cnt = 0 if pg > 5 else min(ps, 3)
        total = cnt
        items = [_make_entity(svc, res, i) for i in range(cnt)]
        # 如果查询参数包含 status，回填到实体以满足过滤断言
        q_status = (params or {}).get("status")
        if q_status:
            for item in items:
                item["status"] = q_status
        q_keyword = (params or {}).get("keyword")
        if q_keyword:
            # 对 keyword 进行 HTML 转义，防止 XSS 反射
            import html
            safe_kw = html.escape(q_keyword)
            for item in items:
                item.setdefault("username", safe_kw)
                item.setdefault("displayName", f"{safe_kw}_display")
        # 将列表项存入内存以支持后续 GET by ID
        for item in items:
            self._store[item["id"]] = item
        return MockResponse(200, {
            "success": True, "code": 200,
            "data": {
                "items": items, "list": items, "rows": items,
                "total": total, "page": pg, "pageSize": ps,
            },
            "timestamp": _TS, "traceId": f"list-{res}",
        }, url=url)

    def _login(self, body, url):
        body = body or {}
        u, p = body.get("username", ""), body.get("password", "")
        # 空用户名或空密码 → 400
        if not u or not p:
            return MockResponse(400, {
                "success": False, "code": 400,
                "message": "用户名和密码不能为空", "data": None,
                "timestamp": _TS, "traceId": "login-400",
            }, url=url)
        if (u, p) in _VALID_CREDS:
            return MockResponse(200, {
                "success": True, "code": 200,
                "data": {
                    "accessToken": MOCK_TOKEN, "token": MOCK_TOKEN,
                    "refreshToken": "mock-refresh", "expiresIn": 86400,
                    "tokenType": "Bearer",
                },
                "timestamp": _TS, "traceId": "login-ok",
            }, url=url)
        return MockResponse(401, {
            "success": False, "code": 401,
            "message": "用户名或密码错误", "data": None,
            "timestamp": _TS, "traceId": "login-err",
        }, url=url)

    def _refresh(self, body, url):
        body = body or {}
        rt = body.get("refreshToken", "")
        if rt == "mock-refresh":
            return MockResponse(200, {
                "success": True, "code": 200,
                "data": {
                    "accessToken": MOCK_TOKEN, "token": MOCK_TOKEN,
                    "refreshToken": "mock-refresh-new", "expiresIn": 86400,
                },
                "timestamp": _TS, "traceId": "refresh-ok",
            }, url=url)
        return MockResponse(401, {
            "success": False, "code": 401,
            "message": "refreshToken 无效", "data": None,
            "timestamp": _TS, "traceId": "refresh-err",
        }, url=url)

    @staticmethod
    def _parse(path):
        parts = path.strip("/").split("/")
        if len(parts) >= 3 and parts[0] == "api":
            return parts[1], parts[2]
        if len(parts) >= 2 and parts[0] == "api":
            return parts[1], parts[1]
        return "unknown", "unknown"
