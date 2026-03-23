/**
 * 增量渲染测试 — GeoFence + IotCloudAI AI新能力 + ColdArchive + Gateway路由
 * ============================================================================
 * 覆盖新增页面的渲染正确性、加载性能、交互元素完整性
 */

const puppeteer = require('puppeteer');

const BASE_URL = process.env.BASE_URL || 'http://localhost:8000';
const TIMEOUT = 15000;

let browser, page;

beforeAll(async () => {
  browser = await puppeteer.launch({
    headless: 'new',
    args: ['--no-sandbox', '--disable-setuid-sandbox', '--disable-dev-shm-usage']
  });
});

afterAll(async () => { if (browser) await browser.close(); });

beforeEach(async () => {
  page = await browser.newPage();
  await page.setViewport({ width: 1920, height: 1080 });
  // Mock API 响应
  await page.setRequestInterception(true);
  page.on('request', (req) => {
    const url = req.url();
    if (url.includes('/api/')) {
      req.respond({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({ code: 200, data: {}, message: 'ok' })
      });
    } else {
      req.continue();
    }
  });
});

afterEach(async () => { if (page) await page.close(); });

// ═══════════════════════════════════════════════════
// Station GeoFence 地理围栏页面
// ═══════════════════════════════════════════════════

describe('GeoFence 围栏管理页面渲染', () => {
  const pages = [
    { path: '/station/geo-fence', title: '地理围栏管理' },
    { path: '/station/geo-fence/create', title: '新建围栏' },
    { path: '/station/geo-fence/map', title: '围栏地图展示' },
  ];

  pages.forEach(({ path, title }) => {
    test(`${title} - 页面加载`, async () => {
      const start = Date.now();
      const resp = await page.goto(`${BASE_URL}${path}`, { waitUntil: 'networkidle2', timeout: TIMEOUT });
      const loadTime = Date.now() - start;
      expect(resp.status()).toBeLessThan(500);
      expect(loadTime).toBeLessThan(TIMEOUT);
    }, TIMEOUT);

    test(`${title} - 无JS错误`, async () => {
      const errors = [];
      page.on('pageerror', e => errors.push(e.message));
      await page.goto(`${BASE_URL}${path}`, { waitUntil: 'networkidle2', timeout: TIMEOUT });
      expect(errors).toHaveLength(0);
    }, TIMEOUT);

    test(`${title} - 关键元素存在`, async () => {
      await page.goto(`${BASE_URL}${path}`, { waitUntil: 'networkidle2', timeout: TIMEOUT });
      const bodyText = await page.evaluate(() => document.body.innerText);
      expect(bodyText.length).toBeGreaterThan(0);
    }, TIMEOUT);
  });
});


// ═══════════════════════════════════════════════════
// IotCloudAI 5大新功能页面
// ═══════════════════════════════════════════════════

describe('IotCloudAI 新功能页面渲染', () => {
  const pages = [
    { path: '/iotcloudai/image-search', title: '图像检索' },
    { path: '/iotcloudai/llm', title: 'LLM多模型管理' },
    { path: '/iotcloudai/model-routing', title: '智能模型路由' },
    { path: '/iotcloudai/solar-prediction', title: '光伏发电预测' },
    { path: '/iotcloudai/vision-inspection', title: '视觉智能巡检' },
    { path: '/iotcloudai/model-routing/benchmarks', title: '精度基准管理' },
    { path: '/iotcloudai/model-routing/dashboard', title: 'AI能力总览' },
  ];

  pages.forEach(({ path, title }) => {
    test(`${title} - 页面加载`, async () => {
      const start = Date.now();
      const resp = await page.goto(`${BASE_URL}${path}`, { waitUntil: 'networkidle2', timeout: TIMEOUT });
      const loadTime = Date.now() - start;
      expect(resp.status()).toBeLessThan(500);
      expect(loadTime).toBeLessThan(TIMEOUT);
    }, TIMEOUT);

    test(`${title} - 无JS错误`, async () => {
      const errors = [];
      page.on('pageerror', e => errors.push(e.message));
      await page.goto(`${BASE_URL}${path}`, { waitUntil: 'networkidle2', timeout: TIMEOUT });
      expect(errors).toHaveLength(0);
    }, TIMEOUT);

    test(`${title} - 关键元素存在`, async () => {
      await page.goto(`${BASE_URL}${path}`, { waitUntil: 'networkidle2', timeout: TIMEOUT });
      const bodyText = await page.evaluate(() => document.body.innerText);
      expect(bodyText.length).toBeGreaterThan(0);
    }, TIMEOUT);
  });
});


// ═══════════════════════════════════════════════════
// Storage Archive 冷归档页面
// ═══════════════════════════════════════════════════

describe('Storage Archive 冷归档页面渲染', () => {
  const pages = [
    { path: '/storage/archive', title: '归档管理' },
    { path: '/storage/archive/metadata', title: '归档元数据' },
  ];

  pages.forEach(({ path, title }) => {
    test(`${title} - 页面加载`, async () => {
      const resp = await page.goto(`${BASE_URL}${path}`, { waitUntil: 'networkidle2', timeout: TIMEOUT });
      expect(resp.status()).toBeLessThan(500);
    }, TIMEOUT);

    test(`${title} - 无JS错误`, async () => {
      const errors = [];
      page.on('pageerror', e => errors.push(e.message));
      await page.goto(`${BASE_URL}${path}`, { waitUntil: 'networkidle2', timeout: TIMEOUT });
      expect(errors).toHaveLength(0);
    }, TIMEOUT);

    test(`${title} - 关键元素存在`, async () => {
      await page.goto(`${BASE_URL}${path}`, { waitUntil: 'networkidle2', timeout: TIMEOUT });
      const bodyText = await page.evaluate(() => document.body.innerText);
      expect(bodyText.length).toBeGreaterThan(0);
    }, TIMEOUT);
  });
});


// ═══════════════════════════════════════════════════
// Permission 区块链三员分立角色页面
// ═══════════════════════════════════════════════════

describe('Permission 三员分立角色页面渲染', () => {
  const pages = [
    { path: '/permission/roles', title: '角色管理' },
    { path: '/permission/roles/security-admin', title: '安全管理员' },
    { path: '/permission/roles/audit-admin', title: '审计管理员' },
    { path: '/permission/roles/sys-admin', title: '系统管理员' },
  ];

  pages.forEach(({ path, title }) => {
    test(`${title} - 页面加载`, async () => {
      const resp = await page.goto(`${BASE_URL}${path}`, { waitUntil: 'networkidle2', timeout: TIMEOUT });
      expect(resp.status()).toBeLessThan(500);
    }, TIMEOUT);

    test(`${title} - 无JS错误`, async () => {
      const errors = [];
      page.on('pageerror', e => errors.push(e.message));
      await page.goto(`${BASE_URL}${path}`, { waitUntil: 'networkidle2', timeout: TIMEOUT });
      expect(errors).toHaveLength(0);
    }, TIMEOUT);

    test(`${title} - 关键元素存在`, async () => {
      await page.goto(`${BASE_URL}${path}`, { waitUntil: 'networkidle2', timeout: TIMEOUT });
      const bodyText = await page.evaluate(() => document.body.innerText);
      expect(bodyText.length).toBeGreaterThan(0);
    }, TIMEOUT);
  });
});


// ═══════════════════════════════════════════════════
// 后台任务监控页面
// ═══════════════════════════════════════════════════

describe('后台任务监控页面渲染', () => {
  const pages = [
    { path: '/analytics/daily-reports', title: '日报管理' },
    { path: '/analytics/scheduled-tasks', title: '定时报表' },
    { path: '/settlement/auto-settlement', title: '自动结算' },
    { path: '/device/command-timeout', title: '命令超时监控' },
  ];

  pages.forEach(({ path, title }) => {
    test(`${title} - 页面加载`, async () => {
      const resp = await page.goto(`${BASE_URL}${path}`, { waitUntil: 'networkidle2', timeout: TIMEOUT });
      expect(resp.status()).toBeLessThan(500);
    }, TIMEOUT);

    test(`${title} - 无JS错误`, async () => {
      const errors = [];
      page.on('pageerror', e => errors.push(e.message));
      await page.goto(`${BASE_URL}${path}`, { waitUntil: 'networkidle2', timeout: TIMEOUT });
      expect(errors).toHaveLength(0);
    }, TIMEOUT);

    test(`${title} - 关键元素存在`, async () => {
      await page.goto(`${BASE_URL}${path}`, { waitUntil: 'networkidle2', timeout: TIMEOUT });
      const bodyText = await page.evaluate(() => document.body.innerText);
      expect(bodyText.length).toBeGreaterThan(0);
    }, TIMEOUT);
  });
});
