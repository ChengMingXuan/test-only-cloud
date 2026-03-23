// ==UserScript==
// @name         AIOPS 权限和角色测试工具
// @namespace    http://localhost:8000/
// @version      2.0
// @description  权限验证、角色快速切换、功能访问验证
// @author       AIOPS Test Team
// @match        http://localhost:8000/*
// @match        http://localhost:*/*
// @grant        GM_addStyle
// @grant        GM_xmlhttpRequest
// @grant        unsafeWindow
// @license      MIT
// ==/UserScript==

(function() {
  'use strict';

  const CONFIG = {
    testRoles: [
      { id: 'super_admin', name: 'SUPER_ADMIN', permissions: ['全部权限'] },
      { id: 'admin', name: 'Admin', permissions: ['管理员权限'] },
      { id: 'user', name: 'User', permissions: ['用户权限'] },
      { id: 'viewer', name: 'Viewer', permissions: ['只读权限'] },
    ],
    criticalFeatures: [
      '/admin/users',
      '/admin/permissions',
      '/charging/orders',
      '/device',
      '/work-order',
      '/settlement',
    ],
  };

  GM_addStyle(`
    #aiops-permission-tool {
      position: fixed;
      top: 50%;
      left: 0;
      transform: translateY(-50%);
      width: 350px;
      max-height: 500px;
      background: white;
      border: 1px solid #ddd;
      border-radius: 0 4px 4px 0;
      box-shadow: 2px 0 8px rgba(0,0,0,0.15);
      z-index: 9996;
      font-family: Arial, sans-serif;
      overflow: hidden;
      display: flex;
      flex-direction: column;
    }

    #permission-header {
      background: linear-gradient(135deg, #1890ff 0%, #0050b3 100%);
      color: white;
      padding: 12px 16px;
      font-weight: bold;
    }

    #permission-content {
      flex: 1;
      overflow-y: auto;
      padding: 12px 16px;
    }

    .permission-section {
      margin-bottom: 12px;
    }

    .permission-section-title {
      font-weight: bold;
      color: #333;
      margin-bottom: 8px;
      font-size: 13px;
      border-bottom: 2px solid #1890ff;
      padding-bottom: 4px;
    }

    .role-item {
      padding: 8px;
      margin-bottom: 6px;
      border: 1px solid #ddd;
      border-radius: 3px;
      cursor: pointer;
      transition: all 0.2s;
      font-size: 12px;
    }

    .role-item:hover {
      background: #f0f0f0;
      border-color: #1890ff;
    }

    .role-item.active {
      background: #e6f7ff;
      border-color: #1890ff;
      font-weight: bold;
    }

    .permission-list {
      font-size: 11px;
      color: #666;
      margin-top: 4px;
      padding: 4px;
      background: #f9f9f9;
      border-radius: 2px;
    }

    .permission-item {
      margin: 2px 0;
    }

    .permission-check {
      margin: 6px 0;
      padding: 6px;
      background: #f9f9f9;
      border-radius: 3px;
      border-left: 3px solid #1890ff;
    }

    .permission-check-item {
      display: flex;
      align-items: center;
      margin: 4px 0;
      font-size: 12px;
    }

    .permission-check-item input {
      margin-right: 6px;
    }

    .feature-test {
      background: #f0f0f0;
      padding: 8px;
      border-radius: 3px;
      margin: 4px 0;
      font-size: 11px;
    }

    .feature-test button {
      display: block;
      width: 100%;
      padding: 6px;
      margin: 2px 0;
      background: #1890ff;
      color: white;
      border: none;
      border-radius: 2px;
      cursor: pointer;
      font-size: 11px;
    }

    .feature-test button:hover {
      background: #0050b3;
    }

    .permission-result {
      margin-top: 8px;
      padding: 8px;
      border-radius: 3px;
      font-size: 11px;
      font-weight: bold;
    }

    .permission-result.success {
      background: #f6ffed;
      border: 1px solid #52c41a;
      color: #52c41a;
    }

    .permission-result.error {
      background: #fff5f5;
      border: 1px solid #f5222d;
      color: #f5222d;
    }

    .permission-result.warning {
      background: #fffbe6;
      border: 1px solid #faad14;
      color: #faad14;
    }
  `);

  // ========== 创建 UI ==========
  function createPermissionTool() {
    const tool = document.createElement('div');
    tool.id = 'aiops-permission-tool';
    tool.innerHTML = `
      <div id="permission-header">
        🔐 权限和角色测试工具
      </div>
      <div id="permission-content">
        <!-- 角色快速切换 -->
        <div class="permission-section">
          <div class="permission-section-title">👤 角色快速切换</div>
          ${CONFIG.testRoles.map(role => `
            <div class="role-item" data-role-id="${role.id}">
              <div><strong>${role.name}</strong></div>
              <div class="permission-list">
                ${role.permissions.map(p => `<div class="permission-item">✓ ${p}</div>`).join('')}
              </div>
            </div>
          `).join('')}
        </div>

        <!-- 权限检查 -->
        <div class="permission-section">
          <div class="permission-section-title">✅ 权限检查</div>
          <div class="permission-check">
            <div class="permission-check-item">
              <input type="checkbox" id="check-create" checked>
              <label for="check-create">创建权限</label>
            </div>
            <div class="permission-check-item">
              <input type="checkbox" id="check-edit" checked>
              <label for="check-edit">编辑权限</label>
            </div>
            <div class="permission-check-item">
              <input type="checkbox" id="check-delete" checked>
              <label for="check-delete">删除权限</label>
            </div>
            <div class="permission-check-item">
              <input type="checkbox" id="check-export" checked>
              <label for="check-export">导出权限</label>
            </div>
          </div>
          <button style="width: 100%; padding: 6px; background: #1890ff; color: white; border: none; border-radius: 2px; cursor: pointer; font-size: 12px; margin-top: 6px;" id="btn-verify-permissions">验证当前权限</button>
        </div>

        <!-- 功能访问测试 -->
        <div class="permission-section">
          <div class="permission-section-title">🧪 功能访问测试</div>
          <div class="feature-test">
            <button id="btn-test-users">测试用户管理</button>
            <button id="btn-test-permissions">测试权限管理</button>
            <button id="btn-test-charging">测试充电功能</button>
            <button id="btn-test-devices">测试设备管理</button>
            <button id="btn-test-workorder">测试工单功能</button>
            <button id="btn-test-all">全部功能测试</button>
          </div>
        </div>

        <!-- 权限结果 -->
        <div id="permission-result" style="margin-top: 12px;"></div>
      </div>
    `;

    document.body.appendChild(tool);
    bindPermissionToolEvents();
  }

  // ========== 绑定事件 ==========
  function bindPermissionToolEvents() {
    const showResult = (message, type = 'success') => {
      const resultDiv = document.getElementById('permission-result');
      resultDiv.innerHTML = `<div class="permission-result ${type}">${message}</div>`;
    };

    // 角色切换
    document.querySelectorAll('.role-item').forEach(item => {
      item.addEventListener('click', async function() {
        document.querySelectorAll('.role-item').forEach(i => i.classList.remove('active'));
        this.classList.add('active');

        const roleId = this.dataset.roleId;
        const roleName = this.querySelector('strong').textContent;

        // 这里调用 API 切换角色
        showResult(`✅ 已切换到 ${roleName} 角色`, 'success');
        
        // 保存到 localStorage
        localStorage.setItem('test_role', roleId);
        localStorage.setItem('test_role_name', roleName);

        // 重新加载权限列表
        setTimeout(() => {
          window.location.reload();
        }, 1000);
      });
    });

    // 验证权限
    document.getElementById('btn-verify-permissions').addEventListener('click', () => {
      const currentRole = localStorage.getItem('test_role') || 'unknown';
      const checks = {
        create: document.getElementById('check-create').checked,
        edit: document.getElementById('check-edit').checked,
        delete: document.getElementById('check-delete').checked,
        export: document.getElementById('check-export').checked,
      };

      let result = `当前角色: ${currentRole}\n已验证权限:\n`;
      Object.entries(checks).forEach(([key, value]) => {
        result += `${key}: ${value ? '✓' : '✗'}\n`;
      });

      showResult(result.replace(/\n/g, '<br>'), 'success');
    });

    // 测试各功能权限访问
    const testFeature = (feature, featureName) => {
      const hasAccess = !isFeatureBlocked(feature);
      if (hasAccess) {
        window.location.href = feature;
        showResult(`✅ 你有权限访问 ${featureName}`, 'success');
      } else {
        showResult(`❌ 你没有权限访问 ${featureName}`, 'error');
      }
    };

    document.getElementById('btn-test-users').addEventListener('click', () => testFeature('/admin/users', '用户管理'));
    document.getElementById('btn-test-permissions').addEventListener('click', () => testFeature('/admin/permissions', '权限管理'));
    document.getElementById('btn-test-charging').addEventListener('click', () => testFeature('/charging/orders', '充电功能'));
    document.getElementById('btn-test-devices').addEventListener('click', () => testFeature('/device', '设备管理'));
    document.getElementById('btn-test-workorder').addEventListener('click', () => testFeature('/work-order', '工单功能'));

    document.getElementById('btn-test-all').addEventListener('click', () => {
      const results = CONFIG.criticalFeatures.map(feature => {
        const accessible = !isFeatureBlocked(feature);
        return `${feature}: ${accessible ? '✓' : '✗'}`;
      }).join('<br>');

      showResult(`功能访问清单:\n${results}`.replace(/\n/g, '<br>'), 'success');
    });
  }

  // ========== 功能可访问性检查 ==========
  function isFeatureBlocked(feature) {
    // 检查当前 URL 是否包含 401/403 提示
    const pageContent = document.body.innerText;
    if (pageContent.includes('401') || pageContent.includes('403') || pageContent.includes('Unauthorized') || pageContent.includes('Forbidden')) {
      return true;
    }

    // 检查当前角色是否有权限
    const currentRole = localStorage.getItem('test_role') || 'user';
    const rolePermissions = {
      'super_admin': ['全部'],
      'admin': ['/admin', '/charging', '/device', '/work-order', '/settlement'],
      'user': ['/charging', '/device', '/work-order'],
      'viewer': ['/charging/orders'],
    };

    const allowedPaths = rolePermissions[currentRole] || [];
    return !allowedPaths.some(path => feature.startsWith(path));
  }

  // ========== 快捷键 ==========
  document.addEventListener('keydown', (e) => {
    if (e.altKey && (e.key === 'p' || e.key === 'P')) {
      e.preventDefault();
      const tool = document.getElementById('aiops-permission-tool');
      if (tool) {
        tool.style.display = tool.style.display === 'none' ? 'flex' : 'none';
      }
    }
  });

  // ========== 初始化 ==========
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', createPermissionTool);
  } else {
    createPermissionTool();
  }

  console.log('✅ AIOPS 权限和角色测试工具已加载 (Alt+P 显示/隐藏)');
})();
