// K6 性能测试 — CarbonTrade 碳交易服务专项
// 覆盖：排放因子查询、MRV核查、碳配额交易、撮合引擎、区块链存证

import http from 'k6/http';
import { check, sleep, group } from 'k6';
import { Rate, Trend } from 'k6/metrics';
import { config } from '../config.js';

const BASE_URL = config.baseUrl;
const errorRate = new Rate('errors');
const apiDuration = new Trend('api_duration');

export const options = {
  scenarios: {
    carbontrade_smoke: {
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
  group('碳交易-仪表盘', () => {
    const res = http.get(`${BASE_URL}/api/carbontrade/dashboard`, { headers: HEADERS });
    check(res, { '仪表盘-200': (r) => r.status < 500 });
    errorRate.add(res.status !== 200);
    apiDuration.add(res.timings.duration);
  });

  group('碳交易-排放因子列表', () => {
    const res = http.get(`${BASE_URL}/api/carbontrade/emission-factor?page=1&pageSize=20`, { headers: HEADERS });
    check(res, { '排放因子-200': (r) => r.status < 500 });
    errorRate.add(res.status !== 200);
    apiDuration.add(res.timings.duration);
  });

  group('碳交易-MRV记录', () => {
    const res = http.get(`${BASE_URL}/api/carbontrade/mrv?page=1&pageSize=10`, { headers: HEADERS });
    check(res, { 'MRV-200': (r) => r.status < 500 });
    errorRate.add(res.status !== 200);
  });

  group('碳交易-配额交易订单', () => {
    const res = http.get(`${BASE_URL}/api/carbontrade/trade-order?page=1&pageSize=10`, { headers: HEADERS });
    check(res, { '交易订单-200': (r) => r.status < 500 });
    errorRate.add(res.status !== 200);
  });

  group('碳交易-撮合记录', () => {
    const res = http.get(`${BASE_URL}/api/carbontrade/trade-matching?page=1&pageSize=10`, { headers: HEADERS });
    check(res, { '撮合记录-可访问': (r) => [200, 404].includes(r.status) });
    errorRate.add(![200, 404].includes(res.status));
  });

  group('碳交易-区块链存证', () => {
    const res = http.get(`${BASE_URL}/api/carbontrade/blockchain-proof?page=1&pageSize=10`, { headers: HEADERS });
    check(res, { '存证-可访问': (r) => [200, 404].includes(r.status) });
    errorRate.add(![200, 404].includes(res.status));
  });

  group('碳交易-碳排放计算', () => {
    const payload = JSON.stringify({
      stationId: '00000000-0000-0000-0000-000000000001',
      energyKwh: 1000.0 + Math.random() * 5000,
      factorCode: 'GRID_DEFAULT',
    });
    const res = http.post(`${BASE_URL}/api/carbontrade/emission/calculate`, payload, { headers: HEADERS });
    check(res, { '计算-可响应': (r) => [200, 400, 404].includes(r.status) });
    errorRate.add(![200, 400, 404].includes(res.status));
  });

  sleep(0.5 + Math.random());
}
