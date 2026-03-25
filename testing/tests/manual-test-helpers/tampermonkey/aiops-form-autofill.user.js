// ==UserScript==
// @name         AIOPS 表单自动填充助手
// @namespace    http://tampermonkey.net/
// @version      1.0.0
// @description  自动填充 AIOPS 平台表单，提高人工测试效率（支持充电订单、工单、设备、租户等模块）
// @author       JGSY Team
// @match        http://localhost:8000/*
// @match        http://localhost:8000/*
// @icon         http://localhost:8000/favicon.ico
// @grant        GM_setValue
// @grant        GM_getValue
// @grant        GM_registerMenuCommand
// @grant        GM_notification
// @run-at       document-end
// ==/UserScript==

(function() {
    'use strict';

    // ========== 配置 ==========
    const CONFIG = {
        // 测试数据模板
        testData: {
            // 用户信息
            user: {
                username: 'test_user_' + Date.now(),
                password: 'Test@123456',
                email: 'test@jgsy.com',
                phone: '13800138000',
                realName: '测试用户',
            },
            // 充电订单
            chargingOrder: {
                stationName: '测试充电站',
                powerKwh: '50',
                duration: '120',
                paymentMethod: 'wechat',
            },
            // 工单
            workOrder: {
                title: '测试工单_' + new Date().toLocaleString('zh-CN'),
                description: '这是一个自动生成的测试工单',
                priority: 'high',
                category: 'maintenance',
            },
            // 设备
            device: {
                deviceName: '测试设备_' + Date.now(),
                deviceType: 'charging_pile',
                model: 'DC-Fast-120kW',
                manufacturer: '测试厂商',
                serialNumber: 'SN' + Date.now(),
            },
            // 租户
            tenant: {
                tenantName: '测试租户_' + Date.now(),
                contactPerson: '张三',
                contactPhone: '13900139000',
                address: '北京市朝阳区测试路123号',
            },
        },
        // 快捷键
        hotkeys: {
            fillForm: 'Alt+F',          // 填充表单
            clearForm: 'Alt+C',         // 清空表单
            submitForm: 'Alt+S',        // 提交表单
            randomData: 'Alt+R',        // 随机数据
        },
        // UI配置
        ui: {
            buttonPosition: 'bottom-right',
            showNotification: true,
        }
    };

    // ========== 工具函数 ==========
    const Utils = {
        // 生成随机字符串
        randomString(length = 8) {
            const chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789';
            let result = '';
            for (let i = 0; i < length; i++) {
                result += chars.charAt(Math.floor(Math.random() * chars.length));
            }
            return result;
        },

        // 生成随机手机号
        randomPhone() {
            const prefixes = ['130', '131', '132', '133', '134', '135', '136', '137', '138', '139'];
            const prefix = prefixes[Math.floor(Math.random() * prefixes.length)];
            const suffix = Math.floor(Math.random() * 100000000).toString().padStart(8, '0');
            return prefix + suffix;
        },

        // 生成随机邮箱
        randomEmail() {
            return `test_${this.randomString(6)}@jgsy.com`;
        },

        // 查找输入框（支持多种选择器）
        findInput(selectors) {
            for (const selector of selectors) {
                const input = document.querySelector(selector);
                if (input) return input;
            }
            return null;
        },

        // 填充输入框
        fillInput(input, value) {
            if (!input) return false;
            
            // 触发 React 事件
            const nativeInputValueSetter = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, 'value').set;
            nativeInputValueSetter.call(input, value);
            
            const event = new Event('input', { bubbles: true });
            input.dispatchEvent(event);
            input.dispatchEvent(new Event('change', { bubbles: true }));
            input.dispatchEvent(new Event('blur', { bubbles: true }));
            
            return true;
        },

        // 选择下拉框
        selectDropdown(select, value) {
            if (!select) return false;
            
            select.value = value;
            select.dispatchEvent(new Event('change', { bubbles: true }));
            
            return true;
        },

        // 显示通知
        showNotification(message, type = 'success') {
            if (!CONFIG.ui.showNotification) return;
            
            GM_notification({
                text: message,
                title: 'AIOPS 自动填充助手',
                timeout: 2000,
            });
            
            // 同时在页面显示 Toast
            this.showToast(message, type);
        },

        // 显示 Toast
        showToast(message, type = 'success') {
            const toast = document.createElement('div');
            toast.style.cssText = `
                position: fixed;
                top: 20px;
                right: 20px;
                padding: 12px 24px;
                background: ${type === 'success' ? '#52c41a' : '#ff4d4f'};
                color: white;
                border-radius: 4px;
                box-shadow: 0 2px 8px rgba(0,0,0,0.15);
                z-index: 10000;
                font-size: 14px;
                animation: slideIn 0.3s ease-out;
            `;
            toast.textContent = message;
            document.body.appendChild(toast);
            
            setTimeout(() => {
                toast.style.animation = 'slideOut 0.3s ease-in';
                setTimeout(() => toast.remove(), 300);
            }, 2000);
        }
    };

    // ========== 表单填充器 ==========
    const FormFillers = {
        // 检测当前页面类型
        detectPageType() {
            const path = window.location.pathname;
            const url = window.location.href;
            
            if (path.includes('/charging') || url.includes('charging')) return 'charging';
            if (path.includes('/workorder') || url.includes('workorder')) return 'workorder';
            if (path.includes('/device') || url.includes('device')) return 'device';
            if (path.includes('/tenant') || url.includes('tenant')) return 'tenant';
            if (path.includes('/user') || url.includes('user')) return 'user';
            if (path.includes('/station') || url.includes('station')) return 'station';
            
            return 'unknown';
        },

        // 填充充电订单表单
        fillChargingForm() {
            const data = CONFIG.testData.chargingOrder;
            let filled = 0;

            // 充电站名称
            const stationInput = Utils.findInput([
                'input[name="stationName"]',
                'input[placeholder*="充电站"]',
                '#stationName',
            ]);
            if (Utils.fillInput(stationInput, data.stationName)) filled++;

            // 充电功率
            const powerInput = Utils.findInput([
                'input[name="powerKwh"]',
                'input[placeholder*="功率"]',
                '#powerKwh',
            ]);
            if (Utils.fillInput(powerInput, data.powerKwh)) filled++;

            // 充电时长
            const durationInput = Utils.findInput([
                'input[name="duration"]',
                'input[placeholder*="时长"]',
                '#duration',
            ]);
            if (Utils.fillInput(durationInput, data.duration)) filled++;

            // 支付方式
            const paymentSelect = Utils.findInput([
                'select[name="paymentMethod"]',
                '#paymentMethod',
            ]);
            if (Utils.selectDropdown(paymentSelect, data.paymentMethod)) filled++;

            return filled;
        },

        // 填充工单表单
        fillWorkOrderForm() {
            const data = CONFIG.testData.workOrder;
            let filled = 0;

            // 工单标题
            const titleInput = Utils.findInput([
                'input[name="title"]',
                'input[placeholder*="标题"]',
                '#title',
            ]);
            if (Utils.fillInput(titleInput, data.title)) filled++;

            // 工单描述
            const descInput = Utils.findInput([
                'textarea[name="description"]',
                'textarea[placeholder*="描述"]',
                '#description',
            ]);
            if (Utils.fillInput(descInput, data.description)) filled++;

            // 优先级
            const prioritySelect = Utils.findInput([
                'select[name="priority"]',
                '#priority',
            ]);
            if (Utils.selectDropdown(prioritySelect, data.priority)) filled++;

            // 类别
            const categorySelect = Utils.findInput([
                'select[name="category"]',
                '#category',
            ]);
            if (Utils.selectDropdown(categorySelect, data.category)) filled++;

            return filled;
        },

        // 填充设备表单
        fillDeviceForm() {
            const data = CONFIG.testData.device;
            let filled = 0;

            const fields = [
                { selectors: ['input[name="deviceName"]', '#deviceName'], value: data.deviceName },
                { selectors: ['select[name="deviceType"]', '#deviceType'], value: data.deviceType, isSelect: true },
                { selectors: ['input[name="model"]', '#model'], value: data.model },
                { selectors: ['input[name="manufacturer"]', '#manufacturer'], value: data.manufacturer },
                { selectors: ['input[name="serialNumber"]', '#serialNumber'], value: data.serialNumber },
            ];

            fields.forEach(field => {
                const input = Utils.findInput(field.selectors);
                if (field.isSelect) {
                    if (Utils.selectDropdown(input, field.value)) filled++;
                } else {
                    if (Utils.fillInput(input, field.value)) filled++;
                }
            });

            return filled;
        },

        // 填充租户表单
        fillTenantForm() {
            const data = CONFIG.testData.tenant;
            let filled = 0;

            const fields = [
                { selectors: ['input[name="tenantName"]', '#tenantName'], value: data.tenantName },
                { selectors: ['input[name="contactPerson"]', '#contactPerson'], value: data.contactPerson },
                { selectors: ['input[name="contactPhone"]', '#contactPhone'], value: data.contactPhone },
                { selectors: ['input[name="address"]', 'textarea[name="address"]', '#address'], value: data.address },
            ];

            fields.forEach(field => {
                const input = Utils.findInput(field.selectors);
                if (Utils.fillInput(input, field.value)) filled++;
            });

            return filled;
        },

        // 填充用户表单
        fillUserForm() {
            const data = CONFIG.testData.user;
            let filled = 0;

            const fields = [
                { selectors: ['input[name="username"]', '#username'], value: data.username },
                { selectors: ['input[name="password"]', '#password'], value: data.password },
                { selectors: ['input[name="email"]', '#email'], value: data.email },
                { selectors: ['input[name="phone"]', '#phone'], value: data.phone },
                { selectors: ['input[name="realName"]', '#realName'], value: data.realName },
            ];

            fields.forEach(field => {
                const input = Utils.findInput(field.selectors);
                if (Utils.fillInput(input, field.value)) filled++;
            });

            return filled;
        },

        // 智能填充（根据页面类型自动选择）
        smartFill() {
            const pageType = this.detectPageType();
            let filled = 0;

            switch (pageType) {
                case 'charging':
                    filled = this.fillChargingForm();
                    break;
                case 'workorder':
                    filled = this.fillWorkOrderForm();
                    break;
                case 'device':
                    filled = this.fillDeviceForm();
                    break;
                case 'tenant':
                    filled = this.fillTenantForm();
                    break;
                case 'user':
                    filled = this.fillUserForm();
                    break;
                default:
                    // 尝试通用填充
                    filled = this.fillGenericForm();
            }

            if (filled > 0) {
                Utils.showNotification(`已填充 ${filled} 个字段`, 'success');
            } else {
                Utils.showNotification('未找到可填充的表单字段', 'error');
            }
        },

        // 通用表单填充（智能识别）
        fillGenericForm() {
            let filled = 0;
            const inputs = document.querySelectorAll('input[type="text"], input[type="email"], input[type="tel"], input[type="number"], textarea');
            
            inputs.forEach(input => {
                if (input.value) return; // 跳过已填充的字段
                
                const name = input.name?.toLowerCase() || '';
                const placeholder = input.placeholder?.toLowerCase() || '';
                const id = input.id?.toLowerCase() || '';
                
                let value = '';
                
                if (name.includes('name') || placeholder.includes('名称') || id.includes('name')) {
                    value = '测试数据_' + Utils.randomString(6);
                } else if (name.includes('phone') || placeholder.includes('手机') || id.includes('phone')) {
                    value = Utils.randomPhone();
                } else if (name.includes('email') || placeholder.includes('邮箱') || id.includes('email')) {
                    value = Utils.randomEmail();
                } else if (input.type === 'number') {
                    value = Math.floor(Math.random() * 100).toString();
                } else if (input.tagName === 'TEXTAREA') {
                    value = '这是自动生成的测试描述内容。';
                } else {
                    value = '测试_' + Utils.randomString(4);
                }
                
                if (Utils.fillInput(input, value)) filled++;
            });

            return filled;
        },

        // 清空表单
        clearForm() {
            const inputs = document.querySelectorAll('input, textarea, select');
            let cleared = 0;

            inputs.forEach(input => {
                if (input.type === 'submit' || input.type === 'button') return;
                
                if (Utils.fillInput(input, '')) cleared++;
            });

            if (cleared > 0) {
                Utils.showNotification(`已清空 ${cleared} 个字段`, 'success');
            }
        }
    };

    // ========== 创建浮动按钮 ==========
    function createFloatingButton() {
        const container = document.createElement('div');
        container.id = 'aiops-autofill-container';
        container.style.cssText = `
            position: fixed;
            bottom: 20px;
            right: 20px;
            z-index: 9999;
            display: flex;
            flex-direction: column;
            gap: 10px;
        `;

        const buttons = [
            { text: '🚀 智能填充 (Alt+F)', action: () => FormFillers.smartFill(), color: '#1890ff' },
            { text: '🗑️ 清空表单 (Alt+C)', action: () => FormFillers.clearForm(), color: '#ff4d4f' },
            { text: '🎲 随机数据 (Alt+R)', action: () => FormFillers.smartFill(), color: '#52c41a' },
        ];

        buttons.forEach(btn => {
            const button = document.createElement('button');
            button.textContent = btn.text;
            button.style.cssText = `
                padding: 10px 16px;
                background: ${btn.color};
                color: white;
                border: none;
                border-radius: 4px;
                cursor: pointer;
                font-size: 14px;
                box-shadow: 0 2px 8px rgba(0,0,0,0.15);
                transition: all 0.3s;
                white-space: nowrap;
            `;
            button.onmouseover = () => button.style.transform = 'scale(1.05)';
            button.onmouseout = () => button.style.transform = 'scale(1)';
            button.onclick = btn.action;
            container.appendChild(button);
        });

        document.body.appendChild(container);
    }

    // ========== 快捷键监听 ==========
    function setupHotkeys() {
        document.addEventListener('keydown', (e) => {
            if (e.altKey && e.key === 'f') {
                e.preventDefault();
                FormFillers.smartFill();
            } else if (e.altKey && e.key === 'c') {
                e.preventDefault();
                FormFillers.clearForm();
            } else if (e.altKey && e.key === 'r') {
                e.preventDefault();
                FormFillers.smartFill();
            } else if (e.altKey && e.key === 's') {
                e.preventDefault();
                const submitBtn = document.querySelector('button[type="submit"], button.ant-btn-primary');
                if (submitBtn) submitBtn.click();
            }
        });
    }

    // ========== 初始化 ==========
    function init() {
        // 等待页面加载完成
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', init);
            return;
        }

        // 创建浮动按钮
        setTimeout(createFloatingButton, 1000);

        // 设置快捷键
        setupHotkeys();

        // 注册右键菜单命令
        GM_registerMenuCommand('🚀 智能填充表单', () => FormFillers.smartFill());
        GM_registerMenuCommand('🗑️ 清空表单', () => FormFillers.clearForm());

        console.log('✅ AIOPS 表单自动填充助手已启动');
    }

    // 启动
    init();

})();
