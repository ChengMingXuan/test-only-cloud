/**
 * 存储服务与模拟器测试场景 - 25
 * 
 * 覆盖模块：
 * ✅ JGSY.AGI.Storage - Storage（存储管理）
 * ✅ JGSY.AGI.Storage - Files（文件操作）
 * ✅ JGSY.AGI.Storage - FileManage（文件管理）
 * ✅ JGSY.AGI.Storage - DataSourceManage（数据源管理）
 * ✅ JGSY.AGI.Simulator - Simulator（模拟器主控）
 * ✅ JGSY.AGI.Simulator - SimulatorCommand（模拟器命令）
 * ✅ JGSY.AGI.Simulator - SimulatorPurge（数据清理）
 * 
 * 测试步骤：5 个核心场景
 * 总耗时：约 25 分钟
 * 难度：MEDIUM
 */

const { test, expect } = require('@playwright/test');
const { SemiAutoHelper } = require('../helpers/semi-auto-helper');
const { TestData } = require('../helpers/test-data');

let helper;

test.beforeEach(async ({ page }) => {
  helper = new SemiAutoHelper(page);
  await helper.navigate('http://localhost:3000');
  await helper.login('admin@example.com', 'P@ssw0rd');
  await helper.logStep('✅ 登录成功 - 准备开始存储/模拟器测试');
});

test.afterEach(async ({ page }) => {
  await helper.generateReport('storage-simulator');
});

// ========================================
// 场景 1: 文件存储管理
// ========================================
test('Step 1: 文件上传/下载/管理全流程', async ({ page }) => {
  await helper.logStep('【场景 1】文件存储管理 - 开始');

  await helper.navigate('http://localhost:3000/storage/files');

  await helper.showPrompt(
    '📁 文件管理验证',
    `请验证以下功能：

    1️⃣ 文件列表（名称/大小/类型/上传时间/存储位置）
    2️⃣ 上传文件：
       - 单文件上传
       - 多文件批量上传
       - 拖拽上传
       - 大文件分片上传
    3️⃣ 文件预览（图片/PDF/文本）
    4️⃣ 文件下载
    5️⃣ 文件重命名
    6️⃣ 文件移动（更换目录）
    7️⃣ 文件删除

    ⚠️ 边界测试重点：
    - 上传 0 字节文件
    - 上传超大文件（>500MB）
    - 文件名包含特殊字符（/\\:*?"<>|空格中文emoji）
    - 同名文件覆盖/重命名策略
    - 不支持格式的文件上传

    完成后请点击 ✅ 确认`
  );

  // 文件管理
  await helper.navigate('http://localhost:3000/storage/manage');

  await helper.showPrompt(
    '🗂️ 文件管理后台验证',
    `请验证以下功能：

    1️⃣ 文件分类管理（创建/编辑/删除分类）
    2️⃣ 存储配额管理（按租户/按用户配额）
    3️⃣ 存储统计（使用量/文件数/按类型分布）
    4️⃣ 批量操作（批量删除/批量移动）
    5️⃣ 回收站管理（恢复/永久删除）

    完成后请点击 ✅ 确认`
  );

  await helper.takeScreenshot('25-01-file-storage');
  await helper.logStep('✅ 文件存储管理验证完成');
});

// ========================================
// 场景 2: 存储配置与数据源
// ========================================
test('Step 2: 存储配置与数据源管理', async ({ page }) => {
  await helper.logStep('【场景 2】存储配置 - 开始');

  await helper.navigate('http://localhost:3000/storage/config');

  await helper.showPrompt(
    '⚙️ 存储配置验证',
    `请验证以下功能：

    1️⃣ 存储后端配置（本地磁盘/MinIO/OSS/S3/Azure Blob）
    2️⃣ 存储策略（默认后端/自动归档/CDN加速）
    3️⃣ 上传限制配置（最大文件大小/允许的文件类型/并发数）
    4️⃣ 防盗链配置
    5️⃣ 存储桶管理

    完成后请点击 ✅ 确认`
  );

  // 数据源管理
  await helper.navigate('http://localhost:3000/storage/data-sources');

  await helper.showPrompt(
    '🔗 存储数据源验证',
    `请验证以下功能：

    1️⃣ 数据源列表（名称/类型/连接状态）
    2️⃣ 添加数据源（连接字符串/凭证配置）
    3️⃣ 测试连接
    4️⃣ 编辑/删除数据源

    完成后请点击 ✅ 确认`
  );

  await helper.takeScreenshot('25-02-storage-config');
  await helper.logStep('✅ 存储配置验证完成');
});

// ========================================
// 场景 3: 模拟器管理
// ========================================
test('Step 4: 设备模拟器管理与数据生成', async ({ page }) => {
  await helper.logStep('【场景 4】模拟器管理 - 开始');

  await helper.navigate('http://localhost:3000/simulator');

  await helper.showPrompt(
    '🤖 模拟器管理验证',
    `请验证以下功能：

    1️⃣ 模拟器状态概览（运行中/已停止的模拟会话数）
    2️⃣ 创建模拟会话：
       - 选择设备模型（充电桩/光伏/储能/传感器）
       - 设置设备数量
       - 配置数据生成参数（频率/范围/模式）
       - 配置异常注入（偶发故障/通信中断/数据异常）
    3️⃣ 启动/暂停/停止模拟
    4️⃣ 实时查看模拟数据流
    5️⃣ 模拟场景预设（正常运行/故障场景/过载场景）

    完成后请点击 ✅ 确认`
  );

  // 模拟器命令
  await helper.showPrompt(
    '📡 模拟器命令验证',
    `请验证以下功能：

    1️⃣ 发送模拟器控制命令（批量启动/批量停止）
    2️⃣ 查看命令执行状态
    3️⃣ 调整实时参数（如当前负载、温度变化率）
    4️⃣ 故障注入命令

    完成后请点击 ✅ 确认`
  );

  await helper.takeScreenshot('25-04-simulator');
  await helper.logStep('✅ 模拟器管理验证完成');
});

// ========================================
// 场景 5: 模拟器数据清理
// ========================================
test('Step 5: 模拟器数据清理与验证', async ({ page }) => {
  await helper.logStep('【场景 5】数据清理 - 开始');

  await helper.navigate('http://localhost:3000/simulator/purge');

  await helper.showPrompt(
    '🗑️ 模拟器数据清理验证',
    `请验证以下功能：

    1️⃣ 预览模式：查看将被清理的数据范围和影响
       - 按设备ID筛选
       - 按会话ID筛选
       - 按时间范围筛选
    2️⃣ 软删除模式：标记删除，可恢复
    3️⃣ 物理删除模式：永久删除模拟数据
    4️⃣ 清理范围：
       - 模拟器生成的设备数据
       - 模拟器生成的遥测数据
       - 模拟器生成的告警数据
       - 模拟器生成的订单数据
    5️⃣ 清理结果：删除数量/耗时/错误

    ⚠️ 安全重点：
    - 清理仅影响模拟器数据，不影响真实数据
    - 物理删除需要二次确认
    - 清理过程有审计日志

    完成后请点击 ✅ 确认`
  );

  await helper.takeScreenshot('25-05-simulator-purge');
  await helper.logStep('✅ 模拟器数据清理验证完成');
});
