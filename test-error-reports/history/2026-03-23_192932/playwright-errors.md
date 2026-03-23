# 🎭 Playwright 测试错误报告

- **执行时间**: 2026-03-23 19:29:32 UTC
- **Git Commit**: 07dd7c36283b798d148c935a0fcc5bd1e47debf3
- **触发方式**: push
- **测试级别**: smoke

## 失败详情

```
  ✘   6 [mobile-chrome] › tests/auth.spec.ts:26:7 › 认证模块 - 登录/登出 › [P0] 正确用户名密码登录成功 @smoke @critical (15.5s)
  ✘   7 [mobile-chrome] › tests/auth.spec.ts:36:7 › 认证模块 - 登录/登出 › [P0] 错误密码登录失败 @smoke (15.5s)
  ✘   8 [mobile-chrome] › tests/auth.spec.ts:26:7 › 认证模块 - 登录/登出 › [P0] 正确用户名密码登录成功 @smoke @critical (retry #1) (15.5s)
  ✘   9 [mobile-chrome] › tests/auth.spec.ts:36:7 › 认证模块 - 登录/登出 › [P0] 错误密码登录失败 @smoke (retry #1) (15.6s)
  ✘  10 [mobile-chrome] › tests/auth.spec.ts:26:7 › 认证模块 - 登录/登出 › [P0] 正确用户名密码登录成功 @smoke @critical (retry #2) (15.6s)
  ✘  11 [mobile-chrome] › tests/auth.spec.ts:36:7 › 认证模块 - 登录/登出 › [P0] 错误密码登录失败 @smoke (retry #2) (15.6s)
    TimeoutError: locator.click: Timeout 15000ms exceeded.
    test-results/auth-认证模块---登录-登出-P0-正确用户名密码登录成功-smoke-critical-mobile-chrome/test-failed-1.png
    Error Context: test-results/auth-认证模块---登录-登出-P0-正确用户名密码登录成功-smoke-critical-mobile-chrome/error-context.md
    TimeoutError: locator.click: Timeout 15000ms exceeded.
    test-results/auth-认证模块---登录-登出-P0-正确用户名密码登录成功-smoke-critical-mobile-chrome-retry1/test-failed-1.png
    Error Context: test-results/auth-认证模块---登录-登出-P0-正确用户名密码登录成功-smoke-critical-mobile-chrome-retry1/error-context.md
    TimeoutError: locator.click: Timeout 15000ms exceeded.
    test-results/auth-认证模块---登录-登出-P0-正确用户名密码登录成功-smoke-critical-mobile-chrome-retry2/test-failed-1.png
    Error Context: test-results/auth-认证模块---登录-登出-P0-正确用户名密码登录成功-smoke-critical-mobile-chrome-retry2/error-context.md
    TimeoutError: locator.click: Timeout 15000ms exceeded.
    test-results/auth-认证模块---登录-登出-P0-错误密码登录失败-smoke-mobile-chrome/test-failed-1.png
    Error Context: test-results/auth-认证模块---登录-登出-P0-错误密码登录失败-smoke-mobile-chrome/error-context.md
    TimeoutError: locator.click: Timeout 15000ms exceeded.
    test-results/auth-认证模块---登录-登出-P0-错误密码登录失败-smoke-mobile-chrome-retry1/test-failed-1.png
    Error Context: test-results/auth-认证模块---登录-登出-P0-错误密码登录失败-smoke-mobile-chrome-retry1/error-context.md
    TimeoutError: locator.click: Timeout 15000ms exceeded.
    test-results/auth-认证模块---登录-登出-P0-错误密码登录失败-smoke-mobile-chrome-retry2/test-failed-1.png
    Error Context: test-results/auth-认证模块---登录-登出-P0-错误密码登录失败-smoke-mobile-chrome-retry2/error-context.md
  2 failed
```
