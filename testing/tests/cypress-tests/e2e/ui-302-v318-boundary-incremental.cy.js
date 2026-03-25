/**
 * v3.18 六边界域架构增量测试 - Cypress UI测试
 * 覆盖范围：
 * 1. 碳认证管理页面
 * 2. 有序充电页面
 * 3. 微电网能耗报表页面
 * 4. CIM协议配置页面
 * 5. 组串监控页面
 * 6. 备件核销页面
 * 7. 六边界域服务监控页面
 */

describe('v3.18 六边界域架构增量测试 - UI交互', () => {

  beforeEach(() => {
    // Mock认证
    cy.intercept('POST', '**/api/identity/auth/login', {
      statusCode: 200,
      body: { code: 200, data: { token: 'test_token', userId: 'test_user' } }
    }).as('login');

    cy.intercept('GET', '**/api/identity/user/current', {
      statusCode: 200,
      body: { code: 200, data: { id: 'test_user', name: '测试用户', roles: ['admin'] } }
    }).as('currentUser');

    cy.intercept('GET', '**/api/permission/menu/tree', {
      statusCode: 200,
      body: { code: 200, data: [] }
    }).as('menuTree');
  });

  // ==================== 碳认证管理页面 ====================
  describe('碳认证管理 (Blockchain.CarbonCertification)', () => {

    beforeEach(() => {
      cy.intercept('GET', '**/api/carbon/irec/certificates*', {
        statusCode: 200,
        body: {
          code: 200,
          data: {
            items: [
              { id: 'cert-001', deviceName: '光伏电站A', status: 'active', issuedDate: '2026-01-15' },
              { id: 'cert-002', deviceName: '光伏电站B', status: 'retired', issuedDate: '2026-02-01' }
            ],
            total: 2
          }
        }
      }).as('getIrecCertificates');

      cy.intercept('GET', '**/api/carbon/ccer/projects*', {
        statusCode: 200,
        body: {
          code: 200,
          data: {
            items: [
              { id: 'proj-001', projectName: '林业碳汇项目', status: 'registered', estimatedReduction: 5000 }
            ],
            total: 1
          }
        }
      }).as('getCcerProjects');
    });

    it('应显示I-REC证书列表', () => {
      cy.visit('/blockchain/carbon/irec');
      cy.wait('@getIrecCertificates');
      cy.get('[data-testid="irec-table"]').should('exist');
      cy.contains('光伏电站A').should('be.visible');
    });

    it('应能提交I-REC设备注册', () => {
      cy.intercept('POST', '**/api/carbon/irec/register', {
        statusCode: 200,
        body: { code: 200, data: 'new-device-id' }
      }).as('registerDevice');

      cy.visit('/blockchain/carbon/irec/register');
      cy.get('[data-testid="device-name"]').type('新光伏电站');
      cy.get('[data-testid="capacity"]').type('10.5');
      cy.get('[data-testid="location"]').type('浙江省杭州市');
      cy.get('[data-testid="submit-btn"]').click();
      cy.wait('@registerDevice');
      cy.contains('注册成功').should('be.visible');
    });

    it('应能申请证书签发', () => {
      cy.intercept('POST', '**/api/carbon/irec/issue', {
        statusCode: 200,
        body: { code: 200, data: 'new-cert-id' }
      }).as('issueCert');

      cy.visit('/blockchain/carbon/irec/issue');
      cy.get('[data-testid="device-select"]').click();
      cy.get('.ant-select-item').first().click();
      cy.get('[data-testid="period"]').type('2026-03');
      cy.get('[data-testid="generation"]').type('1250.5');
      cy.get('[data-testid="submit-btn"]').click();
      cy.wait('@issueCert');
      cy.contains('签发申请已提交').should('be.visible');
    });

    it('应显示CCER项目列表', () => {
      cy.visit('/blockchain/carbon/ccer');
      cy.wait('@getCcerProjects');
      cy.get('[data-testid="ccer-table"]').should('exist');
      cy.contains('林业碳汇项目').should('be.visible');
    });
  });

  // ==================== 有序充电页面 ====================
  describe('有序充电 (Charging.OrderlyCharging)', () => {

    beforeEach(() => {
      cy.intercept('GET', '**/api/charging/orderly/*/queue', {
        statusCode: 200,
        body: {
          code: 200,
          data: [
            { queueId: 'q-001', vehicleId: 'v-001', soc: 25, targetSoc: 80, position: 1 },
            { queueId: 'q-002', vehicleId: 'v-002', soc: 35, targetSoc: 90, position: 2 }
          ]
        }
      }).as('getQueue');

      cy.intercept('GET', '**/api/charging/orderly/*/pile-load', {
        statusCode: 200,
        body: {
          code: 200,
          data: [
            { pileId: 'pile-001', pileName: '充电桩1号', load: 45.5, status: 'charging' },
            { pileId: 'pile-002', pileName: '充电桩2号', load: 0, status: 'idle' }
          ]
        }
      }).as('getPileLoad');
    });

    it('应显示排队列表', () => {
      cy.visit('/charging/orderly/queue/station-001');
      cy.wait('@getQueue');
      cy.get('[data-testid="queue-table"]').should('exist');
      cy.get('[data-testid="queue-row"]').should('have.length', 2);
    });

    it('应能提交排队请求', () => {
      cy.intercept('POST', '**/api/charging/orderly/enqueue', {
        statusCode: 200,
        body: { code: 200, data: 'new-queue-id' }
      }).as('enqueue');

      cy.visit('/charging/orderly/enqueue');
      cy.get('[data-testid="vehicle-id"]').type('粤B12345');
      cy.get('[data-testid="current-soc"]').type('25');
      cy.get('[data-testid="target-soc"]').type('80');
      cy.get('[data-testid="submit-btn"]').click();
      cy.wait('@enqueue');
      cy.contains('排队成功').should('be.visible');
    });

    it('应能执行智能调度', () => {
      cy.intercept('POST', '**/api/charging/orderly/*/dispatch', {
        statusCode: 200,
        body: {
          code: 200,
          data: [
            { queueId: 'q-001', pileId: 'pile-002' }
          ]
        }
      }).as('dispatch');

      cy.visit('/charging/orderly/station-001');
      cy.get('[data-testid="dispatch-btn"]').click();
      cy.wait('@dispatch');
      cy.contains('调度完成').should('be.visible');
    });

    it('应显示充电桩负荷状态', () => {
      cy.visit('/charging/orderly/pile-load/station-001');
      cy.wait('@getPileLoad');
      cy.get('[data-testid="pile-card"]').should('have.length', 2);
      cy.contains('充电桩1号').should('be.visible');
      cy.contains('45.5').should('be.visible');
    });
  });

  // ==================== 微电网能耗报表页面 ====================
  describe('微电网能耗报表 (MicroGrid.MgEnergyReport)', () => {

    beforeEach(() => {
      cy.intercept('GET', '**/api/microgrid/energy/overview*', {
        statusCode: 200,
        body: {
          code: 200,
          data: {
            totalConsumption: 12500.5,
            totalGeneration: 8500.2,
            peakLoad: 450.5,
            avgLoad: 320.3
          }
        }
      }).as('getOverview');

      cy.intercept('GET', '**/api/microgrid/energy/*/daily*', {
        statusCode: 200,
        body: {
          code: 200,
          data: {
            date: '2026-03-18',
            hourlyData: Array.from({ length: 24 }, (_, i) => ({
              hour: i,
              consumption: 50 + Math.random() * 50,
              generation: 30 + Math.random() * 30
            }))
          }
        }
      }).as('getDailyReport');
    });

    it('应显示能耗概览', () => {
      cy.visit('/microgrid/energy/overview');
      cy.wait('@getOverview');
      cy.get('[data-testid="total-consumption"]').should('contain', '12500.5');
      cy.get('[data-testid="total-generation"]').should('contain', '8500.2');
    });

    it('应显示日报表图表', () => {
      cy.visit('/microgrid/energy/daily/grid-001');
      cy.wait('@getDailyReport');
      cy.get('[data-testid="daily-chart"]').should('exist');
      cy.get('[data-testid="hourly-data-table"]').should('exist');
    });

    it('应能导出报表', () => {
      cy.intercept('POST', '**/api/microgrid/energy/export', {
        statusCode: 200,
        headers: { 'Content-Type': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' },
        body: new ArrayBuffer(0)
      }).as('exportReport');

      cy.visit('/microgrid/energy/overview');
      cy.wait('@getOverview');
      cy.get('[data-testid="export-btn"]').click();
      cy.wait('@exportReport');
    });
  });

  // ==================== CIM协议配置页面 ====================
  describe('CIM协议配置 (Orchestrator.CimProtocol)', () => {

    beforeEach(() => {
      cy.intercept('GET', '**/api/orchestrator/cim/config', {
        statusCode: 200,
        body: {
          code: 200,
          data: {
            endpoint: 'http://dispatch.grid.cn',
            authKey: '***',
            timeout: 30,
            enabled: true
          }
        }
      }).as('getConfig');

      cy.intercept('GET', '**/api/orchestrator/cim/dispatch/records*', {
        statusCode: 200,
        body: {
          code: 200,
          data: {
            items: [
              { id: 'rec-001', commandId: 'cmd-001', status: 'completed', targetPower: 5000, timestamp: '2026-03-18T10:00:00' }
            ],
            total: 1
          }
        }
      }).as('getRecords');
    });

    it('应显示CIM配置', () => {
      cy.visit('/orchestrator/cim/config');
      cy.wait('@getConfig');
      cy.get('[data-testid="endpoint-input"]').should('have.value', 'http://dispatch.grid.cn');
      cy.get('[data-testid="timeout-input"]').should('have.value', '30');
    });

    it('应能保存CIM配置', () => {
      cy.intercept('PUT', '**/api/orchestrator/cim/config', {
        statusCode: 200,
        body: { code: 200, data: 'config-id' }
      }).as('saveConfig');

      cy.visit('/orchestrator/cim/config');
      cy.wait('@getConfig');
      cy.get('[data-testid="endpoint-input"]').clear().type('http://new-dispatch.grid.cn');
      cy.get('[data-testid="save-btn"]').click();
      cy.wait('@saveConfig');
      cy.contains('配置已保存').should('be.visible');
    });

    it('应显示调度记录', () => {
      cy.visit('/orchestrator/cim/records');
      cy.wait('@getRecords');
      cy.get('[data-testid="records-table"]').should('exist');
      cy.contains('cmd-001').should('be.visible');
    });
  });

  // ==================== 组串监控页面 ====================
  describe('组串监控 (PVESSC.StringMonitor)', () => {

    beforeEach(() => {
      cy.intercept('GET', '**/api/pvessc/string/*/strings', {
        statusCode: 200,
        body: {
          code: 200,
          data: [
            { stringId: 'S001', current: 8.5, voltage: 650, power: 5525, status: 'normal' },
            { stringId: 'S002', current: 7.2, voltage: 645, power: 4644, status: 'warning' },
            { stringId: 'S003', current: 0, voltage: 0, power: 0, status: 'offline' }
          ]
        }
      }).as('getStrings');

      cy.intercept('GET', '**/api/pvessc/string/*/anomalies', {
        statusCode: 200,
        body: {
          code: 200,
          data: [
            { stringId: 'S002', anomalyType: 'low_current', timestamp: '2026-03-18T09:30:00' },
            { stringId: 'S003', anomalyType: 'offline', timestamp: '2026-03-18T08:00:00' }
          ]
        }
      }).as('getAnomalies');
    });

    it('应显示组串状态列表', () => {
      cy.visit('/pvessc/string/inverter-001');
      cy.wait('@getStrings');
      cy.get('[data-testid="string-table"]').should('exist');
      cy.get('[data-testid="string-row"]').should('have.length', 3);
    });

    it('应高亮显示异常组串', () => {
      cy.visit('/pvessc/string/inverter-001');
      cy.wait('@getStrings');
      cy.get('[data-testid="string-row-S002"]').should('have.class', 'warning');
      cy.get('[data-testid="string-row-S003"]').should('have.class', 'offline');
    });

    it('应显示异常记录', () => {
      cy.visit('/pvessc/string/inverter-001/anomalies');
      cy.wait('@getAnomalies');
      cy.get('[data-testid="anomaly-table"]').should('exist');
      cy.contains('low_current').should('be.visible');
    });
  });

  // ==================== 备件核销页面 ====================
  describe('备件核销 (WorkOrder.SparePartWriteoff)', () => {

    beforeEach(() => {
      cy.intercept('GET', '**/api/workorder/sparepart/writeoff*', {
        statusCode: 200,
        body: {
          code: 200,
          data: {
            items: [
              { id: 'wo-001', workOrderCode: 'WO-2026-001', status: 'pending', totalItems: 3, createdAt: '2026-03-18' },
              { id: 'wo-002', workOrderCode: 'WO-2026-002', status: 'approved', totalItems: 1, createdAt: '2026-03-17' }
            ],
            total: 2
          }
        }
      }).as('getWriteoffs');

      cy.intercept('GET', '**/api/workorder/sparepart/inventory*', {
        statusCode: 200,
        body: {
          code: 200,
          data: {
            items: [
              { id: 'part-001', name: '充电枪头', stock: 50, unit: '个' },
              { id: 'part-002', name: '通讯模块', stock: 20, unit: '块' }
            ],
            total: 2
          }
        }
      }).as('getInventory');
    });

    it('应显示核销单列表', () => {
      cy.visit('/workorder/sparepart/writeoff');
      cy.wait('@getWriteoffs');
      cy.get('[data-testid="writeoff-table"]').should('exist');
      cy.contains('WO-2026-001').should('be.visible');
    });

    it('应能创建核销单', () => {
      cy.intercept('POST', '**/api/workorder/sparepart/writeoff', {
        statusCode: 200,
        body: { code: 200, data: 'new-writeoff-id' }
      }).as('createWriteoff');

      cy.visit('/workorder/sparepart/writeoff/create');
      cy.wait('@getInventory');
      cy.get('[data-testid="workorder-select"]').click();
      cy.get('.ant-select-item').first().click();
      cy.get('[data-testid="add-item-btn"]').click();
      cy.get('[data-testid="part-select-0"]').click();
      cy.get('.ant-select-item').first().click();
      cy.get('[data-testid="quantity-0"]').type('2');
      cy.get('[data-testid="submit-btn"]').click();
      cy.wait('@createWriteoff');
      cy.contains('核销单已创建').should('be.visible');
    });

    it('应能审批核销单', () => {
      cy.intercept('POST', '**/api/workorder/sparepart/writeoff/*/approve', {
        statusCode: 200,
        body: { code: 200, data: '审批成功' }
      }).as('approveWriteoff');

      cy.visit('/workorder/sparepart/writeoff/wo-001');
      cy.get('[data-testid="approve-btn"]').click();
      cy.get('[data-testid="confirm-approve"]').click();
      cy.wait('@approveWriteoff');
      cy.contains('审批成功').should('be.visible');
    });
  });

  // ==================== 六边界域服务监控页面 ====================
  describe('六边界域服务监控 (Observability.ServiceOps)', () => {

    beforeEach(() => {
      cy.intercept('GET', '**/api/serviceops/services', {
        statusCode: 200,
        body: {
          code: 200,
          data: [
            { name: 'gateway', group: 'platform', status: 'running', health: 'healthy' },
            { name: 'device', group: 'shared', status: 'running', health: 'healthy' },
            { name: 'charging', group: 'charging', status: 'running', health: 'healthy' },
            { name: 'orchestrator', group: 'energy-core', status: 'running', health: 'healthy' },
            { name: 'trading', group: 'energy-trade', status: 'running', health: 'healthy' },
            { name: 'iotcloudai', group: 'intelligent', status: 'running', health: 'healthy' }
          ]
        }
      }).as('getServices');

      cy.intercept('GET', '**/api/serviceops/groups', {
        statusCode: 200,
        body: {
          code: 200,
          data: [
            { name: 'platform', displayName: '平台接入与底座域', serviceCount: 6 },
            { name: 'shared', displayName: '共享设备与规则域', serviceCount: 4 },
            { name: 'charging', displayName: '充电运营闭环域', serviceCount: 4 },
            { name: 'energy-core', displayName: '能源资源运营域', serviceCount: 5 },
            { name: 'energy-trade', displayName: '市场交易域', serviceCount: 2 },
            { name: 'intelligent', displayName: '智能与增值能力域', serviceCount: 5 }
          ]
        }
      }).as('getGroups');
    });

    it('应显示六边界域分组', () => {
      cy.visit('/observability/services');
      cy.wait('@getGroups');
      cy.get('[data-testid="group-card"]').should('have.length', 6);
      cy.contains('平台接入与底座域').should('be.visible');
      cy.contains('共享设备与规则域').should('be.visible');
      cy.contains('充电运营闭环域').should('be.visible');
      cy.contains('能源资源运营域').should('be.visible');
      cy.contains('市场交易域').should('be.visible');
      cy.contains('智能与增值能力域').should('be.visible');
    });

    it('应能按边界域筛选服务', () => {
      cy.visit('/observability/services');
      cy.wait('@getServices');
      cy.get('[data-testid="group-filter"]').click();
      cy.get('[data-testid="filter-energy-core"]').click();
      cy.get('[data-testid="service-row"]').should('have.length.at.least', 1);
      cy.contains('orchestrator').should('be.visible');
    });

    it('应显示服务健康状态', () => {
      cy.visit('/observability/services');
      cy.wait('@getServices');
      cy.get('[data-testid="health-indicator-healthy"]').should('have.length', 6);
    });
  });

});
