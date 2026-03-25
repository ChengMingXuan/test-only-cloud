"""
Selenium 测试数据加载 — 从共享常量和本地 fixture 读取
"""
import json
import pathlib

_FIXTURE_DIR = pathlib.Path(__file__).parent
_SHARED_DIR = _FIXTURE_DIR.parent.parent / '_shared'

SHARED = json.loads((_SHARED_DIR / 'constants.json').read_text('utf-8'))
ACCOUNTS = json.loads((_FIXTURE_DIR / 'test_accounts.json').read_text('utf-8'))
BUSINESS_DATA = json.loads((_FIXTURE_DIR / 'test_business_data.json').read_text('utf-8'))

ADMIN = SHARED['admin']
BASE_URL = SHARED['gateway']['frontendUrl']
