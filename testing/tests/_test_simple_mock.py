"""简单测试：独立 Mock 服务器，不依赖 conftest"""
import sys
import time
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
import requests


class H(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):
        pass

    def do_GET(self):
        body = b'{"ok":true}'
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)
        self.wfile.flush()


PORT = 29998
srv = HTTPServer(("127.0.0.1", PORT), H)
t = threading.Thread(target=srv.serve_forever, daemon=True)
t.start()
time.sleep(0.3)

print(f"Mock server started on port {PORT}", flush=True)

try:
    r = requests.get(f"http://127.0.0.1:{PORT}/health", timeout=5)
    print(f"OK: status={r.status_code} body={r.text}", flush=True)
except Exception as e:
    print(f"FAIL: {type(e).__name__}: {e}", flush=True)

srv.shutdown()
print("Done", flush=True)
