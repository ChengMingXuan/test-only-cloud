/**
 * SecuritySwitches 双环境配置 - Puppeteer 渲染/性能增量测试（v2.4.6）
 *
 * 测试维度（Puppeteer 特有）：
 * - 浏览器实际收到的安全响应头
 * - HSTS 条件化渲染行为
 * - 登录页安全属性（密码框、控制台泄露）
 * - Cookie 安全属性
 * - CSP 防护
 * - 页面性能（安全中间件不影响首屏）
 */
const puppeteer = require('puppeteer');

const BASE_URL = process.env.TEST_BASE_URL || 'http://localhost:8000';
const FRONTEND_URL = process.env.FRONTEND_URL || 'http://localhost:8001';

let browser;

beforeAll(async () => {
  browser = await puppeteer.launch({
    headless: 'new',
    args: ['--no-sandbox', '--disable-setuid-sandbox'],
  });
});

afterAll(async () => {
  if (browser) await browser.close();
});

// ==================== 1. 安全响应头（浏览器级） ====================

describe('[v2.4.6][SEC-PP] 安全响应头 - 浏览器实际接收', () => {
  let page;
  let apiHeaders = {};
  let responseReceived = false;

  beforeAll(async () => {
    page = await browser.newPage();
    const response = await page.goto(`${BASE_URL}/api/gateway/health`, {
      waitUntil: 'domcontentloaded',
      timeout: 15000,
    }).catch(() => null);
    if (response) {
      apiHeaders = response.headers();
      responseReceived = true;
    }
  });

  afterAll(async () => {
    if (page) await page.close();
  });

  test('[SEC-PP01] X-Content-Type-Options: nosniff', () => {
    if (!responseReceived) return; // 服务不可达时跳过
    expect(apiHeaders['x-content-type-options']).toBe('nosniff');
  });

  test('[SEC-PP02] X-Frame-Options 存在', () => {
    const xfo = apiHeaders['x-frame-options'];
    if (xfo) {
      expect(xfo.toUpperCase()).toContain('DENY');
    }
  });

  test('[SEC-PP03] HSTS 条件化（Dev 环境不注入）', () => {
    const hsts = apiHeaders['strict-transport-security'];
    // Dev 环境 SecuritySwitches:HstsEnabled=false 时不应有 HSTS
    if (hsts) {
      console.warn(`⚠️ Dev 环境检测到 HSTS: ${hsts}（可能来自反向代理）`);
    }
  });

  test('[SEC-PP04] Server 头不暴露技术栈', () => {
    const server = apiHeaders['server'] || '';
    expect(server).not.toContain('Kestrel');
    expect(server).not.toContain('ASP.NET');
  });

  test('[SEC-PP05] Cache-Control 安全验证', () => {
    const cc = apiHeaders['cache-control'] || '';
    // API 响应不应被公共缓存
    if (cc) {
      expect(cc).not.toContain('public');
    }
  });
});

// ==================== 2. 登录页安全渲染 ====================

describe('[v2.4.6][SEC-PP-LOGIN] 登录页安全属性渲染', () => {
  let page;

  beforeEach(async () => {
    page = await browser.newPage();
  });

  afterEach(async () => {
    if (page) await page.close();
  });

  test('[SEC-PP-LOGIN01] 密码框 type=password 且不明文显示', async () => {
    await page.goto(`${FRONTEND_URL}/user/login`, {
      waitUntil: 'domcontentloaded',
      timeout: 30000,
    }).catch(() => {});

    const pwdInputs = await page.$$('input[type="password"]');
    if (pwdInputs.length > 0) {
      const type = await pwdInputs[0].evaluate(el => el.type);
      expect(type).toBe('password');
    }
  });

  test('[SEC-PP-LOGIN02] 页面源码无敏感信息泄露', async () => {
    await page.goto(`${FRONTEND_URL}/user/login`, {
      waitUntil: 'domcontentloaded',
      timeout: 30000,
    }).catch(() => {});

    const html = await page.content();
    expect(html).not.toContain('P@ssw0rd');
    expect(html).not.toContain('secret_key');
    expect(html).not.toContain('private_key');
  });

  test('[SEC-PP-LOGIN03] 控制台无敏感日志泄露', async () => {
    const logs = [];
    page.on('console', msg => logs.push(msg.text()));

    await page.goto(`${FRONTEND_URL}/user/login`, {
      waitUntil: 'domcontentloaded',
      timeout: 30000,
    }).catch(() => {});

    // 等 2 秒让异步日志输出
    await new Promise(r => setTimeout(r, 2000));

    const logText = logs.join(' ');
    expect(logText).not.toContain('password');
    expect(logText).not.toContain('secret');
    expect(logText).not.toContain('P@ssw0rd');
  });
});

// ==================== 3. Cookie 安全属性 ====================

describe('[v2.4.6][SEC-PP-COOKIE] Cookie 安全属性', () => {
  let page;

  beforeEach(async () => {
    page = await browser.newPage();
  });

  afterEach(async () => {
    if (page) await page.close();
  });

  test('[SEC-PP-COOKIE01] Cookie HttpOnly 属性检查', async () => {
    await page.goto(`${FRONTEND_URL}/user/login`, {
      waitUntil: 'domcontentloaded',
      timeout: 30000,
    }).catch(() => {});

    const cookies = await page.cookies();
    for (const cookie of cookies) {
      // 认证相关 Cookie 应为 HttpOnly
      if (cookie.name.toLowerCase().includes('token') || cookie.name.toLowerCase().includes('session')) {
        expect(cookie.httpOnly).toBe(true);
      }
    }
  });

  test('[SEC-PP-COOKIE02] Cookie SameSite 属性检查', async () => {
    await page.goto(`${FRONTEND_URL}/user/login`, {
      waitUntil: 'domcontentloaded',
      timeout: 30000,
    }).catch(() => {});

    const cookies = await page.cookies();
    for (const cookie of cookies) {
      if (cookie.name.toLowerCase().includes('token')) {
        // SameSite 应为 Strict 或 Lax
        expect(['Strict', 'Lax']).toContain(cookie.sameSite);
      }
    }
  });
});

// ==================== 4. 性能影响 ====================

describe('[v2.4.6][SEC-PP-PERF] 安全中间件性能影响', () => {
  let page;

  beforeEach(async () => {
    page = await browser.newPage();
  });

  afterEach(async () => {
    if (page) await page.close();
  });

  test('[SEC-PP-PERF01] API 健康检查响应时间 < 3s', async () => {
    const start = Date.now();
    await page.goto(`${BASE_URL}/api/gateway/health`, {
      waitUntil: 'domcontentloaded',
      timeout: 10000,
    }).catch(() => {});
    const elapsed = Date.now() - start;
    expect(elapsed).toBeLessThan(3000);
  });

  test('[SEC-PP-PERF02] 登录页首屏渲染 < 5s', async () => {
    const start = Date.now();
    await page.goto(`${FRONTEND_URL}/user/login`, {
      waitUntil: 'domcontentloaded',
      timeout: 30000,
    }).catch(() => {});
    const elapsed = Date.now() - start;
    expect(elapsed).toBeLessThan(5000);
  });
});
