/**
 * Puppeteer 共享测试配置 — 从 _shared/constants.json 读取
 * 
 * Puppeteer 主要做性能基准测试（FCP/LCP/TTI/CLS/TBT），
 * 纯性能测试不需要业务数据；
 * 涉及业务页面性能时仅需登录凭证。
 */
const path = require('path');
const fs = require('fs');

const SHARED_PATH = path.join(__dirname, '..', '..', '_shared', 'constants.json');
const SHARED = JSON.parse(fs.readFileSync(SHARED_PATH, 'utf-8'));

module.exports = {
  // 登录凭证
  ADMIN_USER: {
    username: SHARED.admin.username,
    password: SHARED.admin.password,
  },
  // 网关地址（走前端）
  FRONTEND_URL: SHARED.gateway.frontendUrl,
  // 网关地址（走 API）
  GATEWAY_URL: SHARED.gateway.url,

  // 需测性能的业务页面列表
  BUSINESS_PAGES: [
    { name: '仪表盘', path: '/dashboard' },
    { name: '充电订单', path: '/charging/orders' },
    { name: '设备管理', path: '/device' },
    { name: '场站管理', path: '/station' },
    { name: '工单管理', path: '/workorder' },
  ],
};
