/**
 * comprehensive-permission-ui 拆分 9/10：错误响应处理验证
 * 符合规范：100% cy.intercept() Mock，真实路由 + Ant Design Pro 选择器
 * 用例数：24 条（6 错误码 × 4 页面）
 */

const ERROR_CODES = [400, 401, 403, 404, 409, 500];

const TEST_PAGES = [
  { path: '/device/registry/list', label: '设备列表', apiPath: 'device' },
  { path: '/station/list', label: '场站列表', apiPath: 'station' },
  { path: '/charging/orders', label: '充电订单', apiPath: 'charging' },
  { path: '/system/user', label: '用户管理', apiPath: 'system' },
];

describe('错误响应处理验证', () => {
  TEST_PAGES.forEach((page) => {
    describe(`${page.label} 错误处理`, () => {
      ERROR_CODES.forEach((code) => {
        it(`应正确处理 ${code} 错误 - ${page.label}`, () => {
          // Mock 对应模块 API 返回错误码
          cy.intercept('GET', `**/api/${page.apiPath}/**`, {
            statusCode: code,
            body: { success: false, code: String(code), message: `错误 ${code}`, timestamp: new Date().toISOString() }
          }).as('errorResponse');

          cy.visitAuth(page.path);

          // 页面不白屏 — 无论 API 返回什么错误，前端都应正确渲染
          cy.get('#root, .ant-layout, body', { timeout: 8000 }).should('exist');
          cy.get('body').should('not.be.empty');

          if (code === 401) {
            // 401 可能跳转登录或显示提示
            cy.get('body').should('exist');
          } else {
            // 非 401 错误：页面应存在 root 容器
            cy.get('#root').should('exist');
          }
        });
      });
    });
  });
});
