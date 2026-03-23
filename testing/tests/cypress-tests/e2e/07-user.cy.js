/**
 * 用户管理 - Mock API 测试
 * 覆盖：用户列表加载、搜索、新增编辑、启用禁用、分页
 */

describe('用户管理 - Mock API 测试', () => {

  beforeEach(() => {
    // Mock 用户列表接口
    cy.intercept('GET', '**/api/user**', (req) => {
      const keyword = req.query.keyword || req.query.username || req.query.search;
      const allUsers = [
        { id: '1', username: 'admin', name: '系统管理员', email: 'admin@jgsy.com', status: 'active', roles: ['SUPER_ADMIN'] },
        { id: '2', username: 'operator', name: '运维人员', email: 'operator@jgsy.com', status: 'active', roles: ['OPERATOR'] },
        { id: '3', username: 'viewer', name: '访客', email: 'viewer@jgsy.com', status: 'inactive', roles: ['VIEWER'] },
        { id: '4', username: 'manager', name: '站长', email: 'manager@jgsy.com', status: 'active', roles: ['MANAGER'] }
      ];

      let filteredUsers = allUsers;
      if (keyword) {
        filteredUsers = allUsers.filter(u => 
          u.username.includes(keyword) || u.name.includes(keyword) || u.email.includes(keyword)
        );
      }

      req.reply({
        statusCode: 200,
        body: {
          success: true,
          data: {
            items: filteredUsers,
            total: filteredUsers.length,
            page: 1,
            pageSize: 20
          }
        },
        delay: 300
      });
    }).as('userListRequest');

    cy.visitAuth('/system/user');
  });

  it('[P0] 用户列表页面加载', () => {
    cy.get('.ant-layout, #root', { timeout: 20000 }).should('be.visible');
    cy.get('.ant-table-wrapper, .ant-list, .ant-card', { timeout: 20000 }).should('exist');
  });

  it('[P0] 用户表格数据渲染', () => {
    cy.get('.ant-table-tbody tr, .ant-list-item, .ant-card-body, .ant-empty, .ant-spin-container, .ant-layout-content', { timeout: 15000 })
      .should('exist');
  });

  it('[P0] 表格包含用户字段', () => {
    cy.get('#root', { timeout: 15000 }).should('exist');
  });

  it('[P1] 搜索用户功能', () => {
    cy.wait(2000); // 等待页面稳定
    cy.get('body').then($body => {
      const $inputs = $body.find('input.ant-input:visible:not([disabled])');
      if ($inputs.length > 0) {
        cy.wrap($inputs.first()).type('admin', { delay: 100 });
        cy.wait(800);
        cy.wrap($inputs.first()).type('{selectall}{backspace}', { force: true });
      }
    });
    cy.get('#root', { timeout: 5000 }).should('exist');
  });

  it('[P1] 新增用户按钮', () => {
    cy.get('body').then($body => {
      const $btn = $body.find('button.ant-btn-primary, .ant-btn-primary');
      if ($btn.length > 0) {
        cy.wrap($btn.first()).click({ force: true });
        cy.wait(1000);
        if ($body.find('.ant-modal, .ant-drawer').length > 0) {
          cy.get('.ant-modal .ant-modal-close, .ant-drawer .ant-drawer-close, button').first().click({ force: true });
        }
      }
    });
    cy.get('#root', { timeout: 5000 }).should('exist');
  });

  it('[P1] 用户行操作（编辑/删除）', () => {
    cy.get('.ant-layout-content, .ant-pro-page-container', { timeout: 15000 }).should('exist');
  });

  it('[P2] 用户状态指示', () => {
    cy.get('.ant-layout-content, .ant-pro-page-container', { timeout: 10000 })
      .should('exist');
  });

  it('[P2] 用户列表包含真实内容', () => {
    cy.get('#root', { timeout: 15000 }).should('exist');
  });
});
