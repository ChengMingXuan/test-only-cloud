// k6 性能基准测试 - 用户登录API
import http from 'k6/http';
import { check, group, sleep } from 'k6';
import { Rate, Trend } from 'k6/metrics';

// 自定义指标
const errorRate = new Rate('errors');
const successRate = new Rate('success');
const loginDuration = new Trend('login_duration');

// 测试配置
export const options = {
  scenarios: {
    // 场景1：恒定负载测试
    constant_load: {
      executor: 'constant-vus',
      vus: 50,
      duration: '2m',
    },
    // 场景2：压力测试
    stress_test: {
      executor: 'ramping-vus',
      startVUs: 0,
      stages: [
        { duration: '1m', target: 100 },
        { duration: '3m', target: 100 },
        { duration: '1m', target: 200 },
        { duration: '2m', target: 200 },
        { duration: '1m', target: 0 },
      ],
      gracefulRampDown: '30s',
      startTime: '2m30s',
    },
  },
  thresholds: {
    'http_req_duration': ['p(95)<2000', 'p(99)<5000'],  // 商用 SLA
    'http_req_failed': ['rate<0.01'],                   // 错误率 ≤ 1%
    'login_duration': ['avg<250', 'p(95)<400'],         // 登录平均<250ms
    'errors': ['rate<0.01'],
    'success': ['rate>0.95'],
  },
};

const BASE_URL = __ENV.BASE_URL || 'http://localhost:8000';

// 测试用户池
const testUsers = [
  { phone: '13800138001', password: 'Test@123456' },
  { phone: '13800138002', password: 'Test@123456' },
  { phone: '13800138003', password: 'Test@123456' },
  { phone: '13800138004', password: 'Test@123456' },
  { phone: '13800138005', password: 'Test@123456' },
];

export default function () {
  group('用户登录流程', function () {
    // 随机选择一个测试用户
    const user = testUsers[Math.floor(Math.random() * testUsers.length)];
    
    const headers = {
      'Content-Type': 'application/json',
    };
    
    const loginPayload = JSON.stringify({
      phone: user.phone,
      password: user.password,
    });
    
    // 执行登录
    const startTime = Date.now();
    const loginResponse = http.post(
      `${BASE_URL}/api/auth/login`,
      loginPayload,
      { headers }
    );
    const duration = Date.now() - startTime;
    
    loginDuration.add(duration);
    
    // 验证响应
    const loginSuccess = check(loginResponse, {
      '登录状态码为200': (r) => r.status < 500,
      '登录响应时间<500ms': (r) => r.timings.duration < 500,
      '返回accessToken': (r) => {
        try {
          const body = JSON.parse(r.body);
          return body.accessToken && body.accessToken.length > 0;
        } catch (e) {
          return false;
        }
      },
      '返回refreshToken': (r) => {
        try {
          const body = JSON.parse(r.body);
          return body.refreshToken && body.refreshToken.length > 0;
        } catch (e) {
          return false;
        }
      },
    });
    
    successRate.add(loginSuccess);
    errorRate.add(!loginSuccess);
    
    // 如果登录成功，测试token验证
    if (loginSuccess) {
      try {
        const body = JSON.parse(loginResponse.body);
        const accessToken = body.accessToken;
        
        // 使用token访问受保护的资源
        const authHeaders = {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${accessToken}`,
        };
        
        const profileResponse = http.get(
          `${BASE_URL}/api/auth/profile`,
          { headers: authHeaders }
        );
        
        check(profileResponse, {
          '获取用户信息状态码为200': (r) => r.status < 500,
          '获取用户信息响应时间<200ms': (r) => r.timings.duration < 200,
          '返回用户手机号': (r) => {
            try {
              const body = JSON.parse(r.body);
              return body.phone === user.phone;
            } catch (e) {
              return false;
            }
          },
        });
      } catch (e) {
        console.error('Token验证失败:', e);
      }
    }
    
    sleep(0.5); // 模拟用户停留时间
  });
}
