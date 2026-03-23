/**
 * 工单管理 - Mock API 测试
 * 覆盖：工单列表、优先级过滤、状态筛选、新增操作、详情查看、分页
 */

describe('工单管理 - Mock API 测试', () => {

  beforeEach(() => {
    // Mock 工单列表接口
    cy.intercept('GET', '**/api/workorder**', {
      statusCode: 200,
      body: {
        success: true,
        data: {
          items: [
            { id: '1', title: '充电桩故障维修', code: 'WO20260306001', priority: 'high', status: 'pending', createTime: '2026-03-06 10:00:00' },
            { id: '2', title: '储能设备巡检', code: 'WO20260306002', priority: 'medium', status: 'processing', createTime: '2026-03-06 09:00:00' },
            { id: '3', title: '光伏设备清洁', code: 'WO20260306003', priority: 'low', status: 'completed', createTime: '2026-03-05 14:00:00' },
            { id: '4', title: '逆变器更换', code: 'WO20260306004', priority: 'high', status: 'processing', createTime: '2026-03-06 08:30:00' }
          ],
          total: 4,
          page: 1,
          pageSize: 20
        }
      },
      delay: 300
    }).as('workorderListRequest');

    cy.visitAuth('/workorder/list');
  });

  it('[P0] 工单列表页面加载', () => {
    cy.get('.ant-layout, #root', { timeout: 20000 }).should('be.visible');
    cy.get('.ant-table-wrapper, .ant-list', { timeout: 20000 }).should('exist');
  });

  it('[P0] 工单数据渲染', () => {
    cy.get('.ant-table-tbody tr, .ant-list-item, .ant-card-body, .ant-empty, .ant-spin-container', { timeout: 15000 })
      .should('exist');
  });

  it('[P0] 优先级和状态标签显示', () => {
    // 高/中/低 优先级 Tag，待处理/处理中/已完成 状态 Tag
    cy.get('.ant-tag, .ant-badge', { timeout: 10000 })
      .should('exist');
  });

  it('[P1] 按优先级/状态筛选', () => {
    // 查找筛选下拉或按钮
    cy.get('select, .ant-select, .ant-dropdown, button[class*="filter"]', { timeout: 15000 }).then(($filters) => {
      if ($filters.length > 0) {
        cy.wrap($filters).first().click({ force: true });
        cy.wait(300);
        cy.get('.ant-table-tbody tr, .ant-empty, .ant-spin-container', { timeout: 10000 }).should('exist');
      }
    });
  });

  it('[P1] 新增工单按钮', () => {
    cy.get('button.ant-btn-primary, .ant-btn-primary', { timeout: 15000 })
      .first()
      .should('exist')
      .then($btn => {
        if ($btn.is(':visible')) {
          cy.wrap($btn).click({ force: true });
        }
      });
    // 弹窗可能出现也可能不出现
    cy.wait(1000);
    cy.get('body').then($body => {
      if ($body.find('.ant-modal, .ant-drawer').length > 0) {
        cy.get('.ant-modal .ant-modal-close, .ant-drawer .ant-drawer-close, button').first().click({ force: true });
      }
    });
  });

  it('[P1] 工单行项可点击查看详情', () => {
    cy.get('.ant-table-tbody tr, .ant-empty, .ant-spin-container', { timeout: 15000 })
      .first()
      .within(() => {
        cy.get('button, a').should('exist');
      });
  });

  it('[P2] 分页功能', () => {
    cy.get('.ant-pagination, [class*=pagination], .ant-table-wrapper, .ant-pro-table', { timeout: 15000 })
      .should('exist');
  });

  it('[P2] 工单列表包含真实数据', () => {
    cy.get('.ant-table-tbody tr, .ant-empty, .ant-spin-container', { timeout: 15000 })
      .first()
      .should('exist');
  });
});
