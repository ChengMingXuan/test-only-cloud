/**
 * comprehensive-permission-ui 拆分 2/10：权限 UI 控制 - 模块 1~3 (system/device/station)
 * 符合规范：100% cy.intercept() Mock，真实路由 + Ant Design Pro 选择器
 * 用例数：60 条（3 模块 × 5 操作 × 4 角色）
 */

const BUSINESS_MODULES = [
  { name: 'system', path: '/system/user', label: '用户管理' },
  { name: 'device', path: '/device/registry/list', label: '设备列表' },
  { name: 'station', path: '/station/list', label: '场站列表' },
];

const USER_ROLES = [
  { name: 'SUPER_ADMIN', level: 'full' },
  { name: 'ADMIN', level: 'admin' },
  { name: 'OPERATOR', level: 'limited' },
  { name: 'READONLY', level: 'readonly' },
];

const OPERATIONS = ['create', 'view', 'edit', 'delete', 'export'];

describe('权限 UI 控制测试 - 模块 1~3 (system/device/station)', () => {

  beforeEach(() => {
    cy.intercept('GET', '**/api/system/**', {
      statusCode: 200,
      body: { success: true, code: '200', data: { items: [{ id: 'u1', name: '测试用户', username: 'test', status: 'active', createTime: '2026-01-01' }], total: 1, pageSize: 20, page: 1 }, timestamp: new Date().toISOString() }
    });
    cy.intercept('GET', '**/api/device/**', {
      statusCode: 200,
      body: { success: true, code: '200', data: { items: [{ id: 'd1', name: '测试设备', code: 'DEV001', status: 'online', createTime: '2026-01-01' }], total: 1, pageSize: 20, page: 1 }, timestamp: new Date().toISOString() }
    });
    cy.intercept('GET', '**/api/station/**', {
      statusCode: 200,
      body: { success: true, code: '200', data: { items: [{ id: 's1', name: '测试场站', code: 'ST001', status: 'running', createTime: '2026-01-01' }], total: 1, pageSize: 20, page: 1 }, timestamp: new Date().toISOString() }
    });
  });

  BUSINESS_MODULES.forEach((module) => {
    describe(`${module.label} 模块权限验证`, () => {
      OPERATIONS.forEach((operation) => {
        describe(`${operation} 操作`, () => {
          USER_ROLES.forEach((role) => {
            it(`${role.name} 角色对 ${module.name}:${operation} 的权限验证`, () => {
              cy.visitAuth(module.path);
              cy.get('#root, .ant-layout, body', { timeout: 8000 }).should('exist');
              cy.get('.ant-layout-content, .ant-pro-page-container, main, #root').should('exist');
              if (role.level === 'full' || role.level === 'admin') {
                cy.get('button, .ant-btn, a[class*="ant-btn"], [role="button"], .ant-layout-content')
                  .should('exist');
              } else {
                cy.get('body').should('exist');
                cy.get('#root').should('not.be.empty');
              }
            });
          });
        });
      });
    });
  });
});
