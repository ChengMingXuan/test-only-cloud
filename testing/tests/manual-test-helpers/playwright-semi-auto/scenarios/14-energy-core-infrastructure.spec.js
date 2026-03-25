/**
 * 能源核心基础设施测试场景 - 14
 * 
 * 覆盖模块：
 * ✅ JGSY.AGI.EnergyCore.MicroGrid       (微网管理系统)
 * ✅ JGSY.AGI.EnergyCore.Orchestrator    (能源调度器)
 * ✅ JGSY.AGI.EnergyCore.PVESSC          (光伏储能超级充电)
 * ✅ JGSY.AGI.EnergyCore.VPP             (虚拟电厂)
 * 
 * 测试步骤：6 个核心场景
 * 总耗时：约 35 分钟
 * 难度：HIGH（涉及复杂的能源交互逻辑）
 */

const { test, expect } = require('@playwright/test');
const { SemiAutoHelper } = require('../helpers/semi-auto-helper');
const { TestData } = require('../helpers/test-data');

let helper;

test.beforeEach(async ({ page }) => {
  helper = new SemiAutoHelper(page);
  await helper.navigate('http://localhost:3000');
  await helper.login('admin@example.com', 'P@ssw0rd');
  await helper.logStep('✅ 登录成功 - 准备开始能源核心基础设施测试');
});

test.afterEach(async ({ page }) => {
  await helper.generateReport('energy-core-infrastructure');
});

/**
 * 步骤 1: 微网配置与拓扑管理
 * 测试内容：创建微网、配置拓扑、验证设备接入
 */
test('Step 1: 微网配置与拓扑管理', async () => {
  await helper.logStep('【场景 1】微网配置与拓扑管理 - 开始');
  
  // 导航到微网管理
  await helper.navigate('http://localhost:3000/energy/microgrid');
  await helper.waitForElement('.page-header', 5000);
  await helper.highlightElement('.page-header');
  
  // 创建新微网
  await helper.showPrompt(
    '📋 微网配置向导',
    `请完成以下配置步骤：
    
    1️⃣ 点击【新建微网】按钮
    2️⃣ 输入微网名称：TEST_MICROGRID_${Date.now()}
    3️⃣ 选择微网类型：离岛型/并网型（任选）
    4️⃣ 配置额定容量：100 kW
    5️⃣ 设置地理位置（必需）
    
    完成后请点击 ✅ 确认`
  );
  
  // 验证微网创建
  await helper.waitForElement('[data-testid="microgrid-list"]', 5000);
  const microgridCount = await helper.countElements('[data-testid="microgrid-item"]');
  expect(microgridCount).toBeGreaterThan(0);
  await helper.takeScreenshot('microgrid-created');
  
  // 配置拓扑结构
  await helper.showPrompt(
    '🔗 微网拓扑配置',
    `现在配置微网的设备拓扑：
    
    1️⃣ 进入刚创建的微网
    2️⃣ 点击【拓扑管理】选项卡
    3️⃣ 添加以下设备：
       • PV（光伏）× 3 台
       • BESS（储能）× 2 台
       • Load（负荷）× 4 个
       • Grid（电网）× 1 个
    4️⃣ 配置设备间的连接关系
    
    完成后请点击 ✅ 确认`
  );
  
  await helper.waitFor(3000);
  await helper.takeScreenshot('microgrid-topology-configured');
  
  // 验证拓扑状态
  const topologyValid = await helper.assertElementVisible('.topology-canvas');
  expect(topologyValid).toBe(true);
  
  await helper.logStep('✅ 微网配置与拓扑管理 - 完成');
});

/**
 * 步骤 2: 能源调度策略配置
 * 测试内容：设置调度目标、优先级、约束条件
 */
test('Step 2: 能源调度策略配置', async () => {
  await helper.logStep('【场景 2】能源调度策略配置 - 开始');
  
  await helper.navigate('http://localhost:3000/energy/orchestrator');
  await helper.waitForElement('.orchestrator-panel', 5000);
  
  // 创建调度策略
  await helper.showPrompt(
    '⚙️ 调度策略配置向导',
    `配置能源调度策略：
    
    1️⃣ 点击【新建策略】
    2️⃣ 输入策略名称：DISPATCH_STRATEGY_${Date.now()}
    3️⃣ 设置调度目标：
       • 目标 1: 成本最小化（权重 40%）
       • 目标 2: 碳排放最小化（权重 30%）
       • 目标 3: 供应可靠性（权重 30%）
    4️⃣ 设置调度优先级：
       • 优先级 1: 关键负荷（医院、学校）
       • 优先级 2: 普通负荷
       • 优先级 3: 可延迟负荷
    5️⃣ 配置约束条件：
       • SOC 范围：20% - 90%
       • 功率变化率：≤ 20 kW/min
       • 涉及设备：选择前面创建的微网
    
    完成后请点击 ✅ 确认`
  );
  
  await helper.waitFor(2000);
  const policyExists = await helper.assertElementVisible('[data-testid="dispatch-strategy"]');
  expect(policyExists).toBe(true);
  await helper.takeScreenshot('dispatch-strategy-configured');
  
  // 配置时间计划
  await helper.showPrompt(
    '⏱️ 用电计划配置',
    `配置分时用电计划：
    
    1️⃣ 进入调度策略详情
    2️⃣ 点击【时间计划】标签页
    3️⃣ 添加 3 个时段：
       • 时段 1: 00:00 - 08:00（峰谷时段，优先充电）
       • 时段 2: 08:00 - 17:00（尖峰时段，优先放电）
       • 时段 3: 17:00 - 24:00（高峰时段，控制充放电）
    4️⃣ 为每个时段设置：
       • 目标负荷模式
       • 允许充放电功率范围
       • 价格信号
    
    完成后请点击 ✅ 确认`
  );
  
  await helper.takeScreenshot('time-schedule-configured');
  await helper.logStep('✅ 能源调度策略配置 - 完成');
});

/**
 * 步骤 3: 光伏储能超级充电系统测试
 * 测试内容：PVESSC 系统的工作流程
 */
test('Step 3: 光伏储能超级充电系统 (PVESSC)', async () => {
  await helper.logStep('【场景 3】PVESSC 系统测试 - 开始');
  
  await helper.navigate('http://localhost:3000/energy/pvessc');
  await helper.waitForElement('.pvessc-dashboard', 5000);
  
  // 实时监控
  await helper.showPrompt(
    '📊 PVESSC 即时监控',
    `查看 PVESSC 系统实时数据：
    
    1️⃣ 观察以下实时显示：
       • PV 发电功率（当前）
       • 储能 SOC 状态
       • 充电功率（如有车辆）
       • 并网功率
       • 系统温度和冷却状态
    
    2️⃣ 检查采样频率（应为 1-5 秒）
    3️⃣ 验证数据准确性和流畅性
    4️⃣ 截图保存当前状态
    
    完成后请点击 ✅ 确认`
  );
  
  await helper.takeScreenshot('pvessc-realtime-monitoring');
  
  // 充电管理
  await helper.showPrompt(
    '🔋 超级充电管理',
    `模拟电动车超级充电过程：
    
    1️⃣ 点击【模拟充电车】或【开始充电】
    2️⃣ 配置充电参数：
       • 车型：BYD Yuan Plus / Tesla Model 3（任选）
       • 目标 SOC：80%
       • 充电功率：350 kW（最大）
    3️⃣ 启动充电过程并观察：
       • 功率输出过程
       • SOC 变化曲线
       • 储能补偿机制
       • 热管理系统响应
    4️⃣ 验证充电完成判断逻辑
    5️⃣ 检查充电记录是否正确保存
    
    完成后请点击 ✅ 确认`
  );
  
  await helper.waitFor(3000);
  const chargingRecord = await helper.assertElementVisible('[data-testid="charging-record"]');
  expect(chargingRecord).toBe(true);
  await helper.takeScreenshot('pvessc-charging-process');
  
  // 能量管理
  await helper.showPrompt(
    '⚡ 能量聪慧管理',
    `测试 PVESSC 能量管理功能：
    
    1️⃣ 查看【能量管理】面板
    2️⃣ 验证以下流程：
       • PV 发电 → 优先供车充电
       • PV 不足 → 从储能放电
       • 储能满 → 反向并网
       • 夜间 + 谷电 → 储能充电
    3️⃣ 检查能量流向的优化：
       • 是否最大化利用 PV
       • 是否避免峰值放电
       • 是否实现削峰填谷
    4️⃣ 生成能量平衡报表
    
    完成后请点击 ✅ 确认`
  );
  
  await helper.takeScreenshot('pvessc-energy-management');
  await helper.logStep('✅ PVESSC 系统测试 - 完成');
});

/**
 * 步骤 4: 虚拟电厂 (VPP) 聚合与控制
 * 测试内容：多个微网的聚合、控制、报价
 */
test('Step 4: 虚拟电厂 (VPP) 聚合与控制', async () => {
  await helper.logStep('【场景 4】VPP 聚合与控制 - 开始');
  
  await helper.navigate('http://localhost:3000/energy/vpp');
  await helper.waitForElement('.vpp-aggregation', 5000);
  
  // VPP 组成与聚合
  await helper.showPrompt(
    '🌐 虚拟电厂聚合',
    `配置虚拟电厂聚合关系：
    
    1️⃣ 点击【新建 VPP】
    2️⃣ 选择聚合方式：
       • 按地理位置（同一地区的微网）
       • 按客户类型（工业/商业/住宅）
       • 按功能特性（储能/可调节向荷）
    3️⃣ 添加参与者（需至少 3 个微网）：
       • 选择要加入的微网
       • 配置各微网的参与度（0-100%）
       • 设置黑启动优先级
    4️⃣ 配置容量声明：
       • 总装机容量
       • 实时可用容量
       • 应急应变能力
    5️⃣ 设置通信协议：IEC 60870-5-104 / Modbus / MQTT
    
    完成后请点击 ✅ 确认`
  );
  
  const vppExists = await helper.assertElementVisible('[data-testid="vpp-item"]');
  expect(vppExists).toBe(true);
  await helper.takeScreenshot('vpp-aggregation');
  
  // 电力市场参与
  await helper.showPrompt(
    '📈 电力市场参与',
    `模拟 VPP 的电力市场参与：
    
    1️⃣ 进入 VPP 详情页面
    2️⃣ 点击【市场参与】选项卡
    3️⃣ 查看当前市场行情：
       • 日前市场价格曲线
       • 实时市场价格
       • 辅助服务价格
    4️⃣ 配置报价策略：
       • 有功功率报价：X 元/MW
       • 无功功率支持：X 元/MVar
       • 频率调节服务：X 元/MW·15min
    5️⃣ 提交报价并验证：
       • 报价是否成交
       • 成交价格和数量
       • 与预期的偏差
    6️⃣ 监控执行情况
    
    完成后请点击 ✅ 确认`
  );
  
  await helper.waitFor(2000);
  await helper.takeScreenshot('vpp-market-participation');
  
  // 调度命令执行
  await helper.showPrompt(
    '🎯 VPP 调度执行',
    `测试调度中心对 VPP 的实时控制：
    
    1️⃣ 进入 VPP 控制面板
    2️⃣ 模拟调度中心下达指令：
       • 充电指令：充至 80% SOC，功率 50 MW
       • 放电指令：放电 30 MW，持续 2 小时
       • 功率约束：功率变化率 ≤ 10 MW/min
    3️⃣ 观察各个聚合微网的响应：
       • 响应延迟（目标 < 5 秒）
       • 功率执行精度（±5%）
       • 各微网的协动状态
    4️⃣ 验证通信可靠性：
       • 指令是否都被正确接收
       • 是否有重复或丢失
       • 反馈信息是否及时
    5️⃣ 检查故障处理：
       • 部分微网离线时的处理
       • 超调时的限制
    
    完成后请点击 ✅ 确认`
  );
  
  await helper.takeScreenshot('vpp-dispatch-execution');
  await helper.logStep('✅ VPP 聚合与控制 - 完成');
});

/**
 * 步骤 5: 能源安全与稳定性分析
 * 测试内容：系统保护、黑启动、孤岛运行
 */
test('Step 5: 能源安全与稳定性分析', async () => {
  await helper.logStep('【场景 5】能源安全与稳定性 - 开始');
  
  await helper.navigate('http://localhost:3000/energy/core/security');
  await helper.waitForElement('.security-analysis-panel', 5000);
  
  // 频率电压监测
  await helper.showPrompt(
    '⚡ 频率与电压监测',
    `验证电网频率和电压的实时监测：
    
    1️⃣ 查看实时参数显示：
       • 电压：3 相电压、线电压、相位差
       • 频率：系统频率、频率变化率（df/dt）
       • 功率：有功、无功、视在功率
       • THD：电压谐波失真度
    2️⃣ 检查告警阈值：
       • 频率过高/过低告警
       • 电压越限告警
       • 负序分量告警
    3️⃣ 生成稳定性报表
    4️⃣ 截图保存当前状态
    
    完成后请点击 ✅ 确认`
  );
  
  await helper.takeScreenshot('frequency-voltage-monitoring');
  
  // 故障清除与黑启动
  await helper.showPrompt(
    '🔄 黑启动能力验证',
    `测试微网的黑启动（孤岛启动）能力：
    
    1️⃣ 模拟并网失败场景
    2️⃣ 进入【黑启动】管理
    3️⃣ 配置黑启动顺序：
       • 第一阶段：调度电源（储能 BESS）快速启动
       • 第二阶段：可控电源（柴发、电池）投入
       • 第三阶段：优先负荷接入
    4️⃣ 设置黑启动参数：
       • 最小频率：49.5 Hz
       • 最大频率：50.5 Hz
       • 稳压时间：30 秒
       • 容许频率变化：±0.5 Hz/s
    5️⃣ 模拟黑启动过程：
       • 监控频率恢复曲线
       • 检查电压上升过程
       • 验证负荷逐步接入
    
    完成后请点击 ✅ 确认`
  );
  
  const blackStartReady = await helper.assertElementVisible('[data-testid="black-start-capable"]');
  expect(blackStartReady).toBe(true);
  await helper.takeScreenshot('black-start-process');
  
  // 孤岛运行模式
  await helper.showPrompt(
    '🏝️ 孤岛运行模式',
    `验证孤岛（离岛）运行模式：
    
    1️⃣ 进入孤岛运行配置
    2️⃣ 启用孤岛检测：
       • 频率逸出检测
       • 电压逸出检测
       • THD 异常检测
    3️⃣ 配置孤岛运行参数：
       • 最小容量要求（与所接负荷比例）
       • 最大频率偏差：±2%
       • 最大电压偏差：±10%
    4️⃣ 验证孤岛模式转换：
       • 从并网→孤岛 的平滑切换
       • 从孤岛→并网 的平稳并入
       • 功率平衡的维持
    5️⃣ 检查孤岛运行时的负载优化：
       • 能否自动卸载不重要负荷
       • 能否维持最长孤岛时间
    
    完成后请点击 ✅ 确认`
  );
  
  await helper.takeScreenshot('islanding-mode-verification');
  await helper.logStep('✅ 能源安全与稳定性分析 - 完成');
});

/**
 * 步骤 6: 能源核心系统综合性能评估
 * 测试内容：性能指标、可靠性、成本效益分析
 */
test('Step 6: 能源核心系统综合性能评估', async () => {
  await helper.logStep('【场景 6】综合性能评估 - 开始');
  
  await helper.navigate('http://localhost:3000/energy/core/analytics');
  await helper.waitForElement('.analytics-dashboard', 5000);
  
  // 性能指标收集
  await helper.showPrompt(
    '📊 数据收集与分析',
    `进行能源系统性能评估：
    
    1️⃣ 进入【分析报表】模块
    2️⃣ 选择分析周期：
       • 最近 24 小时
       • 最近 7 天
       • 最近 30 天
       • 自定义日期范围
    3️⃣ 收集以下关键指标：
       ▪ 发电效率：PV 实际发电 / 理论最大值
       ▪ 储能效率：充放电能量比 > 85%
       ▪ VPP 参与度：实际参与 / 计划参与的比例
       ▪ 调度准确度：执行功率与指令的偏差 < 5%
       ▪ 可靠性指标：无故障运行时间占比
    4️⃣ 生成性能报表（包含图表和数字）
    
    完成后请点击 ✅ 确认`
  );
  
  await helper.waitFor(2000);
  const analyticsReport = await helper.assertElementVisible('[data-testid="analytics-report"]');
  expect(analyticsReport).toBe(true);
  await helper.takeScreenshot('energy-analytics-report');
  
  // 经济效益分析
  await helper.showPrompt(
    '💰 经济效益分析',
    `进行经济效益评估：
    
    1️⃣ 进入【经济分析】页面
    2️⃣ 查看以下数据：
       ▪ 收益来源：
         • 充电服务收益
         • 电力市场收益（日前市场成交）
         • 辅助服务收益（频率调节、电压支持）
         • 避免的峰值电费
       ▪ 成本构成：
         • 设备折旧
         • 运维成本
         • 并网费用
    3️⃣ 计算以下指标：
       ▪ 总收益（元）
       ▪ 总成本（元）
       ▪ 净收益（元）
       ▪ 投资回报率（%）
       ▪ 投资回收期（年）
    4️⃣ 对比不同运营策略的效益
    
    完成后请点击 ✅ 确认`
  );
  
  await helper.takeScreenshot('energy-economic-analysis');
  
  // 最终验证与报告生成
  await helper.showPrompt(
    '🎯 最终验证与报告',
    `完成综合评估并生成报告：
    
    1️⃣ 进入【综合评估】版块
    2️⃣ 验证系统整体状态：
       ▪ 所有子系统正常运行
       ▪ 通信链路完好
       ▪ 数据采集正常
       ▪ 控制命令执行良好
    3️⃣ 生成《能源核心系统评估报告》：
       • 执行摘要
       • 性能指标汇总表
       • 发现的问题和改进建议
       • 可靠性和安全性结论
    4️⃣ 导出报告为 PDF/Excel
    5️⃣ 分享报告（选择对象：管理员、运维人员）
    
    完成后请点击 ✅ 确认`
  );
  
  const reportGenerated = await helper.assertElementVisible('[data-testid="export-button"]');
  expect(reportGenerated).toBe(true);
  await helper.takeScreenshot('energy-core-final-report');
  
  await helper.logStep('✅ 综合性能评估 - 完成');
});

// 测试完成
test.afterAll(async ({ browser }) => {
  console.log('✅ 能源核心基础设施测试场景全部完成！');
  console.log('   - 4 个核心模块全面测试');
  console.log('   - 6 个详细测试步骤');
  console.log('   - 生成详尽测试报告');
});
