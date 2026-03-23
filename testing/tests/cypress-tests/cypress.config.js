/**
 * Cypress 配置 - UmiJS 管理后台组件交互测试
 * 
 * 仅测试：JGSY.AGI.Frontend（UmiJS React 管理后台）
 * 规则：页面必须是真实前端服务；后端接口可真实联调，也可使用 cy.intercept() Mock
 * 禁止：Mock 页面、公网域名
 * 详见：docs/04-开发规范/Cypress 前端自动化测试规范 v1.0.md
 */
const { defineConfig } = require('cypress');

module.exports = defineConfig({
  e2e: {
    // 本地 UmiJS 开发服务器（必须←必须）
    // 前提：cd JGSY.AGI.Frontend && npm run dev
    // 不支持：公网域名、Mock 页面
    baseUrl: 'http://localhost:8000',
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
    
    setupNodeEvents(on, config) {
      on('before:run', () => {
        const fs = require('fs');
        if (!fs.existsSync('reports')) fs.mkdirSync('reports', { recursive: true });
      });
    },
  },
});
