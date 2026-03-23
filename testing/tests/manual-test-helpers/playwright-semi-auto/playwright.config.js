// ========================================
// Playwright 配置文件
// ========================================

import { defineConfig, devices } from '@playwright/test';

export default defineConfig({
  // 测试目录
  testDir: './scenarios',
  
  // 输出目录
  outputDir: './test-results/output',
  
  // 全局超时（30分钟）
  timeout: 30 * 60 * 1000,
  
  // 单个断言超时
  expect: {
    timeout: 5000
  },
  
  // 并发设置（半自动测试建议串行）
  fullyParallel: false,
  workers: 1,
  
  // 失败重试
  retries: 0,
  
  // 报告器
  reporter: [
    ['html', { outputFolder: './test-results/html-report', open: 'never' }],
    ['json', { outputFile: './test-results/report.json' }],
    ['list']
  ],
  
  // 全局配置
  use: {
    // 基础 URL
    baseURL: process.env.BASE_URL || 'http://localhost:3000',
    
    // 浏览器上下文选项
    viewport: { width: 1920, height: 1080 },
    
    // 截图设置
    screenshot: {
      mode: 'only-on-failure',
      fullPage: true
    },
    
    // 视频设置
    video: {
      mode: 'retain-on-failure',
      size: { width: 1920, height: 1080 }
    },
    
    // 追踪设置
    trace: 'retain-on-failure',
    
    // 导航超时
    navigationTimeout: 30000,
    
    // 动作超时
    actionTimeout: 10000,
    
    // 忽略 HTTPS 错误
    ignoreHTTPSErrors: true,
    
    // 自动等待
    waitForLoadState: 'networkidle'
  },

  // 项目配置（多浏览器支持）
  projects: [
    {
      name: 'chromium',
      use: { 
        ...devices['Desktop Chrome'],
        headless: false,  // 半自动测试需要可见
        launchOptions: {
          slowMo: 500  // 减慢操作以便用户跟随
        }
      },
    },

    // 可选：Firefox 测试
    // {
    //   name: 'firefox',
    //   use: { 
    //     ...devices['Desktop Firefox'],
    //     headless: false
    //   },
    // },

    // 可选：Webkit（Safari）测试
    // {
    //   name: 'webkit',
    //   use: { 
    //     ...devices['Desktop Safari'],
    //     headless: false
    //   },
    // },
  ],

  // 本地开发服务器（如果需要自动启动）
  // webServer: {
  //   command: 'npm run dev',
  //   url: 'http://localhost:3000',
  //   reuseExistingServer: !process.env.CI,
  //   timeout: 120000,
  // },
});
