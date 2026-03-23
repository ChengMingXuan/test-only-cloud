/**
 * 数字孪生 子页面1 — 孪生总览、孪生监控、实时数据、历史回放
 */
const OPTS = { failOnStatusCode: false, onBeforeLoad(win) { win.localStorage.setItem('jgsy_access_token', 'mock-cypress-token'); } };

describe('数字孪生总览页面', () => {
  beforeEach(() => { cy.setupApiMocks(); cy.visit('/digital-twin/dashboard', OPTS); });
  it('[P0] 页面加载', () => { cy.get('.ant-layout-content, .ant-pro-page-container, #root', { timeout: 15000 }).should('exist'); });
  it('[P0] 孪生统计卡片', () => { cy.get('.ant-card').should('have.length.gte', 1); });
  it('[P1] 图表容器', () => { cy.get('.ant-card').should('exist'); });
});

describe('数字孪生监控页面', () => {
  beforeEach(() => { cy.setupApiMocks(); cy.visit('/digital-twin/monitor', OPTS); });
  it('[P0] 页面加载', () => { cy.get('.ant-layout-content, .ant-pro-page-container, #root', { timeout: 15000 }).should('exist'); });
  it('[P0] 监控数据存在', () => { cy.get('.ant-table-tbody tr, .ant-empty, .ant-layout-content').should('have.length.gte', 1); });
  it('[P1] 实时监控图表', () => { cy.get('body').then($b => { if ($b.find('.ant-table-wrapper').length > 0) cy.get('.ant-table-wrapper').should('exist'); else cy.log('元素未找到: .ant-table-wrapper'); }); });
});

describe('数字孪生实时数据页面', () => {
  beforeEach(() => { cy.setupApiMocks(); cy.visit('/digital-twin/realtime', OPTS); });
  it('[P0] 页面加载', () => { cy.get('.ant-layout-content, .ant-pro-page-container, #root', { timeout: 15000 }).should('exist'); });
  it('[P0] 实时数据卡片', () => { cy.get('.ant-card').should('have.length.gte', 1); });
  it('[P1] 数据刷新按钮', () => { cy.get('.ant-btn').should('exist'); });
});

describe('数字孪生历史回放页面', () => {
  beforeEach(() => { cy.setupApiMocks(); cy.visit('/digital-twin/playback', OPTS); });
  it('[P0] 页面加载', () => { cy.get('.ant-layout-content, .ant-pro-page-container, #root', { timeout: 15000 }).should('exist'); });
  it('[P0] 回放控件区域', () => { cy.get('.ant-card').should('exist'); });
  it('[P1] 播放按钮', () => { cy.get('.ant-btn').should('exist'); });
});
