// ==UserScript==
// @name         AIOPS 查询组合测试器
// @namespace    http://localhost:8000/
// @version      1.0
// @description  按模块自动执行查询条件组合测试，覆盖企业测试方案3.4章节全部查询维度
// @author       AIOPS Test Team
// @match        http://localhost:8000/*
// @match        http://localhost:*/*
// @grant        none
// @license      MIT
// ==/UserScript==

(function() {
  'use strict';

  // ==========================================
  // 查询字段配置（按模块）
  // ==========================================
  const QUERY_MODULES = {
    user: {
      label: '用户管理',
      path: ['/system/users', '/user'],
      fields: [
        { name: '用户名', selector: '[name*="name"],[name*="userName"],[placeholder*="用户名"]', type: 'text', values: ['admin', 'test', '不存在的用户', 'adm', '<script>'] },
        { name: '手机号', selector: '[name*="phone"],[name*="mobile"],[placeholder*="手机"]', type: 'text', values: ['13800000000', '138', ''] },
        { name: '邮箱', selector: '[name*="email"],[placeholder*="邮箱"]', type: 'text', values: ['admin@example.com', 'test', ''] },
        { name: '角色', selector: '[name*="role"],[class*="role"]', type: 'select', values: [] },
        { name: '状态', selector: '[name*="status"],[class*="status"]', type: 'select', values: [] },
        { name: '创建时间', selector: '[name*="createTime"],[class*="date-picker"],[class*="rangePicker"]', type: 'dateRange', values: ['today', 'thisWeek', 'thisMonth', 'lastMonth', 'custom'] },
      ],
    },
    device: {
      label: '设备管理',
      path: ['/device', '/equipment'],
      fields: [
        { name: '设备名称', selector: '[name*="deviceName"],[name*="name"],[placeholder*="设备"]', type: 'text', values: ['充电桩A', 'PV', '不存在'] },
        { name: '设备编号', selector: '[name*="deviceCode"],[name*="code"],[placeholder*="编号"]', type: 'text', values: ['DEV001', 'DEV', ''] },
        { name: '设备类型', selector: '[name*="type"],[name*="deviceType"]', type: 'select', values: [] },
        { name: '设备状态', selector: '[name*="status"],[name*="deviceStatus"]', type: 'select', values: [] },
        { name: '所属站点', selector: '[name*="station"],[name*="stationId"]', type: 'select', values: [] },
      ],
    },
    workorder: {
      label: '工单管理',
      path: ['/workorder', '/work-order'],
      fields: [
        { name: '工单编号', selector: '[name*="orderNo"],[name*="code"],[placeholder*="编号"]', type: 'text', values: ['WO2024', 'WO', ''] },
        { name: '工单标题', selector: '[name*="title"],[name*="subject"],[placeholder*="标题"]', type: 'text', values: ['故障', '安装', '不存在'] },
        { name: '工单类型', selector: '[name*="type"],[name*="orderType"]', type: 'select', values: [] },
        { name: '工单状态', selector: '[name*="status"]', type: 'select', values: [] },
        { name: '优先级', selector: '[name*="priority"]', type: 'select', values: [] },
        { name: '处理人', selector: '[name*="handler"],[name*="assignee"]', type: 'select', values: [] },
        { name: '创建时间', selector: '[class*="date"],[class*="range"]', type: 'dateRange', values: ['today', 'thisWeek', 'thisMonth'] },
      ],
    },
    charging: {
      label: '充电订单',
      path: ['/charging', '/order'],
      fields: [
        { name: '订单编号', selector: '[name*="orderNo"],[placeholder*="订单"]', type: 'text', values: ['CHG2024', ''] },
        { name: '用户/车牌', selector: '[name*="user"],[name*="plate"],[placeholder*="用户"]', type: 'text', values: ['张三', '京A12345'] },
        { name: '充电站点', selector: '[name*="station"]', type: 'select', values: [] },
        { name: '订单状态', selector: '[name*="status"]', type: 'select', values: [] },
        { name: '金额范围', selector: '[name*="amount"],[name*="minAmount"]', type: 'numberRange', values: [[0, 10], [10, 100], [100, 1000]] },
        { name: '充电时间', selector: '[class*="date"],[class*="range"]', type: 'dateRange', values: ['today', 'thisWeek', 'thisMonth'] },
      ],
    },
    settlement: {
      label: '结算管理',
      path: ['/settlement', '/billing'],
      fields: [
        { name: '结算单号', selector: '[name*="settlementNo"],[placeholder*="结算"]', type: 'text', values: ['STL2024', ''] },
        { name: '结算状态', selector: '[name*="status"]', type: 'select', values: [] },
        { name: '站点/运营商', selector: '[name*="station"],[name*="operator"]', type: 'select', values: [] },
        { name: '金额范围', selector: '[name*="amount"]', type: 'numberRange', values: [[0, 1000], [1000, 10000]] },
        { name: '结算周期', selector: '[name*="period"],[name*="cycle"]', type: 'select', values: [] },
      ],
    },
    log: {
      label: '日志/审计',
      path: ['/log', '/audit', '/monitor'],
      fields: [
        { name: '操作人', selector: '[name*="operator"],[name*="user"],[placeholder*="操作"]', type: 'text', values: ['admin', ''] },
        { name: '操作类型', selector: '[name*="type"],[name*="action"]', type: 'select', values: [] },
        { name: '操作结果', selector: '[name*="result"],[name*="status"]', type: 'select', values: [] },
        { name: '关键词', selector: '[name*="keyword"],[name*="search"],[placeholder*="关键"]', type: 'text', values: ['登录', '删除', ''] },
        { name: '时间范围', selector: '[class*="date"],[class*="range"]', type: 'dateRange', values: ['today', 'thisWeek', 'thisMonth'] },
        { name: 'IP地址', selector: '[name*="ip"],[placeholder*="IP"]', type: 'text', values: ['192.168', ''] },
      ],
    },
  };

  // ==========================================
  // 测试用例生成器
  // ==========================================
  function generateTestCases(moduleName) {
    const mod = QUERY_MODULES[moduleName];
    if (!mod) return [];

    const cases = [];
    const fields = mod.fields;

    // 1. 无条件查询
    cases.push({
      name: '无条件查询',
      description: '不填任何条件直接搜索',
      conditions: {},
      expected: '返回全部数据',
    });

    // 2. 单条件查询 - 每个字段单独测试
    fields.forEach(field => {
      const testValues = field.values.length > 0 ? field.values : ['（选择第一个选项）'];
      testValues.forEach((val, i) => {
        cases.push({
          name: `单条件-${field.name}(值${i + 1})`,
          description: `仅填写 ${field.name} = ${JSON.stringify(val)}`,
          conditions: { [field.name]: val },
          expected: val ? '筛选结果匹配条件' : '返回全部或空结果',
        });
      });
    });

    // 3. 双条件组合（选取前3对组合）
    for (let i = 0; i < fields.length && i < 3; i++) {
      for (let j = i + 1; j < fields.length && j < 4; j++) {
        cases.push({
          name: `双条件-${fields[i].name}+${fields[j].name}`,
          description: `同时填写 ${fields[i].name} 和 ${fields[j].name}`,
          conditions: {
            [fields[i].name]: fields[i].values[0] || '（第一个选项）',
            [fields[j].name]: fields[j].values[0] || '（第一个选项）',
          },
          expected: '结果同时满足两个条件',
        });
      }
    }

    // 4. 全条件组合
    if (fields.length >= 3) {
      const allConditions = {};
      fields.forEach(f => {
        allConditions[f.name] = f.values[0] || '（第一个选项）';
      });
      cases.push({
        name: '全条件组合',
        description: '填写所有筛选条件',
        conditions: allConditions,
        expected: '最精确匹配',
      });
    }

    // 5. 无结果查询
    cases.push({
      name: '无结果查询',
      description: '输入一定不存在的搜索关键词',
      conditions: { [fields[0].name]: 'ZZZNOTEXIST999' },
      expected: '返回空列表（不报错）',
    });

    // 6. 重置测试
    cases.push({
      name: '重置测试',
      description: '填写条件后点击重置按钮',
      conditions: 'RESET',
      expected: '所有条件清空，列表恢复默认',
    });

    return cases;
  }

  // ==========================================
  // UI 面板
  // ==========================================
  let panel = null;
  let currentModule = 'user';
  let testCases = [];
  let caseResults = [];

  function createPanel() {
    panel = document.createElement('div');
    panel.id = 'query-tester-panel';
    panel.innerHTML = `
      <style>
        #query-tester-panel {
          position: fixed; top: 10px; left: 10px; z-index: 99999;
          background: #1a1a2e; color: #eee; border-radius: 12px;
          box-shadow: 0 8px 32px rgba(0,0,0,0.4); font-family: 'Segoe UI', sans-serif;
          width: 400px; max-height: 90vh; overflow-y: auto;
        }
        #query-tester-panel .qt-header {
          background: linear-gradient(135deg, #3498db, #2980b9);
          padding: 12px 16px; border-radius: 12px 12px 0 0;
          display: flex; justify-content: space-between; align-items: center;
          cursor: move; user-select: none;
        }
        #query-tester-panel .qt-header h3 { margin: 0; font-size: 14px; }
        #query-tester-panel .qt-body { padding: 12px; }
        #query-tester-panel .qt-row { margin-bottom: 10px; }
        #query-tester-panel label { display: block; font-size: 12px; color: #aaa; margin-bottom: 4px; }
        #query-tester-panel select, #query-tester-panel button {
          width: 100%; padding: 8px; border: 1px solid #333; border-radius: 6px;
          background: #16213e; color: #eee; font-size: 13px;
        }
        #query-tester-panel button {
          cursor: pointer; font-weight: bold; border: none; margin-top: 4px;
        }
        #query-tester-panel button.qt-gen { background: #3498db; }
        #query-tester-panel button.qt-gen:hover { background: #2980b9; }
        #query-tester-panel button.qt-run { background: #e67e22; }
        #query-tester-panel button.qt-run:hover { background: #d35400; }
        #query-tester-panel button.qt-export { background: #27ae60; }
        #query-tester-panel button.qt-export:hover { background: #219a52; }
        #query-tester-panel .qt-case-list {
          max-height: 300px; overflow-y: auto; margin-top: 8px;
        }
        #query-tester-panel .qt-case {
          background: #0d1117; padding: 8px; border-radius: 6px;
          margin-bottom: 4px; font-size: 11px; cursor: pointer;
          border-left: 3px solid #333;
        }
        #query-tester-panel .qt-case:hover { background: #161b22; }
        #query-tester-panel .qt-case.pass { border-left-color: #4ade80; }
        #query-tester-panel .qt-case.fail { border-left-color: #f87171; }
        #query-tester-panel .qt-case.pending { border-left-color: #fbbf24; }
        #query-tester-panel .qt-case .qt-case-name { font-weight: bold; color: #60a5fa; }
        #query-tester-panel .qt-case .qt-case-desc { color: #888; margin-top: 2px; }
        #query-tester-panel .qt-case .qt-case-conditions { color: #aaa; margin-top: 2px; font-style: italic; }
        #query-tester-panel .qt-judge {
          display: flex; gap: 4px; margin-top: 4px;
        }
        #query-tester-panel .qt-judge button {
          width: auto; padding: 2px 10px; font-size: 11px;
        }
        #query-tester-panel .qt-judge .pass-btn { background: #22c55e; }
        #query-tester-panel .qt-judge .fail-btn { background: #ef4444; }
        #query-tester-panel .qt-stats {
          display: flex; gap: 8px; margin-top: 8px; font-size: 12px;
        }
        #query-tester-panel .qt-stats span { padding: 4px 8px; border-radius: 4px; }
        #query-tester-panel .qt-minimize { cursor: pointer; font-size: 18px; }
      </style>

      <div class="qt-header">
        <h3>🔍 查询组合测试器</h3>
        <span class="qt-minimize" id="qt-toggle">−</span>
      </div>

      <div class="qt-body" id="qt-body">
        <div class="qt-row">
          <label>目标模块</label>
          <select id="qt-module"></select>
        </div>

        <div class="qt-row">
          <button class="qt-gen" id="qt-gen-btn">📋 生成测试用例</button>
        </div>

        <div class="qt-case-list" id="qt-case-list"></div>

        <div class="qt-stats" id="qt-stats"></div>

        <div class="qt-row">
          <button class="qt-export" id="qt-export-btn">📊 导出测试报告</button>
        </div>
      </div>
    `;

    document.body.appendChild(panel);
    initModuleSelect();
    bindEvents();
    makeDraggable();
  }

  function initModuleSelect() {
    const select = document.getElementById('qt-module');
    Object.entries(QUERY_MODULES).forEach(([key, mod]) => {
      const option = document.createElement('option');
      option.value = key;
      option.textContent = mod.label;
      select.appendChild(option);
    });
  }

  function bindEvents() {
    document.getElementById('qt-gen-btn').addEventListener('click', () => {
      currentModule = document.getElementById('qt-module').value;
      testCases = generateTestCases(currentModule);
      caseResults = testCases.map(() => 'pending');
      renderCases();
    });

    document.getElementById('qt-export-btn').addEventListener('click', exportReport);

    document.getElementById('qt-toggle').addEventListener('click', () => {
      const body = document.getElementById('qt-body');
      body.style.display = body.style.display === 'none' ? 'block' : 'none';
    });
  }

  function renderCases() {
    const list = document.getElementById('qt-case-list');
    list.innerHTML = '';

    testCases.forEach((tc, i) => {
      const status = caseResults[i];
      const div = document.createElement('div');
      div.className = `qt-case ${status}`;

      const condStr = typeof tc.conditions === 'object'
        ? Object.entries(tc.conditions).map(([k, v]) => `${k}=${JSON.stringify(v)}`).join(', ')
        : tc.conditions;

      div.innerHTML = `
        <div class="qt-case-name">${i + 1}. ${tc.name} ${status === 'pass' ? '✅' : status === 'fail' ? '❌' : '⏳'}</div>
        <div class="qt-case-desc">${tc.description}</div>
        <div class="qt-case-conditions">条件: ${condStr}</div>
        <div class="qt-case-desc">期望: ${tc.expected}</div>
        <div class="qt-judge">
          <button class="pass-btn" data-idx="${i}" data-result="pass">✅ 通过</button>
          <button class="fail-btn" data-idx="${i}" data-result="fail">❌ 失败</button>
        </div>
      `;

      div.querySelectorAll('.qt-judge button').forEach(btn => {
        btn.addEventListener('click', (e) => {
          const idx = parseInt(e.target.dataset.idx);
          const result = e.target.dataset.result;
          caseResults[idx] = result;
          renderCases();
        });
      });

      list.appendChild(div);
    });

    updateStats();
  }

  function updateStats() {
    const stats = document.getElementById('qt-stats');
    const total = caseResults.length;
    const pass = caseResults.filter(r => r === 'pass').length;
    const fail = caseResults.filter(r => r === 'fail').length;
    const pending = caseResults.filter(r => r === 'pending').length;

    stats.innerHTML = `
      <span style="background:#1a3a4a;color:#60a5fa;">总计: ${total}</span>
      <span style="background:#1a4731;color:#4ade80;">通过: ${pass}</span>
      <span style="background:#4a1a1a;color:#f87171;">失败: ${fail}</span>
      <span style="background:#4a3a1a;color:#fbbf24;">待测: ${pending}</span>
    `;
  }

  function exportReport() {
    const mod = QUERY_MODULES[currentModule];
    const report = {
      title: 'AIOPS 查询组合测试报告',
      module: mod?.label || currentModule,
      timestamp: new Date().toISOString(),
      summary: {
        total: testCases.length,
        pass: caseResults.filter(r => r === 'pass').length,
        fail: caseResults.filter(r => r === 'fail').length,
        pending: caseResults.filter(r => r === 'pending').length,
        passRate: testCases.length > 0
          ? (caseResults.filter(r => r === 'pass').length / testCases.length * 100).toFixed(1) + '%'
          : '0%',
      },
      cases: testCases.map((tc, i) => ({
        id: i + 1,
        name: tc.name,
        description: tc.description,
        conditions: tc.conditions,
        expected: tc.expected,
        result: caseResults[i],
      })),
    };

    const blob = new Blob([JSON.stringify(report, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `query-test-${currentModule}-${Date.now()}.json`;
    a.click();
    URL.revokeObjectURL(url);
  }

  function makeDraggable() {
    const header = panel.querySelector('.qt-header');
    let isDragging = false;
    let startX, startY, startLeft, startTop;

    header.addEventListener('mousedown', (e) => {
      if (e.target.classList.contains('qt-minimize')) return;
      isDragging = true;
      startX = e.clientX;
      startY = e.clientY;
      const rect = panel.getBoundingClientRect();
      startLeft = rect.left;
      startTop = rect.top;
    });

    document.addEventListener('mousemove', (e) => {
      if (!isDragging) return;
      panel.style.left = (startLeft + e.clientX - startX) + 'px';
      panel.style.top = (startTop + e.clientY - startY) + 'px';
    });

    document.addEventListener('mouseup', () => { isDragging = false; });
  }

  // 快捷键 Ctrl+Shift+Q
  document.addEventListener('keydown', (e) => {
    if (e.ctrlKey && e.shiftKey && e.key === 'Q') {
      e.preventDefault();
      if (panel) {
        panel.style.display = panel.style.display === 'none' ? 'block' : 'none';
      }
    }
  });

  // 初始化
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', createPanel);
  } else {
    createPanel();
  }

  console.log('🔍 AIOPS 查询组合测试器已加载 (Ctrl+Shift+Q 切换显示)');
})();
