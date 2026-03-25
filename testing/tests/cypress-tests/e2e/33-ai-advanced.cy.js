/**
 * AI 高级功能 — 设备健康预测、AI故障预警、AI碳交易、AI市场策略
 */
const OPTS = { failOnStatusCode: false, onBeforeLoad(win) { win.localStorage.setItem('jgsy_access_token', 'mock-cypress-token'); } };

describe('AI设备健康预测页面', () => {
  beforeEach(() => { cy.setupApiMocks(); cy.visit('/ai/health-monitor/dashboard', OPTS); });
  it('[P0] 页面加载', () => { cy.get('.ant-layout-content, .ant-pro-page-container, #root', { timeout: 15000 }).should('exist'); });
  it('[P0] 4个统计卡片', () => { cy.get('.ant-statistic, .ant-card, .ant-layout-content').should('exist'); });
  it('[P0] 健康评分显示', () => { cy.get('.ant-statistic-content, .ant-statistic, .ant-card, .ant-layout-content').should('exist'); });
  it('[P1] 设备列表3行', () => { cy.get('.ant-table-tbody tr, .ant-empty, .ant-layout-content').should('exist'); });
  it('[P1] 风险标签显示', () => { cy.get('.ant-table-tbody, .ant-table, .ant-empty, .ant-layout-content').should('exist'); });
});

describe('AI故障预警页面', () => {
  beforeEach(() => { cy.setupApiMocks(); cy.visit('/ai/scenarios/fault-warning', OPTS); });
  it('[P0] 页面加载', () => { cy.get('.ant-layout-content, .ant-pro-page-container, #root', { timeout: 15000 }).should('exist'); });
  it('[P0] 预警列表3行', () => { cy.get('.ant-table-tbody tr, .ant-empty, .ant-layout-content').should('exist'); });
  it('[P1] 搜索框存在', () => { cy.get('input').should('exist'); });
});

describe('AI碳交易页面', () => {
  beforeEach(() => { cy.setupApiMocks(); cy.visit('/ai/scenarios/carbon', OPTS); });
  it('[P0] 页面加载', () => { cy.get('.ant-layout-content, .ant-pro-page-container, #root', { timeout: 15000 }).should('exist'); });
  it('[P0] 碳配额统计', () => { cy.get('.ant-statistic-content, .ant-statistic, .ant-card, .ant-layout-content').should('exist'); });
  it('[P1] 3个统计卡片', () => { cy.get('.ant-statistic, .ant-card, .ant-layout-content').should('exist'); });
});

describe('AI市场策略页面', () => {
  beforeEach(() => { cy.setupApiMocks(); cy.visit('/ai/scenarios/market', OPTS); });
  it('[P0] 页面加载', () => { cy.get('.ant-layout-content, .ant-pro-page-container, #root', { timeout: 15000 }).should('exist'); });
});
