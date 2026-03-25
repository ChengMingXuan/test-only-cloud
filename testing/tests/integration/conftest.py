"""
集成测试 conftest — 从父目录 tests/conftest.py 继承 api/v/auth_token 等全部 fixtures
"""
import pytest


def pytest_collection_modifyitems(config, items):
    """确保所有集成测试用例都自动带 integration 标记"""
    for item in items:
        if "integration" not in [m.name for m in item.iter_markers()]:
            item.add_marker(pytest.mark.integration)
