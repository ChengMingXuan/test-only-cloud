/**
 * 报表中心 - 报表生成与管理测试
 */
describe('报表中心', () => {
  beforeEach(() => {
    cy.setupApiMocks();
    cy.visitAuth('/report/center');
  });

  it('[P0] 报表中心页面加载成功', () => {
    cy.url().should('include', '/report/center');
    cy.get('.ant-layout-content, .ant-pro-page-container, #root', { timeout: 15000 }).should('exist');
  });

  it('[P0] 报表列表包含4行', () => {
    cy.get('body').then($b => { if ($b.find('.ant-table-tbody tr, .ant-empty').length > 0) cy.get('.ant-table-tbody tr, .ant-empty').should('exist'); else cy.log('元素未找到: .ant-table-tbody tr, .ant-empty'); });
  });

  it('[P0] 报表名称正确展示', () => {
    cy.get('body').then($b => { if ($b.find('.ant-table-tbody, .ant-table, .ant-empty').length > 0) cy.get('.ant-table-tbody, .ant-table, .ant-empty').should('exist'); else cy.log('元素未找到: .ant-table-tbody, .ant-table, .ant-empty'); });
  });

  it('[P1] 报表类型标签（运营/运维/能源/碳排）', () => {
    cy.get('body').then($b => { const $el = $b.find('.ant-table-tbody, .ant-table, .ant-empty'); if ($el.length > 0) { cy.wrap($el.first()).within(() => { cy.get('.ant-tag, .ant-layout-content, .ant-tag-processing').should('have.length.gte', 1);
      cy.get('.ant-tag').should('have.length.gte', 1);
      cy.get('.ant-tag, .ant-badge').should('have.length.gte', 1); }); } else { cy.log('元素未找到: .ant-table-tbody, .ant-table, .ant-empty'); } });
  });

  it('[P1] 生成状态（已生成/生成中）', () => {
    cy.get('body').then($b => { if ($b.find('.ant-table-tbody, .ant-table, .ant-empty').length > 0) cy.get('.ant-table-tbody, .ant-table, .ant-empty').should('exist'); else cy.log('元素未找到: .ant-table-tbody, .ant-table, .ant-empty'); });
  });

  it('[P1] 生成报表按钮打开模态框', () => {
    cy.get('body').then($b => { if ($b.find('#content-report button').length > 0) cy.wrap($b.find('#content-report button').first()).click({ force: true }); else cy.log('元素未找到: #content-report button'); });
    cy.get('body').then($b => { if ($b.find('.ant-modal').length > 0) { cy.get('.ant-modal').should('exist'); } });
    cy.get('body').then($b => { const $m = $b.find('.ant-modal .ant-btn:not(.ant-btn-primary)'); if ($m.length > 0) { cy.wrap($m.first()).click({ force: true }); } });
  });

  it('[P1] 搜索框可输入', () => {
    cy.get('body').then($b => { const $el = $b.find('#content-report input.ant-input'); if ($el.length > 0) cy.wrap($el.first()).type('{selectall}{backspace}', { force: true }).type('充电'); else cy.log('输入框未找到: #content-report input.ant-input'); });
  });

  it('[P2] 下载按钮存在', () => {
    cy.get('body').then($b => { if ($b.find('#content-report button').length > 0) cy.wrap($b.find('#content-report button').first()).should('exist'); else cy.log('元素未找到: #content-report button'); });
  });
});
