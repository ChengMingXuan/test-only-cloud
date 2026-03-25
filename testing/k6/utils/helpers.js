// Helper utilities for K6 tests

function randomIntBetween(min, max) {
  const lower = Math.ceil(min);
  const upper = Math.floor(max);
  return Math.floor(Math.random() * (upper - lower + 1)) + lower;
}

function randomItem(items) {
  if (!Array.isArray(items) || items.length === 0) {
    return null;
  }

  return items[randomIntBetween(0, items.length - 1)];
}

// 生成随机字符串
export function randomString(length = 10) {
  const chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789';
  let result = '';
  for (let i = 0; i < length; i++) {
    result += chars.charAt(Math.floor(Math.random() * chars.length));
  }
  return result;
}

// 生成随机邮箱
export function randomEmail() {
  return `test_${randomString(8)}@example.com`;
}

// 生成随机手机号
export function randomPhone() {
  return `138${randomIntBetween(10000000, 99999999)}`;
}

// 生成随机日期（过去N天）
export function randomPastDate(daysAgo = 30) {
  const now = new Date();
  const past = new Date(now.getTime() - daysAgo * 24 * 60 * 60 * 1000);
  const randomTime = past.getTime() + Math.random() * (now.getTime() - past.getTime());
  return new Date(randomTime).toISOString();
}

// 生成随机充电记录
export function generateChargingRecord(deviceId, userId) {
  const startTime = randomPastDate(7);
  const duration = randomIntBetween(600, 7200); // 10分钟到2小时
  const endTime = new Date(new Date(startTime).getTime() + duration * 1000).toISOString();
  
  return {
    deviceId: deviceId,
    userId: userId,
    startTime: startTime,
    endTime: endTime,
    energyConsumed: randomIntBetween(5, 80), // 5-80 kWh
    amount: randomIntBetween(10, 200), // 10-200元
    status: randomItem(['completed', 'charging', 'stopped']),
  };
}

// 生成随机设备数据
export function generateDeviceData(deviceId) {
  return {
    deviceId: deviceId,
    timestamp: new Date().toISOString(),
    voltage: randomIntBetween(220, 240),
    current: randomIntBetween(10, 32),
    power: randomIntBetween(2200, 7680),
    temperature: randomIntBetween(20, 45),
    status: randomItem(['idle', 'charging', 'faulted', 'offline']),
  };
}

// 生成随机工单
export function generateWorkOrder(deviceId, userId) {
  return {
    title: `故障工单-${randomString(6)}`,
    description: '设备出现异常，需要维修',
    deviceId: deviceId,
    reporterId: userId,
    priority: randomItem(['low', 'medium', 'high', 'urgent']),
    category: randomItem(['hardware', 'software', 'network', 'power']),
    status: 'pending',
  };
}

// 睡眠（毫秒）
export function sleep(ms) {
  const start = Date.now();
  while (Date.now() - start < ms) {
    // 忙等待
  }
}

// 格式化字节数
export function formatBytes(bytes) {
  if (bytes === 0) return '0 Bytes';
  const k = 1024;
  const sizes = ['Bytes', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
}

// 计算百分位数
export function percentile(arr, p) {
  const sorted = arr.slice().sort((a, b) => a - b);
  const index = Math.ceil(sorted.length * p / 100) - 1;
  return sorted[index];
}

export default {
  randomString,
  randomEmail,
  randomPhone,
  randomPastDate,
  generateChargingRecord,
  generateDeviceData,
  generateWorkOrder,
  sleep,
  formatBytes,
  percentile,
};
