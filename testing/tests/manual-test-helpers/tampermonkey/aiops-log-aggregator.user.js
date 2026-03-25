// ==UserScript==
// @name         AIOPS 实时日志聚合工具
// @namespace    http://localhost:8000/
// @version      2.0
// @description  统一浏览器日志、API 日志、存储变化，实时监控
// @author       AIOPS Test Team
// @match        http://localhost:8000/*
// @match        http://localhost:*/*
// @grant        GM_addStyle
// @grant        GM_getValue
// @grant        GM_setValue
// ==/UserScript==

(function() {
  'use strict';

  GM_addStyle(`
    #aiops-logs-tool {
      position: fixed;
      top: 20px;
      left: 20px;
      width: 500px;
      max-height: 700px;
      background: white;
      border: 1px solid #ddd;
      border-radius: 4px;
      box-shadow: 0 2px 8px rgba(0,0,0,0.15);
      z-index: 9996;
      font-family: 'Courier New', monospace;
      display: flex;
      flex-direction: column;
    }

    #logs-header {
      background: linear-gradient(135deg, #722ed1 0%, #b37feb 100%);
      color: white;
      padding: 12px 16px;
      font-weight: bold;
      display: flex;
      justify-content: space-between;
      align-items: center;
      border-radius: 4px 4px 0 0;
    }

    .logs-btn {
      background: rgba(255,255,255,0.3);
      color: white;
      border: 1px solid rgba(255,255,255,0.5);
      padding: 4px 8px;
      border-radius: 3px;
      cursor: pointer;
      font-size: 11px;
      margin-left: 4px;
    }

    #logs-toolbar {
      background: #f5f5f5;
      padding: 8px 12px;
      border-bottom: 1px solid #ddd;
      display: flex;
      gap: 4px;
      flex-wrap: wrap;
    }

    .logs-filter {
      padding: 3px 8px;
      border: 1px solid #ddd;
      border-radius: 3px;
      background: white;
      cursor: pointer;
      font-size: 11px;
    }

    .logs-filter.active {
      background: #722ed1;
      color: white;
      border-color: #722ed1;
    }

    #logs-content {
      flex: 1;
      overflow-y: auto;
      background: #1e1e1e;
      color: #d4d4d4;
      padding: 8px;
      font-size: 11px;
      line-height: 1.4;
    }

    .log-entry {
      margin-bottom: 4px;
      padding: 6px 8px;
      border-radius: 2px;
      border-left: 3px solid #666;
    }

    .log-entry.log { border-left-color: #0098ff; background: rgba(0, 152, 255, 0.1); }
    .log-entry.warning { border-left-color: #faad14; background: rgba(250, 173, 20, 0.1); }
    .log-entry.error { border-left-color: #f5222d; background: rgba(245, 34, 45, 0.1); }
    .log-entry.info { border-left-color: #1890ff; background: rgba(24, 144, 255, 0.1); }
    .log-entry.api { border-left-color: #52c41a; background: rgba(82, 196, 26, 0.1); }
    .log-entry.storage { border-left-color: #13c2c2; background: rgba(19, 194, 194, 0.1); }

    .log-time {
      color: #858585;
      font-size: 10px;
      margin-right: 8px;
    }

    .log-level {
      display: inline-block;
      padding: 1px 4px;
      border-radius: 2px;
      font-weight: bold;
      margin-right: 4px;
      font-size: 10px;
    }

    .log-level.log { background: #0098ff; color: white; }
    .log-level.warning { background: #faad14; color: white; }
    .log-level.error { background: #f5222d; color: white; }
    .log-level.info { background: #1890ff; color: white; }
    .log-level.api { background: #52c41a; color: white; }
    .log-level.storage { background: #13c2c2; color: white; }

    .log-source {
      color: #888;
      font-size: 10px;
      margin-left: 6px;
    }

    .log-message {
      color: #d4d4d4;
      margin-top: 2px;
      word-break: break-all;
    }

    #logs-stats {
      background: #f5f5f5;
      padding: 8px 12px;
      border-top: 1px solid #ddd;
      font-size: 10px;
      display: flex;
      gap: 12px;
      flex-wrap: wrap;
    }

    .stat-item {
      display: flex;
      gap: 4px;
    }

    .stat-label {
      color: #666;
    }

    .stat-value {
      font-weight: bold;
      color: #333;
    }
  `);

  // ========== 日志收集器 ==========
  const logs = [];
  const MAX_LOGS = 500;
  let filters = { log: true, warning: true, error: true, info: true, api: true, storage: true };

  // 拦截原生 console
  const originalLog = console.log;
  const originalWarn = console.warn;
  const originalError = console.error;
  const originalInfo = console.info;

  console.log = function(...args) {
    addLog('log', args.join(' '), 'Console');
    originalLog.apply(console, args);
  };

  console.warn = function(...args) {
    addLog('warning', args.join(' '), 'Console');
    originalWarn.apply(console, args);
  };

  console.error = function(...args) {
    addLog('error', args.join(' '), 'Console');
    originalError.apply(console, args);
  };

  console.info = function(...args) {
    addLog('info', args.join(' '), 'Console');
    originalInfo.apply(console, args);
  };

  // 拦截 Fetch
  const originalFetch = window.fetch;
  window.fetch = function(...args) {
    const [resource, config] = args;
    const method = (config?.method || 'GET').toUpperCase();
    const url = typeof resource === 'string' ? resource : resource.url;
    
    addLog('api', `${method} ${url}`, 'Fetch');

    return originalFetch.apply(window, args)
      .then(response => {
        const status = response.status;
        const statusColor = status < 400 ? '✅' : status < 500 ? '⚠️' : '❌';
        addLog('api', `${statusColor} ${method} ${url} [${status}]`, 'Fetch');
        return response;
      })
      .catch(error => {
        addLog('error', `${method} ${url} - ${error.message}`, 'Fetch');
        return Promise.reject(error);
      });
  };

  // 拦截 localStorage/sessionStorage
  const storageProxy = (storage, type) => {
    const original = storage.setItem;
    storage.setItem = function(key, value) {
      addLog('storage', `${type}.setItem(${key}, ${value.substring(0, 50)}...)`, 'Storage');
      return original.apply(storage, arguments);
    };
  };

  storageProxy(localStorage, 'localStorage');
  storageProxy(sessionStorage, 'sessionStorage');

  // ========== 添加日志 ==========
  function addLog(level, message, source) {
    const timestamp = new Date().toLocaleTimeString();
    logs.push({
      level,
      message: String(message).substring(0, 1000),
      source,
      timestamp,
    });

    if (logs.length > MAX_LOGS) {
      logs.shift();
    }

    updateLogDisplay();
  }

  // ========== 创建 UI ==========
  function createLogsTool() {
    const tool = document.createElement('div');
    tool.id = 'aiops-logs-tool';
    tool.innerHTML = `
      <div id="logs-header">
        <span>📋 实时日志聚合</span>
        <div>
          <button class="logs-btn" id="btn-export-logs">导出</button>
          <button class="logs-btn" id="btn-clear-logs">清空</button>
          <button class="logs-btn" id="btn-close-logs">关闭</button>
        </div>
      </div>

      <div id="logs-toolbar">
        <button class="logs-filter active" data-level="log">📝 日志</button>
        <button class="logs-filter active" data-level="info">ℹ️ 信息</button>
        <button class="logs-filter active" data-level="warning">⚠️ 警告</button>
        <button class="logs-filter active" data-level="error">❌ 错误</button>
        <button class="logs-filter active" data-level="api">🌐 API</button>
        <button class="logs-filter active" data-level="storage">💾 存储</button>
      </div>

      <div id="logs-content"></div>

      <div id="logs-stats">
        <div class="stat-item">
          <span class="stat-label">总数:</span>
          <span class="stat-value" id="stat-total">0</span>
        </div>
        <div class="stat-item">
          <span class="stat-label">错误:</span>
          <span class="stat-value" id="stat-errors">0</span>
        </div>
        <div class="stat-item">
          <span class="stat-label">警告:</span>
          <span class="stat-value" id="stat-warnings">0</span>
        </div>
        <div class="stat-item">
          <span class="stat-label">API 请求:</span>
          <span class="stat-value" id="stat-apis">0</span>
        </div>
      </div>
    `;

    document.body.appendChild(tool);

    // 事件绑定
    document.getElementById('btn-clear-logs').addEventListener('click', () => {
      logs.length = 0;
      updateLogDisplay();
    });

    document.getElementById('btn-export-logs').addEventListener('click', exportLogs);
    document.getElementById('btn-close-logs').addEventListener('click', () => {
      tool.style.display = 'none';
    });

    // 过滤器
    document.querySelectorAll('.logs-filter').forEach(btn => {
      btn.addEventListener('click', (e) => {
        const level = e.target.dataset.level;
        filters[level] = !filters[level];
        e.target.classList.toggle('active');
        updateLogDisplay();
      });
    });

    updateLogDisplay();
  }

  function updateLogDisplay() {
    const content = document.getElementById('logs-content');
    const filtered = logs.filter(log => filters[log.level]);

    content.innerHTML = filtered.map(log => `
      <div class="log-entry ${log.level}">
        <span class="log-time">${log.timestamp}</span>
        <span class="log-level ${log.level}">${log.level.toUpperCase()}</span>
        <span class="log-source">[${log.source}]</span>
        <div class="log-message">${escapeHtml(log.message)}</div>
      </div>
    `).join('');

    // 自动滚动到底部
    if (content.scrollHeight > content.clientHeight) {
      content.scrollTop = content.scrollHeight;
    }

    // 更新统计信息
    const total = logs.length;
    const errors = logs.filter(l => l.level === 'error').length;
    const warnings = logs.filter(l => l.level === 'warning').length;
    const apis = logs.filter(l => l.level === 'api').length;

    document.getElementById('stat-total').textContent = total;
    document.getElementById('stat-errors').textContent = errors;
    document.getElementById('stat-warnings').textContent = warnings;
    document.getElementById('stat-apis').textContent = apis;
  }

  function exportLogs() {
    const json = JSON.stringify(logs, null, 2);
    const blob = new Blob([json], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `aiops-logs-${new Date().getTime()}.json`;
    a.click();
    URL.revokeObjectURL(url);
  }

  function escapeHtml(text) {
    const map = {
      '&': '&amp;',
      '<': '&lt;',
      '>': '&gt;',
      '"': '&quot;',
      "'": '&#039;'
    };
    return text.replace(/[&<>"']/g, m => map[m]);
  }

  // ========== 快捷键 ==========
  document.addEventListener('keydown', (e) => {
    if (e.altKey && (e.key === 'l' || e.key === 'L')) {
      e.preventDefault();
      const tool = document.getElementById('aiops-logs-tool');
      if (tool) {
        tool.style.display = tool.style.display === 'none' ? 'flex' : 'none';
      }
    }
  });

  // ========== 初始化 ==========
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', createLogsTool);
  } else {
    createLogsTool();
  }

  console.log('✅ AIOPS 实时日志聚合工具已加载 (Alt+L 显示/隐藏)');
})();
