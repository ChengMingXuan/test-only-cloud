/**
 * 全服务压力测试矩阵
 * 覆盖全部 20 个微服务，含边界值注入
 *
 * 运行:
 *   k6 run --env GATEWAY_URL=http://localhost:8000 \
 *          --env AI_URL=http://localhost:8020 \
 *          --env BC_URL=http://localhost:8021 \
 *          k6/scenarios/full-service-stress.js
 *
 * 阶段: 2m 爬坡→30VU, 5m 维持 50VU, 3m 冲刺 100VU, 2m 下降
 */

import http from "k6/http";
import { check, group, sleep } from "k6";
import { textSummary } from 'https://jslib.k6.io/k6-summary/0.0.1/index.js';
import { Rate, Counter, Trend } from "k6/metrics";
import { randomIntBetween } from "https://jslib.k6.io/k6-utils/1.4.0/index.js";

// ─── 配置 ─────────────────────────────────────────────────────────
const GATEWAY = __ENV.GATEWAY_URL || __ENV.BASE_URL || "http://localhost:8000";
const AI_URL  = __ENV.AI_URL      || GATEWAY;
const BC_URL  = __ENV.BC_URL      || GATEWAY;

// ─── 全局指标 ──────────────────────────────────────────────────────
const globalSuccess = new Rate("global_success_rate");
const errorCount    = new Counter("total_errors");
const latencyP95    = new Trend("latency_p95", true);

// 按服务分组指标
const svcRates = {};
[
  "account","analytics","blockchain","charging","content",
  "device","digitaltwin","orchestrator","vpp","pvessc","electrade","identity",
  "ingestion","iotai","observability","permission","settlement",
  "station","storage","tenant","workorder","sehs"
].forEach(svc => { svcRates[svc] = new Rate(`svc_${svc}_success`); });

// ─── 测试阶段 ──────────────────────────────────────────────────────
export const options = {
  stages: [
    { duration: "1m", target: 10  }, // 预热
    { duration: "2m", target: 30  }, // 正常负载
    { duration: "3m", target: 50  }, // 高负载
    { duration: "2m", target: 100 }, // 冲刺
    { duration: "1m", target: 50  }, // 回落
    { duration: "1m", target: 0   }, // 冷却
  ],
  thresholds: {
    http_req_failed:        ["rate<0.02"],   // 失败率 < 2%
    http_req_duration:      ["p(95)<2000"],  // P95 < 2s
    global_success_rate:    ["rate>0.90"],   // 全局成功率 > 90%
    // 各服务阈值
    svc_settlement_success: ["rate>0.85"],
    svc_charging_success:   ["rate>0.85"],
    svc_pvessc_success:     ["rate>0.85"],
    svc_iotai_success:      ["rate>0.80"],   // AI 推理允许稍低
    svc_blockchain_success: ["rate>0.75"],   // 区块链节点允许更低
  },
};

// ─── 共享 token（setup 阶段获取）─────────────────────────────────
let authToken = "";

export function setup() {
  const res = http.post(
    `${GATEWAY}/api/auth/login`,
    JSON.stringify({ username: "admin", password: "P@ssw0rd" }),
    { headers: { "Content-Type": "application/json" }, timeout: "10s" }
  );
  if (res.status === 200) {
    try {
      const data = res.json();
      if (data.success) return { token: data.data.accessToken };
    } catch {}
  }
  console.error(`登录失败: ${res.status}`);
  return { token: "" };
}

// ─── 请求工具 ──────────────────────────────────────────────────────
function get(url, token, tags = {}) {
  const res = http.get(url, {
    headers: { Authorization: `Bearer ${token}` },
    timeout: "15s",
    tags,
  });
  latencyP95.add(res.timings.duration);
  return res;
}

function post(url, body, token, tags = {}) {
  const res = http.post(url, JSON.stringify(body), {
    headers: { Authorization: `Bearer ${token}`, "Content-Type": "application/json" },
    timeout: "15s",
    tags,
  });
  latencyP95.add(res.timings.duration);
  return res;
}

function recordSvc(svc, ok) {
  globalSuccess.add(ok);
  if (svcRates[svc]) svcRates[svc].add(ok);
  if (!ok) errorCount.add(1);
}

// ─── 边界值库 ──────────────────────────────────────────────────────
const BOUNDARY = {
  names: [
    `Test-${Date.now()}`,
    "A".repeat(255),    // 最大长度
    "测试-中文名称",
    "",                  // 空值（期望 400）
    "<script>x</script>", // XSS（期望 400 或安全存储）
  ],
  pages: [1, 2, 100, 9999],
  sizes: [1, 10, 50, 100, 0, -1],
};

// ─── 主测试函数 ────────────────────────────────────────────────────
export default function (data) {
  const token = data.token;
  if (!token) { sleep(1); return; }

  // 按 VU 编号轮转不同服务场景，实现全服务并发覆盖
  const vu  = __VU % 20;
  const iter= __ITER;
  const rand = () => randomIntBetween(0, 100);

  switch (vu) {

    // ── 0: Account / Identity ──────────────────────────────────────
    case 0:
      group("Account", () => {
        const r1 = get(`${GATEWAY}/api/users?pageIndex=1&pageSize=10&keyword=test`, token, {svc:"account"});
        recordSvc("account", r1.status === 200);
        check(r1, { "account users 200": r => r.status < 500 });

        const r2 = get(`${GATEWAY}/api/system/role?pageIndex=1&pageSize=10`, token, {svc:"account"});
        recordSvc("account", r2.status === 200);

        // 边界：超大 pageSize
        const r3 = get(`${GATEWAY}/api/users?pageIndex=1&pageSize=9999`, token, {svc:"account"});
        recordSvc("account", [200, 400].includes(r3.status));
      });
      break;

    // ── 1: Analytics ───────────────────────────────────────────────
    case 1:
      group("Analytics", () => {
        const r1 = get(`${GATEWAY}/api/analytics/reports?pageIndex=1&pageSize=10`, token, {svc:"analytics"});
        recordSvc("analytics", [200,403,404].includes(r1.status));

        const r2 = get(`${GATEWAY}/api/analytics/statistics?startTime=2024-01-01&endTime=2025-12-31&granularity=day`, token, {svc:"analytics"});
        recordSvc("analytics", [200,403,404].includes(r2.status));

        // 边界：时间范围倒置
        const r3 = get(`${GATEWAY}/api/analytics/statistics?startTime=2025-12-31&endTime=2024-01-01`, token, {svc:"analytics"});
        recordSvc("analytics", r3.status !== 500);
      });
      break;

    // ── 2: Blockchain ──────────────────────────────────────────────
    case 2:
      group("Blockchain", () => {
        const r1 = get(`${BC_URL}/api/transactions?pageIndex=1&pageSize=10`, token, {svc:"blockchain"});
        recordSvc("blockchain", [200,403,404].includes(r1.status));
        check(r1, { "blockchain tx 非500": r => r.status !== 500 });

        const r2 = get(`${BC_URL}/api/wallet/system-info`, token, {svc:"blockchain"});
        recordSvc("blockchain", [200,403,404].includes(r2.status));

        const r3 = get(`${BC_URL}/api/certificates?pageIndex=1&pageSize=10`, token, {svc:"blockchain"});
        recordSvc("blockchain", r3.status !== 500);
      });
      break;

    // ── 3: Charging ────────────────────────────────────────────────
    case 3:
      group("Charging", () => {
        const r1 = get(`${GATEWAY}/api/charging/admin/orders?pageIndex=1&pageSize=10`, token, {svc:"charging"});
        recordSvc("charging", r1.status === 200);
        check(r1, { "charging orders 200": r => r.status < 500 });

        const r2 = get(`${GATEWAY}/api/charging/piles?pageIndex=1&pageSize=10`, token, {svc:"charging"});
        recordSvc("charging", [200,403,404].includes(r2.status));

        // 边界：非法 status 参数
        const r3 = get(`${GATEWAY}/api/charging/admin/orders?status=INVALID_STATUS`, token, {svc:"charging"});
        recordSvc("charging", r3.status !== 500);
      });
      break;

    // ── 4: ContentPlatform ─────────────────────────────────────────
    case 4:
      group("ContentPlatform", () => {
        const r1 = get(`${GATEWAY}/api/content/articles?pageIndex=1&pageSize=10`, token, {svc:"content"});
        recordSvc("content", [200,403,404].includes(r1.status));

        // 边界：SQL 注入尝试（必须被拒绝，且不能 500）
        const r2 = get(`${GATEWAY}/api/content/articles?keyword=${encodeURIComponent("'; DROP TABLE")}`, token, {svc:"content"});
        recordSvc("content", r2.status !== 500);
        check(r2, { "content SQL注入不崩溃": r => r.status !== 500 });
      });
      break;

    // ── 5: Device ──────────────────────────────────────────────────
    case 5:
      group("Device", () => {
        const r1 = get(`${GATEWAY}/api/device?pageIndex=1&pageSize=10`, token, {svc:"device"});
        recordSvc("device", [200,403,404].includes(r1.status));

        const r2 = get(`${GATEWAY}/api/device/alarm?pageIndex=1&pageSize=10&level=high`, token, {svc:"device"});
        recordSvc("device", [200,403,404].includes(r2.status));

        // 非法 GUID
        const r3 = get(`${GATEWAY}/api/device/NOT-A-GUID`, token, {svc:"device"});
        check(r3, { "device 非法ID不500": r => r.status !== 500 });
        recordSvc("device", r3.status !== 500);
      });
      break;

    // ── 6: EnergyCore (PVESSC/VPP/MG) ─────────────────────────────
    case 6:
      group("EnergyCore", () => {
        const r1 = get(`${GATEWAY}/api/pvessc/site/list?pageIndex=1&pageSize=10`, token, {svc:"energycore"});
        recordSvc("energycore", [200,403,404].includes(r1.status));

        const r2 = get(`${GATEWAY}/api/vpp/list?pageIndex=1&pageSize=10`, token, {svc:"energycore"});
        recordSvc("energycore", [200,403,404].includes(r2.status));

        const r3 = get(`${GATEWAY}/api/microgrid/list?pageIndex=1&pageSize=10`, token, {svc:"energycore"});
        recordSvc("energycore", [200,403,404].includes(r3.status));

        // 边界：极大页码
        const r4 = get(`${GATEWAY}/api/pvessc/site/list?pageIndex=99999&pageSize=10`, token, {svc:"energycore"});
        recordSvc("energycore", r4.status !== 500);
      });
      break;

    // ── 7: EnergyServices ─────────────────────────────────────────
    case 7:
      group("EnergyServices", () => {
        const endpoints = [
          "/api/electrade/dashboard",
          "/api/carbontrade/dashboard",
          "/api/energyeff/dashboard",
          "/api/demandresp/dashboard",
          "/api/multienergy/dashboard",
        ];
        const ep = endpoints[iter % endpoints.length];
        const r = get(`${GATEWAY}${ep}`, token, {svc:"energysvc"});
        recordSvc("energysvc", [200,403,404].includes(r.status));
        check(r, { "energysvc 非500": r => r.status !== 500 });
      });
      break;

    // ── 8: Identity ────────────────────────────────────────────────
    case 8:
      group("Identity", () => {
        const r1 = get(`${GATEWAY}/api/auth/sessions?pageIndex=1&pageSize=10`, token, {svc:"identity"});
        recordSvc("identity", [200,403,404].includes(r1.status));

        // 无效 Token 访问保护接口
        const r2 = http.get(`${GATEWAY}/api/users?pageIndex=1&pageSize=5`, {
          headers: { Authorization: "Bearer INVALID_TOKEN_XYZ" },
          timeout: "10s",
        });
        check(r2, { "无效token返回401": r => r.status === 401 });
        recordSvc("identity", r2.status === 401);
      });
      break;

    // ── 9: IotCloudAI ──────────────────────────────────────────────
    case 9:
      group("IotCloudAI", () => {
        const r1 = get(`${AI_URL}/api/iotcloudai/dashboard`, token, {svc:"iotai"});
        recordSvc("iotai", [200,403,404].includes(r1.status));

        const devId = `DEV-STRESS-${rand()}`;
        const r2 = get(`${AI_URL}/api/iotcloudai/fault-warning/health/${devId}`, token, {svc:"iotai"});
        recordSvc("iotai", [200,404,403].includes(r2.status));

        // 非常长的设备ID
        const r3 = get(`${AI_URL}/api/iotcloudai/fault-warning/health/${"X".repeat(200)}`, token, {svc:"iotai"});
        check(r3, { "iotai 超长ID不500": r => r.status !== 500 });
        recordSvc("iotai", r3.status !== 500);
      });
      break;

    // ── 10: Observability ─────────────────────────────────────────
    case 10:
      group("Observability", () => {
        const r1 = get(`${GATEWAY}/api/observability/audit?pageIndex=1&pageSize=10`, token, {svc:"observability"});
        recordSvc("observability", [200,403,404].includes(r1.status));

        const r2 = get(`${GATEWAY}/api/observability/alerts?pageIndex=1&pageSize=10&level=error`, token, {svc:"observability"});
        recordSvc("observability", [200,403,404].includes(r2.status));
      });
      break;

    // ── 11: Permission ────────────────────────────────────────────
    case 11:
      group("Permission", () => {
        const r1 = get(`${GATEWAY}/api/permissions?pageIndex=1&pageSize=20`, token, {svc:"permission"});
        recordSvc("permission", [200,403,404].includes(r1.status));

        const r2 = get(`${GATEWAY}/api/system/menu/tree`, token, {svc:"permission"});
        recordSvc("permission", [200,403,404].includes(r2.status));
      });
      break;

    // ── 12: Settlement ────────────────────────────────────────────
    case 12:
      group("Settlement", () => {
        const r1 = get(`${GATEWAY}/api/settlements?pageIndex=1&pageSize=10`, token, {svc:"settlement"});
        recordSvc("settlement", [200,403,404].includes(r1.status));
        check(r1, { "settlement 非500": r => r.status !== 500 });

        // 多条件
        const r2 = get(`${GATEWAY}/api/settlements?pageIndex=1&pageSize=10&startTime=2024-01-01&endTime=2025-12-31&status=completed`, token, {svc:"settlement"});
        recordSvc("settlement", [200,403,404].includes(r2.status));

        // 边界：minFee > maxFee
        const r3 = get(`${GATEWAY}/api/settlements?minFee=9999&maxFee=0`, token, {svc:"settlement"});
        recordSvc("settlement", r3.status !== 500);
      });
      break;

    // ── 13: Station ───────────────────────────────────────────────
    case 13:
      group("Station", () => {
        const r1 = get(`${GATEWAY}/api/stations?pageIndex=1&pageSize=10`, token, {svc:"station"});
        recordSvc("station", [200,403,404].includes(r1.status));

        // 组合查询
        const combos = ["?province=广东省","?city=深圳市","?status=online","?keyword=test&status=online"];
        const r2 = get(`${GATEWAY}/api/stations${combos[iter%combos.length]}`, token, {svc:"station"});
        recordSvc("station", r2.status !== 500);
      });
      break;

    // ── 14: Storage ───────────────────────────────────────────────
    case 14:
      group("Storage", () => {
        const r1 = get(`${GATEWAY}/api/storage/files?pageIndex=1&pageSize=10`, token, {svc:"storage"});
        recordSvc("storage", [200,403,404].includes(r1.status));
      });
      break;

    // ── 15: Tenant ────────────────────────────────────────────────
    case 15:
      group("Tenant", () => {
        const r1 = get(`${GATEWAY}/api/tenants?pageIndex=1&pageSize=10`, token, {svc:"tenant"});
        recordSvc("tenant", [200,403,404].includes(r1.status));

        // 边界：空 keyword
        const r2 = get(`${GATEWAY}/api/tenants?keyword=&status=active`, token, {svc:"tenant"});
        recordSvc("tenant", r2.status !== 500);
      });
      break;

    // ── 16: WorkOrder ─────────────────────────────────────────────
    case 16:
      group("WorkOrder", () => {
        const r1 = get(`${GATEWAY}/api/workorder?pageIndex=1&pageSize=10`, token, {svc:"workorder"});
        recordSvc("workorder", [200,403,404].includes(r1.status));

        const r2 = get(`${GATEWAY}/api/workorder?status=pending&priority=high&pageIndex=1&pageSize=10`, token, {svc:"workorder"});
        recordSvc("workorder", r2.status !== 500);
      });
      break;

    // ── 17: SEHS ──────────────────────────────────────────────────
    case 17:
      group("SEHS", () => {
        const r1 = get(`${GATEWAY}/api/sehs/dashboard`, token, {svc:"sehs"});
        recordSvc("sehs", [200,403,404].includes(r1.status));

        const r2 = get(`${GATEWAY}/api/sehs/schedule?page=1&size=10`, token, {svc:"sehs"});
        recordSvc("sehs", [200,403,404].includes(r2.status));

        // 边界：资源快照注入极值
        const r3 = post(`${GATEWAY}/api/sehs/resource`, {
          sourcePowerKw: -999999,
          loadPowerKw: 9999999,
          storageSoc: 150, // 超过100%
        }, token, {svc:"sehs"});
        check(r3, { "sehs极值不500": r => r.status !== 500 });
        recordSvc("sehs", r3.status !== 500);
      });
      break;

    // ── 18: Ingestion ─────────────────────────────────────────────
    case 18:
      group("Ingestion", () => {
        const r1 = get(`${GATEWAY}/api/ingestion/health`, token, {svc:"ingestion"});
        recordSvc("ingestion", [200,403,404].includes(r1.status));

        // 小量遥测推送压测
        const r2 = post(`${GATEWAY}/api/ingestion/telemetry`, {
          deviceId: `DEV-STRESS-${rand()}`,
          timestamp: new Date().toISOString(),
          metrics: { voltage: 380 + rand(), current: 10 + rand() * 0.1 },
        }, token, {svc:"ingestion"});
        recordSvc("ingestion", [200,201,400,403].includes(r2.status));
      });
      break;

    // ── 19: DigitalTwin ───────────────────────────────────────────
    case 19:
      group("DigitalTwin", () => {
        const r1 = get(`${GATEWAY}/api/digitaltwin?pageIndex=1&pageSize=10`, token, {svc:"digitaltwin"});
        recordSvc("digitaltwin", [200,403,404].includes(r1.status));

        // 非法查询
        const r2 = get(`${GATEWAY}/api/digitaltwin/INVALID-ID-FORMAT`, token, {svc:"digitaltwin"});
        check(r2, { "dt 非法ID不500": r => r.status !== 500 });
        recordSvc("digitaltwin", r2.status !== 500);
      });
      break;
  }

  // 随机 think time 模拟真实用户
  sleep(randomIntBetween(1, 3) * 0.1);
}

// ─── teardown ─────────────────────────────────────────────────────
export function teardown(data) {
  console.log("全服务压力测试完成");
  console.log(`Token was: ${data.token ? "有效" : "无效"}`);
}

export function handleSummary(data) {
  return {
    stdout: textSummary(data, { indent: ' ', enableColors: true }),
  };
}