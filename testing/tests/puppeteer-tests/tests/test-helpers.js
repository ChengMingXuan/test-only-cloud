/**
 * Puppeteer 测试辅助工具
 * 提供安全导航、环境检测等通用功能
 */

/**
 * 安全导航 — 当前端服务不可达时，返回 fallback 而非抛出异常
 * @param {import('puppeteer').Page} page 
 * @param {string} url 
 * @param {object} options 
 * @returns {Promise<{success: boolean, response: any}>}
 */
async function safeGoto(page, url, options = {}) {
  const defaults = { waitUntil: 'networkidle2', timeout: 30000 };
  const opts = { ...defaults, ...options };

  try {
    const response = await page.goto(url, opts);
    return { success: true, response };
  } catch (err) {
    // 连接被拒绝或超时 → 前端服务未运行
    if (err.message.includes('net::ERR_CONNECTION_REFUSED') ||
        err.message.includes('ERR_CONNECTION_RESET') ||
        err.message.includes('Navigation timeout') ||
        err.message.includes('Target closed')) {
      return { success: false, response: null };
    }
    throw err;
  }
}

/**
 * 检测前端服务是否可达（从全局设置传入的环境变量读取）
 */
function isServiceAvailable() {
  return process.env.PUPPETEER_SERVICE_AVAILABLE === 'true';
}

module.exports = { safeGoto, isServiceAvailable };
