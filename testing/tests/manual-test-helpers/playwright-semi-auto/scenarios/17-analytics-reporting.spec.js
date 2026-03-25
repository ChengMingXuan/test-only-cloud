/**
 * 数据分析与报表测试场景 - 17
 * 
 * 覆盖模块：
 * ✅ JGSY.AGI.Analytics - Dashboard（仪表板概览）
 * ✅ JGSY.AGI.Analytics - UserProfile（用户画像）
 * ✅ JGSY.AGI.Analytics - Tracking（行为追踪/事件跟踪）
 * ✅ JGSY.AGI.Analytics - RevenueAnalytics（收入分析）
 * ✅ JGSY.AGI.Analytics - ReportCenter（报表中心）
 * ✅ JGSY.AGI.Analytics - ReportManage（报表管理）
 * ✅ JGSY.AGI.Analytics - ChargingAnalytics（充电分析）
 * ✅ JGSY.AGI.Analytics - DeviceAnalytics（设备分析）
 * ✅ JGSY.AGI.Analytics - OperationsAnalytics（运营分析）
 * ✅ JGSY.AGI.Analytics - DrillDown（数据下钻）
 * ✅ JGSY.AGI.Analytics - FunnelAnalysis（漏斗分析）
 * ✅ JGSY.AGI.Analytics - PathAnalysis（路径分析）
 * ✅ JGSY.AGI.Analytics - AnomalyDetection（异常检测）
 * ✅ JGSY.AGI.Analytics - RealtimeStream/Behavior（实时流/行为）
 * ✅ JGSY.AGI.Analytics - IntelligentReport（智能报表）
 * ✅ JGSY.AGI.Analytics - NaturalLanguageQuery（自然语言查询）
 * ✅ JGSY.AGI.Analytics - RecommendConfig（推荐策略）
 * ✅ JGSY.AGI.Analytics - DailyReport（日报管理）
 * ✅ JGSY.AGI.Analytics - OperationalReport（运营报告）
 * 
 * 测试步骤：8 个核心场景
 * 总耗时：约 40 分钟
 * 难度：MEDIUM-HIGH（涉及复杂图表和数据交互）
 */

const { test, expect } = require('@playwright/test');
const { SemiAutoHelper } = require('../helpers/semi-auto-helper');
const { TestData } = require('../helpers/test-data');

let helper;

test.beforeEach(async ({ page }) => {
  helper = new SemiAutoHelper(page);
  await helper.navigate('http://localhost:3000');
  await helper.login('admin@example.com', 'P@ssw0rd');
  await helper.logStep('✅ 登录成功 - 准备开始数据分析与报表测试');
});

test.afterEach(async ({ page }) => {
  await helper.generateReport('analytics-reporting');
});

// ========================================
// 场景 1: 仪表板与概览数据
// ========================================
test('Step 1: 仪表板概览与实时数据', async ({ page }) => {
  await helper.logStep('【场景 1】仪表板概览与实时数据 - 开始');

  // 1.1 导航到分析仪表板
  await helper.navigate('http://localhost:3000/analytics/dashboard');
  await helper.waitForElement('.page-header, .dashboard-container', 5000);
  await helper.highlightElement('.dashboard-container, .page-header');

  await helper.showPrompt(
    '📊 仪表板验证',
    `请检查以下内容：
    
    1️⃣ 概览数据卡片是否正常加载（总用户数/总订单/总充电量/总收入）
    2️⃣ 实时数据流是否正常更新
    3️⃣ 趋势图表是否渲染正确（折线图/柱状图）
    4️⃣ 告警信息是否展示
    5️⃣ 待办任务列表是否加载
    6️⃣ 服务健康状态指示灯是否正常
    
    完成后请点击 ✅ 确认`
  );

  // 1.2 测试数据刷新
  await helper.showPrompt(
    '🔄 实时数据刷新测试',
    `请测试以下操作：

    1️⃣ 点击【刷新】按钮，确认数据更新
    2️⃣ 切换时间范围（今天/本周/本月/本年）
    3️⃣ 确认各时间范围数据一致性
    4️⃣ 验证最近活动列表是否按时间排序

    完成后请点击 ✅ 确认`
  );

  await helper.takeScreenshot('17-01-dashboard-overview');
  await helper.logStep('✅ 仪表板概览验证完成');
});

// ========================================
// 场景 2: 收入分析与充电分析
// ========================================
test('Step 2: 收入分析与充电数据分析', async ({ page }) => {
  await helper.logStep('【场景 2】收入分析与充电数据分析 - 开始');

  // 2.1 收入分析
  await helper.navigate('http://localhost:3000/analytics/revenue');
  await helper.waitForElement('.page-header', 5000);

  await helper.showPrompt(
    '💰 收入分析验证',
    `请验证以下内容：

    1️⃣ 收入概览数据（总收入/月收入/日均收入）是否正确加载
    2️⃣ 收入趋势图表是否可切换（日/周/月/年）
    3️⃣ 站点收入排名是否按金额降序
    4️⃣ 收入构成分析（充电收入/服务费/停车费等）饼图展示
    5️⃣ 成本构成分析展示
    6️⃣ 尝试【导出】收入报表（Excel/PDF）

    完成后请点击 ✅ 确认`
  );

  // 2.2 充电数据分析
  await helper.navigate('http://localhost:3000/analytics/charging');

  await helper.showPrompt(
    '🔌 充电数据分析验证',
    `请验证以下内容：

    1️⃣ 充电概览（总充电量/总订单/平均时长/平均功率）
    2️⃣ 充电趋势图表（日/周/月切换）
    3️⃣ 小时分布热力图（按24小时展示充电量分布）
    4️⃣ 站点充电排名
    5️⃣ 用户类型分布（个人/企业/访客等）
    6️⃣ 尝试【导出】充电分析报表

    完成后请点击 ✅ 确认`
  );

  await helper.takeScreenshot('17-02-revenue-charging-analytics');
  await helper.logStep('✅ 收入分析与充电分析验证完成');
});

// ========================================
// 场景 3: 设备分析与运营分析
// ========================================
test('Step 3: 设备分析与运营KPI', async ({ page }) => {
  await helper.logStep('【场景 3】设备分析与运营KPI - 开始');

  // 3.1 设备分析
  await helper.navigate('http://localhost:3000/analytics/device');

  await helper.showPrompt(
    '🔧 设备分析验证',
    `请验证以下内容：

    1️⃣ 设备概览数据（在线率/故障率/平均利用率/健康评分）
    2️⃣ 故障趋势图表是否正常
    3️⃣ 故障类型分布（饼图/环形图）
    4️⃣ 设备利用率排名
    5️⃣ 健康评分分布
    6️⃣ 尝试【导出】设备分析报表

    完成后请点击 ✅ 确认`
  );

  // 3.2 运营分析
  await helper.navigate('http://localhost:3000/analytics/operations');

  await helper.showPrompt(
    '📈 运营KPI 验证',
    `请验证以下内容：

    1️⃣ 运营KPI指标卡（营收/订单/客单价/活跃用户）
    2️⃣ 同比/环比对比数据
    3️⃣ 运营报表列表（生成/查看/下载/删除）
    4️⃣ 尝试【生成报表】功能
    5️⃣ 尝试【下载报表】功能

    完成后请点击 ✅ 确认`
  );

  await helper.takeScreenshot('17-03-device-operations-analytics');
  await helper.logStep('✅ 设备分析与运营KPI验证完成');
});

// ========================================
// 场景 4: 报表中心与报表管理
// ========================================
test('Step 4: 报表中心与定时报表', async ({ page }) => {
  await helper.logStep('【场景 4】报表中心与定时报表 - 开始');

  // 4.1 报表中心
  await helper.navigate('http://localhost:3000/analytics/report-center');

  await helper.showPrompt(
    '📋 报表中心验证',
    `请验证以下功能：

    1️⃣ 统计总览（充电统计/用户统计/站点排名/充电类型分布）
    2️⃣ 趋势数据图表展示
    3️⃣ 报表列表查看
    4️⃣ 尝试【生成报表】：选择类型/时间范围/指标/格式
    5️⃣ 定时任务管理：查看/创建/启停/删除定时报表任务
    6️⃣ 已有报表的查看/下载/删除

    完成后请点击 ✅ 确认`
  );

  // 4.2 报表管理
  await helper.navigate('http://localhost:3000/analytics/report-manage');

  await helper.showPrompt(
    '🗂️ 报表管理验证',
    `请验证以下功能：

    1️⃣ 报表列表展示（名称/类型/创建时间/状态）
    2️⃣ 创建新报表（填写模板/参数/调度规则）
    3️⃣ 执行报表运行
    4️⃣ 导出报表结果
    5️⃣ 编辑报表配置
    6️⃣ 删除报表

    完成后请点击 ✅ 确认`
  );

  // 4.3 日报管理
  await helper.navigate('http://localhost:3000/analytics/daily-report');

  await helper.showPrompt(
    '📰 日报管理验证',
    `请验证 CRUD 操作：

    1️⃣ 查看日报列表（分页/排序）
    2️⃣ 创建新日报
    3️⃣ 编辑日报内容
    4️⃣ 删除日报
    5️⃣ 查看日报详情

    完成后请点击 ✅ 确认`
  );

  await helper.takeScreenshot('17-04-report-center');
  await helper.logStep('✅ 报表中心与定时报表验证完成');
});

// ========================================
// 场景 5: 用户画像与行为追踪
// ========================================
test('Step 5: 用户画像与行为事件追踪', async ({ page }) => {
  await helper.logStep('【场景 5】用户画像与行为追踪 - 开始');

  // 5.1 用户画像
  await helper.navigate('http://localhost:3000/analytics/user-profiles');

  await helper.showPrompt(
    '👤 用户画像验证',
    `请验证以下功能：

    1️⃣ 用户画像列表（分页/搜索/筛选）
    2️⃣ 查看单个用户画像详情（行为标签/偏好/活跃度）
    3️⃣ 用户统计（来源/分群/活跃度分布）
    4️⃣ 创建新用户画像
    5️⃣ 编辑用户画像
    6️⃣ 删除用户画像
    7️⃣ 用户群组/队列分析

    完成后请点击 ✅ 确认`
  );

  // 5.2 事件追踪
  await helper.navigate('http://localhost:3000/analytics/tracking');

  await helper.showPrompt(
    '🎯 行为事件追踪验证',
    `请验证以下功能：

    1️⃣ 事件列表查看（事件名/次数/用户数）
    2️⃣ 事件定义管理（创建/编辑/删除事件定义）
    3️⃣ 事件统计全览
    4️⃣ 会话分析列表
    5️⃣ 批量上报事件测试
    6️⃣ 获取埋点代码

    完成后请点击 ✅ 确认`
  );

  await helper.takeScreenshot('17-05-user-tracking');
  await helper.logStep('✅ 用户画像与行为追踪验证完成');
});

// ========================================
// 场景 6: 高级分析（漏斗/路径/下钻）
// ========================================
test('Step 6: 漏斗分析/路径分析/数据下钻', async ({ page }) => {
  await helper.logStep('【场景 6】高级分析功能 - 开始');

  // 6.1 漏斗分析
  await helper.navigate('http://localhost:3000/analytics/funnel');

  await helper.showPrompt(
    '🔽 漏斗分析验证',
    `请验证以下功能：

    1️⃣ 漏斗列表展示
    2️⃣ 创建新漏斗（定义步骤、事件、条件）
    3️⃣ 运行漏斗分析
    4️⃣ 查看转化率数据和漏斗图
    5️⃣ 编辑漏斗配置
    6️⃣ 启停/删除漏斗

    完成后请点击 ✅ 确认`
  );

  // 6.2 路径分析
  await helper.navigate('http://localhost:3000/analytics/path');

  await helper.showPrompt(
    '🗺️ 路径分析验证',
    `请验证以下功能：

    1️⃣ 用户行为路径可视化（桑基图/流程图）
    2️⃣ Top N 路径展示
    3️⃣ 页面流转分析
    4️⃣ 路径筛选条件设置

    完成后请点击 ✅ 确认`
  );

  // 6.3 数据下钻
  await helper.navigate('http://localhost:3000/analytics/drilldown');

  await helper.showPrompt(
    '🔍 数据下钻验证',
    `请验证以下多级下钻流程：

    1️⃣ 区域级别 → 点击某区域 → 进入站点级别
    2️⃣ 站点级别 → 点击某站点 → 进入设备级别
    3️⃣ 设备级别 → 点击某设备 → 进入订单级别
    4️⃣ 趋势对比：收入/能耗/订单/故障趋势
    5️⃣ 站点间对比分析
    6️⃣ 区域列表展示

    完成后请点击 ✅ 确认`
  );

  await helper.takeScreenshot('17-06-advanced-analytics');
  await helper.logStep('✅ 高级分析功能验证完成');
});

// ========================================
// 场景 7: 实时数据流与异常检测
// ========================================
test('Step 7: 实时行为流与AI异常检测', async ({ page }) => {
  await helper.logStep('【场景 7】实时行为流与AI异常检测 - 开始');

  // 7.1 实时行为
  await helper.navigate('http://localhost:3000/analytics/realtime');

  await helper.showPrompt(
    '⚡ 实时行为分析验证',
    `请验证以下功能：

    1️⃣ 实时事件流（实时刷新/时间轴展示）
    2️⃣ 活跃会话数量
    3️⃣ 页面热力分析
    4️⃣ 用户行为轨迹
    5️⃣ 实时概览数据（在线用户/活跃设备/实时订单）

    完成后请点击 ✅ 确认`
  );

  // 7.2 异常检测
  await helper.navigate('http://localhost:3000/analytics/anomaly');

  await helper.showPrompt(
    '🚨 AI 异常检测验证',
    `请验证以下功能：

    1️⃣ 异常检测统计概览
    2️⃣ 触发收入异常检测
    3️⃣ 触发订单异常检测
    4️⃣ 实时异常检测
    5️⃣ 异常记录列表和详情
    6️⃣ 异常告警规则配置

    完成后请点击 ✅ 确认`
  );

  await helper.takeScreenshot('17-07-realtime-anomaly');
  await helper.logStep('✅ 实时行为流与AI异常检测验证完成');
});

// ========================================
// 场景 8: 智能报表与自然语言查询
// ========================================
test('Step 8: 智能报表生成与自然语言查询', async ({ page }) => {
  await helper.logStep('【场景 8】智能报表与自然语言查询 - 开始');

  // 8.1 推荐策略配置
  await helper.navigate('http://localhost:3000/analytics/recommend');

  await helper.showPrompt(
    '🎯 推荐策略配置验证',
    `请验证以下功能：

    1️⃣ 推荐策略列表展示
    2️⃣ 创建新策略（名称/类型/条件/优先级）
    3️⃣ 编辑策略
    4️⃣ 启停策略
    5️⃣ 删除策略
    6️⃣ 推荐类型列表

    完成后请点击 ✅ 确认`
  );

  // 8.2 智能报表
  await helper.navigate('http://localhost:3000/analytics/intelligent-report');

  await helper.showPrompt(
    '🤖 智能报表验证',
    `请验证以下功能：

    1️⃣ 查看可用报表模板列表
    2️⃣ 选择模板生成智能报表
    3️⃣ 验证报表内容正确性
    4️⃣ 报表导出功能

    完成后请点击 ✅ 确认`
  );

  // 8.3 自然语言查询
  await helper.navigate('http://localhost:3000/analytics/nlq');

  await helper.showPrompt(
    '💬 自然语言查询验证',
    `请验证以下功能：

    1️⃣ 输入自然语言问题（如"本月充电总量是多少"）
    2️⃣ 查看AI解析结果和数据图表
    3️⃣ 查看查询历史记录
    4️⃣ 查看推荐问题列表
    5️⃣ 尝试多种问题类型（统计、对比、趋势等）

    完成后请点击 ✅ 确认`
  );

  await helper.takeScreenshot('17-08-intelligent-nlq');
  await helper.logStep('✅ 智能报表与自然语言查询验证完成');
});
