/**
 * 可观测性高级功能深度测试 - 35
 *
 * 补充场景24未覆盖的 22 个子控制器高级功能：
 * ✅ ApiManage（API 管理：接口注册/文档/版本/Mock/限流/统计）
 * ✅ AuditItem（审计项配置：定义哪些操作需要审计）
 * ✅ CodeGen（代码生成器：从数据表→生成 CRUD 代码/前后端模板）
 * ✅ DatabaseBackup（数据库备份管理：手动/自动/恢复/验证）
 * ✅ DbDocs（数据库文档：表结构/ER图/数据字典自动生成）
 * ✅ LoginLog（登录日志：成功/失败/IP/设备/地理位置）
 * ✅ MonitorLifecycle（监控生命周期：告警规则/升级/通知链）
 * ✅ Online（在线用户管理：在线列表/强制下线/踢出）
 * ✅ OperationLog（操作日志：业务操作全量记录/变更对比）
 * ✅ ServiceMeshManage（服务网格管理：服务发现/路由/负载均衡/熔断）
 * ✅ ServiceMonitor（服务监控：健康检查/性能指标/依赖关系图）
 * ✅ ServiceOps（服务运维：启停/重启/扩缩容/灰度/配置推送）
 * ✅ SqlMonitor（SQL 监控：慢查询/执行计划/优化建议）
 * ✅ SystemStatus（系统状态：CPU/内存/磁盘/网络/JVM/GC）
 * ✅ Trace/Tracing（链路追踪：请求链路/耗时分布/异常追踪）
 * ✅ WorkOrderCallback（工单回调：与工单系统联动）
 *
 * 测试步骤：12 个深度场景
 * 总耗时：约 60 分钟
 * 难度：HIGH（涉及运维监控、链路追踪、SQL分析）
 */

const { test, expect } = require('@playwright/test');
const { SemiAutoHelper } = require('../helpers/semi-auto-helper');
const { TestData } = require('../helpers/test-data');

let helper;

test.beforeEach(async ({ page }) => {
  helper = new SemiAutoHelper(page);
  await helper.navigate('http://localhost:3000');
  await helper.login('admin@example.com', 'P@ssw0rd');
  await helper.logStep('✅ 登录成功 - 准备开始可观测性高级功能测试');
});

test.afterEach(async ({ page }) => {
  await helper.generateReport('observability-advanced');
});

// ========================================
// 场景 1: API 管理
// ========================================
test('Step 1: API 管理 - 注册/文档/Mock/统计', async ({ page }) => {
  await helper.logStep('【场景 1】API 管理');

  await helper.navigate('http://localhost:3000/monitor/api-manage');

  await helper.showPrompt(
    '📡 API 管理验证',
    `请验证以下功能：

    1️⃣ API 接口列表（路径/方法/服务/描述/状态/版本）
    2️⃣ API 在线文档（Swagger/ReDoc 风格自动生成）
    3️⃣ API 版本管理（v1/v2 共存/废弃标记）
    4️⃣ API 限流配置（单接口限流策略）
    5️⃣ API 调用统计（QPS/成功率/平均响应时间/P99延迟）
    6️⃣ API 健康检查（各接口可用性/响应时间趋势）
    7️⃣ API Mock 服务（配置 Mock 返回数据/用于前端联调）

    ⚠️ 验证要点：
    - API 文档与实际接口一致性
    - 限流触发后返回 429 状态码
    - 统计数据实时刷新精度

    完成后请点击 ✅ 确认`
  );

  await helper.takeScreenshot('35-01-api-manage');
  await helper.logStep('✅ API 管理验证完成');
});

// ========================================
// 场景 2: 登录日志与操作日志
// ========================================
test('Step 2: 登录日志 + 操作日志全面审计', async ({ page }) => {
  await helper.logStep('【场景 2】日志审计');

  await helper.navigate('http://localhost:3000/monitor/login-log');

  await helper.showPrompt(
    '📝 日志审计验证',
    `请验证以下功能：

    【登录日志 LoginLog】
    1️⃣ 登录日志列表（用户/IP/设备/浏览器/地理位置/时间/结果）
    2️⃣ 登录失败记录（错误原因/连续失败次数/是否触发锁定）
    3️⃣ 异常登录检测（异地登录/频繁登录/非工作时间登录）
    4️⃣ 日志筛选（用户/IP/时间/结果）
    5️⃣ 日志导出

    【操作日志 OperationLog】
    6️⃣ 操作日志列表（时间/用户/模块/操作类型/详情/IP）
    7️⃣ 操作变更对比（Before/After JSON diff 展示）
    8️⃣ 敏感操作高亮标记
    9️⃣ 日志筛选（按模块/用户/操作类型/时间范围）
    🔟 日志统计（操作频率/热门操作/活跃用户 TOP N）

    完成后请点击 ✅ 确认`
  );

  await helper.takeScreenshot('35-02-logs');
  await helper.logStep('✅ 日志审计验证完成');
});

// ========================================
// 场景 3: 服务监控与健康检查
// ========================================
test('Step 3: 服务监控 - 健康/指标/依赖关系', async ({ page }) => {
  await helper.logStep('【场景 3】服务监控');

  await helper.navigate('http://localhost:3000/monitor/service');

  await helper.showPrompt(
    '💓 服务监控验证',
    `请验证以下功能：

    【服务监控 ServiceMonitor】
    1️⃣ 服务列表（名称/状态/实例数/版本/健康/响应时间）
    2️⃣ 健康检查详情（每个服务的 /health 端点状态）
    3️⃣ 性能指标（CPU/内存/线程数/GC 频率/请求数）
    4️⃣ 依赖关系图（服务间调用关系拓扑可视化）
    5️⃣ 异常服务告警（不健康服务自动告警）

    【服务运维 ServiceOps】
    6️⃣ 服务启停控制（启动/停止/重启单个服务）
    7️⃣ 服务配置推送（在线修改配置并推送到运行实例）
    8️⃣ 灰度发布控制（按百分比/按实例切流量）

    完成后请点击 ✅ 确认`
  );

  await helper.takeScreenshot('35-03-service-monitor');
  await helper.logStep('✅ 服务监控验证完成');
});

// ========================================
// 场景 4: 服务网格管理
// ========================================
test('Step 4: 服务网格 - 发现/路由/负载均衡/熔断', async ({ page }) => {
  await helper.logStep('【场景 4】服务网格');

  await helper.navigate('http://localhost:3000/monitor/mesh');

  await helper.showPrompt(
    '🕸️ 服务网格管理验证',
    `请验证以下功能：

    1️⃣ 服务注册/发现（自动注册的服务列表/实例地址）
    2️⃣ 路由规则管理（基于 Header/Path/权重的路由策略）
    3️⃣ 负载均衡策略（轮询/随机/权重/最少连接）
    4️⃣ 熔断配置（错误率阈值/熔断时间/半开探测）
    5️⃣ 限流配置（全局/服务级别/接口级别）
    6️⃣ 流量镜像（镜像流量到测试环境）
    7️⃣ 网格拓扑可视化（实时流量流向/延迟/错误率）

    ⚠️ 验证要点：
    - 服务下线后自动从注册中心摘除
    - 熔断触发后的降级返回
    - 流量切换的无损性

    完成后请点击 ✅ 确认`
  );

  await helper.takeScreenshot('35-04-mesh');
  await helper.logStep('✅ 服务网格验证完成');
});

// ========================================
// 场景 5: 链路追踪
// ========================================
test('Step 5: 链路追踪 - 请求链路/耗时/异常定位', async ({ page }) => {
  await helper.logStep('【场景 5】链路追踪');

  await helper.navigate('http://localhost:3000/monitor/trace');

  await helper.showPrompt(
    '🔗 链路追踪验证',
    `请验证以下功能：

    1️⃣ Trace 列表（TraceID/开始时间/耗时/Span数/状态/入口服务）
    2️⃣ Trace 详情（时序瀑布图/各 Span 耗时/标签/日志）
    3️⃣ 异常 Trace 标记（包含错误的链路高亮）
    4️⃣ 慢 Trace 筛选（耗时排序/超阈值标记）
    5️⃣ 服务间调用统计（A→B 的平均耗时/错误率）
    6️⃣ 按 TraceID 精确查询
    7️⃣ 按时间+服务+状态组合查询

    ⚠️ 验证要点：
    - 跨服务调用链路完整性
    - Span 嵌套关系正确性
    - 异常传播的标记准确性
    - 大量 Trace 数据的查询性能

    完成后请点击 ✅ 确认`
  );

  await helper.takeScreenshot('35-05-trace');
  await helper.logStep('✅ 链路追踪验证完成');
});

// ========================================
// 场景 6: SQL 监控
// ========================================
test('Step 6: SQL 监控 - 慢查询/执行计划/优化建议', async ({ page }) => {
  await helper.logStep('【场景 6】SQL 监控');

  await helper.navigate('http://localhost:3000/monitor/sql');

  await helper.showPrompt(
    '🗄️ SQL 监控验证',
    `请验证以下功能：

    1️⃣ 慢查询列表（SQL/耗时/执行次数/数据库/表/时间）
    2️⃣ 慢查询详情（完整SQL/参数/执行计划/扫描行数）
    3️⃣ 执行计划分析（EXPLAIN 可视化/索引使用情况）
    4️⃣ 优化建议（缺失索引/全表扫描/查询改写建议）
    5️⃣ SQL 统计（TOP N 慢查询/TOP N 高频查询）
    6️⃣ 慢查询阈值配置（超过 xxx ms 记录为慢查询）
    7️⃣ SQL 审计（DDL 操作/高危操作记录）

    ⚠️ 验证要点：
    - 慢查询参数脱敏（不暴露用户数据）
    - 执行计划解读的准确性
    - 大量 SQL 记录的分页查询性能

    完成后请点击 ✅ 确认`
  );

  await helper.takeScreenshot('35-06-sql-monitor');
  await helper.logStep('✅ SQL 监控验证完成');
});

// ========================================
// 场景 7: 系统状态监控
// ========================================
test('Step 7: 系统状态 - CPU/内存/磁盘/网络/JVM', async ({ page }) => {
  await helper.logStep('【场景 7】系统状态');

  await helper.navigate('http://localhost:3000/monitor/system');

  await helper.showPrompt(
    '📈 系统状态监控验证',
    `请验证以下功能：

    1️⃣ CPU 使用率实时图表（各核心/平均/趋势）
    2️⃣ 内存使用情况（总量/已用/缓存/Swap）
    3️⃣ 磁盘使用率（各分区/读写 IOPS/带宽）
    4️⃣ 网络流量（入/出流量/连接数/TCP状态分布）
    5️⃣ 应用运行时（CLR GC/线程池/句柄数）
    6️⃣ 数据库连接池状态（活跃/空闲/等待数/最大连接数）
    7️⃣ Redis 状态（已用内存/命中率/连接数/Key 数量）
    8️⃣ 消息队列状态（队列深度/消费速率/积压量）
    9️⃣ 告警阈值配置（各指标超阈值自动告警）

    完成后请点击 ✅ 确认`
  );

  await helper.takeScreenshot('35-07-system-status');
  await helper.logStep('✅ 系统状态监控验证完成');
});

// ========================================
// 场景 8: 在线用户管理
// ========================================
test('Step 8: 在线用户管理 - 列表/强制下线/踢出', async ({ page }) => {
  await helper.logStep('【场景 8】在线用户');

  await helper.navigate('http://localhost:3000/monitor/online');

  await helper.showPrompt(
    '👥 在线用户管理验证',
    `请验证以下功能：

    1️⃣ 在线用户列表（用户名/IP/登录时间/最后活跃/设备/浏览器）
    2️⃣ 在线用户搜索（按用户名/IP/租户）
    3️⃣ 强制下线（选择用户→确认→立即踢出/Token失效）
    4️⃣ 批量踢出（按租户/按 IP 段批量下线）
    5️⃣ 在线统计（当前在线数/峰值在线数/在线趋势图）
    6️⃣ 被踢出用户的体验（立即跳转登录页/提示被踢出原因）

    ⚠️ 安全验证：
    - 踢出后 Token 立即作废
    - 只有超管可以踢出其他人
    - 踢出操作记录审计日志

    完成后请点击 ✅ 确认`
  );

  await helper.takeScreenshot('35-08-online');
  await helper.logStep('✅ 在线用户验证完成');
});

// ========================================
// 场景 9: 代码生成器
// ========================================
test('Step 9: 代码生成器 - 从表结构生成 CRUD', async ({ page }) => {
  await helper.logStep('【场景 9】代码生成器');

  await helper.navigate('http://localhost:3000/monitor/codegen');

  await helper.showPrompt(
    '🔨 代码生成器验证',
    `请验证以下功能：

    1️⃣ 数据库表列表（连接数据库→读取所有表→展示表结构）
    2️⃣ 选择表生成代码（勾选表→配置生成选项）
    3️⃣ 生成选项（包名/作者/模块名/功能名/前后端生成开关）
    4️⃣ 字段配置（哪些字段参与表单/列表/查询/排序/校验）
    5️⃣ 代码预览（生成前预览各文件内容）
    6️⃣ 代码下载（ZIP 打包下载生成的代码）
    7️⃣ 生成历史记录

    ⚠️ 验证要点：
    - 生成的代码编译通过
    - 表字段类型映射正确性（PostgreSQL→C#/TypeScript）
    - 中文表名/字段备注正确引用

    完成后请点击 ✅ 确认`
  );

  await helper.takeScreenshot('35-09-codegen');
  await helper.logStep('✅ 代码生成器验证完成');
});

// ========================================
// 场景 10: 数据库文档与备份
// ========================================
test('Step 10: 数据库文档自动生成 + 线上备份管理', async ({ page }) => {
  await helper.logStep('【场景 10】数据库文档与备份');

  await helper.navigate('http://localhost:3000/monitor/db-docs');

  await helper.showPrompt(
    '📄 数据库文档与备份验证',
    `请验证以下功能：

    【数据库文档 DbDocs】
    1️⃣ 数据库列表（各微服务数据库）
    2️⃣ 表结构文档（表名/注释/字段名/类型/可空/默认值/注释）
    3️⃣ ER 图自动生成（表间外键关系可视化）
    4️⃣ 数据字典导出（Word/Markdown/HTML）
    5️⃣ 表结构变更历史（版本对比）

    【数据库备份 DatabaseBackup】
    6️⃣ 在线创建备份任务
    7️⃣ 备份列表（名称/大小/时间/状态）
    8️⃣ 下载备份文件
    9️⃣ 恢复备份（选择备份→确认→恢复）
    🔟 自动备份策略配置

    完成后请点击 ✅ 确认`
  );

  await helper.takeScreenshot('35-10-dbdocs-backup');
  await helper.logStep('✅ 数据库文档与备份验证完成');
});

// ========================================
// 场景 11: 审计项配置
// ========================================
test('Step 11: 审计项配置 - 定义哪些操作需要审计', async ({ page }) => {
  await helper.logStep('【场景 11】审计项配置');

  await helper.navigate('http://localhost:3000/monitor/audit-item');

  await helper.showPrompt(
    '🛡️ 审计项配置验证',
    `请验证以下功能：

    1️⃣ 审计项列表（模块/操作/级别/是否启用/记录详情级别）
    2️⃣ 新增审计项（选择模块→操作→级别→记录策略）
    3️⃣ 编辑/删除/启停审计项
    4️⃣ 批量配置（按模块一键启用/禁用所有审计项）
    5️⃣ 审计级别配置（仅操作记录 / 含请求参数 / 含返回结果）
    6️⃣ 审计策略（全量记录 / 采样记录 / 仅异常记录）

    ⚠️ 验证：
    - 启用审计后执行对应操作是否产生日志
    - 禁用后是否停止记录
    - 审计对性能的影响（对比启用前后响应时间）

    完成后请点击 ✅ 确认`
  );

  await helper.takeScreenshot('35-11-audit-item');
  await helper.logStep('✅ 审计项配置验证完成');
});

// ========================================
// 场景 12: 监控生命周期与告警链
// ========================================
test('Step 12: 监控告警规则 + 升级策略 + 通知链', async ({ page }) => {
  await helper.logStep('【场景 12】监控告警');

  await helper.navigate('http://localhost:3000/monitor/lifecycle');

  await helper.showPrompt(
    '🔔 监控告警规则与通知链验证',
    `请验证以下功能：

    1️⃣ 告警规则列表（指标/阈值/持续时间/级别/关联服务/启用状态）
    2️⃣ 创建告警规则（组合条件：AND/OR/持续时间/静默期）
    3️⃣ 告警升级策略（5分钟未处理→升级通知→15分钟→电话）
    4️⃣ 通知链配置（站内信→邮件→短信→企业微信→电话梯级通知）
    5️⃣ 告警确认/解除（人工确认/自动恢复解除）
    6️⃣ 告警历史与统计（触发次数/MTTR/误报率）
    7️⃣ 告警静默（维护窗口期内静默特定告警）
    8️⃣ 工单联动（告警自动创建工单→分配→跟踪）

    完成后请点击 ✅ 确认`
  );

  await helper.takeScreenshot('35-12-alert-lifecycle');
  await helper.logStep('✅ 监控告警验证完成');
});
