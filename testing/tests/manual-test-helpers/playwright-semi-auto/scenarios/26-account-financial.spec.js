/**
 * 账户金融服务测试场景 - 26
 * 
 * 覆盖模块：
 * ✅ JGSY.AGI.Account - Membership（会员管理/等级/消费升降级）
 * ✅ JGSY.AGI.Account - Points（积分体系/赚取/使用/锁定/过期）
 * ✅ JGSY.AGI.Account - Recharge（充值管理/发起/取消/历史）
 * ✅ JGSY.AGI.Account - Withdraw（提现管理/申请/审核/取消）
 * ✅ JGSY.AGI.Account - Invoice（发票管理/申请/开具/红冲）
 * ✅ JGSY.AGI.Account - Coupon（优惠券/模板/发放/使用/验证）
 * ✅ JGSY.AGI.Account - Vehicle（车辆管理）
 * ✅ JGSY.AGI.Account - PaymentCallback（支付回调/微信/支付宝/银联）
 * 
 * 测试步骤：7 个核心场景
 * 总耗时：约 35 分钟
 * 难度：HIGH（涉及金融级数据精度和状态流转）
 */

const { test, expect } = require('@playwright/test');
const { SemiAutoHelper } = require('../helpers/semi-auto-helper');
const { TestData } = require('../helpers/test-data');

let helper;

test.beforeEach(async ({ page }) => {
  helper = new SemiAutoHelper(page);
  await helper.navigate('http://localhost:3000');
  await helper.login('admin@example.com', 'P@ssw0rd');
  await helper.logStep('✅ 登录成功 - 准备开始账户金融服务测试');
});

test.afterEach(async ({ page }) => {
  await helper.generateReport('account-financial');
});

// ========================================
// 场景 1: 会员等级管理
// ========================================
test('Step 1: 会员等级与消费升降级', async ({ page }) => {
  await helper.logStep('【场景 1】会员等级管理 - 开始');

  await helper.navigate('http://localhost:3000/account/membership');

  await helper.showPrompt(
    '👑 会员等级管理验证',
    `请验证以下功能：

    1️⃣ 会员等级列表（等级名称/门槛/权益/折扣）
    2️⃣ 创建/编辑/删除会员等级
    3️⃣ 等级分布统计（各等级用户数/占比）
    4️⃣ 查看用户当前会员信息
    5️⃣ 初始化会员（新用户自动分配）
    6️⃣ 手动调整等级（管理员操作）
    7️⃣ 消费升级触发（消费满足阈值 → 自动升级）
    8️⃣ 升降级日志查看

    ⚠️ 业务逻辑重点：
    - 等级升级自动触发
    - 降级规则（长期不消费/积分过期等）
    - 等级权益联动（折扣/积分倍数/专属服务）

    完成后请点击 ✅ 确认`
  );

  await helper.takeScreenshot('26-01-membership');
  await helper.logStep('✅ 会员等级管理验证完成');
});

// ========================================
// 场景 2: 积分体系
// ========================================
test('Step 2: 积分赚取/使用/锁定/过期全流程', async ({ page }) => {
  await helper.logStep('【场景 2】积分体系 - 开始');

  await helper.navigate('http://localhost:3000/account/points');

  await helper.showPrompt(
    '💎 积分体系验证',
    `请验证以下功能：

    1️⃣ 积分余额查询（可用积分/冻结积分/累计积分）
    2️⃣ 积分统计面板（本月赚取/使用/过期/趋势图）
    3️⃣ 赚取积分（充电消费 → 按规则获得积分）
    4️⃣ 使用积分（抵扣充电费用/兑换优惠券）
    5️⃣ 锁定积分（活动锁定/订单锁定）
    6️⃣ 解锁积分（取消活动/取消订单返还）
    7️⃣ 手动调整积分（管理员加减积分 + 原因备注）
    8️⃣ 积分交易流水（时间/类型/数量/余额/来源）
    9️⃣ 即将过期积分提醒
    🔟 积分计算规则配置

    ⚠️ 金融精度重点：
    - 积分不能为负
    - 使用积分不能超过可用余额
    - 锁定积分不能被使用
    - 过期积分自动清零有记录

    完成后请点击 ✅ 确认`
  );

  await helper.takeScreenshot('26-02-points');
  await helper.logStep('✅ 积分体系验证完成');
});

// ========================================
// 场景 3: 充值管理
// ========================================
test('Step 3: 钱包充值全流程', async ({ page }) => {
  await helper.logStep('【场景 3】充值管理 - 开始');

  await helper.navigate('http://localhost:3000/account/recharge');

  await helper.showPrompt(
    '💰 充值管理验证',
    `请验证以下功能：

    1️⃣ 充值统计（充值总额/今日充值/充值次数/平均金额）
    2️⃣ 充值列表（金额/渠道/状态/时间）
    3️⃣ 发起充值：
       - 选择充值金额（预设金额/自定义金额）
       - 选择支付渠道（微信/支付宝/银联）
       - 提交充值请求
    4️⃣ 查看充值详情
    5️⃣ 充值状态跟踪（待支付→支付中→已完成/已取消/已超时）
    6️⃣ 充值历史记录
    7️⃣ 取消充值（待支付状态可取消）

    ⚠️ 业务逻辑重点：
    - 充值金额 > 0 且有上限
    - 已完成的充值不能取消
    - 超时自动取消
    - 充值成功后钱包余额实时更新

    完成后请点击 ✅ 确认`
  );

  await helper.takeScreenshot('26-03-recharge');
  await helper.logStep('✅ 充值管理验证完成');
});

// ========================================
// 场景 4: 提现管理
// ========================================
test('Step 4: 提现申请/审核/处理全流程', async ({ page }) => {
  await helper.logStep('【场景 4】提现管理 - 开始');

  await helper.navigate('http://localhost:3000/account/withdraw');

  await helper.showPrompt(
    '💸 提现管理验证',
    `请验证以下功能：

    1️⃣ 提现统计（提现总额/待处理/已完成/拒绝数）
    2️⃣ 申请提现：
       - 输入提现金额（不超过可提现余额）
       - 选择提现方式（银行卡/微信/支付宝）
       - 填写提现信息
    3️⃣ 提现审核（管理员）：
       - 待审核列表
       - 审核通过 / 审核拒绝（填写拒绝原因）
    4️⃣ 提现状态流转：申请→审核中→通过→打款→完成 / →拒绝
    5️⃣ 取消提现（审核前可取消）
    6️⃣ 提现历史记录

    ⚠️ 金融风控重点：
    - 提现金额不能超过可用余额
    - 单日/单次提现限额
    - 提现手续费计算
    - 已打款的不能取消/退回

    完成后请点击 ✅ 确认`
  );

  await helper.takeScreenshot('26-04-withdraw');
  await helper.logStep('✅ 提现管理验证完成');
});

// ========================================
// 场景 5: 发票管理
// ========================================
test('Step 5: 电子发票申请/开具/红冲', async ({ page }) => {
  await helper.logStep('【场景 5】发票管理 - 开始');

  await helper.navigate('http://localhost:3000/account/invoice');

  await helper.showPrompt(
    '🧾 发票管理验证',
    `请验证以下功能：

    1️⃣ 发票抬头管理（创建/编辑/删除/设置默认抬头）
    2️⃣ 申请开票：
       - 选择订单/充值记录
       - 选择抬头
       - 个人/企业发票类型
    3️⃣ 发票列表（编号/类型/金额/状态/时间）
    4️⃣ 发票详情查看
    5️⃣ 发票统计（开票金额/数量）
    6️⃣ 发票管理（管理员审核/开具）
       - 审核开票申请
       - 填写开票信息
       - 填写邮寄信息
    7️⃣ 红冲操作（对已开发票进行红冲/作废）
    8️⃣ 红冲完成确认

    ⚠️ 财务合规重点：
    - 已开票金额不能超过实际消费
    - 同一订单不能重复开票
    - 红冲需要完整审批流
    - 发票编号唯一性

    完成后请点击 ✅ 确认`
  );

  await helper.takeScreenshot('26-05-invoice');
  await helper.logStep('✅ 发票管理验证完成');
});

// ========================================
// 场景 6: 优惠券系统
// ========================================
test('Step 6: 优惠券模板/发放/使用/验证', async ({ page }) => {
  await helper.logStep('【场景 6】优惠券系统 - 开始');

  await helper.navigate('http://localhost:3000/account/coupons');

  await helper.showPrompt(
    '🎫 优惠券系统验证',
    `请验证以下功能：

    1️⃣ 我的优惠券（可用/已使用/已过期分组展示）
    2️⃣ 优惠券统计
    3️⃣ 创建优惠券模板（管理员）：
       - 优惠券类型（满减/折扣/抵扣/免费）
       - 使用条件（门槛金额/适用场景/有效期）
       - 发放限制（总量/每人限领）
    4️⃣ 发放优惠券（单个/批量发放给用户）
    5️⃣ 使用优惠券（订单结算时选择优惠券）
    6️⃣ 验证优惠券（检查是否可用/过期/限制）

    ⚠️ 业务逻辑重点：
    - 优惠券不能叠加使用（或有叠加规则）
    - 过期优惠券不能使用
    - 已用优惠券不能重复使用
    - 取消订单后优惠券自动返还
    - 优惠后金额不能为负

    完成后请点击 ✅ 确认`
  );

  await helper.takeScreenshot('26-06-coupons');
  await helper.logStep('✅ 优惠券系统验证完成');
});

// ========================================
// 场景 7: 车辆管理与支付回调
// ========================================
test('Step 7: 车辆管理与支付回调处理', async ({ page }) => {
  await helper.logStep('【场景 7】车辆与支付 - 开始');

  // 7.1 车辆管理
  await helper.navigate('http://localhost:3000/account/vehicles');

  await helper.showPrompt(
    '🚗 车辆管理验证',
    `请验证以下功能：

    1️⃣ 车辆列表（车牌号/品牌/型号/默认车辆标记）
    2️⃣ 添加车辆（车牌号/品牌/型号/VIN码）
    3️⃣ 编辑车辆信息
    4️⃣ 设为默认车辆
    5️⃣ 删除车辆
    6️⃣ 车牌号格式校验（新能源/燃油车各格式）
    7️⃣ 同一账户下车牌号唯一性

    完成后请点击 ✅ 确认`
  );

  // 7.2 支付回调
  await helper.showPrompt(
    '💳 支付回调验证',
    `请验证以下功能（需要配合查看日志/API）：

    1️⃣ 查看支付状态查询接口
    2️⃣ 模拟微信支付回调 → 验证订单状态更新
    3️⃣ 模拟支付宝回调 → 验证金额入账
    4️⃣ 回调幂等性（重复回调不重复入账）
    5️⃣ 回调签名验证（非法签名拒绝处理）

    ⚠️ 安全重点：
    - 回调必须验证签名
    - 金额必须与订单金额一致
    - 重复回调要幂等
    - 异常回调有告警

    完成后请点击 ✅ 确认`
  );

  await helper.takeScreenshot('26-07-vehicle-payment');
  await helper.logStep('✅ 车辆管理与支付验证完成');
});
