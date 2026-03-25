/**
 * 数据摄入与协议管理测试场景 - 22
 * 
 * 覆盖模块：
 * ✅ JGSY.AGI.Ingestion - DataSource（数据源管理）
 * ✅ JGSY.AGI.Ingestion - CollectionPoint（采集点管理）
 * ✅ JGSY.AGI.Ingestion - ProtocolManagement（协议管理）
 * ✅ JGSY.AGI.Ingestion - ProtocolDebug（协议调试）
 * ✅ JGSY.AGI.Ingestion - Ocpp20（OCPP 2.0 协议实现）
 * ✅ JGSY.AGI.Ingestion - IngestionTask（摄入任务管理）
 * ✅ JGSY.AGI.Ingestion - IngestionMonitor（摄入监控）
 * ✅ JGSY.AGI.Ingestion - IngestionMessage（摄入消息）
 * ✅ JGSY.AGI.Ingestion - HybridStorage（混合存储）
 * ✅ JGSY.AGI.Ingestion - BatchWriter（批量写入）
 * 
 * 测试步骤：6 个核心场景
 * 总耗时：约 30 分钟
 * 难度：HIGH（涉及协议交互和大数据量处理）
 */

const { test, expect } = require('@playwright/test');
const { SemiAutoHelper } = require('../helpers/semi-auto-helper');
const { TestData } = require('../helpers/test-data');

let helper;

test.beforeEach(async ({ page }) => {
  helper = new SemiAutoHelper(page);
  await helper.navigate('http://localhost:3000');
  await helper.login('admin@example.com', 'P@ssw0rd');
  await helper.logStep('✅ 登录成功 - 准备开始数据摄入与协议测试');
});

test.afterEach(async ({ page }) => {
  await helper.generateReport('data-ingestion');
});

// ========================================
// 场景 1: 数据源管理
// ========================================
test('Step 1: 数据源配置与管理', async ({ page }) => {
  await helper.logStep('【场景 1】数据源管理 - 开始');

  await helper.navigate('http://localhost:3000/ingestion/data-sources');

  await helper.showPrompt(
    '🔗 数据源管理验证',
    `请验证以下功能：

    1️⃣ 数据源列表（名称/协议类型/状态/连接数/最后活跃时间）
    2️⃣ 创建新数据源：
       - MQTT 数据源（Broker地址/端口/Topic/QoS）
       - HTTP/REST 数据源（URL/Method/Header/Auth）
       - MODBUS 数据源（地址/寄存器/采集周期）
       - OCPP 数据源（WebSocket URL/协议版本）
    3️⃣ 测试连接（验证连通性）
    4️⃣ 编辑数据源配置
    5️⃣ 启用/禁用数据源
    6️⃣ 删除数据源

    完成后请点击 ✅ 确认`
  );

  await helper.takeScreenshot('22-01-data-sources');
  await helper.logStep('✅ 数据源管理验证完成');
});

// ========================================
// 场景 2: 采集点管理
// ========================================
test('Step 2: 采集点配置与映射', async ({ page }) => {
  await helper.logStep('【场景 2】采集点管理 - 开始');

  await helper.navigate('http://localhost:3000/ingestion/collection-points');

  await helper.showPrompt(
    '📡 采集点管理验证',
    `请验证以下功能：

    1️⃣ 采集点列表（名称/设备/数据源/采集频率/状态）
    2️⃣ 创建采集点（绑定设备+数据源+数据映射规则）
    3️⃣ 数据映射配置：
       - 原始字段 → 标准字段映射
       - 数据类型转换
       - 单位换算规则
       - 计算公式配置
    4️⃣ 采集频率设置（1s/5s/30s/1m/5m/自定义）
    5️⃣ 数据质量规则（范围校验/突变检测/缺失补齐）
    6️⃣ 启用/禁用采集点
    7️⃣ 删除采集点

    完成后请点击 ✅ 确认`
  );

  await helper.takeScreenshot('22-02-collection-points');
  await helper.logStep('✅ 采集点管理验证完成');
});

// ========================================
// 场景 3: 协议管理与调试
// ========================================
test('Step 3: 协议管理与调试工具', async ({ page }) => {
  await helper.logStep('【场景 3】协议管理与调试 - 开始');

  // 3.1 协议管理
  await helper.navigate('http://localhost:3000/ingestion/protocols');

  await helper.showPrompt(
    '📋 协议管理验证',
    `请验证以下功能：

    1️⃣ 支持的协议列表（MQTT/OCPP/MODBUS/HTTP等）
    2️⃣ 协议版本管理
    3️⃣ 协议参数配置
    4️⃣ 协议适配器管理
    5️⃣ 自定义协议注册

    完成后请点击 ✅ 确认`
  );

  // 3.2 协议调试
  await helper.navigate('http://localhost:3000/ingestion/protocol-debug');

  await helper.showPrompt(
    '🔧 协议调试工具验证',
    `请验证以下功能：

    1️⃣ 选择协议类型 + 数据源
    2️⃣ 发送测试消息（手动构造报文）
    3️⃣ 接收消息监听（实时展示接收到的消息流）
    4️⃣ 消息解析预览（原始 → 解析后数据对比）
    5️⃣ 错误消息诊断
    6️⃣ 通信日志

    完成后请点击 ✅ 确认`
  );

  // 3.3 OCPP 2.0 协议
  await helper.showPrompt(
    '🔌 OCPP 2.0 协议验证',
    `请验证以下 OCPP 功能：

    1️⃣ OCPP WebSocket 连接状态
    2️⃣ BootNotification 消息处理
    3️⃣ StatusNotification 消息处理
    4️⃣ MeterValues 数据采集
    5️⃣ StartTransaction / StopTransaction
    6️⃣ RemoteStart / RemoteStop 远程控制

    完成后请点击 ✅ 确认`
  );

  await helper.takeScreenshot('22-03-protocol-debug');
  await helper.logStep('✅ 协议管理与调试验证完成');
});

// ========================================
// 场景 4: 摄入任务管理
// ========================================
test('Step 4: 数据摄入任务创建与调度', async ({ page }) => {
  await helper.logStep('【场景 4】摄入任务管理 - 开始');

  await helper.navigate('http://localhost:3000/ingestion/tasks');

  await helper.showPrompt(
    '📥 摄入任务管理验证',
    `请验证以下功能：

    1️⃣ 任务列表（名称/数据源/状态/运行时间/数据量）
    2️⃣ 创建新任务（选择数据源 → 配置采集规则 → 设置存储目标）
    3️⃣ 任务调度配置（立即/定时/周期/Cron表达式）
    4️⃣ 启动/暂停/停止任务
    5️⃣ 任务运行日志
    6️⃣ 任务重试机制（失败后自动重试配置）
    7️⃣ 删除任务

    ⚠️ 业务逻辑重点：
    - 同一数据源不能有重复任务
    - 暂停后恢复应从断点继续
    - 失败任务有告警通知

    完成后请点击 ✅ 确认`
  );

  await helper.takeScreenshot('22-04-ingestion-tasks');
  await helper.logStep('✅ 摄入任务管理验证完成');
});

// ========================================
// 场景 5: 摄入监控与消息
// ========================================
test('Step 5: 摄入监控面板与消息查询', async ({ page }) => {
  await helper.logStep('【场景 5】摄入监控 - 开始');

  // 5.1 摄入监控
  await helper.navigate('http://localhost:3000/ingestion/monitor');

  await helper.showPrompt(
    '📊 摄入监控面板验证',
    `请验证以下功能：

    1️⃣ 全局监控概览（总吞吐量/成功率/延迟/错误率）
    2️⃣ 实时数据流量图表
    3️⃣ 各数据源的吞吐量排名
    4️⃣ 异常/错误告警列表
    5️⃣ 延迟热力图
    6️⃣ 数据质量评分

    完成后请点击 ✅ 确认`
  );

  // 5.2 摄入消息查询
  await helper.navigate('http://localhost:3000/ingestion/messages');

  await helper.showPrompt(
    '💬 摄入消息查询验证',
    `请验证以下功能：

    1️⃣ 消息列表（时间/来源/类型/内容/状态）
    2️⃣ 消息详情查看（原始报文/解析后数据）
    3️⃣ 按条件筛选（时间范围/数据源/消息类型/状态）
    4️⃣ 消息重发
    5️⃣ 导出消息日志

    完成后请点击 ✅ 确认`
  );

  await helper.takeScreenshot('22-05-ingestion-monitor');
  await helper.logStep('✅ 摄入监控验证完成');
});

// ========================================
// 场景 6: 存储管理与批量写入
// ========================================
test('Step 6: 混合存储与批量写入配置', async ({ page }) => {
  await helper.logStep('【场景 6】存储与批量写入 - 开始');

  // 6.1 混合存储配置
  await helper.navigate('http://localhost:3000/ingestion/storage');

  await helper.showPrompt(
    '💾 混合存储配置验证',
    `请验证以下功能：

    1️⃣ 存储策略列表（热/温/冷数据分层）
    2️⃣ 配置热数据存储（实时查询高性能）
    3️⃣ 配置温数据存储（近期查询中等性能）
    4️⃣ 配置冷数据存储（归档低成本）
    5️⃣ 数据生命周期规则（自动降级/删除/归档）
    6️⃣ 存储容量监控

    完成后请点击 ✅ 确认`
  );

  // 6.2 批量写入
  await helper.navigate('http://localhost:3000/ingestion/batch-writer');

  await helper.showPrompt(
    '📦 批量写入配置验证',
    `请验证以下功能：

    1️⃣ 批量写入配置（批次大小/刷新间隔/并发度）
    2️⃣ 写入性能监控（TPS/延迟/失败率）
    3️⃣ 写入失败重试策略
    4️⃣ 死信队列管理（无法写入的消息）

    完成后请点击 ✅ 确认`
  );

  await helper.takeScreenshot('22-06-storage-batch');
  await helper.logStep('✅ 存储与批量写入验证完成');
});
