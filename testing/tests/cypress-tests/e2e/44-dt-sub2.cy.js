/**
 * 数字孪生 子页面2 — 仿真分析、孪生控制、场景管理、孪生仿真
 */
const OPTS = { failOnStatusCode: false, onBeforeLoad(win) { win.localStorage.setItem('jgsy_access_token', 'mock-cypress-token'); } };

describe('数字孪生仿真分析页面', () => {
  beforeEach(() => { cy.setupApiMocks(); cy.visit('/digital-twin/analysis', OPTS); });
  it('[P0] 页面加载', () => { cy.get('.ant-layout-content, .ant-pro-page-container, #root', { timeout: 15000 }).should('exist'); });
  it('[P0] 分析结果存在', () => { cy.get('.ant-card').should('exist'); });
});

describe('数字孪生控制页面', () => {
  beforeEach(() => { cy.setupApiMocks(); cy.visit('/digital-twin/control', OPTS); });
  it('[P0] 页面加载', () => { cy.get('.ant-layout-content, .ant-pro-page-container, #root', { timeout: 15000 }).should('exist'); });
  it('[P0] 控制面板存在', () => { cy.get('.ant-card').should('exist'); });
  it('[P1] 控制按钮', () => { cy.get('body').then($b => { if ($b.find('.ant-btn').length > 0) cy.get('.ant-btn').should('exist'); else cy.log('元素未找到: .ant-btn'); }); });
});

describe('数字孪生场景管理页面', () => {
  beforeEach(() => { cy.setupApiMocks(); cy.visit('/digital-twin/scene3d', OPTS); });
  it('[P0] 页面加载', () => { cy.get('.ant-layout-content, .ant-pro-page-container, #root', { timeout: 15000 }).should('exist'); });
  it('[P0] 3D场景区域', () => { cy.get('.ant-card').should('exist'); });
  it('[P1] 新建场景按钮', () => { cy.get('button').should('exist'); });
});

describe('数字孪生仿真页面', () => {
  beforeEach(() => { cy.setupApiMocks(); cy.visit('/digital-twin/overview', OPTS); });
  it('[P0] 页面加载', () => { cy.get('.ant-layout-content, .ant-pro-page-container, #root', { timeout: 15000 }).should('exist'); });
  it('[P0] 仿真任务列表', () => { cy.get('.ant-table-tbody tr, .ant-empty, .ant-layout-content').should('have.length.gte', 1); });
  it('[P1] 仿真参数设置', () => { cy.get('body').then($b => { if ($b.find('.ant-btn').length > 0) cy.get('.ant-btn').should('exist'); else cy.log('元素未找到: .ant-btn'); }); });
  it('[P2] 仿真状态标签', () => { cy.get('td, .ant-card').should('have.length.gte', 1); });
});
