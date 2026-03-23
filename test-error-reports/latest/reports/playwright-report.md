# 🎭 Playwright（E2E端到端测试） — 测试报告

> 来源：GitHub Actions CI | 级别：smoke | 2026-03-23 17:44:29 UTC

## 执行概要

| 指标 | 数值 |
|------|------|
| 标准用例数 | 11093 |
| 实际执行 | 35 |
| ✅ 通过 | 13 |
| ❌ 失败 | 22 |
| ⏭️ 跳过 | 0 |
| 通过率 | 37.14% |
| 耗时(s) | 112.123606 |

## 发布门禁

- **状态**：❌ 有失败 (22)
- **结论**：存在失败用例 - 不可发布

## 环境信息

| 项 | 值 |
|----|-----|
| Git Commit | `cb077e6d68140aba62e2fb412425abdc5deb0a7c` |
| 触发方式 | push |
| 运行环境 | ubuntu-latest |
| 测试级别 | smoke |

## 失败详情

```
  ✘   6 [firefox] › tests/auth.spec.ts:26:7 › 认证模块 - 登录/登出 › [P0] 正确用户名密码登录成功 @smoke @critical (4ms)
  ✓   5 [chromium] › tests/operation-audit.spec.ts:206:7 › 操作审计日志 — 完整 E2E 流程 › [P0] 回滚操作完整链路 @smoke (1.9s)
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
  ✓  42 [mobile-chrome] › tests/auth.spec.ts:59:7 › 认证模块 - 登录/登出 › [P0] 登录后成功登出 @smoke (527ms)
  ✘  41 [mobile-chrome] › tests/auth.spec.ts:36:7 › 认证模块 - 登录/登出 › [P0] 错误密码登录失败 @smoke (retry #2) (15.6s)
  ✓  43 [mobile-chrome] › tests/operation-audit.spec.ts:138:7 › 操作审计日志 — 完整 E2E 流程 › [P0] 操作日志列表页正常渲染 @smoke @critical (404ms)
  ✘  45 [mobile-safari] › tests/auth.spec.ts:26:7 › 认证模块 - 登录/登出 › [P0] 正确用户名密码登录成功 @smoke @critical (4ms)
  ✘  46 [mobile-safari] › tests/auth.spec.ts:26:7 › 认证模块 - 登录/登出 › [P0] 正确用户名密码登录成功 @smoke @critical (retry #1) (4ms)
  ✓  44 [mobile-chrome] › tests/operation-audit.spec.ts:206:7 › 操作审计日志 — 完整 E2E 流程 › [P0] 回滚操作完整链路 @smoke (2.0s)
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
  ✓  60 [desktop-hd] › tests/auth.spec.ts:26:7 › 认证模块 - 登录/登出 › [P0] 正确用户名密码登录成功 @smoke @critical (530ms)
  ✓  61 [desktop-hd] › tests/auth.spec.ts:59:7 › 认证模块 - 登录/登出 › [P0] 登录后成功登出 @smoke (444ms)
  ✓  63 [desktop-hd] › tests/operation-audit.spec.ts:138:7 › 操作审计日志 — 完整 E2E 流程 › [P0] 操作日志列表页正常渲染 @smoke @critical (429ms)
--
  ✘  65 [tablet] › tests/auth.spec.ts:26:7 › 认证模块 - 登录/登出 › [P0] 正确用户名密码登录成功 @smoke @critical (4ms)
  ✓  64 [desktop-hd] › tests/operation-audit.spec.ts:206:7 › 操作审计日志 — 完整 E2E 流程 › [P0] 回滚操作完整链路 @smoke (1.9s)
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

🧹 [Global Teardown] 开始全局清理...
🌐 [Global Teardown] Mock HTTP Server 已关闭
--
    Error: browserType.launch: Executable doesn't exist at /home/runner/.cache/ms-playwright/firefox-1509/firefox/firefox
    ╔═════════════════════════════════════════════════════════════════════════╗
    ║ Looks like Playwright Test or Playwright was just installed or updated. ║
    ║ Please run the following command to download new browsers:              ║
--
    Error: browserType.launch: Executable doesn't exist at /home/runner/.cache/ms-playwright/firefox-1509/firefox/firefox
    ╔═════════════════════════════════════════════════════════════════════════╗
    ║ Looks like Playwright Test or Playwright was just installed or updated. ║
    ║ Please run the following command to download new browsers:              ║
--
    Error: browserType.launch: Executable doesn't exist at /home/runner/.cache/ms-playwright/firefox-1509/firefox/firefox
    ╔═════════════════════════════════════════════════════════════════════════╗
    ║ Looks like Playwright Test or Playwright was just installed or updated. ║
    ║ Please run the following command to download new browsers:              ║
--
    Error: browserType.launch: Executable doesn't exist at /home/runner/.cache/ms-playwright/firefox-1509/firefox/firefox
    ╔═════════════════════════════════════════════════════════════════════════╗
    ║ Looks like Playwright Test or Playwright was just installed or updated. ║
    ║ Please run the following command to download new browsers:              ║
--
    Error: browserType.launch: Executable doesn't exist at /home/runner/.cache/ms-playwright/firefox-1509/firefox/firefox
    ╔═════════════════════════════════════════════════════════════════════════╗
    ║ Looks like Playwright Test or Playwright was just installed or updated. ║
    ║ Please run the following command to download new browsers:              ║
--
    Error: browserType.launch: Executable doesn't exist at /home/runner/.cache/ms-playwright/firefox-1509/firefox/firefox
    ╔═════════════════════════════════════════════════════════════════════════╗
    ║ Looks like Playwright Test or Playwright was just installed or updated. ║
    ║ Please run the following command to download new browsers:              ║
--
    Error: browserType.launch: Executable doesn't exist at /home/runner/.cache/ms-playwright/firefox-1509/firefox/firefox
    ╔═════════════════════════════════════════════════════════════════════════╗
    ║ Looks like Playwright Test or Playwright was just installed or updated. ║
    ║ Please run the following command to download new browsers:              ║
--
    Error: browserType.launch: Executable doesn't exist at /home/runner/.cache/ms-playwright/firefox-1509/firefox/firefox
    ╔═════════════════════════════════════════════════════════════════════════╗
    ║ Looks like Playwright Test or Playwright was just installed or updated. ║
    ║ Please run the following command to download new browsers:              ║
--
    Error: browserType.launch: Executable doesn't exist at /home/runner/.cache/ms-playwright/firefox-1509/firefox/firefox
    ╔═════════════════════════════════════════════════════════════════════════╗
    ║ Looks like Playwright Test or Playwright was just installed or updated. ║
    ║ Please run the following command to download new browsers:              ║
--
    Error: browserType.launch: Executable doesn't exist at /home/runner/.cache/ms-playwright/firefox-1509/firefox/firefox
    ╔═════════════════════════════════════════════════════════════════════════╗
    ║ Looks like Playwright Test or Playwright was just installed or updated. ║
    ║ Please run the following command to download new browsers:              ║
--
    Error: browserType.launch: Executable doesn't exist at /home/runner/.cache/ms-playwright/firefox-1509/firefox/firefox
    ╔═════════════════════════════════════════════════════════════════════════╗
    ║ Looks like Playwright Test or Playwright was just installed or updated. ║
    ║ Please run the following command to download new browsers:              ║
--
    Error: browserType.launch: Executable doesn't exist at /home/runner/.cache/ms-playwright/firefox-1509/firefox/firefox
    ╔═════════════════════════════════════════════════════════════════════════╗
    ║ Looks like Playwright Test or Playwright was just installed or updated. ║
    ║ Please run the following command to download new browsers:              ║
--
    Error: browserType.launch: Executable doesn't exist at /home/runner/.cache/ms-playwright/firefox-1509/firefox/firefox
    ╔═════════════════════════════════════════════════════════════════════════╗
    ║ Looks like Playwright Test or Playwright was just installed or updated. ║
    ║ Please run the following command to download new browsers:              ║
--
    Error: browserType.launch: Executable doesn't exist at /home/runner/.cache/ms-playwright/firefox-1509/firefox/firefox
    ╔═════════════════════════════════════════════════════════════════════════╗
    ║ Looks like Playwright Test or Playwright was just installed or updated. ║
    ║ Please run the following command to download new browsers:              ║
--
    Error: browserType.launch: Executable doesn't exist at /home/runner/.cache/ms-playwright/firefox-1509/firefox/firefox
    ╔═════════════════════════════════════════════════════════════════════════╗
    ║ Looks like Playwright Test or Playwright was just installed or updated. ║
    ║ Please run the following command to download new browsers:              ║
--
    Error: browserType.launch: Executable doesn't exist at /home/runner/.cache/ms-playwright/webkit-2248/pw_run.sh
    ╔═════════════════════════════════════════════════════════════════════════╗
    ║ Looks like Playwright Test or Playwright was just installed or updated. ║
    ║ Please run the following command to download new browsers:              ║
--
    Error: browserType.launch: Executable doesn't exist at /home/runner/.cache/ms-playwright/webkit-2248/pw_run.sh
    ╔═════════════════════════════════════════════════════════════════════════╗
    ║ Looks like Playwright Test or Playwright was just installed or updated. ║
    ║ Please run the following command to download new browsers:              ║
--
    Error: browserType.launch: Executable doesn't exist at /home/runner/.cache/ms-playwright/webkit-2248/pw_run.sh
    ╔═════════════════════════════════════════════════════════════════════════╗
    ║ Looks like Playwright Test or Playwright was just installed or updated. ║
    ║ Please run the following command to download new browsers:              ║
--
    Error: browserType.launch: Executable doesn't exist at /home/runner/.cache/ms-playwright/webkit-2248/pw_run.sh
    ╔═════════════════════════════════════════════════════════════════════════╗
    ║ Looks like Playwright Test or Playwright was just installed or updated. ║
    ║ Please run the following command to download new browsers:              ║
--
    Error: browserType.launch: Executable doesn't exist at /home/runner/.cache/ms-playwright/webkit-2248/pw_run.sh
    ╔═════════════════════════════════════════════════════════════════════════╗
    ║ Looks like Playwright Test or Playwright was just installed or updated. ║
    ║ Please run the following command to download new browsers:              ║
--
    Error: browserType.launch: Executable doesn't exist at /home/runner/.cache/ms-playwright/webkit-2248/pw_run.sh
    ╔═════════════════════════════════════════════════════════════════════════╗
    ║ Looks like Playwright Test or Playwright was just installed or updated. ║
    ║ Please run the following command to download new browsers:              ║
--
    Error: browserType.launch: Executable doesn't exist at /home/runner/.cache/ms-playwright/webkit-2248/pw_run.sh
    ╔═════════════════════════════════════════════════════════════════════════╗
    ║ Looks like Playwright Test or Playwright was just installed or updated. ║
    ║ Please run the following command to download new browsers:              ║
--
    Error: browserType.launch: Executable doesn't exist at /home/runner/.cache/ms-playwright/webkit-2248/pw_run.sh
    ╔═════════════════════════════════════════════════════════════════════════╗
    ║ Looks like Playwright Test or Playwright was just installed or updated. ║
    ║ Please run the following command to download new browsers:              ║
--
    Error: browserType.launch: Executable doesn't exist at /home/runner/.cache/ms-playwright/webkit-2248/pw_run.sh
    ╔═════════════════════════════════════════════════════════════════════════╗
    ║ Looks like Playwright Test or Playwright was just installed or updated. ║
    ║ Please run the following command to download new browsers:              ║
--
    Error: browserType.launch: Executable doesn't exist at /home/runner/.cache/ms-playwright/webkit-2248/pw_run.sh
```
