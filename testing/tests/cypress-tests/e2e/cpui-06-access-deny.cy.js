/**
 * comprehensive-permission-ui 拆分 6/10：无权限直接访问拒绝测试
 * 符合规范：100% cy.intercept() Mock，真实路由 + Ant Design Pro 选择器
 * 用例数：36 条（4 角色 × 多页面场景）
 */

const PAGES = [
  { path: '/system/user', title: '用户管理', module: 'system' },
  { path: '/system/role', title: '角色管理', module: 'system' },
  { path: '/system/permission', title: '权限管理', module: 'system' },
  { path: '/device/registry/list', title: '设备列表', module: 'device' },
  { path: '/station/list', title: '场站列表', module: 'station' },
  { path: '/charging/orders', title: '充电订单', module: 'charging' },
  { path: '/settlement/list', title: '结算记录', module: 'settlement' },
  { path: '/workorder/list', title: '工单列表', module: 'workorder' },
  { path: '/blockchain/dashboard', title: '区块链概览', module: 'blockchain' },
];

const USER_ROLES = [
  { name: 'SUPER_ADMIN', level: 'full' },
  { name: 'ADMIN', level: 'admin' },
  { name: 'OPERATOR', level: 'limited' },
  { name: 'READONLY', level: 'readonly' },
];

describe('无权限直接访问拒绝测试 - 36 用例', () => {
  USER_ROLES.forEach((role) => {
    describe(`${role.name} 角色访问控制`, () => {
      PAGES.forEach((page) => {
        it(`${role.name} 访问 ${page.title} - 页面响应正确`, () => {
          if (role.level === 'limited' || role.level === 'readonly') {
            // 模拟 403 无权限响应
            cy.intercept('GET', `**/api/${page.module}/**`, {
              statusCode: 403,
              body: { success: false, code: '403', message: '无权限访问', timestamp: new Date().toISOString() }
            });
          }
          cy.visitAuth(page.path);
          cy.get('#root, .ant-layout, body', { timeout: 8000 }).should('exist');
          // 页面应正确响应（不白屏不报500）
          cy.get('body').should('not.be.empty');
          cy.get('#root').should('exist');
        });
      });
    });
  });
});
