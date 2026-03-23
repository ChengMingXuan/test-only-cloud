/**
 * k6 测试用 Mock HTTP 服务器
 * 
 * 双模兼容：
 *   - CI / Mock 模式：在 k6 执行前启动此服务器，k6 连接 localhost:8000
 *   - 真实模式：不启动此服务器，k6 直连真实网关
 * 
 * 用法：node mock-server.js [port]   (默认 8000)
 *       CI 中：node mock-server.js & k6 run scenarios/smoke-test.js
 */
const http = require('http');

const PORT = parseInt(process.argv[2] || process.env.MOCK_PORT || '8000', 10);
let _server = null;

// ═══════════════════════════════════════════════════════════
// Mock API 响应
// ═══════════════════════════════════════════════════════════
const MOCK_TOKEN = 'mock-k6-jwt-token-for-testing';
const MOCK_REFRESH = 'mock-k6-refresh-token';

const API_RESPONSES = {
  'POST /api/auth/login': {
    success: true, code: '200', data: {
      accessToken: MOCK_TOKEN,
      refreshToken: MOCK_REFRESH,
      user: { id: 'u001', name: '管理员', role: 'admin' },
    }
  },
  'POST /api/auth/logout': { success: true, code: '200', data: null },
  'POST /api/auth/refresh': {
    success: true, code: '200', data: { accessToken: MOCK_TOKEN }
  },
  'GET /api/user/profile': {
    success: true, code: '200', data: {
      id: 'u001', name: '管理员', email: 'admin@jgsy.com', role: 'admin',
      tenantId: 't001', tenantName: '演示租户',
    }
  },
  'GET /health': { status: 'healthy', uptime: 99999 },
};

// 通用分页列表 Mock
function pagedResponse(resource) {
  return {
    success: true, code: '200', data: {
      items: [
        { id: `${resource}-1`, name: `${resource} A`, status: 'active', code: `${resource.toUpperCase()}_001` },
        { id: `${resource}-2`, name: `${resource} B`, status: 'active', code: `${resource.toUpperCase()}_002` },
        { id: `${resource}-3`, name: `${resource} C`, status: 'inactive', code: `${resource.toUpperCase()}_003` },
      ],
      total: 100, page: 1, pageSize: 10,
    }
  };
}

// ═══════════════════════════════════════════════════════════
// HTTP 请求处理
// ═══════════════════════════════════════════════════════════
function handleRequest(req, res) {
  const url = new URL(req.url, `http://localhost:${PORT}`);
  const pathname = url.pathname;
  const method = req.method;
  const key = `${method} ${pathname}`;

  // CORS
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET,POST,PUT,DELETE,OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type,Authorization');

  if (method === 'OPTIONS') {
    res.writeHead(204);
    res.end();
    return;
  }

  // 精确匹配
  if (API_RESPONSES[key]) {
    res.writeHead(200, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify(API_RESPONSES[key]));
    return;
  }

  // API 泛匹配
  if (pathname.startsWith('/api/')) {
    // 从 URL 推断资源类型，返回分页列表
    const parts = pathname.split('/').filter(Boolean);
    const resource = parts[1] || 'item'; // /api/stations → stations
    res.writeHead(200, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify(pagedResponse(resource)));
    return;
  }

  // 健康检查
  if (pathname === '/health' || pathname === '/healthz') {
    res.writeHead(200, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify({ status: 'healthy' }));
    return;
  }

  // 兜底
  res.writeHead(200, { 'Content-Type': 'application/json' });
  res.end(JSON.stringify({ success: true, code: '200', data: null }));
}

// ═══════════════════════════════════════════════════════════
// 启动/停止
// ═══════════════════════════════════════════════════════════
function start(port) {
  const p = port || PORT;
  return new Promise((resolve, reject) => {
    _server = http.createServer(handleRequest);
    _server.listen(p, '127.0.0.1', () => {
      console.log(`✅ [k6 mock-server] 已启动: http://127.0.0.1:${p}`);
      resolve(_server);
    });
    _server.on('error', (err) => {
      if (err.code === 'EADDRINUSE') {
        console.log(`⚠️  [k6 mock-server] 端口 ${p} 已被占用，复用现有服务`);
        _server = null;
        resolve(null);
      } else {
        reject(err);
      }
    });
  });
}

function stop() {
  if (_server) {
    _server.close();
    _server = null;
    console.log('🛑 [k6 mock-server] 已停止');
  }
}

// 直接运行时自动启动
if (require.main === module) {
  start().then(() => {
    console.log('[k6 mock-server] 按 Ctrl+C 停止');
  }).catch(err => {
    console.error('[k6 mock-server] 启动失败:', err);
    process.exit(1);
  });
  process.on('SIGINT', () => { stop(); process.exit(0); });
  process.on('SIGTERM', () => { stop(); process.exit(0); });
}

module.exports = { start, stop, PORT };
