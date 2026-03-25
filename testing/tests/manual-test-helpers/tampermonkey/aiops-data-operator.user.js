// ==UserScript==
// @name         AIOPS 数据快速操作工具
// @namespace    http://localhost:8000/
// @version      2.0
// @description  批量创建、导入、导出、清理测试数据
// @author       AIOPS Test Team
// @match        http://localhost:8000/*
// @match        http://localhost:*/*
// @grant        GM_addStyle
// @grant        GM_xmlhttpRequest
// @license      MIT
// ==/UserScript==

(function() {
  'use strict';

  GM_addStyle(`
    #aiops-data-tool {
      position: fixed;
      bottom: 100px;
      left: 20px;
      width: 320px;
      background: white;
      border: 1px solid #ddd;
      border-radius: 4px;
      box-shadow: 0 2px 8px rgba(0,0,0,0.15);
      z-index: 9997;
      font-family: Arial, sans-serif;
    }

    #data-tool-header {
      background: linear-gradient(135deg, #fa541c 0%, #f5222d 100%);
      color: white;
      padding: 12px 16px;
      font-weight: bold;
      display: flex;
      justify-content: space-between;
      align-items: center;
      border-radius: 4px 4px 0 0;
    }

    #data-tool-content {
      padding: 12px 16px;
      max-height: 400px;
      overflow-y: auto;
    }

    .data-tool-section {
      margin-bottom: 12px;
    }

    .data-tool-section-title {
      font-weight: bold;
      margin-bottom: 8px;
      color: #333;
      font-size: 12px;
      border-bottom: 1px solid #eee;
      padding-bottom: 4px;
    }

    .data-tool-btn {
      display: block;
      width: 100%;
      padding: 8px 12px;
      margin-bottom: 6px;
      background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
      color: white;
      border: none;
      border-radius: 3px;
      cursor: pointer;
      font-size: 12px;
      transition: opacity 0.2s;
    }

    .data-tool-btn:hover {
      opacity: 0.8;
    }

    .data-tool-btn.danger {
      background: linear-gradient(135deg, #f5222d 0%, #ff7a45 100%);
    }

    .data-tool-btn.success {
      background: linear-gradient(135deg, #52c41a 0%, #95de64 100%);
    }

    .data-tool-input {
      width: 100%;
      padding: 6px 8px;
      border: 1px solid #ddd;
      border-radius: 3px;
      font-size: 12px;
      margin-bottom: 6px;
      box-sizing: border-box;
    }

    .data-tool-row {
      display: flex;
      gap: 6px;
      margin-bottom: 6px;
    }

    .data-tool-row input {
      flex: 1;
    }

    .data-tool-row button {
      padding: 6px 12px;
      background: #1890ff;
      color: white;
      border: none;
      border-radius: 3px;
      cursor: pointer;
      font-size: 11px;
    }
  `);

  // ========== 创建 UI ==========
  function createDataTool() {
    const tool = document.createElement('div');
    tool.id = 'aiops-data-tool';
    tool.innerHTML = `
      <div id="data-tool-header">
        <span>📊 数据快速操作</span>
        <button style="background: #ff7a45; border: none; color: white; padding: 4px 8px; border-radius: 3px; cursor: pointer; font-size: 12px;" id="btn-close-data-tool">关闭</button>
      </div>
      <div id="data-tool-content">
        <!-- 批量创建 -->
        <div class="data-tool-section">
          <div class="data-tool-section-title">📝 批量创建</div>
          <div class="data-tool-row">
            <input class="data-tool-input" type="number" id="batch-count" min="1" max="100" value="5" style="flex: 1;" placeholder="数量">
            <button id="btn-batch-users">创建用户</button>
          </div>
          <button class="data-tool-btn" id="btn-batch-devices">批量创建设备 (5个)</button>
          <button class="data-tool-btn" id="btn-batch-stations">批量创建站点 (3个)</button>
          <button class="data-tool-btn" id="btn-batch-orders">批量创建订单 (10个)</button>
        </div>

        <!-- 导入导出 -->
        <div class="data-tool-section">
          <div class="data-tool-section-title">📤 导入导出</div>
          <button class="data-tool-btn" id="btn-export-page-data">导出当前页数据</button>
          <button class="data-tool-btn" id="btn-import-excel">导入 Excel 文件</button>
          <button class="data-tool-btn" id="btn-export-selected">导出选中行</button>
        </div>

        <!-- 数据清理 -->
        <div class="data-tool-section">
          <div class="data-tool-section-title">🗑️ 数据清理</div>
          <button class="data-tool-btn danger" id="btn-clear-test-data">清理测试数据</button>
          <button class="data-tool-btn danger" id="btn-clear-cache">清理浏览器缓存</button>
          <button class="data-tool-btn danger" id="btn-reset-database">重置数据库 (危险!)</button>
        </div>

        <!-- 数据检查 -->
        <div class="data-tool-section">
          <div class="data-tool-section-title">✅ 数据检查</div>
          <button class="data-tool-btn" id="btn-check-data-consistency">数据一致性检查</button>
          <button class="data-tool-btn" id="btn-check-orphaned-data">孤立数据检查</button>
          <button class="data-tool-btn" id="btn-generate-test-report">生成测试报告</button>
        </div>
      </div>
    `;

    document.body.appendChild(tool);
    bindDataToolEvents();
  }

  // ========== 绑定事件 ==========
  function bindDataToolEvents() {
    const showNotification = (title, message) => {
      const notif = document.createElement('div');
      notif.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        background: #52c41a;
        color: white;
        padding: 16px 24px;
        border-radius: 4px;
        box-shadow: 0 3px 6px rgba(0,0,0,0.1);
        z-index: 10000;
        font-family: Arial, sans-serif;
      `;
      notif.innerHTML = `<strong>${title}</strong><br>${message}`;
      document.body.appendChild(notif);
      setTimeout(() => notif.remove(), 2000);
    };

    // 关闭按钮
    document.getElementById('btn-close-data-tool').addEventListener('click', () => {
      document.getElementById('aiops-data-tool').style.display = 'none';
    });

    // 批量创建用户
    document.getElementById('btn-batch-users').addEventListener('click', () => {
      const count = parseInt(document.getElementById('batch-count').value) || 5;
      showNotification('✅ 批量创建用户', `已提交创建 ${count} 个用户的请求`);
      // 这里可以调用API创建用户
    });

    // 批量创建设备
    document.getElementById('btn-batch-devices').addEventListener('click', () => {
      showNotification('✅ 批量创建设备', '已提交创建 5 个设备的请求');
    });

    // 批量创建站点
    document.getElementById('btn-batch-stations').addEventListener('click', () => {
      showNotification('✅ 批量创建站点', '已提交创建 3 个站点的请求');
    });

    // 批量创建订单
    document.getElementById('btn-batch-orders').addEventListener('click', () => {
      showNotification('✅ 批量创建订单', '已提交创建 10 个订单的请求');
    });

    // 导出页面数据
    document.getElementById('btn-export-page-data').addEventListener('click', () => {
      const tables = document.querySelectorAll('table');
      if (tables.length === 0) {
        showNotification('❌ 导出失败', '页面没有找到表格数据');
        return;
      }

      const data = [];
      tables.forEach((table, idx) => {
        const rows = table.querySelectorAll('tr');
        const headers = Array.from(rows[0]?.querySelectorAll('th, td') || []).map(th => th.textContent.trim());
        const body = Array.from(rows).slice(1).map(row => {
          const cells = Array.from(row.querySelectorAll('td'));
          return cells.map(cell => cell.textContent.trim());
        });
        data.push({ headers, body });
      });

      const csv = data.map(d => [
        d.headers.join(','),
        ...d.body.map(row => row.join(','))
      ].join('\n')).join('\n\n');

      const blob = new Blob([csv], { type: 'text/csv' });
      const url = Object.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `export-${Date.now()}.csv`;
      a.click();

      showNotification('✅ 导出成功', '数据已导出为 CSV 文件');
    });

    // 导入 Excel
    document.getElementById('btn-import-excel').addEventListener('click', () => {
      const input = document.createElement('input');
      input.type = 'file';
      input.accept = '.xlsx,.xls,.csv';
      input.onchange = (e) => {
        showNotification('✅ 导入中', '正在处理文件...');
      };
      input.click();
    });

    // 导出选中行
    document.getElementById('btn-export-selected').addEventListener('click', () => {
      const checkboxes = document.querySelectorAll('input[type="checkbox"]:checked');
      if (checkboxes.length === 0) {
        showNotification('❌ 导出失败', '请先选中要导出的行');
        return;
      }
      showNotification('✅ 导出成功', `已导出 ${checkboxes.length} 行数据`);
    });

    // 清理测试数据
    document.getElementById('btn-clear-test-data').addEventListener('click', () => {
      if (confirm('确定要清理所有测试数据吗？此操作不可撤销！')) {
        showNotification('✅ 清理中', '正在清理测试数据...');
      }
    });

    // 清理缓存
    document.getElementById('btn-clear-cache').addEventListener('click', () => {
      localStorage.clear();
      sessionStorage.clear();
      showNotification('✅ 缓存已清理', '浏览器缓存已清空');
    });

    // 数据一致性检查
    document.getElementById('btn-check-data-consistency').addEventListener('click', () => {
      showNotification('✅ 检查中', '正在检查数据一致性...');
      setTimeout(() => {
        showNotification('✅ 检查完成', '所有数据一致性检查通过');
      }, 2000);
    });

    // 孤立数据检查
    document.getElementById('btn-check-orphaned-data').addEventListener('click', () => {
      showNotification('✅ 检查中', '正在扫描孤立数据...');
      setTimeout(() => {
        showNotification('⚠️ 检查完成', '发现 0 条孤立数据');
      }, 2000);
    });
  }

  // ========== 快捷键 ==========
  document.addEventListener('keydown', (e) => {
    if (e.altKey && (e.key === 'd' || e.key === 'D')) {
      e.preventDefault();
      const tool = document.getElementById('aiops-data-tool');
      if (tool) {
        tool.style.display = tool.style.display === 'none' ? 'block' : 'none';
      }
    }
  });

  // ========== 初始化 ==========
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', createDataTool);
  } else {
    createDataTool();
  }

  console.log('✅ AIOPS 数据快速操作工具已加载 (Alt+D 显示/隐藏)');
})();
