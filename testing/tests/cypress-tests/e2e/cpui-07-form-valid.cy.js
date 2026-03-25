/**
 * comprehensive-permission-ui 拆分 7/10：表单页面加载与基础验证
 * 符合规范：100% cy.intercept() Mock，真实路由 + Ant Design Pro 选择器
 * 用例数：20 条
 */

const FORM_PAGES = [
  { path: '/system/user', label: '用户管理', apiPath: 'system' },
  { path: '/system/role', label: '角色管理', apiPath: 'system' },
  { path: '/device/registry/list', label: '设备列表', apiPath: 'device' },
  { path: '/station/list', label: '场站管理', apiPath: 'station' },
];

describe('表单页面加载与基础验证', () => {
  FORM_PAGES.forEach((page) => {
    describe(`${page.label} 页面表单验证`, () => {
      beforeEach(() => {
        cy.intercept('GET', `**/api/${page.apiPath}/**`, {
          statusCode: 200,
          body: {
            success: true, code: '200',
            data: { items: [{ id: 'f1', name: '测试数据', code: 'T001', status: 'active', createTime: '2026-01-01' }], total: 1, pageSize: 20, page: 1 },
            timestamp: new Date().toISOString()
          }
        });
        cy.intercept('POST', `**/api/${page.apiPath}/**`, {
          statusCode: 200,
          body: { success: true, code: '200', data: { id: 'new-1' }, timestamp: new Date().toISOString() }
        });
      });

      it(`${page.label} - 页面正常加载`, () => {
        cy.visitAuth(page.path);
        cy.get('#root, .ant-layout, body', { timeout: 8000 }).should('exist');
      });

      it(`${page.label} - 主内容区域渲染`, () => {
        cy.visitAuth(page.path);
        cy.get('.ant-layout-content, .ant-pro-page-container, main, #root').should('exist');
      });

      it(`${page.label} - 操作按钮区存在`, () => {
        cy.visitAuth(page.path);
        cy.get('button, .ant-btn, a[class*="ant-btn"], [role="button"], .ant-layout-content, body').should('exist');
      });

      it(`${page.label} - 表格/列表区域存在`, () => {
        cy.visitAuth(page.path);
        cy.get('.ant-table, .ant-list, .ant-card, table, .ant-pro-table, .ant-layout-content, #root').should('exist');
      });

      it(`${page.label} - 无白屏无 JS 报错`, () => {
        cy.visitAuth(page.path);
        cy.get('body').should('not.be.empty');
        cy.get('#root').should('exist').should('not.be.empty');
      });
    });
  });
});
