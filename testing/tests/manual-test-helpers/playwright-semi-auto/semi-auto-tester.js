/**
 * Playwright 半自动测试脚本
 * 提供录制、重放、暂停点、人工验证等功能
 * 目的：辅助人工测试，提高效率
 */

import { chromium, firefox, webkit } from '@playwright/test';
import * as fs from 'fs';
import * as path from 'path';
import * as readline from 'readline';

// ========== 配置 ==========
const CONFIG = {
  // 基础URL
  baseURL: process.env.BASE_URL || 'https://aiops.jgsy.com',
  
  // 浏览器选择
  browser: process.env.BROWSER || 'chromium', // chromium, firefox, webkit
  
  // 录制模式
  recordMode: process.env.RECORD_MODE === 'true',
  
  // 慢速模式（方便观察）
  slowMo: parseInt(process.env.SLOW_MO || '500'),
  
  // 是否显示浏览器
  headless: process.env.HEADLESS === 'true',
  
  // 截图目录
  screenshotDir: './manual-test-helpers/playwright-semi-auto/screenshots',
  
  // 录制文件目录
  recordingDir: './manual-test-helpers/playwright-semi-auto/recordings',
  
  // 测试场景配置
  scenarios: {
    // 充电订单场景
    chargingOrder: {
      name: '充电订单完整流程',
      steps: [
        { type: 'navigate', url: '/charging/orders' },
        { type: 'pause', message: '➤ 验证充电订单列表页面是否正常加载' },
        { type: 'click', selector: 'button:has-text("新建订单")', waitAfter: 1000 },
        { type: 'pause', message: '➤ 请人工填充订单表单（可使用油猴脚本）' },
        { type: 'screenshot', name: 'order-form-filled' },
        { type: 'click', selector: 'button[type="submit"]' },
        { type: 'wait', selector: '.ant-message-success', timeout: 5000 },
        { type: 'pause', message: '➤ 验证订单创建成功提示' },
        { type: 'screenshot', name: 'order-created' },
      ]
    },
    
    // 工单场景
    workOrder: {
      name: '工单流程',
      steps: [
        { type: 'navigate', url: '/workorder/list' },
        { type: 'pause', message: '➤ 验证工单列表页面' },
        { type: 'click', selector: 'button:has-text("创建工单")' },
        { type: 'pause', message: '➤ 填充工单信息' },
        { type: 'screenshot', name: 'workorder-form' },
      ]
    },
    
    // 设备管理场景
    deviceManagement: {
      name: '设备管理流程',
      steps: [
        { type: 'navigate', url: '/device/list' },
        { type: 'pause', message: '➤ 验证设备列表' },
        { type: 'click', selector: '.ant-table-row:first-child .action-edit' },
        { type: 'pause', message: '➤ 修改设备信息' },
        { type: 'screenshot', name: 'device-edit' },
      ]
    },
  }
};

// ========== 工具函数 ==========
class SemiAutoTester {
  constructor() {
    this.browser = null;
    this.context = null;
    this.page = null;
    this.rl = readline.createInterface({
      input: process.stdin,
      output: process.stdout
    });
    this.recordedActions = [];
    this.screenshotCounter = 0;
  }

  // 提问（等待人工输入）
  async ask(question) {
    return new Promise((resolve) => {
      this.rl.question(question, (answer) => {
        resolve(answer.trim());
      });
    });
  }

  // 暂停执行（等待人工确认）
  async pause(message = '') {
    console.log('\n' + '='.repeat(60));
    console.log('⏸️  暂停点');
    if (message) {
      console.log(`📋 ${message}`);
    }
    console.log('按 Enter 继续执行，输入 s 截图，输入 q 退出...');
    console.log('='.repeat(60));
    
    const answer = await this.ask('> ');
    
    if (answer.toLowerCase() === 'q') {
      console.log('❌ 用户中止测试');
      await this.cleanup();
      process.exit(0);
    } else if (answer.toLowerCase() === 's') {
      await this.screenshot('manual-pause');
      return this.pause(message); // 递归等待继续
    }
  }

  // 初始化浏览器
  async init() {
    console.log('🚀 启动 Playwright 半自动测试...');
    console.log(`浏览器: ${CONFIG.browser}`);
    console.log(`录制模式: ${CONFIG.recordMode ? '开启' : '关闭'}`);
    console.log(`慢速模式: ${CONFIG.slowMo}ms`);
    console.log(`目标URL: ${CONFIG.baseURL}\n`);
    
    // 创建目录
    if (!fs.existsSync(CONFIG.screenshotDir)) {
      fs.mkdirSync(CONFIG.screenshotDir, { recursive: true });
    }
    if (!fs.existsSync(CONFIG.recordingDir)) {
      fs.mkdirSync(CONFIG.recordingDir, { recursive: true });
    }
    
    // 启动浏览器
    const browserType = CONFIG.browser === 'firefox' ? firefox 
                      : CONFIG.browser === 'webkit' ? webkit 
                      : chromium;
    
    this.browser = await browserType.launch({
      headless: CONFIG.headless,
      slowMo: CONFIG.slowMo,
    });
    
    this.context = await this.browser.newContext({
      viewport: { width: 1920, height: 1080 },
      recordVideo: CONFIG.recordMode ? {
        dir: CONFIG.recordingDir,
        size: { width: 1920, height: 1080 }
      } : undefined,
    });
    
    this.page = await this.context.newPage();
    
    // 监听控制台
    this.page.on('console', msg => {
      if (msg.type() === 'error') {
        console.log(`❌ 浏览器控制台错误: ${msg.text()}`);
      }
    });
    
    // 监听页面错误
    this.page.on('pageerror', error => {
      console.log(`❌ 页面错误: ${error.message}`);
    });
    
    console.log('✅ 浏览器已启动\n');
  }

  // 导航到页面
  async navigate(url) {
    const fullUrl = url.startsWith('http') ? url : `${CONFIG.baseURL}${url}`;
    console.log(`🌐 导航到: ${fullUrl}`);
    
    if (CONFIG.recordMode) {
      this.recordedActions.push({ type: 'navigate', url });
    }
    
    await this.page.goto(fullUrl, { waitUntil: 'networkidle' });
    console.log('✅ 页面已加载\n');
  }

  // 点击元素
  async click(selector, options = {}) {
    console.log(`🖱️  点击: ${selector}`);
    
    if (CONFIG.recordMode) {
      this.recordedActions.push({ type: 'click', selector });
    }
    
    await this.page.click(selector, { timeout: 10000 });
    
    if (options.waitAfter) {
      await this.page.waitForTimeout(options.waitAfter);
    }
    
    console.log('✅ 点击完成\n');
  }

  // 填充输入框
  async fill(selector, value) {
    console.log(`⌨️  填充 ${selector}: ${value}`);
    
    if (CONFIG.recordMode) {
      this.recordedActions.push({ type: 'fill', selector, value });
    }
    
    await this.page.fill(selector, value);
    console.log('✅ 填充完成\n');
  }

  // 等待元素
  async waitFor(selector, options = {}) {
    console.log(`⏳ 等待元素: ${selector}`);
    
    try {
      await this.page.waitForSelector(selector, { timeout: options.timeout || 10000 });
      console.log('✅ 元素已出现\n');
      return true;
    } catch (e) {
      console.log(`❌ 元素未出现: ${selector}\n`);
      return false;
    }
  }

  // 截图
  async screenshot(name = '') {
    this.screenshotCounter++;
    const timestamp = new Date().toISOString().replace(/[:.]/g, '-').slice(0, -5);
    const filename = name 
      ? `${timestamp}_${name}.png` 
      : `${timestamp}_${this.screenshotCounter}.png`;
    
    const fullPath = path.join(CONFIG.screenshotDir, filename);
    
    console.log(`📸 截图: ${filename}`);
    await this.page.screenshot({ path: fullPath, fullPage: true });
    console.log(`✅ 截图已保存: ${fullPath}\n`);
  }

  // 执行场景
  async runScenario(scenarioName) {
    const scenario = CONFIG.scenarios[scenarioName];
    if (!scenario) {
      console.log(`❌ 场景不存在: ${scenarioName}`);
      return;
    }
    
    console.log('\n' + '='.repeat(80));
    console.log(`🎬 开始执行场景: ${scenario.name}`);
    console.log('='.repeat(80) + '\n');
    
    for (let i = 0; i < scenario.steps.length; i++) {
      const step = scenario.steps[i];
      console.log(`📍 步骤 ${i + 1}/${scenario.steps.length}: ${step.type}`);
      
      try {
        switch (step.type) {
          case 'navigate':
            await this.navigate(step.url);
            break;
          
          case 'click':
            await this.click(step.selector, { waitAfter: step.waitAfter });
            break;
          
          case 'fill':
            await this.fill(step.selector, step.value);
            break;
          
          case 'wait':
            await this.waitFor(step.selector, { timeout: step.timeout });
            break;
          
          case 'pause':
            await this.pause(step.message);
            break;
          
          case 'screenshot':
            await this.screenshot(step.name);
            break;
          
          default:
            console.log(`⚠️  未知步骤类型: ${step.type}`);
        }
      } catch (error) {
        console.log(`❌ 步骤执行失败: ${error.message}`);
        
        const answer = await this.ask('继续执行？ (y/n): ');
        if (answer.toLowerCase() !== 'y') {
          break;
        }
      }
    }
    
    console.log('\n' + '='.repeat(80));
    console.log(`✅ 场景执行完成: ${scenario.name}`);
    console.log('='.repeat(80) + '\n');
  }

  // 交互式模式
  async interactiveMode() {
    console.log('\n🎮 进入交互式模式');
    console.log('可用命令:');
    console.log('  goto <url>        - 导航到页面');
    console.log('  click <selector>  - 点击元素');
    console.log('  fill <selector> <value> - 填充输入框');
    console.log('  screenshot [name] - 截图');
    console.log('  wait <selector>   - 等待元素');
    console.log('  back              - 后退');
    console.log('  forward           - 前进');
    console.log('  reload            - 刷新');
    console.log('  save              - 保存录制');
    console.log('  quit              - 退出\n');
    
    while (true) {
      const command = await this.ask('🎮 > ');
      const [cmd, ...args] = command.split(' ');
      
      try {
        switch (cmd.toLowerCase()) {
          case 'goto':
            await this.navigate(args.join(' '));
            break;
          
          case 'click':
            await this.click(args[0]);
            break;
          
          case 'fill':
            await this.fill(args[0], args.slice(1).join(' '));
            break;
          
          case 'screenshot':
            await this.screenshot(args[0]);
            break;
          
          case 'wait':
            await this.waitFor(args[0]);
            break;
          
          case 'back':
            await this.page.goBack();
            console.log('✅ 后退完成\n');
            break;
          
          case 'forward':
            await this.page.goForward();
            console.log('✅ 前进完成\n');
            break;
          
          case 'reload':
            await this.page.reload();
            console.log('✅ 刷新完成\n');
            break;
          
          case 'save':
            this.saveRecording();
            break;
          
          case 'quit':
          case 'exit':
            return;
          
          default:
            console.log('❌ 未知命令\n');
        }
      } catch (error) {
        console.log(`❌ 执行失败: ${error.message}\n`);
      }
    }
  }

  // 保存录制
  saveRecording() {
    if (this.recordedActions.length === 0) {
      console.log('⚠️  没有录制内容\n');
      return;
    }
    
    const timestamp = new Date().toISOString().replace(/[:.]/g, '-').slice(0, -5);
    const filename = `recording_${timestamp}.json`;
    const fullPath = path.join(CONFIG.recordingDir, filename);
    
    fs.writeFileSync(fullPath, JSON.stringify({
      timestamp: new Date().toISOString(),
      browser: CONFIG.browser,
      baseURL: CONFIG.baseURL,
      actions: this.recordedActions,
    }, null, 2));
    
    console.log(`✅ 录制已保存: ${fullPath}\n`);
  }

  // 清理资源
  async cleanup() {
    console.log('\n🧹 清理资源...');
    
    if (CONFIG.recordMode && this.recordedActions.length > 0) {
      this.saveRecording();
    }
    
    if (this.context) {
      await this.context.close();
    }
    
    if (this.browser) {
      await this.browser.close();
    }
    
    this.rl.close();
    
    console.log('✅ 清理完成\n');
  }
}

// ========== 主入口 ==========
async function main() {
  const tester = new SemiAutoTester();
  
  try {
    await tester.init();
    
    // 显示菜单
    console.log('请选择执行模式:');
    console.log('1. 运行预定义场景');
    console.log('2. 交互式模式');
    console.log('3. 重放录制文件');
    
    const choice = await tester.ask('\n选择 (1-3): ');
    
    switch (choice) {
      case '1':
        // 场景模式
        console.log('\n可用场景:');
        Object.keys(CONFIG.scenarios).forEach((key, index) => {
          console.log(`${index + 1}. ${CONFIG.scenarios[key].name} (${key})`);
        });
        
        const scenarioChoice = await tester.ask('\n选择场景编号: ');
        const scenarioKey = Object.keys(CONFIG.scenarios)[parseInt(scenarioChoice) - 1];
        
        if (scenarioKey) {
          await tester.runScenario(scenarioKey);
        } else {
          console.log('❌ 无效的场景选择');
        }
        break;
      
      case '2':
        // 交互式模式
        await tester.interactiveMode();
        break;
      
      case '3':
        // 重放模式
        console.log('\n暂未实现重放功能');
        break;
      
      default:
        console.log('❌ 无效选择');
    }
    
  } catch (error) {
    console.error('❌ 执行出错:', error);
  } finally {
    await tester.cleanup();
  }
}

// 运行
main().catch(console.error);
