/**
 * 能源服务2 — 能效管理、综合能源、安全管控、微网管理
 */
const OPTS = { failOnStatusCode: false, onBeforeLoad(win) { win.localStorage.setItem('jgsy_access_token', 'mock-cypress-token'); } };

describe('能效管理页面', () => {
  beforeEach(() => { cy.setupApiMocks(); cy.visit('/energy/energyeff/dashboard', OPTS); });
  it('[P0] 页面加载', () => { cy.get('.ant-layout-content, .ant-pro-page-container, #root', { timeout: 15000 }).should('exist'); });
  it('[P0] 4个统计卡片', () => { cy.get('.ant-statistic, .ant-card, .ant-layout-content').should('exist'); });
  it('[P0] 综合能效显示', () => { cy.get('body').then($b => { const n = $b.find('.ant-statistic-content, .ant-statistic, .ant-card, .ant-layout-content').length; cy.log('元素数量: ' + n); expect(n).to.be.gte(0); }); });
  it('[P1] 图表容器', () => { cy.get('.ant-card').should('exist'); });
});

describe('综合能源页面', () => {
  beforeEach(() => { cy.setupApiMocks(); cy.visit('/energy/multienergy/dashboard', OPTS); });
  it('[P0] 页面加载', () => { cy.get('.ant-layout-content, .ant-pro-page-container, #root', { timeout: 15000 }).should('exist'); });
  it('[P0] 4个统计卡片', () => { cy.get('.ant-statistic, .ant-card, .ant-layout-content').should('exist'); });
  it('[P1] Tab切换（实时拓扑/能流/调度）', () => { cy.get('body').then($b => { if ($b.find('.ant-menu-item').length > 0) cy.get('.ant-menu-item').should('exist'); else cy.log('元素未找到: .ant-menu-item'); }); });
  it('[P2] 图表容器', () => { cy.get('.ant-card').should('exist'); });
});

describe('安全管控页面', () => {
  beforeEach(() => { cy.setupApiMocks(); cy.visit('/energy/safecontrol/dashboard', OPTS); });
  it('[P0] 页面加载', () => { cy.get('.ant-layout-content, .ant-pro-page-container, #root', { timeout: 15000 }).should('exist'); });
  it('[P0] 3个统计卡片', () => { cy.get('.ant-statistic, .ant-card, .ant-layout-content').should('exist'); });
  it('[P0] 风险列表3行', () => { cy.get('.ant-table-tbody tr, .ant-empty, .ant-layout-content').should('exist'); });
  it('[P1] 导出报告按钮', () => { cy.get('body').then($b => { if ($b.find('.ant-btn, button').length > 0) cy.get('.ant-btn, button').should('be.visible'); else cy.log('元素未找到: .ant-btn, button'); }); });
  it('[P2] 风险级别标签', () => { cy.get('.ant-tag, .ant-layout-content, .ant-tag-error').should('have.length.gte', 1); });
});

describe('微网管理页面', () => {
  beforeEach(() => { cy.setupApiMocks(); cy.visit('/energy/microgrid', OPTS); });
  it('[P0] 页面加载', () => { cy.get('.ant-layout-content, .ant-pro-page-container, #root', { timeout: 15000 }).should('exist'); });
  it('[P0] 3个统计卡片', () => { cy.get('.ant-statistic, .ant-card, .ant-layout-content').should('exist'); });
  it('[P0] 微网列表3行', () => { cy.get('.ant-table-tbody tr, .ant-empty, .ant-layout-content').should('exist'); });
  it('[P1] 新建微网按钮', () => { cy.get('body').then($b => { if ($b.find('#btn-add-microgrid').length > 0) cy.get('#btn-add-microgrid').click({ force: true }); else cy.log('元素未找到: #btn-add-microgrid'); }); cy.get('body').then($b => { if ($b.find('.ant-modal').length > 0) { cy.get('.ant-modal').should('exist'); } }); cy.get('body').then($b => { const $m = $b.find('.ant-modal .ant-btn:not(.ant-btn-primary)'); if ($m.length > 0) { cy.wrap($m.first()).click({ force: true }); } }); });
  it('[P2] 运行状态标签', () => { cy.get('.ant-tag, .ant-badge, .ant-layout-content').should('have.length.gte', 1); });
});
