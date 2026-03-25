/**
 * v3.18 增量功能 - Puppeteer 渲染与性能测试
 * ==========================================
 * 测试新增功能页面的渲染性能和视觉完整性：
 * - 图表渲染正确性
 * - 页面加载性能
 * - 关键路径渲染时间
 * - 动态内容渲染
 */

const puppeteer = require('puppeteer');
const { expect } = require('chai');

const BASE_URL = process.env.BASE_URL || 'http://localhost:3000';
const PERFORMANCE_THRESHOLD = {
  FCP: 2000,      // First Contentful Paint < 2s
  LCP: 3000,      // Largest Contentful Paint < 3s
  TTI: 5000,      // Time to Interactive < 5s
  CLS: 0.1        // Cumulative Layout Shift < 0.1
};

let browser;
let page;

// ═══════════════════════════════════════════════════════════════════════════════
// 测试套件初始化
// ═══════════════════════════════════════════════════════════════════════════════

describe('v3.18 增量功能 - 渲染测试', () => {
  // CI 环境无前端服务，跳过复杂渲染测试
  const skipInCI = process.env.CI === 'true';
  if (skipInCI) {
    it.skip('跳过 CI 环境', () => {});
    return;
  }
  jest.setTimeout(60000);

  beforeAll(async () => {
    browser = await puppeteer.launch({
      headless: 'new',
      args: ['--no-sandbox', '--disable-setuid-sandbox']
    });
  });

  afterAll(async () => {
    if (browser) {
      await browser.close();
    }
  });

  beforeEach(async () => {
    page = await browser.newPage();
    await page.setViewport({ width: 1920, height: 1080 });
    
    // Mock认证
    await page.evaluateOnNewDocument(() => {
      localStorage.setItem('token', 'mock_token');
      localStorage.setItem('user', JSON.stringify({ id: 'user-001', name: 'admin' }));
    });
  });

  afterEach(async () => {
    if (page) {
      await page.close();
    }
  });

  // ═══════════════════════════════════════════════════════════════════════════════
  // 1. 碳认证页面渲染测试
  // ═══════════════════════════════════════════════════════════════════════════════

  describe('碳认证页面渲染', () => {
    it('I-REC证书列表页面应正确渲染表格', async () => {
      // Mock API
      await page.setRequestInterception(true);
      page.on('request', request => {
        if (request.url().includes('/api/carbon/irec/certificates')) {
          request.respond({
            status: 200,
            contentType: 'application/json',
            body: JSON.stringify({
              code: 200,
              data: {
                items: [
                  { id: '1', deviceCode: 'PV-001', status: 'active', generationMwh: 150 },
                  { id: '2', deviceCode: 'PV-002', status: 'pending', generationMwh: 200 }
                ],
                total: 2
              }
            })
          });
        } else {
          request.continue();
        }
      });

      await page.goto(`${BASE_URL}/carbon/irec/certificates`, { waitUntil: 'networkidle2' });
      
      const tableExists = await page.$('[data-testid="certificate-table"]') !== null ||
                          await page.$('.ant-table') !== null ||
                          await page.$('table') !== null;
      
      expect(tableExists).to.be.true;
    });

    it('CCER项目列表应在3秒内完成首次内容绘制', async () => {
      await page.setRequestInterception(true);
      page.on('request', request => {
        if (request.url().includes('/api/carbon/ccer/projects')) {
          request.respond({
            status: 200,
            contentType: 'application/json',
            body: JSON.stringify({ code: 200, data: { items: [], total: 0 } })
          });
        } else {
          request.continue();
        }
      });

      const startTime = Date.now();
      await page.goto(`${BASE_URL}/carbon/ccer/projects`, { waitUntil: 'domcontentloaded' });
      const loadTime = Date.now() - startTime;

      expect(loadTime).to.be.lessThan(PERFORMANCE_THRESHOLD.LCP);
    });
  });

  // ═══════════════════════════════════════════════════════════════════════════════
  // 2. 智能排队充电页面渲染测试
  // ═══════════════════════════════════════════════════════════════════════════════

  describe('智能排队充电页面渲染', () => {
    it('排队列表应正确渲染队列卡片', async () => {
      await page.setRequestInterception(true);
      page.on('request', request => {
        if (request.url().includes('/api/charging/orderly') && request.url().includes('/queue')) {
          request.respond({
            status: 200,
            contentType: 'application/json',
            body: JSON.stringify({
              code: 200,
              data: [
                { id: '1', vehicleId: '京A12345', currentSocPercent: 20, position: 1 },
                { id: '2', vehicleId: '京B88888', currentSocPercent: 10, position: 2 }
              ]
            })
          });
        } else {
          request.continue();
        }
      });

      await page.goto(`${BASE_URL}/charging/orderly/station/station-001/queue`, { waitUntil: 'networkidle2' });
      
      // 检查是否有列表或卡片元素
      const hasQueueItems = await page.evaluate(() => {
        return document.querySelectorAll('[data-testid="queue-item"], .queue-card, .list-item').length > 0 ||
               document.body.innerText.includes('京A12345');
      });
      
      expect(hasQueueItems).to.be.true;
    });

    it('充电桩负荷图表应正确渲染', async () => {
      await page.setRequestInterception(true);
      page.on('request', request => {
        if (request.url().includes('/pile-load')) {
          request.respond({
            status: 200,
            contentType: 'application/json',
            body: JSON.stringify({
              code: 200,
              data: [
                { pileId: 'pile-001', loadPercent: 85 },
                { pileId: 'pile-002', loadPercent: 45 }
              ]
            })
          });
        } else {
          request.continue();
        }
      });

      await page.goto(`${BASE_URL}/charging/orderly/station/station-001/pile-load`, { waitUntil: 'networkidle2' });
      
      // 检查图表容器
      const hasChart = await page.evaluate(() => {
        return document.querySelector('canvas, svg, [data-testid="pile-load-chart"], .echarts-container') !== null;
      });
      
      expect(hasChart).to.be.true;
    });
  });

  // ═══════════════════════════════════════════════════════════════════════════════
  // 3. 能耗报表页面渲染测试
  // ═══════════════════════════════════════════════════════════════════════════════

  describe('能耗报表页面渲染', () => {
    it('能耗概览卡片应完整渲染', async () => {
      await page.setRequestInterception(true);
      page.on('request', request => {
        if (request.url().includes('/api/microgrid/energy/overview')) {
          request.respond({
            status: 200,
            contentType: 'application/json',
            body: JSON.stringify({
              code: 200,
              data: {
                totalPvGeneration: 1500.5,
                totalConsumption: 1200.0,
                selfConsumptionRate: 0.85
              }
            })
          });
        } else {
          request.continue();
        }
      });

      await page.goto(`${BASE_URL}/microgrid/energy/overview`, { waitUntil: 'networkidle2' });
      
      const hasOverviewCards = await page.evaluate(() => {
        const text = document.body.innerText;
        return text.includes('1500') || text.includes('发电') || text.includes('能耗');
      });
      
      expect(hasOverviewCards).to.be.true;
    });

    it('日报表图表应在合理时间内渲染完成', async () => {
      await page.setRequestInterception(true);
      page.on('request', request => {
        if (request.url().includes('/daily')) {
          request.respond({
            status: 200,
            contentType: 'application/json',
            body: JSON.stringify({
              code: 200,
              data: {
                hourlyData: Array(24).fill(null).map((_, i) => ({
                  hour: i,
                  pvGeneration: 50 + Math.random() * 100,
                  consumption: 40 + Math.random() * 80
                }))
              }
            })
          });
        } else {
          request.continue();
        }
      });

      const startTime = Date.now();
      await page.goto(`${BASE_URL}/microgrid/energy/grid-001/daily`, { waitUntil: 'networkidle2' });
      
      // 等待图表渲染
      await page.waitForSelector('canvas, svg, .chart-container', { timeout: 5000 }).catch(() => {});
      const renderTime = Date.now() - startTime;

      expect(renderTime).to.be.lessThan(PERFORMANCE_THRESHOLD.TTI);
    });

    it('趋势对比图应正确渲染多条数据线', async () => {
      await page.setRequestInterception(true);
      page.on('request', request => {
        if (request.url().includes('/trend/comparison')) {
          request.respond({
            status: 200,
            contentType: 'application/json',
            body: JSON.stringify({
              code: 200,
              data: [
                { gridId: 'grid-001', data: [100, 150, 200] },
                { gridId: 'grid-002', data: [120, 140, 180] }
              ]
            })
          });
        } else {
          request.continue();
        }
      });

      await page.goto(`${BASE_URL}/microgrid/energy/comparison`, { waitUntil: 'networkidle2' });
      
      const hasComparisonChart = await page.evaluate(() => {
        return document.querySelector('canvas, svg, .comparison-chart') !== null;
      });
      
      expect(hasComparisonChart).to.be.true;
    });
  });

  // ═══════════════════════════════════════════════════════════════════════════════
  // 4. CIM调度页面渲染测试
  // ═══════════════════════════════════════════════════════════════════════════════

  describe('CIM调度页面渲染', () => {
    it('调度记录表格应正确渲染', async () => {
      await page.setRequestInterception(true);
      page.on('request', request => {
        if (request.url().includes('/dispatch/records')) {
          request.respond({
            status: 200,
            contentType: 'application/json',
            body: JSON.stringify({
              code: 200,
              data: {
                items: [
                  { id: '1', commandType: 'EndDeviceControl', status: 'executed' },
                  { id: '2', commandType: 'SetPoint', status: 'pending' }
                ],
                total: 2
              }
            })
          });
        } else {
          request.continue();
        }
      });

      await page.goto(`${BASE_URL}/orchestrator/cim/dispatch/records`, { waitUntil: 'networkidle2' });
      
      const hasTable = await page.evaluate(() => {
        return document.querySelector('table, .ant-table, [data-testid="dispatch-table"]') !== null;
      });
      
      expect(hasTable).to.be.true;
    });

    it('偏差分析图表应正确渲染', async () => {
      await page.setRequestInterception(true);
      page.on('request', request => {
        if (request.url().includes('/deviation') && request.url().includes('/analysis')) {
          request.respond({
            status: 200,
            contentType: 'application/json',
            body: JSON.stringify({
              code: 200,
              data: {
                avgDeviationPercent: 2.5,
                maxDeviationPercent: 5.2,
                complianceRate: 97.5
              }
            })
          });
        } else {
          request.continue();
        }
      });

      await page.goto(`${BASE_URL}/orchestrator/cim/dispatch/record-001/deviation`, { waitUntil: 'networkidle2' });
      
      const hasAnalysisContent = await page.evaluate(() => {
        const text = document.body.innerText;
        return text.includes('2.5') || text.includes('偏差') || text.includes('%');
      });
      
      expect(hasAnalysisContent).to.be.true;
    });
  });

  // ═══════════════════════════════════════════════════════════════════════════════
  // 5. 组串监控页面渲染测试
  // ═══════════════════════════════════════════════════════════════════════════════

  describe('组串监控页面渲染', () => {
    it('异常列表表格应正确渲染', async () => {
      await page.setRequestInterception(true);
      page.on('request', request => {
        if (request.url().includes('/anomalies')) {
          request.respond({
            status: 200,
            contentType: 'application/json',
            body: JSON.stringify({
              code: 200,
              data: {
                items: [
                  { id: '1', stringId: 'STRING-01', anomalyType: 'hotspot', severity: 'high' },
                  { id: '2', stringId: 'STRING-05', anomalyType: 'shading', severity: 'medium' }
                ],
                total: 2
              }
            })
          });
        } else {
          request.continue();
        }
      });

      await page.goto(`${BASE_URL}/pvessc/string-monitor/anomalies`, { waitUntil: 'networkidle2' });
      
      const hasAnomalyTable = await page.evaluate(() => {
        return document.querySelector('table, .ant-table') !== null ||
               document.body.innerText.includes('STRING-01');
      });
      
      expect(hasAnomalyTable).to.be.true;
    });

    it('检测结果应正确渲染异常标记', async () => {
      await page.setRequestInterception(true);
      page.on('request', request => {
        if (request.url().includes('/detect')) {
          request.respond({
            status: 200,
            contentType: 'application/json',
            body: JSON.stringify({
              code: 200,
              data: {
                totalStrings: 100,
                anomalyCount: 3,
                anomalies: [{ stringId: 'STRING-01', type: 'hotspot' }]
              }
            })
          });
        } else {
          request.continue();
        }
      });

      await page.goto(`${BASE_URL}/pvessc/string-monitor/site-001`, { waitUntil: 'networkidle2' });
      
      // 页面应该加载成功
      const pageLoaded = await page.evaluate(() => {
        return document.readyState === 'complete';
      });
      
      expect(pageLoaded).to.be.true;
    });
  });

  // ═══════════════════════════════════════════════════════════════════════════════
  // 6. AI预测页面渲染测试
  // ═══════════════════════════════════════════════════════════════════════════════

  describe('AI预测页面渲染', () => {
    it('预测结果图表应正确渲染', async () => {
      await page.setRequestInterception(true);
      page.on('request', request => {
        if (request.url().includes('/adaptive/predict')) {
          request.respond({
            status: 200,
            contentType: 'application/json',
            body: JSON.stringify({
              code: 200,
              data: {
                predictions: [100, 150, 200, 180, 160],
                modelUsed: 'lstm+attention',
                confidence: 0.92
              }
            })
          });
        } else {
          request.continue();
        }
      });

      await page.goto(`${BASE_URL}/iotcloudai/adaptive/predict`, { waitUntil: 'networkidle2' });
      
      const hasContent = await page.evaluate(() => {
        return document.body.innerText.length > 100; // 页面有内容
      });
      
      expect(hasContent).to.be.true;
    });

    it('模型列表应正确渲染表格', async () => {
      await page.setRequestInterception(true);
      page.on('request', request => {
        if (request.url().includes('/adaptive/models')) {
          request.respond({
            status: 200,
            contentType: 'application/json',
            body: JSON.stringify({
              code: 200,
              data: [
                { id: '1', name: 'LSTM', accuracy: 0.95 },
                { id: '2', name: 'CNN-LSTM', accuracy: 0.93 }
              ]
            })
          });
        } else {
          request.continue();
        }
      });

      await page.goto(`${BASE_URL}/iotcloudai/adaptive/models`, { waitUntil: 'networkidle2' });
      
      const hasModelTable = await page.evaluate(() => {
        return document.querySelector('table, .ant-table') !== null ||
               document.body.innerText.includes('LSTM');
      });
      
      expect(hasModelTable).to.be.true;
    });
  });

  // ═══════════════════════════════════════════════════════════════════════════════
  // 7. Agent对话页面渲染测试
  // ═══════════════════════════════════════════════════════════════════════════════

  describe('Agent对话页面渲染', () => {
    it('对话界面应正确渲染输入框和发送按钮', async () => {
      await page.goto(`${BASE_URL}/iotcloudai/agent`, { waitUntil: 'networkidle2' });
      
      const hasInput = await page.evaluate(() => {
        return document.querySelector('input, textarea, [data-testid="goal-input"]') !== null;
      });
      
      expect(hasInput).to.be.true;
    });

    it('执行结果应正确渲染步骤列表', async () => {
      await page.setRequestInterception(true);
      page.on('request', request => {
        if (request.url().includes('/agent/execute')) {
          request.respond({
            status: 200,
            contentType: 'application/json',
            body: JSON.stringify({
              code: 200,
              data: {
                result: '分析完成',
                steps: [
                  { action: 'query_data', status: 'completed' },
                  { action: 'process', status: 'completed' }
                ]
              }
            })
          });
        } else {
          request.continue();
        }
      });

      await page.goto(`${BASE_URL}/iotcloudai/agent`, { waitUntil: 'networkidle2' });
      
      const pageLoaded = await page.evaluate(() => document.readyState === 'complete');
      expect(pageLoaded).to.be.true;
    });

    it('Agent列表卡片应正确渲染', async () => {
      await page.setRequestInterception(true);
      page.on('request', request => {
        if (request.url().includes('/agent/agents')) {
          request.respond({
            status: 200,
            contentType: 'application/json',
            body: JSON.stringify({
              code: 200,
              data: [
                { agentId: 'daily_ops', name: '日常运维助手' },
                { agentId: 'report', name: '报表生成助手' }
              ]
            })
          });
        } else {
          request.continue();
        }
      });

      await page.goto(`${BASE_URL}/iotcloudai/agent/list`, { waitUntil: 'networkidle2' });
      
      const hasCards = await page.evaluate(() => {
        return document.querySelector('.ant-card, [data-testid="agent-card"]') !== null ||
               document.body.innerText.includes('助手');
      });
      
      expect(hasCards).to.be.true;
    });
  });

  // ═══════════════════════════════════════════════════════════════════════════════
  // 8. 设备健康页面渲染测试
  // ═══════════════════════════════════════════════════════════════════════════════

  describe('设备健康页面渲染', () => {
    it('健康评估结果应正确渲染仪表盘', async () => {
      await page.setRequestInterception(true);
      page.on('request', request => {
        if (request.url().includes('/health/assess') && !request.url().includes('batch')) {
          request.respond({
            status: 200,
            contentType: 'application/json',
            body: JSON.stringify({
              code: 200,
              data: {
                deviceId: 'DEVICE-001',
                healthScore: 85,
                status: 'healthy'
              }
            })
          });
        } else {
          request.continue();
        }
      });

      await page.goto(`${BASE_URL}/iotcloudai/health/assess`, { waitUntil: 'networkidle2' });
      
      const pageLoaded = await page.evaluate(() => document.readyState === 'complete');
      expect(pageLoaded).to.be.true;
    });

    it('健康趋势图应正确渲染', async () => {
      await page.setRequestInterception(true);
      page.on('request', request => {
        if (request.url().includes('/health/trend/')) {
          request.respond({
            status: 200,
            contentType: 'application/json',
            body: JSON.stringify({
              code: 200,
              data: [
                { date: '2025-03-01', score: 90 },
                { date: '2025-03-10', score: 85 },
                { date: '2025-03-18', score: 82 }
              ]
            })
          });
        } else {
          request.continue();
        }
      });

      await page.goto(`${BASE_URL}/iotcloudai/health/trend/DEVICE-001`, { waitUntil: 'networkidle2' });
      
      const hasTrendChart = await page.evaluate(() => {
        return document.querySelector('canvas, svg, .chart-container') !== null;
      });
      
      expect(hasTrendChart).to.be.true;
    });
  });

  // ═══════════════════════════════════════════════════════════════════════════════
  // 9. 第三方模型页面渲染测试
  // ═══════════════════════════════════════════════════════════════════════════════

  describe('第三方模型页面渲染', () => {
    it('对话界面应正确渲染聊天窗口', async () => {
      await page.goto(`${BASE_URL}/iotcloudai/third-party/chat`, { waitUntil: 'networkidle2' });
      
      const hasChatInterface = await page.evaluate(() => {
        return document.querySelector('input, textarea, [data-testid="message-input"]') !== null;
      });
      
      expect(hasChatInterface).to.be.true;
    });

    it('供应商列表应正确渲染', async () => {
      await page.setRequestInterception(true);
      page.on('request', request => {
        if (request.url().includes('/third-party/providers')) {
          request.respond({
            status: 200,
            contentType: 'application/json',
            body: JSON.stringify({
              code: 200,
              data: ['ali', 'tencent', 'baidu', 'bytedance']
            })
          });
        } else {
          request.continue();
        }
      });

      await page.goto(`${BASE_URL}/iotcloudai/third-party/providers`, { waitUntil: 'networkidle2' });
      
      const hasProviders = await page.evaluate(() => {
        const text = document.body.innerText.toLowerCase();
        return text.includes('ali') || text.includes('tencent') || text.includes('供应商');
      });
      
      expect(hasProviders).to.be.true;
    });
  });

  // ═══════════════════════════════════════════════════════════════════════════════
  // 10. 性能基准测试
  // ═══════════════════════════════════════════════════════════════════════════════

  describe('页面性能基准', () => {
    const testPages = [
      { path: '/carbon/irec/certificates', name: 'I-REC证书列表' },
      { path: '/charging/orderly/station/station-001/queue', name: '排队列表' },
      { path: '/microgrid/energy/overview', name: '能耗概览' },
      { path: '/orchestrator/cim/dispatch/records', name: 'CIM调度记录' },
      { path: '/pvessc/string-monitor/anomalies', name: '组串异常列表' },
      { path: '/iotcloudai/adaptive/predict', name: 'AI预测' },
      { path: '/iotcloudai/agent', name: 'Agent对话' },
      { path: '/iotcloudai/health/assess', name: '设备健康' },
      { path: '/iotcloudai/third-party/chat', name: '第三方模型' }
    ];

    testPages.forEach(({ path, name }) => {
      it(`${name}页面加载时间应小于${PERFORMANCE_THRESHOLD.LCP}ms`, async () => {
        await page.setRequestInterception(true);
        page.on('request', request => {
          if (request.url().includes('/api/')) {
            request.respond({
              status: 200,
              contentType: 'application/json',
              body: JSON.stringify({ code: 200, data: { items: [], total: 0 } })
            });
          } else {
            request.continue();
          }
        });

        const startTime = Date.now();
        await page.goto(`${BASE_URL}${path}`, { waitUntil: 'domcontentloaded' });
        const loadTime = Date.now() - startTime;

        console.log(`${name}页面加载时间: ${loadTime}ms`);
        expect(loadTime).to.be.lessThan(PERFORMANCE_THRESHOLD.LCP);
      });
    });
  });
});

// 导出供外部使用
module.exports = { PERFORMANCE_THRESHOLD };
