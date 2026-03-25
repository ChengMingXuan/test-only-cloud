// ==UserScript==
// @name         AIOPS 测试工具栏
// @namespace    http://tampermonkey.net/
// @version      2.0.0
// @description  提供快速切换租户、用户、环境、清理数据等测试功能（悬浮工具栏）
// @author       JGSY Team
// @match        http://localhost:8000/*
// @match        http://localhost:8000/*
// @match        http://localhost:3000/*
// @icon         http://localhost:8000/favicon.ico
// @grant        GM_setValue
// @grant        GM_getValue
// @grant        GM_xmlhttpRequest
// @grant        GM_addStyle
// @grant        GM_registerMenuCommand
// @grant        GM_notification
// @grant        unsafeWindow
// @connect      localhost
// @connect      localhost
// @run-at       document-end
// ==/UserScript==

(function() {
    'use strict';

    // ========== 配置 ==========
    const CONFIG = {
        // API 基础地址
        apiBase: window.location.origin,
        
        // 测试用户
        testUsers: [
            { id: '00000000-0000-0000-0000-000000000001', name: 'SUPER_ADMIN', role: '超级管理员', token: '' },
            { id: '00000000-0000-0000-0000-000000000002', name: 'admin', role: '管理员', token: '' },
            { id: '10000000-0000-0000-0000-000000000001', name: 'test_user_1', role: '普通用户', token: '' },
            { id: '10000000-0000-0000-0000-000000000002', name: 'test_user_2', role: '测试用户', token: '' },
        ],
        
        // 测试租户
        testTenants: [
            { id: '00000000-0000-0000-0000-000000000001', name: 'JGSY集团', code: 'JGSY' },
            { id: '10000000-0000-0000-0000-000000000001', name: '测试租户1', code: 'TEST01' },
            { id: '10000000-0000-0000-0000-000000000002', name: '测试租户2', code: 'TEST02' },
        ],
        
        // 工具栏位置
        position: 'top-right', // top-right, top-left, bottom-right, bottom-left
        
        // 功能开关
        features: {
            switchUser: true,
            switchTenant: true,
            clearCache: true,
            mockData: true,
            apiMonitor: true,
            performanceMonitor: true,
            errorLog: true,
        }
    };

    // ========== 样式 ==========
    GM_addStyle(`
        #aiops-test-toolbar {
            position: fixed;
            top: 60px;
            right: 20px;
            width: 320px;
            background: white;
            border-radius: 8px;
            box-shadow: 0 4px 16px rgba(0,0,0,0.15);
            z-index: 10000;
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            overflow: hidden;
            transition: all 0.3s ease;
        }
        
        #aiops-test-toolbar.minimized {
            width: 48px;
            height: 48px;
        }
        
        #aiops-test-toolbar.minimized .toolbar-body {
            display: none !important;
        }
        
        .toolbar-header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 12px 16px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            cursor: move;
            user-select: none;
        }
        
        .toolbar-title {
            font-weight: 600;
            font-size: 14px;
            display: flex;
            align-items: center;
            gap: 8px;
        }
        
        .toolbar-actions {
            display: flex;
            gap: 8px;
        }
        
        .toolbar-btn-icon {
            background: rgba(255, 255, 255, 0.2);
            border: none;
            color: white;
            width: 24px;
            height: 24px;
            border-radius: 4px;
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
            transition: all 0.2s;
        }
        
        .toolbar-btn-icon:hover {
            background: rgba(255, 255, 255, 0.3);
        }
        
        .toolbar-body {
            max-height: 600px;
            overflow-y: auto;
            padding: 0;
        }
        
        .toolbar-section {
            border-bottom: 1px solid #f0f0f0;
            padding: 12px 16px;
        }
        
        .toolbar-section:last-child {
            border-bottom: none;
        }
        
        .section-title {
            font-size: 12px;
            color: #888;
            margin-bottom: 8px;
            font-weight: 500;
            text-transform: uppercase;
        }
        
        .section-content {
            display: flex;
            flex-direction: column;
            gap: 8px;
        }
        
        .toolbar-btn {
            padding: 8px 12px;
            background: #f5f5f5;
            border: 1px solid #e0e0e0;
            border-radius: 4px;
            cursor: pointer;
            font-size: 13px;
            transition: all 0.2s;
            display: flex;
            align-items: center;
            justify-content: space-between;
            text-align: left;
        }
        
        .toolbar-btn:hover {
            background: #e8e8e8;
            border-color: #d0d0d0;
        }
        
        .toolbar-btn.active {
            background: #e6f7ff;
            border-color: #91d5ff;
            color: #1890ff;
        }
        
        .toolbar-select {
            width: 100%;
            padding: 8px 12px;
            border: 1px solid #e0e0e0;
            border-radius: 4px;
            font-size: 13px;
            background: white;
            cursor: pointer;
        }
        
        .toolbar-input {
            width: 100%;
            padding: 8px 12px;
            border: 1px solid #e0e0e0;
            border-radius: 4px;
            font-size: 13px;
            box-sizing: border-box;
        }
        
        .status-badge {
            display: inline-block;
            padding: 2px 8px;
            border-radius: 10px;
            font-size: 11px;
            font-weight: 500;
        }
        
        .status-badge.success {
            background: #f6ffed;
            color: #52c41a;
            border: 1px solid #b7eb8f;
        }
        
        .status-badge.warning {
            background: #fffbe6;
            color: #faad14;
            border: 1px solid #ffe58f;
        }
        
        .status-badge.error {
            background: #fff1f0;
            color: #ff4d4f;
            border: 1px solid #ffccc7;
        }
        
        .info-row {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 4px 0;
            font-size: 12px;
        }
        
        .info-label {
            color: #888;
        }
        
        .info-value {
            font-weight: 500;
            color: #333;
        }
        
        .toolbar-grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 8px;
        }
        
        .toolbar-toast {
            position: fixed;
            top: 20px;
            left: 50%;
            transform: translateX(-50%);
            padding: 12px 24px;
            background: rgba(0, 0, 0, 0.8);
            color: white;
            border-radius: 4px;
            z-index: 10001;
            font-size: 14px;
            animation: fadeInOut 3s ease-in-out;
        }
        
        @keyframes fadeInOut {
            0%, 100% { opacity: 0; }
            10%, 90% { opacity: 1; }
        }
    `);

    // ========== 工具类 ==========
    const Utils = {
        // 显示 Toast
        showToast(message, duration = 2000) {
            const toast = document.createElement('div');
            toast.className = 'toolbar-toast';
            toast.textContent = message;
            document.body.appendChild(toast);
            
            setTimeout(() => toast.remove(), duration);
        },

        // API 请求
        async apiRequest(endpoint, options = {}) {
            return new Promise((resolve, reject) => {
                const token = localStorage.getItem('token') || '';
                
                GM_xmlhttpRequest({
                    method: options.method || 'GET',
                    url: `${CONFIG.apiBase}${endpoint}`,
                    headers: {
                        'Content-Type': 'application/json',
                        'Authorization': `Bearer ${token}`,
                        ...options.headers,
                    },
                    data: options.body ? JSON.stringify(options.body) : undefined,
                    onload: (response) => {
                        try {
                            const data = JSON.parse(response.responseText);
                            resolve(data);
                        } catch (e) {
                            resolve(response.responseText);
                        }
                    },
                    onerror: reject,
                });
            });
        },

        // 获取当前用户信息
        getCurrentUser() {
            try {
                const userStr = localStorage.getItem('user') || sessionStorage.getItem('user');
                return userStr ? JSON.parse(userStr) : null;
            } catch {
                return null;
            }
        },

        // 获取当前租户信息
        getCurrentTenant() {
            try {
                const tenantStr = localStorage.getItem('tenant') || sessionStorage.getItem('tenant');
                return tenantStr ? JSON.parse(tenantStr) : null;
            } catch {
                return { id: '未知', name: '未知租户' };
            }
        },

        // 清理缓存
        clearCache() {
            // 清理 localStorage（保留 token）
            const token = localStorage.getItem('token');
            localStorage.clear();
            if (token) localStorage.setItem('token', token);
            
            // 清理 sessionStorage
            sessionStorage.clear();
            
            // 清理 IndexedDB
            if (window.indexedDB) {
                indexedDB.databases().then(dbs => {
                    dbs.forEach(db => indexedDB.deleteDatabase(db.name));
                });
            }
            
            this.showToast('✅ 缓存已清理');
        },

        // 监控性能
        getPerformanceMetrics() {
            if (!window.performance) return null;
            
            const perf = performance.getEntriesByType('navigation')[0];
            if (!perf) return null;
            
            return {
                dns: Math.round(perf.domainLookupEnd - perf.domainLookupStart),
                tcp: Math.round(perf.connectEnd - perf.connectStart),
                request: Math.round(perf.responseStart - perf.requestStart),
                response: Math.round(perf.responseEnd - perf.responseStart),
                dom: Math.round(perf.domContentLoadedEventEnd - perf.domContentLoadedEventStart),
                load: Math.round(perf.loadEventEnd - perf.loadEventStart),
                total: Math.round(perf.loadEventEnd - perf.fetchStart),
            };
        },

        // 导出日志
        exportLogs() {
            const logs = {
                timestamp: new Date().toISOString(),
                url: window.location.href,
                user: this.getCurrentUser(),
                tenant: this.getCurrentTenant(),
                performance: this.getPerformanceMetrics(),
                localStorage: { ...localStorage },
                sessionStorage: { ...sessionStorage },
                console: window.console.memory,
            };
            
            const blob = new Blob([JSON.stringify(logs, null, 2)], { type: 'application/json' });
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `aiops-test-logs-${Date.now()}.json`;
            a.click();
            URL.revokeObjectURL(url);
            
            this.showToast('✅ 日志已导出');
        }
    };

    // ========== 工具栏管理器 ==========
    const ToolbarManager = {
        toolbar: null,
        isDragging: false,
        dragOffset: { x: 0, y: 0 },

        // 创建工具栏
        create() {
            const toolbar = document.createElement('div');
            toolbar.id = 'aiops-test-toolbar';
            toolbar.innerHTML = this.getHTML();
            document.body.appendChild(toolbar);
            
            this.toolbar = toolbar;
            this.bindEvents();
            this.updateStatus();
            
            // 定期更新状态
            setInterval(() => this.updateStatus(), 3000);
        },

        // 获取 HTML
        getHTML() {
            const user = Utils.getCurrentUser();
            const tenant = Utils.getCurrentTenant();
            
            return `
                <div class="toolbar-header">
                    <div class="toolbar-title">
                        🧪 测试工具栏
                    </div>
                    <div class="toolbar-actions">
                        <button class="toolbar-btn-icon" id="btn-minimize" title="最小化">─</button>
                        <button class="toolbar-btn-icon" id="btn-close" title="关闭">✕</button>
                    </div>
                </div>
                <div class="toolbar-body">
                    <!-- 当前状态 -->
                    <div class="toolbar-section">
                        <div class="section-title">📊 当前状态</div>
                        <div class="section-content">
                            <div class="info-row">
                                <span class="info-label">用户:</span>
                                <span class="info-value" id="current-user">${user?.name || '未登录'}</span>
                            </div>
                            <div class="info-row">
                                <span class="info-label">租户:</span>
                                <span class="info-value" id="current-tenant">${tenant?.name || '未知'}</span>
                            </div>
                            <div class="info-row">
                                <span class="info-label">环境:</span>
                                <span class="status-badge success" id="env-badge">生产环境</span>
                            </div>
                        </div>
                    </div>
                    
                    <!-- 快速切换 -->
                    <div class="toolbar-section">
                        <div class="section-title">🔄 快速切换</div>
                        <div class="section-content">
                            <select class="toolbar-select" id="select-user">
                                <option value="">切换用户...</option>
                                ${CONFIG.testUsers.map(u => `<option value="${u.id}">${u.name} (${u.role})</option>`).join('')}
                            </select>
                            <select class="toolbar-select" id="select-tenant">
                                <option value="">切换租户...</option>
                                ${CONFIG.testTenants.map(t => `<option value="${t.id}">${t.name}</option>`).join('')}
                            </select>
                        </div>
                    </div>
                    
                    <!-- 数据操作 -->
                    <div class="toolbar-section">
                        <div class="section-title">💾 数据操作</div>
                        <div class="section-content toolbar-grid">
                            <button class="toolbar-btn" id="btn-clear-cache">🗑️ 清理缓存</button>
                            <button class="toolbar-btn" id="btn-mock-data">🎲 模拟数据</button>
                            <button class="toolbar-btn" id="btn-export-logs">📤 导出日志</button>
                            <button class="toolbar-btn" id="btn-screenshot">📸 截图</button>
                        </div>
                    </div>
                    
                    <!-- 监控工具 -->
                    <div class="toolbar-section">
                        <div class="section-title">📈 监控工具</div>
                        <div class="section-content">
                            <button class="toolbar-btn" id="btn-api-monitor">
                                <span>API 监控</span>
                                <span class="status-badge" id="api-count">0 请求</span>
                            </button>
                            <button class="toolbar-btn" id="btn-perf-monitor">
                                <span>性能监控</span>
                                <span class="status-badge" id="perf-time">-- ms</span>
                            </button>
                            <button class="toolbar-btn" id="btn-error-log">
                                <span>错误日志</span>
                                <span class="status-badge error" id="error-count">0 错误</span>
                            </button>
                        </div>
                    </div>
                    
                    <!-- 快速操作 -->
                    <div class="toolbar-section">
                        <div class="section-title">⚡ 快速操作</div>
                        <div class="section-content toolbar-grid">
                            <button class="toolbar-btn" id="btn-reload">🔄 刷新页面</button>
                            <button class="toolbar-btn" id="btn-logout">🚪 退出登录</button>
                            <button class="toolbar-btn" id="btn-console">💻 控制台</button>
                            <button class="toolbar-btn" id="btn-help">❓ 帮助</button>
                        </div>
                    </div>
                </div>
            `;
        },

        // 绑定事件
        bindEvents() {
            // 最小化
            this.toolbar.querySelector('#btn-minimize').onclick = () => {
                this.toolbar.classList.toggle('minimized');
            };
            
            // 关闭
            this.toolbar.querySelector('#btn-close').onclick = () => {
                this.toolbar.style.display = 'none';
            };
            
            // 拖拽
            const header = this.toolbar.querySelector('.toolbar-header');
            header.onmousedown = (e) => this.startDrag(e);
            
            // 切换用户
            this.toolbar.querySelector('#select-user').onchange = (e) => {
                this.switchUser(e.target.value);
                e.target.value = '';
            };
            
            // 切换租户
            this.toolbar.querySelector('#select-tenant').onchange = (e) => {
                this.switchTenant(e.target.value);
                e.target.value = '';
            };
            
            // 清理缓存
            this.toolbar.querySelector('#btn-clear-cache').onclick = () => Utils.clearCache();
            
            // 导出日志
            this.toolbar.querySelector('#btn-export-logs').onclick = () => Utils.exportLogs();
            
            // 刷新页面
            this.toolbar.querySelector('#btn-reload').onclick = () => location.reload();
            
            // 退出登录
            this.toolbar.querySelector('#btn-logout').onclick = () => {
                localStorage.removeItem('token');
                localStorage.removeItem('user');
                Utils.showToast('✅ 已退出登录');
                setTimeout(() => location.reload(), 1000);
            };
            
            // 控制台
            this.toolbar.querySelector('#btn-console').onclick = () => {
                console.log('=== AIOPS 调试信息 ===');
                console.log('用户:', Utils.getCurrentUser());
                console.log('租户:', Utils.getCurrentTenant());
                console.log('性能:', Utils.getPerformanceMetrics());
                console.log('localStorage:', localStorage);
                Utils.showToast('✅ 已输出到控制台');
            };
            
            // 帮助
            this.toolbar.querySelector('#btn-help').onclick = () => {
                alert(`AIOPS 测试工具栏 v2.0\n\n功能:\n- 快速切换用户/租户\n- 清理缓存\n- 导出测试日志\n- 性能监控\n- API 监控\n\n快捷键:\nAlt+T: 显示/隐藏工具栏`);
            };
        },

        // 开始拖拽
        startDrag(e) {
            this.isDragging = true;
            this.dragOffset = {
                x: e.clientX - this.toolbar.offsetLeft,
                y: e.clientY - this.toolbar.offsetTop,
            };
            
            document.onmousemove = (e) => this.onDrag(e);
            document.onmouseup = () => this.stopDrag();
        },

        // 拖拽中
        onDrag(e) {
            if (!this.isDragging) return;
            
            this.toolbar.style.left = (e.clientX - this.dragOffset.x) + 'px';
            this.toolbar.style.top = (e.clientY - this.dragOffset.y) + 'px';
            this.toolbar.style.right = 'auto';
        },

        // 停止拖拽
        stopDrag() {
            this.isDragging = false;
            document.onmousemove = null;
            document.onmouseup = null;
        },

        // 切换用户
        switchUser(userId) {
            const user = CONFIG.testUsers.find(u => u.id === userId);
            if (!user) return;
            
            // 模拟切换用户（实际项目需调用登录API）
            localStorage.setItem('user', JSON.stringify({ id: userId, name: user.name, role: user.role }));
            Utils.showToast(`✅ 已切换到用户: ${user.name}`);
            
            setTimeout(() => location.reload(), 1000);
        },

        // 切换租户
        switchTenant(tenantId) {
            const tenant = CONFIG.testTenants.find(t => t.id === tenantId);
            if (!tenant) return;
            
            localStorage.setItem('tenant', JSON.stringify({ id: tenantId, name: tenant.name }));
            Utils.showToast(`✅ 已切换到租户: ${tenant.name}`);
            
            setTimeout(() => location.reload(), 1000);
        },

        // 更新状态
        updateStatus() {
            if (!this.toolbar) return;
            
            const user = Utils.getCurrentUser();
            const tenant = Utils.getCurrentTenant();
            const perf = Utils.getPerformanceMetrics();
            
            // 更新当前用户
            const userEl = this.toolbar.querySelector('#current-user');
            if (userEl) userEl.textContent = user?.name || '未登录';
            
            // 更新当前租户
            const tenantEl = this.toolbar.querySelector('#current-tenant');
            if (tenantEl) tenantEl.textContent = tenant?.name || '未知';
            
            // 更新性能
            const perfEl = this.toolbar.querySelector('#perf-time');
            if (perfEl && perf) {
                perfEl.textContent = `${perf.total} ms`;
                perfEl.className = 'status-badge ' + (perf.total < 1000 ? 'success' : perf.total < 3000 ? 'warning' : 'error');
            }
        }
    };

    // ========== 快捷键 ==========
    document.addEventListener('keydown', (e) => {
        if (e.altKey && e.key === 't') {
            e.preventDefault();
            const toolbar = document.getElementById('aiops-test-toolbar');
            if (toolbar) {
                toolbar.style.display = toolbar.style.display === 'none' ? 'block' : 'none';
            }
        }
    });

    // ========== 初始化 ==========
    function init() {
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', init);
            return;
        }

        setTimeout(() => {
            ToolbarManager.create();
            console.log('✅ AIOPS 测试工具栏已启动 (Alt+T 显示/隐藏)');
        }, 1000);
    }

    init();

})();
