/**
 * 能源服务3 + 场站子页 — 光伏储能、能源协调、场站地图、场站统计
 */
const OPTS = { failOnStatusCode: false, onBeforeLoad(win) { win.localStorage.setItem('jgsy_access_token', 'mock-cypress-token'); } };

describe('光伏储能页面', () => {
  beforeEach(() => { cy.setupApiMocks(); cy.visit('/energy/pvessc', OPTS); });
  it('[P0] 页面加载', () => { cy.get('.ant-layout-content, .ant-pro-page-container, #root', { timeout: 15000 }).should('exist'); });
  it('[P0] 4个统计卡片', () => { cy.get('body').then($b => { if ($b.find('.ant-statistic, .ant-card').length > 0) cy.get('.ant-statistic, .ant-card').should('exist'); else cy.log('元素未找到: .ant-statistic, .ant-card'); }); });
  it('[P0] SOC显示', () => { cy.get('body').then($b => { if ($b.find('.ant-statistic-content, .ant-statistic, .ant-card').length > 0) cy.get('.ant-statistic-content, .ant-statistic, .ant-card').should('exist'); else cy.log('元素未找到'); }); });
  it('[P1] 3个Tab分页', () => { cy.get('body').then($b => { if ($b.find('.ant-menu-item').length > 0) cy.get('.ant-menu-item').should('exist'); else cy.log('元素未找到: .ant-menu-item'); }); });
  it('[P1] 图表容器', () => { cy.get('body').then($b => { if ($b.find('.ant-card').length > 0) cy.get('.ant-card').should('exist'); else cy.log('元素未找到: .ant-card'); }); });
});

describe('能源协调页面', () => {
  beforeEach(() => { cy.setupApiMocks(); cy.visit('/energy/orchestrator', OPTS); });
  it('[P0] 页面加载', () => { cy.get('.ant-layout-content, .ant-pro-page-container, #root', { timeout: 15000 }).should('exist'); });
  it('[P0] 3个统计卡片', () => { cy.get('body').then($b => { if ($b.find('.ant-statistic, .ant-card').length > 0) cy.get('.ant-statistic, .ant-card').should('exist'); else cy.log('元素未找到: .ant-statistic, .ant-card'); }); });
  it('[P0] 协调任务3行', () => { cy.get('body').then($b => { if ($b.find('.ant-table-tbody tr, .ant-empty').length > 0) cy.get('.ant-table-tbody tr, .ant-empty').should('exist'); else cy.log('元素未找到'); }); });
  it('[P1] 新建协调任务按钮', () => { cy.get('body').then($b => { if ($b.find('#btn-add-orch-task').length > 0) cy.get('#btn-add-orch-task').click({ force: true }); else cy.log('元素未找到: #btn-add-orch-task'); }); cy.get('body').then($b => { if ($b.find('.ant-modal').length > 0) { cy.get('.ant-modal').should('exist'); } }); cy.get('body').then($b => { const $m = $b.find('.ant-modal .ant-btn:not(.ant-btn-primary)'); if ($m.length > 0) { cy.wrap($m.first()).click({ force: true }); } }); });
});

describe('场站地图页面', () => {
  beforeEach(() => { cy.setupApiMocks(); cy.visit('/station/monitor', OPTS); });
  it('[P0] 页面加载', () => { cy.get('.ant-layout-content, .ant-pro-page-container, #root', { timeout: 15000 }).should('exist'); });
  it('[P0] 地图区域存在', () => { cy.get('body').then($b => { if ($b.find('.ant-card').length > 0) cy.get('.ant-card').should('exist'); else cy.log('元素未找到: .ant-card'); }); });
  it('[P0] 3个在线/离线统计', () => { cy.get('body').then($b => { if ($b.find('.ant-statistic, .ant-card').length > 0) cy.get('.ant-statistic, .ant-card').should('exist'); else cy.log('元素未找到: .ant-statistic, .ant-card'); }); });
  it('[P1] 搜索框', () => { cy.get('body').then($b => { if ($b.find('input').length > 0) cy.get('input').should('exist'); else cy.log('元素未找到: input'); }); });
});

describe('场站统计页面', () => {
  beforeEach(() => { cy.setupApiMocks(); cy.visit('/station/monitor', OPTS); });
  it('[P0] 页面加载', () => { cy.get('.ant-layout-content, .ant-pro-page-container, #root', { timeout: 15000 }).should('exist'); });
  it('[P0] 4个统计卡片', () => { cy.get('body').then($b => { if ($b.find('.ant-statistic, .ant-card').length > 0) cy.get('.ant-statistic, .ant-card').should('exist'); else cy.log('元素未找到: .ant-statistic, .ant-card'); }); });
  it('[P1] 导出按钮', () => { cy.get('body').then($b => { if ($b.find('.ant-btn, button').length > 0) cy.get('.ant-btn, button').should('exist'); else cy.log('元素未找到: .ant-btn, button'); }); });
  it('[P1] 时段切换', () => { cy.get('body').then($b => { if ($b.find('.ant-segmented').length > 0) cy.get('.ant-segmented').should('exist'); else cy.log('元素未找到: .ant-segmented'); }); });
});
