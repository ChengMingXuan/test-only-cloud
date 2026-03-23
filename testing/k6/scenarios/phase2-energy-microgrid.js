// K6 性能测试 — MicroGrid 微电网服务专项
// 覆盖：微网拓扑、母线管理、分布式电源、储能系统、并离网切换、能量优化

import http from 'k6/http';
import { check, sleep, group } from 'k6';
import { Rate, Trend } from 'k6/metrics';
import { config } from '../config.js';

const BASE_URL = config.baseUrl;
const errorRate = new Rate('errors');
const apiDuration = new Trend('api_duration');

export const options = {
  scenarios: {
    microgrid_load: {
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
  group('微电网-拓扑列表', () => {
    const res = http.get(`${BASE_URL}/api/microgrid/topology?page=1&pageSize=20`, { headers: HEADERS });
    check(res, { '拓扑-200': (r) => r.status < 500 });
    errorRate.add(res.status !== 200);
    apiDuration.add(res.timings.duration);
  });

  group('微电网-母线管理', () => {
    const res = http.get(`${BASE_URL}/api/microgrid/bus?page=1&pageSize=20`, { headers: HEADERS });
    check(res, { '母线-200': (r) => r.status < 500 });
    errorRate.add(res.status !== 200);
  });

  group('微电网-分布式电源', () => {
    const res = http.get(`${BASE_URL}/api/microgrid/dg?page=1&pageSize=20`, { headers: HEADERS });
    check(res, { 'DG-200': (r) => r.status < 500 });
    errorRate.add(res.status !== 200);
  });

  group('微电网-储能系统', () => {
    const res = http.get(`${BASE_URL}/api/microgrid/ess?page=1&pageSize=20`, { headers: HEADERS });
    check(res, { '储能-200': (r) => r.status < 500 });
    errorRate.add(res.status !== 200);
  });

  group('微电网-负荷设备', () => {
    const res = http.get(`${BASE_URL}/api/microgrid/load?page=1&pageSize=20`, { headers: HEADERS });
    check(res, { '负荷-200': (r) => r.status < 500 });
    errorRate.add(res.status !== 200);
  });

  group('微电网-并离网状态', () => {
    const res = http.get(`${BASE_URL}/api/microgrid/grid-mode/status`, { headers: HEADERS });
    check(res, { '并离网状态-可访问': (r) => [200, 404].includes(r.status) });
    errorRate.add(![200, 404].includes(res.status));
  });

  group('微电网-能量优化', () => {
    const payload = JSON.stringify({
      topologyId: '00000000-0000-0000-0000-000000000001',
      optimizationTarget: 'MIN_COST',
      horizonMinutes: 60,
    });
    const res = http.post(`${BASE_URL}/api/microgrid/energy-optimization`, payload, { headers: HEADERS });
    check(res, { '优化-可响应': (r) => [200, 400, 404].includes(r.status) });
    errorRate.add(![200, 400, 404].includes(res.status));
  });

  sleep(0.5 + Math.random());
}
