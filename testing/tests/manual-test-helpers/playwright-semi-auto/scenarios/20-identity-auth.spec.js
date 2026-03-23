/**
 * 身份认证与用户安全测试场景 - 20
 * 
 * 覆盖模块：
 * ✅ JGSY.AGI.Identity - Auth（登录/登出/Token刷新）
 * ✅ JGSY.AGI.Identity - AuthConfig（认证配置）
 * ✅ JGSY.AGI.Identity - MobileAuth（移动端认证）
 * ✅ JGSY.AGI.Identity - MiniProgramAuth（小程序认证）
 * ✅ JGSY.AGI.Identity - MFA（多因素认证）
 * ✅ JGSY.AGI.Identity - PasswordReset（密码重置）
 * ✅ JGSY.AGI.Identity - OAuth（第三方登录）
 * ✅ JGSY.AGI.Identity - MultiLogin（多端登录管理）
 * ✅ JGSY.AGI.Identity - User（用户资料/密码修改）
 * ✅ JGSY.AGI.Identity - UserManage（后台管理）
 * ✅ JGSY.AGI.Identity - UserTag/Stats/Join/Excel（标签/统计/加入/导入导出）
 * ✅ JGSY.AGI.Identity - Department（部门管理全套）
 * ✅ JGSY.AGI.Identity - IpBlacklist（IP黑名单）
 * ✅ JGSY.AGI.Identity - SensitiveWord（敏感词）
 * ✅ JGSY.AGI.Identity - SecurityAudit（安全审计）
 * ✅ JGSY.AGI.Identity - RealNameAuth（实名认证）
 * ✅ JGSY.AGI.Identity - DataMasking（数据脱敏）
 * ✅ JGSY.AGI.Identity - NotificationSettings（通知设置）
 * ✅ JGSY.AGI.Identity - LoginLogManage（登录日志管理）
 * 
 * 测试步骤：8 个核心场景
 * 总耗时：约 40 分钟
 * 难度：HIGH（涉及安全/认证/多端交互）
 */

const { test, expect } = require('@playwright/test');
const { SemiAutoHelper } = require('../helpers/semi-auto-helper');
const { TestData } = require('../helpers/test-data');

let helper;

test.beforeEach(async ({ page }) => {
  helper = new SemiAutoHelper(page);
  await helper.navigate('http://localhost:3000');
  await helper.logStep('准备开始身份认证与用户安全测试');
});

test.afterEach(async ({ page }) => {
  await helper.generateReport('identity-auth');
});

// ========================================
// 场景 1: 登录认证全流程
// ========================================
test('Step 1: 登录/登出/Token刷新/登录日志', async ({ page }) => {
  await helper.logStep('【场景 1】登录认证全流程 - 开始');

  await helper.showPrompt(
    '🔐 登录认证全流程验证',
    `请验证以下流程：

    1️⃣ 正常登录（用户名+密码 → 获取Token → 跳转主页）
    2️⃣ 错误登录（错误密码 → 提示错误 → 不跳转）
    3️⃣ 空输入提交（用户名/密码均为空 → 前端校验）
    4️⃣ 连续错误登录限制（5次后锁定？验证码？）
    5️⃣ Token刷新（Token即将过期 → 自动刷新 → 无感续期）
    6️⃣ 退出登录（清除Token → 跳转登录页）
    7️⃣ 退出后访问受保护页面（应跳转登录页）
    8️⃣ 查看登录日志（IP/设备/时间/结果）

    ⚠️ 安全重点：
    - 密码是否明文传输
    - Token 存储位置安全性
    - 登录日志完整性

    完成后请点击 ✅ 确认`
  );

  await helper.takeScreenshot('20-01-login-flow');
  await helper.logStep('✅ 登录认证验证完成');
});

// ========================================
// 场景 2: 密码管理与MFA
// ========================================
test('Step 2: 密码重置/修改与多因素认证', async ({ page }) => {
  await helper.logStep('【场景 2】密码管理与MFA - 开始');

  await helper.login('admin@example.com', 'P@ssw0rd');

  // 2.1 密码修改
  await helper.navigate('http://localhost:3000/profile/security');

  await helper.showPrompt(
    '🔑 密码管理验证',
    `请验证以下功能：

    1️⃣ 修改密码（旧密码 + 新密码 + 确认新密码）
    2️⃣ 密码强度校验（最小长度/大小写/数字/特殊字符）
    3️⃣ 新旧密码不能相同验证
    4️⃣ 两次输入不一致提醒

    完成后请点击 ✅ 确认`
  );

  // 2.2 密码重置流程
  await helper.showPrompt(
    '📧 密码重置验证',
    `请验证以下忘记密码流程：

    1️⃣ 点击"忘记密码"链接
    2️⃣ 输入注册邮箱/手机
    3️⃣ 获取验证码（邮件/短信）
    4️⃣ 输入验证码 + 新密码
    5️⃣ 重置成功后用新密码登录

    完成后请点击 ✅ 确认`
  );

  // 2.3 MFA多因素
  await helper.showPrompt(
    '🛡️ 多因素认证验证',
    `请验证以下MFA功能：

    1️⃣ 开启MFA（TOTP/短信/邮件）
    2️⃣ 绑定认证器（扫码绑定/手动输入密钥）
    3️⃣ MFA登录（输入动态码）
    4️⃣ 恢复码功能
    5️⃣ 关闭MFA

    完成后请点击 ✅ 确认`
  );

  await helper.takeScreenshot('20-02-password-mfa');
  await helper.logStep('✅ 密码管理与MFA验证完成');
});

// ========================================
// 场景 3: 用户管理后台
// ========================================
test('Step 3: 后台用户管理（创建/编辑/标签/统计/导入导出）', async ({ page }) => {
  await helper.logStep('【场景 3】用户管理后台 - 开始');

  await helper.login('admin@example.com', 'P@ssw0rd');
  await helper.navigate('http://localhost:3000/admin/users');

  await helper.showPrompt(
    '👥 用户管理后台验证',
    `请验证以下功能：

    1️⃣ 用户列表（分页/搜索/筛选/排序）
    2️⃣ 创建用户（所有字段/必填校验/唯一性校验）
    3️⃣ 编辑用户信息
    4️⃣ 启用/禁用用户
    5️⃣ 重置用户密码
    6️⃣ 删除用户

    完成后请点击 ✅ 确认`
  );

  // 3.2 用户标签与统计
  await helper.showPrompt(
    '🏷️ 用户标签与统计',
    `请验证以下功能：

    1️⃣ 用户标签管理（创建/编辑/删除标签）
    2️⃣ 给用户打标签（单个/批量）
    3️⃣ 按标签筛选用户
    4️⃣ 用户统计面板（总数/增长/活跃/留存）
    5️⃣ 用户加入流程管理

    完成后请点击 ✅ 确认`
  );

  // 3.3 批量导入导出
  await helper.showPrompt(
    '📥 用户导入导出验证',
    `请验证以下功能：

    1️⃣ 下载导入模板
    2️⃣ 填写模板数据 → 上传导入
    3️⃣ 导入结果反馈（成功数/失败数/错误明细）
    4️⃣ 导出用户列表为Excel
    5️⃣ 按条件筛选后导出

    完成后请点击 ✅ 确认`
  );

  await helper.takeScreenshot('20-03-user-manage');
  await helper.logStep('✅ 用户管理后台验证完成');
});

// ========================================
// 场景 4: 部门管理
// ========================================
test('Step 4: 组织架构与部门管理', async ({ page }) => {
  await helper.logStep('【场景 4】部门管理 - 开始');

  await helper.login('admin@example.com', 'P@ssw0rd');
  await helper.navigate('http://localhost:3000/admin/departments');

  await helper.showPrompt(
    '🏢 部门管理验证',
    `请验证以下功能：

    1️⃣ 部门树形结构展示
    2️⃣ 创建部门（名称/上级/排序/负责人）
    3️⃣ 编辑部门信息
    4️⃣ 调整层级（拖拽排序/修改上级）
    5️⃣ 部门成员管理（添加/移除成员）
    6️⃣ 部门统计（人数/设备数/在线率等）
    7️⃣ 部门模板管理（创建/使用模板快速建部门）
    8️⃣ 删除部门（验证：有子部门/有成员时提醒）

    ⚠️ 业务逻辑重点：
    - 部门层级不超过N层限制
    - 不能删除含成员的部门
    - 部门编码唯一性

    完成后请点击 ✅ 确认`
  );

  await helper.takeScreenshot('20-04-department');
  await helper.logStep('✅ 部门管理验证完成');
});

// ========================================
// 场景 5: 安全审计与IP黑名单
// ========================================
test('Step 5: 安全审计/IP黑名单/敏感词/通知设置', async ({ page }) => {
  await helper.logStep('【场景 5】安全功能 - 开始');

  await helper.login('admin@example.com', 'P@ssw0rd');

  // 5.1 安全审计
  await helper.navigate('http://localhost:3000/admin/security-audit');

  await helper.showPrompt(
    '🔍 安全审计验证',
    `请验证以下功能：

    1️⃣ 安全事件列表（登录异常/权限变更/数据操作）
    2️⃣ 事件详情查看
    3️⃣ 按时间/类型/用户筛选
    4️⃣ 审计日志导出
    5️⃣ 安全告警配置

    完成后请点击 ✅ 确认`
  );

  // 5.2 IP黑名单
  await helper.navigate('http://localhost:3000/admin/ip-blacklist');

  await helper.showPrompt(
    '🚫 IP黑名单验证',
    `请验证以下功能：

    1️⃣ 黑名单列表查看
    2️⃣ 添加IP到黑名单（单个IP/IP段/CIDR）
    3️⃣ 设置封禁时长（永久/临时）
    4️⃣ 移除黑名单
    5️⃣ 验证黑名单IP无法登录

    完成后请点击 ✅ 确认`
  );

  // 5.3 敏感词管理
  await helper.navigate('http://localhost:3000/admin/sensitive-words');

  await helper.showPrompt(
    '🔤 敏感词管理验证',
    `请验证以下功能：

    1️⃣ 敏感词列表
    2️⃣ 添加敏感词（单个/批量导入）
    3️⃣ 敏感词分类
    4️⃣ 删除敏感词
    5️⃣ 测试敏感词过滤（输入含敏感词文本，验证被拦截/替换）

    完成后请点击 ✅ 确认`
  );

  // 5.4 通知设置
  await helper.navigate('http://localhost:3000/admin/notification-settings');

  await helper.showPrompt(
    '🔔 通知设置验证',
    `请验证以下功能：

    1️⃣ 通知渠道配置（邮件/短信/站内信/微信）
    2️⃣ 通知模板管理
    3️⃣ 通知规则设置
    4️⃣ 测试发送
    5️⃣ 通知开关控制

    完成后请点击 ✅ 确认`
  );

  await helper.takeScreenshot('20-05-security-features');
  await helper.logStep('✅ 安全功能验证完成');
});

// ========================================
// 场景 6: 实名认证与数据脱敏
// ========================================
test('Step 6: 实名认证流程与数据脱敏', async ({ page }) => {
  await helper.logStep('【场景 6】实名认证与脱敏 - 开始');

  await helper.login('admin@example.com', 'P@ssw0rd');

  // 6.1 实名认证
  await helper.navigate('http://localhost:3000/admin/real-name-auth');

  await helper.showPrompt(
    '🪪 实名认证验证',
    `请验证以下流程：

    1️⃣ 实名认证申请列表
    2️⃣ 提交实名认证（姓名/身份证号/照片上传）
    3️⃣ 审核实名认证（通过/驳回）
    4️⃣ 认证状态查看（未认证/审核中/已通过/已驳回）
    5️⃣ 二要素验证（姓名+身份证号比对）

    完成后请点击 ✅ 确认`
  );

  // 6.2 数据脱敏
  await helper.navigate('http://localhost:3000/admin/data-masking');

  await helper.showPrompt(
    '🔒 数据脱敏验证',
    `请验证以下功能：

    1️⃣ 脱敏规则配置（手机号/身份证/银行卡/邮箱）
    2️⃣ 脱敏效果预览
    3️⃣ 不同角色看到不同脱敏级别
    4️⃣ 申请查看原文（审批流程）

    ⚠️ 安全重点：
    - 普通用户必须看到脱敏数据
    - 管理员也应有脱敏（除非特别授权）

    完成后请点击 ✅ 确认`
  );

  await helper.takeScreenshot('20-06-realname-masking');
  await helper.logStep('✅ 实名认证与脱敏验证完成');
});

// ========================================
// 场景 7: 多端登录与OAuth
// ========================================
test('Step 7: 多端登录管理与第三方OAuth', async ({ page }) => {
  await helper.logStep('【场景 7】多端登录与OAuth - 开始');

  await helper.login('admin@example.com', 'P@ssw0rd');

  // 7.1 多端登录
  await helper.showPrompt(
    '📱 多端登录管理验证',
    `请验证以下功能：

    1️⃣ 当前登录会话列表（设备/IP/时间）
    2️⃣ 踢出其他会话
    3️⃣ 设置最大同时在线数
    4️⃣ 新登录挤掉旧登录验证
    5️⃣ 移动端/小程序/Web端同时登录策略

    完成后请点击 ✅ 确认`
  );

  // 7.2 OAuth第三方
  await helper.showPrompt(
    '🔗 OAuth第三方登录验证',
    `请验证以下功能：

    1️⃣ OAuth配置（微信/支付宝/GitHub等）
    2️⃣ 第三方登录按钮展示
    3️⃣ 跳转授权页面
    4️⃣ 授权回调处理
    5️⃣ 账号绑定/解绑
    6️⃣ 首次登录自动注册

    完成后请点击 ✅ 确认`
  );

  await helper.takeScreenshot('20-07-multilogin-oauth');
  await helper.logStep('✅ 多端登录与OAuth验证完成');
});

// ========================================
// 场景 8: 认证配置管理
// ========================================
test('Step 8: 认证策略配置与安全策略', async ({ page }) => {
  await helper.logStep('【场景 8】认证配置管理 - 开始');

  await helper.login('admin@example.com', 'P@ssw0rd');
  await helper.navigate('http://localhost:3000/admin/auth-config');

  await helper.showPrompt(
    '⚙️ 认证策略配置验证',
    `请验证以下配置项：

    1️⃣ 密码策略（最小长度/复杂度/有效期/历史密码不能重用）
    2️⃣ 登录策略（最大失败次数/锁定时长/验证码触发）
    3️⃣ Token策略（有效期/刷新策略/单点登录）
    4️⃣ 会话策略（超时/最大并发/踢出策略）
    5️⃣ 多端认证策略（移动端/小程序/Web差异配置）
    6️⃣ 配置修改后立即生效验证

    ⚠️ 业务逻辑重点：
    - 策略变更不影响已登录用户（或有明确过渡方案）
    - 不合理配置有警告提示

    完成后请点击 ✅ 确认`
  );

  await helper.takeScreenshot('20-08-auth-config');
  await helper.logStep('✅ 认证配置管理验证完成');
});
