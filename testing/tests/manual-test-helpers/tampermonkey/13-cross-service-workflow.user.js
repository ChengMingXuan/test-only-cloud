// ==UserScript==
// @name         AIOPS 跨服务业务流编排器 (Cross-Service Workflow)
// @namespace    http://localhost:8000/testing
// @version      1.0.0
// @description  跨服务业务流编排、链路追踪、断点续测、流程回放
// @author       AIOPS Test Team
// @match        http://localhost:8000/*
// @match        http://localhost:*/*
// @match        http://localhost:*/*
// @grant        GM_setValue
// @grant        GM_getValue
// @grant        GM_deleteValue
// @grant        GM_notification
// @grant        GM_registerMenuCommand
// ==/UserScript==

(function () {
  'use strict';

  // ============================
  // 配置
  // ============================
  const CONFIG = {
    API_BASE: window.location.origin,
    STORAGE_KEY: 'aiops_workflow_state',
    MAX_STEPS: 200,
    TIMEOUT_MS: 30000,
    RETRY_COUNT: 3,
    RETRY_DELAY_MS: 2000,
  };

  // ============================
  // 预定义业务流模板
  // ============================
  const WORKFLOW_TEMPLATES = {
    // ---- 流程A: 充电全生命周期 ----
    'charging-lifecycle': {
      name: '充电全生命周期',
      description: '用户注册→充值→扫码充电→支付→结算→提现',
      steps: [
        { service: 'Identity', action: 'POST /api/identity/register', desc: '用户注册', params: { email: 'test_wf@example.com', password: 'Test@12345' } },
        { service: 'Account', action: 'POST /api/account/recharge', desc: '充值到钱包', params: { amount: 100.00 } },
        { service: 'Station', action: 'GET /api/station/list', desc: '查询可用站点', params: {} },
        { service: 'Device', action: 'GET /api/device/available', desc: '查询空闲充电桩', params: {} },
        { service: 'Charging', action: 'POST /api/charging/order/start', desc: '开始充电', params: {} },
        { service: 'Charging', action: 'POST /api/charging/order/stop', desc: '结束充电', params: {} },
        { service: 'Account', action: 'POST /api/account/payment', desc: '支付订单', params: {} },
        { service: 'Settlement', action: 'POST /api/settlement/generate', desc: '生成结算单', params: {} },
        { service: 'Settlement', action: 'POST /api/settlement/confirm', desc: '确认结算', params: {} },
        { service: 'Settlement', action: 'POST /api/settlement/withdraw', desc: '提现', params: {} },
      ],
    },

    // ---- 流程B: 运维闭环 ----
    'ops-loop': {
      name: '运维闭环',
      description: '设备告警→工单创建→派工→维修→备件→验收→评价',
      steps: [
        { service: 'Device', action: 'POST /api/device/alert/trigger', desc: '模拟设备告警', params: { deviceId: '', alertType: 'temperature_high' } },
        { service: 'RuleEngine', action: 'POST /api/rule/execute', desc: '规则引擎匹配', params: {} },
        { service: 'WorkOrder', action: 'POST /api/workorder/create', desc: '创建工单', params: { type: 'fault' } },
        { service: 'WorkOrder', action: 'POST /api/workorder/auto-dispatch', desc: '智能派工', params: {} },
        { service: 'WorkOrder', action: 'POST /api/workorder/accept', desc: '技师接单', params: {} },
        { service: 'WorkOrder', action: 'POST /api/workorder/spare-part/apply', desc: '领用备件', params: {} },
        { service: 'WorkOrder', action: 'POST /api/workorder/complete', desc: '维修完成', params: {} },
        { service: 'WorkOrder', action: 'POST /api/workorder/verify', desc: '验收', params: {} },
        { service: 'WorkOrder', action: 'POST /api/workorder/satisfaction', desc: '满意度评价', params: { score: 5 } },
        { service: 'Device', action: 'GET /api/device/alert/check', desc: '确认告警已消除', params: {} },
      ],
    },

    // ---- 流程C: IoT 事件链 ----
    'iot-event-chain': {
      name: 'IoT 事件链',
      description: '规则配置→数据注入→规则触发→通知→审计',
      steps: [
        { service: 'RuleEngine', action: 'POST /api/rule-chain/create', desc: '创建规则链', params: {} },
        { service: 'RuleEngine', action: 'POST /api/rule-chain/enable', desc: '启用规则', params: {} },
        { service: 'Ingestion', action: 'POST /api/ingestion/telemetry', desc: '注入遥测数据', params: { temperature: 65, duration: 360 } },
        { service: 'Device', action: 'GET /api/device/alert/list', desc: '检查告警生成', params: {} },
        { service: 'Observability', action: 'GET /api/observability/operation-log', desc: '查看审计日志', params: {} },
      ],
    },

    // ---- 流程D: 多租户隔离 ----
    'tenant-isolation': {
      name: '多租户隔离验证',
      description: '租户A操作→租户B操作→交叉验证隔离',
      steps: [
        { service: 'Identity', action: 'POST /api/identity/login', desc: '租户A管理员登录', params: { tenant: 'A' } },
        { service: 'Station', action: 'POST /api/station/create', desc: '租户A创建站点', params: { name: 'StationA' } },
        { service: 'Device', action: 'POST /api/device/create', desc: '租户A注册设备', params: { name: 'DeviceA' } },
        { service: 'Identity', action: 'POST /api/identity/login', desc: '租户B管理员登录', params: { tenant: 'B' } },
        { service: 'Station', action: 'GET /api/station/list', desc: '租户B查站点(不应看到A)', params: {} },
        { service: 'Device', action: 'GET /api/device/list', desc: '租户B查设备(不应看到A)', params: {} },
      ],
    },

    // ---- 流程E: 能源全链路 ----
    'energy-chain': {
      name: '能源调度全链路',
      description: '微网配置→调度策略→光伏储能→VPP→碳交易→结算',
      steps: [
        { service: 'MicroGrid', action: 'POST /api/microgrid/topology', desc: '配置微网拓扑', params: {} },
        { service: 'Orchestrator', action: 'POST /api/orchestrator/strategy', desc: '设置调度策略', params: {} },
        { service: 'PVESSC', action: 'GET /api/pvessc/realtime', desc: '光伏实时数据', params: {} },
        { service: 'PVESSC', action: 'POST /api/pvessc/charge-discharge', desc: '储能充放电', params: {} },
        { service: 'VPP', action: 'POST /api/vpp/demand-response', desc: '需求响应', params: {} },
        { service: 'CarbonTrade', action: 'POST /api/carbon/calculate', desc: '碳减排计算', params: {} },
        { service: 'Settlement', action: 'POST /api/settlement/energy', desc: '能源结算', params: {} },
      ],
    },

    // ---- 流程F: 区块链信任 ----
    'blockchain-trust': {
      name: '区块链信任链',
      description: '充电存证→结算存证→审计追溯→防篡改验证',
      steps: [
        { service: 'Charging', action: 'GET /api/charging/order/latest', desc: '获取最新订单', params: {} },
        { service: 'Blockchain', action: 'POST /api/blockchain/evidence/submit', desc: '充电凭证上链', params: {} },
        { service: 'Blockchain', action: 'GET /api/blockchain/evidence/verify', desc: '链上验证', params: {} },
        { service: 'Settlement', action: 'GET /api/settlement/latest', desc: '获取最新结算单', params: {} },
        { service: 'Blockchain', action: 'POST /api/blockchain/evidence/submit', desc: '结算凭证上链', params: {} },
        { service: 'Blockchain', action: 'GET /api/blockchain/audit/report', desc: '生成审计报告', params: {} },
      ],
    },
  };

  // ============================
  // 工作流引擎
  // ============================
  class WorkflowEngine {
    constructor() {
      this.state = this.loadState();
      this.listeners = [];
    }

    loadState() {
      try {
        const saved = GM_getValue(CONFIG.STORAGE_KEY, null);
        return saved ? JSON.parse(saved) : { currentWorkflow: null, currentStep: 0, results: [], status: 'idle' };
      } catch {
        return { currentWorkflow: null, currentStep: 0, results: [], status: 'idle' };
      }
    }

    saveState() {
      GM_setValue(CONFIG.STORAGE_KEY, JSON.stringify(this.state));
      this.notify();
    }

    notify() {
      this.listeners.forEach(fn => fn(this.state));
    }

    onStateChange(fn) {
      this.listeners.push(fn);
    }

    startWorkflow(templateKey) {
      const template = WORKFLOW_TEMPLATES[templateKey];
      if (!template) return;
      this.state = {
        currentWorkflow: templateKey,
        workflowName: template.name,
        steps: template.steps,
        currentStep: 0,
        results: [],
        status: 'running',
        startTime: new Date().toISOString(),
      };
      this.saveState();
      GM_notification({ title: 'AIOPS 工作流', text: `开始执行: ${template.name}`, timeout: 3000 });
    }

    async executeCurrentStep() {
      if (this.state.status !== 'running') return;
      const step = this.state.steps[this.state.currentStep];
      if (!step) {
        this.state.status = 'completed';
        this.saveState();
        return;
      }

      const result = { step: this.state.currentStep, desc: step.desc, service: step.service, status: 'pending', startTime: new Date().toISOString() };

      try {
        // 显示当前步骤信息
        this.showStepDialog(step);
        result.status = 'waiting_user';
        this.state.results.push(result);
        this.saveState();
      } catch (error) {
        result.status = 'error';
        result.error = error.message;
        this.state.results.push(result);
        this.saveState();
      }
    }

    confirmStep(passed, notes) {
      const result = this.state.results[this.state.results.length - 1];
      if (result) {
        result.status = passed ? 'passed' : 'failed';
        result.notes = notes || '';
        result.endTime = new Date().toISOString();
      }
      this.state.currentStep++;
      if (this.state.currentStep >= this.state.steps.length) {
        this.state.status = 'completed';
        GM_notification({ title: 'AIOPS 工作流', text: `✅ ${this.state.workflowName} 执行完成！`, timeout: 5000 });
      }
      this.saveState();
    }

    skipStep() {
      const result = this.state.results[this.state.results.length - 1];
      if (result) {
        result.status = 'skipped';
        result.endTime = new Date().toISOString();
      }
      this.state.currentStep++;
      this.saveState();
    }

    pauseWorkflow() {
      this.state.status = 'paused';
      this.saveState();
    }

    resumeWorkflow() {
      this.state.status = 'running';
      this.saveState();
    }

    resetWorkflow() {
      this.state = { currentWorkflow: null, currentStep: 0, results: [], status: 'idle' };
      this.saveState();
    }

    getReport() {
      const passed = this.state.results.filter(r => r.status === 'passed').length;
      const failed = this.state.results.filter(r => r.status === 'failed').length;
      const skipped = this.state.results.filter(r => r.status === 'skipped').length;
      const total = this.state.steps ? this.state.steps.length : 0;
      return { total, passed, failed, skipped, pending: total - passed - failed - skipped, results: this.state.results };
    }

    showStepDialog(step) {
      // 在 UI 面板中高亮当前步骤
    }
  }

  // ============================
  // UI 面板
  // ============================
  class WorkflowPanel {
    constructor(engine) {
      this.engine = engine;
      this.visible = false;
      this.panel = null;
      this.init();
    }

    init() {
      this.createPanel();
      this.engine.onStateChange(() => this.render());

      // 快捷键 Ctrl+Shift+W
      document.addEventListener('keydown', (e) => {
        if (e.ctrlKey && e.shiftKey && e.key === 'W') {
          e.preventDefault();
          this.toggle();
        }
      });

      GM_registerMenuCommand('🔄 跨服务业务流编排器', () => this.toggle());
    }

    createPanel() {
      this.panel = document.createElement('div');
      this.panel.id = 'aiops-workflow-panel';
      this.panel.style.cssText = `
        position: fixed; top: 60px; right: 20px; width: 420px; max-height: 80vh;
        background: #1a1a2e; color: #eee; border-radius: 12px; padding: 0;
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

    render() {
      const state = this.engine.state;
      const report = this.engine.getReport();

      let stepListHtml = '';
      if (state.steps) {
        stepListHtml = state.steps.map((step, i) => {
          const result = state.results.find(r => r.step === i);
          let icon = '⬜';
          let color = '#666';
          if (result) {
            if (result.status === 'passed') { icon = '✅'; color = '#4caf50'; }
            else if (result.status === 'failed') { icon = '❌'; color = '#f44336'; }
            else if (result.status === 'skipped') { icon = '⏭️'; color = '#ff9800'; }
            else if (result.status === 'waiting_user') { icon = '👉'; color = '#2196f3'; }
          }
          if (i === state.currentStep && state.status === 'running') { icon = '▶️'; color = '#2196f3'; }
          return `<div style="padding:6px 12px;border-left:3px solid ${color};margin:4px 0;background:${i === state.currentStep ? 'rgba(33,150,243,0.15)' : 'transparent'};border-radius:0 6px 6px 0;">
            <span>${icon}</span> <strong style="color:${color}">[${step.service}]</strong> ${step.desc}
            ${result && result.notes ? `<br><small style="color:#aaa">📝 ${result.notes}</small>` : ''}
          </div>`;
        }).join('');
      }

      this.panel.innerHTML = `
        <div style="background:linear-gradient(135deg,#16213e,#0f3460);padding:12px 16px;display:flex;justify-content:space-between;align-items:center;">
          <span style="font-size:15px;font-weight:bold;">🔄 跨服务业务流编排器</span>
          <span style="cursor:pointer;font-size:18px;" onclick="document.getElementById('aiops-workflow-panel').style.display='none'">✕</span>
        </div>

        ${state.status === 'idle' ? `
          <div style="padding:16px;">
            <div style="margin-bottom:12px;font-weight:bold;color:#64b5f6;">📋 选择业务流模板</div>
            ${Object.entries(WORKFLOW_TEMPLATES).map(([key, tpl]) => `
              <div style="padding:10px;margin:6px 0;background:#16213e;border-radius:8px;cursor:pointer;border:1px solid #333;"
                   onmouseover="this.style.borderColor='#2196f3'" onmouseout="this.style.borderColor='#333'"
                   onclick="window.__aiopsWfEngine.startWorkflow('${key}');window.__aiopsWfEngine.executeCurrentStep();">
                <strong>${tpl.name}</strong> <small style="color:#aaa">(${tpl.steps.length}步)</small><br>
                <small style="color:#888">${tpl.description}</small>
              </div>
            `).join('')}
          </div>
        ` : `
          <div style="padding:12px 16px;background:#16213e;">
            <div style="display:flex;justify-content:space-between;align-items:center;">
              <strong style="color:#64b5f6;">${state.workflowName}</strong>
              <span style="font-size:11px;padding:3px 8px;border-radius:10px;background:${state.status === 'running' ? '#2196f3' : state.status === 'paused' ? '#ff9800' : '#4caf50'};color:#fff;">
                ${state.status === 'running' ? '执行中' : state.status === 'paused' ? '已暂停' : '已完成'}
              </span>
            </div>
            <div style="display:flex;gap:8px;margin-top:8px;font-size:11px;">
              <span>✅ ${report.passed}</span>
              <span>❌ ${report.failed}</span>
              <span>⏭️ ${report.skipped}</span>
              <span>⬜ ${report.pending}</span>
              <span style="margin-left:auto;">进度: ${state.currentStep}/${report.total}</span>
            </div>
            <div style="height:4px;background:#333;border-radius:2px;margin-top:6px;">
              <div style="height:100%;background:linear-gradient(90deg,#4caf50,#2196f3);width:${report.total > 0 ? ((state.currentStep / report.total) * 100) : 0}%;border-radius:2px;transition:width 0.3s;"></div>
            </div>
          </div>

          <div style="max-height:40vh;overflow-y:auto;padding:8px 12px;">
            ${stepListHtml}
          </div>

          <div style="padding:12px 16px;border-top:1px solid #333;display:flex;gap:6px;flex-wrap:wrap;">
            ${state.status === 'running' ? `
              <button onclick="window.__aiopsWfEngine.confirmStep(true, prompt('备注(可选):'))" style="flex:1;padding:8px;border:none;border-radius:6px;background:#4caf50;color:#fff;cursor:pointer;font-weight:bold;">✅ 通过</button>
              <button onclick="window.__aiopsWfEngine.confirmStep(false, prompt('失败原因:'))" style="flex:1;padding:8px;border:none;border-radius:6px;background:#f44336;color:#fff;cursor:pointer;font-weight:bold;">❌ 失败</button>
              <button onclick="window.__aiopsWfEngine.skipStep()" style="padding:8px 12px;border:none;border-radius:6px;background:#ff9800;color:#fff;cursor:pointer;">⏭️</button>
              <button onclick="window.__aiopsWfEngine.pauseWorkflow()" style="padding:8px 12px;border:none;border-radius:6px;background:#666;color:#fff;cursor:pointer;">⏸️</button>
            ` : state.status === 'paused' ? `
              <button onclick="window.__aiopsWfEngine.resumeWorkflow();window.__aiopsWfEngine.executeCurrentStep();" style="flex:1;padding:8px;border:none;border-radius:6px;background:#2196f3;color:#fff;cursor:pointer;font-weight:bold;">▶️ 继续</button>
            ` : `
              <button onclick="navigator.clipboard.writeText(JSON.stringify(window.__aiopsWfEngine.getReport(),null,2))" style="flex:1;padding:8px;border:none;border-radius:6px;background:#9c27b0;color:#fff;cursor:pointer;">📋 复制报告</button>
            `}
            <button onclick="if(confirm('确定重置？')){window.__aiopsWfEngine.resetWorkflow()}" style="padding:8px 12px;border:none;border-radius:6px;background:#333;color:#aaa;cursor:pointer;">🔄 重置</button>
          </div>
        `}
      `;
    }
  }

  // ============================
  // 初始化
  // ============================
  const engine = new WorkflowEngine();
  window.__aiopsWfEngine = engine;
  new WorkflowPanel(engine);

  console.log('%c[AIOPS] 跨服务业务流编排器已加载 (Ctrl+Shift+W)', 'color:#2196f3;font-weight:bold;');
})();
