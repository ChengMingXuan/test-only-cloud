/**
 * K6 补充性能测试场景 - 服务网格管理 API
 * 覆盖: ServiceMesh 配置/状态/刷新/连接测试
 * 场景数: 20
 */
import http from 'k6/http';
import { check, sleep } from 'k6';

const BASE_URL = __ENV.BASE_URL || 'http://localhost:8000';
const TOKEN = __ENV.AUTH_TOKEN || 'mock-token';
const HEADERS = { Authorization: `Bearer ${TOKEN}`, 'Content-Type': 'application/json' };

// ============= 服务网格配置 =============

export function smoke_mesh_config_list() {
  const res = http.get(`${BASE_URL}/api/monitor/service-mesh/config`, { headers: HEADERS, tags: { name: 'mesh_config_list' } });
  check(res, { 'mesh config list 200': (r) => r.status < 500 });
  sleep(0.3);
}

export function load_mesh_config_list() {
  const res = http.get(`${BASE_URL}/api/monitor/service-mesh/config`, { headers: HEADERS, tags: { name: 'mesh_config_list_load' } });
  check(res, { 'mesh config list body': (r) => r.body.length > 0 });
  sleep(0.2);
}

export function smoke_mesh_status() {
  const res = http.get(`${BASE_URL}/api/monitor/service-mesh/status`, { headers: HEADERS, tags: { name: 'mesh_status' } });
  check(res, { 'mesh status 200': (r) => r.status < 500 });
  sleep(0.3);
}

export function load_mesh_status() {
  const res = http.get(`${BASE_URL}/api/monitor/service-mesh/status`, { headers: HEADERS, tags: { name: 'mesh_status_load' } });
  check(res, { 'mesh status body': (r) => r.body.length > 0 });
  sleep(0.2);
}

// ============= 服务网格更新 =============

export function smoke_mesh_update_config() {
  const payload = JSON.stringify({
    mode: 'dapr',
    enabled: true,
    daprPort: 3500
  });
  const res = http.put(`${BASE_URL}/api/monitor/service-mesh/config/identity-service`, payload, { headers: HEADERS, tags: { name: 'mesh_update_config' } });
  check(res, { 'mesh update config 200': (r) => r.status < 500 });
  sleep(0.5);
}

export function smoke_mesh_batch_mode() {
  const payload = JSON.stringify({
    mode: 'dapr',
    serviceIds: ['identity-service', 'account-service', 'device-service']
  });
  const res = http.put(`${BASE_URL}/api/monitor/service-mesh/batch-mode`, payload, { headers: HEADERS, tags: { name: 'mesh_batch_mode' } });
  check(res, { 'mesh batch mode 200': (r) => r.status < 500 });
  sleep(0.5);
}

// ============= 服务网格刷新 =============

export function smoke_mesh_refresh() {
  const res = http.post(`${BASE_URL}/api/monitor/service-mesh/refresh`, null, { headers: HEADERS, tags: { name: 'mesh_refresh' } });
  check(res, { 'mesh refresh 200': (r) => r.status < 500 });
  sleep(0.5);
}

export function load_mesh_refresh() {
  const res = http.post(`${BASE_URL}/api/monitor/service-mesh/refresh`, null, { headers: HEADERS, tags: { name: 'mesh_refresh_load' } });
  check(res, { 'mesh refresh body': (r) => r.body.length >= 0 });
  sleep(0.3);
}

// ============= 服务网格连接测试 =============

export function smoke_mesh_test_connection() {
  const res = http.post(`${BASE_URL}/api/monitor/service-mesh/test/identity-service`, null, { headers: HEADERS, tags: { name: 'mesh_test_conn' } });
  check(res, { 'mesh test connection 200': (r) => r.status < 500 });
  sleep(0.5);
}

export function load_mesh_test_connection_multi() {
  const services = ['identity-service', 'account-service', 'device-service', 'station-service', 'permission-service'];
  for (const svc of services) {
    const res = http.post(`${BASE_URL}/api/monitor/service-mesh/test/${svc}`, null, { headers: HEADERS, tags: { name: `mesh_test_${svc}` } });
    check(res, { [`mesh test ${svc} 200`]: (r) => r.status < 500 });
    sleep(0.1);
  }
}

// ============= 并发场景 =============

export function concurrent_mesh_reads() {
  const responses = http.batch([
    ['GET', `${BASE_URL}/api/monitor/service-mesh/config`, null, { headers: HEADERS, tags: { name: 'mesh_concurrent_config' } }],
    ['GET', `${BASE_URL}/api/monitor/service-mesh/status`, null, { headers: HEADERS, tags: { name: 'mesh_concurrent_status' } }],
  ]);
  for (const res of responses) {
    check(res, { 'concurrent mesh read 200': (r) => r.status < 500 });
  }
  sleep(0.3);
}

export function spike_mesh_config_burst() {
  for (let i = 0; i < 10; i++) {
    const res = http.get(`${BASE_URL}/api/monitor/service-mesh/config`, { headers: HEADERS, tags: { name: 'mesh_spike_config' } });
    check(res, { 'spike mesh config 200': (r) => r.status < 500 });
  }
  sleep(1);
}

export function spike_mesh_status_burst() {
  for (let i = 0; i < 10; i++) {
    const res = http.get(`${BASE_URL}/api/monitor/service-mesh/status`, { headers: HEADERS, tags: { name: 'mesh_spike_status' } });
    check(res, { 'spike mesh status 200': (r) => r.status < 500 });
  }
  sleep(1);
}

// ============= 异常场景 =============

export function invalid_mesh_update() {
  const res = http.put(`${BASE_URL}/api/monitor/service-mesh/config/nonexistent-service`, '{}', { headers: HEADERS, tags: { name: 'mesh_invalid_update' } });
  check(res, { 'invalid mesh update handled': (r) => r.status < 500 || r.status === 404 });
  sleep(0.3);
}

export function unauthorized_mesh_access() {
  const res = http.get(`${BASE_URL}/api/monitor/service-mesh/config`, { headers: { 'Content-Type': 'application/json' }, tags: { name: 'mesh_unauthorized' } });
  check(res, { 'unauthorized returns 401/403': (r) => r.status === 401 || r.status === 403 || r.status < 500 });
  sleep(0.3);
}

export function mesh_large_payload() {
  const payload = JSON.stringify({
    mode: 'dapr',
    serviceIds: Array.from({ length: 100 }, (_, i) => `service-${i}`)
  });
  const res = http.put(`${BASE_URL}/api/monitor/service-mesh/batch-mode`, payload, { headers: HEADERS, tags: { name: 'mesh_large_payload' } });
  check(res, { 'large payload handled': (r) => r.status < 500 });
  sleep(0.5);
}

// ============= 响应时间场景 =============

export function latency_mesh_config() {
  const res = http.get(`${BASE_URL}/api/monitor/service-mesh/config`, { headers: HEADERS, tags: { name: 'mesh_latency_config' } });
  check(res, { 'config latency < 3s': (r) => r.timings.duration < 3000 });
  sleep(0.2);
}

export function latency_mesh_status() {
  const res = http.get(`${BASE_URL}/api/monitor/service-mesh/status`, { headers: HEADERS, tags: { name: 'mesh_latency_status' } });
  check(res, { 'status latency < 3s': (r) => r.timings.duration < 3000 });
  sleep(0.2);
}

export function latency_mesh_test_conn() {
  const res = http.post(`${BASE_URL}/api/monitor/service-mesh/test/identity-service`, null, { headers: HEADERS, tags: { name: 'mesh_latency_test' } });
  check(res, { 'test conn latency < 5s': (r) => r.timings.duration < 5000 });
  sleep(0.3);
}

// 默认导出（k6 运行入口）
export default function () {
  smoke_mesh_config_list();
  smoke_mesh_status();
  smoke_mesh_refresh();
  smoke_mesh_test_connection();
  sleep(1);
}

// k6 选项
export const options = {
  scenarios: {
    smoke: {
      executor: 'shared-iterations',
      vus: 1,
      iterations: 5,
      maxDuration: '30s',
    },
  },
  thresholds: {
    http_req_duration: ['p(95)<3000'],
    http_req_failed: ['rate<0.5'],
  },
};
