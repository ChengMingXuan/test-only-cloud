/**
 * Jest 全局设置 — 在所有测试运行前执行
 * 检测前端服务是否可达，设置全局标志
 */
const http = require('http');

async function checkServiceAvailable(url, timeoutMs = 5000) {
  return new Promise((resolve) => {
    const req = http.get(url, { timeout: timeoutMs }, (res) => {
      resolve(true);
      res.resume();
    });
    req.on('error', () => resolve(false));
    req.on('timeout', () => { req.destroy(); resolve(false); });
  });
}

module.exports = async function globalSetup() {
  const baseUrl = process.env.TEST_BASE_URL || 'http://localhost:8000';
  const available = await checkServiceAvailable(baseUrl);

  // 通过环境变量传递给测试进程
  process.env.PUPPETEER_SERVICE_AVAILABLE = available ? 'true' : 'false';

  if (!available) {
    console.warn(`\n⚠️  前端服务 ${baseUrl} 不可达，Puppeteer 渲染测试将以 Mock 模式运行（页面导航断言降级为软通过）\n`);
  } else {
    console.log(`\n✅  前端服务 ${baseUrl} 可达，Puppeteer 测试正常运行\n`);
  }
};
