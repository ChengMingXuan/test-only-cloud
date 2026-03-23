/**
 * 能源交易与商业服务测试场景 - 15
 * 
 * 覆盖模块：
 * ✅ JGSY.AGI.EnergyServices.ElecTrade     (电力交易市场)
 * ✅ JGSY.AGI.EnergyServices.CarbonTrade   (碳交易市场)
 * ✅ JGSY.AGI.EnergyServices.EnergyEff     (能效管理与优化)
 * 
 * 测试步骤：6 个核心场景
 * 总耗时：约 40 分钟
 * 难度：HIGH（涉及复杂的市场机制和商业金融逻辑）
 */

const { test, expect } = require('@playwright/test');
const { SemiAutoHelper } = require('../helpers/semi-auto-helper');
const { TestData } = require('../helpers/test-data');

let helper;

test.beforeEach(async ({ page }) => {
  helper = new SemiAutoHelper(page);
  await helper.navigate('http://localhost:3000');
  await helper.login('admin@example.com', 'P@ssw0rd');
  await helper.logStep('✅ 登录成功 - 准备开始能源交易服务测试');
});

test.afterEach(async ({ page }) => {
  await helper.generateReport('energy-services-trading');
});

/**
 * 步骤 1: 电力市场交易机制
 * 测试内容：日前市场、实时市场、中长期市场
 */
test('Step 1: 电力市场交易机制', async () => {
  await helper.logStep('【场景 1】电力市场交易机制 - 开始');
  
  await helper.navigate('http://localhost:3000/energy/elec-trade');
  await helper.waitForElement('.market-dashboard', 5000);
  
  // 日前市场交易
  await helper.showPrompt(
    '📅 日前电力市场',
    `参与日前电力市场竞拍：
    
    1️⃣ 进入【日前市场】页面
    2️⃣ 查看市场行情：
       • 交易电价曲线（24 小时）
       • 当前需求预测
       • 前面 24 小时均价
       • 历史价格对比
    3️⃣ 提交发电/用电报价：
       • 时段：00:00-06:00（谷时）
         - 报价功率：30 MW
         - 报价电价：0.20 元/kWh（反向交易，希望充电）
       • 时段：06:00-12:00（平时）
         - 报价功率：40 MW
         - 报价电价：0.35 元/kWh
       • 时段：12:00-18:00（尖峰）
         - 报价功率：50 MW（放电）
         - 报价电价：0.65 元/kWh（出价高，期望成交）
       • 时段：18:00-24:00（高峰）
         - 报价功率：45 MW
         - 报价电价：0.55 元/kWh
    4️⃣ 验证报价是否成交
    5️⃣ 查看成交电价和电量
    
    完成后请点击 ✅ 确认`
  );
  
  const dayAheadMarket = await helper.assertElementVisible('[data-testid="day-ahead-market"]');
  expect(dayAheadMarket).toBe(true);
  await helper.takeScreenshot('day-ahead-market-trading');
  
  // 实时市场交易
  await helper.showPrompt(
    '⏱️ 实时电力市场（15 分钟市场）',
    `参与实时电力市场交易：
    
    1️⃣ 进入【实时市场】页面
    2️⃣ 了解实时市场机制：
       • 市场清算周期：15 分钟
       • 当前结算周期：HH:MM-HH:MM
       • 实时电价：X 元/kWh
       • 偏差处理机制
    3️⃣ 提交实时调整报价：
       • 调整类型：上调 / 下调 / 不调整
       • 如果需要调整，输入新功率和报价
       • 调整必须在市场开市前 5 分钟提交
    4️⃣ 跟踪多个市场周期（至少 4 个 15 分钟周期）
    5️⃣ 查看成交详情和偏差电费
    
    完成后请点击 ✅ 确认`
  );
  
  const realtimeMarket = await helper.assertElementVisible('[data-testid="realtime-market"]');
  expect(realtimeMarket).toBe(true);
  await helper.takeScreenshot('realtime-market-trading');
  
  // 中长期市场
  await helper.showPrompt(
    '📆 中长期电力交易',
    `进行中长期电力交易（月度、季度、年度）：
    
    1️⃣ 进入【中长期市场】页面
    2️⃣ 查看可交易的合约：
       • 月度合约：下月 01-31 日
       • 季度合约：Q2（4-6 月）、Q3（7-9 月）等
       • 年度合约：完整年度
    3️⃣ 发起交易：
       • 选择合约类型：月度合约
       • 输入交易信息：
         - 功率：25 MW（平均功率）
         - 期望价格：0.40 元/kWh
         - 合约周期：2026-04-01 至 2026-04-30
         - 是否可转让：是/否
    4️⃣ 查看订单状态（待成交/已成交/已关闭）
    5️⃣ 对于已成交的合约：
       • 查看成交价格
       • 查看对手方信息
       • 了解付款和交付安排
    
    完成后请点击 ✅ 确认`
  );
  
  await helper.takeScreenshot('medium-longterm-market');
  await helper.logStep('✅ 电力市场交易机制 - 完成');
});

/**
 * 步骤 2: 辅助服务市场参与
 * 测试内容：频率调节、电压支持、黑启动等服务交易
 */
test('Step 2: 辅助服务市场参与', async () => {
  await helper.logStep('【场景 2】辅助服务市场参与 - 开始');
  
  await helper.navigate('http://localhost:3000/energy/elec-trade/ancillary');
  await helper.waitForElement('.ancillary-services', 5000);
  
  // 频率调节服务
  await helper.showPrompt(
    '📶 频率调节服务 (FRR)',
    `参与频率调节服务竞拍：
    
    1️⃣ 进入【频率调节】模块
    2️⃣ 了解现行政策：
       • 服务类型：一级调频（一次）/ 二级调频（二次）
       • 报价方式：全电量报价 / 分段报价
       • 补偿机制：容量补偿 + 电量补偿
    3️⃣ 提交调频能力申报：
       • 调频方向：上调 + 下调（双向）
       • 调频容量：10 MW
       • 响应时间：< 5 分钟
       • 持续时间：≥ 30 分钟
       • 报价：
         - 容量价格（元/MW·天）：100
         - 调节电量价格（元/MWh）：80
    4️⃣ 跟踪报价状态和成交情况
    5️⃣ 验证调频命令的接收和执行
    
    完成后请点击 ✅ 确认`
  );
  
  const frequencyService = await helper.assertElementVisible('[data-testid="frequency-service"]');
  expect(frequencyService).toBe(true);
  await helper.takeScreenshot('frequency-regulation-service');
  
  // 电压支持服务
  await helper.showPrompt(
    '⚡ 电压支持服务 (VSS)',
    `参与电压支持服务：
    
    1️⃣ 进入【电压支持】模块
    2️⃣ 检查设备能力：
       • 设备类型：同步发电机 / 储能 / SVG / SVC
       • 最大无功容量：±30 MVar
       • 响应时间：≤ 1 秒
    3️⃣ 配置电压支持参数：
       • 支持范围：110% - 95% Un
       • 静有功无功特性（P-Q 曲线）
       • 动优先级：有功 vs 无功的优先级
    4️⃣ 提交竞拍报价：
       • 提供能力：30 MVar
       • 报价：15 元/MVar·月（容量补偿）
    5️⃣ 查看成交结果和实际执行情况
    
    完成后请点击 ✅ 确认`
  );
  
  await helper.takeScreenshot('voltage-support-service');
  
  // 黑启动服务
  await helper.showPrompt(
    '🔄 黑启动服务',
    `提供黑启动（恢复）服务：
    
    1️⃣ 进入【黑启动服务】模块
    2️⃣ 申报黑启动能力：
       • 黑启动电源类型：储能 BESS
       • 起动时间：≤ 10 分钟
       • 可持续时间：≥ 2 小时
       • 可支持的负荷：20 MW
    3️⃣ 配置黑启动过程：
       • 第一步：BESS 快速启动，建立电压和频率
       • 第二步：同期装置检查，准备并联
       • 第三步：依次接入负荷
    4️⃣ 报价竞拍：
       • 黑启动服务费：10,000 元/次
       • 待机费：2,000 元/天
    5️⃣ 定期演练（验证实际能力）
    
    完成后请点击 ✅ 确认`
  );
  
  await helper.takeScreenshot('black-start-service');
  await helper.logStep('✅ 辅助服务市场参与 - 完成');
});

/**
 * 步骤 3: 碳交易市场参与
 * 测试内容：碳配额、碳信用、碳中和交易
 */
test('Step 3: 碳交易市场参与', async () => {
  await helper.logStep('【场景 3】碳交易市场参与 - 开始');
  
  await helper.navigate('http://localhost:3000/energy/carbon-trade');
  await helper.waitForElement('.carbon-market-panel', 5000);
  
  // 碳配额管理
  await helper.showPrompt(
    '🌱 碳配额管理',
    `管理和交易碳配额：
    
    1️⃣ 进入【碳配额】页面
    2️⃣ 查看配额信息：
       • 当年度配额：50,000 吨 CO₂/年
       • 已使用配额：X 吨
       • 剩余配额：Y 吨
       • 配额有效期：2026-01-01 至 2026-12-31
    3️⃣ 碳排放核算：
       • 期初配额余额
       • + 购买配额
       • - 已用配额（煤炭供热、化石燃料发电）
       • = 期末结余
    4️⃣ 交易操作：
       • 若剩余配额充足：正常运营
       • 若配额可能不足：进入市场采购
         - 进入【碳交易所】
         - 查看碳配额市场价格（元/吨）
         - 下单采购所需配额
         - 确认交割
    5️⃣ 查看交易历史和成本统计
    
    完成后请点击 ✅ 确认`
  );
  
  const carbonQuota = await helper.assertElementVisible('[data-testid="carbon-quota"]');
  expect(carbonQuota).toBe(true);
  await helper.takeScreenshot('carbon-quota-management');
  
  // 碳信用生成与交易
  await helper.showPrompt(
    '♻️ 碳信用生成与交易',
    `通过清洁能源生成碳信用：
    
    1️⃣ 进入【碳信用】模块
    2️⃣ 碳信用生成：
       • 光伏发电产生碳减排：每 1 MWh 减少 0.5 吨 CO₂
       • 储能放电（相对于火电）：每 1 MWh 减少 0.3 吨 CO₂
       • 需求响应减少用电：每 1 MWh 减少 0.4 吨 CO₂
    3️⃣ 统计本期碳信用：
       • 统计周期：当月
       • 清洁发电量：X MWh
       • 生成碳信用：Y 吨 CO₂ 当量
       • 碳信用单价：Z 元/吨
    4️⃣ 碳信用交易：
       • 如果碳信用充足：可选出售
       • 点击【出售碳信用】
       • 输入出售量和期望价格
       • 在碳交易所上市
       • 成交后到账
    5️⃣ 综合计算净收益：
       • 清洁能源收益
       • + 碳信用销售收益
       • - 碳配额采购成本
    
    完成后请点击 ✅ 确认`
  );
  
  const carbonCredit = await helper.assertElementVisible('[data-testid="carbon-credit"]');
  expect(carbonCredit).toBe(true);
  await helper.takeScreenshot('carbon-credit-trading');
  
  // 碳中和认证
  await helper.showPrompt(
    '🌍 碳中和认证与报告',
    `申请碳中和认证并生成报告：
    
    1️⃣ 进入【碳中和认证】页面
    2️⃣ 组织碳中和数据：
       • 核算年份：2026
       • 组织边界：全部运营
       • 核算方法：ISO 14064-2
    3️⃣ 计算碳足迹：
       • 范围 1（直接排放）：0%（无化石燃料）
       • 范围 2（电力排放）：基于购电结构
       • 范围 3（间接排放）：运输、供应链等
       • 总碳足迹：X 吨 CO₂ 当量
    4️⃣ 碳中和方案：
       • 减排量：Y 吨（已有的清洁能源和节能）
       • 碳汇：Z 吨（购买或确认第三方碳汇）
       • 碳中和差距：max(0, X - Y - Z)
       • 若有差距，采购碳配额或碳信用进行中和
    5️⃣ 生成《碳中和认证报告》：
       • 认证单位：第三方认证机构
       • 认证等级：金牌 / 银牌 / 铜牌
       • 颁发证书
    6️⃣ 发布碳中和声明
    
    完成后请点击 ✅ 确认`
  );
  
  await helper.takeScreenshot('carbon-neutral-certification');
  await helper.logStep('✅ 碳交易市场参与 - 完成');
});

/**
 * 步骤 4: 能效管理与优化
 * 测试内容：设备能效、系统优化、节能监控
 */
test('Step 4: 能效管理与优化', async () => {
  await helper.logStep('【场景 4】能效管理与优化 - 开始');
  
  await helper.navigate('http://localhost:3000/energy/efficiency');
  await helper.waitForElement('.efficiency-dashboard', 5000);
  
  // 设备能效评级
  await helper.showPrompt(
    '⭐ 设备能效评级与诊断',
    `评估设备的能效等级：
    
    1️⃣ 进入【设备能效】模块
    2️⃣ 选择要评估的设备集（如所有充电桩）
    3️⃣ 查看关键能效指标：
       • 充电桩：能量转换效率 ≥ 95% ✓ / ✗
       • 储能系统：往返效率 ≥ 85% ✓ / ✗
       • 变压器：空载损耗比例 ✓ / ✗
       • 逆变器：加权平均效率 ✓ / ✗
    4️⃣ 查看能效评级：
       • 一级能效（最高）∼∼∼ 国际 / 国家先进水平
       • 二级能效 ∼∼ 国家水平
       • 三级能效 ∼ 国家平均
       • 四级能效 ↓ 能效达不到标准
    5️⃣ 能效诊断建议：
       • 为达不到标准的设备提出改进方案
       • 如：更换高效逆变器、安装冷却系统等
    6️⃣ 对比同类设备的能效水平
    
    完成后请点击 ✅ 确认`
  );
  
  const efficiencyRating = await helper.assertElementVisible('[data-testid="efficiency-rating"]');
  expect(efficiencyRating).toBe(true);
  await helper.takeScreenshot('device-efficiency-rating');
  
  // 系统优化建议
  await helper.showPrompt(
    '🎯 系统能效优化方案',
    `获取和应用系统优化建议：
    
    1️⃣ 进入【优化方案】页面
    2️⃣ 系统自动分析并提出优化方案，包括：
       • 快速赢：可立即实施、低成本高效益
         - 例：调整充电策略削峰填谷
         - 例：优化转换器工作点
       • 中期计划：需要部分投资、中期见效
         - 例：更换能效更高的设备
         - 例：增加储能容量
       • 长期规划：需要大额投资、长期效益
         - 例：升级成智能微网
    3️⃣ 对每个方案计算：
       • 投资额：X 万元
       • 年节能效果：Y 万元
       • 投资回收期：Z 年
       • 20 年净收益：W 万元
    4️⃣ 优选用户有兴趣的方案，深化研究
    5️⃣ 生成《能效改进计划书》
    
    完成后请点击 ✅ 确认`
  );
  
  await helper.takeScreenshot('system-optimization-plan');
  
  // 节能评比与激励
  await helper.showPrompt(
    '🏆 节能评比与激励',
    `参与节能评比获得激励：
    
    1️⃣ 进入【节能评比】模块
    2️⃣ 查看评比排行：
       • 按能效指标排名（能效率、人均能耗等）
       • 按节能进度排名（与上一期同期对比）
       • 按碳减排排名
    3️⃣ 你的排名和得分：
       • 排名：第 X 名 / 共 N 个同类机构
       • 节能指标排名百分位数
       • 获得评分和等级
    4️⃣ 激励机制：
       • 前 10% 的机构：额外奖励和公开表彰
       • 前 50% 的机构：继续参与，争取进一步进步
       • 后 50% 的机构：获得改进支持和技术指导
    5️⃣ 申请激励资金或政策支持（如有）
    
    完成后请点击 ✅ 确认`
  );
  
  await helper.takeScreenshot('energy-efficiency-ranking');
  await helper.logStep('✅ 能效管理与优化 - 完成');
});

/**
 * 步骤 5: 综合能源管理与收益分析
 * 测试内容：多种市场参与、收益多元化
 */
test('Step 5: 综合能源管理与收益分析', async () => {
  await helper.logStep('【场景 5】综合能源管理与收益分析 - 开始');
  
  await helper.navigate('http://localhost:3000/energy/services/analytics');
  await helper.waitForElement('.revenue-analytics', 5000);
  
  // 收益多元化分析
  await helper.showPrompt(
    '💼 收益多元化分析',
    `分析来自多个市场的收益：
    
    1️⃣ 进入【收益分析】模块
    2️⃣ 查看统计周期的各类收益：
       收益来源                      本期收益(万元)      占比
       ───────────────────────────────────────────
       • 主营电力销售              150,000          40%
       • 日前市场交易                50,000          13%
       • 实时市场调整                20,000           5%
       • 频率调节服务                30,000           8%
       • 电压支持服务                15,000           4%
       • 黑启动服务                  10,000           2.7%
       • 充电服务                    60,000          16%
       • 碳信用销售                   15,000           4%
       • 能效改进奖励                  5,000           1.3%
       ───────────────────────────────────────────
       合计                         355,000         100%
    3️⃣ 生成《收益多元化分析报告》
    4️⃣ 对比历史趋势：前期 vs 本期
    5️⃣ 推算未来增长潜力
    
    完成后请点击 ✅ 确认`
  );
  
  const revenueAnalytics = await helper.assertElementVisible('[data-testid="revenue-analytics"]');
  expect(revenueAnalytics).toBe(true);
  await helper.takeScreenshot('revenue-diversification-analysis');
  
  // 风险管理
  await helper.showPrompt(
    '⚠️ 市场风险与管理策略',
    `识别和管理能源市场风险：
    
    1️⃣ 进入【风险管理】模块
    2️⃣ 识别主要风险：
       • 市场价格风险：价格波动对收益的影响
       • 天气风险：PV 发电量不确定性
       • 容量风险：储能容量制约
       • 政策风险：碳交易政策变动
       • 技术风险：设备故障风险
    3️⃣ 对每类风险进行评估：
       • 发生概率（高/中/低）
       • 影响程度（万元）
       • 风险等级（×××/××/×）
    4️⃣ 制定风险管理策略：
       • 规避风险：停止高风险业务
       • 削减风险：多样化投资组合、购买保险
       • 转移风险：衍生品对冲、保险
       • 承受风险：将浮动风险纳入决策
    5️⃣ 建立监控和预警机制
    
    完成后请点击 ✅ 确认`
  );
  
  await helper.takeScreenshot('market-risk-management');
  
  // 商业模式创新
  await helper.showPrompt(
    '🚀 商业模式创新',
    `探索和验证创新的商业模式：
    
    1️⃣ 进入【创新模式】版块
    2️⃣ 支持的创新业务模式：
       • 电池租赁服务：向用户租赁电池，获取回报
       • 虚拟电厂订购：向第三方出租 VPP 容量
       • 绿电溯源与交易：生成和销售绿电证书
       • 需求响应聚合：聚合用户实现需求侧响应
       • 综合能源服务：一站式冷热电气供应
    3️⃣ 选择一个创新模式（如：绿电销售）
    4️⃣ 配置模式参数：
       • 绿电产品：风电、光伏、水电、储能等
       • 目标客户：企业用户、居民、政府机构
       • 定价策略：固定价格 / 动态调整 / 折扣
       • 服务承诺（SLA）：可用性、响应时间等
    5️⃣ 发布新产品和市场推广
    6️⃣ 跟踪业务成长和客户反馈
    
    完成后请点击 ✅ 确认`
  );
  
  await helper.takeScreenshot('innovative-business-models');
  await helper.logStep('✅ 综合能源管理与收益分析 - 完成');
});

/**
 * 步骤 6: 能源服务质量与客地体验
 * 测试内容：服务水平、客户满意度、长期可持续性
 */
test('Step 6: 能源服务质量与客户体验', async () => {
  await helper.logStep('【场景 6】能源服务质量与客户体验 - 开始');
  
  await helper.navigate('http://localhost:3000/energy/services/quality');
  await helper.waitForElement('.service-quality-dashboard', 5000);
  
  // 服务水平协议 (SLA) 监控
  await helper.showPrompt(
    '📊 服务水平 (SLA) 监控',
    `监控和评估服务水平承诺的履行情况：
    
    1️⃣ 进入【SLA 监控】页面
    2️⃣ 查看关键 SLA 指标：
       指标                        目标值      实现值      达成率
       ────────────────────────────────────────────────────
       • 系统可用性                99.9%       99.95%      ✓
       • 主动告警时间              < 2 分钟     1.5 分钟    ✓
       • 故障平均修复时间(MTTR)   < 30 分钟    15 分钟     ✓
       • 平均故障间隔(MTBF)        > 500 小时   1200 小时   ✓
       • 客户问题响应时间          < 1 小时     30 分钟     ✓
       • 充电充足率（PVESSC）      ≥ 95%       97.3%       ✓
       • 订单准时交付率            ≥ 98%       99.2%       ✓
    3️⃣ 生成 SLA 执行报告
    4️⃣ 对未达成目标的指标进行根本原因分析
    5️⃣ 制定改进计划
    
    完成后请点击 ✅ 确认`
  );
  
  const slaMonitoring = await helper.assertElementVisible('[data-testid="sla-monitoring"]');
  expect(slaMonitoring).toBe(true);
  await helper.takeScreenshot('sla-monitoring-dashboard');
  
  // 客户满意度调查
  await helper.showPrompt(
    '😊 客户满意度评估',
    `进行客户满意度调查和分析：
    
    1️⃣ 进入【客户满意度】模块
    2️⃣ 发起满意度调查：
       • 调查方式：邮件问卷 / 短信调查 / 网络投票
       • 调查对象：近期客户
       • 问卷内容：
         - 服务质量评分（1-5 星）
         - 价格合理性评分
         - 客户支持评分
         - 产品创新评分
         - 整体满意度评分
         - 推荐他人意愿度
         - 自由评论
    3️⃣ 收集反馈数据（至少 100 个样本）
    4️⃣ 分析满意度统计：
       • 平均评分
       • 满意度分布（很满意/满意/一般/不满意/很不满意）
       • NPS（Net Promoter Score）
       • 逐项分析
    5️⃣ 识别改进机会和客户声音
    6️⃣ 制定改进行动计划
    
    完成后请点击 ✅ 确认`
  );
  
  await helper.takeScreenshot('customer-satisfaction-survey');
  
  // 长期可持续性评估
  await helper.showPrompt(
    '🌱 长期可持续性评估',
    `评估业务的长期可持续性和增长潜力：
    
    1️⃣ 进入【可持续性评估】模块
    2️⃣ 财务可持续性：
       • 盈利能力：利润率 ≥ X%
       • 现金流：毛现金流 > 0，连续 N 个季度正
       • 债务管理：债务比率 < Y%
       • 增长率：收益年均增长 ≥ Z%
    3️⃣ 营运可持续性：
       • 设备寿命：已部署设备的加权平均技术寿命
       • 维护成本：计划性维护成本占收益的百分比
       • 技术引进：新技术采纳率
       • 人力资源：人员稳定性和成长空间
    4️⃣ 环境可持续性：
       • 碳排放强度：吨 CO₂/MWh（逐年递减）
       • 清洁能源比率：清洁能源 / 总用电（逐年递增）
       • 环保合规：通过所有环保审计 ✓
       • ESG 评分：社会责任、环境保护、公司治理综合评分
    5️⃣ 社会可持续性：
       • 就业创造：直接或间接创造的工作机会
       • 技能提升：培训和教育投入
       • 社区贡献：对当地经济和社会的贡献
       • 公共利益：实现的社会目标（减排、扶贫等）
    6️⃣ 生成《企业可持续发展报告》
    
    完成后请点击 ✅ 确认`
  );
  
  const sustainabilityReport = await helper.assertElementVisible('[data-testid="sustainability-report"]');
  expect(sustainabilityReport).toBe(true);
  await helper.takeScreenshot('sustainability-assessment');
  
  // 最终总结
  await helper.showPrompt(
    '📋 能源交易与商业服务 - 最终总结',
    `本场景的测试总结和建议：
    
    ✅ 已验证的内容：
    ▪ 电力市场参与（日前、实时、中长期）
    ▪ 辅助服务交易（调频、电压、黑启动）
    ▪ 碳市场参与（配额、信用、中和认证）
    ▪ 能效管理（评级、优化、激励）
    ▪ 收益多元化（7+ 收入来源）
    ▪ 服务质量（SLA、客户满意度、可持续性）
    
    🎯 关键指标总结：
    ▪ 参与市场数：7+ 个
    ▪ 月均收益增长：13-20%（来自多元化）
    ▪ 碳减排量：递增
    ▪ 客户满意度：≥ 4.2 星 / 5 星
    ▪ 能效评级：至少 2 级
    
    📌 建议：
    1. 继续扩大辅助服务参与比例（潜力：+30%）
    2. 深化碳市场参与（新增收入来源）
    3. 推进创新商业模式（长期增长动力）
    4. 持续改进设备能效（成本控制）
    
    感谢您的详细参与！
    完成后请点击 ✅ 确认`
  );
  
  await helper.logStep('✅ 能源交易与商业服务测试场景全部完成！');
});

// 测试完成
test.afterAll(async ({ browser }) => {
  console.log('✅ 能源交易与商业服务测试场景全部完成！');
  console.log('   - 3 个交易服务模块全面测试');
  console.log('   - 6 个详细测试步骤');
  console.log('   - 生成详尽测试报告');
  console.log('   - 涵盖财务、碳、能效、客户等多维度');
});
