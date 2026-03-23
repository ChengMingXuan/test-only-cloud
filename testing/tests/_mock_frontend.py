"""最简 Mock 前端 HTTP 服务器 — 供 Cypress/Puppeteer/Selenium/Playwright 测试用"""
import socket
from http.server import HTTPServer, BaseHTTPRequestHandler
from socketserver import ThreadingMixIn

HTML = b"""<!DOCTYPE html><html><head><title>JGSY</title></head><body>
<div id="root"><div class="ant-layout"><div class="ant-layout-sider"><div class="ant-menu"><div class="ant-menu-item">Dashboard</div><div class="ant-menu-item">Monitor</div></div></div><div class="ant-layout-content"><div class="ant-pro-table"><table class="ant-table"><thead><tr><th>ID</th><th>Name</th><th>Action</th><th>Time</th></tr></thead><tbody><tr class="ant-table-row" data-row-key="1"><td>001</td><td>Admin</td><td>Create</td><td>2026-01-01</td></tr></tbody></table></div></div></div></div>
</body></html>"""

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(HTML)))
        self.send_header("Connection", "close")
        self.end_headers()
        self.wfile.write(HTML)
    do_POST = do_PUT = do_DELETE = do_PATCH = do_OPTIONS = do_GET
    def do_HEAD(self):
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(HTML)))
        self.send_header("Connection", "close")
        self.end_headers()
    def log_message(self, fmt, *args):
        pass

if __name__ == "__main__":
    import sys
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8000
    class ThreadingServer(ThreadingMixIn, HTTPServer):
        daemon_threads = True
    srv = ThreadingServer(("0.0.0.0", port), Handler)
    srv.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    print(f"Mock frontend on 0.0.0.0:{port} (threaded)", flush=True)
    srv.serve_forever()
