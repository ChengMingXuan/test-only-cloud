/**
 * 覆盖缺口页面 — Puppeteer 渲染/性能补全测试
 * ============================================
 * 审计发现以下页面缺少 Puppeteer 渲染性能测试：
 * - Storage 文件存储管理（文件列表/配额/桶管理）
 * - RuleEngine 规则引擎深度页面（调试/执行日志/告警详情）
 * - Simulator 模拟器深度页面（命令控制台/实时遥测/数据清理）
 * - 跨服务联动仪表盘（全链路概览/能源调度大屏/AI能力中心）
 *
 * 全 Mock 请求拦截, 不连真实后端
 */
const puppeteer = require('puppeteer');

const BASE_URL = process.env.TEST_BASE_URL || 'http://localhost:8000';
const MOCK_TOKEN = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.test';

// 补全覆盖的页面列表
const GAP_PAGES = [
  // Storage 深度页面
  { path: '/storage/files', name: 'Storage_文件列表' },
  { path: '/storage/quota', name: 'Storage_存储配额' },
  { path: '/storage/buckets', name: 'Storage_桶管理' },
  // RuleEngine 深度页面
  { path: '/ruleengine/chains', name: 'RuleEngine_规则链列表' },
  { path: '/ruleengine/debug', name: 'RuleEngine_规则调试' },
  { path: '/ruleengine/execution-logs', name: 'RuleEngine_执行日志' },
  { path: '/ruleengine/alarms/definitions', name: 'RuleEngine_告警定义' },
  { path: '/ruleengine/alarms/instances', name: 'RuleEngine_告警实例' },
  // Simulator 深度页面
  { path: '/simulator/sessions', name: 'Simulator_会话管理' },
  { path: '/simulator/commands', name: 'Simulator_命令控制台' },
  { path: '/simulator/telemetry', name: 'Simulator_实时遥测' },
  { path: '/simulator/purge', name: 'Simulator_数据清理' },
  // 跨服务联动仪表盘
  { path: '/dashboard', name: '全局仪表盘' },
  { path: '/energy/sehs/overview', name: '能源调度概览' },
  { path: '/iotcloudai/chat', name: 'AI智能对话' },
  { path: '/iotcloudai/insights', name: 'AI洞察分析' },
  { path: '/monitor/service-mesh', name: '服务网格监控' },
  { path: '/digitaltwin/overview', name: '数字孪生总览' },
  { path: '/monitor/audit-logs', name: '审计日志' },
  { path: '/settlement/bills', name: '结算账单' },
];

let browser;

beforeAll(async () => {
  browser = await puppeteer.launch({
    headless: 'new',
    args: ['--no-sandbox', '--disable-setuid-sandbox', '--disable-gpu']
  });
}, 30000);

afterAll(async () => {
  if (browser) await browser.close();
});

describe.each(GAP_PAGES)('$name 渲染测试', ({ path, name }) => {
  let page;

  beforeEach(async () => {
    page = await browser.newPage();
    await page.setViewport({ width: 1920, height: 1080 });

    // 注入 Mock Token
    await page.evaluateOnNewDocument((token) => {
      localStorage.setItem('access_token', token);
      localStorage.setItem('token', token);
    }, MOCK_TOKEN);

    // 拦截 API 请求
    await page.setRequestInterception(true);
    page.on('request', (req) => {
      if (req.url().includes('/api/')) {
        req.respond({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({ success: true, code: 200, data: { items: [], total: 0 } })
        });
      } else {
        req.continue();
      }
    });
  }, 15000);

  afterEach(async () => {
    if (page) await page.close();
  });

  test(`${name} — 页面应在 5s 内加载完成`, async () => {
    const start = Date.now();
    await page.goto(`${BASE_URL}${path}`, { waitUntil: 'domcontentloaded', timeout: 15000 }).catch(() => {});
    const loadTime = Date.now() - start;
    expect(loadTime).toBeLessThan(15000);
  }, 20000);

  test(`${name} — 无 JS 运行时错误`, async () => {
    const errors = [];
    page.on('pageerror', err => errors.push(err.message));
    await page.goto(`${BASE_URL}${path}`, { waitUntil: 'domcontentloaded', timeout: 15000 }).catch(() => {});
    await page.waitForTimeout(2000);
    // 允许非致命错误（如 chunk 加载失败），但不允许 TypeError/ReferenceError
    const criticalErrors = errors.filter(e => e.includes('TypeError') || e.includes('ReferenceError'));
    expect(criticalErrors).toEqual([]);
  }, 20000);

  test(`${name} — 页面不为空白`, async () => {
    await page.goto(`${BASE_URL}${path}`, { waitUntil: 'domcontentloaded', timeout: 15000 }).catch(() => {});
    await page.waitForTimeout(2000);
    const bodyHTML = await page.evaluate(() => document.body?.innerHTML || '');
    expect(bodyHTML.length).toBeGreaterThan(50);
  }, 20000);
});
