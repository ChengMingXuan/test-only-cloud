# playwright 测试错误报告

- **执行时间**: 2026-03-24 03:58:21 UTC
- **Git Commit**: d7cd74e2b862e40637cac72d93b9bfb18862aae5

## 失败详情

```
  ✘   7546 [chromium] › tests/generated/e2e-302-v318-boundary-incremental.spec.ts:96:7 › 碳认证完整业务流程 › I-REC设备注册到证书签发完整流程 (254ms)
  ✘   7550 [chromium] › tests/generated/e2e-302-v318-boundary-incremental.spec.ts:96:7 › 碳认证完整业务流程 › I-REC设备注册到证书签发完整流程 (retry #1) (360ms)
  ✘   7551 [chromium] › tests/generated/e2e-302-v318-boundary-incremental.spec.ts:96:7 › 碳认证完整业务流程 › I-REC设备注册到证书签发完整流程 (retry #2) (303ms)
  ✘   7552 [chromium] › tests/generated/e2e-302-v318-boundary-incremental.spec.ts:214:7 › 有序充电完整业务流程 › 查看充电桩负荷并取消排队 (10.9s)
  ✘   7547 [chromium] › tests/generated/e2e-302-v318-boundary-incremental.spec.ts:137:7 › 碳认证完整业务流程 › 证书转让流程 (17.0s)
  ✘   7549 [chromium] › tests/generated/e2e-302-v318-boundary-incremental.spec.ts:179:7 › 有序充电完整业务流程 › 排队到调度完整流程 (17.4s)
  ✘   7548 [chromium] › tests/generated/e2e-302-v318-boundary-incremental.spec.ts:153:7 › 碳认证完整业务流程 › CCER项目注册流程 (17.6s)
  ✘   7553 [chromium] › tests/generated/e2e-302-v318-boundary-incremental.spec.ts:214:7 › 有序充电完整业务流程 › 查看充电桩负荷并取消排队 (retry #1) (10.9s)
  ✘   7554 [chromium] › tests/generated/e2e-302-v318-boundary-incremental.spec.ts:137:7 › 碳认证完整业务流程 › 证书转让流程 (retry #1) (16.5s)
  ✘   7555 [chromium] › tests/generated/e2e-302-v318-boundary-incremental.spec.ts:179:7 › 有序充电完整业务流程 › 排队到调度完整流程 (retry #1) (16.9s)
  ✘   7556 [chromium] › tests/generated/e2e-302-v318-boundary-incremental.spec.ts:153:7 › 碳认证完整业务流程 › CCER项目注册流程 (retry #1) (16.9s)
  ✘   7557 [chromium] › tests/generated/e2e-302-v318-boundary-incremental.spec.ts:214:7 › 有序充电完整业务流程 › 查看充电桩负荷并取消排队 (retry #2) (10.8s)
  ✘   7561 [chromium] › tests/generated/e2e-302-v318-boundary-incremental.spec.ts:267:7 › 微电网能耗报表业务流程 › 查看概览到导出报表完整流程 (10.8s)
  ✘   7558 [chromium] › tests/generated/e2e-302-v318-boundary-incremental.spec.ts:137:7 › 碳认证完整业务流程 › 证书转让流程 (retry #2) (16.6s)
  ✘   7559 [chromium] › tests/generated/e2e-302-v318-boundary-incremental.spec.ts:179:7 › 有序充电完整业务流程 › 排队到调度完整流程 (retry #2) (17.2s)
  ✘   7560 [chromium] › tests/generated/e2e-302-v318-boundary-incremental.spec.ts:153:7 › 碳认证完整业务流程 › CCER项目注册流程 (retry #2) (17.3s)
  ✘   7562 [chromium] › tests/generated/e2e-302-v318-boundary-incremental.spec.ts:267:7 › 微电网能耗报表业务流程 › 查看概览到导出报表完整流程 (retry #1) (11.1s)
  ✘   7563 [chromium] › tests/generated/e2e-302-v318-boundary-incremental.spec.ts:290:7 › 微电网能耗报表业务流程 › 日报表和月报表切换 (11.0s)
  ✘   7565 [chromium] › tests/generated/e2e-302-v318-boundary-incremental.spec.ts:367:7 › CIM协议配置业务流程 › 查看偏差分析 (10.8s)
  ✘   7564 [chromium] › tests/generated/e2e-302-v318-boundary-incremental.spec.ts:324:7 › CIM协议配置业务流程 › 配置CIM端点并查看调度记录 (16.1s)
  ✘   7566 [chromium] › tests/generated/e2e-302-v318-boundary-incremental.spec.ts:267:7 › 微电网能耗报表业务流程 › 查看概览到导出报表完整流程 (retry #2) (10.8s)
  ✘   7567 [chromium] › tests/generated/e2e-302-v318-boundary-incremental.spec.ts:290:7 › 微电网能耗报表业务流程 › 日报表和月报表切换 (retry #1) (11.1s)
  ✘   7568 [chromium] › tests/generated/e2e-302-v318-boundary-incremental.spec.ts:367:7 › CIM协议配置业务流程 › 查看偏差分析 (retry #1) (11.1s)
  ✘   7570 [chromium] › tests/generated/e2e-302-v318-boundary-incremental.spec.ts:392:7 › 组串监控业务流程 › 查看组串状态并处理异常 (11.1s)
  ✘   7569 [chromium] › tests/generated/e2e-302-v318-boundary-incremental.spec.ts:324:7 › CIM协议配置业务流程 › 配置CIM端点并查看调度记录 (retry #1) (16.4s)
  ✘   7571 [chromium] › tests/generated/e2e-302-v318-boundary-incremental.spec.ts:290:7 › 微电网能耗报表业务流程 › 日报表和月报表切换 (retry #2) (11.4s)
  ✘   7572 [chromium] › tests/generated/e2e-302-v318-boundary-incremental.spec.ts:367:7 › CIM协议配置业务流程 › 查看偏差分析 (retry #2) (11.1s)
  ✘   7573 [chromium] › tests/generated/e2e-302-v318-boundary-incremental.spec.ts:392:7 › 组串监控业务流程 › 查看组串状态并处理异常 (retry #1) (10.9s)
  ✘   7576 [chromium] › tests/generated/e2e-302-v318-boundary-incremental.spec.ts:524:7 › 六边界域服务监控业务流程 › 查看六边界域分组并按域筛选 (10.8s)
  ✘   7574 [chromium] › tests/generated/e2e-302-v318-boundary-incremental.spec.ts:324:7 › CIM协议配置业务流程 › 配置CIM端点并查看调度记录 (retry #2) (16.1s)
  ✘   7575 [chromium] › tests/generated/e2e-302-v318-boundary-incremental.spec.ts:434:7 › 备件核销业务流程 › 创建核销单到审批完整流程 (16.3s)
  ✘   7577 [chromium] › tests/generated/e2e-302-v318-boundary-incremental.spec.ts:392:7 › 组串监控业务流程 › 查看组串状态并处理异常 (retry #2) (10.8s)
  ✘   7578 [chromium] › tests/generated/e2e-302-v318-boundary-incremental.spec.ts:524:7 › 六边界域服务监控业务流程 › 查看六边界域分组并按域筛选 (retry #1) (10.9s)
  ✘   7579 [chromium] › tests/generated/e2e-302-v318-boundary-incremental.spec.ts:542:7 › 六边界域服务监控业务流程 › 查看服务详情 (11.1s)
  ✘   7580 [chromium] › tests/generated/e2e-302-v318-boundary-incremental.spec.ts:434:7 › 备件核销业务流程 › 创建核销单到审批完整流程 (retry #1) (16.4s)
  ✘   7591 [chromium] › tests/generated/e2e-302-v318-boundary-incremental.spec.ts:524:7 › 六边界域服务监控业务流程 › 查看六边界域分组并按域筛选 (retry #2) (11.4s)
  ✘   7605 [chromium] › tests/generated/e2e-302-v318-boundary-incremental.spec.ts:542:7 › 六边界域服务监控业务流程 › 查看服务详情 (retry #1) (11.2s)
  ✘   7637 [chromium] › tests/generated/e2e-302-v318-boundary-incremental.spec.ts:542:7 › 六边界域服务监控业务流程 › 查看服务详情 (retry #2) (11.9s)
  ✘   7621 [chromium] › tests/generated/e2e-302-v318-boundary-incremental.spec.ts:434:7 › 备件核销业务流程 › 创建核销单到审批完整流程 (retry #2) (17.6s)
```
