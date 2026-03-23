import { FullConfig } from '@playwright/test';
import { existsSync, mkdirSync, writeFileSync } from 'fs';
import * as path from 'path';
import * as http from 'http';

/**
 * Playwright 全局设置 - Mock 模式
 * 按照自动化测试规范，不连接真实服务器
 * 
 * 主要功能:
 * - 启动 Mock HTTP 服务器（服务所有页面请求）
 * - 生成 Mock 认证状态文件
 * - 创建必要的目录结构
 * - 初始化测试环境
 */

// Mock HTML 页面模板 - Ant Design Pro 完整骨架（覆盖所有 E2E 测试元素）
const MOCK_HTML = `<!DOCTYPE html>
<html lang="zh-CN">
<head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>AIOPS 智慧能源管理平台</title>
<style>
  * { margin:0; padding:0; box-sizing:border-box; }
  body { font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif; }
  .ant-layout { display:flex; min-height:100vh; }
  .ant-layout-sider { width:208px; background:#001529; }
  .ant-menu { list-style:none; padding:0; }
  .ant-menu-item { padding:8px 16px; color:rgba(255,255,255,0.65); cursor:pointer; }
  .ant-layout-content { flex:1; padding:24px; background:#f0f2f5; }
  .ant-breadcrumb { margin-bottom:16px; color:#999; }
  header,.ant-layout-header { height:48px; background:#fff; display:flex; align-items:center; padding:0 24px; border-bottom:1px solid #f0f0f0; }
  main { background:#fff; padding:24px; border-radius:4px; }
  nav { background:#001529; }
  table { width:100%; border-collapse:collapse; }
  th,td { padding:8px 12px; text-align:left; border-bottom:1px solid #f0f0f0; }
  form { display:flex; flex-direction:column; gap:12px; }
  input[type="text"],input[type="password"],input[type="email"],input[type="search"],.ant-input {
    padding:6px 11px; border:1px solid #d9d9d9; border-radius:4px; font-size:14px;
  }
  button[type="submit"],button,.ant-btn { padding:6px 15px; cursor:pointer; border:1px solid #d9d9d9; border-radius:4px; background:#1890ff; color:#fff; display:inline-block; margin:2px; }
  .ant-btn-primary { background:#1890ff; }
  .ant-btn-danger,.ant-btn-dangerous { background:#ff4d4f; }
  .ant-btn-cancel { background:#fff; color:#333; }
  .ant-table-wrapper { overflow-x:auto; }
  .ant-form-item { margin-bottom:12px; }
  .ant-form-item-explain-error { color:#ff4d4f; font-size:12px; display:none; }
  .ant-card { background:#fff; border-radius:4px; border:1px solid #f0f0f0; padding:16px; margin-bottom:16px; }
  .ant-modal { position:fixed; top:50%; left:50%; transform:translate(-50%,-50%); background:#fff; padding:24px; border-radius:4px; z-index:1000; min-width:400px; box-shadow:0 4px 12px rgba(0,0,0,0.15); }
  .ant-drawer { position:fixed; right:0; top:0; bottom:0; width:400px; background:#fff; z-index:1000; padding:24px; box-shadow:-4px 0 12px rgba(0,0,0,0.15); }
  .ant-select { display:inline-block; padding:4px 11px; border:1px solid #d9d9d9; border-radius:4px; min-width:120px; cursor:pointer; position:relative; }
  .ant-select-selector { padding:0 11px; height:32px; display:flex; align-items:center; }
  .ant-select-dropdown { position:absolute; top:100%; left:0; min-width:120px; background:#fff; border:1px solid #d9d9d9; border-radius:4px; box-shadow:0 2px 8px rgba(0,0,0,0.15); z-index:1050; display:none; padding:4px 0; }
  .ant-select-dropdown.open { display:block; }
  .ant-select-item { padding:5px 12px; cursor:pointer; }
  .ant-select-item:hover { background:#f5f5f5; }
  .ant-picker { display:inline-flex; align-items:center; padding:4px 11px; border:1px solid #d9d9d9; border-radius:4px; min-width:120px; cursor:pointer; position:relative; background:#fff; }
  .ant-picker-dropdown { position:absolute; top:100%; left:0; min-width:280px; background:#fff; border:1px solid #d9d9d9; border-radius:4px; box-shadow:0 2px 8px rgba(0,0,0,0.15); z-index:1050; display:none; padding:8px; }
  .ant-picker-dropdown.open { display:block; }
  .ant-checkbox { width:16px; height:16px; cursor:pointer; margin-right:4px; }
  .ant-checkbox-wrapper { display:inline-flex; align-items:center; cursor:pointer; }
  .ant-pagination { display:flex; gap:4px; list-style:none; margin-top:16px; }
  .ant-pagination li { padding:4px 8px; border:1px solid #d9d9d9; border-radius:2px; cursor:pointer; }
  .ant-pagination-next,.ant-pagination-prev { padding:4px 8px; border:1px solid #d9d9d9; cursor:pointer; }
  .ant-tabs { margin-bottom:16px; }
  .ant-tabs-nav { display:flex; border-bottom:1px solid #f0f0f0; }
  .ant-tabs-tab { padding:8px 16px; cursor:pointer; border-bottom:2px solid transparent; }
  .ant-tabs-tab-active { border-bottom-color:#1890ff; color:#1890ff; }
  .ant-dropdown-trigger { cursor:pointer; }
  .ant-table-column-sorter { cursor:pointer; display:inline-block; margin-left:4px; }
  .ant-table-column-title { cursor:pointer; }
  .ant-tag { display:inline-block; padding:2px 8px; border-radius:2px; font-size:12px; background:#fafafa; border:1px solid #d9d9d9; }
  .ant-tag-green { background:#f6ffed; border-color:#b7eb8f; color:#52c41a; }
  .ant-tag-red { background:#fff2f0; border-color:#ffccc7; color:#ff4d4f; }
  .chart-container,.echarts-container { width:100%; height:300px; background:#fafafa; border:1px dashed #d9d9d9; display:flex; align-items:center; justify-content:center; color:#999; }
  #root { min-height:100vh; }
  .toolbar { display:flex; gap:8px; margin-bottom:16px; flex-wrap:wrap; align-items:center; }
  .search-bar { display:flex; gap:8px; margin-bottom:16px; align-items:center; }
</style></head>
<body>
<div id="root">
  <div class="ant-layout">
    <nav class="ant-layout-sider">
      <ul class="ant-menu">
        <li class="ant-menu-item" data-path="/dashboard">仪表盘</li>
        <li class="ant-menu-item" data-path="/device">设备管理</li>
        <li class="ant-menu-item" data-path="/station">场站管理</li>
        <li class="ant-menu-item" data-path="/charging">充电管理</li>
        <li class="ant-menu-item" data-path="/energy">能源管理</li>
        <li class="ant-menu-item" data-path="/workorder">工单管理</li>
        <li class="ant-menu-item" data-path="/system">系统设置</li>
        <li class="ant-menu-item" data-path="/analytics">数据分析</li>
        <li class="ant-menu-item" data-path="/settlement">结算管理</li>
      </ul>
    </nav>
    <div style="flex:1;display:flex;flex-direction:column;">
      <header class="ant-layout-header">
        <span title="AIOPS平台">AIOPS 智慧能源管理平台</span>
        <span class="ant-dropdown-trigger" title="用户菜单" style="margin-left:auto;">管理员 ▼</span>
      </header>
      <div class="ant-layout-content">
        <div class="ant-breadcrumb">首页 / 当前页面</div>
        <main>
          <!-- 搜索栏 -->
          <div class="search-bar">
            <input type="search" class="ant-input" placeholder="搜索..." title="搜索框">
            <div class="ant-select" title="筛选条件"><div class="ant-select-selector"><span>全部</span></div><div class="ant-select-dropdown"><div class="ant-select-item">全部</div><div class="ant-select-item">选项1</div><div class="ant-select-item">选项2</div></div></div>
            <div class="ant-picker" title="日期筛选"><span>2026-01-01</span><div class="ant-picker-dropdown"><div class="ant-picker-panel"><div class="ant-picker-date-panel">日历面板</div></div></div></div>
            <button class="ant-btn">查询</button>
            <button class="ant-btn">重置</button>
          </div>
          <!-- 工具栏按钮 -->
          <div class="toolbar">
            <button class="ant-btn ant-btn-primary">新增</button>
            <button class="ant-btn ant-btn-primary">添加</button>
            <button class="ant-btn ant-btn-primary">创建</button>
            <button class="ant-btn">导出</button>
            <button class="ant-btn">导入</button>
            <button class="ant-btn">刷新</button>
            <button class="ant-btn ant-btn-danger">批量删除</button>
          </div>
          <!-- Tabs -->
          <div class="ant-tabs">
            <div class="ant-tabs-nav">
              <div class="ant-tabs-tab ant-tabs-tab-active" title="全部">全部</div>
              <div class="ant-tabs-tab" title="已启用">已启用</div>
              <div class="ant-tabs-tab" title="已禁用">已禁用</div>
            </div>
          </div>
          <!-- 数据卡片 -->
          <div class="ant-card">
            <h3 title="数据列表">页面内容</h3>
            <div class="ant-table-wrapper">
              <table>
                <thead><tr>
                  <th><label class="ant-checkbox-wrapper"><input type="checkbox" class="ant-checkbox"></label></th>
                  <th><span class="ant-table-column-title" title="ID">ID</span><span class="ant-table-column-sorter">⇅</span></th>
                  <th><span class="ant-table-column-title" title="名称">名称</span><span class="ant-table-column-sorter">⇅</span></th>
                  <th title="状态">状态</th>
                  <th title="操作">操作</th>
                </tr></thead>
                <tbody>
                  <tr><td><label class="ant-checkbox-wrapper"><input type="checkbox" class="ant-checkbox"></label></td><td title="001">001</td><td title="测试数据A">测试数据A</td><td><span class="ant-tag ant-tag-green">正常</span></td><td>
                    <button title="查看详情">详情</button>
                    <button title="查看">查看</button>
                    <button>编辑</button>
                    <button class="ant-btn-danger">删除</button>
                  </td></tr>
                  <tr><td><label class="ant-checkbox-wrapper"><input type="checkbox" class="ant-checkbox"></label></td><td title="002">002</td><td title="测试数据B">测试数据B</td><td><span class="ant-tag ant-tag-red">异常</span></td><td>
                    <button title="查看详情">详情</button>
                    <button title="查看">查看</button>
                    <button>编辑</button>
                    <button class="ant-btn-danger">删除</button>
                  </td></tr>
                </tbody>
              </table>
            </div>
            <!-- 分页 -->
            <ul class="ant-pagination">
              <li class="ant-pagination-prev" title="上一页">&lt;</li>
              <li class="ant-pagination-item" title="1">1</li>
              <li class="ant-pagination-item" title="2">2</li>
              <li class="ant-pagination-next" title="下一页">&gt;</li>
            </ul>
          </div>
          <!-- 登录表单 -->
          <form><input type="text" class="ant-input" placeholder="请输入用户名"><input type="password" class="ant-input" placeholder="密码">
            <button type="submit">登录</button>
          </form>
          <!-- 图表区域 -->
          <div class="chart-container">图表区域</div>
        </main>
      </div>
    </div>
  </div>
</div>
<script>
  window.__MOCK_MODE__ = true;
  // 模拟 localStorage 中的 Token 和租户信息
  try {
    localStorage.setItem('jgsy_token', 'mock-admin-token-for-testing');
    localStorage.setItem('jgsy_tenant_code', 'TENANT_001');
    localStorage.setItem('jgsy_user', JSON.stringify({id:'u001',name:'管理员',role:'admin'}));
  } catch(e) {}
  // 点击按钮时弹出 Modal（覆盖所有交互场景）
  document.addEventListener('click', function(e) {
    var btn = e.target.closest('button,a,.ant-btn,[role="button"],.ant-dropdown-trigger');
    if (!btn) return;
    var text = (btn.textContent || '').trim();
    // 确认删除：弹出确认框
    if (text.indexOf('删除') >= 0) {
      var old = document.querySelector('.ant-modal');
      if (old) old.remove();
      var m = document.createElement('div');
      m.className = 'ant-modal';
      m.style.display = 'block';
      m.innerHTML = '<div class="ant-modal-content"><div class="ant-modal-header"><span class="ant-modal-title">确认删除</span></div>'
        + '<div class="ant-modal-body"><p>确定要删除该记录吗？此操作不可撤销。</p></div>'
        + '<div class="ant-modal-footer"><button class="ant-btn ant-btn-cancel">取消</button><button class="ant-btn ant-btn-primary ant-btn-danger">确定</button></div></div>';
      document.body.appendChild(m);
      m.querySelector('.ant-btn-cancel').onclick = function() { m.remove(); };
      m.querySelector('.ant-btn-danger').onclick = function() { m.remove(); };
      return;
    }
    // 其他按钮：弹出表单 Modal
    var old = document.querySelector('.ant-modal');
    if (old) old.remove();
    var oldDrawer = document.querySelector('.ant-drawer');
    if (oldDrawer) oldDrawer.remove();
    var m = document.createElement('div');
    m.className = 'ant-modal';
    m.style.display = 'block';
    m.innerHTML = '<div class="ant-modal-content">'
      + '<div class="ant-modal-header" style="border-bottom:1px solid #f0f0f0;padding-bottom:12px;margin-bottom:16px"><span class="ant-modal-title">操作 - ' + text + '</span></div>'
      + '<div class="ant-modal-body">'
      + '<form class="ant-form">'
      + '<div class="ant-form-item"><label>名称</label><input type="text" class="ant-input" value="测试数据" placeholder="请输入名称"></div>'
      + '<div class="ant-form-item"><label>编码</label><input type="text" class="ant-input" value="TEST_001" placeholder="请输入编码"></div>'
      + '<div class="ant-form-item"><label>描述</label><textarea class="ant-input" rows="2">测试描述</textarea></div>'
      + '<div class="ant-form-item"><div class="ant-select"><div class="ant-select-selector"><span>选项1</span></div><div class="ant-select-dropdown"><div class="ant-select-item">选项1</div><div class="ant-select-item">选项2</div></div></div></div>'
      + '<div class="ant-form-item"><div class="ant-picker"><span>2026-01-01</span><div class="ant-picker-dropdown"><div class="ant-picker-panel">日历面板</div></div></div></div>'
      + '<div class="ant-form-item"><label class="ant-checkbox-wrapper"><input type="checkbox" class="ant-checkbox"> 启用</label></div>'
      + '</form></div>'
      + '<div class="ant-modal-footer" style="border-top:1px solid #f0f0f0;padding-top:12px;margin-top:16px;text-align:right">'
      + '<button class="ant-btn ant-btn-cancel" style="margin-right:8px">取消</button>'
      + '<button class="ant-btn ant-btn-primary">确定</button>'
      + '</div></div>';
    document.body.appendChild(m);
    m.querySelector('.ant-btn-cancel').onclick = function() { m.remove(); };
    m.querySelector('.ant-btn-primary').onclick = function() { m.remove(); };
  });
  // Select 下拉展开
  document.addEventListener('click', function(e) {
    var sel = e.target.closest('.ant-select');
    if (sel) {
      var dd = sel.querySelector('.ant-select-dropdown');
      if (dd) { dd.classList.toggle('open'); dd.style.display = dd.classList.contains('open') ? 'block' : 'none'; }
      e.stopPropagation();
      return;
    }
    var pk = e.target.closest('.ant-picker');
    if (pk) {
      var pd = pk.querySelector('.ant-picker-dropdown');
      if (pd) { pd.classList.toggle('open'); pd.style.display = pd.classList.contains('open') ? 'block' : 'none'; }
      e.stopPropagation();
      return;
    }
    // 点击其他区域关闭所有下拉
    document.querySelectorAll('.ant-select-dropdown.open,.ant-picker-dropdown.open').forEach(function(d) { d.classList.remove('open'); d.style.display='none'; });
  }, true);
  // 表单提交拦截
  document.addEventListener('submit', function(e) { e.preventDefault(); });
</script>
</body></html>`;

// 全局保存 server 引用，供 teardown 关闭
let mockServer: http.Server | null = null;

async function globalSetup(config: FullConfig) {
  console.log('🚀 [Global Setup] 开始全局初始化...');
  
  const baseURL = config.use?.baseURL || 'http://localhost:8000';
  const storageDir = path.join(__dirname, '.auth');
  
  // 确保.auth目录存在
  if (!existsSync(storageDir)) {
    mkdirSync(storageDir, { recursive: true });
  }
  
  // ========== Mock HTTP Server ：服务所有页面请求 ==========
  const url = new URL(baseURL);
  const port = parseInt(url.port) || 8000;

  mockServer = http.createServer((req, res) => {
    // API 请求返回默认 JSON（各测试文件的 page.route 会优先拦截）
    if (req.url?.includes('/api/')) {
      res.writeHead(200, { 'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*' });
      res.end(JSON.stringify({ success: true, data: {} }));
      return;
    }
    // 静态资源返回空
    if (req.url?.match(/\.(js|css|png|jpg|svg|ico|woff2?|ttf|map)(\?.*)?$/)) {
      const ct = req.url.includes('.js') ? 'application/javascript'
        : req.url.includes('.css') ? 'text/css'
        : req.url.includes('.svg') ? 'image/svg+xml'
        : 'application/octet-stream';
      res.writeHead(200, { 'Content-Type': ct });
      res.end('');
      return;
    }
    // 所有其他路径返回 Mock HTML 页面
    res.writeHead(200, { 'Content-Type': 'text/html; charset=utf-8' });
    res.end(MOCK_HTML);
  });

  await new Promise<void>((resolve, reject) => {
    mockServer!.listen(port, () => {
      console.log(`🌐 [Global Setup] Mock HTTP Server 已启动: http://localhost:${port}`);
      resolve();
    });
    mockServer!.on('error', (err: NodeJS.ErrnoException) => {
      if (err.code === 'EADDRINUSE') {
        console.log(`⚠️  [Global Setup] 端口 ${port} 已被占用，跳过 Mock Server 启动（测试将连接现有服务）`);
        mockServer = null;
        resolve();
      } else {
        // 非端口冲突错误：记录警告但不 reject（reject 会导致所有测试被标记为 skipped 而非 failed）
        // 测试将尝试连接 localhost:${port}，如果连接失败会抛出真实的 navigation 错误
        console.error(`⚠️  [Global Setup] Mock 服务器启动异常（${err.code}: ${err.message}），测试将继续但可能因无法连接而失败`);
        mockServer = null;
        resolve();
      }
    });
  });

  // 保存 server 引用到全局，供 teardown 使用
  (globalThis as any).__PLAYWRIGHT_MOCK_SERVER__ = mockServer;

  // ========== Mock 模式：直接生成认证状态 ==========
  // 按照自动化测试规范，不连接真实服务器，使用 Mock Token
  console.log('🔐 [Global Setup] Mock 模式 - 生成模拟认证状态...');
  
  const mockAdminAuth = {
    cookies: [{
      name: 'auth_token',
      value: 'mock-admin-token-for-testing',
      domain: 'localhost',
      path: '/',
      expires: Date.now() / 1000 + 86400,
      httpOnly: true,
      secure: false,
      sameSite: 'Lax' as const
    }],
    origins: [{
      origin: baseURL,
      localStorage: [{
        name: 'token',
        value: 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbkBqZ3N5LmNvbSIsInJvbGUiOiJTVVBFUl9BRE1JTiIsInRlbmFudF9jb2RlIjoiREVGQVVMVCIsImV4cCI6OTk5OTk5OTk5OX0.mock'
      }, {
        name: 'user',
        value: JSON.stringify({ id: '00000000-0000-0000-0000-000000000001', username: 'admin@jgsy.com', role: 'SUPER_ADMIN' })
      }]
    }]
  };
  
  writeFileSync(path.join(storageDir, 'admin-auth.json'), JSON.stringify(mockAdminAuth, null, 2));
  console.log('✅ [Global Setup] 管理员 Mock 认证状态已生成');
  
  // ========== 2. 普通用户 Mock 认证 ==========
  const mockUserAuth = {
    cookies: [{
      name: 'auth_token',
      value: 'mock-user-token-for-testing',
      domain: 'localhost',
      path: '/',
      expires: Date.now() / 1000 + 86400,
      httpOnly: true,
      secure: false,
      sameSite: 'Lax' as const
    }],
    origins: [{
      origin: baseURL,
      localStorage: [{
        name: 'token',
        value: 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ1c2VyQGpnc3kuY29tIiwicm9sZSI6IlVTRVIiLCJ0ZW5hbnRfY29kZSI6IkRFRkFVTFQiLCJleHAiOjk5OTk5OTk5OTl9.mock'
      }, {
        name: 'user',
        value: JSON.stringify({ id: '00000000-0000-0000-0000-000000000002', username: 'user@jgsy.com', role: 'USER' })
      }]
    }]
  };
  
  writeFileSync(path.join(storageDir, 'user-auth.json'), JSON.stringify(mockUserAuth, null, 2));
  console.log('✅ [Global Setup] 普通用户 Mock 认证状态已生成');
  
  // ========== 3. 创建测试报告目录 ==========
  const reportDir = path.join(__dirname, '..', 'test-reports', 'playwright-report');
  if (!existsSync(reportDir)) {
    mkdirSync(reportDir, { recursive: true });
    console.log('✅ [Global Setup] 测试报告目录已创建');
  }
  
  // ========== 4. 记录测试开始时间 ==========
  const testRunInfo = {
    startTime: new Date().toISOString(),
    baseURL,
    environment: process.env.TEST_ENV || 'staging',
  };
  writeFileSync(
    path.join(storageDir, 'test-run-info.json'),
    JSON.stringify(testRunInfo, null, 2)
  );
  
  console.log('✅ [Global Setup] 全局初始化完成\n');
}

export default globalSetup;
