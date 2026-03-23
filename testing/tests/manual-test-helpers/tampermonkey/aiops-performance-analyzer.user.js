// ==UserScript==
// @name         AIOPS 性能诊断工具
// @namespace    http://localhost:8000/
// @version      2.0
// @description  详细性能指标、瓶颈分析、基准对比
// @author       AIOPS Test Team
// @match        http://localhost:8000/*
// @match        http://localhost:*/*
// @grant        GM_addStyle
// @license      MIT
// ==/UserScript==

(function() {
  'use strict';

  GM_addStyle(`
    #aiops-perf-tool {
      position: fixed;
      top: 20px;
      right: 20px;
      width: 420px;
      max-height: 600px;
      background: white;
      border: 1px solid #ddd;
      border-radius: 4px;
      box-shadow: 0 2px 8px rgba(0,0,0,0.15);
      z-index: 9995;
      font-family: 'Courier New', monospace;
      overflow: hidden;
      display: flex;
      flex-direction: column;
    }

    #perf-header {
      background: linear-gradient(135deg, #52c41a 0%, #95de64 100%);
      color: white;
      padding: 12px 16px;
      font-weight: bold;
      display: flex;
      justify-content: space-between;
      align-items: center;
    }

    .perf-btn {
      background: rgba(255,255,255,0.3);
      color: white;
      border: 1px solid rgba(255,255,255,0.5);
      padding: 4px 8px;
      border-radius: 3px;
      cursor: pointer;
      font-size: 11px;
      margin-left: 4px;
    }

    #perf-content {
      flex: 1;
      overflow-y: auto;
      padding: 12px;
      font-size: 11px;
    }

    .perf-metric {
      margin-bottom: 12px;
      padding: 8px;
      background: #f9f9f9;
      border-left: 3px solid #52c41a;
      border-radius: 3px;
    }

    .perf-metric-title {
      font-weight: bold;
      color: #333;
      margin-bottom: 4px;
    }

    .perf-metric-value {
      display: flex;
      justify-content: space-between;
      margin: 2px 0;
      padding: 2px 4px;
    }

    .perf-metric-label {
      color: #666;
    }

    .perf-metric-number {
      font-weight: bold;
      color: #333;
    }

    .perf-metric-number.good { color: #52c41a; }
    .perf-metric-number.warning { color: #faad14; }
    .perf-metric-number.bad { color: #f5222d; }

    .perf-chart {
      background: white;
      border: 1px solid #ddd;
      padding: 8px;
      border-radius: 3px;
      margin-top: 6px;
      font-size: 10px;
    }

    .perf-bar {
      height: 20px;
      background: linear-gradient(90deg, #52c41a 0%, #95de64 100%);
      border-radius: 2px;
      margin: 2px 0;
      display: flex;
      align-items: center;
      padding: 0 4px;
      color: white;
      overflow: hidden;
    }

    .perf-bar.warning { background: linear-gradient(90deg, #faad14 0%, #ffc53d 100%); }
    .perf-bar.bad { background: linear-gradient(90deg, #f5222d 0%, #ff7a45 100%); }
  `);

  let perfData = {};

  // ========== 获取性能数据 ==========
  function collectPerformanceData() {
    // Navigation Timing
    const navigation = performance.getEntriesByType('navigation')[0];
    if (navigation) {
      perfData = {
        // DNS 查询
        dns: Math.round(navigation.domainLookupEnd - navigation.domainLookupStart),
        // 建立连接
        tcp: Math.round(navigation.connectEnd - navigation.connectStart),
        // 时间到第一个字节
        ttfb: Math.round(navigation.responseStart - navigation.requestStart),
        // 完整响应
        download: Math.round(navigation.responseEnd - navigation.responseStart),
        // DOM 解析
        domParse: Math.round(navigation.domContentLoadedEventStart - navigation.domLoading),
        // DOM 内容加载
        domContent: Math.round(navigation.domContentLoadedEventEnd - navigation.domContentLoadedEventStart),
        // 资源加载
        resourceLoad: Math.round(navigation.loadEventStart - navigation.domContentLoadedEventEnd),
        // 页面加载总时间
        pageLoad: Math.round(navigation.loadEventEnd - navigation.fetchStart),
      };
    }

    // 关键指标 (Core Web Vitals)
    if (window.PerformanceObserver) {
      try {
        new PerformanceObserver((list) => {
          list.getEntries().forEach((entry) => {
            if (entry.name === 'largest-contentful-paint') {
              perfData.lcp = Math.round(entry.renderTime || entry.loadTime);
            }
          });
        }).observe({ entryTypes: ['largest-contentful-paint'] });
      } catch (e) {}
    }

    // 内存使用 (如果可用)
    if (performance.memory) {
      perfData.usedMemory = Math.round(performance.memory.usedJSHeapSize / 1048576);
      perfData.totalMemory = Math.round(performance.memory.totalJSHeapSize / 1048576);
    }

    // 网络请求统计
    const resources = performance.getEntriesByType('resource');
    perfData.totalRequests = resources.length;
    perfData.totalPayload = Math.round(resources.reduce((sum, r) => sum + (r.transferSize || 0), 0) / 1024);

    // 最慢的资源
    const slowestResources = resources
      .sort((a, b) => (b.duration || 0) - (a.duration || 0))
      .slice(0, 3);
    perfData.slowestResources = slowestResources;

    return perfData;
  }

  // ========== 创建 UI ==========
  function createPerfTool() {
    const tool = document.createElement('div');
    tool.id = 'aiops-perf-tool';
    tool.innerHTML = `
      <div id="perf-header">
        <span>⚡ 性能诊断工具</span>
        <div>
          <button class="perf-btn" id="btn-refresh-perf">刷新</button>
          <button class="perf-btn" id="btn-close-perf">关闭</button>
        </div>
      </div>
      <div id="perf-content"></div>
    `;

    document.body.appendChild(tool);
    updatePerfDisplay();

    document.getElementById('btn-refresh-perf').addEventListener('click', updatePerfDisplay);
    document.getElementById('btn-close-perf').addEventListener('click', () => {
      tool.style.display = 'none';
    });
  }

  function updatePerfDisplay() {
    perfData = collectPerformanceData();
    const content = document.getElementById('perf-content');

    const getColor = (value, good, warning) => {
      if (value <= good) return 'good';
      if (value <= warning) return 'warning';
      return 'bad';
    };

    let html = `
      <!-- 关键指标 -->
      <div class="perf-metric">
        <div class="perf-metric-title">📊 关键指标</div>
        <div class="perf-metric-value">
          <span class="perf-metric-label">页面加载时间</span>
          <span class="perf-metric-number ${getColor(perfData.pageLoad, 1000, 3000)}">${perfData.pageLoad}ms</span>
        </div>
        <div class="perf-metric-value">
          <span class="perf-metric-label">首字节时间 (TTFB)</span>
          <span class="perf-metric-number ${getColor(perfData.ttfb, 500, 1000)}">${perfData.ttfb}ms</span>
        </div>
        <div class="perf-metric-value">
          <span class="perf-metric-label">最大内容绘制 (LCP)</span>
          <span class="perf-metric-number ${getColor(perfData.lcp || 0, 2500, 4000)}">${perfData.lcp || 'N/A'}ms</span>
        </div>
      </div>

      <!-- 阶段性能 -->
      <div class="perf-metric">
        <div class="perf-metric-title">🔍 阶段性能分析</div>
        <div class="perf-chart">
          <div style="margin-bottom: 2px;">
            <div style="font-weight: bold; color: #333;">DNS 查询</div>
            <div class="perf-bar ${getColor(perfData.dns, 100, 200)}" style="width: ${Math.min(perfData.dns / 5, 100)}%;">
              ${perfData.dns}ms
            </div>
          </div>
          <div style="margin-bottom: 2px;">
            <div style="font-weight: bold; color: #333;">建立连接</div>
            <div class="perf-bar ${getColor(perfData.tcp, 100, 300)}" style="width: ${Math.min(perfData.tcp / 5, 100)}%;">
              ${perfData.tcp}ms
            </div>
          </div>
          <div style="margin-bottom: 2px;">
            <div style="font-weight: bold; color: #333;">网络延迟</div>
            <div class="perf-bar ${getColor(perfData.ttfb, 500, 1000)}" style="width: ${Math.min(perfData.ttfb / 10, 100)}%;">
              ${perfData.ttfb}ms
            </div>
          </div>
          <div style="margin-bottom: 2px;">
            <div style="font-weight: bold; color: #333;">DOM 解析</div>
            <div class="perf-bar ${getColor(perfData.domParse, 500, 1000)}" style="width: ${Math.min(perfData.domParse / 10, 100)}%;">
              ${perfData.domParse}ms
            </div>
          </div>
        </div>
      </div>

      <!-- 资源统计 -->
      <div class="perf-metric">
        <div class="perf-metric-title">📦 资源统计</div>
        <div class="perf-metric-value">
          <span class="perf-metric-label">总请求数</span>
          <span class="perf-metric-number">${perfData.totalRequests}</span>
        </div>
        <div class="perf-metric-value">
          <span class="perf-metric-label">总传输数据</span>
          <span class="perf-metric-number">${perfData.totalPayload}KB</span>
        </div>
      </div>

      <!-- 内存使用 -->
      ${perfData.usedMemory ? `
        <div class="perf-metric">
          <div class="perf-metric-title">💾 内存使用</div>
          <div class="perf-metric-value">
            <span class="perf-metric-label">已用</span>
            <span class="perf-metric-number ${getColor(perfData.usedMemory, 100, 200)}">${perfData.usedMemory}MB</span>
          </div>
          <div class="perf-metric-value">
            <span class="perf-metric-label">总计</span>
            <span class="perf-metric-number">${perfData.totalMemory}MB</span>
          </div>
        </div>
      ` : ''}

      <!-- 最慢的资源 -->
      <div class="perf-metric">
        <div class="perf-metric-title">🐌 最慢的资源</div>
        <div class="perf-chart">
          ${perfData.slowestResources.map((r, idx) => `
            <div style="margin: 4px 0; padding: 4px; background: white; border-radius: 2px;">
              <div style="font-size: 10px; color: #666; margin-bottom: 2px;">
                ${idx + 1}. ${r.name.substring(r.name.lastIndexOf('/') + 1).substring(0, 30)}
              </div>
              <div class="perf-bar ${getColor(r.duration, 500, 1000)}" style="width: ${Math.min(r.duration / 10, 100)}%;">
                ${Math.round(r.duration)}ms
              </div>
            </div>
          `).join('')}
        </div>
      </div>

      <!-- 性能评分 -->
      ${generatePerformanceScore()}
    `;

    content.innerHTML = html;
  }

  function generatePerformanceScore() {
    let score = 100;
    
    // 减分标准
    if (perfData.pageLoad > 3000) score -= 20;
    if (perfData.pageLoad > 5000) score -= 30;
    if (perfData.ttfb > 1000) score -= 15;
    if (perfData.totalPayload > 5000) score -= 15;
    if (perfData.usedMemory && perfData.usedMemory > 200) score -= 10;

    let level = '优秀';
    let color = 'good';
    if (score < 50) { level = '差'; color = 'bad'; }
    else if (score < 70) { level = '良好'; color = 'warning'; }
    else { level = '优秀'; color = 'good'; }

    return `
      <div class="perf-metric" style="border-left-color: ${color === 'good' ? '#52c41a' : color === 'warning' ? '#faad14' : '#f5222d'};">
        <div class="perf-metric-title">📈 性能评分</div>
        <div style="text-align: center; padding: 12px;">
          <div style="font-size: 32px; font-weight: bold; color: ${color === 'good' ? '#52c41a' : color === 'warning' ? '#faad14' : '#f5222d'};">${score}</div>
          <div style="color: #666; margin-top: 4px;">${level}</div>
        </div>
      </div>
    `;
  }

  // ========== 快捷键 ==========
  document.addEventListener('keydown', (e) => {
    if (e.altKey && (e.key === 'e' || e.key === 'E')) {
      e.preventDefault();
      const tool = document.getElementById('aiops-perf-tool');
      if (tool) {
        tool.style.display = tool.style.display === 'none' ? 'flex' : 'none';
      }
    }
  });

  // ========== 初始化 ==========
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', createPerfTool);
  } else {
    createPerfTool();
  }

  console.log('✅ AIOPS 性能诊断工具已加载 (Alt+E 显示/隐藏)');
})();
