"""验证 Mock 服务器是否在 conftest.py 模块加载后正常运行"""
import sys
import os
import time

# 必须在任何 requests/conftest 导入前设置 no_proxy
os.environ["no_proxy"] = "127.0.0.1,localhost,::1"
os.environ["NO_PROXY"] = "127.0.0.1,localhost,::1"

import requests

# conftest 模块加载时会启动 mock server
from conftest import GATEWAY_URL, MOCK_TOKEN

def main():
    print(f"GATEWAY_URL = {GATEWAY_URL}", flush=True)
    print(f"MOCK_TOKEN  = {MOCK_TOKEN[:30]}...", flush=True)

    # 测试1: 健康检查
    try:
        r = requests.get(f"{GATEWAY_URL}/health", timeout=5)
        print(f"[健康检查] status={r.status_code} body={r.text[:80]}", flush=True)
    except Exception as e:
        print(f"[健康检查] FAILED: {e}", flush=True)

    # 测试2: 无 Token → 401
    try:
        r = requests.get(f"{GATEWAY_URL}/api/identity/users", timeout=5)
        print(f"[无Token] status={r.status_code} (期望 401)", flush=True)
    except Exception as e:
        print(f"[无Token] FAILED: {e}", flush=True)

    # 测试3: 有效 Token → 200
    try:
        r = requests.get(
            f"{GATEWAY_URL}/api/identity/users",
            headers={"Authorization": f"Bearer {MOCK_TOKEN}"},
            timeout=5,
        )
        print(f"[有效Token] status={r.status_code} (期望 200)", flush=True)
    except Exception as e:
        print(f"[有效Token] FAILED: {e}", flush=True)

    # 测试4: 登录
    try:
        r = requests.post(
            f"{GATEWAY_URL}/api/auth/login",
            json={"username": "admin", "password": "P@ssw0rd"},
            timeout=5,
        )
        print(f"[登录] status={r.status_code} (期望 200) body={r.text[:80]}", flush=True)
    except Exception as e:
        print(f"[登录] FAILED: {e}", flush=True)

    # 测试5: 内部接口 → 403
    try:
        r = requests.get(
            f"{GATEWAY_URL}/api/internal/health",
            headers={"Authorization": f"Bearer {MOCK_TOKEN}"},
            timeout=5,
        )
        print(f"[内部接口] status={r.status_code} (期望 403)", flush=True)
    except Exception as e:
        print(f"[内部接口] FAILED: {e}", flush=True)

    print("验证完成", flush=True)


if __name__ == "__main__":
    main()
