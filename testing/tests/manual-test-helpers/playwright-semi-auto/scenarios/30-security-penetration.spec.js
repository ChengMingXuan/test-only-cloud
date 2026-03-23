/**
 * 安全渗透测试场景 - 30
 * 
 * 对应企业测试方案 3.5 章节「非功能测试」安全部分
 * 
 * 覆盖维度：
 * ✅ XSS（反射型/存储型/DOM）
 * ✅ SQL注入探测
 * ✅ CSRF 防护验证
 * ✅ 认证/授权绕过
 * ✅ 敏感数据暴露
 * ✅ 接口权限验证
 * ✅ CORS 策略
 * ✅ HTTP 安全头
 * ✅ 信息泄露
 * ✅ 文件上传安全
 * 
 * 按步骤：
 *   Step 1: XSS 注入测试
 *   Step 2: SQL 注入探测
 *   Step 3: 认证安全测试
 *   Step 4: 授权绕过测试
 *   Step 5: 敏感数据暴露
 *   Step 6: HTTP 安全头与 CORS
 *   Step 7: 文件上传安全
 * 
 * 总耗时：约 30 分钟
 * 难度：HIGH（需要安全测试知识）
 */

const { test, expect } = require('@playwright/test');
const { SemiAutoHelper } = require('../helpers/semi-auto-helper');
const { TestData } = require('../helpers/test-data');

let helper;

test.beforeEach(async ({ page }) => {
  helper = new SemiAutoHelper(page);
  await helper.navigate('http://localhost:3000');
  await helper.login('admin@example.com', 'P@ssw0rd');
  await helper.logStep('✅ 登录成功 - 准备开始安全渗透测试');
});

test.afterEach(async ({ page }) => {
  await helper.generateReport('security-penetration');
});

// ========================================
// 场景 1: XSS 注入测试
// ========================================
test('Step 1: XSS 跨站脚本注入测试', async ({ page }) => {
  await helper.logStep('【场景 1】XSS 注入 - 开始');

  await helper.showPrompt(
    '🛡️ XSS 跨站脚本注入测试',
    `请在各输入框中注入以下 XSS Payload 并验证均被过滤/转义：

    === 反射型 XSS ===
    在搜索框/筛选框中输入以下内容，验证页面不弹窗：

    ① <script>alert('XSS')</script>
    ② <img src=x onerror=alert('XSS')>
    ③ <svg onload=alert('XSS')>
    ④ javascript:alert('XSS')
    ⑤ "><script>alert(document.cookie)</script>

    === 存储型 XSS ===
    在以下输入框保存并查看详情/列表，验证不执行脚本：

    ⑥ 用户名/昵称 → <img src=x onerror=alert(1)>
    ⑦ 设备名称 → <script>alert('XSS')</script>
    ⑧ 工单描述 → <iframe src="javascript:alert('XSS')">
    ⑨ 站点地址 → <body onload=alert('XSS')>
    ⑩ 备注/评论 → <a href="javascript:alert('XSS')">恶意链接</a>

    === DOM XSS ===
    ⑪ URL 参数注入：?name=<script>alert(1)</script>
    ⑫ URL Hash 注入：#<img src=x onerror=alert(1)>
    ⑬ 路由参数注入

    === 验证标准 ===
    - ✅ 不弹窗（表示已过滤/转义）
    - ✅ 内容正确显示为文本（<script> 显示为字符串）
    - ❌ 弹窗 = XSS 漏洞
    - ❌ 页面为空/报错 = 处理不当但无 XSS

    完成后请点击 ✅ 确认`
  );

  await helper.takeScreenshot('30-01-xss-injection');
  await helper.logStep('✅ XSS 注入测试完成');
});

// ========================================
// 场景 2: SQL 注入探测
// ========================================
test('Step 2: SQL 注入探测测试', async ({ page }) => {
  await helper.logStep('【场景 2】SQL 注入 - 开始');

  await helper.showPrompt(
    '🛡️ SQL 注入探测测试',
    `请在各搜索/查询框中输入以下 SQL 注入 Payload：

    === 基础注入 ===
    ① ' OR '1'='1
    ② ' OR 1=1 --
    ③ ' UNION SELECT NULL --
    ④ '; DROP TABLE users --
    ⑤ 1' AND '1'='1

    === 时间盲注 ===
    ⑥ ' OR SLEEP(5) --    （如果响应延迟5秒=漏洞）
    ⑦ ' OR pg_sleep(5) -- （PostgreSQL版本）

    === 测试位置 ===
    ⑧ 用户列表搜索框
    ⑨ 设备列表搜索框
    ⑩ 工单搜索框
    ⑪ 订单编号搜索框
    ⑫ 日志查询关键词
    ⑬ URL 查询参数 ?id=1' OR 1=1

    === API 参数注入 ===
    ⑭ 通过浏览器开发者工具修改请求参数
    ⑮ 在排序字段注入：sortBy=name; DROP TABLE--
    ⑯ 在分页参数注入：page=1; DROP TABLE--

    === 验证标准 ===
    - ✅ 返回空结果或报错"无效输入" = 安全
    - ✅ 返回正常搜索结果（将注入当作搜索词）= 安全
    - ❌ 返回全部数据（OR 1=1 生效）= SQL 注入漏洞
    - ❌ 响应延迟（SLEEP生效）= 盲注漏洞
    - ❌ 暴露数据库错误信息 = 信息泄露

    完成后请点击 ✅ 确认`
  );

  await helper.takeScreenshot('30-02-sql-injection');
  await helper.logStep('✅ SQL 注入探测测试完成');
});

// ========================================
// 场景 3: 认证安全测试
// ========================================
test('Step 3: 认证安全测试', async ({ page }) => {
  await helper.logStep('【场景 3】认证安全 - 开始');

  await helper.showPrompt(
    '🔐 认证安全测试',
    `请验证以下认证安全机制：

    === 密码策略 ===
    ① 弱密码（123456 / password / admin）→ 应拒绝
    ② 纯数字密码 → 应拒绝
    ③ 短密码（<8字符）→ 应拒绝
    ④ 密码不含大写字母 → 是否有策略要求
    ⑤ 历史密码重复 → 是否禁止使用最近N个密码

    === 登录安全 ===
    ⑥ 多次错误密码（>5次）→ 应锁定账号/较长间隔
    ⑦ 锁定后正确密码 → 仍应拒绝（锁定期内）
    ⑧ 登录成功后 → Cookie 是否设. HttpOnly + Secure
    ⑨ JWT Token → 是否有合理过期时间
    ⑩ 退出登录后 → Token 是否立即失效

    === 会话管理 ===
    ⑪ 长时间不操作 → 自动退出（会话超时）
    ⑫ 多设备登录/单设备登录策略
    ⑬ 密码修改后 → 已有Session全部失效
    ⑭ 并发登录限制

    === 密码重置 ===
    ⑮ 重置链接有效期（不应>24小时）
    ⑯ 重置链接一次性使用
    ⑰ 重置密码后旧密码不能登录
    ⑱ 暴力枚举用户名 → 不应区分"用户不存在"和"密码错误"

    === MFA 多因素认证 ===
    ⑲ 启用MFA → 登录需要二次验证
    ⑳ 验证码超时 → 需重新获取
    ○21 错误验证码 → 失败计数和限制

    完成后请点击 ✅ 确认`
  );

  await helper.takeScreenshot('30-03-authentication-security');
  await helper.logStep('✅ 认证安全测试完成');
});

// ========================================
// 场景 4: 授权绕过测试
// ========================================
test('Step 4: 授权绕过测试', async ({ page }) => {
  await helper.logStep('【场景 4】授权绕过 - 开始');

  await helper.showPrompt(
    '🔓 授权绕过测试',
    `请验证以下授权绕过场景（建议使用浏览器开发者工具）：

    === API 直接访问 ===
    ① 无 Token → 访问 /api/users → 应 401
    ② 过期 Token → 访问任意 API → 应 401
    ③ 低权限 Token → 访问管理 API → 应 403
    ④ 修改 Token 中的角色信息 → 应验证失败

    === 参数篡改 ===
    ⑤ 修改请求中的 user_id → 不应访问他人数据
    ⑥ 修改请求中的 tenant_id → 不应跨租户
    ⑦ 修改请求中的 role → 不应提升权限
    ⑧ 枚举其他资源 ID → 不应泄露数据

    === 路径遍历 ===
    ⑨ /api/users/../admin/config → 不应访问
    ⑩ /api/../../../etc/passwd → 不应泄露文件
    ⑪ 文件下载路径 → 目录遍历 ../../

    === 功能级授权 ===
    ⑫ 隐藏的管理端点（如 /api/debug /api/actuator）→ 应受保护或不存在
    ⑬ 批量操作接口 → 逐条验证权限（非仅验证第一条）
    ⑭ 只读角色 → DELETE/PUT 方法 → API 层拒绝

    === IDOR（不安全的直接对象引用）===
    ⑮ 修改 URL 中的 ID → /orders/12345 改为 /orders/12346
    ⑯ 查看他人订单详情 → 应 403 或 404
    ⑰ 修改他人配置 → 应被拒绝

    完成后请点击 ✅ 确认`
  );

  await helper.takeScreenshot('30-04-authorization-bypass');
  await helper.logStep('✅ 授权绕过测试完成');
});

// ========================================
// 场景 5: 敏感数据暴露
// ========================================
test('Step 5: 敏感数据暴露检查', async ({ page }) => {
  await helper.logStep('【场景 5】数据暴露 - 开始');

  await helper.showPrompt(
    '🔎 敏感数据暴露检查',
    `请检查以下敏感数据暴露风险：

    === 前端暴露 ===
    ① 前端代码（F12 Sources）→ 不应包含：
       - API 密钥
       - 数据库连接字符串
       - 密码/Token
       - 内部 IP 地址
    ② 前端 console → 不应输出调试信息
    ③ 前端 Network → 响应不应包含不必要的内部字段
    ④ 前端产物 → 不应包含 .map 源码映射（生产环境）

    === API 响应 ===
    ⑤ 用户列表 API → 不应返回密码哈希
    ⑥ 用户详情 API → 手机号/身份证应脱敏
    ⑦ 错误响应 → 不应暴露堆栈信息
    ⑧ 404 页面 → 不应暴露技术栈版本

    === HTTP 头暴露 ===
    ⑨ Server 头不应暴露版本（如 Kestrel/5.x）
    ⑩ X-Powered-By 头不应存在
    ⑪ 错误页面不应暴露 .NET 版本

    === 数据传输 ===
    ⑫ 登录请求密码 → HTTPS 加密传输
    ⑬ Token 传输 → 不在 URL 中（应在 Header）
    ⑭ 敏感操作 → 不使用 GET 请求（如删除）

    === 日志暴露 ===
    ⑮ 前端日志不含用户敏感信息
    ⑯ 后端日志不含密码/Token 明文

    完成后请点击 ✅ 确认`
  );

  await helper.takeScreenshot('30-05-sensitive-data-exposure');
  await helper.logStep('✅ 敏感数据暴露检查完成');
});

// ========================================
// 场景 6: HTTP 安全头与 CORS
// ========================================
test('Step 6: HTTP 安全头与 CORS 策略验证', async ({ page }) => {
  await helper.logStep('【场景 6】安全头/CORS - 开始');

  await helper.showPrompt(
    '🌐 HTTP 安全头与 CORS 验证',
    `请在浏览器开发者工具 Network 面板检查以下响应头：

    === 必须存在的安全头 ===
    ① X-Content-Type-Options: nosniff → 防止 MIME 嗅探
    ② X-Frame-Options: DENY 或 SAMEORIGIN → 防止点击劫持
    ③ X-XSS-Protection: 1; mode=block → XSS 过滤
    ④ Strict-Transport-Security → HTTPS 强制（生产环境）
    ⑤ Content-Security-Policy → CSP 策略（至少有基本策略）
    ⑥ Referrer-Policy → 控制引荐信息泄露

    === 不应存在的头 ===
    ⑦ Server: 不应暴露具体版本
    ⑧ X-Powered-By: 应移除
    ⑨ X-AspNetCore-Version: 应移除

    === CORS 策略 ===
    ⑩ 验证 Access-Control-Allow-Origin → 不应为 *
    ⑪ 验证允许的 Methods
    ⑫ 验证允许的 Headers
    ⑬ 从非允许域发送请求 → 应被 CORS 拒绝
    ⑭ 预检请求（OPTIONS）→ 返回正确的 CORS 头

    === CSRF 防护 ===
    ⑮ 状态修改请求（POST/PUT/DELETE）→ 需要 CSRF Token 或验证
    ⑯ 从第三方页面提交表单 → 应被拒绝
    ⑰ Cookie → SameSite 属性设置

    完成后请点击 ✅ 确认`
  );

  await helper.takeScreenshot('30-06-security-headers-cors');
  await helper.logStep('✅ HTTP 安全头与 CORS 验证完成');
});

// ========================================
// 场景 7: 文件上传安全
// ========================================
test('Step 7: 文件上传安全测试', async ({ page }) => {
  await helper.logStep('【场景 7】上传安全 - 开始');

  await helper.showPrompt(
    '📤 文件上传安全测试',
    `请在所有支持文件上传的功能点进行以下安全测试：

    === 文件类型验证 ===
    ① 上传 .exe 文件 → 应被拒绝
    ② 上传 .bat/.cmd/.ps1 文件 → 应被拒绝
    ③ 上传 .php/.jsp/.aspx 文件 → 应被拒绝
    ④ 改扩展名的 .exe → .jpg → 应基于 Magic Bytes 检测拒绝
    ⑤ 双扩展名 file.jpg.exe → 应被拒绝

    === 文件内容验证 ===
    ⑥ 含恶意脚本的 SVG 文件 → 不应执行脚本
    ⑦ 含宏的 Excel 文件(.xlsm) → 应有提示或拒绝
    ⑧ Polyglot 文件（既是 JPG 又是 HTML）→ 下载后内容类型正确

    === 存储安全 ===
    ⑨ 上传文件名含路径穿越 ../../etc/passwd → 不应覆盖系统文件
    ⑩ 上传文件名含特殊字符 <>&; → 存储/展示安全
    ⑪ 上传路径不可被枚举猜测
    ⑫ 上传文件不可通过直接 URL 执行

    === 大小限制 ===
    ⑬ 超大文件（>上限）→ 应拒绝并提示
    ⑭ 零字节文件 → 应拒绝
    ⑮ 大量小文件连续上传 → 不应造成服务器资源耗尽

    === 下载安全 ===
    ⑯ Content-Disposition → 强制下载不在浏览器直接执行
    ⑰ 下载链接 → 应验证权限（不能通过URL直接下载他人文件）
    ⑱ 临时下载链接 → 应有过期时间

    完成后请点击 ✅ 确认`
  );

  await helper.takeScreenshot('30-07-file-upload-security');
  await helper.logStep('✅ 文件上传安全测试完成');
});
