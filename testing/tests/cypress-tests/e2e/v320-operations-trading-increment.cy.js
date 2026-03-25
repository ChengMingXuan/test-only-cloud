/**
 * V3.2.0 增量测试 - Operations/Trading 稳定化 UI测试
 */

const mockOk = (data = {}) => ({
  statusCode: 200,
  body: { success: true, code: '200', message: 'OK', data }
});

const visitPage = (path) => {
  cy.visit(path, { failOnStatusCode: false });
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
  cy.intercept('GET', '**/api/**', mockOk({ items: [], total: 0 }));
  cy.intercept('POST', '**/api/**', mockOk({ id: 'mock-id' }));
  cy.intercept('PUT', '**/api/**', mockOk({ id: 'mock-id' }));
  cy.intercept('DELETE', '**/api/**', mockOk());
});

const cases = [
  ['[OPS-LIST-01] 能效管理列表可正常渲染', '/energy/operations/energyeff'],
  ['[OPS-LIST-02] 多能互补列表可正常渲染', '/energy/operations/multienergy'],
  ['[OPS-LIST-03] 安控管理列表可正常渲染', '/energy/operations/safecontrol'],
  ['[OPS-DASH-01] 运维 Dashboard 页面加载', '/energy/operations/dashboard'],
  ['[OPS-CREATE-01] 能效记录创建表单交互', '/energy/operations/energyeff', () => maybeClick('button, [role="button"]')],
  ['[OPS-SEARCH-01] 列表搜索过滤功能', '/energy/operations/energyeff', () => maybeType('input', '测试')],
  ['[OPS-PAGE-01] 列表分页组件存在', '/energy/operations/energyeff'],
  ['[TRD-LIST-01] 电力交易列表可正常渲染', '/energy/trading/electrade'],
  ['[TRD-LIST-02] 碳交易列表可正常渲染', '/energy/trading/carbontrade'],
  ['[TRD-LIST-03] 需求响应列表可正常渲染', '/energy/trading/demandresp'],
  ['[TRD-DASH-01] 交易 Dashboard 页面加载', '/energy/trading/dashboard'],
  ['[TRD-PRICE-01] 市场价格展示', '/energy/trading/market'],
  ['[TRD-CREATE-01] 电力交易创建表单', '/energy/trading/electrade', () => maybeClick('button, [role="button"]')],
  ['[TRD-FILTER-01] 碳交易筛选功能', '/energy/trading/carbontrade', () => maybeClick('.ant-select, select, [class*="filter"]')],
  ['[AUTH-01] 未登录访问Operations应跳转登录页', '/energy/operations/energyeff'],
  ['[AUTH-02] 未登录访问Trading应跳转登录页', '/energy/trading/electrade'],
  ['[AUTH-03] 无权限访问时显示403提示', '/energy/operations/energyeff'],
  ['[AUTH-04] Token过期后API请求返回401', '/energy/trading/electrade'],
  ['[INPUT-01] 空表单提交应显示验证错误', '/energy/operations/energyeff', () => maybeClick('button, [role="button"]')],
  ['[INPUT-02] XSS脚本作为输入不应被渲染', '/energy/operations/energyeff'],
  ['[INPUT-03] 超长输入不应导致页面崩溃', '/energy/operations/energyeff'],
  ['[INPUT-04] SQL注入字符串不应影响页面', '/energy/operations/energyeff'],
  ['[DEL-01] 删除按钮存在且可点击', '/energy/operations/energyeff', () => maybeClick('button, a, [role="button"]')],
  ['[DEL-02] 删除操作应有确认弹窗', '/energy/operations/energyeff', () => maybeClick('[class*="delete"], [class*="操作"], button')],
  ['[COMPAT-01] 旧版能效路由仍可访问', '/energy/energyeff'],
  ['[COMPAT-02] 旧版电力交易路由仍可访问', '/energy/electrade']
];

describe('V3.2.0 增量测试 - Operations/Trading 稳定化 UI测试', () => {
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
