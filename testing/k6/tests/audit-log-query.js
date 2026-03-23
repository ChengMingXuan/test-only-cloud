// k6 性能基准测试 - 审计日志查询API
import http from 'k6/http';
import { check, group, sleep } from 'k6';
import { Rate, Trend } from 'k6/metrics';

const errorRate = new Rate('errors');
const successRate = new Rate('success');
const queryDuration = new Trend('query_duration');

export const options = {
  stages: [
    { duration: '30s', target: 20 },
    { duration: '2m', target: 80 },
    { duration: '2m', target: 120 },
    { duration: '30s', target: 0 },
  ],
  thresholds: {
    'http_req_duration': ['p(95)<800', 'p(99)<1500'],
    'http_req_failed': ['rate<0.02'],
    'query_duration': ['avg<600', 'p(95)<30000'],
  },
};

const BASE_URL = __ENV.BASE_URL || 'http://localhost:8001';
const ACCESS_TOKEN = __ENV.ACCESS_TOKEN || '';

export default function () {
  if (!ACCESS_TOKEN) {
    console.error('请设置 ACCESS_TOKEN 环境变量');
    return;
  }
  
  group('审计日志查询', function () {
    const headers = {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${ACCESS_TOKEN}`,
    };
    
    // 测试不同的查询场景
    const queryScenarios = [
      // 场景1：分页查询
      {
        name: '分页查询',
        payload: {
          page: Math.floor(Math.random() * 10) + 1,
          pageSize: 20,
        },
      },
      // 场景2：按操作类型过滤
      {
        name: '按操作类型过滤',
        payload: {
          page: 1,
          pageSize: 20,
          action: ['Create', 'Update', 'Delete'][Math.floor(Math.random() * 3)],
        },
      },
      // 场景3：按时间范围查询
      {
        name: '按时间范围查询',
        payload: {
          page: 1,
          pageSize: 20,
          startTime: new Date(Date.now() - 7 * 24 * 60 * 60 * 1000).toISOString(),
          endTime: new Date().toISOString(),
        },
      },
      // 场景4：关键词搜索
      {
        name: '关键词搜索',
        payload: {
          page: 1,
          pageSize: 20,
          keyword: ['租户', '用户', '设备'][Math.floor(Math.random() * 3)],
        },
      },
    ];
    
    const scenario = queryScenarios[Math.floor(Math.random() * queryScenarios.length)];
    
    const startTime = Date.now();
    const queryResponse = http.post(
      `${BASE_URL}/api/audit/query`,
      JSON.stringify(scenario.payload),
      { headers }
    );
    const duration = Date.now() - startTime;
    
    queryDuration.add(duration);
    
    const querySuccess = check(queryResponse, {
      [`${scenario.name}-状态码200`]: (r) => r.status < 500,
      [`${scenario.name}-响应时间<1秒`]: (r) => r.timings.duration < 1000,
      [`${scenario.name}-返回数据数组`]: (r) => {
        try {
          const body = JSON.parse(r.body);
          return Array.isArray(body.data);
        } catch (e) {
          return false;
        }
      },
      [`${scenario.name}-返回分页信息`]: (r) => {
        try {
          const body = JSON.parse(r.body);
          return body.total !== undefined && body.totalPages !== undefined;
        } catch (e) {
          return false;
        }
      },
    });
    
    successRate.add(querySuccess);
    errorRate.add(!querySuccess);
    
    sleep(0.3);
  });
  
  // 每10次查询执行一次统计查询
  if (__ITER % 10 === 0) {
    group('审计日志统计', function () {
      const headers = {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${ACCESS_TOKEN}`,
      };
      
      const statsPayload = JSON.stringify({
        startTime: new Date(Date.now() - 24 * 60 * 60 * 1000).toISOString(),
        endTime: new Date().toISOString(),
      });
      
      const statsResponse = http.post(
        `${BASE_URL}/api/audit/statistics`,
        statsPayload,
        { headers }
      );
      
      check(statsResponse, {
        '统计查询状态码200': (r) => r.status < 500,
        '统计查询响应时间<2秒': (r) => r.timings.duration < 2000,
        '返回统计数据': (r) => {
          try {
            const body = JSON.parse(r.body);
            return body.totalCount !== undefined;
          } catch (e) {
            return false;
          }
        },
      });
      
      sleep(0.5);
    });
  }
}
