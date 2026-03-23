/**
 * Playwright API 辅助 — 通过 page.request 与网关交互
 *
 * 所有调用经过 YARP 网关，禁止直连微服务。
 */
import { APIRequestContext } from '@playwright/test';
import SHARED from '../../_shared/constants.json';

const BASE = SHARED.gateway.url;

/** 获取分页列表 */
export async function getPagedList(
  request: APIRequestContext,
  endpoint: string,
  params: Record<string, string | number> = {},
) {
  const query = new URLSearchParams();
  for (const [k, v] of Object.entries(params)) {
    query.set(k, String(v));
  }
  const url = `${BASE}${endpoint}?${query.toString()}`;
  const resp = await request.get(url);
  return resp.json();
}

/** 获取单条记录 */
export async function getById(
  request: APIRequestContext,
  endpoint: string,
  id: string,
) {
  const resp = await request.get(`${BASE}${endpoint}/${id}`);
  return resp.json();
}

/** 创建资源 */
export async function createResource(
  request: APIRequestContext,
  endpoint: string,
  data: Record<string, unknown>,
) {
  const resp = await request.post(`${BASE}${endpoint}`, { data });
  return resp.json();
}

/** 更新资源 */
export async function updateResource(
  request: APIRequestContext,
  endpoint: string,
  id: string,
  data: Record<string, unknown>,
) {
  const resp = await request.put(`${BASE}${endpoint}/${id}`, { data });
  return resp.json();
}

/** 删除资源 */
export async function deleteResource(
  request: APIRequestContext,
  endpoint: string,
  id: string,
) {
  const resp = await request.delete(`${BASE}${endpoint}/${id}`);
  return resp.json();
}
