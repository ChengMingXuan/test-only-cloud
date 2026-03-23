// ==UserScript==
// @name         AIOPS 系统运行状态监控
// @namespace    http://localhost:8000/
// @version      2.0
// @description  DOM 节点、事件监听、内存、网络、浏览器存储、Service Worker 状态
// @author       AIOPS Test Team
// @match        http://localhost:8000/*
// @match        http://localhost:*/*
// @grant        GM_addStyle
// ==/UserScript==

(function() {
  'use strict';

  GM_addStyle(`
    #aiops-system-monitor {
      position: fixed;
      bottom: 100px;
      right: 20px;
      width: 360px;
      max-height: 650px;
      background: white;
      border: 1px solid #ddd;
      border-radius: 4px;
      box-shadow: 0 2px 8px rgba(0,0,0,0.15);
      z-index: 9997;
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
      display: flex;
      flex-direction: column;
    }

    #monitor-header {
      background: linear-gradient(135deg, #eb2f96 0%, #ff85c0 100%);
      color: white;
      padding: 12px 16px;
      font-weight: bold;
      display: flex;
      justify-content: space-between;
      align-items: center;
      border-radius: 4px 4px 0 0;
    }

    .monitor-btn {
      background: rgba(255,255,255,0.3);
      color: white;
      border: 1px solid rgba(255,255,255,0.5);
      padding: 4px 8px;
      border-radius: 3px;
      cursor: pointer;
      font-size: 11px;
      margin-left: 4px;
    }

    #monitor-content {
      flex: 1;
      overflow-y: auto;
      padding: 12px;
      font-size: 11px;
      background: #fafafa;
    }

    .monitor-group {
      background: white;
      border: 1px solid #f0f0f0;
      border-radius: 4px;
      padding: 10px;
      margin-bottom: 10px;
      border-left: 3px solid #eb2f96;
    }

    .monitor-group-title {
      font-weight: bold;
      color: #333;
      margin-bottom: 8px;
      font-size: 12px;
    }

    .monitor-item {
      display: flex;
      justify-content: space-between;
      margin: 6px 0;
      padding: 4px 6px;
      background: #f9f9f9;
      border-radius: 2px;
    }

    .monitor-label {
      color: #666;
      flex: 1;
    }

    .monitor-value {
      font-weight: bold;
      color: #333;
      font-family: monospace;
      text-align: right;
      flex: 0 0 auto;
      margin-left: 8px;
    }

    .monitor-value.good { color: #52c41a; }
    .monitor-value.warning { color: #faad14; }
    .monitor-value.bad { color: #f5222d; }

    .monitor-status {
      display: inline-block;
      padding: 2px 6px;
      border-radius: 2px;
      font-size: 10px;
      font-weight: bold;
    }

    .monitor-status.online { background: #f6ffed; color: #52c41a; }
    .monitor-status.offline { background: #fff1f0; color: #f5222d; }
    .monitor-status.active { background: #e6f7ff; color: #0050b3; }
    .monitor-status.inactive { background: #f5f5f5; color: #999; }
    .monitor-status.abnormal { background: #fffbe6; color: #faad14; }

    .monitor-progress {
      background: #f0f0f0;
      height: 6px;
      border-radius: 3px;
      margin-top: 4px;
      overflow: hidden;
    }

    .monitor-progress-bar {
      height: 100%;
      background: linear-gradient(90deg, #eb2f96 0%, #ff85c0 100%);
      transition: width 0.3s;
    }

    .monitor-alert {
      background: #fff1f0;
      border-left: 3px solid #f5222d;
      padding: 8px;
      margin: 6px 0;
      border-radius: 2px;
      color: #f5222d;
      font-size: 10px;
    }

    .monitor-alert.warning {
      background: #fffbe6;
      border-left-color: #faad14;
      color: #faad14;
    }
  `);

  let monitorData = {
    domNodes: 0,
    eventListeners: 0,
    memory: { usedJSHeapSize: 0, totalJSHeapSize: 0 },
    networkStatus: 'online',
    storageStatus: { localStorage: 0, sessionStorage: 0, indexedDB: 'unknown' },
    swStatus: 'unknown',
    pageHeight: 0,
    focusedElement: 'unknown',
    alerts: [],
  };

  // ========== 收集监控数据 ==========
  function collectMonitorData() {
    // DOM 节点计数
    monitorData.domNodes = document.documentElement.querySelectorAll('*').length;

    // 估算事件监听器 (基于常见事件)
    const commonEvents = ['click', 'change', 'submit', 'input', 'scroll', 'load'];
    let estimatedListeners = 0;
    document.querySelectorAll('*').forEach(el => {
      commonEvents.forEach(evt => {
        if (el['on' + evt] !== null) estimatedListeners++;
      });
    });
    monitorData.eventListeners = estimatedListeners;

    // 内存使用
    if (performance.memory) {
      monitorData.memory = {
        usedJSHeapSize: Math.round(performance.memory.usedJSHeapSize / 1048576),
        totalJSHeapSize: Math.round(performance.memory.totalJSHeapSize / 1048576),
        jsHeapSizeLimit: Math.round(performance.memory.jsHeapSizeLimit / 1048576),
      };

      // 检测内存泄漏
      if (monitorData.memory.usedJSHeapSize > monitorData.memory.jsHeapSizeLimit * 0.8) {
        addAlert('warning', '⚠️ 内存使用超过 80%，可能存在内存泄漏');
      }
    }

    // 网络状态
    monitorData.networkStatus = navigator.onLine ? 'online' : 'offline';

    // 浏览器存储大小
    try {
      let lsSize = 0;
      for (let key in localStorage) {
        if (localStorage.hasOwnProperty(key)) {
          lsSize += localStorage[key].length + key.length;
        }
      }
      monitorData.storageStatus.localStorage = Math.round(lsSize / 1024);
    } catch (e) {}

    try {
      let ssSize = 0;
      for (let key in sessionStorage) {
        if (sessionStorage.hasOwnProperty(key)) {
          ssSize += sessionStorage[key].length + key.length;
        }
      }
      monitorData.storageStatus.sessionStorage = Math.round(ssSize / 1024);
    } catch (e) {}

    // Service Worker 状态
    if ('serviceWorker' in navigator) {
      navigator.serviceWorker.getRegistrations().then(registrations => {
        monitorData.swStatus = registrations.length > 0 ? `active (${registrations.length})` : 'inactive';
      });
    }

    // 页面维度
    monitorData.pageHeight = document.documentElement.scrollHeight;

    // 已聚焦元素
    const focused = document.activeElement;
    if (focused && focused !== document.body && focused !== document.documentElement) {
      monitorData.focusedElement = focused.tagName + (focused.id ? `#${focused.id}` : '') + (focused.className ? `.${focused.className.split(' ')[0]}` : '');
    }
  }

  function addAlert(type, message) {
    monitorData.alerts.push({ type, message, time: new Date().toLocaleTimeString() });
    if (monitorData.alerts.length > 10) {
      monitorData.alerts.shift();
    }
  }

  // ========== 创建 UI ==========
  function createSystemMonitor() {
    const monitor = document.createElement('div');
    monitor.id = 'aiops-system-monitor';
    monitor.innerHTML = `
      <div id="monitor-header">
        <span>🖥️ 系统运行监控</span>
        <div>
          <button class="monitor-btn" id="btn-refresh-monitor">刷新</button>
          <button class="monitor-btn" id="btn-close-monitor">关闭</button>
        </div>
      </div>
      <div id="monitor-content"></div>
    `;

    document.body.appendChild(monitor);
    updateMonitorDisplay();

    document.getElementById('btn-refresh-monitor').addEventListener('click', updateMonitorDisplay);
    document.getElementById('btn-close-monitor').addEventListener('click', () => {
      monitor.style.display = 'none';
    });

    // 实时监控，每2秒更新一次
    setInterval(updateMonitorDisplay, 2000);
    
    // 网络状态变化
    window.addEventListener('online', () => {
      monitorData.networkStatus = 'online';
      addAlert('warning', '✅ 网络已连接');
    });

    window.addEventListener('offline', () => {
      monitorData.networkStatus = 'offline';
      addAlert('warning', '❌ 网络已断开');
    });
  }

  function updateMonitorDisplay() {
    collectMonitorData();
    const content = document.getElementById('monitor-content');

    const getMemoryColor = (used, total) => {
      const percent = (used / total) * 100;
      if (percent > 80) return 'bad';
      if (percent > 60) return 'warning';
      return 'good';
    };

    let html = `
      <!-- 页面性能 -->
      <div class="monitor-group">
        <div class="monitor-group-title">📄 页面结构</div>
        <div class="monitor-item">
          <span class="monitor-label">DOM 节点</span>
          <span class="monitor-value ${monitorData.domNodes > 5000 ? 'warning' : 'good'}">${monitorData.domNodes}</span>
        </div>
        <div class="monitor-item">
          <span class="monitor-label">事件监听</span>
          <span class="monitor-value">${monitorData.eventListeners}</span>
        </div>
        <div class="monitor-item">
          <span class="monitor-label">页面高度</span>
          <span class="monitor-value">${monitorData.pageHeight}px</span>
        </div>
        <div class="monitor-item">
          <span class="monitor-label">焦点元素</span>
          <span class="monitor-value" style="font-size: 9px;">${monitorData.focusedElement}</span>
        </div>
      </div>

      <!-- 内存使用 -->
      ${monitorData.memory.usedJSHeapSize ? `
        <div class="monitor-group">
          <div class="monitor-group-title">💾 内存使用</div>
          <div class="monitor-item">
            <span class="monitor-label">已用 / 总计</span>
            <span class="monitor-value ${getMemoryColor(monitorData.memory.usedJSHeapSize, monitorData.memory.jsHeapSizeLimit)}">
              ${monitorData.memory.usedJSHeapSize}MB / ${monitorData.memory.jsHeapSizeLimit}MB
            </span>
          </div>
          <div class="monitor-progress">
            <div class="monitor-progress-bar" style="width: ${(monitorData.memory.usedJSHeapSize / monitorData.memory.jsHeapSizeLimit) * 100}%;"></div>
          </div>
          <div style="margin-top: 6px; font-size: 10px; color: #666;">
            堆大小: ${monitorData.memory.totalJSHeapSize}MB
          </div>
        </div>
      ` : ''}

      <!-- 网络状态 -->
      <div class="monitor-group">
        <div class="monitor-group-title">🌐 网络状态</div>
        <div class="monitor-item">
          <span class="monitor-label">连接状态</span>
          <span class="monitor-status ${monitorData.networkStatus === 'online' ? 'online' : 'offline'}">
            ${monitorData.networkStatus === 'online' ? '✅ 在线' : '❌ 离线'}
          </span>
        </div>
        <div class="monitor-item">
          <span class="monitor-label">连接类型</span>
          <span class="monitor-value" style="font-size: 9px;">
            ${navigator.connection?.effectiveType || 'unknown'}
          </span>
        </div>
      </div>

      <!-- 浏览器存储 -->
      <div class="monitor-group">
        <div class="monitor-group-title">📦 浏览器存储</div>
        <div class="monitor-item">
          <span class="monitor-label">localStorage</span>
          <span class="monitor-value">${monitorData.storageStatus.localStorage}KB</span>
        </div>
        <div class="monitor-item">
          <span class="monitor-label">sessionStorage</span>
          <span class="monitor-value">${monitorData.storageStatus.sessionStorage}KB</span>
        </div>
        <div class="monitor-item">
          <span class="monitor-label">IndexedDB</span>
          <span class="monitor-status ${monitorData.storageStatus.indexedDB === 'unknown' ? 'inactive' : 'active'}">
            ${monitorData.storageStatus.indexedDB === 'unknown' ? '未测试' : '可用'}
          </span>
        </div>
      </div>

      <!-- Service Worker -->
      <div class="monitor-group">
        <div class="monitor-group-title">⚙️ Service Worker</div>
        <div class="monitor-item">
          <span class="monitor-label">状态</span>
          <span class="monitor-status ${monitorData.swStatus.includes('active') ? 'active' : 'inactive'}">
            ${monitorData.swStatus === 'unknown' ? '未支持' : monitorData.swStatus}
          </span>
        </div>
      </div>

      <!-- 浏览器信息 -->
      <div class="monitor-group">
        <div class="monitor-group-title">ℹ️ 浏览器信息</div>
        <div class="monitor-item">
          <span class="monitor-label">用户代理</span>
          <span class="monitor-value" style="font-size: 8px; max-width: 150px; overflow: hidden; text-overflow: ellipsis;">
            ${navigator.userAgent.substring(0, 30)}...
          </span>
        </div>
        <div class="monitor-item">
          <span class="monitor-label">语言</span>
          <span class="monitor-value">${navigator.language}</span>
        </div>
        <div class="monitor-item">
          <span class="monitor-label">时区</span>
          <span class="monitor-value">${-new Date().getTimezoneOffset() / 60}</span>
        </div>
      </div>

      <!-- 警告/提示 -->
      ${monitorData.alerts.length > 0 ? `
        <div class="monitor-group" style="border-left-color: #faad14;">
          <div class="monitor-group-title">⚠️ 系统警告 (最近 ${monitorData.alerts.length})</div>
          ${monitorData.alerts.map(alert => `
            <div class="monitor-alert ${alert.type === 'warning' ? 'warning' : ''}">
              <div style="font-size: 10px; margin-bottom: 2px;">${alert.time}</div>
              <div>${alert.message}</div>
            </div>
          `).join('')}
        </div>
      ` : ''}
    `;

    content.innerHTML = html;
  }

  // ========== 快捷键 ==========
  document.addEventListener('keydown', (e) => {
    if (e.altKey && (e.key === 'm' || e.key === 'M')) {
      e.preventDefault();
      const monitor = document.getElementById('aiops-system-monitor');
      if (monitor) {
        monitor.style.display = monitor.style.display === 'none' ? 'flex' : 'none';
      }
    }
  });

  // ========== 初始化 ==========
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', createSystemMonitor);
  } else {
    createSystemMonitor();
  }

  console.log('✅ AIOPS 系统运行监控已加载 (Alt+M 显示/隐藏)');
})();
