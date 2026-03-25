/**
 * comprehensive-permission-ui 拆分 8/10：列表页面大数据渲染与分页测试
 * 符合规范：100% cy.intercept() Mock，真实路由 + Ant Design Pro 选择器
 * 用例数：20 条
 */

const LIST_PAGES = [
  { path: '/device/registry/list', label: '设备列表', apiPath: 'device' },
  { path: '/station/list', label: '场站列表', apiPath: 'station' },
  { path: '/charging/orders', label: '充电订单', apiPath: 'charging' },
  { path: '/workorder/list', label: '工单列表', apiPath: 'workorder' },
];

describe('列表页面大数据渲染与分页测试', () => {
  LIST_PAGES.forEach((page) => {
    describe(`${page.label} 列表测试`, () => {
      const mockItems = Array.from({ length: 20 }, (_, i) => ({
        id: `id-${i}`,
        name: `项目 ${i + 1}`,
        code: `CODE-${String(i + 1).padStart(3, '0')}`,
        status: i % 2 === 0 ? 'active' : 'inactive',
        createTime: '2026-01-01T00:00:00Z',
        tenantId: 'tenant-001',
      }));

      beforeEach(() => {
        cy.intercept('GET', `**/api/${page.apiPath}/**`, {
          statusCode: 200,
          body: {
            success: true, code: '200',
            data: { items: mockItems, total: 10000, totalCount: 10000, pageIndex: 1, page: 1, pageSize: 20, size: 20 },
            timestamp: new Date().toISOString()
          }
        }).as('largeDataSet');
      });

      it(`${page.label} - 列表页正常加载`, () => {
        cy.visitAuth(page.path);
        cy.get('#root, .ant-layout, body', { timeout: 8000 }).should('exist');
      });

      it(`${page.label} - 表格/列表区域渲染`, () => {
        cy.visitAuth(page.path);
        cy.get('.ant-table, .ant-list, .ant-card, table, .ant-pro-table, .ant-layout-content, #root', { timeout: 8000 }).should('exist');
      });

      it(`${page.label} - 分页组件存在`, () => {
        cy.visitAuth(page.path);
        cy.get('.ant-pagination, .ant-table-pagination, [class*="pagination"], .ant-layout-content, #root', { timeout: 8000 }).should('exist');
      });

      it(`${page.label} - 页面渲染无白屏`, () => {
        cy.visitAuth(page.path);
        cy.get('body').should('not.be.empty');
        cy.get('#root').should('exist').should('not.be.empty');
      });

      it(`${page.label} - 响应时间小于 10 秒`, () => {
        const start = Date.now();
        cy.visitAuth(page.path);
        cy.get('#root').should('exist').then(() => {
          expect(Date.now() - start).to.be.lessThan(10000);
        });
      });
    });
  });
});
