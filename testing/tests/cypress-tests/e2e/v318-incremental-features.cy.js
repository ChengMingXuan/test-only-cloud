/**
 * v3.18 增量功能 - Cypress UI交互测试
 * ======================================
 * 测试新增功能模块的前端页面交互：
 * - 碳认证管理页面
 * - 智能排队充电页面
 * - 能耗报表页面
 * - CIM调度配置页面
 * - 组串监控页面
 * - AI预测配置页面
 * - Agent对话页面
 * - 设备健康页面
 * - 第三方模型配置页面
 */

// ═══════════════════════════════════════════════════════════════════════════════
// 通用配置与工具函数
// ═══════════════════════════════════════════════════════════════════════════════

const BASE_URL = Cypress.env('BASE_URL') || 'http://localhost:3000';

// Mock API响应
const mockApiSuccess = (data = {}) => ({
  statusCode: 200,
  body: { code: 200, data, message: 'OK' }
});

const mockApiError = (message = '操作失败') => ({
  statusCode: 400,
  body: { code: 400, data: null, message }
});

// ═══════════════════════════════════════════════════════════════════════════════
// 1. 碳认证管理页面测试
// ═══════════════════════════════════════════════════════════════════════════════

describe('碳认证管理 - I-REC/CCER', () => {
  beforeEach(() => {
    // Mock登录状态
    cy.intercept('GET', '/api/auth/user/info', mockApiSuccess({
      id: 'user-001',
      username: 'admin',
      permissions: ['blockchain:carbon:view', 'blockchain:carbon:create', 'blockchain:carbon:manage']
    }));
  });

  describe('I-REC 绿证管理', () => {
    it('应该能够查看I-REC证书列表', () => {
      cy.intercept('GET', '/api/carbon/irec/certificates*', mockApiSuccess({
        items: [
          { id: '1', deviceCode: 'PV-001', status: 'active', generationMwh: 150 },
          { id: '2', deviceCode: 'PV-002', status: 'pending', generationMwh: 200 }
        ],
        total: 2
      }));

      cy.visit(`${BASE_URL}/carbon/irec/certificates`);
      cy.get('[data-testid="certificate-table"]').should('be.visible');
      cy.get('[data-testid="certificate-row"]').should('have.length', 2);
    });

    it('应该能够提交I-REC设备注册', () => {
      cy.intercept('POST', '/api/carbon/irec/register', mockApiSuccess({ id: 'new-device-001' }));

      cy.visit(`${BASE_URL}/carbon/irec/register`);
      
      cy.get('[data-testid="device-code-input"]').type('PV-NEW-001');
      cy.get('[data-testid="capacity-input"]').type('500');
      cy.get('[data-testid="device-type-select"]').click();
      cy.get('[data-testid="option-solar_pv"]').click();
      cy.get('[data-testid="submit-btn"]').click();

      cy.get('[data-testid="success-message"]').should('contain', '注册成功');
    });

    it('应该能够执行证书转让操作', () => {
      cy.intercept('POST', '/api/carbon/irec/*/transfer', mockApiSuccess({ message: '转让成功' }));
      cy.intercept('GET', '/api/carbon/irec/certificates/*', mockApiSuccess({
        id: 'cert-001', deviceCode: 'PV-001', status: 'active'
      }));

      cy.visit(`${BASE_URL}/carbon/irec/certificates/cert-001`);
      
      cy.get('[data-testid="transfer-btn"]').click();
      cy.get('[data-testid="transfer-modal"]').should('be.visible');
      cy.get('[data-testid="target-account-input"]').type('account-002');
      cy.get('[data-testid="confirm-transfer-btn"]').click();

      cy.get('[data-testid="success-message"]').should('be.visible');
    });

    it('应该在注销证书时显示确认对话框', () => {
      cy.intercept('POST', '/api/carbon/irec/*/retire', mockApiSuccess({ message: '注销成功' }));

      cy.visit(`${BASE_URL}/carbon/irec/certificates/cert-001`);
      cy.get('[data-testid="retire-btn"]').click();

      cy.get('[data-testid="confirm-dialog"]').should('be.visible');
      cy.get('[data-testid="confirm-dialog"]').should('contain', '确认注销');
    });
  });

  describe('CCER 碳信用管理', () => {
    it('应该能够查看CCER项目列表', () => {
      cy.intercept('GET', '/api/carbon/ccer/projects*', mockApiSuccess({
        items: [
          { id: '1', projectName: '江苏光伏项目', status: 'verified' },
          { id: '2', projectName: '浙江风电项目', status: 'pending' }
        ],
        total: 2
      }));

      cy.visit(`${BASE_URL}/carbon/ccer/projects`);
      cy.get('[data-testid="project-table"]').should('be.visible');
    });

    it('应该能够创建CCER项目', () => {
      cy.intercept('POST', '/api/carbon/ccer/project', mockApiSuccess({ id: 'project-001' }));

      cy.visit(`${BASE_URL}/carbon/ccer/project/create`);
      
      cy.get('[data-testid="project-name-input"]').type('测试碳减排项目');
      cy.get('[data-testid="methodology-select"]').click();
      cy.get('[data-testid="option-CM-001"]').click();
      cy.get('[data-testid="estimated-reduction-input"]').type('10000');
      cy.get('[data-testid="submit-btn"]').click();

      cy.get('[data-testid="success-message"]').should('be.visible');
    });
  });
});

// ═══════════════════════════════════════════════════════════════════════════════
// 2. 智能排队充电页面测试
// ═══════════════════════════════════════════════════════════════════════════════

describe('智能排队充电管理', () => {
  beforeEach(() => {
    cy.intercept('GET', '/api/auth/user/info', mockApiSuccess({
      id: 'user-001',
      permissions: ['charging:orderly:view', 'charging:orderly:create', 'charging:orderly:manage']
    }));
  });

  it('应该能够查看排队列表', () => {
    cy.intercept('GET', '/api/charging/orderly/*/queue', mockApiSuccess([
      { id: '1', vehicleId: '京A12345', currentSocPercent: 20, position: 1 },
      { id: '2', vehicleId: '京B88888', currentSocPercent: 10, position: 2 },
      { id: '3', vehicleId: '京C66666', currentSocPercent: 30, position: 3 }
    ]));

    cy.visit(`${BASE_URL}/charging/orderly/station/station-001/queue`);
    cy.get('[data-testid="queue-list"]').should('be.visible');
    cy.get('[data-testid="queue-item"]').should('have.length', 3);
  });

  it('应该能够提交排队请求', () => {
    cy.intercept('POST', '/api/charging/orderly/enqueue', mockApiSuccess({ queueId: 'queue-001' }));

    cy.visit(`${BASE_URL}/charging/orderly/enqueue`);
    
    cy.get('[data-testid="station-select"]').click();
    cy.get('[data-testid="option-station-001"]').click();
    cy.get('[data-testid="vehicle-id-input"]').type('京D55555');
    cy.get('[data-testid="current-soc-input"]').type('25');
    cy.get('[data-testid="target-soc-input"]').type('80');
    cy.get('[data-testid="submit-btn"]').click();

    cy.get('[data-testid="success-message"]').should('contain', '排队成功');
  });

  it('应该能够执行智能调度', () => {
    cy.intercept('POST', '/api/charging/orderly/*/dispatch', mockApiSuccess([
      { queueId: '1', assignedPileId: 'pile-001' },
      { queueId: '2', assignedPileId: 'pile-002' }
    ]));

    cy.visit(`${BASE_URL}/charging/orderly/station/station-001`);
    cy.get('[data-testid="dispatch-btn"]').click();

    cy.get('[data-testid="dispatch-result"]').should('be.visible');
    cy.get('[data-testid="assignment-item"]').should('have.length.at.least', 1);
  });

  it('应该能够取消排队', () => {
    cy.intercept('DELETE', '/api/charging/orderly/queue/*', mockApiSuccess({ message: '已取消' }));
    cy.intercept('GET', '/api/charging/orderly/*/queue', mockApiSuccess([
      { id: 'queue-001', vehicleId: '京A12345', position: 1 }
    ]));

    cy.visit(`${BASE_URL}/charging/orderly/station/station-001/queue`);
    cy.get('[data-testid="cancel-btn"]').first().click();
    cy.get('[data-testid="confirm-cancel-btn"]').click();

    cy.get('[data-testid="success-message"]').should('contain', '取消');
  });

  it('应该能够查看充电桩负荷状态', () => {
    cy.intercept('GET', '/api/charging/orderly/*/pile-load', mockApiSuccess([
      { pileId: 'pile-001', loadPercent: 85, status: 'high' },
      { pileId: 'pile-002', loadPercent: 45, status: 'normal' },
      { pileId: 'pile-003', loadPercent: 0, status: 'idle' }
    ]));

    cy.visit(`${BASE_URL}/charging/orderly/station/station-001/pile-load`);
    cy.get('[data-testid="pile-load-chart"]').should('be.visible');
    cy.get('[data-testid="pile-status-high"]').should('exist');
  });
});

// ═══════════════════════════════════════════════════════════════════════════════
// 3. 微电网能耗报表页面测试
// ═══════════════════════════════════════════════════════════════════════════════

describe('微电网能耗报表', () => {
  beforeEach(() => {
    cy.intercept('GET', '/api/auth/user/info', mockApiSuccess({
      id: 'user-001',
      permissions: ['mg:energy:view', 'mg:energy:create']
    }));
  });

  it('应该能够查看能耗概览', () => {
    cy.intercept('GET', '/api/microgrid/energy/overview*', mockApiSuccess({
      totalPvGeneration: 1500.5,
      totalConsumption: 1200.0,
      selfConsumptionRate: 0.85,
      gridExport: 300.5
    }));

    cy.visit(`${BASE_URL}/microgrid/energy/overview`);
    cy.get('[data-testid="energy-overview-card"]').should('be.visible');
    cy.get('[data-testid="pv-generation"]').should('contain', '1500.5');
  });

  it('应该能够查看日报表', () => {
    cy.intercept('GET', '/api/microgrid/energy/*/daily*', mockApiSuccess({
      date: '2025-03-18',
      hourlyData: Array(24).fill(null).map((_, i) => ({
        hour: i,
        pvGeneration: 50 + Math.random() * 100,
        consumption: 40 + Math.random() * 80
      }))
    }));

    cy.visit(`${BASE_URL}/microgrid/energy/grid-001/daily?date=2025-03-18`);
    cy.get('[data-testid="daily-chart"]').should('be.visible');
  });

  it('应该能够查看月报表', () => {
    cy.intercept('GET', '/api/microgrid/energy/*/monthly*', mockApiSuccess({
      year: 2025,
      month: 3,
      dailyData: Array(31).fill(null).map((_, i) => ({
        day: i + 1,
        pvGeneration: 500 + Math.random() * 500,
        consumption: 400 + Math.random() * 400
      }))
    }));

    cy.visit(`${BASE_URL}/microgrid/energy/grid-001/monthly?year=2025&month=3`);
    cy.get('[data-testid="monthly-chart"]').should('be.visible');
  });

  it('应该能够进行能耗趋势对比', () => {
    cy.intercept('POST', '/api/microgrid/energy/trend/comparison', mockApiSuccess([
      { gridId: 'grid-001', data: [100, 150, 200] },
      { gridId: 'grid-002', data: [120, 140, 180] }
    ]));

    cy.visit(`${BASE_URL}/microgrid/energy/comparison`);
    
    cy.get('[data-testid="grid-select"]').click();
    cy.get('[data-testid="option-grid-001"]').click();
    cy.get('[data-testid="option-grid-002"]').click();
    cy.get('[data-testid="compare-btn"]').click();

    cy.get('[data-testid="comparison-chart"]').should('be.visible');
  });
});

// ═══════════════════════════════════════════════════════════════════════════════
// 4. CIM调度配置页面测试
// ═══════════════════════════════════════════════════════════════════════════════

describe('CIM调度协议配置', () => {
  beforeEach(() => {
    cy.intercept('GET', '/api/auth/user/info', mockApiSuccess({
      id: 'user-001',
      permissions: ['orchestrator:cim:view', 'orchestrator:cim:manage', 'orchestrator:cim:dispatch']
    }));
  });

  it('应该能够查看CIM配置', () => {
    cy.intercept('GET', '/api/orchestrator/cim/config', mockApiSuccess({
      endpointUrl: 'https://dispatch.grid.cn/cim/v1',
      authType: 'certificate',
      status: 'connected'
    }));

    cy.visit(`${BASE_URL}/orchestrator/cim/config`);
    cy.get('[data-testid="cim-config-form"]').should('be.visible');
    cy.get('[data-testid="endpoint-url-input"]').should('have.value', 'https://dispatch.grid.cn/cim/v1');
  });

  it('应该能够保存CIM配置', () => {
    cy.intercept('PUT', '/api/orchestrator/cim/config', mockApiSuccess({ id: 'config-001' }));

    cy.visit(`${BASE_URL}/orchestrator/cim/config`);
    
    cy.get('[data-testid="endpoint-url-input"]').clear().type('https://new-dispatch.grid.cn/cim/v2');
    cy.get('[data-testid="timeout-input"]').clear().type('60');
    cy.get('[data-testid="save-btn"]').click();

    cy.get('[data-testid="success-message"]').should('be.visible');
  });

  it('应该能够查看调度记录', () => {
    cy.intercept('GET', '/api/orchestrator/cim/dispatch/records*', mockApiSuccess({
      items: [
        { id: '1', commandType: 'EndDeviceControl', status: 'executed', createdAt: '2025-03-18T10:00:00Z' },
        { id: '2', commandType: 'SetPoint', status: 'pending', createdAt: '2025-03-18T11:00:00Z' }
      ],
      total: 2
    }));

    cy.visit(`${BASE_URL}/orchestrator/cim/dispatch/records`);
    cy.get('[data-testid="dispatch-table"]').should('be.visible');
    cy.get('[data-testid="dispatch-row"]').should('have.length', 2);
  });

  it('应该能够查看偏差分析', () => {
    cy.intercept('GET', '/api/orchestrator/cim/deviation/*/analysis', mockApiSuccess({
      avgDeviationPercent: 2.5,
      maxDeviationPercent: 5.2,
      complianceRate: 97.5,
      samples: 100
    }));

    cy.visit(`${BASE_URL}/orchestrator/cim/dispatch/record-001/deviation`);
    cy.get('[data-testid="deviation-analysis"]').should('be.visible');
    cy.get('[data-testid="avg-deviation"]').should('contain', '2.5%');
  });
});

// ═══════════════════════════════════════════════════════════════════════════════
// 5. 光伏组串监控页面测试
// ═══════════════════════════════════════════════════════════════════════════════

describe('光伏组串级监控', () => {
  beforeEach(() => {
    cy.intercept('GET', '/api/auth/user/info', mockApiSuccess({
      id: 'user-001',
      permissions: ['pvessc:string:view', 'pvessc:string:detect', 'pvessc:string:manage']
    }));
  });

  it('应该能够查看异常列表', () => {
    cy.intercept('GET', '/api/pvessc/string-monitor/anomalies*', mockApiSuccess({
      items: [
        { id: '1', stringId: 'STRING-01', anomalyType: 'hotspot', severity: 'high' },
        { id: '2', stringId: 'STRING-05', anomalyType: 'shading', severity: 'medium' }
      ],
      total: 2
    }));

    cy.visit(`${BASE_URL}/pvessc/string-monitor/anomalies`);
    cy.get('[data-testid="anomaly-table"]').should('be.visible');
    cy.get('[data-testid="anomaly-row"]').should('have.length', 2);
  });

  it('应该能够执行异常检测', () => {
    cy.intercept('POST', '/api/pvessc/string-monitor/*/detect', mockApiSuccess({
      totalStrings: 100,
      anomalyCount: 3,
      anomalies: [
        { stringId: 'STRING-01', type: 'hotspot' },
        { stringId: 'STRING-05', type: 'degradation' }
      ]
    }));

    cy.visit(`${BASE_URL}/pvessc/string-monitor/site-001`);
    cy.get('[data-testid="detect-btn"]').click();

    cy.get('[data-testid="detection-result"]').should('be.visible');
    cy.get('[data-testid="anomaly-count"]').should('contain', '3');
  });

  it('应该能够设置组串基准值', () => {
    cy.intercept('PUT', '/api/pvessc/string-monitor/*/baseline', mockApiSuccess({ message: '已设置' }));

    cy.visit(`${BASE_URL}/pvessc/string-monitor/site-001/baseline`);
    
    cy.get('[data-testid="string-select"]').click();
    cy.get('[data-testid="option-STRING-01"]').click();
    cy.get('[data-testid="baseline-power-input"]').type('3500');
    cy.get('[data-testid="save-btn"]').click();

    cy.get('[data-testid="success-message"]').should('be.visible');
  });

  it('应该能够按异常类型筛选', () => {
    cy.intercept('GET', '/api/pvessc/string-monitor/anomalies*', mockApiSuccess({
      items: [{ id: '1', anomalyType: 'hotspot' }],
      total: 1
    }));

    cy.visit(`${BASE_URL}/pvessc/string-monitor/anomalies`);
    cy.get('[data-testid="filter-type"]').click();
    cy.get('[data-testid="option-hotspot"]').click();

    cy.get('[data-testid="anomaly-row"]').should('have.length', 1);
  });
});

// ═══════════════════════════════════════════════════════════════════════════════
// 6. AI自适应预测页面测试
// ═══════════════════════════════════════════════════════════════════════════════

describe('AI自适应预测', () => {
  beforeEach(() => {
    cy.intercept('GET', '/api/auth/user/info', mockApiSuccess({
      id: 'user-001',
      permissions: ['iotcloudai:adaptive:predict', 'iotcloudai:adaptive:query', 'iotcloudai:adaptive:feedback']
    }));
  });

  it('应该能够执行自适应预测', () => {
    cy.intercept('POST', '/api/iotcloudai/adaptive/predict', mockApiSuccess({
      predictions: [100, 150, 200, 180, 160],
      modelUsed: 'lstm+attention',
      confidence: 0.92
    }));

    cy.visit(`${BASE_URL}/iotcloudai/adaptive/predict`);
    
    cy.get('[data-testid="scene-select"]').click();
    cy.get('[data-testid="option-pv_power"]').click();
    cy.get('[data-testid="forecast-hours-input"]').type('24');
    cy.get('[data-testid="predict-btn"]').click();

    cy.get('[data-testid="prediction-chart"]').should('be.visible');
    cy.get('[data-testid="model-used"]').should('contain', 'lstm+attention');
  });

  it('应该能够查看可用模型列表', () => {
    cy.intercept('GET', '/api/iotcloudai/adaptive/models*', mockApiSuccess([
      { id: '1', name: 'LSTM', scene: 'pv_power', accuracy: 0.95 },
      { id: '2', name: 'CNN-LSTM', scene: 'pv_power', accuracy: 0.93 },
      { id: '3', name: 'Transformer', scene: 'pv_power', accuracy: 0.94 }
    ]));

    cy.visit(`${BASE_URL}/iotcloudai/adaptive/models`);
    cy.get('[data-testid="model-table"]').should('be.visible');
    cy.get('[data-testid="model-row"]').should('have.length', 3);
  });

  it('应该能够提交准确率反馈', () => {
    cy.intercept('POST', '/api/iotcloudai/adaptive/performance', mockApiSuccess({ message: '已记录' }));

    cy.visit(`${BASE_URL}/iotcloudai/adaptive/feedback`);
    
    cy.get('[data-testid="scene-select"]').click();
    cy.get('[data-testid="option-pv_power"]').click();
    cy.get('[data-testid="predicted-values-input"]').type('100,150,200');
    cy.get('[data-testid="actual-values-input"]').type('95,155,195');
    cy.get('[data-testid="submit-btn"]').click();

    cy.get('[data-testid="success-message"]').should('be.visible');
  });
});

// ═══════════════════════════════════════════════════════════════════════════════
// 7. AI Agent对话页面测试
// ═══════════════════════════════════════════════════════════════════════════════

describe('AI Agent智能体', () => {
  beforeEach(() => {
    cy.intercept('GET', '/api/auth/user/info', mockApiSuccess({
      id: 'user-001',
      permissions: ['iotcloudai:agent:execute', 'iotcloudai:agent:query']
    }));
  });

  it('应该能够执行Agent任务', () => {
    cy.intercept('POST', '/api/iotcloudai/agent/execute', mockApiSuccess({
      result: '今日充电站收入为¥12,580，同比增长15%',
      steps: [
        { action: 'query_charging_data', status: 'completed' },
        { action: 'analyze_revenue', status: 'completed' }
      ],
      executionTime: 3.5
    }));

    cy.visit(`${BASE_URL}/iotcloudai/agent`);
    
    cy.get('[data-testid="goal-input"]').type('分析今日充电站收入');
    cy.get('[data-testid="execute-btn"]').click();

    cy.get('[data-testid="agent-result"]').should('be.visible');
    cy.get('[data-testid="agent-result"]').should('contain', '¥12,580');
  });

  it('应该显示执行步骤', () => {
    cy.intercept('POST', '/api/iotcloudai/agent/execute', mockApiSuccess({
      result: '分析完成',
      steps: [
        { action: 'query_data', status: 'completed' },
        { action: 'process', status: 'completed' },
        { action: 'generate_report', status: 'completed' }
      ]
    }));

    cy.visit(`${BASE_URL}/iotcloudai/agent`);
    cy.get('[data-testid="goal-input"]').type('测试任务');
    cy.get('[data-testid="execute-btn"]').click();

    cy.get('[data-testid="execution-steps"]').should('be.visible');
    cy.get('[data-testid="step-item"]').should('have.length', 3);
  });

  it('应该能够查看执行历史', () => {
    cy.intercept('GET', '/api/iotcloudai/agent/history*', mockApiSuccess([
      { id: '1', goal: '分析充电收入', createdAt: '2025-03-18T10:00:00Z' },
      { id: '2', goal: '预测光伏发电', createdAt: '2025-03-18T09:00:00Z' }
    ]));

    cy.visit(`${BASE_URL}/iotcloudai/agent/history`);
    cy.get('[data-testid="history-list"]').should('be.visible');
    cy.get('[data-testid="history-item"]').should('have.length', 2);
  });

  it('应该能够查看注册的Agent列表', () => {
    cy.intercept('GET', '/api/iotcloudai/agent/agents', mockApiSuccess([
      { agentId: 'daily_ops', name: '日常运维助手', description: '处理日常运维任务' },
      { agentId: 'report', name: '报表生成助手', description: '生成各类报表' },
      { agentId: 'prediction', name: '预测分析助手', description: '执行预测任务' }
    ]));

    cy.visit(`${BASE_URL}/iotcloudai/agent/list`);
    cy.get('[data-testid="agent-card"]').should('have.length', 3);
  });
});

// ═══════════════════════════════════════════════════════════════════════════════
// 8. 设备健康评估页面测试
// ═══════════════════════════════════════════════════════════════════════════════

describe('设备健康评估', () => {
  beforeEach(() => {
    cy.intercept('GET', '/api/auth/user/info', mockApiSuccess({
      id: 'user-001',
      permissions: ['iotcloudai:health:assess', 'iotcloudai:health:query']
    }));
  });

  it('应该能够评估单台设备健康度', () => {
    cy.intercept('POST', '/api/iotcloudai/health/assess', mockApiSuccess({
      deviceId: 'DEVICE-001',
      healthScore: 85,
      status: 'healthy',
      factors: [
        { name: '温度', score: 90 },
        { name: '电压稳定性', score: 88 },
        { name: '运行时间', score: 75 }
      ]
    }));

    cy.visit(`${BASE_URL}/iotcloudai/health/assess`);
    
    cy.get('[data-testid="device-id-input"]').type('DEVICE-001');
    cy.get('[data-testid="assess-btn"]').click();

    cy.get('[data-testid="health-result"]').should('be.visible');
    cy.get('[data-testid="health-score"]').should('contain', '85');
  });

  it('应该能够批量评估设备', () => {
    cy.intercept('POST', '/api/iotcloudai/health/assess/batch', mockApiSuccess([
      { deviceId: 'DEVICE-001', healthScore: 85 },
      { deviceId: 'DEVICE-002', healthScore: 72 },
      { deviceId: 'DEVICE-003', healthScore: 95 }
    ]));

    cy.visit(`${BASE_URL}/iotcloudai/health/batch`);
    
    cy.get('[data-testid="device-select"]').click();
    cy.get('[data-testid="select-all"]').click();
    cy.get('[data-testid="batch-assess-btn"]').click();

    cy.get('[data-testid="batch-result-table"]').should('be.visible');
    cy.get('[data-testid="result-row"]').should('have.length', 3);
  });

  it('应该能够查看健康趋势', () => {
    cy.intercept('GET', '/api/iotcloudai/health/trend/*', mockApiSuccess([
      { date: '2025-03-01', score: 90 },
      { date: '2025-03-10', score: 85 },
      { date: '2025-03-18', score: 82 }
    ]));

    cy.visit(`${BASE_URL}/iotcloudai/health/trend/DEVICE-001`);
    cy.get('[data-testid="trend-chart"]').should('be.visible');
  });
});

// ═══════════════════════════════════════════════════════════════════════════════
// 9. 第三方大模型配置页面测试
// ═══════════════════════════════════════════════════════════════════════════════

describe('第三方大模型管理', () => {
  beforeEach(() => {
    cy.intercept('GET', '/api/auth/user/info', mockApiSuccess({
      id: 'user-001',
      permissions: ['iotcloudai:thirdparty:chat', 'iotcloudai:thirdparty:query']
    }));
  });

  it('应该能够进行第三方模型对话', () => {
    cy.intercept('POST', '/api/iotcloudai/third-party/chat', mockApiSuccess({
      response: '光储充一体化系统是将光伏发电、储能和充电桩集成在一起的智能能源系统...',
      provider: 'ali',
      tokensUsed: 256
    }));

    cy.visit(`${BASE_URL}/iotcloudai/third-party/chat`);
    
    cy.get('[data-testid="message-input"]').type('请解释光储充一体化系统');
    cy.get('[data-testid="send-btn"]').click();

    cy.get('[data-testid="chat-response"]').should('be.visible');
    cy.get('[data-testid="chat-response"]').should('contain', '光储充');
  });

  it('应该能够查看可用供应商', () => {
    cy.intercept('GET', '/api/iotcloudai/third-party/providers', mockApiSuccess(['ali', 'tencent', 'baidu', 'bytedance']));

    cy.visit(`${BASE_URL}/iotcloudai/third-party/providers`);
    cy.get('[data-testid="provider-item"]').should('have.length', 4);
  });

  it('应该能够切换供应商', () => {
    cy.intercept('POST', '/api/iotcloudai/third-party/chat', mockApiSuccess({
      response: '回复内容',
      provider: 'tencent'
    }));

    cy.visit(`${BASE_URL}/iotcloudai/third-party/chat`);
    cy.get('[data-testid="provider-select"]').click();
    cy.get('[data-testid="option-tencent"]').click();
    cy.get('[data-testid="message-input"]').type('测试');
    cy.get('[data-testid="send-btn"]').click();

    cy.get('[data-testid="provider-badge"]').should('contain', 'tencent');
  });

  it('应该能够查看健康状态', () => {
    cy.intercept('GET', '/api/iotcloudai/third-party/health', mockApiSuccess(true));

    cy.visit(`${BASE_URL}/iotcloudai/third-party/status`);
    cy.get('[data-testid="health-status"]').should('contain', '正常');
  });
});
