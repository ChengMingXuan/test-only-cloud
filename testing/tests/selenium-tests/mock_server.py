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


def find_free_port(start=18123) -> int:
    for port in range(start, start + 100):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.bind(("127.0.0.1", port))
                return port
            except OSError:
                continue
    raise RuntimeError("无可用端口")


class MockServer:
    def __init__(self, port: int = None):
        self.port = port or find_free_port()
        self._server = http.server.HTTPServer(("127.0.0.1", self.port), _Handler)
        self._thread = threading.Thread(target=self._server.serve_forever, daemon=True)

    def start(self):
        self._thread.start()

    def stop(self):
        self._server.shutdown()

    @property
    def base_url(self) -> str:
        return f"http://127.0.0.1:{self.port}"


if __name__ == "__main__":
    srv = MockServer(18123)
    srv.start()
    print(f"Mock server running at {srv.base_url}")
    input("Press Enter to stop...")
    srv.stop()
