"""
pytest 测试数据 fixtures — 从共享常量加载 + 提供数据工厂
"""
import json
import pathlib

# 加载共享常量
_SHARED_DIR = pathlib.Path(__file__).parent.parent.parent / '_shared'
SHARED = json.loads((_SHARED_DIR / 'constants.json').read_text('utf-8'))
MOCK_RESPONSES = json.loads((_SHARED_DIR / 'mock-responses.json').read_text('utf-8'))

ADMIN = SHARED['admin']
TEST_USER = SHARED['testUser']
TEST_TENANT = SHARED['testTenant']
TEST_DEVICES = SHARED['testDevices']
TEST_STATIONS = SHARED['testStations']
