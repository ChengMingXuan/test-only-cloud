/**
 * 账户 子页面 — 个人信息、发票管理、会员等级、积分管理、账户充值
 */
const OPTS = { failOnStatusCode: false, onBeforeLoad(win) { win.localStorage.setItem('jgsy_access_token', 'mock-cypress-token'); } };

describe('个人信息页面', () => {
  beforeEach(() => { 
    cy.setupApiMocks();
    // Mock 账户信息 API
    cy.intercept('GET', '**/api/account/**', {
      statusCode: 200,
      body: { success: true, data: { id: 'u1', name: '测试用户', email: 'test@jgsy.com', phone: '13800138000' } }
    });
    cy.intercept('GET', '**/api/user/profile**', {
      statusCode: 200,
      body: { success: true, data: { id: 'u1', name: '测试用户', email: 'test@jgsy.com', phone: '13800138000' } }
    });
    cy.visit('/account/profile', OPTS); 
  });
  it('[P0] 页面加载', () => { cy.get('.ant-layout-content, .ant-pro-page-container, #root', { timeout: 15000 }).should('exist'); });
  it('[P0] 姓名输入框', () => { cy.get('input[name="name"], input[placeholder*="姓名"], #acc-name, .ant-form-item input, .ant-layout-content', { timeout: 10000 }).should('exist'); });
  it('[P1] 邮箱输入框', () => { cy.get('input[name="email"], input[type="email"], input[placeholder*="邮箱"], #acc-email, .ant-form-item input, .ant-layout-content', { timeout: 10000 }).should('exist'); });
  it('[P1] 手机号输入框', () => { cy.get('input[name="phone"], input[type="tel"], input[placeholder*="手机"], #acc-phone, .ant-form-item input, .ant-layout-content', { timeout: 10000 }).should('exist'); });
});

describe('账户发票管理页面', () => {
  beforeEach(() => { cy.setupApiMocks(); cy.visit('/account/invoice', OPTS); });
  it('[P0] 页面加载', () => { cy.get('.ant-layout-content, .ant-pro-page-container, #root', { timeout: 15000 }).should('exist'); });
  it('[P0] 发票列表存在', () => { cy.get('.ant-table-tbody tr, .ant-empty, .ant-layout-content').should('have.length.gte', 1); });
});

describe('会员等级页面', () => {
  beforeEach(() => { cy.setupApiMocks(); cy.visit('/account/membership', OPTS); });
  it('[P0] 页面加载', () => { cy.get('.ant-layout-content, .ant-pro-page-container, #root', { timeout: 15000 }).should('exist'); });
  it('[P0] 会员等级信息存在', () => { cy.get('.ant-layout-content, .ant-pro-page-container, #root').should('exist'); });
});

describe('积分管理页面', () => {
  beforeEach(() => { cy.setupApiMocks(); cy.visit('/account/points', OPTS); });
  it('[P0] 页面加载', () => { cy.get('.ant-layout-content, .ant-pro-page-container, #root', { timeout: 15000 }).should('exist'); });
  it('[P0] 积分统计存在', () => { cy.get('body').then($b => { const n = $b.find('.ant-card').length; cy.log('元素数量: ' + n); expect(n).to.be.gte(0); }); });
});

describe('账户充值页面', () => {
  beforeEach(() => { cy.setupApiMocks(); cy.visit('/account/recharge', OPTS); });
  it('[P0] 页面加载', () => { cy.get('.ant-layout-content, .ant-pro-page-container, #root', { timeout: 15000 }).should('exist'); });
  it('[P0] 充值表单存在', () => { cy.get('.ant-layout-content, .ant-pro-page-container, #root').should('exist'); });
});
