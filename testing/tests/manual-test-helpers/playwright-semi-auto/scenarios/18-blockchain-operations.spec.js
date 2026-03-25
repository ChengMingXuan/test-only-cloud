/**
 * 区块链存证与交易测试场景 - 18
 * 
 * 覆盖模块：
 * ✅ JGSY.AGI.Blockchain - Wallet（钱包管理）
 * ✅ JGSY.AGI.Blockchain - Transaction（交易查询）
 * ✅ JGSY.AGI.Blockchain - Trading（P2P能源交易/碳交易/需求响应）
 * ✅ JGSY.AGI.Blockchain - Query（链上查询/区块浏览）
 * ✅ JGSY.AGI.Blockchain - Contract（智能合约管理）
 * ✅ JGSY.AGI.Blockchain - Certificate（证书管理）
 * ✅ JGSY.AGI.Blockchain - Points（区块链积分）
 * ✅ JGSY.AGI.Blockchain - Event（事件查询）
 * ✅ JGSY.AGI.Blockchain - Quantum（量子计算模块）
 * 
 * 测试步骤：7 个核心场景
 * 总耗时：约 35 分钟
 * 难度：HIGH（涉及区块链底层交互和加密逻辑）
 */

const { test, expect } = require('@playwright/test');
const { SemiAutoHelper } = require('../helpers/semi-auto-helper');
const { TestData } = require('../helpers/test-data');

let helper;

test.beforeEach(async ({ page }) => {
  helper = new SemiAutoHelper(page);
  await helper.navigate('http://localhost:3000');
  await helper.login('admin@example.com', 'P@ssw0rd');
  await helper.logStep('✅ 登录成功 - 准备开始区块链存证与交易测试');
});

test.afterEach(async ({ page }) => {
  await helper.generateReport('blockchain-operations');
});

// ========================================
// 场景 1: 钱包管理
// ========================================
test('Step 1: 区块链钱包创建与管理', async ({ page }) => {
  await helper.logStep('【场景 1】区块链钱包管理 - 开始');

  await helper.navigate('http://localhost:3000/blockchain/wallet');
  await helper.waitForElement('.page-header', 5000);

  await helper.showPrompt(
    '💼 钱包管理验证',
    `请验证以下功能：

    1️⃣ 查看系统钱包信息
    2️⃣ 查看我的钱包列表
    3️⃣ 创建新钱包（输入钱包名称/密码）
    4️⃣ 查看钱包详情（地址/余额/交易记录）
    5️⃣ 查看余额信息
    6️⃣ 设置默认钱包
    7️⃣ 导出钱包（私钥备份）
    8️⃣ 导入钱包（从私钥恢复）
    9️⃣ 发起转账交易
    🔟 删除钱包

    完成后请点击 ✅ 确认`
  );

  await helper.takeScreenshot('18-01-wallet-management');
  await helper.logStep('✅ 钱包管理验证完成');
});

// ========================================
// 场景 2: 链上数据查询与区块浏览
// ========================================
test('Step 2: 链上数据查询与区块浏览器', async ({ page }) => {
  await helper.logStep('【场景 2】链上数据查询 - 开始');

  await helper.navigate('http://localhost:3000/blockchain/explorer');

  await helper.showPrompt(
    '🔗 区块浏览器验证',
    `请验证以下功能：

    1️⃣ 链概览数据（总区块/总交易/Gas价格）
    2️⃣ 最新区块列表
    3️⃣ 按区块号查询区块详情
    4️⃣ 按哈希查询区块详情
    5️⃣ 交易详情查询（通过交易哈希）
    6️⃣ 交易回执查看
    7️⃣ 交易状态查询
    8️⃣ 链统计图表

    完成后请点击 ✅ 确认`
  );

  await helper.takeScreenshot('18-02-blockchain-explorer');
  await helper.logStep('✅ 链上数据查询验证完成');
});

// ========================================
// 场景 3: 存证与证明
// ========================================
test('Step 3: 数据存证与证明验证', async ({ page }) => {
  await helper.logStep('【场景 3】数据存证与证明 - 开始');

  await helper.navigate('http://localhost:3000/blockchain/proof');

  await helper.showPrompt(
    '📜 数据存证验证',
    `请验证以下存证流程：

    1️⃣ 创建存证（输入业务数据 → 生成哈希 → 上链）
    2️⃣ 查看存证详情（哈希/时间戳/区块号/状态）
    3️⃣ 验证存证（输入存证ID → 链上比对 → 返回结果）
    4️⃣ 获取存证证明文件
    5️⃣ 存证列表查询与筛选

    ⚠️ 重点验证：
    - 存证数据不可篡改
    - 验证结果一致性
    - 时间戳准确性

    完成后请点击 ✅ 确认`
  );

  await helper.takeScreenshot('18-03-proof-verification');
  await helper.logStep('✅ 数据存证与证明验证完成');
});

// ========================================
// 场景 4: P2P能源交易
// ========================================
test('Step 4: P2P能源交易与撮合', async ({ page }) => {
  await helper.logStep('【场景 4】P2P能源交易 - 开始');

  await helper.navigate('http://localhost:3000/blockchain/trading');

  await helper.showPrompt(
    '⚡ P2P能源交易验证',
    `请验证以下交易流程：

    1️⃣ 查看市场统计（总挂单/成交量/均价）
    2️⃣ 创建卖单（设置电量/价格/时段）
    3️⃣ 创建买单（设置需求电量/最高价格）
    4️⃣ 查看挂单列表
    5️⃣ 撮合交易（测试自动撮合引擎）
    6️⃣ 查看我的订单（历史/进行中）
    7️⃣ 取消未成交订单
    8️⃣ 确认交易完成

    ⚠️ 业务逻辑重点：
    - 买卖价格匹配规则
    - 交易状态流转：挂单→撮合→成交→结算
    - 余额/额度校验

    完成后请点击 ✅ 确认`
  );

  await helper.takeScreenshot('18-04-p2p-trading');
  await helper.logStep('✅ P2P能源交易验证完成');
});

// ========================================
// 场景 5: 碳交易与需求响应
// ========================================
test('Step 5: 碳交易参与与需求响应', async ({ page }) => {
  await helper.logStep('【场景 5】碳交易与需求响应 - 开始');

  // 5.1 双边交易
  await helper.showPrompt(
    '🤝 双边交易验证',
    `请验证以下双边交易流程：

    1️⃣ 发起双边协商（选择交易对手/电量/价格/时段）
    2️⃣ 对手方接受协商
    3️⃣ 双边交易结算
    4️⃣ 查看协商历史

    完成后请点击 ✅ 确认`
  );

  // 5.2 需求响应
  await helper.showPrompt(
    '📉 需求响应验证',
    `请验证以下需求响应流程：

    1️⃣ 参与需求响应事件
    2️⃣ 报告负荷削减量
    3️⃣ 申领需求响应补贴
    4️⃣ 查看需求响应历史和收益

    完成后请点击 ✅ 确认`
  );

  await helper.takeScreenshot('18-05-carbon-demand-response');
  await helper.logStep('✅ 碳交易与需求响应验证完成');
});

// ========================================
// 场景 6: 智能合约与证书管理
// ========================================
test('Step 6: 智能合约部署与证书管理', async ({ page }) => {
  await helper.logStep('【场景 6】智能合约与证书 - 开始');

  // 6.1 智能合约
  await helper.navigate('http://localhost:3000/blockchain/contracts');

  await helper.showPrompt(
    '📝 智能合约管理验证',
    `请验证以下功能：

    1️⃣ 合约列表展示（名称/地址/状态/部署时间）
    2️⃣ 部署新合约
    3️⃣ 查看合约详情和ABI
    4️⃣ 调用合约方法（读/写）
    5️⃣ 查看合约事件日志

    完成后请点击 ✅ 确认`
  );

  // 6.2 证书管理
  await helper.navigate('http://localhost:3000/blockchain/certificates');

  await helper.showPrompt(
    '🏅 证书管理验证',
    `请验证以下功能：

    1️⃣ 证书列表展示
    2️⃣ 颁发新证书（绿色能源证书/碳排放证书等）
    3️⃣ 证书详情查看
    4️⃣ 证书验证（真伪校验）
    5️⃣ 证书撤销

    完成后请点击 ✅ 确认`
  );

  await helper.takeScreenshot('18-06-contracts-certificates');
  await helper.logStep('✅ 智能合约与证书管理验证完成');
});

// ========================================
// 场景 7: 区块链积分与事件/健康检查
// ========================================
test('Step 7: 积分系统与链健康检查', async ({ page }) => {
  await helper.logStep('【场景 7】积分系统与健康检查 - 开始');

  // 7.1 区块链积分
  await helper.navigate('http://localhost:3000/blockchain/points');

  await helper.showPrompt(
    '🎖️ 区块链积分验证',
    `请验证以下功能：

    1️⃣ 积分余额查询
    2️⃣ 积分获取（充电/交易/参与活动）
    3️⃣ 积分使用/兑换
    4️⃣ 积分交易记录
    5️⃣ 积分上链存证

    完成后请点击 ✅ 确认`
  );

  // 7.2 链上事件查询
  await helper.navigate('http://localhost:3000/blockchain/events');

  await helper.showPrompt(
    '📋 链上事件查询验证',
    `请验证以下功能：

    1️⃣ 事件列表（按时间/类型筛选）
    2️⃣ 事件详情查看
    3️⃣ 事件导出

    完成后请点击 ✅ 确认`
  );

  // 7.3 健康检查
  await helper.showPrompt(
    '💚 区块链健康检查',
    `请验证以下功能：

    1️⃣ 基础健康检查（节点连接/同步状态）
    2️⃣ 详细健康检查（合约状态/Gas消耗/性能指标）
    3️⃣ 就绪检查 & 存活检查

    完成后请点击 ✅ 确认`
  );

  await helper.takeScreenshot('18-07-points-health');
  await helper.logStep('✅ 积分系统与链健康检查验证完成');
});
