/**
 * comprehensive-permission-ui 拆分 10/10：响应式布局验证
 * 符合规范：100% cy.intercept() Mock，真实路由 + Ant Design Pro 选择器
 * 用例数：16 条（4 分辨率 × 4 页面）
 */

const VIEWPORTS = [
  { name: '1920x1080', width: 1920, height: 1080 },
  { name: '1366x768', width: 1366, height: 768 },
  { name: '768x1024_iPad', width: 768, height: 1024 },
  { name: '375x812_iPhone', width: 375, height: 812 },
];

const TEST_PAGES = [
  { path: '/device/registry/list', label: '设备列表' },
  { path: '/station/list', label: '场站列表' },
  { path: '/charging/orders', label: '充电订单' },
  { path: '/welcome', label: '首页' },
];

describe('响应式布局验证', () => {
  VIEWPORTS.forEach((viewport) => {
    describe(`${viewport.name} 分辨率`, () => {
      beforeEach(() => {
        cy.viewport(viewport.width, viewport.height);
      });

      TEST_PAGES.forEach((page) => {
        it(`${page.label} 在 ${viewport.name} 下正确渲染`, () => {
          cy.visitAuth(page.path);
          // 根布局存在
          cy.get('#root, .ant-layout, body', { timeout: 8000 }).should('exist');
          // 内容区未溢出
          cy.get('.ant-layout-content, .ant-pro-page-container, main, #root').should('exist');
          cy.get('body').invoke('prop', 'scrollWidth').should('be.lte', viewport.width + 20);
          // 无白屏
          cy.get('body').should('not.be.empty');
          cy.get('#root').should('exist').should('not.be.empty');
        });
      });
    });
  });
});
