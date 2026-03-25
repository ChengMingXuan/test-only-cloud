// Authentication utilities for K6 tests
import http from 'k6/http';
import { check } from 'k6';
import config from '../config.js';

function parseLoginBody(response) {
  if (!response || !response.body) {
    return null;
  }

  try {
    return JSON.parse(response.body);
  } catch (e) {
    console.error(`Failed to parse login response: ${e}`);
    return null;
  }
}

function extractTokenPayload(body) {
  if (!body || typeof body !== 'object') {
    return null;
  }

  const accessToken = body.accessToken || body.token?.accessToken || body.data?.accessToken;
  if (!accessToken) {
    return null;
  }

  return {
    accessToken,
    refreshToken: body.refreshToken || body.token?.refreshToken || body.data?.refreshToken || '',
    expiresIn: body.expiresIn || body.token?.expiresIn || body.data?.expiresIn || 0,
    tenantId: body.user?.tenantId || body.data?.user?.tenantId || null,
    user: body.user || body.data?.user || null,
  };
}

function normalizeAccessToken(token) {
  if (!token) {
    return '';
  }

  if (typeof token === 'string') {
    return token;
  }

  if (typeof token === 'object') {
    return token.accessToken || token.token?.accessToken || token.data?.accessToken || '';
  }

  return '';
}

// 登录并获取JWT Token（返回 { accessToken, refreshToken } 对象）
export function login(username, password) {
  const url = `${config.baseUrl}/api/auth/login`;
  const payload = {
    username,
    password,
  };

  const tenantCode = __ENV.ADMIN_TENANT_CODE || __ENV.TENANT_CODE || '';
  if (tenantCode) {
    payload.tenantCode = tenantCode;
  }
  
  const params = {
    headers: config.requestOptions.headers,
    timeout: config.requestOptions.timeout,
  };
  
  const response = http.post(url, JSON.stringify(payload), params);
  const body = parseLoginBody(response);
  const tokenPayload = extractTokenPayload(body);
  
  check(response, {
    'login status is 200': (r) => r.status === 200,
    'login response has token': (r) => {
      return r.status === 200 && tokenPayload !== null;
    },
  });
  
  if (response.status === 200 && tokenPayload) {
    return tokenPayload;
  }

  const message = body?.message || body?.error || `status=${response.status}`;
  console.error(`Login failed for ${username}: ${message}`);
  
  return null;
}

// 获取带认证的请求头
export function getAuthHeaders(token) {
  const accessToken = normalizeAccessToken(token);
  return {
    ...config.requestOptions.headers,
    'Authorization': `Bearer ${accessToken}`,
  };
}

// 刷新Token
export function refreshToken(refreshToken) {
  const url = `${config.baseUrl}/api/auth/refresh`;
  const payload = JSON.stringify({
    refreshToken: refreshToken,
  });
  
  const params = {
    headers: config.requestOptions.headers,
    timeout: config.requestOptions.timeout,
  };
  
  const response = http.post(url, payload, params);
  
  if (response.status === 200) {
    const body = parseLoginBody(response);
    return body?.accessToken || body?.token?.accessToken || body?.data?.accessToken || null;
  }
  
  return null;
}

// 登出（需要 refreshToken）
export function logout(token, rtToken) {
  const url = `${config.baseUrl}/api/auth/logout`;
  const payload = JSON.stringify({ refreshToken: rtToken || '' });
  const params = {
    headers: getAuthHeaders(token),
    timeout: config.requestOptions.timeout,
  };
  
  const response = http.post(url, payload, params);
  
  check(response, {
    'logout status is 200': (r) => r.status < 500,
  });
  
  return response.status === 200;
}

export default {
  login,
  getAuthHeaders,
  refreshToken,
  logout,
};
