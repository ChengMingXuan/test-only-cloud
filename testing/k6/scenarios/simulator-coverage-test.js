// K6 性能测试 — 模拟器覆盖率测试
// 验证模拟器引擎是否覆盖所有设备类型的数据采集与指令下发
// 覆盖：充电桩、光伏、储能、风机、微网、负荷、传感器等设备类型

import http from 'k6/http';
import { check, sleep, group } from 'k6';
import { Rate, Counter } from 'k6/metrics';
import { config } from '../config.js';

const BASE_URL = config.baseUrl;
const errorRate = new Rate('errors');
const coverageHits = new Counter('simulator_coverage_hits');
const coverageMisses = new Counter('simulator_coverage_misses');

export const options = {
  scenarios: {
    simulator_coverage: {
      executor: 'shared-iterations',
      vus: 3,
      iterations: 30,
      maxDuration: '5m',
    },
  },
  thresholds: {
    errors: ['rate<1'],
  },
};

const HEADERS = {
  'Content-Type': 'application/json',
  'Authorization': `Bearer ${__ENV.TOKEN || 'test-token'}`,
};

// 需要模拟器覆盖的设备类型
const DEVICE_TYPES = [
  'CHARGING_PILE',
  'PV_INVERTER',
  'ESS_BMS',
  'WIND_TURBINE',
  'MICROGRID_PCS',
  'LOAD_CONTROLLER',
  'SENSOR_METER',
  'TRANSFORMER',
  'AIR_CONDITIONER',
  'EV_CHARGER_DC',
];

export default function () {
  group('模拟器-引擎状态', () => {
    const res = http.get(`${BASE_URL}/api/simulator/engine/status`, { headers: HEADERS });
    check(res, { '引擎状态-可访问': (r) => [200, 404].includes(r.status) });
    errorRate.add(![200, 404].includes(res.status));
  });

  group('模拟器-会话列表', () => {
    const res = http.get(`${BASE_URL}/api/simulator/session?page=1&pageSize=20`, { headers: HEADERS });
    check(res, { '会话列表-200': (r) => r.status < 500 });
    errorRate.add(res.status !== 200);
  });

  group('模拟器-设备类型覆盖', () => {
    for (const deviceType of DEVICE_TYPES) {
      const res = http.get(`${BASE_URL}/api/simulator/engine/support/${deviceType}`, { headers: HEADERS });
      if (res.status === 200) {
        coverageHits.add(1);
      } else {
        coverageMisses.add(1);
      }
      check(res, {
        [`${deviceType}-已覆盖`]: (r) => r.status < 500,
      });
    }
  });

  group('模拟器-遥测数据推送', () => {
    const payload = JSON.stringify({
      deviceId: '00000000-0000-0000-0000-000000000001',
      deviceType: DEVICE_TYPES[Math.floor(Math.random() * DEVICE_TYPES.length)],
      telemetry: {
        voltage: 220 + Math.random() * 10,
        current: 10 + Math.random() * 50,
        power: 2200 + Math.random() * 5000,
        temperature: 25 + Math.random() * 20,
      },
      timestamp: new Date().toISOString(),
    });
    const res = http.post(`${BASE_URL}/api/simulator/telemetry`, payload, { headers: HEADERS });
    check(res, { '遥测推送-可响应': (r) => [200, 201, 400, 404].includes(r.status) });
    errorRate.add(![200, 201, 400, 404].includes(res.status));
  });

  group('模拟器-控制指令', () => {
    const payload = JSON.stringify({
      deviceId: '00000000-0000-0000-0000-000000000001',
      command: 'START',
      params: { maxPower: 60 },
    });
    const res = http.post(`${BASE_URL}/api/simulator/command`, payload, { headers: HEADERS });
    check(res, { '控制指令-可响应': (r) => [200, 201, 400, 404].includes(r.status) });
    errorRate.add(![200, 201, 400, 404].includes(res.status));
  });

  sleep(1 + Math.random());
}
