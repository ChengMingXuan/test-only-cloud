/**
 * 区块链 Failover API 轻量 Mock 服务器
 * 供 k6 性能测试使用，模拟真实服务响应特征
 * 运行: node mock_server.js
 */

const http = require('http');
const crypto = require('crypto');

// 有状态服务上下文
const state = {
  activeChain: 'ChainMaker',
  activeNode: 'node-A-primary',
  isLocked: false,
  failoverCount: 0,
  nodes: {
    'node-A-primary': { available: true, callCount: 0 },
    'node-B-slave':   { available: true, callCount: 0 },
    'node-C-dr':      { available: true, callCount: 0 },
  },
};

const VALID_CHAINS = new Set(['ChainMaker', 'FISCO', 'Hyperchain']);
const PORT = process.env.PORT || 9021;

function uuid() {
  return crypto.randomUUID();
}

function sendJson(res, status, body) {
  const json = JSON.stringify(body);
  res.writeHead(status, {
    'Content-Type': 'application/json',
    'Content-Length': Buffer.byteLength(json),
  });
  res.end(json);
}

function hasAuth(req) {
  const h = req.headers['authorization'] || '';
  return h.startsWith('Bearer ');
}

function readBody(req) {
  return new Promise((resolve) => {
    let data = '';
    req.on('data', c => data += c);
    req.on('end', () => {
      try { resolve(JSON.parse(data || '{}')); }
      catch { resolve({}); }
    });
  });
}

const server = http.createServer(async (req, res) => {
  const url = req.url.split('?')[0];
  const method = req.method;

  // ---- 健康检查（无需认证）----
  if (url === '/health' || url === '/api/blockchain/health') {
    return sendJson(res, 200, {
      status: 'Healthy',
      data: {
        chains: { ChainMaker: 'Healthy', FISCO: 'Healthy', Hyperchain: 'Healthy' },
        nodes: state.nodes,
      },
    });
  }

  // ---- 要求认证 ----
  if (!hasAuth(req)) {
    return sendJson(res, 401, { code: 401, message: 'Unauthorized' });
  }

  // GET /api/blockchain/failover/status
  if (method === 'GET' && url === '/api/blockchain/failover/status') {
    return sendJson(res, 200, {
      code: 200, message: 'success',
      data: {
        activeChain: state.activeChain,
        activeNode:  state.activeNode,
        isLocked:    state.isLocked,
        failoverCount: state.failoverCount,
        nodes:       state.nodes,
      },
    });
  }

  // POST /api/blockchain/failover/switch-chain
  if (method === 'POST' && url === '/api/blockchain/failover/switch-chain') {
    const body = await readBody(req);
    const target = body.targetChain || '';
    if (!VALID_CHAINS.has(target)) {
      return sendJson(res, 400, { code: 400, message: `不支持的链类型: ${target}` });
    }
    const prev = state.activeChain;
    state.activeChain = target;
    state.isLocked = true;
    state.failoverCount++;
    return sendJson(res, 200, {
      code: 200,
      data: { success: true, previousChain: prev, currentChain: target, message: `切换到 ${target}` },
    });
  }

  // POST /api/blockchain/failover/switch-node
  if (method === 'POST' && url === '/api/blockchain/failover/switch-node') {
    const body = await readBody(req);
    const node = body.nodeName || '';
    if (!state.nodes[node]) {
      return sendJson(res, 400, { code: 400, message: `节点不存在: ${node}` });
    }
    const prev = state.activeNode;
    state.activeNode = node;
    state.nodes[node].callCount++;
    return sendJson(res, 200, {
      code: 200,
      data: { success: true, previousNode: prev, currentNode: node },
    });
  }

  // POST /api/blockchain/failover/reset
  if (method === 'POST' && url === '/api/blockchain/failover/reset') {
    const prev = state.activeChain;
    state.activeChain = 'ChainMaker';
    state.activeNode  = 'node-A-primary';
    state.isLocked    = false;
    return sendJson(res, 200, {
      code: 200,
      data: { success: true, previousChain: prev, currentChain: 'ChainMaker', message: '已重置到默认链' },
    });
  }

  // 默认 404
  sendJson(res, 404, { code: 404, message: `Route not found: ${method} ${url}` });
});

server.listen(PORT, () => {
  console.log(`[mock-blockchain] 服务已启动 http://localhost:${PORT}`);
  console.log(`  GET  /api/blockchain/failover/status`);
  console.log(`  POST /api/blockchain/failover/switch-chain`);
  console.log(`  POST /api/blockchain/failover/switch-node`);
  console.log(`  POST /api/blockchain/failover/reset`);
  console.log(`  GET  /api/blockchain/health`);
});
