/**
 * Puppeteer 性能测试 - charging (tti)
 */

const puppeteer = require('puppeteer');
const assert = require('assert');

(async () => {
  const browser = await puppeteer.launch();
  const page = await browser.newPage();
  
  try {
    await page.goto('http://localhost:3100/charging', { waitUntil: 'networkidle2' });
    
    // 获取性能指标
    const metrics = await page.metrics();
    const perf = JSON.stringify(metrics, null, 2);
    
    console.log('Metrics for charging (tti):');
    console.log(perf);
    
    // 基本验证
    assert(metrics.JSHeapUsedSize < 100000000, 'Memory usage should be < 100MB');
    
  } finally {
    await browser.close();
  }
})().catch(err => {
  console.error(err);
  process.exit(1);
});
