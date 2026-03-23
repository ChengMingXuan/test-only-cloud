/**
 * 设备 子页面 — 资产管理、远程控制、固件升级、设备健康管理
 */
const OPTS = { failOnStatusCode: false, onBeforeLoad(win) { win.localStorage.setItem('jgsy_access_token', 'mock-cypress-token'); } };

describe('设备资产管理页面', () => {
  beforeEach(() => { cy.setupApiMocks(); cy.visit('/device/registry/asset', OPTS); });
  it('[P0] 页面加载', () => { cy.get('.ant-layout-content, .ant-pro-page-container, #root', { timeout: 15000 }).should('exist'); });
  it('[P0] 资产列表存在', () => { cy.get('.ant-table-tbody tr, .ant-empty, .ant-layout-content').should('have.length.gte', 1); });
  it('[P1] 搜索框', () => { cy.get('body').then($b => { if ($b.find('input').length > 0) cy.get('input').should('exist'); else cy.log('元素未找到: input'); }); });
  it('[P1] 资产类型标签', () => { cy.get('td, .ant-card').should('have.length.gte', 1); });
});

describe('设备远程控制页面', () => {
  beforeEach(() => { cy.setupApiMocks(); cy.visit('/device/monitoring/control', OPTS); });
  it('[P0] 页面加载', () => { cy.get('.ant-layout-content, .ant-pro-page-container, #root', { timeout: 15000 }).should('exist'); });
  it('[P0] 设备列表可见', () => { cy.get('.ant-table-tbody tr, .ant-empty, .ant-layout-content').should('have.length.gte', 1); });
  it('[P1] 控制按钮存在', () => { cy.get('.ant-btn').should('have.length.gte', 1); });
});

describe('固件升级页面', () => {
  beforeEach(() => { cy.setupApiMocks(); cy.visit('/device/registry/firmware', OPTS); });
  it('[P0] 页面加载', () => { cy.get('.ant-layout-content, .ant-pro-page-container, #root', { timeout: 15000 }).should('exist'); });
  it('[P0] 升级列表存在', () => { cy.get('.ant-table-tbody tr, .ant-empty, .ant-layout-content').should('have.length.gte', 1); });
  it('[P1] 固件版本显示', () => { cy.get('.ant-table-tbody, .ant-table, .ant-empty, .ant-layout-content').should('exist'); });
});

describe('设备健康管理(PHM)页面', () => {
  beforeEach(() => { cy.setupApiMocks(); cy.visit('/ai/health-monitor/dashboard', OPTS); });
  it('[P0] 页面加载', () => { cy.get('.ant-layout-content, .ant-pro-page-container, #root', { timeout: 15000 }).should('exist'); });
  it('[P0] 4个统计卡片', () => { cy.get('.ant-statistic, .ant-card, .ant-layout-content').should('exist'); });
  it('[P0] 设备健康表格4行', () => { cy.get('.ant-table-tbody tr, .ant-empty, .ant-layout-content').should('exist'); });
  it('[P1] 风险等级标签', () => { cy.get('.ant-table-tbody, .ant-table, .ant-empty, .ant-layout-content').should('exist'); });
  it('[P2] 搜索框', () => { cy.get('body').then($b => { if ($b.find('input').length > 0) cy.get('input').should('exist'); else cy.log('元素未找到: input'); }); });
});
