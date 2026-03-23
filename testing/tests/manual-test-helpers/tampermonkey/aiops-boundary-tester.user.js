// ==UserScript==
// @name         AIOPS 边界测试数据注入器
// @namespace    http://localhost:8000/
// @version      1.0
// @description  按模块自动注入边界/异常测试数据，覆盖企业测试方案3.3章节全部边界维度
// @author       AIOPS Test Team
// @match        http://localhost:8000/*
// @match        http://localhost:*/*
// @grant        none
// @license      MIT
// ==/UserScript==

(function() {
  'use strict';

  // ==========================================
  // 边界测试数据集
  // ==========================================
  const BOUNDARY_DATA = {
    // === 空值/空白 ===
    empty: {
      label: '空值',
      values: ['', '   ', '\t', '\n', '\r\n', '\u200B'], // 空字符串、空格、Tab、换行、零宽空格
    },

    // === 长度边界 ===
    length: {
      label: '长度边界',
      values: {
        min1: 'a',
        char50: 'a'.repeat(50),
        char100: 'a'.repeat(100),
        char255: 'a'.repeat(255),
        char256: 'a'.repeat(256),
        char500: 'a'.repeat(500),
        char1000: 'a'.repeat(1000),
        char5000: '这是一段很长的中文文本。'.repeat(417),
      },
    },

    // === 特殊字符 ===
    specialChars: {
      label: '特殊字符',
      values: [
        '<script>alert("XSS")</script>',
        '"><img src=x onerror=alert(1)>',
        "' OR '1'='1",
        "'; DROP TABLE users; --",
        '<svg onload=alert(1)>',
        'javascript:alert(1)',
        '${7*7}',
        '{{7*7}}',
        '\\x00\\x01\\x02',
        '&lt;script&gt;',
        '%3Cscript%3E',
        '<iframe src="data:text/html,<script>alert(1)</script>">',
      ],
    },

    // === Emoji ===
    emoji: {
      label: 'Emoji字符',
      values: [
        '😀🚗⚡🔋☀️',
        '👨‍👩‍👧‍👦',  // 复合emoji
        '🏳️‍🌈',        // flag序列
        '测试😀数据',
        '⚠️ 警告设备 ⚡',
      ],
    },

    // === 数字边界 ===
    numeric: {
      label: '数字边界',
      values: {
        zero: 0,
        negative: -1,
        negativeDecimal: -0.01,
        minPositive: 0.01,
        maxSafe: Number.MAX_SAFE_INTEGER,
        minSafe: Number.MIN_SAFE_INTEGER,
        infinity: Infinity,
        nan: NaN,
        bigNumber: 999999999999.99,
        tooManyDecimals: 123.456789012345,
      },
    },

    // === 金融精度 ===
    financial: {
      label: '金融精度',
      values: {
        zero: '0.00',
        oneCent: '0.01',
        tooManyDecimals: '0.001',
        negative: '-1.00',
        largeAmount: '999999.99',
        overLimit: '1000000.00',
        maxAmount: '99999999.99',
      },
    },

    // === 日期边界 ===
    date: {
      label: '日期边界',
      values: {
        past: '1970-01-01',
        farPast: '1900-01-01',
        today: new Date().toISOString().split('T')[0],
        tomorrow: new Date(Date.now() + 86400000).toISOString().split('T')[0],
        farFuture: '2099-12-31',
        leapDay: '2024-02-29',
        invalidDate: '2024-02-30',
        yearEnd: '2024-12-31',
      },
    },

    // === 电话号码 ===
    phone: {
      label: '手机号边界',
      values: [
        '',
        '1',
        '1234567890',     // 10位
        '13800000000',    // 11位正常
        '138000000001',   // 12位
        '23800000000',    // 不以1开头
        'abcdefghijk',    // 字母
        '+8613800000000', // 带区号
      ],
    },

    // === 邮箱 ===
    email: {
      label: '邮箱边界',
      values: [
        '',
        'a@b.c',
        'test@example.com',                    // 正常
        'a'.repeat(64) + '@example.com',       // 用户名上限
        'test@' + 'a'.repeat(252) + '.com',    // 域名上限
        'test@.com',                            // 无域名
        '@example.com',                         // 无用户名
        'test@',                                // 无域名后缀
        'test example@mail.com',                // 含空格
        'test..test@example.com',               // 连续点
      ],
    },

    // === SQL注入 ===
    sqlInjection: {
      label: 'SQL注入',
      values: [
        "' OR '1'='1",
        "' OR 1=1 --",
        "' UNION SELECT NULL, NULL --",
        "'; DROP TABLE users; --",
        "1' AND '1'='1",
        "' OR pg_sleep(5) --",
        "admin'--",
        "1; SELECT * FROM pg_tables",
      ],
    },
  };

  // ==========================================
  // 模块专用边界配置
  // ==========================================
  const MODULE_BOUNDARIES = {
    user: {
      标签: '用户管理',
      字段: {
        用户名: { target: 'username|userName|loginName', boundary: ['empty', 'length', 'specialChars', 'emoji', 'sqlInjection'] },
        密码: { target: 'password', boundary: ['empty', 'length'] },
        邮箱: { target: 'email', boundary: ['email'] },
        手机: { target: 'phone|mobile', boundary: ['phone'] },
        姓名: { target: 'realName|name|displayName', boundary: ['empty', 'length', 'specialChars', 'emoji'] },
      },
    },
    device: {
      标签: '设备管理',
      字段: {
        设备名称: { target: 'deviceName|name', boundary: ['empty', 'length', 'specialChars', 'emoji'] },
        设备编号: { target: 'deviceCode|code|sn', boundary: ['empty', 'length', 'specialChars'] },
        经度: { target: 'longitude|lng', boundary: ['numeric'] },
        纬度: { target: 'latitude|lat', boundary: ['numeric'] },
        额定功率: { target: 'ratedPower|power', boundary: ['numeric', 'financial'] },
        IP地址: { target: 'ip|ipAddress', boundary: ['specialChars', 'sqlInjection'] },
      },
    },
    station: {
      标签: '站点管理',
      字段: {
        站点名称: { target: 'stationName|name', boundary: ['empty', 'length', 'specialChars', 'emoji'] },
        站点编号: { target: 'stationCode|code', boundary: ['empty', 'length', 'specialChars'] },
        地址: { target: 'address', boundary: ['empty', 'length', 'specialChars'] },
        充电桩数量: { target: 'pileCount|chargerCount', boundary: ['numeric'] },
        电价: { target: 'price|electricPrice', boundary: ['financial'] },
      },
    },
    workorder: {
      标签: '工单管理',
      字段: {
        工单标题: { target: 'title|subject', boundary: ['empty', 'length', 'specialChars', 'emoji'] },
        工单描述: { target: 'description|content', boundary: ['empty', 'length', 'specialChars', 'emoji'] },
        截止时间: { target: 'deadline|dueDate', boundary: ['date'] },
      },
    },
    charging: {
      标签: '充电订单',
      字段: {
        充电金额: { target: 'amount|totalAmount', boundary: ['financial'] },
        充电电量: { target: 'energy|kwh|power', boundary: ['numeric', 'financial'] },
        充电时长: { target: 'duration|minutes', boundary: ['numeric'] },
      },
    },
    settlement: {
      标签: '结算管理',
      字段: {
        结算金额: { target: 'amount|settlementAmount', boundary: ['financial'] },
        分润比例: { target: 'ratio|shareRatio|percentage', boundary: ['numeric'] },
      },
    },
    recharge: {
      标签: '充值管理',
      字段: {
        充值金额: { target: 'amount|rechargeAmount', boundary: ['financial'] },
      },
    },
    withdraw: {
      标签: '提现管理',
      字段: {
        提现金额: { target: 'amount|withdrawAmount', boundary: ['financial'] },
      },
    },
    invoice: {
      标签: '发票管理',
      字段: {
        抬头名称: { target: 'title|invoiceTitle', boundary: ['empty', 'length', 'specialChars'] },
        税号: { target: 'taxNumber|taxId', boundary: ['empty', 'length', 'specialChars'] },
        开票金额: { target: 'amount|invoiceAmount', boundary: ['financial'] },
      },
    },
  };

  // ==========================================
  // UI 面板
  // ==========================================
  let panel = null;
  let currentModule = 'user';
  let currentBoundary = 'empty';
  let testResults = [];

  function createPanel() {
    panel = document.createElement('div');
    panel.id = 'boundary-tester-panel';
    panel.innerHTML = `
      <style>
        #boundary-tester-panel {
          position: fixed; top: 10px; right: 10px; z-index: 99999;
          background: #1a1a2e; color: #eee; border-radius: 12px;
          box-shadow: 0 8px 32px rgba(0,0,0,0.4); font-family: 'Segoe UI', sans-serif;
          width: 380px; max-height: 90vh; overflow-y: auto;
        }
        #boundary-tester-panel .bt-header {
          background: linear-gradient(135deg, #e74c3c, #c0392b);
          padding: 12px 16px; border-radius: 12px 12px 0 0;
          display: flex; justify-content: space-between; align-items: center;
          cursor: move; user-select: none;
        }
        #boundary-tester-panel .bt-header h3 { margin: 0; font-size: 14px; }
        #boundary-tester-panel .bt-body { padding: 12px; }
        #boundary-tester-panel .bt-row { margin-bottom: 10px; }
        #boundary-tester-panel label { display: block; font-size: 12px; color: #aaa; margin-bottom: 4px; }
        #boundary-tester-panel select, #boundary-tester-panel button {
          width: 100%; padding: 8px; border: 1px solid #333; border-radius: 6px;
          background: #16213e; color: #eee; font-size: 13px;
        }
        #boundary-tester-panel button {
          cursor: pointer; font-weight: bold; border: none; margin-top: 4px;
        }
        #boundary-tester-panel button.bt-inject { background: #e74c3c; }
        #boundary-tester-panel button.bt-inject:hover { background: #c0392b; }
        #boundary-tester-panel button.bt-batch { background: #e67e22; }
        #boundary-tester-panel button.bt-batch:hover { background: #d35400; }
        #boundary-tester-panel button.bt-report { background: #27ae60; }
        #boundary-tester-panel button.bt-report:hover { background: #219a52; }
        #boundary-tester-panel .bt-preview {
          background: #0d1117; padding: 8px; border-radius: 6px;
          font-size: 11px; max-height: 120px; overflow-y: auto;
          white-space: pre-wrap; word-break: break-all; margin-top: 8px;
        }
        #boundary-tester-panel .bt-result {
          font-size: 11px; padding: 4px 8px; margin: 2px 0;
          border-radius: 4px;
        }
        #boundary-tester-panel .bt-result.pass { background: #1a4731; color: #4ade80; }
        #boundary-tester-panel .bt-result.fail { background: #4a1a1a; color: #f87171; }
        #boundary-tester-panel .bt-result.warn { background: #4a3a1a; color: #fbbf24; }
        #boundary-tester-panel .bt-stats {
          display: flex; gap: 8px; margin-top: 8px; font-size: 12px;
        }
        #boundary-tester-panel .bt-stats span {
          padding: 4px 8px; border-radius: 4px;
        }
        #boundary-tester-panel .bt-minimize { cursor: pointer; font-size: 18px; }
      </style>

      <div class="bt-header">
        <h3>🔬 边界测试注入器</h3>
        <span class="bt-minimize" id="bt-toggle">−</span>
      </div>

      <div class="bt-body" id="bt-body">
        <div class="bt-row">
          <label>目标模块</label>
          <select id="bt-module"></select>
        </div>
        <div class="bt-row">
          <label>边界类型</label>
          <select id="bt-boundary">
            <option value="empty">空值/空白</option>
            <option value="length">长度边界</option>
            <option value="specialChars">特殊字符/XSS</option>
            <option value="emoji">Emoji字符</option>
            <option value="numeric">数字边界</option>
            <option value="financial">金融精度</option>
            <option value="date">日期边界</option>
            <option value="phone">手机号边界</option>
            <option value="email">邮箱边界</option>
            <option value="sqlInjection">SQL注入探测</option>
          </select>
        </div>

        <div class="bt-preview" id="bt-preview">选择模块和类型后查看预览...</div>

        <div class="bt-row">
          <button class="bt-inject" id="bt-inject-btn">⚡ 注入当前类型数据</button>
        </div>
        <div class="bt-row">
          <button class="bt-batch" id="bt-batch-btn">🔄 批量遍历全部边界</button>
        </div>
        <div class="bt-row">
          <button class="bt-report" id="bt-report-btn">📊 生成测试报告</button>
        </div>

        <div id="bt-results"></div>
        <div class="bt-stats" id="bt-stats"></div>
      </div>
    `;

    document.body.appendChild(panel);
    initModuleSelect();
    bindEvents();
    makeDraggable();
  }

  function initModuleSelect() {
    const select = document.getElementById('bt-module');
    Object.entries(MODULE_BOUNDARIES).forEach(([key, mod]) => {
      const option = document.createElement('option');
      option.value = key;
      option.textContent = mod.标签;
      select.appendChild(option);
    });
  }

  function bindEvents() {
    document.getElementById('bt-module').addEventListener('change', updatePreview);
    document.getElementById('bt-boundary').addEventListener('change', updatePreview);
    document.getElementById('bt-inject-btn').addEventListener('click', injectBoundaryData);
    document.getElementById('bt-batch-btn').addEventListener('click', batchTest);
    document.getElementById('bt-report-btn').addEventListener('click', generateReport);
    document.getElementById('bt-toggle').addEventListener('click', () => {
      const body = document.getElementById('bt-body');
      body.style.display = body.style.display === 'none' ? 'block' : 'none';
    });
    updatePreview();
  }

  function updatePreview() {
    currentModule = document.getElementById('bt-module').value;
    currentBoundary = document.getElementById('bt-boundary').value;

    const data = BOUNDARY_DATA[currentBoundary];
    const preview = document.getElementById('bt-preview');

    if (!data) {
      preview.textContent = '无对应数据';
      return;
    }

    const values = Array.isArray(data.values) ? data.values : Object.entries(data.values).map(([k, v]) => `${k}: ${JSON.stringify(v)}`);
    preview.textContent = `📋 ${data.label}\n共 ${values.length} 个测试值：\n\n` + values.map((v, i) => `${i + 1}. ${JSON.stringify(v)}`).join('\n');
  }

  // ==========================================
  // 核心：注入边界数据到表单
  // ==========================================
  function injectBoundaryData() {
    const mod = MODULE_BOUNDARIES[currentModule];
    const data = BOUNDARY_DATA[currentBoundary];

    if (!mod || !data) {
      alert('请选择有效的模块和边界类型');
      return;
    }

    const values = Array.isArray(data.values) ? data.values : Object.values(data.values);
    const testValue = values[0]; // 使用第一个值进行注入

    let injected = 0;

    Object.entries(mod.字段).forEach(([fieldName, config]) => {
      if (!config.boundary.includes(currentBoundary)) return;

      const patterns = config.target.split('|');
      const inputs = document.querySelectorAll('input, textarea, select');

      inputs.forEach(input => {
        const name = (input.name || input.id || input.getAttribute('data-field') || '').toLowerCase();
        const placeholder = (input.placeholder || '').toLowerCase();
        const label = findLabelText(input);

        const match = patterns.some(p => {
          const pl = p.toLowerCase();
          return name.includes(pl) || placeholder.includes(pl) || label.includes(pl);
        });

        if (match) {
          setInputValue(input, typeof testValue === 'object' ? JSON.stringify(testValue) : String(testValue));
          highlightInput(input, '#e74c3c');
          injected++;
        }
      });
    });

    const resultDiv = document.getElementById('bt-results');
    const result = {
      module: mod.标签,
      boundary: data.label,
      injected,
      timestamp: new Date().toLocaleTimeString(),
    };
    testResults.push(result);

    resultDiv.innerHTML = `<div class="bt-result ${injected > 0 ? 'pass' : 'warn'}">
      ${result.timestamp} | ${mod.标签} | ${data.label} | 注入 ${injected} 个字段
    </div>` + resultDiv.innerHTML;

    updateStats();
  }

  // ==========================================
  // 批量遍历
  // ==========================================
  async function batchTest() {
    const mod = MODULE_BOUNDARIES[currentModule];
    if (!mod) return;

    const boundaryTypes = Object.keys(BOUNDARY_DATA);
    const resultsDiv = document.getElementById('bt-results');
    resultsDiv.innerHTML = '<div style="color:#fbbf24;font-size:12px;">🔄 批量测试进行中...</div>';
    testResults = [];

    for (const bType of boundaryTypes) {
      const data = BOUNDARY_DATA[bType];
      const values = Array.isArray(data.values) ? data.values : Object.values(data.values);

      for (let i = 0; i < Math.min(values.length, 3); i++) { // 每种类型测试前3个值
        const testValue = values[i];

        let injected = 0;
        Object.entries(mod.字段).forEach(([fieldName, config]) => {
          if (!config.boundary.includes(bType)) return;

          const patterns = config.target.split('|');
          const inputs = document.querySelectorAll('input, textarea');

          inputs.forEach(input => {
            const name = (input.name || input.id || '').toLowerCase();
            const match = patterns.some(p => name.includes(p.toLowerCase()));
            if (match) {
              setInputValue(input, String(testValue));
              injected++;
            }
          });
        });

        testResults.push({
          module: mod.标签,
          boundary: data.label,
          value: String(testValue).substring(0, 50),
          injected,
          timestamp: new Date().toLocaleTimeString(),
        });

        await sleep(500); // 间隔 500ms
      }
    }

    resultsDiv.innerHTML = testResults.map(r =>
      `<div class="bt-result ${r.injected > 0 ? 'pass' : 'warn'}">
        ${r.timestamp} | ${r.boundary} | 值=${r.value.substring(0, 20)}... | 注入${r.injected}个
      </div>`
    ).join('');

    updateStats();
  }

  // ==========================================
  // 报告
  // ==========================================
  function generateReport() {
    const report = {
      title: 'AIOPS 边界测试报告',
      module: MODULE_BOUNDARIES[currentModule]?.标签 || currentModule,
      timestamp: new Date().toISOString(),
      totalTests: testResults.length,
      successInjections: testResults.filter(r => r.injected > 0).length,
      results: testResults,
      boundaryTypes: Object.keys(BOUNDARY_DATA).map(k => ({
        type: k,
        label: BOUNDARY_DATA[k].label,
        valueCount: Array.isArray(BOUNDARY_DATA[k].values)
          ? BOUNDARY_DATA[k].values.length
          : Object.keys(BOUNDARY_DATA[k].values).length,
      })),
    };

    const blob = new Blob([JSON.stringify(report, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `boundary-test-${currentModule}-${Date.now()}.json`;
    a.click();
    URL.revokeObjectURL(url);
  }

  // ==========================================
  // 工具函数
  // ==========================================
  function setInputValue(input, value) {
    const nativeInputValueSetter = Object.getOwnPropertyDescriptor(
      window.HTMLInputElement.prototype, 'value'
    )?.set || Object.getOwnPropertyDescriptor(
      window.HTMLTextAreaElement.prototype, 'value'
    )?.set;

    if (nativeInputValueSetter) {
      nativeInputValueSetter.call(input, value);
    } else {
      input.value = value;
    }
    input.dispatchEvent(new Event('input', { bubbles: true }));
    input.dispatchEvent(new Event('change', { bubbles: true }));
  }

  function findLabelText(input) {
    if (input.id) {
      const label = document.querySelector(`label[for="${input.id}"]`);
      if (label) return label.textContent.toLowerCase();
    }
    const parent = input.closest('.ant-form-item, .el-form-item, .form-group');
    if (parent) {
      const label = parent.querySelector('label, .ant-form-item-label, .el-form-item__label');
      if (label) return label.textContent.toLowerCase();
    }
    return '';
  }

  function highlightInput(input, color) {
    const origBorder = input.style.border;
    input.style.border = `2px solid ${color}`;
    input.style.boxShadow = `0 0 8px ${color}40`;
    setTimeout(() => {
      input.style.border = origBorder;
      input.style.boxShadow = '';
    }, 3000);
  }

  function updateStats() {
    const stats = document.getElementById('bt-stats');
    const total = testResults.length;
    const active = testResults.filter(r => r.injected > 0).length;
    stats.innerHTML = `
      <span style="background:#1a3a4a;color:#60a5fa;">总计: ${total}</span>
      <span style="background:#1a4731;color:#4ade80;">成功: ${active}</span>
      <span style="background:#4a3a1a;color:#fbbf24;">未匹配: ${total - active}</span>
    `;
  }

  function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
  }

  function makeDraggable() {
    const header = panel.querySelector('.bt-header');
    let isDragging = false;
    let startX, startY, startLeft, startTop;

    header.addEventListener('mousedown', (e) => {
      if (e.target.classList.contains('bt-minimize')) return;
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
      panel.style.right = 'auto';
    });

    document.addEventListener('mouseup', () => { isDragging = false; });
  }

  // ==========================================
  // 快捷键
  // ==========================================
  document.addEventListener('keydown', (e) => {
    if (e.ctrlKey && e.shiftKey && e.key === 'B') {
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

  console.log('🔬 AIOPS 边界测试注入器已加载 (Ctrl+Shift+B 切换显示)');
})();
