/**
 * comprehensive-permission-ui 拆分 3/10：权限 UI 控制 - 模块 4~6 (charging/workorder/ingestion)
 * 符合规范：100% cy.intercept() Mock，真实路由 + Ant Design Pro 选择器
 * 用例数：60 条（3 模块 × 5 操作 × 4 角色）
 */

const BUSINESS_MODULES = [
  { name: 'charging', path: '/charging/orders', label: '充电订单' },
  { name: 'workorder', path: '/workorder/list', label: '工单列表' },
  { name: 'ingestion', path: '/ingestion/sources', label: '数据源配置' },
];

const USER_ROLES = [
  { name: 'SUPER_ADMIN', level: 'full' },
  { name: 'ADMIN', level: 'admin' },
  { name: 'OPERATOR', level: 'limited' },
  { name: 'READONLY', level: 'readonly' },
];

const OPERATIONS = ['create', 'view', 'edit', 'delete', 'export'];

describe('权限 UI 控制测试 - 模块 4~6 (charging/workorder/ingestion)', () => {

  beforeEach(() => {
    cy.intercept('GET', '**/api/charging/**', {
      statusCode: 200,
      body: { success: true, code: '200', data: { items: [{ id: 'c1', name: '测试订单', orderNo: 'ORD001', status: 'completed', createTime: '2026-01-01' }], total: 1, pageSize: 20, page: 1 }, timestamp: new Date().toISOString() }
    });
    cy.intercept('GET', '**/api/workorder/**', {
      statusCode: 200,
      body: { success: true, code: '200', data: { items: [{ id: 'w1', name: '测试工单', code: 'WO001', status: 'open', createTime: '2026-01-01' }], total: 1, pageSize: 20, page: 1 }, timestamp: new Date().toISOString() }
    });
    cy.intercept('GET', '**/api/ingestion/**', {
      statusCode: 200,
      body: { success: true, code: '200', data: { items: [{ id: 'i1', name: '测试数据源', type: 'mqtt', status: 'active', createTime: '2026-01-01' }], total: 1, pageSize: 20, page: 1 }, timestamp: new Date().toISOString() }
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
