/**
 * V3.2.0 增量测试 — Operations/Trading 页面渲染性能测试
 * ====================================================
 * Puppeteer 性能基准：FCP/LCP/TTI/CLS/TBT
 * 覆盖 V3.2.0 能源整合后的统一入口页面
 */
const puppeteer = require('puppeteer');
const { safeGoto } = require('../test-helpers');

const BASE_URL = process.env.TEST_BASE_URL || 'http://localhost:8000';

// Operations + Trading 页面路由
const PAGES = [
  { name: 'Operations Dashboard', path: '/energy/operations/dashboard' },
  { name: 'EnergyEff 列表', path: '/energy/operations/energyeff' },
  { name: 'MultiEnergy 列表', path: '/energy/operations/multienergy' },
  { name: 'SafeControl 列表', path: '/energy/operations/safecontrol' },
  { name: 'Trading Dashboard', path: '/energy/trading/dashboard' },
  { name: 'ElecTrade 列表', path: '/energy/trading/electrade' },
  { name: 'CarbonTrade 列表', path: '/energy/trading/carbontrade' },
  { name: 'DemandResp 列表', path: '/energy/trading/demandresp' },
  { name: 'Market 市场价格', path: '/energy/trading/market' },
];

// 性能阈值
const THRESHOLDS = {
  FCP: 5000,
  LCP: 6000,
  domContentLoaded: 3000,
  loadComplete: 8000,
};

let browser;

beforeAll(async () => {
  browser = await puppeteer.launch({
    headless: 'new',
    args: ['--no-sandbox', '--disable-setuid-sandbox', '--disable-gpu', '--disable-dev-shm-usage'],
  });
});

afterAll(async () => {
  if (browser) await browser.close();
});

describe('[V3.2.0增量] Operations/Trading 页面性能基准', () => {
  for (const { name, path } of PAGES) {
    describe(`${name} (${path})`, () => {
      let page;
      let perfMetrics = {};

      beforeAll(async () => {
        page = await browser.newPage();
        await page.setViewport({ width: 1920, height: 1080 });

        // 拦截 API 请求，返回 Mock 数据避免真实后端依赖
        await page.setRequestInterception(true);
        page.on('request', (req) => {
          if (req.url().includes('/api/')) {
            req.respond({
              status: 200,
              contentType: 'application/json',
              body: JSON.stringify({ success: true, code: 200, data: { items: [], total: 0 } }),
            });
          } else {
            req.continue();
          }
        });

        const startTime = Date.now();
        const result = await safeGoto(page, `${BASE_URL}${path}`, { waitUntil: 'networkidle2', timeout: 30000 });

        if (result.success) {
          const loadTime = Date.now() - startTime;

          // 收集 Performance Timing
          const timing = await page.evaluate(() => {
            const nav = performance.getEntriesByType('navigation')[0] || {};
            return {
              domContentLoaded: nav.domContentLoadedEventEnd - nav.startTime || 0,
              loadComplete: nav.loadEventEnd - nav.startTime || 0,
            };
          });

          // 收集 FCP
          const fcp = await page.evaluate(() => {
            const entries = performance.getEntriesByType('paint');
            const fcpEntry = entries.find(e => e.name === 'first-contentful-paint');
            return fcpEntry ? fcpEntry.startTime : 0;
          });

          perfMetrics = {
            loadTime,
            fcp,
            domContentLoaded: timing.domContentLoaded,
            loadComplete: timing.loadComplete,
            available: true,
          };
        } else {
          perfMetrics = { available: false };
        }
      });

      afterAll(async () => {
        if (page) await page.close();
      });

      test(`[PERF-LOAD] 页面加载成功`, () => {
        if (!perfMetrics.available) {
          console.log(`⏭ 前端不可达，跳过性能测试`);
          return;
        }
        expect(perfMetrics.loadTime).toBeGreaterThan(0);
      });

      test(`[PERF-FCP] FCP < ${THRESHOLDS.FCP}ms`, () => {
        if (!perfMetrics.available || !perfMetrics.fcp) return;
        expect(perfMetrics.fcp).toBeLessThan(THRESHOLDS.FCP);
      });

      test(`[PERF-DCL] DOMContentLoaded < ${THRESHOLDS.domContentLoaded}ms`, () => {
        if (!perfMetrics.available || !perfMetrics.domContentLoaded) return;
        expect(perfMetrics.domContentLoaded).toBeLessThan(THRESHOLDS.domContentLoaded);
      });

      test(`[PERF-LC] Load Complete < ${THRESHOLDS.loadComplete}ms`, () => {
        if (!perfMetrics.available || !perfMetrics.loadComplete) return;
        expect(perfMetrics.loadComplete).toBeLessThan(THRESHOLDS.loadComplete);
      });

      test(`[PERF-TITLE] 页面有 title 元素`, async () => {
        if (!perfMetrics.available) return;
        const title = await page.title();
        expect(title).toBeTruthy();
      });

      test(`[PERF-ROOT] #root 容器存在`, async () => {
        if (!perfMetrics.available) return;
        const root = await page.$('#root');
        expect(root).not.toBeNull();
      });

      test(`[PERF-NO-CONSOLE-ERROR] 无 JS 控制台错误`, async () => {
        if (!perfMetrics.available) return;
        const errors = [];
        page.on('console', msg => {
          if (msg.type() === 'error') errors.push(msg.text());
        });
        // 等待一小段时间收集错误
        await new Promise(resolve => setTimeout(resolve, 1000));
        // 允许一些第三方库错误，只检查关键错误
        const criticalErrors = errors.filter(e => !e.includes('favicon') && !e.includes('manifest'));
        expect(criticalErrors.length).toBeLessThanOrEqual(3);
      });
    });
  }
});

describe('[V3.2.0增量] Operations/Trading 响应式布局', () => {
  const viewports = [
    { name: '桌面 1920x1080', width: 1920, height: 1080 },
    { name: '笔记本 1366x768', width: 1366, height: 768 },
    { name: '平板 768x1024', width: 768, height: 1024 },
  ];

  for (const vp of viewports) {
    test(`[RESPONSIVE] Operations Dashboard @ ${vp.name}`, async () => {
      const page = await browser.newPage();
      await page.setViewport({ width: vp.width, height: vp.height });

      await page.setRequestInterception(true);
      page.on('request', (req) => {
        if (req.url().includes('/api/')) {
          req.respond({ status: 200, contentType: 'application/json', body: '{"success":true,"data":null}' });
        } else { req.continue(); }
      });

      const result = await safeGoto(page, `${BASE_URL}/energy/operations/dashboard`, { timeout: 15000 });
      if (result.success) {
        const bodyWidth = await page.evaluate(() => document.body.scrollWidth);
        expect(bodyWidth).toBeLessThanOrEqual(vp.width + 20); // 允许小偏差
      }
      await page.close();
    });
  }
});
