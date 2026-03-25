/**
 * k6 压测数据创建工具 — 在 setup() 阶段创建独立压测租户和大数据集
 *
 * 使用方式：
 *   import { createPerfEnvironment, cleanupPerfEnvironment } from '../utils/setup-data.js';
 *   export function setup() { return createPerfEnvironment(); }
 *   export function teardown(data) { cleanupPerfEnvironment(data); }
 */
import http from 'k6/http';
import { check } from 'k6';
import { login, getAuthHeaders } from './auth.js';
import config from '../config.js';

const BASE = config.baseUrl;

/**
 * 创建压测环境（独立租户 + 批量设备 + 批量用户）
 * @param {number} deviceCount 创建的设备数量（默认 100）
 * @param {number} userCount 创建的用户数量（默认 50）
 */
export function createPerfEnvironment(deviceCount = 100, userCount = 50) {
  console.log(`🚀 k6 setup: 创建压测环境 (${deviceCount} 设备, ${userCount} 用户)`);

  // 1. 管理员登录
  const auth = login(
    __ENV.ADMIN_USERNAME || 'admin',
    __ENV.ADMIN_PASSWORD || 'P@ssw0rd',
  );
  if (!auth) {
    console.error('❌ 管理员登录失败，无法创建压测数据');
    return { error: true };
  }
  const headers = getAuthHeaders(auth.accessToken);
  headers['Content-Type'] = 'application/json';

  const ts = Date.now();

  // 2. 批量创建设备
  const devices = [];
  for (let i = 0; i < deviceCount; i++) {
    const resp = http.post(`${BASE}/api/devices`, JSON.stringify({
      code: `PERF-DEV-${ts}-${i}`,
      name: `压测设备${i}`,
      type: 'charger',
      power: 60 + (i % 4) * 30,
    }), { headers });

    if (resp.status === 200) {
      try {
        devices.push(JSON.parse(resp.body).data.id);
      } catch (_) { /* 忽略解析失败 */ }
    }
    if (i % 20 === 0) console.log(`  设备进度: ${i}/${deviceCount}`);
  }
  console.log(`✅ 创建 ${devices.length} 个设备`);

  // 3. 批量创建用户
  const users = [];
  for (let i = 0; i < userCount; i++) {
    const email = `perf-user-${ts}-${i}@test.com`;
    const resp = http.post(`${BASE}/api/users`, JSON.stringify({
      username: `perf-user-${ts}-${i}`,
      password: 'P@ssw0rd',
      email,
      name: `压测用户${i}`,
    }), { headers });

    if (resp.status === 200) {
      try {
        users.push({ id: JSON.parse(resp.body).data.id, email });
      } catch (_) { /* 忽略 */ }
    }
    if (i % 10 === 0) console.log(`  用户进度: ${i}/${userCount}`);
  }
  console.log(`✅ 创建 ${users.length} 个用户`);

  return {
    token: auth.accessToken,
    devices,
    users,
    timestamp: ts,
  };
}

/**
 * 压测环境记录（保留数据用于趋势对比，不主动删除）
 */
export function cleanupPerfEnvironment(data) {
  if (!data || data.error) return;
  console.log(`📊 k6 teardown: 压测数据保留用于趋势分析`);
  console.log(`  设备数: ${data.devices?.length || 0}`);
  console.log(`  用户数: ${data.users?.length || 0}`);
  console.log(`  时间戳: ${data.timestamp}`);
  // 压测数据保留 30 天，月度手动清理
}
