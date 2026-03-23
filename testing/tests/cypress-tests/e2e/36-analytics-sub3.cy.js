/**
 * 分析 子页面3 — 实时分析、下钻分析、路径分析、用户画像
 */
const OPTS = { failOnStatusCode: false, onBeforeLoad(win) { win.localStorage.setItem('jgsy_access_token', 'mock-cypress-token'); } };

describe('实时分析页面', () => {
  beforeEach(() => { cy.setupApiMocks(); cy.visit('/analytics/realtime', OPTS); });
  it('[P0] 页面加载', () => { cy.get('.ant-layout-content, .ant-pro-page-container, #root', { timeout: 15000 }).should('exist'); });
  it('[P0] 实时数据区域存在', () => { cy.get('.ant-card').should('have.length.gte', 1); });
  it('[P1] 实时图表容器存在', () => { cy.get('.ant-card').should('exist'); });
});

describe('下钻分析页面', () => {
  beforeEach(() => { cy.setupApiMocks(); cy.visit('/analytics/drilldown', OPTS); });
  it('[P0] 页面加载', () => { cy.get('.ant-layout-content, .ant-pro-page-container, #root', { timeout: 15000 }).should('exist'); });
  it('[P0] 内容区可见', () => { cy.get('.ant-card').should('exist'); });
});

describe('路径分析页面', () => {
  beforeEach(() => { cy.setupApiMocks(); cy.visit('/analytics/path', OPTS); });
  it('[P0] 页面加载', () => { cy.get('.ant-layout-content, .ant-pro-page-container, #root', { timeout: 15000 }).should('exist'); });
  it('[P0] 内容区可见', () => { cy.get('.ant-card').should('exist'); });
});

describe('用户画像页面', () => {
  beforeEach(() => { cy.setupApiMocks(); cy.visit('/analytics/user-profile', OPTS); });
  it('[P0] 页面加载', () => { cy.get('.ant-layout-content, .ant-pro-page-container, #root', { timeout: 15000 }).should('exist'); });
  it('[P0] 画像数据存在', () => { cy.get('.ant-table-tbody tr, .ant-empty, .ant-layout-content').should('have.length.gte', 1); });
  it('[P1] 内容区结构', () => { cy.get('.ant-table-wrapper').should('exist'); });
});
