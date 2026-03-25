/**
 * MCP 工具协议性能压测 (k6)
 * =========================
 * 压测 MCP 核心端点：工具列表、工具执行、同步对话、健康检查
 * 严禁压生产/开发环境，仅在性能测试环境执行
 */

import http from 'k6/http';
import { check, sleep, group } from 'k6';
import { Rate, Trend, Counter } from 'k6/metrics';

// === 自定义指标 ===
const mcpToolListSuccess = new Rate('mcp_tool_list_success');
const mcpToolExecSuccess = new Rate('mcp_tool_exec_success');
const mcpChatSuccess     = new Rate('mcp_chat_success');
const mcpHealthSuccess   = new Rate('mcp_health_success');

const mcpToolListDuration = new Trend('mcp_tool_list_duration', true);
const mcpToolExecDuration = new Trend('mcp_tool_exec_duration', true);
const mcpChatDuration     = new Trend('mcp_chat_duration', true);
const mcpHealthDuration   = new Trend('mcp_health_duration', true);

const mcpErrors = new Counter('mcp_errors');

// === 配置 ===
const BASE_URL = __ENV.BASE_URL || 'http://localhost:5062';
const AUTH_TOKEN = __ENV.AUTH_TOKEN || '';

const headers = {
  'Content-Type': 'application/json',
  'Authorization': AUTH_TOKEN ? `Bearer ${AUTH_TOKEN}` : '',
};

// === 场景定义 ===
export const options = {
  scenarios: {
    // 场景1：工具列表 - 轻量读取
    tool_list: {
      executor: 'constant-vus',
      vus: 10,
      duration: '30s',
      exec: 'toolList',
      tags: { endpoint: 'tool_list' },
    },
    // 场景2：工具执行 - 中等负载
    tool_exec: {
      executor: 'ramping-vus',
      startVUs: 1,
      stages: [
        { duration: '10s', target: 5 },
        { duration: '20s', target: 10 },
        { duration: '10s', target: 0 },
      ],
      exec: 'toolExecute',
      startTime: '5s',
      tags: { endpoint: 'tool_exec' },
    },
    // 场景3：同步对话 - 高负载
    chat: {
      executor: 'ramping-vus',
      startVUs: 1,
      stages: [
        { duration: '15s', target: 5 },
        { duration: '20s', target: 15 },
        { duration: '10s', target: 0 },
      ],
      exec: 'chatSync',
      startTime: '10s',
      tags: { endpoint: 'chat' },
    },
    // 场景4：健康检查 - 高频轮询
    health_check: {
      executor: 'constant-vus',
      vus: 5,
      duration: '45s',
      exec: 'healthCheck',
      tags: { endpoint: 'health' },
    },
  },

  thresholds: {
    // 工具列表: P95 < 500ms
    'mcp_tool_list_duration{endpoint:tool_list}': ['p(95)<500'],
    // 工具执行: P95 < 3000ms (含模型推理)
    'mcp_tool_exec_duration{endpoint:tool_exec}': ['p(95)<3000'],
    // 对话: P95 < 5000ms
    'mcp_chat_duration{endpoint:chat}': ['p(95)<5000'],
    // 健康检查: P95 < 200ms
    'mcp_health_duration{endpoint:health}': ['p(95)<200'],
    // 总成功率 > 90%
    'mcp_tool_list_success': ['rate>0.90'],
    'mcp_health_success': ['rate>0.90'],
  },
};

// === 工具列表压测 ===
export function toolList() {
  group('MCP 工具列表', () => {
    const res = http.get(`${BASE_URL}/api/iotcloudai/mcp/tools`, { headers, tags: { name: 'GET /mcp/tools' } });
    const ok = check(res, {
      '状态码 200': (r) => r.status === 200,
      '响应非空': (r) => r.body && r.body.length > 0,
    });
    mcpToolListSuccess.add(ok);
    mcpToolListDuration.add(res.timings.duration);
    if (!ok) mcpErrors.add(1);

    // 按类型筛选
    const resLLM = http.get(`${BASE_URL}/api/iotcloudai/mcp/tools?type=LLM`, { headers, tags: { name: 'GET /mcp/tools?type=LLM' } });
    check(resLLM, { 'LLM 筛选 200': (r) => r.status === 200 });

    sleep(0.5);
  });
}

// === 工具执行压测 ===
export function toolExecute() {
  group('MCP 工具执行', () => {
    // ONNX 预测
    const payload = JSON.stringify({
      features: [100.5, 102.3, 98.7, 101.2, 99.8, 103.1, 97.5, 100.0],
    });
    const res = http.post(
      `${BASE_URL}/api/iotcloudai/mcp/tools/onnx:load_prediction_tcn/execute`,
      payload,
      { headers, tags: { name: 'POST /mcp/tools/execute' } }
    );
    const ok = check(res, {
      '状态码 200/202': (r) => r.status === 200 || r.status === 202,
      '响应有 data': (r) => {
        try { return JSON.parse(r.body).data !== undefined; } catch { return false; }
      },
    });
    mcpToolExecSuccess.add(ok);
    mcpToolExecDuration.add(res.timings.duration);
    if (!ok) mcpErrors.add(1);

    sleep(1);
  });
}

// === 同步对话压测 ===
export function chatSync() {
  const scenes = ['daily_ops', 'charging', 'energy', 'prediction', 'report'];
  const messages = [
    '请预测明天的电力负荷',
    '分析今日充电站运营情况',
    '储能电池健康度如何?',
    '生成本周运营摘要',
    '场站A设备异常分析',
  ];

  group('MCP 同步对话', () => {
    const idx = Math.floor(Math.random() * messages.length);
    const payload = JSON.stringify({
      message: messages[idx],
      scene: scenes[idx],
    });
    const res = http.post(
      `${BASE_URL}/api/iotcloudai/mcp/chat`,
      payload,
      { headers, tags: { name: 'POST /mcp/chat' } }
    );
    const ok = check(res, {
      '状态码 200': (r) => r.status === 200,
      '响应有内容': (r) => r.body && r.body.length > 10,
    });
    mcpChatSuccess.add(ok);
    mcpChatDuration.add(res.timings.duration);
    if (!ok) mcpErrors.add(1);

    sleep(2);
  });
}

// === 健康检查压测 ===
export function healthCheck() {
  group('MCP 健康检查', () => {
    const res = http.get(`${BASE_URL}/api/iotcloudai/mcp/health`, { headers, tags: { name: 'GET /mcp/health' } });
    const ok = check(res, {
      '状态码 200': (r) => r.status === 200,
      '响应含 total': (r) => {
        try { return JSON.parse(r.body).data.total !== undefined; } catch { return false; }
      },
    });
    mcpHealthSuccess.add(ok);
    mcpHealthDuration.add(res.timings.duration);
    if (!ok) mcpErrors.add(1);

    sleep(1);
  });
}
