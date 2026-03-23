/**
 * Puppeteer Jest 全局配置 — 双模兼容
 * - 统一超时设置
 * - JUnit 报告输出到 TestResults/
 * - 环境可达性检查 + Mock 自动启动（globalSetup）
 * - Mock 服务器自动关闭（globalTeardown）
 */
const path = require('path');

module.exports = {
  testMatch: ['**/tests/**/*.test.js'],
  testTimeout: 30000,
  maxWorkers: 2,
  forceExit: true,
  // 全局设置：检测前端 → 可达直连 / 不可达自动启动 mock-server
  globalSetup: path.join(__dirname, 'global-setup.js'),
  globalTeardown: path.join(__dirname, 'global-teardown.js'),
  reporters: [
    'default',
    ['jest-junit', {
      outputDirectory: path.join(__dirname, '..', '..', 'TestResults'),
      outputName: 'puppeteer-results.xml',
      classNameTemplate: '{classname}',
      titleTemplate: '{title}',
      ancestorSeparator: ' › ',
    }],
  ],
};
