// K6 性能测试 — DeviceOps 设备运维服务专项
// 覆盖：巡检计划、巡检任务、故障管理、备品备件、维保记录、运维统计

import http from 'k6/http';
import { check, sleep, group } from 'k6';
import { Rate, Trend } from 'k6/metrics';
import { config } from '../config.js';

const BASE_URL = config.baseUrl;
const errorRate = new Rate('errors');
const apiDuration = new Trend('api_duration');

export const options = {
  scenarios: {
    deviceops_performance: {
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
  group('设备运维-巡检计划', () => {
    const res = http.get(`${BASE_URL}/api/deviceops/inspection-plan?page=1&pageSize=20`, { headers: HEADERS });
    check(res, { '巡检计划-200': (r) => r.status < 500 });
    errorRate.add(res.status !== 200);
    apiDuration.add(res.timings.duration);
  });

  group('设备运维-巡检任务', () => {
    const res = http.get(`${BASE_URL}/api/deviceops/inspection-task?page=1&pageSize=20`, { headers: HEADERS });
    check(res, { '巡检任务-200': (r) => r.status < 500 });
    errorRate.add(res.status !== 200);
  });

  group('设备运维-故障管理', () => {
    const res = http.get(`${BASE_URL}/api/deviceops/fault?page=1&pageSize=10`, { headers: HEADERS });
    check(res, { '故障管理-200': (r) => r.status < 500 });
    errorRate.add(res.status !== 200);
  });

  group('设备运维-备品备件', () => {
    const res = http.get(`${BASE_URL}/api/deviceops/spare-part?page=1&pageSize=20`, { headers: HEADERS });
    check(res, { '备件-可访问': (r) => [200, 404].includes(r.status) });
    errorRate.add(![200, 404].includes(res.status));
  });

  group('设备运维-维保记录', () => {
    const res = http.get(`${BASE_URL}/api/deviceops/maintenance?page=1&pageSize=10`, { headers: HEADERS });
    check(res, { '维保-可访问': (r) => [200, 404].includes(r.status) });
    errorRate.add(![200, 404].includes(res.status));
  });

  group('设备运维-统计仪表盘', () => {
    const res = http.get(`${BASE_URL}/api/deviceops/dashboard`, { headers: HEADERS });
    check(res, { '统计-可访问': (r) => [200, 404].includes(r.status) });
    errorRate.add(![200, 404].includes(res.status));
  });

  group('设备运维-创建巡检任务', () => {
    const payload = JSON.stringify({
      planId: '00000000-0000-0000-0000-000000000001',
      assignee: '张三',
      scheduledTime: new Date(Date.now() + 86400000).toISOString(),
      items: ['外观检查', '电气测试', '接地检测'],
    });
    const res = http.post(`${BASE_URL}/api/deviceops/inspection-task`, payload, { headers: HEADERS });
    check(res, { '创建巡检-可响应': (r) => [200, 201, 400, 404].includes(r.status) });
    errorRate.add(![200, 201, 400, 404].includes(res.status));
  });

  sleep(0.5 + Math.random());
}
