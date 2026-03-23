# 🎭 Playwright 测试错误报告

- **执行时间**: 2026-03-23 17:44:28 UTC
- **Git Commit**: cb077e6d68140aba62e2fb412425abdc5deb0a7c
- **触发方式**: push
- **测试级别**: smoke

## 失败详情

```
  ✘   6 [firefox] › tests/auth.spec.ts:26:7 › 认证模块 - 登录/登出 › [P0] 正确用户名密码登录成功 @smoke @critical (4ms)
  ✘   7 [firefox] › tests/auth.spec.ts:26:7 › 认证模块 - 登录/登出 › [P0] 正确用户名密码登录成功 @smoke @critical (retry #1) (4ms)
  ✘   8 [firefox] › tests/auth.spec.ts:36:7 › 认证模块 - 登录/登出 › [P0] 错误密码登录失败 @smoke (4ms)
  ✘   9 [firefox] › tests/auth.spec.ts:26:7 › 认证模块 - 登录/登出 › [P0] 正确用户名密码登录成功 @smoke @critical (retry #2) (4ms)
  ✘  10 [firefox] › tests/auth.spec.ts:36:7 › 认证模块 - 登录/登出 › [P0] 错误密码登录失败 @smoke (retry #1) (5ms)
  ✘  11 [firefox] › tests/auth.spec.ts:59:7 › 认证模块 - 登录/登出 › [P0] 登录后成功登出 @smoke (4ms)
  ✘  12 [firefox] › tests/auth.spec.ts:36:7 › 认证模块 - 登录/登出 › [P0] 错误密码登录失败 @smoke (retry #2) (4ms)
  ✘  13 [firefox] › tests/auth.spec.ts:59:7 › 认证模块 - 登录/登出 › [P0] 登录后成功登出 @smoke (retry #1) (4ms)
  ✘  14 [firefox] › tests/operation-audit.spec.ts:138:7 › 操作审计日志 — 完整 E2E 流程 › [P0] 操作日志列表页正常渲染 @smoke @critical (4ms)
  ✘  15 [firefox] › tests/auth.spec.ts:59:7 › 认证模块 - 登录/登出 › [P0] 登录后成功登出 @smoke (retry #2) (5ms)
  ✘  16 [firefox] › tests/operation-audit.spec.ts:138:7 › 操作审计日志 — 完整 E2E 流程 › [P0] 操作日志列表页正常渲染 @smoke @critical (retry #1) (5ms)
  ✘  17 [firefox] › tests/operation-audit.spec.ts:206:7 › 操作审计日志 — 完整 E2E 流程 › [P0] 回滚操作完整链路 @smoke (4ms)
  ✘  18 [firefox] › tests/operation-audit.spec.ts:138:7 › 操作审计日志 — 完整 E2E 流程 › [P0] 操作日志列表页正常渲染 @smoke @critical (retry #2) (4ms)
  ✘  19 [firefox] › tests/operation-audit.spec.ts:206:7 › 操作审计日志 — 完整 E2E 流程 › [P0] 回滚操作完整链路 @smoke (retry #1) (5ms)
  ✘  20 [webkit] › tests/auth.spec.ts:26:7 › 认证模块 - 登录/登出 › [P0] 正确用户名密码登录成功 @smoke @critical (4ms)
  ✘  21 [firefox] › tests/operation-audit.spec.ts:206:7 › 操作审计日志 — 完整 E2E 流程 › [P0] 回滚操作完整链路 @smoke (retry #2) (4ms)
  ✘  22 [webkit] › tests/auth.spec.ts:26:7 › 认证模块 - 登录/登出 › [P0] 正确用户名密码登录成功 @smoke @critical (retry #1) (4ms)
  ✘  23 [webkit] › tests/auth.spec.ts:36:7 › 认证模块 - 登录/登出 › [P0] 错误密码登录失败 @smoke (4ms)
  ✘  24 [webkit] › tests/auth.spec.ts:26:7 › 认证模块 - 登录/登出 › [P0] 正确用户名密码登录成功 @smoke @critical (retry #2) (4ms)
  ✘  25 [webkit] › tests/auth.spec.ts:36:7 › 认证模块 - 登录/登出 › [P0] 错误密码登录失败 @smoke (retry #1) (4ms)
  ✘  26 [webkit] › tests/auth.spec.ts:59:7 › 认证模块 - 登录/登出 › [P0] 登录后成功登出 @smoke (4ms)
  ✘  27 [webkit] › tests/auth.spec.ts:36:7 › 认证模块 - 登录/登出 › [P0] 错误密码登录失败 @smoke (retry #2) (4ms)
  ✘  28 [webkit] › tests/auth.spec.ts:59:7 › 认证模块 - 登录/登出 › [P0] 登录后成功登出 @smoke (retry #1) (4ms)
  ✘  29 [webkit] › tests/operation-audit.spec.ts:138:7 › 操作审计日志 — 完整 E2E 流程 › [P0] 操作日志列表页正常渲染 @smoke @critical (4ms)
  ✘  30 [webkit] › tests/auth.spec.ts:59:7 › 认证模块 - 登录/登出 › [P0] 登录后成功登出 @smoke (retry #2) (4ms)
  ✘  31 [webkit] › tests/operation-audit.spec.ts:138:7 › 操作审计日志 — 完整 E2E 流程 › [P0] 操作日志列表页正常渲染 @smoke @critical (retry #1) (4ms)
  ✘  32 [webkit] › tests/operation-audit.spec.ts:206:7 › 操作审计日志 — 完整 E2E 流程 › [P0] 回滚操作完整链路 @smoke (4ms)
  ✘  33 [webkit] › tests/operation-audit.spec.ts:138:7 › 操作审计日志 — 完整 E2E 流程 › [P0] 操作日志列表页正常渲染 @smoke @critical (retry #2) (4ms)
  ✘  34 [webkit] › tests/operation-audit.spec.ts:206:7 › 操作审计日志 — 完整 E2E 流程 › [P0] 回滚操作完整链路 @smoke (retry #1) (4ms)
  ✘  36 [webkit] › tests/operation-audit.spec.ts:206:7 › 操作审计日志 — 完整 E2E 流程 › [P0] 回滚操作完整链路 @smoke (retry #2) (5ms)
  ✘  35 [mobile-chrome] › tests/auth.spec.ts:26:7 › 认证模块 - 登录/登出 › [P0] 正确用户名密码登录成功 @smoke @critical (15.5s)
  ✘  37 [mobile-chrome] › tests/auth.spec.ts:36:7 › 认证模块 - 登录/登出 › [P0] 错误密码登录失败 @smoke (15.5s)
  ✘  38 [mobile-chrome] › tests/auth.spec.ts:26:7 › 认证模块 - 登录/登出 › [P0] 正确用户名密码登录成功 @smoke @critical (retry #1) (15.6s)
  ✘  39 [mobile-chrome] › tests/auth.spec.ts:36:7 › 认证模块 - 登录/登出 › [P0] 错误密码登录失败 @smoke (retry #1) (15.6s)
  ✘  40 [mobile-chrome] › tests/auth.spec.ts:26:7 › 认证模块 - 登录/登出 › [P0] 正确用户名密码登录成功 @smoke @critical (retry #2) (15.6s)
  ✘  41 [mobile-chrome] › tests/auth.spec.ts:36:7 › 认证模块 - 登录/登出 › [P0] 错误密码登录失败 @smoke (retry #2) (15.6s)
  ✘  45 [mobile-safari] › tests/auth.spec.ts:26:7 › 认证模块 - 登录/登出 › [P0] 正确用户名密码登录成功 @smoke @critical (4ms)
  ✘  46 [mobile-safari] › tests/auth.spec.ts:26:7 › 认证模块 - 登录/登出 › [P0] 正确用户名密码登录成功 @smoke @critical (retry #1) (4ms)
  ✘  47 [mobile-safari] › tests/auth.spec.ts:26:7 › 认证模块 - 登录/登出 › [P0] 正确用户名密码登录成功 @smoke @critical (retry #2) (4ms)
  ✘  48 [mobile-safari] › tests/auth.spec.ts:36:7 › 认证模块 - 登录/登出 › [P0] 错误密码登录失败 @smoke (4ms)
  ✘  49 [mobile-safari] › tests/auth.spec.ts:59:7 › 认证模块 - 登录/登出 › [P0] 登录后成功登出 @smoke (4ms)
  ✘  50 [mobile-safari] › tests/auth.spec.ts:36:7 › 认证模块 - 登录/登出 › [P0] 错误密码登录失败 @smoke (retry #1) (5ms)
  ✘  51 [mobile-safari] › tests/auth.spec.ts:59:7 › 认证模块 - 登录/登出 › [P0] 登录后成功登出 @smoke (retry #1) (4ms)
  ✘  52 [mobile-safari] › tests/auth.spec.ts:36:7 › 认证模块 - 登录/登出 › [P0] 错误密码登录失败 @smoke (retry #2) (4ms)
  ✘  53 [mobile-safari] › tests/auth.spec.ts:59:7 › 认证模块 - 登录/登出 › [P0] 登录后成功登出 @smoke (retry #2) (3ms)
  ✘  54 [mobile-safari] › tests/operation-audit.spec.ts:138:7 › 操作审计日志 — 完整 E2E 流程 › [P0] 操作日志列表页正常渲染 @smoke @critical (4ms)
  ✘  55 [mobile-safari] › tests/operation-audit.spec.ts:206:7 › 操作审计日志 — 完整 E2E 流程 › [P0] 回滚操作完整链路 @smoke (4ms)
  ✘  56 [mobile-safari] › tests/operation-audit.spec.ts:138:7 › 操作审计日志 — 完整 E2E 流程 › [P0] 操作日志列表页正常渲染 @smoke @critical (retry #1) (5ms)
  ✘  57 [mobile-safari] › tests/operation-audit.spec.ts:206:7 › 操作审计日志 — 完整 E2E 流程 › [P0] 回滚操作完整链路 @smoke (retry #1) (4ms)
  ✘  58 [mobile-safari] › tests/operation-audit.spec.ts:138:7 › 操作审计日志 — 完整 E2E 流程 › [P0] 操作日志列表页正常渲染 @smoke @critical (retry #2) (4ms)
  ✘  59 [mobile-safari] › tests/operation-audit.spec.ts:206:7 › 操作审计日志 — 完整 E2E 流程 › [P0] 回滚操作完整链路 @smoke (retry #2) (5ms)
  ✘  65 [tablet] › tests/auth.spec.ts:26:7 › 认证模块 - 登录/登出 › [P0] 正确用户名密码登录成功 @smoke @critical (4ms)
  ✘  66 [tablet] › tests/auth.spec.ts:26:7 › 认证模块 - 登录/登出 › [P0] 正确用户名密码登录成功 @smoke @critical (retry #1) (5ms)
  ✘  67 [tablet] › tests/auth.spec.ts:36:7 › 认证模块 - 登录/登出 › [P0] 错误密码登录失败 @smoke (5ms)
  ✘  68 [tablet] › tests/auth.spec.ts:26:7 › 认证模块 - 登录/登出 › [P0] 正确用户名密码登录成功 @smoke @critical (retry #2) (4ms)
  ✘  69 [tablet] › tests/auth.spec.ts:36:7 › 认证模块 - 登录/登出 › [P0] 错误密码登录失败 @smoke (retry #1) (4ms)
  ✘  70 [tablet] › tests/auth.spec.ts:59:7 › 认证模块 - 登录/登出 › [P0] 登录后成功登出 @smoke (4ms)
  ✘  71 [tablet] › tests/auth.spec.ts:36:7 › 认证模块 - 登录/登出 › [P0] 错误密码登录失败 @smoke (retry #2) (4ms)
  ✘  72 [tablet] › tests/auth.spec.ts:59:7 › 认证模块 - 登录/登出 › [P0] 登录后成功登出 @smoke (retry #1) (4ms)
  ✘  73 [tablet] › tests/operation-audit.spec.ts:138:7 › 操作审计日志 — 完整 E2E 流程 › [P0] 操作日志列表页正常渲染 @smoke @critical (4ms)
  ✘  74 [tablet] › tests/auth.spec.ts:59:7 › 认证模块 - 登录/登出 › [P0] 登录后成功登出 @smoke (retry #2) (4ms)
  ✘  75 [tablet] › tests/operation-audit.spec.ts:138:7 › 操作审计日志 — 完整 E2E 流程 › [P0] 操作日志列表页正常渲染 @smoke @critical (retry #1) (4ms)
  ✘  76 [tablet] › tests/operation-audit.spec.ts:206:7 › 操作审计日志 — 完整 E2E 流程 › [P0] 回滚操作完整链路 @smoke (5ms)
  ✘  77 [tablet] › tests/operation-audit.spec.ts:138:7 › 操作审计日志 — 完整 E2E 流程 › [P0] 操作日志列表页正常渲染 @smoke @critical (retry #2) (5ms)
  ✘  78 [tablet] › tests/operation-audit.spec.ts:206:7 › 操作审计日志 — 完整 E2E 流程 › [P0] 回滚操作完整链路 @smoke (retry #1) (4ms)
  ✘  79 [tablet] › tests/operation-audit.spec.ts:206:7 › 操作审计日志 — 完整 E2E 流程 › [P0] 回滚操作完整链路 @smoke (retry #2) (4ms)
    Error: browserType.launch: Executable doesn't exist at /home/runner/.cache/ms-playwright/firefox-1509/firefox/firefox
    Error: browserType.launch: Executable doesn't exist at /home/runner/.cache/ms-playwright/firefox-1509/firefox/firefox
    Error: browserType.launch: Executable doesn't exist at /home/runner/.cache/ms-playwright/firefox-1509/firefox/firefox
    Error: browserType.launch: Executable doesn't exist at /home/runner/.cache/ms-playwright/firefox-1509/firefox/firefox
    Error: browserType.launch: Executable doesn't exist at /home/runner/.cache/ms-playwright/firefox-1509/firefox/firefox
    Error: browserType.launch: Executable doesn't exist at /home/runner/.cache/ms-playwright/firefox-1509/firefox/firefox
    Error: browserType.launch: Executable doesn't exist at /home/runner/.cache/ms-playwright/firefox-1509/firefox/firefox
    Error: browserType.launch: Executable doesn't exist at /home/runner/.cache/ms-playwright/firefox-1509/firefox/firefox
    Error: browserType.launch: Executable doesn't exist at /home/runner/.cache/ms-playwright/firefox-1509/firefox/firefox
    Error: browserType.launch: Executable doesn't exist at /home/runner/.cache/ms-playwright/firefox-1509/firefox/firefox
    Error: browserType.launch: Executable doesn't exist at /home/runner/.cache/ms-playwright/firefox-1509/firefox/firefox
    Error: browserType.launch: Executable doesn't exist at /home/runner/.cache/ms-playwright/firefox-1509/firefox/firefox
    Error: browserType.launch: Executable doesn't exist at /home/runner/.cache/ms-playwright/firefox-1509/firefox/firefox
    Error: browserType.launch: Executable doesn't exist at /home/runner/.cache/ms-playwright/firefox-1509/firefox/firefox
    Error: browserType.launch: Executable doesn't exist at /home/runner/.cache/ms-playwright/firefox-1509/firefox/firefox
    Error: browserType.launch: Executable doesn't exist at /home/runner/.cache/ms-playwright/webkit-2248/pw_run.sh
    Error: browserType.launch: Executable doesn't exist at /home/runner/.cache/ms-playwright/webkit-2248/pw_run.sh
    Error: browserType.launch: Executable doesn't exist at /home/runner/.cache/ms-playwright/webkit-2248/pw_run.sh
    Error: browserType.launch: Executable doesn't exist at /home/runner/.cache/ms-playwright/webkit-2248/pw_run.sh
    Error: browserType.launch: Executable doesn't exist at /home/runner/.cache/ms-playwright/webkit-2248/pw_run.sh
    Error: browserType.launch: Executable doesn't exist at /home/runner/.cache/ms-playwright/webkit-2248/pw_run.sh
    Error: browserType.launch: Executable doesn't exist at /home/runner/.cache/ms-playwright/webkit-2248/pw_run.sh
    Error: browserType.launch: Executable doesn't exist at /home/runner/.cache/ms-playwright/webkit-2248/pw_run.sh
    Error: browserType.launch: Executable doesn't exist at /home/runner/.cache/ms-playwright/webkit-2248/pw_run.sh
    Error: browserType.launch: Executable doesn't exist at /home/runner/.cache/ms-playwright/webkit-2248/pw_run.sh
    Error: browserType.launch: Executable doesn't exist at /home/runner/.cache/ms-playwright/webkit-2248/pw_run.sh
    Error: browserType.launch: Executable doesn't exist at /home/runner/.cache/ms-playwright/webkit-2248/pw_run.sh
    Error: browserType.launch: Executable doesn't exist at /home/runner/.cache/ms-playwright/webkit-2248/pw_run.sh
    Error: browserType.launch: Executable doesn't exist at /home/runner/.cache/ms-playwright/webkit-2248/pw_run.sh
    Error: browserType.launch: Executable doesn't exist at /home/runner/.cache/ms-playwright/webkit-2248/pw_run.sh
    TimeoutError: locator.click: Timeout 15000ms exceeded.
    test-results/auth-认证模块---登录-登出-P0-正确用户名密码登录成功-smoke-critical-mobile-chrome/test-failed-1.png
    Error Context: test-results/auth-认证模块---登录-登出-P0-正确用户名密码登录成功-smoke-critical-mobile-chrome/error-context.md
    TimeoutError: locator.click: Timeout 15000ms exceeded.
```
