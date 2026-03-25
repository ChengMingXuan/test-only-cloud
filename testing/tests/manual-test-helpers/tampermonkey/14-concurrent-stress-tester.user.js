// ==UserScript==
// @name         AIOPS 并发压力与竞态检测器 (Concurrent Stress Tester)
// @namespace    http://localhost:8000/testing
// @version      1.0.0
// @description  并发请求压力测试、竞态条件检测、幂等性验证、双重提交防护检查
// @author       AIOPS Test Team
// @match        http://localhost:8000/*
// @match        http://localhost:*/*
// @match        http://localhost:*/*
// @grant        GM_setValue
// @grant        GM_getValue
// @grant        GM_notification
// @grant        GM_registerMenuCommand
// ==/UserScript==

(function () {
  'use strict';

  // ============================
  // 配置
  // ============================
  const CONFIG = {
    DEFAULT_CONCURRENCY: 5,
    DEFAULT_ITERATIONS: 10,
    MAX_CONCURRENCY: 50,
    TIMEOUT_MS: 30000,
  };

  // ============================
  // 预定义测试用例
  // ============================
  const TEST_CASES = {
    // ---- 双重提交测试 ----
    'double-submit': {
      name: '双重提交防护',
      description: '同一请求快速发送两次，验证幂等性',
      tests: [
        { name: '创建工单双重提交', method: 'POST', url: '/api/workorder/create', body: { title: '双重提交测试', type: 'fault' }, concurrency: 2, delay: 0 },
        { name: '提现申请双重提交', method: 'POST', url: '/api/settlement/withdraw/apply', body: { amount: 100 }, concurrency: 2, delay: 0 },
        { name: '充电启动双重提交', method: 'POST', url: '/api/charging/order/start', body: { deviceId: 'test-device' }, concurrency: 2, delay: 0 },
        { name: '审批操作双重提交', method: 'POST', url: '/api/workorder/approve', body: { orderId: 'test', action: 'approve' }, concurrency: 2, delay: 0 },
      ],
    },

    // ---- 竞态条件测试 ----
    'race-condition': {
      name: '竞态条件检测',
      description: '多个请求同时操作同一资源，检查数据一致性',
      tests: [
        { name: '同一库存并发领用', method: 'POST', url: '/api/workorder/spare-part/apply', body: { partId: 'test-part', quantity: 1 }, concurrency: 5, expectOnlyOneSuccess: true },
        { name: '同一工单并发接单', method: 'POST', url: '/api/workorder/accept', body: { orderId: 'test-order' }, concurrency: 3, expectOnlyOneSuccess: true },
        { name: '同一充电桩并发启动', method: 'POST', url: '/api/charging/order/start', body: { deviceId: 'test-device' }, concurrency: 3, expectOnlyOneSuccess: true },
        { name: '同一钱包并发扣款', method: 'POST', url: '/api/account/payment', body: { amount: 50 }, concurrency: 5, checkBalance: true },
      ],
    },

    // ---- 乐观锁测试 ----
    'optimistic-lock': {
      name: '乐观锁验证',
      description: '并发更新同一记录，验证 RowVersion 机制',
      tests: [
        { name: '并发更新站点信息', method: 'PUT', url: '/api/station/{id}', body: { name: 'Updated' }, concurrency: 3, expectConflict: true },
        { name: '并发更新设备状态', method: 'PUT', url: '/api/device/{id}/status', body: { status: 'maintaining' }, concurrency: 3, expectConflict: true },
        { name: '并发修改工单', method: 'PUT', url: '/api/workorder/{id}', body: { description: 'Updated' }, concurrency: 3, expectConflict: true },
      ],
    },

    // ---- 幂等性测试 ----
    'idempotency': {
      name: '幂等性验证',
      description: '相同请求多次发送，验证结果一致且无副作用',
      tests: [
        { name: 'GET 请求幂等', method: 'GET', url: '/api/station/list', iterations: 10, expectSameResult: true },
        { name: 'DELETE 已删除资源', method: 'DELETE', url: '/api/device/{id}', iterations: 3, expectIdempotent: true },
        { name: '结算确认重复调用', method: 'POST', url: '/api/settlement/confirm', body: { id: 'test' }, iterations: 3, expectIdempotent: true },
      ],
    },

    // ---- 并发读写混合 ----
    'read-write-mix': {
      name: '并发读写混合',
      description: '读写请求同时进行，验证一致性',
      tests: [
        { name: '边读边写工单', readUrl: '/api/workorder/list', writeUrl: '/api/workorder/create', concurrency: 10, readRatio: 0.7 },
        { name: '边读边写设备', readUrl: '/api/device/list', writeUrl: '/api/device/update', concurrency: 10, readRatio: 0.8 },
      ],
    },
  };

  // ============================
  // 并发执行器
  // ============================
  class ConcurrentExecutor {
    constructor() {
      this.results = [];
      this.running = false;
    }

    getAuthHeaders() {
      const token = localStorage.getItem('token') || sessionStorage.getItem('token') || '';
      return {
        'Content-Type': 'application/json',
        'Authorization': token ? `Bearer ${token}` : '',
      };
    }

    async sendRequest(method, url, body) {
      const start = performance.now();
      try {
        const options = { method, headers: this.getAuthHeaders() };
        if (body && method !== 'GET') {
          options.body = JSON.stringify(body);
        }
        const response = await fetch(url, options);
        const duration = performance.now() - start;
        let data = null;
        try { data = await response.json(); } catch { /* 非 JSON 响应 */ }
        return { success: response.ok, status: response.status, duration: Math.round(duration), data };
      } catch (error) {
        return { success: false, status: 0, duration: Math.round(performance.now() - start), error: error.message };
      }
    }

    async runConcurrent(requests) {
      const start = performance.now();
      const promises = requests.map(req => this.sendRequest(req.method, req.url, req.body));
      const results = await Promise.allSettled(promises);
      const totalDuration = performance.now() - start;

      return {
        results: results.map(r => r.status === 'fulfilled' ? r.value : { success: false, error: r.reason?.message }),
        totalDuration: Math.round(totalDuration),
        successCount: results.filter(r => r.status === 'fulfilled' && r.value.success).length,
        failCount: results.filter(r => r.status === 'rejected' || (r.status === 'fulfilled' && !r.value.success)).length,
      };
    }

    analyzeResults(testCase, outcome) {
      const analysis = { testName: testCase.name, verdict: 'UNKNOWN', details: [] };

      if (testCase.expectOnlyOneSuccess) {
        if (outcome.successCount === 1) {
          analysis.verdict = 'PASS';
          analysis.details.push(`✅ 只有1个请求成功（共${outcome.results.length}个并发）`);
        } else if (outcome.successCount === 0) {
          analysis.verdict = 'WARN';
          analysis.details.push(`⚠️ 全部失败，可能缺少测试数据`);
        } else {
          analysis.verdict = 'FAIL';
          analysis.details.push(`❌ ${outcome.successCount}个请求成功，存在竞态问题！`);
        }
      } else if (testCase.concurrency === 2 && testCase.delay === 0) {
        // 双重提交：应该只创建一条
        if (outcome.successCount <= 1) {
          analysis.verdict = 'PASS';
          analysis.details.push('✅ 双重提交防护有效');
        } else {
          analysis.verdict = 'FAIL';
          analysis.details.push(`❌ 双重提交产生了${outcome.successCount}条记录！`);
        }
      } else if (testCase.expectConflict) {
        const conflictCount = outcome.results.filter(r => r.status === 409).length;
        if (conflictCount > 0) {
          analysis.verdict = 'PASS';
          analysis.details.push(`✅ 乐观锁生效，${conflictCount}个请求收到409冲突`);
        } else if (outcome.successCount === outcome.results.length) {
          analysis.verdict = 'FAIL';
          analysis.details.push('❌ 所有并发更新都成功了，乐观锁可能未生效！');
        }
      } else {
        analysis.verdict = outcome.failCount === 0 ? 'PASS' : 'WARN';
      }

      // 性能分析
      const durations = outcome.results.map(r => r.duration || 0).filter(d => d > 0);
      if (durations.length > 0) {
        analysis.details.push(`⏱️ 响应时间: min=${Math.min(...durations)}ms, max=${Math.max(...durations)}ms, avg=${Math.round(durations.reduce((a, b) => a + b, 0) / durations.length)}ms`);
      }

      return analysis;
    }
  }

  // ============================
  // UI 面板
  // ============================
  class StressTesterPanel {
    constructor() {
      this.executor = new ConcurrentExecutor();
      this.visible = false;
      this.testResults = [];
      this.init();
    }

    init() {
      this.createPanel();

      document.addEventListener('keydown', (e) => {
        if (e.ctrlKey && e.shiftKey && e.key === 'C') {
          e.preventDefault();
          this.toggle();
        }
      });

      GM_registerMenuCommand('⚡ 并发压力与竞态检测器', () => this.toggle());
    }

    createPanel() {
      this.panel = document.createElement('div');
      this.panel.id = 'aiops-stress-panel';
      this.panel.style.cssText = `
        position: fixed; top: 60px; left: 20px; width: 460px; max-height: 85vh;
        background: #1a1a2e; color: #eee; border-radius: 12px;
        box-shadow: 0 8px 32px rgba(0,0,0,0.4); z-index: 99999;
        font-family: 'Segoe UI', sans-serif; font-size: 13px;
        display: none; overflow: hidden;
      `;
      document.body.appendChild(this.panel);
      this.render();
    }

    toggle() {
      this.visible = !this.visible;
      this.panel.style.display = this.visible ? 'block' : 'none';
      if (this.visible) this.render();
    }

    async runTestSuite(suiteKey) {
      const suite = TEST_CASES[suiteKey];
      if (!suite) return;

      this.testResults = [];
      this.render();

      for (const testCase of suite.tests) {
        const concurrency = testCase.concurrency || CONFIG.DEFAULT_CONCURRENCY;
        const requests = [];
        for (let i = 0; i < concurrency; i++) {
          requests.push({
            method: testCase.method,
            url: window.location.origin + testCase.url,
            body: testCase.body,
          });
        }

        const outcome = await this.executor.runConcurrent(requests);
        const analysis = this.executor.analyzeResults(testCase, outcome);
        this.testResults.push(analysis);
        this.render();

        // 间隔防止过载
        await new Promise(resolve => setTimeout(resolve, 500));
      }

      GM_notification({
        title: 'AIOPS 并发测试完成',
        text: `${suite.name}: ${this.testResults.filter(r => r.verdict === 'PASS').length}/${this.testResults.length} 通过`,
        timeout: 5000,
      });
    }

    render() {
      const resultsHtml = this.testResults.map(r => {
        const colors = { PASS: '#4caf50', FAIL: '#f44336', WARN: '#ff9800', UNKNOWN: '#666' };
        const icons = { PASS: '✅', FAIL: '❌', WARN: '⚠️', UNKNOWN: '❓' };
        return `
          <div style="padding:8px 12px;margin:4px 0;background:#16213e;border-radius:6px;border-left:3px solid ${colors[r.verdict]};">
            <div><span>${icons[r.verdict]}</span> <strong>${r.testName}</strong> <span style="color:${colors[r.verdict]};float:right;">${r.verdict}</span></div>
            ${r.details.map(d => `<div style="font-size:11px;color:#aaa;margin-top:2px;">${d}</div>`).join('')}
          </div>
        `;
      }).join('');

      const passCount = this.testResults.filter(r => r.verdict === 'PASS').length;
      const failCount = this.testResults.filter(r => r.verdict === 'FAIL').length;

      this.panel.innerHTML = `
        <div style="background:linear-gradient(135deg,#1a0a2e,#3a0e6e);padding:12px 16px;display:flex;justify-content:space-between;align-items:center;">
          <span style="font-size:15px;font-weight:bold;">⚡ 并发压力与竞态检测器</span>
          <span style="cursor:pointer;font-size:18px;" onclick="document.getElementById('aiops-stress-panel').style.display='none'">✕</span>
        </div>

        <div style="padding:12px 16px;">
          <div style="margin-bottom:10px;font-weight:bold;color:#ce93d8;">🧪 选择测试套件</div>
          <div style="display:grid;grid-template-columns:1fr 1fr;gap:6px;">
            ${Object.entries(TEST_CASES).map(([key, suite]) => `
              <div style="padding:8px;background:#16213e;border-radius:6px;cursor:pointer;border:1px solid #333;text-align:center;"
                   onmouseover="this.style.borderColor='#9c27b0'" onmouseout="this.style.borderColor='#333'"
                   onclick="window.__aiopsStressPanel.runTestSuite('${key}')">
                <div style="font-size:12px;font-weight:bold;">${suite.name}</div>
                <div style="font-size:10px;color:#888;">${suite.tests.length} 个测试</div>
              </div>
            `).join('')}
          </div>
        </div>

        ${this.testResults.length > 0 ? `
          <div style="padding:8px 16px;background:#16213e;display:flex;gap:12px;font-size:12px;">
            <span>总计: ${this.testResults.length}</span>
            <span style="color:#4caf50;">通过: ${passCount}</span>
            <span style="color:#f44336;">失败: ${failCount}</span>
            <span style="color:#ff9800;">警告: ${this.testResults.length - passCount - failCount}</span>
          </div>
          <div style="max-height:45vh;overflow-y:auto;padding:8px 12px;">
            ${resultsHtml}
          </div>
          <div style="padding:8px 16px;border-top:1px solid #333;">
            <button onclick="navigator.clipboard.writeText(JSON.stringify(window.__aiopsStressPanel.testResults,null,2))"
                    style="width:100%;padding:8px;border:none;border-radius:6px;background:#9c27b0;color:#fff;cursor:pointer;">
              📋 复制测试报告
            </button>
          </div>
        ` : ''}
      `;
    }
  }

  // ============================
  // 双重提交按钮检测器（自动）
  // ============================
  class DoubleClickDetector {
    constructor() {
      this.init();
    }

    init() {
      // 监控所有按钮点击，检查是否有双击防护
      document.addEventListener('click', (e) => {
        const btn = e.target.closest('button, [role="button"], .ant-btn');
        if (!btn) return;

        // 检查按钮是否有 loading 或 disabled 状态
        const hasProtection = btn.disabled || btn.classList.contains('ant-btn-loading') || btn.getAttribute('aria-disabled') === 'true';
        if (!hasProtection && (btn.textContent.includes('提交') || btn.textContent.includes('确认') || btn.textContent.includes('保存') || btn.textContent.includes('创建'))) {
          // 在100ms后检查按钮是否变为了disabled/loading
          setTimeout(() => {
            const nowProtected = btn.disabled || btn.classList.contains('ant-btn-loading');
            if (!nowProtected) {
              console.warn(`[AIOPS 并发检测] ⚠️ 按钮"${btn.textContent.trim()}"点击后未设置 loading/disabled 状态，可能存在双重提交风险`);
            }
          }, 100);
        }
      }, true);
    }
  }

  // ============================
  // 初始化
  // ============================
  const panel = new StressTesterPanel();
  window.__aiopsStressPanel = panel;
  new DoubleClickDetector();

  console.log('%c[AIOPS] 并发压力与竞态检测器已加载 (Ctrl+Shift+C)', 'color:#9c27b0;font-weight:bold;');
})();
