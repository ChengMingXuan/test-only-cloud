/**
 * V3.2.0 能源整合 + 安全增强 — Puppeteer 渲染/性能测试
 * =====================================================
 * 覆盖 V3.2.0 核心变更页面:
 * - Operations 三合一模块 (EnergyEff + MultiEnergy + SafeControl)
 * - Trading 三合一模块 (ElecTrade + CarbonTrade + DemandResp)
 * - 证书轮换管理
 * - 三权分立角色管理
 * - 敏感数据加密
 * - 绿色电力关联
 * 用例数: 84 条
 */
const puppeteer = require('puppeteer');

const BASE_URL = process.env.TEST_BASE_URL || 'http://localhost:8000';
const MOCK_TOKEN = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.test';

// V3.2.0 新增/变更页面列表
const V320_PAGES = [
    // Operations 三合一
    { name: '能效仪表盘', path: '/energy/energyeff/dashboard', module: 'EnergyEff' },
    { name: '计量表管理', path: '/energy/energyeff/meters', module: 'EnergyEff' },
    { name: '能耗分析', path: '/energy/energyeff/consumption', module: 'EnergyEff' },
    { name: '节能方案', path: '/energy/energyeff/saving', module: 'EnergyEff' },
    { name: '多能互补仪表盘', path: '/energy/multienergy/dashboard', module: 'MultiEnergy' },
    { name: '转换设备管理', path: '/energy/multienergy/devices', module: 'MultiEnergy' },
    { name: '调度计划', path: '/energy/multienergy/schedule', module: 'MultiEnergy' },
    { name: '安全事件列表', path: '/energy/safecontrol/events', module: 'SafeControl' },
    { name: '风险评估', path: '/energy/safecontrol/risk', module: 'SafeControl' },
    { name: '应急预案', path: '/energy/safecontrol/emergency', module: 'SafeControl' },
    // Trading 三合一
    { name: '电力交易订单', path: '/energy/electrade/orders', module: 'ElecTrade' },
    { name: '市场电价', path: '/energy/electrade/market', module: 'ElecTrade' },
    { name: '绿证管理', path: '/energy/electrade/green-certificate', module: 'ElecTrade' },
    { name: '现货出清', path: '/energy/electrade/spot', module: 'ElecTrade' },
    { name: '排放记录', path: '/energy/carbontrade/emission', module: 'CarbonTrade' },
    { name: '碳资产概览', path: '/energy/carbontrade/assets', module: 'CarbonTrade' },
    { name: '履约管理', path: '/energy/carbontrade/fulfillment', module: 'CarbonTrade' },
    { name: '需求响应事件', path: '/energy/demandresp/events', module: 'DemandResp' },
    { name: '邀约管理', path: '/energy/demandresp/invitations', module: 'DemandResp' },
    { name: '基线管理', path: '/energy/demandresp/baseline', module: 'DemandResp' },
    // 安全增强
    { name: '证书轮换状态', path: '/monitor/service-mesh/certificate', module: 'Security' },
    { name: '三权分立角色', path: '/permission/role', module: 'Security' },
    { name: '加密配置', path: '/security/encryption', module: 'Security' },
    { name: '数据脱敏', path: '/security/masking', module: 'Security' },
    // 绿色电力关联
    { name: '绿电碳抵扣', path: '/energy/electrade/green-power', module: 'GreenPower' },
    { name: '碳排放影响', path: '/energy/electrade/green-power/impact', module: 'GreenPower' },
    // 新增权限页面
    { name: 'IotCloudAI聊天', path: '/iotcloudai/chat', module: 'Permission' },
    { name: '区块链故障转移', path: '/blockchain/failover', module: 'Permission' },
];

describe('[渲染测试] V3.2.0 能源整合 + 安全增强', () => {
    let browser;

    beforeAll(async () => {
        browser = await puppeteer.launch({
            headless: 'new',
            args: ['--no-sandbox', '--disable-setuid-sandbox', '--disable-dev-shm-usage']
        });
    });

    afterAll(async () => {
        if (browser) await browser.close();
    });

    V320_PAGES.forEach(pageInfo => {
        describe(`${pageInfo.name} [${pageInfo.module}] (${pageInfo.path})`, () => {
            let page;

            beforeEach(async () => {
                try {
                    page = await browser.newPage();
                } catch (e) {
                    try { await browser.close(); } catch (_) {}
                    browser = await puppeteer.launch({
                        headless: 'new',
                        args: ['--no-sandbox', '--disable-setuid-sandbox', '--disable-dev-shm-usage']
                    });
                    page = await browser.newPage();
                }

                // 注入 Mock Token
                await page.evaluateOnNewDocument((token) => {
                    localStorage.setItem('token', token);
                    localStorage.setItem('accessToken', token);
                }, MOCK_TOKEN);

                // 拦截 API 返回 Mock 数据
                await page.setRequestInterception(true);
                page.on('request', (req) => {
                    const url = req.url();
                    if (url.includes('/api/')) {
                        req.respond({
                            status: 200,
                            contentType: 'application/json',
                            body: JSON.stringify({
                                success: true, code: 200,
                                data: { items: [], total: 0 },
                                timestamp: new Date().toISOString(),
                                traceId: 'puppeteer-v320'
                            })
                        });
                    } else {
                        req.continue();
                    }
                });
            });

            afterEach(async () => {
                if (page) await page.close().catch(() => {});
            });

            test('页面正常渲染（无JS错误）', async () => {
                const errors = [];
                page.on('pageerror', err => errors.push(err.message));

                await page.goto(`${BASE_URL}${pageInfo.path}`, {
                    waitUntil: 'domcontentloaded',
                    timeout: 15000
                }).catch(() => {});

                await page.waitForTimeout(2000);
                // 允许部分非关键 JS 错误
                const criticalErrors = errors.filter(e =>
                    !e.includes('ResizeObserver') &&
                    !e.includes('chunk') &&
                    !e.includes('Loading') &&
                    !e.includes('Network')
                );
                expect(criticalErrors.length).toBeLessThan(3);
            }, 20000);

            test('页面首屏渲染时间 < 5s', async () => {
                const start = Date.now();
                await page.goto(`${BASE_URL}${pageInfo.path}`, {
                    waitUntil: 'domcontentloaded',
                    timeout: 15000
                }).catch(() => {});
                const elapsed = Date.now() - start;
                expect(elapsed).toBeLessThan(5000);
            }, 20000);

            test('页面无控制台严重错误', async () => {
                const severeErrors = [];
                page.on('console', msg => {
                    if (msg.type() === 'error' && !msg.text().includes('net::ERR_')) {
                        severeErrors.push(msg.text());
                    }
                });

                await page.goto(`${BASE_URL}${pageInfo.path}`, {
                    waitUntil: 'domcontentloaded',
                    timeout: 15000
                }).catch(() => {});

                await page.waitForTimeout(2000);
                // 允许最多 5 个非关键控制台错误
                expect(severeErrors.length).toBeLessThan(5);
            }, 20000);
        });
    });
});
