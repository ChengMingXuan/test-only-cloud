/**
 * 内容平台与站点构建器测试场景 - 21
 * 
 * 覆盖模块：
 * ✅ JGSY.AGI.ContentPlatform.CMS - Portal（门户内容管理）
 * ✅ JGSY.AGI.ContentPlatform.CMS - PortalAdmin（后台管理）
 * ✅ JGSY.AGI.ContentPlatform.CMS - Upload（文件上传）
 * ✅ JGSY.AGI.ContentPlatform.Builder - Site（站点管理）
 * ✅ JGSY.AGI.ContentPlatform.Builder - Page（页面管理）
 * ✅ JGSY.AGI.ContentPlatform.Builder - Component（组件管理）
 * ✅ JGSY.AGI.ContentPlatform.Builder - Block（区块管理）
 * ✅ JGSY.AGI.ContentPlatform.Builder - DataSource（数据源配置）
 * ✅ JGSY.AGI.ContentPlatform.Builder - Publish/PublishRecord（发布管理）
 * ✅ JGSY.AGI.ContentPlatform.Builder - Preview/Render/SSG（预览/渲染/静态生成）
 * ✅ JGSY.AGI.ContentPlatform.Builder - SiteTemplate/PageTemplate（模板管理）
 * ✅ JGSY.AGI.ContentPlatform.Builder - Theme（主题管理）
 * ✅ JGSY.AGI.ContentPlatform.Builder - Media/Collection（媒体/集合管理）
 * ✅ JGSY.AGI.ContentPlatform.Builder - Version（版本管理）
 * ✅ JGSY.AGI.ContentPlatform.Builder - Analytics/Audit（分析/审计）
 * ✅ JGSY.AGI.ContentPlatform.Builder - ScreenMatrix（大屏矩阵）
 * 
 * 测试步骤：7 个核心场景
 * 总耗时：约 35 分钟
 * 难度：MEDIUM-HIGH（涉及可视化建站和内容发布流程）
 */

const { test, expect } = require('@playwright/test');
const { SemiAutoHelper } = require('../helpers/semi-auto-helper');
const { TestData } = require('../helpers/test-data');

let helper;

test.beforeEach(async ({ page }) => {
  helper = new SemiAutoHelper(page);
  await helper.navigate('http://localhost:3000');
  await helper.login('admin@example.com', 'P@ssw0rd');
  await helper.logStep('✅ 登录成功 - 准备开始内容平台测试');
});

test.afterEach(async ({ page }) => {
  await helper.generateReport('content-platform');
});

// ========================================
// 场景 1: 站点管理与模板
// ========================================
test('Step 1: 站点创建与模板管理', async ({ page }) => {
  await helper.logStep('【场景 1】站点管理与模板 - 开始');

  await helper.navigate('http://localhost:3000/content/sites');

  await helper.showPrompt(
    '🌐 站点管理验证',
    `请验证以下功能：

    1️⃣ 站点列表（名称/域名/状态/创建时间）
    2️⃣ 创建新站点（名称/域名/模板选择/语言）
    3️⃣ 编辑站点基本信息
    4️⃣ 站点设置（SEO/分析/邮件通知）
    5️⃣ 删除站点（确认提示/关联数据处理）

    完成后请点击 ✅ 确认`
  );

  // 站点模板
  await helper.navigate('http://localhost:3000/content/site-templates');

  await helper.showPrompt(
    '📋 站点模板管理',
    `请验证以下功能：

    1️⃣ 模板列表（预览图/名称/分类）
    2️⃣ 从模板创建站点
    3️⃣ 保存当前站点为模板
    4️⃣ 编辑/删除模板

    完成后请点击 ✅ 确认`
  );

  await helper.takeScreenshot('21-01-site-templates');
  await helper.logStep('✅ 站点与模板验证完成');
});

// ========================================
// 场景 2: 页面构建器（核心功能）
// ========================================
test('Step 2: 可视化页面构建器', async ({ page }) => {
  await helper.logStep('【场景 2】页面构建器 - 开始');

  await helper.navigate('http://localhost:3000/content/pages');

  await helper.showPrompt(
    '📝 页面管理验证',
    `请验证以下功能：

    1️⃣ 页面列表（标题/路由/状态/修改时间）
    2️⃣ 创建新页面（标题/路由/SEO配置）
    3️⃣ 进入页面编辑器

    完成后请点击 ✅ 确认`
  );

  await helper.showPrompt(
    '🎨 页面编辑器验证（核心功能）',
    `请验证以下可视化编辑功能：

    1️⃣ 组件拖拽：从左侧组件面板拖拽组件到画布
    2️⃣ 组件配置：点击组件 → 右侧属性面板配置
    3️⃣ 布局调整：拖拽排序/删除/复制组件
    4️⃣ 区块管理：创建/编辑/复用区块
    5️⃣ 数据绑定：组件绑定动态数据源
    6️⃣ 响应式预览：桌面/平板/手机切换
    7️⃣ 保存草稿
    8️⃣ 页面模板选择

    完成后请点击 ✅ 确认`
  );

  await helper.takeScreenshot('21-02-page-builder');
  await helper.logStep('✅ 页面构建器验证完成');
});

// ========================================
// 场景 3: 组件与区块管理
// ========================================
test('Step 3: 组件库与区块管理', async ({ page }) => {
  await helper.logStep('【场景 3】组件与区块 - 开始');

  // 3.1 组件管理
  await helper.navigate('http://localhost:3000/content/components');

  await helper.showPrompt(
    '🧩 组件库管理验证',
    `请验证以下功能：

    1️⃣ 组件分类列表（基础/布局/数据/图表/业务）
    2️⃣ 组件预览
    3️⃣ 创建自定义组件（代码/配置/预览图）
    4️⃣ 编辑组件属性
    5️⃣ 删除/停用组件

    完成后请点击 ✅ 确认`
  );

  // 3.2 区块管理
  await helper.navigate('http://localhost:3000/content/blocks');

  await helper.showPrompt(
    '📦 区块管理验证',
    `请验证以下功能：

    1️⃣ 区块列表
    2️⃣ 创建区块（组合多个组件为可复用区块）
    3️⃣ 编辑区块布局
    4️⃣ 区块在页面中的引用使用
    5️⃣ 删除区块

    完成后请点击 ✅ 确认`
  );

  await helper.takeScreenshot('21-03-components-blocks');
  await helper.logStep('✅ 组件与区块验证完成');
});

// ========================================
// 场景 4: 媒体与文件管理
// ========================================
test('Step 4: 媒体库与文件上传管理', async ({ page }) => {
  await helper.logStep('【场景 4】媒体管理 - 开始');

  await helper.navigate('http://localhost:3000/content/media');

  await helper.showPrompt(
    '🖼️ 媒体库管理验证',
    `请验证以下功能：

    1️⃣ 媒体文件列表（图片/视频/文档/按文件夹分类）
    2️⃣ 上传文件（单个/批量/拖拽上传）
    3️⃣ 文件预览（图片/视频/PDF）
    4️⃣ 文件信息编辑（名称/描述/标签）
    5️⃣ 文件分类管理（创建文件夹/移动文件）
    6️⃣ 文件删除
    7️⃣ 文件格式/大小限制验证

    ⚠️ 边界测试：
    - 超大文件上传（>100MB）
    - 不支持的格式上传
    - 文件名含特殊字符
    - 同名文件覆盖策略

    完成后请点击 ✅ 确认`
  );

  await helper.takeScreenshot('21-04-media-upload');
  await helper.logStep('✅ 媒体管理验证完成');
});

// ========================================
// 场景 5: 发布与版本管理
// ========================================
test('Step 5: 内容发布与版本控制', async ({ page }) => {
  await helper.logStep('【场景 5】发布与版本 - 开始');

  // 5.1 发布管理
  await helper.navigate('http://localhost:3000/content/publish');

  await helper.showPrompt(
    '🚀 内容发布验证',
    `请验证以下发布流程：

    1️⃣ 选择要发布的页面/站点
    2️⃣ 发布前预览
    3️⃣ 执行发布（一键发布到生产环境）
    4️⃣ 发布状态跟踪（进度/成功/失败）
    5️⃣ 发布记录列表
    6️⃣ 回滚到上一版本

    完成后请点击 ✅ 确认`
  );

  // 5.2 版本管理
  await helper.navigate('http://localhost:3000/content/versions');

  await helper.showPrompt(
    '📌 版本管理验证',
    `请验证以下功能：

    1️⃣ 版本历史列表（版本号/时间/作者/变更说明）
    2️⃣ 版本对比（两个版本间的差异）
    3️⃣ 恢复到指定版本
    4️⃣ 版本分支管理

    完成后请点击 ✅ 确认`
  );

  // 5.3 SSG静态生成
  await helper.showPrompt(
    '⚡ 静态站点生成验证',
    `请验证以下功能：

    1️⃣ 触发SSG生成
    2️⃣ 生成进度和状态
    3️⃣ 生成结果预览
    4️⃣ 部署静态文件

    完成后请点击 ✅ 确认`
  );

  await helper.takeScreenshot('21-05-publish-version');
  await helper.logStep('✅ 发布与版本验证完成');
});

// ========================================
// 场景 6: 主题与数据源
// ========================================
test('Step 6: 主题系统与数据源配置', async ({ page }) => {
  await helper.logStep('【场景 6】主题与数据源 - 开始');

  // 6.1 主题管理
  await helper.navigate('http://localhost:3000/content/themes');

  await helper.showPrompt(
    '🎭 主题管理验证',
    `请验证以下功能：

    1️⃣ 主题列表（预览图/名称/版本/状态）
    2️⃣ 切换主题（预览效果）
    3️⃣ 自定义主题（颜色/字体/间距）
    4️⃣ 导入/导出主题包
    5️⃣ 删除主题

    完成后请点击 ✅ 确认`
  );

  // 6.2 数据源配置
  await helper.navigate('http://localhost:3000/content/data-sources');

  await helper.showPrompt(
    '🔗 数据源配置验证',
    `请验证以下功能：

    1️⃣ 数据源列表（名称/类型/状态/连接信息）
    2️⃣ 添加新数据源（API/数据库/CSV等）
    3️⃣ 测试连接
    4️⃣ 数据映射配置
    5️⃣ 删除数据源

    完成后请点击 ✅ 确认`
  );

  await helper.takeScreenshot('21-06-theme-datasource');
  await helper.logStep('✅ 主题与数据源验证完成');
});

// ========================================
// 场景 7: 大屏矩阵与门户内容审计
// ========================================
test('Step 7: 大屏展示/门户内容/审计日志', async ({ page }) => {
  await helper.logStep('【场景 7】大屏与审计 - 开始');

  // 7.1 大屏矩阵
  await helper.navigate('http://localhost:3000/content/screen-matrix');

  await helper.showPrompt(
    '🖥️ 大屏矩阵验证',
    `请验证以下功能：

    1️⃣ 大屏列表
    2️⃣ 创建大屏（选择分辨率/布局/数据源）
    3️⃣ 大屏编辑器（拖拽组件/数据绑定/动画效果）
    4️⃣ 大屏预览（全屏展示）
    5️⃣ 多屏联动配置

    完成后请点击 ✅ 确认`
  );

  // 7.2 门户内容管理
  await helper.navigate('http://localhost:3000/content/portal');

  await helper.showPrompt(
    '🏠 门户内容管理验证',
    `请验证以下功能：

    1️⃣ 门户首页内容编辑
    2️⃣ 公告/新闻/活动管理
    3️⃣ 轮播图配置
    4️⃣ 导航菜单配置
    5️⃣ 底部信息配置

    完成后请点击 ✅ 确认`
  );

  // 7.3 审计日志
  await helper.navigate('http://localhost:3000/content/audit');

  await helper.showPrompt(
    '📋 内容审计日志',
    `请验证以下功能：

    1️⃣ 操作日志列表（用户/操作/对象/时间）
    2️⃣ 日志筛选（按用户/操作类型/时间范围）
    3️⃣ 日志详情（变更前后对比）
    4️⃣ 分析统计

    完成后请点击 ✅ 确认`
  );

  await helper.takeScreenshot('21-07-screen-portal-audit');
  await helper.logStep('✅ 大屏、门户、审计验证完成');
});
