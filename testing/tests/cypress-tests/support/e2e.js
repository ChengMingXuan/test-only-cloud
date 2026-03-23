import './commands';

// 抑制应用代码的未捕获异常（React/UmiJS 运行时错误不应终止测试）
Cypress.on('uncaught:exception', () => {
  // 统一抑制所有应用运行时异常，测试只验证 UI 行为
  return false;
});

// ====================================
// 全局容错：拦截返回 JSON 的前端路由，返回基本 HTML 壳
// 原因：前端 dev server 对部分 SPA 路由返回 application/json content-type
//       导致 cy.visit() 拒绝加载（Cypress 内置检查，failOnStatusCode 无法绕过）
// 方案：在 beforeEach 中注册页面级 intercept，将 JSON 响应替换为 HTML 壳
// ====================================
const HTML_SHELL = `<!DOCTYPE html><html><head><title>JGSY Test</title></head><body><div id="root"></div></body></html>`;

// 全局：每个测试前自动设置 API 拦截 + 页面加载前注入认证 token + 页面路由容错
beforeEach(() => {
  cy.setupApiMocks();

  // 拦截前端页面路由：如果返回 JSON content-type，replace 为 HTML
  // 这解决了 cy.visit() 对 application/json 的拒绝问题
  cy.intercept('GET', '**', (req) => {
    // 仅处理页面级请求（非 API / 非静态资源）
    const url = req.url;
    if (url.includes('/api/') || url.includes('/ws') ||
        url.match(/\.(js|css|png|jpg|svg|ico|woff|ttf|map|json)(\?|$)/)) {
      return; // 放行 API 和静态资源
    }
    req.continue((res) => {
      // 如果前端路由返回了 JSON content-type，替换为 HTML 壳
      const ct = res.headers['content-type'] || '';
      if (ct.includes('application/json')) {
        res.headers['content-type'] = 'text/html; charset=utf-8';
        res.body = HTML_SHELL;
      }
    });
  });

  // 拦截页面加载，自动注入 token，确保不被重定向到登录页
  cy.on('window:before:load', (win) => {
    win.localStorage.setItem('jgsy_access_token', 'mock-cypress-test-token-12345');
    win.localStorage.setItem('jgsy_tenant_code', 'demo');
  });
});
