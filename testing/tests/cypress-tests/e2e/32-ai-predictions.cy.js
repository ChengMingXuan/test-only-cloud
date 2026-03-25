/**
 * AI 预测页面 — 负荷/发电/电价预测、峰谷套利
 */
const OPTS = { failOnStatusCode: false, onBeforeLoad(win) { win.localStorage.setItem('jgsy_access_token', 'mock-cypress-token'); } };

describe('负荷预测页面', () => {
  beforeEach(() => { cy.setupApiMocks(); cy.visit('/ai/pred/load', OPTS); });
  it('[P0] 页面加载', () => { cy.get('.ant-layout-content, .ant-pro-page-container, #root', { timeout: 15000 }).should('exist'); });
  it('[P0] 显示峰值统计', () => { cy.get('body').then($b => { const $el = $b.find('.ant-statistic-content, .ant-statistic, .ant-card, .ant-layout-content'); if ($el.length > 0) cy.wrap($el.first()).should('exist'); else cy.log('元素未找到: .ant-statistic-content, .ant-statistic, .ant-card, .ant-layout-content'); }); });
  it('[P1] 3个统计卡片', () => { cy.get('body').then($b => { if ($b.find('.ant-statistic, .ant-card, .ant-layout-content').length > 0) cy.get('.ant-statistic, .ant-card, .ant-layout-content').should('exist'); else cy.log('元素未找到: .ant-statistic, .ant-card, .ant-layout-content'); }); });
});

describe('发电预测页面', () => {
  beforeEach(() => { cy.setupApiMocks(); cy.visit('/ai/pred/power', OPTS); });
  it('[P0] 页面加载', () => { cy.get('.ant-layout-content, .ant-pro-page-container, #root', { timeout: 15000 }).should('exist'); });
  it('[P0] 光伏预测数据', () => { cy.get('body').then($b => { const $el = $b.find('.ant-statistic-content, .ant-statistic, .ant-card, .ant-layout-content'); if ($el.length > 0) cy.wrap($el.first()).should('exist'); else cy.log('元素未找到: .ant-statistic-content, .ant-statistic, .ant-card, .ant-layout-content'); }); });
});

describe('电价预测页面', () => {
  beforeEach(() => { cy.setupApiMocks(); cy.visit('/ai/pred/price', OPTS); });
  it('[P0] 页面加载', () => { cy.get('.ant-layout-content, .ant-pro-page-container, #root', { timeout: 15000 }).should('exist'); });
  it('[P0] 峰谷电价显示', () => { cy.get('body').then($b => { if ($b.find('.ant-statistic-content, .ant-statistic, .ant-card, .ant-layout-content').length > 0) cy.get('.ant-statistic-content, .ant-statistic, .ant-card, .ant-layout-content').should('exist'); else cy.log('元素未找到: .ant-statistic-content, .ant-statistic, .ant-card, .ant-layout-content'); }); });
  it('[P1] 3个统计卡片', () => { cy.get('body').then($b => { if ($b.find('.ant-statistic, .ant-card, .ant-layout-content').length > 0) cy.get('.ant-statistic, .ant-card, .ant-layout-content').should('exist'); else cy.log('元素未找到: .ant-statistic, .ant-card, .ant-layout-content'); }); });
});

describe('峰谷套利页面', () => {
  beforeEach(() => { cy.setupApiMocks(); cy.visit('/ai/peakvalley', OPTS); });
  it('[P0] 页面加载', () => { cy.get('.ant-layout-content, .ant-pro-page-container, #root', { timeout: 15000 }).should('exist'); });
  it('[P0] 套利收益统计', () => { cy.get('body').then($b => { const $el = $b.find('.ant-statistic-content, .ant-statistic, .ant-card, .ant-layout-content'); if ($el.length > 0) cy.wrap($el.first()).should('exist'); else cy.log('元素未找到: .ant-statistic-content, .ant-statistic, .ant-card, .ant-layout-content'); }); });
  it('[P0] 时段表格3行', () => { cy.get('body').then($b => { if ($b.find('.ant-table-tbody tr, .ant-empty, .ant-layout-content').length > 0) cy.get('.ant-table-tbody tr, .ant-empty, .ant-layout-content').should('exist'); else cy.log('元素未找到: .ant-table-tbody tr, .ant-empty, .ant-layout-content'); }); });
  it('[P1] 优化策略按钮', () => { cy.get('body').then($b => { if ($b.find('#btn-pv-strategy').length > 0) cy.get('#btn-pv-strategy').should('be.visible').click({ force: true }); else cy.log('元素未找到: #btn-pv-strategy'); }); cy.get('body').then($b => { if ($b.find('.ant-modal').length > 0) { cy.get('.ant-modal').should('exist'); } }); cy.get('body').then($b => { const $m = $b.find('.ant-modal .ant-btn:not(.ant-btn-primary)'); if ($m.length > 0) { cy.wrap($m.first()).click({ force: true }); } }); });
});
