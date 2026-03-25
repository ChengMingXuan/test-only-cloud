/**
 * 内容平台 Builder 深度测试 - 36
 *
 * 补充场景21未覆盖的 22 个 Builder 子控制器功能：
 * ✅ Site（站点管理：创建/配置/域名/SEO）
 * ✅ Page（页面管理：CRUD/版本/多语言/组件布局）
 * ✅ Component（组件管理：注册/配置/属性/事件/样式）
 * ✅ Block（区块管理：预制区块/自定义区块/区块库）
 * ✅ Collection（内容集合：数据模型/CRUD/API/关联查询）
 * ✅ DataSource（数据源管理：API/数据库/静态/动态数据绑定）
 * ✅ Media（媒体库：图片/视频/文件上传/管理/CDN）
 * ✅ PageTemplate（页面模板：模板市场/自定义/应用/分享）
 * ✅ SiteTemplate（站点模板：一键建站模板/主题切换）
 * ✅ Permission（Builder权限：协作者/编辑/预览/发布权限）
 * ✅ Preview（预览：实时预览/多端预览/响应式/暗黑模式）
 * ✅ Public（公开页面访问/SEO友好URL）
 * ✅ Render（渲染引擎：SSR/CSR/SSG 混合渲染）
 * ✅ ScreenMatrix（多屏适配：桌面/平板/手机/大屏）
 * ✅ Theme（主题管理：颜色/字体/间距/组件主题）
 * ✅ Version（版本管理：草稿/发布/回滚/版本对比）
 * ✅ Ssg（静态站点生成：构建/部署/CDN分发）
 * ✅ Publish/PublishRecord（发布管理：发布/发布记录/审核/回滚）
 * ✅ Audit（Builder审计：操作日志/变更追踪）
 * ✅ Analytics（Builder分析：页面PV/UV/停留时间/热力图）
 *
 * 测试步骤：10 个深度场景
 * 总耗时：约 50 分钟
 * 难度：HIGH（涉及页面构建、组件编排、多端预览）
 */

const { test, expect } = require('@playwright/test');
const { SemiAutoHelper } = require('../helpers/semi-auto-helper');
const { TestData } = require('../helpers/test-data');

let helper;

test.beforeEach(async ({ page }) => {
  helper = new SemiAutoHelper(page);
  await helper.navigate('http://localhost:3000');
  await helper.login('admin@example.com', 'P@ssw0rd');
  await helper.logStep('✅ 登录成功 - 准备开始内容平台 Builder 测试');
});

test.afterEach(async ({ page }) => {
  await helper.generateReport('content-builder');
});

// ========================================
// 场景 1: 站点管理
// ========================================
test('Step 1: 站点管理 - 创建/配置/域名/SEO', async ({ page }) => {
  await helper.logStep('【场景 1】站点管理');

  await helper.navigate('http://localhost:3000/builder/site');

  await helper.showPrompt(
    '🌍 站点管理验证',
    `请验证以下功能：

    1️⃣ 站点列表（名称/域名/模板/状态/最后更新）
    2️⃣ 创建站点（名称/描述/选择模板/配置域名）
    3️⃣ 站点设置（基本信息/Logo/Favicon/语言/时区）
    4️⃣ 域名配置（自定义域名绑定/SSL证书/重定向规则）
    5️⃣ SEO 配置（Meta标题/描述/关键词/OG图片/Sitemap）
    6️⃣ 站点统计（PV/UV/访客来源/设备分布）
    7️⃣ 站点复制/归档/删除

    ⚠️ 验证要点：
    - 域名解析验证流程
    - SEO 标签在页面源码中正确渲染
    - 站点删除的级联处理（页面/组件/媒体一并处理）

    完成后请点击 ✅ 确认`
  );

  await helper.takeScreenshot('36-01-site');
  await helper.logStep('✅ 站点管理验证完成');
});

// ========================================
// 场景 2: 页面管理与可视化编辑
// ========================================
test('Step 2: 页面管理 - 创建/组件编排/多语言/版本', async ({ page }) => {
  await helper.logStep('【场景 2】页面管理');

  await helper.navigate('http://localhost:3000/builder/page');

  await helper.showPrompt(
    '📄 页面管理与编辑验证',
    `请验证以下功能：

    1️⃣ 页面列表（站点下的所有页面/路由/状态/最后编辑）
    2️⃣ 创建页面（选择模板/设置路由/标题）
    3️⃣ 可视化编辑器（拖拽组件到画布/调整布局/编辑属性）
    4️⃣ 页面树结构（父子页面/导航层级）
    5️⃣ 多语言支持（同一页面的多语言版本切换编辑）
    6️⃣ 页面版本管理（保存草稿→发布→版本列表→回滚到指定版本）
    7️⃣ 页面复制/移动/删除
    8️⃣ 组件布局编辑（网格/Flex/绝对定位/响应式断点）

    ⚠️ 边界测试 [§3.3]：
    - 页面路由冲突检测
    - 空页面（无组件）发布
    - 超多组件（100+）的页面编辑性能
    - 嵌套层级深度限制

    完成后请点击 ✅ 确认`
  );

  await helper.takeScreenshot('36-02-page');
  await helper.logStep('✅ 页面管理验证完成');
});

// ========================================
// 场景 3: 组件管理
// ========================================
test('Step 3: 组件管理 - 注册/配置/属性/事件/样式', async ({ page }) => {
  await helper.logStep('【场景 3】组件管理');

  await helper.navigate('http://localhost:3000/builder/component');

  await helper.showPrompt(
    '🧱 组件管理验证',
    `请验证以下功能：

    1️⃣ 组件库列表（基础组件/业务组件/布局组件/图表组件）
    2️⃣ 组件注册（名称/类型/图标/属性 Schema/事件定义）
    3️⃣ 组件属性编辑面板（各属性类型：文本/数字/颜色/选择/图片）
    4️⃣ 组件事件绑定（点击事件/数据变更事件→执行动作/调用API）
    5️⃣ 组件样式编辑（内联样式/CSS类/自定义CSS）
    6️⃣ 组件数据绑定（静态数据/API数据/上下文变量）
    7️⃣ 组件预览（单组件独立预览/不同状态预览）

    ⚠️ 验证要点：
    - 属性 Schema 校验
    - 事件循环引用检测
    - 组件热更新（修改后立即生效无需刷新）

    完成后请点击 ✅ 确认`
  );

  await helper.takeScreenshot('36-03-component');
  await helper.logStep('✅ 组件管理验证完成');
});

// ========================================
// 场景 4: 区块与模板
// ========================================
test('Step 4: 区块库 + 页面模板 + 站点模板', async ({ page }) => {
  await helper.logStep('【场景 4】区块与模板');

  await helper.navigate('http://localhost:3000/builder/block');

  await helper.showPrompt(
    '📐 区块与模板验证',
    `请验证以下功能：

    【区块 Block】
    1️⃣ 预制区块列表（Banner/导航/页脚/侧栏/卡片等）
    2️⃣ 自定义区块保存（选中多个组件→保存为区块）
    3️⃣ 区块复用（拖拽区块到页面→展开为组件组）
    4️⃣ 区块编辑/删除

    【页面模板 PageTemplate】
    5️⃣ 模板市场（官方/社区模板浏览）
    6️⃣ 从页面创建模板
    7️⃣ 应用模板到新页面
    8️⃣ 模板分享/导出

    【站点模板 SiteTemplate】
    9️⃣ 站点模板列表（行业模板：电商/官网/博客/后台）
    🔟 一键建站（选择站点模板→配置→自动创建全套页面）
    1️⃣1️⃣ 主题切换（同一站点切换不同视觉主题）

    完成后请点击 ✅ 确认`
  );

  await helper.takeScreenshot('36-04-block-template');
  await helper.logStep('✅ 区块与模板验证完成');
});

// ========================================
// 场景 5: 内容集合与数据源
// ========================================
test('Step 5: 内容集合 + 数据源管理', async ({ page }) => {
  await helper.logStep('【场景 5】集合与数据源');

  await helper.navigate('http://localhost:3000/builder/collection');

  await helper.showPrompt(
    '📊 内容集合与数据源验证',
    `请验证以下功能：

    【内容集合 Collection】
    1️⃣ 定义数据模型（字段名/类型/必填/默认值/关联关系）
    2️⃣ 集合数据 CRUD（新增/编辑/删除/列表/排序/筛选）
    3️⃣ 集合 API 自动生成（RESTful 端点自动创建）
    4️⃣ 关联查询（A 集合关联 B 集合的数据查询）
    5️⃣ 集合数据导入/导出（CSV/JSON）

    【数据源 DataSource】
    6️⃣ API 数据源（配置外部 API URL/参数/转换规则）
    7️⃣ 数据库数据源（直连查询/SQL编辑器）
    8️⃣ 静态数据源（JSON/CSV 手动编辑）
    9️⃣ 数据源绑定到组件（选择数据源→映射字段→预览数据）
    🔟 数据刷新策略（实时/定时/手动）

    完成后请点击 ✅ 确认`
  );

  await helper.takeScreenshot('36-05-collection-datasource');
  await helper.logStep('✅ 集合与数据源验证完成');
});

// ========================================
// 场景 6: 媒体库管理
// ========================================
test('Step 6: 媒体库 - 上传/管理/CDN', async ({ page }) => {
  await helper.logStep('【场景 6】媒体库');

  await helper.navigate('http://localhost:3000/builder/media');

  await helper.showPrompt(
    '🖼️ 媒体库管理验证',
    `请验证以下功能：

    1️⃣ 媒体文件列表（图片/视频/文档/按文件夹组织）
    2️⃣ 上传文件（拖拽上传/批量上传/格式限制/大小限制）
    3️⃣ 文件预览（图片缩略图/视频播放/PDF 预览）
    4️⃣ 文件编辑（裁剪/旋转/调尺寸/添加水印）
    5️⃣ 文件夹管理（创建/重命名/移动/删除）
    6️⃣ CDN 配置（加速域名/缓存策略/回源规则）
    7️⃣ 存储统计（总用量/按类型/按文件夹/清理建议）

    ⚠️ 边界测试：
    - 超大文件上传（100MB+）
    - 不支持的文件格式
    - 文件名特殊字符/超长文件名
    - 并发上传多个文件

    完成后请点击 ✅ 确认`
  );

  await helper.takeScreenshot('36-06-media');
  await helper.logStep('✅ 媒体库验证完成');
});

// ========================================
// 场景 7: 预览与多端适配
// ========================================
test('Step 7: 预览 - 实时/多端/响应式/暗黑模式', async ({ page }) => {
  await helper.logStep('【场景 7】预览与适配');

  await helper.navigate('http://localhost:3000/builder/preview');

  await helper.showPrompt(
    '👁️ 预览与多端适配验证',
    `请验证以下功能：

    【预览 Preview】
    1️⃣ 实时预览（编辑器中修改→预览区域实时更新）
    2️⃣ 全屏预览（独立窗口完整展示）
    3️⃣ 分享预览链接（生成临时预览 URL/可设密码访问）

    【多端适配 ScreenMatrix】
    4️⃣ 桌面端预览（1920px/1440px/1280px）
    5️⃣ 平板端预览（1024px/768px）
    6️⃣ 手机端预览（375px/414px）
    7️⃣ 大屏/数据看板预览（2560px/4K）
    8️⃣ 响应式断点配置（不同断点显示/隐藏组件）

    【主题 Theme】
    9️⃣ 亮色/暗色模式切换
    🔟 自定义主题变量（颜色/字体/间距/圆角/阴影）
    1️⃣1️⃣ 主题实时预览（切换主题后所有组件即时更新样式）

    完成后请点击 ✅ 确认`
  );

  await helper.takeScreenshot('36-07-preview');
  await helper.logStep('✅ 预览与适配验证完成');
});

// ========================================
// 场景 8: 发布管理
// ========================================
test('Step 8: 发布管理 - 发布/记录/审核/回滚/SSG', async ({ page }) => {
  await helper.logStep('【场景 8】发布管理');

  await helper.navigate('http://localhost:3000/builder/publish');

  await helper.showPrompt(
    '🚀 发布管理验证',
    `请验证以下功能：

    【发布 Publish】
    1️⃣ 发布站点（选择环境：预发布/生产→确认→发布）
    2️⃣ 局部发布（只发布变更的页面）
    3️⃣ 发布审核流程（提交审核→审核通过→自动发布）

    【发布记录 PublishRecord】
    4️⃣ 发布记录列表（版本/环境/时间/状态/操作者/变更说明）
    5️⃣ 版本对比（两个版本间的差异）
    6️⃣ 回滚到指定版本

    【静态生成 SSG】
    7️⃣ 触发 SSG 构建（全量/增量）
    8️⃣ 构建进度与日志
    9️⃣ 构建产物预览
    🔟 部署到 CDN

    完成后请点击 ✅ 确认`
  );

  await helper.takeScreenshot('36-08-publish');
  await helper.logStep('✅ 发布管理验证完成');
});

// ========================================
// 场景 9: Builder 协作权限
// ========================================
test('Step 9: Builder 协作权限 - 多人协作/角色/审计', async ({ page }) => {
  await helper.logStep('【场景 9】协作权限');

  await helper.navigate('http://localhost:3000/builder/permission');

  await helper.showPrompt(
    '🤝 Builder 协作权限验证',
    `请验证以下功能：

    【协作权限 Permission】
    1️⃣ 协作者列表（用户/角色/权限级别/邀请时间）
    2️⃣ 邀请协作者（邮箱/选择角色：管理员/编辑者/查看者）
    3️⃣ 角色权限矩阵（管理员所有操作/编辑者不能发布/查看者只读）
    4️⃣ 移除协作者
    5️⃣ 权限继承（站点权限覆盖到子页面）

    【审计 Audit】
    6️⃣ 操作日志（谁/何时/修改了什么页面/什么组件）
    7️⃣ 变更追踪（每次保存的变更详情）
    8️⃣ 内容审核日志（审核结果/审核意见/修改记录）

    【分析 Analytics】
    9️⃣ 页面 PV/UV 统计
    🔟 用户行为热力图
    1️⃣1️⃣ 停留时间分析
    1️⃣2️⃣ 页面转化漏斗

    完成后请点击 ✅ 确认`
  );

  await helper.takeScreenshot('36-09-permission-audit');
  await helper.logStep('✅ 协作权限验证完成');
});

// ========================================
// 场景 10: CMS 内容管理
// ========================================
test('Step 10: CMS 模块 - 上传/门户/管理/认证', async ({ page }) => {
  await helper.logStep('【场景 10】CMS 内容管理');

  await helper.navigate('http://localhost:3000/content/portal');

  await helper.showPrompt(
    '📰 CMS 内容管理验证',
    `请验证以下功能：

    【文件上传 Upload】
    1️⃣ 文件上传接口（图片/视频/文档/格式校验/大小限制）
    2️⃣ 批量上传支持
    3️⃣ 分片上传（大文件分片+断点续传）

    【门户内容 Portal/PortalAdmin】
    4️⃣ 门户首页内容配置（Banner轮播/公告/推荐内容）
    5️⃣ 文章列表管理（分类/标签/置顶/推荐/排序）
    6️⃣ 文章详情编辑（富文本编辑器/图片插入/视频嵌入）
    7️⃣ 文章审核流程（草稿→提交审核→通过发布/驳回修改）
    8️⃣ 评论管理（审核/删除/举报处理）

    【CMS 权限 Auth】
    9️⃣ 内容管理角色（编辑/审核/管理员权限分离）
    🔟 内容发布审批流

    完成后请点击 ✅ 确认`
  );

  await helper.takeScreenshot('36-10-cms');
  await helper.logStep('✅ CMS 内容管理验证完成');
});
