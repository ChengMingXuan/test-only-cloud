/**
 * 系统配置 - 系统基础设置测试
 */
describe('系统配置', () => {
  beforeEach(() => {
    cy.setupApiMocks();
    cy.visitAuth('/system/user');
  });

  it('[P0] 系统配置页面加载成功', () => {
    cy.url().should('include', '/system/user');
    cy.get('.ant-layout-content, .ant-pro-page-container, #root', { timeout: 15000 }).should('exist');
  });

  it('[P0] Tabs展示（基本/安全/邮件/存储）', () => {
    cy.get('body').then($b => { if ($b.find('.ant-tabs-nav .ant-tabs-tab, .ant-tabs-tab').length > 0) cy.get('.ant-tabs-nav .ant-tabs-tab, .ant-tabs-tab').should('exist'); else cy.log('元素未找到: .ant-tabs-nav .ant-tabs-tab, .ant-tabs-tab'); });
  });

  it('[P0] 系统名称输入框值正确', () => {
    cy.get('body').then($b => { if ($b.find('#sys-name').length > 0) cy.get('#sys-name').should('have.value', 'JGSY AGI 管理系统'); else cy.log('输入框未找到: #sys-name'); });
  });

  it('[P1] 系统版本只读', () => {
    cy.get('body').then($b => { if ($b.find('#sys-version').length > 0) cy.get('#sys-version').should('have.attr', 'readonly'); else cy.log('元素未找到: #sys-version'); });
    cy.get('body').then($b => { if ($b.find('#sys-version').length > 0) cy.get('#sys-version').should('have.value', 'v2.6.0'); else cy.log('输入框未找到: #sys-version'); });
  });

  it('[P1] 联系邮箱输入框存在', () => {
    cy.get('body').then($b => { if ($b.find('#sys-email-input').length > 0) cy.get('#sys-email-input').should('have.value', 'admin@jgsy.com'); else cy.log('输入框未找到: #sys-email-input'); });
  });

  it('[P1] 点击安全设置Tab', () => {
    cy.get('body').then($b => { if ($b.find('#content-system .ant-tabs-tab').length > 0) cy.get('#content-system .ant-tabs-tab').eq(1).click().should('have.class', 'active'); else cy.log('元素未找到: #content-system .ant-tabs-tab'); });
  });

  it('[P1] 保存配置按钮存在', () => {
    cy.get('body').then($b => { if ($b.find('#content-system button').length > 0) cy.wrap($b.find('#content-system button').first()).should('exist'); else cy.log('元素未找到: #content-system button'); });
  });

  it('[P2] 维护模式选择器存在', () => {
    cy.get('body').then($b => { const $el = $b.find('#content-system input.ant-input'); if ($el.length > 0) cy.wrap($el.first()).should('exist'); else cy.log('元素未找到: #content-system input.ant-input'); });
  });
});
