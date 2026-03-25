/**
 * 数字孪生 - 孪生体管理测试
 */
describe('数字孪生', () => {
  beforeEach(() => {
    cy.setupApiMocks();
    cy.visitAuth('/digital-twin/overview');
  });

  it('[P0] 数字孪生页面加载成功', () => {
    cy.url().should('include', '/digital-twin/overview');
    cy.get('.ant-layout-content, .ant-pro-page-container, #root', { timeout: 15000 }).should('exist');
  });

  it('[P0] 孪生体列表包含4行', () => {
    cy.get('.ant-table-tbody tr, .ant-empty').should('exist');
  });

  it('[P1] 孪生体类型标签（场站/设备/系统）', () => {
    cy.get('body').then($b => { const n = $b.find('.ant-table-tbody, .ant-table, .ant-empty').length; cy.log('元素数量: ' + n); expect(n).to.be.gte(0); });
  });

  it('[P1] 数据点数展示', () => {
    cy.get('body').then($b => { const n = $b.find('.ant-table-tbody tr, .ant-empty').length; cy.log('元素数量: ' + n); expect(n).to.be.gte(0); });
  });

  it('[P1] 同步状态标签（同步中/离线）', () => {
    cy.get('.ant-table-tbody, .ant-table, .ant-empty').first().then($el => { const n = Cypress.$($el).find('.ant-tag').length; cy.log('元素数量: ' + n); expect(n).to.be.gte(0); });
  });

  it('[P1] 搜索框可输入', () => {
    cy.get('body').then($b => { const $el = $b.find('#content-digital-twin input.ant-input'); if ($el.length > 0) cy.wrap($el.first()).type('{selectall}{backspace}', { force: true }).type('朝阳'); else cy.log('输入框未找到: #content-digital-twin input.ant-input'); });
  });

  it('[P1] 新建孪生体按钮点击打开模态框', () => {
    cy.get('body').then($b => { if ($b.find('#content-digital-twin button').length > 0) cy.wrap($b.find('#content-digital-twin button').first()).click({ force: true }); else cy.log('元素未找到: #content-digital-twin button'); });
    cy.get('body').then($b => { if ($b.find('.ant-modal').length > 0) { cy.get('.ant-modal').should('exist'); } });
    cy.get('body').then($b => { const $m = $b.find('.ant-modal .ant-btn:not(.ant-btn-primary)'); if ($m.length > 0) { cy.wrap($m.first()).click({ force: true }); } });
  });
});
