import { FullConfig } from '@playwright/test';
import { existsSync, readFileSync, writeFileSync } from 'fs';
import * as path from 'path';

/**
 * Playwright 全局清理
 * 在所有测试执行完毕后运行一次
 * 
 * 主要功能:
 * - 清理测试数据
 * - 生成测试摘要
 * - 归档测试结果
 * - 清理临时文件
 */

async function globalTeardown(config: FullConfig) {
  console.log('\n🧹 [Global Teardown] 开始全局清理...');

  // ========== 0. 关闭 Mock HTTP Server ==========
  const mockServer = (globalThis as any).__PLAYWRIGHT_MOCK_SERVER__;
  if (mockServer) {
    await new Promise<void>(resolve => mockServer.close(() => resolve()));
    console.log('🌐 [Global Teardown] Mock HTTP Server 已关闭');
  }
  
  const storageDir = path.join(__dirname, '.auth');
  
  // ========== 1. 读取测试运行信息 ==========
  try {
    const testRunInfoPath = path.join(storageDir, 'test-run-info.json');
    if (existsSync(testRunInfoPath)) {
      const testRunInfo = JSON.parse(readFileSync(testRunInfoPath, 'utf-8'));
      const endTime = new Date();
      const startTime = new Date(testRunInfo.startTime);
      const duration = Math.round((endTime.getTime() - startTime.getTime()) / 1000);
      
      console.log(`📊 [Global Teardown] 测试执行摘要:`);
      console.log(`   开始时间: ${testRunInfo.startTime}`);
      console.log(`   结束时间: ${endTime.toISOString()}`);
      console.log(`   总耗时: ${Math.floor(duration / 60)}分${duration % 60}秒`);
      console.log(`   环境: ${testRunInfo.environment}`);
      console.log(`   Base URL: ${testRunInfo.baseURL}`);
      
      // 更新测试运行信息
      testRunInfo.endTime = endTime.toISOString();
      testRunInfo.durationSeconds = duration;
      writeFileSync(testRunInfoPath, JSON.stringify(testRunInfo, null, 2));
    }
  } catch (error) {
    console.warn('⚠️  [Global Teardown] 无法读取测试运行信息:', error);
  }
  
  // ========== 2. 生成测试摘要 ==========
  try {
    const resultsPath = path.join(__dirname, '..', 'test-reports', 'playwright-report', 'results.json');
    if (existsSync(resultsPath)) {
      const content = readFileSync(resultsPath, 'utf-8').trim();
      // 跳过空文件或无效 JSON
      if (!content || content.length < 10 || !content.startsWith('{')) {
        console.log('⚠️  [Global Teardown] results.json 为空或无效，跳过摘要生成');
      } else {
        const results = JSON.parse(content);
      
      const total = results.suites?.reduce((sum: number, suite: any) => 
        sum + (suite.specs?.length || 0), 0) || 0;
      const passed = results.suites?.reduce((sum: number, suite: any) => 
        sum + (suite.specs?.filter((s: any) => s.tests[0]?.results[0]?.status === 'passed').length || 0), 0) || 0;
      const failed = results.suites?.reduce((sum: number, suite: any) => 
        sum + (suite.specs?.filter((s: any) => s.tests[0]?.results[0]?.status === 'failed').length || 0), 0) || 0;
      const skipped = results.suites?.reduce((sum: number, suite: any) => 
        sum + (suite.specs?.filter((s: any) => s.tests[0]?.results[0]?.status === 'skipped').length || 0), 0) || 0;
      
      console.log(`\n📈 [Global Teardown] Playwright 测试结果:`);
      console.log(`   总计: ${total}`);
      console.log(`   通过: ${passed} (${total > 0 ? (passed / total * 100).toFixed(1) : 0}%)`);
      console.log(`   失败: ${failed}`);
      console.log(`   跳过: ${skipped}`);
      
      // 生成简洁摘要文件
      const summary = {
        tool: 'playwright',
        timestamp: new Date().toISOString(),
        summary: { total, passed, failed, skipped, passRate: total > 0 ? `${(passed / total * 100).toFixed(2)}%` : '0%' },
      };
      writeFileSync(
        path.join(__dirname, '..', 'test-reports', 'playwright-report', 'summary.json'),
        JSON.stringify(summary, null, 2)
      );
      }
    }
  } catch (error) {
    console.warn('⚠️  [Global Teardown] 无法生成测试摘要:', error);
  }
  
  // ========== 3. 清理认证文件（可选）==========
  // 如果不想保留认证状态，可以在这里删除
  // 注释掉保留状态，以便下次运行时复用
  // try {
  //   const authFiles = ['admin-auth.json', 'user-auth.json'];
  //   authFiles.forEach(file => {
  //     const filePath = path.join(storageDir, file);
  //     if (existsSync(filePath)) {
  //       unlinkSync(filePath);
  //     }
  //   });
  //   console.log('✅ [Global Teardown] 认证文件已清理');
  // } catch (error) {
  //   console.warn('⚠️  [Global Teardown] 清理认证文件失败:', error);
  // }
  
  console.log('✅ [Global Teardown] 全局清理完成\n');
}

export default globalTeardown;
