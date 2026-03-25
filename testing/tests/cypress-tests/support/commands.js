/**
 * Cypress 自定义命令
 * 规则：访问真实前端页面，后端接口按需使用 Mock 拦截。
 */

// ==================== 公共 Mock 数据 ====================

const MOCK_USER = {
  success: true, code: '200', message: 'OK',
  data: {
    id: 'user-001', username: 'admin', name: '系统管理员', realName: '系统管理员',
    email: 'admin@jgsy.com', phone: '13800138000', avatar: null,
    tenantId: 'tenant-001', tenantName: '演示租户', isAdmin: true,
    roles: [{ id: 'role-001', name: 'SUPER_ADMIN', displayName: '超级管理员' }],
    permissions: ['*'],
  },
  timestamp: new Date().toISOString(),
};

const MOCK_MENUS = {
  success: true, code: '200', message: 'OK',
  data: [
    { id: '1', name: '仪表盘', path: '/dashboard', icon: 'dashboard', type: 1, parentId: null, sort: 1, visible: true },
    { id: '2', name: '充电运营', path: '/charging', icon: 'thunderbolt', type: 1, parentId: null, sort: 2, visible: true,
      children: [{ id: '2-1', name: '充电订单', path: '/charging/orders', type: 1, parentId: '2', sort: 1, visible: true }],
    },
    { id: '3', name: '场站管理', path: '/station', icon: 'home', type: 1, parentId: null, sort: 3, visible: true },
    { id: '4', name: '设备管理', path: '/device', icon: 'tool', type: 1, parentId: null, sort: 4, visible: true },
    { id: '5', name: '工单管理', path: '/workorder', icon: 'fileText', type: 1, parentId: null, sort: 5, visible: true },
    { id: '6', name: '权限管理', path: '/permission', icon: 'lock', type: 1, parentId: null, sort: 6, visible: true },
    { id: '7', name: '用户管理', path: '/user', icon: 'team', type: 1, parentId: null, sort: 7, visible: true },
  ],
  timestamp: new Date().toISOString(),
};

// 分页列表通用 mock 工厂
function pagedMock(items) {
  return {
    success: true, code: '200', message: 'OK',
    data: { items, totalCount: items.length, total: items.length, pageIndex: 1, page: 1, pageSize: 20 },
    timestamp: new Date().toISOString(),
  };
}

// 单条 mock 工厂
function dataMock(data) {
  return { success: true, code: '200', message: 'OK', data, timestamp: new Date().toISOString() };
}

// ==================== 全局拦截设置 ====================

/**
 * 设置全局 API 拦截降级（兜底），再叠加认证和菜单拦截
 * 必须在 cy.visit() 之前调用
 */
Cypress.Commands.add('setupApiMocks', () => {
  // 兜底 Mock 数据：返回有效的列表/对象结构，避免前端组件因 data: null 崩溃
  const MOCK_ROW1 = { id: 'mock-1', name: 'Mock Item 1', status: 'active', code: 'M001', createTime: '2026-01-01T00:00:00Z', tenantId: 'tenant-001' };
  const MOCK_ROW2 = { id: 'mock-2', name: 'Mock Item 2', status: 'inactive', code: 'M002', createTime: '2026-01-02T00:00:00Z', tenantId: 'tenant-001' };
  const MOCK_ROW3 = { id: 'mock-3', name: 'Mock Item 3', status: 'active', code: 'M003', createTime: '2026-01-03T00:00:00Z', tenantId: 'tenant-001' };
  const fallback = {
    success: true, code: '200', message: 'OK',
    data: {
      ...MOCK_ROW1,  // 兼容单对象响应型 API
      list: [MOCK_ROW1, MOCK_ROW2, MOCK_ROW3],
      items: [MOCK_ROW1, MOCK_ROW2, MOCK_ROW3],
      records: [MOCK_ROW1, MOCK_ROW2, MOCK_ROW3],
      rows: [MOCK_ROW1, MOCK_ROW2, MOCK_ROW3],
      total: 100, page: 1, pageIndex: 1, pageNumber: 1,
      size: 20, pageSize: 20, totalPages: 5, hasNext: true,
    },
    timestamp: new Date().toISOString(),
  };

  // 兜底：所有未被具体拦截的 GET/POST/PUT/DELETE 返回 200
  cy.intercept('GET', '**/api/**', (req) => {
    if (!/\/api\/auth\/me|\/api\/menus\//.test(req.url)) {
      req.alias = 'listData';
    }
    req.reply(fallback);
  });
  cy.intercept('POST',   '**/api/**', fallback);
  cy.intercept('PUT',    '**/api/**', fallback);
  cy.intercept('DELETE', '**/api/**', fallback);

  // 认证（后置覆盖兜底）
  cy.intercept('GET', '**/api/auth/me', MOCK_USER).as('getMe');
  // 菜单接口返回空数组：前端代码检测 menuData.length > 0 才做路径鉴权，
  // 空菜单可绕过路由 403 检查，让测试页面正常加载
  cy.intercept('GET', '**/api/menus/current', { success: true, code: '200', data: [], timestamp: new Date().toISOString() }).as('getMenus');
  cy.intercept('GET', '**/api/auth/captcha', dataMock({ key: 'test-key', image: 'data:image/png;base64,iVBORw=' }));
  cy.intercept('POST', '**/api/auth/login', dataMock({
    success: true, accessToken: 'mock-token', user: MOCK_USER.data,
    token: { accessToken: 'mock-token', refreshToken: 'mock-refresh', expiresIn: 86400 },
  })).as('login');
  cy.intercept('POST', '**/api/auth/logout', { statusCode: 200, body: fallback });

  // 分析追踪（静默忽略）
  cy.intercept('POST', '**/analytics/**', { statusCode: 200, body: {} });
  cy.intercept('POST', '**/api/analytics/**', { statusCode: 200, body: {} });
  cy.intercept('GET',  '**/api/analytics/**', dataMock(null));

  // 模块能力
  cy.intercept('GET', '**/api/modules/**', dataMock([]));
  cy.intercept('GET', '**/api/capabilities/**', dataMock({}));

  // 站点 / 设备下拉选项
  cy.intercept('GET', '**/api/station/options', dataMock([]));
  cy.intercept('GET', '**/api/station/*/options', dataMock([]));
  cy.intercept('GET', '**/api/device/options', dataMock([]));

  // ========== 修复 JS 函数错误：返回数组格式的 API ==========
  
  // 部门树（用户管理页面调用 depts.map）
  cy.intercept('GET', '**/api/dept**', dataMock([
    { id: 'dept-1', name: '总公司', code: 'HQ', parentId: null, sort: 1,
      children: [
        { id: 'dept-2', name: '技术部', code: 'TECH', parentId: 'dept-1', sort: 1 },
        { id: 'dept-3', name: '运营部', code: 'OPS', parentId: 'dept-1', sort: 2 }
      ]
    }
  ]));
  cy.intercept('GET', '**/api/department**', dataMock([
    { id: 'dept-1', name: '总公司', code: 'HQ', parentId: null, sort: 1 }
  ]));

  // 权限列表（权限管理页面调用 perms.map）
  cy.intercept('GET', '**/api/perm**', dataMock([
    { id: 'perm-1', code: 'station:list', name: '查看场站', type: 'api', resource: 'station' },
    { id: 'perm-2', code: 'device:list', name: '查看设备', type: 'api', resource: 'device' },
    { id: 'perm-3', code: 'user:list', name: '查看用户', type: 'api', resource: 'user' }
  ]));

  // 设备类型/支持类型（AI/PHM 页面调用 supportedTypes.reduce）
  cy.intercept('GET', '**/api/device/types**', dataMock([
    { id: 'type-1', code: 'CHARGER', name: '充电桩', category: 'charging' },
    { id: 'type-2', code: 'PV', name: '光伏板', category: 'energy' },
    { id: 'type-3', code: 'BATTERY', name: '储能电池', category: 'storage' }
  ]));
  cy.intercept('GET', '**/api/device-type**', dataMock([
    { id: 'type-1', code: 'CHARGER', name: '充电桩' }
  ]));
  cy.intercept('GET', '**/api/supported-types**', dataMock([
    { id: 'type-1', code: 'CHARGER', name: '充电桩' }
  ]));

  // 区块链原始数据（调用 rawData.some）
  cy.intercept('GET', '**/api/blockchain/raw**', dataMock([]));
  cy.intercept('GET', '**/api/blockchain/transactions**', dataMock([]));
  cy.intercept('GET', '**/api/blockchain/wallet**', dataMock({ balance: '0', address: '0x0000' }));

  // 媒体/内容列表（调用 items.map）
  cy.intercept('GET', '**/api/media**', dataMock([]));
  cy.intercept('GET', '**/api/content**', dataMock([]));
  cy.intercept('GET', '**/api/agent/content**', dataMock([]));

  // PHM 健康数据
  cy.intercept('GET', '**/api/phm**', dataMock({
    score: 85,
    devices: [
      { id: 'd1', name: '设备1', healthScore: 90, riskLevel: 'low' },
      { id: 'd2', name: '设备2', healthScore: 75, riskLevel: 'medium' }
    ]
  }));
  cy.intercept('GET', '**/api/ai/phm**', dataMock({ score: 85, devices: [] }));
  cy.intercept('GET', '**/api/device/health**', dataMock({ devices: [] }));
});

/**
 * 访问需要登录的页面（自动注入 mock token + API 拦截）
 */
Cypress.Commands.add('visitAuth', (path, interceptsFn) => {
  if (typeof interceptsFn === 'function') {
    interceptsFn();
  }
  cy.visit(path, {
    failOnStatusCode: false,
    onBeforeLoad(win) {
      win.localStorage.setItem('jgsy_access_token', 'mock-cypress-test-token-12345');
      win.localStorage.setItem('jgsy_tenant_code', 'demo');
    },
  });
});

// 对常见交互控件的查询默认只保留可见元素，避免命中 Ant Design 的隐藏占位输入。
Cypress.Commands.overwrite('get', (originalFn, selector, options = {}) => {
  const result = originalFn(selector, options);

  if (typeof selector === 'string' && !selector.includes(':visible') && /(input|textarea|select|button)/.test(selector)) {
    return result.filter(':visible');
  }

  return result;
});

// ==================== 登录/登出 ====================

/** 模拟完整登录流程（用于登录页测试） */
Cypress.Commands.add('login', (username = 'admin@jgsy.com', password = 'P@ssw0rd') => {
  // 使用 localStorage 令牌注入方式模拟登录（避免依赖按钮文本）
  cy.setupApiMocks();
  cy.window().then((win) => {
    win.localStorage.setItem('jgsy_access_token', 'mock-cypress-token');
    win.localStorage.setItem('jgsy_tenant_code', 'demo');
    win.localStorage.setItem('jgsy_user', JSON.stringify({ name: username, admin: true }));
  });
});

/** 清除登录状态 */
Cypress.Commands.add('logout', () => {
  cy.window().then((win) => {
    win.localStorage.removeItem('jgsy_access_token');
  });
});

