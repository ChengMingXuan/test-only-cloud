// K6 Performance Testing Configuration
// JGSY AGI Platform Load Testing

export const config = {
  // Base URL
  baseUrl: __ENV.BASE_URL || 'http://localhost:8000',
  
  // Test scenarios — executor + stages only (thresholds 放在 scenarioThresholds 中)
  scenarios: {
    // 冒烟测试 - 验证基本功能
    smoke: {
      executor: 'ramping-vus',
      stages: [
        { duration: '1m', target: 10 },  // 1分钟内增加到10个VU
        { duration: '2m', target: 10 },  // 保持10个VU运行2分钟
        { duration: '1m', target: 0 },   // 1分钟内减少到0
      ],
    },
    
    // 负载测试 - 正常负载
    load: {
      executor: 'ramping-vus',
      stages: [
        { duration: '2m', target: 100 },   // 2分钟增加到100 VU
        { duration: '5m', target: 100 },   // 保持100 VU运行5分钟
        { duration: '2m', target: 200 },   // 2分钟增加到200 VU
        { duration: '5m', target: 200 },   // 保持200 VU运行5分钟
        { duration: '2m', target: 0 },     // 2分钟减少到0
      ],
    },
    
    // 压力测试 - 找到系统极限
    stress: {
      executor: 'ramping-vus',
      stages: [
        { duration: '2m', target: 200 },   // 2分钟增加到200 VU
        { duration: '5m', target: 200 },   // 保持200 VU
        { duration: '2m', target: 500 },   // 2分钟增加到500 VU
        { duration: '5m', target: 500 },   // 保持500 VU
        { duration: '2m', target: 1000 },  // 2分钟增加到1000 VU
        { duration: '5m', target: 1000 },  // 保持1000 VU
        { duration: '2m', target: 0 },     // 2分钟减少到0
      ],
    },
    
    // 峰值测试 - 短时间内大量并发
    spike: {
      executor: 'ramping-vus',
      stages: [
        { duration: '1m', target: 100 },   // 1分钟增加到100 VU
        { duration: '30s', target: 2000 }, // 30秒激增到2000 VU
        { duration: '1m', target: 2000 },  // 保持2000 VU运行1分钟
        { duration: '30s', target: 100 },  // 30秒降回100 VU
        { duration: '1m', target: 100 },   // 保持100 VU
        { duration: '1m', target: 0 },     // 1分钟减少到0
      ],
    },
    
    // 浸泡测试 - 长时间稳定负载（检测内存泄漏）
    soak: {
      executor: 'ramping-vus',
      stages: [
        { duration: '5m', target: 200 },     // 5分钟增加到200 VU
        { duration: '60m', target: 200 },    // 保持200 VU运行60分钟
        { duration: '5m', target: 0 },       // 5分钟减少到0
      ],
    },
  },
  
  // Scenario-specific thresholds (与 scenarios 分离，避免 k6 unknown field 错误)
  // 商用 SLA 标准：冒烟/负载 P95<2s，压力 P95<5s，峰值 P95<8s，浸泡 P95<3s
  scenarioThresholds: {
    smoke: {
      http_req_duration: ['p(95)<2000', 'p(99)<5000'],
      http_req_failed: ['rate<0.01'],
    },
    load: {
      http_req_duration: ['p(95)<2000', 'p(99)<5000'],
      http_req_failed: ['rate<0.05'],
    },
    stress: {
      http_req_duration: ['p(95)<5000', 'p(99)<10000'],
      http_req_failed: ['rate<0.10'],
    },
    spike: {
      http_req_duration: ['p(95)<8000', 'p(99)<15000'],
      http_req_failed: ['rate<0.15'],
    },
    soak: {
      http_req_duration: ['p(95)<3000', 'p(99)<8000'],
      http_req_failed: ['rate<0.05'],
    },
  },
  
  // Performance thresholds (商用 SLA 目标性能指标)
  thresholds: {
    // HTTP 请求持续时间 — 商用标准
    'http_req_duration': [
      'p(50)<500',     // 50% 请求 < 500ms
      'p(90)<1500',    // 90% 请求 < 1.5s
      'p(95)<2000',    // 95% 请求 < 2s（核心 SLA）
      'p(99)<5000',    // 99% 请求 < 5s
    ],
    
    // HTTP 请求失败率 — 商用 SLA ≤ 1%
    'http_req_failed': ['rate<0.01'],
    
    // 检查通过率 — 核心功能 ≥ 95%
    'checks': ['rate>0.95'],
    
    // 迭代持续时间
    'iteration_duration': ['p(95)<10000'],
  },
  
  // Test data
  testData: {
    // 测试用户
    users: [
      { username: 'admin', password: 'P@ssw0rd', role: 'admin' },
    ],
    
    // 测试租户
    tenants: [
      { id: 1, name: 'Tenant_1', code: 'T001' },
      { id: 2, name: 'Tenant_2', code: 'T002' },
    ],
    
    // 测试充电桩
    devices: [
      { id: 1, code: 'DEV001', stationId: 1 },
      { id: 2, code: 'DEV002', stationId: 1 },
      { id: 3, code: 'DEV003', stationId: 2 },
    ],
  },
  
  // Request options
  requestOptions: {
    headers: {
      'Content-Type': 'application/json',
      'Accept': 'application/json',
      'User-Agent': 'k6-load-test',
    },
    timeout: '30s',
  },
};

export default config;
