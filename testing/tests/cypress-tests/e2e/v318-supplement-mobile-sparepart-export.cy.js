/**
 * v3.18 增量补充 - 移动端认证 / 备品备件 / 导出服务
 * ====================================================
 * 补充 v318-incremental-features.cy.js 未覆盖的 3 个模块
 */

const BASE_URL = Cypress.env('BASE_URL') || 'http://localhost:3000';
const mockApiSuccess = (data = {}) => ({
  statusCode: 200,
  body: { code: 200, data, message: 'OK' }
});

// ═══════════════════════════════════════════════════════════════════════════════
// 1. 移动端认证 & 小程序登录
// ═══════════════════════════════════════════════════════════════════════════════

describe('移动端认证', () => {
  describe('短信验证码登录', () => {
    it('应显示手机号输入框和获取验证码按钮', () => {
      cy.intercept('GET', '/api/auth/user/info', { statusCode: 401 });
      cy.visit(`${BASE_URL}/mobile/login`);
      cy.get('[data-testid="phone-input"]').should('be.visible');
      cy.get('[data-testid="send-code-btn"]').should('be.visible');
    });

    it('手机号格式校验', () => {
      cy.visit(`${BASE_URL}/mobile/login`);
      cy.get('[data-testid="phone-input"]').type('123');
      cy.get('[data-testid="send-code-btn"]').click();
      cy.get('.ant-form-item-explain-error').should('be.visible');
    });

    it('验证码发送成功后显示倒计时', () => {
      cy.intercept('POST', '/api/auth/mobile/send-code', mockApiSuccess());
      cy.visit(`${BASE_URL}/mobile/login`);
      cy.get('[data-testid="phone-input"]').type('13812345678');
      cy.get('[data-testid="send-code-btn"]').click();
      cy.get('[data-testid="send-code-btn"]').should('be.disabled');
    });

    it('登录成功后跳转首页', () => {
      cy.intercept('POST', '/api/auth/mobile/sms-login', mockApiSuccess({
        accessToken: 'mock-token',
        refreshToken: 'mock-refresh',
      }));
      cy.visit(`${BASE_URL}/mobile/login`);
      cy.get('[data-testid="phone-input"]').type('13812345678');
      cy.get('[data-testid="code-input"]').type('123456');
      cy.get('[data-testid="login-btn"]').click();
    });
  });

  describe('密码登录', () => {
    it('应能切换到密码登录模式', () => {
      cy.visit(`${BASE_URL}/mobile/login`);
      cy.get('[data-testid="switch-password-login"]').click();
      cy.get('[data-testid="password-input"]').should('be.visible');
    });
  });

  describe('小程序登录', () => {
    it('应显示微信登录按钮', () => {
      cy.visit(`${BASE_URL}/mobile/login`);
      cy.get('[data-testid="wechat-login-btn"]').should('be.visible');
    });
  });

  describe('个人信息', () => {
    beforeEach(() => {
      cy.intercept('GET', '/api/auth/mobile/profile', mockApiSuccess({
        id: 'user-001',
        realName: '张三',
        phone: '138****5678',
        avatar: null,
      }));
    });

    it('应显示个人信息页', () => {
      cy.visit(`${BASE_URL}/mobile/profile`);
      cy.get('[data-testid="user-name"]').should('contain', '张三');
    });

    it('应能编辑个人信息', () => {
      cy.intercept('PUT', '/api/auth/mobile/profile', mockApiSuccess());
      cy.visit(`${BASE_URL}/mobile/profile/edit`);
      cy.get('[data-testid="name-input"]').clear().type('李四');
      cy.get('[data-testid="save-btn"]').click();
      cy.get('.ant-message-success').should('be.visible');
    });
  });
});

// ═══════════════════════════════════════════════════════════════════════════════
// 2. 备品备件管理
// ═══════════════════════════════════════════════════════════════════════════════

describe('备品备件管理', () => {
  beforeEach(() => {
    cy.intercept('GET', '/api/auth/user/info', mockApiSuccess({
      id: 'user-001',
      username: 'admin',
      permissions: ['workorder:sparepart:view', 'workorder:sparepart:create', 'workorder:sparepart:manage']
    }));
  });

  describe('备件列表', () => {
    it('应显示备件列表表格', () => {
      cy.intercept('GET', '/api/spare-part*', mockApiSuccess({
        items: [
          { id: '1', partCode: 'SP-001', partName: '逆变器模块', category: 'inverter', stock: 15 },
          { id: '2', partCode: 'SP-002', partName: '光伏面板', category: 'panel', stock: 50 },
        ],
        total: 2,
      }));
      cy.visit(`${BASE_URL}/workorder/spare-part`);
      cy.get('[data-testid="spare-part-table"]').should('be.visible');
    });

    it('应支持按分类筛选', () => {
      cy.intercept('GET', '/api/spare-part*', mockApiSuccess({ items: [], total: 0 }));
      cy.visit(`${BASE_URL}/workorder/spare-part`);
      cy.get('[data-testid="category-filter"]').click();
      cy.get('.ant-select-item').first().click();
    });
  });

  describe('新增备件', () => {
    it('应能打开新增表单', () => {
      cy.intercept('GET', '/api/spare-part*', mockApiSuccess({ items: [], total: 0 }));
      cy.visit(`${BASE_URL}/workorder/spare-part`);
      cy.get('[data-testid="add-btn"]').click();
      cy.get('[data-testid="spare-part-form"]').should('be.visible');
    });

    it('必填字段校验', () => {
      cy.visit(`${BASE_URL}/workorder/spare-part/create`);
      cy.get('[data-testid="submit-btn"]').click();
      cy.get('.ant-form-item-explain-error').should('have.length.at.least', 1);
    });

    it('创建成功跳转列表', () => {
      cy.intercept('POST', '/api/spare-part', mockApiSuccess({ id: 'new-1' }));
      cy.visit(`${BASE_URL}/workorder/spare-part/create`);
      cy.get('[data-testid="part-code-input"]').type('SP-003');
      cy.get('[data-testid="part-name-input"]').type('控制器');
      cy.get('[data-testid="submit-btn"]').click();
      cy.get('.ant-message-success').should('be.visible');
    });
  });

  describe('入库操作', () => {
    it('应能进行入库操作', () => {
      cy.intercept('POST', '/api/spare-part/stock-in', mockApiSuccess());
      cy.visit(`${BASE_URL}/workorder/spare-part/stock-in`);
      cy.get('[data-testid="part-select"]').click();
      cy.get('.ant-select-item').first().click();
      cy.get('[data-testid="quantity-input"]').type('10');
      cy.get('[data-testid="submit-btn"]').click();
      cy.get('.ant-message-success').should('be.visible');
    });
  });

  describe('出库操作', () => {
    it('应能进行出库操作', () => {
      cy.intercept('POST', '/api/spare-part/stock-out', mockApiSuccess());
      cy.visit(`${BASE_URL}/workorder/spare-part/stock-out`);
      cy.get('[data-testid="part-select"]').click();
      cy.get('.ant-select-item').first().click();
      cy.get('[data-testid="quantity-input"]').type('3');
      cy.get('[data-testid="submit-btn"]').click();
    });
  });

  describe('库存告警', () => {
    it('应显示低库存告警列表', () => {
      cy.intercept('GET', '/api/spare-part/inventory/low-stock', mockApiSuccess([
        { partCode: 'SP-001', partName: '逆变器模块', currentStock: 2, safetyStock: 10 },
      ]));
      cy.visit(`${BASE_URL}/workorder/spare-part/alerts`);
      cy.get('[data-testid="low-stock-table"]').should('be.visible');
    });
  });
});

// ═══════════════════════════════════════════════════════════════════════════════
// 3. 导出服务
// ═══════════════════════════════════════════════════════════════════════════════

describe('导出服务', () => {
  beforeEach(() => {
    cy.intercept('GET', '/api/auth/user/info', mockApiSuccess({
      id: 'user-001',
      username: 'admin',
      permissions: ['export:excel:create', 'export:pdf:create']
    }));
  });

  describe('Excel 导出', () => {
    it('充电订单列表页应有导出按钮', () => {
      cy.intercept('GET', '/api/charging/orders*', mockApiSuccess({ items: [], total: 0 }));
      cy.visit(`${BASE_URL}/charging/orders`);
      cy.get('[data-testid="export-excel-btn"]').should('be.visible');
    });

    it('点击导出应触发下载', () => {
      cy.intercept('POST', '/api/export/excel/generate', {
        statusCode: 200,
        headers: { 'content-type': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' },
        body: new Blob(),
      });
      cy.visit(`${BASE_URL}/charging/orders`);
      cy.get('[data-testid="export-excel-btn"]').click();
    });
  });

  describe('PDF 导出', () => {
    it('报表页应有PDF导出按钮', () => {
      cy.intercept('GET', '/api/microgrid/energy/reports*', mockApiSuccess({ items: [], total: 0 }));
      cy.visit(`${BASE_URL}/energy/reports`);
      cy.get('[data-testid="export-pdf-btn"]').should('be.visible');
    });

    it('点击PDF导出应弹出配置对话框', () => {
      cy.visit(`${BASE_URL}/energy/reports`);
      cy.get('[data-testid="export-pdf-btn"]').click();
      cy.get('[data-testid="pdf-config-modal"]').should('be.visible');
    });
  });
});
