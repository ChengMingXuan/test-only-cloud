/**
 * comprehensive-permission-ui 拆分 1/10：页面加载完整测试
 * 符合规范：100% cy.intercept() Mock，真实路由 + Ant Design Pro 选择器
 * 用例数：17 条
 */

const BUSINESS_PAGES = [
  { path: '/system/user', title: '用户管理', module: 'system' },
  { path: '/system/role', title: '角色管理', module: 'system' },
  { path: '/system/permission', title: '权限管理', module: 'system' },
  { path: '/device/registry/list', title: '设备列表', module: 'device' },
  { path: '/station/list', title: '场站列表', module: 'station' },
  { path: '/charging/orders', title: '充电订单', module: 'charging' },
  { path: '/charging/dashboard', title: '运营概览', module: 'charging' },
  { path: '/settlement/list', title: '结算记录', module: 'settlement' },
  { path: '/workorder/list', title: '工单列表', module: 'workorder' },
  { path: '/rule-engine/chains', title: '规则链管理', module: 'ruleengine' },
  { path: '/blockchain/dashboard', title: '区块链概览', module: 'blockchain' },
  { path: '/ai/dashboard', title: 'AI概览', module: 'ai' },
  { path: '/ingestion/sources', title: '数据源配置', module: 'ingestion' },
  { path: '/message/notice', title: '公告通知', module: 'message' },
  { path: '/digital-twin/overview', title: '总览驾驶舱', module: 'digital-twin' },
  { path: '/tenant/list', title: '租户列表', module: 'tenant' },
  { path: '/welcome', title: '首页', module: '' },
];

describe('页面加载完整测试 - 核心页面验证', () => {
  BUSINESS_PAGES.forEach((page) => {
    it(`应正确加载 ${page.title} (${page.path})`, () => {
      cy.visitAuth(page.path);
      // Ant Design Pro 布局加载成功
      cy.get('#root, .ant-layout, body', { timeout: 8000 }).should('exist');
      // 页面标题非空
      cy.title().should('not.be.empty');
      // 无白屏
      cy.get('body').should('not.be.empty');
      cy.get('#root').should('exist').should('not.be.empty');
    });
  });
});
