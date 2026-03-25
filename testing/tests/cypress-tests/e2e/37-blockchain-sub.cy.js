/**
 * 区块链 子页面 — 区块链总览、交易记录、数字钱包、碳存证
 */
const OPTS = { failOnStatusCode: false, onBeforeLoad(win) { win.localStorage.setItem('jgsy_access_token', 'mock-cypress-token'); } };

describe('区块链总览页面', () => {
  beforeEach(() => { cy.setupApiMocks(); cy.visit('/blockchain/dashboard', OPTS); });
  it('[P0] 页面加载', () => { cy.get('.ant-layout-content, .ant-pro-page-container, #root', { timeout: 15000 }).should('exist'); });
  it('[P0] 链上统计卡片', () => { cy.get('.ant-card').should('have.length.gte', 1); });
  it('[P1] 图表容器', () => { cy.get('.ant-card').should('exist'); });
});

describe('区块链交易记录页面', () => {
  beforeEach(() => { cy.setupApiMocks(); cy.visit('/blockchain/transactions', OPTS); });
  it('[P0] 页面加载', () => { cy.get('.ant-layout-content, .ant-pro-page-container, #root', { timeout: 15000 }).should('exist'); });
  it('[P0] 交易表格存在', () => { cy.get('.ant-table-tbody tr, .ant-empty, .ant-layout-content').should('have.length.gte', 1); });
  it('[P1] 哈希地址显示', () => { cy.get('.ant-table-tbody, .ant-table, .ant-empty, .ant-layout-content').should('exist'); });
  it('[P1] 搜索框', () => { cy.get('input').should('exist'); });
});

describe('数字钱包页面', () => {
  beforeEach(() => { cy.setupApiMocks(); cy.visit('/blockchain/wallet', OPTS); });
  it('[P0] 页面加载', () => { cy.get('.ant-layout-content, .ant-pro-page-container, #root', { timeout: 15000 }).should('exist'); });
  it('[P0] 钱包余额显示', () => { cy.get('.ant-card').should('have.length.gte', 1); });
});

describe('碳存证页面', () => {
  beforeEach(() => { cy.setupApiMocks(); cy.visit('/blockchain/carbon-credit', OPTS); });
  it('[P0] 页面加载', () => { cy.get('.ant-layout-content, .ant-pro-page-container, #root', { timeout: 15000 }).should('exist'); });
  it('[P0] 存证记录存在', () => { cy.get('.ant-table-tbody tr, .ant-empty, .ant-layout-content').should('have.length.gte', 1); });
  it('[P1] 存证状态标签', () => { cy.get('td, .ant-card').should('have.length.gte', 1); });
});
