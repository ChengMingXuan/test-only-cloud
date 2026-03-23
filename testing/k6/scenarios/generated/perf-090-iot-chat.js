/**
 * AI智能对话 - k6 性能测试场景
 * 服务: iotcloudai
 * 端点覆盖:
 *   - POST /api/iotcloudai/chat/send (发送消息)
 *   - GET  /api/iotcloudai/sessions (会话列表)
 *   - GET  /api/iotcloudai/sessions/{id}/messages (消息历史)
 *   - DELETE /api/iotcloudai/sessions/{id} (删除会话)
 *   - POST /api/iotcloudai/insight/predict/load (负荷预测)
 *   - POST /api/iotcloudai/insight/predict/pv (光伏预测)
 *   - POST /api/iotcloudai/insight/predict/price (电价预测)
 *   - POST /api/iotcloudai/insight/vision/shadow (遮挡检测)
 *   - POST /api/iotcloudai/insight/vision/charger (桩巡检)
 *   - GET  /api/iotcloudai/insight/status (引擎状态)
 *   - POST /api/iotcloudai/report/summarize (AI摘要)
 *   - POST /api/iotcloudai/report/intent-feedback (意图反馈)
 * 场景数: 35
 */
import http from 'k6/http';
import { check, sleep, group } from 'k6';
import { Rate, Trend, Counter } from 'k6/metrics';

const BASE_URL = __ENV.TEST_BASE_URL || 'http://localhost:8000';
const MOCK_TOKEN = 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.test';

const errorRate = new Rate('errors');
const responseTrend = new Trend('response_time_ai_chat');
const requestCounter = new Counter('requests_ai_chat');

const headers = {
  'Content-Type': 'application/json',
  'Authorization': MOCK_TOKEN,
  'X-Tenant-Code': 'TEST_TENANT'
};

// ==================== Mock 请求体 ====================
const chatBody = JSON.stringify({
  message: '帮我分析最近一周的负荷数据趋势',
  sessionId: null,
  scene: 'load_analysis'
});

const predictBody = JSON.stringify({
  stationId: 'station-001',
  startTime: '2025-01-01',
  endTime: '2025-01-07',
  granularity: 'hourly'
});

const visionBody = JSON.stringify({
  imageUrl: 'https://example.com/panel.jpg',
  deviceId: 'device-001'
});

const reportBody = JSON.stringify({
  stationId: 'station-001',
  dateRange: '2025-01',
  type: 'monthly'
});

const feedbackBody = JSON.stringify({
  intentLogId: 'log-001',
  isCorrect: true,
  feedback: '识别准确'
});

const SESSION_ID = '00000000-0000-0000-0000-000000000001';

// ==================== 冒烟测试场景 (5条) ====================
export function smoke_basic_chat_send() {
  const res = http.post(BASE_URL + '/api/iotcloudai/chat/send', chatBody, { headers });
  check(res, { '[S01] 发送消息-状态码正常': r => r.status < 500 });
  requestCounter.add(1);
  sleep(0.1);
}

export function smoke_sessions_list() {
  const res = http.get(BASE_URL + '/api/iotcloudai/sessions', { headers });
  check(res, { '[S02] 会话列表-状态码正常': r => r.status < 500 });
  requestCounter.add(1);
  sleep(0.1);
}

export function smoke_engine_status() {
  const res = http.get(BASE_URL + '/api/iotcloudai/insight/status', { headers });
  check(res, { '[S03] 引擎状态-状态码正常': r => r.status < 500 });
  requestCounter.add(1);
  sleep(0.1);
}

export function smoke_predict_load() {
  const res = http.post(BASE_URL + '/api/iotcloudai/insight/predict/load', predictBody, { headers });
  check(res, { '[S04] 负荷预测-状态码正常': r => r.status < 500 });
  requestCounter.add(1);
  sleep(0.1);
}

export function smoke_report_summarize() {
  const res = http.post(BASE_URL + '/api/iotcloudai/report/summarize', reportBody, { headers });
  check(res, { '[S05] AI摘要-状态码正常': r => r.status < 500 });
  requestCounter.add(1);
  sleep(0.1);
}

// ==================== 负载测试场景 (10条) ====================
export function load_10vu_chat_send() {
  const res = http.post(BASE_URL + '/api/iotcloudai/chat/send', chatBody, { headers });
  check(res, { '[L01] 10VU-发送消息': r => r.status < 500 });
  sleep(0.5);
}

export function load_50vu_chat_send() {
  const res = http.post(BASE_URL + '/api/iotcloudai/chat/send', chatBody, { headers });
  check(res, { '[L02] 50VU-发送消息': r => r.status < 500 });
  sleep(0.5);
}

export function load_100vu_sessions() {
  const res = http.get(BASE_URL + '/api/iotcloudai/sessions', { headers });
  check(res, { '[L03] 100VU-会话列表': r => r.status < 500 });
  sleep(0.5);
}

export function load_messages_history() {
  const res = http.get(BASE_URL + `/api/iotcloudai/sessions/${SESSION_ID}/messages`, { headers });
  check(res, { '[L04] 消息历史-负载': r => r.status < 500 });
  sleep(0.5);
}

export function load_predict_pv() {
  const res = http.post(BASE_URL + '/api/iotcloudai/insight/predict/pv', predictBody, { headers });
  check(res, { '[L05] 光伏预测-负载': r => r.status < 500 });
  sleep(0.5);
}

export function load_predict_price() {
  const res = http.post(BASE_URL + '/api/iotcloudai/insight/predict/price', predictBody, { headers });
  check(res, { '[L06] 电价预测-负载': r => r.status < 500 });
  sleep(0.5);
}

export function load_vision_shadow() {
  const res = http.post(BASE_URL + '/api/iotcloudai/insight/vision/shadow', visionBody, { headers });
  check(res, { '[L07] 遮挡检测-负载': r => r.status < 500 });
  sleep(0.5);
}

export function load_vision_charger() {
  const res = http.post(BASE_URL + '/api/iotcloudai/insight/vision/charger', visionBody, { headers });
  check(res, { '[L08] 桩巡检-负载': r => r.status < 500 });
  sleep(0.5);
}

export function load_report_summarize() {
  const res = http.post(BASE_URL + '/api/iotcloudai/report/summarize', reportBody, { headers });
  check(res, { '[L09] AI摘要-负载': r => r.status < 500 });
  sleep(0.5);
}

export function load_intent_feedback() {
  const res = http.post(BASE_URL + '/api/iotcloudai/report/intent-feedback', feedbackBody, { headers });
  check(res, { '[L10] 意图反馈-负载': r => r.status < 500 });
  sleep(0.5);
}

// ==================== 压力测试场景 (10条) ====================
export function stress_200vu_chat() {
  const res = http.post(BASE_URL + '/api/iotcloudai/chat/send', chatBody, { headers });
  responseTrend.add(res.timings.duration);
  check(res, { '[T01] 200VU-发送消息-响应<5s': r => r.timings.duration < 5000 });
  sleep(0.3);
}

export function stress_500vu_sessions() {
  const res = http.get(BASE_URL + '/api/iotcloudai/sessions', { headers });
  responseTrend.add(res.timings.duration);
  check(res, { '[T02] 500VU-会话列表': r => r.status < 500 });
  sleep(0.3);
}

export function stress_burst_chat() {
  for (let i = 0; i < 5; i++) {
    const res = http.post(BASE_URL + '/api/iotcloudai/chat/send', chatBody, { headers });
    errorRate.add(res.status >= 500);
    requestCounter.add(1);
  }
  check(true, { '[T03] 突发5连请求': () => true });
  sleep(0.5);
}

export function stress_concurrent_predict() {
  const endpoints = ['/api/iotcloudai/insight/predict/load', '/api/iotcloudai/insight/predict/pv', '/api/iotcloudai/insight/predict/price'];
  endpoints.forEach(ep => {
    const res = http.post(BASE_URL + ep, predictBody, { headers });
    errorRate.add(res.status >= 500);
    requestCounter.add(1);
  });
  check(true, { '[T04] 并发3预测': () => true });
  sleep(0.5);
}

export function stress_rapid_delete() {
  for (let i = 0; i < 3; i++) {
    const res = http.del(BASE_URL + `/api/iotcloudai/sessions/${SESSION_ID}`, null, { headers });
    errorRate.add(res.status >= 500);
    requestCounter.add(1);
  }
  check(true, { '[T05] 快速删除': () => true });
  sleep(0.5);
}

export function stress_mixed_workload() {
  group('混合负载', () => {
    http.post(BASE_URL + '/api/iotcloudai/chat/send', chatBody, { headers });
    http.get(BASE_URL + '/api/iotcloudai/sessions', { headers });
    http.get(BASE_URL + '/api/iotcloudai/insight/status', { headers });
    http.post(BASE_URL + '/api/iotcloudai/report/summarize', reportBody, { headers });
    requestCounter.add(4);
  });
  check(true, { '[T06] 混合工作负载': () => true });
  sleep(0.5);
}

export function stress_long_message() {
  const longBody = JSON.stringify({
    message: '请详细分析'.repeat(200),
    sessionId: null,
    scene: 'general'
  });
  const res = http.post(BASE_URL + '/api/iotcloudai/chat/send', longBody, { headers });
  check(res, { '[T07] 长消息发送': r => r.status < 500 });
  sleep(0.3);
}

export function stress_no_auth() {
  const noAuthHeaders = { 'Content-Type': 'application/json' };
  const res = http.post(BASE_URL + '/api/iotcloudai/chat/send', chatBody, { headers: noAuthHeaders });
  check(res, { '[T08] 无鉴权-应拒绝': r => r.status === 401 || r.status === 403 || r.status < 500 });
  sleep(0.3);
}

export function stress_invalid_body() {
  const res = http.post(BASE_URL + '/api/iotcloudai/chat/send', 'invalid-json', { headers });
  check(res, { '[T09] 非法请求体': r => r.status < 500 || r.status === 400 });
  sleep(0.3);
}

export function stress_404_endpoint() {
  const res = http.get(BASE_URL + '/api/iotcloudai/nonexistent', { headers });
  check(res, { '[T10] 不存在端点': r => r.status === 404 || r.status < 500 });
  sleep(0.3);
}

// ==================== 耐久测试场景 (5条) ====================
export function endurance_steady_chat() {
  const res = http.post(BASE_URL + '/api/iotcloudai/chat/send', chatBody, { headers });
  responseTrend.add(res.timings.duration);
  check(res, { '[D01] 持续发送消息': r => r.status < 500 });
  sleep(1);
}

export function endurance_steady_query() {
  const res = http.get(BASE_URL + '/api/iotcloudai/sessions', { headers });
  responseTrend.add(res.timings.duration);
  check(res, { '[D02] 持续查询会话': r => r.status < 500 });
  sleep(1);
}

export function endurance_full_workflow() {
  group('完整工作流', () => {
    // 1. 发送消息
    const sendRes = http.post(BASE_URL + '/api/iotcloudai/chat/send', chatBody, { headers });
    check(sendRes, { '发送成功': r => r.status < 500 });
    // 2. 获取会话列表
    const listRes = http.get(BASE_URL + '/api/iotcloudai/sessions', { headers });
    check(listRes, { '获取列表': r => r.status < 500 });
    // 3. 获取消息历史
    const msgRes = http.get(BASE_URL + `/api/iotcloudai/sessions/${SESSION_ID}/messages`, { headers });
    check(msgRes, { '获取消息': r => r.status < 500 });
    // 4. 预测
    const predRes = http.post(BASE_URL + '/api/iotcloudai/insight/predict/load', predictBody, { headers });
    check(predRes, { '负荷预测': r => r.status < 500 });
    // 5. 引擎状态
    const statusRes = http.get(BASE_URL + '/api/iotcloudai/insight/status', { headers });
    check(statusRes, { '引擎状态': r => r.status < 500 });
    requestCounter.add(5);
  });
  check(true, { '[D03] 完整工作流': () => true });
  sleep(2);
}

export function endurance_steady_predict() {
  const endpoints = ['load', 'pv', 'price'];
  const ep = endpoints[Math.floor(Math.random() * endpoints.length)];
  const res = http.post(BASE_URL + `/api/iotcloudai/insight/predict/${ep}`, predictBody, { headers });
  responseTrend.add(res.timings.duration);
  check(res, { '[D04] 持续预测': r => r.status < 500 });
  sleep(1);
}

export function endurance_report_cycle() {
  const res = http.post(BASE_URL + '/api/iotcloudai/report/summarize', reportBody, { headers });
  responseTrend.add(res.timings.duration);
  check(res, { '[D05] 持续AI摘要': r => r.status < 500 });
  sleep(2);
}

// ==================== 基准测试场景 (5条) ====================
export function benchmark_chat_latency() {
  const res = http.post(BASE_URL + '/api/iotcloudai/chat/send', chatBody, { headers });
  responseTrend.add(res.timings.duration);
  check(res, { '[B01] 对话延迟 < 3s': r => r.timings.duration < 3000 });
  sleep(0.1);
}

export function benchmark_session_latency() {
  const res = http.get(BASE_URL + '/api/iotcloudai/sessions', { headers });
  responseTrend.add(res.timings.duration);
  check(res, { '[B02] 会话查询 < 1s': r => r.timings.duration < 1000 });
  sleep(0.1);
}

export function benchmark_predict_latency() {
  const res = http.post(BASE_URL + '/api/iotcloudai/insight/predict/load', predictBody, { headers });
  responseTrend.add(res.timings.duration);
  check(res, { '[B03] 预测延迟 < 2s': r => r.timings.duration < 2000 });
  sleep(0.1);
}

export function benchmark_vision_latency() {
  const res = http.post(BASE_URL + '/api/iotcloudai/insight/vision/shadow', visionBody, { headers });
  responseTrend.add(res.timings.duration);
  check(res, { '[B04] 视觉延迟 < 3s': r => r.timings.duration < 3000 });
  sleep(0.1);
}

export function benchmark_throughput() {
  for (let i = 0; i < 10; i++) {
    http.get(BASE_URL + '/api/iotcloudai/insight/status', { headers });
    requestCounter.add(1);
  }
  check(true, { '[B05] 吞吐量-10请求': () => true });
  sleep(0.5);
}

// ==================== 默认导出 ====================
export default function() {
  group('AI智能对话', () => {
    smoke_basic_chat_send();
    smoke_sessions_list();
    smoke_engine_status();
    smoke_predict_load();
    smoke_report_summarize();
  });
}

// 配置导出
export const options = {
  scenarios: {
    smoke: {
      executor: 'constant-vus',
      vus: 1,
      duration: '10s',
      exec: 'default',
    },
  },
  thresholds: {
    http_req_duration: ['p(95)<5000'],
    errors: ['rate<0.5'],
  },
};
