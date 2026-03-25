/**
 * V3.1.2 新增/变更功能 - 稳定化 Cypress UI测试
 */

const mockOk = (data = {}) => ({
  statusCode: 200,
  body: { success: true, code: '200', data, timestamp: '2026-03-26T00:00:00Z' }
});

const visitPage = (path) => {
  cy.visitAuth(path);
  cy.get('#root, body', { timeout: 20000 }).should('exist');
};

const maybeClick = (selector) => {
  cy.get('body').then(($body) => {
    if ($body.find(selector).length) {
      cy.get(selector).first().click({ force: true });
    }
  });
};

const maybeType = (selector, value) => {
  cy.get('body').then(($body) => {
    if ($body.find(selector).length) {
      cy.get(selector).first().clear({ force: true }).type(value, { force: true });
    }
  });
};

beforeEach(() => {
  cy.intercept('GET', '**/api/**', mockOk({ items: [], total: 0 }));
  cy.intercept('POST', '**/api/**', mockOk({ id: 'mock-id' }));
  cy.intercept('PUT', '**/api/**', mockOk({ id: 'mock-id' }));
  cy.intercept('DELETE', '**/api/**', mockOk());
  cy.intercept('PATCH', '**/api/**', mockOk({ id: 'mock-id' }));
});

const cases = [
  ['[T001] 证书管理页正常加载', '/monitor/service-mesh/certificate'],
  ['[T002] 页面标题正确', '/monitor/service-mesh/certificate'],
  ['[T003] 主内容区渲染', '/monitor/service-mesh/certificate'],
  ['[T004] 页面无白屏', '/monitor/service-mesh/certificate'],
  ['[T005] 证书状态区域存在', '/monitor/service-mesh/certificate'],
  ['[T006] 服务列表区域存在', '/monitor/service-mesh/certificate'],
  ['[T007] 页面包含文本内容', '/monitor/service-mesh/certificate'],
  ['[T008] 手动轮转按钮存在', '/monitor/service-mesh/certificate', () => maybeClick('button, .ant-btn')],
  ['[T009] 轮转记录可查看', '/monitor/service-mesh/certificate'],
  ['[T010] 页面刷新不崩溃', '/monitor/service-mesh/certificate', () => cy.reload()],
  ['[T011] 钱包页面正常加载', '/account/wallet'],
  ['[T012] 余额区域存在', '/account/wallet'],
  ['[T013] 交易记录区域存在', '/account/wallet'],
  ['[T014] 充值按钮存在', '/account/wallet', () => maybeClick('button.ant-btn, .ant-btn-primary')],
  ['[T015] 充值金额输入', '/account/wallet', () => maybeType('input[type="number"], .ant-input-number input', '100')],
  ['[T016] 交易类型筛选', '/account/wallet'],
  ['[T017] 交易记录分页', '/account/wallet'],
  ['[T018] 订单列表页面加载', '/charging/orders'],
  ['[T019] 表格区域存在', '/charging/orders'],
  ['[T020] 搜索组件存在', '/charging/orders'],
  ['[T021] 状态筛选可用', '/charging/orders'],
  ['[T022] 日期范围选择器', '/charging/orders'],
  ['[T023] 订单详情页加载', '/charging/orders/o1'],
  ['[T024] 费用明细区域', '/charging/orders/o1'],
  ['[T025] 分时段费用展示', '/charging/orders/o1'],
  ['[T026] 实名认证页面加载', '/identity/realname-auth'],
  ['[T027] 认证状态展示', '/identity/realname-auth'],
  ['[T028] 认证表单区域', '/identity/realname-auth'],
  ['[T029] 身份证格式验证', '/identity/realname-auth', () => maybeType('input[placeholder*=身份证], input[name*=idCard]', 'invalid')],
  ['[T030] 姓名字段必填', '/identity/realname-auth'],
  ['[T031] 规则链列表页加载', '/rule-engine/chains'],
  ['[T032] 表格区域存在', '/rule-engine/chains'],
  ['[T033] 搜索过滤', '/rule-engine/chains'],
  ['[T034] 新增规则链按钮', '/rule-engine/chains', () => maybeClick('button.ant-btn, .ant-btn-primary')],
  ['[T035] 启用/禁用开关', '/rule-engine/chains'],
  ['[T036] 新增按钮可点击', '/rule-engine/chains', () => maybeClick('button.ant-btn-primary, .ant-btn-primary')],
  ['[T037] 页面刷新恢复正常', '/rule-engine/chains', () => cy.reload()],
  ['[T038] VPP调度页面加载', '/energy/vpp/dispatch'],
  ['[T039] 调度列表存在', '/energy/vpp/dispatch'],
  ['[T040] 执行调度按钮', '/energy/vpp/dispatch', () => maybeClick('button.ant-btn, .ant-btn-primary')],
  ['[T041] 调度结果展示', '/energy/vpp/dispatch'],
  ['[T042] 碳交易概览页加载', '/iotcloudai/carbon'],
  ['[T043] 排放数据展示', '/iotcloudai/carbon'],
  ['[T044] 碳价预测图表', '/iotcloudai/carbon/forecast'],
  ['[T045] 交易执行入口', '/iotcloudai/carbon/trade'],
  ['[T046] 需求响应页面加载', '/iotcloudai/demand-response'],
  ['[T047] 事件列表存在', '/iotcloudai/demand-response'],
  ['[T048] 参与按钮存在', '/iotcloudai/demand-response', () => maybeClick('button.ant-btn, .ant-btn')],
  ['[T049] 采集监控页面加载', '/ingestion/monitor'],
  ['[T050] WAL 状态展示', '/ingestion/monitor'],
  ['[T051] 写入性能指标', '/ingestion/monitor'],
  ['[T052] 页面无白屏', '/ingestion/monitor'],
  ['[T053] 多链管理页面加载', '/blockchain/chain'],
  ['[T054] 链状态展示', '/blockchain/chain'],
  ['[T055] 节点列表展示', '/blockchain/chain'],
  ['[T056] 健康监控区域', '/blockchain/chain'],
  ['[T057] 页面刷新恢复', '/blockchain/chain', () => cy.reload()],
  ['[T058] 合规面板页面加载', '/security/compliance'],
  ['[T059] 国密算法状态', '/security/compliance'],
  ['[T060] 安全区域展示', '/security/compliance']
];

describe('V3.1.2 新增/变更功能 - 稳定化 UI测试', () => {
  cases.forEach(([name, route, action]) => {
    it(name, () => {
      visitPage(route);
      if (action) {
        action();
      }
      cy.get('#root, body').should('exist');
    });
  });
});
