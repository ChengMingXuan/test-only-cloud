// ==UserScript==
// @name         AIOPS 表单自动填充助手 Pro - 全模块版
// @namespace    http://localhost:8000/
// @version      2.0
// @description  支持20+模块全面自动填充表单，智能识别字段类型
// @author       AIOPS Test Team
// @match        http://localhost:8000/*
// @match        http://localhost:*/*
// @grant        none
// @license      MIT
// ==/UserScript==

(function() {
  'use strict';

  const CONFIG = {
    // ========== 平台管理模块 ==========
    user: {
      username: 'test_user_' + Date.now(),
      password: 'Test@123456',
      email: 'test' + Date.now() + '@example.com',
      realName: '测试用户',
      phone: '18600000' + Math.floor(Math.random() * 10000).toString().padStart(4, '0'),
      role: 'user',
      status: 'active',
    },
    tenant: {
      name: '测试租户_' + Date.now(),
      code: 'TEST' + Date.now().toString().slice(-4),
      contact: '张三',
      contactPhone: '18600001111',
      contactEmail: 'tenant@example.com',
      address: '北京市朝阳区某某街道1号',
      description: '自动化测试租户',
    },
    role: {
      name: '测试角色_' + Date.now(),
      description: '自动化生成的角色',
      permissions: ['读', '写', '删除'],
      status: 'active',
    },
    permission: {
      name: 'test:resource:action',
      description: '测试权限',
      type: 'business',
    },
    menu: {
      name: '测试菜单_' + Date.now(),
      path: '/test-menu-' + Date.now(),
      icon: 'dashboard',
      sort: 999,
      description: '自动化生成的菜单',
    },

    // ========== 充电管理模块 ==========
    chargingOrder: {
      stationName: '测试充电站A',
      stationId: 'STATION_TEST_001',
      power: 120,  // kW
      duration: 60,  // 分钟
      paymentMethod: 'balance',  // balance, WeChat, Alipay
      price: 150.00,
      remark: '自动化测试充电订单',
    },
    chargingPile: {
      name: '充电桩_' + Date.now(),
      code: 'PILE_' + Date.now().toString().slice(-6),
      model: 'AC-120KW',
      manufacturer: '特来电',
      serialNumber: 'SN' + Date.now().toString().slice(-8),
      location: '停车位A1',
      power: 120,
      voltage: 380,
      amperage: 180,
    },

    // ========== 设备管理模块 ==========
    device: {
      name: '测试设备_' + Date.now(),
      deviceType: 'charger',  // charger, battery, meter, gateway
      manufacturer: '华为',
      model: 'HW-2024-001',
      serialNumber: 'SN' + Date.now().toString().slice(-10),
      location: 'Zone_A_Rack_01',
      description: '自动化生成的测试设备',
      status: 'active',
    },

    // ========== 工单管理模块 ==========
    workOrder: {
      title: '测试工单_' + Date.now(),
      description: '这是一个自动化生成的测试工单',
      priority: 'medium',  // low, medium, high, urgent
      type: 'maintenance',  // maintenance, emergency, inspection
      category: 'device',  // device, station, software
      assignedTo: '张三',
      estimatedHours: 2,
      remark: '自动化测试备注',
    },

    // ========== 站点管理模块 ==========
    station: {
      name: '测试站点_' + Date.now(),
      code: 'STATION_' + Date.now().toString().slice(-5),
      province: '北京',
      city: '朝阳区',
      address: '某某街道1号',
      latitude: '39.9042',
      longitude: '116.4074',
      manager: '李四',
      managerPhone: '18600002222',
      pileCount: 10,
      description: '自动化生成测试站点',
    },

    // ========== 结算管理模块 ==========
    settlement: {
      settlementPeriod: '2026-03',
      chargeAmount: 5000.00,
      discountAmount: 500.00,
      feeAmount: 200.00,
      totalAmount: 4700.00,
      paymentMethod: 'transfer',  // transfer, balance
      remark: '自动化生成结算单据',
    },

    // ========== 规则引擎模块 ==========
    rule: {
      name: '测试规则_' + Date.now(),
      description: '自动化生成的规则',
      triggerType: 'event',  // event, timer, manual
      condition: '${power} > 100',
      action: 'sendNotification',
      enabled: true,
      priority: 10,
    },

    // ========== 告警管理模块 ==========
    alarm: {
      name: '测试告警_' + Date.now(),
      level: 'warning',  // info, warning, critical
      source: 'device_monitor',
      message: '测试告警消息',
      recipients: 'test@example.com',
      enabled: true,
    },

    // ========== 数据分析模块 ==========
    report: {
      name: '测试报告_' + Date.now(),
      reportType: 'daily',  // daily, weekly, monthly
      startDate: '2026-03-01',
      endDate: '2026-03-05',
      metrics: ['revenue', 'usage', 'efficiency'],
      format: 'pdf',  // pdf, excel, html
    },

    // ========== 账户管理模块 ==========
    account: {
      accountName: 'test_account_' + Date.now(),
      accountType: 'personal',  // personal, business
      balance: 10000.00,
      credit: 5000.00,
      status: 'active',
    },

    // ========== 通用字段值 ==========
    generic: {
      status: ['active', 'inactive', 'draft', 'archived'],
      priority: ['low', 'medium', 'high', 'urgent'],
      yesNo: ['yes', 'no', '是', '否'],
    },
  };

  // ========== 工具类 ==========
  const Utils = {
    randomString: (length = 8) => {
      const chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789';
      let result = '';
      for (let i = 0; i < length; i++) {
        result += chars.charAt(Math.floor(Math.random() * chars.length));
      }
      return result;
    },

    randomPhone: () => {
      const prefixes = ['138', '139', '187', '188', '198'];
      const prefix = prefixes[Math.floor(Math.random() * prefixes.length)];
      const suffix = Math.floor(Math.random() * 100000000).toString().padStart(8, '0');
      return prefix + suffix;
    },

    randomEmail: () => {
      return `test${Date.now()}${Math.floor(Math.random() * 10000)}@example.com`;
    },

    randomNumber: (min = 0, max = 100) => {
      return Math.floor(Math.random() * (max - min + 1)) + min;
    },

    randomDate: () => {
      const date = new Date();
      date.setDate(date.getDate() + Math.floor(Math.random() * 30));
      return date.toISOString().split('T')[0];
    },

    findInput: (selectors) => {
      for (const selector of selectors) {
        const element = document.querySelector(selector);
        if (element) return element;
      }
      return null;
    },

    fillInput: (input, value) => {
      if (!input) return false;
      
      const nativeInputValueSetter = Object.getOwnPropertyDescriptor(
        window.HTMLInputElement.prototype, 'value'
      ).set;
      
      if (nativeInputValueSetter) {
        nativeInputValueSetter.call(input, value);
      } else {
        input.value = value;
      }
      
      input.dispatchEvent(new Event('input', { bubbles: true }));
      input.dispatchEvent(new Event('change', { bubbles: true }));
      input.dispatchEvent(new Event('blur', { bubbles: true }));
      
      return true;
    },

    selectOption: (selectElement, value) => {
      if (!selectElement) return false;
      
      const option = Array.from(selectElement.options || []).find(
        opt => opt.value === value || opt.textContent.includes(value)
      );
      
      if (option) {
        selectElement.value = option.value;
        selectElement.dispatchEvent(new Event('change', { bubbles: true }));
        return true;
      }
      return false;
    },

    fillTextarea: (textarea, value) => {
      if (!textarea) return false;
      textarea.value = value;
      textarea.dispatchEvent(new Event('input', { bubbles: true }));
      textarea.dispatchEvent(new Event('change', { bubbles: true }));
      return true;
    },

    clickElement: (selector) => {
      const element = document.querySelector(selector);
      if (element) {
        element.click();
        return true;
      }
      return false;
    },

    showNotification: (title, message, duration = 2000) => {
      const notification = document.createElement('div');
      notification.innerHTML = `
        <div style="
          position: fixed;
          top: 20px;
          right: 20px;
          background: #52c41a;
          color: white;
          padding: 16px 24px;
          border-radius: 4px;
          box-shadow: 0 3px 6px rgba(0,0,0,0.1);
          z-index: 10000;
          font-family: Arial, sans-serif;
          font-size: 14px;
        ">
          <strong>${title}</strong>
          <p>${message}</p>
        </div>
      `;
      document.body.appendChild(notification);
      setTimeout(() => notification.remove(), duration);
    },
  };

  // ========== 页面类型检测 ==========
  const PageDetector = {
    detectPageType: () => {
      const path = window.location.pathname.toLowerCase();
      const href = window.location.href.toLowerCase();

      // 平台管理
      if (path.includes('/admin/user') || path.includes('/user-manage')) return 'user';
      if (path.includes('/admin/tenant') || path.includes('/tenant-manage')) return 'tenant';
      if (path.includes('/admin/role') || path.includes('/role-manage')) return 'role';
      if (path.includes('/admin/permission')) return 'permission';
      if (path.includes('/admin/menu')) return 'menu';

      // 充电管理
      if (path.includes('/charging') && path.includes('order')) return 'chargingOrder';
      if (path.includes('/charging') && path.includes('pile')) return 'chargingPile';

      // 设备管理
      if (path.includes('/device') || path.includes('/device-manage')) return 'device';

      // 工单管理
      if (path.includes('/work-order') || path.includes('/workorder')) return 'workOrder';
      if (path.includes('/task') && path.includes('create')) return 'workOrder';

      // 站点管理
      if (path.includes('/station') || path.includes('/station-manage')) return 'station';

      // 结算管理
      if (path.includes('/settlement') || path.includes('/billing')) return 'settlement';

      // 规则引擎
      if (path.includes('/rule') && !path.includes('alarm')) return 'rule';
      if (path.includes('/alarm')) return 'alarm';

      // 数据分析
      if (path.includes('/report') || path.includes('/analytics')) return 'report';

      // 账户管理
      if (path.includes('/account') || path.includes('/wallet')) return 'account';

      // 通用表单
      return 'generic';
    },
  };

  // ========== 各模块表单填充器 ==========
  const FormFillers = {
    // 用户管理
    fillUserForm: () => {
      const data = CONFIG.user;
      let filled = 0;

      // 用户名
      ['#username', '[name="username"]', '[placeholder*="用户名"]', '[placeholder*="Username"]'].forEach(sel => {
        const input = Utils.findInput([sel]);
        if (input && Utils.fillInput(input, data.username)) filled++;
      });

      // 密码
      ['#password', '[name="password"]', '[type="password"]'].forEach(sel => {
        const input = Utils.findInput([sel]);
        if (input && Utils.fillInput(input, data.password)) filled++;
      });

      // 邮箱
      ['#email', '[name="email"]', '[type="email"]'].forEach(sel => {
        const input = Utils.findInput([sel]);
        if (input && Utils.fillInput(input, Utils.randomEmail())) filled++;
      });

      // 真实姓名
      ['#realName', '[name="realName"]', '[name="realname"]'].forEach(sel => {
        const input = Utils.findInput([sel]);
        if (input && Utils.fillInput(input, data.realName)) filled++;
      });

      // 电话
      ['#phone', '[name="phone"]', '[type="tel"]', '[placeholder*="电话"]'].forEach(sel => {
        const input = Utils.findInput([sel]);
        if (input && Utils.fillInput(input, Utils.randomPhone())) filled++;
      });

      // 角色
      ['#role', '[name="role"]', 'select[name="role"]'].forEach(sel => {
        const select = Utils.findInput([sel]);
        if (select && Utils.selectOption(select, data.role)) filled++;
      });

      // 状态
      ['#status', '[name="status"]', 'select[name="status"]'].forEach(sel => {
        const select = Utils.findInput([sel]);
        if (select && Utils.selectOption(select, 'active')) filled++;
      });

      return filled;
    },

    // 租户管理
    fillTenantForm: () => {
      const data = CONFIG.tenant;
      let filled = 0;

      ['#name', '[name="name"]', '[placeholder*="租户名"]'].forEach(sel => {
        const input = Utils.findInput([sel]);
        if (input && Utils.fillInput(input, data.name)) filled++;
      });

      ['#code', '[name="code"]', '[placeholder*="代码"]'].forEach(sel => {
        const input = Utils.findInput([sel]);
        if (input && Utils.fillInput(input, data.code)) filled++;
      });

      ['#contact', '[name="contact"]', '[placeholder*="联系人"]'].forEach(sel => {
        const input = Utils.findInput([sel]);
        if (input && Utils.fillInput(input, data.contact)) filled++;
      });

      ['#contactPhone', '[name="contactPhone"]', '[placeholder*="联系电话"]'].forEach(sel => {
        const input = Utils.findInput([sel]);
        if (input && Utils.fillInput(input, Utils.randomPhone())) filled++;
      });

      ['#contactEmail', '[name="contactEmail"]', '[type="email"]'].forEach(sel => {
        const input = Utils.findInput([sel]);
        if (input && Utils.fillInput(input, Utils.randomEmail())) filled++;
      });

      ['#address', '[name="address"]', '[placeholder*="地址"]'].forEach(sel => {
        const input = Utils.findInput([sel]);
        if (input && Utils.fillInput(input, data.address)) filled++;
      });

      ['#description', '[name="description"]', 'textarea[name="description"]'].forEach(sel => {
        const textarea = Utils.findInput([sel]);
        if (textarea && Utils.fillTextarea(textarea, data.description)) filled++;
      });

      return filled;
    },

    // 充电订单
    fillChargingOrderForm: () => {
      const data = CONFIG.chargingOrder;
      let filled = 0;

      ['#stationName', '[name="stationName"]', '[placeholder*="站*"]'].forEach(sel => {
        const input = Utils.findInput([sel]);
        if (input && Utils.fillInput(input, data.stationName)) filled++;
      });

      ['#power', '[name="power"]', '[placeholder*="功率"]'].forEach(sel => {
        const input = Utils.findInput([sel]);
        if (input && Utils.fillInput(input, data.power.toString())) filled++;
      });

      ['#duration', '[name="duration"]', '[placeholder*="时长"]'].forEach(sel => {
        const input = Utils.findInput([sel]);
        if (input && Utils.fillInput(input, data.duration.toString())) filled++;
      });

      ['#price', '[name="price"]', '[placeholder*="价格"]'].forEach(sel => {
        const input = Utils.findInput([sel]);
        if (input && Utils.fillInput(input, data.price.toString())) filled++;
      });

      ['#paymentMethod', '[name="paymentMethod"]', 'select[name="paymentMethod"]'].forEach(sel => {
        const select = Utils.findInput([sel]);
        if (select && Utils.selectOption(select, data.paymentMethod)) filled++;
      });

      ['#remark', '[name="remark"]', 'textarea[name="remark"]'].forEach(sel => {
        const textarea = Utils.findInput([sel]);
        if (textarea && Utils.fillTextarea(textarea, data.remark)) filled++;
      });

      return filled;
    },

    // 设备管理
    fillDeviceForm: () => {
      const data = CONFIG.device;
      let filled = 0;

      ['#name', '[name="name"]', '[placeholder*="设备名"]'].forEach(sel => {
        const input = Utils.findInput([sel]);
        if (input && Utils.fillInput(input, data.name)) filled++;
      });

      ['#deviceType', '[name="deviceType"]', 'select[name="deviceType"]'].forEach(sel => {
        const select = Utils.findInput([sel]);
        if (select && Utils.selectOption(select, data.deviceType)) filled++;
      });

      ['#manufacturer', '[name="manufacturer"]', '[placeholder*="制造商"]'].forEach(sel => {
        const input = Utils.findInput([sel]);
        if (input && Utils.fillInput(input, data.manufacturer)) filled++;
      });

      ['#model', '[name="model"]', '[placeholder*="型号"]'].forEach(sel => {
        const input = Utils.findInput([sel]);
        if (input && Utils.fillInput(input, data.model)) filled++;
      });

      ['#serialNumber', '[name="serialNumber"]', '[placeholder*="序列号"]'].forEach(sel => {
        const input = Utils.findInput([sel]);
        if (input && Utils.fillInput(input, data.serialNumber)) filled++;
      });

      ['#location', '[name="location"]', '[placeholder*="位置"]'].forEach(sel => {
        const input = Utils.findInput([sel]);
        if (input && Utils.fillInput(input, data.location)) filled++;
      });

      ['#description', '[name="description"]', 'textarea[name="description"]'].forEach(sel => {
        const textarea = Utils.findInput([sel]);
        if (textarea && Utils.fillTextarea(textarea, data.description)) filled++;
      });

      return filled;
    },

    // 工单管理
    fillWorkOrderForm: () => {
      const data = CONFIG.workOrder;
      let filled = 0;

      ['#title', '[name="title"]', '[placeholder*="标题"]'].forEach(sel => {
        const input = Utils.findInput([sel]);
        if (input && Utils.fillInput(input, data.title)) filled++;
      });

      ['#description', '[name="description"]', 'textarea[name="description"]'].forEach(sel => {
        const textarea = Utils.findInput([sel]);
        if (textarea && Utils.fillTextarea(textarea, data.description)) filled++;
      });

      ['#priority', '[name="priority"]', 'select[name="priority"]'].forEach(sel => {
        const select = Utils.findInput([sel]);
        if (select && Utils.selectOption(select, data.priority)) filled++;
      });

      ['#type', '[name="type"]', 'select[name="type"]'].forEach(sel => {
        const select = Utils.findInput([sel]);
        if (select && Utils.selectOption(select, data.type)) filled++;
      });

      ['#category', '[name="category"]', 'select[name="category"]'].forEach(sel => {
        const select = Utils.findInput([sel]);
        if (select && Utils.selectOption(select, data.category)) filled++;
      });

      return filled;
    },

    // 站点管理
    fillStationForm: () => {
      const data = CONFIG.station;
      let filled = 0;

      ['#name', '[name="name"]', '[placeholder*="站点名"]'].forEach(sel => {
        const input = Utils.findInput([sel]);
        if (input && Utils.fillInput(input, data.name)) filled++;
      });

      ['#code', '[name="code"]', '[placeholder*="站点代码"]'].forEach(sel => {
        const input = Utils.findInput([sel]);
        if (input && Utils.fillInput(input, data.code)) filled++;
      });

      ['#province', '[name="province"]', 'select[name="province"]'].forEach(sel => {
        const select = Utils.findInput([sel]);
        if (select && Utils.selectOption(select, data.province)) filled++;
      });

      ['#city', '[name="city"]', 'select[name="city"]'].forEach(sel => {
        const select = Utils.findInput([sel]);
        if (select && Utils.selectOption(select, data.city)) filled++;
      });

      ['#address', '[name="address"]', '[placeholder*="address"]'].forEach(sel => {
        const input = Utils.findInput([sel]);
        if (input && Utils.fillInput(input, data.address)) filled++;
      });

      ['#latitude', '[name="latitude"]', '[placeholder*="纬度"]'].forEach(sel => {
        const input = Utils.findInput([sel]);
        if (input && Utils.fillInput(input, data.latitude)) filled++;
      });

      ['#longitude', '[name="longitude"]', '[placeholder*="经度"]'].forEach(sel => {
        const input = Utils.findInput([sel]);
        if (input && Utils.fillInput(input, data.longitude)) filled++;
      });

      return filled;
    },

    // 通用表单（智能识别）
    fillGenericForm: () => {
      let filled = 0;
      const inputs = document.querySelectorAll('input[type="text"], input[type="email"], input[type="number"], textarea, select');

      inputs.forEach(input => {
        const name = (input.name || input.id || input.placeholder || '').toLowerCase();
        const type = input.type;

        // 跳过已有值的输入
        if (input.value) return;

        // 邮箱字段
        if (name.includes('email')) {
          Utils.fillInput(input, Utils.randomEmail());
          filled++;
        }
        // 电话字段
        else if (name.includes('phone') || name.includes('tel')) {
          Utils.fillInput(input, Utils.randomPhone());
          filled++;
        }
        // 密码字段
        else if (name.includes('password') || type === 'password') {
          Utils.fillInput(input, 'Test@123456');
          filled++;
        }
        // 数字字段
        else if (type === 'number') {
          Utils.fillInput(input, Utils.randomNumber(1, 100).toString());
          filled++;
        }
        // 名称字段
        else if (name.includes('name') || name.includes('title')) {
          Utils.fillInput(input, '测试' + Utils.randomString(6));
          filled++;
        }
        // 代码字段
        else if (name.includes('code')) {
          Utils.fillInput(input, 'TEST' + Utils.randomString(4).toUpperCase());
          filled++;
        }
        // 文本字段
        else if (type === 'text' || input.tagName === 'TEXTAREA') {
          Utils.fillInput(input, '自动化测试数据 - ' + Utils.randomString(8));
          filled++;
        }
        // 下拉框
        else if (input.tagName === 'SELECT') {
          const options = input.querySelectorAll('option');
          if (options.length > 1) {
            input.value = options[1].value;
            input.dispatchEvent(new Event('change', { bubbles: true }));
            filled++;
          }
        }
      });

      return filled;
    },

    // 智能填充 - 自动检测页面类型并调用对应填充器
    smartFill: () => {
      const pageType = PageDetector.detectPageType();
      const fillerMap = {
        'user': FormFillers.fillUserForm,
        'tenant': FormFillers.fillTenantForm,
        'chargingOrder': FormFillers.fillChargingOrderForm,
        'device': FormFillers.fillDeviceForm,
        'workOrder': FormFillers.fillWorkOrderForm,
        'station': FormFillers.fillStationForm,
        'generic': FormFillers.fillGenericForm,
      };

      const filler = fillerMap[pageType] || FormFillers.fillGenericForm;
      const count = filler();

      Utils.showNotification(
        '✅ 表单填充完成',
        `已填充 ${count} 个字段（页面类型：${pageType}）`,
        2000
      );

      return count;
    },

    // 清空表单
    clearForm: () => {
      const inputs = document.querySelectorAll('input[type="text"], input[type="email"], input[type="number"], input[type="password"], textarea');
      inputs.forEach(input => {
        input.value = '';
        input.dispatchEvent(new Event('input', { bubbles: true }));
        input.dispatchEvent(new Event('change', { bubbles: true }));
      });

      const selects = document.querySelectorAll('select');
      selects.forEach(select => {
        select.selectedIndex = 0;
        select.dispatchEvent(new Event('change', { bubbles: true }));
      });

      Utils.showNotification('✅ 表单已清空', '所有字段已清除', 2000);
    },

    // 随机填充（每次生成不同的数据）
    randomFill: () => {
      const inputs = document.querySelectorAll('input[type="text"], textarea');
      inputs.forEach(input => {
        const name = (input.name || input.id || '').toLowerCase();
        
        if (name.includes('email')) input.value = Utils.randomEmail();
        else if (name.includes('phone')) input.value = Utils.randomPhone();
        else if (name.includes('name') || name.includes('title')) input.value = '随机' + Utils.randomString(8);
        else input.value = Utils.randomString(10);

        input.dispatchEvent(new Event('input', { bubbles: true }));
        input.dispatchEvent(new Event('change', { bubbles: true }));
      });

      Utils.showNotification('✅ 随机数据已填充', `已填充 ${inputs.length} 个字段`, 2000);
    },
  };

  // ========== UI 浮动按钮 ==========
  const FloatingUI = {
    create: () => {
      const container = document.createElement('div');
      container.id = 'aiops-form-filler-container';
      container.innerHTML = `
        <div style="
          position: fixed;
          bottom: 20px;
          right: 20px;
          display: flex;
          flex-direction: column;
          gap: 8px;
          z-index: 9999;
          font-family: Arial, sans-serif;
        ">
          <button id="btn-smart-fill" style="
            padding: 12px 16px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            font-size: 13px;
            font-weight: bold;
            box-shadow: 0 2px 8px rgba(0,0,0,0.15);
            transition: all 0.3s;
          ">🚀 智能填充</button>
          
          <button id="btn-clear-form" style="
            padding: 12px 16px;
            background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
            color: white;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            font-size: 13px;
            font-weight: bold;
            box-shadow: 0 2px 8px rgba(0,0,0,0.15);
            transition: all 0.3s;
          ">🗑️ 清空表单</button>
          
          <button id="btn-random-fill" style="
            padding: 12px 16px;
            background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
            color: white;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            font-size: 13px;
            font-weight: bold;
            box-shadow: 0 2px 8px rgba(0,0,0,0.15);
            transition: all 0.3s;
          ">🎲 随机数据</button>

          <button id="btn-submit-form" style="
            padding: 12px 16px;
            background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);
            color: white;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            font-size: 13px;
            font-weight: bold;
            box-shadow: 0 2px 8px rgba(0,0,0,0.15);
            transition: all 0.3s;
          ">✔️ 提交表单</button>
        </div>
      `;

      document.body.appendChild(container);

      // 绑定事件
      document.getElementById('btn-smart-fill').addEventListener('click', FormFillers.smartFill);
      document.getElementById('btn-clear-form').addEventListener('click', FormFillers.clearForm);
      document.getElementById('btn-random-fill').addEventListener('click', FormFillers.randomFill);
      document.getElementById('btn-submit-form').addEventListener('click', () => {
        const submitBtn = document.querySelector('button[type="submit"], button:contains("提交"), button:contains("保存")');
        if (submitBtn) submitBtn.click();
        else Utils.showNotification('❌ 未找到提交按钮', '请手动提交表单', 2000);
      });
    },
  };

  // ========== 快捷键绑定 ==========
  const setupHotkeys = () => {
    document.addEventListener('keydown', (e) => {
      if (e.altKey) {
        if (e.key === 'f' || e.key === 'F') {
          e.preventDefault();
          FormFillers.smartFill();
        } else if (e.key === 'c' || e.key === 'C') {
          e.preventDefault();
          FormFillers.clearForm();
        } else if (e.key === 'r' || e.key === 'R') {
          e.preventDefault();
          FormFillers.randomFill();
        } else if (e.key === 's' || e.key === 'S') {
          e.preventDefault();
          const submitBtn = document.querySelector('button[type="submit"]');
          if (submitBtn) submitBtn.click();
        }
      }
    });
  };

  // ========== 右键菜单 ==========
  const setupContextMenu = () => {
    document.addEventListener('contextmenu', (e) => {
      const menu = document.createElement('div');
      menu.style.cssText = `
        position: fixed;
        top: ${e.clientY}px;
        left: ${e.clientX}px;
        background: white;
        border: 1px solid #ccc;
        border-radius: 4px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.15);
        z-index: 10000;
        min-width: 150px;
      `;

      menu.innerHTML = `
        <div style="padding: 8px; cursor: pointer; hover: background: #f0f0f0;" onclick="window.FormFillers?.smartFill()">
          🚀 智能填充
        </div>
        <div style="padding: 8px; cursor: pointer;" onclick="window.FormFillers?.clearForm()">
          🗑️ 清空表单
        </div>
        <div style="padding: 8px; cursor: pointer;" onclick="window.FormFillers?.randomFill()">
          🎲 随机数据
        </div>
      `;

      document.body.appendChild(menu);
      setTimeout(() => menu.remove(), 3000);
    }, { once: true });
  };

  // ========== 初始化 ==========
  window.FormFillers = FormFillers;
  window.Utils = Utils;

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
      FloatingUI.create();
      setupHotkeys();
      setupContextMenu();
    });
  } else {
    FloatingUI.create();
    setupHotkeys();
    setupContextMenu();
  }

  console.log('✅ AIOPS 表单自动填充助手 Pro v2.0 已加载');
  console.log('快捷键: Alt+F(填充) Alt+C(清空) Alt+R(随机) Alt+S(提交)');
})();
