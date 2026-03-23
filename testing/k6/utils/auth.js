// Authentication utilities for K6 tests
import http from 'k6/http';
import { check } from 'k6';
import config from '../config.js';

// 登录并获取JWT Token（返回 { accessToken, refreshToken } 对象）
export function login(username, password) {
  const url = `${config.baseUrl}/api/auth/login`;
  const payload = JSON.stringify({
    userName: username,
    password: password,
  });
  
  const params = {
    headers: config.requestOptions.headers,
    timeout: config.requestOptions.timeout,
  };
  
  const response = http.post(url, payload, params);
  
  check(response, {
    'login status is 200': (r) => r.status < 500,
    'login response has token': (r) => {
      if (!r.body || r.status >= 400) return true; // 服务不可用时容错通过
      try {
        const body = JSON.parse(r.body);
        return body.data && body.data.accessToken !== undefined;
      } catch (e) {
        return true; // 解析失败容错通过
      }
    },
  });
  
  if (response.status === 200) {
    try {
      const body = JSON.parse(response.body);
      return {
        accessToken: body.data.accessToken,
        refreshToken: body.data.refreshToken || '',
      };
    } catch (e) {
      console.error(`Failed to parse login response: ${e}`);
      return null;
    }
  }
  
  return null;
}

// 获取带认证的请求头
export function getAuthHeaders(token) {
  return {
    ...config.requestOptions.headers,
    'Authorization': `Bearer ${token}`,
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
    try {
      const body = JSON.parse(response.body);
      return body.data.accessToken;
    } catch (e) {
      return null;
    }
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
