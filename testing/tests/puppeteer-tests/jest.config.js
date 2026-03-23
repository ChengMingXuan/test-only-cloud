/**
 * Puppeteer Jest 全局配置
 * - 统一超时设置
 * - JUnit 报告输出到 TestResults/
 * - 环境可达性检查（globalSetup）
 */
const path = require('path');

module.exports = {
  testMatch: ['**/tests/**/*.test.js'],
  testTimeout: 30000,
  maxWorkers: 2,
  forceExit: true,
  // 全局设置：检测前端服务可达性
  globalSetup: path.join(__dirname, 'global-setup.js'),
  // 每个测试文件执行前注入环境容错
  setupFilesAfterFramework: [path.join(__dirname, 'jest-env-setup.js')],
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
