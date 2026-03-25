/**
 * Cypress 快速测试配置
 * - 访问真实 UmiJS 前端页面
 * - 后端接口允许由 cy.intercept() Mock
 * - 适合语法/组件回归的快速验证
 */
const { defineConfig } = require('cypress');
const http = require('http');

let passCount = 0;
let failCount = 0;
let specCount = 0;
const FRONTEND_URL = 'http://127.0.0.1:8000';

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
    
    // 禁用视频和截图加速
    video: false,
    screenshotOnRunFailure: false,
    
    // 优化的超时（平衡速度和稳定性）
    defaultCommandTimeout: 8000,
    pageLoadTimeout: 15000,
    requestTimeout: 8000,
    responseTimeout: 8000,
    
    // 视口
    viewportWidth: 1280,
    viewportHeight: 720,
    
    // 重试策略（网络抖动时重试）
    retries: {
      runMode: 0,
      openMode: 0,
    },
    
    // 内存优化 + **降低并发防止限流**
    experimentalMemoryManagement: true,
    numTestsKeptInMemory: 0,
    
    setupNodeEvents(on, config) {
      const fs = require('fs');
      
      on('before:run', async () => {
        await ensureFrontendAvailable();
        if (!fs.existsSync('reports')) fs.mkdirSync('reports', { recursive: true });
        passCount = 0;
        failCount = 0;
        specCount = 0;
        console.log(`\n🚀 Cypress 执行（真实前端: ${FRONTEND_URL}，超时: 8s，重试: 2次，worker: 2 个）...\n`);
      });
      
      // 每个spec完成后输出进度
      on('after:spec', (spec, results) => {
        specCount++;
        if (results && results.stats) {
          passCount += results.stats.passes || 0;
          failCount += results.stats.failures || 0;
          
          // 每10个spec输出一次
          if (specCount % 10 === 0) {
            const now = new Date().toLocaleTimeString('zh-CN');
            console.log(`[${now}] 进度: ✅${passCount} / ❌${failCount} / 总${passCount+failCount} (文件${specCount})`);
          }
        }
      });
      
      on('after:run', (results) => {
        console.log('\n' + '='.repeat(50));
        console.log(`📊 测试完成: ✅通过 ${passCount} | ❌失败 ${failCount} | 总计 ${passCount + failCount}`);
        console.log('='.repeat(50) + '\n');
      });
      
      return config;
    },
  },
});
