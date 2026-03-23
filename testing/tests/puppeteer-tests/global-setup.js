/**
 * Jest 全局设置 — 双模兼容
 * 
 * 真实模式：前端可达时直连真实 Frontend
 * Mock 模式：前端不可达 / CI / MOCK_MODE=1 时自动启动 mock-server
 */
const http = require('http');

async function checkServiceAvailable(url, timeoutMs = 3000) {
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
  const forceMock = process.env.CI || process.env.MOCK_MODE;
  const available = forceMock ? false : await checkServiceAvailable(baseUrl);

  if (!available) {
    // Mock 模式：自动启动 mock-server
    console.log(`\n⚡ [Puppeteer] 前端不可达或 Mock 模式，自动启动 mock-server...`);
    try {
      const mockServer = require('./mock-server');
      // mock-server 默认监听 8000，如果占用会尝试其他端口
      const server = await mockServer.start();
      // 保存引用供 global-teardown 停止
      globalThis.__PUPPETEER_MOCK_SERVER__ = mockServer;
      console.log(`✅ [Puppeteer] Mock 模式 → mock-server 已启动\n`);
    } catch (err) {
      console.warn(`⚠️  [Puppeteer] mock-server 启动失败: ${err.message}，测试将以降级 Mock 模式运行\n`);
    }
    process.env.PUPPETEER_SERVICE_AVAILABLE = 'mock';
  } else {
    console.log(`\n✅ [Puppeteer] 真实模式 → 前端 ${baseUrl} 可达，直连真实服务\n`);
    process.env.PUPPETEER_SERVICE_AVAILABLE = 'true';
  }
};
