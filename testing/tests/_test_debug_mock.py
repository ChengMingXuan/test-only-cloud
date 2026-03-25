"""调试 Mock 服务器：为什么不响应？"""
import sys
import time
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
import requests


class H(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):
        # 不再静音——打印请求日志
        print(f"[SERVER] {self.address_string()} - {fmt % args}", flush=True)

    def do_GET(self):
        print(f"[SERVER] do_GET called: {self.path}", flush=True)
        body = b'{"ok":true}'
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)
        self.wfile.flush()
        print(f"[SERVER] response sent", flush=True)


PORT = 29997
print(f"Starting server on port {PORT}...", flush=True)
srv = HTTPServer(("127.0.0.1", PORT), H)
print(f"Server socket info: {srv.socket.getsockname()}", flush=True)
t = threading.Thread(target=srv.serve_forever, daemon=True, name="MockServer")
t.start()
time.sleep(0.5)
print(f"Server thread started: {t.is_alive()}", flush=True)

try:
    print(f"Sending request to http://127.0.0.1:{PORT}/health ...", flush=True)
    r = requests.get(f"http://127.0.0.1:{PORT}/health", timeout=5)
    print(f"OK: status={r.status_code} body={r.text}", flush=True)
except Exception as e:
    print(f"FAIL: {type(e).__name__}: {e}", flush=True)

srv.shutdown()
print("Done", flush=True)
