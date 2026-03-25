# test-only-cloud

> 自动生成，请勿手动编辑

专用于自动化测试执行。测试脚本由 Gitee 主仓库推送，GitHub Actions 按选择清单自动执行 **6 类中的指定工具** 并分别生成独立报告。

## 架构说明

- **云端 6 类**：pytest / cypress / playwright / puppeteer / selenium / k6（全部 Mock 数据，零外部依赖）
- **本地 1 类**：integration（C# xUnit，依赖业务项目源码编译，在开发机运行）
- **当前选择**：cypress
- **执行模式**：full
- **K6 场景过滤**：无
- **本地默认**：real；仅在显式指定时切换到 local mock
- **报告同步**：pull 脚本只覆盖云端生成的 6 类独立报告；integration 始终保留本地报告

*同步时间: 2026-03-25 23:01:40*
