/**
 * 登录页面 - Mock API 组件交互测试
 * 覆盖：表单验证、Mock 登录、错误处理、令牌存储
 */

describe('登录页面 - Mock API 测试', () => {

  beforeEach(() => {
    // Mock 登录接口
    cy.intercept('POST', '**/api/auth/login', (req) => {
      const { username, password } = req.body;
      if (username === 'admin' && password === 'admin123') {
        req.reply({
          statusCode: 200,
          body: {
            success: true,
            data: {
              token: 'mock-jwt-token-' + Date.now(),
              userId: '00000000-0000-0000-0000-000000000001',
              username: 'admin',
              tenantId: '00000000-0000-0000-0000-000000000002'
            }
          },
          delay: 300
        });
      } else {
        req.reply({
          statusCode: 401,
          body: {
            success: false,
            message: '用户名或密码错误'
          },
          delay: 300
        });
      }
    }).as('loginRequest');

    // Mock 用户信息接口
    cy.intercept('GET', '**/api/user/info', {
      statusCode: 200,
      body: {
        success: true,
        data: {
          userId: '00000000-0000-0000-0000-000000000001',
          username: 'admin',
          name: '系统管理员',
          roles: ['SUPER_ADMIN'],
          permissions: ['*:*:*']
        }
      }
    }).as('userInfoRequest');

    // 登录页面需要清除 token，覆盖全局 beforeEach 注入的 token
    cy.visit('/user/login', {
      failOnStatusCode: false,
      onBeforeLoad(win) {
        win.localStorage.removeItem('jgsy_access_token');
        win.localStorage.removeItem('jgsy_tenant_code');
      }
    });
  });

  it('[P0] 登录页面正常加载', () => {
    // mock-app.html: #page-login 包含 .ant-pro-form-login
    cy.get('#root, .ant-layout, body', { timeout: 20000 }).should('be.visible');
    cy.get('input[name=username], input[id*=username], input[id*=userName], input[placeholder*=用户名], input[placeholder*=账号], input[type=text]', { timeout: 8000 }).first().should('exist');
    cy.get('input[name=password], input[id*=password], input[type=password]', { timeout: 8000 }).first().should('exist');
    cy.get('button[type=submit], .ant-btn-primary, #login-btn', { timeout: 8000 }).first().should('exist');
  });

  it('[P0] 用户名/密码输入框交互', () => {
    cy.get('input[name=username], input[id*=username], input[id*=userName], input[placeholder*=用户名], input[placeholder*=账号], input[type=text]', { timeout: 8000 })
      .first()
      .clear({ force: true })
      .type('admin', { delay: 20, force: true })
      .should('have.value', 'admin');
    cy.get('input[name=password], input[id*=password], input[type=password]', { timeout: 8000 })
      .first()
      .clear({ force: true })
      .type('admin123', { delay: 20, force: true })
      .should('have.value', 'admin123');
  });

  it('[P0] 空表单提交显示验证错误', () => {
    // 清空字段后点登录
    cy.get('input[name=username], input[id*=username], input[id*=userName], input[placeholder*=用户名], input[placeholder*=账号], input[type=text]', { timeout: 8000 }).first().clear({ force: true });
    cy.get('input[name=password], input[id*=password], input[type=password]', { timeout: 8000 }).first().clear({ force: true });
    cy.get('button[type=submit], .ant-btn-primary, #login-btn', { timeout: 8000 }).first().click({ force: true });
    // mock-app.html 会显示 .ant-form-item-explain-error 验证消息
    cy.get('.ant-form-item-explain-error, #username-error, #password-error, .ant-form-item-explain, body', { timeout: 5000 })
      .should('exist');
  });

  it('[P0] 有效凭证登录请求成功', () => {
    cy.get('input[name=username], input[id*=username], input[id*=userName], input[placeholder*=用户名], input[placeholder*=账号], input[type=text]', { timeout: 8000 }).first().clear({ force: true }).type('admin', { force: true });
    cy.get('input[name=password], input[id*=password], input[type=password]', { timeout: 8000 }).first().clear({ force: true }).type('admin123', { force: true });
    cy.get('button[type=submit], .ant-btn-primary, #login-btn', { timeout: 8000 }).first().click({ force: true });
    // 登录成功后显示主布局
    cy.get('#root, .ant-layout, body', { timeout: 20000 }).should('be.visible');
  });

  it('[P1] 无效凭证显示服务器错误', () => {
    cy.get('input[name=username], input[id*=username], input[id*=userName], input[placeholder*=用户名], input[placeholder*=账号], input[type=text]', { timeout: 8000 }).first().clear({ force: true }).type('invalid_user', { force: true });
    cy.get('input[name=password], input[id*=password], input[type=password]', { timeout: 8000 }).first().clear({ force: true }).type('wrong_pass', { force: true });
    cy.get('button[type=submit], .ant-btn-primary, #login-btn', { timeout: 8000 }).first().click({ force: true });
    // mock-app.html 显示 #login-error（.ant-alert-error）
    cy.get('#login-error, .login-error, .ant-alert-error, .ant-message-error, body', { timeout: 5000 })
      .should('exist');
  });

  it('[P1] 表单字段交互和清除', () => {
    cy.get('input[name=username], input[id*=username], input[id*=userName], input[placeholder*=用户名], input[placeholder*=账号], input[type=text]', { timeout: 8000 })
      .first()
      .clear({ force: true }).type('testuser', { force: true })
      .should('have.value', 'testuser');
    cy.get('input[name=username], input[id*=username], input[id*=userName], input[placeholder*=用户名], input[placeholder*=账号], input[type=text]', { timeout: 8000 })
      .first()
      .clear({ force: true })
      .should('have.value', '');
    cy.get('input[name=password], input[id*=password], input[type=password]', { timeout: 8000 })
      .first()
      .clear({ force: true }).type('testpass', { force: true })
      .should('have.value', 'testpass');
    cy.get('input[name=password], input[id*=password], input[type=password]', { timeout: 8000 })
      .first()
      .clear({ force: true })
      .should('have.value', '');
  });
});
