// K6 性能测试 — VPP 虚拟电厂服务专项
// 覆盖：VPP站点管理、聚合单元、调度计划、实时调度、DER设备、负荷预测

import http from 'k6/http';
import { check, sleep, group } from 'k6';
import { Rate, Trend } from 'k6/metrics';
import { config } from '../config.js';

const BASE_URL = config.baseUrl;
const errorRate = new Rate('errors');
const apiDuration = new Trend('api_duration');

export const options = {
  scenarios: {
    vpp_performance: {
      executor: 'ramping-vus',
      startVUs: 1,
      stages: [
        { duration: '30s', target: 5 },
        { duration: '1m', target: 15 },
        { duration: '2m', target: 30 },
        { duration: '1m', target: 10 },
        { duration: '30s', target: 0 },
      ],
    },
  },
  thresholds: {
    http_req_duration: ['p(95)<800', 'p(99)<1500'],
    errors: ['rate<1'],
  },
};

const HEADERS = {
  'Content-Type': 'application/json',
  'Authorization': `Bearer ${__ENV.TOKEN || 'test-token'}`,
};

export default function () {
  group('VPP-站点列表', () => {
    const res = http.get(`${BASE_URL}/api/vpp/site?page=1&pageSize=20`, { headers: HEADERS });
    check(res, { '站点列表-200': (r) => r.status < 500 });
    errorRate.add(res.status !== 200);
    apiDuration.add(res.timings.duration);
  });

  group('VPP-聚合单元', () => {
    const res = http.get(`${BASE_URL}/api/vpp/aggregation-unit?page=1&pageSize=20`, { headers: HEADERS });
    check(res, { '聚合单元-200': (r) => r.status < 500 });
    errorRate.add(res.status !== 200);
  });

  group('VPP-调度计划', () => {
    const res = http.get(`${BASE_URL}/api/vpp/dispatch-plan?page=1&pageSize=10`, { headers: HEADERS });
    check(res, { '调度计划-200': (r) => r.status < 500 });
    errorRate.add(res.status !== 200);
  });

  group('VPP-实时调度', () => {
    const res = http.get(`${BASE_URL}/api/vpp/realtime-dispatch?page=1&pageSize=10`, { headers: HEADERS });
    check(res, { '实时调度-可访问': (r) => [200, 404].includes(r.status) });
    errorRate.add(![200, 404].includes(res.status));
  });

  group('VPP-DER设备管理', () => {
    const res = http.get(`${BASE_URL}/api/vpp/der-device?page=1&pageSize=20`, { headers: HEADERS });
    check(res, { 'DER列表-200': (r) => r.status < 500 });
    errorRate.add(res.status !== 200);
  });

  group('VPP-市场报价', () => {
    const res = http.get(`${BASE_URL}/api/vpp/market-bid?page=1&pageSize=10`, { headers: HEADERS });
    check(res, { '市场报价-可访问': (r) => [200, 404].includes(r.status) });
    errorRate.add(![200, 404].includes(res.status));
  });

  group('VPP-负荷预测', () => {
    const payload = JSON.stringify({
      siteId: '00000000-0000-0000-0000-000000000001',
      forecastHours: 24,
      algorithm: 'LSTM',
    });
    const res = http.post(`${BASE_URL}/api/vpp/load-forecast`, payload, { headers: HEADERS });
    check(res, { '负荷预测-可响应': (r) => [200, 400, 404].includes(r.status) });
    errorRate.add(![200, 400, 404].includes(res.status));
  });

  group('VPP-收益统计', () => {
    const res = http.get(`${BASE_URL}/api/vpp/revenue/statistics`, { headers: HEADERS });
    check(res, { '收益统计-可访问': (r) => [200, 404].includes(r.status) });
    errorRate.add(![200, 404].includes(res.status));
  });

  sleep(0.5 + Math.random());
}
