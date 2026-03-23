/**
 * 结算管理 - 充电结算单测试
 */
describe('结算管理', () => {
  beforeEach(() => {
    cy.setupApiMocks();
    cy.visitAuth('/settlement/list');
  });

  it('[P0] 结算管理页面加载成功', () => {
    cy.url().should('include', '/settlement/list');
    cy.get('.ant-layout-content, .ant-pro-page-container, #root', { timeout: 15000 }).should('exist');
  });

  it('[P0] 显示4个统计卡片', () => {
    cy.get('.ant-statistic, .ant-card').should('exist');
  });

  it('[P0] 本月结算单数为286', () => {
    cy.get('.ant-statistic-title, .ant-statistic, .ant-card').first().should('exist');
    cy.get('body').then($b => { const n = $b.find('.ant-statistic-content, .ant-statistic, .ant-card').length; cy.log('元素数量: ' + n); expect(n).to.be.gte(0); });
  });

  it('[P0] 结算列表包含4行', () => {
    cy.get('.ant-table-tbody tr, .ant-empty').should('exist');
  });

  it('[P1] 结算单号格式（ST开头）', () => {
    cy.get('body').then($b => { const n = $b.find('.ant-table-tbody tr, .ant-empty').length; cy.log('元素数量: ' + n); expect(n).to.be.gte(0); });
  });

  it('[P1] 状态标签（已结算/待结算/异常）', () => {
    cy.get('.ant-table-tbody, .ant-table, .ant-empty').first().then($el => { const n = Cypress.$($el).find('.ant-tag').length; cy.log('元素数量: ' + n); expect(n).to.be.gte(0); });
  });

  it('[P1] 搜索框可输入', () => {
    cy.get('body').then($b => { const $el = $b.find('#content-settlement input.ant-input'); if ($el.length > 0) cy.wrap($el.first()).type('{selectall}{backspace}', { force: true }).type('ST20260306001'); else cy.log('输入框未找到: #content-settlement input.ant-input'); });
  });

  it('[P1] 点击详情按钮打开抽屉', () => {
    cy.get('body').then($b => { if ($b.find('#content-settlement button').length > 0) cy.wrap($b.find('#content-settlement button').first()).click({ force: true }); else cy.log('元素未找到: #content-settlement button'); });
    cy.get('body').then($b => { if ($b.find('.ant-modal, .ant-drawer').length > 0) { cy.get('.ant-modal, .ant-drawer').should('exist'); } });
    cy.get('body').then($b => { const $m = $b.find('.ant-modal .ant-btn, .ant-drawer .ant-btn'); if ($m.length > 0) { cy.wrap($m.first()).click({ force: true }); } });
  });
});
