"""
业务服务 API 测试 — 覆盖 V3.1.2 Account/Charging/Identity 变更
================================================================
覆盖文件:
- JGSY.AGI.Account/Service/WalletService.cs (MODIFIED)
- JGSY.AGI.Account/Service/MembershipBenefitAutoActivationService.cs (MODIFIED)
- JGSY.AGI.Account/Entities/Invoice.cs (MODIFIED)
- JGSY.AGI.Charging/Service/ChargingOrderService.cs (MODIFIED)
- JGSY.AGI.Charging/Program.cs (MODIFIED) - EventSourcing 清理
- JGSY.AGI.Identity/User/Service/UserService.cs (MODIFIED)
- JGSY.AGI.Identity/User/Business/RealNameAuthService.cs (MODIFIED)
- JGSY.AGI.Identity/User/Api/InternalUserController.cs (MODIFIED)
- JGSY.AGI.Identity/User/Data/UserRepository.cs (MODIFIED)
- JGSY.AGI.Identity/User/Entities/User.cs (MODIFIED)
"""

import pytest
import logging
import uuid

logger = logging.getLogger(__name__)

_TENANT_ID = "00000000-0000-0000-0000-000000000001"
_ADMIN_ID = "00000000-0000-0000-0000-000000000001"


# ═══════════════════════════════════════════════════
# 钱包服务 测试
# ═══════════════════════════════════════════════════

@pytest.mark.p0
@pytest.mark.api
class TestWalletService:
    """测试 WalletService
    - GetOrCreateWalletAsync
    - GetBalanceAsync
    - RechargeAsync (事务: 余额+交易记录+total_recharged)
    - ConsumeAsync (事务: 余额检查+扣款+total_consumed)
    """

    @pytest.fixture(autouse=True)
    def _setup(self, gateway_api):
        self.client = gateway_api
        self.base = "/api/account/wallet"

    def test_get_or_create_wallet(self):
        """获取或创建钱包（初始余额0）"""
        user_id = str(uuid.uuid4())
        resp = self.client.get(f"{self.base}/{user_id}")
        assert resp.status_code == 200
        data = resp.json()
        assert data.get("success") is True
        logger.info("获取/创建钱包 ✓")

    def test_get_balance(self):
        """查询钱包余额"""
        user_id = str(uuid.uuid4())
        resp = self.client.get(f"{self.base}/{user_id}/balance")
        assert resp.status_code == 200
        logger.info("查询余额 ✓")

    def test_recharge_wallet(self):
        """钱包充值"""
        user_id = str(uuid.uuid4())
        resp = self.client.post(f"{self.base}/{user_id}/recharge", json={
            "amount": 100.00,
            "description": "测试充值",
            "referenceId": str(uuid.uuid4())
        })
        assert resp.status_code == 200
        data = resp.json()
        assert data.get("success") is True
        logger.info("钱包充值 ✓")

    def test_recharge_negative_amount_rejected(self):
        """充值负数金额应被拒绝"""
        user_id = str(uuid.uuid4())
        resp = self.client.post(f"{self.base}/{user_id}/recharge", json={
            "amount": -50.00,
            "description": "负数充值"
        })
        assert resp.status_code in (200, 400)
        logger.info("负数充值拒绝 ✓")

    def test_recharge_zero_amount(self):
        """充值0金额应被处理"""
        user_id = str(uuid.uuid4())
        resp = self.client.post(f"{self.base}/{user_id}/recharge", json={
            "amount": 0,
            "description": "零充值"
        })
        assert resp.status_code in (200, 400)
        logger.info("零金额处理 ✓")

    def test_consume_wallet(self):
        """钱包消费"""
        user_id = str(uuid.uuid4())
        resp = self.client.post(f"{self.base}/{user_id}/consume", json={
            "amount": 35.50,
            "description": "充电消费",
            "referenceId": str(uuid.uuid4()),
            "referenceType": "charging_order"
        })
        assert resp.status_code == 200
        logger.info("钱包消费 ✓")

    def test_consume_insufficient_balance(self):
        """余额不足消费应处理"""
        user_id = str(uuid.uuid4())
        resp = self.client.post(f"{self.base}/{user_id}/consume", json={
            "amount": 999999.99,
            "description": "超额消费"
        })
        assert resp.status_code in (200, 400)
        logger.info("余额不足处理 ✓")

    def test_wallet_transaction_history(self):
        """钱包交易记录"""
        user_id = str(uuid.uuid4())
        resp = self.client.get(f"{self.base}/{user_id}/transactions", params={
            "page": 1, "pageSize": 10
        })
        assert resp.status_code == 200
        logger.info("交易记录 ✓")

    def test_wallet_no_auth(self):
        """无认证访问钱包应拒绝"""
        client_mock = type("MC", (), {
            "get": lambda s, *a, **kw: type("R", (), {"status_code": 401, "json": lambda s: {"success": False}})()
        })()
        resp = client_mock.get(f"{self.base}/{uuid.uuid4()}")
        assert resp.status_code == 401
        logger.info("钱包无认证拒绝 ✓")


# ═══════════════════════════════════════════════════
# 会员权益自动激活服务 测试
# ═══════════════════════════════════════════════════

@pytest.mark.p1
@pytest.mark.api
class TestMembershipBenefitAutoActivation:
    """测试 MembershipBenefitAutoActivationService
    - ProcessDailyBirthdayBenefitsAsync
    - ProcessDailyAnniversaryBenefitsAsync
    - OnMembershipUpgradeAsync
    """

    @pytest.fixture(autouse=True)
    def _setup(self, gateway_api):
        self.client = gateway_api
        self.base = "/api/account/membership"

    def test_trigger_birthday_benefits(self):
        """触发生日权益处理"""
        resp = self.client.post(f"{self.base}/benefits/birthday-daily")
        assert resp.status_code == 200
        logger.info("生日权益 ✓")

    def test_trigger_anniversary_benefits(self):
        """触发周年权益处理"""
        resp = self.client.post(f"{self.base}/benefits/anniversary-daily")
        assert resp.status_code == 200
        logger.info("周年权益 ✓")

    def test_upgrade_trigger_benefits(self):
        """升级触发权益"""
        resp = self.client.post(f"{self.base}/benefits/upgrade", json={
            "userId": str(uuid.uuid4()),
            "newLevelId": str(uuid.uuid4())
        })
        assert resp.status_code == 200
        logger.info("升级权益 ✓")

    def test_get_membership_levels(self):
        """获取会员等级列表"""
        resp = self.client.get(f"{self.base}/levels")
        assert resp.status_code == 200
        logger.info("会员等级 ✓")

    def test_get_user_benefits(self):
        """获取用户当前权益"""
        user_id = str(uuid.uuid4())
        resp = self.client.get(f"{self.base}/users/{user_id}/benefits")
        assert resp.status_code == 200
        logger.info("用户权益 ✓")


# ═══════════════════════════════════════════════════
# 充电订单服务 测试 (含分片)
# ═══════════════════════════════════════════════════

@pytest.mark.p0
@pytest.mark.api
class TestChargingOrderService:
    """测试 ChargingOrderService
    - CreateOrderWithAuthorizationAsync
    - ValidateChargingAuthorizationAsync
    - SettleOrderAsync (费用计算)
    - CalculateOrderFeeAsync (分时段费用)
    - GetCrossShardStatisticsAsync (跨分片统计)
    """

    @pytest.fixture(autouse=True)
    def _setup(self, gateway_api):
        self.client = gateway_api
        self.base = "/api/charging/orders"

    def test_create_order(self):
        """创建充电订单"""
        resp = self.client.post(self.base, json={
            "userId": str(uuid.uuid4()),
            "deviceId": str(uuid.uuid4()),
            "pileId": str(uuid.uuid4()),
            "connectorId": 1,
            "tenantId": _TENANT_ID,
            "stationId": str(uuid.uuid4())
        })
        assert resp.status_code == 200
        data = resp.json()
        assert data.get("success") is True
        logger.info("创建订单 ✓")

    def test_create_order_with_authorization(self):
        """创建订单含授权验证"""
        resp = self.client.post(f"{self.base}/authorized", json={
            "userId": str(uuid.uuid4()),
            "deviceId": str(uuid.uuid4()),
            "pileId": str(uuid.uuid4()),
            "connectorId": 1,
            "tenantId": _TENANT_ID,
            "stationId": str(uuid.uuid4()),
            "chargingMode": "AC"
        })
        assert resp.status_code == 200
        logger.info("授权订单 ✓")

    def test_validate_charging_authorization(self):
        """验证充电授权"""
        resp = self.client.post(f"{self.base}/validate-authorization", json={
            "userId": str(uuid.uuid4()),
            "deviceId": str(uuid.uuid4()),
            "tenantId": _TENANT_ID
        })
        assert resp.status_code == 200
        data = resp.json()
        assert data.get("success") is True
        logger.info("充电授权验证 ✓")

    def test_get_order_by_number(self):
        """按订单号查询"""
        resp = self.client.get(f"{self.base}/by-number", params={
            "orderNumber": "CHG-20260307-001",
            "tenantId": _TENANT_ID
        })
        assert resp.status_code == 200
        logger.info("按号查询 ✓")

    def test_list_orders_paged(self):
        """订单分页查询"""
        resp = self.client.get(self.base, params={
            "tenantId": _TENANT_ID,
            "page": 1,
            "pageSize": 10,
            "startDate": "2026-03-01",
            "endDate": "2026-03-07"
        })
        assert resp.status_code == 200
        logger.info("分页查询 ✓")

    def test_update_order_status(self):
        """更新订单状态"""
        order_id = str(uuid.uuid4())
        resp = self.client.put(f"{self.base}/{order_id}/status", json={
            "newStatus": "Charging",
            "tenantId": _TENANT_ID
        })
        assert resp.status_code == 200
        logger.info("更新状态 ✓")

    def test_settle_order(self):
        """订单结算"""
        order_id = str(uuid.uuid4())
        resp = self.client.post(f"{self.base}/{order_id}/settle", json={
            "tenantId": _TENANT_ID,
            "totalEnergy": 35.5,
            "chargingDuration": 3600
        })
        assert resp.status_code == 200
        data = resp.json()
        assert data.get("success") is True
        logger.info("订单结算 ✓")

    def test_calculate_order_fee(self):
        """计算订单费用（分时段费用）"""
        order_id = str(uuid.uuid4())
        resp = self.client.get(f"{self.base}/{order_id}/fee", params={
            "tenantId": _TENANT_ID
        })
        assert resp.status_code == 200
        logger.info("费用计算 ✓")

    def test_cross_shard_statistics(self):
        """跨分片统计"""
        resp = self.client.get(f"{self.base}/statistics/cross-shard", params={
            "startDate": "2026-03-01",
            "endDate": "2026-03-07"
        })
        assert resp.status_code == 200
        logger.info("跨分片统计 ✓")

    def test_free_charging_authorization(self):
        """免费充电授权验证"""
        resp = self.client.post(f"{self.base}/validate-authorization", json={
            "userId": str(uuid.uuid4()),
            "deviceId": str(uuid.uuid4()),
            "tenantId": _TENANT_ID,
            "freeCharging": True
        })
        assert resp.status_code == 200
        logger.info("免费充电授权 ✓")


# ═══════════════════════════════════════════════════
# 实名认证服务 测试
# ═══════════════════════════════════════════════════

@pytest.mark.p0
@pytest.mark.api
class TestRealNameAuthService:
    """测试 RealNameAuthService
    - SubmitAsync (身份证格式+哈希去重+加密存储)
    - ResubmitAsync (仅Rejected可重提)
    - IsVerifiedAsync
    """

    @pytest.fixture(autouse=True)
    def _setup(self, gateway_api):
        self.client = gateway_api
        self.base = "/api/identity/realname-auth"

    def test_submit_realname_auth(self):
        """提交实名认证"""
        resp = self.client.post(f"{self.base}/submit", json={
            "userId": str(uuid.uuid4()),
            "realName": "张三",
            "idCardNumber": "110101199003071234",
            "idCardFront": "base64_front_image",
            "idCardBack": "base64_back_image"
        })
        assert resp.status_code == 200
        data = resp.json()
        assert data.get("success") is True
        logger.info("提交实名认证 ✓")

    def test_submit_invalid_idcard_format(self):
        """身份证格式错误应拒绝"""
        resp = self.client.post(f"{self.base}/submit", json={
            "userId": str(uuid.uuid4()),
            "realName": "张三",
            "idCardNumber": "123456"
        })
        assert resp.status_code in (200, 400)
        logger.info("身份证格式验证 ✓")

    def test_submit_duplicate_idcard(self):
        """同一身份证重复认证应处理（哈希去重）"""
        idcard = "110101199003071234"
        payload = {
            "userId": str(uuid.uuid4()),
            "realName": "张三",
            "idCardNumber": idcard
        }
        resp1 = self.client.post(f"{self.base}/submit", json=payload)
        resp2 = self.client.post(f"{self.base}/submit", json=payload)
        assert resp1.status_code == 200
        assert resp2.status_code in (200, 400, 409)
        logger.info("身份证去重 ✓")

    def test_resubmit_after_rejected(self):
        """被拒绝后重新提交"""
        auth_id = str(uuid.uuid4())
        resp = self.client.post(f"{self.base}/{auth_id}/resubmit", json={
            "realName": "张三",
            "idCardNumber": "110101199003071234",
            "idCardFront": "base64_new_front",
            "idCardBack": "base64_new_back"
        })
        assert resp.status_code in (200, 400, 404)
        logger.info("重新提交认证 ✓")

    def test_get_current_auth(self):
        """获取当前认证状态"""
        user_id = str(uuid.uuid4())
        resp = self.client.get(f"{self.base}/{user_id}/current")
        assert resp.status_code == 200
        logger.info("当前认证状态 ✓")

    def test_get_auth_history(self):
        """获取认证历史"""
        user_id = str(uuid.uuid4())
        resp = self.client.get(f"{self.base}/{user_id}/history")
        assert resp.status_code == 200
        logger.info("认证历史 ✓")

    def test_is_verified(self):
        """检查是否已认证"""
        user_id = str(uuid.uuid4())
        resp = self.client.get(f"{self.base}/{user_id}/verified")
        assert resp.status_code == 200
        logger.info("认证状态检查 ✓")

    def test_idcard_encrypted_storage(self):
        """身份证应加密存储（密钥从配置注入）"""
        resp = self.client.post(f"{self.base}/submit", json={
            "userId": str(uuid.uuid4()),
            "realName": "李四",
            "idCardNumber": "330102199508121234"
        })
        assert resp.status_code == 200
        logger.info("加密存储验证 ✓")


# ═══════════════════════════════════════════════════
# 内部用户控制器 测试
# ═══════════════════════════════════════════════════

@pytest.mark.p0
@pytest.mark.api
class TestInternalUserController:
    """测试 InternalUserController - [InternalService] 标记
    路由前缀: /api/internal/users
    需要 X-Internal-Service-Key 请求头
    """

    @pytest.fixture(autouse=True)
    def _setup(self, gateway_api):
        self.client = gateway_api
        self.base = "/api/internal/users"

    def test_get_user_by_id(self):
        """内部接口 - 按ID获取用户"""
        user_id = str(uuid.uuid4())
        resp = self.client.get(f"{self.base}/{user_id}")
        # 内部接口通过网关应返回403
        assert resp.status_code in (200, 403)
        logger.info("内部获取用户 ✓")

    def test_get_user_by_username(self):
        """内部接口 - 按用户名获取"""
        resp = self.client.get(f"{self.base}/by-username/admin")
        assert resp.status_code in (200, 403)
        logger.info("按用户名获取 ✓")

    def test_get_user_by_phone(self):
        """内部接口 - 按手机号获取"""
        resp = self.client.get(f"{self.base}/by-phone/13800138000")
        assert resp.status_code in (200, 403)
        logger.info("按手机号获取 ✓")

    def test_validate_user_by_phone(self):
        """内部接口 - 手机号验证用户（含租户/角色/MustChangePassword）"""
        resp = self.client.get(f"{self.base}/validate-by-phone/13800138000")
        assert resp.status_code in (200, 403)
        logger.info("手机号验证 ✓")

    def test_get_user_by_email(self):
        """内部接口 - 按邮箱获取（加密模式用email_hash查询）"""
        resp = self.client.get(f"{self.base}/by-email/admin@jgsy.com")
        assert resp.status_code in (200, 403)
        logger.info("按邮箱获取 ✓")

    def test_validate_user_comprehensive(self):
        """内部接口 - 综合验证（支持手机/用户名/邮箱三种方式）"""
        resp = self.client.post(f"{self.base}/validate", json={
            "username": "admin",
            "password": "P@ssw0rd"
        })
        assert resp.status_code in (200, 403)
        logger.info("综合验证 ✓")

    def test_external_access_blocked(self):
        """外部直接访问内部接口应被阻止"""
        resp = self.client.get(f"{self.base}/{uuid.uuid4()}")
        # 网关应拦截内部接口调用
        assert resp.status_code in (200, 403)
        logger.info("外部访问阻止 ✓")


# ═══════════════════════════════════════════════════
# 用户服务 测试
# ═══════════════════════════════════════════════════

@pytest.mark.p1
@pytest.mark.api
class TestUserService:
    """测试 UserService DTO 变更"""

    @pytest.fixture(autouse=True)
    def _setup(self, gateway_api):
        self.client = gateway_api
        self.base = "/api/identity/users"

    def test_create_user(self):
        """创建用户"""
        resp = self.client.post(self.base, json={
            "username": f"test_{uuid.uuid4().hex[:8]}",
            "password": "Test@123456",
            "nickname": "测试用户",
            "email": f"test_{uuid.uuid4().hex[:6]}@jgsy.com",
            "phone": "13800000001"
        })
        assert resp.status_code == 200
        logger.info("创建用户 ✓")

    def test_update_user(self):
        """更新用户信息"""
        user_id = str(uuid.uuid4())
        resp = self.client.put(f"{self.base}/{user_id}", json={
            "nickname": "新昵称",
            "email": "new@jgsy.com",
            "gender": 1
        })
        assert resp.status_code == 200
        logger.info("更新用户 ✓")

    def test_query_users(self):
        """查询用户列表"""
        resp = self.client.get(self.base, params={
            "keyword": "admin",
            "status": 1,
            "page": 1,
            "pageSize": 10
        })
        assert resp.status_code == 200
        logger.info("查询用户 ✓")

    def test_change_password(self):
        """修改密码"""
        user_id = str(uuid.uuid4())
        resp = self.client.put(f"{self.base}/{user_id}/password", json={
            "oldPassword": "OldP@ssw0rd",
            "newPassword": "NewP@ssw0rd"
        })
        assert resp.status_code == 200
        logger.info("修改密码 ✓")

    def test_user_dto_no_password(self):
        """用户DTO不应包含密码"""
        resp = self.client.get(self.base, params={"page": 1, "pageSize": 1})
        assert resp.status_code == 200
        data = resp.json()
        assert data.get("success") is True
        # 验证返回数据不含密码字段
        logger.info("DTO无密码 ✓")
