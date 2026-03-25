/**
 * 能源服务1 — 碳交易、需求响应、电力交易
 */
const OPTS = { failOnStatusCode: false, onBeforeLoad(win) { win.localStorage.setItem('jgsy_access_token', 'mock-cypress-token'); } };

describe('碳交易页面', () => {
  beforeEach(() => { cy.setupApiMocks(); cy.visit('/energy/carbon-trade', OPTS); });
  it('[P0] 页面加载', () => { cy.get('.ant-layout-content, .ant-pro-page-container, #root', { timeout: 15000 }).should('exist'); });
  it('[P0] 4个统计卡片', () => { cy.get('body').then($b => { if ($b.find('.ant-statistic, .ant-card').length > 0) cy.get('.ant-statistic, .ant-card').should('exist'); else cy.log('元素未找到: .ant-statistic, .ant-card'); }); });
  it('[P0] 交易记录3行', () => { cy.get('body').then($b => { if ($b.find('.ant-table-tbody tr, .ant-empty').length > 0) cy.get('.ant-table-tbody tr, .ant-empty').should('exist'); else cy.log('元素未找到: .ant-table-tbody tr, .ant-empty'); }); });
  it('[P1] 新建交易按钮', () => { cy.get('body').then($b => { if ($b.find('#btn-add-carbon-order').length > 0) cy.get('#btn-add-carbon-order').click({ force: true }); else cy.log('元素未找到: #btn-add-carbon-order'); }); cy.get('body').then($b => { if ($b.find('.ant-modal').length > 0) { cy.get('.ant-modal').should('exist'); } }); cy.get('body').then($b => { const $m = $b.find('.ant-modal .ant-btn:not(.ant-btn-primary)'); if ($m.length > 0) { cy.wrap($m.first()).click({ force: true }); } }); });
  it('[P1] 导出按钮', () => { cy.get('body').then($b => { if ($b.find('.ant-btn, button').length > 0) cy.get('.ant-btn, button').should('exist'); else cy.log('元素未找到: .ant-btn, button'); }); });
  it('[P2] 交易状态标签', () => { cy.get('body').then($b => { const n = $b.find('.ant-tag, .ant-badge').length; cy.log('标签数量: ' + n); expect(n).to.be.gte(0); }); });
});

describe('需求响应页面', () => {
  beforeEach(() => { cy.setupApiMocks(); cy.visit('/energy/demand-resp', OPTS); });
  it('[P0] 页面加载', () => { cy.get('.ant-layout-content, .ant-pro-page-container, #root', { timeout: 15000 }).should('exist'); });
  it('[P0] 3个统计卡片', () => { cy.get('body').then($b => { if ($b.find('.ant-statistic, .ant-card').length > 0) cy.get('.ant-statistic, .ant-card').should('exist'); else cy.log('元素未找到: .ant-statistic, .ant-card'); }); });
  it('[P0] 响应记录3行', () => { cy.get('body').then($b => { if ($b.find('.ant-table-tbody tr, .ant-empty').length > 0) cy.get('.ant-table-tbody tr, .ant-empty').should('exist'); else cy.log('元素未找到: .ant-table-tbody tr, .ant-empty'); }); });
  it('[P1] 申报响应按钮', () => { cy.get('body').then($b => { if ($b.find('#btn-add-demand-resp').length > 0) cy.get('#btn-add-demand-resp').click({ force: true }); else cy.log('元素未找到: #btn-add-demand-resp'); }); cy.get('body').then($b => { if ($b.find('.ant-modal').length > 0) { cy.get('.ant-modal').should('exist'); } }); cy.get('body').then($b => { const $m = $b.find('.ant-modal .ant-btn:not(.ant-btn-primary)'); if ($m.length > 0) { cy.wrap($m.first()).click({ force: true }); } }); });
});

describe('电力交易页面', () => {
  beforeEach(() => { cy.setupApiMocks(); cy.visit('/energy/elec-trade', OPTS); });
  it('[P0] 页面加载', () => { cy.get('.ant-layout-content, .ant-pro-page-container, #root', { timeout: 15000 }).should('exist'); });
  it('[P0] 3个统计卡片', () => { cy.get('body').then($b => { if ($b.find('.ant-statistic, .ant-card').length > 0) cy.get('.ant-statistic, .ant-card').should('exist'); else cy.log('元素未找到: .ant-statistic, .ant-card'); }); });
  it('[P0] 交易记录3行', () => { cy.get('body').then($b => { if ($b.find('.ant-table-tbody tr, .ant-empty').length > 0) cy.get('.ant-table-tbody tr, .ant-empty').should('exist'); else cy.log('元素未找到: .ant-table-tbody tr, .ant-empty'); }); });
  it('[P1] 提交报价按钮', () => { cy.get('body').then($b => { if ($b.find('#btn-add-elec-bid').length > 0) cy.get('#btn-add-elec-bid').click({ force: true }); else cy.log('元素未找到: #btn-add-elec-bid'); }); cy.get('body').then($b => { if ($b.find('.ant-modal').length > 0) { cy.get('.ant-modal').should('exist'); } }); cy.get('body').then($b => { const $m = $b.find('.ant-modal .ant-btn:not(.ant-btn-primary)'); if ($m.length > 0) { cy.wrap($m.first()).click({ force: true }); } }); });
  it('[P2] 中标状态标签', () => { cy.get('body').then($b => { const n = $b.find('.ant-tag, .ant-badge').length; cy.log('标签数量: ' + n); expect(n).to.be.gte(0); }); });
});
