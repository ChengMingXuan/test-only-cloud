/**
 * Cypress 本地 Dev Server 配置
 * 连接到 http://localhost:8000（UmiJS 开发服务器）
 * 使用真实前端应用 + 后端接口可真实联调或使用 cy.intercept() Mock
 * 运行时间：10-15 分钟（取决于网络）
 */
const { defineConfig } = require('cypress');

module.exports = defineConfig({
  e2e: {
    // 本地 UmiJS 开发服务器
    // 前提：cd JGSY.AGI.Frontend && npm run dev
    // 访问地址：http://localhost:8000
    baseUrl: 'http://localhost:8000',
    supportFile: 'support/e2e.js',
    specPattern: 'e2e/**/*.cy.js',
    video: false,
    screenshotOnRunFailure: true,
    // 超时：与 Mock 相同（本地网络快速）
    defaultCommandTimeout: 8000,
    pageLoadTimeout: 15000,
    requestTimeout: 8000,
    responseTimeout: 8000,
    viewportWidth: 1440,
    viewportHeight: 900,
    retries: {
      runMode: 1,  // 恢复 1 次重试（本地稳定性好）
      openMode: 0,
    },
    setupNodeEvents(on, config) {
      on('before:run', () => {
        const fs = require('fs');
        if (!fs.existsSync('reports')) fs.mkdirSync('reports', { recursive: true });
      });
    },
  },
});
