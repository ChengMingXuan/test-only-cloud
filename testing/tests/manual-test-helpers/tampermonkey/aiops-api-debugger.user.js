// ==UserScript==
// @name         AIOPS API 调试监控工具
// @namespace    http://localhost:8000/
// @version      2.0
// @description  实时监控API请求/响应，进行性能分析和调试
// @author       AIOPS Test Team
// @match        http://localhost:8000/*
// @match        http://localhost:*/*
// @grant        unsafeWindow
// @grant        GM_addStyle
// @license      MIT
// ==/UserScript==

(function() {
  'use strict';

  const CONFIG = {
    maxLogs: 100,
    warningThreshold: 500,  // ms
    errorThreshold: 1000,   // ms
  };

  let requestLogs = [];
  let isMonitoring = true;

  // ========== 样式注入 ==========
  GM_addStyle(`
    #aiops-api-monitor {
      position: fixed;
      top: 50%;
      right: 0;
      transform: translateY(-50%);
      width: 400px;
      max-height: 600px;
      background: white;
      border: 1px solid #ddd;
      border-radius: 4px 0 0 4px;
      box-shadow: -2px 0 8px rgba(0,0,0,0.15);
      z-index: 9998;
      font-family: 'Courier New', monospace;
      overflow: hidden;
      display: flex;
      flex-direction: column;
    }

    #api-monitor-header {
      background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
      color: white;
      padding: 12px 16px;
      font-weight: bold;
      display: flex;
      justify-content: space-between;
      align-items: center;
    }

    .api-monitor-btn {
      background: rgba(255,255,255,0.3);
      color: white;
      border: 1px solid rgba(255,255,255,0.5);
      padding: 4px 8px;
      border-radius: 3px;
      cursor: pointer;
      font-size: 11px;
      margin-left: 4px;
    }

    .api-monitor-btn:hover {
      background: rgba(255,255,255,0.5);
    }

    #api-logs-container {
      flex: 1;
      overflow-y: auto;
      border-top: 1px solid #eee;
    }

    .api-log-item {
      padding: 8px 12px;
      border-bottom: 1px solid #eee;
      font-size: 12px;
      cursor: pointer;
      transition: background 0.2s;
    }

    .api-log-item:hover {
      background: #f5f5f5;
    }

    .api-log-item.success { background: #f6ffed; border-left: 3px solid #52c41a; }
    .api-log-item.warning { background: #fffbe6; border-left: 3px solid #faad14; }
    .api-log-item.error { background: #fff5f5; border-left: 3px solid #f5222d; }

    .api-method {
      font-weight: bold;
      margin-right: 4px;
    }

    .api-method.get { color: #52c41a; }
    .api-method.post { color: #1890ff; }
    .api-method.put { color: #faad14; }
    .api-method.delete { color: #f5222d; }

    .api-time {
      float: right;
      font-size: 11px;
      color: #999;
    }

    .api-url {
      color: #666;
      word-break: break-all;
      margin: 4px 0;
      font-size: 11px;
    }

    .api-status {
      font-size: 11px;
      margin-top: 4px;
    }

    .api-status.success { color: #52c41a; }
    .api-status.error { color: #f5222d; }

    .api-details {
      background: #f9f9f9;
      padding: 8px;
      border-radius: 3px;
      margin-top: 6px;
      max-height: 200px;
      overflow-y: auto;
      font-size: 10px;
    }

    .api-details-title {
      font-weight: bold;
      margin-bottom: 4px;
      color: #333;
    }

    .api-details-item {
      word-break: break-all;
      margin-bottom: 4px;
      padding: 4px;
      background: white;
      border-radius: 2px;
    }

    #api-monitor-stats {
      padding: 8px 12px;
      background: #f9f9f9;
      border-top: 1px solid #eee;
      font-size: 11px;
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 4px;
    }

    .stat-item {
      text-align: center;
      padding: 4px;
    }

    .stat-label {
      color: #999;
      font-size: 10px;
    }

    .stat-value {
      font-weight: bold;
      color: #333;
    }
  `);

  // ========== 拦截 Fetch ==========
  const originalFetch = window.fetch;
  window.fetch = function(...args) {
    const startTime = performance.now();
    const [resource, config] = args;
    const method = (config?.method || 'GET').toUpperCase();
    const url = typeof resource === 'string' ? resource : resource.url;

    return originalFetch.apply(this, args)
      .then(response => {
        const endTime = performance.now();
        const duration = endTime - startTime;

        // 记录日志
        logRequest({
          method,
          url,
          status: response.status,
          duration,
          type: 'fetch',
          headers: response.headers,
        });

        return response;
      })
      .catch(error => {
        logRequest({
          method,
          url,
          status: 0,
          duration: performance.now() - startTime,
          type: 'fetch',
          error: error.message,
        });
        throw error;
      });
  };

  // ========== 拦截 XMLHttpRequest ==========
  const originalOpen = XMLHttpRequest.prototype.open;
  const originalSend = XMLHttpRequest.prototype.send;

  XMLHttpRequest.prototype.open = function(method, url) {
    this._method = method;
    this._url = url;
    this._startTime = performance.now();
    return originalOpen.apply(this, arguments);
  };

  XMLHttpRequest.prototype.send = function() {
    this.addEventListener('load', function() {
      const duration = performance.now() - this._startTime;
      logRequest({
        method: this._method,
        url: this._url,
        status: this.status,
        duration,
        type: 'xhr',
        responseSize: this.responseText?.length || 0,
      });
    });

    return originalSend.apply(this, arguments);
  };

  // ========== 记录请求 ==========
  function logRequest(info) {
    if (!isMonitoring) return;

    const log = {
      id: Date.now() + Math.random(),
      method: info.method,
      url: info.url,
      status: info.status,
      duration: info.duration,
      timestamp: new Date(),
      type: info.type,
      error: info.error,
      responseSize: info.responseSize,
    };

    // 判断状态
    if (info.status === 0) {
      log.state = 'error';
    } else if (info.status >= 400) {
      log.state = 'error';
    } else if (info.duration > CONFIG.errorThreshold) {
      log.state = 'error';
    } else if (info.duration > CONFIG.warningThreshold) {
      log.state = 'warning';
    } else {
      log.state = 'success';
    }

    requestLogs.unshift(log);
    if (requestLogs.length > CONFIG.maxLogs) {
      requestLogs.pop();
    }

    updateMonitor();
  }

  // ========== UI 更新 ==========
  function updateMonitor() {
    const container = document.getElementById('api-logs-container');
    if (!container) return;

    container.innerHTML = requestLogs.map(log => `
      <div class="api-log-item ${log.state}">
        <div>
          <span class="api-method ${log.method.toLowerCase()}">${log.method}</span>
          <span class="api-time">${log.duration.toFixed(0)}ms</span>
        </div>
        <div class="api-url">${log.url.substring(0, 50)}...</div>
        <div class="api-status ${log.state}">
          ${log.status > 0 ? `Status: ${log.status}` : 'Failed'} 
          ${log.responseSize ? `| ${(log.responseSize / 1024).toFixed(1)}KB` : ''}
        </div>
      </div>
    `).join('');

    // 更新统计信息
    updateStats();
  }

  function updateStats() {
    const stats = document.getElementById('api-monitor-stats');
    if (!stats) return;

    const total = requestLogs.length;
    const errors = requestLogs.filter(log => log.state === 'error').length;
    const avgDuration = total > 0 
      ? (requestLogs.reduce((sum, log) => sum + log.duration, 0) / total).toFixed(0)
      : 0;
    const maxDuration = total > 0 
      ? Math.max(...requestLogs.map(log => log.duration)).toFixed(0)
      : 0;

    stats.innerHTML = `
      <div class="stat-item">
        <div class="stat-label">总请求</div>
        <div class="stat-value">${total}</div>
      </div>
      <div class="stat-item">
        <div class="stat-label">错误数</div>
        <div class="stat-value" style="color: ${errors > 0 ? '#f5222d' : '#52c41a'}">${errors}</div>
      </div>
      <div class="stat-item">
        <div class="stat-label">平均时间</div>
        <div class="stat-value">${avgDuration}ms</div>
      </div>
      <div class="stat-item">
        <div class="stat-label">最大时间</div>
        <div class="stat-value" style="color: ${maxDuration > CONFIG.errorThreshold ? '#f5222d' : '#faad14'}">${maxDuration}ms</div>
      </div>
    `;
  }

  // ========== 创建 UI ==========
  function createMonitorUI() {
    const monitor = document.createElement('div');
    monitor.id = 'aiops-api-monitor';
    monitor.innerHTML = `
      <div id="api-monitor-header">
        <span>🔍 API 监控</span>
        <div>
          <button class="api-monitor-btn" id="btn-toggle-monitor">暂停</button>
          <button class="api-monitor-btn" id="btn-clear-logs">清空</button>
          <button class="api-monitor-btn" id="btn-close-monitor">关闭</button>
        </div>
      </div>
      <div id="api-logs-container"></div>
      <div id="api-monitor-stats">
        <div class="stat-item"><div class="stat-label">总请求</div><div class="stat-value">0</div></div>
        <div class="stat-item"><div class="stat-label">错误数</div><div class="stat-value">0</div></div>
        <div class="stat-item"><div class="stat-label">平均时间</div><div class="stat-value">0ms</div></div>
        <div class="stat-item"><div class="stat-label">最大时间</div><div class="stat-value">0ms</div></div>
      </div>
    `;

    document.body.appendChild(monitor);

    // 绑定事件
    document.getElementById('btn-toggle-monitor').addEventListener('click', function() {
      isMonitoring = !isMonitoring;
      this.textContent = isMonitoring ? '暂停' : '继续';
    });

    document.getElementById('btn-clear-logs').addEventListener('click', function() {
      requestLogs = [];
      updateMonitor();
    });

    document.getElementById('btn-close-monitor').addEventListener('click', function() {
      monitor.style.display = 'none';
    });
  }

  // ========== 快捷键 ==========
  document.addEventListener('keydown', (e) => {
    if (e.altKey && (e.key === 'a' || e.key === 'A')) {
      e.preventDefault();
      const monitor = document.getElementById('aiops-api-monitor');
      if (monitor) {
        monitor.style.display = monitor.style.display === 'none' ? 'flex' : 'none';
      }
    }
  });

  // ========== 初始化 ==========
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', createMonitorUI);
  } else {
    createMonitorUI();
  }

  console.log('✅ AIOPS API 调试监控工具已加载 (Alt+A 显示/隐藏)');
})();
