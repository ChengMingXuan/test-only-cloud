import uuid
from datetime import datetime
from typing import Dict, Any, Optional
import random
import string

class TestDataFactory:
    """测试数据生成工厂"""
    
    @staticmethod
    def generate_id() -> str:
        """生成 UUID"""
        return str(uuid.uuid4())
    
    @staticmethod
    def generate_email() -> str:
        """生成测试邮箱"""
        return f"test{random.randint(100000, 999999)}@example.com"
    
    @staticmethod
    def generate_phone() -> str:
        """生成测试手机号（11 位数字）"""
        return '1' + ''.join([str(random.randint(0, 9)) for _ in range(10)])
    
    @staticmethod
    def generate_password(length: int = 12) -> str:
        """生成测试密码（大小字母+数字+特殊字符）"""
        chars = string.ascii_letters + string.digits + '!@#$%^&*'
        return ''.join(random.choice(chars) for _ in range(length))
    
    @staticmethod
    def generate_strong_password() -> str:
        """生成符合密码强度要求的密码"""
        # 至少 8 位，含大写字母、小写字母、数字、特殊字符
        return "Test@Pass" + ''.join([str(random.randint(0, 9)) for _ in range(3)])
    
    @staticmethod
    def generate_tenant_data(**overrides) -> Dict[str, Any]:
        """生成租户数据"""
        data = {
            'name': f"租户_{random.randint(10000, 99999)}",
            'type': 'ENERGY_OPERATOR',
            'contact_name': 'Admin',
            'contact_email': TestDataFactory.generate_email(),
            'contact_phone': TestDataFactory.generate_phone(),
            'address': '北京市朝阳区',
            'business_scope': '充电桩运营',
            'status': 'PENDING_ACTIVATION',
            'max_users': 100,
            'max_devices': 1000,
            'storage_quota_gb': 100
        }
        data.update(overrides)
        return data
    
    @staticmethod
    def generate_user_data(**overrides) -> Dict[str, Any]:
        """生成用户数据"""
        data = {
            'username': f"testuser_{random.randint(10000, 99999)}",
            'email': TestDataFactory.generate_email(),
            'phone': TestDataFactory.generate_phone(),
            'password': TestDataFactory.generate_strong_password(),
            'full_name': '测试用户',
            'status': 'ACTIVE'
        }
        data.update(overrides)
        return data
    
    @staticmethod
    def generate_menu_data(**overrides) -> Dict[str, Any]:
        """生成菜单数据"""
        data = {
            'name': f"菜单_{random.randint(10000, 99999)}",
            'path': f"/menu-{random.randint(10000, 99999)}",
            'icon': 'SettingOutlined',
            'component': 'UserManagement',
            'sort': random.randint(100, 999),
            'visible': True,
            'parent_id': None
        }
        data.update(overrides)
        return data
    
    @staticmethod
    def generate_permission_data(**overrides) -> Dict[str, Any]:
        """生成权限数据"""
        data = {
            'code': f"custom:resource:action",
            'name': f"权限_{random.randint(10000, 99999)}",
            'description': '测试权限',
            'enabled': True
        }
        data.update(overrides)
        return data
    
    @staticmethod
    def generate_station_data(**overrides) -> Dict[str, Any]:
        """生成场站数据"""
        data = {
            'name': f"场站_{random.randint(10000, 99999)}",
            'address': '北京市朝阳区建国路',
            'longitude': 116.4074,
            'latitude': 39.9042,
            'business_hours_start': '06:00',
            'business_hours_end': '23:00',
            'total_sockets': 20,
            'available_sockets': 15,
            'contact_name': '王经理',
            'contact_phone': TestDataFactory.generate_phone(),
            'status': 'NORMAL'
        }
        data.update(overrides)
        return data
    
    @staticmethod
    def generate_device_data(**overrides) -> Dict[str, Any]:
        """生成设备数据"""
        data = {
            'name': f"充电桩_{random.randint(10000, 99999)}",
            'sn': f"CHG{datetime.now().strftime('%Y%m%d%H%M%S')}{random.randint(1000, 9999)}",
            'model': 'DC-20kW',
            'manufacturer': '制造商A',
            'protocol': 'MQTT',
            'power_rating_kw': 20,
            'gun_num': 2,
            'status': 'OFFLINE'
        }
        data.update(overrides)
        return data
    
    @staticmethod
    def generate_charging_order_data(**overrides) -> Dict[str, Any]:
        """生成充电订单数据"""
        data = {
            'order_no': f"CHG{datetime.now().strftime('%Y%m%d%H%M%S')}{random.randint(100000, 999999)}",
            'device_id': TestDataFactory.generate_id(),
            'user_id': TestDataFactory.generate_id(),
            'station_id': TestDataFactory.generate_id(),
            'start_time': datetime.now().isoformat(),
            'end_time': None,
            'charged_energy_kwh': 0,
            'total_amount_yuan': 0,
            'status': 'PENDING',
            'payment_status': 'UNPAID'
        }
        data.update(overrides)
        return data
    
    @staticmethod
    def generate_rate_data(**overrides) -> Dict[str, Any]:
        """生成费率数据"""
        data = {
            'name': f"费率方案_{random.randint(10000, 99999)}",
            'description': '分时电价费率',
            'peak_price': 1.2,  # 尖峰 1.2 元/kWh
            'high_price': 0.85,  # 高峰 0.85 元/kWh
            'normal_price': 0.55,  # 平段 0.55 元/kWh
            'valley_price': 0.25,  # 谷段 0.25 元/kWh
            'service_fee': 0.08,  # 服务费 0.08 元/kWh
            'enabled': True
        }
        data.update(overrides)
        return data
    
    @staticmethod
    def generate_workorder_data(**overrides) -> Dict[str, Any]:
        """生成工单数据"""
        data = {
            'ticket_no': f"WO{datetime.now().strftime('%Y%m%d%H%M%S')}{random.randint(100000, 999999)}",
            'title': f"故障处理_{random.randint(10000, 99999)}",
            'description': '设备离线，需要检修',
            'priority': 'HIGH',
            'category': 'DEVICE_FAULT',
            'device_id': TestDataFactory.generate_id(),
            'reporter_id': TestDataFactory.generate_id(),
            'status': 'OPEN',
            'created_time': datetime.now().isoformat()
        }
        data.update(overrides)
        return data


class AssertionHelper:
    """断言帮助类"""
    
    @staticmethod
    def assert_api_success(response_dict: Dict[str, Any], message: str = ""):
        """断言 API 返回码为成功"""
        code = response_dict.get('code')
        msg = response_dict.get('message', '')
        assert code == 200 or code == 0 or code == '0', \
            f"API 返回码不为成功。code={code}, message={msg}. {message}"
    
    @staticmethod
    def assert_api_error(response_dict: Dict[str, Any], expected_code: int = None, message: str = ""):
        """断言 API 返回错误"""
        code = response_dict.get('code')
        assert code != 200 and code != 0, f"期望错误，但 API 返回成功。{message}"
        
        if expected_code:
            assert code == expected_code, f"期望错误码 {expected_code}，但得到 {code}。{message}"
    
    @staticmethod
    def assert_field_exists(data: Dict[str, Any], field_name: str, message: str = ""):
        """断言字段存在"""
        assert field_name in data, f"字段缺失: {field_name}. {message}"
    
    @staticmethod
    def assert_fields_exist(data: Dict[str, Any], field_names: list, message: str = ""):
        """断言多个字段存在"""
        for field in field_names:
            AssertionHelper.assert_field_exists(data, field, message)
    
    @staticmethod
    def assert_tenant_isolation(records: list, tenant_id: str, tenant_id_field: str = 'tenant_id'):
        """断言多租户隔离：所有记录都属于同一租户"""
        for record in records:
            assert tenant_id_field in record, f"记录缺少 {tenant_id_field} 字段"
            assert record[tenant_id_field] == tenant_id, \
                f"数据泄露：记录属于其他租户 {record[tenant_id_field]}，期望 {tenant_id}"
    
    @staticmethod
    def assert_soft_delete_compliance(records: list, delete_at_field: str = 'delete_at'):
        """断言软删除合规：所有记录都未被删除"""
        for record in records:
            assert delete_at_field in record, f"记录缺少 {delete_at_field} 字段"
            assert record[delete_at_field] is None, \
                f"返回了已删除的记录: {record}"
    
    @staticmethod
    def assert_response_time(elapsed_ms: float, max_ms: float = 500, message: str = ""):
        """断言响应时间在限制内"""
        assert elapsed_ms <= max_ms, \
            f"响应时间过长: {elapsed_ms:.0f}ms，期望 ≤ {max_ms}ms. {message}"
    
    @staticmethod
    def assert_array_length(data: list, expected_length: int = None, 
                           min_length: int = None, max_length: int = None, message: str = ""):
        """断言数组长度"""
        if expected_length is not None:
            assert len(data) == expected_length, \
                f"数组长度不符：期望 {expected_length}，实际 {len(data)}. {message}"
        
        if min_length is not None:
            assert len(data) >= min_length, \
                f"数组长度过短：期望 ≥ {min_length}，实际 {len(data)}. {message}"
        
        if max_length is not None:
            assert len(data) <= max_length, \
                f"数组长度过长：期望 ≤ {max_length}，实际 {len(data)}. {message}"
    
    @staticmethod
    def assert_value_in_enum(value: str, enum_values: list, field_name: str = "", message: str = ""):
        """断言值在枚举范围内"""
        assert value in enum_values, \
            f"{field_name} 值不在枚举范围内: {value}。允许值: {enum_values}. {message}"
    
    @staticmethod
    def assert_string_matches_pattern(value: str, pattern: str, field_name: str = "", message: str = ""):
        """断言字符串匹配正则表达式"""
        import re
        assert re.match(pattern, value), \
            f"{field_name} 值不匹配模式 {pattern}: {value}. {message}"


# 示例用法
if __name__ == '__main__':
    # 生成测试数据
    tenant_data = TestDataFactory.generate_tenant_data(name="测试租户")
    print(f"租户数据: {tenant_data}")
    
    user_data = TestDataFactory.generate_user_data(username="testadmin")
    print(f"用户数据: {user_data}")
    
    # 断言示例
    response = {
        'code': 200,
        'message': '成功',
        'data': {
            'id': '123',
            'name': 'Test'
        }
    }
    
    AssertionHelper.assert_api_success(response)
    AssertionHelper.assert_field_exists(response['data'], 'id')
    print("✅ 所有断言通过")
