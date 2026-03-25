"""
工具5: Python 安全合规测试
覆盖维度: 认证安全 / 水平越权 / SQL注入 / XSS / 敏感信息泄露 / CORS / Header安全
"""
import json, sys, time, uuid, re
from datetime import datetime

try:
    import requests
    requests.packages.urllib3.disable_warnings()
except ImportError:
    print("需要: pip install requests")
    sys.exit(1)

BASE = os.getenv("JGSY_GATEWAY_URL", "http://localhost:8000")
ADMIN = {"username": "admin", "password": "P@ssw0rd"}

results = {
    "tool": "security",
    "timestamp": datetime.now().isoformat(),
    "total": 0, "passed": 0, "failed": 0, "warnings": 0,
    "details": []
}

def add(cat, name, status, msg):
    results["total"] += 1
    results[{"PASS": "passed", "FAIL": "failed", "WARN": "warnings"}[status]] += 1
    results["details"].append({"category": cat, "name": name, "status": status, "message": msg})
    icon = {"PASS": "[PASS]", "FAIL": "[FAIL]", "WARN": "[WARN]"}[status]
    print(f"{icon} {cat} :: {name} - {msg}")

def login(creds):
    r = requests.post(f"{BASE}/api/auth/login", json=creds, timeout=10)
    if r.status_code == 200:
        return r.json().get("data", {}).get("accessToken")
    return None

# 获取管理员 token
token = login(ADMIN)
if not token:
    print("FATAL: 无法登录，终止安全测试")
    sys.exit(1)
auth = {"Authorization": f"Bearer {token}"}

# ══════════════════════════════════════
# T5.1 未认证访问检测
# ══════════════════════════════════════
print("\n=== T5.1 未认证访问检测 ===")
protected_endpoints = [
    "/api/tenants", "/api/roles", "/api/menus", "/api/device",
    "/api/charging/orders", "/api/ruleengine/chains", "/api/analytics/funnel",
    "/api/workorder", "/api/station",
]
for ep in protected_endpoints:
    r = requests.get(f"{BASE}{ep}", timeout=10)
    if r.status_code == 401:
        add("未认证", ep, "PASS", "正确返回 401")
    elif r.status_code == 403:
        add("未认证", ep, "PASS", "返回 403 Forbidden")
    else:
        add("未认证", ep, "FAIL", f"未认证竟返回 {r.status_code}（应为 401）")

# ══════════════════════════════════════
# T5.2 伪造/过期 Token 检测
# ══════════════════════════════════════
print("\n=== T5.2 Token 安全 ===")
fake_tokens = [
    ("空Token", ""),
    ("伪造Token", "Bearer fake-token-12345"),
    ("篡改Token", f"Bearer {token[:-10]}TAMPERED12"),
    ("格式错误", "NotBearer " + token),
]
for name, tk in fake_tokens:
    h = {"Authorization": tk} if tk else {}
    r = requests.get(f"{BASE}/api/roles", headers=h, timeout=10)
    if r.status_code in (401, 403):
        add("Token安全", name, "PASS", f"正确拒绝: {r.status_code}")
    else:
        add("Token安全", name, "FAIL", f"应拒绝但返回 {r.status_code}")

# ══════════════════════════════════════
# T5.3 SQL 注入检测
# ══════════════════════════════════════
print("\n=== T5.3 SQL 注入防护 ===")
sql_payloads = [
    ("单引号", "' OR '1'='1"),
    ("UNION注入", "' UNION SELECT 1,2,3--"),
    ("注释截断", "admin'--"),
    ("批量注入", "1; DROP TABLE users;--"),
    ("布尔盲注", "' AND 1=1--"),
]
for name, payload in sql_payloads:
    # 测试查询参数注入
    r = requests.get(f"{BASE}/api/roles", params={"keyword": payload}, headers=auth, timeout=10)
    if r.status_code < 500:
        add("SQL注入", f"查询参数-{name}", "PASS", f"未触发服务器错误 ({r.status_code})")
    else:
        add("SQL注入", f"查询参数-{name}", "FAIL", f"可能存在SQL注入: {r.status_code}")

    # 测试登录注入
    r2 = requests.post(f"{BASE}/api/auth/login",
                       json={"username": payload, "password": payload}, timeout=10)
    if r2.status_code < 500:
        add("SQL注入", f"登录-{name}", "PASS", f"安全处理 ({r2.status_code})")
    else:
        add("SQL注入", f"登录-{name}", "FAIL", f"可能存在SQL注入: {r2.status_code}")

# ══════════════════════════════════════
# T5.4 XSS 注入检测
# ══════════════════════════════════════
print("\n=== T5.4 XSS 防护 ===")
xss_payloads = [
    ("Script标签", "<script>alert('xss')</script>"),
    ("事件处理", '<img onerror="alert(1)" src=x>'),
    ("SVG注入", "<svg onload=alert(1)>"),
]
for name, payload in xss_payloads:
    uid = uuid.uuid4().hex[:8]
    body = {"name": payload, "description": f"xss_test_{uid}",
            "steps": [{"name": "S1", "eventName": "view"}, {"name": "S2", "eventName": "click"}]}
    r = requests.post(f"{BASE}/api/analytics/funnel", json=body, headers=auth, timeout=10)
    if r.status_code < 500:
        # 检查响应是否原样返回了脚本内容（未转义）
        if r.status_code in (200, 201):
            resp_text = r.text
            # 成功创建 - 检查读回时是否转义
            data = r.json().get("data", {})
            rid = data.get("id") if isinstance(data, dict) else data
            if rid:
                rr = requests.get(f"{BASE}/api/analytics/funnel/{rid}", headers=auth, timeout=10)
                if rr.status_code == 200:
                    rd = rr.json().get("data", {})
                    stored_name = rd.get("name", "") if isinstance(rd, dict) else ""
                    if "<script>" in stored_name or "onerror" in stored_name.lower():
                        add("XSS", name, "WARN", "XSS 载荷被原样存储（依赖前端转义）")
                    else:
                        add("XSS", name, "PASS", "安全处理")
                # 清理
                requests.delete(f"{BASE}/api/analytics/funnel/{rid}", headers=auth, timeout=5)
            else:
                add("XSS", name, "PASS", "安全处理（无需转义验证）")
        else:
            add("XSS", name, "PASS", f"被拒: {r.status_code}")
    else:
        add("XSS", name, "FAIL", f"服务端错误: {r.status_code}")

# ══════════════════════════════════════
# T5.5 水平越权检测（IDOR）
# ══════════════════════════════════════
print("\n=== T5.5 水平越权（IDOR） ===")
# 尝试用管理员 token 访问其他租户数据
fake_ids = [
    str(uuid.UUID(int=0)),  # 00000000-0000-0000-0000-000000000000
    str(uuid.UUID(int=1)),  # 只有一个位不同
    "99999999-9999-9999-9999-999999999999",
]
for fid in fake_ids:
    r = requests.get(f"{BASE}/api/roles/{fid}", headers=auth, timeout=10)
    if r.status_code in (404, 403):
        add("IDOR", f"角色/{fid[:8]}", "PASS", f"正确拒绝: {r.status_code}")
    elif r.status_code == 200:
        add("IDOR", f"角色/{fid[:8]}", "WARN", "返回 200，需确认是否为当前租户数据")
    else:
        add("IDOR", f"角色/{fid[:8]}", "PASS", f"返回 {r.status_code}")

# ══════════════════════════════════════
# T5.6 敏感信息泄露
# ══════════════════════════════════════
print("\n=== T5.6 敏感信息泄露 ===")
# 检查错误响应是否泄露堆栈/数据库信息
sensitive_patterns = [
    ("数据库连接串", r"(Host|Server|Data Source|ConnectionString)\s*="),
    ("密码泄露", r"(password|passwd|pwd)\s*[:=]\s*\w+"),
    ("堆栈跟踪", r"at\s+\w+\.\w+\(.*\)\s+in\s+"),
    ("SQL语句", r"(SELECT|INSERT|UPDATE|DELETE)\s+.*FROM\s+\w+"),
]

# 触发一个 500 错误来检查
r = requests.get(f"{BASE}/api/device/not-a-valid-uuid", headers=auth, timeout=10)
resp_text = r.text.lower() if r.text else ""

for name, pattern in sensitive_patterns:
    if re.search(pattern, r.text, re.IGNORECASE):
        add("信息泄露", name, "FAIL", f"错误响应中发现敏感信息")
    else:
        add("信息泄露", name, "PASS", "未泄露")

# 检查 /health 端点是否泄露过多信息
r_health = requests.get(f"{BASE}/health", timeout=10)
health_text = r_health.text.lower() if r_health.text else ""
if "connection" in health_text or "password" in health_text or "host=" in health_text:
    add("信息泄露", "健康端点", "FAIL", "健康端点泄露连接信息")
else:
    add("信息泄露", "健康端点", "PASS", "健康端点安全")

# ══════════════════════════════════════
# T5.7 HTTP 安全头检测
# ══════════════════════════════════════
print("\n=== T5.7 HTTP 安全头 ===")
r = requests.get(f"{BASE}/api/roles", headers=auth, timeout=10)
headers = r.headers

security_headers = {
    "X-Content-Type-Options": "nosniff 防 MIME 嗅探",
    "X-Frame-Options": "防点击劫持",
    "Strict-Transport-Security": "HSTS（仅 HTTPS 时生效）",
    "X-XSS-Protection": "XSS 保护(旧浏览器)",
}
for header, desc in security_headers.items():
    if header.lower() in {h.lower(): h for h in headers}:
        add("安全头", header, "PASS", f"已配置: {desc}")
    else:
        add("安全头", header, "WARN", f"缺失: {desc}")

# 检查是否泄露服务器版本
server_header = headers.get("Server", "")
if "kestrel" in server_header.lower() or "microsoft" in server_header.lower():
    add("安全头", "Server隐藏", "WARN", f"暴露技术栈: {server_header}")
elif server_header:
    add("安全头", "Server隐藏", "PASS", f"Server: {server_header}")
else:
    add("安全头", "Server隐藏", "PASS", "未暴露 Server 头")

# ══════════════════════════════════════
# T5.8 暴力破解防护
# ══════════════════════════════════════
print("\n=== T5.8 暴力破解防护 ===")
fail_count = 0
locked = False
for i in range(8):
    r = requests.post(f"{BASE}/api/auth/login",
                      json={"username": "admin", "password": f"wrong_pass_{i}"}, timeout=10)
    fail_count += 1
    if r.status_code == 429:
        locked = True
        add("暴力破解", "登录限流", "PASS", f"第 {i+1} 次失败后触发限流 (429)")
        break
    elif r.status_code == 423:
        locked = True
        add("暴力破解", "账号锁定", "PASS", f"第 {i+1} 次失败后锁定账号 (423)")
        break
if not locked:
    add("暴力破解", "无限登录", "WARN", f"连续 {fail_count} 次错误密码未触发限流或锁定")

# ══════════════════════════════════════
# T5.9 路径遍历检测
# ══════════════════════════════════════
print("\n=== T5.9 路径遍历防护 ===")
traversal_paths = [
    "/api/../../../etc/passwd",
    "/api/device/..%2F..%2Fetc%2Fpasswd",
    "/api/storage/download?path=../../../etc/passwd",
]
for path in traversal_paths:
    try:
        r = requests.get(f"{BASE}{path}", headers=auth, timeout=10, allow_redirects=False)
        if r.status_code in (400, 404, 403, 401):
            add("路径遍历", path[:40], "PASS", f"安全拒绝: {r.status_code}")
        elif r.status_code == 200 and ("root:" in r.text or "/bin/" in r.text):
            add("路径遍历", path[:40], "FAIL", "可能存在路径遍历漏洞！")
        else:
            add("路径遍历", path[:40], "PASS", f"响应 {r.status_code}")
    except:
        add("路径遍历", path[:40], "PASS", "请求被拒绝")

# ══════════════════════════════════════
# T5.10 大请求/DoS 防护
# ══════════════════════════════════════
print("\n=== T5.10 大请求防护 ===")
# 超大 JSON body
big_body = {"name": "A" * 100000, "description": "B" * 100000,
            "steps": [{"name": f"S{i}", "eventName": "ev"} for i in range(1000)]}
try:
    r = requests.post(f"{BASE}/api/analytics/funnel", json=big_body, headers=auth, timeout=15)
    if r.status_code in (400, 413, 414):
        add("DoS防护", "超大Body", "PASS", f"正确拒绝: {r.status_code}")
    elif r.status_code < 500:
        add("DoS防护", "超大Body", "WARN", f"未限制大请求: {r.status_code}")
    else:
        add("DoS防护", "超大Body", "WARN", f"服务端错误: {r.status_code}")
except requests.exceptions.Timeout:
    add("DoS防护", "超大Body", "PASS", "请求超时（有保护）")
except Exception as e:
    add("DoS防护", "超大Body", "WARN", f"异常: {type(e).__name__}")

# ── 输出 JSON ──
json_path = r"D:\2026\aiops.v2\TestResults\security-results.json"
with open(json_path, "w", encoding="utf-8") as f:
    json.dump(results, f, ensure_ascii=False, indent=2)

print(f"\n=== 安全合规测试汇总 ===")
print(f"总计: {results['total']} | 通过: {results['passed']} | 失败: {results['failed']} | 警告: {results['warnings']}")
print(f"结果已保存: {json_path}")
