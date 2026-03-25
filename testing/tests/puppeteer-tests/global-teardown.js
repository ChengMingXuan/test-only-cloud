/**
 * Jest 全局清理 — 停止 Mock 服务器
 */
module.exports = async function globalTeardown() {
  if (globalThis.__PUPPETEER_MOCK_SERVER__) {
    try {
      globalThis.__PUPPETEER_MOCK_SERVER__.stop();
      console.log('🛑 [Puppeteer] mock-server 已停止');
    } catch (err) {
      // 静默忽略关闭错误
    }
  }
};
