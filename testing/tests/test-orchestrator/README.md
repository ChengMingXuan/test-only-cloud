# AIOPS 统一测试编排器

> **一键执行全部 5 大测试工具**  
> 协调 Playwright + Selenium + Puppeteer + Cypress + K6

---

## 🚀 快速开始

```bash
cd tests/test-orchestrator

# 顺序执行全部测试
npm run test:all

# 并行执行（更快，但资源消耗大）
npm run test:parallel

# 快速模式（仅pytest + cypress，20分钟）
npm run test:quick

# E2E模式（playwright + selenium，2小时）
npm run test:e2e

# 性能模式（puppeteer + k6，1.5小时）
npm run test:performance
```

---

## 📊 聚合报告

测试完成后，查看统一报告：

```bash
# Windows
start ../test-reports/aggregated-report.json

# 或直接查看控制台输出
```

示例输出：

```
========================================================================
  📊 AIOPS 平台测试总览
========================================================================
  时间: 2026-03-05T10:30:00.000Z
========================================================================

┌─────────────┬────────┬────────┬────────┬──────────┐
│ 测试工具     │ 总数   │ 通过   │ 失败   │ 通过率   │
├─────────────┼────────┼────────┼────────┼──────────┤
│ pytest      │     93 │     93 │      0 │  100.0%  │
│ cypress     │    145 │    142 │      3 │   97.9%  │
│ playwright  │    120 │    115 │      5 │   95.8%  │
│ selenium    │     85 │     81 │      4 │   95.3%  │
│ puppeteer   │     42 │     40 │      2 │   95.2%  │
│ k6          │     28 │     25 │      3 │   89.3%  │
├─────────────┼────────┼────────┼────────┼──────────┤
│ 总计        │    513 │    496 │     17 │   96.7%  │
└─────────────┴────────┴────────┴────────┴──────────┘

发布门禁状态: ❌ 不通过

阻塞原因:
  - playwright: 5个测试失败
  - selenium: 4个测试失败
  - k6: 3个测试失败

========================================================================

总耗时: 285.50分钟
```

---

## 🎯 使用场景

### 场景1: 本地开发 - 快速验证

```bash
# 20分钟快速验证（仅API + 组件）
npm run test:quick
```

### 场景2: CI Pipeline - 每次提交

```bash
# 1小时标准验证
npm run test:all
```

### 场景3: 发版前 - 完整回归

```bash
# 4-5小时完整验证（顺序执行）
node run-all-tests.js sequential
```

### 场景4: 夜间定时 - 并行加速

```bash
# 2-3小时并行验证（需要强劲硬件）
npm run test:parallel
```

---

## 🔧 高级用法

### 自定义筛选

```bash
# 仅运行playwright和k6
node run-all-tests.js sequential playwright k6

# 仅运行API测试
node run-all-tests.js sequential pytest

# 仅运行UI测试
node run-all-tests.js sequential playwright selenium cypress
```

### CI集成

```yaml
# .github/workflows/test.yml
name: AIOPS测试流水线

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: 安装依赖
        run: |
          cd tests/test-orchestrator
          npm install
      
      - name: 执行测试
        run: |
          cd tests/test-orchestrator
          npm run test:all
      
      - name: 上传报告
        uses: actions/upload-artifact@v3
        with:
          name: test-reports
          path: tests/test-reports/
```

---

**最后更新**: 2026-03-05  
**维护者**: JGSY.AGI 测试团队
