"""
test_compat 目录专用 conftest —— Selenium Grid 可用性检查
Grid 不可达时自动跳过本目录全部用例，避免 CI 中 ConnectionRefusedError。
"""
import socket
import pytest


def _is_grid_available(host: str = "localhost", port: int = 4444, timeout: float = 2) -> bool:
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(timeout)
            s.connect((host, port))
            return True
    except (ConnectionRefusedError, OSError, socket.timeout):
        return False


_grid_ok = _is_grid_available()


def pytest_collection_modifyitems(config, items):
    """Grid 不可达时，给本目录下所有用例打 skip 标记。"""
    if _grid_ok:
        return
    skip_marker = pytest.mark.skip(reason="Selenium Grid (localhost:4444) 不可达，跳过兼容性测试")
    for item in items:
        item.add_marker(skip_marker)
