# 测试错误报告目录

本目录存放 GitHub Actions 自动生成的测试错误报告。

## 结构

```
test-error-reports/
├── latest/              ← 最新一次测试报告（每次覆盖更新）
│   ├── summary.md       ← 汇总报告
│   ├── pytest-errors.md
│   ├── cypress-errors.md
│   ├── playwright-errors.md
│   ├── puppeteer-errors.md
│   ├── selenium-errors.md
│   └── k6-errors.md
│
└── history/             ← 历史报告（按时间戳归档）
    └── YYYY-MM-DD_HHMMSS/
```

## 如何获取

在主项目中运行：

```powershell
.\scripts\pull-cloud-test-reports.ps1
```

报告会被拉取到主项目的 `TestResults/cloud-test-reports/` 目录。
