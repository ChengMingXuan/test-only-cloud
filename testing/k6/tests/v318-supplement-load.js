/**
 * v3.18 增量补充 - 移动端认证/备品备件/导出 k6 性能测试
 * =====================================================
 * 补充 v318-incremental-load.js 未覆盖的 3 个模块
 */

import http from 'k6/http';
import { check, sleep, group } from 'k6';
import { Rate, Trend, Counter } from 'k6/metrics';

// 自定义指标
const errorRate = new Rate('errors');
const mobileAuthTrend = new Trend('mobile_auth_duration');
const sparePartTrend = new Trend('spare_part_duration');
const exportTrend = new Trend('export_duration');
const apiCallCounter = new Counter('api_calls');

// 测试配置
export const options = {
  scenarios: {
    smoke_test: {
      executor: 'constant-vus',
      vus: 1,
      duration: '30s',
      tags: { type: 'smoke' },
    },
    load_test: {
      executor: 'ramping-vus',
      startVUs: 0,
      stages: [
        { duration: '30s', target: 10 },
        { duration: '1m', target: 10 },
        { duration: '30s', target: 0 },
      ],
      tags: { type: 'load' },
      startTime: '35s',
    },
  },
  thresholds: {
    'mobile_auth_duration': ['p(95)<500', 'p(99)<1000'],
    'spare_part_duration': ['p(95)<300', 'p(99)<800'],
    'export_duration': ['p(95)<5000', 'p(99)<10000'],
    'errors': ['rate<0.1'],
  },
};

// API 基础路径
const BASE_URL = __ENV.BASE_URL || 'http://localhost:5000';
const headers = {
  'Content-Type': 'application/json',
  'Authorization': `Bearer ${__ENV.API_TOKEN || 'test-token'}`,
};

function randomUUID() {
  return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
    const r = Math.random() * 16 | 0;
    const v = c === 'x' ? r : (r & 0x3 | 0x8);
    return v.toString(16);
  });
}

// ═══════════════════════════════════════════════════════════════════════════════
// 移动端认证 API 性能测试
// ═══════════════════════════════════════════════════════════════════════════════

function testMobileAuth() {
  group('移动端认证 API', () => {
    // 发送验证码
    let res = http.post(`${BASE_URL}/api/auth/mobile/send-code`,
      JSON.stringify({ phone: '13812345678' }),
      { headers, tags: { endpoint: 'send_code' } }
    );
    mobileAuthTrend.add(res.timings.duration);
    apiCallCounter.add(1);
    check(res, { '发送验证码 status 200/429': (r) => r.status === 200 || r.status === 429 });
    errorRate.add(res.status >= 500);

    // 短信登录
    res = http.post(`${BASE_URL}/api/auth/mobile/sms-login`,
      JSON.stringify({ phone: '13812345678', verifyCode: '123456' }),
      { headers, tags: { endpoint: 'sms_login' } }
    );
    mobileAuthTrend.add(res.timings.duration);
    apiCallCounter.add(1);
    check(res, { '短信登录 status < 500': (r) => r.status < 500 });
    errorRate.add(res.status >= 500);

    // 密码登录
    res = http.post(`${BASE_URL}/api/auth/mobile/password-login`,
      JSON.stringify({ phone: '13812345678', password: 'Test@123456' }),
      { headers, tags: { endpoint: 'password_login' } }
    );
    mobileAuthTrend.add(res.timings.duration);
    apiCallCounter.add(1);
    check(res, { '密码登录 status < 500': (r) => r.status < 500 });
    errorRate.add(res.status >= 500);

    // 获取个人信息
    res = http.get(`${BASE_URL}/api/auth/mobile/profile`, { headers, tags: { endpoint: 'get_profile' } });
    mobileAuthTrend.add(res.timings.duration);
    apiCallCounter.add(1);
    check(res, { '个人信息 status < 500': (r) => r.status < 500 });
    errorRate.add(res.status >= 500);

    sleep(0.5);
  });
}

// ═══════════════════════════════════════════════════════════════════════════════
// 备品备件 API 性能测试
// ═══════════════════════════════════════════════════════════════════════════════

function testSparePart() {
  group('备品备件 API', () => {
    // 备件列表
    let res = http.get(`${BASE_URL}/api/spare-part?page=1&pageSize=20`, { headers, tags: { endpoint: 'list_parts' } });
    sparePartTrend.add(res.timings.duration);
    apiCallCounter.add(1);
    check(res, { '备件列表 status < 500': (r) => r.status < 500 });
    errorRate.add(res.status >= 500);

    // 创建备件
    res = http.post(`${BASE_URL}/api/spare-part`,
      JSON.stringify({
        partCode: `SP_${Date.now()}`,
        partName: `压力测试备件_${Date.now()}`,
        category: 'inverter',
        specification: '50kW',
        unit: '个',
        safetyStock: 10,
        warehouseId: randomUUID(),
      }),
      { headers, tags: { endpoint: 'create_part' } }
    );
    sparePartTrend.add(res.timings.duration);
    apiCallCounter.add(1);
    check(res, { '创建备件 status < 500': (r) => r.status < 500 });
    errorRate.add(res.status >= 500);

    // 入库
    res = http.post(`${BASE_URL}/api/spare-part/stock-in`,
      JSON.stringify({
        partId: randomUUID(),
        quantity: 10,
        supplierId: randomUUID(),
        unitPrice: 15000.0,
        batchNo: `BATCH_${Date.now()}`,
      }),
      { headers, tags: { endpoint: 'stock_in' } }
    );
    sparePartTrend.add(res.timings.duration);
    apiCallCounter.add(1);
    check(res, { '入库 status < 500': (r) => r.status < 500 });
    errorRate.add(res.status >= 500);

    // 出库
    res = http.post(`${BASE_URL}/api/spare-part/stock-out`,
      JSON.stringify({
        partId: randomUUID(),
        quantity: 2,
        workOrderId: randomUUID(),
        recipientName: '张工',
        purpose: '维修更换',
      }),
      { headers, tags: { endpoint: 'stock_out' } }
    );
    sparePartTrend.add(res.timings.duration);
    apiCallCounter.add(1);
    check(res, { '出库 status < 500': (r) => r.status < 500 });
    errorRate.add(res.status >= 500);

    // 库存查询
    res = http.get(`${BASE_URL}/api/spare-part/inventory?page=1&pageSize=20`, { headers, tags: { endpoint: 'inventory' } });
    sparePartTrend.add(res.timings.duration);
    apiCallCounter.add(1);
    check(res, { '库存查询 status < 500': (r) => r.status < 500 });
    errorRate.add(res.status >= 500);

    // 低库存告警
    res = http.get(`${BASE_URL}/api/spare-part/inventory/low-stock`, { headers, tags: { endpoint: 'low_stock' } });
    sparePartTrend.add(res.timings.duration);
    apiCallCounter.add(1);
    check(res, { '低库存告警 status < 500': (r) => r.status < 500 });
    errorRate.add(res.status >= 500);

    sleep(0.5);
  });
}

// ═══════════════════════════════════════════════════════════════════════════════
// 导出服务 API 性能测试
// ═══════════════════════════════════════════════════════════════════════════════

function testExport() {
  group('导出服务 API', () => {
    // Excel 导出
    let res = http.post(`${BASE_URL}/api/export/excel/generate`,
      JSON.stringify({
        dataSource: 'charging_orders',
        filters: { startDate: '2025-01-01', endDate: '2025-06-30' },
        columns: ['orderId', 'stationName', 'amount'],
        fileName: 'k6测试导出',
      }),
      { headers, tags: { endpoint: 'excel_generate' } }
    );
    exportTrend.add(res.timings.duration);
    apiCallCounter.add(1);
    check(res, { 'Excel导出 status < 500': (r) => r.status < 500 });
    errorRate.add(res.status >= 500);

    // PDF 导出
    res = http.post(`${BASE_URL}/api/export/pdf/generate`,
      JSON.stringify({
        templateId: randomUUID(),
        reportType: 'monthly_summary',
        parameters: { month: '2025-06', stationId: randomUUID() },
      }),
      { headers, tags: { endpoint: 'pdf_generate' } }
    );
    exportTrend.add(res.timings.duration);
    apiCallCounter.add(1);
    check(res, { 'PDF导出 status < 500': (r) => r.status < 500 });
    errorRate.add(res.status >= 500);

    // 模板列表
    res = http.get(`${BASE_URL}/api/export/excel/templates`, { headers, tags: { endpoint: 'excel_templates' } });
    exportTrend.add(res.timings.duration);
    apiCallCounter.add(1);
    check(res, { 'Excel模板列表 status < 500': (r) => r.status < 500 });
    errorRate.add(res.status >= 500);

    res = http.get(`${BASE_URL}/api/export/pdf/templates`, { headers, tags: { endpoint: 'pdf_templates' } });
    exportTrend.add(res.timings.duration);
    apiCallCounter.add(1);
    check(res, { 'PDF模板列表 status < 500': (r) => r.status < 500 });
    errorRate.add(res.status >= 500);

    sleep(0.5);
  });
}

// ═══════════════════════════════════════════════════════════════════════════════
// 主测试函数
// ═══════════════════════════════════════════════════════════════════════════════

export default function () {
  testMobileAuth();
  testSparePart();
  testExport();

  sleep(1);
}

export function setup() {
  console.log('=== v3.18 补充模块性能测试开始 ===');
  console.log(`目标: ${BASE_URL}`);
  return { startTime: new Date().toISOString() };
}

export function teardown(data) {
  console.log('=== v3.18 补充模块性能测试结束 ===');
  console.log(`开始时间: ${data.startTime}`);
  console.log(`结束时间: ${new Date().toISOString()}`);
}
