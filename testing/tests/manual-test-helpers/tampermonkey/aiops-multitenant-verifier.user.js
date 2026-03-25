// ==UserScript==
// @name         AIOPS 多租户隔离验证工具
// @namespace    http://localhost:8000/
// @version      2.0
// @description  快速切换租户、验证数据隔离、检测越权访问
// @author       AIOPS Test Team
// @match        http://localhost:8000/*
// @match        http://localhost:*/*
// @grant        GM_addStyle
// @grant        GM_xmlhttpRequest
// @run-at       document-start
// ==/UserScript==

(function() {
  'use strict';

  GM_addStyle(`
    #aiops-tenant-tool {
      position: fixed;
      bottom: 20px;
      left: 20px;
      width: 380px;
      max-height: 700px;
      background: white;
      border: 1px solid #ddd;
      border-radius: 4px;
      box-shadow: 0 2px 8px rgba(0,0,0,0.15);
      z-index: 9994;
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
      display: flex;
      flex-direction: column;
    }

    #tenant-header {
      background: linear-gradient(135deg, #1890ff 0%, #69c0ff 100%);
      color: white;
      padding: 12px 16px;
      font-weight: bold;
      display: flex;
      justify-content: space-between;
      align-items: center;
      border-radius: 4px 4px 0 0;
    }

    .tenant-btn {
      background: rgba(255,255,255,0.3);
      color: white;
      border: 1px solid rgba(255,255,255,0.5);
      padding: 4px 8px;
      border-radius: 3px;
      cursor: pointer;
      font-size: 11px;
      margin-left: 4px;
    }

    #tenant-content {
      flex: 1;
      overflow-y: auto;
      padding: 12px;
      font-size: 12px;
    }

    .tenant-section {
      margin-bottom: 12px;
      padding: 10px;
      background: #f5f8fa;
      border-radius: 4px;
      border-left: 3px solid #1890ff;
    }

    .tenant-section-title {
      font-weight: bold;
      color: #0050b3;
      margin-bottom: 8px;
      font-size: 13px;
    }

    .tenant-card {
      background: white;
      border: 1px solid #d9d9d9;
      padding: 8px 12px;
      border-radius: 3px;
      margin-bottom: 6px;
      cursor: pointer;
      transition: all 0.2s;
    }

    .tenant-card:hover {
      border-color: #1890ff;
      background: #e6f7ff;
    }

    .tenant-card.active {
      background: linear-gradient(135deg, #e6f7ff 0%, #bae7ff 100%);
      border-color: #1890ff;
      font-weight: bold;
      color: #0050b3;
    }

    .tenant-card-name {
      font-weight: bold;
      color: #333;
      margin-bottom: 2px;
    }

    .tenant-card-id {
      font-size: 10px;
      color: #999;
      font-family: monospace;
    }

    .isolation-check {
      background: white;
      border: 1px solid #f0f0f0;
      padding: 8px;
      margin: 4px 0;
      border-radius: 3px;
      font-size: 11px;
    }

    .isolation-check-label {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 4px;
    }

    .isolation-check-status {
      font-weight: bold;
      padding: 2px 6px;
      border-radius: 2px;
      font-size: 10px;
    }

    .isolation-check-status.pass {
      background: #f6ffed;
      color: #52c41a;
    }

    .isolation-check-status.fail {
      background: #fff1f0;
      color: #f5222d;
    }

    .isolation-check-status.warning {
      background: #fffbe6;
      color: #faad14;
    }

    .test-button {
      background: #1890ff;
      color: white;
      border: none;
      padding: 6px 12px;
      border-radius: 3px;
      cursor: pointer;
      font-size: 11px;
      margin-right: 4px;
      margin-top: 6px;
    }

    .test-button:hover {
      background: #0050b3;
    }

    .test-result {
      background: #fafafa;
      border-left: 2px solid #1890ff;
      padding: 6px 8px;
      margin: 6px 0;
      border-radius: 2px;
      font-size: 10px;
      font-family: monospace;
    }

    .test-result.error {
      border-left-color: #f5222d;
      background: #fff1f0;
    }
  `);

  // ========== 租户配置 ==========
  const TEST_TENANTS = [
    { id: '00000000-0000-0000-0000-000000000001', name: '全局租户', color: '#1890ff' },
    { id: '00000000-0000-0000-0000-000000000002', name: 'Tenant-A', color: '#52c41a' },
    { id: '00000000-0000-0000-0000-000000000003', name: 'Tenant-B', color: '#faad14' },
    { id: '00000000-0000-0000-0000-000000000004', name: 'Tenant-C', color: '#f5222d' },
  ];

  let currentTenant = TEST_TENANTS[0];
  let isolationResults = [];

  // ========== 租户切换 ==========
  function switchTenant(tenant) {
    currentTenant = tenant;
    localStorage.setItem('currentTenantId', tenant.id);
    localStorage.setItem('currentTenantName', tenant.name);
    
    // 设置到 sessionStorage 以便后续 API 请求使用
    sessionStorage.setItem('tenantId', tenant.id);
    
    // 添加 Authorization header 中的租户信息
    const token = localStorage.getItem('token');
    if (token) {
      try {
        const payload = token.split('.')[1];
        const decoded = JSON.parse(atob(payload));
        decoded.tenant_id = tenant.id;
        decoded.tenant_name = tenant.name;
        // 这里实际中应该调用后端重新颁发 token
      } catch (e) {}
    }

    setTimeout(() => location.reload(), 1000);
  }

  // ========== 获取当前租户 ID ==========
  function getCurrentTenantId() {
    const stored = localStorage.getItem('currentTenantId');
    if (stored) return stored;
    
    const token = localStorage.getItem('token');
    if (token) {
      try {
        const payload = token.split('.')[1];
        const decoded = JSON.parse(atob(payload));
        return decoded.tenant_id;
      } catch (e) {}
    }
    
    return TEST_TENANTS[0].id;
  }

  // ========== 验证数据隔离 ==========
  async function verifyDataIsolation() {
    isolationResults = [];
    
    // 检查关键 API 路径的数据隔离
    const criticalPaths = [
      '/api/users',
      '/api/tenants',
      '/api/roles',
      '/api/permissions',
      '/api/devices',
      '/api/stations',
      '/api/orders',
      '/api/settlement',
    ];

    for (const path of criticalPaths) {
      try {
        const response = await fetch(path);
        const data = await response.json();
        
        // 检查返回数据中是否包含租户 ID
        let hasTenantField = false;
        let allDataBelongsToTenant = true;
        
        if (data.data && Array.isArray(data.data)) {
          hasTenantField = data.data.length > 0 && data.data[0].tenant_id;
          allDataBelongsToTenant = data.data.every(item => 
            !item.tenant_id || item.tenant_id === currentTenant.id
          );
        }

        isolationResults.push({
          path,
          hasTenantField,
          allDataBelongsToTenant,
          dataCount: data.data?.length || 0,
          status: hasTenantField && allDataBelongsToTenant ? 'pass' : 'warning',
        });
      } catch (e) {
        isolationResults.push({
          path,
          status: 'fail',
          error: e.message,
        });
      }
    }

    updateTenantDisplay();
  }

  // ========== 检测跨租户数据泄露 ==========
  async function detectDataLeak() {
    const testResults = [];
    
    // 切换到第一个租户，记录数据
    switchTenant(TEST_TENANTS[1]);
    await new Promise(r => setTimeout(r, 2000));
    
    const tenant1Data = {};
    try {
      const resp = await fetch('/api/users');
      const data = await resp.json();
      tenant1Data.users = (data.data || []).map(u => u.id);
    } catch (e) {
      testResults.push({ check: '用户数据隔离', status: 'fail', message: e.message });
    }

    // 切换到第二个租户
    switchTenant(TEST_TENANTS[2]);
    await new Promise(r => setTimeout(r, 2000));
    
    try {
      const resp = await fetch('/api/users');
      const data = await resp.json();
      const tenant2Users = (data.data || []).map(u => u.id);
      
      const leaked = tenant2Users.filter(id => tenant1Data.users?.includes(id));
      testResults.push({
        check: '用户数据隔离',
        status: leaked.length === 0 ? 'pass' : 'fail',
        message: leaked.length === 0 ? '✅ 数据隔离正确' : `❌ 检测到 ${leaked.length} 条泄露数据`,
      });
    } catch (e) {
      testResults.push({ check: '用户数据隔离', status: 'fail', message: e.message });
    }

    // 返回到初始租户
    switchTenant(TEST_TENANTS[0]);

    return testResults;
  }

  // ========== 检测权限越界 ==========
  async function detectPermissionEscalation() {
    const results = [];
    
    const restrictedPaths = [
      { path: '/api/admin/permissions', requiresAdmin: true },
      { path: '/api/admin/role-users', requiresAdmin: true },
      { path: '/api/audit-logs', requiresAdmin: true },
      { path: '/api/system/config', requiresAdmin: true },
    ];

    for (const pathConfig of restrictedPaths) {
      try {
        const response = await fetch(pathConfig.path);
        const isAccessible = response.ok;
        const isForbidden = response.status === 403;
        const isUnauthorized = response.status === 401;

        results.push({
          path: pathConfig.path,
          status: (isForbidden || isUnauthorized) ? 'pass' : 'warning',
          httpStatus: response.status,
          message: isForbidden ? '正确拒绝' : isUnauthorized ? '要求认证' : '⚠️ 访问可能不应该被允许',
        });
      } catch (e) {
        results.push({
          path: pathConfig.path,
          status: 'fail',
          message: e.message,
        });
      }
    }

    return results;
  }

  // ========== 创建 UI ==========
  function createTenantTool() {
    const tool = document.createElement('div');
    tool.id = 'aiops-tenant-tool';
    tool.innerHTML = `
      <div id="tenant-header">
        <span>🏢 多租户验证工具</span>
        <div>
          <button class="tenant-btn" id="btn-refresh-tenant">检查</button>
          <button class="tenant-btn" id="btn-close-tenant">关闭</button>
        </div>
      </div>
      <div id="tenant-content"></div>
    `;

    document.body.appendChild(tool);
    updateTenantDisplay();

    document.getElementById('btn-refresh-tenant').addEventListener('click', verifyDataIsolation);
    document.getElementById('btn-close-tenant').addEventListener('click', () => {
      tool.style.display = 'none';
    });
  }

  function updateTenantDisplay() {
    const content = document.getElementById('tenant-content');
    currentTenant = TEST_TENANTS.find(t => t.id === getCurrentTenantId()) || TEST_TENANTS[0];

    let html = `
      <!-- 租户快速切换 -->
      <div class="tenant-section">
        <div class="tenant-section-title">🔄 快速切换</div>
        ${TEST_TENANTS.map(t => `
          <div class="tenant-card ${t.id === currentTenant.id ? 'active' : ''}" onclick="window.__aiops_tenantTool.switchTenant('${t.id}')">
            <div class="tenant-card-name">${t.name}</div>
            <div class="tenant-card-id">${t.id}</div>
          </div>
        `).join('')}
      </div>

      <!-- 当前租户信息 -->
      <div class="tenant-section">
        <div class="tenant-section-title">ℹ️ 当前租户</div>
        <div style="padding: 8px;">
          <div style="margin: 4px 0;"><strong>租户名:</strong> ${currentTenant.name}</div>
          <div style="margin: 4px 0; font-family: monospace; font-size: 10px;">
            <strong>ID:</strong><br>${currentTenant.id}
          </div>
        </div>
      </div>

      <!-- 数据隔离检查 -->
      <div class="tenant-section">
        <div class="tenant-section-title">🔒 数据隔离检查</div>
        ${isolationResults.length > 0 ? isolationResults.map(r => `
          <div class="isolation-check">
            <div class="isolation-check-label">
              <span>${r.path}</span>
              <span class="isolation-check-status ${r.status}">${r.status === 'pass' ? '✅ 隔离' : r.status === 'warning' ? '⚠️ 需检查' : '❌ 失败'}</span>
            </div>
            ${r.error ? `<div style="color: #f5222d; font-size: 10px;">${r.error}</div>` : `
              <div style="color: #666; font-size: 10px;">
                数据条数: ${r.dataCount}, 租户字段: ${r.hasTenantField ? '✅ 有' : '❌ 无'}
              </div>
            `}
          </div>
        `).join('') : '<div style="color: #999; padding: 8px;">点击"检查"开始验证</div>'}
      </div>

      <!-- 测试按钮 -->
      <div class="tenant-section">
        <div class="tenant-section-title">🧪 自动化测试</div>
        <button class="test-button" onclick="window.__aiops_tenantTool.testDataLeak()">检测数据泄露</button>
        <button class="test-button" onclick="window.__aiops_tenantTool.testPermEsc()">检测权限越界</button>
      </div>

      <!-- 测试结果 -->
      ${window.__aiops_testResults && window.__aiops_testResults.length > 0 ? `
        <div class="tenant-section">
          <div class="tenant-section-title">📊 测试结果</div>
          ${window.__aiops_testResults.map(r => `
            <div class="test-result ${r.status === 'fail' ? 'error' : ''}">
              <strong>${r.check || r.path}</strong><br>
              ${r.message}
            </div>
          `).join('')}
        </div>
      ` : ''}
    `;

    content.innerHTML = html;
  }

  // ========== 全局对象 ==========
  window.__aiops_tenantTool = {
    switchTenant: (tenantId) => {
      const tenant = TEST_TENANTS.find(t => t.id === tenantId);
      if (tenant) switchTenant(tenant);
    },
    testDataLeak: async () => {
      window.__aiops_testResults = await detectDataLeak();
      updateTenantDisplay();
    },
    testPermEsc: async () => {
      window.__aiops_testResults = await detectPermissionEscalation();
      updateTenantDisplay();
    },
  };

  // ========== 快捷键 ==========
  document.addEventListener('keydown', (e) => {
    if (e.altKey && (e.key === 't' || e.key === 'T')) {
      e.preventDefault();
      const tool = document.getElementById('aiops-tenant-tool');
      if (tool) {
        tool.style.display = tool.style.display === 'none' ? 'flex' : 'none';
      }
    }
  });

  // ========== 初始化 ==========
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', createTenantTool);
  } else {
    createTenantTool();
  }

  console.log('✅ AIOPS 多租户验证工具已加载 (Alt+T 显示/隐藏)');
})();
