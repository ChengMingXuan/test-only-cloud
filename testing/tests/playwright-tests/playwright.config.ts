import { defineConfig, devices } from '@playwright/test';

/**
 * Playwright 配置文件
 * AIOPS 平台端到端测试配置
 * 
 * 核心特性:
 * - 跨浏览器测试 (Chrome/Firefox/Safari)
 * - 并行执行 (最多4个worker)
 * - 失败重试 (最多2次)
 * - 视频录制 (仅失败用例)
 * - 追踪 (仅失败用例)
 * - 截图 (仅失败时)
 */

export default defineConfig({
  // 测试目录
  testDir: './tests',
  
  // 测试匹配模式
  testMatch: '**/*.spec.ts',
  
  // 全局超时设置
  timeout: 60 * 1000, // 单个测试60秒超时
  expect: {
    timeout: 10 * 1000, // 断言10秒超时
  },
  
  // 失败重试（FULL_RUN 模式不重试以减少内存压力）
  retries: process.env.FULL_RUN ? 0 : (process.env.CI ? 2 : 1),
  
  // 并行执行
  workers: process.env.CI ? 2 : 4, // CI环境2个worker，本地4个
  
  // 全局配置
  fullyParallel: true, // 完全并行执行测试
  forbidOnly: !!process.env.CI, // CI环境禁止使用test.only
  
  // 测试产物输出目录（相对路径，确保在项目 D 盘目录内）
  outputDir: './test-results',
  
  // 报告器配置（JUnit 输出到项目根 TestResults/ 统一目录）
  reporter: process.env.FULL_RUN ? [
    // 全量运行模式：使用 JUnit（流式写入不占内存）+ dot（轻量控制台输出）
    ['junit', { outputFile: '../../TestResults/playwright-results.xml' }],
    ['dot'],
  ] : [
    ['html', { outputFolder: '../test-reports/playwright-report', open: 'never' }],
    ['json', { outputFile: '../test-reports/playwright-report/results.json' }],
    ['junit', { outputFile: '../../TestResults/playwright-results.xml' }],
    ['list'], // 控制台输出
  ],
  
  // 通用测试配置
  use: {
    // 基础URL - Mock 模式使用本地服务器
    baseURL: process.env.TEST_BASE_URL || 'http://localhost:8000',
    
    // 追踪配置（全量运行时禁用以避免内存溢出）
    trace: process.env.FULL_RUN ? 'off' : 'retain-on-failure',
    
    // 截图配置（全量运行时禁用）
    screenshot: process.env.FULL_RUN ? 'off' : 'only-on-failure',
    
    // 视频录制（全量运行时禁用）
    video: process.env.FULL_RUN ? 'off' : 'retain-on-failure',
    
    // 浏览器上下文选项
    viewport: { width: 1280, height: 720 },
    ignoreHTTPSErrors: true,
    
    // 操作超时
    actionTimeout: 15 * 1000, // 15秒
    navigationTimeout: 30 * 1000, // 30秒
    
    // 自定义存储状态目录
    storageState: undefined,
  },
  
  // 浏览器项目配置
  projects: [
    // ========== Chromium (Chrome) ==========
    {
      name: 'chromium',
      use: { 
        ...devices['Desktop Chrome'],
        // Chrome特定配置
        launchOptions: {
          args: [
            '--disable-blink-features=AutomationControlled', // 绕过自动化检测
            '--disable-dev-shm-usage',
            '--no-sandbox',
          ],
        },
      },
    },
    
    // ========== Firefox ==========
    {
      name: 'firefox',
      use: { 
        ...devices['Desktop Firefox'],
        // Firefox特定配置
        launchOptions: {
          firefoxUserPrefs: {
            'media.navigator.streams.fake': true,
          },
        },
      },
    },
    
    // ========== WebKit (Safari) ==========
    {
      name: 'webkit',
      use: { 
        ...devices['Desktop Safari'],
        // Safari特定配置
      },
    },
    
    // ========== Mobile Chrome ==========
    {
      name: 'mobile-chrome',
      use: { 
        ...devices['Pixel 5'],
      },
    },
    
    // ========== Mobile Safari ==========
    {
      name: 'mobile-safari',
      use: { 
        ...devices['iPhone 13'],
      },
    },
    
    // ========== 高分辨率桌面 ==========
    {
      name: 'desktop-hd',
      use: {
        ...devices['Desktop Chrome'],
        viewport: { width: 1920, height: 1080 },
      },
    },
    
    // ========== Tablet ==========
    {
      name: 'tablet',
      use: {
        ...devices['iPad (gen 7)'],
      },
    },
  ],
  
  // Web Server配置（如果需要本地启动开发服务器）
  // webServer: {
  //   command: 'npm run dev',
  //   port: 3000,
  //   timeout: 120 * 1000,
  //   reuseExistingServer: !process.env.CI,
  // },
  
  // 全局设置和清理
  globalSetup: require.resolve('./global-setup.ts'),
  globalTeardown: require.resolve('./global-teardown.ts'),
});
