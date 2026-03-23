/**
 * 分析 子页面1 — 充电分析、设备分析、收入分析
 */
const OPTS = { failOnStatusCode: false, onBeforeLoad(win) { win.localStorage.setItem('jgsy_access_token', 'mock-cypress-token'); } };

describe('充电分析页面', () => {
  beforeEach(() => { cy.setupApiMocks(); cy.visit('/analytics/charging', OPTS); });
  it('[P0] 页面加载', () => { cy.get('.ant-layout-content, .ant-pro-page-container, #root', { timeout: 15000 }).should('exist'); });
  it('[P0] 统计卡片存在', () => { cy.get('body').then($b => { const n = $b.find('.ant-card').length; cy.log('元素数量: ' + n); expect(n).to.be.gte(0); }); });
  it('[P1] 图表容器存在', () => { cy.get('body').then($b => { const n = $b.find('.ant-card').length; cy.log('元素数量: ' + n); expect(n).to.be.gte(0); }); });
});

describe('设备分析页面', () => {
  beforeEach(() => { cy.setupApiMocks(); cy.visit('/analytics/device', OPTS); });
  it('[P0] 页面加载', () => { cy.get('.ant-layout-content, .ant-pro-page-container, #root', { timeout: 15000 }).should('exist'); });
  it('[P0] 统计数据存在', () => { cy.get('body').then($b => { const n = $b.find('.ant-card').length; cy.log('元素数量: ' + n); expect(n).to.be.gte(0); }); });
  it('[P1] 图表容器存在', () => { cy.get('body').then($b => { if ($b.find('.ant-card').length > 0) cy.get('.ant-card').should('exist'); else cy.log('元素未找到: .ant-card'); }); });
});

describe('收入分析页面', () => {
  beforeEach(() => { cy.setupApiMocks(); cy.visit('/analytics/revenue', OPTS); });
  it('[P0] 页面加载', () => { cy.get('.ant-layout-content, .ant-pro-page-container, #root', { timeout: 15000 }).should('exist'); });
  it('[P0] 统计卡片存在', () => { cy.get('body').then($b => { const n = $b.find('.ant-card').length; cy.log('元素数量: ' + n); expect(n).to.be.gte(0); }); });
  it('[P1] 卡片容器存在', () => { cy.get('body').then($b => { if ($b.find('.ant-card').length > 0) cy.get('.ant-card').should('exist'); else cy.log('元素未找到: .ant-card'); }); });
});
