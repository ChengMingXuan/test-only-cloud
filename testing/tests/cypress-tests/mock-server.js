/**
 * Cypress 测试用 Mock 前端服务器
 * 提供基于 Ant Design Pro 布局的 Mock HTML 页面
 * 所有 API 由 Cypress cy.intercept() 拦截处理
 */
const http = require('http');
const fs = require('fs');
const path = require('path');

const PORT = process.env.MOCK_PORT || 8000;
let server = null;

function getMockHtml() {
  return fs.readFileSync(path.join(__dirname, 'mock-app.html'), 'utf-8');
}

function start() {
  return new Promise((resolve, reject) => {
    server = http.createServer((req, res) => {
      // API 请求返回空（交给 Cypress intercept）
      if (req.url.startsWith('/api/')) {
        res.writeHead(200, { 'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*' });
        res.end(JSON.stringify({ success: true, code: '200', data: null }));
        return;
      }
      // 静态资源
      if (req.url.endsWith('.js') || req.url.endsWith('.css') || req.url.endsWith('.map')) {
        res.writeHead(200, { 'Content-Type': 'text/plain' });
        res.end('');
        return;
      }
      // 所有其他请求返回 mock HTML
      res.writeHead(200, { 'Content-Type': 'text/html; charset=utf-8' });
      res.end(getMockHtml());
    });

    server.listen(PORT, '127.0.0.1', () => {
      console.log(`[mock-server] 已启动: http://127.0.0.1:${PORT}`);
      resolve(server);
    });

    server.on('error', (err) => {
      if (err.code === 'EADDRINUSE') {
        console.log(`[mock-server] 端口 ${PORT} 已被占用，尝试复用`);
        resolve(null);
      } else {
        reject(err);
      }
    });
  });
}

function stop() {
  if (server) {
    server.close();
    server = null;
    console.log('[mock-server] 已停止');
  }
}

// 直接运行时启动服务器
if (require.main === module) {
  start().then(() => {
    console.log('[mock-server] 按 Ctrl+C 停止');
  }).catch(err => {
    console.error('[mock-server] 启动失败:', err);
    process.exit(1);
  });
}

module.exports = { start, stop, PORT };
