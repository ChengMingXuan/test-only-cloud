/**
 * 充电服务高级功能深度测试 - 32
 *
 * 补充场景04未覆盖的子控制器与复杂业务逻辑：
 * ✅ Reservation（预约全流程：创建→签到→开始充电→取消/过期/统计/配置）
 * ✅ Refund（退款全流程：申请→审核→回调确认→拒绝→重试→统计）
 * ✅ OcppDebug（OCPP 协议调试：消息日志/统计/调试会话/测试用例/执行/发送消息）
 * ✅ ChargingPricing（计价规则：分时电价/费率计算/预估费用）
 * ✅ FreeChargingQuota（免费充电配额：账户/配额/明细/发放/使用/退还/校验）
 * ✅ DataLifecycle（数据生命周期：心跳归档/订单日志归档/清理/全量执行/统计）
 * ✅ HlhtIntegration（互联互通：订单同步/批量同步/拉取更新/站点同步/连接器同步/失败重试/清理/记录/统计）
 * ✅ AdminOrder（管理端订单管理）
 *
 * 测试步骤：10 个深度场景
 * 总耗时：约 50 分钟
 * 难度：CRITICAL（涉及金融支付、协议调试、数据一致性）
 */

const { test, expect } = require('@playwright/test');
const { SemiAutoHelper } = require('../helpers/semi-auto-helper');
const { TestData } = require('../helpers/test-data');

let helper;

test.beforeEach(async ({ page }) => {
  helper = new SemiAutoHelper(page);
  await helper.navigate('http://localhost:3000');
  await helper.login('admin@example.com', 'P@ssw0rd');
  await helper.logStep('✅ 登录成功 - 准备开始充电高级功能测试');
});

test.afterEach(async ({ page }) => {
  await helper.generateReport('charging-advanced');
});

// ========================================
// 场景 1: 预约全流程
// ========================================
test('Step 1: 充电预约全流程 - 创建→签到→充电→取消/过期', async ({ page }) => {
  await helper.logStep('【场景 1】预约全流程');

  await helper.navigate('http://localhost:3000/charging/reservation');

  await helper.showPrompt(
    '📅 充电预约全流程验证',
    `请验证以下完整流程：

    1️⃣ 查询充电口可用性（station-availability / port-availability）
    2️⃣ 创建预约（选择充电口/预约时段/车辆）
    3️⃣ 预约详情查看（预约号/状态/倒计时）
    4️⃣ 用户签到（到达充电站后签到确认）
    5️⃣ 开始充电（签到后关联充电订单）
    6️⃣ 取消预约（用户主动取消/规则限制/退款逻辑）
    7️⃣ 预约过期自动处理（未签到超时→自动取消→释放充电口）
    8️⃣ 预约统计（日/周/月预约量/取消率/签到率）
    9️⃣ 预约配置（提前预约时间/最大预约数/超时分钟数）
    🔟 用户预约资格检查（是否有未完成预约/黑名单等）

    ⚠️ 边界测试：
    - 同一充电口同一时段重复预约
    - 预约时间段交叉冲突
    - 预约开始前 1 分钟取消
    - 同一用户同时存在多个活跃预约

    完成后请点击 ✅ 确认`
  );

  await helper.takeScreenshot('32-01-reservation');
  await helper.logStep('✅ 预约全流程验证完成');
});

// ========================================
// 场景 2: 退款全流程
// ========================================
test('Step 2: 退款全流程 - 申请→审核→回调→统计', async ({ page }) => {
  await helper.logStep('【场景 2】退款全流程');

  await helper.navigate('http://localhost:3000/charging/refund');

  await helper.showPrompt(
    '💸 退款全流程验证',
    `请验证以下流程：

    1️⃣ 申请退款（选择订单→输入原因→提交）
    2️⃣ 退款列表查看（按状态/时间/金额筛选）
    3️⃣ 退款详情（原订单信息/退款金额/渠道/进度）
    4️⃣ 用户取消退款申请
    5️⃣ 管理员审核退款（通过/拒绝/部分退款）
    6️⃣ 退款回调处理（支付渠道回调确认到账）
    7️⃣ 退款失败重试
    8️⃣ 退款统计（总退款额/退款率/平均处理时间）

    ⚠️ 业务逻辑重点：
    - 部分退款：退款金额 ≤ 原支付金额
    - 退款渠道必须原路返回
    - 已退款订单状态不可逆
    - 退款后优惠券/积分的冲回处理

    完成后请点击 ✅ 确认`
  );

  await helper.takeScreenshot('32-02-refund');
  await helper.logStep('✅ 退款全流程验证完成');
});

// ========================================
// 场景 3: OCPP 协议调试
// ========================================
test('Step 3: OCPP 协议调试 - 消息/会话/测试用例', async ({ page }) => {
  await helper.logStep('【场景 3】OCPP 调试');

  await helper.navigate('http://localhost:3000/charging/ocpp-debug');

  await helper.showPrompt(
    '🔧 OCPP 协议调试验证',
    `请验证以下功能：

    【消息管理】
    1️⃣ OCPP 消息日志列表（时间/方向/消息类型/充电桩ID/内容）
    2️⃣ 消息详情查看（完整 JSON 解析展示）
    3️⃣ 消息统计（按类型/按桩/按时间分布）

    【调试会话】
    4️⃣ 创建调试会话（选择充电桩/设置过滤条件）
    5️⃣ 调试会话列表（活跃/已结束）
    6️⃣ 停止调试会话
    7️⃣ 会话内实时消息流

    【测试用例】
    8️⃣ 创建 OCPP 测试用例（名称/步骤/预期结果）
    9️⃣ 编辑/删除测试用例
    🔟 执行测试用例（发送 OCPP 消息并校验返回）
    1️⃣1️⃣ 查看执行记录（通过/失败/耗时）

    【自定义消息发送】
    1️⃣2️⃣ 手动发送 OCPP 消息（选择充电桩/消息类型/编辑 payload）

    完成后请点击 ✅ 确认`
  );

  await helper.takeScreenshot('32-03-ocpp-debug');
  await helper.logStep('✅ OCPP 调试验证完成');
});

// ========================================
// 场景 4: 计价规则管理
// ========================================
test('Step 4: 分时电价与计价规则管理', async ({ page }) => {
  await helper.logStep('【场景 4】计价规则');

  await helper.navigate('http://localhost:3000/charging/pricing');

  await helper.showPrompt(
    '💰 计价规则管理验证',
    `请验证以下功能：

    1️⃣ 查看充电站计价规则列表（站点ID→时段→电价/服务费）
    2️⃣ 查看当前时刻实时电价
    3️⃣ 计算充电费用（输入电量→返回电费+服务费+总费用）
    4️⃣ 预估充电费用（输入预计充电量→预估金额区间）
    5️⃣ 电价汇总（站点各时段价格一览）

    ⚠️ 边界测试：
    - 跨时段充电的费用计算（如 22:00 开始充到次日 2:00）
    - 充电量为 0 / 极小值（0.001 kWh）
    - 电价为 0 的免费时段
    - 夏季/冬季不同电价策略切换

    完成后请点击 ✅ 确认`
  );

  await helper.takeScreenshot('32-04-pricing');
  await helper.logStep('✅ 计价规则验证完成');
});

// ========================================
// 场景 5: 免费充电配额
// ========================================
test('Step 5: 免费充电配额全流程', async ({ page }) => {
  await helper.logStep('【场景 5】免费配额');

  await helper.navigate('http://localhost:3000/charging/free-quota');

  await helper.showPrompt(
    '🎁 免费充电配额验证',
    `请验证以下功能：

    1️⃣ 查看我的免费充电账户（总配额/已用/剩余）
    2️⃣ 查看我的配额明细（各来源配额分别展示）
    3️⃣ 配额详情列表（发放记录/使用记录/退还记录）
    4️⃣ 管理员发放配额（选择用户→输入额度→发放原因）
    5️⃣ 使用配额（充电支付时抵扣）
    6️⃣ 退还配额（退款时返还已用配额）
    7️⃣ 配额校验（检查用户是否有足够免费额度）

    ⚠️ 边界测试：
    - 配额恰好为 0 时使用
    - 发放负数配额
    - 退还超过已用的金额
    - 多个配额同时使用的优先级

    完成后请点击 ✅ 确认`
  );

  await helper.takeScreenshot('32-05-free-quota');
  await helper.logStep('✅ 免费配额验证完成');
});

// ========================================
// 场景 6: 互联互通（HLHT）
// ========================================
test('Step 6: 互联互通 HLHT 集成全流程', async ({ page }) => {
  await helper.logStep('【场景 6】HLHT 互联互通');

  await helper.navigate('http://localhost:3000/charging/hlht');

  await helper.showPrompt(
    '🔗 互联互通 HLHT 验证',
    `请验证以下功能：

    【订单同步】
    1️⃣ 同步单个订单到 HLHT 平台（sync-order）
    2️⃣ 批量同步订单（batch-sync）
    3️⃣ 拉取 HLHT 平台更新（pull-updates）

    【站点与连接器同步】
    4️⃣ 同步充电站信息（sync-station）
    5️⃣ 同步连接器信息（sync-connector）

    【异常处理】
    6️⃣ 失败重试机制（retry-failed）
    7️⃣ 过期数据清理（cleanup）

    【数据查询】
    8️⃣ 同步记录列表（成功/失败/时间筛选）
    9️⃣ 统计概览（同步成功率/失败率/最后同步时间）

    ⚠️ 关键测试：
    - 网络异常时的重试机制
    - 数据冲突时的处理策略
    - 大批量同步的性能表现

    完成后请点击 ✅ 确认`
  );

  await helper.takeScreenshot('32-06-hlht');
  await helper.logStep('✅ HLHT 互联互通验证完成');
});

// ========================================
// 场景 7: 数据生命周期管理
// ========================================
test('Step 7: 数据生命周期 - 归档/清理/全量执行', async ({ page }) => {
  await helper.logStep('【场景 7】数据生命周期');

  await helper.navigate('http://localhost:3000/charging/data-lifecycle');

  await helper.showPrompt(
    '🔄 数据生命周期管理验证',
    `请验证以下功能：

    1️⃣ 心跳数据归档（archive-heartbeats：指定天数前的心跳→归档表）
    2️⃣ 订单日志归档（archive-order-logs：历史日志→归档存储）
    3️⃣ 过期数据清理（cleanup：清理归档后的原始数据）
    4️⃣ 全量执行（execute-full：一键归档+清理）
    5️⃣ 数据统计（stats：各表数据量/归档量/清理量/存储占用）

    ⚠️ 关键测试：
    - 归档后原表数据是否正确减少
    - 归档数据是否可查询
    - 清理操作是否只删已归档数据
    - 归档/清理的并发安全
    - 大数据量归档的性能表现

    完成后请点击 ✅ 确认`
  );

  await helper.takeScreenshot('32-07-data-lifecycle');
  await helper.logStep('✅ 数据生命周期验证完成');
});

// ========================================
// 场景 8: 管理端订单管理
// ========================================
test('Step 9: 管理端订单管理 - 查询/状态管控/导出', async ({ page }) => {
  await helper.logStep('【场景 9】管理端订单');

  await helper.navigate('http://localhost:3000/charging/admin-order');

  await helper.showPrompt(
    '📊 管理端订单管理验证',
    `请验证以下功能：

    1️⃣ 订单综合查询（多条件：时间/站点/充电桩/状态/用户/金额区间）
    2️⃣ 订单详情查看（充电曲线/计费明细/支付信息/退款记录）
    3️⃣ 管理员手动结束异常订单
    4️⃣ 管理员手动退款
    5️⃣ 订单数据导出（Excel/CSV）
    6️⃣ 订单删除（仅 admin 权限）

    ⚠️ 查询组合测试 [§3.4]：
    - 无条件查全量
    - 单条件：按站点/按时间/按状态
    - 多条件叠加：站点 + 时间 + 状态 + 金额区间
    - 无结果查询
    - 大数据量分页

    完成后请点击 ✅ 确认`
  );

  await helper.takeScreenshot('32-09-admin-order');
  await helper.logStep('✅ 管理端订单验证完成');
});

// ========================================
// 场景 10: 充电订单核心业务逻辑深度验证
// ========================================
test('Step 10: 充电订单核心业务逻辑深度验证', async ({ page }) => {
  await helper.logStep('【场景 10】核心业务逻辑');

  await helper.navigate('http://localhost:3000/charging/order');

  await helper.showPrompt(
    '⚡ 充电业务逻辑深度验证 [§3.2]',
    `请验证以下核心业务逻辑：

    【状态机验证】
    1️⃣ 合法流转：创建→充电中→充电完成→支付完成→已结算
    2️⃣ 非法流转：已结算→充电中（应拒绝）
    3️⃣ 异常流转：充电中→异常中断→恢复/手动结束

    【计费逻辑验证】
    4️⃣ 电量 × 单价 = 电费（精度到分）
    5️⃣ 服务费按规则计算
    6️⃣ 优惠券/会员折扣/免费配额联合抵扣（优先级）
    7️⃣ 跨时段计费（尖/峰/平/谷切换）

    【并发与异常】
    8️⃣ 同一充电桩同时下发两个充电指令
    9️⃣ 充电过程中网络断开后恢复
    🔟 充电过程中设备故障报警
    1️⃣1️⃣ 支付过程中订单被取消的处理

    完成后请点击 ✅ 确认`
  );

  await helper.takeScreenshot('32-10-business-logic');
  await helper.logStep('✅ 核心业务逻辑验证完成');
});
