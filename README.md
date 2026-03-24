# test-only-cloud

> 自动生成，请勿手动编辑

专用于自动化测试执行。测试脚本由 Gitee 主仓库推送，GitHub Actions 自动执行 **6 类**测试并生成报告。

## 架构说明

- **云端 6 类**：pytest / cypress / playwright / puppeteer / selenium / k6（全部 Mock 数据，零外部依赖）
- **本地 1 类**：integration（C# xUnit，依赖业务项目源码编译，在开发机运行）
- **报告合并**：本地通过 pull 脚本拉取云端 6 份报告 + 本地 integration 报告 → 7 份总报告

*同步时间: 2026-03-25 00:41:38*
