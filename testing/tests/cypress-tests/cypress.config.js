/**
 * Cypress 配置 - UmiJS 管理后台组件交互测试
 * 
 * 双模兼容：
 *   真实模式 — 前端可达时直连真实 Frontend，后端接口按需 Mock
 *   Mock 模式 — 前端不可达 / CI / CYPRESS_MOCK_MODE=1 时自动启动 mock-server
 * 
 * 规则：同一套测试代码两种模式均可通过
 * 详见：docs/04-开发规范/Cypress 前端自动化测试规范 v1.0.md
 */
const { defineConfig } = require('cypress');
const http = require('http');

/**
 * 检测前端服务是否可达（3s 超时）
 */
function checkFrontendAvailable(url) {
  return new Promise((resolve) => {
    const req = http.get(url, { timeout: 3000 }, (res) => {
      resolve(true);
      res.resume();
    });
    req.on('error', () => resolve(false));
    req.on('timeout', () => { req.destroy(); resolve(false); });
  });
}

module.exports = defineConfig({
  e2e: {
    // 本地优先用真实前端，CI/Mock 自动降级
    baseUrl: process.env.CYPRESS_BASE_URL || 'http://localhost:8000',
    supportFile: 'support/e2e.js',
    specPattern: 'e2e/**/*.cy.js',
    
    // 仅失败时截图（全部输出到项目 D 盘目录，避免 C 盘空间不足）
    video: false,
    screenshotOnRunFailure: true,
    screenshotsFolder: 'cypress/screenshots',
    videosFolder: 'cypress/videos',
    downloadsFolder: 'cypress/downloads',
    
    // 超时（本地网络）
    defaultCommandTimeout: 10000,
    pageLoadTimeout: 20000,
    requestTimeout: 10000,
    responseTimeout: 10000,
    
    // 视口
    viewportWidth: 1440,
    viewportHeight: 900,
    
    // 失败重试 1 次
    retries: {
      runMode: 1,
      openMode: 0,
    },
    
    async setupNodeEvents(on, config) {
      const fs = require('fs');
      const mockServer = require('./mock-server');
      let mockStarted = false;

      on('before:run', async () => {
        // 创建报告目录
        if (!fs.existsSync('reports')) fs.mkdirSync('reports', { recursive: true });

        // 双模判断：CI / 显式 Mock / 前端不可达 → 自动启动 mock-server
        const forceMock = process.env.CI || process.env.CYPRESS_MOCK_MODE;
        const baseUrl = config.baseUrl || 'http://localhost:8000';
        const available = forceMock ? false : await checkFrontendAvailable(baseUrl);

        if (!available) {
          console.log('\n⚡ [Cypress] 前端不可达或 Mock 模式，自动启动 mock-server...');
          await mockServer.start();
          mockStarted = true;
          // 确保 baseUrl 指向 mock-server
          config.baseUrl = `http://127.0.0.1:${mockServer.PORT}`;
          console.log(`✅ [Cypress] Mock 模式 → baseUrl = ${config.baseUrl}\n`);
        } else {
          console.log(`\n✅ [Cypress] 真实模式 → 前端 ${baseUrl} 可达，直连真实服务\n`);
        }
      });

      on('after:run', () => {
        if (mockStarted) {
          mockServer.stop();
          console.log('🛑 [Cypress] mock-server 已停止');
        }
      });

      return config;
    },
  },
});
