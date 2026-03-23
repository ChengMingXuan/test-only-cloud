# 🎭 Playwright（E2E端到端测试） — 测试报告

> 来源：GitHub Actions CI | 级别：smoke | 2026-03-23 21:09:38 UTC

## 执行概要

| 指标 | 数值 |
|------|------|
| 标准用例数 | 11093 |
| 实际执行 | 15 |
| ✅ 通过 | 13 |
| ❌ 失败 | 2 |
| ⏭️ 跳过 | 0 |
| 通过率 | 86.67% |
| 耗时(s) | 70.84926800000001 |

## 发布门禁

- **状态**：❌ 有失败 (2)
- **结论**：存在失败用例 - 不可发布

## 环境信息

| 项 | 值 |
|----|-----|
| Git Commit | `982d1937eec60eb18fdd932357bc0407f837e120` |
| 触发方式 | push |
| 运行环境 | ubuntu-latest |
| 测试级别 | smoke |

## 失败详情

```
  ✘   6 [mobile-chrome] › tests/auth.spec.ts:26:7 › 认证模块 - 登录/登出 › [P0] 正确用户名密码登录成功 @smoke @critical (15.5s)
  ✘   7 [mobile-chrome] › tests/auth.spec.ts:36:7 › 认证模块 - 登录/登出 › [P0] 错误密码登录失败 @smoke (15.5s)
  ✘   8 [mobile-chrome] › tests/auth.spec.ts:26:7 › 认证模块 - 登录/登出 › [P0] 正确用户名密码登录成功 @smoke @critical (retry #1) (15.5s)
  ✘   9 [mobile-chrome] › tests/auth.spec.ts:36:7 › 认证模块 - 登录/登出 › [P0] 错误密码登录失败 @smoke (retry #1) (15.5s)
  ✘  10 [mobile-chrome] › tests/auth.spec.ts:26:7 › 认证模块 - 登录/登出 › [P0] 正确用户名密码登录成功 @smoke @critical (retry #2) (15.5s)
  ✓  12 [mobile-chrome] › tests/auth.spec.ts:59:7 › 认证模块 - 登录/登出 › [P0] 登录后成功登出 @smoke (398ms)
  ✓  13 [mobile-chrome] › tests/operation-audit.spec.ts:138:7 › 操作审计日志 — 完整 E2E 流程 › [P0] 操作日志列表页正常渲染 @smoke @critical (465ms)
  ✘  11 [mobile-chrome] › tests/auth.spec.ts:36:7 › 认证模块 - 登录/登出 › [P0] 错误密码登录失败 @smoke (retry #2) (15.6s)
  ✓  15 [desktop-hd] › tests/auth.spec.ts:26:7 › 认证模块 - 登录/登出 › [P0] 正确用户名密码登录成功 @smoke @critical (508ms)
  ✓  14 [mobile-chrome] › tests/operation-audit.spec.ts:206:7 › 操作审计日志 — 完整 E2E 流程 › [P0] 回滚操作完整链路 @smoke (2.0s)
  ✓  16 [desktop-hd] › tests/auth.spec.ts:36:7 › 认证模块 - 登录/登出 › [P0] 错误密码登录失败 @smoke (493ms)
--
    TimeoutError: locator.click: Timeout 15000ms exceeded.
    Call log:
    [2m  - waiting for locator('button[type="submit"], button:has-text("登录")').first()[22m
    [2m    - locator resolved to <button type="submit">登录</button>[22m
--
    Error Context: test-results/auth-认证模块---登录-登出-P0-正确用户名密码登录成功-smoke-critical-mobile-chrome/error-context.md

    attachment #4: trace (application/zip) ─────────────────────────────────────────────────────────
    test-results/auth-认证模块---登录-登出-P0-正确用户名密码登录成功-smoke-critical-mobile-chrome/trace.zip
--
    TimeoutError: locator.click: Timeout 15000ms exceeded.
    Call log:
    [2m  - waiting for locator('button[type="submit"], button:has-text("登录")').first()[22m
    [2m    - locator resolved to <button type="submit">登录</button>[22m
--
    Error Context: test-results/auth-认证模块---登录-登出-P0-正确用户名密码登录成功-smoke-critical-mobile-chrome-retry1/error-context.md

    attachment #4: trace (application/zip) ─────────────────────────────────────────────────────────
    test-results/auth-认证模块---登录-登出-P0-正确用户名密码登录成功-smoke-critical-mobile-chrome-retry1/trace.zip
--
    TimeoutError: locator.click: Timeout 15000ms exceeded.
    Call log:
    [2m  - waiting for locator('button[type="submit"], button:has-text("登录")').first()[22m
    [2m    - locator resolved to <button type="submit">登录</button>[22m
--
    Error Context: test-results/auth-认证模块---登录-登出-P0-正确用户名密码登录成功-smoke-critical-mobile-chrome-retry2/error-context.md

    attachment #4: trace (application/zip) ─────────────────────────────────────────────────────────
    test-results/auth-认证模块---登录-登出-P0-正确用户名密码登录成功-smoke-critical-mobile-chrome-retry2/trace.zip
--
    TimeoutError: locator.click: Timeout 15000ms exceeded.
    Call log:
    [2m  - waiting for locator('button[type="submit"], button:has-text("登录")').first()[22m
    [2m    - locator resolved to <button type="submit">登录</button>[22m
--
    Error Context: test-results/auth-认证模块---登录-登出-P0-错误密码登录失败-smoke-mobile-chrome/error-context.md

    attachment #4: trace (application/zip) ─────────────────────────────────────────────────────────
    test-results/auth-认证模块---登录-登出-P0-错误密码登录失败-smoke-mobile-chrome/trace.zip
--
    TimeoutError: locator.click: Timeout 15000ms exceeded.
    Call log:
    [2m  - waiting for locator('button[type="submit"], button:has-text("登录")').first()[22m
    [2m    - locator resolved to <button type="submit">登录</button>[22m
--
    Error Context: test-results/auth-认证模块---登录-登出-P0-错误密码登录失败-smoke-mobile-chrome-retry1/error-context.md

    attachment #4: trace (application/zip) ─────────────────────────────────────────────────────────
    test-results/auth-认证模块---登录-登出-P0-错误密码登录失败-smoke-mobile-chrome-retry1/trace.zip
--
    TimeoutError: locator.click: Timeout 15000ms exceeded.
    Call log:
    [2m  - waiting for locator('button[type="submit"], button:has-text("登录")').first()[22m
    [2m    - locator resolved to <button type="submit">登录</button>[22m
--
    Error Context: test-results/auth-认证模块---登录-登出-P0-错误密码登录失败-smoke-mobile-chrome-retry2/error-context.md

    attachment #4: trace (application/zip) ─────────────────────────────────────────────────────────
    test-results/auth-认证模块---登录-登出-P0-错误密码登录失败-smoke-mobile-chrome-retry2/trace.zip
```
