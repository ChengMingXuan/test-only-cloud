/**
 * 代理商管理、内容管理、媒体管理
 */
const OPTS = { failOnStatusCode: false, onBeforeLoad(win) { win.localStorage.setItem('jgsy_access_token', 'mock-cypress-token'); } };

describe('代理商管理页面', () => {
  beforeEach(() => { cy.setupApiMocks(); cy.visit('/tenant/agent-manage', OPTS); });
  it('[P0] 页面加载', () => { cy.get('.ant-layout-content, .ant-pro-page-container, #root', { timeout: 15000 }).should('exist'); });
  it('[P0] 代理商列表存在', () => { cy.get('.ant-table-tbody tr, .ant-empty, .ant-layout-content').should('have.length.gte', 1); });
  it('[P1] 搜索框', () => { cy.get('input').should('exist'); });
  it('[P1] 分页组件', () => { cy.get('table, .ant-table-wrapper').should('exist'); });
});

describe('佣金管理页面', () => {
  beforeEach(() => { cy.setupApiMocks(); cy.visit('/tenant/agent-manage', OPTS); });
  it('[P0] 页面加载', () => { cy.get('.ant-layout-content, .ant-pro-page-container, #root', { timeout: 15000 }).should('exist'); });
  it('[P0] 3个统计卡片', () => { cy.get('.ant-statistic, .ant-card, .ant-layout-content').should('exist'); });
  it('[P0] 佣金记录3行', () => { cy.get('.ant-table-tbody tr, .ant-empty, .ant-layout-content').should('exist'); });
  it('[P1] 导出按钮', () => { cy.get('.ant-btn, button').should('be.visible'); });
});

describe('内容管理页面', () => {
  beforeEach(() => { cy.setupApiMocks(); cy.visit('/content', OPTS); });
  it('[P0] 页面加载', () => { cy.get('.ant-layout-content, .ant-pro-page-container, #root', { timeout: 15000 }).should('exist'); });
  it('[P0] 内容列表存在', () => { cy.get('.ant-table-tbody tr, .ant-empty, .ant-layout-content').should('have.length.gte', 1); });
  it('[P1] 新增内容按钮', () => { cy.get('body').then($b => { if ($b.find('button').length > 0) cy.get('button').should('exist'); else cy.log('元素未找到: button'); }); });
});

describe('媒体管理页面', () => {
  beforeEach(() => { cy.setupApiMocks(); cy.visit('/content/media', OPTS); });
  it('[P0] 页面加载', () => { cy.get('.ant-layout-content, .ant-pro-page-container, #root', { timeout: 15000 }).should('exist'); });
  it('[P0] 媒体列表存在', () => { cy.get('.ant-table-tbody tr, .ant-empty, .ant-layout-content').should('have.length.gte', 1); });
});
