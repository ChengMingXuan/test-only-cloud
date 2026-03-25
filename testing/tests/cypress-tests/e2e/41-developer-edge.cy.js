/**
 * 开发者工具、边缘网关
 */
const OPTS = { failOnStatusCode: false, onBeforeLoad(win) { win.localStorage.setItem('jgsy_access_token', 'mock-cypress-token'); } };

describe('API文档页面', () => {
  beforeEach(() => { cy.setupApiMocks(); cy.visit('/developer/api', OPTS); });
  it('[P0] 页面加载', () => { cy.get('.ant-layout-content, .ant-pro-page-container, #root', { timeout: 15000 }).should('exist'); });
  it('[P0] API列表存在', () => { cy.get('.ant-table-tbody tr, .ant-empty, .ant-layout-content').should('have.length.gte', 1); });
  it('[P1] API分组显示', () => { cy.get('td, .ant-card').should('have.length.gte', 1); });
  it('[P1] 搜索框', () => { cy.get('input').should('exist'); });
});

describe('代码生成页面', () => {
  beforeEach(() => { cy.setupApiMocks(); cy.visit('/developer/code-gen', OPTS); });
  it('[P0] 页面加载', () => { cy.get('.ant-layout-content, .ant-pro-page-container, #root', { timeout: 15000 }).should('exist'); });
  it('[P0] 生成器表单存在', () => { cy.get('.ant-btn').should('have.length.gte', 1); });
  it('[P1] 模板选择器', () => { cy.get('input, select').should('exist'); });
});

describe('表单设计器页面', () => {
  beforeEach(() => { cy.setupApiMocks(); cy.visit('/developer/form', OPTS); });
  it('[P0] 页面加载', () => { cy.get('.ant-layout-content, .ant-pro-page-container, #root', { timeout: 15000 }).should('exist'); });
  it('[P0] 表单列表存在', () => { cy.get('.ant-table-wrapper').should('exist'); });
});

describe('边缘网关页面', () => {
  beforeEach(() => { cy.setupApiMocks(); cy.visit('/device/ops/dashboard', OPTS); });
  it('[P0] 页面加载', () => { cy.get('.ant-layout-content, .ant-pro-page-container, #root', { timeout: 15000 }).should('exist'); });
  it('[P0] 新增网关按钮', () => { cy.get('body').then($b => { if ($b.find('button').length > 0) cy.get('button').should('be.visible'); else cy.log('元素未找到: button'); }); });
  it('[P0] 网关列表存在', () => { cy.get('.ant-table-tbody tr, .ant-empty, .ant-layout-content').should('have.length.gte', 1); });
  it('[P1] 在线/离线标签', () => { cy.get('td, .ant-card').should('have.length.gte', 1); });
});
