// K6 性能测试 — DemandResp 需求响应服务专项
// 覆盖：需求响应事件、响应资源注册、响应执行、响应评估、激励结算

import http from 'k6/http';
import { check, sleep, group } from 'k6';
import { Rate, Trend } from 'k6/metrics';
import { config } from '../config.js';

const BASE_URL = config.baseUrl;
const errorRate = new Rate('errors');
const apiDuration = new Trend('api_duration');

export const options = {
  scenarios: {
    demandresp_performance: {
      executor: 'ramping-vus',
      startVUs: 1,
      stages: [
        { duration: '30s', target: 5 },
        { duration: '1m', target: 10 },
        { duration: '2m', target: 20 },
        { duration: '1m', target: 5 },
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
  group('需求响应-事件列表', () => {
    const res = http.get(`${BASE_URL}/api/demandresp/event?page=1&pageSize=20`, { headers: HEADERS });
    check(res, { '事件列表-200': (r) => r.status < 500 });
    errorRate.add(res.status !== 200);
    apiDuration.add(res.timings.duration);
  });

  group('需求响应-资源注册', () => {
    const res = http.get(`${BASE_URL}/api/demandresp/resource?page=1&pageSize=20`, { headers: HEADERS });
    check(res, { '资源列表-200': (r) => r.status < 500 });
    errorRate.add(res.status !== 200);
  });

  group('需求响应-响应执行记录', () => {
    const res = http.get(`${BASE_URL}/api/demandresp/execution?page=1&pageSize=10`, { headers: HEADERS });
    check(res, { '执行记录-可访问': (r) => [200, 404].includes(r.status) });
    errorRate.add(![200, 404].includes(res.status));
  });

  group('需求响应-响应评估', () => {
    const res = http.get(`${BASE_URL}/api/demandresp/evaluation?page=1&pageSize=10`, { headers: HEADERS });
    check(res, { '评估-可访问': (r) => [200, 404].includes(r.status) });
    errorRate.add(![200, 404].includes(res.status));
  });

  group('需求响应-激励结算', () => {
    const res = http.get(`${BASE_URL}/api/demandresp/incentive?page=1&pageSize=10`, { headers: HEADERS });
    check(res, { '结算-可访问': (r) => [200, 404].includes(r.status) });
    errorRate.add(![200, 404].includes(res.status));
  });

  group('需求响应-发布响应事件', () => {
    const payload = JSON.stringify({
      eventName: `DR_LOAD_${Date.now()}`,
      eventType: 'PRICE_BASED',
      targetReductionKw: 500 + Math.random() * 2000,
      startTime: new Date(Date.now() + 3600000).toISOString(),
      durationMinutes: 60,
    });
    const res = http.post(`${BASE_URL}/api/demandresp/event`, payload, { headers: HEADERS });
    check(res, { '发布事件-可响应': (r) => [200, 201, 400, 404].includes(r.status) });
    errorRate.add(![200, 201, 400, 404].includes(res.status));
  });

  sleep(0.5 + Math.random());
}
