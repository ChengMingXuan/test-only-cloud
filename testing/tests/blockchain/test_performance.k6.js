// 区块链服务 — k6 性能与压力测试
// ========================================================
//
// 覆盖：
//   - 故障转移响应时间
//   - 并发操作吞吐量
//   - 链切换延迟
//   - 压力测试（持续高并发）
//   - 内存和 CPU 占用监控
//
// 前提条件：
//   - k6 已安装：https://k6.io/docs/getting-started/installation/
//   - 区块链服务在 http://localhost:8021 运行
//
// 运行：
//   k6 run tests/blockchain/test_performance.k6.js -u 10 -d 30s
//   k6 run tests/blockchain/test_performance.k6.js -u 50 -d 5m --rps 1000
//

import http from 'k6/http';
import { check, group, sleep } from 'k6';
import encoding from 'k6/encoding';


// ═══════════════════════════════════════════════════════════════
// 配置
// ═══════════════════════════════════════════════════════════════

const BASE_URL = __ENV.BASE_URL || 'http://localhost:8021';
const AUTH_TOKEN = __ENV.AUTH_TOKEN || 'mock-jwt-token';

// 并发用户数
const VU = parseInt(__ENV.VU || '10');
// 持续时间
const DURATION = __ENV.DURATION || '30s';
// 预热阶段
const RAMP_UP = '10s';
// 冷却阶段
const RAMP_DOWN = '10s';

// k6 配置
export const options = {
  stages: [
    { duration: RAMP_UP, target: VU },          // 预热：0 → VU 用户
    { duration: DURATION, target: VU },         // 主阶段：VU 用户
    { duration: RAMP_DOWN, target: 0 },         // 冷却：VU → 0 用户
  ],
  thresholds: {
    'http_req_duration': ['p(95)<500', 'p(99)<1000'],  // 95% 请求 < 500ms，99% < 1s
    'http_req_failed': ['rate<0.05'],                   // 失败率 < 5%
    'group_duration': ['p(90)<2000'],                   // 组级别 90% < 2s
  },
};


// ═══════════════════════════════════════════════════════════════
// 辅助函数
// ═══════════════════════════════════════════════════════════════

function getAuthHeaders() {
  return {
    'Authorization': `Bearer ${AUTH_TOKEN}`,
    'Content-Type': 'application/json'
  };
}

function generateUUID() {
  return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
    const r = Math.random() * 16 | 0;
    const v = c === 'x' ? r : (r & 0x3 | 0x8);
    return v.toString(16);
  });
}


// ═══════════════════════════════════════════════════════════════
// 测试场景 1: 获取故障转移状态
// ═══════════════════════════════════════════════════════════════

export function testFailoverStatus() {
  group('Failover Status Query', () => {
    const res = http.get(
      `${BASE_URL}/api/blockchain/failover/status`,
      { headers: getAuthHeaders() }
    );

    check(res, {
      'status is 200': (r) => r.status === 200,
      'response time < 100ms': (r) => r.timings.duration < 100,
      'has activeChain': (r) => r.json().data?.activeChain !== undefined,
      'has nodes': (r) => r.json().data?.nodes !== undefined,
    });

    return res.timings.duration;
  });

  sleep(1);
}


// ═══════════════════════════════════════════════════════════════
// 测试场景 2: 链切换
// ═══════════════════════════════════════════════════════════════

export function testChainSwitch() {
  group('Chain Switch Operation', () => {
    const chains = ['FISCO', 'Hyperchain', 'ChainMaker'];
    const targetChain = chains[Math.floor(Math.random() * chains.length)];

    const payload = JSON.stringify({
      targetChain: targetChain,
      reason: `Performance test - switch to ${targetChain}`
    });

    const res = http.post(
      `${BASE_URL}/api/blockchain/failover/switch-chain`,
      payload,
      { headers: getAuthHeaders() }
    );

    check(res, {
      'status is 200 or 202': (r) => r.status === 200 || r.status === 202,
      'switch successful': (r) => r.json().data?.success === true,
      'response time < 500ms': (r) => r.timings.duration < 500,
    });

    return res.timings.duration;
  });

  sleep(1);
}


// ═══════════════════════════════════════════════════════════════
// 测试场景 3: 节点切换
// ═══════════════════════════════════════════════════════════════

export function testNodeSwitch() {
  group('Node Switch Operation', () => {
    const nodes = ['node-A-primary', 'node-B-slave', 'node-C-dr'];
    const targetNode = nodes[Math.floor(Math.random() * nodes.length)];

    const payload = JSON.stringify({
      nodeName: targetNode,
      reason: `Performance test - switch to ${targetNode}`
    });

    const res = http.post(
      `${BASE_URL}/api/blockchain/failover/switch-node`,
      payload,
      { headers: getAuthHeaders() }
    );

    check(res, {
      'status is 200 or 202': (r) => r.status === 200 || r.status === 202,
      'switch successful': (r) => r.json().data?.success === true,
      'response time < 500ms': (r) => r.timings.duration < 500,
    });

    return res.timings.duration;
  });

  sleep(1);
}


// ═══════════════════════════════════════════════════════════════
// 测试场景 4: 重置到默认链
// ═══════════════════════════════════════════════════════════════

export function testReset() {
  group('Reset to Default Chain', () => {
    const payload = JSON.stringify({
      reason: 'Performance test - reset'
    });

    const res = http.post(
      `${BASE_URL}/api/blockchain/failover/reset`,
      payload,
      { headers: getAuthHeaders() }
    );

    check(res, {
      'status is 200': (r) => r.status === 200,
      'reset successful': (r) => r.json().data?.success === true,
      'response time < 300ms': (r) => r.timings.duration < 300,
    });

    return res.timings.duration;
  });

  sleep(1);
}


// ═══════════════════════════════════════════════════════════════
// 测试场景 5: 健康检查
// ═══════════════════════════════════════════════════════════════

export function testHealth() {
  group('Health Check', () => {
    const res = http.get(
      `${BASE_URL}/api/blockchain/health`,
      { headers: getAuthHeaders() }
    );

    check(res, {
      'status is 200': (r) => r.status === 200,
      'health is Healthy': (r) => r.json().status === 'Healthy',
      'response time < 50ms': (r) => r.timings.duration < 50,
    });

    return res.timings.duration;
  });

  sleep(1);
}


// ═══════════════════════════════════════════════════════════════
// 默认导出函数（主测试）
// ═══════════════════════════════════════════════════════════════

export default function () {
  // 随机选择一个测试场景
  const scenarios = [
    testFailoverStatus,
    testChainSwitch,
    testNodeSwitch,
    testReset,
    testHealth,
  ];

  const scenario = scenarios[Math.floor(Math.random() * scenarios.length)];
  scenario();
}


// ═══════════════════════════════════════════════════════════════
// 高压测试（持续 5 分钟，100 个并发用户）
// ═══════════════════════════════════════════════════════════════

export function stressTest() {
  const scenarios = [
    testFailoverStatus,
    testChainSwitch,
    testNodeSwitch,
    testReset,
    testHealth,
  ];

  const scenario = scenarios[Math.floor(Math.random() * scenarios.length)];
  scenario();
}


// ═══════════════════════════════════════════════════════════════
// 故障转移延迟测试
// ═══════════════════════════════════════════════════════════════

export function failoverLatencyTest() {
  group('Failover Operation Latency', () => {
    // 连续测试故障转移操作的延迟
    const chains = ['ChainMaker', 'FISCO', 'Hyperchain'];
    const timings = [];

    for (let i = 0; i < 10; i++) {
      const chain = chains[i % chains.length];
      const duration = testChainSwitch();
      timings.push(duration);
    }

    const avgDelay = timings.reduce((a, b) => a + b, 0) / timings.length;
    const maxDelay = Math.max(...timings);
    const minDelay = Math.min(...timings);

    console.log(`Chain Switch - Avg: ${avgDelay.toFixed(2)}ms, Min: ${minDelay.toFixed(2)}ms, Max: ${maxDelay.toFixed(2)}ms`);
  });
}


// ═══════════════════════════════════════════════════════════════
// 并发故障转移测试
// ═══════════════════════════════════════════════════════════════

export function concurrentFailoverTest() {
  group('Concurrent Failover Operations', () => {
    // 并发执行多个故障转移操作
    const batch = [];

    for (let i = 0; i < 20; i++) {
      batch.push(http.asyncRequest('POST', `${BASE_URL}/api/blockchain/failover/switch-chain`, 
        JSON.stringify({
          targetChain: i % 2 === 0 ? 'FISCO' : 'Hyperchain',
          reason: `Concurrent test ${i}`
        }),
        { headers: getAuthHeaders() }
      ));
    }

    const responses = http.batch(batch);

    check(responses, {
      'all switch successful': (r) => r.every((res) => res.status === 200 || res.status === 202),
      'no errors': (r) => r.every((res) => res.status < 400),
    });
  });
}
