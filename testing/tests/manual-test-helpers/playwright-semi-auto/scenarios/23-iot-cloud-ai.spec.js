/**
 * IoT 云端 AI 与智能调度测试场景 - 23
 * 
 * 覆盖模块：
 * ✅ JGSY.AGI.IotCloudAI - Dashboard（仪表板）
 * ✅ JGSY.AGI.IotCloudAI - Config（配置管理）
 * ✅ JGSY.AGI.IotCloudAI - AiCore（AI核心引擎）
 * ✅ JGSY.AGI.IotCloudAI - Model（模型管理）
 * ✅ JGSY.AGI.IotCloudAI - Training（训练任务）
 * ✅ JGSY.AGI.IotCloudAI - PeakValley（峰谷管理）
 * ✅ JGSY.AGI.IotCloudAI - DemandResponse（负荷响应）
 * ✅ JGSY.AGI.IotCloudAI - GridConnection（并网管理）
 * ✅ JGSY.AGI.IotCloudAI - CarbonTrading（碳交易）
 * ✅ JGSY.AGI.IotCloudAI - MarketTrading（市场交易）
 * ✅ JGSY.AGI.IotCloudAI - FaultWarning（故障告警）
 * ✅ JGSY.AGI.IotCloudAI - HealthMonitor（健康监测）
 * ✅ JGSY.AGI.IotCloudAI - VirtualPowerPlant（虚拟电厂）
 * ✅ JGSY.AGI.IotCloudAI - EdgeStatus（边缘状态）
 * 
 * 测试步骤：7 个核心场景
 * 总耗时：约 35 分钟
 * 难度：HIGH（涉及 AI 推理和复杂调度逻辑）
 */

const { test, expect } = require('@playwright/test');
const { SemiAutoHelper } = require('../helpers/semi-auto-helper');
const { TestData } = require('../helpers/test-data');

let helper;

test.beforeEach(async ({ page }) => {
  helper = new SemiAutoHelper(page);
  await helper.navigate('http://localhost:3000');
  await helper.login('admin@example.com', 'P@ssw0rd');
  await helper.logStep('✅ 登录成功 - 准备开始 IoT 云端 AI 测试');
});

test.afterEach(async ({ page }) => {
  await helper.generateReport('iot-cloud-ai');
});

// ========================================
// 场景 1: 仪表板与全局配置
// ========================================
test('Step 1: IoT AI 仪表板与平台配置', async ({ page }) => {
  await helper.logStep('【场景 1】仪表板与配置 - 开始');

  // 1.1 仪表板
  await helper.navigate('http://localhost:3000/iot-ai/dashboard');

  await helper.showPrompt(
    '📊 IoT AI 仪表板验证',
    `请验证以下内容：

    1️⃣ AI 系统概览（模型数量/推理次数/准确率/活跃设备数）
    2️⃣ 实时推理指标
    3️⃣ 预测 vs 实际对比图表
    4️⃣ 异常检测告警面板
    5️⃣ 系统资源使用（GPU/CPU/RAM）

    完成后请点击 ✅ 确认`
  );

  // 1.2 配置管理
  await helper.navigate('http://localhost:3000/iot-ai/config');

  await helper.showPrompt(
    '⚙️ 平台配置验证',
    `请验证以下配置项：

    1️⃣ AI 推理引擎配置
    2️⃣ 数据处理管道配置
    3️⃣ 边缘计算节点配置
    4️⃣ 通信协议桥接配置
    5️⃣ 告警阈值配置

    完成后请点击 ✅ 确认`
  );

  await helper.takeScreenshot('23-01-dashboard-config');
  await helper.logStep('✅ 仪表板与配置验证完成');
});

// ========================================
// 场景 2: AI 模型管理与训练
// ========================================
test('Step 2: AI 模型管理与训练任务', async ({ page }) => {
  await helper.logStep('【场景 2】AI 模型与训练 - 开始');

  // 2.1 模型管理
  await helper.navigate('http://localhost:3000/iot-ai/models');

  await helper.showPrompt(
    '🧠 AI 模型管理验证',
    `请验证以下功能：

    1️⃣ 模型列表（名称/类型/版本/状态/精度/最后训练时间）
    2️⃣ 创建新模型（类型：预测/分类/异常检测/推荐）
    3️⃣ 模型版本管理（v1/v2/...）
    4️⃣ 模型详情（架构/参数/训练历史/性能指标）
    5️⃣ 模型上线/下线
    6️⃣ 模型删除
    7️⃣ 模型对比（两个模型/版本间的性能对比）

    完成后请点击 ✅ 确认`
  );

  // 2.2 训练任务
  await helper.navigate('http://localhost:3000/iot-ai/training');

  await helper.showPrompt(
    '🏋️ 训练任务验证',
    `请验证以下功能：

    1️⃣ 训练任务列表（模型/数据集/状态/进度/用时/GPU使用）
    2️⃣ 创建训练任务（选择模型+数据集+超参数+硬件配额）
    3️⃣ 启动/暂停/终止训练
    4️⃣ 训练进度实时监控（Loss曲线/精度曲线）
    5️⃣ 训练日志查看
    6️⃣ 训练结果保存为新模型版本

    完成后请点击 ✅ 确认`
  );

  await helper.takeScreenshot('23-02-model-training');
  await helper.logStep('✅ 模型管理与训练验证完成');
});

// ========================================
// 场景 3: AI 核心引擎推理
// ========================================
test('Step 3: AI 核心推理引擎与预测', async ({ page }) => {
  await helper.logStep('【场景 3】AI 核心推理 - 开始');

  await helper.navigate('http://localhost:3000/iot-ai/ai-core');

  await helper.showPrompt(
    '🤖 AI 推理引擎验证',
    `请验证以下功能：

    1️⃣ 实时推理接口测试（输入数据 → 获取预测结果）
    2️⃣ 负荷预测（输入历史数据 → 预测未来负荷曲线）
    3️⃣ 发电量预测（光伏/风电基于气象数据预测）
    4️⃣ 故障预测（设备运行数据 → 故障概率/预警期限）
    5️⃣ 优化调度建议（基于预测结果生成调度方案）
    6️⃣ 推理性能指标（延迟/吞吐量/模型切换）

    ⚠️ 业务逻辑重点：
    - 预测结果的合理性（不能出现负数功率、超范围值）
    - 模型热切换不影响服务可用性
    - 异常输入的容错处理

    完成后请点击 ✅ 确认`
  );

  await helper.takeScreenshot('23-03-ai-inference');
  await helper.logStep('✅ AI 推理引擎验证完成');
});

// ========================================
// 场景 4: 峰谷管理与电力市场
// ========================================
test('Step 4: 峰谷策略与电力市场交易', async ({ page }) => {
  await helper.logStep('【场景 4】峰谷与市场 - 开始');

  // 4.1 峰谷管理
  await helper.navigate('http://localhost:3000/iot-ai/peak-valley');

  await helper.showPrompt(
    '📈 峰谷管理验证',
    `请验证以下功能：

    1️⃣ 峰谷时段配置（尖峰/高峰/平段/低谷/深谷）
    2️⃣ 峰谷电价策略（按时段/按季节）
    3️⃣ 储能充放电策略（谷充峰放）
    4️⃣ 实时峰谷状态展示
    5️⃣ 峰谷套利收益分析

    完成后请点击 ✅ 确认`
  );

  // 4.2 市场交易
  await helper.navigate('http://localhost:3000/iot-ai/market-trading');

  await helper.showPrompt(
    '💹 电力市场交易验证',
    `请验证以下功能：

    1️⃣ 市场行情展示（实时价格/历史走势）
    2️⃣ 交易委托（报量报价/发起竞价）
    3️⃣ 交易撮合结果
    4️⃣ 持仓/结算查看
    5️⃣ 交易策略配置

    完成后请点击 ✅ 确认`
  );

  // 4.3 碳交易
  await helper.navigate('http://localhost:3000/iot-ai/carbon-trading');

  await helper.showPrompt(
    '🌿 碳交易模块验证',
    `请验证以下功能：

    1️⃣ 碳资产概览（碳配额/CCER/碳排放）
    2️⃣ 碳交易下单（买入/卖出碳配额）
    3️⃣ 碳核算（排放因子/活动水平/排放量计算）
    4️⃣ 减排认证

    完成后请点击 ✅ 确认`
  );

  await helper.takeScreenshot('23-04-peak-market-carbon');
  await helper.logStep('✅ 峰谷与市场交易验证完成');
});

// ========================================
// 场景 5: 需求响应与并网管理
// ========================================
test('Step 5: 需求响应与并网控制', async ({ page }) => {
  await helper.logStep('【场景 5】需求响应与并网 - 开始');

  // 5.1 需求响应
  await helper.navigate('http://localhost:3000/iot-ai/demand-response');

  await helper.showPrompt(
    '📉 需求响应验证',
    `请验证以下功能：

    1️⃣ 需求响应事件列表（发布/进行中/结束）
    2️⃣ 参与响应（确认参与/报告削减量）
    3️⃣ 负荷调控策略（分级降负荷方案）
    4️⃣ 响应效果评估（削减量/基线对比）
    5️⃣ 补贴结算

    完成后请点击 ✅ 确认`
  );

  // 5.2 并网管理
  await helper.navigate('http://localhost:3000/iot-ai/grid-connection');

  await helper.showPrompt(
    '⚡ 并网管理验证',
    `请验证以下功能：

    1️⃣ 并网状态监控（频率/电压/功率因数/谐波）
    2️⃣ 并网保护参数配置
    3️⃣ 离网/并网切换控制
    4️⃣ 电能质量分析
    5️⃣ 功率调节（有功/无功调整）

    ⚠️ 安全重点：
    - 保护定值不能随意修改
    - 切换操作需要二次确认

    完成后请点击 ✅ 确认`
  );

  await helper.takeScreenshot('23-05-demand-grid');
  await helper.logStep('✅ 需求响应与并网验证完成');
});

// ========================================
// 场景 6: 故障告警与健康监测
// ========================================
test('Step 6: 故障预警与设备健康监测', async ({ page }) => {
  await helper.logStep('【场景 6】故障与健康 - 开始');

  // 6.1 故障告警
  await helper.navigate('http://localhost:3000/iot-ai/fault-warning');

  await helper.showPrompt(
    '⚠️ 故障告警验证',
    `请验证以下功能：

    1️⃣ 告警列表（级别/设备/类型/时间/状态）
    2️⃣ 告警详情与根因分析
    3️⃣ 告警确认/处理
    4️⃣ 告警规则配置（阈值/条件/通知方式）
    5️⃣ 告警统计与趋势
    6️⃣ AI 辅助故障诊断

    完成后请点击 ✅ 确认`
  );

  // 6.2 健康监测
  await helper.navigate('http://localhost:3000/iot-ai/health-monitor');

  await helper.showPrompt(
    '💚 设备健康监测验证',
    `请验证以下功能：

    1️⃣ 设备健康评分看板（红/黄/绿分布）
    2️⃣ 单设备健康详情（温度/振动/绝缘/老化指标）
    3️⃣ 预防性维护建议
    4️⃣ 健康趋势预测
    5️⃣ 设备寿命估算

    完成后请点击 ✅ 确认`
  );

  await helper.takeScreenshot('23-06-fault-health');
  await helper.logStep('✅ 故障告警与健康监测验证完成');
});

// ========================================
// 场景 7: 虚拟电厂与边缘计算
// ========================================
test('Step 7: VPP虚拟电厂与边缘状态', async ({ page }) => {
  await helper.logStep('【场景 7】VPP与边缘 - 开始');

  // 7.1 虚拟电厂
  await helper.navigate('http://localhost:3000/iot-ai/vpp');

  await helper.showPrompt(
    '🏭 虚拟电厂验证',
    `请验证以下功能：

    1️⃣ VPP 概览（聚合容量/在线资源/调度能力）
    2️⃣ 分布式资源列表（光伏/储能/充电桩/空调等可调节资源）
    3️⃣ 聚合调度策略配置
    4️⃣ 调度指令下发
    5️⃣ 调度效果跟踪
    6️⃣ VPP 收益分析

    完成后请点击 ✅ 确认`
  );

  // 7.2 边缘计算状态
  await helper.navigate('http://localhost:3000/iot-ai/edge-status');

  await helper.showPrompt(
    '📡 边缘节点状态验证',
    `请验证以下功能：

    1️⃣ 边缘节点列表（名称/位置/状态/负载/版本）
    2️⃣ 节点详细信息（CPU/内存/网络/运行时间）
    3️⃣ 边缘模型部署状态
    4️⃣ 边云协同数据同步状态
    5️⃣ 节点远程管理（重启/升级/配置下发）

    完成后请点击 ✅ 确认`
  );

  await helper.takeScreenshot('23-07-vpp-edge');
  await helper.logStep('✅ VPP与边缘计算验证完成');
});
