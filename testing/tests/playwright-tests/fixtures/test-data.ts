/**
 * Playwright 测试数据工厂 — 通过 API 创建/清理真实数据
 *
 * 每个测试用 timestamp + uuid 保证数据唯一，afterAll 中清理。
 */
import { APIRequestContext } from '@playwright/test';
import SHARED from '../../_shared/constants.json';

const BASE = SHARED.gateway.url;

/** 生成唯一编码 */
export function uniqueCode(prefix: string): string {
  return `${prefix}-${Date.now()}-${Math.random().toString(36).slice(2, 8)}`;
}

/** 通过 API 创建测试设备（返回 id） */
export async function createTestDevice(
  request: APIRequestContext,
  overrides: Record<string, unknown> = {},
): Promise<string> {
  const resp = await request.post(`${BASE}/api/devices`, {
    data: {
      code: uniqueCode('E2E-DEV'),
      name: 'Playwright 测试设备',
      type: 'charger',
      power: 120,
      ...overrides,
    },
  });
  const body = await resp.json();
  return body.data?.id ?? '';
}

/** 通过 API 创建测试场站（返回 id） */
export async function createTestStation(
  request: APIRequestContext,
  overrides: Record<string, unknown> = {},
): Promise<string> {
  const resp = await request.post(`${BASE}/api/stations`, {
    data: {
      code: uniqueCode('E2E-STA'),
      name: 'Playwright 测试场站',
      address: '自动化测试地址',
      ...overrides,
    },
  });
  const body = await resp.json();
  return body.data?.id ?? '';
}

/** 通过 API 创建测试工单（返回 id） */
export async function createTestWorkOrder(
  request: APIRequestContext,
  overrides: Record<string, unknown> = {},
): Promise<string> {
  const resp = await request.post(`${BASE}/api/workorders`, {
    data: {
      title: `E2E 测试工单 ${Date.now()}`,
      type: 'repair',
      priority: 'normal',
      description: 'Playwright E2E 自动创建',
      ...overrides,
    },
  });
  const body = await resp.json();
  return body.data?.id ?? '';
}

/** 软删除资源 */
export async function cleanupResource(
  request: APIRequestContext,
  endpoint: string,
  id: string,
): Promise<void> {
  if (!id) return;
  await request.delete(`${BASE}${endpoint}/${id}`);
}

/** 批量清理 */
export async function cleanupResources(
  request: APIRequestContext,
  endpoint: string,
  ids: string[],
): Promise<void> {
  for (const id of ids) {
    await cleanupResource(request, endpoint, id);
  }
}
