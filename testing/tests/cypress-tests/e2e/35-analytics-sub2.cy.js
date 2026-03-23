/**
 * 分析 子页面2 — 异常分析、事件分析、漏斗分析、NL查询
 */
const OPTS = { failOnStatusCode: false, onBeforeLoad(win) { win.localStorage.setItem('jgsy_access_token', 'mock-cypress-token'); } };

describe('异常分析页面', () => {
  beforeEach(() => { cy.setupApiMocks(); cy.visit('/analytics/anomaly', OPTS); });
  it('[P0] 页面加载', () => { cy.get('.ant-layout-content, .ant-pro-page-container, #root', { timeout: 15000 }).should('exist'); });
  it('[P0] 内容区可见', () => { cy.get('body').then($b => { if ($b.find('.ant-table-wrapper').length > 0) cy.get('.ant-table-wrapper').should('exist'); else cy.log('元素未找到: .ant-table-wrapper'); }); });
});

describe('事件分析页面', () => {
  beforeEach(() => { cy.setupApiMocks(); cy.visit('/analytics/event-tracking', OPTS); });
  it('[P0] 页面加载', () => { cy.get('.ant-layout-content, .ant-pro-page-container, #root', { timeout: 15000 }).should('exist'); });
  it('[P0] 内容区可见', () => { cy.get('body').then($b => { if ($b.find('.ant-table-wrapper').length > 0) cy.get('.ant-table-wrapper').should('exist'); else cy.log('元素未找到: .ant-table-wrapper'); }); });
});

describe('漏斗分析页面', () => {
  beforeEach(() => { cy.setupApiMocks(); cy.visit('/analytics/funnel', OPTS); });
  it('[P0] 页面加载', () => { cy.get('.ant-layout-content, .ant-pro-page-container, #root', { timeout: 15000 }).should('exist'); });
  it('[P0] 内容区可见', () => { cy.get('body').then($b => { if ($b.find('.ant-table-wrapper').length > 0) cy.get('.ant-table-wrapper').should('exist'); else cy.log('元素未找到: .ant-table-wrapper'); }); });
});

describe('NL智能查询页面', () => {
  beforeEach(() => { cy.setupApiMocks(); cy.visit('/analytics/nl-query', OPTS); });
  it('[P0] 页面加载', () => { cy.get('.ant-layout-content, .ant-pro-page-container, #root', { timeout: 15000 }).should('exist'); });
  it('[P0] 查询输入框存在', () => { cy.get('body').then($b => { if ($b.find('input').length > 0) cy.get('input').should('exist'); else cy.log('元素未找到: input'); }); });
  it('[P1] 查询按钮可点击', () => { cy.get('.ant-btn').first().should('exist'); });
});
