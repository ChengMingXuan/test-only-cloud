/**
 * Cypress 快速本地模式配置
 * - 访问真实 UmiJS 前端开发服务器（http://localhost:8000）
 * - 允许后端接口使用 Cypress API 拦截 Mock
 * - 禁止使用 Mock HTML / Mock 页面壳
 */
const { defineConfig } = require('cypress');
const fs = require('fs');
const http = require('http');
const FRONTEND_URL = 'http://127.0.0.1:4200';

function ensureFrontendAvailable() {
  return new Promise((resolve, reject) => {
    const req = http.get(FRONTEND_URL, (res) => {
      res.resume();
      if (res.statusCode && res.statusCode < 500) {
        resolve();
        return;
      }
      reject(new Error(`前端服务状态异常: ${FRONTEND_URL} -> HTTP ${res.statusCode}`));
    });
    req.on('error', () => {
      reject(new Error(`前端服务未启动，请先在 JGSY.AGI.Frontend 执行 npm run dev (${FRONTEND_URL})`));
    });
    req.setTimeout(3000, () => {
      req.destroy();
      reject(new Error(`连接前端服务超时，请确认已启动 ${FRONTEND_URL}`));
    });
  });
}

module.exports = defineConfig({
  e2e: {
    baseUrl: FRONTEND_URL,
    supportFile: 'support/e2e.js',
    specPattern: 'e2e/**/*.cy.js',
    video: false,
    screenshotOnRunFailure: true,
    screenshotsFolder: 'cypress/screenshots',
    videosFolder: 'cypress/videos',
    downloadsFolder: 'cypress/downloads',
    defaultCommandTimeout: 8000,
    pageLoadTimeout: 10000,
    requestTimeout: 5000,
    responseTimeout: 5000,
    viewportWidth: 1440,
    viewportHeight: 900,
    retries: {
      runMode: 1,
      openMode: 0,
    },
    setupNodeEvents(on, config) {
      on('before:run', async () => {
        await ensureFrontendAvailable();
        if (!fs.existsSync('reports')) fs.mkdirSync('reports', { recursive: true });
      });
      return config;
    },
  },
});
