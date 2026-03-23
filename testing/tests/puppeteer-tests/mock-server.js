/**
 * Puppeteer 测试用 Mock HTTP 服务器
 * 为渲染/性能测试提供模拟页面响应
 * 符合规范：100% Mock，不连真实后端
 * 
 * 用法: node mock-server.js [port] (默认 3000)
 *       同时在 8000 端口启动镜像（供 pages-render 使用）
 */

const http = require('http');

const PORT = parseInt(process.env.MOCK_PORT || '8000', 10);

// ═══════════════════════════════════════════════════════════
// 模拟 API 响应
// ═══════════════════════════════════════════════════════════
const API_RESPONSES = {
  '/api/auth/login': { code: 200, data: { token: 'mock-jwt-token', refreshToken: 'mock-refresh', user: { id: '1', name: '管理员', role: 'admin' } } },
  '/api/account/login': { code: 200, data: { token: 'mock-jwt-token', user: { id: '1', name: '管理员' } } },
  '/api/account/profile': { code: 200, data: { id: '1', name: '管理员', email: 'admin@test.com' } },
  '/api/device/list': { code: 200, data: { items: [{ id: '1', name: '设备A', status: 'online' }], total: 1 } },
  '/api/station/list': { code: 200, data: { items: [{ id: '1', name: '场站A' }], total: 1 } },
  '/api/permission/menus': { code: 200, data: [{ id: '1', name: '首页', path: '/dashboard' }] },
  '/api/tenant/current': { code: 200, data: { id: '1', name: '默认租户', code: 'demo' } },
  '/health': { status: 'healthy' },
};

// ═══════════════════════════════════════════════════════════
// 模拟页面 HTML（满足 Puppeteer 渲染检查条件）
// ═══════════════════════════════════════════════════════════
function generatePageHTML(path) {
  const pageName = path === '/' ? '首页' : path.replace(/\//g, ' / ').trim();
  return `<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>JGSY AGI Platform - ${pageName}</title>
  <link rel="icon" href="/favicon.ico" type="image/x-icon" />
  <link rel="shortcut icon" href="/favicon.ico" />
  <script src="/umi.js" defer></script>
  <style>
    * { margin: 0; padding: 0; box-sizing: border-box; }
    body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; background: #f0f2f5; }
    .ant-layout { display: flex; min-height: 100vh; }
    .ant-layout-sider { width: 200px; background: #001529; color: #fff; padding: 20px 0; }
    .ant-layout-sider .ant-menu { list-style: none; padding: 0; }
    .ant-layout-sider .ant-menu-item { padding: 12px 24px; color: rgba(255,255,255,0.65); cursor: pointer; }
    .ant-layout-sider .ant-menu-item:hover { color: #fff; background: #1890ff22; }
    .ant-layout-sider .logo { height: 32px; margin: 16px; text-align: center; color: #fff; font-size: 18px; font-weight: bold; }
    .ant-layout-content-wrapper { flex: 1; display: flex; flex-direction: column; }
    .ant-layout-header { background: #fff; height: 48px; line-height: 48px; padding: 0 24px; box-shadow: 0 1px 4px rgba(0,0,0,0.1); display: flex; align-items: center; justify-content: space-between; }
    .ant-layout-content { flex: 1; padding: 24px; margin: 0; }
    .ant-layout-footer { text-align: center; padding: 16px 50px; background: #f0f2f5; color: rgba(0,0,0,0.45); }
    .ant-breadcrumb { margin-bottom: 16px; font-size: 14px; color: rgba(0,0,0,0.45); }
    .ant-breadcrumb a { color: rgba(0,0,0,0.45); }
    .ant-card { background: #fff; border-radius: 2px; box-shadow: 0 1px 2px rgba(0,0,0,0.05); margin-bottom: 16px; }
    .ant-card-head { padding: 0 24px; border-bottom: 1px solid #f0f0f0; min-height: 48px; display: flex; align-items: center; }
    .ant-card-head-title { font-size: 16px; font-weight: 500; }
    .ant-card-body { padding: 24px; }
    .ant-table { width: 100%; border-collapse: collapse; }
    .ant-table th, .ant-table td { padding: 12px 16px; border-bottom: 1px solid #f0f0f0; text-align: left; }
    .ant-table th { background: #fafafa; font-weight: 500; }
    .ant-table-row:hover td { background: #e6f7ff; }
    .ant-btn { display: inline-block; padding: 4px 15px; border: 1px solid #d9d9d9; border-radius: 2px; cursor: pointer; background: #fff; line-height: 1.5; }
    .ant-btn-primary { background: #1890ff; border-color: #1890ff; color: #fff; }
    .ant-input { padding: 4px 11px; border: 1px solid #d9d9d9; border-radius: 2px; line-height: 1.5; width: 200px; }
    .ant-form-item { margin-bottom: 24px; }
    .ant-form-item-label { display: block; margin-bottom: 8px; font-weight: 500; }
    .ant-statistic { text-align: center; }
    .ant-statistic-title { font-size: 14px; color: rgba(0,0,0,0.45); margin-bottom: 4px; }
    .ant-statistic-content { font-size: 24px; font-weight: 600; color: rgba(0,0,0,0.85); }
    .ant-tag { display: inline-block; padding: 0 7px; font-size: 12px; line-height: 20px; border-radius: 2px; border: 1px solid #d9d9d9; background: #fafafa; }
    .ant-tag-green { color: #52c41a; background: #f6ffed; border-color: #b7eb8f; }
    .ant-tag-blue { color: #1890ff; background: #e6f7ff; border-color: #91d5ff; }
    .ant-pagination { display: flex; list-style: none; padding: 0; margin-top: 16px; justify-content: flex-end; gap: 8px; }
    .ant-pagination li { width: 32px; height: 32px; text-align: center; line-height: 32px; border: 1px solid #d9d9d9; border-radius: 2px; cursor: pointer; }
    .ant-pagination .ant-pagination-item-active { border-color: #1890ff; color: #1890ff; }
    .ant-select { position: relative; display: inline-block; }
    .ant-select-selector { padding: 0 11px; border: 1px solid #d9d9d9; border-radius: 2px; min-width: 120px; height: 32px; line-height: 32px; }
    .ant-modal { display: none; }
    .ant-spin { display: none; }
    .ant-empty { text-align: center; padding: 32px; color: rgba(0,0,0,0.25); }
    .ant-alert { padding: 8px 15px; border-radius: 2px; border: 1px solid #91d5ff; background: #e6f7ff; margin-bottom: 16px; }
    .ant-tabs { margin-bottom: 16px; }
    .ant-tabs-nav { display: flex; gap: 0; border-bottom: 1px solid #f0f0f0; }
    .ant-tabs-tab { padding: 12px 16px; cursor: pointer; }
    .ant-tabs-tab-active { color: #1890ff; border-bottom: 2px solid #1890ff; }
    #root { min-height: 100vh; }
    a { color: #1890ff; text-decoration: none; }
    a:hover { color: #40a9ff; }
    h1, h2, h3 { color: rgba(0,0,0,0.85); }
    /* 响应式布局：移动端隐藏侧栏，确保 body 不超过 viewport */
    @media (max-width: 768px) {
      .ant-layout { flex-direction: column; }
      .ant-layout-sider { display: none; }
      .ant-layout-content { padding: 12px; }
      .ant-table { font-size: 12px; }
      .ant-table th, .ant-table td { padding: 6px 8px; }
      div[style*="grid-template-columns"] { grid-template-columns: repeat(2,1fr) !important; }
    }
    @media (max-width: 480px) {
      div[style*="grid-template-columns"] { grid-template-columns: 1fr !important; }
      .ant-input { width: 100%; }
    }
    html, body { max-width: 100vw; overflow-x: hidden; }
  </style>
</head>
<body>
  <div id="root">
    <div class="ant-layout">
      <div class="ant-layout-sider">
        <div class="logo">JGSY AGI</div>
        <ul class="ant-menu">
          <li class="ant-menu-item"><a href="/dashboard">首页概览</a></li>
          <li class="ant-menu-item"><a href="/device">设备管理</a></li>
          <li class="ant-menu-item"><a href="/station">场站管理</a></li>
          <li class="ant-menu-item"><a href="/charging">充电管理</a></li>
          <li class="ant-menu-item"><a href="/energy">能源管理</a></li>
          <li class="ant-menu-item"><a href="/workorder">工单管理</a></li>
          <li class="ant-menu-item"><a href="/settlement">结算管理</a></li>
          <li class="ant-menu-item"><a href="/rule-engine">规则引擎</a></li>
          <li class="ant-menu-item"><a href="/analytics">数据分析</a></li>
          <li class="ant-menu-item"><a href="/permission">权限管理</a></li>
          <li class="ant-menu-item"><a href="/system">系统设置</a></li>
        </ul>
      </div>
      <div class="ant-layout-content-wrapper">
        <div class="ant-layout-header">
          <div class="ant-breadcrumb">
            <a href="/">首页</a> / <span>${pageName}</span>
          </div>
          <div style="display:flex;align-items:center;gap:16px;">
            <span class="ant-tag ant-tag-green">在线</span>
            <span>admin</span>
            <button class="ant-btn" id="logout-btn">退出</button>
          </div>
        </div>
        <div class="ant-layout-content" role="main">
          <h1 style="margin-bottom:24px;">${pageName}</h1>
          <div class="ant-alert">当前页面: ${path}</div>
          <div class="ant-card">
            <div class="ant-card-head">
              <span class="ant-card-head-title">数据概览</span>
            </div>
            <div class="ant-card-body">
              <div style="display:grid;grid-template-columns:repeat(4,1fr);gap:24px;margin-bottom:24px;">
                <div class="ant-statistic"><div class="ant-statistic-title">总数</div><div class="ant-statistic-content">1,234</div></div>
                <div class="ant-statistic"><div class="ant-statistic-title">在线</div><div class="ant-statistic-content">856</div></div>
                <div class="ant-statistic"><div class="ant-statistic-title">告警</div><div class="ant-statistic-content">12</div></div>
                <div class="ant-statistic"><div class="ant-statistic-title">离线</div><div class="ant-statistic-content">366</div></div>
              </div>

              <div class="ant-tabs">
                <div class="ant-tabs-nav">
                  <div class="ant-tabs-tab ant-tabs-tab-active">列表视图</div>
                  <div class="ant-tabs-tab">图表视图</div>
                  <div class="ant-tabs-tab">地图视图</div>
                </div>
              </div>

              <div style="margin-bottom:16px;display:flex;gap:12px;align-items:center;">
                <input type="text" class="ant-input" placeholder="搜索..." id="search-input" />
                <div class="ant-select"><div class="ant-select-selector">全部状态</div></div>
                <button class="ant-btn ant-btn-primary" id="search-btn">查询</button>
                <button class="ant-btn" id="add-btn">新增</button>
                <button class="ant-btn" id="export-btn">导出</button>
              </div>

              <table class="ant-table">
                <thead>
                  <tr>
                    <th>序号</th><th>名称</th><th>编码</th><th>状态</th><th>创建时间</th><th>操作</th>
                  </tr>
                </thead>
                <tbody>
                  <tr class="ant-table-row"><td>1</td><td>测试项目A</td><td>CODE-001</td><td><span class="ant-tag ant-tag-green">正常</span></td><td>2026-03-08</td><td><a href="#">编辑</a> <a href="#">删除</a></td></tr>
                  <tr class="ant-table-row"><td>2</td><td>测试项目B</td><td>CODE-002</td><td><span class="ant-tag ant-tag-blue">待审核</span></td><td>2026-03-07</td><td><a href="#">编辑</a> <a href="#">删除</a></td></tr>
                  <tr class="ant-table-row"><td>3</td><td>测试项目C</td><td>CODE-003</td><td><span class="ant-tag ant-tag-green">正常</span></td><td>2026-03-06</td><td><a href="#">编辑</a> <a href="#">删除</a></td></tr>
                  <tr class="ant-table-row"><td>4</td><td>测试项目D</td><td>CODE-004</td><td><span class="ant-tag">已停用</span></td><td>2026-03-05</td><td><a href="#">编辑</a> <a href="#">删除</a></td></tr>
                  <tr class="ant-table-row"><td>5</td><td>测试项目E</td><td>CODE-005</td><td><span class="ant-tag ant-tag-green">正常</span></td><td>2026-03-04</td><td><a href="#">编辑</a> <a href="#">删除</a></td></tr>
                </tbody>
              </table>

              <ul class="ant-pagination">
                <li>«</li>
                <li class="ant-pagination-item-active">1</li>
                <li>2</li>
                <li>3</li>
                <li>»</li>
              </ul>

              <form style="margin-top:24px;display:none;" id="edit-form">
                <div class="ant-form-item">
                  <label class="ant-form-item-label">名称</label>
                  <input type="text" class="ant-input" name="name" value="测试" />
                </div>
                <div class="ant-form-item">
                  <label class="ant-form-item-label">编码</label>
                  <input type="text" class="ant-input" name="code" value="CODE-001" />
                </div>
                <div class="ant-form-item">
                  <label class="ant-form-item-label">描述</label>
                  <textarea class="ant-input" name="description" style="width:400px;height:80px;">描述内容</textarea>
                </div>
                <button type="submit" class="ant-btn ant-btn-primary">保存</button>
                <button type="button" class="ant-btn">取消</button>
              </form>
            </div>
          </div>
        </div>
        <div class="ant-layout-footer">
          JGSY AGI Platform ©2026 — 智能运维平台
        </div>
      </div>
    </div>
  </div>
  <script>
    // 模拟 localStorage 中的认证状态
    if (!localStorage.getItem('token')) {
      localStorage.setItem('token', 'mock-jwt-token');
      localStorage.setItem('user', JSON.stringify({ id: '1', name: 'admin', role: 'admin' }));
    }
    // 基本的路由导航模拟
    document.querySelectorAll('a').forEach(a => {
      a.addEventListener('click', e => {
        e.preventDefault();
        const href = a.getAttribute('href');
        if (href && href !== '#') {
          window.history.pushState({}, '', href);
          document.querySelector('h1').textContent = href.replace(/\\//g, ' / ').trim() || '首页';
        }
      });
    });
    // 搜索/按钮交互模拟
    const searchBtn = document.getElementById('search-btn');
    if (searchBtn) searchBtn.addEventListener('click', () => {});
    const addBtn = document.getElementById('add-btn');
    if (addBtn) addBtn.addEventListener('click', () => {
      const form = document.getElementById('edit-form');
      if (form) form.style.display = form.style.display === 'none' ? 'block' : 'none';
    });
  </script>
</body>
</html>`;
}

// ═══════════════════════════════════════════════════════════
// HTTP 请求处理
// ═══════════════════════════════════════════════════════════
function handleRequest(req, res) {
  const url = new URL(req.url, `http://localhost`);
  const pathname = url.pathname;

  // API 请求返回 JSON
  if (pathname.startsWith('/api/') || pathname === '/health') {
    res.writeHead(200, {
      'Content-Type': 'application/json',
      'Access-Control-Allow-Origin': '*',
      'Access-Control-Allow-Headers': '*',
      'Access-Control-Allow-Methods': '*',
    });

    if (req.method === 'OPTIONS') {
      res.end();
      return;
    }

    const mockData = API_RESPONSES[pathname] || { code: 200, data: null, message: 'OK' };
    res.end(JSON.stringify(mockData));
    return;
  }

  // 静态资源
  if (pathname.match(/\.(js|css|png|jpg|svg|ico|woff2?)$/)) {
    if (pathname.endsWith('.css')) {
      res.writeHead(200, { 'Content-Type': 'text/css' });
      res.end('body{}');
    } else if (pathname.endsWith('.js')) {
      res.writeHead(200, { 'Content-Type': 'application/javascript' });
      res.end('// mock');
    } else {
      res.writeHead(200, { 'Content-Type': 'application/octet-stream' });
      res.end('');
    }
    return;
  }

  // 页面请求返回 HTML
  res.writeHead(200, { 'Content-Type': 'text/html; charset=utf-8' });
  res.end(generatePageHTML(pathname));
}

// ═══════════════════════════════════════════════════════════
// 启动服务器
// ═══════════════════════════════════════════════════════════
const server = http.createServer(handleRequest);
server.listen(PORT, () => {
  console.log(`✅ Mock 服务器已启动: http://localhost:${PORT}`);
});

// 优雅退出
process.on('SIGINT', () => {
  console.log('\n🛑 关闭 Mock 服务器...');
  server.close();
  process.exit(0);
});

process.on('SIGTERM', () => {
  server.close();
  process.exit(0);
});
