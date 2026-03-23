"""
tests/api 本地 Fixture 配置
===========================
为 api/ 子目录提供专用的 fixture 和辅助工具
"""
import pytest
import uuid
import logging

logger = logging.getLogger(__name__)

# ═══════════════════════════════════════════
# 常量
# ═══════════════════════════════════════════
CHARGING_PREFIX = "/api/charging"
IDENTITY_PREFIX = "/api/identity"
PERMISSION_PREFIX = "/api/permission"
DEVICE_PREFIX = "/api/device"
STATION_PREFIX = "/api/station"
ACCOUNT_PREFIX = "/api/account"
TENANT_PREFIX = "/api/tenant"
WORKORDER_PREFIX = "/api/workorder"
SETTLEMENT_PREFIX = "/api/settlement"

# 能源服务前缀
ENERGY_PREFIXES = {
    "carbontrade": "/api/carbontrade",
    "vpp": "/api/vpp",
    "electrade": "/api/electrade",
    "microgrid": "/api/microgrid",
    "pvessc": "/api/pvessc",
    "orchestrator": "/api/orchestrator",
    "demandresp": "/api/demandresp",
    "deviceops": "/api/deviceops",
    "energyeff": "/api/energyeff",
    "multienergy": "/api/multienergy",
    "safecontrol": "/api/safecontrol",
}


def _gen_uuid():
    return str(uuid.uuid4())


# ═══════════════════════════════════════════
# Fixture
# ═══════════════════════════════════════════

@pytest.fixture
def random_id():
    """生成随机UUID"""
    return _gen_uuid()


@pytest.fixture
def charging_order_payload():
    """充电订单创建载荷"""
    return {
        "stationId": _gen_uuid(),
        "pileId": _gen_uuid(),
        "connectorId": 1,
        "userId": _gen_uuid(),
        "startSoc": 20.0,
        "chargingMode": "fast",
    }


@pytest.fixture
def user_payload():
    """用户创建载荷"""
    return {
        "username": f"test_{uuid.uuid4().hex[:8]}",
        "password": "Test@123456",
        "realName": "测试用户",
        "phone": f"138{uuid.uuid4().int % 100000000:08d}",
        "email": f"test_{uuid.uuid4().hex[:6]}@test.com",
    }


@pytest.fixture
def role_payload():
    """角色创建载荷"""
    return {
        "roleName": f"test_role_{uuid.uuid4().hex[:6]}",
        "roleCode": f"TEST_{uuid.uuid4().hex[:6].upper()}",
        "description": "自动化测试角色",
        "status": 1,
    }


@pytest.fixture
def device_payload():
    """设备创建载荷"""
    return {
        "deviceCode": f"DEV_{uuid.uuid4().hex[:8]}",
        "deviceName": f"测试设备_{uuid.uuid4().hex[:4]}",
        "deviceType": "charging_pile",
        "stationId": _gen_uuid(),
        "status": "online",
    }


@pytest.fixture
def station_payload():
    """场站创建载荷"""
    return {
        "stationName": f"测试场站_{uuid.uuid4().hex[:4]}",
        "stationCode": f"ST_{uuid.uuid4().hex[:6]}",
        "address": "北京市朝阳区测试路1号",
        "longitude": 116.404,
        "latitude": 39.915,
        "status": "operating",
    }


@pytest.fixture
def workorder_payload():
    """工单创建载荷"""
    return {
        "title": f"测试工单_{uuid.uuid4().hex[:4]}",
        "description": "自动化测试工单描述",
        "orderType": "repair",
        "priority": "high",
        "deviceId": _gen_uuid(),
    }


@pytest.fixture
def energy_config_payload():
    """能源配置载荷"""
    return {
        "configName": f"energy_cfg_{uuid.uuid4().hex[:6]}",
        "configType": "dispatch",
        "parameters": {"mode": "auto", "threshold": 0.8},
    }
