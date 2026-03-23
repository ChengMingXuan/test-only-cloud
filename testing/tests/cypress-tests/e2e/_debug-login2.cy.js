/**
 * 调试登录页面 DOM 结构 - 输出到 task log
 */
describe('调试登录页面', () => {
  it('诊断 DOM 结构', () => {
    cy.visit('/user/login', { failOnStatusCode: false });
    cy.wait(3000);
    
    cy.get('body').then(($body) => {
      const inputs = $body.find('input');
      const info = [];
      info.push('=== INPUTS (' + inputs.length + ') ===');
      inputs.each((i, el) => {
        info.push(`  [${i}] type=${el.type} name=${el.name} id=${el.id} placeholder=${el.placeholder} value="${el.value}"`);
      });
      
      const buttons = $body.find('button');
      info.push('=== BUTTONS (' + buttons.length + ') ===');
      buttons.each((i, el) => {
        info.push(`  [${i}] type=${el.type} cls=${el.className.substring(0,100)} text="${el.textContent.trim().substring(0,50)}"`);
      });
      
      const formItems = $body.find('.ant-form-item');
      info.push('=== FORM ITEMS: ' + formItems.length + ' ===');
      
      const loginForm = $body.find('.ant-pro-form-login-main');
      info.push('=== LOGIN FORM: ' + loginForm.length + ' ===');
      
      const tabs = $body.find('.ant-tabs-tab');
      info.push('=== TABS (' + tabs.length + ') ===');
      tabs.each((i, el) => {
        info.push(`  [${i}] text="${el.textContent.trim()}"`);
      });
      
      // Write to file so we can read it
      cy.writeFile('debug-dom-output.txt', info.join('\n'));
    });
    
    // 尝试清空 username 然后点击登录，观察验证消息
    cy.get('input').first().then($el => {
      cy.wrap($el).clear({ force: true });
    });
    cy.wait(500);
    
    // 找登录按钮
    cy.get('button.ant-btn-primary, button.ant-btn-lg, button[type="submit"]').first().click({ force: true });
    cy.wait(1500);
    
    // 检查是否出现验证消息
    cy.get('body').then(($body) => {
      const explains = $body.find('.ant-form-item-explain, .ant-form-item-explain-error, [role="alert"]');
      const msgs = [];
      msgs.push('=== AFTER SUBMIT ===');
      msgs.push('Validation messages found: ' + explains.length);
      explains.each((i, el) => {
        msgs.push(`  [${i}] cls=${el.className} text="${el.textContent.trim()}"`);
      });
      
      // Check for alert messages  
      const alerts = $body.find('.ant-alert, .ant-message, .ant-notification');
      msgs.push('Alert elements: ' + alerts.length);
      
      // Check for error messages anywhere
      const errors = $body.find('[class*="error"], [class*="Error"]');
      msgs.push('Error-class elements: ' + errors.length);
      errors.each((i, el) => {
        msgs.push(`  [${i}] tag=${el.tagName} cls=${el.className.substring(0,100)} text="${el.textContent.trim().substring(0,80)}"`);
      });
      
      cy.writeFile('debug-dom-after-submit.txt', msgs.join('\n'));
    });
  });
});
