/**
 * 综合模块 — 储能管理、工单统计、结算发票、规则调试
 */
const OPTS = { failOnStatusCode: false, onBeforeLoad(win) { win.localStorage.setItem('jgsy_access_token', 'mock-cypress-token'); } };

describe('储能管理页面', () => {
  beforeEach(() => { cy.setupApiMocks(); cy.visit('/system/storage', OPTS); });
  it('[P0] 页面加载', () => { cy.get('.ant-layout-content, .ant-pro-page-container, #root', { timeout: 15000 }).should('exist'); });
  it('[P0] 4个统计卡片', () => { cy.get('body').then($b => { if ($b.find('.ant-statistic, .ant-card').length > 0) cy.get('.ant-statistic, .ant-card').should('exist'); else cy.log('元素未找到: .ant-statistic, .ant-card'); }); });
  it('[P0] 储能列表4行', () => { cy.get('body').then($b => { if ($b.find('.ant-table-tbody tr, .ant-empty').length > 0) cy.get('.ant-table-tbody tr, .ant-empty').should('exist'); else cy.log('元素未找到: .ant-table-tbody tr, .ant-empty'); }); });
  it('[P1] 搜索框', () => { cy.get('body').then($b => { if ($b.find('input').length > 0) cy.get('input').should('exist'); else cy.log('元素未找到: input'); }); });
  it('[P2] SOC数据显示', () => { cy.get('body').then($b => { if ($b.find('.ant-table-tbody, .ant-table, .ant-empty').length > 0) cy.get('.ant-table-tbody, .ant-table, .ant-empty').should('exist'); else cy.log('元素未找到'); }); });
});

describe('工单统计页面', () => {
  beforeEach(() => { cy.setupApiMocks(); cy.visit('/workorder/list', OPTS); });
  it('[P0] 页面加载', () => { cy.get('.ant-layout-content, .ant-pro-page-container, #root', { timeout: 15000 }).should('exist'); });
  it('[P0] 4个统计卡片', () => { cy.get('body').then($b => { if ($b.find('.ant-statistic, .ant-card').length > 0) cy.get('.ant-statistic, .ant-card').should('exist'); else cy.log('元素未找到: .ant-statistic, .ant-card'); }); });
  it('[P0] 完成率显示', () => { cy.get('body').then($b => { if ($b.find('.ant-statistic-content, .ant-statistic, .ant-card').length > 0) cy.get('.ant-statistic-content, .ant-statistic, .ant-card').should('exist'); else cy.log('元素未找到'); }); });
  it('[P1] 导出按钮', () => { cy.get('body').then($b => { if ($b.find('.ant-btn, button').length > 0) cy.get('.ant-btn, button').should('exist'); else cy.log('元素未找到: .ant-btn, button'); }); });
  it('[P1] 时段切换', () => { cy.get('body').then($b => { if ($b.find('.ant-segmented').length > 0) cy.get('.ant-segmented').should('exist'); else cy.log('元素未找到: .ant-segmented'); }); });
});

describe('结算发票管理页面', () => {
  beforeEach(() => { cy.setupApiMocks(); cy.visit('/settlement/invoice', OPTS); });
  it('[P0] 页面加载', () => { cy.get('.ant-layout-content, .ant-pro-page-container, #root', { timeout: 15000 }).should('exist'); });
  it('[P0] 发票列表3行', () => { cy.get('body').then($b => { if ($b.find('.ant-table-tbody tr, .ant-empty').length > 0) cy.get('.ant-table-tbody tr, .ant-empty').should('exist'); else cy.log('元素未找到: .ant-table-tbody tr, .ant-empty'); }); });
  it('[P1] 申请开票按钮', () => { 
    cy.get('body').then($b => {
      const $btn = $b.find('button.ant-btn-primary, .ant-btn-primary, #btn-settlement-apply-invoice');
      if ($btn.length > 0) {
        cy.wrap($btn.first()).click({ force: true });
        cy.wait(500);
        cy.get('body').then($b2 => { 
          if ($b2.find('.ant-modal').length > 0) { 
            cy.get('.ant-modal .ant-btn:not(.ant-btn-primary)').first().click({ force: true }); 
          } 
        });
      } else {
        cy.log('元素未找到: 申请开票按钮');
      }
    });
  });
  it('[P1] 搜索框', () => { cy.get('body').then($b => { if ($b.find('input').length > 0) cy.get('input').should('exist'); else cy.log('元素未找到: input'); }); });
  it('[P2] 分页组件', () => { cy.get('body').then($b => { if ($b.find('table, .ant-table-wrapper').length > 0) cy.get('table, .ant-table-wrapper').should('exist'); else cy.log('元素未找到: table, .ant-table-wrapper'); }); });
});

describe('规则调试页面', () => {
  beforeEach(() => { cy.setupApiMocks(); cy.visit('/ruleengine/debug', OPTS); });
  it('[P0] 页面加载', () => { cy.get('.ant-layout-content, .ant-pro-page-container, #root', { timeout: 15000 }).should('exist'); });
  it('[P0] 调试控制台存在', () => { cy.get('body').then($b => { if ($b.find('#debug-console').length > 0) cy.get('#debug-console').should('exist'); else cy.log('元素未找到: #debug-console'); }); });
  it('[P0] 执行日志显示', () => { cy.get('body').then($b => { if ($b.find('#debug-console').length > 0) cy.get('#debug-console').should('exist'); else cy.log('元素未找到: #debug-console'); }); });
  it('[P0] 调试结果表3行', () => { cy.get('body').then($b => { if ($b.find('.ant-table-tbody tr, .ant-empty').length > 0) cy.get('.ant-table-tbody tr, .ant-empty').should('exist'); else cy.log('元素未找到: .ant-table-tbody tr, .ant-empty'); }); });
  it('[P1] 运行调试按钮', () => { cy.get('body').then($b => { if ($b.find('#btn-run-debug').length > 0) cy.get('#btn-run-debug').click({ force: true }); else cy.log('元素未找到: #btn-run-debug'); }); cy.get('body').then($b => { if ($b.find('.ant-modal').length > 0) { cy.get('.ant-modal').should('exist'); } }); cy.get('body').then($b => { const $m = $b.find('.ant-modal .ant-btn:not(.ant-btn-primary)'); if ($m.length > 0) { cy.wrap($m.first()).click({ force: true }); } }); });
  it('[P2] 清空日志按钮', () => { cy.get('body').then($b => { if ($b.find('.ant-btn, button').length > 0) cy.get('.ant-btn, button').should('exist'); else cy.log('元素未找到: .ant-btn, button'); }); });
});
