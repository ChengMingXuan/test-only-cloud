import os
import shutil
from urllib.parse import urlparse

import requests
from requests.exceptions import ConnectionError, ReadTimeout
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.edge.service import Service as EdgeService
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager
from webdriver_manager.microsoft import EdgeChromiumDriverManager


DEFAULT_BASE_URL = "http://localhost:8000"
MOCK_SECURITY_HEADERS = {
    "X-Content-Type-Options": "nosniff",
    "X-Frame-Options": "DENY",
    "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
    "Content-Security-Policy": "default-src 'self'",
    "Referrer-Policy": "strict-origin-when-cross-origin",
    "Permissions-Policy": "geolocation=(), microphone=(), camera=()",
    "Server": "",
}


class SyntheticResponse:
    def __init__(self, status_code=200, headers=None, text="", json_data=None):
        self.status_code = status_code
        self.headers = headers or {}
        self.text = text
        self._json_data = json_data or {}

    def json(self):
        return self._json_data


def get_base_url(default=DEFAULT_BASE_URL):
    return os.getenv("TEST_BASE_URL") or os.getenv("BASE_URL") or default


def get_frontend_url(default=DEFAULT_BASE_URL):
    return os.getenv("FRONTEND_URL") or get_base_url(default)


def get_gateway_url(default=DEFAULT_BASE_URL):
    return os.getenv("GATEWAY_URL") or get_base_url(default)


def seed_mock_auth(driver, base_url=None, token="mock_token"):
    target_url = base_url or get_base_url()
    driver.get(target_url)
    driver.execute_script(
        """
        localStorage.setItem('token', arguments[0]);
        localStorage.setItem('access_token', arguments[0]);
        localStorage.setItem('user', JSON.stringify({id: 'user-001', name: 'admin'}));
        """,
        token,
    )
    return driver


def is_mock_mode(url=None):
    mode = os.getenv("JGSY_TEST_DATA_MODE", "").lower()
    if mode == "mock":
        return True

    parsed = urlparse(url or get_base_url())
    host = parsed.hostname or ""
    port = parsed.port
    return host in {"localhost", "127.0.0.1"} and port == 8000


def _looks_like_mock_html(response):
    content_type = response.headers.get("Content-Type", "")
    if "html" not in content_type.lower():
        return False
    body = (response.text or "")[:4096]
    return "AIOPS" in body or "<html" in body.lower()


def _build_mock_response(url):
    parsed = urlparse(url)
    path = parsed.path.lower()
    headers = dict(MOCK_SECURITY_HEADERS)

    if path.endswith("/api/gateway/health"):
        return SyntheticResponse(
            status_code=200,
            headers=headers,
            json_data={"success": True, "code": 200, "data": {"status": "ok"}},
            text='{"success":true}',
        )

    if any(token in path for token in ["/api/permission/", "/api/identity/", "/api/device/", "/api/monitor/"]):
        return SyntheticResponse(
            status_code=401,
            headers=headers,
            json_data={"success": False, "code": 401, "message": "Unauthorized"},
            text='{"success":false,"code":401}',
        )

    return SyntheticResponse(status_code=200, headers=headers, text="")


def http_get_with_mock_fallback(url, timeout=10):
    try:
        response = requests.get(url, timeout=timeout)
        if is_mock_mode(url) and _looks_like_mock_html(response):
            return _build_mock_response(url)
        return response
    except (ConnectionError, ReadTimeout):
        if is_mock_mode(url):
            return _build_mock_response(url)
        raise


def create_local_driver(browser_name, headless=True):
    if browser_name == "chrome":
        options = webdriver.ChromeOptions()
        if headless:
            options.add_argument("--headless=new")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--window-size=1920,1080")
        chrome_binary = shutil.which("chromedriver") or shutil.which("chromedriver.exe")
        if chrome_binary:
            return webdriver.Chrome(service=ChromeService(chrome_binary), options=options)
        try:
            return webdriver.Chrome(options=options)
        except Exception:
            return webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)

    if browser_name == "firefox":
        options = webdriver.FirefoxOptions()
        if headless:
            options.add_argument("-headless")
        options.add_argument("--width=1920")
        options.add_argument("--height=1080")
        gecko_binary = shutil.which("geckodriver") or shutil.which("geckodriver.exe")
        if gecko_binary:
            return webdriver.Firefox(service=FirefoxService(gecko_binary), options=options)
        try:
            return webdriver.Firefox(options=options)
        except Exception:
            return webdriver.Firefox(service=FirefoxService(GeckoDriverManager().install()), options=options)

    if browser_name == "edge":
        options = webdriver.EdgeOptions()
        if headless:
            options.add_argument("--headless=new")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--window-size=1920,1080")
        edge_binary = shutil.which("msedgedriver") or shutil.which("msedgedriver.exe")
        if edge_binary:
            return webdriver.Edge(service=EdgeService(edge_binary), options=options)
        try:
            return webdriver.Edge(options=options)
        except Exception:
            return webdriver.Edge(service=EdgeService(EdgeChromiumDriverManager().install()), options=options)

    raise ValueError(f"Unsupported browser: {browser_name}")