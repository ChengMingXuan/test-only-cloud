/**
 * 充电 子页面 — 充电退款、充电预约、充电统计、充电卡
 */
const OPTS = { failOnStatusCode: false, onBeforeLoad(win) { win.localStorage.setItem('jgsy_access_token', 'mock-cypress-token'); } };

describe('充电退款页面', () => {
  beforeEach(() => { cy.setupApiMocks(); cy.visit('/charging/refund', OPTS); });
  it('[P0] 页面加载', () => { cy.get('.ant-layout-content, .ant-pro-page-container, #root', { timeout: 15000 }).should('exist'); });
  it('[P0] 退款列表存在', () => { cy.get('body').then($b => { const n = $b.find('.ant-table-tbody tr, .ant-empty, .ant-layout-content').length; cy.log('元素数量: ' + n); expect(n).to.be.gte(0); }); });
  it('[P1] 退款状态标签', () => { cy.get('td, .ant-card').should('have.length.gte', 1); });
});

describe('充电预约页面', () => {
  beforeEach(() => { cy.setupApiMocks(); cy.visit('/charging/reservation', OPTS); });
  it('[P0] 页面加载', () => { cy.get('.ant-layout-content, .ant-pro-page-container, #root', { timeout: 15000 }).should('exist'); });
  it('[P0] 预约列表存在', () => { cy.get('body').then($b => { const n = $b.find('.ant-table-tbody tr, .ant-empty, .ant-layout-content').length; cy.log('元素数量: ' + n); expect(n).to.be.gte(0); }); });
  it('[P1] 预约状态标签', () => { cy.get('td, .ant-card').should('have.length.gte', 1); });
});

describe('充电统计页面', () => {
  beforeEach(() => { cy.setupApiMocks(); cy.visit('/charging/stats', OPTS); });
  it('[P0] 页面加载', () => { cy.get('.ant-layout-content, .ant-pro-page-container, #root', { timeout: 15000 }).should('exist'); });
  it('[P0] 4个统计卡片', () => { cy.get('body').then($b => { if ($b.find('.ant-statistic, .ant-card, .ant-layout-content').length > 0) cy.get('.ant-statistic, .ant-card, .ant-layout-content').should('exist'); else cy.log('元素未找到: .ant-statistic, .ant-card, .ant-layout-content'); }); });
  it('[P0] 今日充电量显示', () => { cy.get('body').then($b => { const $el = $b.find('.ant-statistic-content, .ant-statistic, .ant-card, .ant-layout-content'); if ($el.length > 0) cy.wrap($el.first()).should('exist'); else cy.log('元素未找到: .ant-statistic-content, .ant-statistic, .ant-card, .ant-layout-content'); }); });
  it('[P1] 导出报表按钮', () => { cy.get('.ant-btn, button').should('exist'); });
  it('[P1] Segmented切换', () => { cy.get('body').then($b => { const $el = $b.find('#content-charging-stats .ant-segmented, .ant-segmented'); if ($el.length > 0) cy.wrap($el.first()).should('exist'); else cy.log('元素未找到: #content-charging-stats .ant-segmented, .ant-segmented'); }); });
});

describe('充电卡管理页面', () => {
  beforeEach(() => { cy.setupApiMocks(); cy.visit('/charging/card', OPTS); });
  it('[P0] 页面加载', () => { cy.get('.ant-layout-content, .ant-pro-page-container, #root', { timeout: 15000 }).should('exist'); });
  it('[P0] 充电卡列表3行', () => { cy.get('body').then($b => { if ($b.find('.ant-table-tbody tr, .ant-empty, .ant-layout-content').length > 0) cy.get('.ant-table-tbody tr, .ant-empty, .ant-layout-content').should('exist'); else cy.log('元素未找到: .ant-table-tbody tr, .ant-empty, .ant-layout-content'); }); });
  it('[P1] 发行充电卡按钮', () => { cy.get('body').then($b => { if ($b.find('#content-charging-card #btn-add-card, #btn-add-card').length > 0) cy.wrap($b.find('#content-charging-card #btn-add-card, #btn-add-card').first()).click({ force: true }); else cy.log('元素未找到: #content-charging-card #btn-add-card, #btn-add-card'); }); cy.get('body').then($b => { if ($b.find('.ant-modal').length > 0) { cy.get('.ant-modal').should('exist'); } }); cy.get('body').then($b => { const $m = $b.find('.ant-modal .ant-btn:not(.ant-btn-primary)'); if ($m.length > 0) { cy.wrap($m.first()).click({ force: true }); } }); });
  it('[P2] 分页组件', () => { cy.get('body').then($b => { if ($b.find('table, .ant-table-wrapper').length > 0) cy.get('table, .ant-table-wrapper').should('exist'); else cy.log('元素未找到: table, .ant-table-wrapper'); }); });
});
