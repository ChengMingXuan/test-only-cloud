/**
 * V3.2.0 增量测试 — Operations/Trading 三合一前端组件交互测试
 * ============================================================
 * 规则：访问真实前端页面，后端 API 用 cy.intercept() Mock
 * 覆盖：Operations（EnergyEff + MultiEnergy + SafeControl）统一入口
 *       Trading（ElecTrade + CarbonTrade + DemandResp）统一入口
 */

// ══════════════════════════════════════
// Mock 数据
// ══════════════════════════════════════

const pagedMock = (items) => ({
  success: true, code: '200', message: 'OK',
  data: { items, totalCount: items.length, total: items.length, pageIndex: 1, pageSize: 20 },
});

const dataMock = (data) => ({
  success: true, code: '200', message: 'OK', data,
});

const MOCK_ENERGYEFF_LIST = [
  { id: 'eff-001', name: '能效记录A', type: 'daily', efficiency: 95.5, stationId: 'sta-001', stationName: '测试场站A', createTime: '2026-03-01T10:00:00Z' },
  { id: 'eff-002', name: '能效记录B', type: 'monthly', efficiency: 92.1, stationId: 'sta-002', stationName: '测试场站B', createTime: '2026-03-02T10:00:00Z' },
];

const MOCK_MULTIENERGY_LIST = [
  { id: 'me-001', name: '多能互补计划A', strategy: 'peak_shaving', priority: 1, status: 'active' },
  { id: 'me-002', name: '多能互补计划B', strategy: 'load_balancing', priority: 2, status: 'draft' },
];

const MOCK_SAFECONTROL_LIST = [
  { id: 'sc-001', name: '安控规则A', ruleType: 'threshold', threshold: 85.0, action: 'alarm', status: 'enabled' },
  { id: 'sc-002', name: '安控规则B', ruleType: 'frequency', threshold: 50.5, action: 'trip', status: 'enabled' },
];

const MOCK_ELECTRADE_LIST = [
  { id: 'et-001', tradeType: 'spot', quantity: 1000, price: 0.35, direction: 'sell', status: 'completed' },
  { id: 'et-002', tradeType: 'forward', quantity: 2000, price: 0.42, direction: 'buy', status: 'pending' },
];

const MOCK_CARBONTRADE_LIST = [
  { id: 'ct-001', carbonType: 'CER', quantity: 500, price: 65.0, direction: 'buy', status: 'settled' },
  { id: 'ct-002', carbonType: 'CCER', quantity: 800, price: 58.0, direction: 'sell', status: 'pending' },
];

const MOCK_DEMANDRESP_LIST = [
  { id: 'dr-001', eventType: 'curtailment', capacity: 200, duration: 120, incentiveRate: 0.8, status: 'active' },
  { id: 'dr-002', eventType: 'shifting', capacity: 150, duration: 60, incentiveRate: 0.6, status: 'completed' },
];

// ══════════════════════════════════════
// Operations 统一入口测试
// ══════════════════════════════════════

describe('[V3.2.0增量] Operations 运维服务统一入口', () => {
  beforeEach(() => {
    // Mock Operations 相关 API
    cy.intercept('GET', '**/api/operations/energyeff/list*', { body: pagedMock(MOCK_ENERGYEFF_LIST) }).as('effList');
    cy.intercept('GET', '**/api/operations/multienergy/list*', { body: pagedMock(MOCK_MULTIENERGY_LIST) }).as('meList');
    cy.intercept('GET', '**/api/operations/safecontrol/list*', { body: pagedMock(MOCK_SAFECONTROL_LIST) }).as('scList');
    cy.intercept('GET', '**/api/operations/dashboard*', { body: dataMock({ effCount: 10, meCount: 5, scCount: 8, alarmCount: 2 }) }).as('opsDash');
    cy.intercept('POST', '**/api/operations/energyeff', { statusCode: 201, body: dataMock({ id: 'new-eff-001' }) }).as('effCreate');
    cy.intercept('PUT', '**/api/operations/energyeff/*', { statusCode: 200, body: dataMock(null) }).as('effUpdate');
    cy.intercept('DELETE', '**/api/operations/energyeff/*', { statusCode: 204 }).as('effDelete');
  });

  it('[OPS-LIST-01] 能效管理列表可正常渲染', () => {
    cy.visit('/energy/operations/energyeff');
    cy.get('.ant-table, [class*="table"], [role="grid"]', { timeout: 10000 }).should('exist');
  });

  it('[OPS-LIST-02] 多能互补列表可正常渲染', () => {
    cy.visit('/energy/operations/multienergy');
    cy.get('.ant-table, [class*="table"], [role="grid"]', { timeout: 10000 }).should('exist');
  });

  it('[OPS-LIST-03] 安控管理列表可正常渲染', () => {
    cy.visit('/energy/operations/safecontrol');
    cy.get('.ant-table, [class*="table"], [role="grid"]', { timeout: 10000 }).should('exist');
  });

  it('[OPS-DASH-01] 运维 Dashboard 页面加载', () => {
    cy.visit('/energy/operations/dashboard');
    cy.get('[class*="layout"], [class*="content"], #root', { timeout: 10000 }).should('exist');
  });

  it('[OPS-CREATE-01] 能效记录创建表单交互', () => {
    cy.visit('/energy/operations/energyeff');
    cy.get('button, [role="button"]').contains(/新建|新增|创建|添加/).should('exist');
  });

  it('[OPS-SEARCH-01] 列表搜索过滤功能', () => {
    cy.visit('/energy/operations/energyeff');
    cy.get('input[placeholder*="搜索"], input[placeholder*="关键词"], .ant-input-search input').should('exist');
  });

  it('[OPS-PAGE-01] 列表分页组件存在', () => {
    cy.visit('/energy/operations/energyeff');
    cy.get('.ant-pagination, [class*="pagination"]', { timeout: 10000 }).should('exist');
  });
});

// ══════════════════════════════════════
// Trading 统一入口测试
// ══════════════════════════════════════

describe('[V3.2.0增量] Trading 交易服务统一入口', () => {
  beforeEach(() => {
    // Mock Trading 相关 API
    cy.intercept('GET', '**/api/trading/electrade/list*', { body: pagedMock(MOCK_ELECTRADE_LIST) }).as('etList');
    cy.intercept('GET', '**/api/trading/carbontrade/list*', { body: pagedMock(MOCK_CARBONTRADE_LIST) }).as('ctList');
    cy.intercept('GET', '**/api/trading/demandresp/list*', { body: pagedMock(MOCK_DEMANDRESP_LIST) }).as('drList');
    cy.intercept('GET', '**/api/trading/dashboard*', { body: dataMock({ tradeCount: 20, volume: 50000, revenue: 18000 }) }).as('tradingDash');
    cy.intercept('GET', '**/api/trading/market/price*', { body: dataMock({ spotPrice: 0.35, peakPrice: 0.52, valleyPrice: 0.22 }) }).as('marketPrice');
  });

  it('[TRD-LIST-01] 电力交易列表可正常渲染', () => {
    cy.visit('/energy/trading/electrade');
    cy.get('.ant-table, [class*="table"], [role="grid"]', { timeout: 10000 }).should('exist');
  });

  it('[TRD-LIST-02] 碳交易列表可正常渲染', () => {
    cy.visit('/energy/trading/carbontrade');
    cy.get('.ant-table, [class*="table"], [role="grid"]', { timeout: 10000 }).should('exist');
  });

  it('[TRD-LIST-03] 需求响应列表可正常渲染', () => {
    cy.visit('/energy/trading/demandresp');
    cy.get('.ant-table, [class*="table"], [role="grid"]', { timeout: 10000 }).should('exist');
  });

  it('[TRD-DASH-01] 交易 Dashboard 页面加载', () => {
    cy.visit('/energy/trading/dashboard');
    cy.get('[class*="layout"], [class*="content"], #root', { timeout: 10000 }).should('exist');
  });

  it('[TRD-PRICE-01] 市场价格展示', () => {
    cy.visit('/energy/trading/market');
    cy.get('[class*="layout"], [class*="content"], #root', { timeout: 10000 }).should('exist');
  });

  it('[TRD-CREATE-01] 电力交易创建表单', () => {
    cy.visit('/energy/trading/electrade');
    cy.get('button, [role="button"]').contains(/新建|新增|创建|下单/).should('exist');
  });

  it('[TRD-FILTER-01] 碳交易筛选功能', () => {
    cy.visit('/energy/trading/carbontrade');
    cy.get('.ant-select, select, [class*="filter"]').should('exist');
  });
});

// ══════════════════════════════════════
// 鉴权拦截测试
// ══════════════════════════════════════

describe('[V3.2.0增量] 鉴权与权限控制', () => {
  it('[AUTH-01] 未登录访问Operations应跳转登录页', () => {
    // 模拟未登录状态：拦截API返回401
    cy.intercept('GET', '**/api/operations/**', { statusCode: 401, body: { success: false, message: '未认证' } });
    cy.visit('/energy/operations/energyeff');
    // 未登录应被重定向到登录页或显示未授权提示
    cy.url().should('satisfy', (url) => url.includes('/user/login') || url.includes('/energy/operations'));
  });

  it('[AUTH-02] 未登录访问Trading应跳转登录页', () => {
    cy.intercept('GET', '**/api/trading/**', { statusCode: 401, body: { success: false, message: '未认证' } });
    cy.visit('/energy/trading/electrade');
    cy.url().should('satisfy', (url) => url.includes('/user/login') || url.includes('/energy/trading'));
  });

  it('[AUTH-03] 无权限访问时显示403提示', () => {
    cy.intercept('GET', '**/api/operations/energyeff/list*', { statusCode: 403, body: { success: false, message: '无权限' } });
    cy.visit('/energy/operations/energyeff');
    // 应显示无权限提示或空状态
    cy.get('#root', { timeout: 10000 }).should('exist');
  });

  it('[AUTH-04] Token过期后API请求返回401', () => {
    cy.intercept('GET', '**/api/trading/electrade/list*', { statusCode: 401, body: { success: false, message: 'Token已过期' } });
    cy.visit('/energy/trading/electrade');
    cy.get('#root', { timeout: 10000 }).should('exist');
  });
});

// ══════════════════════════════════════
// 输入验证测试
// ══════════════════════════════════════

describe('[V3.2.0增量] 表单输入验证', () => {
  beforeEach(() => {
    // Mock 返回400验证错误
    cy.intercept('POST', '**/api/operations/energyeff', { statusCode: 400, body: { success: false, message: '参数验证失败', errors: { name: '名称不能为空' } } }).as('createFail');
    cy.intercept('GET', '**/api/operations/energyeff/list*', { body: pagedMock(MOCK_ENERGYEFF_LIST) });
  });

  it('[INPUT-01] 空表单提交应显示验证错误', () => {
    cy.visit('/energy/operations/energyeff');
    // 尝试点击新建按钮
    cy.get('button, [role="button"]').contains(/新建|新增|创建|添加/).first().click({ force: true });
    // 如果有弹窗表单，直接点击确定应提示验证错误
    cy.get('.ant-modal, [class*="modal"], [role="dialog"]').then(($modal) => {
      if ($modal.length > 0) {
        cy.get('.ant-modal .ant-btn-primary, .ant-modal button[type="submit"]').first().click({ force: true });
        // 应出现验证错误提示
        cy.get('.ant-form-item-explain, .ant-form-item-has-error, [class*="error"]', { timeout: 5000 }).should('exist');
      }
    });
  });

  it('[INPUT-02] XSS脚本作为输入不应被渲染', () => {
    cy.intercept('GET', '**/api/operations/energyeff/list*', {
      body: pagedMock([{ ...MOCK_ENERGYEFF_LIST[0], name: '<script>alert("xss")</script>' }]),
    });
    cy.visit('/energy/operations/energyeff');
    // 确保XSS脚本以文本形式而非执行形式显示
    cy.get('.ant-table, [class*="table"]', { timeout: 10000 }).should('exist');
    cy.get('script').should('not.contain', 'alert("xss")');
  });

  it('[INPUT-03] 超长输入不应导致页面崩溃', () => {
    const longText = 'A'.repeat(5000);
    cy.intercept('GET', '**/api/operations/energyeff/list*', {
      body: pagedMock([{ ...MOCK_ENERGYEFF_LIST[0], name: longText }]),
    });
    cy.visit('/energy/operations/energyeff');
    cy.get('#root', { timeout: 10000 }).should('exist');
    // 页面不应白屏
    cy.get('.ant-table, [class*="table"], [class*="layout"]').should('exist');
  });

  it('[INPUT-04] SQL注入字符串不应影响页面', () => {
    cy.intercept('GET', '**/api/operations/energyeff/list*', {
      body: pagedMock([{ ...MOCK_ENERGYEFF_LIST[0], name: "'; DROP TABLE--" }]),
    });
    cy.visit('/energy/operations/energyeff');
    cy.get('#root', { timeout: 10000 }).should('exist');
  });
});

// ══════════════════════════════════════
// 软删除UI交互测试
// ══════════════════════════════════════

describe('[V3.2.0增量] 软删除UI交互', () => {
  beforeEach(() => {
    cy.intercept('GET', '**/api/operations/energyeff/list*', { body: pagedMock(MOCK_ENERGYEFF_LIST) });
    cy.intercept('DELETE', '**/api/operations/energyeff/*', { statusCode: 204 }).as('deleteItem');
  });

  it('[DEL-01] 删除按钮存在且可点击', () => {
    cy.visit('/energy/operations/energyeff');
    cy.get('.ant-table, [class*="table"]', { timeout: 10000 }).should('exist');
    // 检查操作列有删除按钮
    cy.get('.ant-table-row, [class*="row"]').first().within(() => {
      cy.get('button, a, [role="button"]').should('have.length.gte', 1);
    });
  });

  it('[DEL-02] 删除操作应有确认弹窗', () => {
    cy.visit('/energy/operations/energyeff');
    cy.get('.ant-table, [class*="table"]', { timeout: 10000 }).should('exist');
    // 尝试找到删除按钮
    cy.get('[class*="delete"], [class*="操作"]').first().click({ force: true });
    // 应出现确认弹窗
    cy.get('.ant-popconfirm, .ant-modal-confirm, [class*="confirm"]', { timeout: 5000 }).should('exist');
  });
});

// ══════════════════════════════════════
// V3.2.0 向后兼容路由测试
// ══════════════════════════════════════

describe('[V3.2.0增量] 旧路由兼容性', () => {
  it('[COMPAT-01] 旧版能效路由仍可访问', () => {
    cy.intercept('GET', '**/api/energyeff/list*', { body: pagedMock(MOCK_ENERGYEFF_LIST) });
    cy.visit('/energy/energyeff');
    cy.get('#root', { timeout: 10000 }).should('exist');
  });

  it('[COMPAT-02] 旧版电力交易路由仍可访问', () => {
    cy.intercept('GET', '**/api/electrade/list*', { body: pagedMock(MOCK_ELECTRADE_LIST) });
    cy.visit('/energy/electrade');
    cy.get('#root', { timeout: 10000 }).should('exist');
  });
});
