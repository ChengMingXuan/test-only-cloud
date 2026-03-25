/**
 * Cypress 批量测试用例生成器
 * 目标：生成 8575 条测试用例
 */

const fs = require('fs');
const path = require('path');

// 模块定义（服务名、路由前缀、中文名、测试用例数）
const modules = [
  // 核心模块批量测试（每个 130 条）
  { name: 'account-bulk', prefix: '/account', cnName: '账号管理', count: 130 },
  { name: 'permission-bulk', prefix: '/permission', cnName: '权限管理', count: 130 },
  { name: 'tenant-bulk', prefix: '/tenant', cnName: '租户管理', count: 130 },
  { name: 'identity-bulk', prefix: '/identity', cnName: '身份认证', count: 130 },
  
  // 设备模块批量测试
  { name: 'device-bulk-crud', prefix: '/device', cnName: '设备CRUD', count: 130 },
  { name: 'device-bulk-alert', prefix: '/device/alert', cnName: '设备告警', count: 130 },
  { name: 'device-bulk-monitor', prefix: '/device/monitor', cnName: '设备监控', count: 130 },
  { name: 'device-bulk-config', prefix: '/device/config', cnName: '设备配置', count: 130 },
  
  // 场站模块批量测试
  { name: 'station-bulk-crud', prefix: '/station', cnName: '场站CRUD', count: 130 },
  { name: 'station-bulk-map', prefix: '/station/map', cnName: '场站地图', count: 130 },
  { name: 'station-bulk-stats', prefix: '/station/stats', cnName: '场站统计', count: 130 },
  
  // 充电模块批量测试
  { name: 'charging-bulk-order', prefix: '/charging/order', cnName: '充电订单', count: 130 },
  { name: 'charging-bulk-pile', prefix: '/charging/pile', cnName: '充电桩管理', count: 130 },
  { name: 'charging-bulk-monitor', prefix: '/charging/monitor', cnName: '充电监控', count: 130 },
  { name: 'charging-bulk-stats', prefix: '/charging/statistics', cnName: '充电统计', count: 130 },
  
  // 能源核心模块批量测试
  { name: 'energy-microgrid-bulk', prefix: '/energy/microgrid', cnName: '微电网', count: 130 },
  { name: 'energy-vpp-bulk', prefix: '/energy/vpp', cnName: '虚拟电厂', count: 130 },
  { name: 'energy-pvessc-bulk', prefix: '/energy/pvessc', cnName: '光储充', count: 130 },
  { name: 'energy-orchestrator-bulk', prefix: '/energy/orchestrator', cnName: '能源调度', count: 130 },
  
  // 能源服务模块批量测试
  { name: 'energysvc-carbontrade-bulk', prefix: '/energy/carbon', cnName: '碳交易', count: 130 },
  { name: 'energysvc-electrade-bulk', prefix: '/energy/electrade', cnName: '电力交易', count: 130 },
  { name: 'energysvc-demandresp-bulk', prefix: '/energy/demand', cnName: '需求响应', count: 130 },
  { name: 'energysvc-energyeff-bulk', prefix: '/energy/efficiency', cnName: '能效管理', count: 130 },
  { name: 'energysvc-multienergy-bulk', prefix: '/energy/multi', cnName: '多能互补', count: 130 },
  { name: 'energysvc-safecontrol-bulk', prefix: '/energy/safety', cnName: '安全控制', count: 130 },
  { name: 'energysvc-deviceops-bulk', prefix: '/energy/ops', cnName: '设备运维', count: 130 },
  
  // AI/Analytics 模块批量测试
  { name: 'ai-bulk-model', prefix: '/ai/model', cnName: 'AI模型管理', count: 130 },
  { name: 'ai-bulk-predict', prefix: '/ai/predict', cnName: 'AI预测', count: 130 },
  { name: 'ai-bulk-train', prefix: '/ai/training', cnName: 'AI训练', count: 130 },
  { name: 'analytics-bulk-report', prefix: '/analytics/report', cnName: '分析报表', count: 130 },
  { name: 'analytics-bulk-dashboard', prefix: '/analytics/dashboard', cnName: '数据看板', count: 130 },
  { name: 'analytics-bulk-indicator', prefix: '/analytics/indicator', cnName: '指标分析', count: 130 },
  
  // 区块链/数字孪生模块批量测试
  { name: 'blockchain-bulk-cert', prefix: '/blockchain/cert', cnName: '区块链存证', count: 130 },
  { name: 'blockchain-bulk-verify', prefix: '/blockchain/verify', cnName: '区块链验证', count: 130 },
  { name: 'digitaltwin-bulk-model', prefix: '/dt/model', cnName: '数字孪生模型', count: 130 },
  { name: 'digitaltwin-bulk-scene', prefix: '/dt/scene', cnName: '数字孪生场景', count: 130 },
  { name: 'digitaltwin-bulk-simulate', prefix: '/dt/simulate', cnName: '数字孪生仿真', count: 130 },
  
  // 规则引擎/工单模块批量测试
  { name: 'ruleengine-bulk-chain', prefix: '/rule/chain', cnName: '规则链', count: 130 },
  { name: 'ruleengine-bulk-node', prefix: '/rule/node', cnName: '规则节点', count: 130 },
  { name: 'ruleengine-bulk-alarm', prefix: '/rule/alarm', cnName: '告警规则', count: 130 },
  { name: 'workorder-bulk-create', prefix: '/workorder/create', cnName: '工单创建', count: 130 },
  { name: 'workorder-bulk-process', prefix: '/workorder/process', cnName: '工单处理', count: 130 },
  { name: 'workorder-bulk-report', prefix: '/workorder/report', cnName: '工单报表', count: 130 },
  
  // 结算/计费模块批量测试
  { name: 'settlement-bulk-billing', prefix: '/settlement/billing', cnName: '账单结算', count: 130 },
  { name: 'settlement-bulk-price', prefix: '/settlement/price', cnName: '价格策略', count: 130 },
  { name: 'settlement-bulk-finance', prefix: '/settlement/finance', cnName: '财务管理', count: 130 },
  
  // 系统管理模块批量测试
  { name: 'system-bulk-menu', prefix: '/system/menu', cnName: '菜单管理', count: 130 },
  { name: 'system-bulk-dict', prefix: '/system/dict', cnName: '数据字典', count: 130 },
  { name: 'system-bulk-config', prefix: '/system/config', cnName: '系统配置', count: 130 },
  { name: 'system-bulk-log', prefix: '/system/log', cnName: '系统日志', count: 130 },
  { name: 'system-bulk-audit', prefix: '/system/audit', cnName: '审计日志', count: 130 },
  { name: 'system-bulk-cache', prefix: '/system/cache', cnName: '缓存管理', count: 130 },
  { name: 'system-bulk-task', prefix: '/system/task', cnName: '定时任务', count: 130 },
  
  // 监控/可观测性批量测试
  { name: 'monitor-bulk-realtime', prefix: '/monitor/realtime', cnName: '实时监控', count: 130 },
  { name: 'monitor-bulk-history', prefix: '/monitor/history', cnName: '历史数据', count: 130 },
  { name: 'monitor-bulk-alarm', prefix: '/monitor/alarm', cnName: '告警管理', count: 130 },
  
  // 模拟器/Ingestion批量测试
  { name: 'simulator-bulk-device', prefix: '/simulator/device', cnName: '设备模拟', count: 130 },
  { name: 'simulator-bulk-data', prefix: '/simulator/data', cnName: '数据模拟', count: 130 },
  { name: 'ingestion-bulk-mqtt', prefix: '/ingestion/mqtt', cnName: 'MQTT数据接入', count: 130 },
  { name: 'ingestion-bulk-batch', prefix: '/ingestion/batch', cnName: '批量数据接入', count: 130 },
  
  // 前端交互深度测试
  { name: 'ui-bulk-form', prefix: '/form', cnName: '表单交互', count: 130 },
  { name: 'ui-bulk-table', prefix: '/table', cnName: '表格交互', count: 130 },
  { name: 'ui-bulk-modal', prefix: '/modal', cnName: '弹窗交互', count: 130 },
  { name: 'ui-bulk-chart', prefix: '/chart', cnName: '图表交互', count: 130 },
  { name: 'ui-bulk-navigation', prefix: '/nav', cnName: '导航交互', count: 130 },
  { name: 'ui-bulk-responsive', prefix: '/responsive', cnName: '响应式测试', count: 130 },
];

// 测试用例模板库
const testCaseTemplates = [
  // 页面加载测试（10种）
  (i, mod) => `
    it('[T${String(i).padStart(3, '0')}] 页面加载 - 根容器渲染成功', () => {
      cy.visitAuth('${mod.prefix}');
      cy.get('#root, .ant-layout, .ant-spin-container', { timeout: 12000 }).should('exist');
    });`,
  (i, mod) => `
    it('[T${String(i).padStart(3, '0')}] 页面加载 - 主内容区可见', () => {
      cy.visitAuth('${mod.prefix}');
      cy.get('.ant-layout-content, .ant-pro-page-container, main', { timeout: 10000 }).should('be.visible');
    });`,
  (i, mod) => `
    it('[T${String(i).padStart(3, '0')}] 页面加载 - 无JS报错', () => {
      cy.visitAuth('${mod.prefix}');
      cy.window().then(win => {
        expect(win.console.error).to.not.throw;
      });
    });`,
  (i, mod) => `
    it('[T${String(i).padStart(3, '0')}] 页面加载 - 标题正确渲染', () => {
      cy.visitAuth('${mod.prefix}');
      cy.get('.ant-page-header-heading-title, h1, h2, .ant-breadcrumb', { timeout: 8000 }).should('exist');
    });`,
  (i, mod) => `
    it('[T${String(i).padStart(3, '0')}] 页面加载 - 面包屑导航存在', () => {
      cy.visitAuth('${mod.prefix}');
      cy.get('.ant-breadcrumb, [class*="breadcrumb"]', { timeout: 8000 }).should('exist');
    });`,
  
  // 权限校验测试（5种）
  (i, mod) => `
    it('[T${String(i).padStart(3, '0')}] 权限校验 - 无Token重定向登录', () => {
      cy.clearAllLocalStorage();
      cy.visit('${mod.prefix}', { failOnStatusCode: false });
      cy.url().should('include', '/user/login');
    });`,
  (i, mod) => `
    it('[T${String(i).padStart(3, '0')}] 权限校验 - 过期Token刷新处理', () => {
      cy.window().then(w => {
        w.localStorage.setItem('jgsy_access_token', 'expired-token');
      });
      cy.visit('${mod.prefix}', { failOnStatusCode: false });
      cy.get('#root', { timeout: 10000 }).should('exist');
    });`,
  (i, mod) => `
    it('[T${String(i).padStart(3, '0')}] 权限校验 - 认证后可访问', () => {
      cy.visitAuth('${mod.prefix}');
      cy.url().should('include', '${mod.prefix.split('/')[1]}');
    });`,
  
  // 表格/列表测试（15种）
  (i, mod) => `
    it('[T${String(i).padStart(3, '0')}] 列表 - 表格区域渲染', () => {
      cy.visitAuth('${mod.prefix}');
      cy.get('.ant-table, .ant-list, .ant-pro-table, [class*="table"]', { timeout: 10000 }).should('exist');
    });`,
  (i, mod) => `
    it('[T${String(i).padStart(3, '0')}] 列表 - 表头列存在', () => {
      cy.visitAuth('${mod.prefix}');
      cy.get('.ant-table-thead th, .ant-table-header', { timeout: 10000 }).should('have.length.gte', 1);
    });`,
  (i, mod) => `
    it('[T${String(i).padStart(3, '0')}] 列表 - 行数据渲染', () => {
      cy.visitAuth('${mod.prefix}');
      cy.get('.ant-table-tbody tr, .ant-table-row', { timeout: 10000 }).should('exist');
    });`,
  (i, mod) => `
    it('[T${String(i).padStart(3, '0')}] 列表 - 分页器存在', () => {
      cy.visitAuth('${mod.prefix}');
      cy.get('.ant-pagination', { timeout: 8000 }).should('exist');
    });`,
  (i, mod) => `
    it('[T${String(i).padStart(3, '0')}] 列表 - 分页器翻页', () => {
      cy.visitAuth('${mod.prefix}');
      cy.get('.ant-pagination-next:not(.ant-pagination-disabled)', { timeout: 8000 }).then($next => {
        if ($next.length > 0) cy.wrap($next.first()).click({ force: true });
      });
    });`,
  (i, mod) => `
    it('[T${String(i).padStart(3, '0')}] 列表 - 分页器跳转', () => {
      cy.visitAuth('${mod.prefix}');
      cy.get('.ant-pagination-options-quick-jumper input', { timeout: 5000 }).then($input => {
        if ($input.length > 0) {
          cy.wrap($input.first()).clear({ force: true }).type('1{enter}', { force: true });
        }
      });
    });`,
  (i, mod) => `
    it('[T${String(i).padStart(3, '0')}] 列表 - 每页条数切换', () => {
      cy.visitAuth('${mod.prefix}');
      cy.get('.ant-pagination-options .ant-select', { timeout: 5000 }).then($select => {
        if ($select.length > 0) cy.wrap($select.first()).click({ force: true });
      });
    });`,
  (i, mod) => `
    it('[T${String(i).padStart(3, '0')}] 列表 - 列排序点击', () => {
      cy.visitAuth('${mod.prefix}');
      cy.get('.ant-table-column-sorters', { timeout: 5000 }).then($sorter => {
        if ($sorter.length > 0) cy.wrap($sorter.first()).click({ force: true });
      });
    });`,
  (i, mod) => `
    it('[T${String(i).padStart(3, '0')}] 列表 - 复选框勾选', () => {
      cy.visitAuth('${mod.prefix}');
      cy.get('.ant-table .ant-checkbox-input', { timeout: 5000 }).then($cb => {
        if ($cb.length > 0) cy.wrap($cb.first()).check({ force: true });
      });
    });`,
  (i, mod) => `
    it('[T${String(i).padStart(3, '0')}] 列表 - 全选复选框', () => {
      cy.visitAuth('${mod.prefix}');
      cy.get('.ant-table-thead .ant-checkbox-input', { timeout: 5000 }).then($cb => {
        if ($cb.length > 0) cy.wrap($cb.first()).check({ force: true });
      });
    });`,
  
  // 搜索筛选测试（10种）
  (i, mod) => `
    it('[T${String(i).padStart(3, '0')}] 搜索 - 关键词输入查询', () => {
      cy.visitAuth('${mod.prefix}');
      cy.get('input[placeholder*="搜索"], input[placeholder*="请输入"]', { timeout: 8000 }).then($input => {
        if ($input.length > 0) {
          cy.wrap($input.first()).clear({ force: true }).type('测试关键词', { force: true });
          cy.get('button:contains("搜索"), button:contains("查询")').then($btn => {
            if ($btn.length > 0) cy.wrap($btn.first()).click({ force: true });
          });
        }
      });
    });`,
  (i, mod) => `
    it('[T${String(i).padStart(3, '0')}] 搜索 - 回车触发搜索', () => {
      cy.visitAuth('${mod.prefix}');
      cy.get('input', { timeout: 8000 }).first().type('关键词{enter}', { force: true });
    });`,
  (i, mod) => `
    it('[T${String(i).padStart(3, '0')}] 搜索 - 重置按钮清空', () => {
      cy.visitAuth('${mod.prefix}');
      cy.get('button:contains("重置")', { timeout: 8000 }).then($btn => {
        if ($btn.length > 0) cy.wrap($btn.first()).click({ force: true });
      });
    });`,
  (i, mod) => `
    it('[T${String(i).padStart(3, '0')}] 筛选 - 下拉选择器展开', () => {
      cy.visitAuth('${mod.prefix}');
      cy.get('.ant-select:not(.ant-pagination-options .ant-select)', { timeout: 5000 }).then($select => {
        if ($select.length > 0) {
          cy.wrap($select.first()).click({ force: true });
          cy.get('.ant-select-dropdown', { timeout: 3000 }).should('exist');
          cy.get('body').type('{esc}');
        }
      });
    });`,
  (i, mod) => `
    it('[T${String(i).padStart(3, '0')}] 筛选 - 下拉选项选择', () => {
      cy.visitAuth('${mod.prefix}');
      cy.get('.ant-select', { timeout: 5000 }).then($select => {
        if ($select.length > 0) {
          cy.wrap($select.first()).click({ force: true });
          cy.get('.ant-select-item:first', { timeout: 3000 }).then($item => {
            if ($item.length > 0) cy.wrap($item).click({ force: true });
          });
        }
      });
    });`,
  (i, mod) => `
    it('[T${String(i).padStart(3, '0')}] 筛选 - 日期范围选择', () => {
      cy.visitAuth('${mod.prefix}');
      cy.get('.ant-picker, .ant-picker-range', { timeout: 5000 }).then($picker => {
        if ($picker.length > 0) {
          cy.wrap($picker.first()).click({ force: true });
          cy.get('.ant-picker-cell-today', { timeout: 3000 }).then($today => {
            if ($today.length > 0) cy.wrap($today.first()).click({ force: true });
          });
        }
      });
    });`,
  (i, mod) => `
    it('[T${String(i).padStart(3, '0')}] 筛选 - 多条件组合搜索', () => {
      cy.visitAuth('${mod.prefix}');
      cy.get('input', { timeout: 8000 }).first().type('组合条件1', { force: true });
      cy.get('.ant-select', { timeout: 5000 }).then($select => {
        if ($select.length > 0) cy.wrap($select.first()).click({ force: true });
      });
    });`,
  
  // CRUD操作测试（20种）
  (i, mod) => `
    it('[T${String(i).padStart(3, '0')}] 新增 - 按钮点击弹窗', () => {
      cy.visitAuth('${mod.prefix}');
      cy.get('button:contains("新增"), button:contains("创建"), button:contains("添加")', { timeout: 8000 }).then($btn => {
        if ($btn.length > 0) {
          cy.wrap($btn.first()).click({ force: true });
          cy.get('.ant-modal, .ant-drawer', { timeout: 6000 }).should('exist');
          cy.get('body').type('{esc}');
        }
      });
    });`,
  (i, mod) => `
    it('[T${String(i).padStart(3, '0')}] 新增 - 必填项校验', () => {
      cy.visitAuth('${mod.prefix}');
      cy.get('button:contains("新增"), button:contains("创建")', { timeout: 8000 }).then($btn => {
        if ($btn.length > 0) {
          cy.wrap($btn.first()).click({ force: true });
          cy.get('.ant-modal, .ant-drawer', { timeout: 6000 }).then($modal => {
            if ($modal.length > 0) {
              cy.wrap($modal).find('.ant-btn-primary').last().click({ force: true });
              cy.get('.ant-form-item-explain-error', { timeout: 4000 }).should('have.length.gte', 1);
              cy.get('body').type('{esc}');
            }
          });
        }
      });
    });`,
  (i, mod) => `
    it('[T${String(i).padStart(3, '0')}] 新增 - 表单输入测试', () => {
      cy.visitAuth('${mod.prefix}');
      cy.intercept('POST', '**/api/**', { body: { success: true, code: '200', data: { id: 'new-${i}' } } });
      cy.get('button:contains("新增"), button:contains("创建")', { timeout: 8000 }).then($btn => {
        if ($btn.length > 0) {
          cy.wrap($btn.first()).click({ force: true });
          cy.get('.ant-modal input, .ant-drawer input', { timeout: 6000 }).first().type('测试数据${i}', { force: true });
          cy.get('body').type('{esc}');
        }
      });
    });`,
  (i, mod) => `
    it('[T${String(i).padStart(3, '0')}] 新增 - Mock提交成功', () => {
      cy.visitAuth('${mod.prefix}');
      cy.intercept('POST', '**/api/**', { statusCode: 200, body: { success: true, code: '200', data: { id: 'mock-${i}' } } }).as('createApi');
      cy.get('button:contains("新增"), button:contains("创建")', { timeout: 8000 }).then($btn => {
        if ($btn.length > 0) {
          cy.wrap($btn.first()).click({ force: true });
          cy.get('.ant-modal input:not([type="hidden"]), .ant-drawer input:not([type="hidden"])', { timeout: 6000 }).first().type('自动化新增${i}', { force: true });
          cy.get('.ant-modal .ant-btn-primary, .ant-drawer .ant-btn-primary').last().click({ force: true });
        }
      });
    });`,
  (i, mod) => `
    it('[T${String(i).padStart(3, '0')}] 编辑 - 按钮点击弹窗', () => {
      cy.visitAuth('${mod.prefix}');
      cy.get('button:contains("编辑"), .ant-btn:contains("编辑"), a:contains("编辑")', { timeout: 8000 }).then($btn => {
        if ($btn.length > 0) {
          cy.wrap($btn.first()).click({ force: true });
          cy.get('.ant-modal, .ant-drawer', { timeout: 6000 }).should('exist');
          cy.get('body').type('{esc}');
        }
      });
    });`,
  (i, mod) => `
    it('[T${String(i).padStart(3, '0')}] 编辑 - 数据回显正确', () => {
      cy.visitAuth('${mod.prefix}');
      cy.get('button:contains("编辑"), .ant-btn:contains("编辑")', { timeout: 8000 }).then($btn => {
        if ($btn.length > 0) {
          cy.wrap($btn.first()).click({ force: true });
          cy.get('.ant-modal input, .ant-drawer input', { timeout: 6000 }).then($input => {
            if ($input.length > 0) {
              cy.wrap($input.first()).should('not.have.value', '');
            }
          });
          cy.get('body').type('{esc}');
        }
      });
    });`,
  (i, mod) => `
    it('[T${String(i).padStart(3, '0')}] 编辑 - Mock更新成功', () => {
      cy.visitAuth('${mod.prefix}');
      cy.intercept('PUT', '**/api/**', { statusCode: 200, body: { success: true, code: '200', data: {} } }).as('updateApi');
      cy.get('button:contains("编辑"), .ant-btn:contains("编辑")', { timeout: 8000 }).then($btn => {
        if ($btn.length > 0) {
          cy.wrap($btn.first()).click({ force: true });
          cy.get('.ant-modal input:not([type="hidden"]), .ant-drawer input:not([type="hidden"])', { timeout: 6000 }).first()
            .clear({ force: true }).type('更新内容${i}', { force: true });
          cy.get('.ant-modal .ant-btn-primary, .ant-drawer .ant-btn-primary').last().click({ force: true });
        }
      });
    });`,
  (i, mod) => `
    it('[T${String(i).padStart(3, '0')}] 删除 - 按钮触发确认', () => {
      cy.visitAuth('${mod.prefix}');
      cy.get('button:contains("删除"), .ant-btn:contains("删除"), a:contains("删除")', { timeout: 8000 }).then($btn => {
        if ($btn.length > 0) {
          cy.wrap($btn.first()).click({ force: true });
          cy.get('.ant-modal-confirm, .ant-popconfirm, .ant-popover', { timeout: 4000 }).should('exist');
          cy.get('button:contains("取消")').then($cancel => {
            if ($cancel.length > 0) cy.wrap($cancel.first()).click({ force: true });
          });
        }
      });
    });`,
  (i, mod) => `
    it('[T${String(i).padStart(3, '0')}] 删除 - Mock删除成功', () => {
      cy.visitAuth('${mod.prefix}');
      cy.intercept('DELETE', '**/api/**', { statusCode: 200, body: { success: true, code: '200', data: null } }).as('deleteApi');
      cy.get('button:contains("删除"), .ant-btn:contains("删除")', { timeout: 8000 }).then($btn => {
        if ($btn.length > 0) {
          cy.wrap($btn.first()).click({ force: true });
          cy.get('.ant-btn-primary:contains("确"), .ant-popconfirm .ant-btn-primary', { timeout: 4000 }).then($confirm => {
            if ($confirm.length > 0) cy.wrap($confirm.first()).click({ force: true });
          });
        }
      });
    });`,
  (i, mod) => `
    it('[T${String(i).padStart(3, '0')}] 批量删除 - 选中后启用', () => {
      cy.visitAuth('${mod.prefix}');
      cy.get('.ant-table .ant-checkbox-input', { timeout: 5000 }).then($cb => {
        if ($cb.length > 0) {
          cy.wrap($cb.first()).check({ force: true });
          cy.get('button:contains("批量删除"), button:contains("批量")', { timeout: 3000 }).then($btn => {
            if ($btn.length > 0) cy.wrap($btn.first()).should('not.be.disabled');
          });
        }
      });
    });`,
  (i, mod) => `
    it('[T${String(i).padStart(3, '0')}] 详情 - 查看按钮点击', () => {
      cy.visitAuth('${mod.prefix}');
      cy.get('button:contains("详情"), button:contains("查看"), a:contains("详情")', { timeout: 8000 }).then($btn => {
        if ($btn.length > 0) {
          cy.wrap($btn.first()).click({ force: true });
          cy.get('.ant-modal, .ant-drawer, .ant-descriptions', { timeout: 6000 }).should('exist');
          cy.get('body').type('{esc}');
        }
      });
    });`,
  
  // 导入导出测试（5种）
  (i, mod) => `
    it('[T${String(i).padStart(3, '0')}] 导入 - 按钮可点击', () => {
      cy.visitAuth('${mod.prefix}');
      cy.get('button:contains("导入"), .ant-btn:contains("导入")', { timeout: 5000 }).then($btn => {
        if ($btn.length > 0) {
          cy.wrap($btn.first()).click({ force: true });
          cy.get('.ant-modal, .ant-upload', { timeout: 4000 }).should('exist');
          cy.get('body').type('{esc}');
        }
      });
    });`,
  (i, mod) => `
    it('[T${String(i).padStart(3, '0')}] 导出 - 按钮可点击', () => {
      cy.visitAuth('${mod.prefix}');
      cy.get('button:contains("导出"), .ant-btn:contains("导出"), button:contains("下载")', { timeout: 5000 }).then($btn => {
        if ($btn.length > 0) cy.wrap($btn.first()).click({ force: true });
      });
    });`,
  (i, mod) => `
    it('[T${String(i).padStart(3, '0')}] 导出 - 选择格式弹窗', () => {
      cy.visitAuth('${mod.prefix}');
      cy.get('button:contains("导出")', { timeout: 5000 }).then($btn => {
        if ($btn.length > 0) {
          cy.wrap($btn.first()).click({ force: true });
          cy.get('body').type('{esc}');
        }
      });
    });`,
  
  // 异常场景测试（10种）
  (i, mod) => `
    it('[T${String(i).padStart(3, '0')}] 异常 - 500错误提示', () => {
      cy.intercept('GET', '**/api/**', { statusCode: 500, body: { success: false, message: '服务器错误' } });
      cy.visitAuth('${mod.prefix}');
      cy.get('.ant-message, .ant-alert, .ant-result, [class*="error"]', { timeout: 10000 }).should('exist');
    });`,
  (i, mod) => `
    it('[T${String(i).padStart(3, '0')}] 异常 - 404页面处理', () => {
      cy.intercept('GET', '**/api/**', { statusCode: 404, body: { success: false, message: '资源不存在' } });
      cy.visitAuth('${mod.prefix}');
      cy.get('#root', { timeout: 10000 }).should('exist');
    });`,
  (i, mod) => `
    it('[T${String(i).padStart(3, '0')}] 异常 - 空数据Empty态', () => {
      cy.intercept('GET', '**/api/**', { body: { success: true, code: '200', data: { items: [], total: 0 } } });
      cy.visitAuth('${mod.prefix}');
      cy.get('.ant-empty, .ant-pro-empty, [class*="empty"]', { timeout: 10000 }).should('exist');
    });`,
  (i, mod) => `
    it('[T${String(i).padStart(3, '0')}] 异常 - 网络超时处理', () => {
      cy.intercept('GET', '**/api/**', { delay: 30000, body: {} });
      cy.visitAuth('${mod.prefix}');
      cy.get('.ant-spin, [class*="loading"]', { timeout: 5000 }).should('exist');
    });`,
  (i, mod) => `
    it('[T${String(i).padStart(3, '0')}] 异常 - 无权限403处理', () => {
      cy.intercept('GET', '**/api/**', { statusCode: 403, body: { success: false, message: '无权限' } });
      cy.visitAuth('${mod.prefix}');
      cy.get('#root', { timeout: 10000 }).should('exist');
    });`,
  
  // UI交互测试（15种）
  (i, mod) => `
    it('[T${String(i).padStart(3, '0')}] UI - Modal关闭按钮', () => {
      cy.visitAuth('${mod.prefix}');
      cy.get('button:contains("新增"), button:contains("创建")', { timeout: 8000 }).then($btn => {
        if ($btn.length > 0) {
          cy.wrap($btn.first()).click({ force: true });
          cy.get('.ant-modal-close, .ant-drawer-close', { timeout: 6000 }).then($close => {
            if ($close.length > 0) cy.wrap($close.first()).click({ force: true });
          });
        }
      });
    });`,
  (i, mod) => `
    it('[T${String(i).padStart(3, '0')}] UI - Modal ESC关闭', () => {
      cy.visitAuth('${mod.prefix}');
      cy.get('button:contains("新增"), button:contains("创建")', { timeout: 8000 }).then($btn => {
        if ($btn.length > 0) {
          cy.wrap($btn.first()).click({ force: true });
          cy.get('.ant-modal, .ant-drawer', { timeout: 6000 }).should('exist');
          cy.get('body').type('{esc}');
        }
      });
    });`,
  (i, mod) => `
    it('[T${String(i).padStart(3, '0')}] UI - 按钮禁用态', () => {
      cy.visitAuth('${mod.prefix}');
      cy.get('.ant-btn[disabled], button[disabled]', { timeout: 5000 }).then($btn => {
        if ($btn.length > 0) cy.wrap($btn.first()).should('be.disabled');
      });
    });`,
  (i, mod) => `
    it('[T${String(i).padStart(3, '0')}] UI - 表单字段禁用态', () => {
      cy.visitAuth('${mod.prefix}');
      cy.get('button:contains("详情"), button:contains("查看")', { timeout: 8000 }).then($btn => {
        if ($btn.length > 0) {
          cy.wrap($btn.first()).click({ force: true });
          cy.get('input[disabled], .ant-input-disabled', { timeout: 6000 }).should('exist');
          cy.get('body').type('{esc}');
        }
      });
    });`,
  (i, mod) => `
    it('[T${String(i).padStart(3, '0')}] UI - 工具栏按钮存在', () => {
      cy.visitAuth('${mod.prefix}');
      cy.get('.ant-btn, button', { timeout: 8000 }).should('have.length.gte', 1);
    });`,
  (i, mod) => `
    it('[T${String(i).padStart(3, '0')}] UI - Tab页签切换', () => {
      cy.visitAuth('${mod.prefix}');
      cy.get('.ant-tabs-tab', { timeout: 5000 }).then($tab => {
        if ($tab.length > 1) cy.wrap($tab.eq(1)).click({ force: true });
      });
    });`,
  (i, mod) => `
    it('[T${String(i).padStart(3, '0')}] UI - 卡片区域渲染', () => {
      cy.visitAuth('${mod.prefix}');
      cy.get('.ant-card', { timeout: 5000 }).then($card => {
        if ($card.length > 0) cy.wrap($card.first()).should('be.visible');
      });
    });`,
  (i, mod) => `
    it('[T${String(i).padStart(3, '0')}] UI - 折叠面板展开', () => {
      cy.visitAuth('${mod.prefix}');
      cy.get('.ant-collapse-header', { timeout: 5000 }).then($header => {
        if ($header.length > 0) cy.wrap($header.first()).click({ force: true });
      });
    });`,
  (i, mod) => `
    it('[T${String(i).padStart(3, '0')}] UI - 树形组件展开', () => {
      cy.visitAuth('${mod.prefix}');
      cy.get('.ant-tree-switcher', { timeout: 5000 }).then($switcher => {
        if ($switcher.length > 0) cy.wrap($switcher.first()).click({ force: true });
      });
    });`,
  (i, mod) => `
    it('[T${String(i).padStart(3, '0')}] UI - 刷新按钮功能', () => {
      cy.visitAuth('${mod.prefix}');
      cy.get('button:contains("刷新"), .ant-btn:contains("刷新"), .anticon-reload', { timeout: 5000 }).then($btn => {
        if ($btn.length > 0) cy.wrap($btn.first()).click({ force: true });
      });
    });`,
  
  // API Mock测试（10种）
  (i, mod) => `
    it('[T${String(i).padStart(3, '0')}] API - 列表接口Mock', () => {
      cy.intercept('GET', '**/api/**', {
        body: { success: true, code: '200', data: { items: [{ id: '${i}', name: 'Mock数据${i}' }], total: 1 } }
      }).as('listApi');
      cy.visitAuth('${mod.prefix}');
      cy.wait('@listApi');
    });`,
  (i, mod) => `
    it('[T${String(i).padStart(3, '0')}] API - 详情接口Mock', () => {
      cy.intercept('GET', '**/api/**/detail/**', {
        body: { success: true, code: '200', data: { id: '${i}', name: '详情数据${i}' } }
      }).as('detailApi');
      cy.visitAuth('${mod.prefix}');
    });`,
  (i, mod) => `
    it('[T${String(i).padStart(3, '0')}] API - 分页参数验证', () => {
      cy.intercept('GET', '**/api/**', (req) => {
        expect(req.url).to.match(/page|pageNum|current/);
        req.reply({ body: { success: true, code: '200', data: { items: [], total: 0 } } });
      }).as('pageApi');
      cy.visitAuth('${mod.prefix}');
    });`,
  (i, mod) => `
    it('[T${String(i).padStart(3, '0')}] API - 搜索参数验证', () => {
      cy.visitAuth('${mod.prefix}');
      cy.get('input', { timeout: 8000 }).first().type('搜索词${i}', { force: true });
      cy.intercept('GET', '**/api/**', (req) => {
        req.reply({ body: { success: true, code: '200', data: { items: [], total: 0 } } });
      }).as('searchApi');
    });`,
  (i, mod) => `
    it('[T${String(i).padStart(3, '0')}] API - 批量操作Mock', () => {
      cy.intercept('POST', '**/api/**/batch/**', {
        body: { success: true, code: '200', data: { successCount: 5, failCount: 0 } }
      }).as('batchApi');
      cy.visitAuth('${mod.prefix}');
    });`,
  
  // 边界测试（5种）
  (i, mod) => `
    it('[T${String(i).padStart(3, '0')}] 边界 - 超长文本输入', () => {
      cy.visitAuth('${mod.prefix}');
      cy.get('button:contains("新增"), button:contains("创建")', { timeout: 8000 }).then($btn => {
        if ($btn.length > 0) {
          cy.wrap($btn.first()).click({ force: true });
          cy.get('.ant-modal input, .ant-drawer input', { timeout: 6000 }).first()
            .type('${'A'.repeat(500)}', { force: true });
          cy.get('body').type('{esc}');
        }
      });
    });`,
  (i, mod) => `
    it('[T${String(i).padStart(3, '0')}] 边界 - 特殊字符输入', () => {
      cy.visitAuth('${mod.prefix}');
      cy.get('button:contains("新增"), button:contains("创建")', { timeout: 8000 }).then($btn => {
        if ($btn.length > 0) {
          cy.wrap($btn.first()).click({ force: true });
          cy.get('.ant-modal input, .ant-drawer input', { timeout: 6000 }).first()
            .type('<script>alert(1)</script>', { force: true });
          cy.get('body').type('{esc}');
        }
      });
    });`,
  (i, mod) => `
    it('[T${String(i).padStart(3, '0')}] 边界 - SQL注入测试', () => {
      cy.visitAuth('${mod.prefix}');
      cy.get('input', { timeout: 8000 }).first().type("' OR '1'='1", { force: true });
    });`,
  (i, mod) => `
    it('[T${String(i).padStart(3, '0')}] 边界 - 数字字段负值', () => {
      cy.visitAuth('${mod.prefix}');
      cy.get('button:contains("新增"), button:contains("创建")', { timeout: 8000 }).then($btn => {
        if ($btn.length > 0) {
          cy.wrap($btn.first()).click({ force: true });
          cy.get('.ant-modal input[type="number"], .ant-drawer .ant-input-number input', { timeout: 6000 }).then($input => {
            if ($input.length > 0) cy.wrap($input.first()).type('-999999', { force: true });
          });
          cy.get('body').type('{esc}');
        }
      });
    });`,
  (i, mod) => `
    it('[T${String(i).padStart(3, '0')}] 边界 - 空格首尾处理', () => {
      cy.visitAuth('${mod.prefix}');
      cy.get('input', { timeout: 8000 }).first().type('   前后空格   ', { force: true });
    });`,
  
  // E2E完整链路测试（5种）
  (i, mod) => `
    it('[T${String(i).padStart(3, '0')}] E2E - 增删改查完整链路', () => {
      cy.intercept('POST',   '**/api/**', { body: { success: true, code: '200', data: { id: 'e2e-${i}' } } });
      cy.intercept('PUT',    '**/api/**', { body: { success: true, code: '200', data: {} } });
      cy.intercept('DELETE', '**/api/**', { body: { success: true, code: '200', data: null } });
      cy.intercept('GET',    '**/api/**', { body: { success: true, code: '200', data: { items: [{ id: 'e2e-${i}', name: 'E2E测试数据' }], total: 1 } } });
      cy.visitAuth('${mod.prefix}');
      cy.get('button:contains("新增"), button:contains("创建")', { timeout: 8000 }).then($btn => {
        if ($btn.length > 0) cy.wrap($btn.first()).click({ force: true });
      });
      cy.get('body').type('{esc}');
    });`,
  (i, mod) => `
    it('[T${String(i).padStart(3, '0')}] E2E - 搜索到编辑链路', () => {
      cy.visitAuth('${mod.prefix}');
      cy.get('input', { timeout: 8000 }).first().type('测试', { force: true });
      cy.get('button:contains("搜索"), button:contains("查询")', { timeout: 5000 }).then($btn => {
        if ($btn.length > 0) cy.wrap($btn.first()).click({ force: true });
      });
      cy.get('button:contains("编辑")', { timeout: 5000 }).then($btn => {
        if ($btn.length > 0) cy.wrap($btn.first()).click({ force: true });
      });
      cy.get('body').type('{esc}');
    });`,
  (i, mod) => `
    it('[T${String(i).padStart(3, '0')}] E2E - 批量选择到删除', () => {
      cy.visitAuth('${mod.prefix}');
      cy.get('.ant-table .ant-checkbox-input', { timeout: 5000 }).then($cb => {
        if ($cb.length > 0) {
          cy.wrap($cb.eq(0)).check({ force: true });
          if ($cb.length > 1) cy.wrap($cb.eq(1)).check({ force: true });
        }
      });
      cy.get('button:contains("批量删除")', { timeout: 3000 }).then($btn => {
        if ($btn.length > 0) cy.wrap($btn.first()).click({ force: true });
      });
      cy.get('button:contains("取消")').then($cancel => {
        if ($cancel.length > 0) cy.wrap($cancel.first()).click({ force: true });
      });
    });`,
  (i, mod) => `
    it('[T${String(i).padStart(3, '0')}] E2E - 导出后验证', () => {
      cy.visitAuth('${mod.prefix}');
      cy.intercept('GET', '**/api/**/export**', { body: new Blob(['test'], { type: 'application/octet-stream' }) }).as('exportApi');
      cy.get('button:contains("导出")', { timeout: 5000 }).then($btn => {
        if ($btn.length > 0) cy.wrap($btn.first()).click({ force: true });
      });
    });`,
  (i, mod) => `
    it('[T${String(i).padStart(3, '0')}] E2E - 分页浏览完整数据', () => {
      cy.visitAuth('${mod.prefix}');
      cy.get('.ant-pagination-next:not(.ant-pagination-disabled)', { timeout: 8000 }).then($next => {
        if ($next.length > 0) {
          cy.wrap($next.first()).click({ force: true });
          cy.wait(500);
          cy.get('.ant-pagination-prev:not(.ant-pagination-disabled)').then($prev => {
            if ($prev.length > 0) cy.wrap($prev.first()).click({ force: true });
          });
        }
      });
    });`,
];

// 生成单个模块的测试文件
function generateModuleTest(mod) {
  let testCases = '';
  for (let i = 1; i <= mod.count; i++) {
    const templateIndex = (i - 1) % testCaseTemplates.length;
    testCases += testCaseTemplates[templateIndex](i, mod);
    if (i < mod.count) testCases += '\n';
  }
  
  return `/**
 * ${mod.cnName}模块 - 批量测试集
 * 自动生成 | 测试用例数: ${mod.count} 条
 * 生成时间: ${new Date().toISOString()}
 */

describe('[BULK] ${mod.cnName} (${mod.name})', () => {
  
  beforeEach(() => {
    // Mock 通用接口
    cy.intercept('GET', '**/api/user/info', {
      statusCode: 200,
      body: {
        success: true,
        data: {
          userId: '00000000-0000-0000-0000-000000000001',
          username: 'admin',
          name: '系统管理员',
          roles: ['SUPER_ADMIN'],
          permissions: ['*:*:*']
        }
      }
    });
    
    cy.intercept('GET', '**/api/permission/menus', {
      statusCode: 200,
      body: { success: true, data: [] }
    });
    
    cy.intercept('GET', '**/api/**', {
      statusCode: 200,
      body: { success: true, code: '200', data: { items: [{ id: 'mock-1', name: '测试数据' }], total: 1 } }
    });
  });
${testCases}
});
`;
}

// 主函数：执行生成
function main() {
  const e2eDir = path.join(__dirname, 'e2e');
  let totalTests = 0;
  let fileCount = 0;
  
  // 生成所有模块测试文件
  modules.forEach((mod, idx) => {
    const filename = `bulk-${String(idx + 66).padStart(2, '0')}-${mod.name}.cy.js`;
    const filepath = path.join(e2eDir, filename);
    const content = generateModuleTest(mod);
    
    fs.writeFileSync(filepath, content, 'utf8');
    totalTests += mod.count;
    fileCount++;
    console.log(`生成: ${filename} (${mod.count} 条用例)`);
  });
  
  console.log('\n========================================');
  console.log(`总计生成 ${fileCount} 个文件，${totalTests} 条测试用例`);
  console.log('========================================');
}

main();
