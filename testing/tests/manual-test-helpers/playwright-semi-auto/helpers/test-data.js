// ========================================
// 测试数据生成器
// ========================================
// 功能：生成随机但真实的测试数据

export class TestData {
  static generateUser() {
    const timestamp = Date.now();
    const random = Math.floor(Math.random() * 1000);
    
    return {
      username: `test_user_${timestamp}_${random}`,
      email: `test${timestamp}@aiops.com`,
      phone: this.generatePhone(),
      password: 'Test123!@#',
      realName: `测试用户${random}`,
      role: '普通用户',
      department: '测试部门',
      position: '测试工程师'
    };
  }

  static generateTenant() {
    const timestamp = Date.now();
    const random = Math.floor(Math.random() * 1000);
    
    return {
      name: `测试租户_${timestamp}`,
      code: `TENANT${random}`,
      contact: `联系人${random}`,
      phone: this.generatePhone(),
      email: `tenant${timestamp}@aiops.com`,
      address: `测试地址${random}号`,
      description: '这是一个自动生成的测试租户'
    };
  }

  static generateDevice() {
    const types = ['光伏板', '储能柜', '充电桩', '变压器', '逆变器'];
    const manufacturers = ['华为', '比亚迪', '特来电', 'ABB', '施耐德'];
    const random = Math.floor(Math.random() * 10000);
    
    return {
      name: `设备_${random}`,
      code: `DEV${Date.now()}`,
      type: types[Math.floor(Math.random() * types.length)],
      manufacturer: manufacturers[Math.floor(Math.random() * manufacturers.length)],
      model: `Model-${random}`,
      sn: `SN${Date.now()}${random}`,
      power: Math.floor(Math.random() * 1000) + 100,
      location: `位置${random}`,
      installDate: new Date().toISOString().split('T')[0],
      status: '在线'
    };
  }

  static generateChargingOrder() {
    const random = Math.floor(Math.random() * 1000);
    
    return {
      orderNo: `CHG${Date.now()}`,
      pileId: `PILE${random}`,
      userId: `USER${random}`,
      startTime: new Date().toISOString(),
      energy: Math.floor(Math.random() * 50) + 10,
      amount: (Math.random() * 100 + 20).toFixed(2),
      status: '充电中'
    };
  }

  static generateWorkOrder() {
    const types = ['设备故障', '定期维护', '紧急抢修', '巡检任务'];
    const priorities = ['低', '中', '高', '紧急'];
    const random = Math.floor(Math.random() * 1000);
    
    return {
      title: `工单_${random}`,
      orderNo: `WO${Date.now()}`,
      type: types[Math.floor(Math.random() * types.length)],
      priority: priorities[Math.floor(Math.random() * priorities.length)],
      deviceId: `DEV${random}`,
      description: `这是一个自动生成的测试工单描述_${random}`,
      assignee: `工程师${random % 10}`,
      expectedTime: new Date(Date.now() + 86400000).toISOString().split('T')[0],
      status: '待处理'
    };
  }

  static generateStation() {
    const types = ['充电站', '储能站', '光伏站', '综合能源站'];
    const random = Math.floor(Math.random() * 1000);
    
    return {
      name: `站点_${random}`,
      code: `STATION${random}`,
      type: types[Math.floor(Math.random() * types.length)],
      address: `测试地址${random}号`,
      longitude: (116 + Math.random()).toFixed(6),
      latitude: (39 + Math.random()).toFixed(6),
      capacity: Math.floor(Math.random() * 1000) + 500,
      deviceCount: Math.floor(Math.random() * 50) + 10,
      operator: `运营商${random % 5}`,
      contactPhone: this.generatePhone(),
      status: '运营中'
    };
  }

  static generatePermission() {
    const services = ['user', 'device', 'charging', 'workorder', 'station'];
    const resources = ['user', 'role', 'permission', 'device', 'order'];
    const actions = ['create', 'read', 'update', 'delete', 'export'];
    
    const service = services[Math.floor(Math.random() * services.length)];
    const resource = resources[Math.floor(Math.random() * resources.length)];
    const action = actions[Math.floor(Math.random() * actions.length)];
    
    return {
      code: `${service}:${resource}:${action}`,
      name: `${service}服务-${resource}-${action}`,
      description: `允许对${service}服务的${resource}进行${action}操作`,
      service,
      resource,
      action
    };
  }

  static generateRule() {
    const types = ['阈值告警', '状态变化', '数据异常', '定时任务'];
    const random = Math.floor(Math.random() * 1000);
    
    return {
      name: `规则_${random}`,
      code: `RULE${Date.now()}`,
      type: types[Math.floor(Math.random() * types.length)],
      condition: `temperature > ${Math.floor(Math.random() * 50) + 30}`,
      action: `发送告警通知`,
      enabled: true,
      priority: Math.floor(Math.random() * 5) + 1,
      description: `这是一个自动生成的测试规则_${random}`
    };
  }

  static generateSettlement() {
    const random = Math.floor(Math.random() * 1000);
    
    return {
      settlementNo: `SETTLE${Date.now()}`,
      tenantId: `TENANT${random}`,
      period: new Date().toISOString().substring(0, 7),
      totalEnergy: Math.floor(Math.random() * 10000) + 1000,
      totalAmount: (Math.random() * 10000 + 1000).toFixed(2),
      status: '待结算'
    };
  }

  // ========== 辅助方法 ==========
  
  static generatePhone() {
    const prefixes = ['138', '139', '158', '188', '189'];
    const prefix = prefixes[Math.floor(Math.random() * prefixes.length)];
    const suffix = Math.floor(Math.random() * 100000000).toString().padStart(8, '0');
    return prefix + suffix;
  }

  static generateEmail() {
    const domains = ['aiops.com', 'test.com', 'example.com'];
    const domain = domains[Math.floor(Math.random() * domains.length)];
    return `test${Date.now()}@${domain}`;
  }

  static generateDateRange(days = 7) {
    const end = new Date();
    const start = new Date(end.getTime() - days * 24 * 60 * 60 * 1000);
    
    return {
      start: start.toISOString().split('T')[0],
      end: end.toISOString().split('T')[0]
    };
  }

  static generateRandomString(length = 8) {
    const chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789';
    let result = '';
    for (let i = 0; i < length; i++) {
      result += chars.charAt(Math.floor(Math.random() * chars.length));
    }
    return result;
  }

  static generateRandomNumber(min = 0, max = 100) {
    return Math.floor(Math.random() * (max - min + 1)) + min;
  }
}
