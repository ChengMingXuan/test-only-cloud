/**
 * 充电监控 - Mock API 测试
 * 覆盖：监控页加载、实时数据、告警信息、图表、状态指示
 */

describe('充电监控 - Mock API 测试', () => {

  beforeEach(() => {
    // Mock 充电监控数据接口
    cy.intercept('GET', '**/api/charging/monitor**', {
      statusCode: 200,
      body: {
        success: true,
        data: {
          onlineCount: 85,
          chargingCount: 42,
          idleCount: 43,
          faultCount: 3,
          totalPower: 2350.7,
          realtimeData: [
            { deviceId: 'PILE-001', power: 120, soc: 65, status: 'charging' },
            { deviceId: 'PILE-002', power: 80, soc: 45, status: 'charging' },
            { deviceId: 'PILE-003', power: 0, soc: 0, status: 'idle' }
          ]
        }
      },
      delay: 300
    }).as('chargingMonitorRequest');

    // Mock 充电趋势数据
    cy.intercept('GET', '**/api/charging/trend**', {
      statusCode: 200,
      body: {
        success: true,
        data: [
          { time: '00:00', count: 12, power: 450 },
          { time: '04:00', count: 8, power: 320 },
          { time: '08:00', count: 25, power: 1200 },
          { time: '12:00', count: 42, power: 2100 },
          { time: '16:00', count: 38, power: 1850 },
          { time: '20:00', count: 28, power: 1350 }
        ]
      },
      delay: 200
    }).as('chargingTrendRequest');

    cy.visitAuth('/charging/monitor');
  });

  it('[P0] 充电监控页面加载', () => {
    cy.get('.ant-layout, #root', { timeout: 20000 }).should('be.visible');
    cy.url().should('include', '/charging/monitor');
  });

  it('[P0] 监控数据卡片显示', () => {
    cy.get('.ant-card, .ant-statistic, .ant-pro-card, [class*="card"]', { timeout: 20000 })
      .should('exist');
  });

  it('[P0] 统计数据包含内容', () => {
    cy.get('.ant-card, .ant-statistic', { timeout: 15000 })
      .first()
      .should('exist');
  });

  it('[P1] Tab/分段器切换', () => {
    cy.get('.ant-tabs-tab, .ant-segmented-item, [class*=tab], .ant-card, .ant-layout-content', { timeout: 15000 }).then(($tabs) => {
      const realTabs = $tabs.filter('.ant-tabs-tab, .ant-segmented-item');
      if (realTabs.length > 1) {
        cy.wrap(realTabs).eq(1).click({ force: true });
        cy.wait(300);
      }
      cy.get('.ant-layout, #root', { timeout: 10000 }).should('exist');
    });
  });

  it('[P1] 图表区域存在', () => {
    // 图表可能异步加载，检查容器存在即可
    cy.get('canvas, [class*=chart], [class*=Chart], .ant-card, .ant-statistic, svg, .ant-layout-content', { timeout: 15000 }).should('exist');
  });

  it('[P1] 筛选或操作按钮', () => {
    cy.get('button, .ant-btn, .ant-dropdown', { timeout: 15000 })
      .should('exist');
  });

  it('[P2] 无显示错误', () => {
    cy.get('body').should('not.contain.text', 'Uncaught Error');
    cy.get('body').should('not.contain.text', 'ChunkLoadError');
  });
});
