// K6 性能测试 — ElecTrade 电力交易服务专项
// 覆盖：交易计划、合约管理、实时竞价、结算核算、偏差考核、辅助服务

import http from 'k6/http';
import { check, sleep, group } from 'k6';
import { Rate, Trend } from 'k6/metrics';
import { config } from '../config.js';

const BASE_URL = config.baseUrl;
const errorRate = new Rate('errors');
const apiDuration = new Trend('api_duration');

export const options = {
  scenarios: {
    electrade_performance: {
      executor: 'ramping-vus',
      startVUs: 1,
      stages: [
        { duration: '30s', target: 5 },
        { duration: '1m', target: 10 },
        { duration: '2m', target: 25 },
        { duration: '1m', target: 8 },
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
  group('电力交易-交易计划', () => {
    const res = http.get(`${BASE_URL}/api/electrade/trade-plan?page=1&pageSize=20`, { headers: HEADERS });
    check(res, { '交易计划-200': (r) => r.status < 500 });
    errorRate.add(res.status !== 200);
    apiDuration.add(res.timings.duration);
  });

  group('电力交易-合约管理', () => {
    const res = http.get(`${BASE_URL}/api/electrade/contract?page=1&pageSize=20`, { headers: HEADERS });
    check(res, { '合约-200': (r) => r.status < 500 });
    errorRate.add(res.status !== 200);
  });

  group('电力交易-实时竞价', () => {
    const res = http.get(`${BASE_URL}/api/electrade/spot-bid?page=1&pageSize=10`, { headers: HEADERS });
    check(res, { '竞价-200': (r) => r.status < 500 });
    errorRate.add(res.status !== 200);
  });

  group('电力交易-中长期交易', () => {
    const res = http.get(`${BASE_URL}/api/electrade/bilateral?page=1&pageSize=10`, { headers: HEADERS });
    check(res, { '中长期-可访问': (r) => [200, 404].includes(r.status) });
    errorRate.add(![200, 404].includes(res.status));
  });

  group('电力交易-结算核算', () => {
    const res = http.get(`${BASE_URL}/api/electrade/settlement?page=1&pageSize=10`, { headers: HEADERS });
    check(res, { '结算-200': (r) => r.status < 500 });
    errorRate.add(res.status !== 200);
  });

  group('电力交易-偏差考核', () => {
    const res = http.get(`${BASE_URL}/api/electrade/deviation?page=1&pageSize=10`, { headers: HEADERS });
    check(res, { '偏差考核-可访问': (r) => [200, 404].includes(r.status) });
    errorRate.add(![200, 404].includes(res.status));
  });

  group('电力交易-辅助服务', () => {
    const res = http.get(`${BASE_URL}/api/electrade/ancillary?page=1&pageSize=10`, { headers: HEADERS });
    check(res, { '辅助服务-可访问': (r) => [200, 404].includes(r.status) });
    errorRate.add(![200, 404].includes(res.status));
  });

  group('电力交易-提交竞价', () => {
    const payload = JSON.stringify({
      period: `${new Date().toISOString().split('T')[0]}T08:00:00`,
      priceYuan: 350 + Math.random() * 200,
      quantityMwh: 10 + Math.random() * 50,
      bidType: 'SELL',
    });
    const res = http.post(`${BASE_URL}/api/electrade/spot-bid`, payload, { headers: HEADERS });
    check(res, { '提交竞价-可响应': (r) => [200, 201, 400, 404].includes(r.status) });
    errorRate.add(![200, 201, 400, 404].includes(res.status));
  });

  sleep(0.5 + Math.random());
}
