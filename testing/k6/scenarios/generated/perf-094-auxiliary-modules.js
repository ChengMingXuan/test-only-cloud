/**
 * K6 补充性能测试场景 - 平台辅助模块
 * 覆盖: Help / I18n / OpenPlatform / Builder / Welcome / Ops / Portal / Platform
 * 场景数: 20
 */
import http from 'k6/http';
import { check, sleep } from 'k6';

const BASE_URL = __ENV.BASE_URL || 'http://localhost:8000';
const TOKEN = __ENV.AUTH_TOKEN || 'mock-token';
const HEADERS = { Authorization: `Bearer ${TOKEN}`, 'Content-Type': 'application/json' };

// Help - 帮助中心
export function smoke_help_center() {
  const res = http.get(`${BASE_URL}/api/help/articles`, { headers: HEADERS, tags: { name: 'help_center' } });
  check(res, { 'help articles 200': (r) => r.status < 500 });
  sleep(0.3);
}

export function load_help_search() {
  const res = http.get(`${BASE_URL}/api/help/search?keyword=充电`, { headers: HEADERS, tags: { name: 'help_search' } });
  check(res, { 'help search 200': (r) => r.status < 500 });
  sleep(0.2);
}

// I18n - 国际化
export function smoke_i18n_list() {
  const res = http.get(`${BASE_URL}/api/i18n/languages`, { headers: HEADERS, tags: { name: 'i18n_list' } });
  check(res, { 'i18n languages 200': (r) => r.status < 500 });
  sleep(0.3);
}

export function load_i18n_translations() {
  const res = http.get(`${BASE_URL}/api/i18n/translations?lang=zh-CN`, { headers: HEADERS, tags: { name: 'i18n_trans' } });
  check(res, { 'i18n translations 200': (r) => r.status < 500 });
  sleep(0.2);
}

// OpenPlatform - 开放平台
export function smoke_openplatform_apis() {
  const res = http.get(`${BASE_URL}/api/open-platform/api-keys`, { headers: HEADERS, tags: { name: 'open_apis' } });
  check(res, { 'open platform apis 200': (r) => r.status < 500 });
  sleep(0.3);
}

export function load_openplatform_oauth() {
  const res = http.get(`${BASE_URL}/api/open-platform/oauth/apps`, { headers: HEADERS, tags: { name: 'open_oauth' } });
  check(res, { 'open platform oauth 200': (r) => r.status < 500 });
  sleep(0.2);
}

// Builder - 表单设计器
export function smoke_builder_forms() {
  const res = http.get(`${BASE_URL}/api/builder/forms`, { headers: HEADERS, tags: { name: 'builder_forms' } });
  check(res, { 'builder forms 200': (r) => r.status < 500 });
  sleep(0.3);
}

export function load_builder_preview() {
  const res = http.get(`${BASE_URL}/api/builder/forms/preview/form-001`, { headers: HEADERS, tags: { name: 'builder_preview' } });
  check(res, { 'builder preview 200': (r) => r.status < 500 });
  sleep(0.2);
}

// Welcome - 欢迎页
export function smoke_welcome_stats() {
  const res = http.get(`${BASE_URL}/api/dashboard/welcome/stats`, { headers: HEADERS, tags: { name: 'welcome_stats' } });
  check(res, { 'welcome stats 200': (r) => r.status < 500 });
  sleep(0.3);
}

export function load_welcome_notices() {
  const res = http.get(`${BASE_URL}/api/dashboard/welcome/notices`, { headers: HEADERS, tags: { name: 'welcome_notices' } });
  check(res, { 'welcome notices 200': (r) => r.status < 500 });
  sleep(0.2);
}

// Ops - 运维工具
export function smoke_ops_health() {
  const res = http.get(`${BASE_URL}/api/ops/health`, { headers: HEADERS, tags: { name: 'ops_health' } });
  check(res, { 'ops health 200': (r) => r.status < 500 });
  sleep(0.3);
}

export function load_ops_services() {
  const res = http.get(`${BASE_URL}/api/ops/services/status`, { headers: HEADERS, tags: { name: 'ops_services' } });
  check(res, { 'ops services status 200': (r) => r.status < 500 });
  sleep(0.2);
}

// Portal - 门户
export function smoke_portal_home() {
  const res = http.get(`${BASE_URL}/api/portal/home`, { headers: HEADERS, tags: { name: 'portal_home' } });
  check(res, { 'portal home 200': (r) => r.status < 500 });
  sleep(0.3);
}

export function load_portal_news() {
  const res = http.get(`${BASE_URL}/api/portal/news?page=1&size=10`, { headers: HEADERS, tags: { name: 'portal_news' } });
  check(res, { 'portal news 200': (r) => r.status < 500 });
  sleep(0.2);
}

// Platform - 平台设置
export function smoke_platform_settings() {
  const res = http.get(`${BASE_URL}/api/platform/settings`, { headers: HEADERS, tags: { name: 'platform_settings' } });
  check(res, { 'platform settings 200': (r) => r.status < 500 });
  sleep(0.3);
}

export function load_platform_theme() {
  const res = http.get(`${BASE_URL}/api/platform/theme`, { headers: HEADERS, tags: { name: 'platform_theme' } });
  check(res, { 'platform theme 200': (r) => r.status < 500 });
  sleep(0.2);
}

// Finance - 财务
export function smoke_finance_summary() {
  const res = http.get(`${BASE_URL}/api/finance/summary`, { headers: HEADERS, tags: { name: 'finance_summary' } });
  check(res, { 'finance summary 200': (r) => r.status < 500 });
  sleep(0.3);
}

export function load_finance_transactions() {
  const res = http.get(`${BASE_URL}/api/finance/transactions?page=1&size=20`, { headers: HEADERS, tags: { name: 'finance_trans' } });
  check(res, { 'finance transactions 200': (r) => r.status < 500 });
  sleep(0.2);
}

// Agent - 智能体
export function smoke_agent_list() {
  const res = http.get(`${BASE_URL}/api/agent/list`, { headers: HEADERS, tags: { name: 'agent_list' } });
  check(res, { 'agent list 200': (r) => r.status < 500 });
  sleep(0.3);
}

export function load_agent_status() {
  const res = http.get(`${BASE_URL}/api/agent/status`, { headers: HEADERS, tags: { name: 'agent_status' } });
  check(res, { 'agent status 200': (r) => r.status < 500 });
  sleep(0.2);
}
