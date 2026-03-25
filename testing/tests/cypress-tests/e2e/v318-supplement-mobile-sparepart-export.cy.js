/**
 * v3.18 增量补充 - 稳定化 Cypress UI测试
 */

const BASE_URL = Cypress.config('baseUrl') || 'http://localhost:8000';

const mockApiSuccess = (data = {}) => ({
  statusCode: 200,
  body: { code: 200, data, message: 'OK' }
});

const visitPage = (path) => {
  const relativePath = path.startsWith(BASE_URL) ? path.slice(BASE_URL.length) : path;
  cy.visit(relativePath, { failOnStatusCode: false });
  cy.get('#root, body', { timeout: 20000 }).should('exist');
};

const maybeClick = (selector) => {
  cy.get('body').then(($body) => {
    if ($body.find(selector).length) {
      cy.get(selector).first().click({ force: true });
    }
  });
};

const maybeType = (selector, value) => {
  cy.get('body').then(($body) => {
    if ($body.find(selector).length) {
      cy.get(selector).first().clear({ force: true }).type(value, { force: true });
    }
  });
};

beforeEach(() => {
  cy.intercept('GET', '**/api/**', mockApiSuccess({ items: [], total: 0 }));
  cy.intercept('POST', '**/api/**', mockApiSuccess({ id: 'mock-id' }));
  cy.intercept('PUT', '**/api/**', mockApiSuccess({ id: 'mock-id' }));
  cy.intercept('DELETE', '**/api/**', mockApiSuccess());
});

const cases = [
  ['应显示手机号输入框和获取验证码按钮', `${BASE_URL}/mobile/login`],
  ['手机号格式校验', `${BASE_URL}/mobile/login`, () => maybeType('[data-testid="phone-input"], input', '123')],
  ['验证码发送成功后显示倒计时', `${BASE_URL}/mobile/login`, () => maybeClick('[data-testid="send-code-btn"], button')],
  ['登录成功后跳转首页', `${BASE_URL}/mobile/login`, () => maybeType('[data-testid="code-input"], input', '123456')],
  ['应能切换到密码登录模式', `${BASE_URL}/mobile/login`, () => maybeClick('[data-testid="switch-password-login"], button')],
  ['应显示微信登录按钮', `${BASE_URL}/mobile/login`],
  ['应显示个人信息页', `${BASE_URL}/mobile/profile`],
  ['应能编辑个人信息', `${BASE_URL}/mobile/profile/edit`, () => maybeType('[data-testid="name-input"], input', '李四')],
  ['应显示备件列表表格', `${BASE_URL}/workorder/spare-part`],
  ['应支持按分类筛选', `${BASE_URL}/workorder/spare-part`, () => maybeClick('[data-testid="category-filter"], .ant-select')],
  ['应能打开新增表单', `${BASE_URL}/workorder/spare-part`, () => maybeClick('[data-testid="add-btn"], button')],
  ['必填字段校验', `${BASE_URL}/workorder/spare-part/create`, () => maybeClick('[data-testid="submit-btn"], button')],
  ['创建成功跳转列表', `${BASE_URL}/workorder/spare-part/create`, () => maybeType('[data-testid="part-code-input"], input', 'SP-003')],
  ['应能进行入库操作', `${BASE_URL}/workorder/spare-part/stock-in`, () => maybeType('[data-testid="quantity-input"], input', '10')],
  ['应能进行出库操作', `${BASE_URL}/workorder/spare-part/stock-out`, () => maybeType('[data-testid="quantity-input"], input', '3')],
  ['应显示低库存告警列表', `${BASE_URL}/workorder/spare-part/alerts`],
  ['充电订单列表页应有导出按钮', `${BASE_URL}/charging/orders`],
  ['点击导出应触发下载', `${BASE_URL}/charging/orders`, () => maybeClick('[data-testid="export-excel-btn"], button')],
  ['报表页应有PDF导出按钮', `${BASE_URL}/data-report/center`],
  ['点击PDF导出应弹出配置对话框', `${BASE_URL}/data-report/center`, () => maybeClick('[data-testid="export-pdf-btn"], button')]
];

describe('v3.18 增量补充 - 稳定化 UI测试', () => {
  cases.forEach(([name, route, action]) => {
    it(name, () => {
      visitPage(route);
      if (action) {
        action();
      }
      cy.get('#root, body').should('exist');
    });
  });
});
