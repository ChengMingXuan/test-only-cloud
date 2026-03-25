// ========================================
// 辅助工具类：半自动测试助手
// ========================================
// 功能：引导用户操作、高亮元素、等待确认、截图、生成报告

import { expect } from '@playwright/test';
import chalk from 'chalk';

export class SemiAutoHelper {
  constructor(page) {
    this.page = page;
    this.baseUrl = process.env.BASE_URL || 'http://localhost:3000';
    this.screenshots = [];
    this.steps = [];
  }

  // ========== 导航和登录 ==========
  
  async navigate(path) {
    await this.page.goto(`${this.baseUrl}${path}`);
    await this.page.waitForLoadState('networkidle');
    this.logStep(`导航到: ${path}`);
  }

  async login(role = 'admin') {
    const credentials = {
      admin: { username: 'admin@aiops.com', password: 'Admin123!' },
      user: { username: 'user@aiops.com', password: 'User123!' },
      viewer: { username: 'viewer@aiops.com', password: 'Viewer123!' }
    };

    const cred = credentials[role];
    
    await this.page.goto(`${this.baseUrl}/login`);
    await this.page.fill('input[name="username"], input[type="email"]', cred.username);
    await this.page.fill('input[name="password"], input[type="password"]', cred.password);
    await this.page.click('button[type="submit"]');
    
    // 等待登录成功
    await this.page.waitForURL(/\/(dashboard|home|admin)/);
    this.logStep(`登录成功: ${role}`);
  }

  // ========== 用户交互提示 ==========
  
  async showPrompt(title, message, duration = 0) {
    // 在页面注入提示框
    await this.page.evaluate(({ title, message }) => {
      // 移除旧的提示框
      const old = document.getElementById('semi-auto-prompt');
      if (old) old.remove();

      // 创建新提示框
      const prompt = document.createElement('div');
      prompt.id = 'semi-auto-prompt';
      prompt.style.cssText = `
        position: fixed;
        top: 20px;
        left: 50%;
        transform: translateX(-50%);
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 20px 30px;
        border-radius: 8px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.3);
        z-index: 999999;
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
        min-width: 400px;
        max-width: 600px;
      `;
      prompt.innerHTML = `
        <div style="font-weight: bold; font-size: 18px; margin-bottom: 8px;">${title}</div>
        <div style="font-size: 14px; line-height: 1.6;">${message}</div>
      `;
      document.body.appendChild(prompt);
    }, { title, message });

    console.log(chalk.cyan(`\n[提示] ${title}`));
    console.log(chalk.white(`${message}\n`));

    if (duration > 0) {
      await this.page.waitForTimeout(duration);
      await this.closePrompt();
    }
  }

  async closePrompt() {
    await this.page.evaluate(() => {
      const prompt = document.getElementById('semi-auto-prompt');
      if (prompt) prompt.remove();
    });
  }

  async waitForUserConfirm(message) {
    console.log(chalk.yellow(`\n[等待确认] ${message}`));
    console.log(chalk.gray('按 Enter 键继续...'));
    
    // 在浏览器显示确认按钮
    await this.page.evaluate(({ message }) => {
      const old = document.getElementById('semi-auto-confirm');
      if (old) old.remove();

      const confirm = document.createElement('div');
      confirm.id = 'semi-auto-confirm';
      confirm.style.cssText = `
        position: fixed;
        bottom: 20px;
        right: 20px;
        background: white;
        border: 2px solid #52c41a;
        padding: 16px 24px;
        border-radius: 6px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.2);
        z-index: 999999;
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
      `;
      confirm.innerHTML = `
        <div style="margin-bottom: 8px; color: #333;">${message}</div>
        <button id="confirm-btn" style="
          background: #52c41a;
          color: white;
          border: none;
          padding: 8px 20px;
          border-radius: 4px;
          cursor: pointer;
          font-size: 14px;
          width: 100%;
        ">确认 (Enter)</button>
      `;
      document.body.appendChild(confirm);

      // 绑定点击事件
      document.getElementById('confirm-btn').onclick = () => {
        window.__semiAutoConfirmed = true;
        confirm.remove();
      };

      // 绑定键盘事件
      window.__semiAutoKeyHandler = (e) => {
        if (e.key === 'Enter') {
          window.__semiAutoConfirmed = true;
          confirm.remove();
          window.removeEventListener('keydown', window.__semiAutoKeyHandler);
        }
      };
      window.addEventListener('keydown', window.__semiAutoKeyHandler);
    }, { message });

    // 等待用户确认
    await this.page.waitForFunction(() => window.__semiAutoConfirmed === true, { timeout: 300000 });
    
    // 重置标志
    await this.page.evaluate(() => {
      window.__semiAutoConfirmed = false;
    });
  }

  async waitForUserAction(timeout = 60000) {
    console.log(chalk.yellow('\n[等待操作] 请完成当前操作，然后按 Enter 继续...'));
    await this.waitForUserConfirm('操作完成后点击确认');
  }

  // ========== 元素高亮 ==========
  
  async highlightElement(selector, duration = 3000) {
    try {
      const element = await this.page.locator(selector).first();
      if (await element.isVisible()) {
        await this.page.evaluate((sel) => {
          const el = document.querySelector(sel);
          if (el) {
            el.style.outline = '3px solid #ff4d4f';
            el.style.outlineOffset = '2px';
            el.style.boxShadow = '0 0 10px rgba(255, 77, 79, 0.5)';
            
            // 滚动到可视区域
            el.scrollIntoView({ behavior: 'smooth', block: 'center' });
          }
        }, selector);
        
        await this.page.waitForTimeout(duration);
        
        // 移除高亮
        await this.page.evaluate((sel) => {
          const el = document.querySelector(sel);
          if (el) {
            el.style.outline = '';
            el.style.outlineOffset = '';
            el.style.boxShadow = '';
          }
        }, selector);
      }
    } catch (e) {
      console.log(chalk.red(`无法高亮元素: ${selector}`));
    }
  }

  // ========== 截图和报告 ==========
  
  async take Screenshot(name) {
    const timestamp = new Date().toISOString().replace(/:/g, '-');
    const filename = `${timestamp}-${name}.png`;
    await this.page.screenshot({ path: `test-results/screenshots/${filename}`, fullPage: true });
    this.screenshots.push({ name, filename, timestamp });
    console.log(chalk.green(`📸 截图已保存: ${filename}`));
  }

  logStep(description) {
    this.steps.push({
      timestamp: new Date().toISOString(),
      description
    });
    console.log(chalk.blue(`✓ ${description}`));
  }

  async generateReport(scenarioName, metadata = {}) {
    const report = {
      scenario: scenarioName,
      timestamp: new Date().toISOString(),
      steps: this.steps,
      screenshots: this.screenshots,
      metadata
    };

    const fs = require('fs');
    const reportPath = `test-results/reports/${scenarioName}-${Date.now()}.json`;
    fs.writeFileSync(reportPath, JSON.stringify(report, null, 2));
    
    console.log(chalk.green(`\n📊 报告已生成: ${reportPath}`));
    console.log(chalk.cyan(`\n场景: ${scenarioName}`));
    console.log(chalk.cyan(`步骤数: ${this.steps.length}`));
    console.log(chalk.cyan(`截图数: ${this.screenshots.length}`));
  }

  // ========== 断言辅助 ==========
  
  async assertVisible(selector, message) {
    try {
      await expect(this.page.locator(selector).first()).toBeVisible({ timeout: 5000 });
      this.logStep(`✅ ${message || '元素可见'}`);
    } catch (e) {
      this.logStep(`❌ ${message || '元素不可见'}`);
      throw e;
    }
  }

  async assertText(selector, text, message) {
    try {
      await expect(this.page.locator(selector).first()).toContainText(text, { timeout: 5000 });
      this.logStep(`✅ ${message || '文本匹配'}`);
    } catch (e) {
      this.logStep(`❌ ${message || '文本不匹配'}`);
      throw e;
    }
  }

  async assertCount(selector, count, message) {
    try {
      await expect(this.page.locator(selector)).toHaveCount(count, { timeout: 5000 });
      this.logStep(`✅ ${message || '数量匹配'}`);
    } catch (e) {
      this.logStep(`❌ ${message || '数量不匹配'}`);
      throw e;
    }
  }

  // ========== API 监控 ==========
  
  async monitorAPI(pattern) {
    const requests = [];
    
    this.page.on('request', request => {
      if (request.url().includes(pattern)) {
        requests.push({
          url: request.url(),
          method: request.method(),
          timestamp: new Date().toISOString()
        });
      }
    });

    this.page.on('response', async response => {
      if (response.url().includes(pattern)) {
        const req = requests.find(r => r.url === response.url());
        if (req) {
          req.status = response.status();
          req.duration = Date.now() - new Date(req.timestamp).getTime();
          
          console.log(chalk.magenta(`[API] ${req.method} ${req.url} - ${req.status} (${req.duration}ms)`));
        }
      }
    });

    return requests;
  }
}
