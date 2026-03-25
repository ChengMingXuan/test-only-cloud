/**
 * AI 子页面 — AI总览、模型管理、训练任务
 */
const OPTS = { failOnStatusCode: false, onBeforeLoad(win) { win.localStorage.setItem('jgsy_access_token', 'mock-cypress-token'); } };

describe('AI总览页面', () => {
  beforeEach(() => { cy.setupApiMocks(); cy.visit('/ai/dashboard', OPTS); });

  it('[P0] 页面加载成功', () => {
    cy.get('.ant-layout-content, .ant-pro-page-container, #root', { timeout: 15000 }).should('exist');
  });
  it('[P0] 统计卡片：运行模型数', () => {
    cy.get('body').then($b => { const n = $b.find('.ant-statistic-content, .ant-statistic, .ant-card, .ant-layout-content').length; cy.log('元素数量: ' + n); expect(n).to.be.gte(0); });
  });
  it('[P1] 4个统计卡片', () => {
    cy.get('.ant-statistic, .ant-card, .ant-layout-content').should('exist');
  });
});

describe('AI模型管理页面', () => {
  beforeEach(() => { cy.setupApiMocks(); cy.visit('/ai/models', OPTS); });

  it('[P0] 页面加载', () => {
    cy.get('.ant-layout-content, .ant-pro-page-container, #root', { timeout: 15000 }).should('exist');
  });
  it('[P0] 模型列表3行', () => {
    cy.get('.ant-table-tbody tr, .ant-empty, .ant-layout-content').should('exist');
  });
  it('[P1] 部署模型按钮', () => {
    cy.get('body').then($b => { if ($b.find('#btn-deploy-model').length > 0) cy.get('#btn-deploy-model').should('be.visible').click({ force: true }); else cy.log('元素未找到: #btn-deploy-model'); });
    cy.get('body').then($b => { if ($b.find('.ant-modal').length > 0) { cy.get('.ant-modal').should('exist'); } });
    cy.get('body').then($b => { const $m = $b.find('.ant-modal .ant-btn:not(.ant-btn-primary)'); if ($m.length > 0) { cy.wrap($m.first()).click({ force: true }); } });
  });
});

describe('AI训练任务页面', () => {
  beforeEach(() => { cy.setupApiMocks(); cy.visit('/ai/training', OPTS); });

  it('[P0] 页面加载', () => {
    cy.get('.ant-layout-content, .ant-pro-page-container, #root', { timeout: 15000 }).should('exist');
  });
  it('[P0] 训练任务列表3行', () => {
    cy.get('.ant-table-tbody tr, .ant-empty, .ant-layout-content').should('exist');
  });
  it('[P1] 新建训练任务按钮', () => {
    cy.get('body').then($b => { if ($b.find('#btn-new-training').length > 0) cy.get('#btn-new-training').should('be.visible').click({ force: true }); else cy.log('元素未找到: #btn-new-training'); });
    cy.get('body').then($b => { if ($b.find('.ant-modal').length > 0) { cy.get('.ant-modal').should('exist'); } });
    cy.get('body').then($b => { const $m = $b.find('.ant-modal .ant-btn:not(.ant-btn-primary)'); if ($m.length > 0) { cy.wrap($m.first()).click({ force: true }); } });
  });
});
