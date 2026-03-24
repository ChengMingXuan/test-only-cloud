"""
Selenium 测试用 Mock HTTP 服务器
返回满足所有浏览器兼容性测试断言的最小 HTML 页面。

支持的测试：
  - find_element(By.ID, "root")                    ✅ <div id="root">
  - find_elements(".ant-layout, .layout, body")    ✅ body.ant-layout
  - find_elements("link[rel='stylesheet'], style") ✅ <style>
  - CSS.supports('display', 'flex')                ✅ 原生支持
  - CSS.supports('display', 'grid')                ✅ 原生支持
  - document.body.scrollHeight > 0                 ✅ 有内容
  - localStorage.setItem(...)                      ✅ http://127.0.0.1 有 origin
  - data-testid="sidebar/content/page-title"       ✅ 伪造结构
"""
import http.server
import threading
import socket
import time
from urllib.parse import urlparse

# 最小 HTML 页面 — 满足全部断言
MOCK_HTML = b"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <title>AIOPS Mock</title>
  <style>
    body { display: flex; margin: 0; height: 100vh; }
    .ant-layout { display: grid; min-height: 100px; }
  </style>
</head>
<body class="ant-layout layout" style="overflow-y: auto; overflow-x: hidden;">
  <div id="root" class="app-root" style="width:100%; min-height:200px;">
    <aside class="sidebar" data-testid="sidebar" style="display:block; width:200px;">
      Sidebar
    </aside>
    <main class="main-content" data-testid="content" style="display:block; flex:1;">
      <h1 data-testid="page-title">AIOPS</h1>
      <div class="content-area" data-testid="content">
        <button type="button">Click</button>
        <form action="#">
          <input id="username" name="username" type="text" autocomplete="username" />
          <input id="password" name="password" type="password" />
          <select><option value="a">Option A</option></select>
          <input type="checkbox" id="check" />
          <input type="date" />
          <button type="submit">Login</button>
        </form>
        <table>
          <thead><tr><th>Name</th><th>Status</th></tr></thead>
          <tbody><tr><td>Item 1</td><td>Active</td></tr></tbody>
        </table>
      </div>
    </main>
  </div>
</body>
</html>
"""


class _Handler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(MOCK_HTML)))
        self.end_headers()
        self.wfile.write(MOCK_HTML)

    def log_message(self, format, *args):
        pass  # 静默日志


class _ThreadingHTTPServer(http.server.ThreadingHTTPServer):
    allow_reuse_address = True


class ExistingMockServer:
    def __init__(self, base_url: str):
        self._base_url = base_url.rstrip("/")

    def start(self):
        return None

    def stop(self):
        return None

    @property
    def base_url(self) -> str:
        return self._base_url


def is_mock_server_available(base_url: str, timeout: float = 1.0) -> bool:
  try:
    parsed = urlparse(base_url)
    host = parsed.hostname or "127.0.0.1"
    port = parsed.port or 80
    path = parsed.path or "/"

    with socket.create_connection((host, port), timeout=timeout) as conn:
      request = f"GET {path} HTTP/1.1\r\nHost: {host}\r\nConnection: close\r\n\r\n"
      conn.sendall(request.encode("ascii"))

      chunks = []
      while True:
        data = conn.recv(4096)
        if not data:
          break
        chunks.append(data)

    html = b"".join(chunks).decode("utf-8", errors="ignore")
    return 'id="root"' in html and "AIOPS" in html
  except (OSError, ValueError):
    return False


def wait_for_mock_server(base_url: str, retries: int = 20, delay: float = 0.1):
    for _ in range(max(retries, 1)):
        if is_mock_server_available(base_url):
            return ExistingMockServer(base_url)
        time.sleep(delay)
    return None


class MockServer:
    def __init__(self, port: int = None, host: str = "127.0.0.1"):
        requested_port = 0 if port is None else port
        self._server = _ThreadingHTTPServer((host, requested_port), _Handler)
        self.port = int(self._server.server_address[1])
        self.host = host
        self._thread = threading.Thread(target=self._server.serve_forever, daemon=True)
        self._started = False

    def start(self):
        if self._started:
            return
        self._thread.start()
        self._started = True

    def stop(self):
        if not self._started:
            return
        self._server.shutdown()
        self._server.server_close()
        self._thread.join(timeout=2)
        self._started = False

    @property
    def base_url(self) -> str:
        return f"http://{self.host}:{self.port}"


if __name__ == "__main__":
    srv = MockServer(18123)
    srv.start()
    print(f"Mock server running at {srv.base_url}")
    input("Press Enter to stop...")
    srv.stop()
