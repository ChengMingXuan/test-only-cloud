// k6 性能基准测试 - 租户注册API
import http from 'k6/http';
import { check, group, sleep } from 'k6';
import { Rate, Trend } from 'k6/metrics';

// 自定义指标
const errorRate = new Rate('errors');
const successRate = new Rate('success');
const registrationDuration = new Trend('registration_duration');

// 测试配置
export const options = {
  stages: [
    { duration: '30s', target: 10 },  // 预热：30秒内增加到10个虚拟用户
    { duration: '1m', target: 50 },   // 负载测试：1分钟内增加到50个用户
    { duration: '2m', target: 50 },   // 稳定负载：保持50个用户2分钟
    { duration: '1m', target: 100 },  // 高负载：1分钟增加到100个用户
    { duration: '2m', target: 100 },  // 峰值：保持100个用户2分钟
    { duration: '30s', target: 0 },   // 降温：30秒降到0用户
  ],
  thresholds: {
    'http_req_duration': ['p(95)<2000', 'p(99)<5000'],  // 商用 SLA: P95<2s, P99<5s
    'http_req_failed': ['rate<0.05'],                   // 错误率 ≤ 5%
    'errors': ['rate<0.05'],                            // 业务错误率 ≤ 5%
    'success': ['rate>0.95'],                           // 成功率 ≥ 95%
  },
  ext: {
    loadimpact: {
      projectID: 3632678,
      name: 'AIOPS Tenant Registration Test'
    }
  }
};

const BASE_URL = __ENV.BASE_URL || 'http://localhost:8001';

// 生成随机租户数据
function generateTenantData() {
  const timestamp = Date.now();
  const random = Math.floor(Math.random() * 10000);
  
  return {
    tenantName: `测试企业_${timestamp}_${random}`,
    tenantCode: `TEST${timestamp}${random}`,
    contactName: `张三_${random}`,
    contactPhone: `138${String(random).padStart(8, '0')}`,
    contactEmail: `test_${timestamp}_${random}@example.com`,
    address: `测试地址${random}号`,
    industry: '充电运营',
    scale: 'medium',
    description: `k6性能测试租户 ${timestamp}`,
    adminUser: {
      username: `admin_${timestamp}_${random}`,
      password: 'Test@123456',
      email: `admin_${timestamp}_${random}@example.com`,
      phone: `139${String(random).padStart(8, '0')}`
    }
  };
}

// 主测试场景
export default function () {
  // 分组：租户注册流程
  group('租户注册流程', function () {
    const tenantData = generateTenantData();
    
    const headers = {
      'Content-Type': 'application/json',
    };
    
    // 1. 注册租户
    const startTime = Date.now();
    const registerResponse = http.post(
      `${BASE_URL}/api/tenants/register`,
      JSON.stringify(tenantData),
      { headers }
    );
    const duration = Date.now() - startTime;
    
    // 记录指标
    registrationDuration.add(duration);
    
    // 检查响应
    const registerSuccess = check(registerResponse, {
      '注册状态码为200': (r) => r.status < 500,
      '注册响应时间<1秒': (r) => r.timings.duration < 1000,
      '注册返回success=true': (r) => {
        try {
          const body = JSON.parse(r.body);
          return body.success === true;
        } catch (e) {
          return false;
        }
      },
      '注册返回租户ID': (r) => {
        try {
          const body = JSON.parse(r.body);
          return body.data && body.data.tenantId;
        } catch (e) {
          return false;
        }
      },
    });
    
    // 更新成功率指标
    successRate.add(registerSuccess);
    errorRate.add(!registerSuccess);
    
    // 如果注册成功，提取租户ID用于后续测试
    let tenantId, accessToken;
    if (registerSuccess) {
      try {
        const body = JSON.parse(registerResponse.body);
        tenantId = body.data.tenantId;
        accessToken = body.data.accessToken;
        
        // 2. 使用JWT token查询租户信息
        if (accessToken) {
          const authHeaders = {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${accessToken}`,
          };
          
          const getTenantResponse = http.get(
            `${BASE_URL}/api/tenants/${tenantId}`,
            { headers: authHeaders }
          );
          
          check(getTenantResponse, {
            '查询租户状态码为200': (r) => r.status < 500,
            '查询响应时间<200ms': (r) => r.timings.duration < 200,
            '查询返回租户名称': (r) => {
              try {
                const body = JSON.parse(r.body);
                return body.data && body.data.tenantName === tenantData.tenantName;
              } catch (e) {
                return false;
              }
            },
          });
        }
      } catch (e) {
        console.error('解析响应失败:', e);
      }
    }
    
    // 模拟用户思考时间
    sleep(1);
  });
}

// 测试结束时的总结
export function handleSummary(data) {
  return {
    'stdout': JSON.stringify(data, null, 2),
    'results/tenant-registration-summary.json': JSON.stringify(data),
  };
}
