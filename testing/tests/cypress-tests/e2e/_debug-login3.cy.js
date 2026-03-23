/**
 * 调试登录页面 DOM - 加长等待
 */
describe('debug', () => {
  it('v3', () => {
    cy.visit('/user/login', { failOnStatusCode: false, timeout: 30000 });
    cy.wait(8000); // 等待 React hydration 完成
    
    cy.get('body').then(($body) => {
      const info = [];
      const html = $body.html();
      info.push('BODY length: ' + html.length);
      info.push('Has ant-pro: ' + html.includes('ant-pro'));
      info.push('Has ant-form: ' + html.includes('ant-form'));
      info.push('Has LoginForm: ' + html.includes('LoginForm'));
      info.push('Has ant-tabs: ' + html.includes('ant-tabs'));
      info.push('Has ProForm: ' + html.includes('ProForm'));
      info.push('Has ant-btn: ' + html.includes('ant-btn'));
      
      const inputs = $body.find('input');
      info.push('\n=== INPUTS (' + inputs.length + ') ===');
      inputs.each((i, el) => {
        info.push(`  [${i}] type=${el.type} name=${el.name} id=${el.id} ph="${el.placeholder}" val="${el.value}" cls="${el.className}"`);
      });
      
      const buttons = $body.find('button');
      info.push('\n=== BUTTONS (' + buttons.length + ') ===');
      buttons.each((i, el) => {
        info.push(`  [${i}] type=${el.type} cls="${el.className}" text="${el.textContent.trim().substring(0,50)}"`);
      });
      
      // 显示 #root 直接子元素
      const root = $body.find('#root');
      info.push('\n#root children: ' + root.children().length);
      root.children().each((i, el) => {
        info.push(`  [${i}] tag=${el.tagName} cls="${el.className.substring(0,150)}"`);
      });
      
      // 写出前 5000 字符的 HTML 用于分析
      info.push('\n=== HTML (first 5000) ===');
      info.push(html.substring(0, 5000));
      
      cy.writeFile('debug-dom-v3.txt', info.join('\n'));
    });
  });
});
