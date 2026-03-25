/**
 * 调试登录页面 DOM 结构
 */
describe('调试登录页面', () => {
  it('截图并输出 DOM 结构', () => {
    cy.visit('/user/login', { failOnStatusCode: false });
    cy.wait(3000);
    cy.screenshot('login-page-full');
    
    // 输出表单结构
    cy.get('body').then(($body) => {
      // 查找所有 input
      const inputs = $body.find('input');
      cy.log('Input count: ' + inputs.length);
      inputs.each((i, el) => {
        cy.log(`Input[${i}]: type=${el.type}, name=${el.name}, id=${el.id}, placeholder=${el.placeholder}, value=${el.value}`);
      });
      
      // 查找所有 button
      const buttons = $body.find('button');
      cy.log('Button count: ' + buttons.length);
      buttons.each((i, el) => {
        cy.log(`Button[${i}]: type=${el.type}, class=${el.className}, text=${el.textContent.trim()}`);
      });
      
      // 查找 ant-form-item
      const formItems = $body.find('.ant-form-item');
      cy.log('FormItem count: ' + formItems.length);
      
      // 查找 ant-btn
      const antBtns = $body.find('.ant-btn');
      cy.log('AntBtn count: ' + antBtns.length);
      antBtns.each((i, el) => {
        cy.log(`AntBtn[${i}]: class=${el.className}, text=${el.textContent.trim()}`);
      });
      
      // 查找 LoginForm 特征
      const loginForm = $body.find('.ant-pro-form-login, .ant-pro-form-login-main');
      cy.log('LoginForm found: ' + loginForm.length);
    });
    
    // 尝试清空并提交，看验证消息
    cy.get('input').first().then(($el) => {
      if ($el.length > 0) {
        cy.wrap($el).focus().clear({ force: true });
      }
    });
    cy.wait(500);
    cy.screenshot('login-after-clear');
    
    // 点击提交看验证消息
    cy.get('button').then(($buttons) => {
      // 找登录按钮
      $buttons.each((i, el) => {
        if (el.textContent.includes('登录') || el.className.includes('ant-btn-primary')) {
          cy.wrap(el).click({ force: true });
          return false;
        }
      });
    });
    cy.wait(1000);
    cy.screenshot('login-after-submit');
    
    // 输出 body innerHTML 的前2000字符到日志
    cy.get('#root').then(($root) => {
      const html = $root.html().substring(0, 3000);
      cy.log('ROOT HTML (first 3000 chars): ' + html);
    });
  });
});
