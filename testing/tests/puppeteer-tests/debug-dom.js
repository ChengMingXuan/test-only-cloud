const puppeteer = require('puppeteer');
(async () => {
  const browser = await puppeteer.launch({headless:'new', args:['--no-sandbox','--disable-setuid-sandbox','--disable-dev-shm-usage']});
  const page = await browser.newPage();
  
  // 模仿测试的 beforeEach 设置
  await page.evaluateOnNewDocument((token) => {
    localStorage.setItem('jgsy_access_token', token);
    localStorage.setItem('jgsy_tenant_code', 'TEST_TENANT');
  }, 'mocktoken');
  
  await page.setRequestInterception(true);
  page.on('request', request => {
    if (request.url().includes('/api/')) {
      request.respond({status:200,contentType:'application/json',body:JSON.stringify({success:true,data:{items:[],total:0}})});
    } else {
      request.continue();
    }
  });
  
  await page.goto('http://localhost:8000/login', {waitUntil:'networkidle2',timeout:15000});
  
  // 检查 script[src]
  const scriptSrcCount = await page.evaluate(() => document.querySelectorAll('script[src]').length);
  console.log('script[src] count:', scriptSrcCount);
  
  const allScriptCount = await page.evaluate(() => document.querySelectorAll('script').length);
  console.log('all script count:', allScriptCount);
  
  // 检查 link[rel*="icon"]
  const faviconCount = await page.evaluate(() => document.querySelectorAll('link[rel*="icon"]').length);
  console.log('favicon count:', faviconCount);
  
  const allLinkCount = await page.evaluate(() => document.querySelectorAll('link').length);
  console.log('all link count:', allLinkCount);
  
  // 输出 head 内容
  const headHTML = await page.evaluate(() => document.head.innerHTML);
  console.log('=== HEAD HTML ===');
  console.log(headHTML);
  console.log('=================');
  
  await browser.close();
})();
