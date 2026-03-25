/**
 * 可观测性与运维监控测试场景 - 24
 * 
 * 覆盖模块：
 * ✅ JGSY.AGI.Observability - Dashboard（监控仪表板）
 * ✅ JGSY.AGI.Observability - ServiceMonitor（服务监控）
 * ✅ JGSY.AGI.Observability - ServiceMeshManage（服务网格管理）
 * ✅ JGSY.AGI.Observability - ServiceOps（服务运维）
 * ✅ JGSY.AGI.Observability - SystemStatus（系统状态）
 * ✅ JGSY.AGI.Observability - Trace/Tracing（链路追踪）
 * ✅ JGSY.AGI.Observability - Log（日志查询）
 * ✅ JGSY.AGI.Observability - SqlMonitor（SQL监控）
 * ✅ JGSY.AGI.Observability - OperationLog（操作日志）
 * ✅ JGSY.AGI.Observability - LoginLog（登录日志）
 * ✅ JGSY.AGI.Observability - Online（在线用户）
 * ✅ JGSY.AGI.Observability - AuditItem（审计项目）
 * ✅ JGSY.AGI.Observability - ApiManage（API管理）
 * ✅ JGSY.AGI.Observability - CodeGen（代码生成）
 * ✅ JGSY.AGI.Observability - DatabaseBackup（数据库备份）
 * ✅ JGSY.AGI.Observability - DbDocs（数据库文档）
 * ✅ JGSY.AGI.Observability - MonitorLifecycle（监控生命周期）
 * 
 * 测试步骤：7 个核心场景
 * 总耗时：约 35 分钟
 * 难度：MEDIUM（涉及运维场景）
 */

const { test, expect } = require('@playwright/test');
const { SemiAutoHelper } = require('../helpers/semi-auto-helper');
const { TestData } = require('../helpers/test-data');

let helper;

test.beforeEach(async ({ page }) => {
  helper = new SemiAutoHelper(page);
  await helper.navigate('http://localhost:3000');
  await helper.login('admin@example.com', 'P@ssw0rd');
  await helper.logStep('✅ 登录成功 - 准备开始可观测性测试');
});

test.afterEach(async ({ page }) => {
  await helper.generateReport('observability');
});

// ========================================
// 场景 1: 监控仪表板与系统状态
// ========================================
test('Step 1: 监控仪表板与系统全局状态', async ({ page }) => {
  await helper.logStep('【场景 1】监控仪表板 - 开始');

  await helper.navigate('http://localhost:3000/observability/dashboard');

  await helper.showPrompt(
    '📊 监控仪表板验证',
    `请验证以下内容：

    1️⃣ 系统整体健康状态（绿/黄/红指示灯）
    2️⃣ 各微服务状态概览（31个服务在线/离线/异常）
    3️⃣ 实时请求量/错误率/响应时间 Top N
    4️⃣ 资源使用率（CPU/内存/磁盘/网络）
    5️⃣ 关键指标趋势图（近1h/6h/24h/7d）
    6️⃣ 告警面板

    完成后请点击 ✅ 确认`
  );

  // 系统状态
  await helper.navigate('http://localhost:3000/observability/system-status');

  await helper.showPrompt(
    '🖥️ 系统状态详情',
    `请验证以下内容：

    1️⃣ 各节点状态（主机名/IP/CPU/内存/磁盘）
    2️⃣ 容器运行状态（运行中/停止/重启次数）
    3️⃣ 数据库连接池状态
    4️⃣ 消息队列状态（积压/消费速率）
    5️⃣ 缓存命中率

    完成后请点击 ✅ 确认`
  );

  await helper.takeScreenshot('24-01-dashboard-status');
  await helper.logStep('✅ 监控仪表板验证完成');
});

// ========================================
// 场景 2: 服务监控与网格管理
// ========================================
test('Step 2: 微服务监控与Service Mesh', async ({ page }) => {
  await helper.logStep('【场景 2】服务监控 - 开始');

  // 2.1 服务监控
  await helper.navigate('http://localhost:3000/observability/services');

  await helper.showPrompt(
    '🔍 服务监控验证',
    `请验证以下功能：

    1️⃣ 微服务列表（名称/端口/状态/请求量/错误率/P99延迟）
    2️⃣ 服务详情（实例列表/指标图表/依赖关系）
    3️⃣ 服务拓扑图（调用关系可视化）
    4️⃣ 服务健康检查配置
    5️⃣ 监控告警规则设置

    完成后请点击 ✅ 确认`
  );

  // 2.2 服务网格
  await helper.navigate('http://localhost:3000/observability/service-mesh');

  await helper.showPrompt(
    '🕸️ 服务网格管理验证',
    `请验证以下功能：

    1️⃣ 服务网格拓扑图（全局调用链路图）
    2️⃣ 流量路由规则配置
    3️⃣ 熔断/限流策略配置
    4️⃣ 负载均衡策略
    5️⃣ 灰度发布配置

    完成后请点击 ✅ 确认`
  );

  // 2.3 服务运维
  await helper.navigate('http://localhost:3000/observability/service-ops');

  await helper.showPrompt(
    '🔧 服务运维操作验证',
    `请验证以下功能：

    1️⃣ 服务重启
    2️⃣ 服务扩缩容
    3️⃣ 配置热更新
    4️⃣ 服务版本回退

    完成后请点击 ✅ 确认`
  );

  await helper.takeScreenshot('24-02-service-mesh');
  await helper.logStep('✅ 服务监控与网格验证完成');
});

// ========================================
// 场景 3: 链路追踪
// ========================================
test('Step 3: 分布式链路追踪', async ({ page }) => {
  await helper.logStep('【场景 3】链路追踪 - 开始');

  await helper.navigate('http://localhost:3000/observability/tracing');

  await helper.showPrompt(
    '🔍 链路追踪验证',
    `请验证以下功能：

    1️⃣ Trace 列表（TraceID/服务/操作/时长/状态/时间）
    2️⃣ 按条件筛选（服务名/操作名/时间范围/最小耗时/状态）
    3️⃣ Trace 详情 - 瀑布图（Span层级/时序/耗时分布）
    4️⃣ 跨服务调用链路完整性
    5️⃣ 慢接口识别（P99/异常高亮）
    6️⃣ 比较两个Trace的差异

    ⚠️ 业务重点：
    - 确保31个微服务的调用链路完整
    - Trace ID 贯穿全链路

    完成后请点击 ✅ 确认`
  );

  await helper.takeScreenshot('24-03-tracing');
  await helper.logStep('✅ 链路追踪验证完成');
});

// ========================================
// 场景 4: 日志管理
// ========================================
test('Step 4: 结构化日志查询与分析', async ({ page }) => {
  await helper.logStep('【场景 4】日志管理 - 开始');

  // 4.1 日志查询
  await helper.navigate('http://localhost:3000/observability/logs');

  await helper.showPrompt(
    '📋 日志查询验证',
    `请验证以下功能：

    1️⃣ 日志列表（时间/级别/服务/消息/TraceID）
    2️⃣ 按级别筛选（Debug/Info/Warning/Error/Fatal）
    3️⃣ 按服务筛选
    4️⃣ 全文搜索
    5️⃣ 时间范围选择
    6️⃣ 日志详情展开（结构化字段/堆栈跟踪）
    7️⃣ 从日志跳转到对应Trace

    完成后请点击 ✅ 确认`
  );

  // 4.2 操作日志
  await helper.navigate('http://localhost:3000/observability/operation-logs');

  await helper.showPrompt(
    '📝 操作日志验证',
    `请验证以下功能：

    1️⃣ 操作日志列表（用户/操作/模块/时间/IP）
    2️⃣ 按用户/模块/操作类型筛选
    3️⃣ 操作详情（变更前后数据对比）
    4️⃣ 日志导出

    完成后请点击 ✅ 确认`
  );

  // 4.3 登录日志
  await helper.navigate('http://localhost:3000/observability/login-logs');

  await helper.showPrompt(
    '🔑 登录日志验证',
    `请验证以下功能：

    1️⃣ 登录日志列表（用户/IP/设备/时间/结果）
    2️⃣ 筛选：成功/失败登录
    3️⃣ 异常登录检测（异地/频繁失败）
    4️⃣ 日志导出

    完成后请点击 ✅ 确认`
  );

  await helper.takeScreenshot('24-04-logs');
  await helper.logStep('✅ 日志管理验证完成');
});

// ========================================
// 场景 5: SQL 监控与性能分析
// ========================================
test('Step 5: SQL 监控与数据库性能', async ({ page }) => {
  await helper.logStep('【场景 5】SQL 监控 - 开始');

  await helper.navigate('http://localhost:3000/observability/sql-monitor');

  await helper.showPrompt(
    '🗄️ SQL 监控验证',
    `请验证以下功能：

    1️⃣ 慢 SQL 列表（SQL文本/执行时间/影响行数/服务）
    2️⃣ SQL 执行频率统计
    3️⃣ 执行计划解析
    4️⃣ 慢查询告警配置
    5️⃣ 数据库连接池监控

    完成后请点击 ✅ 确认`
  );

  // 在线用户
  await helper.navigate('http://localhost:3000/observability/online-users');

  await helper.showPrompt(
    '👥 在线用户监控',
    `请验证以下功能：

    1️⃣ 当前在线用户列表（用户名/IP/设备/登录时间/最后活跃）
    2️⃣ 强制下线操作
    3️⃣ 在线统计（按时间/按租户）

    完成后请点击 ✅ 确认`
  );

  await helper.takeScreenshot('24-05-sql-online');
  await helper.logStep('✅ SQL 监控与在线用户验证完成');
});

// ========================================
// 场景 6: API 管理与代码生成
// ========================================
test('Step 6: API 管理/代码生成/数据库文档', async ({ page }) => {
  await helper.logStep('【场景 6】API与工具 - 开始');

  // 6.1 API 管理
  await helper.navigate('http://localhost:3000/observability/api-manage');

  await helper.showPrompt(
    '🔌 API 管理验证',
    `请验证以下功能：

    1️⃣ API 列表（路径/方法/服务/版本/状态）
    2️⃣ API 详情（参数/响应/示例）
    3️⃣ API 调用统计
    4️⃣ API Mock 配置
    5️⃣ API 分组管理

    完成后请点击 ✅ 确认`
  );

  // 6.2 代码生成
  await helper.navigate('http://localhost:3000/observability/code-gen');

  await helper.showPrompt(
    '🛠️ 代码生成器验证',
    `请验证以下功能：

    1️⃣ 选择数据库表
    2️⃣ 配置生成选项（实体/仓储/服务/控制器/前端页面）
    3️⃣ 预览生成代码
    4️⃣ 下载/复制代码

    完成后请点击 ✅ 确认`
  );

  // 6.3 数据库文档
  await helper.navigate('http://localhost:3000/observability/db-docs');

  await helper.showPrompt(
    '📚 数据库文档验证',
    `请验证以下功能：

    1️⃣ 数据库列表
    2️⃣ 表结构文档（表名/字段/类型/注释）
    3️⃣ 文档导出（Word/PDF/HTML）
    4️⃣ 版本对比

    完成后请点击 ✅ 确认`
  );

  await helper.takeScreenshot('24-06-api-codegen-docs');
  await helper.logStep('✅ API、代码生成、数据库文档验证完成');
});

// ========================================
// 场景 7: 数据库备份与审计
// ========================================
test('Step 7: 数据库备份与审计项目', async ({ page }) => {
  await helper.logStep('【场景 7】备份与审计 - 开始');

  // 7.1 数据库备份
  await helper.navigate('http://localhost:3000/observability/db-backup');

  await helper.showPrompt(
    '💾 数据库备份验证',
    `请验证以下功能：

    1️⃣ 备份列表（数据库/类型/大小/时间/状态）
    2️⃣ 创建备份（全量/增量/指定数据库）
    3️⃣ 定时备份策略配置
    4️⃣ 备份恢复（选择备份 → 恢复到目标）
    5️⃣ 备份文件下载
    6️⃣ 清理过期备份

    完成后请点击 ✅ 确认`
  );

  // 7.2 审计项目
  await helper.navigate('http://localhost:3000/observability/audit');

  await helper.showPrompt(
    '🔍 审计项目验证',
    `请验证以下功能：

    1️⃣ 审计策略配置（需要审计的操作类型）
    2️⃣ 审计日志查询
    3️⃣ 审计报告生成
    4️⃣ 审计合规检查

    完成后请点击 ✅ 确认`
  );

  // 7.3 监控生命周期
  await helper.navigate('http://localhost:3000/observability/monitor-lifecycle');

  await helper.showPrompt(
    '♻️ 监控数据生命周期',
    `请验证以下功能：

    1️⃣ 监控数据保留策略（指标/日志/Trace 保留天数）
    2️⃣ 归档策略配置
    3️⃣ 数据清理执行
    4️⃣ 存储空间使用统计

    完成后请点击 ✅ 确认`
  );

  await helper.takeScreenshot('24-07-backup-audit');
  await helper.logStep('✅ 数据库备份与审计验证完成');
});
